#!/usr/bin/env python3
"""E46 Part-2 rescan (orchestrator follow-up).

Relaxed static pass: data-section words pointing at INTERIOR addresses of
CSV functions (not a start), 8-aligned, preceded within 3 words by jr ra
plus nop padding (word[A-12] == jr ra and word[A-4] == nop — the shape all
18 census targets share). Cross-checks the census. Report-only: no entries
are added from the hits without a boot.
"""
import struct
import sys

JR_RA = 0x03E00008


def main():
    sys.path.insert(0, 'local/research/E46')
    from e46_scan import load_elf, sec_name, read_word
    elf = "/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72"
    csv = "/Users/brad/dev/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv"
    img, secs = load_elf(elf)
    for i, s in enumerate(secs):
        s["secname"] = sec_name(img, secs, i)
    exec_secs = [s for s in secs if s["flags"] & 0x4 and s["type"] != 8 and s["size"] > 0]
    data_secs = [s for s in secs if not (s["flags"] & 0x4) and s["type"] != 8 and s["size"] > 0]
    data_secs = [s for s in data_secs if s["type"] == 1 and (s["flags"] & 0x2 or s["secname"] == ".rodata")]

    def in_exec(a):
        return any(s["addr"] <= a < s["addr"] + s["size"] for s in exec_secs)

    rows = []
    with open(csv) as f:
        f.readline()
        for line in f:
            p = line.strip().split(",")
            if len(p) >= 4:
                rows.append((p[0], int(p[1], 0), int(p[2], 0)))
    starts = {r[1] for r in rows}

    def containing(a):
        best = None
        for r in rows:
            if r[1] <= a < r[2]:
                if best is None or r[1] > best[1]:
                    best = r
        return best

    census = {0x396b40, 0x140bc0, 0x38f7f8, 0x375a00, 0x3968c8, 0x30db90,
              0x26a0b8, 0x3b1140, 0x144928, 0x14e130, 0x26a068, 0x284b50,
              0x155380, 0x2849b8, 0x284940, 0x153258, 0x1566e8, 0x153200,
              0x32f8b0}
    hits = {}
    nwords = 0
    for s in data_secs:
        base, size, off = s["addr"], s["size"], s["off"]
        for a in range(base, base + size, 4):
            o = off + (a - base)
            if o + 4 > len(img):
                continue
            nwords += 1
            v = struct.unpack("<I", img[o:o + 4])[0]
            if v % 8 != 0 or not in_exec(v) or v in starts:
                continue
            c = containing(v)
            if c is None or not (c[1] < v < c[2]):
                continue
            if read_word(img, secs, v - 12) != JR_RA:
                continue
            if read_word(img, secs, v - 4) != 0:
                continue
            hits.setdefault(v, []).append((s["secname"], a))
    print("words scanned: %d, relaxed hits: %d" % (nwords, len(hits)))
    print("hit_A,refcount,refs,census?,csv_func,@A")
    for v in sorted(hits):
        refs = hits[v]
        inc = "CENSUS" if v in census else "-"
        c = containing(v)
        w0 = read_word(img, secs, v)
        refstr = "+".join("%s:0x%x" % r for r in refs[:4])
        if len(refs) > 4:
            refstr += "+%d" % (len(refs) - 4)
        print("0x%x,%d,%s,%s,%s[0x%x,0x%x),0x%08x" % (
            v, len(refs), refstr, inc, c[0], c[1], c[2], w0 if w0 is not None else 0))
    print("census recall: %d/%d" % (sum(1 for t in census if t in hits), len(census)))
    print("census missed: %s" % " ".join("0x%x" % t for t in sorted(census) if t not in hits))


if __name__ == "__main__":
    main()
