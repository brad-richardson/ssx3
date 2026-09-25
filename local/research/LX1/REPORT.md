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

## Part 1b — tick-39 divergence: host timezone leaks via OSD config (no fix)

Worker: Muse Code, brief `local/muse/prompts/LX1.md` §Part 1b. No push.
Budget ~1.5 h of 2 h.

**Verdict: the divergence is host wall-clock *zone*, not guest math.**
`getTimezoneOffsetMinutes()` (`ps2xRuntime/src/lib/Kernel/Syscalls/Helpers/Runtime.h:239-254`)
reads the HOST's UTC offset with no deterministic override. Mini (EDT box,
mktime quirk yields standard time): **−300 min**. bradflix container (UTC):
**0**. The game reads it through `sceScfGetTimeZone` → `AdjustTime` applied
to the (fixed) RTC, producing different local hour/day — the only 2
differing rdram words at tick 39. Full field-level arithmetic match below.

Method note: no existing knob fit — there is no guest function/PC trace
(E55 is det-hash itself; `PS2X_DIAG_WATCH` needs addresses first). So:
(1) minimal local-only rdump tap (commit `lx1b-rdump.diff` here; applied
to the two scratch trees only, never the fork) dumping 32 MB rdram for
ticks 36–40; (2) `PS2X_DIAG_WATCH` on the differing words (DIAG_TAPS
build); (3) `PS2X_TRACE_SYSCALLS` (+PC) to prove the path. Drivers gained
`--extra-env` (this part's only tooling change).

### Builds + neutrality

Fresh diag dirs both hosts (`DET_HASH_TAP=ON` + `DIAG_TAPS=ON`, else the
Part-1 flags; `-msse4.1` on bradflix): `mac-build-diag` (~12 min, 8 jobs),
`build-diag` (~20 min, 16 jobs — two unity TUs take 10+ min each at -O3
with taps on). Neutrality: MD1 vs M1 **0/186** differing det-hash
payloads; D1 vs B4 **0/149**.

### Dumps: exactly 2 words differ, first at 0x548548

| Tick | Words compared | Differing |
| --- | --- | --- |
| 38 | 8,388,608 | **0** |
| 39 | 8,388,608 | **2**: `0x548548` mac `0x16` (22) vs bradflix `0x03` (3); `0x54855c` mac `0x0f` (15) vs bradflix `0x10` (16) |

### Watch: same stores, same PCs — different values

MD2/D2 (`PS2X_DIAG_WATCH=0x548548,0x54855c`), 4 lines each, identical
except the two values (thread=1, ra=`0x2c75d0`, sp=`0x1fffe60` both):

| PC (`sub_002C7478`) | Store | Mac | bradflix |
| --- | --- | --- | --- |
| `0x2c7650` `sw $t2,8($s5)` | 0x548548 (hour) | 22 | 3 |
| `0x2c7654` | 0x54854c (min) | 34 | 34 |
| `0x2c7668` `sw $a0,1C($s5)` (delay slot) | 0x54855c (day) | 15 | 16 |
| `0x2c76a0` | 0x548560 | 0 | 0 |

The caller unpacks BCD (`srl 4`/`andi 0xF`/`mult 10`, `+2000` for year)
from an 8-byte stack buffer filled by `sceScfGetLocalTimefromRTC`
(`0x40BFE0`, `jal` at `0x2c75c8`, ra matches). Full decoded TMD —
sec 56, min 34, year 2004, month 7 identical; only hour/day differ.

### Chain to the host call

`sceScfGetLocalTimefromRTC` → `sceScfGetTimeZone` (`0x40BAE8`) +
`sceScfGetSummerTime` → `AdjustTime` (`0x40BF48`, offset `$a1 = tz +
60·DST − 540`) applied to the **fixed** RTC (`CD.cpp:708-717`,
2004-07-16 12:34:56 UTC under `PS2X_DETERMINISTIC=1`).
The syscall trace proves the path: `SetOsdConfigParam (4a)` ×2 at boot
(game read-modify-write preserving tz bits), then a `GetOsdConfigParam
(4b)`/`GetOsdConfigParam2 (6f)` burst at t≈0.71 s (tick 39) on **both**
hosts; first 13,000 syscalls byte-identical (names+PCs). No
`SetOsdConfigParam2` anywhere → DST=0 both (init constant).

| Host | `getTimezoneOffsetMinutes()` (verbatim probe) | `$a1` (min) | Predicted local | Observed |
| --- | --- | --- | --- | --- |
| Mini (EDT box; mktime `tm_isdst=0` idiom yields EST) | −300 | −840 | 12:34−14 h = **22:34 day 15** | hour 22, day 15 ✓ |
| bradflix container (UTC) | 0 | −540 | 12:34−9 h = **03:34 day 16** | hour 3, day 16 ✓ |

All six TMD fields match on both hosts. The `eeCycle` +8 at tick 39 is
transient (rejoins at tick 41) and lives in the same tick's
value-dependent flow (syscall sequences identical); its exact
instruction provenance is untraced — no PC-trace facility exists — and
was not chased further.

### Which host matches the PS2?

**Neither.** On a real PS2 the SCF timezone is the *user's* OSD setting
(stored config), which PCSX2 likewise models as console configuration —
not the host machine's zone. Under `PS2X_DETERMINISTIC=1` the value must
be pinned (as the RTC clock already is); the E-lane fix is to gate
`getTimezoneOffsetMinutes()` (or the OSD init) on deterministic mode,
e.g. return 0. Not done here (brief: stop, no fix).

### Receipts + close

- `local/research/LX1/lx1b-rdump.diff` (31 insertions, 1 file; `git
  apply` clean on both trees; trees left with it uncommitted by design).
- Boots: MD1/D1 (dumps), MD2/D2 (watch), MD3/D3 (noisy stack watch,
  superseded), MD4/D4 (syscall trace) — all `target`, one Mac slot each.
- Scratch at close: mini LX1 5.1 GB (diag build + dumps), bradflix LX1
  11 GB (+diag build). Bradflix lease released at close (verified).
- G1 (Part 1) is answered by this section: the suspect list
  (sse2neon/`long double`/VU1/auto-vectorization) is ruled OUT for
  tick 39 — guest FP is innocent; it's host timezone config.

```sh
git -C ~/dev/ssx3-work/LX1/PS2Recomp diff > local/research/LX1/lx1b-rdump.diff
scp local/research/LX1/lx1b-rdump.diff bradflix:~/dev/ssx3-work/LX1/
ssh bradflix 'cd ~/dev/ssx3-work/LX1/PS2Recomp && git apply ~/dev/ssx3-work/LX1/lx1b-rdump.diff'
# diag builds (both flags ON), then e.g.:
python3 local/research/LX1/lx1_boot_mac.py --mode det --backend cpu --runner ~/dev/ssx3-work/LX1/mac-build-diag/ps2xRuntime/ps2EntryRunner --label MD1 --stop-tick 45 --sound off --extra-env PS2X_LX1B_RDUMP_DIR=$PWD/run/MD1/rdump --extra-env PS2X_LX1B_RDUMP_TICKS=36-40
python3 /tmp/lx1b_rdiff.py run/MD1/rdump/rdram-39.bin from-bradflix/D1/rdram-39.bin
```


## Orchestrator gate, Part 1b (2026-09-25)

**Pass: root cause named.** The x86/arm64 "divergence" is the host time zone:
`getTimezoneOffsetMinutes()` (`Runtime.h:239-254`) reads the host's UTC offset with no deterministic
override (mini −300, container 0), the game reads it via `sceScfGetTimeZone` → `AdjustTime` on the fixed
RTC, and two words (local hour/day) differ from tick 39 on. No guest-math difference between hosts was
found. Side bug: the mini reports −300 (EST) in September, when EDT (−240) applies (the "mktime quirk").
Part 1c released: deterministic mode pins the zone; the host path gets DST right; parity re-run.

## Part 1c — tz fix + x86 fixes on `lx1-tz`: tick 39 fixed, new split at 94

Worker: Muse Code, brief `local/muse/prompts/LX1.md` §Part 1c. No push.
Budget ~1.75 h of 2 h.

**Tick 39 is FIXED (ticks 1–93 now identical), but a second divergence
appears at tick 94** — reported below, no second hunt per the brief.

### Branch (from `ec2dbf1`, experiment branch, never pushed)

`lx1-tz`, 3 commits (mini SHAs; bradflix got the same content via
`format-patch` + `git am`, tip `73e01fe` — committer differs so SHAs
differ, but `rev-parse lx1-tz^{tree}` = `068253018e61549407cdf4b8292e50808bd0efc2`
on BOTH sides):

1. `5f32212` deterministic OSD timezone + `tm_gmtoff` host offset + tests
   — `getTimezoneOffsetMinutes()` returns 0 under `PS2X_DETERMINISTIC=1`,
   overridable by `PS2X_TIMEZONE_MINUTES` (strict decimal, fails closed
   to 0 with one diagnostic); host path uses `tm_gmtoff` (DST-aware) on
   Apple/Linux, legacy mktime idiom elsewhere (MSVC/Vita-safe). New
   `ps2_tz_offset_tests.cpp` (4 tests, faked env).
2. `20377a3` x86_64 GCC/Clang `-msse4.1` in the root `CMakeLists.txt`
   (MSVC untouched — different `/arch` spelling, no lane to validate).
3. `b4cb476` E53 FP-mode asserts read MXCSR RC bits on x86
   (`PS2X_FPMODE_X86`) instead of `fegetround()` (x87 word).

`sceScfGetSummerTime` does NOT read the host: DST comes from the OSD2
init constant (`packOsdConfig2(0, 0, …)`, all constant) — verified by the
Part-1b syscall trace (no `SetOsdConfigParam2` anywhere), so no change
needed there. No emitter/TOML changes in `0ed07c4..ec2dbf1` → canonical
codegen stands.

### Builds + suites (always rebuilt; bradflix without manual arch flags)

| Runner (det-hash tap ON, diag taps OFF) | SHA-256 (two reads) | Suite |
| --- | --- | --- |
| Mac `mac-build-tz/ps2xRuntime/ps2EntryRunner` (133,548,320 B) | `b75fd6fa…9d30aa` | **650/650, rc=0** |
| bradflix `build-tz/ps2xRuntime/ps2EntryRunner` (145,691,232 B) | `83a658ee…941ee` | **650/650, rc=0** |

650 = 616 + 30 F3 + 4 tz tests. E53 **passes on x86** now. The bradflix
configure consumed the fork's `-msse4.1` itself (message in
`tz-configure.log`); `bradflix_boot.sh` still passes the flags, which is
now redundant but harmless (keeps old SHAs building) — untouched.

