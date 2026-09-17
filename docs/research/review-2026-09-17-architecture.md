# Architecture review of September 16–17 changes

Read-only pass over `5addae1`..`6e8082a` plus the uncommitted working tree
(live-switch spike in `recompcore-course-redirect.patch`, the untracked
`android_trial_driver.h` / `android_trial.py`), with extra time on the Odin M5
CPU profiles (`/tmp/m5/m5c-rep-all.txt`, `/tmp/m5/m5e-rep-all.txt`, aggregated
with the agent's `agg.py`) and the desktop `sample` dumps under
`local/research/fastfp-ab/`. Nothing was edited or run except this file and a
hermetic pytest of the new/changed test modules (89 passed, no cache or
bytecode written). Focus: architecture and the 120 Hz direction; performance
observations are included where they fell out of the reading.

Ordered by how much I think each one changes a decision.

## 1. The M5 Odin profile is of a pre-Wave-B module, so "CPU core is now the frontier" is stale

The todo records M5 as "FP outlined 25.8→16.2, CPU core now the frontier
(Run/HookExternal/dispatch)". The symbol set in the M5 dumps says the module
that was profiled predates the Wave B commit (`1c6e9e7`, 07:15; M5 ran at
03:50–04:00):

| leaf in Odin m5e | share | present in desktop fast-FP OFF (`sample-off3`) | present in desktop fast-FP ON (`sample-on` … `sample-psq`) |
| --- | ---: | --- | --- |
| `ppc_fmuls` | 3.03% | yes (372) | no |
| `ppc_fadds` | 2.74% | yes (366) | no |
| `ppc_fma` | 2.48% | yes (278) | no |
| `dolrecomp_f32_from_bits` (unsplit) | 1.34% | yes (301) | only the `_slow` variant after the conversion split |
| `ppc_fsubs`, `ppc_fmul`, `ni_madd_msub` | 2.05% | yes | no |

Under `cpu_fast_fp.h` those names are macro-redirected to `always_inline`
fast paths and only reached on the strict-FPSCR / NaN fallback, which is why
they vanish from every fast-FP-ON desktop sample. Their presence at ~12% of
Odin cycles means the Odin module was built without fast-FP and without the
conversion split. So of the 16.98% "fp_helpers" bucket in `agg.py`, roughly
three quarters is exactly what Wave B removes, and the 13.98% "cpu_core"
bucket is not yet the largest addressable one.

Suggestion: rebuild the Odin module from HEAD (fast-FP default, conversion
split, psq merge, same -O2+ThinLTO) and re-run the M4-identical recipe before
ranking core-side work. Record the module sha in the M5 notes; the m5 dumps
carry the binary path but no provenance.

## 2. The "inline" psq helpers are not inlined anywhere, and the psq merge could not have paid off yet

`ppc_psq_load_inline` / `ppc_psq_store_inline` are `static inline` in
`cpu.h`; the psq-merge comment says the win comes from per-site constant
folding "which it cannot do across a call". Every profile shows them as
out-of-line leaves:

| sample | `Run()` | `psq_load_inline` | `psq_store_inline` |
| --- | ---: | ---: | ---: |
| desktop off3 | 656 | 257 | 187 |
| desktop on | 698 | 252 | 200 |
| desktop conv | 626 | 260 | 228 |
| desktop psq (after merge) | 678 | 282 | 249 |
| Odin m5e | 2.65% | 1.07% | 1.06% |

The merge did not move them because the compiler is outlining the helper
(large body, many call sites) and the literals never reach it. Same fix the
fast-FP header already uses: `__attribute__((always_inline))`, or split the
inline part down to the LSQE test + the 8-byte fast path with the helper call
as the only out-of-line piece. Verify by the symbol disappearing from
`sample`, not by wall time.

Two neighbours in the same class:

- `dolrecomp_f32_from_bits_slow` stays at 175–184 samples after the split
  (about a quarter of `Run()`), so the "exceptional inputs" path is hot. Worth
  a one-run histogram of what reaches it; my guess is signed zeros or NI-flush
  denormals from cleared matrices, both of which could take the inline path.
- `ppc_fcmp` at 120–170 samples is untouched by fast-FP and is now the
  largest remaining scalar helper on desktop.

## 3. Odin FIFO panic: the static recomp has no FIFO-write exception check, and the profile shows the sync-GPU preprocess running on the CPU thread

Both M5 runs end at the same place: `FIFO is overflowed by GatherPipe! CPU
thread is too fast!` about 15 s into the race. Two things in the CPU-thread
profile bear on it.

`JitInterface::CompileExceptionCheck(FIFOWrite)` is 0.45% of cycles on the
CPU thread. In Dolphin that call exists so the JIT records the PC of a
gather-pipe burst and recompiles the block with an exception check right after
the write; that is how the CP high-watermark interrupt (the game's overflow
throttle) gets taken promptly. For the static recomp the call is a
`std::set` insert per burst that nothing consumes, and there is no equivalent
"check external exceptions after a FIFO write" in the recomp's dispatch path
as far as I can see from the patch. On desktop the Metal video thread drains
fast enough that the watermark never matters; on Odin the video thread is
slower, the write pointer runs past `CPEnd` between exception polls, and the
panic fires. Hypothesis, not proven, but it fits "deterministic, in-race,
Adreno-only".

Second, the CPU thread carries `OpcodeDecoder::RunFifo<true>` (0.55%),
`ReadDataFromFifoOnCPU` (0.16%) and `RunGpuOnCpu` (0.51%) while a separate
"Video thread" runs `RunFifo<false>` and GL. That is the deterministic GPU
thread path (`SyncGPU=True` under dual core): every FIFO byte is decoded twice,
once as preprocess on the CPU thread and once for real, and the CPU thread
waits on the GPU thread at slot boundaries. That may be deliberate for movie
determinism, but the Odin ini is not in the repo (device template `m6h`), so
I could not confirm.

Suggested checks, cheapest first: (a) pull the Odin `Dolphin.ini` and record
`SyncGPU`/`SyncGPUMaxDistance`; (b) make the recomp's write hook for
`0xCC008000` request an exception poll at the next dispatch when
`CommandProcessor` has raised the watermark interrupt, and drop the
`CompileExceptionCheck` call on the recomp path; (c) if the panic survives,
it is a genuine "GPU too slow" and SyncGPU distance is the knob.

## 4. Thread attribution in the M5 dumps is wrong or reveals a placement problem

80.7% of process cycles land on a thread named `GC Adapter Scan` (tid 6193).
Dolphin's CPU thread names itself `CPU thread`; with `DOLPHIN_NO_JVM` the
stubbed `ScanThreadFunc` names itself and exits immediately. The emu thread
(`Video thread`, tid 6199) was created after 6193, so 6193 was spawned before
`Core::Init`, which no Dolphin CPU thread is. Either the core is executing on
a thread nobody named (Linux copies `comm` from the creator) or naming is
being clobbered. Cheap check during any run: `cat /proc/<pid>/task/*/comm`
next to `ps -T -p <pid> -o tid,psr,pri,comm`.

Why it matters beyond labels: on the Odin's 1+4+3 Snapdragon the placement of
the one hot thread is worth more than any helper inlining; nothing in the
headless runner or `android_trial.py` sets affinity or priority, and the
`psr` column would show whether the scheduler keeps it on the prime core. Also
`agg.py` classifies by `cmd == 'Video thread'` and lumps everything else in
`moderngekko-run-egl` into `7.cpu_core`, so DSP HLE (`AXUCode::ProcessPBList`
0.32%) and the FIFO preprocess above are being counted as "core".

Related perturbation: `android_trial.py` defaults `--screenshot-seconds 2`,
and the M5 window shows a `FrameDumping` thread (PNG deflate) plus readbacks
on the video thread. The desktop harness already scopes texture preload out of
trial windows; screenshots on the trial binary deserve the same treatment
(capture before/after the window, or lengthen the cadence inside it).

## 5. Generation fix (`3a21fc3`) is correct; the blended gate is a weak bar

Checked the ordering: `NativeInterpolation::Before` runs before
`NativeProbe::Step` at the same dispatch, so at the first half's return
`update.repeated` is still false (counted), the probe then sets it true and
re-enters, and the second return is skipped. Non-doubled ticks count once.
`extras_blended` is incremented at `render.ret` from the per-render `blended`
counter that is zeroed at render entry, and the extra render re-enters
`history.Begin` with the same generation (keeps `previous`), so both draws in
a tick sample the same pair. Sound.

Residuals:

- `blended > 0` passes with one matrix out of ~6000. The gate-4b re-issue
  should carry the ratio (`blended / loaded`) or a floor, otherwise a
  regression that blends only the camera still reads green. The lifecycle
  proof's "202/203 extras blended, 262k matrices" is the right shape; put that
  ratio in `validate_trial_trace`.
- The prior review's alpha-period note still applies (alpha uses
  `TicksPerSecond/59.94`, `Deadline` uses `/120`).

