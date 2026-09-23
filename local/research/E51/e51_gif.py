#!/usr/bin/env python3
"""E51: one GIF-stream decoder for both sides.

Inputs
  pcsx2 <file.gs>     PCSX2 GS dump (framing per G8: u32 crc, u32 header_size,
                      9xu32 header, serial, screenshot, state, regs[8192],
                      then packets: 0 Transfer(u8 index, u32 size, data),
                      1 VSync(u8 field), 2 ReadFIFO(u32), 3 Regs(8192)).
                      State = GSState::Freeze v9: VRAM (4 MiB) at offset 425 (found by page match),
                      context registers at 124 (ctx0) / 220 (ctx1).
  recomp <file.bin>   PS2X_GIF_DUMP records (u32 magic 'GIFP', vsync, path,
                      vu1 startPC, size, data).

Output: python objects (prims, images) used by e51_tables.py.
"""
import struct
import math
from collections import defaultdict

REG_PRIM, REG_RGBAQ, REG_ST, REG_UV, REG_XYZF2, REG_XYZ2 = 0x00, 0x01, 0x02, 0x03, 0x04, 0x05
REG_TEX0_1, REG_TEX0_2, REG_CLAMP_1, REG_CLAMP_2, REG_FOG = 0x06, 0x07, 0x08, 0x09, 0x0A
REG_XYZF3, REG_XYZ3, REG_AD, REG_NOP = 0x0C, 0x0D, 0x0E, 0x0F
REG_TEX1_1, REG_TEX1_2, REG_TEX2_1, REG_TEX2_2 = 0x14, 0x15, 0x16, 0x17
REG_XYOFFSET_1, REG_XYOFFSET_2, REG_PRMODECONT, REG_PRMODE = 0x18, 0x19, 0x1A, 0x1B
REG_SCISSOR_1, REG_SCISSOR_2, REG_TEST_1, REG_TEST_2 = 0x40, 0x41, 0x47, 0x48
REG_FRAME_1, REG_FRAME_2, REG_ZBUF_1, REG_ZBUF_2 = 0x4C, 0x4D, 0x4E, 0x4F
REG_BITBLTBUF, REG_TRXPOS, REG_TRXREG, REG_TRXDIR = 0x50, 0x51, 0x52, 0x53

NEEDED = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 2, 7: 0}
BPP = {0x00: 32, 0x01: 24, 0x02: 16, 0x0A: 16, 0x13: 8, 0x14: 4, 0x1B: 8, 0x24: 4, 0x2C: 4,
       0x30: 32, 0x31: 24, 0x32: 16, 0x3A: 16}


def f32(u):
    return struct.unpack('<f', struct.pack('<I', u & 0xFFFFFFFF))[0]


def tex0_fields(v):
    return dict(tbp0=v & 0x3FFF, tbw=(v >> 14) & 0x3F, psm=(v >> 20) & 0x3F, tw=(v >> 26) & 0xF,
                th=(v >> 30) & 0xF, tcc=(v >> 34) & 1, tfx=(v >> 35) & 3, cbp=(v >> 37) & 0x3FFF,
                cpsm=(v >> 51) & 0xF, csm=(v >> 55) & 1, csa=(v >> 56) & 0x1F, cld=(v >> 61) & 7)


class Ctx:
    def __init__(self):
        self.xyoffset = 0
        self.tex0 = 0
        self.tex1 = 0
        self.clamp = 0
        self.scissor = 0
        self.test = 0
        self.frame = 0
        self.zbuf = 0


