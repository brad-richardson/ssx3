# AC1 — 0x12 alarm/timer/INTC contract validation (read-only)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read first: `local/research/K1/REPORT.md` §K1-10 (R1A vs K1
alarm rows), §K1-13 (G7: `0x12C` timer-3 structural difference — this brief),
and the refinement-2 correction (absence explained by `InitAlarm@0x42C7C8` +
`InitThread` HLE collapse — compare semantics, not counts) + the guest alarm
block at `42c768` (R1A: 8/6/2 install shape incl. `SetSyscall(0x12c)`,
timer-3 meaning per Play!) + the `InitAlarm` HLE implementation source. K1
proved the absence is explained at call-path level; this brief validates the
replacement CONTRACT and bounds the downstream effect of the missing `0x12C`.

## Facts you start from

- Reference side (R1A recompiler trace post-`ExecPS2:5`): alarm installer
  block present with 8/6/2 shape; `SetSyscall(0x12c)` present (timer-3);
  `AddIntcHandler (10)` / `_EnableIntc (14)` / `_DisableIntc (15)` = 7/7/5.
- Runtime side (K1 boot-1, committed `syscalls-k1-on.txt`): alarm block
  HLE-collapsed (0/0/0); `SetSyscall(0x12c)` absent; INTC triple = 6/6/5
  (within 1 —.counts are explicitly NOT the question).
- Deliverable 1 — contract table: guest alarm-block behavior (calls × args
  × timing/interrupt effects, each with source bytes) vs HLE replacement
  behavior (same columns from the HLE source). Every row ends in: EQUIVALENT
  (with the proof line), DIVERGENT (with the consequence), or OPEN (with the
  exact probe that would close it).
- Deliverable 2 — downstream-effect table for the missing `0x12C`: who
  consumes timer-3 state downstream (callers + readers, sourced), what each
  consumer observes under the HLE replacement vs the guest block, and
  whether any in-window behavior differs (committed traces only).
- READ ONLY: `grep`/`sed`/`awk`/reads + read-only `git`; committed traces
  + R1 report + sources. No boots, no lease, no fork writes, no `adb`. If a
  question needs a run, table it as an OPEN row with the exact command.

## Gates and rules

- `export COPYFILE_DISABLE=1` on every SSD step (reads only).
- Evidence dir `local/research/AC1/` (STANDALONE). Commit with `git add -f`,
  prefix `[AC1]`, trailer `Orchestrated-By: Muse Code`. Do not push (the
  orchestrator pushes at poll when the tree is clean).
- Experiment contract up front (hypothesis/observable/alternatives/stop).
  Time box: 3 h. Tables, no verdicts.
- Hygiene: report in chunks + tail receipt (truncated tail fails the gate).

## Task 1 — contract table (guest block vs HLE replacement)

1. Disassemble/tabulate the guest alarm block (`42c768`, 8/6/2 shape):
   calls, args, timer programming, INTC effects — all from committed
   bytes/traces.
2. Tabulate the HLE replacement (`InitAlarm@0x42C7C8` + `InitThread`
   collapse) in the same columns, from source.
3. Row dispositions: EQUIVALENT / DIVERGENT / OPEN per the rules above.

## Task 2 — 0x12C downstream effect

1. Consumer table: every timer-3 reader/caller + what it observes under
   each side + whether in-window behavior differs (trace evidence).
2. Gap list: anything unresolvable statically, each with the exact run
   that would resolve it.

## Report

`local/research/AC1/REPORT.md`: contract, consumer table, INTC/timer
comparison (semantic framing), exact commands, gaps. Commit evidence
(`[AC1]`), stop.
