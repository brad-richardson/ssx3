# M10 — Discriminating instruments: hit/draw order, full matrices, render targets: REPORT

Hit/draw stream order, 12-word matrix values, per-draw render-target epochs
and occlusion classes for the M9 slot-0 residue, plus the pixel-compare
controls the M10 runs forced: NOP-collective arms, a forced-RAM arm, and a
rendered-reference true-delta arm. Desktop only. Runbook
`local/muse/prompts/M10.md`. No `adb`, no device. Tables, no verdicts.

Header read first: `local/research/M9/REPORT.md` (all of it: the narrowed
residue — 21 Tex2 + 800 Pos draws consume perturbed snapshots with 0 pixels
differing — and "What I could not do" items 1, 3–6, which specify the
instruments this brief builds) and the base header
`local/research/M9/m9_replay_context.h`.

Time box 6 hours; used about 1.6. Zero lease waits (nine claim/release
pairs plus two annotations; the P1q agent never observed holding the lease;
never forced).

## Baseline note (read before the tables)

The M9 header on disk (`local/research/M9/m9_replay_context.h`, clean tree)
hashes to `418f9113600eb16e0d2208be6cb85144c494a37739482451de5b2c57aee9827a`
via `shasum -a 256` (trust `shasum`, not memory; matches the M9 report's
pinned prefix).
Step 1 copied the on-disk file verbatim to
`local/research/M10/m10_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8/M9 mechanism is kept in all
steps: PE mask, verbatim execute stream, restore, stall, pipe snapshot,
watched-window re-hash, `done`, XFB hash + scratch redirect, side-effect
counters, continuation capture, scoped bus, `m6frame`, presenter tracing,
record guard, trig_imx probe, M7 full/delta transforms, per-replay xdiff
stats, M8 census/slot/proj modes with stream-epoch census, M9 VAT walk +
slot/survival. All M10 additions are env-gated with defaults that preserve
M9 behavior (`SSX_M10_SLOT` unset); the committed header is the step-3
header, from which every step's run is reproducible via env.

M10 modes (`SSX_M10_SLOT=N`, 0-63, forces M9 mode 2 on the same slot, so
each M10 run carries its own M8 census, M9 VAT census and M9 survival
receipts as cross-checks; counting stays on in every M10 mode):
mode 2 (slot delta + order/matrix/epoch/occ walks),
`SSX_M10_NOPCONS=1` (NOP consuming draws; delta disarmed),
`SSX_M10_NOPCONS=2` (NOP every draw; positive control; delta disarmed),
`SSX_M10_RAMCOPY=1` (force EFB/XFB copies to RAM for the sequence),
`SSX_M10_RAMREF=1` (implies RAMCOPY; split at replay 100 — pristine
first half, delta second half — with a rendered-reference diff; needs
`NOPCONS=0`). Survival reuses `SSX_M9_SURV=1`.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M9. `m10-det*`
configuration means dual core + `SSX_S2_FORCE_DETERMINISM=1` +
`--cpu-thread`. Profile directories are fresh per run. Each desktop run
held `/tmp/ssx3-host-lease` (`printf 'M10\n'`, removed after each run);
the log is `local/research/M10/waits.log` (zero waits, nine claim/release
pairs, never forced). Builds ran any time; no build ran during a run.
`complete_hazard_resets` (harness field, as observed): all seven arms 0;
every sequence is 200/200 with `done` and clean counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `418f9113…` (= M9 on disk) | `players/m10-baseline` | `m10-det-run` (`m10-det`, `SSX_M9_SLOT=0 SSX_M9_SURV=1`) | `m10-det-probe.jsonl` |
| 2 order+matrix | `8d804e06…` | `players/m10-order` | `m10-det2-run` (`m10-det2`, `SSX_M10_SLOT=0 SSX_M9_SURV=1`) | `m10-det2-probe.jsonl` |
| 3 target+occ | `bdd642a2…` | `players/m10-target` | `m10-det3-run` (`m10-det3`, `SSX_M10_SLOT=0 SSX_M9_SURV=1`) | `m10-det3-probe.jsonl` |
| 3 nop-cons | `bdd642a2…` | `players/m10-target` | `m10-det4-run` (`m10-det4`, `SSX_M10_SLOT=0 SSX_M10_NOPCONS=1`) | `m10-det4-probe.jsonl` |
| 3 nop-all control | `4b5a1572…` | `players/m10-target2` | `m10-det5-run` (`m10-det5`, `SSX_M10_SLOT=0 SSX_M10_NOPCONS=2`) | `m10-det5-probe.jsonl` |
| 3 forced-RAM nop-all | `e3b3497b…` | `players/m10-ram` | `m10-det6-run` (`m10-det6`, `SSX_M10_SLOT=0 SSX_M10_NOPCONS=2 SSX_M10_RAMCOPY=1`) | `m10-det6-probe.jsonl` |
| 3 true-delta | `88eeb5aa…` (= committed) | `players/m10-ref` | `m10-det7-run` (`m10-det7`, `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1`) | `m10-det7-probe.jsonl` |

The committed header is `88eeb5aa…`. Later step-3 revisions only add
env-gated branches (`NOPCONS=2`, `RAMCOPY`, `RAMREF`) and the drain-clear
rule fix (below); the `nop=0/1`, `ram=0` paths that det3/det4 ran are
preserved verbatim, so every arm above is reproducible from the committed
header via env. One det3 run was discarded before analysis (drain-copy
clear-bit rule, fixed per the vendor's copy-then-clear order; see
§Step 3 and `waits.log`); the table lists the re-run.

Player dirs live under `local/research/M10/players/` (the build driver
requires outputs under `local/`; they are gitignored build outputs, never
committed). Run dirs and every probe jsonl (>5 MB, ~21 MB each) live under
`/Volumes/Extreme SSD/m10/` (symlink-free; `realpath` is the path as
written). Probes, runs and players are not committed.

## Step 1 — baseline (M9 end state reproduces)

Unmodified copy, M9 slot-0 delta env. `analyze.py` prints 200 rows + `done` +
`xfb_equal_scratch=200/200` + `live_xfb_untouched=1` +
`dafter_live`/`dframe`/`dpres`/`dimx` all 0/0. Control for steps 2–3.
(The `xfb_equal_scratch`/`xdiff` zeros are re-read in §Step 3: with the
default skip-to-VRAM config they compare uninit patterns, not pixels.)

Seam-application receipt (`xform_stats`, M9 slot mode):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 431400 (2157/replay = the run's `indexed` count) |
| `hits` | 27600 (138/replay covering word 3) |
| `regcalls` | 0 |

138 vs M9 det4's 74 is frame variation (this frame: 338020 B / 2157
indexed; M9's det4: 284471 B / 1037 indexed; hits/indexed = 6.4% here vs
7.1% there), same phenomenon: triple-digit seam hits per replay, zero
bytes differ under the skip config.

Own-frame M9 census, m10-det (draws=1454, verts=31002; VAT walk):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1335 | 119 | n/a | n/a |
| Tex0 | 1454 | 0 | 1414 | 1414 |
| Tex1 | 1353 | 101 | 533 | 432 |
| Tex2 | 1454 | 0 | 30 | 30 |
| Tex3 | 1454 | 0 | 9 | 9 |
| Tex4-7 | 1454 | 0 | 0 | 0 |

Shared reach: Pos 0:705, Tex2 36:30. Survival trichotomy: live
200/200, per-vertex 200/200, shared-pos 200/200 (resident 200/200),
shared-tex 0 (resident 0/200); `dirty_post=0`, `zfreeze=0`; `xdiff>0`
replays = 0/200 (skip config).

## Per-step wall table (all seven arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m10-det | 200 | 3.067 / 4.099 / 2.580 / 8.651 | 1.777 / 2.104 | 338020 / 2961 | YES | seq_wall_ms=1032.986 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det2 | 200 | 2.553 / 3.692 / 2.283 / 6.491 | 1.408 / 1.607 | 284021 / 2496 | YES | seq_wall_ms=926.396 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det3 | 200 | 2.708 / 3.984 / 2.353 / 5.679 | 1.536 / 1.667 | 319034 / 2596 | YES | seq_wall_ms=948.471 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det4 | 200 | 2.316 / 2.939 / 1.860 / 5.718 | 1.336 / 1.410 | 352379 / 2986 | YES | seq_wall_ms=856.299 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det5 | 200 | 1.603 / 2.542 / 1.174 / 5.566 | 0.589 / 0.672 | 309906 / 2656 | YES | seq_wall_ms=726.073 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det6 | 200 | 4.322 / 8.203 / 3.627 / 391.554 | 1.167 / 1.456 | 400262 / 3489 | YES | seq_wall_ms=1731.924 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
| m10-det7 | 200 | 3.641 / 5.439 / 3.090 / 13.481 | 1.649 / 2.014 | 318998 / 2543 | YES | seq_wall_ms=1258.812 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (284021 … 400262 B), so wall medians are not
comparable across rows as mechanism costs (M5 §Per-step wall table). All
seven rows: 200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2
dls=0 walk=100% unknown=0 benign=1` in all runs. det6 wall max 391.554 ms
is one slow replay (encode hitch; p95 8.203). det6/det7
`xfb_equal_scratch=0/200` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), not a failure.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m10-det | 0.132 | 0.001 | 0.034 | 2.903 | 0.001 | 3.864 |
| m10-det2 | 0.082 | 0.001 | 0.024 | 2.444 | 0.001 | 3.593 |
| m10-det3 | 0.090 | 0.001 | 0.027 | 2.586 | 0.001 | 3.871 |
| m10-det4 | 0.097 | 0.001 | 0.065 | 2.152 | 0.001 | 2.763 |
| m10-det5 | 0.093 | 0.001 | 0.088 | 1.422 | 0.001 | 2.364 |
| m10-det6 | 0.182 | 0.001 | 0.133 | 3.992 | 0.000 | 7.797 |
| m10-det7 | 0.094 | 0.001 | 0.027 | 3.521 | 0.000 | 5.300 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m10-det | 2157 | 103536 | 20.3 |
| m10-det2 | 1047 | 50256 | 41.7 |
| m10-det3 | 1076 | 51648 | 40.6 |
| m10-det4 | 1159 | 55632 | 37.7 |
| m10-det5 | 1431 | 68688 | 30.5 |
| m10-det6 | 2928 | 140544 | 14.9 |
| m10-det7 | 1078 | 51744 | 40.5 |

## Step 2 — order + values (M9 gaps 1, 3–4)

One instrument, header-only, env-gated (unset = M9 behavior): the M10
order walk records stream-position stamps (draw clock + byte offset +
size via deferred `OnCommand` attribution) for every XF write covering
the delta word and every shared-path draw consuming the slot, in one
walk; the seam captures the slot's 12-word matrix before/after the
first hit, and post-replay sampling captures live xfmem + consumed
snapshot 12-word values (replay 0 stored, later replays counted by
mismatch).

Walk cross-checks, m10-det2 (M10 walk vs M9 walk on the same stream):
draws 1470 = 1470, verts 25301 = 25301, `idx_loads` 1047 = `indexed`
1047, `cons_pos` 689 = shared-pos reach slot-0 689, consumed == size
both, walk_ok=1 both. Seam/walk cross-check: walk covering loads 77 =
seam hits/replay 77 (m10-det3: 75 = 75).

Hit/draw order table, m10-det2 (slot 0, word 3):

| field | value |
| --- | --- |
| draws / verts | 1470 / 25301 |
| idx_loads | 1047 |
| covering (idx_cover / direct_cover; arr12/13/14/15) | 77 (77 / 0; 77/0/0/0) |
| first covering load (draw clock / byte off / kind) | 0 / 2635 / indexed |
| last covering load (draw clock / byte off) | 1406 / 273006 |
| cons_pos / cons_tex / cons_any | 689 / 0 / 689 |
| first / last consuming draw | 1 / 1470 |
| cons_before_first / cons_at_after_first | 0 / 689 |
| loads_before_first / loads_first_to_lastcons | 0 / 1047 |
| seam_hits / seam_per_replay | 15400 / 77 |
| walk / walk_ok | 284021/284021 / 1 |

Covering-load draw clocks (n=77, full list):
`0,9,10,11,12,13,14,15,16,17,18,19,49,57,476,478,480,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,606,642,678,707,791,792,832,873,914,928,940,952,1014,1094,1144,1194,1244,1294,1312,1338,1350,1352,1406`.

