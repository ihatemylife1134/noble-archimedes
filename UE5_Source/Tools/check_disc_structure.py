#!/usr/bin/env python3
"""
Analyze the PS2 disc structure (FILEDATA.BIN, SLUS_211.68) to extract
format information for the UE5 rebuild.

This tool reads the disc image and documents:
- ELF executable structure
- Archive directory table
- File type signatures
- Disc layout

No copyrighted content is extracted - only format documentation.
"""

import struct
import sys
from pathlib import Path

DISC_ROOT = Path("/Volumes/Untitled")

def analyze_elf(filepath):
    """Analyze the PS2 ELF executable."""
    print("=" * 60)
    print("SLUS_211.68 - PS2 ELF Executable Analysis")
    print("=" * 60)

    with open(filepath, "rb") as f:
        # ELF header
        f.seek(0)
        magic = f.read(4)
        if magic != b'\x7fELF':
            print("ERROR: Not a valid ELF file")
            return

        ei_class = f.read(1)[0]  # 1=32-bit, 2=64-bit
        ei_data = f.read(1)[0]   # 1=little endian, 2=big endian
        f.read(16)  # Rest of e_ident

        e_type = struct.unpack('<H', f.read(2))[0]
        e_machine = struct.unpack('<H', f.read(2))[0]
        e_version = struct.unpack('<I', f.read(4))[0]
        e_entry = struct.unpack('<I', f.read(4))[0]
        e_phoff = struct.unpack('<I', f.read(4))[0]
        e_shoff = struct.unpack('<I', f.read(4))[0]
        e_flags = struct.unpack('<I', f.read(4))[0]
        e_ehsize = struct.unpack('<H', f.read(2))[0]
        e_phentsize = struct.unpack('<H', f.read(2))[0]
        e_phnum = struct.unpack('<H', f.read(2))[0]
        e_shentsize = struct.unpack('<H', f.read(2))[0]
        e_shnum = struct.unpack('<H', f.read(2))[0]
        e_shstrndx = struct.unpack('<H', f.read(2))[0]

        print(f"Magic: {magic}")
        print(f"Class: {ei_class} (32-bit)")
        print(f"Data: {ei_data} (little-endian)")
        print(f"Type: {e_type} (2=ET_EXEC executable)")
        print(f"Machine: {e_machine} (8=MIPS R3000)")
        print(f"Entry Point: 0x{e_entry:08x}")
        print(f"Program Header Offset: 0x{e_phoff:x}")
        print(f"Program Header Count: {e_phnum}")
        print(f"Section Header Count: {e_shnum}")
        print()

        # Program headers
        f.seek(e_phoff)
        for i in range(e_phnum):
            ph = f.read(e_phentsize)
            p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack('<IIIIIIII', ph)
            type_name = {1: 'PT_LOAD', 2: 'PT_DYNAMIC', 3: 'PT_INTERP', 4: 'PT_NOTE', 6: 'PT_PHDR'}.get(p_type, f'UNKNOWN(0x{p_type:08x})')
            flags = []
            if p_flags & 1: flags.append('X')
            if p_flags & 2: flags.append('W')
            if p_flags & 4: flags.append('R')
            print(f"  PH[{i}]: {type_name:12} offset=0x{p_offset:08x} vaddr=0x{p_vaddr:08x} filesz=0x{p_filesz:08x} memsz=0x{p_memsz:08x} flags={''.join(flags):3} align=0x{p_align:08x}")


