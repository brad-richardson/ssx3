# M11 — True-delta partitions: slot-36, indexed path, texture-mediated share: REPORT

Slot-36 true delta, per-vertex indexed-path decode with a shared-vs-indexed
partition, and a forced-RAM NOPTEXT arm for the texture-mediated share of
the slot-0 true-delta effect. Desktop only. Runbook
`local/muse/prompts/M11.md`. No `adb`, no device. Tables, no verdicts.

Header read first: `local/research/M10/REPORT.md` (all of it: the
32954-byte true delta, the "What I could not do" items 1–4 + 6, which
this brief works through in feasibility order) and the base header
`local/research/M10/m10_replay_context.h`.

Time box 6 hours; used about 1.5. Zero lease waits (eleven claim/release
pairs plus one annotation; the P1s agent never observed holding the
lease; never forced). One lease anomaly is logged in `waits.log` (file
absent at one release; run clean).

## Baseline note (read before the tables)

The M10 header on disk (`local/research/M10/m10_replay_context.h`, clean
tree) hashes to
`88eeb5aaa4c410b2c1fd85670be138875fe2edb912727bc85b186ecaaa2378f2`
via `shasum -a 256` (trust `shasum`, not memory; matches the M10 report's
pinned prefix).
Step 1 copied the on-disk file verbatim to
`local/research/M11/m11_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8/M9/M10 mechanism is kept in all
steps: PE mask, verbatim execute stream, restore, stall, pipe snapshot,
watched-window re-hash, `done`, XFB hash + scratch redirect, side-effect
counters, continuation capture, scoped bus, `m6frame`, presenter tracing,
record guard, trig_imx probe, M7 full/delta transforms, per-replay xdiff
stats, M8 census/slot/proj modes with stream-epoch census, M9 VAT walk +
slot/survival, M10 order/matrix/epoch/occ walks + NOP/RAM/ref2 arms. All
M11 additions are env-gated with defaults that preserve M10 behavior
(`SSX_M11_SLOT` unset); the committed header is the step-4 header, from
which every step's run is reproducible via env.

M11 modes (`SSX_M11_SLOT=N`, 0-63, forces M10 mode 2 on the same slot, so
each M11 run carries its own M10 order/matrix/epoch/occ receipts plus its
M9 VAT census, M9 survival and M8 census as cross-checks; M11 takes
precedence over `SSX_M10_SLOT`; M10 env alone = M10 behavior):
`SSX_M11_RAMREF=1` (same split as `SSX_M10_RAMREF`: implies RAMCOPY,
pristine replays 0–99, delta 100–199, rendered-reference diff; needs
`NOPCONS=0`),
`SSX_M11_NOPSHR=1` (NOP shared-path consuming draws, delta stays armed),
`SSX_M11_NOPIDX=1` (NOP indexed-position draws exposed to the slot, delta
stays armed),
`SSX_M11_NOPTEXT=1` (NOP texture-copy-epoch draws only, delta stays
armed). Unlike `SSX_M10_NOPCONS`, the M11 selectors never disarm the
delta. Survival reuses `SSX_M9_SURV=1`.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M10. `m11-det*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M11\n'`, removed after each run);
the log is `local/research/M11/waits.log` (zero waits, eleven
claim/release pairs, one annotation, never forced). Builds ran any time;
no build ran during a run.
`complete_hazard_resets` (harness field, as observed): all six arms 0;
every sequence is 200/200 with `done` and clean counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `88eeb5aa…` (= M10 on disk) | `players/m11-baseline` | `m11-det-run` (`m11-det`, `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1`) | `m11-det-probe.jsonl` |
| 2 slot-36 | `8d0051a5…` | `players/m11-slot36` | `m11-det2-run` (`m11-det2`, `SSX_M11_SLOT=36 SSX_M11_RAMREF=1 SSX_M9_SURV=1`) | `m11-det2-probe.jsonl` |
| 3 decode | `51b44e38…` | `players/m11-idx` | `m11-det3-run` (`m11-det3`, `SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M9_SURV=1`) | `m11-det3-probe.jsonl` |
| 3 nop-shr | `51b44e38…` | `players/m11-idx` | `m11-det4-run` (`m11-det4`, `SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPSHR=1 SSX_M9_SURV=1`) | `m11-det4-probe.jsonl` |
| 3 nop-idx | `51b44e38…` | `players/m11-idx` | `m11-det5-run` (`m11-det5`, `SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPIDX=1 SSX_M9_SURV=1`) | `m11-det5-probe.jsonl` |
| 4 notext | `f3383745…` (= committed) | `players/m11-text` | `m11-det6-run` (`m11-det6`, `SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPTEXT=1 SSX_M9_SURV=1`) | `m11-det6-probe.jsonl` |

The committed header is `f3383745…`. Later step revisions only add
env-gated branches (M11 slot/RAMREF, idx decode + NOPSHR/NOPIDX, NOPTEXT)
plus receipt-format supersets (`m11shr/m11idx/m11text` in `restored`,
`text=` in `m11_nop`); the unset paths that det2/det3/det4/det5 ran are
preserved verbatim, so every arm above is reproducible from the committed
header via env. Two det3–det6 runs were superseded before analysis (one
redundant duplicate guard line removed from the step-3/4 headers —
behavior-neutral: the rebuilt players hash identically to the pre-fix
builds — players rebuilt, arms re-run; one det6 re-run attempt exited
-5 post-sequence on live resume with a complete 200/200 `done` sequence,
kept as `-failed`; see `waits.log`); the table lists the final runs.

Player dirs live under `local/research/M11/players/` (the build driver
requires outputs under `local/`; they are gitignored build outputs, never
committed). Run dirs and every probe jsonl (>5 MB, ~5–22 MB each) live under
`/Volumes/Extreme SSD/m11/` (symlink-free; `realpath` is the path as
written). Probes, runs and players are not committed.

## Step 1 — baseline (M10 end state reproduces)

Unmodified copy, M10 slot-0 true-delta env. `analyze.py` prints 200 rows +
`done` + `xfb_equal_scratch=0/200` (forced-RAM signature, as M10 det7) +
`live_xfb_untouched=1` + `dafter_live`/`dframe`/`dpres`/`dimx` all 0/0 +
`pediff`/`vidiff` 0/0. Control for steps 2–4.

Seam-application receipt (`xform_stats`, slot mode):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 377400 |
| `hits` | 16600 (= 100 × 166 covering loads; first half counting-only) |
| `regcalls` | 0 |

