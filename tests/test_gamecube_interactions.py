import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import gamecube_interactions as gi  # noqa: E402
import gamecube_lun as lun  # noqa: E402


def synthetic_script(instances=(0, 1, 1, 2, 2), definitions=3, class_rows=4, stub_spans=(36, 36, 36, 548, 120, 36)):
    """A kind-16 record with the header fields the binder reads."""
    load = [8 << 24 | i for i in (0, 1, 3)]
    load_at = 96
    class_at = load_at + 4*len(load)
    table_at = class_at + 24*class_rows                      # program table
    programs_at = table_at + 4*len(stub_spans)
    starts, body, at = [], b'', programs_at
    for span in stub_spans:
        starts.append(at)
        body += lun.EMPTY_RETURN + bytes(span-len(lun.EMPTY_RETURN))
        at += span
    programs_end = at
    base = programs_end                                      # definitions base
    defs = b''
    for d in range(definitions):
        flags = 0x00210000 if d else 0x00010000
        collision = 0x08000000 | d if d else 0xffffffff
        defs += struct.pack('>4I3f', 0, flags, 0xffffffff, collision, 1e30, 0, 0)
    ordinals_at = base + len(defs)
    ordinals = struct.pack(f'>{len(instances)}H', *instances)
    pad = -(ordinals_at+len(ordinals)) % 4
    offsets_at = ordinals_at + len(ordinals) + pad
    offsets = struct.pack(f'>{definitions}I', *(28*d for d in range(definitions)))
    spline_at = offsets_at + len(offsets)
    script = bytearray(bytes.fromhex('00100000') + bytes(12))
    script += struct.pack('>4I', len(load), load_at, class_rows, class_at)
    script += bytes(56-len(script))
    script += struct.pack('>3I', len(stub_spans), table_at, programs_end)   # word 64 doubles as defs base
    script += struct.pack('>6I', len(instances), ordinals_at, definitions, offsets_at, 0, spline_at)
    script += bytes(load_at-len(script))
    script += struct.pack(f'>{len(load)}I', *load)
    rows = [(0xffffffff,)*6 for _ in range(class_rows)]
    rows[0] = (0xffffffff, 8 << 24 | 1, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff)  # a used row
    for row in rows:
        script += struct.pack('>6I', *row)
    script += struct.pack(f'>{len(stub_spans)}I', *starts) + body + defs + ordinals + bytes(pad) + offsets
    assert len(script) == spline_at
    return bytes(script)


def test_binds_blocks_to_a_new_class_row_and_program():
    script = synthetic_script()
    out, report = gi.bind_pushables(script, 8, {1: 0.2, 2: 0.2, 3: 0.2})
    h = gi.header(out)
    assert report['class_row'] == 1 and report['class_oid'] == 0x01000001
    assert report['program_slot'] == 4                       # smallest free stub that fits, not 0/1/3
    assert h['definitions'] == 5 and h['count'] == 5
    ordinals = struct.unpack_from(f'>{h["count"]}H', out, h['table'])
    assert ordinals == (0, 3, 3, 4, 2)                       # 1,2 shared def 1 -> clone 3; 3 had def 2 -> clone 4
    starts = struct.unpack_from(f'>{h["definitions"]}I', out, h['offsets'])
    clone = out[h['base']+starts[3]:h['base']+starts[3]+28]
    original = script[gi.header(script)['base']+28:gi.header(script)['base']+56]
    assert clone[:8] == original[:8] and clone[12:] == original[12:]
    assert struct.unpack_from('>I', clone, 8)[0] == 0x01000001
    row = struct.unpack_from('>6I', out, h['class_at']+24)
    assert row[gi.CREATE_SLOT] == 8 << 24 | 4 and row.count(0xffffffff) == 5
    start, span = lun.program_spans(out)[4]
    program = lun.disassemble(out[start:start+report['program_size']])
    assert [c for c in program[0]['code'] if c[0] == lun.OP_CALLBUILTIN] == [(33, 2, 6, 5, None)]
    # Everything before the definitions is untouched except the class row and program slot.
    hs = gi.header(script)
    assert out[:68] == script[:68] and out[92:hs['class_at']+24] == script[92:hs['class_at']+24]
    assert out[hs['class_at']+48:start] == script[hs['class_at']+48:start]


def test_refuses_placements_that_already_carry_a_class_or_lie_outside_the_table():
    script = synthetic_script()
    with pytest.raises(ValueError):
        gi.bind_pushables(script, 8, {9: 0.2})
    out, _ = gi.bind_pushables(script, 8, {1: 0.2})
    with pytest.raises(ValueError):
        gi.bind_pushables(out, 8, {1: 0.2})
    with pytest.raises(ValueError):
        gi.bind_pushables(script, 8, {1: 0.2, 2: 0.5})   # one program per restitution only


def test_teeter_program_matches_the_stock_shape():
    program = lun.disassemble(gi.teeter_program(0.2))
    assert len(program) == 1 and program[0]['params'] == 3 and program[0]['stack'] == 5
    ops = [c[0] for c in program[0]['code']]
    assert ops == [38, 40, 38, 38, 38, 33, 42]
