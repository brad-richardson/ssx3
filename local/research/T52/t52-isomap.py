#!/usr/bin/env python3
# T52 isomap: walk ISO9660 (+Joliet if present) directories, emit extent map.
# Usage: python3 t52-isomap.py <iso>  ->  "lbn=<extent> sectors=<n> size=<bytes> name=<path>"
import struct
import sys


def read_sector(f, lbn, n=1):
    f.seek(lbn * 2048)
    return f.read(n * 2048)


def parse_dir(f, extent, size, path, out, seen):
    data = read_sector(f, extent, (size + 2047) // 2048)
    off = 0
    while off < len(data):
        if off + 1 > len(data):
            break
        rl = data[off]
        if rl == 0:
            # pad to next sector
            nxt = ((off // 2048) + 1) * 2048
            off = nxt if nxt > off else off + 1
            continue
        rec = data[off:off + rl]
        if len(rec) < 33:
            break
        flags = rec[25]
        ext = struct.unpack("<I", rec[2:6])[0]
        sz = struct.unpack("<I", rec[10:14])[0]
        nlen = rec[32]
        name = rec[33:33 + nlen]
        off += rl
        if nlen == 1 and name[0] in (0, 1):
            continue
        try:
            nm = name.decode("utf-8", "replace").split(";")[0]
        except Exception:
            nm = repr(name)
        full = path + "/" + nm
        if flags & 0x02:
            if (ext, full) not in seen:
                seen.add((ext, full))
                parse_dir(f, ext, sz, full, out, seen)
        else:
            out.append((ext, (sz + 2047) // 2048, sz, full))


def main():
    iso = sys.argv[1]
    with open(iso, "rb") as f:
        pvd = read_sector(f, 16)
        assert pvd[0] == 1 and pvd[1:6] == b"CD001", "not ISO9660 PVD at 16"
        root_ext = struct.unpack("<I", pvd[156 + 2:156 + 6])[0]
        root_sz = struct.unpack("<I", pvd[156 + 10:156 + 14])[0]
        print("PVD root_ext=%d root_size=%d" % (root_ext, root_sz))
        # supplementary (Joliet) descriptors
        for sec in (17, 18):
            d = read_sector(f, sec)
            if d[0] == 2 and d[1:6] == b"CD001":
                esc = d[88:120]
                rext = struct.unpack("<I", d[156 + 2:156 + 6])[0]
                rsz = struct.unpack("<I", d[156 + 10:156 + 14])[0]
                print("SVD sec=%d esc=%r root_ext=%d root_size=%d" % (sec, esc, rext, rsz))
        out, seen = [], set()
        parse_dir(f, root_ext, root_sz, "", out, seen)
    for ext, sec, sz, name in sorted(out):
        print("lbn=%d sectors=%d size=%d name=%s" % (ext, sec, sz, name))


main()
