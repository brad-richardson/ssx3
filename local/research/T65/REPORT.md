# T65 REPORT — PCSX2: race-time transform inputs (the healthy side of E50)

Brief: `local/muse/prompts/T65.md`. Worker: Claude Code (Opus). Tables and
receipts only; the orchestrator decides. Read first: `AGENTS.md`,
`local/AGENTS.local.md`, `local/research/T48/REPORT.md` (§T48-6),
`local/research/E47/REPORT.md` (Part 2), `local/muse/prompts/E50.md`.

## T65-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Per-vsync PATH1 xy/z box + on/off/straddle counts over a race window | DONE: `T65_BOX` every vsync from boot to kill (27,159 lines); race and SC tables in §T65-4 |
| 2 | VF00–31 + whole VU1 data memory at the first world program of one race vsync; decode matrix-like 4×4 blocks | DONE: every VU1 program start over 3 EE vsyncs was dumped (2,074 race starts); tables in §T65-5 |
| 3 | Same dump at Select Character (control) | DONE: 1,833 SC starts over 3 EE vsyncs, same boot |
| 4 | Race VU1 startPC list | DONE: §T65-6 |
| 5 | Preservation | DONE: G13 replay 7/7 md5 pins + HWSTAT exact, 0 T65 lines (§T65-3) |

Budget: **1 build of ≤2, 1 capture of ≤3**, about 1 h 15 min of 4 h, bytesize
about 1.8 GB new of the 3 GB cap (the capture emulog alone is 1.54 GB, §T65-7).

What the tables show (observations, not a verdict):

- **PCSX2's race prim box is pinned to the same guard band.** Over every race
  vsync the non-ADC PATH1 prim box is XYOFFSET-relative x −768.5..1279.5,
  y −800.5..1247.5. Adding XYOFFSET (1792, 1824) gives **1023.5–3071.5 on
  both axes**: the same numbers E47 reports for the recomp. The per-vertex box
  including ADC vertices spans the whole 0..4096 range. The SC box stays
  inside the viewport (1741.06–2329.88 × 1765.5–2324.69).
- **In PCSX2, 2,700–3,060 race prims per vsync are fully off-screen**
  (median 2,997 over the race), alongside about 16,700–16,900 on-screen and
  about 850–900 straddling ones (race window 26714–26723). At SC, 1–65 are
  off-screen.
- **The viewport transform explains the 1023.5/3071.5 bounds.** VU1 data
  qw 0x004/0x005 hold scale (1024, −1024, −8388467.5) and offset (2047.5,
  2047.5, 8388467.5), so NDC ±1 maps to 1023.5 and 3071.5.
- **The camera (view×projection) matrix is at VU1 data qw 0x000–0x003** in
  both the race and SC 3D programs. It is identical in the x, y and w columns
  across every camera-carrying program in a vsync. There are two z-column
  variants (A = the first ~11 programs of the vsync, B = the rest). The
  healthy invariants are: columns x, y, w mutually orthogonal (dots ≤ 2e-8),
  |w| = 1.000000, |x| = 0.266262, |y| = 0.310638 (y/x = 1.1667) in the race
  and 0.536127 / 0.625481 (same 1.1667 ratio) at SC. None of the blocks
  contain NaN, Inf or denormal values.

