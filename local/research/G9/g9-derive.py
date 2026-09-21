#!/usr/bin/env python3
# G9 Task 1: derive expected scanout widths from the dump's own PrivRegs.
# Two independent chains, both evaluated from regs0 bytes:
#  (A) PCSX2: SetRects -> GetResolution -> upscale -> SaveSnapshotToMemory aspect
#  (B) replayer: vsync() NTSC branch -> adapt_to_internal_horizontal_resolution
# Source refs: GSState.cpp SetRects/GetResolution/VideoMode* tables,
# GSRenderer.cpp SaveSnapshotToMemory/CalculateDrawSrcRect, gs_renderer.cpp vsync().
import struct, sys, math

def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]
def f32(x): return struct.unpack('f', struct.pack('f', x))[0]
def bits(v, lo, w): return (v >> lo) & ((1 << w) - 1)

OFF = {'PMODE': 0x00, 'SMODE1': 0x10, 'SMODE2': 0x20, 'DISPFB1': 0x70,
       'DISPLAY1': 0x80, 'DISPFB2': 0x90, 'DISPLAY2': 0xA0}

def regs0_of(path):
    b = open(path, 'rb').read()
    o = 8
    (ver, state_size, s_off, s_sz, crc, sw, sh, sh_off, sh_sz) = struct.unpack_from('<9I', b, o)
    o += 36 + s_sz + sh_sz + state_size
    return bytes(b[o:o+8192])

