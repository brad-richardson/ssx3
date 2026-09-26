# VR4 — make VU1 blocks cheaper on the MTVU unit thread

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/VR4.md`, 2026-09-26 from 06:10 EDT.
**Stage 1 (assembly read + design) only. Stopped for the gate.** No code, no builds, no boots,
no device use. The receipts are text; generated code, disassembly and listings stay in scratch
(`~/dev/ssx3-work/VR4/asm/`, `SHA256SUMS` there).

## Headline

- **The FMAC core, not register traffic, is where the unit thread spends its VU1 time.**
  - The FMAC core is `execUpperImpl`: operand normalization, the float op, the exact double
    result and its classification, product sticky, and flag assembly.
  - It takes **63.6 % of B2a10's samples, 77.0 % of B0628's and 80.4 % of B0a58's**.
  - Over all generated VU1 code on MTVU it is **13.0 of 21.6 ms per guest frame**. That is
    **43 % of the unit's 30.1 ms running time**.
- **What RV4 §2's residency targets is small.** Scoreboard reads, VF/ACC snapshot and revert
  copies, sequence and ready-cycle stores, pc/branch/halt state, the per-pair cycle step, the
  vf0/vi0 stores and block glue come to **≈ 6.6 ms per frame over all generated code**, and
  about two thirds of that is inside blocks. In the three hot blocks it is 15–30 % of samples.
  Removing half of the in-block part gives **≈ 2–3 ms per frame**.
- **Why the FMAC core is expensive.** Per lane:
  - each operand is normalized **three times**: in `execUpperImpl`, again in
    `calculateFmacExactResults`, and again in `calculateFmacProductSticky`;
  - each normalization is a branchy sequence of about 6 instructions (`ubfx`, `cbz`,
    `cmp #0xff`, `b.ne`, fix-up), and the compiler does not merge the copies;
  - the exact-result classification is a three-way branch per lane;
  - product sticky repeats the double products that the exact result already computed.

  All of it is scalar, one lane at a time. Normalization appears in 29 % of FMAC-core samples,
  product sticky in 23 %, result classification in 33 %, and flag assembly in 13 %.
- **The Mac and Odin code have the same shape.** Instruction counts are within 3–4 %, and the
  `ubfx`/`fcvt`/`fcmp`/`bl`/`cbz` counts are identical (`macshape.txt`). A Mac A/B should
  transfer in kind, but not in size.
- **Design decision (for your gate).** Stage 2 starts with **D1: an exact SIMD FMAC core.**
  - All four lanes are normalized once. The float op, the exact double results, the
    classification and product sticky are branchless vector code, and the products are shared.
  - The change is in the runtime headers only, so the images are unchanged. It applies to
    blocks, pair functions, the interpreter and VU0.
  - It sits behind a compile-time switch, and a unit test compares it bit for bit against the
    unchanged scalar reference.
  - **D2 comes second:** block-static pc/branch/halt state, the cycle count kept in a local, and
    exit-only bookkeeping. It is the residency-lite part of RV4's sketch, and the block version
    stays behind `PS2X_VU1_BLOCKS`.
  - Full VF residency across the block (RV4 §2 "queue") is deferred until the post-D1 profile
    shows the copy slice matters. Reasons are below. **Your call.**

## Method and inputs

| Item | Value |
| --- | --- |
| Odin code | the play build's unstripped `libps2EntryRunner.so` (VR3 build on bytesize, SHA `01fceae5…2273ea`, BuildID `837d7dbb…14fa` = play APK `825b436d`, `-O3` per BA1/F7), disassembled with NDK 28.2 `llvm-objdump` |
| Samples | CP1 R2b `perf-R2b.data` (on bytesize, 106.8 MB), cpu-clock, MTVU tid 30588 and GameThread 30578, 405 record frames; read with NDK `simpleperf_report_lib` (`iphist*.py` in scratch) |
| Source attribution | every sampled address in the `.so`, 34,994 of them, plus every instruction of the three hot blocks, symbolized with `llvm-symbolizer --inlining` (JSON). Each instruction is mapped to its innermost inlined function and to the `issuePair` source line that inlines it (`regions.py`: ranges of `ps2_vu1_step_impl.h` at `5d5c382`) |
| Mac code | the two hot images compiled with the Mac build's exact flags (`clang++ -O3 -std=gnu++20 -ffp-contract=off -arch arm64`, fork `5d5c382` headers, canonical `vu1gen-ssx3`) to `-S` |
| Member offsets | `offsetof` on the fork header (arm64): `x23 = vu`, `x22 = vu+0x30a30` (ready tables, `m_cycle` at `+0x968`), `x24 = &m_state.acc`, `x25 = &m_accReady` |

