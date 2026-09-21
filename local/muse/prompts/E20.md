# E20 — Repair + prove parser-observer forwarding, then resume Q1→Q2→Q3 (E19 recovery; measurement first; fix ONLY the single demonstrated edge)

You are the frontier worker in a herdr panel in `/Users/bradrichardson/dev/ssx3`.
**Tables, no verdicts.** Read `local/research/E19/REPORT.md` + `local/research/E19/NEXT-BRIEF.md`
first (all of both: E19 stopped correctly — its `DYLD_INSERT_LIBRARIES`
interposer recursed at E18 R3 (`RTLD_NEXT` forwarding assumption false:
18,827 enters, 0 returns, SIGSEGV) and honored the any-red rule with zero
boots/edits/commits; Q1/Q2/Q3 never opened). Then re-read
`local/research/E18/NEXT-BRIEF.md` (the parked input→packet questions +
ABI constraints — they BIND this brief). This brief repairs observation,
THEN resumes the original E19 order (Q1 threshold → Q2 demand audit → Q3
demand-watch boot). It fixes a target edge ONLY if exactly one is
demonstrated (S7/S10 stop rule — no stacking, no policy/decoder/EOF
invention, no fabricated frames).

## Facts you start from

- BASE: fork `3adc0478` (E18 BEHAVIOR, PUSHED — verify `fork/ssx3`
  before building). `/tmp/p1-link` + `/tmp/e17-map-link` +
  `/tmp/e18-mpeg-link` exist (PROTECT all + DerivedData; never
  reclaim). Checkpoint re-verify first (fork SHA, 9,457-name audit,
  suite 458/458, E16 closure cases, E15 cases rc0, E18 R1–R6).
- The failed dylib (`parser/e19-parser-observer.dylib`) is a FAILED
  EVIDENCE ARTIFACT — do NOT reuse it for any suite or title run.
  Repair forwarding FIRST and prove it in isolation: one real backend
  invocation per observer call with identical arguments/return
  behavior (table the mechanism — explicit-handle `dlopen` of the
  real libav vs link-order fix vs static link of the observer
  against the real symbols — and why `RTLD_NEXT` lied here); prove
  real `_Exit` counter closure separately (E19's capture lacked the
  footer). Proof = a minimal non-title harness showing 1:1
  enter→backend→return with byte-identical results vs the
  uninstrumented call, BEFORE the observer touches the full suite.
- Then the original E19 order: (Q1) emission-threshold fixtures at
  the 5,040 / 8,192 / 16,384 authored-byte marks (E19's retained
  first64 + authored cases carry over — re-verify, don't re-derive;
  table bytes→packets/frames + the packet-1 threshold); (Q2) static
  demand audit (who asks for more, with what signal, or the proven
  absence — E18's post-input silence is the baseline); (Q3) ONE
  guarded demand-watch boot (fresh T13 pre-claims, shared P-lane
  lease, wall/progress/byte caps, REPORT_ALL=1 + parser-boundary
  observations; lease occupied → table and stop).
- The fix gate (strict, unchanged): implement something ONLY if the
  diagnosis isolates ONE edge with a minimal, ABI-preserving change
  (caller-owned sync dispatch, word0-only cbData, v0-discard,
  valid-no-input waits, mutex discipline, delete/reset cancellation,
  stream retention). "Guest never sends more without X" → NAME X and
  STOP. Any regression red → table + stop (no boot on red), exactly
  as E19 did.
- Regressions: suite 458/458 + all E18 fixtures (R1–R6 + flipped E15
  cases STAY flipped) + E16 closure + prior bindings, run WITH the
  repaired observer loaded (that combination is the regression that
  matters now). No CSV/regen (pure runtime/diagnosis brief — regen
  need = stop).
- Success bars (tabled): forwarding proven 1:1 in isolation (+ `_Exit`
  closure proven); observer-loaded full regression green; threshold
  table; demand-audit verdict; one boot with the second-request
  verdict; EITHER one minimal fix with its own fail-before + full
  regression OR the named next edge.

## Gates and rules

- Fork owner: you. A fix (if the gate opens) is a BEHAVIOR commit
  (named files only — table the set; NOTHING else; push to `fork`
  yourself with the `ls-remote` receipt). Diagnosis-only outcome =
  zero fork commits (evidence only).
- Boots: ≤1 guarded boot under the shared P-lane lease. Fixtures:
  non-title only. No boot without the lease; never wait on another
  lane's lease.
- `export COPYFILE_DISABLE=1` on SSD steps; allocated-byte caps declared
  + tracked (ExFAT). No bytesize/WSL. Host builds `-j2` unless provably
  otherwise (table it). Declare + verify the budget BEFORE editing.
- Evidence dir `local/research/E20/` (STANDALONE). Commit with `git add -f`,
  prefix `[E20]`, trailer `Orchestrated-By: Muse Code`. Do not push ssx3
  (the orchestrator pushes at poll when the tree is clean).
- Experiment contract up front (hypothesis/observable/alternatives/stop).
  Time box: 8 h. Tables, no verdicts.
- Hygiene: report in chunks + tail receipt (truncated tail fails the gate).

## Task 1 — forwarding repair + proof + loaded regression (no title boot)

1. Checkpoint re-verify (fork/9,457/458/E16-closure/E15-rc0/R1–R6).
   Budget declared + verified-fitting before edits. Table the
   forwarding mechanism + why `RTLD_NEXT` lied.
2. Isolation proof (1:1 enter→backend→return, byte-identical, `_Exit`
   closure). THEN observer-loaded full regression (458 + all fixtures
   + E16 closure). Any red: table + stop (E19 precedent).

## Task 2 — Q1 → Q2 → Q3 (+ fix ONLY if gated)

1. Q1 threshold fixtures (retained first64 + authored marks; table
   bytes→packets/frames + packet-1 threshold). Q2 demand audit
   (signal or proven absence). Q3: fresh T13 pre-claims, lease, caps,
   REPORT_ALL=1 + parser-boundary observations; table the
   second-request verdict. First missing link after that → table + STOP.
2. Fix ONLY if exactly one edge demonstrated (fail-before + full
   regression + fork commit + push + `ls-remote` receipt). Handoff:
   the exact next dependency with the missing signal named.

## Report

`local/research/E20/REPORT.md`: contract, forwarding proof, Q1/Q2/Q3,
fix-or-stop, handoff, exact commands, gaps. Commit evidence (`[E20]`),
stop.
