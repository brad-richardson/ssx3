# RP1 notebook (append-only)

Worker: Claude Code (Opus 5.5), exploratory. Box 3 h from 16:11 EDT (ends ~19:11).

## 16:11–16:20 setup
- Read brief + RR1/RD1/DK1/ST1/PX1/HR1/G46, facts, orchestration §3.
- Fork worktree `~/dev/ssx3-work/RP1/PS2Recomp`, branch `rp1-polish` from fork `ssx3` `8559ab9`.
- Codegen: APFS clone of F4's (unpromoted, TC1 vf0) codegen → `RP1/codegen` (register_functions `8ea8ed43…`,
  sub_003FE828 `89953ba2…`). VU1 images `~/dev/ssx3-work/vu1gen-ssx3`. paraLLEl `F2/parallel-gs` `19d93b2`.
- Build: Release, det-hash tap ON, diag taps/logs OFF, `GS_SHADOW_PARALLEL=ON` (background).
- Reference plan: PCSX2 own run on bytesize from T65's race statefile (00:00:18, 2ND/2), no inputs, F8 every
  ~20 s; ours: FR1-R1 route (I26-FAST minus the down hold) det boot, snapshots, ≤ 600 s. Match by race clock + %.

## 16:12–16:22 build, PCSX2 reference, gallery boot queued
- Build rc 0 (637 steps). Dev commit (pending): `PS2X_FRAME_DUMP_EVERY=N` keeps one frame per N ticks
  (`upload-t<tick>.png`) so long boots don't PNG-encode every present. Runner `bin/runner-base`
  `c77898b6…264e6b` (2 reads). Suite from worktree root **650/650** rc 0.
- PCSX2 own run (bytesize, `rp1-pcsx2.sh`): pcsx2-qt (T65 build) `-statefile t65-race-state` (00:00:18),
  no inputs, F8 every 20 s. Runs ~0.3× race-clock per wall-s under Xvfb. Shots 00:25 (12 %), 00:30 (14 %),
  00:34 (17 %), 00:39 (19 %), 00:46 (23 %, ice tunnel). Rider = default (red/black top).
- Driver `rp1_boot.py` (F4 driver + `--route fr1r1`, `--dump-every`, `--dump-ticks`, `--wall ≤590`).
- Boot g1 (FR1-R1, dump every 300 ticks) waiting: F4-2b speed pair holds all four slots (16:17).

## 16:22–16:28 first gallery frames
- g1 (FR1-R1) stopped at tick 4095: det-hash's 4096-line cap tripped the driver's hash_error bound. Added
  `--hash-every`; g2 relaunched with hash every 4 ticks (slot 1). Frames t1800–t3900 viewed (00:01–00:35).
- PCSX2 rp1a 14 shots viewed (00:18–01:31, 9–44 %). rp1b (30 shots, 30 s period, 880 s cap) running on bytesize.
- **Candidate D1:** t2400 (00:00:11, 14 MPH, spray over the rider) shows a **hard-edged translucent rectangle**
  of spray below the rider; PCSX2 spray (shots 00:34, 00:46) is soft-edged. Hypothesis: particle sprite
  texture alpha (PSMT8H/4HH CLUT alpha, TEXA, or wrong texture) — RR1 noted PSMT8H particle classes.
- c1: GS capture boot to 2401 (I26, slot 4) for the spray draw census.

## 16:28–16:35 gallery g2 + matched pairs; the carve trail
- g2 (FR1-R1, hash every 4, dump every 300): wall cap 590 s at tick ~11,700 (race 00:02:46, 69 %). Race clock
  ≈ (tick − 1740)/60 s. Our rider is slower than PCSX2's (14 % at 00:41 vs 19 % at 00:39), so pairs are matched
  by progress %.
- Pairs viewed (`pairs-1.png`, `pairs-2.png`): 13/14 %, 19/19 %, 23/23 %, 27/27 %, 31/30 %, 35/35 %, 39/40 %, 45/44 %.
- **D2 (most visible): the carve trail is missing.** PCSX2 draws a bright white raised groove behind the board in
  nearly every riding frame (00:25, 00:30, 00:46, 00:57, 01:31); ours never shows it (27 %: PCSX2 wide white trail,
  ours faint spray only). At t2398 our translucent "rectangle" sits where the trail should be.
- c1 capture (tick 2398) draw list: trail = TBP 14281 CT32 128×64 strips, a dest-alpha stencil sequence:
  #286/287 alpha-only (FBMSK 0xFFFFFF) A=0, Z ALWAYS, no Z write → clear dest alpha;
  #288/289 alpha-only, Z GEQUAL, **FBA=1** → mark visible trail alpha;
  #290/291 alpha-only, Z ALWAYS, **DATE=1 DATM=1**, Z write → trail depth where marked;
  #292–301 textured RGBA, Z GEQUAL, FBA=1, Z write; #302/303 textured, **DATE=1 DATM=0**.
- CT32 spray textures (12713/12841) resident in the race are soft-edged (edge alpha ≈ 0–1) in the upload data:
  the rectangle isn't the spray texture.
- CPU-backend replay of c1 (PPM 2397–2399) running to split backend vs stream.