## T65-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`), T64 working tree + T65 hunks |
| Pre-T65 (T64) qt | `626be79691b318211206c85f60cc79879d5a3405559d81558042ea05df12360f` (= T64 pin; copy in `/home/brad/pcsx2-g7/pre-t65/pcsx2-qt.t64`) |
| Pre-T65 file SHAs | Counters.cpp `0aada58be35681113a282b80a36e3cf87291e816fb5c9410bef559e088d412b9`, GS.cpp `20a473e01ad82b4fb4f24fe690356d31c141b37116b61e580d54648a609dedfc`, GSState.cpp `530d28fa3b24a5d0062b91ba53cf940ce411cdc18b56cf5084941a693028fe58`, VU1micro.cpp `dfa62898cfc52f954011ac1a5004cedf17007c1c12c4a8b79ca9c48a9283192c` (copies in `pre-t65/`) |
| T65 qt | `e85ddbfca5e1c4768e3e8e6da097a50839932c41ae4603953e270f53a47b1696`, 131,352,816 B |
| T65 gsrunner | `042b80af6fbef45ec61c190d43a25072ef80dedec87669e68a704442f8e41d62`, 90,858,104 B |
| Patch | `t65-patch.diff` sha256 `dbb9ea05c98aff13cfb7fcf2c3a4729996e972b569a0d159f2f979e6360287b6` (235 lines, 4 files; T65 hunks only, diffed against `pre-t65/`) |
| Config | `dat-t48` unchanged: EE rec, VU0 rec, **VU1 interpreter, MTVU off** (`vuThread = false`, `EnableVU1 = false`); ISO `SSX 3 (USA).iso`; `T48_MODE mtvu=0` logged |
| SC dump | `t65-vu1-1.bin` 31,479,264 B sha256 `7777e70a693a4803fd687dcfc4c67549fb06fb265af59aebc6c76212fc749e46` (EE vsyncs 12235–12237, 1,833 starts) |
| Race dump | `t65-vu1-2.bin` 36,063,936 B sha256 `bf61f3cd217744d2f867e4b0dd4545c5dcc5b46879e851948ef09e9a25211c37` (EE vsyncs 26718–26720, 2,074 starts) |
| Race GS dump (T48 trigger, 8 vsyncs from 26784) | `SSX 3_SLUS-20772_20260923162250.gs.zst` 4,675,130 B sha256 `aa56234aa9543d32c1303f482fa557461aec4b6eb8e0061aa760ba961ba4e475` (not analyzed here; a receipt for E50) |
| Race statefile | `/home/brad/pcsx2-g7/t65-race-state` 14,281,263 B sha256 `7d639f1a318476ee5ce5b3b95377b6695eb3f327ab44e6d931617b092e14e7d6` (F1 in the race, after both dumps and the race F8) |
| Capture emulog | 1,539,539,828 B sha256 `1a583778075b0e03f59d92bd48b498ad7eb47c559788b6aafec6bd54cdd6ee58` (left in place on bytesize; the next capture rotates it) |

Both `.bin` SHAs and the `.gs.zst` SHA were read twice (bytesize and mini) and
a third time on the share mirror. All match.

## T65-2. The patch (`t65-hook.py` → `t65-patch.diff`)

`t65-hook.py` checks all 9 anchors (count == 1, no prior T65 text) before it
writes, and it applied on the first try. It adds counters and log lines only;
no renderer, EE, VU or timing behaviour changes.

| Hunk | File / anchor | What |
| --- | --- | --- |
| T65-S1 | `GS/GSState.cpp` after `g_t48_curpath` | globals: `g_t65_on`, counters, vertex box, prim box, z range, last OFX/OFY/scissor, context-change count |
| T65-S2 | `GSState::VertexKick` after `xy_tail++` | every kicked vertex while `g_t48_curpath == 1` (PATH1, T48 mapping): **absolute** raw 12.4 x/y min/max and z min/max, ADC included; other paths counted separately |
| T65-S3 | `GSState::VertexKick` before PCSX2's scissor/cull test | each completed prim (n = 1/2/3 verts; fans use the head vertex): ADC prims are counted and skipped. For the rest the XYOFFSET-relative bbox is taken from the vertex buffer and classified against the context **SCISSOR** (px [SCAX0, SCAX1+1] × [SCAY0, SCAY1+1]). **off**: bbox doesn't touch the rect; **on**: bbox inside it (edges inclusive); **straddle**: the rest; **zero-area**: x0 == x1 or y0 == y1 (a subset of the three). Counting happens **before** PCSX2's cull, so culled prims are included |
| T65-G1/G2 | `GS/GS.cpp` `GSvsync` (after the T48 vsync mirror; runs regardless of `/tmp/t48-arm`) | prints `T65_BOX` for the vsync that just ended when `g_t65_on`, resets, re-reads `/tmp/t65-arm`; `/tmp/t65-vu-now` is consumed and bumps `g_t65_vu_req` (`T65_VU_REQ`) |
| T65-C1 | `Counters.cpp` `VSyncStart` | `g_t65_ee_vsync++` (EE-thread vsync counter) |
| T65-V1/V2 | `VU1micro.cpp` `vu1ExecMicro`, after the T48 begin-record | one binary file per request (`/home/brad/pcsx2-g7/t65-vu1-N.bin`). Every program start in EE vsyncs [req+1, req+4) writes a record: an 80 B header (seq, EE vsync, GS vsync mirror, TPC, VU1.cycle, T48 xgkick counter, VIF1 top/tops/itop/itops/base/ofst/DBF, FNV-1a of data and micro memory, has_micro), then VI[32], VF[32], ACC, 16 KiB data memory, and 16 KiB micro memory when its FNV changed. Plus one `T65_VUREC` line per start and `T65_VU_ARM`/`T65_VU_DONE`. Needs MTVU off (`THREAD_VU1` returns earlier) |

