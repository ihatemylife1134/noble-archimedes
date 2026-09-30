"""
Noble Archimedes - PS2 ISO Reader & Streamer
Provides direct sector-level and file-level access to Castlevania: Curse of Darkness ISO.
"""

import os
import struct
import sys
from typing import Dict, Optional, Tuple

SECTOR_SIZE = 2048

class PS2IsoReader:
    def __init__(self, iso_path: str):
        self.iso_path = iso_path
        self._file = open(iso_path, "rb")
        self.files: Dict[str, Tuple[int, int]] = {} # path -> (sector_offset, size_bytes)
        self._parse_iso()

    def _parse_iso(self):
        # Read Primary Volume Descriptor at sector 16 (0x10 * 2048 = 0x8000)
        self._file.seek(16 * SECTOR_SIZE)
        pvd = self._file.read(SECTOR_SIZE)
        if pvd[1:6] != b"CD001":
            raise ValueError("Not a standard ISO9660 filesystem!")

        # Root directory record is at offset 156 (0x9C) in PVD
        root_record = pvd[156:156 + 34]
        root_extent = struct.unpack("<I", root_record[2:6])[0]
        root_size = struct.unpack("<I", root_record[10:14])[0]

        self._read_directory(root_extent, root_size, "")

    def _read_directory(self, extent: int, size: int, current_path: str):
        self._file.seek(extent * SECTOR_SIZE)
        dir_data = self._file.read(size)
        offset = 0

        while offset < len(dir_data):
            length = dir_data[offset]
            if length == 0:
                # Padding to sector boundary
                offset = ((offset // SECTOR_SIZE) + 1) * SECTOR_SIZE
                continue

            record = dir_data[offset:offset + length]
            file_extent = struct.unpack("<I", record[2:6])[0]
            file_size = struct.unpack("<I", record[10:14])[0]
            flags = record[25]
            name_len = record[32]
            name_raw = record[33:33 + name_len]

            # Parse filename (strip version ";1")
            name = name_raw.decode("latin1", errors="replace").split(";")[0]

            offset += length

            if name in ("\x00", "\x01", ""):
                continue # . and .. entries

            full_path = f"{current_path}/{name}".lstrip("/")

            is_dir = (flags & 2) != 0
            if is_dir:
                self._read_directory(file_extent, file_size, full_path)
            else:
                self.files[full_path.upper()] = (file_extent, file_size)

    def list_files(self):
        return {k: f"{v[1]:,} bytes @ sector {v[0]}" for k, v in sorted(self.files.items())}

    def read_file(self, path: str, offset: int = 0, length: Optional[int] = None) -> bytes:
        norm_path = path.upper().replace("\\", "/").lstrip("/")
        if norm_path not in self.files:
            raise FileNotFoundError(f"File '{path}' not found in ISO")

        extent, file_size = self.files[norm_path]
        if offset >= file_size:
            return b""

        read_len = file_size - offset if length is None else min(length, file_size - offset)
        self._file.seek(extent * SECTOR_SIZE + offset)
        return self._file.read(read_len)

    def get_sector_lba(self, path: str) -> int:
        norm_path = path.upper().replace("\\", "/").lstrip("/")
        if norm_path not in self.files:
            raise FileNotFoundError(f"File '{path}' not found in ISO")
        return self.files[norm_path][0]

    def close(self):
        if self._file:
            self._file.close()

if __name__ == "__main__":
    iso_file = "Castlevania - Curse of Darkness (USA).iso"
    if os.path.exists(iso_file):
        reader = PS2IsoReader(iso_file)
        print(f"Discovered {len(reader.files)} files in ISO:")
        for name, meta in reader.list_files().items():
            print(f"  {name:30s} -> {meta}")
        reader.close()
    else:
        print(f"ISO not found at {iso_file}")
