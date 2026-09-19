# P1l — SSX 3 on PS2Recomp, Part 13: split 0x395cf0 + siblings, re-boot the ladder (fix brief)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 12 first (P12-2 missing-target analysis + sibling table, P12-1 park
+ driver + 8-caller table), plus Part 5 for the regenerate/rebuild
receipts. `W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1l`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1l-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1l-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3` (the orchestrator owns that origin).
Time box 4 hours.

## Facts you start from

Boot-p1k-1 (binary `e5f81397`, fork `8fad69e`): thread 1 parked in
`SYNCTASK_run` (`0x3e5980` 15/17), one missing target JALR
`0x3760d0→0x395cf0` (byte-identical to p1j). `0x395cf0` is an unsplit
frameless leaf (`lui $v0,0x50` at target, `jr $ra` + `nop` immediately
before at `0x395ce4/0x395cec`) with three unsplit siblings (`0x395c38`,
`0x395c68`, `0x395d28` — no split file, no reg line, verified 09-19).
`0x395c70` already HAS a split file + reg line: do NOT re-split it,
verify and move on. The P1k `sd`-path watch missed the outer-caller
receipt (`0x3dd214` `sd` never fired in 32,077 watch lines); the
documented next receipt is a w4-watch on `0x1ffe000` (`sw` at
`0x3dd1e0`, same frame). Out of scope: the `*(entry+8)` driver-flag
writer, sema-26 non-delivery, any SYNCTASK park fix — splits + ladder
only.

## Step 1 — splits (no lease, map CSV only)

Add `0x395cf0`, `0x395c38`, `0x395c68`, `0x395d28` to the function-map
CSV per the Part 5 receipts; confirm `0x395c70` needs no row. Receipts:
CSV row count before/after (expect 9,270 → 9,274), the 4 new rows, the
`0x395c70` pre-existing row. No source change, no fork commit for the
CSV (it is untracked — same as P1d).

## Step 2 — regenerate + rebuild + tests (no lease)

Re-run the analyzer/recomp per Part 5; rebuild `/tmp/p1-link`.
Receipts: recompile counts (expect 9092→9096 functions or the exact
new totals, 0 decode failures, 0 unhandled), new split files +
registration lines for all 4 addrs, `ps2xTest` result (P1j baseline:
424/425 with 1 failure proven pre-existing by stash A/B — re-prove it
the same way if it fails, do not fix it here).

## Step 3 — one boot (lease-poll; env = p1k env + w4 0x1ffe000)

Boot 1 (≤90 s foreground, log `$W/P1/run/boot-p1l-1.log`), same env as
boot-p1k-1 plus `0x1ffe000` appended to `PS2X_DIAG_WATCH`. Receipts:
binary sha, missing-target lines (expect zero; else table each),
thread-1 census (park pc + split), threads 2/4/5 states, first new
syscall ids, first VIF MPG/MSCAL, first GIF kick, first presented
frame, crash, `0x1ffe000` watch lines (`pc=0x3dd1e0` = outer caller
caught — name it from the 8-candidate table; zero lines = receipt
missed again, say so). If thread 1 advances to a new park, record it
(thread table + last dispatch lines) and stop — no further fix.

## Step 4 — report

Append `## Part 13` (P13-0 lease record, P13-1 splits + regen audit,
P13-2 boot ladder delta vs boot-p1k-1, P13-3 outer-caller receipt,
P13-4 binaries and commits, P13-5 exact commands, P13-6 what I could
not do) to `local/research/P1/REPORT.md` in
`/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1l]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push — CSV untracked, no source change; verify up-to-date);
remove the lease if held; stop.
