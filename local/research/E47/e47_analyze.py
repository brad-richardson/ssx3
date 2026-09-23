#!/usr/bin/env python3
"""E47 analyzer: SC vs race tables from the windowed diagnostics.

Usage:
  python3 local/research/E47/e47_analyze.py <label> <from> <to> [<label> <from> <to> ...]

Reads ~/dev/ssx3-work/E47-run/{gfx,vu1,e43,mpg}-<label>.txt and
e4-<label>/e4-history.txt. Prints markdown tables per label. Lines outside
[from,to] are dropped (E43/MPG windows run past `to` on purpose).
"""
import collections
import os
import re
import sys

RUN = os.path.expanduser("~/dev/ssx3-work/E47-run")
PRIM_NAMES = ["point", "line", "lstrip", "tri", "tstrip", "tfan", "sprite", "prim7"]


def kv(line):
    return dict(re.findall(r"(\w+)=(\S+)", line))


def gfx(label, lo, hi):
    rows = []
    path = f"{RUN}/gfx-{label}.txt"
    if not os.path.exists(path):
        return rows
    for line in open(path):
        d = kv(line)
        if "vsync" in d and lo <= int(d["vsync"]) <= hi:
            rows.append(d)
    return rows


def print_gfx(label, rows):
    print(f"\n#### gfx stats {label} ({len(rows)} vsyncs)\n")
    cols = ["vsync", "mscal", "mscnt", "vu_cycles", "vu_exhausted", "vu_maxcyc",
            "xgkick", "p1_pkt", "p2_pkt", "p3_pkt", "d1_n", "d1_vert", "d2_n",
            "d2_vert", "d3_n", "d3_vert"]
    print("| " + " | ".join(cols) + " | top (fbp:primtype=n) |")
    print("|" + "---|" * (len(cols) + 1))
    for d in rows:
        print("| " + " | ".join(d.get(c, "-") for c in cols) + f" | {d.get('top', '-')} |")
    print("\nBoxes (x0,x1,y0,y1,z0,z1) per path:")
    for d in rows:
        print(f"- vsync {d['vsync']}: d1 {d.get('d1_box')} | d2 {d.get('d2_box')} | d3 {d.get('d3_box')}")


def decode_prim(p):
    p = int(p)
    return (f"{PRIM_NAMES[p & 7]} tme={(p >> 4) & 1} abe={(p >> 6) & 1} "
            f"fge={(p >> 5) & 1} fst={(p >> 8) & 1} ctxt={(p >> 9) & 1}")


def print_top_prims(label, rows):
    agg = collections.Counter()
    for d in rows:
        top = d.get("top", "none")
        if top == "none":
            continue
        for ent in top.split(","):
            pair, n = ent.split("=")
            tbp, prim = pair.split(":")
            agg[(int(tbp), int(prim))] += int(n)
    # gfx_stats noteDraw passes (FRAME.fbp, PRIM.type) despite the header's
    # "TBP0, PRIM" wording (gs_frontend.cpp:1620-1623).
    print(f"\n#### top (FRAME.fbp, prim type) summed over window, {label} (per-vsync top-5 only)\n")
    print("| FRAME.fbp | prim type | draws |")
    print("|---|---|---|")
    for (fbp, prim), n in agg.most_common(12):
        print(f"| {fbp} | {PRIM_NAMES[prim & 7]} | {n} |")


def vu1(label, lo, hi):
    census = collections.defaultdict(lambda: [0, 0, 0])
    details = []
    path = f"{RUN}/vu1-{label}.txt"
    if not os.path.exists(path):
        return census, details
    for line in open(path):
        if line.startswith("census "):
            d = kv(line)
            if lo <= int(d["vsync"]) <= hi:
                c = census[d["startPC"]]
                c[0] += 1
                c[1] += int(d["cycles"])
                c[2] += int(d["xgkick"])
        elif line.startswith("detail "):
            details.append(line.strip()[:200])
    return census, details


def print_vu1(label, census, details, nvs):
    print(f"\n#### VU1 budget-exhausted programs {label} (census lines; per window of {nvs} vsyncs)\n")
    print("| startPC | exhausted runs | per vsync | cycles total | xgkicks in exhausted runs |")
    print("|---|---|---|---|---|")
    for pc, (n, cyc, xg) in sorted(census.items(), key=lambda kvp: -kvp[1][0]):
        print(f"| {pc} | {n} | {n / max(nvs, 1):.1f} | {cyc} | {xg} |")
    print(f"\ndetail headers ({len(details)}):")
    for h in details[:40]:
        print(f"- `{h}`")


def e43(label, lo, hi):
    drec = collections.defaultdict(lambda: collections.Counter())
    drecs = collections.Counter()
    other = collections.Counter()
    path = f"{RUN}/e43-{label}.txt"
    if not os.path.exists(path):
        return drec, drecs, other
    for line in open(path):
        kind = line.split(" ", 1)[0]
        d = kv(line)
        if "vsync" not in d or not (lo <= int(d["vsync"]) <= hi):
            continue
        if kind == "drec":
            drec[int(d["vsync"])][(d["src"], d["mode"])] += int(d["count"])
        elif kind == "drecs":
            drecs[(d["src"], d["mode"], d["w0"])] += 1
        else:
            other[kind] += 1
    return drec, drecs, other


