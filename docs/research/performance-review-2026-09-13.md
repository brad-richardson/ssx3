# Performance review — September 13, 2026

A read-through of the September 13 profiling, spike and phone evidence, plus
the generated module and runtime sources they measure. The conclusion is that
the remaining performance work should move from helper micro-optimizations to
three structural costs: the shape of the generated code, single-threaded
CPU/GPU execution, and a 120 Hz design that re-runs the guest renderer. This
document ranks that work and states the evidence bar for each item. Nothing
here changes a build, a default or a guard.

## Where the project stands

- **Course port.** Garibaldi rides on the GameCube engine with its own
  textures, lightmaps, race line, opponents, static scenery, rails and
  terrain reset recovery (assets 027 installed, candidate 031 for object
  collision). Fog/backdrop, start gate, breakables, curved rails and full
  route acceptance are the open content items and are correctly tracked in
  `docs/todo.md`.
- **Phone shell.** Fast start, checkpoint/resume, direct output and detail
  controls, and the smoothing trial all work on the iPhone 16 Pro Max.
  Phone smoke runs reach about 60 FPS; sustained acceptance is deferred.
- **120 Hz.** Short high-refresh bursts are real (up to 117–120 displays/s
  for under 16 seconds), but no trial has sustained the 25-second target.
  Nearly every trial ends through the speed guard, and most thermal samples
  in the latest session are *serious*.
- **Micro-optimization spikes.** The classifier, conversion-inlining, O2/O3
  and probe-buffering spikes are complete, correct and correctly rejected.
  They bound the total available from that direction at about one to two
  percent of CPU-thread samples. They should be closed rather than refined.

## What the measurements say

Sources: [ordinary-frame profile](normal-frame-cpu-spike.md),
[CPU/config spikes](120hz-cpu-overhead-spikes.md),
[output-resolution runs](120hz-output-resolution.md) and
`local/research/120hz/normal-frame-cpu-race/leaf-report.json`.

| Fact | Value | Where |
| --- | ---: | --- |
| Desktop CPU-thread samples in the generated module (self) | 72.5% | Mac, Snow Jam, 3× |
| Named FP / paired-single / conversion helpers (subset) | 14.5% | same |
| Guest idle spin `loop_80288ED4` (subset) | 7.8% | same |
| Host yield inside the throttle (`swtch_pri`) | 3.5% | same |
| Software vertex conversion (inclusive) | 6.6% | same |
| Phone ordinary update callback, median thread CPU | 3.3–3.5 ms | 113c9b20, 2×/Match |
| Phone ordinary render callback, median | 5.8–9.6 ms | same |
| Phone extra render callback, median | 4.7–9.1 ms | same |
| Phone extra callback wall vs thread CPU | 8.64 vs 8.45 ms | 1747c62a |
| Native dispatches per second on the phone | 7.1–9.5 million | c2e098d3 |
| Thermal samples serious in the latest phone session | 268 of 466 | f40bfef6 |

Two conclusions follow directly. The phone callbacks are CPU-bound, not
waiting on the GPU. And an ordinary frame already spends roughly 9–13 ms of a
16.7 ms budget on one thread before any extra draw (measured while trials
were active, so slightly pessimistic), so a second guest render cannot fit no
matter how the schedule is tuned.

## Structural cost 1: the shape of the generated code

The generated module is the same `dolrecomp --backend=c` output on Mac and
phone. Reading the hottest chunk,
`local/native/ssx3-module/codegen/generated/chunks/chunk_0134_text1_802197A0.c`
(37,943 lines, 4,168 guest instructions), shows what the 72.5% is made of:

