# N1 — Android native preparation audit (READ-ONLY, no build)

- Date: 2026-09-22. Tables + receipts, no verdicts beyond the missions.
- Read first in full: the fork's `android/README.md` @`3adc0478` (§M1 row 1),
  `docs/research/review-2026-09-22-progress-and-parallelization.md` §Android
  (track deliverable: reproducible arm64 APK + linkage/binding manifest +
  retained logs + app-owned boot paths + one stock-title launch),
  `local/research/I24/REPORT.md` §Task-2 (staged set: .app + ELF + ISO +
  provision + vector) and §cheap-rechecks (what "served to guest" means).
- Fork: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, read at ref
  `3adc0478` = `3adc0478b6d2260acdd28a249466f2eef9a20176` (`rev-parse`,
  doubled). Every fork content read names the ref (`git show REF:path` /
  `git grep REF`); zero fork worktree content reads (E29 mid-lane checkout
  protection). Fork `status --short` = exactly `?? ps2_log.txt`
  (pre-existing, untouched); `HEAD` = `3adc0478` on `ssx3` at N1 open.
- Rules honored: no builds, no installs, no device contact (no adb at all),
  no boots, no lease, zero fork edits/commits/pushes; evidence
  `local/research/N1/` text-only; zero SSD writes; `/tmp/n1-*` scratch
  208,043 B (≤512 MB cap); zero deletions; `COPYFILE_DISABLE=1` on SSD steps.
- SSD rule: every cited file carries size + SHA256 from 2 matching reads
  (`logs/file-shas.txt`); counts re-run twice (`logs/linkage-counts.txt`).

## Mission 1 — Scaffold audit (quote, don't summarize)

All fork paths below are @`3adc0478` (full sha above). "Blocks-N2" = the N2
first build (Mission 3: stub redact, FFmpeg OFF, static checks only) cannot
proceed without it.