Own-frame M9 census, m11-det (draws=1805, verts=38525; VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1680 | 125 | n/a | n/a |
| Tex0 | 1805 | 0 | 1710 | 1710 |
| Tex1 | 1723 | 82 | 523 | 441 |
| Tex2 | 1805 | 0 | 24 | 24 |
| Tex3 | 1805 | 0 | 5 | 5 |
| Tex4 | 1805 | 0 | 5 | 5 |
| Tex5-7 | 1805 | 0 | 0 | 0 |

Shared reach: Pos 0:797, Tex2 36:24. Survival trichotomy: live
100/100, per-vertex 100/100, shared-pos 100/100 (resident 100/100),
shared-tex 0 (resident 0/100); `dirty_post=0`, `zfreeze=0`;
`vb_mm=15500 va_mm=15500`, `hdirty 14000/4700/4600/16600`.
True-delta row: `ref=1 kref=100 refok=1 refhash=df24b2e79e810bc9`,
`n2=100 gt0=100 uniform2=100 xd2min/xd2max=29960 xdmax2max=120
xdmean2=2.924`.

Recorded without verdict: M10's end-state mechanism reproduces (100/100
uniform true delta against a rendered reference, guest/event clean); the
byte count is frame-dependent (29960 here on a 383902 B frame vs 32954 on
M10 det7's 318998 B frame).

## Per-step wall table (all six arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m11-det | 200 | 7.983 / 9.510 / 7.020 / 272.424 | 2.870 / 3.104 | 383902 / 3266 | YES | seq_wall_ms=2370.865 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m11-det2 | 200 | 7.083 / 7.655 / 6.649 / 277.870 | 3.026 / 3.444 | 353899 / 3043 | YES | seq_wall_ms=2362.815 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m11-det3 | 200 | 3.389 / 4.127 / 2.784 / 9.096 | 1.465 / 1.676 | 266045 / 2438 | YES | seq_wall_ms=1154.738 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m11-det4 | 200 | 4.405 / 5.752 / 4.077 / 12.479 | 1.844 / 2.138 | 401350 / 3450 | YES | seq_wall_ms=1374.590 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m11-det5 | 200 | 5.081 / 6.908 / 4.268 / 12.970 | 2.054 / 2.478 | 400719 / 3479 | YES | seq_wall_ms=1536.850 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m11-det6 | 200 | 5.367 / 7.506 / 4.795 / 14.006 | 2.006 / 2.505 | 342504 / 2999 | YES | seq_wall_ms=1623.527 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (266045 … 401350 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table). All
six rows: 200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2
dls=0 walk=100% unknown=0 benign=1` in all runs.
`xfb_equal_scratch=0/200` on all six rows is the forced-RAM signature
(rendered scratch vs fuchsia live ref), not a failure.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m11-det | 0.128 | 0.001 | 0.040 | 7.803 | 0.000 | 9.339 |
| m11-det2 | 0.149 | 0.001 | 0.049 | 6.874 | 0.000 | 7.423 |
| m11-det3 | 0.088 | 0.001 | 0.025 | 3.274 | 0.000 | 4.001 |
| m11-det4 | 0.096 | 0.001 | 0.074 | 4.234 | 0.000 | 5.557 |
| m11-det5 | 0.102 | 0.001 | 0.054 | 4.922 | 0.000 | 6.721 |
| m11-det6 | 0.134 | 0.001 | 0.039 | 5.188 | 0.000 | 7.299 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m11-det | 1887 | 90576 | 23.2 |
| m11-det2 | 1923 | 92304 | 22.7 |
| m11-det3 | 1047 | 50256 | 41.7 |
| m11-det4 | 1492 | 71616 | 29.3 |
| m11-det5 | 1454 | 69792 | 30.0 |
| m11-det6 | 2099 | 100752 | 20.8 |

## Step 2 — slot-36 true delta (M10 gaps 4 + 6, texcoord-stage residue)

M10 instruments unchanged on slot 36 (`SSX_M11_SLOT=36
SSX_M11_RAMREF=1 SSX_M9_SURV=1`): order table, matrix table, epoch table,
ref2 row. One run (m11-det2, 353899 B / 3043 updates, draws=1616,
verts=33750).

Walk cross-checks, m11-det2 (M10 walk vs M9 walk on the same stream):
draws 1616 = 1616, verts 33750 = 33750, `idx_loads` 1923 = stream
indexed 1923, `cons_tex` 14 = Tex2 shared+enabled reach slot-36 14,
consumed == size both, walk_ok=1 both. Seam/walk cross-check: walk
covering loads 110 = 11000/100 per-delta-replay seam hits (first half
counting-only).

Hit/draw order table, m11-det2 (slot 36, word 147):

| field | value |
| --- | --- |
| draws / verts | 1616 / 33750 |
| idx_loads | 1923 |
| covering (idx_cover / direct_cover; arr12/13/14/15) | 110 (110 / 0; 0/0/110/0) |
| first covering load (draw clock / byte off / kind) | 118 / 31172 / indexed |
| last covering load (draw clock / byte off) | 601 / 171742 |
| cons_pos / cons_tex / cons_any | 0 / 14 / 14 |
| first / last consuming draw | 428 / 500 |
| cons_before_first / cons_at_after_first | 0 / 14 |
| loads_before_first / loads_first_to_lastcons | 144 / 20 |
| seam_hits / seam_per_replay | 11000 / 55 |
| walk / walk_ok | 353899/353899 / 1 |

Covering-load draw clocks (n=110, full list):
`118,236,258,323,332,389,422,427,445,467,515,517,519,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,542,543,544,545,545,546,547,548,549,550,551,552,553,553,554,554,555,555,556,556,557,557,558,559,560,561,562,563,564,565,566,567,568,568,569,570,571,572,572,573,573,574,574,575,575,577,578,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,593,594,595,596,597,597,598,598,599,599,600,600,601`.

Consuming draw indices (n=14, full list):
`428,429,430,431,432,433,434,435,436,496,497,498,499,500`.

Full-matrix values, m11-det2 (slot 36, words 144..155; `done=1`,
`snap_which=2` shared-tex, `snap_ti=2`, `n=200`, `mm_live=100`,
`mm_snap=100`):

| i | word | before hex | before float | after hex | after float | post-live hex | post-live float | post-snap hex | post-snap float |
| ---: | ---: | --- | ---: | --- | ---: | --- | ---: | --- | ---: |
| 0 | 144 | 3cd5b19c | 0.0260857 | 3cd5b19c | 0.0260857 | 3f800000 | 1 | 3f800000 | 1 |
| 1 | 145 | bf2cc4cf | -0.674878 | bf2cc4cf | -0.674878 | 00000000 | 0 | 00000000 | 0 |
| 2 | 146 | 3f3ccab3 | 0.737468 | 3f3ccab3 | 0.737468 | 00000000 | 0 | 00000000 | 0 |
| 3 | 147 | 00000000 | 0 | 3dcccccd | 0.1 | 00000000 | 0 | 00000000 | 0 |
| 4 | 148 | 3f7fe9b0 | 0.99966 | 3f7fe9b0 | 0.99966 | 00000000 | 0 | 00000000 | 0 |
| 5 | 149 | 3c90442f | 0.0176106 | 3c90442f | 0.0176106 | 3f800000 | 1 | 3f800000 | 1 |
| 6 | 150 | bc9da55e | -0.0192439 | bc9da55e | -0.0192439 | 00000000 | 0 | 00000000 | 0 |
| 7 | 151 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 8 | 152 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 9 | 153 | 3f3cdb29 | 0.737719 | 3f3cdb29 | 0.737719 | 00000000 | 0 | 00000000 | 0 |
| 10 | 154 | 3f2cd3dd | 0.675108 | 3f2cd3dd | 0.675108 | 3f800000 | 1 | 3f800000 | 1 |
| 11 | 155 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |

Recorded without verdict: the +0.1 lands on word 147 only (all 11
siblings bit-identical before/after). Post-replay live and snapshot agree
on all 12 words (`live == snap`) with the 100/100 split (`mm=100`).

EFB-copy table, m11-det2 (compared xfb=`0x004dc660`/573440):

| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |
| ---: | ---: | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |
| 0 | 9 | 0x00701560 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 1 | 18 | 0x00702580 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 2 | 27 | 0x007035a0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 3 | 37 | 0x0110c440 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 4 | 48 | 0x013faee0 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 5 | 59 | 0x014d61e0 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 6 | 1616 | 0x004dc660 | 573440 | 1 | 1 | 0x000000 | 640 | 448 | 1 |

Epoch table, m11-det2 (draws=1616; epoch_cons=`0,0,0,0,0,0,14,0`):

| epoch | draw range | cons draws | closing copy |
| ---: | --- | ---: | --- |
| 0 | 1..9 | 0 | copy 0 (ovl 0, clear 1) |
| 1 | 10..18 | 0 | copy 1 (ovl 0, clear 1) |
| 2 | 19..27 | 0 | copy 2 (ovl 0, clear 1) |
| 3 | 28..37 | 0 | copy 3 (ovl 0, clear 1) |
| 4 | 38..48 | 0 | copy 4 (ovl 0, clear 1) |
| 5 | 49..59 | 0 | copy 5 (ovl 0, clear 1) |
| 6 | 60..1616 | 14 | copy 6 (ovl 1, clear 1) |
| 7 | 1617..1616 | 0 | tail (none) |

Per-class table, consuming draws (same buckets as M10):

| Arm | cons | culled | out-of-range | in-range | cull reasons (cons; non-disjoint) | copies (XFB + non-XFB) |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| m11-det2 | 14 | 0 | 0 | 14 | cull_all=0 scis_empty=0 znever=0 | 1 + 6 (3× 32×32, 3× 128×128 clears) |

All-draw context: `all_cull=0 all_scis=0 all_znever=0`.
Survival trichotomy (`n=200`, second half 100/100): live 100/0/0,
per-vertex 100/0/0, shared-pos resident 0, shared-tex resident 100 with
100/0/0; `vb_mm=3800 va_mm=300`,
`hdirty 7500/11000/1700/11000`, `dirty_post=0`, `zfreeze=0`.

True-delta arm (m11-det2: forced RAM + split at replay 100, diffed
against replay 99's rendered scratch frame):

| field | value |
| --- | --- |
| ref / kref / refok / refhash | 1 / 100 / 1 / `18325adea03e306e` |
| n2 (delta replays) | 100 |
| gt0 (differing) | 100 |
| uniform2 (identical to replay 100) | 100 |
| xd2min / xd2max (bytes, of 573440) | 501 / 501 |
| xdmax2max | 6 |
| xdmean2min / xdmean2max | 1.234 / 1.234 |
| samples | r100:501/6/1.234, r101:501/6/1.234, r102:501/6/1.234 |

Standing of the texcoord-stage row (table):

| Candidate | Standing | Receipt |
| --- | --- | --- |
| Tex2 path moves no pixels (texcoord stage) | excluded | det2: the slot-36 delta moves 501 bytes on 100/100 delta replays against a rendered pristine reference — 14/14 Tex2 consuming draws in-range and unculled |
| perturbation lands after consumption, slot-36 path | excluded | `cons_before_first=0/14`; first covering load at draw clock 118, first consuming draw 428 |

## Step 3 — indexed-path exposure (M10 gap 2)

Per-vertex `pnmtxidx` decoded into `transformmatrices` in the M10 walk
(header-only: each vertex carries its index as a direct u8 `& 0x3f` at
the vertex start — posmtx first, then texmtx bytes in texgen order —
with the vendor-passed `vertex_size` stride; `m11_idx` event). Three
runs on the step-3 header: a plain slot-0 true delta (m11-det3, decode +
total), a shared-NOP + delta arm (m11-det4, `SSX_M11_NOPSHR=1`), and an
indexed-NOP + delta arm (m11-det5, `SSX_M11_NOPIDX=1`).

Decode table (`m11_idx`; slot 0; `tex_draws`/`tex_exp_draws` per texgen
0..7):

| Arm | idx_pos_draws | idx_pos_verts | exp_draws | exp_verts | tex_draws | tex_exp_draws |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| m11-det3 | 51 | 7418 | 49 | 2678 | 0,42,0,0,0,0,0,0 | 0,0,0,0,0,0,0,0 |
| m11-det4 | 75 | 10008 | 73 | 3548 | 0,54,0,0,0,0,0,0 | 0,0,0,0,0,0,0,0 |
| m11-det5 | 69 | 10045 | 67 | 3707 | 0,52,0,0,0,0,0,0 | 0,0,0,0,0,0,0,0 |
| m11-det6 | 120 | 16135 | 118 | 6144 | 0,93,0,0,0,0,0,0 | 0,0,0,0,0,0,0,0 |
| m11-det | n/a | n/a | n/a | n/a | n/a | n/a |
| m11-det2 | n/a | n/a | n/a | n/a | n/a | n/a |

(m11-det ran on the step-1 header and m11-det2 on the step-2 header, both
predating the decode event; m11-det6's row rides on the step-4 header.)
No indexed-texgen vertex references slot 0 on any arm
(`tex_exp_draws` all zero; only Tex1 carries indexed vertices).

Decode cross-checks (table):

| Check | det3 | det4 | det5 | det6 |
| --- | ---: | ---: | ---: | ---: |
| `idx_pos_draws` vs M9 `pos_indexed` | 51 = 51 | 75 = 75 | 69 = 69 | 120 = 120 |
| `tex_draws[1]` vs M9 `tex_indexed[1]` | 42 = 42 | 54 = 54 | 52 = 52 | 93 = 93 |
| seam hits vs 100 × covering loads | 7500 = 100×75 | 11900 = 100×119 | 11200 = 100×112 | 14600 = 100×146 |

Partition arms (each arm its own recorded frame with its own replay-99
reference; cross-arm subtraction is frame-confounded — see note):

| Arm | Frame B / draws | cons (shr) | NOP draws / bytes (ok) | ref2 gt0/uniform2 | ref2 xd2min/xd2max | xdmax2max | xdmean2 | refhash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| m11-det (total) | 383902 / 1805 | 797 | 0 / 0 (n/a) | 100 / 100 | 29960 / 29960 | 120 | 2.924 | `df24b2e79e810bc9` |
| m11-det3 (total) | 266045 / 1392 | 622 | 0 / 0 (0) | 100 / 100 | 44021 / 44021 | 105 | 2.380 | `631ae1dfdcf76e5f` |
| m11-det4 (NOPSHR → indexed-only) | 401350 / 2299 | 823 | 823 / 157032 (1) | 100 / 100 | 498 / 498 | 143 | 6.269 | `15379c5435144421` |
| m11-det5 (NOPIDX → shared-only) | 400719 / 2314 | 871 | 67 / 70341 (1) | 100 / 100 | 72719 / 72719 | 125 | 2.369 | `5fdf80f160c017c3` |

NOP-span cross-checks: det4 NOP draws 823 = `cons_any` 823; det5 NOP
draws 67 = `exp_draws` 67. Shared and indexed draw sets are disjoint by
construction (the VAT path bit decides per draw), so each arm removes
exactly one path's slot-0 consumers; the surviving ref2 bytes are that
arm's other-path contribution on its own frame.

Recorded without verdict: un-NOP'd slot-0 totals are 29960 (det) and
44021 (det3) on their frames; the indexed-only arm moves 498 bytes and
the shared-only arm 72719 bytes on theirs. Totals and partition arms run
on different recorded frames, so the shares cannot be subtracted against
one frame's total (see "What I could not do" 2).

m11-det4 survival note (as observed): with the shared set NOP'd, the
post-replay trichotomy reads `pv_other=100 pos_other=100
pos_res=100 tex_res=0 dirty_post=100` (vs `pv_after=100 pos_after=100
dirty_post=0` on every other slot-0 arm); live xfmem still
`xf_after=100`, and ref2 still moves 498 bytes on 100/100.

## Step 4 — texture-mediated share (M10 gap 3)

Forced-RAM NOPTEXT arm: NOP the early texture-copy epochs' draws only
(draws whose render-target epoch closes with a non-XFB copy,
`is_xfb==0`), delta armed (`SSX_M11_SLOT=0 SSX_M11_RAMREF=1
SSX_M11_NOPTEXT=1 SSX_M9_SURV=1`). One run (m11-det6, 342504 B / 2999
updates, draws=1448, verts=32653, covering=146, cons=656).

EFB-copy table, m11-det6 (compared xfb=`0x004dc660`/573440):

| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |
| ---: | ---: | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |
| 0 | 9 | 0x00701560 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 1 | 18 | 0x00702580 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 2 | 27 | 0x007035a0 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 3 | 37 | 0x0110c440 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 4 | 49 | 0x013ef240 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 5 | 57 | 0x014c8b80 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 6 | 1448 | 0x004dc660 | 573440 | 1 | 1 | 0x000000 | 640 | 448 | 1 |

Epoch table, m11-det6 (draws=1448; epoch_cons=`9,9,9,1,1,1,626,0`):

| epoch | draw range | cons draws | closing copy |
| ---: | --- | ---: | --- |
| 0 | 1..9 | 9 | copy 0 (texture) |
| 1 | 10..18 | 9 | copy 1 (texture) |
| 2 | 19..27 | 9 | copy 2 (texture) |
| 3 | 28..37 | 1 | copy 3 (texture) |
| 4 | 38..49 | 1 | copy 4 (texture) |
| 5 | 50..57 | 1 | copy 5 (texture) |
| 6 | 58..1448 | 626 | copy 6 (XFB drain) |
| 7 | 1449..1448 | 0 | tail (none) |

NOPTEXT receipt (`m11_nop`): `shr=0 idx=0 text=1 ok=1 draws=57
bytes=18143` — draws 1..57, exactly the six texture epochs
(9+9+9+10+12+8). Per-class context: cons=656, culled=0, out-of-range=30
(the 30 texture-epoch consuming draws behind clear barriers),
in-range=626; `all_cull=all_scis=all_znever=0`.

True-delta row with texture carriers removed (ref2-style):

| field | value |
| --- | --- |
| ref / kref / refok / refhash | 1 / 100 / 1 / `444e7aa0d7c7adbc` |
| n2 (delta replays) | 100 |
| gt0 (differing) | 100 |
| uniform2 (identical to replay 100) | 100 |
| xd2min / xd2max (surviving bytes, of 573440) | 44470 / 44470 |
| xdmax2max | 153 |
| xdmean2min / xdmean2max | 2.024 / 2.024 |
| samples | r100:44470/153/2.024, r101:44470/153/2.024, r102:44470/153/2.024 |

Recorded without verdict: 44470 bytes survive on 100/100 delta replays
with the texture-copy epochs' draws removed. Mechanism note (no
verdict): recorded texture bytes are restored from memory updates before
every replay, so NOP'd texture renders sample recorded texels in both
halves and the texture-mediated delta path cancels from the ref2 diff;
the surviving bytes flow through the 626 in-range main-epoch consuming
draws. Same-frame caveat as §Step 3 (this frame's own un-NOP'd total is
unmeasured).

Per-draw depth (M10 gap 1): not attempted; restated as open — no
header-only per-draw depth instrument exists (`Flush`/`SetConstants` are
vendor-called with no header hook; the header drives the execute pass
through `RunFifo` with the live decoder's internal callbacks, so there is
no header-overridable per-draw callback in that path), and M11's
draw-granular NOP arms bound each path's collective contribution only.

## Mechanism table (M10 gaps this brief works through)

| M10 gap | Standing | Receipt |
| --- | --- | --- |
| 4 + texcoord stage (slot-36 delta) | measured | §Step 2: 501 bytes on 100/100, 14/14 Tex2 draws in-range, unculled |
| 2 (per-vertex `pnmtxidx`) | decoded + partitioned (draw-granular, cross-frame) | §Step 3: 49–118 exposed draws/frame (2678–6144 verts); indexed-only 498 B, shared-only 72719 B surviving arms |
| 3 (direct vs texture-mediated) | measured (surviving share) | §Step 4: 44470 surviving bytes with texture epochs removed |
| 1 (per-draw depth) | open | no header-only per-draw instrument (see above) |
| 6 (other-slot runs) | partly (slot 36 run) | §Step 2; other slots remain unrun |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m11-det | `fc=8153` | `replay_disabled=0 fc=8156 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m11-det2 | `fc=8041` | `replay_disabled=0 fc=8044 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m11-det3 | `fc=8146` | `replay_disabled=0 fc=8149 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m11-det4 | `fc=8133` | `replay_disabled=0 fc=8136 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m11-det5 | `fc=7409` | `replay_disabled=0 fc=7412 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m11-det6 | `fc=6770` | `replay_disabled=0 fc=6773 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the sextuple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M10/M9/M8/M7 sequence hashes and all
M6 sequence and M5 sequence/disabled hashes) is tabulated as observed.
`resume fc − fc0 = 3` in each run (the live record window; per-replay
`dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m11-det | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m11-det2 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m11-det3 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m11-det4 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m11-det5 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m11-det6 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

Scratch `0/200` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M10/build_replay_player.py`; `m11-idx` was built from the
step-3 snapshot and `m11-text` from the step-4/committed header via a
header swap — the driver compiles `local/research/M11/m11_replay_context.h`):

```
python3 local/research/M11/build_replay_player.py local/research/M11/players/m11-baseline
python3 local/research/M11/build_replay_player.py local/research/M11/players/m11-slot36
python3 local/research/M11/build_replay_player.py local/research/M11/players/m11-idx
python3 local/research/M11/build_replay_player.py local/research/M11/players/m11-text
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M11\n'`,
remove after each run; profiles fresh per run):

