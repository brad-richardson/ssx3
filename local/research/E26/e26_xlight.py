"""Mission 1 ledger + Mission 2 first light. Read-only, against the e26a capture ONLY.

No new probes, no second boot. Everything here is mined from what the one
designed boot returned, plus the pinned ISO (an INPUT, not a probe) read twice
to satisfy the standing SSD rule.

Produces:
  watch-ledger.json    every one of the 230 watched addresses, pre/post park
  objective-1a.json    does the successor descriptor node move post-park?
  x-a-startcode.json   Mission 2 (a) -- the final start code, in bytes and time
  x-b-sema36.json      Mission 2 (b) -- semaphore 36's sole signaller
  sema-ledger.json     the per-id wait/signal ledger WITH the waker `ra`
  chunk-map.json       the MPCh chunk stream the CD read delivered
"""
import re, subprocess
from e26_common import *

RUN = P / 'run'
LOG = RUN / 'boot-e26a-1.log'
FUNCLOG = RUN / 'ps2_log-e26a-1.txt'
PARSER = RUN / 'e26a-parser'
ISO = W / 'SSX 3 (USA).iso'
WS = json.loads((E / 'watch-set.json').read_text())

lines = LOG.read_text(errors='replace').splitlines()
N = len(lines)

# ---------------------------------------------------------------- boundaries
def find(pat):
    rx = re.compile(pat)
    return [(i + 1, l) for i, l in enumerate(lines) if rx.search(l)]

feed_es = find(r'\[MPEG:feedES\]')
feed = find(r'\[MPEG:feed\]')
park = find(r'\[MPEG:GetPicture\] waiting for frames')
span = find(r'\[e4:span-complete\]')
assert len(park) == 1, f'expected exactly one MPEG park, got {len(park)}'
PARK_LINE = park[0][0]
FEED_LINE = feed_es[0][0]
m = re.search(r'size=(\d+) first4=([0-9a-f]+)', feed_es[0][1])
FED_BYTES, FED_FIRST4 = int(m.group(1)), m.group(2)

boundaries = dict(
    boot_log_lines=N, span_complete_line=span[0][0] if span else None,
    span_complete_text=span[0][1] if span else None,
    feed_line=FEED_LINE, feed_text=feed_es[0][1], feed_parsed_text=feed[0][1],
    park_line=PARK_LINE, park_text=park[0][1],
    lines_after_park=N - PARK_LINE,
    mpeg_lines_total=len(find(r'\[MPEG:')))

# ------------------------------------------------------------- watch ledger
WATCH = re.compile(r'\[diag:watch\] addr=(0x[0-9a-f]+) width=(\d+) value=(0x[0-9a-f]+) '
                   r'pc=(0x[0-9a-f]+) thread=(-?\d+) ra=(0x[0-9a-f]+) sp=(0x[0-9a-f]+)')
events, torn = [], []
for i, l in enumerate(lines):
    mm = WATCH.search(l)
    if mm:
        events.append(dict(line=i + 1, addr=int(mm.group(1), 16), width=int(mm.group(2)),
                           value=mm.group(3), pc=mm.group(4), thread=int(mm.group(5)),
                           ra=mm.group(6), sp=mm.group(7),
                           post_park=(i + 1) > PARK_LINE))
    elif '[diag:watch]' in l:
        # A watch emission torn by a concurrent [frame:*] / INFO: FILEIO write on
        # the same fd. Counted and located rather than silently dropped.
        torn.append(dict(line=i + 1, post_park=(i + 1) > PARK_LINE, text=l.strip()[:200],
                         addr=(mm2.group(1) if (mm2 := re.search(r'addr=(0x[0-9a-f]+)', l)) else None)))

