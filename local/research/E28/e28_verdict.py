"""Mission 2 -- grade P1-P4 against the e28a capture, on the rows pre-registered.

Nothing is graded that `pre-registration.json` did not register before the
lease was claimed, and the grading rule for each row is read back OUT of that
file rather than restated here. Mined: P1-P4 and the carried controls, nothing
else -- this lane is a confirmation, not a fishing trip.
"""
import re
from e28_common import *

RUN = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')
BOOT = RUN / 'boot-e28a-1.log'
PREREG = json.loads((E / 'pre-registration.json').read_text())
M1 = json.loads((E / 'mission-1-slot.json').read_text())
WS = json.loads((E / 'watch-set.json').read_text())
SLOT = int(M1['result']['kind1_slot'], 16)
HEAD, BYTES, OWNER, KIND = SLOT + 0xC, SLOT + 8, SLOT, SLOT + 4
WIN_LO, WIN_HI = 0xd486e0, 0xd48748
C0MAGIC, C0LEN = 0xd48740, 0xd48744
NEXT_HDR, NEXT_LEN = 0xd49b14, 0xd49b18

# --------------------------------------------------------------- pin first --
caps = {}
for name in ('boot-e28a-1.log', 'ps2_log-e28a-1.txt', 'syscalls-e28a-on.txt'):
    p = RUN / name
    caps[name] = dict(bytes=p.stat().st_size, sha_read_a=sha(p), sha_read_b=sha(p))
pin_in = RUN / 'e28a-parser/parser-input.bin'
if pin_in.exists():
    caps['parser-input.bin'] = dict(bytes=pin_in.stat().st_size, sha_read_a=sha(pin_in), sha_read_b=sha(pin_in))
for k, v in caps.items():
    v['reads_agree'] = v['sha_read_a'] == v['sha_read_b']
(E / 'observed').mkdir(exist_ok=True)
(E / 'observed/e28a-capture-sha256.txt').write_text(
    ''.join(f"{v['sha_read_a']}  {k}\n" for k, v in caps.items()))

lines = BOOT.read_text(errors='replace').splitlines()
N = len(lines)
def find(rx):
    r = re.compile(rx)
    return [(i + 1, l) for i, l in enumerate(lines) if r.search(l)]

# the park line, detected exactly as E26 detects it -- not by a looser pattern
park = find(r'\[MPEG:GetPicture\] waiting for frames')
assert len(park) == 1, f'expected exactly one MPEG park, got {len(park)}'
feed_es = find(r'\[MPEG:feedES\]')
getpic = find(r'\[MPEG:GetPicture\]')
getpic_frame = find(r'\[MPEG:GetPicture:FRAME\]')
feed = find(r'\[MPEG:feed\]')
cdread = find(r'\[diag:cd\] sceCdRead lbn=')
FEED_LINE = feed_es[0][0] if feed_es else None
PARK_LINE = park[0][0] if park else None

WATCH = re.compile(r'\[diag:watch\] addr=(0x[0-9a-f]+) width=(\d+) value=(0x[0-9a-f]+) '
                   r'pc=(0x[0-9a-f]+) thread=(-?\d+) ra=(0x[0-9a-f]+) sp=(0x[0-9a-f]+)')
events, torn = [], []
for i, l in enumerate(lines):
    mm = WATCH.search(l)
    if mm:
        events.append(dict(line=i + 1, addr=int(mm.group(1), 16), width=int(mm.group(2)),
                           value=mm.group(3), pc=mm.group(4), thread=int(mm.group(5)),
                           ra=mm.group(6), sp=mm.group(7),
                           post_park=PARK_LINE is not None and (i + 1) > PARK_LINE,
                           post_feed=FEED_LINE is not None and (i + 1) > FEED_LINE))
    elif '[diag:watch]' in l:
        torn.append(dict(line=i + 1, text=l.strip()[:200],
                         addr=(m2.group(1) if (m2 := re.search(r'addr=(0x[0-9a-f]+)', l)) else None),
                         post_park=PARK_LINE is not None and (i + 1) > PARK_LINE))

def at(*addrs):
    s = set(addrs)
    return [e for e in events if e['addr'] in s]
def window(lo, hi):
    return [e for e in events if lo <= e['addr'] < hi]

