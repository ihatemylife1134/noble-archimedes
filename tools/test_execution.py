import subprocess
import time
import os
import sys
from pathlib import Path

print("[Test] Launching NobleArchimedes.exe...")

with open("stdout.log", "w") as out_f, open("stderr.log", "w") as err_f:
    p = subprocess.Popen(["./NobleArchimedes.exe"], stdout=out_f, stderr=err_f)
    print(f"[Test] Process started with PID {p.pid}. Running for 12 seconds...")
    try:
        time.sleep(12)
    except KeyboardInterrupt:
        pass
    
    if p.poll() is None:
        print("[Test] Process still running smoothly. Terminating for diagnosis...")
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
    else:
        print(f"[Test] Process exited early with code {p.returncode}")

print("[Test] Analyzing stdout.log...")
if os.path.exists("stdout.log"):
    with open("stdout.log", "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        print(f"[Test] Total stdout lines: {len(lines)}")
        for l in lines[-40:]:
            print("  " + l.rstrip())

if os.path.exists("stderr.log"):
    with open("stderr.log", "r", encoding="utf-8", errors="ignore") as f:
        errs = f.read().strip()
        if errs:
            print("[Test] stderr.log contents:")
            print(errs[:2000])

if os.path.exists("noble_archimedes_preview.png"):
    stat = os.stat("noble_archimedes_preview.png")
    print(f"[Test] Screenshot preview exists! Size: {stat.st_size} bytes, modified: {stat.st_mtime}")
