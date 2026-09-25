#!/usr/bin/env python3
"""PX1: build a minimal .gs with only ticks [T0,T1]'s transfers + Regs.

Tests whether tick T's packets render in PCSX2 standalone (packet-intrinsic)
or need full history (history-dependent cache/state). The replayer needs >=2
vsyncs to dump a frame, so use a 2-tick range and read the first frame.
Usage: px1_mini.py <full.gs> <t0,t1,..> <out.gs>
"""
import struct, sys

full, tspec, out = sys.argv[1], sys.argv[2], sys.argv[3]
ticks = {}
with open(full + '.ticks') as f:
    for line in f:
        i, t = line.split()
        ticks[int(t)] = int(i)
want = [ticks[int(t)] for t in tspec.split(',')]
vi0, vi1 = min(want), max(want)
wantset = set(want)

b = open(full, 'rb').read()
o = 8
ver, ss, so, ssz, crc, w, h, sho, shs = struct.unpack_from('<9I', b, o)
hdr_end = o + 36 + ssz + shs
state = b[hdr_end:hdr_end + ss]
o = hdr_end + ss
init_regs = b[o:o + 8192]
o += 8192
frames = []
cur = None
vs = -1
n = len(b)
while o < n:
    pid = b[o]
    o += 1
    if pid == 0:
        idx = b[o]
        size = struct.unpack_from('<I', b, o + 1)[0]
        o += 5
        if vs + 1 in wantset:
            if cur is None:
                cur = []
            cur.append((0, idx, b[o:o + size]))
        o += size
    elif pid == 1:
        field = b[o]
        o += 1
        vs += 1
        if cur is not None:
            cur.append((1, field, None))
            frames.append(cur)
            cur = None
        if vs > vi1:
            break
    elif pid == 2:
        o += 4
    elif pid == 3:
        if vs + 1 in wantset:
            if cur is None:
                cur = []
            cur.append((3, 0, b[o:o + 8192]))
        o += 8192
    else:
        raise ValueError(f'bad packet id {pid} at {o - 1}')
assert len(frames) == len(wantset), f'got {len(frames)} frames want {sorted(wantset)}'
print(f'vsyncs {sorted(wantset)}: ' + ', '.join(
    f"{sum(1 for p in fr if p[0] == 0)}xf" for fr in frames))
w = open(out, 'wb')
w.write(b[0:hdr_end])
w.write(state)
w.write(init_regs)
for fr in frames:
    for kind, idx, data in fr:
        if kind == 0:
            w.write(struct.pack('<BBI', 0, idx, len(data)))
            w.write(data)
        elif kind == 3:
            w.write(struct.pack('<B', 3))
            w.write(data)
        else:
            w.write(struct.pack('<BB', 1, idx))
w.close()
print('wrote', out)
