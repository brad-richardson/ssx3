# M23 — Design (recorded before running)

Goal: tail value mechanism (M22 gap 1): the 102 s0 / 134 m15 tail
δ values at ρ≈0.42 regime, sign following the gap on ~90%, gaps
≥17. Given (gap, position, carrier-context) at a tail site, is δ
predictable? Per-site value tables + predictor fits on the FIXED
list below — no additions mid-run (M20 stencil-fit precedent).
Tables, no verdicts. Fully offline: no lease of any kind, no
boots, no harness runs, no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m22/m22.txt` (tail membership to
reproduce: 102/134 counts + max 47/48 — match exactly or table
the mismatch and stop). Work dir: `/Volumes/Extreme SSD/m23/`
(new). Evidence: `local/research/M23/` (committed with
`git add -f`, prefix `[M23]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M22/REPORT.md` (all of it:
102/134 tail, max 47/48, 100% luma, top-band + dec-9 heavy,
25/31 8-conn comps, top streak columns c257/277/296/301/321/
340–343 recurring both frames, no carrier mask holds more than
1 B, 727/764 maps byte-identical to s0, Jaccard 0.4132, gaps
17–115 mean ~54, ρ peak [0.4,0.5] mean|ρ| 0.42/0.40, sign agrees
with gap 90.2%/89.6%) plus M20's stencil-fit precedent (fixed
candidate list in DESIGN.md, no fishing) and M21's Task-1.1 map
machinery (per-shape persistence + Jaccard) for the cross-shape
check.

## Estimator (`m23.py`, `control.py`)

Shared core (M22 `m22.py` verbatim where reused): YUYV 640x448
decode (`split_planes`, `flat_to_planes`), `synth_w_bytes` at
w=0.5, `xdiff`, `mag_hist`, `bands_of` (thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG
writer, `plane_of_byte`, `plane_coords`, `p1_gradient` (M18 P1
block verbatim), `connected_components` (union-find, 4/8-conn),
`jaccard`. Byte offset o -> row o//1280; Y bytes at o%4==0/2.

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard).
- Bulk = cell-7 bytes with |δ|<8 (want 2373 s0 / 2405 m15).
  Tail = cell-7 bytes with |δ|≥8 (want 102 s0 / 134 m15; s0
  sub-bins 28 in 8–15 + 74 in 16+, m15 50 + 84; max 47/48).
- Plane of a byte: Y (o%4==0/2), U (o%4==1), V (o%4==3).
- Signed gap g = v0−full (int16, ≠0 on moved sites, hence on
  all tail sites). Unsigned gap |g| for M22-bin tables.
- Tail MAP of shape s: T_s = tail boolean mask (N bytes).

Rounding convention (fixed, all predictors): round-half-away-
from-zero, computed in exact integer arithmetic (no floats).

### Fixed predictor list (9 predictors, no additions mid-run)

| id | formula | constants |
| --- | --- | --- |
| K40+ | sign(g)·((2\|g\|+2)//5) | none (= round(0.40·g)) |
| K40− | −sign(g)·((2\|g\|+2)//5) | none (= round(−0.40·g)) |
| K45+ | sign(g)·((9\|g\|+10)//20) | none (= round(0.45·g)) |
| K45− | −sign(g)·((9\|g\|+10)//20) | none (= round(−0.45·g)) |
| STEP1 | sign(g)·1 | none |
| STEP2 | sign(g)·2 | none |
| STEP3 | sign(g)·3 | none |
| COMP | 8-conn tail-Y component id → round-half-away(mean δ of fit-frame tail bytes in that component) | per-component means from fit frame |
| POS | (band × decile-9/not) cell → median δ of fit-frame tail bytes in that cell | 6 cell medians from fit frame |

Details:

- K predictors: exact integer forms of round(k·g); halves round
  away from zero (k=0.4=2/5 has no exact halves; k=0.45=9/20
  halves round up in magnitude).
- STEP predictors: gap-side fixed step, c ∈ {1,2,3} (small
  integers per the brief; expected ~0 exact hits on |δ|≥8
  tail — tabled as falsification).
- COMP: components = Y-plane 8-conn tail components of the FIT
  frame (M22 union-find verbatim; want 25 comps s0 / 31 m15 —
  tabled, not guarded). Component mean δ rounded half-away via
  sign(sum)·((2·|sum|+n)//(2n)). Fallback for bytes in no Y
  8-conn component (non-Y tail bytes, if any): round-half-away
  of the fit frame's global tail mean δ.
- POS: cells = band (M19 thirds: 0/1/2) × P1-decile-9/not
  (M18 P1 verbatim; U/V tail bytes, if any, via co-located Y
  decile (r,2c), M20 verbatim). Cell value = median δ of
  fit-frame tail bytes in the cell; even-n median = mean of
  the two middles, halves away from zero. Empty-cell fallback
  (recorded; expect none on s0/m15): fit frame's global tail
  median δ. Empties tabled.
- Hit = prediction == δ exactly. Near-hit = |pred−δ| ≤ 1 and
  not exact. Near-hits tabled separately, never merged.
- Miss |err| distribution: exact |err| value counts in the
  receipt + coarse bins 2–3/4–7/8–15/16+.

Best predictor (fixed rule): highest exact-hit count on the s0
tail; tie-break: higher m15 exact-hit count; then list order
(K40+, K40−, K45+, K45−, STEP1, STEP2, STEP3, COMP, POS).
Explained bytes = best predictor's exact hits (per frame +
pooled s0+m15). Residual = |δ − pred_best| hist per frame
(exact value counts in receipt + M20-style coarse bins
1/2–3/4–7/8–15/16+ over the residual, hits reading 0).

### Task 1 — per-site value tables (s0 + m15)

Tail membership recomputed from the dumps; 102/134 + max 47/48
must match M22 EXACTLY or table the mismatch and stop (no
further tasks run).

1. (gap, δ) joint per frame: (a) |g| bins from M22's hist edges
   (2–3/4–7/8–15/16–31/32–63/64+): n, distinct-δ count, full
   sorted δ list in receipt; (b) exact signed-gap-value table:
   per distinct g value: n, δ list (collisions = same g with
   >1 distinct δ — flagged; "is δ a function of gap?"
   tabled via H6).
2. (position, δ) joint: δ stats (n, mean δ, mean |δ|, full
   sorted δ list in receipt) per band × decile-9/not cell
   (6 cells) + per top-streak column c ∈
   {257,277,296,301,321,340,341,342,343} over all tail-Y sites
   in that column (row range observed tabled; M22 streak band
   is r23–33).
3. (carrier-context, δ): δ stats (n, mean δ, mean |δ|, full
   sorted δ list in receipt) inside/outside each top-10
   removed mask (M19 Test-C verbatim res0 & ~ress on Y; U/V
   via co-located Y (r,2c); guards: removed counts
   [4888,1208,649,448,248,244,191,174,190,202] + M19 bands) +
   inside/outside-701 (expect ~all outside per M22 — tabled
   to confirm).

### Task 2 — predictor fits (fixed list, exact-hit scoring)

1. Score each of the 9 predictors on s0 + m15 tail bytes (fit
   frame = score frame for COMP/POS): exact hits / near hits
   / miss |err| distribution. Best predictor (rule above):
   explained bytes + residual |δ| hist per frame.
2. Cross-frame check: fit constants on s0, score on m15 (and
   vice versa) — tabled both directions. K*/STEP* have no
   fitted constants (identical by construction — tabled once
   per direction with that note). POS uses the fit frame's 6
   cell medians. COMP is frame-local by construction (no
   shared component-id space across frames): cross-frame
   cells read N/A with this reason (pre-registered, not
   filled post-hoc).
3. Cross-shape check (cheap): score the best predictor on 3
   non-s0 shapes: shapes {1, 2, 733} (1, 2 per brief; 733 =
   min-Jaccard shape 0.6694 from M22's below-0.95 table),
   each shape's tail recomputed from its dumps, constants
   from s0 (K*/STEP* constant-free; POS s0 cell medians;
   COMP s0-component rule: sites in T_s0∩T_shape get the s0
   component mean, other sites the s0 global tail mean —
   pre-registered fallback). Table per shape: tail n, exact
   hits, near hits, miss |err| coarse hist.

### Task 3 — controls + determinism (M18–M22 precedent)

`control.py` (imports `m23` cell/tail/core; expectations
analytic; feasibility per M22's lesson: interior ⇒ |δ| <
|gap|/2, so injections need gap ≥ 17 minimum and per-site
strict-inside verification):

- C-V1: synthetic truth mid' on s0: N=60 currently-interior-
  BULK sites with gap≥17 (first 60 in offset order passing
  the strict-inside check for the injected value; skips
  counted), injected δ = K45+ exactly (round(0.45·g),
  |δ|≥8 verified per site — gap≥17 ⇒ 0.45·17=7.65 → 8).
  Recompute cell 7 + tail from (v0,mid',full): the recomputed
  tail set must equal T_s0 ∪ injected exactly (count 162 +
  values + map), original tail members' δ unchanged. Score
  all 9 predictors on the control frame; restricted scoring
  on the 60 injected sites only must read argmax = K45+
  unique with 60/60 exact hits (best-predictor identity
  recovered exactly). Full-frame scores tabled.

Determinism: re-run Task 1 on s0 (cell-7 + tail recompute +
value tables); canonical-text sha + counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
top-10 carrier triplets. Model-0 recompute: R_0/fnv must match
M17–M22 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_KFIT (gap-proportional values): best K predictor
  exact-hit rate ≥ 0.25 on the s0 tail (≥26/102).
- H2_STEP (fixed-step values): best STEP predictor exact-hit
  rate ≥ 0.10 on the s0 tail (≥11/102).
- H3_COMP (component-constant values): COMP exact-hit rate
  ≥ 0.25 on the s0 tail (≥26/102).
- H4_POS (position-cell values): POS exact-hit rate ≥ 0.25
  on the s0 tail (≥26/102).
- H5_XFER (constants transfer): the s0-best transferable
  predictor (K*/STEP*/POS; COMP excluded per §Task 2.2),
  fit on s0 and scored on m15, reads an m15 exact-hit rate
  within 0.15 (absolute) of its s0 exact-hit rate.
- H6_GAPDET (δ determined by gap): among signed-gap values
  with ≥2 s0-tail sites, the share with all-equal δ
  ≥ 0.50.
- N (standing remainder + best predictor): cell 7 after the
  best predictor's exact hits + remaining split — the
  deliverable whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact + tail counts 102/134 exact with
sub-bins 28+74 / 50+84 and max 47/48 (else stop before Task
1.1); δ≠0 throughout cell 7; P(δ>0)==M19/M20 0.8093/0.8019;
P1 rounded edges match m18.txt; `loo.txt` 764 rows + top-10
shapes/shares; removed counts + bands; 701 interior-in-mask
367 + tail-outside-701 102; self Jaccard == 1.0.

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 + tail recompute + count guard (102/134 + max
   47/48 or stop).
3. Task 1: (gap,δ) joints; (position,δ) cell + streak-column
   tables; carrier-context inside/outside tables.
4. Task 2: 9-predictor scores; best-predictor explained +
   residual; cross-frame both directions; 3-shape transfer.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG predictor-residual map (320x224, <5 MB total) to work
   dir; evidence copy ONLY if the map discriminates spatially
   (hits/misses separate by a tabled split —
   component/band/decile); else absence reasoned.
7. `control.py` receipt.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 02:19 EDT, stop by 06:19).
