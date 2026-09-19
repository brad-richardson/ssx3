# P1u — SSX 3 on PS2Recomp, Part 22: the WaitSema(-1) stall — attribute the slot (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 21 first (P21-2c the `-1` spin shape + call sites, P21-2f census,
P21-5 the unattributed-slot residue), plus Part 20 §P20-1 (sema
signal/wait paths, for the id-validation read). `W=/Volumes/Extreme
SSD/ps2recomp-spike`. Rules exactly as `local/muse/prompts/P1c.md` "Rules"
(lease `P1u`, no adb, never commit generated runner sources or `._*`,
purge sidecars, one commit per change with the two trailers, boots
foreground ≤90 s, logs `$W/P1/run/boot-p1u-N.log`,
`PS2X_DIAG_PERIOD_MS=5000`), plus: builds may run any time (`-j4`); boots
only while holding the host lease — if `/tmp/ssx3-host-lease` names
another agent, poll every 5 minutes and log waits to
`$W/P1/run/p1u-waits.log`. Push rule: `git push` ONLY inside this fork
clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1t's fix moved the boot: thread 1 now spins `WaitSema(-1)` 1.39M times
(`KE_UNKNOWN_SEMID`, never blocks) from `jal WaitSema` @ `0x31aa84`
(`$a0`=`*($s0+0x18)`=`-1`, thread 1, `sub_0031A6B8`), with 24 sibling
`SignalSema(-1)` from `jal` @ `0x31aadc` (`$a0`=`*($a0+0x18)`, thread 4,
same function). The slot reads `-1` constantly; nothing wrote it this
boot. Open: CreateSema failure return? uninitialized slot? deleted sema?
stale object? Fork HEAD `58c9144`. Diagnose only — no behavior fix (a
`Diag:` logging commit is allowed if the receipt needs it, nothing else).

## Step 1 — static: the slot + its writers (no lease, no boot)

a. **The struct.** What object holds the `+0x18` sema-id slot (`$s0` at
   `0x31aa84`, `$a0` at `0x31aadc`)? Constructor/init sites, field
   layout around `+0x18` (id? state? chain?), and every writer to the
   slot (CreateSema stores, init memsets, DeleteSema clears, `-1`
   sentinels). ELF-decode every offset you cite.
b. **The `-1` source.** Which writer can store `-1`: a CreateSema
   failure return propagated? an init path that never ran (which
   one — callers + reachability in this boot)? a delete-then-reuse?
   One row per candidate with its for/against evidence.
c. **The loop's intent.** What does `sub_0031A6B8` do around the spin
   (the `0x31a9d8`/`0x31aa18` cluster + PollSema `0x45` sibling)? Is the
   `-1` a guest bug exposed by progress, or a host-side init the game
   expects (which one)?

## Step 2 — dynamic receipt (≤2 boots, designed from Step 1)

Minimal set that attributes the slot: the slot's absolute addr(s) (from
`$s0`/`$a0` values — design how to learn them: trace sample? targeted
watch on candidate addrs? one `Diag:` line?) watched across the boot —
who writes `-1` (or proves nobody does, dating it to init), plus the
first `-1` wait's position relative to boot phase. One boot if it
closes; two only if the first re-scopes.

## Step 3 — report

Append `## Part 22` (P22-0 lease record, P22-1 slot + writers + loop
intent, P22-2 dynamic answer, P22-3 binaries and commits, P22-4 exact
commands, P22-5 what I could not do) to `local/research/P1/REPORT.md`
in `/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1u]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push unless Step 2 needed the `Diag:` commit —
verify); remove the lease if held; stop.