| # | Path | Exists | Quoted evidence | Blocks-N2? |
|---|---|---|---|---|
| 1 | `android/README.md` (1164 B, `7627a149…f9bdcf6`) | yes | Requirements: "Android Studio (recommended) or a local Gradle 8.7+ / JDK 17 install", "Android SDK 34 + NDK", "CMake 3.22.1 from the SDK". Build: "Option B — command line (no wrapper is committed; generate it once): `gradle wrapper --gradle-version 8.9` / `./gradlew assembleRelease`". Output: "APK output: `android/app/build/outputs/apk/release/app-release.apk`". Boot: "Since there is no argv on Android, the guest ELF path comes from `PS2X_DEFAULT_BOOT_ELF`, set via the `ps2xBootElf` Gradle property". Stage: `adb push "path/to/game/." /storage/emulated/0/Android/data/com.ps2x.runner/files/`. Logs: "raylib output goes to logcat (`adb logcat -s raylib`); runtime `std::cout`/`cerr` output is not redirected to logcat yet." | no |
| 2 | `android/app/src/main/AndroidManifest.xml` (953 B, `4f2fcad4…1e10e3e`) | yes | No `package=` attr (namespace lives in Gradle). `<application android:label="PS2 Recomp" android:hasCode="false" android:isGame="true">`. `<activity android:name="android.app.NativeActivity" android:configChanges="orientation\|screenSize\|screenLayout\|keyboard\|keyboardHidden\|navigation" android:screenOrientation="landscape" android:exported="true">` + `<!-- Runner shared library built by ps2xRuntime/CMakeLists.txt -->` + `<meta-data android:name="android.app.lib_name" android:value="ps2EntryRunner" />` + MAIN/LAUNCHER intent-filter. Zero `<uses-permission>`, zero other activities/filters/providers. | no |
| 3 | `android/app/build.gradle` (1588 B, `ba3c0a7d…205c845`) | yes | `namespace 'com.ps2x.runner'`, `compileSdk 34`, `ndkVersion '28.2.13676358'`, `applicationId 'com.ps2x.runner'`, `minSdk 28`, `targetSdk 34`, `versionCode 1`, `versionName '0.1.0'`. Default: `def ps2xBootElf = project.findProperty('ps2xBootElf') ?: '/storage/emulated/0/Android/data/com.ps2x.runner/files/game.elf'`. CMake args: `'-DPS2X_BUILD_RECOMP=OFF'`, `'-DPS2X_BUILD_ANALYZER=OFF'`, `'-DPS2X_BUILD_TEST=OFF'`, `'-DPS2X_BUILD_STUDIO=OFF'`, `'-DPS2X_ENABLE_SCCACHE=OFF'`, `'-DPS2X_RUNNER_UNITY_BUILD_BATCH_SIZE=32'`, `'-DANDROID_CPP_FEATURES=rtti exceptions'`, `"-DPS2X_DEFAULT_BOOT_ELF=${ps2xBootElf}"`; `targets 'ps2EntryRunner'`. `externalNativeBuild.cmake { path '../../CMakeLists.txt'; version '3.22.1' }`. `ndk { abiFilters 'arm64-v8a', 'x86_64' }`. Release: `minifyEnabled false`, `signingConfig signingConfigs.debug`. | no |
| 4 | `android/build.gradle` (73 B, `36d655a9…967cb`) + `android/settings.gradle` (263 B, `2f4f5b2d…183f`) + `android/gradle.properties` (133 B, `94ee6207…4b4e`) + `android/gradle/wrapper/gradle-wrapper.properties` (250 B, `3d91f093…88484`) | yes | AGP: `id 'com.android.application' version '8.6.1' apply false`. Settings: `rootProject.name = 'PS2Recomp'`, `include ':app'`, google()+mavenCentral()+gradlePluginPortal(). Properties: `org.gradle.jvmargs=-Xmx4g`, `android.useAndroidX=true`, `# ps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_201.84` (commented example). Wrapper props: `distributionUrl=https\://services.gradle.org/distributions/gradle-8.9-bin.zip`. | no |
| 5 | `android/` gradle wrapper script (`gradlew`, `gradle/wrapper/*.jar`) | MISSING | `git ls-tree -r 3adc0478 -- android` = exactly the 7 files in rows 1–4 (no `gradlew`, no jar, no `jni/`, no `res/`, no Java/Kotlin — consistent with `hasCode="false"`). README row 1 says "no wrapper is committed; generate it once". | no (N2 input: local Gradle 8.7+ or generate wrapper; record which) |
| 6 | Android CMake entry | yes | Row 3 `path '../../CMakeLists.txt'` + root `CMakeLists.txt` (4221 B, `7a4f64e2…24b4a2`): `if(ANDROID)` / `message(STATUS "Android target detected, building runtime only")` + force RECOMP/ANALYZER/TEST/STUDIO OFF (:22–28). `ps2xRuntime/CMakeLists.txt` (23746 B, `42ea0e16…9554a0`): `if(ANDROID) set(PS2X_IS_ANDROID ON)` (:47–48); `set(PLATFORM "Android" CACHE STRING "" FORCE)` (:81–82); `target_link_libraries(ps2_host_backend INTERFACE log android)` (:266–267); `add_library(ps2EntryRunner SHARED ${RUNNER_SRC_FILES})` + `target_link_options(ps2EntryRunner PRIVATE "-Wl,--undefined=ANativeActivity_onCreate")` (:477–482); `target_sources(ps2EntryRunner PRIVATE src/lib/ps2_android_runtime.cpp)` (:623–624). Debug UI excluded: `if(PS2X_ENABLE_DEBUG_UI AND NOT PS2X_IS_VITA AND NOT PS2X_IS_ANDROID)` (:539). | no |
| 7 | Android toolchain file in repo | MISSING (by design) | No `*toolchain*` file at ref; "toolchain" hits are Vita-only (`CMakeLists.txt:4,8`, `ps2xRuntime/CMakeLists.txt:65`, `vita/*.sh`) plus an ARM-inference comment. NDK toolchain is AGP-supplied (row 3: NDK `28.2.13676358`, CMake `3.22.1`). | no |
| 8 | Logcat-routing gap | CODE PRESENT, README STALE | `ps2xRuntime/src/main.cpp` (9215 B, `9a7ea63e…0a1d7f94`) defines `redirectStdioToLogcat()` (:60–105: `pipe()` + `setvbuf` + `dup2` over STDOUT/STDERR + reader thread `__android_log_write(ANDROID_LOG_INFO, "ps2x", line)` with 1024 B `fgets` lines) and calls it first in `main()` under `#if defined(__ANDROID__)` (:182–184). README row 1 still claims "not redirected to logcat yet" — stale. stdout/stderr today = the pipe→logcat path on paper; **never build-verified** (no Android build receipt exists in any lane). | no for build; YES for launch observability (N3+ must confirm `ps2x` tag lines on a real boot) |
| 9 | FFmpeg-defaults-off site | yes (flag + entailment quoted) | `ps2xRuntime/CMakeLists.txt:271–281`: `if(PS2X_IS_ANDROID OR PS2X_IS_IOS)` / `set(PS2X_ENABLE_FFMPEG_DEFAULT OFF)` / `else()` / `set(PS2X_ENABLE_FFMPEG_DEFAULT ON)` / `option(PS2X_ENABLE_FFMPEG "Enable FFmpeg-backed MPEG video decoding" ${PS2X_ENABLE_FFMPEG_DEFAULT})`; OFF branch: `message(STATUS "FFmpeg disabled; MPEG video decode falls back to stub frames")` + `add_library(ffmpeg INTERFACE)`. Enabling on Android today falls into the final `else()` (:363–373): `find_package(PkgConfig REQUIRED)` + `pkg_check_modules(FFMPEG REQUIRED … libavcodec libavformat libavutil libswresample libswscale)` — host pkg-config under NDK cross-compile, i.e. no usable .pc files without extra work. The proven alternative is a C1-style `elseif(PS2X_IS_ANDROID)` IMPORTED-archives block from an Android FFmpeg prefix (iOS template: `696a968`, quoted Mission 2; E-lane owns the edit). | no if N2 keeps the default OFF; YES for any video-decode milestone (N4+) |
| 10 | Activity entry (`ANativeActivity_onCreate` / `android_main` definition) | MISSING | `git grep "ANativeActivity_onCreate\|android_main\|NativeActivity" 3adc0478` = manifest line + CMake `:482` `--undefined` flag only; **zero definitions** in fork sources. Entry must come from a dependency (raylib FetchContent 5.5 glue) — chain unverified at N1 (read-only; no fetch). | no for link (`--undefined` keeps it an `nm -D U` import); YES for launch (N2 must table the provider; N3+ proves it on device) |
| 11 | `ps2xRuntime/src/lib/ps2_android_runtime.cpp` (99 B, `8783cb5f…9325a7a`) | yes (stub) | Full content: `// TODO: on-screen touch joystick / button overlay.` + empty `#if defined(__ANDROID__)` / `#endif`. | no for build; YES for playable input (N5) |
| 12 | Codegen/packaging reuse points | yes (3 proven, 1 needs adoption) | (a) C17 generated set `/Volumes/Extreme SSD/ps2x-i17/codegen-output`: 9455 `.cpp` = 265,956,572 B logical + 2 headers (read-only `stat` census; allocated ~9.5 GB ExFAT). (b) I10 mechanism `PS2X_GAME_CODEGEN_DIR` (`eb3fb16`, +22 lines, quoted Mission 2) + I21 in-tree-drop extension — **NOT at `3adc0478`** (grep-empty); E-lane adoption or N-lane local port required before any full-title link. (c) Title bits pinned by I23/I24: ELF `1b49d05c…` (3,890,784 B), ISO 3005415424 B `3c2f8eb1…`. (d) FetchContent pins by E25: raylib `c1ab645c` (5.5), imgui `b1bcb12`, rlImGui `118221c`; sse2neon `v1.9.1` (root CMake, ARM fetch). | (b) blocks full-title link; N2 stub build proceeds without it |

