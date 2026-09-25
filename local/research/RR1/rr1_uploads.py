#!/usr/bin/env python3
"""RR1: ordered IMAGE uploads (GIF + native) and TEX0 writes for one tick of our capture.
Usage: rr1_uploads.py <gs.cap> <tick> [max_lines]"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import rr1_census as rc
import rr1_cap as cap
g = rc.g


def main():
    path, tick = sys.argv[1], int(sys.argv[2])
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    gs = g.GS(); decs = {}
    out = []
    orig = g.GS.write
    def w(self, reg, val):
        if reg in (0x06, 0x07):
            t = g.tex0_fields(val)
            out.append(f"TEX0 tbp={t['tbp0']} psm={t['psm']:#x} tw={t['tw']} th={t['th']} cbp={t['cbp']} cpsm={t['cpsm']:#x} csa={t['csa']} cld={t['cld']}")
        elif reg == 0x53 and (val & 3) == 0:
            b = self.bitbltbuf
            out.append(f"UPLOAD dbp={(b>>32)&0x3fff} dbw={(b>>48)&0x3f} dpsm={(b>>56)&0x3f:#x} {self.trxreg & 0xfff}x{(self.trxreg>>32)&0xfff} pos={(self.trxpos>>32)&0x7ff},{(self.trxpos>>48)&0x7ff}")
        orig(self, reg, val)
    g.GS.write = w
    for kind, tk, body in cap.iter_records(path, tick, tick):
        if kind == 1:
            pth = body[0]; (sz,) = struct.unpack_from('<I', body, 1)
            decs.setdefault(pth, g.PathDecoder(gs)).feed(body[5:5 + sz])
        elif kind == 5:
            bb, tp, tr, td = struct.unpack_from('<4Q', body, 0)
            out.append(f"NATIVE dbp={(bb>>32)&0x3fff} dbw={(bb>>48)&0x3f} dpsm={(bb>>56)&0x3f:#x} {tr & 0xfff}x{(tr>>32)&0xfff} pos={(tp>>32)&0x7ff},{(tp>>48)&0x7ff}")
    for l in out[:mx]:
        print(l)

if __name__ == '__main__':
    main()
