# BA1 — Android build flags: -O3 / ThinLTO on the Odin

Worker: muse. Fork `ssx3` base **`173b31f`** (pushed; worktree `~/dev/ssx3-work/BA1/PS2Recomp`, branch `ba1`, never pushed).
Brief: `local/muse/prompts/BA1.md`. Parent review: RV4 §1 + orchestrator adoption.

## 1. Flag audit (base APK build)

Sources: `compile_commands.json` (458 entries) + `build.ninja` link edge +
`CMakeCache.txt` + `metadata_generation_command.txt` from
`.cxx/RelWithDebInfo/*/arm64-v8a/` on bytesize. Read first from the F5 tree
(scratch `f5-*`); flag-relevant sources are identical F5→173b31f except one
added file (`ps2_savestate.cpp`, no flag effect), and the BA1 base build's
own `compile_commands.json` is re-checked after the build.

Toolchain: NDK `28.2.13676358` clang++ (`--target=aarch64-none-linux-android28`,
minSdk 28), CMake 3.22.1 Ninja, AGP 8.6.1 / Gradle 8.9.
Build type: AGP passes `-DCMAKE_BUILD_TYPE=RelWithDebInfo` for
`assembleRelease` itself (`metadata_generation_command.txt`); the release
block in `build.gradle` sets no build type (the `:69` argument is the debug
block's). Cache: `CMAKE_CXX_FLAGS_RELWITHDEBINFO` =
`CMAKE_C_FLAGS_RELWITHDEBINFO` = `-O2 -g -DNDEBUG` (pristine CMake default);
`CMAKE_CXX_FLAGS`/`CMAKE_C_FLAGS` empty.

### Effective flags by TU class

All 458 entries carry `-O2`, `-g` (×2: NDK toolchain + config flags) and
`-DNDEBUG`; 0× `-flto`, 0× `-mcpu`/`-mtune`, 0× `-fno-plt` in the whole db.
Every C++ TU carries, in order: `-frtti -fexceptions` then
`-march=armv8-a+fp+simd+crypto+crc` (root `CMakeLists.txt` `CMAKE_CXX_FLAGS`
after the crypto check) … `-O2 -g -DNDEBUG -fPIC` then
`-march=armv8-a+fp+simd` (root `add_compile_options`) then
`-ffp-contract=off` (root `:111`) then `-std=gnu++20`. The 12 C TUs
(raylib/volk/stb/app-glue) carry only the plain `-march` (crypto probe is
C++-only) with the same `-O2 -g -DNDEBUG`.

| TU class | Example TU | -O | -g | -flto | arch (effective) | FP / exc | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Generated EE (`ps2_game_objects`, unity batch 32) | `ps2_game_objects.dir/Unity/unity_0_cxx.cxx` (296 unity TUs) | -O2 | yes | none | plain simd (see quirk) | `-ffp-contract=off`, rtti+exc on | unity TU |
| VU1 image (runner, `SKIP_UNITY`) | `vu1gen-f5/vu1_00df9699b042f1b9.cpp` (7 TUs) | -O2 | yes | none | plain simd | same | + `ps2EntryRunner_EXPORTS`, boot-ELF define |
| Runtime (`ps2_runtime`, per-file) | `ps2xRuntime/src/lib/ps2_runtime.cpp` | -O2 | yes | none | plain simd | same | not unity-built |
| Link `libps2EntryRunner.so` | `build.ninja` `CXX_SHARED_LIBRARY_LINKER` edge | n/a | n/a | none | n/a | n/a | `-Wl,-Bsymbolic` (NP1), `-Wl,--gc-sections`, `-static-libstdc++`, `--build-id=sha1`, no `-O` |

Arch quirk (verified with the NDK clang itself, `-###`): the command line
carries crypto+crc `-march` first and plain `-march` last; last wins, so
the effective arch is plain `armv8-a+fp+simd` — the root CMake's crypto+crc
detection is defeated by the later `add_compile_options` flag (crypto-only
probe emits `+crypto`/`+crc` ×1; crypto-then-plain emits ×0). Out of scope
for BA1 (flags only as briefed); flagging for F6.

## 2. Staging (bytesize `/home/brad/ba1`)

Recipe: F5 `build-android.sh` (`local/research/BA1/build-android.sh`, SHA
`23a06225…`, per-leg `root=` substituted; remote SHAs match local for all
three). Fork sources via `git archive` from the mini worktree (branch
`ba1`): base `173b31f`, O3 `7d44ba8`, LTO `722057e` (amended; the first LTO
commit `416f1d5` used the IPO property and is retired — see G2). Shared read-only
inputs: codegen `/home/brad/f5/codegen-ssx3` (9,457 files),
vu1gen `/home/brad/f5/vu1gen-f5` (7 files), jniLibs `/home/brad/f5/jniLibs`,
gradle wrapper `/home/brad/n2/PS2Recomp/android`. Fresh input:
paraLLEl-GS @ fork `ssx3` `464f263` + Granite `166ba21` (submodule
populated), tarred from `~/dev/ssx3-work/parallel-gs-ssx3` (24,314 files
both sides; nested `.git` pointers excluded): `gs/gs_renderer.cpp`
`8e6b30c3…`, `gs/gs_interface.hpp` `fee5389f…`, `Granite/CMakeLists.txt`
present. Candidate markers verified remote: o3 gradle 2×
`RELWITHDEBINFO` flag lines, lto cmake 4× `-flto=thin`
(`722057e` re-stage; the `416f1d5` markers were verified before it was
retired). Bytesize idle at each launch
(no ninja/cmake; vk1/vr2fold logs untouched).

## 3. Candidates (one variable each)

| Candidate | Change | APK SHA | APK bytes | .text bytes | Build wall | Link wall / peak RSS |
| --- | --- | --- | --- | --- | --- | --- |
| base (173b31f, current flags) | none | `2dcf2ae9…69abf` | 180,180,552 | 138,018,964 (`0x8438394`) | 8m 16s (48/48) | 1.04 s (`.ninja_log`) / n/a |
| O3 (`7d44ba8`) | gradle: `CMAKE_{C,CXX}_FLAGS_RELWITHDEBINFO=-O3 -g -DNDEBUG` (all targets; keeps `-g`, exact FP) | `bec0d84c…223e4` | 178,280,008 (−1.9 MB vs base) | 138,067,996 (`0x83a861c`, +49 KB) | 8m 34s (48/48) | 1.00 s / n/a |
| O3+ThinLTO (`722057e`) | + explicit `-flto=thin` (compile+link, Android-gated) on `ps2_runtime`, `ps2EntryRunner`, `ps2_game_objects` — the IPO property cannot work here (G2); no full LTO, no fast-math | `96271ec8…9710` | 177,968,712 (−311 KB vs O3) | 137,758,056 (`0x835fb68`, −310 KB) | 11m 32s (48/48, solo) | 6m 51s, peak ld.lld RSS ≈10.6 GB (15 s sampler, lower bound), 0 Killed/FAILED — no OOM on 12 GB WSL |

Flag verification per candidate (own `.cxx` `compile_commands.json` + `build.ninja`):
base 461/461 `-O2`, 0× `flto` (matches §1 audit — F5's db had 458 entries,
+3 sources since a3efbfe); O3 461/461 `-O3`, 0× `flto`, `-g` kept,
`-ffp-contract=off` on all 461; LTO 461/461 `-O3`, 360× `-flto=thin`
(296 game-unity + 51 `ps2_runtime` incl. 4 vu files + 7 vu1 images +
runner unity + runner PCH; 0 in paraLLEl/Granite — the 101 without are 80 PGS/Granite, 11
`ps2_iop`, 2 `ps2_gs_shadow`, 7 deps, 1 NDK glue, all separate targets),
0× `-fuse-ld`, `-Bsymbolic` kept on the link.

Suite: not run — no source change (build flags only), per brief.

## 4. Odin ABBA (≤ 8 launches)

Method: `leg.sh <apk> <R#>` = one atomic `BA1` lease held from install
through play-restore; inside: install + installed-SHA check, F5-method
`cooldown.py` (status 0 + 180 s + status 0), N12-lineage `launch.py`
(variant A: I26-FAST, unpaced, sound on, `PS2X_PGS_PRESENT_PIPELINE=1`,
stop 4500; play-env pin `a8d651a7`), race rate via F4 `phases.py`, then
`restore-play.sh` (F5 APK `4ff81032…` + env `a8d651a7…`, mc0-test emptied,
force-stop, release). Order ABBA per pair; ≤ 8 launches.

| Leg | APK | End | Race rate | GPU busy race mean (n) | Thermal | FATAL |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | base | STOP 4536, 227 s | 1714→4536 / 181.8 s = 15.52/s = **0.259×** | 39.9 % (30) | status 0 (40.7 °C) → 3 | 0 |
| R2 | O3 | STOP 4574, 222 s | 1714→4574 / 177.4 s = 16.12/s = **0.269×** | 40.8 % (29) | status 0 (46.1 °C) → 3 | 0 |
| R3 | O3 | STOP 4556, 216 s | 1714→4556 / 172.8 s = 16.44/s = **0.274×** | 36.2 % (28) | status 0 (49.6 °C) → 3 (1 at first poll) | 0 |
| R4 | base | STOP 4508, 227 s | 1714→4508 / 181.6 s = 15.39/s = **0.257×** | 39.5 % (31) | status 0 (48.4 °C) → 3 | 0 |
| R5 | base | STOP 4600, 225 s | 1714→4600 / 182.2 s = 15.84/s = **0.264×** | 34.2 % (30) | status 0 (47.7 °C) → 3 | 0 |
| R6 | LTO | STOP 4531, 216 s | 1714→4531 / 172.9 s = 16.29/s = **0.272×** | 35.6 % (29) | status 0 (46.9 °C) → 3 | 0 |
| R7 | LTO | STOP 4534, 216 s | 1714→4534 / 173.1 s = 16.29/s = **0.272×** | 35.1 % (28) | status 0 (47.3 °C) → 3 | 0 |
| R8 | base | STOP 4572, 227 s | 1714→4572 / 182.1 s = 15.70/s = **0.262×** | 33.8 % (30) | status 0 (47.7 °C) → 3 (1 at first poll) | 0 |

Pair 1 (base vs O3): base legs 15.52 / 15.39 (agree 0.8 %), mean
**15.455/s = 0.2578×**; O3 legs 16.12 / 16.44 (agree 2.0 %), mean
**16.28/s = 0.2716×**. **O3/base = 1.053 — O3 is +5.3 %**, drift-cancelled
ABBA. O3 kept → pair 2 runs base vs O3+ThinLTO. (All legs: 0 FATAL, 0
disconnects, env restored `a8d651a7` match, mc0-after clean, play APK
restored, force-stopped, lease released.)

Pair 2 (base vs O3+ThinLTO): base legs 15.84 / 15.70 (agree 0.9 %), mean
**15.77/s = 0.2631×**; LTO legs 16.29 / 16.29 (identical), mean
**16.29/s = 0.2718×**. **LTO/base = 1.033 — +3.3 % within-pair.** LTO legs
land exactly where O3 legs landed (pair-1 O3 mean 16.28/s): ThinLTO adds
**~nothing over -O3** (cross-pair O3↔LTO delta +0.06 %, inside leg noise).
The smaller pair-2 ratio is drift in its base legs (+2 % vs pair-1 bases),
not slower LTO. Guest identity: all 8 legs reached the same screens
(tick-2100/3000/4000 + final scaps) with 0 FATAL.

Per-phase means (guest vsyncs/s; menus near 60 are present-capped, short
phases noisy — the ABBA race rows above are the rigorous figures):

| Phase | base (n=4) | O3 (n=2) | LTO (n=2) |
| --- | --- | --- | --- |
| title/startup | 57.36 | 57.74 | 57.38 |
| main menu | 54.86 | 58.39 | 57.85 |
| Select Character | 55.55 | 58.39 | 57.85 |
| Setup Character / Peak | 65.08 | 61.35 | 62.00 |
| Select Mode / Event / My Rules | 54.48 | 53.65 | 53.73 |
| loading + Rival card | 20.43 | 21.56 | 22.23 |
| race (pooled) | 15.61 | 16.28 | 16.29 |

Recommended next action (orchestrator decides for F6): adopt `-O3`
(≈+5 % race, free at build time, keeps `-g`/exact FP); do NOT adopt
ThinLTO (no gain over O3, +~3 min build, 6m51 s link, ≈10.6 GB peak RSS —
too close to the 12 GB WSL ceiling for zero return).

## 5. Exact commands

```sh
# worktree + candidates (fork checkout ~/dev/PS2Recomp untouched; ba1 never pushed)
git -C ~/dev/PS2Recomp worktree add -b ba1 ~/dev/ssx3-work/BA1/PS2Recomp 173b31f
(cd ~/dev/ssx3-work/BA1/PS2Recomp && git commit -m '[BA1] O3 ...')        # 7d44ba8
(cd ~/dev/ssx3-work/BA1/PS2Recomp && git commit -m '[BA1] ThinLTO ...')   # 416f1d5
# stage (bytesize idle: no ninja/cmake, vk1/vr2fold logs untouched)
ssh bytesize 'wsl -d Ubuntu -- bash -lc "mkdir -p /home/brad/ba1/base/PS2Recomp /home/brad/ba1/o3/PS2Recomp /home/brad/ba1/lto/PS2Recomp /home/brad/ba1/parallel-gs"'
git -C ~/dev/ssx3-work/BA1/PS2Recomp archive 173b31f | ssh bytesize 'wsl -d Ubuntu -- bash -lc "tar -x -C /home/brad/ba1/base/PS2Recomp"'
git -C ~/dev/ssx3-work/BA1/PS2Recomp archive 7d44ba8 | ssh bytesize 'wsl -d Ubuntu -- bash -lc "tar -x -C /home/brad/ba1/o3/PS2Recomp"'
git -C ~/dev/ssx3-work/BA1/PS2Recomp archive 722057e | ssh bytesize 'wsl -d Ubuntu -- bash -lc "tar -x -C /home/brad/ba1/lto/PS2Recomp"'  # lto re-staged fresh after the 416f1d5 dud (rm -rf first)
COPYFILE_DISABLE=1 tar -cf - --exclude='./.git' --exclude='./Granite/.git' .  # in ssx3-work/parallel-gs-ssx3 @464f263
  | ssh bytesize 'wsl -d Ubuntu -- bash -lc "tar -x -C /home/brad/ba1/parallel-gs"'
sed "s|ba1/LEG|ba1/$leg|" local/research/BA1/build-android.sh | staged per leg  # remote SHAs match
# builds (each over one held foreground ssh; WSL dies if all clients drop, F5 G5)
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/ba1/base/build.sh"'   # BUILD SUCCESSFUL in 8m 16s
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/ba1/o3/build.sh"'     # BUILD SUCCESSFUL in 8m 34s
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/ba1/lto/build.sh"'    # result below
# LTO mem sampler (second held ssh; RSS KB of top-4 clang/lld, 15 s x70)
# for i in $(seq 1 70); do echo SAMPLE $i SECONDS=$SECONDS; ps -eo rss,comm --no-headers | grep -E clang | sort -rn | head -4; sleep 15; done > /home/brad/ba1/lto/mem-sample.log
# audit pulls
ssh bytesize "wsl -d Ubuntu -- bash -lc 'cat $B/compile_commands.json'" > f5-compile-commands.json  # $B=f5 .cxx arm64-v8a
ssh bytesize "wsl -d Ubuntu -- bash -lc 'cat $B/build.ninja'" > f5-build.ninja
# APK pulls (remote x2 + pulled x2 SHAs all match per APK)
ssh bytesize "wsl -d Ubuntu -- bash -lc 'cat /home/brad/ba1/<leg>/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk'" > ~/dev/ssx3-work/BA1/odin/app-<leg>.apk
# .text / link wall
llvm-readelf -S <obj>/libps2EntryRunner.so | grep text            # NDK 28.2 toolchain
grep libps2EntryRunner.so <.cxx>/arm64-v8a/.ninja_log              # end-start ms = link wall
# Odin (my turn = stable LEASE_FREE after VK2 per orchestrator order F6→VK2→BA1)
bash local/research/BA1/leg.sh base R1    # ABBA pair 1: R1=B R2=O R3=O R4=B
bash local/research/BA1/leg.sh o3 R2      # ABBA pair 2: R5=B R6=L R7=L R8=B
# leg.sh = atomic BA1 claim; install+SHA; cooldown; launch (var A, stop 4500);
# phases.py | tee phases.txt; restore-play.sh (F5 APK + a8d651a7); release
```

## 6. Gaps

- G1. Build-slot contention on the LTO leg: another lane (`/home/brad/f6`,
  staged 23:34, ninja from 23:35) built concurrently with the BA1 LTO build
  (launched ~23:34 into an idle box; a genuine race — neither side could see
  the other). 8 clang processes, ~6 GB available, 1 GB swap used at the
  23:5x sample — no OOM. The LTO build-wall number is contaminated (slower
  under contention); flags/APK bytes are unaffected. Neither build was
  touched.
- G2. First LTO commit (`416f1d5`) was a dud: it set
  `INTERPROCEDURAL_OPTIMIZATION_RELWITHDEBINFO` behind `if(IPO_SUPPORTED)`,
  but CMake 3.22.1's `check_ipo_supported` fails with NDK r28 ("Interprocedural
  optimization not supported", empty reason — the helper prints the wrong-case
  `${ipo_error}`), so the block never applied: 0× `-flto` in compile db and
  link, APK `e41df741…` byte-identical in size to O3. Root cause
  (`CMakeError.log` + a 2-file NDK-toolchain probe on bytesize): CMake 3.22
  forces `-fuse-ld=gold` on IPO links (real links, not just the check) and NDK
  r28 ships no `LLVMgold.so`, so IPO links fail (`unsupported ELF machine
  number`). Fix: explicit `-flto=thin` (probe B: `libbar.so` links, 0×
  `-fuse-ld`, 3× `-flto=thin`), amended into `722057e`. The dud APK never
  touches the Odin. Builds used: 3 of 4 (base, O3, dud); the rebuild is #4.
