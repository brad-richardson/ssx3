# N4 — Android APK on the folded fork: rebase, lock-screen-safe, profileable; first on-device CPU profile (title + Select Character)

- Date: 2026-09-23. Brief: `local/muse/prompts/N4.md`.
- Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/N3/REPORT.md`,
  `local/research/PF1/REPORT.md`, `local/research/E32/REPORT.md`.
- HEADLINE: `n2-android` rebased onto the folded `ssx3` (`e57b5f8`); release APK is
  profileable, lock-screen-safe, and writes PNG frame dumps (N3's failure fixed);
  first on-device per-function profiles taken on the title (+Select Character).
  Title is GS-rasterizer-bound (59.5% self); Select Character is VU1-bound
  (91.6% self, guest ticks ~0.2/s while host CPU burns in VU1 FMAC emulation).
  The static recomp itself (guest `sub_*`) is 0.39% / 0.00% — essentially free.
- Budget: 1/3 builds, 2 launches (+0 extra; the `--app` retry ran inside launch 1's
  session, not a new launch), ~4 h of 5 h. No push anywhere; `n2-android`
  local-only on bytesize.

## Mission 1 — rebase `n2-android` (`619d48a`) onto `e57b5f8`

`git fetch origin` (origin/ssx3 = `e57b5f8`, as briefed), then
`git rebase -i --onto origin/ssx3 3adc047` with the bypass/pad picks dropped.
The H1 CMakeLists hunk auto-resolved to empty (content already upstream);
only its `build.gradle` property wiring survived as `8e7d5ac`.

| Old commit | New commit | Disposition / why |
|---|---|---|
| `695b96e` H1 codegen port | `8e7d5ac` (partial) | CMakeLists mechanism DROPPED: all 28 added lines verified present in `e57b5f8`'s `CMakeLists.txt` (`git diff e57b5f8 695b96e -- ps2xRuntime/CMakeLists.txt` shows only E32-fold hunks, no H1 delta); `build.gradle` `ps2xGameCodegenDir` property KEPT (Android-only, absent on `ssx3`) |
| `8c04667` bypass | — | DROPPED: on `ssx3` as `6526329` (`SKIP_MOVIE` ×4 in `origin/ssx3:MPEG.cpp`) |
| `b003c8a` pad script | — | DROPPED: on `ssx3` as `5461ad8` (`PS2X_PAD_SCRIPT` ×4 in `origin/ssx3:Pad.cpp`) |
| `6ec61ee` env shim | `322e55b` | KEPT: Android build files + `ps2x.env` shim per brief |
| `619d48a` arm64-only | `3da81ad` | KEPT: `abiFilters 'arm64-v8a'` |

Result: `n2-android` = `e57b5f8` + 3 local commits, then Mission 2–3 commit
`f9d78da` (below). Local branch only, never pushed. Tree clean except the
pre-existing untracked gradle wrapper files. Full log: `logs/branch-log.txt`.

## Mission 2 — manifest (all verified in the built APK binary via `aapt`)

`android/app/src/main/AndroidManifest.xml` (+6 lines, committed as `f9d78da`):
`android:showWhenLocked="true"` + `android:turnScreenOn="true"` on the
NativeActivity, and `<profileable android:shell="true"/>` under `<application>`.
Release stays release: no debuggable flag, optimization flags untouched.
`aapt dump xmltree` confirms all three in `app-release.apk`
(`logs/aapt-profileable.txt`).

## Mission 3 — PNG frame export fix (PROVEN on device)

Root-cause trace (receipts in `logs/`): N3's log shows two messages per dump —
`FILEIO: [.../upload-latest.png] Failed to open file` (raylib `SaveFileData`:
`fopen(path,"wb")` returned NULL) then `Failed to export image`. The same
directory took every `.txt` sidecar via `std::ofstream` (6,596/6,596 PNG opens
failed across the N3 run; txt 100%). No `fopen` interposer in our code, no
custom raylib `SUPPORT_*` defines, no save-callback set — raylib's fopen path
fails on this device's external-files dir while C++ `ofstream` succeeds
(bionic/FUSE quirk, mechanism unnamed).

Fix (one function, `ps2xRuntime/src/lib/ps2_runtime.cpp`, committed as
`f9d78da`): `writePngBytes()` encodes via `ExportImageToMemory(img,".png")`
(same stb encoder) and writes the bytes with `std::ofstream` (binary) — the
path proven writable. Both `ExportImage` call sites replaced.
Hypothesis/alternative tabled before the run: PNGs land+decode = fopen-path
fault (PROVEN: `upload-latest.png` 320,973 B, `file` = PNG 512×448 RGBA,
renders the title frame); PNGs land corrupt = encoder fault (not observed).

## Mission 4 — build + pins (build 1/3, N3 recipe + same `-P` flags)

`./gradlew assembleRelease` EXIT=0, 25 s incremental. `logs/build4-bars.txt`.

| Item | Value |
|---|---|
| APK | `d93b81a72d101b4b61fa54fb66f560b7eb8f91255e579a66df79597e6ee76229`, 134,164,820 B — build tree + Windows landing + mini ×2 reads agree |
| Unstripped `.so` (obj dir, symbols for reports) | `9528e21aff8bcba6e0dc819654129cb33da37e408a56fecb397c32171c67915c`, 905,605,320 B, `with debug_info, not stripped`, BuildID `8e313844…` — build tree + Windows landing + mini agree |
| APK members | single ABI `lib/arm64-v8a/libps2EntryRunner.so` + dex/manifest/arsc/metadata |
| Symbols | game `sub_*` **9,457 defined `T`, 0 `U`**; `ANativeActivity_onCreate` + `main` `T`; `ExportImageToMemory`, `MemFree`, `writePngBytes` present (`logs/so-probe.txt`) |
| Strings | `PS2X_SKIP_MOVIE` ×1, `PS2X_PAD_SCRIPT` ×2, `ps2x.env` ×4, `SLUS_207.72` ×3, `DEINTERLACE` ×1 |
| Device inputs | SLUS `1b49d05c…` ✓ (matches N3), ISO `3c2f8eb1…` ✓ re-hashed on device (3,005,415,424 B), env `d8321b85…` |

## Mission 5 — Odin (lease `N4 2026-09-22T…`→`LEASE_FREE N4 done`, keyguard `showing=false` throughout)

No lockscreen incident on either launch; BACK sent after each `am start`; all
screencaps show the game rendering, no "Use USB for" dialog. Battery 90→~87%,
charging. Crash buffer: 0 FATAL/tombstone (filtered log).

| Launch | Env / script | Result |
|---|---|---|
| 1 | clean (CD+SKIP+DUMP) | VALID title: logo + "Press START button" on scap at t+10 s and t+28 s; 767 dumps, tick 0→835; PNGs land (fix proven) |
| 2 | + `PS2X_PAD_SCRIPT=25000:start:5000,90000:cross:5000` | **Select Character (Zoe) by t+100 s** — first Odin visit. Both inputs confirmed in log (`armed n=2`, start@25001 ms, cross@90035 ms). 4/4 screencaps byte-distinct; 2,215 dumps, tick 0→2285 |

Guest rates (tick-gated `[frame:dump]`; **diagnostic build — PNG encode on every
present — NOT quotable speed numbers** per the speed rule):

| Phase | Ticks/wall | Rate (% of 59.94) |
|---|---|---|
| L1 title, whole run | 0→835 / 30.95 s | **27.0/s (45.0%)** |
| L2 title+menus, +0–30 s | 0→752 | 25.1/s |
| L2 +30–60 s | 753→1493 | 24.7/s |
| L2 +60–90 s | 1494→2215 | 24.1/s |
| L2 +90–120 s (cross@90 transition) | 2216→2279 | 2.2/s |
| L2 settled Select Character, +120–180 s (profile window) | 2280→2285 | **~0.2/s** |

Note: L1 27.0/s exceeds N3's 21.3/s and PF1's 21.5/s **despite** doing per-frame
PNG encode that N3 silently skipped — the folded base is faster on the title,
but weave-vs-bob (E32) and dump-path changes confound a direct claim; a
dumps-off build is needed for a quotable number.

simpleperf: `-p PID` still denied even profileable
(`event_selection_set.cpp:739 … Permission denied`, `logs/simpleperf-pid-denied.txt`).
`--app` mode works on the profileable build — the unlock this mission needed:
10 s test 66,172 samples, 0 lost. Both missions recorded with
`simpleperf record -g --app com.ps2x.runner --duration 30`, 0 samples lost.

| Profile | pid (main/GameThread) | Samples | Events |
|---|---|---|---|
| title | 309 (343/379) | 194,954 | 166,417,934,387 |
| Select Character | 1454 (1608/1656) | 128,639 | 116,665,403,085 |

Reports symbolized host-side with the unstripped `.so` via `--symfs`
(lib loads from inside `base.apk`; bare `[+offset]` rows resolved with
`llvm-addr2line`, `logs/addr2line.txt`). Full self reports in-repo
(`reports/`); full callgraph reports (2.1/3.7 MB) in `~/dev/ssx3-work/N4/` +
share mirror `/Volumes/share/ssx3/N4/` with the raw `perf.data`.

### Profile 1 — title, top-25 by self (of 1,946 rows, 98.49% captured)

Bare offsets annotated via addr2line (`*`): `+dff210`/`+dfc014` = GS read-path
`std::function` invoke wrappers; `+dfbef4`/`+dfbf90`/`+dfbff4`/`+dfc194` =
`SampleTexture` lambda bodies; `+dfbf14` = `wrapTextureCoordinate`;
`+dfbf68` = `clampInt`; `+dfc04c` = `ReadVramUnlocked`; `+dfc148` =
`applyTexa`; `+de581c`/`+de5824`/`+de5818` = `fnv1a32` (dump hash).

| # | Self | Tid | Symbol |
|---|---|---|---|
| 1 | 25.66% | main | `stbi_zlib_compress` (PNG encode — diagnostics) |
| 2 | 15.99% | GameThread | `GSCpuBackend::WritePixel` |
| 3 | 7.32% | GameThread | `GSCpuBackend::SampleTexture` |
| 4 | 5.58% | GameThread | `GSCpuBackend::DrawTriangle` |
| 5 | 5.37% | GameThread | `GSCpuBackend::LookupCLUT` |
| 6 | 2.74% | GameThread | `GSMem::ReadCT32` |
| 7 | 1.98% | GameThread | `GSMem::ReadP8H` |
| 8 | 1.61% | GameThread | `@plt` |
| 9 | 1.36% | main | `stbi_write_png_to_mem` (diagnostics) |
| 10 | 1.05% | main | `GSCpuBackend::CopyFrameToHostRgba` (VRAM readback) |
| 11 | 0.91% | GameThread | `*+dff210` (GS dispatch) |
| 12 | 0.89% | GameThread | `*+dfbef4` (GS) |
| 13 | 0.85% | GameThread | `*+dfbf14` (GS) |
| 14 | 0.79% | GameThread | `GSCpuBackend::DrawSprite` |
| 15 | 0.78% | main | libc `scudo::HybridMutex::tryLock` |
| 16 | 0.76% | GameThread | `*+dfbf68` (GS) |
| 17 | 0.70% | GameThread | `*+dfbf90` (GS) |
| 18 | 0.70% | GameThread | `GSMem::WriteCT32` |
| 19 | 0.68% | main | `*+de581c` (`fnv1a32`, diagnostics) |
| 20 | 0.65% | GameThread | `VU1Interpreter::commitReadyPipelines` |
| 21 | 0.64% | GameThread | `*+dfc04c` (GS) |
| 22 | 0.63% | GameThread | `*+dfbff4` (GS) |
| 23 | 0.58% | GameThread | `*+dfc014` (GS dispatch) |
| 24 | 0.54% | main | libc `__memcpy_aarch64_nt` |
| 25 | 0.43% | main | libc scudo `allocate` |

### Profile 2 — Select Character, top-25 by self (of 1,497 rows, 99.16% captured)

`+7968xxx` = compiler-rt quad-precision soft-float (`__addtf3`,
`__extendsftf2`, `__eqtf2`, `__multf3`); `+e105d8` = VU1 FMAC lambda;
`+dff210`/`+dff224` = GS dispatch (as above).

| # | Self | Tid | Symbol |
|---|---|---|---|
| 1 | 23.55% | GameThread | `VU1Interpreter::commitReadyPipelines` |
| 2 | 12.45% | GameThread | `VU1Interpreter::calculatePairReadyCycle` |
| 3 | 6.73% | GameThread | `VU1Interpreter::run` |
| 4 | 5.20% | GameThread | `VU1Interpreter::calculateFmacExactResult` |
| 5 | 4.45% | GameThread | `VU1Interpreter::execUpper` |
| 6 | 4.33% | GameThread | `@plt` |
| 7 | 3.94% | GameThread | `VU1Interpreter::markPairWrites` |
| 8 | 3.43% | GameThread | `VU1Interpreter::normalizeOperand` |
| 9 | 2.73% | GameThread | `*+79688bc` (`__addtf3`) |
| 10 | 2.66% | GameThread | `VU1Interpreter::normalizeFmacResult` |
| 11 | 2.55% | GameThread | `VU1Interpreter::calculateFmacProductSticky` |
| 12 | 1.81% | GameThread | `VU1Interpreter::updateFmacFlags` |
| 13 | 1.54% | GameThread | `*+7968cc8` (`__addtf3`) |
| 14 | 1.40% | GameThread | `VU1Interpreter::execLower` |
| 15 | 1.33% | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc` |
| 16 | 1.07% | main | libc `clock_gettime` (main-thread spin-wait) |
| 17 | 0.98% | GameThread | `*+7968ef0` (`__extendsftf2`) |
| 18 | 0.91% | GameThread | `VU1Interpreter::queueVfWrite` |
| 19 | 0.84% | main | `[vdso] __kernel_clock_gettime` |
| 20 | 0.64% | GameThread | `*+7968f74` (`__extendsftf2`) |
| 21 | 0.54% | GameThread | `*+7968f1c` (`__extendsftf2`) |
| 22 | 0.52% | GameThread | `*+7968f5c` (`__extendsftf2`) |
| 23 | 0.50% | GameThread | `VU1Interpreter::applyFmacDest` |
| 24 | 0.41% | GameThread | `VU1Interpreter::progressXgkick` |
| 25 | 0.34% | GameThread | `VU1Interpreter::applyFmacDestAcc` |