The per-program xgkick count is `xg[next start] − xg[this start]`, using the
T48 `_vuXGKICK` counter. `mfnv` hashes the whole 16 KiB micro memory, so it
names the loaded microcode set. It is not comparable to E47's per-MPG-upload
FNVs.

## T65-3. Preservation

`t65-replay.sh`: the T65 gsrunner on the G13 rich dump, with no arm files present.

| Check | Result |
| --- | --- |
| 7 PNG md5 | `b7a3e8db a7929218 bb8b1d85 817e934f 817e934f 85cf3599 85cf3599`: **7/7 = the T48/T64 pins** |
| HWSTAT | 791 draws / 37 passes / 0 barriers / 14 copies / 320 uploads / 6 readbacks: **exact** |
| T65 lines in replay emulog | **0** |

The live route is a behaviour check too: every T48 gate passed on try 1 with
T48-range scores (TITLE 0.33, MENU 0.59, SC 0.38, ZC 0.36, SP 0.39, SM 0.41,
SC settled 0.55, race depart 11.25). The F8 frames show a normal SC (Zoe
rendered) and a normal race (terrain, trees, rider, HUD 2ND/2, 00:00:18,
64 MPH): `t65-shot-t65a-sc.png`, `t65-shot-t65a-race.png`,
`t65a-race-live.png`. I did not re-run the T48 two-leg live-frame proof (no
extra boot), and the taps are read-only.

## T65-4. Box and on/off counts (definitions in §T65-2)

`vx/vy` are absolute px (raw/16) over **all** PATH1 vertices, ADC included.
`prim px/py` are XYOFFSET-relative px over non-ADC prims. `of` is OFX/OFY in
px, `sc` is SCISSOR, and `ctxchg` counts prims whose offset/scissor differs
from the previous prim's. Every PATH1 prim in both windows had OF 1792,1824
and SC 0..511,0..447.

Race window (VU dump requested at GS vsync 26716, a few seconds before the 00:00:18 race F8):

| vsync | p1 verts | vx | vy | z | on | off | straddle | zero-area | adc | prim px | prim py | ctxchg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 26714 | 27666 | 53.06..4087.50 | 5.13..4082.25 | 0..16777215 | 16662 | 2703 | 856 | 140 | 4924 | −768.50..1365.88 | −800.50..1247.50 | 7 |
| 26715 | 27537 | 21.69..4088.00 | 8.44..4077.13 | 0..16777215 | 16708 | 2783 | 837 | 138 | 4736 | −768.56..1279.50 | −800.50..1247.50 | 7 |
| 26716 | 27567 | 5.19..4067.13 | 1.06..4089.00 | 0..16777215 | 16739 | 2722 | 854 | 142 | 4758 | −768.50..1279.50 | −800.50..1247.50 | 7 |
| 26717 | 27660 | 9.00..4091.19 | 1.31..4046.06 | 0..16777215 | 16766 | 2691 | 866 | 153 | 4866 | −768.56..1345.69 | −801.13..1247.44 | 7 |
| 26718 | 27645 | 8.88..4084.06 | 45.63..4079.63 | 0..16777215 | 16767 | 2653 | 880 | 139 | 4879 | −768.50..1395.00 | −800.50..1247.50 | 7 |
| 26719 | 28115 | 15.88..4069.13 | 5.50..4020.13 | 0..16777215 | 16770 | 3063 | 895 | 135 | 4896 | −768.50..1279.50 | −800.50..1247.50 | 7 |
| 26720 | 28167 | 19.94..4071.38 | 12.56..4064.19 | 0..16777215 | 16816 | 3003 | 898 | 157 | 4924 | −768.56..1279.50 | −800.50..1247.44 | 7 |
| 26721 | 28237 | 1.50..4093.94 | 11.94..4064.44 | 0..16777215 | 16865 | 3060 | 880 | 162 | 4927 | −768.50..1279.50 | −800.50..1247.44 | 7 |
| 26722 | 28058 | 9.00..4066.75 | 13.38..4092.56 | 0..16777215 | 16898 | 2975 | 897 | 147 | 4820 | −768.56..1279.50 | −801.44..1247.50 | 7 |
| 26723 | 28041 | 3.13..4082.13 | 9.81..4094.56 | 0..16777215 | 16942 | 2895 | 912 | 138 | 4833 | −768.50..1279.50 | −800.50..1247.50 | 7 |

