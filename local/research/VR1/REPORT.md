# VR1 — VU1 static recompilation, stage A

Worker: Claude Code (Opus 5.5), exploratory, brief `local/muse/prompts/VR1.md`. Box
09:48–12:48 EDT 2026-09-25, Mac mini only. Tables and receipts; the orchestrator decides.
No push, no Odin, no devices.

## Headline

- **Stage A works and is bit-exact on the gate that can discriminate on this build.** SSX 3's
  VU1 code images become generated C++, one function per pair PC, keyed by XXH64 of the
  code memory. Across all candidates (r, g, g2, g3, g4, g5): suite 616/616, all 2,400 `[det-hash:v1]` lines
  equal to base `0ed07c4`, GS content equal per path. **100 % of VU1 cycles run in
  generated code** on the I26-FAST route to t2400. Total VU1 cycles are identical to the
  interpreter's (959,411,166).
- **On the CPU GS backend, g4 passes E57's strict gate unchanged**: whole-file GS capture SHA
  equal (`f2233e7e…`, null control also equal). On the paraLLEl Mac build the strict check
  fails its own null control (base vs base): record tick stamps and cross-path interleave
  race. Per-path payload sequences (tick stripped), VBlank, privileged writes and transfers
  are deterministic there, and all candidates match on them (`gs_types.py`).
- **Race speed on the Mac mini (M5 Pro), diagnostics off, paraLLEl, exclusive lease, ABBA:
  14.85 → 21.45 guest vsyncs/s (0.248× → 0.358× of 59.94), 1.44× on the whole game** (g4,
  fork `1f51e48`; base 14.79/14.90, g4 21.92/20.97). Stage A as sketched (g) gives 1.24×;
  inlining the FMAC helpers (g3) takes it to 1.35×; chaining pairs (g4) to 1.44×.
- **VU1 share (diagnostic `sample`, process-wide busy samples):** 82.5 % (base) → 70.7 %
  (g2) → 62.5 % (g4). The decode, usage lookup, opcode switch and FMAC re-decode are gone.
  What's left is the scoreboard (`commitReadyPipelines`) and the FMAC exact-result
  arithmetic. That's stage B territory.
- **Recommendation:** **ready for an Odin speed pair**; the orchestrator decides. Fold
  `0ed07c4..1f51e48` plus `6c2de6f` (Gradle); leave g5 `8cea160` out (bit-exact, not shown to
  help). Build the APK with `-Pps2xVu1RecompDir=<copy of gen-v2>`: game-derived, so copy it privately to
  bytesize and never into a repo. Run a clean pair vs the F2 APK. Odin VU1 is
  62.8 + 25.7 of 121 ms (NP1), and the Mac game thread is now just as VU1-bound
  (82.5 % base), so the Mac 1.44× is a fair first guess at the relative VU1 gain there.
  NP1 Part 2's memset/`-Bsymbolic` work is orthogonal, with a trivial textual overlap in
  `ps2_vu1.h`. Before shipping to players: dump images on more routes (other courses) or
  accept interpreter fallback there.

## Design

