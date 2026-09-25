# DK1 — the picture is ~50 % too dark on iOS (paraLLEl) and likely the Odin (muse, 2 h)

## Facts
- Brad (09-25, iPhone, I33 build = paraLLEl default): "rendering feels darker than expected, like 50 % of the typical brightness". Main menu otherwise "basically perfect".
- Compare the Odin screencap `~/dev/ssx3-work/F2/odin/S1/sc01-tick2100-t123.png` (visibly dim) with the Mac paraLLEl frame `~/dev/ssx3-work/F2/run/B1/frames/snap/snap-002090t-0062.47s.png` (normal) and the earlier iOS **CPU-backend** iPad shots (`~/dev/ssx3-work/F1/ios/run-ipad/shot-t1960.png`, normal).
- PS2 framebuffers carry alpha where 0x80 means 1.0; a presenter that alpha-blends the game texture over black (or uses its alpha anywhere) shows ~50 %. Other candidates: sRGB vs UNORM texture/swapchain mismatch (gamma), paraLLEl's scanout output range (e.g. PMODE/CRTC merge ALP), a GLES-only shader path, a texture format swizzle.

## Steps
1. Trace the present path per platform with file:line: paraLLEl `vsync()` output → how the runtime turns it into the raylib texture → the draw call and its blend state/shader on desktop GL (Mac), GLES (iOS, Android). Note where they differ.
2. Measure: pixel stats (mean RGB and the alpha channel) of the image right before presentation on the Mac, and from the Odin/iPad screenshots of comparable scenes (Select Peak and race). Is iOS/Odin ≈ 0.5 × Mac? Is the pre-present alpha ≈ 0x80?
3. One fix for the named mechanism (e.g. draw the game quad with blending off / alpha forced to 1, or the correct texture format), unit or visual check, on fork branch `dk1-bright` from fork `ssx3` `0ed07c4`. Validate on the **iPad** (install + one fresh-card launch with live container path; `deploy-ios.sh ipad` after install; I33 recipe `local/research/I33/build-install.sh`), screenshots viewed before/after. The **Odin**: only if the lease is free and battery ≥ 20 % (NP1 may hold it; don't wait for it, note it as a gap). **iPhone: nothing** (the orchestrator installs a combined build).
Rules: never push; runner-dir check empty; Android compile check if you touch shared presenter code (bytesize, F2 recipe) or note it as a gap; text only in git. Deliverable `local/research/DK1/REPORT.md`; commit `[DK1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push. Budget 2 h.
