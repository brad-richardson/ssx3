#!/usr/bin/env python3
"""G13: read-only census of the rich .gs dump (framing from G12).

Per dump-vsync aggregates:
  - transfer count / total GIF bytes / paths seen / sizes (min/med/max)
  - IMAGE-mode TRX bytes up (host->local, DIR=0) vs down (local->host, DIR=1)
    via TRXDIR/TRXREG+DPSM accounting (ADDRs 0x50-0x53 per Gif_Unit.cpp)
  - FRAME_1/2 FBP targets touched (in-packet order, first 12)
  - PRIM-reg histogram (PACKED PRIM + TAGPRE: type + TME)
  - ZBUF_1/2 ZBP targets touched
Header: version, state_size, serial, crc, shot WxH; EOF-sync assert.
"""
import struct
import sys

PSM_BPP = {0x00: 4, 0x01: 3, 0x02: 2, 0x0A: 2, 0x13: 1, 0x14: 0.5,
           0x1B: 1, 0x24: 0.5, 0x2C: 0.5, 0x30: 4, 0x31: 3, 0x32: 2, 0x3A: 2}
PRIM_NAMES = {0: "POINT", 1: "LINE", 2: "LINESTRIP", 3: "TRI",
              4: "TRISTRIP", 5: "TRIFAN", 6: "SPRITE"}


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def u64(b, o):
    return struct.unpack_from('<Q', b, o)[0]


def note_ad(addr, d0, st):
    """Fold one A+D write (PACKED AD or REGLIST direct) into state dict."""
    if addr == 0x50:
        st['blt'] = ((d0 >> 32) & 0x3FFF, (d0 >> 56) & 0x3F)
        st['moves'].add((d0 & 0x3FFF, (d0 >> 24) & 0x3F,
                         (d0 >> 32) & 0x3FFF, (d0 >> 56) & 0x3F))
        st['n_trx'] += 1
    elif addr == 0x51:
        st['trxpos'] = d0
        st['n_trx'] += 1
    elif addr == 0x52:
        st['trxreg'] = (d0 & 0xFFF, (d0 >> 16) & 0xFFF)
        st['n_trx'] += 1
    elif addr == 0x53:
        st['xdir'] = d0 & 3
        st['n_trx'] += 1
    elif addr in (0x3C, 0x3D):
        st['fbps'].append(d0 & 0x1FF)
    elif addr in (0x3E, 0x3F):
        st['zbps'].append(d0 & 0x1FF)
    elif addr in (0x06, 0x07):
        st['tbps'].append(d0 & 0x3FFF)
    elif addr == 0x00:
        k = ("PRIM", d0 & 7, (d0 >> 4) & 1, (d0 >> 9) & 1)
        st['primhist'][k] = st['primhist'].get(k, 0) + 1
    elif addr in (0x04, 0x05, 0x0C, 0x0D):
        st['kicks'][addr] = st['kicks'].get(addr, 0) + 1


def fresh_st():
    return {'blt': (None, None), 'trxreg': (None, None), 'trxpos': None,
            'xdir': None, 'fbps': [], 'zbps': [], 'tbps': [],
            'primhist': {}, 'kicks': {}, 'packed': {}, 'moves': set(),
            'n_trx': 0}


