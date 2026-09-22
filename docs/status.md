# Status board (compact, authoritative — orchestrator updates each poll)

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on Odin.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
Updated 2026-09-22 evening.

| Lane | State | Pinned rev | Next action | Blocker / lease |
| --- | --- | --- | --- | --- |
| E (PS2 runtime) | **E29 PASS: title screen reached** (bypass flag on). E31 running (title → menu → race); E30 running (MPEG fix design, read-only) | fork `3adc0478`; bypass `e29-movie-bypass` @ `e5ce086d` (local) | Gate E31 → next blocker or race; E32 apply+boot E30's fix | P-lane lease + fork (E31) |
| G (GS composite) | G39 PASS (fixes HOLD; carried diffs). G40 running | clone `3a66c19` + G26/G28 | Gate G40 → fix or next wall | Odin (G40) |
| N (Android) | N1 PASS (scaffold audit). N2 running on bytesize | fork `3adc0478` (clean clone) | Gate N2 → N4 FFmpeg / N5 launch | bytesize (N2) |
| T (PCSX2 reference) | T46 PASS | bytesize WSL | T47 after N2 releases bytesize | shares bytesize with N |
| V (storage) | V1 PASS (audit ×2, manifest, smoke, cutover list) | — | Mac mini cutover | **Brad: mini not set up** |
| I (iOS) | Parked | `i23-ffmpeg-ios` @ `aa73dbc` | Re-probe after E30 | needs E change |
| GameCube | Reserve (`docs/reserve.md`) | — | none | — |

Gate reads 2026-09-22 (orchestrator): **E29 PASS**. `PS2X_SKIP_MOVIE=1` reaches the rendered SSX 3 title screen ("Press START button"; frame `2ab49bac…` checked by eye). Flag off reproduces e28a 20/20; suite 458/458 with the flag off, 453/458 on (the 5 MPEG tests the bypass suspends). Three movies skipped, `offered=15056 consumed=15056 packets=0`. C3 missed as written (wrong proxy). A2 amendment accepted: the SSD byte caps are logical bytes, because ExFAT allocates 1 MiB per file. **G39 PASS**. Both fixes hold on
current HEAD, 48/48 no-perturbation classes equal. Adoption decision:
carried diffs now, in-clone commit after the storage cutover. **V1 PASS**.
7610/7610 files stable across two passes, restore manifest written, smoke
restore passed. **N1 PASS**. The Android scaffold exists; the logcat pipe is
in code but never built; the entry provider comes from raylib and is
unverified; `PS2X_CD_IMAGE` can't be set on device (H4); the codegen-dir
mechanism isn't on `3adc0478` (H1).
