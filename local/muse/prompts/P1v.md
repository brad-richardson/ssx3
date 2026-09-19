# P1v — SSX 3 on PS2Recomp, Part 23: FIX — zero-max CreateSema parity (second behavior fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 22 first (P22-1a rule, P22-1b/1c the F2 zero-param call, P22-2b the
exact census, P22-5 thread-3 starvation). `W=/Volumes/Extreme
SSD/ps2recomp-spike`. Rules exactly as `local/muse/prompts/P1c.md` "Rules"
(lease `P1v`, no adb, never commit generated runner sources or `._*`,
purge sidecars, one commit per change with the two trailers, boots
foreground ≤90 s, logs `$W/P1/run/boot-p1v-N.log`,
`PS2X_DIAG_PERIOD_MS=5000`), plus: builds may run any time (`-j4`); boots
only while holding the host lease — if `/tmp/ssx3-host-lease` names
another agent, poll every 5 minutes and log waits to
`$W/P1/run/p1v-waits.log`. Push rule: `git push` ONLY inside this fork
clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1u attributed the 1.39M `WaitSema(-1)` spin: F2 stores the unchecked
return of a zero-param `CreateSema` (init 0, max 0), which the host
rejects (`maxCount<=0` → `KE_ERROR`); the game expects success (no
caller checks for `-1` anywhere in the F-table). Thread 3 (the F2
flag-clearer, prio 101) is starved by thread 1's no-block spin (prio
100). This brief IS the fix — the second behavior change. Ground rule:
match REAL PS2 behavior, not the game's wish — check what a PS2 BIOS
does with max_count=0 first (PCSX2 source on the SSD reference clones
or pcsx2 source you can read — read-only, cite file:line; if sources
disagree or are silent, say so and pick the minimal rule the game
needs, recorded as provisional).

## Step 1 — the fix (one `Fix:` commit, build any time)

Minimal rule that makes zero-max `CreateSema` return a usable id
(likely: clamp/accept max 0 as 1, or bypass validation for the
zero-struct case — decide from the Step-0 evidence, record the
alternatives rejected). Keep it reviewable (<40 lines non-test);
BEFORE/AFTER receipts: zero-param create returns id (not -1), valid
creates unchanged, `ps2xTest` (424/425 baseline — the 1 pre-existing
failure stands; no NEW failures), rebuild green.

## Step 2 — one boot (lease-poll; `PS2X_DIAG_SEMA=1` + create-trace on)

Boot 1 (≤90 s foreground, log `$W/P1/run/boot-p1v-1.log`), p1u env.
Receipts: zero-param F2 creates now return ids (count + the two
pcs), `op=wait id=-1` count (expect 0 — else the residue), thread-3
scheduled≠0 + flag clears observed (or the new stall tabled), the new
thread-1 park (record it fully — the ladder moved again), plus the
standard ladder row. Second boot only if the fix fires but the chain
stalls at a NEW point worth one receipt.

## Step 3 — report

Append `## Part 23` (P23-0 lease record, P23-1 evidence + fix diff +
choice + tests, P23-2 boot + chain answer, P23-3 binaries and commits,
P23-4 exact commands, P23-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1v]`, trailers; push `fork ssx3`
from the fork clone only; remove the lease if held; stop.