### Top-25 by children (callgraph; trimmed to the discriminating frames)

Both screens funnel through one guest function: `sub_00382760` → `Store32` →
`writeIORegister` → `processPendingTransfers` → `processVIF1Data`. Title (62%):
→ `GifArbiter::drain` → `GS::processGIFPacket` → `vertexKick` → `Submit` →
`DrawTriangle` (43.5%) / `SampleTexture` (32.3%). Menu (95%): →
`syncCoreSubsystems` (`+de65cc`) → `VU1Interpreter::run` (94.8%) →
`execUpper` (42.1%) / `commitReadyPipelines` (23.6%, leaf).
Main thread children: title `main`→`run` (35.0%) → `dumpPresentationFrame`
(`+de5a04`, 30.6%) → `writePngBytes` (`+de6218`, 30.3%) → `stbi_write_png_to_mem`
(30.3%) → `stbi_zlib_compress` (27.6%); menu `main` only 2.7% (idle + timers).

### Bucket rollup (brief's buckets + `diag` diagnostics row; `scripts/buckets.py`)

| Bucket | Title self | Menu self | Notes |
|---|---|---|---|
| Guest code (`sub_*`) | 0.39% (163 fns) | 0.00% (19 fns, <0.005%) | static recomp ~free on both |
| VU1 interpreter | 2.15% | **91.55%** | menu incl. ~8–9% compiler-rt quad soft-float |
| GS CPU rasterizer | **59.53%** | 0.59% | incl. std::function dispatch wrappers, `CopyFrameToHostRgba` 1.05% |
| GIF/VIF/DMA | ~0% self (46.7% children via `processVIF1Data`) | ~0% self (95% children) | thin dispatch, no bulk work |
| Present/upload (raylib/GL) | ~0.1% (Adreno GLES) | ~0.05% | single upload + swap; negligible |
| Kernel/syscalls (libc/vdso/kallsyms) | 4.12% | 2.03% | scudo/malloc, memcpy, clock_gettime |
| Frame-dump diagnostics | **28.43%** | 0.29% | title: zlib 25.66 + png_to_mem 1.36 + fnv ~1.1; menu: 2 dumps only |
| Scheduler/sampler/snapshots | 0.09% | 0.00% | `EeScheduler` sort shards (tiny) |
| PLT / STL / other / unresolved | 3.78% / 1.40% residual | 4.70% / 0.00% residual | |

