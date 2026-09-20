# P1af — Emulate SPR normal-mode DMA data movement (SPR_FROM first)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 28 §P28-1f/g
(the HLE gap + candidate table), §P28-2b (probe proof), and §P28-3b
(this brief's exact spec) first. This is a FIX brief: implement §P28-3b.
(NOTE: Part 28 titles this fix "P1ae"; renamed P1af — P1ae is the
standing generic-SIF-peer brief queued for SIF-shaped parks.) P13/M17
run concurrently in other panes — you share only the fork remote.

## Facts you start from

Main wedges in `sub_00394ED0` on a self-looped hash chain
(`0x85aabc→self`): the HLE completes SPR_FROM DMA without moving data,
so `sub_00362CC8` re-inits reset pool counts but never re-zero the
256 buckets. Observed op: `MADR`=bucket array, `QWC`=64,
`SADR`=scratchpad byte offset, `CHCR`=`0x100`. Sibling table
`0x395000` shares the exposure (healthy by luck). SPR_TO status is
unresolved (working vs varying-memset-window) — this brief resolves
it empirically.

## Gates and rules

- Lease `P1af`: boots ONLY while holding `/tmp/ssx3-p-lane-lease`
  (the SHARED P-lane lease — M lane keeps the host lease) — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1af-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`. Mark ladder throughput columns
  "contended".
- Fork: the DMA files ONLY (`ps2_memory.cpp` + tests — record the
  list). `git add` those NAMED files only — never `-A`, never stage
  or touch anything else. Verify the diff before committing. One
  commit per change with the `Orchestrated-By: Muse Code` trailer.
  `git pull --rebase` before pushing; `git push` ONLY inside the
  fork clone to the `fork` remote. Stop on any foreign rebase
  conflict. Never commit generated sources or `._*`.
- ssx3: append `## Part 29` to `local/research/P1/REPORT.md`; commit
  that file ONLY with `git add -f`, prefix `[P1af]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Implement §P28-3b.** P0: on `CHCR` STR write to `0x1000D000`
   (SPR_FROM) with `MOD`=NORMAL, synchronously copy `QWC` quads
   from scratchpad host store + `SADR` to RAM `MADR&0x01FFFFFF`;
   update `MADR`/`QWC`/`SADR`, clear `STR`, set the channel
   `D_STAT` CIS (mirror the VIF0/VIF1/GIF section ~:1298-1420).
   P1 (co-fix): SPR_TO (`0x1000D400`) mirror + resolve TO status
   (scratchpad dump or hash comparison — record which model
   holds). Keep the STR auto-clear-on-read (`:2248-2256`).
   BEFORE/AFTER receipts (bucket bytes moved / regs updated /
   `STR` clear). Suite must stay all-green (state totals — count
   them, peers add tests — name any face).
2. **Max 2 boots** (reuse `/tmp/p1ad-boot{1,2}.py` +
   `PS2X_DIAG_394ED0=1`): (1) probe shows `head=0x0` after every
   re-init and `n` advancing past 136 with pool cycling cleanly;
   (2) a 4th sema-30 signal appears and thread 3 leaves `WAIT 30`;
   (3) main leaves `0x394ED0` (park gone); (4) census/drops/RPC/
   ladder show no other face. One ladder table vs P28-boot1,
   throughput contended.
3. **Report.** `## Part 29` (P29-0 lease record, P29-1 diff +
   BEFORE/AFTER + tests, P29-2 boots + unstick proof + new park
   if any, P29-3 binaries and commits, P29-4 exact commands,
   P29-5 what I could not do — incl. probe disposition: keep
   `5001830` or remove it, implementer's call recorded). Commit,
   remove the lease if held, stop.
