#!/usr/bin/env python3
"""GB7C3 read-only provenance checker.

Verifies candidate-pairs.tsv rows against the pinned GB7C2 full trace
(~/dev/ssx3-work/GB4/run/gb7c2/chain.tsv), batch rects, the observed
carrier src=dst+(1,1) shift, linear fbp offsets, and PPM dimensions.
Reads only; prints PASS/FAIL per check.
"""
import os
import re
import struct
import sys

TRACE = "/Users/brad/dev/ssx3-work/GB4/run/gb7c2/chain.tsv"
CAND = "/Users/brad/dev/ssx3/local/research/GB7C3/candidate-pairs.tsv"
PPM = "/Users/brad/dev/ssx3-work/GB4/run/gb7c2/ppm/vq-000600.ppm"
STRIDE = 8 * 64 * 4  # fbw8 CT32 linear bytes/row (swizzled addr NOT verified)

fails = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + f" {name}" + (f" :: {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def parse_xy(s):
    m = re.match(r"\((\d+),(\d+)\)", s)
    assert m is not None, s
    return (int(m.group(1)), int(m.group(2)))


def main():
    rows = open(TRACE).read().splitlines()
    print(f"trace_rows={len(rows) - 1}")
    traced = [r.split("\t") for r in rows[1:] if "traced-write" in r]
    carriers = [r.split("\t") for r in rows[1:] if "write-same-value-unknown" in r]
    batches_c1 = [r.split("\t") for r in rows[1:] if r.endswith("batch-c1")]
    batches_car = [r.split("\t") for r in rows[1:] if r.endswith("batch-carrier")]
    check("trace-320-data-rows", len(rows) - 1 == 320, f"got={len(rows) - 1}")
    check("c1-48-batches", len(batches_c1) == 48, f"got={len(batches_c1)}")
    check("carrier-24-samples", len(carriers) == 24, f"got={len(carriers)}")

    # observed carrier shift src == dst + (1,1) on all 24 samples
    ok = True
    for c in carriers:
        sx, sy = parse_xy(c[4])
        dx, dy = parse_xy(c[5])
        if not (sx == dx + 1 and sy == dy + 1):
            ok = False
    check("carrier-shift-src-dst-plus-1", ok)
    # wrap == src (identity) on all traced rows with wrap field
    ok = True
    for t in traced + carriers:
        tex = t[8]
        m = re.search(r"wrap=\((\d+),(\d+)\)", tex)
        s = t[4]
        if m and s != "-" and f"({m.group(1)},{m.group(2)})" != s:
            ok = False
    check("wrap-identity", ok)
    # carrier rects cover the 4 candidate dsts
    rects = {}
    for b in batches_car:
        m = re.search(r"rect=\((\d+),(\d+)\)-\((\d+),(\d+)\)", b[8])
        assert m is not None, b[8]
        rects[int(b[3])] = tuple(map(int, m.groups()))
    check(
        "carrier-rects-known",
        rects.get(10) == (319, 0, 350, 445)
        and rects.get(11) == (351, 0, 382, 445)
        and rects.get(12) == (383, 0, 414, 445),
        f"{rects.get(10)} {rects.get(11)} {rects.get(12)}",
    )

    clines = open(CAND).read().splitlines()
    check("cand-4-data-rows", len(clines) - 1 == 4, f"got={len(clines) - 1}")
    by_src = {}
    for t in traced:
        if t[0] == "600" and t[1] == "47176":
            by_src[t[5]] = t
    for line in clines[1:]:
        f = line.split("\t")
        cand, src, new, off, dst, batch, prior, neigh, amb = f
        t = by_src.get(src)
        check(f"{cand}-src-traced-write", t is not None, src)
        if t is None:
            continue
        check(f"{cand}-old-ne-new", t[6] != t[7], f"{t[6]}->{t[7]}")
        m = re.search(r"nibble=([0-9a-f])", t[8])
        check(f"{cand}-stroke-nibble-nonzero", m and m.group(1) != "0", m.group(1) if m else "?")
        sx, sy = parse_xy(src)
        dx, dy = parse_xy(dst)
        check(f"{cand}-dst-eq-src-minus-1", (dx, dy) == (sx - 1, sy - 1))
        x0, y0, x1, y1 = rects[int(batch)]
        check(f"{cand}-dst-in-batch-rect", x0 <= dx <= x1 and y0 <= dy <= y1, rects[int(batch)])
        want = sy * STRIDE + sx * 4
        check(f"{cand}-linear-off", off.lower() == hex(want), f"{off} vs {hex(want)}")
        check(f"{cand}-prior-unknown", prior == "unknown")
        check(f"{cand}-new-eq-trace-new", new == t[7])

    with open(PPM, "rb") as fh:
        magic = fh.readline().strip()
        wh = fh.readline().strip()
        mx = fh.readline().strip()
    check("ppm-512x448", magic == b"P6" and wh == b"512 448" and mx == b"255", f"{magic} {wh} {mx}")

    print("OVERALL " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


sys.exit(main())