## 6. Android trial driver: per-dispatch cost lives only in the trial binary

`NativeTrialAndroid::Step` runs on every dispatch and, before any PC filter,
does two `NativeTrial::status.load()` atomics, `RefreshNow`, and a
`polls & 4095` counter. `NativeInterpolation::Step` deliberately avoids
atomics and clock reads on the fast path (its comment says so) and filters on
thirteen PCs first. The driver undoes that for the trial binary only, so the
trial binary is slower than the control EGL runner by construction and the
SpeedFloor then judges the trial against a floor the control never pays.
Small, but it biases exactly the number the trial exists to measure. Move the
status checks behind the same PC filter (they only need to run at the
boundary PCs and at the scheduled request time). Minor: the local `kind`
shadows `NativeTrial::kind`, and a watchdog-only `at + 120` means a stuck
trial in a 240 s run emits one row and nothing else.

## 7. Idle-skip × smoothing-trial: a one-script check before any mechanism work

`SpeedFloor::Observe` takes its wall side from `now_cached`, which
`RefreshNow` updates only at three guest PCs (idle `0x801cad24`, update
entry, render entry), while the guest side is CoreTiming ticks, which the idle
skip advances in bursts. The schedule rows already log both `wall`
(`now_cached`) and `host_seconds` (`PresentationClock`, real). Diffing the two
deltas across the idle-on arm's samples answers "guard misread vs real
starvation" without a new run: if `wall` stalls relative to `host_seconds`
while ticks jump, the 0.44 ratio is an artefact of where the clock is read.

