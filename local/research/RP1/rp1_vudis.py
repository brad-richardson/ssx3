#!/usr/bin/env python3
"""RP1: minimal VU micro-code disassembler (upper + lower) for reading one VU1 program.
Source: the micro memory of a PCSX2 T65 VU1 start record (t65-vu1-N.bin).
Usage: rp1_vudis.py <t65-vu1.bin> <start_byte_pc_hex> [count]"""
import sys, struct, importlib.util

spec = importlib.util.spec_from_file_location('t65a', '/Users/brad/dev/ssx3/local/research/T65/t65-analyze.py')
t65 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t65)

BC = 'xyzw'
def dest(w):
    d = (w >> 21) & 0xF
    return ''.join(c for i, c in enumerate('xyzw') if d & (8 >> i))
def vf(n): return 'vf%02d' % n
def vi(n): return 'vi%02d' % n

UP = {}
for i, n in enumerate(('ADD', 'SUB', 'MADD', 'MSUB', 'MAX', 'MINI', 'MUL')):
    for b in range(4):
        UP[i * 4 + b] = n + BC[b]
UP.update({0x1c: 'MULq', 0x1d: 'MAXi', 0x1e: 'MULi', 0x1f: 'MINIi', 0x20: 'ADDq', 0x21: 'MADDq', 0x22: 'ADDi',
           0x23: 'MADDi', 0x24: 'SUBq', 0x25: 'MSUBq', 0x26: 'SUBi', 0x27: 'MSUBi', 0x28: 'ADD', 0x29: 'MADD',
           0x2a: 'MUL', 0x2b: 'MAX', 0x2c: 'SUB', 0x2d: 'MSUB', 0x2e: 'OPMSUB', 0x2f: 'MINI'})
US = {}
for i, n in enumerate(('ADDA', 'SUBA', 'MADDA', 'MSUBA')):
    for b in range(4):
        US[i * 4 + b] = n + BC[b]
US.update({0x10: 'ITOF0', 0x11: 'ITOF4', 0x12: 'ITOF12', 0x13: 'ITOF15', 0x14: 'FTOI0', 0x15: 'FTOI4',
           0x16: 'FTOI12', 0x17: 'FTOI15'})
for b in range(4):
    US[0x18 + b] = 'MULA' + BC[b]
US.update({0x1c: 'MULAq', 0x1d: 'ABS', 0x1e: 'MULAi', 0x1f: 'CLIP', 0x20: 'ADDAq', 0x21: 'MADDAq', 0x22: 'ADDAi',
           0x23: 'MADDAi', 0x24: 'SUBAq', 0x25: 'MSUBAq', 0x26: 'SUBAi', 0x27: 'MSUBAi', 0x28: 'ADDA', 0x29: 'MADDA',
           0x2a: 'MULA', 0x2c: 'SUBA', 0x2d: 'MSUBA', 0x2e: 'OPMULA', 0x2f: 'NOP'})

