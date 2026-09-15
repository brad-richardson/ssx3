#!/usr/bin/env python3
"""Import GameCube Tricky course textures and lightmaps into SSX 3 world records.

Sources (decoded 2026-09-11 from GameCube Tricky gari.gsh, gari_L.gsh, gari.nbd):
  SHPG entries carry one image each: u8 type (0x10 | GX texture format: 0x14
  RGB565, 0x15 RGB5A3, 0x19 CI8, 0x1e CMPR), u24 BE size, u16 BE width, u16 BE
  height, 4 zero bytes, u32 LE 0x20, pixels from +16 in native GX tiling;
  CI8 is followed by a 0x32 palette chunk (256 x u16 BE RGB5A3 from +16).
  NBD patches (448 bytes) bind a texture index (i16 at 428, an entry of the
  course .gsh; the material table is not involved), a lightmap sheet index
  (i16 at 430, an entry of the _L.gsh), a lightmap rectangle (u, v, w, h
  floats at 0; 8 px cells of a 128 px sheet) and four corner UV vec4s at 16.
  Checked on the PS2 gari.pbd too: the same words, little-endian.

Target: SSX 3 world texture (kind 9) and lightmap (kind 10) records, 32-byte
header (type, u24 size or 0, width, height, 0, 0x30, 0, levels-1, 0, u32 0x20,
12 zero bytes) then the pixel levels; CI8 adds a 32-byte 0x32 palette chunk
header and 512 palette bytes. Surveyed over all 4,571 texture records in
GXBE69: kind 10 always uses one level, kind 9 one to four.
Terrain patches bind a texture through word 416 (texture rid << 16 |
lightmap rid) and word 412 (0x80000 | texture group index); the lightmap
rectangle is at 16 (u, v, w, h) and the corner UVs at 32.
"""
import argparse
from pathlib import Path
import struct

from gamecube_shape import entries as shape_entries
from gamecube_world import unused_global_rids

WORLD_HEADER = 32
PATCH_STRIDE = 448
BITS = {0x14: 16, 0x15: 16, 0x16: 32, 0x19: 8, 0x1e: 4}
# Palette chunk header copied from GXBE69 world CI8 records (before 512 palette bytes).
PALETTE_HEADER = bytes.fromhex('3200000000ff000100ff00001000000000000020') + bytes(12)


def shape_images(data):
    """Decode every image entry of a SHPG container: list of dicts with type, width, height, pixels, palette."""
    out = []
    for e in shape_entries(data):
        o = e['offset']
        kind = data[o]
        if kind not in BITS:
            continue
        width, height = struct.unpack_from('>HH', data, o + 4)
        n = width * height * BITS[kind] // 8
        pixels = data[o + 16:o + 16 + n]
        if len(pixels) != n:
            raise ValueError(f'Truncated image {e["index"]}')
        palette = None
        if kind == 0x19:
            size = int.from_bytes(data[o + 1:o + 4], 'big')
            pal = o + size
            if data[pal] != 0x32:
                raise ValueError(f'Missing palette for image {e["index"]}')
            palette = data[pal + 16:pal + 16 + 512]
        out.append(dict(index=e['index'], name=e['name'], type=kind, width=width, height=height,
                        pixels=pixels, palette=palette))
    return out


def world_image_record(img):
    """SSX 3 world kind 9/10 payload for a single-level image."""
    kind, width, height = img['type'], img['width'], img['height']
    pixels = img['pixels']
    if len(pixels) != width * height * BITS[kind] // 8:
        raise ValueError('Pixel size does not match the image dimensions')
    size = WORLD_HEADER + len(pixels) if kind == 0x19 else 0
    header = bytes([kind]) + size.to_bytes(3, 'big') + struct.pack('>HHI', width, height, 0)
    header += bytes([0x30, 0, 0, 0]) + struct.pack('>I', 0x20) + bytes(12)
    out = header + pixels
    if kind == 0x19:
        if not img.get('palette') or len(img['palette']) != 512:
            raise ValueError('CI8 image needs a 512-byte palette')
        out += PALETTE_HEADER + img['palette']
    return out