Units: ms per guest frame = sampled seconds ÷ 405 × 1000. This is diagnostic profiler time, not
a speed number.

## Table 1 — MTVU on-cpu by class (ms per guest frame; `threadshare.txt`)

The unit's on-cpu time is 30.1 ms per frame (CP1 Table 2). The sampled total of 49.5 includes
~19 ms of off-cpu sleep PCs, which land in the kernel row.

| Class | ms/frame |
| --- | ---: |
| **Generated VU1: FMAC core (`execUpperImpl` subtree)** | **13.03** |
| Generated VU1: `issuePair` state/scoreboard (all other `issuePair` lines) | 6.30 |
| Generated VU1: block/pair glue (`next`, trampolines, `recompBlockReady`, stop checks) | 1.58 |
| Generated VU1: lower exec | 0.72 |
| `commitReadyPipelines` (out of line) | 1.30 |
| `processVIF1DataImpl` | 0.86 |
| `progressXgkick` | 0.68 |
| libc | 1.15 |
| kernel on-cpu (≈ 22.2 kernel rows − ~19 off-cpu) | ≈ 3 |
| Generated code by kind: block bodies `B*` / pair functions `f*` / trampolines `b*` | 14.96 / 6.43 / 0.23 |

GameThread for scale: the interpreted VU0 FMAC core is **1.71** and its `issuePair` state
**1.37 ms/frame**. D1 speeds up the VU0 FMAC core as well.

## Table 2 — the generated-code state slice by `issuePair` region (MTVU, ms/frame)

This is what RV4 §2's residency and static state could reach.

| Region | ms/frame | Residency / static-state effect |
| --- | ---: | --- |
| pc / branch / halt tail | 1.51 | inside a block these are compile-time facts: pc = leader + 8·i; no branch pending before the branch pair; E/halt clear under the guard |
| `advanceOneCycle` (`++m_cycle`, `m_state.cycles` store, the commit and XGKICK tests) | 1.08 | the cycle can live in a register; the two tests and their calls stay per cycle (exact PATH1 and commit timing) |
| revert + commit writes (`directVf/Acc/ViWrite`, copies) | 1.17 | copies disappear once results are written once; sequence and latest-write stores are needed only at exit, and only when no queued write can land in between |
| stall / scoreboard (`calculatePairReadyCycle`) | 0.64 | already skipped in `noStall` pairs; what remains is live-in reads, needed |
| `markPairWrites` | 0.35 | exit-only when no in-block reader |
| direct-map setup, counters, vf0/vi0 stores, post-exec clears, snapshot | 1.15 | mostly constant-foldable in blocks |
| **total** | **≈ 5.9** (+ glue 0.76) | ≈ 2/3 of it is in blocks (`B*` = 15.0 of 21.6 ms of generated code) |

## Table 3 — the three hot blocks (`attr-blocks.txt`)

These are CP1 Table 3's blocks. Samples are this block's MTVU self samples.

| Block (image) | Insns (Odin) | Samples | FMAC core | lower exec | state + glue | stack spills (sp/x29 mem ops) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B2a10 (`f587…`, 9-pair loop) | 4,429 | 890.8 ms | **63.6 %** | 6.3 % | ≈ 30 % | 252 ops, 6.9 % of samples |
| B0628 (`a564…`) | 9,258 | 600.8 ms | **77.0 %** | 1.6 % | ≈ 21 % | 678 ops, 12.1 % |
| B0a58 (`f587…`) | 8,263 | 344.2 ms | **80.4 %** | 0.5 % | ≈ 19 % | 604 ops, 9.7 % |

**What B2a10 is.** It is a 9-pair vertex loop:

- MULAx, MADDAy, MADDAz and MADDw, i.e. a matrix × vector into ACC;
- `DIV Q, vf0w, vf6w`, then MULq ×2 and FTOI4, ITOF15 and ITOF12;
- LQI ×3 and SQI ×3, with an IBNE back edge and an SQI in its delay slot.

The Q written by each iteration's DIV lands 7 cycles later, in the middle of the next
iteration, through `commitReadyPipelines`. So the out-of-line commit runs once per vertex.