def analyze_filedatabin(filepath):
    """Analyze the FILEDATA.BIN archive."""
    print("=" * 60)
    print("FILEDATA.BIN - Game Data Archive Analysis")
    print("=" * 60)

    with open(filepath, "rb") as f:
        # Header text (SYSTEM.CNF style)
        f.seek(0)
        header_text = f.read(0x34).decode('ascii', errors='replace').strip('\x00')
        print(f"Header text: {header_text}")

        # Directory table at 0x800
        f.seek(0x800)
        magic = struct.unpack('<I', f.read(4))[0]
        unk1 = struct.unpack('<I', f.read(4))[0]
        data_start = struct.unpack('<Q', f.read(8))[0]
        num_entries = struct.unpack('<I', f.read(4))[0]
        entry_size = struct.unpack('<I', f.read(4))[0]
        pad = f.read(8)

        print(f"\nDirectory Table (at 0x800):")
        print(f"  Magic: 0x{magic:08x}")
        print(f"  Unknown: {unk1}")
        print(f"  Data Start: 0x{data_start:x} ({data_start} bytes)")
        print(f"  Entry Count: {num_entries}")
        print(f"  Entry Size: {entry_size} bytes")
        print(f"  Pad: {pad.hex()}")
        print()

        # Read entries
        print("  Entries:")
        for i in range(num_entries):
            entry = f.read(entry_size)
            if len(entry) < entry_size:
                break
            fields = struct.unpack('<IIIIIIII', entry)
            print(f"    Entry {i+1}: id=0x{fields[0]:08x} type=0x{fields[1]:08x} offset=0x{fields[2]:08x} size=0x{fields[3]:08x} unk4=0x{fields[4]:08x} unk5=0x{fields[5]:08x} unk6=0x{fields[6]:08x} unk7=0x{fields[7]:08x}")

        # Scan for file signatures in data region
        print("\n  File Signature Scan (first 2MB of data):")
        f.seek(data_start)
        data = f.read(2 * 1024 * 1024)  # 2MB

        signatures = {
            b'\xff\xd8\xff': 'JPEG image',
            b'\x89PNG\r\n\x1a\n': 'PNG image',
            b'BM': 'BMP image',
            b'\x1f\x8b': 'GZIP compressed',
            b'PK\x03\x04': 'ZIP archive',
            b'RIFF': 'RIFF (WAV/AVI)',
            b'\x00\x00\x01\xba': 'MPEG Program Stream',
            b'TIM2': 'PS2 TIM2 texture',
            b'VAGp': 'PS2 VAG audio',
        }

        found = []
        for sig, name in signatures.items():
            idx = 0
            while True:
                idx = data.find(sig, idx)
                if idx == -1:
                    break
                found.append((data_start + idx, name))
                idx += 1

        for offset, name in sorted(found)[:30]:
            print(f"    0x{offset:08x}: {name}")

        if len(found) > 30:
            print(f"    ... and {len(found) - 30} more")


def analyze_pss_files(disc_root):
    """Analyze PSS video cutscene files."""
    print("=" * 60)
    print("PSS/ - Video Cutscene Analysis")
    print("=" * 60)

    pss_dir = disc_root / "PSS"
    if not pss_dir.exists():
        print("PSS directory not found")
        return

    total_size = 0
    for pss_file in sorted(pss_dir.glob("*.PSS")):
        size = pss_file.stat().st_size
        total_size += size
        print(f"  {pss_file.name}: {size / (1024*1024):.1f} MB")

    print(f"  Total: {total_size / (1024*1024):.1f} MB ({len(list(pss_dir.glob('*.PSS')))} files)")


def analyze_sound(disc_root):
    """Analyze sound bank files."""
    print("=" * 60)
    print("SOUND/ - Audio Bank Analysis")
    print("=" * 60)

    sound_dir = disc_root / "SOUND"
    if not sound_dir.exists():
        print("SOUND directory not found")
        return

    for snd_file in sorted(sound_dir.glob("*.BIN")):
        size = snd_file.stat().st_size
        with open(snd_file, "rb") as f:
            header = f.read(4)
        print(f"  {snd_file.name}: {size / (1024*1024):.1f} MB, header: {header.hex()}")


def main():
    if not DISC_ROOT.exists():
        print(f"Disc root not found: {DISC_ROOT}")
        print("Make sure the game disc is mounted at /Volumes/Untitled")
        sys.exit(1)

    print("Noble Archimedes - PS2 Disc Structure Analysis")
    print("For UE5 Rebuild Reference Only")
    print("No copyrighted content is extracted")
    print()

    analyze_elf(DISC_ROOT / "SLUS_211.68")
    print()
    analyze_filedatabin(DISC_ROOT / "FILEDATA.BIN")
    print()
    analyze_pss_files(DISC_ROOT)
    print()
    analyze_sound(DISC_ROOT)
    print()
    print("Analysis complete. Use this information to inform the UE5 rebuild.")


if __name__ == "__main__":
    main()