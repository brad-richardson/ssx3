#!/usr/bin/env python3
"""VR4: attribute every instruction of an Odin block function to source (via
llvm-symbolizer --inlining JSON) and weight it by CP1 R2b MTVU samples.
Usage: attribute.py iphist.txt <block>.s <block>.sym.json"""
import json, re, sys, collections
hist_path, dis_path, sym_path = sys.argv[1:4]
samples = collections.Counter()
for line in open(hist_path):
    p = line.split(); samples[int(p[-2], 16)] += int(p[-1])
ops = {}
for line in open(dis_path):
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', line)
    if m: ops[int(m.group(1), 16)] = (m.group(2), m.group(3))
# issuePair source-line ranges (ps2_vu1_step_impl.h at fork 5d5c382)
def issue_region(line):
    for lo, hi, name in [(229, 269, 'stall/scoreboard'), (270, 299, 'direct-map setup'),
                         (300, 340, 'old VF/ACC/VI snapshot'), (341, 372, 'exec dispatch'),
                         (373, 391, 'post-exec clears'), (392, 450, 'revert+commit writes'),
                         (451, 454, 'markPairWrites'), (455, 460, 'vf0/vi0 constants'),
                         (461, 510, 'pc/branch/halt'), (511, 511, 'advanceOneCycle'),
                         (512, 527, 'counters/return')]:
        if lo <= line <= hi: return name
    return f'issuePair:{line}'
region = collections.Counter(); rstat = collections.Counter()
inner = collections.Counter(); istat = collections.Counter()
memr = collections.Counter(); mstat = collections.Counter()
tot = 0
for rec in map(json.loads, open(sym_path)):
    a = int(rec['Address'], 16); w = samples[a]; tot += w
    chain = rec['Symbol']
    names = [f['FunctionName'] for f in chain]
    # outermost frame is the block; find the frame that issuePair called
    reg = 'block glue'
    for i, n in enumerate(names):
        if n.startswith('issuePair'):
            if i == 0: reg = issue_region(chain[0]['Line'])
            else:
                child = names[i - 1]
                reg = issue_region(chain[i]['Line']) + ' > ' + child
            break
    region[reg] += w; rstat[reg] += 1
    inn = names[0] if names else '?'
    inner[inn] += w; istat[inn] += 1
    op, args = ops.get(a, ('?', ''))
    if op.startswith(('ld', 'st')):
        kind = 'load' if op.startswith('ld') else 'store'
        memr[(kind, reg.split(' > ')[0])] += w; mstat[(kind, reg.split(' > ')[0])] += 1
print(f'{dis_path}: {len(ops)} insns, {tot/1e6:.1f} ms samples')
def show(title, c, s, n=30):
    print(f'-- {title} (samples %, static insns)')
    for k, v in c.most_common(n):
        print(f'  {100*v/tot:5.1f}%  {s[k]:5d}  {k}')
show('issuePair region > called helper', region, rstat)
show('innermost function', inner, istat, 25)
show('loads/stores by region', memr, mstat, 20)
# second level: under execUpperImpl / execLowerImpl, by the path of helpers
sub = collections.Counter(); sstat = collections.Counter()
for rec in map(json.loads, open(sym_path)):
    a = int(rec['Address'], 16); w = samples[a]
    names = [f['FunctionName'] for f in rec['Symbol']]
    for top in ('execUpperImpl', 'execLowerImpl'):
        if top in names:
            i = names.index(top)
            path = [n for n in names[:i] if n not in ('operator()', 'memcpy')][::-1][:2]
            key = top + ' > ' + (' > '.join(path) if path else '(own)')
            sub[key] += w; sstat[key] += 1
            break
show('inside exec*Impl (first two helper levels)', sub, sstat, 30)
