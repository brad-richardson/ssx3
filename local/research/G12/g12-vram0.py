#!/usr/bin/env python3
"""G12: dump-VRAM census at the sprite buffer (block 0) + full-page histogram.

Reuses G11 g11-vram.py layout (state tail: VRAM 4MiB + 84 B). Read-only.
Question: does the dump's initial VRAM at block 0 contain sprite pixels
(nonzero/non-cleared) or the cleared pattern (00 00 00 80 repeating)?
Decides between initial-VRAM asymmetry (A) and present-path shift (B).
"""
import struct
import sys


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def main(path):
    b = open(path, 'rb').read()
    o = 8
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o)
    o += 36
    state_start = o + serial_sz + shot_sz
    state_end = state_start + state_size
    assert state_size == 4194813, state_size
    vram_end = state_end - 84
    vram_start = vram_end - 4 * 1024 * 1024
    v = b[vram_start:vram_end]
    print(f"VRAM len={len(v)}")
    print(f"VRAM[0:64] = {v[0:64].hex()}")
    # cleared-pattern census: words equal to 0x80000000 vs 0 vs other
    import collections
    words = struct.unpack('<%dI' % (len(v) // 4), v)
    c = collections.Counter(words)
    print(f"distinct u32 words: {len(c)}")
    print("top 5 words:", c.most_common(5))
    # per-8KiB-page nonzero-byte census (full)
    P = 8192
    pages = len(v) // P
    nzpages = []
    for p in range(pages):
        n = sum(1 for x in v[p * P:(p + 1) * P] if x)
        if n:
            nzpages.append((p, n))
    print(f"nonzero 8KiB pages: {len(nzpages)} / {pages}")
    print("pages:", nzpages)
    # fine census: first 32KiB in 2KiB units (FBP units), count non-cleared words
    print("first 16 x 2KiB units (non-0x80000000 words / 512):")
    for u in range(16):
        seg = words[u * 512:(u + 1) * 512]
        nc = sum(1 for w in seg if w != 0x80000000)
        print(f"  unit {u}: {nc}")
    # atlas region: TBP0=3584 blocks = byte 3584*256 = 917504 (PCSX2 units);
    # also paraLLEl-style 3584*2048 mod 4MiB for comparison
    for off in (3584 * 256, (3584 * 2048) % (4 * 1024 * 1024)):
        seg = v[off:off + 8192]
        print(f"8KiB @byte {off}: nonzero={sum(1 for x in seg if x)} head={seg[:32].hex()}")


if __name__ == '__main__':
    main(sys.argv[1])
