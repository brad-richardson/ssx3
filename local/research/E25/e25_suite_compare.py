"""Behaviour-compare the REBUILT suite against E23's retained suite text.

Same inputs must give same outputs. This diffs the whole suite transcript,
not just the totals: every `[Suite]` header, every `[Run]` name and its
verdict, every diagnostic line the tests print (including the E18 R1-R6
blocks), in order. ANSI colour is stripped; nothing else is normalised, so a
genuine behavioural difference cannot hide inside a mask.
"""
import difflib, re, sys
from e25_common import *

ANSI = re.compile(r'\x1b\[[0-9;]*m')
# The four `mc0` tests echo their own TMPDIR scratch path, which contains the
# LANE directory name and a monotonic-clock nonce. Masking exactly that span --
# and nothing else -- shows whether anything behavioural differs underneath.
SCRATCH = re.compile(r'/local/research/E\d+/\.suite-[A-Za-z0-9_-]+/ps2recomp-mc0-\d+/')
RUN = re.compile(r'^\s*\[Run\]:\s*(.*?)\s*(\[Passed\]|\[Failed\])?\s*$')

def load(path):
    return [ANSI.sub('', l).rstrip() for l in Path(path).read_text(errors='replace').splitlines()]

def names(lines):
    out = []
    for l in lines:
        m = RUN.match(l)
        if m: out.append(m.group(1))
    return out

def totals(lines):
    d = {}
    for l in lines:
        for key in ('Total Tests', 'Passed', 'Failed'):
            if l.startswith(key + ':'):
                d[key] = int(l.split(':')[1])
    return d

label = sys.argv[1] if len(sys.argv) > 1 else 'checkpoint'
old_path = E.parent / 'E23' / f'{label}-suite.txt'
new_path = E / f'{label}-suite.txt'
old, new = load(old_path), load(new_path)
mask = lambda L: [SCRATCH.sub('/<LANE-SCRATCH>/', l) for l in L]
mold, mnew = mask(old), mask(new)
masked_spans_old = sum(len(SCRATCH.findall(l)) for l in old)
masked_spans_new = sum(len(SCRATCH.findall(l)) for l in new)
mdiff = [l for l in difflib.unified_diff(mold, mnew, 'E23', 'E25', lineterm='', n=0)]
mremoved = [l[1:] for l in mdiff if l.startswith('-') and not l.startswith('---')]
madded = [l[1:] for l in mdiff if l.startswith('+') and not l.startswith('+++')]
diff = [l for l in difflib.unified_diff(old, new, 'E23', 'E25', lineterm='', n=0)]
removed = [l[1:] for l in diff if l.startswith('-') and not l.startswith('---')]
added = [l[1:] for l in diff if l.startswith('+') and not l.startswith('+++')]

on, nn = names(old), names(new)
ot, nt = totals(old), totals(new)

# The six E18 regression tests, compared by their own lines.
def r_block(lines):
    return [l for l in lines if re.search(r'MPEG non-stream R[1-6] ', l)]
ro, rn = r_block(old), r_block(new)

out = dict(utc=utc(), label=label,
           old=dict(path=str(old_path), lines=len(old), runs=len(on), totals=ot),
           new=dict(path=str(new_path), lines=len(new), runs=len(nn), totals=nt),
           transcript_identical=old == new,
           transcript_identical_scratch_masked=mold == mnew,
           masked_spans=dict(old=masked_spans_old, new=masked_spans_new),
           masked_diff_removed=mremoved, masked_diff_added=madded,
           masked_diff_line_count=len(mremoved) + len(madded),
           run_names_identical=on == nn,
           totals_identical=ot == nt,
           r1_r6_present_old=len(ro), r1_r6_present_new=len(rn),
           r1_r6_identical=ro == rn, r1_r6_lines=rn,
           names_only_in_old=sorted(set(on) - set(nn)),
           names_only_in_new=sorted(set(nn) - set(on)),
           diff_removed=removed, diff_added=added,
           diff_line_count=len(removed) + len(added))
save(f'suite-compare-{label}.json', out)
print(f'{label}: E23 {len(old)} lines / {len(on)} runs {ot}')
print(f'{label}: E25 {len(new)} lines / {len(nn)} runs {nt}')
print('transcript identical :', old == new)
print('  ... scratch-masked  :', mold == mnew,
      f'(masked spans {masked_spans_old} old / {masked_spans_new} new,'
      f' residual diff lines {len(mremoved)+len(madded)})')
print('run names identical  :', on == nn)
print('totals identical     :', ot == nt)
print('R1-R6 identical      :', ro == rn, f'({len(rn)}/6 present)')
if removed or added:
    print(f'--- differing lines ({len(removed)} removed / {len(added)} added) ---')
    for l in removed[:40]: print('  -', l)
    for l in added[:40]: print('  +', l)
print(f'# E25 SUITE COMPARE TAIL COMPLETE label={label}')
