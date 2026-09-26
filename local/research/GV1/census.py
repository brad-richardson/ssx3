#!/usr/bin/env python3
"""GV1 census: static structure of the 7 VU1 images, weighted by VR4's MTVU cpu-clock samples.

Inputs: ~/dev/ssx3-work/vu1gen-ssx3/vu1_<hash>.cpp (canonical images) and
~/dev/ssx3-work/VR4/asm/iphist-all.txt (CP1 R2b samples, Odin play build, 405 frames).
Program regions: code split after each E-bit pair's delay slot (the VU ends a program there).
Samples on a block function B<leader> are spread evenly over the block's pairs (approximation).
"""
import collections, glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from vu1dis import (load_image, upper_name, lower_name, upper_class, CLASS, BRANCHES,
                    branch_target, fmt_upper, fmt_lower)

GEN = os.path.expanduser("~/dev/ssx3-work/vu1gen-ssx3")
HIST = os.path.expanduser("~/dev/ssx3-work/VR4/asm/iphist-all.txt")
FRAMES = 405.0

imgs, blocks = {}, {}
for p in sorted(glob.glob(f"{GEN}/vu1_*.cpp")):
    h = int(os.path.basename(p)[4:20], 16)
    imgs[h] = load_image(p)
    cur, bl = None, {}
    for line in open(p):
        m = re.search(r"static bool B([0-9a-f]{4})\(", line)
        if m: cur = int(m.group(1), 16); bl[cur] = []; continue
        if cur is not None:
            m = re.search(r"issuePair<[^>]*>\(d([0-9a-f]{4})", line)
            if m: bl[cur].append(int(m.group(1), 16))
            if "return next(" in line: cur = None
    blocks[h] = bl

# ms/frame per (image, pc)
w = collections.defaultdict(float)
kindw = collections.Counter()
tot_mtvu = 0.0
sym_re = re.compile(r"VU1RecompImage<(\d+)ul>::([fBb])([0-9a-f]{4})\(")
for line in open(HIST):
    if line.startswith("#TOTAL MTVU"): tot_mtvu = float(line.split()[2]) / 1e9 / FRAMES * 1e3
    if not line.startswith("MTVU "): continue
    parts = line.split(None, 4)
    m = sym_re.search(parts[4])
    if not m: continue
    ns = float(parts[3]); h = int(m.group(1)); kind = m.group(2); pc = int(m.group(3), 16)
    ms = ns / 1e9 / FRAMES * 1e3
    kindw[kind] += ms
    if kind == "B" and pc in blocks.get(h, {}):
        pcs = blocks[h][pc]
        for q in pcs: w[(h, q)] += ms / len(pcs)
    else:
        w[(h, pc)] += ms

out = []
P = out.append
gen_total = sum(w.values())
P(f"MTVU total samples {tot_mtvu:.2f} ms/frame (incl. off-cpu); generated VU1 code {gen_total:.2f} ms/frame")
P(f"by kind: " + ", ".join(f"{k}={v:.2f}" for k, v in kindw.items()))
P("")

def regions(img):
    """Split 0..0x4000 into program regions ending at E-bit pc + 8 (delay slot)."""
    res, start = [], 0
    for pc in range(0, 0x4000, 8):
        l, u = img[pc]
        if (u >> 30) & 1:
            res.append((start, pc + 16)); start = pc + 16
    res.append((start, 0x4000))
    return res

def is_nop_pair(l, u):
    return upper_name(u) == "NOP" and l == 0x8000033C and not (u >> 31 & 1)

P("== Per image")
P("| image | code pairs (non-NOP) | E-bit ends | ms/frame (MTVU gen) | share |")
P("|---|---:|---:|---:|---:|")
img_ms = {}
for h, img in imgs.items():
    nn = sum(1 for pc in img if not is_nop_pair(*img[pc]))
    ne = sum(1 for pc in img if img[pc][1] >> 30 & 1)
    ms = sum(v for (hh, _), v in w.items() if hh == h)
    img_ms[h] = ms
    P(f"| {h:016x} | {nn} | {ne} | {ms:.2f} | {100*ms/gen_total:.1f}% |")
P("")

