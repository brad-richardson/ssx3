#!/usr/bin/env python3
# G8: dump provenance + EOF-synced packet census + per-vsync transfer map.
# Framing from pcsx2/GS/GSDump.h comment + GSDump.cpp writer (bytes, not docs):
#   u32 fake_crc, u32 header_size, GSDumpHeader(9xu32), serial, screenshot,
#   state[state_size], regs[8192], packets:
#   id0 Transfer: u8 index + u32 size + size bytes
#   id1 Vsync:    u8 field
#   id2 ReadFIFO: u32 size (no payload)
#   id3 PrivRegs: 8192 bytes
# Prints header table, census, per-vsync map, embedded-shot stats, ref PNG stats.
import struct, sys, hashlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def main(path, ref_png=None):
    b = open(path, 'rb').read()
    n = len(b)
    print(f"file={path}")
    print(f"size={n} sha256={hashlib.sha256(b).hexdigest()}")
    o = 0
    fake_crc = u32(b, o); o += 4
    header_size = u32(b, o); o += 4
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o); o += 36
    serial = b[o:o+serial_sz]; o += serial_sz
    shot = b[o:o+shot_sz]; o += shot_sz
    state = b[o:o+state_size]; o += state_size
    regs0 = b[o:o+8192]; o += 8192
    print(f"fakeCRC=0x{fake_crc:08x} header_size={header_size} "
          f"(36+serial({serial_sz})+shot({shot_sz})={36+serial_sz+shot_sz})")
    print(f"version={ver} state_size={state_size} crc=0x{crc:08x} serial={serial!r}")
    print(f"screenshot={shot_w}x{shot_h} shot_size={shot_sz} "
          f"(expect {shot_w*shot_h*4})")
    print(f"packet_region_start={o} packet_region_size={n-o}")
    # embedded screenshot stats (u32 LE pixels)
    px = struct.unpack('<%dI' % (len(shot)//4), shot)
    distinct = len(set(px))
    nonblack = sum(1 for p in px if (p & 0x00FFFFFF) != 0)
    print(f"embedded_shot: pixels={len(px)} distinct_u32={distinct} "
          f"nonblack_rgb={nonblack} ({nonblack/len(px):.4f})")
    # packet walk
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    phases = []
    xfer_bytes = 0
    xfer_by_path = {}
    per_vsync = []  # (dump_vsync_idx, phase, n_xfer, xfer_bytes)
    cur_n = 0; cur_b = 0
    nv = 0
    while o < n:
        pid = b[o]; o += 1
        assert pid in counts, (o, pid)
        counts[pid] += 1
        if pid == 0:
            idx = b[o]; o += 1
            sz = u32(b, o); o += 4
            xfer_by_path[idx] = xfer_by_path.get(idx, 0) + 1
            xfer_bytes += sz
            cur_n += 1; cur_b += sz
            o += sz
        elif pid == 1:
            f = b[o]; o += 1
            phases.append(f)
            per_vsync.append((nv, f, cur_n, cur_b))
            nv += 1; cur_n = 0; cur_b = 0
        elif pid == 2:
            sz = u32(b, o); o += 4
        elif pid == 3:
            o += 8192
    print(f"EOF_SYNC={'yes' if o == n else f'NO off={o-n}'}")
    print(f"census: Vsync={counts[1]} PrivRegs={counts[3]} "
          f"Transfer={counts[0]} ReadFIFO={counts[2]} GIF_bytes={xfer_bytes}")
    print(f"phases={phases}")
    print(f"xfer_by_path={xfer_by_path}")
    print("per_vsync(dump_idx,phase,n_xfer,xfer_bytes):")
    for v in per_vsync:
        print(f"  vsync#{v[0]} phase={v[1]} n_xfer={v[2]} bytes={v[3]}")
    ht = [v[0] for v in per_vsync if v[2] > 0]
    print(f"has_transfer_vsyncs={ht} first_iterate_maps_to_dump_vsync="
          f"{ht[0] if ht else None}")
    if ref_png:
        from PIL import Image
        im = Image.open(ref_png).convert('RGB')
        w, h = im.size
        data = im.tobytes()
        px3 = [data[i:i+3] for i in range(0, len(data), 3)]
        d = len(set(px3))
        nb = sum(1 for p in px3 if p != b'\x00\x00\x00')
        print(f"ref_png: {w}x{h} distinct_rgb={d} nonblack={nb} "
              f"({nb/(w*h):.4f})")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
