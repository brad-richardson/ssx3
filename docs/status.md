# Status board

Milestone: stock SSX 3 gameplay through our PS2 static recomp runtime on the Odin 3.
Rules: `AGENTS.md`. Open work: `docs/todo.md`. Numbers: `docs/numbers-ledger.md`.
History: git log (this board is current state only). Updated 2026-09-25 ~07:15 EDT, Mac mini.

**Pins:** PS2Recomp fork `ssx3` `74e2df2` (F4 + musttail chain fix: VU1 static recompile stage A, NP1 host fixes, vf0 read-only emitter, VU0 R ctor; F3: pacing, full brightness, pad v2, tap latch, V2/V3 unpack, rider vf0 fix; Android lambda build fix; ST1 progressive scanout, no stripes; F2: 64-bit sign branches + canonical codegen regen, sound HLE on guest time, coverage/INTC counters; F1 fold: RR1 race/menu rendering fixes, E57 VU1 speed, AU9 race SFX, N11 profileable + pin knob; I32 iOS controls; sound HLE, GS replay harness, widescreen, Turnip packaging) ·
paraLLEl-GS fork `ssx3` `19d93b2` (wave64 binning fix; `PGS_HIER_BINNING` knob) · Granite fork `ssx3` `166ba21a` ·
canonical codegen `~/dev/ssx3-work/codegen-ssx3` (F2/SB1 regen, `PS2X_SBR_*` predicates; previous kept as `codegen-ssx3-pre-sb1`).

| Lane | State | Next | Blocker |
| --- | --- | --- | --- |
| **N** Android / Odin | **Brad's play build = F4** (APK `f2e519de`, fork `74e2df2`: VU1 static recompile, NP1 host fixes, rider, brightness, his save, manual play). **Race 0.1665×** (1.20× vs F3); frame 100 ms. adb over Wi-Fi. | F5 build (stage B, pipelined present, 4× decision by measurement) | — |
| **E** PS2 runtime | **First stock race finished** (FR1: Happiness 2nd 04:18 → results); Snow Jam + Metro-City race; post-race garbage jump under PF1. **Race looks like the real game on the Mac** (RR1: PATH3 one-EOP-per-unmask, V4-5 unpack expansion, DMA 4096-tag cap; menus fixed incl. the Peak 1 photo). **VU1 1.35× bit-exact** (E57). Sound banks load (AU9 `0x3E3968` override); the 32-bit sign-branch bug class is open. All on branches; **F1 folding onto fork `ssx3`**. | F1 fold + device builds; sign-extension hunt (after RV3) | — |
| **G** GS / GPU backend | **paraLLEl is now the Mac default** (GB8: det-hash identical to the CPU backend, 1.87× faster to the race, race 0.224× vs 0.134×); set `PS2X_GS_BACKEND=parallel` + `GRANITE_VULKAN_LIBRARY` in boot tooling, CPU GS kept for reference. Odin menus are GsWorker-bound in the Turnip driver's CPU side (N11). | GB9 Mac↔Odin path alignment; glyph producer; exact bilinear | — |
| **A** Audio | **Menu music fixed and confirmed by Brad** (AU8: tag-1 PCM is planar; matches PCSX2's real output). Host output still needs `PS2X_SOUND=1`. **Race SFX working on AU9's branch and confirmed by Brad** (SPU2 voice layer + sound-bank lookup fix); not folded yet. Sound on in the iOS and Odin play builds. | Gate + fold AU9 |  — |
| **I** iOS | **F3 build `ec2dbf1` on Brad's iPhone (no launch) and iPad**: paraLLEl (GPU) default, full brightness, rider fixed, pad v2 (stick ×1.5, D-pad below-left), tap latch, pacing, race SFX, his save + manual play. | Brad's play; F4 (VU1 recompile) next; I28 iPad layout | Brad's play |
| **W** Widescreen | Anamorphic 16:9 default; 2D stretch accepted by Brad. | — | — |
| **T** PCSX2 reference | bytesize PCSX2 with trace hooks (T48/T49, AU4/AU6 tag capture). | On demand | — |
| **V** Storage | Mini internal 161/200 GB. SSD tier-1 cleanup done. | Brad decides GameCube-reserve and personal folders | Brad |
| GameCube | Reserve (`docs/reserve.md`). | — | — |

**Disk:** mini 63.5 of 200 GB after archiving 26 closed lanes to the SSD (`ssx3-archive/2026-09-25/MANIFEST.txt`, SHA-verified).
**Speed:** Odin race 0.140× on the F1 fold (N11 before it: 0.116×, VU1 = 118 of 145 ms/frame). Mac race 0.224× on paraLLEl (GB8), CPU GS 0.179× with E57. F1 re-measures both on the folded tip.
**Workers:** bounded briefs on muse (Go Muse Spark Contributor); Opus panes when Brad approves;
no Codex workers (quota). RV3 Fable review running. **Leases:** Odin on the mini USB (~55 %): NP1 next; USB drains under load, ~1–4 %/run; mini: four boot slots (speed runs take all four).
