# VB1 — VU1 stage B: commit at issue (static per-pair maps + guards)

Worker: Claude Code (Opus 5.5), exploratory, brief `local/muse/prompts/VB1.md`. Box
12:12–15:12 EDT 2026-09-25, Mac mini only. Tables and receipts; the orchestrator decides.
No push, no Odin, no devices.

## Headline

- **What stage B became.** After VR1, `commitReadyPipelines` alone was 28 % of busy samples
  (≈ 45 % of VU1 time); the stall computation was already cheap (constant usages, inlined).
  So VB1 attacked the queue→commit round trip, not the stall calculation: writes are applied
  **when the pair issues** wherever a static per-pair map and a runtime guard show that no one
  can tell the difference. No precomputed stall tables (sketch step 1) were built; see
  "What's left".
- **Bit-exact** (final candidate d4 `9638b3d`): suite 617/617 (616 + a new differential
  case), det-hash 2,400/2,400 equal, **strict CPU-backend GS SHA equal** (`f2233e7e…`,
  1,906,204 records, `check-d4-cpu.txt`), paraLLEl per-path GS content equal (the whole-file
  check isn't deterministic on paraLLEl even base vs base, as VR1 showed), total VU1 cycles
  **959,411,166** (identical).
- **Speed (Mac mini M5 Pro, paraLLEl, diagnostics off, exclusive lease, ABBA):** d1b vs stage
  A g4 (holds A/B): 20.23 → 22.99 vsyncs/s, 1.14×. **Final d4 vs g4 (holds C/D): 20.17 →
  23.18 vsyncs/s (0.337× → 0.387× of 59.94), 1.15×.** Over all four holds g4 = 20.20.
- **Profile (diagnostic, d2 vs g4):** VU1 62.5 % → 54.5 % of busy samples; commitReadyPipelines
  28.0 % → 6.9 %. The pair functions (FMAC arithmetic + remaining bookkeeping) are now the bulk.
- **The differential test found two gaps that the whole-game gate cannot see** (the route never
  cuts a program at the 65,536-cycle budget): (1) the queue model *retires* an older write when
  a newer write to the same lanes issues before it lands, so at a budget cut, a resume or a new
  `execute()` the old value is still visible; d1–d3 were not exact there. d4 fixes it with a
  second static bit. (2) A pre-existing usage-table gap: OPMULA/OPMSUB declare `fs` lanes =
  dest but read `fs.xyz` (0 non-xyz uses in SSX 3's images; stage A has the same gap).
- **Recommendation:** d4 (`1f51e48..9638b3d`, plus the hash-only counters `9b71115` if wanted)
  is ready to fold, followed by an Odin speed pair. The orchestrator decides.
- **Paused by Brad at 13:58, resumed 15:15, closed ~15:55 (≈ 2h25m active of the 3 h box).**
  After the resume: a d4 profile and an instruction-level `xctrace` profile (below); no new
  candidate (the mini was fully leased by other lanes; a build + gates + an exclusive ABBA
  didn't fit the remaining time).

## Design

| Piece | What | Where (fork) |
| --- | --- | --- |
| Direct commit | In `issuePair`, after the stall: VF (upper, lower), VI, ACC writes and LSU stores are applied to `m_state`/VU data at issue instead of `queue*Write` + commit at readyCycle. Same lane masks, VI keeps the commit's `int16_t` cast, a fresh write sequence retires older queued writes to the same lanes. `m_vfReady/m_viReady/m_accReady` are still set by `markPairWrites`, so every stall is unchanged. | `ps2_vu1_step_impl.h` (`directVfWrite/ViWrite/AccWrite`), `ps2_vu1_fmac_impl.h` (`issueStore`) |
| Flags at issue | FMAC MAC/status and CLIP writes applied at issue when the map's flag bit is set; older queued flag entries are demoted to a sticky-only OR (`writesStickyOr`); a queued FSSET keeps the pair queued. | `updateFmacFlags`, `queueClip`, `demoteQueuedFlags`, commit |
| Static map (per image) | One byte per pair, built from the code bytes, cached by XXH64 (tests: per run). **Flag bit:** no flag op (0x10–0x1C, FSSET/FCSET included) in the pair or any pair that can issue in the next 4. **VF bits (upper, lower):** no newer write to an overlapping lane can issue in the next 3 pairs before a read of those lanes (reads stall to landing). Paths: delay slots, static targets, not-taken, pc wrap, entry as a delay slot of `i-1`; JR/JALR, out-of-range targets, branch in a delay slot, reserved pair → treated as a hit (queue). | `buildDirectFlagMap` in `ps2_vu1_recomp.cpp` |
| Runtime guard | VU1 only, dev traces off (`m_entryArmed`/`m_traceArmed`), `m_cycle + 4 ≤ budgetEnd` (every direct write lands before a budget cut), VI direct only at latency 1 (ILW/ILWR queued). `m_directPendingUntil` makes `pipelinesPending()`/`flushPipelines()` run the same cycles as the queue would. | `issuePair`, `pipelinesPending` |
| Fallback | Anything the guard or map rejects goes through the unchanged queue. `PS2X_VU1_DIRECT=0` queues everything (stage A behavior). Q/P (FDIV/EFU) always stay queued: upper ops read Q/P without stalling. | — |
| Chaining safety | `issueStore` keeps the SQ executors' local `words[4]` from escaping; d1 had given 1,603 pair functions a stack protector, which turned the `musttail` hand-off into a real call (stack overflow at t1605). `tailcall_audit.sh` counts `blr` in all 14,336 pair functions (d4: 0). | `ps2_vu1_fmac_impl.h`, `tailcall_audit.sh` |

**Why it's exact (the argument, then the test).** Inside a run, a VF/VI/ACC register can only
be read by a pair whose usage lists it, and that pair stalls to the same readyCycle the queue
would commit at; so the value between issue and landing is never read. What can observe it is
the run's exit (budget cut, then `resume()` or a new `execute()` whose `resetScheduler` drops
queued writes): the budget guard makes every direct write land before the cut, and the VF map
bit makes sure no newer write retires a direct write before it lands (the queue would have kept
the old value). Stores land at the next cycle boundary before PATH1 reads VU data, so applying
them at issue is invisible. Flags have no stall; the map's window covers every pair that could
issue before the flag entry lands, and the order change with older entries is repaired by
demotion (MAC, status bits 0–3 and CLIP are overwritten by the newer entry; sticky bits OR and
the FDIV D/I update commute).

**Differential test** (`ps2_vu1_tests.cpp`, "VB1 direct commit matches queued commit at every
budget cut"): 200 random programs of 12–39 pairs (FMAC/ACC/CLIP/ITOF/FTOI uppers; LQ/SQ/LQI/
SQI/ILW/IADDIU/FMEQ/FMAND/FSEQ/FSAND/FSSET/FCAND/FCSET/FCGET/DIV/WAITQ/B/IBNE lowers), random
VF/VI/data, each run direct vs queued and cut at every budget 1…4·len+64; VU state (whole
`VU1State`) and data memory must match at the cut, after `resume()` and after a fresh
`execute()`. ~15 s. It failed d3 (program 1, budget 4: supersede at a cut) and a 2×-margin
variant (program 35, budget 18: a chain of overwrites), then passed d4.

## Fork commits (`~/dev/ssx3-work/VB1/PS2Recomp`, local branch `vb1-stageb` from `1f51e48`)

| # | Commit | Change | `--stat` |
| --- | --- | --- | --- |
| d1 | `9983169` | direct VF/VI/ACC/store commits, flag map + empty-queue guard, `PS2X_VU1_DIRECT` | 5 files, +264/−5 |
| d1b | `86509dc` | `issueStore` always-inline (d1 crashed: stack protector broke the musttail chain) | 4 files, +38/−24 |
| — | `fda8364` | `[vu1-direct]` share counters (hash builds only) | 5 files, +35 |
| d2 | `b74d81d` | VR1 g5 cherry-pick (inline `advanceOneCycle`, commit gate at call sites) | 2 files, +17/−12 |
| d3 | `09ebafd` | flags at issue past older queued entries (demote to sticky OR) | 4 files, +55/−2 |
| **d4** | `9638b3d` | VF no-supersede map bits, VI direct only at latency 1, budget guard back to +4; differential test; `setDirectCommitForTest` | 5 files, +315/−37 |
| — | `9b71115` | VF direct/queued counters (hash builds only) | 3 files, +15 |

Branch total `1f51e48..9b71115`: 7 files, +681/−22 (VU1 files and one test file). Runner-dir
guard (`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) empty at every commit.
Commits carry `Orchestrated-By: Claude Code`. Not pushed. Generated VU1 sources unchanged
(`~/dev/ssx3-work/vu1gen-ssx3`, SHAs = VR1 `gen-v2.sha`); no regeneration needed because the
maps are built at run time from the code bytes.

## Acceptance

Base = VR1's `runner-g4-{hash,speed}` (fork `1f51e48` + gen-v2; SHAs re-read, match VR1
`binaries-sha.txt`). Boots: `vb1_boot.py` (VR1's driver, VB1 paths): `PS2X_DETERMINISTIC=1`,
`PS2X_SKIP_MOVIE=1` (dev-only), I26-FAST vsync pad script, empty mc0/mc1, det-hash every tick,
GS capture to t2400, one mini slot each; ISO `3c2f8eb1…`/ELF `1b49d05c…` read twice.

| Candidate | Suite | det-hash t1–2400 | GS CPU backend (strict, vs VR1 `h-base-cpu`) | GS paraLLEl (vs fresh `h-g4`) | VU1 cycles | Receipt |
| --- | --- | --- | --- | --- | --- | --- |
| d1 | 616/616 | — | — | — | — | **crash** SIGBUS t1605 (both backends) |
| d1b | 616/616 | 2400/2400 equal | **BIT-EXACT** (SHA `f2233e7e…`) | per-path content EQUAL | 959,411,166 | `check-d1b-cpu.txt`, `check-d1b.txt`, `gs-types-d1b.txt` |
| d2 | 616/616 | 2400/2400 equal (vs VR1 `h-base-1`) | — | — | 959,411,166 | NOTEBOOK 12:50 |
| d3 | 616/616 | 2400/2400 equal | **BIT-EXACT** | per-path content EQUAL | 959,411,166 | `check-d3-cpu.txt`, `check-d3.txt`, `gs-types-d3.txt` |
| **d4** | **617/617** | 2400/2400 equal | **BIT-EXACT** | per-path content EQUAL | 959,411,166 | `check-d4-cpu.txt`, `check-d4.txt`, `gs-types-d4.txt` |

d1b and d3 pass the whole-game gate but are **not** exact at budget cuts (the differential test
fails them); only d4 passes both.

## Speed

Mac mini M5 Pro, `build.sh <c> speed` (VR1 recipe: Release, ThinLTO, homebrew clang, diag taps
and det-hash tap off, logs off, paraLLEl shadow ON), speed env as VR1 (`PS2X_SOUND=1`,
`PS2X_VSYNC_RATE_LOG=1`, paraLLEl, `PGS_HIER_BINNING=force`). Rate = mean of 5 s
`[vsync-rate]` samples ending in (1800, 2400] (`speed_table.py`). Exclusive lease (all four
slots) per hold, two boots per hold, ≥ 1 min gap between holds.

| Hold | Run | Runner sha256 | vsyncs/s | ÷ 59.94 |
| --- | --- | --- | ---: | ---: |
| A (12:45) | s1-g4 | `0800ace0…` | 20.82 | 0.347× |
| A | s2-d1b | `53d31f8a…` | 23.78 | 0.397× |
| B (12:58) | s11-d1b | `53d31f8a…` | 22.19 | 0.370× |
| B | s12-g4 | `0800ace0…` | 19.63 | 0.327× |
| C (13:52) | s21-g4 | `0800ace0…` | 19.46 | 0.325× |
| C | s22-d4 | `1b255b33…` | 22.69 | 0.379× |
| D (13:55) | s31-d4 | `1b255b33…` | 23.67 | 0.395× |
| D | s32-g4 | `0800ace0…` | 20.88 | 0.348× |

| Candidate | Mean vsyncs/s | ÷ 59.94 | vs g4 |
| --- | ---: | ---: | ---: |
| g4 (stage A, `1f51e48`) | 20.23 | 0.337× | 1.00× |
| d1b (A/B vs g4 20.23) | 22.99 | 0.384× | 1.14× |
| **d4** (C/D vs g4 20.17) | **23.18** | **0.387×** | **1.15×** |

Host load 3–10 during the holds (other lanes' unleased work). Hold C waited 19 min for
the four slots and load < 8. Within a pair, runs of the same binary differ by up to 7 %
(g4 19.46/20.88), so d1b ≈ d4 (d4 queues 1.5 % of VF writes that d1b didn't). All runs:
`speed-all.txt`.

## Share of VU1 work on the fast path (hash runs, `PS2X_VU1_RECOMP_STATS=1`, route to t2400)

| | d2 | d3 | d4 |
| --- | ---: | ---: | ---: |
| VU1 cycles in pairs that passed the runtime guard | 100.00 % | 100.00 % | 100.00 % |
| FMAC/CLIP flag writes applied at issue | 51.2 % | 76.9 % | 76.9 % |
| VF writes applied at issue | 100 % (no map bit yet) | 100 % | **98.45 %** (570,867,241 / 8,983,046 queued) |

The budget guard never rejected a pair on the route (no program comes within 4 cycles of the
65,536-cycle budget).

## VU1 profile share (diagnostic `sample`, 20 s from ~t1900, one slot; `profile-d2.txt`)

| | g4 (VR1 `p-g4`) | d2 |
| --- | ---: | ---: |
| Busy samples | 6,140 | 6,650 |
| VU1 total | 62.5 % | 54.5 % |
| generated pair functions | 26.4 % | 36.6 % |
| commitReadyPipelines | 28.0 % | 6.9 % |
| run | 3.2 % | 3.7 % |
| execUpper (VU0) | 2.3 % | 3.6 % |
| progressXgkick | 1.7 % | 2.3 % |

Hot spot now: image `f587…` pairs 0x2a10–0x2a50 (LQI/SQI/DIV with FMACs, a per-vertex loop),
~20 % of pair-function samples. d4 (`profile-d4.txt`, after the resume): VU1 54.5 %, pair
functions 38.5 %, commitReadyPipelines 5.3 %, run 4.3 %, execUpper (VU0) 3.0 %.

**Inside the pair functions (d4, `xctrace` Time Profiler, 10 s from ~t1800, 1 ms samples,
GameThread; `xtrace-d4-classes.txt`, `xtrace_pcs.py`).** 9,175 GameThread samples, 56.0 % in pair
functions. By instruction at the sampled PC: loads 48.3 %, integer ALU 19.3 %, **FP double
12.0 %**, stores 10.5 %, branches 6.2 %, FP single 3.5 %. So the FMAC exact-result arithmetic
is roughly an eighth of the pair time; the rest is per-pair control and state traffic. The
hottest loads, mapped to member offsets (offsetof on this build's layout): `m_flagValidMask`
274 samples (VB1's flag guard), `m_traceArmed` 186 and `m_entryArmed` 108 (dev-only E36/E37
checks, constant for a run), `RunContext` budgetEnd 157 / codeSize 123 / programEnded 92
(the per-pair `next()` checks), `m_nextCommitCycle` 118, `m_directPendingUntil` 160. Samples on
Apple cores skid, so read these as "where the dependency chains are", not exact costs. Also on
GameThread: `__bzero` 4.9 % (the 64 KB `XgkickPipeline` zeroed by `m_xgkick = {}` in
`resetScheduler()` and `startXgkick()`: NP1 Part 2's target, not touched here) and
`__psynch_cvsignal` 4.1 % (GS worker hand-off).

## What's left

- **Next levers, measured above, cheapest first:** (1) generated pairs skip the dev-only
  `m_traceArmed`/`m_entryArmed` checks (`run()` sends an armed run to the interpreter instead);
  (2) hoist the per-pair `next()` checks (budget, pc bound, stop) to block granularity where a
  block's worst-case cycles fit the budget; (3) keep `m_flagValidMask`/`m_directPendingUntil`
  updates off the common path (e.g. the pending-until max only matters at a flush);
  (4) NP1's `m_xgkick` zeroing (4.9 %). These are the per-pair overheads a block-level stage B
  would remove anyway; (2) is most of what "static schedules per block" buys now.
- **Stage B as sketched (static stall schedules per block with an entry-scoreboard guard) was
  not built.** With the commit round trip gone, what the pair functions still do per pair is:
  the stall max over `m_vfReady` lanes (~8–12 loads), `markPairWrites` (~4–8 stores), the
  old/new register copies, the direct writes + sequence stores, and the FMAC exact-result
  arithmetic and flag computation. A block schedule removes only the first two; I estimate
  ≤ 10 % of the pair time, against the 3–5 day cost E57 gave it. The FMAC arithmetic (double
  exact results, normalization, per-lane flags) is now the likely leader; a line-level
  profile (Instruments or `perf` on the Odin) should confirm before choosing.
- Remaining commit work (6.9 % in d2): the 23 % of flag writes still queued (flag readers
  nearby, or a queued FSSET), Q/P. The flag window could be narrowed with real issue cycles.
- VU0 still runs the interpreter (`execUpper` 3.6 %).
- Cheap follow-ups: skip the old/new copy for fully-masked direct writes; count per-pc which
  flag writes stay queued.

## Gaps

- Mac only; no Odin pair.
- Route coverage is I26-FAST to t2400 (VR1's 7 images). Budget-cut exactness rests on the
  differential test (random programs; XGKICK, EFU/P, MFP, JR/JALR and I-bit pairs are not in
  its instruction mix) plus the argument above.
- Reserved-instruction stop (error path): a run stopped mid-program by `m_stopRequested` may
  leave direct writes visible that the queue would still hold; a following `execute()` would
  then differ. 0 reserved-instruction reports on the route (VR1 logs and ours).
- OPMULA/OPMSUB usage gap (fs lanes = dest, reads fs.xyz): pre-existing, affects the stall for
  non-xyz dests in stage A too; not fixed here.
- paraLLEl strict whole-file GS check is not deterministic base vs base (VR1); the strict check
  ran on the CPU backend for d1b, d3, d4.
- `sample` profiles are process-wide top of stack.

## Commands and pins

- Worktree `~/dev/ssx3-work/VB1/PS2Recomp`, branch `vb1-stageb` (`1f51e48..9b71115`, not pushed).
- Builds: `~/dev/ssx3-work/VB1/build.sh <label> hash|speed` (copy here), dirs `build-hash`,
  `build-speed`; paraLLEl-GS `~/dev/ssx3-work/F2/parallel-gs` @ `19d93b2`, codegen
  `~/dev/ssx3-work/codegen-ssx3`, VU1 images `~/dev/ssx3-work/vu1gen-ssx3`. Binaries and SHAs:
  `binaries-sha.txt`.
- Suite: `cd ~/dev/ssx3-work/VB1/PS2Recomp && ../bin/tests-d4-hash`.
- Hash boots: `vb1_boot.py --mode hash [--backend cpu] --runner bin/runner-<c>-hash --label
  h-<c> [--env PS2X_VU1_RECOMP_STATS=1]`; checks `check.py --base … --cand …` and
  `gs_types.py <base gs.cap> <cand gs.cap>`.
- Speed: `speed_hold.py hold<X> <start> <candA> <candB>`, `speed_table.py run`. Profile:
  `vb1_boot.py --mode profile --runner bin/runner-<c>-speed --label p-<c> --stop-tick 2000
  --sample-at 1800 --sample-s 20`, `profile_share.py`.
- Tail-call audit: `tailcall_audit.sh bin/runner-<c>-<kind>`.
