"""Run a hidden candidate and send keys only to its own window.

Append button names to <out>/input.txt while running. Logs and guest frames
are preserved; the candidate runs from the asset directory. No global input
or guest memory writes are used.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def honor_owned_timer_resolution(pid):
    """Disable only Windows' timer-request suppression for this child process."""
    class PowerThrottling(ctypes.Structure):
        _fields_ = [('Version', ctypes.c_ulong), ('ControlMask', ctypes.c_ulong),
                    ('StateMask', ctypes.c_ulong)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.SetProcessInformation.argtypes = (ctypes.c_void_p, ctypes.c_int,
                                             ctypes.c_void_p, ctypes.c_ulong)
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    handle = kernel.OpenProcess(0x0200, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        state = PowerThrottling(1, 4, 0)
        if not kernel.SetProcessInformation(handle, 4, ctypes.byref(state), ctypes.sizeof(state)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


def send_button(pid, button, hold=1.0):
    """Deliver a bounded key press to an already running hidden game."""
    user = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    user.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    user.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
    user.GetWindowTextW.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
    user.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)
    keys = {"cross": 0x20, "circle": 0x45, "triangle": 0x4B,
            "start": 0x0D, "left": 0x25, "up": 0x26,
            "right": 0x27, "down": 0x28, "square": 0x4A,
            "move-forward": 0x57, "move-back": 0x53,
            "move-left": 0x41, "move-right": 0x44}
    found = []
    def find(hwnd, _):
        owner = ctypes.c_ulong()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value != pid:
            return 1
        title = ctypes.create_unicode_buffer(512)
        user.GetWindowTextW(hwnd, title, len(title))
        if title.value.startswith("Noble Archimedes:"):
            found.append(hwnd)
            return 0
        return 1
    user.EnumWindows(callback_type(find), None)
    if not found:
        # The bounded probe can end between a state read and its next input.
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong)
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.GetExitCodeProcess.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
        kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle and ctypes.get_last_error() == 87:
            return False
        if handle:
            try:
                exit_code = ctypes.c_ulong()
                if kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)) and exit_code.value != 259:
                    return False
            finally:
                kernel.CloseHandle(handle)
        raise RuntimeError(f"No game window owned by PID {pid}")
    key = keys[button]
    scan = user.MapVirtualKeyW(key, 0)
    flags = 1 | (scan << 16) | ((1 << 24) if key in (0x25, 0x26, 0x27, 0x28) else 0)
    if not user.PostMessageW(found[0], 0x100, key, flags):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        time.sleep(hold)
    finally:
        user.PostMessageW(found[0], 0x101, key, flags | (3 << 30))
    print(f"pid={pid} button={button} hold={hold}s", flush=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seconds", type=int, default=600)
    parser.add_argument("--show-window", action="store_true",
                        help="Show only the owned game window while preserving headless audio/runtime settings")
    parser.add_argument("--honor-timer-resolution", action="store_true",
                        help="Disable timer-request suppression for this owned child only")
    parser.add_argument("--gs-threads", type=int, default=8,
                        help="CPU renderer worker count (0 disables workers)")
    parser.add_argument("--native-vu-dll", type=Path,
                        help="Stage an isolated VU DLL and executable in the probe output directory")
    parser.add_argument("--env", action="append", default=[], metavar="NAME=VALUE",
                        help="Additional runtime diagnostic setting; repeat as needed")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    commands = out / "input.txt"
    commands.write_text("", encoding="utf-8")
    base_hint = out / "rdram_base.txt"
    base_hint.unlink(missing_ok=True)
    temp = (out if args.native_vu_dll else root) / f"NobleArchimedes_probe_{os.getpid()}.exe"
    if args.native_vu_dll:
        if not out.is_relative_to(root / 'output' / 'fps60'):
            parser.error('Isolated DLL probes require a workspace output/fps60 directory')
        # The game changes its working directory to its executable folder.
        # Reference original assets without copying or changing their contents.
        asset_dir = out / 'extracted'
        if asset_dir.exists():
            parser.error('Isolated asset directory already exists')
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(asset_dir), str(root / 'extracted')],
                       check=True, capture_output=True)
        iso = root / 'Castlevania - Curse of Darkness (USA).iso'
        if iso.exists():
            os.link(iso, out / iso.name)
        (out / 'asset_references.json').write_text(json.dumps(dict(
            extracted_junction=str(root / 'extracted'),
            iso_hardlink=str(iso) if iso.exists() else None), indent=2))
        inputs = {}
        for source in root.glob('*.dll'):
            selected = args.native_vu_dll.resolve() if source.name.lower() == 'noble_vu_jit.dll' else source
            expected = hashlib.sha256(selected.read_bytes()).hexdigest()
            target = out / source.name
            if target.exists():
                parser.error('Isolated DLL output already exists: ' + str(target))
            shutil.copy2(selected, target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise RuntimeError('Isolated DLL copy mismatch')
            inputs[str(selected)] = expected
        (out / 'dll_inputs.json').write_text(json.dumps(inputs, indent=2))
    shutil.copy2(args.exe.resolve(), temp)
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("PS2_"):
            del env[key]
    env.update(PS2_HEADLESS="1", NOBLE_OVERLAY="0", PS2_PAD_TRACE="1",
               PS2_MPEG_TRACE="1", PS2_GS_THREADS=str(args.gs_threads),
               PS2_HOST_PROFILE="rate", PS2_HOST_PROFILE_FILE=str(out / "host_profile.log"),
               PS2_RDRAM_BASE_FILE=str(base_hint),
               PS2_FRAME_DUMP_PREFIX=str(out / "frame"))
    for setting in args.env:
        name, separator, value = setting.partition("=")
        if not separator or not (name.startswith("PS2_") or name in {
            "NOBLE_ENGINE_SEAM_CAPTURE_GATE", "NOBLE_ENGINE_SEAM_JOB_CAPTURE",
            "NOBLE_ENGINE_PROVENANCE_GATE", "NOBLE_ENGINE_PROVENANCE_FILE",
            "NOBLE_VU_CENSUS_GATE", "NOBLE_VU_CENSUS_FILE",
            "NOBLE_VIF1_CAUSAL_GATE", "NOBLE_VU_IMAGE_DUMP_DIR",
            "NOBLE_VU_DEAD_FLAG_ELIMINATION"
        }):
            parser.error("--env requires a PS2_NAME=value setting")
        env[name] = value
    gate = env.get("PS2_VU_CAPTURE_GATE_FILE")
    if gate and Path(gate).exists():
        temp.unlink(missing_ok=True)
        parser.error("PS2_VU_CAPTURE_GATE_FILE must name a fresh, initially absent marker")
    user = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    user.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    user.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
    user.GetWindowTextW.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
    user.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)
    user.MapVirtualKeyW.argtypes = (ctypes.c_uint, ctypes.c_uint)
    user.ShowWindow.argtypes = (ctypes.c_void_p, ctypes.c_int)
    user.IsWindowVisible.argtypes = (ctypes.c_void_p,)
    keys = {"cross": 0x20, "circle": 0x45, "triangle": 0x4B,
            "start": 0x0D, "left": 0x25, "up": 0x26,
            "right": 0x27, "down": 0x28, "square": 0x4A,
            "move-forward": 0x57, "move-back": 0x53,
            "move-left": 0x41, "move-right": 0x44}
    window = None
    with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
        try:
            proc = subprocess.Popen([str(temp)], cwd=root, env=env, stdout=stdout,
                                    stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        except OSError:
            temp.unlink(missing_ok=True)
            raise
        (out / "pid.txt").write_text(str(proc.pid))
        import psutil
        (out / 'probe_identity.json').write_text(json.dumps(dict(
            pid=proc.pid, creation_time=psutil.Process(proc.pid).create_time(),
            executable=str(temp.resolve())), indent=2))
        print(f"pid={proc.pid} input={commands}", flush=True)
        start = time.monotonic()
        (out / "timing.json").write_text(json.dumps({"started_monotonic": start, "pid": proc.pid}))
        consumed = 0
        try:
            if args.honor_timer_resolution:
                honor_owned_timer_resolution(proc.pid)
                (out / 'timer_resolution_policy.json').write_text(json.dumps(dict(
                    pid=proc.pid, control_mask=4, state_mask=0, version=1,
                    monotonic=time.monotonic()), indent=2))
            while proc.poll() is None and time.monotonic() - start < args.seconds:
                if window is None:
                    def find_window(hwnd, _):
                        nonlocal window
                        owner = ctypes.c_ulong()
                        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
                        if owner.value == proc.pid:
                            title = ctypes.create_unicode_buffer(512)
                            user.GetWindowTextW(hwnd, title, len(title))
                            if title.value.startswith("Noble Archimedes:"):
                                window = hwnd
                                return 0
                        return 1
                    user.EnumWindows(callback_type(find_window), None)
                    if window and args.show_window:
                        user.ShowWindow(window, 1)
                        if not user.IsWindowVisible(window):
                            raise RuntimeError('Owned game window did not become visible')
                        (out / 'window_visibility.json').write_text(json.dumps(dict(
                            pid=proc.pid, hwnd=window, visible=True,
                            headless_environment=env['PS2_HEADLESS'],
                            monotonic=time.monotonic()), indent=2))
                lines = commands.read_text(encoding="utf-8-sig").splitlines()
                if window:
                    for line in lines[consumed:]:
                        button = line.strip().lower()
                        if button not in keys:
                            continue
                        key = keys[button]
                        scan = user.MapVirtualKeyW(key, 0)
                        flags = 1 | (scan << 16) | ((1 << 24) if key in (0x25, 0x26, 0x27, 0x28) else 0)
                        user.PostMessageW(window, 0x100, key, flags)
                        time.sleep(0.5)
                        user.PostMessageW(window, 0x101, key, flags | (3 << 30))
                        print(f"t={time.monotonic()-start:.1f} key={button}", flush=True)
                        time.sleep(0.5)
                    consumed = len(lines)
                time.sleep(0.1)
        finally:
            stopped_by_harness = proc.poll() is None
            if stopped_by_harness:
                proc.terminate()
            proc.wait(timeout=10)
            (out / "exit.json").write_text(json.dumps({
                "returncode": proc.returncode,
                "stopped_by_harness": stopped_by_harness,
                "elapsed_seconds": time.monotonic() - start,
            }))
            temp.unlink(missing_ok=True)
    print(f"capture complete: {out}", flush=True)


if __name__ == "__main__":
    main()