```
SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det-run" --seconds 240
SSX_M11_SLOT=36 SSX_M11_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-slot36 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det2 --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det2-run" --seconds 240
SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-idx --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det3 --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det3-run" --seconds 240
SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPSHR=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-idx --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det4 --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det4-run" --seconds 240
SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPIDX=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det5-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-idx --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det5 --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det5-run" --seconds 240
SSX_M11_SLOT=0 SSX_M11_RAMREF=1 SSX_M11_NOPTEXT=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m11/m11-det6-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M11/players/m11-text --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m11-det6 --cpu-thread --output "/Volumes/Extreme SSD/m11/m11-det6-run" --seconds 240
```

Analysis:

```
python3 local/research/M11/analyze.py "m11-det=/Volumes/Extreme SSD/m11/m11-det-probe.jsonl" "m11-det2=/Volumes/Extreme SSD/m11/m11-det2-probe.jsonl" "m11-det3=/Volumes/Extreme SSD/m11/m11-det3-probe.jsonl" "m11-det4=/Volumes/Extreme SSD/m11/m11-det4-probe.jsonl" "m11-det5=/Volumes/Extreme SSD/m11/m11-det5-probe.jsonl" "m11-det6=/Volumes/Extreme SSD/m11/m11-det6-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M11/` — `m11_replay_context.h`
(`f3383745…`), `build_replay_player.py`, `analyze.py`, `REPORT.md` (this
file), `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m11/` —
`m11-det-probe.jsonl` (20838614 B), `m11-det2-probe.jsonl` (15399698 B),
`m11-det3-probe.jsonl`, `m11-det4-probe.jsonl`, `m11-det5-probe.jsonl`,
`m11-det6-probe.jsonl` and the matching `-run` dirs and `-run.log`
harness receipts; `analyze-all.txt` (the six-arm analyzer output) and
`analyze-det{,2,3,4,5,6}.txt` (per-arm outputs); per-step header
snapshots `m11_replay_context.step1.h` (= M10 header),
`m11_replay_context.step2.h`, `m11_replay_context.step3.h`,
`m11_replay_context.step4.h` (= committed header); superseded first-run
files (`*-superseded`: pre-guard-fix det3–det6 probes/runs/analyses) and
the post-sequence-crash det6 attempt (`m11-det6-probe.jsonl-failed`,
`m11-det6-run-failed`, `m11-det6-run.log-failed`; complete 200/200
`done` sequence, missing `resume_xfb`). Players (gitignored):
`local/research/M11/players/{m11-baseline,m11-slot36,m11-idx,m11-text}/`
(each with `player`, `build.json`, launchers). All paths above are
symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m11-baseline` `88eeb5aaa4c4` /
`9188345ed349` (player hash identical to M10's `m10-ref`: same header
compiles to the same binary), `m11-slot36` `8d0051a57cda` /
`8a755848956d`, `m11-idx` `51b44e3820d0` / `edce1f978790`,
`m11-text` `f3383745b6ed` / `fe222dbd18e7`.

## What I could not do

1. No per-draw depth-occlusion query exists header-only: `Flush` /
`SetConstants` are vendor-called with no header hook (M10 gap 1
persists), so per-draw occlusion is bounded collectively per path
(det4/det5/det6 surviving-bytes arms) but not attributed per draw. The
header drives the execute pass through `RunFifo` with the live decoder's
internal callbacks, so there is no header-overridable per-draw callback
in that path; a per-draw receipt needs a vendor execute-pass hook or
per-draw EFB readback (ordered follow-up, not this runbook).
2. Same-frame partition is not measured: each NOP arm records its own
frame, so the indexed-only (498 B), shared-only (72719 B) and NOPTEXT
(44470 B) surviving counts cannot be subtracted against one frame's
total. The decode admits draw-granular partition (done); same-frame
would need alternating NOP streams with dual ref2 references in one run
(ordered follow-up, not this runbook).
3. Slot-36 indexed-path exposure is unmeasured: m11-det2 ran on the
step-2 header, before the decode event existed. The decode is
slot-parametric (`SSX_M11_SLOT=36` on the committed header fills it);
ordered follow-up, not a gap in this runbook.
4. The `xform` capacity-row flag does not reflect the RAMREF split
(all 200 rows tag `xform=1` on every M11 arm; the split is visible in
hits/trichotomy/`mm` instead). Inherited cosmetic (M10 gap 5); the
analyzer does not use the flag for M11 tables.
5. Player dirs are under `local/research/M11/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs and all
probes are on the SSD as ordered.
6. Desktop only; no device work.

