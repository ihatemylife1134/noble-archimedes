"""
Noble Archimedes - Fast Direct Unity Chunk Generator
Inlines recompiled function implementations directly into chunk files,
completely eliminating 500+ redundant file-opens and header reparses per chunk.
Reduces compilation time by over 90%.
"""

from pathlib import Path
import re
if __package__:
    from .generate_guest_entries import generate_guest_entries
    from .generate_resource_entries import generate_resource_entries
else:
    from generate_guest_entries import generate_guest_entries
    from generate_resource_entries import generate_resource_entries


_DISPATCH_TRANSFER_HELPERS = {
    "sub_00420450_0x420450.cpp",
    "sub_0041FFF0_0x41fff0.cpp",
}
_SOUND_BANK_HELPERS = {"sub_0042FD28_0x42fd28.cpp", "sub_00431128_0x431128.cpp"}

def _apply_split_delay_slot_fix(function_file: Path, content: str) -> str:
    # Discovery split this function exactly at the JAL's delay slot.
    if function_file.name != "sub_004FFDC0_0x4ffdc0.cpp" or "// restored cross-boundary delay slot" in content:
        return content
    anchor = "    SET_GPR_U32(ctx, 31, 0x500004u);"
    if content.count(anchor) != 1:
        raise ValueError("Expected one cross-boundary JAL")
    return content.replace(anchor, anchor + "\n    // restored cross-boundary delay slot: 0x500000 mov.s f13, f12\n    ctx->f[13] = FPU_MOV_S(ctx->f[12]);", 1)


def _apply_sound_bank_fix(function_file: Path, content: str) -> str:
    """Replace the legacy always-busy stub and model accepted bank commands."""
    if function_file.name == "sub_0042FD28_0x42fd28.cpp":
        if "FAST_WRITE16(0xAD82B0u, 0x0003)" not in content:
            return content
        return '''void sub_0042FD28_0x42fd28(uint8_t* rdram, R5900Context* ctx, PS2Runtime*) {
    const uint32_t result = noble_sound::bankStatus(rdram, ctx->pc, GPR_U32(ctx, 4));
    SET_GPR_S32(ctx, 2, static_cast<int32_t>(result));
    ctx->pc = GPR_U32(ctx, 31);
}
'''
    if function_file.name == "sub_00431128_0x431128.cpp":
        if "noble_sound::acceptedCommand(" in content:
            return content
        anchor = "        WRITE32(ADD32(GPR_U32(ctx, 5), 8), GPR_U32(ctx, 7));"
        if content.count(anchor) != 1:
            raise ValueError("Expected one accepted sound-command queue write")
        return content.replace(anchor, anchor + "\n        noble_sound::acceptedCommand(rdram, GPR_U32(ctx, 9), GPR_U32(ctx, 10));", 1)
    return content
_DISPATCH_TRANSFER_SWITCH = "    switch (ctx->pc) {"
_DISPATCH_TRANSFER_GUARD_PATTERN = re.compile(
    r"if\s*\(\s*runtime->guestDispatchDepth\(\)\s*!=\s*0u?\s*&&\s*"
    r"runtime->eeScheduler\(\)\.currentContext\(\)\s*==\s*ctx\s*\)\s*"
    r"\{\s*throw\s+EeDispatcherTransfer\s*\{\s*\}\s*;\s*\}",
    re.MULTILINE,
)
_DISPATCH_TRANSFER_GUARD = (
    "    if (runtime->guestDispatchDepth() != 0 && "
    "runtime->eeScheduler().currentContext() == ctx) {\n"
    "        throw EeDispatcherTransfer{};\n"
    "    }\n\n"
)


def _apply_dispatch_transfer_fix(function_file: Path, content: str) -> tuple[str, bool]:
    """Keep nested EE dispatcher transfer guards on the targeted helpers after regeneration."""
    if function_file.name not in _DISPATCH_TRANSFER_HELPERS:
        return content, False

    if _DISPATCH_TRANSFER_GUARD_PATTERN.search(content):
        return content, True

    if content.count(_DISPATCH_TRANSFER_SWITCH) != 1:
        raise ValueError(
            f"Expected one resume switch in generated {function_file.name}"
        )
    return content.replace(
        _DISPATCH_TRANSFER_SWITCH,
        _DISPATCH_TRANSFER_GUARD + _DISPATCH_TRANSFER_SWITCH,
        1,
    ), True


def generate_chunks(generated_dir: str, chunks_dir: str, num_chunks: int = 32):
    generate_guest_entries(generated_dir)
    generate_resource_entries(generated_dir)
    gen_path = Path(generated_dir)
    chunk_path = Path(chunks_dir)
    chunk_path.mkdir(parents=True, exist_ok=True)

    func_files = sorted(list(gen_path.glob("sub_*.cpp")))
    print(f"Discovered {len(func_files)} recompiled function files.")

    if not func_files:
        print("No function files found to batch!")
        return

    chunks = [[] for _ in range(num_chunks)]
    for idx, f in enumerate(func_files):
        chunks[idx % num_chunks].append(f)

    changed_chunks = []
    for i, file_list in enumerate(chunks):
        chunk_file = chunk_path / f"recomp_chunk_{i:02d}.cpp"
        contains_dispatch_transfer_helper = any(f.name in _DISPATCH_TRANSFER_HELPERS for f in file_list)
        parts = [
            "// Auto-generated Noble Archimedes fast unity chunk\n",
            "#include <stdexcept>\n",
            '#include "ps2_runtime_macros.h"\n',
            '#include "ps2_runtime.h"\n',
            "#include <ps2_recompiled_functions.h>\n",
            "#include <ps2_recompiled_stubs.h>\n",
            '#include "ps2_syscalls.h"\n',
            '#include "ps2_stubs.h"\n\n',
        ]
        if contains_dispatch_transfer_helper:
            parts.insert(-1, '#include "runtime/ee_scheduler.h"\n')
        if any(f.name in _SOUND_BANK_HELPERS for f in file_list):
            parts.insert(-1, '#include "../sound_bank_compat.hpp"\n')

        for function_file in file_list:
            content = function_file.read_text(encoding="utf-8", errors="replace")
            # Find start of function definition (void sub_...).
            idx = content.find("void sub_")
            function_content = content[idx:] if idx != -1 else content
            function_content, _ = _apply_dispatch_transfer_fix(function_file, function_content)
            function_content = _apply_sound_bank_fix(function_file, function_content)
            function_content = _apply_split_delay_slot_fix(function_file, function_content)
            parts.extend((function_content, "\n\n"))

        content = "".join(parts)
        if not chunk_file.exists() or chunk_file.read_text(encoding="utf-8") != content:
            chunk_file.write_text(content, encoding="utf-8")
            changed_chunks.append(chunk_file)

    print(f"Generated {num_chunks} inlined unity chunks in {chunks_dir}; updated {len(changed_chunks)}.")
    return changed_chunks

if __name__ == "__main__":
    generate_chunks("src/recomp/generated", "src/recomp/chunks", num_chunks=32)
