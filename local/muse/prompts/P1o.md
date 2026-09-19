# P1o — SSX 3 on PS2Recomp, Part 16: true-frame watch confirm + driver-flag writer hunt (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 15 first (P15-2b true frames, the P13-3 hex slip, P15-2c resume
path), plus Part 12 §P12-1 (driver flag `*(entry+8)`, `$s1` =
`*(0x519AD8)`+byte·`0x30`, P6 lead `0x3de420
iFILESYS_CommandCompleteCallback`). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Rules exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1o`, no
adb, never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1o-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1o-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule (P1n lesson):
machine-check EVERY hand hex computation with python3 and paste the
check line — no unaudited hex arithmetic anywhere. Time box 4 hours.

## Facts you start from

P1n named the fresh caller (`0x3ded80`, #6, entry sp `0x1fffe80`) and
the true driver frame (`0x1fffe00`/`0x1fffe10`); the 3-brief miss was a
hex slip in P13-3 (`0x1fffd80+0x80` written as `0x1ffe000`). The other
4037 enters are scheduler resumes that skip the prologue (no frame
writes). Fork HEAD `e73e36a` (probe committed, pushed), binary
`7a7d4b64` fresh. The driver's SYNCTASK wait is on `*(entry+8)` with an
unknown writer. Out of scope: sema-26 non-delivery, any behavior fix.

## Step 1 — true-frame watch confirm (one boot ≤90 s)

Boot 1, p1n env with WATCH swapped to the TRUE frame: `0x1fffe00` (w4,
`sw` at `0x3dd1e0`) + `0x1fffe10` (w8, `sd` at `0x3dd214`), keeping the
driver probe on. Expectation (machine-checked): exactly 1 hit each, both
`pc=0x3dd1e0`/`0x3dd214`, sp `0x1fffe00`. Receipts: the hit lines (or
the miss, with the new residue tabled), probe line (expect the same
single line), plus the standard ladder row. If the hits land, the
caller saga is CLOSED — say so and move to Step 2 in the same boot's
data where possible.

## Step 2 — driver-flag writer hunt (closed logs + sources first)

a. **Static.** Who writes `*(entry+8)`? Enumerate writers to the slot
   array (`0x51ED98`+8·slot… — recompute and machine-check) and to
   `0x519AD8` (the `$s1` base) in `$O/*.cpp` + ELF: store pcs, owning
   functions, P6 names if any. Check the P6 lead `0x3de420
   iFILESYS_CommandCompleteCallback` (exists? called? near the flag?).
b. **Dynamic (only if static fails).** Design ONE receipt for a second
   boot (≤90 s): the minimal watch set that catches the flag writer
   (slot addrs + `0x519AD8` region). If Step 1's boot already carries
   the needed watches, no second boot — say so.
c. Either way: table the writer (or the narrowed residue + the exact
   next receipt).

## Step 3 — report

Append `## Part 16` (P16-0 lease record, P16-1 watch confirm, P16-2
flag-writer hunt, P16-3 binaries and commits, P16-4 exact commands,
P16-5 what I could not do) to `local/research/P1/REPORT.md` in
`/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1o]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push — verify up-to-date); remove the lease if held; stop.
