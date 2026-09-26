#!/usr/bin/env python3
"""VR4: per-thread on-cpu ms/frame by source class over CP1 R2b (405 record
frames). Classes from each sample's inline chain (llvm-symbolizer JSON)."""
import json, re, sys, collections
hist, symf = sys.argv[1:3]
FRAMES = 405.0
sym = {}
for rec in map(json.loads, open(symf)):
    sym[int(rec['Address'], 16)] = [f['FunctionName'] for f in rec['Symbol']]
def klass(names, top):
    gen = 'VU1RecompImage' in top or 'VU0RecompImage' in top
    where = 'gen' if gen else 'ool'
    if any(n.startswith('execUpper') for n in names): return where + ':FMAC/upper core'
    if any(n.startswith('execLower') for n in names): return where + ':lower exec'
    if any(n.startswith('issuePair') for n in names): return where + ':issuePair state/scoreboard'
    if gen: return 'gen:block/pair glue'
    return 'ool:' + (names[-1] if names else top.split('(')[0])[:48]
cls = collections.defaultdict(collections.Counter); tot = collections.Counter()
for line in open(hist):
    if line.startswith('#TOTAL'): continue
    t, dso, a, v, name = line.rstrip('\n').split(' ', 4)
    v = int(v)
    if dso == 'libps2EntryRunner.so':
        k = klass(sym.get(int(a, 16), []), name)
    else:
        k = 'other dso: ' + dso
    cls[t][k] += v; tot[t] += v
for t in cls:
    print(f'== {t}: all samples {tot[t]/1e9/FRAMES*1e3:.2f} ms/frame (incl. off-cpu sleep PCs)')
    for k, v in cls[t].most_common(22):
        print(f'  {v/1e9/FRAMES*1e3:6.2f} ms/frame  {k}')
# generated code on MTVU: split by issuePair region (same ranges as attribute.py)
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from importlib import util
spec = util.spec_from_file_location('attr_regions', __file__.rsplit('/', 1)[0] + '/regions.py')
R = util.module_from_spec(spec); spec.loader.exec_module(R)
lines = {}
for rec in map(json.loads, open(symf)):
    lines[int(rec['Address'], 16)] = rec['Symbol']
reg = collections.Counter(); blk = collections.Counter()
for line in open(hist):
    if line.startswith('#TOTAL'): continue
    t, dso, a, v, name = line.rstrip('\n').split(' ', 4)
    if t != 'MTVU' or dso != 'libps2EntryRunner.so' or 'VU1RecompImage' not in name: continue
    ch = lines.get(int(a, 16), [])
    reg[R.region(ch)] += int(v)
    m = re.search(r'>::(\w)', name); fn = m.group(1) if m else '?'
    blk[{'B': 'block body B*', 'b': 'trampoline b*', 'f': 'pair fn f*', 'n': 'next()'}.get(fn, fn)] += int(v)
print('== MTVU generated code by function kind')
for k, v in blk.most_common(): print(f'  {v/1e9/FRAMES*1e3:6.2f} ms/frame  {k}')
print('== MTVU generated code by issuePair region')
for k, v in reg.most_common(26): print(f'  {v/1e9/FRAMES*1e3:6.2f} ms/frame  {k}')
