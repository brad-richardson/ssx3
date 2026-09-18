# P1c — SSX 3 on PS2Recomp, Part 4: what the guest is waiting for after boot 8

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (our fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read first: `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
sections P3-3, P3-5, P3-6, P3-7 (how P1b built and booted: TOML
`$W/P1/ssx3.toml`, map `$W/P1/ssx3-functions.csv`, runner sources copied
from `$W/P1/output/`, build dir `/tmp/p1-link/runtime`, boot command with
`PS2X_CD_IMAGE`, CWD `$W/P1/run`). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Boot 8 (`$W/P1/run/boot-p1b-8.log`) is the starting state: all constructor
entries resolved, six IOP modules loaded, then no syscall/VIF/GIF line for
10 minutes, no idle dump, runner at ~10% CPU.

## Rules

- Host lease: `printf 'P1c\n' > /tmp/ssx3-host-lease` when it is absent or
  empty; if it names someone else, wait 5 minutes and re-check. Remove it
  at the end. No `adb`, no device.
- Never add, commit, or push `ps2xRuntime/src/runner/sub_*.cpp`,
  `ps2_recompiled_*.h`, `register_functions.cpp`, logs, or `._*` files.
  Purge `._*` sidecars (`find <dir> -name '._*' -delete`) after every edit.
- Commit each fix as one commit on `ssx3` (one or two files), trailers
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_01H9JEyNpHtANpAU2dB1YuC7`,
  `git push fork ssx3` after each. Diagnostics are env-gated and off by
  default so they can be upstreamed as-is.
- Boots: run the same way as boot 8, foreground, `stdbuf -o0 -e0`, log
  direct to `$W/P1/run/boot-p1c-N.log`, kill after the stated time.
  Never pipe through `head`. No build or log above 200 MB; if a log grows
  past 50 MB, stop the run and cut the diagnostic's verbosity.
- Time box 5 hours. At the box, write the report and stop.

## Step 1 — steady-state diagnostics (one commit, `Diag:` prefix)

Add, all gated on `PS2X_DIAG_PERIOD_MS` (unset = compiled in, nothing
printed, zero cost beyond a counter increment):

a. **Periodic thread dump** in `EeScheduler::run()`: every period print
   the Fix C table for all threads (id, status, waitReason, waitId, pc,
   entry, priority) plus, per thread, how many times it was scheduled
   since the last dump. Reuse Fix C's printing code.
b. **Syscall histogram** in `Kernel/Syscalls/Dispatcher.cpp`: count per
   syscall id, with the first and most recent caller pc (`ctx->pc` or
   the epc the dispatcher has); print the top 20 every period, then
   reset the counts.
c. **HLE stub histogram** at the single place the runtime resolves a
   guest call to a registered host function (find it: it is where the
   `register_functions.cpp` bindings are looked up at call time; record
   the file:line in the report): count per stub name with first/last
   `ra`; print the top 30 every period, then reset.
d. **Fix D receipt**: one `[cd:callback]` line when `queueCdCallback`
   queues an invocation (function id, callback pc) and one when the
   scheduler starts that invocation.

Rebuild (`cmake --build /tmp/p1-link/runtime --target ps2EntryRunner`),
purge sidecars, `shasum -a 256` the binary. Boot 1 (`boot-p1c-1.log`):
`PS2X_DIAG_PERIOD_MS=5000`, 90 seconds. Receipts: the diff, the binary
sha, and from the log the last three period blocks verbatim.

## Step 2 — name the loop (no code change)

From boot 1: table of every thread with its pc at each dump and its
schedule count; the syscall top 20; the stub top 30. For each of the
top 5 guest pcs and stub callers' `ra`, resolve the enclosing function via
`$W/P1/ssx3-functions.csv` and quote the loop body from
`$W/P1/output/sub_XXXXXXXX_*.cpp` (at most 40 lines each, with the
original MIPS in the comments if present). Record what memory word or
kernel object each loop reads/waits on (address, and which HLE stub or
syscall writes it, if any does; say "nothing writes it" when that is
what you find). Table only.

## Step 3 — completion fixes (at most 3 iterations, one boot each)

If Step 2 shows a wait on something an HLE stub is supposed to complete
(examples, not a list to force-fit: a pad state that never becomes
"stable", an `sceMc*` request whose `sceMcSync` never reports done, a SIF
RPC whose completion flag never sets, a CD command whose `sceCdSync`
never returns idle, a semaphore only an interrupt would signal, a
`sceCdCallback` that Fix D queued but never ran), implement the
completion in the corresponding stub in `Kernel/Stubs/` or `Syscalls/`,
matching the SDK's documented return values (state the value you chose
and where it comes from). One commit per fix (`Pad:`/`MC:`/`CD:`/`SIF:`
prefix), rebuild, boot for 3 minutes with the diagnostics on, record the
new ladder line (first syscall id not seen before, first VIF MPG/MSCAL,
first GIF kick, first presented frame, crash) and the new period block.
If the wait is on something no stub owns (a hardware register, a timer,
a DMA channel), record the address and what the runtime does with it,
implement nothing, and stop at Step 4.

## Step 4 — report

Append `## Part 4` to `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
(sections P4-0 lease record, P4-1 diagnostics diff + boot-1 period
blocks, P4-2 loop table with quoted bodies, P4-3 fixes + ladders per
boot, P4-4 binaries and commits, P4-5 exact commands, P4-6 what I could
not do). Commit with `git add -f local/research/P1/REPORT.md`, prefix
`[P1c]`, same trailers. Push the fork. Remove the lease. Stop.
