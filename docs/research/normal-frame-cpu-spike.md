# Ordinary-frame CPU attribution

The first ordinary-gameplay CPU profile points toward generated guest code,
including Gekko floating-point and paired-single helpers, before broad renderer
configuration changes. Software vertex conversion is a measurable secondary
target. This is a desktop hotspot map; it does not establish an iPhone speedup
or split guest update code from guest draw code inside the generated module.

## Measured workload

An unchanged production native player ran for a 225-second bounded session.
Time Profiler attached only to that process and recorded **20.809 seconds**,
from September 13, 2026, 20:54:34.521 to 20:54:55.329 EDT. There were **16,988
running CPU-GPU-thread samples**, each with a 1 ms sampling weight. Waiting
threads were excluded by the template, so the percentages below describe
sampled active work rather than blocked GPU/audio wait time or frame latency.

The frontend selected **Snow Jam** from the `local/game/gc-gari-027` asset
directory. That directory name is not proof that this sample represents the
imported Garibaldi collision route. The exact loaded identities are:

| Input | SHA256 |
| --- | --- |
| GXBE69 revision-0 DOL | `b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce` |
| `files/data/worlds/bam.big` | `a67ec9e518a46fb07c1ed433ecc8c4300dd734e42347b4290e8befcfb3318e7f` |
| Native player | `8f69fd5d00d7d481df0fd5202f79090e8aea19f722e5e4d4a0f604c9ef95c404` |
| Generated module | `ca06dba7726f57547efe2508f9a2ebe437ad249568a30da9e127f51bdd37e547` |

The MacBook Air ran macOS 26.6.2. Its existing player configured **3× internal
resolution**, Metal, Cubeb audio, software vertex loading and a single CPU/GPU
thread. Saved frame captures are 1792 × 1376; actual EFB dimensions were not
instrumented. These settings differ from the phone's 1×/2× and CoreAudio.
The native executable and module hashes still matched after recording.

Screenshots before and during the sample show an active race, including an
unattended fall/recovery and subsequent progress to 28% at 60 MPH. The ordinary
host-timed input sequence stopped sending events before its old pause/restart
section. The run retained roughly 60 FPS and 1.0 guest speed around the sample;
it completed with zero invalid accesses, GPU command errors, unknown guest
instructions, failed chunk checks or fallback JIT entries. This is bounded
runtime evidence, not complete-course correctness or a physical-display test.

There were no injected draw callbacks, startup shortcut, MemoryWatcher
locations/socket, or per-dispatch sampling/timers. No HostRead/MemoryWatcher
warning appeared. Periodic screenshots remained enabled and produced 391
FrameDumping-thread samples; this diagnostic overhead is another reason not
to interpret the recording as a phone timing baseline. Parent builds and
Simulator execution were kept out of the sampling window.

## Hotspots

All percentages use the 16,988 CPU-GPU-thread samples as their denominator.
Self time identifies the sampled leaf; inclusive time includes callees.
Subset rows and inclusive paths overlap and **must not be added together**.

| Scope | Samples | Share | Accounting |
| --- | ---: | ---: | --- |
| Generated module | 12,315 | 72.49% | Self, including the next three subsets |
| Named FP, paired-single, conversion and quantized load/store helpers | 2,465 | 14.51% | Subset of generated-module self |
| Guest idle loop `loop_80288ED4` | 1,323 | 7.79% | Subset of generated-module self |
| `chassis_dispatch` | 186 | 1.09% | Subset of generated-module self |
| `StaticRecompCore::Run` | 513 | 3.02% | Self |
| `VertexLoader::RunVertices` | 1,114 | 6.56% | Inclusive software conversion |
| `Metal::StateTracker` paths | 349 | 2.05% | Inclusive |
| `VertexManagerBase` paths | 338 | 1.99% | Inclusive |
| `TextureCacheBase` paths | 247 | 1.45% | Inclusive |
| `PrecisionTimer::SleepUntil` | 659 | 3.88% | Inclusive active throttle/yield samples; excludes blocked time |

The largest generated chunk is `func_802197A0`: 1,106 self samples (6.51%),
and 1,877 including callees (11.05%). Other prominent chunks are
`func_8022D7A0` (496 self samples), `func_801097A0` (374), and
`func_802697A0` (373). These names identify generated address chunks,
not individual recovered game functions. The profile cannot yet label their
work as simulation, animation, culling, or guest rendering with confidence.

Useful concrete leaves include `ppc_fadds` (326), `ppc_fmuls` (325),
`dolrecomp_f32_from_bits` (298), `ppc_fma` (250), `ppc_psq_load_inline` (242),
and `dolrecomp_f32_to_bits` (186). The most sampled software vertex stage is
indexed 16-bit signed XYZ position conversion (287), followed by the loader
loop itself (196); indexed float normals, position and texture-coordinate
conversion also appear. Metal draw preparation is present, but it is not the
largest named CPU path in this sample.

