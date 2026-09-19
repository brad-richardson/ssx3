# P1p — SSX 3 on PS2Recomp, Part 17: which flag writer fires for entry 0 at runtime (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 16 first (P16-2c–2e writers W1/W2/W3 + table writer, P16-2k designed
receipt, P16-2l machine-check block). `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Rules exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1p`, no
adb, never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1p-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1p-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1o closed the caller saga (true-frame hits land, probe byte-identical)
and named the writers statically: ONE table-base writer (`0x3dccfc` →
`0x519AD8`), THREE flag writers (W1 `0x3de468` = P6
`iFILESYS_CommandCompleteCallback`, W2 `0x3dd83c` = 1, W3 `0x3ddd30` =
−2), parked wait on entry 0 (`*( *(0x519AD8) + 8 )`). Open: which writer
fires for entry 0 at runtime, and the table base / entry-0 absolute
addrs (never watched). Fork HEAD `e73e36a`, binary `7a7d4b64` fresh
(rebuild only if stale). Out of scope: sema-26 non-delivery, any
behavior fix.

## Step 1 — learn the table (one boot ≤90 s)

Boot 1 with `PS2X_DIAG_WATCH=0x519AD8,0x519AD4` (w4 each; zero
steady-state traffic expected — these are one-time/shift values).
Receipts: table base value + writer pc (expect `0x3dccfc`), current
entry value + set/clear pcs (expect `0x3de0b0`/`0x3de470`), computed
entry-0+8 absolute addr (machine-checked, pasted), plus the standard
ladder row.

## Step 2 — catch the writer (one more boot ≤90 s, only if Step 1 resolves the addr)

Boot 2 watching the Step-1 entry-0+8 addr (w4). Receipts: writer
pc(s) with values — W1/W2/W3 identified (or the residue if a fourth
writer appears, with its pc + owning function + ELF word). If Step 1
fails to resolve the addr, skip this boot and table the residue +
the exact next receipt instead.

## Step 3 — report

Append `## Part 17` (P17-0 lease record, P17-1 table addrs, P17-2
runtime writer answer, P17-3 binaries and commits, P17-4 exact
commands, P17-5 what I could not do) to `local/research/P1/REPORT.md`
in `/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1p]`, trailers; push `fork ssx3` from the fork clone only (expect
nothing to push — verify up-to-date); remove the lease if held; stop.
