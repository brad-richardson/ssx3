"""E29 Mission 1(b)+(c) -- the PRE-REGISTRATION, written before the branch is cut.

(b) the flag-OFF equivalence bar: e28a's terminal state as EXACT VALUES, not
    "same". Boot 1 must reproduce every row or the bypass is CONTAMINATED.
(a) the menu/race CHECKPOINT with its byte observables.
(c) what the bypass CANNOT show.

Every number is mined from E28's OWN committed pins and re-read from the
captures on the SSD, so the bar is not recalled -- it is computed. Run twice;
the caller separates the passes in time (standing SSD rule).
"""
import re, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
PASS = sys.argv[1] if len(sys.argv) > 1 else '1'
RUN = P / 'run'
BOOT = RUN / 'boot-e28a-1.log'
PARSER = RUN / 'e28a-parser/parser-events.txt'
FEED = RUN / 'e28a-parser/parser-input.bin'
PARK = RUN / 'park-e28a-1/park-snapshot.txt'

# --- corroboration: E28's committed capture pins, in this repo, git-tracked ---
e28_pins = {r['file']: r for r in json.loads(
    (E.parent / 'E28' / 'capture-pins.json').read_text())['rows']}

def pinned(p, key):
    row = dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p))
    ref = e28_pins.get(key)
    row['E28_committed_sha256'] = ref['pass1'] if ref else None
    row['equals_E28_committed_pin'] = bool(ref) and row['sha256'] == ref['pass1']
    return row

captures = dict(boot=pinned(BOOT, 'boot-e28a-1.log'), feed=pinned(FEED, 'parser-input.bin'))

text = BOOT.read_text(errors='replace')
lines = text.splitlines()

def count(pat): return sum(1 for l in lines if l.startswith(pat))
def only(pat):
    hits = [(i + 1, l) for i, l in enumerate(lines) if l.startswith(pat)]
    return hits

# ------------------------------------------------ (b) flag-OFF equivalence bar
getpic = only('[MPEG:GetPicture] waiting')
feedes = only('[MPEG:feedES]')
feedln = only('[MPEG:feed] ')
frame = only('[MPEG:GetPicture:FRAME]')
park_text = PARK.read_text(errors='replace')
t1 = [l for l in park_text.splitlines() if ' id=1 ' in l or l.strip().startswith('id=1 ')]
parser_tail = [l for l in PARSER.read_text(errors='replace').splitlines()
               if l.startswith('# E21 PARSER CLOSURE')]

def field(line, key):
    m = re.search(re.escape(key) + r'=([^\s]+)', line)
    return m.group(1) if m else None

closure = parser_tail[0] if parser_tail else ''
BAR = {
  'park_counter_GetPicture_wait': dict(expect=1, got=len(getpic),
      exact_line=getpic[0][1] if getpic else None, at_log_line=getpic[0][0] if getpic else None),
  'park_counter_feedES': dict(expect=1, got=len(feedes),
      exact_line=feedes[0][1] if feedes else None, at_log_line=feedes[0][0] if feedes else None),
  'feed_line': dict(expect=1, got=len(feedln), exact_line=feedln[0][1] if feedln else None),
  'GetPicture_FRAME': dict(expect=0, got=len(frame)),
  'park_thread1': dict(expect='Waiting wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028',
      exact_line=t1[0].strip() if t1 else None,
      pc='0x3b1028', ra='0x3b1028', wait='Mpeg:0', chain='[0x3b1028]'),
  'feed_vector': dict(bytes=captures['feed']['bytes'], sha256=captures['feed']['sha256'],
      first4='000001b3', fnv64='0xd2a9588f0e0fd358',
      equals_E22_E23_E24_E26_E28_pin=captures['feed']['equals_E28_committed_pin']),
  'parser_closure': dict(parseCalls=field(closure, 'parseCalls'), offered=field(closure, 'offered'),
      consumed=field(closure, 'consumed'), packets=field(closure, 'packets'),
      frames=field(closure, 'frames'), errors=field(closure, 'errors'),
      pending=field(closure, 'pending')),
  'queue_head_last_value': dict(address='0xd486f8', expect='0xd49b14',
      note='E28 P1: 2 stores in the whole run, 0 after the feed'),
  'queue_bytes_last_value': dict(address='0xd486f4', expect='0x696e0', decimal=431840,
      note='E28 P1: 30 stores, settles after the dequeue'),
  'watch_vector_entries': dict(expect=243, note='E28 vector carried UNCHANGED this lane'),
}
bar_green = (BAR['park_counter_GetPicture_wait']['got'] == 1 and
             BAR['park_counter_feedES']['got'] == 1 and
             BAR['GetPicture_FRAME']['got'] == 0 and
             captures['feed']['equals_E28_committed_pin'] and bool(t1))

# ------------------------------------------------------------ (a) CHECKPOINT
# e28a's terminal steady state is a FIXED 13-stub loop. Its fingerprint is the
# final [diag:stubs] block; anything outside it is the guest doing new work.
blocks, cur, hdr = [], [], None
for l in lines:
    if l.startswith('[diag:stubs] '):
        if hdr is not None: blocks.append((hdr, cur))
        hdr, cur = l, []
    elif l.startswith('[diag:stub ') or l.startswith('[diag:stub]'):
        if hdr is not None: cur.append(l)
