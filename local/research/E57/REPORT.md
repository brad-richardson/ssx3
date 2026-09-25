# E57 — VU1 interpreter speed, bit-exact

Worker: Claude Code (Opus 5.5), exploratory, approved by Brad. Box 22:13–01:13 EDT
2026-09-24/25. Tables and receipts; the orchestrator decides. No push, no Odin.

## Headline

- **Race speed on the Mac mini (M5 Pro), diagnostics off: 7.97 → 10.72 guest vsyncs/s
  (0.133× → 0.179× of 59.94), 1.35× on the whole game**, fork tip `a4ecce5` (code = c5
  `0a4aa5e`). Window: I26-FAST ticks (1800, 2400], exclusive lease, final session 4 in ABBA
  order (base 7.99/7.95, c5 10.75/10.69). Sessions drift ~2–3 % (c4 read 10.44 in session 2
  and 10.69 in session 3), so compare only within a session.
- **Bit-exact**: every candidate commit matches the baseline on all 2,400 `[det-hash:v1]`
  lines (RDRAM, scratchpad, VU1 data/code, VU1 execute count) and on the GS stream capture
  (1,387,680 records, 1,745,374,710 B, sha256 `6e9e03fd027019c6…`). Suite 600/600 at each
  step (baseline 600/600).
- Nearly all of the gain is **c1** (commit gate + valid-entry masks): VU1 share of busy
  game-process samples 46.0 % → 32.4 %; commitReadyPipelines 17.2 % → 5.1 %. c1 alone
  is 1.31× (session 1); c2–c5 add ~3 % together.
- VU1 and the CPU GS rasterizer share the GameThread. After E57, **the CPU GS backend is
  ~60 % of busy samples and VU1 ~33 %** (diagnostic profile). The next big Mac lever is the
  GS rasterizer (or the GPU backend), not VU1.
- **Recommendation:** ready for an Odin speed pair (baseline `f949ff0` vs `a4ecce5`, rebased
  onto `71c952e` for the fold; E57 touches only VU1 files and `71c952e` touches none). Nothing here is
  Mac-specific. The inline normalizers (c2) target an Odin-only symptom (N5 showed
  `normalizeOperand` as its own 2.4 % symbol). Expect a larger relative gain on the Odin if its
  race profile still has VU1 at ~50 % (N5). The orchestrator decides.

## Candidates (fork `~/dev/ssx3-work/E57/PS2Recomp`, local branch `e57-vu1` from `f949ff0`)

| # | Fork commit | Change | `--stat` |
| --- | --- | --- | --- |
| c1 | `69b3256` | `commitReadyPipelines()` returns before the earliest queued readyCycle (`m_nextCommitCycle`, a lower bound min-updated on every queue and recomputed on every real scan); per-pipeline valid bitmasks, so scans visit only valid entries in index order; first-free slot via the mask; `pipelinesPending()` from the masks; VI read/write loops by bit scan | h +16/−0, core +181/−137 |
| c2 | `ed35abf` | `normalizeOperand`/`normalizeResult` inline static in the header (same bodies); `calculatePairReadyCycle` lane tests as selects | h +47/−2, core +9/−51 |
| c3 | `cbca1ad` | inline commit gate + out-of-line scan; `progressXgkick()` only while a kick is active; written-VI pick via `countr_zero`; upper NOP (special 0x2F/0x30) returns before the side-effect-free operand normalization | h +8/−1, core +9/−12, upper +8 |
| c4 | `802f5d2` | FMAC exact results for all dest lanes from one op decode (`calculateFmacExactResults`, same per-lane expressions); XGKICK qword by `memcpy` when it doesn't wrap; the commit gate moves back inside the out-of-line function (see "c3 anomaly") | h +2/−8, core +117/−9 |
| c5 | `0a4aa5e` | `getDecodedInstructionPairForPc()` returns a const reference into the decode cache (uncached PCs decode into `m_decodeScratch`) instead of a copy per pair. Safe because the cache is rebuilt only inside that call and nothing in `run()` re-enters the interpreter (PATH1 goes to the GIF arbiter; `execute()` callers are only VIF1 MSCAL and EE CMSAR1) | h +5/−1, core +5/−5 |
| — | `a4ecce5` | comment only: drops the stale session-1 speed note from c4's gate comment | core −2 |

