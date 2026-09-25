# AU9: decode the PCSX2 SPU2 register-write log (spureg.bin: u32 ns, u32 rmem, u32 value).
import numpy as np, sys, collections
r = np.fromfile(sys.argv[1], dtype='<u4').reshape(-1, 3)
ns, addr, val = r[:, 0], r[:, 1], r[:, 2]
VREG = ['VOLL', 'VOLR', 'PITCH', 'ADSR1', 'ADSR2', 'ENVX', 'VOLXL', 'VOLXR']
CREG = {0x180: 'PMON0', 0x182: 'PMON1', 0x184: 'NON0', 0x186: 'NON1', 0x188: 'VMIXL0', 0x18A: 'VMIXL1',
        0x18C: 'VMIXEL0', 0x18E: 'VMIXEL1', 0x190: 'VMIXR0', 0x192: 'VMIXR1', 0x194: 'VMIXER0', 0x196: 'VMIXER1',
        0x198: 'MMIX', 0x19A: 'ATTR', 0x19C: 'IRQAH', 0x19E: 'IRQAL', 0x1A0: 'KON0', 0x1A2: 'KON1', 0x1A4: 'KOFF0',
        0x1A6: 'KOFF1', 0x1A8: 'TSAH', 0x1AA: 'TSAL', 0x1AC: 'DATA', 0x1AE: 'CTRL', 0x1B0: 'ADMAS', 0x340: 'ENDX0', 0x342: 'ENDX1',
        0x344: 'STATX', 0x2E0: 'ESAH', 0x2E2: 'ESAL', 0x33C: 'EEA'}
def name(a):
    a = int(a)
    if (a >> 16) != 0x1f90: return f'other_{a:x}'
    o = a & 0xffff
    if o >= 0x7c0: return f'SPDIF_{o:x}'
    core = 1 if o >= 0x400 and o < 0x760 else 0
    if o >= 0x760:
        core = (o - 0x760) // 0x28; oo = (o - 0x760) % 0x28
        n = ['MVOLL', 'MVOLR', 'EVOLL', 'EVOLR', 'AVOLL', 'AVOLR', 'BVOLL', 'BVOLR', 'MVOLXL', 'MVOLXR'] + [f'rev{i}' for i in range(10)]
        return f'c{core}.{n[oo // 2] if oo // 2 < len(n) else hex(oo)}'
    o -= core * 0x400
    if o < 0x180: return f'c{core}.v{o // 0x10:02d}.{VREG[(o % 0x10) // 2]}'
    if 0x1C0 <= o < 0x2E0:
        v, k = divmod(o - 0x1C0, 0xC); return f'c{core}.v{v:02d}.' + ['SSAH', 'SSAL', 'LSAXH', 'LSAXL', 'NAXH', 'NAXL'][k // 2]
    return f'c{core}.' + CREG.get(o, hex(o))
names = [name(a) for a in addr]
print('writes', len(r), 'ns span', ns.min(), ns.max(), f'({ns.max()/48000:.1f} s)')
kinds = collections.Counter(n.split('.', 2)[-1] if '.v' in n else n for n in names)
print('by register kind:', dict(kinds.most_common(40)))
# time histogram (10 s bins) of voice-ish writes
vt = ns[[('.v' in n) or ('KON' in n) or ('KOFF' in n) for n in names]]
h = np.bincount((vt // 480000).astype(int))
print('voice/KON writes per 10 s bin:', ' '.join(map(str, h)))
kon = [(int(t), n, int(v)) for t, n, v in zip(ns, names, val) if 'KON' in n and v]
print('KON writes', len(kon), 'first', kon[:8])
# setup writes (non-voice) in order, first 60
setup = [(int(t), n, hex(int(v))) for t, n, v in zip(ns, names, val) if '.v' not in n and 'KO' not in n and 'TSA' not in n and 'DATA' not in n and 'ADMAS' not in n and 'CTRL' not in n and 'STATX' not in n]
print('non-voice writes', len(setup))
for s in setup[:70]: print('  ', s)
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as f:
        for t, n, v in zip(ns, names, val): f.write(f'{t} {n} {v:04x}\n')