| Pattern | Count in the hot chunk | Cost |
| --- | ---: | --- |
| `ctx->pc = 0x...` store | 3,885 | one store per guest instruction; keeps `CPUState` memory-resident |
| `ppc_fp_available_inline` check | 1,120 | global load, MSR load and branch before every FP instruction |
| Outlined `ppc_fadds` / `ppc_fmuls` / `ppc_fma` calls | 155 | interpreter-fidelity helpers with FPRF classification, NI flush and exception gating on every operation |
| Outlined `dolrecomp_f32_from_bits` / `to_bits` sites | 316 + 273 | Clang declines to inline them at O2 (cost 165/70 vs threshold 45) |
| Chunk entry `switch (ctx->pc)` | 4,216 cases | every entry from the chassis re-selects its label |
| Cross-chunk `bl` / `bctrl` | every one | sets `lr`/`pc` and **returns to the C++ chassis** |
| `blr` | 32 | second in-chunk switch; leaves the chunk if the target is elsewhere |

Chunks are fixed 16 KiB address ranges, not functions, so any call whose
target lies in another chunk and any return to a caller in another chunk costs
a round trip through `StaticRecompCore::Run`, `dolrecomp_call`, the chunk
function prologue and the entry switch. At 7–9.5 million dispatches per second
on the phone, that is 120,000–160,000 round trips per 60 Hz frame. The
existing `dolrecomp_call_enter` depth guard in `generated.h` would allow direct
C calls, but no chunk uses it. Guest memory access itself is fine: the
shipping `mem_read*`/`mem_write*` helpers in `GXRuntime/include/core/cpu.h`
are always-inline range checks with a byteswap. Stores add a reservation
check and a global write-journal test each time.

The floating-point helpers deserve a specific note. They reproduce Dolphin's
**interpreter**: every result is classified into FPRF, NI flushing is applied,
NaN payloads are propagated and exception enables are consulted. Dolphin's
**JIT**, which is what every Dolphin user runs this game on, skips all of that
by default: `JitArm64_FloatingPoint.cpp:28` returns early from FPRF unless
`MAIN_FPRF` is set, and `MainSettings.cpp:216-217` default both `FPRF` and
`AccurateNaNs` to false. The JIT does keep the 25-bit rounding of the C
operand for multiplies (`Force25BitPrecision`) and single-precision result
rounding. The spikes so far have treated interpreter semantics as the
correctness bar and therefore could only shave a few percent off a helper
that is inherently ten times the cost of the native instruction. The
defensible bar is the JIT's default semantics plus a repeatable gameplay
comparison; that is a different experiment from fast-math, which remains
excluded.

## Structural cost 2: one thread for CPU, FIFO and Metal

Both the Mac runner (`tools/native_gamecube.py:242`) and the phone
(`native/ios/App.mm:531`) set `CPUThread = False`. In that mode the guest's
render callback also performs FIFO decoding, software vertex conversion,
texture cache work and Metal encoding synchronously, which is why the phone's
render callback costs two to three times its update callback. Dual-core mode
moves that host work to a second thread, and the iPhone has cores to spare.
This has never been tried here. Two diagnostics assume single core and must
stay disabled during the experiment: `native_frame_replay.h:194` refuses to
run in dual-core mode, and the pose-interpolation adapter intercepts XF
uploads on the dispatch thread.

## Structural cost 3: 120 Hz by re-entering the guest renderer

The extra draw calls the guest render callback at `0x8010A4C8` again with
interpolated palettes. It therefore costs a full guest scene traversal plus
FIFO decode and vertex conversion (4.7–9.1 ms median on the phone), and the
interpolation trial adds a median of 1,725 blended matrix re-uploads per
ordinary frame. Even a generated module twice as fast would leave update plus
render plus extra near or above 16.7 ms on a thermally limited device.

The [host replay](120hz-host-replay.md) path executes no guest code; its Mac
decode-and-submit cost at 640 × 528 was a few milliseconds including the
present. Its correctness gates (encoder frame identity, isolated render state,
owned memory) are the right gates. The change proposed here is priority, not
rigor: treat retained host-side replay as the mainline 120 Hz design and keep
guest re-entry as the reference for state-purity checks.

## Runtime overhead that costs nothing to remove

