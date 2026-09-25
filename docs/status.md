# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-24 ~20:00 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `71c952e` (iOS analog stick + D-pad right, sound HLE with planar tag-1 fix, VIF1 IMAGE continuation, GS replay harness + `[gs-path]` log, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `963cb57` (wave64 binning fix) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (E54F2 regen).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | **Live Odin race from committed fork code** (N9). **First clean baseline (N10, 2 runs, sound off): race 0.113×**, menus ~0.5×, title ~0.54×; rider moves (44 MPH by 00:00:46). Thermal status 4–5 under sustained load. | **Brad's play build installed** (TL1 APK `aeb60d4d`: planar audio, sound on, his save autoloads, manual play; I31). N11 stage budget; rider idle 00:00:06–00:00:40 (check Mac); image fill/margins; stripes. Odin replays: `local/tooling/odin/odin_replay.py` | — |
| **E** PS2 runtime | Race terrain, rider, HUD draw on Mac; sky/sun missing, dark GS region. Save seed source found: Odin AetherSX2 `Mcd001.ps2` has `BASLUS-20772-GAM0001`/`SET0001` (private copy, `ac98cf37…`). | save-card seed; sky; E54E, INTC 5/7; E57 VU1 speed | — |
| **G** GS / GPU backend | GPU backend opt-in on Mac (GB6C, 578/578 replays). Damaged title glyphs traced to a texture word at packet 5470 (GB7C7P2); earlier producer open. Bilinear rounding differs Mac vs Adreno (small). | Glyph producer; exact bilinear (shader regen); wave128 Turnip probe (later) | — |
| **A** Audio | **Menu music fixed and confirmed by Brad** (AU8: tag-1 PCM is planar; matches PCSX2's real output). Host output still needs `PS2X_SOUND=1`. **Race SFX working on AU9's branch and confirmed by Brad** (SPU2 voice layer + sound-bank lookup fix); not folded yet. Sound on in the iOS and Odin play builds. | Gate + fold AU9 |  — |
| **I** iOS | **I32: build `71c952e` installed on Brad's iPhone (no launch) and iPad**: floating analog stick left, D-pad right, fixed music, sound on, his save autoloads, manual play (I31). Simulator + iPad reach the race. Audio gaps expected below full speed. iPad still an iPhone-compat window. | Brad listens on the phone; I28 iPad-native (low priority) | Brad's listen |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Speed:** Odin clean baseline is N10 (race 0.113×); Mac baselines predate the sound fold (re-measure before quoting).
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). **Leases:** Odin: N11; mini: four boot slots (speed runs take all four).
