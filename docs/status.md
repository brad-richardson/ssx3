# Status board (compact, authoritative — orchestrator updates each poll)

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on Odin.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
Updated 2026-09-22 ~21:00 on the **Mac mini** (host of record; laptop retired, still the bytesize jump host).

| Lane | State | Pinned rev | Next action | Blocker / lease |
| --- | --- | --- | --- | --- |
| E (PS2 runtime) | **E31: stock race runs on the Mac** (Happiness Rival: HUD, timer 00:00:03 → 00:00:04); Snow Jam stalls at 99%. **E32 fold running on the mini's internal disk** | fork `ssx3` @ `3d4feed`; bypass + pad script `fork/e29-movie-bypass` @ `ee39b9f` | Gate E31, E32 → E33 apply E30's fix; Snow Jam stall diagnosis after T47 | P-lane lease (E32) |
| G (GS composite) | G42 PASS (table + stop): Turnip didn't start due to a struct-layout bug in our loader hunk. **G43 running**: fix + rerun, G lane onto internal | clone `3a66c19` + G26/G28 + G40/G41 hunks (SSD `parallel-gs-g7`) | Gate G42 → bundle Turnip or pipeline fix | Odin after PF1 |
| N (Android) | N3 PASS: title screen natively on the Odin | bytesize `n2-android` @ `619d48a` (local) | N4 after PF1's Odin race attempt: showWhenLocked, PNG export, clean build | bytesize via laptop jump |
| T (PCSX2 reference) | **T47 PASS**: reference frames show the recomp misses 3D models and draws wrong sprite cells | bytesize WSL | T48: PCSX2 GS dumps for the 3D gap (drafting) | none |
| Perf / GS bridge | PF1 resumed: Odin title baseline done (21.5 guest vsyncs/s = 0.36×, GameThread 99%); launch 6 = **first Odin race attempt** (Happiness, 900 s cap). Mac mission moved to a post-E32 brief | N3 APK `69a79e29…` | Gate PF1 → GS bridge step (a) | Odin after G42 |
| V (storage) | **Mini is up** (smoke 458/458 at 19:13). V2 running: SSD inventory for a cleanup pass (read-only) | — | Orchestrator deletes from V2's table; Brad decides NOT-SSX3 rows | Brad: Tailscale on the mini |
| I (iOS) | Parked | `i23-ffmpeg-ios` @ `aa73dbc` | Re-probe after E30 | needs E change |
| GameCube | Reserve (`docs/reserve.md`) | — | none | — |

Gate reads 2026-09-22 (orchestrator): **E31 PASS**. All four bars met on Happiness Rival (e31l): menus respond, load completes, HUD live, timer advances; caveat: 3D renders near-black. Snow Jam stalls at 99%. **G42 PASS (table + stop)**. The Turnip HAL opened, but our `G42HalDevice` omitted `hw_device_t.reserved[12]` and read `GetInstanceProcAddr` at offset 40 instead of 136; the driver question stays open (G43). C1 landed on the system control this time (G41: lost). **T47 PASS**. Reference frames are renderer-independent; by eye the recomp lacks 3D (no rider on Select Character) and misplaces sprite atlas cells. **The E31 race frame is almost black apart from the HUD**: the race runs (timer advances) but the 3D world (terrain textures, sky, rider) doesn't render. **G41 PASS**. Masked PSM1 draws land byte-exact on the Odin, so B's loss depends on pass context; the Mission-2 skip was correct; the build overage (4 Mac builds) is accepted as declared. **N3 PASS**. First native Odin boot of the PS2 recomp reaches the animating title screen (orchestrator viewed on-device screencap `scap-14`); bar (c) accepted on behavioral proxy because the marker is compiled out of release builds. **N2 PASS**. The Android full-title link is green with the codegen-dir port (APK `21a9230c…`, 9,441 functions, 0 undefined); gate exception accepted, because the stub premise was wrong at the old pin. **G40 PASS**. F2 execution-loss: composite draws are accepted with byte-exact input but never write B on Adreno (Mac writes `840cd308…`). The mission-2 skip was correct; the budget overage (3 Mac builds/runs for two hunk-bug repairs) is accepted as declared. **E30 PASS (design)**. The zero-packet stall is a correct parser waiting on chunk 2, which the host latch never requests; the fix + 6 new tests are ready as diffs (harness-proven, both compile under E29's flags). **E29 PASS**. `PS2X_SKIP_MOVIE=1` reaches the rendered SSX 3 title screen ("Press START button"; frame `2ab49bac…` checked by eye). Flag off reproduces e28a 20/20; suite 458/458 with the flag off, 453/458 on (the 5 MPEG tests the bypass suspends). Three movies skipped, `offered=15056 consumed=15056 packets=0`. C3 missed as written (wrong proxy). A2 amendment accepted: the SSD byte caps are logical bytes, because ExFAT allocates 1 MiB per file. **G39 PASS**. Both fixes hold on
current HEAD, 48/48 no-perturbation classes equal. Adoption decision:
carried diffs now, in-clone commit after the storage cutover. **V1 PASS**.
7610/7610 files stable across two passes, restore manifest written, smoke
restore passed. **N1 PASS**. The Android scaffold exists; the logcat pipe is
in code but never built; the entry provider comes from raylib and is
unverified; `PS2X_CD_IMAGE` can't be set on device (H4); the codegen-dir
mechanism isn't on `3adc0478` (H1).
