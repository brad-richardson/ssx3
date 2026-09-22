# E24 experiment contract — written before any copy, rename, run or boot

## Question
E23 killed C2a/C4 and moved X upstream. E24 executes E23 NEXT-BRIEF's two
cheap follow-ups, in order, plus one same-boot I-lane relay:

1a. Close E23's NAMED RESIDUAL: the descriptor head advanced
    `0x548800 = 0x548880` at boot-log line 10,168 and the successor node at
    `0x548880` was NOT in the watched set, so its post-park silence is
    vacuous rather than measured. Does the successor node move post-park?
1b. Attribute thread 4's ~300 wakes per 5 s: what do they touch?
2.  Follow the semaphore wait: threads 2-6 parked `waitReason=2` at
    `pc=0x423de8`. Who is meant to signal each, what are the signalers
    doing instead, and does the MPEG stall read as symptom?
3.  I-lane relay (I23 H2): are the title movie dims derivable? The 5,040 B
    are already retained (E22/E23 `observed/parser-input.bin`,
    FNV64 `0xd2a9588f0e0fd358`). Trace-mining only; burn nothing extra.

## Hypothesis
H0 (null): the successor descriptor node at `0x548880` and the `0xd48748+`
data region are also silent after the park, so E23's KILLED verdict is
exhaustive over the producer's whole source structure, and threads 2-6 are
blocked on semaphores whose signalers are themselves blocked.
H1 (alternative): the successor node or the data region DOES move post-park,
so the guest does advance its source while the caller is parked and E23's
verdict was an artifact of an incomplete watch set.
Both are decidable from one extended-watch boot. The measurement is the same
either way.

## Observable
From runtime-closed receipts, in ONE guarded title boot:
- every guest WRITE to the successor descriptor node `0x548880`-`0x5488ff`,
  to the descriptor node array, to the `0xd48748+` data region and to the
  staging buffer, with pc / thread / ra / sp, split before vs after the park;
- one `[diag:sema]` line per semaphore signal and wait
  (`PS2X_DIAG_SEMA=1`, already compiled into the runner, no rebuild):
  id, count transition, waiters, waker thread, waker pc AND ra, inInt,
  iSafe, invocation kind/depth/cbFunc, target waiter, result;
- the park snapshot's always-on sema wait/signal tallies and thread chains;
- the per-call parser receipt through the REUSED observer, 1:1 forwarding,
  4/4 bindings, and the retained payload for objective 3.

## Instruments (no rebuild of any proven instrument)
- `parser/e21-parser-observer.dylib` REUSED by copy + re-sha to
  `e4d88fdc6740449893d5a96c112fae6ce3f19135bad8a309d140d45bbf38e6be`
  (52,472 B). It owns its interface: `PS2X_E21_PARSER_DIR`, `PS2X_E21_PROOF`
  and `# E21 PARSER CLOSURE` stay E21-spelled by necessity (E21/E22/E23 carry).
- E23 tools carried by mechanical rename under the HEX-SAFE proof and the
  hex audit required by errata E23-E1.
- NO fork source edit, NO regeneration, NO relink, NO observer rebuild.

## Alternatives considered before measuring
(a) successor node and data region silent post-park -> E23's KILLED verdict
    is exhaustive over the source structure;
(b) either moves post-park -> E23's verdict was watch-set-limited and the
    demand edge reopens with a measured bound;
(c) the semaphore wait resolves upstream of MPEG -> the MPEG stall is a
    symptom and X moves again;
(d) observation fails (no receipt) and nothing is decidable.

## Strict order
Contract -> admission -> checkpoint (unloaded) -> observer-loaded regression
-> boot design -> ONE boot -> mine -> fix gate -> close.
Any red checkpoint gate: table and STOP with no boot.

## Fix gate (strict, unchanged)
Implement ONLY if the diagnosis isolates ONE edge with a minimal
ABI-preserving change + its own fail-before + full regression. No decoder,
EOF or policy invention; no fabricated frames. The MPEG demand edge is
CLOSED (all candidates killed) -- a fix, if any, lives upstream now.
"Guest never sends more without X" -> NAME X and STOP.

## Preserved constraints (ABI carry)
Caller-owned synchronous dispatch; word0-only cbData; v0 discarded;
valid-no-input waits; dispatch outside the MPEG mutex; delete/reset
cancellation; stream behaviour unchanged. No CSV, main, scheduler or
stream-callback edits.

## Bounds
Time box 8 h from `2026-09-22T11:31:22Z`, deadline `2026-09-22T19:31:22Z`.
ONE title boot maximum. ONE lease claim, atomic, clean release, post-release
`pgrep` check. Lease occupied -> table and stop, no wait.
No CSV/regen (regen need = stop). No fork behavior commits outside the fix
gate. Internal reservation 512 MiB (E23 amendment A1 carried: the relink
that justified 3 GiB is not repeated in this lane and every large artifact
goes to the SSD), floor 2 GiB + 0.5 GiB guard. SSD reservation 16 GiB in NEW
`e24-*` paths (tooltmp 8, fixtures 2, probe 1.5, reserve 4.5), same
floor/guard. `COPYFILE_DISABLE=1` on every SSD step. No reclaim, no deletion.

## Publication
Evidence-only `[E24]` commit, `git add -f`, trailer `Orchestrated-By: Muse
Code`. Not pushed; the orchestrator pushes at poll.
