#!/usr/bin/env python3
"""Variant streams around the tick-43 logo sprite (GIF record at offset LOGO_OFF).
Output: prefix records up to LOGO_OFF, marker(44), [inject A+D], logo packet (maybe patched), marker(44)."""
import struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from gsstream import records
SRC = '/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs'
AD = {'FRAME_1': 0x4c, 'ZBUF_1': 0x4e, 'TEX1_1': 0x14, 'TEST_1': 0x47, 'ALPHA_1': 0x42, 'TEX0_1': 0x06, 'CLAMP_1': 0x08, 'TEXFLUSH': 0x3f, 'DTHE': 0x45, 'COLCLAMP': 0x46, 'PABE': 0x49, 'FBA_1': 0x4a, 'TEXA': 0x3b, 'PRMODECONT': 0x1a}
def rb(rec): return struct.pack('<I', len(rec)) + rec
def marker(t): return rb(bytes([4]) + struct.pack('<Q', t))
def gif(path, tick, data): return rb(bytes([1]) + struct.pack('<QBI', tick, path, len(data)) + data)
def adpacket(pairs):
    tag = struct.pack('<QQ', len(pairs) | (1 << 15) | (1 << 60), 0xe)
    return tag + b''.join(struct.pack('<QQ', v, AD[n]) for n, v in pairs)
def build(out, logo_off, inject=(), patch=None, end_tick=44, after=()):
    with open(out, 'wb') as o:
        o.write(b'PS2XGSC1')
        for off, k, t, rec in records(SRC, end_tick):
            if off < logo_off:
                o.write(rb(rec)); continue
            assert off == logo_off and k == 1, (off, k)
            o.write(marker(end_tick))
            if inject: o.write(gif(2, t, adpacket(inject))); o.write(marker(end_tick))
            size = struct.unpack_from('<I', rec, 10)[0]
            data = bytearray(rec[14:14 + size])
            if patch: patch(data)
            o.write(gif(rec[9], t, bytes(data))); o.write(marker(end_tick))
            if after: o.write(gif(2, t, adpacket(after))); o.write(marker(end_tick))
            break
def setprim(v):
    def f(d):
        lo, = struct.unpack_from('<Q', d, 16); assert lo & 0x7ff == 0x5e
        struct.pack_into('<Q', d, 16, (lo & ~0x7ff) | v)
    return f
if __name__ == '__main__':
    import os
    D = '/Users/brad/dev/ssx3-work/N8X1/streams'
    L = 9353
    V = {
      'v-base': {},
      'v-zmsk': dict(inject=[('ZBUF_1', 0x1010000e0)]),
      'v-rgbonly': dict(inject=[('FRAME_1', 0xff00000000080000)]),
      'v-alphaonly': dict(inject=[('FRAME_1', 0x00ffffff00080000)]),
      'v-nearest': dict(inject=[('TEX1_1', 0x0)]),
      'v-noabe': dict(patch=setprim(0x1e)),
    }
    for name, kw in V.items():
        build(f'{D}/{name}.gs', L, **kw)
        print(name, os.path.getsize(f'{D}/{name}.gs'))
