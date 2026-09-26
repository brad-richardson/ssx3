# CP1 — Odin critical-path timeline on the MTVU play build

Worker: Muse Code. Brief: `local/muse/prompts/CP1.md`. Date: 2026-09-26.
Method: F7 `launch.py` + `cooldown.py` adapted (play-env pin `ef9f94e1…`,
CP1 paths/lease, `--offcpu` profiler mode, concurrent sampler during the
profile window: schedstat + cpufreq + gpubusy + gpuclk); rates via F4
`phases.py`; symbolization per N12 (host simpleperf + unstripped `.so`,
Build ID checked). **Measurement only; no conclusions** (brief §Goal).

## Status

**R1 done (clean anchor), R2 failed (driver), R2b done (offcpu profile).**
R1: race 23.00/s = 0.384×; exact-tick window 1969→2568 (598.6 frames,
48.78 ms/frame): MTVU 28.7 / 1.9 / 18.2, GameThread 12.2 / 0.7 / 35.9,
GsWorker 9.6 / 3.7 / 35.4 ms/frame (run / runnable / blocked). R2b: 20.0 s `--trace-offcpu`
profile (ticks ~1990→2395, 106.8 MB, 474,268 samples), matched schedstat
window 1983→2403 (420 frames, 50.00 ms/frame): MTVU 30.1 / 0.9 / 19.0
(starved 12.2 + GS-backpressure 6.7), GameThread 13.1 / 0.2 / 36.7
(vblank), GsWorker-30557 9.7 / 3.7 / 36.6 (queue-empty ~19.5 + kgsl-fence
~19.1, ±20% split). Zero profiler perturbation (R1 clean 19.49 vs R2b
19.55 vs/s over ticks 1949→2340). 4 transient Turnip worker threads
(named GsWorker, ~96% CPU each) alive in R2/R2b's early window, gone by
R1's window and by R2b's end. R3: the ~22 ms `flush_submit` wait is
essentially all in the two `submit_empty` timeline signals (21.7–22.1
ms/present; main submits 6 µs, drain 0.4 µs; closure residual 0.04).
R4 (LAG): −5.34 ms/frame identical-tick (2000→2500). All tables
delivered; 5/5 launches, 1/1 build.

## Build (play build, installed before each run)

| Item | Result |
| --- | --- |
| APK | `~/dev/ssx3-work/odin-play/app-release.apk`, `825b436dd2cfc9f3ee42e7ac06643623b9651df409892c6a3e25af27cc531254`, 190,748,236 B |
| Pre-install SHA reads | R1/R2/R2b `825b436d…531254` ×2 match each |
| Installed `base.apk` SHAs | R1 `…-rNtk-clvdpFRkWFtZHqWXw==`, R2 `…-oT9tIsmBnCw2rmNgHA4FvQ==`, R2b `…-rKnedQzg6II7qeuwr5Ef_Q==` — all match |
| Pins | fork `5d5c382` + paraLLEl-GS `1b3a294` per F7; 1× + `PS2X_PGS_PRESENT_PIPELINE=1`; MTVU + VU1 blocks; GameThread cpu6, MTVU unit cpu7 |
| Unstripped `.so` (bytesize) | `/home/brad/vr3/PS2Recomp/android/app/build/intermediates/cxx/RelWithDebInfo/1q4v1f66/obj/arm64-v8a/libps2EntryRunner.so`, 1,327,528,856 B, SHA `01fceae5…2273ea`, BuildID `837d7dbb…14fa` **= APK's**; `file`: ELF aarch64, with debug_info, not stripped |

## Env (full CP1 env per run; Brad's play env restored after every run)

Play keys: `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`,
`PS2X_CD_IMAGE=…/SSX3.iso`, `PS2X_SKIP_MOVIE=1`, `PS2X_SOUND=1`,
`PS2X_PGS_PRESENT_PIPELINE=1`, `PS2X_MTVU=1`, `PS2X_VU1_BLOCKS=1`,
`PS2X_GAME_THREAD_CPUS=6`, `PS2X_MTVU_CPUS=7` (+ test keys
`PS2X_MC_ROOT=…/mc0-test`, I26-FAST `PS2X_PAD_SCRIPT`,
`PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_VSYNC_RATE_LOG=1`, `PS2X_UNPACED=1`).

