# AU9: timeline of SND uploads (ra 0x3c4438 4 KB payloads) and 0x30-byte cid-0 packets in sifdma.bin.
import struct, sys
d = open(sys.argv[1], 'rb').read()
p = 0; up = []; pk = []
while p + 32 <= len(d):
    mag, vs, ns, src, dst, size, attr, ra = struct.unpack_from('<8I', d, p)
    n = min(size & 0x1fffffff, 0x20000)
    if ra == 0x3c4438: up.append((vs, ns, src, size))
    if dst == 0x1e2c0 and size == 0x30:
        w = struct.unpack_from('<12I', d, p + 32); pk.append((vs, ns, w))
    p += 32 + n
def runs(xs):
    out = []; 
    for v in xs:
        if out and v - out[-1][1] <= 30: out[-1][1] = v; out[-1][2] += 1
        else: out.append([v, v, 1])
    return out
print('uploads', len(up), 'bytes', sum(u[3] for u in up))
for a, b, c in runs([u[0] for u in up]): print(f'  upload vsync {a}-{b}: {c} chunks')
print('cid0 packets', len(pk))
for a, b, c in runs([x[0] for x in pk]): print(f'  cid0 vsync {a}-{b}: {c}')
for vs, ns, w in pk[:6]: print('  pkt vs', vs, ' '.join(hex(x) for x in w))
