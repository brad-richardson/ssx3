# VR1 notebook (append-only)

Worker: Claude Code (Opus 5.5), exploratory. Box 09:48:35–12:48 EDT 2026-09-25.
Worktree `~/dev/ssx3-work/VR1/PS2Recomp` branch `vr1-vu1-recomp` from `0ed07c4`;
base source = `git archive 0ed07c4` in `~/dev/ssx3-work/VR1/base-src` (so base builds never
see candidate edits). Builds: `~/dev/ssx3-work/VR1/build.sh base|vr1 hash|speed` (F2 Mac
recipe: Release, homebrew clang, paraLLEl shadow ON from `F2/parallel-gs` @ `19d93b2`,
diag taps OFF; hash adds only `PS2X_ENABLE_DET_HASH_TAP=ON`). Full build ≈ 2 min.

## 09:50 plan
Design (stage A):
- Refactor the body of `run()`'s pair loop into one always-inline template
  `issuePair<kStatic>(const DecodedInstructionPair&, ctx)`; the interpreter calls it with the
  decode-cache entry (`kStatic=false`, out-of-line `execUpper/execLower`), generated code calls
  it with a `static constexpr DecodedInstructionPair` and `kStatic=true`, which calls
  always-inline `execUpperImpl/execLowerImpl` with a constant word (switch folds away).
  `calculatePairReadyCycle`/`markPairWrites` become inline so the usage loops fold on
  constants. Scoreboard, commit, cycle accounting: the same functions, unchanged.
- Generated code: one function per pair PC (so any PC can be entered: resume/MSCNT, budget
  truncation), one table per code image `pairs[codeSize/8]`, null = interpreter for that
  PC. Keyed by XXH64 of the code image, recomputed only when the code generation changes.
- Pipeline: dump boot (`PS2X_VU1_RECOMP_DUMP=<dir>`) writes each new image + the PCs it
  executes; generator tool emits one `.cpp` per image outside the repo; CMake
  `PS2X_VU1_RECOMP_DIR` compiles them into `ps2EntryRunner`.

## 10:05 implementation (refactor + hooks = candidate "r")
- `ps2_vu1_{upper,lower}.cpp` bodies moved verbatim into `ps2_vu1_{upper,lower}_impl.h` as
  always-inline `execUpperImpl/execLowerImpl` (helpers in named detail namespaces, `inline`);
  the `.cpp` files keep `execUpper/execLower` as out-of-line wrappers.
- `ps2_vu1_step_impl.h`: `calculatePairReadyCycle`, `markPairWrites` (verbatim, now inline)
  and `issuePair<kStatic>` (the verbatim loop body of `run()`, `break`→`return true`, loop
  locals → `RunContext`). `run()` keeps commit, pc bound, decode, reserved check.
- `ps2_vu1_recomp.cpp`: registry (hash → table), `lookupRecompProgram` (XXH64 of the code
  image on generation change), `emitRecompSource` (every non-reserved pair, decoded by the
  interpreter's own `decodeInstructionPair`, as `static constexpr DecodedInstructionPair` +
  `static bool fXXXX(vu, c) { return vu.issuePair<true>(dXXXX, c); }` in an explicit
  specialization `VU1RecompImage<hash>` (friend of the interpreter), table `kPairs[2048]`,
  static-init registration). Env: `PS2X_VU1_RECOMP=0` (off), `_DUMP=<dir>`, `_STATS=1`.
- CMake `PS2X_VU1_RECOMP_DIR`: globs `vu1_*.cpp` into `ps2EntryRunner` (no unity, no PCH).
- Build fix: XXH64 needs `XXH_INLINE_ALL` (as EeScheduler.cpp does).
- Suites: base `0ed07c4` 616/616/0; r 616/616/0 (from the worktree root).
- Boots (one slot each): `h-base-1` (base hash), `h-r-dump` (r hash + dump + stats).

## 10:12 gate for r and g (NULL CONTROL FIRST: it fails the strict GS check)
- 7 code images in the I26-FAST boot to t2400 (`gen-v1/`, SHAs `gen-v1.sha`); my key equals
  the det-hash `vu1Code` field (both XXH64 seed 0). Generated file: 2,048 pairs each (every
  pair decodes without a reserved op), 6,173 lines, 8 s compile, 5.3 MB ThinLTO object.
  Asm check (`-S`): 2,048 pair functions, median 333 asm lines, no opcode switch left;
  remaining calls: advanceTo/advanceOneCycle, queueVfWrite/ViWrite/AccWrite/Store,
  applyDest/applyFmacDest(Acc), broadcast, microAddressMask (fixed in g2).
- **Null control h-base-1 vs h-base-2 (same binary): det-hash 2400/2400 equal, GS capture
  whole-file SHA differs** (first diff record 7,348, tick 253; equal record count and bytes).
  E57's strict GS SHA check was on the CPU backend; this is the paraLLEl Mac build.
  `gs_types.py`: per record type, and per GIF path for packets, the payload sequences
  without the record tick are EQUAL; only record tick stamps and cross-path interleave
  race. So the GS gate here = per-path tick-stripped payload sequences + VBlank + priv
  writes + transfers (all deterministic in the null control). Cross-path order can't
  discriminate on this build; noted as a gap.
- Receipts `check-gate.txt`: suite 616/616 (base, r, g2); det-hash 2400/2400 equal and GS
  per-path content equal for h-base-2 (null), h-r-dump (refactor), h-g-1 (generated),
  h-g2-1 (g2).
