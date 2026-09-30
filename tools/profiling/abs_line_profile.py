"""Function and source-line histogram of absolute RIP samples (with module header).

Usage: abs_line_profile.py <exe> <samples.txt> [top]
"""
import collections
import ntpath
import subprocess
import sys

exe, path = sys.argv[1], sys.argv[2]
top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
base = None
rvas = []
for line in open(path):
    if line.startswith('module'):
        fields = line.split(maxsplit=3)
        if base is None and fields[3].strip().lower().endswith('.exe'):
            base = (int(fields[1], 16), int(fields[2], 16))
        continue
    if line.strip():
        address = int(line, 16)
        rvas.append(address - base[0] if base[0] <= address < base[0] + base[1] else -1)
total = len(rvas)
print('samples', total, 'outside exe', rvas.count(-1))
counts = collections.Counter(r for r in rvas if r >= 0)
hot = counts.most_common(3000)
out = subprocess.run(['addr2line', '-f', '-C', '-i', '-e', exe] + ['0x%x' % (0x140000000 + r) for r, _ in hot],
                     capture_output=True, text=True).stdout.splitlines()
# With -i, each address yields one or more (function, line) pairs; the first
# pair is the innermost inlined frame. Re-run without -i to split reliably.
out = subprocess.run(['addr2line', '-f', '-C', '-e', exe] + ['0x%x' % (0x140000000 + r) for r, _ in hot],
                     capture_output=True, text=True).stdout.splitlines()
by_line = collections.Counter()
by_fn = collections.Counter()
for i, (rva, n) in enumerate(hot):
    fn = out[2 * i]
    where = ntpath.basename(out[2 * i + 1].replace('/', '\\')).split(' ')[0]
    by_line[where] += n
    by_fn[fn[:100]] += n
for k, n in by_fn.most_common(15):
    print('%5.1f%% %s' % (100.0 * n / total, k))
print()
for k, n in by_line.most_common(top_n):
    print('%5.1f%% %s' % (100.0 * n / total, k))