Whole race, GS vsyncs 25600–27178 (1,579 vsyncs, from race onset to kill):

| metric | min / median / max |
| --- | --- |
| prims on-screen | 9,591 / 20,382 / 29,644 |
| prims off-screen | 1,321 / 2,997 / 5,652 |
| prims straddling | 474 / 719 / 1,453 |
| zero-area prims | 49 / 180 / 461 |
| ADC prims | 4,298 / 7,822 / 10,497 |
| PATH1 vertices | 19,382 / 33,700 / 46,822 |
| prim px (relative) over the race | −896.44 .. 1407.44 (x), −927.88 .. 1374.75 (y) |
| most common per-vsync prim box | px −768.50..1279.50 × py −800.56..1247.50 (525 vsyncs); the next two are the same to ±1/16 px |

→ absolute non-ADC prim box, typical vsync: **1023.5–3071.5 × 1023.44–3071.5**.
Recomp (E47 Part 2): 1023.5–3071.5 × 1023.4–3071.5.

SC control (identical on every vsync 12230–12240):

| vsync | p1 verts | vx | vy | z | on | off | straddle | zero-area | adc | prim px | prim py | ctxchg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12232–12238 | 7900 | 1741.06..2329.88 | 1765.50..2324.69 | 0..16751937 | 5015 | 1 | 63 | 8–10 | 1294 | −50.94..537.88 | −58.50..500.69 | 0 |

SC over GS vsyncs 12000–12400: on 4,971–5,027, off 1–65, straddle 43–71;
absolute vertex box 1726.69–2380.75 × 1765.5–2324.69. Recomp SC (E47):
1741–2359 × 1799–2325.

## T65-5. Matrix tables

**Where the dumps come from.** One record per program start, so "the first
world program of the race vsync" can be chosen after the fact. The first start
of EE vsync 26719 is seq 684 (0x44e), and the first 0xd7 is seq 771. T48's
race census names 0x459/0x44e as the most-started race programs. Which
programs draw terrain is not established here. Per-start tables for every
group are reproducible with `t65-analyze.py mats <bin> <seq>`.

**Layout (same offsets at SC and in the race).** qw 0x000–0x003 is a 4×4
matrix (rows as stored). qw 0x004 is the viewport scale and qw 0x005 the
viewport offset. The 2D programs keep an ortho screen matrix at the same
place.

### 5a. Race: camera matrix, variant A (seq 684, EE vsync 26719, tpc 0x44e, microcode `a439a372`)

| qw | x | y | z | w |
|---|---|---|---|---|
| 0x000 | bd5eddf7 (-0.0544109) | 3e33bcf0 (0.175525) | 3f4ca5c0 (0.799404) | 3f4ca243 (0.799351) |
| 0x001 | be8572f9 (-0.260643) | bd161605 (-0.0366421) | be2ae2d3 (-0.166881) | be2adfe9 (-0.16687) |
| 0x002 | 31085370 (1.9838e-09) | 3e81dffc (0.253662) | bf13c7bf (-0.577267) | bf13c53a (-0.577228) |
| 0x003 | c6135c0f (-9431.01) | c6c9531e (-25769.6) | 46b285b0 (22850.8) | 46b286a6 (22851.3) |
| 0x004 | 44800000 (1024) | c4800000 (-1024) | cafffee7 (-8.38847e+06) | 00000000 (0) |
| 0x005 | 44fff000 (2047.5) | 44fff000 (2047.5) | 4afffee7 (8.38847e+06) | 00000000 (0) |

### 5b. Race: camera matrix, variant B (seq 771, same vsync, tpc 0xd7, microcode `1ec2db6c`)

