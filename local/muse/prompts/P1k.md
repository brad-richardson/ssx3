# P1k — SSX 3 on PS2Recomp, Part 12: diagnose the 0x3e5980 dispatch-loop park + missing target (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 11 first (P11-2 new park + driver + missing target). If
`/Users/bradrichardson/dev/ssx3/local/research/P6/ssx3-decomp-names.csv`
exists by the time you read, use it for function names (cite addr→name
rows); if not, use sweep `sub_*` labels. `W=/Volumes/Extreme
SSD/ps2recomp-spike`. Rules exactly as `local/muse/prompts/P1c.md`
"Rules" (lease `P1k`, no adb, never commit generated runner sources or
`._*`, purge sidecars, one commit per change with the two trailers,
boots foreground ≤90 s, logs `$W/P1/run/boot-p1k-N.log`,
`PS2X_DIAG_PERIOD_MS=5000`), plus: lease protocol (check absent,
`printf`, release immediately; if foreign, poll every 5 min, log
waits to `$W/P1/run/p1k-waits.log`). Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Time box 3 hours.

## Facts you start from

Boot-p1j-1 (`43aba129`→`e5f81397`): thread 1 past the CSR park, now in
`sub_003E5928` (`0x3e5928-0x3e5a78`), a 16-slot dispatch loop (`$s1`
from `0xF`, park pc `0x3e5980` 31/35 blocks), mid driver
`sub_003DD1D8` (`0x3dd278`: `jal 0x3e5440`, `jal 0x3e5928`), outer
caller unidentified. One new missing target: JALR `0x3760d0→0x395cf0`.
First `[cd:callback]` queued+start (`cb=0x3e3ad8`). New thread 5
(WaitSema 30). New syscalls `0x15`/`0x17`. No VIF/GIF/frame/crash.

## Step 1 — diagnose from the closed log + ELF + sources (no lease, no boot)

a. **The dispatch loop's wait.** The 16 slots at `$s0`: empty or
   filled (what values — table a sample)? What code fills them, and
   has it run (log/caller evidence)? Table the loop's exit condition
   and exactly why it never holds. ELF-decode any block you cite.
b. **The outer caller.** Name the spinning caller of `sub_003DD1D8`:
   RA/stack receipts in the log, back-edge search over `jal
   func_3DD1D8` sites, P6 names if available. One row: caller,
   evidence, what IT waits on (one level only).
c. **Missing target `0x395cf0`.** Which function contains it (sweep
   CSV + P6 name)? Why no slot (unsplit prologue? data-only code
   pointer? the JALR at `0x3760d0` — which function, what does it
   load)? One-line fix class (split/literal/sweep-gap/other). Also
   table the other new stubs (`0x31ad20`, `0x3825f8`, `0x3e33b0`,
   `0x3e5440`, `0x3e5928`, `0x411c38`): called-from, returns-or-parks.
d. **First CD callback.** What queued it (which read completed)?
   Start line present — completion/finish line? Any bearing on the
   parked threads 2 (sema 26), 4 (sema 29), 5 (sema 30)?
e. **Syscalls `0x15`/`0x17`.** Names from `Dispatcher.cpp`, purpose,
   callers (`0x423af8`/`0x423b18` — which stubs?), return values.
State the wait object / next fix class per item. If the closed log +
sources cannot answer an item, name the single missing receipt and go
to Step 2 for that item only; otherwise skip Step 2 entirely.

## Step 2 — one short boot only for missing receipts (≤90 s)

Current `/tmp/p1-link` binary (state sha; rebuild first only if stale),
same env as boot-p1j-1, foreground max 90 s, log
`$W/P1/run/boot-p1k-1.log`. Release the lease immediately after.
Receipts: the missing items only, plus the standard ladder row.

## Step 3 — report

Append `## Part 12` (P12-0 lease record, P12-1 park + driver + caller,
P12-2 missing-target analysis, P12-3 CD + syscall deltas, P12-4 ladder
delta vs boot-p1j-1, P12-5 binaries and commits, P12-6 exact commands,
P12-7 what I could not do) to `local/research/P1/REPORT.md` in
`/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1k]`, trailers; push `fork ssx3` from the fork clone only; remove
the lease if held; stop. No runtime fix in this brief.