| Item | Result |
| --- | --- |
| Run env SHAs (device) | R1 `76ba7d54…d17e5`, R2 `55a27962…d57d5e`, R2b `2b786cd5…bd740e` (play keys + I26-FAST + mc0-test + vsync-rate + unpaced; comment line differs) |
| Pre-run device env | `ef9f94e1…9a390` (play env) every run, else abort |
| Restored env SHA | R1/R2/R2b `ef9f94e1…9a390` match=True (driver) + `odin_restore_play.sh` 6/6 saves OK each |
| Brad `mc0` | 6/6 SHAs match I31 pins before and after every run (read-only; never written) |
| `mc0-test` | created empty, empty before each run, removed at close |

## Launches

Route I26-FAST. Every PRE: lease free, keyguard `showing=false`, 100% on
AC, app stopped, play env, mc0 pins. Every run: install Success,
force-stopped after, env restored, lease released.

| Launch | Window | Cooldown | Result | Receipts |
| --- | --- | --- | --- | --- |
| R1 clean anchor | tick 0→4519, 157 s wall | PRE status 0 (34.1 °C) + 180 s → POST 0 | STOP 4519; race 23.00/s = 0.384×; 0 FATAL; 100→100% | `logs/R1/` + 4 PNGs in scratch |
| R2 offcpu profile | tick 0→1949, 54 s wall | PRE status 0 (36.4 °C) + 180 s → POST 0 | **profile failed**: `--trace-offcpu` needs `-e cpu-clock` (`cmd_record.cpp:1405`); 0-byte perf.data; fallback check missed it (file-exists vs size). 0 FATAL; 100→100% | `logs/R2/` + 2 PNGs in scratch |
| R2b offcpu profile | tick 1949→2340 profiled, 72 s wall | PRE status 0 (35.6 °C) + 180 s → POST 0 | 20.0 s profile, 474,268 samples, `perf-R2b.data` 106.8 MB (`1f835a3a…`); 0 FATAL; 100→100% | `logs/R2b/` + 2 PNGs + perf.data in scratch |
| R3 flush split | tick 0→4563, 157 s wall | PRE status 0 (34.9 °C) + 180 s → POST 0 | STOP 4563; race 23.34/s = 0.389× (diagnostic, timers on); split = submit_empty; 0 FATAL; 100→100% | `logs/R3/` + 4 PNGs in scratch |
| R4 LAG timeline | tick 0→4562, 147 s wall | PRE status 0 (36.8 °C) + 180 s → POST 0 | STOP 4562; race 25.23/s = 0.421×; 0 FATAL; 100→100% | `logs/R4/` + 4 PNGs in scratch |
| R3 flush_submit split | only if R2 shows the GsWorker blocked there | — | not found | `logs/R3/` |
| R4 LAG timeline | optional | — | not found | `logs/R4/` |

## Table 1 — R1 anchor: per-phase rates + counters

Guest vsyncs/s (`phases.py`; STOP-capped race 1714→4519 / 121.9 s):

| Phase | Ticks | vsyncs/s | × |
| --- | --- | ---: | ---: |
| title/startup | 0→636 | 56.01 | 0.934 |
| main menu | 636→766 | 60.00 | 1.001 |
| Select Character | 766→884 | 60.00 | 1.001 |
| Setup Character / Peak | 884→1099 | 60.00 | 1.001 |
| Select Mode / Event / My Rules | 1099→1440 | 55.95 | 0.933 |
| loading + Rival card | 1440→1714 | 30.72 | 0.513 |
| **race** | **1714→4519** | **23.00** | **0.384** |

Race per-5s: 18.8 19.0 18.2 19.7 19.9 19.7 21.0 23.0 23.9 24.6 22.9
23.4 24.5 24.0 22.9 24.2 24.2 23.3 23.2 24.9 24.6 24.2 27.5 31.7
(warmup ramp + wind-down speedup, same shape as F7).

