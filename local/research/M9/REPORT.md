# M9 — Propagation mechanism: VAT paths, texgen enablement, upload timing: REPORT

Slot-36 (Tex2) and slot-0 (PosNormal) reachability through per-draw VAT paths
and per-draw texgen enablement, plus an upload-timing survival test of the
perturbed word (live xfmem vs `SetConstants`-uploaded snapshots), desktop
only. Runbook `local/muse/prompts/M9.md`. No `adb`, no device. No verdicts.

Header read first: `local/research/M8/REPORT.md` (all of it: slot-36 zero,
Tex2-only reference, the "seam writes don't reach rendering" re-scope, "What I
could not do" gaps 1-3), `local/research/M7/REPORT.md` Step 3 (slot-0
PosNormal zero), and the base header `local/research/M8/m8_replay_context.h`.

Time box 6 hours; used about 0.7. One lease wait (P1p held at first check,
free at the next 5-minute poll), four claim/release pairs, no force.

## Baseline note (read before the tables)

The M8 header on disk (`local/research/M8/m8_replay_context.h`, clean tree)
hashes to `c98e5582129302d0da24e472d96770fd0d3c1b0b5fa2fca69a37502bf168ae51`
via `shasum -a 256` (trust `shasum`, not memory; matches the M8 report's pinned
prefix). Step 1 copied the on-disk file verbatim to
`local/research/M9/m9_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6/M7/M8 mechanism is kept in all steps: PE
mask, verbatim execute stream, restore, stall, pipe snapshot, watched-window
re-hash, `done`, XFB hash + scratch redirect, side-effect counters,
continuation capture, scoped bus, `m6frame`, presenter tracing, record guard,
trig_imx probe, M7 full/delta transforms, per-replay xdiff stats, M8 census /
slot / proj modes with their stream-epoch census. All M9 additions are
env-gated with defaults that preserve M8 behavior (`SSX_M9_CENSUS` /
`SSX_M9_SLOT` / `SSX_M9_SURV` all unset); the committed header is the step-3
header, from which every step's run is reproducible via env.

M9 transform modes (M9 overrides M8 when set; counting stays on in every M9
mode, so each delta run carries its own M8 census and its own M9 VAT census):
mode 1 (`SSX_M9_CENSUS=1`, counts only, `xform_stats` mode 10), mode 2
(`SSX_M9_SLOT=N`, N=0-63, M8's +0.1f tx delta on word N\*4+3,
`xform_stats` mode 11). `SSX_M9_SURV=1` arms survival sampling, only in mode
2. M8's `xform_stats` modes 7/8/9 are unchanged on the M8 path.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M8. `m9-det` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile directories are
fresh per run. Each desktop run held `/tmp/ssx3-host-lease` (`printf 'M9\n'`,
removed after each run); the log is `local/research/M9/waits.log` (one P1p wait,
four claim/release pairs, never forced). Builds ran any time; no build ran
during a run. `complete_hazard_resets` (harness field, as observed): m9-det 0,
m9-det2 0, m9-det3 0, m9-det4 0; every sequence is 200/200 with `done` and clean
counters (see tables).

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `c98e5582…` (= M8 on disk) | `players/m9-baseline` | `m9-det-run` (`m9-det`, `SSX_M8_SLOT=36`) | `m9-det-probe.jsonl` |
| 2 census | `5c47b068…` | `players/m9-census` | `m9-det2-run` (`m9-det2`, `SSX_M9_CENSUS=1`) | `m9-det2-probe.jsonl` |
| 3 slot36+surv | `418f9113…` | `players/m9-delta` | `m9-det3-run` (`m9-det3`, `SSX_M9_SLOT=36 SSX_M9_SURV=1`) | `m9-det3-probe.jsonl` |
| 4 slot0+surv | `418f9113…` | `players/m9-delta` | `m9-det4-run` (`m9-det4`, `SSX_M9_SLOT=0 SSX_M9_SURV=1`) | `m9-det4-probe.jsonl` |

The committed header is `418f9113…` (step 3; step 4 adds no header change —
mode 2 with a different slot ships in this header).

Player dirs live under `local/research/M9/players/` (the build driver requires
outputs under `local/`; they are gitignored build outputs, never committed).
Run dirs and every probe jsonl (>5 MB, ~21 MB each) live under
`/Volumes/Extreme SSD/m9/` (symlink-free; `realpath` is the path as written).
Probes, runs and players are not committed.

## Step 1 — baseline (M8 end state reproduces)

Unmodified copy, M8 slot-36 delta env. `analyze.py` prints 200 rows + `done` +
`xfb_equal_scratch=200/200` + `live_xfb_untouched=1` +
`dafter_live`/`dframe`/`dpres`/`dimx` all 0/0. Control for steps 2-4.

Seam-application receipt (`xform_stats`, M8 slot mode):

| Field | Value |
| --- | --- |
| `mode` | 8 |
| `slot` | 36 |
| `calls` | 332600 (1663/replay = the run's `indexed` count) |
| `hits` | 21400 (107/replay covering word 147) |
| `regcalls` | 0 |

107 vs M8's 53 is frame variation (this frame: 335901 B / 1663 indexed; M8's
det3: 295842 B / 1050 indexed; hits/indexed = 6.4% here vs 5.0% there — M8's
own slot-36 range across runs), same phenomenon: triple-digit seam hits per
replay, zero bytes differ.

Own-frame M8 census, m9-det (draws=1526, verts=31044, epochs=177,
matidx 210/210, numtex_w=26, walk_ok=1):

| Expr | Draws by slot |
| --- | --- |
| PosNormal | 0:805 3:84 6:63 9:90 12:84 15:79 18:86 21:90 24:40 27:105 |
| Tex0 | 30:815 60:711 |
| Tex1 | 60:1526 |
| Tex2 | 36:1526 |
| Tex3 | 39:1526 |
| Tex4 | 42:1526 |
| Tex5 | 45:1526 |
| Tex6 | 48:1526 |
| Tex7 | 51:1526 |

## Per-step wall table (all four arms)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m9-det | 200 | 3.116 / 4.203 / 2.624 / 7.982 | 1.752 / 2.016 | 335901 / 2814 | YES | seq_wall_ms=1038.335 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m9-det2 | 200 | 2.442 / 3.209 / 1.894 / 7.911 | 1.320 / 1.501 | 266923 / 2382 | YES | seq_wall_ms=897.977 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m9-det3 | 200 | 3.014 / 4.148 / 2.543 / 8.425 | 1.712 / 1.997 | 334601 / 2837 | YES | seq_wall_ms=1024.102 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m9-det4 | 200 | 2.540 / 3.533 / 2.117 / 8.330 | 1.375 / 1.643 | 284471 / 2474 | YES | seq_wall_ms=946.992 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (266923 … 335901 B), so wall medians are not comparable
across rows as mechanism costs (M5 §Per-step wall table). All four rows:
200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2 dls=0 walk=100%
unknown=0 benign=1` in all runs.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m9-det | 0.096 | 0.001 | 0.029 | 2.989 | 0.001 | 4.063 |
| m9-det2 | 0.084 | 0.001 | 0.022 | 2.333 | 0.001 | 3.079 |
| m9-det3 | 0.120 | 0.001 | 0.032 | 2.863 | 0.001 | 3.975 |
| m9-det4 | 0.085 | 0.001 | 0.025 | 2.428 | 0.001 | 3.402 |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m9-det | 1663 | 79824 | 26.3 |
| m9-det2 | 1020 | 48960 | 42.8 |
| m9-det3 | 1852 | 88896 | 23.6 |
| m9-det4 | 1037 | 49776 | 42.1 |

## Step 2 — VAT + texgen closure (M8 gaps 1-3)

Two instruments, both header-only, both env-gated (unset = M8 behavior):

- (a) **per-draw VAT path**: `M9CensusWalk` tracks CP VCD/VAT state through
  in-stream CP writes and calls the vendor's own
  `VertexLoaderBase::GetVertexComponents(vtx_desc, vtx_attr[vat])` at every
  draw, recording `VB_HAS_POSMTXIDX` / `VB_HAS_TEXMTXIDXi` (shared vs indexed
  per position + per texgen). Shared reach counts only draws that can consume
  the shared slot: position draws on the shared path (no enablement gate),
  texgen draws on the shared path AND enabled (`i < numtex`).
  Indexed-path draws are counted per expression as totals only: per-vertex
  indices are not decoded, so attributing them to index-state slots would
  repeat M8's over-count (see "What I could not do").
- (b) **per-draw texgen enablement**: live XF 0x103f low nibble
  (`numTexGens = value & 15`, `XFStructs.cpp:141-144`), seeded from the
  recorded frame-start value and advanced through the `numtex_w` in-stream
  writes; texgen types from XF 0x1040-0x1047 (`TexMtxInfo.texgentype`, bits
  4-6) tracked alongside.

Walk cross-checks, m9-det2 (M8 walk vs M9 walk on the same stream): draws
1346 = 1346, verts 23218 = 23218, matidx_cp 176 = 176, matidx_xf 176 = 176,
numtex_w 19 = 19, consumed == size both, walk_ok=1 both. `m9_meta`:
`draws=1346 verts=23218 vcd_lo=19 vcd_hi=19 vat_w=0 numtex0=0x1 numtex_w=19
texinfo_w=23 epochs=12`.

Per-draw path table, m9-det2 (draws; VAT decode + enablement):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1295 | 51 | n/a | n/a |
| Tex0 | 1346 | 0 | 1325 | 1325 |
| Tex1 | 1304 | 42 | 460 | 418 |
| Tex2 | 1346 | 0 | 21 | 21 |
| Tex3 | 1346 | 0 | 0 | 0 |
| Tex4 | 1346 | 0 | 0 | 0 |
| Tex5 | 1346 | 0 | 0 | 0 |
| Tex6 | 1346 | 0 | 0 | 0 |
| Tex7 | 1346 | 0 | 0 | 0 |

Texgen enablement, m9-det2: `numtex_hist` (draws at numtex 0..15) =
21,865,439,21,0,0,0,0,0,0,0,0,0,0,0,0. Epoch timeline (1-based draw:numtex)
= `1:0,20:1,58:2,388:3,404:2,455:3,460:2,518:1,1279:0,1280:1,1284:0,1285:1`
(12 epochs). Tex2 enabled on 21 draws (numtex=3 epochs 388-403 and 455-459);
Tex3-7 enabled on 0 draws. `vat_hist` (draws per vat 0..7) =
125,51,738,0,2,0,430,0.

Texgen types, m9-det2 (draws per texgen at draw time, enabled or not; Regular
= matrix consumed, Color0/1 = matrix bypassed, EmbossMap = bump path):

| texgen | Regular | EmbossMap | Color0 | Color1 |
| --- | ---: | ---: | ---: | ---: |
| Tex0 | 1346 | 0 | 0 | 0 |
| Tex1 | 1346 | 0 | 0 | 0 |
| Tex2 | 1346 | 0 | 0 | 0 |
| Tex3 | 1346 | 0 | 0 | 0 |
| Tex4 | 1346 | 0 | 0 | 0 |
| Tex5 | 1346 | 0 | 0 | 0 |
| Tex6 | 1346 | 0 | 0 | 0 |
| Tex7 | 1346 | 0 | 0 | 0 |

