#!/usr/bin/env python3
"""Read-only, reproducible joins from E11's single closed capture.

The copy calculation decodes the packet's individual sprites, including its
different final row. It describes the captured runtime's sampling behavior;
it neither changes the renderer nor asserts hardware raster conformance.
"""
import hashlib
import json
import re
import struct
from collections import Counter
from fractions import Fraction
from pathlib import Path

from e11_frame import address, census, surface
from e11_io import read_capture
from e11_mine import packet, tap

E = Path(__file__).resolve().parent
RUN = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')


def put(name, obj):
    (E/name).write_text(json.dumps(obj, indent=2)+'\n')


def copy_join():
    summary = json.loads((E/'e11a-summary.json').read_text())
    name = next(p['file'] for p in summary['packets'] if 'tick600-' in p['file'])
    path = RUN/'e11a-join'/name
    data = read_capture(path)
    decoded = packet(path)
    assert decoded['parsed_end'] == len(data) == 1696
    tag = next(t for t in decoded['tags'] if t['flg'] == 1 and t['nloop'] == 17)
    assert tag['nreg'] == 4 and int(tag['hi'], 16) == 0x5353
    regs = {int(r['reg'],16):int(r['value'],16) for r in decoded['registers'] if r['offset'] < tag['offset']}
    assert regs[0x4c]&511 == 112 and regs[6]&0x3fff == 0
    assert regs[6]>>14&63 == 8 and regs[8] == 5
    assert regs[0x14] == 0x61 and regs[0x4c]>>24&63 == 1
    offset = regs[0x18]
    ox, oy = (offset&0xffff)>>4, (offset>>32&0xffff)>>4
    assert (ox,oy) == (1792,1824)
    vram = read_capture(RUN/'e11a-1/e4-vram-freeze.bin')
    arm = read_capture(RUN/'e11a-1/e4-vram-arm.bin')
    assert vram == arm
    d = surface(vram,112,8,512,448)
    expected = bytearray(b'\0\0\0\xff'*(512*448))
    coverage = set()
    rectangles = []
    # The current DrawSprite truncates positive XY before subtracting XYOFFSET,
    # truncates FST endpoint UV to texels, and passes interpolated fixed UV to
    # SampleTexture. TEX1=0x61 selects linear filtering (half-texel subtraction).
    def rgb(u,v):
        u=max(0,min(1023,u));v=max(0,min(511,v))
        a=address(0,8,u,v)
        return vram[a:a+3]
    for i in range(17):
        uv0,xy0,uv1,xy1=struct.unpack_from('<4Q',data,tag['offset']+16+i*32)
        x0,y0=(xy0&0xffff)//16-ox,(xy0>>16&0xffff)//16-oy
        x1,y1=(xy1&0xffff)//16-ox,(xy1>>16&0xffff)//16-oy
        u0,v0=(uv0&0x3fff)//16,(uv0>>16&0x3fff)//16
        u1,v1=(uv1&0x3fff)//16,(uv1>>16&0x3fff)//16
        sx,sy=x1-x0,y1-y0
        row=dict(index=i,raw=[hex(v) for v in (uv0,xy0,uv1,xy1)],
                 xy_fixed=[[((xy&0xffff)/16)-ox,((xy>>16&0xffff)/16)-oy] for xy in (xy0,xy1)],
                 uv_fixed=[[(uv&0x3fff)/16,(uv>>16&0x3fff)/16] for uv in (uv0,uv1)],
                 draw_bounds=[max(0,x0),max(0,y0),min(511,x1-1),min(447,y1-1)])
        rectangles.append(row)
        for y in range(max(0,y0),min(448,y1)):
            vf=Fraction(v0)+Fraction((v1-v0)*(2*(y-y0)+1),2*sy)
            sv=Fraction(int(vf*16+Fraction(1,2)),16)-Fraction(1,2)
            va=sv.numerator//sv.denominator;fy=sv-va
            for x in range(max(0,x0),min(512,x1)):
                uf=Fraction(u0)+Fraction((u1-u0)*(2*(x-x0)+1),2*sx)
                su=Fraction(int(uf*16+Fraction(1,2)),16)-Fraction(1,2)
                ua=su.numerator//su.denominator;fx=su-ua
                a,b,c,f=rgb(ua,va),rgb(ua+1,va),rgb(ua,va+1),rgb(ua+1,va+1)
                color=bytes(int((1-fy)*((1-fx)*a[k]+fx*b[k])+fy*((1-fx)*c[k]+fx*f[k])+Fraction(1,2)) for k in range(3))
                at=(y*512+x)*4;expected[at:at+3]=color;coverage.add((x,y))
    differences=[dict(x=i%512,y=i//512,expected=expected[i*4:i*4+3].hex(),actual=d[i*4:i*4+3].hex())
                 for i in range(512*448) if expected[i*4:i*4+3]!=d[i*4:i*4+3]]
    uncovered=[(x,y) for y in range(448) for x in range(512) if (x,y) not in coverage]
    assert not differences, differences[:4]
    assert all(d[(y*512+x)*4:(y*512+x)*4+3]==b'\0\0\0' for x,y in uncovered)
    return dict(packet_sha256=hashlib.sha256(data).hexdigest(),vram_sha256=hashlib.sha256(vram).hexdigest(),
                arm_equals_freeze=True,registers={hex(k):hex(v) for k,v in regs.items()},rectangles=rectangles,
                covered_pixels=len(coverage),uncovered_black_pixels=len(uncovered),full_rgb_differences=0,
                full_rgba_equals=bytes(expected)==d,expected=census(bytes(expected),512,448),
                initial_uniform_offset_model_differences=2,
                correction='Final sprite covers row 446 with U endpoints 0..512 at X 0..512, unlike the half-pixel-offset first 16 sprites. Its V endpoints are both 447.5. Decode individual rectangles; do not apply a uniform source offset to the last row.',
                limit='Uncovered right/bottom border is measured black. This is the captured runtime sampling model, not an independent hardware raster conformance claim.')


def main():
    result=json.loads((E/'e11a-result.json').read_text());assert result.get('release_utc')
    events,tail=tap(RUN/'e11a-join/e7-events.txt')
    byseq={r['seq']:r for r in events}
    pairs=[]
    for tick in range(599,604):
        dm=[r for r in events if r['tick']==tick and r['kind']=='gif-dma' and r['source']==0x4ffcc0]
        assert len(dm)==1
        a=dm[0]
        gs=[r for r in events if r['tick']==tick and r['kind']=='gs-enter' and r['bytes']==a['bytes'] and r['fnv64']==a['fnv64']]
        assert len(gs)==1 and gs[0]['seq']>a['seq'] and a['bytes']==1696
        assert a['mask']==a['queued']==gs[0]['mask']==gs[0]['queued']==0
        pairs.append(dict(tick=tick,dma_seq=a['seq'],gs_seq=gs[0]['seq'],bytes=a['bytes'],fnv64=hex(a['fnv64']),mask=a['mask'],queued=a['queued']))
    summary=json.loads((E/'e11a-summary.json').read_text())
    assert len(summary['singleton'])==1 and summary['singleton'][0]['value']==0x61ba60
    assert summary['counter']['continuous'] and summary['counter']['M']=={'1':561}
    assert summary['counter']['pairs']=={'(0, 112, 0, 112)':560}
    assert len(summary['packets'])==5 and len({p['sha256'] for p in summary['packets']})==1
    card=json.loads((E/'e11a-card.json').read_text())
    assert card['query_calls']==card['query_returns']==321
    assert not card['unmatched_returns'] and not card['unclosed_calls']
    selected=[1702,1703,1705,1706,1707,1711,1712,1713,1714,1717,1718,1720,1721,1722,1723,1725,1728,1735,1741,1742,1747,1748,1750,1751,1752]
    request=[byseq[n] for n in selected]
    assert byseq[1703]['v0']==0 and byseq[1717]['v0']==1
    assert byseq[1712]['info']=='2,8192,0,1' and byseq[1721]['v0']==1
    assert byseq[1752]['value']==0 and byseq[1752]['addr']==byseq[1752]['UI']+0x338
    raw=read_capture(RUN/'boot-e11a-1.log').decode()
    missing=[dict(line=n,text=line) for n,line in enumerate(raw.splitlines(),1) if '[guest-branch:missing-target]' in line and 'target=0x2c5300 ' in line]
    assert len(missing)==2
    for r in missing:
        assert all(s in r['text'] for s in ['a0=0xb851a0 ','a1=0x0 ','v0=0x2c5300 ','a0[0]=0x486f78 ','policy=1 '])
    slots=[r for r in events if r['kind']=='mc-write' and r['addr'] in (0xb85324,0xb85338)]
    assert slots and all(r['value']==0 for r in slots)
    sibling=card['sibling_missing']
    assert len(sibling)==113 and all(r['a1']==r['slot0']==r['slot1']==0 for r in sibling)
    frames=json.loads((E/'e11a-frame.json').read_text())
    assert len(frames['field_present_matches'])==4 and all(r['matches'] for r in frames['field_present_matches'])
    assert frames['host_latest_equals_expected_display_field']
    progress=json.loads((E/'e11a-progress.json').read_text())
    assert progress['card_query_count']==0 and not progress['damaged_missing']
    assert not progress['function_mismatches'] and not progress['function_live_stack']
    copy=copy_join()
    packet_name=summary['packets'][0]['file'];h=14695981039346656037
    for b in read_capture(RUN/'e11a-join'/packet_name):h=((h^b)*1099511628211)&0xffffffffffffffff
    assert all(r['fnv64']==hex(h) for r in pairs)
    put('e11a-copy-content-join.json',copy)
    put('e11a-request-join.json',dict(events=request,api_counts=Counter(hex(p['call']['target']) for p in card['api_pairs']),
                                   getinfo_results=Counter(str(p['exit']['v0']) for p in card['api_pairs'] if p['call']['target']==0x40a498),
                                   sync_results=Counter(str(p['exit']['v0']) for p in card['api_pairs'] if p['call']['target']==0x40a360)))
    put('e11a-residual-join.json',dict(first_missing=missing,slot_status_writes=slots,
        same_run_following_sibling=sibling[0],sibling_missing_count=len(sibling),sibling_all_a1_statuses_zero=True,
        predicate='uint32(status[a1] ^ 0xffffd8ee) < 1; selected status=0 => expected v0=0',
        first_branch='Observed missing call has v0=0x2c5300 under policy=1. Actual generated caller tests this nonzero value before delay-slot replacement; 0x242158 -> 0x2421a8 -> UI+0x344=0. Correct predicate on the observed slot would not take that branch.',
        limit='Missing-call inputs are observed; downstream branch/store is a generated-code inference, not a new PC/store tap. Full attribution of the later message is not claimed. No second gap was repaired.'))
    put('e11a-join.json',dict(copy_pairs=pairs,copy_rgb_differences=copy['full_rgb_differences'],
        display_rgb_nonblack=frames['display']['rgb_nonblack'],present_matches=frames['field_present_matches'],host_present_exact=True,
        dynamic_query_pairs=321,query_missing=0,first_remaining_entry='0x2c5300',sibling_residual='0x2c5358',
        selected_outcome='ii',tap_tail=tail,function_lines=progress['function_lines'],function_stack_closed=True))
    print('copy 5/5; packet-derived RGB differences 0; field Present 4/4; host exact')
    print('query pairs 321; GetInfo 12; Sync 15; UI pending cleared; remaining entry 0x2c5300')
    print('# E11 JOIN TAIL COMPLETE')


if __name__=='__main__':main()
