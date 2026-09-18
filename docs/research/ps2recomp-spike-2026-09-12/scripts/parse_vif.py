# write_file /tmp/ssx3vu/parse_vif.py
#!/usr/bin/env python3
"""Parse .vutext as a VIF packet stream: find MPG uploads, histogram only the
true VU instruction words with the PS2Recomp decoder mirror from histogram.py.
"""
import struct, sys
sys.path.insert(0, '/tmp/ssx3vu')
from histogram import classify_upper, classify_lower

blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
words = struct.unpack(f'<{len(blob)//4}I', blob[:len(blob)//4*4])

VIF_CMD = {0x00:"NOP",0x01:"STCYCL",0x02:"OFFSET",0x03:"BASE",0x04:"ITOP",
  0x05:"STMOD",0x06:"MSKPATH3",0x07:"MARK",0x10:"FLUSHE",0x11:"FLUSH",
  0x13:"FLUSHA",0x14:"MSCAL",0x15:"MSCALF",0x17:"MSCNT",0x20:"STMASK",
  0x30:"STROW",0x31:"STCOL",0x4A:"MPG",0x50:"DIRECT",0x51:"DIRECTHL"}
def vifname(cmd):
    if cmd in VIF_CMD: return VIF_CMD[cmd]
    if 0x60 <= cmd <= 0x7F: return "UNPACK"
    return f"CMD{cmd:02x}"

# pass 1: list all VIFcode-like words (top byte is a known CMD) with context
print("=== MPG packets ===")
mpgs = []
for i,w in enumerate(words):
    if (w >> 24) == 0x4A:
        num = (w >> 16) & 0xFF
        imm = w & 0xFFFF
        nwords = num if num else 256
        mpgs.append((i, imm, nwords))
        print(f"word#{i} (off 0x{i*4:x}): MPG load_addr=0x{imm:04x} num={nwords} -> code bytes [{(i+1)*4}:{(i+1)*4+nwords*8}]")
print(f"\n{len(mpgs)} MPG packets")
print("\n=== MSCAL/F/CNT ===")
for i,w in enumerate(words):
    cmd = w >> 24
    if cmd in (0x14,0x15,0x17):
        print(f"word#{i}: {vifname(cmd)} exec_addr=0x{w & 0xFFFF:04x} immed_bit={(w>>23)&1}")

# pass 2: histogram VU code inside MPG payloads
from collections import Counter
cnt = Counter(); res = []
total = 0
for i, addr, nwords in mpgs:
    start = (i+1)*4
    for k in range(nwords):
        off = start + k*8
        if off+8 > len(blob): break
        lo, hi = struct.unpack_from('<II', blob, off)
        total += 1
        for ok, tag in (classify_upper(hi), classify_lower(lo)):
            if ok: cnt[tag] += 1
            else: res.append((f"mpg@{addr:04x}+{k}", f"{hi:08x}{lo:08x}", tag))
print(f"\n=== MPG payload: {total} half-instructions ===")
print(f"reserved hits: {len(res)}")
for loc, hexcode, tag in res[:40]:
    print(f"  {loc}: {hexcode} {tag}")
print("\n=== opcode usage inside MPG payloads (top 40) ===")
for tag, c in cnt.most_common(40):
    print(f"  {c:5d}  {tag}")
print(f"\n distinct implemented ops used: {len(cnt)}")
