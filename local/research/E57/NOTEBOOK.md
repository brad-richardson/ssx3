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