Consuming draw indices (n=689; first 30 + last 10; full list in probe):
first 30 = `1,2,3,4,5,6,7,8,9,10,20,21,22,23,24,25,26,27,28,29,30,31,50,58,59,60,61,62,63,64`;
last 10 = `1461,1462,1463,1464,1465,1466,1467,1468,1469,1470`.

Full-matrix values, m10-det2 (slot 0, words 0..11; `done=1`,
`snap_which=1` shared-pos, `n=200`, `mm_live=0`, `mm_snap=0`):

| i | word | before hex | before float | after hex | after float | post-live hex | post-live float | post-snap hex | post-snap float |
| ---: | ---: | --- | ---: | --- | ---: | --- | ---: | --- | ---: |
| 0 | 0 | 3f800000 | 1 | 3f800000 | 1 | 3f800000 | 1 | 3f800000 | 1 |
| 1 | 1 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 2 | 2 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 3 | 3 | 00000000 | 0 | 3dcccccd | 0.1 | 3dcccccd | 0.1 | 3dcccccd | 0.1 |
| 4 | 4 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 5 | 5 | 3f800000 | 1 | 3f800000 | 1 | 3f800000 | 1 | 3f800000 | 1 |
| 6 | 6 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 7 | 7 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 | 00000000 | 0 |
| 8 | 8 | 80000000 | -0 | 80000000 | -0 | 80000000 | -0 | 80000000 | -0 |
| 9 | 9 | 80000000 | -0 | 80000000 | -0 | 80000000 | -0 | 80000000 | -0 |
| 10 | 10 | bf800000 | -1 | bf800000 | -1 | bf800000 | -1 | bf800000 | -1 |
| 11 | 11 | c0000000 | -2 | c0000000 | -2 | 80000000 | -0 | 80000000 | -0 |

Recorded without verdict: the first-hit matrix is row0 `[1,0,0,0]`,
row1 `[0,1,0,0]`, row2 `[-0,-0,-1,-2]`; the +0.1 lands on word 3 only
(all 11 siblings bit-identical before/after). Post-replay live and
snapshot agree on all 12 words (`live == snap`, `mm=0` over 200
replays); word 11 reads `-0` post-replay vs `-2` at the first hit
(later loads overwrite the slot's non-delta words; the M9 `vb_mm` /
`va_mm` tallies show the same evolution on the delta word).

Same-shape matrix receipts: m10-det3 before/after/post identical to
the table above; m10-det7 before/after (first hit at replay 100)
identical, post = pristine replay-0 values with `mm_live=100`
`mm_snap=100` (the 100/100 split); m10-det6 (no delta) post = pristine
uniform, `mm_live=0` `mm_snap=0`, `done=0`.

Standing of the "loads trail draws" variant (table):

| Candidate | Standing | Receipt |
| --- | --- | --- |
| perturbation lands after consumption ("loads trail draws"), shared-pos path | excluded | `cons_before_first=0/689` (det2), `0/712` (det3), `0/774` (det7); first covering load at draw clock 0 on all three delta frames; 1047–1863 flush-triggering indexed loads between first load and last consuming draw; M9 dirty flags arm upload at every covering write (`hdirty_pervtx` = hits) |

## Step 3 — render-target + occlusion (M9 gaps 1, 5–6)

Two header-only instruments, env-gated (unset = M9 behavior), in the same
M10 walk: per-draw render-target epochs (every EFB-copy trigger decoded
with dest/bytes/XFB-bit/clear/source-rect; each consuming draw classified
against the compared XFB range) and per-draw rasterizer state (GenMode
cull, scissor-empty, ZMode test/func/update) plus a NOP-collective arm
(consuming draws' command bytes replaced with GX_NOPs in the replayed
streams) with a NOP-all positive control. One det3 run was discarded
before analysis: the first in-range rule disqualified a draining copy
with the clear bit set; the vendor copies first, then clears the source
rect (`BPStructs.cpp`: "Clear the rectangular region after copying it"),
so the rule was fixed (draining copy needs overlap only; intervening
clear-copies are barriers) and det3 re-ran on the fixed header.

EFB-copy table, m10-det3 (compared xfb=`0x004dc660`/573440):

| copy | draw clock | dest | bytes | xfb bit | clear | tl | w | h | ovl |
| ---: | ---: | --- | ---: | :-: | :-: | --- | ---: | ---: | :-: |
| 0 | 9 | 0x00701560 | 16384 | 0 | 1 | 0x000000 | 32 | 32 | 0 |
| 1 | 17 | 0x0110c440 | 65536 | 0 | 1 | 0x000000 | 128 | 128 | 0 |
| 2 | 1767 | 0x004dc660 | 573440 | 1 | 1 | 0x000000 | 640 | 448 | 1 |

Epoch table, m10-det3 (draws=1767; epoch_cons=`9,1,702,0`):

| epoch | draw range | cons draws | closing copy |
| ---: | --- | ---: | --- |
| 0 | 1..9 | 9 | copy 0 (ovl 0, clear 1) |
| 1 | 10..17 | 1 | copy 1 (ovl 0, clear 1) |
| 2 | 18..1767 | 702 | copy 2 (ovl 1, clear 1) |
| 3 | 1768..1767 | 0 | tail (none) |

Per-class table, consuming draws (buckets disjoint by priority culled >
out-of-range > in-range; in-range = an overlapping copy triggers at/after
the draw with no clear-copy between; culled = cull-all, scissor-empty, or
z-test with func Never):

| Arm | cons | culled | out-of-range | in-range | cull reasons (cons; non-disjoint) | copies (XFB + non-XFB) |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| m10-det3 | 712 | 0 | 10 | 702 | cull_all=0 scis_empty=0 znever=0 | 1 + 2 (32×32, 128×128 clears) |
| m10-det4 | 868 | 0 | 10 | 858 | cull_all=0 scis_empty=0 znever=0 | 1 + 2 (32×32, 128×128 clears) |
| m10-det5 | 721 | 0 | 20 | 701 | cull_all=0 scis_empty=0 znever=0 | 1 + 4 (2× 32×32, 2× 128×128 clears) |
| m10-det6 | 701 | 0 | 30 | 671 | cull_all=0 scis_empty=0 znever=0 | 1 + 6 (3× 32×32, 3× 128×128 clears) |
| m10-det7 | 774 | 0 | 10 | 764 | cull_all=0 scis_empty=0 znever=0 | 1 + 2 (32×32, 128×128 clears) |

All-draw context (every arm): `all_cull=0 all_scis=0 all_znever=0` — no
draw on any M10 frame is culled by state. The out-of-range draws sit in
the early texture-copy epochs behind clear barriers (small clear rects:
32×32/128×128 at TL 0,0); the tail epoch past the final XFB copy holds 0
consuming draws on every arm. `mask.xfb` (compared range) agrees with the
overlapping copy on every arm (1 XFB copy each; `efb_total` 3–7).

NOP-collective receipts:

| Arm | nop | ok | draws NOPed | bytes NOPed | xdiff>0 (skip config) |
| --- | ---: | :-: | ---: | ---: | ---: |
| m10-det4 (cons) | 1 | 1 | 868 / 2073 | 151438 / 352379 | 0/200 |
| m10-det5 (all) | 2 | 1 | 1449 / 1449 | 265418 / 309906 | 0/200 |

The det5 row (every draw removed, zero bytes differ) forced the
pixel-compare audit below; det4's 0/200 is vacuous under the skip config
(see next table), not a contribution receipt.

Pixel-compare audit (why every skip-config xdiff is 0/200). Code path
(read-only vendor facts):

| # | Fact | Source |
| --- | --- | --- |
| 1 | `copy_to_ram = !(skip) \|\| !copy_to_vram`; when false, the XFB dest is filled with the fuchsia uninit pattern (`0xFE01…`) instead of encoded pixels | `TextureCacheBase.cpp` `CopyRenderTargetToTexture` + `UninitializeXFBMemory` |
| 2 | Config-layer defaults: `XFBToTextureEnable` (`bSkipXFBCopyToRam`) = true, `EFBToTextureEnable` (`bSkipEFBCopyToRam`) = true, `DeferEFBCopies` = true | `GraphicsSettings.cpp:198-201` |
| 3 | The harness `GFX.ini` sets only `ImmediateXFBEnable`/`CapImmediateXFB`; no GXBE69 game INI exists in tree or profiles; `bSupportsCopyToVram=true` on Metal and Vulkan | `tools/gamecube_schedule_check.py:154`, profile `Config/GFX.ini`, `MTLUtil.mm:63`, `VulkanContext.cpp:447` |
| 4 | With `bDeferEFBCopies=false`, XFB copies call `WriteEFBCopyToRAM` synchronously at the trigger (no pending-queue delay) | `TextureCacheBase.cpp` (`if (!copy_to_vram \|\| !bDeferEFBCopies)` flush branch) |

Run receipts (`m10_ram`: live pre-flip sample + post-sequence sample):

| Arm | ram | skipx_pre | skipe_pre | defer_pre | skipx_post | skipe_post | defer_post |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| m10-det6 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| m10-det7 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |

Skip-vs-forced contrast (same NOP-all machinery, same compare code):

| Arm | copies to RAM | NOPall draws/bytes | xfb_equal_scratch | xdiff>0 | xdiff bytes | xdmax | xdmean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| m10-det5 | skipped (default) | 1449 / 265418 | 200/200 | 0/200 | 0 | 0 | 0.000 |
| m10-det6 | forced | 1570 / 343777 | 0/200 | 200/200 | 573440 / 573440 | 234 (r0) / 126 (r1+) | 135.598 (r0) / 70.5 (r1+) |

Recorded without verdict: with copies skipped, the live XFB and every
replay scratch hold the same uninit pattern, so `xfb_equal_scratch` and
`xdiff` cannot see rendered pixels on any M5–M10 skip-config run,
including the M7/M8/M9 "0 pixels differ" rows. With copies forced, the
same NOP-all machinery moves all 573440 bytes on all 200 replays (blank
frame vs fuchsia ref), which validates the NOP patch spans, the scratch
redirect, and the xdiff chain end to end. det6 replay 0 differs from
replays 1+ (cold EFB with live leftovers vs cleared EFB), uniform
thereafter — the reason the true-delta arm below references replay 99,
not replay 0.

True-delta arm (m10-det7: forced RAM + split at replay 100 — replays
0–99 pristine, 100–199 slot-0 delta — diffed against replay 99's
rendered scratch frame):

| field | value |
| --- | --- |
| ref / kref / refok / refhash | 1 / 100 / 1 / `92356d0665e47854` |
| n2 (delta replays) | 100 |
| gt0 (differing) | 100 |
| uniform2 (identical to replay 100) | 100 |
| xd2min / xd2max (bytes, of 573440) | 32954 / 32954 |
| xdmax2max | 116 |
| xdmean2min / xdmean2max | 2.287 / 2.287 |
| samples | r100:32954/116/2.287, r101:32954/116/2.287, r102:32954/116/2.287 |

Second-half corroboration, m10-det7: `xform_stats` hits=7700
(= 100 × 77 covering loads; first half counting-only); M9 trichotomy
over the second half 100/100 perturbed in live, per-vertex and
shared-pos snapshots; `m10_matrix` before/after at the replay-100 first
hit identical to the §Step 2 table, post = pristine replay-0 values
with `mm_live=100` `mm_snap=100` (the 100/100 split).

Standing of the visibility variant (table):

| Candidate | Standing | Receipt |
| --- | --- | --- |
| consuming draws miss the compared range (render-target) | excluded | 702/712 (det3), 858/868 (det4), 701/721 (det5), 671/701 (det6), 764/774 (det7) consuming draws in-range; single draining XFB copy per frame; tail epochs empty |
| consuming draws culled by rasterizer state | excluded | `culled=0` on all five arms; `all_cull=all_scis=all_znever=0` on all draws |
| consuming draws depth-occluded, collectively | excluded | det7: the slot-0 delta moves 32954 bytes on 100/100 delta replays against a rendered pristine reference — the consuming set provably contributes pixels |
| consuming draws depth-occluded, per draw | open | no header-only per-draw depth instrument (see "What I could not do" 1); direct vs texture-mediated partition of the 32954 open (early texture copies + undecoded per-vertex indices) |

## Step 4 — verdict-free synthesis

Mechanism table (each M9 residue row with its receipt):

