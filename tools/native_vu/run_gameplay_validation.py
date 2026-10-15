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


def gs_telemetry_environment(out, enabled, direct):
    if not enabled:
        return []
    key = ('PS2_GS_PGS_GPU_PRESENT_TELEMETRY_FILE' if direct else
           'PS2_GS_PGS_PRESENT_RING_TELEMETRY_FILE')
    return ['--env', key + '=' + str(out / 'ring_telemetry.json')]


def direct_gpu_environment(out, enabled):
    if not enabled:
        return []
    return ['--env', 'PS2_GS_PGS_GPU_PRESENT=1', '--env',
            'PS2_FRAME_DUMP_STOP_FILE=' + str(out / 'timed_window_active')]


def native_census_environment(out, enabled):
    if not enabled:
        return []
    return ['--env', 'NOBLE_VU_CENSUS_FILE=' + str(out / 'native_census.bin'),
            '--env', 'NOBLE_VU_CENSUS_GATE=' + str(out / 'census_ready')]


def vblank_environment(enabled, gate=None):
    if not enabled:
        return []
    result = ['--env', 'PS2_VBLANK_DIAGNOSTIC_UNPACED=1']
    if gate is not None:
        result += ['--env', 'PS2_VBLANK_DIAGNOSTIC_GATE=' + str(gate)]
    return result


def gs_cut_environment(skip_fullscreen_blends, suppress_texture_invalidation, gate):
    result = []
    if skip_fullscreen_blends:
        result += ['--env', 'PS2_GS_PGS_SKIP_FULLSCREEN_BLENDS=1']
    if suppress_texture_invalidation:
        result += ['--env', 'PS2_GS_PGS_SUPPRESS_TEXTURE_INVALIDATION=1']
    if result:
        result += ['--env', 'PS2_GS_PGS_DIAGNOSTIC_GATE=' + str(gate)]
    return result


def vif_fence_profile_environment(enabled, gate):
    if not enabled:
        return []
    return [
        '--env', 'PS2_VIF1_FENCE_PROFILE=1',
        '--env', 'PS2_VIF1_FENCE_PROFILE_GATE=' + str(gate),
    ]


def dead_flag_environment(enabled):
    return ['--env', 'NOBLE_VU_DEAD_FLAG_ELIMINATION=1'] if enabled else []


