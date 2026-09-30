import subprocess
import time
import sys

def main():
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    stdout_file = sys.argv[2] if len(sys.argv) > 2 else 'stdout_test6.log'
    stderr_file = sys.argv[3] if len(sys.argv) > 3 else 'stderr_test6.log'
    
    print(f"[Runner] Launching NobleArchimedes.exe for {seconds}s...")
    with open(stdout_file, 'wb') as out_f, open(stderr_file, 'wb') as err_f:
        p = subprocess.Popen(['./NobleArchimedes.exe'], stdout=out_f, stderr=err_f)
        time.sleep(seconds)
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
    print(f"[Runner] Finished running for {seconds}s.")

if __name__ == '__main__':
    main()