## Findings (table exactly, no verdicts)

1. **Guest EE cost is negligible on both screens** (0.39% / 0.00% self), yet
   one guest function (`sub_00382760`, via VIF1 Store32) parents 62–95% of
   GameThread children. The bottleneck is host emulation of what it submits,
   and it differs by screen: GS rasterizer on title, VU1 on Select Character.
2. **Select Character runs ~3 guest ticks in the 30 s window (0.2/s) with all
   58 late-run frame hashes distinct** — the guest renders new frames, each
   costing ~5–10 s of host VU1 time (pipeline modeling + `long double` FMAC
   emulation via `__multf3`/`__addtf3`). Not a hang (no fatal/exception, 0
   lost samples, presents land).
3. **Frame-dump PNG encode costs 28.4% of all title samples on the main
   thread** (`stbi_zlib_compress` alone 25.66%). Any Odin rate measured with
   `FRAME_DUMP_DIR` set is a diagnostic number, never speed — including the
   27.0/s above and, strictly, N3's 21.3/s (whose encode silently failed).
4. **`simpleperf record -p` is denied on user builds even when profileable**;
   **`--app` works** (first successful on-device CPU profile). `dumpsys
   package` does not surface the profileable flag (display quirk only —
   `aapt` proves it in the APK).
5. **Main thread is idle on the menu** (`clock_gettime` + vdso ≈ 1.9%, app
   2.7% children) — all burn is GameThread. Threading work targets one thread.
