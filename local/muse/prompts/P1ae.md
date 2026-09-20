# P1ae — Generic virtual-IOP SIF peer (SET_SREG/INIT_CMD via the guest table)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 26 §P26-1f/h/3
first (why the poke was needed + the responder shape), plus Part 27
§P27-1b/2b (the poke to supersede + the RPC-client evidence), plus the
frontier's §11 concern 1 (the mandate: generic peer, not a second
address poke). This brief replaces the per-address handshake with the
hardware-faithful shape. **Trigger:** the orchestrator launches this
only on a SIF-shaped park — record the stated trigger (P1ad successor
park / `sid=0x80000211` RPC / later SIF park) in the report.

## Facts you start from

On hardware the EE sends `SET_SREG`/`INIT_CMD` (cid `0x80000001` /
`0x80000002`); the IOP replies and EE `set_sreg` writes that game's
`sregs` wherever it keeps them. The HLE can do the same: learn the
guest `sif_cmd_data` address at `sceSifInitCmd`/`SetCmdBuffer`, and on
the EE send, queue the IOP's reply command and deliver it by
dispatching the guest's OWN sifcmd system-handler for `SET_SREG` —
no game `.bss` address in host code. References (read-only; verify
paths, do NOT assume): DobieStation `src/core/sif.cpp` (how the IOP
answers `INIT_CMD`/`SET_SREG`, SIF0/SIF1 register semantics —
`/Volumes/Extreme SSD/dobiestation-q4/...`); ps2sdk `iop/system/sifcmd`
server side (`/tmp/ps2sdk-ref/...` — if the `/tmp` clone is gone,
re-clone ps2sdk to SSD scratch; explicit exception to no-downloads
for this source-only reference). Play! `Iop_SifCmd` is a known third
source if the two disagree — record, don't clone.

## Gates and rules

- Lease `P1ae`: boots ONLY while holding `/tmp/ssx3-p-lane-lease`
  (the SHARED P-lane lease — M lane keeps the host lease) — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1ae-waits.log`. Builds any time (`-j4`). Max 3 boots,
  ≤90 s foreground each (two-stage proof needs the third; record
  why). No `adb`. Mark ladder throughput columns "contended".
- Fork: the peer files ONLY (SIF/RPC paths + tests — record the
  list). `git add` those NAMED files only — never `-A`, never stage
  or touch anything else. Verify the diff before committing. One
  commit per change with the `Orchestrated-By: Muse Code` trailer.
  `git pull --rebase` before pushing; `git push` ONLY inside the
  fork clone to the `fork` remote. Stop on any foreign rebase
  conflict. Never commit generated sources or `._*`.
- Report: if `P1/REPORT.md` is unowned when you launch (no peer
  brief appending), append the next `## Part` there and commit that
  file ONLY with `git add -f`; else use standalone
  `local/research/P1ae/`. State which. Prefix `[P1ae]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Design from the refs (lease-free).** Peer shape (reply queue on
   EE `SET_SREG`/`INIT_CMD`; guest-handler dispatch; `sif_cmd_data`
   capture point), the SSX3-vs-generic split (what, if anything, is
   game-specific — the goal is zero addresses), and the supersede
   plan for the `6447d8b` poke (peer proves first with the poke
   intact and a peer-specific receipt line distinguishing the
   delivery path; then the poke is deleted and re-proved).
2. **Implement + tests** (harness where the suite allows).
   BEFORE/AFTER receipts (peer receipt present/absent; handler
   dispatch evidence). Suite must stay all-green (state totals,
   name any face).
3. **Max 3 boots.** Stage 1 (peer + poke intact): handshake completes
   via the PEER path (receipt line proves which path delivered).
   Stage 2 (poke deleted): re-prove the handshake + the trigger
   park advances or moves. One ladder table vs the then-current
   baseline (state which) — throughput marked contended.
4. **Report.** Lease record, design + refs, diff + BEFORE/AFTER +
   tests, boots + peer-delivery proof + park movement, binaries
   and commits, exact commands, receipt paths, "What I could not
   do" (open IOP-model rows stay open — §13 says post-first-frame).
   Commit, remove the lease if held, stop.
