# Status board (compact, authoritative — orchestrator updates each poll)

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on Odin.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
Updated 2026-09-22 evening.

| Lane | State | Pinned rev | Next action | Blocker / lease |
| --- | --- | --- | --- | --- |
| E (PS2 runtime) | **E29 PASS: title screen reached** (bypass flag on). E31 running (title → menu → race); E30 PASS (fix + regression as diffs) | fork `ssx3` @ `3d4feed` (scrubbed; was `3adc0478`); bypass `e29-movie-bypass` @ `ee39b9f` | Gate E31 → next blocker or race; E32 fold → E33 apply E30's fix | P-lane lease + fork (E31) |
| G (GS composite) | G40 PASS: F2 execution-loss (masked PSM1 composite writes vanish on Adreno). G41 running (canary + one fix) | clone `3a66c19` + G26/G28 + G40 wall | Gate G41 | Odin (G41) |
| N (Android) | **N2 PASS: first arm64 APK links** (full title, 271 MB). N3 running: env shim + first Odin boot | bytesize `n2-android` (local) | Gate N3 | bytesize, then Odin lease |
| T (PCSX2 reference) | T46 PASS | bytesize WSL | T47 after N3's bytesize build | shares bytesize with N |
| V (storage) | V1 PASS (audit ×2, manifest, smoke, cutover list) | — | Mac mini cutover | **Brad: mini not set up** |
| I (iOS) | Parked | `i23-ffmpeg-ios` @ `aa73dbc` | Re-probe after E30 | needs E change |
| GameCube | Reserve (`docs/reserve.md`) | — | none | — |

Gate reads 2026-09-22 (orchestrator): **N2 PASS**. The Android full-title link is green with the codegen-dir port (APK `21a9230c…`, 9,441 functions, 0 undefined); gate exception accepted, because the stub premise was wrong at the old pin. **G40 PASS**. F2 execution-loss: composite draws are accepted with byte-exact input but never write B on Adreno (Mac writes `840cd308…`). The mission-2 skip was correct; the budget overage (3 Mac builds/runs for two hunk-bug repairs) is accepted as declared. **E30 PASS (design)**. The zero-packet stall is a correct parser waiting on chunk 2, which the host latch never requests; the fix + 6 new tests are ready as diffs (harness-proven, both compile under E29's flags). **E29 PASS**. `PS2X_SKIP_MOVIE=1` reaches the rendered SSX 3 title screen ("Press START button"; frame `2ab49bac…` checked by eye). Flag off reproduces e28a 20/20; suite 458/458 with the flag off, 453/458 on (the 5 MPEG tests the bypass suspends). Three movies skipped, `offered=15056 consumed=15056 packets=0`. C3 missed as written (wrong proxy). A2 amendment accepted: the SSD byte caps are logical bytes, because ExFAT allocates 1 MiB per file. **G39 PASS**. Both fixes hold on
current HEAD, 48/48 no-perturbation classes equal. Adoption decision:
carried diffs now, in-clone commit after the storage cutover. **V1 PASS**.
7610/7610 files stable across two passes, restore manifest written, smoke
restore passed. **N1 PASS**. The Android scaffold exists; the logcat pipe is
in code but never built; the entry provider comes from raylib and is
unverified; `PS2X_CD_IMAGE` can't be set on device (H4); the codegen-dir
mechanism isn't on `3adc0478` (H1).