| M9 residue row | Standing | Receipt |
| --- | --- | --- |
| order (perturbation lands after consumption) | excluded | §Step 2 order table: 0 consuming draws before the first covering load on all delta frames |
| values (delta word live at draw time, sane siblings) | confirmed live | §Step 2 matrix table: +0.1 on word 3 only, 11/11 siblings bit-identical; post live == post snapshot on all 12 words, mm=0 |
| visibility (render-target / cull state) | excluded | §Step 3 per-class table: 96–99% of consuming draws in-range, 0 culled on all arms |
| visibility (depth occlusion, collective) | excluded | §Step 3 det7: 32954 bytes move on 100/100 delta replays vs rendered reference |
| visibility (depth occlusion, per draw) | open | no header-only per-draw depth query; receipt: collective bound only |
| texcoord stage (why 21 perturbed Tex2 draws move zero UV pixels) | open | M10 ran slot 0 only; the order/matrix/epoch instruments are slot-parametric but unrun on slot 36 |
| pixel-compare validity (M7/M8/M9 "0 pixels") | artifact identified | §Step 3 audit: default skip-to-VRAM config fills both sides with the uninit pattern; det5/det6 contrast 0/200 vs 200/200 |

Tabled finding (not a verdict), single sentence: on the slot-0
PosNormal path, the +0.1 perturbation lands before all of its ~700
shared-position consuming draws with live snapshot values and sane
matrix siblings, ~97% of those draws drain in-range and unculled into
the compared XFB, and the delta moves 32954/573440 bytes deterministically
against a rendered pristine reference — the earlier "0 pixels" rows
measured the skip-to-VRAM uninit pattern, not rendered output.

Exact experiment that would flip it: re-run the M10 true-delta arm
(`SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1` on the committed header,
fresh profile) with the ref2 window moved to a different warm replay
pair (e.g. ref replay 50, delta from replay 51 via a `kref` env instead
of the fixed 100) — non-identical `xd2` across the two windows would
refute the 32954-byte effect size.

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m10-det | `fc=6783` | `replay_disabled=0 fc=6786 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det2 | `fc=6681` | `replay_disabled=0 fc=6684 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det3 | `fc=6917` | `replay_disabled=0 fc=6920 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det4 | `fc=6927` | `replay_disabled=0 fc=6930 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det5 | `fc=6787` | `replay_disabled=0 fc=6790 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det6 | `fc=6315` | `replay_disabled=0 fc=6318 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m10-det7 | `fc=6575` | `replay_disabled=0 fc=6578 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ);
the septuple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same
address and size, also identical to all M9/M8/M7 sequence hashes and all
M6 sequence and M5 sequence/disabled hashes) is tabulated as observed.
`resume fc − fc0 = 3` in each run (the live record window; per-replay
`dframe` sums are 0/0 in all arms).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest
and event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m10-det | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det2 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det3 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det4 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det5 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det6 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m10-det7 | 200/200 / 0/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

det6/det7 scratch `0/200` is the forced-RAM signature (rendered scratch
vs fuchsia live ref), tabulated as observed. `present_trace` on all
arms: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0` with zero
`seq_*` (tracer's positive control intact, sequence silent).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M9/build_replay_player.py`):

```
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-baseline
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-order
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-target
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-target2
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-ram
python3 local/research/M10/build_replay_player.py local/research/M10/players/m10-ref
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M10\n'`,
remove after each run; profiles fresh per run):

```
SSX_M9_SLOT=0 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det-run" --seconds 240
SSX_M10_SLOT=0 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-order --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det2 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det2-run" --seconds 240
SSX_M10_SLOT=0 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-target --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det3 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det3-run" --seconds 240
SSX_M10_SLOT=0 SSX_M10_NOPCONS=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-target --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det4 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det4-run" --seconds 240
SSX_M10_SLOT=0 SSX_M10_NOPCONS=2 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det5-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-target2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det5 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det5-run" --seconds 240
SSX_M10_SLOT=0 SSX_M10_NOPCONS=2 SSX_M10_RAMCOPY=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det6-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-ram --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det6 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det6-run" --seconds 240
SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m10/m10-det7-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M10/players/m10-ref --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m10-det7 --cpu-thread --output "/Volumes/Extreme SSD/m10/m10-det7-run" --seconds 240
```

Analysis:

```
python3 local/research/M10/analyze.py "m10-det=/Volumes/Extreme SSD/m10/m10-det-probe.jsonl" "m10-det2=/Volumes/Extreme SSD/m10/m10-det2-probe.jsonl" "m10-det3=/Volumes/Extreme SSD/m10/m10-det3-probe.jsonl" "m10-det4=/Volumes/Extreme SSD/m10/m10-det4-probe.jsonl" "m10-det5=/Volumes/Extreme SSD/m10/m10-det5-probe.jsonl" "m10-det6=/Volumes/Extreme SSD/m10/m10-det6-probe.jsonl" "m10-det7=/Volumes/Extreme SSD/m10/m10-det7-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M10/` — `m10_replay_context.h`
(`88eeb5aa…`), `build_replay_player.py`, `analyze.py`, `REPORT.md` (this
file), `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m10/` —
`m10-det-probe.jsonl`, `m10-det2-probe.jsonl`, `m10-det3-probe.jsonl`,
`m10-det4-probe.jsonl`, `m10-det5-probe.jsonl`, `m10-det6-probe.jsonl`,
`m10-det7-probe.jsonl` (~21 MB each) and the matching `-run` dirs and
`-run.log` harness receipts; `analyze-all.txt` (the seven-arm analyzer
output) and `analyze-det{,2,3,4,5,6,7}.txt` (per-arm outputs); per-step
header snapshots `m10_replay_context.step1.h`,
`m10_replay_context.step2.h`, `m10_replay_context.step3.h` (= committed
header). Players (gitignored):
`local/research/M10/players/{m10-baseline,m10-order,m10-target,m10-target2,m10-ram,m10-ref}/`
(each with `player`, `build.json`, launchers). All paths above are
symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` /
`player_sha256`, 12-char prefixes): `m10-baseline` `418f9113600e` /
`f27c29a4eafd` (player hash identical to M9's `m9-delta`: same header
compiles to the same binary), `m10-order` `8d804e0609c7` / `a3ef0a0a6c95`,
`m10-target` `bdd642a20cb9` / `574edcc04c25`, `m10-target2` `4b5a15725233` /
`031c535e840b`, `m10-ram` `e3b3497baba1` / `af4c9b01495d`, `m10-ref`
`88eeb5aaa4c4` / `9188345ed349`.

## What I could not do

1. No per-draw depth-occlusion query exists header-only: `Flush` /
`SetConstants` are vendor-called with no header hook (M9 gap 1
persists), so per-draw occlusion is bounded collectively (det7's moved
pixels exclude blanket occlusion) but not attributed per draw. A
per-draw receipt needs a vendor execute-pass hook or per-draw EFB
readback (ordered follow-up, not this runbook).
2. Per-vertex matrix indices (`pnmtxidx` into `transformmatrices`) are
still not decoded (M9 gap 2 persists): the 49–162 indexed-position
draws per frame have unknown slot-0 exposure, and the 32954 moved
bytes are not partitioned between shared-path, indexed-path, and
texture-mediated carriers.
3. Direct vs texture-mediated partition of the true-delta effect is
not measured: the early render-to-texture copies (32×32/128×128) could
carry part of the 32954 bytes through textures sampled by later draws.
Discriminating instrument: a forced-RAM NOPTEXT arm (NOP the
texture-copy epochs' draws only).
4. No delta run on slot 36 (Tex2): step 4's texcoord-stage row is open.
The order/matrix/epoch instruments are slot-parametric
(`SSX_M10_SLOT=36 SSX_M10_RAMREF=1` runs them unchanged); ordered
follow-up beyond this runbook, not a gap in it.
5. The `xform` capacity-row flag does not reflect the RAMREF split
(all 200 rows tag `xform=1` on det7; the split is visible in
hits/trichotomy/`mm` instead). Cosmetic; the analyzer does not use the
flag for M10 tables.
6. M9's "What I could not do" 7 (other-slot delta runs) is partly
inherited: M10 ran slot 0 only (runbook prescription).
7. Player dirs are under `local/research/M10/players/` rather than the
SSD: the build driver refuses outputs outside `local/`, and the brief
orders changing only the header path it compiles in. Run dirs and all
>5 MB probes are on the SSD as ordered.
8. Desktop only; no device work.

## Files

Committed under `local/research/M10/`: `m10_replay_context.h` (research
header, `88eeb5aa…`), `build_replay_player.py` (M9 driver, header path
only), `analyze.py` (M9 tables unchanged + M10 `m10_order`/`m10_loads`/
`m10_cons`/`m10_matrix`/`m10_copy`/`m10_occ`/`m10_nop`/`m10_ram`/
`m10_ref2` parsing, order tables, 12-word hex+float matrix tables,
copy/epoch/occlusion tables, NOP/RAM/ref2 receipts; missing keys print
as n/a / sections skipped), `REPORT.md` (this file), `waits.log` (zero
waits, nine claim/release pairs, two annotations).

## Header diffs per step (`diff -u` against the M9 header)

Step 1: empty (verbatim copy). Steps 2–3 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m10/m10_replay_context.step2.h` and
the committed `local/research/M10/m10_replay_context.h` (= step 3; the
step-3 header grew through det3–det7 with env-gated additions only, so
every arm is reproducible from it via env).

### Step 2