6. `EeScheduler::dispatchIrq`/`publishSnapshot` STL sorts appear as
   single-sample shards (title only) — negligible, no action.

## Recommendation (orchestrator decides)

1. ACCEPT: rebase (local branch, no push), profileable + lock-screen manifest,
   PNG fix (proven end-to-end), and both profiles with buckets.
2. Next device numbers need a **dumps-off logs-off build** (28% main-thread
   tax + fnv/hash per present otherwise). One build, title-only re-measure.
3. Threading order per data: (a) VU1 FMAC exactness on a cheaper path
   (`long double` → float/double, flag emulation granularity) and/or VU1
   recomp — unlocks Select Character (~500× needed for 1×); (b) GS GPU
   backend (G lane) — unlocks title/menus (~2× needed for 1× after dumps off);
   (c) guest `sub_*` needs nothing (0.4%).
4. Hand E lane: `sub_00382760` identity (the VIF1 submission hotspot parent),
   VU1 soft-float finding, `dispatchIrq` sort shards (info only).
5. Keep `writePngBytes` + manifest on `n2-android` until E folds or drops
   them; both are local-only commits.

## Gaps

- Title profile window (≈t+40–70) has no overlapping logcat (capture ended at
  script end); pairing rests on whole-run 27.0/s + title screencap at t+28.
