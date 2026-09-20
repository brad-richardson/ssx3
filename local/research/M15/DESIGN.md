# M15 — Design (recorded before running)

Base pair: renders at slot-0 v0 (pristine, +0.0) and v1 (+0.1, M7's
shape on word 3). Ground truth: render at the true mid matrix (+0.05)
— the harness renders this exactly via the seam. Synth: offline
image-space interpolation between the dumped v0/v1 pair (method below).
No device work. One recorded frame per run carries all arms that must
combine (M14 §Step 3: every run records its own frame).

## Synth method choice (implementer's call)

Chosen: global-translation warp + blend. Estimate the dominant (dx,dy)
image shift between the v0 and v1 dumps (SAD search on the Y plane),
shift v0 forward by half and v1 back by half, average. Plane-separated
(Y vs U/V) so odd-pixel shifts never break YUYV pairing; exact
algorithm + estimated shift recorded with the results.

Why warp, not mid-matrix re-render: the harness's mid-matrix render IS
the truth path (it applies +0.05 through the same seam), so using it as
"synth" would read 0 residual by construction and measure nothing. Warp
captures the rigid camera component in image space; content that breaks
the rigid assumption (dynamic draws) lands in the residual — the split
the M14 thesis predicts. Control: 50 mid replays must read identical
(harness renders mid exactly + deterministically). Baseline for the warp:
plain 50% byte blend (no motion compensation), to table what the warp buys.

Rejected alternative recorded: per-draw leave-one-out warp (render each
shape at v0/v1/mid, warp per draw, attribute residual per draw) — needs
a same-frame 3-phase scan (~3x autoscan cost + warp in the loop); gap row
in the report, needs its own brief.

## Arm table (recorded before running)

| Arm | Player (header) | Env (plus standard replay/determinism/probe) | Replays | Purpose |
| --- | --- | --- | --- | --- |
| A m15-mid | `players/m15-mid` (M15 header) | `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M15_MID=1 SSX_M15_DUMP_DIR=/Volumes/Extreme\ SSD/m15` | 200: 100 v0 + 50 mid + 50 full | base pair + truth + dumps + per-phase determinism (N≥10: 100/50/50) |
| B m15-scan | M14 `players/m14-autoscan2` (M14 header, unchanged instrument) | M14 det4 env (`SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1`) | 4(C+1) | delta carrier table: where to look for the residual (own recorded frame; frames differ per run, tabled as observed) |

Standard env both arms: `SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1`
+ `SSX_NATIVE_PROBE` on the m15 SSD dir; dual core + `--cpu-thread`;
`--immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock
--seconds 240`; fresh profiles `m15-mid`, `m15-scan`; run dirs +
probes + dumps under `/Volumes/Extreme SSD/m15/`.

Per-arm records (step 2): wall time, exit, probe bytes + shas,
determinism rows (same shape as the M14 baseline table: per-phase
n/gt0/uniform/xd2min/xd2max/xdmax/xdmean + hash histograms).

## M15 header delta (env-gated; unset = M14 behavior)

- `s_m15_scale` (default 1.0): the M8 slot-delta add becomes
  `*f += 0.1f * s_m15_scale`. Non-M15 runs never touch it.
- `m15_mid` = `m10_ramref && !autoscan && !perreplay && SSX_M15_MID==1`.
- Phases over the standard 200/100 sequence: v0 replays 0–99 (seam
  disarmed), mid 100–149 (slot armed, scale 0.5 → +0.05), full 150–199
  (scale 1.0 → +0.1). Reference = replay 99's scratch (as M10 ref2).
- Per-replay rows `m15_ref2` (r, phase v0/mid/full, ok, xd2, xdmax,
  xdmean, hash) + guard `m15_win`; M10 ref2 aggregate left running
  (spans mid+full; tabled as observed).
- Dumps (fail-soft, receipted in `m15_win`): r0, v0(r99), mid(r149),
  full(r199) scratch frames to `$SSX_M15_DUMP_DIR/m15-*.bin`.
- XFB geometry assumption for decode: 640x448 YUYV (573440 = 640·448·2);
  verified by successful decode, else reasoned absence.

## Compare plan (step 3)

`synth.py`: decode dumps → estimate shift → warp-synth + blend
baseline → byte diffs vs truth (M14 §analyze.py shape: xd/xdmax/xdmean
+ moved-bytes distributions) → residual-carrier discussion from arm B
→ base/synth/truth/diff-map PNGs (downscaled, <5MB total).
Deliverable table: what interpolates cleanly vs what breaks, with bytes.