Counters (race window unless noted):
`[mtvu] threaded tick=4500 lag=0 jobs=55479 violations=0 waits:
vblank=2975/97253.8ms` (F7 D2: 2938/95.7 s — agrees).
`[gs:parallel] sync` (per present, presents=3600 line):
flush_submits 4.09, frame_ctx_wait 0.42 ms, timeline_waits 0,
**flush_submit 22.6 ms**, iface_flush 7.50, iface_vsync 0.43
(VK1 L2 1×: 23.4 / 6.5 / 0.29 — agrees).
`[gs:parallel] periodic`: present_ms_avg 7.47, readback/copy 0,
vk_queued=4174 vk_dropped=0 vk_timeouts=0, vk_apply 0.150 ms,
vk_latch_interval 35.70 ms.
Screencap R1 sc01 (tick~2126, viewed): race 2ND/2 00:00:07 1%, rider
down in spray, full-screen 1920×1080, EA Radio "Emerge - Junkie XL
Remix / Fischerspooner".

## Table 2 — THE POINT: per-thread running / runnable / blocked (ms per guest frame, matched window)

Matched window R2b: exact ticks 1983→2403 (420 frames; schedstat sample
edges t+47.6→68.6, 21.0 s wall = 50.00 ms/frame; simpleperf record span
20.020 s ≈ 405 frames inside it). run/wait from schedstat deltas;
blocked = wall − run − wait; three methods agree within 1–6%
(schedstat vs cpu-clock vs switch pairs; see §Method). Blocked splits
from time-weighted sleep-stack classification (`reports/classes.txt`).

| Thread (TID) | running | runnable | blocked (wait object/reason) | core + freq residency |
| --- | ---: | ---: | --- | --- |
| MTVU unit (30588) | 30.1 | 0.9 | **19.0** = 12.2 starved for jobs (`Worker::loop` → `cvWork.wait`) + 6.7 GS-queue-full (`GsWorker::enqueue` → `m_hasSpace.wait`) + 0.3 other | cpu7 pinned (8/8 samples); cpu7 3801–4320 MHz in-window (R1 exact: 4089 27%, 4320 26%, 3801 15%, 4204 7%) |
| GameThread (30578) | 13.1 | 0.2 | **36.7** = 36.2 vblank (`ps2_mtvu::vblank` → `Worker::waitFor` → cond) + 0.5 other | cpu6 pinned (8/8); cpu6 3072–4320 MHz in-window (R1 exact: same cluster table as cpu7) |
| GsWorker (30557) | 9.7 | 3.7 | **36.6** = ~19.5 queue-empty (`threadMain` → cond) + ~19.1 kgsl fence (`__ioctl` sleep; userspace parent unbinned — kernel-only unwind; ±20% split, see gaps) | roams cpu 0/1/2/4/5 (never 6/7 in 8 samples); 181,700 slices/window |
| Turnip worker ×4 (30581–84) | 40.4 / 40.0 / 31.7 / 3.3 each (transient; exited t+49/+61/+64/+64; 96% busy while alive) | — | ~0.3 each | roam all cores incl. 6/7 (sampled on 0/1/2/4/5/6/7) |
| main (30555) | 0.1 | 0.0 | 49.7 looper/present wait (13.6 bottom-at-`main` + 6.4 futex-cond of 20.0 paired) | roams |
| AAudio_1 (30576) | 0.2 | 0.0 | 49.8 audio-callback waits | roams |
| PGS-Waiter (30580) | 0.1 | 0.1 | 49.9 futex-cond (idle timeline waiter; `timeline_waits=0`) | roams |

Critical path (observed dependencies): **the MTVU unit gates frame
completion.** GameThread's 36.2 ms/frame vblank wait ends when the unit
completes the frame's jobs; the unit works 30.1 and stalls 19.0 (12.2
waiting for GameThread submissions + 6.7 on the GS queue); the GS queue
drains through GsWorker-30557, which is itself fenced on the GPU ~19.1
ms/frame inside `flush_submit`'s span (`[gs:parallel] sync`:
flush_submit 22.6 ms/present). R3 splits that span; R4 tests LAG on the
12.2 ms starvation.

