# VR3 — static recompile of VU0 microprograms (Opus, ≤ 6 h, staged)

## Goal
VU0 microprograms still run in the interpreter. N12 (`local/research/N12/REPORT.md` gate): the `executeVU0Microprogram` subtree is ~7 % of Odin race samples ≈ 5.5 ms of the 68 ms frame (called from guest `sub_0022ADD8`); on the Mac `execUpper` (VU0 path) is 3–4 % (VR2 profiles). RV4 §1 rank 4 sizes it at 2–4 model-ms and flags the entry costs (reset, context copy in/out, 4096-cycle budget) as possibly dominant. Recompile VU0 microprograms with VR1's machinery, **exact** (det-hash identical; differential test generated-vs-interpreter for VU0), and measure.

## Facts
- VR1/VB1/VR2 (`local/research/{VR1,VB1,VR2}/REPORT.md`): VU1 images are dumped from a boot (`PS2X_VU1_RECOMP_DUMP`), keyed by a code hash, compiled into the runner (`PS2X_VU1_RECOMP_DIR`), pair functions chained by musttail, blocks behind `PS2X_VU1_BLOCKS`; the generated lookup rejects VU0 and non-16 KiB images (`ps2xRuntime/src/lib/vu/ps2_vu1_recomp.cpp:88-97`). VR2's differential test (`ps2_vu1_tests.cpp`) compares generated vs the queued interpreter at every budget cut.
- VU0 entry: `ps2xRuntime/src/lib/ps2_runtime.cpp:~2869-2918` (`executeVU0Microprogram`: reset, copy EE-side context in/out, 4 KiB code/data, 4096-cycle budget). VU0 has no XGKICK path (gated off, `ps2_vu1_core.cpp:785`). VU0-specific rules: 4 KiB code/data masks, VU0↔EE register sharing (COP2 macro-mode registers are the same VF/VI file), `VCALLMS`/`VCALLMSR` start addresses, CMSAR0.
- **Measure first:** before generating code, profile what the VU0 path spends on reset/copies vs execution (Mac `sample`/`xctrace` on the race window). If entry overhead dominates, fix that first (exact) and report; recompiling may be secondary.
- Fork `ssx3` tip `d585e5c` (canonical VU1 images `~/dev/ssx3-work/vu1gen-ssx3`). Build `local/tooling/build/mac_build.sh`; det boots on bradflix (`bradflix_build.sh`, `ssx3_boot.py --host bradflix`; HS2 may be changing the build script — if it misbehaves, use a private `git archive` copy as VR2 did); speed on the mini (exclusive ≤ 5 min when quiet; MT1 also takes holds).

## Stages
1. Profile + design (commit): entry-cost split, VU0 program census on the race route (count, sizes, hashes, call frequency), what VR1's emitter needs for VU0 (masks, register sharing with COP2, entry/exit), plan for exactness tests.
2. Entry-overhead fixes if they dominate (exact; det IDENTICAL; ABBA).
3. VU0 images: dump, emit, link behind `PS2X_VU0_RECOMP` (default off); differential test VU0 generated vs interpreter at every budget cut; det IDENTICAL on and off (bradflix, +512 KB); Mac ABBA. Stop before any device.

## Rules
Worktree `~/dev/ssx3-work/VR3/PS2Recomp`, branch `vr3` from fork `ssx3` tip; never push; runner-dir check empty; suite green. Generated code never in git; VU0 images in `~/dev/ssx3-work/vu0gen-vr3`. ≤ 10 builds. Text only in git. First unexpected failure: save the error and hand back.

## Deliverable
`local/research/VR3/REPORT.md` + `[VR3]` commits (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
