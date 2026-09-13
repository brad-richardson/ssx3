#!/usr/bin/env python3
"""Check the captured-frame prerequisite, keeping renderer acceptance closed.

Default exit status is nonzero until renderer isolation and same-frame replay
fidelity are implemented. --capture-only checks only the original capture and
three private ordered decode passes; success does not authorize replay rendering.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib


SIDE_EFFECTS = ('draw_done', 'tokens', 'efb_copies', 'xfb_copies', 'tmem_loads', 'bbox_writes')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_info(path):
    """Read the pinned little-endian Dolphin FIFO v6 container, with bounds checks."""
    data = path.read_bytes()

    def unpack(fmt, offset):
        size = struct.calcsize(fmt)
        if offset < 0 or offset + size > len(data):
            raise ValueError('Truncated FIFO container')
        return struct.unpack_from(fmt, data, offset)

    def span(offset, size):
        if offset > len(data) or size > len(data) - offset:
            raise ValueError('FIFO range outside container')
        return data[offset:offset + size]

    file_id, version, minimum = unpack('<III', 0)
    if file_id != 0x0D01F1F0 or version != 6 or minimum > 6:
        raise ValueError('Expected the pinned Dolphin FIFO v6 container')
    for offset, count in ((12, 256), (24, 256), (36, 4096), (48, 88)):
        position, size = unpack('<QI', offset)
        if size != count:
            raise ValueError('Unexpected initial register size')
        span(position, size * 4)
    frames_offset, frame_count = unpack('<QI', 60)
    if frame_count != 1:
        raise ValueError('Expected exactly one captured frame')
    tmem_offset, tmem_size = unpack('<QI', 76)
    if tmem_size != 1024 * 1024:
        raise ValueError('Unexpected initial TMEM size')
    span(tmem_offset, tmem_size)
    fifo_offset, fifo_size, fifo_start, fifo_end, updates_offset, updates_count = unpack(
        '<QIIIQI', frames_offset)
    fifo = span(fifo_offset, fifo_size)
    if not fifo or not updates_count:
        raise ValueError('Empty FIFO or resource capture')
    span(updates_offset, updates_count * 24)
    previous = 0
    for i in range(updates_count):
        position, address, offset, size, kind = unpack('<IIQIB3x', updates_offset + i * 24)
        if not previous <= position <= fifo_size:
            raise ValueError('Unordered or out-of-range memory update')
        if kind not in (1, 2, 4, 8):
            raise ValueError('Unknown recorded memory update kind')
        span(offset, size)
        previous = position
    return dict(sha256=hashlib.sha256(data).hexdigest(), fifo_sha256=hashlib.sha256(fifo).hexdigest(),
                bytes=fifo_size, memory_updates=updates_count, fifo_start=fifo_start, fifo_end=fifo_end)


def png_info(path):
    """Decode Dolphin's noninterlaced 8-bit RGB/RGBA PNGs without optional packages."""
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected a PNG screenshot')
    position, header, ended = 8, None, False
    compressed = bytearray()
    while position < len(data):
        if position + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        size, kind = struct.unpack_from('>I4s', data, position)
        end = position + 12 + size
        if end > len(data):
            raise ValueError('PNG chunk extends beyond file')
        payload = data[position + 8:end - 4]
        if zlib.crc32(kind + payload) != struct.unpack_from('>I', data, end - 4)[0]:
            raise ValueError('PNG chunk CRC mismatch')
        if kind == b'IHDR':
            if header is not None or position != 8 or size != 13:
                raise ValueError('Invalid PNG header')
            header = struct.unpack('>IIBBBBB', payload)
        elif header is None:
            raise ValueError('PNG header must be first')
        elif kind == b'IDAT':
            compressed.extend(payload)
        elif kind == b'IEND':
            if size or end != len(data):
                raise ValueError('Invalid PNG end')
            ended = True
        elif not kind[0] & 0x20:
            raise ValueError('Unsupported critical PNG chunk')
        position = end
    if not ended or header is None:
        raise ValueError('Incomplete PNG screenshot')
    width, height, depth, color, compression, filtering, interlace = header
    if not (width > 0 and height > 0 and width * height <= 16_777_216):
        raise ValueError('Invalid or oversized screenshot dimensions')
    if depth != 8 or color not in (2, 6) or compression or filtering or interlace:
        raise ValueError('Expected a noninterlaced 8-bit RGB/RGBA screenshot')
    bpp = 3 if color == 2 else 4
    stride = width * bpp
    expected = (stride + 1) * height
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, expected + 1)
    if len(raw) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError('PNG pixel data size mismatch')
    previous = bytearray(stride)
    digest = hashlib.sha256()
    for y in range(height):
        offset = y * (stride + 1)
        method = raw[offset]
        if method > 4:
            raise ValueError('Invalid PNG filter')
        row = bytearray(raw[offset + 1:offset + 1 + stride])
        if method:
            for x in range(stride):
                left = row[x - bpp] if x >= bpp else 0
                up = previous[x]
                corner = previous[x - bpp] if x >= bpp else 0
                if method == 1:
                    predictor = left
                elif method == 2:
                    predictor = up
                elif method == 3:
                    predictor = (left + up) // 2
                else:
                    base = left + up - corner
                    distances = (abs(base-left), abs(base-up), abs(base-corner))
                    predictor = (left, up, corner)[distances.index(min(distances))]
                row[x] = (row[x] + predictor) & 255
        if bpp == 4:
            digest.update(row)
        else:
            rgba = bytearray(width * 4)
            for x in range(width):
                rgba[x*4:x*4+3] = row[x*3:x*3+3]
                rgba[x*4+3] = 255
            digest.update(rgba)
        previous = row
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(),
                pixels_sha256=digest.hexdigest(), width=width, height=height)


