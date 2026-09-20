# P1aj — Drain-termination diagnosis: what ends the 31-drain? + next-experiment spec (Part 33, no boot)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/T15/REPORT.md` first (all of it —
NO post-241 event to the 2400 s cap: the 31-drain runs 71,762
iterations over 235 blocks and never idles; main stays DORMANT;
dma/gif frozen 160 pairs; N = 72,176 third count), plus P1
REPORT Part 32 (P1ai's post-exit diagnosis: drain = 781-iter
pump subprocess, W1–W12 watches, M1–M10 miner rows — T15
never read it; you reconcile it) and `local/research/T13/
REPORT.md` §T13-1 (the exit table). This is a DIAGNOSIS brief
on committed logs — no boot. Your §P33-4 next-experiment spec
is read by the boot brief that follows — write it to be
executed. Peer lanes run concurrently — you share only the fork
remote (read-only for you).

## Facts you start from

- Inputs (read-only, never copy 6.6 GB anywhere — stream it):
  `W/P1/run/boot-t15-1.log` (2,857,096 lines),
  `W/P1/run/ps2_log-t15-1.txt` (187,727,172 lines, post-phase
  ≥ line 185,264,991), T15's `blocks.tsv` (477) + `ticks.tsv`
  (267), T13's logs + TSVs for the 781-vs-71762 join,
  `W=/Volumes/Extreme SSD/ps2recomp-spike`.
- Drain landmarks (T15 — verify, don't trust): 31w/s31
  143940/143939 (+1 in-flight); drain = 71,762 iters =
  Δ(31−29); 9-func ×143,524 drain family; 0/31 every post
  block (min 295 @b415); 3E4AF0 ×21026 post-phase; main
  dormant ×237; t4 sole LIVE thread (P1ai — re-verify on
  T15's log); sema-30 4w/3s parked, t3 never releases.
- The question: WHAT ENDS the drain (a terminator in the
  9-func family? a counter? an external signal that never
  comes?) — per-iteration inputs across 71,762 iters (fixed
  point or drift?) — and WHAT exact experiment breaks the
  park (longer boot bound? stimulus? probe?). Answer by table.

## Gates and rules

- NO lease of any kind (diagnosis brief — no boots, no harness
  runs). No fork changes at all. No `adb`. Read-only on every
  other agent's dirs; scratch in `/tmp/p1aj/`; stream the
  6.6 GB trace (never copy it).
- Evidence: APPEND Part 33 to `local/research/P1/REPORT.md`
  (do NOT rewrite earlier Parts; a peer brief may own other
  regions — append only). Commit with `git add -f`, prefix
  `[P1aj]`, trailer `Orchestrated-By: Muse Code`. NEVER run
  `git push` in ssx3.
- Time box: 4 h. Tables, no verdicts.

## Task 1 — P32-6 reconciliation (§P33-1 — what did T15 answer?)

1. Watch table: P1ai's W1–W12 vs T15's 7 generic watches
   (which W-rows were covered? which fired/answered?).
2. Miner table: P1ai's M1–M10 rows vs T15's §T15-2/3 tables
   (which M-rows got values? which stay open?).
3. Invariant table: P1ai's 10 next-boot invariants vs T15's
   exit-invariant (§T15-1 — reproduced? deviated?).

## Task 2 — drain fixed-point analysis (§P33-2 — 71,762 iters)

1. Iteration table: drain iterations chunked (per-1000:
   func mix, call ratios, sema values — fixed point or
   drift across the 71 chunks? first vs last chunk rows).
2. Input table: per-iteration INPUTS of the 9-func family
   (sema addrs/values? counters? buffer states? — what
   does each iteration read, and does any input change?).
3. Terminator table: the 9 funcs + 3E4AF0 roles from
   `ps2_recompiled_functions.h` (which func COULD end the
   drain? what condition does it test? table the branch
   rows, don't execute).

## Task 3 — park-break census (§P33-3 — what never comes?)

1. Waiter table: every parked waiter at cap (t1 dormant?
   t3 on 30? t4 on 31? t6 on 36? — who waits on WHAT with
   which values, T15's tail window).
2. Missing-signal table: sema-30's 4th signal (still 4w/3s
   to cap — who SHOULD signal? tamp the code path),
   IOP announcer (0 sightings — where would it appear?),
   0x3C45C0 (0 sightings — what arms it?).
3. Halt-split table: block-239 5/296 (T15) vs 117/298 (T13)
   with exact last-29-signal lines in BOTH runs (bound
   the halt point tighter than either run alone).

## Task 4 — next-experiment spec (§P33-4 — the follower reads this)

1. Experiment table: the 3 candidate next experiments
   (longer boot with bound? IOP/sema stimulus? new probe?)
   with exact trigger rows + success rows + miner rows.
2. Bound table: for the longer-boot candidate, the bound
   math (what N2/drain-count would falsify "infinite"?).
3. Lease table: which experiments need the P-lane lease,
   boot caps, and script derivations (T15's scripts +
   rows to change).

## Report

Append `local/research/P1/REPORT.md` Part 33 (§P33-1..4 +
exact commands + receipt paths + "What I could not do").
Commit (`[P1aj]`, no push), stop.
