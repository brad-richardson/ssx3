# M15 — Host interpolated-frame synthesis (seam → synth vs truth): REPORT

Base pair (slot-0 v0/v1 renders) → offline warp/blend synth of the
mid-frame → measured against ground truth (the harness rendering the
true mid matrix exactly), plus the M14 autoscan as the residual-carrier
guide. Desktop only. Runbook `local/muse/prompts/M15.md`. No `adb`, no
device. Tables, no verdicts.

Headers read first: `local/research/M14/REPORT.md` (all of it: the
step-2 true-delta arms, the step-3 autoscan carriers, the
header/player/analyzer system, the determinism evidence).

Time box 6 hours; used about 1. No lease waits (lease absent at both
claims; claim/release pairs logged in
`local/research/M15/waits.log`; never forced).

## Baseline note (read before the tables)

The M14 header on disk (`local/research/M14/m14_replay_context.h`, clean
tree) hashes to
`40533e4dba118b6b8f7fc220fa6b8d9e9ea58f7a42100c0cf85a5b90be6add66`
via `shasum -a 256` (trust `shasum`, not memory; matches the M14
report's committed sha). Step 1 copied the on-disk file verbatim to
`local/research/M15/m15_replay_context.h`, then added the M15 delta
(`diff -u` M14→M15 is §Header diffs, nothing else). Every
M5–M14 mechanism is kept: the M15 additions are env-gated with defaults
that preserve M14 behavior (`SSX_M15_MID` / `SSX_M15_DUMP_DIR` unset).
The committed header is `910163fa…`.

M15 mode (`SSX_M15_MID=1`, M10 RAMREF only, mutually exclusive with
perreplay/autoscan — perreplay wins when both are set): a 3-phase
sequence over the standard 200/100 constants — v0 replays 0–99 (seam
disarmed), mid 100–149 (slot armed, `s_m15_scale=0.5` → +0.05 truth),
full 150–199 (scale 1.0 → +0.1). Reference = replay 99's scratch (as
M10 ref2); v0 replays stash bytes (diffed post-loop), mid/full rows
record live; one `m15_win` guard line + one `m15_ref2` event per replay
(200 rows, phases v0/mid/full). Dumps (fail-soft, receipted in
`m15_win`): r0, v0 (r99), mid (r149), full (r199) scratch frames to
`$SSX_M15_DUMP_DIR`. The M10 ref2 aggregate is left running (it spans
mid+full; tabled as observed).

Arm B runs the M14 instrument unchanged (committed M14
`players/m14-autoscan2` + M14 det4 env); only probe/run paths are new.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M14. `m15-*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M15\n'`, removed after each run).
`complete_hazard_resets`: 0 on both runs; every sequence is complete
with `done` and clean counters (see tables).

| Arm | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| A 3-phase capture | `910163fa…` (= committed M15) | `players/m15-mid` | `m15-mid-run` (`m15-mid`, `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M15_MID=1 SSX_M15_DUMP_DIR=/Volumes/Extreme SSD/m15`) | `m15-mid-probe.jsonl` |
| B delta carriers | `40533e4d…` (= M14 committed) | M14 `players/m14-autoscan2` | `m15-scan-run` (`m15-scan`, `SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1`) | `m15-scan-probe.jsonl` |

Player dirs live under `local/research/M15/players/` (arm A) and
`local/research/M14/players/` (arm B reuse); the build driver requires
outputs under `local/`. Run dirs, probes, dumps, and analyzer outputs
live under `/Volumes/Extreme SSD/m15/` (symlink-free; `realpath` is the
path as written). Probes, runs, dumps, and players are not committed
(players: the brief's "players included per M14 precedent" is followed
literally — repo evidence `git ls-files local/research/M14/` shows M14
players are gitignored build outputs, present but never committed).

