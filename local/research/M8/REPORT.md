# M8 — Delta propagation: why 152 seam hits move zero pixels: REPORT

Slot-usage census + second-slot delta + projection-path reachability on the
`g_transform` seam, desktop only. Runbook `local/muse/prompts/M8.md`. No
`adb`, no device. No verdicts.

Header read first: `local/research/M7/REPORT.md` (all of it: Step 3's
152-hits/0-bytes finding, the slot-0 choice rationale, "What I could not do"),
`local/research/S2/REPORT.md` Part 4 section "What a `ReplayContext` still has
to own" item 5 (the honesty gate this closes: "original-frame equality,
unchanged guest and event state, clean continuation"), and the base header
`local/research/M7/m7_replay_context.h`.

Time box 6 hours; used about 1.2. One lease wait (P1n held at first check,
released within ~2 minutes; no 5-minute poll elapsed), four claim/release
pairs, no force.

## Baseline note (read before the tables)

The M7 header on disk (`local/research/M7/m7_replay_context.h`, clean tree)
hashes to `0bfc4860257330c65c5e4407b94e2350bc549f93f527cbacfbc70f0bc6886f36`
via `shasum -a 256` (trust `shasum`, not memory; matches the M7 report's pinned
prefix). Step 1 copied the on-disk file verbatim to
`local/research/M8/m8_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7 mechanism is kept in all steps: PE mask,
verbatim execute stream, restore, stall, pipe snapshot, watched-window
re-hash, `done`, XFB hash + scratch redirect, side-effect counters,
continuation capture, scoped bus, `m6frame`, presenter tracing, record guard,
trig_imx probe, M7 full/delta transforms, per-replay xdiff stats. All M8
additions are env-gated with defaults that preserve M7 behavior
(`SSX_M8_CENSUS`/`SSX_M8_SLOT`/`SSX_M8_PROJ` all unset); the committed header
is the step-3 header, from which every step's run is reproducible via env.

M8 transform modes (precedence SLOT > PROJ > CENSUS; counting stays on in
every M8 mode, so each delta run carries its own census): mode 1
(`SSX_M8_CENSUS=1`, counts only, `xform_stats` mode 7), mode 2
(`SSX_M8_SLOT=N`, N=0-63, M7's +0.1f tx delta retargeted to word N*4+3,
`xform_stats` mode 8), mode 3 (`SSX_M8_PROJ=1`, +0.1f on XF regs 0x1020-0x1026
IF a seam call ever covers one, `xform_stats` mode 9). `regcalls` counts seam
calls at addr >= 0x1000 in every M8 mode.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M7. `m8-det` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile directories are
fresh per run. Each desktop run held `/tmp/ssx3-host-lease` (`printf 'M8\n'`,
removed after each run); the log is `local/research/M8/waits.log` (one P1n wait,
four claim/release pairs, no polls past the first check, never forced). Builds
ran any time; no build ran during a run. `complete_hazard_resets` (harness
field, as observed): m8-det 0, m8-det2 1, m8-det3 0, m8-det4 0; every sequence
is 200/200 with `done` and clean counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `0bfc4860…` (= M6-on-disk via M7) | `players/m8-baseline` | `m8-det-run` (`m8-det`, `SSX_M7_XFORM=delta`) | `m8-det-probe.jsonl` |
| 2 census | `b8f28048…` | `players/m8-census` | `m8-det2-run` (`m8-det2`, `SSX_M8_CENSUS=1`) | `m8-det2-probe.jsonl` |
| 3 slot36 | `c98e5582…` | `players/m8-delta` | `m8-det3-run` (`m8-det3`, `SSX_M8_SLOT=36`) | `m8-det3-probe.jsonl` |
| 4 proj | `c98e5582…` | `players/m8-delta` | `m8-det4-run` (`m8-det4`, `SSX_M8_PROJ=1`) | `m8-det4-probe.jsonl` |

The committed header is `c98e5582…` (step 3, identical to the step-3 snapshot).

Player dirs live under `local/research/M8/players/` (the build driver requires
outputs under `local/`; they are gitignored build outputs, never committed).
Run dirs and every probe jsonl (>5 MB, ~21 MB each) live under
`/Volumes/Extreme SSD/m8/` (symlink-free; `realpath` is the path as written).
Probes, runs and players are not committed.

## Step 1 — baseline (M7 end state reproduces)

Unmodified copy, M7 delta env. `analyze.py` prints 200 rows + `done` +
`xfb_equal_scratch=200/200` + `live_xfb_untouched=1` +
`dafter_live`/`dframe`/`dpres`/`dimx` all 0/0. Control for steps 2-4.

Seam-application receipt (`xform_stats`, M7 delta mode):

| Field | Value |
| --- | --- |
| `mode` | 2 |
| `calls` | 324400 (1622/replay = the run's `indexed` count: every indexed load fired the seam) |
| `hits` | 24400 (122/replay covering word 0x003; M7: 152/replay on its frame) |

122 vs 152 is frame variation (this frame: 331509 B / 1622 indexed; M7's:
360159 B / 1741 indexed; hits/indexed = 7.5% here vs 8.7% there), same
phenomenon: triple-digit seam hits per replay, zero bytes differ.

## Per-step wall table (all four arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m8-det | 200 | 3.242 / 4.457 / 2.881 / 6.245 | 1.774 / 2.007 | 331509 / 2782 | YES | seq_wall_ms=1121.653 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m8-det2 | 200 | 2.913 / 3.864 / 2.420 / 9.553 | 1.637 / 1.907 | 308134 / 2681 | YES | seq_wall_ms=1011.314 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m8-det3 | 200 | 2.616 / 3.443 / 2.182 / 8.353 | 1.442 / 1.634 | 295842 / 2125 | YES | seq_wall_ms=940.775 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m8-det4 | 200 | 4.231 / 5.280 / 3.353 / 6.782 | 2.239 / 2.518 | 385167 / 3262 | YES | seq_wall_ms=1265.743 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (295842 … 385167 B), so wall medians are not comparable
across rows as mechanism costs (M5 §Per-step wall table). All four rows:
200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2 dls=0 walk=100%
unknown=0 benign=1` in all runs.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m8-det | 0.105 | 0.001 | 0.032 | 3.101 | 0.001 | 4.310 |
| m8-det2 | 0.095 | 0.001 | 0.029 | 2.788 | 0.001 | 3.741 |
| m8-det3 | 0.077 | 0.001 | 0.024 | 2.516 | 0.001 | 3.326 |
| m8-det4 | 0.193 | 0.001 | 0.046 | 3.981 | 0.001 | 5.064 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m8-det | 1622 | 77856 | 26.9 |
| m8-det2 | 1412 | 67776 | 30.9 |
| m8-det3 | 1050 | 50400 | 41.6 |
| m8-det4 | 2570 | 123360 | 17.0 |

## Step 2 — slot-usage census

Three instruments, all header-only, all env-gated (unset = M7 behavior):

- (a) **writes**: per-seam-call tally of every pos-matrix slot (0-63)
  overlapped by `[address, address+count)`. Sequence totals over 200 replays.
- (b) **reads**: on each seam call, sample of the exact matrix-index
  expressions `VertexShaderManager::SetConstants` reads
  (`g_main_cp_state.matrix_index_a/b`: PosNormalMtxIdx, Tex0-7MtxIdx;
  `VertexShaderManager.cpp:292,307-310,324-327`), tallying each distinct
  referenced slot per call. All nine are 6-bit pos-slot indices; the
  normal-matrix (&31) sub-path is not separately tabled.
- (c) **draws-affected**: `M8CensusWalk` decodes the verbatim recorded stream
  once at setup, tracking matrix-index state through CP 0x30/0x40 writes
  (`CPState::LoadCPReg`) and XF 0x1018/0x1019 writes
  (`XFStateManager::SetTexMatrixChangedA/B` write-through to the same CP
  state), attributing every primitive command to the distinct slots the live
  index state references. Per-frame (one attribution per draw, not per
  replay). Per-vertex pnmtxidx (the `transformmatrices` indexed path) is NOT
  decoded.