- `native/ios/App.mm:560` sets `STATICRECOMP_DISPATCH_SAMPLES=1` for every
  phone launch, and `StaticRecompCore.cpp` treats presence as enabled. That
  is a branch per dispatch and a map update every 4,096 dispatches in
  production. Make it opt-in from the diagnostics menu only.
- `native/ios/CMakeLists.txt:30` injects `StartupBoot::Step` and
  `NativeInterpolation::Step` before every dispatch, whether or not a trial is
  armed. Both early-out through a `switch` on the PC, but that is still two
  calls and two switches at 8 million dispatches per second. One hoisted
  "trial armed" branch removes both from ordinary play.
- `m_chunk_lookup_table` is a `std::vector<int>` with one entry per guest
  word, 24 MiB for 24 MiB of RAM, probed on every burst back-edge by
  `fast_dispatchable_at`. A chunk-granular byte table (1,536 entries at
  16 KiB) answers the same question without evicting the guest's working set.
- The guest idle spin and the host yield together are about 11% of desktop
  samples. They do not cost frame time, but on the phone they are pure heat
  while thermal state is the binding limit on any sustained result. Earlier
  idle-skip attempts regressed because `CoreTiming::Idle()` only skips one
  slice; a correct version fast-forwards to the next scheduled event and lets
  the throttle sleep instead of yield-spinning. Measure this by thermal state
  and callback CPU, not by FPS.

## Priorities

Ordered by expected effect on the phone divided by risk and effort. Each item
names its evidence bar. Items 1 and 2 need no generated-code change.

1. **Build a deterministic replay check before touching codegen.** Current
   course checks inject host-timed input, so two runs follow different
   trajectories and only "watched state unchanged" comparisons are possible.
   Inject the same input sequence at guest frame counts, record rider
   position/velocity/state per update, and diff two runs of the unchanged
   build to learn the baseline divergence. Every later item uses this diff
   as its acceptance gate. Most of the pieces exist: pipe-controller input,
   the callback trace and the watched-field snapshots.
2. **Try dual-core.** Flip `CPUThread = True` in the Mac profile, run the
   course checker with the interpolation and replay diagnostics off, and
   compare ordinary update/render callback CPU, guest speed and invalid
   access counts. Then the same on the phone with thermal state recorded.
   Expected effect: the render callback loses most of its host share. Total
   power may not fall, so record thermal samples alongside.
3. **Remove the production-only overhead above.** Dispatch sampling opt-in,
   one hoisted branch for the trial steps, and the chunk-granular lookup
   table. Small individually; free; they also make later measurements
   cleaner.
4. **Generated-code floating point at JIT fidelity.** In the DolRecomp C
   emitter (`vendor/dolphin/DolRecomp/src/backend/emitter.c`): emit
   `fadds`/`fsubs`/`fmuls`/`fmadds` and the paired-single arithmetic inline
   as host double operations with explicit single rounding and the retained
   25-bit C rounding; compute FPRF and exception state only when a global
   "strict" flag is set (verify once by tracing `mtfsf`/`mtfsb1` that the
   game never enables FP exceptions); hoist `ppc_fp_available_inline` to
   block entry; omit `ctx->pc` stores before instructions that cannot raise
   or that already pass `cia`. Keep `-ffp-contract=off` and `-fno-fast-math`.
   Bar: Dolphin JIT default semantics, the item 1 replay diff within
   baseline divergence, and unchanged native/course checks. The profile
   bounds the direct effect at up to about 15% of CPU-thread samples; the
   indirect effect from freeing registers around the removed calls is
   unmeasured and probably larger.
5. **Cut chassis round-trips.** First measure: extend the dispatch sample map
   to classify dispatches by cause (`bl`, `bctrl`, `blr`, exception) per
   frame. Then, in order of effort: align chunk boundaries to function
   boundaries using the GXBE69 symbol map so hot call trees stay in one
   chunk; emit direct C calls for statically known cross-chunk `bl` targets
   using the existing depth guard; and only later consider one C function
   per guest function. Bar: dispatch count per frame, callback CPU, replay
   diff.
