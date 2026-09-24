# N5 — Odin: current tree, dumps-off, first real speed numbers through the race

- Date: 2026-09-23/24. Brief: `local/muse/prompts/N5.md`, plus orchestrator
  amendments: new branch instead of a rebase; the vsync-rate line; launch
  first as a functional check; the tap guard as build 3. Worker: Claude Code
  (Opus pane).
- **HEADLINE: the Odin now plays title → menus → Select Character (rider
  drawn) → Happiness race (world draws, race clock and speed advance) on
  the current tree.**
  - First diagnostics-off speed numbers, from two clean runs:
    - title **0.47×**
    - main menu **0.44×**
    - Select Character **0.33×** (was ~0.2 vsyncs/s, about 100× slower,
      in N4)
    - Select Mode/Event **0.39×**
    - race **0.19–0.26×** (11.5–15.5 guest vsyncs/s over the first
      41–47 s of racing)
  - Presents are ~60/s throughout.
  - In the race, VU1 interpreter 50 % self and GS CPU rasterizer 36 %;
    guest code 0.43 %.
  - Found and fixed on the way: `eac6cba` compiled the E40–E44 watch taps
    into every guest store (guest `.text` 3.2×). The new
    `PS2X_ENABLE_DIAG_TAPS` guard (`[N5-local]` `6c335e6`) restores N4's
    size. The diff is below as a candidate for fork `ssx3`.
- Budget: **3/3 builds** (1 OOM, 1 taps-in, 1 clean), **4/5 launches**,
  ~3.5 h of 5 h. No push anywhere; `n5-android` is local on bytesize and
  `n2-android` untouched at `65c95d9`.
- Odin: lease `N5 …` → `LEASE_FREE N5 done 2026-09-24T00:26:22Z`;
  `am force-stop` after every run (`pid-after=none` ×4);
  `/data/local/tmp/n5` removed. Battery 31 → 41 %, charging throughout.
  Keyguard `showing=false` before every launch.

## Ledger-ready table (speed builds only)

Build: APK **`b9737306b65c8976eea5f438b1d2c4f162fa67d93b9b12ed81012bf4992779ce`**
(`n5-android` @ `6c335e6`).
- Diagnostics: runtime/aggressive logs OFF, frame dumps OFF (env unset),
  guest-memory taps compiled out.
- Env: `PS2X_VSYNC_RATE_LOG=1` (one line per 5 s),
  `PS2X_SKIP_MOVIE=1` (dev-only), E33 route with `PS2X_PAD_SCRIPT_CLOCK=vsync`.
