#!/usr/bin/env python3
"""AU2: walk an EE->IOP SND tag buffer dump (SNDIOP_processtagbuf layout:
u32 tag; tag 0/5 = 12 more bytes; 1 mix, 2 maincpufx, 3 updatevoices,
4 parsedts carry {u32 len, payload}; 6 = end). Prints records; the length
rule for tags 1-4 is inferred from the dumps (u32 byte length after tag)."""
import struct, sys
b = open(sys.argv[1], "rb").read(); o = 0
while o + 4 <= len(b):
    tag = struct.unpack_from("<I", b, o)[0]
    if tag in (0, 5):
        print(f"{o:#06x} tag {tag} skip {[hex(x) for x in struct.unpack_from('<3I', b, o + 4)]}"); o += 16; continue
    if tag == 6:
        print(f"{o:#06x} tag 6 end"); break
    if tag in (1, 2, 3, 4):
        ln = struct.unpack_from("<I", b, o + 4)[0]
        body = b[o + 8:o + 8 + ln]
        nz = sum(1 for x in body if x)
        print(f"{o:#06x} tag {tag} len {ln:#x} nonzero {nz} head {body[:32].hex(' ')}")
        o += 8 + ln; continue
    print(f"{o:#06x} unknown word {tag:#x}; stop"); break