| Piece | What | Where (fork) |
| --- | --- | --- |
| Shared pair step | `run()`'s loop body moved verbatim into the always-inline template `issuePair<kStatic>(const DecodedInstructionPair&, RunContext&)`, together with `calculatePairReadyCycle` and `markPairWrites`. The interpreter calls it with its decode-cache entry (`kStatic=false`, out-of-line `execUpper/execLower`). Generated code calls it with a `static constexpr` pair (`kStatic=true`, always-inline executors). Scoreboard, commit, stall and cycle rules are one copy of the code. | `ps2_vu1_step_impl.h` |
| Executors | `execUpper`/`execLower` bodies moved verbatim into always-inline `execUpperImpl/execLowerImpl`. The `.cpp` keeps out-of-line wrappers for the interpreter. With a constant word, the opcode switch folds. | `ps2_vu1_{upper,lower}_impl.h` |
| FMAC helpers (g3) | `normalizeFmacResult`, `calculateFmacExactResults`, product sticky, flag queueing, `applyFmac*`, `applyDest`, `broadcast` moved verbatim into an always-inline header. The upper word that `execUpperImpl` stores in `m_currentUpperInstruction` forwards as a constant, so the op re-decode and dest-lane loops fold. | `ps2_vu1_fmac_impl.h` |
| Keying | `lookupRecompProgram()` at each `run()`: VU1 only, code pointer must be the memory's VU1 code; XXH64(code, codeSize) recomputed only when `getVU1CodeGeneration()` changes (the same trigger as the decode cache); registry hit also requires an equal `codeSize`. The key equals the det-hash `vu1Code` field. | `ps2_vu1_recomp.cpp` |
| Entry points | One function per pair PC (every pair that decodes without a reserved op: all 2,048 in each of the 7 images). So `execute()`, `resume()`/MSCNT and budget truncation at 65,536 cycles can enter or leave at any pair. `run()` dispatches through the image's table per pair. | emitted |
| Chaining (g4) | Each pair function ends with `next()`. It runs the `run()` loop header in the same order (budget/stop, commit, pc bound/alignment), then `[[clang::musttail]]`-calls the next pair's function from the table. A null entry returns to `run()`. | emitted + `recompChainReady` |
| Fallback | Unknown image, VU0, untracked code pointer, unaligned PC, reserved pair (null table entry), `PS2X_VU1_RECOMP=0`: the interpreter, unchanged. | `run()` |
| Generation | `PS2X_VU1_RECOMP_DUMP=<dir>` makes the runtime emit `vu1_<hash>.cpp` for each image it meets without generated code, using the interpreter's own `decodeInstructionPair`. `PS2X_VU1_RECOMP_DIR` (CMake; Android `-Pps2xVu1RecompDir`) compiles them into `ps2EntryRunner` (no unity, no PCH); static initializers register them. Generated files are derived from game data and live in `~/dev/ssx3-work/VR1/gen-v2`, outside every repo. | CMake, Gradle |
| Stats | `PS2X_VU1_RECOMP_STATS=1`: every 16,384 VU1 runs, cumulative generated vs interpreted VU1 cycles (two counters, always maintained). | `ps2_vu1_recomp.cpp` |

Per image: 6.2 k lines, ~8 s compile, 2,048 pair functions (median ~305 asm lines after g3).
Seven images for boot → race on I26-FAST.

## Fork commits (`~/dev/ssx3-work/VR1/PS2Recomp`, local branch `vr1-vu1-recomp` from `0ed07c4`)

| # | Commit | Change | `--stat` |
| --- | --- | --- | --- |
| g (stage A) | `00381ff` | shared inline pair step, inline executors, registry/keying/emitter, CMake option | 10 files, +1982/−1597 (mostly verbatim moves) |
| g2 | `71fda22` | E37 entry-trace snapshot (576 B zeroed per pair on the stack) → members; `microAddressMask` inline | 3 files, +12/−11 |
| g3 | `1b09a49` | FMAC result helpers always-inline (verbatim move) | 5 files, +320/−299 (verbatim move) |
| g4 | `1f51e48` | chained pairs via `musttail` (emitter + `recompChainReady`) | 4 files, +39/−6 |
| — | `6c2de6f` | Android `-Pps2xVu1RecompDir` | 1 file, +4/−1 |
| g5 | `8cea160` | `advanceOneCycle` inline, commit gate at call sites | 2 files, +17/−12 |

Branch total `0ed07c4..8cea160`: 12 files, +2361/−1913 (most of it verbatim moves into
the three `*_impl.h` headers).

