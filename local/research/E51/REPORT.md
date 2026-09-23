# E51 report: race terrain untextured/shard-like after the camera fix

Brief `local/muse/prompts/E51.md`. Worker: Claude Code (Opus, the E50 pane).
Tables and receipts; the orchestrator decides. **Handed back early, per the
orchestrator's E52/E53 note.** The trace points at the VCALLMSR defect E52
found (E53 is fixing it). 1 of 3 boots used; no fix applied.

## Outcome

1. **The recomp barely streams textures.** In an 8-vsync window at
   00:00:19, PCSX2's race GS dump carries **73–74 IMAGE uploads per vsync
   (~445 KB)**. The recomp's GIF stream at the same timer value carries
   **1 per vsync (1 KB, 16×16 CT32)**.
   - PCSX2 re-uploads what it samples every frame: 9,876 of 20,149
     textured prims use a TBP re-uploaded inside the dump.
   - The recomp's texture-cache slots hold other or stale content. Its
     32×32 PSMT4 slots 13257/13289 are 6% nonzero and carry 1,482
     terrain-program prims per vsync, which fits the dark ground.
2. **The EE-computed per-object LOD bias is broken.**
   - Every recomp TEX1 on the terrain programs' PATH2 packets has
     K = 0x801 (−127.94, the saturated minimum).
   - PCSX2's TEX1s carry per-object K values (0xef2 … 0xf4e, about −17
     … −11).
3. **Texture coordinates are sane.** Recomp terrain prims have Q in
   3.6e-5…1.5e-4, |S/Q| ≤ 4, |T/Q| ≤ 5, and no NaN/Inf, like PCSX2's. So
   degenerate geometry doesn't explain the look at this moment. The e50f
   zero-area excess is moment-dependent: here it's 96–128/vsync, inside
   PCSX2's range.
4. **Only 4 VU1 programs run in this window**: 0xd7, 0x257, 0x44e,
   0x459, 272–286 MSCAL/vsync. e50f ran 19 programs and PCSX2 runs ~22
   (~690 starts). Most of the scene isn't submitted.
5. **Lead: the camera's per-object test runs the wrong VU0
   microprogram.**
   - `sub_0037DE88` is a vtable method (slot 0x49354c) of the same class
     as E50's camera builder (`0x37dbe8`, slot 0x49353c).
   - It loads vf15/vf16 and a 4×4 matrix into vf10–13, writes CMSAR0 =
     0x570/8 with `ctc2 $v0, $vi27` (0x37deac), then runs `vcallmsr
     $vi27` (0x37deb8), reads vi1/vi2 back with `cfc2`, and branches on
     vi2 ≠ 0.
   - That's the shape of a bounding-volume-vs-frustum visibility test.
   - Generated code: `ctc2` stores `ctx->vu0_cmsar0`, but `vcallmsr`
     starts at `ctx->vi[27] & 0x1FF`, which `ctc2` never wrote. This is
     E52's VCALLMSR finding (8 sites). **E53 owns the fix. Not
     duplicated here.**
   - A wrong visibility result would explain the missing objects, the
     missing startPCs, and the texture manager not uploading. It may
     also explain the saturated K, if K is derived from the same test's
     output. That last link is **not tested**.
6. **VU1 budget exits:** there were none in this window (vsyncs
   8200–8280, 81/81 at `vu_exhausted=0`, so `PS2X_VU1_TRACE` wrote no
   file). e50f had them around 7600, at a different race state. **Still
   unidentified.**
7. **The race is not reproducible run to run** at the same tick with the
   same runner inputs:
   - e50f at 00:00:19 (tick 8275): 2ND/2, 19 programs.
   - e51a at 00:00:19 (tick 8279): 1ST/2, 20 points, 4 programs.

   So "matching the moment" matches the HUD timer, not the scene.

## Recommended next (the orchestrator decides)

1. Let E53's VCALLMSR/VSQI batch land. Its race boot should show 20+
   startPCs, PATH1 prims near PCSX2's 21.9k all-path/vsync, and per-vsync
   IMAGE uploads approaching PCSX2's ~73.
2. If E53 wants the discriminators here, `e51_gif.py` + `PS2X_GIF_DUMP`
   (fork `e51-diag` `0af7eed`) give the same tables for any boot:
   - uploads per vsync (shapes, DBPs);
   - TEX1 K distribution;
   - prims per startPC.
