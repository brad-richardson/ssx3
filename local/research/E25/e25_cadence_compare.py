"""Carried control: the complete-feed cadence reference, E25 vs E24 vs E23.

Beyond mission 3's list. It runs on the SURVIVING E23 fixture binary with the
reused observer, so it tests the retained artifacts and the environment, NOT
the rebuild. Recorded as a carried control so E26 knows the fixture still
behaves as E23 and E24 measured it.
"""
from e25_common import *

def rows(p):
    d = json.loads(Path(p).read_text())
    out = {}
    for r in d['rows']:
        c, f = r['cadence'], r['parser']['footer']
        out[r['feedBytes']] = dict(outcome=r['outcome'], rc=r['rc'],
            producerFirings=c['producerFirings'], addBs=c['addBs'],
            completions=c['completions'], completionsMatched=c['completionsMatched'],
            parks=c['parks'], parseCalls=f['parseCalls'], packets=f['packets'],
            frames=f['frames'], pending=f['pending'], errors=f['errors'],
            bindingChecks=f['bindingChecks'])
    return d, out

d24, r24 = rows(E.parent / 'E24/cadence.json')
d25, r25 = rows(E / 'cadence.json')
cmp = {}
for k in sorted(set(r24) | set(r25)):
    a, b = r24.get(k), r25.get(k)
    cmp[k] = dict(e24=a, e25=b, match=a == b)
ok = all(v['match'] for v in cmp.values())
save('cadence-compare.json', dict(utc=utc(), scope='carried control, beyond mission 3',
    binary_e24=d24['binary']['sha256'], binary_e25=d25['binary']['sha256'],
    binary_same=d24['binary']['sha256'] == d25['binary']['sha256'],
    observer_same=d24['observer']['sha256'] == d25['observer']['sha256'],
    cases=cmp, all_match=ok,
    e23_reference='60 STALLED / 120 STALLED / 180 SERVED / 240 SERVED, producerFirings=1 on all four'))
for k, v in cmp.items():
    print(f"  feed {k:>3}  {'MATCH' if v['match'] else 'DELTA'}  {v['e25']}")
print('binary identical to E24 run:', d24['binary']['sha256'] == d25['binary']['sha256'])
print('ALL MATCH:', ok)
print('# E25 CADENCE COMPARE TAIL COMPLETE')
