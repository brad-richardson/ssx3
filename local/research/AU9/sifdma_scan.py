# AU9: summarize sifdma.bin (AU9 PCSX2 hook): per-descriptor header + payload; group by (ra, dst, size).
import struct, sys, collections
d = open(sys.argv[1], 'rb').read()
p = 0; rows = []
while p + 32 <= len(d):
    mag, vs, ns, src, dst, size, attr, ra = struct.unpack_from('<8I', d, p)
    assert mag == 0x30414d44, hex(p)
    n = min(size & 0x1fffffff, 0x20000)
    rows.append((vs, ns, src, dst, size, attr, ra, p + 32))
    p += 32 + n
print('descriptors', len(rows))
g = collections.Counter((hex(r[6]), hex(r[3]), hex(r[4])) for r in rows)
for k, v in g.most_common(25): print(v, k)
print('first 12:')
for r in rows[:12]: print('vs', r[0], 'ns', r[1], 'src', hex(r[2]), 'dst', hex(r[3]), 'size', hex(r[4]), 'attr', hex(r[5]), 'ra', hex(r[6]))