3. If terrain is still wrong after E53: one E51 boot with
   `PS2X_VU1_TRACE` over a wide window (the exits appear only in some
   states), plus a `PS2X_E50_VALWATCH` on the TEX1 upper word
   `0xfffff801` to find the K builder.

## Build and boot

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/E50/PS2Recomp`, branch `e51-diag` = `ssx3` `eac6cba` (FPU fix) + E50 taps `749afb7`, `3685507` + `0af7eed` (GIF dump). Not pushed |
| Build | `~/dev/ssx3-work/E50/build`, reconfigured to canonical `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (= E50 regen: 30 files differ from e49, as expected). 8 min 43 s, nice 10 after the quiet-host wait |
| Runner | `20163c2a22b52689361944406a881b665728926c9936e53c29abaa053fb3b010` ×2 |
| Suite | 604/604 from the worktree root (`E51/suite.log`) |
| Boot e51a | `local/research/E51/e51_boot.sh e51a 480 1`: slot 1, 480 s, rc 0, final tick 9314. gfx 8200–8280, GIF dump 8258–8265 (+PATH2/3 from 8200), E4 arm 8260 (head + VRAM), VU1 trace 8240–8280 (no exits, no file) |
| Frame | `frames/e51a-race-tick8279.png` (00:00:19; dark ground, light-blue shards, rider, HUD). PCSX2: `frames/pcsx2-t65-race-0018.png` |

New tap `PS2X_GIF_DUMP` (default off, unit-tested): each packet entering
`GS::processGIFPacket` (before the native image fast path) is written as
`u32 'GIFP', vsync, path, VU1 startPC, size, data`. PATH1–3 are kept in
`_FROM.._TO`, PATH2/3 also from `_IMG_FROM`. 256 MiB cap.

## Decoder (`e51_gif.py`, `e51_tables.py`, `e51_texdump.cpp`)

- One streaming GIF decoder for both sides: PACKED/REGLIST/IMAGE, A+D,
  PRE, ADC, strips/fans, TEX0/TEX2/TEX1/CLAMP/XYOFFSET/SCISSOR,
  BITBLTBUF/TRXREG/TRXDIR → IMAGE census, T65 on/off/straddle/zero-area.
- **PCSX2 dump framing** as in G8. The dump stores every GIF transfer
  under one index (4), so PCSX2's side can't be split by path, and
  comparisons use all-path totals.
- **GS state:** VRAM is at state offset **425**. That's the only offset
  in 396–444 where any 8 KiB page matches the recomp's VRAM byte for
  byte (21 pages).
- **Self-check:** the parser's all-path totals on the recomp dump match
  gfx stats within 0.2% (8261: 9,512 vs 9,497). On PCSX2 it gives
  on 18.8–19.0k / off 2.1–2.3k / straddle 780–810 / zero-area 125–192 /
  ADC 4.99–5.20k per vsync, the same shape as T65's PATH1 counts.
- **`e51_texdump.cpp`** decodes PSMT4/PSMT8/CT32 textures from either
  VRAM image using the runtime's own swizzle headers. The decode is
  validated by eye: PCSX2 14857 = bare tree; recomp 13417/13513 = snowy
  pines.

## Tables

### IMAGE uploads per vsync

| Side | Window | uploads/vsync | IMAGE bytes/vsync | shapes (dpsm, w×h: count over window) | DBPs |
|---|---|---|---|---|---|
| PCSX2 dump | 8 vsyncs from GS 26784 (~00:00:19) | 73–74 | 444,928–445,184 | CT32 64×32: 184, 32×16: 184, 16×8: 184 (mip chains), CT32 128×128: 16, 16×16: 8, PSMT4 512×256: 8, PSMT8 16×16: 4 | 8 per vsync (11017, 14665, 14857, 14889, 14921, 15145, 15177, 15209) |
| recomp e51a | 8258–8265 (00:00:19) | 1 (0 on 8260) | 1,024 | CT32 16×16: 7 | — |
| recomp e51a | 8200–8257 (PATH2/3) | ≤1 | ≤1,024 | | |

