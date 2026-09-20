# M16 — Design (recorded before running)

Goal: attribute M15's 13418-B synth-vs-truth residual to draws ON THE
SAME recorded frame (M15 gap 1; HUD-edge gap 3 falls under this scan).
One run records one frame; on it, a verbatim 3-phase triplet (the new
frame's total residual R_0) plus a per-draw triplet for every consuming
draw, with the warp synth done offline per shape. No device work.

## Leave-one-out mechanics (implementer's call)

Chosen: **per-draw withheld synth**. For each shape s in 0..C (shape 0 =
verbatim, shape s>0 NOPs consuming draw `condraw[s-1]`, M13 shapes on
the one shared frame):

- render v0_s (pristine, seam disarmed), mid_s (+0.05 truth), full_s
  (+0.1) scratch frames in-harness and dump all three;
- offline per shape: masked-SAD shift estimate on that shape's moved-Y
  mask (M15 `synth.py` estimator, full ±24 search), plane-separated
  warp synth_s = mean(warp(v0_s,+half), warp(full_s,−half));
- residual R_s = xd(synth_s, mid_s) in raw bytes (M14 shape);
- removed share_s = R_0 − R_s (M14 removed-share shape: verbatim total
  minus surviving shape).

Rejected alternative recorded: per-draw residual delta measured
in-harness (no dumps, diff tallies only) — cannot work because the
warp needs full frames offline; in-harness tallies can only carry the
rigid-blind byte diff, which is the M14 instrument, not the residual.

Degenerate-mask rule (recorded before running): a shape with <64
moved-Y pixels uses shift (0,0) (synth = blend). Rationale: masked SAD
over a near-empty mask has no minimum to find; there is no motion to
compensate. Shapes hitting this rule are tabled.

## Schedule: 6(C+1) contiguous-block scan

Six contiguous blocks of (C+1) replays; replay r carries shape
r mod (C+1) (M13 modN select, unchanged) and the phase of its block:

| block | replays | phase | seam |
| --- | --- | --- | --- |
| v0a | 0..C | v0 (rep a) | disarmed |
| v0b | C+1..2C+1 | v0 (rep b, reference) | disarmed |
| mida | 2C+2..3C+2 | mid (rep a, +0.05) | armed, scale 0.5 |
| midb | 3C+3..4C+3 | mid (rep b) | armed, scale 0.5 |
| fulla | 4C+4..5C+4 | full (rep a, +0.1) | armed, scale 1.0 |
| fullb | 5C+5..6C+5 | full (rep b) | armed, scale 1.0 |

Bounds: nreps = 6(C+1), kfrom = 2(C+1) (seam arms, scale 0.5),
kfull = 4(C+1) (scale 1.0). Per-shape reference = last v0b rep
(kref = (C+1)+s, warm: the M14 det3 lesson — shape 0's ref is replay
C+1 ≥ 571, never replay 0). Contiguous blocks (not interleaved
phases) so the seam arms once and the scale switches once, exactly
like the proven M15 3-phase capture.

Replay counts with the M15 determinism floors: M15 measured mid/full
phases 50/50 identical (one xd2, one hash each) and v0 99/99
identical plus the cold r0; M14 2P+2D showed n=2 per shape bounds
predecessor-dependence (619/644 uniform, 25 spread ≤10 B). Those
floors justify n=2 per (shape, phase) here: the a/b pair is the
within-(shape,phase) uniformity receipt (hash equality + xd
equality for mid/full; hash equality for v0a — no second stash, see
below). Total ≈ 4746 replays at C≈790 (the brief estimated ~3x
autoscan; 2 reps × 3 phases = 1.5x autoscan carries the same
uniformity receipt per phase as 2P+2D, so no third rep). C is
frame-dependent and tabled as measured.

## Dumps and probe rows

- v0_s: dumped post-loop from the per-shape ref stash (M13 refs,
  same 768 MiB budget guard as autoscan: (C+1) frames ≈ 453 MB).
- mid_s / full_s: captured at the b-rep (last rep of each
  (shape,phase)) and written per replay, fail-soft, to
  `$SSX_M16_DUMP_DIR/m16-{mid,full}-sNNNN.bin` (2(C+1) writes,
  ≈ 907 MB; no extra RAM stash — mid+full stashes would triple
  RAM past the guard).
- v0a reps are hash rows only (no v0a stash/dump: uniformity via
  hash equality with the v0b ref, the M14/M15 hash-histogram
  precedent; mismatches tabled with the shape caveated).
- Per-replay `m16_ref2` rows: r, shape, clk, phase, rep a/b, ok,
  xd2, xdmax, xdmean, hash, refhash (v0 rows: hash + refhash, xd2
  by hash rule; mid/full rows: live xd vs the shape's v0 ref from
  the M13 diff block). Guard `m16_win`: mode + bounds + dump
  ok-counts + per-phase hash-uniformity counts.
- Inherited M13 per-shape tallies span mid+full (n2=4); tabled as
  observed, like M15's inherited M10 aggregate.

## Offline warp protocol (`loo.py`, copied from `synth.py`)

1. Shape-0 triplet first: full ±24 masked-SAD search → shift_0,
   synth_0, R_0 (the new frame's total; M15's frame read 13418 B —
   frames differ per run, tabled as measured).
2. Per shape: full 49² masked-SAD search (M15 `sad_shift` verbatim),
   parallelized over shapes; single-shape cost measured first to
   size workers inside the box. Fallback if box-pressured:
   coarse (stride-4) + 3×3 refine, validated by full search on
   shape-0 + every 8th shape (100/100 agreement required, else
   full search for all). The path taken is recorded with receipts.
3. Attribution tables (M14-autoscan shape): R_s per shape; top-10
   carriers by removed share (clk/shape/surviving/removed/draw
   bytes/samp); share arithmetic (positive/zero/negative counts,
   max/min/median, Σ positive vs R_0, top fraction); negatives
   list; scan cross-checks (ndraws vs cons_any, spans ok,
   kref pattern, seam = 4(C+1) × covering loads).
4. HUD-edge: per-carrier removed-residual maps (residual_0 pixels
   vanishing in residual_s) + top/mid/bot band clustering; draw
   identification if the scan resolves it.
5. PNGs: base / diff-map / top-carrier overlay(s) if they
   discriminate, 320x224, <5 MB total.

## What "attributed" means numerically

The residual is attributed when the report tables, on the one synth
frame: R_0 (bytes + Y-|d| histogram, M15 shape); every shape's R_s
and removed share R_0 − R_s; the top carriers + full distribution +
negatives/zeros; and Σ positive shares against R_0 (M14 det4 read
74%, M15 arm B 62.5% — strict additivity is not assumed; the ratio
is the completeness receipt, tabled as measured). Deliverable: which
draws carry the non-rigid remainder.

## Arm table (recorded before running)

| Arm | Player (header) | Env (plus standard replay/determinism/probe) | Replays | Purpose |
| --- | --- | --- | --- | --- |
| A m16-loo | `players/m16-loo` (M16 header) | `SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M16_LOO=1 SSX_M9_SURV=1 SSX_M16_DUMP_DIR=/Volumes/Extreme\ SSD/m16` | 6(C+1) ≈ 4746 | per-draw withheld-synth triplets + dumps + per-(shape,phase) determinism on one frame; shape 0 is the verbatim control |

Standard env: `SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1` +
`SSX_NATIVE_PROBE` on the m16 SSD dir; dual core + `--cpu-thread`;
`--immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock
--seconds 240`; fresh profile `m16-loo`; run dir + probe + dumps
under `/Volumes/Extreme SSD/m16/`.

Single arm: shape 0 is the verbatim control on the SAME frame, so no
second arm can validate R_0 (every run records its own frame); the
M15 dumps on the SSD validate only the `synth.py` code path, which
`loo.py` inherits verbatim for shape 0.

Per-arm records: wall time, exit, probe bytes + sha, determinism
rows (per-(shape,phase) a/b uniformity + hash histograms, same
shape as the M15 per-phase table).

## M16 header delta (env-gated; unset = M15 behavior)

- `m16_want` = drawscan-wanted && slot mode && !autoscan &&
  `SSX_M16_LOO==1`; `m16_loo` = want && scan (fail-closed over the
  same 768 MiB ref budget; cap lifted to C like autoscan).
- Bounds fold into the runtime bounds: nreps 6(C+1), kfrom 2(C+1);
  `m16_kfull` = 4(C+1). `m14_perreplay`/`m15_mid` exclude `m16_want`
  (defense in depth; already excluded via `m10_ramref==0`).
- On-demand shape streams extended to M16 (validate-only spans;
  no C×2-frame prebuild).
- Seam: arm at kfrom with `s_m15_scale=0.5` (mid), 1.0 at kfull
  (full); `s_m15_scale` reused, M16-gated.
- M13 ref/diff block: refs capture over v0a+v0b (last = v0b, warm);
  mid/full diff live vs shape refs; M16 hook records per-replay
  rows and writes mid_b/full_b dumps; post-loop dumps v0 refs.
- `restored` detail gains `m16loo=%d m16kfull=%u`.

## Risks (recorded before running)

- Per-replay dump I/O inside the sequence: after render+diff per
  replay; forced determinism makes wall the only cost. Fail-soft
  with ok-counts; a missing dir still yields probe rows (re-run).
- If mid/full a/b pairs mismatch widely (beyond M14's ≤10 B
  precedent), dumps still define the attribution frame; the
  mismatch table becomes the caveat.
- No second stash: v0a uniformity rests on hash equality (precedent:
  M14/M15 hash histograms). A v0a mismatch leaves that shape's v0a
  xd2 n/a (tabled, shape caveated).
