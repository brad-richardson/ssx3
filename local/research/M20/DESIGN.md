# M20 — Design (recorded before running)

Goal: interior-cell mechanism (M19 gap 1): per-byte mid-vs-blend
offset distribution + filter-tap fits on cell 7 (strict interior:
mid strictly inside (v0,full), v0≠full). Tables, no verdicts.
Fully offline: no lease of any kind, no boots, no harness runs,
no fork changes, no `adb`. Desktop only.

Inputs (read-only, never written): `/Volumes/Extreme SSD/m16/`
(764 per-shape triplets + `loo.txt`), `/Volumes/Extreme SSD/m15/`
(triplet), `/Volumes/Extreme SSD/m18/m18.txt` + `/Volumes/Extreme
SSD/m19/m19.txt` (receipt values to re-verify, not to trust).
Work dir: `/Volumes/Extreme SSD/m20/` (new). Evidence:
`local/research/M20/` (committed with `git add -f`, prefix
`[M20]`; NEVER `git push` in ssx3).

Headers read first: `local/research/M19/REPORT.md` (all of it:
cell 7 = 2475 B s0 / 2539 B m15, negrate 0.81/0.80, 53.1%
mid-band s0-Y, 15.2% of interior Y in 701's mask, zero interior
in HUD-draw masks 366/370/376, the only w-sensitive residual
class) plus M18's Test W/P tables (weight cusp at 0.5, P1
gradient deciles, top-quartile carry 45.0%/61.1%).

## Estimator (`m20.py`, `control.py`)

Shared core (M19 `m19.py` verbatim where reused): YUYV 640x448
decode (`split_planes`), `synth_w_bytes` at w=0.5 (== M15 blend
byte-exactly), `xdiff`, `y_hist`, `bands_of` (thirds via
`np.array_split(arange(448),3)`), `fnv1a`, `parse_loo`, PNG
writer. Byte offset o -> row o//1280; Y bytes at o%4==0/2.
M18 `grad_tables` P1 block verbatim for gradient + decile
assignment (central differences on mid-Y, mag=|gx|+|gy|,
`np.quantile(mag, linspace(0,1,11))`, `digitize(mag, qs[1:-1],
right=True)` clipped 0..9).

Definitions (raw bytes, full 573440-B frame):

- synth = blend ((v0+full)//2 byte-exact). Residual byte:
  synth != mid.
- Cell 7 (M19 id 7 verbatim): residual + moved (v0!=full) +
  lo<mid<hi strict, lo=min(v0,full), hi=max(v0,full).
- δ = mid − blend (int16 per byte), computed on cell-7 bytes
  only. Cell-7 bytes are residual by construction, so δ≠0
  throughout (guard: zero-δ count must read 0).
- Plane of a byte: Y (o%4==0/2), U (o%4==1), V (o%4==3).

### Task 1 — offset distribution (s0 + m15 cell-7 bytes)

Cell-7 membership recomputed from the dumps; counts must match
M19's 2475/2539 EXACTLY or table the mismatch and stop (no
further tasks run).

1. δ histogram (signed, full observed range: per-value counts)
   + |δ| histogram (M18 `y_hist`-style bins [1,2–3,4–7,8–15,16+],
   max, mean) + per-plane split (Y / U / V / U+V rows).
