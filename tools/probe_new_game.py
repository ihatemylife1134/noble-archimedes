"""Drive the headless probe by observed guest menu state, not wall time."""
import re
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from probe_headless import send_button


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("out", type=Path)
parser.add_argument("--menu-seconds", type=float, default=3)
parser.add_argument("--cursor-test", action="store_true")
parser.add_argument("--menu-only", action="store_true", help="exercise the menu cursor without starting a game")
parser.add_argument("--name-only", action="store_true", help="observe name entry without accepting it")
parser.add_argument("--name-seconds", type=float, default=5,
                    help="Observe name entry before accepting it")
parser.add_argument("--observe-render-gate", action="store_true",
                    help="Read the original completion gate and swap deadline without modifying them")
parser.add_argument("--capture-gate-file", type=Path,
                    help="Open a VU capture gate after the observed post-movie 3D state")
parser.add_argument("--capture-gate-state", type=int, nargs=4, default=(4, 10, 3, 1),
                    help="Observed state that opens the capture gate; four decimal words")
parser.add_argument("--skip-movie-after", type=float,
                    help="Diagnostic only: request ordinary movie skip after this many seconds")
args = parser.parse_args()
if args.menu_only and args.name_only:
    parser.error("--menu-only and --name-only select different screens")
if args.capture_gate_file and args.capture_gate_file.exists():
    parser.error("--capture-gate-file must name a fresh, initially absent marker")
out = args.out
pid_deadline = time.monotonic() + 30
while not (out / "pid.txt").exists() and time.monotonic() < pid_deadline:
    time.sleep(0.25)
pid = int((out / "pid.txt").read_text())
reader = Path(__file__).resolve().with_name("probe_guest_ram.py")
words = (0xAC23A4, 0xAC23A8, 0xAC23AC, 0xAC23B0)
gate_words = (0xAD3F80, 0x9395C0, 0x9395B8, 0x9395BC, 0xA3DD30, 0xA3DD34,
              0xA3DD70, 0xA3DD18) if args.observe_render_gate else ()
last = None
notice_done = menu_done = name_done = save_done = False
notice_sent_at = 0.0
movie_seen_at = None
movie_skip_sent_at = None
capture_gate_open = False
start = time.monotonic()
with (out / "navigation.log").open("w", buffering=1) as log, \
        (out / "phase_samples.jsonl").open("w", buffering=1) as samples:
    timing_path = out / "timing.json"
    if timing_path.exists():
        timing = json.loads(timing_path.read_text())
        if timing.get("pid") == pid:
            print(f"probe_time_offset={start - timing['started_monotonic']:.3f}", file=log)
    while time.monotonic() - start < 600:
        result = subprocess.run([sys.executable, str(reader),
                                 "--base-file", str(out / "rdram_base.txt"), str(pid),
                                 *[hex(w) for w in (*words, *gate_words)]], capture_output=True, text=True)
        if result.returncode:
            # pid.txt precedes ELF loading; wait for the anchor during boot.
            if time.monotonic() - start < 30:
                time.sleep(1)
                continue
            print(result.stderr, file=log)
            break
        observed = tuple(int(v, 16) for v in re.findall(r"guest\[.*?\]=0x([0-9A-F]+)", result.stdout))
        state = observed[:len(words)]
        phase_index = re.search(r"phase_index=(\d+)", result.stdout)
        phase = re.search(r"phase=0x([0-9A-F]+) phase_frames=(\d+)", result.stdout)
        if phase_index:
            print(json.dumps({"monotonic": time.monotonic(), "driver_seconds": time.monotonic() - start,
                              "phase_index": int(phase_index[1]), "phase_invalid": phase is None,
                              "phase": int(phase[1], 16) if phase else None,
                              "phase_frames": int(phase[2]) if phase else None, "state": state,
                              "render_gate": dict(zip((hex(w) for w in gate_words), observed[len(words):]))}), file=samples)
        if state != last:
            print(f"t={time.monotonic()-start:.1f} state={state}", file=log)
            print(f"state={state}", flush=True)
            last = state
        if state == tuple(args.capture_gate_state) and args.capture_gate_file and not capture_gate_open:
            args.capture_gate_file.parent.mkdir(parents=True, exist_ok=True)
            args.capture_gate_file.write_text(f"pid={pid} monotonic={time.monotonic()} state={state}\n")
            print(f"t={time.monotonic()-start:.1f} capture gate opened state={state}", file=log)
            capture_gate_open = True
        if state == (4, 10, 7, 1):
            if movie_seen_at is None:
                movie_seen_at = time.monotonic()
            if args.skip_movie_after is not None and time.monotonic() - movie_seen_at >= args.skip_movie_after \
                    and (movie_skip_sent_at is None or time.monotonic() - movie_skip_sent_at >= 15):
                send_button(pid, "start", 0.3)
                time.sleep(0.5)
                send_button(pid, "cross", 0.3)
                movie_skip_sent_at = time.monotonic()
                print(f"t={time.monotonic()-start:.1f} diagnostic movie skip requested", file=log)
        if args.menu_only and state == (4, 7, 2, 0):
            for button in ("down", "up"):
                send_button(pid, button, 0.15)
                time.sleep(1)
            continue
        if args.name_only and state == (4, 7, 3, 1):
            if args.cursor_test:
                for button in ("down", "up"):
                    send_button(pid, button, 0.15)
                    time.sleep(1)
            else:
                time.sleep(1)
            continue
        if state == (4, 4, 1, 0) and (not notice_done or time.monotonic() - notice_sent_at > 30):
            if not notice_done:
                time.sleep(5)
                send_button(pid, "cross", 2)
                time.sleep(2)
            send_button(pid, "left", 2)
            time.sleep(2)
            send_button(pid, "cross", 2)
            notice_done = True
            notice_sent_at = time.monotonic()
        elif state == (4, 7, 2, 0) and not menu_done:
            time.sleep(args.menu_seconds)
            if args.cursor_test:
                for button in ("down", "up", "down", "up"):
                    send_button(pid, button, 0.15)
                    time.sleep(0.7)
                print("menu cursor inputs completed", file=log)
            send_button(pid, "cross", 0.3)
            menu_done = True
        elif state == (4, 7, 3, 1) and not name_done:
            # The cursor initially selects A. Enter one character before Accept.
            time.sleep(args.name_seconds)
            send_button(pid, "cross", 2)
            time.sleep(2)
            send_button(pid, "start", 2)
            time.sleep(2)
            send_button(pid, "cross", 2)
            time.sleep(3)
            send_button(pid, "cross", 2)
            name_done = True
            print("name confirmation accepted", file=log)
        elif state == (4, 7, 3, 2) and not save_done:
            time.sleep(5)
            send_button(pid, "triangle", 2)
            time.sleep(3)
            send_button(pid, "left", 2)
            time.sleep(2)
            send_button(pid, "cross", 2)
            save_done = True
            print("start without saving accepted; observing loading", file=log)
        time.sleep(1)
