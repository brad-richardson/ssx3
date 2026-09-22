#!/usr/bin/env python3
# G39: regression/no-perturbation scorer (R1/R2 vs B0=G38-O1, B1=G31).
import re, sys

SSD = "/Volumes/Extreme SSD"
B0 = f"{SSD}/ps2x-g38/g38-odin-logcat.txt"
B1 = f"{SSD}/ps2x-g31/g31-logcat.txt"
R1 = f"{SSD}/ps2x-g39/g39-r1-logcat.txt"
R2 = f"{SSD}/ps2x-g39/g39-r2-logcat.txt"

def strip(lines):
    out = []
    for ln in lines:
        ln = re.sub(r"^\d\d-\d\d \d\d:\d\d:\d\d\.\d+ +\d+ +\d+ +[IVEW] Granite *: ?", "", ln)
        out.append(ln)
    return out

def load(p):
    return strip(open(p).read().splitlines())

def sel(lines, *pats):
    return [ln for ln in lines if any(p in ln for p in pats)]

def norm_g10(ln):
    return re.sub(r"scratch=\d+ img=\d+", "scratch=X img=X", ln)

b0, b1 = load(B0), load(B1)
runs = {}
for tag, p in (("R1", R1), ("R2", R2)):
    try:
        runs[tag] = load(p)
    except FileNotFoundError:
        print(f"{tag}: MISSING {p}")
print(f"lines b0={len(b0)} b1={len(b1)} " + " ".join(f"{t}={len(v)}" for t, v in runs.items()))

CLASSES = [("FRAME", ["G11: FRAME"]), ("RECORD", ["G11: record", "G11:   inst"]),
           ("TEX", ["G11:   tex"]), ("FLUSH", ["G11: flush"]),
           ("G10n", ["G10: pass"]), ("STATE", ["G31: state"]),
           ("BYTES", ["G31: bytes"]), ("VPAGE", ["G30: vpage"]),
           ("LADDER", ["G29: ladder"]), ("VRAM", ["G29: vram"]),
           ("WROTE", ["G8: wrote"]), ("RUN", ["Running frame"])]
for tag, r in runs.items():
    for base, bl in (("B0", b0), ("B1", b1)):
        print(f"--- {tag}-vs-{base} ---")
        for name, pats in CLASSES:
            a, b = sel(r, *pats), sel(bl, *pats)
            if name == "G10n":
                a, b = [norm_g10(x) for x in a], [norm_g10(x) for x in b]
            # WROTE paths differ by run dir (g39 vs g38/g31): compare basenames
            if name == "WROTE":
                f = lambda s: [re.sub(r".*/g\d+/", "", x) for x in s]
                a, b = f(a), f(b)
            eq = (a == b)
            print(f"  {name}: {len(a)}/{len(b)} eq={eq}")
            if not eq:
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        print(f"    FIRST-DIFF idx{i}:\n     new {x[:160]}\n     base {y[:160]}")
                        break
                if len(a) != len(b):
                    print(f"    COUNT-MISMATCH new={len(a)} base={len(b)}")

# R-* regression checks per run
for tag, r in runs.items():
    print(f"--- R-* {tag} ---")
    g26 = sel(r, "G26: debug_mode delivered")
    print(f"  R-G26-1 receipts={len(g26)} vals={[re.findall(r'=\d', x) for x in g26]}")
    g10 = sel(r, "G10: pass")
    imgs = [re.search(r"img=(\d+)", x).group(1) for x in g10 if "img=" in x]
    # pass split: first 9 G10 lines = pass 0 (2 reset + ... ) — report raw + warm tail
    print(f"  R-G26-2 G10={len(g10)} img-tail8={imgs[-8:] if len(imgs) >= 8 else imgs}")
    g28 = sel(r, "G28: create_image_view")
    print(f"  R-G28-1 receipts={len(g28)} {g28[0][:120] if g28 else ''}")
    print(f"  R-G28-3 corrupted={len(sel(r, 'corrupted chunk'))} success-no={len(sel(r, 'success: no'))} success-yes={len(sel(r, 'success: yes'))}")
    print(f"  R-G26-3 crasher e5825d(txt)=present-in-log-ok(driver hash line is Stalled post, checked success) dispatch={len(sel(r, 'dispatch_texture_analysis'))} vkCreateCompute={len(sel(r, 'vkCreateComputePipelines'))}")
    print(f"  last-line: {r[-1][:100] if r else 'EMPTY'}")
    print(f"  Done! count={len(sel(r, 'Done!'))} wrote={len(sel(r, 'G8: wrote'))}")

# B bytes == load check per run (Odin rule-3/4 expectation)
LOAD_B = ("eea04488c453e75b", "149721", "0000000000000000")
for tag, r in runs.items():
    n = nload = 0
    for ln in sel(r, "G31: bytes"):
        b = re.search(r"B fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+)", ln)
        n += 1
        if b and b.groups() == LOAD_B:
            nload += 1
    print(f"{tag}: B==load {nload}/{n}")
