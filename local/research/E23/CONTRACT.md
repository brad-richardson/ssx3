# E23 experiment contract — written before any copy, build, link or boot

## Question
E22 sharpened X to a mechanism (C2a `MPEG.cpp:1757-1760`+`:2484`, C4 `:2496-2513`)
plus a MISSING RULE with two unknowns: the re-ask trigger point and the loop
bound. E22's NEXT-BRIEF states the rule needs a reference this lane cannot
produce. E23 produces the closest in-lane reference: the demand cadence on the
path where the bytes SUFFICE (R3 shape, 240 B authored, frames SERVED), and
names the trigger + bound by comparison against the title stall.

## Hypothesis
H0 (null): the complete-feed path runs a MULTI-ROUND demand cadence — the
type-1 producer fires more than once per `GetPicture` before a frame — and the
round count / stop condition observed there is the missing rule.
H1 (alternative): the complete path fires the type-1 producer exactly ONCE per
`GetPicture`, the same as the title stall, and terminates not by any demand
rule but by the single round happening to suffice. Under H1 the complete feed
supplies NO multi-round reference, and C2a/C4 remain uncalibrated in-lane.

Both are decidable by counting producer firings per `GetPicture` on a path that
demonstrably terminates. The measurement is the same either way.

## Observable
Per `GetPicture`, from runtime-closed receipts:
- count and order of type-1 callback dispatches (`mpeg-call callback=1`),
- count of `sceMpegAddBs` entries (`mpeg-input`) and bytes accepted,
- count of `mpeg-complete` (`completeExternalWait`) edges,
- the thread id and tick of each, in sequence order,
- the terminating event (frame served + resume, or park),
- host parser per-call timing through the reused observer (`parse-enter` /
  `parse-return`, `packets`, `frames`), 1:1 backend forwarding, 4/4 bindings.

## Instruments (no rebuild of the proven instrument)
- `parser/e21-parser-observer.dylib` REUSED by copy + re-sha to
  `e4d88fdc6740449893d5a96c112fae6ce3f19135bad8a309d140d45bbf38e6be`
  (52,472 B). It owns its interface: `PS2X_E21_PARSER_DIR`, `PS2X_E21_PROOF`,
  `# E21 PARSER CLOSURE` stay E21-spelled by necessity.
- Nine E22 tools carried by mechanical rename with byte-empty normalized diff
  (`rename-proof.json`), protected tokens held.
- A NEW E23 fixture entry compiled against the CURRENT UNMODIFIED runner object
  set (the E21 `e21_link_test.py` precedent), driving the E15 actual-wrapper
  shape with the R3 authored payload. No fork source edit, no regeneration.

## Alternatives considered before measuring
(a) the complete path loops and its bound transfers to the title;
(b) the complete path fires once and the loops differ only by byte sufficiency;
(c) the complete path loops but for a reason (registration list, queue drain)
    that does not transfer;
(d) observation fails (no receipt) and nothing is decidable.

## Strict order
Contract -> admission -> checkpoint (unloaded) -> observer-loaded regression ->
complete-feed reference fixture -> join/compare -> ONE title observation design
-> boot ONLY if it measures -> fix gate -> close.
Any red checkpoint gate: table and STOP with no fixture, no boot.

## Fix gate (strict, unchanged)
Implement ONLY if the diagnosis isolates ONE edge with a minimal
ABI-preserving change + its own fail-before + full regression. Policy, decoder
and EOF invention excluded; no fabricated frames. "Guest never sends more
without X" -> NAME X and STOP.

## Preserved constraints (ABI carry)
Caller-owned synchronous dispatch; word0-only cbData; v0 discarded;
valid-no-input waits; dispatch outside the MPEG mutex; delete/reset
cancellation; stream behaviour unchanged. No CSV, main, scheduler or
stream-callback edits.

## Bounds
Time box 8 h from `2026-09-22T00:02:45Z`, deadline `2026-09-22T08:02:45Z`.
ONE title boot maximum (step 4 only, and only if it measures rather than
assumes). ONE lease claim, atomic, clean release, post-release `pgrep` check.
No CSV/regen (regen need = stop). No fork behavior commits outside the fix gate.
Internal reservation 3 GiB (evidence 0.5, fixture/scratch 0.25, reserve 2.25),
floor 2 GiB + 0.5 GiB guard. SSD reservation 16 GiB in NEW `e23-*` paths
(tooltmp 8, fixtures 2, probe 1.5, reserve 4.5), same floor/guard.
`COPYFILE_DISABLE=1` on every SSD step. Large artifacts stay off the internal
volume. No reclaim, no deletion.

## Publication
Evidence-only `[E23]` commit, `git add -f`, trailer `Orchestrated-By: Muse
Code`. Not pushed; the orchestrator pushes at poll.
