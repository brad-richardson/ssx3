# E57 notebook (append-only)

Worker: Claude Code (Opus 5.5), exploratory, 3 h box from 22:13 EDT 2026-09-24.
Worktree `~/dev/ssx3-work/E57/PS2Recomp`, branch `e57-vu1` from `f949ff0`.

## 22:13–22:45 orientation

- Read brief, AGENTS files, facts, orchestration §3, N5/E45/E53/E55C2, E55D16 boot script, I26 routes.
- Hot loop (`ps2_vu1_core.cpp` `run()`): per issued pair, `commitReadyPipelines()` runs twice
  (loop top + `advanceOneCycle()`), each a full scan of 8 flag + 1 FDIV + 2 EFU + 8 store +
  16 VF + 8 VI + 8 ACC entries (51), even when nothing is due. `calculatePairReadyCycle()`
  tests all 15 VI bits one by one; `markPairWrites()` the same.
- Every FMAC op queues a flag entry (ready +4), so a pure "nothing due" gate alone won't skip
  most calls in FMAC-dense code; visiting only valid entries is the other half.
- Candidate 1 (hypothesis H1: the commit scan's cost is the scan, not the commits):
  gate `commitReadyPipelines()` on a conservative lower bound of the earliest queued
  readyCycle (`m_nextCommitCycle`, min-updated on every queue, recomputed on every real
  scan); per-pipeline valid bitmasks so scans visit only valid entries in the same index
  order; first-free slot via the mask (same slot as the linear scan); `pipelinesPending()`
  from the masks; VI read/write loops via bit scan. Correct-behavior argument: a commit call
  before any entry is due has no side effects; masks mirror `.valid` exactly (only writers are
  the queue functions, commit, `resetScheduler()`).
- Gotcha: the baseline build reads the same worktree; edits moved to `../cand1.patch` until
  the baseline binaries are copied out.
- Builds: `~/dev/ssx3-work/E57/build.sh hash|speed` (Release, clang 22 homebrew, CPU GS only
  `PS2X_GS_SHADOW_PARALLEL=OFF`, logs/diag taps OFF; `hash` = `PS2X_ENABLE_DET_HASH_TAP=ON`).

## 22:25 null control (baseline vs baseline)

- Baseline `f949ff0` hash runner `bin/runner-base-hash` sha256 `9b546d3d…6a22`; suite
  (hash build, worktree root) **600/600**.
- Two baseline hash boots, in parallel under heavy host load (load avg up to 187 with builds):
  `check.py --base run/h-base-1 --cand run/h-base-2` → hash PASS (2400/2400 lines, no diff),
  gs PASS (1,387,680 records, 1,745,374,710 B, sha256 `6e9e03fd027019c6…`), BIT-EXACT.
  Each boot 278 s wall to t2400 (diagnostic, not speed). Deterministic mode repeats exactly;
  the gate discriminates. `h-base-2/gs.cap` deleted after the check (disk), digest above.
- Baseline speed runner `bin/runner-base-speed` sha256 `0592bf74…fe47`.

## ~22:30 candidate 1 gated; baseline profile

- Baseline profile (`sample` 20 s from t1825, speed runner, one slot, host busy with builds;
  **diagnostic**): busy samples 11,862; VU1Interpreter **46.0 %**, GS CPU backend 47.0 %.
  VU1 rows: commitReadyPipelines 17.2 %, calculatePairReadyCycle 8.3 %, run 5.3 %,
  calculateFmacExactResult 3.2 %, execUpper 2.8 %, execLower 1.8 %, markPairWrites 1.6 %.
  Same shape as N5's Odin table. (`profile_share.py`.)
- C1 fork commit `69b3256` (`e57-vu1`): suite 600/600; `check.py` base vs c1 → hash PASS
  2400/2400, gs PASS (same sha `6e9e03fd…`), **BIT-EXACT** (`check-c1.txt`). Runners: hash
  `8e7fb77e…`, speed `7483d5c1…`. Runner-dir guard empty.
- C2 (drafted in scratch worktree `E57/c2src`, copied in): `normalizeOperand`/
  `normalizeResult` inline static in the header (Odin build shows normalizeOperand as its own
  2.4 % symbol); calculatePairReadyCycle lane tests as selects. Building; c1 profile running.

## ~22:45 c1 profile, c2 gated, c3 built

- C1 profile (diagnostic, same method as baseline): VU1Interpreter **32.4 %** of busy samples
  (was 46.0 %); commitReadyPipelines 5.1 % (was 17.2 %), calculatePairReadyCycle 3.5 % (was
  8.3 %). GS CPU backend now 60.2 %. All busy samples are on GameThread (VU1 and the CPU GS
  rasterizer share the one thread), so the game thread is the bottleneck.
- C2 fork commit `ed35abf`: suite 600/600, `check-c2.txt` BIT-EXACT (hash 2400/2400, gs sha
  `6e9e03fd…`). Runners: hash `0f5cf9aa…`, speed `b018e2d4…`.
- C3 (uncommitted until gated): inline commit gate (`commitReadyPipelines()` = one compare,
  scan moved to `commitDuePipelines()`), `progressXgkick()` only called while a kick is active
  (its first line returned otherwise), written-VI pick via countr_zero, upper NOP (special
  0x2F/0x30) returns before the side-effect-free operand normalization. Suite 600/600.
  Runners: hash `7f89366f…`, speed `c6f94626…`.
- Speed session `speed_session.sh`: base c1 c2 c3 c3 c2 c1 base, each boot with the exclusive
  lease to t2400, window (1800, 2400] of `[vsync-rate]` (`speed_table.py`). The c3 hash boot
  waits for a free slot between speed boots (no overlap: speed boots take all four slots).

## ~23:20 speed session 1, c3 slower, c4

- Speed session 1 (exclusive lease per boot, no overlaps: start/end times checked, load 2–4 at
  each start), window (1800, 2400]: base 7.85 vs/s (0.131×), c1 10.28 (0.171×), c2 10.28
  (0.172×), c3 9.64 / 9.70 (0.161×). `speed-1.txt`. Session stopped after s5: other lanes
  (au9, rr1) held single slots, so the exclusive claim for s6 was starving; I killed my own
  waiting session script (no runner had started).
- C3 gated BIT-EXACT (`check-c3.txt`) and committed as fork `cbca1ad`, but it is ~6 % slower
  than c2, reproducibly (two runs, 141 vs 136 s wall to t2400). Hypothesis: the inline header
  gate + out-of-line scan changed inlining of the hot loop (c2 had the gate inside the
  out-of-line function). Not proven; other c3 items (NOP early out, countr_zero VI pick, XGKICK
  active check) remove work and are unlikely to cost 6 %.
- C4 = c3 with the gate split reverted + FMAC exact results for all dest lanes from one op
  decode (`calculateFmacExactResults`, same per-lane expressions; `-ffp-contract=off` is global
  incl. Android, so the double expressions round identically) + XGKICK qword copy by memcpy
  when the 16 bytes don't wrap (same bytes as the per-byte modulo). Suite 600/600. Runners hash
  `656f5aad…`, speed `d4b21a7d…`. Hash boot and speed session 2 (base c2 c3 c4 c4 c3 c2 base)
  queued on the lease.
- Orchestrator FYI: fork ssx3 moved to `71c952e` (I32); it touches no VU1 file, so these
  commits should rebase cleanly.

## ~00:15 sessions 2–4, c5, close

- Session 2 (clean host): base 7.86/7.90, c2 10.25/10.28, c3 10.45/10.46, c4 10.48/10.40.
  The session-1 c3 dip does not reproduce, so it was host interference the lease doesn't cover
  (5/15-min loads were 6–22 then). My inlining hypothesis was wrong; c4's revert of the gate
  split is neutral. `a4ecce5` drops the stale comment (comment only, no rebuild).
- C4 profile (idle host, diagnostic): VU1 33.1 %, GS CPU backend 60.6 %. c2–c4 barely move
  the VU1 share; c1 did the work.
- C5 `0a4aa5e`: decoded pair by const reference (re-entrancy checked: PATH1 goes to the GIF
  arbiter, `execute()` callers are only VIF1 MSCAL and EE CMSAR1). Suite 600/600,
  `check-c5.txt` BIT-EXACT. Session 3: c4 10.71/10.67 vs c5 10.71/10.71 (tie). Note c4 drifted
  +2.4 % between sessions 2 and 3.
- Session 4 (final, ABBA): base 7.99/7.95 vs c5 10.75/10.69 → **1.35×** (0.133× → 0.179×).
- Scratch worktree `E57/c2src` removed after a byte compare with the committed c4. The
  reference capture `run/h-base-1/gs.cap` is kept; the other captures were deleted after their
  checks. Write-up in REPORT.md.