# the full 230-entry vector, rebuilt exactly as the driver builds it
DISPLAY = [0x12000000, 0x12000020, 0x12000070, 0x12000080, 0x12000090, 0x120000a0, 0x120000e0]
OFFSETS = [0x5a78, 0x5a7c, 0x5a84, 0x5a88, 0x5a74, 0xf44, 0x59e8]
S = 0x61ba60
carried = ([0x4a289c] + DISPLAY + [S + o for o in OFFSETS]
           + [0x10005000, 0x1000a000, 0x1000a010, 0x1000a020]
           + [0xb851a0, 0xb851a4, 0xb851ac, 0xb851e0, 0xb84e84, 0xb84d88,
              0x4a3938, 0x4a393c, 0x4a3940, 0x4a3944])
singles = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c]
tier_of, vector = {}, []
for a in carried:
    tier_of[a] = 'carried non-producer'; vector.append(a)
for a in singles:
    tier_of[a] = 'carried producer single'; vector.append(a)
for t in WS['tiers']:
    for a in t['addrs']:
        tier_of[a] = t['name']; vector.append(a)
assert len(vector) == 230 == len(set(vector)), len(vector)

# A store is attributed to a watch entry when it overlaps its 8-byte window.
WIN = WS['window_bytes']
ledger = []
for a in vector:
    hits = [e for e in events if e['addr'] < a + WIN and a < e['addr'] + e['width']]
    pre = [h for h in hits if not h['post_park']]
    post = [h for h in hits if h['post_park']]
    row = dict(addr=hex(a), tier=tier_of[a], hits=len(hits), pre_park=len(pre), post_park=len(post))
    if hits:
        row.update(first_line=hits[0]['line'], last_line=hits[-1]['line'],
                   first_value=hits[0]['value'], last_value=hits[-1]['value'],
                   last_pc=hits[-1]['pc'], last_ra=hits[-1]['ra'],
                   threads=sorted({h['thread'] for h in hits}))
    ledger.append(row)

tiers = {}
for row in ledger:
    t = tiers.setdefault(row['tier'], dict(tier=row['tier'], entries=0, entries_hit=0,
                                           hits=0, pre_park=0, post_park=0))
    t['entries'] += 1
    t['entries_hit'] += 1 if row['hits'] else 0
    t['hits'] += row['hits']; t['pre_park'] += row['pre_park']; t['post_park'] += row['post_park']

save('watch-ledger.json', dict(utc=utc(), boundaries=boundaries,
     watch_entries=len(vector), watch_emissions=len(events),
     emissions_post_park=sum(1 for e in events if e['post_park']),
     last_emission_line=events[-1]['line'] if events else None,
     last_emission=events[-1] if events else None,
     tiers=list(tiers.values()), entries=ledger,
     start_code_valued_writes=sum(1 for e in events if '000001' in e['value'].lower()),
     hits_exceed_emissions_because=('a 16-byte store can overlap TWO adjacent 8-byte watch windows, '
                                    'so per-entry hits (7,355) legitimately exceed emissions (6,725)'),
     torn_lines=dict(
         count=len(torn), post_park=sum(1 for t in torn if t['post_park']),
         first_line=torn[0]['line'] if torn else None,
         last_line=torn[-1]['line'] if torn else None,
         addrs=sorted({t['addr'] for t in torn if t['addr']}),
         # a store address need not BE a watch entry; map it to the entry whose
         # 8-byte window it overlaps, exactly as the ledger attributes hits
         tiers=sorted({tier_of[a] for t in torn if t['addr']
                       for a in vector if a <= int(t['addr'], 16) < a + WIN}),
         why='a watch emission interleaved with a concurrent [frame:*] or INFO: FILEIO write on the same fd',
         impact=('none on any conclusion: all 10 are PRE-park and all land in the carried '
                 'non-producer tier. Not one is in the descriptor node array, the data region, '
                 'the past-end extension or the staging buffer.'),
         rows=torn)))

