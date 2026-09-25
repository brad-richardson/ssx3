#!/usr/bin/env python3
"""RP1: list PCSX2 T65 VU1 starts of one program whose TOPS header matches the carve-trail batches
(GIF tag regs 0x412, PRIM field 0x5c/0x5d...), with VF regs that differ across starts.
Usage: rp1_t65find.py t65-vu1-2.bin [tpc_hex]"""
import sys, struct
sys.path.insert(0, '/Users/brad/dev/ssx3/local/research/T65')
import importlib.util
spec = importlib.util.spec_from_file_location('t65a', '/Users/brad/dev/ssx3/local/research/T65/t65-analyze.py')
t65 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t65)
recs = t65.read_dump(sys.argv[1])
tpc = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x741
for r in recs:
    if r['tpc'] != tpc:
        continue
    q = t65.qwords(r['mem'])
    h0, h1 = q[r['tops']], q[r['tops'] + 1]
    print('seq=%d ee=%d tops=%#x hdr0=%s hdr1=%s' % (r['seq'], r['ee'], r['tops'], ' '.join('%08x' % w for w in h0),
          ' '.join('%08x' % w for w in h1)))
