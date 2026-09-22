"""Mission 0.1 -- verify-or-restore the instrument, and SAY which path was taken.

The brief's order is (a) verify in place, else (b) full rebuild on E25's recipe,
else (c) two-binary restore from the share tier. This tool evaluates (a) and
refuses to guess: it either reports VERIFIED-IN-PLACE with two matching
re-shas, or reports what is wrong and leaves the restore decision to the lane.

Standing SSD rule (SanDisk link artifacts): lane-critical SSD bytes need 2+
matching reads SEPARATED IN TIME before entering a gate. This tool is run more
than once, at different points in the lane, and `e26_restore_gate.py` compares
the passes. Within a pass each file is also read twice back to back, so a
single-read artifact cannot enter even one pass.

The ISO is checked by SIZE only, exactly as E24's designed preflight checks it
-- hashing 3,005,415,424 B over a flaky USB link is not a gate this boot needs.

Usage: e26_restore.py <pass-number>
"""
import shutil, sys, time
from e26_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
n = int(sys.argv[1])

# The pins E24 declared lost and E25 reproduced BIT-IDENTICALLY.
PINS = {
    'runner': dict(path=B0/'ps2xRuntime/ps2EntryRunner', bytes=163529696,
                   sha256='e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22'),
    'suite': dict(path=B0/'ps2xTest/ps2x_tests', bytes=5695128,
                  sha256='2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0'),
    'ELF (cd)': dict(path=W/'P1/cd/SLUS_207.72', bytes=3890784,
                     sha256='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'),
    'ELF (P1)': dict(path=W/'P1/SLUS_207.72', bytes=3890784,
                     sha256='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'),
}
ISO = dict(path=W/'SSX 3 (USA).iso', bytes=3005415424)

# SSD link health FIRST: if the volume is gone, table and stop -- never
# improvise a path. (Standing rule from the brief.)
ssd_mounted = W.exists() and W.is_dir()
link = dict(mount=str(W), mounted=ssd_mounted)
if ssd_mounted:
    link['free'] = shutil.disk_usage(W).free
assert ssd_mounted, 'SSD MOUNT ABSENT -- table and stop; do not improvise paths'

rows = []
for label, want in PINS.items():
    p = Path(want['path'])
    row = dict(item=label, path=str(p), present=p.exists(), on_ssd=str(p).startswith(str(W)))
    if p.exists():
        st = p.stat()
        t0 = time.monotonic(); a = sha(p); ta = time.monotonic() - t0
        t1 = time.monotonic(); b = sha(p); tb = time.monotonic() - t1
        row.update(bytes=st.st_size, bytes_ok=st.st_size == want['bytes'],
                   sha_read_a=a, sha_read_b=b, reads_agree=a == b,
                   sha_ok=(a == want['sha256'] and b == want['sha256']),
                   expected_sha=want['sha256'],
                   read_a_s=round(ta, 3), read_b_s=round(tb, 3))
    rows.append(row)

iso_p = Path(ISO['path'])
iso_row = dict(item='ISO', path=str(iso_p), present=iso_p.exists(),
               check='size only, exactly as E24 designed preflight checks it')
if iso_p.exists():
    iso_row.update(bytes=iso_p.stat().st_size, bytes_ok=iso_p.stat().st_size == ISO['bytes'])
rows.append(iso_row)

# The fallback tiers, RECORDED as present-or-not -- not used, because (a) held.
snapshot = W/'P1/e25-snapshot'
fallbacks = dict(
    rebuild_recipe=dict(path=str(E.parent/'E18/configure-command.json'),
                        present=(E.parent/'E18/configure-command.json').exists(),
                        measured_cost_s=72.5+530.8, restores_pins=True),
    e25_snapshot=dict(path=str(snapshot), present=snapshot.exists(),
                      members=[q.name for q in sorted(snapshot.glob('*'))] if snapshot.exists() else []),
    share_tier=dict(path='/Volumes/share/ssx3/e25-restore/',
                    present=Path('/Volumes/share/ssx3/e25-restore/').exists()))

all_ok = (all(r.get('present') and r.get('bytes_ok') and r.get('sha_ok') and r.get('reads_agree')
              for r in rows if r['item'] in PINS)
          and iso_row.get('present') and iso_row.get('bytes_ok'))
path_taken = '(a) VERIFIED IN PLACE' if all_ok else 'NOT (a) -- restore required'

save(f'restore-pass-{n}.json', dict(utc=utc(), passno=n, ssd_link=link, rows=rows,
     fallbacks=fallbacks, path_taken=path_taken, all_ok=all_ok,
     note=('Two back-to-back reads per file inside this pass; the lane runs this tool more '
           'than once and e26_restore_gate.py compares ACROSS passes, which is the '
           'separated-in-time half of the standing SSD rule.')))
for r in rows:
    print(f"{'PASS' if (r.get('sha_ok') if r['item'] in PINS else r.get('bytes_ok')) else 'FAIL'}  "
          f"{r['item']:<12} {r.get('bytes')} B "
          f"{'reads_agree=' + str(r.get('reads_agree')) if r['item'] in PINS else '(size only)'}")
print('PATH:', path_taken)
print(f'# E26 RESTORE PASS {n} TAIL COMPLETE')
raise SystemExit(0 if all_ok else 3)
