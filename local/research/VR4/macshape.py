#!/usr/bin/env python3
"""VR4: static shape of a block function in Mac clang -S output vs Odin objdump."""
import re, sys
def mac(path, blk):
    lines = open(path).read().split('\n'); ops = []
    pat = re.compile(r'^__ZN14VU1RecompImageILy\d+EE5%sER14VU1InterpreterRNS1_10RunContextE:' % blk)
    i = next(k for k, l in enumerate(lines) if pat.match(l))
    for l in lines[i + 1:]:
        if l.startswith('\t.cfi_endproc'): break
        if l.startswith('\t') and not l.startswith(('\t.', '\t;')): ops.append(l.split()[0])
    return ops
def odin(path):
    return [m.group(1) for m in (re.match(r'\s*[0-9a-f]+:\s+(\S+)', l) for l in open(path)) if m]
for img, blk, od in [('f587398bb6fc4651', 'B2a10', 'odin-f587-B2a10.s'), ('a56458ed3544b351', 'B0628', 'odin-a564-B0628.s'), ('f587398bb6fc4651', 'B0a58', 'odin-f587-B0a58.s')]:
    for host, ops in (('mac', mac(f'mac-{img}.s', blk)), ('odin', odin(od))):
        c = lambda k: sum(1 for o in ops if o == k)
        print(f'{blk} {host:4s} insns {len(ops):5d} ubfx {c("ubfx"):4d} fcvt {c("fcvt"):4d} fcmp {c("fcmp"):4d} bl {c("bl"):3d} cbz+cbnz {c("cbz")+c("cbnz"):4d}')