class GS:
    def __init__(self):
        self.prim = 0
        self.prmodecont = 1
        self.prmode = 0
        self.ctx = [Ctx(), Ctx()]
        self.rgbaq = 0
        self.s = 0.0
        self.t = 0.0
        self.q = 1.0
        self.u = 0
        self.v = 0
        self.fog = 0
        self.queue = []
        self.bitbltbuf = 0
        self.trxpos = 0
        self.trxreg = 0
        self.prims = []
        self.images = []
        self.meta = {}
        self.pending_image = None

    # --- register writes (raw 64-bit values) ---
    def write(self, reg, val):
        if reg == REG_PRIM:
            self.prim = val & 0x7FF
            self.queue = []
        elif reg == REG_RGBAQ:
            self.rgbaq = val & 0xFFFFFFFF
            self.q = f32(val >> 32)
        elif reg == REG_ST:
            self.s = f32(val)
            self.t = f32(val >> 32)
        elif reg == REG_UV:
            self.u = val & 0x3FFF
            self.v = (val >> 16) & 0x3FFF
        elif reg in (REG_XYZ2, REG_XYZ3):
            self.kick(val & 0xFFFF, (val >> 16) & 0xFFFF, (val >> 32) & 0xFFFFFFFF, reg == REG_XYZ2)
        elif reg in (REG_XYZF2, REG_XYZF3):
            self.fog = (val >> 56) & 0xFF
            self.kick(val & 0xFFFF, (val >> 16) & 0xFFFF, (val >> 32) & 0xFFFFFF, reg == REG_XYZF2)
        elif reg in (REG_TEX0_1, REG_TEX0_2):
            self.ctx[reg - REG_TEX0_1].tex0 = val
        elif reg in (REG_TEX2_1, REG_TEX2_2):
            c = self.ctx[reg - REG_TEX2_1]
            mask = (0x3F << 20) | (((1 << 27) - 1) << 37)
            c.tex0 = (c.tex0 & ~mask) | (val & mask)
        elif reg in (REG_CLAMP_1, REG_CLAMP_2):
            self.ctx[reg - REG_CLAMP_1].clamp = val
        elif reg in (REG_TEX1_1, REG_TEX1_2):
            self.ctx[reg - REG_TEX1_1].tex1 = val
        elif reg in (REG_XYOFFSET_1, REG_XYOFFSET_2):
            self.ctx[reg - REG_XYOFFSET_1].xyoffset = val
        elif reg in (REG_SCISSOR_1, REG_SCISSOR_2):
            self.ctx[reg - REG_SCISSOR_1].scissor = val
        elif reg in (REG_TEST_1, REG_TEST_2):
            self.ctx[reg - REG_TEST_1].test = val
        elif reg in (REG_FRAME_1, REG_FRAME_2):
            self.ctx[reg - REG_FRAME_1].frame = val
        elif reg in (REG_ZBUF_1, REG_ZBUF_2):
            self.ctx[reg - REG_ZBUF_1].zbuf = val
        elif reg == REG_PRMODECONT:
            self.prmodecont = val & 1
        elif reg == REG_PRMODE:
            self.prmode = val & 0x7F8
        elif reg == REG_BITBLTBUF:
            self.bitbltbuf = val
        elif reg == REG_TRXPOS:
            self.trxpos = val
        elif reg == REG_TRXREG:
            self.trxreg = val
        elif reg == REG_TRXDIR:
            d = val & 3
            if d == 0:
                b = self.bitbltbuf
                self.pending_image = dict(dbp=(b >> 32) & 0x3FFF, dbw=(b >> 48) & 0x3F, dpsm=(b >> 56) & 0x3F,
                                          dsax=(self.trxpos >> 32) & 0x7FF, dsay=(self.trxpos >> 48) & 0x7FF,
                                          rrw=self.trxreg & 0xFFF, rrh=(self.trxreg >> 32) & 0xFFF,
                                          bytes=0, **self.meta)
                self.images.append(self.pending_image)

    def attrs(self):
        return self.prim if self.prmodecont else ((self.prim & 7) | self.prmode)

    def kick(self, x, y, z, drawing):
        self.queue.append(dict(x=x / 16.0, y=y / 16.0, z=z, s=self.s, t=self.t, q=self.q,
                               u=self.u / 16.0, v=self.v / 16.0, a=(self.rgbaq >> 24) & 0xFF))
        ptype = self.prim & 7
        need = NEEDED.get(ptype, 0)
        if need == 0 or len(self.queue) < need:
            return
        verts = self.queue[-need:] if ptype != 5 else [self.queue[0]] + self.queue[-2:]
        if drawing:
            a = self.attrs()
            ci = (a >> 9) & 1
            c = self.ctx[ci]
            self.prims.append(dict(type=ptype, tme=(a >> 4) & 1, fst=(a >> 8) & 1, abe=(a >> 6) & 1,
                                   ctxt=ci, tex0=c.tex0, tex1=c.tex1, clamp=c.clamp, xyoffset=c.xyoffset,
                                   scissor=c.scissor, test=c.test, frame=c.frame, verts=[dict(v) for v in verts],
                                   **self.meta))
        else:
            self.prims.append(dict(type=ptype, adc=True, **self.meta))
        # queue maintenance
        if ptype in (0, 1, 3, 6):
            self.queue = []
        elif ptype in (2, 4):
            self.queue = self.queue[-(need - 1):]
        elif ptype == 5:
            self.queue = [self.queue[0], self.queue[-1]]