Shared reach, m9-det2 (the corrected per-slot answer):

| Expr | Draws by slot (shared [+enabled]) |
| --- | --- |
| PosNormal | 0:664 3:106 6:76 9:65 12:112 15:62 18:61 21:46 24:64 27:39 (total 1295) |
| Tex0 | 30:740 60:585 (total 1325) |
| Tex1 | 60:418 (total 418) |
| Tex2 | 36:21 (total 21) |
| Tex3-7 | (all zero) |

Recorded without verdict: M8's index-state attribution on this same frame
says PosNormal 0:715 and Tex2 36:1346; the VAT walk says shared-position
slot-0 reach is 664 (715 − 664 = 51 = `pos_indexed`: every indexed-position
draw on this frame carries index-state 0) and shared+enabled Tex2 slot-36
reach is 21 (Tex2 enabled 21/1346; Tex2 path shared on all 1346; type Regular
on all 1346). Tex1's 42 indexed draws are exactly the enabled-but-indexed
remainder (460 − 418 = 42).

## Step 3 — upload-timing test (slot 36 + survival)

Code paths (read-only; no vendor change). Every matrix the vertex shader
consumes arrives via a `SetConstants`-uploaded snapshot; the only live-xfmem
read in the render path is the z-slope CPU path:

| # | Consumer | Source snapshot | Upload site | Dirty trigger | Shader use |
| --- | --- | --- | --- | --- | --- |
| 1 | shared position | `constants.posnormalmatrix[0..2]` ← `xfmem.posMatrices[idx*4]`, 3x float4 | `VertexShaderManager::SetConstants`, `VertexShaderManager.cpp:289-301` (`DidPosNormalChange`) | `XFStateManager::InvalidateXFRange` overlap with current `PosNormalMtxIdx` (`XFStateManager.cpp:54-64`) or index change (`:172-182`) | `I_POSNORMALMATRIX[0..2]`, `VertexShaderGen.cpp:118-124`; applied `vertex_input.position * dolphin_position_matrix()` with `rawpos.w=1`, `:884-888` |
| 2 | shared texgen i | `constants.texmatrices[3i..3i+2]` ← indexed slot rows | `VertexShaderManager.cpp:303-335` (`DidTexMatrixA/BChange`) | `InvalidateXFRange` overlap with current `TexiMtxIdx` (`XFStateManager.cpp:66-88`) or index change | `I_TEXMATRICES[3i..3i+2]`, `VertexShaderGen.cpp:191-204`; `coord.w=1`, `:639-671`, so the `.w` lane contributes |
| 3 | indexed (per-vertex) | `constants.transformmatrices[]` ← `xfmem.posMatrices` range | `VertexShaderManager.cpp:179-189` (min/max range) | any pos-matrix-range write (`XFStateManager.cpp:90-107`) | `I_TRANSFORMMATRICES[posidx..+2]` by per-vertex `posmtx`/`rawtex.z`, `VertexShaderGen.cpp:105-116,176-189`; presence from VCD via `VertexLoaderBase::GetVertexComponents`, `VertexLoaderBase.cpp:206-215` |
| 4 | upload→draw order | same `constants` struct | `VertexManagerBase::Flush`: `SetConstants` (`:599`) … `RenderDrawCall` (`:661`) → `UploadUniforms` (`:1072`, backend override) → `SetPipeline` → `DrawIndexed` | — | one Flush uploads then draws; draws in later flushes see earlier hits |
| 5 | seam order | live `xfmem` write + `+0.1f` | `LoadIndexedXF`: `XFMemWritten` → Flush (consumes old flags, draws pending with old constants) → data write → `g_transform` (`XFStructs.cpp:294-301`); `changed=true` whenever the seam is installed (`:288`) | — | the perturbed value reaches the *next* Flush's upload, never the current one |
| 6 | live-xfmem read (non-render) | `xfmem.posMatrices` read directly | `VertexShaderManager::TransformToClipSpace`, `VertexShaderManager.cpp:458-460` | n/a | sole caller `CalculateZSlope`, `VertexManagerBase.cpp:729` (z-freeze CPU path); result unused unless `zfreeze` |

Run receipts, m9-det3 (`SSX_M9_SLOT=36 SSX_M9_SURV=1`; 1500 draws):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 36 |
| `calls` | 370400 (1852/replay = the run's `indexed` count) |
| `hits` | 21000 (105/replay covering word 147) |
| `regcalls` | 0 |

Seam-side survival (`m9_surv` hit aggregates over 21000 hits):

| Field | Value |
| --- | --- |
| `vbefore` / `vafter` (first hit) | `0x00000000` / `0x3dcccccd` (`0` / `0.1`) |
| `vb_mm` / `va_mm` | 9200 / 1200 (hits whose pre/post-add word differed from the first hit's) |
| `hdirty_pos` / `hdirty_texa` / `hdirty_texb` / `hdirty_pervtx` | 15000 / 21000 / 2000 / 21000 (dirty flags set by the covering write) |

Post-replay survival trichotomy, m9-det3 (per-replay end state vs the
first-hit before/after hexes, exact u32 compare; n=200):

| sample | perturbed (==after) | pristine (==before) | other |
| --- | ---: | ---: | ---: |
| live xfmem | 200 | 0 | 0 |
| per-vertex snapshot | 200 | 0 | 0 |
| shared-pos snapshot | 0 (resident 0/200: post-frame `PosNormalMtxIdx` never 36) | 0 | 0 |
| shared-tex snapshot | 200 (resident 200/200) | 0 | 0 |

`dirty_post=0` (no pending upload after the last Flush), `zfreeze=0` (the
live-read consumer is off).

Own-frame VAT census, m9-det3 (`m9_meta`: draws=1500 verts=30563 vcd_lo=23
vcd_hi=23 vat_w=0 numtex_w=23 texinfo_w=29 epochs=14; M8 cross-checks equal:
draws/verts/matidx 174/174/numtex_w 23; texgen types all Regular):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1403 | 97 | n/a | n/a |
| Tex0 | 1500 | 0 | 1464 | 1464 |
| Tex1 | 1417 | 83 | 515 | 432 |
| Tex2 | 1500 | 0 | 21 | 21 |
| Tex3 | 1500 | 0 | 9 | 9 |
| Tex4-7 | 1500 | 0 | 0 | 0 |

Enablement: `numtex_hist` = 36,949,494,12,9,0,…; timeline =
`1:0,35:1,73:2,401:4,410:2,479:3,484:2,492:3,499:2,588:1,1436:0,1437:1,1439:0,1440:1`
(Tex2 enabled on 21 draws: numtex=3 epochs 479-483, 492-498 plus the numtex=4
epoch 401-409; Tex3 enabled on the 9 numtex=4 draws). Shared reach: Pos
0:773 (M8 index-state 0:870; 870 − 773 = 97 = `pos_indexed`), Tex0 30:692
60:772, Tex1 60:432, Tex2 36:21, Tex3 39:9, Tex4-7 zero. `vat_hist` =
267,97,690,0,2,0,444,0.

Survival table per draw class, m9-det3 (slot 36, word 147):

| Draw class (draws) | Matrix source consumed | Perturbed in snapshot? (run receipt) | Pixels |
| --- | --- | --- | --- |
| Tex2 shared+enabled, Regular (21) | `texmatrices[6..8]` snapshot (path 2) | yes: `tex_after=200/200`, resident 200/200 | xdiff 0/200 |
| Tex2 shared+disabled (1479) | none (texgen off; loop bounded by numTexGens; unused coords zeroed) | n/a (not consumed) | 0 |
| Tex2 indexed (0) | — | — (no such draws) | — |
| Position-indexed draws (97; per-vertex path) | `transformmatrices[posidx]` snapshot (path 3) | snapshot perturbed (`pv_after=200/200`); per-vertex indices not decoded, so slot-36 exposure unknown | 0 |
| All other draws | other slots' words | unaffected by the word-147 delta | 0 |

Pixel quantification (per-replay scratch-vs-live-original diff over 573440
bytes):

| Arm | differing frames | xdiff min / max / mean | xdmax min / max | xdmean min / max |
| --- | ---: | --- | ---: | --- |
| m9-det3 | 0 | 0 / 0 / 0 | 0 / 0 | 0.000 / 0.000 |

`xdiff>0 replays = 0/200` (sample rows 0/1/100/199 all 0/0/0.000).
Counters: `dtex` 0/1, `dpend`/`dframe`/`dafter_live`/`dpres`/`dimx`/
`trig_imx` 0/0, `dafter` 1/1, `pediff`/`vidiff` 0/0. Sequence absolutes: tex
101→102, pend 0→0, fc 6848→6848, imx 0→0.

Mechanism table, slot 36 (each row: code path + run receipt):

| Candidate | Standing | Code path | Run receipt |
| --- | --- | --- | --- |
| upload timing (perturbed value never uploaded) | excluded | paths 4-5 | `tex_after=200/200`, `pv_after=200/200`, `hdirty_texa=21000/21000`, `dirty_post=0` |
| shadow copy (stale snapshot served) | excluded | paths 1-3 | snapshots hold `vafter`, never `vbefore` (0 `*_before` in all four rows) |
| indexed-copy bypass | n/a for Tex2 (0 indexed draws); open for position-indexed vertices | path 3 | `tex_indexed[2]=0`; 97 pos-indexed draws' per-vertex indices not decoded |
| live-xfmem read | no rendering consumer | path 6 | `zfreeze=0` |
| texgen disabled | explains 1479/1500 Tex2 draws only | loop bounded by numTexGens (`VertexShaderGen.cpp:164`) + enablement table | 21 draws remain shared+enabled+Regular |
| narrowed residue | 21 shared+enabled Regular-Tex2 draws consume perturbed `texmatrices[6..8]` yet 0/200 frames differ | — | see "What I could not do" 1, 3-6 for the discriminating instruments |

## Step 4 — PosNormal-path delta (slot 0 + survival)

Recorded choice: slot 0. The runbook prescribes a slot the Step-2 receipts
prove flows through the SHARED position path on visible draws; the receipt is
the shared-position reach column:

| Slot | det2 shared-pos reach | det3 shared-pos reach | det4 shared-pos reach |
| ---: | ---: | ---: | ---: |
| 0 | 664 | 773 | 800 |
| 3 | 106 | 77 | 119 |
| 6 | 76 | 69 | 85 |
| 9 | 65 | 90 | 83 |
| 12 | 112 | 43 | 72 |
| 15 | 62 | 79 | 63 |
| 18 | 61 | 50 | 85 |
| 21 | 46 | 81 | 62 |
| 24 | 64 | 54 | 73 |
| 27 | 39 | 87 | 43 |

Slot 0 is the largest on all three M9 frames (664/773/800 shared-position
draws). Same +0.1f translation on the slot's 4th column (word 0\*4+3 = 3,
the M7 word), same pure-function shape. Installed via `SSX_M9_SLOT=0`
(+ `SSX_M9_SURV=1`); `restored` reads `m9mode=2 m9slot=0 m9surv=1`; all 200
rows tag `xform=1`.

Seam-application receipt (`xform_stats`):

| Field | Value |
| --- | --- |
| `mode` / `slot` | 11 / 0 |
| `calls` | 207400 (1037/replay = the run's `indexed` count) |
| `hits` | 14800 (74/replay covering word 3) |
| `regcalls` | 0 |

Seam-side survival (`m9_surv` hit aggregates over 14800 hits):

| Field | Value |
| --- | --- |
| `vbefore` / `vafter` (first hit) | `0x00000000` / `0x3dcccccd` (`0` / `0.1`) |
| `vb_mm` / `va_mm` | 13800 / 13800 |
| `hdirty_pos` / `hdirty_texa` / `hdirty_texb` / `hdirty_pervtx` | 11200 / 2001 / 1601 / 14800 |

Post-replay survival trichotomy, m9-det4 (n=200):

| sample | perturbed (==after) | pristine (==before) | other |
| --- | ---: | ---: | ---: |
| live xfmem | 200 | 0 | 0 |
| per-vertex snapshot | 200 | 0 | 0 |
| shared-pos snapshot | 200 (resident 200/200) | 0 | 0 |
| shared-tex snapshot | 0 (resident 0/200: post-frame `TexiMtxIdx` never 0) | 0 | 0 |

`dirty_post=0`, `zfreeze=0`.

Own-frame VAT census, m9-det4 (`m9_meta`: draws=1534 verts=24377 vcd_lo=21
vcd_hi=21 vat_w=0 numtex_w=21 texinfo_w=25 epochs=12; M8 cross-checks equal;
texgen types all Regular):

| expr | shared | indexed | enabled | shared+enabled |
| --- | ---: | ---: | ---: | ---: |
| Pos | 1485 | 49 | n/a | n/a |
| Tex0 | 1534 | 0 | 1515 | 1515 |
| Tex1 | 1492 | 42 | 474 | 432 |
| Tex2 | 1534 | 0 | 21 | 21 |
| Tex3-7 | 1534 | 0 | 0 | 0 |

Enablement timeline =
`1:0,18:1,56:2,309:3,325:2,464:3,469:2,530:1,1471:0,1472:1,1474:0,1475:1`
(Tex2 enabled on 21 draws: numtex=3 epochs 309-324 and 464-468). Shared
reach: Pos 0:800 (M8 index-state 0:849; 849 − 800 = 49 = `pos_indexed`),
Tex0 30:794 60:721, Tex1 60:432, Tex2 36:21, Tex3-7 zero. `vat_hist` =
247,49,792,0,2,0,444,0.

Pixel quantification (per-replay scratch-vs-live-original diff over 573440
bytes):

| Arm | differing frames | xdiff min / max / mean | xdmax min / max | xdmean min / max |
| --- | ---: | --- | ---: | --- |
| m9-det4 | 0 | 0 / 0 / 0 | 0 / 0 | 0.000 / 0.000 |

`xdiff>0 replays = 0/200` (no nonzero-pixel run; the mechanism does not
permit it on this frame).

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m9-det4 | dtex | 0 | 1 |
| m9-det4 | dpend | 0 | 0 |
| m9-det4 | dframe | 0 | 0 |
| m9-det4 | dafter | 1 | 1 |
| m9-det4 | dafter_live | 0 | 0 |
| m9-det4 | dpres | 0 | 0 |
| m9-det4 | dimx | 0 | 0 |
| m9-det4 | trig_imx | 0 | 0 |
| m9-det4 | pediff | 0 | 0 |
| m9-det4 | vidiff | 0 | 0 |
```

Sequence absolutes: tex 96→97, pend 0→0, fc 6791→6791, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=13577 first_imm_fc=6788`. `done` stands (watched-window re-hash
clean); `xfb_equal=200/200`, `live_xfb_untouched=1`; guest/event unchanged;
continuation `0cbfe49a0d4ee325` (see §Continuation check).

Mechanism table, slot 0 (each row: code path + run receipt; paths as in
Step 3):

| Candidate | Standing | Run receipt |
| --- | --- | --- |
| upload timing | excluded | `pos_after=200/200` (resident 200/200), `pv_after=200/200`, `hdirty_pervtx=14800/14800`, `dirty_post=0` |
| shadow copy | excluded | snapshots hold `vafter`, never `vbefore` |
| indexed-copy bypass | excluded for the 800 shared draws (shared path proven per draw); open for the 49 pos-indexed draws' vertices | `pos_shared=1485`, slot-0 reach 800; per-vertex indices not decoded |
| texgen disabled | n/a (position has no enablement gate) | — |
| narrowed residue | 800 shared-position draws consume perturbed `posnormalmatrix[0..2]` yet 0/200 frames differ | see "What I could not do" 1, 3-5 |

Corrected reach summary, both slots (M8 index-state attribution vs M9
shared[+enabled] reach, per run; det1 ran the step-1 header, M8 columns
only):

| Slot (expr) | det1 M8 | det2 M8 → M9 | det3 M8 → M9 | det4 M8 → M9 |
| --- | ---: | ---: | ---: | ---: |
| 36 (Tex2) | 1526 | 1346 → 21 | 1500 → 21 | 1534 → 21 |
| 0 (PosNormal) | 805 | 715 → 664 | 870 → 773 | 849 → 800 |
| 39 (Tex3) | 1526 | 1346 → 0 | 1500 → 9 | 1534 → 0 |
| 42/45/48/51 (Tex4-7) | 1526 ea. | 1346 → 0 ea. | 1500 → 0 ea. | 1534 → 0 ea. |
| 30 (Tex0) | 815 | 740 → 740 | 692 → 692 | 794 → 794 |
| 60 (Tex0/Tex1) | 711/1526 | 606/1346 → 585/418 | 808/1500 → 772/432 | 740/1534 → 721/432 |

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m9-det | `fc=6790` | `replay_disabled=0 fc=6793 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m9-det2 | `fc=6800` | `replay_disabled=0 fc=6803 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m9-det3 | `fc=6845` | `replay_disabled=0 fc=6848 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m9-det4 | `fc=6788` | `replay_disabled=0 fc=6791 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ); the
quadruple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same address and
size, also identical to all M8/M7 sequence hashes and all M6 sequence and M5
sequence/disabled hashes) is tabulated as observed. `resume fc − fc0 = 3` in
each run (the live record window; per-replay `dframe` sums are 0/0/0/0).