| qw | x | y | z | w |
|---|---|---|---|---|
| 0x000 | bd5eddf7 (-0.0544109) | 3e33bcf0 (0.175525) | 3f4d0b23 (0.800951) | 3f4ca243 (0.799351) |
| 0x001 | be8572f9 (-0.260643) | bd161605 (-0.0366421) | be2b377c (-0.167204) | be2adfe9 (-0.16687) |
| 0x002 | 31085370 (1.9838e-09) | 3e81dffc (0.253662) | bf1410f5 (-0.578384) | bf13c53a (-0.577228) |
| 0x003 | c6135c0f (-9431.01) | c6c9531e (-25769.6) | 46b26a06 (22837) | 46b286a6 (22851.3) |
| 0x004 | 44800000 (1024) | c4800000 (-1024) | cafffee7 (-8.38847e+06) | 00000000 (0) |
| 0x005 | 44fff000 (2047.5) | 44fff000 (2047.5) | 4afffee7 (8.38847e+06) | 00000000 (0) |

Which programs carry which qw 0x000–0x005 (EE vsync 26719; 26718 and 26720
have the same pattern with the camera moved):

| programs (tpc/microcode) | qw 0x000–0x003 | qw 0x004 / 0x005 |
| --- | --- | --- |
| 0x44e, 0x459 (`a439a372`), first ~11 starts of the vsync (seq 684–697) | camera **A** | (1024, −1024, −8388467.5) / (2047.5, 2047.5, 8388467.5) |
| 0x44e, 0x459 later in the vsync (seq 888–1302); 0x134, 0x147 (`7e33f933`); 0xd7, 0xf2, 0xe0, 0xfb (`1ec2db6c`); 0x741, 0x257 (first 3) (`a439a372`); 0x22a, 0x0, 0xa, 0x6, 0x73, 0x2, 0x8, and 0x10/0xe late in the vsync (seq ≥ 951) (`405df496`) | camera **B** | same |
| 0x741, 4 starts (seq 860–863) | camera B | z entries 0 / 0 |
| 0x28c, 0x140 (`5ec94df5`) | camera B | z scale −524279.22 |
| 0x10, 0xe, 0x4 early (`405df496`, seq 698–759) | 2D matrix, z column 0, two variants in the vsync (first: x (−0.00954, −0.00520), y (0.00641, −0.00774), t (467.78, −202.39, 1, 1)) | (64, 64, 0) / (2048, 2048, 0) |
| 0x257 (`a439a372`), 32 later starts | ortho screen matrix (1/1280, 1/1097.14, 2; t −0.25, −0.21875, −1, 1) | (1024, **+1024**, …) / (2047.5, 2047.5, …) |

### 5c. SC control, first 3D program (seq 696, EE vsync 12236, tpc 0x22a, microcode `489f5136`)

| qw | x | y | z | w |
|---|---|---|---|---|
| 0x000 | bf093f99 (-0.536127) | 00000000 (0) | 3380419a (5.9724e-08) | 33800000 (5.96046e-08) |
| 0x001 | b3093f9a (-3.19556e-08) | 00000000 (0) | bf804199 (-1.002) | bf7fffff (-1) |
| 0x002 | 00000000 (0) | 3f201f88 (0.625481) | 00000000 (0) | 00000000 (0) |
| 0x003 | 36d67360 (6.39113e-06) | 00000000 (0) | 433e63ef (190.39) | 4347ffff (200) |
| 0x004 | 44800000 (1024) | c4800000 (-1024) | cafffee7 (-8.38847e+06) | 00000000 (0) |
| 0x005 | 44fff000 (2047.5) | 44fff000 (2047.5) | 4afffee7 (8.38847e+06) | 00000000 (0) |

Every SC 3D program (0x22a, 0x10, 0xe, 0x0, 0xa, 0x2, 0x8, 0x73, 0x6 on
`489f5136`) carries this block unchanged on all three vsyncs. The SC 2D
program 0x257 (`4a3ef372`, 85 starts/vsync, the first program of the vsync)
carries the ortho screen matrix (0.00078125, 0.000911458, 1; t −0.25,
−0.21875, 0, 1) with qw 0x004 = (1024, **+1024**, −8388467.5). In every SC
start I checked (seq 611, 696), 4-qword blocks from qw 0x011 in steps of 4
(0x011–0x014, 0x015–0x018, 0x019–0x01c, …) are z≈w perspective blocks
with translation-row w 463.6–473.7. Which object they belong to is not
established. See `an-mats-sc-611.md`.

