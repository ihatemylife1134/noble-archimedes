"""Run ordinary-input menu probes serially, restoring any temporary power plan."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid


def active_power_plan():
    report = subprocess.check_output(["powercfg", "/getactivescheme"], text=True)
    return re.search(r"[0-9a-fA-F-]{36}", report)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seconds", type=int, default=80)
    parser.add_argument("--scenario", choices=("menu", "name", "game"), action="append")
    parser.add_argument("--power-plan", type=uuid.UUID)
    parser.add_argument("--env", action="append", default=[],
                        help="Pass a PS2_NAME=value setting to each headless probe")
    parser.add_argument("--observe-render-gate", action="store_true")
    parser.add_argument("--cursor-test", action="store_true",
                        help="Exercise cursor movement during the name-entry probe")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    scenarios = args.scenario or ["menu", "name"]
    if len(set(scenarios)) != len(scenarios):
        parser.error("Each scenario must be selected once")
    if any((out / scenario / "pid.txt").exists() for scenario in scenarios):
        parser.error("Use a fresh output directory for each scenario run")
    out.mkdir(parents=True, exist_ok=True)
    original_plan = active_power_plan()
    with args.exe.open("rb") as executable:
        executable_hash = hashlib.file_digest(executable, "sha256").hexdigest()
    manifest = {"exe": str(args.exe.resolve()), "sha256": executable_hash,
                "original_power_plan": original_plan, "runs": []}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    try:
        if args.power_plan:
            subprocess.run(["powercfg", "/setactive", str(args.power_plan)], check=True)
        manifest["test_power_plan"] = active_power_plan()
        for scenario in scenarios:
            directory = out / scenario
            directory.mkdir(parents=True)
            with (directory / "probe_launch.log").open("w") as probe_log, \
                    (directory / "driver_launch.log").open("w") as driver_log:
                started = time.monotonic()
                probe_args = [sys.executable, "-u", str(root / "tools/probe_headless.py"),
                                          str(args.exe.resolve()), str(directory),
                                          "--seconds", str(args.seconds), "--gs-threads", "2",
                                          "--env", "PS2_FRAME_DUMP_PREFIX="]
                for setting in args.env:
                    probe_args.extend(("--env", setting))
                probe = subprocess.Popen(probe_args,
                                         cwd=root, stdout=probe_log, stderr=subprocess.STDOUT)
                driver_args = [] if scenario == "game" else [f"--{scenario}-only"]
                if args.observe_render_gate:
                    driver_args.append("--observe-render-gate")
                if args.cursor_test:
                    driver_args.append("--cursor-test")
                driver = None
                try:
                    driver = subprocess.Popen([sys.executable, "-u", str(root / "tools/probe_new_game.py"),
                                               str(directory), *driver_args], cwd=root,
                                              stdout=driver_log, stderr=subprocess.STDOUT)
                    probe_code = probe.wait()
                    try:
                        driver_code = driver.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        driver.terminate()
                        driver_code = driver.wait(timeout=10)
                    manifest["runs"].append({"scenario": scenario, "probe_exit": probe_code,
                                             "driver_exit": driver_code,
                                             "wall_seconds": time.monotonic() - started})
                    print(json.dumps(manifest["runs"][-1]), flush=True)
                finally:
                    for child in (probe, driver):
                        if child is not None and child.poll() is None:
                            child.terminate()
                            child.wait(timeout=10)
    finally:
        if args.power_plan:
            subprocess.run(["powercfg", "/setactive", original_plan], check=True)
        manifest["restored_power_plan"] = active_power_plan()
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return int(any(run["probe_exit"] or run["driver_exit"] for run in manifest["runs"]))


if __name__ == "__main__":
    raise SystemExit(main())