def print_e43(label, drec, drecs, other):
    print(f"\n#### draw-record modes per vsync {label} (E43 drec)\n")
    keys = sorted({k for v in drec.values() for k in v})
    print("| vsync | " + " | ".join(f"{s} m{m}" for s, m in keys) + " |")
    print("|---|" + "---|" * len(keys))
    for t in sorted(drec):
        print(f"| {t} | " + " | ".join(str(drec[t].get(k, 0)) for k in keys) + " |")
    print(f"\ndrecs (src, mode, w0) sample counts: {dict(drecs.most_common(20))}")
    print(f"other line kinds in window: {dict(other)}")


def mpg(label, lo, hi):
    rows = []
    path = f"{RUN}/mpg-{label}.txt"
    if not os.path.exists(path):
        return rows
    for line in open(path):
        d = kv(line)
        if "vsync" in d and lo <= int(d["vsync"]) <= hi:
            rows.append(d)
    return rows


def print_mpg(label, rows, nvs):
    print(f"\n#### MPG uploads {label} ({len(rows)} in window)\n")
    agg = collections.Counter((d["imm"], d["num"], d["dest"], d["outcome"], d["fnv"]) for d in rows)
    print("| imm | num | dest bytes | outcome | fnv | count | per vsync |")
    print("|---|---|---|---|---|---|---|")
    for (imm, num, dest, oc, fnv), n in sorted(agg.items(), key=lambda x: (-x[1], x[0])):
        print(f"| {imm} | {num} | {dest} | {oc} | {fnv} | {n} | {n / max(nvs, 1):.1f} |")


def hist(label):
    path = f"{RUN}/e4-{label}/e4-history.txt"
    if not os.path.exists(path):
        return None, []
    header, draws = [], []
    for line in open(path):
        if line.startswith("#"):
            header.append(line.strip())
        elif "kind=draw" in line:
            draws.append(line.strip())
    return header, draws


def parse_draw(line):
    d = kv(line)
    x0, x1 = (float(v) for v in d["x"].split(".."))
    y0, y1 = (float(v) for v in d["y"].split(".."))
    d["area"] = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    return d


def print_hist(label, header, draws):
    print(f"\n#### E4 GS history {label}\n")
    for h in header:
        print(f"- `{h}`")
    if not draws:
        print("\n(no draw events)")
        return
    ds = [parse_draw(l) for l in draws]
    ticks = collections.Counter(d["tick"] for d in ds)
    print(f"\ndraw events: {len(ds)} by tick {dict(ticks)}")
    print("\nPrim census over the history's draw events:\n")
    c = collections.Counter((PRIM_NAMES[int(d["prim"]) & 7], d["ctxt"], d["tme"], d["abe"],
                             d["fbp"], d["zbp"], d["test"], d["alpha"], d["fbmsk"],
                             d["zmask"]) for d in ds)
    print("| prim | ctxt | tme | abe | fbp | zbp | test | alpha | fbmsk | zmask | draws |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, n in c.most_common(30):
        print("| " + " | ".join(str(x) for x in k) + f" | {n} |")
    print("\n10 largest-area draws:\n")
    print("| seq | tick | prim | ctxt | tme | abe | FRAME fbp/fbw/psm/fbmsk | ZBUF zbp/zpsm/zmask | TEST | ALPHA | SCISSOR | TEX0 | x | y | z | vtx a | verts |")
    print("|---|" * 1 + "---|" * 16)
    for d in sorted(ds, key=lambda d: -d["area"])[:10]:
        print(f"| {d['seq']} | {d['tick']} | {PRIM_NAMES[int(d['prim']) & 7]} | {d['ctxt']} | {d['tme']} | {d['abe']} "
              f"| {d['fbp']}/{d['fbw']}/{d['psm']}/{d['fbmsk']} | {d['zbp']}/{d['zpsm']}/{d['zmask']} "
              f"| {d['test']} | {d['alpha']} | {d['scissor']} | {d['tex0']} | {d['x']} | {d['y']} | {d['z']} "
              f"| {d['a']} | {d['verts']} |")


def main(argv):
    specs = [(argv[i], int(argv[i + 1]), int(argv[i + 2])) for i in range(0, len(argv), 3)]
    for label, lo, hi in specs:
        nvs = hi - lo + 1
        print(f"\n### {label} window {lo}-{hi}")
        rows = gfx(label, lo, hi)
        print_gfx(label, rows)
        print_top_prims(label, rows)
        census, details = vu1(label, lo, hi)
        print_vu1(label, census, details, nvs)
        print_e43(label, *e43(label, lo, hi))
        print_mpg(label, mpg(label, lo, hi), nvs)
        print_hist(label, *hist(label))


if __name__ == "__main__":
    main(sys.argv[1:])