### 5d. Column invariants (rows 0–2 as a 3×4; "col" = that component across the 3 rows)

| block | abs col x | abs col y | abs col z | abs col w | x·y | x·w | y·w | y/x | NaN/Inf/den |
|---|---|---|---|---|---|---|---|---|---|
| race ee 26718 seq 0 (A) | 0.266262 | 0.310638 | 1.000066 | 1.000000 | 1.29e-11 | 2.50e-09 | 1.15e-08 | 1.1667 | none |
| race ee 26718 seq 87 (B) | 0.266262 | 0.310638 | 1.002002 | 1.000000 | 1.29e-11 | 2.50e-09 | 1.15e-08 | 1.1667 | none |
| race ee 26719 seq 684 (A) | 0.266262 | 0.310638 | 1.000066 | 1.000000 | 1.55e-09 | 3.83e-14 | 1.77e-08 | 1.1667 | none |
| race ee 26719 seq 771 (B) | 0.266262 | 0.310638 | 1.002002 | 1.000000 | 1.55e-09 | 3.83e-14 | 1.77e-08 | 1.1667 | none |
| race ee 26720 seq 1379 (A) | 0.266262 | 0.310638 | 1.000066 | 1.000000 | -1.13e-10 | -3.71e-09 | -6.72e-09 | 1.1667 | none |
| race ee 26720 seq 1466 (B) | 0.266262 | 0.310638 | 1.002002 | 1.000000 | -1.13e-10 | -3.71e-09 | -6.72e-09 | 1.1667 | none |
| SC ee 12236 first 0x22a | 0.536127 | 0.625481 | 1.002002 | 1.000000 | 0.00e+00 | 1.65e-15 | 0.00e+00 | 1.1667 | none |

Race camera translation row qw 0x003 (x, y, w) across the three vsyncs:
(−9409.49, −25794.3, 22751.2) → (−9431.01, −25769.6, 22851.3) →
(−9452.85, −25744.2, 22955.6). Camera variant B's z column is 1.002002 × w
plus a constant: z = 22837.0 vs w = 22851.3 in qw 0x003.

### 5e. Race: other matrix-like blocks and VF at entry (seq 684)

- qw 0x00d = (0, 0, −3000, 0), qw 0x00e = (−300, −300, −300, 0), and
  **qw 0x00f–0x012 = diag(200, 200, 200) with w row (0, 0, 0, 1)** (affine, no
  translation).
- All other data memory in these starts is per-batch unpack data (vertex
  positions around 9.3e4 in world units, normals, colours, GIF tags). The
  heuristic scan lists them in `an-mats-race-684.md` / `an-mats-sc-611.md` as
  "general" blocks. Many are vertex runs or normal runs, **not** matrices: the
  heuristic already rejects rows that are nearly parallel, but normals still
  pass.
- **VF at entry are inherited from the previous program.** At seq 684 that is
  the last program of vsync 26718 (a 2D 0x257), so: vf01–vf04 = the ortho
  screen matrix; vf05/vf06 = (1024, **+1024**, −8388467.5) /
  (2047.5, 2047.5, 8388467.5); vf28–vf31 = **the previous vsync's camera B in
  reverse row order** (vf31 = qw0 … vf28 = qw3 of 26718). There are no
  NaN/Inf values. vf08, vf09.w and vf14.xy hold small integers (they show as
  denormals). Full VF00–31 + ACC + VI tables for race seq 684 and SC
  seq 696 are in `tbl-vf.md`.

### 5f. Table index (same formats as E50: 16 floats in hex + decimal)

| file | content |
| --- | --- |
| `tbl-blocks.md` | qw 0x000–0x005 at race A/B, race 2D, SC 2D, SC 3D; race qw 0x00d–0x012 |
| `tbl-cols.md` | §5d |
| `tbl-vf.md` | VF00–31, ACC, VI00–15 at race seq 684 and SC seq 696 |
| `an-mats-race-684.md`, `an-mats-sc-611.md` | VF window scan + heuristic 4×4 scan of all data memory (affine / general), each block in hex + decimal |
| `an-progs-race.md`, `an-progs-sc.md` | every program start (seq, EE/GS vsync, tpc, byte pc, xgkicks, FNVs, VIF regs) + a per-(tpc, microcode) summary |