## Files

Committed under `local/research/M11/`: `m11_replay_context.h` (research
header, `f3383745…`), `build_replay_player.py` (M10 driver, header path
only), `analyze.py` (M10 tables unchanged + M11 `m11_idx`/`m11_nop`
parsing, indexed-decode tables, partition-NOP receipts; missing keys
print as n/a / sections skipped), `REPORT.md` (this file), `waits.log`
(zero waits, eleven claim/release pairs, one annotation).

## Header diffs per step (`diff -u` against the M10 header)

Step 1: empty (verbatim copy). Steps 2–4 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m11/m11_replay_context.step2.h`,
`/Volumes/Extreme SSD/m11/m11_replay_context.step3.h` and the committed
`local/research/M11/m11_replay_context.h` (= step 4; the step-4 header
adds env-gated branches only, so every arm is reproducible from it via
env).

### Step 2

```diff
--- local/research/M10/m10_replay_context.h	2026-09-19 12:16:29
+++ /Volumes/Extreme SSD/m11/m11_replay_context.step2.h	2026-09-19 12:49:46
@@ -1511,7 +1511,22 @@
   // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
   // (all M9 walks + survival receipts ride along as cross-checks) and arms
   // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
-  const int m10_slot = [] {
+  // M11 step 2: SSX_M11_SLOT=N (0-63) runs the M10 instruments unchanged on
+  // the same slot (M11 mode forces M10 mode 2; all M10/M9/M8 receipts ride
+  // along). Precedence: M11 > M10. M10 env alone = M10 behavior.
+  const int m11_slot_self = [] {
+    const char* v = std::getenv("SSX_M11_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m11_mode = m11_slot_self >= 0 ? 2 : 0;
+  const int m10_slot_self = [] {
     const char* v = std::getenv("SSX_M10_SLOT");
     if (!v || !*v) return -1;
     int n = 0;
@@ -1522,6 +1537,7 @@
     }
     return n;
   }();
+  const int m10_slot = m11_mode != 0 ? m11_slot_self : m10_slot_self;
   const int m10_mode = m10_slot >= 0 ? 2 : 0;
   // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
   // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
@@ -1546,15 +1562,25 @@
   const int m10_ramcopy = m10_mode == 2 ? ([] {
                             const char* v = std::getenv("SSX_M10_RAMCOPY");
                             const char* r = std::getenv("SSX_M10_RAMREF");
+                            // M11 step 2: SSX_M11_RAMREF=1 implies RAMCOPY too.
+                            const char* r11 = std::getenv("SSX_M11_RAMREF");
                             const int ref =
-                                (r && std::strcmp(r, "1") == 0) ? 1 : 0;
+                                (r && std::strcmp(r, "1") == 0) ||
+                                        (r11 && std::strcmp(r11, "1") == 0)
+                                    ? 1
+                                    : 0;
                             return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
                           })()
                                         : 0;
   const int m10_ramref =
       (m10_mode == 2 && m10_nopcons == 0) ? ([] {
         const char* r = std::getenv("SSX_M10_RAMREF");
-        return r && std::strcmp(r, "1") == 0 ? 1 : 0;
+        // M11 step 2: SSX_M11_RAMREF=1 arms the same split (needs nop=0).
+        const char* r11 = std::getenv("SSX_M11_RAMREF");
+        return (r && std::strcmp(r, "1") == 0) ||
+                       (r11 && std::strcmp(r11, "1") == 0)
+                   ? 1
+                   : 0;
       })()
                                          : 0;
   const int m9_slot = m10_mode != 0 ? m10_slot : [] {
@@ -1744,7 +1770,7 @@
     return 0;
   }();
   {
-    char detail[512];
+    char detail[640];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
@@ -1752,7 +1778,8 @@
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
-                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d",
+                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
+                  "m11mode=%d m11slot=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1761,7 +1788,8 @@
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                   xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
                   m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
-                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref);
+                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
+                  m11_mode, m11_slot_self);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
```

### Step 3

```diff
--- local/research/M10/m10_replay_context.h	2026-09-19 12:16:29
+++ /Volumes/Extreme SSD/m11/m11_replay_context.step3.h	2026-09-19 13:18:46
@@ -857,6 +857,10 @@
   u32 size = 0;
   u32 cons_pos = 0;
   u32 cons_texmask = 0;  // bit i = consumes the slot via texgen i
+  // M11 step 3: per-vertex indexed-position exposure of this draw to the slot
+  // (decoded from the leading index bytes; 0 when the shared path is used).
+  u32 idx_pos_any = 0;  // >= 1 vertex with pnmtxidx == slot
+  u32 idx_pos_n = 0;    // vertices with pnmtxidx == slot
   // M10 step 3: rasterizer state at draw time (seeded from recorded BPMem).
   u32 cull = 0;  // GenMode cull_mode (0 none, 1 back, 2 front, 3 all)
   u32 scis_empty = 0;  // scissor TL>BR in 11-bit coords
@@ -886,6 +890,13 @@
   std::vector<M10DrawRec> drawrec;  // per draw (index d-1), stream order
   std::vector<u32> load_draws;  // draw clock at every indexed load
   std::vector<M10CopyRec> copies;  // EFB-copy triggers, stream order
+  // M11 step 3: per-vertex indexed-path aggregates (decoded in the walk).
+  u32 idx_pos_draws = 0;       // draws with VB_HAS_POSMTXIDX
+  u32 idx_pos_verts = 0;       // vertices in those draws
+  u32 idx_pos_exp_draws = 0;   // ... with >= 1 vertex pnmtxidx == slot
+  u32 idx_pos_exp_verts = 0;   // vertices with pnmtxidx == slot
+  u32 idx_tex_draws[8] = {};   // draws with VB_HAS_TEXMTXIDXi
+  u32 idx_tex_exp_draws[8] = {};  // ... with >= 1 vertex texmtxidx[i] == slot
 };
 class M10OrderWalk final : public OpcodeDecoder::Callback {
 public:
@@ -995,8 +1006,8 @@
       m_pending_load = true;
     }
   }
