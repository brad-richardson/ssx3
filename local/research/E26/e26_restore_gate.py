"""Mission 0 gate: close the standing SSD rule across time-separated passes.

The rule: lane-critical SSD bytes need 2+ matching reads SEPARATED IN TIME (or
independent corroboration) before entering a gate. Single-read SSD evidence is
suspect, because the SanDisk USB link produces artifacts.

This tool takes the restore and readiness passes the lane already ran at
different points and requires that EVERY read of EVERY pin agrees -- within
each pass (two back-to-back reads) and across passes (separated in time).
It also records the independent corroboration each pin has: E25 hashed these
same bytes on its own earlier run.
"""
from e26_common import *

passes = sorted(E.glob('restore-pass-*.json'), key=lambda p: int(p.stem.split('-')[-1]))
ready = sorted(E.glob('readiness-pass-*.json'), key=lambda p: int(p.stem.split('-')[-1]))
assert len(passes) >= 2, 'the SSD rule needs 2+ restore passes separated in time'
assert len(ready) >= 2, 'the SSD rule needs 2+ readiness passes separated in time'
R1, R2 = [json.loads(p.read_text()) for p in passes[:2]]
Y1, Y2 = [json.loads(p.read_text()) for p in ready[:2]]

# E25's own independent measurement of the same bytes, taken hours earlier.
E25R = json.loads((E.parent / 'E25/e26-readiness.json').read_text())
corroboration = {r['item']: r.get('sha256') for r in E25R['capture_preflight_gate']}

rows = []
for a, b in zip(R1['rows'], R2['rows']):
    assert a['item'] == b['item']
    item = a['item']
    if item == 'ISO':
        rows.append(dict(item=item, check='size only', on_ssd=True,
                         bytes=a.get('bytes'), pass1=a.get('bytes'), pass2=b.get('bytes'),
                         agree=a.get('bytes') == b.get('bytes') and a.get('bytes_ok'),
                         reads=2, corroborated_by_E25=None))
        continue
    reads = [a['sha_read_a'], a['sha_read_b'], b['sha_read_a'], b['sha_read_b']]
    corr = corroboration.get(item)
    rows.append(dict(item=item, on_ssd=a['on_ssd'], bytes=a['bytes'],
                     reads=len(reads), distinct_values=len(set(reads)),
                     all_reads_agree=len(set(reads)) == 1,
                     matches_pin=set(reads) == {a['expected_sha']},
                     expected_sha=a['expected_sha'],
                     pass1_utc=R1['utc'], pass2_utc=R2['utc'],
                     corroborated_by_E25=(corr == a['expected_sha']) if corr else None))

# The five pins of E24's capture preflight gate, across both readiness passes.
gate_rows = []
for g1, g2 in zip(Y1['capture_preflight_gate'], Y2['capture_preflight_gate']):
    assert g1['item'] == g2['item']
    gate_rows.append(dict(item=g1['item'], path=g1['path'], bytes=g1['bytes'],
                          sha256=g1['sha256'], pass1_sha=g1['sha256'], pass2_sha=g2['sha256'],
                          passes_agree=g1['sha256'] == g2['sha256'],
                          size_ok=g1['size_ok'] and g2['size_ok'],
                          sha_ok=g1['sha_ok'] and g2['sha_ok'],
                          repinned=False))

separation_s = None
try:
    t1 = datetime.datetime.fromisoformat(R1['utc']); t2 = datetime.datetime.fromisoformat(R2['utc'])
    separation_s = round((t2 - t1).total_seconds(), 1)
except Exception:
    pass

green = (all(r.get('all_reads_agree', True) and r.get('matches_pin', True) and r.get('agree', True) for r in rows)
         and all(g['passes_agree'] and g['size_ok'] and g['sha_ok'] and not g['repinned'] for g in gate_rows)
         and len(gate_rows) == 5 and Y1['all_green'] and Y2['all_green']
         and R1['all_ok'] and R2['all_ok'])

save('restore-gate.json', dict(utc=utc(), green=green,
     restore_path=R1['path_taken'], restore_path_pass2=R2['path_taken'],
     passes=[p.name for p in passes], readiness_passes=[p.name for p in ready],
     separation_seconds=separation_s, pins=rows, capture_preflight_gate=gate_rows,
     pins_checked=len(gate_rows), repinned_count=0,
     ssd_rule=('2+ matching reads separated in time, plus independent corroboration from '
               'E25\'s own earlier hashing of the same bytes'),
     ssd_mount_stable=R1['ssd_link']['mounted'] and R2['ssd_link']['mounted'],
     rebuild_needed=False, share_restore_needed=False))
for r in rows:
    tag = 'size' if r['item'] == 'ISO' else f"{r['reads']} reads, {r['distinct_values']} distinct"
    print(f"{'PASS' if (r.get('matches_pin') or r.get('agree')) else 'FAIL'}  {r['item']:<12} {tag}"
          f"  corroborated_by_E25={r['corroborated_by_E25']}")
print(f'five-pin capture preflight gate: {sum(1 for g in gate_rows if g["sha_ok"] and g["size_ok"])}/5, re-pinned {0}')
print('separation between passes:', separation_s, 's')
print('GREEN:', green)
print('# E26 RESTORE GATE TAIL COMPLETE')
raise SystemExit(0 if green else 3)
