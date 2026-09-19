# P1g — SSX 3 on PS2Recomp, Part 8: diagnose the post-fix park at 0x391330 (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 7 first (P1f's fix + boot-2 ladder). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Rules exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1g`, no
adb, never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground, logs
`$W/P1/run/boot-p1g-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: M5 owns
the host-lease priority — if `/tmp/ssx3-host-lease` names another
agent, poll every 5 minutes, log waits to `$W/P1/run/p1g-waits.log`,
and never hold the lease longer than one short boot. Push the `fork`
remote only; never push the ssx3 origin. Time box 2 hours.

## Facts you start from

Boot 2 (`boot-p1f-2.log`, fixed binary `f4d16b98`) verified the P1f
fix: 165 watch lines, 0 from the handler, thread 1 runs past the old
death point and is `Running` at `pc=0x391330` (in
`sub_003912A8,[0x3912a8,0x391360)`) with `scheduled` advancing
302→304→306 across the last blocks but pc stable. Threads 3 and 4
exist only after the fix. No VIF MPG/MSCAL, no GIF kick, no presented
frame, no crash. The pc-stable-but-scheduled pattern may be a spin
loop or a short wait loop, not forward progress.

## Step 1 — diagnose the park from the closed log + ELF (no lease, no boot)

a. ELF words around `0x391330` (`SLUS_207.72`, file offset
   `0x1000+(va-0x100000)`, mipsel): disassemble the enclosing basic
   block and its branch targets by hand from the opcode table (no
   disassembler install; `mipsel-linux-gnu-objdump` only if already
   present). Table each instruction: va, word, mnemonic, what it does.
b. Function bounds for `sub_003912A8` from `$W/P1/ssx3-functions.sweep.csv`
   + callers of it (who jumps/calls into `[0x3912a8,0x391360)`).
c. From `boot-p1f-2.log` (closed log only): the last 30 dispatch lines
   before the end (is `0x391330` a tight loop or one stop among many?),
   the last block's full thread table with statuses, the last new
   syscall ids, the last CD/VIF/GIF activity. Table: what thread 1 is
   waiting on (sema id? vsync? CD callback? VIF? none visible?).
d. State the wait object or the next missing rung, with the exact
   lines/words that prove it. If the closed log cannot answer, say
   which single receipt is missing and go to Step 2; otherwise skip it.

## Step 2 — one short boot only if Step 1 cannot answer (lease-poll, ≤90 s)

One boot with the current `/tmp/p1-link` binary (no rebuild unless the
binary is stale — state its sha), same env as boot 2, foreground max
90 s, log `$W/P1/run/boot-p1g-1.log`. Release the lease immediately
after. Receipts: the missing Step-1 receipt only, plus the standard
ladder row (thread table, first new syscall ids, VIF/GIF/frame/crash).

## Step 3 — report

Append `## Part 8` (P8-0 lease record, P8-1 park diagnosis: disasm
table + wait object, P8-2 ladder delta vs boot 2, P8-3 binaries and
commits, P8-4 exact commands, P8-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1g]`, trailers; push `fork ssx3`
only; remove the lease if held; stop. No runtime fix in this brief.
