# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-24 ~20:00 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `f949ff0` (sound HLE with planar tag-1 fix, VIF1 IMAGE continuation, GS replay harness + `[gs-path]` log, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `963cb57` (wave64 binning fix) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (E54F2 regen).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | **Live Odin race from committed fork code** (N9). **First clean baseline (N10, 2 runs, sound off): race 0.113×**, menus ~0.5×, title ~0.54×; rider moves (44 MPH by 00:00:46). Thermal status 4–5 under sustained load. | Rider idle 00:00:06–00:00:40 (check Mac on the same route); image fill/margins; stripes; TL1 tooling after UP1 | — |
| **E** PS2 runtime | Race terrain, rider, HUD draw on Mac; sky/sun missing, dark GS region. Save seed source found: Odin AetherSX2 `Mcd001.ps2` has `BASLUS-20772-GAM0001`/`SET0001` (private copy, `ac98cf37…`). | save-card seed; sky; E54E, INTC 5/7; E57 VU1 speed | — |
| **G** GS / GPU backend | GPU backend opt-in on Mac (GB6C, 578/578 replays). Damaged title glyphs traced to a texture word at packet 5470 (GB7C7P2); earlier producer open. Bilinear rounding differs Mac vs Adreno (small). | Glyph producer; exact bilinear (shader regen); wave128 Turnip probe (later) | — |
| **A** Audio | **Menu music fixed (AU8):** tag-1 PCM is planar; our fixed runtime (`f2ec588`, on `ssx3`) matches PCSX2's real output. Host output still needs `PS2X_SOUND=1`. | Brad listens to AU8 clips; turn sound on in the iOS/Odin env; race/SFX paths (IOP slice, voices) | Brad's listen |
| **I** iOS | I29: iOS build of `fb11e18` runs to the race on Simulator and iPad; installed on Brad's iPhone (no launch). Sound off by default and pre-planar-fix. iPad still an iPhone-compat window. | Rebuild after the AU8 fold (sound on, planar fix); I28 iPad-native (low priority) | — |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Speed:** Odin clean baseline is N10 (race 0.113×); Mac baselines predate the sound fold (re-measure before quoting).
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). **Leases:** Odin free; mini slots free.
