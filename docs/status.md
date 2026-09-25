# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-25 ~07:15 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `71c952e` (iOS analog stick + D-pad right, sound HLE with planar tag-1 fix, VIF1 IMAGE continuation, GS replay harness + `[gs-path]` log, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `963cb57` (wave64 binning fix) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (E54F2 regen).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | **Live Odin race from committed fork code** (N9). **First clean baseline (N10, 2 runs, sound off): race 0.113×**, menus ~0.5×, title ~0.54×; rider moves (44 MPH by 00:00:46). Thermal status 4–5 under sustained load. | **Brad's play build installed** (TL1 APK `aeb60d4d`: planar audio, sound on, his save autoloads, manual play; I31). N11 stage budget; rider idle 00:00:06–00:00:40 (check Mac); image fill/margins; stripes. Odin replays: `local/tooling/odin/odin_replay.py` | — |
| **E** PS2 runtime | **Race looks like the real game on the Mac** (RR1: PATH3 one-EOP-per-unmask, V4-5 unpack expansion, DMA 4096-tag cap; menus fixed incl. the Peak 1 photo). **VU1 1.35× bit-exact** (E57). Sound banks load (AU9 `0x3E3968` override); the 32-bit sign-branch bug class is open. All on branches; **F1 folding onto fork `ssx3`**. | F1 fold + device builds; sign-extension hunt (after RV3) | — |
| **G** GS / GPU backend | **paraLLEl is now the Mac default** (GB8: det-hash identical to the CPU backend, 1.87× faster to the race, race 0.224× vs 0.134×); set `PS2X_GS_BACKEND=parallel` + `GRANITE_VULKAN_LIBRARY` in boot tooling, CPU GS kept for reference. Odin menus are GsWorker-bound in the Turnip driver's CPU side (N11). | GB9 Mac↔Odin path alignment; glyph producer; exact bilinear | — |
| **A** Audio | **Menu music fixed and confirmed by Brad** (AU8: tag-1 PCM is planar; matches PCSX2's real output). Host output still needs `PS2X_SOUND=1`. **Race SFX working on AU9's branch and confirmed by Brad** (SPU2 voice layer + sound-bank lookup fix); not folded yet. Sound on in the iOS and Odin play builds. | Gate + fold AU9 |  — |
| **I** iOS | **I32: build `71c952e` installed on Brad's iPhone (no launch) and iPad**: floating analog stick left, D-pad right, fixed music, sound on, his save autoloads, manual play (I31). Simulator + iPad reach the race. Audio gaps expected below full speed. iPad still an iPhone-compat window. | Brad listens on the phone; I28 iPad-native (low priority) | Brad's listen |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Speed:** Odin race 0.116× sound on (N11; VU1 = 118 of 145 ms/frame). Mac race 0.224× on paraLLEl (GB8), CPU GS 0.179× with E57. F1 re-measures both on the folded tip.
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). RV3 Fable review running. **Leases:** Odin free (F1 Part 2 next); mini: four boot slots (speed runs take all four).
