# RP1 report: race visual polish (what still differs from a real PS2)

Exploratory session (Claude Code, Opus 5.5), 2026-09-25 16:11–17:10 EDT (about 1 h of the 3 h box).
Notebook: `NOTEBOOK.md`. The orchestrator decides; labels say what was measured and what is a guess.

## Outcome

**The most visible remaining difference was the missing snowboard carve trail**: PCSX2 draws a bright
white raised groove behind the board in almost every riding frame; ours drew nothing there, or a pale
translucent box (the trail's stencil passes with nothing to fill them).

**Mechanism (measured end to end): VU1 `MAX`/`MINI` flushed denormal operands to zero.** SSX 3's trail
program (VU1 0x3a08, MSCAL imm 0x741) interleaves the trail's two rails and copies each vertex's RGBA
*integers* with `MAX.xyzw vf09, vf04, vf04`. Colour words such as 0x6E/0x7F are denormal bit patterns as
floats. Our `execUpperImpl` passes every FMAC operand through `normalizeOperand` (exponent 0 → ±0) before
the compare, so the copy came out RGBA 0 and the textured trail blended to nothing. PCSX2 (`VUops.cpp:791`
`fp_max`/`fp_min`) compares the raw bits as sign-magnitude integers and passes the operand through. Our EE
macro-mode `Ps2VuMax`/`Ps2VuMin` already did the same; only VU1/VU0 micro mode was wrong.

**Fix:** fork branch `rp1-polish` (local, not pushed) commit **`9bfd4aa`**: MAX/MINI (plus the bc and I
forms) on raw bits. Shared by the interpreter and the generated VU1 images. The trail now matches PCSX2
(frames below). Guest state is unchanged: rdram, scratch and eeCycle are identical at every tick.

## Difference table (ranked by visibility; race on the Happiness course, Mac paraLLEl vs PCSX2 own run)

| # | Difference | Where seen | Cause | Status |
|---|---|---|---|---|
| 1 | **Carve trail missing** behind the board (PCSX2: white raised groove) | every riding pair: 13 %, 23 %, 27 %, 44 % … | VU1 MAX flushes integer colour words → trail RGBA 0 (measured) | **fixed** `9bfd4aa` |
| 2 | Pale translucent boxes/bubbles around and below the board (00:11 braking spray, 00:35 bubble, 00:41 by the rock) | t2400, t3900, t4200 | same: the trail's alpha-only stencil passes (FBMSK 0xFFFFFF, FBA, DATE) drawn with zero colour | **fixed** (same commit; after-frames viewed) |
| 3 | Distant riders' trails faint | TBP 12777 strip at t2398 (A 0–14 before, 0–128 after) | same | **fixed** |
| 4 | Snow-spray particles "hard-edged" | t2400 | were #2, not the particles: the CT32 spray textures are soft (edge alpha 0–1 in the upload data, `rp1_texdump.py`) | no separate fault found |
| 5 | Our rider slower than PCSX2's (14 % at 00:41 vs 19 % at 00:39); different trick score | gallery | different start state: PCSX2 runs from T65's statefile, ours is FR1-R1 from boot. Gameplay, not rendering | not a visual fault (not investigated) |
| 6 | Same-state boots present frames one frame apart (trick counter 180 vs 190 at t2098) | hA/hB | known racy present latch (GB2/HR1). Guest identical | known, not a device-visible fault |
| 7 | "SUPER UBER" label absent in some early frames (00:06–00:26) where PCSX2 shows it faintly | g2 t2700–3300 vs PCSX2 00:25/00:30 | guess: trick-meter state (it appears in ours from 00:31 on) | low confidence, not investigated |
| 8 | Mip/LOD and fog on distant terrain | vista frames (55 % ours, 32 % PCSX2) | no visible difference at 512×448 vs PCSX2 640×480, but no same-camera pair | none found |
| 9 | Backdrop / CLUT | all pairs | sky, panorama and colours match PCSX2 by eye (RR1 E5 measured the CLUT equal) | none found |
| 10 | Pop-in | c2 capture ticks 2200–2300 (`receipts/flash-c2.txt`) | only animated PSMT8H particle pages and one 29-prim CT32 class (TBP 14121) come and go; HUD prims 83 on every tick | none found in this window |

PATH3 window-count gap (RR1): not re-measured. RR1's own final boot already had ≤ 1 leftover packet per
frame besides the frame-start post packet, and no frame in this gallery showed a depth/post artefact.

## Evidence

| Row | Measurement | Before (ours) | PCSX2 / after fix | Receipt |
|---|---|---|---|---|
| E1 | Trail draw sequence, tick 2398 | TBP 14281 CT32 128×64: alpha-only clear (Z ALWAYS) → FBA=1 mark (Z GEQUAL) → DATE/DATM=1 Z write → textured FBA=1 strips/fans → DATE/DATM=0 pass | PCSX2 T48b vsync 1: the same sequence (TBP 14313) | `receipts/trail-batches-ours-2398.txt`, `…-pcsx2-t48b-v1.txt` |
| E2 | Trail vertex RGBA | fans **all 0**, strips mostly 0 (R 0–118, A 0–127) | PCSX2: every vertex RGB 0x6E–0x77, A 0x7F | `rd1_draws.py`, per-vertex dumps (NOTEBOOK 16:35) |
| E3 | CPU backend on our stream | same box, no trail | → not a paraLLEl bug; stream fault | `cpu-vs-par-2398.png` (scratch) |
| E4 | VU1 input for the trail (probe p1, tick 2398) | V4_32 [ST, RGBA ints, XYZW], RGBA 0x6E–0x7A / A 0x7F | = PCSX2's output colours | `probe/p1.trace` (scratch) |
| E5 | VU1 output (XGKICK 812 dump) | RGBAQ row = 0; ST/XYZ match the capture | → colour lost inside VU1 program 0x3a08 | `probe/p1.trace` |
| E6 | Program 0x3a08 (disassembled from T65 micro memory) | rail copy via `MAX.xyzw vf09, vf04, vf04` / `MAX.xyzw vf06, vf02, vf02`, last pair stored without MAX | explains zero colours + the few non-zero vertices | `rp1_vudis.py` (listing kept in scratch: game-derived) |
| E7 | Our MAX semantics | `normalizeOperand` before compare (denormal → ±0) | PCSX2 `fp_max`: raw signed-int compare | `ps2_vu1_upper_impl.h`, PCSX2 `VUops.cpp:791` |
| E8 | Det-hash A/B (hA runner-probe vs hB runner-fix, ticks 1..2400) | — | first_diff = **1756, vu1Data only**; rdram/scratch/eeCycle/vu1Code equal at all 2,458 ticks | `receipts/hashdiff-hA-hB.txt` |
| E9 | Draw-level diff, tick 2398 (c1 before vs c2 after) | 27,158 prims | 27,158 prims; **only vertex RGBA differs, on 1,014 prims**: 954 trail prims all-zero → 0, plus 60 distant-trail prims | `receipts/primdiff-2398.txt` |
| E10 | Same-stream CPU replay, tick 2398 | — | 25,233 px changed, all in the trail region (bbox (228,271)–(512,447)); sky and top/left HUD unchanged | `ab-2398-replay.png` (scratch) |

## Fix, tests, checks

- Fork worktree `~/dev/ssx3-work/RP1/PS2Recomp`, branch **`rp1-polish`** from fork `ssx3` `8559ab9`, not pushed:
  - **`9bfd4aa`** `[RP1] VU MAX/MINI compare raw bits: no denormal flush (carve trail colours)`:
    `ps2xRuntime/src/lib/vu/ps2_vu1_upper_impl.h` +23/−8, `ps2xTest/src/ps2_vu1_tests.cpp` +35
    (2 files, +58/−8). **This is the commit to fold.**
  - `f233fc5` dev probe (cherry-pick of RD1 `1f3180d`, default off) and `edce9dd` dev knob
    `PS2X_FRAME_DUMP_EVERY=N` (default off). Dev tooling only; skip when folding.
  - Total vs `8559ab9`: 7 files, +367/−10.
- Test "RP1: MAX/MINI compare raw bits and keep integer data (no denormal flush)": **red 650/651** on the
  unfixed tree (only the new test fails, all four checks), **green 651/651** rc 0 with the fix; both runs
  from the worktree root (`receipts/suite-red-tail.txt`, `suite-green-tail.txt`).
- Runner-dir check: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` is **empty**.
- Build: Release, Homebrew clang, det-hash tap ON, diag taps/logs OFF, `GS_SHADOW_PARALLEL=ON`, paraLLEl
  `19d93b2` (F2 worktree, read-only), VU1 images `~/dev/ssx3-work/vu1gen-ssx3`, codegen = APFS clone of F4's
  unpromoted codegen (`register_functions` `8ea8ed43…`, `sub_003FE828` `89953ba2…`) at `RP1/codegen`.
- Runners (two matching SHA reads each): `runner-base` `c77898b6…` (8559ab9 + frame-dump knob),
  `runner-probe` `02282804…` (+ probe), **`runner-fix` `3a5a8367…`** (+ fix). hA/hB differ only by the fix.
- No speed numbers (det-hash tap on). The change is per-lane integer compares instead of float compares:
  no expected speed effect.

## Frames to view (all under `~/dev/ssx3-work/RP1/`, scratch only)

| What | Path |
|---|---|
| **Before / after, same stream, CPU replay, t2398 (+ diff mask)** | `ab-2398-replay.png` |
| Before / after, paraLLEl live, t2398 and t2098 | `ab-2398.png`, `ab-2098.png` |
| Before / after at t2400 (braking spray moment) | `spray-2400.png` |
| **Before / after / PCSX2 at 13 %, 14 %, 27 %** | `triples-1.png` |
| After vs PCSX2 at 42–65 % | `triples-2.png` |
| Before (g2) vs PCSX2 matched pairs, 13–45 % | `pairs-1.png`, `pairs-2.png`, full-size 27 % `pair-27.png` |
| Late-course after frames (69–77 %) | `g3-late.png` |
| The pale box (contrast-stretched crop, before) | `crop-c1-spray.png` |
| PCSX2 own-run shots | `pcsx2/rp1a/` (00:18–01:31), `pcsx2/rp1b/` (to 85 %) |
| Raw frames | `run/g2/frames/` (before, every 300 ticks to 11,700), `run/g3/frames/` (after, to 12,900) |

## Boots (Mac mini, `PS2X_DETERMINISTIC=1`, paraLLEl + `PGS_HIER_BINNING=force`, `PS2X_SOUND=1`, `rp1_boot.py`)

| Boot | Runner | Route | Slot | Bound / wall | Last tick | Purpose |
|---|---|---|---|---|---|---|
| g1 | base | FR1-R1 | 1 | hash_error (det-hash 4096-line cap) 151 s | 4095 | first gallery (superseded) |
| g2 | base | FR1-R1 | 1 | wall cap 590 s | 11,920 | before gallery, 1 frame / 300 ticks |
| c1 | base | I26 | 4 | target 79 s | 2403 | GS capture to 2401 (before) |
| p1 | probe | I26 | 1 | target 92 s | 2404 | one-tick VIF1/VU1 trace + XGK dumps, `PS2X_VU1_RECOMP=0` |
| p2 | probe | I26 | 1 | target 88 s | 2404 | VU1 memory at MSCAL 209/221 (not needed in the end) |
| hA / hB | probe / fix | I26 | 2 / 3 | target 74 / 76 s | 2401 / 2408 | det-hash A/B + frames |
| g3 | fix | FR1-R1 | 4 | wall cap 590 s | 13,000 | after gallery |
| c2 | fix | I26 | 2 | target 73 s | 2410 | GS capture to 2401 (after) |

All `gs_fatal=null`. PCSX2 on bytesize (`rp1_pcsx2.sh`, bytesize otherwise idle): T65 build `pcsx2-qt` with
`-statefile t65-race-state` (00:00:18), no inputs, F8 every 20 s (rp1a, 14 shots) and every 30 s (rp1b,
29 shots, 880 s cap), datapath `~/rp1/dat-rp1` (copies of dat-t48's inis/bios/memcards). It runs at about
0.3× race-clock speed under Xvfb (llvmpipe GL).

## Gaps

- No same-camera PCSX2 frame: pairs are matched by course progress %, so fog/mip/LOD verdicts (row 8)
  are by eye on different views.
- PCSX2-on-our-stream still doesn't draw the race world (PX1), so it can't serve as a pixel reference for
  the race.
- The fix was validated on the Mac (paraLLEl live + CPU replay). No Odin or iOS run. The code is shared by
  every platform and by both VU1 paths.
- VU0 micro mode uses the same `execUpperImpl`, so it gets the fix too; no VU0 micro-program was observed in
  the race (T57 found none at Select Character).
- Other FMAC ops still normalize operands. That's correct for arithmetic (hardware treats denormals as
  zero), and only MAX/MINI pass an operand through unchanged.
- Row 7 ("SUPER UBER") and the rider-pace difference weren't investigated.
- Scratch: `~/dev/ssx3-work/RP1` 7.4 GB (two 2.3 GB captures `run/c1`, `run/c2`, build 1.8 GB). The
  captures and `t65-vu1-2.bin` (36 MB copy of T65's dump) can go after the gate. ssx3 internal 135/200 GB.

## Next (the orchestrator decides)

1. Fold `9bfd4aa` alone onto fork `ssx3`. It touches one VU header, so the VU1 images rebuild. Then run
   the suite, one det race boot, and view frames. Include it in the next Odin/iPhone build: the trail is
   in every race frame.
2. Optional audit: grep the other VU1 upper/lower paths for operand normalization on pass-through ops.
   From the code read, only MAX/MINI move data unchanged, but `MOVE`/`MR32` (lower) weren't reviewed here.

## Tools (this dir)

`rp1_boot.py` (F4 driver + `--route fr1r1`, `--dump-every`, `--dump-ticks`, `--hash-every`, `--wall`,
`--env`), `rp1_pcsx2.sh` (PCSX2 statefile + timed F8 shots), `rp1_sprites.py` (per-sprite dump),
`rp1_texdump.py` (IMAGE upload extraction by DBP + alpha stats), `rp1_vudis.py` (VU upper/lower disassembler
over T65 micro memory), `rp1_t65find.py` (T65 start headers), `rp1_primdiff.py` (draw-level diff of two
captures), `rp1_sheet.py` (contact sheets; needs Pillow via `uv run --with pillow`).
