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


STOCK_WORLD = Path(__file__).resolve().parents[1]/'local/game/gxbe69-stock/files/data/worlds/bam.big'
DONOR_GSF = Path(__file__).resolve().parents[1]/'local/source/gamecube/tricky/gari.gsf'
DONOR_NBD = Path(__file__).resolve().parents[1]/'local/source/gamecube/tricky/gari.nbd'


def test_shatter_program_matches_the_stock_shape():
    program = lun.disassemble(gi.shatter_program([0x08000924, 0x0800092c]))
    assert len(program) == 1 and program[0]['params'] == 3 and program[0]['stack'] == 52
    code = program[0]['code']
    calls = [c for c in code if c[0] == lun.OP_CALLBUILTIN]
    # The particle block is emitted while the node is still alive, then the pane
    # and its overlay are removed with builtin 2 command 0 (DeadNode).
    assert calls == [(33, 2, 26, 52, None), (33, 2, 2, 2, None), (33, 2, 2, 2, None)]
    removals = [c for c in code if c[0] == lun.OP_PUSH_INT]
    assert [c[4] for c in removals] == [0x08000924, 0x0800092c]
    assert code.index(calls[0]) < code.index(removals[0])
    # Command 0 = DeadNode; the particle block also pushes slot 1 with 0 once.
    assert [c for c in code if c[0] == lun.OP_PUSH_BYTE and c[1] == 1] == [(40, 1, 0, 0, None)]*3
    with pytest.raises(ValueError):
        gi.shatter_program([])


def test_shatter_program_carries_debris_pieces_when_they_exist():
    program = lun.disassemble(gi.shatter_program([7], pieces=[(0x0800000e, 20)]))[0]
    calls = [c for c in program['code'] if c[0] == lun.OP_CALLBUILTIN]
    assert calls == [(33, 2, 26, 52, None), (33, 2, 3, 3, None), (33, 2, 44, 1, None),
                     (33, 2, 2, 2, None)]


@pytest.mark.skipif(not STOCK_WORLD.exists(), reason='stock world archive is local evidence')
def test_particle_block_reproduces_stock_abc1_program_171():
    """The 52-argument builtin 26 template must be the stock bytes, not a paraphrase."""
    import gamecube_world  # noqa: E402  (local evidence only)
    world = gamecube_world.World(STOCK_WORLD.read_bytes())
    location = [l for l in world.index['locations'] if l['name'] == 'ABC1'][0]
    script = [p for g in range(location['group_start'], location['last_group']+1)
              for e, p in world.records(g) if e['kind'] == 16][0]
    start, _ = lun.program_spans(script)[171]
    stock = script[start:start+struct.unpack_from('>I', script, start+12)[0]]
    code = [lun.push_byte(1, 3), lun.call_builtin(2, 2, 1)]          # RestoreNode(self)
    for oid, rate in ((0x0600008e, 20), (0x06000584, 15), (0x06000257, 20), (0x060008f3, 15)):
        code += gi.debris_block(oid, rate) + gi.particle_block()
    assert lun.assemble([dict(code=code+[lun.return_nil()], params=3, stack=52)]) == stock


def glass_script():
    # Panes 3 and 4 share definition 0: drawn, no collision resource, which is
    # exactly the shape the imported LCD panes have.
    return synthetic_script(instances=(0, 1, 1, 0, 0),
                            stub_spans=(36, 36, 36, 548, 120, 360, 400, 36))


def test_binds_each_pane_to_its_own_bounds_volume_definition():
    script = glass_script()
    out, report = gi.bind_glass(script, 8, {3: [1], 4: []})
    h = gi.header(out)
    assert report['class_rows'] == [1, 2] and report['program_slots'] == [5, 6]
    panes = report['panes']
    assert panes['3']['removes'] == [1, 3] and panes['4']['removes'] == [4]
    # Both panes shared definition 0, but they carry different class oids, so two clones.
    assert h['definitions'] == 5
    assert [(panes[p]['cloned_from'], panes[p]['definition']) for p in ('3', '4')] == [(0, 3), (0, 4)]
    ordinals = struct.unpack_from(f'>{h["count"]}H', out, h['table'])
    assert ordinals == (0, 1, 1, 3, 4)
    starts = struct.unpack_from(f'>{h["definitions"]}I', out, h['offsets'])
    for index, pane in ((3, '3'), (4, '4')):
        clone = out[h['base']+starts[index]:h['base']+starts[index]+28]
        kind, flags, class_oid, collision = struct.unpack_from('>4I', clone)
        assert kind == gi.DEF_KIND_BOUNDS_VOLUME and flags == gi.DEF_FLAGS_DRAW_COLLIDE
        assert class_oid == panes[pane]['class_oid'] and collision == 0xffffffff
    for pane in panes.values():
        row = struct.unpack_from('>6I', out, h['class_at']+24*pane['class_row'])
        assert row[gi.CONTACT_SLOT] == 8 << 24 | pane['program_slot']
        assert row.count(0xffffffff) == 5
        start, _ = lun.program_spans(out)[pane['program_slot']]
        assert out[start:start+pane['program_size']] == bytes.fromhex(pane['program'])


def test_glass_refuses_empty_targets_and_placements_outside_the_table():
    with pytest.raises(ValueError):
        gi.bind_glass(glass_script(), 8, {})
    with pytest.raises(ValueError):
        gi.bind_glass(glass_script(), 8, {99: []})
    with pytest.raises(ValueError):    # definition 2 names a collision resource
        gi.bind_glass(synthetic_script(stub_spans=(36, 36, 36, 548, 120, 360, 400, 36)), 8, {3: []})


def test_pushables_and_glass_can_share_one_script():
    script = glass_script()
    script, _ = gi.bind_pushables(script, 8, {1: 0.2})
    out, report = gi.bind_glass(script, 8, {3: [1]})
    assert report['class_rows'] == [2] and report['program_slots'] == [5]
    row = struct.unpack_from('>6I', out, gi.header(out)['class_at']+24)
    assert row[gi.CREATE_SLOT] == 8 << 24 | 4      # the pushable binding survives


@pytest.mark.skipif(not (DONOR_GSF.exists() and DONOR_NBD.exists()),
                    reason='donor Garibaldi assets are local evidence')
def test_donor_breakables_are_the_lcd_screen_logos():
    from gamecube_scenery import TrickyScenery  # noqa: E402  (local evidence only)
    gsf = DONOR_GSF.read_bytes()
    scene = TrickyScenery(DONOR_NBD.read_bytes(), gsf)
    entries = gi.breakable_logos(gsf, scene)
    assert len(entries) == 10 and all(e['function'].startswith('BreakLogo') for e in entries)
    for entry in entries:
        play = scene.gameplay[entry['pane']]
        assert play['collision_mode'] == 2 and play['visible'] and play['effect_slot'] >= 0
        assert len(entry['reveal']) == 1 and entry['pane'] in entry['hide']
        assert len(entry['hide']) == 2          # the pane and its scan-line overlay
    assert {scene.instances[e['pane']]['model'] for e in entries} == {48, 87, 89, 133, 153}
