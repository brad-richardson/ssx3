# P1ak — E1 long-window diagnosis: does the fixed point hold over 359,749 iters (no boot)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/T16/REPORT.md` first (all of it —
E1's 7200 s run: NO drain break, 359,748 iters, N = 72,176
exact, 887 frozen pairs, 4 disclosed deviations), plus P1 REPORT
Part 33 (P1aj's drain-termination analysis: fixed point from
iter 2, 13-row terminator table, E2/E3 spec — your baseline)
and `local/research/T16/blocks.tsv` + `ticks.tsv` (per-block /
per-tick rows). This run diagnoses T16's long window WITHOUT
booting (T13/T16 logs read-only). Peer lanes run concurrently —
no lease; T17 holds no lease either (bytesize).

## Facts you start from

- Logs (read-only): `$W/P1/run/boot-t16-1.log` (4,315,920
  lines) + `$W/P1/run/ps2_log-t16-1.txt` (197,603,104 lines)
  on the SSD. Stream + seeks; never copy whole.
- Fixed baselines to check over the 5× window (or table the
  deviation exactly): 15-func/34.29-line fixed point iters
  2–359,748; 3E4AF0 gaps {6,7} only; halt trio +0/+1/+2;
  sema-31 294–308/block; residue-13 same addresses;
  syscall ids {0x44, 0xffffffbd} post-241; 113 post funcs,
  0 post-only; empty stack at EOF.
- The 4 deviations to disposition (one-block-shorter tail,
  preamble T11-repeat 961/497, probe NULL-head 3135 −1,
  exit-tail singleton-58, chunk-71 span +2 — five with the
  tail): reproduce each from the logs, table whether each
  recurs vs T13/T15, and whether any touches the drain
  (all read pre-exit so far — verify, don't assume).
- The question: Part 34 — (a) fixed-point reconfirmation at
  5× scale, (b) deviation dispositions, (c) terminator-table
  bound updates (monotonic horizons now 5× tighter in
  evidence, same in claim — recompute), (d) E2/E3 firm-up
  (stimulus rows + probe rows promotable to briefs?).

## Gates and rules

- NO lease of any kind (no boot — diagnosis only). No fork
  changes at all (no source edits, no commits, no push).
  No `adb`.
- APPEND Part 34 to `local/research/P1/REPORT.md` (P-lane
  convention — one running report; append-only, no edits
  to Parts 1–33). Commit with `git add -f`, prefix `[P1ak]`,
  trailer `Orchestrated-By: Muse Code`. NEVER run `git push`
  in ssx3.
- Time box: 4 h. Tables, no verdicts.

## Task 1 — fixed-point reconfirmation (does it hold at 5×?)

1. Chunk table: per-1000-chunk schema (§P33-2a) over iters
   1–359,749 (distinct counts, lines/iter, 9-fam rate —
   chunk-0 tail-in-iter-1? chunks 1–358 fixed? final cut?).
2. Cadence table: 3E4AF0 gap histogram + per-1000 146/147
   alternation over the full window (any gap outside {6,7}?
   any cadence drift in chunks 72–359?).
3. Guard table: the 13 terminator rows re-polled over
   blocks 242–1429 (any row nearer its trip than at T15
   scale? monotonic counters advanced how far?).

## Task 2 — deviations + E2/E3 firm-up (what's new? what's next?)

1. Deviation table: the 5 deviations reproduced + T13/T15/
   T16 recurrence matrix + drain-touch verdict per item.
2. Bound table: terminator-table horizon recompute at
   359,749-iter evidence (which bounds tighten? which are
   evidence-invariant?).
3. E2/E3 table: each E2 stimulus row + E3 probe row from
   §P33-4a promoted to brief-shape or tabled why-not
   (inputs needed? lease? boots?).

## Report

P1 REPORT Part 34: reconfirmation + deviation + bound +
E2/E3 tables, exact commands, gaps. Append-only commit
(`[P1ak]`, no push), stop.
