"""Build isolated VU sources and run PS2VU1 tests or captured microprogram replays."""
import argparse
import os
from pathlib import Path
import subprocess

from build_recomp_chunks import INCLUDE_FLAGS
from link_noble_archimedes import LIBRARIES, optional_gpu_link_inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/vu_performance/candidate.exe"))
    parser.add_argument("--runtime-library", type=Path)
    parser.add_argument("--gpu-library-dir", type=Path)
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--minimal", action="store_true", help="Link replay-only memory/PATH1 shims; --tests still requires the full build")
    parser.add_argument("--debug", action="store_true", help="Include symbols for replay RIP sampling")
    parser.add_argument("--cpu", type=int, help="Pin the replay process to one Windows logical CPU")
    parser.add_argument("args", nargs="*")
    args, extra = parser.parse_known_args()
    root = Path(__file__).resolve().parents[1]
    source_dir = args.source_dir or root / "tools/PS2Recomp/ps2xRuntime/src/lib/vu"
    if not source_dir.is_absolute():
        source_dir = root / source_dir
    exe = args.output if args.output.is_absolute() else root / args.output
    exe.parent.mkdir(parents=True, exist_ok=True)
    if not args.no_build:
        if args.minimal:
            command = ["g++", "-std=c++20", "-O3", "-DNDEBUG", "-flto=1", "-msse4.1",
                       "-Itools/PS2Recomp/ps2xRuntime/include", "-Itools/PS2Recomp/ps2xTest/include",
                       f"-I{source_dir}", "tools/vu_benchmark.cpp", "tools/vu_replay_stub.cpp",
                       *[str(source_dir / f"ps2_vu1_{part}.cpp") for part in ("core", "upper", "lower")],
                       "-Wl,--stack,8388608", "-o", str(exe)]
            if args.debug:
                command.insert(2, "-g")
            subprocess.run(command, cwd=root, check=True)
        else:
            build_full_replay(root, source_dir, exe, args)
    return run_replay(root, exe, args, extra)


def build_full_replay(root, source_dir, exe, args):
    libraries = list(LIBRARIES)
    if args.runtime_library:
        libraries[0] = args.runtime_library
    command = ["g++", "-std=c++20", "-O3", "-DNDEBUG", "-flto=1", "-msse4.1", *INCLUDE_FLAGS,
               "-Itools/PS2Recomp/ps2xTest/include", f"-I{source_dir}", "tools/vu_benchmark.cpp",
               "tools/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp",
               "tools/PS2Recomp/ps2xTest/src/test_function_table.cpp",
               *[str(source_dir / f"ps2_vu1_{part}.cpp") for part in ("core", "upper", "lower")],
               *map(str, libraries)]
    if args.debug:
        command.insert(2, "-g")
    gpu_inputs = optional_gpu_link_inputs(root)
    if args.gpu_library_dir:
        saved = args.gpu_library_dir if args.gpu_library_dir.is_absolute() else root / args.gpu_library_dir
        gpu_inputs = [value if value.startswith("-l") else str(saved / Path(value).name) for value in gpu_inputs]
        for value in gpu_inputs:
            if not value.startswith("-l") and not Path(value).is_file():
                raise FileNotFoundError(f"Missing saved GPU link input: {value}")
    if gpu_inputs:
        command.extend(("-Wl,--start-group", *gpu_inputs, "-Wl,--end-group"))
    command.extend(("-Wl,--stack,8388608", "-lwinmm", "-lgdi32", "-lopengl32",
                    "-lkernel32", "-luser32", "-lshell32", "-o", str(exe)))
    subprocess.run(command, cwd=root, check=True)


def run_replay(root, exe, args, extra):
    env = dict(os.environ, PS2_GS_THREADS="0")
    for name in ("PS2_VU_CAPTURE_PREFIX", "PS2_VU_PROFILE"):
        env.pop(name, None)
    env["PATH"] = str(root) + os.pathsep + env.get("PATH", "")
    if args.cpu is not None and env.get("PS2_VU_REPLAY_RIP"):
        raise ValueError("Do not pin replay and its busy-loop RIP sampler to one CPU; omit --cpu for sampling")
    process = subprocess.Popen([str(exe), *args.args, *extra], cwd=root, env=env)
    if args.cpu is not None:
        if os.name != "nt" or not 0 <= args.cpu < 64:
            process.terminate()
            process.wait()
            raise ValueError("--cpu requires Windows and a logical CPU index from 0 through 63")
        import ctypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.SetProcessAffinityMask.argtypes = (ctypes.c_void_p, ctypes.c_size_t)
        kernel.SetProcessAffinityMask.restype = ctypes.c_int
        if not kernel.SetProcessAffinityMask(int(process._handle), 1 << args.cpu):
            process.terminate()
            process.wait()
            raise ctypes.WinError(ctypes.get_last_error())
    return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
