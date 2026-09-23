#!/usr/bin/env python3
"""E46 census + static-scan analysis.

Part A: for every missing-target (source,target,count) in /tmp/e46-census.txt,
report the containing CSV function, 8-byte alignment, and the jr-ra+delay
predecessor signature from the ELF.

Static pass: scan the ELF's alloc non-exec sections for 4-aligned words that
point into executable sections at a 4-aligned address A with jr-ra at A-8 and
A not already a CSV start. Report hits and the census intersection.

Usage: python3 e46_scan.py [--elf PATH] [--csv PATH] [--census PATH]
Writes tables to stdout; exits nonzero on internal error only.
"""
import struct
import sys

JR_RA = 0x03E00008

REG = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3",
       "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
       "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7",
       "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]


def dec(w, pc):
    """Tiny MIPS disassembler; returns short string (best effort)."""
    if w == 0:
        return "nop"
    op = (w >> 26) & 0x3F
    rs, rt = (w >> 21) & 31, (w >> 16) & 31
    rd, sa, fn = (w >> 11) & 31, (w >> 6) & 31, w & 0x3F
    imm = w & 0xFFFF
    simm = imm - 0x10000 if imm & 0x8000 else imm
    tgt = ((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
    if op == 0x00:
        S = {0x00: "sll", 0x02: "srl", 0x03: "sra", 0x08: "jr", 0x09: "jalr",
             0x0C: "syscall", 0x10: "mfhi", 0x12: "mflo", 0x18: "mult", 0x19: "multu",
             0x1A: "div", 0x1B: "divu", 0x20: "add", 0x21: "addu", 0x22: "sub",
             0x23: "subu", 0x24: "and", 0x25: "or", 0x26: "xor", 0x27: "nor",
             0x2A: "slt", 0x2B: "sltu"}
        m = S.get(fn, "special_%02x" % fn)
        if m == "jr":
            return "jr %s" % REG[rs]
        if m == "jalr":
            return "jalr %s,%s" % (REG[rd], REG[rs])
        if m in ("sll", "srl", "sra"):
            return "%s %s,%s,%d" % (m, REG[rd], REG[rt], sa)
        if m == "syscall":
            return "syscall"
        if m in ("mfhi", "mflo"):
            return "%s %s" % (m, REG[rd])
        if m in ("mult", "multu", "div", "divu"):
            return "%s %s,%s" % (m, REG[rs], REG[rt])
        return "%s %s,%s,%s" % (m, REG[rd], REG[rs], REG[rt])
    if op in (0x02, 0x03):
        return "%s 0x%x" % ("j" if op == 2 else "jal", tgt)
    B = {0x04: "beq", 0x05: "bne", 0x06: "blez", 0x07: "bgtz"}
    if op in B:
        return "%s %s,%s,0x%x" % (B[op], REG[rs], REG[rt], pc + 4 + (simm << 2))
    if op == 0x01:
        return "b%ccond %s,0x%x" % ("g" if (rt & 1) else "l", REG[rs], pc + 4 + (simm << 2))
    M = {0x08: "addi", 0x09: "addiu", 0x0C: "andi", 0x0D: "ori", 0x0E: "xori",
         0x0A: "slti", 0x0B: "sltiu", 0x0F: "lui",
         0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu", 0x27: "lwu",
         0x28: "sb", 0x29: "sh", 0x2B: "sw", 0x30: "ll", 0x38: "sc",
         0x1A: "ldl", 0x1B: "ldr", 0x2C: "sdl", 0x2D: "sdr",
         0x37: "ld", 0x3F: "sd", 0x1E: "lq", 0x3E: "sq"}
    if op in M:
        m = M[op]
        if m == "lui":
            return "lui %s,0x%x" % (REG[rt], imm)
        if m in ("addi", "addiu", "slti", "sltiu"):
            return "%s %s,%s,%d" % (m, REG[rt], REG[rs], simm)
        if m in ("andi", "ori", "xori"):
            if m == "or" and rs == 0:
                return "move %s,%s" % (REG[rt], REG[rt])
            return "%s %s,%s,0x%x" % (m, REG[rt], REG[rs], imm)
        return "%s %s,%d(%s)" % (m, REG[rt], simm, REG[rs])
    if op == 0x10:
        return "cop0_%08x" % w
    if op == 0x2F:
        return "cache 0x%x,%d(%s)" % (rt, simm, REG[rs])
    return "op%02x_%08x" % (op, w)


def load_elf(path):
    with open(path, "rb") as f:
        img = f.read()
    assert img[:4] == b"\x7fELF", "not an ELF"
    e_shoff, _, _, _, _, e_shentsize, e_shnum, _ = struct.unpack("<IIHHHHHH", img[32:52])
    secs = []
    for i in range(e_shnum):
        o = e_shoff + i * e_shentsize
        name, typ, flags, addr, off, size, link, info, align, entsz = struct.unpack("<IIIIIIIIII", img[o:o + 40])
        secs.append(dict(name=name, type=typ, flags=flags, addr=addr, off=off, size=size))
    # section names
    names = b""
    for s in secs:
        pass
    return img, secs


def sec_name(img, secs, idx):
    # find STRTAB section (type 3) that is the shstrtab: last STRTAB
    strtabs = [s for s in secs if s["type"] == 3 and s["addr"] == 0]
    if not strtabs:
        return "?"
    st = strtabs[-1]
    o = st["off"] + secs[idx]["name"]
    e = img.index(b"\x00", o)
    return img[o:e].decode("ascii", "replace")


def read_word(img, secs, addr):
    for s in secs:
        if s["type"] == 8:  # NOBITS
            continue
        if s["addr"] <= addr < s["addr"] + s["size"]:
            o = s["off"] + (addr - s["addr"])
            if o + 4 > len(img):
                return None
            return struct.unpack("<I", img[o:o + 4])[0]
    return None


def main():
    elf = "/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72"
    csv = "/Users/brad/dev/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv"
    census = "/tmp/e46-census.txt"
    for i, a in enumerate(sys.argv):
        if a == "--elf":
            elf = sys.argv[i + 1]
        if a == "--csv":
            csv = sys.argv[i + 1]
        if a == "--census":
            census = sys.argv[i + 1]
    img, secs = load_elf(elf)
    names = {i: sec_name(img, secs, i) for i in range(len(secs))}
    for i, s in enumerate(secs):
        s["secname"] = names[i]
    exec_secs = [s for s in secs if s["flags"] & 0x4 and s["type"] != 8 and s["size"] > 0]
    data_secs = [s for s in secs if not (s["flags"] & 0x4) and s["type"] != 8 and s["size"] > 0]
    data_secs = [s for s in data_secs if s["type"] == 1 and (s["flags"] & 0x2 or s["secname"] == ".rodata")]

    def in_exec(a):
        return any(s["addr"] <= a < s["addr"] + s["size"] for s in exec_secs)

    # CSV
    rows = []
    with open(csv) as f:
        hdr = f.readline()
        for line in f:
            p = line.strip().split(",")
            if len(p) < 4:
                continue
            rows.append((p[0], int(p[1], 0), int(p[2], 0)))
    starts = {r[1] for r in rows}

    def containing(a):
        best = None
        for r in rows:
            if r[1] <= a < r[2]:
                if best is None or r[1] > best[1]:
                    best = r
        return best

    # Part A census
    pairs = []  # (count, src, tgt)
    with open(census) as f:
        for line in f:
            p = line.split()
            if len(p) != 3:
                continue
            pairs.append((int(p[0]), int(p[1].split("=")[1], 0), int(p[2].split("=")[1], 0)))
    by_tgt = {}
    for c, s, t in pairs:
        by_tgt.setdefault(t, []).append((c, s))
    print("PART A CENSUS: %d pairs, %d distinct targets" % (len(pairs), len(by_tgt)))
    print("target,count,sources,csv_func,csv_range,align8,prev8,prev4,sig")
    for t in sorted(by_tgt, key=lambda t: -sum(c for c, _ in by_tgt[t])):
        tot = sum(c for c, _ in by_tgt[t])
        srcs = "+".join("0x%x(x%d)" % (s, c) for c, s in sorted(by_tgt[t], reverse=True))
        c = containing(t)
        cn = "%s [0x%x,0x%x)" % (c[0], c[1], c[2]) if c else "NONE(!)"
        a8 = "yes" if t % 8 == 0 else "no"
        p8 = read_word(img, secs, t - 8)
        p4 = read_word(img, secs, t - 4)
        w0 = read_word(img, secs, t)
        sig = "yes" if p8 == JR_RA else "no"
        print("0x%x,%d,%s,%s,%s,0x%08x[%s],0x%08x[%s],%s // @t: 0x%08x[%s]" % (
            t, tot, srcs, cn, a8,
            p8 if p8 is not None else 0, dec(p8, t - 8) if p8 is not None else "?",
            p4 if p4 is not None else 0, dec(p4, t - 4) if p4 is not None else "?",
            sig, w0 if w0 is not None else 0, dec(w0, t) if w0 is not None else "?"))

    # Static pass
    print("")
    print("STATIC PASS: data sections scanned: %s" % ",".join(
        "%s[0x%x+0x%x]" % (s["secname"], s["addr"], s["size"]) for s in data_secs))
    hits = {}  # A -> list of (secname, refaddr)
    nwords = 0
    for s in data_secs:
        base, size, off = s["addr"], s["size"], s["off"]
        for a in range(base, base + size, 4):
            if a % 4 != 0:
                continue
            o = off + (a - base)
            if o + 4 > len(img):
                continue
            nwords += 1
            v = struct.unpack("<I", img[o:o + 4])[0]
            if v % 4 != 0 or not in_exec(v):
                continue
            if v in starts:
                continue
            if read_word(img, secs, v - 8) != JR_RA:
                continue
            hits.setdefault(v, []).append((s["secname"], a))
    print("words scanned: %d, hits: %d" % (nwords, len(hits)))
    print("hit_A,refcount,refs,census?,csv_func,align8,@A,@A+4")
    for v in sorted(hits):
        refs = hits[v]
        inc = "CENSUS" if v in by_tgt else "-"
        c = containing(v)
        cn = "%s[0x%x,0x%x)" % (c[0], c[1], c[2]) if c else "NONE"
        w0 = read_word(img, secs, v)
        w1 = read_word(img, secs, v + 4)
        refstr = "+".join("%s:0x%x" % r for r in refs[:4]) + ("+%d" % (len(refs) - 4) if len(refs) > 4 else "")
        print("0x%x,%d,%s,%s,%s,%s,0x%08x[%s],0x%08x[%s]" % (
            v, len(refs), refstr, inc, cn, "yes" if v % 8 == 0 else "no",
            w0 if w0 is not None else 0, dec(w0, v) if w0 is not None else "?",
            w1 if w1 is not None else 0, dec(w1, v + 4) if w1 is not None else "?"))
    # census targets NOT hit by scan
    print("")
    print("census targets missed by static pass:")
    for t in sorted(by_tgt):
        if t not in hits:
            print("0x%x (count %d)" % (t, sum(c for c, _ in by_tgt[t])))


if __name__ == "__main__":
    main()
