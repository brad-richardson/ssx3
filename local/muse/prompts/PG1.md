# PG1 — Per-platform build tuning: PGO, code layout, CPU target (muse, 5 h)

## Goal
Brad (09-26) approved compiler-side speed work. Behaviour doesn't change (same source, same semantics), so it
stacks with every other lane. The recompiled game is ~9,500 generated files and the unit thread runs large generated
VU1 blocks (CP1 Table 3), so instruction-cache/branch layout plausibly matters. Measure three levers, Mac first
(cheap), then the Odin.

## Levers
- **L1 CPU target.** Android today: `-O3` (BA1) with a plain `armv8-a+fp+simd` `-march` that overrides the root
  CMake's crypto/crc one (`docs/todo.md` "Android -march quirk", BA1 §1). Try `-mcpu=oryon-1` (Snapdragon 8 Elite;
  check the NDK r29 clang accepts it — else the closest supported) for the runner + generated code. Mac: `-mcpu=native`
  is not allowed for shipped builds; test `-mcpu=apple-m4` or whatever matches the mini, labelled Mac-only.
- **L2 PGO.** Instrumented build (`-fprofile-generate`) → one I26-FAST race to t4500 → `llvm-profdata merge` →
  `-fprofile-use` build. On Android the profile file must land somewhere writable (app files dir; flush it at the run's
  stop — find the cleanest way and say which). Same clang version for generate and use.
- **L3 Layout.** With the profile: `-ffunction-sections` + the linker's profile-guided ordering (lld
  `--symbol-ordering-file` or `-fprofile-use` + machine function splitting `-fsplit-machine-functions`). BOLT only if
  the first two are cheap and it installs cleanly; otherwise note it as a gap.

## Correct-behaviour model / observables
Same source → identical guest behaviour. Mac: `local/tooling/boot/baseline.py` compare = IDENTICAL for every tuned
build. Android: `jobs=55501 violations=0` at t4500 and `diff_px=0` at t1100/t3000 (FS2/F8 `--compare-ticks`).
Speed: Mac race vsyncs/s with all four mini slots held (speed rule); Odin screening pairs (knob-free, since these are
build variants: A = F8's play APK, B = tuned APK), then **final** ABBA only for the best variant.

## Steps
1. Mac (`local/tooling/build/mac_build.sh`, ccache): baseline, L1, L2, L2+L3 builds; det IDENTICAL each; speed holds.
   Report each lever's gain. If nothing beats noise on the Mac, still do the Android L1 + L2 (different CPU/compiler).
2. Android (bytesize under `local/tooling/bytesize_lock.sh run PG1 -- …`, or bradflix if AB1 has landed its route —
   check `local/research/AB1/REPORT.md`): from F8's source pin (fork `ssx3` `1425844` or newer, paraLLEl `3d72467`,
   patched Turnip `a315b74a…`): L1 build; instrumented build + one Odin profile run; L1+L2(+L3) build.
3. Odin, after F8/CP2/TN1 have released it (lease tool serializes): screening pairs, then final ABBA for the best.

## Rules / budgets
Build-system changes only (CMake/gradle flags, a profile file) on a local fork branch `pg1`; no source edits, no push.
≤ 6 Mac builds, ≤ 4 Android builds, ≤ 10 Odin launches (every install/launch/force-stop under `odin_lease.sh`,
keyguard + AC + ≥ 20 % before each, `odin_restore_play.sh PG1` after each, fan left alone), Mac speed holds per
AGENTS. Profiles are binary artefacts: keep them in `~/dev/ssx3-work/PG1/`, never commit. 5 h. First failure: stop.

## Deliverable
`local/research/PG1/REPORT.md`: per-lever table (Mac and Odin, mode labels, det results), exact flags, how the profile
is collected, build-time cost, pins/SHAs, gaps, recommended default per platform. Commit `[PG1] …` with `git add -f`,
trailer `Orchestrated-By: Muse Code`, no push.
