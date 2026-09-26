# AB1 — Android APK builds on bradflix (Docker, ccache, 3 at a time) (muse, 3 h)

## Goal
Every Odin test needs an APK, and today only bytesize's WSL (12 GB RAM, one heavy job at a time via `local/tooling/bytesize_lock.sh`, 9–25 min per build) can build one — the queue is the bottleneck of the 90 % push. bradflix (20 cores, 62 GB, native Linux + Docker; Brad-approved build host, `AGENTS.md` Hosts) can run several at once and already has a shared ccache for the Linux runner. Make bradflix the primary Android build host.

## Facts
- Current recipe: VR3's/VR4's Android build scripts (`local/research/VR3/build-android-vr3.sh` lineage, `local/research/VR4/` fold script): `git archive` of a fork SHA, canonical codegen (`register_functions.cpp` `8ea8ed43…`), VU1 images `vu1gen-ssx3` (set `d28e3fc6…`), VU0 `vu0gen-ssx3` (`2652966b…`), paraLLEl fork `ssx3` (`3d72467`) + Granite with nested submodules, jniLibs (Turnip `libvulkan_freedreno.so` + others from bytesize `/home/brad/f2`/`f5`), gradle `assembleRelease` with `-Pps2xVu1RecompDir -Pps2xVu0RecompDir`, NDK `28.2.13676358`, CMake 3.22.1, AGP 8.6.1 / Gradle 8.9, `--max-workers=2` (raise on bradflix).
- bradflix tooling: `local/tooling/build/bradflix_build.sh` (HS2: per-build `git archive` export, content-addressed shared inputs under `~/dev/ssx3-work/HS1/`, one setup lock, Docker image `ssx3-hs1`, ccache at `~/dev/ssx3-work/ccache`). Don't break it; add alongside.
- Generated code and game data never leave our machines; the Docker image contains only toolchains.

## Deliverable
1. `local/tooling/build/Dockerfile.android` (Ubuntu 24.04 + JDK 17 + Android SDK cmdline-tools with platform/build-tools the gradle files need + NDK `28.2.13676358` + CMake 3.22.1 + ccache), built on bradflix as `ssx3-android`.
2. `local/tooling/build/bradflix_apk.sh <fork-sha> <name> [--pgs PIN] [--vu1 DIR] [--vu0 DIR] [--jnilibs DIR] [--gradle-prop K=V …]`: reuses HS2's export + content-addressed inputs (add a `jnilibs-<sha12>` input, synced from the mini's copy or bytesize's `/home/brad/f5/jniLibs` with SHA checks), runs gradle in Docker with `CMAKE_{C,CXX}_COMPILER_LAUNCHER=ccache` (via gradle cmake arguments or an init script), prints wall time + ccache stats, and leaves the APK at `~/dev/ssx3-work/HS1/<name>/app-release.apk` (+ pull to the mini with two SHA reads). Concurrency: up to 3 builds at once (a counting lock like `p_lane_lease.py --host bradflix`, or three slots); cap each at a sensible `-j` so 3 fit in 62 GB.
3. Acceptance: (a) build fork `ssx3` `b97b241` with the canonical inputs; compare its `libps2EntryRunner.so` symbols/size and the APK's non-native contents with bytesize's VR4 fold APK `47b3ef38…` (same source + inputs; list any differences and their cause); (b) a warm rebuild (ccache hits, wall time); (c) two builds started 10 s apart both succeed; (d) **one Odin smoke run** of the bradflix APK on the play settings (lease via `odin_lease.sh`, restore with `odin_restore_play.sh`): reaches the race, 0 FATAL, `[mtvu] violations=0`, a screencap viewed. FS2/AP1/CP2 have Odin priority; wait for the lease.
4. Proposed runbook/AGENTS text in the report (the orchestrator edits docs).

## Rules
Docker only on bradflix; don't touch media containers (`docker ps` first); stay under `~/dev/ssx3-work/`. Never push. Text only in git. First failure: stop, save the error, hand back.

## Deliverable
`local/research/AB1/REPORT.md` + the two tooling files; `[AB1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