def tricky_bindings(nbd):
    """Per-patch texture/lightmap bindings from a GameCube Tricky NBD."""
    count, patch_offset = struct.unpack_from('>I', nbd, 8)[0], struct.unpack_from('>I', nbd, 68)[0]
    n_textures = struct.unpack_from('>I', nbd, 52)[0]
    out = []
    for i in range(count):
        o = patch_offset + PATCH_STRIDE * i
        texture, lightmap = struct.unpack_from('>hh', nbd, o + 428)
        if not 0 <= texture < n_textures:
            raise ValueError(f'Patch {i}: texture {texture} out of range')
        uv = [struct.unpack_from('>2f', nbd, o + 16 + 16 * k) for k in range(4)]
        out.append(dict(texture=texture, lightmap=lightmap, lightmap_rect=struct.unpack_from('>4f', nbd, o), uv=uv))
    return out


def bind_patch(payload, texture_rid, lightmap_rid, texture_group, uv, lightmap_rect,
               lightmap_size=128, inset=0.5, track=8):
    """Write texture/lightmap binding words into a GameCube SSX 3 terrain payload.

    Tricky corner UVs use v in [-1, 0] where SSX 3 uses [0, 1] for the same corner
    order, so v is shifted by +1. The lightmap rectangle gets a half-texel inset
    like the stock records (cell 16 px -> u + 0.5/128, w - 1/128).

    The page word at 412 is `track << 16 | texture group`. It used to be written
    as `0x80000 | group`, i.e. always track 8 - right for ARA1, whose track *is*
    8, and wrong for every other slot: the Aloha build's ASS1 patches all read
    page track 8 where stock ASS1 reads 11. Pass the target location's track.
    """
    out = bytearray(payload)
    u, v, w, h = lightmap_rect
    step = inset / lightmap_size
    struct.pack_into('>4f', out, 16, u + step, v + step, w - 2 * step, h - 2 * step)
    for k, (tu, tv) in enumerate(uv):
        struct.pack_into('>2f', out, 32 + 8 * k, tu, tv + 1.0)
    struct.pack_into('>I', out, 412, (track << 16) | texture_group)
    struct.pack_into('>HH', out, 416, texture_rid, lightmap_rid)
    return bytes(out)


def import_course_textures(world, location, texture_group, added, bindings, textures, lightmaps,
                           material_profile='tricky-gc-to-ssx3-gc-v1', track=None):
    """Append the donor textures/lightmaps to the pinned group and bind the added patches.

    added: [(entry, payload)] terrain records in donor order; bindings: tricky_bindings()
    entries in the same order. Returns ({group: records} for every rewritten texture
    group, rebound patches, report).
    """
    if len(added) != len(bindings):
        raise ValueError('Patch and binding counts differ')
    used_textures = sorted({b['texture'] for b in bindings})
    used_lightmaps = sorted({b['lightmap'] for b in bindings})
    if any(not 0 <= t < len(textures) for t in used_textures) or any(not 0 <= l < len(lightmaps) for l in used_lightmaps):
        raise ValueError('Binding refers to an image outside the shape containers')
    loc = world.location(location)
    if not loc['group_start'] <= texture_group < loc['last_group']:
        raise ValueError('Texture group must belong to the target location')
    tex_rid = dict(zip(used_textures, unused_global_rids(world, 9, len(used_textures))))
    lm_rid = dict(zip(used_lightmaps, unused_global_rids(world, 10, len(used_lightmaps))))
    replaced = {}
    group_records = list(world.records(texture_group))
    resident = len(group_records)
    for t in used_textures:
        payload = world_image_record(textures[t])
        group_records.append((dict(kind=9, size=len(payload), track=255, rid=tex_rid[t]), payload))
    from gamecube_materials import convert_lightmap
    transfers = {}
    for l in used_lightmaps:
        converted, transfers[l] = convert_lightmap(lightmaps[l], material_profile)
        payload = world_image_record(converted)
        group_records.append((dict(kind=10, size=len(payload), track=255, rid=lm_rid[l]), payload))
    replaced[texture_group] = group_records
    rebound = []
    for (entry, payload), b in zip(added, bindings):
        lm = lightmaps[b['lightmap']]
        rebound.append((entry, bind_patch(payload, tex_rid[b['texture']], lm_rid[b['lightmap']], texture_group,
                                          b['uv'], b['lightmap_rect'], lightmap_size=lm['width'],
                                          track=entry['track'] if track is None else track)))
    report = dict(texture_group=texture_group, textures={t: tex_rid[t] for t in used_textures},
                  lightmaps={l: lm_rid[l] for l in used_lightmaps},
                  texture_types={t: hex(textures[t]['type']) for t in used_textures},
                  lightmap_types={l: hex(lightmaps[l]['type']) for l in used_lightmaps},
                  lightmap_transfer=transfers, material_profile=material_profile,
                  allocation='new-global-rids', dropped_stock_records={},
                  added_bytes=sum(len(p) + 8 for e, p in group_records[resident:]))
    return replaced, rebound, report


