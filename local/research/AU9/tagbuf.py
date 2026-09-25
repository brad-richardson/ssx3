# AU9: decode tagbuf.bin (AU9 PCSX2 hook) or our runtime's tagbuf capture: per tick, the tag-3 voice record.
# record: 'TAGB' u32 vsync u32 ns u32 size, size bytes (tag buffer), 0x240 bytes EE status 0x50b740.
# tag-3 payload (SNDIOP_updatevoices, AU2 snddrv-disasm 0x7d1c): +0 wet bus mask (u64), +8 dry bus mask (u64),
# +0x20 + v*8 for v < 48: u32 SPU start address (bits 0-22; 0 = key off), u16 pitch, s8 volL, s8 volR.
import struct, sys, collections
def records(path):
    d = open(path, 'rb').read(); p = 0
    while p + 16 <= len(d):
        mag, vs, ns, size = struct.unpack_from('<4I', d, p)
        assert mag == 0x42474154, hex(p)
        buf = d[p + 16:p + 16 + size]; st = d[p + 16 + size:p + 16 + size + 0x240]
        p += 16 + size + 0x240
        yield vs, ns, buf, st
def tags(buf):
    off = 0; out = {}
    while off + 4 <= len(buf):
        t = struct.unpack_from('<I', buf, off)[0]
        if t == 6: break
        if t in (0, 5): out.setdefault(t, buf[off + 4:off + 16]); off += 16; continue
        ln = struct.unpack_from('<I', buf, off + 4)[0]
        hdr = 16 if t == 1 else 8  # tag 1 = {1, len, 0, 0}; tag 3 = {3, len} (SNDIOP_processtagbuf 0x7084)
        out[t] = buf[off + hdr:off + hdr + ln]
        off += hdr + ln
    return out
def voices(p3):
    return [struct.unpack_from('<IHbb', p3, 0x20 + v * 8) for v in range(48)]
if __name__ == '__main__':
    n = 0; prev = None; ev = collections.Counter(); first = {}; busses = collections.Counter(); kon_ticks = []
    tagset = collections.Counter(); lens = collections.Counter(); tail_nz = collections.Counter()
    for vs, ns, buf, st in records(sys.argv[1]):
        n += 1; t = tags(buf); tagset[tuple(sorted(t))] += 1
        if 3 not in t: continue
        p3 = t[3]; lens[len(p3)] += 1
        busses[(p3[0:8].hex(), p3[8:16].hex(), p3[16:32].hex())] += 1
        for i in range(0x1A0, len(p3)):
            if p3[i]: tail_nz[i] += 1
        vv = voices(p3)
        if prev:
            k = 0
            for v, (a, b) in enumerate(zip(prev, vv)):
                if a[0] != b[0]:
                    kind = 'keyoff' if (b[0] & 0x7fffff) == 0 else 'keyon'
                    ev[kind] += 1; k += kind == 'keyon'
                    first.setdefault(kind, []).append((vs, ns, v, hex(b[0]), b[1], b[2], b[3])) if len(first.get(kind, [])) < 12 else None
                if a[1] != b[1]: ev['pitch'] += 1
                if a[2:] != b[2:]: ev['vol'] += 1
            if k: kon_ticks.append(ns)
        prev = vv
    print('records', n, 'tag sets', dict(tagset), 'tag3 payload lens', dict(lens))
    print('events', dict(ev))
    for k, v in first.items():
        print(k); [print('  ', x) for x in v]
    print('bus masks (wet, dry, +0x10..0x20):', busses.most_common(5))
    print('nonzero bytes past voice table (offset: ticks):', sorted(tail_nz.items())[:40])
    if kon_ticks:
        import itertools
        print('keyon ticks: first ns', kon_ticks[0], 'last', kon_ticks[-1], 'count', len(kon_ticks))
