#!/usr/bin/env python3
"""VR3: split a macOS `sample` call graph under one function (diagnostic).

Usage: vr3_tree.py sample.txt [ROOT_SUBSTRING=PS2Runtime::executeVU0Microprogram]

Parses the call-graph section (indent = depth, first number = inclusive
samples). For every outermost node whose symbol contains ROOT, it adds the
node's inclusive count and each descendant's *self* count (inclusive minus
its children) by symbol. The root's own self count is its inlined code
(copy in/out, census branch). Busy samples = the top-of-stack rows minus
kernel waits (VB1's profile_share.py rule), so shares compare with VR2's.
Also prints the root's share of the GameThread's samples (wall, 15 s).
"""
import re
import sys
from collections import Counter

WAIT = ('__workq_kernreturn', 'mach_msg2_trap', 'semaphore_wait_signal_trap',
        '__semwait_signal', '__psynch_mutexwait', 'start_wqthread', '__psynch_cvwait')
path = sys.argv[1]
root = sys.argv[2] if len(sys.argv) > 2 else 'PS2Runtime::executeVU0Microprogram'
text = open(path).read()
graph = text[text.index('Call graph:'):text.index('Total number in stack')]
sec = text[text.index('Sort by top of stack'):]
tops = re.findall(r'^\s+(.+?)\s+\(in [^)]+\)\s+(\d+)$', sec, re.M)
busy = sum(int(c) for n, c in tops if not n.startswith(WAIT))

line_re = re.compile(r'^(?P<pre>[\s+!:|]*?)(?P<count>\d+)\s+(?P<name>.+?)(?:\s+\(in [^)]+\))?(?:\s+\+\s+\d+)?(?:\s+\[[^\]]+\])?(?:\s+[\w./-]+:\d+)?\s*$')
nodes = []  # (depth, count, name)
for raw in graph.splitlines()[1:]:
    m = line_re.match(raw)
    if not m:
        continue
    nodes.append((len(m.group('pre')), int(m.group('count')), m.group('name').strip()))

def short(name):
    name = re.sub(r'\(.*$', '', name)
    if name.startswith('VU1RecompImage'):
        return 'VU1RecompImage::*'
    if name.startswith('VU0RecompImage'):
        return 'VU0RecompImage::* (generated VU0 pairs)'
    return name

incl = 0
selfc = Counter()
i = 0
while i < len(nodes):
    depth, count, name = nodes[i]
    if root not in name:
        i += 1
        continue
    incl += count
    j = i + 1
    while j < len(nodes) and nodes[j][0] > depth:
        j += 1
    sub = nodes[i:j]
    for k, (d, c, n) in enumerate(sub):
        kids = 0
        child_depth = None
        for d2, c2, _ in sub[k + 1:]:
            if d2 <= d:
                break
            if child_depth is None:
                child_depth = d2
            if d2 == child_depth:
                kids += c2
        selfc[short(n) + (' [root self]' if k == 0 else '')] += c - kids
    i = j

gt = re.search(r'^\s+(\d+) Thread_\d+: GameThread', text, re.M)
game = int(gt.group(1)) if gt else 0
print('file %s' % path)
if game:
    print('GameThread samples %d; %s inclusive = %.2f%% of GameThread' % (game, root, 100.0 * incl / game))
print('busy samples %d; %s inclusive %d = %.2f%% of busy' % (busy, root, incl, 100.0 * incl / max(busy, 1)))
for n, c in selfc.most_common(40):
    if c:
        print('  %6d %6.2f%% busy %6.1f%% of root  %s' % (c, 100.0 * c / max(busy, 1), 100.0 * c / max(incl, 1), n))
