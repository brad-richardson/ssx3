#!/usr/bin/env python3
"""Assemble and place SSX 3 course-script ("LUN") programs.

A course's kind-16 script record carries a table of Luno bytecode programs.
The imported course has every one of them replaced by a 36-byte empty return,
so no authored behaviour runs. This module writes a real program back into one
slot, using the format decoded from the stock Snow Jam record
(local/research/startgate/lun-callback-path.md):

    chunk header  16 bytes: magic 0x004E554C, code_end, data_end, length
    code          big-endian words [op][A][B][C]; nine opcodes carry an
                  immediate word (20-23, 29, 36-39)
    functions     16 bytes each: -offset of this record from the chunk start,
                  entry pc (word index), parameter slots, stack entries

Function 0 runs once at course load with slot 0 holding the course object;
storing a closure under a name hash there (SETINDEX) is how the stock course
registers its event handlers. The engine sizes every handler frame from
function 0's parameter count, so it must be at least as large as any handler's.
Handlers are called with (course, nil) and run to completion: there is no wait.
"""
import struct

MAGIC = 0x004E554C
IMMEDIATE_OPCODES = {20, 21, 22, 23, 29, 36, 37, 38, 39}
OP_SETINDEX, OP_LOADNAME, OP_CLOSURE, OP_CALLBUILTIN, OP_RETNIL = 18, 20, 29, 33, 42
OP_PUSH_FLOAT, OP_PUSH_INT, OP_PUSH_BYTE = 38, 39, 40
EMPTY_RETURN = bytes.fromhex('004e554c0000001400000024000000242aff0000ffffffec000000000000000200000000')


def name_hash(name):
    """The engine's string hash (0x801CCFE4): ELF variant over signed bytes."""
    value = 0
    for byte in name.encode():
        if byte >= 128:
            byte -= 256
        value = (value << 4) + byte & 0xffffffff
        high = value & 0xF0000000
        if high:
            value ^= ((high << 9) | (high >> 23)) & 0x1ff
            value ^= high
    return value


def instruction(op, a=0, b=0, c=0, imm=None):
    if not (0 <= op <= 42 and 0 <= a < 256 and 0 <= b < 256 and 0 <= c < 256):
        raise ValueError('Instruction field out of range')
    if (imm is not None) != (op in IMMEDIATE_OPCODES):
        raise ValueError(f'Opcode {op} immediate mismatch')
    return (op, a, b, c, imm)


def closure(dest, function):
    return instruction(OP_CLOSURE, dest, imm=function)


def load_name(dest, name):
    return instruction(OP_LOADNAME, dest, imm=name_hash(name) if isinstance(name, str) else name)


def set_index(table, key, value):
    return instruction(OP_SETINDEX, table, key, value)


def push_int(slot, value):
    return instruction(OP_PUSH_INT, slot, imm=value & 0xffffffff)


def push_byte(slot, value):
    return instruction(OP_PUSH_BYTE, slot, value)


def push_float(slot, value):
    return instruction(OP_PUSH_FLOAT, slot, imm=struct.unpack('>I', struct.pack('>f', value))[0])


def call_builtin(dest, index, argc):
    return instruction(OP_CALLBUILTIN, dest, index, argc)


def return_nil():
    return instruction(OP_RETNIL, 0xff)


def assemble(functions):
    """functions: list of dict(code=[instructions], params=int, stack=int)."""
    words, entries = [], []
    for function in functions:
        entries.append(len(words))
        for op, a, b, c, imm in function['code']:
            words.append(op << 24 | a << 16 | b << 8 | c)
            if imm is not None:
                words.append(imm & 0xffffffff)
    code_end = 16 + 4*len(words)
    data_end = code_end + 16*len(functions)
    out = bytearray(struct.pack('>4I', MAGIC, code_end, data_end, data_end))
    out += struct.pack(f'>{len(words)}I', *words)
    for i, (function, entry) in enumerate(zip(functions, entries)):
        out += struct.pack('>iIII', -(code_end + 16*i), entry, function['params'], function['stack'])
    return bytes(out)


