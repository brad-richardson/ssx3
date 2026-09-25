#!/usr/bin/env python3
"""Condense a boot.log: [diag:watch] hits (+ ra/regs summary) tagged with the last [vsync-rate] tick."""
import re, sys
tick = 0
rt = re.compile(r'\[vsync-rate\] tick=(\d+)')
for line in open(sys.argv[1], errors='replace'):
    m = rt.search(line)
    if m:
        tick = int(m.group(1)); continue
    if line.startswith('[diag:watch]'):
        print('t%-6d %s' % (tick, line[13:].strip()))
    elif line.startswith('[rd1:regs]') and len(sys.argv) > 2:
        f = dict(kv.split('=') for kv in line.split()[1:])
        print('        a0=%s a1=%s a2=%s a3=%s s0=%s s1=%s s2=%s v0=%s v1=%s' % tuple(f.get(k) for k in 'a0 a1 a2 a3 s0 s1 s2 v0 v1'.split()))
    elif 'missing-target' in line:
        print('t%-6d %s' % (tick, line[:300].strip()))