- Coverage (g, g2): `[vu1-recomp] runs=1048576 generated_cycles=959411166
  interpreted_cycles=0` → **100 % of VU1 cycles in generated code**; the interpreter run (r)
  has the same total (959,411,166 cycles), another exactness signal.
- Fork commits: `00381ff` stage A, `71fda22` g2 (entry snapshot to members, 576 B stack
  clear per pair gone; microAddressMask inline). Runner guard empty on both.
- Host: load 60–96 (SJ1, FP1, NP1 boots, I33 simulator); all four mini slots held by
  others. Speed session 1 (`base g g base`) queued, waiting for the exclusive lease.

## 10:28 profiles (diagnostic, `sample` 20 s from t1800, speed runners, one slot, load ~15)
`profile_share.py` (process-wide top of stack; busy = non-wait rows):

| | p-base (0ed07c4) | p-g2 |
| --- | ---: | ---: |
| busy samples | 10,423 | 8,085 |
| VU1 total (interpreter + generated) | **82.5 %** | **70.7 %** |
| VU1RecompImage::f* (generated pair bodies) | — | 9.0 % |
| run | 17.5 % | 6.3 % |
| commitReadyPipelines | 16.5 % | 25.8 % |
| normalizeFmacResult | 9.8 % | 16.5 % |
| calculatePairReadyCycle | 9.4 % | (inlined) |
| execUpper / execLower | 8.8 / 4.6 % | 0.9 / 0.4 % (VU0) |
| markPairWrites | 4.2 % | (inlined) |
| calculateFmacProductSticky | 3.6 % | 6.1 % |
| getDecodedInstructionPairForPc + decode | 4.1 % | 0.4 % (VU0) |
| updateFmacFlags | 2.3 % | 3.8 % |

On the paraLLEl Mac build the GS work is off the game thread, so VU1 is 82.5 % of busy
samples (E57's CPU-GS profile had 33 %). Decode, usage lookups and dispatch are gone; what's
left is the scoreboard commit and the FMAC exact-result path. The FMAC helpers re-decode
`m_currentUpperInstruction` and loop over dest lanes at run time → g3.

## 10:30 g3 = FMAC result helpers always-inline (fork `1b09a49`)
broadcast/applyDest/normalizeFmacResult/calculateFmacExactResults/normalizeFmacExactResult/
calculateFmacProductSticky/updateFmacFlags/applyFmacDest(Acc) moved verbatim into
`ps2_vu1_fmac_impl.h` (always-inline). Asm: the applyFmac* calls are gone from the pair
functions and the median pair function shrank 333 → 305 lines (op decode + lane loops fold
on the constant word the store-to-load forwards from `m_currentUpperInstruction`).
Gate: suite 616/616, det-hash 2400/2400, GS per-path content equal, 100 % coverage.

## 10:32 speed: exclusive claims starve
Session 1 (`base g g base` with polling exclusive claims) never got the lease in ~15 min:
NP1, SJ1, FP1, I33 keep cycling single slots. Replaced by `speed_hold.py`: claims each slot
as it frees (5 s poll) until it holds all four, runs two ~90 s speed boots back to back
(one hold ≤ 5 min), releases. Hold A = base, g3; hold B = g3, base (ABBA across holds).

## 10:45 g4 = chained pairs (generated code hands off without returning to run())
- Emitter: every pair function ends `return next(vu, c)`; `next` runs
  `recompChainReady` (the run() loop header in the same order: budget/stop, commit, pc
  bound, alignment) and `[[clang::musttail]]`-calls `kPairs[pc>>3]` (null → back to run()).
  The repeated commit when run() resumes is a no-op at the same cycle.
- Needs regenerated sources: dump boot `h-g4a-dump` with `PS2X_VU1_RECOMP=0` →
  `gen-v2/` (same 7 hashes; interpreted total again 959,411,166 cycles).
- Mistake on the way: `cmake -B` without `-S` failed silently in my loop, so the first g4
  build still used gen-v1; redone with `-S PS2Recomp` (configure log shows gen-v2).
- Another mistake: killing `speed_hold.py` with SIGTERM skipped its `finally`, leaving my
  own lease files (pid dead); I removed only files naming my dead pid. The holder now turns
  SIGTERM into exit so `finally` releases. It also waits while `VR1/BUILDING` exists so my
  own builds never overlap my speed boots.
- Suite g4 616/616.

## 10:53 speed hold A (base, g4), exclusive, host load ~3
`speed_hold.py holdA 0 base g4`: waited 451 s for all four slots, hold 157 s.
s1-base 14.79 vs/s (0.247×, n=8 samples in (1800,2400]); s2-g4 21.92 (0.366×, n=5) → 1.48×.
(My first wait loop matched "holding…" instead of "hold <s>"; fixed.)

## 11:01 speed holds B–D; attribution
Holds B (g4, base), C (g, g3), D (g3, g), each ~150 s, host load 2.9–4.2
(`speed-all.txt`): base 14.79/14.90, g4 21.92/20.97 → **1.44×** (0.248× → 0.358×);
g 18.48/18.36 (1.24×), g3 19.56/20.47 (1.35×). Runner SHAs in `binaries-sha.txt` match
the speed_table prefixes. Fork `6c2de6f`: Android `-Pps2xVu1RecompDir`.
Next: g4 profile; CPU-backend null pair (h-base-cpu vs h-base-cpu-2) to see whether E57's
strict whole-file GS check is deterministic there, plus h-g4-cpu.
