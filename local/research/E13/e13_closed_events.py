"""Read the audited closed E13 prefix; never replace a missing raw footer."""
import hashlib,json
from pathlib import Path
from e13_io import read_capture
E=Path(__file__).resolve().parent
def tap(path):
    data=read_capture(path);audit=json.loads((E/'e13a-observation-closure.json').read_text())
    assert hashlib.sha256(data).hexdigest()==audit['raw_sha256'] and data.endswith(b'\n')
    assert audit['complete_newline'] and audit['contiguous_sequences'] and not audit['footer_present']
    rows=[]
    for line in data.decode().splitlines():
        if not line.startswith('seq='):continue
        row={}
        for part in line.split():
            k,v=part.split('=',1)
            try:row[k]=int(v,0)
            except ValueError:row[k]=v
        rows.append(row)
    assert [r['seq'] for r in rows]==list(range(1,len(rows)+1))
    assert rows[-1]==audit['last'] and len(rows)==audit['events']
    return rows,data.decode().splitlines()[-1]