- Device: Odin 3, CPU GS backend, E45 double VU1 FMAC.
- Rate = guest vsyncs per wall second (tick deltas interpolated from
  `[vsync-rate]` lines at each phase's boundary ticks).
- Phase boundaries = the route's guest-ms anchors (tick = ms × 5994/100000)
  cross-checked by screencap.

| Phase (ticks) | L2 vsyncs/s | L4 vsyncs/s | Ratio ÷59.94 | Presents/s (SF) | Notes |
|---|---|---|---|---|---|
| Title (0→621) | 28.17 | 28.02 | **0.47×** | 59.9–60.1 | PF1 0.36× (21.5/s, N3 APK) |
| Main menu (621→1238) | 26.25 | 26.17 | **0.44×** | 59.2–59.9 | PF1 My Rules 0.43× (25.5/s) |
| Select Character (1238→1852) | 19.82 | 19.78 | **0.33×** | 59.7–60.1 | rider (Zoe) drawn; N4 ~0.2/s (diagnostic build) |
| Select Mode + Select Event (1852→3892) | 23.41 | 23.42 | **0.39×** | 59.2–60.4 | |
| Loading + Rival Challenge dialog (3892→7089) | 16.61 | 11.54 | 0.19–0.28× | 59.4–60.6 | steady *within* a run (L2 ~16/s, L4 ~11/s per 5 s bin), differs between runs |
| **Race** (7089→9906 / →9564) | **11.52** | **15.47** | **0.19–0.26×** | 59.7–60.6 | first 47 s / 41 s of race (600 s cap); per-5 s 9.4–14.0 (L2), 11.8–19.4 (L4) |

- Speed-number runs: L2 and L4, same APK and route. The non-race phases
  agree within 1 %.
- Race and pre-race rates change with race content. The runs diverge
  (L1 1st place / sun, L2 1st → 2nd, L4 2nd / in fog). That's consistent
  with the RTC-seeded RNG named in `de3781a`, but I didn't test that.
- Thermals (L4 sampler, every 10 s):
  - cpu7 held **4.32 GHz** the whole run, and cpu5 1.79–2.00 GHz.
  - CPU temperature `cpu-1-1-1` read 80–104 °C (the ~104 °C reading is
    the known clamp), and Android thermal status was 3 from t+21 s.
  - No clock drop, so the race spread isn't thermal.
- Presents run at ~60/s in every phase: the host loop presents whether or
  not the guest advanced, so presents aren't guest frames. The panel runs
  at 120 Hz (8.33 ms refresh period in the SF dumps).

### Diagnostic runs (not ledger speed)

| Phase | L1 taps-in (`6298a616`) | L3 profile run (`b9737306`) |
|---|---|---|
| Title | 27.96 | 27.57 |
| Main menu | 25.08 | 25.43 |
| Select Character | 19.29 | 19.83 |
| Select Mode + Event | 22.42 | 23.32 |
| Loading + dialog | 15.28 | 15.76 |
| Race | 9.13 (first 34 s) | 6.84 (first ~9 s; simpleperf from tick 7,424; ~5–7/s even before it started) |

Tap cost, L1 vs the L2/L4 mean, menus only (race content confounds the race):
- title −0.5 %
- main menu −4.3 %
- Select Character −2.6 %
- Select Mode/Event −4.3 %

That's one diagnostic run, so indicative only.

## Launches

| Launch | APK | Result |
|---|---|---|
| L1-diag | `6298a616` (taps in) | SC with rider (tick 1,306), all 13 presses, race 00:00:11 → 00:00:33 (sky, sun, lens flare, terrain shards), 34 → 53 MPH; wall cap at tick 9,115; 0 FATAL. SF layer picked wrong (leash), so no presents |
| L2-speed | `b9737306` | SC with rider (tick 1,320), 13/13 presses, race to 00:00:46 (tick 9,906); cap 600 s; 0 FATAL |
| L3-profile | `b9737306` | race reached (tick 7,325); 30 s `simpleperf record -g --app` from tick 7,424; 0 FATAL |
| L4-speed2 | `b9737306` | repeat of L2 with a thermal/clock sampler; race to 00:00:32+ (tick 9,564); 0 FATAL |

- Screencaps in the repo (`shots/`, JPEG 960 px):
  - `L2-select-character-tick1320.jpg` (Zoe drawn, plus G44's stray menu
    sprites)
  - `L2-race-0032-tick9004.jpg`
  - `L1diag-race-0033-sun-tick9115.jpg`
  - `L4-race-0032-fog-tick9026.jpg`
- The race world matches the Mac/iOS state on `eac6cba`: sky, sun, fog,
  trail and rider-side shards draw, but the terrain is untextured (E51).
  The rider itself isn't clearly visible in these frames.
- Full PNG sets + SHA lists: `~/dev/ssx3-work/N5/L*/` and
  `/Volumes/share/ssx3/N5/`; per-run `scap-sha.txt` in `logs/L*/`.
- The PNG-dump APK (b) wasn't needed: the screencaps verified every phase.

## Race profile (L3, clean APK, 30 s from race tick 7,424)

- Recorded with `simpleperf record -g --app com.ps2x.runner --duration 30`.
- 130,515 samples, 120.2 G cpu-cycles, `perf-race.data` sha256
  `cc976497…d0ec` (mini, share and bytesize agree).
- Symbolized on bytesize against the unstripped clean `.so`
  (`a7bd36bc…dde3`, BuildID `13c128cd…6b37`) via `--symdir` build-ID
  match: **0 unresolved rows**.
- Profiler-perturbed: the guest ran ~6–10 vsyncs/s during recording.

Thread split: **GameThread 96.17 %**, main (`com.ps2x.runner`) 3.62 %
(`clock_gettime` + vdso 1.76 %, `CopyFrameToHostRgba` 0.56 %), AAudio 0.08 %.
DSO: our `.so` 95.00 %, libc 3.27 %, vdso 0.78 %, kernel 0.36 %, Adreno
GLES 0.21 %.

| Bucket (self, rows ≥ 0.05 % = 96.54 % covered; `scripts/buckets.py`) | Race | N4 Select Character (diagnostic) |
|---|---|---|
| VU1 interpreter | **50.30 %** | 91.55 % (incl. ~8–9 % quad soft-float) |
| GS CPU rasterizer / GS memory | **36.15 %** | 0.59 % |
| PLT stubs | 4.35 % | — |
| libc / kernel / vdso | 3.69 % | 2.03 % |
| VIF / DMA / memory / scheduler | 1.04 % | ~0 |
| Guest code (`sub_*`) | **0.43 %** | 0.00 % |
| other | 0.58 % | — |

Inclusive (children) view:
- Guest `sub_00382760` → `PS2Runtime::Store32` → `processPendingTransfers`
  parents **87.2 %**. That's the same VIF1 hotspot N4 found.
- Under it: `processVIF1Data` 80.5 %, `VU1Interpreter::run` 71.4 %, and
  `GifArbiter::drain` → `GSCpuBackend::Submit` 35.9 % (`DrawSprite`
  22.4 %, `SampleTexture` 17.1 %).
- VU1 pipeline/hazard modelling (`commitReadyPipelines` +
  `calculatePairReadyCycle` + `markPairWrites`) is **29.6 %** self.
- E45 worked: no `__addtf3`/`__multf3`/`__extendsftf2` in the binary, and
  `calculateFmacExactResult(unsigned, double&)` is 2.08 %.

Top 25 by self (`reports/race-top25.md`; full reports `reports/race-*.txt`):

| # | Self | Thread | Symbol |
|---|---|---|---|
| 1 | 17.85% | GameThread | `VU1Interpreter::commitReadyPipelines()` |
| 2 | 11.23% | GameThread | `GSCpuBackend::WritePixel()` |
| 3 | 9.40% | GameThread | `VU1Interpreter::calculatePairReadyCycle()` |
| 4 | 7.28% | GameThread | `GSCpuBackend::SampleTexture() lambda` |
| 5 | 5.08% | GameThread | `VU1Interpreter::run()` |
| 6 | 4.58% | GameThread | `GSCpuBackend::SampleTexture()` |
| 7 | 4.35% | GameThread | `@plt` |
| 8 | 2.81% | GameThread | `VU1Interpreter::execUpper()` |
| 9 | 2.42% | GameThread | `VU1Interpreter::normalizeOperand()` |
| 10 | 2.33% | GameThread | `VU1Interpreter::markPairWrites()` |
| 11 | 2.13% | GameThread | `GSCpuBackend::LookupCLUT()` |
| 12 | 2.11% | GameThread | `GSCpuBackend::DrawTriangle()` |
| 13 | 2.08% | GameThread | `VU1Interpreter::calculateFmacExactResult(unsigned, double&)` |
| 14 | 1.57% | GameThread | `GSMem::ReadCT32()` |
| 15 | 1.47% | GameThread | `GSCpuBackend::DrawSprite()` |
| 16 | 1.44% | GameThread | `__memset_aarch64_nt` |
| 17 | 1.42% | GameThread | `VU1Interpreter::execLower()` |
| 18 | 1.36% | GameThread | `VU1Interpreter::normalizeFmacResult()` |
| 19 | 1.30% | GameThread | `VU1Interpreter::calculateFmacProductSticky()` |
| 20 | 1.12% | GameThread | `(anon)::combineTexture()` (GS) |
| 21 | 1.01% | GameThread | `std::function<GSMem read fn>` invoke (GS) |
| 22 | 0.98% | com.ps2x.runner | `clock_gettime` |
| 23 | 0.94% | GameThread | `VU1Interpreter::updateFmacFlags()` |
| 24 | 0.88% | GameThread | `VU1Interpreter::getDecodedInstructionPairForPc()` |
| 25 | 0.78% | com.ps2x.runner | `__kernel_clock_gettime` |

## Tap guard (candidate for fork `ssx3`)

`[N5-local] 6c335e6` on `n5-android`. Full diff:
`logs/tap-guard-6c335e6.diff`, 4 files, +297/−208.

- **`ps2_runtime_macros.h`**
  - The macros now reach the four trace namespaces through aliases:
    `ps2x_tap_mpg`, `ps2x_tap_e41`, `ps2x_tap_e43`, `ps2x_tap_e44`.
  - With `PS2X_ENABLE_DIAG_TAPS=1`, the header includes the trace headers
    and aliases the real namespaces. That's today's behavior.
  - With `=0`, the aliases are stub namespaces:
    - `constexpr` predicates that return false (`*Armed`, `enabled`, `is*`);
    - empty variadic `note*` functions;
    - no-op `detail::ScopedProdSuppress`/`ScopedFastSuppress`.
  - So every `if (tap) note(...)` and its argument setup (`__func__`, value
    extraction) compiles to nothing.
  - Macros can't contain `#if`, which is why the aliases exist. Nothing in
    the macros references the real names any more (script-checked).
  - A header-side `#ifndef … 1` keeps it ON for any TU built outside CMake.
- **`ps2xRuntime/CMakeLists.txt`**
  - `option(PS2X_ENABLE_DIAG_TAPS …)`, default **OFF if `ANDROID`**, ON
    otherwise.
  - A PUBLIC define on `ps2_runtime`, which reaches `ps2_game_objects`
    through its PUBLIC link.
- **`Stubs/GS.cpp`, `Stubs/Pad.cpp`**
  - `+#include "ps2_e44_trace.h"`: both used `ps2_e44_trace` but only got
    it through the macros header.
  - Found by a `-fsyntax-only` pass over all 67 runtime TUs plus 2 guest
    unity TUs with taps OFF, plus 1 guest TU with taps ON
    (`scripts/syntax_check.py`): 70/70 after the fix.
- **Verified in the clean `.so`** (build 3 bars):
  - guest `sub_*` 38,150 symbols, total **110.6 MB**, median **228 B**
    (N4: 110.3 MB / 228 B; taps-in: 354.9 MB / 632 B);
  - `.text` 113.2 MB (N4 112.8, taps-in 357.9);
  - `sub_002127E8` 0xe3bbc (N4 0xdf71c, taps-in 0x3f7218);
  - tap call symbols (`noteFast`, `noteProdSite`, `noteFastWriteSite`,
    `noteReadCtx`) **0**, `ps2x_tap_*` symbols 0;
  - `CMakeCache` `PS2X_ENABLE_DIAG_TAPS:BOOL=OFF`, and 345/345 compile
    commands carry `=0`.
- **Not covered:** host-side taps outside the macros (e.g. `ps2_memory.cpp`,
  `ps2_vif1_interpreter.cpp`, `EeScheduler.cpp`, Stubs) are still compiled
  in, env-off. Their `PS2X_E4x_TRACE` env strings remain in the binary.
  They run per host event, not per guest instruction, and their cost isn't
  measured.
- Desktop suite not run: with the default ON, desktop builds are byte-for-byte
  the same code path. Brief scope was Android.

## Builds

| Build | Tree | Result | APK | Peak memory |
|---|---|---|---|---|
| 1 | `1669d50` | OOM at [173/369] (ninja -j20 default) | — | killed |
| 2 | `1669d50` | PASS, ninja -j6 29 min + Gradle 27 s | `6298a616…9325` (384,931,204 B; taps in) | 9.8 GB RAM + 0.5 GB swap, then governor-held |
| 3 | `6c335e6` | PASS, ninja -j6 7.5 min + Gradle 40 s, governor from start (never triggered) | **`b9737306…79ce`** (134,575,796 B) | **4.0 GB** |

Build 3 pins:
- APK `b9737306…79ce`: build tree ×2, `~/n5/apk`, mini ×2, Odin
  `base.apk` and share all agree.
- Packaged `.so`: stored uncompressed, 134,553,752 B, `8f9bbc72…c555`,
  BuildID `13c128cd…`, matching the unstripped `.so`.
- Strings: `PS2X_PAD_SCRIPT_CLOCK` 1, `PS2X_VSYNC_RATE_LOG` 1,
  `[vsync-rate]` 1, `PS2X_FRAME_DUMP_DIR` 1.
- `calculateFmacExactResult(…double&)` present.
- Scripts: `scripts/build3.sh`, `scripts/mem_governor.sh` (LOW 3 GB /
  HIGH 5 GB).
- Build 2 notes:
  - Its first bars probed N4/N6's stale `282v703p` `.so`; `bars2.sh`
    re-ran them on `321r613w` and the APK member (BuildID `ede29bea…`).
  - `mem_governor.sh` (then LOW 2 GB) paused 3 compiles and resumed 5,
    killing none (`~/n5/logs/build2-governor.txt`).

Most of build 2's memory peak (2.8–2.9 GB per unity TU) came from the taps
themselves: 3× code per function. Without them the full guest recompile
peaks at 4 GB at -j6.

## Recommendations (orchestrator decides)

1. **Ledger:**
   - Add the table above as speed rows: title 0.47×, main menu 0.44×,
     Select Character 0.33×, Select Mode/Event 0.39×, race 0.19–0.26×
     (first 41–47 s, 2 runs), APK `b9737306`.
   - Retire N4's "SC ~0.2/s".
   - The race profile shares (VU1 50 %, GS 36 %, guest 0.4 %) can go in as
     measured on the clean APK under the profiler.
2. **Fold the tap guard into fork `ssx3`** (`logs/tap-guard-6c335e6.diff`).
   It restores N4's code size, cuts full-rebuild memory from ~10 GB to
   4 GB on bytesize, and costs 0–4 % on menus when left in.
3. **Speed levers:** the next ~4–5× needed for 1× in the race sits in two
   host subsystems, not guest code:
   - VU1 interpreter: the pipeline/hazard bookkeeping alone is 29.6 %;
     next steps are a VU1 recomp or a cheaper timing model.
   - GS CPU rasterizer (36 %): the G-lane GPU backend.
4. **Measurement:**
   - A full 60 s race window needs a ~720–780 s boot at today's speed.
     That needs orchestrator OK over 600 s, or a shorter route (I26).
   - Race rates vary between runs with content, so race numbers need
     ≥2 runs (as here) or a fixed RNG seed.

## Part 1 receipt: the denied rebase

One Bash call via `ssh bytesize 'wsl -d Ubuntu -- bash -s'` with
`git branch -f n5-pre-rebase 65c95d9`, `git fetch origin`,
`git rebase --onto eac6cba e57b5f8 n2-android`. Refused whole:

> Permission for this action was denied by the Claude Code auto mode
> classifier. Reason: [Git Destructive].

Nothing ran. The orchestrator ruled that the brief shouldn't have asked for
a rewrite (AGENTS.md forbids it) and approved a new branch instead.

## Step 1: `n5-android` (bytesize, local only, never pushed)

`git fetch origin` gave `origin/ssx3 = eac6cba6677663d25b31d7228d7d08eb3ee1c275`.
`git checkout -b n5-android eac6cba`, then `git cherry-pick -x` one commit at
a time, then `git am -3 ~/n5/e45.patch`. **No conflicts at any step.**
`n2-android` is still `65c95d9`. No ref was deleted, moved or force-updated.

| Source | New | Subject |
|---|---|---|
| `8e7d5ac` | `bb6d82b` | [N2-local] H1 port: PS2X_GAME_CODEGEN_DIR game-objects lib |
| `322e55b` | `aa1abd3` | [N3-local] Android env-file shim + parser test |
| `3da81ad` | `22199fe` | [N3-local] arm64-v8a only |
| `f9d78da` | `d5a940e` | [N4-local] profileable + show-when-locked; PNG via memory-encode + ofstream |
| `ae210c9` | `f64e388` | [N6-local] keyboard + gamepad union on Android |
| `65c95d9` | `842567c` | [N6-local] env-gated `PS2X_PAD_LOG` |
| mini `310b30f` (E45, on no remote; `format-patch` sha256 `ae21c498…0de2`, same on both hosts) | `c6fda05` | "VU1 FMAC exact math in VuWide=double, quad kept behind PS2X_VU_WIDE_QUAD" (`git am` dropped the `[E45]` tag from the subject) |
| new | `1669d50` | [N5-local] env-gated `PS2X_VSYNC_RATE_LOG` line, ported from I25 `31d988d` |

Checks on `1669d50`:
- `ps2_runtime.cpp` has no bare `ExportImage(` calls; both dump sites
  call `writePngBytes` (lines 488/491), so N4's fix survived the
  cherry-pick onto the 110-line-larger file.
- `ps2_vu1.h` uses `VuWide = double` unless `PS2X_VU_WIDE_QUAD` is
  defined at compile time. It isn't.
- The vsync-rate hunk is I25's code copied as-is (+23 lines, including
  `#include <cstdio>`). It prints `[vsync-rate] tick=… rate=…/s` to stderr
  every 5 s on the host loop, and only when `PS2X_VSYNC_RATE_LOG=1`.

