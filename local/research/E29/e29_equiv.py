"""E29 Mission 3, Boot 1 -- flag-OFF EQUIVALENCE against the PRE-REGISTERED bar.

The bar was computed from e28a BEFORE the branch was cut (pre-registration-pass-
{1,2}.json). Every row is an exact value, not "same". If any row misses, the
bypass is CONTAMINATED: table + STOP, and Boot 2 does not happen.
"""
import re, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
LABEL = sys.argv[1] if len(sys.argv) > 1 else 'e29a'
RUN = P / 'run'
BOOT = RUN / f'boot-{LABEL}-1.log'
PARK = RUN / f'park-{LABEL}-1/park-snapshot.txt'
PARSER = RUN / f'{LABEL}-parser/parser-events.txt'
FEED = RUN / f'{LABEL}-parser/parser-input.bin'

bar = json.loads((E / 'pre-registration-pass-1.json').read_text())['equivalence_bar']
lines = BOOT.read_text(errors='replace').splitlines()
def n(pat): return sum(1 for l in lines if l.startswith(pat))

park_text = PARK.read_text(errors='replace') if PARK.exists() else ''
t1 = [l.strip() for l in park_text.splitlines() if ' id=1 ' in l]
closure = [l for l in PARSER.read_text(errors='replace').splitlines()
           if l.startswith('# E21 PARSER CLOSURE')] if PARSER.exists() else []
def field(line, key):
    m = re.search(re.escape(key) + r'=([^\s]+)', line)
    return m.group(1) if m else None
cl = closure[0] if closure else ''

# the watch ledger: last value stored to the queue head and byte count
emits = {}
for l in lines:
    if l.startswith('[diag:watch]'):
        m = re.search(r'addr=(0x[0-9a-f]+).*?val(?:ue)?=(0x[0-9a-f]+)', l)
        if m: emits.setdefault(m.group(1), []).append(m.group(2))

rows = []
def row(name, expect, got, ok=None):
    rows.append(dict(row=name, expect=expect, got=got,
                     pass_=(expect == got) if ok is None else ok))

row('[MPEG:GetPicture] waiting count', 1, n('[MPEG:GetPicture] waiting'))
row('[MPEG:feedES] count', 1, n('[MPEG:feedES]'))
row('[MPEG:feed] count', 1, n('[MPEG:feed] '))
row('[MPEG:GetPicture:FRAME] count', 0, n('[MPEG:GetPicture:FRAME]'))
row('[MPEG:DEV-SKIP-MOVIE] count (flag OFF => 0)', 0, n('[MPEG:DEV-SKIP-MOVIE]'))
park_line = t1[0] if t1 else None
row('park thread 1 pc/ra/wait', 'wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028',
    None if not park_line else ' '.join(park_line.split()[2:5]),
    ok=bool(park_line) and 'wait=Mpeg:0' in park_line and 'pc=0x3b1028' in park_line
       and 'ra=0x3b1028' in park_line)
row('park chain', '[0x3b1028]', 'chain=[0x3b1028]' in (park_line or ''), ok='chain=[0x3b1028]' in (park_line or ''))
row('feed vector bytes', 5040, FEED.stat().st_size if FEED.exists() else None)
row('feed vector sha256', bar['feed_vector']['sha256'], sha(FEED) if FEED.exists() else None)
for k in ('parseCalls', 'offered', 'consumed', 'packets', 'frames', 'errors', 'pending'):
    row(f'parser closure {k}', bar['parser_closure'][k], field(cl, k))
row('queue head 0xd486f8 last value', '0xd49b14',
    emits.get('0xd486f8', [None])[-1] if emits.get('0xd486f8') else None)
row('queue bytes 0xd486f4 last value', '0x696e0',
    emits.get('0xd486f4', [None])[-1] if emits.get('0xd486f4') else None)
# The driver arms ONE vector of 243: 1 + 7 display + 7 offsets + 4 + 10 carried
# singles + 214 from watch-set.json (210 tiered + 4 producer singles). That 243
# is E28's number, carried unchanged as the brief requires.
_armed = len(json.loads((E / f'{LABEL}-config.json').read_text())['watch_addresses'])
row('watch vector entries', 243, _armed)
row('flag absent from boot env', None,
    json.loads((E / f'{LABEL}-config.json').read_text())['skip_movie_flag'])

green = all(r['pass_'] for r in rows)
save(f'equivalence-{LABEL}.json', dict(utc=utc(), label=LABEL,
     bar_source='pre-registration-pass-1.json (written before the branch was cut)',
     rows=rows, green=green,
     verdict='EQUIVALENT to e28a on every pre-registered row' if green else 'CONTAMINATED'))
w = max(len(r['row']) for r in rows)
for r in rows:
    print(f"{'PASS' if r['pass_'] else 'MISS'}  {r['row']:<{w}}  expect={r['expect']!r}  got={r['got']!r}")
print('# E29 EQUIVALENCE TAIL COMPLETE label=%s green=%s' % (LABEL, '1' if green else '0'))
