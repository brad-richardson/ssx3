# N5 — Odin: current tree, dumps-off, speed through the race

- Date: 2026-09-23. Brief: `local/muse/prompts/N5.md`. Worker: Claude Code
  (Opus pane).
- **STATUS: build 2/3 PASS (APK `6298a616…`). HELD before launches on one
  question: `eac6cba` compiles the E41/E43/E44 watch taps into every guest
  memory-write macro, with no compile-time switch.** They're off by
  default but always compiled in, and guest `.text` is 3.2× N4's.
  AGENTS.md says speed numbers come only from builds with watch sets
  compiled out, so this APK's numbers would be diagnostic-labelled.
  Orchestrator decides (see "Decision needed" below).
- Odin: charger reseated by Brad; now `status: 2`, 30 %, +2.86 A. Lease
  untouched.
- Budget used: 2/3 builds (1 OOM, 1 PASS), 0/5 launches, ~2 h.

## Build 2/3 (PASS): resumed build 1's tree with a ninja job cap

Script: `scripts/build2.sh`. It runs `ninja -C …/.cxx/RelWithDebInfo/321r613w/arm64-v8a -j6
ps2EntryRunner` on build 1's tree, then `gradlew assembleRelease` (same
`-P` flags) to package it. Gradle rebuilt 0 C++ objects.
- Ninja: 23:07:24Z → 23:36:35Z (29 min 11 s), EXIT=0. Gradle packaging
  +27 s, EXIT=0.
- **Peak memory missed the ~7 GB target:** 9,785 MB RAM + 538 MB swap
  at 23:23:35 (`~/n5/logs/build2-mem.txt`, 5 s samples).
  - `-j6` isn't enough of a cap: the big unity TUs reach 2.8–2.9 GB
    each. `sub_0037E120`, `sub_001E9A30` and `sub_002127E8` are
    2.5–4.2 MB functions.
  - From 23:23:45 `scripts/mem_governor.sh` held it: SIGSTOP on the
    youngest `clang++` when MemAvailable < 2 GB, SIGCONT above 4 GB.
    It paused 3 compiles and resumed 5 (`~/n5/logs/build2-governor.txt`).
    Nothing was killed, and no second OOM happened.
  - For a future full rebuild: `-j3`, or the governor from the start.

| Item | Value |
|---|---|
| APK | `6298a61620e747b211d3326606a147f50d3e9ee05b222e0c64a63634c6629325`, 384,931,204 B. The build tree, `~/n5/apk` and the mini (`~/dev/ssx3-work/N5/apk/`, 2 reads) all agree |
| Packaged `.so` | stored uncompressed, 384,909,160 B, stripped, `0b72e112…f4bad`, BuildID `ede29bea…2ad2b` |
| Unstripped `.so` (symbols) | `636d8b25…4377f`, 2,501,059,848 B, same BuildID, `321r613w` obj dir, copy in `~/n5/apk/` on bytesize (not yet on the mini) |
| Guest functions | 38,164 defined symbols matching `sub_XXXXXXXX` (mangled `_Z21sub_…`), 0 undefined. N4's .so: 38,150 by the same count |
| E45 in binary | `VU1Interpreter::calculateFmacExactResult(unsigned, double&)` (`…EjRd`); `__addtf3`/`__multf3`/`__extendsftf2` symbols: 0 |
| Strings (packaged .so) | `PS2X_PAD_SCRIPT_CLOCK` 1, `PS2X_VSYNC_RATE_LOG` 1, `[vsync-rate]` 1, `PS2X_FRAME_DUMP_DIR` 1, `PS2X_PAD_LOG` 1, `PS2X_SKIP_MOVIE` 1, `ps2x.env` 4, `SLUS_207.72` 3 |
| Bars fix | `build2.sh`'s bars probed a stale `.so`: `ls …/*/obj/…` picked N4/N6's `282v703p` (11:59). `scripts/bars2.sh` re-ran them on `321r613w` and the APK member (`~/dev/ssx3-work/N5/bars2.txt`) |

## Finding: the diagnostic taps are compiled into every guest store