def upper(w):
    op = w & 0x3F
    ft, fs, fd = (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31
    flags = ''.join(f for b, f in ((31, 'I'), (30, 'E'), (29, 'M'), (28, 'D'), (27, 'T')) if w >> b & 1)
    d = dest(w)
    if op >= 0x3c:
        idx = (((w >> 6) & 31) << 2) | (op & 3)
        n = US.get(idx, 'U?%02x' % idx)
        if n == 'NOP':
            s = 'nop'
        elif n.startswith(('ITOF', 'FTOI', 'ABS')):
            s = '%s.%s %s, %s' % (n, d, vf(ft), vf(fs))
        elif n == 'CLIP':
            s = 'clipw.xyz %s, %s' % (vf(fs), vf(ft))
        elif n[-1] in BC and n[:-1] in ('ADDA', 'SUBA', 'MADDA', 'MSUBA', 'MULA'):
            s = '%s.%s ACC, %s, %s%s' % (n, d, vf(fs), vf(ft), n[-1])
        elif n[-1] in 'qi':
            s = '%s.%s ACC, %s, %s' % (n, d, vf(fs), n[-1].upper())
        else:
            s = '%s.%s ACC, %s, %s' % (n, d, vf(fs), vf(ft))
    else:
        n = UP.get(op, 'U?%02x' % op)
        if n[-1] in BC and len(n) > 1 and n[:-1] in ('ADD', 'SUB', 'MADD', 'MSUB', 'MAX', 'MINI', 'MUL'):
            s = '%s.%s %s, %s, %s%s' % (n, d, vf(fd), vf(fs), vf(ft), n[-1])
        elif n[-1] in 'qi':
            s = '%s.%s %s, %s, %s' % (n, d, vf(fd), vf(fs), n[-1].upper())
        else:
            s = '%s.%s %s, %s, %s' % (n, d, vf(fd), vf(fs), vf(ft))
    return ('[%s] ' % flags if flags else '') + s

LS = {0x30: 'MOVE', 0x31: 'MR32', 0x34: 'LQI', 0x35: 'SQI', 0x36: 'LQD', 0x37: 'SQD', 0x38: 'DIV', 0x39: 'SQRT',
      0x3a: 'RSQRT', 0x3b: 'WAITQ', 0x3c: 'MTIR', 0x3d: 'MFIR', 0x3e: 'ILWR', 0x3f: 'ISWR', 0x40: 'RNEXT',
      0x41: 'RGET', 0x42: 'RINIT', 0x43: 'RXOR', 0x64: 'MFP', 0x68: 'XTOP', 0x69: 'XITOP', 0x6c: 'XGKICK',
      0x70: 'ESADD', 0x71: 'ERSADD', 0x72: 'ELENG', 0x73: 'ERLENG', 0x74: 'EATANxy', 0x75: 'EATANxz', 0x76: 'ESUM',
      0x78: 'ESQRT', 0x79: 'ERSQRT', 0x7a: 'ERCPR', 0x7b: 'WAITP', 0x7c: 'ESIN', 0x7d: 'EATAN', 0x7e: 'EEXP'}
LO = {0x00: 'LQ', 0x01: 'SQ', 0x04: 'ILW', 0x05: 'ISW', 0x08: 'IADDIU', 0x09: 'ISUBIU', 0x10: 'FCEQ', 0x11: 'FCSET',
      0x12: 'FCAND', 0x13: 'FCOR', 0x14: 'FSEQ', 0x15: 'FSSET', 0x16: 'FSAND', 0x17: 'FSOR', 0x18: 'FMEQ',
      0x1a: 'FMAND', 0x1b: 'FMOR', 0x1c: 'FCGET', 0x20: 'B', 0x21: 'BAL', 0x24: 'JR', 0x25: 'JALR', 0x28: 'IBEQ',
      0x29: 'IBNE', 0x2c: 'IBLTZ', 0x2d: 'IBGTZ', 0x2e: 'IBLEZ', 0x2f: 'IBGEZ'}

def s11(w):
    v = w & 0x7FF
    return v - 0x800 if v & 0x400 else v

def lower(w, pc):
    it, is_, id_ = (w >> 16) & 31, (w >> 11) & 31, (w >> 6) & 31
    d = dest(w)
    fsf, ftf = (w >> 21) & 3, (w >> 23) & 3
    if (w >> 25) == 0x40:
        op = w & 0x3F
        if op < 0x3c:
            n = {0x30: 'IADD', 0x31: 'ISUB', 0x32: 'IADDI', 0x34: 'IAND', 0x35: 'IOR'}.get(op, 'L?%02x' % op)
            if n == 'IADDI':
                imm = (w >> 6) & 31
                imm = imm - 32 if imm & 16 else imm
                return 'iaddi %s, %s, %d' % (vi(it), vi(is_), imm)
            return '%s %s, %s, %s' % (n.lower(), vi(id_), vi(is_), vi(it))
        idx = (((w >> 6) & 31) << 2) | (op & 3)
        n = LS.get(idx, 'LS?%02x' % idx)
        if n in ('MOVE', 'MR32'):
            return '%s.%s %s, %s' % (n.lower(), d, vf(it), vf(is_))
        if n in ('LQI', 'LQD'):
            return '%s.%s %s, (%s%s)' % (n.lower(), d, vf(it), vi(is_), '++' if n == 'LQI' else '--')
        if n in ('SQI', 'SQD'):
            return '%s.%s %s, (%s%s)' % (n.lower(), d, vf(is_), vi(it), '++' if n == 'SQI' else '--')
        if n in ('DIV', 'RSQRT'):
            return '%s Q, %s%s, %s%s' % (n.lower(), vf(is_), BC[fsf], vf(it), BC[ftf])
        if n == 'SQRT':
            return 'sqrt Q, %s%s' % (vf(it), BC[ftf])
        if n in ('MTIR',):
            return 'mtir %s, %s%s' % (vi(it), vf(is_), BC[fsf])
        if n in ('MFIR',):
            return 'mfir.%s %s, %s' % (d, vf(it), vi(is_))
        if n in ('ILWR', 'ISWR'):
            return '%s.%s %s, (%s)' % (n.lower(), d, vi(it), vi(is_))
        if n in ('XGKICK', 'XTOP', 'XITOP'):
            return '%s %s' % (n.lower(), vi(is_) if n == 'XGKICK' else vi(it))
        if n == 'MFP':
            return 'mfp.%s %s, P' % (d, vf(it))
        if n in ('WAITQ', 'WAITP'):
            return n.lower()
        return '%s %s%s (it=%d)' % (n.lower(), vf(is_), BC[fsf], it)
    op = w >> 25
    n = LO.get(op, 'L?%02x' % op)
    if n in ('LQ', 'SQ'):
        if n == 'LQ':
            return 'lq.%s %s, %d(%s)' % (d, vf(it), s11(w), vi(is_))
        return 'sq.%s %s, %d(%s)' % (d, vf(is_), s11(w), vi(it))
    if n in ('ILW', 'ISW'):
        return '%s.%s %s, %d(%s)' % (n.lower(), d, vi(it), s11(w), vi(is_))
    if n in ('IADDIU', 'ISUBIU'):
        imm = ((w >> 10) & 0x7800) | (w & 0x7FF)
        return '%s %s, %s, %d' % (n.lower(), vi(it), vi(is_), imm)
    if n in ('B', 'BAL', 'IBEQ', 'IBNE', 'IBLTZ', 'IBGTZ', 'IBLEZ', 'IBGEZ'):
        tgt = (pc + 8 + s11(w) * 8) & 0x3FFF
        if n in ('B',):
            return 'b 0x%x' % tgt
        if n == 'BAL':
            return 'bal %s, 0x%x' % (vi(it), tgt)
        if n in ('IBEQ', 'IBNE'):
            return '%s %s, %s, 0x%x' % (n.lower(), vi(it), vi(is_), tgt)
        return '%s %s, 0x%x' % (n.lower(), vi(is_), tgt)
    if n in ('JR', 'JALR'):
        return '%s %s' % (n.lower(), vi(is_)) if n == 'JR' else 'jalr %s, %s' % (vi(it), vi(is_))
    if n.startswith('F'):
        if n in ('FCAND', 'FCOR', 'FCEQ', 'FCSET'):
            return '%s vi01, 0x%06x' % (n.lower(), w & 0xFFFFFF)
        if n == 'FCGET':
            return 'fcget %s' % vi(it)
        return '%s %s, %s, 0x%x' % (n.lower(), vi(it), vi(is_), ((w >> 10) & 0x800) | (w & 0x7FF))
    return '%s raw=%08x' % (n.lower(), w)

def main():
    recs = t65.read_dump(sys.argv[1])
    start = int(sys.argv[2], 16)
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    micro = None
    for r in recs:
        if r['micro'] is not None and r['tpc'] * 8 == start:
            micro = r['micro']
            break
    if micro is None:
        micro = next(r['micro'] for r in recs if r['micro'] is not None)
    for k in range(count):
        pc = start + k * 8
        lo, up = struct.unpack_from('<II', micro, pc)
        l = '' if (up >> 31) & 1 else lower(lo, pc)
        if (up >> 31) & 1:
            l = 'loi 0x%08x (%g)' % (lo, struct.unpack('<f', struct.pack('<I', lo))[0])
        print('%04x: %-44s | %s' % (pc, upper(up), l))

if __name__ == '__main__':
    main()
