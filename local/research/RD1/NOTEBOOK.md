# RD1 notebook (append-only)

Worker: Claude Code (Opus 5.5), exploratory, 3 h box from 11:02 EDT 2026-09-25.

## 11:02–11:08 — offline analysis of existing captures (no boots, no builds)

- UV1 Part 2 (V2/V3 z/w per PCSX2) already ran: frames at 1091/1800/2100 pixel-identical
  to base. So the UNPACK lanes lead does not change the rider on this route.
- Input: UV1 boot A1 capture (base `0ed07c4`+counters, det, I26-FAST, Zoe),
  hardlinked as `~/dev/ssx3-work/RD1/in/uv1-A1.gs.stream`. Tool `rd1_draws.py` (batch census
  on the E51/RR1 decoder, adds full per-vertex RGBA, FBA, ZBUF, q range, bbox).
- Tick 1799 (race 00:00:01): player rider = the tfx=3 (HIGHLIGHT2) tri-strip batches at
  screen centre, q ≈ 0.0025–0.0034 (nearest object). Rival = tfx=3 batches at x≈430–460.
- **Same-rider structure in PCSX2** (`RR1/ref/pcsx2-race.gs`, T65 race dump, vsync 0 and 3):
  player batches n = 1849, 80, 118, 353, 484, then 53, 411 (alpha 0x44 pass). Ours at tick
  1799: 1849, 80, 118, 353, 449, then 53, 411. Same program structure, same texture layout.

| batch (n) | PCSX2 bbox (px) | PCSX2 vertex RGB / A | ours bbox (px) | ours vertex RGB / A |
|---|---|---|---|---|
| 1849 | 47×70 | 54–255 / 0–95 | 38×37 | 122–171 / 35–75 |
| 80 | 44×31 | 79–255 / 0–72 | **0×0 (one point)** | **149,154,184 / 71 constant** |
| 118 | 78×52 | 56–255 / 0–93 | **0×0 (one point)** | constant |
| 353 | 9×14 | 54–255 / 0–95 | **1×5** | constant |
| 484 / 449 | 51×59 | 54–255 / 0–95 | 41×33 | 147–150 / 70–71 |
| 53 | 47×30 | 68–255 / 0–95 | 38×25 | constant |
| 411 | 18×17 | 60–255 / 0–95 | **2×7** | constant |

  Rival in ours (same tick): lit per vertex (53–255 / 0–95), shapes normal.
- Wireframe of our tick-2099 player batches (`out/geo-2099.png`): a stick figure — most
  vertices collapse onto a few points, limbs are thin spikes. Reading: skinning output with
  the per-vertex **position offset ≈ 0 and normal ≈ 0** (verts land on bone origins / along
  bones; lighting = ambient only → one constant colour). Bone matrices look sane (limbs point
  the right way). So the fault is upstream of the GS: the player's vertex positions/normals
  reach (or are read by) the VU1 program as zero.
- Candidates now: (a) EE-side vertex buffer for the player never filled / zero,
  (b) VIF1 UNPACK of that data wrong (format/mask/ROW), (c) VU1 program for the player reads
  the wrong address. Next: runtime probe at one race tick logging UNPACK/MSCAL/XGKICK with
  data non-zero counts, mapped to capture packets by PATH1 ordinal.

## 11:08–11:13 — disk, worktree, probe

- 11:07 disk_budget read 202.3/200 GB (not from RD1: my capture is a hardlink, worktree 22 MB).
  Told the orchestrator; it freed space (151.4 GB) and said resume.
- Worktree `~/dev/ssx3-work/RD1/PS2Recomp`, branch `rd1-rider` from `0ed07c4`. Build dir
  `~/dev/ssx3-work/RD1/build` (same flags as UV1: Release, diag taps OFF, paraLLEl from
  F2 clone `19d93b2`).
- Probe (default-off, new header `ps2_rd1_trace.h`): `PS2X_RD1_TRACE=<file>` +
  `PS2X_RD1_TICK=<n>` logs for one vsync: VIF1 DMA tags (`dma`), deliveries (`dlv`), every
  VIF1 command with offset (`cmd`) and the E37 `vif` line (UNPACK format/addr/data words),
  `mscal` (ordinal, startPC, TOP), `xgk` (ordinal, bytes, VU src row); VU1 data memory dumps
  at chosen xgk ordinals (`PS2X_RD1_XGK_DUMP`) or MSCAL ordinals (`PS2X_RD1_DUMP`).
