#!/usr/bin/env python3
"""RP1: find IMAGE uploads whose DBP is in a set over a tick range of a PS2XGSC1 capture (our stream)
or a PCSX2 .gs dump, and save the raw pixel bytes (CT32 → PNG with alpha histogram).
Usage: rp1_texdump.py cap|pcsx2 <path> <t_from> <t_to> <dbp,dbp,...> <outdir>"""
import sys, os, struct
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'RR1'))
import rr1_census as rc
import rr1_cap as cap
g = rc.g

src, path, t0, t1, dbps, outdir = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), \
    set(int(x) for x in sys.argv[5].split(',')), sys.argv[6]
os.makedirs(outdir, exist_ok=True)
gs = g.GS(); decs = {}
found = []
orig_feed = g.PathDecoder.feed

def feed(self, data):
    # capture IMAGE bytes for watched uploads: re-run the IMAGE branch bookkeeping by diffing byte counts
    pi = self.gs.pending_image
    before = pi['bytes'] if pi is not None else 0
    buf_before = self.buf + data
    orig_feed(self, data)
    pi2 = self.gs.pending_image
    if pi2 is not None and pi2.get('watch'):
        pass
g.PathDecoder.feed = feed

orig_write = g.GS.write
def write(self, reg, val):
    orig_write(self, reg, val)
    if reg == 0x53 and (val & 3) == 0 and self.pending_image is not None:
        if self.pending_image['dbp'] in dbps:
            self.pending_image['watch'] = True
            self.pending_image['data'] = bytearray()
            found.append(self.pending_image)
g.GS.write = write

# Patch the IMAGE branch: wrap feed's slicing by intercepting pending_image['bytes'] updates.
class Tracker(dict):
    pass

def run_feed(dec, data):
    # replicate e51 PathDecoder.feed but append IMAGE bytes to pending_image['data'] when watched
    dec.buf += data
    o = 0; n = len(dec.buf); gsx = dec.gs
    while True:
        if dec.loops == 0:
            if n - o < 16: break
            lo, hi = struct.unpack_from('<QQ', dec.buf, o); o += 16
            nloop = lo & 0x7FFF; pre = (lo >> 46) & 1; prim = (lo >> 47) & 0x7FF
            dec.flg = (lo >> 58) & 3; nreg = (lo >> 60) & 0xF
            dec.nreg = 16 if nreg == 0 else nreg
            dec.regs = [(hi >> (4 * i)) & 0xF for i in range(dec.nreg)]
            if dec.flg == 0 and pre: gsx.write(g.REG_PRIM, prim)
            dec.loops = nloop; dec.ri = 0
            if dec.flg >= 2:
                dec.image_left = nloop * 16; dec.loops = 1 if nloop else 0
            if dec.flg == 1 and nloop: dec.reglist_left = nloop * dec.nreg
            continue
        if dec.flg == 0:
            if n - o < 16: break
            lo, hi = struct.unpack_from('<QQ', dec.buf, o); o += 16
            dec.packed(dec.regs[dec.ri], lo, hi); dec.ri += 1
            if dec.ri == dec.nreg: dec.ri = 0; dec.loops -= 1
        elif dec.flg == 1:
            if n - o < 8: break
            (v,) = struct.unpack_from('<Q', dec.buf, o); o += 8
            r = dec.regs[dec.ri]
            if r not in (g.REG_AD, g.REG_NOP): gsx.write(r, v)
            dec.ri += 1; dec.reglist_left -= 1
            if dec.ri == dec.nreg: dec.ri = 0
            if dec.reglist_left == 0:
                if (dec.loops * dec.nreg) % 2 == 1: o += 8
                dec.loops = 0
        else:
            take = min(dec.image_left, n - o)
            if take <= 0: break
            pi = gsx.pending_image
            if pi is not None:
                pi['bytes'] += take
                if pi.get('watch'): pi['data'] += dec.buf[o:o + take]
            o += take; dec.image_left -= take
            if dec.image_left == 0: dec.loops = 0
    dec.buf = dec.buf[o:]

if src == 'cap':
    for kind, tk, body in cap.iter_records(path, t0, t1):
        gs.meta = dict(vsync=tk, path=0, seq=0) if not hasattr(gs, 'meta') else gs.meta
        if kind == 1:
            pth = body[0]; (sz,) = struct.unpack_from('<I', body, 1)
            gs.meta = dict(gs.meta, vsync=tk, path=pth)
            run_feed(decs.setdefault(pth, g.PathDecoder(gs)), body[5:5 + sz])
else:
    raise SystemExit('pcsx2 mode: use rp1_texdump_pcsx2 path')

for k, im in enumerate(found):
    d = bytes(im['data'])
    name = 'up%02d-t%s-dbp%d-psm%#x-%dx%d-pos%d,%d' % (k, im.get('vsync'), im['dbp'], im['dpsm'], im['rrw'], im['rrh'], im['dsax'], im['dsay'])
    open(os.path.join(outdir, name + '.bin'), 'wb').write(d)
    line = name + ' bytes=%d dbw=%d' % (len(d), im['dbw'])
    if im['dpsm'] == 0 and len(d) >= im['rrw'] * im['rrh'] * 4:
        a = Counter(d[3::4]); line += ' alpha: min=%d max=%d top=%s' % (min(a), max(a), a.most_common(5))
        edge = [d[(y * im['rrw'] + x) * 4 + 3] for y in range(im['rrh']) for x in range(im['rrw'])
                if x in (0, im['rrw'] - 1) or y in (0, im['rrh'] - 1)]
        line += ' edge_alpha: min=%d max=%d mean=%.1f' % (min(edge), max(edge), sum(edge) / len(edge))
    print(line)