2. δ vs edge distance: d_edge = Manhattan pixel distance (in the
   byte's own plane grid: Y 640x448, U/V 320x448) from the byte's
   site to the nearest static site (v0==full) of the same plane,
   via exact BFS with nearest-source tracking. Bins {1,2,3,4,5+}
   (interior sites are moved by construction so d≥1; one-sided
   by construction — tabled, not forced). "Both directions":
   the nearest-source vector is decomposed into row/column
   components (dr, dc) and δ mean/sd/n is tabled per dr bin ×
   dc bin (small cross) alongside the Manhattan bins.
   δ vs M18-P1 gradient decile: P1 gradient + quantile edges
   recomputed from the dumps with M18's code verbatim; rounded
   edges guarded vs m18.txt (`0 1 2 2 4 6 8 12 18 29 176` s0 /
   `0 0 1 2 4 6 9 13 19 30 181` m15). Primary join: interior Y
   bytes only (P1 is Y-native); U/V bytes get a labeled
   secondary join via co-located Y decile (r,2c). Per decile:
   n, mean δ, sd δ, mean |δ|.
3. δ sign vs (v0−full) sign joint table: 2 rows (v0>full /
   v0<full) × 2 cols (δ>0 / δ<0) + shares; plus signed-ratio
   ρ = δ/|v0−full| histogram (bins of width 0.1 over (−0.5,0.5])
   + mean |ρ| (interior ⇒ |v0−full|≥2, |δ|≤|v0−full|/2).

### Task 2 — filter-tap fits (fixed list, no fishing)

Stencils evaluated per plane (Y bytes on the Y plane, U bytes on
U, V on V; sites whose taps reach out of bounds are excluded —
coverage n tabled per stencil, no clamped taps). Source frames:
v0 and full (same 5 stencils × 2 sources). Rounding: floor-mean
(blend convention) and round-half-up, both fixed. Hit =
prediction == mid byte exactly.

| id | taps | floor | half-up |
| --- | --- | --- | --- |
| S1 h2 | (r,c),(r,c+1) | sum//2 | (sum+1)//2 |
| S2 v2 | (r,c),(r+1,c) | sum//2 | (sum+1)//2 |
| S3 b22 | 2x2 at (r,c) | sum//4 | (sum+2)//4 |
| S4 h3 | (1,2,1)/4 centered | sum//4 | (sum+2)//4 |
| S5 h4 | (−1,+9,+9,−1)/16 at c−1..c+2 | sum//16 | (sum+8)//16 |

Table per stencil × source × rounding × frame: hits, n, rate.
"Does any stencil shrink cell 7": explained = hits (bytes of
cell 7 exactly predicted); remainder stands.

Positional fit: δ by (v0−full) parity (even/odd via int &1) and
by coordinate parity ((r%2)*2+(c%2), plane-native coords):
n, mean δ, sd δ, mean |δ| per class; all-interior + per-plane.

Carrier cut: 701 removed mask (M18 Test C verbatim: res0 &
~res701 via blend resynth on shape-701's triplet; guards:
removed Y px = 649, M19 interior-in-mask = 367). Interior Y
bytes inside vs outside the mask: δ per-value counts (same
bins), n, mean δ, mean |δ| — same shape or different, tabled.

### Task 3 — controls + determinism (M18/M19 precedent)

`control.py` (imports `m20` cell/δ core; expectations analytic):

- C-δ1: synthetic truth mid' = blend+1 on interior sites with
  blend≤254 (blend==255 sites left at blend: they drop out of
  cell 7 by construction — counted, not forced). Recompute
  cell-7 membership from (v0,mid',full): every recomputed
  interior site must read δ==+1 and the set must equal the
  injected set exactly.
- C-δpm: synthetic truth mid' = blend±1 checker ((r+c)%2) on
  interior sites (blend≤254 / blend≥1 edge handling same as
  C-δ1, tabled): recovered δ histogram must equal the injected
  histogram exactly.

Determinism: re-run Task 1 on s0; canonical-text sha +
cell-7 counts byte-identical.

Input shas (sha256 full, in the receipt): s0 + m15 triplets +
shape-701 triplet. Model-0 recompute: R_0/fnv must match
M17–M19 (22815/13418, `6b9ffda25bd76c6f` /
`306b5c778898b64a`). Mismatch = stop and table.

## Falsification bars (recorded before running; tables, no verdicts)

- H1_DSPREAD (±1 dominance): P(|δ|==1) over s0 cell-7 bytes
  ≥ 0.75.
- H2_LEAN (offset side): majority-side share of δ sign
  (max(P(δ>0), P(δ<0))) ≥ 0.75 on s0.
- H3_EDGE (edge dependence): max over Manhattan d_edge bins
  {1,2,3,4,5+} of mean|δ| minus min over the same bins ≥ 1.0
  on s0.
- H4_STENCIL (tap explanation): some stencil × source ×
  rounding cell reads hit rate ≥ 0.50 on s0 cell-7 bytes.
- H5_CARRIER (701-cut difference): |mean δ inside 701 mask −
  mean δ outside| ≥ 1.0 on s0 interior Y bytes, or the
  in-mask |δ| mean differs from out-of-mask by a factor ≥ 2.
- N (standing remainder + best stencil): cell-7 bytes after
  the best stencil's hits + remaining split — the deliverable
  whatever the bars read.

Guards (stop-and-table, not bars): baseline R_0/fnv; cell-7
counts 2475/2539 exact (else stop before Task 2); δ≠0
throughout cell 7; P1 rounded edges match m18.txt; 701 removed
649 + interior-in-mask 367; `loo.txt` 764 rows + shape-701
share 1126.

## Run protocol

1. Input shas + Model-0 recompute + cross-checks (§Task 3).
2. Cell-7 recompute + count guard (2475/2539 or stop).
3. Task 1: δ hists + plane split; edge-distance BFS + (dr,dc)
   cross; P1 decile join; sign joint + ratio dist.
4. Task 2: 20 stencil hit rates; parity tables; 701 carrier cut.
5. Determinism re-run receipt (Task 1 on s0, canonical sha).
6. PNG δ map (320x224, <5 MB total) ONLY if a δ map
   discriminates spatially (sign/edge structure separates by
   region — 701 mask vs rest or band split); else absence
   reasoned.
7. `control.py` receipts.

Wall time, exit, and exact commands recorded. Time box
4 hours (start 2026-09-20 01:35 EDT, stop by 05:35).
