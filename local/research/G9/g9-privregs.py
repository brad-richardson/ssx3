#!/usr/bin/env python3
# G9 Task 1: extract + decode PrivRegisters (DISPLAY/DISPFB/SMODE1/SMODE2/PMODE)
# from the G8 dump's own bytes. Framing reused from g8-census.py (GSDump writer).
# Layout cross-check: parallel-gs PrivRegisterState (gs_interface.hpp:70) reads
# the 8192 B blob directly, so offsets below are asserted against BOTH that
# struct order and PCSX2's GSPrivRegSet (GSRegs.h, bytesize read).
import struct, sys, hashlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]

# offset within 8192 B blob (16 B stride, low qword live) per PrivRegisterState order
OFF = {'PMODE': 0x00, 'SMODE1': 0x10, 'SMODE2': 0x20, 'SYNCH1': 0x40,
       'SYNCH2': 0x50, 'SYNCV': 0x60, 'DISPFB1': 0x70, 'DISPLAY1': 0x80,
       'DISPFB2': 0x90, 'DISPLAY2': 0xA0, 'EXTBUF': 0xB0, 'EXTDATA': 0xC0,
       'EXTWRITE': 0xD0, 'BGCOLOR': 0xE0,
       'CSR': 0x1000, 'IMR': 0x1010, 'BUSDIR': 0x1040, 'SIGLBLID': 0x1080}

def bits(v, lo, w): return (v >> lo) & ((1 << w) - 1)

def dec_display(v):
    return dict(DX=bits(v,0,12), DY=bits(v,12,11), MAGH=bits(v,23,4),
                MAGV=bits(v,27,2), DW=bits(v,32,12), DH=bits(v,44,11))

def dec_dispfb(v):
    return dict(FBP=bits(v,0,9), FBW=bits(v,9,6), PSM=bits(v,15,5),
                DBX=bits(v,32,11), DBY=bits(v,43,11))

def dec_smode1(v):
    return dict(RC=bits(v,0,3), LC=bits(v,3,7), T1248=bits(v,10,2),
                SLCK=bits(v,12,1), CMOD=bits(v,13,2), EX=bits(v,15,1),
                PRST=bits(v,16,1), SINT=bits(v,17,1), XPCK=bits(v,18,1),
                PCK2=bits(v,19,2), SPML=bits(v,21,4), GCONT=bits(v,25,1),
                PHS=bits(v,26,1), PVS=bits(v,27,1), PEHS=bits(v,28,1),
                PEVS=bits(v,29,1), CLKSEL=bits(v,30,2), NVCK=bits(v,32,1),
                SLCK2=bits(v,33,1), VCKSEL=bits(v,34,2), VHP=bits(v,36,1))

def dec_smode2(v):
    return dict(INT=bits(v,0,1), FFMD=bits(v,1,1), DPMS=bits(v,2,2))

def dec_pmode(v):
    return dict(EN1=bits(v,0,1), EN2=bits(v,1,1), MMOD=bits(v,2,1),
                AMOD=bits(v,3,1), SLBG=bits(v,4,1), ALP=bits(v,5,8))

def dec_syncv(v):
    return dict(VFP=bits(v,0,10), VFPE=bits(v,10,10), VBP=bits(v,20,12),
                VBPE=bits(v,32,10), VDP=bits(v,42,11), VS=bits(v,53,11))

def show(tag, blob):
    print(f"--- {tag} ---")
    for name in ('PMODE','SMODE1','SMODE2','SYNCV','DISPFB1','DISPLAY1',
                 'DISPFB2','DISPLAY2','EXTBUF','EXTDATA','EXTWRITE','BGCOLOR'):
        v = u64(blob, OFF[name])
        hi = u64(blob, OFF[name]+8)
        print(f"  {name:8s} off=0x{OFF[name]:04x} lo=0x{v:016x} hi=0x{hi:016x}")
    p = dec_pmode(u64(blob, OFF['PMODE']))
    s1 = dec_smode1(u64(blob, OFF['SMODE1']))
    s2 = dec_smode2(u64(blob, OFF['SMODE2']))
    sv = dec_syncv(u64(blob, OFF['SYNCV']))
    f1 = dec_dispfb(u64(blob, OFF['DISPFB1']))
    d1 = dec_display(u64(blob, OFF['DISPLAY1']))
    f2 = dec_dispfb(u64(blob, OFF['DISPFB2']))
    d2 = dec_display(u64(blob, OFF['DISPLAY2']))
    print(f"  PMODE={p}")
    print(f"  SMODE1={s1}")
    print(f"  SMODE2={s2}")
    print(f"  SYNCV={sv}")
    print(f"  DISPFB1={f1}")
    print(f"  DISPLAY1={d1}")
    print(f"  DISPFB2={f2}")
    print(f"  DISPLAY2={d2}")
    return {'PMODE': p, 'SMODE1': s1, 'SMODE2': s2, 'SYNCV': sv,
            'DISPFB1': f1, 'DISPLAY1': d1, 'DISPFB2': f2, 'DISPLAY2': d2}

def main(path):
    b = open(path, 'rb').read()
    n = len(b)
    print(f"file={path}\nsize={n} sha256={hashlib.sha256(b).hexdigest()}")
    o = 0
    fake_crc = u32(b, o); o += 4
    header_size = u32(b, o); o += 4
    (ver, state_size, serial_off, serial_sz, crc, shot_w, shot_h,
     shot_off, shot_sz) = struct.unpack_from('<9I', b, o); o += 36
    o += serial_sz + shot_sz
    print(f"version={ver} state_size={state_size} serial_sz={serial_sz} "
          f"shot={shot_w}x{shot_h} shot_sz={shot_sz}")
    o += state_size
    regs0 = b[o:o+8192]; o += 8192
    pk_start = o
    # packet walk: collect PrivRegs blobs + vsync phases
    privs = []
    phases = []
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    xfer = 0
    while o < n:
        pid = b[o]; o += 1
        assert pid in counts, (o, pid)
        counts[pid] += 1
        if pid == 0:
            o += 1
            sz = u32(b, o); o += 4
            xfer += sz
            o += sz
        elif pid == 1:
            phases.append(b[o]); o += 1
        elif pid == 2:
            o += 4
        elif pid == 3:
            privs.append(bytes(b[o:o+8192])); o += 8192
    print(f"EOF_SYNC={'yes' if o == n else f'NO off={o-n}'} "
          f"census={counts} GIF_bytes={xfer} phases={phases}")
    print(f"packet_region={pk_start}..{n} ({n-pk_start} B)")
    dec0 = show("header regs0 (dump-start state)", regs0)
    decs = []
    for i, p in enumerate(privs):
        same0 = (p == regs0)
        print(f"PrivRegs packet #{i}: identical_to_header_regs0={same0} "
              f"sha={hashlib.sha256(p).hexdigest()[:16]}")
        decs.append(show(f"PrivRegs packet #{i}", p))
    # diff summary across packets
    alld = [dec0] + decs
    print("--- field stability across header + %d PrivRegs packets ---" % len(privs))
    for reg in ('PMODE','SMODE1','SMODE2','SYNCV','DISPFB1','DISPLAY1','DISPFB2','DISPLAY2'):
        vals = [repr(d[reg]) for d in alld]
        print(f"  {reg}: {'STABLE' if len(set(vals))==1 else 'VARIES'}")

if __name__ == '__main__':
    main(sys.argv[1])
