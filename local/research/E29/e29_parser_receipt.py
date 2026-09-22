"""Verify real parser API source closure, not appended synthetic footers."""
from pathlib import Path
from e29_closed_events import fields

def fnv(data):
    h=14695981039346656037
    for b in data:h=((h^b)*1099511628211)&((1<<64)-1)
    return h

def receipt(directory, *, expect_proof=None, expect_exit=None):
    p=Path(directory);data=(p/'parser-events.txt').read_bytes();payload=(p/'parser-input.bin').read_bytes()
    assert data.endswith(b'\n')
    lines=data.decode().splitlines();assert lines[-1].startswith('# E21 PARSER CLOSURE ')
    assert sum(l.startswith('# E21 PARSER CLOSURE ') for l in lines)==1
    end=fields(lines[-1]);rows=[fields(l) for l in lines[:-1]]
    assert [r['seq'] for r in rows]==list(range(1,len(rows)+1))
    assert end['events']==len(rows) and end['eventBytes']==sum(len((l+'\n').encode()) for l in lines[:-1])
    assert end['pending']==end['textTruncated']==end['payloadTruncated']==end['ioErrors']==0
    assert end['returned']==end['parseCalls']+end['sendCalls']+end['receiveCalls']
    assert len(payload)==end['payloadBytes']
    entered=[r for r in rows if r['kind']=='parse-enter'];returned=[r for r in rows if r['kind']=='parse-return']
    send=[r for r in rows if r['kind']=='send-return'];recv=[r for r in rows if r['kind']=='receive-return']
    assert len(entered)==len(returned)==end['parseCalls'] and len(send)==end['sendCalls'] and len(recv)==end['receiveCalls']
    assert [r['call'] for r in entered]==[r['call'] for r in returned]==list(range(1,len(entered)+1))
    assert sum(max(0,r['used']) for r in returned)==end['consumed']
    assert sum(r['packetSize']>0 for r in returned)==end['packets']
    assert sum(max(0,r['packetSize']) for r in returned)==end['packetBytes']
    assert sum(r['rc']==0 for r in recv)==end['frames']
    assert sum(max(0,r['size']) for r in entered)==end['offered']
    assert sum(r['eof'] for r in rows if r['kind']=='send-enter')==end['sendEof']
    # 1:1 forwarding: exactly one backend entry per observed API call.
    assert end['backendParse']==end['parseCalls'] and end['backendSend']==end['sendCalls'] and end['backendReceive']==end['receiveCalls']
    assert end['bindingChecks']==4 and end['recursionGuards']==0
    for r in entered:
        b=payload[r['payloadOffset']:r['payloadOffset']+r['kept']]
        assert len(b)==r['kept']==max(0,r['size'])
        if b:assert fnv(b)==r['fnv64'] and b[:64].hex()==str(r['first64']).zfill(len(b[:64])*2)
    bindings=[r for r in rows if r['kind']=='binding']
    assert len(bindings)==4 and all(r['valid']==1 for r in bindings)
    if expect_proof is not None:assert end['proof']==expect_proof
    if expect_exit is not None:assert (end['reason'],end['rc'])==expect_exit
    return dict(footer=end,rows=rows,payload_bytes=len(payload),text_bytes=len(data),count_match=True)