def assess(rows, capture, reference, candidates=()):
    events = [r for r in rows if r.get('event') == 'replay']
    expected = ['record_start', 'reference_requested', 'recorded', 'capture_saved',
                'audit', 'audit', 'audit', 'audit_complete', 'blocked']
    if [r.get('action') for r in events] != expected:
        raise ValueError('Missing ordered capture, reference, or private-audit evidence')
    if any(r.get('schema') != 2 or r.get('render_execution') is not False for r in events):
        raise ValueError('Unsupported or unsafe replay evidence')
    if any(not isinstance(r.get('wall'), (float, int)) or not math.isfinite(r['wall']) for r in events):
        raise ValueError('Invalid event clock')
    if any(b['wall'] < a['wall'] for a, b in zip(events, events[1:])):
        raise ValueError('Nonmonotonic replay events')
    request, recorded = events[1:3]
    for r in (request, recorded):
        if (r.get('frame_boundaries') != 2 or type(r.get('reference_frame')) is not int or
                type(r.get('reference_present')) is not int or r['reference_frame'] <= 0 or
                r['reference_present'] <= 0):
            raise ValueError('Reference was not bound to the recorded frame present')
    if any(request[k] != recorded[k] for k in ('reference_frame', 'reference_present')):
        raise ValueError('Reference and captured frame identities differ')
    audits = events[4:7]
    if any(r.get('pass') != i or r.get('ok') is not True or r.get('private_memory') is not True or
           r.get('initial_state_reset') is not True for i, r in enumerate(audits)):
        raise ValueError('Each audit needs fresh private memory and initial registers')
    keys = ('commands', 'primitives', 'indexed_loads', 'indexed_bytes_hash', *SIDE_EFFECTS)
    if any(any(r.get(k) != audits[0].get(k) for k in keys) for r in audits[1:]):
        raise ValueError('Repeated private audits disagree')
    if any(type(audits[0].get(k)) is not int or audits[0][k] <= 0
           for k in ('commands', 'primitives', 'indexed_loads', 'xfb_copies')):
        raise ValueError('No complete scene command stream in capture')
    if events[-1].get('reason') != 'renderer_isolation_and_pixel_fidelity_unimplemented':
        raise ValueError('Unexpected renderer isolation gate')
    container = capture_info(capture)
    if any(recorded.get(k) != container[k] for k in ('bytes', 'memory_updates', 'fifo_start', 'fifo_end')):
        raise ValueError('FIFO artifact does not match recorded metadata')
    original = png_info(reference)
    comparisons = []
    for candidate in candidates:
        if candidate.resolve() == reference.resolve() or candidate.samefile(reference):
            raise ValueError('A replay capture must be a separate artifact')
        info = png_info(candidate)
        info['png_bytes_identical'] = info['sha256'] == original['sha256']
        info['pixels_equal'] = all(info[k] == original[k] for k in ('pixels_sha256', 'width', 'height'))
        info['same_frame_provenance_verified'] = False
        comparisons.append(info)
    return dict(schema=1, capture_gate_passed=True, replay_accepted=False,
                guest_render_isolation_verified=False, original_frame_fidelity_verified=False,
                reference_request_bound_to_present=True, reference_image_frame_verified=False,
                blocked_reasons=['renderer isolation is not implemented',
                                 'PNG encoder frame identity is not recorded',
                                 'no isolated replay image bound to the original frame'],
                capture=container, reference=original, reference_frame=request['reference_frame'],
                reference_present=request['reference_present'], private_audit_passes=len(audits),
                commands=audits[0]['commands'], primitives=audits[0]['primitives'],
                observed_side_effect_commands={k: audits[0][k] for k in SIDE_EFFECTS},
                candidate_comparisons=comparisons,
                scope='Private command/resource ordering audit; no vertex/texture/EFB execution or GPU purity claim')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, action='append', default=[])
    parser.add_argument('--capture-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.events.read_text().splitlines()]
    result = assess(rows, Path(str(args.events) + '.fifo'), args.reference, args.candidate)
    result['events_sha256'] = sha(args.events)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as output:
            output.write(text)
    print(text, end='')
    raise SystemExit(0 if args.capture_only and result['capture_gate_passed'] else 1)


if __name__ == '__main__':
    main()
