#!/usr/bin/env python3
"""GB7C6 checker: verifies packet5470 identity, GIF walk, batch10 math and table fields.

Format-only checks against the pinned capture + sidecar + X5 index. Asserts NO
semantic glyph claim and NO GPU cause. Exit 0 ACCEPT, else FAIL with reasons.
"""
import hashlib
import math
import os
import struct
import sys

CAP = "/Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin"
PATHS = "/Users/brad/dev/ssx3-work/GB4/run/gb4p4.paths.txt"
X5 = "/Users/brad/dev/ssx3/local/research/X5/packets-949-950.csv"
TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "packet-table.tsv")

CAP_SHA = "a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851"
PKT_SHA = "79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31"
FAIL = []


def check(name, cond, detail=None):
    tail = "" if detail is None or cond else " :: " + str(detail)
    print(("PASS " if cond else "FAIL ") + name + tail)
    if not cond:
        FAIL.append(name)


def fnv(data):
    h = 2166136261
    for b in data:
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h


def bt_ct():
    bt = [[0, 1, 4, 5, 16, 17, 20, 21], [2, 3, 6, 7, 18, 19, 22, 23],
          [8, 9, 12, 13, 24, 25, 28, 29], [10, 11, 14, 15, 26, 27, 30, 31]]
    ct = [[0, 1, 4, 5, 8, 9, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15],
          [16, 17, 20, 21, 24, 25, 28, 29], [18, 19, 22, 23, 26, 27, 30, 31],
          [32, 33, 36, 37, 40, 41, 44, 45], [34, 35, 38, 39, 42, 43, 46, 47],
          [48, 49, 52, 53, 56, 57, 60, 61], [50, 51, 54, 55, 58, 59, 62, 63]]
    return bt, ct


def addr32(block, width, x, y):
    bt, ct = bt_ct()
    ppr = width or 1
    page = (block >> 5) + (y >> 5) * ppr + (x >> 6)
    bid = (block & 0x1F) + bt[(y >> 3) & 3][(x >> 3) & 7]
    return (page << 13) + ((bid >> 5) << 13) + (bid & 0x1F) * 256 + ct[y & 7][x & 7] * 4


def walk_gif(data):
    """Mirror GS::processGIFPacket tag walk (PACKED/REGLIST/IMAGE)."""
    off, tags = 0, []
    while off + 16 <= len(data):
        lo = struct.unpack("<Q", data[off:off + 8])[0]
        hi = struct.unpack("<Q", data[off + 8:off + 16])[0]
        off += 16
        nloop = lo & 0x7FFF
        pre = (lo >> 46) & 1
        flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xF or 16
        regs = [(hi >> (i * 4)) & 0xF for i in range(nreg)]
        payload = []
        if flg == 0:
            for _ in range(nloop):
                for r in regs:
                    lo2 = struct.unpack("<Q", data[off:off + 8])[0]
                    hi2 = struct.unpack("<Q", data[off + 8:off + 16])[0]
                    off += 16
                    payload.append((r, lo2, hi2))
        elif flg == 1:
            for _ in range(nloop):
                for r in regs:
                    payload.append((r, struct.unpack("<Q", data[off:off + 8])[0]))
                    off += 8
            if (nloop * nreg) & 1:
                off += 8
        elif flg == 2:
            off += nloop * 16
        else:
            return None, off
        tags.append({"nloop": nloop, "pre": pre, "flg": flg, "regs": regs, "payload": payload})
    return tags, off


