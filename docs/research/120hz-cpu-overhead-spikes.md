# CPU and diagnostic overhead spikes

The existing phone measurements justify separating callback CPU work from
waiting before choosing another Dolphin setting. An extra-render callback
takes roughly 6.8–9.7 ms across the six `c2e098d3` trials. The final Metal
command buffer takes roughly 1.9–2.5 ms, but those quantities cannot simply be
subtracted: the callback contains guest execution, renderer work and waits,
while the GPU measurement excludes earlier command buffers and may overlap CPU
execution. The new callback thread-CPU timer is intended to narrow that gap.

The first phone results with that timer, build `1747c62a`, make active CPU work
the stronger lead for the observed section:

| Trial | Completed extras | Median callback wall | Median callback thread CPU | Median paired wall-minus-CPU |
| --- | ---: | ---: | ---: | ---: |
| 1 | 52 | 8.638 ms | 8.453 ms | 0.039 ms |
| 2 | 3 | 11.858 ms | 11.789 ms | 0.030 ms |

Both trials lasted about three seconds before the guard stopped them; both
used full output resolution. These measurements suggest the callback thread
was predominantly busy in those samples. They do not distinguish generated
guest code from nested host renderer, software vertex conversion or probe work,
and the second sample is particularly small. The paired gap is measured per
callback; it is not the difference between independently aggregated medians.
No causal comparison against the older route or half output is established.
The session records 421 half-size submits during ordinary rendering, but no
half-output smoothing trial. Evidence is in
`local/research/120hz/output-resolution-phone-pacing.json` and
`local/reports/mobile/20260913-184102/Reports/1789338548.428`.

## Audit of actual settings and build commands

`local/research/120hz/aot-config-audit.json` records source hashes, actual Ninja
flags and the earlier phone measurements.

- All 183 generated-module objects use effective `-O2`, `-flto=thin`,
  `-ffp-contract=off` and `-fno-fast-math`. The target's final `-O2` overrides the
  earlier Release `-O3`. The module already has ThinLTO even though Dolphin's
  separate `ENABLE_LTO` option is off.
- Dolphin's core and software vertex loader already compile at `-O3`.
- The runtime explicitly chooses asynchronous ubershaders, shader caching and
  waiting for shaders before startup. Changing those INI fields alone does not
  override the explicit runtime selection. No new vertex or pixel shader
  creation appears in the sampled phone trial intervals.
- The no-JIT path forces software vertex loading and disables DSP JIT and the
  large entry-point map. CPU EFB reads and accurate CPU data-cache emulation
  are already off, and EFB copies remain textures.
- These trials have approximately 375–697 draw calls per video frame event,
  7.1–9.5 million native dispatches per second and 59–61 thousand interpreted
  instructions per second. Those counts do not measure CPU time spent in each
  path. They support measuring the native/renderer path before another shader
  configuration change. Earlier idle-skip experiments regressed or failed to
  progress, so this work retains the current idle behavior and clocks.

## Callback trace emission: measured, low priority

`tools/native_probe_io_bench.py` builds an isolated harness around the current
`NativeProbe::Emit` source. It changes exactly one flush call in a copied header,
leaving original sources and runtime behavior intact. The harness exercises
512 evenly selected callback records' fields and watched-offset patterns from
the phone session. Because raw RAM snapshots are not recorded, it reconstructs
deterministic representative bytes; this is an emission-cost benchmark, not a
guest-state replay.

Four alternating rounds compared flushing after every callback against a
64 KiB stdio buffer with a final flush/close. Each case emitted 4,096 records.
The latest run used a quiet CPU/GPU slot after the Simulator and collision
checks, and exercised the newly added non-null thread-CPU duration field.

| Mode | Median CPU ms/callback | Median elapsed ms/callback | Explicit fflush calls/case |
| --- | ---: | ---: | ---: |
| Flush each callback | 0.00718 | 0.00718 | 4,097 |
| 64 KiB buffering | 0.00573 | 0.00573 | 1 |
| Observed reduction | 0.00145 | 0.00145 | — |

All 32,768 emitted records were complete and identical after removing timing
fields. This includes diff construction, hashing, formatting and emission;
it excludes entry/exit snapshot capture, schedule/interpolation event emission
and all game execution. Explicit flush calls are counted, not kernel write
syscalls. A full stdio buffer can write independently of an explicit flush.

