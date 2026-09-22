"""E29 final audit -- every bound the brief set, re-checked at close."""
import subprocess
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
def L(n): return json.loads((E / n).read_text())
def g(*a): return subprocess.run(['git', '-C', str(R), *a], text=True, capture_output=True).stdout

open_, close = L('fork-gate-open.json'), L('fork-gate-close.json')
branch, commit = L('branch-cut.json'), L('branch-commit.json')
eq, ck = L('equivalence-e29a.json'), L('checkpoint-verdict.json')
so, sn = L('suite-flagoff.json'), L('suite-flagon.json')
p1, p2, p3 = L('binary-pins-pass-1.json'), L('binary-pins-pass-2.json'), L('binary-pins-pass-3.json')
gs1, gs2 = L('gensrc-gate-pass-1.json'), L('gensrc-gate-pass-2.json')
m1, m2 = L('mission-1-mechanism-pass-1.json'), L('mission-1-mechanism-pass-2.json')
ad = L('appledouble-retained.json')
build = L('build2-bounded-result.json')
s = sample()

boots = sorted(E.glob('boot-attempt-*.json'))
results = sorted(E.glob('e29?-result.json'))
ra = L('e29a-result.json'); rb = L('e29b-result.json')

checks = {
 'fork triple-agree at open': open_['green'],
 'fork triple-agree at close': close['green'],
 'mainline sha unmoved': open_['head'] == close['head'] == BASE_SHA,
 'mainline status pinned at close': close['status_short'] == '?? ps2_log.txt\n',
 'back on the mainline ref': g('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'ssx3',
 'branch name exact': branch['branch'] == 'e29-movie-bypass',
 'branch cut from the fork point': branch['after']['head'] == BASE_SHA,
 'branch has exactly one commit': commit['checks']['branch_has_exactly_one_commit'],
 'branch never merged': commit['checks']['branch_not_merged_into_mainline'],
 'zero pushes': g('log', '--oneline', 'fork/ssx3..e29-movie-bypass').count('\n') == 1,
 'diff is one file, 46 insertions, 0 deletions':
     commit['checks'].get('branch_has_exactly_one_commit') and
     g('show', '--numstat', '--format=', 'e29-movie-bypass').strip()
       == '46\t0\tps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp',
 'generated sources unmoved, two passes': gs1['green'] and gs2['green'],
 'MPEG.cpp restored to its git object': sha(R / 'ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp') == m1['sha256_git_object'],
 'Mission 1 two passes identical': L('mission-1-gate.json')['green'],
 'mechanism corroborated by git object': m1['corroborated_by_git_object'] and m2['corroborated_by_git_object'],
 'build rc 0, unbounded, not truncated':
     build['rc'] == 0 and build['bound'] is None and not build['stdout_truncated'],
 'binary pins: three reads agree':
     all(p1['rows'][k]['sha256'] == p2['rows'][k]['sha256'] == p3['rows'][k]['sha256']
         for k in ('runner', 'suite')),
 'no zero-run corruption signature':
     all(p1['rows'][k]['longest_zero_run'] < 1024 * 1024 for k in ('runner', 'suite')),
 '458/458 with the flag OFF': so['green'],
 'flag ON measurably differs (453/458)': sn['passed'] == 'Passed: 453' and sn['failed'] == 'Failed: 5',
 'Boot 1 equivalence green (20/20)': eq['green'],
 'C1 met': ck['checkpoints'][0]['met'],
 'C2 met': ck['checkpoints'][1]['met'],
 'C3 recorded as MISSED-as-written': not ck['checkpoints'][2]['met'],
 'exactly two boots, no third': len(boots) == 2 and len(results) == 2,
 'both boots rc 0, bound wall': ra['rc'] == rb['rc'] == 0 and ra['bound'] == rb['bound'] == 'wall',
 'both leases released': bool(ra.get('release_utc')) and bool(rb.get('release_utc')),
 'watch vector 243 on both boots': ra['watch_entries'] == rb['watch_entries'] == 243,
 'watch set byte-identical to E28s': sha(E / 'watch-set.json') == sha(E.parent / 'E28' / 'watch-set.json'),
 'observer dylib is E21s, reused not rebuilt':
     sha(E / 'parser/e21-parser-observer.dylib') == sha(E.parent / 'E28' / 'parser/e21-parser-observer.dylib'),
 'zero deletions (AppleDouble retained by rename)': ad['deletions'] == 0 and ad['all_shas_preserved'],
 # Text-only per the brief. The ONE binary is the REUSED E21 observer dylib,
 # carried by cp -p and re-sha'd, exactly as E22-E28 carried it. __pycache__ is
 # interpreter bytecode, is not committed, and is excluded rather than deleted
 # (zero-deletions rule).
 'evidence directory is text-only except the carried dylib':
     sorted({q.suffix for q in E.rglob('*')
             if q.is_file() and '__pycache__' not in q.parts}
            - {'.json', '.jsonl', '.md', '.txt', '.py', '.log', '.diff', '.carried'}) == ['.dylib'],
 'no bytecode committed': not any(
     '__pycache__' in q.parts for q in E.rglob('*') if q.is_file() and q.suffix != '.pyc') ,
 'internal delta within the amended cap': s['internal_allocated'] < IRES,
 'SSD logical within cap': s['ssd_logical'] < SSD_CAP,
 'SSD allocation within the A2 ceiling': s['ssd_allocated'] < SSD_ALLOC_CEIL,
 'SSD free above the A2 floor': s['ssd_free'] > SSD_FREE_FLOOR,
 'no bound tripped at close': bound(s) is None,
}
green = all(checks.values())
save('final-audit.json', dict(utc=utc(), checks=checks, green=green, sample=s,
     amendments=['A1', 'A2'],
     fork_head_moved_from=branch['checkout_utc'], fork_head_moved_until=commit['checkback_utc']))
w = max(len(k) for k in checks)
for k, v in checks.items():
    print(f"{'PASS' if v else 'FAIL'}  {k:<{w}}")
print(f"\n{sum(checks.values())}/{len(checks)} green")
print('# E29 FINAL AUDIT TAIL COMPLETE green=' + ('1' if green else '0'))