class PathDecoder:
    """Streaming GIF decoder for one path (qword granular)."""

    def __init__(self, gs):
        self.gs = gs
        self.buf = b''
        self.loops = 0
        self.nreg = 0
        self.regs = []
        self.flg = 0
        self.ri = 0
        self.image_left = 0

    def feed(self, data):
        self.buf += data
        o = 0
        n = len(self.buf)
        gs = self.gs
        while True:
            if self.loops == 0:
                if n - o < 16:
                    break
                lo, hi = struct.unpack_from('<QQ', self.buf, o)
                o += 16
                nloop = lo & 0x7FFF
                pre = (lo >> 46) & 1
                prim = (lo >> 47) & 0x7FF
                self.flg = (lo >> 58) & 3
                nreg = (lo >> 60) & 0xF
                self.nreg = 16 if nreg == 0 else nreg
                self.regs = [(hi >> (4 * i)) & 0xF for i in range(self.nreg)]
                if self.flg == 0 and pre:
                    gs.write(REG_PRIM, prim)
                self.loops = nloop
                self.ri = 0
                if self.flg >= 2:
                    self.image_left = nloop * 16
                    self.loops = 1 if nloop else 0
                if self.flg == 1 and nloop:
                    self.reglist_left = nloop * self.nreg
                continue
            if self.flg == 0:  # PACKED
                if n - o < 16:
                    break
                lo, hi = struct.unpack_from('<QQ', self.buf, o)
                o += 16
                self.packed(self.regs[self.ri], lo, hi)
                self.ri += 1
                if self.ri == self.nreg:
                    self.ri = 0
                    self.loops -= 1
            elif self.flg == 1:  # REGLIST
                if n - o < 8:
                    break
                (v,) = struct.unpack_from('<Q', self.buf, o)
                o += 8
                r = self.regs[self.ri]
                if r not in (REG_AD, REG_NOP):
                    gs.write(r, v)
                self.ri += 1
                self.reglist_left -= 1
                if self.ri == self.nreg:
                    self.ri = 0
                if self.reglist_left == 0:
                    if (self.loops * self.nreg) % 2 == 1:
                        o += 8  # pad to qword
                    self.loops = 0
            else:  # IMAGE
                take = min(self.image_left, n - o)
                if take <= 0:
                    break
                if gs.pending_image is not None:
                    gs.pending_image['bytes'] += take
                o += take
                self.image_left -= take
                if self.image_left == 0:
                    self.loops = 0
        self.buf = self.buf[o:]

    def packed(self, reg, lo, hi):
        gs = self.gs
        if reg == REG_PRIM:
            gs.write(REG_PRIM, lo & 0x7FF)
        elif reg == REG_RGBAQ:
            r, g = lo & 0xFF, (lo >> 32) & 0xFF
            b, a = hi & 0xFF, (hi >> 32) & 0xFF
            gs.rgbaq = r | (g << 8) | (b << 16) | (a << 24)
        elif reg == REG_ST:
            gs.s = f32(lo)
            gs.t = f32(lo >> 32)
            gs.q = f32(hi)
        elif reg == REG_UV:
            gs.u = lo & 0x3FFF
            gs.v = (lo >> 32) & 0x3FFF
        elif reg == REG_XYZF2:
            adc = (hi >> 47) & 1
            gs.fog = (hi >> 36) & 0xFF
            gs.kick(lo & 0xFFFF, (lo >> 32) & 0xFFFF, (hi >> 4) & 0xFFFFFF, not adc)
        elif reg == REG_XYZ2:
            adc = (hi >> 47) & 1
            gs.kick(lo & 0xFFFF, (lo >> 32) & 0xFFFF, hi & 0xFFFFFFFF, not adc)
        elif reg == REG_FOG:
            gs.fog = (hi >> 36) & 0xFF
        elif reg == REG_XYZF3:
            gs.kick(lo & 0xFFFF, (lo >> 32) & 0xFFFF, (hi >> 4) & 0xFFFFFF, False)
        elif reg == REG_XYZ3:
            gs.kick(lo & 0xFFFF, (lo >> 32) & 0xFFFF, hi & 0xFFFFFFFF, False)
        elif reg == REG_AD:
            gs.write(hi & 0xFF, lo)
        elif reg == REG_NOP:
            pass
        else:
            gs.write(reg, lo)  # TEX0/CLAMP etc. packed = raw 64-bit