def counter_coverage(rows, start, end, settle):
    eligible = [r for r in rows if start + settle <= r['monotonic'] <= end
                and r.get('phase_index') == 0 and r.get('phase') == 4
                and r.get('state') in ([4, 10, 3, 1], [4, 10, 3, 3]) and not r.get('phase_invalid')]
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
    parser.add_argument('--show-window', action='store_true',
                        help='Show the owned game window without changing headless audio/runtime settings')
    parser.add_argument('--honor-timer-resolution', action='store_true',
                        help='Honor timer requests for the owned probe, including while hidden')
    parser.add_argument('--host-profile', choices=('0', 'rate', 'full'), default='0',
                        help='Host instrumentation; disabled by default for performance measurement')
    diagnostic_mode = parser.add_mutually_exclusive_group()
    diagnostic_mode.add_argument('--diagnostic-jit', action='store_true',
                        help='JIT attribution only: skip compiler wait and tolerate unavailable FPS')
    diagnostic_mode.add_argument('--diagnostic-timing', action='store_true',
                        help='Inclusive native timing attribution: diagnostic FPS, no compiler wait or JIT map required')
    parser.add_argument('--gs-backend', choices=('pgs', 'cpu', 'pcsx2', 'default'), default='default',
                        help='Explicit GS selector forwarded to the owned probe')
    parser.add_argument('--pgs-scanout', choices=('logical', 'native', 'compatible'),
                        help='Explicit PGS scanout path; compatible uses CPU display composition')
    parser.add_argument('--pcsx2-gs-adapter', type=Path,
                        help='Actual GS-only module; requires pcsx2 and the matching resource directory')
    parser.add_argument('--pcsx2-gs-resources', type=Path,
                        help='Pinned upstream GS resource directory for the selected adapter')
    parser.add_argument('--pcsx2-gs-trace-real-adapter', type=Path,
                        help='Diagnostic-only real adapter forwarded by the qualified GS trace shim')
    parser.add_argument('--skip-movie-hold', type=float, default=2.0,
                        help='Duration of the ordinary Start press used to skip the intro movie')
    parser.add_argument('--seconds', type=int, default=75)
    parser.add_argument('--settle', type=int, default=10)
    parser.add_argument('--measurement-gate', action='store_true',
                        help='Wait for OUT/measurement_ready after gameplay; coordinate worker quiescence')
    parser.add_argument('--exercise-gameplay-input', action='store_true',
                        help='Send ordinary right input after measurement/profile and retain before/after image paths')
    parser.add_argument('--gs-ring-telemetry', action='store_true',
                        help='Measure fresh native GPU images through owned read-only counters')
    parser.add_argument('--gs-direct-gpu', action='store_true',
                        help='Enable direct native GPU texture presentation and its separate fresh counters')
    parser.add_argument('--profile-seconds', type=int, default=0, choices=range(0,31),
                        help='Sample the owned probe after the FPS window, for at most 30s')
    parser.add_argument('--profile-jit-thread', action='store_true',
                        help='Enable owned JIT map and profile its recorded current thread')
    parser.add_argument('--profile-all-threads', action='store_true',
                        help='Sample every current thread of the verified owned probe')
    parser.add_argument('--profile-suspended-stack', action='store_true',
                        help='Diagnostic-only consistent stack snapshots; adds sampling perturbation')
    parser.add_argument('--profile-confirmed-jit', action='store_true', help='Discover an actual allocation-contained execution RIP, then sample only that owned thread')
    parser.add_argument('--profile-crt-copy-return', action='store_true',
                        help='Diagnostic-only suspended leaf RSP[0] copy-caller attribution')
    parser.add_argument('--priority', choices=['normal', 'above-normal', 'high'], default='normal',
                        help='Priority of this owned probe only; ends with the probe')
    parser.add_argument('--boundary-diagnostics', action='store_true',
                        help='Diagnostic-only render completion, pacing, PGS scopes and guest swap fields')
    parser.add_argument('--gs-present-trace', action='store_true',
                        help='Diagnostic-only full frontend draw tracking and display-copy trace')
    parser.add_argument('--render-wait-diagnostics', action='store_true',
                        help='Diagnostic-only isolation of render-wait reporting and its timer reads')
    parser.add_argument('--guest-pc-diagnostics', action='store_true',
                        help='Diagnostic-only sampled guest PCs at scheduler checkpoints')
    parser.add_argument('--pool-store-trace', action='store_true',
                        help='Diagnostic-only selected guest RAM-store tracing; requires a trace-enabled private EXE')
    parser.add_argument('--native-vif1-worker', action='store_true',
                        help='Opt into the isolated native VIF1 worker prototype')
    parser.add_argument('--vu-dead-flag-elimination', action='store_true',
                        help='Opt into PCSX2-style VU FMAC flag liveness elimination')
    parser.add_argument('--vblank-unpaced', action='store_true',
                        help='Diagnostic-only: retain virtual VBLANK state but remove host-deadline sleeping')
    parser.add_argument('--gs-skip-fullscreen-blends', action='store_true',
                        help='Diagnostic-only: consume state but skip frame-sized all-blended render passes')
    parser.add_argument('--gs-suppress-texture-invalidation', action='store_true',
                        help='Diagnostic-only: retain PGS cached textures instead of applying overlap invalidations')
    parser.add_argument('--quiet-runtime-traces', action='store_true',
                        help='Disable periodic pad and MPEG trace output for performance validation')
    parser.add_argument('--native-census', action='store_true',
                        help='Diagnostic-only gameplay-gated native VU program and block counts')
    parser.add_argument('--ee-mesh-timing', action='store_true',
                        help='Diagnostic-only bounded EE mesh builder timing; requires a timing-enabled private EXE')
    parser.add_argument('--vif-worker-latency', action='store_true',
                        help='Gameplay-gated worker latency diagnostic; requires a timing-enabled private EXE')
    parser.add_argument('--vif-fence-profile', action='store_true',
                        help='Gameplay-gated aggregate VIF wait/commit profile; requires a build with NOBLE_VIF1_FENCE_PROFILE_DIAGNOSTIC')
    parser.add_argument('--dma-job-capture', action='store_true',
                        help='Diagnostic-only whole DMA/parser observer, gated at OUT/capture_ready')
    parser.add_argument('--engine-seam-capture', action='store_true',
                        help='Diagnostic-only owned engine inputs and complete jobs, gated at OUT/capture_ready')
    parser.add_argument('--engine-provenance-capture', action='store_true',
                        help='Diagnostic-only physical VIF1 ancestry and same-worker VU state, gated at OUT/capture_ready')
    parser.add_argument('--crt-request-trace', action='store_true',
                        help='Diagnostic-only bounded original CRT request observer output')
    args = parser.parse_args()
    if args.gs_direct_gpu and not (args.diagnostic_jit or args.diagnostic_timing):
        args.gs_ring_telemetry = True
    if args.gs_direct_gpu and args.gs_backend != 'pgs':
        parser.error('--gs-direct-gpu requires --gs-backend pgs')
    if args.pgs_scanout and args.gs_backend != 'pgs':
        parser.error('--pgs-scanout requires --gs-backend pgs')
    if (args.gs_skip_fullscreen_blends or args.gs_suppress_texture_invalidation) and args.gs_backend != 'pgs':
        parser.error('GS diagnostic cuts require --gs-backend pgs')
    if args.native_census and not (args.diagnostic_timing and args.native_vif1_worker):
        parser.error('--native-census requires --diagnostic-timing and --native-vif1-worker')
    if args.ee_mesh_timing and not args.diagnostic_timing:
        parser.error('--ee-mesh-timing requires --diagnostic-timing')
    if args.vif_worker_latency and not (args.diagnostic_timing and args.native_vif1_worker):
        parser.error('--vif-worker-latency requires --diagnostic-timing and --native-vif1-worker')
    if args.gs_ring_telemetry and (args.gs_backend != 'pgs' or
                                  args.diagnostic_jit or args.diagnostic_timing):
        parser.error('--gs-ring-telemetry requires non-diagnostic --gs-backend pgs')
    if not 0.05 <= args.skip_movie_hold <= 2.0:
        parser.error('--skip-movie-hold must be between 0.05 and 2 seconds')
    if args.pcsx2_gs_trace_real_adapter and not (args.diagnostic_timing and args.gs_backend == 'pcsx2' and args.pcsx2_gs_trace_real_adapter.is_file()):
        parser.error('--pcsx2-gs-trace-real-adapter requires diagnostic-timing, pcsx2 and an existing real module')
    if args.gs_backend == 'pcsx2':
        if not args.pcsx2_gs_adapter or not args.pcsx2_gs_adapter.is_file() or not args.pcsx2_gs_resources or not args.pcsx2_gs_resources.is_dir():
            parser.error('pcsx2 requires an existing --pcsx2-gs-adapter and --pcsx2-gs-resources')
    elif args.pcsx2_gs_adapter or args.pcsx2_gs_resources:
        parser.error('PCSX2 GS module paths require --gs-backend pcsx2')
    if args.dma_job_capture and not (args.diagnostic_timing and args.native_vif1_worker):
        parser.error('--dma-job-capture requires --diagnostic-timing and --native-vif1-worker')
    if args.engine_seam_capture and not (args.diagnostic_timing and args.native_vif1_worker):
        parser.error('--engine-seam-capture requires --diagnostic-timing and --native-vif1-worker')
    if args.engine_provenance_capture and not (args.diagnostic_timing and args.native_vif1_worker):
        parser.error('--engine-provenance-capture requires --diagnostic-timing and --native-vif1-worker')
    if args.crt_request_trace and not args.diagnostic_timing:
        parser.error('--crt-request-trace requires --diagnostic-timing')
    if args.boundary_diagnostics and not (args.diagnostic_jit or args.diagnostic_timing):
        parser.error('--boundary-diagnostics requires a diagnostic mode')
    if args.gs_present_trace and not args.diagnostic_timing:
        parser.error('--gs-present-trace requires --diagnostic-timing')
    if args.render_wait_diagnostics and not (args.diagnostic_jit or args.diagnostic_timing):
        parser.error('--render-wait-diagnostics requires a diagnostic mode')
    if args.guest_pc_diagnostics and not (args.diagnostic_jit or args.diagnostic_timing):
        parser.error('--guest-pc-diagnostics requires a diagnostic mode')
    if args.pool_store_trace and not (args.diagnostic_jit or args.diagnostic_timing):
        parser.error('--pool-store-trace requires a diagnostic mode')
    if args.profile_crt_copy_return and not (args.diagnostic_jit and args.profile_confirmed_jit):
        parser.error('--profile-crt-copy-return requires diagnostic-jit and profile-confirmed-jit')
    if args.profile_confirmed_jit and not (args.diagnostic_jit and args.profile_jit_thread and args.profile_seconds and not args.profile_all_threads):
        parser.error('--profile-confirmed-jit requires diagnostic-jit, profile-jit-thread, positive profile duration and no all-threads')
    if args.diagnostic_jit and (not args.profile_jit_thread or not args.profile_seconds):
        parser.error('--diagnostic-jit requires --profile-jit-thread and positive --profile-seconds')
    if args.profile_suspended_stack and not (args.diagnostic_jit and args.profile_seconds):
        parser.error('--profile-suspended-stack requires --diagnostic-jit and positive --profile-seconds')
    minimum_settled_seconds = 5 if (args.diagnostic_jit or args.diagnostic_timing) else 35
    if args.settle < 0 or args.seconds < args.settle + minimum_settled_seconds or args.seconds > 180:
        parser.error(f'Measurement must leave at least {minimum_settled_seconds} settled seconds and be <=180s')
    out = args.out.resolve()
    if out.exists():
        parser.error('Use a fresh output directory')
    if not out.is_relative_to(ROOT / 'output/fps60'):
        parser.error('Output must be inside output/fps60')
    out.mkdir(parents=True)
    record = {'exe': str(args.exe.resolve()), 'dll': str(args.dll.resolve()),
              'native_census': args.native_census,
              'ee_mesh_timing': args.ee_mesh_timing,
              'vif_worker_latency': args.vif_worker_latency,
              'vif_fence_profile': args.vif_fence_profile,
              'gs_backend_selector': args.gs_backend, 'diagnostic_jit': args.diagnostic_jit,
              'pgs_scanout': args.pgs_scanout,
              'gs_ring_telemetry': args.gs_ring_telemetry,
              'gs_direct_gpu': args.gs_direct_gpu,
              'diagnostic_timing': args.diagnostic_timing,
              'host_profile': args.host_profile,
              'boundary_diagnostics': args.boundary_diagnostics,
              'gs_present_trace': args.gs_present_trace,
              'skip_movie_hold': args.skip_movie_hold,
              'render_wait_diagnostics': args.render_wait_diagnostics,
              'guest_pc_diagnostics': args.guest_pc_diagnostics,
              'pool_store_trace': args.pool_store_trace,
              'native_vif1_worker': args.native_vif1_worker,
              'vblank_unpaced': args.vblank_unpaced,
              'vblank_unpaced_gate': str(out / 'vblank_unpaced_ready') if args.vblank_unpaced else None,
              'gs_skip_fullscreen_blends': args.gs_skip_fullscreen_blends,
              'gs_suppress_texture_invalidation': args.gs_suppress_texture_invalidation,
              'gs_diagnostic_gate': str(out / 'gs_cut_ready') if (args.gs_skip_fullscreen_blends or args.gs_suppress_texture_invalidation) else None,
              'quiet_runtime_traces': args.quiet_runtime_traces,
              'dma_job_capture': args.dma_job_capture,
              'engine_provenance_capture': args.engine_provenance_capture,
              'crt_request_trace': args.crt_request_trace,
              'engine_seam_capture': args.engine_seam_capture,
              'diagnostic_only': args.diagnostic_jit or args.diagnostic_timing}
    record['profile_suspended_stack'] = args.profile_suspended_stack
    record['exercise_gameplay_input'] = args.exercise_gameplay_input
    record['show_window'] = args.show_window
    record['honor_timer_resolution'] = args.honor_timer_resolution
    for key in ('exe', 'dll'):
        record[key + '_sha256'] = hashlib.sha256(Path(record[key]).read_bytes()).hexdigest()
    pcsx2_environment = []
    if args.gs_backend == 'pcsx2':
        adapter = args.pcsx2_gs_adapter.resolve()
        resources = args.pcsx2_gs_resources.resolve()
        record['pcsx2_gs_adapter'] = str(adapter)
        record['pcsx2_gs_resources'] = str(resources)
        record['pcsx2_gs_inputs'] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(set(adapter.parent.glob('*.dll')) | {p for p in resources.rglob('*') if p.is_file()})}
        pcsx2_environment = ['--env', 'PS2_PCSX2_GS_ADAPTER=' + str(adapter),
                              '--env', 'PS2_PCSX2_GS_RESOURCES=' + str(resources)]
        if args.pcsx2_gs_trace_real_adapter:
            real = args.pcsx2_gs_trace_real_adapter.resolve()
            record['pcsx2_gs_trace_real_adapter'] = str(real)
            record['pcsx2_gs_trace_output'] = str(out / 'gs_trace.bin')
            record['pcsx2_gs_real_inputs'] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in real.parent.glob('*.dll')}
            pcsx2_environment += ['--env', 'PS2_PCSX2_GS_TRACE_REAL_ADAPTER=' + str(real),
                                  '--env', 'PS2_PCSX2_GS_TRACE_OUTPUT=' + record['pcsx2_gs_trace_output']]
    (out / 'validation_inputs.json').write_text(json.dumps(record, indent=2))
    env = os.environ.copy()
    env['PGS_SKIP_COMPILATION_TASKS'] = '1'
    original = re.search(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',
                         subprocess.check_output(['powercfg', '/getactivescheme'], text=True), re.I).group()
    power = {'original': original, 'changed': args.performance_power}
    navigation = None
    ring_reader = None
    with (out / 'harness.log').open('w') as log, (out / 'driver.log').open('w') as driver_log:
        probe = subprocess.Popen([sys.executable, str(ROOT / 'tools/probe_headless.py'), record['exe'], str(out),
                                  '--seconds', '600', '--native-vu-dll', record['dll'], '--gs-threads', '2',
                                  '--env', 'PS2_VU_BACKEND=play',
                                  '--env', 'PS2_HOST_PROFILE=' + args.host_profile,
                                  '--env', 'PS2_GS_BACKEND=' + args.gs_backend] + pcsx2_environment +
                                 gs_telemetry_environment(out, args.gs_ring_telemetry, args.gs_direct_gpu) +
                                 direct_gpu_environment(out, args.gs_direct_gpu) +
                                 (['--env', 'PS2_GS_PGS_SCANOUT=' + args.pgs_scanout]
                                  if args.pgs_scanout else []) +
                                 native_census_environment(out, args.native_census) +
                                 (['--env', 'PS2_EE_MESH_TIMING_FILE=' + str(out / 'ee_mesh_timing.bin')]
                                  if args.ee_mesh_timing else []) +
                                 (['--env', 'NOBLE_VIF1_CAUSAL_GATE=' + str(out / 'vif_causal_ready')]
                                  if args.vif_worker_latency else []) +
                                 (['--env', 'PS2_GS_PRESENT_TRACE=1'] if args.gs_present_trace else []) +
                                 (['--env', 'PS2_EE_RENDER_WAIT_DIAGNOSTICS=1',
                                   '--env', 'PS2_EE_RENDER_COMPLETION_DIAGNOSTICS=1',
                                   '--env', 'PS2_GS_PGS_PROFILE=1'] if args.boundary_diagnostics else []) +
                                  (['--env', 'PS2_EE_RENDER_WAIT_DIAGNOSTICS=1']
                                   if args.render_wait_diagnostics and not args.boundary_diagnostics else []) +
                                  (['--env', 'PS2_GUEST_PC_PROFILE=1'] if args.guest_pc_diagnostics else []) +
                                  (['--env', 'PS2_VIF1_POOL_TRACE_FILE=' + str(out / 'pool_trace.bin')]
                                   if args.pool_store_trace else []) +
                                  (['--env', 'PS2_NATIVE_VIF1_WORKER=1'] if args.native_vif1_worker else []) +
                                  dead_flag_environment(args.vu_dead_flag_elimination) +
                                  vblank_environment(args.vblank_unpaced, out / 'vblank_unpaced_ready') +
                                  gs_cut_environment(args.gs_skip_fullscreen_blends,
                                                     args.gs_suppress_texture_invalidation,
                                                     out / 'gs_cut_ready') +
                                  vif_fence_profile_environment(args.vif_fence_profile,
                                                                out / 'vif_fence_ready') +
                                  (['--env', 'PS2_PAD_TRACE=0', '--env', 'PS2_MPEG_TRACE=0']
                                   if args.quiet_runtime_traces else []) +
                                  (['--env', 'PS2_VIF1_DMA_JOB_CAPTURE=' + str(out / 'jobs.bin'),
                                    '--env', 'PS2_VIF1_DMA_JOB_CAPTURE_GATE=' + str(out / 'capture_ready')]
                                   if args.dma_job_capture else []) +
                                  (['--env', 'NOBLE_ENGINE_SEAM_CAPTURE_GATE=' + (out / 'capture_ready').as_posix(),
                                    '--env', 'NOBLE_ENGINE_SEAM_JOB_CAPTURE=' + (out / 'jobs.bin').as_posix()]
                                   if args.engine_seam_capture else []) +
                                  (['--env', 'NOBLE_ENGINE_PROVENANCE_GATE=' + (out / 'capture_ready').as_posix(),
                                    '--env', 'NOBLE_ENGINE_PROVENANCE_FILE=' + (out / 'provenance.bin').as_posix()]
                                   if args.engine_provenance_capture else []) +
                                  (['--env', 'PS2_CRT_REQUEST_TRACE_FILE=' + str(out / 'crt_requests.bin')]
                                   if args.crt_request_trace else []) +
                                 (['--env', 'PS2_VU_JIT_MAP_FILE=' + str(out / 'native_jit.jsonl')]
                                  if args.profile_jit_thread else []) +
                                 (['--show-window'] if args.show_window else []) +
                                 (['--honor-timer-resolution'] if args.honor_timer_resolution else []),
                                 cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
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
                                           '--skip-movie-after', '3', '--skip-movie-hold', str(args.skip_movie_hold)] +
                                          (['--observe-render-gate'] if args.boundary_diagnostics else []),
                                          cwd=ROOT, stdout=driver_log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 480
            while time.monotonic() < deadline:
                rows = samples(out)
                if rows and rows[-1].get('state') in ([4, 10, 3, 1], [4, 10, 3, 3]):
                    break
                if probe.poll() is not None:
                    raise RuntimeError('Probe exited before gameplay')
                time.sleep(1)
            else:
                raise RuntimeError('No gameplay reached')
            print('Gameplay reached; waiting 15s before protected measurement', flush=True)
            time.sleep(15)
            if args.vblank_unpaced:
                (out / 'vblank_unpaced_ready').write_text(
                    'Protected gameplay reached; enable diagnostic unpaced VBLANK\n')
            if args.gs_skip_fullscreen_blends or args.gs_suppress_texture_invalidation:
                (out / 'gs_cut_ready').write_text(
                    'Protected gameplay reached; enable requested GS diagnostic cut\n')
            if args.vif_fence_profile:
                (out / 'vif_fence_ready').write_text(
                    'Protected gameplay reached; enable aggregate VIF fence profile\n')
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
            if args.gs_ring_telemetry:
                sys.path.insert(0, str(ROOT / 'tools/native_render'))
                from pgs_ring_telemetry import OwnedReader, interval as ring_interval
                ring_reader = OwnedReader(out)
            cpu_start = psutil.cpu_times()
            process_start = process.cpu_times()
            power['performance_monotonic'] = time.monotonic()
            ring_start = ring_reader.read() if ring_reader else None
            if args.gs_direct_gpu:
                (out / 'timed_window_active').write_text('Diagnostic image downloads paused during measurement\n')
            if args.native_census:
                (out / 'census_ready').write_text('Gameplay diagnostic only\n')
            if args.vif_worker_latency:
                (out / 'vif_causal_ready').write_text('Gameplay diagnostic only\n')
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
            ring_end = ring_reader.read() if ring_reader else None
            if args.gs_direct_gpu:
                (out / 'timed_window_active').unlink(missing_ok=True)
            if args.native_census:
                (out / 'census_ready').unlink(missing_ok=True)
            if args.vif_worker_latency:
                (out / 'vif_causal_ready').unlink(missing_ok=True)
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
            result['native_vif1_worker'] = args.native_vif1_worker
            result['diagnostic_only'] = args.diagnostic_jit or args.diagnostic_timing
            result['measurement_gate_used'] = args.measurement_gate
            if ring_reader:
                renderer = ring_interval(ring_start['counters'], ring_end['counters'],
                                        ring_end['monotonic'] - ring_start['monotonic'])
                renderer.update(start_read=ring_start, end_read=ring_end,
                                telemetry_tool_sha256=hashlib.sha256(
                                    (ROOT / 'tools/native_render/pgs_ring_telemetry.py').read_bytes()).hexdigest())
                (out / 'renderer_fresh_result.json').write_text(json.dumps(renderer, indent=2))
                result['renderer_fresh_fps'] = renderer['fresh_fps']
                result['renderer_repeated_frames'] = renderer['repeated_frames']
                result['guest_and_fresh_target_met'] = bool(result['guest_fps'] is not None
                    and result['guest_fps'] >= 58 and renderer['fresh_target_met'])
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
                sampler = [sys.executable, str(ROOT / 'tools/profiling/sample_owned_callers.py'),
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
                if args.profile_suspended_stack:
                    sampler += ['--stack-while-suspended', '--stack-bytes', '256']
                subprocess.run(sampler, cwd=ROOT, check=True)
                (profile / 'window.json').write_text(json.dumps(dict(
                    start=profile_start, end=time.monotonic(),
                    fps_window_end=power['measurement_end_monotonic']), indent=2))
            if args.exercise_gameplay_input:
                sys.path.insert(0, str(ROOT / 'tools'))
                from probe_headless import send_button
                if process.create_time() != identity['creation_time'] or Path(process.exe()) != Path(identity['executable']):
                    raise RuntimeError('Probe identity changed before gameplay input')
                images = list(out.glob('frame_*.png'))
                before_image = max(images, key=lambda p: p.stat().st_mtime_ns).name if images else None
                movement = dict(pid=identity['pid'], button='right', hold_seconds=2.0,
                                before_image=before_image, start_monotonic=time.monotonic(),
                                fps_window_complete=True, profile_complete=True)
                movement['delivered'] = send_button(identity['pid'], 'right', 2.0)
                (out / 'gameplay_input.json').write_text(json.dumps(movement, indent=2))
                if not movement['delivered']:
                    raise RuntimeError('Owned gameplay window ended before input could be delivered')
                time.sleep(4)
                images = list(out.glob('frame_*.png'))
                movement['after_image'] = max(images, key=lambda p: p.stat().st_mtime_ns).name if images else None
                movement['end_monotonic'] = time.monotonic()
                movement['visual_movement_verified'] = False  # Requires independent image inspection.
                (out / 'gameplay_input.json').write_text(json.dumps(movement, indent=2))
        finally:
            if args.native_census:
                (out / 'census_ready').unlink(missing_ok=True)
            if ring_reader:
                ring_reader.close()
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
