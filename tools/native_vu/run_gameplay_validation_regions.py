"""Run an isolated native candidate, measure guest frames, and close its owned window."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import psutil
from measure_gameplay import calculate, samples

ROOT = Path(__file__).resolve().parents[2]


def counter_coverage(rows, start, end, settle):
    eligible = [r for r in rows if start + settle <= r['monotonic'] <= end
                and r.get('phase_index') == 0 and r.get('phase') == 4
                and r.get('state') == [4, 10, 3, 1] and not r.get('phase_invalid')]
    reset = next(((a, b) for a, b in zip(eligible, eligible[1:])
                  if b['phase_frames'] < a['phase_frames']), None)
    return dict(samples=len(eligible),
                span_seconds=eligible[-1]['monotonic'] - eligible[0]['monotonic'] if len(eligible) >= 2 else 0,
                first=eligible[0] if eligible else None,
                last=eligible[-1] if eligible else None, reset_pair=reset)


def close_owned(out):
    identity = json.loads((out / 'probe_identity.json').read_text())
    try:
        process = psutil.Process(identity['pid'])
        if process.create_time() != identity['creation_time'] or Path(process.exe()) != Path(identity['executable']):
            raise RuntimeError('Probe identity changed')
    except psutil.NoSuchProcess:
        return
    user = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    user.EnumWindows.argtypes = (callback_type, ctypes.c_void_p)
    user.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
    user.GetWindowTextW.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int)
    user.PostMessageW.argtypes = (ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)
    found = []

    def callback(hwnd, _):
        pid = ctypes.c_ulong()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == identity['pid']:
            title = ctypes.create_unicode_buffer(512)
            user.GetWindowTextW(hwnd, title, len(title))
            if title.value.startswith('Noble Archimedes:'):
                found.append(hwnd)
        return 1

    user.EnumWindows(callback_type(callback), None)
    for hwnd in found:
        if not user.PostMessageW(hwnd, 0x10, 0, 0):
            raise ctypes.WinError(ctypes.get_last_error())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    parser.add_argument('dll', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--performance-power', action='store_true')
    parser.add_argument('--host-profile', choices=('0', 'rate', 'full'), default='0',
                        help='Host instrumentation; disabled by default for performance measurement')
    diagnostic_mode = parser.add_mutually_exclusive_group()
    diagnostic_mode.add_argument('--diagnostic-jit', action='store_true',
                        help='JIT attribution only: skip compiler wait and tolerate unavailable FPS')
    diagnostic_mode.add_argument('--diagnostic-timing', action='store_true',
                        help='Inclusive native timing attribution: diagnostic FPS, no compiler wait or JIT map required')
    parser.add_argument('--gs-backend', choices=('pgs', 'cpu', 'default'), default='default',
                        help='Explicit GS selector forwarded to the owned probe')
    parser.add_argument('--seconds', type=int, default=75)
    parser.add_argument('--settle', type=int, default=10)
    parser.add_argument('--measurement-gate', action='store_true',
                        help='Wait for OUT/measurement_ready after gameplay; coordinate worker quiescence')
    parser.add_argument('--profile-seconds', type=int, default=0, choices=range(0,31),
                        help='Sample the owned probe after the FPS window, for at most 30s')
    parser.add_argument('--profile-jit-thread', action='store_true',
                        help='Enable owned JIT map and profile its recorded current thread')
    parser.add_argument('--profile-all-threads', action='store_true',
                        help='Sample every current thread of the verified owned probe')
    parser.add_argument('--profile-confirmed-jit', action='store_true', help='Discover an actual allocation-contained execution RIP, then sample only that owned thread')
    parser.add_argument('--profile-crt-copy-return', action='store_true',
                        help='Diagnostic-only suspended leaf RSP[0] copy-caller attribution')
    parser.add_argument('--priority', choices=['normal', 'above-normal', 'high'], default='normal',
                        help='Priority of this owned probe only; ends with the probe')
    args = parser.parse_args()
    if args.profile_crt_copy_return and not (args.diagnostic_jit and args.profile_confirmed_jit):
        parser.error('--profile-crt-copy-return requires diagnostic-jit and profile-confirmed-jit')
    if args.profile_confirmed_jit and not (args.diagnostic_jit and args.profile_jit_thread and args.profile_seconds and not args.profile_all_threads):
        parser.error('--profile-confirmed-jit requires diagnostic-jit, profile-jit-thread, positive profile duration and no all-threads')
    if args.diagnostic_jit and (not args.profile_jit_thread or not args.profile_seconds):
        parser.error('--diagnostic-jit requires --profile-jit-thread and positive --profile-seconds')
    if args.seconds < args.settle + 35 or args.seconds > 180:
        parser.error('Measurement must leave at least 35 settled seconds and be <=180s')
    out = args.out.resolve()
    if out.exists():
        parser.error('Use a fresh output directory')
    if not out.is_relative_to(ROOT / 'output/fps60'):
        parser.error('Output must be inside output/fps60')
    out.mkdir(parents=True)
    record = {'exe': str(args.exe.resolve()), 'dll': str(args.dll.resolve()),
              'gs_backend_selector': args.gs_backend, 'diagnostic_jit': args.diagnostic_jit,
              'diagnostic_timing': args.diagnostic_timing,
              'host_profile': args.host_profile,
              'diagnostic_only': args.diagnostic_jit or args.diagnostic_timing}
    for key in ('exe', 'dll'):
        record[key + '_sha256'] = hashlib.sha256(Path(record[key]).read_bytes()).hexdigest()
    (out / 'validation_inputs.json').write_text(json.dumps(record, indent=2))
    env = os.environ.copy()
    env['PGS_SKIP_COMPILATION_TASKS'] = '1'
    original = re.search(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',
                         subprocess.check_output(['powercfg', '/getactivescheme'], text=True), re.I).group()
    power = {'original': original, 'changed': args.performance_power}
    navigation = None
    with (out / 'harness.log').open('w') as log, (out / 'driver.log').open('w') as driver_log:
        probe = subprocess.Popen([sys.executable, str(ROOT / 'tools/probe_headless.py'), record['exe'], str(out),
                                  '--seconds', '600', '--native-vu-dll', record['dll'], '--gs-threads', '2',
                                  '--env', 'PS2_VU_BACKEND=play',
                                  '--env', 'PS2_HOST_PROFILE=' + args.host_profile,
                                  '--env', 'PS2_GS_BACKEND=' + args.gs_backend] +
                                 (['--env', 'PS2_VU_JIT_MAP_FILE=' + str(out / 'native_jit.jsonl')]
                                  if args.profile_jit_thread else []), cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            if args.performance_power:
                subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True)
                power['performance_power_start_monotonic'] = time.monotonic()
                (out / 'power_comparison.json').write_text(json.dumps(power, indent=2))
            startup_deadline = time.monotonic() + 120
            while not (out / 'probe_identity.json').exists() or not (out / 'pid.txt').exists():
                if probe.poll() is not None:
                    raise RuntimeError('Probe exited before owned identity became available')
                if time.monotonic() > startup_deadline:
                    raise RuntimeError('Owned probe identity startup timed out')
                time.sleep(.2)
            navigation = subprocess.Popen([sys.executable, str(ROOT / 'tools/probe_new_game.py'), str(out),
                                           '--skip-movie-after', '3'], cwd=ROOT, stdout=driver_log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 480
            while time.monotonic() < deadline:
                rows = samples(out)
                if rows and rows[-1].get('state') == [4, 10, 3, 1]:
                    break
                if probe.poll() is not None:
                    raise RuntimeError('Probe exited before gameplay')
                time.sleep(1)
            else:
                raise RuntimeError('No gameplay reached')
            print('Gameplay reached; waiting 15s before protected measurement', flush=True)
            time.sleep(15)
            if args.measurement_gate:
                print('Waiting for measurement_ready gate', flush=True)
                gate_deadline = time.monotonic() + 240
                while not (out / 'measurement_ready').exists():
                    if probe.poll() is not None:
                        raise RuntimeError('Probe exited before measurement gate')
                    if time.monotonic() > gate_deadline:
                        raise RuntimeError('Measurement gate was not released')
                    time.sleep(1)
            # Compilation belongs outside a performance window.
            compiler_deadline = time.monotonic() + 180
            while True:
                if args.diagnostic_jit or args.diagnostic_timing:
                    break
                active = []
                for process in psutil.process_iter(['name', 'cmdline']):
                    if process.info['name'] in ('cc1plus.exe', 'lto1.exe', 'clang++.exe'):
                        command = ' '.join(process.info['cmdline'] or [])
                        if 'noble-archimedes' in command.lower():
                            active.append(process.pid)
                if not active:
                    break
                if time.monotonic() > compiler_deadline:
                    raise RuntimeError('Workspace compilation did not finish before measurement deadline')
                print('Waiting for workspace compiler processes:', active, flush=True)
                time.sleep(5)
            identity = json.loads((out / 'probe_identity.json').read_text())
            process = psutil.Process(identity['pid'])
            if process.create_time() != identity['creation_time'] or Path(process.exe()) != Path(identity['executable']):
                raise RuntimeError('Probe identity changed before measurement')
            process.nice({'normal': psutil.NORMAL_PRIORITY_CLASS,
                          'above-normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                          'high': psutil.HIGH_PRIORITY_CLASS}[args.priority])
            cpu_start = psutil.cpu_times()
            process_start = process.cpu_times()
            power['performance_monotonic'] = time.monotonic()
            (out / 'power_comparison.json').write_text(json.dumps(power, indent=2))
            print(f'Measuring actual guest updates for {args.seconds}s; no sampling', flush=True)
            end = time.monotonic() + args.seconds
            while time.monotonic() < end:
                if probe.poll() is not None:
                    raise RuntimeError('Probe exited during measurement')
                time.sleep(1)
            coverage_deadline = end + 45
            while True:
                coverage_now = time.monotonic()
                coverage = counter_coverage(samples(out), power['performance_monotonic'], coverage_now, args.settle)
                reset_pair = coverage['reset_pair']
                coverage_span = coverage['span_seconds']
                coverage.update(requested_seconds=args.seconds, extension_seconds=max(0, coverage_now - end))
                if reset_pair:
                    (out / 'measurement_counter_rejection.json').write_text(json.dumps(coverage, indent=2))
                    if args.diagnostic_jit or args.diagnostic_timing:
                        break
                    raise RuntimeError('Gameplay counter reset; measurement rejected')
                if coverage_span >= 30 or args.diagnostic_jit or args.diagnostic_timing:
                    break
                if coverage_now >= coverage_deadline:
                    (out / 'measurement_counter_rejection.json').write_text(json.dumps(coverage, indent=2))
                    raise RuntimeError('Gameplay counter coverage remained below 30s after bounded 45s extension')
                if probe.poll() is not None:
                    raise RuntimeError('Probe exited while waiting for counter coverage')
                time.sleep(1)
            (out / 'measurement_counter_coverage.json').write_text(json.dumps(coverage, indent=2))
            power['measurement_end_monotonic'] = time.monotonic()
            try:
                result = calculate(samples(out), power['performance_monotonic'], power['measurement_end_monotonic'], args.settle)
            except RuntimeError as error:
                if not (args.diagnostic_jit or args.diagnostic_timing):
                    raise
                result = dict(guest_fps=None, measured_seconds=None, diagnostic_only=True,
                              fps_unavailable_reason=str(error))
            cpu_end = psutil.cpu_times()
            process_end = process.cpu_times()
            # Windows interrupt/DPC counters are subsets of system time.
            total_cpu = (cpu_end.user + cpu_end.system + cpu_end.idle
                         - cpu_start.user - cpu_start.system - cpu_start.idle)
            result['system_busy_fraction'] = 1 - (cpu_end.idle - cpu_start.idle) / total_cpu if total_cpu else None
            elapsed = power['measurement_end_monotonic'] - power['performance_monotonic']
            result['process_cpu_cores'] = (process_end.user + process_end.system - process_start.user - process_start.system) / elapsed
            result['owned_probe_priority'] = args.priority
            result['gs_backend_selector'] = args.gs_backend
            result['diagnostic_only'] = args.diagnostic_jit or args.diagnostic_timing
            result['measurement_gate_used'] = args.measurement_gate
            result['power_plan'] = power
            (out / 'steady_gameplay_result.json').write_text(json.dumps(result, indent=2))
            if result['guest_fps'] is None:
                print('Diagnostic FPS unavailable:', result['fps_unavailable_reason'], flush=True)
            else:
                label = 'Diagnostic gameplay' if result['diagnostic_only'] else 'Actual gameplay'
                print(f"{label} {result['guest_fps']:.3f} FPS / {result['measured_seconds']:.3f}s", flush=True)
            if args.profile_seconds:
                profile = out / 'profile'
                profile.mkdir()
                profile_start = time.monotonic()
                print('FPS window complete; starting separate caller sampling', flush=True)
                sampler = [sys.executable, str(ROOT / 'tools/profiling/sample_owned_callers_regions.py'),
                           str(identity['pid']), str(profile / 'rips.txt'),
                           '--identity', str(out / 'probe_identity.json'), '--seconds', str(args.profile_seconds)]
                if args.profile_confirmed_jit:
                    discovery = profile / 'discovery.txt'
                    subprocess.run([*sampler[:3], str(discovery), '--identity', str(out / 'probe_identity.json'),
                                    '--seconds', '2', '--all-threads', '--stack-bytes', '0'], cwd=ROOT, check=True)
                    from jit_map_parse import validate, lookup
                    from collections import Counter
                    _, map_index = validate(out / 'native_jit.jsonl')
                    matches = Counter()
                    for line in discovery.with_suffix('.stacks.jsonl').read_text().splitlines():
                        sample = json.loads(line)
                        if lookup(map_index, sample['pid'], sample['qpc'], sample['rip']):
                            matches[sample['tid']] += 1
                    if not matches:
                        raise RuntimeError('Discovery found no actual allocation-contained execution thread')
                    selected = matches.most_common(1)[0][0]
                    (profile / 'confirmed_thread.json').write_text(json.dumps(dict(
                        pid=identity['pid'], selected_tid=selected, validated_execution_matches=dict(matches),
                        basis='Actual PID/QPC/RIP-contained JIT allocation from fresh owned discovery'), indent=2))
                    sampler += ['--thread-id', str(selected), '--stack-bytes', '0']
                    if args.profile_crt_copy_return:
                        sampler += ['--crt-copy-return']
                else:
                    sampler += (['--all-threads'] if args.profile_all_threads else
                                ['--jit-map', str(out / 'native_jit.jsonl')] if args.profile_jit_thread else [])
                subprocess.run(sampler, cwd=ROOT, check=True)
                (profile / 'window.json').write_text(json.dumps(dict(
                    start=profile_start, end=time.monotonic(),
                    fps_window_end=power['measurement_end_monotonic']), indent=2))
        finally:
            if args.performance_power:
                subprocess.run(['powercfg', '/setactive', original], check=True)
            power['restored_monotonic'] = time.monotonic()
            (out / 'power_comparison.json').write_text(json.dumps(power, indent=2))
            if (out / 'probe_identity.json').exists():
                close_owned(out)
            try:
                probe.wait(timeout=20)
            except subprocess.TimeoutExpired:
                # Harness owns and identifies its child; let it clean up.
                print('Normal close pending; awaiting bounded harness cleanup', flush=True)
                probe.wait(timeout=620)
            if navigation is not None:
                try:
                    navigation.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    navigation.terminate()
                    navigation.wait(timeout=5)
            if probe.returncode:
                raise RuntimeError(f'Harness failed: {probe.returncode}')
    print('Probe closed; original power plan restored', flush=True)


if __name__ == '__main__':
    main()