An earlier quiet-slot run with the nullable CPU field reported approximately
2.31 microseconds of elapsed savings, versus 1.45 microseconds in the latest
run. Neither is a controlled comparison of the field's cost. Both establish
that this Mac emission experiment is far below the 0.1 ms priority threshold.

About one to two microseconds saved per callback on this Mac is too small to prioritize
against a roughly seven-millisecond callback. Phone storage costs remain
unmeasured. No buffering change is promoted. Removing flushes could obscure
trial-end/restoration evidence and a crash tail; a live implementation would
need an explicit terminal-event and bounded periodic flush policy. Neither the
existing flush nor this benchmark adds `fsync` or proves crash durability.

Reproduction:

```sh
python3 tools/native_probe_io_bench.py prepare \
  --trace PHONE_SESSION/native-trial.jsonl \
  --output local/research/120hz/probe-io-new
python3 tools/native_probe_io_bench.py run local/research/120hz/probe-io-new
```

Evidence: `local/research/120hz/probe-io-spike-cpu-field/report.json` records
compiler, source/helper hashes, binary, corpus, each timed case and output
fidelity. The earlier nullable-field run remains in
`local/research/120hz/probe-io-spike/report.json`.

## Generated module O2 versus O3

`tools/native_module_opt_spike.py` creates fresh isolated module builds with
the same generated C, DOL, CPU runtime, ABI headers and module template. It
changes only the module optimization level and retains strict floating point,
ThinLTO, code verification, no-JIT execution and the current scheduler guards.
Each actual object command is checked for the requested final optimization
level and required flags. Source identity must remain unchanged across builds.

The tool records compile/link elapsed time, module size/segments, exported ABI,
and binary hashes. It then builds one common diagnostic player and private
launchers for the two module paths. Both launchers preserve the normal native,
course and watched-state acceptance checks. Production module paths and phone
defaults are never rewritten. The existing O2 manifest lacks a complete
generated-source/template hash receipt, so this spike builds both controls
fresh rather than attributing a difference to an unverified historical build.

```sh
python3 tools/native_module_opt_spike.py build \
  --output local/research/120hz/aot-opt-spike \
  --game local/game/gc-gari-027 --jobs 4 --compiler /usr/bin/clang
# Run only when other builds and native/Simulator tests are finished:
python3 tools/native_module_opt_spike.py run \
  local/research/120hz/aot-opt-spike --rounds 2
# Recheck recorded identities, complete watched fields and observer warnings:
python3 tools/native_module_opt_spike.py audit \
  local/research/120hz/aot-opt-spike
```

The test order is O2 / O3 / O3 / O2, with fresh profiles and the same
180-second course sequence, a requested 640 × 528 window, immediate XFB, Metal validation
off and identical diagnostic settings. CPU timing, callback wall timing,
game speed, extra-render completion and watched-state checks remain separate.
The desktop scheduler retains its existing host-seconds 140–175 experimental
window and speed floor, with measurement over 145–170. The phone's three-second
performance cutoff belongs to its app trial path; this desktop run does not
validate that cutoff or justify extending a phone trial. No scheduler policy is
changed for either platform.
These host-timed routes are not identical trajectories; any observed difference
is descriptive and does not establish a causal phone speedup. Keep thermal and
concurrent workload context with the report. A single faster Mac result cannot
justify changing phone defaults.

The first fresh builds selected Homebrew Clang 23.1 through CMake's default,
whereas the historical and phone modules use AppleClang 21. Both fresh variants
share Clang 23.1, so their comparison remains scoped to that compiler. Their
sizes or timings must not be attributed solely to optimization level when
compared against the historical AppleClang binary. The runner now makes compiler
selection explicit and defaults to `/usr/bin/clang`. Reproducing this initial
experiment requires `--compiler /opt/homebrew/opt/llvm/bin/clang`; any promising
result still needs an AppleClang comparison before phone consideration.

Both builds completed with identical generated-source inputs, compiler identity,
module tables and non-optimization flags. All 183 object recipes retained
strict floating point and ThinLTO. Both exported the required module entry point.