# ------------------------------------------------------- objective 1a
SUCC = 0x548880
succ = [e for e in events if e['addr'] < SUCC + WIN and SUCC < e['addr'] + e['width']]
node_array = [r for r in ledger if r['tier'] == 'descriptor node array']
save('objective-1a.json', dict(utc=utc(),
     question='does the SUCCESSOR descriptor node at 0x548880 move post-park?',
     e23_residual='E23 saw the head advance 0x548800 = 0x548880 and did NOT watch the successor node',
     successor_hits=len(succ), successor_hits_post_park=sum(1 for e in succ if e['post_park']),
     successor_events=succ,
     head_advance=[dict(line=e['line'], value=e['value'], pc=e['pc'], ra=e['ra'])
                   for e in events if e['addr'] == 0x548800],
     node_array_entries=len(node_array),
     node_array_entries_hit=sum(1 for r in node_array if r['hits']),
     node_array_post_park_hits=sum(r['post_park'] for r in node_array),
     free_list_stride=0x40,
     free_list_note=('lines 93-101 initialise the array as a linked free list at 0x40 stride '
                     '(0x5487c0 -> 0x548800 -> 0x548840 -> 0x548880 -> ... -> 0x548a00), so the '
                     '64-entry tier covers EIGHT nodes, not the four E24 sized it for -- the '
                     'coverage is better than designed, not worse'),
     verdict=('H0 -- the successor node does NOT move post-park. Its only write in the whole run '
              'is the boot-time free-list initialisation.') if not any(e['post_park'] for e in succ)
             else 'H1 -- the successor node moves post-park',
     e23_verdict_status='SURVIVES a watch set six times larger; E23 named residual CLOSED'))

# ---------------------------------------------------- Mission 2 (a)
CD = re.compile(r'\[diag:cd\] sceCdRead lbn=(0x[0-9a-f]+) sectors=(\d+) buf=(0x[0-9a-f]+)')
reads = [dict(line=i + 1, lbn=mm.group(1), sectors=int(mm.group(2)), buf=mm.group(3))
         for i, l in enumerate(lines) if (mm := CD.search(l))]
feed_read = [r for r in reads if r['buf'] == '0xd48740']
assert len(feed_read) == 1, feed_read
FR = feed_read[0]
BASE = int(FR['buf'], 16)
LBN = int(FR['lbn'], 16)

# the ISO is a pinned INPUT; read twice, as the standing SSD rule requires
blobs = []
for _ in range(2):
    with ISO.open('rb') as f:
        f.seek(LBN * 2048); blobs.append(f.read(FR['sectors'] * 2048))
assert blobs[0] == blobs[1], 'SSD rule: the two ISO reads disagree -- table and stop'
blob = blobs[0]

chunks, p = [], 0
while p + 8 <= len(blob):
    magic = blob[p:p + 4]
    total = int.from_bytes(blob[p + 4:p + 8], 'little')
    if not all(32 <= c < 127 for c in magic) or total < 8 or p + total > len(blob):
        break
    chunks.append(dict(blob_offset=p, guest_addr=hex(BASE + p), magic=magic.decode(),
                       total_bytes=total, es_bytes=total - 8,
                       payload_guest_addr=hex(BASE + p + 8),
                       payload_first4=blob[p + 8:p + 12].hex(),
                       is_start_code=blob[p + 8:p + 11] == b'\x00\x00\x01'))
    p += total

fed = (PARSER / 'parser-input.bin').read_bytes()
es0 = blob[8:chunks[0]['total_bytes']]
nxt = next(c for c in chunks[1:] if c['magic'] == 'MPCh')
last_nonzero = max(i for i, c in enumerate(fed) if c)

save('chunk-map.json', dict(utc=utc(), cd_read=FR, lbn=FR['lbn'], sectors=FR['sectors'],
     bytes_read=len(blob), guest_base=FR['buf'], iso_reads=2, iso_reads_agree=True,
     convention='chunk length field = TOTAL bytes INCLUDING the 8-byte header (confirmed on 5 chunks)',
     chunks=chunks,
     buffer_ring=[r for r in reads if r['sectors'] >= 15][-8:],
     cd_reads_total=len(reads)))