## Per-step wall table (final arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m15-mid | 200 | 7.737 / 9.115 / 7.035 / 20.574 | 2.724 / 3.102 | 374221 / 3249 | YES | seq_wall_ms=2091.498 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m15-scan | 3164 | 6.877 / 8.184 / 5.751 / 15.827 | 2.484 / 2.865 | 363734 / 3157 | YES | seq_wall_ms=30398.256 completed=3164 xfb_equal=3164/3164 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/3164 live_xfb_untouched=1 live_same=3164/3164 |
```

Frames differ per run (374221 vs 363734 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table).
Both rows: complete sequences, `done`, `restored det=1 dual=1`,
`mask_bp=2 dls=0 walk=100% unknown=0 benign=1`.
`xfb_equal_scratch=0/N` on both rows is the forced-RAM signature
(rendered scratch vs fuchsia live ref), not a failure. All capacity rows
carry `xform=1` on both arms (inherited: `xform_flag` includes
`m9_mode != 0`; M14 det2 reads identically n/a / 200).

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m15-mid | 0.120 | 0.001 | 0.037 | 7.584 | 0.000 | 8.939 |
| m15-scan | 0.122 | 0.001 | 0.047 | 6.706 | 0.000 | 7.979 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m15-mid | 1854 | 88992 | 23.6 |
| m15-scan | 1744 | 83712 | 25.0 |

## Step 1 — design (recorded before running; `DESIGN.md`)

Base pair: renders at slot-0 v0 (pristine, +0.0) and v1 (+0.1, M7's
shape on word 3). Ground truth: render at the true mid matrix (+0.05) —
the harness renders this exactly via the seam. Synth: offline
image-space interpolation between the dumped v0/v1 pair. All arms that
must combine share one recorded frame (M14 §Step 3: every run records
its own frame).

Method choice (implementer's call, recorded before running): chosen =
global-translation warp + blend. Estimate the dominant (dx,dy) image
shift between the v0 and v1 dumps (SAD search on the Y plane), shift v0
forward by half and v1 back by half, average; plane-separated (Y vs
U/V) so odd-pixel shifts never break YUYV pairing. Why warp, not
mid-matrix re-render: the harness's mid-matrix render IS the truth path
(it applies +0.05 through the same seam), so using it as "synth" would
read 0 residual by construction and measure nothing. Warp captures the
rigid camera component in image space; content breaking the rigid
assumption lands in the residual — the split the M14 thesis predicts.
Control: 50 mid replays must read identical. Baseline for the warp:
plain 50% byte blend (no motion compensation).

As-run change to the estimator (recorded with receipts): the unmasked
SAD search degenerated to (0,0) — on a static-dominated frame any
nonzero shift misaligns the static majority, so (0,0) wins trivially
(first run kept as `/Volumes/Extreme SSD/m15/synth-unmasked.txt`).
Revised to masked SAD (only moved pixels vote); the masked search still
reads (0,0), now as a genuine sharp minimum (§Step 3). Synth therefore
equals the blend by measurement, not by bug.

## Step 2 — runs (per-arm: wall, exit, probes, determinism)

Exits 0/0. Probe receipts: `m15-mid-probe.jsonl` 20781764 B
(`dd91580a…`), `m15-scan-probe.jsonl` 17886575 B (`a23f218b…`).

Arm A guard receipt (`m15_win`): `mid=1 ref=1 kref=99 refok=1
refhash=fd0822497fe303d5 nreps=200 kfrom=100 kfull=150 xfbbytes=573440
d0=1 dv=1 dm=1 df=1 d0hash=0e93e581b2640c4a dvhash=fd0822497fe303d5
dmhash=39f3fd25c0ca5866 dfhash=1d2c0334906f27a4`. All 4 dumps ok, one
hash per phase. Dump-vs-probe FNV cross-check (recomputed in
`synth.py`): dv/dm/df all match=True.

Arm A per-replay moved-bytes rows (vs the v0 rendered reference; full
200 rows in `analyze-mid.txt`):

| r | phase | ok | xd2 | xdmax | xdmean | hash |
| ---: | --- | :-: | ---: | ---: | ---: | --- |
| 0 | v0 | 1 | 236751 | 234 | 115.551 | `0e93e581b2640c4a` |
| 1 | v0 | 1 | 0 | 0 | 0.000 | `fd0822497fe303d5` |
| 99 | v0 (ref) | 1 | 0 | 0 | 0.000 | `fd0822497fe303d5` |
| 100 | mid | 1 | 17255 | 67 | 1.887 | `39f3fd25c0ca5866` |
| 149 | mid | 1 | 17255 | 67 | 1.887 | `39f3fd25c0ca5866` |
| 150 | full | 1 | 24858 | 113 | 3.059 | `1d2c0334906f27a4` |
| 199 | full | 1 | 24858 | 113 | 3.059 | `1d2c0334906f27a4` |

Moved-bytes distributions (N≥10 per arm: 100/50/50):

| phase | n | xd2 min / max | distinct xd2 | hist | distinct hashes |
| --- | ---: | --- | ---: | --- | --- |
| v0 | 100 | 0 / 236751 | 2 | {0: 99, 236751: 1} | 2 (`0e93e581b2640c4a`: r0, `fd0822497fe303d5`: r1–r99) |
| mid | 50 | 17255 / 17255 | 1 | {17255: 50} | 1 (`39f3fd25c0ca5866` ×50) |
| full | 50 | 24858 / 24858 | 1 | {24858: 50} | 1 (`1d2c0334906f27a4` ×50) |

Inherited M10 ref2 aggregate over the mixed mid+full second half (tabled
as observed): `ref=1 kref=100 refok=1 n2=100 gt0=100 uniform2=50
xd2min=17255 xd2max=24858 xdmax2max=113 xdmean2min=1.887 xdmean2max=3.059
refhash=fd0822497fe303d5 samp=r100:17255/67/1.887,…` — min/max span the
mid and full totals; uniform2=50 (hk = replay 100 = mid).

Second-half corroboration: `xform_stats` hits=16200 (= 100 × 162
covering loads; first half counting-only); matrix before/after at the
replay-100 first hit is +0.05 on word 3 only (`3d4ccccd`, `mm_live=100
mm_snap=100`, 11/11 siblings bit-identical); M9 trichotomy over the
second half reads 50/0/50 in live, per-vertex and shared-pos snapshots
(`xf_after=50 xf_other=50 pos_after=50 pos_other=50`, `pos_res=100
tex_res=0 dirty_post=0`) — the inherited instrument bins the 50 mid
replays as "after" (first-hit value 0.05) and the 50 full replays as
"other" (0.1).

Own-frame M9 census, m15-mid (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1686 | 124 | n/a | n/a |
| Tex0 | 1810 | 0 | 1714 | 1714 |
| Tex1 | 1730 | 80 | 524 | 444 |
| Tex2 | 1810 | 0 | 24 | 24 |
| Tex3 | 1810 | 0 | 12 | 12 |
| Tex4–5 | 1810 | 0 | 5 | 5 |
| Tex6–7 | 1810 | 0 | 0 | 0 |

Shared-pos reach total 1686 (`0:784 3:95 6:128 9:81 12:142 15:100
18:116 21:61 24:103 27:76`); tex2 shared+enabled reach `36:24`.
Order row: draws=1810, covering=162, cons_pos=784, cons_tex=0;
first_cons=1 last_cons=1810; first covering load draw 0 / off 2587,
last 1746 / 363238; seam 16200 = 100×162. EFB copies n=11 (10 texture
+ XFB drain at draw 1810, `w=640,h=448` — the XFB geometry receipt for
the §Step 3 decode); `epoch_cons=9,9,9,9,9,1,1,1,1,1,734,0`; occ:
cons=784, culled=0, out-of-range=50, in-range=734;
`all_cull=all_scis=all_znever=0`.

Recorded without verdict: the 3-phase capture moves 17255 B at +0.05
and 24858 B at +0.1, each identically on all 50 replays, against the
rendered v0 reference; the 100 v0 replays read 0 except replay 0
(236751 B, the first-replay frame).

Arm B guard receipt (`m13_win`): `scan=1 slot=0 scheme=modN nshapes=791
ndraws=790 cap=790 sel_shr=0 sel_idx=0 sel_text=0 m10nop_ok=0` — no M11
selector armed, so shape 0 is the verbatim total. `restored` carries
`m14auto=1 m14cap=790 m14reps=3164 m14from=1582 m14perrep=0`. All 790
per-draw NOP spans ok=1. The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Shape-0 (verbatim total) row: `shape=0 kref=791 refok=1 n2=2 gt0=2
uniform2=2 xd2min/xd2max=21599/21599 xdmax2max=102 xdmean2=3.026
refhash=cfe3a7e32b1b3c18 samp=r1582:21599/102/3.026,r2373:21599/102/3.026`.
The full 791-row shape table is in `analyze-scan.txt`.

Own-frame context, m15-scan: draws=1778, covering=145, cons=790 all
pos; VAT Pos 1668/110; Tex0 1778/0/1700/1700; Tex1 1704/74/526/452;
Tex2 1778/0/33/33; Tex3–4 5 enabled; rest 0. Shared-pos reach total
1668 (`0:790 3:98 6:147 9:81 12:108 15:58 18:124 21:76 24:108 27:78`).
Matrix: +0.1 on word 3 only, `mm_live=1582 mm_snap=1582`. Survival:
1582/1582/1582 (`pos_res=1582`), shared-tex 0, `dirty_post=0`. Seam
229390 = 1582×145. EFB copies n=9;
`epoch_cons=9,9,9,9,1,1,1,1,750,0`; occ: cons=790, culled=0,
out-of-range=40, in-range=750.

## Step 3 — compare (synth vs truth)

Decode receipt: dumps are 573440 B each; `m10_copy` gives the XFB drain
as `w=640,h=448` (640·448·2 = 573440 = YUYV). `synth.py` decodes
640x448 YUYV → Y (640x448) + U/V (320x448); the decoded base frame is a
recognizable SSX3 ride frame (`m15-base.png`).

Shift estimation (SAD on the Y plane, search ±24): moved-Y mask =
17533/286720 px (6.12%). Masked best = (dx,dy) = (0,0), SAD 66599 —
the full 49² search minimum; 3x3 around best:

```
dy=-1: 481956 279458 392910
dy=0:  408231 66599 340887
dy=+1: 439264 270754 430888
```

(cols dx−1..dx+1). The (0,0) minimum is sharp (nearest neighbor 270754,
4.1×). Half shifts (0,0)/(0,0); synth == blend byte-identically
(fnvs `306b5c778898b64a` both) — by measurement: no integer
translation in ±24 explains the moved pixels better than no shift.

Byte diffs (raw 573440-B frames, M14 §analyze.py shape):

| pair | xd | xdmax | xdmean | frac_moved |
| --- | ---: | ---: | ---: | ---: |
| full-vs-v0 | 24858 | 113 | 3.059 | 0.0433 |
| mid-vs-v0 | 17255 | 67 | 1.887 | 0.0301 |
| full-vs-mid | 18672 | 159 | 2.546 | 0.0326 |
| synth-vs-truth | 13418 | 102 | 1.712 | 0.0234 |
| blend-vs-truth | 13418 | 102 | 1.712 | 0.0234 |

Y-plane |d| histograms: v0-vs-full moved 17533 px with
[1: 9031, 2–3: 4459, 4–7: 2236, 8–15: 986, 16+: 821] (77% at |d|≤3);
synth-vs-truth moved 8584 px with [1: 7474, 2–3: 398, 4–7: 339, 8–15:
172, 16+: 201] (87% at |d|=1). Residual-Y vertical bands top/mid/bot:
2191/3072/3321 px (moved-Y bands: 4755/6228/6550) — spread over the
frame, slightly bottom-weighted.

Deliverable table — what interpolates cleanly vs what breaks:

| content | bytes | behavior |
| --- | ---: | --- |
| static (v0==mid==full) | 548582 (95.67%) | synth byte-exact (no motion to interpolate) |
| moved (v0≠full) | 24858 (4.33%) | blend-synth leaves 13418 B residual vs truth (xdmean 1.7; 87% of residual Y px at |d|=1) |
| rigid-translation component | 0 px shift | masked SAD minimum at (0,0): no integer global shift in ±24; motion reads as in-place value changes (sub-pixel/filtering scale) |

Screenshots (committed, 320x224 PNG): `m15-base.png` 124373 B (v0),
`m15-synth.png` 124407 B, `m15-truth.png` 124365 B (mid),
`m15-diffmap.png` 124854 B (truth + red residual overlay, alpha ∝
|d|/32). Total 497999 B (budget 5242880). Diff-map reading: red
concentrates on high-contrast edges — mountain/rock faces, tree
clusters, the rider + board, HUD glyph edges — while sky and snowfields
are clean.

Residual-carrier table (arm B autoscan: where to look; own recorded
frame — frames differ per run, tabled as observed):

Top-10 carriers by removed share (total shape0 21599 minus surviving
shape, same frame):

| rank | clk | shape | surviving xd2 | removed share | samp |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 1716 | 728 | 20037 | 1562 | r2310:20037/102/2.822,r3101:20037/102/2.822 |
| 2 | 1709 | 721 | 20974 | 625 | r2303:20974/102/3.060,r3094:20974/102/3.060 |
| 3 | 1742 | 754 | 21043 | 556 | r2336:21043/102/3.055,r3127:21043/102/3.055 |
| 4 | 1741 | 753 | 21070 | 529 | r2335:21070/102/3.053,r3126:21070/102/3.053 |
| 5 | 1769 | 781 | 21121 | 478 | r2363:21121/102/3.066,r3154:21121/102/3.066 |
| 6 | 1768 | 780 | 21122 | 477 | r2362:21122/102/3.067,r3153:21122/102/3.067 |
| 7 | 1766 | 778 | 21179 | 420 | r2360:21179/102/3.064,r3151:21179/102/3.064 |
| 8 | 1764 | 776 | 21187 | 412 | r2358:21187/102/3.062,r3149:21187/102/3.062 |
| 9 | 1767 | 779 | 21188 | 411 | r2361:21188/102/3.063,r3152:21188/102/3.063 |
| 10 | 1763 | 775 | 21198 | 401 | r2357:21198/102/3.061,r3148:21198/102/3.061 |

Share arithmetic (total 21599; 790 shares):

| Field | Value |
| --- | --- |
| positive / zero / negative | 260 / 410 / 120 |
| max / min / median | 1562 (draw 1716) / −383 (draw 4) / 0 |
| sum of positive shares vs total | 13503 vs 21599 (62.5%) |
| top carrier fraction | 1562 / 21599 (7.2%) |

Within-shape uniformity (n2=2 with different predecessors): 791/791
shapes read 2/2/2.

Negatives (120, range −383…−1): −383 clk 4, −273 clk 1715, −245 clk 5,
−202 clk 3, −187 clk 2, −158 clk 9, −96 clk 6, −78 clk 483 (remaining
112 in −78…−1; full list in `analyze-scan.txt`).

Scan cross-checks (table):

| Check | Value |
| --- | --- |
| `ndraws` vs `cons_any` | 790 = 790 |
| per-draw spans ok | 790 / 790 |
| `n2`/`gt0`/`uniform2` pattern | 2/2/2 on all 791 shapes |
| `kref` = last pristine replay of shape | shape+791 on all 791 (shape 0: 791, warm) |
| seam hits vs 1582 × covering loads | 229390 = 1582×145 |
| shared Tex2 reach 36 vs `cons_tex` | 33 vs 0 (slot-0 consumers are all pos) |

Recorded without verdict: the carrier table is flatter than M14 det4's
(top 7.2% vs 19%, all shapes uniform vs 619/644) on its own frame; the
negatives repeat M14's early-draw pattern (clks 2–9). Same-frame
per-draw residual attribution (which draws carry the 13418-B remainder)
needs the warp leave-one-out scan — gap row 1.

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| base pair + truth + per-phase determinism (N≥10) | measured | §Step 2: 200/200 rows ok=1; v0 {0: 99, 236751: 1}; mid {17255: 50}; full {24858: 50} |
| synth-vs-truth byte diffs + moved-bytes distributions | measured | §Step 3: 5-pair table; synth==blend 13418 B residual; Y-|d| hists; bands |
| carrier attribution of the residual (autoscan = where to look) | measured with caveat | §Step 3: 791-shape scan, top-10 + arithmetic; own frame, not the synth frame |
| screenshots base/synth/truth/diff-map | measured | 4 PNGs, 497999 B total |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m15-mid | `fc=8139` | `replay_disabled=0 fc=8142 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m15-scan | `fc=8167` | `replay_disabled=0 fc=8170 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same address and
size, also identical to all M14/M13/M12/M11/M10/M9/M8/M7 sequence
hashes and all M6 sequence and M5 sequence/disabled hashes) is tabulated
as observed. `resume fc − fc0 = 3` in each run (the live record window;
per-replay `dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m15-mid | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m15-scan | 3164/3164 / 0/3164 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

