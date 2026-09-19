# P1r — SSX 3 on PS2Recomp, Part 19: the CD-completion→W1 gap (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 18 first (P18-1f sites #7/#9/#10, P18-1g the traced chain broken at
the CD→W1 link, P18-2a :411–:416, P18-5 the poll-vs-lost-wake residue),
plus Part 17 §P17-1 (sema-26 context: out of scope here, do not chase
it). `W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1r`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1r-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1r-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1q traced entry-0's completion chain statically and broke it at one
link: the recycled slot's CD read (`sceCdRead lbn=0x5f1a3
ret=0x3e3b8c`) fires its callback (`0x3e3ad8` queued+started), but W1
site #9 (`0x3e3d64` in CD worker `3E3B00`) is never reached and current
stays set. Residue: poll-vs-lost-wake undetermined. Known addresses:
CD state `0x519C40` (`&~2` writeback @ `0x3e3d68`), async flag
`*(0x519C20)`, counters `0x450C40`/`0x450C4C`, worker `0x3e33b0` (no
`jal` caller tree-wide). Fork HEAD `e73e36a`, binary `7a7d4b64` fresh
(rebuild only if stale). Out of scope: sema-26 non-delivery, entry-0
selection (answered), any behavior fix.

## Step 1 — static: the worker's road to W1 (no lease, no boot)

a. **Worker path.** From the callback (`0x3e3ad8`) to site #9
   (`0x3e3d64`): every predicate, flag test, and counter compare in
   `3E3B00` between "transfer done" and the W1 `jal`. One row per
   gate: pc, condition, pass/fail effect.
b. **Poll registration.** Who calls the `0x3e33b0` poll (site #7's
   host) — pointer/table search for its registration (P18-1f residue);
   same for `3E3B00`'s own trigger. If unfindable statically, that IS
   a dynamic target for Step 2, not a failure.
c. **Lost-wake candidates.** Which flag/counter in (a) could already
   hold its "done" value before the waiter arms (the classic lost-wake
   shape)? Name each with its writer pc + timing relative to the
   callback lines.

## Step 2 — dynamic receipt (≤2 boots, designed from Step 1)

Minimal watch set over the Step-1 gates (state `0x519C40`, async flag
`0x519C20`, counters, + worker-progress pcs if observable): does the
worker advance to site #9 and stall ON a gate (poll — name the gate +
its held value), or never advance at all (lost wake / untriggered —
name the last observed progress point)? One boot if it closes; two
only if the first re-scopes.

## Step 3 — report

Append `## Part 19` (P19-0 lease record, P19-1 worker path + gates,
P19-2 dynamic answer, P19-3 binaries and commits, P19-4 exact
commands, P19-5 what I could not do) to `local/research/P1/REPORT.md`
in `/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1r]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push — verify up-to-date); remove the lease if held; stop.