gfx-stats PATH3 at 8256–8265 is 1.7–8.2 KB/vsync. e50f (7600, a
different state) had ~346 KB/vsync on PATH3, so the recomp does stream in
some states. (T48's PCSX2 path tap puts all 1.8 MB/vsync on "PATH1";
that mapping looks unreliable and isn't used here.)

### Textures sampled (vsync 0 of the dump / recomp 8261), with VRAM content

PCSX2 top keys (TBP, TBW, PSM, size, CBP): prims; nonzero fraction of the
texture's VRAM range in PCSX2 / recomp:

| TBP | psm | size | CBP | PCSX2 prims | what it is (decoded) | VRAM nz PCSX2 / recomp |
|---|---|---|---|---|---|---|
| 14857 | T4 | 128² | 16367 / 16368 / 10996 / 10952 | 4,259 / 3,172 / 922 / 652 | bare tree (re-uploaded per frame) | 0.28 / 0.24 |
| 15241 | T8 | 256² | 15497 | 1,849 | rider outfit | 1.00 / 0.60 |
| 12777 | CT32 | 128² | — | 1,266 | scrambled yellow (per-frame target; looks the same in both) | 0.71 / 0.64 |
| 14953 | T4 | 128² | 10958 | 1,101 | **snow** | 1.00 / 0.55 (recomp slot = a bare tree) |
| 14569 | T4 | 32² | 10995 | 960 | | 0.25 / 0.72 |
| 14313 | CT32 | 128×64 | — | 430 | **snow/trail** | 0.99 / 1.00 (recomp slot = noise) |

Recomp top keys (startPC shares):

| TBP | psm | size | CBP | recomp prims | programs | what it is | VRAM nz recomp / PCSX2 |
|---|---|---|---|---|---|---|---|
| 13417 | T4 | 128² | 10990 | 3,724 | 0x22c8 3,031, 0x2270 693 | snowy pine | 0.74 / 0.31 |
| 13513 | T4 | 128² | 10991 | 2,508 | 0x22c8 1,881, 0x2270 627 | snowy pine | 0.76 / 0.71 |
| 13257 | T4 | 32² | 10987 | 760 | 0x2270 | **near-empty page** | **0.06** / 0.69 |
| 13289 | T4 | 32² | 10988 | 722 | 0x22c8 400, 0x2270 322 | **near-empty page** | **0.06** / 0.30 |
| 14953 | T4 | 128² | 11008 | 315 | 0x22c8, 0x2270 | bare tree | 0.55 / 1.00 |
| 14185 | T8 | 256² | 10756 | 91 | 0x22c8, 0x2270 | sky dome | 1.00 / 0.97 |

No (TBP, CBP) key is shared between the two frames: the texture cache
allocates per frame, and the scenes differ. Decoded samples are in `tex/`
(`p-strip.png` = PCSX2 12777 | 13449 | 14313 | 14953;
`r-strip.png` = recomp 14953 | 14313 | 12777 | 13513).

### Terrain-program prims: ST/Q/UV, TEX1, zero-area

| side | pc | psm | prims | zero-area | Q min..max | Q ≤ 0 | NaN/Inf ST | max \|S/Q\| | max \|T/Q\| | TEX1 (mode) | CLAMP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PCSX2 | — | T4 | 12,443 | 93 | 3.3e-05..1 | 0 | 0 | 4 | 5 | 0xffffff4e00000168 | 0 |
| PCSX2 | — | T8 | 4,251 | 26 | 2.3e-04..0.055 | 0 | 0 | 1 | 1 | 0x61 | 0 |
| PCSX2 | — | CT32 | 3,073 | 50 | 3.3e-05..1 | 0 | 0 | 32 | 1 | 0x61 | 5 |
| recomp | 0x22c8 | T4 | 5,878 | 64 | 3.6e-05..1.5e-04 | 0 | 0 | 3.97 | 4.88 | 0xfffff80100000168 | 0 |
| recomp | 0x2270 | T4 | 2,814 | 60 | 3.6e-05..1.5e-04 | 0 | 0 | 3.97 | 4.95 | 0xfffff80100000168 | 0 |
| recomp | 0x6b8 | T4 | 198 | 0 | 3.5e-05..1.0e-04 | 0 | 0 | 4 | 5 | 0xfffff80100000168 | 0 |

TEX1 = LCM 0, MXL 2, MMAG 1, MMIN 5 (low word 0x168) on both sides.
**K** (bits 32–43, signed 7.4):

| | K values seen (TEX1 writes over the window) |
|---|---|
| PCSX2 | 0xf3c ×56, 0xef2 ×40, 0xf23 ×40, 0xf1f ×40, 0xf28 ×24, 0xf32 ×24, 0xf47 ×16, 0xf0b ×8, …: per object, −17.1 … −11.1 |
| recomp | **0x801 only** (−127.94), all on PATH2 from the terrain/object programs' packets (0x2270 203, 0x22c8 155, 0x6b8 284) |

### Recomp per-startPC census (8256–8265, 9 drawing vsyncs)

| tpc | MSCAL/vsync | PATH1 draws/vsync |
|---|---|---|
| 0xd7 | 8.6 | 308 |
| 0x257 | 41.0 | 187 |
| 0x44e | 104.6 | 2,916 |
| 0x459 | 121.6 | 5,667 |

T65 §6 (PCSX2 race) runs 22 startPCs. Missing here: 0x10, 0xe, 0x4,
0x134, 0x147, 0xf2, 0xe0, 0xfb, 0x741, 0x22a, 0x0, 0xa, 0x6, 0x73, 0x2,
0x8, 0x28c, 0x140.

T65-format PATH1 counts (gfx stats): on 8,684–9,232, off 218–229,
straddle 54–56, zero-area 96–128, ADC 332–346 per drawing vsync.

### The VU0 call (static; `ee-at`, `ee-func`, `ee-xref`, codegen)

| Address | Instruction | Generated code |
|---|---|---|
| 0x37de88–0x37dea8 | `lui/addiu $v0 = 0x570; srl 3`; `lqc2 vf15, 0(a1)`; `lqc2 vf16, 0(a2)`; `lqc2 vf10..vf13, 0..0x30(a3)` | |
| 0x37deac | `ctc2.ni $v0, $vi27` (CMSAR0 = 0xAE) | `ctx->vu0_cmsar0 = GPR_U32(ctx, 2);` |
| 0x37deb8 | `vcallmsr $vi27` | `instr_index = ctx->vi[27] & 0x1FF; … vu0StartMicroProgram(…, instr_index << 3)`: **reads vi[27], not vu0_cmsar0** |
| 0x37debc–0x37dec8 | `cfc2.i $a0, $vi1`; `cfc2.ni $v1, $vi2`; `bnez $v1` | result consumed by the caller |

`0x37de88` has no static callers; it's a vtable slot (0x49354c) next to
`0x37dbe8`'s (0x49353c), the class of E50's camera builder `0x37d968`.
The other VCALLMSR sites (E52 table): 0x22aa4c (`sub_0022A830`, self-
recursive ×5), 0x2d20c0, 0x1223f0, 0x391470, 0x32b6d0, 0x3fe824.

## Gaps

- The visibility-test role of `0x37de88` is inferred from its shape and
  class. It wasn't measured (no call counts or return values).
- The K builder wasn't found. `0x3680b4`'s `+0x801` is sprite XYZ
  packing, not TEX1.
- The VU1 budget-exit program is still unidentified (none in this
  window).
- The PCSX2 dump can't be split by path.
- The race diverges between runs, so exact same-moment comparison isn't
  possible with the current route.

## Receipts

- In this dir: `e51_boot.sh`, `e51_gif.py`, `e51_tables.py`,
  `e51_texdump.cpp`, `gfx-e51a.txt`, `gif-e51a.bin.gz` (1,114,026 B),
  `frames/`, `tex/`.
- Raw (`~/dev/ssx3-work/E51/`, short SHA-256, bytes): boot-e51a
  `26afe8639589ab96` 10,874,867; gif-e51a `c5f9e541d618e734` 4,553,624;
  gfx-e51a `87fdac85a9ffd7f8` 47,587; E4 VRAM arm `6a92cb8e3fb3341b`
  4,194,304; PCSX2 dump `pcsx2-race.gs` (from T65 `t65a-race.gs.zst`
  `aa56234a…`, decompressed 20,258,277 B) and its VRAM `pcsx2-vram.bin`
  `0644f7db598dcb50`.
- Budget: 1/3 boots, ~1 h 45 min. E51 dir 62 MB; internal total 62.1 of
  200 GB.