S2 item-5 honesty gate per run (original-frame equality, unchanged guest and
event state, clean continuation):

| Run | `xfb_equal` / scratch | `live_xfb_untouched` | guest (`pediff`/`vidiff`) | event (`dafter_live`/`dframe`/`dpres`/`dimx`) | continuation |
| --- | --- | :-: | --- | --- | --- |
| m9-det | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m9-det2 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m9-det3 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |
| m9-det4 | 200/200 / 200/200 | 1 | 0/0 | 0/0/0/0 | `0cbfe49a0d4ee325` |

## Exact commands

Builds (any time; only the header path differs from
`local/research/M8/build_replay_player.py`):

```
python3 local/research/M9/build_replay_player.py local/research/M9/players/m9-baseline
python3 local/research/M9/build_replay_player.py local/research/M9/players/m9-census
python3 local/research/M9/build_replay_player.py local/research/M9/players/m9-delta
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M9\n'`, remove after
each run; profiles fresh per run):

```
SSX_M8_SLOT=36 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m9/m9-det-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M9/players/m9-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m9-det --cpu-thread --output "/Volumes/Extreme SSD/m9/m9-det-run" --seconds 240
SSX_M9_CENSUS=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m9/m9-det2-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M9/players/m9-census --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m9-det2 --cpu-thread --output "/Volumes/Extreme SSD/m9/m9-det2-run" --seconds 240
SSX_M9_SLOT=36 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m9/m9-det3-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M9/players/m9-delta --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m9-det3 --cpu-thread --output "/Volumes/Extreme SSD/m9/m9-det3-run" --seconds 240
SSX_M9_SLOT=0 SSX_M9_SURV=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m9/m9-det4-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M9/players/m9-delta --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m9-det4 --cpu-thread --output "/Volumes/Extreme SSD/m9/m9-det4-run" --seconds 240
```

Analysis:

```
python3 local/research/M9/analyze.py "m9-det=/Volumes/Extreme SSD/m9/m9-det-probe.jsonl" "m9-det2=/Volumes/Extreme SSD/m9/m9-det2-probe.jsonl" "m9-det3=/Volumes/Extreme SSD/m9/m9-det3-probe.jsonl" "m9-det4=/Volumes/Extreme SSD/m9/m9-det4-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M9/` — `m9_replay_context.h`
(`418f9113…`), `build_replay_player.py`, `analyze.py`, `REPORT.md`, `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m9/` —
`m9-det-probe.jsonl`, `m9-det2-probe.jsonl`, `m9-det3-probe.jsonl`,
`m9-det4-probe.jsonl` (~21 MB each) and the matching `-run` dirs and `-run.log`
harness receipts; `analyze-all.txt` (the four-arm analyzer output) and
`analyze-det{,2,3,4}.txt` (per-arm outputs); per-step header snapshots
`m9_replay_context.step1.h`, `m9_replay_context.step2.h`,
`m9_replay_context.step3.h` (= committed header). Players (gitignored):
`local/research/M9/players/{m9-baseline,m9-census,m9-delta}/` (each with
`player`, `build.json`, launchers). All paths above are symlink-free as
written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` / `player_sha256`,
12-char prefixes): `m9-baseline` `c98e55821293` / `ac4fe91bfc6f` (player hash
identical to M8's `m8-delta`: same header compiles to the same binary),
`m9-census` `5c47b0681523` / `c339e91fc811`,
`m9-delta` `418f9113600e` / `f27c29a4eafd`.

## What I could not do

- No per-draw execute-pass logging exists header-only: `OpcodeDecoder`
  callbacks serve offline stream decode, and `Flush`/`SetConstants` are
  vendor-called with no header hook, so "at each draw, the live word plus the
  consumed source" is sampled seam-side (write time: value before/after +
  dirty flags) and post-frame (live xfmem vs snapshots), then joined to draw
  classes via the stream census — per-class survival, not per-draw
  observation. A per-draw receipt needs a vendor execute-pass hook (ordered
  follow-up, not this runbook).
- Per-vertex matrix indices (`pnmtxidx` into `transformmatrices`) are not
  decoded: the 49-97 indexed-position draws and 42-83 indexed-Tex1 draws per
  frame have unknown slot exposure. Direct vertices are inline in the stream;
  indexed vertices need guest-RAM array walks at setup — not built.
- Hit/draw stream order is not recorded: the 74-105 covering hits per replay
  cannot be ordered against the consuming draws, so the "perturbation lands
  after consumption" upload-timing variant (loads trailing their draws) is
  neither confirmed nor excluded. Discriminating instrument: stream-position
  stamps for covering loads and consuming draws in one walk.
- Full-matrix values are not captured (only the delta word's before/after at
  hits): the other 11 words of the slot-0/slot-36 matrices are unknown.
  Discriminating instrument: 12-word capture at the first hit.
- Per-draw render-target/occlusion/visibility attribution is not built (2-6
  non-XFB EFB copies per frame; the XFB compare covers the XFB range only):
  which consuming draws rasterize into the compared range, or are
  occluded/culled, is unknown. Discriminating instrument: per-draw
  render-target epochs + occlusion queries.
- The texcoord-consumer side (TEV/pixel stage, sampled textures) is not
  instrumented: why the 21 perturbed Tex2 draws move zero UV-dependent
  pixels is not resolved beyond the vertex-stage receipts.
- No follow-up delta run on any other slot (e.g. slot 30 = Tex0 shared+enabled
  on 692-794 draws): step 4 prescribes one PosNormal-path slot. Ordered
  follow-up beyond this runbook, not a gap in it.
- Player dirs are under `local/research/M9/players/` rather than the SSD: the
  build driver refuses outputs outside `local/`, and the brief orders changing
  only the header path it compiles in. Run dirs and all >5 MB probes are on
  the SSD as ordered.
- Desktop only; no device work.

## Files

Committed under `local/research/M9/`: `m9_replay_context.h` (research header,
`418f9113…`), `build_replay_player.py` (M8 driver, header path only),
`analyze.py` (M8 tables unchanged + M9 `m9_meta`/`m9_path`/`m9_texen`/
`m9_texep`/`m9_vat`/`m9_textype`/`m9_reachp`/`m9_reach0-7`/`m9_surv` parsing,
VAT path tables, texgen type tables, shared-reach histograms, survival
trichotomy; missing keys print as n/a / sections skipped), `REPORT.md` (this
file), `waits.log` (one P1p wait, four claim/release pairs).

## Header diffs per step (`diff -u` against the M8 header)

Step 1: empty (verbatim copy). Steps 2-3 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m9/m9_replay_context.step2.h` and
the committed `local/research/M9/m9_replay_context.h` (= step 3; step 4 adds
no header change).