Stream-census summary (`m8_meta`) across the three M8 runs:

| Run | draws | verts | epochs | matidx_cp | matidx_xf | direct_xfmem | direct_pos_words | stream_indexed | idx_pos | idx_reg | projreg_writes | walk | walk_ok |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | :-: |
| m8-det2 | 1468 | 28081 | 172 | 194 | 194 | 0 | 0 | 1412 | 1412 | 0 | 9 | 308134/308134 | 0 (see note) |
| m8-det3 | 1481 | 26431 | 200 | 234 | 234 | 0 | 0 | 1050 | 1050 | 0 | 7 | 295842/295842 | 1 |
| m8-det4 | 1571 | 36266 | 169 | 201 | 201 | 0 | 0 | 2570 | 2570 | 0 | 11 | 385167/385167 | 1 |

Step-2 `walk_ok=0` note: the step-2 header had no benign split in
`M8CensusWalk::OnUnknown`, so the frame's single known-but-ignored 0x44/0x48
byte (the same byte `PeMaskWalk` reports as `benign=1` on these same bytes)
tripped `unknown=1`. The walk is valid: `consumed == size` on all three runs
and `stream_indexed == mask.indexed` exactly (1412/1050/2570). The benign
split landed in the step-3 header (`walk_ok=1`, `benign=1` on det3/det4).

Recorded without verdict: `direct_xfmem=0` on all three frames (no direct XF
load touches XF mem, so the seam fires only via indexed loads here);
`idx_pos == stream_indexed` on all three (every indexed load covers >= 1
pos-matrix word); `idx_reg=0` on all three (no indexed load covers regs);
`matidx_cp == matidx_xf` on all three (index writes arrive in equal numbers
via both paths); projection regs are written 7-11x per frame via the regs
path (see Step 4).

Slot table, m8-det2 (step-2 receipt; writes/reads = sequence totals over 200
replays; draws = per-frame epoch attribution):

```
| slot | writes (tot) | writes/replay | reads (tot) | draws-affected |
| 0 | 20600 | 103.00 | 250800 | 796 |
| 1 | 20600 | 103.00 | 0 | 0 |
| 2 | 20600 | 103.00 | 0 | 0 |
| 3 | 16600 | 83.00 | 400 | 62 |
| 4 | 16600 | 83.00 | 0 | 0 |
| 5 | 16600 | 83.00 | 0 | 0 |
| 6 | 15400 | 77.00 | 400 | 88 |
| 7 | 15400 | 77.00 | 0 | 0 |
| 8 | 15400 | 77.00 | 0 | 0 |
| 9 | 14800 | 74.00 | 600 | 85 |
| 10 | 14800 | 74.00 | 0 | 0 |
| 11 | 14800 | 74.00 | 0 | 0 |
| 12 | 14200 | 71.00 | 400 | 80 |
| 13 | 14200 | 71.00 | 0 | 0 |
| 14 | 14200 | 71.00 | 0 | 0 |
| 15 | 14200 | 71.00 | 400 | 84 |
| 16 | 14200 | 71.00 | 0 | 0 |
| 17 | 14200 | 71.00 | 0 | 0 |
| 18 | 13800 | 69.00 | 400 | 104 |
| 19 | 13800 | 69.00 | 0 | 0 |
| 20 | 13800 | 69.00 | 0 | 0 |
| 21 | 13200 | 66.00 | 1000 | 41 |
| 22 | 13200 | 66.00 | 0 | 0 |
| 23 | 13200 | 66.00 | 0 | 0 |
| 24 | 12600 | 63.00 | 400 | 85 |
| 25 | 12600 | 63.00 | 0 | 0 |
| 26 | 12600 | 63.00 | 0 | 0 |
| 27 | 12200 | 61.00 | 27600 | 43 |
| 28 | 12200 | 61.00 | 0 | 0 |
| 29 | 12200 | 61.00 | 0 | 0 |
| 30 | 19400 | 97.00 | 32200 | 797 |
| 31 | 19400 | 97.00 | 0 | 0 |
| 32 | 19400 | 97.00 | 0 | 0 |
| 33 | 14000 | 70.00 | 0 | 0 |
| 34 | 14000 | 70.00 | 0 | 0 |
| 35 | 14000 | 70.00 | 0 | 0 |
| 36 | 17200 | 86.00 | 282400 | 1468 |
| 37 | 17200 | 86.00 | 0 | 0 |
| 38 | 17200 | 86.00 | 0 | 0 |
| 39 | 13800 | 69.00 | 282400 | 1468 |
| 40 | 13800 | 69.00 | 0 | 0 |
| 41 | 13800 | 69.00 | 0 | 0 |
| 42 | 13400 | 67.00 | 282400 | 1468 |
| 43 | 13400 | 67.00 | 0 | 0 |
| 44 | 13400 | 67.00 | 0 | 0 |
| 45 | 13400 | 67.00 | 282400 | 1468 |
| 46 | 13400 | 67.00 | 0 | 0 |
| 47 | 13400 | 67.00 | 0 | 0 |
| 48 | 13000 | 65.00 | 282400 | 1468 |
| 49 | 13000 | 65.00 | 0 | 0 |
| 50 | 13000 | 65.00 | 0 | 0 |
| 51 | 12800 | 64.00 | 282400 | 1468 |
| 52 | 12800 | 64.00 | 0 | 0 |
| 53 | 12800 | 64.00 | 0 | 0 |
| 54 | 9000 | 45.00 | 0 | 0 |
| 55 | 9000 | 45.00 | 0 | 0 |
| 56 | 9000 | 45.00 | 0 | 0 |
| 57 | 8800 | 44.00 | 0 | 0 |
| 58 | 8800 | 44.00 | 0 | 0 |
| 59 | 8800 | 44.00 | 0 | 0 |
| 60 | 0 | 0.00 | 282400 | 1468 |
```

3 slots all-zero (61, 62, 63: never written, never referenced).
Totals: writes 847200, reads 2291400, draws 12541 (draws double-count
multi-slot epochs).

Recorded without verdict: writes arrive in identical triples (slots 3k/3k+1/
3k+2, the 12-word indexed-load shape); reads/draws land only on triple-start
slots. Slot 0: 103 writes/replay, reads on 250800/282400 seam samples (88.8%),
draws-affected 796/1468 (54.2%). The two independent instruments (live seam-time
sampling vs offline stream-epoch decode) agree exactly on the referenced-slot
SET (the same 18 slots have reads>0 and draws>0; magnitudes differ because the
sampling bases differ: per-seam-call vs per-draw). Largest draws-affected is a
7-way tie at 1468/1468: slots 36, 39, 42, 45, 48, 51, 60. Slot 60 is referenced
on every draw and every sample yet never written (0 writes).

## Step 3 — second-slot delta (slot 36)

Recorded choice: slot 36. The runbook prescribes the largest-draws-affected
slot; the census returns a 7-way tie at 1468/1468 (36, 39, 42, 45, 48, 51,
60), broken by largest writes (proves the slot is live this frame and
guarantees seam coverage of the delta word): 36: 17200, 39: 13800, 42: 13400,
45: 13400, 48: 13000, 51: 12800, 60: 0. Slot 0 (796 draws) is excluded: M7
already ran it and the step title is "Second-slot". Same +0.1f translation on
the slot's 4th column (word 36*4+3 = 147), same pure-function shape (no
accumulation). Installed via `SSX_M8_SLOT=36`; `restored` reads `m8mode=2
m8slot=36`; all 200 rows tag `xform=1`.

Seam-application receipt (`xform_stats`):

