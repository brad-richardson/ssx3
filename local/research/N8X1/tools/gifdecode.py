#!/usr/bin/env python3
import struct, sys
sys.path.insert(0, __file__.rsplit('/',1)[0])
from gsstream import records
REG = {0:'PRIM',1:'RGBAQ',2:'ST',3:'UV',4:'XYZF2',5:'XYZ2',6:'TEX0_1',7:'TEX0_2',8:'CLAMP_1',9:'CLAMP_2',0xa:'FOG',0xc:'XYZF3',0xd:'XYZ3',0xe:'A+D',0xf:'NOP'}
AD = {0x00:'PRIM',0x01:'RGBAQ',0x02:'ST',0x03:'UV',0x04:'XYZF2',0x05:'XYZ2',0x06:'TEX0_1',0x07:'TEX0_2',0x08:'CLAMP_1',0x09:'CLAMP_2',0x0a:'FOG',0x14:'TEX1_1',0x15:'TEX1_2',0x16:'TEX2_1',0x17:'TEX2_2',0x18:'XYOFFSET_1',0x19:'XYOFFSET_2',0x1a:'PRMODECONT',0x1b:'PRMODE',0x1c:'TEXCLUT',0x22:'SCANMSK',0x34:'MIPTBP1_1',0x35:'MIPTBP1_2',0x36:'MIPTBP2_1',0x37:'MIPTBP2_2',0x3b:'TEXA',0x3d:'FOGCOL',0x3f:'TEXFLUSH',0x40:'SCISSOR_1',0x41:'SCISSOR_2',0x42:'ALPHA_1',0x43:'ALPHA_2',0x44:'DIMX',0x45:'DTHE',0x46:'COLCLAMP',0x47:'TEST_1',0x48:'TEST_2',0x49:'PABE',0x4a:'FBA_1',0x4b:'FBA_2',0x4c:'FRAME_1',0x4d:'FRAME_2',0x4e:'ZBUF_1',0x4f:'ZBUF_2',0x50:'BITBLTBUF',0x51:'TRXPOS',0x52:'TRXREG',0x53:'TRXDIR',0x54:'HWREG',0x60:'SIGNAL',0x61:'FINISH',0x62:'LABEL'}
def decode(data, out):
    p = 0
    while p + 16 <= len(data):
        lo, hi = struct.unpack_from('<QQ', data, p); p += 16
        nloop = lo & 0x7fff; eop = (lo>>15)&1; pre=(lo>>46)&1; prim=(lo>>47)&0x7ff; flg=(lo>>58)&3; nreg=(lo>>60)&0xf or 16
        regs=[(hi>>(4*i))&0xf for i in range(nreg)]
        out.append(f"  TAG nloop={nloop} eop={eop} flg={flg} pre={pre} prim=0x{prim:x} regs={[REG.get(r,r) for r in regs]}")
        if flg == 0:
            for l in range(nloop):
                for r in regs:
                    a, b = struct.unpack_from('<QQ', data, p); p += 16
                    if r == 0xe:
                        out.append(f"    {AD.get(b&0xff, hex(b&0xff))} = 0x{a:016x}")
                    else:
                        out.append(f"    {REG.get(r,r)} {a:016x} {b:016x}")
        elif flg == 1:
            for l in range(nloop):
                words = []
                for r in regs:
                    a, = struct.unpack_from('<Q', data, p); p += 8
                    words.append(f"{REG.get(r,r)}={a:016x}")
                out.append("    " + " ".join(words))
            p = (p + 15) & ~15
        else:
            out.append(f"    IMAGE qwords={nloop} sha={__import__('hashlib').sha1(data[p:p+nloop*16]).hexdigest()[:12]}")
            p += nloop*16
        if eop and p < len(data):
            out.append("  (EOP, more data follows)")
    return out
if __name__ == '__main__':
    path, t = sys.argv[1], int(sys.argv[2])
    for off, k, tick, rec in records(path, t+1):
        if tick != t: continue
        if k == 1:
            size = struct.unpack_from('<I', rec, 10)[0]
            print(f"GIF off={off} path={rec[9]} size={size}")
            print("\n".join(decode(rec[14:14+size], [])))
        elif k == 2:
            o, v = struct.unpack_from('<IQ', rec, 9); print(f"PRIV off=0x{o:x} val=0x{v:x}")
        elif k == 4: print(f"MARKER {tick}")
