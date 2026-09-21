"""Read E15 runtime-closed observations; never synthesize a source footer."""
from e15_io import read_capture
def fields(line):
    row={}
    for item in line.split():
        if '=' not in item:continue
        k,v=item.split('=',1)
        try:row[k]=int(v,0)
        except ValueError:row[k]=v
    return row
def tap(path, *, allow_missing_footer=False):
    data=read_capture(path);assert data.endswith(b'\n')
    lines=data.decode().splitlines();rows=[fields(l) for l in lines if l.startswith('seq=')]
    assert [r['seq'] for r in rows]==list(range(1,len(rows)+1))
    closed=lines[-1].startswith('# E7 SHUTDOWN') and lines[-2].startswith('# E15 CLOSURE')
    if not closed:
        assert allow_missing_footer, 'Required runtime shutdown footers absent'
        # Preserve positive rows for a qualified partial analysis. This does not
        # supply counters/flags or turn the failed closure gate into a pass.
        return rows, None
    end=fields(lines[-1]);scope=fields(lines[-2])
    assert end['events']==len(rows) and end['bootTruncated']==end['boundaryTruncated']==end['packetTruncated']==0
    assert scope['calls']==scope['returned']+scope['unwound'] and scope['pending']==scope['registrationTruncated']==0
    return rows,lines[-1]
