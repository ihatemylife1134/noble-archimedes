"""Inspect candidate framebuffers in a saved 4 MiB GS VRAM snapshot."""
import ast
import struct
import sys
from pathlib import Path
from PIL import Image

source = Path("output/diag_priority_coalesce_validation/decode_nonblack_vram.py").read_text()
prefix = source[:source.index("def decode16s():")]
env = {"__file__": str(Path("output/diag_priority_coalesce_validation/decode_nonblack_vram.py"))}
exec(compile(ast.parse(prefix), "gs_addresses", "exec"), env)
vram = Path(sys.argv[1]).read_bytes()
outdir = Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)

for fbp in (0, 150, 168, 236):
    for psm, addr in (("ct16s", env["addr16s"]), ("ct16", env["addr16"]), ("ct32", env["addr32"])):
        pixels = bytearray(512 * 448 * 3)
        nonblack = 0
        for y in range(448):
            for x in range(512):
                offset = addr(fbp << 5, 8, x, y)
                if offset + (4 if psm == "ct32" else 2) > len(vram):
                    continue
                if psm == "ct32":
                    value = struct.unpack_from("<I", vram, offset)[0]
                    color = (value & 255, (value >> 8) & 255, (value >> 16) & 255)
                else:
                    value = struct.unpack_from("<H", vram, offset)[0]
                    color = tuple(((value >> shift) & 31) * 255 // 31 for shift in (0, 5, 10))
                nonblack += any(color)
                pixels[(y * 512 + x) * 3:(y * 512 + x) * 3 + 3] = bytes(color)
        path = outdir / f"fbp{fbp}_{psm}.png"
        Image.frombytes("RGB", (512, 448), bytes(pixels)).save(path)
        print(path, nonblack)
