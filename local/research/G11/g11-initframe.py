#!/usr/bin/env python3
# G11: decode the dump's INITIAL VRAM through paraLLEl's own scanout math
# (sample_circuit.frag + swizzle_PS2 PSMCT32/24 path, coord mapping for
# force_progressive: phase=0 stride=1, DBX=DBY=0). DISPFB1: FBP=112 FBW=8
# PSM=1(PSMCT24). Frame 512x448. Read-only.
# Question: how many nonblack (RGB) pixels does the initial frame hold?
# ~0 -> presented(0)=black is pure one-vsync lag (initial buffer black).
# ~400+ icon -> #0 needs a second cause beyond the lag.
import struct, sys

PAGE_WL2, PAGE_HL2 = 6, 5
BLK_WL2, BLK_HL2 = 3, 3
COL_HL2 = 1
PAGE_BYTES = 8192
BLOCK_BYTES = 256
COL_BYTES = 64
BLOCKS_PER_PAGE = 32

def swizzle(x, y, base_pointer, page_stride, vram_mask):
    page_x = x >> PAGE_WL2
    page_y = y >> PAGE_HL2
    page_index = page_y * page_stride + page_x
    block_x = (x & 63) >> BLK_WL2
    block_y = (y & 31) >> BLK_HL2
    column_index = (y & 7) >> COL_HL2
    pixel_x = x & 7
    pixel_y = y & 1
    block_index = ((block_x & 1) | ((block_y & 1) << 1) | ((block_x & 2) << 1) |
                   ((block_y & 2) << 2) | ((block_x & 4) << 2)) + base_pointer
    pixel_index = ((pixel_x & 1) | ((pixel_y & 1) << 1) | ((pixel_x & 2) << 1) |
                   ((pixel_x & 4) << 1))
    return ((page_index * PAGE_BYTES + block_index * BLOCK_BYTES +
             column_index * COL_BYTES + pixel_index * 4) & vram_mask) >> 2

def main(path):
    b = open(path, 'rb').read()
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, 8)
    state_start = 44 + serial_sz + shot_sz
    vram_start = state_start + state_size - 84 - 4 * 1024 * 1024
    v = b[vram_start:vram_start + 4 * 1024 * 1024]
    mask = 4 * 1024 * 1024 - 1
    base = 112 * BLOCKS_PER_PAGE
    W, H = 512, 448
    nb = 0
    nbs = []
    for y in range(H):
        for x in range(W):
            w = struct.unpack_from('<I', v, swizzle(x, y, base, 8, mask) * 4)[0]
            if w & 0xffffff:
                nb += 1
                if len(nbs) < 10:
                    nbs.append((x, y, w))
    print(f"initial frame nonblack(RGB) pixels: {nb} / {W*H} ({nb/(W*H):.4f})")
    print("first nonblack samples (x,y,u32):", nbs)
    # where do scanned addresses fall? (sanity: distinct u32 addrs touched)
    addrs = set()
    for y in range(0, H, 7):
        for x in range(0, W, 7):
            addrs.add(swizzle(x, y, base, 8, mask))
    print(f"sampled distinct u32 addrs: {len(addrs)} (expect {(W//7+1)*(H//7+1)})")

if __name__ == '__main__':
    main(sys.argv[1])
