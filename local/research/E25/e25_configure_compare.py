"""Compare E25's configure against E18's, line by line, with only the
mechanically-varying parts normalised: git transfer progress, elapsed seconds
and ninja edge counters. Everything else must match or it is reported."""
import difflib, re
from e25_common import *

NOISE = re.compile(r'^(remote:|Receiving objects:|Resolving deltas:|Updating files:|'
                   r'Counting objects:|Compressing objects:|Cloning into )')
def norm(text):
    out = []
    for line in text.splitlines():
        if NOISE.search(line.strip()): continue
        line = re.sub(r'\(\d+(\.\d+)?s\)', '(Ns)', line)
        line = re.sub(r'^\[\d+/\d+\]', '[N/M]', line)
        out.append(line.rstrip())
    return out

a = norm((E.parent / 'E18/configure.log').read_text())
b = norm((E / 'configure.log').read_text())
diff = [l for l in difflib.unified_diff(a, b, 'E18', 'E25', lineterm='', n=1)]
only_e18 = [l[1:] for l in diff if l.startswith('-') and not l.startswith('---')]
only_e25 = [l[1:] for l in diff if l.startswith('+') and not l.startswith('+++')]

# The FetchContent dependency HEADs -- the one part of the configure that could
# silently move between runs. Recorded for both lanes.
HEAD = re.compile(r'^HEAD is now at (\S+) (.*)$')
TAG = re.compile(r'^-- Already at requested tag: (\S+)$')
def deps(text):
    heads, tags = [], []
    for line in text.splitlines():
        m = HEAD.match(line.strip())
        if m: heads.append(dict(sha=m.group(1), subject=m.group(2)))
        m = TAG.match(line.strip())
        if m: tags.append(m.group(1))
    return dict(heads=heads, tags=tags)
d18 = deps((E.parent / 'E18/configure.log').read_text())
d25 = deps((E / 'configure.log').read_text())

out = dict(utc=utc(),
           e18_substantive_lines=len(a), e25_substantive_lines=len(b),
           identical=a == b,
           only_in_e18=only_e18, only_in_e25=only_e25,
           dependency_heads=dict(e18=d18, e25=d25,
                                 heads_equal=d18['heads'] == d25['heads'],
                                 tags_equal=d18['tags'] == d25['tags']),
           normalisation='git transfer progress dropped; "(N.Ns)" and "[n/m]" masked')
save('configure-compare.json', out)
print('substantive lines  E18', len(a), ' E25', len(b), ' identical', a == b)
print('only in E18:'); [print('  -', l) for l in only_e18]
print('only in E25:'); [print('  +', l) for l in only_e25]
print('dep tags equal ', d18['tags'] == d25['tags'], d25['tags'])
print('dep heads equal', d18['heads'] == d25['heads'])
for x, y in zip(d18['heads'], d25['heads']):
    print(f"   E18 {x['sha']}  E25 {y['sha']}  {'SAME' if x==y else 'DIFFER'}  {x['subject'][:50]}")
print('# E25 CONFIGURE COMPARE TAIL COMPLETE')