## Table 3 — top-5 self-time symbols on the critical-path thread

MTVU on-cpu self (cpu-clock event counts ÷ 405 record frames; total
oncpu 12.13 s = 30.0 ms/frame):

| # | ms/frame | Symbol |
| ---: | ---: | --- |
| 1 | 2.29 | `[kernel.kallsyms][+ffffffe761a8e810]` (running kernel, same PC as N12's #1 row; no kallsyms names on this ROM) |
| 2 | 2.20 | `VU1RecompImage<17692172933381506641>::B2a10` (VU1 **block**) |
| 3 | 1.48 | `VU1RecompImage<11917748289753363281>::B0628` (VU1 **block**) |
| 4 | 1.30 | `VU1Interpreter::commitReadyPipelines()` |
| 5 | 0.86 | `PS2Memory::processVIF1DataImpl` |
| 6 | 0.85 | `VU1RecompImage<17692172933381506641>::B0a58` (VU1 **block**) |

VU1 generated blocks dominate MTVU's on-cpu (next: `progressXgkick`
self 0.3, children 24.7% incl. the GIF/enqueue path). GameThread's
on-cpu top (for scale): `execUpper` 1.71, `VU1Interpreter::run` 1.57
(both = the interpreted **VU0** path via `executeVU0Microprogram`
9.91%), `commitReadyPipelines` 0.88, guest `sub_0037E120` 0.36.

## Table 4 — GPU busy % and GPU time per frame

| Window | kgsl busy % (n) | gpuclk | busy × wall/frame (crude) |
| --- | ---: | --- | ---: |
| R2b profile (in-window, 2.6 s cadence) | 47.1 47.0 49.1 47.9 48.2 46.9 48.0 56.4 56.1 (mean 49.6) | 660 MHz all 9 | 49.6% × 50.00 = **24.8 ms/frame** |
| R1 race window (5 s cadence) | mean 50.9 (n=6) | 660 MHz | 50.9% × 48.78 = **24.8 ms/frame** |
| R1 GPU freq residency | 100% at 660 MHz (`gpu_clock_stats` delta all in the 660 bin) | — | — |

GPU-busy-per-frame agrees to 0.0 ms between the clean (R1) and profiled
(R2b) windows. Per-guest GPU timestamps: not obtained (no calibrated
timestamp capture on this route).

## Method (three independent clocks, one window)

1. **schedstat** (primary for run/runnable/blocked): per-thread
   `/proc/<pid>/task/<tid>/schedstat` (run ns, runqueue-wait ns) +
   `stat` (CPU ticks, current CPU) sampled at ~2.6 s during the R2b
   profile (`logs/R2b/profile-samples.txt`, 9 groups) and at the R1
   cpu-window edges (`logs/R1/schedstat.txt`). blocked = wall − run −
   wait. Ticks at sample edges interpolated from epoch-stamped
   `[vsync-rate]` lines (±1 tick; driver poll ticks are ±40).
2. **cpu-clock** (on-cpu + self symbols): `simpleperf record -g -e
   cpu-clock --trace-offcpu --app` (R2b: 19.9938 s, 474,268 samples).
   On-cpu seconds per thread = cpu-clock event counts; self symbols
   from the same.
3. **sched_switch** (exact off-CPU + wait objects): context-switch
   records pair off→on per thread; each off-sample's dwarf callchain
   is classified (enqueue / futex-cond / ioctl-fence / other) and
   weighted by its sleep duration (`reports/classes.txt`, classifier
   at `~/dev/ssx3-work/CP1/classify.py`, run on bytesize over the
   streamed `report-sample --show-callchain` output).

Cross-checks (R2b, per frame): MTVU run 30.1 (schedstat) vs 30.0
(cpu-clock); blocked 19.0 vs 19.2 (switches). GameThread 13.1 vs 12.7;
36.7 vs 36.2. GsWorker-30557 9.7 vs 10.0; 36.6 vs 38.8 (widest gap, 6%;
   window-edge + unpaired sleeps, see gaps).

## Symbolization

