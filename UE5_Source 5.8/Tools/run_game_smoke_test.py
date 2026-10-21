#!/usr/bin/env python3
"""Run the game headlessly in UE5 and assert the in-game smoke test.

Launches UnrealEditor in game mode on the default chapter map with the
``-NATestCombat`` smoke test enabled (see AHectorCharacter::RunCombatSmokeTest),
waits for it to finish, then checks the log for the expected results.

Usage:
    python Tools/run_game_smoke_test.py [--seconds 40] [--map /Game/Maps/...]

Exit code 0 means every check passed.
"""
import argparse
import os
import re
import subprocess
import sys
import time

UE_ROOT = r"C:\Program Files\Epic Games\UE_5.8"
EDITOR = os.path.join(UE_ROOT, "Engine", "Binaries", "Win64", "UnrealEditor.exe")
PROJECT = r"C:\Projects\NobleArchimedes\NobleArchimedes.uproject"
LOG = r"C:\Projects\NobleArchimedes\Saved\Logs\NobleArchimedes.log"

# Markers that must appear for the run to count as a pass.
REQUIRED = [
    ("spawned enemy", r"NA-TEST: spawned enemy"),
    ("light attack 1", r"NA-TEST: light attack 1"),
    ("light attack 2", r"NA-TEST: light attack 2"),
    ("combo montage played", r"NA-ANIM: combo stage 1 -> AM_Hector_Light1"),
    ("enemy hp report", r"NA-TEST: enemy hp="),
    ("item drops", r"NA-TEST: item drops in world="),
    ("innocent devil", r"NA-TEST: active innocent devil="),
    ("damage taken", r"NA-TEST: player hp after 10 damage="),
    ("save/load", r"NA-TEST: save-load"),
]

# Failures that invalidate the run even when the markers appear.
FORBIDDEN = [
    ("failed enemy spawn", r"NA-TEST: failed to spawn"),
    ("missing montage", r"NA-ANIM: .*has no (combo|finisher) montage"),
    ("null anim instance", r"AnimInstance.*(null|invalid)"),
    ("montage play failure", r"LogAnimation:.*(Failed|Error).*Montage"),
    ("script error", r"LogPython: Error"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=40.0,
                        help="how long to let the game run before terminating")
    parser.add_argument("--map", default="/Game/Maps/Chap_01_AbandonedCastle")
    args = parser.parse_args()

    if not os.path.exists(EDITOR):
        print("FAIL: editor not found at %s" % EDITOR)
        return 1

    if os.path.exists(LOG):
        os.remove(LOG)

    cmd = [
        EDITOR, PROJECT, args.map,
        "-game", "-nullrhi", "-unattended", "-nosplash", "-nop4", "-nosound",
        "-NATestCombat", "-stdout", "-FullStdOutLogOutput",
    ]
    print("launching: %s" % " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

    deadline = time.time() + args.seconds
    saw_report = False
    while time.time() < deadline:
        time.sleep(1.0)
        if os.path.exists(LOG):
            try:
                with open(LOG, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            if "NA-TEST: save-load" in text:
                saw_report = True
                break

    # Give the report timer a moment to flush before shutting the game down.
    time.sleep(2.0)
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()

    if not os.path.exists(LOG):
        print("FAIL: no log written at %s" % LOG)
        return 1

    with open(LOG, "r", encoding="utf-8", errors="ignore") as fh:
        text = fh.read()

    failures = []
    for label, pattern in REQUIRED:
        if re.search(pattern, text):
            print("  PASS  %s" % label)
        else:
            print("  FAIL  %s (pattern %r)" % (label, pattern))
            failures.append(label)

    if not saw_report:
        failures.append("smoke test did not reach its report")
        print("  FAIL  smoke test did not reach its report")

    for label, pattern in FORBIDDEN:
        match = re.search(pattern, text)
        if match:
            print("  FAIL  %s (%s)" % (label, match.group(0)))
            failures.append(label)

    # Report gameplay lines so regressions are visible in the transcript.
    for line in text.splitlines():
        if "NA-TEST:" in line:
            print("  | " + line.split("]:", 1)[-1].strip())

    if failures:
        print("RESULT: FAIL (%d)" % len(failures))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