6. **Specialize the software vertex loader.** Log the VAT/CP formats the
   game uses, compile fused loaders for those formats ahead of time, keep the
   generic loader as fallback. Worth about the measured 6.6% on the guest
   thread today, and nothing on that thread if item 2 lands, so do this
   after item 2 decides where the FIFO work runs.
7. **Idle spin to a real host sleep.** Thermal item; see above.
8. **120 Hz: depth reprojection on the GPU.** Superseded on September 13
   evening by [the reprojection design](120hz-reprojection.md): the phone's
   GPU-time measurements rule out a second raster at 3×, so the in-between
   frame must be synthesized from the last frame's color and depth with the
   predicted camera. Guest re-entry stays a diagnostic only.
9. **Loading: FastDiscSpeed on the phone.** The paired Mac check saved 26% of
   time to the menu. Repeat the paired check on the phone with card
   read/write/relaunch verification before changing the default.

Closed, not to be reopened without new evidence: classifier and conversion
inlining candidates, generated-module O3, probe emission buffering, symbol
stripping, and further tuning of the smoothing guards.

## Batch 1 results, September 13 evening

Delivered as phone build `6513686a`: an always-on ordinary-callback timer,
dispatch sampling off unless requested, and launch-only switches for
dual-core, FastDiscSpeed and sampling. No generated-code change. The user
rode the same short Garibaldi route twice at Half output and 2× detail,
starting cool, single-core first. Both Mac course checks (dual-core and the
single-core control, 200 s each) passed with zero invalid accesses, zero GPU
command errors, zero failed chunk checks and no reset loops.

| Phone, riding seconds only | Single-core (session 1789352759) | Dual-core (session 1789353082) |
| --- | ---: | ---: |
| Riding seconds / seconds below 0.97 speed or 57 FPS | 150 / 34 | 155 / 3 |
| Speed median / minimum | 0.998 / 0.842 | 1.000 / 0.872 |
| Guest headroom (`maxSpeedExcludingThrottle` median) | 1.00 | 1.25 |
| Update callback CPU median / p95 | 3.41 / 3.86 ms | 3.26 / 3.70 ms |
| Render callback CPU median / p95 | 9.49 / 10.51 ms | 7.77 / 8.43 ms |
| Stadium section (≥ 800 draws per frame): speed median, render CPU median | 0.887, 12.8 ms | 1.000, 9.7 ms |
| Draw calls / converted vertex data per frame, medians | 490 / 1.9 MB | 501 / 2.0 MB |
| Audio empty dequeues during riding | 80 | 6 |
| Thermal | nominal throughout | fair from 132 s |
| Steady footprint | about 430 MB | about 540 MB |

The user reported no visible wavering from full speed in the dual-core run,
including the stadium and overlapping-track section near 40% of the course
that previously slowed. That section is the heaviest rendering load on the
route: 830–970 draw calls and 3.1–3.7 MB of converted vertex data per frame
against about 500 and 2 MB elsewhere. Single-core, its render callback cost
12.5–14.3 ms plus a 3.5 ms update, over the 16.7 ms frame; dual-core, the
CPU thread's share of the same section fits with margin because FIFO
decoding and vertex conversion run on the second thread. The dual-core run
resumed from the first run's checkpoint, so the two rides are the same
course but not a trajectory-matched pair. The remaining 7.8 ms render cost
on the CPU thread is guest scene traversal plus per-write FIFO hooks, which
is the generated-code work items 4 and 5 target. A second guest render per
frame still does not fit (3.3 + 7.8 + 7.8 ms), so the 120 Hz conclusion
above stands. Batch 1b makes dual-core the persisted default with a menu
switch and a `--single-core` launch control. Evidence:
`local/reports/mobile/20260913-223516/Reports/{1789352759.918,1789353082.926}`,
`local/research/perf-batch1/phone-round1.json`, Mac checks under
`local/research/perf-batch1/`; summarize with `tools/mobile_frame_cost.py`.

