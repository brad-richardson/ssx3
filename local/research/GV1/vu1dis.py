#!/usr/bin/env python3
"""GV1: minimal VU1 disassembler/classifier over the generated recomp images.

Reads the (lower, upper) words each image embeds as `static constexpr D dXXXX{lower, upper, ...}`
and the E/I bits from the upper word. Opcode tables follow the VU ISA (PCSX2 VUops tables).
"""
import re, sys

BC = "xyzw"
UPPER = {}
for i, b in enumerate(BC):
    UPPER[0x00 + i] = f"ADD{b}"; UPPER[0x04 + i] = f"SUB{b}"; UPPER[0x08 + i] = f"MADD{b}"
    UPPER[0x0C + i] = f"MSUB{b}"; UPPER[0x10 + i] = f"MAX{b}"; UPPER[0x14 + i] = f"MINI{b}"
    UPPER[0x18 + i] = f"MUL{b}"
UPPER.update({0x1C: "MULq", 0x1D: "MAXi", 0x1E: "MULi", 0x1F: "MINIi", 0x20: "ADDq", 0x21: "MADDq",
              0x22: "ADDi", 0x23: "MADDi", 0x24: "SUBq", 0x25: "MSUBq", 0x26: "SUBi", 0x27: "MSUBi",
              0x28: "ADD", 0x29: "MADD", 0x2A: "MUL", 0x2B: "MAX", 0x2C: "SUB", 0x2D: "MSUB",
              0x2E: "OPMSUB", 0x2F: "MINI"})
UPPER_T3 = {}
for i, b in enumerate(BC):
    UPPER_T3[0x00 + i] = f"ADDA{b}"; UPPER_T3[0x04 + i] = f"SUBA{b}"; UPPER_T3[0x08 + i] = f"MADDA{b}"
    UPPER_T3[0x0C + i] = f"MSUBA{b}"; UPPER_T3[0x18 + i] = f"MULA{b}"
UPPER_T3.update({0x10: "ITOF0", 0x11: "ITOF4", 0x12: "ITOF12", 0x13: "ITOF15", 0x14: "FTOI0",
                 0x15: "FTOI4", 0x16: "FTOI12", 0x17: "FTOI15", 0x1C: "MULAq", 0x1D: "ABS",
                 0x1E: "MULAi", 0x1F: "CLIP", 0x20: "ADDAq", 0x21: "MADDAq", 0x22: "ADDAi",
                 0x23: "MADDAi", 0x24: "SUBAq", 0x25: "MSUBAq", 0x26: "SUBAi", 0x27: "MSUBAi",
                 0x28: "ADDA", 0x29: "MADDA", 0x2A: "MULA", 0x2C: "SUBA", 0x2D: "MSUBA",
                 0x2E: "OPMULA", 0x2F: "NOP"})

LOWER = {0x00: "LQ", 0x01: "SQ", 0x04: "ILW", 0x05: "ISW", 0x08: "IADDIU", 0x09: "ISUBIU",
         0x10: "FCEQ", 0x11: "FCSET", 0x12: "FCAND", 0x13: "FCOR", 0x14: "FSEQ", 0x15: "FSSET",
         0x16: "FSAND", 0x17: "FSOR", 0x18: "FMEQ", 0x1A: "FMAND", 0x1B: "FMOR", 0x1C: "FCGET",
         0x20: "B", 0x21: "BAL", 0x24: "JR", 0x25: "JALR", 0x28: "IBEQ", 0x29: "IBNE",
         0x2C: "IBLTZ", 0x2D: "IBGTZ", 0x2E: "IBLEZ", 0x2F: "IBGEZ"}
LOWER40 = {0x30: "IADD", 0x31: "ISUB", 0x32: "IADDI", 0x34: "IAND", 0x35: "IOR"}
T3 = {
    0: {12: "MOVE", 13: "LQI", 14: "DIV", 15: "MTIR", 16: "RNEXT", 25: "MFP", 26: "XTOP",
        27: "XGKICK", 28: "ESADD", 29: "EATANxy", 30: "ESQRT", 31: "ESIN"},
    1: {12: "MR32", 13: "SQI", 14: "SQRT", 15: "MFIR", 16: "RGET", 26: "XITOP", 28: "ERSADD",
        29: "EATANxz", 30: "ERSQRT", 31: "EATAN"},
    2: {13: "LQD", 14: "RSQRT", 15: "ILWR", 16: "RINIT", 28: "ELENG", 29: "ESUM", 30: "ERCPR",
        31: "EEXP"},
    3: {13: "SQD", 14: "WAITQ", 15: "ISWR", 16: "RXOR", 28: "ERLENG", 30: "WAITP"},
}

