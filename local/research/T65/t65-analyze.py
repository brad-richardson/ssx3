#!/usr/bin/env python3
"""T65 analyzer: VU1 start dumps (t65-vu1-N.bin) + T65_BOX lines.

Usage:
  t65-analyze.py progs <dump.bin>                 program-start list (seq, vsync, tpc, xgkicks, fnvs)
  t65-analyze.py mats  <dump.bin> <seq> [label]   VF regs + matrix-like 4x4 blocks at that program start
  t65-analyze.py const <dump.bin> <ee_vsync>      qwords constant across every start of that EE vsync
  t65-analyze.py box   <box.txt> <from> <to>      T65_BOX rows for a GS vsync range
"""
import math
import re
import struct
import sys

HDR = 20
REGS = 32 + 128 + 4
MEM = 0x4000


def read_dump(path):
    recs = []
    micro = None
    with open(path, "rb") as f:
        data = f.read()
    o = 0
    while o < len(data):
        h = struct.unpack_from("<20I", data, o)
        assert h[0] == 0x52353654, f"bad magic at {o}"
        o += HDR * 4
        regs = struct.unpack_from(f"<{REGS}I", data, o)
        o += REGS * 4
        mem = data[o:o + MEM]
        o += MEM
        if h[18]:
            micro = data[o:o + MEM]
            o += MEM
        recs.append({
            "seq": h[1], "ee": h[2], "gs": h[3], "tpc": h[4], "cycle": h[5] | (h[6] << 32),
            "xg": h[7] | (h[8] << 32), "top": h[9], "tops": h[10], "itop": h[11], "itops": h[12],
            "base": h[13], "ofst": h[14], "dbf": h[15], "dfnv": h[16], "mfnv": h[17], "has_micro": h[18],
            "vi": regs[:32], "vf": [regs[32 + i * 4:32 + i * 4 + 4] for i in range(32)], "acc": regs[160:164],
            "mem": mem, "micro": micro,
        })
    return recs


def f32(u):
    return struct.unpack("<f", struct.pack("<I", u))[0]


def fclass(u):
    e = (u >> 23) & 0xFF
    m = u & 0x7FFFFF
    if e == 0xFF:
        return "NaN" if m else "Inf"
    if e == 0 and m:
        return "den"
    return ""


def fmt(u):
    c = fclass(u)
    if c == "NaN":
        return f"{u:08x} (NaN)"
    if c == "Inf":
        return f"{u:08x} ({'-' if u >> 31 else '+'}Inf)"
    if c == "den":
        return f"{u:08x} (den {f32(u):.3g})"
    return f"{u:08x} ({f32(u):.6g})"