Bytesize NDK simpleperf
(`/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf/…`;
bytesize idle, `ps aux` first) + symdir (VR3 unstripped `.so`
`01fceae5…`, Build ID `837d7dbb…14fa` = APK's, + device `libc.so`
`dd242326…`). N5 `report.sh` recipe: threads, per-TID, self/comm-sym,
self/sym-dso, dso, children (≥1%), per-thread children (MTVU,
GameThread, GsWorker, PGS-Waiter ≥0.5%), per-TID GsWorker symbols,
caller graphs (MTVU, GameThread — kept in scratch, 1.3 MB).

- R2b: 474,268 samples, 204.9 s thread-time, **0 unresolved rows in
  our `.so`**; 16 Turnip-offset rows (stripped adrenotools build, as
  N11/N12); kernel rows address-only (kptr_restrict, no kallsyms).
- Reports committed: `reports/threads.txt`, `tid.txt`,
  `self-comm-sym.txt`, `self-sym-dso.txt`, `dso.txt`, `children.txt`,
  `child-{MTVU,GameThread,GsWorker,PGS-Waiter}.txt`, `classes.txt`.
  Full perf data (106.8 MB) + graphs stay in scratch
  (`~/dev/ssx3-work/CP1/`).

## R3 — flush_submit split (one Android build + one launch)

Justification (brief step 3): R2b shows GsWorker-30557 blocked ~19.1
ms/frame in a kgsl-fence ioctl inside `flush_submit`'s 22.6 ms/present
span, propagating 6.7 ms/frame of GS-queue backpressure onto MTVU, the
frame's gating thread. Condition met.

Build (1/1): fork branch `cp1` `10dfcb2` (= `5d5c382` + sync-line
print of 3 fields) + paraLLEl branch `cp1` `b0e331a` (= `1b3a294` +
default-off `PS2X_PGS_FLUSH_SPLIT` timers around the 6 `device->submit`
sites, the 2 `submit_empty` sites and `drain_compilation_tasks_nonblock`;
env read once, first flush; off = one branch per site). VR3's
`build-android-vr3.sh` recipe verbatim except the two source roots
(same codegen/VU1/VU0/jniLibs, same `-O3`, `--max-workers=2`).
**BUILD SUCCESSFUL in 23 m 3 s.** APK
`484dc4dbbf0266a2907080a3537522c81817d15f03f71878e99d436a85a268c7`
(remote ×2 + local ×2 + installed base.apk match), 190,748,236 B.
Runner-dir guard (`git diff --stat 14b1e5cb cp1 --
ps2xRuntime/src/runner`) empty. Branches local, never pushed.

Run: env `cb69ad79…` (play keys + `PS2X_PGS_FLUSH_SPLIT=1`), STOP 4563,
race 23.34/s = **0.389×** (diagnostic: timers on; cf. R1 0.384× —
timers cost nothing measurable). `[mtvu] jobs=55501` (deterministic,
as F7), vblank 2934/95.8 s, violations 0. Cap sc01 viewed: race 2ND/2
00:00:08 1%, rider down in spray, 15 MPH, full-screen.

Split (ms per present, race `[gs:parallel] sync` lines):

| presents | flush_submits | frame_ctx | timeline | flush_submit | **submit** | **submit_empty** | **drain** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3300 | 4.07 | 0.37 | 0 | 22.52 | **0.0064** | **22.10** | **0.0004** |
| 3600 | 4.12 | 0.38 | 0 | 22.16 | **0.0064** | **21.73** | **0.0005** |
| 3900 | 4.11 | 0.37 | 0 | 22.41 | **0.0064** | **22.00** | **0.0004** |
| 4200 | 4.51 | 0.36 | 0 | 22.38 | **0.0076** | **21.97** | **0.0004** |
| 4500 | 4.09 | 0.33 | 0 | 19.38 | **0.0066** | **19.01** | **0.0004** |

Closure (presents=3600 line): 0.0064 + 21.7337 + 0.0005 + 0.3846 =
22.13 vs flush_submit 22.16 (residual 0.04 ms = barrier/CPU work
between the timed regions). **The ~22 ms wait is essentially all in
the two `submit_empty` timeline-signal submits** (~5.5 ms per flush
each); the main submits are 6 µs (pure queueing) and the compile
drain is 0.4 µs (nothing queued — compilation runs on Turnip's own
threads, Table 2).

