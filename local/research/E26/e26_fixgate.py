"""E26 fix gate. E24 set it to STOP and designed the boot around it. Honored as written.

The gate's rule: a fix needs exactly ONE demonstrated edge, plus its own
fail-before and its own full regression. E26 diagnoses and tables. It does not
patch, and it does not infer authority it was not given.
"""
from e26_common import *

xa = json.loads((E / 'x-a-startcode.json').read_text())
xb = json.loads((E / 'x-b-sema36.json').read_text())
o1a = json.loads((E / 'objective-1a.json').read_text())
led = json.loads((E / 'watch-ledger.json').read_text())

edges = [
    dict(n=1, edge='The terminating start code is already in guest RAM, 48 B past the fed data',
         receipt=(f"guest {xa['bytes']['terminating_start_code_guest_addr']}, first4 "
                  f"{xa['bytes']['next_chunk']['payload_first4']}, delivered by the same "
                  f"16-sector CD read at lbn {xa['bytes']['cd_read']['lbn']}; chunk-map.json"),
         demonstrated=True),
    dict(n=2, edge='Nothing in the 230-entry watch set moves after the park',
         receipt=(f"{led['watch_emissions']} emissions, {led['emissions_post_park']} post-park; "
                  f"last at line {led['last_emission_line']}, park at "
                  f"{led['boundaries']['park_line']}, {led['boundaries']['lines_after_park']} "
                  f"log lines and ~65 s of run remaining; watch-ledger.json"),
         demonstrated=True),
    dict(n=3, edge="Semaphore 36's sole signaller never runs, now confirmed dynamically",
         receipt=(f"sema 36 has {xb['sema36_event_count']} event in the whole run "
                  f"(the wait, ra {xb['waiter_ra_observed']} = E24's predicted "
                  f"{xb['waiter_ra_predicted_by_E24']}); sub_003C1298 entries "
                  f"{xb['signaller_entries']} in 3,607,246 function-log lines; x-b-sema36.json"),
         demonstrated=True),
    dict(n=4, edge="E23's named residual -- the successor descriptor node -- is CLOSED",
         receipt=(f"0x548880 has {o1a['successor_hits']} write in the whole run, the boot-time "
                  f"free-list init, {o1a['successor_hits_post_park']} post-park; objective-1a.json"),
         demonstrated=True),
]

save('fix-gate.json', dict(utc=utc(),
     gate='STOP', gate_source='E24 set it to STOP and designed the boot around it',
     honored_as_written=True,
     demonstrated_edges=edges, edge_count=len(edges),
     isolated_to_one_edge=False,
     why_not=('Four edges are demonstrated, not one, and they are not the same edge: two are about '
              'the MPEG feed, one is about a semaphore chain with no proven dependency on it, and '
              'one closes a prior lane\'s residual. A fix needs exactly ONE edge plus its own '
              'fail-before and full regression; E26 has none of those and was not asked to build them.'),
     decision='STOP -- diagnose and table, never patch',
     mutations=dict(fork_source_edits=0, fork_commits=0, pushes=0, regenerations=0,
                    builds=0, relinks=0, observer_rebuilds=0, deletions=0),
     candidates_still_killed=('C2a and C4 (E23); C1, C3, C5-C9 (E22). E26 re-confirms the reference '
                              'they were killed against by identity -- the runner it booted is the '
                              'binary E23 booted -- and re-proposes none of them.'),
     x_after_E26=('X moves from "why does the guest stop one start code short?" to "why does the guest '
                  'stop one CHUNK short of feeding, when the chunk it needs is already in RAM 48 bytes '
                  'away and it has already walked to its header?" -- and, still separately, why '
                  'semaphore 36\'s only signaller never runs.'),
     note='Recorded with its receipt rather than asserted or skipped.'))
print('fix gate: STOP; edges demonstrated', len(edges), '; isolated to one edge: False')
print('# E26 FIX GATE TAIL COMPLETE')
