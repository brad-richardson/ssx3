# N12 — Odin per-stage re-profile on the F5 play build

Worker: Muse Code. Brief: `local/muse/prompts/N12.md`. Date: 2026-09-25.
Method: F5 `launch.py` + `cooldown.py` adapted (play-env pin `a8d651a7…`,
N12 paths/lease, `--variant` default A, profiler command N11-verbatim
`simpleperf record -g --app`); rates via F4 `phases.py`; buckets via N11
`buckets.py` + the brief's new VU1/VU0/`__memset` shapes + a `--counts`
mode (exact event-count shares, 100% of samples). No fork edits, no
builds. **Measurement only; no conclusions** (brief §Goal).

## Status

**3/3 launches; all five tables delivered.** S1 clean race 14.64/s =
0.244× (anchor for k). S2 race profile tick 2468→~2930, 130,822 samples,
0 unresolved rows. S3 profile tick 867→~1802 — **not pure menus** (see
§S3 window): SC-tail → setup → mode/event → loading → early race, 600,515
samples, 0 unresolved. Key rows (S2, GameThread-bound, k = 0.7848):
**VU1 total 59.53% = 46.72 ms** (generated 48.41/37.99 + interpreter/other
7.93/6.22 + issue/hazard 3.19/2.50), **GameThread-minus-VU1 27.51% =
21.59 ms**, GsWorker 9.20% = 7.22 ms.

## Build (F5 play build, installed before each run)

| Item | Result |
| --- | --- |
| APK | `~/dev/ssx3-work/F5/odin/app-release.apk`, `4ff81032a175689be276819381f5ff52710e37101f99289d76b25a5c95609753`, 186,947,144 B |
| Pre-install SHA reads | `4ff81032…09753` ×2 match |
| Installed `base.apk` SHAs | S1 `…/com.ps2x.runner-qF-IuaVNm3JnWbY80ArfwQ==/base.apk` ×2 match; S2 `…/com.ps2x.runner-WSCgaD2JPMF3qPfspf2iVA==/base.apk` ×1 match; S3 `…/com.ps2x.runner-uOg1LE2w5bsMaJZjY37MtQ==/base.apk` ×1 match |
| Pins | PS2Recomp `a3efbfe` + paraLLEl-GS `19d93b2` per F5; 1× + `PS2X_PGS_PRESENT_PIPELINE=1`; diagnostics off; profileable since F1 |
| Unstripped `.so` (bytesize) | `/home/brad/f5/…/cxx/RelWithDebInfo/y195x5l4/obj/arm64-v8a/libps2EntryRunner.so`, 1,225,766,664 B, SHA `0e11119f…aa04`, BuildID `e39b09b3…9999` |

## Env (full N12 env per run; Brad's play env restored after every run)

Play keys: `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`,
`PS2X_CD_IMAGE=…/SSX3.iso`, `PS2X_SKIP_MOVIE=1`, `PS2X_SOUND=1`,
`PS2X_PGS_PRESENT_PIPELINE=1` (+ test keys `PS2X_MC_ROOT=…/mc0-test`,
I26-FAST `PS2X_PAD_SCRIPT`, `PS2X_PAD_SCRIPT_CLOCK=vsync`,
`PS2X_VSYNC_RATE_LOG=1`, `PS2X_UNPACED=1`).

