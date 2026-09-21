#!/usr/bin/env python3
# G11: dump-VRAM zero-check at the scanned buffer (read-only).
# Layout (G8 §2d, verified): file = 8 + 36 + serial + shot + state(4194813)
# + regs(8192) + packets. State tail (paraLLEl restart() order): VRAM 4MiB,
# then 4x GIF path (16B tag + u32 reg) + f32 internal_q = 84 B.
# So VRAM = state_end-84-4MiB .. state_end-84. DISPFB1 FBP=112, PSM=1:
# FBP unit = 2048 B -> base offset 112*2048 = 229376 = page 28 (8KiB pages).
# Question: is the scanned region zero in the dump's initial VRAM?
# If yes -> presented(0)=black is consistent with pure one-vsync lag.
# If no  -> #0 needs a second cause (init artifact) on top of the lag.
import struct, sys, hashlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def main(path):
    b = open(path, 'rb').read()
    print(f"size={len(b)} sha256={hashlib.sha256(b).hexdigest()[:16]}")
    o = 8
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o); o += 36
    state_start = o + serial_sz + shot_sz
    state_end = state_start + state_size
    print(f"version={ver} state_size={state_size} state=[{state_start},{state_end})")
    assert state_size == 4194813, state_size
    vram_end = state_end - 84
    vram_start = vram_end - 4 * 1024 * 1024
    print(f"VRAM=[{vram_start},{vram_end}) len={vram_end - vram_start}")
    v = b[vram_start:vram_end]
    # whole-VRAM census
    nz = sum(1 for x in v if x)
    print(f"VRAM nonzero bytes: {nz} / {len(v)} ({nz/len(v):.4f})")
    # per-8KiB-page nonzero census around FBP=112 (page 28)
    P = 8192
    pages = len(v) // P
    nzpages = []
    for p in range(pages):
        c = sum(1 for x in v[p*P:(p+1)*P] if x)
        if c:
            nzpages.append((p, c))
    print(f"nonzero 8KiB pages: {len(nzpages)} / {pages}")
    print("first 20:", nzpages[:20])
    # window around page 28
    print("pages 24..40:", [(p, sum(1 for x in v[p*P:(p+1)*P] if x)) for p in range(24, 41)])
    # FBP base offsets for a few interpretations (bytes from VRAM start)
    for fbp_off in (112 * 2048, 112 * 8192 // 4):
        seg = v[fbp_off:fbp_off + 8192]
        print(f"8KiB @FBP112-offset {fbp_off}: nonzero={sum(1 for x in seg if x)}")
    # GIF-path tail sanity: 4x (16B + u32) then f32
    tail = b[vram_end:state_end]
    print(f"tail bytes: {tail.hex()[:64]}...")

if __name__ == '__main__':
    main(sys.argv[1])
