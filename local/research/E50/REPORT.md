# E50 report: race 3D lands off-screen: find the bad transform input (recomp)

Brief `local/muse/prompts/E50.md`, redirected mid-run by the orchestrator
after T65 (`da0ec81`: the pinned box is not a symptom; the discriminators are
T65-format prim counts and the camera block at VU1 qw 0x000–0x003). Worker:
Claude Code (Opus). This report gives tables and receipts plus a recommended
next action. The orchestrator decides.

## Outcome

- **The recomp's camera block fails T65's healthy invariants, in the race and
  at SC.** Race (vsync 7605): |w| = 1.212564 (healthy 1.000000),
  x·y / x·w / y·w = 1.9e-2 / −3.3e-2 / 4.1e-2 (healthy ≤ 2e-8), |x| = 0.306167
  (healthy 0.266262), y/x = 1.1507 (healthy 1.1667). At SC, |w| = 1.094054 and
  |x| = 0.586552 (PCSX2 1.000000 / 0.536127).
- **The SC error is one exact linear map.** Against PCSX2's SC block (T65 §5c),
  the recomp's rows satisfy row0′ = 1.0000037·row0 − 0.4437871·row1 and
  row1′ = 0.4437871·row0 + 1.0000038·row1 (residuals ≤ 8e-8). Row 2 is
  unchanged. Solving −p·M = row 3 gives the same camera position in both
  emulators, (x, y) = (0, 200). So only the 3×3 view rotation is wrong: the
  recomp's is R + 0.4438·I where PCSX2's R is a 90° yaw about +Z
  (diagonal 0, off-diagonal ±1).
- **The value first appears in the output of an EE quaternion→matrix routine,
  `sub_0015D928`.** A value-match store watch (boot 3) followed 0.443787
  (`0x3ee33810`) through every store in SC vsyncs 1303–1305:
  `0x15d928` (diagonal terms vf10.x and vf11.y, then the object matrix at
  0x00bc5960) → `0x395c38` → `0x389cb8` → `0x37d968` (builds view×proj at
  0x00621260) → `0x3645b8` / `0x364cd0` (copy into the VIF1 packet) →
  UNPACK V4_32 num=6/7 to VU1 qw 0. `0x15d928` reads its quaternion from
  object+0x30 = **0x00bc5950** (object a0 = 0x00bc5920; position at +0x20,
  matrix out at +0x40).
- **`0x15d928`'s own COP2 translation reads correct.** vopmula lane
  shuffles, dest masks and the ACC→vmsub/vmadd chains all match VU semantics,
  and the routine has no vdiv/vsqrt/vrsqrt/FPU sqrt. The observed output needs
  2z² = 0.5562 and 2zw = 1.0000037. With x = y = 0 that solves to
  q ≈ (0, 0, 0.52736, 0.94813), |q|² = 1.177, where the healthy value would
  be (0, 0, √½, √½). A uniformly scaled (unnormalised) healthy q is ruled out:
  it predicts a diagonal of 1.084 in the map above, and the map's diagonal is
  1.0000037. So **the quaternion in memory is wrong before `0x15d928` reads
  it**; its writer has not been found yet.
- **Counts in T65's definitions:** race 4,810 on / 0 off / 2 straddle /
  53–59 zero-area / 936 ADC / 6,196 PATH1 verts per drawing vsync (PCSX2
  ≈ 16.7k / 2.9k / 870 / ~145 / 4.8k / 27.6k). The recomp starts **191
  programs per vsync, from 5 of PCSX2's 22 startPCs**. At SC the per-startPC
  MSCAL counts match T65 exactly (10 of 10 programs).
- Not tested: whether the wrong camera causes the missing programs (for
  example EE-side visibility culling against a bad frustum). It fits the
  data, but nothing here proves the link.

## Recommended next action (the orchestrator decides)

1. **One SC boot, existing tap, no rebuild:** `PS2X_DIAG_WATCH=0xbc5950,0xbc5958`
   on the E50 runner (or any E46+ runner) with the e50c route, wall ~100 s. It
   logs every write to the quaternion with pc/ra/value. Expected: a writer
   storing (0, 0, 0x3f0700ef, 0x3f72b864) (0.52736, 0.94813) if the inference
   holds. Its disassembly names the next suspect (sin/cos, slerp,
   normalisation or an Euler→quaternion step, and which FPU/COP2 ops it uses).
   `valwatch` can then follow the writer's inputs the same way.
