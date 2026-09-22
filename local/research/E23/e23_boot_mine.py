"""Mine the e23a boot: demand verdict, parser receipt, and the producer/source watch verdict."""
import re
from e23_common import *
from e23_closed_events import tap
from e23_parser_receipt import receipt
from e23_mine import fixture_cadence
RUN=P/'run'
cfg=json.loads((E/'e23a-config.json').read_text())
res=json.loads((E/'e23a-result.json').read_text())
tapfile=Path(cfg['paths']['e7_dir'])/'e7-events.txt'
rows,footer=tap(tapfile)
cad=fixture_cadence(tapfile)
park=[r for r in rows if r['kind']=='mpeg-wait']
park_seq=park[0]['seq'] if park else None
park_tick=park[0]['tick'] if park else None

# The watch verdict: guest writes to the producer/source structures, split by
# whether they land BEFORE or AFTER the MPEG caller parks.
PRODUCER=[int(x,16) for x in cfg['watch_addresses']][-8:]
log=Path(cfg['paths']['boot_log'])
watch=[]
pattern=re.compile(r'\[diag:watch\] addr=0x([0-9a-f]+) width=(\d+) value=0x([0-9a-f]+)(.*)')
lines=log.read_text(errors='replace').splitlines()
# The park is ordered against the watch hits IN THE SAME STREAM: the runtime
# prints '[MPEG:GetPicture] waiting' from getMpegPicture immediately before
# waitExternal, so its line number splits before-park from after-park.
park_line=next((i for i,l in enumerate(lines) if '[MPEG:GetPicture] waiting' in l), None)
assert park_line is not None, 'no park marker in the boot log; the split is undefined'
for i,line in enumerate(lines):
    m=pattern.search(line)
    if not m: continue
    addr=int(m.group(1),16);width=int(m.group(2))
    hit=[w for w in PRODUCER if addr < w+8 and w < addr+width]
    if hit:
        extra={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',m.group(4))}
        watch.append(dict(line=i+1,after_park=i>park_line,addr=hex(addr),width=width,
                          value='0x'+m.group(3),watched=[hex(w) for w in hit],**extra))
total_watch_lines=sum('[diag:watch]' in l for l in lines)
after=[w for w in watch if w['after_park']]
parser_dir=Path(cfg['paths']['parser_dir'])
parser=None
if (parser_dir/'parser-events.txt').exists():
    r=receipt(parser_dir);parser=dict(footer=r['footer'],rows=len(r['rows']),payload_bytes=r['payload_bytes'])
    for name in ('parser-events.txt','parser-input.bin'):
        (E/'observed').mkdir(exist_ok=True)
        (E/'observed'/name).write_bytes((parser_dir/name).read_bytes())
out=dict(utc=utc(),bound=res['bound'],rc=res['rc'],elapsed_s=res['elapsed_s'],
         e7_footer=footer,events=len(rows),cadence={k:v for k,v in cad.items() if k!='sequence'},
         park=dict(seq=park_seq,tick=park_tick,present=bool(park)),
         producer_watch_addresses=[hex(x) for x in PRODUCER],
         diag_watch_lines_total=total_watch_lines,
         boot_log_lines=len(lines),park_marker_line=park_line+1,
         lines_after_park=len(lines)-(park_line+1),
         producer_watch_hits=len(watch),producer_watch_hits_after_park=len(after),
         producer_watch_hits_before_park=len(watch)-len(after),
         last_producer_watch_line=watch[-1]['line'] if watch else None,
         producer_watch_rows_after_park=after[:64],
         producer_watch_rows=watch[:64],parser=parser)
save('e23a-boot.json',out)
print(json.dumps({k:v for k,v in out.items() if k not in ('producer_watch_rows','e7_footer','parser')},indent=2))
print('E7 footer:',footer)
if parser:print('PARSER footer:',json.dumps(parser['footer']))
print('# E23 BOOT MINE TAIL COMPLETE')
