"""Recheck E14's established five receipts against current inputs; no derivation."""
import gzip,re,struct
from e17_common import *
old=json.loads((E/'e14-row-verification.json').read_text())
elf=(P/'SLUS_207.72').read_bytes();assert hashlib.sha256(elf).hexdigest()=='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
phoff=struct.unpack_from('<I',elf,0x1c)[0];ents,count=struct.unpack_from('<HH',elf,0x2a)
segments=[struct.unpack_from('<8I',elf,phoff+i*ents) for i in range(count)]
def word(pc):
    for typ,off,va,pa,fs,ms,flags,align in segments:
        if typ==1 and va<=pc<va+fs:return struct.unpack_from('<I',elf,off+pc-va)[0]
    raise AssertionError(hex(pc))
records=[]
for r in old['rows']:
    n=dict(r);reasons=[];start,end=int(r['start'],16),int(r['end'],16)
    for kind,key,pathkey in [('baseline-owner','baseline_owner_sha256','baseline'),('I-owner','i_owner_sha256','i_owner'),('I-entry','i_entry_sha256','i_entry')]:
        retained=gzip.decompress((E/'row-sources'/f'{start:x}-{kind}.cpp.gz').read_bytes())
        if hashlib.sha256(retained).hexdigest()!=r[key]:reasons.append(kind+' retained hash mismatch')
        path=Path(r['source_paths'][pathkey])
        if not path.exists():reasons.append(kind+' current path missing');continue
        data=path.read_bytes()
        if data!=retained:reasons.append(kind+' current bytes changed from E14')
        comments={int(a,16):int(v,16) for a,v in re.findall(r'// (0x[0-9a-f]+): (0x[0-9a-f]+)',data.decode())}
        if any(comments.get(pc,0)!=word(pc) for pc in range(start,end,4)):reasons.append(kind+' raw ELF mismatch')
    raw=b''.join(struct.pack('<I',word(pc)) for pc in range(start,end,4))
    if raw!=(E/'row-sources'/f'{start:x}-guest.bin').read_bytes():reasons.append('raw slice changed')
    if (r['row']+'\n').encode().hex()!=r['row_hex']:reasons.append('row bytes mismatch')
    if r['row'] not in (E/f"{r['lane']}-row-receipts.txt").read_text():reasons.append('origin receipt mismatch')
    if word(int(r['return_pc'],16))!=0x03e00008 or int(r['return_pc'],16)+8>end:reasons.append('return bounds changed')
    n.update(verified=not reasons,exclusion_reasons=reasons);records.append(n)
csv=(R/'games/ssx3/ssx3-functions.sweep.csv').read_bytes();assert hashlib.sha256(csv).hexdigest()==old['before_csv_sha256']
lines=csv.splitlines(keepends=True)
for r in records:
    assert (r['row']+'\n').encode() not in lines
    pos=next(i for i,l in enumerate(lines) if len(l.split(b','))>1 and l.split(b',')[1].startswith(b'0x') and int(l.split(b',')[1],16)>int(r['start'],16))
    lines.insert(pos,(r['row']+'\n').encode())
predicted=b''.join(lines);digest=hashlib.sha256(predicted).hexdigest()
result=dict(utc=utc(),rows=records,verified_count=sum(r['verified'] for r in records),before_csv_sha256=hashlib.sha256(csv).hexdigest(),predicted_csv_sha256=digest,csv_modified=False)
save('row-verification.json',result)
assert result['verified_count']==5 and digest==old['predicted_csv_sha256']=='7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba',result
(E/'predicted.csv').write_bytes(predicted)
for r in records:print(r['row'],'E14/current owner/I-lane/ELF bytes agree')
print('Predicted CSV',digest);print('# E17 ROW REVERIFICATION TAIL COMPLETE')
