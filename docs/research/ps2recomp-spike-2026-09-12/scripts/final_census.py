# write_file /tmp/ssx3vu/final_census.py
#!/usr/bin/env python3
"""Final census: all 32 MPG payloads in .vutext (= the 7 real VU programs),
decoded with the I-bit-aware mirror of PS2Recomp's VU1Interpreter."""
import struct, sys
from collections import Counter
sys.path.insert(0, '/tmp/ssx3vu')
from histogram import classify_pair

blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
words = struct.unpack(f'<{len(blob)//4}I', blob)

mpgs = [(i, w & 0xFFFF, ((w >> 16) & 0xFF) or 256)
        for i, w in enumerate(words) if (w >> 24) == 0x4A]
print(f"{len(mpgs)} MPG packets")

# group into programs: new program when load_addr == 0
progs, cur = [], []
for i, addr, num in mpgs:
    if addr == 0 and cur:
        progs.append(cur); cur = []
    cur.append((i, addr, num))
if cur: progs.append(cur)
print(f"{len(progs)} programs\n")

grand_res = []
for pi, prog in enumerate(progs):
    cnt = Counter(); res = []; ebits = loi = ninstr = 0
    size = sum(n * 8 for _, _, n in prog)
    for i, addr, num in prog:
        for k in range(num):
            off = (i + 1) * 4 + k * 8
            lo, hi = struct.unpack_from('<II', blob, off)
            ninstr += 1
            uok, utag, lok, ltag, ibit, ebit = classify_pair(hi, lo)
            loi += ibit; ebits += ebit
            cnt[utag] += 1; cnt[ltag] += 1
            if not uok: res.append((f"{addr:04x}+{k}", f"{hi:08x}{lo:08x}", utag))
            if not lok: res.append((f"{addr:04x}+{k}", f"{hi:08x}{lo:08x}", ltag))
    grand_res += [(pi,) + r for r in res]
    print(f"Program {pi}: {ninstr} instr ({size} B), E-bits={ebits}, LOI={loi}, reserved={len(res)}")
    for r in res[:8]: print("    RESERVED:", r)
    print(f"    distinct ops: {len(cnt)}")

print(f"\nTOTAL programs={len(progs)} reserved hits={len(grand_res)}")
for r in grand_res[:20]: print("  ", r)

# combined op usage
cnt = Counter()
for i, addr, num in mpgs:
    for k in range(num):
        off = (i + 1) * 4 + k * 8
        lo, hi = struct.unpack_from('<II', blob, off)
        uok, utag, lok, ltag, ibit, ebit = classify_pair(hi, lo)
        cnt[utag] += 1; cnt[ltag] += 1
print(f"\nCombined distinct ops: {len(cnt)}")
vu1only = ["L:XGKICK","L:XTOP","L:XITOP","U:CLIP","L:DIV","L:SQRT","L:RSQRT",
           "L:RNEXT","L:RGET","L:RINIT","L:RXOR","L:ESADD","L:ERSADD","L:ELENG",
           "L:ERLENG","L:EATANxy","L:EATANxz","L:ESUM","L:ERSQRT","L:ESQRT",
           "L:ESIN","L:ERCPR","L:EATAN","L:EEXP","L:WAITP","L:WAITQ","L:MFP",
           "L:ILWR","L:ISWR"]
print("VU1-specialty ops present:", {k: cnt[k] for k in vu1only if cnt[k]})
print("\nFull usage:")
for tag, c in cnt.most_common(): print(f"  {c:5d}  {tag}")
