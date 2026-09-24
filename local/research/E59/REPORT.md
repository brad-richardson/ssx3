# E59 — race sky/sun and flat terrain textures

Worker: Codex. Brief: `local/muse/prompts/E59.md`. The orchestrator decides.

## Pins and budget

| Item | Value |
| --- | --- |
| Fork base | `b9647f5` |
| Worktree / branch | `~/dev/ssx3-work/E59/PS2Recomp`, `e59-sky` at `b9647f5` |
| Fold runner SHA-256 read 1 / read 2 | `f3de8d2cc051c4ac30f8e0e07a84f45eb4889923727627b7416b67c79d251608` / same |
| ELF SHA-256 read 1 / read 2 | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` / same |
| ISO SHA-256 read 1 / read 2 | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same |
| Builds / boots | 6 build invocations (5 variant runners plus 1 recompiler) / 6 boots; all passed |
| Disk | 92.4 GB of 200 GB before work; 96.6 GB after work; E59 workdir 1.6 GB (<8 GB cap) |

## Sky discriminator

| Variant | Change | Build | Boot/ticks | Sky | Sun | Flare | Frame |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IEEE | `PS2X_EE_FPMODE=ieee` | existing fold runner | slot 1, PID 93263, target tick 2127, 115.921 s, bounded exit | absent in all 3 views | absent in all 3 views | absent in all 3 views | `~/dev/ssx3-work/E59/run/ieee/race{1800,1950,2100}-tick{1796,1942,2094}.png` |
| h revert | VU1 EFU decode, latency, trace names reversed in 2 files | E59 build PASS, SHA `8e0b92ed4179b0e99463c8e112779461946e77a391cf871ee7edba7bc6cf2117` ×2 | slot 1, PID 1817, target tick 2131, 152.308 s, bounded exit | absent in all 3 views | absent in all 3 views | absent in all 3 views | `~/dev/ssx3-work/E59/run/h_revert/race{1800,1950,2100}-tick{1793,1944,2090}.png` |
| a revert | old generated VU0 transfer/call paths plus CTC2 CMSAR1; 13 generated files differ | E59 build PASS, SHA `ddaad998ba463649160b2a1b64e8c4026a76cc17d8f00649436fc2c4565d22b5` ×2 | slot 1, PID 18181, target tick 2141, 86.753 s, bounded exit | visible by tick 2103 | bright disk visible by tick 2103 | visible by tick 2103 | `~/dev/ssx3-work/E59/run/a_revert/race{1800,1950,2100}-tick{1793,1947,2103}.png` |
| c+d revert | special values, VFTOI, MAX/MIN/C.cond | not found | not found | not found | not found | not found | not found |
| g revert | guest log binding | not found | not found | not found | not found | not found | not found |

### Subgroup discriminator

| Variant | Generated difference from folded codegen | Runner SHA-256 ×2 | Race result |
| --- | --- | --- | --- |
| VCALLMSR-old only | 8 sites in 8 generated files; transfer and CMSAR1 translations remain new | `575c34f0c036d9746dfaba0b8f473f9c856f0985640c9efceaddc5becf0319f8` | Boot 4, slot 2, PID 19923, tick 2162, 101.824 s. Viewed frames at 1795, 1946, 2096: no visible sun/flare; terrain mostly whole, with viewpoint variation. Receipt `~/dev/ssx3-work/E59/run/vcallold/result.json` and PNGs. |
| VSQI-old only | 14 sites in 3 generated files; VCALLMSR, VLQI, CMSAR1 stay new | `eefbc974a92262193b00ca8bd752c71bae6302f0fc47912721f0a91f516f9dfc` | Boot 5, slot 1, PID 21706, tick 2121, 96.784 s. Viewed frames at 1796, 1948, 2092: shard/spray scene and no visible sun/flare. Receipt `~/dev/ssx3-work/E59/run/vsqiold/result.json` and PNGs. |
| VCALLMSR-old + VSQI-old | 22 sites in 11 generated files; VLQI and CMSAR1 stay new | `a8517d41d2c42be656867dc782c042626d2a8c14af8e996d99f1a69b8b58c31a` | Boot 6, slot 1, PID 28807, tick 2169, 76.634 s. Viewed frames at 1790, 1943, 2100: shard terrain and no visible sun/flare. Receipt `~/dev/ssx3-work/E59/run/vcall_vsqiold/result.json` and PNGs. |

The 13 generated files changed by full group a contain 8 VCALLMSR sites, 14 VSQI sites, 1 VLQI site, and 1 CTC2 CMSAR1 site. The changed VSQI sites are 0x229f48–0x229f74, 0x229fac–0x229fbc, and 0x3feb64; VLQI is 0x3feb8c. Receipts: `~/dev/ssx3-work/E59/{codegen-a.diff-list,codegen-vcallold.diff-list}`.

## PCSX2 comparison

| Site/program | Our input/output or GIF packet | PCSX2 input/output or GIF packet | Interpretation |
| --- | --- | --- | --- |
| VSQI at 0x229f48/4c/50/54, 0x229f68/6c/70/74, 0x229fac/b0/b4/b8/bc, 0x3feb64 | Fold translation stores `vf[fs]` at `VU0 data[vi[it]*16]`, then increments `vi[it]`; pre-E53 translation stores to EE RAM at `(vi[is]&0x3ff)*16` and uses the wrong register fields. Full-a revert and VSQI-only variants use that old behavior. | E53's PCSX2 `_vuSQI` comparison says source `fs=bits 15:11`, address register `it=bits 20:16`, VU data memory, then `it++` (see E53 report §changes 1). | **New VSQI behavior matches PCSX2; old behavior is wrong.** The old behavior's effect on sky cannot be accepted as a fix. The 14 sites are the exact guest instructions changed in this program; isolation among sites is pending. |
| VCALLMSR at eight generated sites, including 0x37deb8 | Fold reads CMSAR0 to start VU0; VCALLMSR-old variant reads vi27. | E53's PCSX2 comparison says VCALLMSR starts at CMSAR0. | New behavior matches PCSX2. VCALLMSR-old alone did not visibly restore sun/flare in the sampled race frames. |
| VLQI at **0x3feb8c**, inside the function whose verified label is `sceVu0MemReadQ` | Fold reads VU0 data at `vi1*16`; full-a revert reads EE RAM at `(vi1&0x3ff)*16`. This is one of only two generated differences between the full-a and final combined variants. | E53's PCSX2 `_vuLQI` comparison says read VU0 data, then increment vi1; the current fold matches. | Best remaining exact instruction lead. The other difference is CTC2 CMSAR1 at 0x3fed54, whose new path would print on its first eight uses; no such print appeared in E53 or E59 boot logs. Different race scenes prevent assigning the visible sun in the full-a run to VLQI alone. |
| 0x2270/0x22c8 sky-like PSMT8 256² packet at TBP0 11017 | E53 GIF at tick 8261: 75 prims, TEX0 CBP 10756, TEX1 0x61, CLAMP 0x5, ALPHA 0x1, MIPTBP1 0x6d2906d0906ce9. | T65 PCSX2 GS vsync 0: 81 prims with same TBP0, PSM/TW/TH, TEX1 and CLAMP; TEX0 CBP 14473, ALPHA 0x2a, MIPTBP1 0x500004f8004f00. | The candidate sky packet is submitted in E53, but palette, blend state, and mip pointers differ. Which difference hides the sky is unproved; scene and frame are not identical. |

## Flat textures

| Field | Recomp terrain 0x2270/0x22c8 | PCSX2 terrain 0x2270/0x22c8 | Systematic difference? |
| --- | --- | --- | --- |
| TEX0 | E53 tick 8261: 10,411 textured 0x2270/0x22c8 prims, 20 raw values; common PSMT4 128², TBP0 14441, CBP 11657/11658; same format bits as T65 | T65 GS vsync 0: 20,149 all-path textured prims, 63 raw values; common PSMT4 128², TBP0 14857, CBP 16367/16368 | Base/CLUT pointers differ, but texture-cache allocation and visible scene differ; no field-mode defect established |
| TEX1 | E53 terrain: 11 raw values, K top 0xf4e×3382, 0xf79×2586, 0xf20×1179; low word 0x168 on the mipmapped terrain, 0x61 on no-mip prims | T65 all-path: low word 0x168 on 10,861 prims; K top 0xf4e×4259, 0xf53×3172, 0xf3c×1101 | The mip mode 0x168 matches; K differs by object and moment |
| CLAMP | E53 terrain: 0x0×10,200, 0x5×211 | T65 all-path: 0x0×17,391, 0x5×2,758 | Both values appear; population differs |
| ALPHA | E53 terrain: 0x44×7345, 0x2a×2756, 0x48×235, 0x1×75 | T65 all-path: 0x44×9110, 0x2a×8197, 0x81×2426, others | Terrain modes overlap; the matched sky-like subset below differs |
| IMAGE uploads/vsync | E53 8258, 8259, 8261–8265: **60**, 397,056 bytes each; 8260: 0 (non-drawing vsync). Mip chain shapes 64×32/32×16/16×8: 13 each on drawing vsyncs | T65 GS vsyncs 0–7: **73–74**, 444,928–445,184 bytes each; same mip shapes: 23 each | **First reproducible stream difference:** 13–14 fewer uploads and 10 fewer three-level mip chains per drawing vsync in E53; same timer region, not a same-scene proof of a bug |
| MIPTBP | E53 terrain: MIPTBP1 4 values, top 0x78c9078a907889×8592; MIPTBP2 0 on all 10,411 | T65 all-path: MIPTBP1 6 values, top 0x7a6907a4907a29×15,299; MIPTBP2 0 on all 20,149 | Mip base pointers vary with allocations; no format difference established |

The T65 GS dump does not carry a VU1 startPC per GIF transfer, so its per-prim side is all-path. The E53 side is restricted to 0x2270/0x22c8. These views are about 18–19 seconds into different races and cannot attribute every primitive to the same object.

### Matching sky-like GIF subset

The PSMT8 256² TEX0 at **TBP0 11017** is present in both dumps. At E53 tick 8261 its 75 primitives came from 0x22c8 (45) and 0x2270 (30). T65 GS vsync 0 has 81 primitives with the same TBP0, TBW=4, PSMT8, TW=TH=8, TFX=0, TEX1=0x61, CLAMP=0x5, ABE=1, and MIPTBP2=0. The other fields are:

| Field | E53 75/75 prims | T65 81/81 prims |
| --- | --- | --- |
| TEX0 full / CBP | 0x2005408621312b09 / 10756 | 0x2007112621312b09 / 14473 |
| ALPHA | 0x1 | 0x2a |
| MIPTBP1 | 0x6d2906d0906ce9 | 0x500004f8004f00 |

This is a packet-level discrepancy on the candidate sky texture, including palette pointer and blend state. The E51 VRAM decode identified a PSMT8 256², TEX1=0x61 terrain-program texture as the sky dome, but at a different TBP (14185); therefore the TBP-11017 identification remains an inference. Raw tables and the E51-based parser extension are `~/dev/ssx3-work/E59/{gif_table.txt,gif_table.py,e59_gif.py}`; the PCSX2 dump was decompressed from `~/dev/ssx3-work/T65/out/t65a-race.gs.zst`.

## Receipts and commands

`python3 ~/dev/ssx3-work/E59/e59_boot.py --label ieee --capture --fpmode ieee --target 2110 --wall 500` (escalated). Receipt: `~/dev/ssx3-work/E59/run/ieee/result.json`, `boot.log`, and the three PNGs. Direct view shows snow terrain and a black upper background; no sky dome, sun, or flare.

`git diff f4ba160^ f4ba160 -- ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp | git apply -R`; `zsh ~/dev/ssx3-work/E59/build.sh`; `python3 ~/dev/ssx3-work/E59/e59_boot.py --label h_revert --capture --fpmode ps2 --runner ~/dev/ssx3-work/E59/build/ps2xRuntime/ps2EntryRunner --target 2110 --wall 500` (escalated). Receipts: `~/dev/ssx3-work/E59/{cmake.log,build.log,run/h_revert/result.json,run/h_revert/boot.log}` and three PNGs. Direct view: black upper background and lit snow in all three frames; no sky dome, sun, or flare.

`python3 ~/dev/ssx3-work/E59/revert_a.py` restored seven VU0 translation functions and CTC2 CMSAR1 to their pre-E53 bodies; `nice -n 10 ninja -C ~/dev/ssx3-work/E59/build -j8 ps2_recomp`; `ps2_recomp ~/dev/ssx3-work/E59/ssx3-a.toml`; `zsh ~/dev/ssx3-work/E59/build-a.sh`; `python3 ~/dev/ssx3-work/E59/e59_boot.py --label a_revert --capture --fpmode ps2 --runner ~/dev/ssx3-work/E59/build/ps2xRuntime/ps2EntryRunner --target 2110 --wall 500` (escalated). Receipts: `~/dev/ssx3-work/E59/{a-source.diff,build-recompiler-a.log,regen-a.log,codegen-a.diff-list,cmake-a.log,build-a.log,run/a_revert/result.json,run/a_revert/boot.log}`. Direct view: at tick 2103 the sun and a large orange flare are present, with shard terrain like E50. The earlier two frames show shards but no visible sun; camera/scene timing differs between runs. The function-map SHA-256 was `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba` twice.

Subgroup builds: `zsh ~/dev/ssx3-work/E59/build-vcallold.sh`, `build-vsqiold.sh`, and `build-vcall-vsqiold.sh`. Each reconfigured the same build dir with its named generated-code directory; sources and binary differences are in `~/dev/ssx3-work/E59/codegen-*.diff-list`. Each was booted with `e59_boot.py --label <vcallold|vsqiold|vcall_vsqiold> --capture --fpmode ps2 --runner ~/dev/ssx3-work/E59/build/ps2xRuntime/ps2EntryRunner --target 2110 --wall 500` (escalated). Their CMake/build logs, result JSONs, boot logs, and all three captured frames per run are in `~/dev/ssx3-work/E59/`. The worktree source diff for the final combined variant is saved as `vcall-vsqiold-source.diff`; afterward `git restore` left the local `e59-sky` branch clean at `b9647f5`. No fork commit or push.

GIF analysis: `zstd -d -f ~/dev/ssx3-work/T65/out/t65a-race.gs.zst -o ~/dev/ssx3-work/E59/t65a-race.gs`; `python3 ~/dev/ssx3-work/E59/gif_table.py` reads that and `~/dev/ssx3-work/E53/run/gif-e53c.bin`. It extends E51's decoder only for ALPHA and MIPTBP registers. Raw one-vsync counts are in `gif-table.txt` here. Six directly viewed comparison frames at about tick 2100 are in `frames/` here; all three per run remain in the workdir. The IEEE boot log explicitly says `PS2X_EE_FPMODE=ieee`; the h and a logs say `ps2`. All boots stopped their own PID at the target, released their slot, and exited without a crash.

## Gaps and recommended next action

- **Group-a is the only revert group with a visible sun and flare** in its tick-2103 frame. IEEE mode and the EFU revert did not restore them. The subgroup boots did not reproduce that appearance; race state varies between runs. The group-level result is therefore a visual lead, not proof of a causal instruction.
- The exact guest sites changed by group a are enumerated above. The **single-site lead is VLQI at 0x3feb8c**, because the final combined variant differs from full group a only there and at CTC2 CMSAR1 0x3fed54; no CMSAR1 starts were logged. The new VLQI and VSQI semantics match PCSX2, so restoring old behavior is not a candidate fix.
- The matching sky-like 0x2270/0x22c8 packet already differs from PCSX2 at TEX0 CBP, ALPHA and MIPTBP1. A deterministic same-scene capture of the 0x3feb8c input/output and this packet would decide whether the sky is lost before GIF submission or through texture/blend state. The T65 dump lacks per-primitive VU1 startPC, so the PCSX2 side of the texture table is all-path. No fix or unit test was made because no single corrected mechanism was established.
- The brief's c+d and g group reverts were not run after group a produced the visible sun; the remaining two boot slots were used on subgroup discrimination. The final variant consumed the sixth boot.