## Batch 2: fast floating point, chunk-granular lookup, determinism gate

Delivered on the Mac on the evening of September 13; the phone module build
follows the gate below.

- **Determinism gate.** `SSX3_MOVIE_RECORD`/`SSX3_MOVIE_PLAY` in the runtime
  record and replay Dolphin input movies; `tools/native_determinism_check.py`
  wraps the course checker and compares the runtime's dispatch trace (now
  appended across run-loop re-entries) row for row by dispatch count.
  Replaying the recording against the baseline module reproduces the sampled
  control-register rows in single-core mode. This is a control-flow check;
  floating-point registers and gameplay memory are not covered.
- **Fast floating point** (`RECOMPCORE_FAST_FP`, `cpu_fast_fp.h`): inline
  scalar and paired-single arithmetic at Dolphin-JIT fidelity, forced into the
  generated chunks by a compile option; helpers, interpreter and generated
  sources unchanged; NaN results and enabled exceptions fall back to the
  exact helpers. Module grows from 76.6 to 80.4 MB. Replay verdict against the
  baseline module over a 200-second Garibaldi ride: **1,022 of 1,022 samples
  identical** (pc, lr, ctr, cr, timebase per 1,048,576 dispatches, from
  dispatch 0 to 1.07 billion), zero invalid accesses, zero GPU command errors,
  zero failed chunk checks. Evidence: `local/research/perf-batch2/`
  (`det-record-1.dtm`, `det-play-base-2`, `det-play-fast-2`,
  `compare-base-vs-fast-2.json`).
- **Chunk lookup table**: one `s16` per 256-byte granule instead of one `int`
  per word; mixed granules resolve by binary search. Same replay verdict
  covers it (both replays ran on the rebuilt core).
- **Smoothing guard** relaxed after the user's 3×/4× session showed every
  dual-core trial cancelled at 0.93–0.95 half-second speed while trial
  frames ran at 0.996–1.003 median: 10-second settling, 2-second cancel
  window at 0.95, per-frame veto 0.97/0.99.

The 3×/4× session (`1789354928.040`, build `060197cd`) also settled the GPU
question for now: at every internal scale up to 4× and every output up to
Full, the render callback's wall-minus-CPU gap stayed at or below 0.1 ms, so
the graphics thread keeps up and internal resolution costs the CPU thread
nothing. Thermal reached *fair* after about four minutes at 3×.

## Evidence boundary

Percentages are from a single 20.8-second desktop Time Profiler sample at 3×
internal resolution with periodic screenshots on; they identify where the
cost is, not phone timings. Phone numbers are callback medians from
different rides and thermal states. Counts from the hot chunk describe one
of 176 chunks. No new run was executed for this review. The phone-side
attribution with callback signposts planned in the ordinary-frame profile
remains the right next measurement and does not conflict with any item here.

## September 14 follow-up: bound the fast-FP gate before expanding it

The [bounded phone comparison and evidence audit](performance-batch2-followup.md)
keeps fast-FP as a candidate pending a paired phone measurement. The updated
comparator confirms 1,022 identical samples in an uninterrupted prefix from
dispatch zero, matching runner/course/configuration and clean reported native
execution/fault counters. The legacy runs did not capture movie hashes, so
their historical input identity cannot satisfy the new strict acceptance gate.
Both runs also show the same 83 successive rider-state entries
(82 changes after the initial state).
However, the rider observations use host time, and the sampled dispatch trace
does not include FPRs or gameplay memory. **Gameplay-state equivalence remains
unverified.** Future semantic changes need samples aligned to guest updates.

The earlier categorical GPU statements above are also hypotheses, not a
complete scheduling proof: the phone's presenting-command-buffer timing is
not total GPU work, and near-zero render callback wall-minus-CPU time in
dual-core mode does not establish GPU headroom. The next 120 Hz batch measures
coherent capture and reprojection cost without changing physics cadence.
