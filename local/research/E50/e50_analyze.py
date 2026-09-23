#!/usr/bin/env python3
"""E50 analyzer: screen classes, E4 head, VU1 entry dumps (matrix scan).

Usage: e50_analyze.py <label> [<label> ...]  (reads ~/dev/ssx3-work/E50/run)
Prints markdown tables to stdout.
"""
import gzip
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict

RUN = os.path.expanduser("~/dev/ssx3-work/E50/run")
# per-vsync gfx table windows (the race boot logs 1300..7610)
WINDOW = {"e50a": (1300, 1310), "e50b": (7600, 7610)}


def opener(path):
    if os.path.exists(path):
        return open(path, errors="replace")
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="replace")
    return None


def f32(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def kind(w):
    e = (w >> 23) & 0xFF
    if e == 0xFF:
        return "nan" if (w & 0x7FFFFF) else "inf"
    if e == 0 and (w & 0x7FFFFF):
        return "den"
    return "ok"


# ---------------- gfx stats ----------------
def gfx(label):
    f = opener(f"{RUN}/gfx-{label}.txt")
    if f is None:
        print(f"(no gfx for {label})\n")
        return {}
    print(f"### gfx stats ({label})\n")
    print("| vsync | mscal | d1_n | d1 on/off/straddle | d1 box | d2_n | d2 scr | d3 scr |")
    print("|---|---|---|---|---|---|---|---|")
    pcs_all = defaultdict(lambda: [0, 0, 0, 0])
    nv = 0
    lo, hi = WINDOW.get(label, (0, 1 << 62))
    for line in f:
        d = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
        if not (lo <= int(d["vsync"]) <= hi):
            continue
        print(f"| {d['vsync']} | {d['mscal']} | {d['d1_n']} | {d.get('d1_scr','-')} | "
              f"{d['d1_box']} | {d['d2_n']} | {d.get('d2_scr','-')} | {d.get('d3_scr','-')} |")
        if "pcs" in d:
            nv += 1
            for item in d["pcs"].split(";"):
                if item == "+more":
                    continue
                pc, ms, scr = item.split(":")
                on, off, st = scr.split("/")
                if not (lo <= int(d["vsync"]) <= hi):
                    continue
                a = pcs_all[int(pc, 16)]
                a[0] += int(ms); a[1] += int(on); a[2] += int(off); a[3] += int(st)
    print()
    if pcs_all:
        print(f"### per-startPC census ({label}, summed over {nv} vsyncs)\n")
        print("| startPC | MSCAL | PATH1 on | off | straddle | off % |")
        print("|---|---|---|---|---|---|")
        for pc in sorted(pcs_all):
            ms, on, off, st = pcs_all[pc]
            tot = on + off + st
            pct = f"{100.0*off/tot:.1f}" if tot else "-"
            print(f"| 0x{pc:x} | {ms} | {on} | {off} | {st} | {pct} |")
        print()
    return pcs_all


# ---------------- E4 head ----------------
EV = re.compile(r"(\w+)=(\S+)")


def head(label, n_rows=20):
    f = opener(f"{RUN}/e4-{label}/e4-head.txt")
    if f is None:
        print(f"(no e4 head for {label})\n")
        return
    hdr = f.readline().strip()
    print(f"### E4 head ({label}): `{hdr}`\n")
    draws = []
    xyofs = {}
    for line in f:
        d = dict(EV.findall(line))
        if d.get("kind") != "draw":
            continue
        ofs = d.get("ofs", "0,0").split(",")
        ox, oy = float(ofs[0]), float(ofs[1])
        sc = [int(v) for v in d["scissor"].split(",")]  # x0,y0,x1,y1
        vs = []
        for v in d.get("v", "").split(";"):
            if v:
                x, y, z = v.split(",")
                vs.append((float(x) - ox, float(y) - oy, float(z)))
        xs = [v[0] for v in vs]; ys = [v[1] for v in vs]
        if not vs:
            continue
        left, right, top, bot = sc[0], sc[2] + 1, sc[1], sc[3] + 1
        if max(xs) < left or min(xs) >= right or max(ys) < top or min(ys) >= bot:
            cls = "off"
        elif min(xs) >= left and max(xs) < right and min(ys) >= top and max(ys) < bot:
            cls = "on"
        else:
            cls = "straddle"
        d["_cls"] = cls; d["_vs"] = vs
        draws.append(d)
    c = Counter(d["_cls"] for d in draws)
    print(f"Head draws: {len(draws)}; on {c['on']}, off {c['off']}, straddle {c['straddle']}.\n")
    # guard-band pins
    pin = 0
    for d in draws:
        for (x, y, z) in d["_vs"]:
            if abs(x + (1792 - 1023.5)) < 0.01 or abs(x - (3071.5 - 1792)) < 0.01:
                pin += 1
    print(f"Vertices exactly at guard-band x = 1023.5/3071.5 (GS space): {pin} of "
          f"{sum(len(d['_vs']) for d in draws)}.\n")
    by = Counter((d["prim"], d["tex0"].split(",")[0], d["_cls"]) for d in draws)
    print("| prim | TBP0 | class | draws |")
    print("|---|---|---|---|")
    for (p, t, cl), n in sorted(by.items(), key=lambda kv: -kv[1])[:25]:
        print(f"| {p} | {t} | {cl} | {n} |")
    print()
    print(f"First {n_rows} draws (screen coords = GS - XYOFFSET):\n")
    print("| seq | prim | tme | TEX0 (tbp,tbw,psm,tw,th) | TEST | class | v0 | v1 | v2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for d in draws[:n_rows]:
        t = d["tex0"].split(",")
        vs = [f"{x:.1f},{y:.1f},{z:.0f}" for (x, y, z) in d["_vs"]]
        vs += [""] * (3 - len(vs))
        print(f"| {d['seq']} | {d['prim']} | {d['tme']} | {t[0]},{t[1]},{t[2]},{t[3]},{t[4]} | "
              f"{d['test']} | {d['_cls']} | {vs[0]} | {vs[1]} | {vs[2]} |")
    print()
    tri = [d for d in draws if d["prim"] in ("3", "4", "5")]
    print(f"First {n_rows} triangle/strip/fan draws (the world/3D candidates; {len(tri)} in the head):\n")
    print("| seq | prim | tme | TEX0 (tbp,tbw,psm,tw,th) | TEST | class | v0 | v1 | v2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for d in tri[:n_rows]:
        t = d["tex0"].split(",")
        vs = [f"{x:.1f},{y:.1f},{z:.0f}" for (x, y, z) in d["_vs"]]
        vs += [""] * (3 - len(vs))
        print(f"| {d['seq']} | {d['prim']} | {d['tme']} | {t[0]},{t[1]},{t[2]},{t[3]},{t[4]} | "
              f"{d['test']} | {d['_cls']} | {vs[0]} | {vs[1]} | {vs[2]} |")
    print()


# ---------------- VU1 entry trace ----------------
def entry_blocks(label):
    f = opener(f"{RUN}/entry-{label}.txt")
    if f is None:
        return []
    blocks = []
    cur = None
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("entry "):
            d = dict(EV.findall(line))
            cur = {"pc": int(d["startPC"], 16), "vsync": int(d["vsync"]),
                   "reg": {}, "mem": [None] * 1024, "vif": [], "pairs": []}
            blocks.append(cur)
        elif cur is None:
            continue
        elif line.startswith("reg "):
            parts = line.split()
            cur["reg"][parts[1]] = line[4:]
        elif line.startswith("vumem "):
            p = line.split()
            cur["mem"][int(p[1])] = [int(x, 16) for x in p[2:6]]
        elif line.startswith("vif "):
            cur["vif"].append(line)
        elif line.startswith("pair "):
            cur["pairs"].append(line)
        elif line.startswith("endentry"):
            cur["end"] = line
    return blocks


def mat_stats(rows):
    """rows: 4 lists of 4 floats. Returns flags + row norms + max off-dot."""
    flags = []
    words_ok = True
    for r in rows:
        for v in r:
            if isinstance(v, str):
                flags.append(v); words_ok = False
    if not words_ok:
        return flags, None, None
    norms = [math.sqrt(sum(v * v for v in r[:3])) for r in rows[:3]]
    dots = []
    for i in range(3):
        for j in range(i + 1, 3):
            if norms[i] > 0 and norms[j] > 0:
                dots.append(abs(sum(rows[i][k] * rows[j][k] for k in range(3))) / (norms[i] * norms[j]))
    maxdot = max(dots) if dots else None
    for n in norms:
        if n == 0:
            flags.append("zero-row")
        elif n > 1e6:
            flags.append("huge")
    if maxdot is not None and maxdot > 0.05:
        flags.append("non-orth")
    return flags, norms, maxdot


def row_floats(q):
    out = []
    for w in q:
        k = kind(w)
        out.append(f32(w) if k == "ok" else k)
    return out


def plausible_matrix(mem, r):
    rows = mem[r:r + 4]
    if any(q is None for q in rows):
        return False
    words = [w for q in rows for w in q]
    nz = sum(1 for w in words if w & 0x7FFFFFFF)
    if nz < 6:
        return False
    for w in words:
        e = (w >> 23) & 0xFF
        if w & 0x7FFFFFFF and not (0x60 <= e <= 0xA0):  # |v| in ~[1e-10, 1e10]
            if e != 0xFF and not (e == 0 and w & 0x7FFFFF):
                return False
    # reject rows that repeat exactly (vertex/colour runs)
    if len({tuple(q) for q in rows}) < 3:
        return False
    return True


LQ = re.compile(r"\| rd (\d+):")


def loaded_rows(block, limit=4000):
    rows = []
    for p in block["pairs"][:limit]:
        m = LQ.search(p)
        if m:
            rows.append(int(m.group(1)))
    return rows


def entry(label, pcs_census=None, max_mats=12):
    blocks = entry_blocks(label)
    if not blocks:
        print(f"(no entry trace for {label})\n")
        return blocks
    print(f"### VU1 entry blocks ({label})\n")
    print("| startPC | vsync | vif lines | UNPACK | pairs | end |")
    print("|---|---|---|---|---|---|")
    for b in blocks:
        nun = sum(1 for v in b["vif"] if v.startswith("vif UNPACK"))
        print(f"| 0x{b['pc']:x} | {b['vsync']} | {len(b['vif'])} | {nun} | {len(b['pairs'])} | "
              f"{b.get('end','(open)')} |")
    print()
    return blocks


def dump_matrix_rows(mem, r):
    lines = []
    for i in range(4):
        q = mem[r + i]
        fl = row_floats(q)
        lines.append(" ".join(f"{w:08x}" for w in q) + " | " +
                     " ".join(f"{v:.6g}" if not isinstance(v, str) else v for v in fl))
    return lines


def matrices(block, label, max_rows=40):
    mem = block["mem"]
    ld = loaded_rows(block)
    ldset = sorted(set(ld))
    print(f"#### startPC 0x{block['pc']:x} ({label}, vsync {block['vsync']}): "
          f"rows loaded by the first {len(block['pairs'])} pairs: "
          f"{', '.join(map(str, ldset[:60]))}{' …' if len(ldset) > 60 else ''}\n")
    cands = []
    for r in range(0, 1021):
        if plausible_matrix(mem, r):
            cands.append(r)
    # collapse overlapping candidates: keep starts that are loaded rows
    # or 4-aligned runs
    keep = []
    for r in cands:
        if keep and r < keep[-1] + 4:
            continue
        keep.append(r)
    print("| rows | loaded | 16 words (hex) / floats | flags | row norms | max |cos| |")
    print("|---|---|---|---|---|---|")
    n = 0
    for r in keep:
        rows = [row_floats(mem[r + i]) for i in range(4)]
        flags, norms, maxdot = mat_stats(rows)
        ldn = sum(1 for i in range(4) if (r + i) in ld)
        cell = "<br>".join(dump_matrix_rows(mem, r))
        ns = ",".join(f"{x:.4g}" for x in norms) if norms else "-"
        md = f"{maxdot:.3f}" if maxdot is not None else "-"
        print(f"| {r}–{r+3} | {ldn}/4 | `{cell}` | {' '.join(flags) or '-'} | {ns} | {md} |")
        n += 1
        if n >= max_rows:
            print(f"| … | | {len(keep) - n} more | | | |")
            break
    print()


def main():
    labels = sys.argv[1:]
    for label in labels:
        print(f"## {label}\n")
        pcs = gfx(label)
        head(label)
        blocks = entry(label, pcs)
        for b in blocks:
            matrices(b, label)




# ---------------- T65-format tables (appended after the T65 gate) -----------
def t65_counts(label, lo, hi):
    f = opener(f"{RUN}/gfx-{label}.txt")
    print(f"### PATH1 counts in T65 definitions ({label}, vsync {lo}–{hi})\n")
    print("| vsync | mscal | p1 verts | vx | vy | z | on | off | straddle | zero-area | adc |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for line in f:
        d = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
        v = int(d["vsync"])
        if v < lo or v > hi:
            continue
        t = d.get("d1_t65", "0,0,0,0,0,0").split(",")
        b = d["d1_box"].split(",") if d["d1_box"] != "none" else ["-"] * 6
        print(f"| {v} | {d['mscal']} | {t[0]} | {b[0]}..{b[1]} | {b[2]}..{b[3]} | {b[4]}..{b[5]} | "
              f"{t[1]} | {t[2]} | {t[3]} | {t[4]} | {t[5]} |")
    print("\n(vx/vy/z = the E33 box over drawn, non-ADC prims only; T65's vx/vy include ADC vertices.)\n")


def t65_pcs(label, lo, hi):
    f = opener(f"{RUN}/gfx-{label}.txt")
    acc = defaultdict(lambda: [0, 0, 0, 0])
    n = 0
    for line in f:
        d = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
        v = int(d["vsync"])
        if v < lo or v > hi or "pcs" not in d:
            continue
        n += 1
        for item in d["pcs"].split(";"):
            if item == "+more":
                continue
            pc, ms, scr = item.split(":")
            on, off, st = scr.split("/")
            a = acc[int(pc, 16)]
            a[0] += int(ms); a[1] += int(on); a[2] += int(off); a[3] += int(st)
    print(f"### Per-startPC census ({label}, {n} drawing vsyncs in {lo}–{hi}; per-vsync means)\n")
    print("| tpc | byte pc | MSCAL/vsync | PATH1 draws/vsync (on/off/straddle) |")
    print("|---|---|---|---|")
    for pc in sorted(acc):
        ms, on, off, st = acc[pc]
        print(f"| 0x{pc//8:x} | 0x{pc:x} | {ms/n:.1f} | {(on+off+st)/n:.1f} ({on/n:.0f}/{off/n:.0f}/{st/n:.0f}) |")
    print()


def fmtw(w):
    k = kind(w)
    return f"{w:08x} ({f32(w):.6g})" if k == "ok" else f"{w:08x} ({k})"


def t65_blocks(label):
    blocks = entry_blocks(label)
    cols = []
    for b in blocks:
        mem = b["mem"]
        print(f"**{label} tpc 0x{b['pc']//8:x} (byte 0x{b['pc']:x}), vsync {b['vsync']}**, first start at/after the gate\n")
        print("| qw | x | y | z | w |")
        print("|---|---|---|---|---|")
        for r in range(6):
            q = mem[r]
            print(f"| 0x{r:03x} | " + " | ".join(fmtw(w) for w in q) + " |")
        print()
        rows = [[f32(w) for w in mem[r]] for r in range(3)]
        bad = [kind(w) for r in range(4) for w in mem[r] if kind(w) != "ok"]
        colv = [[rows[i][c] for i in range(3)] for c in range(4)]
        nrm = [math.sqrt(sum(x * x for x in cv)) for cv in colv]
        dot = lambda a, c: sum(colv[a][i] * colv[c][i] for i in range(3))
        yx = nrm[1] / nrm[0] if nrm[0] else float("nan")
        cols.append((f"{label} vsync {b['vsync']} tpc 0x{b['pc']//8:x}", nrm, dot(0, 1), dot(0, 3), dot(1, 3), yx,
                     ",".join(sorted(set(bad))) or "none"))
    print("| block | abs col x | abs col y | abs col z | abs col w | x.y | x.w | y.w | y/x scale | NaN/Inf/den |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, nrm, xy, xw, yw, yx, bad in cols:
        print(f"| {name} | {nrm[0]:.6f} | {nrm[1]:.6f} | {nrm[2]:.6f} | {nrm[3]:.6f} | {xy:.2e} | {xw:.2e} | "
              f"{yw:.2e} | {yx:.4f} | {bad} |")
    print()
    return blocks


def t65_main(argv):
    # t65 <label> <lo> <hi>
    label, lo, hi = argv[0], int(argv[1]), int(argv[2])
    t65_counts(label, lo, hi)
    t65_pcs(label, lo, hi)
    if len(argv) > 3 and argv[3] == "blocks":
        t65_blocks(label)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "t65":
        t65_main(sys.argv[2:])
    else:
        main()
