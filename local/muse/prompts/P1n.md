# P1n — SSX 3 on PS2Recomp, Part 15: driver-entry probe — name the live caller (diag + boot)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 14 first (P14-1d designed receipt, P14-1b dispatch note, P14-5
fresh-vs-resume gap). `W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules
exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1n`, no adb,
never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1n-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1n-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Time box 4 hours.

## Facts you start from

P1m proved frame-elsewhere: driver `sub_003DD1D8` stores take
fires-paths, yet 0 watch hits, because its frames are not at the
watched addrs (7 of 8 direct-jal candidates never entered in 72.3M
trace lines; the 8th wrote elsewhere; the live invocation is a depth-0
checkpointed dispatch with no guest parent). Driver entered 3940× over
90 s (~44/s). Fork HEAD `8fad69e`, binary `0b38f7b6` fresh. Out of
scope: the `*(entry+8)` driver-flag writer, sema-26 non-delivery, any
behavior fix — probe + caller only.

## Step 1 — driver-entry probe (one `Diag:` commit, build any time)

Implement exactly P14-1d: env-gated (e.g. `PS2X_DIAG_DRIVER_PROBE=1`,
default off) log line `[diag:driver-entry] sp ra sourcePc
checkpointed` in `dispatchGuestBranch` for `targetPc==0x3dd1d8`, on
BOTH the checkpoint path (before `return false`) and the call path
(before `targetFn`). `sp`/`ra` = guest regs at dispatch; `sourcePc`
= calling pc; `checkpointed` = which path. Receipts: the diff (one
commit, two trailers, push `fork ssx3`), rebuild, `ps2xTest` result
(P1l baseline 424/425 same single pre-existing failure — re-confirm,
do not fix).

## Step 2 — one boot (lease-poll; probe on)

Boot 1 (≤90 s foreground, log `$W/P1/run/boot-p1n-1.log`), p1l env +
probe var (keep the `0x1ffe000`/`0x1ffe010` watches: a hit on the true
frame would confirm the probe). Receipts: binary sha, probe-line count
(~3940 expected) + table (distinct `sp` values with counts, distinct
`ra` values with counts, checkpointed split, sourcePc values), the
live caller NAMED (or narrowed with the exact residue), true driver
frames vs watched addrs, plus the standard ladder row (thread census,
threads 2/4/5, syscalls, VIF/GIF/frame, missing targets).

## Step 3 — report

Append `## Part 15` (P15-0 lease record, P15-1 probe diff + build +
tests, P15-2 boot + caller answer, P15-3 binaries and commits, P15-4
exact commands, P15-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1n]`, trailers; push `fork ssx3`
from the fork clone only; remove the lease if held; stop.
