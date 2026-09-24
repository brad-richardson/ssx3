#!/usr/bin/env python3
"""E53 Part 2: GameThread inclusive samples for outermost frames matching each
substring (a frame nested inside an earlier match of the same key is not
counted twice), plus the callers of __vfprintf."""
import re, sys, collections
path = sys.argv[1]
keys = ['executeVU0Microprogram', 'VU1Interpreter::execute', 'VU1Interpreter::resume', 'GS::processGIFPacket',
        'GSCpuBackend::Submit', '__vfprintf', 'wait', 'EeScheduler::run']
lines = open(path, errors='replace').read().splitlines()
start = next(i for i, l in enumerate(lines) if re.search(r'^\s+\d+ Thread_\d+: GameThread', l))
total = int(re.search(r'^\s+(\d+)', lines[start]).group(1))
node = re.compile(r'^(\s+)([+!:| ]*)(\d+) (.+?)  \(in ([^)]+)\)')
nodes = []
for l in lines[start + 1:]:
    if re.search(r'^\s+\d+ Thread_', l) or not l.strip():
        break
    m = node.match(l)
    if m:
        nodes.append((len(m.group(1)) + len(m.group(2)), int(m.group(3)), re.sub(r'\s+\+\s*\d+.*$', '', m.group(4)).strip()))
print(f'GameThread samples {total}')
for k in keys:
    s = 0; i = 0; vu1viaVu0 = 0
    while i < len(nodes):
        d, c, n = nodes[i]
        if k.lower() in n.lower() if k == 'wait' else k in n:
            s += c
            j = i + 1
            while j < len(nodes) and nodes[j][0] > d:
                j += 1
            i = j
            continue
        i += 1
    print(f'| `{k}` | {s} | {100.0 * s / total:.1f}% |')
# callers of __vfprintf: the frame above each __vfprintf leaf chain (first non-libc parent)
par = collections.Counter(); stack = []
for d, c, n in nodes:
    while stack and stack[-1][0] >= d:
        stack.pop()
    if n == '__vfprintf':
        for sd, sn in reversed(stack):
            if not any(x in sn for x in ('printf', 'vfprintf', 'fprintf', '__v', 'snprintf')):
                par[sn] += c
                break
    stack.append((d, n))
print('__vfprintf callers:', [(n[:80], c) for n, c in par.most_common(5)])
