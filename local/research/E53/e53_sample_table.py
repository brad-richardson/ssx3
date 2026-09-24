#!/usr/bin/env python3
"""E53 Part 2: GameThread profile from a macOS `sample` file.
Prints the top-N functions by self samples, and the inclusive share under
PS2Runtime::executeVU0Microprogram (outermost frames only) with its top
callees by inclusive samples."""
import re, sys, collections
path = sys.argv[1]; topn = int(sys.argv[2]) if len(sys.argv) > 2 else 25
lines = open(path, errors='replace').read().splitlines()
start = next(i for i, l in enumerate(lines) if re.search(r'^\s+\d+ Thread_\d+: GameThread', l))
node = re.compile(r'^(\s+)([+!:| ]*)(\d+) (.+?)  \(in ([^)]+)\)')
nodes = []  # (depth, count, name)
total = int(re.search(r'^\s+(\d+)', lines[start]).group(1))
for l in lines[start + 1:]:
    if re.search(r'^\s+\d+ Thread_', l) or not l.strip():
        break
    m = node.match(l)
    if not m:
        continue
    depth = len(m.group(1)) + len(m.group(2))
    name = re.sub(r'\s+\+\s*\d+.*$', '', m.group(4)).strip()
    nodes.append((depth, int(m.group(3)), name))
selfc = collections.Counter()
for i, (d, c, n) in enumerate(nodes):
    child = 0
    for d2, c2, _ in nodes[i + 1:]:
        if d2 <= d:
            break
        # direct children only: depth strictly greater, count only the first level below
    # compute direct children
    j = i + 1; cd = None
    while j < len(nodes) and nodes[j][0] > d:
        if cd is None:
            cd = nodes[j][0]
        if nodes[j][0] == cd:
            child += nodes[j][1]
        j += 1
    selfc[n] += c - child
print(f'GameThread samples: {total} (1 ms interval, 10 s)\n')
print('| # | function (GameThread) | self samples | share |')
print('|---|---|---|---|')
for k, (n, c) in enumerate(selfc.most_common(topn), 1):
    print(f'| {k} | `{n[:110]}` | {c} | {100.0 * c / total:.1f}% |')
# inclusive under executeVU0Microprogram (outermost)
vu0 = 0; callee = collections.Counter(); i = 0
while i < len(nodes):
    d, c, n = nodes[i]
    if 'executeVU0Microprogram' in n:
        vu0 += c
        j = i + 1; cd = None
        while j < len(nodes) and nodes[j][0] > d:
            if cd is None:
                cd = nodes[j][0]
            if nodes[j][0] == cd:
                callee[nodes[j][2]] += nodes[j][1]
            j += 1
        i = j
        continue
    i += 1
print(f'\nInclusive under executeVU0Microprogram: {vu0} of {total} = {100.0 * vu0 / total:.1f}%\n')
print('| direct callee of executeVU0Microprogram | inclusive samples | share of thread |')
print('|---|---|---|')
for n, c in callee.most_common(12):
    print(f'| `{n[:110]}` | {c} | {100.0 * c / total:.1f}% |')