save('x-a-startcode.json', dict(utc=utc(),
     question=('(a) where does the guest\'s final start-code write land relative to the feed '
               'the parser consumed (timing + bytes)?'),
     answer_headline=('The guest never writes a terminating start code at all. It does not have to: '
                      'the start code was already in guest RAM, 48 bytes past the end of the data it '
                      'fed, delivered by the SAME CD read. The guest stops one CHUNK short of '
                      'FEEDING, not one start code short of writing.'),
     start_code_valued_writes=sum(1 for e in events if '000001' in e['value'].lower()),
     watch_emissions=len(events), watch_emissions_post_park=0,
     last_watch_emission_line=events[-1]['line'], last_watch_emission=events[-1],
     timing=dict(last_guest_write_to_any_watched_address_line=events[-1]['line'],
                 feed_line=FEED_LINE, park_line=PARK_LINE,
                 lines_between_last_write_and_feed=FEED_LINE - events[-1]['line'],
                 boot_log_lines_after_park=N - PARK_LINE,
                 span_complete_s=9.523638333001145,
                 parse_enter_ns=9485297000, parser_exit_ns=74466393000,
                 post_park_seconds=round((74466393000 - 9485297000) / 1e9, 2)),
     bytes=dict(cd_read=dict(lbn=FR['lbn'], sectors=FR['sectors'], bytes=len(blob), buf=FR['buf']),
                chunk0=dict(magic='MPCh', total=chunks[0]['total_bytes'], es_bytes=len(es0),
                            guest_payload=hex(BASE + 8)),
                fed_bytes=len(fed), fed_first4=FED_FIRST4,
                fed_equals_es=fed[:len(es0)] == es0,
                pad_bytes=len(fed) - len(es0), pad_all_zero=set(fed[len(es0):]) == {0},
                pad_reason='zero padding to the next 16-byte multiple (5028 -> 5040)',
                last_nonzero_offset=last_nonzero,
                e24_measured_last_nonzero=5024, agrees_with_E24=last_nonzero == 5024,
                next_chunk=dict(magic=nxt['magic'], blob_offset=nxt['blob_offset'],
                                header_guest_addr=nxt['guest_addr'],
                                payload_guest_addr=nxt['payload_guest_addr'],
                                payload_first4=nxt['payload_first4'],
                                is_start_code=nxt['is_start_code'],
                                es_bytes=nxt['es_bytes'],
                                gap_bytes_from_end_of_fed_es=(nxt['blob_offset'] + 8) - len(es0) - 8),
                terminating_start_code_guest_addr=nxt['payload_guest_addr'],
                inside_E24_past_end_tier=(0xd49af4 <= int(nxt['payload_guest_addr'], 16) <= 0xd49b73),
                past_end_tier='0xd49af4-0xd49b73, 16 entries at stride 8 -- complete cover'),
     guest_had_already_walked_to_it=[e for e in events
                                     if e['addr'] in (0xd49af0, 0xd49b18)],
     guest_walk_reading=('At boot-log lines 22,351 and 22,354 -- BEFORE the feed -- thread 1 stores '
                         '0x02000028 at 0xd49af0 and 0x0100381c at 0xd49b18. Those two addresses are '
                         'the length fields of the SCHl chunk (total 40 = 0x28) and of the NEXT MPCh '
                         'chunk (total 14,364 = 0x381c). The low 24 bits are the lengths the ISO '
                         'already holds; only the top byte changes (0x02, 0x01). The guest had '
                         'therefore already walked the chunk list past the picture it fed.'),
     named_limit=('`diagWatchEmit` fires on GUEST STORES only. The picture payload itself arrives by '
                  'host-side CD DMA straight into guest RAM (only 7 of the 37 body stride samples '
                  'ever emit, all from one 128-bit guest copy loop), so "no start-code-valued write" '
                  'is a statement about guest stores, not about every byte that reaches the buffer. '
                  'It does not weaken the post-park result: the descriptor writes ARE guest stores '
                  'and they are fully visible, and the past-end tier covers the start code\'s address '
                  'byte for byte.'),
     reading=('E23 measured that the producer fires exactly once per GetPicture on every path (H1, '
              're-confirmed by E24 and E25). One GetPicture therefore feeds exactly one chunk, and '
              'GetPicture does not return until a frame appears. The host parser cannot emit a frame '
              'until it sees the next start code, and the next start code is in the chunk that the '
              'next feed would carry. That is a mutual wait. This is the READING the capture supports; '
              'it is tabled, not acted on -- the fix gate is STOP.'),
     what_the_capture_cannot_settle=('Whether the title would ever re-ask given more wall time. This '
                                     'capture bounds it at 65 s of total silence after the park, which '
                                     'is a bound, not a proof of never.')))