def qwords(mem):
    return [struct.unpack_from("<4I", mem, r * 16) for r in range(MEM // 16)]


def block_kind(rows):
    """rows: 4 tuples of 4 u32. Returns (kind, notes) or None."""
    words = [w for row in rows for w in row]
    flags = [fclass(w) for w in words]
    vals = [f32(w) if not fclass(w) else float("nan") for w in words]
    nz = [abs(v) for v in vals if v == v and v != 0.0]
    bad = sum(1 for f in flags if f)
    # affine (row-vector convention): w column (0,0,0,1)
    r = [[f32(w) for w in row] for row in rows]
    if bad == 0 and r[0][3] == 0.0 and r[1][3] == 0.0 and r[2][3] == 0.0 and r[3][3] == 1.0:
        norms = [math.sqrt(sum(x * x for x in r[i][:3])) for i in range(3)]
        if all(1e-4 <= n <= 1e5 for n in norms):
            return "affine"
    # general 4x4: >= 10 finite nonzero entries in a sane range, no row all-equal-to-vertex pattern
    if len(nz) >= 10 and all(1e-6 <= a <= 1e7 for a in nz) and bad <= 4:
        ws = [r[i][3] for i in range(4)]
        if all(w == 1.0 for w in ws):
            return None  # four xyz1 vertices
        rowsets = {tuple(row) for row in rows}
        if len(rowsets) < 3:
            return None
        nzrows = sum(1 for i in range(4) if any(x != 0.0 for x in r[i] if x == x))
        if nzrows == 4 and bad == 0:
            norms, dots, _ = metrics(rows)
            if all(abs(d) > 0.99 for d in dots if d == d):
                return None  # rows nearly parallel: a run of nearby vertex positions, not a basis
            return "general"
    return None


def metrics(rows):
    r = [[f32(w) for w in row] for row in rows]
    norms = [math.sqrt(sum(x * x for x in r[i][:3])) for i in range(3)]
    dots = []
    for a, b in ((0, 1), (0, 2), (1, 2)):
        d = sum(r[a][k] * r[b][k] for k in range(3))
        dots.append(d / (norms[a] * norms[b]) if norms[a] * norms[b] else float("nan"))
    m = [row[:3] for row in r[:3]]
    det = (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
           + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    return norms, dots, det


def cmd_progs(path):
    recs = read_dump(path)
    print(f"# program starts in {path}: {len(recs)} records")
    print("| seq | ee_vsync | gs_vsync | tpc (instr) | byte pc | xgkicks (to next start) | mfnv | dfnv | tops | itops | top | itop | dbf |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(recs):
        xk = (recs[i + 1]["xg"] - r["xg"]) if i + 1 < len(recs) else "?"
        print(f"| {r['seq']} | {r['ee']} | {r['gs']} | 0x{r['tpc']:x} | 0x{r['tpc'] * 8:x} | {xk} | {r['mfnv']:08x} | {r['dfnv']:08x} | "
              f"0x{r['tops']:x} | 0x{r['itops']:x} | 0x{r['top']:x} | 0x{r['itop']:x} | {r['dbf']} |")
    # summary by (tpc, mfnv)
    agg = {}
    for i, r in enumerate(recs):
        k = (r["tpc"], r["mfnv"])
        a = agg.setdefault(k, [0, 0, None])
        a[0] += 1
        if i + 1 < len(recs):
            a[1] += recs[i + 1]["xg"] - r["xg"]
        if a[2] is None:
            a[2] = r["seq"]
    print()
    print("| tpc (instr) | byte pc | mfnv | starts | xgkicks (sum) | first seq |")
    print("|---|---|---|---|---|---|")
    for (tpc, mf), (n, xk, first) in sorted(agg.items(), key=lambda kv: kv[1][2]):
        print(f"| 0x{tpc:x} | 0x{tpc * 8:x} | {mf:08x} | {n} | {xk} | {first} |")


def cmd_mats(path, seq, label):
    recs = read_dump(path)
    r = next(x for x in recs if x["seq"] == seq)
    print(f"# {label}: {path} seq {seq} ee_vsync {r['ee']} gs_vsync {r['gs']} tpc 0x{r['tpc']:x} (byte 0x{r['tpc'] * 8:x}) mfnv {r['mfnv']:08x} dfnv {r['dfnv']:08x}")
    print(f"tops 0x{r['tops']:x} itops 0x{r['itops']:x} top 0x{r['top']:x} itop 0x{r['itop']:x} base 0x{r['base']:x} ofst 0x{r['ofst']:x} dbf {r['dbf']}")
    print()
    print("VI: " + " ".join(f"vi{i:02d}={r['vi'][i] & 0xffff:04x}" for i in range(16)))
    print()
    print("| VF | x | y | z | w |")
    print("|---|---|---|---|---|")
    for i in range(32):
        print(f"| vf{i:02d} | " + " | ".join(fmt(w) for w in r["vf"][i]) + " |")
    print(f"| ACC | " + " | ".join(fmt(w) for w in r["acc"]) + " |")
    print()
    print("## VF register windows that look like a matrix (4 consecutive VF as rows)")
    print()
    for v in range(0, 29):
        k = block_kind([tuple(r["vf"][v + i]) for i in range(4)])
        if k:
            norms, dots, det = metrics([tuple(r["vf"][v + i]) for i in range(4)])
            print(f"- vf{v:02d}-vf{v + 3:02d}: {k}; row norms {norms[0]:.4g} {norms[1]:.4g} {norms[2]:.4g}; cos {dots[0]:.3f} {dots[1]:.3f} {dots[2]:.3f}; det3 {det:.4g}")
    print()
    q = qwords(r["mem"])
    found = []
    taken = set()
    for kind_pass in ("affine", "general"):
        for off in range(len(q) - 3):
            if any(o in taken for o in range(off, off + 4)):
                continue
            rows = q[off:off + 4]
            k = block_kind(rows)
            if k == kind_pass:
                found.append((off, k, rows))
                taken.update(range(off, off + 4))
    found.sort()
    print(f"## Matrix-like 4x4 blocks in VU1 data memory: {len(found)}")
    print()
    print("| qw | byte | kind | row norms (3x3) | cos(r0,r1) cos(r0,r2) cos(r1,r2) | det3 | flags |")
    print("|---|---|---|---|---|---|---|")
    for off, k, rows in found:
        norms, dots, det = metrics(rows)
        flags = sorted({fclass(w) for row in rows for w in row} - {""})
        print(f"| 0x{off:03x} | 0x{off * 16:04x} | {k} | {norms[0]:.4g} {norms[1]:.4g} {norms[2]:.4g} | "
              f"{dots[0]:.3f} {dots[1]:.3f} {dots[2]:.3f} | {det:.4g} | {','.join(flags) or '-'} |")
    print()
    for off, k, rows in found:
        print(f"### qw 0x{off:03x} (byte 0x{off * 16:04x}) {k}")
        print()
        print("| row | x | y | z | w |")
        print("|---|---|---|---|---|")
        for i, row in enumerate(rows):
            print(f"| {i} | " + " | ".join(fmt(w) for w in row) + " |")
        print()


def cmd_const(path, ee):
    recs = [x for x in read_dump(path) if x["ee"] == ee]
    qs = [qwords(x["mem"]) for x in recs]
    const = [i for i in range(len(qs[0])) if all(q[i] == qs[0][i] for q in qs[1:])]
    runs = []
    for i in const:
        if runs and runs[-1][1] == i - 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    print(f"# {path} ee_vsync {ee}: {len(recs)} starts; {len(const)} of 1024 qwords constant across all")
    print("| qw range | count | nonzero qwords |")
    print("|---|---|---|")
    for a, b in runs:
        nzc = sum(1 for i in range(a, b + 1) if any(qs[0][i]))
        print(f"| 0x{a:03x}-0x{b:03x} | {b - a + 1} | {nzc} |")


BOX_RE = re.compile(r"T65_BOX vsync=(\d+) (.*)")


def cmd_box(path, a, b):
    print("| vsync | p1 verts | vx | vy | z | on | off | straddle | zero-area | adc | prim px | prim py | of | scissor | ctxchg | non-p1 prims |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for line in open(path, errors="replace"):
        m = BOX_RE.search(line)
        if not m:
            continue
        v = int(m.group(1))
        if not (a <= v <= b):
            continue
        kv = dict(t.split("=", 1) for t in m.group(2).split())
        print(f"| {v} | {kv['p1_verts']} | {kv['vx']} | {kv['vy']} | {kv['z']} | {kv['prims_on']} | {kv['off']} | {kv['strad']} | "
              f"{kv['zeroarea']} | {kv['adc']} | {kv['px']} | {kv['py']} | {kv['of']} | {kv['sc']} | {kv['ctxchg']} | {kv['np1_prims']} |")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "progs":
        cmd_progs(sys.argv[2])
    elif c == "mats":
        cmd_mats(sys.argv[2], int(sys.argv[3], 0), sys.argv[4] if len(sys.argv) > 4 else "")
    elif c == "const":
        cmd_const(sys.argv[2], int(sys.argv[3], 0))
    elif c == "box":
        cmd_box(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
