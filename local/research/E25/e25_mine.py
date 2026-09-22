"""Join the complete-feed demand cadence: suite counters, per-parse-call table, fixture E7 tap."""
import re, sys
from e25_common import *
from e25_parser_receipt import receipt
from e25_closed_events import tap

TESTS=['R1 delivers','R2 re-enters','R3 resumes','R4 ignores','R5 invalidates','R6 leaves']

def suite_groups(path):
    """Attribute every [MPEG:*] line to the test whose [Run] line precedes it."""
    groups={};current=None
    for line in Path(path).read_text(errors='replace').splitlines():
        plain=re.sub(r'\x1b\[[0-9;]*m','',line)
        run=re.search(r'\[Run\]:\s*(.+?)(?=\s*\[MPEG:|$)',plain)
        if run:
            current=run.group(1).strip();groups.setdefault(current,[])
        for hit in re.findall(r'(\[MPEG:[^\n]*)',plain):
            if current is not None:groups.setdefault(current,[]).append(hit.strip())
    return groups

def mpeg_fields(line):
    row=dict(tag=line.split(']')[0].lstrip('['))
    for k,v in re.findall(r'(\w+)=([^\s]+)',line):
        try:row[k]=int(v,0)
        except ValueError:row[k]=v
    return row

def parse_table(directory):
    """Decompose the observer event stream into per-AddBs feed episodes."""
    r=receipt(directory)
    rows=r['rows'];episodes=[];current=None;order=[]
    for row in rows:
        kind=row['kind']
        if kind=='parse-enter':
            # The host feed loop re-offers the UNCONSUMED tail of the same
            # sceMpegAddBs buffer each iteration, so a continuation is exactly
            # `offered == previous offered - previous used`. Anything else is a
            # fresh offering from a new sceMpegAddBs / flush entry.
            if current is None or row['size']!=current['expectedNext']:
                current=dict(feedBytes=row['size'],startOffset=row['payloadOffset'],calls=[],
                             packets=0,frames=0,sends=0,receives=0,eofSends=0,expectedNext=None)
                episodes.append(current)
            current['calls'].append(dict(call=row['call'],offered=row['size'],offset=row['payloadOffset'],
                                          fnv64=hex(row['fnv64'])))
            order.append(('parse-enter',row['call']))
        elif kind=='parse-return' and current is not None:
            last=current['calls'][-1];last.update(used=row['used'],packetSize=row['packetSize'],
                                                  cumulativeConsumed=row['consumed'],packetsAfter=row['packets'])
            current['expectedNext']=last['offered']-row['used']
            if row['packetSize']>0:current['packets']+=1
            order.append(('parse-return',row['call']))
        elif kind=='send-enter' and current is not None:
            current['sends']+=1;current['eofSends']+=row['eof'];order.append(('send',row['call']))
        elif kind=='receive-return' and current is not None:
            current['receives']+=1
            if row['rc']==0:current['frames']+=1
            current['calls'][-1].setdefault('receives',[]).append(dict(rc=row['rc'],width=row['width'],
                                                                       height=row['height'],framesAfter=row['frames']))
            order.append(('receive',row['call']))
    for e in episodes:
        e.pop('expectedNext')
        e['parseCalls']=len(e['calls'])
        e['consumed']=sum(c.get('used',0) for c in e['calls'])
    return dict(footer=r['footer'],episodes=episodes,order=order)

def fixture_cadence(tapfile):
    rows,footer=tap(tapfile)
    kinds={}
    for r in rows:kinds[r['kind']]=kinds.get(r['kind'],0)+1
    sequence=[dict(seq=r['seq'],tick=r['tick'],kind=r['kind'],thread=r.get('thread'),
                   target=hex(r['target']) if isinstance(r.get('target'),int) else r.get('target'),
                   callback=r.get('callback'),matched=r.get('matched'),requested=r.get('requested'),
                   v0=hex(r['v0']) if isinstance(r.get('v0'),int) else None,
                   pc=hex(r['pc']) if isinstance(r.get('pc'),int) else None)
              for r in rows]
    return dict(footer=footer,kind_counts=kinds,sequence=sequence,
                producerFirings=sum(1 for r in rows if r['kind']=='mpeg-call' and r.get('callback')==1),
                addBs=sum(1 for r in rows if r['kind']=='mpeg-input'),
                completions=sum(1 for r in rows if r['kind']=='mpeg-complete'),
                completionsMatched=sum(r.get('matched',0) for r in rows if r['kind']=='mpeg-complete'),
                parks=sum(1 for r in rows if r['kind']=='mpeg-wait'))
