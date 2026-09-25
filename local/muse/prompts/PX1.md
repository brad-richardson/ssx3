# PX1 — PCSX2 as the pixel reference for our race frames (muse, 3 h, Mac + bytesize)

## Why
The CPU GS backend isn't a pixel reference (no dither, mip/LOD, COLCLAMP, AA1, SCANMSK; `docs/facts.md`). PCSX2's gsrunner replaying **our** GS stream is: it tells us whether a visual difference is our GS (paraLLEl) or upstream. RR1's converter (`local/research/RR1/rr1_cap2gs.py`, originally G46's `g46_rec2gs.py`) produced blank PCSX2 frames from tick 1608 on (review §4, "converter gap"). Fix that, then build a side-by-side gallery for the long tail of visual polish.

## Steps
1. Reproduce the blank-after-1608 issue on a fresh capture from the current fork tip (F3 tip if pushed, else `0ed07c4`; det boot to t2400, paraLLEl env, `PS2X_GS_CAPTURE`), convert, replay in the T48-pinned gsrunner on bytesize (`local/research/G46/g46_gsrunner.sh`; one heavy job at a time there; PINE one client). Find why frames go blank (e.g. a register/packet type the converter drops, a VSync/field mapping, the SMODE forcing) and fix the converter (text tool in `local/research/PX1/`). Validation: PCSX2's replay of our stream shows the race at 1800/2100/2400.
2. Gallery: for ticks ~1090 (Select Peak), 1180, 1800, 2100, 2400: our paraLLEl frame vs PCSX2-on-our-stream vs PCSX2's own run at a comparable moment (T47/T65 references). View every triple; table what differs and which side (ours-GS vs upstream vs same). Frames stay in scratch; the table in git.
Budget: ≤ 2 boots (one slot each), gsrunner jobs as needed, 3 h. No fork changes. Deliverable `local/research/PX1/REPORT.md` + the fixed converter; commit `[PX1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push.
