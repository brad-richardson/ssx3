# N5 — Odin: current tree, dumps-off, speed through the race

- Date: 2026-09-23. Brief: `local/muse/prompts/N5.md`. Worker: Claude Code
  (Opus pane).
- **STATUS: STOPPED at step 3 (build 1 OOM-killed), with the Odin blocked
  on power as well.**
  - Part 1 stopped at the rebase (denied). The orchestrator then approved
    option 2 (new branch, cherry-picks) and the vsync-rate commit.
  - Steps 1–2 are done.
  - Build 1/3 failed: bytesize's OOM killer took `clang++` (a resource
    failure, not a code error).
  - Separately, the Odin **isn't charging on AC**. The brief's
    precondition is at least 20 % and charging.
- Budget used: 1/3 builds (failed), 0/5 launches, no Odin lease taken,
  ~1 h 15 min.

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

## Step 3: build 1/3, FAILED (OOM)

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

## Step 4 blocker: the Odin isn't charging

| Time (EDT) | Level | Status | current_now (µA) | Screen |
|---|---|---|---|---|
| 18:53:40 | 16 % | 3 (discharging) | −208,746 | awake, app not running |
| 18:54:19 | 16 % | 3 | −214,850 | same |
| 19:05:27 | 15 % | 3 | −198,980 | same |

- `AC powered: true`, `Max charging current: 3000000`, `Charging state: 0`.
- `percent_80_charge_limit=0`, `is_charging_separation=0`: no charge
  limit or bypass is set.
- So the wall charger or cable isn't delivering power. The device loses
  about 1 % per 10 min at idle and will drain faster under load.
- The harness refuses below 10 %; the brief's precondition is at least
  20 % and charging.
- **Needs Brad hands-on: reseat or swap the charger/cable, confirm
  `status: 2`, then wait for at least 20 %.**
- Lease untouched (`LEASE_FREE E45 done`). The device keyguard reads
  `showing=false`.

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

## Recommended next action (orchestrator decides)

1. **Build 2/3 with bounded parallelism.** Run ninja on the existing tree
   with a job cap, then let Gradle package it. The ~150 finished objects
   are reused:
   ```
   ninja -C ~/n2/PS2Recomp/android/app/.cxx/RelWithDebInfo/321r613w/arm64-v8a -j6 ps2EntryRunner
   ./gradlew assembleRelease <same -P flags> --max-workers=4
   ```
   At -j6 × ~0.7 GB peak it stays within 9 GB. The alternative is
   `-j8` with a WSL memory raise, which is Brad's machine setting and
   not proposed here. The time estimate is a guess, not measured:
   perhaps 20–30 min for the remaining ~200 steps.
2. The Odin launches wait for the charger fix (above). Once it charges and
   shows at least 20 %, run launch 1: dumps off, race window, simpleperf
   after tick 11,100 if the wall allows. Then launches 2 and 3 as needed
   (PNG dumps for verification if (a)'s screencaps are unclear).

## Gaps

- No APK, no SHAs, no device numbers yet.
- The OOM diagnosis rests on dmesg plus the ninja default. I didn't check
  whether `-j6` itself fits; the 0.7 GB peak comes from one killed TU.
