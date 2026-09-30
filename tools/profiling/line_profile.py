"""Source-line histogram of RIP samples from a -g build.

Usage: line_profile.py <exe> <samples.txt> [top]
Samples are image-relative RVAs (one hex value per line), as written by the
gs_sprite_raster_bench sampler.
"""
import ntpath
import subprocess
import sys
from collections import Counter

exe, path = sys.argv[1], sys.argv[2]
top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 30
rvas = [int(line, 16) for line in open(path) if line.strip() and not line.startswith('module')]
counts = Counter(rvas)
hot = counts.most_common(600)
addresses = ['0x%x' % (0x140000000 + rva) for rva, _ in hot]
output = subprocess.run(['addr2line', '-e', exe, *addresses], text=True, capture_output=True).stdout.splitlines()
by_line = Counter()
for (rva, n), where in zip(hot, output):
    by_line[ntpath.basename(where.replace('/', '\\'))] += n
total = len(rvas)
for where, n in by_line.most_common(top_n):
    print(f'{100.0 * n / total:5.1f}%  {where}')
print('samples', total)
