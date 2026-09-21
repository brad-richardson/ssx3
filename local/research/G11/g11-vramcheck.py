#!/usr/bin/env python3
# G11: VRAM cleared-pattern confirmation (read-only companion to g11-vram.py).
# Prints raw bytes at VRAM start + FBP112 base, byte histogram over the
# linear-equivalent frame span (pages 28..140), whole-VRAM top values,
# and the all-zero page list.
import struct
from collections import Counter

def main(path):
    b = open(path, 'rb').read()
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, 8)
    state_start = 44 + serial_sz + shot_sz
    vram_start = state_start + state_size - 84 - 4 * 1024 * 1024
    v = b[vram_start:vram_start + 4 * 1024 * 1024]
    print("first 32B of VRAM:", v[:32].hex(' '))
    print("32B @FBP112 (229376):", v[229376:229376 + 32].hex(' '))
    win = v[28 * 8192:141 * 8192]
    c = Counter(win)
    print(f"pages28..140: zeros={c[0]} 0x80={c[128]} other={len(win)-c[0]-c[128]}")
    c2 = Counter(v)
    print("whole-VRAM distinct byte values:", len(c2), "top:", c2.most_common(6))
    P = 8192
    zp = [p for p in range(512) if not any(v[p*P:(p+1)*P])]
    print(f"zero pages ({len(zp)}):", zp)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
