# E3b — One-or-two-frame order capture (boots unparked: same park survived K1)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables +
hypothesis + next-action recommendation, no verdicts.** G0 gate: K1's
gate read confirms the SAME park (threads/semaphores/hot-pc/uploads
identical, counters ≤0.3%) — E3 boots are unparked by the frontier
conditional. Read first: `local/research/E3/REPORT.md` (E3-3 recipe +
E3-4 settling map + E3-0 rec 3 K1-drift warning), `local/research/K1/
REPORT.md` (post-K1 dispatch state, park signature, helpers dormant),
`local/research/T26/REPORT.md` G1 (one-skip vs four-nonzero — the
discrepancy this capture resolves).

## Facts you start from

- Implement the E3-3 taps (fork instrumentation; read the recipe, do not
  reinvent): R1 read-tap at `362DE8` halfword checks + `s1` capture;
  R2 `diagWatchEmit` old-value extension on T26's 83 windows;
  R3 SPR/SIF/file/CD/tick/stub taps with window-intersection filter;
  R4 boundary taps; ONE shared `u64` seq domain; binds `PS2X_E3_INV` +
  `PS2X_E3_BYTES`. Constraint C1: DO NOT force flag values.
- Pre-capture re-verify (post-K1 tree moved): override table contents,
  K1 dispatch state (`[k1]` armed? helper liveness), trampoline/binding
  deltas for every E3 DEAD/COND row. Table the deltas first; stale
  assumptions fail the gate.
- Scope: ONE complete invocation, expanding to at most one or two guest
  frames when needed — NOT another long census. Answer E3-4 rows 1–7
  (SPR overlap? 0x501420 overlap? read-vs-written records? 1-vs-4 skip?
  in-window host writes? scratchpad reuse? post-K1 state?).
- Fork `$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`.
  Plain commits, pushed to the FORK remote only, never upstream. Generated
  runner sources never staged.

## Gates and rules

- Capture boots ONLY while holding `/tmp/ssx3-p-lane-lease` (SHARED P-lane)
  — poll every 5 min + log waits to `$W/P1/run/e3b-waits.log` if taken. Max
  2 boots ≤600 s each (Part 4 budget); EVERY boot script gets wall + progress
  + BYTE caps (table all three binds; abort past cap, keep partial).
  Builds `-j4` any time. No `adb`.
- `export COPYFILE_DISABLE=1` on every SSD step. Retain: the capture + one
  baseline (compress closed raws; single canonical copies).
- Evidence dir `local/research/E3b/` (STANDALONE). Commit with `git add -f`,
  prefix `[E3b]`, trailer `Orchestrated-By: Muse Code`. Do not push ssx3
  (orchestrator pushes at poll). Fork commits pushed to fork remote (table
  SHAs).
- Experiment contract up front (hypothesis/observable/alternatives/stop +
  how each outcome changes the next action). Time box: 6 h.
- Hygiene: report in chunks + tail receipt (truncated tail fails the gate).

## Task 1 — instrument + re-verify (no boot yet)

1. Pre-capture re-verify block (G0): override table, K1 state, binding
   deltas. Table every delta vs E3's static rows.
2. Implement R1–R4 taps + shared seq + binds. Suite must re-green before
   any boot (table counts). Build receipts (binary sha + size).

## Task 2 — capture boot + order tables

1. Pre-claim checks (T13 §T13-0 verbatim + K1 binary sha): lease absent,
   `pgrep` exit 1, ISO/ELF sizes, free space (SSD + internal `df`), selftest
   green, waits tails, THREE caps recorded.
2. Claim → foreground capture boot → at first binding cap: SIGTERM →
   release AT ONCE → analysis (lease-free).
3. Tables: R1 reads+branches (20/invocation), R2 guest writes (old/new),
   R3 host transfers (overlapping only + 8 B slices), R4 boundaries +
   s1-identity; E3-4 rows 1–7 answered; hypothesis verdict + the ONE next
   action.

## Report

`local/research/E3b/REPORT.md`: contract, re-verify table, build record,
suite record, lease record, R1–R4 tables, E3-4 answers, exact commands,
gaps. Commit fork first (pushed fork remote), then evidence (`[E3b]`),
remove the lease if held, stop.

## Frontier evidence correction (same poll — applies before capture, also sent to the worker)

- E3's "every guest store fires" is FALSE for generated constant-address
  FAST_WRITE stores (genFastWrite → no-op trace hook + unwatched
  Ps2FastWrite*; concrete case: generated `42CC88 → FAST_WRITE32(0x456538)`).
  Cover relevant emitted FAST stores or prove target disjointness; zero R2
  rows alone cannot exclude them.
- Overlap tests: normalize RAM/KSEG aliases + SPR offsets, split wrapped DMA
  intervals, dedupe WRITE*/Store* double reports.
- Negative results require capture-complete + dropped/interleaved-row status.
- FIRST-SUCCESS ADDENDUM (no separate boot): enable PS2X_FRAME_DUMP_DIR on
  the capture boot, implement K1 G4 per-path keeps, capture the first-success
  PNG (K1-9 sidecar shape).
