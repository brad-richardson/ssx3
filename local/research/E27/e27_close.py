"""E27 close: prove the two pin passes agree, account bytes, and emit the tail
receipt whose hashed prefix is every line ABOVE the tail-receipt header
(errata E24-E2: the row lives after the boundary and cannot invalidate itself)."""
import hashlib
from e27_common import *

p1 = json.loads((E / 'pins-pass-1.json').read_text())
p2 = json.loads((E / 'pins-pass-2.json').read_text())
by1 = {r['path']: r for r in p1['rows']}
by2 = {r['path']: r for r in p2['rows']}
assert set(by1) == set(by2)
mismatch = [p for p in by1 if by1[p]['sha256'] != by2[p]['sha256']]
gap_s = (datetime.datetime.fromisoformat(p2['utc']) -
         datetime.datetime.fromisoformat(p1['utc'])).total_seconds()
tracked = [r for r in p2['rows'] if r.get('git_object') is not None]
captures = [r for r in p2['rows'] if 'equals_committed_pin' in r]

files = sorted(x for x in E.iterdir() if x.is_file())
own_bytes = sum(x.stat().st_size for x in files)
own_alloc = sum(x.stat().st_blocks * 512 for x in files)

audit = dict(
  utc=utc(), lane='E27',
  pin_passes=dict(pass1_utc=p1['utc'], pass2_utc=p2['utc'],
                  separation_seconds=gap_s, files=len(by1),
                  mismatches=mismatch, all_equal=(not mismatch)),
  independent_corroboration=dict(
    git_tracked_equal=all(r['git_object'] == r['sha256'] for r in tracked),
    git_tracked=[Path(r['path']).name for r in tracked],
    captures_equal_committed_pins=all(r['equals_committed_pin'] for r in captures),
    captures=[Path(r['path']).name for r in captures],
    no_corroboration_available=[Path(r['path']).name for r in p2['rows']
                                if r['kind'].startswith('generated-source')],
    why='ps2xRuntime/src/runner is .gitignore(d) at .gitignore:21, so the generated guest '
        'sources have no content-addressed copy anywhere; two matching reads separated in '
        'time is the only check available and that is stated, not hidden.'),
  budget=dict(internal_bytes=own_bytes, internal_allocated=own_alloc,
              cap_bytes=512*M, within_cap=own_alloc <= 512*M,
              ssd_scratch_created=0, deletions=0),
  launches=dict(boots=0, lease_claims=0, probe_claims=0, builds=0, relinks=0,
                capture_driver_runs=0, suite_runs=0, stdbuf_uses=0),
  fork=dict(base=BASE_SHA, gate_open='fork-gate.json', gate_close='fork-gate-close.json',
            source_edits=0, commits=0, pushes=0),
  ssd_mounted_at_close=Path('/Volumes/Extreme SSD').is_dir(),
)
save('final-audit.json', audit)

rep = E / 'REPORT.md'
text = rep.read_text()
BOUND = '| Tail receipt | Value |'
prefix = text.split(BOUND)[0] if BOUND in text else text
sha_prefix = hashlib.sha256(prefix.encode()).hexdigest()
tail = dict(utc=utc(), file=str(rep), boundary=BOUND,
            prefix_lines=prefix.count('\n'), prefix_bytes=len(prefix.encode()),
            prefix_sha256=sha_prefix)
save('tail-receipt.json', tail)
print(json.dumps(dict(pins_all_equal=audit['pin_passes']['all_equal'],
                      separation_seconds=gap_s,
                      git_tracked_equal=audit['independent_corroboration']['git_tracked_equal'],
                      captures_equal=audit['independent_corroboration']['captures_equal_committed_pins'],
                      internal_allocated=own_alloc,
                      prefix_lines=tail['prefix_lines'],
                      prefix_bytes=tail['prefix_bytes'],
                      prefix_sha256=sha_prefix), indent=2))
print('# E27 CLOSE TAIL COMPLETE')
