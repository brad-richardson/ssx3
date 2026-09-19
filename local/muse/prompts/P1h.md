# P1h — SSX 3 on PS2Recomp, Part 9: fix the LUI+ORI MMIO fold, regenerate, re-boot

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 8 first (P8-1a fold table, P8-1d proof chain), plus Part 5 for the
regenerate/rebuild receipts. `W=/Volumes/Extreme SSD/ps2recomp-spike`.
Rules exactly as `local/muse/prompts/P1c.md` "Rules" (lease `P1h`, no
adb, never commit generated runner sources or `._*`, purge sidecars, one
commit per change with the two trailers, boots foreground 3 min, logs
`$W/P1/run/boot-p1h-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease, and
M5 has priority — if `/tmp/ssx3-host-lease` names another agent, poll
every 5 minutes and log waits to `$W/P1/run/p1h-waits.log`. Push rule:
`git push` ONLY inside this fork clone to the `fork` remote; NEVER run
`git push` in `/Users/bradrichardson/dev/ssx3` (the orchestrator owns
that origin — prior agents pushed it by running bare `git push`; do not
repeat that). Time box 4 hours.

## Facts you start from

Thread 1 spins at `0x391330` polling VIF0_CHCR STR because the
recompiler folds all 7 MMIO accesses in `sub_003912A8` to `0x10000000`:
the kick stores land in `m_ioRegisters[0x10000000]` (DMA gate needs
`address>=0x10008000`, so no transfer, no STR clear) and the poll reads
back the stuck `0x104`. Root cause is the analyzer's MMIO detector
(`ps2xAnalyzer/src/elf_analyzer.cpp:427-447`): it scans back ≤5
instructions for the LUI, takes `baseAddr = IMM<<16`, and adds only the
`int16` load/store offset — the ORI low half (`ori $v,$v,0x8000/0x8020/
0x8030`) is never read. 249 of 273 TOML `[mmio]` entries fold to
`0x10000000`, but truncation is proven only for this function's 7 pcs.

## Step 1 — analyzer fix (one commit `Analyzer:`, build any time)

Extend the scanback so the MMIO target accounts for the low half:
match `ORI`/`ADDIU` (state if any other opcode writes the low half in
the game's MMIO sequences — scan, do not assume) targeting the same
base register between the LUI and the access; target =
`(LUI<<16 | ori_imm) + int16(offset)`. State the exact rule, the
opcodes covered, and what happens when no LUI is found (unchanged
behavior). Receipts: diff, analyzer rebuild, nothing else.

## Step 2 — regenerate + audit (no lease)

Re-run the analyzer/recomp for the game per the Part 5 receipts.
Receipts: count of `[mmio]` entries changed (and how many remain
folded to `0x10000000` — each remaining one gets one line: pc, true
address by hand decode, why the new rule still folds it or why the
fold is correct); the 7 `sub_003912A8` pcs now mapping to their true
`0x10008000/20/30`; `diff --stat` of the regenerated runner sources
(never committed). If regen needs the lease for any reason, it doesn't
— regen is file-to-file; only boots take the lease.

## Step 3 — rebuild + one boot (lease-poll, M5 priority)

Rebuild `/tmp/p1-link`, boot 1 (≤3 min foreground). Receipts: binary
sha, ladder (thread table at last dump, thread-1 pc past `0x391344`?,
first new syscall ids, first VIF MPG/MSCAL, first GIF kick, first
presented frame, crash, missing targets). If thread 1 advances to a new
park, record it (thread table + last dispatch lines) and stop — no
further fix in this brief.

## Step 4 — report

Append `## Part 9` (P9-0 lease record, P9-1 analyzer rule + diff,
P9-2 regen audit table, P9-3 boot ladder, P9-4 binaries and commits,
P9-5 exact commands, P9-6 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1h]`, trailers; push `fork ssx3`
from the fork clone only; remove the lease if held; stop.
