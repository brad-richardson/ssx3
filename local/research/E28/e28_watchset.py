"""Build E28's watch set: E26's 230-entry vector CARRIED VERBATIM + ONE new tier.

The brief permits exactly one intentional change to the capture driver's
behaviour -- the watch set -- and requires before/after receipts. This tool
makes that change auditable rather than asserted:

  * every carried tier is copied from E26's `watch-set.json` and compared back
    element for element, in order, so "carried verbatim" is MEASURED;
  * the one new tier is appended LAST, so the driver's PRODUCER vector is
    E26's vector with a suffix and nothing is reordered;
  * the three counters that must move (new_entries, total_entries and the tier
    list) are the ONLY keys that differ; every other key is byte-equal.

The new tier is the kind-1 queue slot, Mission 1's deliverable. It is sized to
the WHOLE window the slot array could occupy if the 64-byte alignment step were
wrong, with complete 8-byte cover, so the boot measures the address instead of
trusting it -- and it is extended down to chunk 0's own header at 0xd48740,
E27's named blind spot, because the store that strips chunk 0's tag
(sub_003E12E0 0x3e1330) is the COMPANION of the head advance P1 is about.
"""
from e28_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
SRC = E.parent / 'E26' / 'watch-set.json'
before = json.loads(SRC.read_text())
before_sha = sha(SRC)

M1 = json.loads((E / 'mission-1-slot.json').read_text())
assert M1['result']['derived'] and M1['result']['check_passes'], 'Mission 1 did not derive the slot'
SLOT = int(M1['result']['kind1_slot'], 16)
LO = int(M1['armed_window']['lo'], 16)
HI = 0xd48748                      # extended over chunk 0's header, see docstring
assert LO % 8 == 0 and HI % 8 == 0 and LO < SLOT < HI

addrs = list(range(LO, HI, 8))
new_tier = dict(
    name='kind-1 queue slot (+ chunk 0 header)',
    lo=hex(LO), hi=hex(HI), stride=8, entries=len(addrs),
    why=('E27 named the kind-1 slot as ctx0->[0x24]+0 but had no guest address for it. E28 '
         'Mission 1 derives it: the STRM constructor sub_003E06D8 computes the slot array base '
         'and then the DATA REGION BASE from it, and E26 measured that data base in bytes '
         '(sceCdRead buf=0xd48740). Running the identity backwards over the allocator\'s '
         '64-byte alignment floor (sub_00253AD0) gives ctx0=0xd48300 uniquely, so the kind-1 '
         'slot is 0xd486ec: owner +0, kind +4, bytes +8, head +0xC. This tier covers the whole '
         'window the slot array could occupy at ANY alignment, so the boot MEASURES the address. '
         'It is extended down to 0xd48740 so chunk 0\'s header -- E27\'s named blind spot, where '
         'sub_003E12E0 strips the tag in the same breath as it advances the head -- is visible.'),
    guarantee='complete: every byte of [0xd486e0, 0xd48748) is inside a watched 8-byte window',
    p_meaning=dict(
        p1_bytes=hex(SLOT + 8), p1_head=hex(SLOT + 0xC),
        p1='slot+8 (byte count) and slot+0xC (head) carry P1; both receive GUEST STORES '
           '(walker 0x3dffc0/0x3dffc4, dequeue 0x3e134c/0x3e13c8), so P1 is observable',
        owner=hex(SLOT), kind=hex(SLOT + 4),
        control='slot+0 is written once at construction with ctx0 itself (0x3e0914), which '
                'independently confirms the address if it emits',
        chunk0_header='0xd48740 magic / 0xd48744 tagged length -- E27 named 0xd48744 as outside '
                      'every E24 tier, so chunk 0\'s own tag store was never observable'),
    addrs=addrs)

after = dict(before)
after['tiers'] = list(before['tiers']) + [new_tier]
after['new_entries'] = before['new_entries'] + len(addrs)
after['total_entries'] = before['total_entries'] + len(addrs)
after['e28_change'] = dict(
    what='ONE tier appended; the 230-entry E26/E24 vector is carried verbatim and unreordered',
    carried_from=str(SRC), carried_sha256=before_sha,
    appended_tier=new_tier['name'], appended_entries=len(addrs),
    before=dict(new_entries=before['new_entries'], total_entries=before['total_entries'],
                tiers=len(before['tiers'])),
    after=dict(new_entries=after['new_entries'], total_entries=after['total_entries'],
               tiers=len(after['tiers'])),
    keys_that_differ=['tiers', 'new_entries', 'total_entries', 'e28_change'],
    cost=('E26 refit the model to k=0.00806 s/entry, base=7.683 s on three points, so 13 extra '
          'entries cost about 0.10 s of span-complete against a 75 s bound'))
(E / 'watch-set.json').write_text(json.dumps(after, indent=2) + '\n')
after_sha = sha(E / 'watch-set.json')

# ------------------------------------------------------------- the receipt --
carried_equal = all(a == b for a, b in zip(before['tiers'], after['tiers'][:len(before['tiers'])]))
same_keys = {k: (before[k] == after[k]) for k in before}
differ = sorted(k for k, v in same_keys.items() if not v)
vec_before = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c] + [a for t in before['tiers'] for a in t['addrs']]
vec_after = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c] + [a for t in after['tiers'] for a in t['addrs']]
prefix_ok = vec_after[:len(vec_before)] == vec_before
uniq = len(set(vec_after)) == len(vec_after)
disjoint = not (set(addrs) & set(vec_before))
covers_slot = all(any(a <= x < a + 8 for a in addrs) for x in (SLOT, SLOT + 4, SLOT + 8, SLOT + 0xC))

save('watch-set-change.json', dict(utc=utc(),
     before=dict(path=str(SRC), sha256=before_sha, tiers=len(before['tiers']),
                 new_entries=before['new_entries'], total_entries=before['total_entries'],
                 producer_vector=len(vec_before)),
     after=dict(path=str(E / 'watch-set.json'), sha256=after_sha, tiers=len(after['tiers']),
                new_entries=after['new_entries'], total_entries=after['total_entries'],
                producer_vector=len(vec_after)),
     appended_tier={k: v for k, v in new_tier.items() if k != 'addrs'},
     appended_addrs=[hex(a) for a in addrs],
     checks=dict(carried_tiers_identical_element_for_element=carried_equal,
                 only_expected_keys_differ=differ == ['new_entries', 'tiers', 'total_entries'],
                 keys_that_differ=differ,
                 e26_vector_is_an_exact_prefix=prefix_ok,
                 no_duplicate_addresses=uniq,
                 new_tier_disjoint_from_carried=disjoint,
                 all_four_slot_fields_covered=covers_slot),
     green=all([carried_equal, differ == ['new_entries', 'tiers', 'total_entries'],
                prefix_ok, uniq, disjoint, covers_slot])))
ch = json.loads((E / 'watch-set-change.json').read_text())
for k, v in ch['checks'].items():
    if isinstance(v, bool):
        print(f"{'PASS' if v else 'FAIL'}  {k}")
print(f"before {before_sha[:16]} {before['total_entries']} entries -> after {after_sha[:16]} {after['total_entries']} entries")
print(f"appended {len(addrs)} entries [{hex(LO)},{hex(HI)}) around slot {hex(SLOT)}")
print('# E28 WATCHSET TAIL COMPLETE green=' + ('1' if ch['green'] else '0'))
assert ch['green'], ch['checks']
