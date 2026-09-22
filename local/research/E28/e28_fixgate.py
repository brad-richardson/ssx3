"""E28 fix gate. The brief sets it to STOP. Honored as written.

WRITTEN FRESH, not carried: E26's fix gate reads E26's own mission receipts
(`x-a-startcode.json`, `x-b-sema36.json`, `objective-1a.json`,
`watch-ledger.json`), which are E26's questions and not E28's. Carrying it
mechanically would have made it read files this lane never produces. Recorded
in `tooling-changes.json` under `written_fresh` rather than claimed as a carry.
E27 set the same precedent when it wrote `e27_common.py` fresh.

The gate's rule: a fix needs exactly ONE demonstrated edge, plus its own
fail-before and its own full regression. E28 diagnoses and tables. It does not
patch, and it does not infer authority it was not given.
"""
from e28_common import *

V = json.loads((E / 'mission-2-verdicts.json').read_text())
M1 = json.loads((E / 'mission-1-slot.json').read_text())
C = V['controls']
p1 = V['verdicts'][0]['receipts']
addr = C['derived_address_confirmed_by_the_guest']

edges = [
    dict(n=1, edge='The kind-1 queue slot has a guest address, derived statically and then '
                   'confirmed by the guest itself',
         receipt=(f"derived {M1['result']['kind1_slot']} from the STRM constructor's own layout "
                  f"arithmetic (ctx0+0x3ec) run backwards through the data-region base E26 "
                  f"measured ({M1['arithmetic']['data_base']}) over the allocator's 64-byte "
                  f"alignment floor; the guest then stored ctx0 = {M1['result']['ctx0']} into "
                  f"slot+0 at boot-log line {addr['owner_stores'][0]['line']}, pc "
                  f"{addr['owner_stores'][0]['pc']} -- the derived value, written by the machine. "
                  f"mission-1-slot.json, mission-2-verdicts.json"),
         demonstrated=True),
    dict(n=2, edge='The kind-1 head is parked on the chunk E27 named, and never moves again',
         receipt=(f"head {p1['head_addr']}: {p1['head_stores']} stores in the whole run -- "
                  f"line {p1['head_rows'][0]['line']} = 0xd48740 (walker first publish, pc "
                  f"{p1['head_rows'][0]['pc']}), line {p1['head_rows'][1]['line']} = "
                  f"{p1['head_rows'][1]['value']} (dequeue head advance, pc "
                  f"{p1['head_rows'][1]['pc']}); {p1['stores_after_feed']} stores after the feed"),
         demonstrated=True),
    dict(n=3, edge='The queue the guest is sitting on is not one chunk deep, it is 431,840 bytes deep',
         receipt=(f"bytes {p1['bytes_addr']}: {p1['bytes_stores']} stores; the count climbs to "
                  f"0x6aa8c = 436,876 over 28 walker publishes and the single dequeue takes "
                  f"0x13ac = 5,036 back off, leaving {p1['bytes_last_value']} = "
                  f"{p1['bytes_last_decimal']:,} bytes still queued at the park -- 30x E27's "
                  f"predicted floor of 14,364"),
         demonstrated=True),
    dict(n=4, edge="E27's whole guest-half prediction set survives a fresh boot, and the post-park "
                   "silence reproduces on a bigger vector",
         receipt=(f"P1-P4 all CONFIRM (P2's value-half unobservable-as-designed); "
                  f"{C['whole_vector']['emissions']} emissions across "
                  f"{C['whole_vector']['entries']} armed entries, "
                  f"{C['whole_vector']['post_park']} post-park and "
                  f"{C['whole_vector']['post_feed']} post-feed, last at line "
                  f"{C['whole_vector']['last_emission_line']} against a feed at "
                  f"{C['boundaries']['feed_line']} and a park at {C['boundaries']['park_line']}, "
                  f"with {C['boundaries']['lines_after_park']} log lines still to run"),
         demonstrated=True),
]

save('fix-gate.json', dict(utc=utc(),
     gate='STOP', gate_source="the E28 brief sets it, as E24/E26/E27 did before it",
     honored_as_written=True, written_fresh=True,
     demonstrated_edges=edges, edge_count=len(edges),
     isolated_to_one_edge=False,
     why_not=('Four edges are demonstrated and they are not the same edge: one is an address '
              'derivation, one is a queue head, one is a queue depth, one is a whole prediction '
              'set reproducing. A fix needs exactly ONE edge plus its own fail-before and full '
              'regression; E28 has none of those and was not asked to build them.'),
     why_a_fix_would_be_premature_anyway=(
         'Every edge E28 demonstrates is on the GUEST side, and the guest side is not where the '
         'stall lives. E27 located the one-shot in the host: a shared_ptr held by the very wait it '
         'blocks. E28 confirms the guest is healthy -- it has the chunk, it has the queue, it has '
         'the branch -- which makes the host the only remaining place to look, and looking there '
         'needs MPEG.cpp instrumentation that is E29\'s lane, not this one.'),
     decision='STOP -- diagnose and table, never patch',
     mutations=dict(fork_source_edits=0, fork_commits=0, pushes=0, regenerations=0,
                    builds=0, relinks=0, observer_rebuilds=0, deletions=0),
     candidates_still_killed=('C2a and C4 (E23); C1, C3, C5-C9 (E22). E28 re-confirms the reference '
                              'they were killed against by identity -- the runner it booted is the '
                              'binary E23 and E26 booted -- and re-proposes none of them.'),
     x_after_E28=('X is no longer "why does the guest stop one chunk short". It does not stop one '
                  'chunk short: it holds 431,840 bytes in a queue whose head is parked on exactly '
                  'the chunk it needs, and a live backward branch at 0x3b10ac that would ask for '
                  'it the moment the host call returns. X is now entirely host-side: why does '
                  'getMpegPicture never return, and is the delivery shared_ptr that suppresses the '
                  'producer really still alive at the park? That is one MPEG.cpp log line away and '
                  'it is E29\'s.')))
print('fix gate: STOP; edges demonstrated', len(edges), '; isolated to one edge: False')
print('# E28 FIX GATE TAIL COMPLETE')