Scratch `0/N` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Build (any time; only the header path differs from
`local/research/M14/build_replay_player.py`; `m15-mid` was built from
the M15 header — the driver compiles
`local/research/M15/m15_replay_context.h`; arm B reuses the M14
`m14-autoscan2` player, no rebuild):

```
python3 local/research/M15/build_replay_player.py local/research/M15/players/m15-mid
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M15\n'`,
remove after each run; profiles fresh per run):

```
SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M15_MID=1 SSX_M15_DUMP_DIR="/Volumes/Extreme SSD/m15" SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m15/m15-mid-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M15/players/m15-mid --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m15-mid --cpu-thread --output "/Volumes/Extreme SSD/m15/m15-mid-run" --seconds 240
SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m15/m15-scan-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M14/players/m14-autoscan2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m15-scan --cpu-thread --output "/Volumes/Extreme SSD/m15/m15-scan-run" --seconds 240
```

Analysis + synth:

```
python3 local/research/M15/analyze.py "m15-mid=/Volumes/Extreme SSD/m15/m15-mid-probe.jsonl"
python3 local/research/M15/analyze.py "m15-scan=/Volumes/Extreme SSD/m15/m15-scan-probe.jsonl"
python3 local/research/M15/synth.py "/Volumes/Extreme SSD/m15" local/research/M15 "/Volumes/Extreme SSD/m15/m15-mid-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M15/` — `m15_replay_context.h`
(`910163fa…`), `build_replay_player.py`, `analyze.py`, `synth.py`,
`DESIGN.md`, `REPORT.md` (this file), `waits.log`, `m15-base.png`,
`m15-synth.png`, `m15-truth.png`, `m15-diffmap.png`.