**FMAC-core split over all MTVU generated code (13.03 ms/frame):**

| Part | ms/frame | Share |
| --- | ---: | ---: |
| `normalizeFmacResult` (exact double + classification) | 4.32 | 33 % |
| `calculateFmacProductSticky` | 2.97 | 23 % |
| own code (operand loads, float op, decode) | 2.50 | 19 % |
| `updateFmacFlags` | 1.64 | 13 % |
| `normalizeOperand`, standalone and inside `broadcast` | 1.07 | 8 % |

`normalizeOperand` appears somewhere in the inline chain of 3.76 ms/frame, which is 29 %.

## Assembly read (Odin and Mac)

- **What stays in registers.** Within one pair, the operand bits and the lane results stay in
  registers. Across pairs, nothing does.
  - Every pair reloads its VF/ACC lanes from `m_state`, `m_cycle` (`[x22,#0x968]`) and the
    ready rows.
  - Every pair stores `m_currentUpperInstruction`, the `m_directStores`/`m_directFlags`
    halfword, the new VF lanes, their `m_vfLatestWrite` rows, `m_nextWriteSequence`, the ready
    rows, pc, `m_state.cycles` and vf0/vi0.
- **Stack traffic.** Scalar 4-lane processing needs more registers than the core has. The
  compiler also keeps the local arrays in memory: the old/new VF copies, `result[4]`,
  `laneFlags[4]` and `exactResults[4]`. Together these make 250–680 sp-relative memory
  operations per block, 7–12 % of block samples.
- **Opaque calls.** B2a10 contains 9 `commitReadyPipelines` and 9 `progressXgkick` call sites,
  one of each per pair in `advanceOneCycle`. There are also 4 `advanceTo` stall calls, 6
  `recordViWriteForBranch`, 2 `readBranchVi`, and 6 cold `reportReservedInstruction` (flag
  queue full). Because of these calls, `m_cycle` and every `m_state` field must be in memory
  at every cycle boundary. That is what defeats the compiler's register allocation across
  pairs today. It is also why residency can only be implemented with locals the callees cannot
  see, plus guards that no queued VF/VI/ACC write lands inside the block (the calls commit
  those into `m_state`).
- **Stack protector.** Every block function has a canary (`mrs TPIDR_EL0` … `__stack_chk_fail`),
  because of its local arrays. At ~0.4 % of B2a10 it doesn't matter.
- **Mac vs Odin** (`macshape.txt`):

  | Block | Mac insns | Odin insns |
  | --- | ---: | ---: |
  | B2a10 | 4,307 | 4,429 |
  | B0628 | 8,874 | 9,258 |
  | B0a58 | 8,097 | 8,263 |

  The `ubfx`/`fcvt`/`fcmp`/`bl`/`cbz+cbnz` counts are equal to ±2. Same code, same bottleneck.

## Design (stage 2 plan, for your decision)

### D1 — exact SIMD FMAC core (first; the largest lever)

- **Scope.** All upper ops that end in `applyFmacDest`/`applyFmacDestAcc`, i.e. the set where
  `calculateFmacExactResults` has an exact form:
  - ADD/SUB/MUL/MADD/MSUB in the bc, q, i and vector forms, and their ACC (`…A`) forms;
  - OPMULA/OPMSUB.

  MAX/MINI, ABS, FTOI/ITOF, CLIP and the lower ops keep their scalar code.
- **Form.** A new header, `ps2_vu1_fmac_simd.h`, written with clang/GCC vector extensions
  (`float4`, `uint4`, `double2`, `__builtin_convertvector`). Every build host is clang: Mac,
  NDK, iOS, and bradflix's clang 18 with `-msse4.1`.
  1. Load vs, vt and acc as 16-byte vectors (the rows are not 16-byte aligned; use unaligned
     loads via memcpy). Normalize all four lanes once:
     `exp==0 → sign; exp==0xFF → sign|0x7F7FFFFF`, as two compares and selects.
     Broadcast bc/q/i after normalizing.
  2. Compute the float result in the same expression order, e.g. `acc + vs*bc`; no FMA, since
     `-ffp-contract=off` applies to vector ops too.
  3. Compute the exact result per two-lane half in double, in the same order as
     `calculateFmacExactResults`. The float×float product is exact in double.
  4. Classify branchlessly and override values exactly as `normalizeFmacExactResult` does:
     zero → Z and ±0; `>FLT_MAX` → O and ±MAX; `<FLT_MIN` → U|Z and ±0; sign → S.
  5. For product-sum ops, compute product sticky from **the same double products**, with the
     same classification: OR of `flags & 0xF` over the dest lanes.
  6. Build MAC and status with constant lane masks and a horizontal OR.
  7. Then run the **unchanged** commit tail (`directFlagsNow`, the demote/queue paths,
     `noteDirect`) and `applyDest` with the constant dest.
