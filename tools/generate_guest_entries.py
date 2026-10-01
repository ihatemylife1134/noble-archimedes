"""Generate compact entry adapters from local, ignored MIPS instruction comments."""
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Entry:
    source: str
    name: str
    start: int
    end: int


# Discovery metadata only; registers, operands and jump targets come from inputs.
ENTRIES = (
    Entry("sub_00454AD0_0x454ad0.cpp", "resourcePointer", 0x454B40, 0x454B50),
    Entry("sub_00500000_0x500000.cpp", "levelSetupReturn", 0x500004, 0x500024),
)
_INSTRUCTION = re.compile(r"^\s*//\s*0x([0-9a-fA-F]+):\s*0x([0-9a-fA-F]+)\b", re.MULTILINE)


@dataclass(frozen=True)
class Instruction:
    pc: int
    operation: str
    rs: int
    rt: int
    rd: int
    immediate: int
    target: int = 0

    @property
    def destination(self):
        if self.operation in ("lui", "addiu", "ld"):
            return self.rt
        if self.operation in ("daddu", "movn"):
            return self.rd
        return None


def _signed32(value):
    value &= 0xffffffff
    return value - 0x100000000 if value & 0x80000000 else value


def _decode(pc, word):
    if not 0 <= word <= 0xffffffff:
        raise ValueError(f"Instruction word exceeds 32 bits at {pc:#x}")
    opcode = word >> 26
    rs, rt, rd = (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31
    immediate = word & 0xffff
    if immediate & 0x8000:
        immediate -= 0x10000
    target = 0
    if opcode == 0:
        operation = {8: "jr", 11: "movn", 45: "daddu"}.get(word & 63)
        if operation is None or (word >> 6) & 31 or (operation == "jr" and (rt or rd)):
            raise ValueError(f"Unsupported SPECIAL instruction at {pc:#x}")
    else:
        operation = {2: "j", 9: "addiu", 15: "lui", 43: "sw", 55: "ld"}.get(opcode)
        if operation is None or (operation == "lui" and rs):
            raise ValueError(f"Unsupported instruction at {pc:#x}")
        if operation == "j":
            target = ((pc + 4) & 0xf0000000) | ((word & 0x3ffffff) << 2)
        if operation == "lui":
            immediate = word & 0xffff
    return Instruction(pc, operation, rs, rt, rd, immediate, target)


def _read_entry(root, entry):
    if entry.start & 3 or entry.end & 3 or entry.end <= entry.start:
        raise ValueError(f"Invalid instruction range for {entry.name}")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", entry.name):
        raise ValueError("Invalid generated function name")
    words = {}
    for match in _INSTRUCTION.finditer((root / entry.source).read_text(encoding="utf-8")):
        pc, word = (int(value, 16) for value in match.groups())
        if entry.start <= pc <= entry.end:
            if pc in words:
                raise ValueError(f"Duplicate instruction at {pc:#x}")
            words[pc] = word
    instructions = []
    for pc in range(entry.start, entry.end + 1, 4):
        if pc not in words:
            raise ValueError(f"Missing instruction at {pc:#x} in {entry.source}")
        instructions.append(_decode(pc, words[pc]))
    branches = [i for i, ins in enumerate(instructions) if ins.operation in ("j", "jr")]
    if branches != [len(instructions) - 2]:
        raise ValueError(f"Entry {entry.name} must end in one jump and its delay instruction")
    return instructions


def _offset(base, displacement):
    if displacement == 0:
        return base
    return f"{base} {'+' if displacement > 0 else '-'} {abs(displacement)}"


def _literal(value):
    return f"0x{value:X}" if value >= 0x10000 else str(value)


def _render_entry(entry, instructions):
    lines = [f"inline void {entry.name}(uint8_t* rdram, R5900Context* ctx, PS2Runtime* runtime) {{"]
    constants = {0: 0}
    loads = [i for i, ins in enumerate(instructions) if ins.operation == "ld"]
    cached_register = None
    if len(loads) > 1:
        base = instructions[loads[0]].rs
        if (all(instructions[i].rs == base for i in loads) and
                all(ins.destination != base for ins in instructions[loads[0]:loads[-1]])):
            cached_register = base
    cached_name = "sp" if cached_register == 29 else f"base{cached_register}"
    cache_active = False

    def emit(statement):
        lines.append("    " + statement)

    def address(ins):
        if cache_active and ins.rs == cached_register:
            return _offset(cached_name, ins.immediate)
        if ins.rs in constants:
            return f"0x{(constants[ins.rs] + ins.immediate) & 0xffffffff:X}u"
        return f"ADD32(GPR_U32(ctx, {ins.rs}), {ins.immediate & 0xffffffff})"

    def arithmetic(ins):
        nonlocal cache_active
        destination = ins.destination
        known = None
        if ins.operation == "lui":
            known = _signed32(ins.immediate << 16)
            emit(f"SET_GPR_S32(ctx, {ins.rt}, {_literal(known)});")
        elif ins.operation == "addiu":
            if ins.rs in constants:
                known = _signed32(constants[ins.rs] + ins.immediate)
                value = _literal(known)
            elif cache_active and ins.rs == cached_register:
                value = f"static_cast<int32_t>({_offset(cached_name, ins.immediate)})"
            else:
                value = f"static_cast<int32_t>(ADD32(GPR_U32(ctx, {ins.rs}), {ins.immediate & 0xffffffff}))"
            emit(f"SET_GPR_S32(ctx, {ins.rt}, {value});")
        elif ins.operation == "daddu":
            operands = [f"GPR_U64(ctx, {reg})" for reg in (ins.rs, ins.rt) if reg != 0]
            value = " + ".join(operands) if operands else "0"
            emit(f"SET_GPR_U64(ctx, {ins.rd}, {value});")
            if ins.rs in constants and ins.rt in constants:
                known = (constants[ins.rs] + constants[ins.rt]) & 0xffffffffffffffff
        elif ins.operation == "sw":
            emit(f"WRITE32({address(ins)}, GPR_U32(ctx, {ins.rt}));")
        elif ins.operation == "ld":
            if ins.rs == cached_register and not cache_active:
                emit(f"const uint32_t {cached_name} = GPR_U32(ctx, {cached_register});")
                cache_active = True
            emit(f"SET_GPR_U64(ctx, {ins.rt}, READ64({address(ins)}));")
        elif ins.operation == "movn":
            emit(f"if (GPR_U64(ctx, {ins.rt}) != 0) SET_GPR_VEC(ctx, {ins.rd}, GPR_VEC(ctx, {ins.rs}));")
        else:
            raise ValueError(f"Unexpected control instruction at {ins.pc:#x}")
        if destination is not None:
            constants.pop(destination, None)
            if known is not None:
                constants[destination] = known
            constants[0] = 0
            if destination == cached_register:
                cache_active = False

    for ins in instructions[:-2]:
        arithmetic(ins)
    branch, delay = instructions[-2:]
    if branch.operation == "jr":
        emit(f"const uint32_t target = GPR_U32(ctx, {branch.rs});")
        arithmetic(delay)
        emit("ctx->pc = target;")
    else:
        arithmetic(delay)
        emit(f"ctx->pc = 0x{branch.target:x}u;")
        emit(f"runtime->dispatchGuestBranch(rdram, ctx, 0x{branch.target:x}u, 0x{branch.pc:x}u, 0u,")
        lines.append('                                PS2Runtime::GuestBranchKind::DirectJump, "J");')
    lines.append("}")
    return lines


def render_guest_entries(generated_dir, entries=ENTRIES):
    root = Path(generated_dir)
    present = [(root / entry.source).exists() for entry in entries]
    if not any(present):
        return None
    for entry, exists in zip(entries, present):
        if not exists:
            raise ValueError(f"Missing local input {entry.source}")
    bodies = [_render_entry(entry, _read_entry(root, entry)) for entry in entries]
    lines = ['#pragma once', '#include "ps2_runtime.h"', '#include "ps2_runtime_macros.h"', '',
             '// Entries missed when function discovery grouped independent leaves or split',
             '// an epilogue at 0x500000. These execute the original ELF instructions.',
             'namespace noble_entries {']
    for body in bodies:
        lines.extend(body)
    lines.append('inline void install(PS2Runtime* runtime) {')
    for entry in entries:
        lines.append(f"    runtime->registerFunction(0x{entry.start:X}u, {entry.name});")
    lines.extend(['}', '}', ''])
    return "\n".join(lines)


def generate_guest_entries(generated_dir, output=None, entries=ENTRIES):
    text = render_guest_entries(generated_dir, entries)
    if text is None:
        return None
    target = Path(output) if output is not None else Path(generated_dir).parent / "guest_entry_compat.hpp"
    data = text.encode("utf-8")
    if not target.exists() or target.read_bytes() != data:
        target.write_bytes(data)
    return target


if __name__ == "__main__":
    print(generate_guest_entries("src/recomp/generated"))
