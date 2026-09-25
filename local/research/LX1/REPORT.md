# LX1 — bradflix as a Linux correctness/build host: setup + det-hash parity

Worker: Muse Code, brief `local/muse/prompts/LX1.md`. No push (orchestrator gates).

**Result: host works, parity FAILS early and deterministically — first
differing tick 39 (eeCycle +8, rdram, combined), ticks 1–38 byte-identical
all fields.** Per the brief, Part 2 chases the host-arch difference; this
report stops at the first differing tick. The bradflix Linux build runs the
full I26-FAST route to the race (tick 2401, HUD, race frames viewed).

Parity commit: fork `ssx3` **`0ed07c4`** both sides (not `96e9f45`: that
commit cannot compile on Linux — the HF1 LP64 lambda bug that blocked F2
Part 2; so a fresh Mac det boot at the tip was needed instead of reusing
F2's B2). Same codegen, same inputs, same route, CPU GS both sides, sound
off both sides.

## 1. bradflix host + deps (no sudo → docker route)

bradflix: Ubuntu 24.04, x86_64, 20 cores, 62 GB, Intel Arrow Lake iGPU,
994 GB free, idle (load ~0.3). `sudo -n` fails (password required), and
the host lacks ninja, xvfb, vulkaninfo and all X11/GL dev headers — so no
system install was possible. The build/boot run inside a docker container
(user is in the `docker` group), image `ssx3-lx1` (this dir's
`Dockerfile`, Ubuntu 24.04 + clang 18 + cmake + ninja + X11/GL/ALSA/Wayland
dev + FFmpeg dev + xvfb + vulkan-tools + Mesa ANV). Image ID
`c5810babb595`. Bind-mount `~/dev/ssx3-work/LX1` at `/work`, `--user
1000:1000`, nothing under host `/tmp`, all work under
`~/dev/ssx3-work/LX1/`.

| Dep | Host | Container | Receipt |
| --- | --- | --- | --- |
| clang | 18.1.3 present | 18.1.3 (Mac: Homebrew 23.1.1) | `clang --version` both |
| cmake/ninja/make | cmake 3.28 + make (no ninja) | cmake + ninja | configure rc=0 |
| X11/GL/ALSA dev | absent | installed | raylib X11 configure `Found X11`, link rc=0 |
| FFmpeg dev | absent | `libav*-dev` (2nd Dockerfile rev) | 1st configure failed on `libavcodec` etc., 2nd rc=0 |
| xvfb/Xvfb | absent | xvfb (Xvfb used directly, see §5) | socket + GL probe |
| Vulkan/ANV | libvulkan1 + mesa-vulkan-drivers 25.2.8, `/dev/dri` present | `vulkaninfo --summary` | GPU0 Intel(R) Graphics (ARL), apiVersion 1.4.318, driver 25.2.8 |

## 2. Inputs (verified SHAs both sides)

| Input | Mini | bradflix `~/dev/ssx3-work/LX1/` | SHA |
| --- | --- | --- | --- |
| Codegen 9,457 files, 623 `PS2X_SBR_LT`, 0 `._*` | canonical `codegen-ssx3` | `codegen/` via `tar \| ssh` | `register_functions.cpp` `8ea8ed43…688a3` both sides |
| ISO 3,005,415,424 B | `E32-inputs/SSX 3 (USA).iso` | `inputs/` (local `cp` from Brad's `~/dev/ssx3/` copy) | `3c2f8eb1…ebf5` both sides |
| ELF 3,890,784 B | `E32-inputs/cd/SLUS_207.72` | `inputs/` via `scp` | `1b49d05c…af7bc` both sides |
| Fork | worktree `LX1/PS2Recomp` @ `0ed07c4` (detached) | clone `LX1/PS2Recomp` @ `0ed07c4`, clean | `rev-parse` both sides |

## 3. Builds (Release, logs/taps off, det-hash tap ON, tests ON, CPU GS)

Same flags both sides (Mac: Homebrew clang, `PS2X_GAME_CODEGEN_DIR` =
canonical; bradflix: container clang 18, codegen = `/work/codegen`).
No `PS2X_GS_SHADOW_PARALLEL` / no parallel-gs anywhere (CPU-only).

**Linux needed `-msse4.1`** (passed as `CMAKE_C/CXX_FLAGS`; E-lane
follow-up: the fork sets an arch flag only for ARM — `CMakeLists.txt:84`
`-march=armv8-a+fp+simd` — so x86 defaults to SSE2 and the build fails on
SSSE3/SSE4.1 intrinsics in `ps2_runtime_macros.h` + 430 codegen files;
AVX2 use is xxhash-internal only). First bradflix build died at
[216/569]; after the flag, [569/569] rc=0, 0 FAILED.

| Runner (det-hash tap ON, string present) | SHA-256 (two matching reads) | Size |
| --- | --- | --- |
| bradflix `build/ps2xRuntime/ps2EntryRunner` | `3c570c257a35c583463c0ba04fad2f00a4c80631ffc2402666f4bcd16c33d9ca` | 145,673,120 B |
| Mac `mac-build/ps2xRuntime/ps2EntryRunner` | `e63c318af0a46c4420eb9a3da78144a912289f000a5eeec2e6d70cf745fd539c` | 133,530,144 B |

Wall: bradflix build ~3.2 min (16 jobs, idle box), Mac build ~5 min
(8 jobs). Configures rc=0 both sides.

## 4. Suite (from the worktree root)

| Side | Result |
| --- | --- |
| Mac `0ed07c4` tap-on | **616/616, rc=0** (`mac-suite.log`) |
| bradflix `0ed07c4` tap-on | **615/616, rc=1** (`suite.log`): only `E53 FP mode` fails |

The E53 failure is x86-test-only, not guest math: `ScopedPs2Mode` sets
MXCSR (chop+FTZ+DAZ) but not the x87 control word, and glibc's
`fegetround()` reads the x87 word — so the two `fegetround() ==
FE_TOWARDZERO` asserts fail while the SSE-math checks (chop, denormal
flush, IEEE restore, control-word restore) all pass. Proven with a
10-line probe in the container: MXCSR=chop → `fegetround()=0`
(FE_TONEAREST) but `1+0.75ulp` CHOPS. E-lane follow-up: assert MXCSR RC
on x86 (or sync the x87 word in `ScopedControl`).

## 5. Boots (I26-FAST, empty mc0, `SKIP_MOVIE=1`, deterministic, sound off)

Drivers: `lx1_boot.py` (bradflix; F2 det-mode logic over docker) and
`lx1_boot_mac.py` (Mac; F2 driver at the LX1 root). Same caps (500 s
wall, 120 s progress, 16 MiB log, 1 GiB frames), same snapshotter.
M1 took one mini slot (waited ~90 s on VR1's exclusive hold); B4 ran
under the manually-held bradflix lease (released after; the wrap script
claims/releases per run).

**X lesson:** `xvfb-run` hangs in this container — its Xvfb-ready
handshake (SIGUSR1 + `wait`) never fires as PID 1 and proved flaky
under a wrapper too (2 orphaned containers, B1/B2 `progress_cap`, 0-byte
logs — a killed runner's fully-buffered output is lost). The driver
manages Xvfb directly (start, poll `/tmp/.X11-unix/X99`, `DISPLAY=:99`,
kill after) and wraps the runner in `stdbuf -o0 -e0`. X/GL itself is
fine (llvmpipe 4.5, Mesa 25.2.8). Dead runs: B1/B2 (xvfb-run hang), B3
(driver path bug `/workbuild/…`, rc=127, fixed).

| Boot | Bound | Wall | Last tick | HUD wall | det-hash lines | Ticks |
| --- | --- | --- | --- | --- | --- | --- |
| B4 bradflix | target | 329.4 s | 2401 | 129.25 s | 2,411 | 1..2411 |
| M1 Mac | target | 218.8 s | 2402 | 86.53 s | 2,421 | 1..2421 |

(Wall is diagnostic-build pace under different renderers — llvmpipe vs
Mac hardware GL — not a speed number.)

## 6. Parity: FAIL at tick 39 (glue-immune field extract, `/tmp/lx1_hashdiff.py`)

2,411 common ticks. **Ticks 1–38: byte-identical, all 7 fields**
(`eeCycle/rdram/scratch/vu1Data/vu1Code/combined/count`). First
difference at **tick 39**:

| Tick 39 field | M1 (Mac arm64) | B4 (bradflix x86_64) |
| --- | --- | --- |
| eeCycle | 191696672 | 191696680 (+8) |
| rdram | `bfbe04a58ccdac9a` | `57e3d45b79b85829` |
| combined | `563eb259435ab2d8` | `a008194a30902ff9` |
| scratch/vu1Data/vu1Code/count | `594edc66…` / `…` / `…` / 0 | identical |

2,373/2,411 common payloads differ (divergence persists; `eeCycle`
rejoins at tick 41 while `rdram` stays diverged). Route/input artifacts
are ruled out: divergence starts at tick 39, long before the first pad
press (~tick 636). **Stop per the brief — Part 2 chases it.**

## 7. Frames (viewed; 512×448, fbp 112, no corruption)

| Boot | Snap (det tick) | Sidecar fnv1a | Viewed verdict |
| --- | --- | --- | --- |
| B4 | t1090 | `dc4ae5b1` | Select Peak: Peak 1 mountain photo, Peak 1 highlighted, 2/3 locked, correct text |
| B4 | t2100 | — | Race 2ND/2 00:00:06, 1%, trick 240, rider/snow/pines/mountains, EA Radio "Go / Andy Hunter / Exodus" |
| M1 | t1087 | `f34038e5` | Same Select Peak screen (Δ3-tick animation) |
| M1 | t2099 | — | Same race 2ND/2 00:00:06 1%, same EA card, trick 250 (Δ1 tick; ±10/tick is animation-rate noise — cf. F2 B1/B2 160 vs 270 over ~7 ticks) |

Both runs progress identically through menus → race HUD (~1714) → racing
at t2100: the tick-39 divergence is visually silent through t2400.

## 8. Deliverables + wrap-script self-test

- `local/research/LX1/Dockerfile` — image recipe (rev 2: +FFmpeg dev).
- `local/research/LX1/lx1_boot.py` — bradflix det-boot driver (refuses
  without the lease; direct-Xvfb + stdbuf).
- `local/research/LX1/lx1_boot_mac.py` — Mac parity driver (F2 at LX1 root).
- `local/tooling/remote/bradflix_boot.sh` — build + boot by fork SHA,
  pulls `result.json`/`boot.log`/`trace.jsonl`/`suite-*.log` + snap
  frames to `~/dev/ssx3-work/LX1/from-bradflix/<label>/`; usage block in
  the file; per-SHA build dirs; suite failure warns but boots.
- Self-test `WRAP1` (`--stop-tick 150`): rc=0 end to end — lease
  claim/release, sync, checkout (40-hex validated), cached docker build,
  configure rc=0, build 569/569 rc=0, suite 615/616 (warn-through),
  boot bound=target in 7.7 s (152 ticks), pull-back complete
  (`result.json`/`boot.log`/`trace.jsonl`/build+suite logs/12 snap pairs),
  lease clean after. Two script bugs found and fixed during the
  self-test (repo-root path; multiline-SHA capture that executed git
  output — the `HEAD is n` HTTP mystery). Bonus receipt: the fresh
  per-SHA build's runner SHA is `3c570c25…` — **identical to the
  manual `build/` runner: reproducible builds**.

## 9. Budgets, exact commands, gaps

Builds: bradflix 2 (1 failed pre-SSE4.1 + 1 clean) + WRAP1 rebuild;
Mac 1. Boots: bradflix 5 (B1/B2 hang, B3 path bug, B4 full, WRAP1 short);
Mac 1 (M1). Time ~2.5 h of the 3 h box. Scratch `~/dev/ssx3-work/LX1`
2.1 GB (mac build + M1 run + B4 pullback); bradflix
`~/dev/ssx3-work/LX1` 6.8 GB (3 GB ISO + 274 MB codegen + 2×1.8 GB
builds + 247 MB runs). Lease: bradflix free at close (verified);
mini slot released by the driver.

```sh
# deps/image
scp local/research/LX1/Dockerfile bradflix:~/dev/ssx3-work/LX1/
ssh bradflix 'cd ~/dev/ssx3-work/LX1 && docker build -t ssx3-lx1 -f Dockerfile .'
# inputs + fork
COPYFILE_DISABLE=1 tar -C ~/dev/ssx3-work/codegen-ssx3 -cf - . | ssh bradflix 'tar -C ~/dev/ssx3-work/LX1/codegen -xf -'
scp ~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72 bradflix:~/dev/ssx3-work/LX1/inputs/
ssh bradflix 'cp ~/dev/ssx3/"SSX 3 (USA).iso" ~/dev/ssx3-work/LX1/inputs/'
ssh bradflix 'cd ~/dev/ssx3-work/LX1 && git clone --branch ssx3 https://github.com/brad-richardson/PS2Recomp.git PS2Recomp'
# configure+build (bradflix; -msse4.1 workaround, §3)
ssh bradflix 'docker run --rm --user 1000:1000 -e HOME=/work -w /work -v ~/dev/ssx3-work/LX1:/work ssx3-lx1 cmake -S /work/PS2Recomp -B /work/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DPS2X_GAME_CODEGEN_DIR=/work/codegen -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=ON -DCMAKE_C_FLAGS=-msse4.1 -DCMAKE_CXX_FLAGS=-msse4.1'
ssh bradflix 'docker run --rm --user 1000:1000 -e HOME=/work -w /work -v ~/dev/ssx3-work/LX1:/work ssx3-lx1 cmake --build /work/build --parallel 16 --target ps2x_tests ps2EntryRunner'
# mac build (CPU-only)
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/LX1/PS2Recomp 0ed07c4362b9bd53c09094fd028ee05e8aaf021a
cmake -S ~/dev/ssx3-work/LX1/PS2Recomp -B ~/dev/ssx3-work/LX1/mac-build -G Ninja [same flags, Homebrew clang, canonical codegen, no -msse4.1]
cmake --build ~/dev/ssx3-work/LX1/mac-build --parallel 8 --target ps2x_tests ps2EntryRunner
# boots
scp local/research/LX1/lx1_boot.py bradflix:~/dev/ssx3-work/LX1/
ssh bradflix 'cd ~/dev/ssx3-work/LX1 && python3 lx1_boot.py --runner ~/dev/ssx3-work/LX1/build/ps2xRuntime/ps2EntryRunner --label B4 --stop-tick 2400'
python3 local/research/LX1/lx1_boot_mac.py --mode det --backend cpu --runner ~/dev/ssx3-work/LX1/mac-build/ps2xRuntime/ps2EntryRunner --label M1 --stop-tick 2400 --sound off --coverage-tick 2400
python3 /tmp/lx1_hashdiff.py ~/dev/ssx3-work/LX1/run/M1/boot.log ~/dev/ssx3-work/LX1/from-bradflix/B4/boot.log
./local/tooling/remote/bradflix_boot.sh --sha 0ed07c4362b9bd53c09094fd028ee05e8aaf021a --label WRAP1 --stop-tick 150
```

Gaps, stated plainly:
- G1. Parity FAILS at tick 39 (Part 2's chase; the prime suspects from
  facts.md stand: sse2neon-vs-SSE rsqrt/rcp, `long double`, VU1 double
  paths, FP codegen under `-msse4.1` auto-vectorization).
- G2. paraLLEl on bradflix not attempted (ANV present and enumerated;
  needs the parallel-gs fork + Granite submodule + build — out of the
  brief's time box by design).
- G3. Suite is 615/616 on x86 until the E53 fegetround assert is fixed.
- G4. One speed-relevant note, not a number: B4's wall (329 s) trails M1
  (219 s) on an idle 20-core box — llvmpipe software GL; irrelevant for
  correctness boots.
- G5. The wrap script always rebuilds per-SHA dirs from scratch (no
  ccache); fine at ~3 min/build.

## Orchestrator gate, Part 1 (2026-09-25)

**Accepted: host works, parity fails.** bradflix builds (docker image `ssx3-lx1`, no sudo) and runs the
route to the race; frames match the Mac visually. Det-hash is byte-identical for ticks 1–38 and splits
at **tick 39** (eeCycle +8, rdram), long before any input, so something host-dependent changes guest
behaviour early in boot: a float result (sse2neon on arm64 vs native SSE on x86), x87 vs SSE rounding,
a libm call, or host time leaking into a deterministic path. That's a correctness question as well as a
tooling one: one of the two hosts may be wrong vs the PS2. Part 1b released (below); the GPU Part 2
waits. E-lane follow-ups for a later fold: x86 needs `-msse4.1` (CMake sets an arch flag only for ARM);
the E53 FP-mode test reads the x87 word via `fegetround()` on x86.