## Mission 2 — Linkage + boot-path inventory

### How the runtime locates the title (all @`3adc0478`)

`main.cpp:153–176` `getExecutablePath()`: argv[1] wins ("Using argv boot
path"); else `PS2X_DEFAULT_BOOT_ELF` ("Using default boot file";
absolute kept, relative resolved against `current_path()`); else
`throw std::runtime_error("Unable to determine executable path. Pass the
guest ELF as argv[1] or define PS2X_DEFAULT_BOOT_ELF.")`. `main()` then:
`loadELF(filePathStr)` → `configureIoPathsFromElf` → optional
`PS2X_CD_IMAGE` override (`main.cpp:242–250`) → `runtime.run()`.
`loadELF` calls `configureIoPathsFromElf(elfPath)`
(`ps2_runtime.cpp:853`), which sets `elfPath`, `elfDirectory =
parent(elfPath)`, `hostRoot = cdRoot = elfDirectory`, `mcRoot =
elfDirectory/mc0` (`ps2_runtime.cpp:1143–1159`). `IoPaths` struct:
`ps2_runtime.h:295–303` (`elfPath elfDirectory hostRoot cdRoot mcRoot
cdImage`); cold defaults = CWD for dir/host/cd, CWD/`mc0` for mc, empty
ELF + CD image (`ps2_runtime.cpp:336–352`).

### Every hardcoded or env-driven path the Android app must own