-  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
-                          const u8*) override {
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32 vertex_size,
+                          u16 num_vertices, const u8* vertex_data) override {
     ++m_stats.draws;
     m_stats.verts += num_vertices;
     const u32 v = vat & 7;
@@ -1016,6 +1027,52 @@
       if ((comp & (VB_HAS_TEXMTXIDX0 << i)) == 0 && enabled &&
           idx[1 + i] == m_stats.slot) {
         d.cons_texmask |= 1u << i;
+      }
+    }
+    // M11 step 3: per-vertex matrix-index decode (M10 gap 2). Header-only:
+    // when the path bit is set, each vertex carries its index as a direct
+    // u8 (& 0x3f) at the vertex start — posmtx first, then texmtx bytes in
+    // texgen order (VertexLoader.cpp PosMtx_ReadDirect_UByte /
+    // TexMtx_ReadDirect_UByte; popcount(vtx_desc & 0x1FF) index bytes per
+    // vertex in GetVertexSize). Stride is the vendor-passed vertex_size;
+    // vertex_data points at the first vertex (OpcodeDecoding.h RunCommand).
+    const bool has_pos = (comp & VB_HAS_POSMTXIDX) != 0;
+    u32 tex_off[8];
+    {
+      u32 noff = has_pos ? 1 : 0;
+      for (u32 i = 0; i < 8; ++i) {
+        tex_off[i] = noff;
+        if (comp & (VB_HAS_TEXMTXIDX0 << i)) ++noff;
+      }
+    }
+    if (has_pos) {
+      ++m_stats.idx_pos_draws;
+      m_stats.idx_pos_verts += num_vertices;
+    }
+    for (u32 i = 0; i < 8; ++i) {
+      if (comp & (VB_HAS_TEXMTXIDX0 << i)) ++m_stats.idx_tex_draws[i];
+    }
+    if (vertex_data != nullptr && vertex_size > 0) {
+      bool tex_exp[8] = {};
+      for (u32 n = 0; n < u32(num_vertices); ++n) {
+        const u8* vd = vertex_data + size_t(n) * vertex_size;
+        if (has_pos && vertex_size > 0 && (vd[0] & 63) == m_stats.slot) {
+          d.idx_pos_any = 1;
+          ++d.idx_pos_n;
+        }
+        for (u32 i = 0; i < 8; ++i) {
+          if ((comp & (VB_HAS_TEXMTXIDX0 << i)) != 0 &&
+              tex_off[i] < vertex_size && (vd[tex_off[i]] & 63) == m_stats.slot) {
+            tex_exp[i] = true;
+          }
+        }
+      }
+      if (d.idx_pos_any) {
+        ++m_stats.idx_pos_exp_draws;
+        m_stats.idx_pos_exp_verts += d.idx_pos_n;
+      }
+      for (u32 i = 0; i < 8; ++i) {
+        if (tex_exp[i]) ++m_stats.idx_tex_exp_draws[i];
+      }
+    }
     d.cull = (m_gen >> 14) & 3u;
     d.scis_tl = m_scis_tl;
     d.scis_br = m_scis_br;