## 16:35–16:45 trail = stream fault (vertex colours zero)
- CPU-backend replay of c1 (`ps2x_tests` GS replay, PPM 2398) shows the **same** translucent box and no
  trail as paraLLEl → not a backend bug; the fault is in the GS stream (`cpu-vs-par-2398.png`).
- PCSX2 own race dump (T48b, vsync 1): the same trail sequence exists (TBP 14313, same TEST/FBA/DATE passes).
  Vertex colours: **PCSX2 every trail vertex RGB ≈ 0x6E–0x77, A = 0x7F** (textured pass);
  **ours: fans RGBA = 0 on every vertex, strips mostly 0** (R 0–118, A 0–127 over the batch).
  With A = 0 the textured trail blends to nothing, and the DATE/FBA passes leave the box outline.
- PCSX2 T48b rp1b shots cover 9–85 %; trail visible throughout.
- Fork: committed dev probe `f233fc5` (RD1 1f3180d cherry-pick) + `edce9dd` (FRAME_DUMP_EVERY).
- Probe boot p1 (tick 2398, VU1 interpreter, XGK dumps at trail p1 ordinals 794/796/812/814/816, RAM snapshot).

## 16:45–16:50 mechanism named, fix landed
- Probe p1 (tick 2398, VU1 interpreter): trail input arrives as V4_32 [ST, RGBA ints, XYZW] with RGBA
  0x6E–0x7A / A 0x7F (= PCSX2's output colours). VU1 output (XGKICK 812 dump, row 970) RGBAQ = 0 while ST/XYZ
  match the capture → colour lost **inside VU1 program 0x3a08**.
- Wrote `rp1_vudis.py` (VU upper+lower disassembler over T65 micro memory). 0x3a08 interleaves the trail's two
  rails, ramps alpha (ITOF0.w / MUL.w / FTOI0.w) and copies each vertex with **`MAX.xyzw vf09, vf04, vf04`** /
  `MAX.xyzw vf06, vf02, vf02` before storing, then branches to the shared transform/clip routine 0x12b8.
  The final pair is stored without MAX (explains the few non-zero strip vertices).
- Ours: `execUpperImpl` normalizes every operand (`normalizeOperand`: exponent 0 → ±0) before MAX/MINI, so
  integer colour words (denormal bit patterns) become 0. PCSX2 `VUops.cpp:791` fp_max/fp_min: raw bits,
  signed-integer order, no flush.
- Fix `9bfd4aa` (fork `rp1-polish`): `vuMinMaxBits` for MAX/MINI/MAXbc/MINIbc/MAXi/MINIi. Test "RP1: MAX/MINI
  compare raw bits…": red 650/651 on unfixed code (`suite-red.log`), green **651/651** (`suite-green.log`).
  Runner-dir check empty. `bin/runner-fix` `3a5a8367…` (×2).
- Boots: hA (runner-probe = same tree minus the fix) / hB (runner-fix), det-hash every tick to 2400, frames
  2098/2398/2399; g3 = after-gallery FR1-R1 (590 s).

## 16:50–17:00 validation
- Det-hash A/B (hA runner-probe vs hB runner-fix, I26, ticks 1..2400+): `gb8_hashdiff.py` first_diff=1756,
  **vu1Data only**; rdram/scratch/eeCycle/vu1Code identical at every one of 2,458 ticks (`hashdiff-hA-hB.txt`).
  Guest logic untouched; tick 1756 = first trail draws of the race.
- Frames hA/hB 2398 (`ab-2398.png`): after = white raised carve trail from the board to the camera (PCSX2 look),
  translucent box gone. hA/hB frames sit one presented frame apart (trick counter 180 vs 190 at 2098:
  racy present latch), so whole-frame pixel diffs show camera motion; used a draw-level diff instead.
- Draw diff c1 (before) vs c2 (after) at 2398 (`rp1_primdiff.py`, `primdiff-2398.txt`): 27,158 prims both;
  **only vertex RGBA differs, on 1,014 prims**: 954 trail prims all-zero before → none after (TBP 14281
  passes + untextured stencil passes), plus 60 prims of a distant trail at TBP 12777 (A 0–14 → 0–128).
- CPU-backend replay of c2 (PPM 2398) running for a same-tick before/after image.

## 17:00–17:10 gallery after, report
- g3 (after, FR1-R1): tick 13,000 in 590 s. Before/after/PCSX2 triples at 13/14/27 % (`triples-1.png`): trail
  matches PCSX2; the 00:35 bubble and the 00:41 pale boxes are now the lit/shaded trail. After vs PCSX2 at
  42–65 % (`triples-2.png`): no further rendering difference found by eye.
- Same-stream CPU replay before/after at 2398 (`ab-2398-replay.png`): 25,233 px changed, all in the trail region.
- Pop-in re-check on c2 (2200–2300): only animated PSMT8H particle pages + one 29-prim CT32 class vary.
- EE macro VMAX/VMINI (`Ps2VuMax`/`Ps2VuMin`) already raw-bit; only micro mode was wrong.
- VU1 disassembly listings are game-derived: kept in scratch, not committed.
- REPORT.md written.