# ---- Decoding for previews (GX tiling) ----

def rgb5a3(v):
    if v & 0x8000:
        return ((v >> 10 & 31) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v & 31) * 255 // 31, 255)
    return ((v >> 8 & 15) * 17, (v >> 4 & 15) * 17, (v & 15) * 17, (v >> 12 & 7) * 255 // 7)


def rgb565(v):
    # GX expands short channels by bit replication, not floor(v * 255 / max).
    r, g, b = v >> 11 & 31, v >> 5 & 63, v & 31
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2), 255)


def decode(img):
    """Row-major RGBA tuples for an image dict."""
    kind, w, h, px = img['type'], img['width'], img['height'], img['pixels']
    out = [(0, 0, 0, 0)] * (w * h)
    if kind in (0x14, 0x15):
        conv = rgb565 if kind == 0x14 else rgb5a3
        i = 0
        for by in range(0, h, 4):
            for bx in range(0, w, 4):
                for y in range(4):
                    for x in range(4):
                        out[(by + y) * w + bx + x] = conv(struct.unpack_from('>H', px, i)[0])
                        i += 2
    elif kind == 0x16:
        i = 0
        for by in range(0, h, 4):
            for bx in range(0, w, 4):
                for y in range(4):
                    for x in range(4):
                        j = 2 * (y * 4 + x)
                        a, r = px[i + j:i + j + 2]
                        g, b = px[i + 32 + j:i + 34 + j]
                        out[(by + y) * w + bx + x] = (r, g, b, a)
                i += 64
    elif kind == 0x19:
        cols = [rgb5a3(struct.unpack_from('>H', img['palette'], i * 2)[0]) for i in range(256)]
        i = 0
        for by in range(0, h, 4):
            for bx in range(0, w, 8):
                for y in range(4):
                    for x in range(8):
                        out[(by + y) * w + bx + x] = cols[px[i]]
                        i += 1
    elif kind == 0x1e:
        i = 0
        for by in range(0, h, 8):
            for bx in range(0, w, 8):
                for sy in (0, 4):
                    for sx in (0, 4):
                        c0, c1 = struct.unpack_from('>HH', px, i)
                        bits = struct.unpack_from('>I', px, i + 4)[0]
                        i += 8
                        p0, p1 = rgb565(c0), rgb565(c1)
                        if c0 > c1:
                            p2 = tuple((2 * a + b) // 3 for a, b in zip(p0, p1))
                            p3 = tuple((a + 2 * b) // 3 for a, b in zip(p0, p1))
                        else:
                            p2 = tuple((a + b) // 2 for a, b in zip(p0, p1))
                            p3 = (0, 0, 0, 0)
                        pal = (p0, p1, p2, p3)
                        for y in range(4):
                            for x in range(4):
                                sel = bits >> (30 - 2 * (y * 4 + x)) & 3
                                out[(by + sy + y) * w + bx + sx + x] = pal[sel]
    else:
        raise ValueError(f'Unsupported type {kind:#x}')
    return out


def to_png(img, path):
    from PIL import Image
    im = Image.new('RGBA', (img['width'], img['height']))
    im.putdata(decode(img))
    im.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('shape', type=Path, help='SHPG container (.gsh)')
    ap.add_argument('--png', type=Path, help='Directory for one PNG per image')
    ap.add_argument('--only', type=int, nargs='*', help='Image indices to export')
    ap.add_argument('--bindings', type=Path, help='NBD: print texture/lightmap usage by the terrain patches')
    args = ap.parse_args()
    images = shape_images(args.shape.read_bytes())
    for img in images:
        if args.only and img['index'] not in args.only:
            continue
        print(f"{img['index']:3} {img['name']!r} type {img['type']:#x} {img['width']}x{img['height']}")
        if args.png:
            args.png.mkdir(parents=True, exist_ok=True)
            to_png(img, args.png / f"{img['index']:03}.png")
    if args.bindings:
        b = tricky_bindings(args.bindings.read_bytes())
        from collections import Counter
        print('textures used:', sorted(Counter(x['texture'] for x in b).items()))
        print('lightmaps used:', sorted(Counter(x['lightmap'] for x in b).items()))


if __name__ == '__main__':
    main()
