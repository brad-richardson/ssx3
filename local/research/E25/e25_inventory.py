"""E25 mission 1 -- the loss, inventoried precisely, BEFORE any rebuild.

Read-only. Records, never asserts away. Three layers:
  (a) the three protected build trees, per path, present/missing;
  (b) E24's section-1 market map carried forward and RE-MEASURED today, so the
      report cites E25's own numbers next to E24's, not E24's alone;
  (c) the audits that must stay green: 9,457 generated names/hashes and the
      21 E18 input/behavior source hashes; plus the 1,725 protected hashes,
      which are EXPECTED missing and are recorded as such.
Also pins what survived (fixtures, instrument, retained e23a artifacts) and
proves the no-boot posture at open: no lease, no runner process.
"""
import subprocess
from collections import Counter
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
E23D = E.parent / 'E23'
E24D = E.parent / 'E24'
E18D = E.parent / 'E18'

# --- (a) protected build manifest, per path -------------------------------
manifest = json.loads((E23D / 'protected-build-before.json').read_text())
present, missing = [], []
by_tree = {}
for row in manifest:
    p = Path(row['path'])
    tree = '/'.join(p.parts[:3])
    slot = by_tree.setdefault(tree, dict(tree=tree, files=0, bytes=0,
                                         present=0, missing=0, missing_bytes=0,
                                         sha_equal=0, sha_differ=0))
    slot['files'] += 1
    slot['bytes'] += row['bytes']
    if p.exists():
        eq = sha(p) == row['sha256']
        present.append(dict(path=row['path'], sha_equal=eq,
                            bytes=p.stat().st_size, expected_bytes=row['bytes']))
        slot['present'] += 1
        slot['sha_equal' if eq else 'sha_differ'] += 1
    else:
        missing.append(row['path'])
        slot['missing'] += 1
        slot['missing_bytes'] += row['bytes']

trees = [dict(path=str(b), present=b.exists(), allocated=size(b)) for b in PROTECTED_BUILDS]

# --- E24's section-1 numbers, carried and re-measured ---------------------
e24_env = json.loads((E24D / 'env-audit.json').read_text())
carried = dict(
    e24_protected_files_manifest=e24_env['protected_files_manifest'],
    e24_protected_files_present=e24_env['protected_files_present'],
    e24_protected_files_missing=e24_env['protected_files_missing'],
    e24_protected_missing_bytes=e24_env['protected_missing_bytes'],
    e24_missing_by_tree=e24_env['protected_missing_by_tree'],
)
carried['e25_agrees_with_e24'] = (
    carried['e24_protected_files_missing'] == len(missing) and
    carried['e24_protected_missing_bytes'] == sum(v['missing_bytes'] for v in by_tree.values()))

# --- (b) key binaries + what survived -------------------------------------
final23 = json.loads((E23D / 'final-audit.json').read_text())
key = {}
for name in ('runner', 'suite', 'fixture', 'cadence_fixture'):
    row = final23[name]
    p = Path(row['path'])
    entry = dict(path=row['path'], expected_bytes=row['bytes'],
                 expected_sha=row['sha256'], present=p.exists())
    if p.exists():
        entry.update(actual_bytes=p.stat().st_size, actual_sha=sha(p))
        entry['sha_equal'] = entry['actual_sha'] == row['sha256']
    key[name] = entry

proven = json.loads((E.parent / 'E21/parser-build.json').read_text())['observer']
dylib = E24D / 'parser/e21-parser-observer.dylib'
instrument = dict(source=str(dylib), present=dylib.exists(),
                  expected_sha=proven['sha256'], expected_bytes=proven.get('bytes'))
if dylib.exists():
    instrument.update(actual_bytes=dylib.stat().st_size, actual_sha=sha(dylib))
    instrument['sha_equal'] = instrument['actual_sha'] == proven['sha256']

# --- (c) the audits that must stay green ----------------------------------
expected_gen = json.loads((E18D / 'before-generated.json').read_text())
actual_gen = [pin(p) for p in sorted((R / 'ps2xRuntime/src/runner').iterdir())
              if p.suffix in ('.cpp', '.h') and not p.name.startswith('._')]
gen_ok = (len(actual_gen) == 9457 and
          {p['path']: p['sha256'] for p in actual_gen} ==
          {p['path']: p['sha256'] for p in expected_gen})
save('generated-audit.json', dict(utc=utc(), count=len(actual_gen),
                                  expected=len(expected_gen), all_hashes_match=gen_ok))

end18 = json.loads((E18D / 'final-audit.json').read_text())
srcs = []
for item in end18['inputs_sources'] + end18['behavior_sources']:
    row = pin_or_missing(item['path'])
    row['expected_sha'] = item['sha256']
    row['sha_equal'] = row.get('sha256') == item['sha256']
    srcs.append(row)

# --- posture: no boot, no lease -------------------------------------------
def command(args):
    p = subprocess.run([str(x) for x in args], text=True, capture_output=True)
    return dict(argv=[str(x) for x in args], rc=p.returncode, stdout=p.stdout, stderr=p.stderr)

lease = Path('/tmp/ssx3-p-lane-lease')
pg = command(['pgrep', '-x', 'ps2EntryRunner'])

RUN = P / 'run'
retained = {n: pin_or_missing(RUN / n) for n in
            ('boot-e23a-1.log', 'syscalls-e23a-on.txt', 'park-e23a-1/park-snapshot.json',
             'e23a-join/e7-events.txt', 'e23a-parser/parser-events.txt',
             'e23a-parser/parser-input.bin')}
retained['E23 observed/parser-input.bin'] = pin_or_missing(E23D / 'observed/parser-input.bin')
retained['E24 observed/parser-input.bin'] = pin_or_missing(E24D / 'observed/parser-input.bin')

out = dict(
    utc=utc(),
    trigger=('host restart between E23 close 2026-09-22T00:23:30Z and E24 open '
             '2026-09-22T11:31:22Z; E25 opens 2026-09-22T12:03:15Z with the loss unchanged'),
    protected_build_trees=trees,
    protected_files_manifest=len(manifest),
    protected_files_present=len(present),
    protected_files_missing=len(missing),
    protected_missing_bytes=sum(v['missing_bytes'] for v in by_tree.values()),
    protected_by_tree=sorted(by_tree.values(), key=lambda r: r['tree']),
    e24_section1_carried=carried,
    key_binaries=key,
    instrument=instrument,
    generated_names=len(actual_gen), generated_expected=9457,
    generated_all_hashes_match=gen_ok,
    e18_sources=len(srcs), e18_sources_all_equal=all(s['sha_equal'] for s in srcs),
    e18_sources_detail=srcs,
    retained_title_artifacts=retained,
    lease_present=lease.exists(),
    runner_processes=pg,
    tmp_entries=sorted(p.name for p in Path('/tmp').iterdir()),
    resources=sample(),
)
save('inventory.json', out)
print(json.dumps({k: v for k, v in out.items() if k not in
                  ('e18_sources_detail', 'retained_title_artifacts', 'tmp_entries', 'resources')}, indent=2))
print('SURVIVED:', json.dumps({k: v.get('sha_equal') for k, v in key.items() if v['present']}))
print('LOST    :', json.dumps([k for k, v in key.items() if not v['present']]))
print('RETAINED:', json.dumps({k: v.get('present') for k, v in retained.items()}))
print('# E25 INVENTORY TAIL COMPLETE')