- **Knob.** Compile-time `PS2X_VU1_FMAC_SIMD`, a CMake option that is **default OFF** on the
  branch until your gate. A runtime switch would put a branch in every FMAC.
  - This is a pure refactor, so the bar is det-IDENTICAL against the current key with no
    re-baseline.
  - The scalar code stays in the tree, unchanged, as the reference. `execUpperImpl` takes a
    `kSimd` template parameter, so one test binary can run both forms.
  - MSVC and `PS2X_VU_WIDE_QUAD=1` builds keep the scalar form.
- **Correctness model.** For every FMAC op, dest mask and operand bit pattern, D1 produces the
  same result bits, ACC, MAC, status (incl. sticky 6–11), flag-pipeline entries,
  `m_directPendingUntil` and cycle as the scalar form, on both the direct and queued flag paths.
- **Exactness gates.**
  1. A new unit test: the SIMD form against the scalar form. It covers:
     - every opcode in scope, all 15 dest masks;
     - operand classes ±0, ±denormal, ±Inf/NaN bit patterns, the neighbourhoods of FLT_MIN
       and FLT_MAX, sums and products that straddle the overflow and underflow thresholds,
       and random normals (≥ 10⁶ cases per op family);
     - random pre-set sticky bits and queued flag entries (direct and queued paths, queued
       FSSET).

     It compares every output field bit for bit.
  2. The suite, and VR2's differential test with 0 mismatches.
  3. det-hash IDENTICAL on bradflix with blocks on and off, a 512 KB stack, and VU1 100 %
     generated.

  The route exercises ~1 G VU1 cycles of real data through the new core. VU0 also runs through
  it (interpreted on GameThread), so the det gate covers VU0 too.
- **Expected.** A guess until built. D1 replaces roughly 250–400 scalar, branchy instructions
  per 4-lane FMAC with an estimated 60–90 mostly vector instructions. If the FMAC core halves:
  - MTVU running time drops by ~6.5 of 30.1 ms per frame;
  - GameThread's VU0 FMAC drops by ~0.8.

  On the Mac, VR2's c4 profile (before blocks) had VU1 at ~57 % of busy samples and the
  generated functions at 36 %. If ~60 % of the generated code is FMAC core and it halves, that
  is **~1.08–1.15× on the race**. On the Odin the frame gain is smaller than the thread gain,
  because the unit also waits 12.2 ms per frame on GameThread and 6.7 ms on the GS queue
  (CP1).

### D2 — block static state and residency-lite (second; emitter, new images, block v2 behind `PS2X_VU1_BLOCKS`)

- **Static tail.** Inside a block, a `kBlockTail` form of `issuePair` drops the
  branch-pending, E-bit and halt tests and the pc arithmetic. pc is stored once before each
  exit and before any out-of-line call that reads it. It skips the `m_directStores`/
  `m_directFlags` stores between pairs that don't use them, and the vf0/vi0 stores after pairs
  that can't write them. That is ≈ 1.5 ms of Table 2.
- **Cycle in a local.** The block keeps `cyc` in a register. `m_cycle` and `m_state.cycles`
  are written before a `commitReadyPipelines`, `progressXgkick` or `advanceTo` call and at
  every exit. The per-cycle tests against `m_nextCommitCycle` and `m_xgkick.active` stay, so
  commit and PATH1 timing are unchanged.
- **Exit-only bookkeeping.** This is guarded at entry by "no queued VF/VI/ACC writes"
  (`m_vf/vi/accWriteValidMask == 0`) and needs every in-block VF write to be direct (map bits;
  true for the hot blocks). Under it:
  - the `m_vfLatestWrite`, `m_accLatestWrite` and `m_viLatestWrite` stores and
    `m_nextWriteSequence` are emitted once per register at exit, with the values the per-pair
    path would have left;
  - `markPairWrites` stores are emitted once per lane at exit, except where an in-block
    scoreboard read needs them.

  On a guard miss the block uses the v1 path, which is today's code. That is ≈ 1–1.5 ms.