## T65-6. Race VU1 program startPC list (EE vsyncs 26718–26720, 2,074 starts)

`tpc` is in instruction units (T48/E47 convention); byte pc = tpc × 8.

| tpc | byte pc | microcode (micro-mem FNV) | starts (3 vsyncs) | xgkicks (sum) | first seq |
|---|---|---|---|---|---|
| 0x44e | 0x2270 | a439a372 | 362 | 472 | 0 |
| 0x459 | 0x22c8 | a439a372 | 399 | 533 | 1 |
| 0x10 | 0x80 | 405df496 | 138 | 0 | 14 |
| 0xe | 0x70 | 405df496 | 138 | 0 | 15 |
| 0x4 | 0x20 | 405df496 | 72 | 72 | 16 |
| 0x134 | 0x9a0 | 7e33f933 | 24 | 96 | 76 |
| 0x147 | 0xa38 | 7e33f933 | 9 | 178 | 84 |
| 0xd7 | 0x6b8 | 1ec2db6c | 149 | 596 | 87 |
| 0xf2 | 0x790 | 1ec2db6c | 69 | 324 | 90 |
| 0xe0 | 0x700 | 1ec2db6c | 9 | 36 | 93 |
| 0xfb | 0x7d8 | 1ec2db6c | 15 | 138 | 95 |
| 0x741 | 0x3a08 | a439a372 | 117 | 249 | 167 |
| 0x22a | 0x1150 | 405df496 | 60 | 0 | 263 |
| 0x0 | 0x0 | 405df496 | 243 | 243 | 266 |
| 0xa | 0x50 | 405df496 | 48 | 48 | 315 |
| 0x6 | 0x30 | 405df496 | 6 | 6 | 337 |
| 0x73 | 0x398 | 405df496 | 33 | 33 | 342 |
| 0x2 | 0x10 | 405df496 | 36 | 0 | 360 |
| 0x8 | 0x40 | 405df496 | 12 | 12 | 362 |
| 0x28c | 0x1460 | 5ec94df5 | 9 | 15 | 636 |
| 0x257 | 0x12b8 | a439a372 | 105 | 110 | 642 |
| 0x140 | 0xa00 | 5ec94df5 | 21 | 15 | 643 |

Per vsync: 684 / 695 / 695 starts (the recomp runs 221–229 MSCAL/vsync in
the race). The vsync order in 26719 is: 0x44e/0x459 → 0x10/0xe/0x4 loop →
0x134/0x147 → 0xd7/0xf2/0xe0/0xfb → 0x741 → 0x22a/0x0/… → 0x257 → 0x28c/0x140.
The first start of each EE vsync is 0x44e.

SC (EE vsyncs 12235–12237, 611 starts/vsync, the same count as the
recomp's 611 MSCAL/vsync at SC in E47): 0x257 (`4a3ef372`) 255, and on
`489f5136`: 0x22a 33, 0x10 54, 0xe 54, 0x0 192, 0xa 12, 0x2 531, 0x8 585,
0x73 111, 0x6 6.

The T48 hooks also logged 6,431 `T48_VU1` records (cycles/xgkicks per
program) for the T48 window around the GS dump (`t65a-t48vu1.txt.gz`).

## T65-7. Gaps and deviations

1. **Config: EE recompiler, not the EE interpreter.** The brief says "EE + VU
   interpreters". I used T48 Capture B's `dat-t48` unchanged (EE rec,
   **VU1 interp**, MTVU off). The T65 taps sit in the GS thread and in
   `vu1ExecMicro`, and need only synchronous VU1. EE interp was not needed
   for them, and it would have slowed the route that already worked.
2. **Draw-count definitions differ from the recomp's.** My counts are per
   GS primitive (each strip/fan triangle, each sprite), with ADC prims
   excluded and counted apart. PCSX2 has about 20k non-ADC PATH1 prims per
   race vsync; E47 counts 6,474–6,828 "PATH1 draws" in the recomp. E50's
   definition decides whether these are comparable. I haven't reconciled them.
3. **Screen rect = SCISSOR (0..511 × 0..447), not a hard-coded 512×448.**
   These are the same values here, since every prim had the same scissor.
4. **Choice of "world program"**: nothing here establishes which program draws
   terrain. §T65-5 gives both the first program of the vsync (0x44e,
   camera A) and the first 0xd7 (camera B), and every start is in the dumps.
