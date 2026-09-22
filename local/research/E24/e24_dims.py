"""Objective 3 (I-lane relay, I23 H2): are the title movie dims DERIVABLE?

Trace-mining only -- no boot, no probe, nothing extra burned. The 5,040 B the
guest handed to `sceMpegAddBs` are already retained byte-for-byte by E22 and
E23 (`observed/parser-input.bin`, FNV64 0xd2a9588f0e0fd358, first4 000001b3).
Dims, if derivable at all, are derivable from those bytes: 000001b3 IS the
MPEG-2 `sequence_header_code`, and `horizontal_size_value` /
`vertical_size_value` are its first two fields.

This tool proves identity against the committed receipts first, then parses.
"""
import json
from pathlib import Path
from e24_common import E, P, pin, save, sha, utc
from e24_parser_receipt import fnv

ASPECT = {0: 'forbidden', 1: 'square samples (1:1)', 2: '4:3 display',
          3: '16:9 display', 4: '2.21:1 display'}
FRAME_RATE = {0: 'forbidden', 1: '24000/1001 (23.976)', 2: '24', 3: '25',
              4: '30000/1001 (29.97)', 5: '30', 6: '50',
              7: '60000/1001 (59.94)', 8: '60'}
CHROMA = {0: 'reserved', 1: '4:2:0', 2: '4:2:2', 3: '4:4:4'}
START = {0x00: 'picture_start_code', 0xb2: 'user_data_start_code',
         0xb3: 'sequence_header_code', 0xb4: 'sequence_error_code',
         0xb5: 'extension_start_code', 0xb7: 'sequence_end_code',
         0xb8: 'group_start_code'}


class Bits:
    def __init__(self, data, bit=0):
        self.d, self.i = data, bit

    def u(self, n):
        v = 0
        for _ in range(n):
            byte = self.d[self.i >> 3]
            v = (v << 1) | ((byte >> (7 - (self.i & 7))) & 1)
            self.i += 1
        return v


def start_codes(data):
    out = []
    i = 0
    while True:
        j = data.find(b'\x00\x00\x01', i)
        if j < 0 or j + 3 >= len(data):
            break
        out.append((j, data[j + 3]))
        i = j + 3
    return out


