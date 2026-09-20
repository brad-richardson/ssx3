# E2a — STIMULUS pad-state: flip buttons/analog mid-drain, does the 326EB0 arm fire (P-lane lease)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read P1 REPORT Part 34 §P34-2c first (the E2a
brief-shape row — trigger rows, success rows, miner rows,
inputs — plus §P34-1c guard table: T8's 326EB0 live-span
branches, jointly fixed by the exact 2×/iter pad-pair over
719,498 pairs, per-branch proof missing), plus
`local/research/T16/REPORT.md` (the E1 baseline this run
perturbs: exit @b235, drain 359,748 iters, bands w31 294–308
/ d-w31 [1.9,2.2] / gaps {6,7}) and T18's ladder precedent
(fork-diff + rebuild + sha-record discipline). This is the
first live stimulus experiment: it DELIBERATELY changes guest
behavior mid-drain. Peer lanes run concurrently — you hold
the P-lane lease for the stimulus boot(s).

## Facts you start from

- Fork `$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`,
  branch `ssx3` (table HEAD at start; T18's `f2b1852`
  channel is HEAD unless something moved — record don't
  fight). Stimulus surface: `ps2xRuntime/src/lib/Kernel/
  Stubs/Pad.cpp` (buttons active-low, default 0xFFFF;
  analog center 0x80; digital mode 0x41 — P34-verified).
- The stimulus: a fork hook flipping pad state mid-drain,
  post-exit (buttons and/or analog — table the exact flip
  + arming tick BEFORE the boot; arming = block count or
  drain-iter count, recorded). Rebuild `-j4`, record binary
  sha + size (T13 §T13-0 style). Keep T18's channel ON as
  well (dual-purpose boot: stimulus response + EE stream).
- Fixed baselines the run must reproduce BEFORE the arming
  point (or table the deviation exactly): T16 exit @b235,
  residue-13 from b240, drain bands (w31 294–308, d/w31
  [1.9,2.2], gaps {6,7}) up to arming.
- Trigger = stimulus response: residue ≠13 OR new HLE
  target in stubs OR 326EB0/iter ≠2 OR the dormant
  326EB0 arms fire (0x3FF708@0x326EE4 or 0x3FFBC0@0x327080
  executes) — plus E1's no-break watches (main wake, new
  caller, dma/gif unfreeze, 2nd halt). Cap = 2400 s per
  boot (arming must land well post-exit; 2nd boot ONLY if
  stimulus timing missed — table why).

## Gates and rules

- Lease `E2a`: stimulus boot(s) ONLY while holding
  `/tmp/ssx3-p-lane-lease` (the SHARED P-lane lease) — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/e2a-waits.log`. Max 2 boots ≤2400 s each.
  Builds any time (`-j4`). No `adb`.
- Fork diff = the experiment (stimulus hook + arming tick):
  minimal diff, committed to the fork's `ssx3` branch ONLY
  (never push the fork past origin rules — table the fork
  commit; ssx3 evidence NEVER pushes).
- Evidence dir `local/research/E2a/` (STANDALONE — do NOT
  append to `P1/REPORT.md`). Commit with `git add -f`,
  prefix `[E2a]`, trailer `Orchestrated-By: Muse Code`.
  NEVER run `git push` in ssx3.
- Time box: 6 h. Tables, no verdicts.

## Task 1 — stimulus boot(s) (response or cap)

1. Pre-claim checks (T13 §T13-0 verbatim + stimulus): lease
   absent, `pgrep -x ps2EntryRunner` exit 1, stimulus
   binary sha + size, ISO + ELF sizes, free space,
   waits-log tails, arming-point record.
2. Claim → monitor first (E1 watches + E2a armed rows:
   residue, stub targets, 326EB0/iter) → foreground boot
   → on trigger: 30 s grace → SIGTERM → release AT ONCE
   → trace copy (lease-free) → analysis. If the exit
   invariant FAILS (no block-235 collapse), table the
   deviation exactly and still run to cap.
3. 2nd boot ONLY if stimulus timing missed (arming never
   reached or stimulus never injected — table the miss,
   adjust, re-run once).

## Task 2 — stimulus-response tables (whatever the run shows)

1. Pre-arming table: T16 baselines reproduced to arming?
   (exit row, residue, bands — match/no vs T16).
2. Response table: first stimulus response (block, wall,
   logline, which armed row fired — or NONE (bands hold
   through stimulus: absence with a bound)).
3. Diff table: pre/post-stimulus residue diff + pad/HLE
   call census + 326EB0 enter census + T8 branch split
   if fired (E1 miners P33-4a M1–M10 + P34-1a/b/c).

## Report

`local/research/E2a/REPORT.md`: T13-0..T13-7 SHAPE (lease
record, stimulus diff record, pre-arming/response/diff
tables, exact commands, gaps — incl. E2b/E2c/E3 reads if
the response reshapes them). Commit evidence (`[E2a]`, no
push), remove the lease if held, stop.
