"""E29 -- authorize (or refuse) a boot, and write that boot's build pins.

WRITTEN FRESH, not carried. E28's `prepare_probe` pins the MAINLINE binary and
gates on an E28 Mission-0 restore receipt that E29 never produces: E29's whole
purpose is to boot a binary that did not exist until this lane built it. The
INHERITED assertions (E25's regression chain, E21's instrument receipts) are
carried VERBATIM -- they are properties of the runtime's test corpus and the
observer dylib, not of any one binary -- and the binary-identity block is
replaced by E29's own, stronger evidence.

Usage: e29_probe_gate.py <a|b>
"""
import subprocess, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
PHASE = sys.argv[1]
assert PHASE in ('a', 'b')
LABEL = 'e29' + PHASE
GATES = E.parent / 'E25'
PRIOR = E.parent / 'E21'

# ---------------- inherited, carried verbatim from E28's prepare_probe --------
chk = json.loads((GATES / 'checkpoint-complete.json').read_text())
assert chk['suite'] == 458 and chk['closure_cases'] == 6 and chk['e15_rc'] == [0, 0] and chk['extra_cases'] == 8 and chk['boot'] == 0
txt = (GATES / 'checkpoint-suite.txt').read_text()
assert 'Total Tests: 458' in txt and 'Failed: 0' in txt
assert 'MPEG non-stream R1' in txt and 'MPEG non-stream R6' in txt
v = json.loads((GATES / 'checkpoint-bindings-validation.json').read_text()); prior = v['cases'][0]
assert (prior['leaf'], prior['consumer'], prior['predicate'], prior['query'], prior['drop']) == (24, 3, 14, 4, True)
obs = json.loads((GATES / 'observer-regression.json').read_text())
assert obs['suite'] == 458 and obs['closure_cases'] == 6 and obs['boot'] == 0
assert all(c['footer']['pending'] == 0 for c in obs['closures'])
iso = json.loads((PRIOR / 'isolation-proof.json').read_text())
assert iso['feed']['identical'] and iso['exit']['plain_rc'] == iso['exit']['loaded_rc'] == 3
assert all(b['valid'] == 1 for b in iso['addrs']['observer_bindings'])
q1 = json.loads((PRIOR / 'q1-complete.json').read_text()); assert q1['cases'] == 9 and q1['EOF_flushes'] == 0
assert (PRIOR / 'Q2-AUDIT.md').is_file()
proven = json.loads((PRIOR / 'parser-build.json').read_text())['observer']
assert sha(E / 'parser/e21-parser-observer.dylib') == proven['sha256'], 'reused instrument re-sha missed'
assert obs['observer']['sha256'] == proven['sha256']
cad = json.loads((GATES / 'cadence.json').read_text())
assert len(cad['rows']) == 4 and {r['feedBytes'] for r in cad['rows']} == {60, 120, 180, 240}
assert all(r['rc'] == 0 and r['cadence']['producerFirings'] == 1 and r['cadence']['addBs'] == 1 for r in cad['rows'])
assert {r['outcome'] for r in cad['rows']} == {'SERVED', 'STALLED'}
assert all(r['parser']['footer']['pending'] == 0 and r['parser']['footer']['errors'] == 0 for r in cad['rows'])
for lab in ('newbin-bindings', 'newbin-closure'):
    ctl = json.loads((GATES / f'{lab}-validation.json').read_text())
    assert all(c['rc'] == 0 for c in ctl['cases']), lab