- Kernel symbols restricted (`kptr_restrict`, no root): 0.2–0.4% unattributed.
- `writePngBytes` failure mode if the encoder (not fopen) ever breaks is
  untested — no corrupt-PNG case observed.
- Loading/in-race Odin profiles unmeasured (never reached).
- bytesize `~/n4work` holds 63 MB (profiles + texts); `~/n2` total 16 GB
  (pre-existing toolchain/builds); mini `~/dev/ssx3-work/N4` ≈ 1.1 GB
  (APK + unstripped `.so` + profiles). Share mirror `/Volumes/share/ssx3/N4/`.

## Receipts

- Repo: `logs/` (branch-log, build4-bars, so-probe, aapt-profileable,
  simpleperf-pid-denied, tickbins, addr2line, buckets, apk-sha ×2),
  `reports/` (full self reports), `scripts/` (launch1/launch2/buckets/build
  recipes + env files).
- `~/dev/ssx3-work/N4/` + `/Volumes/share/ssx3/N4/`: raw `perf.data` (36/23 MB)
  + full callgraph reports. Unstripped `.so` pinned in ssx3-work
  (`9528e21a…`, matches build tree).
- Leases: Odin claimed `N4 2026-09-23T01:40Z`, released (`LEASE_FREE N4 done`)
  after force-stop; `/data/local/tmp/n4` removed. No source edits on the mini
  fork checkout; no push anywhere.

## Mission 6 — closeout

Force-stop verified (`pidof` exit 1), `/data/local/tmp/n4` removed, lease
released, bytesize Windows staging (`n4-*`) + symfs duplicate removed.