| | N4/N6 `.so` (`e57b5f8` base) | N5 `.so` (`eac6cba` base) |
|---|---|---|
| `.text` | 112,843,420 B | **357,946,604 B (3.17×)** |
| guest `sub_*` total / median size | 110.3 MB / 228 B | **354.9 MB / 632 B** |
| largest guest fn (`sub_002127E8`) | 0xdf71c (0.9 MB) | 0x3f7218 (4.2 MB) |
| `.debug_info` | 198 MB | 828 MB |

Cause (`git diff e57b5f8 eac6cba -- ps2xRuntime/include/ps2_runtime_macros.h`):
- The WRITE/fast-write macros that every generated function expands now
  include `ps2_mpg_src_trace.h`, `ps2_e41_trace.h`, `ps2_e43_trace.h` and
  `ps2_e44_trace.h`.
- Each store carries three runtime-checked taps: `ps2_e41_trace::plantArmed()`,
  `ps2_e43_trace::enabled()`, and `ps2_e44_trace::enabled()` →
  `noteFast(…, __func__)`.
- `e44::enabled()` does `detail::ensureInit()` + an atomic load per call.
- The header has 208 tap references and **no `#if` guard**: only the env
  turns them off, never the compiler.
- Commits: E40 (`9b82d35`…`9840542`), E41 `7d7bbc6`, E42 `25cde0f`,
  E43 `e4083c1`, E44 `571579e`/`e52b6bf`.
- Macs and iOS builds from `eac6cba` carry the same.

Not measured: the actual runtime cost. N4 had guest `sub_*` at 0.39 % /
0.00 % self on title/SC, so the cost could be small in samples. But 3×
guest i-cache footprint plus ~3 branches and calls per store is exactly
what the "watch sets compiled out" rule is for.

## Decision needed (orchestrator)

Options:
- **A.** Measure with APK `6298a616…` as is, and label every number
  "watch taps compiled in (env-off)". Diagnostic under the rule, so not
  ledger speed.
- **B.** Build 3/3: an `[N5-local]` commit wrapping the tap blocks in
  `ps2_runtime_macros.h` in `#if PS2X_ENABLE_DIAG_TAPS` (default 0 on
  Android), then a full guest recompile. That's ~30 min at `-j3` or with
  the governor. The E lane owns the file, but the change stays on
  `n5-android` and never goes upstream.
- **C (recommended).** Do both in parallel, since they use different
  machines:
  - Build 3 (B) runs on bytesize.
  - Meanwhile launch 1 on the Odin uses the current APK as a
    **route + profile run**: E33 route, screencaps at SC and in the race,
    simpleperf in the race. Its top-25 then measures the tap cost directly
    (`ps2_e4x_trace::*`/`ensureInit` rows).
  - Launches 2–3 on the clean APK give the ledger speed numbers
    (dumps-off), with the PNG-dump env only if screencaps are ambiguous.
  - That's within ≤3 builds and ≤5 launches.

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

## What is ready

- `scripts/launch.py` (not yet run) does the following:
  - uses the E33 vsync-clock route, because `local/research/I26/ROUTES.md`
    doesn't exist yet;
  - sets `PS2X_VSYNC_RATE_LOG=1` and leaves dumps off unless `--dumps`;
  - checks preconditions: the lease is free or ours, keyguard
    `showing=false`, battery ≥ 20 % and status 2;
  - sends BACK after `am start`;
  - polls `dumpsys SurfaceFlinger --latency` every 10 s;
  - takes screencaps at ticks 1300/1800/2600 (SC) and 7500/9000/10800
    (race), plus every 30 s;
  - stops at tick 11,100 (≈60 s of racing after the i=11 anchor at
    tick 7,344) or 600 s;
  - can run `simpleperf record -g --app` after the race window in the same
    launch.
- One APK serves both (a) and (b): `dumpPresentationFrame` returns on its
  first line when `PS2X_FRAME_DUMP_DIR` is unset (a cached `getenv`; no
  hash or encode). Runtime and aggressive logs default OFF
  (`ps2xRuntime/CMakeLists.txt:15-16`), and gradle doesn't set them.

## Gaps

- No device numbers yet (0/5 launches).
- The tap cost is inferred from code size and the macro text; runtime
  cost isn't measured.
- The unstripped `.so` (2.5 GB) is still on bytesize only; it gets copied
  to the mini when a profile needs symbolizing.
