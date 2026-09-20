# M14 — Camera-delta true delta: REPORT

M7's +0.1 camera delta on slot 0 against a rendered reference with the
full per-replay moved-bytes series, plus M13's leave-one-out drawscan
generalized to slot-0-scale frames (autoscan: runtime cap + 2P+2D
schedule) run on the camera delta. Desktop only. Runbook
`local/muse/prompts/M14.md`. No `adb`, no device. Tables, no verdicts.

Headers read first: `local/research/M13/REPORT.md` (the drawscan
instrument + guard-receipt pattern), `local/research/M7/REPORT.md`
Step 3 (the original +0.1 camera delta, measured 0 only because the
reference was uninit), `local/research/M10/REPORT.md` (RAMREF
rendered-reference method), and the base header
`local/research/M13/m13_replay_context.h`.

Time box 6 hours; used about 1. Three lease waits (P1v held the lease
for ~20 minutes before the det3 run; logged in
`local/research/M14/waits.log`; never forced).

## Baseline note (read before the tables)

The M13 header on disk (`local/research/M13/m13_replay_context.h`, clean
tree) hashes to
`b09643b1590dbae3bfeb47b57c0d1ecc0fadc26039638c8a43d4cbad5354f3a0`
via `shasum -a 256` (trust `shasum`, not memory; matches the M13 report's
pinned prefix).
Step 1 copied the on-disk file verbatim to
`local/research/M14/m14_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8/M9/M10/M11/M12/M13 mechanism is
kept in all steps: PE mask, verbatim execute stream, restore, stall, pipe
snapshot, watched-window re-hash, `done`, XFB hash + scratch redirect,
side-effect counters, continuation capture, scoped bus, `m6frame`,
presenter tracing, record guard, trig_imx probe, M7 full/delta transforms,
per-replay xdiff stats, M8 census/slot/proj modes with stream-epoch
census, M9 VAT walk + slot/survival, M10 order/matrix/epoch/occ walks +
NOP/RAM/ref2 arms, M11 slot chain + idx decode + NOPSHR/NOPIDX/NOPTEXT
arms, M12 slot chain + RAMREF alias + alternating-NOP windows, M13
per-draw leave-one-out scan. All M14 additions are env-gated with defaults
that preserve M13 behavior (`SSX_M14_PERREPLAY` / `SSX_M14_AUTOSCAN`
unset); the committed header is the step-3 header (`40533e4d…`), from
which the step-1 and step-2 runs are reproducible via env.

M14 step 2 (`SSX_M14_PERREPLAY=1`, M10 RAMREF only, mutually exclusive
with autoscan): per-replay moved-bytes series — pristine replays stash
their scratch bytes (diffed post-loop against the rendered reference,
which does not exist when they run), delta replays record live; one
`m14_win` guard line + one `m14_ref2` event per replay (200 rows).

M14 step 3 (`SSX_M14_AUTOSCAN=1`, drawscan-wanted only): autoscan —
runtime cap lifted to the frame's own consumer count (fail-closed over a
768 MiB ref-bytes budget), runtime sequence bounds 4(C+1) replays with the
split at 2(C+1) (2 pristine + 2 delta replays per shape, so every shape's
reference is warm and n2=2 carries a within-shape uniformity receipt),
on-demand per-replay shape streams (byte-identical to the prebuilt
copies), replay-indexed timing stores converted to runtime-sized vectors,
and a fail-closed guard on the `m13_nop` receipt rows (`want && !scan`
left those vectors empty, so indexing them was out-of-bounds; rows now
carry ok=0).

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M13. `m14-det*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M14\n'`, removed after each run);
the log is `local/research/M14/waits.log` (3 waits, four claim/release
pairs, one annotation, never forced). Builds ran any time; no build ran
during a run.
`complete_hazard_resets` (harness field, as observed): det 1, det2/det3/
det4 0; every sequence is complete with `done` and clean counters (see
tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `b09643b1…` (= M13 on disk) | `players/m14-baseline` | `m14-det-run` (`m14-det`, `SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1`) | `m14-det-probe.jsonl` |
| 2 camera true delta | `54c182b4…` | `players/m14-perreplay` | `m14-det2-run` (`m14-det2`, `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M14_PERREPLAY=1`) | `m14-det2-probe.jsonl` |
| 3 drawscan exact-fit | `9eb23c24…` | `players/m14-autoscan` | `m14-det3-run` (`m14-det3`, `SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1`) | `m14-det3-probe.jsonl` |
| 3 drawscan 2P+2D | `40533e4d…` (= committed) | `players/m14-autoscan2` | `m14-det4-run` (`m14-det4`, same env) | `m14-det4-probe.jsonl` |

The committed header is `40533e4d…`. Step 1 needs no new header code;
step 2 adds the per-replay series; step 3 adds autoscan (the exact-fit
1P+1D schedule is revved to 2P+2D in the committed header; the det3
attempt is reproducible only from the exact-fit header snapshot on the
SSD, see §Player and run dir paths, and its rows are tabulated as the
attempt log in §Step 3). The `m14-det3` attempt is sequence-complete
(1672/1672 `done`, clean continuation) with a warm caveat on shape 0
only (kref=0); its per-shape surviving rows are tabulated alongside the
re-run.

Player dirs live under `local/research/M14/players/` (the build driver
requires outputs under `local/`; they are gitignored build outputs, never
committed). Run dirs and every probe jsonl live under
`/Volumes/Extreme SSD/m14/` (symlink-free; `realpath` is the path as
written). Probes, runs and players are not committed.

## Step 1 — baseline (M13 slot-0 alternating end state as control)

Unmodified copy, M13 slot-0 alternating env. `analyze.py` prints 200 rows +
`done` + `xfb_equal_scratch=0/200` (forced-RAM signature, as M13 det) +
`live_xfb_untouched=1` + `dafter_live`/`dframe`/`dpres`/`dimx` all 0/0 +
`pediff`/`vidiff` 0/0. Control for steps 2–3.

This run recorded a new frame (325746 B / 2649 updates, draws=1781,
verts=29877, covering=75, cons=853), so the byte counts below are that
frame's, next to M13's `m13-det` frame (299569 B, total 40688, shares
40294/1371/850) for shape comparison only.

Seam-application receipt (`xform_stats`, slot mode):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 214600 (= 200 × 1073 indexed) |
| `hits` | 7500 (= 100 × 75 covering loads; second half counting-only) |
| `regcalls` | 0 |

Guard receipt (`m12_win`): `alt=1 slot=0 scheme=mod4
map=0:verbatim,1:nopshr,2:nopidx,3:notext kref=96,97,98,99 sel_shr=0
sel_idx=0 sel_text=0 m10nop_ok=0`. NOP-span receipts (`m12_nop`):
`shr_ok=1 shr_draws=853 shr_bytes=148748 idx_ok=1 idx_draws=47
idx_bytes=53157 text_ok=1 text_draws=17 text_bytes=5719`. The single
`m10_ref2` is off by design (`ref=0 n2=0`).

Per-window ref2 rows (SAME recorded frame; per-window pristine refs):

| win | name | kref | refhash | n2 | gt0 | uniform2 | xd2min/xd2max | xdmax2max | xdmean2 |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | verbatim (total) | 96 | `e77f8d8f5405e129` | 25 | 25 | 25 | 30785 / 30785 | 107 | 2.377 |
| 1 | nopshr (indexed-only) | 97 | `36c049c8b369e4ac` | 25 | 25 | 25 | 515 / 515 | 94 | 5.693 |
| 2 | nopidx (shared-only) | 98 | `14b49f5dfb90c943` | 25 | 25 | 25 | 29327 / 29327 | 107 | 2.312 |
| 3 | notext (non-texture-mediated) | 99 | `b18fc9cca8a15cd0` | 25 | 25 | 25 | 29577 / 29577 | 107 | 2.329 |

Samples: w0 `r100:30785/107/2.377,r104:30785/107/2.377,r108:30785/107/2.377`;
w1 `r101:515/94/5.693,r105:515/94/5.693,r109:515/94/5.693`;
w2 `r102:29327/107/2.312,r106:29327/107/2.312,r110:29327/107/2.312`;
w3 `r103:29577/107/2.329,r107:29577/107/2.329,r111:29577/107/2.329`.

Subtracted shares (total win0 30785 minus surviving window, same frame):

| removed set | surviving win | surviving xd2 | removed share (total − surviving) |
| --- | ---: | ---: | ---: |
| shared-path (nopshr) | 1 | 515 | 30270 |
| indexed-path (nopidx) | 2 | 29327 | 1458 |
| texture-epoch (notext) | 3 | 29577 | 1208 |

Partition cross-checks (table):

| Check | Value |
| --- | --- |
| `shr_draws` vs `cons_any` | 853 = 853 |
| `idx_draws` vs `exp_draws` | 47 = 47 |
| `text_draws` vs draws 1..17 (2 texture epochs) | 17 = 17 |
| `idx_pos_draws` vs M9 `pos_indexed` | 49 = 49 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 42 = 42 |
| seam hits vs 100 × covering loads | 7500 = 100×75 |

Own-frame M9 census, m14-det (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1732 | 49 | n/a | n/a |
| Tex0 | 1781 | 0 | 1762 | 1762 |
| Tex1 | 1739 | 42 | 407 | 365 |
| Tex2 | 1781 | 0 | 58 | 58 |
| Tex3-7 | 1781 | 0 | 0 | 0 |

Shared-pos reach total 1732 (`0:853 3:143 6:98 9:93 12:105 15:98
18:89 21:101 24:73 27:79`); tex2 shared+enabled reach `36:58`.
Decode row (slot 0): `idx_pos_draws=49 idx_pos_verts=7283 exp_draws=47
exp_verts=2543`, `tex_draws=0,42,0,0,0,0,0,0`, `tex_exp_draws` all zero.
Order row: covering=75 (`arr12=75`), cons_pos=853, cons_tex=0,
cons_any=853; first_cons=1 last_cons=1781; first covering load draw 0 /
off 2482 / kind 0, last 1717 / 314090; seam 7500 = 100×75.
Matrix: +0.1 on word 3 only, `mm_live=100 mm_snap=125`.
Survival trichotomy: live 100/100, per-vertex 75/0/25, shared-pos
75/0/25 (resident 100/100), shared-tex 0 (resident 0/100);
`dirty_post=25`, `zfreeze=0`; first-hit 0 → 0.1.
EFB copies n=3 (2 texture + XFB drain at draw 1781);
`epoch_cons=9,1,843,0`; occ: cons=853, culled=0, out-of-range=10,
in-range=843; `all_cull=all_scis=all_znever=0`.

Recorded without verdict: the M13 alternating machinery reproduces on a
new frame (four 25/25 uniform windows against their own shape's pristine
reference, guest/event clean); the shares above subtract against this
frame's total (30785) — the byte counts are frame-dependent (M13's
frame: total 40688, shares 40294/1371/850).

## Per-step wall table (final arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m14-det | 200 | 3.583 / 5.007 / 2.853 / 13.678 | 1.652 / 1.842 | 325746 / 2649 | YES | seq_wall_ms=1264.643 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m14-det2 | 200 | 5.465 / 6.494 / 5.074 / 14.478 | 2.063 / 2.323 | 329356 / 2751 | YES | seq_wall_ms=1629.855 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m14-det4 | 2576 | 5.803 / 7.477 / 5.042 / 14.496 | 2.351 / 2.774 | 355316 / 3064 | YES | seq_wall_ms=22860.334 completed=2576 xfb_equal=2576/2576 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/2576 live_xfb_untouched=1 live_same=2576/2576 |
```

Attempt wall row (sequence-complete 1672/1672 `done`, clean
continuation; exact-fit 1P+1D schedule, so shape 0's reference is replay
0 — tabulated as the attempt log in §Step 3):
`m14-det3`: 1672 replays, wall 8.553 / 9.689 / 7.147 / 20.979,
Thread-CPU 3.165 / 3.866, frame 390897 / 3397, `done`, `seq_wall_ms=
19413.845 completed=1672 xfb_equal=1672/1672 ... xfb_equal_scratch=0/1672
live_xfb_untouched=1 live_same=1672/1672`.

Frames differ per run (325746 … 390897 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table). All
rows: complete sequences, `done`, `restored det=1 dual=1`, `mask_bp=2
dls=0 walk=100% unknown=0 benign=1` in all runs.
`xfb_equal_scratch=0/N` on all rows is the forced-RAM signature
(rendered scratch vs fuchsia live ref), not a failure.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m14-det | 0.104 | 0.001 | 0.037 | 3.451 | 0.000 | 4.840 |
| m14-det2 | 0.099 | 0.001 | 0.030 | 5.335 | 0.000 | 6.342 |
| m14-det4 | 0.167 | 0.001 | 0.050 | 5.585 | 0.000 | 7.240 |
```

(`m14-det3`: 0.176 / 0.001 / 0.067 / 8.304 / 0.001 / 9.408.)

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m14-det | 1073 | 51504 | 40.7 |
| m14-det2 | 1433 | 68784 | 30.5 |
| m14-det4 | 2114 | 101472 | 20.7 |

(`m14-det3`: 2132 / 102336 / 20.5.)

## Step 2 — camera-delta true delta (M7's shape vs a rendered reference)

Slot choice (recorded why):

| Choice | Value |
| --- | --- |
| Slot | 0, word 3, +0.1 translation (M7's shape, M9/M10 slot mode) |
| Why | M7 Step 3: the projection matrix lives in XF regs where `LoadXFReg` never fires the seam, so slot-0 word 3 (position-matrix slot 0, row-0 tx) is the camera-most word the seam can reach; the +0.1 lands on word 3 only (11/11 siblings bit-identical, matrix table below); the M10 RAMREF arm carries the rendered reference (replay 99's scratch frame) |

One run (`SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1
SSX_M14_PERREPLAY=1`), one recorded frame (329356 B / 2751 updates,
draws=1528, verts=31404, covering=120, cons=699 all pos), 200/200
per-replay rows ok=1. Guard receipt (`m14_win`): `perreplay=1 ref=1
kref=99 refok=1 refhash=82fe20c19fa10d40 nreps=200 kfrom=100`.
Aggregate (`m10_ref2`): `ref=1 kref=100 refok=1 n2=100 gt0=100
uniform2=100 xd2min=53636 xd2max=53636 xdmax2max=106
xdmean2min=2.087 xdmean2max=2.087 refhash=82fe20c19fa10d40
samp=r100:53636/106/2.087,r101:53636/106/2.087,r102:53636/106/2.087`.

kref note (tabled): `m10_ref2` prints `kref=100` (it prints
`kTransformFrom`; inherited) while the reference bytes are replay 99's
(captured at `replays == kfrom-1`); `m14_win` prints the true `kref=99`;
both refhashes are identical (`82fe20c19fa10d40`).

Per-replay moved-bytes rows (vs the rendered reference; full 200 rows in
`analyze-det2.txt`):

| r | phase | ok | xd2 | xdmax | xdmean | hash |
| ---: | --- | :-: | ---: | ---: | ---: | --- |
| 0 | pristine | 1 | 127103 | 178 | 22.216 | `4fce8faf8c83c278` |
| 1 | pristine | 1 | 0 | 0 | 0.000 | `82fe20c19fa10d40` |
| 2 | pristine | 1 | 0 | 0 | 0.000 | `82fe20c19fa10d40` |
| 99 | pristine (ref) | 1 | 0 | 0 | 0.000 | `82fe20c19fa10d40` |
| 100 | delta | 1 | 53636 | 106 | 2.087 | `3c14673842bb7d0a` |
| 101 | delta | 1 | 53636 | 106 | 2.087 | `3c14673842bb7d0a` |
| 199 | delta | 1 | 53636 | 106 | 2.087 | `3c14673842bb7d0a` |

Moved-bytes distributions:

| phase | n | xd2 min / max | distinct xd2 | hist | distinct hashes |
| --- | ---: | --- | ---: | --- | ---: |
| pristine | 100 | 0 / 127103 | 2 | {0: 99, 127103: 1} | 2 (`4fce8faf8c83c278`: r0, `82fe20c19fa10d40`: r1–r99) |
| delta | 100 | 53636 / 53636 | 1 | {53636: 100} | 1 (`3c14673842bb7d0a` ×100) |

Second-half corroboration: `xform_stats` hits=12000 (= 100 × 120
covering loads; first half counting-only); M9 trichotomy over the second
half 100/100 perturbed in live, per-vertex and shared-pos snapshots
(`pos_res=100 tex_res=0 dirty_post=0`); matrix before/after at the
replay-100 first hit is +0.1 on word 3 only with post = pristine
replay-0 values (`mm_live=100 mm_snap=100`, word 11 `-0` post vs `-2` at
the first hit, live == snap post).

Own-frame M9 census, m14-det2 (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1436 | 92 | n/a | n/a |
| Tex0 | 1528 | 0 | 1466 | 1466 |
| Tex1 | 1466 | 62 | 472 | 410 |
| Tex2 | 1528 | 0 | 26 | 26 |
| Tex3 | 1528 | 0 | 7 | 7 |
| Tex4-7 | 1528 | 0 | 0 | 0 |

Shared-pos reach total 1436 (`0:699 3:105 6:59 9:100 12:96 15:87
18:56 21:96 24:45 27:93`); tex2 shared+enabled reach `36:26`.
(M11 mode is off in the pure-M10-slot env, so no `m11_idx` decode row
exists for this frame; see "What I could not do" 1.)
Order row: covering=120 (`arr12=120`), cons_pos=699, cons_tex=0,
cons_any=699; first_cons=1 last_cons=1528; first covering load draw 0 /
off 2784 / kind 0, last 1463 / 318148; seam 12000 = 100×120.
EFB copies n=7 (6 texture + XFB drain at draw 1528);
`epoch_cons=9,9,9,1,1,1,669,0`; occ: cons=699, culled=0,
out-of-range=30, in-range=669; `all_cull=all_scis=all_znever=0`.

Recorded without verdict: the slot-0 +0.1 camera delta moves 53636 of
573440 bytes identically on all 100 delta replays against the rendered
pristine reference; the 100 pristine replays read 0 except replay 0
(127103 B, the first-replay frame).

## Step 3 — drawscan the camera delta (autoscan)

Why autoscan (tabled): slot-0 frames carry 570+ consuming draws
(853/699/835/643 on the four M14 frames) — past the M13 128 draw cap
(fail-closed) and past a 200-replay sequence (each of the C+1 shapes
needs ≥1 pristine + ≥1 delta replay on the SAME recorded frame; every
run records its own frame, so cross-run chunking cannot combine).
Autoscan lifts the cap to the frame's own consumer count and sizes the
sequence to 4(C+1) replays (2 pristine + 2 delta per shape).

Final run (`SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1
SSX_M9_SURV=1`), one recorded frame (355316 B / 3064 updates,
draws=1498, verts=34375, covering=150, cons=643 all pos), 2576 replays,
644 interleaved shapes with one warm pristine reference each. Guard
receipt (`m13_win`): `scan=1 slot=0 scheme=modN nshapes=644 ndraws=643
cap=643 sel_shr=0 sel_idx=0 sel_text=0 m10nop_ok=0` — no M11 selector
armed, so shape 0 is the verbatim total. `restored` carries
`m14auto=1 m14cap=643 m14reps=2576 m14from=1288 m14perrep=0`. All 643
per-draw NOP spans ok=1. The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Shape-0 (verbatim total) row:

| shape | kref | refok | n2 | gt0 | uniform2 | xd2min/xd2max | xdmax2max | xdmean2 | refhash |
| ---: | ---: | :-: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 644 | 1 | 2 | 2 | 2 | 44087 / 44087 | 106 | 2.284 | `d9f8be7b82864d0b` |

Samples shape 0: `r1288:44087/106/2.284,r1932:44087/106/2.284`. The full
644-row shape table + 643-row removed-shares table are in
`analyze-det4.txt`.

Top-10 carriers by removed share (total shape0 44087 minus surviving
shape, same frame):

| rank | clk | shape | surviving xd2 | removed share | draw bytes | samp |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 1429 | 574 | 35794 | 8293 | 1203 | r1862:35794/106/2.485,r2506:35794/106/2.485 |
| 2 | 1436 | 581 | 42373 | 1714 | 99 | r1869:42373/106/2.127,r2513:42373/106/2.127 |
| 3 | 429 | 377 | 42397 | 1690 | 51 | r1665:42397/106/2.320,r2309:42397/106/2.320 |
| 4 | 1428 | 573 | 42628 | 1459 | 1203 | r1861:42628/106/2.319,r2505:42628/106/2.319 |
| 5 | 436 | 384 | 42937 | 1150 | 45 | r1672:42937/106/2.320,r2316:42937/106/2.320 |
| 6 | 430 | 378 | 43037 | 1050 | 51 | r1666:43037/106/2.338,r2310:43037/106/2.338 |
| 7 | 426 | 374 | 43251 | 836 | 51 | r1662:43251/106/2.332,r2306:43251/106/2.332 |
| 8 | 1379 | 524 | 43346 | 741 | 12323 | r1812:43346/106/2.298,r2456:43346/106/2.298 |
| 9 | 428 | 376 | 43457 | 630 | 51 | r1664:43457/106/2.153,r2308:43457/106/2.153 |
| 10 | 447 | 395 | 43482 | 605 | 45 | r1683:43482/106/2.317,r2327:43482/106/2.317 |

Share arithmetic (total 44087; 643 shares):

| Field | Value |
| --- | --- |
| positive / zero / negative | 229 / 333 / 81 |
| max / min / median | 8293 (draw 1429) / −990 (draw 427) / 0 |
| sum of positive shares vs total | 32554 vs 44087 (74%) |
| top carrier fraction | 8293 / 44087 (19%) |

Within-shape uniformity (n2=2 with different predecessors, so the pair
bounds predecessor-dependence): 619/644 shapes read 2/2/2; 25 shapes
read 2/2/1 with |xd2max−xd2min| spread 1–10 B (worst: shape 271 / clk
323, 44089/44099, `r1559:44089/106/2.279,r2203:44099/106/2.279`).

Negatives (81, range −990…−1; removing the draw widens the delta):

| share | clk | shape | draw bytes |
| ---: | ---: | ---: | ---: |
| −990 | 427 | 375 | 51 |
| −184 | 5 | 5 | 131 |
| −151 | 6 | 6 | 131 |
| −150 | 4 | 4 | 131 |
| −139 | 9 | 9 | 19 |
| −119 | 3 | 3 | 131 |
| −99 | 2 | 2 | 131 |
| −95 | 450 | 398 | 39 |

(remaining 73 negatives in −95…−1; full list in `analyze-det4.txt`).

Scan cross-checks (table):

| Check | Value |
| --- | --- |
| `ndraws` vs `cons_any` | 643 = 643 |
| per-draw spans ok | 643 / 643 |
| `n2`/`gt0` pattern | 2/2 on all 644 shapes; uniform2 2 on 619, 1 on 25 |
| `kref` = last pristine replay of shape | shape+644 on all 644 (shape 0: 644, warm) |
| seam hits vs 1288 × covering loads | 193200 = 1288×150 |
| shared Tex2 reach 36 vs `cons_tex` | 30 vs 0 (slot-0 consumers are all pos) |
| `tex_exp_draws[1]` (indexed-Tex1 exposure of slot 0) | 0 |
| `exp_draws` (indexed-position exposure of slot 0) | 120 |

Own-frame context, m14-det4: VAT Pos 1376/122; Tex0 1498/0/1439/1439;
Tex1 1403/95/512/417; Tex2 1498/0/30/30; Tex3 1498/0/7/7; Tex4
1498/0/7/7; rest 0 enabled. Shared-pos reach total 1376 (`0:643 3:133
6:63 9:90 12:82 15:92 18:72 21:79 24:52 27:70`). Order: covering=150
(`arr12=150`), cons_pos=643, cons_tex=0; first_cons=1 last_cons=1498.
Matrix: +0.1 on word 3 only, `mm_live=1288 mm_snap=1288`.
Survival: live/per-vertex/shared-pos 1288/1288 (`pos_res=1288`),
shared-tex 0, `dirty_post=0`; first-hit 0 → 0.1. EFB copies n=7 (6
texture + XFB drain at draw 1498); `epoch_cons=9,9,9,1,1,1,613,0`; occ:
cons=643, culled=0, out-of-range=30, in-range=613.

Recorded without verdict: the drawscan arm attributes the slot-0 44087 B
total to individual consuming draws on the one shared frame — one draw
carries 8293 B, the next carries 1714 B, 229 read positive, 333 read
exactly 0, 81 read negative (worst −990) — with 619/644 shapes uniform
and 25/644 spread ≤10 B across their two delta replays.

Attempt log (`m14-det3`, exact-fit 1P+1D header `9eb23c24…`, same env,
new frame 390897 B / 3397 updates, draws=1791, covering=175, cons=835):
sequence-complete 1672/1672 `done` with `scan=1 nshapes=836 ndraws=835
cap=835`, clean continuation (`resume_xfb` hash matches), seam 146300 =
836×175, survival/matrix 836/836, occ 785/835 in-range (copies n=11).
The exact-fit schedule gives each shape exactly one pristine replay, so
shape 0's reference is replay 0 (`kref=0 refok=1 n2=1 gt0=1 uniform2=1
xd2=116170 xdmax=181 xdmean=14.443 refhash=0aae52ec77d4742a
samp=r836:116170/181/14.443`); all 836 shapes read n2/gt0/uniform2
1/1/1 with `kref == shape`, and all 835 NOP spans are ok=1. Surviving
xd2 over the 835 left-out shapes clusters at 33690–36836 (median 36461,
mean 36439.9), so all 835 removed shares read positive (79334–82480,
median 79709; sum 66574649 vs total 116170). Top-10 by share: clks
473/474/475/1729/471/470/1755/1754/1781/1782, shares 82480–80160,
survivors 33690–36010, draw bytes 51/51/51/99/51/51/99/99/99/99
(full 836-row table in `analyze-det3.txt`).
Fix: 2P+2D schedule (every shape's reference warm, n2=2), rebuilt,
re-ran as `m14-det4`.

Diagnosis receipts (tabled, no verdict):

| Receipt | Value |
| --- | --- |
| det3 shape-0 kref | 0 (replay 0; n2=1) |
| det4 shape-0 kref | 644 (warm; n2=2) |
| M13 det4 shape-0 kref (31 shapes, kfrom=100) | 93 (warm; n2=3–4) |
| step-2 replay-0 vs warm pristine (same streams) | 127103 B (r1–r99 all 0) |
| det3 share span over 835 draws | 79334–82480 (span 3146) |
| det3 rank-1 draw bytes vs share | 51 B (clk 473) vs 82480 |
| det3 sum of positive shares / total | 66574649 / 116170 (573×) |
| det4 sum of positive shares / total | 32554 / 44087 (74%) |
| det4 warm total vs step-2 warm total | 44087 vs 53636 (different frames) |

## Mechanism table (brief items this run works through)

| Brief item | Standing | Receipt |
| --- | --- | --- |
| slot-0 camera true delta vs rendered ref + per-replay series | measured | §Step 2: 200/200 rows ok=1; pristine {0: 99, 127103: 1}; delta {53636: 100} |
| drawscan of the camera delta (which draws move camera pixels) | measured | §Step 3 det4: 644-shape scan; one 8293-B carrier (draw 1429), 229 +/333 zero/81 −; n2=2 (619 uniform, 25 spread ≤10 B) |
| M13 gap 3 (drawscan 128 cap; slot-0-scale needs a bigger scan) | measured (autoscan: runtime cap + 2P+2D schedule) | §Step 3: cap=C, nreps=4(C+1); det3 exact-fit attempt kept with tables |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m14-det | `fc=8042` | `replay_disabled=0 fc=8045 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m14-det2 | `fc=8141` | `replay_disabled=0 fc=8144 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m14-det3 | `fc=8139` | `replay_disabled=0 fc=8142 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m14-det4 | `fc=6373` | `replay_disabled=0 fc=6376 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the quadruple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M13/M12/M11/M10/M9/M8/M7 sequence
hashes and all M6 sequence and M5 sequence/disabled hashes) is tabulated
as observed. `resume fc − fc0 = 3` in each run (the live record window;
per-replay `dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m14-det | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m14-det2 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m14-det3 | 1672/1672 / 0/1672 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m14-det4 | 2576/2576 / 0/2576 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

Scratch `0/N` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M13/build_replay_player.py`; `m14-baseline` was built
from the step-1 header — the driver compiles
`local/research/M14/m14_replay_context.h`):

```
python3 local/research/M14/build_replay_player.py local/research/M14/players/m14-baseline
python3 local/research/M14/build_replay_player.py local/research/M14/players/m14-perreplay
python3 local/research/M14/build_replay_player.py local/research/M14/players/m14-autoscan
python3 local/research/M14/build_replay_player.py local/research/M14/players/m14-autoscan2
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M14\n'`,
remove after each run; profiles fresh per run):

```
SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m14/m14-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M14/players/m14-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m14-det --cpu-thread --output "/Volumes/Extreme SSD/m14/m14-det-run" --seconds 240
SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M14_PERREPLAY=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m14/m14-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M14/players/m14-perreplay --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m14-det2 --cpu-thread --output "/Volumes/Extreme SSD/m14/m14-det2-run" --seconds 240
SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m14/m14-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M14/players/m14-autoscan --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m14-det3 --cpu-thread --output "/Volumes/Extreme SSD/m14/m14-det3-run" --seconds 240
SSX_M12_SLOT=0 SSX_M13_DRAWSCAN=1 SSX_M14_AUTOSCAN=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m14/m14-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M14/players/m14-autoscan2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m14-det4 --cpu-thread --output "/Volumes/Extreme SSD/m14/m14-det4-run" --seconds 240
```

Analysis:

```
python3 local/research/M14/analyze.py "m14-det=/Volumes/Extreme SSD/m14/m14-det-probe.jsonl" "m14-det2=/Volumes/Extreme SSD/m14/m14-det2-probe.jsonl" "m14-det3=/Volumes/Extreme SSD/m14/m14-det3-probe.jsonl" "m14-det4=/Volumes/Extreme SSD/m14/m14-det4-probe.jsonl"
python3 local/research/M14/analyze.py "m14-det=/Volumes/Extreme SSD/m14/m14-det-probe.jsonl"
python3 local/research/M14/analyze.py "m14-det2=/Volumes/Extreme SSD/m14/m14-det2-probe.jsonl"
python3 local/research/M14/analyze.py "m14-det3=/Volumes/Extreme SSD/m14/m14-det3-probe.jsonl"
python3 local/research/M14/analyze.py "m14-det4=/Volumes/Extreme SSD/m14/m14-det4-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M14/` — `m14_replay_context.h`
(`40533e4d…`), `build_replay_player.py`, `analyze.py`, `REPORT.md` (this
file), `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m14/` —
`m14-det-probe.jsonl` (21897049 B), `m14-det2-probe.jsonl` (20916626 B),
`m14-det3-probe.jsonl` (19047335 B), `m14-det4-probe.jsonl` (18778263 B)
and the matching `-run` dirs and `-run.log` harness receipts;
`analyze-all.txt` (the four-arm analyzer output) and `analyze-det.txt`,
`analyze-det2.txt`, `analyze-det3.txt`, `analyze-det4.txt` (per-arm
outputs); per-step header snapshots `m14_replay_context.step1.h` (=
M13 header), `m14_replay_context.step2.h` (`54c182b4…`),
`m14_replay_context.step3-exactfit.h` (`9eb23c24…`, the det3 attempt's
header), `m14_replay_context.step3.h` (= committed header). Players
(gitignored):
`local/research/M14/players/{m14-baseline,m14-perreplay,m14-autoscan,m14-autoscan2}/`
(each with `player`, `build.json`, launchers). All paths above are
symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m14-baseline` `b09643b1590d` /
`cef4e601a09f` (player hash identical to M13's `m13-drawscan2`: same
header compiles to the same binary), `m14-perreplay` `54c182b4d467` /
`11e18608fd10`, `m14-autoscan` `9eb23c24c67a` / `7eabdb212c0a`,
`m14-autoscan2` `40533e4dba11` / `12f34ed7a06b`.

## What I could not do

1. The step-2 arm carries no indexed-path decode row: the pure-M10-slot
env leaves M11 mode off, so no `m11_idx` event exists for the det2
frame (cf. the det/det4 decode rows with `exp_draws` 47/120). An M12
RAMREF-mode re-run would carry it; not run.
2. The 25 non-uniform det4 shapes bound predecessor-dependence at ≤10 B
but the byte-level source (which EFB-copy texels differ between the two
delta replays) is unattributed.
3. The `m10_copy` detail renders 6 of 7 copies on the det2/det4 frames
(1024 B buffer cap; the XFB drain is the unrendered 7th; det3's n=11
renders fewer still). `epoch_cons` carries all epochs, and the report's
epoch tables are built from it (inherited cosmetic, not a receipt gap).
4. The det3 exact-fit attempt is reproducible only from the SSD header
snapshot (`m14_replay_context.step3-exactfit.h`, `9eb23c24…`); the
committed header revs the autoscan schedule to 2P+2D.
5. Player dirs are under `local/research/M14/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs and all
probes are on the SSD as ordered.
6. Desktop only; no device work.

## Files

Committed under `local/research/M14/`: `m14_replay_context.h` (research
header, `40533e4d…`), `build_replay_player.py` (M13 driver, header path
only), `analyze.py` (M13 tables unchanged + M14 `m14_win`/`m14_ref2`
parsing, per-replay moved-bytes table + distributions, drawscan top-10
carriers; missing keys print as n/a / sections skipped), `REPORT.md`
(this file), `waits.log` (3 waits, four claim/release pairs, one
annotation).

## Header diffs per step (`diff -u` against the M13 header)

Step 1: empty (verbatim copy). Step 2 follows, generated from
`/Volumes/Extreme SSD/m14/m14_replay_context.step2.h`. Step 3 follows,
cumulative (step 2 + step 3), generated from the committed
`local/research/M14/m14_replay_context.h` (= step 3; the step-3 header
adds env-gated branches only, so the step-1/step-2 arms are reproducible
from it via env).

### Step 2

```diff
--- local/research/M13/m13_replay_context.h	2026-09-19 16:01:30
+++ /Volumes/Extreme SSD/m14/m14_replay_context.step2.h	2026-09-19 19:34:08
@@ -1978,6 +1978,27 @@
       m13_bytes[s] = dr.size;
     }
   }
+  // M14 step 2: per-replay moved-bytes series (SSX_M14_PERREPLAY=1, M10
+  // RAMREF only). The M10 ref2 block keeps tallies + 3 samples; the
+  // camera-delta true delta needs every replay's moved bytes against the
+  // rendered reference (replay kTransformFrom-1's scratch frame). Pristine
+  // replays stash their scratch bytes (diffed post-loop, once the ref
+  // exists); delta replays record live in the M10 block below. Unset =
+  // M13 behavior (no stash, no rows).
+  const int m14_perreplay = (m10_ramref != 0) ? ([] {
+                              const char* v = std::getenv("SSX_M14_PERREPLAY");
+                              return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                            })()
+                                            : 0;
+  std::vector<u8> m14_prist;  // kTransformFrom pristine frames, stashed bytes
+  std::vector<u32> m14_xd2(kReplays, 0);
+  std::vector<int> m14_xdmax(kReplays, 0);
+  std::vector<double> m14_xdmean(kReplays, 0.0);
+  std::vector<u64> m14_hash(kReplays, 0);
+  std::vector<char> m14_have(kReplays, 0);  // 0 none, 1 stashed, 2 complete
+  if (m14_perreplay && xfb_scratch_ok && mask.xfb.bytes > 0) {
+    m14_prist.assign(size_t(kTransformFrom) * size_t(mask.xfb.bytes), 0);
+  }
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
   const std::vector<u8>& pre_stream =
@@ -2460,6 +2481,14 @@
     if (m10_ramref && xfb_scratch_ok) {
       u8* r2p = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
       if (r2p) {
+        // M14 step 2: stash pristine scratch frames for the post-loop diff.
+        if (m14_perreplay && replays < kTransformFrom &&
+            m14_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+          m14_hash[replays] = RamHash(r2p, mask.xfb.bytes);
+          std::memcpy(&m14_prist[size_t(replays) * size_t(mask.xfb.bytes)], r2p,
+                      mask.xfb.bytes);
+          m14_have[replays] = 1;
+        }
         if (replays == kTransformFrom - 1) {
           m10_ref2.assign(r2p, r2p + mask.xfb.bytes);
           m10_ref2_hash = RamHash(r2p, mask.xfb.bytes);
@@ -2482,6 +2511,14 @@
             }
           }
           const double xn2 = x2 ? double(xa2) / double(x2) : 0.0;
+          // M14 step 2: record this delta replay's moved bytes live.
+          if (m14_perreplay) {
+            m14_xd2[replays] = x2;
+            m14_xdmax[replays] = xm2;
+            m14_xdmean[replays] = xn2;
+            m14_hash[replays] = hh;
+            m14_have[replays] = 2;
+          }
           if (x2 > 0) {
             ++m10_gt0;
             if (m10_samp_n < 3) {
@@ -3222,6 +3259,55 @@
                                m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
     }
     Event("m10_ref2", m10f);
+    // M14 step 2: per-replay moved-bytes rows (perreplay-gated). Pristine
+    // replays diff their stashed bytes against the rendered reference here
+    // (the ref did not exist when they ran); delta rows were recorded
+    // live. One m14_win guard line + one m14_ref2 event per replay.
+    if (m14_perreplay) {
+      if (m10_ref2_ok &&
+          m14_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+        for (unsigned r = 0; r < kTransformFrom; ++r) {
+          if (m14_have[r] != 1) continue;
+          const u8* pb = &m14_prist[size_t(r) * size_t(mask.xfb.bytes)];
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
+          m14_xd2[r] = x;
+          m14_xdmax[r] = xm;
+          m14_xdmean[r] = x ? double(xa) / double(x) : 0.0;
+          m14_have[r] = 2;
+        }
+      }
+      char m14w[192];
+      std::snprintf(m14w, sizeof(m14w),
+                    "perreplay=%d ref=%d kref=%u refok=%d refhash=%016llx "
+                    "nreps=%u kfrom=%u",
+                    m14_perreplay, m10_ramref, kTransformFrom - 1,
+                    int(m10_ref2_ok),
+                    static_cast<unsigned long long>(m10_ref2_hash), kReplays,
+                    kTransformFrom);
+      Event("m14_win", m14w);
+      for (unsigned r = 0; r < kReplays; ++r) {
+        char m14f[192];
+        std::snprintf(m14f, sizeof(m14f),
+                      "r=%u phase=%s ok=%d xd2=%u xdmax=%d xdmean=%.3f "
+                      "hash=%016llx refhash=%016llx",
+                      r, r < kTransformFrom ? "pristine" : "delta",
+                      m14_have[r] == 2 ? 1 : 0, m14_xd2[r], m14_xdmax[r],
+                      m14_xdmean[r], static_cast<unsigned long long>(m14_hash[r]),
+                      static_cast<unsigned long long>(m10_ref2_hash));
+        Event("m14_ref2", m14f);
+      }
+    }
     // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
     // only; the M10 receipts above are unchanged). m11_idx carries the
     // per-vertex decode aggregates; m11_nop the armed selectors + spans.
```

### Step 3

```diff
--- local/research/M13/m13_replay_context.h	2026-09-19 16:01:30
+++ local/research/M14/m14_replay_context.h	2026-09-19 20:09:41
@@ -122,8 +122,9 @@
 static u32 fifo_start = 0, fifo_end = 0;
 static double record_wall = 0;
 static constexpr unsigned kReplays = 200;
-static double replay_wall_ms[kReplays] = {};
-static double replay_cpu_ms[kReplays] = {};
+// M14 step 3: replay-indexed timing stores are vectors sized to the runtime
+// sequence length at sequence start (default 200 = M13 behavior).
+static std::vector<double> replay_wall_ms, replay_cpu_ms;
 
 // Thread-CPU time of the calling thread in ms (-1 when unavailable). On the
 // thread that runs the dispatch this is the decode-and-submit CPU of the
@@ -1951,16 +1952,60 @@
     }
   }
   const unsigned kM13DrawCap = 128;
+  // M14 step 3: autoscan (SSX_M14_AUTOSCAN=1, drawscan-wanted only).
+  // Slot-0-scale frames carry 570+ consuming draws: past the M13 128 cap
+  // (fail-closed) and past a 200-replay sequence (each of the C+1 shapes
+  // needs >=1 pristine + >=1 delta replay). Autoscan lifts the cap to the
+  // frame's own consumer count and sizes the sequence to 4*(C+1) replays
+  // (2 pristine + 2 delta per shape), so the whole scan shares ONE
+  // recorded frame. Fail-closed over a 768 MiB ref-bytes budget.
+  // Unset = M13 behavior (cap 128, 200/100).
+  const int m14_autoscan = (m13_want && m10_mode != 0) ? ([] {
+                             const char* v = std::getenv("SSX_M14_AUTOSCAN");
+                             return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                           })()
+                                                       : 0;
+  const unsigned m14_cap =
+      m14_autoscan ? (unsigned)m13_condraw.size() : kM13DrawCap;
+  const unsigned long long m14_refneed =
+      (unsigned long long)(m13_condraw.size() + 1) *
+      (unsigned long long)mask.xfb.bytes;
+  const int m14_overbudget =
+      (m14_autoscan && m14_refneed > 768ull * 1024ull * 1024ull) ? 1 : 0;
   const int m13_scan = (m13_want && !m13_condraw.empty() &&
-                        m13_condraw.size() <= kM13DrawCap)
+                        m13_condraw.size() <= m14_cap && !m14_overbudget)
                            ? 1
                            : 0;
   const unsigned m13_nshapes =
       m13_scan ? 1u + (unsigned)m13_condraw.size() : 0u;
+  // M14 step 3: runtime sequence bounds (defaults = M13 constants). Every
+  // kReplays/kTransformFrom use in the sequence below reads these. Autoscan
+  // runs 2 pristine + 2 delta replays per shape (revs the exact-fit 1+1:
+  // exact-fit forced shape 0's only pristine replay to replay 0, whose
+  // scratch frame carries first-replay EFB state — every shape's reference
+  // is warm here, and n2=2 carries a within-shape uniformity receipt).
+  const unsigned m14_nreps =
+      (m14_autoscan && m13_scan) ? 4u * m13_nshapes : kReplays;
+  const unsigned m14_kfrom =
+      (m14_autoscan && m13_scan) ? 2u * m13_nshapes : kTransformFrom;
   std::vector<std::vector<u8>> m13_exec, m13_pre;
   std::vector<char> m13_ok;
   std::vector<u32> m13_bytes;
-  if (m13_scan) {
+  if (m13_scan && m14_autoscan) {
+    // M14 step 3: validate spans only (the live shape's streams are built
+    // on demand per replay; prebuilding all copies would cost C*2 frames).
+    m13_ok.assign(m13_condraw.size(), 0);
+    m13_bytes.assign(m13_condraw.size(), 0);
+    for (size_t s = 0; s < m13_condraw.size(); ++s) {
+      const M10DrawRec& dr = m10stream.drawrec[m13_condraw[s]];
+      if (dr.size == 0 || dr.off + dr.size > frame_exec.size() ||
+          dr.off + dr.size > frame_pre_exec.size())
+        continue;
+      m13_ok[s] = 1;
+      m13_bytes[s] = dr.size;
+    }
+  }
+  if (m13_scan && !m14_autoscan) {
     m13_exec.resize(m13_condraw.size());
     m13_pre.resize(m13_condraw.size());
     m13_ok.assign(m13_condraw.size(), 0);
@@ -1977,6 +2022,29 @@
       m13_ok[s] = 1;
       m13_bytes[s] = dr.size;
     }
+  }
+  // M14 step 2: per-replay moved-bytes series (SSX_M14_PERREPLAY=1, M10
+  // RAMREF only). The M10 ref2 block keeps tallies + 3 samples; the
+  // camera-delta true delta needs every replay's moved bytes against the
+  // rendered reference (replay kTransformFrom-1's scratch frame). Pristine
+  // replays stash their scratch bytes (diffed post-loop, once the ref
+  // exists); delta replays record live in the M10 block below. Unset =
+  // M13 behavior (no stash, no rows).
+  // M14 step 3: perreplay and autoscan are mutually exclusive (perreplay
+  // storage is sized to the 200/100 constants).
+  const int m14_perreplay = (m10_ramref != 0 && !m14_autoscan) ? ([] {
+                              const char* v = std::getenv("SSX_M14_PERREPLAY");
+                              return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                            })()
+                                            : 0;
+  std::vector<u8> m14_prist;  // kTransformFrom pristine frames, stashed bytes
+  std::vector<u32> m14_xd2(kReplays, 0);
+  std::vector<int> m14_xdmax(kReplays, 0);
+  std::vector<double> m14_xdmean(kReplays, 0.0);
+  std::vector<u64> m14_hash(kReplays, 0);
+  std::vector<char> m14_have(kReplays, 0);  // 0 none, 1 stashed, 2 complete
+  if (m14_perreplay && xfb_scratch_ok && mask.xfb.bytes > 0) {
+    m14_prist.assign(size_t(kTransformFrom) * size_t(mask.xfb.bytes), 0);
   }
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
@@ -2019,7 +2087,8 @@
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
                   "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
                   "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d "
-                  "m12mode=%d m12slot=%d m12alt=%d m13scan=%d m13shapes=%u",
+                  "m12mode=%d m12slot=%d m12alt=%d m13scan=%d m13shapes=%u "
+                  "m14auto=%d m14cap=%u m14reps=%u m14from=%u m14perrep=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -2031,7 +2100,8 @@
                   m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
                   m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
                   m11_notext, m12_mode, m12_slot_self, m12_alt, m13_scan,
-                  m13_nshapes);
+                  m13_nshapes, m14_autoscan, m14_cap, m14_nreps, m14_kfrom,
+                  m14_perreplay);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2210,8 +2280,13 @@
   std::vector<int> m13_samp_xm(m13_nshapes * 3, 0);
   std::vector<double> m13_samp_xn(m13_nshapes * 3, 0.0);
   std::vector<unsigned> m13_samp_n(m13_nshapes, 0);
+  // M14 step 3: size replay-indexed stores to the runtime sequence length.
+  replay_wall_ms.assign(m14_nreps, 0.0);
+  replay_cpu_ms.assign(m14_nreps, 0.0);
+  // M14 step 3: autoscan on-demand shape streams (one live shape per replay).
+  std::vector<u8> m14_tmp_exec, m14_tmp_pre;
   const double seq_start = Now();
-  for (replays = 0; replays < kReplays; ++replays) {
+  for (replays = 0; replays < m14_nreps; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
     // re-arms g_record_fifo_data would corrupt any live capture.
     if (OpcodeDecoder::g_record_fifo_data) {
@@ -2229,11 +2304,12 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
+    if (replays == m14_kfrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     // M10 step 3: arm delta half (M12 step 2: the alt arm splits identically;
-    // M13 step 3: the drawscan arm splits identically too).
-    if (replays == kTransformFrom && (m10_ramref || m12_alt || m13_scan)) {
+    // M13 step 3: the drawscan arm splits identically too; M14 step 3:
+    // runtime split).
+    if (replays == m14_kfrom && (m10_ramref || m12_alt || m13_scan)) {
       s_m8_slot = m10_slot;
       s_m10_cap = 1;
     }
@@ -2266,8 +2342,20 @@
     if (m13_scan) {
       m13_win = replays % m13_nshapes;
       if (m13_win > 0 && m13_ok[m13_win - 1]) {
-        m12_pre = &m13_pre[m13_win - 1];
-        m12_exec = &m13_exec[m13_win - 1];
+        // M14 step 3: autoscan builds the live shape's streams on demand
+        // (byte-identical to the prebuilt copies: same bases, same span).
+        if (m14_autoscan) {
+          const M10DrawRec& m14dr = m10stream.drawrec[m13_condraw[m13_win - 1]];
+          m14_tmp_exec = frame_exec;
+          m14_tmp_pre = frame_pre_exec;
+          std::memset(m14_tmp_exec.data() + m14dr.off, 0x00, m14dr.size);
+          std::memset(m14_tmp_pre.data() + m14dr.off, 0x00, m14dr.size);
+          m12_pre = &m14_tmp_pre;
+          m12_exec = &m14_tmp_exec;
+        } else {
+          m12_pre = &m13_pre[m13_win - 1];
+          m12_exec = &m13_exec[m13_win - 1];
+        }
       }
     }
     if (deterministic) RunPre(*m12_pre);
@@ -2460,14 +2548,22 @@
     if (m10_ramref && xfb_scratch_ok) {
       u8* r2p = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
       if (r2p) {
-        if (replays == kTransformFrom - 1) {
+        // M14 step 2: stash pristine scratch frames for the post-loop diff.
+        if (m14_perreplay && replays < kTransformFrom &&
+            m14_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+          m14_hash[replays] = RamHash(r2p, mask.xfb.bytes);
+          std::memcpy(&m14_prist[size_t(replays) * size_t(mask.xfb.bytes)], r2p,
+                      mask.xfb.bytes);
+          m14_have[replays] = 1;
+        }
+        if (replays == m14_kfrom - 1) {
           m10_ref2.assign(r2p, r2p + mask.xfb.bytes);
           m10_ref2_hash = RamHash(r2p, mask.xfb.bytes);
           m10_ref2_ok = true;
-        } else if (replays >= kTransformFrom && m10_ref2_ok) {
+        } else if (replays >= m14_kfrom && m10_ref2_ok) {
           ++m10_n2;
           const u64 hh = RamHash(r2p, mask.xfb.bytes);
-          if (replays == kTransformFrom) m10_hk_hash = hh;
+          if (replays == m14_kfrom) m10_hk_hash = hh;
           if (hh == m10_hk_hash) ++m10_uniform2;
           unsigned x2 = 0;
           int xm2 = 0;
@@ -2482,6 +2578,14 @@
             }
           }
           const double xn2 = x2 ? double(xa2) / double(x2) : 0.0;
+          // M14 step 2: record this delta replay's moved bytes live.
+          if (m14_perreplay) {
+            m14_xd2[replays] = x2;
+            m14_xdmax[replays] = xm2;
+            m14_xdmean[replays] = xn2;
+            m14_hash[replays] = hh;
+            m14_have[replays] = 2;
+          }
           if (x2 > 0) {
             ++m10_gt0;
             if (m10_samp_n < 3) {
@@ -2515,7 +2619,7 @@
       u8* rwp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
       if (rwp) {
         const int w = int(replays % 4);
-        if (replays < kTransformFrom) {
+        if (replays < m14_kfrom) {
           m12_ref[w].assign(rwp, rwp + mask.xfb.bytes);
           m12_ref_hash[w] = RamHash(rwp, mask.xfb.bytes);
           m12_ref_ok[w] = true;
@@ -2570,7 +2674,7 @@
       u8* rwp13 = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
       if (rwp13) {
         const unsigned w13 = replays % m13_nshapes;
-        if (replays < kTransformFrom) {
+        if (replays < m14_kfrom) {
           m13_ref[w13].assign(rwp13, rwp13 + mask.xfb.bytes);
           m13_ref_hash[w13] = RamHash(rwp13, mask.xfb.bytes);
           m13_ref_ok[w13] = 1;
@@ -2674,7 +2778,7 @@
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
     // M7 step 2: tag actual install state (default mode identical to M6).
-    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0 ||
+    const int xform_flag = int(replays >= m14_kfrom || m7_xform != 0 || m8_mode != 0 ||
                                m9_mode != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
@@ -3211,7 +3315,7 @@
         m10f, sizeof(m10f),
         "ref=%d kref=%u refok=%d n2=%u gt0=%u uniform2=%u xd2min=%u xd2max=%u "
         "xdmax2max=%d xdmean2min=%.3f xdmean2max=%.3f refhash=%016llx samp=",
-        m10_ramref, kTransformFrom, int(m10_ref2_ok), m10_n2, m10_gt0,
+        m10_ramref, m14_kfrom, int(m10_ref2_ok), m10_n2, m10_gt0,
         m10_uniform2, m10_xd2_min, m10_xd2_max, m10_xdmax2_max,
         m10_xdmean2_min, m10_xdmean2_max,
         static_cast<unsigned long long>(m10_ref2_hash));
@@ -3222,6 +3326,55 @@
                                m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
     }
     Event("m10_ref2", m10f);
+    // M14 step 2: per-replay moved-bytes rows (perreplay-gated). Pristine
+    // replays diff their stashed bytes against the rendered reference here
+    // (the ref did not exist when they ran); delta rows were recorded
+    // live. One m14_win guard line + one m14_ref2 event per replay.
+    if (m14_perreplay) {
+      if (m10_ref2_ok &&
+          m14_prist.size() == size_t(kTransformFrom) * size_t(mask.xfb.bytes)) {
+        for (unsigned r = 0; r < kTransformFrom; ++r) {
+          if (m14_have[r] != 1) continue;
+          const u8* pb = &m14_prist[size_t(r) * size_t(mask.xfb.bytes)];
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
+          m14_xd2[r] = x;
+          m14_xdmax[r] = xm;
+          m14_xdmean[r] = x ? double(xa) / double(x) : 0.0;
+          m14_have[r] = 2;
+        }
+      }
+      char m14w[192];
+      std::snprintf(m14w, sizeof(m14w),
+                    "perreplay=%d ref=%d kref=%u refok=%d refhash=%016llx "
+                    "nreps=%u kfrom=%u",
+                    m14_perreplay, m10_ramref, kTransformFrom - 1,
+                    int(m10_ref2_ok),
+                    static_cast<unsigned long long>(m10_ref2_hash), kReplays,
+                    kTransformFrom);
+      Event("m14_win", m14w);
+      for (unsigned r = 0; r < kReplays; ++r) {
+        char m14f[192];
+        std::snprintf(m14f, sizeof(m14f),
+                      "r=%u phase=%s ok=%d xd2=%u xdmax=%d xdmean=%.3f "
+                      "hash=%016llx refhash=%016llx",
+                      r, r < kTransformFrom ? "pristine" : "delta",
+                      m14_have[r] == 2 ? 1 : 0, m14_xd2[r], m14_xdmax[r],
+                      m14_xdmean[r], static_cast<unsigned long long>(m14_hash[r]),
+                      static_cast<unsigned long long>(m10_ref2_hash));
+        Event("m14_ref2", m14f);
+      }
+    }
     // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
     // only; the M10 receipts above are unchanged). m11_idx carries the
     // per-vertex decode aggregates; m11_nop the armed selectors + spans.
@@ -3263,8 +3416,8 @@
       std::snprintf(m12w, sizeof(m12w),
                     "alt=%d slot=%d scheme=mod4 map=0:verbatim,1:nopshr,2:nopidx,3:notext "
                     "kref=%u,%u,%u,%u sel_shr=%d sel_idx=%d sel_text=%d m10nop_ok=%d",
-                    m12_alt, m10_slot, kTransformFrom - 4, kTransformFrom - 3,
-                    kTransformFrom - 2, kTransformFrom - 1, m11_nopshr,
+                    m12_alt, m10_slot, m14_kfrom - 4, m14_kfrom - 3,
+                    m14_kfrom - 2, m14_kfrom - 1, m11_nopshr,
                     m11_nopidx, m11_notext, int(m10_nop_ok));
       Event("m12_win", m12w);
       char m12n[256];
@@ -3284,7 +3437,7 @@
             "win=%d name=%s ref=%d kref=%u refok=%d n2=%u gt0=%u uniform2=%u "
             "xd2min=%u xd2max=%u xdmax2max=%d xdmean2min=%.3f xdmean2max=%.3f "
             "refhash=%016llx samp=",
-            w, m12_names[w], m12_alt, kTransformFrom - 4 + (unsigned)w,
+            w, m12_names[w], m12_alt, m14_kfrom - 4 + (unsigned)w,
             int(m12_ref_ok[w]), m12_n2[w], m12_gt0[w], m12_uniform2[w],
             m12_xd2_min[w], m12_xd2_max[w], m12_xdmax2_max[w],
             m12_xdmean2_min[w], m12_xdmean2_max[w],
@@ -3308,15 +3461,19 @@
                     "scan=%d slot=%d scheme=modN nshapes=%u ndraws=%u cap=%u "
                     "sel_shr=%d sel_idx=%d sel_text=%d m10nop_ok=%d",
                     m13_scan, m10_slot, m13_nshapes,
-                    (unsigned)m13_condraw.size(), kM13DrawCap, m11_nopshr,
+                    (unsigned)m13_condraw.size(), m14_cap, m11_nopshr,
                     m11_nopidx, m11_notext, int(m10_nop_ok));
       Event("m13_win", m13w);
       for (size_t s = 0; s < m13_condraw.size(); ++s) {
+        // M14 step 3: fail-closed rows carry ok=0 (want && !scan left these
+        // vectors empty — indexing them was out-of-bounds).
+        const int m14ok = (s < m13_ok.size() && m13_ok[s]) ? 1 : 0;
+        const u32 m14nb = (s < m13_bytes.size()) ? m13_bytes[s] : 0u;
         char m13n[160];
         std::snprintf(m13n, sizeof(m13n),
                       "shape=%u clk=%u ok=%d draws=%u bytes=%u",
-                      1u + (unsigned)s, m13_condraw[s] + 1, int(m13_ok[s]),
-                      m13_ok[s] ? 1u : 0u, m13_bytes[s]);
+                      1u + (unsigned)s, m13_condraw[s] + 1, m14ok,
+                      m14ok ? 1u : 0u, m14nb);
         Event("m13_nop", m13n);
       }
       for (unsigned w = 0; w < m13_nshapes; ++w) {
@@ -3378,13 +3535,13 @@
        live_same_count == replays)
           ? 1
           : 0;
-  char done_detail[288]; // whole-200 wall time + M5 XFB counts on the done event.
+  char done_detail[288]; // whole-sequence wall time + M5 XFB counts on the done event.
   std::snprintf(done_detail, sizeof(done_detail),
-                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u "
-                "xfb_equal_scratch=%u/200 live_xfb_untouched=%d live_same=%u/%u",
-                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, mask.xfb.addr,
-                mask.xfb.bytes, xfb_scratch_count, live_xfb_untouched, live_same_count,
-                replays);
+                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/%u xfb_addr=0x%08x xfb_bytes=%u "
+                "xfb_equal_scratch=%u/%u live_xfb_untouched=%d live_same=%u/%u",
+                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, m14_nreps,
+                mask.xfb.addr, mask.xfb.bytes, xfb_scratch_count, m14_nreps,
+                live_xfb_untouched, live_same_count, replays);
   Event(window_ok ? "done" : "watched_window_changed", done_detail);
   // M5 step 5: arm the first-live-XFB-after-resume capture. The existing
   // watched-window re-hash + done above remain the receipt.
```
