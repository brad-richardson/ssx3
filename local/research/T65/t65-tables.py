#!/usr/bin/env python3
"""T65 report tables: camera/viewport blocks (hex+dec), column metrics, VF at entry, box summary."""
import importlib.util, math, re, sys, collections
spec = importlib.util.spec_from_file_location('a', sys.path[0] + '/t65-analyze.py'); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
R = a.read_dump('out/t65-vu1-2.bin'); S = a.read_dump('out/t65-vu1-1.bin')
def rec(recs, seq): return next(x for x in recs if x['seq'] == seq)
def block(r, lo, hi, title):
    q = a.qwords(r['mem'])
    print(f"**{title}** (seq {r['seq']}, ee_vsync {r['ee']}, tpc 0x{r['tpc']:x}, mfnv {r['mfnv']:08x})\n")
    print("| qw | x | y | z | w |\n|---|---|---|---|---|")
    for i in range(lo, hi): print(f"| 0x{i:03x} | " + " | ".join(a.fmt(w) for w in q[i]) + " |")
    print()
def colmetrics(r, label):
    q = a.qwords(r['mem']); m = [[a.f32(w) for w in q[i]] for i in range(3)]
    col = lambda c: [m[i][c] for i in range(3)]
    n = lambda v: math.sqrt(sum(x*x for x in v)); d = lambda u, v: sum(x*y for x, y in zip(u, v))
    X, Y, Z, W = col(0), col(1), col(2), col(3)
    flags = sorted({a.fclass(w) for i in range(4) for w in q[i]} - {''})
    print(f"| {label} | {n(X):.6f} | {n(Y):.6f} | {n(Z):.6f} | {n(W):.6f} | {d(X,Y):.2e} | {d(X,W):.2e} | {d(Y,W):.2e} | {n(Y)/n(X) if n(X) else float('nan'):.4f} | {','.join(flags) or 'none'} |")
def vf(r, title):
    print(f"**{title}**: VF at entry (seq {r['seq']}, tpc 0x{r['tpc']:x})\n")
    print("| VF | x | y | z | w |\n|---|---|---|---|---|")
    for i in range(32): print(f"| vf{i:02d} | " + " | ".join(a.fmt(w) for w in r['vf'][i]) + " |")
    print("| ACC | " + " | ".join(a.fmt(w) for w in r['acc']) + " |")
    print("\nVI: " + " ".join(f"vi{i:02d}={r['vi'][i] & 0xffff:04x}" for i in range(16)) + "\n")
which = sys.argv[1]
if which == 'blocks':
    block(rec(R, 684), 0, 6, "RACE, first program of the vsync (0x44e): camera variant A")
    block(rec(R, 771), 0, 6, "RACE, first 0xd7 of the same vsync: camera variant B")
    block(rec(R, 698), 0, 6, "RACE, 0x10 (405df496): a 2D matrix (z column 0; qw4 = 64,64; qw5 = 2048)")
    block(rec(S, 611), 0, 6, "SC control, first program (0x257, 2D)")
    first3d = next(x for x in S if x['ee'] == 12236 and x['tpc'] == 0x22a)
    block(first3d, 0, 6, "SC control, first 3D program (0x22a)")
    block(rec(R, 684), 0xd, 0x13, "RACE seq 684: the other affine block (qw 0x00f-0x012, diag 200)")
elif which == 'cols':
    print("| block | abs col x | abs col y | abs col z | abs col w | x.y | x.w | y.w | y/x scale | NaN/Inf/den |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for ev in (26718, 26719, 26720):
        f = next(x for x in R if x['ee'] == ev)
        colmetrics(f, f"race ee {ev} seq {f['seq']} (A)")
        b = next(x for x in R if x['ee'] == ev and x['tpc'] == 0xd7)
        colmetrics(b, f"race ee {ev} seq {b['seq']} (B)")
    colmetrics(next(x for x in S if x['ee'] == 12236 and x['tpc'] == 0x22a), "SC ee 12236 first 0x22a")
elif which == 'vf':
    vf(rec(R, 684), "RACE seq 684 (0x44e)")
    vf(next(x for x in S if x['ee'] == 12236 and x['tpc'] == 0x22a), "SC first 3D program (0x22a)")
elif which == 'boxsum':
    rows = []
    for line in open('out/t65a-box.txt', errors='replace'):
        m = re.search(r"T65_BOX vsync=(\d+) (.*)", line)
        if not m: continue
        kv = dict(t.split('=', 1) for t in m.group(2).split()); kv['v'] = int(m.group(1)); rows.append(kv)
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    rs = [r for r in rows if lo <= r['v'] <= hi and int(r['p1_verts']) > 0]
    rng = lambda k: (min(float(r[k].split('..')[0]) for r in rs), max(float(r[k].split('..')[1]) for r in rs))
    ints = lambda k: (min(int(r[k]) for r in rs), sorted(int(r[k]) for r in rs)[len(rs)//2], max(int(r[k]) for r in rs))
    print(f"vsyncs {lo}-{hi}: {len(rs)} with PATH1 verts")
    for k in ('prims_on', 'off', 'strad', 'zeroarea', 'adc', 'p1_verts', 'ctxchg'): print(f"  {k}: min/median/max {ints(k)}")
    for k in ('vx', 'vy', 'px', 'py'): print(f"  {k}: {rng(k)}")
    pxs = collections.Counter((r['px'], r['py']) for r in rs); print("  top prim boxes:", pxs.most_common(3))
    print("  of/sc:", collections.Counter((r['of'], r['sc']) for r in rs).most_common(3))
