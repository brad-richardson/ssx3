# P1ah — Hash-phase work census: progress indicators + completion projection from the P1ag 300 s trace (no boot, no fork changes)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Parts 29–30 first
(P1af: unpark + main RUNNING; P1ag: 300 s, 4th sema-30 signal still
absent, 13,108 balanced `0x362DE8` invocations, stubs steady 222,
no new park, phase-exit "not projectable — total phase work
unknown"). This brief squeezes the EXISTING receipts for
phase-progress indicators. No new boot can beat this brief's cost
(zero lease, zero fork risk) — run it before anyone schedules a
600 s boot. Peer lanes run concurrently; T1 owns the fork tree
(never stage/touch/commit foreign files; you make zero changes).

## Facts you start from

- Receipts (read-only): `$W/P1/run/boot-p1ag-1.log` (475,304
  lines, 84,053,701 B) + `$W/P1/run/ps2_log-p1ag-1.txt` (1.27 GB
  trace, 35.9M lines); P1af's 2×90 s pair for rate comparison.
  `W=/Volumes/Extreme SSD/ps2recomp-spike`.
- Known: probe cap (20k) hides late-phase probe bodies; trace has
  enter/exit but no args; CD did no new work in the extended
  window (810 lbns, first-last identical P1af→P1ag); the phase is
  driven through `0x362DE8` ← caller `0x36356c`
  (`sub_00363490+0xdc`, per P1af ticks — confirm at 300 s scale).
- The question: is there a progress indicator anywhere (counter,
  trend, work-list shrinkage) that projects phase completion? A
  well-evidenced NO is a complete result — but it must name the
  ONE minimal receipt that WOULD decide it.

## Gates and rules

- NO lease (no boots at all). ZERO fork changes (no source edits,
  no commits, no push). No `adb`. Read-only on every other
  agent's dirs and the ISO.
- Evidence: append Part 31 to `local/research/P1/REPORT.md` ONLY
  (no other ssx3 files). Commit with `git add -f`, prefix
  `[P1ah]`, trailer `Orchestrated-By: Muse Code`. NEVER run `git
  push` in ssx3.
- Time box: 4 h. Tables, no verdicts.

## Task 1 — progress-indicator hunt (trace + log mining)

1. Invocation-rate shape: `0x362DE8` enter rate per 60 s slice
   (speedup / steady / slowdown?); same for `0x394ED0` /
   `0x395000`. A decelerating rate with a trend tabled is a
   projection input; a flat rate is a NO input.
2. Caller confirmation: `0x362DE8` callers at 300 s scale (is
   `0x36356c` still the only driver? any new caller = new phase
   edge — table it).
3. Counter slopes: dma/gif tick deltas per block (linear?
   kinked?); dormant-count slope; 29/31 handshake volume slope.
   Any slope break = candidate phase edge with block + evidence.
4. Early-phase probe trend (the capped 20k window): `total`
   `0x2`→`0x14` (P1af) — table total-vs-n, arena growth,
   distinct-key growth. Extrapolate ONLY with the fit + residuals
   tabled; no bare projection.
5. CD/SIF/GS silence: confirm zero new CD/SIF/RPC/GS work past
   the P1af window (or table the first new event with line + pc).

## Task 2 — completion projection (or the deciding receipt)

1. If a progress indicator exists: project phase completion (fit
   + confidence inputs tabled, not a bare time) and state what
   the FIRST post-phase event should look like (which trace
   signature would confirm exit — for the next boot brief).
2. If none exists: table the examined-and-absent list (indicator,
   where looked, why it reads flat/silent), then specify the ONE
   minimal receipt that would decide projection (a probe field?
   a counter? which function, which arg, what trend?) and who
   should emit it (T1's snapshot emitter? a P1ad-style probe
   brief? — name the owner, don't build it).
3. Either way: 600 s boot recommendation as a TABLE (cost:
   ~10 min lease + T1 contention; value-if-hit; value-if-miss)
   — no verdict, the numbers only.

## Report

Part 31: indicator tables (rate shapes, caller, slopes, probe
trend, silence audit) + projection-or-receipt + 600 s cost
table + gap rows. Commit REPORT.md only, stop.
