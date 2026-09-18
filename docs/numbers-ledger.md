# Current numbers ledger

One table for every quoted metric. Documents cite rows here instead of
restating values. Status: **live** (trust it) | **contested**
(conflicting evidence, do not quote) | **stale** (superseded config,
re-run before quoting) | **void** (measured broken, never quote).

Rules that keep this table honest (perf-review §1+§7):

- Verdict-grade runs get an exclusive host AND device: no sibling
  builds, runs, or device shells during the window.
- Under any cap, report host CPU-ms per guest frame (or busy fraction)
  as the primary number; speed is pass/fail only (it saturates at 1.00
  and hides wins as idle).
- Uncapped means `EmulationSpeed = 0` (true unlimited), never 10.
- Every race number is screenshot-verified as racing (timer/HUD/slope);
  menu pace is never reported as race pace.
- Every receipt records module sha, backend (true, post-movie-override),
  cap, determinism mode, vertex loader, and validation-layer state.

## Live

| Metric | Value | Date | Device / config | How measured |
| --- | --- | --- | --- | --- |
| Odin race pace, OGL | 0.83× mean / 0.63× low (~50/~38 fps) | 09-17 | Odin 3, m3-menu verified racing (gate→0:07/49 MPH), dual-core detGPU, idle ON, null audio, speed 10 fixed | 4–5 sample window, `pace-hunt/pace-menu-egl-receipts/` |
| Odin race pace, Vulkan (true) | 0.73× mean / 0.64× low (~44/~38 fps) | 09-17 | Same, backend-patched DTM | Same, `pace-menu-vk-receipts/` |
| Odin menu pace | ~1.3–1.4× OGL, ~1.5× VK | 09-17 | Same runs, menu windows | Same receipts |
| Desktop menu ceiling | 3.89× OGL / 4.0× Metal / 6.6× idle-skip | 09-17 | Mac, m3-menu, post-throttle-fix | pace-hunt Phase 1 |
| Throttle proof | speed9: 0.15× pre (= predicted 0.1626×) → 3.66× post; speed10 menus 3.89×; speed1/2 intact; throttle sleep 56% → 0% | 09-17 | Desktop + Odin | `1f1bc2d` |
| FIFO fix | Control panics sample 140 (tombstoned GatherPipe stack); fix runs clean to completion, zero tombstones; desktop baseline panics ~129 s, fix exits 0 at 200 s; movie A/B 2234-prefix identical | 09-17 | Odin + desktop | `309f639`, `panic-fix/` |
| Pinned PAUSE tail, NOT race (emu→7, vid→6) | 1.974× (+25%) / 14.93 ms/frame (−19.5%) vs 1.578×/18.52 unpinned; samples 120–270 are the scripted post-race pause menu | 09-17 | Odin 3 (2+6, prime cpu6–7 @4.32GHz), m3-menu EGL, speed 0 | `23c5b86`, `affinity/` (pin2/both agree; flag replicates manual within 0.6%) |
| Pinned RACE window (gate→last racing shot) | HUD pace base 0.938 → pin2 1.000 / both 1.071 / fd-pin 1.00 (±20%: 5 s CPU ticks over 14–16 s windows); lows 0.63–0.70 → 0.94+ are the LOAD phase, not racing | 09-17 | Same runs | `affinity-summary.json` results.race_hud_pace; "remainder is GPU-driver-bound" there is an inference from the desktop OGL det-GPU profile, contradicted by M7 on the Odin (emu thread ~98% busy, video 15% of samples) — treat as unproven |
| Pinned load dip | 0.70 → 1.15 (+64%); lows 0.63–0.70 → 0.94+ | 09-17 | Same | Same; FD alone +37%, FD+pin stacks ≈1.41× |
| Priority / quarantine | renice −10: nil; emu→cpu0 control: −41% tail | 09-17 | Same | Same (contaminated pin1 kept as negative control) |
| Capped/uncapped reconciliation | RESOLVED: capped saturates 1.0 while sub-capability dips run identically in both regimes — content + cap saturation, no DVFS paradox | 09-17 | Odin, m3-menu capped arm + busy fraction | Affinity hunt |
| Snow scorer calibration | clean ≤0.05 (iPad) / ≤0.08 (Odin menu); corrupt ≥0.17 transition / ≥0.38 full; threshold 0.12 | 09-17 | Archived shots | `tools/gamecube_snow_check.py` |
| Onscreen trial | 25/25 presented + correlated | 09-17 | Odin onscreen | `8df3c42` |
| FP-unavailable fault rate, desktop | ~1,640/s in-race (41,022 in a 25 s race window); ~610–690/s whole-run average (menus dilute) | 09-17 | Mac, C backend module, `hle_vectors=1` (syscall vector already HLE'd) | `native_exc` counters in `android-spike/codegen/` ab2 receipts and RESULTS.md, read by M2; per-fault host cost NOT yet measured (M2b); Odin rate NOT yet measured (D1b dispatch-samples arm) |
| Upstream native-ABI module has no runtime (M1c) | Native-ABI flavor LINKED (961 MB dylib, 0 undefined) but the upstream runner rejects it: it only accepts `ModernGekkoModuleDesc` via `staticrecomp_get_module`; no consumer of the native module ABI exists anywhere in the upstream checkout | 09-18 | Mac, upstream trees on the SSD | `local/research/M1/REPORT.md` Part 3; using that ABI means writing the runtime side (S1-class), not a link fix |
| Upstream runner limits (M1c) | No movie playback, no working frame dump on Metal (`DumpFramesAsImages` honoured but inert), no `--config`; boot-only evidence is counters | 09-18 | Same | Same; M1d rebuilds this repo's patched runner on upstream to get movies + screenshots |
| Upstream LLVM module boots (M1b) | recompcore-flavor LLVM module (14,419 objects, 270 MB dylib, 54 min generation at -j8) linked via the module template plus a one-function shim and ran 155 s on Metal under the upstream runner: native cycles 4.72 G, fallback 0, native_exc 0, exit 0 | 09-18 | Mac, `/Volumes/Extreme SSD/upstream-review/build-m1` (Release -O3), LLVM 23 + compat patch | `local/research/M1/REPORT.md` Part 2; NOT visually verified (no screen capture from any agent context), no fps number, host under load ~40 during the run; ABI stats: this flavor is 1,616 native / 12,803 compat functions, so it carries little of the native-ABI benefit |
| Upstream LLVM module, native-ABI flavor | `--runtime moderngekko` flavor: 14,367 native / 52 compat functions, 63,583 direct call edges; generated (66 min) but NO in-tree link path (template parses recompcore headers only) | 09-18 | Same | Same; linking it is S1/M1c work |
| LSE / no-outline-atomics runtime (M4) | INCONCLUSIVE: emu ms/frame base 11.76–12.30 (×3) vs LSE 10.97–12.77 (×2), direction flips between repeats; video 3.62–3.75 vs 3.46–3.77; nm shows 0 `__aarch64_*` outline atomics. Window caveat: M4's analysis window (samples 43–55) is the scripted PAUSE MENU (anchored shots), the race is ~15 HUD s earlier; flags landed for hygiene (5cc328b), not as a measured win | 09-18 | Odin 3 stock, pinned, uncapped, m3-menu, `aff-tpl` | `android-spike/M4/REPORT.md` §3; LSE arms have zero emulator screenshots (dead shot path in binaries built from the pristine `m4-src` tree) |
| Shader cache persistence (M4) | Nothing is ever written: no `Cache/` in any user dir; the only "cache" log lines are the asset-list metadata cache. No warm/cold A/B possible; race-start dip is content load | 09-18 | Same | Same §2 |
| Per-callback update/render split on Odin | STILL OPEN: FIFO-fixed trial relink (220488ca) survives the race but the trial skips at engage (`invalid_immediate_copy_setup`, status 1→4 at wall 45.01) under the pace template; needs the trial's own template (immediate XFB) or a simpleperf race profile (D6) | 09-18 | Same | Same §4 |
| Odin in-race exception attribution (D5) | 100% vector 0x800 (FP-unavailable): 36,121/s over the HUD-timed race window uncapped, mean 1,408 ns raise→rfi-return = **5.68% of race emu-thread CPU**; capped 1.0: 8,693/s, 2,140 ns, 3.78%; menus 1,385/s. Two faulting PCs (0x8026e1a0 `lfd`, 0x80264b48 `stfd f31` prologue) carry 59% with identical counts (a thread-pair ping-pong); nearly all faulting words are FP loads/stores | 09-18 | Odin 3 stock, pinned, D1 launch shape, instrumented m4-src build (temporary, `D5/instrument.patch`) | `android-spike/D5/REPORT.md`; fault count per guest second is host-timing dependent (capped full run 185k vs uncapped race alone ~397k); race verified by metric pattern vs D1b (m4-src builds record no screenshots: `!headless` gate at `dolphin_runtime.cpp:488`) |
| Stock-track corpus census (M3), desktop | 13 of 17 courses ride; render CPU median (ms) / update (ms): Crow's Nest 23.26/8.07, Launch Time 23.23/7.96, R&B 22.76/8.46, Gravitude 21.54/8.38, Kick Doubt 21.33/8.02, Much-2-Much 20.97/8.54, Style Mile 17.87/7.20, Ruthless Ridge 14.80/7.62, Schizophrenia 9.37/3.57, Metro-City 8.41/5.23, The Junction 7.12/3.25, Intimidator 6.69/3.14, **Snow Jam 6.30/3.08 (the lightest course in the corpus)**. Heaviest that rides: Crow's Nest, 3.7× Snow Jam's render and 2.6× its update. Unmeasured: Perpendiculous, Happiness, Ruthless, The Throne (legs died on the pin check while S3 edited the vendor tree) | 09-18 | Mac, census player (probe + per-present draw hook), 640x528 immediate XFB, single core, Metal validation OFF, 180 s legs, local stock game, load 2.8–8.0 at leg start (M1d build overlapped) | `local/research/M3/REPORT.md` step 2, `census-table.json`, per-leg `census.json`; **every Odin budget number so far is Snow Jam, the easiest case** |
| Corpus movies (M3) | `local/research/M3/movies/m3-snow-jam-3min.dtm` (sha 563b3b46…, 18,022 frames, strict compare 1325/1325 identical, gate passed); `m3-crows-nest-3min.dtm` (sha d80a1050…, 10,942 frames, results screen reached; strict dispatch compare diverges across plays with equal rider-state transitions — dual-core interleave, trajectory equal). Both bake dual-core, immediate XFB, FastDisc, backend Metal | 09-18 | Mac, production runner 24c2e26c, recorded with `--cpu-thread` | Same, step 4; Odin controls (step 5) not run yet (device busy, pace binary not on device) |
| Odin race-window emu-thread profile, stock (D6) | guest module 74.6/74.9%; dispatcher + core 13.2/13.0% (Run 3.6, HookExternalWrite 2.4, chassis_dispatch 1.7, CoreTiming::Advance ~3% of Run's children); FIFO/GatherPipe 4.5/4.4%; libc+kernel 2.4%; atomics 2.1% (`__aarch64_swp4_acq_rel` 1.17); JIT/Poison 0.3%; explicit exception frames 0.02% (the FP storm's cost sits inside guest handler chunks + Run). Top chunks: func_802197A0 8.1/8.4%, func_8022D7A0 6.3/6.4%, func_801097A0 3.1% — the first two are the codegen-spike chunks; func_802197A0's callees are the FP helper set (`ppc_fcmp` 4.9%, `dolrecomp_f32_from_bits_slow` 3.0% of its subtree; `f32_from_bits_slow` 1.28% flat) | 09-18 | Odin 3 stock, pace binary 84de2c22, simpleperf cpu-clock 4 kHz on the emu TID, gate→pause bracket (≤2–4 s pause sliver), two arms agree within 0.3 points | `android-spike/D6/REPORT.md` symbol/grouping tables and caller chains; kernel symbols unresolved (kptr_restrict) |
| Odin race pace, stock vs underclock (D1b) | HUD pace 1.273×/1.273× stock (base-stock-a/b) vs 1.071×/1.071× underclock (base-a/b); emu busy 0.92–0.93 vs 0.88–0.89; video busy 0.39 vs 0.26. +41% clock bought +19% pace | 09-17 | Odin 3 stock (cpu7 4.32 GHz), m3-menu EGL dual-core det-GPU, pinned emu→7 video→6, uncapped, perf mode 1 | `android-spike/D1/REPORT.md` Part 2 table; pace is HUD-seconds/wall over 11–14 s windows (1 s quantization ≈ ±9%); the table's "emu ms/f" column is inflated by 5 s tick bracketing — quote busy fractions, not it |
| Odin determinism tax (race) | det-none 1.364×/1.364× vs det-GPU 1.273×/1.273× (+7%); boot→gate 19 s vs 35 s (menus much faster); trajectory identical | 09-17 | Same, `user-aff-detnone` template | Same; every movie-driven Odin race number carries this ~7% harness tax |
| Odin Null video backend | 1.25×/1.273× = base; video busy 0.39 = base; screenshots still render | 09-17 | Same, `--graphics Null` | Same; the video thread's cost is CPU-side FIFO decode, not the GPU driver — retires the "GPU-driver-bound" inference for good |
| Odin capped 1.0 budget, stock | emu busy 0.58, video 0.27 at 60 Hz → ≈9.7 ms / 4.5 ms CPU per guest frame (cpu7 mean 3.79 GHz: DVFS idles down under the cap; ≈8.6 ms emu at a held 4.3 GHz) | 09-17 | Same, `user-m6h` (EmulationSpeed 1.0) | Same; 120 Hz sim on the emu thread needs ≤8.33 ms at 100% busy — F route is ~1.05–1.2× short before codegen wins |
| Odin in-race native exception rate | native_exc 35,646/s in-race (base-stock-a − menu-pre over 11 s); menus/boot ≈1,550/s; hook_fb 38,861/s tracks it 1:1; dispatch samples 0.000% at 0x800/0x500/0x900 | 09-17 | Same | Same, "Derived numbers"; `m_native_exceptions` counts every dispatch where the module raised a guest exception — vector NOT attributed on the Odin (D5); 20× the desktop's 1,640/s |
| Odin shader cache | No `Cache/` dir after a 330 s graceful stop; zero shader/cache log lines | 09-17 | Same, `cache-late` | Same; race-start dip at stock is small (min 1.185–1.23× vs 1.273× steady) |
| Odin stock thermals | cpu-1-1-1 reads exactly 104.7 °C on 7 arms (reading clamp; 46.5 idle); cpu7 never below 3.28 GHz, zero throttle ticks; capped1x peaks 94.6 | 09-17 | Same | Same; Sport fan not needed for correctness of these numbers |
| Odin per-callback update/render split, stock (D6) | update CPU 3.19 ms med / 3.69 p95 (wall 3.20 / 3.73, n=707); render CPU 7.93 med / 11.00 p95 (wall 8.63 / 12.51, max 20.7, n=1010 incl. 303 blended extras) — 11.1 ms CPU per 60 Hz frame; render alone is 95% of a 120 Hz budget | 09-18 | Odin 3 stock, FIFO-fixed trial binary 220488ca, `m6h` + `m3-menu-imm.dtm`, trial at=112 s for 12 s, capped 1.0, guest-clean (all updates position_changed) | `android-spike/D6/REPORT.md` probe table; trial engages only with the imm movie + m6h template (the `aff-tpl`/m3-menu shape skips with `invalid_immediate_copy_setup`); no screenshots from that binary (dead shot path), race anchored by the D1 capped1x mapping + engagement rows |
| Odin clock caps | The 3.072 GHz prime / 2.75 GHz mid `scaling_max_freq` caps seen in D1 part 1 were a user-installed underclock tool running by default; removed 09-17 ~21:35, stock caps now read cpu6–7 4.32 GHz, cpu0–5 3.53 GHz, GPU max 1.1 GHz. `performance_mode` 0/1 never changed the caps. **Every Odin number dated 09-17 before ~21:35 (pace hunt, affinity, D1 base-a/base-b) was measured underclocked at ≤3.07 GHz on the emulation core.** D1b re-ran base at stock: see "Odin race pace, stock vs underclock" | 09-17 | Odin 3 | adb sysfs read-back; `android-spike/D1/REPORT.md` Part 1 for the underclocked arm (emu core 3.072 GHz every race sample, cpu zones 74–92 °C) |

## Contested

None currently. (Resolved 09-17: M5-vs-0.83× — see Live "Capped/uncapped
reconciliation".)

## Stale (re-run before quoting)

| Metric | Why stale |
| --- | --- |
| Desktop cost table ("needs 1.3–1.9×") | Predates the FP wave by a day; taken with Metal validation on |
| M5 profile ("CPU core now the frontier") | Module predates Wave B (no fast-FP, no conversion split) |
| "Endian helpers 12.1 → 0.00" | Reads "inlined, now unattributable" — cost moved into `func_*` bodies |

## Void (measured at the phantom 1.16 wall — never quote)

fast-FP "0.00 prize" + STOP decision · "every CPU opt ~0%" ·
determinism-off 0.0% · pinning 0.0% · EGL==Vulkan to 4 decimals ·
EFB-2× "full speed" · desktop 1.17 bind + validation-on/off-identical ·
psq wall-clock null · "1.16 is STRUCTURAL". All re-measured or queued
for re-measurement off the wall (perf-review §1, `todo.md` Now).
