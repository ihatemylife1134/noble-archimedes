import subprocess
import sys
import time
from pathlib import Path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

from tools.link_noble_archimedes import (
    CHUNKS_DIR,
    LIBRARIES,
    chunk_objects,
    host_objects,
    optional_gpu_link_inputs,
)

def link_stage_a(output_exe):
    root = Path.cwd()
    output_path = Path(output_exe).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    chunks = chunk_objects(root)
    hosts = host_objects(root)
    gpus = optional_gpu_link_inputs(root)

    print(f"[Link] Chunk objects: {len(chunks)}")
    print(f"[Link] Host objects: {len(hosts)}")
    print(f"[Link] GPU inputs: {len(gpus)}")

    cmd = ["g++", "-std=c++20", "-msse4.1", "-O3", "-o", output_path.as_posix()]
    cmd.extend(p.relative_to(root).as_posix() for p in hosts)
    cmd.extend(p.relative_to(root).as_posix() for p in chunks)
    cmd.extend(p.as_posix() for p in LIBRARIES)

    if gpus:
        cmd.extend(("-Wl,--start-group", *gpus, "-Wl,--end-group"))

    cmd.extend((
        "-Wl,--allow-multiple-definition",
        "-lwinmm",
        "-lgdi32",
        "-lopengl32",
        "-lkernel32",
        "-luser32",
        "-lshell32"
    ))

    print(f"[Link] Launching link for {output_path}...")
    start = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    elapsed = time.time() - start

    if res.returncode != 0:
        print(f"[FAILED] Link failed with code {res.returncode}")
        print(res.stderr[:2000])
        sys.exit(res.returncode)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Linked {output_path} ({size_mb:.2f} MB) in {elapsed:.1f}s")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "output/fps60/stage_a_gameplay_v1/NobleArchimedes_stage_a.exe"
    link_stage_a(out)
