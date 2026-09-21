# EF — Frontier prep: E-lane warm-up + static S-trace (read-only; E7 lead follows)

You are the frontier agent (Codex Astra) in a herdr panel in
`/Users/bradrichardson/dev/ssx3`. You are READING IN tonight to take the
E-lane lead: when worker E6 lands, the orchestrator will hand you its
finding and you will author + execute E7 (the S+0x5a88 join — advance
logic, fix-or-gate decision, implementation if it is an emulator gap).
This brief is PREP ONLY.

## Facts you start from

- E4 located branch (c): steady production draws a real icon into fbp0
  while the display reads black fbp112; Present is faithful
  (`local/research/E4/REPORT.md`, all of it).
- E5 closed the flip contract via J2: per-frame guest-direct display
  re-assert `0x382af0` (~59/s, thread 5, caller `0x38281c`) re-selects
  fbp112 every frame; every field comes from config struct S (`$s0` at the
  call); display-FBP variable `S+0x5a88` stuck at 112 while production
  draws at fbp0 (`local/research/E5/REPORT.md`, all of it, + G6).
- E6 (running now, separate worker) is source-tracing S: allocation,
  writers of `S+0x5a88`, producer-side FBP field, advance/copy logic
  (`local/muse/prompts/E6.md` for its exact scope — do NOT duplicate its
  capture; if it lands first, its finding supersedes overlapping prep).

## Prep tasks (read-only, static, no boots/builds/commits)

1. Read E4 + E5 REPORTs in full + the joined evidence (`e5-watch-series.txt`
   head/shape, `e5-flip-dis.txt`, `e5-history.txt` head, `e5-present.txt`).
2. Static pre-pass, INDEPENDENT of E6: from `$s0` @ `0x38281c` / `$a0` @
   `0x382af0` / `0x37c160` / `0x3827e0`, trace S's allocation site + runtime
   address, all static writers of `S+0x5a88`, the producer-side FBP field,
   and the advance/copy/gate logic (ELF reads via `local/research/AC1/
   ac1_dis.py`-shape tooling, OUT reads, committed-trace joins only).
3. Fix-design angle (your comparative advantage — E6 does NOT do this):
   given the traced logic, table the candidate joins (S+0x5a88 advance?
   blit re-fire? guest gate?), each with: emulator-gap vs guest-gate
   verdict + forcing receipts, candidate fix shape + exact files, risks,
   and the proving receipt. Frame the E7 decision BEFORE E6 lands so the
   handover is instant.
4. Challenge contradicted premises (standing rule): if E4/E5's chain has a
   weak link, name it with tables.

## Gates and rules

- READ-ONLY this brief: no boots, no builds, no lease, no fork writes, no
  `adb`, no commits, no pushes. `export COPYFILE_DISABLE=1` on SSD steps.
- Evidence dir `local/research/EF/` (STANDALONE): `PREP.md` (trace tables
  + fix-design matrix + challenged premises, if any) + miner scripts.
  Commit with `git add -f`, prefix `[EF]`, trailer `Orchestrated-By: Muse
  Code`. Do not push (orchestrator pushes at poll).
- Time box: work until E6 lands or 6 h; the orchestrator will prompt this
  session with the E6 finding + the E7 execution brief when it is ready.
  Tables + hypothesis + next-action recommendation, no verdicts beyond the
  E7 framing.
- Hygiene: report in chunks + tail receipt (truncated tail fails the gate).
