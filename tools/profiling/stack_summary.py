"""Summarize candidate stack frames of every thread in a set of minidumps.

Usage: python stack_summary.py <exe> <dump> [<dump> ...]
Heuristic scan (as in the earlier native_stack tooling): the instruction pointer
plus executable return-address candidates on the stack are symbolized with nm.
Threads whose frames include EeScheduler::run are reported as the EE thread.
"""
import struct
import subprocess
import sys
from bisect import bisect_right
from collections import Counter

from minidump.minidumpfile import MinidumpFile

PREFERRED_BASE = 0x140000000


def load_symbols(exe):
    out = subprocess.run(['nm', '-n', '-C', exe], text=True, capture_output=True, check=True).stdout
    symbols = []
    for line in out.splitlines():
        fields = line.split(maxsplit=2)
        if len(fields) == 3 and fields[1] in ('T', 't'):
            try:
                symbols.append((int(fields[0], 16), fields[2]))
            except ValueError:
                pass
    symbols.sort()
    return [a for a, _ in symbols], [n for _, n in symbols]


def main():
    exe, dumps = sys.argv[1], sys.argv[2:]
    addrs, names = load_symbols(exe)
    ee_top = Counter()
    for path in dumps:
        dump = MinidumpFile.parse(path)
        reader = dump.get_reader()
        module = dump.modules.modules[0]
        ntdll = next((m for m in dump.modules.modules if m.name.lower().endswith('ntdll.dll')), None)

        def sym(loaded):
            if module.baseaddress <= loaded < module.baseaddress + module.size:
                va = PREFERRED_BASE + loaded - module.baseaddress
                i = bisect_right(addrs, va) - 1
                return names[i] if i >= 0 else '<exe?>'
            for m in dump.modules.modules:
                if m.baseaddress <= loaded < m.baseaddress + m.size:
                    return '<' + m.name.split('\\')[-1] + '>'
            return None

        print(f'== {path}')
        for thread in dump.threads.threads:
            ctx = thread.ContextObject
            start = ctx.Rsp
            end = thread.Stack.StartOfMemoryRange + thread.Stack.DataSize
            size = min(max(end - start, 0), 65536)
            try:
                stack = reader.read(start, size) if size else b''
            except Exception:
                stack = b''
            frames = [sym(ctx.Rip) or f'0x{ctx.Rip:x}']
            for off in range(0, len(stack) - 7, 8):
                value = struct.unpack_from('<Q', stack, off)[0]
                s = sym(value)
                if s and s.startswith('<') is False:
                    if frames[-1] != s:
                        frames.append(s)
                if len(frames) >= 40:
                    break
            is_ee = any('EeScheduler::run' in f for f in frames)
            if is_ee:
                # first exe frame and the first few distinct frames summarize the wait site
                ee_top[' <- '.join(frames[:6])] += 1
                print(f'  EE thread {thread.ThreadId}:')
                for f in frames[:18]:
                    print(f'      {f[:150]}')
    print('\n== EE thread top-of-stack histogram')
    for key, count in ee_top.most_common():
        print(f'{count:3d}  {key[:400]}')


if __name__ == '__main__':
    main()
