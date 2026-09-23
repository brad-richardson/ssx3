#!/usr/bin/env python3
"""AU1: dump FUNC/OBJECT symbols from an ELF32-LE symtab (IRX or EE ELF).
Usage: au1_elfsyms.py <elf> [grep-regex]"""
import re, struct, sys
b = open(sys.argv[1], "rb").read(); pat = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
shoff, = struct.unpack_from("<I", b, 32); shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 46)
secs = [struct.unpack_from("<10I", b, shoff + i * shentsize) for i in range(shnum)]
rows = []
for s in secs:
    if s[1] != 2: continue  # SHT_SYMTAB
    strs = secs[s[6]]; so = strs[4]
    for i in range(s[5] // 16):
        nm, val, size, info, oth, shn = struct.unpack_from("<IIIBBH", b, s[4] + 16 * i)
        name = b[so + nm: b.index(b"\0", so + nm)].decode("latin1")
        typ = info & 15
        if typ in (1, 2) and name: rows.append((val, size, "FUNC" if typ == 2 else "OBJ", name))
rows.sort()
f = [r for r in rows if r[2] == "FUNC"]
print(f"# {sys.argv[1].split('/')[-1]}: {len(f)} FUNC, {len(rows)-len(f)} OBJ symbols; FUNC bytes {sum(r[1] for r in f)}")
for v, sz, t, n in rows:
    if pat is None or pat.search(n): print(f"{v:#010x} {sz:6d} {t} {n}")
