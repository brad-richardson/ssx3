# P1f — SSX 3 on PS2Recomp, Part 7: who writes 0 into the main thread's return-address slot

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
sections P6-1, P6-2, P6-4 (the return to 0), P6-3 (semaphore 26),
P5-6/P6-6 (commands; current CSV `$W/P1/ssx3-functions.sweep.csv`,
runner sources already refreshed from it; normal build dir
`/tmp/p1-link`, strict `/tmp/p1-link-strict`). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Rules exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1f`, no
adb, never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, push `fork ssx3`, boots
foreground 3 min, logs `$W/P1/run/boot-p1f-N.log`,
`PS2X_DIAG_PERIOD_MS=5000`). Time box 4 hours.

## Facts you start from

Thread 1 (main) dies at `0x3dcc7c` (`sub_003DCBD8` epilogue) because
`ld $ra,0($sp)` with `sp=0x1ffff60` reads 0. The generated code for the
prologue's `sd $ra,0($sp)` (delay slot of the `beqz` at `0x3dcc04`) is
correct: the store executes on both branch outcomes (orchestrator read
`output/sub_003DCBD8_0x3dcbd8.cpp` lines 116–144). So either the slot
was written with 0 by the prologue itself (ra was 0 on entry), or
something wrote 0 over it later, or `sp` at the epilogue differs from
`sp` at the prologue. Candidates for a later write: thread 2's stack
(`Thread.cpp:203–276`: how `stack`/`stack_size` from the SDK
`ee_thread_t` become the initial sp), the invocation stacks
(`EeScheduler::invocationStackTop()` → `reserveAsyncCallbackStack(0x4000)`:
record where that reserves from), the INTC/alarm handler contexts
(`EeScheduler.cpp:1468` uses a stored `handler.sp`; the periodic returns
in boot-p1e-1 from `0x3e4e8c` all show `sp=0x1ffff20`), or the CD
callback stack (`sceCdInitEeCB stack=0x51a480 size=0x800`).

## Step 1 — watchpoint and stack map (one commit `Diag:`, one build, one boot)

a. Env `PS2X_DIAG_WATCH=0x1ffff60` (comma list of 8-byte-aligned
   addresses): every guest memory write of any width (8/16/32/64/128
   bit — find the write helpers the generated code uses, `WRITE8`…
   `WRITE128`, and the runtime-side writers `writeGuestU32` etc.; the
   check may live in a slow path behind one global bool) that overlaps a
   watched 8-byte window prints `[diag:watch] addr=… width=… value=…
   pc=… thread=… ra=… sp=…`. Cost does not matter.
b. `[diag:stacks]` at every periodic dump: for every guest thread its
   `stack`, `stackSize`, current sp; every invocation stack top reserved
   so far (with its key); `g_cdCallbackStackTop`; every stored INTC/DMAC
   `handler.sp`; the alarm invocation's sp.
c. One line at `StartThread` printing the parsed `ee_thread_t` fields
   (func, stack, stack_size, gp, priority, attr) and the initial sp the
   runtime assigns.
Rebuild `/tmp/p1-link`, boot 1 with the three env vars. Receipts: diff,
binary sha, every `[diag:watch]` line (there should be few), the
`[diag:stacks]` block nearest the thread-1 Dormant line, the StartThread
line.

## Step 2 — name the writer (no build)

Table: each write to `0x1ffff60`, in order: value, width, pc → CSV row
→ what instruction (ELF word), thread or invocation, sp/ra at the time.
State which write left the 0 that the epilogue read and what that code
was doing (a thread-2 prologue, an invocation prologue, a `sq` of a
frame, a memset/clear loop, or the prologue of `sub_003DCBD8` itself
with ra 0 — in the last case also table the caller chain that entered
`sub_003DCBD8` and why ra was 0 there).

## Step 3 — one fix, one boot

- Thread-2 stack overlaps thread 1's: fix the `ee_thread_t` stack
  handling in `Thread.cpp` per the SDK (`stack` is the base address,
  initial sp = `stack + stack_size` aligned down to 16, minus the SDK's
  reserved area if the runtime already models one; state the value).
- Invocation stack overlaps a live thread stack: move
  `reserveAsyncCallbackStack` to a region no guest thread uses (record
  the region chosen and why it is free: e.g. inside the runtime's own
  reserved guest RAM, not below the ELF's stack top), or make the alarm/
  INTC invocation use its own reserved top instead of a stored sp.
- Any other writer: record it; implement a fix only if the runtime owns
  the code (`Kernel/`, `Syscalls/`, scheduler); a recompiler-side cause
  (`ps2xRecomp/`) is recorded with the exact instruction and generated
  code and left unfixed.
Commit (`Kernel:`/`Scheduler:` prefix), rebuild, boot 2, ladder (thread
table at last dump, first new syscall id, first VIF MPG/MSCAL, first GIF
kick, first presented frame, crash, missing targets). If thread 1 now
runs past the point but parks elsewhere, one more diagnostic boot to
record the new park (thread table + dispatch history), no further fix.

## Step 4 — report

Append `## Part 7` (P7-0 lease, P7-1 diag diff + watch/stacks/StartThread
lines, P7-2 writer table, P7-3 fix + ladder, P7-4 binaries and commits,
P7-5 exact commands, P7-6 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1f]`, trailers; push the fork;
remove the lease; stop.
