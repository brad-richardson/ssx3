#!/usr/bin/env python3
"""GV1: MTVU generated-code time by innermost loop (backward branch t<-s, body t..s+8 incl. delay slot)."""
import sys, os, collections
sys.argv = [sys.argv[0], "/dev/null"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census as C
from vu1dis import lower_name, upper_name, upper_class, CLASS, BRANCHES, branch_target
rows = []
covered = 0.0
for h, img in C.imgs.items():
    loops = []
    for pc in range(0, 0x4000, 8):
        l, u = img[pc]
        if u >> 31 & 1: continue
        m = lower_name(l)
        if m in BRANCHES and m not in ("JR", "JALR", "B", "BAL"):
            t = branch_target(pc, l)
            if t <= pc and (pc - t) // 8 < 200: loops.append((t, pc + 8))
    inner = {}
    for pc in range(0, 0x4000, 8):
        best = None
        for (a, b) in loops:
            if a <= pc <= b and (best is None or b - a < best[1] - best[0]): best = (a, b)
        if best: inner.setdefault(best, []).append(pc)
    for (a, b), pcs in inner.items():
        ms = sum(C.w.get((h, pc), 0) for pc in pcs)
        if ms < 0.05: continue
        cnt = collections.Counter()
        for pc in range(a, b + 8, 8):
            l, u = img[pc]
            cnt["fmac"] += upper_class(upper_name(u)) == "fmac"
            if not (u >> 31 & 1):
                lm = lower_name(l); c = CLASS.get(lm, "")
                cnt[c] += 1
                if lm in ("DIV", "SQRT", "RSQRT"): cnt["div"] += 1
                if lm == "CLIP": cnt["clip"] += 1
            if upper_name(u) == "CLIP": cnt["CLIP"] += 1
            if upper_name(u).startswith("FTOI"): cnt["ftoi"] += 1
        rows.append((ms, h, a, b, (b - a) // 8 + 1, cnt))
        covered += ms
rows.sort(reverse=True)
tot = sum(C.w.values())
print(f"generated VU1 code {tot:.2f} ms/frame; inside innermost loops (>=0.05 ms) {covered:.2f} ({100*covered/tot:.0f}%)")
print("| image | loop | body pairs | ms/frame | share | FMAC upper | LQ/SQ | DIV | CLIP | FTOI | flag ops | branches |")
print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for ms, h, a, b, n, c in rows[:15]:
    print(f"| {h:016x}"[:7] + f" | {a:04x}-{b:04x} | {n} | {ms:.2f} | {100*ms/tot:.1f}% | {c['fmac']} | {c['vf-mem']} | {c['div']} | {c['CLIP']} | {c['ftoi']} | {c['flag']} | {c['branch']} |")