| # | Path / input | Site @`3adc0478` | Default | Owner | Android note |
|---|---|---|---|---|---|
| P1 | Guest ELF path | `main.cpp:153–176` + `ps2xRuntime/CMakeLists.txt:518–521` (`PS2X_DEFAULT_BOOT_ELF="…"` compile define from Gradle `ps2xBootElf`; default `/storage/emulated/0/Android/data/com.ps2x.runner/files/game.elf`) | Gradle default above | N-lane (app + push path) | App-owned: bake via `-Pps2xBootElf`, push ELF to the matching `files/` dir (README row M1.1). No argv on Android — this define is the ONLY ELF route. |
| P2 | `PS2X_CD_IMAGE` (ISO) | `main.cpp:242–250` → `setIoPaths` | empty = no image; CD reads fall through to `sceCdRead unresolved LBN … (no mapped file and no configured CD image)` (`Support.h:455–475`, 60369 B, `bce13ab0…d8558`) | E-lane (derivation edit) + N-lane (staging) | NativeActivity launch sets no env: P2 is UNSETTABLE on device as-is. Track needs an E-lane derivation (e.g. default `cdImage` from `elfDirectory`, or a no-arg lookup) — handoff H4. Staging (2.8 GB ISO beside the ELF) is N-lane. |
| P3 | `elfDirectory`/`hostRoot`/`cdRoot` | `ps2_runtime.cpp:1143–1159` | `parent(elfPath)` at `loadELF` | automatic (follows P1) | App-owned by construction once P1 is absolute. |
| P4 | `mcRoot` (`…/mc0`) | `ps2_runtime.cpp:1156`; `MemoryCard.cpp:119,158,685,1275` (55664 B, `eea4c547…faa9`) `create_directories` (tolerant `ec`) | `elfDirectory/mc0` | automatic | App-private `files/` is writable; no pre-creation needed (tolerant mkdir). N5 confirms on device. |
| P5 | `PS2X_DIAG_PERIOD_MS`, `PS2X_DIAG_SEMA`, `PS2X_DIAG_SEMA_S0`, `PS2X_DIAG_SEMA_CREATE`, `PS2X_DIAG_WATCH`, `PS2X_DIAG_REPORT_ALL`, `PS2X_DIAG_DRIVER_PROBE`, `PS2X_DIAG_394ED0`, `PS2X_DIAG_PARK*` | `EeScheduler.cpp:101,159,171`, `CD.cpp:50`, `Dispatcher.cpp:15`, `Sync.cpp:19`, `ps2_e3.h:368`, `ps2_runtime.cpp:1169,1267,1519,1533,1558`, `ps2_park_snapshot.h:52,64,83` | all unset = compiled in, silent | E-lane (owns semantics); N-lane must NOT need them | Unsettable on device: first-launch diagnostics = logcat stdout/stderr (M1.8) + frame/RGBA receipts only. Any diag-gated bring-up needs an E-lane non-env trigger — handoff H7. |
| P6 | `PS2X_DROP_SILENCE` | `ps2_log.h:129` (9347 B, `566c30a6…c1e0`); drop census "ON by default in every build … Deliberately cerr-only" | unset = census ON (good) | E-lane | Favorable default: `[drop]` lines ride the logcat pipe with no action. |
| P7 | `PS2X_FRAME_DUMP_DIR`, `PS2X_TRACE_SYSCALLS[_PC]`, `PS2X_E7_DIR`, `PS2X_E15_TRACE/ALIGN`, `PS2X_E3_*`, `PS2X_E4_*`, `PS2X_PAD_STIM_*` | `ps2_runtime.cpp:395`, `TraceChannel.cpp:79,84`, `ps2_e7.h:19,27`, `ps2_e15.h:10`, `ps2_e3.h:63,89,105`, `ps2_e4.h:72,84,95`, `Pad.cpp:119–120` | all unset = feature off | E-lane | Same unsettable class as P5; frame dumps need an E-lane app-relative default to be usable on device — handoff H7. |
| P8 | `PS2X_MPEG_VECTOR_PATH`, `PS2X_MPEG_FEED_TRACE` (I23 C3/C5 vector diagnostics) | ABSENT at `3adc0478` (grep-empty; live only on `i23-ffmpeg-ios` @`aa73dbc`) | n/a | E-lane (merge) | N4 vector parity needs the merge — handoff H3. |

### Generated-title linkage surface (the APK must link)

