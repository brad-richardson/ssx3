# VR4 — make VU1 blocks cheaper on the MTVU unit thread (Opus, ≤ 6 h)

## Goal
With MTVU, the unit thread gates the Odin frame (CP1: 30.1 ms/frame running), and its top self symbols are VU1 generated **blocks** (`B2a10` 2.2 ms, `B0628` 1.5 ms, `B0a58` 0.9 ms), then `commitReadyPipelines` 1.3 ms and `processVIF1DataImpl` 0.9 ms (`local/research/CP1/REPORT.md` Table 3). VR2's blocks v1 (`local/research/VR2/REPORT.md` Parts 2B–2D) keep VF/VI in the VU object and run the pair path's own `issuePair` per pair; RV4 §2 (`docs/research/review-2026-09-26-astra-perf.md`) sketches the next step: register residency in locals across a block (and across a self-loop), loads of live-ins, stores of live-outs at exits, with every pending-effect/budget rule kept. Build that, exact, and measure on the Mac and the Odin.

## Facts
- Fork `ssx3` tip (`5d5c382`+; blocks behind `PS2X_VU1_BLOCKS`, on in Brad's play env), canonical VU1 images `~/dev/ssx3-work/vu1gen-ssx3`. VR2's differential test (every budget cut, cut/resume/fresh, pipes fixture with EFU/WAITP/MFP/DIV/I-bit/JR/XGKICK) and coverage/guard-miss counters are the exactness net.
- Start by reading the assembly of the three hot blocks on arm64 (Odin build) and on the Mac: where the loads/stores go (VF lanes, ready tables, flags, cycle counters), what the compiler already keeps in registers, what spills. Decide the design from that, not from the sketch alone.
- Exactness bar unchanged: suite, differential 0 mismatches, det IDENTICAL on bradflix (`bradflix_build.sh`, now concurrency-safe) incl. 512 KB, VU1 100 % generated. New knob or new block version behind the existing knob — say which.
- Speed: Mac ABBA (exclusive, quiet host) and one Odin pair on the play settings (MTVU + blocks; `odin_lease.sh`, `odin_restore_play.sh`; FS2 also uses the Odin: coordinate through the lease).

## Stages
1. Assembly read + design (commit before code). 2. Implementation behind a knob + exactness gates + Mac ABBA. 3. One Android build + Odin pair. Stop and hand back. ≤ 10 builds. Never push. Text only in git; generated code never in git.

## Deliverable
`local/research/VR4/REPORT.md` + `[VR4]` commits (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
