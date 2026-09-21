"""Read E17 runtime-closed observations; never synthesize a source footer."""
from e17_io import read_capture
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
    assert sum(l.startswith('# E15 CLOSURE') for l in lines)==1
    assert sum(l.startswith('# E7 SHUTDOWN') for l in lines)==1
    assert end['events']==len(rows) and end['bootTruncated']==end['boundaryTruncated']==end['packetTruncated']==0
    assert scope['calls']==scope['returned']+scope['unwound'] and scope['pending']==scope['registrationTruncated']==0
    assert scope['calls']==sum(r['kind']=='mpeg-call' for r in rows)
    assert scope['returned']==sum(r['kind']=='mpeg-return' for r in rows)
    assert scope['unwound']==sum(r['kind']=='mpeg-unwind' for r in rows)
    assert scope['selections']==sum(r['kind']=='mpeg-selected' for r in rows)
    assert scope['invocations']==sum(r['kind']=='mpeg-call' and r.get('callback')==1 for r in rows)
    boot=boundary=0
    for line,row in zip((l for l in lines if l.startswith('seq=')),rows):
        in_window=(end['arm']<=row['tick']<=end['arm']+1) if end['aligned'] else (599<=row['tick']<=603)
        if in_window:boundary+=len((line+'\n').encode())
        else:boot+=len((line+'\n').encode())
    assert (boot,boundary)==(end['bootBytes'],end['boundaryBytes'])
    return rows,lines[-1]