2. **T lane (cheap, confirms the model):** read PCSX2 EE RAM 0x00bc5920–0x00bc59a0
   at SC. The prediction is q = (0, 0, 0x3f3504f3, 0x3f3504f3) and
   pos.y = 200. If PCSX2's object sits elsewhere, find it by the SC camera
   words instead.
3. No candidate fix yet: no single mechanism is named. The only other lead,
   a guest write to VU0 VF0, is ruled out (below).

## Pins and builds

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/E50/PS2Recomp`, local branch `e50-diag` off `ssx3` @ `2e21cdc` (not pushed) |
| Commits | `b50a4d1` taps (a)/(b) + entry trace; `387eb12` T65-format counters; `237e904` value watch |
| Codegen | `~/dev/ssx3-work/codegen-ssx3` (canonical) |
| Build dir | `~/dev/ssx3-work/E50/build` (Release, runtime/aggressive logs OFF, tests ON); diagnostic build, no speed numbers |
| Runner e50a | `9e11bab5798d77673f3036f003fa43b15f35f5c64089997dbd0132cb3fdb3fec` ×2 (595/595 tests) |
| Runner e50b | `d2f52cb65fa0ffadfce98ad583a24977142b0d3bde27e01df64b5200729013fd` ×2 (597/597) |
| Runner e50c | `d457a3672bea36886e1b46bf44e9e560b01e5ecdbfc0adef7eef65ad9ed6e7a9` ×2 (598/598) |
| Tests | `ps2x_tests` from the worktree root; logs `~/dev/ssx3-work/E50/tests{,2,3}.log` |

## Taps added (all dev-only, default off, unit tested)

| Env | What |
| --- | --- |
| `PS2X_GFX_STATS` (existing) + E50 fields | `dN_scr=on,off,straddle` (bbox against SCISSOR after XYOFFSET); `dN_t65=verts,on,off,straddle,zero,adc` in T65's exact definitions (every kicked vertex; each completed prim: ADC counted and skipped; inclusive edges [SCAX0, SCAX1+1]; zero-area = x0==x1 or y0==y1); `pcs=<startPC>:<mscal>:<on>/<off>/<straddle>` per VU1 startPC (PATH1 draws attributed to the latest MSCAL). Fields appear only when seen, so pre-E50 lines are byte-identical |
| `PS2X_E4_HEAD=<N>` | E4 keeps the first N draws of the armed vsync, with the register/GIF-tag events between them, in `e4-head.txt`, plus XYOFFSET and the first 3 vertices per draw |
| `PS2X_VU1_ENTRY_TRACE_PCS=all`, `_MAXPAIRS`, `_MAXLINES` | first MSCAL of each distinct startPC at/after the gate; `reg` lines (VF0–31, ACC, VI0–15, Q/P/I, TOP/ITOP at entry); UNPACK `vif` lines carry `src=<EE addr> tag=<id>@<tag addr>` from the E40 pay map (recorded when the entry trace is on) |
| `PS2X_E50_VALWATCH=<file>` + `_VALUES=<hex,…>` + `_FROM/_TO` | every WRITE32/64/128 with a 32-bit lane equal to a listed word, logged with pc/ra/host fn/GPRs a0–s7; lock-free compare; 512-line cap. Inlined constant-address FAST_WRITE stores bypass it (stated gap) |

## Boots (Mac mini, slot 1, own run dir `~/dev/ssx3-work/E50/run`, PID-tracked)

| Boot | Purpose | Window | Wall | Result |
| --- | --- | --- | --- | --- |
| e50a | SC control | gfx 1300–1310, E4 arm 1305 (+head), entry trace from 1305 | 121 s, rc 0 | 10 SC programs dumped, head 4,096 draws |
| e50b | race | gfx 1300–7610 (SC + race in one file), E4 arm 7605, entry from 7605 | 450 s, rc 0 (E49 held slot 2) | race at 7600–7610 (frame at tick 7690: 00:00:10, 2ND/2, dark world, `e50b-race-tick7690.png`); 5 race programs dumped |
| e50c | SC value watch | valwatch 1303–1305 on `3ee33810,3ee3ac84,be73a2e6,bf093fba,423e5743` | 101 s, rc 0 | 153 lines, 51 per vsync, identical across the 3 vsyncs |

Missing targets: `0x3b1140` ×3 only, as in E46/E47. Lease released after each
boot, peers [] or E49's runner.

**This race window is a different moment from E47's.** E47b: 221–229
MSCAL/vsync, 6,474 draws and 81 off-screen trail draws. Here: 191 MSCAL,
4,812 draws, **0 off-screen**. The route is vsync-scripted, but the race
state at a given tick differs between runs (E47 already noted host effects).

## Tables

### PATH1 counts in T65's definitions (per vsync; drawing vsyncs are identical)

| window | mscal | p1 verts | on | off | straddle | zero-area | adc | prim box (abs, non-ADC) |
|---|---|---|---|---|---|---|---|---|
| recomp race 7600–7610 (9 drawing vsyncs; 7601/7607 draw nothing) | 191 | 6,196 | 4,810 | 0 | 2 | 49–59 | 936 | 1791.5–2303.5 × 1823.5–2271.5 |
| PCSX2 race (T65 §4, 26714–26723) | 684–695 starts | 27.5k–28.2k | 16.7k–16.9k | 2.65k–3.06k | 837–912 | 135–162 | 4.7k–4.9k | 1023.5–3071.5 × 1023.44–3071.5 |
| recomp SC 1300–1310 (e50b) | 611 | 5,844 | 4,112 | 32–34 | 20–22 | 6–8 | 1,294 | 1741.06–2358.56 × 1799.19–2324.69 |
| PCSX2 SC (T65 §4) | 611 | 7,900 | 5,015 | 1 | 63 | 8–10 | 1,294 | (vertex box) 1741.06–2329.88 × 1765.5–2324.69 |

Per-vsync rows: `an-e50b-t65.md` (race) and `an-e50b-sc-t65.md` (SC).
Definition gap: T65's p1 verts include ADC vertices and so do ours
(`noteT65Vertex` on every kick), but the prim box column is the E33 box over
drawn prims only.

### Per-startPC census: race vs T65 §6 (per vsync; T65 = 3-vsync sum ÷ 3)

| tpc | byte pc | recomp MSCAL | recomp PATH1 draws (on/off/str) | PCSX2 starts | PCSX2 xgkicks |
|---|---|---|---|---|---|
| 0x44e | 0x2270 | 73 | 1,803 (1803/0/0) | 120.7 | 157.3 |
| 0x459 | 0x22c8 | 54 | 2,545 (2545/0/0) | 133.0 | 177.7 |
| 0xd7 | 0x6b8 | 11 | 396 (396/0/0) | 49.7 | 198.7 |
| 0x741 | 0x3a08 | 18 | 0 | 39.0 | 83.0 |
| 0x257 | 0x12b8 | 35 | 68 (66/0/2) | 35.0 | 36.7 |
| 0x10, 0xe, 0x4 | 0x80, 0x70, 0x20 | **0** | — | 46, 46, 24 | 0, 0, 24 |
| 0x134, 0x147 | 0x9a0, 0xa38 | **0** | — | 8, 3 | 32, 59.3 |
| 0xf2, 0xe0, 0xfb | 0x790, 0x700, 0x7d8 | **0** | — | 23, 3, 5 | 108, 12, 46 |
| 0x22a, 0x0, 0xa, 0x6, 0x73, 0x2, 0x8 | | **0** | — | 20, 81, 16, 2, 11, 12, 4 | 0, 81, 16, 2, 11, 0, 4 |
| 0x28c, 0x140 | 0x1460, 0xa00 | **0** | — | 3, 7 | 5, 5 |
| total | | **191** | 4,812 | ~691 | |

SC (e50a, per vsync) vs T65 SC ÷ 3: 0x257 85/85, 0x22a 11/11, 0x10 18/18,
0xe 18/18, 0x0 64/64, 0xa 4/4, 0x2 177/177, 0x8 195/195, 0x73 37/37,
0x6 2/2. **Exact match.** Race attribution caveat: PATH1 draws are counted
against the most recent MSCAL, so a queued GIF packet would be credited to a
later program (none suspected: packets drain immediately).

### Camera block, qw 0x000–0x005 (T65 format: 16 floats hex + decimal)

Race, vsync 7605. The same block is in all 5 race programs' first starts
(0xd7, 0x741, 0x44e, 0x459, 0x257). There is one variant, B-like (z = 1.002·w + c):

| qw | x | y | z | w |
|---|---|---|---|---|
| 0x000 | 3e937926 (0.288034) | 3e2abdc6 (0.16674) | 3de08396 (0.109626) | 3de010c0 (0.109407) |
| 0x001 | bdd4969a (-0.103803) | 3e8d3b7d (0.275844) | 3f1e7a37 (0.619052) | 3f1e2928 (0.617815) |
| 0x002 | 00000000 (0) | 3e11a567 (0.142233) | bf8514a4 (-1.03969) | bf84d092 (-1.03762) |
| 0x003 | c5c16e2e (-6189.77) | c4cab499 (-1621.64) | 47ec2e6b (120925) | 47ebd396 (120743) |
| 0x004 | 44800000 (1024) | c4800000 (-1024) | cafffee7 (-8.38847e+06) | 00000000 (0) |
| 0x005 | 44fff000 (2047.5) | 44fff000 (2047.5) | 4afffee7 (8.38847e+06) | 00000000 (0) |

SC, vsync 1305. The same block is in all 9 SC 3D programs; T65 §5c is
PCSX2's:

| qw | x | y | z | w |
|---|---|---|---|---|
| 0x000 | bf093fba (-0.536129) | 00000000 (0) | 3ee3ac84 (0.444676) | 3ee33810 (0.443787) |
| 0x001 | be73a2e6 (-0.237926) | 00000000 (0) | bf8041b9 (-1.00201) | bf80001f (-1) |
| 0x002 | 00000000 (0) | 3f201f89 (0.625481) | 00000000 (0) | 00000000 (0) |
| 0x003 | 423e5743 (47.5852) | 00000000 (0) | 433e6421 (190.391) | 43480030 (200.001) |
| 0x004 | 44800000 (1024) | c4800000 (-1024) | cafffee7 (-8.38847e+06) | 00000000 (0) |
| 0x005 | 44fff000 (2047.5) | 44fff000 (2047.5) | 4afffee7 (8.38847e+06) | 00000000 (0) |

Viewport qw 0x004/0x005 match PCSX2 bit for bit in both scenes.

### Column invariants (T65 §5d format)

| block | abs col x | abs col y | abs col z | abs col w | x.y | x.w | y.w | y/x scale | NaN/Inf/den |
|---|---|---|---|---|---|---|---|---|---|
| recomp race vsync 7605 (all 5 programs) | 0.306167 | 0.352310 | 1.214991 | 1.212564 | 1.94e-02 | -3.26e-02 | 4.11e-02 | 1.1507 | none |
| PCSX2 race (T65, any) | 0.266262 | 0.310638 | 1.000066 / 1.002002 | 1.000000 | ≤1.6e-09 | ≤3.7e-09 | ≤1.8e-08 | 1.1667 | none |
| recomp SC vsync 1305 (all 9 3D programs) | 0.586552 | 0.625481 | 1.096244 | 1.094054 | 0.00e+00 | 1.64e-09 | 0.00e+00 | 1.0664 | none |
| PCSX2 SC (T65) | 0.536127 | 0.625481 | 1.002002 | 1.000000 | 0.00e+00 | 1.65e-15 | 0.00e+00 | 1.1667 | none |

At SC the error is invisible to the dot products: it scales and rotates the
x and w columns together in the world X/Y plane, so x·w stays small and |w|
shows it. The race camera has pitch too, so all three dots fail.

### First draws of the frame (E4 head, 4,096 draws each)

- Race (7605): 4,063 triangle-class draws, **all on-screen** (0 off, 33
  straddle, 0 vertices at the guard-band edges). The first 20 are small
  textured tstrips around (334–360, 77–89) px, TEX0 13065 (psm 0x14,
  128²) then 12809, TEST 0x51143. Full table: `an-e50b.md`
  ("First 20 triangle/strip/fan draws").
- SC (1305): `an-e50a.md`, same format. The first 17 draws of both frames
  are full-screen sprite strips (TEX0 0, TEST 0x30000), not world draws.

### Matrix scan of VU1 data memory

`an-e50a.md` / `an-e50b.md` list every plausible 4×4 block per program
(16 words hex + decimal, NaN/Inf/denormal flags, row norms, max |cos|,
which rows the first 4,000 pairs load). No NaN, Inf or denormal appears in
any camera or viewport block. Per-batch vertex and normal runs pass the
heuristic as "matrices" too (T65 §5e noted the same). Only qw 0x000–0x005
are asserted here.

## Code read

| Step | Fact | Source |
|---|---|---|
| UNPACK | race/SC camera = `UNPACK V4_32 num=6` or `num=7` `addr=0` (not TOPS), payload inline after a CNT tag (id 1) in the VIF1 chain arena, e.g. `src=0x006f7ea0 tag=1@0x006f7e80` (race), `src=0x0070a0e0 tag=1@0x0070a0c0` (SC). Race also sends qw 4–5 alone (`num=2 addr=4`) | `entry-e50{a,b}.txt.gz` |
| Packet copy | `0x364cd0` (draw-record dispatch per labels.tsv, E42/T54; called from 0x363cfc inside the render-list walker `0x363c20`) writes the rows into 0x3070a0e0 / 0x3070a960 (uncached mirror of the arena) at pc 0x3659f0–0x365a14; `0x3645b8` (called from 0x37dbd8) makes an earlier copy at 0x00873340 | `valwatch-e50c.txt` |
| view×proj | `sub_0037D968` (called from 0x37a6bc inside `0x37a430`, the SC render-list appenders per labels.tsv, T61/T62) stores the full camera to stack and to 0x00621260; ops: vmulax/vmadday/vmaddaz/vmaddw ×13, `vcallmsr`, FPU `div` ×1 | codegen op census |
| view | `sub_00389CB8` (0x878 B) stores 0x3ee33810 at 0x01fffae8/…b00; ops include **`vrsqrt` ×1, `vwaitq` ×2, `vmulq`, FPU `div` ×2** (the only rsqrt/div-class ops in the chain) | codegen op census |
| copy | `sub_00395C38` (0x30 B, lqc2/sqc2 ×4) copies the object matrix to 0x0061cb88 | codegen |
| **origin** | `sub_0015D928` (virtual, via wrapper 0x168060 in vtables 0x45b8cc/0x46d8f4) takes object a0 = 0x00bc5920: copies the 4×4 template at 0x004c53a0 to a0+0x40, loads **quaternion vf4 = a0+0x30**, builds the rotation with vadd/vmul/vopmula/vsuba*/vmsub*/vadda*/vmadd* (no vdiv/vsqrt/vrsqrt, no FPU sqrt), multiplies template × R, stores to a0+0x40, then negates position a0+0x20..0x28 (FPU `neg.s`) for the translation. **The first store of 0.443787 is its vf10.x (1−2y²−2z²) and vf11.y (1−2x²−2z²)** | `ee-at 0x15d928`, valwatch pcs 0x15d9cc/0x15d9d0/0x15da38 |
| Ruled out | The only guest write to VU0 VF0 in the codegen (`lqc2 $vf0` at 0x3fe9bc, which the recomp would honour but hardware ignores) is in `sceDevVu0PutCnd`, which `ssx3.toml` stubs, so it never runs | `grep vu0_vf\[0\] =` over codegen; `ssx3.toml:278` |

Names come only from `labels.tsv` (`0x364cd0`, `0x363c20`, `0x37a430`) and the
`ssx3.toml` stub list (`sceDevVu0PutCnd`). Every other function is described by address.

## Gaps

- The quaternion values are **inferred** (from the SC block algebra, which
  assumes everything downstream of `0x15d928` matches PCSX2), not read. One
  watch boot settles it (next action 1).
- The race camera wasn't decomposed. With a moving camera and no
  same-moment PCSX2 block, only the invariants are compared.
- Whether the bad camera explains the 5-of-22 program set in the race is
  not tested.
- `valwatch` misses inlined constant-address FAST_WRITE stores. The 51
  lines per vsync form a complete source-to-packet chain, so nothing on
  this path was missed.
- Taps (a)/(b) as first briefed (on/off vs the guard-band box, first-N
  draws) are superseded by T65: the recomp's race box doesn't reach the
  guard band in this window at all.

## Exact commands

```
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/E50/PS2Recomp -b e50-diag ssx3
cmake -S ~/dev/ssx3-work/E50/PS2Recomp -B ~/dev/ssx3-work/E50/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_BUILD_TEST=ON \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
cd ~/dev/ssx3-work/E50/build && nice -n 10 ninja -j8 ps2x_tests ps2EntryRunner   # after each tap commit
cd ~/dev/ssx3-work/E50/PS2Recomp && ../build/ps2xTest/ps2x_tests
local/research/E50/e50_boot.sh e50a 1300 1310 1305 1305 120 5
local/research/E50/e50_boot.sh e50b 7600 7610 7605 7605 450 5 1300
local/research/E50/e50_valwatch_boot.sh e50c 1303 1305 3ee33810,3ee3ac84,be73a2e6,bf093fba,423e5743 100
python3 local/research/E50/e50_analyze.py e50a > an-e50a.md; ... e50b > an-e50b.md
python3 local/research/E50/e50_analyze.py t65 e50b 7600 7610 blocks > an-e50b-t65.md
python3 local/research/E50/e50_analyze.py t65 e50b 1300 1310 > an-e50b-sc-t65.md
python3 local/research/E50/e50_analyze.py t65 e50a 1305 1305 blocks > an-e50a-t65.md
```

## Receipts

- In this dir: `e50_boot.sh`, `e50_valwatch_boot.sh`, `e50_analyze.py`,
  `an-e50a.md`, `an-e50b.md`, `an-e50a-t65.md`, `an-e50b-t65.md`,
  `an-e50b-sc-t65.md`, `gfx-e50a.txt`, `gfx-e50b-windows.txt` (1300–1310 +
  7600–7610), `entry-e50{a,b}.txt.gz`, `e4-head-e50{a,b}.txt.gz`,
  `valwatch-e50c.txt`, `e50b-race-tick7690.png`.
- Raw data in `~/dev/ssx3-work/E50/run/` (short SHA-256): boot-e50a
  `854f2fe807e217f8` (7,867,871 B), boot-e50b `97e96a1ed43e01ce`
  (22,276,509 B), boot-e50c `ed8f489532eb8d9a` (6,730,074 B), gfx-e50b
  `d4306f70b6889784` (3,493,017 B, 1300–7610), entry-e50a `8ef4350551ab3bb8`,
  entry-e50b `1e64b47fa1677dc9`, valwatch-e50c `bfe0c1fb34b2a3e7`.
- Budget: 3/3 boots, ~2 h of 5 h (16:05–17:05). E50 disk 3.3 GB of 4 GB (build
  3.2 GB). Internal total 51.3 of 200 GB.

---

## Part 2: the quaternion's writer, bisect to the first differing op

Orchestrator gate: max 3 boots; name the writer, follow its inputs to the
first differing op, unit-test it, and apply ONE fix only if a single
translation defect is named. **Stopped before any fix: two defects are
named, and each fixed alone still breaks the camera (table below).** 1 of
3 boots used.

### Boot e50d (SC, 101 s, rc 0, E50 runner `d457a367…`, slot 1)

`PS2X_DIAG_WATCH=0xbc5950,0xbc5958` plus `PS2X_E50_VALWATCH` on
`3f0700ef,3f72b864,3f3504f3` over vsyncs 1250–1305
(`diagwatch-e50d.txt`, `valwatch-e50d.txt`; boot log `266dcfaef6ca78b4`,
6,842,073 B).

| # | pc | ra | thread | value at 0xbc5950 (x, y, z, w) |
|---|---|---|---|---|
| 1–2 | 0x15d6e8 | 0x195728 | 1 | (0, 1, 0, 1): init |
| 3–4 | 0x15d754 | 0x195784 | 1 | (0, 1, 0, 1) |
| 5–6 | 0x1a2020 | 0x1a1fc8 | 3 | (0, 1, 0, 1) |
| 7–8 | **0x15e0d4** | **0x15e0bc** | 1 | **(−0, −0, `3f0700ef`, `3f72b863`) = (0, 0, 0.527358, 0.948126)** |
| 9–10 | 0x15e0d4 | 0x15e0bc | 1 | same (second setup call, sp 0x1fff8f0) |

(Each write is logged twice because the two watched 8-byte windows both
overlap the 16-byte `sq`.) The value matches Part 1's prediction to 1 ulp
(`3f72b864` predicted). T66 (`8289688`) independently puts the same writer
in PCSX2 (`sq a0, 0x30(s0)` at 0x15e0d4, written once) with
q = (−0, −0, `3f3504f3`, `3f3504f3`) and pos (0, 200, 0, 1). The
`3f3504f3` stores in this boot come from `0x30dbd0` (vsync 1264, stack
0x01fffc50/…5c) and are unrelated to this object.

### The chain (static, `ee-at`/`ee-func`; every step matches T66's)

| Function | Role | Evidence |
|---|---|---|
| `sub_0015E050` | sets up the camera object (s0 = 0x00bc5920) from two input vectors (`*a2` → sp+0x20, `*a1` → sp+0x40, w = 1.0), calls `func_166640(sp, 1)`, `func_166F90(sp)`, `func_1673A0(sp+0x390, sp)`, stores pos → +0x20 and **quat → +0x30 at 0x15e0d4**, then runs the same quat→matrix block as `0x15d928` | disassembly 0x15e050–0x15e2a4 |
| `sub_001673A0` | getter: copies work-struct +0x60 (pos) and +0x70 (quat) | 0x1673a0–0x1673b4 |
| `sub_00166F90` | builds the rotation from two angles (work +0x54, then +0x50; each `neg.s`), each via **`func_31BE50(&sin, &cos)`** and an axis-angle (Rodrigues) matrix, diagonal = (1−c)·a² + c, off-diagonal ±s; then `func_31B748` → matrix to (pos, quat) | 0x166f90–0x16739c |
| `sub_0031B748` → `sub_0031B7A8` | matrix → quaternion (Shoemake: w = ½·sqrt(1+trace), q_i = (m_jk − m_kj)·(½/sqrt)) | 0x31b7a8–0x31b9ac |
| **`sub_0031BE50`** | **sincos**: `q = CVT.W.S(a·2/π ± 0.5)`, x = a − q·π/2, sin(x) = x·P(x²) (degree 9), **cos(x) = SQRT.S(1 − sin²x)**, quadrant swap on q & 3 → *a0 = sin(a), *a1 = cos(a) | 0x31be50–0x31bf5c; constants at gp−0x2ec0 = 0x4a0230: 2/π, π/2, 2.7557e-6, −1.9841e-4, 8.3333e-3, −0.16667 |

The SQRT.S sites in `0x31B7A8` (0x31b7ec `sqrt.s f0,f0`, 0x31b8e0
`sqrt.s f5,f0`) have ft = fs = 0, so they translate correctly by accident.
The trace 2.5957 that `0x31B7A8` sees is already in its input matrix.

### The first differing op, and the second

At the SC yaw a = π/2 (header +0x0c = π/4 in T66 is the half-angle of this
rotation; the recomp's header word was not read in this boot):

| Step (guest pc) | EE semantics (PCSX2 FPU.cpp) | recomp translation | EE value | recomp value |
|---|---|---|---|---|
| 0x31be88 `cvt.w.s f1, f1` on 1.5 | `CVT_W`: `(s32)Fs`, saturating = **truncate** | `FPU_CVT_W_S` = `(int32_t)nearbyintf(a)` = **round to nearest even** | q = 1 → x = −4.4e-8 | **q = 2 → x = −π/2** (outside the ±π/4 range the polynomial and quadrant table assume) |
| 0x31beec `0x46050044` = `sqrt.s $f1, $f5` | `SQRT_S`: sqrt(\|**Ft**\|) = sqrt(\|f5\|), ±0 kept | generator emits `FPU_SQRT_S(ctx->f[fs])` = sqrt(f0) (fs field = 0 in every SQRT.S encoding); `FPU_SQRT_S` = `sqrtf` (NaN on negatives) | sqrt(1 − sin²x) = 1 | **sqrt(f0 = P(x²) = sin(x)/x = 0.63662) = 0.797886** |
| output (quadrant 1 vs 2) | sin = 1, cos = −0 | | (1, −0) | **(1.0000036, −0.797886)** |

Downstream the numbers follow exactly: Rodrigues about z gives
[[c, s], [−s, c]] with c = −0.797886, s = 1.0000036. Its trace + 1 = 3.5957,
so w = ½·√3.5957 = 0.948126 and z = 2·1.0000036·(½/1.8963) = 0.527358,
i.e. the stored q. `0x15d928` then turns that q into R + 0.4438·I
(Part 1). Offline replay of `0x31BE50` (float32, ELF constants) under four
semantics, every 0.001 rad over ±2π:

| Semantics | max \|sin err\| | max \|cos err\| | at π/2 (sin, cos) |
|---|---|---|---|
| recomp now (CVT rounds, SQRT reads fs) | 7.98e-01 | 7.98e-01 | (1.0000036, −0.797886), the observed values |
| fix SQRT.S only (ft, sqrt\|·\|) | 2.22e-03 | 2.67e-03 | (1.0000036, −0.002674): camera dots ~1e-3, still fails T65 |
| fix CVT.W.S only (truncate) | 2.42e-01 | 2.42e-01 | (1, −0): SC would pass; any race angle with \|x\| ≫ 0 still wrong |
| both = EE | 4.12e-07 | 2.77e-07 | (1, −0) |

Game-wide reach: `FPU_CVT_W_S` appears at **992 sites in 283 generated
files**. SQRT.S has 107 sites, **36 with ft ≠ fs** (these read the wrong
register today). The generator's RSQRT.S has the same field bug
(1/sqrt(fs) instead of fs/sqrt(ft)), but SSX 3 has no FPU RSQRT.S sites.

### Unit tests (fork `e50-diag` `68d4a52`, `ps2_fpu_semantics_tests.cpp`, copy in this dir)

All 4 fail on the current tree (598 other tests pass; `tests-part2-failing.txt`):

| Test | Result today |
|---|---|
| SQRT.S reads ft: decode 0x46050044 → expect `ctx->f[1] = FPU_SQRT_S(ctx->f[5]);` | FAIL: got `FPU_SQRT_S(ctx->f[0])` |
| SQRT.S takes sqrt(\|ft\|): `FPU_SQRT_S(-4) == 2`, no NaN for −7.4e-6 | FAIL: NaN |
| CVT.W.S truncates: 1.5→1, −1.5→−1, 2.7→2, −0.7→0 | FAIL: 2, −2, 3, −1 |
| Guest sincos `0x31be50` replay (runtime macros + the generator's own SQRT.S operand) at a = ±π/2 → sin 1, cos 0; error < 1e-5 over ±2π | FAIL: cos = −0.797886 |

### Decision needed (the orchestrator decides)

Two translation defects, both needed for T65's invariants. Proposed fix
(not applied; `part2-proposed-fix.diff`):

- **(A) SQRT.S:** a one-line generator change (`fs` → `ft`), plus
  `FPU_SQRT_S` = sqrt(\|a\|) with ±0 kept. It needs regenerated codegen:
  either a full regen into an E50-private dir, or an APFS clone of
  `codegen-ssx3` with the 36 affected lines rewritten and checked against
  a generator run.
- **(B) CVT.W.S:** a runtime macro only (truncate + saturate, PCSX2
  `CVT_W`). No regen, rebuild ~8 min. Touches 992 sites, so it's a wider
  behaviour change.

Options:

1. **Allow A + B as one "R5900 FPU semantics" fix.** Validation is the 2
   remaining boots: SC camera block vs T65 invariants, and race T65 counts,
   startPC census and frame.
2. **B only.** Predicted: SC passes (cos(π/2) = −0), and the race camera
   stays wrong wherever \|x\| ≫ 0.
3. **A only.** Predicted: SC dots ~1e-3, and the race improves but still
   fails T65.

Recommendation: 1. Neither half alone meets the gate's validation
criterion, and both are plain field/rounding mismatches against PCSX2's
FPU.cpp.