### Parity re-run (I26-FAST, CPU GS, sound off, t2400)

| Boot | Bound | Wall | det-hash lines |
| --- | --- | --- | --- |
| MT1 Mac | target | 233.7 s | 2,421 (ticks 1..2421) |
| BT1 bradflix | target | 328.9 s | 2,410 (ticks 1..2410) |

**Ticks 1–93 byte-identical (all fields). New first divergence at tick
94: `rdram` + `combined` only — `eeCycle`, scratch, VU, count all
identical** (2,317/2,410 later payloads differ). One-line smell: same
guest path/cycles with different data, in early boot right after an env
fix → **another host-env/data leak, not guest math** — but that is a
hunch for the next part's hunt, not a finding.

### Receipts + close

- Fork branch `lx1-tz` lives in `~/dev/PS2Recomp` (mini worktree
  `LX1/PS2Recomp-tz`) + bradflix clone; never pushed. Part-1b's rdump
  tap is NOT in it (stashed on bradflix, separate worktree on mini).
- Boots MT1/BT1; BT1 log pulled to `from-bradflix/BT1/`.
- Scratch at close: mini LX1 7.0 GB, bradflix LX1 13 GB. Bradflix lease
  released at close (verified).

## Orchestrator gate, Part 1c (2026-09-25)