Large outputs (not committed): `/Volumes/Extreme SSD/m15/` —
`m15-mid-probe.jsonl` (20781764 B, `dd91580a…`),
`m15-scan-probe.jsonl` (17886575 B, `a23f218b…`) and the matching `-run`
dirs and harness receipts; `m15-r000.bin` / `m15-v0.bin` / `m15-mid.bin`
/ `m15-full.bin` (573440 B each; shas `7b57a58b…` / `879c74ec…` /
`10e2514a…` / `b4053af3…`); `m15-synth.bin` (573440 B, `f9311eaa…`);
`analyze-mid.txt`, `analyze-scan.txt`, `synth.txt`,
`synth-unmasked.txt` (first estimator run), `m15-header.diff`. Players
(gitignored): `local/research/M15/players/m15-mid/` (`player`,
`build.json`, launchers). All paths above are symlink-free as written
(`realpath` identical).

Build receipts (`build.json`: `s2_header_sha256` / `player_sha256`,
12-char prefixes): `m15-mid` `910163fa4139` / `e6b018c38b8f`.

## What I could not do

1. Same-frame per-draw residual attribution: which draws carry the
13418-B synth-vs-truth remainder is unattributed — arm B's carriers are
a different recorded frame ("where to look", not the answer). Needs its
own brief: warp leave-one-out scan (3-phase capture × per-draw shapes +
offline warp per shape; ~3x autoscan replays + new header code). The
dumps + `synth.py` on the SSD are the starting input.
2. Sub-pixel / local motion model: the global integer warp measured
(0,0), so the rigid component at sub-pixel scale (or per-block motion)
is untested. Needs its own brief: sub-pixel estimator (bilinear
half-pixel SAD) or block matching, offline on the committed dumps —
no new harness code.
3. HUD-edge residual source: HUD glyph edges carry residual (HUD draws
appear to consume slot 0), but which draws is unattributed — falls
under gap 1's scan.
4. The r0 first-replay frame reads 236751 B here (M14 det2: 127103 B;
frame-dependent); inherited, tabled, not re-explained.
5. Player dirs are under `local/research/M15/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs, probes,
and dumps are on the SSD as ordered.
6. Desktop only; no device work.

## Files

Committed under `local/research/M15/`: `m15_replay_context.h` (research
header, `910163fa…`), `build_replay_player.py` (M14 driver, header path
only), `analyze.py` (M14 tables unchanged + M15 `m15_win`/`m15_ref2`
parsing, 3-phase per-replay moved-bytes table + distributions; missing
keys print as n/a / sections skipped), `synth.py` (YUYV decode, masked
SAD shift estimation, plane-separated warp + blend baseline, M14-shape
diffs, PNG + diff-map writer), `DESIGN.md` (arm table + method choice,
recorded before running), `REPORT.md` (this file), `waits.log` (0
waits, two claim/release pairs, never forced), `m15-base.png`,
`m15-synth.png`, `m15-truth.png`, `m15-diffmap.png` (320x224, 497999 B
total).

## Header diffs (`diff -u` against the M14 header)

Step 1 was a verbatim copy (empty diff at copy time; copy sha
`40533e4d…` verified). What follows is the complete M14→M15 delta,
generated from the committed `local/research/M15/m15_replay_context.h`
(`910163fa…`; env-gated additions only, so the M14 arms are
reproducible from it via env — arm B ran the M14 player instead, kept
as the unchanged instrument).

```diff
--- local/research/M14/m14_replay_context.h	2026-09-19 20:09:41
+++ local/research/M15/m15_replay_context.h	2026-09-19 23:38:03
@@ -1276,6 +1276,10 @@
 static unsigned long long s_m8_reads[64] = {};
 static int s_m8_slot = -1;  // mode-2 target slot, else -1
 static int s_m8_proj = 0;   // mode-3 flag
