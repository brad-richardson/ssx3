#!/usr/bin/env python3
"""PX1: find GIF-stream state (IMAGE/PACKED/REGLIST) split across packets with
different path labels. PCSX2 keeps per-path GIF units, so a mid-transfer
label flip corrupts its stream while our single-unit backends stay correct.

Usage: px1_imgspan.py <gs.cap> <from_tick> <to_tick>
"""
import os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'E51'))
import e51_gif as g

cap, t_from, t_to = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
dec = g.PathDecoder(g.GS())
prev = None
nflip = 0
with open(cap, 'rb') as f:
    assert f.read(8) == b'PS2XGSC1'
    while True:
        h = f.read(4)
        if len(h) < 4:
            break
        (n,) = struct.unpack('<I', h)
        kind = f.read(1)[0]
        (tk,) = struct.unpack('<Q', f.read(8))
        body = f.read(n - 9)
        if tk < t_from:
            continue
        if tk > t_to:
            break
        if kind != 1:
            continue
        path = body[0]
        (sz,) = struct.unpack_from('<I', body, 1)
        st = (dec.loops, dec.flg, getattr(dec, 'image_left', 0),
              getattr(dec, 'reglist_left', 0), dec.ri, len(dec.buf))
        if prev is not None and path != prev[0] and (st[0] > 0 or st[2] > 0 or st[5] > 0):
            print(f"tick={tk} label {prev[0]}->{path} mid-stream: "
                  f"loops={st[0]} flg={st[1]} image_left={st[2]} "
                  f"reglist_left={st[3]} ri={st[4]} buf={st[5]} prev_sz={prev[1]} cur_sz={sz}")
            nflip += 1
            if nflip > 40:
                print('... (capped)')
                break
        dec.feed(body[5:5 + sz])
        prev = (path, sz)
print(f"done flips={nflip} end_state loops={dec.loops} flg={dec.flg} "
      f"image_left={getattr(dec, 'image_left', 0)} buf={len(dec.buf)}")
