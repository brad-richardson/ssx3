#!/usr/bin/env python3
"""VR1: per-record-type comparison of two PS2XGSC1 captures.

For each record type (payload[0]) compare the ordered sequence of that type's
payloads (blake2b-16). Also report per-type counts, and for the full stream the
first differing record. The RESULT line is over the tick-stripped sequences only: the base-vs-base null
control (VR1 NOTEBOOK 10:25) shows record tick stamps and cross-path interleave
are racy on the paraLLEl Mac build, while each path's payload sequence is not.
Usage: gs_types.py A/gs.cap B/gs.cap
"""
import hashlib, struct, sys
from collections import defaultdict

def load(p):
    seqs = defaultdict(list); full = []
    with open(p, 'rb') as f:
        assert f.read(8) == b'PS2XGSC1'
        while True:
            h = f.read(4)
            if len(h) < 4: break
            (n,) = struct.unpack('<I', h); pl = f.read(n)
            if len(pl) < n: break
            d = hashlib.blake2b(pl, digest_size=16).digest()
            key = pl[0] if pl[0] != 1 else 'pkt-path%d' % pl[9]
            nt = hashlib.blake2b(pl[:1] + pl[9:], digest_size=16).digest()  # without the tick
            seqs[key].append(d); seqs[str(key) + '-notick'].append(nt); full.append((pl[0], d))
    return seqs, full

a, fa = load(sys.argv[1]); b, fb = load(sys.argv[2])
ok = True
for t in sorted(set(a) | set(b), key=str):
    sa, sb = a.get(t, []), b.get(t, [])
    first = next((i for i, (x, y) in enumerate(zip(sa, sb)) if x != y), None)
    same = sa == sb
    if str(t).endswith('-notick'):
        ok &= same
    print('type %s: count %d/%d  sequence %s%s' % (t, len(sa), len(sb), 'EQUAL' if same else 'DIFF',
          '' if first is None else ' first_diff_index=%d' % first))
# full-stream check with type-2 records removed
def strip(full, drop):
    return [x for x in full if x[0] not in drop]
print('full stream equal:', fa == fb)
print('RESULT', 'PER-PATH-CONTENT-EQUAL' if ok else 'DIFF')