- Capture mapping (`rd1_p1map.py`, UV1 A1, tick 1799): player batches = PATH1 packets
  (= xgk ordinals) **1237–1311**; rival = **1312–1348**. 1,797 PATH1 packets in the tick.

## 11:14–11:20 — probe boot P1 (tick 1799) — mechanism narrowed to EE-side bone matrices

- Build `~/dev/ssx3-work/RD1/build` (probe only, default-off), suite **612/612 rc=0**
  (`suite-probe.log`). Runner `runners/ps2EntryRunner-probe` sha256 `539e944f…f2f7da`.
- Boot P1: `rd1_boot.py --label P1 --stop-tick 1802 --no-capture --once-ticks 1800`
  `PS2X_RD1_TICK=1799 PS2X_RD1_XGK_DUMP=1240,1286,1320`; slot 1, bound=target, 46 s,
  gs_fatal null. Trace 5.5 MB: 1,797 `xgk` = the capture's 1,797 PATH1 packets, and the
  sizes match packet for packet (1237: 2752, 1238: 2848, …) → ordinals are aligned.
- Player segments (xgk 1237–1311) vs rival (1312–1348): **same UNPACK formats** (V4_32 1x1
  header, V4_16 3x1, V3_16 + V3_32 3x1 with mask 0x40404040 w←ROW) and same programs
  (0x0/0x50/0x30; player also 0x398). Player vertex data is real: V3_32 positions
  (-46.3, -15.0, -6.9 …), V3_16 normals non-zero. → not an UNPACK problem.
- **VU1 data memory** at xgk 1240 (player) vs 1320 (rival), rows 17–116 = 25 bone matrices
  (4 QW each): player rows 17/18/19 (and every 4k+1..4k+3) are **all zero**, only the 4th
  row (translation, world coords ≈ (2850, -45485, 95610, 1)) is set. Rival: full 3×3
  (0.02, 0.21, 0.49 …) + translation. Rows 0–16 (view/proj, lights) identical-shaped in both.
  Zero 3×3 + sane translation explains everything: vertices land on bone origins (stick
  figure), normals transform to 0 (flat ambient colour 0x47b89a95).
- Source: the matrix UNPACK (`6c640011`, V4_32 num=100 addr=17) comes from DMA CALL tag
  at 0x646280 → CNT qwc=102 at **EE 0x624d50, data 0x624d60**. So the matrices are built
  wrong on the EE side (or by VU0 macro code) before DMA. Not UNPACK, not VU1, not GS.
- Also seen: several earlier addr=17 uploads in the same tick with zero 3×3 and signed
  zeros (0x80000000), and other uploads with full rotations (rival etc.).
- Next: diag-taps build + E44 EXTRA watch on 0x624d60 (row0.x) and 0x624d90 (row3.x) at
  tick ~1799 to get the writer pc/ra/fn.

## 11:20–11:55 — chasing the zero rotation back to its producer (boots W1–W7, R1)

All det I26-FAST boots, one slot each, stop 1800–1801; runners in `~/dev/ssx3-work/RD1/runners/`.

