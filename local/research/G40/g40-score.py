#!/usr/bin/env python3
# G40: score the F1/F2/F3 wall from the Mac (F0) + Odin logs.
# Usage: g40-score.py <mac-stderr> <odin-logcat>
# Prints O1-O5 split tables + verdict. Exit 0 iff parse complete.
import re
import sys

MAC, ODIN = sys.argv[1], sys.argv[2]
LOAD = "eea04488c453e75b"


def rows(path):
    out = {"O1": {}, "O2": {}, "O2x": {}, "O3": {}, "O3b": {}, "O4": {}, "O4m": {}, "O5": {}, "O5i": {}}
    for ln in open(path, errors="replace"):
        m = re.search(r"G40: (O1|O2x|O2|O3b|O3|O4m|O4|O5) (.*)", ln)
        if not m:
            continue
        k, body = m.group(1), m.group(2)
        f = dict(re.findall(r"(\S+?)=([0-9a-fx]+|-?\d+|[A-Za-z]+)", body))
        if k == "O1":
            out["O1"][int(f["ford"])] = body.strip()
        elif k == "O2x":
            out["O2x"][int(f["ford"])] = body.strip()
        elif k == "O5" and "inst=" in body:
            out["O5i"][(int(f["ford"]), int(f["inst"]))] = body.strip()
        elif k in ("O2", "O3", "O3b", "O4", "O4m", "O5"):
            c = int(f.get("cord", -99))
            out[k].setdefault(c, []).append(body.strip())
    return out


def get(d, c, i=0):
    v = d.get(c, [])
    return v[i] if len(v) > i else "MISSING"


mac, od = rows(MAC), rows(ODIN)
print("== counts mac/odin ==")
for k in ("O1", "O2", "O2x", "O3", "O3b", "O4", "O4m", "O5", "O5i"):
    print(f"{k}: {len(mac[k])}/{len(od[k])}")
print("== cord0/cord1 probe rows ==")
for k in ("O2", "O3", "O3b", "O4"):
    for c in (0, 1):
        print(f"{k} mac c{c}: {get(mac[k], c)}")
        print(f"{k} odin c{c}: {get(od[k], c)}")
print("== O1 comp rows (acc) mac vs odin ==")
for c in range(16):
    mo = [b for f, b in mac["O1"].items() if f"cord={c} " in b]
    oo = [b for f, b in od["O1"].items() if f"cord={c} " in b]
    acc = lambda b: re.search(r"acc=(\d+)", b[0]).group(1) if b else "?"
    print(f"cord{c}: mac acc={acc(mo)} odin acc={acc(oo)}")
print("== O4m hash mac vs odin ==")
for c in range(16):
    mh = re.search(r"hash=([0-9a-f]+)", get(mac["O4m"], c))
    oh = re.search(r"hash=([0-9a-f]+)", get(od["O4m"], c))
    print(f"cord{c}: mac={mh.group(1) if mh else '?'} odin={oh.group(1) if oh else '?'}")
print("== verdict inputs (cord1) ==")
o1 = re.search(r"acc=(\d+)", [b for f, b in od["O1"].items() if "cord=1 " in b][0]).group(1)
o3 = re.search(r"post-fnv=([0-9a-f]+)", get(od["O3"], 1)).group(1)
o3b = re.search(r"gpuB-fnv=([0-9a-f]+)", get(od["O3b"], 1)).group(1)
o4o = re.search(r"tex-fnv=([0-9a-f]+)", get(od["O4"], 1)).group(1)
o4m = re.search(r"tex-fnv=([0-9a-f]+)", get(mac["O4"], 1)).group(1)
o4o0 = re.search(r"tex-fnv=([0-9a-f]+)", get(od["O4"], 0)).group(1)
print(f"O1acc={o1} O3==load:{o3 == LOAD} O3b==load:{o3b == LOAD} O4==mac:{o4o == o4m} O4c1==O4c0:{o4o == o4o0}")
if o1 == "17" and o4o == o4m and o3 == LOAD and o3b == LOAD:
    print("VERDICT: F2 (unwritten B, execution-loss subtype: O1=17, O4=mac-exact, O3=O3b=load)")
elif o1 != "17":
    print("VERDICT: F1 (O1<17)")
elif o4o != o4m:
    print("VERDICT: F3-or-OTHER (O4 differs from mac)")
else:
    print("VERDICT: OTHER (unclassified)")
