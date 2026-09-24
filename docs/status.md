# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-24 ~20:00 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `fb11e18` (sound HLE, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `963cb57` (wave64 binning fix) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (E54F2 regen).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | Odin black frame solved (N8X1: paraLLEl-GS hierarchical binner at wave128 on Adreno; fixed wave64). Live Odin shows menu and race on screen (diagnostic APK). Fix and packaging now on the fork tips. | **N9 Part 2** (running, `w2:p7C`): one APK from fork tips, live Odin race, no knob env | — |
| **E** PS2 runtime | Race terrain, rider, HUD draw on Mac; sky/sun missing, dark GS region. Save seed source found: Odin AetherSX2 `Mcd001.ps2` has `BASLUS-20772-GAM0001`/`SET0001` (private copy, `ac98cf37…`). | UP1 upstream harvest (after N9); save-card seed; sky; E54E, INTC 5/7; E57 VU1 speed | — |
| **G** GS / GPU backend | GPU backend opt-in on Mac (GB6C, 578/578 replays). Damaged title glyphs traced to a texture word at packet 5470 (GB7C7P2); earlier producer open. Bilinear rounding differs Mac vs Adreno (small). | Glyph producer; exact bilinear (shader regen); wave128 Turnip probe (later) | — |
| **A** Audio | Sound HLE folded and default-on. Menu music equals PCSX2 to 1 LSB incl. stereo (AU7). | Brad listens to AU7 clip; race/SFX scene; host-output level | Brad's listen |
| **I** iOS | Simulator + iPhone install current as of `04f3ace` (no iPhone launch). iPad runs title→race but as an iPhone-compat portrait window. | I28 iPad-native landscape (low priority); rebuild on `fb11e18` when useful | — |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Speed:** clean baselines predate the 09-24 sound fold; re-measure before quoting (ledger).
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). **Leases:** Odin free; mini slots free.
