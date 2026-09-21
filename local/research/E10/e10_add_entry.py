#!/usr/bin/env python3
"""The authorized single-row SSX3 busy-query map repair, after DROP preflight."""
import hashlib,json,os
from pathlib import Path
E=Path(__file__).resolve().parent
P=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    gate=json.loads((E/'drop-preflight.json').read_text());assert gate['suite_rc']==gate['binding_rc']==0 and gate['query_absent']
    before=P.read_bytes();assert hashlib.sha256(before).hexdigest()=='b9aae74782fde6ba54671cfe07a9887c0af8ba1aad9d5befc1095e8cfef146ca'
    assert b'\r' not in before and b'sub_002C5140,' not in before
    lines=before.splitlines(keepends=True);pos=None
    for i,line in enumerate(lines):
        cells=line.decode().strip().split(',')
        if len(cells)>1 and cells[1].startswith('0x') and int(cells[1],16)>0x2c5140:pos=i;break
    assert pos is not None
    row=b'sub_002C5140,0x2c5140,0x2c5168,0x28\n'
    after=b''.join(lines[:pos]+[row]+lines[pos:]);P.write_bytes(after)
    rec=dict(path=str(P),line=pos+1,row=row.decode().strip(),previous=lines[pos-1].decode().strip(),following=lines[pos].decode().strip(),before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest())
    (E/'query-map-edit.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
    assert after.replace(row,b'',1)==before
    print('# E10 MAP EDIT TAIL COMPLETE one row; prior owner unchanged')
if __name__=='__main__':main()