### Step 2

```diff
--- local/research/M8/m8_replay_context.h	2026-09-19 07:50:38
+++ /Volumes/Extreme SSD/m9/m9_replay_context.step2.h	2026-09-19 10:37:07
@@ -62,6 +62,8 @@
 #include "VideoCommon/DataReader.h"
 #include "VideoCommon/OpcodeDecoding.h"
 #include "VideoCommon/VertexLoaderManager.h"
+#include "VideoCommon/VertexLoaderBase.h"  // M9 step 2: GetVertexComponents for per-draw VAT decode
+#include "VideoCommon/NativeVertexFormat.h"  // M9 step 2: VB_HAS_POSMTXIDX / VB_HAS_TEXMTXIDXi
 #include "VideoCommon/XFMemory.h"
 #include "VideoCommon/BPMemory.h"
 #include "VideoCommon/CPMemory.h"
@@ -673,6 +675,160 @@
   return stats;
 }
 
+// --- M9 step 2: per-draw VAT + texgen-enablement walk --------------------------
+// Closes M8 gaps 1-3 (per-draw VAT path, shared-vs-indexed split, per-draw
+// texgen enablement). Read-only decode of the verbatim recorded stream (own
+// CPState seeded from recorded registers; own numtex/texinfo state seeded from
+// recorded XF regs). Per draw records, via the vendor's own
+// VertexLoaderBase::GetVertexComponents (VCD + VAT[vat]): VB_HAS_POSMTXIDX and
+// VB_HAS_TEXMTXIDXi path bits; numtex = live XF 0x103f low nibble after
+// in-stream writes (XFStructs.cpp:141-144: numTexGens = value & 15); texgen
+// types from XF 0x1040-0x1047 (TexMtxInfo.texgentype = bits 4-6); matrix-index
+// state via the same CP/XF write-through as M8CensusWalk. Shared reach counts
+// only draws that can actually consume the shared slot: position draws with
+// the shared path (no enablement gate), texgen draws with shared path AND
+// i < numtex. Indexed-path draws are counted per expression as totals only:
+// their per-vertex indices are not decoded (residue), so attributing them to
+// index-state slots would repeat M8's over-count.
+struct M9Census {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 vcd_lo = 0;   // CP 0x50 writes in the stream
+  u32 vcd_hi = 0;   // CP 0x60 writes in the stream
+  u32 vat_w = 0;    // CP 0x70-0x97 writes in the stream
+  u32 matidx_cp = 0;
+  u32 matidx_xf = 0;
+  u32 numtex0 = 0;  // recorded frame-start value of XF 0x103f
+  u32 numtex_w = 0;
+  u32 texinfo_w = 0;  // in-stream writes to XF 0x1040-0x1047
+  u32 benign = 0;
+  u32 unknown = 0;
+  u64 vat_hist[8] = {};      // draws per vat index
+  u64 numtex_hist[16] = {};  // draws per live numtex value
+  u64 pos_shared = 0, pos_indexed = 0;
+  u64 tex_shared[8] = {}, tex_indexed[8] = {};
+  u64 tex_enabled[8] = {};         // draws with i < live numtex
+  u64 tex_shared_enabled[8] = {};  // draws with shared path AND enabled
+  u64 tex_type[8][4] = {};         // draws per texgen per TexGenType (at draw, enabled or not)
+  u64 reach_pos[64] = {};          // draws with PosNormalMtxIdx==s AND pos shared
+  u64 reach_tex[8][64] = {};       // draws with TexiMtxIdx==s AND tex-i shared AND enabled
+  static constexpr u32 kMaxEpochs = 80;
+  u32 epoch_draw[80] = {};  // draw index (1-based) where the epoch starts
+  u32 epoch_numtex[80] = {};
+  u32 epochs = 0;
+};
+class M9CensusWalk final : public OpcodeDecoder::Callback {
+public:
+  M9CensusWalk(const u32* cp_mem, const u32* xf_regs, M9Census& stats)
+      : m_cp(cp_mem), m_stats(stats) {
+    m_numtex = xf_regs[0x3f] & 0xf;
+    for (u32 i = 0; i < 8; ++i) m_texhex[i] = xf_regs[0x40 + i];
+  }
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address;
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      if (word == XFMEM_SETNUMTEXGENS) {
+        ++m_stats.numtex_w;
+        m_numtex = v & 0xf;
+      } else if (word >= XFMEM_SETTEXMTXINFO && word < XFMEM_SETTEXMTXINFO + 8) {
+        ++m_stats.texinfo_w;
+        m_texhex[word - XFMEM_SETTEXMTXINFO] = v;
+      }
+      if (word == XFMEM_SETMATRIXINDA) {
+        m_cp.matrix_index_a.Hex = v;
+        ++m_stats.matidx_xf;
+      } else if (word == XFMEM_SETMATRIXINDB) {
+        m_cp.matrix_index_b.Hex = v;
+        ++m_stats.matidx_xf;
+      }
+    }
+  }
+  void OnCP(u8 command, u32 value) override {
+    m_cp.LoadCPReg(command, value);
+    if ((command & CP_COMMAND_MASK) == VCD_LO && command == VCD_LO) ++m_stats.vcd_lo;
+    if ((command & CP_COMMAND_MASK) == VCD_HI && command == VCD_HI) ++m_stats.vcd_hi;
+    const u32 grp = command & CP_COMMAND_MASK;
+    if (grp == CP_VAT_REG_A || grp == CP_VAT_REG_B || grp == CP_VAT_REG_C) ++m_stats.vat_w;
+    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
+  }
+  void OnBP(u8, u32) override {}
+  void OnIndexedLoad(CPArray, u32, u16, u8) override {}
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 v = vat & 7;
+    ++m_stats.vat_hist[v];
+    ++m_stats.numtex_hist[m_numtex & 15];
+    if (m_stats.draws == 1 || (m_numtex & 15) != m_last_numtex) {
+      if (m_stats.epochs < M9Census::kMaxEpochs) {
+        m_stats.epoch_draw[m_stats.epochs] = m_stats.draws;
+        m_stats.epoch_numtex[m_stats.epochs] = m_numtex & 15;
+      }
+      ++m_stats.epochs;
+      m_last_numtex = m_numtex & 15;
+    }
+    const u32 comp =
+        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
+    const bool pos_idx = (comp & VB_HAS_POSMTXIDX) != 0;
+    if (pos_idx)
+      ++m_stats.pos_indexed;
+    else
+      ++m_stats.pos_shared;
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    if (!pos_idx) ++m_stats.reach_pos[idx[0]];
+    for (u32 i = 0; i < 8; ++i) {
+      const bool t_idx = (comp & (VB_HAS_TEXMTXIDX0 << i)) != 0;
+      if (t_idx)
+        ++m_stats.tex_indexed[i];
+      else
+        ++m_stats.tex_shared[i];
+      const bool enabled = i < (m_numtex & 15);
+      if (enabled) ++m_stats.tex_enabled[i];
+      if (!t_idx && enabled) {
+        ++m_stats.tex_shared_enabled[i];
+        ++m_stats.reach_tex[i][idx[1 + i]];
+      }
+      const u32 ty = (m_texhex[i] >> 4) & 7;
+      if (ty < 4) ++m_stats.tex_type[i][ty];
+    }
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8 opcode, const u8*) override {
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
+  M9Census& m_stats;
+  u32 m_numtex = 0;
+  u32 m_last_numtex = 0;
+  u32 m_texhex[8] = {};
+};
+static M9Census RunM9Census(const std::vector<u8>& src, const u32* cp_mem,
+                            const u32* xf_regs) {
+  M9Census stats;
+  stats.numtex0 = xf_regs[0x3f];
+  if (src.empty()) return stats;
+  M9CensusWalk walk(cp_mem, xf_regs, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
+  return stats;
+}
+
 // Snapshot of the live video registers, restored after the sequence so the
 // game's own command stream keeps decoding with the state it expects.
 struct LiveState {
@@ -1038,12 +1194,37 @@
                         const char* v = std::getenv("SSX_M8_CENSUS");
                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                       })());
+  // M9 steps 2-4: mode select (parsed early: the stream walks run at setup).
+  // 0 = unset = M8/M7 behavior; 1 = census (SSX_M9_CENSUS=1: VAT+texgen walk,
+  // counts only); 2 = slot delta (SSX_M9_SLOT=N, 0-63: M8 mode-2 delta +
+  // VAT+texgen walk). Precedence: SLOT > CENSUS; M9 overrides M8 when set.
+  // Counting stays on in every M9 mode, so each delta run carries its own
+  // M8 census and its own M9 VAT census.
+  const int m9_slot = [] {
+    const char* v = std::getenv("SSX_M9_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m9_mode = m9_slot >= 0 ? 2 : ([] {
+                        const char* v = std::getenv("SSX_M9_CENSUS");
+                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                      })();
   // M8 step 2: stream-epoch census over the verbatim recorded stream. The XFB
   // scratch patch touches BP dest addresses only, so verbatim and executed
-  // streams agree on draws and index state.
-  const M8Census m8stream = m8_mode != 0 ? RunM8Census(frame, file->GetCPMem(),
+  // streams agree on draws and index state. M9 modes carry their own M8 census.
+  const M8Census m8stream = (m8_mode != 0 || m9_mode != 0)
+                                ? RunM8Census(frame, file->GetCPMem(), file->GetXFRegs())
+                                : M8Census{};
+  // M9 step 2: per-draw VAT + texgen-enablement census (same stream).
+  const M9Census m9stream = m9_mode != 0 ? RunM9Census(frame, file->GetCPMem(),
                                                        file->GetXFRegs())
-                                         : M8Census{};
+                                         : M9Census{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -1163,14 +1344,16 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
+                  "m9mode=%d m9slot=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
+                  m9_mode, m9_slot);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1246,7 +1429,18 @@
   }
   // M8 steps 2-3: census/slot/proj transform (counting always on; delta
   // arms per mode). Overrides the M7 select above when set; unset = M7 behavior.
-  if (m8_mode != 0) {
+  // M9 overrides M8 when set (M9 modes reuse M8Transform + counters: same
+  // seam tallies, same slot-delta shape, plus the M9 VAT census at setup).
+  if (m9_mode != 0) {
+    s_m8_calls = 0;
+    s_m8_hits = 0;
+    s_m8_regcalls = 0;
+    for (auto& w : s_m8_writes) w = 0;
+    for (auto& r : s_m8_reads) r = 0;
+    s_m8_slot = m9_mode == 2 ? m9_slot : -1;
+    s_m8_proj = 0;
+    XFReplay::g_transform = &M8Transform;
+  } else if (m8_mode != 0) {
     s_m8_calls = 0;
     s_m8_hits = 0;
     s_m8_regcalls = 0;
@@ -1275,7 +1469,7 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0)
+    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     ApplyMemory(system, file);
     const double t_mem = Now();
@@ -1404,7 +1598,8 @@
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
     // M7 step 2: tag actual install state (default mode identical to M6).
-    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0);
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0 ||
+                               m9_mode != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1497,12 +1692,15 @@
   // m8_meta carries the stream-epoch census; m8_writes/m8_reads/m8_draws carry
   // the 64-slot CSVs (slot order 0..63); m8_expr0-8 carry the per-expression
   // draw histograms (0=PosNormal, 1-8=Tex0-7).
-  if (m8_mode != 0) {
+  if (m8_mode != 0 && m9_mode == 0) {
     char xs[160];
     std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
                   m8_mode == 1 ? 7 : (m8_mode == 2 ? 8 : 9), s_m8_slot, s_m8_calls,
                   s_m8_hits, s_m8_regcalls);
     Event("xform_stats", xs);
+  }
+  // M9: the M8 stream census rides on M9 runs too (mode = the active mode).
+  if (m8_mode != 0 || m9_mode != 0) {
     char meta[448];
     std::snprintf(
         meta, sizeof(meta),
@@ -1510,7 +1708,8 @@
         "direct_xfmem=%u direct_pos_words=%u stream_indexed=%u idx_pos=%u idx_reg=%u "
         "projreg_writes=%u numtex0=0x%x numtex_w=%u idxa0=0x%08x idxb0=0x%08x "
         "walk=%u/%zu benign=%u walk_ok=%d",
-        m8_mode, m8stream.draws, (unsigned long long)m8stream.verts, m8stream.epochs,
+        m8_mode != 0 ? m8_mode : m9_mode, m8stream.draws,
+        (unsigned long long)m8stream.verts, m8stream.epochs,
         m8stream.matidx_cp, m8stream.matidx_xf, m8stream.direct_xfmem,
         m8stream.direct_pos_words, m8stream.indexed, m8stream.idx_pos, m8stream.idx_reg,
         m8stream.projreg_writes, m8stream.numtex0, m8stream.numtex_w, m8stream.idxa0,
@@ -1551,6 +1750,124 @@
       Event(ename, csv);
     }
   }
+  // M9 step 2: VAT + texgen-enablement receipts (every M9 mode: each delta run
+  // carries its own M8 census above plus its own M9 VAT census here).
+  // xform_stats mode 10/11 = census/slot (same seam counters as M8's 7/8).
+  // m9_meta carries the walk summary; m9_path the shared-vs-indexed path table
+  // (position + per-texgen); m9_texen the numtex histogram + per-texgen
+  // enabled counts; m9_texep the enablement-epoch timeline
+  // (draw:numtex,...); m9_vat the vat-index histogram; m9_textype the
+  // per-texgen TexGenType histogram (texgen-major, 4 types); m9_reachp the
+  // shared-position reach per slot; m9_reach0-7 the shared+enabled texgen
+  // reach per slot.
+  if (m9_mode != 0) {
+    char xs[160];
+    std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
+                  m9_mode == 1 ? 10 : 11, s_m8_slot, s_m8_calls, s_m8_hits,
+                  s_m8_regcalls);
+    Event("xform_stats", xs);
+    char meta[448];
+    std::snprintf(
+        meta, sizeof(meta),
+        "mode=%d draws=%u verts=%llu vcd_lo=%u vcd_hi=%u vat_w=%u matidx_cp=%u matidx_xf=%u "
+        "numtex0=0x%x numtex_w=%u texinfo_w=%u epochs=%u "
+        "walk=%u/%zu benign=%u walk_ok=%d",
+        m9_mode, m9stream.draws, (unsigned long long)m9stream.verts, m9stream.vcd_lo,
+        m9stream.vcd_hi, m9stream.vat_w, m9stream.matidx_cp, m9stream.matidx_xf,
+        m9stream.numtex0, m9stream.numtex_w, m9stream.texinfo_w, m9stream.epochs,
+        m9stream.consumed, frame.size(), m9stream.benign,
+        int(m9stream.consumed == frame.size() && m9stream.unknown == 0));
+    Event("m9_meta", meta);
+    char path[1024];
+    std::snprintf(
+        path, sizeof(path),
+        "pos_shared=%llu pos_indexed=%llu "
+        "tex_shared=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_indexed=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_shared_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu",
+        (unsigned long long)m9stream.pos_shared, (unsigned long long)m9stream.pos_indexed,
+        (unsigned long long)m9stream.tex_shared[0], (unsigned long long)m9stream.tex_shared[1],
+        (unsigned long long)m9stream.tex_shared[2], (unsigned long long)m9stream.tex_shared[3],
+        (unsigned long long)m9stream.tex_shared[4], (unsigned long long)m9stream.tex_shared[5],
+        (unsigned long long)m9stream.tex_shared[6], (unsigned long long)m9stream.tex_shared[7],
+        (unsigned long long)m9stream.tex_indexed[0], (unsigned long long)m9stream.tex_indexed[1],
+        (unsigned long long)m9stream.tex_indexed[2], (unsigned long long)m9stream.tex_indexed[3],
+        (unsigned long long)m9stream.tex_indexed[4], (unsigned long long)m9stream.tex_indexed[5],
+        (unsigned long long)m9stream.tex_indexed[6], (unsigned long long)m9stream.tex_indexed[7],
+        (unsigned long long)m9stream.tex_enabled[0], (unsigned long long)m9stream.tex_enabled[1],
+        (unsigned long long)m9stream.tex_enabled[2], (unsigned long long)m9stream.tex_enabled[3],
+        (unsigned long long)m9stream.tex_enabled[4], (unsigned long long)m9stream.tex_enabled[5],
+        (unsigned long long)m9stream.tex_enabled[6], (unsigned long long)m9stream.tex_enabled[7],
+        (unsigned long long)m9stream.tex_shared_enabled[0],
+        (unsigned long long)m9stream.tex_shared_enabled[1],
+        (unsigned long long)m9stream.tex_shared_enabled[2],
+        (unsigned long long)m9stream.tex_shared_enabled[3],
+        (unsigned long long)m9stream.tex_shared_enabled[4],
+        (unsigned long long)m9stream.tex_shared_enabled[5],
+        (unsigned long long)m9stream.tex_shared_enabled[6],
+        (unsigned long long)m9stream.tex_shared_enabled[7]);
+    Event("m9_path", path);
+    char txe[768];
+    int toff = std::snprintf(txe, sizeof(txe), "numtex_hist=");
+    for (u32 n = 0; n < 16; ++n) {
+      if (toff < 0 || size_t(toff) >= sizeof(txe) - 24) break;
+      toff += std::snprintf(txe + toff, sizeof(txe) - size_t(toff), "%s%llu", n ? "," : "",
+                            (unsigned long long)m9stream.numtex_hist[n]);
+    }
+    Event("m9_texen", txe);
+    char tep[1024];
+    int eoff = 0;
+    const u32 nepoch = m9stream.epochs < M9Census::kMaxEpochs ? m9stream.epochs
+                                                             : M9Census::kMaxEpochs;
+    for (u32 e = 0; e < nepoch; ++e) {
+      if (eoff < 0 || size_t(eoff) >= sizeof(tep) - 24) break;
+      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), "%s%u:%u", e ? "," : "",
+                            m9stream.epoch_draw[e], m9stream.epoch_numtex[e]);
+    }
+    if (m9stream.epochs > M9Census::kMaxEpochs) {
+      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), ",TRUNC=%u",
+                            m9stream.epochs);
+    }
+    Event("m9_texep", tep);
+    char vat[256];
+    int voff = 0;
+    for (u32 i = 0; i < 8; ++i) {
+      if (voff < 0 || size_t(voff) >= sizeof(vat) - 24) break;
+      voff += std::snprintf(vat + voff, sizeof(vat) - size_t(voff), "%s%llu", i ? "," : "",
+                            (unsigned long long)m9stream.vat_hist[i]);
+    }
+    Event("m9_vat", vat);
+    char tty[512];
+    int yoff = 0;
+    for (u32 t = 0; t < 8; ++t)
+      for (u32 ty = 0; ty < 4; ++ty) {
+        if (yoff < 0 || size_t(yoff) >= sizeof(tty) - 24) break;
+        yoff += std::snprintf(tty + yoff, sizeof(tty) - size_t(yoff), "%s%llu",
+                              (t || ty) ? "," : "",
+                              (unsigned long long)m9stream.tex_type[t][ty]);
+      }
+    Event("m9_textype", tty);
+    char rcsv[2048];
+    int roff = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
+      roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
+                            (unsigned long long)m9stream.reach_pos[s]);
+    }
+    Event("m9_reachp", rcsv);
+    for (u32 t = 0; t < 8; ++t) {
+      roff = 0;
+      for (u32 s = 0; s < 64; ++s) {
+        if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
+        roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
+                              (unsigned long long)m9stream.reach_tex[t][s]);
+      }
+      char rname[16];
+      std::snprintf(rname, sizeof(rname), "m9_reach%u", t);
+      Event(rname, rcsv);
+    }
+  }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```