+// --- M15: mid-delta scale ------------------------------------------------------
+// The slot-delta add is 0.1f * s_m15_scale. The M15 mid phase sets 0.5
+// (+0.05 truth render); every other mode leaves 1.0 (M14 behavior).
+static float s_m15_scale = 1.0f;
 // --- M9 step 3: upload-timing survival sampling -------------------------------
 // At each seam hit (a write covering the delta word), records the live xfmem
 // word before/after the +0.1 (first-hit hexes + mismatch tallies prove the
@@ -1336,7 +1340,7 @@
         for (u32 i = 0; i < 12; ++i)
           std::memcpy(&s_m10_mat_before[i], &xfmem.posMatrices[base + i], 4);
       }
-      *f += 0.1f;
+      *f += 0.1f * s_m15_scale;  // M15: mid phase scales to +0.05
       if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: post-add 12-word capture
         const u32 base = u32(s_m8_slot) * 4;
         for (u32 i = 0; i < 12; ++i)
@@ -2046,6 +2050,29 @@
   if (m14_perreplay && xfb_scratch_ok && mask.xfb.bytes > 0) {
     m14_prist.assign(size_t(kTransformFrom) * size_t(mask.xfb.bytes), 0);
   }
+  // M15: mid-frame capture (SSX_M15_MID=1, M10 RAMREF only, mutually
+  // exclusive with perreplay/autoscan: perreplay wins when both are set).
+  // Three phases over the standard 200/100 constants: v0 replays 0..99
+  // (seam disarmed), mid 100..149 (slot armed, scale 0.5 -> +0.05 truth),
+  // full 150..199 (scale 1.0 -> +0.1). Reference = replay 99's scratch
+  // (as M10 ref2). Pristine replays stash bytes (diffed post-loop); mid
+  // and full rows record live. Unset = M14 behavior (no stash, no rows).
+  const int m15_mid = (m10_ramref != 0 && !m14_autoscan && !m14_perreplay) ? ([] {
+                          const char* v = std::getenv("SSX_M15_MID");
+                          return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                        })()
+                                      : 0;
+  const unsigned m15_kfull = 150;  // full phase starts here
+  std::vector<u8> m15_prist;  // kTransformFrom pristine frames, stashed bytes
+  std::vector<u8> m15_mid_dump, m15_full_dump;  // one mid + one full frame
+  std::vector<u32> m15_xd2(kReplays, 0);
+  std::vector<int> m15_xdmax(kReplays, 0);
+  std::vector<double> m15_xdmean(kReplays, 0.0);
+  std::vector<u64> m15_hash(kReplays, 0);
+  std::vector<char> m15_have(kReplays, 0);  // 0 none, 1 stashed, 2 complete
+  if (m15_mid && xfb_scratch_ok && mask.xfb.bytes > 0) {
+    m15_prist.assign(size_t(kTransformFrom) * size_t(mask.xfb.bytes), 0);
+  }
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
   const std::vector<u8>& pre_stream =
