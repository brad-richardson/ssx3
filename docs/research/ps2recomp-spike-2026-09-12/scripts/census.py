# write_file /tmp/ssx3vu/census.py
#!/usr/bin/env python3
"""Per-VU-program opcode census using the corrected (I-bit aware) decoder.
Programs = .DVP.overlay groups (flat VU micro-mem images)."""
import struct, sys, glob, os
from collections import Counter
sys.path.insert(0, '/tmp/ssx3vu')
from histogram import classify_pair

groups = {}
for path in sorted(glob.glob('/tmp/ssx3vu/sec*.bin')):
    base = os.path.basename(path)
    if '.DVP.overlay.' not in base:
        continue
    # group consecutive sections: split when a section starts at 0x0
    addr = base.split('..0x')[1].split('.')[0]
    groups.setdefault(path, addr)

# order by section number, split into programs at 0x0
paths = sorted(glob.glob('/tmp/ssx3vu/sec*.bin'))
progs, cur = [], []
for p in paths:
    b = os.path.basename(p)
    if '.DVP.overlay.' not in b:
        continue
    addr = '0x' + b.split('..0x')[1].split('.')[0]
    if addr == '0x0' and cur:
        progs.append(cur); cur = []
    cur.append((addr, p))
if cur: progs.append(cur)

INTEREST = {"L:XGKICK","L:XTOP","L:XITOP","U:CLIP","L:DIV","L:SQRT","L:RSQRT",
            "L:RNEXT","L:RGET","L:RINIT","L:RXOR","L:ESADD","L:ERSADD","L:ELENG",
            "L:ERLENG","L:EATANxy","L:EATANxz","L:ESUM","L:ERSQRT","L:ESQRT",
            "L:ESIN","L:ERCPR","L:EATAN","L:EEXP","L:WAITP","L:WAITQ","L:MFP",
            "L:ILWR","L:ISWR","L:MTIR","L:MFIR","L:LQD","L:SQD","L:LQI","L:SQI",
            "L:FCGET","L:B","L:BAL","L:JR","L:JALR","L:LOI-imm"}
for pi, prog in enumerate(progs):
    cnt = Counter(); res = []; ebits = 0; ninstr = 0
    size = 0
    for addr, p in prog:
        blob = open(p,'rb').read(); size += len(blob)
        for i in range(len(blob)//8):
            lo, hi = struct.unpack_from('<II', blob, i*8)
            ninstr += 1
            uok, utag, lok, ltag, ibit, ebit = classify_pair(hi, lo)
            ebits += ebit
            cnt[utag] += 1; cnt[ltag] += 1
            if not uok: res.append((addr, i, utag))
            if not lok: res.append((addr, i, ltag))
    print(f"--- Program {pi}: {len(prog)} sections, {size} bytes, {ninstr} instr, E-bits={ebits}, reserved={len(res)}")
    for r in res[:10]: print("    RESERVED:", r)
    print("    ops used:", len(cnt), "| VU1-only-ops:", {k: cnt[k] for k in INTEREST if cnt[k]})
    print("    top:", ", ".join(f"{c}x{t}" for t, c in cnt.most_common(12)))