def main():
    # 1. capture SHA (pinned)
    h = hashlib.sha256()
    with open(CAP, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    check("capture-sha", h.hexdigest() == CAP_SHA, h.hexdigest())

    # 2. independent stream scan to packet5470
    f = open(CAP, "rb")
    check("capture-magic", f.read(8) == b"PS2XGSC1")
    pkt_ord, found, prev, nxt = -1, None, None, None
    while True:
        off = f.tell()
        lb = f.read(4)
        if not lb:
            break
        ln = struct.unpack("<I", lb)[0]
        rec = f.read(ln)
        if len(rec) != ln:
            check("stream-truncated", False, off)
            break
        if rec[0] == 1:
            pkt_ord += 1
            if pkt_ord == 5469:
                prev = (struct.unpack("<Q", rec[1:9])[0], rec[9],
                        struct.unpack("<I", rec[10:14])[0])
            if pkt_ord == 5470:
                found = {"off": off, "len": ln, "tick": struct.unpack("<Q", rec[1:9])[0],
                         "epath": rec[9], "size": struct.unpack("<I", rec[10:14])[0],
                         "gif": rec[14:]}
            if pkt_ord == 5471:
                nxt = (struct.unpack("<Q", rec[1:9])[0],
                       struct.unpack("<I", rec[10:14])[0])
                break
    f.close()
    check("packet5470-found", found is not None)
    if found is None:
        print("RESULT FAIL"); return 1
    check("packet5470-tick", found["tick"] == 259, found["tick"])
    check("packet5470-epath", found["epath"] == 1, found["epath"])
    check("packet5470-size", found["size"] == 1696 and len(found["gif"]) == 1696)
    check("packet5470-recoff", found["off"] == 6673427 and found["len"] == 1710,
          (found["off"], found["len"]))
    check("packet5470-sha", hashlib.sha256(found["gif"]).hexdigest() == PKT_SHA)
    check("packet5470-fnv", fnv(found["gif"]) == 0xCC6DD8DF,
          hex(fnv(found["gif"])))
    check("neighbours", prev == (258, 1, 144) and nxt == (259, 144), (prev, nxt))

    # 3. sidecar corrected path
    with open(PATHS, "rb") as pf:
        pf.seek(0, 2)
        size = pf.tell()
        # line 5471 (1-based) holds index 5470
        pf.seek(0)
        for _ in range(5470):
            pf.readline()
        line = pf.readline().decode().strip()
    check("sidecar-5470-path3", line == "5470 3", line)
    _ = size

    # 4. packet144266 byte-identity via X5 offset
    xoff = None
    with open(X5) as xf:
        for ln in xf:
            if ln.startswith("144266,"):
                xoff = int(ln.split(",")[2])
    check("x5-offset", xoff == 158919448, xoff)
    if xoff is None:
        print("RESULT FAIL"); return 1
    with open(CAP, "rb") as cf:
        cf.seek(xoff)
        ln2 = struct.unpack("<I", cf.read(4))[0]
        rec2 = cf.read(ln2)
    d2 = rec2[14:]
    check("p144266-tick-size", struct.unpack("<Q", rec2[1:9])[0] == 950 and
          struct.unpack("<I", rec2[10:14])[0] == 1696)
    check("byte-identical-144266", hashlib.sha256(d2).hexdigest() == PKT_SHA)

    # 5. GIF walk: 6 tags, exact consumption, batch accounting
    tags, end = walk_gif(found["gif"])
    check("walk-exact", tags is not None and end == 1696, end)
    check("tag-count", tags is not None and len(tags) == 6, len(tags) if tags else None)
    if tags and len(tags) == 6:
        flgs = [(t["flg"], t["nloop"], t["regs"]) for t in tags]
        check("tag-shape", flgs[0] == (0, 11, [14]) and flgs[1] == (1, 1, [0, 1]) and
              flgs[2] == (1, 17, [3, 5, 3, 5]) and flgs[3] == (0, 16, [14]) and
              flgs[4] == (0, 36, [14]) and flgs[5] == (0, 2, [14]), flgs)
        check("no-image-tags", all(t["flg"] != 2 for t in tags))
        check("pre-clear", all(t["pre"] == 0 for t in tags))
        xyz2_t2 = sum(1 for p in tags[2]["payload"] if p[0] == 5)
        xyz2_t4 = sum(1 for p in tags[4]["payload"] if p[0] == 0x0E and (p[2] & 0xFF) == 5)
        check("batch-accounting-33", xyz2_t2 == 34 and xyz2_t4 == 32, (xyz2_t2, xyz2_t4))
        ad0 = {p[2] & 0xFF: p[1] for p in tags[0]["payload"]}
        check("tag0-frame", ad0.get(0x4C) == 0xFF00000001080070, hex(ad0.get(0x4C, 0)))
        check("tag0-tex0", ad0.get(0x06) == 0x0000000268020000, hex(ad0.get(0x06, 0)))
        prim = tags[1]["payload"][0][1]
        rgbaq = tags[1]["payload"][1][1]
        check("tag1-prim-rgbaq", prim == 0x11E and rgbaq == 0x3F80000080808080,
              (hex(prim), hex(rgbaq)))

        # 6. batch10 recomputation: vertices, rect, UV interp, taps, addresses
        g10 = tags[2]["payload"][40:44]
        check("batch10-regs", [p[0] for p in g10] == [3, 5, 3, 5])
        U0, X0r = g10[0][1] & 0x3FFF, g10[1][1] & 0xFFFF
        V0, Y0r = (g10[0][1] >> 16) & 0x3FFF, (g10[1][1] >> 16) & 0xFFFF
        U1, X1r = g10[2][1] & 0x3FFF, g10[3][1] & 0xFFFF
        V1, Y1r = (g10[2][1] >> 16) & 0x3FFF, (g10[3][1] >> 16) & 0xFFFF
        check("batch10-raw", (U0, V0, X0r, Y0r) == (5120, 8, 33784, 29176) and
              (U1, V1, X1r, Y1r) == (5632, 7160, 34296, 36328),
              ((U0, V0, X0r, Y0r), (U1, V1, X1r, Y1r)))
        OFX, OFY = 0x7000, 0x7200
        X0, Y0 = int(X0r / 16) - (OFX >> 4), int(Y0r / 16) - (OFY >> 4)
        X1, Y1 = int(X1r / 16) - (OFX >> 4), int(Y1r / 16) - (OFY >> 4)
        spX, spY = max(1, X1 - X0), max(1, Y1 - Y0)
        check("batch10-rect", (X0, Y0, X0 + spX - 1, Y0 + spY - 1) == (319, -1, 350, 445),
              (X0, Y0, spX, spY))
        u0f, v0f, u1f, v1f = (U0 >> 4), (V0 >> 4), (U1 >> 4), (V1 >> 4)
        x, y = 342, 377
        tU = u0f + (u1f - u0f) * (x - X0 + 0.5) / spX
        tV = v0f + (v1f - v0f) * (y - Y0 + 0.5) / spY
        check("interp-343.5-378.5", abs(tU - 343.5) < 1e-9 and abs(tV - 378.5) < 1e-9, (tU, tV))
        sU, sV = tU - 0.5, tV - 0.5
        iu, iv = math.floor(sU), math.floor(sV)
        check("taps-fx-fy-0", (iu, iv) == (343, 378) and (sU - iu, sV - iv) == (0.0, 0.0),
              ((iu, iv), (sU - iu, sV - iv)))
        check("tap0-addr", addr32(0, 8, 343, 378) == 0xBAE74, hex(addr32(0, 8, 343, 378)))
        check("dst-addr", addr32(112 << 5, 8, 342, 377) == 0x19AE38,
              hex(addr32(112 << 5, 8, 342, 377)))

    # 7. packet-table.tsv required fields (value or explicit UNKNOWN)
    req = {}
    with open(TABLE) as tf:
        for ln in tf:
            parts = ln.rstrip("\n").split("\t")
            if len(parts) == 4 and parts[0] not in ("section",):
                req[(parts[0], parts[1])] = parts[2]
    need = [("identity", "gif_sha256"), ("identity", "gif_fnv32"),
            ("batch", "batch10_v0"), ("computed", "tap0_addr"),
            ("computed", "texel_word_at_0x000bae74_tick259"),
            ("state", "FOG/FOGCOL/TEXCLUT/PRMODE"), ("verdict", "outcome")]
    missing = [k for k in need if k not in req or req[k] in ("", "UNKNOWN-UNSTATED")]
    check("table-fields", not missing, missing)
    check("table-marks-unknowns", "UNKNOWN" in req.get(("computed", "texel_word_at_0x000bae74_tick259"), ""),
          req.get(("computed", "texel_word_at_0x000bae74_tick259")))
    check("verdict-B-no-gpu-cause", req.get(("verdict", "outcome")) == "B", req.get(("verdict", "outcome")))

    print("RESULT " + ("ACCEPT" if not FAIL else "FAIL:" + ",".join(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
