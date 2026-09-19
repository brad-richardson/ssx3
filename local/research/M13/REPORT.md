# M13 — Slot-36 same-frame partition + per-draw depth attempt: REPORT

Slot-36 same-frame partition via the M12 alternating-NOP machinery, plus
a per-consuming-draw leave-one-out scan (draw-clock refinement to
per-draw granularity) as the per-draw depth attempt. Desktop only.
Runbook `local/muse/prompts/M13.md`. No `adb`, no device. Tables, no
verdicts.

Header read first: `local/research/M12/REPORT.md` (all of it: the slot-0
same-frame partition, "What I could not do" items 1 — per-draw depth —
and 3 — alternating-NOP ran slot 0 only — which this brief takes in
reverse order) and the base header
`local/research/M12/m12_replay_context.h`.

Time box 6 hours; used about 2. Two lease waits (P1u held the lease
for ~10 minutes before the det4 run; logged in
`local/research/M13/waits.log`; never forced).

## Baseline note (read before the tables)

The M12 header on disk (`local/research/M12/m12_replay_context.h`, clean
tree) hashes to
`14f7c7f7f58a65d10e91363ae172c4096a4311782d224498d03a5f0dd55e9434`
via `shasum -a 256` (trust `shasum`, not memory; matches the M12 report's
pinned prefix).
Step 1 copied the on-disk file verbatim to
`local/research/M13/m13_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8/M9/M10/M11/M12 mechanism is kept
in all steps: PE mask, verbatim execute stream, restore, stall, pipe
snapshot, watched-window re-hash, `done`, XFB hash + scratch redirect,
side-effect counters, continuation capture, scoped bus, `m6frame`,
presenter tracing, record guard, trig_imx probe, M7 full/delta transforms,
per-replay xdiff stats, M8 census/slot/proj modes with stream-epoch
census, M9 VAT walk + slot/survival, M10 order/matrix/epoch/occ walks +
NOP/RAM/ref2 arms, M11 slot chain + idx decode + NOPSHR/NOPIDX/NOPTEXT
arms, M12 slot chain + RAMREF alias + alternating-NOP windows. All M13
additions are env-gated with defaults that preserve M12 behavior
(`SSX_M13_DRAWSCAN` unset); the committed header is the step-3 header
(step 1 and step 2 need no new header; §Header diffs), from which the
step-1 and step-2 runs are reproducible via env.

M13 mode (`SSX_M13_DRAWSCAN=1` in M12 mode, i.e. with `SSX_M12_SLOT=N`;
requires `SSX_M12_ALT` unset): per-consuming-draw leave-one-out scan —
shape 0 is the verbatim total, shapes 1..C each NOP one slot-consuming
draw (drawrec cons bit), cycling `replays % (C+1)` with one pristine
reference per shape at that shape's last pristine replay. Fail-closed per
shape (`ok=0` leaves that shape verbatim) and fail-closed for the arm (no
consuming draws, or more than the 128 cap, leaves the arm off). The
drawscan arm implies RAMCOPY and the same 100-split with the same
pre-loop pristine gating as the M12 alt arm (delta arms at replay 100).

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M12. `m13-det*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M13\n'`, removed after each run);
the log is `local/research/M13/waits.log` (2 waits, four claim/release
pairs, two annotations, never forced). Builds ran any time; no build ran
during a run.
`complete_hazard_resets` (harness field, as observed): all arms 0;
every sequence is 200/200 with `done` and clean counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `14f7c7f7…` (= M12 on disk) | `players/m13-baseline` | `m13-det-run` (`m13-det`, `SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1`) | `m13-det-probe.jsonl` |
| 2 slot36-alt | `14f7c7f7…` (= step 1) | `players/m13-baseline` (same player, env-only change) | `m13-det2-run` (`m13-det2`, `SSX_M12_SLOT=36 SSX_M12_ALT=1 SSX_M9_SURV=1`) | `m13-det2-probe.jsonl` |
| 3 drawscan | `839cb759…` (pre-fix) | `players/m13-drawscan` | `m13-det3-run-failed` (`m13-det3`, `SSX_M12_SLOT=36 SSX_M13_DRAWSCAN=1 SSX_M9_SURV=1`) | `m13-det3-probe.jsonl-failed` |
| 3 drawscan re-run | `b09643b1…` | `players/m13-drawscan2` | `m13-det4-run` (`m13-det4`, same env) | `m13-det4-probe.jsonl` |