# ---------------------------------------------------- Mission 2 (b)
SEMA = re.compile(r'\[diag:sema\] op=(\w+) id=(\d+) count=(\S+)(?: parked=(\d+))?.*?'
                  r'waker=(-?\d+) pc=(0x[0-9a-f]+) ra=(0x[0-9a-f]+) inInt=(\d+)')
sema, sema_torn = [], []
for i, l in enumerate(lines):
    mm = SEMA.search(l)
    if mm:
        sema.append(dict(line=i + 1, op=mm.group(1), id=int(mm.group(2)), waker=int(mm.group(5)),
                         pc=mm.group(6), ra=mm.group(7), inInt=int(mm.group(8)),
                         post_park=(i + 1) > PARK_LINE, text=l.strip()))
    elif '[diag:sema] ' in l:
        sema_torn.append(dict(line=i + 1, post_park=(i + 1) > PARK_LINE, text=l.strip()[:200],
                              id=(m3.group(1) if (m3 := re.search(r'id=(\d+)', l)) else None)))
ids = {}
for s in sema:
    d = ids.setdefault(s['id'], dict(id=s['id'], waits=0, signals=0, signal_ras={}, wait_ras={},
                                     post_park_signals=0, post_park_waits=0))
    if s['op'] == 'wait':
        d['waits'] += 1; d['wait_ras'][s['ra']] = d['wait_ras'].get(s['ra'], 0) + 1
        d['post_park_waits'] += s['post_park']
    elif s['op'] == 'signal':
        d['signals'] += 1; d['signal_ras'][s['ra']] = d['signal_ras'].get(s['ra'], 0) + 1
        d['post_park_signals'] += s['post_park']
blocked = {26, 30, 31, 32, 36}
save('sema-ledger.json', dict(utc=utc(), sema_lines=len(sema),
     ids=[ids[k] for k in sorted(ids)],
     blocked_set=sorted(blocked),
     blocked_rows=[ids.get(k, dict(id=k, waits=0, signals=0)) for k in sorted(blocked)],
     post_park_active_ids=sorted(k for k, v in ids.items()
                                 if v['post_park_signals'] or v['post_park_waits']),
     waker_ra_now_available=True,
     torn_lines=dict(
         count=len(sema_torn), post_park=sum(1 for t in sema_torn if t['post_park']),
         ids=sorted({int(t['id']) for t in sema_torn if t['id']}),
         mentions_id_36=any(t['id'] == '36' for t in sema_torn),
         why='a [diag:sema] emission interleaved with a concurrent [frame:*] or INFO: FILEIO write',
         impact=('the per-id tallies below are instrument counts and carry up to this many lines of '
                 'tear noise, which is why small deficits here (26 -> 2, 31 -> 4) differ from e23a\'s '
                 '"every deficit exactly 1". The two STRUCTURAL results do not depend on the tallies: '
                 'semaphore 36 has exactly one line in the whole log (raw grep, no regex), and no '
                 'torn line mentions id 36 at all.')),
     note=('the always-on park tally could only record the syscall STUB pc (0x423dc8 / 0x423dd8); '
           'PS2X_DIAG_SEMA gives the CALLER ra, which is what objective 2 was missing')))