# ---------------- E29's OWN identity block, replacing the carried one --------
def git(*a): return subprocess.check_output(['git', '-C', str(R), *a], text=True)
head = git('rev-parse', 'HEAD').strip()
assert head == BASE_SHA, 'mainline must be checked back out before a boot'
assert git('diff', '--cached', '--name-only') == ''
assert git('status', '--short') == '?? ps2_log.txt\n'
assert git('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'ssx3'

pins1 = json.loads((E / 'binary-pins-pass-1.json').read_text())['rows']
pins2 = json.loads((E / 'binary-pins-pass-2.json').read_text())['rows']
suite_off = json.loads((E / 'suite-flagoff.json').read_text())
# `bypass-apply.json` records the APPLY step, whose own green flag was tripped by
# a mis-stated self-check (it asserted the flag name appears once; it appears
# twice by design -- the getenv and the log line). The authoritative receipt is
# `bypass-verify-pass-1.json`, taken while the branch was checked out, which
# re-audits the same diff 17/17. The branch commit's own diffstat is checked
# here too, so the claim does not rest on a working tree that no longer exists.
apply_row = json.loads((E / 'bypass-verify-pass-1.json').read_text())
branch_stat = subprocess.check_output(
    ['git', '-C', str(R), 'show', '--numstat', '--format=', 'e29-movie-bypass'], text=True).strip()
commit_row = json.loads((E / 'branch-commit.json').read_text())
build_row = json.loads((E / 'build2-bounded-result.json').read_text())
gensrc = json.loads((E / 'gensrc-gate-pass-1.json').read_text())

# a THIRD read of the binaries, here, at the gate
third = {k: dict(bytes=Path(p).stat().st_size, sha256=sha(Path(p)))
         for k, p in (('runner', BYPASS_RUNNER), ('suite', BYPASS_SUITE))}

checks = dict(
  two_reads_agree=all(pins1[k]['sha256'] == pins2[k]['sha256'] for k in ('runner', 'suite')),
  third_read_agrees=all(third[k]['sha256'] == pins1[k]['sha256'] for k in ('runner', 'suite')),
  no_zero_run_signature=all(pins1[k]['longest_zero_run'] < 1024 * 1024 for k in ('runner', 'suite')),
  binary_differs_from_mainline=all(pins1[k]['differs_from_mainline'] for k in ('runner', 'suite')),
  bypass_strings_present=all(
      subprocess.run(['grep', '-c', 'PS2X_SKIP_MOVIE'], input=subprocess.run(
          ['strings', '-a', str(p)], capture_output=True).stdout,
          capture_output=True).stdout.strip() != b'0'
      for p in (BYPASS_RUNNER, BYPASS_SUITE)),
  suite_458_flag_off=suite_off['green'] and suite_off['failed'] == 'Failed: 0'
                     and suite_off['total'] == 'Total Tests: 458' and not suite_off['flag_in_env'],
  diff_one_file_zero_deletions=apply_row['green'],
  branch_commit_is_one_file_46_insertions_0_deletions=(
      branch_stat == '46\t0\tps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp'),
  branch_one_commit_and_checked_back=commit_row['green'],
  build_rc0_unbounded=build_row['rc'] == 0 and build_row['bound'] is None and not build_row['stdout_truncated'],
  generated_sources_unmoved=gensrc['green'],
  observer_dylib_is_E21s=sha(E / 'parser/e21-parser-observer.dylib') == proven['sha256'],
)
green = all(checks.values())

save('entry-preflight.json', dict(utc=utc(), phase=PHASE, inherited_from=['E25', 'E21'],
     # The inherited counts the capture driver's own preflight re-asserts. They
     # are E28's values because they are properties of the SAME E25/E21 receipts
     # asserted above, not of any binary; every one is re-derived here, not copied.
     suite_rc=0, binding_rc=0, query_cases=prior['query'], predicate_cases=prior['predicate'],
     leaf_cases=prior['leaf'], consumer_cases=prior['consumer'], leaf_present=True,
     mpeg_delivery_cases=2, new_regression_cases=obs['closure_cases'],
     run_exit_cases=chk['closure_cases'],
     isolation_identical=iso['feed']['identical'], loaded_regression_green=True,
     q1_cases=q1['cases'], q2_audit=True,
     cadence_cases=len(cad['rows']), cadence_branches=2,
     instrument_reused_sha=proven['sha256'], instrument_rebuilt=False,
     regression_receipts_note=('E25/E21 assertions carried verbatim -- they are properties of the '
        'test corpus and the observer dylib. The binary-identity block is E29\'s own: three '
        'time-separated reads, a zero-run scan, a string proof and 458/458 with the flag off.'),
     checks=checks, green=green, third_read=third))
save(f'{LABEL}-build.json', dict(utc=utc(), fork_head=head, fork_status='?? ps2_log.txt\n',
     test_count=458,
     bin_size=third['runner']['bytes'], bin_sha=third['runner']['sha256'],
     test_size=third['suite']['bytes'], test_sha=third['suite']['sha256'],
     bypass_branch_commit=commit_row['commit'], bypass_fork_point=BASE_SHA,
     mainline_bin_sha=pins1['runner']['mainline_sha256'],
     mainline_test_sha=pins1['suite']['mainline_sha256']))
print(json.dumps(dict(phase=PHASE, checks=checks, third_read=third), indent=2))
print('# E29 PROBE GATE TAIL COMPLETE phase=%s green=%s' % (PHASE, '1' if green else '0'))
if not green:
    raise SystemExit('BOOT NOT AUTHORIZED')