```diff

--- local/research/M9/m9_replay_context.h	2026-09-19 10:40:01
+++ /Volumes/Extreme SSD/m10/m10_replay_context.step2.h	2026-09-19 11:37:22
@@ -827,6 +827,159 @@
   stats.numtex0 = xf_regs[0x3f];
   if (src.empty()) return stats;
   M9CensusWalk walk(cp_mem, xf_regs, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
+  return stats;
+}
+
+// --- M10 step 2: hit/draw order stamps + consuming-draw spans -----------------
+// One read-only walk over the verbatim recorded stream (own CPState + numtex
+// state, same seeding as M9CensusWalk). Records in stream order: every XF
+// write covering the delta word (indexed loads via OnIndexedLoad — address is
+// the xfmem word address for every array, XFStructs.cpp LoadIndexedXF — plus
+// direct XF writes via OnXF below 0x1000), and every draw consuming the slot
+// through the shared path (position: shared + PosNormalMtxIdx==slot, no
+// enablement gate; texgen i: shared + enabled + TexiMtxIdx==slot). Positions
+// come from OnCommand, which the vendor calls immediately after each
+// command's specific callback with the command's start pointer and total size
+// (OpcodeDecoding.h RunCommand): specific callbacks push pending records, the
+// next OnCommand stamps offset/size. Display-list bodies are not decoded by
+// the offline Run (the execute pass handles them); mask.dls==0 on these
+// frames, and the report carries the count.
+struct M10LoadRec {
+  u32 draw = 0;   // draws completed before this command (draw clock)
+  u32 off = 0;    // stream byte offset of the command
+  u32 size = 0;   // command byte size
+  u32 kind = 0;   // 0 = indexed load, 1 = direct XF write
+  u32 array = 0;  // CPArray id for indexed loads
+};
+struct M10DrawRec {
+  u32 off = 0;
+  u32 size = 0;
+  u32 cons_pos = 0;
+  u32 cons_texmask = 0;  // bit i = consumes the slot via texgen i
+};
+struct M10Order {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 unknown = 0;
+  u32 benign = 0;
+  u32 slot = 0;
+  u32 word = 0;
+  u32 idx_loads = 0;  // all indexed loads (any coverage)
+  std::vector<M10LoadRec> loads;  // covering loads, stream order
+  std::vector<M10DrawRec> drawrec;  // per draw (index d-1), stream order
+  std::vector<u32> load_draws;  // draw clock at every indexed load
+};
+class M10OrderWalk final : public OpcodeDecoder::Callback {
+public:
+  M10OrderWalk(const u8* base, const u32* cp_mem, const u32* xf_regs, u32 slot,
+               M10Order& stats)
+      : m_base(base), m_cp(cp_mem), m_stats(stats) {
+    m_stats.slot = slot;
+    m_stats.word = slot * 4 + 3;
+    m_numtex = xf_regs[0x3f] & 0xf;
+  }
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address, hi = u32(address) + u32(count);
+    if (lo < 0x1000 && lo <= m_stats.word && m_stats.word < hi) {
+      M10LoadRec r;
+      r.draw = m_stats.draws;
+      r.kind = 1;
+      m_stats.loads.push_back(r);
+      m_pending_load = true;
+    }
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      if (word == XFMEM_SETNUMTEXGENS) {
+        m_numtex = v & 0xf;
+      }
+      if (word == XFMEM_SETMATRIXINDA) {
+        m_cp.matrix_index_a.Hex = v;
+      } else if (word == XFMEM_SETMATRIXINDB) {
+        m_cp.matrix_index_b.Hex = v;
+      }
+    }
+  }
+  void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
+  void OnBP(u8, u32) override {}
+  void OnIndexedLoad(CPArray array, u32, u16 address, u8 size) override {
+    ++m_stats.idx_loads;
+    m_stats.load_draws.push_back(m_stats.draws);
+    const u32 lo = address, hi = u32(address) + u32(size);
+    if (lo <= m_stats.word && m_stats.word < hi) {
+      M10LoadRec r;
+      r.draw = m_stats.draws;
+      r.kind = 0;
+      r.array = static_cast<u32>(array);
+      m_stats.loads.push_back(r);
+      m_pending_load = true;
+    }
+  }
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 v = vat & 7;
+    const u32 comp =
+        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    M10DrawRec d;
+    if ((comp & VB_HAS_POSMTXIDX) == 0 && idx[0] == m_stats.slot) d.cons_pos = 1;
+    for (u32 i = 0; i < 8; ++i) {
+      const bool enabled = i < (m_numtex & 15);
+      if ((comp & (VB_HAS_TEXMTXIDX0 << i)) == 0 && enabled &&
+          idx[1 + i] == m_stats.slot) {
+        d.cons_texmask |= 1u << i;
+      }
+    }
+    m_stats.drawrec.push_back(d);
+    m_pending_draw = true;
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8 opcode, const u8*) override {
+    if (opcode == 0x44 || opcode == 0x48)
+      ++m_stats.benign;
+    else
+      ++m_stats.unknown;
+  }
+  void OnCommand(const u8* data, u32 size) override {
+    const u32 off = u32(data - m_base);
+    if (m_pending_load && !m_stats.loads.empty()) {
+      m_stats.loads.back().off = off;
+      m_stats.loads.back().size = size;
+      m_pending_load = false;
+    }
+    if (m_pending_draw && !m_stats.drawrec.empty()) {
+      m_stats.drawrec.back().off = off;
+      m_stats.drawrec.back().size = size;
+      m_pending_draw = false;
+    }
+  }
+  CPState& GetCPState() override { return m_cp; }
+
+private:
+  const u8* m_base;
+  CPState m_cp;
+  M10Order& m_stats;
+  u32 m_numtex = 0;
+  bool m_pending_load = false;
+  bool m_pending_draw = false;
+};
+static M10Order RunM10Order(const std::vector<u8>& src, const u32* cp_mem,
+                            const u32* xf_regs, u32 slot) {
+  M10Order stats;
+  stats.slot = slot;
+  stats.word = slot * 4 + 3;
+  if (src.empty()) return stats;
+  M10OrderWalk walk(src.data(), cp_mem, xf_regs, slot, stats);
   stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
   return stats;
 }
@@ -989,6 +1142,22 @@
 static unsigned long long s_m9_vb_mm = 0, s_m9_va_mm = 0;
 static unsigned long long s_m9_hit_dirty_pos = 0, s_m9_hit_dirty_texa = 0;
 static unsigned long long s_m9_hit_dirty_texb = 0, s_m9_hit_dirty_pervtx = 0;
+// --- M10 step 2: 12-word matrix capture --------------------------------------
+// At the first seam hit covering the delta word, captures the slot's full
+// 3x4 matrix (words slot*4..slot*4+11) before and after the +0.1f add;
+// post-replay sampling captures live xfmem + the consumed snapshot's 12
+// words on replay 0 with mismatch tallies across the sequence. Gated on
+// s_m10_cap (M10 mode only); unset = M9 shape.
+static int s_m10_cap = 0;
+static int s_m10_mat_done = 0;
+static u32 s_m10_mat_before[12] = {};
+static u32 s_m10_mat_after[12] = {};
+static u32 s_m10_post_live[12] = {};
+static u32 s_m10_post_snap[12] = {};
+static int s_m10_snap_which = 0;  // 0 = none resident, 1 = shared pos, 2 = shared tex
+static int s_m10_snap_ti = -1;  // resident texgen for which==2
+static unsigned s_m10_mm_live = 0, s_m10_mm_snap = 0;
+static int s_m10_post_done = 0;
 static void M8Transform(u16 address, u32 count) {
   ++s_m8_calls;
   const u32 lo = address, hi = address + count;  // covered words [lo, hi)
@@ -1013,7 +1182,18 @@
       float* f = &xfmem.posMatrices[w];
       u32 vb = 0;
       std::memcpy(&vb, f, 4);  // read-only when s_m9_surv == 0
+      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: pre-add 12-word capture
+        const u32 base = u32(s_m8_slot) * 4;
+        for (u32 i = 0; i < 12; ++i)
+          std::memcpy(&s_m10_mat_before[i], &xfmem.posMatrices[base + i], 4);
+      }
       *f += 0.1f;
+      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: post-add 12-word capture
+        const u32 base = u32(s_m8_slot) * 4;
+        for (u32 i = 0; i < 12; ++i)
+          std::memcpy(&s_m10_mat_after[i], &xfmem.posMatrices[base + i], 4);
+        s_m10_mat_done = 1;
+      }
       ++s_m8_hits;
       if (s_m9_surv) {
         u32 va = 0;
@@ -1237,7 +1417,22 @@
   // VAT+texgen walk). Precedence: SLOT > CENSUS; M9 overrides M8 when set.
   // Counting stays on in every M9 mode, so each delta run carries its own
   // M8 census and its own M9 VAT census.
-  const int m9_slot = [] {
+  // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
+  // (all M9 walks + survival receipts ride along as cross-checks) and arms
+  // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
+  const int m10_slot = [] {
+    const char* v = std::getenv("SSX_M10_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m10_mode = m10_slot >= 0 ? 2 : 0;
+  const int m9_slot = m10_mode != 0 ? m10_slot : [] {
     const char* v = std::getenv("SSX_M9_SLOT");
     if (!v || !*v) return -1;
     int n = 0;
@@ -1248,10 +1443,10 @@
     }
     return n;
   }();
-  const int m9_mode = m9_slot >= 0 ? 2 : ([] {
+  const int m9_mode = m10_mode != 0 ? 2 : (m9_slot >= 0 ? 2 : ([] {
                         const char* v = std::getenv("SSX_M9_CENSUS");
                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
-                      })();
+                      })());
   // M9 step 3: survival sampling (SSX_M9_SURV=1). Arms only with a slot delta
   // (M9 mode 2); elsewhere parsed but inert.
   const int m9_surv = m9_mode == 2 ? ([] {
@@ -1269,6 +1464,11 @@
   const M9Census m9stream = m9_mode != 0 ? RunM9Census(frame, file->GetCPMem(),
                                                        file->GetXFRegs())
                                          : M9Census{};
+  // M10 step 2: hit/draw order stamps + consuming-draw spans (same stream).
+  const M10Order m10stream =
+      m10_mode != 0 ? RunM10Order(frame, file->GetCPMem(), file->GetXFRegs(),
+                                  u32(m10_slot))
+                    : M10Order{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -1382,14 +1582,14 @@
     return 0;
   }();
   {
-    char detail[448];
+    char detail[512];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
-                  "m9mode=%d m9slot=%d m9surv=%d",
+                  "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1397,7 +1597,7 @@
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                   xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
-                  m9_mode, m9_slot, m9_surv);
+                  m9_mode, m9_slot, m9_surv, m10_mode, m10_slot);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1496,6 +1696,15 @@
     s_m9_vb_mm = s_m9_va_mm = 0;
     s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
     s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
+    s_m10_cap = m10_mode;
+    s_m10_mat_done = 0;
+    s_m10_post_done = 0;
+    s_m10_snap_which = 0;
+    s_m10_snap_ti = -1;
+    s_m10_mm_live = s_m10_mm_snap = 0;
+    for (u32 i = 0; i < 12; ++i)
+      s_m10_mat_before[i] = s_m10_mat_after[i] = s_m10_post_live[i] =
+          s_m10_post_snap[i] = 0;
     XFReplay::g_transform = &M8Transform;
   } else if (m8_mode != 0) {
     s_m8_calls = 0;
@@ -1604,6 +1813,63 @@
           xfm.GetPerVertexTransformMatrixChanges()[0] >= 0)
         ++m9_dirty_post;
     }
+    // M10 step 2: post-replay 12-word sample (live xfmem + the consumed
+    // snapshot; replay 0 stored, later replays counted by mismatch).
+    if (m10_mode != 0) {
+      const u32 m10base = u32(m10_slot) * 4;
+      u32 live12[12];
+      for (u32 i = 0; i < 12; ++i)
+        std::memcpy(&live12[i], &xfmem.posMatrices[m10base + i], 4);
+      const auto& m10v = system.GetVertexShaderManager().constants;
+      const u32 m10pia = g_main_cp_state.matrix_index_a.Hex;
+      const u32 m10pib = g_main_cp_state.matrix_index_b.Hex;
+      int m10which = 0, m10ti = -1;
+      u32 snap12[12] = {};
+      if ((m10pia & 63) == u32(m10_slot)) {
+        m10which = 1;
+        for (u32 r = 0; r < 3; ++r)
+          for (u32 cc = 0; cc < 4; ++cc)
+            std::memcpy(&snap12[r * 4 + cc], &m10v.posnormalmatrix[r][cc], 4);
+      } else {
+        const u32 m10tidx[8] = {(m10pia >> 6) & 63,  (m10pia >> 12) & 63,
+                                (m10pia >> 18) & 63, (m10pia >> 24) & 63,
+                                m10pib & 63,         (m10pib >> 6) & 63,
+                                (m10pib >> 12) & 63, (m10pib >> 18) & 63};
+        for (u32 ti = 0; ti < 8; ++ti) {
+          if (m10tidx[ti] == u32(m10_slot)) {
+            m10which = 2;
+            m10ti = int(ti);
+            for (u32 r = 0; r < 3; ++r)
+              for (u32 cc = 0; cc < 4; ++cc)
+                std::memcpy(&snap12[r * 4 + cc],
+                            &m10v.texmatrices[3 * ti + r][cc], 4);
+            break;
+          }
+        }
+      }
+      if (!s_m10_post_done) {
+        for (u32 i = 0; i < 12; ++i) {
+          s_m10_post_live[i] = live12[i];
+          s_m10_post_snap[i] = snap12[i];
+        }
+        s_m10_snap_which = m10which;
+        s_m10_snap_ti = m10ti;
+        s_m10_post_done = 1;
+      } else {
+        for (u32 i = 0; i < 12; ++i) {
+          if (live12[i] != s_m10_post_live[i]) {
+            ++s_m10_mm_live;
+            break;
+          }
+        }
+        for (u32 i = 0; i < 12; ++i) {
+          if (snap12[i] != s_m10_post_snap[i]) {
+            ++s_m10_mm_snap;
+            break;
+          }
+        }
+      }
+    }
     // read_ptr == write_ptr after a matched pair, so this compacts zero bytes
     // and rewinds both aux pointers to the base of the 2 MiB buffer.
     if (deterministic) fifo.SyncGPU(Fifo::SyncGPUReason::AuxSpace, false);
@@ -2012,6 +2278,128 @@
       Event("m9_surv", surv);
     }
   }
+  // M10 step 2: order + matrix receipts (M10 mode only; M9's receipts above
+  // ride along as cross-checks). m10_order carries the split counts,
+  // m10_loads the covering-load draw clocks, m10_cons the consuming draw
+  // indices (1-based), m10_matrix the 12-word captures as u32 hex.
+  if (m10_mode != 0) {
+    const size_t m10_nload = m10stream.loads.size();
+    const size_t m10_ndraw = m10stream.drawrec.size();
+    u32 m10_idx_cover = 0, m10_direct_cover = 0;
+    u32 m10_arr[16] = {};
+    for (const auto& l : m10stream.loads) {
+      if (l.kind == 0) {
+        ++m10_idx_cover;
+        if (l.array < 16) ++m10_arr[l.array];
+      } else {
+        ++m10_direct_cover;
+      }
+    }
+    u32 m10_cons_pos = 0, m10_cons_tex = 0, m10_cons_any = 0;
+    u32 m10_first_cons = 0, m10_last_cons = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (m10stream.drawrec[d].cons_pos) ++m10_cons_pos;
+      if (m10stream.drawrec[d].cons_texmask) ++m10_cons_tex;
+      if (any) {
+        ++m10_cons_any;
+        if (m10_first_cons == 0) m10_first_cons = u32(d) + 1;
+        m10_last_cons = u32(d) + 1;
+      }
+    }
+    const u32 m10_first_loaddraw =
+        m10_nload ? m10stream.loads.front().draw : 0;
+    const u32 m10_last_loaddraw = m10_nload ? m10stream.loads.back().draw : 0;
+    u32 m10_cons_before = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (any && m10_nload && u32(d) + 1 <= m10_first_loaddraw) ++m10_cons_before;
+    }
+    u32 m10_loads_before = 0, m10_loads_span = 0;
+    for (u32 ld : m10stream.load_draws) {
+      if (m10_nload && ld < m10_first_loaddraw) ++m10_loads_before;
+      if (m10_nload && m10_cons_any && ld >= m10_first_loaddraw &&
+          ld < m10_last_cons)
+        ++m10_loads_span;
+    }
+    char m10o[768];
+    std::snprintf(
+        m10o, sizeof(m10o),
+        "slot=%d word=%u draws=%u verts=%llu idx_loads=%u covering=%zu idx_cover=%u "
+        "direct_cover=%u arr12=%u arr13=%u arr14=%u arr15=%u "
+        "first_load_draw=%u first_load_off=%u first_load_kind=%u "
+        "last_load_draw=%u last_load_off=%u "
+        "cons_pos=%u cons_tex=%u cons_any=%u first_cons=%u last_cons=%u "
+        "cons_before_first=%u cons_at_after_first=%u loads_before_first=%u "
+        "loads_first_to_lastcons=%u seam_hits=%llu seam_per_replay=%llu "
+        "walk=%u/%zu benign=%u walk_ok=%d",
+        m10_slot, m10stream.word, m10stream.draws,
+        (unsigned long long)m10stream.verts, m10stream.idx_loads, m10_nload,
+        m10_idx_cover, m10_direct_cover, m10_arr[12], m10_arr[13], m10_arr[14],
+        m10_arr[15], m10_first_loaddraw,
+        m10_nload ? m10stream.loads.front().off : 0,
+        m10_nload ? m10stream.loads.front().kind : 0, m10_last_loaddraw,
+        m10_nload ? m10stream.loads.back().off : 0, m10_cons_pos, m10_cons_tex,
+        m10_cons_any, m10_first_cons, m10_last_cons, m10_cons_before,
+        m10_cons_any - m10_cons_before, m10_loads_before, m10_loads_span,
+        s_m8_hits, replays ? s_m8_hits / replays : 0, m10stream.consumed,
+        frame.size(), m10stream.benign,
+        int(m10stream.consumed == frame.size() && m10stream.unknown == 0));
+    Event("m10_order", m10o);
+    char m10l[2048];
+    int m10loff = 0;
+    size_t m10ln = 0;
+    for (size_t i = 0; i < m10_nload; ++i) {
+      if (m10loff < 0 || size_t(m10loff) >= sizeof(m10l) - 24) break;
+      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
+                               "%s%u", i ? "," : "", m10stream.loads[i].draw);
+      ++m10ln;
+    }
+    if (m10ln < m10_nload)
+      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
+                               ",TRUNC=%zu", m10_nload);
+    Event("m10_loads", m10l);
+    char m10c[8192];
+    int m10coff = 0;
+    size_t m10cn = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (!any) continue;
+      if (m10coff < 0 || size_t(m10coff) >= sizeof(m10c) - 24) break;
+      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
+                               "%s%u", m10cn ? "," : "", u32(d) + 1);
+      ++m10cn;
+    }
+    if (m10cn < m10_cons_any)
+      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
+                               ",TRUNC=%u", m10_cons_any);
+    Event("m10_cons", m10c);
+    char m10m[1024];
+    int m10moff = std::snprintf(m10m, sizeof(m10m),
+                                "slot=%d word=%u done=%d snap_which=%d snap_ti=%d "
+                                "n=%u mm_live=%u mm_snap=%u before=",
+                                m10_slot, m10stream.word, s_m10_mat_done,
+                                s_m10_snap_which, s_m10_snap_ti, replays,
+                                s_m10_mm_live, s_m10_mm_snap);
+    const u32* m10lists[4] = {s_m10_mat_before, s_m10_mat_after, s_m10_post_live,
+                              s_m10_post_snap};
+    const char* m10tags[4] = {"before=", "after=", "live=", "snap="};
+    for (u32 l = 0; l < 4; ++l) {
+      if (l) {
+        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
+                                 " %s", m10tags[l]);
+      }
+      for (u32 i = 0; i < 12; ++i) {
+        if (m10moff < 0 || size_t(m10moff) >= sizeof(m10m) - 24) break;
+        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
+                                 "%s%08x", i ? "," : "", m10lists[l][i]);
+      }
+    }
+    Event("m10_matrix", m10m);
+  }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);

```

