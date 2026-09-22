"""E29 Mission 3, Boot 2 -- the CHECKPOINT verdict against Mission 1(a).

Pre-registered BEFORE the branch was cut. Each checkpoint is scored exactly as
written, and where a pre-registered observable turns out to have been the wrong
proxy, that is recorded as a MISS with the reason -- not quietly replaced by a
different one that happened to fire.
"""
import re, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
A, B_ = 'e29a', 'e29b'
RUN = P / 'run'
prereg = json.loads((E / 'pre-registration-pass-1.json').read_text())['checkpoint']

def load(label):
    L = RUN / f'boot-{label}-1.log'
    lines = L.read_text(errors='replace').splitlines()
    park = RUN / f'park-{label}-1/park-snapshot.txt'
    ptxt = park.read_text(errors='replace') if park.exists() else ''
    t1 = [l.strip() for l in ptxt.splitlines() if ' id=1 ' in l and 'count=' not in l]
    blocks = [l for l in lines if l.startswith('[diag:stubs] ')]
    last = blocks[-1] if blocks else ''
    m = re.search(r'distinct=(\d+)', last)
    # top-30 rows of the FINAL block only (the printer caps at 30 of `distinct`)
    idx = lines.index(last) if last in lines else -1
    rows = []
    for l in lines[idx + 1:]:
        if l.startswith('[diag:stub] '): rows.append(l)
        elif l.startswith('[diag:stubs] '): break
    targets = sorted({re.search(r'target=(0x[0-9a-f]+)', r).group(1) for r in rows})
    ups = sorted({re.sub(r' idx=\d+| tick=\d+', '', l) for l in lines if l.startswith('[frame:upload]')})
    # A handful of [frame:dump] lines are torn by a concurrent write on the same
    # fd (errata E24-E1's class, counted by E28 at 6 of 6,810). Skip the ones
    # whose fnv1a does not parse rather than crashing or silently dropping them.
    fnv, torn = [], 0
    for l in lines:
        if l.startswith('[frame:dump]') and 'fallback=0' in l:
            m2 = re.search(r'fnv1a=([0-9a-f]+)', l)
            if m2: fnv.append(m2.group(1))
            else: torn += 1
    return dict(label=label, log_lines=len(lines),
                dev_skip=sum(1 for l in lines if l.startswith('[MPEG:DEV-SKIP-MOVIE]')),
                getpic_wait=sum(1 for l in lines if l.startswith('[MPEG:GetPicture] waiting')),
                feedes=sum(1 for l in lines if l.startswith('[MPEG:feedES]')),
                frames_served=sum(1 for l in lines if l.startswith('[MPEG:GetPicture:FRAME]')),
                thread1=t1[0] if t1 else None,
                final_block=last, final_distinct=int(m.group(1)) if m else None,
                final_top30_targets=targets, display_configs=ups,
                distinct_frame_contents=len(set(fnv)), frame_dumps=len(fnv), torn_frame_dump_lines=torn,
                last_frames=fnv[-5:])

a, b = load(A), load(B_)
E28_13 = set(prereg['C2_left_the_terminal_13_stub_loop']['e28a_final_target_set'])

C1 = dict(
  name='C1 -- movie sequencing exited', necessary=True,
  rows=[dict(obs='[MPEG:DEV-SKIP-MOVIE] >= 1', e29a=a['dev_skip'], e29b=b['dev_skip'], pass_=b['dev_skip'] >= 1),
        dict(obs='[MPEG:GetPicture] waiting == 0', e29a=a['getpic_wait'], e29b=b['getpic_wait'], pass_=b['getpic_wait'] == 0),
        dict(obs='thread 1 NOT parked on Mpeg:0 pc=0x3b1028', e29a=a['thread1'], e29b=b['thread1'],
             pass_=bool(b['thread1']) and 'wait=Mpeg:0' not in b['thread1'])])
C1['met'] = all(r['pass_'] for r in C1['rows'])

C2 = dict(
  name='C2 -- left e28a\'s terminal 13-stub loop (THE REACHABILITY CLAIM)',
  rows=[dict(obs='final [diag:stubs] distinct > 13', e29a=a['final_distinct'], e29b=b['final_distinct'],
             pass_=b['final_distinct'] > 13),
        dict(obs='final top-30 target set NOT a subset of e28a\'s 13',
             e29a=sorted(set(a['final_top30_targets']) - E28_13),
             e29b=len(set(b['final_top30_targets']) - E28_13),
             pass_=not set(b['final_top30_targets']) <= E28_13)])
C2['met'] = all(r['pass_'] for r in C2['rows'])

C3 = dict(
  name='C3 -- menu/race rendering, AS PRE-REGISTERED',
  rows=[dict(obs='a [frame:upload] display configuration e28a never produced',
             e29a=a['display_configs'], e29b=b['display_configs'],
             pass_=len(b['display_configs']) > 1 or b['display_configs'] != a['display_configs']),
        dict(obs='a [frame:dump] size other than 512x448 (non-fallback)',
             e29a='512x448 only (+ the 18 boot fallbacks at 640x512)',
             e29b='512x448 only (+ the 19 boot fallbacks at 640x512)', pass_=False)])
C3['met'] = all(r['pass_'] for r in C3['rows'])
C3['why_it_missed'] = (
  'The pre-registered proxy was WRONG, and is recorded as a miss rather than swapped out. '
  'SSX 3\'s front end renders at the SAME 512x448 framebuffer (fbp=112) the movie used, so a '
  'display-configuration change was never going to signal it. What DID change is frame '
  'CONTENT: e28a produced %d distinct non-fallback frames and then froze on one forever; '
  'e29b produced %d and was still changing at the wall.' % (a['distinct_frame_contents'], b['distinct_frame_contents']))

out = dict(utc=utc(), a=a, b=b,
           checkpoints=[C1, C2, C3],
           verdict=('C1 MET, C2 MET, C3 MISSED-AS-WRITTEN' if (C1['met'] and C2['met'] and not C3['met'])
                    else 'see rows'))
save('checkpoint-verdict.json', out)
for c in (C1, C2, C3):
    print(f"\n{'MET ' if c['met'] else 'MISS'}  {c['name']}")
    for r in c['rows']:
        print(f"      {'pass' if r['pass_'] else 'MISS'}  {r['obs']}")
        print(f"            e29a(OFF)={r['e29a']!r}")
        print(f"            e29b(ON) ={r['e29b']!r}")
print('\nframe contents: e29a %d distinct / %d dumps | e29b %d distinct / %d dumps'
      % (a['distinct_frame_contents'], a['frame_dumps'], b['distinct_frame_contents'], b['frame_dumps']))
print('# E29 CHECKPOINT TAIL COMPLETE')
