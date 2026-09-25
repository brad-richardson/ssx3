#!/usr/bin/env python3
"""RD1: map capture PATH1 packets (ordinal within the tick = probe `xgk` ordinal) to draw batches.
Usage: rd1_p1map.py <gs.stream> <tick> <batch#> [...]  -> per batch: p1 ordinals + packet sizes."""
import sys, struct
from collections import defaultdict
import rd1_draws as d
path, tick = sys.argv[1], int(sys.argv[2]); want = [int(x) for x in sys.argv[3:]]
sizes = {}
p1ord = {}
k = pk = 0
for kind, t, body in d.iter_cap(path, tick, tick):
    if kind == 1:
        if body[0] == 1:
            (sz,) = struct.unpack_from('<I', body, 1)
            p1ord[pk] = k; sizes[k] = sz; k += 1
        pk += 1
print('p1 packets', k, 'all packets', pk)
gs = d.load_cap(path, tick, tick)
bs = d.batches(gs.prims)
for i in want:
    seqs = sorted({p['seq'] for p in bs[i]['prims']})
    ords = [p1ord.get(s) for s in seqs]
    print('#%d n=%d p1 ords %s..%s (%d pkts) sizes %s' % (i, len(bs[i]['prims']), ords[0], ords[-1], len(ords),
          [sizes.get(o) for o in ords[:6]]))