rows = []
for h, img in imgs.items():
    for (a, b) in regions(img):
        ms = sum(w.get((h, pc), 0.0) for pc in range(a, b, 8))
        if ms <= 0: continue
        st = collections.Counter(); dyn = collections.Counter()
        loops, kicks, branches = [], [], 0
        for pc in range(a, b, 8):
            l, u = img[pc]
            um = upper_name(u); uc = upper_class(um)
            if uc != "nop": st["U:" + uc] += 1; dyn["U:" + uc] += w.get((h, pc), 0)
            if not (u >> 31 & 1):
                lm = lower_name(l)
                if not (lm == "MOVE" and l == 0x8000033C):
                    c = CLASS.get(lm, "other")
                    st["L:" + c] += 1; dyn["L:" + c] += w.get((h, pc), 0)
                    st["op:" + lm] += 1
                if lm in BRANCHES:
                    branches += 1
                    if lm not in ("JR", "JALR"):
                        t = branch_target(pc, l)
                        if t <= pc: loops.append((t, pc))
                if lm == "XGKICK": kicks.append(pc)
            else:
                st["L:loi"] += 1
            st["U:" + um] += 0  # keep
            st["up:" + um] += 1
        rows.append((ms, h, a, b, st, dyn, loops, kicks, branches))
rows.sort(reverse=True)

P("== Program regions by MTVU generated time (top 20)")
P("| image | region | pairs | ms/frame | share | cum | loops (target<-branch, pairs) | XGKICK pcs | branches | EFU ops | FDIV ops | flag ops | vi-mem | vf-mem | ialu |")
P("|---|---|---:|---:|---:|---:|---|---|---:|---|---|---:|---:|---:|---:|")
cum = 0
for ms, h, a, b, st, dyn, loops, kicks, br in rows[:20]:
    cum += ms
    efu = ",".join(sorted({k[3:] for k in st if k.startswith("op:") and CLASS.get(k[3:]) == "efu"}))
    fdv = ",".join(sorted({k[3:] for k in st if k.startswith("op:") and CLASS.get(k[3:]) == "fdiv"}))
    lp = " ".join(f"{t:04x}<-{s:04x}({(s - t)//8 + 2})" for t, s in loops)
    P(f"| {h:016x}"[:7] + f" | {a:04x}-{b-8:04x} | {(b-a)//8} | {ms:.2f} | {100*ms/gen_total:.1f}% | {100*cum/gen_total:.1f}% | {lp} | {' '.join(f'{k:04x}' for k in kicks)} | {br} | {efu or '-'} | {fdv or '-'} | {st['L:flag']} | {st['L:vi-mem']} | {st['L:vf-mem']} | {st['L:ialu']} |")
P("")

# Class mix, static and time-weighted, over all regions with samples
P("== Instruction class mix over sampled regions (static count / sampled ms per frame on pairs holding that class)")
S = collections.Counter(); D = collections.Counter()
for ms, h, a, b, st, dyn, *_ in rows:
    for k, v in st.items():
        if k.startswith(("U:", "L:")): S[k] += v
    for k, v in dyn.items(): D[k] += v
P("| class | static slots | sampled ms/frame (pairs containing it) |")
P("|---|---:|---:|")
for k in sorted(S, key=lambda k: -D[k]):
    if S[k]: P(f"| {k} | {S[k]} | {D[k]:.2f} |")
P("")
P("== Opcode inventory over sampled regions (static)")
OP = collections.Counter()
for ms, h, a, b, st, *_ in rows:
    for k, v in st.items():
        if k.startswith(("op:", "up:")): OP[k] += v
P(", ".join(f"{k}={v}" for k, v in OP.most_common()))
open(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout", "w").write("\n".join(out) + "\n")

# listings of the top 6 regions for the report's appendix
if len(sys.argv) > 2:
    with open(sys.argv[2], "w") as f:
        for ms, h, a, b, *_ in rows[:6]:
            f.write(f"\n== {h:016x} {a:04x}-{b-8:04x}  {ms:.2f} ms/frame\n")
            img = imgs[h]
            for pc in range(a, b, 8):
                l, u = img[pc]
                fl = ("I" if u >> 31 & 1 else "") + ("E" if u >> 30 & 1 else "") + ("M" if u >> 29 & 1 else "") + ("D" if u >> 28 & 1 else "") + ("T" if u >> 27 & 1 else "")
                f.write(f"{pc:04x} {fl:3} {w.get((h,pc),0):6.3f} {fmt_upper(u):30} | {fmt_lower(pc, l, u >> 31 & 1)}\n")
