# P1m — SSX 3 on PS2Recomp, Part 14: diagnose the outer-caller watch-miss mechanism (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 13 first (P13-3 outer-caller receipt + derivation audit, P13-6
could-not-do), plus Part 12 §P12-1d (the 8-candidate table) and Part 6
(P1f watchpoint behavior: `sw`/`sq` covered, `sd` path suspect).
`W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1m`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1m-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1m-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Time box 4 hours.

## Facts you start from

Two boots (p1k, p1l) watched arithmetically-correct addrs for the
driver `sub_003DD1D8` frame (`0x1ffe000` for the `sw` at `0x3dd1e0`,
`0x1ffe010` for the `sd` at `0x3dd214`) and caught 0 hits on both —
only pre-park `sq` zero-clears. The P12 `sd`-path theory is now
insufficient (the `sw` is covered yet also missed). The driver IS live
in steady state (run `0x3e5928` callers are only the driver,
`firstRa=lastRa=0x3dd290`, all blocks both boots). 8 outer-caller
candidates stand (P12-1d). Out of scope: the `*(entry+8)` driver-flag
writer, sema-26 non-delivery, any runtime fix — miss mechanism only.

## Step 1 — mechanism hunt from the closed logs + sources (no lease, no boot)

a. **Watchpoint coverage audit.** Which store paths fire
   `PS2X_DIAG_WATCH`? Read the watch hooks (`ps2_runtime.cpp`
   WATCH parse/hooks from P12-6 + P1f stack-map work): `sw`? `sd`?
   `sq`? `sb`/`sh`/`swl`/`swr`? cached vs uncached segment? KSEG
   aliasing? Table each path: fires / never-fires / unknown, with
   file:line. If the driver's `sw`/`sd` take a never-fire path,
   that IS the mechanism — name it.
b. **Driver-entry census.** Is `0x3dd1d8` entered per-period or once
   at setup? Stub/histogram/call evidence from boot-p1l-1 (and p1k).
   If entered once, the frame writes happened before the watch
   mattered — table the entry count + first/last evidence.
c. **Frame placement.** sp at driver entry vs park sp `0x1fffd80`:
   same frame or shifted? Which of the 8 candidates actually place
   the driver frame at the watched addrs (call-site sp arithmetic
   per candidate, one row each)?
d. State the single most likely miss mechanism and design the ONE
   receipt for Step 2 that distinguishes it (whole-frame watch range?
   driver-entry probe? ra-sample at `0x3dd1d8` entry?). If Step 1
   fully determines the mechanism from closed sources, skip Step 2.

## Step 2 — one boot only for the distinguishing receipt (≤90 s)

Current `/tmp/p1-link` binary (state sha; rebuild first only if stale),
p1l env + the Step-1 receipt mechanism, foreground max 90 s, log
`$W/P1/run/boot-p1m-1.log`. Release the lease immediately after.
Receipts: the mechanism answer (caller named or mechanism proven +
  next receipt), plus the standard ladder row.

## Step 3 — report

Append `## Part 14` (P14-0 lease record, P14-1 coverage audit +
entry census + frame table, P14-2 boot + mechanism answer, P14-3
binaries and commits, P14-4 exact commands, P14-5 what I could not
do) to `local/research/P1/REPORT.md` in
`/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1m]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push — verify up-to-date); remove the lease if held; stop.
