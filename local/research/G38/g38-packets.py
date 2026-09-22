#!/usr/bin/env python3
# G38: dump packet walk + span-0 GIF census (host-only, Task 1).
# Layout from dump/gs_dump_parser.cpp::restart + gif_transfer.
import struct, sys, hashlib

DUMP = "/Volumes/Extreme SSD/ps2x-g13/g13-dump.gs"
PIN = "154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32"

raw = open(DUMP, "rb").read()
sha = hashlib.sha256(raw).hexdigest()
print(f"dump sha {sha} match={sha == PIN} size={len(raw)}")
assert sha == PIN, "dump pin mismatch -> STOP"

fake, hsize = struct.unpack_from("<II", raw, 0)
assert fake == 0xFFFFFFFF, hex(fake)
ver, state_size, serial_off, serial_size, crc, sw, sh, shot_off, shot_size = \
    struct.unpack_from("<IIIIIIIII", raw, 8)
print(f"ver={ver} state_size={state_size} hsize={hsize}")
assert state_size == 4194813, state_size

# regs(425) + vram(4M) + paths(80) + internal_q(4) = state; priv(8192) after
p = 8 + hsize
regs_off = p
vram_off = p + 425
paths_off = vram_off + 4194304
iq_off = paths_off + 80
priv_off = iq_off + 4
packets_off = priv_off + 8192
print(f"packets_off={packets_off} (file {len(raw)}, tail={len(raw) - packets_off})")

# initial GIF path state: tag(16B) + reg(u32) per path
paths = []
for i in range(4):
    tag_lo, tag_hi, reg = struct.unpack_from("<QQI", raw, paths_off + 20 * i)
    paths.append({"tag_lo": tag_lo, "tag_hi": tag_hi, "reg": reg, "loop": 0})
    if tag_lo or tag_hi or reg:
        print(f"path{i} init tag_lo={tag_lo:#x} tag_hi={tag_hi:#x} reg={reg}")

def tag_fields(lo, hi):
    return dict(nloop=lo & 0x7FFF, eop=(lo >> 15) & 1, pre=(lo >> 46) & 1,
                prim=(lo >> 47) & 0x7FF, flg=(lo >> 58) & 3, nreg=(lo >> 60) & 0xF,
                regs=hi)

# packet walk
pkts = []
o = packets_off
n = len(raw)
while o < n:
    t = raw[o]; o += 1
    if t == 0:  # Transfer
        path = raw[o]; size = struct.unpack_from("<I", raw, o + 1)[0]; o += 5
        pkts.append(("XFER", path, size, o))
        o += size
    elif t == 1:  # Vsync
        ph = raw[o]; o += 1
        pkts.append(("VSYNC", ph))
    elif t == 3:  # PrivRegisters
        pkts.append(("PRIV", o))
        o += 8192
    elif t == 2:  # ReadFIFO
        size = struct.unpack_from("<I", raw, o)[0]; o += 4
        pkts.append(("FIFO", size))
        break
    else:
        print(f"UNKNOWN packet type {t} at file offset {o - 1}")
        break
print(f"packets={len(pkts)} EOF_SYNC={o == n} end_off={o}")
vs = [i for i, k in enumerate(pkts) if k[0] == "VSYNC"]
print(f"vsync packet idx={vs} nvsync={len(vs)}")
for i in vs:
    print(f"  vsync pkt#{i} phase={pkts[i][1]}")
# span sizes
bounds = [-1] + vs
for s in range(len(vs)):
    span = pkts[bounds[s] + 1:bounds[s + 1]]
    nx = sum(1 for k in span if k[0] == "XFER")
    npr = sum(1 for k in span if k[0] == "PRIV")
    nby = sum(k[2] for k in span if k[0] == "XFER")
    print(f"span{s}: xfers={nx} privs={npr} xfer_bytes={nby}")

# span-0 GIF census
print("--- span0 GIF census ---")
GIFREG = {0x0: "PRIM", 0x1: "RGBAQ", 0x2: "ST", 0x3: "UV", 0x4: "XYZF2",
          0x5: "XYZ2", 0x6: "TEX0_1", 0x7: "TEX0_2", 0x8: "CLAMP_1",
          0x9: "CLAMP_2", 0xA: "FOG", 0xB: "RSV", 0xC: "XYZF3",
          0xD: "XYZ3", 0xE: "A_D", 0xF: "NOP"}
# fresh path state (restart inits loop=0, tag+reg from state)
pst = [{"lo": p["tag_lo"], "hi": p["tag_hi"], "reg": p["reg"], "loop": 0}
       for p in paths]
span0 = pkts[:vs[0]]
xfer_no = 0
for k in span0:
    if k[0] != "XFER":
        print(f"  [{k[0]}]")
        continue
    _, path, size, off = k
    nqw = size // 16
    st = pst[path]
    nreg = (st["lo"] >> 60) & 0xF or 16
    # need current tag NLOOP: from st
    def cur_nloop():
        return st["lo"] & 0x7FFF
    i = 0
    tags = 0
    ad = {}  # addr -> list of (xfer, qwoff, data)
    vtx = 0
    flgs = {}
    while i < nqw:
        if st["loop"] == cur_nloop():
            lo, hi = struct.unpack_from("<QQ", raw, off + 16 * i)
            st["lo"], st["hi"] = lo, hi
            tf = tag_fields(lo, hi)
            tags += 1
            flgs[tf["flg"]] = flgs.get(tf["flg"], 0) + 1
            st["loop"] = 0; st["reg"] = 0
            i += 1
            nreg = tf["nreg"] or 16
        else:
            tf = tag_fields(st["lo"], st["hi"])
            if tf["flg"] == 0:  # PACKED
                r = (st["hi"] >> (4 * st["reg"])) & 0xF
                st["reg"] += 1
                if r == 0xE:
                    data, hi2 = struct.unpack_from("<QQ", raw, off + 16 * i)
                    addr = hi2 & 0x7F
                    ad.setdefault(addr, []).append((xfer_no, i, data))
                elif r in (4, 5, 0xC, 0xD):
                    vtx += 1
                i += 1
                if st["reg"] == nreg:
                    st["loop"] += 1; st["reg"] = 0
            elif tf["flg"] == 1:  # REGLIST
                for j in range(2):
                    r = (st["hi"] >> (4 * st["reg"])) & 0xF
                    st["reg"] += 1
                    if r in (4, 5, 0xC, 0xD):
                        vtx += 1
                    if st["reg"] == nreg:
                        st["loop"] += 1; st["reg"] = 0
                        if st["loop"] == tf["nloop"]:
                            break
                i += 1
            else:  # IMAGE
                take = min(nqw - i, tf["nloop"] - st["loop"])
                i += take; st["loop"] += take
    print(f"  xfer#{xfer_no} path={path} size={size} tags={tags} flgs={flgs} vtx={vtx} "
          f"AD_addrs={sorted((hex(a), len(v)) for a, v in ad.items())}")
    for a in sorted(ad):
        for (x, q, d) in ad[a][:6]:
            print(f"      AD addr={a:#04x} data={d:#018x} (qw {q})")
    xfer_no += 1
