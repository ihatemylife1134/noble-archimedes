"""Compile and execute the sound handshake regression against guest sources."""
import argparse
from pathlib import Path
import subprocess

from build_recomp_chunks import INCLUDE_FLAGS
from generate_unity_chunks import _apply_sound_bank_fix
from generate_resource_entries import generate_resource_entries
from link_noble_archimedes import LIBRARIES, optional_gpu_link_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    generate_resource_entries(root / "src/recomp/generated")
    out = root / "output/sound_status_test"
    out.mkdir(parents=True, exist_ok=True)
    sources = []
    for name in ("sub_0042FD28_0x42fd28.cpp", "sub_00431128_0x431128.cpp",
                 "sub_0042F790_0x42f790.cpp", "sub_0042FCE8_0x42fce8.cpp",
                 "sub_0042FCB0_0x42fcb0.cpp", "sub_0042FA50_0x42fa50.cpp"):
        source = root / "src/recomp/generated" / name
        content = source.read_text()
        if not args.legacy:
            content = _apply_sound_bank_fix(source, content)
        target = out / name
        target.write_text('#include "ps2_runtime.h"\n#include "ps2_runtime_macros.h"\n'
                          '#include "../../src/recomp/sound_bank_compat.hpp"\n' + content)
        sources.append(str(target))
    exe = out / ("legacy.exe" if args.legacy else "test.exe")
    cmd = ["g++", "-std=c++20", "-O0", "-fno-strict-aliasing", "-DNDEBUG", "-msse4.1",
           *INCLUDE_FLAGS, "tests/sound_bank_status_test.cpp", "src/recomp/sound_bank_compat.cpp", *sources,
           *map(str, LIBRARIES)]
    gpu_inputs = optional_gpu_link_inputs(root)
    if gpu_inputs:
        cmd.extend(("-Wl,--start-group", *gpu_inputs, "-Wl,--end-group"))
    cmd.extend(("-lwinmm", "-lgdi32", "-lopengl32", "-lkernel32",
           "-luser32", "-lshell32", "-o", str(exe)))
    subprocess.run(cmd, cwd=root, check=True)
    import os
    env = dict(os.environ, PS2_GS_BACKEND="cpu", PS2_GS_THREADS="0")
    return subprocess.run([str(exe)], cwd=root, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
