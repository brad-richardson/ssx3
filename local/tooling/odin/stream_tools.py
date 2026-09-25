#!/usr/bin/env python3
"""ssx3 GS stream surgery (TL1 Part 2): fold of N8X1's ad-hoc stream tools.

Subcommands (each with --help):
  records     list records of a PS2XGSC1 stream around a tick (gsstream.py)
  split       EOP-split one tick's GIF packets, marker after each piece (mkstream.py)
  variants    A+D TEX1/single-packet variants around one GIF record (mkvariant.py)
  nearestify  force every A+D TEX1_1/TEX1_2 write to nearest (nearestify.py)

Stream framing (PS2XGSC1): 8-byte magic, then records: u32 length + body.
Body: u8 kind, u64 tick, kind-specific payload. Kind 1 (GIF): u8 pathId at
byte 9, u32 size at bytes 10-13, GIF data at bytes 14..14+size. Kind 4
(marker): no payload beyond the tick.
"""

import argparse
import os
import struct
import sys
import tempfile

MAGIC = b"PS2XGSC1"
KINDS = {1: "gif", 2: "priv", 3: "xfer", 4: "marker", 5: "k5", 6: "l2h", 7: "clear"}

# A+D register ids (mkvariant.py).
AD = {'FRAME_1': 0x4c, 'ZBUF_1': 0x4e, 'TEX1_1': 0x14, 'TEST_1': 0x47,
      'ALPHA_1': 0x42, 'TEX0_1': 0x06, 'CLAMP_1': 0x08, 'TEXFLUSH': 0x3f,
      'DTHE': 0x45, 'COLCLAMP': 0x46, 'PABE': 0x49, 'FBA_1': 0x4a,
      'TEXA': 0x3b, 'PRMODECONT': 0x1a}

MMIN_MAP = {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 2}