| Item | Result |
| --- | --- |
| S1/S2/S3 env SHA (device) | `d7dd9564…84ec45` / `8fefb12c…ca885a8` / `1ac10f4c…5343f5ce` (comment line only differs) |
| Pre-run device env | `a8d651a7…0ebd` (Brad's play env) all 3 runs, else abort |
| Restored env SHA | `a8d651a7…0ebd` match=True after S1, S2, S3, and final check |
| Brad `mc0` | 6/6 SHAs match I31 pins before S1 and after every run (read-only; never written) |
| `mc0-test` | created empty, empty before each run, empty after (game wrote nothing), removed at close |

## Launches

Route I26-FAST, `--stop-tick 4500`, `--wall 600`. Every PRE: lease free,
keyguard `showing=false`, 100% on AC, app stopped, Brad play env, mc0
pins. Every run: install Success, focus foreground (no BACK needed),
force-stopped after (pid-after=none), env restored, lease released.
Transport: Wi-Fi TLS serial `adb-622c49b1-IJnTHA._adb-tls-connect._tcp`
all runs, **0 disconnects** (`transport-start/end.txt` per run).

| Launch | Window | Cooldown (fixed 180 s waits recorded) | Result | Receipts |
| --- | --- | --- | --- | --- |
| S1 clean | tick 0→4582, 241 s wall | PRE status 0 immediate (34.5 °C) + 180 s → POST 0 | STOP tick 4582; 0 FATAL; battery 100→100% | `logs/S1/` + 4 PNGs in scratch |
| S2 race profile | tick 2468→~2930 in 30.9 s wall (14.96/s, unperturbed §) | PRE status 0 (47.3 °C) + 180 s → POST 0 (36.8 °C) | 30 s profile from t+101.9; `perf-S2.data` 23.6 MB (`afde7322…`); 0 FATAL; 100→100% | `logs/S2/` + 3 PNGs |
| S3 menu profile | tick 867→~1802 in 34.9 s wall (26.8/s) — menus+loading+early race | PRE status 0 (47.7 °C) + 180 s → POST 0 (36.8 °C) | 30 s profile from t+16.8; `perf-S3.data` 90.4 MB (`4db1d33b…`); 0 FATAL; 100→100% | `logs/S3/` + 3 PNGs |

S2 window rate 14.96/s vs S1 clean ~14.8/s over the same ticks: no
measurable profiler perturbation (cf. N11's 9% slowdown). S2/S3
pre-profile phases match S1 within noise (title 50.8, menu 53.0, SC 54.8,
setup 67.0, mode 54.7, loading 19.1/17.9 — see `phases.py` outputs in
driver logs). Logcat keys S1: `[padscript] armed n=31 source=env
clock=vsync`, `[snd-output] stream rate=48000 channels=2 bits=16`,
`[gs-path] … gpu=Adreno (TM) 830`, zero FATAL (all runs).

Device left: lease `LEASE_FREE N12 done`, play APK + env `a8d651a7…`,
mc0 pins match, `/data/local/tmp/n12` + `mc0-test` removed, app stopped.

## Table 1 — S1 per-phase rates vs N11 S1 and F5 Part 2

Guest vsyncs/s and ratio ÷59.94 (`phases.py` on epoch-stamped
`[vsync-rate]` lines). F5 Part 2 published race only (A legs R1/R4).

| Phase | N12 S1 /s | N12 S1 × | N11 S1 × | F5 R1/R4 × |
| --- | ---: | ---: | ---: | --- |
| Title/startup (0→636) | 50.91 | 0.849 | 0.533 | — |
| Main menu (636→766) | 52.96 | 0.884 | 0.488 | — |
| Select Character (766→884) | 54.82 | 0.915 | 0.266 | — |
| Setup Character / Peak (884→1099) | 67.12 | 1.120 | 0.391 | — |
| Select Mode / Event / My Rules (1099→1440) | 54.78 | 0.914 | 0.582 | — |
| Loading / Rival card (1440→1714) | 19.07 | 0.318 | 0.190 | — |
| **Race (1714→4582)** | **14.64** | **0.244** | **0.117** | **0.245 / 0.244** |

S1 race per-5s: 9.4 9.6 10.0 11.4 13.0 13.2 13.6 13.4 13.4 14.4 14.6 14.4
15.0 15.0 15.2 15.2 15.0 14.8 15.0 15.4 15.0 15.2 15.0 14.8 15.2 15.0 15.2
15.2 14.8 15.0 15.0 15.2 15.4 14.8 15.4 18.0 17.2 19.2 20.2 (warmup ramp +
final-bins speedup, same shape as N11/F5). SF presents/s: race 59.7–60.4
(n=17); menu phases n≤1 (phases pass between 10 s polls, as N11).

## Table 2 — S2 race stage table vs N11 S2

Conversion model (N11's, stated): sample share × scale k. S2 race is
GameThread-bound (87.04% of event counts), so GameThread ms/frame =
clean race wall/frame W = 68.31 ms (S1 race: 2868 vsyncs / 195.9 s) →
**k = 68.31/87.04 = 0.7848 ms per 1%**. Shares are exact event-count
fractions (`report --print-event-count`, limit 0: 8,500 rows, 100.00%
of 98,380,655,774 cycles). N11's column is its published ≥0.05% table
(92.11% covered, k = 1.7122); the N12@0.05 column is the like-for-like
cutoff recomputation (59.25% covered). Cutoff notes: N11 guest 0.38% is
≥0.05%-rows only; N12 guest 8.71 ms = 5.09% at N11's k, which fits inside
N11's 7.89% unmapped tail (consistency check, not a correction).

| Stage | N12 share | N12 ms | N11 share | N11 ms | N12@0.05 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **VU1 generated pairs** | 48.41% | 37.99 | — | — | 21.45% |
| **VU1 interpreter/other** | 7.93% | 6.22 | (in exec) | (48.2) | 7.83% |
| **VU1 issue/hazard** | 3.19% | 2.50 | (haz 40.92) | (70.1) | 3.19% |
| **VU1 TOTAL** | **59.53%** | **46.72** | **69.09%** | **118.3** | **32.47%** |
| **GameThread-minus-VU1** | **27.51%** | **21.59** | **15.83%** | **27.1** | — |
| libc/kernel/vdso | 13.77% | 10.81 | 14.53% | 24.9 | 11.82% |
| guest code | 11.10% | 8.71 | 0.38% | 0.7 | 3.57% |
| paraLLEl CPU submit | 3.05% | 2.39 | 0.36% | 0.6 | 2.48% |
| other | 2.78% | 2.18 | 0.30% | 0.5 | 1.47% |
| GIF/GS packet handling | 2.70% | 2.12 | 0.80% | 1.4 | 2.52% |
| scheduler/sync/waits | 2.14% | 1.68 | 0.60% | 1.0 | 1.62% |
| VIF1/DMA | 1.13% | 0.89 | 0.30% | 0.5 | 1.12% |
| PS2 runtime other | 1.05% | 0.82 | 0.14% | 0.2 | 0.48% |
| profiler unwind overhead | 0.91% | 0.71 | 0.14% | 0.2 | 0.80% |
| EE runtime helpers | 0.80% | 0.63 | 0.53% | 0.9 | 0.52% |
| Vulkan driver CPU (Turnip) | 0.36% | 0.28 | — | — | <0.05/row |
| __bzero/__memset zeroing | 0.29% | 0.23 | (in libc) | — | 0.24% |
| SND/audio | 0.19% | 0.15 | — | — | <0.05/row |
| PLT | 0.15% | 0.12 | 4.94% | 8.5 | 0.08% |
| VU0 (self only; subtree §) | 0.06% | 0.05 | — | — | 0.06% |
| tail (unmapped) | 0.00% | 0.00 | 7.89% | 13.5 | 40.75% |

S2 thread rows (CPU-ms per guest frame): GameThread 68.31 (by
construction), **GsWorker 7.22**, main 2.61, AAudio 0.16. Total ≈ 78.3 ms
= 1.15 cores. DSO: our `.so` 83.07%, kernel 8.31%, libc 6.29%, vdso
0.95%, Adreno GLES 0.40%, Turnip 0.37%. Children: `EeScheduler::run`
85.77% → guest `sub_00382760` 64.95% → `Store32` → `writeIORegister` →
`processPendingTransfers` → `processVIF1Data[Impl]` →
`VU1Interpreter::run` 67.42% (children) / 2.52% (self).

VU0 / execUpper subtree (children view): `executeVU0Microprogram`
children = **7.02%**, self 0.06%. `execUpper` self 2.419% +
`execLower` self 0.320% are `VU1Interpreter::` symbols shared between
the VU0 path and the VU1-interpreter path — **not separable** from
these reports (brief's anticipated outcome). The 7.02% VU0 subtree
overlaps the `VU1 interpreter/other` bucket (its execUpper/Lower self);
it is not an additional row. `executeVU0Microprogram` is called from
guest `sub_0022ADD8` (children 6.87%).

## Table 3 — S2 top-25 GameThread symbols + top-10 generated pairs

Shares of ALL samples; ms = share × 0.7848.

| # | Share | ms | Symbol (truncated) |
| ---: | ---: | ---: | --- |
| 1 | 4.719% | 3.70 | `[kernel.kallsyms][+ffffffe761a8e810]` |
| 2 | 3.189% | 2.50 | `VU1Interpreter::commitReadyPipelines()` |
| 3 | 2.522% | 1.98 | `VU1Interpreter::run(…)` |
| 4 | 2.419% | 1.90 | `VU1Interpreter::execUpper(unsigned int)` |
| 5 | 1.125% | 0.88 | `PS2Memory::processVIF1DataImpl(…)` |
| 6 | 0.892% | 0.70 | `VU1Interpreter::progressXgkick()` |
| 7 | 0.679% | 0.53 | `__memcpy_aarch64_nt` |
| 8 | 0.621% | 0.49 | `VU1RecompImage<…6641>::f2a18(…)` |
| 9 | 0.615% | 0.48 | `VU1RecompImage<…6641>::f2a10(…)` |
| 10 | 0.615% | 0.48 | `[kernel.kallsyms][+ffffffe760a2784c]` |
| 11 | 0.573% | 0.45 | `__vfprintf` |
| 12 | 0.556% | 0.44 | `libunwind::findUnwindSectionsByPhdr(…)` |
| 13 | 0.552% | 0.43 | `VU1RecompImage<…6641>::f2a20(…)` |
| 14 | 0.499% | 0.39 | `sub_0037E120_0x37e120(…)` |
| 15 | 0.473% | 0.37 | `VU1RecompImage<…6641>::f2a50(…)` |
| 16 | 0.456% | 0.36 | `__emutls_get_address` |
| 17 | 0.415% | 0.33 | `VU1RecompImage<…6641>::f2a38(…)` |
| 18 | 0.376% | 0.30 | `VU1RecompImage<…6641>::f2a40(…)` |
| 19 | 0.341% | 0.27 | `__sfvwrite` |
| 20 | 0.325% | 0.26 | `[kernel.kallsyms][+ffffffe761a8e664]` |
| 21 | 0.320% | 0.25 | `VU1Interpreter::execLower(…)` |
| 22 | 0.319% | 0.25 | `pthread_mutex_unlock` |
| 23 | 0.310% | 0.24 | `VU1Interpreter::getDecodedInstructionPairForPc(…)` |
| 24 | 0.300% | 0.24 | `VU1Interpreter::readBranchVi(unsigned char) const` |
| 25 | 0.298% | 0.23 | `scudo::…::quarantineOrDeallocateChunk(…)` |

Top-10 generated pair functions by image hash + pc (hot loops: consecutive
pcs in two images):

| Share | Image hash | pc |
| ---: | --- | --- |
| 0.621% | 17692172933381506641 | 0x2a18 |
| 0.615% | 17692172933381506641 | 0x2a10 |
| 0.552% | 17692172933381506641 | 0x2a20 |
| 0.473% | 17692172933381506641 | 0x2a50 |
| 0.415% | 17692172933381506641 | 0x2a38 |
| 0.376% | 17692172933381506641 | 0x2a40 |
| 0.297% | 11917748289753363281 | 0x0638 |
| 0.286% | 11917748289753363281 | 0x0678 |
| 0.285% | 11917748289753363281 | 0x0710 |
| 0.282% | 17692172933381506641 | 0x2a28 |

Pair-image totals (share of all): `…6641` 19.84%, `…6281` 11.98%,
`…0957` 7.14%, `…3931` 7.14%, `…0532` 2.32% (= 48.42%).

## Table 4 — S3 menu stage table vs N11 S3

**§S3 window: tick 867→~1802 (935 vsyncs in 34.9 s wall = 26.8/s),
i.e. Select-Character tail → Setup/Peak → Mode/Event → loading →
early race (~6 s past tick 1714), NOT the brief's 636–1099.** Cause:
menus now run ~53–67/s (Table 1), so tick 636 passed between the
driver's 2 s logcat polls (first sighting 867), and the 30 s window
covers ~935 ticks. End-of-window cap (`sc02-postprofile`) shows the
race HUD at 00:00:01. Model (N11's, stated): GsWorker-pool-bound
(83.33%; end snapshot 3× GsWorker at 100% + 7.6% ≈ 3.08 cores), so
GsWorker ms/frame = 37.33 ms window wall/frame × 3.08 → **k = 1.3796**
(approximate: end-snapshot anchor, unscaled perturbation). N11's column
is its published ≥0.01% table (71.62% covered, k = 1.5716, window tick
676→1525).

| Stage | N12 share | N12 ms | N11 share | N11 ms | N12@0.05 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vulkan driver CPU (Turnip, stripped) | 65.38% | 90.20 | 39.39% | 61.9 | 19.53% |
| libc/kernel/vdso | 12.66% | 17.47 | 17.93% | 28.2 | 10.26% |
| VU1 generated pairs | 7.67% | 10.58 | — | — | 1.06% |
| scheduler/sync/waits | 5.45% | 7.52 | 4.84% | 7.6 | 5.13% |
| profiler unwind overhead | 1.73% | 2.39 | 0.87% | 1.4 | 1.53% |
| guest code | 1.57% | 2.17 | 0.55% | 0.9 | 0.45% |
| __bzero/__memset zeroing | 1.18% | 1.63 | (in libc) | — | 1.14% |
| other | 1.05% | 1.45 | 0.38% | 0.6 | 0.31% |
| VU1 interpreter/other | 0.88% | 1.21 | (in exec 3.19) | (5.0) | 0.64% |
| paraLLEl CPU submit | 0.50% | 0.69 | 0.03% | 0.0 | 0.19% |
| EE runtime helpers | 0.36% | 0.50 | 0.15% | 0.2 | 0.22% |
| VU1 issue/hazard | 0.33% | 0.46 | (in haz 3.50) | (5.5) | 0.33% |
| GIF/GS packet handling | 0.31% | 0.43 | 0.02% | 0.0 | 0.19% |
| PS2 runtime other | 0.30% | 0.41 | 0.11% | 0.2 | 0.05% |
| PLT | 0.28% | 0.39 | 0.61% | 1.0 | 0.23% |
| VIF1/DMA | 0.24% | 0.33 | 0.05% | 0.1 | 0.24% |
| SND/audio | 0.08% | 0.11 | — | — | <0.05/row |
| VU0 | 0.00% | 0.00 | — | — | <0.05/row |
| tail (unmapped) | 0.00% | 0.00 | 28.38% | 44.6 | 58.50% |

S3 thread rows: GsWorker 115.0 (by construction), GameThread 20.79,
main 2.00, AAudio 0.10. DSO: Turnip 65.60%, our `.so` 14.35%, libc
14.16%, kernel 4.61%. S3 top self rows: `HybridMutex::tryLock` 3.31% /
`unlock` 1.58% (GsWorker lock churn), scudo `allocate` 1.17% /
`deallocate` 1.07% / `quarantine…` 0.97% + `malloc` 0.61% (malloc
traffic), `__memset_aarch64_nt` 1.14%, `__memcpy_aarch64_nt` 0.87%,
top Turnip offset `b40d34` 1.10%. Our own PGS/GS code ≈ 0.8%: window
time is driver-internal + allocator + mutex over ~35k rows.

## Table 5 — thread rows + GPU busy % + thermal per phase

Thread rows (CPU-ms per guest frame): S2 GameThread 68.31 /
GsWorker 7.22 / main 2.61 / AAudio 0.16; S3 GsWorker 115.0 /
GameThread 20.79 / main 2.00 / AAudio 0.10. S1 coarse (`top` TIME+ ÷
4582 ticks): GameThread 161.03 s → 35.1, GsWorker 37.97 s → 8.3, main
14.09 s → 3.1, AAudio 0.89 s → 0.2 (whole-run averages; race-only wall
is 68.31). End snapshots: S1 GameThread 73.0% / GsWorker 19.2%; S2
69.2% / 19.2%; S3 3× GsWorker 100% + GameThread 84.6%. S1 race gtcpu:
6/7 (5 polls; prime cores).

GPU busy % (per-sample kgsl ratio means) and thermal (status range,
cpu7 MHz, raw temp):

| Phase | S1 GPU% | S2 GPU% | S3 GPU% | S1 therm |
| --- | ---: | ---: | ---: | --- |
| Title (0→636) | 26.8 (n=1) | 26.4 (n=1) | 31.9 (n=2) | status 0, cpu7 4320 |
| Menus (636→1099) | 41.6 (n=1) | 43.2 (n=1) | — (in profile gap) | — (no poll hit) |
| Mode/Event (1099→1440) | 43.3 (n=1) | 43.9 (n=1) | — | status 1, cpu7 4090 |
| Loading (1440→1714) | 17.8 (n=2) | 19.4 (n=2) | — | status 3, cpu7 4090 |
| **Race (1714+)** | **37.1 (n=33)** | **34.5 (n=11, pre-profile)** | — | **status 3, cpu7 2246–4320, temp 66700–104300 (n=17)** |

S2 race polls are pre-profile only; **S3 has no in-window GPU/thermal
samples** (the driver blocks inside `simpleperf record` for the 30 s
window — same limitation as N11). Small-n menu rows indicative only.
Race GPU ~35–37% (F5 A legs: 31.8/37.2%); menus/mode ~42–44% per
single samples.

## Screencap readings (3 viewed)

| Capture | Tick~ | Reading |
| --- | --- | --- |
| S1 sc04-final | 4582 | Race 2ND/2 00:00:48 5%, 42 MPH, rider descending with carve trail; full brightness, no corruption |
| S2 sc01-tick2100 | 2100 | Race 2ND/2 00:00:06 1%, EA Radio "Glass Danse - Oakenfold Remix / The Faint", rider mid-trick; profile starts at 2468 shortly after |
| S3 sc02-postprofile | ~1800 | Race 2ND/2 00:00:01 0%, EA Radio "Emerge - Junkie XL Remix / Fischerspooner", rider at race start in snow spray — confirms the S3 window ran into early race |

## Symbolization

Bytesize NDK simpleperf
(`/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf/…`;
bytesize idle, `ps aux` first) + symdir (F5 unstripped `.so` + device
`libc.so` `dd242326…`, pulled from `/system/lib64/libc.so`). N5
`report.sh` recipe: self/comm-sym, self/sym-dso, threads, dso,
children(≥1%), each at limit 0.05, plus self/comm-sym at 0.01 and 0
(`--print-event-count` for exact weights).

- S2: 130,822 samples, 98.38 G cycles, **0 unresolved rows**. S3:
  600,515 samples, 451.01 G cycles, **0 unresolved rows** (our `.so`;
  Turnip offsets + kernel rows as N11).
- Basis note: raw sample counts (`-n`) do NOT match Overhead
  (GameThread 63.37% of samples vs 87.04% of cycles; GsWorker 30.05%
  vs 9.20%) — per-sample cycle weights vary ~4.5× between threads
  (prime-core vs roaming/low-clock sampling). All shares here are
  **event-count (cycle) weights**, consistent with N11's Overhead
  basis. `buckets.py --counts` sums the exact count column (100%).
- Turnip `libvulkan_freedreno.so` still stripped (offsets only —
  23,266 sub-0.01% rows in S3); kernel rows still `[kernel.kallsyms]`.
- Reports committed: `reports/s2|s3-{self-comm-sym,threads,dso,
  children}.txt` (0.05) + `s2-self-sym-dso.txt` (0.32 MB) +
  `s3-self-sym-dso.txt` (0.33 MB) + `-001` self-comm-sym files +
  `s2|s3-stage-appendix.md` (all rows ≥0.01%: 1,514 / 1,569 rows with
  every symbol→stage mapping). Full event-count reports (0.96 / 2.95
  MB) stay in scratch (`~/dev/ssx3-work/N12/`); the exact tables
  reproduce with `buckets.py --counts`. Bytesize: `/home/brad/n12`
  (prof/, symdir/).

## Exact commands

```sh
mkdir -p local/research/N12/logs local/research/N12/reports ~/dev/ssx3-work/N12
cp local/research/F5/launch.py local/research/F5/cooldown.py local/research/N11/buckets.py local/research/N12/
cp local/research/F4/phases.py local/research/N11/build.sh local/research/N12/  # phases used; build.sh unused (no builds)
# (+ N12 edits: pin a8d651a7, N12 paths/lease, variant default A, -g profiler, cooldown <=1+180s fixed, new bucket shapes, --counts)
sha256sum ~/dev/ssx3-work/F5/odin/app-release.apk  # x2: 4ff81032...09753
adb -s $S install -r ~/dev/ssx3-work/F5/odin/app-release.apk  # before S1, S2, S3 (base.apk SHAs match)
python3 local/research/N12/cooldown.py --label S1  # + S2, S3 (status<=1, fixed 180 s)
python3 local/research/N12/launch.py --label S1 --wall 600 --stop-tick 4500
python3 local/research/N12/launch.py --label S2 --wall 600 --stop-tick 4500 --profile-after-tick 2400 --profile-secs 30
python3 local/research/N12/launch.py --label S3 --wall 600 --stop-tick 4500 --profile-after-tick 636 --profile-secs 30 --scap-ticks 700,1000,1400
python3 local/research/N12/phases.py local/research/N12/logs/S1  # + S2, S3
adb -s $S pull /system/lib64/libc.so ~/dev/ssx3-work/N12/libc-device.so
ssh bytesize 'wsl -d Ubuntu -- bash -lc "… cat > /home/brad/n12/prof/<file> …"' < <perf-S2.data, perf-S3.data, libc>  # SHAs match both ends
# bytesize (one held ssh): symdir stage + simpleperf report x(5x2 + 2x0.01 + 2xcount + 2x-n) ; tar back
python3 local/research/N12/buckets.py /tmp/S2e.txt --counts  # + S3e, --comm GameThread, --appendix for tables
adb -s $S shell 'rm -rf /data/local/tmp/n12 …/files/mc0-test'  # device left clean
```

## Gaps

| Gap | Reason |
| --- | --- |
| S3 is menus+loading+early race (867→1802), not 636–1099 | menus ~2× faster than N11; trigger granularity (2 s polls) + 30 s window; ≤3 launches used, no relaunch per brief |
| S3 has no in-window GPU/thermal samples | driver blocks inside `simpleperf record` (same as N11) |
| execUpper/execLower not separable between VU0 and VU1 callers | shared `VU1Interpreter::` symbols; VU0 subtree = 7.02% children (overlaps `VU1 interpreter/other`) |
| Turnip/kernel symbol names | stripped adrenotools build; no kallsyms (as N11) |
| S3 ms scale ±15% | GsWorker-pool anchor from end snapshot, unscaled perturbation (N11's model) |
| N11 columns are cutoff tables (92.11%/71.62%), N12 exact (100%) | N11 perf re-analysis out of scope; like-for-like N12@0.05 columns provided |

Budgets: 0 fork edits, 0 builds, 3/3 launches (S1 ~241 s, S2 ~138 s,
S3 ~58 s wall), ~1.6 h of 1.5 h, N12 git dir 1.9 MB text-only, scratch
`~/dev/ssx3-work/N12/` 121 MB (≤5 GB). Bytesize: `/home/brad/n12`
(prof + symdir; idle before/after).

## Orchestrator gate (2026-09-25)

**Pass.** Tables complete; exact event-count basis (better than N11's cutoff tables); Brad's env and
save verified restored; 0 Wi-Fi drops. Readings (mine):
- Race frame 68.3 ms: **VU1 46.7 ms (68 %)** — generated pairs 38.0, interpreter/other 6.2, issue/hazard
  2.5 (was 70.1: VB1 worked). GameThread-minus-VU1 21.6 ms, of which guest code 8.7 (N11's 0.7 was a
  cutoff artifact), libc/kernel 10.8.
- **VU1 thread sizing:** moving VU1 off GameThread would leave VU1 (46.7 ms + handoff) as the long pole:
  frame ≈ 47–50 ms, ~1.4× (0.244× → ~0.34×). Making VU1 cheaper (VR2) comes first; the thread pays
  more once VU1 ≈ the rest. It stays parked.
- **VU0 is still interpreted:** `executeVU0Microprogram` subtree 7.0 % ≈ 5.5 ms/frame (called from guest
  `sub_0022ADD8`). A VU0 static recompile on VR1's machinery is a clear next lever (queued as VR3).
- Hot-path hygiene: `snprintf` subtree 1.06 % (~0.8 ms) on GameThread in a release build, and
  `__emutls_get_address` 0.68 % (GameThread + GsWorker; emulated TLS on Android). Cheap to find and fix.
- Menus are now 0.85–1.12× (NP1's GS handoff), so MD1 retargets to **loading (0.32×)**: S3's window
  (mostly loading) is GsWorker-pool-bound in Turnip driver CPU (90 ms/frame across ~3 workers) plus
  HybridMutex and allocator churn.
