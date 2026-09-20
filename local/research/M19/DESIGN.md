# M19 — Design (recorded before running)

Goal: endpoint-direction split of the M18 residual (M18 gap 1): on
the 17751 endpoint residual bytes is mid the BRIGHTER or the DARKER
endpoint? Which side do the outside-interval bytes fall on? How many
RAW residual bytes sit on static sites (v0==full)? Tables, no
verdicts. Fully offline: no lease of any kind, no boots, no harness
runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m18/m18.txt` (receipt values to
re-verify, not to trust). Work dir: `/Volumes/Extreme SSD/m19/`
(new). Evidence: `local/research/M19/` (committed with
`git add -f`, prefix `[M19]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M18/REPORT.md` (all of it: the
22815-B remainder, 77.8% endpoint + 91.7%/86.5% synth<truth
marginals, P4 463/439 static-site Y px, Test C carrier behavior)
plus the M16 carrier table (effect draws 694/693/701 vs HUD draws).

## Estimator (`m19.py`, `control.py`)

Shared core (M18 `m18.py` verbatim where reused): YUYV 640x448
decode (`split_planes`), `synth_w_bytes` at w=0.5 (== M15 blend
byte-exactly), `xdiff`, `y_hist`, `bands_of` ( thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG writer.
Byte offset o -> row o//1280; Y bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid. n = R_0 (want 22815 s0 / 13418 m15).
- moved: v0 != full. static site: v0 == full.
- lo = min(v0,full), hi = max(v0,full) (int16).

Direction classes — a PARTITION of the residual bytes:

| id | cell | predicate (all include res) |
| --- | --- | --- |
| 0 | ep-v0-max | mid==v0, v0>full |
| 1 | ep-v0-min | mid==v0, v0<full |
| 2 | ep-full-max | mid==full, full>v0 |
| 3 | ep-full-min | mid==full, full<v0 |
| 4 | above | moved, mid>hi |
| 5 | below | moved, mid<lo |
| 6 | static | v0==full |
| 7 | interior | moved, lo<mid<hi (strict) |

Note vs M18: M18's `mid_split` coded `static` as
res&(v0==full)&~outside, which is empty by construction
(v0==full + res implies mid outside the degenerate interval),
so its `outside` (2589/1674) = static-site + moved-outside.
M19 counts static-site FIRST; moved-outside is v0!=full only.
Reconciliation guard: M19 static + above + below == M18
outside exactly (2589 s0 / 1674 m15).

Sign: d = synth − mid (int16 per byte); neg = d<0
(synth<truth). Per-cell neg counts/rates + overall byte-level
rate + Y-byte-only rate (must reproduce M18's Y-px 91.7%/86.5%
up to px↔byte identity — Y-px residual IS Y-byte residual).

### Task 1 — direction split (s0 + m15 + 764-shape coarse pass)

Per frame (s0, m15), over residual bytes:

1. 4 endpoint cells (0–3) + marginals mid==max (0+2) vs
   mid==min (1+3), mid==v0 (0+1) vs mid==full (2+3).
2. Outside-moved: above (4) vs below (5) + distance
   distribution dout = mid−hi / lo−mid (bins
   [1,2–3,4–7,8–15,16+], max, mean) per side + combined.
3. Static-site byte count (6), both frames; reconciled with
   P4's Y-px 463/439 (Y bytes of class 6 vs P4 outside-mask
   px — same quantity in px units, must match exactly).
4. Sign cross: synth<truth rate inside EACH of the 8 cells
   (does the −1 bias live in one cell?).

Coarse pass (cheap — one synth + boolean splits per shape, no
sweep): per-shape direction split over all 764 M16 triplets
(R_s recompute + max/min endpoint counts + static + above /
below + interior + byte neg rate). Full 764-row table in the
receipt; share distributions in the report.

Direction-rule synths (explained-vs-standing rule table, s0 +
m15): synth_max = hi, synth_min = lo, synth_v0 = v0,
synth_full = full (per byte); R_rule = xd(rule, mid),
explained = R_0 − R_rule, e = explained / R_0. This is the
"does direction shrink the 22815 B, by what rule" table.

### Task 2 — carrier/band cut (where the direction lives)

Join unit: s0 Y-residual bytes, labeled by direction cell
(Y-px (r,c) ↔ its Y byte; non-residual Y px labeled −1).
Per band (M18 thirds): residual-Y count + cell shares; raw-byte
band table alongside. Per top-10 carrier (derived from
`loo.txt`, cross-checked vs M16's shapes + shares — mismatch
= stop per-carrier, tabled; M18 precedent): removed mask =
res0 & ~ress with blend resynth (M18 Test C verbatim;
removed counts + bands must match M18's 4888/1208/649/…
guard), then cell shares of s0 Y-residual bytes inside the
mask. Concentration rows: per cell, share of its Y bytes in
each band / each carrier mask. Tabled, not explained.

### Task 3 — controls + determinism (M18 precedent)

`control.py` (imports `m19.direction_split`; expectations
analytic or independently counted):

- D-min: synthetic truth = lo(v0,full) on s0 → every
  residual byte must read endpoint-min (cells 1+3 only);
  max/above/below/static/interior exactly 0.
- D-max: synthetic truth = hi → mirror (cells 0+2 only,
  rest exactly 0).
- D-v0: synthetic truth = v0 → all residual in ep-v0
  cells (0+1), ep-full/outside/static/interior exactly 0.
- D-out: synthetic truth = lo−1 (lo>0) else lo →
  above/interior exactly 0; all 8 cells must match the
  independently counted expectation exactly.

Determinism: re-run the Task-1 + Task-2 split on s0;
canonical-text sha + cell counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets
+ top-10 carrier triplets. Model-0 recompute: R_0/fnv must
match M17/M18 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_DIR (bright-side dominance): mid==max share of
  endpoint residual bytes ≥ 0.75 on s0.
- H2_CELL (single-cell dominance): max 4-cell share of
  endpoint bytes ≥ 0.50 on s0.
- H3_OUT (outside side): majority-side share of
  moved-outside bytes ≥ 0.75 on s0.
- H4_SIGN (bias localization): max over the 6 moved
  direction cells (0–5) of byte synth<truth rate minus min
  over the same cells ≥ 0.40 on s0.
- H5_CONC (spatial concentration): some direction cell has
  ≥ 75% of its s0 Y bytes in one band, or ≥ 50% in one
  top-10 carrier removed mask.
- N (standing remainder + rule): R after the best
  direction rule + remaining split — the deliverable
  whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv;
M18 marginal match (ep-v0 9412/5281, ep-full 8339/3924,
interior 2475/2539, outside totals 2589/1674);
`loo.txt` 764/764 + R_s match; carrier top-10 + removed
masks match M18; partition sums == R_0; P4 static-Y match
(463/439).

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Task 1: s0 + m15 8-cell split + marginals + dout dist +
   static count + sign cross.
3. Task 2: band cut (Y + raw) + per-carrier masked cell
   shares + concentration rows.
4. Coarse 764-shape direction pass.
5. Direction-rule synths (max/min/v0/full).
6. Determinism re-run receipt.
7. PNG split map (320x224, <5 MB total) ONLY if the cell
   map discriminates spatially; else absence reasoned.
8. `control.py` receipts.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 01:26 EDT, stop by 05:26).