**Pass.** TZ pinned in det mode (host path DST-aware via `tm_gmtoff`), x86 build + E53 test fixed: suites
650/650 on both hosts, ticks 1–93 identical. New split at tick 94 (rdram only; eeCycle identical) looks
like another host-data leak. `lx1-tz` (`5f32212 20377a3 b4cb476`) folds after F4 (F5). Part 1d released.

## Part 1d (PAUSED 2026-09-25 ~17:55Z — progress notes, NOT gated, no verdict)

Question: name tick-94's split source (rdram-only, eeCycle identical per
Part 1c), one-line determinism pin if applicable, parity re-run to t2400.

### Method (all local-only rdump tap, Part-1b style)

- `local/research/LX1/lx1b-rdump.diff` applied UNCOMMITTED to both
  `lx1-tz` trees (`73e01fe` + tap); DIAG_TAPS builds
  `~/dev/ssx3-work/LX1/mac-build-tzd` (arm64, brew LLVM clang++) and
  bradflix `~/dev/ssx3-work/LX1/build-tzd` (amd64 docker ssx3-lx1).
- Taps also used: `PS2X_DIAG_WATCH` (PC/ra/sp), `PS2X_TRACE_SYSCALLS`
  (D4, 812 KB, collected, not yet mined — trace has no ticks, TBD).