- **Knob.** Stays behind `PS2X_VU1_BLOCKS`, as a new block version in the emitter. The images
  are regenerated by a dump boot, and the same 7 hashes are expected.
- **Why not full VF residency now.** After D1 the VF operands are loaded once per op as a
  vector, and results are stored once per op. Residency would save those loads and stores and
  the revert copies. But it needs:
  - locals the callees cannot see;
  - guards on every queued write that could land in the block;
  - exit spills on every stop path (`m_stopRequested` after each pair,
    `reportReservedInstruction`).

  For about 1 ms per frame on the current profile, that is the riskiest part of RV4's sketch.
  Re-read the profile after D1; if the copy slice has grown to matter, it becomes D3.
- **Not chosen:**
  - **Skipping product sticky or flags.** It is a semantic change, not a timing one, and the
    brief says exact.
  - **Known-normal operand tracking in the emitter.** It skips normalization of in-block FMAC
    results. After D1, normalization costs ~2 vector instructions per operand, so the gain is
    gone.
  - **A `commitReadyPipelines` fast path for the lone-Q landing.** It is 1.3 ms per frame and
    a separate small lever. Noted for later.

### Stage-2 budget and measurement

- **Builds (≤ 10 total, stage 3 included):**
  - Mac tests: ≤ 3;
  - Mac runners: D1 and base, or reuse an existing `5d5c382` canonical runner if its SHA
    matches; +1 for D2;
  - D2 dump runner: 1;
  - bradflix det: ≤ 2;
  - Android (stage 3): 1.
- **Speed.**
  - Mac ABBA with VR2's `speed_hold.py` on an exclusive, quiet host (all four slots, load and
    `ps` checked): base vs D1, then D1 vs D1+D2.
  - Odin: one pair with MTVU and blocks on, play APK `825b436d` vs the VR4 APK, under
    `odin_lease.sh`, coordinated with FS2.

  Each lever is its own commit with the same gates.

## Exact commands (stage 1)

```sh
git -C ~/dev/PS2Recomp worktree add -b vr4 ~/dev/ssx3-work/VR4/PS2Recomp 5d5c382   # read-only so far
# Mac asm (flags from VR3/build-fold compile_commands.json, -S instead of -o .o, no -flto)
clang++ -O3 -DNDEBUG -std=gnu++20 -arch arm64 -ffp-contract=off -DPS2X_ENABLE_DET_HASH_TAP=0 … -S -o asm/mac-<img>.s ~/dev/ssx3-work/vu1gen-ssx3/vu1_<img>.cpp
# bytesize (scripts piped to `wsl -d Ubuntu -- bash -s`): symbols, disassembly, samples, inline chains
llvm-nm -C -S $SO | grep 'VU1RecompImage<…>::(B2a10|B0628|B0a58|…)'
llvm-objdump -d --no-show-raw-insn --start-address=… --stop-address=… $SO > odin-<img>-<blk>.s
python3 iphist.py; python3 iphist2.py     # simpleperf_report_lib over /home/brad/cp1/prof/perf-R2b.data
llvm-symbolizer --obj=$SO --inlining --functions=short --demangle --output-style=JSON < *.addrs > *.sym.json
# mini
python3 local/research/VR4/attribute.py asm/iphist.txt asm/odin-<blk>.s asm/odin-<blk>.sym.json   # -> attr-blocks.txt
python3 local/research/VR4/threadshare.py asm/iphist-all.txt asm/all.sym.json                        # -> threadshare.txt
python3 local/research/VR4/macshape.py                                                                # -> macshape.txt
```

## Gaps

- The attribution is sampled cpu-clock. Skid can move a sample by a few instructions, which
  blurs region edges (e.g. `issuePair:0` rows, the compiler's line-0 code) but not the
  64–80 % FMAC-core result.
- The D1 and D2 gains are estimates, stated as such. They depend on the SIMD code the compiler
  actually emits, which I'll check in the stage-2 assembly before any speed run.
- No dynamic opcode census was taken. The FMAC-core share is measured directly, so none is
  needed to justify D1.
- The GameThread VU0 numbers come from the same R2b window. VU0 runs interpreted there, since
  `PS2X_VU0_RECOMP` is off in the play env.
- Budgets used: 0 builds, 0 boots, 0 device time. The scratch is `~/dev/ssx3-work/VR4`,
  ~165 MB (asm, JSON and the worktree).
