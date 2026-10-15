"""Measure actual gameplay frames from a running probe's guest phase counter.

Example: python tools/native_vu/measure_gameplay.py output/fps60/my_probe
         --performance-power
The optional power-plan change is bounded and restored in finally.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time


def samples(out):
    path = out / 'phase_samples.jsonl'
    if not path.exists():
        return []
    result = []
    for line in path.read_text().splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # The driver can be writing its last line.
    return result


def calculate(rows, start, end, settle=10):
    rows = [r for r in rows if start + settle <= r['monotonic'] <= end
            and r.get('phase_index') == 0 and r.get('phase') == 4
            and r.get('state') == [4, 10, 3, 1]
            and not r.get('phase_invalid')]
    if len(rows) < 2:
        raise RuntimeError('No sustained gameplay counter interval was captured')
    first, last = rows[0], rows[-1]
    seconds = last['monotonic'] - first['monotonic']
    if seconds < 30 or any(b['phase_frames'] < a['phase_frames']
                           for a, b in zip(rows, rows[1:])):
        raise RuntimeError('Gameplay interval is too short or the counter reset')
    frames = last['phase_frames'] - first['phase_frames']
    return dict(guest_frames=frames, measured_seconds=seconds,
                guest_fps=frames / seconds, first=first, last=last)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    parser.add_argument('--performance-power', action='store_true')
    parser.add_argument('--start-after', type=float, default=200,
                        help='Minimum probe age before measuring settled gameplay')
    args = parser.parse_args()
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        rows = samples(args.out)
        if rows and rows[-1].get('state') == [4, 10, 3, 1] and rows[-1]['driver_seconds'] >= args.start_after:
            break
        if (args.out / 'exit.json').exists():
            raise RuntimeError('Probe ended before the sustained gameplay measurement')
        time.sleep(1)
    else:
        raise RuntimeError('Timed out waiting for gameplay')
    original = re.search(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',
                         subprocess.check_output(['powercfg', '/getactivescheme'], text=True), re.I).group()
    power = dict(original=original, changed=args.performance_power)
    try:
        if args.performance_power:
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True)
        power['performance_monotonic'] = time.monotonic()
        (args.out / 'power_comparison.json').write_text(json.dumps(power, indent=2))
        print('Measuring sustained gameplay for 55 seconds', flush=True)
        time.sleep(55)
    finally:
        power['measurement_end_monotonic'] = time.monotonic()
        if args.performance_power:
            subprocess.run(['powercfg', '/setactive', original], check=True)
        power['restored_monotonic'] = time.monotonic()
        (args.out / 'power_comparison.json').write_text(json.dumps(power, indent=2))
    result = calculate(samples(args.out), power['performance_monotonic'], power['measurement_end_monotonic'])
    result['power_plan'] = power
    (args.out / 'steady_gameplay_result.json').write_text(json.dumps(result, indent=2))
    print(f"Actual guest gameplay: {result['guest_fps']:.2f} FPS over {result['measured_seconds']:.2f}s", flush=True)


if __name__ == '__main__':
    main()