- G3. Odin lane interference (mine, 00:12–00:13): I chained pre-checks with
  `adb install -r app-base.apk` via `&&` with no lease gate; the lease had
  flipped F6-done → VK2-ST1 between my checks, so the install landed on
  VK2's live session (`Success`, pid 3567 → 6875 across the install,
  installed `base.apk` verified `2dcf2ae9…` = MY base APK). Orchestrator
  verdict: the install killed VK2's stress run (~00:15); its data is void.
  Fix adopted: every Odin install/launch/force-stop holds the lease through
  `local/tooling/odin_lease.sh` (atomic mkdir-lock claim); `launch.py`'s
  pre-check stays as a second guard and its claim/release now go through
  the tool, as do `restore-play.sh`'s; new `leg.sh` holds ONE `BA1` claim
  from install through play-restore per leg (with a stray-vs-Brad guard:
  running app + play env/APK = abort). Odin order: F6 Part 1 → VK2 → BA1;
  BA1 claims only on a stable re-free after VK2.

Budgets: 4 Android builds (base, O3, LTO dud, LTO rebuild — cap reached);
8 Odin launches (cap reached); scratch `~/dev/ssx3-work/BA1` 574 MB
(≤10 GB cap); global disk 73.9/200 GB at close. Suite not run (build flags
only, no source change). Wall time ~3.7 h, over the 3 h box (LTO dud
diagnosis + F6/VK2 queue waits); no lane was disturbed after G3.

## Orchestrator gate (2026-09-26) — adopted, lane closed

**Pass.** Audit confirmed RV4 (all 458 TUs `-O2`, no LTO). `-O3`: **+5.3 %** Odin race (drift-cancelled ABBA);
ThinLTO: +0 over `-O3` at a 7-min, ~10.6 GB link → not adopted. Pushed the `-O3` gradle change as fork `ssx3`
`a5e5940` (cherry-pick of `7d44ba8` onto `703a554`). The unleased install that hit VK2 (G3) led to
`odin_lease.sh`. Follow-up queued: the `-march` quirk (a later plain `armv8-a+fp+simd` overrides the
crypto/crc detection).
