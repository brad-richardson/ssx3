#!/usr/bin/env python3
"""Recheck the five row receipts using only standalone E17 retained bytes."""
import gzip,hashlib,json,re,struct
from pathlib import Path
E=Path(__file__).resolve().parent
record=json.loads((E/'row-verification.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
for row in record['rows']:
    start,end=int(row['start'],16),int(row['end'],16)
    prefix=E/'row-sources'/f'{start:x}'
    raw=Path(str(prefix)+'-guest.bin').read_bytes()
    assert len(raw)==end-start==row['guest_bytes'] and sha(raw)==row['guest_sha256']
    values=struct.unpack('<'+'I'*(len(raw)//4),raw)
    owners=[]
    for kind,key in [('baseline-owner','baseline_owner_sha256'),('I-owner','i_owner_sha256'),('I-entry','i_entry_sha256')]:
        data=gzip.decompress(Path(str(prefix)+f'-{kind}.cpp.gz').read_bytes())
        assert sha(data)==row[key]
        comments={int(a,16):int(w,16) for a,w in re.findall(r'// (0x[0-9a-f]+): (0x[0-9a-f]+)',data.decode())}
        for i,word in enumerate(values):
            pc=start+i*4
            assert comments.get(pc,0)==word
        if kind!='I-entry':owners.append(data)
        else:assert f'// Address: {start:#x} - {end:#x}' in data.decode()
    assert owners[0]==owners[1]
    assert values[(int(row['return_pc'],16)-start)//4]==0x03e00008
    assert (row['row']+'\n').encode().hex()==row['row_hex']
    assert row['verified'] and not row['exclusion_reasons']
    print(row['row'],'retained raw/owners/entry/bounds agree')
assert record['verified_count']==5 and record.get('excluded_count',5-record['verified_count'])==0
print('# E17 STANDALONE BYTE VERIFICATION TAIL COMPLETE')
