# I33 Part 1 — paraLLEl-GS (GPU) on iOS: feasibility, Simulator + iPad

Worker: Muse Code, brief `local/muse/prompts/I33.md` Part 1 only. No iPhone
in Part 1 (no install); the bundled env stays CPU until the orchestrator gates.

## Result

paraLLEl-GS runs on the iPad Air 11" M2 and reaches the race: `[gs:parallel]
init ok`, `[gs-path] … gpu=Apple M2 GPU`, race HUD at tick ~1714, frames
viewed at Select Event + race on both backends. No fork or parallel-gs source
changes were needed (`i33-pgs-ios` == `0ed07c4`, clean). The Simulator cannot
run the Vulkan path (emulated GPU lacks descriptor indexing) — device-only
validation. Diagnostic pace (one launch per backend, console-pty + vsync-rate
overhead, NOT speed numbers): launch→t2100 97 s (parallel) vs 209 s (CPU);
race window 6.81 vs 3.84 vs/s (1.77×); menus run full-speed on parallel
(~60 vs/s vs ~19).

## Plan (written before the build)

**MoltenVK artifact:** upstream `MoltenVK-all.tar` v1.4.2 (KhronosGroup/MoltenVK
release, Apache-2.0, same version as Homebrew's macOS molten-vk 1.4.2),
SHA-256 `562a15a2…ef17276` (×2). It ships `MoltenVK/MoltenVK/dynamic/
MoltenVK.xcframework` with `ios-arm64` and `ios-arm64_x86_64-simulator`
slices (plus macos/tvos/xros). Homebrew's `MoltenVK.xcframework` is
macOS-only (`macos-arm64`), so it cannot serve iOS; no Vulkan SDK is
installed locally (`/usr/local/share/vulkan`, `~/VulkanSDK` absent).
The dynamic `MoltenVK.framework` slice is embedded per target at
`ps2EntryRunner.app/Frameworks/MoltenVK.framework` (stage step, then signed).

**How Granite gets the entry point:** non-Android boots call
`Vulkan::Context::init_loader(nullptr)` (fork
`ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:414`), which
`dlopen`s `$GRANITE_VULKAN_LIBRARY` and `dlsym`s `vkGetInstanceProcAddr`
into volk (`Granite/vulkan/context.cpp:219-246`; Apple fallbacks
`libvulkan.1.dylib` / `libMoltenVK.dylib` don't exist on iOS, so the env var
is required). Init is headless — `init_instance_and_device(nullptr, 0,
nullptr, 0, flags)` (no surface/WSI) — so no iOS WSI work is needed.
`GRANITE_VULKAN_LIBRARY` is passed per launch with the absolute container
path (sim: `SIMCTL_CHILD_GRANITE_VULKAN_LIBRARY=<bundle>/Frameworks/
MoltenVK.framework/MoltenVK`; iPad: `devicectl launch -e`, live container
path first). The iOS env layer would also substitute `${BUNDLE}` for file
keys (`ps2_ios_runtime.mm:80-88`), but the bundled env stays CPU per brief.

**CMake flags for the iOS target:** `-DPS2X_GS_SHADOW_PARALLEL=ON`
`-DPS2X_PARALLEL_GS_SOURCE_DIR=<parallel-gs @ 19d93b2>` on top of the F2/I32
recipe (Xcode generator, I26 toolchains, same deps). Fork `0ed07c4` needs
parallel-gs `19d93b2` (GB9 `pgs_env_knobs.hpp` include; `963cb575` lacks the
header and fails the build). Standalone headless config
(`PARALLEL_GS_STANDALONE`, `GRANITE_PLATFORM=null`, no runtime shader
compiler) is the same shape as the working Odin/Android build. Defaults kept:
`PGS_HIER_BINNING` unset (Mac GB8 runs flat-always; hier-force on Apple GPUs
is GB9 follow-up, not Part 1).

## Pins and inputs

| Item | Pin | Receipt |
| --- | --- | --- |
| Fork worktree `~/dev/ssx3-work/I33/PS2Recomp`, branch `i33-pgs-ios` | `0ed07c4` (== `fork/ssx3`, clean, no source changes) | `logs/fork-head.txt`, `status --porcelain` empty |
| parallel-gs worktree `~/dev/ssx3-work/I33/parallel-gs` | `19d93b2` (detached, clean) | `git rev-parse`, preflight |
| Granite submodule of the above | `166ba21a` + nested subs (vulkan-headers v1.4.358, volk, …) | `logs/granite-head.txt`, `submodule status` |
| MoltenVK-all.tar v1.4.2 | SHA `562a15a2…ef17276` (×2) | `moltenvk-sha.txt` |
| MoltenVK device slice (`ios-arm64`) | SHA `6cd58884…96aff` (source == staged) | `logs/moltenvk-device-sha.txt`, `logs/device-mvk-stage-sha.txt` |
| MoltenVK sim slice (`ios-arm64_x86_64-simulator`) | SHA `c6027cfb…2e1d` (source == staged) | `logs/moltenvk-sim-sha.txt`, `logs/sim-mvk-stage-sha.txt` |
| Canonical codegen | `register_functions.cpp` SHA `8ea8ed43…e662d688a3` (matches E54F2/GB8) | `logs/codegen-sha.txt` |
| Stock ELF / ISO, raylib `c1ab645`, SDL2/FFmpeg ios-deps, toolchains, I32 env | F2/I32 pins, all re-hashed | `logs/*-sha.txt`, `*-cache.txt` |
| Route | I26-FAST re-armed per launch via `-e` (484 chars, from I32 env) | `env-parallel.json`, `env-cpu.json` |
| Sim binary | SHA `1ce60ef4…060085` (×2) | `logs/sim-source-binary-sha.txt` |
| Device binary (pre-sign) | SHA `48c81315…63abb3` (×2) | `logs/device-source-binary-sha.txt` |
| Device binary (signed) | SHA `bbdc5685…9198e` (×2) | `logs/signed-binary-sha.txt` |

Runner-dir check: `git diff --exit-code 14b1e5cb HEAD --
ps2xRuntime/src/runner` empty (no fork changes at all). `~/dev/parallel-gs`
canonical clone untouched (read-only source for the worktree).

## Simulator: builds, loader works, emulated GPU is a hard blocker

Sim configure + build succeed with `PS2X_GS_SHADOW_PARALLEL=ON`
(`BUILD SUCCEEDED`, `logs/sim-build.log`). Two staging lessons, both fixed
in `build-install.sh`:
1. First run: `Context::init_loader failed` — the top-level ad-hoc
   `codesign --sign -` does not sign the nested `MoltenVK.framework`
   (`code object is not signed at all`), and the loader refuses it. Fix:
   sign the framework explicitly before the bundle (sim and device `sign`).
2. Rerun: MoltenVK 1.4.2 loads (`Found layer: MoltenVK`, Vulkan 1.4.357,
   `VkInstance` + `VkDevice` created on `Apple iOS simulator GPU`), then
   Granite aborts device init: `[ERROR]: Sufficient features for descriptor
   indexing is not supported on this device` / `Cannot support descriptor
   indexing on this device`. The sim's emulated GPU reports **GPU Family
   Apple 2** with no descriptor indexing — a sim-emulation capability gap,
   not a code bug. No `[gs-path]` line on the sim; no sim frames (brief step
   2 unmet as predicted-impossible on this GPU — the iPad is the real test).

No `PGS_HIER_BINNING` / flag workaround exists: descriptor indexing is core
to Granite's descriptor-heap path. The Simulator cannot validate the iOS
Vulkan path; device runs are required.

## iPad: parallel reaches the race; CPU A/B

Device configure + build succeed (`BUILD SUCCEEDED`, 126 MB binary);
`deploy-ios.sh ipad` verified (save + 496-byte manual-play env, all OK);
probe launch read the live paths (Data `…/02D4A244-…/Documents`,
Bundle `…/B126086B-…/ps2EntryRunner.app`, matches the install URL). One
launch per backend, fresh cards (`mc-i33-par`, `mc-i33-cpu`), route re-armed,
`PS2X_VSYNC_RATE_LOG=1`, terminated after each (0 `ps2EntryRunner` procs left).

Parallel launch (`run-ipad-parallel`, `PS2X_GS_BACKEND=parallel`):
- `[gs:parallel] live backend selected`, `init: GRANITE_VULKAN_LIBRARY=
  …/ps2EntryRunner.app/Frameworks/MoltenVK.framework/MoltenVK`,
  `Created VkDevice … on GPU Apple M2 GPU`, `[gs:parallel] init ok`.
- `[gs-path] hier_rule=flat-always hier_t2=1 hier_t4=1
  subgroup_flat=free-4..128 subgroup_hier=free-4..128 vk11_subgroup=32
  max_wg_inv=1024 desc=plain desc_req=push+heap+buffer sampler_feedback=on
  feedback_rt=off gpu=Apple M2 GPU` (same rule/shape as Mac GB8).
- Benign: `[ERROR]: Could not find a suitable time domain for calibrated
  timestamps` (also on Mac), two `[mvk-warn] … Metal does not support
  disabling primitive restart` (one per pipeline setup, no frame impact).
- Periodic tail: `presents=1500 present_ms_avg=11.5 readback_ms_avg=8.27
  unsupported_clears=0 unsupported_vram_io=0`.

Pace (DIAGNOSTIC — console-pty capture + vsync-rate logging overhead, one run
per backend, not speed numbers). Guest vsyncs/s ÷ 59.94 from `[vsync-rate]`:

| Phase (ticks) | CPU vs/s (×) | Parallel vs/s (×) | Parallel ÷ CPU |
| --- | --- | --- | --- |
| Title [0,636) | 25.37 (0.423×) | 59.93 (1.000×) | 2.36× |
| Menus [636,1440) | 18.87 (0.315×) | 59.97 (1.001×) | 3.18× |
| Loading [1440,1714) | 9.15 (0.153×) | 31.18 (0.520×) | 3.41× |
| Race (1800,2100] | 3.84 (0.064×) | 6.81 (0.114×) | 1.77× |
| Wall launch → t2100 | 209 s | 97 s | 2.15× |

Frames viewed (all 6; iPad screenshots with virtual pad + letterbox):
- Parallel t1090 (tick 1201): Select Event — Snow Jam / Metro-City /
  Happiness + Rival mountain-map card, all legible. Correct.
- Parallel t1810 (tick 1849): race HUD — 2ND/2, timer 00:00:02, snowy
  track, EA Radio overlay. Correct.
- Parallel t2100 (tick 2103): race, HUD advanced. Correct.
- CPU t1810 (tick 1825): same race scene as parallel (2ND/2, 00:00:02,
  same track frame modulo animation tick). Same-scene A/B holds.
- CPU t1090/t2100: menu + race, correct phase.

Frame paths (scratch): `~/dev/ssx3-work/I33/ios/run-ipad-{parallel,cpu}/
shot-t{1090,1810,2100}.png` (+ `console.log`, `run.txt` each).

## Exact commands

```sh
# Worktrees (from ~/dev/PS2Recomp, ~/dev/parallel-gs)
git worktree add ~/dev/ssx3-work/I33/PS2Recomp -b i33-pgs-ios fork/ssx3  # 0ed07c4
git worktree add ~/dev/ssx3-work/I33/parallel-gs 19d93b2
git -C ~/dev/ssx3-work/I33/parallel-gs/Granite submodule update --init   # nested subs
# MoltenVK (scratch)
curl -sL https://github.com/KhronosGroup/MoltenVK/releases/download/v1.4.2/MoltenVK-all.tar -o MoltenVK-all.tar
tar -xf MoltenVK-all.tar   # MoltenVK/MoltenVK/dynamic/MoltenVK.xcframework
# Build (W=~/dev/ssx3-work/I33/ios; script mirrors F2's + PGS flags + MVK stage)
bash build-install.sh preflight configure_sim build_sim stage_sim sim_install
bash run-sim-parallel.sh                                   # sim: descriptor-indexing blocker
bash build-install.sh configure_device build_device stage_device sign install_ipad
bash ~/dev/ssx3/local/research/I31/deploy-ios.sh ipad
bash ipad-probe.sh                                         # live Data + Bundle paths
# env-parallel.json / env-cpu.json: route + fresh MC_ROOT + VSYNC_RATE_LOG (+ BACKEND)
bash ipad-run.sh run-ipad-parallel env-parallel.json '1090 1810 2100'
bash ipad-run.sh run-ipad-cpu env-cpu.json '1090 1810 2100'
```

Scripts in scratch (not committed): `ios/build-install.sh`,
`ios/run-sim-parallel.sh`, `ios/ipad-probe.sh`, `ios/ipad-run.sh`,
`ios/env-{parallel,cpu}.json`. Scratch `~/dev/ssx3-work/I33/` 7.6 GB (< 20).

## Budgets and gaps

~45 min of the 3 h box. Builds 2/2 (sim + device, +1 failed sim attempt on
the wrong parallel-gs pin and 1 restage on the signing fix — no extra device
builds). iPad launches: 1 probe (CPU, title hold) + 1 parallel + 1 CPU, each
< 420 s wall. Gaps stated plainly: one run per backend (no drift
cancellation, second decimal is noise); pace is diagnostic (console capture
overhead), not a speed number; no sim frames; no det-hash determinism check
on iOS (guest-state parity iOS CPU-vs-parallel unproven — Mac GB8 proved it
for the Mac); `PGS_HIER_BINNING=force` untested on the M2; iPhone untouched.

## Recommended next action (orchestrator decides)

Gate the bundled-env flip (`PS2X_GS_BACKEND=parallel` + embedded
`GRANITE_VULKAN_LIBRARY=${BUNDLE}/…` — substitution already handles all file
keys) for iPhone/iPad behind one iPad det-hash A/B (CPU vs parallel guest
identity on iOS) plus a `PGS_HIER_BINNING=force` iPad boot (GB9 says it works
on Apple GPUs; measures whether hier beats flat on the M2). The MoltenVK
v1.4.2 tarball + SHAs above are the pinned artifact; a `ios-deps`-style
persistent home for the xcframework (outside the 20 GB I33 scratch) is needed
before any iPhone recipe references it.

## Orchestrator gate, Part 1 (2026-09-25)

**Pass.** paraLLEl-GS runs on the iPad (M2) from fork `0ed07c4` + paraLLEl `19d93b2` with no source
changes: MoltenVK 1.4.2 (Apache-2.0) embedded as `Frameworks/MoltenVK.framework`, Granite loads it via
`GRANITE_VULKAN_LIBRARY`, headless init (no WSI work). Diagnostic pace: menus ~60 vs/s vs ~19 on the
CPU backend, race 1.77×, launch → t2100 97 s vs 209 s. The Simulator can't run the Vulkan path
(no descriptor indexing), so iOS paraLLEl is device-validated only. Part 2 released: paraLLEl as the
iOS default (bundled env), iPad test, iPhone install when reachable.
