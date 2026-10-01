"""Histogram of RIP samples by function.

Usage: symbolize_samples.py <exe> <samples.txt>
Samples are hex RIPs, one per line. Files that start with "module <base> <size>
<path>" lines hold absolute RIPs: executable addresses are symbolized with nm,
system DLL addresses through their export tables (pefile). Older files without
a module header hold executable-relative RVAs.
"""
import ntpath
import subprocess
import sys
from bisect import bisect_right
from collections import Counter

exe, path = sys.argv[1], sys.argv[2]
IMAGE_BASE = 0x140000000

syms = []
for line in subprocess.run(['nm', '-n', '-C', exe], text=True, capture_output=True).stdout.splitlines():
    f = line.split(maxsplit=2)
    if len(f) == 3 and f[1] in 'Tt':
        try:
            syms.append((int(f[0], 16), f[2]))
        except ValueError:
            pass
syms.sort()
starts = [a for a, _ in syms]

modules = []
rips = []
for text in open(path):
    if text.startswith('module '):
        _, base, size, name = text.rstrip('\n').split(' ', 3)
        modules.append((int(base, 16), int(size, 16), name))
    elif text.strip():
        rips.append(int(text, 16))
modules.sort()
exe_module = next((m for m in modules if m[2].lower().endswith('.exe')), None)

export_cache = {}


def dll_symbol(name, rva):
    if name not in export_cache:
        try:
            import pefile
            pe = pefile.PE(name, fast_load=True)
            pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
            exports = sorted((e.address, (e.name or b'?').decode()) for e in pe.DIRECTORY_ENTRY_EXPORT.symbols)
            export_cache[name] = (exports, [entry[0] for entry in exports])
        except Exception:
            export_cache[name] = ([], [])
    exports, addresses = export_cache[name]
    i = bisect_right(addresses, rva) - 1
    return f'{ntpath.basename(name)}!{exports[i][1]}' if i >= 0 else ntpath.basename(name)


counts = Counter()
for rip in rips:
    if modules:
        hit = next((m for m in modules if m[0] <= rip < m[0] + m[1]), None)
        if hit is None:
            counts['<unknown>'] += 1
            continue
        if hit is not exe_module:
            counts[dll_symbol(hit[2], rip - hit[0])] += 1
            continue
        va = IMAGE_BASE + rip - hit[0]
    else:
        va = IMAGE_BASE + rip
    i = bisect_right(starts, va) - 1
    counts[syms[i][1] if i >= 0 else '?'] += 1

total = len(rips)
for name, n in counts.most_common(25):
    print(f'{100.0 * n / total:5.1f}%  {n:6d}  {name[:140]}')
print('samples', total)