| Variant | Module bytes | Executable `__text` bytes | Build elapsed |
| --- | ---: | ---: | ---: |
| O2 | 84,917,784 | 72,224,624 | 827.5 s |
| O3 | 83,993,064 | 71,318,064 | 713.0 s |

O3's executable section is about 1.26% smaller within this pair. Build durations
include different cache and background correctness-test conditions, so the
elapsed difference does not establish a compile-time improvement. A single
common diagnostic player serves both modules; the runner verifies actual
executed module/player hashes from each native runtime receipt.

All four 180-second native runs completed in the reserved quiet slot. The
measurements below cover host seconds 145–170; callback counts are not actual
display presentations.

| Case | Complete extras | Guest/host speed | Extra wall median / p95 | Extra thread CPU median / p95 | Strict artifact verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| First O2 | 874 | 0.9965 | 7.900 / 10.249 ms | 5.903 / 10.238 ms | Passed bounded checks |
| First O3 | 572 | 0.9995 | 8.280 / 9.743 ms | 8.155 / 9.581 ms | Inconclusive: observer warnings |
| Second O3 | 767 | 0.9932 | 8.536 / 9.916 ms | 8.314 / 9.889 ms | Passed bounded checks |
| Second O2 | 806 | 0.9959 | 8.354 / 10.182 ms | 7.750 / 10.159 ms | Inconclusive: observer warnings |

All four passed the existing native/course checks: native module execution,
interpreter fallback, zero fallback JIT runs, zero code-verification failures,
zero guest invalid accesses, zero unknown instructions and zero GPU command
errors. The full traces contain 40,158 callbacks with complete known watched
fields, including 4,137 extras and zero observed extra state changes. These are
bounded observations, not complete-course correctness. The final O2 ride also
contains an ordinary reset/recovery, illustrating that the trajectories differ.
Representative screenshots show the rider, course and HUD continuing to render;
all saved frame captures are 640 × 491, which distinguishes the actual capture
from the requested window dimensions.

The separate artifact audit matters: the existing runtime gate does not reject
MemoryWatcher's unresolved host reads. The first O3 and final O2 each contain
24 reads of `803da1f8` at low exception PCs. Some first-O3 warnings occur during
the experimental section, so they cannot all be dismissed as startup noise.
The known failed observer-read path can raise a PI interrupt; those two runs
remain inconclusive for strict functional integrity. The warning recurred under
both optimization levels and does not establish an O3-specific defect.

World, graphics and frontend configuration hashes match exactly. Raw core
configuration hashes differ only in the per-profile random `Analytics.ID`;
canonical comparison excludes that field alone and retains every other line.
Each profile's raw hash still matches its runtime receipt. OS thermal and
performance warning queries reported no recorded warnings before/after all
four runs; this is not a temperature or clock measurement.

The observed callback timings do not establish an O3 benefit. The rides are
unmatched and two are affected by observer warnings, so no causal speedup or
regression is claimed. Keep the phone's O2 default. Build evidence is in
`local/research/120hz/aot-opt-spike/build.json`, timed results in `report.json`,
and strict field/config/observer checks in `audit.json` in the same directory.
The combined timed report also embeds those checks as `artifact_audit`.
The `accepted` fields in the timed report refer to the existing native/course
gate; the audit's explicit verdicts are required before treating them as clean
comparison evidence.

Before another timed comparison, replace the observer's failed-read path with
checked `HostTryRead` access and verify that unmapped reads cannot perturb the
guest. The current spike leaves the observer unchanged.

The next priority is opt-in callback signposts around the existing
`0x8010a4c8` entry-to-return span, tagged regular/extra and with the callback
thread ID, paired with on-phone Time Profiler leaf/self samples. Classify
generated chunks, `VertexLoader::RunVertices` conversion, FIFO and
`VertexManagerBase::Flush` host preparation, `MTLStateTracker::FlushEncoders`,
core and other work. `VertexLoaderManager` is broader than actual conversion,
and nested timers need exclusive accounting to avoid counting the same work
twice. Preserve the current callback-boundary timing; per-dispatch clock reads
previously caused a documented 25–30% regression. No additional profiling
instrumentation is implemented by this spike.