@@ -1511,7 +1568,22 @@
   // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
   // (all M9 walks + survival receipts ride along as cross-checks) and arms
   // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
-  const int m10_slot = [] {
+  // M11 step 2: SSX_M11_SLOT=N (0-63) runs the M10 instruments unchanged on
+  // the same slot (M11 mode forces M10 mode 2; all M10/M9/M8 receipts ride
+  // along). Precedence: M11 > M10. M10 env alone = M10 behavior.
+  const int m11_slot_self = [] {
+    const char* v = std::getenv("SSX_M11_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m11_mode = m11_slot_self >= 0 ? 2 : 0;
+  const int m10_slot_self = [] {
     const char* v = std::getenv("SSX_M10_SLOT");
     if (!v || !*v) return -1;
     int n = 0;
@@ -1522,6 +1594,7 @@
     }
     return n;
   }();
+  const int m10_slot = m11_mode != 0 ? m11_slot_self : m10_slot_self;
   const int m10_mode = m10_slot >= 0 ? 2 : 0;
   // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
   // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
@@ -1546,15 +1619,25 @@
   const int m10_ramcopy = m10_mode == 2 ? ([] {
                             const char* v = std::getenv("SSX_M10_RAMCOPY");
                             const char* r = std::getenv("SSX_M10_RAMREF");
+                            // M11 step 2: SSX_M11_RAMREF=1 implies RAMCOPY too.
+                            const char* r11 = std::getenv("SSX_M11_RAMREF");
                             const int ref =
-                                (r && std::strcmp(r, "1") == 0) ? 1 : 0;
+                                (r && std::strcmp(r, "1") == 0) ||
+                                        (r11 && std::strcmp(r11, "1") == 0)
+                                    ? 1
+                                    : 0;
                             return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
                           })()
                                         : 0;
   const int m10_ramref =
       (m10_mode == 2 && m10_nopcons == 0) ? ([] {
         const char* r = std::getenv("SSX_M10_RAMREF");
-        return r && std::strcmp(r, "1") == 0 ? 1 : 0;
+        // M11 step 2: SSX_M11_RAMREF=1 arms the same split (needs nop=0).
+        const char* r11 = std::getenv("SSX_M11_RAMREF");
+        return (r && std::strcmp(r, "1") == 0) ||
+                       (r11 && std::strcmp(r11, "1") == 0)
+                   ? 1
+                   : 0;
       })()
                                          : 0;
   const int m9_slot = m10_mode != 0 ? m10_slot : [] {
@@ -1680,6 +1763,22 @@
       }
     }
   }
+  // M11 step 3: NOP selectors that keep the delta armed (unlike
+  // SSX_M10_NOPCONS, which disarms it), for the shared-vs-indexed partition.
+  // SSX_M11_NOPSHR=1 NOPs shared-path consuming draws (the M10 NOPCONS=1 set);
+  // SSX_M11_NOPIDX=1 NOPs indexed-position draws exposed to the slot
+  // (idx_pos_any from the step-3 decode). M11 mode only; combine with
+  // SSX_M11_RAMREF=1 for ref2-style surviving-bytes arms. Unset = M10 shape.
+  const int m11_nopshr = m11_mode == 2 ? ([] {
+                           const char* v = std::getenv("SSX_M11_NOPSHR");
+                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                         })()
+                                       : 0;
+  const int m11_nopidx = m11_mode == 2 ? ([] {
+                           const char* v = std::getenv("SSX_M11_NOPIDX");
+                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                         })()
+                                       : 0;
   // M10 step 3: NOP-collective arm. Consuming-draw spans come from the M10
   // walk over the verbatim stream; both replay streams share its layout
   // (scratch patch changes BP values, not sizes). Fail closed: any bad span
@@ -1687,15 +1786,19 @@
   std::vector<u8> frame_nop_exec, frame_nop_pre;
   u32 m10_nop_draws = 0, m10_nop_bytes = 0;
   bool m10_nop_ok = false;
-  if (m10_nopcons && m10_mode != 0) {
+  if ((m10_nopcons || m11_nopshr || m11_nopidx) && m10_mode != 0) {
     frame_nop_exec = frame_exec;
     frame_nop_pre = frame_pre_exec;
     bool patch_ok = !m10stream.drawrec.empty();
     u32 nd = 0, nb = 0;
     for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
       const M10DrawRec& dr = m10stream.drawrec[d];
-      const bool hit = m10_nopcons == 2 || dr.cons_pos != 0 ||
-                       dr.cons_texmask != 0;
+      const bool cons = dr.cons_pos != 0 || dr.cons_texmask != 0;
+      // M10 NOPCONS=1/2 sets preserved verbatim; M11 selectors add the
+      // shared set (NOPSHR) and the indexed-exposed set (NOPIDX).
+      const bool hit = m10_nopcons == 2 || (m10_nopcons == 1 && cons) ||
+                       (m11_nopshr && cons) ||
+                       (m11_nopidx && dr.idx_pos_any != 0);
       if (!hit) continue;
       if (dr.size == 0 || dr.off + dr.size > frame_nop_exec.size() ||
           dr.off + dr.size > frame_nop_pre.size()) {
@@ -1744,7 +1847,7 @@
     return 0;
   }();
   {
-    char detail[512];
+    char detail[640];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
@@ -1752,7 +1855,8 @@
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
-                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d",
+                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
+                  "m11mode=%d m11slot=%d m11shr=%d m11idx=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1761,7 +1865,8 @@
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                   xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
                   m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
-                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref);
+                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
+                  m11_mode, m11_slot_self, m11_nopshr, m11_nopidx);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2779,6 +2884,38 @@
                                m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
     }
     Event("m10_ref2", m10f);
