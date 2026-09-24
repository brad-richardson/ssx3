#!/usr/bin/env python3
"""Summarize AU6 SND status snapshots and EE mixer/stream memory."""
import argparse
from collections import Counter
import json
from pathlib import Path
import struct


def status(path):
    b = path.read_bytes()
    stride = 4 + 0x240
    assert len(b) % stride == 0, (len(b), stride)
    rows = [b[i:i + stride] for i in range(0, len(b), stride)]
    words = [[struct.unpack_from('<I', row, 4 + o)[0]
              for o in range(0, 0x240, 4)] for row in rows]
    serials = [struct.unpack_from('<I', row)[0] for row in rows]
    fields = []
    for j, o in enumerate(range(0, 0x240, 4)):
        vals = [r[j] for r in words]
        changes = sum(a != z for a, z in zip(vals, vals[1:]))
        nz = sum(v != 0 for v in vals)
        if nz or changes:
            ct = Counter(vals)
            fields.append(dict(offset=f'0x{o:03x}', first=f'0x{vals[0]:08x}',
                               last=f'0x{vals[-1]:08x}', nonzero=nz,
                               changes=changes, unique=len(ct),
                               common=[(f'0x{k:08x}', v) for k, v in ct.most_common(5)]))
    return dict(records=len(rows), first_serial=serials[0], last_serial=serials[-1],
                serial_gaps=sum(z != a + 1 for a, z in zip(serials, serials[1:])),
                nonzero_fields=fields)


def snapshot(path):
    b = path.read_bytes()
    assert len(b) == 0x2000000, len(b)

    def u32(a):
        if a < 0 or a + 4 > len(b):
            return None
        return struct.unpack_from('<I', b, a)[0]

    def f32(a):
        if a < 0 or a + 4 > len(b):
            return None
        return struct.unpack_from('<f', b, a)[0]

    g = 0x515b40
    count = b[g + 4]
    channels = b[g + 5]
    table = u32(g + 0x1dc)
    globals_nz = {f'0x{o:03x}': f'0x{u32(g + o):08x}'
                  for o in range(0, 0x240, 4) if u32(g + o)}
    voices = []
    if table is not None and table < len(b):
        for i in range(min(count, 128)):
            a = table + 0x60 * i
            if a + 0x60 > len(b):
                break
            row = {f'0x{o:02x}': f'0x{u32(a + o):08x}' for o in range(0, 0x60, 4) if u32(a + o)}
            voices.append(dict(index=i, addr=f'0x{a:08x}', type=b[a], flag=b[a + 1],
                               level_1c=f32(a + 0x1c), level_38=f32(a + 0x38), words=row))
    sig = struct.pack('<II', 0x3c9520, 0x3c95f0)
    stream_objects = []
    at = 0
    while True:
        at = b.find(sig, at)
        if at == -1:
            break
        stream_objects.append(dict(addr=f'0x{at:08x}', handle=f'0x{u32(at + 0x1c):08x}',
                                   pos=u32(at + 0x20), loop_start=u32(at + 0x24),
                                   loop_end=u32(at + 0x28), source=f'0x{u32(at + 0x2c):08x}',
                                   first_48=b[at:at + 0x30].hex()))
        at += 8
    return dict(global_addr=f'0x{g:08x}', count=count, channels=channels,
                voice_table=f'0x{table:08x}', global_nonzero=globals_nz,
                voices=voices, stream_objects=stream_objects)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--status', type=Path)
    ap.add_argument('--snap', type=Path)
    a = ap.parse_args()
    print(json.dumps({'status': status(a.status) if a.status else None,
                      'snapshot': snapshot(a.snap) if a.snap else None}, indent=2))
