# M16 — Same-frame residual attribution (warp leave-one-out): REPORT

M15's synth-vs-truth residual attributed to draws ON THE SAME recorded
frame: one run records one frame; on it a verbatim 3-phase triplet
(the frame's total residual R_0 = 22815 B) plus a per-draw
v0/mid/full triplet for every consuming draw (764 shapes); the warp
synth runs offline per shape (`loo.py`), and each draw's removed
share is R_0 minus its shape's surviving residual. Desktop only.
Runbook `local/muse/prompts/M16.md`. No `adb`, no device. Tables, no
verdicts.

Headers read first: `local/research/M15/REPORT.md` (all of it: the
3-phase capture design, `synth.py`'s warp/blend synth, the 13418-B
synth-vs-truth residual, the arm-B carrier guide and its own-frame
caveat), `local/research/M14/REPORT.md` (the step-2 true-delta arms,
the step-3 autoscan carriers, the header/player/analyzer system, the
determinism evidence).

Time box 6 hours; used about 1. No lease waits (lease absent at
claim; one annotation for the attempt-1 timeout; claim/release pair
logged in `local/research/M16/waits.log`; never forced).

## Baseline note (read before the tables)

The M15 header on disk (`local/research/M15/m15_replay_context.h`,
clean tree) hashes to
`910163fa413995a487e16ff43e4fdf7ccfe388ceb76bf1f71c39eea92aeb87de`
via `shasum -a 256` (trust `shasum`, not memory; matches the M15
report's committed sha). Step 1 copied the on-disk file verbatim to
`local/research/M16/m16_replay_context.h`, then added the M16 delta
(`diff -u` M15→M16 is §Header diffs, nothing else). Every
M5–M15 mechanism is kept: the M16 additions are env-gated with
defaults that preserve M15 behavior (`SSX_M16_LOO` unset). The
committed header is `64501bdc…`.

M16 mode (`SSX_M16_LOO=1`, drawscan-wanted only, mutually exclusive
with autoscan — autoscan wins when both are set): a 6(C+1) sequence
in six contiguous (C+1) blocks — v0a/v0b (seam disarmed), mida/midb
(slot armed, `s_m15_scale=0.5` → +0.05 truth), fulla/fullb (scale
1.0 → +0.1). Per-shape reference = last v0b rep (kref = (C+1)+s,
warm); v0a uniformity rests on hash equality (no second stash —
RAM budget); mid/full rows record live; one `m16_win` guard line +
one `m16_ref2` event per replay (4584 rows). Dumps (fail-soft,
receipted in `m16_win`): v0 refs post-loop from the M13 stash,
mid_b/full_b per replay, to `$SSX_M16_DUMP_DIR/m16-{v0,mid,full}-sNNNN.bin`.
The inherited M13 per-shape tallies span mid+full (n2=4; tabled as
observed).

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock`, as M15. `m16-*` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile
directories are fresh per run. Each desktop run held
`/tmp/ssx3-host-lease` (`printf 'M16\n'`, removed after the final
run). `complete_hazard_resets`: 0 on the final run (attempt 1 has
no value — killed before the observation wrote it); the final
sequence is complete with `done` and clean counters (see tables).

| Arm | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| A leave-one-out | `64501bdc…` (= committed M16) | `players/m16-loo` | `m16-loo-run` (`m16-loo2`, `SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M16_LOO=1 SSX_M9_SURV=1 SSX_M16_DUMP_DIR=/Volumes/Extreme SSD/m16`, `--seconds 540`) | `m16-loo-probe.jsonl` |

Player dirs live under `local/research/M16/players/` (the build
driver requires outputs under `local/`). Run dirs, probes, dumps,
synths, and analyzer outputs live under `/Volumes/Extreme SSD/m16/`
(symlink-free; `realpath` is the path as written). Probes, runs,
dumps, synths, and players are not committed (players: per M14
precedent — repo evidence `git ls-files local/research/M14/` shows
M14 players are gitignored build outputs, present but never
committed).

Attempt log (`m16-loo` profile, `--seconds 240`, same env otherwise):
the 6072-replay sequence on that run's frame (520139 B / 4242
updates, C+1 = 1012) outlived the 240 s native budget — SIGKILLed
(exit −9) at replay 5089 (wall 254.8 s = 240 s deadline + 15 s
grace), with 1012 mid + 30 full dumps written and no v0 dumps or
post-loop rows. Receipts kept as `m16-loo-probe-attempt1.jsonl`
(3892818 B), `m16-loo-run-attempt1/`, `m16-loo-run-attempt1.log`;
partial dumps cleared. Fix: `--seconds 540` (as-run change,
recorded with receipts — the 6(C+1) scan needs pre-sequence +
6(C+1)×~25 ms + post-loop inside the budget; sizing rule in
"What I could not do" 6), fresh profile `m16-loo2`, re-ran.

## Per-step wall table (final arm)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m16-loo | 4584 | 5.728 / 21.043 / 4.795 / 25.300 | 2.164 / 12.347 | 332610 / 2855 | YES | seq_wall_ms=101464.972 completed=4584 xfb_equal=4584/4584 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/4584 live_xfb_untouched=1 live_same=4584/4584 |
```

Frame differs per run, so the wall median is not comparable across
rows as a mechanism cost (M5 §Per-step wall table). Complete
sequence, `done`, `restored det=1 dual=1`, `mask_bp=2 dls=0
walk=100% unknown=0 benign=1`. `xfb_equal_scratch=0/4584` is the
forced-RAM signature (rendered scratch vs fuchsia live ref), not a
failure. All capacity rows carry `xform=1` (inherited:
`xform_flag` includes `m9_mode != 0`; M15 reads identically).

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m16-loo | 0.123 | 0.001 | 0.045 | 5.566 | 0.000 | 19.890 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m16-loo | 1646 | 79008 | 26.5 |

## Step 1 — design (recorded before running; `DESIGN.md`)

Mechanics choice (implementer's call, recorded before running):
chosen = per-draw withheld synth. For each shape s on the one
recorded frame, render v0_s/mid_s/full_s, warp offline per shape
(M15 estimator verbatim), residual R_s = xd(synth_s, mid_s);
removed share_s = R_0 − R_s (M14 removed-share shape). Rejected:
in-harness residual-delta tallies (the warp needs full frames
offline). Degenerate-mask rule (<64 moved-Y px → shift (0,0)),
recorded before running; 0 shapes hit it.

Schedule: 6(C+1) contiguous blocks (v0a/v0b/mida/midb/fulla/fullb),
2 reps per (shape,phase) — the M15 floors (mid/full 50/50
identical, v0 99/99 + cold r0) plus M14 2P+2D (n2=2 bounds
predecessor-dependence) justify n=2. Total 1.5x autoscan (the
brief estimated ~3x; recorded with rationale). Dumps: v0 from the
ref stash post-loop, mid_b/full_b per replay (fail-soft); v0a
uniformity via hash equality (no second stash — RAM budget).

As-run change (recorded with receipts): `--seconds 240` → `540`
(the attempt-1 timeout; the 6(C+1) sequence needs pre-sequence +
sequence + post-loop inside the native budget). No estimator
fallback needed: full 49² masked-SAD search ran on all 764 shapes
(539.2 s over 8 workers).

## Step 2 — runs (per-arm: wall, exit, probes, determinism)

Exit 0. Probe receipt: `m16-loo-probe.jsonl` 52614717 B
(`0cbdb34a…`).

Arm guard receipt (`m16_win`): `loo=1 nshapes=764 nreps=4584
kfrom=1528 kfull=3056 xfbbytes=573440 dv=764 dm=764 df=764
uv0=763 uvm=764 uvf=764` — all 2292 dumps ok (each exactly
573440 B); mid/full pairs 764/764 uniform; the single v0 miss is
the shape-0 cold pair (below). Dump-vs-probe FNV cross-check
(recomputed in `loo.py`): 0/2292 mismatches.

Per-(shape,phase) group rows (4584/4584 ok=1; full 764-row
per-shape table + 4584-row per-replay table in `analyze-loo.txt`):

| group | n | ok | um1 | xd2 min / max | distinct xd2 | distinct hashes |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| v0a | 764 | 764 | 763 | 0 / 0 (hash rule) | 1 | 374 |
| v0b | 764 | 764 | 763 | 0 / 0 (is-ref) | 1 | 373 |
| mida | 764 | 764 | 764 | 19974 / 29956 | 129 | 374 |
| midb | 764 | 764 | 764 | 19974 / 29956 | 129 | 374 |
| fulla | 764 | 764 | 764 | 30703 / 45167 | 152 | 373 |
| fullb | 764 | 764 | 764 | 30703 / 45167 | 152 | 373 |

Non-uniform ok rows: exactly 2 — the shape-0 v0a/v0b pair (r=0
`98ca9ade15440e0f`, cold first-replay frame; r=764
`bfca778291ac3ec0`, the ref). Zero mid/full non-uniformity
(M14 det4 read 25/644 spread ≤10 B; here 0/1528 pairs).

Shape-0 (verbatim control) rows:

| r | phase | rep | ok | xd2 | xdmax | xdmean | hash |
| ---: | --- | :-: | :-: | ---: | ---: | ---: | --- |
| 0 | v0 | a | 1 | 0 (hash rule, um=0) | 0 | 0.000 | `98ca9ade15440e0f` |
| 764 | v0 (ref) | b | 1 | 0 | 0 | 0.000 | `bfca778291ac3ec0` |
| 1528 | mid | a | 1 | 29601 | 99 | 1.421 | `070fc31fa7507425` |
| 2292 | mid | b | 1 | 29601 | 99 | 1.421 | `070fc31fa7507425` |
| 3056 | full | a | 1 | 44976 | 115 | 2.087 | `0999001c76ed8bc4` |
| 3820 | full | b | 1 | 44976 | 115 | 2.087 | `0999001c76ed8bc4` |

Offline/probe agreement: `loo.py` recomputes mid-vs-v0 29601 and
full-vs-v0 44976 from the shape-0 dumps — identical to the live
probe rows.

Arm B-style guard receipts (inherited M13 aggregate, spans
mid+full, tabled as observed): `m13_win`: `scan=1 slot=0
scheme=modN nshapes=764 ndraws=763 cap=763 sel_shr=0 sel_idx=0
sel_text=0 m10nop_ok=0` — shape 0 is the verbatim total.
`restored` carries `m14auto=0 m14cap=763 m14reps=4584
m14from=1528 m14perrep=0 m15mid=0 m16loo=1 m16kfull=3056`. All 763
per-draw NOP spans ok=1. The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Shape-0 inherited row: `shape=0 kref=764 refok=1 n2=4 gt0=4
uniform2=2 xd2min=29601 xd2max=44976 xdmax2max=115
xdmean2min=1.421 xdmean2max=2.087 refhash=bfca778291ac3ec0`
(uniform2=2: the two mid hashes match the first-delta hash; the
min/max span mid+full by design).

Inherited spanning top-10 (xdmax-based, full-phase-dominated;
NOT the attribution — the corroboration table for §Step 3):

| rank | clk | shape | surviving xd2 | removed share | samp |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 1496 | 694 | 30703 | 14273 | r2222:19974/99/1.598,r2986:19974/99/1.598,r3750:30703/115/2.441 |
| 2 | 1495 | 693 | 41568 | 3408 | r2221:27316/99/1.449,r2985:27316/99/1.449,r3749:41568/115/2.145 |
| 3 | 1503 | 701 | 43146 | 1830 | r2229:28640/99/1.343,r2993:28640/99/1.343,r3757:43146/115/1.927 |
| 4 | 419 | 369 | 44287 | 689 | r1897:29226/99/1.436,r2661:29226/99/1.436,r3425:44287/115/2.108 |
| 5 | 416 | 366 | 44305 | 671 | r1894:29234/99/1.454,r2658:29234/99/1.454,r3422:44305/115/2.126 |
| 6 | 418 | 368 | 44318 | 658 | r1896:29253/99/1.431,r2660:29253/99/1.431,r3424:44318/115/2.114 |
| 7 | 1530 | 728 | 44403 | 573 | r2256:29205/99/1.424,r3020:29205/99/1.424,r3784:44403/115/2.093 |
| 8 | 1529 | 727 | 44470 | 506 | r2255:29279/99/1.423,r3019:29279/99/1.423,r3783:44470/115/2.093 |
| 9 | 426 | 376 | 44494 | 482 | r1904:29343/99/1.425,r2668:29343/99/1.425,r3432:44494/115/2.102 |
| 10 | 415 | 365 | 44495 | 481 | r1893:29355/99/1.427,r2657:29355/99/1.427,r3421:44495/115/2.102 |

Second-half corroboration: `xform_stats` hits=375888 (=
3056 × 123 covering loads; mid+full blocks); matrix before/after
at the first hit (a mid replay) is +0.05 on word 3 only
(`3d4ccccd`, 11/11 siblings bit-identical, `mm_live=3056
mm_snap=3056`); post live/snap word 11 reads `80000000` vs
`c0000000` at the first hit (tabled as observed, cf. M14's
word-11 note). M9 trichotomy over the second half reads
1528/0/1528 in live, per-vertex and shared-pos snapshots
(`xf_after=1528 xf_other=1528 pos_after=1528 pos_other=1528`,
`pos_res=3056 tex_res=0 dirty_post=0`) — the inherited
instrument bins the 1528 mid replays as "after" (first-hit
value 0.05) and the 1528 full replays as "other" (0.1); first-hit
before/after hexes are 0 → 0.05 with `vb_mm=354496
va_mm=365192` (the full-phase 0.1 hits mismatch the mid
first-hit value; tabled).

Own-frame M9 census, m16-loo (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1470 | 95 | n/a | n/a |
| Tex0 | 1565 | 0 | 1508 | 1508 |
| Tex1 | 1495 | 70 | 479 | 409 |
| Tex2 | 1565 | 0 | 21 | 21 |
| Tex3 | 1565 | 0 | 7 | 7 |
| Tex4 | 1565 | 0 | 7 | 7 |
| Tex5–7 | 1565 | 0 | 0 | 0 |

Shared-pos reach total 1470 (`0:763 3:67 6:94 9:85 12:102
15:79 18:106 21:50 24:68 27:56`); tex2 shared+enabled reach
`36:21`. Order row: draws=1565, verts=31055, covering=123,
cons_pos=763, cons_tex=0; first_cons=1 last_cons=1565; first
covering load draw 0 / off 2644, last 1501 / 321530; seam
375888 = 3056×123. EFB copies n=7 (6 texture + XFB drain at
draw 1565, `w=640,h=448` — the XFB geometry receipt for the
§Step 3 decode); `epoch_cons=9,9,9,1,1,1,733,0`; occ: cons=763,
culled=0, out-of-range=30, in-range=733;
`all_cull=all_scis=all_znever=0`.

Recorded without verdict: the 6-block scan renders 764
per-shape v0/mid/full triplets with 4584/4584 rows ok, mid/full
pairs 1528/1528 hash-identical, the only v0 miss the cold r0;
shape 0 moves 29601 B at +0.05 and 44976 B at +0.1 against its
own warm v0 reference.

## Step 3 — attribute (warp leave-one-out)

Decode receipt: dumps are 573440 B each; `m10_copy` gives the XFB
drain as `w=640,h=448` (640·448·2 = 573440 = YUYV). `loo.py`
decodes 640x448 YUYV → Y (640x448) + U/V (320x448); the decoded
base frame is a recognizable SSX3 race frame (`m16-base.png`).

Shift estimation (full ±24 masked SAD on the Y plane, all 764
shapes, 539.2 s over 8 workers; shape-0 full search 1.4 s):
shift distribution (dx,dy) = {(0,0): 764}; degenerate-mask rule
hits 0. Shape-0 masked best = (0,0), SAD 81268 = sad00
(nmoved-Y 33389). Every per-shape synth therefore equals its
blend byte-identically (shape-0 verified: blend fnv
`6b9ffda25bd76c6f` == synth fnv) — by measurement: no integer
translation in ±24 explains any shape's moved pixels better
than no shift, so the removed-residual maps below are exact.

Byte diffs (raw 573440-B frames, M14 §analyze.py shape):

| pair | xd | xdmax | xdmean | frac_moved |
| --- | ---: | ---: | ---: | ---: |
| full-vs-v0 | 44976 | 115 | 2.087 | 0.0784 |
| mid-vs-v0 | 29601 | 99 | 1.421 | 0.0516 |
| full-vs-mid | 31274 | 100 | 1.831 | 0.0545 |
| synth-vs-truth (R_0) | 22815 | 49 | 1.361 | 0.0398 |

Y-plane |d| histograms: v0-vs-full moved 33389 px with
[1: 21519, 2–3: 8338, 4–7: 2004, 8–15: 772, 16+: 756];
synth-vs-truth moved 14984 px with [1: 14021, 2–3: 368, 4–7:
280, 8–15: 140, 16+: 175] (93.6% at |d|=1). Residual-Y
vertical bands top/mid/bot: 5678/5300/4006 px — spread over
the frame, top-weighted (M15's frame read bottom-weighted;
frames differ per run).

Deliverable table — what interpolates cleanly vs what breaks:

| content | bytes | behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 528464 (92.16%) | synth byte-exact (no motion to interpolate) |
| moved (v0≠full) | 44976 (7.84%) | blend-synth leaves 22815 B residual vs truth (xdmean 1.36; 93.6% of residual Y px at |d|=1) |
| rigid-translation component | 0 px shift | masked SAD minimum at (0,0) on all 764 shapes: no integer global shift in ±24; motion reads as in-place value changes (sub-pixel/filtering scale) |

Residual attribution (same-frame per-draw withheld synth;
R_0 = 22815; full 763-row table in `loo.txt`):

Top-10 carriers by removed share (R_0 minus surviving R_s):

| rank | clk | shape | surviving R_s | removed share | draw bytes | shift | nmoved |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 1496 | 694 | 16290 | 6525 | 1203 | (0,0) | 21293 |
| 2 | 1495 | 693 | 21235 | 1580 | 1203 | (0,0) | 30567 |
| 3 | 1503 | 701 | 21689 | 1126 | 99 | (0,0) | 32454 |
| 4 | 418 | 368 | 22374 | 441 | 51 | (0,0) | 32935 |
| 5 | 419 | 369 | 22422 | 393 | 51 | (0,0) | 32951 |
| 6 | 416 | 366 | 22443 | 372 | 51 | (0,0) | 32953 |
| 7 | 420 | 370 | 22553 | 262 | 51 | (0,0) | 33079 |
| 8 | 426 | 376 | 22555 | 260 | 45 | (0,0) | 33101 |
| 9 | 1550 | 748 | 22570 | 245 | 99 | (0,0) | 33065 |
| 10 | 1552 | 750 | 22576 | 239 | 99 | (0,0) | 33060 |

Share arithmetic (total 22815; 763 shares):

| Field | Value |
| --- | --- |
| positive / zero / negative | 233 / 437 / 93 |
| max / min / median | 6525 (draw 1496) / −244 (draw 5) / 0 |
| distinct shares | 126 |
| sum of positive shares vs total | 18607 vs 22815 (81.6%) |
| top carrier fraction | 6525 / 22815 (28.6%) |
| top-3 combined | 9231 (40.5%) |

Share distribution (buckets): negative 93, exactly 0: 437,
1–99: 204, 100–499: 26, 500–1499: 1, 1500+: 2. Top-20 tail
after rank 10: 236/233/230/228/216/211/207/200/186/175.

Within-(shape,phase) uniformity (a/b pairs): 763/764 v0 (the
miss is the shape-0 cold pair), 764/764 mid, 764/764 full —
every attributed triplet's reps are hash-identical.

Negatives (93, range −244…−1): −244 clk 5, −228 clk 9, −219
clk 1502, −212 clk 6, −204 clk 4, −159 clk 3, −113 clk 22,
−90 clk 23, −84 clk 21, −66 clk 2, −57 clk 24, −53 clk 8
(remaining 81 in −53…−1; full list in `loo.txt`). The
early-draw pattern repeats M14/M15's (clks 2–9).

Removed-residual maps (residual_0 Y pixels vanishing in
residual_s; res0 = 14984 px; rows 0-148/149-297/298-447):

| rank | clk | shape | removed Y px | bands top/mid/bot |
| ---: | ---: | ---: | ---: | --- |
| 1 | 1496 | 694 | 4888 | 3415 / 1442 / 31 |
| 2 | 1495 | 693 | 1208 | 824 / 384 / 0 |
| 3 | 1503 | 701 | 649 | 186 / 463 / 0 |
| 4 | 418 | 368 | 448 | 0 / 0 / 448 |
| 5 | 419 | 369 | 248 | 0 / 0 / 248 |
| 6 | 416 | 366 | 244 | 0 / 0 / 244 |
| 7 | 420 | 370 | 191 | 0 / 0 / 191 |
| 8 | 426 | 376 | 174 | 0 / 0 / 174 |
| 9 | 1550 | 748 | 190 | 0 / 0 / 190 |
| 10 | 1552 | 750 | 202 | 0 / 187 / 15 |

HUD-edge draw identification (M15 gap 3 — the scan resolves
the bottom band): ranks 4–9 (clks 418/419/416/420/426/1550;
51/45/99-B draws) remove residual exclusively in the bottom
band (rows 298–447), the bottom-HUD zone (75 MPH / 3% glyphs
in `m16-diffmap.png`). Top-band HUD glyph edges (2ND/16,
timer) carry red residual with no single carrier above rank
10 claiming them — they fall in the long tail (tabled, not
isolated).

Scan cross-checks (table):

| Check | Value |
| --- | --- |
| `ndraws` vs `cons_any` | 763 = 763 |
| per-draw spans ok | 763 / 763 |
| `kref` = last v0b rep of shape | shape+764 on all 764 (shape 0: 764, warm) |
| `n2`/`gt0` pattern (inherited, spans mid+full) | 4/4 on shape 0 |
| seam hits vs 3056 × covering loads | 375888 = 3056×123 |
| dump-vs-probe FNV | 0/2292 mismatches |
| offline-vs-probe xd2 (shape 0) | 29601/44976 = 29601/44976 |
| synth==blend (all shifts (0,0)) | shape-0 byte-identical (`6b9ffda25bd76c6f`) |

Corroboration note (tabled, no verdict): the inherited
M13 spanning top-10 (§Step 2) ranks clks 1496/1495/1503
first/second/third — the same three draws head the
warp-residual attribution (6525/1580/1126). The spanning
aggregate overestimates rank-1's share (14273 vs 6525).

Screenshots (committed, 320x224 PNG): `m16-base.png` 123685 B
(v0: rider center, mountains/trees, chevron fence, HUD 2ND/16
+ timer + 75 MPH + 3% + trick/jump meters),
`m16-diffmap.png` 124723 B (truth + red residual overlay,
alpha ∝ |d|/32: red on mountain/rock edges, tree clusters,
rider + board, chevron fence, HUD glyph edges, jump meter;
sky and snowfields clean), `m16-carrier1.png` 115678 B,
`m16-carrier2.png` 115631 B (dimmed truth + red remaining
residual + green removed-by-carrier: carrier 1's green is the
god-ray shafts from the top + rider glow; carrier 2's is a
narrower shaft + rider area). Total 479717 B (budget
5242880). Synth/truth frames omitted (pixel-near-identical at
thumbnail scale; the diff-map carries the difference).

Recorded without verdict: one draw (clk 1496) carries 6525 B
(28.6%) of the 22815-B residual; the top 3 carry 40.5%;
233 read positive, 437 read exactly 0, 93 read negative
(worst −244); Σ positive = 81.6% of R_0; every shape's warp
reads (0,0), so synth == blend on all 764 triplets.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| leave-one-out mechanics + arm table + attribution criterion, recorded before running | recorded | `DESIGN.md`: per-draw withheld synth, 6(C+1) blocks, shares vs R_0 |
| lease-coordinated replays with per-arm wall/exit/probes/determinism | measured | §Step 2: 4584/4584 ok; m16_win all dumps + uniformity; attempt-1 timeout kept as log |
| per-draw residual shares on the synth frame (top carriers + distribution + negatives/zeros) | measured | §Step 3: top-10 + 763-row table; 233/437/93; Σpos 81.6% of R_0 |
| HUD-edge draw identification | measured (bottom band) | §Step 3: clks 418/419/416/420/426/1550 remove bottom-band-only residual; top-HUD glyphs in the tail |
| updated deliverable table: which draws carry the non-rigid remainder | measured | §Step 3: effect draws 1496/1495/1503 (40.5%) + HUD glyph draws + 204-draw tail |
| screenshots that discriminate | measured | 4 PNGs, 479717 B total; carrier overlays green/red |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m16-loo | `fc=8113` | `replay_disabled=0 fc=8116 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams
differ); the `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M15/M14/M13/M12/M11/
M10/M9/M8/M7 sequence hashes and all M6 sequence and M5
sequence/disabled hashes) is tabulated as observed. `resume fc
− fc0 = 3` (the live record window; per-replay `dframe` sums
are 0/0).

S2 item-5 honesty gate (original-frame equality, unchanged
guest and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m16-loo | 4584/4584 / 0/4584 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

Scratch `0/N` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `dafter` reads
1/1 (inherited: M15 reads identically). `present_trace`:
`pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with
zero `seq_*` (tracer's positive control intact, sequence
silent).

## Exact commands

Build (any time; only the header path differs from
`local/research/M15/build_replay_player.py`):

```
python3 local/research/M16/build_replay_player.py local/research/M16/players/m16-loo
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf
'M16\n'`, remove after the final run; profiles fresh per run;
`--seconds 540` is the as-run change from the attempt-1
timeout at 240):

```
SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M16_LOO=1 SSX_M9_SURV=1 SSX_M16_DUMP_DIR="/Volumes/Extreme SSD/m16" SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m16/m16-loo-probe-attempt1.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M16/players/m16-loo --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m16-loo --cpu-thread --output "/Volumes/Extreme SSD/m16/m16-loo-run-attempt1" --seconds 240
SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M16_LOO=1 SSX_M9_SURV=1 SSX_M16_DUMP_DIR="/Volumes/Extreme SSD/m16" SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m16/m16-loo-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M16/players/m16-loo --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m16-loo2 --cpu-thread --output "/Volumes/Extreme SSD/m16/m16-loo-run" --seconds 540
```

(The attempt-1 probe/run above were renamed with the
`-attempt1` suffix after the kill; the run itself used the
canonical names.)

Analysis + attribution:

```
python3 local/research/M16/analyze.py "m16-loo=/Volumes/Extreme SSD/m16/m16-loo-probe.jsonl"
python3 local/research/M16/loo.py "/Volumes/Extreme SSD/m16" local/research/M16 "/Volumes/Extreme SSD/m16/m16-loo-probe.jsonl" 8
```

## Player and run dir paths

Evidence dir (committed): `local/research/M16/` —
`m16_replay_context.h` (`64501bdc…`),
`build_replay_player.py`, `analyze.py`, `loo.py`, `DESIGN.md`,
`REPORT.md` (this file), `waits.log`, `m16-base.png`,
`m16-diffmap.png`, `m16-carrier1.png`, `m16-carrier2.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m16/` —
`m16-loo-probe.jsonl` (52614717 B, `0cbdb34a…`),
`m16-loo-probe-attempt1.jsonl` (3892818 B) and the matching
`-run` dirs and harness receipts; `m16-{v0,mid,full}-sNNNN.bin`
(2292 × 573440 B) and `m16-synth-sNNNN.bin` (764 × 573440 B);
`analyze-loo.txt`, `loo.txt` (full 763-row share table),
`m16-loo-run.log`, `m16-header.diff`. Players (gitignored):
`local/research/M16/players/m16-loo/` (`player`,
`build.json`, launchers). All paths above are symlink-free as
written (`realpath` identical).

Build receipts (`build.json`: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m16-loo`
`64501bdc30e5` / `555e763b7a52`.

## What I could not do

1. Sub-pixel / local motion model: the global integer warp
measured (0,0) on all 764 shapes, so the rigid component at
sub-pixel scale (or per-block motion) is untested — and the
residual's 93.6%-at-|d|=1 structure points there. Needs its
own brief: half-pixel bilinear SAD + block matching, offline
on the committed dumps + synths on the SSD — no new harness
code. (M15 gap 2, still open.)
2. Odin port readiness: no Odin contract exists in-repo (zero
matches for "odin" repo-wide), so readiness has no interface
to check against. The handoff artifact this run produces is
the per-draw residual-share table (`loo.txt` full 763-row
table + dumps + synths on the SSD). Needs its own brief once
the consumer names its interface (input format, per-draw
weights vs pixel masks, frame coverage).
3. Negative-share mechanism: 93 negatives (worst −244, the
M14/M15 early-draw pattern plus clk 1502 at −219) — removing
those draws widens the residual, but the byte-level source
(EFB-copy feedback texels? overdraw reveal?) is
unattributed. Needs its own brief: per-shape added-residual
maps (residual_s pixels absent from residual_0) + EFB-copy
diffing, offline on the SSD dumps — no new harness code.
4. Top-HUD glyph residual is not isolated: bottom-HUD draws
are identified (ranks 4–9, bottom-band-exclusive), but the
top-band HUD glyph edges (2ND/16, timer) sit in the long
tail with no single carrier above rank 10. Needs its own
brief if draw-level top-HUD isolation matters: HUD-region
masked re-attribution (restrict R_s to glyph bounding
boxes), offline — no new harness code.
5. Carrier screen identity is visual description only (god-ray
shafts for clks 1496/1495, glyph-scale draws for the HUD
ranks); draw→material/shader binding needs draw
introspection the probe does not carry. Tabled, not chased.
6. Attempt-1 timeout sizing rule for future scans: the native
budget must cover pre-sequence (~140 s here, frame/menu
dependent) + 6(C+1)×~25 ms + post-loop; C itself is
frame-dependent (1011 here vs 763 on the final frame).
`--seconds 540` covered C=763 with ~250 s spare. Future
scan briefs should budget from these two ceilings, not
from `--seconds 240`.
7. Player dirs are under `local/research/M16/players/` rather
than the SSD: the build driver refuses outputs outside
`local/`, and the brief orders changing only the header
path it compiles in. Run dirs, probes, dumps, and synths
are on the SSD as ordered.
8. Desktop only; no device work.

## Files

Committed under `local/research/M16/`:
`m16_replay_context.h` (research header, `64501bdc…`),
`build_replay_player.py` (M15 driver, header path only),
`analyze.py` (M15 tables unchanged + M16 `m16_win`/`m16_ref2`
parsing, per-(shape,phase) uniformity table + group
distributions + non-uniform list + full row table; missing
keys print as n/a / sections skipped), `loo.py` (M15
`synth.py` core verbatim — YUYV decode, masked SAD, warp +
blend — plus the LOO driver: per-shape parallel synth,
dump-vs-probe FNV chain, share tables, removed-residual maps,
PNG writer), `DESIGN.md` (mechanics choice + arm table +
attribution criterion, recorded before running), `REPORT.md`
(this file), `waits.log` (0 waits, one claim/release pair,
one annotation, never forced), `m16-base.png`,
`m16-diffmap.png`, `m16-carrier1.png`, `m16-carrier2.png`
(320x224, 479717 B total).

## Header diffs (`diff -u` against the M15 header)

Step 1 was a verbatim copy (empty diff at copy time; copy sha
`910163fa…` verified). What follows is the complete M15→M16
delta, generated from the committed
`local/research/M16/m16_replay_context.h` (`64501bdc…`;
env-gated additions only, so the M15 arms are reproducible
from it via env).

```diff
--- local/research/M15/m15_replay_context.h	2026-09-19 23:38:03
+++ local/research/M16/m16_replay_context.h	2026-09-20 00:04:06
@@ -1969,13 +1969,23 @@
                               return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                             })()
                                                         : 0;
-  const unsigned m14_cap =
-      m14_autoscan ? (unsigned)m13_condraw.size() : kM13DrawCap;
+  // M16: leave-one-out 3-phase scan (SSX_M16_LOO=1, drawscan-wanted only,
+  // mutually exclusive with autoscan: autoscan wins when both are set).
+  const int m16_want = (m13_want && m10_mode != 0 && !m14_autoscan) ? ([] {
+                         const char* v = std::getenv("SSX_M16_LOO");
+                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                       })()
+                                                                   : 0;
+  const unsigned m14_cap = (m14_autoscan || m16_want)
+                               ? (unsigned)m13_condraw.size()
+                               : kM13DrawCap;
   const unsigned long long m14_refneed =
       (unsigned long long)(m13_condraw.size() + 1) *
       (unsigned long long)mask.xfb.bytes;
-  const int m14_overbudget =
-      (m14_autoscan && m14_refneed > 768ull * 1024ull * 1024ull) ? 1 : 0;
+  const int m14_overbudget = ((m14_autoscan || m16_want) &&
+                              m14_refneed > 768ull * 1024ull * 1024ull)
+                                 ? 1
+                                 : 0;
   const int m13_scan = (m13_want && !m13_condraw.empty() &&
                         m13_condraw.size() <= m14_cap && !m14_overbudget)
                            ? 1
@@ -1989,15 +1999,26 @@
   // scratch frame carries first-replay EFB state — every shape's reference
   // is warm here, and n2=2 carries a within-shape uniformity receipt).
   const unsigned m14_nreps =
-      (m14_autoscan && m13_scan) ? 4u * m13_nshapes : kReplays;
+      (m16_want && m13_scan)
+          ? 6u * m13_nshapes
+          : ((m14_autoscan && m13_scan) ? 4u * m13_nshapes : kReplays);
   const unsigned m14_kfrom =
-      (m14_autoscan && m13_scan) ? 2u * m13_nshapes : kTransformFrom;
+      (m16_want && m13_scan)
+          ? 2u * m13_nshapes
+          : ((m14_autoscan && m13_scan) ? 2u * m13_nshapes : kTransformFrom);
+  // M16: the loo arm runs 6 contiguous (C+1) blocks (v0a/v0b/mida/midb/
+  // fulla/fullb); the seam arms at kfrom (scale 0.5, mid) and the scale
+  // returns to 1.0 at kfull (full). Fail-closed via m13_scan (cap +
+  // 768 MiB ref budget shared with autoscan).
+  const int m16_loo = (m16_want && m13_scan) ? 1 : 0;
+  const unsigned m16_kfull = m16_loo ? 4u * m13_nshapes : 0u;
   std::vector<std::vector<u8>> m13_exec, m13_pre;
   std::vector<char> m13_ok;
   std::vector<u32> m13_bytes;
-  if (m13_scan && m14_autoscan) {
+  if (m13_scan && (m14_autoscan || m16_loo)) {
     // M14 step 3: validate spans only (the live shape's streams are built
     // on demand per replay; prebuilding all copies would cost C*2 frames).
+    // M16: the loo arm shares the on-demand path (no prebuild).
     m13_ok.assign(m13_condraw.size(), 0);
     m13_bytes.assign(m13_condraw.size(), 0);
     for (size_t s = 0; s < m13_condraw.size(); ++s) {
@@ -2009,7 +2030,7 @@
       m13_bytes[s] = dr.size;
     }
   }
-  if (m13_scan && !m14_autoscan) {
+  if (m13_scan && !m14_autoscan && !m16_loo) {
     m13_exec.resize(m13_condraw.size());
     m13_pre.resize(m13_condraw.size());
     m13_ok.assign(m13_condraw.size(), 0);
@@ -2036,7 +2057,7 @@
   // M13 behavior (no stash, no rows).
   // M14 step 3: perreplay and autoscan are mutually exclusive (perreplay
   // storage is sized to the 200/100 constants).
-  const int m14_perreplay = (m10_ramref != 0 && !m14_autoscan) ? ([] {
+  const int m14_perreplay = (m10_ramref != 0 && !m14_autoscan && !m16_want) ? ([] {
                               const char* v = std::getenv("SSX_M14_PERREPLAY");
                               return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                             })()
@@ -2057,7 +2078,8 @@
   // full 150..199 (scale 1.0 -> +0.1). Reference = replay 99's scratch
   // (as M10 ref2). Pristine replays stash bytes (diffed post-loop); mid
   // and full rows record live. Unset = M14 behavior (no stash, no rows).
-  const int m15_mid = (m10_ramref != 0 && !m14_autoscan && !m14_perreplay) ? ([] {
+  const int m15_mid = (m10_ramref != 0 && !m14_autoscan && !m14_perreplay && !m16_want)
+                      ? ([] {
                           const char* v = std::getenv("SSX_M15_MID");
                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                         })()
@@ -2073,6 +2095,20 @@
   if (m15_mid && xfb_scratch_ok && mask.xfb.bytes > 0) {
     m15_prist.assign(size_t(kTransformFrom) * size_t(mask.xfb.bytes), 0);
   }
+  // M16: leave-one-out 3-phase scan (SSX_M16_LOO=1, drawscan-wanted only).
+  // Six contiguous (C+1) blocks (v0a/v0b/mida/midb/fulla/fullb): per-shape
+  // v0/mid/full triplets on ONE recorded frame for the offline per-shape
+  // warp. Refs = last v0b rep per shape (the M13 stash, same 768 MiB
+  // budget). mid_b/full_b frames are written per replay (fail-soft); v0a
+  // uniformity rests on hash equality (no second stash — RAM budget).
+  // Unset = M15 behavior (no rows, no dumps).
+  std::vector<u32> m16_xd2(m14_nreps, 0);
+  std::vector<int> m16_xdmax(m14_nreps, 0);
+  std::vector<double> m16_xdmean(m14_nreps, 0.0);
+  std::vector<u64> m16_hash(m14_nreps, 0);
+  std::vector<char> m16_have(m14_nreps, 0);  // 0 none, 1 hashed, 2 complete
+  const char* m16_dump_dir = m16_loo ? std::getenv("SSX_M16_DUMP_DIR") : nullptr;
+  unsigned m16_dv = 0, m16_dm = 0, m16_df = 0;  // dump ok counts per phase
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
   const std::vector<u8>& pre_stream =
@@ -2116,7 +2152,7 @@
                   "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d "
                   "m12mode=%d m12slot=%d m12alt=%d m13scan=%d m13shapes=%u "
                   "m14auto=%d m14cap=%u m14reps=%u m14from=%u m14perrep=%d "
-                  "m15mid=%d",
+                  "m15mid=%d m16loo=%d m16kfull=%u",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -2129,7 +2165,7 @@
                   m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
                   m11_notext, m12_mode, m12_slot_self, m12_alt, m13_scan,
                   m13_nshapes, m14_autoscan, m14_cap, m14_nreps, m14_kfrom,
-                  m14_perreplay, m15_mid);
+                  m14_perreplay, m15_mid, m16_loo, m16_kfull);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2342,9 +2378,12 @@
       s_m8_slot = m10_slot;
       s_m10_cap = 1;
       if (m15_mid) s_m15_scale = 0.5f;  // M15: mid phase renders +0.05
+      if (m16_loo) s_m15_scale = 0.5f;  // M16: mid blocks render +0.05
     }
     // M15: full phase renders +0.1 (replays 150..199 of the 200-sequence).
     if (m15_mid && replays == m15_kfull) s_m15_scale = 1.0f;
+    // M16: full blocks render +0.1 (replays 4(C+1)..6(C+1)-1).
+    if (m16_loo && replays == m16_kfull) s_m15_scale = 1.0f;
     if (m10_ramcopy) {  // M10 step 3: hold the forced-RAM flip every replay
       g_ActiveConfig.bSkipXFBCopyToRam = false;
       g_ActiveConfig.bSkipEFBCopyToRam = false;
@@ -2376,7 +2415,8 @@
       if (m13_win > 0 && m13_ok[m13_win - 1]) {
         // M14 step 3: autoscan builds the live shape's streams on demand
         // (byte-identical to the prebuilt copies: same bases, same span).
-        if (m14_autoscan) {
+        // M16: the loo arm shares the on-demand path.
+        if (m14_autoscan || m16_loo) {
           const M10DrawRec& m14dr = m10stream.drawrec[m13_condraw[m13_win - 1]];
           m14_tmp_exec = frame_exec;
           m14_tmp_pre = frame_pre_exec;
@@ -2732,6 +2772,12 @@
           m13_ref_hash[w13] = RamHash(rwp13, mask.xfb.bytes);
           m13_ref_ok[w13] = 1;
           m13_kref[w13] = replays;
+          // M16: per-replay hash row for v0 reps (uniformity via hash
+          // equality with the v0b ref; no second stash — RAM budget).
+          if (m16_loo) {
+            m16_hash[replays] = m13_ref_hash[w13];
+            m16_have[replays] = 1;
+          }
         } else if (m13_ref_ok[w13]) {
           const u64 hh13 = RamHash(rwp13, mask.xfb.bytes);
           if (m13_n2[w13] == 0) m13_hk_hash[w13] = hh13;
@@ -2750,6 +2796,39 @@
             }
           }
           const double xn13 = x13 ? double(xa13) / double(x13) : 0.0;
+          // M16: per-replay row (live xd vs the shape's v0 ref) + b-rep
+          // dumps (mid_b/full_b frames to $SSX_M16_DUMP_DIR, fail-soft).
+          if (m16_loo) {
+            m16_xd2[replays] = x13;
+            m16_xdmax[replays] = xm13;
+            m16_xdmean[replays] = xn13;
+            m16_hash[replays] = hh13;
+            m16_have[replays] = 2;
+            if (m16_dump_dir && m16_dump_dir[0] && mask.xfb.bytes > 0) {
+              const unsigned m16ns = m13_nshapes;
+              const char* m16tag = nullptr;
+              unsigned* m16okp = nullptr;
+              if (m16ns > 0 && replays >= 3u * m16ns && replays < 4u * m16ns) {
+                m16tag = "mid";
+                m16okp = &m16_dm;
+              } else if (m16ns > 0 && replays >= 5u * m16ns &&
+                         replays < 6u * m16ns) {
+                m16tag = "full";
+                m16okp = &m16_df;
+              }
+              if (m16tag) {
+                char m16_path[512];
+                std::snprintf(m16_path, sizeof(m16_path), "%s/m16-%s-s%04u.bin",
+                              m16_dump_dir, m16tag, w13);
+                if (std::FILE* m16_fp = std::fopen(m16_path, "wb")) {
+                  const size_t m16_w =
+                      std::fwrite(rwp13, 1, mask.xfb.bytes, m16_fp);
+                  std::fclose(m16_fp);
+                  if (m16_w == mask.xfb.bytes) ++(*m16okp);
+                }
+              }
+            }
+          }
           if (x13 > 0) {
             ++m13_gt0[w13];
             if (m13_samp_n[w13] < 3) {
@@ -3516,7 +3595,84 @@
                       m15_xdmean[r], static_cast<unsigned long long>(m15_hash[r]),
                       static_cast<unsigned long long>(m10_ref2_hash));
         Event("m15_ref2", m15f);
+      }
+    }
+    // M16: leave-one-out rows + v0 dumps (loo-gated). v0 refs dump from
+    // the M13 ref stash; mid_b/full_b were written per replay. Uniformity
+    // counts compare a/b pair hashes per (shape,phase). Fail-soft: dump
+    // ok counts ride m16_win; a missing dir never aborts the sequence.
+    if (m16_loo) {
+      if (m16_dump_dir && m16_dump_dir[0] && xfb_scratch_ok &&
+          mask.xfb.bytes > 0) {
+        for (unsigned w = 0; w < m13_nshapes; ++w) {
+          if (!m13_ref_ok[w] || m13_ref[w].size() != mask.xfb.bytes) continue;
+          char m16_path[512];
+          std::snprintf(m16_path, sizeof(m16_path), "%s/m16-v0-s%04u.bin",
+                        m16_dump_dir, w);
+          if (std::FILE* m16_fp = std::fopen(m16_path, "wb")) {
+            const size_t m16_w =
+                std::fwrite(m13_ref[w].data(), 1, mask.xfb.bytes, m16_fp);
+            std::fclose(m16_fp);
+            if (m16_w == mask.xfb.bytes) ++m16_dv;
+          }
+        }
+      }
+      const unsigned m16_ns = m13_nshapes;
+      unsigned m16_uv0 = 0, m16_uvm = 0, m16_uvf = 0;
+      for (unsigned w = 0; w < m16_ns; ++w) {
+        const unsigned rv0a = w, rv0b = m16_ns + w;
+        const unsigned rma = 2u * m16_ns + w, rmb = 3u * m16_ns + w;
+        const unsigned rfa = 4u * m16_ns + w, rfb = 5u * m16_ns + w;
+        if (rfb >= m14_nreps) continue;
+        if (m16_have[rv0a] == 1 && m16_have[rv0b] == 1 &&
+            m16_hash[rv0a] == m16_hash[rv0b])
+          ++m16_uv0;
+        if (m16_have[rma] == 2 && m16_have[rmb] == 2 &&
+            m16_hash[rma] == m16_hash[rmb])
+          ++m16_uvm;
+        if (m16_have[rfa] == 2 && m16_have[rfb] == 2 &&
+            m16_hash[rfa] == m16_hash[rfb])
+          ++m16_uvf;
+      }
+      char m16w[256];
+      std::snprintf(m16w, sizeof(m16w),
+                    "loo=%d nshapes=%u nreps=%u kfrom=%u kfull=%u xfbbytes=%u "
+                    "dv=%u dm=%u df=%u uv0=%u uvm=%u uvf=%u",
+                    m16_loo, m16_ns, m14_nreps, m14_kfrom, m16_kfull,
+                    mask.xfb.bytes, m16_dv, m16_dm, m16_df, m16_uv0, m16_uvm,
+                    m16_uvf);
+      Event("m16_win", m16w);
+      for (unsigned r = 0; r < m14_nreps; ++r) {
+        const unsigned w = m16_ns ? r % m16_ns : 0;
+        const char* m16ph =
+            r < m14_kfrom ? "v0" : (r < m16_kfull ? "mid" : "full");
+        const unsigned m16pstart =
+            r < m14_kfrom ? 0 : (r < m16_kfull ? m14_kfrom : m16_kfull);
+        const char m16rep = (m16_ns && r - m16pstart < m16_ns) ? 'a' : 'b';
+        const int m16ok = (r < m14_kfrom) ? (m16_have[r] == 1 ? 1 : 0)
+                                          : (m16_have[r] == 2 ? 1 : 0);
+        // um: pair-hash uniformity (a v0 row's xd2 reads 0 iff um==1).
+        int m16um = 0;
+        if (m16_ns) {
+          const unsigned m16pair =
+              (m16rep == 'a') ? r + m16_ns : r - m16_ns;
+          if (m16pair < m14_nreps && m16_have[r] && m16_have[m16pair] &&
+              m16_hash[r] == m16_hash[m16pair])
+            m16um = 1;
+        }
+        const unsigned m16clk = w == 0 ? 0u : m13_condraw[w - 1] + 1;
+        char m16f[256];
+        std::snprintf(m16f, sizeof(m16f),
+                      "r=%u shape=%u clk=%u phase=%s rep=%c ok=%d xd2=%u "
+                      "xdmax=%d xdmean=%.3f hash=%016llx refhash=%016llx um=%d",
+                      r, w, m16clk, m16ph, m16rep, m16ok, m16_xd2[r],
+                      m16_xdmax[r], m16_xdmean[r],
+                      static_cast<unsigned long long>(m16_hash[r]),
+                      static_cast<unsigned long long>(
+                          m13_ref_ok[w] ? m13_ref_hash[w] : 0),
+                      m16um);
+        Event("m16_ref2", m16f);
+      }
     }
     // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
     // only; the M10 receipts above are unchanged). m11_idx carries the
```

