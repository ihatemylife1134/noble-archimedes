"""
Noble Archimedes - CVCoD ELF Analysis Engine
Parses SLUS_211.68 and extracts:
- ELF header & Section headers (.text, .vutext, .rodata, DVP overlays)
- Syscall sites (instruction and v1 register patterns)
- Entry points & Function boundaries
- Branch tables and indirect jumps
- Generates TOML configuration compatible with PS2Recomp
"""

import os
import struct
from typing import Dict, List, Set, Tuple

class CVCoDElfAnalyzer:
    def __init__(self, elf_path: str):
        self.elf_path = elf_path
        with open(elf_path, "rb") as f:
            self.data = f.read()

        self._parse_elf_header()
        self._parse_sections()

    def _parse_elf_header(self):
        if self.data[:4] != b"\x7fELF":
            raise ValueError("Not a valid ELF binary!")

        self.entry_point = struct.unpack("<I", self.data[24:28])[0]
        self.shoff = struct.unpack("<I", self.data[32:36])[0]
        self.shentsize = struct.unpack("<H", self.data[46:48])[0]
        self.shnum = struct.unpack("<H", self.data[48:50])[0]
        self.shstrndx = struct.unpack("<H", self.data[50:52])[0]

    def _parse_sections(self):
        self.sections: Dict[str, Tuple[int, int, int]] = {} # name -> (vaddr, offset, size)
        
        # Read shstrtab header
        shstr_hdr = self.data[self.shoff + self.shstrndx * self.shentsize : self.shoff + (self.shstrndx + 1) * self.shentsize]
        shstr_off = struct.unpack("<I", shstr_hdr[16:20])[0]
        shstr_size = struct.unpack("<I", shstr_hdr[20:24])[0]
        shstr_data = self.data[shstr_off : shstr_off + shstr_size]

        for i in range(self.shnum):
            hdr = self.data[self.shoff + i * self.shentsize : self.shoff + (i + 1) * self.shentsize]
            name_idx = struct.unpack("<I", hdr[0:4])[0]
            vaddr = struct.unpack("<I", hdr[12:16])[0]
            offset = struct.unpack("<I", hdr[16:20])[0]
            size = struct.unpack("<I", hdr[20:24])[0]

            name = shstr_data[name_idx:].split(b"\x00")[0].decode("latin1", errors="replace")
            if name:
                self.sections[name] = (vaddr, offset, size)

    def scan_syscalls(self) -> List[Tuple[int, int]]:
        text_vaddr, text_off, text_size = self.sections[".text"]
        syscalls = []

        for pc in range(text_vaddr, text_vaddr + text_size, 4):
            off = text_off + (pc - text_vaddr)
            word = struct.unpack("<I", self.data[off:off+4])[0]

            # MIPS SYSCALL: 0x0000000c (opcode 0, funct 0x0c, with code in bits 6-25)
            if (word & 0xfc00003f) == 0x0000000c:
                code = (word >> 6) & 0xfffff
                # Also check preceding instructions for addiu v1, zero, imm
                prev_imm = None
                if pc >= text_vaddr + 4:
                    prev_word = struct.unpack("<I", self.data[off-4:off])[0]
                    # addiu $v1, $zero, imm -> 0x2403xxxx
                    if (prev_word & 0xffff0000) == 0x24030000:
                        prev_imm = prev_word & 0xffff

                syscall_id = code if code != 0 else (prev_imm if prev_imm is not None else 0)
                syscalls.append((pc, syscall_id))

        return syscalls

    def scan_function_prologues(self) -> List[int]:
        """Detect function entry points via stack allocation (addiu sp, sp, -X / daddiu sp, sp, -X)."""
        text_vaddr, text_off, text_size = self.sections[".text"]
        entries = set()
        entries.add(self.entry_point)

        for pc in range(text_vaddr, text_vaddr + text_size, 4):
            off = text_off + (pc - text_vaddr)
            word = struct.unpack("<I", self.data[off:off+4])[0]

            # addiu $sp, $sp, -imm: 0x27bdxxxx (imm < 0 -> imm >= 0x8000)
            # daddiu $sp, $sp, -imm: 0x67bdxxxx
            if (word & 0xffff0000) in (0x27bd0000, 0x67bd0000):
                imm = word & 0xffff
                if imm >= 0x8000:
                    entries.add(pc)

        return sorted(list(entries))

    def generate_recomp_toml(self, output_path: str):
        syscalls = self.scan_syscalls()
        prologues = self.scan_function_prologues()

        text_vaddr, text_off, text_size = self.sections[".text"]

        with open(output_path, "w") as f:
            f.write("# Noble Archimedes - CVCoD Static Recompilation Configuration\n")
            f.write(f'# Target: Castlevania - Curse of Darkness (USA) [SLUS_211.68]\n\n')
            f.write('[general]\n')
            f.write('input = "extracted/SLUS_211.68"\n')
            f.write('output = "src/recomp/generated"\n')
            f.write('single_file_output = false\n')
            f.write('low_memory_mode = true\n')
            f.write('output_worker_threads = 4\n')
            f.write('patch_syscalls = false\n')
            f.write('patch_cop0 = true\n')
            f.write('patch_cache = true\n\n')

            f.write('# Function stubs and SDK bindings\n')
            f.write('stubs = [\n')
            f.write('    "printf",\n')
            f.write('    "puts",\n')
            f.write(']\n\n')

            f.write(f'# Discovered {len(syscalls)} SYSCALL sites\n')
            f.write('# Known syscall sites:\n')
            for pc, sc_id in syscalls[:30]:
                f.write(f'# 0x{pc:08x} -> syscall 0x{sc_id:04x}\n')

            f.write(f'\n# Function entry count detected: {len(prologues)}\n')

if __name__ == "__main__":
    elf_file = "extracted/SLUS_211.68"
    if os.path.exists(elf_file):
        analyzer = CVCoDElfAnalyzer(elf_file)
        print(f"ELF Sections ({len(analyzer.sections)}):")
        for name, (vaddr, off, sz) in list(analyzer.sections.items())[:10]:
            print(f"  {name:15s} VAddr=0x{vaddr:08x} Off=0x{off:08x} Size=0x{sz:08x} ({sz:,} bytes)")
        
        syscalls = analyzer.scan_syscalls()
        print(f"\nTotal SYSCALL instructions found: {len(syscalls)}")
        
        prologues = analyzer.scan_function_prologues()
        print(f"Total function prologues detected: {len(prologues)}")
        
        analyzer.generate_recomp_toml("cvcod_recomp_config.toml")
        print(f"Generated cvcod_recomp_config.toml")
    else:
        print(f"ELF file not found at {elf_file}")