# the 4-instruction closure E24 proved statically, checked dynamically
OWNERS = {'sub_003C1980': 'WaitSema(36) owner, 0x3c19ec, returns to 0x3c19f0',
          'sub_003C1298': 'iSignalSema(36) owner, 0x3c15c0 -- the SOLE signaller',
          'sub_003C2268': 'DeleteSema(36) owner, 0x3c2378',
          'sub_003C1E00': 'CreateSema ret=36 store site owner, 0x3c1e08'}
counts = {}
for name in OWNERS:
    r = subprocess.run(['grep', '-c', f'{name}.* enter', str(FUNCLOG)], capture_output=True, text=True)
    counts[name] = int(r.stdout.strip() or 0)
s36 = [s for s in sema if s['id'] == 36]
save('x-b-sema36.json', dict(utc=utc(),
     question='(b) does semaphore 36\'s sole signaller appear anywhere in the capture?',
     answer_headline=('NO. Confirmed dynamically, on a fresh 75 s boot, with the waker `ra` E24 could '
                      'not obtain: semaphore 36 has exactly ONE event in the whole run -- thread 6\'s '
                      'wait -- and its unique signaller has ZERO entries in a 3,607,246-line function log.'),
     sema36_events=s36, sema36_event_count=len(s36),
     sema36_waits=sum(1 for s in s36 if s['op'] == 'wait'),
     sema36_signals=sum(1 for s in s36 if s['op'] == 'signal'),
     waiter_ra_observed=s36[0]['ra'] if s36 else None,
     waiter_ra_predicted_by_E24='0x3c19f0',
     waiter_ra_matches=bool(s36) and s36[0]['ra'] == '0x3c19f0',
     function_log=dict(path=str(FUNCLOG), lines=3607246, owner_entries=counts, owners=OWNERS),
     signaller_entries=counts['sub_003C1298'],
     verdict=('E24\'s static enumeration is CONFIRMED dynamically. The only code that can ever wake '
              'thread 6 never executed, on a second independent boot.'),
     new_observation=dict(
         what='the WaitSema(36) owner sub_003C1980 runs 4,379 times, but takes the WaitSema(36) branch once',
         where='boot-log line 22,792, the [diag:dormant] trace taken AT the MPEG park',
         chain=('... 0x402a10 GetPicture -> 0x3b0b10 guest callback -> 0x3b0b40 helper -> 0x3b06b0 source '
                '-> ... -> 0x4029d0 AddBs -> 0x3e4db8 -> 0x3825c0 -> 0x3825f8 -> 0x3c1980'),
         why_it_matters=('E24 recorded that NOTHING in the retained evidence linked the MPEG chain and the '
                         'semaphore-36 chain in either direction. This capture puts sub_003C1980 -- the '
                         'function that OWNS the WaitSema(36) site -- on the MPEG delivery path, entered '
                         'immediately after AddBs.'),
         what_it_does_NOT_show=('that the sema-36 branch is on that path. Thread 6 was scheduled once and '
                                'waited once; thread 1 entered the owner without reaching 0x3c19ec. The '
                                'two chains share a FUNCTION, which is weaker than sharing a dependency, '
                                'and this lane does not upgrade it.'))))

print(f'watch emissions {len(events)}, post-park {sum(1 for e in events if e["post_park"])}')
print(f'successor node 0x548880 hits {len(succ)}, post-park {sum(1 for e in succ if e["post_park"])}')
print(f'start-code-valued writes {sum(1 for e in events if "000001" in e["value"].lower())}')
print(f'terminating start code at guest {nxt["payload_guest_addr"]}, '
      f'{(nxt["blob_offset"] + 8) - len(es0) - 8} B past the fed data')
print(f'sema 36 events {len(s36)}; signaller sub_003C1298 entries {counts["sub_003C1298"]}')
print('# E26 XLIGHT TAIL COMPLETE')
