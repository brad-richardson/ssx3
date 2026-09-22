"""E29 close: refit E24's cost model with its third point, then the final audit."""
import subprocess
from e29_common import *

RUN = P / 'run'
result = json.loads((E / 'e29a-result.json').read_text())
WS = json.loads((E / 'watch-set.json').read_text())
rst = json.loads((E / 'restore-pass-2.json').read_text())

# ------------------------------------------------- the refit E24 asked for
# BOOT-DESIGN.md: "the driver records the actual span-complete time so the next
# lane can refit" -- E24 CHANGE 4 exists for exactly this. Not a new question.
# E29 CHANGE 4: take the calibration points from E26's COMMITTED refit receipt,
# which already carries E24's two plus E26's own measured third, instead of from
# the two-point list frozen inside watch-set.json before either big boot existed.
PRIOR = json.loads((E.parent / 'E26/cost-model-refit.json').read_text())['points']
pts = [dict(boot=c['boot'], watches=c['watches'], span_complete_s=c['span_complete_s'])
       for c in PRIOR]
pts.append(dict(boot='e29a', watches=result['watch_entries'],
                span_complete_s=round(result['span_complete_s'], 3)))
n = len(pts)
sx = sum(p['watches'] for p in pts); sy = sum(p['span_complete_s'] for p in pts)
sxx = sum(p['watches']**2 for p in pts); sxy = sum(p['watches']*p['span_complete_s'] for p in pts)
k = (n*sxy - sx*sy) / (n*sxx - sx*sx); base = (sy - k*sx) / n
k23 = (pts[2]['span_complete_s'] - pts[1]['span_complete_s']) / (pts[2]['watches'] - pts[1]['watches'])
save('cost-model-refit.json', dict(utc=utc(),
     old=dict(k_seconds_per_entry=WS['cost_model']['k_seconds_per_entry'],
              base_seconds=WS['cost_model']['base_seconds'],
              predicted_span_complete_s=WS['cost_model']['predicted_span_complete_s'],
              predicted_post_park_window_s=WS['cost_model']['predicted_post_park_window_s'],
              fit_on='two points, e22a and e23a'),
     points=pts,
     measured=dict(watches=result['watch_entries'], span_complete_s=round(result['span_complete_s'], 3),
                   predicted=WS['cost_model']['predicted_span_complete_s'],
                   over_prediction_s=round(WS['cost_model']['predicted_span_complete_s']
                                           - result['span_complete_s'], 2),
                   over_prediction_factor=round(WS['cost_model']['predicted_span_complete_s']
                                                / result['span_complete_s'], 2)),
     refit_three_point=dict(k_seconds_per_entry=round(k, 5), base_seconds=round(base, 3)),
     slope_e23a_to_e29a=round(k23, 5),
     finding=('The two-point fit over-predicted by a factor of 2.6. Adding 193 watch entries cost '
              '1.22 s of span-complete, a slope of 0.0063 s/entry -- 14x shallower than the '
              '0.0863 s/entry the e22a->e23a pair implied. That pair differed by only 8 entries, '
              'so its slope was dominated by run-to-run variation, not by watch count.'),
     consequence=('The residual E24 declared -- an isolated write shorter than 121 B inside the '
                  'sampled body span -- was paid for a scan cost that is not there. On this '
                  'measurement a FULL 630-entry 8-byte cover of the body would have cost about '
                  f'{round(base + k*630, 1)} s of span-complete, not the ~64 s the old model '
                  'predicted, and would have left roughly 65 s of post-park window. A later lane '
                  'that wants the residual closed can afford it. E29 does not re-spend a boot to '
                  'prove that; it tables the number.'),
     caveat='three points, still a small fit; the driver keeps recording span-complete on every path'))