- Boots: MD5/MD6 (mac, ps2-env rdump/watch), D5/D6 (bradflix, ps2-env
  rdump/watch), D7 (fespy fesetround log), D8 (swapspy, 0 GL swaps —
  CPU GS, no GL path), **D9 (bradflix `PS2X_EE_FPMODE=ieee`, stop-tick
  120)**, **D10 (bradflix ps2-env control, stop-tick 120)**. D9/D10
  short boots take ~7 s each. No mac ieee boot yet (slots held, see
  pause note). No `main`-branch changes; fork `lx1-tz` never pushed.

### Numbers (all word-wise over 8,388,608 rdram words)

- Tick 92 MD5-vs-D5: **0**. Tick 93: **0**. Tick 94: **24** (list
  below). Tick 95: **30**.
- det-hash `combined` streams (MD5 ticks 1–206, D5 ticks 1–212):
  first differing tick **94**; every tick 94–206 differs, none
  re-converge.
- D10-vs-D5 (x86 ps2-vs-ps2 rerun): **0/0/0/0** at 92/93/94/95 —
  x86 self-consistent, deterministic.
- D9-vs-D5 (x86 ieee-vs-ps2): tick 92: **527**, tick 93: **1618**,
  tick 94: **946**. FP mode steers the guest path from early boot;
  ieee boot is on a different path before the rdump window.
- D9-vs-MD5 tick 94: **965** ≈ D9-vs-D5 (946) → MD5 (ARM ps2-env)
  sits on the **chop path** with D5, far from the ieee path. ARM
  FPCR chop is effective at control-flow level.
- Tick-94 24 words (addr, mac, bradflix, signed delta — ALL +1/+2):