## Step 2: codegen

| Check | Mini | bytesize |
|---|---|---|
| Source | `~/dev/ssx3-work/codegen-ssx3` (canonical, E50 regen per I25 §Pins) | `~/n5/codegen-ssx3` |
| Tar (`COPYFILE_DISABLE=1`), 283,675,648 B | `a90af6fd…d0480f` ×2 | `a90af6fd…d0480f` ×2 |
| Files | 9,457 | 9,457 |
| Tree hash (sha256 of sorted per-file sha256 list) | `a2adcb50…e02c` | `a2adcb50…e02c` |
| E50 signature | `FPU_SQRT_S(ctx->f[ft])` with varied ft (f1, f2, f3, f5, f7, f8, f12, f20, f21) | same tree |

The tar also carries `com.apple.provenance` xattr headers. GNU tar ignores
them, and the tree hash is unaffected. Gradle property:
`-Pps2xGameCodegenDir=/home/brad/n5/codegen-ssx3`.

## Build 1/3: FAILED (OOM), kept for the record

Script: `scripts/build1.sh`, the N4 recipe with the new codegen path and
extra bars. Build log: `~/n5/logs/build1-assembleRelease.log` on bytesize,
console copy in `~/dev/ssx3-work/N5/build1-console.txt`.

| Item | Value |
|---|---|
| Start / end | 22:53:35Z / 23:04:53Z (11 min 17 s), EXIT=1, `pgrep -f pcsx2` = 0 at start |
| First failure | log line 751: `FAILED: …/ps2_game_objects.dir/Unity/unity_211_cxx.cxx.o` → `Killed` |
| Kernel | `clang++ invoked oom-killer … Out of memory: Killed process 2211 (clang++) … anon-rss:716524kB` (dmesg t=381 s) |
| Progress | [173/369] ninja steps when stopped, mostly `ps2_game_objects` unity TUs (the full codegen recompiles because the dir changed) |
| Cause | `--max-workers=4` limits Gradle workers, not ninja. Ninja defaults to `nproc` = 20 parallel clang jobs, and the new unity TUs peak at ~0.7 GB each, which overran WSL's 9 GB + 3 GB swap. N4/N6 didn't hit this: their builds were incremental (25 s) |
| Warnings only | `-Warray-bounds` on `ctx->vi[27]` in the VCALLMSR sequences (e.g. `sub_0037DE88`, `sub_0032B6A8`). This is E52's known VCALLMSR defect, which E53 is fixing. Not an error |

