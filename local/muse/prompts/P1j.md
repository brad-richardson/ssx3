# P1j — SSX 3 on PS2Recomp, Part 11: identify GS CSR bits 15:14, drive the exit state, re-boot

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 10 first (P10-1: no in-tree producer for bits 15:14; consumer is
dynamic `READ64`; exit needs bit14=1, bit15=0; init value 0).
`W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1j`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground 3 min, logs
`$W/P1/run/boot-p1j-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
any time (`-j4`); boots only while holding the host lease (check
absent, `printf`, release immediately; if it names another agent, poll
every 5 min, log waits to `$W/P1/run/p1j-waits.log`). Push rule:
`git push` ONLY inside this fork clone to the `fork` remote; NEVER run
`git push` in `/Users/bradrichardson/dev/ssx3`. Time box 4 hours.

## Facts you start from

Thread 1 spins at `0x375d10` while `(CSR&0xC000)!=0x4000` (GS CSR at
`0x12001000`, read via dynamic `READ64` → `gs_regs.csr.load()`). The
runtime writes CSR bits {0, 1, 13} only, plus init-0 and guest merge;
nothing ever sets bit 14 or clears bit 15. Bits 15:14 have no name
anywhere in our tree. The game needs bit14=1 AND bit15=0 to proceed.

## Step 1 — identify the bits from public sources (no lease, no code)

GS CSR layout, bits 15:14: name, set-by, cleared-by, reset value, and
which hardware event sequence produces `0x4000`. Sources, in order:
(a) DobieStation GS registers (already cloned at
`/Volumes/Extreme SSD/dobiestation-q4` — read, do not re-clone);
(b) PCSX2 GS source (already cloned at
`/Volumes/Extreme SSD/pcsx2-ref` — P2's brief is done, the clone is
shared now); (c) public PS2 GS documentation online (cite URL +
section). Table: bit, name, set-by, cleared-by, reset value, exact
cite. No guessing: every cell cited or marked uncited-and-open.

## Step 2 — minimal producer (one commit, build any time)

Implement the smallest change that produces the exit state at the
correct lifecycle point (vsync worker? finish-event path? init
value? — state why that point from Step 1). If the correct producer
is a whole unbuilt subsystem, implement the minimal HLE that satisfies
THIS wait and document the cheat explicitly (code comment + report
row: what was faked, what would replace it). Receipts: diff, rebuild,
nothing else. One commit (`Kernel:` or `GS:` prefix).

## Step 3 — rebuild + one boot (lease protocol)

Rebuild `/tmp/p1-link`, boot 1 (≤3 min foreground). Receipts: binary
sha, ladder (thread-1 pc past `0x375d24`?, first new syscall ids,
first VIF MPG/MSCAL, first GIF kick, first presented frame, crash,
missing targets). New park recorded only (thread table + loop) — no
further fix in this brief.

## Step 4 — report

Append `## Part 11` (P11-0 lease record, P11-1 bit table + producer
diff + cheat row if any, P11-2 boot ladder, P11-3 binaries and
commits, P11-4 exact commands, P11-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1j]`, trailers; push `fork ssx3`
from the fork clone only; remove the lease if held; stop.
