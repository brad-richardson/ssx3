#!/usr/bin/env python3
# R1 game-entry mining: ExecPS2 list, post-LAST-ExecPS2 events 1-30,
# WaitVblankStart sample shape, recompiler/interpreter markers, sha.
import re, sys, hashlib
path = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else path
TS = re.compile(r"^\[\s*(\d+\.\d+)\]")
EE = re.compile(r"Bios call: (\S+) \(([0-9a-fA-F]+)\)(?: pc=([0-9a-fA-F]+) a0=([0-9a-fA-F]+))?")
h = hashlib.sha256()
nlines = 0
evs = []
vbsamp = []
markers = []
with open(path, "rb") as f:
    for raw in f:
        h.update(raw)
        nlines += 1
        try:
            line = raw.decode("utf-8", "replace")
        except Exception:
            continue
        m = EE.search(line)
        t = TS.match(line)
        ts = float(t.group(1)) if t else -1.0
        if m:
            evs.append((nlines, ts, m.group(1), m.group(2).lower(), m.group(3), m.group(4)))
        if "WaitVblankStart" in line and len(vbsamp) < 2:
            vbsamp.append((nlines, line.rstrip()[:160]))
        if ("ecompiler Reset" in line or "nterpreter" in line) and len(markers) < 8:
            markers.append((nlines, line.rstrip()[:130]))
print(f"[{tag}] file_lines={nlines} sha256={h.hexdigest()}")
ex = [(i, e) for i, e in enumerate(evs) if e[2] == "ExecPS2"]
for n, (i, e) in enumerate(ex):
    print(f"[{tag}] exec{n+1} evidx={i} file={e[0]} ts={e[1]} pc={e[4]} a0={e[5]}")
n, (i, e) = len(ex), ex[-1]
s = i + 1
print(f"[{tag}] last_t0={e[1]}")
for k in range(30):
    g = evs[s + k]
    print(f"[{tag}] g{k+1} file={g[0]} ts={g[1]} {g[2]} ({g[3]}) pc={g[4]} a0={g[5]}")
for fl, sl in vbsamp:
    print(f"[{tag}] vbsamp file={fl} :: {sl}")
for fl, ml in markers:
    print(f"[{tag}] marker file={fl} :: {ml}")