| step | boot | tool | finding |
|---|---|---|---|
| 1 | W1 (taps runner `348c5ac4…`) | E44 EXTRA 0x624d60… | the DMA-list stores go through the fast path (no pc); E44's own SPR watch shows `store128` to 0x70000000 at pc **0x386cc0** (ra 0x3108a0) writing 0 / -0 words |
| 2 | W2 (probe) | `PS2X_DIAG_WATCH` on the list words | copier: pc 0x37ac2c–0x37ac6c in sub_0037A430 copies 64-B matrices `palette[idx]` into the VIF list; palette base = `[s0+0x13E8]` |
| 3 | W3 (probe3: diag watch + GPR snapshot, `PS2X_RD1_WATCH_REGS=1`) | regs at 0x37ac6c | palette base **t0 = 0x70000000** (scratchpad), v0 = 0x70000380 |
| 4 | W1 E44 regs at 0x386cc0 | — | sub_00386128 = skin blend: `pal[i] = Σ (w·0.01) · Bone[idx]`, I=0x3C23D70A; `a1 = 0x4fc420` (bone world matrices). Player pass: s0 0x1465c40, 158 entries → zero rows; rival pass s0 0x16d2360 → real rotations. Translation w = 0.99999994 → weights/I fine |
| 5 | R1 (probe2: RDRAM/SPR dump at tick 1799) | RAM scan | 0x4fc420 bone 28 has rows 0–1 zero, translation set |
| 6 | W5 | watch 0x4fcb20.. + regs | writer sub_00310640 @0x31076c: `out = B × A` (4×4 VU0 macro), A = [s1+0x34] (0x149a690, real rotations), **B = [s1+0x38] = 0x158f240** |
| 7 | R1 dump | B bone 0/1/28 | B rows 0/1 = 0, row 2 = (0,0,-1) or denormal junk, row 3 = (0,0,0,1) → the per-bone bind/pose base matrices are broken |
| 8 | W6 | watch 0x158f240.. whole boot | last writer before the race: sub_0030DBD0 @0x30e708/0x30e6c4 (+ transpose swc1 at 0x30e794–0x30e7b0), **guest thread 3** (loader), ra 0x30e4dc |
| 9 | static | ee-at 0x30e578.. | textbook quaternion→matrix on VU0 macro: `vaddw.xyz vf1, vf0, vf0w` (=1,1,1) then `1 − 2yy − 2zz` style rows via vsuba*/vmsub* .x/.y/.z; codegen for these ops checked, correct |
| 10 | W7 (probe4: + VU0 vf0–15/ACC in the snapshot) | regs at 0x30e708 | **vf0 = (0,0,0,0)**, vf1 = (0,0,0,0) on thread 3's context; quaternion vf4 = (0,0,0,1) |

**Root cause:** `R5900Context()` (ps2_runtime.h) memsets itself and sets only Q; `vu0_vf[0]` stays
(0,0,0,0). The runtime patches vf0 = (0,0,0,1) only for the main context (`ps2_runtime.cpp:876`)
and the VU0 state restore (`:331`). `EeScheduler::startThread` gives every guest thread
`R5900Context{}` → vf0 = 0 on all non-main threads. SSX 3 builds the player's hi-detail rider
bind matrices on loader thread 3 → `vf1 = vf0 + vf0.w = 0` → every "1 − …" diagonal term is
lost → rows 0/1 zero (identity quaternion (0,0,0,1) gives all-zero rows, row 2 picks up −1 from
other paths) → skin palette → VU1 collapses the rider. The rival's matrices are built where
vf0 is right (not on that thread), so it renders.

Fix candidate: set `vu0_vf[0] = (0,0,0,1)` in the constructor. Unit test (kernel tests):
default-constructed context and a StartThread'd thread both have vf0 = (0,0,0,1).
Red: 612 pass / 1 fail (the new test). Green: 613/613 rc=0 after the full rebuild (header is in codegen).

## 11:55–12:08 — fix, validation, commit

- Fork `rd1-rider`: `51c759b` fix + test (2 files, +28), `1f3180d` default-off probe (5 files,
  +280/−2). Suite green 613/613. Runner-dir diff vs 14b1e5cb empty.
- V1 (fix runner `8b844cf9…`): tick 1090 fnv f86140f2 = base; 1800/2100 differ; at 2100 the
  full Zoe model is visible (hair, red top, pants, board). Capture: player batches lit
  (RGB 53–255, A 0–95) with PCSX2-like sizes; rival batches unchanged.
- D1 (fix + det tap `80e94f05…`) vs UV1 A2: first diff tick 231 (rdram, transient to 255),
  then 1543→end (race load: rdram, later vu1Data/scratch); eeCycle identical everywhere.
- M0/M1: Brad's save (`E55D16/mc0` copied into the lane dir), I26-FAST +3337 ms. Race at 2300:
  pre-fix Mac is a faint wisp (Brad's "mostly missing"); fix = solid Mac.
- Checked other contexts: thread/invocation/IOP contexts default-construct (covered); callback
  contexts copy callers. Guest `lqc2 $vf0` at 0x3fe9bc (sub_003FE828, VU0 reg-file restore)
  can still write vf0: gap, recompiler change.
