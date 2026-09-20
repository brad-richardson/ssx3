# P1x — PCSX2 reference trace of the real boot (read-only)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `docs/research/review-2026-09-19-progress.md` §7.3
first (the ask), plus `local/research/P1/REPORT.md` Part 23 §P23-2d (the
fork's current event skeleton — the shape your reference must beat). This
brief produces the ordered ground-truth boot sequence the fork must
reproduce. No fixes, no fork writes, no fork boots.

## Facts you start from

P2 read PCSX2 source (negative on semantics); this is different: a RUNTIME
trace — EE syscall/thread/CD logging on the real ISO to the first menu
frame. A reference clone (`pcsx2-ref`) exists — verify its path, do NOT
assume. The trace (or the exact reason it cannot be produced headless) is
the deliverable. P1w runs concurrently in another pane (fork tooling,
appends to `P1/REPORT.md`) — you share nothing with it.

## Gates and rules

- READ ONLY everywhere: no fork writes/commits/pushes, no ssx3 writes
  outside your evidence dir, no fork boots, no lease (host-only work),
  no `adb`. Never download emulators, BIOSes, or runtimes — installed
  tools and the reference clone only.
- Disk: internal disk is tight — work under
  `/Volumes/Extreme SSD/ps2x-p1x/` (new dir); the trace itself goes to
  `$W/P1/ref/` (`$W=/Volumes/Extreme SSD/ps2recomp-spike`; create the
  dir) with its bytes + sha recorded. Never touch `/tmp/p1-link`,
  `ps2x-i*`, or other agents' dirs.
- Evidence dir `local/research/P1x/` (STANDALONE — do NOT append to
  `P1/REPORT.md`; a peer brief owns it concurrently). Commit with
  `git add -f`, prefix `[P1x]`, two-trailer convention (copy from the
  previous ssx3 commit). NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Survey.** How to run PCSX2 headless/batch with EE logging
   (reference-source flags, `--batch`/`--nogui`/CLI, log channels).
   Table every option with file:line or `--help` receipts.
2. **Capture.** Run to the first menu frame (or the furthest
   obtainable); record the exact command, wall time, and exit. Store
   the trace under `$W/P1/ref/` + sha.
3. **Distill.** An ordered event table (syscall/thread/CD sequence) +
   a histogram in the fork's §P23-2d shape, so future parks diff fork
   vs reference directly. If headless capture is impossible: the exact
   blocker + cheapest path (Xvfb? scripted GUI? source patch?) as gap
   rows — the negative result IS the deliverable, no heroics.
4. **Report.** `local/research/P1x/REPORT.md`: method, trace receipts,
   event table/histogram OR blocker+path, exact commands, receipt
   paths, "What I could not do". Commit, stop.