+    // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
+    // only; the M10 receipts above are unchanged). m11_idx carries the
+    // per-vertex decode aggregates; m11_nop the armed selectors + spans.
+    if (m11_mode != 0) {
+      char m11i[512];
+      int m11ioff = std::snprintf(
+          m11i, sizeof(m11i),
+          "slot=%d idx_pos_draws=%u idx_pos_verts=%u exp_draws=%u exp_verts=%u "
+          "tex_draws=",
+          m10_slot, m10stream.idx_pos_draws, m10stream.idx_pos_verts,
+          m10stream.idx_pos_exp_draws, m10stream.idx_pos_exp_verts);
+      for (u32 i = 0; i < 8; ++i) {
+        if (m11ioff < 0 || size_t(m11ioff) >= sizeof(m11i) - 24) break;
+        m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                                 "%s%u", i ? "," : "",
+                                 m10stream.idx_tex_draws[i]);
+      }
+      m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                               " tex_exp_draws=");
+      for (u32 i = 0; i < 8; ++i) {
+        if (m11ioff < 0 || size_t(m11ioff) >= sizeof(m11i) - 24) break;
+        m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                                 "%s%u", i ? "," : "",
+                                 m10stream.idx_tex_exp_draws[i]);
+      }
+      Event("m11_idx", m11i);
+      char m11n[128];
+      std::snprintf(m11n, sizeof(m11n), "shr=%d idx=%d ok=%d draws=%u bytes=%u",
+                    m11_nopshr, m11_nopidx, int(m10_nop_ok), m10_nop_draws,
+                    m10_nop_bytes);
+      Event("m11_nop", m11n);
+    }
   }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
```

### Step 4 (= committed)

```diff
--- local/research/M10/m10_replay_context.h	2026-09-19 12:16:29
+++ local/research/M11/m11_replay_context.h	2026-09-19 13:18:57
@@ -857,6 +857,10 @@
   u32 size = 0;
   u32 cons_pos = 0;
   u32 cons_texmask = 0;  // bit i = consumes the slot via texgen i
+  // M11 step 3: per-vertex indexed-position exposure of this draw to the slot
+  // (decoded from the leading index bytes; 0 when the shared path is used).
+  u32 idx_pos_any = 0;  // >= 1 vertex with pnmtxidx == slot
+  u32 idx_pos_n = 0;    // vertices with pnmtxidx == slot
   // M10 step 3: rasterizer state at draw time (seeded from recorded BPMem).
   u32 cull = 0;  // GenMode cull_mode (0 none, 1 back, 2 front, 3 all)
   u32 scis_empty = 0;  // scissor TL>BR in 11-bit coords
@@ -886,6 +890,13 @@
   std::vector<M10DrawRec> drawrec;  // per draw (index d-1), stream order
   std::vector<u32> load_draws;  // draw clock at every indexed load
   std::vector<M10CopyRec> copies;  // EFB-copy triggers, stream order
+  // M11 step 3: per-vertex indexed-path aggregates (decoded in the walk).
+  u32 idx_pos_draws = 0;       // draws with VB_HAS_POSMTXIDX
+  u32 idx_pos_verts = 0;       // vertices in those draws
+  u32 idx_pos_exp_draws = 0;   // ... with >= 1 vertex pnmtxidx == slot
+  u32 idx_pos_exp_verts = 0;   // vertices with pnmtxidx == slot
+  u32 idx_tex_draws[8] = {};   // draws with VB_HAS_TEXMTXIDXi
+  u32 idx_tex_exp_draws[8] = {};  // ... with >= 1 vertex texmtxidx[i] == slot
 };
 class M10OrderWalk final : public OpcodeDecoder::Callback {
 public:
@@ -995,8 +1006,8 @@
       m_pending_load = true;
     }
   }
-  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
-                          const u8*) override {
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32 vertex_size,
+                          u16 num_vertices, const u8* vertex_data) override {
     ++m_stats.draws;
     m_stats.verts += num_vertices;
     const u32 v = vat & 7;
@@ -1014,8 +1025,54 @@
       if ((comp & (VB_HAS_TEXMTXIDX0 << i)) == 0 && enabled &&
           idx[1 + i] == m_stats.slot) {
         d.cons_texmask |= 1u << i;
+      }
+    }
+    // M11 step 3: per-vertex matrix-index decode (M10 gap 2). Header-only:
+    // when the path bit is set, each vertex carries its index as a direct
+    // u8 (& 0x3f) at the vertex start — posmtx first, then texmtx bytes in
+    // texgen order (VertexLoader.cpp PosMtx_ReadDirect_UByte /
+    // TexMtx_ReadDirect_UByte; popcount(vtx_desc & 0x1FF) index bytes per
+    // vertex in GetVertexSize). Stride is the vendor-passed vertex_size;
+    // vertex_data points at the first vertex (OpcodeDecoding.h RunCommand).
+    const bool has_pos = (comp & VB_HAS_POSMTXIDX) != 0;
+    u32 tex_off[8];
+    {
+      u32 noff = has_pos ? 1 : 0;
+      for (u32 i = 0; i < 8; ++i) {
+        tex_off[i] = noff;
+        if (comp & (VB_HAS_TEXMTXIDX0 << i)) ++noff;
+      }
+    }
+    if (has_pos) {
+      ++m_stats.idx_pos_draws;
+      m_stats.idx_pos_verts += num_vertices;
+    }
+    for (u32 i = 0; i < 8; ++i) {
+      if (comp & (VB_HAS_TEXMTXIDX0 << i)) ++m_stats.idx_tex_draws[i];
+    }
+    if (vertex_data != nullptr && vertex_size > 0) {
+      bool tex_exp[8] = {};
+      for (u32 n = 0; n < u32(num_vertices); ++n) {
+        const u8* vd = vertex_data + size_t(n) * vertex_size;
+        if (has_pos && vertex_size > 0 && (vd[0] & 63) == m_stats.slot) {
+          d.idx_pos_any = 1;
+          ++d.idx_pos_n;
+        }
+        for (u32 i = 0; i < 8; ++i) {
+          if ((comp & (VB_HAS_TEXMTXIDX0 << i)) != 0 &&
+              tex_off[i] < vertex_size && (vd[tex_off[i]] & 63) == m_stats.slot) {
+            tex_exp[i] = true;
+          }
+        }
+      }
+      if (d.idx_pos_any) {
+        ++m_stats.idx_pos_exp_draws;
+        m_stats.idx_pos_exp_verts += d.idx_pos_n;
+      }
+      for (u32 i = 0; i < 8; ++i) {
+        if (tex_exp[i]) ++m_stats.idx_tex_exp_draws[i];
+      }
+    }
     d.cull = (m_gen >> 14) & 3u;
     d.scis_tl = m_scis_tl;
     d.scis_br = m_scis_br;
@@ -1511,7 +1568,22 @@
   // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
   // (all M9 walks + survival receipts ride along as cross-checks) and arms
   // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
