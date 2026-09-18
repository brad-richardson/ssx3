# P1e — SSX 3 on PS2Recomp, Part 6: who returns the main thread to 0, and who owns semaphore 26

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
sections P5-2 (sweep, current CSV = `$W/P1/ssx3-functions.sweep.csv`,
runner sources already refreshed from it), P5-3 (strict build dir
`/tmp/p1-link-strict`, the startup Return-to-0 in `sub_0042CB78`), P5-6
(commands). `W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1e`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, push `fork ssx3`, boots foreground 3 min with
`PS2X_DIAG_PERIOD_MS=5000`, logs `$W/P1/run/boot-p1e-N.log`). Time box
4 hours.

## Facts you start from

Boot-p1d-2 (strict): thread 1 (entry 0x100008) is Dormant with pc 0
after 22 schedulings; thread 2 (entry 0x3e3be0, priority 12) parks in
WaitSema on semaphore 26 after one scheduling. The only Return-to-0
diagnostic in the log fires at startup in `sub_0042CB78` (a bss-clear
loop reached from crt0 with ra 0, trace `0x100008 -> 0x42c300 -> …`)
and execution continued past it, so it is not what made thread 1
Dormant 22 schedulings later. `reportMissingFunction`
(`ps2_runtime.cpp:1228–1384`) has a first-report path (`firstReport`,
~line 1368): establish whether reports are de-duplicated per target,
because a second return to target 0 would then be silent.
`EeScheduler::run()` makes a thread Dormant at two sites
(`EeScheduler.cpp` ~396: pc 0 after a generated function returns; ~432:
pc with no function slot).

## Step 1 — Dormant receipt (one commit `Diag:`, one build, one boot)

a. At both `makeDormant` sites in `EeScheduler::run()`, when
   `PS2X_DIAG_PERIOD_MS` is set, print one line `[diag:dormant]` with
   thread id, entry, the context's pc, ra, sp, gp, v0, a0, the
   scheduling count, and `m_runtime.formatDispatchHistory()` (the same
   trace string the missing-target line prints).
b. Add env `PS2X_DIAG_REPORT_ALL=1`: when set, `reportMissingFunction`
   prints every occurrence (no first-report suppression, no per-target
   de-dup), and every Return-kind report also prints the dispatch
   history. Keep the default behaviour unchanged when unset.
c. Rebuild the strict dir (`/tmp/p1-link-strict`) and boot 1 with
   both env vars. Receipts: the diff, binary sha, the `[diag:dormant]`
   line for thread 1, every Return-to-0 line (count them), and the
   dispatch history preceding the Dormant event.

## Step 2 — name the returner (no build)

From the dispatch history and the ra/sp in the Dormant line: the guest
function that executed the final `jr $ra` with ra 0 (resolve through
the sweep CSV), its caller chain from the trace (each hop resolved to a
CSV row), and a quoted body of at most 40 lines around the return.
State what the function was doing (an SDK routine name if the SDK
pattern is recognisable: `sceSif*`, `sceCd*`, `scePad*`, `sceMc*`,
`sceGs*`, `_start`/`main`, memory-card or disc checks) and which
condition led to the return (the register values on the line). If the
returner is the game's `main`, quote the branch in `main` that exits
and the value it tested.

## Step 3 — semaphore 26 (no build)

Which `CreateSema` produced id 26 (order among the CreateSema calls,
caller site from the histogram ra or the generated source), which
guest sites `SignalSema`/`iSignalSema` that stored id, and which thread
they belong to. Table.

## Step 4 — one fix, one boot (only if Step 2 names something the runtime owns)

If the returning branch tests a value an HLE stub or syscall produced
(a return code from `sceCd*`, `sceMc*`, `scePad*`, `sceSif*`, a
`ReferThreadStatus`, a `GetMemorySize`, a disc-type check), implement
or correct that value in `Kernel/Stubs/` or `Syscalls/` per the SDK
(state the value chosen and its source), commit (`CD:`/`MC:`/`Pad:`/
`SIF:`/`Kernel:` prefix), rebuild the normal dir (`/tmp/p1-link`),
boot 2, record the ladder (first new syscall id, threads at last dump,
first VIF MPG/MSCAL, first GIF kick, first presented frame, crash,
missing targets). If the return is a recompilation artefact (a
cross-function `j` or fallthrough that the recompiler turned into a
C call so the guest ra never got set), record the exact instruction
pair and the generated code for both sides, implement nothing, and
stop at Step 5.

## Step 5 — report

Append `## Part 6` (P6-0 lease, P6-1 diag diff + dormant/return lines,
P6-2 returner table + quoted body, P6-3 semaphore 26 table, P6-4 fix +
ladder or artefact record, P6-5 binaries and commits, P6-6 exact
commands, P6-7 what I could not do) to
`/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`; commit
with `git add -f`, prefix `[P1e]`, trailers; push the fork; remove the
lease; stop.
