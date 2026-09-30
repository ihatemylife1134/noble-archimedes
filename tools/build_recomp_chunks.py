"""Build source-consistent guest chunks and native host objects."""

import os
import argparse
import re
import shlex
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

if __package__:
    from .generate_unity_chunks import generate_chunks
else:  # Executed as ``python tools/build_recomp_chunks.py``.
    from generate_unity_chunks import generate_chunks


CHUNKS_DIR = Path("src/recomp/chunks")
GENERATED_DIR = Path("src/recomp/generated")
INCLUDE_FLAGS = [
    "-Itools/PS2Recomp/build/_deps/raylib-build/raylib/include",
    "-Itools/PS2Recomp/build/_deps/imgui-src",
    "-Itools/PS2Recomp/build/_deps/rlimgui-src",
    "-Itools/PS2Recomp/ps2xRuntime/include",
    "-Itools/PS2Recomp/ps2xRuntime/src/lib/Kernel",
    "-Itools/PS2Recomp/ps2xIOP/include",
    "-Isrc/recomp/generated",
]
# Generated guest code type-puns guest memory and relies on two's-complement
# wrap-around (MIPS addu/subu), so optimize without those assumptions.
GUEST_OPT_FLAGS = ["-O2", "-fno-strict-aliasing", "-fwrapv"]
HOST_OPT_FLAGS = ["-O0"]
HOST_OBJECTS = (
    (Path("src/main.cpp"), Path("src/main.o")),
    (Path("src/camera/camera_controller.cpp"), Path("src/camera/camera_controller.o")),
    (Path("src/input/input_manager.cpp"), Path("src/input/input_manager.o")),
    (Path("src/ui/modern_overlay.cpp"), Path("src/ui/modern_overlay.o")),
    (Path("src/vfs/iso_vfs.cpp"), Path("src/vfs/iso_vfs.o")),
    (Path("src/recomp/generated/register_functions.cpp"), Path("src/recomp/register_functions.o")),
    (Path("src/recomp/runtime_stub_registry.cpp"), Path("src/recomp/runtime_stub_registry.o")),
)


def dependency_file(object_file: Path) -> Path:
    return object_file.with_suffix(object_file.suffix + ".d")


def flags_file(object_file: Path) -> Path:
    return object_file.with_suffix(object_file.suffix + ".flags")


def object_is_current(object_file: Path, source_file: Path, dep_file: Path | None = None, flags=None) -> bool:
    """Return whether an object and its recorded compiler inputs are current.

    With ``flags``, the object must also have been built with exactly those
    compiler options (recorded next to it by compile_source).
    """
    object_file = Path(object_file)
    source_file = Path(source_file)
    dep_file = Path(dep_file) if dep_file else dependency_file(object_file)
    if not object_file.is_file() or object_file.stat().st_size == 0:
        return False
    if flags is not None:
        stamp = flags_file(object_file)
        if not stamp.is_file() or stamp.read_text(encoding="utf-8") != " ".join(flags):
            return False
    if not source_file.is_file() or object_file.stat().st_mtime_ns < source_file.stat().st_mtime_ns:
        return False
    if not dep_file.is_file():
        # Objects built before dependency files were introduced must be rebuilt once.
        return False

    dep_text = dep_file.read_text(encoding="utf-8", errors="replace")
    dep_text = dep_text.replace("\\\r\n", " ").replace("\\\n", " ")
    match = re.search(r":\s+", dep_text)
    if not match:
        return False
    dependencies = dep_text[match.end():]
    try:
        dependency_paths = [Path(value) for value in shlex.split(dependencies, posix=True)]
    except ValueError:
        return False
    if not dependency_paths:
        return False

    object_mtime = object_file.stat().st_mtime_ns
    source_resolved = source_file.resolve()
    found_source = False
    for dependency in dependency_paths:
        if not dependency.is_absolute():
            dependency = Path.cwd() / dependency
        if not dependency.is_file():
            return False
        if dependency.resolve() == source_resolved:
            found_source = True
        if dependency.stat().st_mtime_ns > object_mtime:
            return False
    return found_source


def compile_source(source_file: Path, object_file: Path, include_flags=None, cwd=None, opt_flags=None):
    source_file = Path(source_file)
    object_file = Path(object_file)
    dep_file = dependency_file(object_file)
    opt_flags = list(opt_flags if opt_flags is not None else HOST_OPT_FLAGS)
    if object_is_current(object_file, source_file, dep_file, flags=opt_flags):
        return (source_file.name, True, 0.0, "Already current")

    object_file.parent.mkdir(parents=True, exist_ok=True)
    dep_file.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "g++", "-std=c++20", "-msse4.1", *opt_flags, "-MMD", "-MF", dep_file.as_posix(),
        "-c", source_file.as_posix(), "-o", object_file.as_posix(),
    ] + list(include_flags if include_flags is not None else INCLUDE_FLAGS)
    start = time.time()
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    elapsed = time.time() - start
    if result.returncode == 0:
        stamp = flags_file(object_file) if cwd is None else Path(cwd) / flags_file(object_file)
        stamp.write_text(" ".join(opt_flags), encoding="utf-8")
    return source_file.name, result.returncode == 0, elapsed, result.stderr if result.returncode else ""


def compile_chunk(chunk_file: Path):
    return compile_source(chunk_file, Path(chunk_file).with_suffix(".o"), opt_flags=GUEST_OPT_FLAGS)


def build_chunks(generated_dir=GENERATED_DIR, chunks_dir=CHUNKS_DIR, num_chunks=32, max_workers=None):
    """Refresh unity chunks from generated functions, then compile stale chunks."""
    generate_chunks(generated_dir, chunks_dir, num_chunks=num_chunks)
    chunk_files = sorted(Path(chunks_dir).glob("recomp_chunk_*.cpp"))
    if max_workers is None:
        cpu_count = os.cpu_count() or 4
        max_workers = max(1, min(14, cpu_count - 1))
    if max_workers <= 1:
        results = []
        for index, path in enumerate(chunk_files, start=1):
            result = compile_chunk(path)
            results.append(result)
            print(f"[Build] {index}/{len(chunk_files)} {result[0]} {'current' if result[2] == 0 else f'compiled in {result[2]:.1f}s'}", flush=True)
        return results

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compile_chunk, path): path for path in chunk_files}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"[Build] {len(results)}/{len(chunk_files)} {result[0]} {'current' if result[2] == 0 else f'compiled in {result[2]:.1f}s'}", flush=True)
    return results


def build_host_objects(root=Path.cwd()):
    root = Path(root)
    return [compile_source(root / source, root / target, cwd=root) for source, target in HOST_OBJECTS]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=None, help="Maximum parallel chunk compilers")
    args = parser.parse_args()
    results = build_chunks(max_workers=args.jobs)
    results.extend(build_host_objects())
    failures = [(name, error) for name, ok, _, error in results if not ok]
    for name, ok, elapsed, error in results:
        if ok:
            state = "current" if elapsed == 0 else f"compiled in {elapsed:.1f}s"
            print(f"[Build] {name}: {state}")
        else:
            print(f"[ERROR] {name}: {error}")
    if failures:
        print(f"[Build] Failed {len(failures)} of {len(results)} objects.")
        sys.exit(1)
    print(f"[Build] All {len(results)} guest and host objects are current.")


if __name__ == "__main__":
    main()
