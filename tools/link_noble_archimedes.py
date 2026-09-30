"""Link the native app, host objects, and recompilation chunks."""

import subprocess
import sys
import time
from pathlib import Path

if __package__:
    from .build_recomp_chunks import HOST_OBJECTS as HOST_SOURCE_OBJECTS
    from .build_recomp_chunks import object_is_current
else:
    try:
        from tools.build_recomp_chunks import HOST_OBJECTS as HOST_SOURCE_OBJECTS
        from tools.build_recomp_chunks import object_is_current
    except ModuleNotFoundError:
        from build_recomp_chunks import HOST_OBJECTS as HOST_SOURCE_OBJECTS
        from build_recomp_chunks import object_is_current


CHUNKS_DIR = Path("src/recomp/chunks")
LIBRARIES = (
    Path("tools/PS2Recomp/build/ps2xRuntime/libps2_runtime.a"),
    Path("tools/PS2Recomp/build/ps2xRuntime/librlImGui.a"),
    Path("tools/PS2Recomp/build/ps2xRuntime/libimgui.a"),
    Path("tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/avcodec.lib"),
    Path("tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/avformat.lib"),
    Path("tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/avutil.lib"),
    Path("tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/swresample.lib"),
    Path("tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/swscale.lib"),
    Path("tools/PS2Recomp/build/ps2xIOP/libps2_iop.a"),
    Path("tools/PS2Recomp/build/_deps/raylib-build/raylib/libraylib.a"),
)


def host_objects(root=Path.cwd()):
    return [Path(root) / object_file for _, object_file in HOST_SOURCE_OBJECTS]


def chunk_objects(root=Path.cwd()):
    return sorted((Path(root) / CHUNKS_DIR).glob("recomp_chunk_*.o"))


def validate_link_objects(root=Path.cwd()):
    root = Path(root)
    expected_chunk_names = {f"recomp_chunk_{index:02d}.o" for index in range(32)}
    expected_chunk_names.add("recomp_chunk_entries.o")
    actual_chunk_names = {path.name for path in chunk_objects(root)}
    missing = sorted(expected_chunk_names - actual_chunk_names)
    extras = sorted(actual_chunk_names - expected_chunk_names)
    if missing:
        raise FileNotFoundError(f"Missing expected chunk object: {missing[0]}")
    if extras:
        raise FileNotFoundError(f"Unexpected chunk object: {extras[0]}")

    source_by_object = {
        root / object_file: root / source_file
        for source_file, object_file in HOST_SOURCE_OBJECTS
    }
    for object_file in host_objects(root):
        source_file = source_by_object[object_file]
        if not object_is_current(object_file, source_file):
            raise FileNotFoundError(f"Stale or dependency-untracked object: {object_file.name}")
    for object_file in chunk_objects(root):
        source_file = root / CHUNKS_DIR / (object_file.stem + ".cpp")
        if not object_is_current(object_file, source_file):
            raise FileNotFoundError(f"Stale or dependency-untracked object: {object_file.name}")


def build_link_command(output_path, root=Path.cwd()):
    root = Path(root)
    output_path = Path(output_path)
    validate_link_objects(root)
    chunk_objs = chunk_objects(root)
    host_objs = host_objects(root)

    command = ["g++", "-std=c++20", "-msse4.1", "-O3", "-o", output_path.as_posix()]
    command.extend(path.relative_to(root).as_posix() for path in host_objs)
    command.extend(path.relative_to(root).as_posix() for path in chunk_objs)
    command.extend(path.as_posix() for path in LIBRARIES)
    command.extend(("-Wl,--allow-multiple-definition", "-lwinmm", "-lgdi32", "-lopengl32", "-lkernel32", "-luser32", "-lshell32"))
    return command


def link_executable(output_path=None, root=Path.cwd(), run=None):
    root = Path(root)
    output_path = Path(output_path) if output_path is not None else Path("NobleArchimedes.exe")
    if not output_path.is_absolute():
        executable_path = root / output_path
    else:
        executable_path = output_path
    executable_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_link_command(output_path, root=root)

    print(f"[Link] Found {len(chunk_objects(root))} chunk object files.")
    print(f"[Link] Launching final link command for {executable_path}...")
    start = time.time()
    runner = run if run is not None else subprocess.run
    result = runner(command, capture_output=True, text=True, cwd=root)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"[FAILED] Link failed with code {result.returncode}:")
        print(result.stderr[:2000])
        return result.returncode
    if not executable_path.is_file():
        print(f"[FAILED] Linker did not create {executable_path}")
        return 1

    size_mb = executable_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Linked {executable_path} ({size_mb:.2f} MB) in {elapsed:.1f}s!")
    return 0


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    raise SystemExit(link_executable(output_path))


if __name__ == "__main__":
    main()
