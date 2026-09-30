import subprocess
import time
import sys

print("[Launcher] Starting NobleArchimedes.exe on Windows Desktop...")
p = subprocess.Popen(["NobleArchimedes.exe"])
time.sleep(3)
if p.poll() is None:
    print(f"[Launcher] SUCCESS: NobleArchimedes.exe is RUNNING! (PID: {p.pid})")
else:
    print(f"[Launcher] ERROR: Process exited with code {p.returncode}")
    sys.exit(1)
