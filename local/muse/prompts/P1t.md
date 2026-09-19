# P1t — SSX 3 on PS2Recomp, Part 21: FIX — dispatch mid-label callback invocations (first behavior fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 20 first (P20-1b invocation context + table rule, P20-2a–2b the
silent-drop receipts, P20-5 the diagnosed-untouched note). `W=/Volumes/Extreme
SSD/ps2recomp-spike`. Rules exactly as `local/muse/prompts/P1c.md` "Rules"
(lease `P1t`, no adb, never commit generated runner sources or `._*`,
purge sidecars, one commit per change with the two trailers, boots
foreground ≤90 s, logs `$W/P1/run/boot-p1t-N.log`,
`PS2X_DIAG_PERIOD_MS=5000`), plus: builds may run any time (`-j4`); boots
only while holding the host lease — if `/tmp/ssx3-host-lease` names
another agent, poll every 5 minutes and log waits to
`$W/P1/run/p1t-waits.log`. Push rule: `git push` ONLY inside this fork
clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1s proved sema-26 "non-delivery" is non-dispatch: the CD callback
invocation (`pc=0x3e3ad8`, mid-`sub_003E39A8`) is attached, then dropped
silently (`hasFunction` false → pc zeroed → popped, `Sched:506-512`),
so its `iSignalSema` body never runs and the worker never wakes. The
signal path itself is intact in both contexts. This brief IS the fix —
the first behavior change on the critical path. Keep it minimal: the
smallest rule that dispatches mid-label invocations WITHOUT changing
any other dispatch behavior (exact-entry hits, miss diagnostics, and
the empty-invocations path must all behave exactly as before — prove
each with a before/after receipt).

## Step 1 — the fix (one `Fix:` commit, build any time)

Implement ONE of these (pick the smallest that the code admits; record
why the others were not chosen):
(a) register `0x3e3ad8` as an exact table entry pointing at the
containing function with an entry offset; (b) a mid-label invocation
rule: when `hasFunction(pc)` is false but pc falls inside a registered
range, dispatch at pc (not at the range start); (c) whatever smaller
shape the scheduler code admits. Env-gate NOT required (this is a real
fix), but keep the diff reviewable (<60 lines non-test). Receipts: the
diff, `ps2xTest` (424/425 baseline — the 1 pre-existing failure stands;
no NEW failures), rebuild green.

## Step 2 — one boot (lease-poll; `PS2X_DIAG_SEMA=1` + probe on)

Boot 1 (≤90 s foreground, log `$W/P1/run/boot-p1t-1.log`), p1s env.
Receipts: `ra=0x3e3af0` signal line(s) (the callback body RAN — count
them), thread-2 wake after the callback (scheduled≠0 past the epoch),
site #9 / G6 progress (reached or new residue), entry-0 flag value at
park (set or still 0 — if the chain now completes, record the new
thread-1 park instead of the old one), plus the standard ladder row.
Second boot only if the first shows the fix firing but the chain
stalling at a NEW point worth one receipt.

## Step 3 — report

Append `## Part 21` (P21-0 lease record, P21-1 fix diff + choice +
tests, P21-2 boot + chain answer, P21-3 binaries and commits, P21-4
exact commands, P21-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1t]`, trailers; push `fork ssx3`
from the fork clone only; remove the lease if held; stop.
