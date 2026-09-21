#!/usr/bin/env python3
"""Independent CT32/CT24 VRAM and host-PNG join; standard library only.

Address tables match the corrected E4 decoder (FBP is in 8-KiB pages,
converted to 256-byte blocks before the swizzle). Emits full-size images,
pixel metrics, and exact host/hash comparisons, never resampling evidence.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib
from e8_io import read_capture, resolve

EVIDENCE=Path(__file__).resolve().parent
RUN=Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
BLOCK=[[0,1,4,5,16,17,20,21],[2,3,6,7,18,19,22,23],[8,9,12,13,24,25,28,29],[10,11,14,15,26,27,30,31]]
COL=[[0,1,4,5,8,9,12,13],[2,3,6,7,10,11,14,15],[16,17,20,21,24,25,28,29],[18,19,22,23,26,27,30,31],
     [32,33,36,37,40,41,44,45],[34,35,38,39,42,43,46,47],[48,49,52,53,56,57,60,61],[50,51,54,55,58,59,62,63]]


def address(fbp,bw,x,y):
    block=fbp<<5
    page=(block>>5)+(y>>5)*(bw or 1)+(x>>6)
    bid=(block&31)+BLOCK[(y>>3)&3][(x>>3)&7]
    return ((page+(bid>>5))<<13)+(bid&31)*256+COL[y&7][x&7]*4


def surface(data,fbp,bw,w,h):
    rgba=bytearray(w*h*4)
    for y in range(h):
        for x in range(w):
            src=address(fbp,bw,x,y);dst=(y*w+x)*4
            rgba[dst:dst+3]=data[src:src+3];rgba[dst+3]=255
    return bytes(rgba)


def fnv32(data):
    h=2166136261
    for c in data: h=((h^c)*16777619)&0xffffffff
    return h


def field_surface(rgba,w,h,parity):
    """SMODE2=1 field presentation: select each row pair's even/odd row."""
    return b''.join(rgba[min((y//2)*2+parity,h-1)*w*4:
                         (min((y//2)*2+parity,h-1)+1)*w*4] for y in range(h))


def census(rgba,w,h):
    points=[(i%w,i//w) for i in range(w*h) if any(rgba[i*4:i*4+3])]
    return dict(width=w,height=h,rgb_nonblack=len(points),
                bbox=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)] if points else None,
                rgba_sha256=hashlib.sha256(rgba).hexdigest(),rgba_fnv32=hex(fnv32(rgba)))


def write_png(path,w,h,rgba):
    def chunk(t,d):
        return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    raw=b''.join(b'\0'+rgba[y*w*4:(y+1)*w*4] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))


def read_png(path):
    data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    pos=8;compressed=b'';shape=None
    while pos<len(data):
        n=struct.unpack_from('>I',data,pos)[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+n]
        assert zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from('>I',data,pos+8+n)[0]
        if kind==b'IHDR':shape=struct.unpack('>IIBBBBB',payload)
        if kind==b'IDAT':compressed+=payload
        pos+=12+n
        if kind==b'IEND':break
    w,h,depth,color,compression,filtering,interlace=shape
    assert depth==8 and color in (2,6) and compression==filtering==interlace==0,shape
    bpp=4 if color==6 else 3;stride=w*bpp;raw=zlib.decompress(compressed)
    assert len(raw)==h*(stride+1)
    out=bytearray();prev=bytearray(stride)
    def paeth(a,b,c):
        p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
        return a if pa<=pb and pa<=pc else b if pb<=pc else c
    for y in range(h):
        at=y*(stride+1);f=raw[at];row=bytearray(raw[at+1:at+1+stride]);assert f<=4
        for x in range(stride):
            a=row[x-bpp] if x>=bpp else 0;b=prev[x];c=prev[x-bpp] if x>=bpp else 0
            predictor=[0,a,b,(a+b)//2,paeth(a,b,c)][f]
            row[x]=(row[x]+predictor)&255
        out+=row;prev=row
    if color==2:out=bytearray(b''.join(out[i:i+3]+b'\xff' for i in range(0,len(out),3)))
    return w,h,bytes(out)


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['a','b','c','d']);a=p.parse_args();label='e8'+a.phase
    vrampath=RUN/f'{label}-1/e4-vram-freeze.bin'
    vram=read_capture(vrampath)
    w,h=512,448;prod=surface(vram,0,8,w,h);disp=surface(vram,112,8,w,h)
    result=dict(label=label,vram_sha256=hashlib.sha256(vram).hexdigest(),producer=census(prod,w,h),display=census(disp,w,h),
                producer_display_equal=prod==disp,rgb_different_pixels=sum(prod[i:i+3]!=disp[i:i+3] for i in range(0,len(prod),4)))
    result['producer_png']='producer-'+result['producer']['rgba_sha256']+'.png'
    result['display_png']='display-'+result['display']['rgba_sha256']+'.png'
    write_png(EVIDENCE/result['producer_png'],w,h,prod);write_png(EVIDENCE/result['display_png'],w,h,disp)
    logpath=RUN/f'boot-{label}-1.log'
    text=read_capture(logpath).decode(errors='replace')
    dumps=[]
    for match in re.finditer(r'\[frame:dump\] seq=(\d+) tick=(\d+) size=(\d+)x(\d+) fbp=(\d+)/(\d+) fallback=(\d+) fnv1a=([0-9a-f]+)',text):
        seq,tick,ww,hh,d,s,f,hashtext=match.groups()
        dumps.append(dict(seq=int(seq),tick=int(tick),width=int(ww),height=int(hh),display=int(d),source=int(s),fallback=int(f),fnv=hex(int(hashtext,16))))
    config=json.loads((EVIDENCE/f'{label}-config.json').read_text())
    arm=int(config['env']['PS2X_E4_ARM_TICK'])
    result['boundary_present']=[r for r in dumps if arm-1<=r['tick']<=arm+3]
    result['display_hash_present_matches']=[r for r in dumps if r['fnv']==result['display']['rgba_fnv32'] and arm-1<=r['tick']<=arm+3]
    host=resolve(RUN/f'frames-{label}-1/upload-latest.png')
    ww,hh,rgba=read_png(host)
    result['host_latest']=census(rgba,ww,hh)
    result['host_latest_equals_frozen_display']=ww==w and hh==h and rgba==disp
    result['host_png_sha256']=hashlib.sha256(host.read_bytes()).hexdigest()
    # Raw VRAM pixels differ from a field-presented upload by design. Read the
    # captured mode and tick, then compare the complete independently decoded
    # surface after that documented row selection. Retain the raw comparison.
    present=read_capture(RUN/f'{label}-1/e4-present.txt').decode()
    smode2=int(re.search(r'smode2=0x([0-9a-f]+)',present).group(1),16)
    dispfb=int(re.search(r'dispfb1=0x([0-9a-f]+)',present).group(1),16)
    pmode=int(re.search(r'pmode=0x([0-9a-f]+)',present).group(1),16)
    assert pmode&3==1 and dispfb==0x9070, 'outside this miner\'s CRT1 geometry'
    metadata=read_capture(RUN/f'frames-{label}-1/upload-latest.txt').decode().strip()
    hosttick=int(re.search(r'tick=(\d+)',metadata).group(1))
    result['host_latest_metadata']=metadata
    result['present_mode']={'pmode':hex(pmode),'smode2':hex(smode2),'dispfb1':hex(dispfb)}
    if smode2&3==1:
        fields=[field_surface(disp,w,h,parity) for parity in [0,1]]
        result['display_fields']=[dict(parity=p,**census(data,w,h)) for p,data in enumerate(fields)]
        result['field_present_matches']=[dict(r,expected_fnv=result['display_fields'][r['tick']&1]['rgba_fnv32'],
            matches=r['fnv']==result['display_fields'][r['tick']&1]['rgba_fnv32']) for r in result['boundary_present']]
        result['host_latest_field_parity']=hosttick&1
        result['host_latest_equals_expected_display_field']=ww==w and hh==h and rgba==fields[hosttick&1]
    # The observed copy's sampled content is shifted one source pixel in each
    # axis. Measure it explicitly; do not confuse this with P==D bit identity.
    shifted=b''.join(prod[((y+1)*w+1)*4:((y+2)*w)*4]+b'\0\0\0\xff' for y in range(h-1))+b'\0\0\0\xff'*w
    assert len(shifted)==len(disp)
    result['copy_content_comparison']={'source_offset':[1,1],'outside_source':'black',
        'full_rgb_different_pixels':sum(shifted[i:i+3]!=disp[i:i+3] for i in range(0,len(disp),4)),
        'overlap_pixels':(w-1)*(h-1)}
    (EVIDENCE/f'{label}-frame.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));print('# E8 FRAME TAIL COMPLETE')


if __name__=='__main__':main()