R3 three-way (exact ticks 1984→2621, 636.5 frames, 47.29 ms/frame):
MTVU 28.1 / 0.5 / 18.7, GameThread 12.0 / 0.1 / 35.2, GsWorker 9.9 /
3.4 / 34.0 — agrees with R1 (timers ~free).

## R4 — LAG timeline (optional)

Run: play APK `825b436d…`, env `145da62b…` (play keys +
`PS2X_MTVU_LAG=1`), STOP 4562, race 25.23/s = **0.421×** (F7 E leg
25.45/s = 0.425× — agrees). `[mtvu] lag=1 jobs=55501 violations=0
waits: vblank=2916/86.2 s` (vs R1 2975/97.3 s). Cap sc01 viewed: race
2ND/2 00:00:08 1%, rider carving, 14 MPH, full-screen (no LAG artifact
at this tick, as F7 E).

Identical-tick LAG effect (ticks 2000→2500, interpolated): R1 24.59 s
= 49.19 ms/frame vs R4 21.92 s = 43.85 ms/frame → **−5.34 ms/frame
(−10.9%, 1.122×)**.

R4 three-way (exact ticks 2054→2609, 554.5 frames, 42.02 ms/frame):
MTVU 27.0 / 0.5 / 14.6, GameThread 12.4 / 0.1 / 29.5, GsWorker 8.6 /
2.3 / 31.0. Deltas vs R1's window (48.78 ms/frame; partly the faster
tick range — the identical-tick −5.3 is the fair LAG number): frame
−6.8, MTVU blocked −3.6, GameThread blocked (vblank) −6.4, runs
~flat (MTVU −1.7 incl. tick range, GT +0.2). No R4 profile was taken,
so R4's blocked time is unsplit (gap).

## Exact commands

```sh
mkdir -p local/research/CP1/logs local/research/CP1/reports ~/dev/ssx3-work/CP1
cp local/research/F7/launch.py local/research/F7/cooldown.py local/research/CP1/
cp local/research/F4/phases.py local/research/CP1/  # (+ CP1 edits: play pin ef9f94e1, CP1 paths/lease, --offcpu, schedstat+residency, concurrent sampler)
python3 local/research/CP1/cooldown.py --label R1  # + R2, R2b
python3 local/research/CP1/launch.py --label R1 --variant A --wall 600 --stop-tick 4500 --cpu-window 1900,2500 --apk ~/dev/ssx3-work/odin-play/app-release.apk --apk-sha 825b436d… --env PS2X_MTVU=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7
# R2/R2b: + --profile-after-tick 1936 --profile-secs 20 --offcpu (R2b after the -e cpu-clock fix)
bash local/tooling/odin_restore_play.sh CP1-R1  # + CP1-R2, CP1-R2b (after every run)
python3 local/research/CP1/phases.py local/research/CP1/logs/R1
adb -s $S pull /system/lib64/libc.so ~/dev/ssx3-work/CP1/libc-device.so
ssh bytesize 'wsl -d Ubuntu -- bash -lc "cat > /home/brad/cp1/prof/perf-R2b.data && sha256sum …"' < ~/dev/ssx3-work/CP1/odin/R2b/perf-R2b.data  # + libc, SHAs match both ends
# bytesize (one held ssh): symdir stage + simpleperf report x(threads, tid, self x2, dso, children, 4x child-T, tidsym, 2x graph); classify.py over report-sample; tar back
# R3 patch (scratch worktrees, local branches, never pushed)
git -C ~/dev/PS2Recomp worktree add -b cp1 ~/dev/ssx3-work/CP1/PS2Recomp 5d5c382
git clone ~/dev/parallel-gs ~/dev/ssx3-work/CP1/parallel-gs  # + checkout -b cp1 1b3a294, submodules
# (+ CP1 edits: PGS b0e331a timers, fork 10dfcb2 print; runner-dir guard empty)
git -C ~/dev/ssx3-work/CP1/PS2Recomp archive --format=tar cp1 > fork-cp1.tar  # 80ef3cdb… both ends
tar -cf pgs-cp1.tar --exclude=.git -C ~/dev/ssx3-work/CP1 parallel-gs  # ad98d26b… both ends
ssh bytesize 'wsl -d Ubuntu -- bash -lc "cat > /home/brad/cp1/fork-cp1.tar && sha256sum …"' < fork-cp1.tar  # + pgs, build.sh
ssh bytesize 'wsl -d Ubuntu -- bash -lc "/home/brad/cp1/build.sh"'  # VR3 recipe; BUILD SUCCESSFUL 23m3s; APK 484dc4db…
ssh bytesize 'wsl -d Ubuntu -- bash -lc "cat /home/brad/cp1/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk"' > ~/dev/ssx3-work/CP1/odin/app-release-r3.apk  # 484dc4db… x2
python3 local/research/CP1/launch.py --label R3 --variant A --wall 600 --stop-tick 4500 --cpu-window 1900,2500 --apk …/app-release-r3.apk --apk-sha 484dc4db… --env PS2X_MTVU=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 --env PS2X_PGS_FLUSH_SPLIT=1
python3 local/research/CP1/launch.py --label R4 … --apk ~/dev/ssx3-work/odin-play/app-release.apk --apk-sha 825b436d… --env PS2X_MTVU=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 --env PS2X_MTVU_LAG=1
bash local/tooling/odin_restore_play.sh CP1-R3  # + CP1-R4 (after every run)
```