def disassemble(blob):
    """Inverse of assemble, for round-trip checks against stock programs."""
    magic, code_end, data_end, length = struct.unpack_from('>4I', blob, 0)
    if magic != MAGIC or length != data_end or not 16 <= code_end <= data_end <= len(blob):
        raise ValueError('Invalid LUN chunk header')
    if (code_end-16) % 4 or (data_end-code_end) % 16:
        raise ValueError('Invalid LUN chunk sizes')
    words = struct.unpack_from(f'>{(code_end-16)//4}I', blob, 16)
    metas = [struct.unpack_from('>iIII', blob, code_end + 16*i) for i in range((data_end-code_end)//16)]
    for i, (back, entry, _, _) in enumerate(metas):
        if back != -(code_end + 16*i) or entry > len(words):
            raise ValueError('Invalid LUN function record')
    bounds = [m[1] for m in metas] + [len(words)]
    functions = []
    for (_, entry, params, stack), end in zip(metas, bounds[1:]):
        code, pc = [], entry
        while pc < end:
            word = words[pc]
            op, a, b, c = word >> 24, word >> 16 & 0xff, word >> 8 & 0xff, word & 0xff
            imm = None
            pc += 1
            if op in IMMEDIATE_OPCODES:
                imm = words[pc]
                pc += 1
            code.append(instruction(op, a, b, c, imm))
        if pc != end:
            raise ValueError('Function code does not end on its boundary')
        functions.append(dict(code=code, params=params, stack=stack))
    return functions


def program_spans(script):
    """(start, size) of every program slot in a kind-16 script record."""
    if len(script) < 92 or script[:4] != bytes.fromhex('00100000'):
        raise ValueError('Unsupported course script header')
    count, table, end = struct.unpack_from('>3I', script, 56)
    starts = struct.unpack_from(f'>{count}I', script, table)
    if list(starts) != sorted(set(starts)) or starts[0] < table + count*4 or end > len(script):
        raise ValueError('Invalid course program table')
    return [(a, b-a) for a, b in zip(starts, (*starts[1:], end))]


def replace_program(script, index, blob):
    """Write `blob` into program slot `index` in place, zero-padding the slot.

    Slots keep their original spans, so the program must fit. The rest of the
    record -- every other program, the instance definitions and the spline
    binding -- is untouched.
    """
    start, size = program_spans(script)[index]
    if len(blob) > size:
        raise ValueError(f'Program {index} needs {len(blob)} bytes but its slot holds {size}')
    if script[start:start+len(EMPTY_RETURN)] != EMPTY_RETURN:
        raise ValueError(f'Program {index} is not the disabled stub')
    out = bytearray(script)
    out[start:start+size] = blob + bytes(size-len(blob))
    return bytes(out)


def dead_node(oid):
    return [push_int(0, oid), push_byte(1, 0), call_builtin(2, 2, 2)]


def countdown_program(gate_ids, lights_id, rate, probe=False):
    """Register the two countdown handlers the imported course lacks.

    StartlightBegin: attach a texture-flip modifier (builtin 22) to the lights
    so the five-frame countdown sequence advances at `rate` flips per second.
    StartgateOpen: remove every staged instance through builtin 2's DeadNode
    command, the donor's own authored post-countdown state.

    `probe` moves the gate removal to StartlightBegin and leaves only the
    lights for StartgateOpen, so a countdown screenshot shows both effects:
    the canopy gone, the light column present and (if the modifier took)
    advancing. Diagnostic only.
    """
    register = dict(code=[
        closure(2, 1), load_name(3, 'StartgateOpen'), set_index(0, 3, 2),
        closure(2, 2), load_name(3, 'StartlightBegin'), set_index(0, 3, 2),
        return_nil()], params=4, stack=0)
    gates = [oid for oid in gate_ids if oid != lights_id]
    at_open = [lights_id] if probe else gates + [lights_id]
    at_lights = gates if probe else []
    hide = dict(code=sum((dead_node(oid) for oid in at_open), []) + [return_nil()],
                params=3, stack=2)
    # Builtin 22 attaches to the instance's modifier host at +132, which only
    # builtin 0 creates; without it the builtin returns silently. The stock
    # courses always call builtin 0 on an instance before attaching modifiers
    # (local/research/startgate/builtin22-diagnosis.md).
    lights = dict(code=sum((dead_node(oid) for oid in at_lights), []) + [
        push_int(0, lights_id), call_builtin(2, 0, 1),
        push_int(0, lights_id), push_byte(1, 0), push_byte(3, 1), push_float(4, rate),
        call_builtin(2, 22, 4), return_nil()], params=3, stack=4)
    return assemble([register, hide, lights])