## Phone callback context

The existing phone session `1789345362.689`, build `113c9b20`, provides
callback thread-CPU timing while its smoothing trials are active. All three
sections below used 2× internal detail and Match output at 1947 × 896.

| Trial start, trace seconds | Ordinary update median | Completed ordinary render median | Completed extra render median | Counts: update / ordinary / extra |
| --- | ---: | ---: | ---: | ---: |
| 119.554 | 3.443 ms | 9.645 ms | 9.112 ms | 205 / 205 / 55 |
| 164.678 | 3.507 ms | 7.100 ms | 6.045 ms | 290 / 290 / 172 |
| 237.895 | 3.276 ms | 5.783 ms | 4.728 ms | 809 / 794 / 267 |

Ordinary rendering is more expensive than the ordinary update callback in
each observed section. These are different trajectories and ordinary
callbacks running alongside injected work, not a clean standalone 60 Hz
comparison. The callbacks include their diagnostic capture overhead and omit
some surrounding core, DSP and presentation work. Do not add independent
medians into a whole-frame budget or subtract them to claim an extra-frame
optimization. A completed render requires a nonzero result plus observed view
and frame-end calls. The profile has no callback phase signposts, so desktop
leaf percentages cannot be assigned to these phone callback durations.

## Next bounded work

1. Add opt-in callback-boundary signposts around ordinary update
   `0x8010550c` and ordinary/extra draw `0x8010a4c8`, tagged with thread ID and
   phase, then collect a phone Time Profiler recording. Add line tables for the
   hottest generated chunks to distinguish their guest instructions. Keep
   clocks out of the per-dispatch path; prior per-dispatch timing regressed
   execution substantially.
2. Test one narrow, equivalent generated-code/helper optimization against
   the existing semantics. The pinned
   `GXRuntime/src/core/cpu_interpreter_float.c` helpers update FPSCR, preserve
   paired-single results, handle NaNs and apply Gekko rounding. The generated
   `generated.h` conversion helpers explicitly preserve bit behavior. Their
   measured cost justifies investigating specialization/inlining or a proven
   finite-value fast path with the existing path retained for exceptional
   inputs. It does not justify fast-math, discarded FPSCR updates, or removing
   exceptional cases. Require differential FP tests and unchanged code guards.
3. For a renderer target, measure a static specialization for the most common
   software vertex format. `VertexLoader.cpp:RunVertices` loops over indirect
   stage calls for every vertex, and the measured position/normal/UV stages
   identify formats worth counting first. A statically compiled fused path
   can preserve no-JIT execution, with the generic converter retained as the
   reference/fallback. Eliminating the entire measured converter would cover
   only 6.56% of this CPU-thread sample, so this has a smaller bounded scope
   than the generated-code work.

The observed guest idle loop is not permission to enable the earlier idle
skip experiment; that route previously regressed or failed progress. The
existing O2/O3 spike also did not establish an O3 benefit. Preserve clocks,
strict floating point, executable-memory guards, and the phone's current
optimization defaults while measuring focused changes. Safe renderer replay
remains blocked on the separate isolation work in
[120hz-host-replay.md](120hz-host-replay.md).

## Artifacts and reproduction

`local/research/120hz/normal-frame-cpu-race/summary.json` contains the
runtime receipt, exact configuration files, capture timing, source identities,
phone distributions and screenshot hashes. `leaf-report.json` contains self
and inclusive symbol rankings; `samples.xml` and `resolved-samples.json` retain
the sample stacks. `run.py`, `summarize.py`, and the preceding
`normal-frame-cpu-spike/analyze.py` record the isolated launch and analysis.
The raw Instruments trace remains local/ignored; the exported index omits
the process environment. The second launch passed only required environment
keys to the player.

The native receipt is `local/reports/native-runs/20260913-205127.json`.
The earlier 180-second attempt under `normal-frame-cpu-spike` sampled mostly
the pre-race confirmation screen; its short race tail was excluded from the
reported percentages. A later, screenshot-verified sample window corrected
that mistake. Reproduction should use a fresh profile, the same identities,
ordinary input only, and a confirmed race before attaching Time Profiler:

```sh
xcrun xctrace record --template 'Time Profiler' --attach PLAYER_PID \
  --time-limit 20s --output NEW_LOCAL_TRACE.trace --no-prompt
xcrun xctrace export --input NEW_LOCAL_TRACE.trace \
  --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' \
  --output NEW_LOCAL_SAMPLES.xml
```