## Gaps

| Gap | Reason |
| --- | --- |
| GsWorker-30557's blocked split ±20% | 3.46 s of its 15.70 s switch-off (22%) has no paired sleep sample (unwind/sample drops under 17.6k switches/s); pro-rata 50/50 with the bound stated. R3's hardware counters are authoritative for the fence side |
| Fence-ioctl sleep stacks are kernel-only | dwarf unwind fails at the kernel boundary for the kgsl waits, so no userspace caller (flush_submit vs Present) from stacks; placed in `flush_submit` by elimination with the sync counters (frame-ctx 0.4 + timeline 0 + readback 0.3 « 19.1). R3 confirms |
| R2b schedstat edges ±1 s vs record span | first/last sampler groups bracket the 20.02 s record; per-frame uses each span's own interpolated ticks (420 vs ~405 frames) |
| Turnip/kernel symbol names | stripped adrenotools build (16 offset rows); kptr_restrict, no kallsyms (as N11/N12) |
| R2's launch spent on a driver bug | `--trace-offcpu` requires `-e cpu-clock`; fallback checked file existence, not size. Fixed + re-ran as R2b (3/5 launches used before R3/R4) |
| R2 t=60.7 sched group missed all GsWorkers | sampler/parser glitch for one 2.6 s group (30583 exiting mid-read); other 8 groups complete |
| R4's blocked time is unsplit | no LAG profile taken (launch budget); R4 gives run/runnable/blocked + counters only, no sleep-stack split |
| R3's first attempt died pre-launch | driver PGS-key allowlist missed `PS2X_PGS_FLUSH_SPLIT` (assert after install, before launch); fixed, re-ran. No launch consumed |
| R4 window ticks differ from R1's | R4 cpu-window landed 2054→2609 vs R1 1969→2568; the identical-tick 2000→2500 comparison (−5.34) is the fair LAG number |

Budgets: 1/1 Android builds (23 m 3 s), 5/5 launches (R1 157 s, R2
54 s failed profile, R2b 72 s, R3 161 s, R4 151 s wall; all ≤ 600 s),
~3 h of 3 h. Scratch `~/dev/ssx3-work/CP1/` 2.3 GB (≤ 5 GB brief cap;
perf.data 107 MB + APKs + worktrees). Mini 85.3 → 91.4 GB of 200.
Never pushed; fork/PGS `cp1` branches local only; text in git
(REPORT, 2 Odin scripts, phases, 9 report files); runners signalled
only by the drivers; no lease held at close; play state restored
(APK `825b436d…`, env `ef9f94e1…`, 6/6 saves, app stopped).
