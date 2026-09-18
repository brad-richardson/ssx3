# P1d — SSX 3 on PS2Recomp, Part 5: the code-pointer sweep, and why main returned to 0

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (our fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read first: `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
sections P3-4 (how splits are made), P4-3 (the two P1c splits and the
boot-3 end state), P4-5 (commands). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Starting state = boot-p1c-3: no missing targets, WaitSema balanced,
thread 2 (entry 0x3e3be0, priority 12) created and started but never
scheduled, 20 `sceCdRead` + `sceCdInitEeCB`, 1,135 comparator calls, then
both threads Dormant with pc 0 through `makeDormant` (no exit syscall).

Rules: as P1c (`local/muse/prompts/P1c.md` "Rules" section): host lease
`P1d`, no adb, never add/commit/push generated runner sources or `._*`
files, purge sidecars after every edit, one commit per fix with the two
trailers, push `fork ssx3` after each, boots foreground with
`stdbuf -o0 -e0` direct to `$W/P1/run/boot-p1d-N.log`, 3 minutes each,
`PS2X_DIAG_PERIOD_MS=5000`. Time box 5 hours.

## Step 1 — thread entry (fact check, no build)

`Kernel/Syscalls/Thread.cpp:269` refuses an entry the runtime has no
function for. Is 0x3e3be0 a map start in `$W/P1/ssx3-functions.csv`?
Quote the ELF words at 0x3e3bd8–0x3e3be8 and the row that contains it.
Table row: address · map row · prologue evidence · verdict-free note.

## Step 2 — code-pointer sweep (one script, one recompile, one boot)

Write `$W/P1/tools/codeptr_sweep.py` (commit it under
`docs/research/`? no: keep it in `$W/P1/tools/`, quote it in the report).
Inputs: the ELF `$W/P1/cd/SLUS_207.72`, the CSV. It collects every
candidate code address T in .text from (a) every 32-bit aligned word in
every loaded segment whose value lies in [text_start, text_end) and is
word-aligned, (b) every `lui rX, hi` followed within 4 instructions by
`addiu rX, rX, lo` or `ori rX, rX, lo` whose composed value lies in
.text, (c) the a1/handler arguments already seen: 0x3e3588 (SetAlarm),
0x3e3968 (comparator), 0x3e3be0 (thread entry), the 39 constructors
(as a self-check: the script must find all of them). A candidate becomes
a split when T is not already a map start AND at least one of: the
instruction at T is `addiu $sp,$sp,-N`; the instruction at T-8 is
`jr $ra` (0x03e00008) or at T-4 is `jr $ra`; the instruction at T-4 is
`j`/`jr` and T-8 is not a branch. Everything else is listed but not
split. Output: a new CSV (`ssx3-functions.sweep.csv`), and a table of
counts: candidates by source (a/b/c), already-mapped, split, rejected
(with the top 20 rejected by frequency and their instruction words).
Sanity rules: never split inside a function whose generated source
shows the address as an internal branch target (grep the
`output/sub_*.cpp` for `case 0x<T>` / `L_<T>` labels; list any such
collisions instead of splitting them). Recompile in map mode with the
sweep CSV (expect stubs 176, 0 decode failures, 0 unhandled; record the
row counts), refresh runner sources, rebuild, boot 1 (`boot-p1d-1.log`).
Receipts: script, count table, recompile summary, binary sha, ladder
(first new syscall id, thread table at the last dump, first VIF
MPG/MSCAL, first GIF kick, first presented frame, crash, missing
targets).

## Step 3 — strict return diagnostics (one build, one boot)

Configure a second build dir `/tmp/p1-link-strict` with
`-DPS2X_STRICT_RETURN_DIAGNOSTICS=ON` (see `ps2xRuntime/CMakeLists.txt:16`
and where the define is consumed) plus the same options as P1b's build,
same runner sources as boot 1. Boot 2 (`boot-p1d-2.log`). Receipt: the
first diagnostic that reports a return to 0 (or any bad return): the
function, its pc, ra, sp and the last 5 stub/call lines before it. Then
resolve that function in the CSV and quote up to 40 lines of its
generated body around the return. If no diagnostic fires and the threads
still go Dormant, add a one-line log in `EeScheduler::makeDormant`
callers at lines ~396 and ~432 printing the thread id, the previous pc,
ra and the invocation-stack depth (env-gated on `PS2X_DIAG_PERIOD_MS`,
commit as `Diag:`), rebuild the normal dir, boot 3.

## Step 4 — CD payload check (one log line, no separate boot needed)

In `sceCdRead`'s entry log (`Kernel/Stubs/CD.cpp`, P1c's `[diag:cd]`
line) also print, after the read is served, the first 8 bytes of the
destination buffer in hex. Fold this into whichever boot comes next
(step 3's boot if not yet run, else one more boot). Receipt: the line
for LBN 0x10 (an ISO9660 PVD begins `01 43 44 30 30 31`) and for the
first directory sector.

## Step 5 — report

Append `## Part 5` (P5-0 lease, P5-1 thread-entry table, P5-2 sweep
script + count table + recompile + boot-1 ladder, P5-3 strict-return
receipt + quoted body, P5-4 CD payload lines, P5-5 binaries and commits,
P5-6 exact commands, P5-7 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`,
commit with `git add -f`, prefix `[P1d]`, trailers. Push the fork.
Remove the lease. Stop.
