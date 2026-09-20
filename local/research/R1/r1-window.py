#!/usr/bin/env python3
# R1 window analysis: EE events, ExecPS2 anchors, events 1-10 post-ExecPS2:2,
# (74)/(5b)/(5a)/(64) counts over 30 s post-ExecPS2:2 + full run. Small stdout.
import re, sys, hashlib
path = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else path
TS = re.compile(r"^\[\s*(\d+\.\d+)\]")
EE = re.compile(r"Bios call: (\S+) \(([0-9a-fA-F]+)\)(?: pc=([0-9a-fA-F]+) a0=([0-9a-fA-F]+))?")
h = hashlib.sha256()
nlines = 0
evs = []  # (fileline, ts, name, hex, pc, a0)
with open(path, "rb") as f:
    for raw in f:
        h.update(raw)
        nlines += 1
        try:
            line = raw.decode("utf-8", "replace")
        except Exception:
            continue
        m = EE.search(line)
        if not m:
            continue
        t = TS.match(line)
        ts = float(t.group(1)) if t else -1.0
        evs.append((nlines, ts, m.group(1), m.group(2).lower(), m.group(3), m.group(4)))
print(f"[{tag}] file_lines={nlines} sha256={h.hexdigest()}")
print(f"[{tag}] ee_events={len(evs)} with_pc={sum(1 for e in evs if e[4])} with_ts={sum(1 for e in evs if e[1] >= 0)}")
print(f"[{tag}] last_ts={evs[-1][1] if evs else -1}")
ex = [(i, e) for i, e in enumerate(evs) if e[2] == "ExecPS2"]
print(f"[{tag}] execps2_n={len(ex)} " + " ".join(f"ev{i}@file{e[0]} ts={e[1]}" for i, e in ex[:4]))
if len(ex) >= 2:
    s = ex[1][0] + 1
    t0 = ex[1][1][1]
    print(f"[{tag}] post2_start_ev={s} t0={t0}")
    for k in range(10):
        e = evs[s + k]
        print(f"[{tag}] ev{k+1} file={e[0]} ts={e[1]} {e[2]} ({e[3]}) pc={e[4]} a0={e[5]}")
    win = [e for e in evs[s:] if t0 < e[1] <= t0 + 30.0]
    post = evs[s:]
    for name, coll in (("win30", win), ("fullpost", post)):
        c = {}
        for e in coll:
            c[e[3]] = c.get(e[3], 0) + 1
        get = lambda x: c.get(x, 0)
        print(f"[{tag}] {name}_n={len(coll)} 74={get('74')} 5b={get('5b')} 5a={get('5a')} 64={get('64')} 2f={get('2f')} 7={get('7')}")
    cov = max((e[1] for e in evs[s:]), default=-1)
    print(f"[{tag}] post2_last_ts={cov} covers_30s={cov >= t0 + 30.0}")
vb = sum(1 for e in evs if e[2] == "WaitVblankStart")
print(f"[{tag}] vblanks={vb}")
