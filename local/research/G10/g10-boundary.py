#!/usr/bin/env python3
# G10: boundary definition from the G8 dump's own bytes.
# Extends the G8 census framing (id0 Transfer: u8 index + u32 size + payload;
# id1 Vsync: u8 field; id2 ReadFIFO: u32 size; id3 PrivRegs: 8192 B) with the
# packet ordinal of every packet, so both replay sides can name THE boundary
# (packet index + vsync index) identically. Read-only; prints the boundary
# table: per dump-vsync k, its VSync packet ordinal P_k, phase, transfer
# packet ordinals + path/size, and cumulative packet counts.
import struct, sys, hashlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def main(path):
    b = open(path, 'rb').read()
    n = len(b)
    print(f"file={path}")
    print(f"size={n} sha256={hashlib.sha256(b).hexdigest()}")
    o = 0
    fake_crc = u32(b, o); o += 4
    header_size = u32(b, o); o += 4
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o); o += 36
    o += serial_sz + shot_sz + state_size + 8192
    print(f"version={ver} packet_region_start={o}")
    # packet walk with ordinals
    ordinal = 0
    nv = 0
    cur_xfer = []  # (ordinal, path, size)
    print("BOUNDARY TABLE (ordinal = packet index shared by both sides):")
    while o < n:
        pid = b[o]; o += 1
        assert pid in (0, 1, 2, 3), (o, pid)
        if pid == 0:
            idx = b[o]; o += 1
            sz = u32(b, o); o += 4
            cur_xfer.append((ordinal, idx, sz))
            o += sz
        elif pid == 1:
            f = b[o]; o += 1
            t = ",".join(f"#{t[0]}:p{t[1]}:{t[2]}B" for t in cur_xfer)
            print(f"  dump-vsync#{nv}: VSync packet ordinal={ordinal} phase={f} "
                  f"n_xfer={len(cur_xfer)} [{t}]")
            nv += 1
            cur_xfer = []
        elif pid == 2:
            sz = u32(b, o); o += 4
            print(f"  ordinal={ordinal}: ReadFIFO size={sz}")
        elif pid == 3:
            o += 8192
            print(f"  ordinal={ordinal}: PrivRegs")
        ordinal += 1
    print(f"EOF_SYNC={'yes' if o == n else f'NO off={o-n}'} "
          f"total_packets={ordinal} total_vsyncs={nv}")

if __name__ == '__main__':
    main(sys.argv[1])
