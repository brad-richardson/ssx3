#!/usr/bin/env python3
"""AU1: list EA BIGF archive entries (big-endian dir) and census payload magics.
Usage: au1_big.py <file.BIG> [--list N]"""
import struct, sys, collections
path = sys.argv[1]
listn = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--list" else 0
with open(path, "rb") as f:
    hdr = f.read(16)
    magic, total, count, dirsize = hdr[:4], *struct.unpack(">III", hdr[4:16])
    # BIGF: total size is little-endian in some tools; count/dirsize are BE
    f.seek(16); d = f.read(dirsize)
    ents = []; p = 0
    for _ in range(count):
        off, size = struct.unpack(">II", d[p:p+8]); p += 8
        e = d.index(b"\0", p); name = d[p:e].decode("latin1"); p = e + 1
        ents.append((off, size, name))
    ext = collections.Counter(); mag = collections.Counter(); bytes_by = collections.Counter()
    for off, size, name in ents:
        f.seek(off); m = f.read(8)
        x = name.rsplit(".", 1)[-1].lower()
        ext[x] += 1; bytes_by[x] += size
        tag = m[:4].decode("latin1") if all(32 <= c < 127 for c in m[:4]) else m[:4].hex()
        mag[(x, tag)] += 1
print(f"{path}: magic={magic!r} entries={count} dirsize={dirsize} filesize_field_le={struct.unpack('<I', hdr[4:8])[0]}")
for x, n in ext.most_common():
    print(f"  ext .{x}: {n} entries, {bytes_by[x]} bytes")
for (x, t), n in sorted(mag.items()):
    print(f"  payload magic .{x} {t!r}: {n}")
for off, size, name in ents[:listn]:
    print(f"  {off:#010x} {size:10d} {name}")
