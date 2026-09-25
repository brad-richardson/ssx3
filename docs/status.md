# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-25 ~07:15 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `0ed07c4` (Android lambda build fix; ST1 progressive scanout, no stripes; F2: 64-bit sign branches + canonical codegen regen, sound HLE on guest time, coverage/INTC counters; F1 fold: RR1 race/menu rendering fixes, E57 VU1 speed, AU9 race SFX, N11 profileable + pin knob; I32 iOS controls; sound HLE, GS replay harness, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `19d93b2` (wave64 binning fix; `PGS_HIER_BINNING` knob) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (F2/SB1 regen, `PS2X_SBR_*` predicates; previous kept as `codegen-ssx3-pre-sb1`).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | **Brad's play build = F2 + ST1** (APK `a3d26b56`, fork `0ed07c4`: RR1 rendering, race SFX, E57 VU1, 64-bit sign branches, no stripes, sound on, his save, manual play). **Race 0.139×** (F2; F1 0.140×, N11 0.117×); VU1 was 81 % of the frame before E57 (N11). Odin replays: `local/tooling/odin/odin_replay.py`. | NP1 profile + link/copy fixes; GB9 Part 2 descriptor-path replay; rider idle | — |
| **E** PS2 runtime | **Race looks like the real game on the Mac** (RR1: PATH3 one-EOP-per-unmask, V4-5 unpack expansion, DMA 4096-tag cap; menus fixed incl. the Peak 1 photo). **VU1 1.35× bit-exact** (E57). Sound banks load (AU9 `0x3E3968` override); the 32-bit sign-branch bug class is open. All on branches; **F1 folding onto fork `ssx3`**. | F1 fold + device builds; sign-extension hunt (after RV3) | — |
| **G** GS / GPU backend | **paraLLEl is now the Mac default** (GB8: det-hash identical to the CPU backend, 1.87× faster to the race, race 0.224× vs 0.134×); set `PS2X_GS_BACKEND=parallel` + `GRANITE_VULKAN_LIBRARY` in boot tooling, CPU GS kept for reference. Odin menus are GsWorker-bound in the Turnip driver's CPU side (N11). | GB9 Mac↔Odin path alignment; glyph producer; exact bilinear | — |
| **A** Audio | **Menu music fixed and confirmed by Brad** (AU8: tag-1 PCM is planar; matches PCSX2's real output). Host output still needs `PS2X_SOUND=1`. **Race SFX working on AU9's branch and confirmed by Brad** (SPU2 voice layer + sound-bank lookup fix); not folded yet. Sound on in the iOS and Odin play builds. | Gate + fold AU9 |  — |
| **I** iOS | **I33: paraLLEl (GPU) is the iOS default; installed on Brad's iPhone (no launch) and iPad** (fork `0ed07c4` + paraLLEl `19d93b2`, MoltenVK 1.4.2 embedded, Odin binning): iPad menus full speed (~60 vs/s vs ~19 on CPU), race 1.77×. His save + manual play kept. | Brad's first play; CPU fallback / error if Vulkan init fails; I28 iPad layout | Brad's play |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Speed:** Odin race 0.140× on the F1 fold (N11 before it: 0.116×, VU1 = 118 of 145 ms/frame). Mac race 0.224× on paraLLEl (GB8), CPU GS 0.179× with E57. F1 re-measures both on the folded tip.
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). RV3 Fable review running. **Leases:** Odin on the mini USB (~55 %): NP1 next; USB drains under load, ~1–4 %/run; mini: four boot slots (speed runs take all four).