| # | Surface | Count / identity | Source @ref (or named lane commit) |
|---|---|---|---|
| L1 | Function-table slots | 833,862 (`base 0x100008`, `end 0x42e520`) | `register_functions.cpp` header (32,674,881 B, `564acae2…6655b`, re-read ×2) |
| L2 | Table assignments | 398,961 `g_ps2RecompiledFunctionTable[…]` lines (re-counted ×2) | same file |
| L3 | Distinct `sub_*` symbols | 9,441 (re-counted ×2) = 9,441 `^void sub_` decls in committed `ps2_recompiled_functions.h` (794,469 B, `e2fa11e8…160e0`) | same file + `src/runner/ps2_recompiled_functions.h` |
| L4 | Committed bodies at ref | 5 `sub_*.cpp` + `register_functions.cpp` + header = 7 files in `src/runner/` | `git ls-tree 3adc0478 -- ps2xRuntime/src/runner` (`/tmp/n1-runner-files.txt`) |
| L5 | Full generated set (C17) | 9,455 `.cpp` = 265,956,572 B logical + 2 headers; configure prints `PS2X: game objects: 9455 sources` (I23) | `/Volumes/Extreme SSD/ps2x-i17/codegen-output` (read-only census); I23 REPORT §build-stack |
| L6 | E-lane manifest scale | 9,457 generated names (E25 audit); 552 pinned `.o`; 543/543 edges, `-j2`, 530.8 s build + 72.5 s configure (host Release) | E25 REPORT Missions 2–4 |
| L7 | In-APK form | ALL linked into `libps2EntryRunner.so` (`SHARED`, M1.6): at ref via `file(GLOB … src/runner/*.cpp)` (:448–458); with I10 via `ps2_game_objects` STATIC lib + in-tree drop (iOS analog `libps2_game_objects.a` sha `f356aaa7…`, byte-identical I17/I18/I21/I23) | `ps2xRuntime/CMakeLists.txt:448–458`; `eb3fb16` (quoted below); I23 §final-build |
| L8 | Codegen manifests | `games/ssx3/ssx3.toml` (56644 B, `2f2ae543…aaf1c`: input ELF + sweep CSV + output dir + `single_file_output = false` + stub list) + `games/ssx3/ssx3-functions.sweep.csv` (336944 B, `7c827add…b9ba`, 9284 lines = header + 9283 functions; sha EQUALS I17/I18/I21/I23's — codegen input unchanged) | both @`3adc0478`, re-read ×2 |
| L9 | Missing generated pieces at ref | `src/runner/ps2_recompiled_functions.cpp` + `include/ps2_recompiled_*.h` absent (gitignored, generated); `.gitignore` even ignores `ps2xRuntime/src/runner` + `register_functions.cpp` (tracked copies are force-added) | `git ls-tree` (empty) + `.gitignore:15–20` |

I10 reuse mechanism (`eb3fb16`, `muse-i10`, NOT at ref — E-lane adoption
candidate H1), quoted verbatim:
`set(PS2X_GAME_CODEGEN_DIR "" CACHE PATH "ps2_recomp output dir for one
game (register_functions.cpp + function .cpps + ps2_recompiled_*.h); when
set, builds them as ps2_game_objects and drops the in-tree stub table")`
+ `list(REMOVE_ITEM RUNNER_SRC_FILES …/register_functions.cpp)` +
`file(GLOB PS2X_GAME_SOURCES … "${PS2X_GAME_CODEGEN_DIR}/*.cpp")` +
`add_library(ps2_game_objects STATIC …)` (unity batch 32) +
`target_link_libraries(ps2_game_objects PUBLIC ps2_runtime)` +
`target_link_libraries(ps2EntryRunner PRIVATE ps2_game_objects)`.
I21 extension (@`193451a:515–523`) additionally drops the in-tree
`sub_*.cpp` (`dropped 5 in-tree game sources`).

### iOS staged set (I24 §Task-2) vs Android — row by row

| # | I24 staged piece | iOS receipt | Android transfer | Differs |
|---|---|---|---|---|
| C1 | `.app` bundle (build-tree binary + sign) | 122,458,696 B pre-sign `edb3eadc…`; post-sign 122,717,056 B (I24; CMS time attr only) | Build-tree `libps2EntryRunner.so` (arm64-v8a) + Gradle APK assembly + debug signing = direct analog | Mach-O→ELF `.so`; `codesign`→`apksigner`/Gradle-debug; bundle-id→`applicationId com.ps2x.runner`; no `embedded.mobileprovision` (debug key instead) |
| C2 | Guest ELF beside binary | `SLUS_207.72` `1b49d05c…` (3,890,784 B), argv[1] | Same bytes via `adb push` to `files/` + `ps2xBootElf` define (P1) | No argv: compile-time define replaces the launch argument |
| C3 | ISO beside binary | `SSX3.iso` 3005415424 B `3c2f8eb1…`, via `PS2X_CD_IMAGE` env (`devicectl -e`) | Same bytes via `adb push`; env route MISSING (P2) | `devicectl -e` has no NativeActivity equivalent → E-lane derivation (H4) |
| C4 | Provisioning/entitlements | wildcard profile `f0793278-…`, identity `295EFB42…`, I21 entitlements plist | Debug signing (`signingConfigs.debug`, M1.3) + `minSdk 28` install | No Apple identity/profile; `adb install` replaces `devicectl device install app` |
| C5 | Vector file (`i24-v3.m2v`) + C3/C5 diagnostics | V3 5040 B `cde8a830…`; `[MPEG:vector]`/`[MPEG:feed-trace]` lines; `wrote=…/tmp//i23-vector-rgba.bin` retrieval | Same vector bytes pushable; diagnostic code ABSENT at ref (P8) | Needs H3 merge + an app-relative write dir (`files/` instead of `TMPDIR`) |
| C6 | Console/log capture | `devicectl … --console` 45611 lines + `device copy from` retrieval | `adb logcat -s ps2x` (M1.8 pipe) + `adb pull` from `files/` | Tag/filter shape differs; content (stdout/stderr + `[drop]` census) transfers |
| C7 | Pack launch env (`PS2X_DIAG_*`, period/sema) | 6-key `-e` dict on every I-probe | All unsettable (P5) | First-launch flies silent-diag; needs H7 for any gated bring-up |
| C8 | "Served to guest" bar (I24 cheap-rechecks) | P2b/P9b NOT OBSERVED (main parked, 0 guest frames); decoder proof ≠ guest serve | Identical bar for the Android track: logcat + frame/RGBA receipts must show a GUEST-visible frame + resume, not a diagnostic drain | No difference — the bar transfers verbatim |

## Mission 3 — N2 plan (scoped, costed, gated)

N2 brief-input (not the brief — one section). N2 = first build + static
checks only: no install, no device, no boot (device contact starts at N5).

### The exact first build

| Item | Spec (from M1 rows, not invented) |
|---|---|
| Target | `ps2EntryRunner` SHARED (`libps2EntryRunner.so`), in-tree stub sources ONLY (7 files, L4), FFmpeg default OFF (M1.9), `assembleRelease` |
| Toolchain | NDK `28.2.13676358` + AGP `8.6.1` + Gradle 8.9 (wrapper props; local Gradle 8.7+ if wrapper ungenerated — M1.5) + SDK 34 + CMake `3.22.1` + JDK 17 (README M1.1) |
| Flags | `android/app/build.gradle` cmake args verbatim (M1.3) + `-Pps2xBootElf=/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72` (gradle.properties commented example, M1.4); ABIs `arm64-v8a` + `x86_64` (record both, gate on arm64) |
| Fetch inputs | Network at configure: raylib 5.5 (`c1ab645c`), sse2neon `v1.9.1` (root CMake ARM branch); imgui/rlImGui SKIPPED on Android (M1.6 :539 gate). N2 pins all three resolved SHAs against E25's. |
| Worktree rule | Separate worktree/build dir at `3adc0478`; never the E-lane checkout; `.cxx/` + `.gradle/` already gitignored (M1: `.gitignore:21–23`) |
| Expected outputs | `android/app/build/outputs/apk/release/app-release.apk` + per-ABI `libps2EntryRunner.so` under `android/app/build/intermediates/` (Gradle layout; N2 records exact paths) |
| Expected sizes | MEASURED, not claimed: stub-only `.so` has no precedent (host 163,529,696 B and iOS 122,458,696 B both carry all 9,455 game objects + logs). Budget: arm64 `.so` ≤ 80 MB, APK ≤ 100 MB (generous vs raylib+runtime scale; N2 records actuals + `size`/`nm` decomposition for the N3 full-link comparison) |
| Cost | Configure ~1–2 min (fetch-bound) + build ~10–20 min `-j2`-class (iOS FFmpeg build 10m00s; host 530.8 s) + static checks; 6 h box with room for one retry |

### Its success bars (all must pass)

| # | Bar | Check |
|---|---|---|
| B1 | Exit | `./gradlew assembleRelease` (or generated wrapper) exit 0; zero `error:` lines; configure log shows `Android target detected, building runtime only` + `FFmpeg disabled; MPEG video decode falls back to stub frames` |
| B2 | `file` | arm64 `.so` = `ELF 64-bit LSB shared object, ARM aarch64`; APK = `Zip archive`; x86_64 `.so` present (recorded, ungated) |
| B3 | Symbols | `nm -D`: `U ANativeActivity_onCreate` (import, M1.10 — provider tabled: which linked object defines/uses it, raylib version line); `nm -g`: `main` defined; defined `sub_*` count = 5 bodies (L4) + stub table base/end symbols; `without FFmpeg` string present (stub branch compiled IN, the OFF receipt); `ps2x` logcat tag string present |
| B4 | Size budget | arm64 `.so` ≤ 80 MB and APK ≤ 100 MB, with per-section `size` output committed; over-budget = investigate (symbols/strip level), not silent-pass |
| B5 | Reproducibility seed | Two consecutive builds: `.so` sha recorded both times; equal = receipt, differ = table cause class (ar timestamps per E25) — either is a result, not a failure |
| B6 | Zero-drift | Fork unmoved (`3adc0478` both ends), zero fork commits, E-lane checkout untouched; evidence text-only |

### Stop rules

| Failure | Disposition |
|---|---|
| Missing SDK/NDK/CMake/JDK/Gradle; FetchContent network failure; ExFAT sidecar/`._*` compile poisoning (E25 class) | TABLE N2 (environment): fix env/purge, re-run same spec once; second failure → new brief, same scope |
| Compile error in `ps2_runtime`/`main.cpp`/raylib glue under NDK clang | RE-SCOPE the track: table file + error + minimal fix shape for E-lane; N2 does not edit runtime sources |
| Link error: `ANativeActivity_onCreate` (or any NDK symbol) unresolved at `.so` link | RE-SCOPE: entry-provider design question (M1.10) → E-lane; N2 stops after tabling the undefined set |
| B4 over-budget with no identified cause | TABLE N2 with the decomposition; re-scope only if cause = source change |
| Any urge to install/boot/push past static checks | STOP: device contact is N5-gated, not N2 |

### Ordered N2→N5 milestone chain

| Step | Milestone | Inputs | Closes with |
|---|---|---|---|
| N2 | Stub `.so` + APK + static bars (this input) | M1 scaffold @ref; NDK/SDK host; FetchContent network | B1–B6 receipts; entry-provider table; size baseline |
| N3 | Full-title link + linkage manifest | H1 adopted (or N-lane local port of `eb3fb16` + I21 ext, unpushed like I-lane); C17 set read-only (L5); N2 size baseline | arm64 `.so` with 9,441 `sub_*` defined + 398,961-line table linked; manifest (object count, symbol census, section sizes); `file`/`nm`/budget bars re-run; still no device |
| N4 | FFmpeg-Android prefix + ON build + vector parity | H2 prefix recipe + ANDROID IMPORTED block; H3 C3/C5 merge; host-7.1.1 anchors (I24: V3 `parsed=5040 packets=0/1`, RGBA `048b41af…`) | Prefix archives (`lipo`-analog `llvm-readobj` arm64) + ON `.so` (`without FFmpeg` ×0, `ff_mpeg2video_decoder` linked) + host-side vector-harness parity; still no device |
| N5 | Install + stock-title launch to a named checkpoint | H4 boot-path derivation; H5 entry proof; H6 logcat confirm; H7 diag escalation if needed; ELF+ISO staging (C2/C3); Odin lease | `adb install` exit 0; launch to checkpoint (menu/race-card, named by E-lane state); retained logcat (`ps2x` tag) + `adb pull` receipts; C8 guest-serve bar applied |

### E-lane handoff table (E owns every edit; N names file + symbol + why)

| # | File | Symbol / site | Why (N-lane need) |
|---|---|---|---|
| H1 | `ps2xRuntime/CMakeLists.txt` | Adopt `PS2X_GAME_CODEGEN_DIR` (`eb3fb16` + I21 @`193451a:515–523` drop ext) | Full-title `ps2_game_objects` link for N3; zero-behavior default preserves all other builds |
| H2 | `ps2xRuntime/CMakeLists.txt` | `elseif(PS2X_IS_ANDROID)` IMPORTED-archives block (C1 `696a968` analog: `PS2X_FFMPEG_ANDROID_ROOT` + 3–5 `ffmpeg_*` IMPORTED libs + loud FATAL_ERROR) + C2-analog default flip | `PS2X_ENABLE_FFMPEG=ON` under NDK without host pkg-config (M1.9); N4 |
| H3 | `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` | Merge C3 (`29633ee`, `PS2X_MPEG_VECTOR_PATH`) + C5 (`aa73dbc`, `PS2X_MPEG_FEED_TRACE`) from `i23-ffmpeg-ios` | N4 device vector parity (same fields I24 proved on iOS); unset = zero behavior change |
| H4 | `ps2xRuntime/src/main.cpp` (`getExecutablePath` area) or `ps2_runtime.cpp` (`configureIoPathsFromElf`) | New no-env `cdImage` derivation (e.g. default from `elfDirectory`, exact contract E's call) | `PS2X_CD_IMAGE` is unsettable on NativeActivity (P2); without this the title cannot stream on device |
| H5 | Entry chain (raylib glue or new `ps2_android_runtime.cpp` code) | Provide/verify `ANativeActivity_onCreate`→`main()` path | M1.10: no in-fork definition; N2 tables the provider, E owns any missing piece |
| H6 | `android/README.md` + `ps2xRuntime/src/main.cpp` (`redirectStdioToLogcat`) | Correct the stale "not redirected yet" line after N5 confirms `ps2x`-tag logcat lines | Doc/code mismatch (M1.8); verification rides the first real boot |
| H7 | Any `PS2X_DIAG_*` / `PS2X_FRAME_DUMP_DIR` consumer (only if N5 bring-up needs it) | Non-env trigger or app-relative default (contract E's call) | P5/P7 are unsettable on device; silent-diag first launch is the default plan, this is the fallback |
| H8 | `ps2xRuntime/src/lib/ps2_android_runtime.cpp` | Touch joystick/button overlay (file's own TODO) | Playable input for the N5 stock-title launch (M1.11) |

## Success bars (tabled)

| Bar (N1 prompt) | N1 receipt |
|---|---|
| Scaffold table with quoted evidence + blocks-N2 flags | Mission 1, 12 rows, every quote @`3adc0478` with size+sha |
| Path + linkage inventory with iOS comparison | Mission 2: P1–P8 paths, L1–L9 linkage, C1–C8 iOS rows |
| N2-input with build spec + bars + stops + milestone chain + E-handoff table | Mission 3: build table, B1–B6, stop table, N2→N5 chain, H1–H8 |
| Zero mutations | Zero fork ops beyond `rev-parse`/`status`/`ls-tree`/`show`/`grep`; zero SSD writes; zero deletions; E-lane checkout never moved (`3adc0478` throughout); no adb/build/boot/lease |
| Tail receipt with byte-exact prefix sha | Below |

## What N1 could not do

- Build, install, boot, or touch a device (forbidden; no adb at all) — M1.8/M1.10 stay code-shape findings until N2/N5.
- Name the `ANativeActivity_onCreate` provider beyond "must come from a dependency" (raylib 5.5 fetch uninspected — no network, no checkout; N2 tables it from the real link).
- Re-verify C17's 9,455 sources byte-for-byte against a fresh codegen run (codegen forbidden; census is names+count+logical bytes; content trust rides I17/I18/I21/I23's byte-identical `f356aaa7…` lib).
- Resolve the 9,441-vs-9,455-vs-9,457 delta beyond tabling (distinct `sub_*` syms vs C17 `.cpp` count vs E25 name manifest — N3's manifest reconciles).
- Confirm `mc0` writability and `files/` layout on a real device (N5).
- Merge or port anything (H1–H8 are E-lane owned; N1 is read-only).

## Receipt paths

- `local/research/N1/REPORT.md` (this file)
- `local/research/N1/logs/file-shas.txt` (22 fork files: size + sha, 2 matching passes)
- `local/research/N1/logs/linkage-counts.txt` (slots/assignments/symbols/csv, counted ×2)
- `local/research/N1/logs/ref-pin.txt` (ref resolution + fork status + read-rule note)
- `local/research/N1/logs/env-inventory.txt` (every `getenv("PS2X_…")` site @ref)
- `local/research/N1/logs/exact-commands.txt` (every fork/SSD command N1 ran)
- `/tmp/n1-runner-files.txt` (341 B) + `/tmp/n1-sub-symbols.txt` (207,702 B): transient scratch, kept

## TAIL RECEIPT

Report written in 4 chunks (header + Mission 1; Mission 2; Mission 3 + bars + could-not-do + receipts; this receipt). Pre-receipt measure: 205 lines total, sha256 `8581fed5208bf9c44be4d025d618e01d644eda8b6fa49f6d9f6484836d089d63` over lines 1–205 (everything before this `## TAIL RECEIPT` section).
Tail content line: "`/tmp/n1-runner-files.txt` (341 B) + `/tmp/n1-sub-symbols.txt` (207,702 B): transient scratch, kept". This receipt line ends the report. END-N1-REPORT.