Total `f949ff0..a4ecce5`: 3 files, 389 insertions, 210 deletions (`ps2_vu1.h`,
`ps2_vu1_core.cpp`, `ps2_vu1_upper.cpp`). Runner-dir guard
(`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) empty at every commit. Commits carry
`Orchestrated-By: Claude Code`.

**Correct-behavior argument (all candidates):** a commit call before any entry's readyCycle
has no side effects, and the gate bound is conservative (only ever lowered by queues, exact
after a scan). The masks mirror `.valid`: the only writers are the queue functions, the
commit scan and `resetScheduler()`, which were all checked. Iteration order within a pipeline
is unchanged (low bit first = index order); pipeline order is unchanged. The other items
reorganize pure computations: the same IEEE expressions under `-ffp-contract=off`, which
CMake sets globally, Android included. The hash/digest gate is the empirical check.

## Acceptance (`check.py`)

`check.py --base run/h-base-1 --cand run/h-cN --base-suite suite-base.log --cand-suite suite-cN.log`

| Pair | Suite (total, passed, failed) | det-hash t1–2400 | GS capture | Result | Receipt |
| --- | --- | --- | --- | --- | --- |
| base vs base (null control) | 600/600/0 | 2400/2400 equal | equal, sha `6e9e03fd…` | BIT-EXACT | NOTEBOOK 22:25 |
| base vs c1 | 600/600/0 | equal, no first diff | equal | BIT-EXACT | `check-c1.txt` |
| base vs c2 | 600/600/0 | equal | equal | BIT-EXACT | `check-c2.txt` |
| base vs c3 | 600/600/0 | equal | equal | BIT-EXACT | `check-c3.txt` |
| base vs c4 | 600/600/0 | equal | equal | BIT-EXACT | `check-c4.txt` |
| base vs c5 | 600/600/0 | equal | equal | BIT-EXACT | `check-c5.txt` |

Boot settings (`e57_boot.py --mode hash`): `PS2X_DETERMINISTIC=1`, `PS2X_SKIP_MOVIE=1`
(dev-only), I26-FAST vsync pad script, empty `mc0`/`mc1` under each run dir,
`PS2X_DET_HASH_EVERY=1`, `PS2X_GS_CAPTURE` closed at `PS2X_GS_CAPTURE_STOP_TICK=2400`. Caps:
500 s wall, 120 s no-progress, 16 MiB log. One mini slot each, runner killed by recorded PID.
ISO `3c2f8eb1…` and ELF `1b49d05c…` read twice before each boot (in each `result.json`).

## Speed (Mac mini M5 Pro, diagnostics-off Release builds, exclusive lease per boot)

`build.sh speed`: Release, ThinLTO, homebrew clang, `PS2X_ENABLE_DIAG_TAPS=OFF`,
`PS2X_ENABLE_DET_HASH_TAP=OFF`, runtime/aggressive logs OFF, CPU GS only
(`PS2X_GS_SHADOW_PARALLEL=OFF`), codegen `~/dev/ssx3-work/codegen-ssx3`. Boots: same env as
the hash boots minus hash/capture, plus `PS2X_VSYNC_RATE_LOG=1`. Same guest work in every run
(deterministic). Rate = mean of the 5 s `[vsync-rate]` samples with end tick in (1800, 2400]
(`speed_table.py`, `speed-all.txt`).

| Run | Runner sha256 (two reads match, `binaries-sha.txt`) | vsyncs/s | ÷ 59.94 |
| --- | --- | ---: | ---: |
| s11-base, s18-base (session 2) | `0592bf74…fe47` | 7.86, 7.90 | 0.131×, 0.132× |
| s12-c2, s17-c2 | `b018e2d4…bbd2` | 10.25, 10.28 | 0.171×, 0.172× |
| s13-c3, s16-c3 | `c6f9462d…bb13` | 10.45, 10.46 | 0.174×, 0.175× |
| s14-c4, s15-c4 | `d4b21a7d…1bcb` | 10.48, 10.40 | 0.175×, 0.173× |
| s1-base / s2-c1 / s3-c2 (session 1) | base / `7483d5c1…` / c2 | 7.85 / 10.28 / 10.28 | 0.131× / 0.171× / 0.172× |
| s4-c3, s5-c3 (session 1, see anomaly) | c3 | 9.64, 9.70 | 0.161×, 0.162× |
| s21-c4, s24-c4 (session 3) | c4 | 10.71, 10.67 | 0.179×, 0.178× |
| s22-c5, s23-c5 (session 3) | `0d73edd7…ed4c` | 10.71, 10.71 | 0.179×, 0.179× |
| **s31-base, s34-base (session 4)** | base | **7.99, 7.95** | **0.133×, 0.133×** |
| **s32-c5, s33-c5 (session 4)** | c5 | **10.75, 10.69** | **0.179×, 0.178×** |

Within-session ratios: session 2 c4/base 1.33×, session 4 c5/base 1.35×, session 3 c5/c4
1.002× (c5's copy removal is within noise).

**c3 anomaly.** In session 1, c3 read 6 % below c2 on both runs (141 vs 136 s wall to t2400).
I blamed the inline-gate split and reverted it in c4. In session 2 (quieter host: 5/15-min
loads 2–7 vs 6–22), c3 reads 10.45/10.46, above c2. So the session-1 dip was host
interference that the lease doesn't cover (other lanes' unleased work), not c3. The c4 revert
of the gate split is neutral (c3 ≈ c4). Its code comment still cites the session-1 numbers
and should be corrected in any fold.

## VU1 profile share (diagnostic: `sample` 20 s from ~t1825, speed runner, one slot)

`profile_share.py`: busy = all top-of-stack rows except kernel waits. All busy samples are on
GameThread.

| | base | c1 | c4 |
| --- | ---: | ---: | ---: |
| Busy samples (20 s) | 11,862 | 11,563 | 14,198 |
| VU1Interpreter total | **46.0 %** | **32.4 %** | **33.1 %** |
| commitReadyPipelines | 17.2 % | 5.1 % | 6.7 % |
| calculatePairReadyCycle | 8.3 % | 3.5 % | 3.6 % |
| run | 5.3 % | 6.1 % | 6.8 % |
| FMAC flag/exact path (exact + normalize + sticky + flags) | 5.5 % | 6.6 % | 6.5 % |
| execUpper / execLower | 2.8 / 1.8 % | 3.8 / 2.4 % | 3.4 / 2.0 % |
| GS CPU backend (GSCpuBackend, GSMem, fn-ptr thunks) | 47.0 % | 60.2 % | 60.6 % |

The base and c1 profiles ran while builds were loading the host; c4 ran on an idle host.
Shares are within-process, so they are comparable; absolute sample counts are not.
Receipts: `profile-{base,c1,c4}.txt`.

## What's left, and what a static VU1 recompile would take

The remaining VU1 cost is spread out. The timing model is ~20 % of busy samples (run 6.8,
commit 6.7, pair ready 3.6, decode fetch 1.7, markPairWrites 1.5), FMAC math and flags ~10 %,
dispatch ~5 %. There's no single hot spot left for another pure refactor of this interpreter.
A timing wheel for the commit scan might save ~3–4 %.

Static recompilation of the 7 microprograms (7,305 instructions, E53), sketched:
1. **Keying:** hash the VU1 code memory at each `execute()` when the code generation changes
   (the decode cache already tracks it). Known hash → generated function; unknown → the
   interpreter.
2. **Stage A (dynamic scoreboard kept):** emit one C++ function per program, one `case` per
   pair PC (so `resume()`/MSCNT and budget truncation at 65,536 cycles can re-enter at any
   PC). Each pair calls the existing exec helpers with constant-folded fields, and passes
   read/write sets and latencies as constants to the unchanged scoreboard/commit code. This
   removes decode, the `InstructionUsage` lookups and the opcode switches: roughly the
   `run` + `getDecoded` + exec dispatch share, ~10 % of busy samples. It keeps every
   cycle-accounting rule.
3. **Stage B (static schedules):** per basic block, precompute stalls assuming the pipeline
   state at block entry, with a cheap guard (compare the entry scoreboard against the assumed
   one; interpreter fallback on mismatch). Must preserve: flag pipeline visibility at exact
   cycles (FMAND/FSAND/FCAND reads), Q/P latencies and WAITQ/WAITP, the LSU commit before
   PATH1 consumes a qword, XGKICK per-cycle progress, the VI branch backup, E-bit and D/T-bit
   delay slots.
4. **Validation:** the E57 gate (det-hash + GS digest) plus a per-program differential test
   that replays captured inputs through both paths and compares VU state, data memory and
   GIF bytes.
5. **Estimate:** stage A ~2–3 focused days (generator + codegen integration outside the
   runner dir + validation), stage B another 3–5 days. **Payoff bound on the Mac:** VU1 is
   ~33 % of the game thread now, so even a 3× VU1 speed-up gives ≤ ~1.28× overall while the
   CPU GS rasterizer is ~60 %. On the Odin the bound depends on its GS path: with the GPU
   backend and a VU1-dominated thread, the ceiling is much higher.

## Commands and pins

- Worktree `~/dev/ssx3-work/E57/PS2Recomp` (branch `e57-vu1`); builds
  `~/dev/ssx3-work/E57/build.sh hash|speed` (dirs `build-hash`, `build-speed`); binaries
  copied to `~/dev/ssx3-work/E57/bin/` (SHAs in `binaries-sha.txt`, two reads match).
- Suites: `cd ~/dev/ssx3-work/E57/PS2Recomp && ../bin/tests-<c>-hash > ../suite-<c>.log`.
- Hash boots: `e57_boot.py --mode hash --runner bin/runner-<c>-hash --label h-<c>`; speed:
  `CANDS="base c2 c3 c4 c4 c3 c2 base" START=10 speed_session.sh`; profiles:
  `e57_boot.py --mode profile --runner bin/runner-<c>-speed --label p-<c> --stop-tick 2000
  --sample-at 1800 --sample-s 20`.
- Scratch `~/dev/ssx3-work/E57` ~6.5 GB (cap 20 GB); GS captures deleted after each check
  except `run/h-base-1/gs.cap` (the reference). Disk budget 90.2 GB / 200 GB.

## Gaps

- Mac only; no Odin number. The Android build uses the same CMake flags
  (`-ffp-contract=off`), but the Odin hash/speed pair hasn't been run.
- Bit-exactness is shown on one route (I26-FAST, t1–2400, empty cards) plus the suite. Paths
  this route doesn't exercise (for example reserved-instruction stops or a full flag
  pipeline) rest on the code argument above.
- Speed: four sessions, ABBA order within each, one route window. Session-1 c3 shows host interference can
  move a run by ~6 % even under the exclusive lease.
- Profiles are `sample` top-of-stack only (no line-level attribution inside `run`).
- VU0 shares this interpreter class (`VU1Interpreter(Unit::VU0)`), so the changes apply to
  it too. Its micro-programs run in the race (E53: 1.67 M starts per boot), and their results
  reach RDRAM, which the det-hash covers. No VU0-specific profile or count was taken; its
  samples are included in the VU1Interpreter rows above.