BRANCHES = {"B", "BAL", "JR", "JALR", "IBEQ", "IBNE", "IBLTZ", "IBGTZ", "IBLEZ", "IBGEZ"}
CLASS = {}
for m in ("LQ", "SQ", "LQI", "SQI", "LQD", "SQD"): CLASS[m] = "vf-mem"
for m in ("ILW", "ISW", "ILWR", "ISWR"): CLASS[m] = "vi-mem"
for m in ("IADD", "ISUB", "IADDI", "IAND", "IOR", "IADDIU", "ISUBIU", "MFIR", "MTIR"): CLASS[m] = "ialu"
for m in ("FCEQ", "FCSET", "FCAND", "FCOR", "FSEQ", "FSSET", "FSAND", "FSOR", "FMEQ", "FMAND",
          "FMOR", "FCGET"): CLASS[m] = "flag"
for m in BRANCHES: CLASS[m] = "branch"
for m in ("DIV", "SQRT", "RSQRT", "WAITQ"): CLASS[m] = "fdiv"
for m in ("ESADD", "ERSADD", "ELENG", "ERLENG", "EATANxy", "EATANxz", "ESUM", "ESQRT", "ERSQRT",
          "ERCPR", "ESIN", "EATAN", "EEXP", "MFP", "WAITP"): CLASS[m] = "efu"
for m in ("XGKICK", "XTOP", "XITOP"): CLASS[m] = "gif/top"
for m in ("RNEXT", "RGET", "RINIT", "RXOR"): CLASS[m] = "random"
for m in ("MOVE", "MR32"): CLASS[m] = "move"


def upper_name(u):
    op = u & 0x3F
    if op >= 0x3C:
        return UPPER_T3.get((((u >> 6) & 0x1F) << 2) | (u & 3), f"U?{u:08x}")
    return UPPER.get(op, f"U?{u:08x}")


def lower_name(l):
    op = (l >> 25) & 0x7F
    if op == 0x40:
        f = l & 0x3F
        if f >= 0x3C:
            return T3[f & 3].get((l >> 6) & 0x1F, f"L?{l:08x}")
        return LOWER40.get(f, f"L?{l:08x}")
    return LOWER.get(op, f"L?{l:08x}")


def dest(w):
    d = (w >> 21) & 0xF
    return "".join(c for c, bit in zip("xyzw", (8, 4, 2, 1)) if d & bit)


def upper_class(m):
    if m == "NOP": return "nop"
    if m.startswith(("ITOF", "FTOI")): return "conv"
    if m in ("CLIP",): return "clip"
    if m.startswith(("MAX", "MINI", "ABS")): return "minmax/abs"
    return "fmac"


def fmt_upper(u):
    m = upper_name(u)
    if m == "NOP": return "NOP"
    ft, fs, fd = (u >> 16) & 31, (u >> 11) & 31, (u >> 6) & 31
    return f"{m}.{dest(u)} fd{fd},fs{fs},ft{ft}"


def branch_target(pc, l):
    imm = l & 0x7FF
    if imm & 0x400: imm -= 0x800
    return (pc + 8 + imm * 8) & 0x3FFF


def fmt_lower(pc, l, ibit):
    if ibit:
        import struct
        return f"LOI {struct.unpack('<f', struct.pack('<I', l))[0]:g}"
    m = lower_name(l)
    it, is_ = (l >> 16) & 31, (l >> 11) & 31
    if m in BRANCHES and m not in ("JR", "JALR"):
        return f"{m} vi{it},vi{is_} -> {branch_target(pc, l):04x}"
    if m == "MOVE" and l == 0x8000033C: return "NOP"
    return f"{m}.{dest(l)} t{it},s{is_}"


PAIR_RE = re.compile(r"static constexpr D d([0-9a-f]{4})\{0x([0-9a-f]{8})u, 0x([0-9a-f]{8})u")


def load_image(path):
    pairs = {}
    with open(path) as f:
        for line in f:
            m = PAIR_RE.search(line)
            if m:
                pairs[int(m.group(1), 16)] = (int(m.group(2), 16), int(m.group(3), 16))
    return pairs


if __name__ == "__main__":
    img = load_image(sys.argv[1])
    lo, hi = (int(x, 16) for x in sys.argv[2:4]) if len(sys.argv) > 3 else (0, 0x4000)
    for pc in range(lo, hi, 8):
        l, u = img[pc]
        ib, eb = bool(u >> 31 & 1), bool(u >> 30 & 1)
        flags = ("I" if ib else "") + ("E" if eb else "") + ("M" if u >> 29 & 1 else "") + \
                ("D" if u >> 28 & 1 else "") + ("T" if u >> 27 & 1 else "")
        print(f"{pc:04x} {flags:3} {fmt_upper(u):30} | {fmt_lower(pc, l, ib)}")
