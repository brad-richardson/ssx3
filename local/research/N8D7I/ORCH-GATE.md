# N8D7I orchestrator gate — PASS, category A

Worker commit `713e6c44`; read the whole report, run receipt and excerpt,
checked script SHA `c842e4c7…7013c` against the released version, reran
the 26/26 parser self-check, and viewed the committed 512×448 PNG
(`ee2a6849…6e0a`). The frame is mostly black with isolated snowy terrain
and HUD fragments. One APK install and one launch only; PID 10097 was
force-stopped and absent; Odin lease was released. Device preflights
passed keyguard, battery and storage checks. PNG and metadata had two
matching device and local SHA reads.

Same tick2050 FBP112/PMODE ff21 receipt: selected input, circuit1 and
GPU stage each 448 words, 5,333 occupied pixels and **35 active tiles**;
input=circuit and circuit=stage at 448/448. Independent circuit1 and
merged summaries match. Final sampled and raw vectors match at 896/896,
10,636 occupied pixels and **63 active tiles**, with control 128 PASS.
The Android probe prints SHA fields `unavailable`; the packed vector
digests in the report were recomputed from the complete parsed vectors.

This meets predeclared **category A**: the selected input is already
sparse on this Odin run. It rules out circuit1 or a later readback as the
first place these particular pixels were lost. It does not distinguish
sparse raw VRAM from CPU decode, input selection or driver behavior;
Mac and Odin used different GS streams. The 114.32 s diagnostic wall
time is not a speed measurement. Next: N8D7J source audit and bounded
same-run raw-input discriminator.