def walk(payload, st):
    """Walks one transfer; TRX regs persist in st across transfers.
    Returns (img_up_qw, img_mv_qw, img_unk_qw, n_img_tags, tags, flghist,
    leftover). st accumulates fbps/zbps/tbps/primhist/kicks/packed/moves."""
    nb = len(payload)
    o = 0  # byte offset
    img_up = img_mv = img_unk = n_img = 0
    tags = 0
    flghist = {}
    while o + 16 <= nb:
        lo, hi = u64(payload, o), u64(payload, o + 8)
        o += 16
        nloop = lo & 0x7FFF
        eop = (lo >> 15) & 1
        pre = (lo >> 46) & 1
        primval = (lo >> 47) & 0x7FF
        flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xF
        nreg = nreg if nreg else 16
        regs = [(hi >> (4 * i)) & 0xF for i in range(16)]
        tags += 1
        flghist[flg] = flghist.get(flg, 0) + 1
        if pre:
            k = ("TAGPRE", primval & 7, (primval >> 4) & 1, (primval >> 9) & 1)
            st['primhist'][k] = st['primhist'].get(k, 0) + 1
        if nloop == 0:
            nloop = 32768
        if flg == 0:  # PACKED: NREG qwads per loop
            done = False
            for _ in range(nloop):
                for r in regs[:nreg]:
                    if o + 16 > nb:
                        done = True
                        break
                    d0, d1 = u64(payload, o), u64(payload, o + 8)
                    o += 16
                    st['packed'][r] = st['packed'].get(r, 0) + 1
                    if r == 0xE:
                        note_ad(d1 & 0xFF, d0, st)
                    elif r == 0x0:
                        k = ("PRIM", d0 & 7, (d0 >> 4) & 1, (d0 >> 9) & 1)
                        st['primhist'][k] = st['primhist'].get(k, 0) + 1
                    elif r in (0x4, 0x5, 0xC, 0xD):
                        st['kicks'][0x100 + r] = st['kicks'].get(0x100 + r, 0) + 1
                if done:
                    break
        elif flg == 1:  # REGLIST: regs are A_D addrs directly, 64b each
            done = False
            for _ in range(nloop):
                for r in regs[:nreg]:
                    if o + 8 > nb:
                        done = True
                        break
                    v = u64(payload, o)
                    o += 8
                    note_ad(r, v, st)
                if done:
                    break
                if nreg % 2 == 1 and o + 8 <= nb:
                    o += 8  # odd-NREG loops pad to qword
        else:  # IMAGE / IMAGE2: NLOOP qwads of image data
            take = min(nloop, (nb - o) // 16)
            if st['xdir'] == 0:
                img_up += take
            elif st['xdir'] == 2:
                img_mv += take
            else:
                img_unk += take
            n_img += 1
            o += take * 16
        if eop:
            break
    return img_up, img_mv, img_unk, n_img, tags, flghist, nb - o


def main(path):
    b = open(path, 'rb').read()
    n = len(b)
    o = 8
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o)
    o += 36
    serial = b[o:o + serial_sz]
    o += serial_sz + shot_sz + state_size + 8192
    print(f"file_bytes={n} version={ver} state_size={state_size} serial={serial} "
          f"crc={crc:#x} shot={shot_w}x{shot_h} shot_sz={shot_sz}")
    ordinal, nv = 0, 0
    cur = []
    tot_xfer = tot_gif = 0
    persist = fresh_st()  # TRX regs persist across transfers (HW regs)
    while o < n:
        pid = b[o]
        o += 1
        assert pid in (0, 1, 2, 3), (o, pid)
        if pid == 0:
            idx = b[o]
            o += 1
            sz = u32(b, o)
            o += 4
            cur.append((ordinal, idx, sz, o))
            o += sz
        elif pid == 1:
            f = b[o]
            o += 1
            sizes = sorted(sz for (_, _, sz, _) in cur)
            paths = sorted(set(idx for (_, idx, _, _) in cur))
            gif = sum(sizes)
            iu = imv = iunk = nimg = atrx = tags = 0
            fbp_order, zbp_set, tbp_set = [], set(), set()
            ph, kicks, flg, packed, moves = {}, {}, {}, {}, set()
            maxleft = 0
            for (_, _, sz, off) in cur:
                wst = fresh_st()
                # thread persistent TRX regs through this transfer
                for k in ('blt', 'trxreg', 'trxpos', 'xdir'):
                    wst[k] = persist[k]
                wup, wmv, wunk, wni, wt, wf, wleft = walk(b[off:off + sz], wst)
                for k in ('blt', 'trxreg', 'trxpos', 'xdir'):
                    persist[k] = wst[k]
                iu += wup
                imv += wmv
                iunk += wunk
                nimg += wni
                for x in wst['fbps']:
                    if x not in fbp_order:
                        fbp_order.append(x)
                zbp_set.update(wst['zbps'])
                tbp_set.update(wst['tbps'])
                moves.update(wst['moves'])
                for k, v in wst['primhist'].items():
                    ph[k] = ph.get(k, 0) + v
                for k, v in wst['kicks'].items():
                    kicks[k] = kicks.get(k, 0) + v
                for k, v in wst['packed'].items():
                    packed[k] = packed.get(k, 0) + v
                for k, v in wf.items():
                    flg[k] = flg.get(k, 0) + v
                atrx += wst['n_trx']
                tags += wt
                maxleft = max(maxleft, wleft)
            phs = {f"{k[0]}:{PRIM_NAMES.get(k[1], k[1])}:TME{k[2]}:CTXT{k[3]}": v
                   for k, v in sorted(ph.items())}
            med = sizes[len(sizes) // 2] if sizes else 0
            print(f"vsync#{nv} phase={f} xfer={len(cur)} gif_bytes={gif} "
                  f"paths={paths} sizes(min/med/max)={sizes[0] if sizes else 0}/{med}/{sizes[-1] if sizes else 0}")
            print(f"  img_up={iu * 16} B img_move={imv * 16} B img_unk={iunk * 16} B img_tags={nimg} "
                  f"trx_writes={atrx} tags={tags} flg={dict(sorted(flg.items()))} max_leftover={maxleft}")
            print(f"  fbp_order={fbp_order[:12]} zbps={sorted(zbp_set)} tbp0s={sorted(tbp_set)[:12]}")
            print(f"  prims={phs}")
            print(f"  kicks={dict(sorted(kicks.items()))} packed={dict(sorted(packed.items()))}")
            mv = sorted(moves)
            print(f"  moves(SBP,SPSM,DBP,DPSM) n={len(mv)} {mv[:8]}")
            tot_xfer += len(cur)
            tot_gif += gif
            nv += 1
            cur = []
        elif pid == 2:
            sz = u32(b, o)
            o += 4
        else:
            o += 8192
        ordinal += 1
    print(f"EOF_SYNC={'yes' if o == n else 'NO'} total_vsyncs={nv} "
          f"total_xfer={tot_xfer} total_gif={tot_gif}")


if __name__ == '__main__':
    main(sys.argv[1])