The committed header is `b09643b1…`. Steps 1–2 need no new header code
(step 2 runs the M12 alt machinery on slot 36 via env only;
step2-vs-step1 and step1-vs-M12 `diff -u` are both empty), so those arms
are reproducible from the committed header via env. The `m13-det3`
attempt is kept as `-failed`: its sequence is a complete 200/200 `done`
but the pre-fix header armed the slot delta on replays 0–199 (missing
pre-loop pristine gate), so every shape's xd2 reads 0; it is
reproducible only from the pre-fix header snapshot on the SSD (see
§Player and run dir paths), and its rows are tabulated as the attempt
log in §Step 3, marked `-failed`. The `m13-det3` attempt also exited -5
post-sequence on live resume (missing `resume_xfb` only; same signature
as M12's `m12-det3`).

Player dirs live under `local/research/M13/players/` (the build driver
requires outputs under `local/`; they are gitignored build outputs, never
committed). Run dirs and every probe jsonl live under
`/Volumes/Extreme SSD/m13/` (symlink-free; `realpath` is the path as
written). Probes, runs and players are not committed.

## Step 1 — baseline (M12 slot-0 alternating end state as control)

Unmodified copy, M12 slot-0 alternating env. `analyze.py` prints 200 rows +
`done` + `xfb_equal_scratch=0/200` (forced-RAM signature, as M12 det) +
`live_xfb_untouched=1` + `dafter_live`/`dframe`/`dpres`/`dimx` all 0/0 +
`pediff`/`vidiff` 0/0. Control for steps 2–3.

This run recorded a new frame (299569 B / 2286 updates, draws=1203,
verts=27334, covering=100, cons=570), so the byte counts below are that
frame's, next to M12's `m12-det2` frame (531035 B, total 70584, shares
68012/37207/36479) for shape comparison only.

Seam-application receipt (`xform_stats`, slot mode):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 259000 |
| `hits` | 10000 (= 100 × 100 covering loads; first half counting-only) |
| `regcalls` | 0 |

Guard receipt (`m12_win`): `alt=1 slot=0 scheme=mod4
map=0:verbatim,1:nopshr,2:nopidx,3:notext kref=96,97,98,99 sel_shr=0
sel_idx=0 sel_text=0 m10nop_ok=0`. NOP-span receipts (`m12_nop`):
`shr_ok=1 shr_draws=570 shr_bytes=134205 idx_ok=1 idx_draws=72
idx_bytes=81224 text_ok=1 text_draws=38 text_bytes=12610`. The single
`m10_ref2` is off by design (`ref=0 n2=0`).

Per-window ref2 rows (SAME recorded frame; per-window pristine refs):

| win | name | kref | refhash | n2 | gt0 | uniform2 | xd2min/xd2max | xdmax2max | xdmean2 |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | verbatim (total) | 96 | `018d36204d3dd538` | 25 | 25 | 25 | 40688 / 40688 | 106 | 2.177 |
| 1 | nopshr (indexed-only) | 97 | `99828b89d72957ac` | 25 | 25 | 25 | 394 / 394 | 78 | 5.627 |
| 2 | nopidx (shared-only) | 98 | `9710e76d6afb8dc5` | 25 | 25 | 25 | 39317 / 39317 | 106 | 2.168 |
| 3 | notext (non-texture-mediated) | 99 | `86352522db243b0a` | 25 | 25 | 25 | 39838 / 39838 | 106 | 2.165 |

Samples: w0 `r100:40688/106/2.177,r104:40688/106/2.177,r108:40688/106/2.177`;
w1 `r101:394/78/5.627,r105:394/78/5.627,r109:394/78/5.627`;
w2 `r102:39317/106/2.168,r106:39317/106/2.168,r110:39317/106/2.168`;
w3 `r103:39838/106/2.165,r107:39838/106/2.165,r111:39838/106/2.165`.

Subtracted shares (total win0 40688 minus surviving window, same frame):

| removed set | surviving win | surviving xd2 | removed share (total − surviving) |
| --- | ---: | ---: | ---: |
| shared-path (nopshr) | 1 | 394 | 40294 |
| indexed-path (nopidx) | 2 | 39317 | 1371 |
| texture-epoch (notext) | 3 | 39838 | 850 |

Partition cross-checks (table):

| Check | Value |
| --- | --- |
| `shr_draws` vs `cons_any` | 570 = 570 |
| `idx_draws` vs `exp_draws` | 72 = 72 |
| `text_draws` vs draws 1..38 (4 texture epochs) | 38 = 38 |
| `idx_pos_draws` vs M9 `pos_indexed` | 74 = 74 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 56 = 56 |
| seam hits vs 100 × covering loads | 10000 = 100×100 |

Own-frame M9 census, m13-det (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1129 | 74 | n/a | n/a |
| Tex0 | 1203 | 0 | 1163 | 1163 |
| Tex1 | 1147 | 56 | 387 | 331 |
| Tex2 | 1203 | 0 | 14 | 14 |
| Tex3-7 | 1203 | 0 | 0 | 0 |

Shared-pos reach total 1129 (`0:570 3:79 6:79 9:85 12:39 15:59
18:57 21:76 24:36 27:49`); tex2 shared+enabled reach `36:14`.
Decode row (slot 0): `idx_pos_draws=74 idx_pos_verts=11505 exp_draws=72
exp_verts=4161`, `tex_draws=0,56,0,0,0,0,0,0`, `tex_exp_draws` all zero.
Order row: covering=100 (`arr12=100`), cons_pos=570, cons_tex=0,
cons_any=570; first_cons=1 last_cons=1203; seam 10000 = 100×100.
Matrix: +0.1 on word 3 only, `mm_live=100 mm_snap=125`.
Survival trichotomy: live 100/100, per-vertex 75/0/25, shared-pos
75/0/25 (resident 100/100), shared-tex 0 (resident 0/100);
`dirty_post=25`, `zfreeze=0`; first-hit 0 → 0.1.
EFB copies n=5 (4 texture + XFB drain at draw 1203);
`epoch_cons=9,9,1,1,550,0`; occ: cons=570, culled=0, out-of-range=20,
in-range=550; `all_cull=all_scis=all_znever=0`.

Recorded without verdict: the M12 alternating machinery reproduces on a
new frame (four 25/25 uniform windows against their own shape's pristine
reference, guest/event clean); the shares above subtract against this
frame's total (40688) — the byte counts are frame-dependent (M12's
frame: total 70584, shares 68012/37207/36479).

## Per-step wall table (final arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m13-det | 200 | 4.167 / 7.221 / 3.360 / 17.851 | 1.613 / 1.998 | 299569 / 2286 | YES | seq_wall_ms=1468.413 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m13-det2 | 200 | 5.984 / 10.448 / 5.175 / 13.861 | 2.216 / 2.686 | 359121 / 2952 | YES | seq_wall_ms=1885.409 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m13-det4 | 200 | 7.219 / 11.495 / 6.725 / 263.852 | 2.827 / 2.959 | 364048 / 2966 | YES | seq_wall_ms=2486.204 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
```

Failed-arm wall row (sequence-complete 200/200 `done`; pre-fix header
armed the delta on all 200 replays, so every shape's xd2 reads 0; native
exit -5 post-sequence, missing `resume_xfb` only; rc=1):
`m13-det3-failed`: 200 replays, wall 29.543 / 71.584 / 13.634 / 124.181,
Thread-CPU 12.535 / 19.046, frame 665820 / 6010, `done`, `seq_wall_ms=
8616.595 completed=200 xfb_equal=200/200 ... xfb_equal_scratch=0/200
live_xfb_untouched=1 live_same=200/200`.

Frames differ per run (299569 … 665820 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table). All
rows: 200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2
dls=0 walk=100% unknown=0 benign=1` in all runs.
`xfb_equal_scratch=0/200` on all rows is the forced-RAM signature
(rendered scratch vs fuchsia live ref), not a failure.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m13-det | 0.107 | 0.001 | 0.043 | 4.025 | 0.000 | 7.035 |
| m13-det2 | 0.146 | 0.001 | 0.038 | 5.802 | 0.000 | 10.210 |
| m13-det4 | 0.207 | 0.002 | 0.045 | 6.964 | 0.001 | 11.231 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m13-det | 1295 | 62160 | 33.7 |
| m13-det2 | 1966 | 94368 | 22.2 |
| m13-det4 | 2005 | 96240 | 21.8 |

(`m13-det3-failed`: 5961 / 286128 / 7.3.)

## Step 2 — slot-36 alternating partition (M12 gap 3 follow-up)

One run (`SSX_M12_SLOT=36 SSX_M12_ALT=1`), one recorded frame (359121 B /
2952 updates, draws=1551, verts=34028, covering=120, cons=28 all tex),
four interleaved windows with one pristine reference each. Guard receipt
(`m12_win`): `alt=1 slot=36 scheme=mod4
map=0:verbatim,1:nopshr,2:nopidx,3:notext kref=96,97,98,99 sel_shr=0
sel_idx=0 sel_text=0 m10nop_ok=0` — no M11 selector armed, so window 0 is
the verbatim total. NOP-span receipts (`m12_nop`): `shr_ok=1 shr_draws=28
shr_bytes=1234 idx_ok=0 idx_draws=0 idx_bytes=0 text_ok=1 text_draws=54
text_bytes=18926` — the indexed-position shape is fail-closed verbatim
(no indexed-position draw is exposed to slot 36 on this frame; see
`exp_draws=0` below). The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Per-window ref2 rows (SAME recorded frame; per-window pristine refs):

| win | name | kref | refhash | n2 | gt0 | uniform2 | xd2min/xd2max | xdmax2max | xdmean2 |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | verbatim (total) | 96 | `999cdb6660c0b88c` | 25 | 25 | 25 | 3001 / 3001 | 90 | 5.360 |
| 1 | nopshr (indexed-only) | 97 | `c772b6f6699c3bac` | 25 | 25 | 25 | 890 / 890 | 10 | 1.457 |
| 2 | nopidx (shared-only) | 98 | `999cdb6660c0b88c` | 25 | 25 | 25 | 3001 / 3001 | 90 | 5.360 |
| 3 | notext (non-texture-mediated) | 99 | `9923abd221a4cf70` | 25 | 25 | 24 | 1553 / 1561 | 10 | 1.376/1.378 |

Samples: w0 `r100:3001/90/5.360,r104:3001/90/5.360,r108:3001/90/5.360`;
w1 `r101:890/10/1.457,r105:890/10/1.457,r109:890/10/1.457`;
w2 `r102:3001/90/5.360,r106:3001/90/5.360,r110:3001/90/5.360`;
w3 `r103:1553/10/1.378,r107:1553/10/1.378,r111:1553/10/1.378`.

Window 2's refhash equals window 0's (`999cdb6660c0b88c`), tabulating
the fail-closed verbatim shape; window 3 reads 24/25 uniform (one delta
replay at 1561 B vs 1553 B on the other 24).

Subtracted shares (total win0 3001 minus surviving window, same frame):

| removed set | surviving win | surviving xd2 | removed share (total − surviving) |
| --- | ---: | ---: | ---: |
| shared-path (nopshr) | 1 | 890 | 2111 |
| indexed-path (nopidx) | 2 | 3001 | 0 |
| texture-epoch (notext) | 3 | 1561 | 1440 |

Partition cross-checks (table):

| Check | Value |
| --- | --- |
| `shr_draws` vs `cons_any` | 28 = 28 |
| `idx_draws` vs `exp_draws` | 0 = 0 |
| `text_draws` vs draws 1..54 (6 texture epochs) | 54 = 54 |
| `idx_pos_draws` vs M9 `pos_indexed` | 115 = 115 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 91 = 91 |
| `tex_draws[2]` vs M9 `tex_indexed[2]` | 0 = 0 |
| seam hits vs 100 × covering loads | 12000 = 100×120 |
| shared Tex2 reach 36 vs `cons_tex` | 28 = 28 |

Tex2-path partition shape vs slot 0's (tabled, no verdict):

| Shape row | slot 0 (M12 det2) | slot 0 (M13 det control) | slot 36 (M13 det2) |
| --- | ---: | ---: | ---: |
| frame draws / cons draws | 1863 / 609 | 1203 / 570 | 1551 / 28 |
| verbatim total xd2 (B) | 70584 | 40688 | 3001 |
| shared-path removed share | 68012 | 40294 | 2111 |
| indexed-path removed share | 37207 | 1371 | 0 |
| texture-epoch removed share | 36479 | 850 | 1440 |
| `idx_ok` (indexed-pos shape live) | 1 | 1 | 0 |
| win2 refhash vs win0 refhash | differ | differ | equal |
| win3 uniform2 / n2 | 25 / 25 | 25 / 25 | 24 / 25 |
| `tex_exp_draws[1]` (indexed-Tex1 exposure of slot) | 0 | 0 | 77 |

EFB-copy table, m13-det2 (compared xfb=`0x004dc660`/573440; `n=7`):

| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |
| ---: | --- | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |
| 0 | 9 | 0x00701560 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 1 | 18 | 0x00702580 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 2 | 27 | 0x007035a0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 3 | 35 | 0x0110c440 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 4 | 44 | 0x013fe160 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 5 | 54 | 0x014c6ce0 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 6 | 1551 | 0x004dc660 | 573440 | 1 | 1 | 0x000000 | 640 | 448 | 1 |

Epoch table, m13-det2 (draws=1551; epoch_cons=`0,0,0,0,0,0,28,0`):

| epoch | draw range | cons draws | closing copy |
| ---: | --- | ---: | --- |
| 0–5 | 1..54 | 0 each | copies 0–5 (texture) |
| 6 | 55..1551 | 28 | copy 6 (XFB drain) |
| 7 | 1552..1551 | 0 | tail (none) |

Per-class context: cons=28, culled=0, out-of-range=0, in-range=28;
`all_cull=all_scis=all_znever=0`.

Own-frame M9 census, m13-det2 (VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1436 | 115 | n/a | n/a |
| Tex0 | 1551 | 0 | 1495 | 1495 |
| Tex1 | 1460 | 91 | 525 | 434 |
| Tex2 | 1551 | 0 | 28 | 28 |
| Tex3-4 | 1551 | 0 | 7 | 7 |
| Tex5-7 | 1551 | 0 | 0 | 0 |

Shared-pos reach total 1436 (`0:816 3:77 6:70 9:103 12:42 15:79
18:50 21:58 24:54 27:87`); tex2 shared+enabled reach `36:28`.
Decode row (slot 36): `idx_pos_draws=115 idx_pos_verts=17767
exp_draws=0 exp_verts=0`, `tex_draws=0,91,0,0,0,0,0,0`,
`tex_exp_draws=0,77,0,0,0,0,0,0`.
Order row: covering=120 (`arr14=120`), cons_pos=0, cons_tex=28,
cons_any=28; first_cons=407 last_cons=520; seam 12000 = 100×120.
Matrix: +0.1 on word 147 only, `mm_live=100 mm_snap=100`,
`snap_which=2 snap_ti=2`.
Survival: live/per-vertex/shared-tex all 0/0/100 (`other`),
`pos_res=0 tex_res=100`, `dirty_post=0`; first-hit -15.8044 →
-15.7044 (+0.1).

Recorded without verdict: the slot-36 frame partitions into
2111/0/1440 removed shares against its own 3001 B total on the one
shared frame; the indexed-position shape is verbatim-identical to the
total (fail-closed, `idx_ok=0`, equal refhashes), and the texture-epoch
shape reads 24/25 uniform.

## Step 3 — per-draw depth attempt (draw-clock refinement to per-draw granularity)

One header-only instrument, attempted inside the 2h sub-box: draw-clock
refinement of the M12 partition below window granularity, taken to the
per-draw limit as a per-consuming-draw leave-one-out scan
(`SSX_M13_DRAWSCAN=1`; §Header diffs, step 3). Option survey (tabled, no
verdict):

| Candidate | Standing | Note |
| --- | --- | --- |
| draw-clock refinement below window granularity | attempted (works: per-draw table below) | per-consuming-draw leave-one-out; M12-proven NOP + ref2 machinery generalized 4 → N shapes |
| per-draw EFB readback orchestration | not attempted in-box | `FramebufferManager::PeekEFBDepth` exists vendor-side (`VideoCommon/FramebufferManager.h:119`, via `g_framebuffer_manager`), but per-draw prefixes re-execute from byte 0 with no header-side EFB reset between prefixes, so prefix scans would double-render; needs its own reset receipt |
| depth-buffer sampling at window boundaries | not attempted in-box | same EFB API; yields per-window samples, not the per-draw receipt — the leave-one-out scan carries the occlusion signal per draw instead |

One run (`SSX_M12_SLOT=36 SSX_M13_DRAWSCAN=1`), one recorded frame
(364048 B / 2966 updates, draws=1490, verts=34144, covering=122,
cons=30 all tex), 31 interleaved shapes with one pristine reference
each. Guard receipt (`m13_win`): `scan=1 slot=36 scheme=modN nshapes=31
ndraws=30 cap=128 sel_shr=0 sel_idx=0 sel_text=0 m10nop_ok=0` — no M11
selector armed, so shape 0 is the verbatim total. All 30 per-draw NOP
spans ok=1 (draws 1, bytes 39/45/51 per draw clock; clocks 408–416,
422–437, 498–502). The single `m10_ref2` is off by design
(`ref=0 n2=0`).

Per-draw leave-one-out ref2 rows (SAME recorded frame; per-shape
pristine refs; `n2`/`gt0`/`uniform2` read `n2`/`n2`/`n2` on all 31
shapes — 4/4/4 on shapes 7–13, 3/3/3 elsewhere):

| shape | clk | kref | refhash | xd2min/xd2max | xdmax2max | xdmean2 |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 0 (verbatim total) | 93 | `f21c30fede69d0a6` | 2401 / 2401 | 96 | 13.975 |
| 1 | 408 | 94 | `8d1ffbaef720e431` | 2401 / 2401 | 96 | 13.975 |
| 2 | 409 | 95 | `2b72bb847eb34d3b` | 2401 / 2401 | 96 | 13.975 |
| 3 | 410 | 96 | `b9646772e3386819` | 2401 / 2401 | 96 | 13.975 |
| 4 | 411 | 97 | `84936818dfbe6e2b` | 2401 / 2401 | 96 | 13.975 |
| 5 | 412 | 98 | `52a9a503bf52b26b` | 2401 / 2401 | 96 | 13.975 |
| 6 | 413 | 99 | `1da47b8fdf321745` | 2401 / 2401 | 96 | 13.975 |
| 7 | 414 | 69 | `77241be47f2beb3f` | 2401 / 2401 | 96 | 13.975 |
| 8 | 415 | 70 | `2018b0352c28f797` | 2400 / 2400 | 96 | 13.980 |
| 9 | 416 | 71 | `b2d612af53f4891d` | 2402 / 2402 | 96 | 13.969 |
| 10 | 422 | 72 | `f21c30fede69d0a6` | 2401 / 2401 | 96 | 13.975 |
| 11 | 423 | 73 | `f21c30fede69d0a6` | 2401 / 2401 | 96 | 13.975 |
| 12 | 424 | 74 | `f21c30fede69d0a6` | 2401 / 2401 | 96 | 13.975 |
| 13 | 425 | 75 | `923343f9c255e1cb` | 2401 / 2401 | 96 | 13.975 |
| 14 | 426 | 76 | `9724c6be5ac8a42c` | 2401 / 2401 | 96 | 13.975 |
| 15 | 427 | 77 | `95c551c9db0d75b7` | 1517 / 1517 | 94 | 3.457 |
| 16 | 428 | 78 | `1b18274569fe8c51` | 2401 / 2401 | 96 | 13.975 |
| 17 | 429 | 79 | `0025271f3849f4d2` | 2401 / 2401 | 96 | 13.975 |
| 18 | 430 | 80 | `93589d58dd8ab13f` | 2401 / 2401 | 96 | 13.975 |
| 19 | 431 | 81 | `3333891a759fe85e` | 2400 / 2400 | 96 | 13.980 |
| 20 | 432 | 82 | `d8bd2beb0a62ce4b` | 2407 / 2407 | 96 | 13.942 |
| 21 | 433 | 83 | `429cb3b29ef9f1e4` | 2404 / 2404 | 96 | 13.958 |
| 22 | 434 | 84 | `b3ba27928c686a11` | 2289 / 2289 | 96 | 13.207 |
| 23 | 435 | 85 | `72a1ad57923914fe` | 2401 / 2401 | 96 | 13.975 |
| 24 | 436 | 86 | `0fda657946fe6f37` | 2400 / 2400 | 96 | 13.980 |
| 25 | 437 | 87 | `7e174c8af63b6489` | 2401 / 2401 | 96 | 13.975 |
| 26 | 498 | 88 | `a9e24db3355fb661` | 2370 / 2370 | 96 | 14.144 |
| 27 | 499 | 89 | `01d48e74212abfb5` | 2199 / 2199 | 96 | 15.161 |
| 28 | 500 | 90 | `61dbf484ef3cce50` | 2189 / 2189 | 96 | 15.225 |
| 29 | 501 | 91 | `6bfb85a8175caf8c` | 2180 / 2180 | 96 | 15.273 |
| 30 | 502 | 92 | `7250c57eb5d40e96` | 2294 / 2294 | 96 | 14.580 |

Samples: shape 0 `r124:2401/96/13.975,r155:2401/96/13.975,r186:2401/96/13.975`;
shape 15 `r108:1517/94/3.457,r139:1517/94/3.457,r170:1517/94/3.457`;
shape 29 `r122:2180/96/15.273,r153:2180/96/15.273,r184:2180/96/15.273`
(full per-shape samples in `analyze-det4.txt`). Each shape's sample
replays are 31 apart (mod-31 cycling). Shapes 10/11/12 refhashes equal
shape 0's (`f21c30fede69d0a6`): removing draw 422/423/424 leaves that
shape's pristine XFB byte-identical to the verbatim pristine frame.

Per-draw removed shares (total shape0 2401 minus surviving shape,
same frame):

| left-out draw clk | surviving shape | surviving xd2 | removed share (total − surviving) |
| ---: | ---: | ---: | ---: |
| 408 | 1 | 2401 | 0 |
| 409 | 2 | 2401 | 0 |
| 410 | 3 | 2401 | 0 |
| 411 | 4 | 2401 | 0 |
| 412 | 5 | 2401 | 0 |
| 413 | 6 | 2401 | 0 |
| 414 | 7 | 2401 | 0 |
| 415 | 8 | 2400 | 1 |
| 416 | 9 | 2402 | -1 |
| 422 | 10 | 2401 | 0 |
| 423 | 11 | 2401 | 0 |
| 424 | 12 | 2401 | 0 |
| 425 | 13 | 2401 | 0 |
| 426 | 14 | 2401 | 0 |
| 427 | 15 | 1517 | 884 |
| 428 | 16 | 2401 | 0 |
| 429 | 17 | 2401 | 0 |
| 430 | 18 | 2401 | 0 |
| 431 | 19 | 2400 | 1 |
| 432 | 20 | 2407 | -6 |
| 433 | 21 | 2404 | -3 |
| 434 | 22 | 2289 | 112 |
| 435 | 23 | 2401 | 0 |
| 436 | 24 | 2400 | 1 |
| 437 | 25 | 2401 | 0 |
| 498 | 26 | 2370 | 31 |
| 499 | 27 | 2199 | 202 |
| 500 | 28 | 2189 | 212 |
| 501 | 29 | 2180 | 221 |
| 502 | 30 | 2294 | 107 |

Observed arithmetic (tabulated, no verdict): positive shares sum to
1769 (884+112+31+202+212+221+107) vs total 2401; three shapes read
negative (-1/-6/-3: removing the draw widens the delta by 1/6/3 B);
eighteen shapes read exactly 0.

Scan cross-checks (table):

| Check | Value |
| --- | --- |
| `ndraws` vs `cons_any` | 30 = 30 |
| per-draw spans ok | 30 / 30 |
| `n2` pattern (mod-31 split) | 4 on shapes 7–13, 3 elsewhere |
| `kref` = last pristine replay of shape | 93–99 shapes 0–6, 69–75 shapes 7–13, 76–92 shapes 14–30 |
| seam hits vs 100 × covering loads | 12200 = 100×122 |
| shared Tex2 reach 36 vs `cons_tex` | 30 = 30 |
| `tex_exp_draws[1]` (indexed-Tex1 exposure of slot 36) | 78 |
| `exp_draws` (indexed-position exposure of slot 36) | 0 |

Own-frame context, m13-det4: VAT Pos 1376/114; Tex0 1490/0/1435/1435;
Tex1 1399/91/521/430; Tex2 1490/0/30/30; Tex3 16/16; Tex4 9/9; rest 0
enabled. Shared-pos reach total 1376 (`0:735 3:115 6:72 9:68 12:52
15:63 18:44 21:74 24:54 27:99`). Order: covering=122 (`arr14=122`),
cons_pos=0, cons_tex=30; first_cons=408 last_cons=502. Matrix: +0.1 on
word 147 only, `mm_live=100 mm_snap=100`, `snap_which=2 snap_ti=2`.
Survival: live/per-vertex/shared-tex 0/0/100 (`other`), `pos_res=0
tex_res=100`, `dirty_post=0`; first-hit -9.99886 → -9.89886 (+0.1).
EFB copies n=7 (6 texture + XFB drain at draw 1490);
`epoch_cons=0,0,0,0,0,0,30,0`; occ: cons=30, culled=0, out-of-range=0,
in-range=30.

Attempt log (`m13-det3-failed`, pre-fix header `839cb759…`, same env, new
frame 665820 B / 6010 updates, draws=3235, covering=316, cons=27):
sequence-complete 200/200 `done` with `scan=1 nshapes=28 ndraws=27`,
but the pre-fix header missed the pre-loop pristine gate, so the slot
delta armed on replays 0–199 (seam 63200 = 200×316; matrix
`mm_live=0 mm_snap=0`) and every shape's xd2 reads 0 including shape 0.
Fix: `!m13_scan` added to the two pre-loop gates (`s_m8_slot`,
`s_m10_cap`; §Header diffs, step 3), rebuilt, re-ran as `m13-det4`.
The failed attempt also exited -5 post-sequence (missing `resume_xfb`
only; same signature as M12's `m12-det3`).

Recorded without verdict: the drawscan arm attributes the slot-36
2401 B total to individual consuming draws on the one shared frame —
one draw carries 884 B, five carry 31–221 B each, one carries 112 B,
three read negative (-1/-6/-3), eighteen read exactly 0 — with every
shape uniform (all delta replays identical within shape).

## Mechanism table (M12 gaps this brief works through)

| M12 gap | Standing | Receipt |
| --- | --- | --- |
| 3-follow-up (slot-36 same-frame partition) | measured | §Step 2: 25/25 windows on one frame; removed shares 2111/0/1440; `idx_ok=0` fail-closed verbatim |
| 1 (per-draw depth) | measured (consuming-draw leave-one-out) | §Step 3: 31-shape scan on one frame; per-draw shares 884 max, 18 zeros, 3 negatives; EFB-readback orchestration and window-boundary depth sampling not attempted in-box |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m13-det | `fc=6513` | `replay_disabled=0 fc=6516 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m13-det2 | `fc=6506` | `replay_disabled=0 fc=6509 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m13-det4 | `fc=6100` | `replay_disabled=0 fc=6103 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m13-det3-failed | `fc=5484` | (missing: native exit -5 post-sequence; sequence itself 200/200 `done`) |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the triple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M12/M11/M10/M9/M8/M7 sequence hashes
and all M6 sequence and M5 sequence/disabled hashes) is tabulated as
observed. `resume fc − fc0 = 3` in each final run (the live record window;
per-replay `dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m13-det | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m13-det2 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m13-det4 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m13-det3-failed | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | (missing; see above) |

Scratch `0/200` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M12/build_replay_player.py`; `m13-baseline` was built
from the step-1 header — the driver compiles
`local/research/M13/m13_replay_context.h`):

```
python3 local/research/M13/build_replay_player.py local/research/M13/players/m13-baseline
python3 local/research/M13/build_replay_player.py local/research/M13/players/m13-drawscan
python3 local/research/M13/build_replay_player.py local/research/M13/players/m13-drawscan2
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M13\n'`,
remove after each run; profiles fresh per run):

```
SSX_M12_SLOT=0 SSX_M12_ALT=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m13/m13-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M13/players/m13-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m13-det --cpu-thread --output "/Volumes/Extreme SSD/m13/m13-det-run" --seconds 240
SSX_M12_SLOT=36 SSX_M12_ALT=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m13/m13-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M13/players/m13-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m13-det2 --cpu-thread --output "/Volumes/Extreme SSD/m13/m13-det2-run" --seconds 240
SSX_M12_SLOT=36 SSX_M13_DRAWSCAN=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m13/m13-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M13/players/m13-drawscan --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m13-det3 --cpu-thread --output "/Volumes/Extreme SSD/m13/m13-det3-run" --seconds 240
SSX_M12_SLOT=36 SSX_M13_DRAWSCAN=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m13/m13-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M13/players/m13-drawscan2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m13-det4 --cpu-thread --output "/Volumes/Extreme SSD/m13/m13-det4-run" --seconds 240
```

Analysis:

```
python3 local/research/M13/analyze.py "m13-det=/Volumes/Extreme SSD/m13/m13-det-probe.jsonl" "m13-det2=/Volumes/Extreme SSD/m13/m13-det2-probe.jsonl" "m13-det4=/Volumes/Extreme SSD/m13/m13-det4-probe.jsonl"
python3 local/research/M13/analyze.py "m13-det3=/Volumes/Extreme SSD/m13/m13-det3-probe.jsonl-failed"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M13/` — `m13_replay_context.h`
(`b09643b1…`), `build_replay_player.py`, `analyze.py`, `REPORT.md` (this
file), `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m13/` —
`m13-det-probe.jsonl` (20888180 B), `m13-det2-probe.jsonl` (20904583 B),
`m13-det4-probe.jsonl` (20807015 B) and the matching `-run` dirs and
`-run.log` harness receipts; `analyze-all.txt` (the three-arm analyzer
output) and `analyze-det.txt`, `analyze-det2.txt`, `analyze-det4.txt`
(per-arm outputs); per-step header snapshots
`m13_replay_context.step1.h` (= M12 header),
`m13_replay_context.step2.h` (= M12 header, byte-identical),
`m13_replay_context.step3.h` (= committed header),
`m13_replay_context.step3-prefail.h` (pre-fix step-3 header,
`839cb759…`, recovered from the `m13-drawscan` player's
`native_frame_replay.h` copy); the pre-fix det3 attempt
(`m13-det3-probe.jsonl-failed` (239867 B), `m13-det3-run-failed`,
`m13-det3-run.log-failed`, `analyze-det3-failed.txt`; complete 200/200
`done` sequence with the delta armed on all 200 replays, missing
`resume_xfb`). Players (gitignored):
`local/research/M13/players/{m13-baseline,m13-drawscan,m13-drawscan2}/`
(each with `player`, `build.json`, launchers). All paths above are
symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m13-baseline` `14f7c7f7f58a` /
`45d923c93a6a` (player hash identical to M12's `m12-alt`/`m12-slot36`:
same header compiles to the same binary), `m13-drawscan` `839cb759b07e` /
`0ff1d86d4ca4`, `m13-drawscan2` `b09643b1590d` / `cef4e601a09f`.

## What I could not do

1. Per-draw EFB readback orchestration was not attempted in-box: the
readback entry point exists (`FramebufferManager::PeekEFBDepth`,
`VideoCommon/FramebufferManager.h:119`), but per-draw stream prefixes
re-execute from byte 0 with no header-side EFB reset between prefixes,
so a prefix scan would double-render; the reset receipt is ordered
follow-up, not this runbook. New in M13: the leave-one-out scan carries
the occlusion signal per draw without EFB access (each replay renders a
complete frame, so no reset question arises), but it attributes only
slot-consuming draws (30 of 1490 on the det4 frame); non-consuming
draws' occlusion interactions are not scanned.
2. Depth-buffer sampling at window boundaries was not attempted in-box:
same EFB API, but it yields per-window samples rather than the per-draw
receipt (ordered follow-up, not this runbook).
3. The drawscan arm caps at 128 consuming draws (fail-closed above the
cap); slot-0-scale frames (570+ consumers) need a chunked scan (ordered
follow-up, not this runbook).
4. The `m10_copy` detail renders 6 of 7 copies on the det2/det4 frames
(1024 B buffer cap; the XFB drain is the unrendered 7th).
`epoch_cons` carries all epochs, and the report's epoch tables are built
from it (inherited cosmetic, not a receipt gap).
5. Player dirs are under `local/research/M13/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs and all
probes are on the SSD as ordered.
6. Desktop only; no device work.

## Files

Committed under `local/research/M13/`: `m13_replay_context.h` (research
header, `b09643b1…`), `build_replay_player.py` (M12 driver, header path
only), `analyze.py` (M12 tables unchanged + M13 `m13_win`/`m13_nop`/
`m13_ref2` parsing, per-draw leave-one-out tables, per-draw
removed-shares table; missing keys print as n/a / sections skipped),
`REPORT.md` (this file), `waits.log` (2 waits, four claim/release pairs,
two annotations).

## Header diffs per step (`diff -u` against the M12 header)

Step 1: empty (verbatim copy). Step 2: empty (env-only; the M12 alt
machinery runs on slot 36 with no new header code). Step 3 follows,
generated from the committed `local/research/M13/m13_replay_context.h`
(= step 3; the step-3 header adds env-gated branches only, so the
step-1/step-2 arms are reproducible from it via env).

### Step 3

```diff
--- local/research/M12/m12_replay_context.h	2026-09-19 14:41:11
+++ local/research/M13/m13_replay_context.h	2026-09-19 16:01:30
@@ -1642,12 +1642,17 @@
                             // SSX_M12_ALT=1 imply RAMCOPY too.
                             const char* r12 = std::getenv("SSX_M12_RAMREF");
                             const char* alt = std::getenv("SSX_M12_ALT");
+                            // M13 step 3: SSX_M13_DRAWSCAN=1 (in M12 mode)
+                            // implies RAMCOPY too.
+                            const char* ds13 = std::getenv("SSX_M13_DRAWSCAN");
                             const int ref =
                                 (r && std::strcmp(r, "1") == 0) ||
                                         (r11 && std::strcmp(r11, "1") == 0) ||
                                         (r12 && std::strcmp(r12, "1") == 0) ||
                                         (m12_mode != 0 && alt &&
-                                         std::strcmp(alt, "1") == 0)
+                                         std::strcmp(alt, "1") == 0) ||
+                                        (m12_mode != 0 && ds13 &&
+                                         std::strcmp(ds13, "1") == 0)
                                     ? 1
                                     : 0;
                             return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
@@ -1926,6 +1931,53 @@
       }
     }
   }
+  // M13 step 3: per-consuming-draw leave-one-out scan (SSX_M13_DRAWSCAN=1,
+  // M12 mode only, m12_alt off). Draw-clock refinement of the M12 partition
+  // to per-draw granularity: shape 0 is the verbatim total, shapes 1..C each
+  // NOP one slot-consuming draw (drawrec cons bit), so every shape shares
+  // the SAME recorded frame. Fail-closed per shape (ok=0 leaves that shape
+  // verbatim) and fail-closed for the arm (no consuming draws, or more than
+  // the cap, leaves the whole sequence verbatim).
+  const int m13_want = (m12_mode == 2 && m12_alt == 0) ? ([] {
+                         const char* v = std::getenv("SSX_M13_DRAWSCAN");
+                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                       })()
+                                                     : 0;
+  std::vector<u32> m13_condraw;
+  if (m13_want && m10_mode != 0) {
+    for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
+      const M10DrawRec& dr = m10stream.drawrec[d];
+      if (dr.cons_pos != 0 || dr.cons_texmask != 0) m13_condraw.push_back(u32(d));
+    }
+  }
+  const unsigned kM13DrawCap = 128;
+  const int m13_scan = (m13_want && !m13_condraw.empty() &&
+                        m13_condraw.size() <= kM13DrawCap)
+                           ? 1
+                           : 0;
+  const unsigned m13_nshapes =
+      m13_scan ? 1u + (unsigned)m13_condraw.size() : 0u;
+  std::vector<std::vector<u8>> m13_exec, m13_pre;
+  std::vector<char> m13_ok;
+  std::vector<u32> m13_bytes;
+  if (m13_scan) {
+    m13_exec.resize(m13_condraw.size());
+    m13_pre.resize(m13_condraw.size());
+    m13_ok.assign(m13_condraw.size(), 0);
+    m13_bytes.assign(m13_condraw.size(), 0);
+    for (size_t s = 0; s < m13_condraw.size(); ++s) {
+      const M10DrawRec& dr = m10stream.drawrec[m13_condraw[s]];
+      m13_exec[s] = frame_exec;
+      m13_pre[s] = frame_pre_exec;
+      if (dr.size == 0 || dr.off + dr.size > m13_exec[s].size() ||
+          dr.off + dr.size > m13_pre[s].size())
+        continue;
+      std::memset(m13_exec[s].data() + dr.off, 0x00, dr.size);
+      std::memset(m13_pre[s].data() + dr.off, 0x00, dr.size);
+      m13_ok[s] = 1;
+      m13_bytes[s] = dr.size;
+    }
+  }
   const std::vector<u8>& exec_stream =
       m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
   const std::vector<u8>& pre_stream =
@@ -1967,7 +2019,7 @@
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
                   "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
                   "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d "
-                  "m12mode=%d m12slot=%d m12alt=%d",
+                  "m12mode=%d m12slot=%d m12alt=%d m13scan=%d m13shapes=%u",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1978,7 +2030,8 @@
                   m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
                   m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
                   m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
-                  m11_notext, m12_mode, m12_slot_self, m12_alt);
+                  m11_notext, m12_mode, m12_slot_self, m12_alt, m13_scan,
+                  m13_nshapes);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2077,7 +2130,9 @@
     s_m8_regcalls = 0;
     for (auto& w : s_m8_writes) w = 0;
     for (auto& r : s_m8_reads) r = 0;
-    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref && !m12_alt) ? m9_slot : -1;
+    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref && !m12_alt && !m13_scan)
+                      ? m9_slot
+                      : -1;
     s_m8_proj = 0;
     s_m9_surv = m9_surv;
     s_m9_first_hit = 0;
@@ -2085,7 +2140,9 @@
     s_m9_vb_mm = s_m9_va_mm = 0;
     s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
     s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
-    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref && !m12_alt) ? 1 : 0;
+    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref && !m12_alt && !m13_scan)
+                      ? 1
+                      : 0;
     s_m10_mat_done = 0;
     s_m10_post_done = 0;
     s_m10_snap_which = 0;
@@ -2134,6 +2191,25 @@
   int m12_samp_xm[4][3] = {};
   double m12_samp_xn[4][3] = {};
   unsigned m12_samp_n[4] = {};
+  // M13 step 3: per-shape ref2 storage + tallies (shape = replays % nshapes;
+  // shape 0 verbatim, shapes 1..C leave-one-out; one pristine ref per shape).
+  // vector<char> stands in for bool arrays (no vector<bool> bit-packing).
+  std::vector<std::vector<u8>> m13_ref(m13_nshapes);
+  std::vector<char> m13_ref_ok(m13_nshapes, 0);
+  std::vector<u64> m13_ref_hash(m13_nshapes, 0), m13_hk_hash(m13_nshapes, 0);
+  std::vector<unsigned> m13_kref(m13_nshapes, 0);
+  std::vector<unsigned> m13_n2(m13_nshapes, 0), m13_gt0(m13_nshapes, 0),
+      m13_uniform2(m13_nshapes, 0);
+  std::vector<unsigned> m13_xd2_min(m13_nshapes, 0), m13_xd2_max(m13_nshapes, 0);
+  std::vector<int> m13_xdmax2_max(m13_nshapes, 0);
+  std::vector<double> m13_xdmean2_min(m13_nshapes, 0.0),
+      m13_xdmean2_max(m13_nshapes, 0.0);
+  std::vector<char> m13_xd2_first(m13_nshapes, 1);
+  std::vector<u32> m13_samp_r(m13_nshapes * 3, 0);
+  std::vector<unsigned> m13_samp_xd(m13_nshapes * 3, 0);
+  std::vector<int> m13_samp_xm(m13_nshapes * 3, 0);
+  std::vector<double> m13_samp_xn(m13_nshapes * 3, 0.0);
+  std::vector<unsigned> m13_samp_n(m13_nshapes, 0);
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -2155,8 +2231,9 @@
     // bases, strides and VATs.
     if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
-    // M10 step 3: arm delta half (M12 step 2: the alt arm splits identically).
-    if (replays == kTransformFrom && (m10_ramref || m12_alt)) {
+    // M10 step 3: arm delta half (M12 step 2: the alt arm splits identically;
+    // M13 step 3: the drawscan arm splits identically too).
+    if (replays == kTransformFrom && (m10_ramref || m12_alt || m13_scan)) {
       s_m8_slot = m10_slot;
       s_m10_cap = 1;
     }
@@ -2183,6 +2260,16 @@
         m12_exec = &m12_nop_exec[m12_win - 1];
       }
     }
+    // M13 step 3: drawscan shape select (scan mode only; m12_alt is off,
+    // so the mod-4 select above is inert).
+    unsigned m13_win = 0;
+    if (m13_scan) {
+      m13_win = replays % m13_nshapes;
+      if (m13_win > 0 && m13_ok[m13_win - 1]) {
+        m12_pre = &m13_pre[m13_win - 1];
+        m12_exec = &m13_exec[m13_win - 1];
+      }
+    }
     if (deterministic) RunPre(*m12_pre);
     const double t_pre = Now();
     Run(*m12_exec);
@@ -2471,6 +2558,62 @@
             if (xm2 > m12_xdmax2_max[w]) m12_xdmax2_max[w] = xm2;
             if (xn2 < m12_xdmean2_min[w]) m12_xdmean2_min[w] = xn2;
             if (xn2 > m12_xdmean2_max[w]) m12_xdmean2_max[w] = xn2;
+          }
+        }
+      }
+    }
+    // M13 step 3: per-shape ref2 capture + diff (drawscan arm). Each
+    // shape's last pristine replay is its reference; that shape's delta
+    // replays diff against their own shape's bytes. After wall_end, out
+    // of wall_ms.
+    if (m13_scan && xfb_scratch_ok) {
+      u8* rwp13 = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
+      if (rwp13) {
+        const unsigned w13 = replays % m13_nshapes;
+        if (replays < kTransformFrom) {
+          m13_ref[w13].assign(rwp13, rwp13 + mask.xfb.bytes);
+          m13_ref_hash[w13] = RamHash(rwp13, mask.xfb.bytes);
+          m13_ref_ok[w13] = 1;
+          m13_kref[w13] = replays;
+        } else if (m13_ref_ok[w13]) {
+          const u64 hh13 = RamHash(rwp13, mask.xfb.bytes);
+          if (m13_n2[w13] == 0) m13_hk_hash[w13] = hh13;
+          if (hh13 == m13_hk_hash[w13]) ++m13_uniform2[w13];
+          ++m13_n2[w13];
+          unsigned x13 = 0;
+          int xm13 = 0;
+          unsigned long long xa13 = 0;
+          for (u32 i = 0; i < mask.xfb.bytes; ++i) {
+            const int dd = rwp13[i] > m13_ref[w13][i] ? rwp13[i] - m13_ref[w13][i]
+                                                     : m13_ref[w13][i] - rwp13[i];
+            if (dd > 0) {
+              ++x13;
+              xa13 += (unsigned)dd;
+              if (dd > xm13) xm13 = dd;
+            }
+          }
+          const double xn13 = x13 ? double(xa13) / double(x13) : 0.0;
+          if (x13 > 0) {
+            ++m13_gt0[w13];
+            if (m13_samp_n[w13] < 3) {
+              const unsigned sn = m13_samp_n[w13]++;
+              m13_samp_r[w13 * 3 + sn] = replays;
+              m13_samp_xd[w13 * 3 + sn] = x13;
+              m13_samp_xm[w13 * 3 + sn] = xm13;
+              m13_samp_xn[w13 * 3 + sn] = xn13;
+            }
+          }
+          if (m13_xd2_first[w13]) {
+            m13_xd2_min[w13] = m13_xd2_max[w13] = x13;
+            m13_xdmax2_max[w13] = xm13;
+            m13_xdmean2_min[w13] = m13_xdmean2_max[w13] = xn13;
+            m13_xd2_first[w13] = 0;
+          } else {
+            if (x13 < m13_xd2_min[w13]) m13_xd2_min[w13] = x13;
+            if (x13 > m13_xd2_max[w13]) m13_xd2_max[w13] = x13;
+            if (xm13 > m13_xdmax2_max[w13]) m13_xdmax2_max[w13] = xm13;
+            if (xn13 < m13_xdmean2_min[w13]) m13_xdmean2_min[w13] = xn13;
+            if (xn13 > m13_xdmean2_max[w13]) m13_xdmean2_max[w13] = xn13;
           }
         }
       }
@@ -3154,6 +3297,55 @@
               m12_samp_xm[w][s], m12_samp_xn[w][s]);
         }
         Event("m12_ref2", m12f);
+      }
+    }
+    // M13 step 3: drawscan receipts (want-gated; scan=0 rows carry the
+    // fail-closed shape via nshapes=0). m13_win carries the scheme + guard
+    // echo; one m13_nop per left-out draw; one m13_ref2 per shape.
+    if (m13_want) {
+      char m13w[256];
+      std::snprintf(m13w, sizeof(m13w),
+                    "scan=%d slot=%d scheme=modN nshapes=%u ndraws=%u cap=%u "
+                    "sel_shr=%d sel_idx=%d sel_text=%d m10nop_ok=%d",
+                    m13_scan, m10_slot, m13_nshapes,
+                    (unsigned)m13_condraw.size(), kM13DrawCap, m11_nopshr,
+                    m11_nopidx, m11_notext, int(m10_nop_ok));
+      Event("m13_win", m13w);
+      for (size_t s = 0; s < m13_condraw.size(); ++s) {
+        char m13n[160];
+        std::snprintf(m13n, sizeof(m13n),
+                      "shape=%u clk=%u ok=%d draws=%u bytes=%u",
+                      1u + (unsigned)s, m13_condraw[s] + 1, int(m13_ok[s]),
+                      m13_ok[s] ? 1u : 0u, m13_bytes[s]);
+        Event("m13_nop", m13n);
+      }
+      for (unsigned w = 0; w < m13_nshapes; ++w) {
+        char m13f[512];
+        char m13name[24];
+        if (w == 0) {
+          std::snprintf(m13name, sizeof(m13name), "verbatim");
+        } else {
+          std::snprintf(m13name, sizeof(m13name), "nodraw%u",
+                        m13_condraw[w - 1] + 1);
+        }
+        int m13foff = std::snprintf(
+            m13f, sizeof(m13f),
+            "shape=%u clk=%u name=%s ref=%d kref=%u refok=%d n2=%u gt0=%u "
+            "uniform2=%u xd2min=%u xd2max=%u xdmax2max=%d xdmean2min=%.3f "
+            "xdmean2max=%.3f refhash=%016llx samp=",
+            w, w == 0 ? 0u : m13_condraw[w - 1] + 1, m13name, m13_scan,
+            m13_kref[w], int(m13_ref_ok[w]), m13_n2[w], m13_gt0[w],
+            m13_uniform2[w], m13_xd2_min[w], m13_xd2_max[w], m13_xdmax2_max[w],
+            m13_xdmean2_min[w], m13_xdmean2_max[w],
+            static_cast<unsigned long long>(m13_ref_hash[w]));
+        for (unsigned s = 0; s < m13_samp_n[w]; ++s) {
+          if (m13foff < 0 || size_t(m13foff) >= sizeof(m13f) - 48) break;
+          m13foff += std::snprintf(
+              m13f + m13foff, sizeof(m13f) - size_t(m13foff), "%sr%u:%u/%d/%.3f",
+              s ? "," : "", m13_samp_r[w * 3 + s], m13_samp_xd[w * 3 + s],
+              m13_samp_xm[w * 3 + s], m13_samp_xn[w * 3 + s]);
+        }
+        Event("m13_ref2", m13f);
       }
     }
   }
```
