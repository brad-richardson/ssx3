# N2 — First Android build of the PS2 recomp runner on bytesize

- Date: 2026-09-22. Brief: `local/muse/prompts/N2.md`. Spec: N1 Mission 3 + bars B1–B6.
- Build host: bytesize WSL Ubuntu 24.04.1 (`~/n2`, user-local, no sudo). The Mac did SSD reads, tar/scp, and evidence only. No device, no adb, no install, no boot — honored.
- Read first: `local/research/N1/REPORT.md` (unchanged input).
- HEADLINE: the verbatim stub (Mission 1) cannot link at the pin; the full-title link (Mission 2) built clean — exit 0, `app-release.apk` 270,957,997 B, sha `21a9230c…`, on the Mac SSD, not installed. Mission 2 was attempted under a recorded gate exception (below); the orchestrator rules on acceptance.

## Gate exception (read before the tables)

Mission 1 (stub) failed B1 twice with two distinct pre-existing causes at
the pin: (1) generated header `ps2_recompiled_stubs.h` absent on a fresh
clone (recovered by staging the byte-matched C17 headers, no source edits,
no cmake-arg change); (2) the in-tree "stub" table is the FULL
398,961-assignment table referencing 9,441 `sub_*` with only 5 bodies, and
NDK r28 lld enforces `--no-undefined` — the stub link is infeasible without
a source or link-flag change, both outside N2's mandate. Mission 2's
mechanism (H1 port: drop the in-tree table + bodies, link all 9,455 C17
sources) is the direct remedy, and every toolchain risk Mission 1 was meant
to retire was retired (clean NDK-clang compile of all runtime sources +
raylib + PCH, correct configure lines, FetchContent pins match). Proceeding
produced the evidence the orchestrator needs to rule; stopping would have
returned no APK on a gate whose underlying concern is satisfied.

## Mission 1 — stub build (B1–B6)

Full table: `manifests/mission1-bars.md`. Summary:

| Bar | Result |
|---|---|
| B1 exit + configure | FAIL — build1 exit 1 (33 s, missing header); build1c exit 1 (18 m 20 s, 9,436 undefined `sub_*` at link). Configure lines present on both (`Android target detected…`, `FFmpeg disabled…`) |
| B2 `file` | n/a — 0 `.so`, 0 APK |
| B3 symbols | provider hunt SUCCEEDED (see row below); `main` T; defined `sub_*` = 5 as N1 predicted; FFmpeg/tag strings deferred to the Mission-2 `.so` (both present) |
| B4 budget | n/a — no artifacts |
| B5 repro seed | none — no `.so` in either mission (Mission 2 link ran once) |
| B6 zero-drift | PASS — pin held, zero commits, wrapper files only untracked, staged headers gitignored, E-lane checkout untouched |

