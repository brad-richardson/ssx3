import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import gamecube_lun as lun  # noqa: E402

STOCK = Path(__file__).resolve().parents[1]/'local/research/startgate/host-script.bin'


def test_name_hash_matches_engine_dispatch_hashes():
    assert lun.name_hash('StartgateOpen') == 0x0dfb527e
    assert lun.name_hash('StartlightBegin') == 0x0ebf88fe


def test_assemble_layout_and_round_trip():
    functions = [
        dict(code=[lun.closure(2, 1), lun.load_name(3, 'StartgateOpen'),
                   lun.set_index(0, 3, 2), lun.return_nil()], params=4, stack=0),
        dict(code=[lun.push_int(0, 0x08000CA7), lun.push_byte(1, 0),
                   lun.call_builtin(2, 2, 2), lun.return_nil()], params=3, stack=2),
    ]
    blob = lun.assemble(functions)
    magic, code_end, data_end, length = struct.unpack_from('>4I', blob, 0)
    assert magic == lun.MAGIC and length == data_end == len(blob)
    assert code_end == 16 + 4*(6 + 5)          # two immediates in f0, one in f1
    assert data_end == code_end + 32
    back, entry, params, stack = struct.unpack_from('>iIII', blob, code_end + 16)
    assert (back, entry, params, stack) == (-(code_end+16), 6, 3, 2)
    assert lun.disassemble(blob) == functions


def test_immediate_mismatch_is_refused():
    with pytest.raises(ValueError):
        lun.instruction(lun.OP_RETNIL, imm=1)
    with pytest.raises(ValueError):
        lun.instruction(lun.OP_CLOSURE, 2)


def synthetic_script(spans):
    count = len(spans)
    table = 92
    programs = table + 4*count
    starts, body, at = [], b'', programs
    for size in spans:
        starts.append(at)
        body += lun.EMPTY_RETURN + bytes(size-len(lun.EMPTY_RETURN))
        at += size
    script = bytearray(bytes.fromhex('00100000') + bytes(52))
    script += struct.pack('>3I', count, table, at)
    script += bytes(table-len(script))
    script += struct.pack(f'>{count}I', *starts) + body
    return bytes(script)


def test_replace_program_writes_in_place_and_leaves_the_rest():
    script = synthetic_script([36, 548, 36])
    blob = lun.countdown_program([1, 2], 3, 1.5)
    out = lun.replace_program(script, 1, blob)
    start, size = lun.program_spans(script)[1]
    assert len(out) == len(script)
    assert out[start:start+len(blob)] == blob
    assert not any(out[start+len(blob):start+size])
    assert out[:start] == script[:start] and out[start+size:] == script[start+size:]
    with pytest.raises(ValueError):
        lun.replace_program(script, 0, blob)      # 176 bytes do not fit in 36
    with pytest.raises(ValueError):
        lun.replace_program(out, 1, blob)         # slot is no longer the stub


def test_countdown_program_registers_both_handlers():
    functions = lun.disassemble(lun.countdown_program([0x08000CA7, 0x08000CA8], 0x08000CA9, 1.3))
    register, hide, lights = functions
    assert register['params'] >= max(f['params'] for f in functions)
    names = [c[4] for c in register['code'] if c[0] == lun.OP_LOADNAME]
    assert names == [lun.name_hash('StartgateOpen'), lun.name_hash('StartlightBegin')]
    assert [c for c in hide["code"] if c[0] == lun.OP_CALLBUILTIN] == [(33, 2, 2, 2, None)]*3
    assert [c for c in lights['code'] if c[0] == lun.OP_CALLBUILTIN] == \
        [(33, 2, 0, 1, None), (33, 2, 22, 4, None)]   # modifier host first, then the flip
    assert lights['stack'] == 4 and hide['stack'] == 2


@pytest.mark.skipif(not STOCK.exists(), reason='stock Snow Jam script is local evidence')
def test_every_stock_program_round_trips():
    script = STOCK.read_bytes()
    for start, size in lun.program_spans(script):
        blob = script[start:start+size]
        length = struct.unpack_from('>I', blob, 12)[0]
        assert lun.assemble(lun.disassemble(blob[:length])) == blob[:length]
        assert not any(blob[length:])


def test_probe_variant_moves_the_gate_removal_to_the_lights_event():
    _, hide, lights = lun.disassemble(lun.countdown_program([7, 8, 9], 9, 1.0, probe=True))
    assert [c for c in hide['code'] if c[0] == lun.OP_CALLBUILTIN] == [(33, 2, 2, 2, None)]
    assert [c for c in lights['code'] if c[0] == lun.OP_CALLBUILTIN] == \
        [(33, 2, 2, 2, None)]*2 + [(33, 2, 0, 1, None), (33, 2, 22, 4, None)]