def main():
    # --- identity: the SAME bytes E22 and E23 committed ---------------------
    sources = {
        'E22': E.parent / 'E22/observed/parser-input.bin',
        'E23': E.parent / 'E23/observed/parser-input.bin',
        'e23a run dir': P / 'run/e23a-parser/parser-input.bin',
    }
    ident = {}
    payload = None
    for name, path in sources.items():
        if not path.exists():
            ident[name] = dict(present=False)
            continue
        data = path.read_bytes()
        ident[name] = dict(present=True, bytes=len(data), sha256=sha(path),
                           fnv64=hex(fnv(data)), first4=data[:4].hex())
        if payload is None:
            payload = data
        else:
            ident[name]['byte_identical_to_first'] = data == payload
    assert payload is not None, 'no retained payload found'
    # E22 REPORT / E18 committed values.
    assert len(payload) == 5040, len(payload)
    assert sha(sources['E22']) == 'cde8a830265592be927d28ec78c26a27567ce046a7ac161698759e742a1c875a'
    assert fnv(payload) == 0xd2a9588f0e0fd358, hex(fnv(payload))
    assert payload[:4] == bytes.fromhex('000001b3')

    # --- start-code census: what the 5,040 B actually contains --------------
    codes = start_codes(payload)
    census = {}
    for off, code in codes:
        key = START.get(code, 'slice_start_code' if 0x01 <= code <= 0xaf else f'0x{code:02x}')
        census[key] = census.get(key, 0) + 1

    # --- sequence_header (000001b3) -----------------------------------------
    b = Bits(payload, 4 * 8)
    seq = dict(horizontal_size_value=b.u(12), vertical_size_value=b.u(12),
               aspect_ratio_information=b.u(4), frame_rate_code=b.u(4),
               bit_rate_value=b.u(18), marker_bit=b.u(1),
               vbv_buffer_size_value=b.u(10), constrained_parameters_flag=b.u(1))
    seq['load_intra_quantiser_matrix'] = b.u(1)
    if seq['load_intra_quantiser_matrix']:
        b.u(64 * 8)
    seq['load_non_intra_quantiser_matrix'] = b.u(1)
    if seq['load_non_intra_quantiser_matrix']:
        b.u(64 * 8)
    assert seq['marker_bit'] == 1, 'sequence header marker bit not set; parse is unsound'

    # --- sequence_extension / sequence_display_extension (000001b5) ---------
    ext = {}
    for off, code in codes:
        if code != 0xb5:
            continue
        e = Bits(payload, (off + 4) * 8)
        ident_id = e.u(4)
        if ident_id == 1 and 'sequence_extension' not in ext:
            ext['sequence_extension'] = dict(
                offset=off, profile_and_level_indication=e.u(8),
                progressive_sequence=e.u(1), chroma_format=e.u(2),
                horizontal_size_extension=e.u(2), vertical_size_extension=e.u(2),
                bit_rate_extension=e.u(12), marker_bit=e.u(1),
                vbv_buffer_size_extension=e.u(8), low_delay=e.u(1),
                frame_rate_extension_n=e.u(2), frame_rate_extension_d=e.u(5))
        elif ident_id == 2 and 'sequence_display_extension' not in ext:
            row = dict(offset=off, video_format=e.u(3), colour_description=e.u(1))
            if row['colour_description']:
                row.update(colour_primaries=e.u(8), transfer_characteristics=e.u(8),
                           matrix_coefficients=e.u(8))
            row.update(display_horizontal_size=e.u(14), marker_bit=e.u(1),
                       display_vertical_size=e.u(14))
            ext['sequence_display_extension'] = row

    se = ext.get('sequence_extension')
    width = seq['horizontal_size_value'] | ((se['horizontal_size_extension'] << 12) if se else 0)
    height = seq['vertical_size_value'] | ((se['vertical_size_extension'] << 12) if se else 0)
    stream = 'MPEG-2 (sequence_extension present)' if se else 'MPEG-1 (no sequence_extension)'

    out = dict(
        utc=utc(), objective='I23 H2 relay: title movie dims if derivable',
        method='static parse of the ALREADY-RETAINED 5,040 B; no boot, nothing extra burned',
        payload_identity=ident,
        payload_bytes=len(payload), payload_sha256=sha(sources['E22']),
        payload_fnv64=hex(fnv(payload)),
        derivable=True,
        derived_from='sequence_header_code 0x000001b3 at offset 0'
                     + (' + sequence_extension 0x000001b5 id=1' if se else ''),
        dims=dict(width=width, height=height),
        stream_kind=stream,
        sequence_header=seq,
        aspect_ratio=ASPECT.get(seq['aspect_ratio_information'], 'reserved'),
        frame_rate=FRAME_RATE.get(seq['frame_rate_code'], 'reserved'),
        bit_rate_bps=(seq['bit_rate_value'] | ((se['bit_rate_extension'] << 18) if se else 0)) * 400,
        chroma_format=CHROMA.get(se['chroma_format']) if se else None,
        progressive_sequence=se['progressive_sequence'] if se else None,
        extensions=ext,
        start_code_census=census,
        start_codes_first=[dict(offset=o, code=hex(c),
                                name=START.get(c, 'slice' if 0x01 <= c <= 0xaf else '?'))
                           for o, c in codes[:12]],
        start_codes_total=len(codes),
    )
    save('dims.json', out)
    # Standalone replayable vector for the I-lane (H2's other half), carried
    # into this lane with its own receipt so one path serves both requests.
    (E / 'observed').mkdir(exist_ok=True)
    (E / 'observed/parser-input.bin').write_bytes(payload)
    save('observed-vector.json', dict(
        utc=utc(), file='local/research/E24/observed/parser-input.bin',
        **pin(E / 'observed/parser-input.bin'), fnv64=hex(fnv(payload)),
        provenance='byte-identical carry of E22/E23 observed/parser-input.bin '
                   '(the bytes sceMpegAddBs accepted at E18 tick-249)'))
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ('payload_identity', 'start_codes_first')}, indent=2))
    print('# E24 DIMS TAIL COMPLETE')


if __name__ == '__main__':
    main()