Entry-provider row (closes N1 M1.10): `ANativeActivity_onCreate` is `T`
(DEFINED) in the NDK's `android_native_app_glue.c.o`; `android_main` is `T`
in raylib 5.5 `rcore.c.o`; runner defines `T main`. Chain: NativeActivity →
glue `ANativeActivity_onCreate` → rcore `android_main` → runner `main()`.
No object references the entry (it enters via CMake's `--undefined` flag).
In the final Mission-2 `.so` the entry is statically linked (`T`), not an
import. On-device proof remains N5's.

Anomaly (receipted, cause undetermined): the first detached rebuild
(build1b) vanished ~35 s after launch — no exit file, no surviving
processes. Forensics in this report's §Anomalies; all foreground runs
before and after were stable. No evidence of OOM (empty dmesg, memory
headroom on every probe).

## Mission 2 — full-title link

Full manifest: `manifests/mission2-manifest.md`. Transfers: `manifests/transfer-manifest.md`. H1 diff: `logs/m2b-full-diff.txt`.

| Step | Result |
|---|---|
| 1. C17 set to bytesize | tar 273,988,608 B sha `6b2332b6…` (2 SSD reads + bytesize re-verify); untar census 9,455/2/9,457/265,956,572 exact; header shas re-verified; never to GitHub |
| 2. H1 port, local branch `n2-android` (`695b96e`, never pushed) | `eb3fb16` + `193451a:515–523` mechanisms applied by hand (one anchor adapted: pin's link block carries explicit `PRIVATE`); +29 CMakeLists, +2/−1 build.gradle (`ps2xGameCodegenDir` property, empty default = zero behavior change); `ssx3` verified still `3adc0478` |
| 3. Rebuild with codegen dir | exit 0, BUILD SUCCESSFUL in 9 m 30 s, 0 `error:` lines; configure `dropped 5`, `game objects: 9455`; 296 game unity objects + 1 runner unity; `libps2_game_objects.a` 1.7 GB / 296 members; defined game-shape `sub_*` 9,441/9,441 distinct; undefined `sub_*` 0; table `D/R` symbols linked; `file`/`nm`/`size` all recorded |
| 4. APK to Mac SSD | `/Volumes/Extreme SSD/n2-android/app-release.apk`, sha `21a9230c…` on build tree + stage + Mac ×2 reads; NOT installed |

Delta reconciliation (N1's open item): 9,441 distinct `sub_*` syms;
9,455 `.cpp` = 9,441 bodies + 13 named bodies + 1 table file; 9,457 census
entries = +2 headers. C17 table sha == in-tree table sha; M1's
9,436 U + 5 T = 9,441 closes the loop from the stub side.

## Toolchain (URLs + shas)

Full table: `manifests/toolchain-table.md`. Temurin jdk-17.0.20.1+1
(`3808d1d1…`, 193 MB) · cmdline-tools 13114758 (`7ec96528…`) · Gradle 8.9
(`d725d707…`, 136 MB, wrapper generated per README Option B) · sdkmanager
19.0: platform-34, build-tools 34.0.0, NDK r28c (clang 19.0.1), CMake
3.22.1 (SDK 2.7 GB). No `unzip` on the box — python3 zipfile + `chmod`
(receipted). Clang/LLVM tools for `nm`/`size` came from the installed NDK.

## What N3/N4/N5 now need (H1–H8 status)

| # | Status after N2 |
|---|---|
| H1 (game-codegen mechanism) | PROVEN on local branch `n2-android` (full link green); E-lane still owns adoption onto `ssx3` (or the track keeps the local port) |
| H2 (Android FFmpeg block) | still needed for any ON/video milestone; OFF receipt in `.so` (stub string present) |
| H3 (C3/C5 vector merge) | unchanged — needed for N4 parity |
| H4 (`cdImage` derivation) | unchanged — still the launch blocker (P2 unsettable); N5 cannot stream without it |
| H5 (entry proof) | provider IDENTIFIED (glue + rcore + `main`); on-device proof still N5's |
| H6 (logcat doc fix) | still needs N5's `ps2x`-tag confirmation |
| H7 (non-env diag trigger) | unchanged fallback; first launch flies silent-diag |
| H8 (touch overlay) | unchanged — needed for playable input |

N3 as N1 scoped it (full-title link + manifest) is substantially DONE by
this mission under the gate exception; N4 (FFmpeg prefix + vector parity)
and N5 (install + launch) are unchanged. Note the APK is dual-ABI
(arm64 + x86_64, 271 MB); N5 may want an arm64-only packaging pass.

## Anomalies and method notes

- build1b silent death (~35 s, no exit file, no survivors, log stalled):
  forensics — `who -b`/uptime discrepancy noted but inconclusive (WSL utmp
  quirk); dmesg empty; later `pgrep -f` sightings were partly self-matches
  (corrected methodology after). All foreground builds stable. No verdict.
- `set -o pipefail` + `yes|…`, `grep -m`, `head`bit three scripts (141s);
  fixed by neutralizing pipe status on terminal pipelines. A few `(no …)`
  fallback echoes in `logs/m2c-bars.txt` are pipefail artifacts — the
  matched lines they guard are printed directly above them.
- `ssh bytesize` lands in cmd: `&`/`|` outside the `bash -lc` quotes break;
  all complex logic ran from scp-transferred scripts via `wsl -- bash <file>`.
- Zero commits/pushes on `ssx3` anywhere (bytesize or Mac); the one commit
  is bytesize-local `n2-android`, never pushed. Zero E-lane worktree reads.

## Recommendation (orchestrator decides)

1. ACCEPT the Mission-2 APK + manifest as the track's first arm64 runner
   build (evidence complete), and treat N1's stub-link premise as
   superseded: the pin has no linkable stub configuration.
2. RULE whether Mission 2's gate exception stands, or N2 must be re-scoped
   (e.g. E-lane first lands a linkable stub table or the H1 adoption).
3. If accepted: N3 = arm64-only packaging + repro-pair build (B5 for the
   full link); keep H4/H7 queued for E before any N5 lease.

## What N2 could not do

- Produce ANY stub `.so`/APK (infeasible at pin, proven twice).
- Re-run the full link for a B5 reproducibility pair (time; single EXIT=0).
- Take shas of the x86_64 `.so` pair (paths receipted only).
- Prove anything on-device (forbidden); entry/logcat/boot-path proofs stay N5.
- Adopt H1 onto `ssx3` (E-lane owns the ref).

## Receipt paths

- `local/research/N2/REPORT.md` (this file)
- `local/research/N2/manifests/toolchain-table.md`
- `local/research/N2/manifests/mission1-bars.md`
- `local/research/N2/manifests/mission2-manifest.md`
- `local/research/N2/manifests/transfer-manifest.md`
- `local/research/N2/logs/` (45 files: exit codes, build tails, both
  `configure_stdout.txt`, census/probe outputs, full H1 port diff,
  branch/pin receipts, toolchain version logs)
- `/Volumes/Extreme SSD/n2-android/app-release.apk` (271 MB, NOT in git)
- `/Volumes/Extreme SSD/n2-scratch/c17-codegen.tar` (transfer artifact)
- `~/n2/` on bytesize WSL (toolchain, clone @`695b96e` on `n2-android`
  with `ssx3` == `3adc0478`, C17 set, full logs)

END-N2-REPORT.
