#!/usr/bin/env python3
# G41 scorer: canary matrix (Mac vs Odin per cell) + hash-input breakdown
# check + scratch-overlap violation census. Mechanical extraction only.
# Usage: g41-score.py <mac-stderr> <odin-logcat>
import re
import sys

MAC, ODIN = sys.argv[1], sys.argv[2]


def parse(path):
    t = open(path).read()
    d = {}
    d["cord"] = re.findall(r"G41: cord g41=(-?\d+) g40=(-?\d+) ford=(\d+) prims=(\d+) tex=(\d+)", t)
    d["census"] = re.findall(r"G41: census ford=(\d+) prims=(\d+) inst=(\d+)/(\d+) FBP=(\d+) FBW=(\d+) PSM=(\d+) MSK=([0-9a-f]+) ZBP=(\d+) ZPSM=(\d+) ZMSK=(\d+) zwr=(\d+) zsen=(\d+) cwm=([0-9a-f]+) bb=(-?\d+,-?\d+,-?\d+,-?\d+) fpg=(\d+)\.\.(\d+) zpg=(\d+)\.\.(\d+) fov=(\d+) zov=(\d+) reason=([A-Za-z]+)", t)
    d["hash"] = re.findall(r"G41: hash inputs tex0=([0-9a-f]+) tex1=([0-9a-f]+) texa=([0-9a-f]+) mb13=([0-9a-f]+) mb46=([0-9a-f]+) clamp=([0-9a-f]+) bank=(\d+) smp=(\d+) recomp=([0-9a-f]+) TBP0=(\d+) TBW=(\d+) TPSM=(\d+)", t)
    d["rect"] = re.findall(r"G41: hash rect x=(\d+) y=(\d+) w=(\d+) h=(\d+) lv=(\d+) ctx=(\d+) rtex0=([0-9a-f]+) rtex1=([0-9a-f]+) rclamp=([0-9a-f]+) rmb13=([0-9a-f]+) rmb46=([0-9a-f]+) rtexa=([0-9a-f]+)", t)
    d["texinfo"] = re.findall(r"G41: hash texinfo n=(\d+) sizes=([^ ]+) region=([^ ]+) bias=([^ ]+) arrayed=(-?\d+) flags=(-?\d+)", t)
    d["arena"] = re.findall(r"G41: arena pre-fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+) vq=(\d+)", t)
    d["c5live"] = re.findall(r"G41: C5 live prim=([0-9a-f]+) test=([0-9a-f]+) zbuf=([0-9a-f]+) tex0=([0-9a-f]+) alpha=([0-9a-f]+) fba=([0-9a-f]+) pabe=([0-9a-f]+)", t)
    d["kick"] = re.findall(r"G41: C(\d) kick acc=(\d+) ctx=(\d+) prim=([0-9a-f]+) FBP=(\d+) FBW=(\d+) PSM=(\d+) MSK=([0-9a-f]+) ZBP=(\d+) ZMSK=(\d+) bb=(-?\d+,-?\d+,-?\d+,-?\d+)", t)
    d["verd"] = re.findall(r"G41: C(\d) verd acc=(\d+) landed=(\d+) nchg=(\d+) chg0=(\d+) fbp=(\d+)", t)
    d["chg"] = re.findall(r"G41: C(\d) chg page=(\d+) fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+)", t)
    d["restored"] = re.findall(r"G41: C(\d) restored=(\d+|MAPFAIL)", t)
    d["o4m"] = re.findall(r"G40: O4m ford=(\d+) cord=(-?\d+) texdims=(\d+x\d+) created=(\d+) longterm=(\d+) tbp0=(\d+) tbw=(\d+) psm=(\d+) lv=(\d+) smp=(\d+) reuse=(\d+) hash=([0-9a-f]+)", t)
    d["o3"] = re.findall(r"G40: O3 ford=(\d+) cord=(-?\d+) rec=(\d+) B post-fnv=([0-9a-f]+) nz=(\d+) head=([0-9a-f]+)", t)
    d["done"] = "Done!" in t
    return d


m, o = parse(MAC), parse(ODIN)

print("== fire/census ==")
print("mac cord rows:", len(m["cord"]), "census rows:", len(m["census"]))
print("odin cord rows:", len(o["cord"]), "census rows:", len(o["census"]))
for tag, d in (("mac", m), ("odin", o)):
    fov = [c for c in d["census"] if c[19] == "1"]
    zov = [c for c in d["census"] if c[20] == "1"]
    print("%s overlap: fov=%d zov=%d %s" % (tag, len(fov), len(zov), "VIOLATION" if (fov or zov) else "clean"))

print("== hash breakdown ==")
for tag, d in (("mac", m), ("odin", o)):
    h = d["hash"][0] if d["hash"] else None
    o4 = [x for x in d["o4m"] if x[1] == "1"]
    o4h = o4[0][11] if o4 else "?"
    print(tag, "inputs:", h, "rect:", d["rect"], "texinfo:", d["texinfo"])
    print(tag, "recomp==o4m-cord1:", (h[8] == o4h) if h else None, "recomp=%s o4m=%s" % (h[8] if h else "?", o4h))
if m["hash"] and o["hash"]:
    names = ["tex0", "tex1", "texa", "mb13", "mb46", "clamp", "bank", "smp"]
    diffs = [n for i, n in enumerate(names) if m["hash"][0][i] != o["hash"][0][i]]
    print("input diffs mac-vs-odin:", diffs if diffs else "NONE (identical inputs, different hash impossible)")
    print("rect mac-vs-odin:", "SAME" if m["rect"] == o["rect"] else ("DIFF " + str((m["rect"], o["rect"]))))
    print("texinfo mac-vs-odin:", "SAME" if m["texinfo"] == o["texinfo"] else ("DIFF " + str((m["texinfo"], o["texinfo"]))))

print("== canary matrix ==")
print("cell | mac kick acc/FBP/PSM/MSK | mac landed/nchg/chg0 | odin kick | odin landed/nchg/chg0")
for c in "12345":
    mk = [k for k in m["kick"] if k[0] == c]
    mv = [v for v in m["verd"] if v[0] == c]
    ok = [k for k in o["kick"] if k[0] == c]
    ov = [v for v in o["verd"] if v[0] == c]
    print("C%s | %s %s | %s %s" % (c, mk, mv, ok, ov))
print("== chg pages ==")
for tag, d in (("mac", m), ("odin", o)):
    for c in d["chg"]:
        print(tag, "C%s page=%s fnv=%s nz=%s head=%s" % c)
print("== restored ==")
print("mac:", m["restored"], "odin:", o["restored"])
print("== arena/vq ==")
print("mac:", m["arena"], "odin:", o["arena"])
print("== B at cord1 (O3) ==")
print("mac:", [x for x in m["o3"] if x[1] == "1"])
print("odin:", [x for x in o["o3"] if x[1] == "1"])
print("done:", m["done"], o["done"])

# Mechanical verdict on the matrix
ml = {v[0]: v[2] for v in m["verd"]}
ol = {v[0]: v[2] for v in o["verd"]}
print("VERDICT-MATRIX mac-landed=%s odin-landed=%s" % (ml, ol))