def main(path, obs_png_wh, obs_ppm_wh):
    r = regs0_of(path)
    pmode = u64(r, OFF['PMODE']); smode1 = u64(r, OFF['SMODE1']); smode2 = u64(r, OFF['SMODE2'])
    EN1, EN2 = bits(pmode,0,1), bits(pmode,1,1)
    CMOD, LC = bits(smode1,13,2), bits(smode1,3,7)
    INT, FFMD = bits(smode2,0,1), bits(smode2,1,1)
    d1 = u64(r, OFF['DISPLAY1']); f1 = u64(r, OFF['DISPFB1'])
    d2 = u64(r, OFF['DISPLAY2']); f2 = u64(r, OFF['DISPFB2'])
    DX, DY, MAGH, MAGV, DW, DH = (bits(d1,0,12), bits(d1,12,11), bits(d1,23,4),
                                  bits(d1,27,2), bits(d1,32,12), bits(d1,44,11))
    FBW1 = bits(f1,9,6)
    print(f"regs: PMODE=0x{pmode:08x}(EN1={EN1} EN2={EN2}) SMODE1=0x{smode1:08x}(CMOD={CMOD} LC={LC}) "
          f"SMODE2=0x{smode2:x}(INT={INT} FFMD={FFMD})")
    print(f"regs: DISPLAY1=0x{d1:016x} DX={DX} DY={DY} MAGH={MAGH} MAGV={MAGV} DW={DW} DH={DH}  DISPFB1.FBW={FBW1}")
    print("--- (A) PCSX2 chain ---")
    # GetVideoMode: CMOD 2 -> NTSC -> videomode idx 0 (GSState.cpp:854-855, GS.h:26)
    assert (CMOD, LC) == (2, 32), "only NTSC/ANALOG handled"
    vm_off, vm_div = (640, 224, 642, 25), (3, 0, 2559, 239)
    print(f"videomode=NTSC idx0 offsets={vm_off} dividers={vm_div}")
    # SetRects circuit 0 (GSState.cpp:7312); circuit2 all-zero/FBW==0 -> disabled
    c2dis = (bits(f2,9,6) == 0 and bits(d2,32,12) == 0 and bits(d2,44,11) == 0 and bits(d2,23,4) == 0)
    magx, magy = MAGH + 1, MAGV + 1
    DW1, DH1 = DW + 1, DH + 1
    renderW, renderH = DW1 // magx, DH1 // magy
    # PCRTCOffsets=false (default; not in ini) -> min() branch
    finalW = min(renderW, DW1 // (vm_div[0] + 1))
    finalH = min(renderH, DH1 // (vm_div[1] + 1))
    print(f"mag=({magx},{magy}) DW+1={DW1} DH+1={DH1} render={renderW}x{renderH} "
          f"DW//4={DW1//(vm_div[0]+1)} DH//1={DH1//(vm_div[1]+1)} finalDisplay={finalW}x{finalH} c2_disabled={c2dis}")
    # GetResolution (GSState.cpp:7172): interlaced=INT&&analogue; full height
    interlaced = INT and True
    full_h = bool(interlaced)
    if EN1 and not EN2:
        res = (finalW, finalH)
    elif not EN1 and not EN2:
        res = (vm_off[0], vm_off[1] << (1 if full_h else 0))
    else:
        res = (None, None)
    res = (min(res[0], vm_off[0]), min(res[1], (vm_off[1] << 1) if full_h else vm_off[1]))
    print(f"interlaced={interlaced} full_h={full_h} GetResolution={res[0]}x{res[1]}")
    # fs = res * UpscaleMultiplier(1.0 default) -> m_real_size == current texture
    fs = (int(res[0] * 1.0), int(res[1] * 1.0))
    print(f"upscale=1.0 -> m_real_size/current={fs[0]}x{fs[1]}  crop=0 (ini) -> src_rect=full texture")
    # SaveSnapshotToMemory(0,0,aspect_correct=True,crop=True): Auto 4:3/3:2, non-progressive -> 4/3
    aspect = f32(f32(4.0) / f32(3.0))
    tex_aspect = fs[0] / fs[1]
    if tex_aspect >= aspect:
        dw, dh = f32(float(fs[0])), f32(float(fs[0]) / aspect)
    else:
        dw, dh = f32(float(fs[1]) * aspect), f32(float(fs[1]))
    pred_png = (int(dw), int(dh))
    print(f"aspect={aspect:.7f} tex_aspect={tex_aspect:.4f} branch={'width-driven' if tex_aspect>=aspect else 'height-driven'} "
          f"draw=({dw:.4f},{dh:.4f}) -> PNG predict={pred_png[0]}x{pred_png[1]} observed={obs_png_wh} "
          f"{'MATCH' if pred_png == obs_png_wh else 'MISMATCH'}")
    print("--- (B) replayer chain (defaults) ---")
    # NTSC non-overscan (gs_renderer.cpp:4334): 640x224 off(159,25); force_progressive -> x448
    mw, mh = 640, 224 * 2
    clk = 4  # CLOCK_DIVIDER_COMPOSITE
    print(f"mode_base={mw}x{mh} clock_div={clk} force_progressive=1 anti_blur=1 adapt=1")
    if EN1:
        cw = DW1 // magx
        ch = (DH1 + 1) & ~1
        print(f"circuit1=({cw}x{ch}) circuit2=none")
        # adapt: h0=cw h1=0->cw equal -> scaling=clk/magh
        scaling = f32(float(clk) / float(magx))
        mw2 = int(math.floor(f32(float(mw) * scaling) + 0.5))
        print(f"scaling={scaling:.7f} mode={mw}->{mw2} (round)")
        mw = mw2
    else:
        print("no circuits enabled -> no adapt scaling")
    pred_ppm = (mw, mh)
    print(f"internal=mode={pred_ppm[0]}x{pred_ppm[1]} hi-res=off -> PPM predict={pred_ppm[0]}x{pred_ppm[1]} "
          f"observed={obs_ppm_wh} {'MATCH' if pred_ppm == obs_ppm_wh else 'MISMATCH'}")
    print("--- conservative-crtc prediction (Task 2 check) ---")
    mh_c = 240 if INT else 448  # overscan; INT=1 stays interlaced (no force_progressive)
    mw_c = 712
    if EN1:
        scaling = f32(float(clk) / float(magx))
        mw_c = int(math.floor(f32(float(mw_c) * scaling) + 0.5))
    print(f"overscan base=712 scaling={scaling if EN1 else 1:.4f} -> predict {mw_c}x{mh_c}")

if __name__ == '__main__':
    # args: dump.gs png_W png_H ppm_W ppm_H
    main(sys.argv[1], (int(sys.argv[2]), int(sys.argv[3])), (int(sys.argv[4]), int(sys.argv[5])))
