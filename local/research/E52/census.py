#!/usr/bin/env python3
"""E52 census: count FPU (COP1, LWC1/SWC1) and COP2 (VU0 macro, LQC2/SQC2) sites
in a codegen dir by decoding the raw instruction word in each
'// 0xADDR: 0xWORD  mnemonic' comment. Reports emitted sites and unique addresses."""
import os, re, sys, collections
root = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/dev/ssx3-work/codegen-ssx3')
pat = re.compile(r'^\s*// 0x([0-9a-f]+): 0x([0-9a-f]{8})\s+(\S+)?(.*)$')
S1 = {0x00:'VADDx',0x01:'VADDy',0x02:'VADDz',0x03:'VADDw',0x04:'VSUBx',0x05:'VSUBy',0x06:'VSUBz',0x07:'VSUBw',
0x08:'VMADDx',0x09:'VMADDy',0x0A:'VMADDz',0x0B:'VMADDw',0x0C:'VMSUBx',0x0D:'VMSUBy',0x0E:'VMSUBz',0x0F:'VMSUBw',
0x10:'VMAXx',0x11:'VMAXy',0x12:'VMAXz',0x13:'VMAXw',0x14:'VMINIx',0x15:'VMINIy',0x16:'VMINIz',0x17:'VMINIw',
0x18:'VMULx',0x19:'VMULy',0x1A:'VMULz',0x1B:'VMULw',0x1C:'VMULq',0x1D:'VMAXi',0x1E:'VMULi',0x1F:'VMINIi',
0x20:'VADDq',0x21:'VMADDq',0x22:'VADDi',0x23:'VMADDi',0x24:'VSUBq',0x25:'VMSUBq',0x26:'VSUBi',0x27:'VMSUBi',
0x28:'VADD',0x29:'VMADD',0x2A:'VMUL',0x2B:'VMAX',0x2C:'VSUB',0x2D:'VMSUB',0x2E:'VOPMSUB',0x2F:'VMINI',
0x30:'VIADD',0x31:'VISUB',0x32:'VIADDI',0x34:'VIAND',0x35:'VIOR',0x38:'VCALLMS',0x39:'VCALLMSR'}
S2 = {0x00:'VADDAx',0x01:'VADDAy',0x02:'VADDAz',0x03:'VADDAw',0x04:'VSUBAx',0x05:'VSUBAy',0x06:'VSUBAz',0x07:'VSUBAw',
0x08:'VMADDAx',0x09:'VMADDAy',0x0A:'VMADDAz',0x0B:'VMADDAw',0x0C:'VMSUBAx',0x0D:'VMSUBAy',0x0E:'VMSUBAz',0x0F:'VMSUBAw',
0x10:'VITOF0',0x11:'VITOF4',0x12:'VITOF12',0x13:'VITOF15',0x14:'VFTOI0',0x15:'VFTOI4',0x16:'VFTOI12',0x17:'VFTOI15',
0x18:'VMULAx',0x19:'VMULAy',0x1A:'VMULAz',0x1B:'VMULAw',0x1C:'VMULAq',0x1D:'VABS',0x1E:'VMULAi',0x1F:'VCLIPw',
0x20:'VADDAq',0x21:'VMADDAq',0x22:'VADDAi',0x23:'VMADDAi',0x24:'VSUBAq',0x25:'VMSUBAq',0x26:'VSUBAi',0x27:'VMSUBAi',
0x28:'VADDA',0x29:'VMADDA',0x2A:'VMULA',0x2C:'VSUBA',0x2D:'VMSUBA',0x2E:'VOPMULA',0x2F:'VNOP',0x30:'VMOVE',0x31:'VMR32',
0x34:'VLQI',0x35:'VSQI',0x36:'VLQD',0x37:'VSQD',0x38:'VDIV',0x39:'VSQRT',0x3A:'VRSQRT',0x3B:'VWAITQ',0x3C:'VMTIR',
0x3D:'VMFIR',0x3E:'VILWR',0x3F:'VISWR',0x40:'VRNEXT',0x41:'VRGET',0x42:'VRINIT',0x43:'VRXOR'}
FS = {0:'ADD.S',1:'SUB.S',2:'MUL.S',3:'DIV.S',4:'SQRT.S',5:'ABS.S',6:'MOV.S',7:'NEG.S',0x16:'RSQRT.S',0x18:'ADDA.S',
0x19:'SUBA.S',0x1A:'MULA.S',0x1C:'MADD.S',0x1D:'MSUB.S',0x1E:'MADDA.S',0x1F:'MSUBA.S',0x24:'CVT.W.S',0x28:'MAX.S',
0x29:'MIN.S',0x30:'C.F.S',0x32:'C.EQ.S',0x34:'C.LT.S',0x36:'C.LE.S'}
def classify(w):
    op = w >> 26
    if op == 0x31: return 'LWC1'
    if op == 0x39: return 'SWC1'
    if op == 0x36: return 'LQC2'
    if op == 0x3E: return 'SQC2'
    if op == 0x11:
        fmt = (w >> 21) & 0x1F; fn = w & 0x3F
        if fmt == 0: return 'MFC1'
        if fmt == 2: return 'CFC1(fs=%d)' % ((w >> 11) & 0x1F)
        if fmt == 4: return 'MTC1'
        if fmt == 6: return 'CTC1(fs=%d)' % ((w >> 11) & 0x1F)
        if fmt == 8: return ['BC1F','BC1T','BC1FL','BC1TL'][(w >> 16) & 3]
        if fmt == 0x10: return FS.get(fn, 'COP1.S fn=0x%x' % fn)
        if fmt == 0x14: return 'CVT.S.W' if fn == 0x20 else 'COP1.W fn=0x%x' % fn
        return 'COP1 fmt=0x%x' % fmt
    if op == 0x12:
        fmt = (w >> 21) & 0x1F
        if fmt == 1: return 'QMFC2'
        if fmt == 2: return 'CFC2(rd=%d)' % ((w >> 11) & 0x1F)
        if fmt == 5: return 'QMTC2'
        if fmt == 6: return 'CTC2(rd=%d)' % ((w >> 11) & 0x1F)
        if fmt == 8: return ['BC2F','BC2T','BC2FL','BC2TL'][(w >> 16) & 3]
        if fmt >= 0x10:
            fn = w & 0x3F
            if fn >= 0x3C:
                f2 = (((w >> 6) & 0x1F) << 2) | (w & 3)
                return S2.get(f2, 'VU0.S2 0x%x' % f2)
            return S1.get(fn, 'VU0.S1 0x%x' % fn)
        return 'COP2 fmt=0x%x' % fmt
    return None