```
0x004c9454 mac=0x426fffff bradflix=0x42700000 +1
0x005426a4 mac=0x3e2aaaa9 bradflix=0x3e2aaaaa +1
0x00622590 mac=0x414ccccc bradflix=0x414ccccd +1
0x006225a4 mac=0x416eeeee bradflix=0x416eeeef +1
0x006efeb0 mac=0x43a67fff bradflix=0x43a68000 +1
0x006efee4 mac=0x4346ffff bradflix=0x43470000 +1
0x006eff10 mac=0x43a67fff bradflix=0x43a68000 +1
0x006eff14 mac=0x4346ffff bradflix=0x43470000 +1
0x006f00e0 mac=0x3a4ccccc bradflix=0x3a4ccccd +1
0x006f00f4 mac=0x3a6eeeee bradflix=0x3a6eeef0 +2
0x00873480 mac=0x3a4ccccc bradflix=0x3a4ccccd +1
0x00873494 mac=0x3a6eeeee bradflix=0x3a6eeef0 +2
0x008734c0 mac=0x3a4ccccc bradflix=0x3a4ccccd +1
0x008734d4 mac=0x3a6eeeee bradflix=0x3a6eeef0 +2
0x00873520 mac=0x3b4ccccc bradflix=0x3b4ccccd +1
0x00873534 mac=0x3b888888 bradflix=0x3b888889 +1
0x00873560 mac=0x3b4ccccc bradflix=0x3b4ccccd +1
0x00873574 mac=0x3b888888 bradflix=0x3b888889 +1
0x01fffa20 mac=0x3b4ccccc bradflix=0x3b4ccccd +1
0x01fffa34 mac=0x3b888888 bradflix=0x3b888889 +1
0x01fffbb0 mac=0x43a67fff bradflix=0x43a68000 +1
0x01fffbe4 mac=0x4346ffff bradflix=0x43470000 +1
0x01fffc10 mac=0x43a67fff bradflix=0x43a68000 +1
0x01fffc14 mac=0x4346ffff bradflix=0x43470000 +1
```

Only 10 distinct values; same mantissas recur at several exponents
(0x4ccccc, 0x6eeeee) and several addresses (copies/mirrors) → a few
distinct FP ops, not 24 independent ones. Just-below-round values
(63.99→64.0, ~199, ~333) match chop-vs-nearest straddle pattern.

### The flip op, fully resolved (0x005426a4)

- Watch (MD6 264 hits, D6 same stream): `3e4ccccd (pc 231cec,
  init) → 3e3bbbbb (pc 231d4c) → FLIP: mac 3e2aaaa9 /
  bradflix 3e2aaaaa (same pc=0x231d4c, ra=0x231cc0, sp, thread=1)`.
  Per-tick countdown timer; values keep decrementing after, staying
  1–3 ULP apart.
- Codegen `sub_00231D18_0x231d18.cpp` (PS2X_GAME_CODEGEN_DIR, pinned
  SHA 8ea8…688a3): path `lwc1 f0,[a0+4]; lwc1 f1,[gp-0x51AC];
  f0=FPU_SUB_S(f0,f1) @0x231d3c; c.lt.s; swc1 f0,[a0+4] @0x231d4c`
  (delay slot, the watched PC). `FPU_SUB_S(a,b)` =
  `(float)(a)-(float)(b)` — plain host sub
  (`ps2xRuntime/include/ps2_runtime_macros.h:930`).
- Inputs PROVEN identical: f0_old = rdram[0x005426a4] = 0x3e3bbbbb
  both (watch stream + tick-93 dumps); K = rdram[gp-0x51AC] =
  0x3c888889 (1/60), a .data constant (~200 copies, e.g.
  0x0049b15c, 0x004c943c), bit-stable across ticks 92–95 both
  hosts; no neighbouring K±δ word exists anywhere in rdram (scan
  0x3c888880–0x3c888890 → only 0x3c888889), so x86's reloaded f1
  cannot be K−δ from memory (modulo gp equality — near-certain:
  gp set once at boot; a wrong gp shifts all gp-loads, not 24
  words).
- Exact decimal: d = 0x3e3bbbbb − 0x3c888889 sits 0.125 ULP below
  0x3e2aaaaa → chop(d) = **0x3e2aaaa9 (mac)**, nearest(d) =
  **0x3e2aaaaa (bradflix)**. Assignment is K-independent (interval
  proof in work notes). So at THIS op: mac = chop-exact,
  bradflix = nearest-exact.
