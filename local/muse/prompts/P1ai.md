# P1ai — Post-exit diagnosis: main-return, 31-drain, freeze sequencing + next-park spec (Part 32, no boot)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/T13/REPORT.md` first (all of it —
the phase EXITED at block 235: stub collapse → 29-halt →
31-drain (781) → main DORMANT pc 0x0 → dma/gif freeze; N =
72,176; T13's miners tabled the exit but did not diagnose the
post-exit state), plus P1 REPORT Part 31 (the pre-exit
ladder) and Part 24 §P24-1f/g (`[drop]` census conventions).
This is a DIAGNOSIS brief on committed logs — no boot. A peer
(T15) runs the follow-up boot concurrently; your §P32-6
next-park spec is its signature watchlist — write it to be
read by a boot brief. Peer lanes run concurrently — you share
only the fork remote (read-only for you).

## Facts you start from

- Inputs (read-only, never copy 6.5 GB anywhere — stream it):
  `W/P1/run/boot-t13-1.log` (2,493,828 lines, exit region ≥
  line 2,453,403), `W/P1/run/ps2_log-t13-1.txt` (185,293,022
  lines, post-phase ≥ line 185,264,991), T13's `blocks.tsv`
  (242) + `ticks.tsv` (166), `W=/Volumes/Extreme
  SSD/ps2recomp-spike`.
- Exit landmarks (T13 — verify, don't trust): stub
  222→218→211→189→13 (b235–241); 29-halt (117/0/0 at
  b239–241); 31-drain 781 iterations (9-func family);
  main status 5 pc 0x0 (b240–241, empty stack); dma/gif
  0.02703 → 8658/234 → 0/0 frozen; sema-30 4w/3s parked
  (t3 never releases); 113 post-phase funcs, 0 post-only;
  CD/SIF/GS/RPC 0 new past block 2.
- The question: WHAT IS the post-exit state (a returned main?
  a drained pump? a frozen device pair? — mechanistically,
  per thread per device), and WHAT should the next boot
  watch for (exact next-park spec: signatures + first-line
  watches + miner rows)? Answer by table.

## Gates and rules

- NO lease of any kind (diagnosis brief — no boots, no harness
  runs). No fork changes at all. No `adb`. Read-only on every
  other agent's dirs; scratch in `/tmp/p1ai/`; stream the
  6.5 GB trace (never copy it).
- Evidence: APPEND Part 32 to `local/research/P1/REPORT.md`
  (do NOT rewrite earlier Parts; a peer brief may own other
  regions — append only). Commit with `git add -f`, prefix
  `[P1ai]`, trailer `Orchestrated-By: Muse Code`. NEVER run
  `git push` in ssx3.
- Time box: 4 h. Tables, no verdicts.

## Task 1 — main-return mechanics (§P32-1)

1. Status-5 table: every status-5 sample (block, pc, ra —
   T13: 2 samples b240–241; reproduce + extend: any more
   in the tail?).
2. Return-path table: from the post-phase trace, the call
   chain that returns main (which functions exit in
   unwind order? the 4,049-frame unwind itemized by
   function, top 20 + the rest pooled).
3. Dormant-precedent table: P1's `makeDormant on pc==0`
   precedent vs this return (same call site? same
   register state? table the match/mismatch rows).

## Task 2 — 31-drain family + 29-halt split (§P32-2)

1. Drain-family table: the 9 funcs × 781 iterations with
   names/roles from `ps2_recompiled_functions.h` (what
   DOES the drain do? pump subprocess? teardown?).
2. Halt-split table: last 29-events (block, line, op) vs
   continuing 31-events over b239–241 (where exactly
   does 29 stop while 31 continues?).
3. Handshake-balance table: 29w/s29 72178/72178 + 31w/s31
   72959/72958 reproduced; the +2 29-edge +1 31-inflight
   itemized (which lines? which threads?).

## Task 3 — freeze sequencing + residue + silence audit (§P32-3/4)

1. Freeze table: last 5 tick pairs (dma/gif/deltas/ratio —
   reproduce T13's 8658/234 → 0/0) + which device stops
   first (dma? gif? same tick?).
2. Residue table: the 13 b241 stubs identified (which
   addresses? the @606/303 counts itemized — what REMAINS
   stubbed after the collapse?).
3. Silence re-audit: drops/RPC/CD/SIF/GS over the exit
   region only (lines ≥2453403 / trace ≥185264991 — all 0
   per T13; reproduce with last-line-before-exit rows).

## Task 4 — next-park spec (§P32-5/6 — T15 reads this)

1. State table: post-exit state per thread (t1/t3/t6) per
   device (sema-29/30/31, dma/gif, stubs) — the von-Neumann
   snapshot the next boot starts from (it reboots, so: what
   INVARIANT should it reproduce at block 235?).
2. Watchlist table: exact next-phase signatures for T15
   (new stub phase after residue? main wake from dormant?
   first new guest event? new caller? dma/gif unfreeze?
   second exit?) with trigger rows a monitor can poll.
3. Miner-row table: the 10 miner rows T15's analysis must
   emit (block of next event, N2 count?, handshake
   deltas, stack state at next cap — table the row specs).

## Report

Append `local/research/P1/REPORT.md` Part 32 (§P32-1..6 +
exact commands + receipt paths + "What I could not do").
Commit (`[P1ai]`, no push), stop.