def records(path, max_tick=None):
    """Yield (offset, kind, tick, body) for each record; stop after marker >= max_tick."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != MAGIC:
            raise ValueError(f"{path}: bad magic {magic!r}")
        off = 8
        while True:
            hdr = f.read(4)
            if len(hdr) < 4:
                return
            (length,) = struct.unpack("<I", hdr)
            rec = f.read(length)
            if len(rec) < length:
                raise ValueError(f"{path}: truncated record at offset {off}")
            kind = rec[0]
            (tick,) = struct.unpack_from("<Q", rec, 1)
            yield off, kind, tick, rec
            off += 4 + length
            if max_tick is not None and kind == 4 and tick >= max_tick:
                return


def rec_bytes(rec):
    return struct.pack("<I", len(rec)) + rec


def marker(tick):
    return rec_bytes(bytes([4]) + struct.pack("<Q", tick))


def gif_record(path, tick, data):
    return rec_bytes(bytes([1]) + struct.pack("<QBI", tick, path, len(data)) + data)


def eop_pieces(data):
    """Split GIF data at EOP tag boundaries (mkstream.py, verbatim logic)."""
    p, start, pieces = 0, 0, []
    while p + 16 <= len(data):
        lo, hi = struct.unpack_from("<QQ", data, p)
        p += 16
        nloop = lo & 0x7fff
        eop = (lo >> 15) & 1
        flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xf or 16
        if flg == 0:
            p += nloop * nreg * 16
        elif flg == 1:
            p += ((nloop * nreg * 8) + 15) & ~15
        else:
            p += nloop * 16
        if eop:
            pieces.append(data[start:p])
            start = p
    if start < len(data):
        pieces.append(data[start:])
    return pieces


def cmd_records(args):
    for off, kind, t, rec in records(args.src, args.tick):
        if t == args.tick or (kind == 4 and t >= args.tick - 1):
            extra = ""
            if kind == 1:
                extra = f" path={rec[9]} size={struct.unpack_from('<I', rec, 10)[0]}"
            elif kind == 2:
                o, v = struct.unpack_from("<IQ", rec, 9)
                extra = f" off=0x{o:x} val=0x{v:x}"
            elif kind == 5:
                extra = f" len={len(rec)}"
            print(f"{off} {KINDS.get(kind, kind)} tick={t}{extra}")


def cmd_split(args):
    """mkstream.py: prefix through end_tick with end_tick-1 GIF split at EOP + markers."""
    n = 0
    with open(args.out, "wb") as o:
        o.write(MAGIC)
        for off, k, t, rec in records(args.src, args.end_tick):
            if k == 4 and t == args.end_tick:
                o.write(rec_bytes(rec))
                n += 1
                break
            if t == args.end_tick - 1 and k == 1 and not args.no_split:
                size = struct.unpack_from("<I", rec, 10)[0]
                for piece in eop_pieces(rec[14:14 + size]):
                    r = rec[:10] + struct.pack("<I", len(piece)) + piece
                    o.write(rec_bytes(r))
                    o.write(marker(args.end_tick))
                    n += 1
            else:
                o.write(rec_bytes(rec))
    print(f"markers inserted/ending {n}")


def adpacket(pairs):
    tag = struct.pack("<QQ", len(pairs) | (1 << 15) | (1 << 60), 0xe)
    return tag + b"".join(struct.pack("<QQ", v, AD[n]) for n, v in pairs)


def setprim(value):
    def patch(d):
        lo, = struct.unpack_from("<Q", d, 16)
        if lo & 0x7ff != 0x5e:
            raise ValueError(f"variant patch: expected PRIM 0x5e tag, got 0x{lo & 0x7ff:x}")
        struct.pack_into("<Q", d, 16, (lo & ~0x7ff) | value)
    return patch


VARIANTS = {
    "v-base": {},
    "v-zmsk": dict(inject=[("ZBUF_1", 0x1010000e0)]),
    "v-rgbonly": dict(inject=[("FRAME_1", 0xff00000000080000)]),
    "v-alphaonly": dict(inject=[("FRAME_1", 0x00ffffff00080000)]),
    "v-nearest": dict(inject=[("TEX1_1", 0x0)]),
    "v-noabe": dict(patch=setprim(0x1e)),
}


def build_variant(out, src, logo_off, inject=(), patch=None, end_tick=44, after=()):
    """mkvariant.py: prefix to logo_off, marker, [inject], logo (maybe patched), marker."""
    with open(out, "wb") as o:
        o.write(MAGIC)
        for off, k, t, rec in records(src, end_tick):
            if off < logo_off:
                o.write(rec_bytes(rec))
                continue
            if not (off == logo_off and k == 1):
                raise ValueError(f"variant: expected GIF record at {logo_off}, got {k} at {off}")
            o.write(marker(end_tick))
            if inject:
                o.write(gif_record(2, t, adpacket(inject)))
                o.write(marker(end_tick))
            size = struct.unpack_from("<I", rec, 10)[0]
            data = bytearray(rec[14:14 + size])
            if patch:
                patch(data)
            o.write(gif_record(rec[9], t, bytes(data)))
            o.write(marker(end_tick))
            if after:
                o.write(gif_record(2, t, adpacket(after)))
                o.write(marker(end_tick))
            break


def cmd_variants(args):
    os.makedirs(args.out_dir, exist_ok=True)
    names = [args.only] if args.only else sorted(VARIANTS)
    for name in names:
        kw = VARIANTS[name]
        out = os.path.join(args.out_dir, name + ".gs")
        build_variant(out, args.src, args.logo_off, end_tick=args.end_tick,
                      inject=kw.get("inject", ()), patch=kw.get("patch"))
        print(name, os.path.getsize(out))


def patch_gif_nearest(d, cnt):
    """nearestify.py: force A+D TEX1_1/TEX1_2 (0x14/0x15) to nearest in packed GIF data."""
    p, n = 0, len(d)
    while p + 16 <= n:
        lo, hi = struct.unpack_from("<QQ", d, p)
        p += 16
        nloop = lo & 0x7fff
        flg = (lo >> 58) & 3
        nreg = (lo >> 60) & 0xf or 16
        if flg == 0:
            regs = [(hi >> (4 * i)) & 0xf for i in range(nreg)]
            if 0xe in regs:
                for _ in range(nloop):
                    for r in regs:
                        if r == 0xe and p + 16 <= n:
                            a = d[p + 8]
                            if a in (0x14, 0x15):
                                (v,) = struct.unpack_from("<Q", d, p)
                                mmin = (v >> 6) & 7
                                nv = (v & ~(0xf << 5)) | (MMIN_MAP.get(mmin, mmin) << 6)
                                if nv != v:
                                    struct.pack_into("<Q", d, p, nv)
                                    cnt["patched"] += 1
                                cnt["tex1"] += 1
                        p += 16
            else:
                p += nloop * nreg * 16
        elif flg == 1:
            p += ((nloop * nreg * 8) + 15) & ~15
        else:
            p += nloop * 16


def cmd_nearestify(args):
    cnt = {"tex1": 0, "patched": 0, "gif": 0}
    with open(args.src, "rb") as f, open(args.dst, "wb") as o:
        magic = f.read(8)
        if magic != MAGIC:
            raise ValueError(f"{args.src}: bad magic {magic!r}")
        o.write(magic)
        while True:
            h = f.read(4)
            if len(h) < 4:
                break
            (length,) = struct.unpack("<I", h)
            rec = bytearray(f.read(length))
            if len(rec) < length:
                raise ValueError(f"{args.src}: truncated record")
            if rec[0] == 1:
                (size,) = struct.unpack_from("<I", rec, 10)
                patch_gif_nearest(memoryview(rec)[14:14 + size], cnt)
                cnt["gif"] += 1
            o.write(h)
            o.write(rec)
    print(cnt)
    return cnt


def _fixture_stream(path):
    """Tiny 2-tick stream: tick-1 GIF (EOP split point + TEX1 bilinear) + markers."""
    tag1 = struct.pack("<QQ", 1 | (1 << 15) | (1 << 60), 0xe)  # PACKED, 1 reg, EOP
    ad = struct.pack("<QQ", 0x61, 0x14)  # TEX1_1 bilinear-ish value
    tag2 = struct.pack("<QQ", 1 | (1 << 15) | (1 << 60), 0xe)  # EOP set
    gif = tag1 + ad + tag2 + ad
    with open(path, "wb") as o:
        o.write(MAGIC)
        o.write(gif_record(2, 1, gif))
        o.write(marker(1))
        o.write(gif_record(2, 2, gif))
        o.write(marker(2))


def self_test():
    """No-device check: records/split/variants/nearestify on a synthetic stream."""
    tmp = tempfile.mkdtemp(prefix="stream-tools-selftest-")
    src = os.path.join(tmp, "in.gs")
    _fixture_stream(src)
    rows = list(records(src))
    assert [k for _, k, _, _ in rows] == [1, 4, 1, 4], rows
    assert [t for _, _, t, _ in rows] == [1, 1, 2, 2], rows
    # split at end_tick=2: tick-1 GIF -> 2 pieces + 2 markers; marker(1),
    # tick-2 GIF copied whole; ends at marker(2).
    out = os.path.join(tmp, "split.gs")
    cmd_split(argparse.Namespace(src=src, out=out, end_tick=2, no_split=False))
    rows = list(records(out))
    assert [k for _, k, _, _ in rows] == [1, 4, 1, 4, 4, 1, 4], [k for _, k, _, _ in rows]
    # variants around the first GIF record (offset 8); v-noabe's PRIM
    # patch is layout-specific, unit-tested separately below.
    vdir = os.path.join(tmp, "v")
    plain = [n for n, kw in VARIANTS.items() if "patch" not in kw]
    for name in plain:
        cmd_variants(argparse.Namespace(src=src, out_dir=vdir, logo_off=8, end_tick=2, only=name))
    assert sorted(os.listdir(vdir)) == sorted(n + ".gs" for n in plain), os.listdir(vdir)
    for name in plain:
        for _, k, _, _ in records(os.path.join(vdir, name + ".gs")):
            assert k in (1, 4), (name, k)
    buf = bytearray(32)
    struct.pack_into("<Q", buf, 16, 0x5e)
    setprim(0x1e)(buf)
    assert struct.unpack_from("<Q", buf, 16)[0] == 0x1e
    struct.pack_into("<Q", buf, 16, 0x61)
    try:
        setprim(0x1e)(buf)
    except ValueError:
        pass
    else:
        raise AssertionError("setprim accepted a non-PRIM tag")
    # nearestify: 4 TEX1 writes (2 per GIF record x2 records), value 0x61 -> patched
    dst = os.path.join(tmp, "near.gs")
    cnt = cmd_nearestify(argparse.Namespace(src=src, dst=dst))
    assert cnt["gif"] == 2 and cnt["tex1"] == 4 and cnt["patched"] == 4, cnt
    for _, k, t, rec in records(dst):
        if k == 1:
            for at in (14 + 16, 14 + 48):
                assert struct.unpack_from("<Q", rec, at)[0] == 1, hex(struct.unpack_from("<Q", rec, at)[0])
    print(f"stream_tools self-test PASS ({tmp})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true", help="run the no-device self-test and exit")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("records", help="list records around a tick")
    p.add_argument("src")
    p.add_argument("tick", type=int)
    p.set_defaults(fn=cmd_records)
    p = sub.add_parser("split", help="EOP-split tick end_tick-1 GIF packets with markers after each piece")
    p.add_argument("out")
    p.add_argument("end_tick", type=int)
    p.add_argument("--src", default="/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs")
    p.add_argument("--no-split", action="store_true", help="copy the prefix without splitting")
    p.set_defaults(fn=cmd_split)
    p = sub.add_parser("variants", help="A+D/patch variants around one GIF record (v-base, v-zmsk, ...)")
    p.add_argument("--src", default="/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs")
    p.add_argument("--logo-off", type=int, required=True, help="byte offset of the target GIF record")
    p.add_argument("--end-tick", type=int, default=44)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--only", choices=sorted(VARIANTS), help="build one variant only")
    p.set_defaults(fn=cmd_variants)
    p = sub.add_parser("nearestify", help="force every A+D TEX1 write to nearest filtering")
    p.add_argument("src")
    p.add_argument("dst")
    p.set_defaults(fn=cmd_nearestify)
    args = ap.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    if not args.cmd:
        ap.print_help()
        return 2
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