Runner-dir guard (`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) is empty at every
commit. Commits carry `Orchestrated-By: Claude Code`. Nothing outside VU1 files, CMake and
the Gradle property.

**Overlap with NP1 Part 2** (branch `np1-link`, VU1 execute's per-call memset): VR1 doesn't
touch `execute()` or `resetScheduler()`. g2 removes a different clear: the per-pair
zero-init of the dev-only entry-trace snapshot inside the `run()` loop body, which NP1's
callers table puts under "VU1 run 0.54 %". Both touch `ps2_vu1.h` members; the textual
conflict should be trivial. `-Bsymbolic` is orthogonal.

## Acceptance

Base = `0ed07c4` built from `git archive` (`base-src/`), so candidate edits never reach it.
Boots: `vr1_boot.py --mode hash` (E57 driver + F2's Mac env: `PS2X_GS_BACKEND=parallel`,
`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`, `PGS_HIER_BINNING=force`),
`PS2X_DETERMINISTIC=1`, `PS2X_SKIP_MOVIE=1` (dev-only), I26-FAST vsync pad script, empty mc0/mc1,
`PS2X_DET_HASH_EVERY=1`, GS capture to t2400, sound off. One mini slot each. ISO `3c2f8eb1…`
and ELF `1b49d05c…` read twice before each boot.

| Pair | Suite | det-hash t1–2400 | GS whole-file SHA | GS per-path content (tick stripped) | Coverage |
| --- | --- | --- | --- | --- | --- |
| h-base-1 vs h-base-2 (**null control**) | 616/616/0 both | 2400/2400 equal | **differs** (record 7,348, t253) | EQUAL (path1 1,530,114; path2 275,682; path3 27,001; priv 14,049; transfer 56,958; VBlank 2,400) | — |
| base vs r (refactor, interpreter only) | 616/616/0 | equal | differs (as null) | EQUAL | 0 % (total 959,411,166 cycles) |
| base vs g | 616/616/0 | equal | differs (as null) | EQUAL | 100 % |
| base vs g2 | 616/616/0 | equal | differs (as null) | EQUAL | 100 % |
| base vs g3 | 616/616/0 | equal | differs (as null) | EQUAL | 100 % |
| base vs g4 | 616/616/0 | equal | differs (as null) | EQUAL | 100 % |
| base vs g5 | 616/616/0 | equal | differs (as null) | EQUAL | 100 % |

**Strict check on the CPU GS backend** (`--backend cpu`, same hash runners; E57's gate as
it was, whole-file SHA included), `check-cpu.txt`:

| Pair | Suite | det-hash t1–2400 | GS capture (1,906,204 records, 2,510,683,433 B) | Result |
| --- | --- | --- | --- | --- |
| h-base-cpu vs h-base-cpu-2 (**null control**) | — | equal | whole-file SHA equal `f2233e7e…` | BIT-EXACT |
| h-base-cpu vs **h-g4-cpu** | 616/616/0 | equal | whole-file SHA equal `f2233e7e…` | **BIT-EXACT** |

So the racy interleave is a paraLLEl-backend property (host timing), not a VU1 one. On the
CPU backend the full GS stream, cross-path order included, is identical with generated VU1
code.

Receipts: `check-gate.txt` (paraLLEl pairs), `check-null.txt`, `check-r.txt`, `check-cpu.txt`.
Result: **BIT-EXACT** for r, g, g2, g3, g4, g5 on the paraLLEl gate (no first differing tick),
and strict BIT-EXACT for g4 on the CPU backend.

## Speed

Mac mini M5 Pro. `build.sh base|gen speed`: Release, ThinLTO, homebrew clang,
`PS2X_ENABLE_DIAG_TAPS=OFF`, `PS2X_ENABLE_DET_HASH_TAP=OFF`, runtime/aggressive logs OFF,
paraLLEl shadow ON (F2 recipe), codegen `~/dev/ssx3-work/codegen-ssx3`. Boots: hash-boot
env minus hash/capture, plus `PS2X_VSYNC_RATE_LOG=1` and `PS2X_SOUND=1` (the F2 speed env).
Rate = mean of the 5 s `[vsync-rate]` samples whose end tick is in (1800, 2400]
(`speed_table.py`, `speed-all.txt`). Deterministic, so the guest work is the same in every run.

Exclusive lease: plain exclusive claims starved for 15 min while four other lanes cycled
single slots, so `speed_hold.py` claims each slot as it frees, then runs two boots per hold
(146–157 s per hold, under the brief's 5 min) and releases. It also waits while this lane's
own build runs. All eight runs were 10:51–11:01, with host load 2.6–4.2.

| Hold | Run | Runner sha256 (two reads match, `binaries-sha.txt`) | vsyncs/s | ÷ 59.94 |
| --- | --- | --- | ---: | ---: |
| A | s1-base | `bd2290f4…` | 14.79 | 0.247× |
| A | s2-g4 | `0800ace0…` | 21.92 | 0.366× |
| B | s3-g4 | `0800ace0…` | 20.97 | 0.350× |
| B | s4-base | `bd2290f4…` | 14.90 | 0.249× |
| C | s5-g | `99edb7df…` | 18.48 | 0.308× |
| C | s6-g3 | `7675d47b…` | 19.56 | 0.326× |
| D | s7-g3 | `7675d47b…` | 20.47 | 0.341× |
| D | s8-g | `99edb7df…` | 18.36 | 0.306× |

| Candidate | Mean vsyncs/s | ÷ 59.94 | vs base |
| --- | ---: | ---: | ---: |
| base `0ed07c4` | 14.85 | 0.248× | 1.00× |
| g (stage A as sketched) | 18.42 | 0.307× | 1.24× |
| g3 (+ g2 + FMAC helpers inline) | 20.01 | 0.334× | 1.35× |
| **g4 (+ chained pairs)** | **21.45** | **0.358×** | **1.44×** |

Later holds (11:09–11:40; host load rose between runs, so these are weaker):

| Hold | Runs (vsyncs/s) | Read |
| --- | --- | --- |
| E | s9-g4 23.32, s10-g5 19.01 (load 4.8 → 9.1 during g5) | g5 run disturbed |
| F | s11-g5 14.03, s12-g4 11.68, load 70–130 | **void** (`run/void-*`) |
| F2 | s21-g5 21.82, s22-g4 21.27 (load 3.4–4.0) | g5 ≈ g4 |
| G | s13-base 14.45, s14-g4off 14.97 (load 2.7–3.6) | interpreter-only after the refactor ≈ base (1.04×) |
| H | s15-g4off 13.00 (load reached 9.9 by its end); s16-base abandoned by the load gate | weak |

g5 vs g4 (E + F2): means 20.42 vs 22.30, but g5's low run was disturbed. **g5 is not shown to
help**, so it's not in the recommended fold. `g4off` is the g4 runner with
`PS2X_VU1_RECOMP=0`, i.e. the fallback for images that aren't compiled in. Its clean pair
with base (hold G) reads 14.97 vs 14.45, so the refactor didn't slow the interpreter. H was
cut short when the orchestrator paused speed holds (RD1/F3 needed slots). All runs,
including the extra g4 runs (overall g4 mean 21.87 across four), are in `speed-all.txt`.

Base vs g4 is a clean ABBA (holds A and B, back to back). g and g3 ran ABBA against each
other (holds C and D) in the same quiet 10-minute session, so their ratios to base cross
holds. g2 wasn't measured alone. Within a pair, runs of the same binary differ by up to
4.5 % (g4 21.92/20.97), so treat the g3 vs g4 step (~7 %) as approximate.

## VU1 profile share (diagnostic)

`sample` 20 s from t1800 on the speed runners (`vr1_boot.py --mode profile`, one slot, not a
speed number). `profile_share.py`: process-wide top of stack, busy = non-wait rows.
Receipts `profile-{base,g2,g4}.txt`. Shares are within-process; absolute counts aren't
comparable.

| | base `0ed07c4` | g2 | g4 |
| --- | ---: | ---: | ---: |
| Busy samples (20 s) | 10,423 | 8,085 | 6,140 |
| **VU1 total** (interpreter + generated) | **82.5 %** | **70.7 %** | **62.5 %** |
| generated pair functions (`VU1RecompImage<…>::f*`) | — | 9.0 % | 26.4 % (FMAC path inlined) |
| commitReadyPipelines | 16.5 % | 25.8 % | 28.0 % |
| run | 17.5 % | 6.3 % | 3.2 % |
| normalizeFmacResult / product sticky / flags | 9.8 / 3.6 / 2.3 % | 16.5 / 6.1 / 3.8 % | inlined |
| calculatePairReadyCycle / markPairWrites | 9.4 / 4.2 % | inlined | inlined |
| execUpper / execLower | 8.8 / 4.6 % | 0.9 / 0.4 % (VU0) | 2.3 / 0.5 % (VU0) |
| getDecodedInstructionPairForPc + decode | 4.1 % | 0.4 % (VU0) | 0.3 % (VU0) |
| progressXgkick | 0.8 % | 1.5 % | 1.7 % |
| `__bzero` (per-execute clear, NP1 Part 2's target) | 2.2 % | — | 4.3 % |

On the paraLLEl Mac build the GS work is off the game thread, so VU1 dominates (82.5 %; E57's
CPU-GS profile showed 33 %). Stage A removed decode, usage lookups, dispatch and the FMAC
re-decode. The scoreboard commit is now the largest single item.

## What stage B would add

After stage A the VU1 cost is the timing model itself plus FMAC arithmetic.
`commitReadyPipelines` alone is ~26 % of busy samples in g2. Stage B (E57 sketch step 3)
would, per basic block of each image:
1. Precompute stalls and write-back cycles from an assumed entry scoreboard (all ready),
   with a guard comparing the live scoreboard (`m_vfReady/m_viReady/m_accReady`, FDIV/EFU
   state, pending masks) against the assumption. On a mismatch, run the block through the
   stage-A pair functions (already exact, so the fallback is fast).
2. Replace the queue/commit round trip for writes that no instruction in the block reads
   before they land with direct register writes at the known cycle. Flag-pipeline
   visibility (FMAND/FSAND/FCAND, the branch-VI backup, Q/P via WAITQ/WAITP, LSU commit
   before PATH1 consumes a qword, XGKICK per-cycle progress, E/D/T-bit delay slots) stays
   on the queue path.
3. Keep `advanceOneCycle` per cycle only while an XGKICK is active; otherwise advance
   `m_cycle` by the block's precomputed length.
Validation needs a per-program differential harness (captured VU1 state + data memory in,
VU state + data memory + GIF bytes out) before the first block is scheduled. Estimate 3–5
days, as E57 said.

## Gaps

- Mac only. The Odin pair (fork `1f51e48`+`6c2de6f`, `-Pps2xVu1RecompDir=<gen-v2 copy>`) hasn't
  been built or run. Android uses the same `-ffp-contract=off`; `musttail` is clang-only
  (the NDK is clang; MSVC would fall back to an ordinary call).
- On the paraLLEl build the GS capture's record ticks and cross-path interleave race (null
  control), so that gate compares per-path content only. The strict whole-stream check was
  run on the CPU backend for g4 only (it passed). g, g2 and g3 have only the paraLLEl gate.
- Coverage is measured on one route (I26-FAST to t2400: boot, menus, one race). Other
  courses or modes may upload other microcode images. Those run in the interpreter
  (correct, slower) until a dump boot on that route adds them. The image set is keyed by
  exact code bytes, so a patched or relocated program is a new image.
- Generated files aren't produced by the build. A dump boot (or a copy of `gen-v2`) is a
  manual step. They're derived from game data and must stay outside every repo.
- No per-program differential unit test; the whole-game gate plus the verbatim-move
  argument stand in for it.
- VU0 still runs in the interpreter (the residual execUpper/decode rows in the g profiles).
- Profiles are process-wide top of stack (`sample`), not per thread.
- Generated code adds ~4 MB of machine code per image (Mac runner 135.1 → 162.7 MB), because
  every one of the 2,048 pairs is emitted, including stale data in code memory. Emitting
  only statically reachable pairs from observed start PCs would cut that; not done.
- Scratch: VR1 grew to 39 GB against the 20 GB brief cap (2.5 GB per GS capture, not
  deleted after each check). Pruned to 7.3 GB on the orchestrator's request (NOTEBOOK
  11:18). The kept reference capture is `run/h-base-cpu/gs.cap`.

## Commands and pins

- Fork worktree `~/dev/ssx3-work/VR1/PS2Recomp`, branch `vr1-vu1-recomp` (`0ed07c4..8cea160`,
  not pushed). Base source `~/dev/ssx3-work/VR1/base-src` = `git archive 0ed07c4`.
- Builds: `~/dev/ssx3-work/VR1/build.sh base|gen hash|speed` (copy in this dir).
  paraLLEl-GS `~/dev/ssx3-work/F2/parallel-gs` @ `19d93b2` (read-only), codegen
  `~/dev/ssx3-work/codegen-ssx3` (`register_functions.cpp` `8ea8ed43…`), generated VU1
  images `~/dev/ssx3-work/VR1/gen-v2` (7 files, SHAs `gen-v2.sha`). Binaries in
  `~/dev/ssx3-work/VR1/bin/`, SHAs `binaries-sha.txt` (two reads match).
- Regenerate images: boot any VR1 runner with `PS2X_VU1_RECOMP=0
  PS2X_VU1_RECOMP_DUMP=<dir>` over the route to cover, then `cmake -S PS2Recomp -B <build>
  -DPS2X_VU1_RECOMP_DIR=<dir>` (Android: `-Pps2xVu1RecompDir=<dir>`).
- Suites: `cd ~/dev/ssx3-work/VR1/PS2Recomp && ../bin/tests-<c>-hash > ../suite-<c>.log`.
- Hash boots: `vr1_boot.py --mode hash [--backend cpu] --runner bin/runner-<c>-hash --label
  h-<c> [--env PS2X_VU1_RECOMP_STATS=1]`. Checks: `check.py --base run/h-base-1 --cand
  run/h-<c> --base-suite suite-base.log --cand-suite suite-<c>.log` plus `gs_types.py
  run/h-base-1/gs.cap run/h-<c>/gs.cap`.
- Speed: `speed_hold.py hold<X> <start> <candA> <candB>`, then `speed_table.py run`.
  Profiles: `vr1_boot.py --mode profile --runner bin/runner-<c>-speed --label p-<c>
  --stop-tick 2000 --sample-at 1800 --sample-s 20`, then `profile_share.py`.

## Orchestrator gate (2026-09-25)

**Pass.** Stage A: SSX 3's 7 VU1 images become generated C++ (one function per pair, keyed by XXH64 of
code memory, interpreter fallback for anything unknown), 100 % of VU1 cycles in generated code on the
route, total VU1 cycles identical, det-hash 2,400/2,400 equal, strict whole-file GS SHA equal on the CPU
backend (paraLLEl's strict check isn't deterministic even base vs base; per-path content equal). Mac
race **0.248× → 0.358×** (1.44×, ABBA, exclusive). Fold `0ed07c4..1f51e48` + `6c2de6f` (Gradle), not
g5, in **F4** (after F3, which was mid-build), with an Odin speed pair and an iPhone build. The generated
VU1 sources are game-derived: promote `gen-v2` to `~/dev/ssx3-work/vu1gen-ssx3` (outside any repo, like
the codegen), copy privately to bytesize for APKs, never commit. Other courses may hit the interpreter
fallback until their images are dumped.