@@ -2088,7 +2115,8 @@
                   "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
                   "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d "
                   "m12mode=%d m12slot=%d m12alt=%d m13scan=%d m13shapes=%u "
-                  "m14auto=%d m14cap=%u m14reps=%u m14from=%u m14perrep=%d",
+                  "m14auto=%d m14cap=%u m14reps=%u m14from=%u m14perrep=%d "
+                  "m15mid=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -2101,7 +2129,7 @@
                   m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
                   m11_notext, m12_mode, m12_slot_self, m12_alt, m13_scan,
                   m13_nshapes, m14_autoscan, m14_cap, m14_nreps, m14_kfrom,
-                  m14_perreplay);
+                  m14_perreplay, m15_mid);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2204,6 +2232,7 @@
                       ? m9_slot
                       : -1;
     s_m8_proj = 0;
+    s_m15_scale = 1.0f;  // M15: default scale; the mid phase sets 0.5
     s_m9_surv = m9_surv;
     s_m9_first_hit = 0;
     s_m9_vbefore = s_m9_vafter = 0;
@@ -2312,7 +2341,10 @@
     if (replays == m14_kfrom && (m10_ramref || m12_alt || m13_scan)) {
       s_m8_slot = m10_slot;
       s_m10_cap = 1;
+      if (m15_mid) s_m15_scale = 0.5f;  // M15: mid phase renders +0.05
     }