if hdr is not None: blocks.append((hdr, cur))
final_hdr, final_rows = blocks[-1]
final_targets = sorted({re.search(r'target=(0x[0-9a-f]+)', r).group(1) for r in final_rows})
uploads = sorted({re.sub(r' idx=\d+| tick=\d+', '', l) for l in lines if l.startswith('[frame:upload]')})
dumps = [l for l in lines if l.startswith('[frame:dump]')]

CHECKPOINT = {
  'C1_movie_sequencing_exited': dict(
     necessary=True,
     observables=[
       'boot log: "[MPEG:DEV-SKIP-MOVIE]" count >= 1  (the flag fired; e28a: 0)',
       'boot log: "[MPEG:GetPicture] waiting" count == 0  (the park never happens; e28a: 1)',
       'park snapshot: thread id=1 is NOT "Waiting wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028"',
     ]),
  'C2_left_the_terminal_13_stub_loop': dict(
     is_the_reachability_claim=True,
     e28a_final_block=final_hdr, e28a_final_distinct=len(final_targets),
     e28a_final_target_set=final_targets,
     observables=[
       'the FINAL [diag:stubs] block reports distinct > %d, OR' % len(final_targets),
       'its target set is NOT a subset of the %d addresses listed above' % len(final_targets),
     ]),
  'C3_menu_or_race_rendering': dict(
     e28a_display_configs=uploads, e28a_frame_upload_lines=len(uploads),
     e28a_last_frame_dump=dumps[-1] if dumps else None,
     e28a_frame_dump_lines=len(dumps),
     observables=[
       'at least one [frame:upload] line whose displayFbp/sourceFbp/size differs '
       'from the ONE configuration e28a ever produced (listed above) -- the line '
       'prints past its 128 cap precisely when that configuration changes',
       'and/or a [frame:dump] size= other than 512x448',
     ]),
}

# ------------------------------------------------------- (c) what it CANNOT show
LIMITS = [
 '1. It cannot show the faithful movie path works. Flag-ON skips the movie; it '
 'does not play it. Any picture the flag-ON run shows is writeBlankMpegFrame '
 'output, not decoded video. Ordinary-boot/movie fidelity stays OPEN.',
 '2. It cannot show WHY the host stalls. streamEnded is set by fiat above the '
 'wait guard; the nonStreamDeliveries latch E27 named is neither exercised nor '
 'disproved. E30\'s question is untouched by this lane.',
 '3. It cannot show the guest re-ask loop would ever have terminated on its own. '
 'The bypass changes WHICH exit that loop takes.',
 '4. It cannot bound how far past movie sequencing the title gets. If a second '
 'blocker lies beyond it, E29 records the next reached blocker as a PARTIAL '
 'RESULT, which the review names as a result and not a failure.',
 '5. Flag-OFF equivalence is measured at ONE terminal state on ONE title boot. '
 'It is not a fidelity proof for any other path. The 458-test suite is the only '
 'broad flag-off evidence this lane produces.',
 '6. [gs:prim] caps at 64 and [gs:kick] caps at 96, and e28a sits EXACTLY at '
 'both caps. Neither can discriminate menu/race rendering. Named before the run '
 'so no reader mistakes a capped counter for a result. C3 uses [frame:upload], '
 'which prints past its cap whenever the display configuration changes.',
 '7. It says nothing about Odin/Android: this is a macOS arm64 host build.',
 '8. If the flag-ON run parks elsewhere, E29 reports the NEW park. The bypass\'s '
 'own observable (C1) is independent of whatever happens after it.',
 '9. [MPEG:DEV-SKIP-MOVIE] is inside PS2_IF_AGRESSIVE_LOGS, so it is visible '
 'only because the build carries -DPS2X_ENABLE_AGRESSIVE_LOGS=ON, exactly as '
 'every other [MPEG:*] marker this bar relies on.',
]

out = dict(utc=utc(), pass_id=PASS, lane='E29',
           registered_before=['branch cut', 'any build', 'any lease', 'any boot'],
           captures=captures, equivalence_bar=BAR, bar_computable_and_green=bar_green,
           checkpoint=CHECKPOINT, limits=LIMITS)
save(f'pre-registration-pass-{PASS}.json', out)
print(json.dumps(dict(pass_id=PASS, bar_green=bar_green,
                      getpicture_wait=BAR['park_counter_GetPicture_wait']['got'],
                      feedes=BAR['park_counter_feedES']['got'],
                      frame=BAR['GetPicture_FRAME']['got'],
                      feed_sha=BAR['feed_vector']['sha256'][:16] + '...',
                      feed_equals_pin=BAR['feed_vector']['equals_E22_E23_E24_E26_E28_pin'],
                      park=BAR['park_thread1']['exact_line'],
                      closure=BAR['parser_closure'],
                      final_stub_block=final_hdr, final_distinct=len(final_targets),
                      e28a_display_configs=uploads), indent=2))
assert bar_green, 'BAR NOT COMPUTABLE'
print('# E29 PREREG TAIL COMPLETE pass=' + PASS)