emitted = collections.Counter(); uniq = collections.defaultdict(set); files = collections.defaultdict(set)
extra = collections.defaultdict(collections.Counter)  # per-op detail
for fn in sorted(os.listdir(root)):
    if not fn.endswith('.cpp'): continue
    with open(os.path.join(root, fn), errors='replace') as fh:
        for line in fh:
            m = pat.match(line)
            if not m: continue
            a = int(m.group(1), 16); w = int(m.group(2), 16)
            c = classify(w)
            if not c: continue
            emitted[c] += 1; uniq[c].add(a); files[c].add(fn)
            if c == 'SQRT.S' or c == 'RSQRT.S':
                extra[c]['fs!=0' if (w >> 11) & 0x1F else 'fs==0'] += 1
            if c in ('VDIV','VSQRT','VRSQRT','VMTIR','VCALLMSR','VCALLMS','VCLIPw') or c.startswith('CFC2') or c.startswith('CTC2'):
                extra[c]['0x%08x' % w] += 1
            if c.startswith('V') and not c.startswith('VI') and c not in ('VCALLMS','VCALLMSR','VNOP','VWAITQ'):
                vfd = (w >> 6) & 0x1F; vft = (w >> 16) & 0x1F
                if (w & 0x3F) < 0x3C and vfd == 0: extra['dest VF0']['%s' % c] += 1
kind = lambda c: 'FPU' if (c.endswith('.S') or c.endswith('.W') or 'C1' in c or c.startswith('BC1') or c.startswith('COP1')) else 'COP2'
print('# census of', root)
print('| class | op | emitted sites | unique guest addrs | files |')
print('|---|---|---|---|---|')
for c in sorted(emitted, key=lambda c: (kind(c), -len(uniq[c]))):
    print('| %s | %s | %d | %d | %d |' % (kind(c), c, emitted[c], len(uniq[c]), len(files[c])))
print()
for c, cnt in sorted(extra.items()):
    print('##', c, dict(cnt.most_common(20)))