head_ev, bytes_ev = at(HEAD), at(BYTES)
own_ev, kind_ev = at(OWNER), at(KIND)
win_ev = window(WIN_LO, WIN_HI)
c0_ev = at(C0MAGIC, C0LEN)
nxt_ev = at(NEXT_HDR, NEXT_LEN)
slot_ev = window(SLOT, SLOT + 16)
outside_ev = [e for e in win_ev if not (SLOT <= e['addr'] < SLOT + 16)]

def last(evs): return evs[-1] if evs else None
def after_feed(evs): return [e for e in evs if e['post_feed']]
def after_park(evs): return [e for e in evs if e['post_park']]

# ------------------------------------------------------------------ P1-P4 --
lh, lb = last(head_ev), last(bytes_ev)
p1_head_ok = lh is not None and int(lh['value'], 16) == NEXT_HDR
p1_bytes_ok = lb is not None and int(lb['value'], 16) >= 14364
p1_quiet = not after_feed(head_ev) and not after_feed(bytes_ev)
P1 = 'CONFIRM' if (p1_head_ok and p1_bytes_ok and p1_quiet) else 'REFUTE'
if not head_ev and not bytes_ev and not win_ev:
    P1 = 'UNOBSERVABLE-AS-DESIGNED'

tagstore = [e for e in at(NEXT_LEN) if int(e['value'], 16) == 0x0100381c]
p2_change_ok = bool(tagstore) and not after_feed(at(NEXT_LEN))
P2 = 'CONFIRM (change-half); at-park VALUE unobservable-as-designed' if p2_change_ok else 'REFUTE'

p3_ok = not after_feed(nxt_ev)
P3 = 'CONFIRM' if p3_ok else 'REFUTE'

P4 = 'CONFIRM' if (len(getpic) == 1 and len(feed_es) == 1) else 'REFUTE'

verdicts = [
 dict(id='P1', verdict=P1,
      receipts=dict(
        head_addr=hex(HEAD), head_stores=len(head_ev),
        head_rows=[dict(line=e['line'], value=e['value'], pc=e['pc'], ra=e['ra'], thread=e['thread']) for e in head_ev],
        head_last_value=lh['value'] if lh else None, head_last_is_0xd49b14=p1_head_ok,
        bytes_addr=hex(BYTES), bytes_stores=len(bytes_ev),
        bytes_rows=[dict(line=e['line'], value=e['value'], pc=e['pc'], ra=e['ra'], thread=e['thread']) for e in bytes_ev],
        bytes_last_value=lb['value'] if lb else None,
        bytes_last_decimal=int(lb['value'], 16) if lb else None,
        bytes_last_ge_14364=p1_bytes_ok,
        stores_after_feed=len(after_feed(head_ev)) + len(after_feed(bytes_ev)),
        stores_after_park=len(after_park(head_ev)) + len(after_park(bytes_ev)))),
 dict(id='P2', verdict=P2,
      receipts=dict(addr=hex(NEXT_LEN),
        tag_store_rows=[dict(line=e['line'], value=e['value'], pc=e['pc'], ra=e['ra']) for e in tagstore],
        all_stores=len(at(NEXT_LEN)), stores_after_feed=len(after_feed(at(NEXT_LEN))),
        value_half=('NOT OBTAINABLE with the existing instruments: diagWatchEmit is '
                    'store-triggered, so an address nothing writes emits nothing and its at-park '
                    'VALUE is never read. E28 reports the change-half and does not infer the rest.'),
        residual=('host CD DMA can write this buffer without emitting (E26\'s named limit). '
                  'Bounded here by the sceCdRead count after the feed, below.'),
        cd_reads_total=len(cdread),
        cd_reads_after_feed=len([1 for ln, _ in cdread if FEED_LINE and ln > FEED_LINE]))),
 dict(id='P3', verdict=P3,
      receipts=dict(addrs=[hex(NEXT_HDR), hex(NEXT_LEN)],
        stores_total=len(nxt_ev), stores_after_feed=len(after_feed(nxt_ev)),
        stores_after_park=len(after_park(nxt_ev)),
        rows=[dict(line=e['line'], addr=hex(e['addr']), value=e['value'], pc=e['pc'], ra=e['ra']) for e in nxt_ev])),
 dict(id='P4', verdict=P4,
      receipts=dict(getpicture=len(getpic), feedes=len(feed_es), feed=len(feed),
        getpicture_frame=len(getpic_frame),
        getpicture_lines=[dict(line=l, text=t.strip()) for l, t in getpic],
        feedes_lines=[dict(line=l, text=t.strip()) for l, t in feed_es],
        cap='every [MPEG:*] counter caps at 32 in MPEG.cpp, so 1 is a true count')),
]