The build is incremental: the finished objects are in
`android/app/.cxx/RelWithDebInfo/321r613w/arm64-v8a`.

## Odin power (resolved)

18:53–19:05 EDT: discharging on AC at idle (16 % → 15 %, status 3,
about −0.2 A). Brad reseated the charger; at 23:4xZ it read `status: 2`,
30 %, +2.86 A. The new AGENTS.md rule is in `launch.py`: `am force-stop`
after every run via atexit/SIGTERM, and a battery check (charging,
≥ 20 %) before every launch.

## Gaps

- Race window is **41–47 s**, not the brief's 60 s: the 600 s boot cap
  hit first, and no run over 600 s was approved.
- Race rate spread (11.5 vs 15.5) is attributed to race content, from
  screencaps and the thermal sampler. The cause (RNG seed) isn't tested.
- SF presents come from the 128-frame `--latency` ring per 10 s poll, so
  each is a ~2 s sample, not a full-phase count. L1's presents are
  missing (wrong layer, fixed in `launch.py` for L2+).
- GameThread's core wasn't captured: `ps -T -o psr` printed nothing on
  this ROM.
- Taps-in cost rests on one diagnostic run (L1); race excluded.
- Host-side (non-macro) taps are still compiled in; cost unmeasured.
- Desktop/Mac suite not run with the guard (default ON there, so
  unchanged by construction).
- Unused: PNG-dump APK variant (b), and launch 5.

## Receipts

- In-repo:
  - `scripts/`: build1/2/3, bars2, `mem_governor.sh`, `guard_taps.py`,
    `syntax_check.py`, `launch.py`, `phases.py`, `buckets.py`, `report.sh`,
    `battery_wait.sh`.
  - `logs/`: branch log, the tap-guard and vsync-rate diffs, and per-launch
    `phases.md`, `driver.log`, `ps2x.env`, `scap-sha.txt`,
    `logcat-rates-presses.txt`, plus L4's `thermal.txt`.
  - `reports/`: race self/children/threads/DSO reports and the top-25.
  - `shots/`: 4 JPEGs.
- Mini `~/dev/ssx3-work/N5/` (1.4 GB): both APKs, the clean unstripped
  `.so`, per-launch full PNG screencaps + logcats + SF dumps, and
  `perf-race.data`.
- Share mirror `/Volumes/share/ssx3/N5/` (541 MB): the same, without the
  unstripped `.so`.
- bytesize:
  - `~/n2/PS2Recomp` branch `n5-android` @ `6c335e6` (local only);
  - `~/n5/`: codegen, APKs, unstripped `.so` files, logs, prof;
  - `n5-pre-rebase` was never created.