+    // M15: full phase renders +0.1 (replays 150..199 of the 200-sequence).
+    if (m15_mid && replays == m15_kfull) s_m15_scale = 1.0f;
     if (m10_ramcopy) {  // M10 step 3: hold the forced-RAM flip every replay
       g_ActiveConfig.bSkipXFBCopyToRam = false;
       g_ActiveConfig.bSkipEFBCopyToRam = false;
@@ -2556,6 +2588,14 @@
                       mask.xfb.bytes);
           m14_have[replays] = 1;
         }
+        // M15: stash v0 scratch frames for the post-loop diff (same shape).
+        if (m15_mid && replays < kTransformFrom &&
+            m15_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+          m15_hash[replays] = RamHash(r2p, mask.xfb.bytes);
+          std::memcpy(&m15_prist[size_t(replays) * size_t(mask.xfb.bytes)], r2p,
+                      mask.xfb.bytes);
+          m15_have[replays] = 1;
+        }
         if (replays == m14_kfrom - 1) {
           m10_ref2.assign(r2p, r2p + mask.xfb.bytes);
           m10_ref2_hash = RamHash(r2p, mask.xfb.bytes);
@@ -2585,6 +2625,19 @@
             m14_xdmean[replays] = xn2;
             m14_hash[replays] = hh;
             m14_have[replays] = 2;
+          }
+          // M15: record this mid/full replay's moved bytes live + capture
+          // one dump frame per phase (mid at 149, full at 199).
+          if (m15_mid) {
+            m15_xd2[replays] = x2;
+            m15_xdmax[replays] = xm2;
+            m15_xdmean[replays] = xn2;
+            m15_hash[replays] = hh;
+            m15_have[replays] = 2;
+            if (replays == m15_kfull - 1)
+              m15_mid_dump.assign(r2p, r2p + mask.xfb.bytes);
+            if (replays == m14_nreps - 1)
+              m15_full_dump.assign(r2p, r2p + mask.xfb.bytes);
           }
           if (x2 > 0) {
             ++m10_gt0;
@@ -3375,6 +3428,96 @@
         Event("m14_ref2", m14f);
       }
     }