| Field | Value |
| --- | --- |
| `mode` | 8 |
| `slot` | 36 |
| `calls` | 210000 (1050/replay = the run's `indexed` count) |
| `hits` | 10600 (53/replay covering word 147; every slot-36-covering write covers it) |
| `regcalls` | 0 |

Pixel quantification (per-replay scratch-vs-live-original diff over 573440
bytes; `xdiff` = differing bytes, `xdmax` = max abs byte diff, `xdmean` =
mean abs byte diff over differing bytes):

| Arm | differing frames (`200 − xfb_scratch_equal`) | xdiff min / max / mean | xdmax min / max | xdmean min / max |
| --- | ---: | --- | ---: | --- |
| m8-det3 | 0 | 0 / 0 / 0 | 0 / 0 | 0.000 / 0.000 |

Sample rows (replay: xdiff/xdmax/xdmean): 0: 0/0/0.000, 1: 0/0/0.000,
100: 0/0/0.000, 199: 0/0/0.000. `xdiff>0 replays = 0/200`.

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m8-det3 | dtex | 0 | 0 |
| m8-det3 | dpend | 0 | 0 |
| m8-det3 | dframe | 0 | 0 |
| m8-det3 | dafter | 1 | 1 |
| m8-det3 | dafter_live | 0 | 0 |
| m8-det3 | dpres | 0 | 0 |
| m8-det3 | dimx | 0 | 0 |
| m8-det3 | trig_imx | 0 | 0 |
| m8-det3 | pediff | 0 | 0 |
| m8-det3 | vidiff | 0 | 0 |
```

Sequence absolutes: tex 101→101, pend 0→0, fc 6878→6878, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=13751 first_imm_fc=6875`. The continuation `resume_xfb` listener
fired normally (see §Continuation check).

Recorded without verdict: `done` stands (watched-window re-hash clean);
`xfb_equal=200/200` (live range untouched) and `live_xfb_untouched=1`; guest
state unchanged (`pediff`/`vidiff` 0/0); event state unchanged
(`dafter_live`/`dframe`/`dpres`/`dimx` 0/0, `trig_imx` 0/0); the delta perturbed
xfmem 53 times per replay yet 0 of 200 replayed frames differ from the
original by any byte, with no drift across replays (xdiff flat 0 on rows
0…199). Per the runbook's step-3 clause, this second zero re-scopes the
finding from "wrong slot" to "seam writes don't reach rendering" — tabled as
the clause's outcome; the per-expression receipts below ride alongside it. No
leak into guest or event state is observed.

Own-frame census, m8-det3 (counting stays on in mode 2; same column
definitions as Step 2):

```
| slot | writes (tot) | writes/replay | reads (tot) | draws-affected |
| 0 | 14400 | 72.00 | 172800 | 611 |
| 1 | 14400 | 72.00 | 0 | 0 |
| 2 | 14400 | 72.00 | 0 | 0 |
| 3 | 12800 | 64.00 | 400 | 85 |
| 4 | 12800 | 64.00 | 0 | 0 |
| 5 | 12800 | 64.00 | 0 | 0 |
| 6 | 12000 | 60.00 | 400 | 76 |
| 7 | 12000 | 60.00 | 0 | 0 |
| 8 | 12000 | 60.00 | 0 | 0 |
| 9 | 12000 | 60.00 | 400 | 67 |
| 10 | 12000 | 60.00 | 0 | 0 |
| 11 | 12000 | 60.00 | 0 | 0 |
| 12 | 12000 | 60.00 | 400 | 57 |
| 13 | 12000 | 60.00 | 0 | 0 |
| 14 | 12000 | 60.00 | 0 | 0 |
| 15 | 12000 | 60.00 | 400 | 217 |
| 16 | 12000 | 60.00 | 0 | 0 |
| 17 | 12000 | 60.00 | 0 | 0 |
| 18 | 11800 | 59.00 | 400 | 65 |
| 19 | 11800 | 59.00 | 0 | 0 |
| 20 | 11800 | 59.00 | 0 | 0 |
| 21 | 11200 | 56.00 | 800 | 102 |
| 22 | 11200 | 56.00 | 0 | 0 |
| 23 | 11200 | 56.00 | 0 | 0 |
| 24 | 10600 | 53.00 | 200 | 108 |
| 25 | 10600 | 53.00 | 0 | 0 |
| 26 | 10600 | 53.00 | 0 | 0 |
| 27 | 10400 | 52.00 | 33800 | 93 |
| 28 | 10400 | 52.00 | 0 | 0 |
| 29 | 10400 | 52.00 | 0 | 0 |
| 30 | 13400 | 67.00 | 37600 | 951 |
| 31 | 13400 | 67.00 | 0 | 0 |
| 32 | 13400 | 67.00 | 0 | 0 |
| 33 | 9000 | 45.00 | 0 | 0 |
| 34 | 9000 | 45.00 | 0 | 0 |
| 35 | 9000 | 45.00 | 0 | 0 |
| 36 | 10600 | 53.00 | 210000 | 1481 |
| 37 | 10600 | 53.00 | 0 | 0 |
| 38 | 10600 | 53.00 | 0 | 0 |
| 39 | 9000 | 45.00 | 210000 | 1481 |
| 40 | 9000 | 45.00 | 0 | 0 |
| 41 | 9000 | 45.00 | 0 | 0 |
| 42 | 9000 | 45.00 | 210000 | 1481 |
| 43 | 9000 | 45.00 | 0 | 0 |
| 44 | 9000 | 45.00 | 0 | 0 |
| 45 | 9000 | 45.00 | 210000 | 1481 |
| 46 | 9000 | 45.00 | 0 | 0 |
| 47 | 9000 | 45.00 | 0 | 0 |
| 48 | 8800 | 44.00 | 210000 | 1481 |
| 49 | 8800 | 44.00 | 0 | 0 |
| 50 | 8800 | 44.00 | 0 | 0 |
| 51 | 8600 | 43.00 | 210000 | 1481 |
| 52 | 8600 | 43.00 | 0 | 0 |
| 53 | 8600 | 43.00 | 0 | 0 |
| 54 | 6800 | 34.00 | 0 | 0 |
| 55 | 6800 | 34.00 | 0 | 0 |
| 56 | 6800 | 34.00 | 0 | 0 |
| 57 | 6600 | 33.00 | 0 | 0 |
| 58 | 6600 | 33.00 | 0 | 0 |
| 59 | 6600 | 33.00 | 0 | 0 |
| 60 | 0 | 0.00 | 210000 | 1481 |
```

3 slots all-zero (61, 62, 63). Totals: writes 630000, reads 1717600, draws
12799. Slot 36 on its own frame: 53 writes/replay, reads on every seam sample
(210000/210000), draws-affected 1481/1481. The referenced-slot SET again
matches exactly between the two instruments (same 18 slots as det2).

Per-expression draw attribution, m8-det3 (`m8_expr0-8`; each expression
attributes its own slot independently; rows sum to 1481 = draws):

| Expr | Draws by slot |
| --- | --- |
| PosNormal | 0:611 3:85 6:76 9:67 12:57 15:217 18:65 21:102 24:108 27:93 |
| Tex0 | 30:951 60:530 |
| Tex1 | 60:1481 |
| Tex2 | 36:1481 |
| Tex3 | 39:1481 |
| Tex4 | 42:1481 |
| Tex5 | 45:1481 |
| Tex6 | 48:1481 |
| Tex7 | 51:1481 |

Recorded without verdict: PosNormal varies per object over triple-start slots
0-27 (slot 0: 611/1481 draws); Tex0 splits 30/60; Tex1-7 are constant
(60/36/39/42/45/48/51). Slot 36 is referenced only via Tex2MtxIdx. Frame-start
`numtex0=0x1` with `numtex_w=23` in-stream writes to XF 0x103f (numTexGens =
value & 0xF per `XFStructs.cpp:143-146`), so per-draw texgen enablement is not
settled by the frame-start value (see "What I could not do"). Position
transform path, for the record: `VertexShaderGen.cpp:104-123` transforms
positions via per-vertex `transformmatrices[posidx]` when the vertex format
carries POSMTXIDX, else via shared `posnormalmatrix`; per-texgen shared vs
indexed branch at `:161-200`, loop bounded by numTexGens. Per-draw VAT was not
decoded (see "What I could not do").

## Step 4 — projection-path reachability

Receipt: UNREACHABLE, by code path plus a targeted run that was orderable
within the box (mode 3 on the step-3 player: the projection-word delta
attempt plus its proof-of-non-application).

Code path (read-only; no vendor change). The seam has exactly two call sites
in the vendor tree (`grep g_transform` over
`third_party/ModernGekko/vendor/dolphin/Source/`):

| Site | Lines | Fires for |
| --- | --- | --- |
| `XFStructs.cpp:246-247` | inside `LoadXFReg`'s XF-mem branch | direct XF loads to words < 0x1000 only (the branch clamps at `XFMEM_REGISTERS_START`, `:234-238`) |
| `XFStructs.cpp:299-300` | inside `LoadIndexedXF` | indexed XF loads (unconditional on address) |

Supporting lines: declaration `XFMemory.h:472`, definition
`XFStructs.cpp:203`, early-out check `XFStructs.cpp:288`.
`LoadXFReg`'s regs branch (`XFStructs.cpp:250-262`) contains no `g_transform`
call: it runs `XFRegWritten` + the xfmem write per word and returns.
Projection lives at XF regs 0x1020-0x1026 (`XFMemory.h:226-232`), so every
direct projection write takes the regs branch and never fires the seam. The
render-side read exists (`VertexShaderManager::LoadProjectionMatrix` reads
`xfmem.projection.rawProjection`, `VertexShaderManager.cpp:41-65`, after
`XFRegWritten` sets projection-changed at `XFStructs.cpp:128-137`); the seam
side has no write path to it. The only hypothetical seam route to regs-range
words is an indexed load with address >= 0x1000 (the `LoadIndexedXF` call
site is address-unconditional) — measured below at zero.

Targeted run (m8-det4, `SSX_M8_PROJ=1`, same receipts as step 3):

| Field | Value |
| --- | --- |
| `mode` | 9 |
| `calls` | 514000 (2570/replay = the run's `indexed` count) |
| `hits` | 0 (no seam call covered a projection word) |
| `regcalls` | 0 (no seam call at addr >= 0x1000 in 514000 invocations) |
| `idx_reg` (stream side) | 0 (no indexed load covers regs) |
| `projreg_writes` (stream side) | 11 (projection IS written 11x/frame via the regs path — never through the seam) |

| Arm | differing frames | xdiff min / max / mean | xdmax min / max | xdmean min / max |
| --- | ---: | --- | ---: | --- |
| m8-det4 | 0 | 0 / 0 / 0 | 0 / 0 | 0.000 / 0.000 |

`xdiff>0 replays = 0/200` (no delta applied anywhere: the run is a no-op
replay by construction, same shape as M7's `full` no-op).

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m8-det4 | dtex | 0 | 1 |
| m8-det4 | dpend | 0 | 0 |
| m8-det4 | dframe | 0 | 0 |
| m8-det4 | dafter | 1 | 1 |
| m8-det4 | dafter_live | 0 | 0 |
| m8-det4 | dpres | 0 | 0 |
| m8-det4 | dimx | 0 | 0 |
| m8-det4 | trig_imx | 0 | 0 |
| m8-det4 | pediff | 0 | 0 |
| m8-det4 | vidiff | 0 | 0 |
```

Sequence absolutes: tex 98→99, pend 0→0, fc 7445→7445, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=14885 first_imm_fc=7442`.

Own-frame census, m8-det4 (same column definitions as Step 2):

```
| slot | writes (tot) | writes/replay | reads (tot) | draws-affected |
| 0 | 33600 | 168.00 | 482800 | 906 |
| 1 | 33600 | 168.00 | 0 | 0 |
| 2 | 33600 | 168.00 | 0 | 0 |
| 3 | 28800 | 144.00 | 400 | 85 |
| 4 | 28800 | 144.00 | 0 | 0 |
| 5 | 28800 | 144.00 | 0 | 0 |
| 6 | 26800 | 134.00 | 400 | 63 |
| 7 | 26800 | 134.00 | 0 | 0 |
| 8 | 26800 | 134.00 | 0 | 0 |
| 9 | 26600 | 133.00 | 600 | 123 |
| 10 | 26600 | 133.00 | 0 | 0 |
| 11 | 26600 | 133.00 | 0 | 0 |
| 12 | 25600 | 128.00 | 400 | 56 |
| 13 | 25600 | 128.00 | 0 | 0 |
| 14 | 25600 | 128.00 | 0 | 0 |
| 15 | 25400 | 127.00 | 400 | 92 |
| 16 | 25400 | 127.00 | 0 | 0 |
| 17 | 25400 | 127.00 | 0 | 0 |
| 18 | 24600 | 123.00 | 400 | 63 |
| 19 | 24600 | 123.00 | 0 | 0 |
| 20 | 24600 | 123.00 | 0 | 0 |
| 21 | 23400 | 117.00 | 1200 | 67 |
| 22 | 23400 | 117.00 | 0 | 0 |
| 23 | 23400 | 117.00 | 0 | 0 |
| 24 | 22800 | 114.00 | 400 | 49 |
| 25 | 22800 | 114.00 | 0 | 0 |
| 26 | 22800 | 114.00 | 0 | 0 |
| 27 | 21800 | 109.00 | 27000 | 67 |
| 28 | 21800 | 109.00 | 0 | 0 |
| 29 | 21800 | 109.00 | 0 | 0 |
| 30 | 32400 | 162.00 | 31600 | 776 |
| 31 | 32400 | 162.00 | 0 | 0 |
| 32 | 32400 | 162.00 | 0 | 0 |
| 33 | 26400 | 132.00 | 0 | 0 |
| 34 | 26400 | 132.00 | 0 | 0 |
| 35 | 26400 | 132.00 | 0 | 0 |
| 36 | 30400 | 152.00 | 514000 | 1571 |
| 37 | 30400 | 152.00 | 0 | 0 |
| 38 | 30400 | 152.00 | 0 | 0 |
| 39 | 26400 | 132.00 | 514000 | 1571 |
| 40 | 26400 | 132.00 | 0 | 0 |
| 41 | 26400 | 132.00 | 0 | 0 |
| 42 | 26200 | 131.00 | 514000 | 1571 |
| 43 | 26200 | 131.00 | 0 | 0 |
| 44 | 26200 | 131.00 | 0 | 0 |
| 45 | 25800 | 129.00 | 514000 | 1571 |
| 46 | 25800 | 129.00 | 0 | 0 |
| 47 | 25800 | 129.00 | 0 | 0 |
| 48 | 25000 | 125.00 | 514000 | 1571 |
| 49 | 25000 | 125.00 | 0 | 0 |
| 50 | 25000 | 125.00 | 0 | 0 |
| 51 | 24800 | 124.00 | 514000 | 1571 |
| 52 | 24800 | 124.00 | 0 | 0 |
| 53 | 24800 | 124.00 | 0 | 0 |
| 54 | 19000 | 95.00 | 0 | 0 |
| 55 | 19000 | 95.00 | 0 | 0 |
| 56 | 19000 | 95.00 | 0 | 0 |
| 57 | 18200 | 91.00 | 0 | 0 |
| 58 | 18200 | 91.00 | 0 | 0 |
| 59 | 18200 | 91.00 | 0 | 0 |
| 60 | 0 | 0.00 | 514000 | 1571 |
```

3 slots all-zero (61, 62, 63). Totals: writes 1542000, reads 4143600, draws
13344. Same triple structure, same 18-slot referenced set, same 7-way
all-draws tie (36/39/42/45/48/51/60) as det2/det3. Slot 36 here: 152
writes/replay.

Per-expression draw attribution, m8-det4 (rows sum to 1571 = draws):

| Expr | Draws by slot |
| --- | --- |
| PosNormal | 0:906 3:85 6:63 9:123 12:56 15:92 18:63 21:67 24:49 27:67 |
| Tex0 | 30:776 60:795 |
| Tex1 | 60:1571 |
| Tex2 | 36:1571 |
| Tex3 | 39:1571 |
| Tex4 | 42:1571 |
| Tex5 | 45:1571 |
| Tex6 | 48:1571 |
| Tex7 | 51:1571 |

Frame-start `numtex0=0x1`, `numtex_w=26`, `idxa0=0x2793cf00 idxb0=0x00cf0b6a`
(identical to det3's frame-start hexes). `walk_ok=1`, `benign=1`.

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m8-det | `fc=5895` | `replay_disabled=0 fc=5898 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m8-det2 | `fc=6533` | `replay_disabled=0 fc=6536 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m8-det3 | `fc=6875` | `replay_disabled=0 fc=6878 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m8-det4 | `fc=7442` | `replay_disabled=0 fc=7445 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ); the
quadruple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same address and
size, also identical to all M7 sequence hashes and all M6 sequence and M5
sequence/disabled hashes) is tabulated as observed. `resume fc − fc0 = 3` in
each run (the live record window; per-replay `dframe` sums are 0/0/0/0).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest and
event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m8-det | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m8-det2 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m8-det3 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m8-det4 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

## Exact commands

Builds (any time; only the header path differs from
`local/research/M7/build_replay_player.py`):

```
python3 local/research/M8/build_replay_player.py local/research/M8/players/m8-baseline
python3 local/research/M8/build_replay_player.py local/research/M8/players/m8-census
python3 local/research/M8/build_replay_player.py local/research/M8/players/m8-delta
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M8\n'`, remove after
each run; profiles fresh per run):

```
SSX_M7_XFORM=delta SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m8/m8-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M8/players/m8-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m8-det --cpu-thread --output "/Volumes/Extreme SSD/m8/m8-det-run" --seconds 240
SSX_M8_CENSUS=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m8/m8-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M8/players/m8-census --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m8-det2 --cpu-thread --output "/Volumes/Extreme SSD/m8/m8-det2-run" --seconds 240
SSX_M8_SLOT=36 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m8/m8-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M8/players/m8-delta --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m8-det3 --cpu-thread --output "/Volumes/Extreme SSD/m8/m8-det3-run" --seconds 240
SSX_M8_PROJ=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m8/m8-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M8/players/m8-delta --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m8-det4 --cpu-thread --output "/Volumes/Extreme SSD/m8/m8-det4-run" --seconds 240
```

Analysis:

```
python3 local/research/M8/analyze.py "m8-det=/Volumes/Extreme SSD/m8/m8-det-probe.jsonl" "m8-det2=/Volumes/Extreme SSD/m8/m8-det2-probe.jsonl" "m8-det3=/Volumes/Extreme SSD/m8/m8-det3-probe.jsonl" "m8-det4=/Volumes/Extreme SSD/m8/m8-det4-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M8/` — `m8_replay_context.h`
(`c98e5582…`), `build_replay_player.py`, `analyze.py`, `REPORT.md`, `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m8/` —
`m8-det-probe.jsonl`, `m8-det2-probe.jsonl`, `m8-det3-probe.jsonl`,
`m8-det4-probe.jsonl` (~21 MB each) and the matching `-run` dirs and `-run.log`
harness receipts; `analyze-all.txt` (the four-arm analyzer output);
per-step header snapshots `m8_replay_context.step1.h`,
`m8_replay_context.step2.h`, `m8_replay_context.step3.h` (= committed header).
Players (gitignored): `local/research/M8/players/{m8-baseline,m8-census,
m8-delta}/` (each with `player`, `build.json`, launchers). All paths
above are symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` / `player_sha256`,
12-char prefixes): `m8-baseline` `0bfc48602573` / `e41afcc3b33a` (player hash
identical to M7's `m7-delta`: same header compiles to the same binary),
`m8-census` `b8f280484e9a` / `fb868300d275`,
`m8-delta` `c98e55821293` / `ac4fe91bfc6f`.

## What I could not do

- Per-vertex matrix indices (`pnmtxidx` into `transformmatrices`) are not
  decoded: draws are attributed via matrix-index state only. Positions take
  the indexed path whenever the vertex format carries POSMTXIDX
  (`VertexShaderGen.cpp:104-116`) and the shared `posnormalmatrix` path
  otherwise (`:117-123`); texcoords branch per texgen the same way (`:161-200`,
  loop bounded by numTexGens). Which draws take which path is not in the
  receipts.
- Per-draw VAT / vertex-format path was not decoded (the walker sees each
  draw's `vat` but does not map CP VAT state to `VB_HAS_POSMTXIDX` /
  `VB_HAS_TEXMTXIDXi`), so the shared-vs-indexed position split per draw is
  unknown.
- Per-draw texgen enablement was not tracked: `numtex_w` (23 on det3, 26 on
  det4) in-stream writes to XF 0x103f change numTexGens mid-frame, so the
  frame-start `numtex0=0x1` does not settle which of Tex1-7 are enabled on
  any given draw.
- No follow-up delta run on any other slot (e.g. slot 30 = Tex0 on 776-951
  draws): step 3 prescribes one second slot and its re-scope clause covers
  the zero outcome. Ordered follow-up beyond this runbook, not a gap in it.
- The step-2 `walk_ok=0` (missing benign split; validity cross-checked via
  `consumed == size` and `stream_indexed == mask.indexed`) was fixed in the
  step-3 header rather than re-run; the step-2 receipts stand as recorded.
- Player dirs are under `local/research/M8/players/` rather than the SSD: the
  build driver refuses outputs outside `local/`, and the brief orders changing
  only the header path it compiles in. Run dirs and all >5 MB probes are on
  the SSD as ordered.
- Desktop only; no device work.

## Files

Committed under `local/research/M8/`: `m8_replay_context.h` (research header,
`c98e5582…`), `build_replay_player.py` (M7 driver, header path only),
`analyze.py` (M7 tables unchanged + M8 `m8_meta`/`m8_writes`/`m8_reads`/
`m8_draws`/`m8_expr0-8` parsing, slot census tables, per-expression tables,
xdiff distribution rows; missing keys print as n/a / sections skipped),
`REPORT.md` (this file), `waits.log` (one P1n wait, four claim/release pairs).

## Header diffs per step (`diff -u` against the M7 header)

Step 1: empty (verbatim copy). Steps 2-3 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m8/m8_replay_context.step2.h` and
the committed `local/research/M8/m8_replay_context.h` (= step 3).

### Step 2

```diff
--- local/research/M7/m7_replay_context.h	2026-09-19 00:45:24
+++ /Volumes/Extreme SSD/m8/m8_replay_context.step2.h	2026-09-19 07:38:44
@@ -548,7 +548,108 @@
   if (stats.consumed != out.size() || stats.unknown != 0) {
     out = src;  // fail closed: preprocess the verbatim stream instead
     stats.masked = 0;
+  }
+  return stats;
+}
+
+// --- M8 step 2: stream-epoch census walk ------------------------------------
+// Read-only decode of the verbatim recorded stream (no mutation; own CPState
+// seeded from the recorded registers like PeMaskWalk). Counts draws, tracks
+// matrix-index epochs through CP and XF writes, attributes draws to the slots
+// the live index state references. Deadline-free setup cost (~one decode).
+struct M8Census {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 epochs = 0;  // index-state transitions observed at draws, +1 (0 if no draws)
+  u32 matidx_cp = 0;  // CP 0x30/0x40 writes in the stream
+  u32 matidx_xf = 0;  // XF 0x1018/0x1019 words in the stream
+  u32 direct_xfmem = 0;  // direct XF commands touching words < 0x1000
+  u32 direct_pos_words = 0;  // of those, words in the pos-matrix range
+  u32 indexed = 0;
+  u32 idx_pos = 0;  // indexed loads covering >= 1 pos-matrix word
+  u32 idx_reg = 0;  // indexed loads covering regs (expect 0)
+  u32 projreg_writes = 0;  // direct XF commands covering 0x1020-0x1026
+  u32 unknown = 0;
+  u64 draws_aff[64] = {};
+};
+class M8CensusWalk final : public OpcodeDecoder::Callback {
+public:
+  M8CensusWalk(const u32* cp_mem, M8Census& stats) : m_cp(cp_mem), m_stats(stats) {}
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address, hi = u32(address) + u32(count);
+    if (lo < 0x1000) {
+      ++m_stats.direct_xfmem;
+      const u32 plo = lo < 0x100 ? lo : 0x100;
+      const u32 phi = hi < 0x100 ? hi : 0x100;
+      if (phi > plo) m_stats.direct_pos_words += phi - plo;
+    }
+    if (lo <= XFMEM_SETPROJECTION + 6 && hi > XFMEM_SETPROJECTION)
+      ++m_stats.projreg_writes;
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      if (word != XFMEM_SETMATRIXINDA && word != XFMEM_SETMATRIXINDB) continue;
+      // Stream words are big-endian; LoadXFReg applies Common::swap32 per word.
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      // Mirror the SetTexMatrixChangedA/B write-through to CP state.
+      if (word == XFMEM_SETMATRIXINDA)
+        m_cp.matrix_index_a.Hex = v;
+      else
+        m_cp.matrix_index_b.Hex = v;
+      ++m_stats.matidx_xf;
+    }
+  }
+  void OnCP(u8 command, u32 value) override {
+    m_cp.LoadCPReg(command, value);
+    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
   }
+  void OnBP(u8, u32) override {}
+  void OnIndexedLoad(CPArray, u32, u16 address, u8 size) override {
+    ++m_stats.indexed;
+    const u32 lo = address, hi = u32(address) + u32(size);
+    if (lo < 0x100) ++m_stats.idx_pos;
+    if (hi > 0x1000) ++m_stats.idx_reg;
+  }
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    if (m_stats.draws == 1) {
+      m_stats.epochs = 1;
+    } else if (ia != m_idx_a || ib != m_idx_b) {
+      ++m_stats.epochs;
+    }
+    m_idx_a = ia;
+    m_idx_b = ib;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    for (u32 k = 0; k < 9; ++k) {
+      bool seen = false;
+      for (u32 j = 0; j < k; ++j)
+        if (idx[j] == idx[k]) seen = true;
+      if (!seen) ++m_stats.draws_aff[idx[k]];
+    }
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8, const u8*) override { ++m_stats.unknown; }
+  void OnCommand(const u8*, u32) override {}
+  CPState& GetCPState() override { return m_cp; }
+
+private:
+  CPState m_cp;
+  M8Census& m_stats;
+  u32 m_idx_a = 0, m_idx_b = 0;
+};
+static M8Census RunM8Census(const std::vector<u8>& src, const u32* cp_mem) {
+  M8Census stats;
+  if (src.empty()) return stats;
+  M8CensusWalk walk(cp_mem, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
   return stats;
 }
 
@@ -658,6 +759,47 @@
     float* w = &xfmem.posMatrices[3];
     *w += 0.1f;
     ++s_m7_xform_hits;
+  }
+}
+// --- M8 step 2: slot-usage census -------------------------------------------
+// Why M7's 152 seam hits move zero pixels: which XF position-matrix slots
+// (0-63, words 0x000-0x0FF) actually feed visible draws? Three instruments,
+// all env-gated (SSX_M8_CENSUS=1; unset = exact M7 behavior):
+//   (a) seam write counts: M8Transform tallies, per call, every pos slot
+//       overlapped by [address, address+count). Mode 1 applies no delta.
+//   (b) index-state reads: on each seam call the transform also samples the
+//       exact matrix-index expressions VertexShaderManager::SetConstants reads
+//       (g_main_cp_state.matrix_index_a/b: PosNormalMtxIdx, Tex0-7MtxIdx;
+//       VertexShaderManager.cpp:292,307-310,324-327) and tallies each distinct
+//       referenced slot. All nine are 6-bit pos-slot indices (& 0x3f); the
+//       normal-matrix (&31) sub-path is not separately tabled.
+//   (c) stream-epoch draws: M8CensusWalk (next to PeMaskWalk) decodes the
+//       verbatim recorded stream once at setup, tracking matrix-index state
+//       through CP 0x30/0x40 writes (CPState::LoadCPReg) and XF 0x1018/0x1019
+//       writes (XFStateManager::SetTexMatrixChangedA/B write-through to the
+//       same CP state), attributing every primitive command to the slots the
+//       live index state references. Per-vertex pnmtxidx (the
+//       transformmatrices indexed path) is NOT decoded (see report).
+// (Step 3 arms the slot/proj delta in this same transform; step 2 counts only.)
+static unsigned long long s_m8_calls = 0;
+static unsigned long long s_m8_writes[64] = {};
+static unsigned long long s_m8_reads[64] = {};
+static void M8Transform(u16 address, u32 count) {
+  ++s_m8_calls;
+  const u32 lo = address, hi = address + count;  // covered words [lo, hi)
+  for (u32 s = 0; s < 64; ++s) {
+    if (lo < s * 4 + 4 && hi > s * 4) ++s_m8_writes[s];
+  }
+  const u32 ia = g_main_cp_state.matrix_index_a.Hex;
+  const u32 ib = g_main_cp_state.matrix_index_b.Hex;
+  const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                      (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                      (ib >> 18) & 63};
+  for (u32 k = 0; k < 9; ++k) {
+    bool seen = false;
+    for (u32 j = 0; j < k; ++j)
+      if (idx[j] == idx[k]) seen = true;
+    if (!seen) ++s_m8_reads[idx[k]];
   }
 }
 
@@ -824,6 +966,17 @@
   // Always built (the counters are the receipt for the aux-budget arithmetic);
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
+  // M8 step 2: census select (parsed early: the stream walk runs at setup).
+  // Unset = exact M7 behavior.
+  const int m8_census = [] {
+    const char* v = std::getenv("SSX_M8_CENSUS");
+    return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+  }();
+  // M8 step 2: stream-epoch census over the verbatim recorded stream. The XFB
+  // scratch patch touches BP dest addresses only, so verbatim and executed
+  // streams agree on draws and index state.
+  const M8Census m8stream =
+      m8_census ? RunM8Census(frame, file->GetCPMem()) : M8Census{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -943,14 +1096,14 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8census=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n, int(m7_no_suppress), m7_xform);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_census);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1024,6 +1177,14 @@
     s_m7_xform_hits = 0;
     XFReplay::g_transform = &M7DeltaTransform;
   }
+  // M8 step 2: census transform (counts only, no delta). Overrides the M7
+  // select above when set; unset = M7 behavior.
+  if (m8_census == 1) {
+    s_m8_calls = 0;
+    for (auto& w : s_m8_writes) w = 0;
+    for (auto& r : s_m8_reads) r = 0;
+    XFReplay::g_transform = &M8Transform;
+  }
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -1043,7 +1204,7 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom && m7_xform == 0)
+    if (replays == kTransformFrom && m7_xform == 0 && m8_census == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     ApplyMemory(system, file);
     const double t_mem = Now();
@@ -1172,7 +1333,7 @@
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
     // M7 step 2: tag actual install state (default mode identical to M6).
-    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0);
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_census != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1259,6 +1420,49 @@
     std::snprintf(xs, sizeof(xs), "mode=%d calls=%llu hits=%llu", m7_xform,
                   s_m7_xform_calls, s_m7_xform_hits);
     Event("xform_stats", xs);
+  }
+  // M8 step 2: slot-usage census receipts (census mode only). xform_stats
+  // carries the seam-invocation count (no delta word in census mode);
+  // m8_meta carries the stream-epoch census; m8_writes/m8_reads/m8_draws
+  // carry the 64-slot CSVs (slot order 0..63).
+  if (m8_census == 1) {
+    char xs[128];
+    std::snprintf(xs, sizeof(xs), "mode=7 slot=-1 calls=%llu hits=0", s_m8_calls);
+    Event("xform_stats", xs);
+    char meta[320];
+    std::snprintf(
+        meta, sizeof(meta),
+        "mode=1 draws=%u verts=%llu epochs=%u matidx_cp=%u matidx_xf=%u "
+        "direct_xfmem=%u direct_pos_words=%u stream_indexed=%u idx_pos=%u idx_reg=%u "
+        "projreg_writes=%u walk=%u/%zu walk_ok=%d",
+        m8stream.draws, (unsigned long long)m8stream.verts, m8stream.epochs,
+        m8stream.matidx_cp, m8stream.matidx_xf, m8stream.direct_xfmem,
+        m8stream.direct_pos_words, m8stream.indexed, m8stream.idx_pos, m8stream.idx_reg,
+        m8stream.projreg_writes, m8stream.consumed, frame.size(),
+        int(m8stream.consumed == frame.size() && m8stream.unknown == 0));
+    Event("m8_meta", meta);
+    char csv[2048];
+    int off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           s_m8_writes[s]);
+    }
+    Event("m8_writes", csv);
+    off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           s_m8_reads[s]);
+    }
+    Event("m8_reads", csv);
+    off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           (unsigned long long)m8stream.draws_aff[s]);
+    }
+    Event("m8_draws", csv);
   }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
```

### Step 3 (= committed header; step 4 adds no header change — mode 3 ships in this header)

```diff
--- local/research/M7/m7_replay_context.h	2026-09-19 00:45:24
+++ local/research/M8/m8_replay_context.h	2026-09-19 07:50:38
@@ -552,6 +552,127 @@
   return stats;
 }
 
+// --- M8 step 2: stream-epoch census walk ------------------------------------
+// Read-only decode of the verbatim recorded stream (no mutation; own CPState
+// seeded from the recorded registers like PeMaskWalk). Counts draws, tracks
+// matrix-index epochs through CP and XF writes, attributes draws to the slots
+// the live index state references. Deadline-free setup cost (~one decode).
+struct M8Census {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 epochs = 0;  // index-state transitions observed at draws, +1 (0 if no draws)
+  u32 matidx_cp = 0;  // CP 0x30/0x40 writes in the stream
+  u32 matidx_xf = 0;  // XF 0x1018/0x1019 words in the stream
+  u32 direct_xfmem = 0;  // direct XF commands touching words < 0x1000
+  u32 direct_pos_words = 0;  // of those, words in the pos-matrix range
+  u32 indexed = 0;
+  u32 idx_pos = 0;  // indexed loads covering >= 1 pos-matrix word
+  u32 idx_reg = 0;  // indexed loads covering regs (expect 0)
+  u32 projreg_writes = 0;  // direct XF commands covering 0x1020-0x1026
+  u32 numtex_w = 0;  // in-stream writes to XF 0x103f (SETNUMTEXGENS)
+  u32 numtex0 = 0;  // recorded frame-start value of XF 0x103f
+  u32 idxa0 = 0, idxb0 = 0;  // recorded frame-start CP matrix-index hexes
+  u32 benign = 0;  // 0x44 / 0x48 (step-3 fix: step 2 counted these as unknown)
+  u32 unknown = 0;
+  u64 draws_aff[64] = {};
+  // M8 step 3: per-expression draw attribution (0=PosNormal, 1-8=Tex0-7).
+  // Each expression attributes its own slot independently (no cross-expression
+  // dedupe); draws_aff above keeps the per-draw dedupe.
+  u64 expr[9][64] = {};
+};
+class M8CensusWalk final : public OpcodeDecoder::Callback {
+public:
+  M8CensusWalk(const u32* cp_mem, M8Census& stats) : m_cp(cp_mem), m_stats(stats) {}
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address, hi = u32(address) + u32(count);
+    if (lo < 0x1000) {
+      ++m_stats.direct_xfmem;
+      const u32 plo = lo < 0x100 ? lo : 0x100;
+      const u32 phi = hi < 0x100 ? hi : 0x100;
+      if (phi > plo) m_stats.direct_pos_words += phi - plo;
+    }
+    if (lo <= XFMEM_SETPROJECTION + 6 && hi > XFMEM_SETPROJECTION)
+      ++m_stats.projreg_writes;
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      if (word == XFMEM_SETNUMTEXGENS) ++m_stats.numtex_w;
+      if (word != XFMEM_SETMATRIXINDA && word != XFMEM_SETMATRIXINDB) continue;
+      // Stream words are big-endian; LoadXFReg applies Common::swap32 per word.
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      // Mirror the SetTexMatrixChangedA/B write-through to CP state.
+      if (word == XFMEM_SETMATRIXINDA)
+        m_cp.matrix_index_a.Hex = v;
+      else
+        m_cp.matrix_index_b.Hex = v;
+      ++m_stats.matidx_xf;
+    }
+  }
+  void OnCP(u8 command, u32 value) override {
+    m_cp.LoadCPReg(command, value);
+    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
+  }
+  void OnBP(u8, u32) override {}
+  void OnIndexedLoad(CPArray, u32, u16 address, u8 size) override {
+    ++m_stats.indexed;
+    const u32 lo = address, hi = u32(address) + u32(size);
+    if (lo < 0x100) ++m_stats.idx_pos;
+    if (hi > 0x1000) ++m_stats.idx_reg;
+  }
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    if (m_stats.draws == 1) {
+      m_stats.epochs = 1;
+    } else if (ia != m_idx_a || ib != m_idx_b) {
+      ++m_stats.epochs;
+    }
+    m_idx_a = ia;
+    m_idx_b = ib;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    for (u32 k = 0; k < 9; ++k) {
+      ++m_stats.expr[k][idx[k]];  // M8 step 3: per-expression, no dedupe
+      bool seen = false;
+      for (u32 j = 0; j < k; ++j)
+        if (idx[j] == idx[k]) seen = true;
+      if (!seen) ++m_stats.draws_aff[idx[k]];
+    }
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8 opcode, const u8*) override {
+    // Mirror PeMaskWalk: 0x44/0x48 are known-but-ignored single bytes.
+    if (opcode == 0x44 || opcode == 0x48)
+      ++m_stats.benign;
+    else
+      ++m_stats.unknown;
+  }
+  void OnCommand(const u8*, u32) override {}
+  CPState& GetCPState() override { return m_cp; }
+
+private:
+  CPState m_cp;
+  M8Census& m_stats;
+  u32 m_idx_a = 0, m_idx_b = 0;
+};
+static M8Census RunM8Census(const std::vector<u8>& src, const u32* cp_mem,
+                            const u32* xf_regs) {
+  M8Census stats;
+  stats.numtex0 = xf_regs[0x3f];  // 0x103f - 0x1000
+  stats.idxa0 = cp_mem[MATINDEX_A];
+  stats.idxb0 = cp_mem[MATINDEX_B];
+  if (src.empty()) return stats;
+  M8CensusWalk walk(cp_mem, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
+  return stats;
+}
+
 // Snapshot of the live video registers, restored after the sequence so the
 // game's own command stream keeps decoding with the state it expects.
 struct LiveState {
@@ -660,6 +781,76 @@
     ++s_m7_xform_hits;
   }
 }
+// --- M8 step 2: slot-usage census -------------------------------------------
+// Why M7's 152 seam hits move zero pixels: which XF position-matrix slots
+// (0-63, words 0x000-0x0FF) actually feed visible draws? Three instruments,
+// all env-gated (SSX_M8_CENSUS=1; unset = exact M7 behavior):
+//   (a) seam write counts: M8Transform tallies, per call, every pos slot
+//       overlapped by [address, address+count). Mode 1 applies no delta.
+//   (b) index-state reads: on each seam call the transform also samples the
+//       exact matrix-index expressions VertexShaderManager::SetConstants reads
+//       (g_main_cp_state.matrix_index_a/b: PosNormalMtxIdx, Tex0-7MtxIdx;
+//       VertexShaderManager.cpp:292,307-310,324-327) and tallies each distinct
+//       referenced slot. All nine are 6-bit pos-slot indices (& 0x3f); the
+//       normal-matrix (&31) sub-path is not separately tabled.
+//   (c) stream-epoch draws: M8CensusWalk (next to PeMaskWalk) decodes the
+//       verbatim recorded stream once at setup, tracking matrix-index state
+//       through CP 0x30/0x40 writes (CPState::LoadCPReg) and XF 0x1018/0x1019
+//       writes (XFStateManager::SetTexMatrixChangedA/B write-through to the
+//       same CP state), attributing every primitive command to the slots the
+//       live index state references. Per-vertex pnmtxidx (the
+//       transformmatrices indexed path) is NOT decoded (see report).
+// M8 step 3: the slot/proj delta arms live in this same transform (counting
+// stays on in every M8 mode, so each delta run carries its own census).
+// Mode 2 (SSX_M8_SLOT=N): the M7 +0.1f tx delta retargeted to slot N's 4th
+// column (word N*4+3), same pure-function-of-(address,value) shape (no
+// accumulation: each replay reloads from identical sources first).
+// Mode 3 (SSX_M8_PROJ=1): a +0.1f delta on the projection words (XF regs
+// 0x1020-0x1026), applied IF a seam call ever covers one. LoadXFReg's regs
+// branch never fires the seam (XFStructs.cpp:250-262 has no g_transform call),
+// so regcalls/hits are expected 0: the run is the attempt plus the proof.
+static unsigned long long s_m8_calls = 0;
+static unsigned long long s_m8_hits = 0;
+static unsigned long long s_m8_regcalls = 0;  // seam calls at addr >= 0x1000
+static unsigned long long s_m8_writes[64] = {};
+static unsigned long long s_m8_reads[64] = {};
+static int s_m8_slot = -1;  // mode-2 target slot, else -1
+static int s_m8_proj = 0;   // mode-3 flag
+static void M8Transform(u16 address, u32 count) {
+  ++s_m8_calls;
+  const u32 lo = address, hi = address + count;  // covered words [lo, hi)
+  if (lo >= 0x1000) ++s_m8_regcalls;
+  for (u32 s = 0; s < 64; ++s) {
+    if (lo < s * 4 + 4 && hi > s * 4) ++s_m8_writes[s];
+  }
+  const u32 ia = g_main_cp_state.matrix_index_a.Hex;
+  const u32 ib = g_main_cp_state.matrix_index_b.Hex;
+  const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                      (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                      (ib >> 18) & 63};
+  for (u32 k = 0; k < 9; ++k) {
+    bool seen = false;
+    for (u32 j = 0; j < k; ++j)
+      if (idx[j] == idx[k]) seen = true;
+    if (!seen) ++s_m8_reads[idx[k]];
+  }
+  if (s_m8_slot >= 0) {
+    const u32 w = u32(s_m8_slot) * 4 + 3;
+    if (lo <= w && w < hi) {
+      xfmem.posMatrices[w] += 0.1f;
+      ++s_m8_hits;
+    }
+  }
+  if (s_m8_proj) {
+    for (u32 p = XFMEM_SETPROJECTION; p <= XFMEM_SETPROJECTION + 6; ++p) {
+      if (lo <= p && p < hi) {
+        float* w = reinterpret_cast<float*>(&((u32*)&xfmem)[p]);
+        *w += 0.1f;
+        ++s_m8_hits;
+      }
+    }
+  }
+}
 
 static inline void Step(CPUState& c) {
   NativeSchedule::Step(c);
@@ -824,6 +1015,35 @@
   // Always built (the counters are the receipt for the aux-budget arithmetic);
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
+  // M8 steps 2-3: mode select (parsed early: the stream walk runs at setup).
+  // 0 = unset = exact M7 behavior; 1 = census (SSX_M8_CENSUS=1, counts only);
+  // 2 = slot delta (SSX_M8_SLOT=N, 0-63); 3 = projection attempt (SSX_M8_PROJ=1).
+  // Precedence: SLOT > PROJ > CENSUS. Counting stays on in every M8 mode.
+  const int m8_slot = [] {
+    const char* v = std::getenv("SSX_M8_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m8_proj = [] {
+    const char* v = std::getenv("SSX_M8_PROJ");
+    return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+  }();
+  const int m8_mode = m8_slot >= 0 ? 2 : (m8_proj ? 3 : ([] {
+                        const char* v = std::getenv("SSX_M8_CENSUS");
+                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                      })());
+  // M8 step 2: stream-epoch census over the verbatim recorded stream. The XFB
+  // scratch patch touches BP dest addresses only, so verbatim and executed
+  // streams agree on draws and index state.
+  const M8Census m8stream = m8_mode != 0 ? RunM8Census(frame, file->GetCPMem(),
+                                                       file->GetXFRegs())
+                                         : M8Census{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -943,14 +1163,14 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n, int(m7_no_suppress), m7_xform);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1024,6 +1244,18 @@
     s_m7_xform_hits = 0;
     XFReplay::g_transform = &M7DeltaTransform;
   }
+  // M8 steps 2-3: census/slot/proj transform (counting always on; delta
+  // arms per mode). Overrides the M7 select above when set; unset = M7 behavior.
+  if (m8_mode != 0) {
+    s_m8_calls = 0;
+    s_m8_hits = 0;
+    s_m8_regcalls = 0;
+    for (auto& w : s_m8_writes) w = 0;
+    for (auto& r : s_m8_reads) r = 0;
+    s_m8_slot = m8_mode == 2 ? m8_slot : -1;
+    s_m8_proj = m8_mode == 3 ? 1 : 0;
+    XFReplay::g_transform = &M8Transform;
+  }
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -1043,7 +1275,7 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom && m7_xform == 0)
+    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     ApplyMemory(system, file);
     const double t_mem = Now();
@@ -1172,7 +1404,7 @@
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
     // M7 step 2: tag actual install state (default mode identical to M6).
-    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0);
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1259,6 +1491,65 @@
     std::snprintf(xs, sizeof(xs), "mode=%d calls=%llu hits=%llu", m7_xform,
                   s_m7_xform_calls, s_m7_xform_hits);
     Event("xform_stats", xs);
+  }
+  // M8 steps 2-3: slot-usage census receipts (every M8 mode: each delta run
+  // carries its own census). xform_stats mode 7/8/9 = census/slot/proj;
+  // m8_meta carries the stream-epoch census; m8_writes/m8_reads/m8_draws carry
+  // the 64-slot CSVs (slot order 0..63); m8_expr0-8 carry the per-expression
+  // draw histograms (0=PosNormal, 1-8=Tex0-7).
+  if (m8_mode != 0) {
+    char xs[160];
+    std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
+                  m8_mode == 1 ? 7 : (m8_mode == 2 ? 8 : 9), s_m8_slot, s_m8_calls,
+                  s_m8_hits, s_m8_regcalls);
+    Event("xform_stats", xs);
+    char meta[448];
+    std::snprintf(
+        meta, sizeof(meta),
+        "mode=%d draws=%u verts=%llu epochs=%u matidx_cp=%u matidx_xf=%u "
+        "direct_xfmem=%u direct_pos_words=%u stream_indexed=%u idx_pos=%u idx_reg=%u "
+        "projreg_writes=%u numtex0=0x%x numtex_w=%u idxa0=0x%08x idxb0=0x%08x "
+        "walk=%u/%zu benign=%u walk_ok=%d",
+        m8_mode, m8stream.draws, (unsigned long long)m8stream.verts, m8stream.epochs,
+        m8stream.matidx_cp, m8stream.matidx_xf, m8stream.direct_xfmem,
+        m8stream.direct_pos_words, m8stream.indexed, m8stream.idx_pos, m8stream.idx_reg,
+        m8stream.projreg_writes, m8stream.numtex0, m8stream.numtex_w, m8stream.idxa0,
+        m8stream.idxb0, m8stream.consumed, frame.size(), m8stream.benign,
+        int(m8stream.consumed == frame.size() && m8stream.unknown == 0));
+    Event("m8_meta", meta);
+    char csv[2048];
+    int off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           s_m8_writes[s]);
+    }
+    Event("m8_writes", csv);
+    off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           s_m8_reads[s]);
+    }
+    Event("m8_reads", csv);
+    off = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+      off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                           (unsigned long long)m8stream.draws_aff[s]);
+    }
+    Event("m8_draws", csv);
+    for (u32 e = 0; e < 9; ++e) {
+      off = 0;
+      for (u32 s = 0; s < 64; ++s) {
+        if (off < 0 || size_t(off) >= sizeof(csv) - 24) break;
+        off += std::snprintf(csv + off, sizeof(csv) - size_t(off), "%s%llu", s ? "," : "",
+                             (unsigned long long)m8stream.expr[e][s]);
+      }
+      char ename[16];
+      std::snprintf(ename, sizeof(ename), "m8_expr%u", e);
+      Event(ename, csv);
+    }
   }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
```