def load_pcsx2(path, max_vsyncs=None):
    b = open(path, 'rb').read()
    o = 8
    ver, ss, so, ssz, c, w, h, sho, shs = struct.unpack_from('<9I', b, o)
    o += 36 + ssz + shs
    state = b[o:o + ss]
    o += ss + 8192
    vram = state[425:425 + 4 * 1024 * 1024]
    gs = GS()
    for i in range(2):
        base = 124 + 96 * i
        r = struct.unpack_from('<12Q', state, base)
        c_ = gs.ctx[i]
        (c_.xyoffset, c_.tex0, c_.tex1, c_.clamp, _m1, _m2, c_.scissor, _al, c_.test, _fba, c_.frame,
         c_.zbuf) = r
    gs.prim = struct.unpack_from('<Q', state, 4)[0] & 0x7FF
    gs.prmodecont = struct.unpack_from('<Q', state, 12)[0] & 1
    decs = defaultdict(lambda: PathDecoder(gs))
    vs = 0
    gs.meta = dict(vsync=vs, path=0, pc=None)
    n = len(b)
    while o < n:
        pid = b[o]
        o += 1
        if pid == 0:
            idx = b[o]
            size = struct.unpack_from('<I', b, o + 1)[0]
            o += 5
            gs.meta = dict(vsync=vs, path=idx + 1, pc=None)
            decs[idx].feed(b[o:o + size])
            o += size
        elif pid == 1:
            o += 1
            vs += 1
            if max_vsyncs is not None and vs >= max_vsyncs:
                break
        elif pid == 2:
            o += 4
        elif pid == 3:
            o += 8192
        else:
            raise ValueError(f'bad packet id {pid} at {o - 1}')
    return gs, vram


def load_recomp(path):
    b = open(path, 'rb').read()
    gs = GS()
    decs = defaultdict(lambda: PathDecoder(gs))
    o = 0
    n = len(b)
    while o + 20 <= n:
        magic, vs, pth, pc, size = struct.unpack_from('<5I', b, o)
        if magic != 0x50464947:
            raise ValueError(f'bad magic at {o}')
        o += 20
        gs.meta = dict(vsync=vs, path=pth, pc=pc)
        decs[pth].feed(b[o:o + size])
        o += size
    return gs


def classify(p):
    ox = (p['xyoffset'] & 0xFFFF) / 16.0
    oy = ((p['xyoffset'] >> 32) & 0xFFFF) / 16.0
    sc = p['scissor']
    x0s, x1s, y0s, y1s = sc & 0x7FF, (sc >> 16) & 0x7FF, (sc >> 32) & 0x7FF, (sc >> 48) & 0x7FF
    xs = [v['x'] - ox for v in p['verts']]
    ys = [v['y'] - oy for v in p['verts']]
    zero = (min(xs) == max(xs)) or (min(ys) == max(ys))
    left, right, top, bot = x0s, x1s + 1, y0s, y1s + 1
    if max(xs) < left or min(xs) > right or max(ys) < top or min(ys) > bot:
        cls = 'off'
    elif min(xs) >= left and max(xs) <= right and min(ys) >= top and max(ys) <= bot:
        cls = 'on'
    else:
        cls = 'straddle'
    return cls, zero


def tex_range(t):
    """Approximate byte range of a texture in native GS VRAM (block-granular)."""
    bpp = BPP.get(t['psm'], 32)
    w = max(t['tbw'], 1) * 64
    h = 1 << t['th']
    size = (w * h * bpp) // 8
    start = t['tbp0'] * 256
    size = ((size + 8191) // 8192) * 8192
    return start, min(start + size, 4 * 1024 * 1024)