## 8. Patch-stack checker leaves shared files unverified

`check_patches` reverse-checks each layer with `--exclude` for files owned by
layers above it. The platform patch's `Mixer.cpp`/`Mixer.h` hunks are now
excluded because the mixer patch owns those files, so a lost platform hunk in
either file passes the check (the mixer hunks' three context lines do not
cover it). `bootstrap`'s "missing exactly when it forward-applies" is fine as
all-or-nothing. Cheapest fix: after the per-layer checks, reverse-check the
concatenated stack once with no excludes, or record per-file sha256 receipts
at apply time.

## 9. Live-switch spike in the working tree

`MaybeArmLiveSwitchWatcher` is clearly labelled temporary, but it sits inside
`recompcore-course-redirect.patch`, which is in `CORE_STACK`, so it ships in
the next commit unless stripped. As written it is a detached thread that
writes guest memory while the CPU thread runs, captures `system` by reference,
and calls `setenv` concurrently with other threads' `getenv`. Fine for a
one-off probe; the todo already says the production version needs a
pause-point apply on a controlled thread. Flagging only so it does not slip
into the stack by inertia.

## 10. Signpost attribution has an update-side blind spot

`dctx/attribution-detail.txt` shows `u=0` (or near it) for every hot chunk,
including rider physics where `fn_801A6118` carries the weight and has zero
hits of any class. That is by construction (same-chunk callees compile to
gotos and never dispatch, as the header says), but it means signposts can only
speak to the render side of the frame. Consumers of `attribution.json` should
treat the update columns as "unobservable", not "zero", and the earlier
pc-histogram result ("update ~99% traversal+physics") remains the only update
attribution.

## 11. Smaller notes

- **Mixer silent-FIFO skip** — correct as far as I can see: `m_ever_fed` is a
  one-way latch, the faded case snaps `m_fade_volume` on the mixer thread
  only, DMA is excluded so the starvation diagnostic keeps counting.
- **Snow scorer** — fine as a regression oracle. It has no frame alignment,
  so cross-device "pairs" compare different frames; the same caveat applies to
  `fastfp-ab/pairs*.json`, whose 90%-of-pixels diffs are free-ride
  trajectory divergence, not parity evidence. The movie A/B is the parity
  oracle and should be what "frame-compare clean" cites.
- **`chunk_signposts.h`** — runs a binary search on every dispatch when
  enabled, after the probe; research-only and env-gated, acceptable.
- **`callback_timer.h` / `native_render_schedule.h` clocks** — the
  non-Apple `WallMsPerTick` returns `1e-6` (ns→ms) matching
  `clock_gettime` ns; `PresentationClock` on `CLOCK_MONOTONIC` is the right
  domain for EGL/Vulkan presentation timestamps.
- **`idle_pc_ini_line`** default-off revert — consistent across desktop and
  iOS; the Odin ini keeps it on, which is another reason the M5 numbers and
  the desktop numbers are not directly comparable.

## Not reviewed

`gamecube_movie_ab.py` and `gamecube_line_tables.py` internals beyond their
docstrings, `metal_gpu_ms.py`, the Vulkan patch beyond its CMake changes, and
the `dispatch.csv` rows of the live-switch runs (in flight).

## Suggested order

1. Re-profile the Odin with a HEAD-built module (finding 1) before ranking
   core-side work; make the psq helpers actually inline (finding 2) in the
   same rebuild.
2. Pull the Odin ini and confirm SyncGPU; then try the exception-poll-after-
   gather-pipe-write change against the 15 s panic (finding 3).
3. `cat /proc/<pid>/task/*/comm` and `psr` on the next run (finding 4).
4. Ratio gate for blended extras before re-issuing gate 4b (finding 5).
5. The `wall` vs `host_seconds` diff over the existing idle-on traces
   (finding 7).
