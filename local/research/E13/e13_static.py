#!/usr/bin/env python3
"""E13 read-only ELF/OUT miner, inherited from trusted EF decoder; standard library only, never boots or builds.

ELF virtual mapping follows AC1/ac1_dis.py. OUT comments are accepted only
after their raw instruction word matches the ELF. Unknown words remain raw;
the output never silently stops at R5900 instructions. Immediate scans are
syntactic candidates, not an assertion of alias-analysis completeness.
"""
import argparse
import bisect
import csv
import hashlib
import re
import struct
from pathlib import Path

ROOT = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1')
REG = 'zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split()
MEM = {0x1e:'lq', 0x1f:'sq', 0x20:'lb', 0x21:'lh', 0x22:'lwl',
       0x23:'lw', 0x24:'lbu', 0x25:'lhu', 0x26:'lwr', 0x27:'lwu',
       0x28:'sb', 0x29:'sh', 0x2a:'swl', 0x2b:'sw', 0x2c:'sdl',
       0x2d:'sdr', 0x2e:'swr', 0x31:'lwc1', 0x36:'lqc2', 0x37:'ld',
       0x39:'swc1', 0x3e:'sqc2', 0x3f:'sd'}


class Elf:
    def __init__(self, root):
        self.root = root
        self.path = root / 'SLUS_207.72'
        self.data = self.path.read_bytes()
        assert self.data[:6] == b'\x7fELF\x01\x01'
        phoff = self.u32(0x1c)
        entsize, count = struct.unpack_from('<HH', self.data, 0x2a)
        self.segs = [struct.unpack_from('<8I', self.data, phoff+i*entsize)
                     for i in range(count)]
        shoff = self.u32(0x20)
        size, count, namesidx = struct.unpack_from('<HHH', self.data, 0x2e)
        sections = [struct.unpack_from('<10I', self.data, shoff+i*size)
                    for i in range(count)]
        names = sections[namesidx]
        strings = self.data[names[4]:names[4]+names[5]]
        self.sections = {}
        for s in sections:
            name = strings[s[0]:].split(b'\0', 1)[0].decode()
            self.sections[name] = s
        self.text = self.sections['.text']
        with (root / 'ssx3-functions.csv').open() as f:
            self.funcs = sorted((int(r['start'], 0), int(r['end'], 0), r['name'])
                                for r in csv.DictReader(f))
        self.starts = [r[0] for r in self.funcs]
        self.comments = {}
        self.files = {}

    def u32(self, off):
        return struct.unpack_from('<I', self.data, off)[0]

    def off(self, pc):
        for typ, off, va, pa, fs, ms, flags, align in self.segs:
            if typ == 1 and va <= pc < va+fs:
                return off+pc-va
        return None

    def word(self, pc):
        off = self.off(pc)
        return None if off is None else self.u32(off)

    def owner(self, pc):
        i = bisect.bisect_right(self.starts, pc)-1
        if i >= 0 and self.funcs[i][0] <= pc < self.funcs[i][1]:
            return self.funcs[i]
        return None

    def comment(self, pc):
        owner = self.owner(pc)
        if owner and owner[0] not in self.files:
            path = self.root / 'output' / f'{owner[2]}_0x{owner[0]:x}.cpp'
            self.files[owner[0]] = path
            if path.exists():
                for line in path.read_text().splitlines():
                    m = re.search(r'// (0x[0-9a-f]+): (0x[0-9a-f]+)\s+(.*)', line)
                    if m:
                        addr, word = int(m[1], 16), int(m[2], 16)
                        if self.word(addr) != word:
                            raise ValueError(f'ELF/OUT mismatch {path} {addr:#x}')
                        self.comments.setdefault(addr, m[3].replace(' (Delay Slot)', ''))
        return self.comments.get(pc)

    def decode(self, pc):
        w = self.word(pc)
        if w is None:
            return f'{pc:08x} -------- BSS/unmapped'
        op, rs, rt, imm = w>>26, (w>>21)&31, (w>>16)&31, w&0xffff
        simm = imm if imm < 0x8000 else imm-0x10000
        s = self.comment(pc)
        if s is None:
            if w == 0:
                s = 'nop'
            elif op in MEM:
                s = f'{MEM[op]} ${REG[rt]}, {simm:#x}(${REG[rs]})'
            elif op in (2, 3):
                s = f'{"jal" if op == 3 else "j"} {((pc+4)&0xf0000000)|((w&0x3ffffff)<<2):#x}'
            else:
                s = '.word (no verified OUT annotation)'
        if op in (4,5,6,7,0x14,0x15,0x16,0x17) or op==1 or (op==0x11 and rs==8):
            s += f' ; target={pc+4+simm*4:#x}'
        return f'{pc:08x} {w:08x} {s}'

    def text_words(self):
        for pc in range(self.text[3], self.text[3]+self.text[5], 4):
            yield pc, self.word(pc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('command', choices=['manifest','dis','words','imm','calls','refs'])
    parser.add_argument('values', nargs='*', type=lambda s:int(s,0))
    args = parser.parse_args()
    elf = Elf(args.root)
    print(f'# ELF sha256={hashlib.sha256(elf.data).hexdigest()} bytes={len(elf.data)}')
    if args.command == 'manifest':
        for name, s in elf.sections.items():
            print(f'{name} va={s[3]:#x} size={s[5]:#x} offset={s[4]:#x}')
    elif args.command in ('dis','words'):
        start, end = args.values
        if start % 4 or end % 4 or end < start:
            parser.error('ranges must be ordered and word-aligned (end exclusive)')
        for pc in range(start, end, 4):
            print(elf.decode(pc) if args.command=='dis' else f'{pc:08x} {elf.word(pc)} {elf.word(pc):#010x}' if elf.word(pc) is not None else f'{pc:08x} BSS/unmapped')
    elif args.command == 'imm':
        wanted = set(v&0xffff for v in args.values)
        count = 0
        for pc,w in elf.text_words():
            if w&0xffff in wanted and w>>26 not in (0,2,3,0x10,0x11,0x12,0x1c):
                print(elf.decode(pc)); count += 1
        print(f'# matches={count}; .text only; includes unrelated displacement/address literals')
    elif args.command == 'calls':
        wanted = set(args.values)
        for pc,w in elf.text_words():
            if w>>26 in (2,3) and (((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)) in wanted:
                print(elf.decode(pc))
    elif args.command == 'refs':
        wanted = set(args.values)
        for typ, off, va, pa, fs, ms, flags, align in elf.segs:
            if typ==1:
                for i in range(0,fs-3,4):
                    w=elf.u32(off+i)
                    if w in wanted:
                        print(f'{va+i:08x} -> {w:08x}')
    print('# E13 STATIC TAIL COMPLETE')


if __name__ == '__main__':
    main()
