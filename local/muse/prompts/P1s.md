# P1s — SSX 3 on PS2Recomp, Part 20: sema-26 delivery mechanism (diag + boots)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 19 first (P19-1a callback→wake link, P19-2b the :433→:434 order
receipt, P19-5 the unwarchable-count + pump-sema residues), plus Part 17
§P17-1 (sema-26 history). `W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules
exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1s`, no adb,
never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1s-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1s-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1r proved the ORDER: the worker re-parks at G0 before the CD callback's
signal, and the completion wake never lands (site #9 + G6 unreached).
Open: the delivery MECHANISM — why a signal-during-park on sema 26 never
wakes thread 2. Known: sema id 26 (`*(0x519C4C)`, max `0x20`, init 0);
callback `0x3e3ad8` → `jal 0x423DD0` (iSignalSema); worker waits via
`jal 0x423DE0` (WaitSema); first signal (3E4648 @ `0x3e48b0`, thread 1)
DOES wake; pump `0x3E5760` signals some unobserved sema. The sema count
is host-side `EeScheduler` state (RDRAM-unwatchable). Fork HEAD
`e73e36a`. This is now the critical-path item: nothing else unblocks
FILESYS. Diagnose only — no behavior fix (a `Diag:` logging commit is
allowed, nothing else).

## Step 1 — static: the signal/wait paths (no lease, no boot)

a. **Wait path.** `WaitSema` (`0x423DE0`) → scheduler: thread-state
   transition, which queues hold thread 2, what a wake requires
   (count>0 at wait time? pend on signal?). File:line per step.
b. **Signal paths.** `iSignalSema` (`0x423DD0`) from callback context
   vs `SignalSema` (`0x423DC0`) from thread context: do both reach the
   same wake logic? Any "called from callback/scheduler" guard,
   deferred queue, or dropped-if-not-waiting branch? The first
   (thread-1) signal wakes but the callback signal doesn't — table
   every code difference between the two paths.
c. **Name the pump's sema** (P19-5 residue): `*(mutex+0xC)` value —
   static fill-site search; if unresolvable statically, fold into
   Step 2's logging.

## Step 2 — one `Diag:` commit + boots (≤2)

Env-gated (default off) log line on sema-26 signal AND wake-check
(sema id, count before/after, waker context thread/callback, target
thread state): the minimal pair that shows the callback's signal
arriving at a parked thread 2 and the wake decision. Rebuild,
`ps2xTest` (424/425 baseline stands — re-confirm, do not fix), boot
≤90 s each. Receipts: the signal/wake line pairs (or the absence
that names the break), plus the standard ladder row.

## Step 3 — report

Append `## Part 20` (P20-0 lease record, P20-1 paths + differences,
P20-2 dynamic answer, P20-3 binaries and commits, P20-4 exact
commands, P20-5 what I could not do) to `local/research/P1/REPORT.md`
in `/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1s]`, trailers; push `fork ssx3` from the fork clone only; remove
the lease if held; stop.
