# IS1 — first real iOS speed numbers (iPad), play settings (muse, 2 h)

## Goal
We've never measured iOS race speed cleanly (F5–F7 iPad launches were diagnostic: console-pty + vsync-rate overhead). Brad plays on the iPhone. Get clean iPad race rates for the current iOS build's settings and a small A/B, so iOS gets its own speed track. **iPhone: never launched** (install-only rule, `AGENTS.md`).

## Facts
- Current iOS build = F7 (`local/research/F7/REPORT.md` Part 2; fork `a5e5940`, bundled env `local/research/F7/ps2x.env`: 4× SSAA + hi-res + pipelined + zero-copy + `PS2X_MTVU=1 PS2X_VU1_BLOCKS=1`). Fork `ssx3` is now `b97b241` (adds the SIMD FMAC core, on by default; VU0 recompile off). Recipe `~/dev/ssx3-work/F6/ios/build-install.sh` (MoltenVK at `~/dev/ssx3-work/moltenvk-1.4.2`, VU0 dir wiring added by VR3).
- iPad launch/probe scripts: F7's `ipad-probe.sh`/`ipad-run.sh` (read the live container path first; fresh-card `-e PS2X_MC_ROOT`, never Brad's `Documents/mc0`).
- Clean rate: measure race vsyncs/s from `[vsync-rate]` lines **without** console-pty capture overhead if possible (log to a file in the container and pull it after), unpaced (`PS2X_UNPACED=1`), I26-FAST, stop ~t4500. Say what overhead remains.

## Runs (iPad only; ≤ 8 launches; let it cool between runs, record battery/thermal state if readable)
1. Build a device app from fork `b97b241` (one build). 
2. A/B pairs (ABBA where it matters): **A** F7 settings (4×+hi-res+MTVU+blocks); **B** A + `PS2X_MTVU_LAG=1`; **C** A at 1× (no SSAA/hi-res); **D** A with `PS2X_MTVU=0`. Report race rate per leg, per-phase table, and one race frame viewed per leg.
3. Restore the iPad to Brad's state after (`deploy-ios.sh ipad`, save byte-identical).

## Deliverable
`local/research/IS1/REPORT.md` (pins, SHAs, method incl. remaining overhead, the table, frames, gaps) + `[IS1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push. Hand back the table; don't conclude.
