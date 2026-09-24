# GB7C6 orchestrator gate — PASS/B (2026-09-24)

Read the full REPORT and packet table. Reran `python3 local/research/GB7C6/check.py`: 33 PASS rows and `RESULT ACCEPT`. `git show --check 48d2253e` passed. Checked the load-bearing `combineTexture`, `WritePixel`, `SampleTexture`, `DrawSprite`, and `addrPSMCT32` source in the pinned GB4 fork. No new frame was generated; the GB7C5 gate viewed the tick600/601 frames from this same stream.

The supported conclusion is narrow: packet5470 at tick259, batch10 is a textured sprite that writes FBP112 pixel (342,377), and its MODULATE-white path makes the destination RGB equal the sampled RGB. The computed tap0 is (343,378), GS address `0x000bae74`; the watched destination is `0x0019ae38`. The observed `dc302f3b → dc353341` implies sampled RGB `353341` **backwards**. The actual texture word and its earlier writer were not observed, so this is category B, not forward source proof. One pixel does not establish a glyph shape, and no GPU cause follows from this CPU/static analysis.

Next: GB7C7 one default-OFF direct-CPU replay tap at packet5470/batch10/pixel (342,377), logging the sampled word and immediate pre/post pixel words; compare ON/OFF hashes and frames. Only then design a same-stream CPU/paraLLEl comparison. No build, replay, boot, device, or speed number in GB7C6.