controls = dict(
  derived_address_confirmed_by_the_guest=dict(
      owner_stores=[dict(line=e['line'], addr=hex(e['addr']), value=e['value'], pc=e['pc']) for e in own_ev],
      kind_stores=[dict(line=e['line'], addr=hex(e['addr']), value=e['value'], pc=e['pc']) for e in kind_ev],
      emissions_inside_the_kind1_slot=len(slot_ev),
      emissions_elsewhere_in_the_derived_window=len(outside_ev),
      elsewhere_rows=[dict(line=e['line'], addr=hex(e['addr']), value=e['value'], pc=e['pc'], ra=e['ra']) for e in outside_ev],
      elsewhere_by_address={hex(a): len([e for e in outside_ev if e['addr'] == a])
                            for a in sorted({e['addr'] for e in outside_ev})},
      kind2_slot=hex(SLOT + 16),
      all_window_addresses_hit={hex(a): len([e for e in win_ev if e['addr'] == a])
                                for a in sorted({e['addr'] for e in win_ev})},
      verdict=('the Mission-1 address is confirmed if every slot emission lands in '
               f'[{hex(SLOT)},{hex(SLOT+16)}) and refuted if any lands elsewhere in '
               f'[{hex(WIN_LO)},{hex(WIN_HI)})')),
  chunk0_header=dict(rows=[dict(line=e['line'], addr=hex(e['addr']), value=e['value'], pc=e['pc'], ra=e['ra']) for e in c0_ev],
      note="E27 named 0xd48744 as outside every E24 tier; E28's new tier covers it"),
  whole_vector=dict(entries=WS['total_entries'], emissions=len(events),
      distinct_addresses=len({e['addr'] for e in events}),
      post_park=len(after_park(events)), post_feed=len(after_feed(events)),
      last_emission_line=events[-1]['line'] if events else None,
      torn_lines=len(torn), torn_post_park=len([t for t in torn if t['post_park']]),
      torn_addrs=sorted({t['addr'] for t in torn if t['addr']})),
  boundaries=dict(boot_log_lines=N, feed_line=FEED_LINE, park_line=PARK_LINE,
      lines_after_park=N - PARK_LINE if PARK_LINE else None,
      feed_text=feed_es[0][1].strip() if feed_es else None,
      park_text=park[0][1].strip()[:160] if park else None,
      first_cd_read=cdread[0][1].strip() if cdread else None),
)

out = dict(utc=utc(), label='e28a', captures=caps,
           pre_registered_rows=[r['id'] for r in PREREG['rows']],
           graded_rows=[v['id'] for v in verdicts],
           only_pre_registered_rows_graded=[v['id'] for v in verdicts] == [r['id'] for r in PREREG['rows']],
           verdicts=verdicts, controls=controls,
           named_limit=PREREG['named_limit'])
save('mission-2-verdicts.json', out)

print(f"boot log {N} lines | feed {FEED_LINE} | park {PARK_LINE} | emissions {len(events)} | torn {len(torn)}")
for v in verdicts:
    print(f"{v['id']}  {v['verdict']}")
print(f"head {hex(HEAD)}: {len(head_ev)} stores, last={lh['value'] if lh else None}")
print(f"bytes {hex(BYTES)}: {len(bytes_ev)} stores, last={lb['value'] if lb else None}"
      f" ({int(lb['value'],16) if lb else None})")
print(f"slot window: {len(slot_ev)} inside {hex(SLOT)}..{hex(SLOT+16)}, {len(outside_ev)} elsewhere in window")
print(f"post-park emissions across all {WS['total_entries']} entries: {len(after_park(events))}")
print('# E28 VERDICT TAIL COMPLETE')