-  const int m10_slot = [] {
+  // M11 step 2: SSX_M11_SLOT=N (0-63) runs the M10 instruments unchanged on
+  // the same slot (M11 mode forces M10 mode 2; all M10/M9/M8 receipts ride
+  // along). Precedence: M11 > M10. M10 env alone = M10 behavior.
+  const int m11_slot_self = [] {
+    const char* v = std::getenv("SSX_M11_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m11_mode = m11_slot_self >= 0 ? 2 : 0;
+  const int m10_slot_self = [] {
     const char* v = std::getenv("SSX_M10_SLOT");
     if (!v || !*v) return -1;
     int n = 0;
@@ -1522,6 +1594,7 @@
     }
     return n;
   }();
+  const int m10_slot = m11_mode != 0 ? m11_slot_self : m10_slot_self;
   const int m10_mode = m10_slot >= 0 ? 2 : 0;
   // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
   // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
@@ -1546,15 +1619,25 @@
   const int m10_ramcopy = m10_mode == 2 ? ([] {
                             const char* v = std::getenv("SSX_M10_RAMCOPY");
                             const char* r = std::getenv("SSX_M10_RAMREF");
+                            // M11 step 2: SSX_M11_RAMREF=1 implies RAMCOPY too.
+                            const char* r11 = std::getenv("SSX_M11_RAMREF");
                             const int ref =
-                                (r && std::strcmp(r, "1") == 0) ? 1 : 0;
+                                (r && std::strcmp(r, "1") == 0) ||
+                                        (r11 && std::strcmp(r11, "1") == 0)
+                                    ? 1
+                                    : 0;
                             return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
                           })()
                                         : 0;
   const int m10_ramref =
       (m10_mode == 2 && m10_nopcons == 0) ? ([] {
         const char* r = std::getenv("SSX_M10_RAMREF");
-        return r && std::strcmp(r, "1") == 0 ? 1 : 0;
+        // M11 step 2: SSX_M11_RAMREF=1 arms the same split (needs nop=0).
+        const char* r11 = std::getenv("SSX_M11_RAMREF");
+        return (r && std::strcmp(r, "1") == 0) ||
+                       (r11 && std::strcmp(r11, "1") == 0)
+                   ? 1
+                   : 0;
       })()
                                          : 0;
   const int m9_slot = m10_mode != 0 ? m10_slot : [] {
@@ -1680,6 +1763,32 @@
       }
     }
   }
+  // M11 step 3: NOP selectors that keep the delta armed (unlike
+  // SSX_M10_NOPCONS, which disarms it), for the shared-vs-indexed partition.
+  // SSX_M11_NOPSHR=1 NOPs shared-path consuming draws (the M10 NOPCONS=1 set);
+  // SSX_M11_NOPIDX=1 NOPs indexed-position draws exposed to the slot
+  // (idx_pos_any from the step-3 decode). M11 mode only; combine with
+  // SSX_M11_RAMREF=1 for ref2-style surviving-bytes arms. Unset = M10 shape.
+  const int m11_nopshr = m11_mode == 2 ? ([] {
+                           const char* v = std::getenv("SSX_M11_NOPSHR");
+                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                         })()
+                                       : 0;
+  const int m11_nopidx = m11_mode == 2 ? ([] {
+                           const char* v = std::getenv("SSX_M11_NOPIDX");
+                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                         })()
+                                       : 0;
+  // M11 step 4: SSX_M11_NOPTEXT=1 NOPs the early texture-copy epochs' draws
+  // only (draws whose render-target epoch closes with a non-XFB copy —
+  // is_xfb==0 — per M10 gap 3), keeping the delta armed. Combine with
+  // SSX_M11_RAMREF=1: surviving ref2 bytes are the non-texture-mediated
+  // share. M11 mode only. Unset = step-3 shape.
+  const int m11_notext = m11_mode == 2 ? ([] {
+                           const char* v = std::getenv("SSX_M11_NOPTEXT");
+                           return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                         })()
+                                       : 0;
   // M10 step 3: NOP-collective arm. Consuming-draw spans come from the M10
   // walk over the verbatim stream; both replay streams share its layout
   // (scratch patch changes BP values, not sizes). Fail closed: any bad span
@@ -1687,15 +1796,34 @@
   std::vector<u8> frame_nop_exec, frame_nop_pre;
   u32 m10_nop_draws = 0, m10_nop_bytes = 0;
   bool m10_nop_ok = false;
-  if (m10_nopcons && m10_mode != 0) {
+  if ((m10_nopcons || m11_nopshr || m11_nopidx || m11_notext) &&
+      m10_mode != 0) {
     frame_nop_exec = frame_exec;
     frame_nop_pre = frame_pre_exec;
     bool patch_ok = !m10stream.drawrec.empty();
     u32 nd = 0, nb = 0;
     for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
       const M10DrawRec& dr = m10stream.drawrec[d];
-      const bool hit = m10_nopcons == 2 || dr.cons_pos != 0 ||
-                       dr.cons_texmask != 0;
+      const bool cons = dr.cons_pos != 0 || dr.cons_texmask != 0;
+      // M11 step 4: texture-epoch test — the draw's epoch is the first copy
+      // at/after it (same attribution as the m10_occ epoch table); a
+      // texture epoch closes with a non-XFB copy. Tail draws (no copy
+      // at/after) are not texture-epoch draws.
+      bool in_tex_epoch = false;
+      if (m11_notext) {
+        for (size_t e = 0; e < m10stream.copies.size(); ++e) {
+          if (m10stream.copies[e].draw < u32(d) + 1) continue;
+          in_tex_epoch = m10stream.copies[e].is_xfb == 0;
+          break;
+        }
+      }
+      // M10 NOPCONS=1/2 sets preserved verbatim; M11 selectors add the
+      // shared set (NOPSHR), the indexed-exposed set (NOPIDX) and the
+      // texture-epoch set (NOPTEXT).
+      const bool hit = m10_nopcons == 2 || (m10_nopcons == 1 && cons) ||
+                       (m11_nopshr && cons) ||
+                       (m11_nopidx && dr.idx_pos_any != 0) ||
+                       (m11_notext && in_tex_epoch);
       if (!hit) continue;
       if (dr.size == 0 || dr.off + dr.size > frame_nop_exec.size() ||
           dr.off + dr.size > frame_nop_pre.size()) {
@@ -1744,7 +1872,7 @@
     return 0;
   }();
   {
-    char detail[512];
+    char detail[640];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
@@ -1752,7 +1880,8 @@
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
                   "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
-                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d",
+                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d "
+                  "m11mode=%d m11slot=%d m11shr=%d m11idx=%d m11text=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1761,7 +1890,9 @@
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                   xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
                   m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
-                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref);
+                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref,
+                  m11_mode, m11_slot_self, m11_nopshr, m11_nopidx,
+                  m11_notext);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -2779,6 +2910,39 @@
                                m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
     }
     Event("m10_ref2", m10f);
+    // M11 step 3: indexed-path exposure + partition-NOP receipts (M11 mode
+    // only; the M10 receipts above are unchanged). m11_idx carries the
+    // per-vertex decode aggregates; m11_nop the armed selectors + spans.
+    if (m11_mode != 0) {
+      char m11i[512];
+      int m11ioff = std::snprintf(
+          m11i, sizeof(m11i),
+          "slot=%d idx_pos_draws=%u idx_pos_verts=%u exp_draws=%u exp_verts=%u "
+          "tex_draws=",
+          m10_slot, m10stream.idx_pos_draws, m10stream.idx_pos_verts,
+          m10stream.idx_pos_exp_draws, m10stream.idx_pos_exp_verts);
+      for (u32 i = 0; i < 8; ++i) {
+        if (m11ioff < 0 || size_t(m11ioff) >= sizeof(m11i) - 24) break;
+        m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                                 "%s%u", i ? "," : "",
+                                 m10stream.idx_tex_draws[i]);
+      }
+      m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                               " tex_exp_draws=");
+      for (u32 i = 0; i < 8; ++i) {
+        if (m11ioff < 0 || size_t(m11ioff) >= sizeof(m11i) - 24) break;
+        m11ioff += std::snprintf(m11i + m11ioff, sizeof(m11i) - size_t(m11ioff),
+                                 "%s%u", i ? "," : "",
+                                 m10stream.idx_tex_exp_draws[i]);
+      }
+      Event("m11_idx", m11i);
+      char m11n[128];
+      std::snprintf(m11n, sizeof(m11n),
+                    "shr=%d idx=%d text=%d ok=%d draws=%u bytes=%u", m11_nopshr,
+                    m11_nopidx, m11_notext, int(m10_nop_ok), m10_nop_draws,
+                    m10_nop_bytes);
+      Event("m11_nop", m11n);
+    }
   }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
```