### Step 3 (= committed header; step 4 adds no header change)

```diff
--- local/research/M8/m8_replay_context.h	2026-09-19 07:50:38
+++ local/research/M9/m9_replay_context.h	2026-09-19 10:40:01
@@ -62,6 +62,10 @@
 #include "VideoCommon/DataReader.h"
 #include "VideoCommon/OpcodeDecoding.h"
 #include "VideoCommon/VertexLoaderManager.h"
+#include "VideoCommon/VertexLoaderBase.h"  // M9 step 2: GetVertexComponents for per-draw VAT decode
+#include "VideoCommon/NativeVertexFormat.h"  // M9 step 2: VB_HAS_POSMTXIDX / VB_HAS_TEXMTXIDXi
+#include "VideoCommon/VertexShaderManager.h"  // M9 step 3: constants snapshot reads
+#include "VideoCommon/XFStateManager.h"  // M9 step 3: dirty-flag reads
 #include "VideoCommon/XFMemory.h"
 #include "VideoCommon/BPMemory.h"
 #include "VideoCommon/CPMemory.h"
@@ -673,6 +677,160 @@
   return stats;
 }
 
+// --- M9 step 2: per-draw VAT + texgen-enablement walk --------------------------
+// Closes M8 gaps 1-3 (per-draw VAT path, shared-vs-indexed split, per-draw
+// texgen enablement). Read-only decode of the verbatim recorded stream (own
+// CPState seeded from recorded registers; own numtex/texinfo state seeded from
+// recorded XF regs). Per draw records, via the vendor's own
+// VertexLoaderBase::GetVertexComponents (VCD + VAT[vat]): VB_HAS_POSMTXIDX and
+// VB_HAS_TEXMTXIDXi path bits; numtex = live XF 0x103f low nibble after
+// in-stream writes (XFStructs.cpp:141-144: numTexGens = value & 15); texgen
+// types from XF 0x1040-0x1047 (TexMtxInfo.texgentype = bits 4-6); matrix-index
+// state via the same CP/XF write-through as M8CensusWalk. Shared reach counts
+// only draws that can actually consume the shared slot: position draws with
+// the shared path (no enablement gate), texgen draws with shared path AND
+// i < numtex. Indexed-path draws are counted per expression as totals only:
+// their per-vertex indices are not decoded (residue), so attributing them to
+// index-state slots would repeat M8's over-count.
+struct M9Census {
+  u32 consumed = 0;
+  u32 draws = 0;
+  u64 verts = 0;
+  u32 vcd_lo = 0;   // CP 0x50 writes in the stream
+  u32 vcd_hi = 0;   // CP 0x60 writes in the stream
+  u32 vat_w = 0;    // CP 0x70-0x97 writes in the stream
+  u32 matidx_cp = 0;
+  u32 matidx_xf = 0;
+  u32 numtex0 = 0;  // recorded frame-start value of XF 0x103f
+  u32 numtex_w = 0;
+  u32 texinfo_w = 0;  // in-stream writes to XF 0x1040-0x1047
+  u32 benign = 0;
+  u32 unknown = 0;
+  u64 vat_hist[8] = {};      // draws per vat index
+  u64 numtex_hist[16] = {};  // draws per live numtex value
+  u64 pos_shared = 0, pos_indexed = 0;
+  u64 tex_shared[8] = {}, tex_indexed[8] = {};
+  u64 tex_enabled[8] = {};         // draws with i < live numtex
+  u64 tex_shared_enabled[8] = {};  // draws with shared path AND enabled
+  u64 tex_type[8][4] = {};         // draws per texgen per TexGenType (at draw, enabled or not)
+  u64 reach_pos[64] = {};          // draws with PosNormalMtxIdx==s AND pos shared
+  u64 reach_tex[8][64] = {};       // draws with TexiMtxIdx==s AND tex-i shared AND enabled
+  static constexpr u32 kMaxEpochs = 80;
+  u32 epoch_draw[80] = {};  // draw index (1-based) where the epoch starts
+  u32 epoch_numtex[80] = {};
+  u32 epochs = 0;
+};
+class M9CensusWalk final : public OpcodeDecoder::Callback {
+public:
+  M9CensusWalk(const u32* cp_mem, const u32* xf_regs, M9Census& stats)
+      : m_cp(cp_mem), m_stats(stats) {
+    m_numtex = xf_regs[0x3f] & 0xf;
+    for (u32 i = 0; i < 8; ++i) m_texhex[i] = xf_regs[0x40 + i];
+  }
+  void OnXF(u16 address, u8 count, const u8* data) override {
+    const u32 lo = address;
+    for (u32 i = 0; i < u32(count); ++i) {
+      const u32 word = lo + i;
+      const u32 v = (u32(data[4 * i]) << 24) | (u32(data[4 * i + 1]) << 16) |
+                    (u32(data[4 * i + 2]) << 8) | u32(data[4 * i + 3]);
+      if (word == XFMEM_SETNUMTEXGENS) {
+        ++m_stats.numtex_w;
+        m_numtex = v & 0xf;
+      } else if (word >= XFMEM_SETTEXMTXINFO && word < XFMEM_SETTEXMTXINFO + 8) {
+        ++m_stats.texinfo_w;
+        m_texhex[word - XFMEM_SETTEXMTXINFO] = v;
+      }
+      if (word == XFMEM_SETMATRIXINDA) {
+        m_cp.matrix_index_a.Hex = v;
+        ++m_stats.matidx_xf;
+      } else if (word == XFMEM_SETMATRIXINDB) {
+        m_cp.matrix_index_b.Hex = v;
+        ++m_stats.matidx_xf;
+      }
+    }
+  }
+  void OnCP(u8 command, u32 value) override {
+    m_cp.LoadCPReg(command, value);
+    if ((command & CP_COMMAND_MASK) == VCD_LO && command == VCD_LO) ++m_stats.vcd_lo;
+    if ((command & CP_COMMAND_MASK) == VCD_HI && command == VCD_HI) ++m_stats.vcd_hi;
+    const u32 grp = command & CP_COMMAND_MASK;
+    if (grp == CP_VAT_REG_A || grp == CP_VAT_REG_B || grp == CP_VAT_REG_C) ++m_stats.vat_w;
+    if (command == MATINDEX_A || command == MATINDEX_B) ++m_stats.matidx_cp;
+  }
+  void OnBP(u8, u32) override {}
+  void OnIndexedLoad(CPArray, u32, u16, u8) override {}
+  void OnPrimitiveCommand(OpcodeDecoder::Primitive, u8 vat, u32, u16 num_vertices,
+                          const u8*) override {
+    ++m_stats.draws;
+    m_stats.verts += num_vertices;
+    const u32 v = vat & 7;
+    ++m_stats.vat_hist[v];
+    ++m_stats.numtex_hist[m_numtex & 15];
+    if (m_stats.draws == 1 || (m_numtex & 15) != m_last_numtex) {
+      if (m_stats.epochs < M9Census::kMaxEpochs) {
+        m_stats.epoch_draw[m_stats.epochs] = m_stats.draws;
+        m_stats.epoch_numtex[m_stats.epochs] = m_numtex & 15;
+      }
+      ++m_stats.epochs;
+      m_last_numtex = m_numtex & 15;
+    }
+    const u32 comp =
+        VertexLoaderBase::GetVertexComponents(m_cp.vtx_desc, m_cp.vtx_attr[v]);
+    const bool pos_idx = (comp & VB_HAS_POSMTXIDX) != 0;
+    if (pos_idx)
+      ++m_stats.pos_indexed;
+    else
+      ++m_stats.pos_shared;
+    const u32 ia = m_cp.matrix_index_a.Hex;
+    const u32 ib = m_cp.matrix_index_b.Hex;
+    const u32 idx[9] = {ia & 63, (ia >> 6) & 63, (ia >> 12) & 63, (ia >> 18) & 63,
+                        (ia >> 24) & 63, ib & 63, (ib >> 6) & 63, (ib >> 12) & 63,
+                        (ib >> 18) & 63};
+    if (!pos_idx) ++m_stats.reach_pos[idx[0]];
+    for (u32 i = 0; i < 8; ++i) {
+      const bool t_idx = (comp & (VB_HAS_TEXMTXIDX0 << i)) != 0;
+      if (t_idx)
+        ++m_stats.tex_indexed[i];
+      else
+        ++m_stats.tex_shared[i];
+      const bool enabled = i < (m_numtex & 15);
+      if (enabled) ++m_stats.tex_enabled[i];
+      if (!t_idx && enabled) {
+        ++m_stats.tex_shared_enabled[i];
+        ++m_stats.reach_tex[i][idx[1 + i]];
+      }
+      const u32 ty = (m_texhex[i] >> 4) & 7;
+      if (ty < 4) ++m_stats.tex_type[i][ty];
+    }
+  }
+  void OnDisplayList(u32, u32) override {}
+  void OnNop(u32) override {}
+  void OnUnknown(u8 opcode, const u8*) override {
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
+  M9Census& m_stats;
+  u32 m_numtex = 0;
+  u32 m_last_numtex = 0;
+  u32 m_texhex[8] = {};
+};
+static M9Census RunM9Census(const std::vector<u8>& src, const u32* cp_mem,
+                            const u32* xf_regs) {
+  M9Census stats;
+  stats.numtex0 = xf_regs[0x3f];
+  if (src.empty()) return stats;
+  M9CensusWalk walk(cp_mem, xf_regs, stats);
+  stats.consumed = OpcodeDecoder::Run(src.data(), u32(src.size()), walk);
+  return stats;
+}
+
 // Snapshot of the live video registers, restored after the sequence so the
 // game's own command stream keeps decoding with the state it expects.
 struct LiveState {
@@ -816,6 +974,21 @@
 static unsigned long long s_m8_reads[64] = {};
 static int s_m8_slot = -1;  // mode-2 target slot, else -1
 static int s_m8_proj = 0;   // mode-3 flag
+// --- M9 step 3: upload-timing survival sampling -------------------------------
+// At each seam hit (a write covering the delta word), records the live xfmem
+// word before/after the +0.1 (first-hit hexes + mismatch tallies prove the
+// perturbed value existed uniformly, no accumulation) and samples the
+// XFStateManager dirty flags set by THIS write (LoadIndexedXF order:
+// XFMemWritten -> Flush consumes old flags + InvalidateXFRange sets new ones,
+// then the data write, then this seam: XFStructs.cpp:294-301). Post-replay
+// sampling in the loop below compares live xfmem against the
+// SetConstants-uploaded snapshots. All gated on s_m9_surv (unset = M8 shape).
+static int s_m9_surv = 0;
+static int s_m9_first_hit = 0;
+static u32 s_m9_vbefore = 0, s_m9_vafter = 0;
+static unsigned long long s_m9_vb_mm = 0, s_m9_va_mm = 0;
+static unsigned long long s_m9_hit_dirty_pos = 0, s_m9_hit_dirty_texa = 0;
+static unsigned long long s_m9_hit_dirty_texb = 0, s_m9_hit_dirty_pervtx = 0;
 static void M8Transform(u16 address, u32 count) {
   ++s_m8_calls;
   const u32 lo = address, hi = address + count;  // covered words [lo, hi)
@@ -837,8 +1010,28 @@
   if (s_m8_slot >= 0) {
     const u32 w = u32(s_m8_slot) * 4 + 3;
     if (lo <= w && w < hi) {
-      xfmem.posMatrices[w] += 0.1f;
+      float* f = &xfmem.posMatrices[w];
+      u32 vb = 0;
+      std::memcpy(&vb, f, 4);  // read-only when s_m9_surv == 0
+      *f += 0.1f;
       ++s_m8_hits;
+      if (s_m9_surv) {
+        u32 va = 0;
+        std::memcpy(&va, f, 4);
+        if (!s_m9_first_hit) {
+          s_m9_vbefore = vb;
+          s_m9_vafter = va;
+          s_m9_first_hit = 1;
+        } else {
+          if (vb != s_m9_vbefore) ++s_m9_vb_mm;
+          if (va != s_m9_vafter) ++s_m9_va_mm;
+        }
+        const auto& xfm = Core::System::GetInstance().GetXFStateManager();
+        if (xfm.DidPosNormalChange()) ++s_m9_hit_dirty_pos;
+        if (xfm.DidTexMatrixAChange()) ++s_m9_hit_dirty_texa;
+        if (xfm.DidTexMatrixBChange()) ++s_m9_hit_dirty_texb;
+        if (xfm.GetPerVertexTransformMatrixChanges()[0] >= 0) ++s_m9_hit_dirty_pervtx;
+      }
     }
   }
   if (s_m8_proj) {
@@ -1038,12 +1231,44 @@
                         const char* v = std::getenv("SSX_M8_CENSUS");
                         return v && std::strcmp(v, "1") == 0 ? 1 : 0;
                       })());
+  // M9 steps 2-4: mode select (parsed early: the stream walks run at setup).
+  // 0 = unset = M8/M7 behavior; 1 = census (SSX_M9_CENSUS=1: VAT+texgen walk,
+  // counts only); 2 = slot delta (SSX_M9_SLOT=N, 0-63: M8 mode-2 delta +
+  // VAT+texgen walk). Precedence: SLOT > CENSUS; M9 overrides M8 when set.
+  // Counting stays on in every M9 mode, so each delta run carries its own
+  // M8 census and its own M9 VAT census.
+  const int m9_slot = [] {
+    const char* v = std::getenv("SSX_M9_SLOT");
+    if (!v || !*v) return -1;
+    int n = 0;
+    for (const char* p = v; *p; ++p) {
+      if (*p < '0' || *p > '9') return -1;
+      n = n * 10 + (*p - '0');
+      if (n > 63) return -1;
+    }
+    return n;
+  }();
+  const int m9_mode = m9_slot >= 0 ? 2 : ([] {
+                        const char* v = std::getenv("SSX_M9_CENSUS");
+                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                      })();
+  // M9 step 3: survival sampling (SSX_M9_SURV=1). Arms only with a slot delta
+  // (M9 mode 2); elsewhere parsed but inert.
+  const int m9_surv = m9_mode == 2 ? ([] {
+                        const char* v = std::getenv("SSX_M9_SURV");
+                        return v && std::strcmp(v, "1") == 0 ? 1 : 0;
+                      })()
+                                   : 0;
   // M8 step 2: stream-epoch census over the verbatim recorded stream. The XFB
   // scratch patch touches BP dest addresses only, so verbatim and executed
-  // streams agree on draws and index state.
-  const M8Census m8stream = m8_mode != 0 ? RunM8Census(frame, file->GetCPMem(),
+  // streams agree on draws and index state. M9 modes carry their own M8 census.
+  const M8Census m8stream = (m8_mode != 0 || m9_mode != 0)
+                                ? RunM8Census(frame, file->GetCPMem(), file->GetXFRegs())
+                                : M8Census{};
+  // M9 step 2: per-draw VAT + texgen-enablement census (same stream).
+  const M9Census m9stream = m9_mode != 0 ? RunM9Census(frame, file->GetCPMem(),
                                                        file->GetXFRegs())
-                                         : M8Census{};
+                                         : M9Census{};
 
   // M5 step 2: reference hash of the live XFB after the original frame, taken
   // before the first restore. After every replay the same range is hashed
@@ -1163,14 +1388,16 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d m8mode=%d m8slot=%d "
+                  "m9mode=%d m9slot=%d m9surv=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform, m8_mode, m8_slot,
+                  m9_mode, m9_slot, m9_surv);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -1246,12 +1473,36 @@
   }
   // M8 steps 2-3: census/slot/proj transform (counting always on; delta
   // arms per mode). Overrides the M7 select above when set; unset = M7 behavior.
-  if (m8_mode != 0) {
+  // M9 overrides M8 when set (M9 modes reuse M8Transform + counters: same
+  // seam tallies, same slot-delta shape, plus the M9 VAT census at setup).
+  // M9 step 3: post-replay survival tallies (live xfmem vs snapshots).
+  unsigned m9_xf_after = 0, m9_xf_before = 0, m9_xf_other = 0;
+  unsigned m9_pv_after = 0, m9_pv_before = 0, m9_pv_other = 0;
+  unsigned m9_pos_res = 0, m9_pos_after = 0, m9_pos_before = 0, m9_pos_other = 0;
+  unsigned m9_tex_res = 0, m9_tex_after = 0, m9_tex_before = 0, m9_tex_other = 0;
+  unsigned m9_dirty_post = 0;
+  s_m9_surv = 0;
+  if (m9_mode != 0) {
     s_m8_calls = 0;
     s_m8_hits = 0;
     s_m8_regcalls = 0;
     for (auto& w : s_m8_writes) w = 0;
     for (auto& r : s_m8_reads) r = 0;
+    s_m8_slot = m9_mode == 2 ? m9_slot : -1;
+    s_m8_proj = 0;
+    s_m9_surv = m9_surv;
+    s_m9_first_hit = 0;
+    s_m9_vbefore = s_m9_vafter = 0;
+    s_m9_vb_mm = s_m9_va_mm = 0;
+    s_m9_hit_dirty_pos = s_m9_hit_dirty_texa = 0;
+    s_m9_hit_dirty_texb = s_m9_hit_dirty_pervtx = 0;
+    XFReplay::g_transform = &M8Transform;
+  } else if (m8_mode != 0) {
+    s_m8_calls = 0;
+    s_m8_hits = 0;
+    s_m8_regcalls = 0;
+    for (auto& w : s_m8_writes) w = 0;
+    for (auto& r : s_m8_reads) r = 0;
     s_m8_slot = m8_mode == 2 ? m8_slot : -1;
     s_m8_proj = m8_mode == 3 ? 1 : 0;
     XFReplay::g_transform = &M8Transform;
@@ -1275,7 +1526,7 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0)
+    if (replays == kTransformFrom && m7_xform == 0 && m8_mode == 0 && m9_mode == 0)
       XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     ApplyMemory(system, file);
     const double t_mem = Now();
@@ -1291,6 +1542,68 @@
       g_gfx->WaitForGPUIdle();
     }
     const double t_run = Now();
+    // M9 step 3: post-replay survival sample (after all Flushes, before the
+    // next restore). Compares live xfmem against the SetConstants-uploaded
+    // snapshots the shader consumes: transformmatrices[slot] (indexed path),
+    // posnormalmatrix[0] when the post-frame PosNormalMtxIdx == slot (shared
+    // position), texmatrices[3i] for the lowest-index resident texgen
+    // (shared texgen). Values trichotomized against the first-hit
+    // before/after hexes (exact u32 compare, no float neighborhood).
+    if (m9_surv && s_m9_first_hit) {
+      const u32 mw = u32(m9_slot) * 4 + 3;
+      u32 xfv = 0;
+      std::memcpy(&xfv, &xfmem.posMatrices[mw], 4);
+      if (xfv == s_m9_vafter)
+        ++m9_xf_after;
+      else if (xfv == s_m9_vbefore)
+        ++m9_xf_before;
+      else
+        ++m9_xf_other;
+      const auto& vconst = system.GetVertexShaderManager().constants;
+      u32 pvv = 0;
+      std::memcpy(&pvv, &vconst.transformmatrices[u32(m9_slot)][3], 4);
+      if (pvv == s_m9_vafter)
+        ++m9_pv_after;
+      else if (pvv == s_m9_vbefore)
+        ++m9_pv_before;
+      else
+        ++m9_pv_other;
+      const u32 pia = g_main_cp_state.matrix_index_a.Hex;
+      const u32 pib = g_main_cp_state.matrix_index_b.Hex;
+      if ((pia & 63) == u32(m9_slot)) {
+        ++m9_pos_res;
+        u32 psv = 0;
+        std::memcpy(&psv, &vconst.posnormalmatrix[0][3], 4);
+        if (psv == s_m9_vafter)
+          ++m9_pos_after;
+        else if (psv == s_m9_vbefore)
+          ++m9_pos_before;
+        else
+          ++m9_pos_other;
+      }
+      const u32 tidx[8] = {(pia >> 6) & 63,  (pia >> 12) & 63, (pia >> 18) & 63,
+                           (pia >> 24) & 63, pib & 63,         (pib >> 6) & 63,
+                           (pib >> 12) & 63, (pib >> 18) & 63};
+      for (u32 ti = 0; ti < 8; ++ti) {
+        if (tidx[ti] == u32(m9_slot)) {
+          ++m9_tex_res;
+          u32 txv = 0;
+          std::memcpy(&txv, &vconst.texmatrices[3 * ti][3], 4);
+          if (txv == s_m9_vafter)
+            ++m9_tex_after;
+          else if (txv == s_m9_vbefore)
+            ++m9_tex_before;
+          else
+            ++m9_tex_other;
+          break;  // lowest-index resident texgen only
+        }
+      }
+      const auto& xfm = system.GetXFStateManager();
+      if (xfm.DidPosNormalChange() || xfm.DidTexMatrixAChange() ||
+          xfm.DidTexMatrixBChange() ||
+          xfm.GetPerVertexTransformMatrixChanges()[0] >= 0)
+        ++m9_dirty_post;
+    }
     // read_ptr == write_ptr after a matched pair, so this compacts zero bytes
     // and rewinds both aux pointers to the base of the 2 MiB buffer.
     if (deterministic) fifo.SyncGPU(Fifo::SyncGPUReason::AuxSpace, false);
@@ -1404,7 +1717,8 @@
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
     // M7 step 2: tag actual install state (default mode identical to M6).
-    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0);
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0 || m8_mode != 0 ||
+                               m9_mode != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1497,12 +1811,15 @@
   // m8_meta carries the stream-epoch census; m8_writes/m8_reads/m8_draws carry
   // the 64-slot CSVs (slot order 0..63); m8_expr0-8 carry the per-expression
   // draw histograms (0=PosNormal, 1-8=Tex0-7).
-  if (m8_mode != 0) {
+  if (m8_mode != 0 && m9_mode == 0) {
     char xs[160];
     std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
                   m8_mode == 1 ? 7 : (m8_mode == 2 ? 8 : 9), s_m8_slot, s_m8_calls,
                   s_m8_hits, s_m8_regcalls);
     Event("xform_stats", xs);
+  }
+  // M9: the M8 stream census rides on M9 runs too (mode = the active mode).
+  if (m8_mode != 0 || m9_mode != 0) {
     char meta[448];
     std::snprintf(
         meta, sizeof(meta),
@@ -1510,7 +1827,8 @@
         "direct_xfmem=%u direct_pos_words=%u stream_indexed=%u idx_pos=%u idx_reg=%u "
         "projreg_writes=%u numtex0=0x%x numtex_w=%u idxa0=0x%08x idxb0=0x%08x "
         "walk=%u/%zu benign=%u walk_ok=%d",
-        m8_mode, m8stream.draws, (unsigned long long)m8stream.verts, m8stream.epochs,
+        m8_mode != 0 ? m8_mode : m9_mode, m8stream.draws,
+        (unsigned long long)m8stream.verts, m8stream.epochs,
         m8stream.matidx_cp, m8stream.matidx_xf, m8stream.direct_xfmem,
         m8stream.direct_pos_words, m8stream.indexed, m8stream.idx_pos, m8stream.idx_reg,
         m8stream.projreg_writes, m8stream.numtex0, m8stream.numtex_w, m8stream.idxa0,
@@ -1551,6 +1869,149 @@
       Event(ename, csv);
     }
   }
+  // M9 step 2: VAT + texgen-enablement receipts (every M9 mode: each delta run
+  // carries its own M8 census above plus its own M9 VAT census here).
+  // xform_stats mode 10/11 = census/slot (same seam counters as M8's 7/8).
+  // m9_meta carries the walk summary; m9_path the shared-vs-indexed path table
+  // (position + per-texgen); m9_texen the numtex histogram + per-texgen
+  // enabled counts; m9_texep the enablement-epoch timeline
+  // (draw:numtex,...); m9_vat the vat-index histogram; m9_textype the
+  // per-texgen TexGenType histogram (texgen-major, 4 types); m9_reachp the
+  // shared-position reach per slot; m9_reach0-7 the shared+enabled texgen
+  // reach per slot.
+  if (m9_mode != 0) {
+    char xs[160];
+    std::snprintf(xs, sizeof(xs), "mode=%d slot=%d calls=%llu hits=%llu regcalls=%llu",
+                  m9_mode == 1 ? 10 : 11, s_m8_slot, s_m8_calls, s_m8_hits,
+                  s_m8_regcalls);
+    Event("xform_stats", xs);
+    char meta[448];
+    std::snprintf(
+        meta, sizeof(meta),
+        "mode=%d draws=%u verts=%llu vcd_lo=%u vcd_hi=%u vat_w=%u matidx_cp=%u matidx_xf=%u "
+        "numtex0=0x%x numtex_w=%u texinfo_w=%u epochs=%u "
+        "walk=%u/%zu benign=%u walk_ok=%d",
+        m9_mode, m9stream.draws, (unsigned long long)m9stream.verts, m9stream.vcd_lo,
+        m9stream.vcd_hi, m9stream.vat_w, m9stream.matidx_cp, m9stream.matidx_xf,
+        m9stream.numtex0, m9stream.numtex_w, m9stream.texinfo_w, m9stream.epochs,
+        m9stream.consumed, frame.size(), m9stream.benign,
+        int(m9stream.consumed == frame.size() && m9stream.unknown == 0));
+    Event("m9_meta", meta);
+    char path[1024];
+    std::snprintf(
+        path, sizeof(path),
+        "pos_shared=%llu pos_indexed=%llu "
+        "tex_shared=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_indexed=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu "
+        "tex_shared_enabled=%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu",
+        (unsigned long long)m9stream.pos_shared, (unsigned long long)m9stream.pos_indexed,
+        (unsigned long long)m9stream.tex_shared[0], (unsigned long long)m9stream.tex_shared[1],
+        (unsigned long long)m9stream.tex_shared[2], (unsigned long long)m9stream.tex_shared[3],
+        (unsigned long long)m9stream.tex_shared[4], (unsigned long long)m9stream.tex_shared[5],
+        (unsigned long long)m9stream.tex_shared[6], (unsigned long long)m9stream.tex_shared[7],
+        (unsigned long long)m9stream.tex_indexed[0], (unsigned long long)m9stream.tex_indexed[1],
+        (unsigned long long)m9stream.tex_indexed[2], (unsigned long long)m9stream.tex_indexed[3],
+        (unsigned long long)m9stream.tex_indexed[4], (unsigned long long)m9stream.tex_indexed[5],
+        (unsigned long long)m9stream.tex_indexed[6], (unsigned long long)m9stream.tex_indexed[7],
+        (unsigned long long)m9stream.tex_enabled[0], (unsigned long long)m9stream.tex_enabled[1],
+        (unsigned long long)m9stream.tex_enabled[2], (unsigned long long)m9stream.tex_enabled[3],
+        (unsigned long long)m9stream.tex_enabled[4], (unsigned long long)m9stream.tex_enabled[5],
+        (unsigned long long)m9stream.tex_enabled[6], (unsigned long long)m9stream.tex_enabled[7],
+        (unsigned long long)m9stream.tex_shared_enabled[0],
+        (unsigned long long)m9stream.tex_shared_enabled[1],
+        (unsigned long long)m9stream.tex_shared_enabled[2],
+        (unsigned long long)m9stream.tex_shared_enabled[3],
+        (unsigned long long)m9stream.tex_shared_enabled[4],
+        (unsigned long long)m9stream.tex_shared_enabled[5],
+        (unsigned long long)m9stream.tex_shared_enabled[6],
+        (unsigned long long)m9stream.tex_shared_enabled[7]);
+    Event("m9_path", path);
+    char txe[768];
+    int toff = std::snprintf(txe, sizeof(txe), "numtex_hist=");
+    for (u32 n = 0; n < 16; ++n) {
+      if (toff < 0 || size_t(toff) >= sizeof(txe) - 24) break;
+      toff += std::snprintf(txe + toff, sizeof(txe) - size_t(toff), "%s%llu", n ? "," : "",
+                            (unsigned long long)m9stream.numtex_hist[n]);
+    }
+    Event("m9_texen", txe);
+    char tep[1024];
+    int eoff = 0;
+    const u32 nepoch = m9stream.epochs < M9Census::kMaxEpochs ? m9stream.epochs
+                                                             : M9Census::kMaxEpochs;
+    for (u32 e = 0; e < nepoch; ++e) {
+      if (eoff < 0 || size_t(eoff) >= sizeof(tep) - 24) break;
+      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), "%s%u:%u", e ? "," : "",
+                            m9stream.epoch_draw[e], m9stream.epoch_numtex[e]);
+    }
+    if (m9stream.epochs > M9Census::kMaxEpochs) {
+      eoff += std::snprintf(tep + eoff, sizeof(tep) - size_t(eoff), ",TRUNC=%u",
+                            m9stream.epochs);
+    }
+    Event("m9_texep", tep);
+    char vat[256];
+    int voff = 0;
+    for (u32 i = 0; i < 8; ++i) {
+      if (voff < 0 || size_t(voff) >= sizeof(vat) - 24) break;
+      voff += std::snprintf(vat + voff, sizeof(vat) - size_t(voff), "%s%llu", i ? "," : "",
+                            (unsigned long long)m9stream.vat_hist[i]);
+    }
+    Event("m9_vat", vat);
+    char tty[512];
+    int yoff = 0;
+    for (u32 t = 0; t < 8; ++t)
+      for (u32 ty = 0; ty < 4; ++ty) {
+        if (yoff < 0 || size_t(yoff) >= sizeof(tty) - 24) break;
+        yoff += std::snprintf(tty + yoff, sizeof(tty) - size_t(yoff), "%s%llu",
+                              (t || ty) ? "," : "",
+                              (unsigned long long)m9stream.tex_type[t][ty]);
+      }
+    Event("m9_textype", tty);
+    char rcsv[2048];
+    int roff = 0;
+    for (u32 s = 0; s < 64; ++s) {
+      if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
+      roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
+                            (unsigned long long)m9stream.reach_pos[s]);
+    }
+    Event("m9_reachp", rcsv);
+    for (u32 t = 0; t < 8; ++t) {
+      roff = 0;
+      for (u32 s = 0; s < 64; ++s) {
+        if (roff < 0 || size_t(roff) >= sizeof(rcsv) - 24) break;
+        roff += std::snprintf(rcsv + roff, sizeof(rcsv) - size_t(roff), "%s%llu", s ? "," : "",
+                              (unsigned long long)m9stream.reach_tex[t][s]);
+      }
+      char rname[16];
+      std::snprintf(rname, sizeof(rname), "m9_reach%u", t);
+      Event(rname, rcsv);
+    }
+    // M9 step 3: survival receipt (armed only in mode 2 with SSX_M9_SURV=1).
+    {
+      float fb = 0, fa = 0;
+      std::memcpy(&fb, &s_m9_vbefore, 4);
+      std::memcpy(&fa, &s_m9_vafter, 4);
+      char surv[768];
+      std::snprintf(
+          surv, sizeof(surv),
+          "armed=%d slot=%d word=%u hits=%llu first=%d "
+          "vbefore=0x%08x vafter=0x%08x fbefore=%g fafter=%g vb_mm=%llu va_mm=%llu "
+          "hdirty_pos=%llu hdirty_texa=%llu hdirty_texb=%llu hdirty_pervtx=%llu "
+          "n=%u xf_after=%u xf_before=%u xf_other=%u "
+          "pv_after=%u pv_before=%u pv_other=%u "
+          "pos_res=%u pos_after=%u pos_before=%u pos_other=%u "
+          "tex_res=%u tex_after=%u tex_before=%u tex_other=%u "
+          "dirty_post=%u zfreeze=%d",
+          m9_surv, m9_slot, m9_mode == 2 ? u32(m9_slot) * 4 + 3 : 0, s_m8_hits,
+          s_m9_first_hit, s_m9_vbefore, s_m9_vafter, fb, fa, s_m9_vb_mm, s_m9_va_mm,
+          s_m9_hit_dirty_pos, s_m9_hit_dirty_texa, s_m9_hit_dirty_texb,
+          s_m9_hit_dirty_pervtx, replays, m9_xf_after, m9_xf_before, m9_xf_other,
+          m9_pv_after, m9_pv_before, m9_pv_other, m9_pos_res, m9_pos_after,
+          m9_pos_before, m9_pos_other, m9_tex_res, m9_tex_after, m9_tex_before,
+          m9_tex_other, m9_dirty_post, int(bpmem.genMode.zfreeze));
+      Event("m9_surv", surv);
+    }
+  }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```
