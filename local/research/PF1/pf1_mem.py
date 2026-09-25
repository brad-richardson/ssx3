#!/usr/bin/env python3
"""Read guest words from the SLUS ELF (default) or a 32 MB RDRAM dump (--ram FILE).
Usage: pf1_mem.py [--ram FILE] words ADDR [N]    # N 32-bit words
       pf1_mem.py [--ram FILE] vt ADDR [N]       # gcc2 vtable entries {s16 delta, s16, fn}
       pf1_mem.py [--ram FILE] floats ADDR [N]
"""
import struct, sys
ELF = '/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72'

class Mem:
    def __init__(self, ram=None):
        self.ram = open(ram, 'rb').read() if ram else None
        d = open(ELF, 'rb').read()
        phoff, = struct.unpack_from('<I', d, 0x1c)
        phnum, = struct.unpack_from('<H', d, 0x2c)
        self.segs = []
        for i in range(phnum):
            t, off, va, pa, fsz, msz = struct.unpack_from('<6I', d, phoff + 32 * i)
            if t == 1:
                self.segs.append((va, off, fsz, msz))
        self.elf = d
    def u32(self, a):
        a &= 0x1fffffff
        if self.ram is not None:
            return struct.unpack_from('<I', self.ram, a & 0x1ffffff)[0]
        for va, off, fsz, msz in self.segs:
            if va <= a < va + msz:
                return struct.unpack_from('<I', self.elf, off + a - va)[0] if a - va < fsz else 0
        return None

def main():
    args = sys.argv[1:]
    ram = None
    if args[0] == '--ram':
        ram = args[1]; args = args[2:]
    m = Mem(ram)
    cmd, a = args[0], int(args[1], 0)
    n = int(args[2], 0) if len(args) > 2 else 16
    if cmd == 'words':
        for i in range(n):
            w = m.u32(a + 4 * i)
            f = struct.unpack('<f', struct.pack('<I', w or 0))[0]
            print('0x%06x +0x%03x: 0x%08x  %g' % (a + 4 * i, 4 * i, w or 0, f))
    elif cmd == 'vt':
        for i in range(n):
            w0, fn = m.u32(a + 8 * i), m.u32(a + 8 * i + 4)
            print('0x%06x slot+0x%03x: delta=%d idx=%d fn=0x%x' % (a + 8 * i, 8 * i,
                  struct.unpack('<h', struct.pack('<H', w0 & 0xffff))[0], (w0 >> 16), fn))
    elif cmd == 'floats':
        for i in range(n):
            w = m.u32(a + 4 * i)
            print('0x%06x %g' % (a + 4 * i, struct.unpack('<f', struct.pack('<I', w))[0]))

if __name__ == '__main__':
    main()
