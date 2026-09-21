#!/usr/bin/env python3
"""Authorized single predicate row, after baseline regression and fresh admission."""
import hashlib,json,os,shutil,datetime
from pathlib import Path
E=Path(__file__).resolve().parent
P=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    gate=json.loads((E/'checkpoint.json').read_text());assert gate['suite_rc']==gate['binding_absent_rc']==0 and gate['binding_present_rc']==1
    admission=json.loads((E/'admission-before-edit.json').read_text());assert admission['admitted'] and admission['headroom_met']
    fresh=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free=shutil.disk_usage('/private/tmp').free,required=3489660928)
    (E/'admission-at-edit.json').write_text(json.dumps(fresh,indent=2)+'\n')
    assert fresh['free']>=fresh['required'],'Stop before CSV mutation: fresh admission unmet'
    before=P.read_bytes();assert hashlib.sha256(before).hexdigest()=='c17db90b72db490772a649eb64b91487d54d1602b258be2e3205e2e7b039c6aa'
    assert b'\r' not in before and b'sub_002C5300,' not in before and b'sub_002C5358,' not in before
    assert before.count(b'sub_002C5140,0x2c5140,0x2c5168,0x28\n')==1
    lines=before.splitlines(keepends=True);pos=None
    for i,line in enumerate(lines):
        cells=line.decode().strip().split(',')
        if len(cells)>1 and cells[1].startswith('0x') and int(cells[1],16)>0x2c5300:pos=i;break
    assert pos is not None
    row=b'sub_002C5300,0x2c5300,0x2c5320,0x20\n'
    assert lines[pos-1]==b'sub_002C52D8,0x2c52d8,0x2c5320,0x48\n'
    after=b''.join(lines[:pos]+[row]+lines[pos:])
    assert hashlib.sha256(after).hexdigest()=='41024f83a9e95408a48dbb91336db52b88f0b6fc7335a91eb6719479679f363d'
    P.write_bytes(after)
    rec=dict(path=str(P),line=pos+1,row=row.decode().strip(),previous=lines[pos-1].decode().strip(),following=lines[pos].decode().strip(),before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest())
    (E/'predicate-map-edit.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
    assert after.replace(row,b'',1)==before
    print('# E12 MAP EDIT TAIL COMPLETE one row; prior owner unchanged')
if __name__=='__main__':main()
