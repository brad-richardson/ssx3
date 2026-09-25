#!/usr/bin/env python3
"""E57 (VR1: + generated VU1RecompImage rows): bucket a macOS `sample` report's top-of-stack counts (diagnostic).

Busy = all rows except kernel waits (workq/mach_msg/semaphore/semwait/psynch/start_wqthread).
Prints VU1Interpreter share of busy samples, the GS CPU backend share, and the VU1 rows.
"""
import re
import sys

WAIT = ('__workq_kernreturn', 'mach_msg2_trap', 'semaphore_wait_signal_trap',
        '__semwait_signal', '__psynch_mutexwait', 'start_wqthread', '__psynch_cvwait')
text = open(sys.argv[1]).read()
sec = text[text.index('Sort by top of stack'):]
rows = re.findall(r'^\s+(.+?)\s+\(in [^)]+\)\s+(\d+)$', sec, re.M)
busy = [(n, int(c)) for n, c in rows if not n.startswith(WAIT)]
total = sum(c for _, c in busy)
vu = [(n, c) for n, c in busy if n.startswith(('VU1Interpreter::', 'VU1RecompImage'))]
gen = sum(c for n, c in busy if n.startswith('VU1RecompImage'))
gs = sum(c for n, c in busy if n.startswith(('GSCpuBackend', 'GSMem', 'std::__function')))
vsum = sum(c for _, c in vu)
print('busy samples %d; VU1Interpreter %d = %.1f%%; GS CPU backend (+fn ptrs) %d = %.1f%%'
      % (total, vsum, 100.0 * vsum / total, gs, 100.0 * gs / total))
print('generated pair functions (VU1RecompImage) %d = %.1f%%' % (gen, 100.0 * gen / total))
from collections import Counter
agg = Counter()
for n, c in vu:
    agg['VU1RecompImage::f*' if n.startswith('VU1RecompImage') else n.split('(')[0]] += c
for n, c in agg.most_common():
    print('  %6d %5.1f%%  %s' % (c, 100.0 * c / total, n))