5. **GS vsync vs EE vsync**: dump records carry both. The GS mirror lags by
   1 (EE 26719 ↔ GS 26718). The box lines use GS vsyncs.
6. **Emulog size 1.54 GB**, mostly pre-existing `Bios`/`SIF` console lines
   (sampled 315k + 121k per 1/50 of the lines), not T65 lines. I added a 2 GB
   emulog stop to the capture script, and it didn't trigger. The emulog is
   still on bytesize and gets rotated by the next capture.
7. The race GS dump (`.gs.zst`, 8 vsyncs from GS 26784) and the race
   statefile were captured for reuse but not analyzed here.
8. The matrix heuristic in `t65-analyze.py` is loose. The only blocks I
   claim are matrices are qw 0x000–0x003 (camera/ortho), qw 0x00f–0x012
   (race, diag 200) and the SC z≈w blocks from qw 0x011. They were
   identified by their structure and cross-checked across programs and vsyncs.

## T65-8. Exact commands

All bytesize steps ran through `run.sh` (scp a script to `C:/Users/bradr/t65stage/`,
then `ssh bytesize "wsl -d Ubuntu -- bash /mnt/c/Users/bradr/t65stage/<script>"`,
foreground, one held connection).

1. `t65-apply-build.sh`: stash pre-SHAs/copies to `pre-t65/`, run
   `python3 t65-hook.py /home/brad/pcsx2-g7/pcsx2/pcsx2`, then
   `cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2`
   (4 TUs, clean).
2. `t65-replay.sh`: `pcsx2-gsrunner -renderer vulkan -dumpdir … -logfile … -loop 1 -noshadercache -surfaceless -ini g10-uncorrected.ini -- <G13 .gs>`.
3. `t65-cap.sh` (generated from `T48/t48-capB.sh` by `gencap.py`, changes
   marked `T65`): Xvfb :99, `pcsx2-qt -nogui -slowboot -turbo -datapath dat-t48 … -- ISO`,
   `/tmp/t48-arm` + `/tmp/t65-arm` from boot. The T48 legs run to SC, then a
   15 s settle, SC ident, `touch /tmp/t65-vu-now` (dump 1) and F8. Then the
   T48 legs continue to Happiness → rules → race depart, followed by 3 s,
   dump 2, `touch /tmp/t48-dump-now`, F8, snap, F1 state and kill. WALL_CAP 598 s;
   the run finished at about 350 s.
4. `t65-extract.sh`: line families to `t65-out/`, copy the bins/shots, tar.
5. Analysis (mini, `~/dev/ssx3-work/T65/`):
   `t65-analyze.py progs|mats|const|box …`, `t65-tables.py blocks|cols|vf|boxsum <from> <to>`.

## T65-9. Receipts

- Repo (`local/research/T65/`): this file, `t65-patch.diff`, `t65-hook.py`,
  scripts, `t65a-poll.log`, `t65a-capout.txt.gz` (capture stdout/xtrace),
  line extracts (`t65a-box`, `t65a-paths`, `t65a-vu`, `t65a-t48vu1`,
  `t65a-draw` `.txt.gz`), tables (`tbl-*.md`, `an-*.md`), 3 screenshots.
- Share mirror `/Volumes/share/ssx3/ps2x-t65/`: `t65-vu1-1.bin`,
  `t65-vu1-2.bin`, `t65a-race.gs.zst` (SHAs §T65-1). The same files are in
  `~/dev/ssx3-work/T65/out/` (98 MB).
- Bytesize: `pre-t65/` (4 source copies + the T64 qt), `t65-out/`,
  `t65-vu1-{1,2}.bin`, `t65-race-state`, T65-built binaries in the tree,
  `dat-t48` emulog (1.54 GB), `pcsx2-t4/t65a-*` snaps.

Recommended next action (the orchestrator decides): give E50 the §T65-5
tables (camera at VU1 qw 0x000–0x003, viewport at 0x004/0x005, and the
column invariants), plus §T65-4. PCSX2's own race prim box is pinned to
1023.5–3071.5 with about 3k off-screen prims/vsync, so the E47 box figure on
its own does not separate healthy from broken. The two binary dumps allow a
start-by-start comparison against E50's `PS2X_VU1_ENTRY_TRACE` for any startPC.