- Mode architecture (verified by read): `EeScheduler::run()` holds
  `ps2_fpmode::ScopedEeMode` (chop+FTZ+DAZ, both archs;
  `ps2xRuntime/include/ps2_fpmode.h`); `[E53] …=ps2` banner on
  BOTH hosts. All other in-tree setters are balanced RAII
  (GS `ScopedHostMode` ×3 + MPEG ×2, VU1 fesetround pair,
  gs_replay pair — latter inactive, no replay env). Build flags
  clean (`-ffp-contract=off`, `-msse4.1`, no fast-math).
  libavcodec/libavutil contain **zero** ldmxcsr (FFmpeg-MXCSR
  theory dead). No ucontext/setjmp anywhere. D4 syscall trace:
  zero mpeg hits.

### Current conclusion (high but not full confidence)

D9≠D5 + D10=D5 proves x86 runs the chop path (scope effective at
boot); MD5-far-from-D9 proves ARM does too. Yet at tick 94's FP
ops x86 produces nearest-exact results while ARM produces
chop-exact. The remaining model: **x86 MXCSR is nearest during
tick-94's guest FP ops — a transient clobberer resets the
run()-installed chop and (given 24→30 slow growth, not D9-style
hundreds) it does not visibly persist as a full ieee path**.
The clobberer is UNNAMED: every static candidate is balanced or
absent. Ruled out: env (banners equal), build flags, FFmpeg
MXCSR, GL (no swaps), fibers, VU1/gs_replay pairs, input values
(for the lead op).

### Resume plan (no new boots/builds started; lease released)

1. MXCSR-vs-tick tap (local-only diff like lx1b-rdump.diff):
   log `_mm_getcsr()`/FPCR at each vsync entry + re-install chop.
   Discriminates clobberer-between-ticks (host-side: dump/hash/
   PNG/snd) vs clobberer-during-tick-94 (which subsystem —
   bisect GS/VU1/MPEG/CD). Needs one diag rebuild per host.
2. Mac ieee boot MD7 (1 P-lane slot; at pause all 4 held by
   `VB1-holdC pid=59219`) to complete the mode matrix, esp.
   mac-ieee-vs-D9 (both nearest ⇒ expect full parity if mode is
   the only host difference).
3. Mine D4-syscalls.txt + MD6/D6 watch PCs for the other 23
   words (single site vs global flip).
4. Pin + parity re-run to t2400 per brief after the source is
   named. NOTE: `PS2X_EE_FPMODE=ieee` everywhere is NOT an
   acceptable pin (changes guest math vs real PS2 chop); the
   right pin makes x86 actually-chop (or names the clobberer).

### Paths

- REPORT/brief: `local/research/LX1/REPORT.md`,
  `local/muse/prompts/LX1.md`, tap
  `local/research/LX1/lx1b-rdump.diff`, tools `/tmp/lx1b_rdiff.py`.
- Mac runs: `~/dev/ssx3-work/LX1/run/MD5` (rdump 92–95,
  boot.log w/ det-hash 1–206), `.../MD6` (watch).
- Pulled: `~/dev/ssx3-work/LX1/from-bradflix/{D5,D6-boot.log,
  D7-boot.log,D4-syscalls.txt,D9,D10}` (D9: ieee rdump 92–94 +
  boot.log; D10: ps2 rdump 92–95 + boot.log).
- Bradflix runs (remote): `~/dev/ssx3-work/LX1/run/{D5,D6,D7,
  D8,D9,D10}`, builds `build-tzd` (diag+taps), `build-tz`;
  lease dir released (was `owner=LX1d-muse … purpose=lx1d-t94`).
- Sources read: `ps2xRuntime/include/ps2_{fpmode,runtime_macros}.h`,
  `src/lib/Kernel/{EeScheduler.cpp,Stubs/MPEG.cpp}`,
  `src/lib/{gs/gs_frontend.cpp,gs/gs_replay_core.cpp,
  vu/ps2_vu1_core.cpp}`, codegen
  `/Users/brad/dev/ssx3-work/codegen-ssx3/
  sub_00231D18_0x231d18.cpp`, `CMakeLists.txt` (flags), ldd of
  `build-tzd/ps2xRuntime/ps2EntryRunner`.
