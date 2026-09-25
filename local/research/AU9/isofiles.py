# AU9: list ISO9660 files (path, lbn, size) and map byte offsets to files.
import struct, sys
f = open(sys.argv[1], 'rb')
def sec(l, n=1): f.seek(l * 2048); return f.read(2048 * n)
pvd = sec(16); root = pvd[156:156 + 34]
files = []
def walk(rec, path):
    lbn, size = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
    data = sec(lbn, (size + 2047) // 2048); o = 0
    while o < len(data):
        ln = data[o]
        if ln == 0: o = (o // 2048 + 1) * 2048; continue
        r = data[o:o + ln]; nl = r[32]; name = r[33:33 + nl]
        if name not in (b'\x00', b'\x01'):
            nm = name.decode('ascii', 'replace').split(';')[0]
            if r[25] & 2: walk(r, path + nm + '/')
            else: files.append((struct.unpack_from('<I', r, 2)[0], struct.unpack_from('<I', r, 10)[0], path + nm))
        o += ln
walk(root, '/')
files.sort()
offs = [int(x, 0) for x in sys.argv[2:]]
for off in offs:
    l = off // 2048
    hit = [x for x in files if x[0] <= l < x[0] + (x[1] + 2047) // 2048]
    print(hex(off), hit[0][2] if hit else '?', 'at +' + hex(off - hit[0][0] * 2048) if hit else '', hex(hit[0][1]) if hit else '')
if not offs:
    for l, s, p in files: print(l, s, p)
