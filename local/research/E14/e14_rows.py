#!/usr/bin/env python3
"""Verify each authorized row against raw ELF, baseline owner and I-lane output."""
import gzip,hashlib,json,re,struct
from pathlib import Path
from e14_static import Elf,ROOT
E=Path(__file__).resolve().parent;R=ROOT.parent/'PS2Recomp'
SPECS=[
    (0x14f2a8,0x14f35c,0x14f250,12,0x14f354,'740bac80'),
    (0x156750,0x1567b8,0x1565c8,13,0x1567b0,'aa6b35d8'),
    (0x243a80,0x243ab0,0x243a40,14,0x243aa8,'f75aeb02'),
    (0x395730,0x395750,0x3956e8,11,0x395748,'8dbfb208'),
    (0x3a0158,0x3a0290,0x3a0048,15,0x3a0284,'cbc6a2ad'),
]
def digest(data):return hashlib.sha256(data).hexdigest()
def annotations(data):
    return {int(a,16):int(w,16) for a,w in re.findall(r'// (0x[0-9a-f]+): (0x[0-9a-f]+)',data.decode())}
def insert_rows(data,rows):
    lines=data.splitlines(keepends=True)
    for row in rows:
        start=int(row.split(',')[1],16)
        pos=next(i for i,l in enumerate(lines) if len(l.split(b','))>1 and l.split(b',')[1].startswith(b'0x') and int(l.split(b',')[1],16)>start)
        lines.insert(pos,(row+'\n').encode())
    return b''.join(lines)
def main():
    elf=Elf(ROOT);csv=(R/'games/ssx3/ssx3-functions.sweep.csv').read_bytes()
    assert digest(csv)=='0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4'
    cross=json.loads((E/'expected-i17-rows.json').read_text())['i17_only_rows']
    dest=E/'row-sources';dest.mkdir(exist_ok=True);records=[]
    for start,end,owner,lane,ret,prefix in SPECS:
        row=f'sub_{start:08X},{start:#x},{end:#x},{end-start:#x}'
        current=R/f'ps2xRuntime/src/runner/sub_{owner:08X}_0x{owner:x}.cpp'
        iroot=Path(f'/Volumes/Extreme SSD/ps2x-i{lane}/codegen-output')
        prior=iroot/current.name;entry=iroot/f'sub_{start:08X}_0x{start:x}.cpp'
        a=current.read_bytes();b=prior.read_bytes();c=entry.read_bytes()
        ownwords=annotations(a);iwords=annotations(b);entrywords=annotations(c)
        raw=b''.join(struct.pack('<I',elf.word(pc)) for pc in range(start,end,4))
        reasons=[]
        if row not in cross:reasons.append('row disagrees with I17 cross-check')
        if row not in (E/f'I{lane}-row-receipts.txt').read_text():reasons.append('row missing from originating report')
        if a!=b:reasons.append('baseline owner bytes differ from I-lane owner')
        if not digest(c).startswith(prefix):reasons.append('I-lane entry hash disagrees with originating report')
        if f'// Address: {start:#x} - {end:#x}' not in c.decode():reasons.append('I-lane entry bounds differ')
        if elf.word(ret)!=0x03e00008 or ret+8>end:reasons.append('return/delay-slot bound differs')
        omitted={}
        for label,words in [('baseline',ownwords),('I-owner',iwords),('I-entry',entrywords)]:
            missing=[pc for pc in range(start,end,4) if pc not in words]
            omitted[label]=[hex(pc) for pc in missing]
            bad=[pc for pc in range(start,end,4) if (pc in words and words[pc]!=elf.word(pc)) or (pc not in words and elf.word(pc)!=0)]
            if bad:reasons.append(f'{label} raw words disagree at {[hex(pc) for pc in bad]}')
        for label,data in [('baseline-owner',a),('I-owner',b),('I-entry',c)]:
            (dest/f'{start:x}-{label}.cpp.gz').write_bytes(gzip.compress(data,mtime=0))
        (dest/f'{start:x}-guest.bin').write_bytes(raw)
        records.append(dict(start=hex(start),end=hex(end),owner=hex(owner),lane=f'I{lane}',row=row,row_hex=(row+'\n').encode().hex(),
            source_paths=dict(baseline=str(current),i_owner=str(prior),i_entry=str(entry)),
            baseline_owner_sha256=digest(a),i_owner_sha256=digest(b),i_entry_sha256=digest(c),guest_bytes=len(raw),guest_sha256=digest(raw),
            elided_zero_nops=omitted,return_pc=hex(ret),verified=not reasons,exclusion_reasons=reasons))
    good=[r['row'] for r in records if r['verified']]
    predicted=insert_rows(csv,good)
    result=dict(rows=records,verified_count=len(good),excluded_count=len(records)-len(good),before_csv_sha256=digest(csv),predicted_csv_sha256=digest(predicted),csv_modified=False)
    (E/'row-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in records:print(r['row'], 'VERIFIED' if r['verified'] else r['exclusion_reasons'])
    print('Expected CSV SHA256:',result['predicted_csv_sha256'])
    assert len(good)>=3,'Stop: fewer than three rows verify'
    print('# E14 ROW VERIFICATION TAIL COMPLETE — no CSV mutation')
if __name__=='__main__':main()