+    // M15: 3-phase rows + frame dumps (mid-gated). v0 replays diff their
+    // stashed bytes post-loop (the ref did not exist when they ran);
+    // mid/full rows were recorded live. Dumps: r0, v0 (r99), mid (r149),
+    // full (r199) scratch frames to $SSX_M15_DUMP_DIR. Fail-soft: dump ok
+    // flags ride m15_win; a missing dir never aborts the sequence.
+    if (m15_mid) {
+      if (m10_ref2_ok &&
+          m15_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+        for (unsigned r = 0; r < kTransformFrom; ++r) {
+          if (m15_have[r] != 1) continue;
+          const u8* pb = &m15_prist[size_t(r) * size_t(mask.xfb.bytes)];
+          unsigned x = 0;
+          int xm = 0;
+          unsigned long long xa = 0;
+          for (u32 i = 0; i < mask.xfb.bytes; ++i) {
+            const int dd = pb[i] > m10_ref2[i] ? pb[i] - m10_ref2[i]
+                                              : m10_ref2[i] - pb[i];
+            if (dd > 0) {
+              ++x;
+              xa += (unsigned)dd;
+              if (dd > xm) xm = dd;
+            }
+          }
+          m15_xd2[r] = x;
+          m15_xdmax[r] = xm;
+          m15_xdmean[r] = x ? double(xa) / double(x) : 0.0;
+          m15_have[r] = 2;
+        }
+      }
+      const char* m15_dir = std::getenv("SSX_M15_DUMP_DIR");
+      int m15_d0 = 0, m15_dv = 0, m15_dm = 0, m15_df = 0;
+      u64 m15_d0h = 0, m15_dvh = 0, m15_dmh = 0, m15_dfh = 0;
+      if (m15_dir && m15_dir[0] && xfb_scratch_ok && mask.xfb.bytes > 0) {
+        const u8* m15_frames[4] = {
+            (m15_have[0] != 0 &&
+             m15_prist.size() >= size_t(mask.xfb.bytes))
+                ? m15_prist.data()
+                : nullptr,
+            m10_ref2_ok ? m10_ref2.data() : nullptr,
+            m15_mid_dump.size() == mask.xfb.bytes ? m15_mid_dump.data()
+                                                  : nullptr,
+            m15_full_dump.size() == mask.xfb.bytes ? m15_full_dump.data()
+                                                   : nullptr};
+        const char* m15_names[4] = {"m15-r000.bin", "m15-v0.bin", "m15-mid.bin",
+                                    "m15-full.bin"};
+        int* m15_oks[4] = {&m15_d0, &m15_dv, &m15_dm, &m15_df};
+        u64* m15_hs[4] = {&m15_d0h, &m15_dvh, &m15_dmh, &m15_dfh};
+        for (int f = 0; f < 4; ++f) {
+          if (!m15_frames[f]) continue;
+          char m15_path[512];
+          std::snprintf(m15_path, sizeof(m15_path), "%s/%s", m15_dir,
+                        m15_names[f]);
+          if (std::FILE* m15_fp = std::fopen(m15_path, "wb")) {
+            const size_t m15_w =
+                std::fwrite(m15_frames[f], 1, mask.xfb.bytes, m15_fp);
+            std::fclose(m15_fp);
+            if (m15_w == mask.xfb.bytes) {
+              *m15_oks[f] = 1;
+              *m15_hs[f] = RamHash(m15_frames[f], mask.xfb.bytes);
+            }
+          }
+        }
+      }
+      char m15w[512];
+      std::snprintf(m15w, sizeof(m15w),
+                    "mid=%d ref=%d kref=%u refok=%d refhash=%016llx nreps=%u "
+                    "kfrom=%u kfull=%u xfbbytes=%u d0=%d dv=%d dm=%d df=%d "
+                    "d0hash=%016llx dvhash=%016llx dmhash=%016llx dfhash=%016llx",
+                    m15_mid, m10_ramref, kTransformFrom - 1, int(m10_ref2_ok),
+                    static_cast<unsigned long long>(m10_ref2_hash), kReplays,
+                    kTransformFrom, m15_kfull, mask.xfb.bytes, m15_d0, m15_dv,
+                    m15_dm, m15_df,
+                    static_cast<unsigned long long>(m15_d0h),
+                    static_cast<unsigned long long>(m15_dvh),
+                    static_cast<unsigned long long>(m15_dmh),
+                    static_cast<unsigned long long>(m15_dfh));
+      Event("m15_win", m15w);
+      for (unsigned r = 0; r < kReplays; ++r) {
+        char m15f[192];
+        std::snprintf(m15f, sizeof(m15f),
+                      "r=%u phase=%s ok=%d xd2=%u xdmax=%d xdmean=%.3f "
+                      "hash=%016llx refhash=%016llx",
+                      r,
+                      r < kTransformFrom ? "v0" : (r < m15_kfull ? "mid" : "full"),
+                      m15_have[r] == 2 ? 1 : 0, m15_xd2[r], m15_xdmax[r],
+                      m15_xdmean[r], static_cast<unsigned long long>(m15_hash[r]),
+                      static_cast<unsigned long long>(m10_ref2_hash));
+        Event("m15_ref2", m15f);
+      }
+    }
     // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
     // only; the M10 receipts above are unchanged). m11_idx carries the
     // per-vertex decode aggregates; m11_nop the armed selectors + spans.

```