### Step 3

```diff
--- local/research/M9/m9_replay_context.h	2026-09-19 10:40:01
+++ local/research/M10/m10_replay_context.h	2026-09-19 12:16:29
@@ -831,6 +831,250 @@
   return stats;
 }
 
+// --- M10 step 2: hit/draw order stamps + consuming-draw spans -----------------
+// One read-only walk over the verbatim recorded stream (own CPState + numtex
+// state, same seeding as M9CensusWalk). Records in stream order: every XF
+// write covering the delta word (indexed loads via OnIndexedLoad — address is
+// the xfmem word address for every array, XFStructs.cpp LoadIndexedXF — plus
+// direct XF writes via OnXF below 0x1000), and every draw consuming the slot
+// through the shared path (position: shared + PosNormalMtxIdx==slot, no
+// enablement gate; texgen i: shared + enabled + TexiMtxIdx==slot). Positions
+// come from OnCommand, which the vendor calls immediately after each
+// command's specific callback with the command's start pointer and total size
+// (OpcodeDecoding.h RunCommand): specific callbacks push pending records, the
+// next OnCommand stamps offset/size. Display-list bodies are not decoded by
+// the offline Run (the execute pass handles them); mask.dls==0 on these
+// frames, and the report carries the count.
+struct M10LoadRec {
+  u32 draw = 0;   // draws completed before this command (draw clock)
+  u32 off = 0;    // stream byte offset of the command
+  u32 size = 0;   // command byte size
+  u32 kind = 0;   // 0 = indexed load, 1 = direct XF write
+  u32 array = 0;  // CPArray id for indexed loads
+};
+struct M10DrawRec {
+  u32 off = 0;
+  u32 size = 0;
+  u32 cons_pos = 0;
+  u32 cons_texmask = 0;  // bit i = consumes the slot via texgen i
+  // M10 step 3: rasterizer state at draw time (seeded from recorded BPMem).
+  u32 cull = 0;  // GenMode cull_mode (0 none, 1 back, 2 front, 3 all)
+  u32 scis_empty = 0;  // scissor TL>BR in 11-bit coords
+  u32 scis_tl = 0, scis_br = 0;  // raw BP hexes at draw
+  u32 ztest = 0, zfunc = 0, zupdate = 0;  // ZMode at draw
+};
+// M10 step 3: EFB-copy trigger record (register decoding mirrors PeMaskWalk).
+struct M10CopyRec {
+  u32 draw = 0;  // draw clock at trigger
+  u32 dest = 0;  // guest byte address (copyTexDest << 5)
+  u32 bytes = 0;  // height * stride
+  u32 is_xfb = 0;
+  u32 clear = 0;
+  u32 tl = 0;  // copy source-rect top-left raw BP hex (for clear-rect notes)
+  u32 w = 0, h = 0;  // copy source rect w/h as decoded
+};
+struct M10Order {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 unknown = 0;
+  u32 benign = 0;
+  u32 slot = 0;
+  u32 word = 0;
+  u32 idx_loads = 0;  // all indexed loads (any coverage)
+  std::vector<M10LoadRec> loads;  // covering loads, stream order
+  std::vector<M10DrawRec> drawrec;  // per draw (index d-1), stream order
+  std::vector<u32> load_draws;  // draw clock at every indexed load
+  std::vector<M10CopyRec> copies;  // EFB-copy triggers, stream order
+};
+class M10OrderWalk final : public OpcodeDecoder::Callback {
+public:
+  M10OrderWalk(const u8* base, const u32* cp_mem, const u32* xf_regs,
+               const u32* bp_mem, u32 slot, M10Order& stats)
+      : m_base(base), m_cp(cp_mem), m_stats(stats) {
+    m_stats.slot = slot;
+    m_stats.word = slot * 4 + 3;
+    m_numtex = xf_regs[0x3f] & 0xf;
+    // M10 step 3: BP rasterizer/copy state seeded from recorded BPMem.
+    m_gen = bp_mem[BPMEM_GENMODE] & 0xffffffu;
+    m_scis_tl = bp_mem[BPMEM_SCISSORTL] & 0xffffffu;
+    m_scis_br = bp_mem[BPMEM_SCISSORBR] & 0xffffffu;
+    m_zmode = bp_mem[BPMEM_ZMODE] & 0xffffffu;
+    m_tl = bp_mem[BPMEM_EFB_TL] & 0xffffffu;
+    m_wh = bp_mem[BPMEM_EFB_WH] & 0xffffffu;
+    m_dest = bp_mem[BPMEM_EFB_ADDR] & 0xffffffu;
+    m_stride = bp_mem[BPMEM_EFB_STRIDE] & 0xffffffu;
+    m_yscale = bp_mem[BPMEM_COPYYSCALE] & 0xffffffu;
+  }
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address, hi = u32(address) + u32(count);
+    if (lo < 0x1000 && lo <= m_stats.word && m_stats.word < hi) {
+      M10LoadRec r;
+      r.draw = m_stats.draws;
+      r.kind = 1;
+      m_stats.loads.push_back(r);
+      m_pending_load = true;
+    }
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      if (word == XFMEM_SETNUMTEXGENS) {
+        m_numtex = v & 0xf;
+      }
+      if (word == XFMEM_SETMATRIXINDA) {
+        m_cp.matrix_index_a.Hex = v;
+      } else if (word == XFMEM_SETMATRIXINDB) {
+        m_cp.matrix_index_b.Hex = v;
+      }
+    }
+  }
+  void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
+  void OnBP(u8 command, u32 value) override {
+    switch (command) {
+    case BPMEM_GENMODE:
+      m_gen = value;
+      break;
+    case BPMEM_SCISSORTL:
+      m_scis_tl = value;
+      break;
+    case BPMEM_SCISSORBR:
+      m_scis_br = value;
+      break;
+    case BPMEM_ZMODE:
+      m_zmode = value;
+      break;
+    case BPMEM_EFB_TL:
+      m_tl = value;
+      break;
+    case BPMEM_EFB_WH:
+      m_wh = value;
+      break;
+    case BPMEM_EFB_ADDR:
+      m_dest = value;
+      break;
+    case BPMEM_EFB_STRIDE:
+      m_stride = value;
+      break;
+    case BPMEM_COPYYSCALE:
+      m_yscale = value;
+      break;
+    case BPMEM_TRIGGER_EFB_COPY: {
+      M10CopyRec c;
+      c.draw = m_stats.draws;
+      c.is_xfb = (value >> 14) & 1u;
+      c.clear = (value >> 11) & 1u;
+      const u32 w = (m_wh & 0x3ffu) + 1u;
+      const u32 hsrc = (m_wh >> 10) & 0x3ffu;
+      const bool invert = ((value >> 10) & 1u) != 0;
+      float yscale = 1.0f;
+      if (m_yscale != 0)
+        yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
+      c.w = w;
+      c.h = u32(1.0f + float(hsrc) * yscale);
+      c.tl = m_tl;
+      c.dest = m_dest << 5;
+      c.bytes = c.h * (m_stride << 5);
+      m_stats.copies.push_back(c);
+      break;
+    }
+    default:
+      break;
+    }
+  }
+  void OnIndexedLoad(CPArray array, u32, u16 address, u8 size) override {
+    ++m_stats.idx_loads;
+    m_stats.load_draws.push_back(m_stats.draws);
+    const u32 lo = address, hi = u32(address) + u32(size);
+    if (lo <= m_stats.word && m_stats.word < hi) {
+      M10LoadRec r;
+      r.draw = m_stats.draws;
+      r.kind = 0;
+      r.array = static_cast<u32>(array);
+      m_stats.loads.push_back(r);
+      m_pending_load = true;
+    }
+  }
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 v = vat & 7;
+    const u32 comp =
+        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    M10DrawRec d;
+    if ((comp & VB_HAS_POSMTXIDX) == 0 && idx[0] == m_stats.slot) d.cons_pos = 1;
+    for (u32 i = 0; i < 8; ++i) {
+      const bool enabled = i < (m_numtex & 15);
+      if ((comp & (VB_HAS_TEXMTXIDX0 << i)) == 0 && enabled &&
+          idx[1 + i] == m_stats.slot) {
+        d.cons_texmask |= 1u << i;
+      }
+    }
+    d.cull = (m_gen >> 14) & 3u;
+    d.scis_tl = m_scis_tl;
+    d.scis_br = m_scis_br;
+    const u32 tlx = (m_scis_tl >> 12) & 0x7ffu, tly = m_scis_tl & 0x7ffu;
+    const u32 brx = (m_scis_br >> 12) & 0x7ffu, bry = m_scis_br & 0x7ffu;
+    d.scis_empty = (tlx > brx || tly > bry) ? 1 : 0;
+    d.ztest = m_zmode & 1u;
+    d.zfunc = (m_zmode >> 1) & 7u;
+    d.zupdate = (m_zmode >> 4) & 1u;
+    m_stats.drawrec.push_back(d);
+    m_pending_draw = true;
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8 opcode, const u8*) override {
+    if (opcode == 0x44 || opcode == 0x48)
+      ++m_stats.benign;
+    else
+      ++m_stats.unknown;
+  }
+  void OnCommand(const u8* data, u32 size) override {
+    const u32 off = u32(data - m_base);
+    if (m_pending_load && !m_stats.loads.empty()) {
+      m_stats.loads.back().off = off;
+      m_stats.loads.back().size = size;
+      m_pending_load = false;
+    }
+    if (m_pending_draw && !m_stats.drawrec.empty()) {
+      m_stats.drawrec.back().off = off;
+      m_stats.drawrec.back().size = size;
+      m_pending_draw = false;
+    }
+  }
+  CPState& GetCPState() override { return m_cp; }
+
+private:
+  const u8* m_base;
+  CPState m_cp;
+  M10Order& m_stats;
+  u32 m_numtex = 0;
+  bool m_pending_load = false;
+  bool m_pending_draw = false;
+  // M10 step 3: live BP rasterizer/copy state (seeded from recorded BPMem).
+  u32 m_gen = 0;
+  u32 m_scis_tl = 0, m_scis_br = 0;
+  u32 m_zmode = 0;
+  u32 m_tl = 0, m_wh = 0, m_dest = 0, m_stride = 0, m_yscale = 0;
+};
+static M10Order RunM10Order(const std::vector<u8>& src, const u32* cp_mem,
+                            const u32* xf_regs, const u32* bp_mem, u32 slot) {
+  M10Order stats;
+  stats.slot = slot;
+  stats.word = slot * 4 + 3;
+  if (src.empty()) return stats;
+  M10OrderWalk walk(src.data(), cp_mem, xf_regs, bp_mem, slot, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
+  return stats;
+}
+
 // Snapshot of the live video registers, restored after the sequence so the
 // game's own command stream keeps decoding with the state it expects.
 struct LiveState {
@@ -989,6 +1233,22 @@
 static unsigned long long s_m9_vb_mm = 0, s_m9_va_mm = 0;
 static unsigned long long s_m9_hit_dirty_pos = 0, s_m9_hit_dirty_texa = 0;
 static unsigned long long s_m9_hit_dirty_texb = 0, s_m9_hit_dirty_pervtx = 0;
+// --- M10 step 2: 12-word matrix capture --------------------------------------
+// At the first seam hit covering the delta word, captures the slot's full
+// 3x4 matrix (words slot*4..slot*4+11) before and after the +0.1f add;
+// post-replay sampling captures live xfmem + the consumed snapshot's 12
+// words on replay 0 with mismatch tallies across the sequence. Gated on
+// s_m10_cap (M10 mode only); unset = M9 shape.
+static int s_m10_cap = 0;
+static int s_m10_mat_done = 0;
+static u32 s_m10_mat_before[12] = {};
+static u32 s_m10_mat_after[12] = {};
+static u32 s_m10_post_live[12] = {};
+static u32 s_m10_post_snap[12] = {};
+static int s_m10_snap_which = 0;  // 0 = none resident, 1 = shared pos, 2 = shared tex
+static int s_m10_snap_ti = -1;  // resident texgen for which==2
+static unsigned s_m10_mm_live = 0, s_m10_mm_snap = 0;
+static int s_m10_post_done = 0;
 static void M8Transform(u16 address, u32 count) {
   ++s_m8_calls;
   const u32 lo = address, hi = address + count;  // covered words [lo, hi)
@@ -1013,7 +1273,18 @@
       float* f = &xfmem.posMatrices[w];
       u32 vb = 0;
       std::memcpy(&vb, f, 4);  // read-only when s_m9_surv == 0
+      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: pre-add 12-word capture
+        const u32 base = u32(s_m8_slot) * 4;
+        for (u32 i = 0; i < 12; ++i)
+          std::memcpy(&s_m10_mat_before[i], &xfmem.posMatrices[base + i], 4);
+      }
       *f += 0.1f;
+      if (s_m10_cap && !s_m10_mat_done) {  // M10 step 2: post-add 12-word capture
+        const u32 base = u32(s_m8_slot) * 4;
+        for (u32 i = 0; i < 12; ++i)
+          std::memcpy(&s_m10_mat_after[i], &xfmem.posMatrices[base + i], 4);
+        s_m10_mat_done = 1;
+      }
       ++s_m8_hits;
       if (s_m9_surv) {
         u32 va = 0;
@@ -1237,7 +1508,56 @@
   // VAT+texgen walk). Precedence: SLOT > CENSUS; M9 overrides M8 when set.
   // Counting stays on in every M9 mode, so each delta run carries its own
   // M8 census and its own M9 VAT census.
-  const int m9_slot = [] {
+  // M10 steps 2-3: SSX_M10_SLOT=N (0-63) forces M9 mode 2 on the same slot
+  // (all M9 walks + survival receipts ride along as cross-checks) and arms
+  // the M10 order/matrix/epoch instruments. Unset = M9/M8 behavior.
+  const int m10_slot = [] {
+    const char* v = std::getenv("SSX_M10_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m10_mode = m10_slot >= 0 ? 2 : 0;
+  // M10 step 3: SSX_M10_NOPCONS=1 replaces every consuming draw's command
+  // bytes with GX_NOPs in the replayed streams (the verbatim stream is still
+  // walked for receipts); =2 replaces EVERY draw (positive control for the
+  // patch machinery + xdiff chain). Only in M10 mode 2; the delta is
+  // disarmed in NOP modes so xdiff measures pixel contribution alone.
+  const int m10_nopcons = m10_mode == 2 ? ([] {
+                            const char* v = std::getenv("SSX_M10_NOPCONS");
+                            if (v && std::strcmp(v, "2") == 0) return 2;
+                            return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                          })()
+                                        : 0;
+  // M10 step 3: SSX_M10_RAMCOPY=1 forces EFB/XFB copies to RAM for the
+  // sequence (default config skips them: GFX_HACK_SKIP_*_TO_RAM default
+  // true, XFB dest then filled with the fuchsia uninit pattern).
+  // Precedent: the bImmediateXFB flip. Re-applied at every loop top (any
+  // mid-sequence config refresh cannot clobber it); restored after.
+  // SSX_M10_RAMREF=1 (step-3 true-delta arm, needs nop=0): implies RAMCOPY
+  // and splits the sequence at kTransformFrom — replays 0..99 pristine
+  // (counting on, delta off), 100..199 delta — storing replay 99's
+  // rendered scratch frame as ref2 and diffing replays 100+ against it.
+  const int m10_ramcopy = m10_mode == 2 ? ([] {
+                            const char* v = std::getenv("SSX_M10_RAMCOPY");
+                            const char* r = std::getenv("SSX_M10_RAMREF");
+                            const int ref =
+                                (r && std::strcmp(r, "1") == 0) ? 1 : 0;
+                            return (v && std::strcmp(v, "1") == 0) || ref ? 1 : 0;
+                          })()
+                                        : 0;
+  const int m10_ramref =
+      (m10_mode == 2 && m10_nopcons == 0) ? ([] {
+        const char* r = std::getenv("SSX_M10_RAMREF");
+        return r && std::strcmp(r, "1") == 0 ? 1 : 0;
+      })()
+                                         : 0;
+  const int m9_slot = m10_mode != 0 ? m10_slot : [] {
     const char* v = std::getenv("SSX_M9_SLOT");
     if (!v || !*v) return -1;
     int n = 0;
@@ -1248,10 +1568,10 @@
     }
     return n;
   }();
-  const int m9_mode = m9_slot >= 0 ? 2 : ([] {
+  const int m9_mode = m10_mode != 0 ? 2 : (m9_slot >= 0 ? 2 : ([] {
                         const char* v = std::getenv("SSX_M9_CENSUS");
                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
-                      })();
+                      })());
   // M9 step 3: survival sampling (SSX_M9_SURV=1). Arms only with a slot delta
   // (M9 mode 2); elsewhere parsed but inert.
   const int m9_surv = m9_mode == 2 ? ([] {
@@ -1269,6 +1589,13 @@
   const M9Census m9stream = m9_mode != 0 ? RunM9Census(frame, file->GetCPMem(),
                                                        file->GetXFRegs())
                                          : M9Census{};
+  // M10 step 2: hit/draw order stamps + consuming-draw spans (same stream).
+  // M10 step 3: the same walk also records render-target epochs + per-draw
+  // rasterizer state (BP seeded from recorded BPMem).
+  const M10Order m10stream =
+      m10_mode != 0 ? RunM10Order(frame, file->GetCPMem(), file->GetXFRegs(),
+                                  file->GetBPMem(), u32(m10_slot))
+                    : M10Order{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -1353,8 +1680,43 @@
       }
     }
   }
-  const std::vector<u8>& exec_stream = xfb_scratch_ok ? frame_exec : frame;
-  const std::vector<u8>& pre_stream = xfb_scratch_ok ? frame_pre_exec : frame_pre;
+  // M10 step 3: NOP-collective arm. Consuming-draw spans come from the M10
+  // walk over the verbatim stream; both replay streams share its layout
+  // (scratch patch changes BP values, not sizes). Fail closed: any bad span
+  // disables the patch and runs verbatim.
+  std::vector<u8> frame_nop_exec, frame_nop_pre;
+  u32 m10_nop_draws = 0, m10_nop_bytes = 0;
+  bool m10_nop_ok = false;
+  if (m10_nopcons && m10_mode != 0) {
+    frame_nop_exec = frame_exec;
+    frame_nop_pre = frame_pre_exec;
+    bool patch_ok = !m10stream.drawrec.empty();
+    u32 nd = 0, nb = 0;
+    for (size_t d = 0; d < m10stream.drawrec.size(); ++d) {
+      const M10DrawRec& dr = m10stream.drawrec[d];
+      const bool hit = m10_nopcons == 2 || dr.cons_pos != 0 ||
+                       dr.cons_texmask != 0;
+      if (!hit) continue;
+      if (dr.size == 0 || dr.off + dr.size > frame_nop_exec.size() ||
+          dr.off + dr.size > frame_nop_pre.size()) {
+        patch_ok = false;
+        break;
+      }
+      std::memset(frame_nop_exec.data() + dr.off, 0x00, dr.size);
+      std::memset(frame_nop_pre.data() + dr.off, 0x00, dr.size);
+      ++nd;
+      nb += dr.size;
+    }
+    if (patch_ok && nd > 0) {
+      m10_nop_ok = true;
+      m10_nop_draws = nd;
+      m10_nop_bytes = nb;
+    }
+  }
+  const std::vector<u8>& exec_stream =
+      m10_nop_ok ? frame_nop_exec : (xfb_scratch_ok ? frame_exec : frame);
+  const std::vector<u8>& pre_stream =
+      m10_nop_ok ? frame_nop_pre : (xfb_scratch_ok ? frame_pre_exec : frame_pre);
   unsigned xfb_scratch_count = 0;
   unsigned live_same_count = 0;
   unsigned live_ok_count = 0;
@@ -1382,14 +1744,15 @@
     return 0;
   }();
   {
-    char detail[448];
+    char detail[512];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
                   "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
-                  "m9mode=%d m9slot=%d m9surv=%d",
+                  "m9mode=%d m9slot=%d m9surv=%d m10mode=%d m10slot=%d "
+                  "m10nop=%d nopdraws=%u nopbytes=%u m10ram=%d m10ref=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
@@ -1397,10 +1760,19 @@
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
                   xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
-                  m9_mode, m9_slot, m9_surv);
+                  m9_mode, m9_slot, m9_surv, m10_mode, m10_slot, m10_nopcons,
+                  m10_nop_draws, m10_nop_bytes, m10_ramcopy, m10_ramref);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
+  const bool m10_skipx_pre = g_ActiveConfig.bSkipXFBCopyToRam;
+  const bool m10_skipe_pre = g_ActiveConfig.bSkipEFBCopyToRam;
+  const bool m10_defer_pre = g_ActiveConfig.bDeferEFBCopies;
+  if (m10_ramcopy) {
+    g_ActiveConfig.bSkipXFBCopyToRam = false;
+    g_ActiveConfig.bSkipEFBCopyToRam = false;
+    g_ActiveConfig.bDeferEFBCopies = false;
+  }
   g_ActiveConfig.bImmediateXFB = false;
   // M6 step 2: install the scoped bus; the header's own counter moves to it
   // (still counts every trigger) while the live listeners stay on the saved
@@ -1488,7 +1860,7 @@
     s_m8_regcalls = 0;
     for (auto& w : s_m8_writes) w = 0;
     for (auto& r : s_m8_reads) r = 0;
-    s_m8_slot = m9_mode == 2 ? m9_slot : -1;
+    s_m8_slot = (m9_mode == 2 && !m10_nopcons && !m10_ramref) ? m9_slot : -1;
     s_m8_proj = 0;
     s_m9_surv = m9_surv;
     s_m9_first_hit = 0;
@@ -1496,6 +1868,15 @@
     s_m9_vb_mm = s_m9_va_mm = 0;
     s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
     s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
+    s_m10_cap = (m10_mode && !m10_nopcons && !m10_ramref) ? 1 : 0;
+    s_m10_mat_done = 0;
+    s_m10_post_done = 0;
+    s_m10_snap_which = 0;
+    s_m10_snap_ti = -1;
+    s_m10_mm_live = s_m10_mm_snap = 0;
+    for (u32 i = 0; i < 12; ++i)
+      s_m10_mat_before[i] = s_m10_mat_after[i] = s_m10_post_live[i] =
+          s_m10_post_snap[i] = 0;
     XFReplay::g_transform = &M8Transform;
   } else if (m8_mode != 0) {
     s_m8_calls = 0;
@@ -1507,6 +1888,20 @@
     s_m8_proj = m8_mode == 3 ? 1 : 0;
     XFReplay::g_transform = &M8Transform;
   }
+  // M10 step 3: RAMREF ref2 storage + tallies (true-delta arm).
+  std::vector<u8> m10_ref2;
+  bool m10_ref2_ok = false;
+  u64 m10_ref2_hash = 0, m10_hk_hash = 0;
+  unsigned m10_n2 = 0, m10_gt0 = 0, m10_uniform2 = 0;
+  unsigned m10_xd2_min = 0, m10_xd2_max = 0;
+  int m10_xdmax2_max = 0;
+  double m10_xdmean2_min = 0, m10_xdmean2_max = 0;
+  bool m10_xd2_first = true;
+  u32 m10_samp_r[3] = {};
+  unsigned m10_samp_xd[3] = {};
+  int m10_samp_xm[3] = {};
+  double m10_samp_xn[3] = {};
+  unsigned m10_samp_n = 0;
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -1528,6 +1923,15 @@
     // bases, strides and VATs.
     if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
+    if (replays == kTransformFrom && m10_ramref) {  // M10 step 3: arm delta half
+      s_m8_slot = m10_slot;
+      s_m10_cap = 1;
+    }
+    if (m10_ramcopy) {  // M10 step 3: hold the forced-RAM flip every replay
+      g_ActiveConfig.bSkipXFBCopyToRam = false;
+      g_ActiveConfig.bSkipEFBCopyToRam = false;
+      g_ActiveConfig.bDeferEFBCopies = false;
+    }
     ApplyMemory(system, file);
     const double t_mem = Now();
     Run(cp_prelude);
@@ -1604,6 +2008,63 @@
           xfm.GetPerVertexTransformMatrixChanges()[0] >= 0)
         ++m9_dirty_post;
     }
+    // M10 step 2: post-replay 12-word sample (live xfmem + the consumed
+    // snapshot; replay 0 stored, later replays counted by mismatch).
+    if (m10_mode != 0) {
+      const u32 m10base = u32(m10_slot) * 4;
+      u32 live12[12];
+      for (u32 i = 0; i < 12; ++i)
+        std::memcpy(&live12[i], &xfmem.posMatrices[m10base + i], 4);
+      const auto& m10v = system.GetVertexShaderManager().constants;
+      const u32 m10pia = g_main_cp_state.matrix_index_a.Hex;
+      const u32 m10pib = g_main_cp_state.matrix_index_b.Hex;
+      int m10which = 0, m10ti = -1;
+      u32 snap12[12] = {};
+      if ((m10pia & 63) == u32(m10_slot)) {
+        m10which = 1;
+        for (u32 r = 0; r < 3; ++r)
+          for (u32 cc = 0; cc < 4; ++cc)
+            std::memcpy(&snap12[r * 4 + cc], &m10v.posnormalmatrix[r][cc], 4);
+      } else {
+        const u32 m10tidx[8] = {(m10pia >> 6) & 63,  (m10pia >> 12) & 63,
+                                (m10pia >> 18) & 63, (m10pia >> 24) & 63,
+                                m10pib & 63,         (m10pib >> 6) & 63,
+                                (m10pib >> 12) & 63, (m10pib >> 18) & 63};
+        for (u32 ti = 0; ti < 8; ++ti) {
+          if (m10tidx[ti] == u32(m10_slot)) {
+            m10which = 2;
+            m10ti = int(ti);
+            for (u32 r = 0; r < 3; ++r)
+              for (u32 cc = 0; cc < 4; ++cc)
+                std::memcpy(&snap12[r * 4 + cc],
+                            &m10v.texmatrices[3 * ti + r][cc], 4);
+            break;
+          }
+        }
+      }
+      if (!s_m10_post_done) {
+        for (u32 i = 0; i < 12; ++i) {
+          s_m10_post_live[i] = live12[i];
+          s_m10_post_snap[i] = snap12[i];
+        }
+        s_m10_snap_which = m10which;
+        s_m10_snap_ti = m10ti;
+        s_m10_post_done = 1;
+      } else {
+        for (u32 i = 0; i < 12; ++i) {
+          if (live12[i] != s_m10_post_live[i]) {
+            ++s_m10_mm_live;
+            break;
+          }
+        }
+        for (u32 i = 0; i < 12; ++i) {
+          if (snap12[i] != s_m10_post_snap[i]) {
+            ++s_m10_mm_snap;
+            break;
+          }
+        }
+      }
+    }
     // read_ptr == write_ptr after a matched pair, so this compacts zero bytes
     // and rewinds both aux pointers to the base of the 2 MiB buffer.
     if (deterministic) fifo.SyncGPU(Fifo::SyncGPUReason::AuxSpace, false);
@@ -1661,6 +2122,59 @@
         if (xdiff > 0) xdmean = double(xdacc) / double(xdiff);
       }
     }
+    // M10 step 3: RAMREF ref2 capture + diff (forced-RAM true-delta arm).
+    // Replay 99's rendered scratch frame is the pristine reference; replays
+    // 100+ (delta) diff against its bytes. After wall_end, out of wall_ms.
+    if (m10_ramref && xfb_scratch_ok) {
+      u8* r2p = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
+      if (r2p) {
+        if (replays == kTransformFrom - 1) {
+          m10_ref2.assign(r2p, r2p + mask.xfb.bytes);
+          m10_ref2_hash = RamHash(r2p, mask.xfb.bytes);
+          m10_ref2_ok = true;
+        } else if (replays >= kTransformFrom && m10_ref2_ok) {
+          ++m10_n2;
+          const u64 hh = RamHash(r2p, mask.xfb.bytes);
+          if (replays == kTransformFrom) m10_hk_hash = hh;
+          if (hh == m10_hk_hash) ++m10_uniform2;
+          unsigned x2 = 0;
+          int xm2 = 0;
+          unsigned long long xa2 = 0;
+          for (u32 i = 0; i < mask.xfb.bytes; ++i) {
+            const int dd = r2p[i] > m10_ref2[i] ? r2p[i] - m10_ref2[i]
+                                               : m10_ref2[i] - r2p[i];
+            if (dd > 0) {
+              ++x2;
+              xa2 += (unsigned)dd;
+              if (dd > xm2) xm2 = dd;
+            }
+          }
+          const double xn2 = x2 ? double(xa2) / double(x2) : 0.0;
+          if (x2 > 0) {
+            ++m10_gt0;
+            if (m10_samp_n < 3) {
+              m10_samp_r[m10_samp_n] = replays;
+              m10_samp_xd[m10_samp_n] = x2;
+              m10_samp_xm[m10_samp_n] = xm2;
+              m10_samp_xn[m10_samp_n] = xn2;
+              ++m10_samp_n;
+            }
+          }
+          if (m10_xd2_first) {
+            m10_xd2_min = m10_xd2_max = x2;
+            m10_xdmax2_max = xm2;
+            m10_xdmean2_min = m10_xdmean2_max = xn2;
+            m10_xd2_first = false;
+          } else {
+            if (x2 < m10_xd2_min) m10_xd2_min = x2;
+            if (x2 > m10_xd2_max) m10_xd2_max = x2;
+            if (xm2 > m10_xdmax2_max) m10_xdmax2_max = xm2;
+            if (xn2 < m10_xdmean2_min) m10_xdmean2_min = xn2;
+            if (xn2 > m10_xdmean2_max) m10_xdmean2_max = xn2;
+          }
+        }
+      }
+    }
     // M5 step 3: after-state and deltas. Captured after wall_end so the
     // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
     const SideFx fx_after = CaptureSideFx(system);
@@ -2012,8 +2526,267 @@
       Event("m9_surv", surv);
     }
   }
+  // M10 step 2: order + matrix receipts (M10 mode only; M9's receipts above
+  // ride along as cross-checks). m10_order carries the split counts,
+  // m10_loads the covering-load draw clocks, m10_cons the consuming draw
+  // indices (1-based), m10_matrix the 12-word captures as u32 hex.
+  // Post-sequence copy-flag sample (pre sample at sequence start; the flip
+  // is re-applied at every loop top and restored after the receipts).
+  const bool m10_skipx_post = g_ActiveConfig.bSkipXFBCopyToRam;
+  const bool m10_skipe_post = g_ActiveConfig.bSkipEFBCopyToRam;
+  const bool m10_defer_post = g_ActiveConfig.bDeferEFBCopies;
+  if (m10_mode != 0) {
+    const size_t m10_nload = m10stream.loads.size();
+    const size_t m10_ndraw = m10stream.drawrec.size();
+    u32 m10_idx_cover = 0, m10_direct_cover = 0;
+    u32 m10_arr[16] = {};
+    for (const auto& l : m10stream.loads) {
+      if (l.kind == 0) {
+        ++m10_idx_cover;
+        if (l.array < 16) ++m10_arr[l.array];
+      } else {
+        ++m10_direct_cover;
+      }
+    }
+    u32 m10_cons_pos = 0, m10_cons_tex = 0, m10_cons_any = 0;
+    u32 m10_first_cons = 0, m10_last_cons = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (m10stream.drawrec[d].cons_pos) ++m10_cons_pos;
+      if (m10stream.drawrec[d].cons_texmask) ++m10_cons_tex;
+      if (any) {
+        ++m10_cons_any;
+        if (m10_first_cons == 0) m10_first_cons = u32(d) + 1;
+        m10_last_cons = u32(d) + 1;
+      }
+    }
+    const u32 m10_first_loaddraw =
+        m10_nload ? m10stream.loads.front().draw : 0;
+    const u32 m10_last_loaddraw = m10_nload ? m10stream.loads.back().draw : 0;
+    u32 m10_cons_before = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (any && m10_nload && u32(d) + 1 <= m10_first_loaddraw) ++m10_cons_before;
+    }
+    u32 m10_loads_before = 0, m10_loads_span = 0;
+    for (u32 ld : m10stream.load_draws) {
+      if (m10_nload && ld < m10_first_loaddraw) ++m10_loads_before;
+      if (m10_nload && m10_cons_any && ld >= m10_first_loaddraw &&
+          ld < m10_last_cons)
+        ++m10_loads_span;
+    }
+    char m10o[768];
+    std::snprintf(
+        m10o, sizeof(m10o),
+        "slot=%d word=%u draws=%u verts=%llu idx_loads=%u covering=%zu idx_cover=%u "
+        "direct_cover=%u arr12=%u arr13=%u arr14=%u arr15=%u "
+        "first_load_draw=%u first_load_off=%u first_load_kind=%u "
+        "last_load_draw=%u last_load_off=%u "
+        "cons_pos=%u cons_tex=%u cons_any=%u first_cons=%u last_cons=%u "
+        "cons_before_first=%u cons_at_after_first=%u loads_before_first=%u "
+        "loads_first_to_lastcons=%u seam_hits=%llu seam_per_replay=%llu "
+        "walk=%u/%zu benign=%u walk_ok=%d",
+        m10_slot, m10stream.word, m10stream.draws,
+        (unsigned long long)m10stream.verts, m10stream.idx_loads, m10_nload,
+        m10_idx_cover, m10_direct_cover, m10_arr[12], m10_arr[13], m10_arr[14],
+        m10_arr[15], m10_first_loaddraw,
+        m10_nload ? m10stream.loads.front().off : 0,
+        m10_nload ? m10stream.loads.front().kind : 0, m10_last_loaddraw,
+        m10_nload ? m10stream.loads.back().off : 0, m10_cons_pos, m10_cons_tex,
+        m10_cons_any, m10_first_cons, m10_last_cons, m10_cons_before,
+        m10_cons_any - m10_cons_before, m10_loads_before, m10_loads_span,
+        s_m8_hits, replays ? s_m8_hits / replays : 0, m10stream.consumed,
+        frame.size(), m10stream.benign,
+        int(m10stream.consumed == frame.size() && m10stream.unknown == 0));
+    Event("m10_order", m10o);
+    char m10l[2048];
+    int m10loff = 0;
+    size_t m10ln = 0;
+    for (size_t i = 0; i < m10_nload; ++i) {
+      if (m10loff < 0 || size_t(m10loff) >= sizeof(m10l) - 24) break;
+      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
+                               "%s%u", i ? "," : "", m10stream.loads[i].draw);
+      ++m10ln;
+    }
+    if (m10ln < m10_nload)
+      m10loff += std::snprintf(m10l + m10loff, sizeof(m10l) - size_t(m10loff),
+                               ",TRUNC=%zu", m10_nload);
+    Event("m10_loads", m10l);
+    char m10c[8192];
+    int m10coff = 0;
+    size_t m10cn = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const bool any = m10stream.drawrec[d].cons_pos != 0 ||
+                       m10stream.drawrec[d].cons_texmask != 0;
+      if (!any) continue;
+      if (m10coff < 0 || size_t(m10coff) >= sizeof(m10c) - 24) break;
+      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
+                               "%s%u", m10cn ? "," : "", u32(d) + 1);
+      ++m10cn;
+    }
+    if (m10cn < m10_cons_any)
+      m10coff += std::snprintf(m10c + m10coff, sizeof(m10c) - size_t(m10coff),
+                               ",TRUNC=%u", m10_cons_any);
+    Event("m10_cons", m10c);
+    char m10m[1024];
+    int m10moff = std::snprintf(m10m, sizeof(m10m),
+                                "slot=%d word=%u done=%d snap_which=%d snap_ti=%d "
+                                "n=%u mm_live=%u mm_snap=%u before=",
+                                m10_slot, m10stream.word, s_m10_mat_done,
+                                s_m10_snap_which, s_m10_snap_ti, replays,
+                                s_m10_mm_live, s_m10_mm_snap);
+    const u32* m10lists[4] = {s_m10_mat_before, s_m10_mat_after, s_m10_post_live,
+                              s_m10_post_snap};
+    const char* m10tags[4] = {"before=", "after=", "live=", "snap="};
+    for (u32 l = 0; l < 4; ++l) {
+      if (l) {
+        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
+                                 " %s", m10tags[l]);
+      }
+      for (u32 i = 0; i < 12; ++i) {
+        if (m10moff < 0 || size_t(m10moff) >= sizeof(m10m) - 24) break;
+        m10moff += std::snprintf(m10m + m10moff, sizeof(m10m) - size_t(m10moff),
+                                 "%s%08x", i ? "," : "", m10lists[l][i]);
+      }
+    }
+    Event("m10_matrix", m10m);
+    // M10 step 3: render-target epochs + occlusion classes. Overlap is
+    // against the compared XFB range (mask.xfb). A consuming draw is
+    // in-range iff an overlapping copy triggers at/after it with no
+    // clear-copy between (the copy path copies first, then clears the
+    // source rect — BPStructs.cpp "Clear the rectangular region after
+    // copying it" — so a draining copy's own clear bit does not
+    // disqualify it, while an intervening clear-copy wipes the draw's
+    // pixels from EFB); culled iff cull-all, scissor-empty, or
+    // depth-test-on with func Never. Buckets are disjoint by priority
+    // culled > out-of-range > in-range.
+    const size_t m10_ncopy = m10stream.copies.size();
+    std::vector<u32> m10_ovl(m10_ncopy, 0);
+    for (size_t i = 0; i < m10_ncopy; ++i) {
+      const M10CopyRec& cp = m10stream.copies[i];
+      const u32 clo = cp.dest, chi = cp.dest + cp.bytes;
+      const u32 xlo = mask.xfb.addr, xhi = mask.xfb.addr + mask.xfb.bytes;
+      if (mask.xfb.found && mask.xfb.bytes > 0 && cp.bytes > 0 && clo < xhi &&
+          xlo < chi)
+        m10_ovl[i] = 1;
+    }
+    u32 m10_culled = 0, m10_outrange = 0, m10_inrange = 0;
+    u32 m10_cull_all = 0, m10_scis = 0, m10_znever = 0;
+    u32 m10_all_cull = 0, m10_all_scis = 0, m10_all_znever = 0;
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const M10DrawRec& dr = m10stream.drawrec[d];
+      const bool culled = dr.cull == 3 || dr.scis_empty != 0 ||
+                          (dr.ztest != 0 && dr.zfunc == 0);
+      if (dr.cull == 3) ++m10_all_cull;
+      if (dr.scis_empty) ++m10_all_scis;
+      if (dr.ztest && dr.zfunc == 0) ++m10_all_znever;
+      if (dr.cons_pos == 0 && dr.cons_texmask == 0) continue;
+      if (dr.cull == 3) ++m10_cull_all;
+      if (dr.scis_empty) ++m10_scis;
+      if (dr.ztest && dr.zfunc == 0) ++m10_znever;
+      if (culled) {
+        ++m10_culled;
+        continue;
+      }
+      bool ir = false;
+      for (size_t i = 0; i < m10_ncopy; ++i) {
+        const M10CopyRec& cp = m10stream.copies[i];
+        if (cp.draw < u32(d) + 1) continue;
+        if (!m10_ovl[i]) continue;
+        bool barrier = false;
+        for (size_t j = 0; j < m10_ncopy; ++j) {
+          const M10CopyRec& cj = m10stream.copies[j];
+          if (cj.clear && cj.draw >= u32(d) + 1 && cj.draw < cp.draw) {
+            barrier = true;
+            break;
+          }
+        }
+        if (!barrier) {
+          ir = true;
+          break;
+        }
+      }
+      if (ir)
+        ++m10_inrange;
+      else
+        ++m10_outrange;
+    }
+    // Consuming draws per render-target epoch (epoch e = draws strictly
+    // after copy e-1 up to and including copy e's clock; tail past last).
+    std::vector<u32> m10_epoch_cons(m10_ncopy + 1, 0);
+    for (size_t d = 0; d < m10_ndraw; ++d) {
+      const M10DrawRec& dr = m10stream.drawrec[d];
+      if (dr.cons_pos == 0 && dr.cons_texmask == 0) continue;
+      size_t e = 0;
+      while (e < m10_ncopy && m10stream.copies[e].draw < u32(d) + 1) ++e;
+      ++m10_epoch_cons[e];
+    }
+    char m10cp[1024];
+    int m10cpoff = std::snprintf(m10cp, sizeof(m10cp), "n=%zu xfb=0x%08x/%u ",
+                                 m10_ncopy, mask.xfb.addr, mask.xfb.bytes);
+    for (size_t i = 0; i < m10_ncopy; ++i) {
+      const M10CopyRec& cp = m10stream.copies[i];
+      if (m10cpoff < 0 || size_t(m10cpoff) >= sizeof(m10cp) - 128) break;
+      m10cpoff += std::snprintf(
+          m10cp + m10cpoff, sizeof(m10cp) - size_t(m10cpoff),
+          "%sdraw=%u,dest=0x%08x,bytes=%u,xfb=%u,clear=%u,tl=0x%06x,w=%u,h=%u,ovl=%u",
+          i ? ";" : "", cp.draw, cp.dest, cp.bytes, cp.is_xfb, cp.clear, cp.tl, cp.w,
+          cp.h, m10_ovl[i]);
+    }
+    Event("m10_copy", m10cp);
+    char m10oc[1024];
+    int m10ocoff = std::snprintf(
+        m10oc, sizeof(m10oc),
+        "cons=%u culled=%u outrange=%u inrange=%u cull_all=%u scis_empty=%u "
+        "znever=%u all_cull=%u all_scis=%u all_znever=%u all_draws=%zu ncopy=%zu "
+        "epoch_cons=",
+        m10_cons_any, m10_culled, m10_outrange, m10_inrange, m10_cull_all,
+        m10_scis, m10_znever, m10_all_cull, m10_all_scis, m10_all_znever,
+        m10_ndraw, m10_ncopy);
+    for (size_t e = 0; e < m10_ncopy + 1; ++e) {
+      if (m10ocoff < 0 || size_t(m10ocoff) >= sizeof(m10oc) - 24) break;
+      m10ocoff += std::snprintf(m10oc + m10ocoff, sizeof(m10oc) - size_t(m10ocoff),
+                                "%s%u", e ? "," : "", m10_epoch_cons[e]);
+    }
+    Event("m10_occ", m10oc);
+    char m10n[128];
+    std::snprintf(m10n, sizeof(m10n), "nop=%d ok=%d draws=%u bytes=%u",
+                  m10_nopcons, int(m10_nop_ok), m10_nop_draws, m10_nop_bytes);
+    Event("m10_nop", m10n);
+    char m10r[192];
+    std::snprintf(m10r, sizeof(m10r),
+                  "ram=%d skipx_pre=%d skipe_pre=%d defer_pre=%d skipx_post=%d "
+                  "skipe_post=%d defer_post=%d",
+                  m10_ramcopy, int(m10_skipx_pre), int(m10_skipe_pre),
+                  int(m10_defer_pre), int(m10_skipx_post), int(m10_skipe_post),
+                  int(m10_defer_post));
+    Event("m10_ram", m10r);
+    char m10f[512];
+    int m10foff = std::snprintf(
+        m10f, sizeof(m10f),
+        "ref=%d kref=%u refok=%d n2=%u gt0=%u uniform2=%u xd2min=%u xd2max=%u "
+        "xdmax2max=%d xdmean2min=%.3f xdmean2max=%.3f refhash=%016llx samp=",
+        m10_ramref, kTransformFrom, int(m10_ref2_ok), m10_n2, m10_gt0,
+        m10_uniform2, m10_xd2_min, m10_xd2_max, m10_xdmax2_max,
+        m10_xdmean2_min, m10_xdmean2_max,
+        static_cast<unsigned long long>(m10_ref2_hash));
+    for (unsigned s = 0; s < m10_samp_n; ++s) {
+      if (m10foff < 0 || size_t(m10foff) >= sizeof(m10f) - 48) break;
+      m10foff += std::snprintf(m10f + m10foff, sizeof(m10f) - size_t(m10foff),
+                               "%sr%u:%u/%d/%.3f", s ? "," : "", m10_samp_r[s],
+                               m10_samp_xd[s], m10_samp_xm[s], m10_samp_xn[s]);
+    }
+    Event("m10_ref2", m10f);
+  }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
+  if (m10_ramcopy) {
+    g_ActiveConfig.bSkipXFBCopyToRam = m10_skipx_pre;
+    g_ActiveConfig.bSkipEFBCopyToRam = m10_skipe_pre;
+    g_ActiveConfig.bDeferEFBCopies = m10_defer_pre;
+  }
   RestoreLive(live);
   if (ram_size) std::memcpy(live_memory.GetRAM(), saved_ram.data(), ram_size);
   if (exram_size) std::memcpy(live_memory.GetEXRAM(), saved_exram.data(), exram_size);

```
