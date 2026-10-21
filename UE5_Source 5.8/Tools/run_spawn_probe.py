#!/usr/bin/env python3
"""Headless probe for the Chapter 1 spawn regression.

Launches the game with -NATestSpawn and waits for AHectorCharacter::RunSpawnProbe
to report how many enemies the entrance hall spawned and how far the player
could walk from the PlayerStart. Exits 0 on PASS.
"""
import os
import subprocess
import sys
import time

UE_ROOT = r"C:\Program Files\Epic Games\UE_5.8"
EDITOR = os.path.join(UE_ROOT, "Engine", "Binaries", "Win64", "UnrealEditor.exe")
PROJECT = r"C:\Projects\NobleArchimedes\NobleArchimedes.uproject"
LOG = r"C:\Projects\NobleArchimedes\Saved\Logs\NobleArchimedes.log"
MAP = "/Game/Maps/Chap_01_AbandonedCastle"


def main():
    if os.path.exists(LOG):
        try:
            os.remove(LOG)
        except OSError:
            pass

    cmd = [
        EDITOR, PROJECT, MAP,
        "-game", "-nullrhi", "-unattended", "-nosplash", "-nop4", "-nosound",
        "-NATestSpawn", "-stdout", "-FullStdOutLogOutput",
    ]
    print("launching: %s" % " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    deadline = time.time() + 90
    result = None
    while time.time() < deadline:
        time.sleep(1.0)
        if not os.path.exists(LOG):
            continue
        try:
            with open(LOG, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if "NATEST_SPAWN RESULT" in text:
            result = text
            break

    proc.kill()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass

    if not result:
        print("FAIL: no NATEST_SPAWN result before timeout")
        return 1

    for line in result.splitlines():
        if "NATEST_SPAWN" in line or "NATEST_MOVE" in line:
            print(line.split("]", 1)[-1].strip())

    if "NATEST_SPAWN RESULT PASS" in result:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