# ------------------------------------------------------------ final audit
def git(*a):
    p = subprocess.run(['git', '-C', str(R), *a], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

rc_h, head, _ = git('rev-parse', 'HEAD', 'refs/remotes/fork/ssx3')
rc_r, remote, _ = git('ls-remote', 'fork', 'refs/heads/ssx3')
rc_s, status, status_err = git('status', '--short')
lease = Path('/tmp/ssx3-p-lane-lease')
pg = subprocess.run(['pgrep', '-x', 'ps2EntryRunner'], capture_output=True, text=True)

lines = head.splitlines()
fork_ok = (lines[:2] == [BASE_SHA, BASE_SHA]
           and remote.split() and remote.split()[0] == BASE_SHA
           and status == '?? ps2_log.txt\n')

bins = {name: sha(p) for name, p in
        [('runner', B0/'ps2xRuntime/ps2EntryRunner'), ('suite', B0/'ps2xTest/ps2x_tests')]}
pins = {r['item']: r['expected_sha'] for r in rst['rows'] if 'expected_sha' in r}
bins_ok = bins['runner'] == pins['runner'] and bins['suite'] == pins['suite']

boot_dirs = sorted(str(q) for q in RUN.glob('*e29a*'))
s = sample()
checks = dict(fork_triple_agree=fork_ok, binaries_unmoved=bins_ok,
              lease_absent=not lease.exists(), no_runner_process=pg.returncode == 1,
              boots_spent_is_one=len(list(E.glob('e29?-result.json'))) == 1,
              boot_attempt_written_once=(E/'boot-attempt.json').exists(),
              lease_released_cleanly=bool(result.get('release_utc'))
                                     and not result.get('lease_ownership_error'),
              no_sigkill=not result.get('needed_sigkill'),
              fork_growth_zero=s['fork_positive_growth'] == 0,
              within_internal_reservation=s['internal_allocated'] < IRES,
              within_ssd_reservation=s['ssd_allocated'] < 16*G,
              floors_clear=s['internal_free'] > 2*G+512*M and s['ssd_free'] > 2*G+512*M,
              no_bound_tripped=bound(s) is None,
              ssd_still_mounted=W.exists())
green = all(checks.values())

save('final-audit.json', dict(utc=utc(), green=green, checks=checks,
     fork=dict(head=lines[0] if lines else None, ref=lines[1] if len(lines) > 1 else None,
               ls_remote=remote.split()[0] if remote.split() else None,
               status_short=status, status_stderr_preexisting=status_err),
     binaries=bins, pins=pins,
     boot=dict(label=result['label'], claim_utc=result['claim_utc'], boot_utc=result['boot_utc'],
               pid=result['pid'], bound=result['bound'], rc=result['rc'],
               elapsed_s=round(result['elapsed_s'], 3),
               span_complete_s=round(result['span_complete_s'], 3),
               watch_entries=result['watch_entries'],
               signal_utc=result['signal_utc'], process_end_utc=result['process_end_utc'],
               release_utc=result['release_utc'],
               release_latency_ms=round((datetime.datetime.fromisoformat(result['release_utc'])
                                         - datetime.datetime.fromisoformat(result['process_end_utc'])
                                        ).total_seconds()*1000, 3),
               needed_sigkill=bool(result.get('needed_sigkill'))),
     probes=dict(title_boots_spent=1, title_boots_allowed=1,
                 lease_claims=1, lease_releases=1),
     mutations=dict(fork_source_edits=0, fork_commits=0, pushes=0, regenerations=0,
                    builds=0, configures=0, relinks=0, observer_rebuilds=0,
                    deletions=0, reclaims=0),
     artifacts=boot_dirs, resources=s, bound=bound(s),
     reservations=dict(internal=IRES, ssd=16*G, floor=2*G, guard=512*M)))

for k_, v in checks.items():
    print(f"{'PASS' if v else 'FAIL'}  {k_}")
print('ALL GREEN:', green)
print('# E29 CLOSE TAIL COMPLETE')
raise SystemExit(0 if green else 3)
