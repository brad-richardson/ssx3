"""Pre-register the armed set and the EXACT P1-P4 pass/fail bytes, before the boot.

E27 owns the predictions; the brief pre-registered them; E28 registers nothing
new. What E28 must fix in advance is (a) which address carries which
prediction and (b) the literal byte that decides each row -- so no row can be
re-read after the fact to fit what the capture happened to show.

Written BEFORE the lease is claimed. `e28_prereg_check.py` at close re-reads
this file and refuses to grade a row that was not registered here.
"""
from e28_common import *

M1 = json.loads((E / 'mission-1-slot.json').read_text())
WS = json.loads((E / 'watch-set.json').read_text())
SLOT = int(M1['result']['kind1_slot'], 16)
assert M1['result']['derived'] and M1['result']['check_passes']

ARMED = [
 dict(addr=hex(SLOT + 0xC), name='kind-1 slot +0xC  HEAD', carries='P1',
      expect_last_value='0xd49b14',
      expect_writers=['0x3dffc4 (walker, first publish)', '0x3e13c8 (dequeue, head advance)'],
      after_feed='ZERO further stores'),
 dict(addr=hex(SLOT + 8), name='kind-1 slot +8    BYTES', carries='P1',
      expect_last_value='>= 14364 (0x381c)',
      expect_writers=['0x3dffc0 (walker, bytes += len)', '0x3e134c (dequeue, bytes -= len)'],
      after_feed='ZERO further stores'),
 dict(addr=hex(SLOT), name='kind-1 slot +0    OWNER', carries='control',
      expect_last_value='0xd48300 (= ctx0)', expect_writers=['0x3e0914 (STRM construction)'],
      after_feed='ZERO further stores',
      why='if this emits with value 0xd48300 the derived address is confirmed by the guest itself'),
 dict(addr=hex(SLOT + 4), name='kind-1 slot +4    KIND', carries='control',
      expect_last_value='1', expect_writers=['stream setup'], after_feed='ZERO further stores'),
 dict(addr='0xd486e0-0xd4873f', name='the rest of the derived window', carries='control',
      expect_last_value='n/a', expect_writers=['kind-2 slot at 0xd486fc'],
      after_feed='ZERO further stores',
      why=('covers every position the slot array could occupy if the 64-byte alignment step were '
           'wrong; an emission OUTSIDE 0xd486ec-0xd486fb would REFUTE the Mission-1 address and '
           'name the true one')),
 dict(addr='0xd48740 / 0xd48744', name='chunk 0 header (magic / tagged length)', carries='control',
      expect_last_value='0x13ac at 0xd48744 after the dequeue strips the tag',
      expect_writers=['0x3dff8c (walker tag)', '0x3e1330 (dequeue strip)'],
      after_feed='ZERO further stores',
      why="E27 named 0xd48744 as outside every E24 tier; this closes that blind spot"),
 dict(addr='0xd49b14 / 0xd49b18', name='the SECOND MPCh chunk header', carries='P2, P3',
      expect_last_value='0x0100381c at 0xd49b18, stored pre-feed at boot-log line 22354 in e26a',
      expect_writers=['0x3dff8c (walker tag) -- pre-feed only'],
      after_feed='ZERO stores -- this IS P3',
      why='already inside E24/E26 past-end extension tier 0xd49af4-0xd49b73; carried unchanged'),
]

ROWS = [
 dict(id='P1', claim=('the kind-1 queue head reads 0xd49b14 with a byte count >= 14,364 from the '
                      'feed onward and NEVER changes to end of run'),
      observable='YES -- both fields receive guest stores, so diagWatchEmit sees them',
      addresses=[hex(SLOT + 0xC), hex(SLOT + 8)],
      confirm=('the LAST pre-park store to ' + hex(SLOT + 0xC) + ' carries value 0xd49b14 AND the '
               'last pre-park store to ' + hex(SLOT + 8) + ' carries a value >= 14364 AND there '
               'are ZERO stores to either address after the park'),
      refute=('the last store to ' + hex(SLOT + 0xC) + ' is not 0xd49b14, or the last store to ' +
              hex(SLOT + 8) + ' is < 14364, or EITHER address is stored to after the park'),
      unobservable_if='no emission ever lands anywhere in 0xd486e0-0xd4873f (then the derived address is wrong)'),
 dict(id='P2', claim='0xd49b18 still reads 0x0100381c at the park',
      observable=('PARTLY -- E26\'s named limit binds. diagWatchEmit fires on GUEST STORES ONLY, '
                  'so the at-park VALUE of an address nothing writes is not readable with the '
                  'existing instruments: no store, no emission, no value. What IS observable is '
                  'that the value does not CHANGE by any guest store after it is set.'),
      addresses=['0xd49b18'],
      confirm=('a store of 0x0100381c at 0xd49b18 from pc=0x3dff8c pre-feed, and ZERO stores to '
               '0xd49b18 thereafter -- i.e. the value is unchanged by any guest store'),
      refute='any later store to 0xd49b18, or no 0x0100381c store at all',
      unobservable_as_designed=('the at-park READ of 0xd49b18 is NOT obtainable: the instrument is '
                                'store-triggered. E28 reports the change-half and marks the '
                                'value-half unobservable rather than inferring it. The residual '
                                'is host CD DMA, which E26 already showed writes this buffer '
                                'without emitting -- bounded here by there being no further '
                                'sceCdRead into it, which the boot log counts.')),
 dict(id='P3', claim='ZERO guest stores to 0xd49b14 / 0xd49b18 after the feed',
      observable='YES -- exactly what a store-triggered instrument measures',
      addresses=['0xd49b14', '0xd49b18'],
      confirm='zero [diag:watch] emissions at either address on any line after the feed line',
      refute='one or more emissions at either address after the feed'),
 dict(id='P4', claim='[MPEG:GetPicture] x1 and [MPEG:feedES] x1 in the new boot log',
      observable='YES -- host-side counters already compiled in, capped at 32 so 1 is a true count',
      addresses=['n/a -- boot-log counters'],
      confirm='exactly 1 [MPEG:GetPicture] line and exactly 1 [MPEG:feedES] line',
      refute='any other count'),
]

save('pre-registration.json', dict(utc=utc(),
     registered_before='the lease claim and the boot',
     predictions_owned_by='E27 Mission 3, carried by the E28 brief; E28 registers nothing new',
     kind1_slot=hex(SLOT), ctx0=M1['result']['ctx0'],
     watch_set_sha256=sha(E / 'watch-set.json'), watch_entries=WS['total_entries'],
     armed=ARMED, rows=ROWS,
     named_limit=('E26: diagWatchEmit fires on GUEST STORES ONLY. Every row above is graded on '
                  'stores. A row whose at-park VALUE has no store behind it is reported '
                  'unobservable-as-designed WITH its reason, and its observable half stands.'),
     scope='P1-P4 and the carried controls ONLY. This lane is a confirmation, not a fishing trip.'))
for r in ROWS:
    print(f"{r['id']}  {r['claim'][:78]}")
    print(f"     observable: {r['observable'][:90]}")
print(f"armed: {len(ARMED)} groups over {WS['total_entries']} entries; kind-1 slot {hex(SLOT)}")
print('# E28 PREREG TAIL COMPLETE')
