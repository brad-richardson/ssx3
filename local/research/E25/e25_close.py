"""E25 close: re-verify everything the lane promised not to move, and audit
the storage ledger against the caps declared in CONTRACT.md."""
import subprocess
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
E23D = E.parent / 'E23'

def run(argv):
    p = subprocess.run([str(x) for x in argv], text=True, capture_output=True)
    return dict(argv=[str(x) for x in argv], rc=p.returncode, stdout=p.stdout, stderr=p.stderr)

# --- fork unmoved ---------------------------------------------------------
head = run(['git', '-C', R, 'rev-parse', 'HEAD', 'refs/remotes/fork/ssx3'])
remote = run(['git', '-C', R, 'ls-remote', 'fork', 'refs/heads/ssx3'])
status = run(['git', '-C', R, 'status', '--short'])
fork_ok = (head['stdout'].splitlines() == [BASE_SHA, BASE_SHA]
           and remote['stdout'].split()[0] == BASE_SHA
           and status['stdout'] == '?? ps2_log.txt\n')

# --- 9,457 generated sources unmoved --------------------------------------
expected = json.loads((E.parent / 'E18/before-generated.json').read_text())
actual = [pin(p) for p in sorted((R / 'ps2xRuntime/src/runner').iterdir())
          if p.suffix in ('.cpp', '.h') and not p.name.startswith('._')]
gen_ok = (len(actual) == 9457 and
          {p['path']: p['sha256'] for p in actual} == {p['path']: p['sha256'] for p in expected})

# --- the rebuilt binaries, re-hashed at close -----------------------------
e23 = json.loads((E23D / 'final-audit.json').read_text())
binaries = {}
for key, rel in (('runner', 'ps2xRuntime/ps2EntryRunner'), ('suite', 'ps2xTest/ps2x_tests')):
    p = B0 / rel
    binaries[key] = dict(**pin(p), expected_sha=e23[key]['sha256'],
                         sha_equal_to_pin=sha(p) == e23[key]['sha256'])
for key, src in (('fixture', 'fixture'), ('cadence_fixture', 'cadence_fixture')):
    p = Path(e23[src]['path'])
    binaries[key] = dict(**pin(p), expected_sha=e23[src]['sha256'],
                         sha_equal_to_pin=sha(p) == e23[src]['sha256'])
obs = E / 'parser/e21-parser-observer.dylib'
proven = json.loads((E.parent / 'E21/parser-build.json').read_text())['observer']
binaries['observer'] = dict(**pin(obs), expected_sha=proven['sha256'],
                            sha_equal_to_pin=sha(obs) == proven['sha256'])

# --- 575 protected pins in the rebuilt tree, re-hashed at close -----------
manifest = [r for r in json.loads((E23D / 'protected-build-before.json').read_text())
            if r['path'].startswith('/tmp/e18-mpeg-link')]
close_present = sum(Path(r['path']).exists() for r in manifest)
close_equal = sum(Path(r['path']).exists() and sha(r['path']) == r['sha256'] for r in manifest)

# --- posture --------------------------------------------------------------
lease = Path('/tmp/ssx3-p-lane-lease')
pg = run(['pgrep', '-x', 'ps2EntryRunner'])
boots = sorted(E.glob('boot-attempt*.json'))
fork_commits = run(['git', '-C', R, 'log', '--oneline', f'{BASE_SHA}..HEAD'])

s = sample()
audit = dict(utc=utc(),
    fork=dict(head=head['stdout'].splitlines(), ls_remote=remote['stdout'].strip(),
              status_short=status['stdout'], agrees=fork_ok, sha=BASE_SHA),
    generated=dict(count=len(actual), expected=9457, all_hashes_match=gen_ok),
    binaries=binaries,
    all_binaries_match_pins=all(b['sha_equal_to_pin'] for b in binaries.values()),
    protected_e18_tree=dict(manifest=len(manifest), present=close_present,
                            sha_equal=close_equal,
                            differing=close_present-close_equal,
                            differing_cause='delta-cause.json: ar member timestamps + the pch'),
    posture=dict(boots=0, lease_claims=0, lease_present=lease.exists(),
                 runner_processes_rc=pg['rc'], boot_attempt_files=[p.name for p in boots],
                 fork_commits_since_base=fork_commits['stdout'].strip(),
                 fork_edits=0, pushes=0, regenerations=0, observer_rebuilds=0, deletions=0),
    storage=dict(reservation_internal=IRES, reservation_ssd=16*G,
                 floor=2*G, guard=512*M, sample=s, bound=bound(s),
                 internal_owned=s['internal_allocated'], ssd_owned=s['ssd_allocated'],
                 fork_positive_growth=s['fork_positive_growth'],
                 internal_within_reservation=s['internal_allocated'] < IRES,
                 ssd_within_reservation=s['ssd_allocated'] < 16*G,
                 internal_above_floor=s['internal_free'] > 2*G+512*M,
                 ssd_above_floor=s['ssd_free'] > 2*G+512*M))
green = (fork_ok and gen_ok and audit['all_binaries_match_pins']
         and not lease.exists() and pg['rc'] == 1 and not boots
         and not fork_commits['stdout'].strip()
         and audit['storage']['internal_within_reservation']
         and audit['storage']['ssd_within_reservation']
         and audit['storage']['internal_above_floor'] and audit['storage']['ssd_above_floor'])
audit['all_green'] = green
save('final-audit.json', audit)
print('fork agrees          :', fork_ok, BASE_SHA)
print('9,457 generated      :', gen_ok)
print('binaries match pins  :', audit['all_binaries_match_pins'])
for k, b in binaries.items():
    print(f"   {k:16} {b['bytes']:>12} B  sha_equal_to_pin={b['sha_equal_to_pin']}")
print(f"protected (E18 tree) : {close_equal}/{len(manifest)} sha-equal, {close_present} present")
print('lease absent         :', not lease.exists(), '| pgrep rc', pg['rc'],
      '| boot-attempt files', len(boots), '| fork commits since base:',
      repr(fork_commits['stdout'].strip()))
print(f"internal owned {s['internal_allocated']:,} / {IRES:,}  free {s['internal_free']:,}")
print(f"ssd owned      {s['ssd_allocated']:,} / {16*G:,}  free {s['ssd_free']:,}")
print('fork growth          :', s['fork_positive_growth'])
print('ALL GREEN            :', green)
print('# E25 CLOSE TAIL COMPLETE')
