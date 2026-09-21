# G30 report — VRAM-content/circuit-content split: uploads land byte-exact, scene+Z raster lands, circuit mis-samples (b) on Adreno (Odin)

Brief: G30 (this turn) — executes G29 §4's ONE next action ONLY: the
VRAM-content/circuit-content split probe ((a) composite/scene GPU writes
unlanded/misplaced vs (b) `sample_quad` mis-samples on Adreno). Tables +
hypothesis + next-action recommendation, no verdicts beyond the hypothesis.
Time box 6 h (used ~0.6 h — measured wall 18:02:17→18:41 EDT; dir snapshot
→ commit). Read first per the brief: `local/research/G29/REPORT.md` (all of
it: ladder P1 = P2 = P3 = uniform `(0,0,0,128)` on all 10 images — readback
exonerated three ways; opaque-blit math makes scanout == circuit1 == VRAM
cleared pattern; graphics execution provably works; the defect sits between
VRAM bytes and circuit-fragment output). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8–G29 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g30/`
ONLY; removed at end (`mg/` only).

Headline result: **(b) — the writes landed, the circuit mis-samples.** (1)
Task 1 static work PROVED G29's VRAM checksum read LOAD state (host load
FNV `6002946899e9cae0` == G29's line byte-exact; mechanism: the replayer's
trailing `restart()` reloads all 4 MB before G29's post-loop read), so the
probe site MUST be pre-restart. (2) Expected-upload map re-verified from
the dump: 593 tags, all CT32, 38 distinct DBP dests (3 base + 35 stream),
every tag a complete logical transfer, last-write-wins in vsync#7; host
byte-exact prediction for 174 upload-only VRAM pages (swizzle port
differential-verified: 96,632 vectors, 0 mismatch). (3) ONE hunk (G30
pre-restart per-page VRAM dump, G29 ladder retained), ONE build (exit 0
`[458/458]`, full identity), verify-then-push with NO gap, ONE run:
**exit 0**, 512/512 `G30: vpage` lines + 10/10 ladder lines (== G29 values)
+ 1 `G29: vram` line (== load FNV again), ZERO new tombstone. (4) Page
verdicts: uploads **174/174 LANDED byte-exact** (device == predicted),
scene raster (FBP0, was 100% cleared in load) 112/112 CHANGED (bright
`ff490180`), Z raster (ZBP224) 112/112 CHANGED, control 510/511
UNCHANGED, ZERO stray — while FBP112 (circuit1's nominal source,
DISPFB1 = FBP 112/FBW 8/PSMCT24/DBX=DBY=0) holds STALE non-cleared load
bytes (99.96%) and the circuit emits uniform cleared `(0,0,0,128)`: the
circuit provably does not emit its source bytes, and NO uniformly-cleared
512×448 region exists anywhere in post-run VRAM. (a) is REFUTED for every
write class observed; the defect is downstream (composite→circuit stage).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g30-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g30/` (retrieval: logcat + stderr/stdout + 10 PPMs) | 50 MB | ~7.0 MB apparent; 25,600 KiB allocated PASS |
| SSD `ps2x-g10..g29` + G14/G15/G16/G18/G20/G22/G24/G26/G27/G28/G29 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g15 31744, g16 43008, g18–g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24–g25 5120, g26 5120, g27 28672, g28 25600, g29 25600; g14-build 4480000, g15-hwasan 4816896, g16-asan 4577280, g18/g20/g22/g24/g26/g28/g29-build 4482048, g27-hwasan 4817920 KiB) PASS |
| SSD clone (source) | ONE hunk max (diagnostic-dump ONLY) | ONE hunk in `tools/gs_dump_replayer.cpp` (+43/−0, UNCOMMITTED; G22 + G26 + G28 + G29 hunks untouched, HUNK_MATCH re-verified); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g30-*` ~40 KB (7 session scripts + harness + page tables, session-only); G30 evidence dir ~40 KB (text) PASS |
| device | `/data/local/tmp/g30/` ONLY | staged 2 files, pulled 13, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warning only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The pre-restart per-page VRAM dump discriminates (a) vs (b): upload pages == host-predicted ⟹ (b) (writes landed, sampler mis-reads); upload pages == load ⟹ (a)-unlanded; changed control pages or predicted-matches elsewhere ⟹ (a)-misplaced |
| observable signal | design tables (§2: load-proof + upload map + bounds + prediction + site + matrix) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + page verdicts + scanouts scored |
| alternatives | (a)-unlanded (pages == load everywhere writable); (a)-misplaced (pages == load at dests + stray changes); (b)-landed (pages == predicted); mixed per-class (finer split — verdict per write class) |
| stop condition | ONE hunk max (diagnostic-dump ONLY); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: (b) for uploads (174/174 byte-exact), scene raster, and Z raster;
FBP112 == stale load while the circuit emits cleared — the defect is
downstream of all observed write classes (composite→circuit stage). No
tuning loop was entered: one hunk, one build, one device run. Retry not
used (exit 0 — no retry condition); lldb not used (zero new tombstone —
nothing to triage).

## 2. Task 1 — static design (no device runs)

### 2a. Pin verification (pre-work — G29 §2a reproduced, ZERO edits before the hunk)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G29 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 39, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 214 (277+/4-) — G29 end state |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | `@@ -93,9 +96,15 @@` block present verbatim (pre-existing) |
| G29 ladder | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 markers) |
| Granite submodule | HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (== pin); 5 files incl. `memory_allocator.cpp` 19+/1- with `G28: create_image_view` ×1 (G28 hunk present, uncommitted) |
| G28 binary (re-sha, standing hygiene) | 265,841,104 B, sha `450471e2…` FULL-match, magic `7f45 4c46` ELF — **INTACT** |
| G29 binary (re-sha) | 265,846,144 B, **0 nonzero bytes**, sha `7c8593bd…` (all-zeros), magic `0000` — **8th zero-damage recurrence COMPLETED** (was mid-destruction `e353aabf…` at G29 report time; destruction is progressive, not instant) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G29 §0 exactly (see §0, snapshot 18:02); post-run re-verified §0 |
| recipe | NDK r30; cmake + ninja; G22/G26/G28/G29 non-sanitizer flags |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 29 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 10 PPMs (8 vsync + first + last) |

### 2b. G29-confounding proof (host load extraction — the site constraint)

State-blob layout verified against `dump/gs_dump_parser.cpp::restart()`:
regs 425 B + VRAM 4,194,304 B + GIF paths 80 B + internal_q 4 B = 4,194,813
== `state_size` EXACTLY; VRAM file offset = header + serial + shot + 425.

| check | observed |
| --- | --- |
| extraction receipt | bytes 0–32768 pure `00 00 00 80` (G13's cleared block-0 receipt reproduced) |
| host load full-VRAM FNV (truncated basis, G29-E1) | `6002946899e9cae0`, nz = 1,184,729, n = 4,194,304 |
| G29 on-device `G29: vram` line | `6002946899e9cae0`, nz = 1,184,729 — **BYTE-EXACT MATCH** |
| mechanism | replayer `do/while` calls `parser.restart()` after EVERY pass incl. the last; `restart()` rewrites all 4 MB VRAM from file (`map_vram_write` + `end_vram_write`); G29's read (first post-loop `save_scanout_ppm`) observed pristine reloaded load state |
| consequence | G29's "landing suggested" reading is WITHDRAWN (nz is pure load content); **the G30 dump site MUST be pre-restart** (after the last vsync loop, before the trailing `restart()`); the retained G29 line doubles as an on-device load-state receipt |
| load texture (record) | 0/512 pages fully cleared-pattern-at-page-size (block-0 cleared region is 32 KB = 4 pages; per-page cleared check); 23 fully-zero pages; standard-basis full FNV `b742cbfd8de2d75e` (record only) |

### 2c. Expected-upload map (re-verified against the dump — G13 §2e superset)

593 IMAGE tags walked (EOF_SYNC=yes); TRX regs persist across transfers
(HW regs, G13 precedent). TRXREG layout corrected during analysis: RRH sits
at bits 32–43 (`gs_registers.hpp`), not 16.

| property | observed |
| --- | --- |
| XDIR / DPSM / DBW / DSAX / DSAY / DIR / FLG | ALL 593 tags: XDIR=0 (host→local), DPSM=0 (PSMCT32), DBW=1, DSAX=DSAY=0, DIR=0, FLG=IMAGE2 — single-PSM world |
| per-vsync tag counts | #0,1,2,4,6: 61 each; #3,5,7: 96 each (== G10 `copies` exactly) |
| base shape (#0,1,2,4,6) | 3 distinct (DBP,DPSM,DBW): 10756 (20×4096 B, 16×64), 10820 (20×8192 B, 16×128), 11017 (21×16384 B, 16×256) — G13's DBP triple CONFIRMED |
| stream shape (#3,5,7) | 38 distinct dests (the 3 base + 35 more, one frag each: 4K/8K/16K cycling) — G13's "38" CONFIRMED |
| logical-transfer check | EVERY tag complete: frag bytes == RRW×RRH×4 (multi-frag rows = repeated overwrites of the same rect — one `copy_vram` per tag, last wins) |
| post-run determinism | vsync#7 covers all 38 DBPs; every dest's post-run content = its #7 last frag (base rewritten every vsync, stream on #3/#5/#7) |
| GPU-path proof | `num_copies++` only in `copy_vram` (+batched host/retention syncs); copies == tags exactly ⟹ ZERO CPU-path uploads, ZERO block/page syncs; `copy_threads`×4 B == IMAGE bytes exactly |

Full 38-DBP list (all PSMCT32/DBW=1): 10756, 10820, 10948, 11017, 11273,
11401, 11657, 11721, 11849, 12105, 12169, 12297, 12553, 12617, 12745, 13001,
13065, 13193, 13449, 13513, 13641, 13897, 13961, 14089, 14345, 14409, 14537,
14793, 14857, 14985, 15241, 15305, 15433, 15689, 15753, 15881, 16137, 16201.

### 2d. Raster bounds (state regs + packet census + on-device G11)

| source | observed |
| --- | --- |
| state ctx0/ctx1 FRAME | FBP=0, FBW=8, PSMCT32 (both); SCISSOR 512×448 (both); ctx0 TEX0 TBP0=10820 (== upload dest — textures sample uploads) |
| state ctx0 ZBUF (corrected decode) | ZBP=224, ZMSK=0 (bit 32 — writes ENABLED; an initial bit-28 read of ZMSK was corrected during analysis when device Z pages changed), ZTE=0/ZTST=0 (unconditional writes); ctx1 ZMSK=1 (masked) |
| packet A+D census | TEX0_1 ×776, ZBUF_2=0 ×609, **FRAME ×0** (G13's "FRAME writes: NONE" HOLDS) |
| on-device G11 records (G28 logcat) | composite: `FRAME FBP=112 FBW=8 PSM=1` (PSMCT24), 17 prims, tex TBP0=0; scene: `FRAME FBP=0 FBW=8 PSM=0`, 112/113 prims, 96 tex binds with TBP0 ∈ upload dests (10756/10820/…) |
| circuit nominal source (priv regs, all 8 vsyncs + initial) | EN1=1/EN2=0; DISPFB1 = FBP 112, FBW 8, PSMCT24, DBX=DBY=0 (EN/blend per G29: opaque blit, scanout == circuit1) |
| VRAM writer census | uploads (593 GPU `vram_copy`) + raster (FBP0/FBP112/ZBP224) ONLY: no local-to-local moves (all XDIR=0), pal=0 (no CLUT), `vsync()` contains ZERO VRAM writes (4278–5215: no copy/fill/map/flush — circuits render into fresh VkImages sampling `buffers.gpu` read-only) |

Page bounds (8 KB pages, CT32/CT24 swizzle — same addressing):
FBP0 512×448 → pages 0..111; FBP112 512×448 → 112..223; ZBP224 → 224..335;
uploads (38 rects, exact swizzle) → **174 pages, contiguous 336..509, no
wrap**; control → 510..511. Upload ∩ raster = ∅ (all 174 upload-only).

### 2e. Host prediction + swizzle verification

`vram_upload` CT32 semantics ported to host; vsync#7 last-frag payloads
applied onto the load blob: per-page predicted FNVs for all 174
upload-touched pages — **174/174 differ from load** (maximum discrimination;
device==pred ⟺ landed, device==load ⟺ unlanded, no ambiguity).

Swizzle port differential-tested against a standalone C++ harness built
from VERBATIM-extracted `get_data_structure` + `swizzle_PS2` bodies:
96,632 vectors (all 38 rects' full pixel sets + FBP0/FBP112 strided samples
+ wrap probes) — **0 mismatches**.

### 2f. Dump-site decision (tabled — exactly one shape picked)

| site | shape | verdict |
| --- | --- | --- |
| A. Pre-restart post-run VRAM pages (last pass, before trailing `restart()`) | replayer-TU loop body; `map_vram_read` (G29-proven mechanism) + per-8KB-page FNV/nz/head-8B × 512 lines, logcat only | **CHOSEN** — genuinely post-run (all writes complete, vsync mutates no VRAM); read-only; no render-path intrusion; discriminates (a)/(b) byte-exact via §2e prediction |
| B. In-`vsync()` circuit checksums | renderer-TU; GPU→host readbacks of circuit images mid-render | REJECTED — zero discrimination gain (circuit content already known 3 ways via P1/P2/P3 + opaque-blit proof) with real intrusion cost (new barriers/copies/timing in the render path) |
| C. Post-loop VRAM bytes (G29's site) | same read after the loop | REJECTED as primary — PROVEN load state (§2b); retained only as the G29-line load receipt |
| Ladder (G29 block) | retain vs remove | **RETAINED** — keeps the P1/P2/P3 control (proves this run's black == G29's black) + the load-state receipt; zero new risk |

Hunk spec: ONE contiguous +43/−0 insertion in `main()` after the last-pass
`for(;;)` vsync loop, guarded by `g8_last_pass`; FNV lambda duplicated
(self-contained — G29's lambda is out of scope; SAME truncated basis per
G29-E1). Costs tabled up front: +512 logcat lines (~50 KB; 1816 → ~2330
total, inside the buffer); runs inside the timed region (expect inflated
ms/VBlank — diagnostic cost, not a signal).

### 2g. Decision matrix (pre-registered)

| upload pages (336..509) | raster pages (0..223) | control (510..511) | reading |
| --- | --- | --- | --- |
| all == predicted | changed | == load | (b) pure — writes landed, sampler mis-reads |
| all == load | == load | == load | (a) unlanded-nowhere |
| == load at dests + stray changes / pred-match elsewhere | mixed | changed | (a) misplaced |
| mixed per class | mixed | mixed | finer split — verdict per write class |
| ≠ load AND ≠ predicted on upload pages | — | — | OTHER — re-examine the read mechanism (tear/stale map) |

## 3. Task 2 — ONE content probe + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G29's run is the G30 hunk)

| knob / flag | G29 setting | G30 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G29 = G28 + ladder | G30 = G29 + page-dump hunk | the single delta |

### 3b. Hunk record (ONE hunk, diagnostic-dump ONLY)

`tools/gs_dump_replayer.cpp`, ONE contiguous +43/−0 insertion (new lines
~310–352) in `main()` after the last-pass vsync loop, before
`parser.restart()`: `g8_last_pass`-guarded per-page VRAM dump (FNV-1a
truncated basis + nz + head 8 B × 512, `G30: vpage` LOGI; `G30: vram map
failed` fallback). Files/regs/loop untouched. Full diff text in
`g30-content.diff` beside this report (mechanically extracted: 43+/0-).
G22 HUNK_MATCH + G26 block + G28 Granite hunk + G29 ladder all untouched;
zero commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G29 recipe, `g30-build.sh` mirrored): exit 0
(`Configuring done (13.5s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`).

| item | observed |
| --- | --- |
| warnings | pre-existing `-Wshadow` (`FileDeleter`) only; zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,847,904 B (+1,760 vs G29 — the hunk; NEW size expected) |
| sha (build-time) | `a1963e661e27830f1233affede63792e4ac12a4b17b0e2d25245a70d8de08f82` (NEW) |
| build-id | `9452cce351d6b9c8af3c336e1bb1f8c59e4e622d` (distinct from G29 `662ab626…`) |
| plumbing presence | `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 18:26:50 | `a1963e66…` (binary) + `154d9d85…` (dump) FULL-match build sha |
| device stage | 18:26:50–53 | `rm -rf` + `mkdir` + push dump (0.015 s) + push binary (2.043 s) into `/data/local/tmp/g30/` ONLY |
| on-device sha match | 18:26:53 | `154d9d85…` + `a1963e66…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 18:27 | `logcat -c` (verified empty before) then run — no idle window |
| report-time re-sha | 18:30:44 | `a1963e66…` FULL-match + ELF magic — **binary INTACT, no 9th zero-damage recurrence this window** |

### 3e. Run table (ONE run — retry not used, §3i)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g30/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g30/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g30-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790029619→1790029620; logcat 18:27:00.0→18:27:00.7) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28/G29) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 512 `G30: vpage` (pass=1, pages 0..511 — all firing as designed) + 10 `G29: ladder` (§3f) + 1 `G29: vram` (§3f) |
| logcat | 2328 lines (== G29's 1816 + 512 vpage exactly): init + 18 `Running frame` + 18 G10 (warm == G29 exactly) + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 3.880 ms` (inflated vs G29's 1.807 — PREDICTED diagnostic cost inside the timed region, §2f) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 ERROR/LOGE; 0 `corrupted chunk` |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each, all sha `99418f1b…` — black files reproduced, byte-identical to G29); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (ladder + load line — continuity with G29)

| receipt | observed |
| --- | --- |
| 10 `G29: ladder` | ALL == G29 values: P1 = P2 = P3 = FNV `aa2fa32572450383`, nz = 229,376 (this run's black == G29's black; readback exoneration stands) |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz = 1,184,729 == host load FNV (§2b) — trailing-restart mechanism reproduced on-device a second time; comparison baseline exonerated |

### 3g. Page verdicts (the split — device vs load vs predicted)

| page class | pages | device == predicted (LANDED) | device == load | other |
| --- | --- | --- | --- | --- |
| uploads | 336..509 (174) | **174** | 0 | 0 |
| scene raster FBP0 | 0..111 (112) | n/a (no byte prediction) | 0 — **112 CHANGED** (bright `ff490180` heads: R=255/G=73/B=1/A=128 scene content over load-cleared) | — |
| Z raster ZBP224 | 224..335 (112) | n/a | 0 — **112 CHANGED** (Z-content heads `e7feff07…`) | — |
| composite FBP112 | 112..223 (112) | n/a | **112 UNCHANGED** (stale live content: 99.96% non-cleared words) | — |
| control | 510..511 (2) | n/a | **2 UNCHANGED** | — |
| stray predicted-match outside upload set | — | 0 | — | — |

Changed set == {0..111, 224..509} == FBP0 ∪ Z ∪ uploads EXACTLY. Zero
misplaced writes. Load-region content: FBP0 was 100% cleared-pattern in
load (scene visibly landed); FBP112 0.04% cleared (stale content);
ZBP224 12.05% cleared.

### 3h. Circuit-stage analysis ((b) — the sampler reads the wrong bytes)

| link | evidence |
| --- | --- |
| circuit1's nominal source | DISPFB1 = FBP 112/FBW 8/PSMCT24/DBX=DBY=0, all 8 vsyncs (§2d) → VRAM pages 112..223 |
| those bytes post-run | STALE load content (112/112 == load, 99.96% non-cleared) — NOT cleared pattern |
| circuit1's output | uniform `(0,0,0,128)` (ladder §3f + scanout files) — cleared pattern |
| cleared output matches NOTHING in VRAM | post-run VRAM holds no uniformly-cleared 512×448 region (FBP0 bright incl. ex-block-0 pages 0..3, FBP112 stale, Z Z-content, uploads textures; FBP112 holds only 83 scattered cleared words of 229,376 needed) |
| elimination | stale-source + cleared-output ⟹ the circuit does not emit its source bytes under ANY addressing of its nominal region; (a)-unlanded REFUTED for every observed write class (uploads byte-exact, scene+Z raster landed); (a)-misplaced has zero supporting pages |
| verdict | **(b): writes landed correctly; the sample/circuit path mis-samples on Adreno.** Whether composite VRAM write-back ALSO differs (mac FBP112 oracle absent) is secondary — it cannot explain cleared output from stale bytes. Residual split for the next probe: (b1) VRAM-sample misaddressing vs (b2) promoted-image content (promotion state unobserved — §4) |

### 3i. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g30` (tool exit 0): oracles **ALL OK** (8/8
pixel-shas); device PPMs: **10**, all black (`99418f1b…`), byte-identical
to G29 (`cmp` IDENTICAL on sampled + sha-unanimous). Score table
value-identical to G29 §3h:

| k | exact | \|d\|≤2 | \|d\|≤32 | PSNR R/G/B (dB) |
| --- | --- | --- | --- | --- |
| 1 | 0.0000 | 0.0000 | 0.0000 | 1.9 / 2.4 / 33.1 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 1.1 / 1.5 / 32.3 |
| 3 | 0.0000 | 0.0000 | 0.0000 | 0.4 / 0.8 / 31.2 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 5 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 6 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |
| 7 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 512 vpage lines + ladder + `Done!`; nothing to retry |
| second shape | NOT USED | out of budget by the stop rule (split closed on the first run) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The pre-restart per-page VRAM dump discriminates (a) vs (b) (upload pages == predicted ⟹ (b); == load ⟹ (a)-unlanded; stray changes ⟹ (a)-misplaced) | **CONFIRMED as (b), decisively.** 174/174 upload pages == host-predicted byte-exact (§3g: uploads landed with correct swizzle); scene raster 112/112 changed over load-cleared (bright content) and Z raster 112/112 changed (both landed); control unchanged; zero stray — while circuit1 emits uniform cleared pattern from a nominal VRAM source holding stale non-cleared bytes, and no uniformly-cleared 512×448 region exists anywhere in post-run VRAM (§3h). (a) is refuted for every observed write class. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **a circuit-input/promotion-state
probe brief (the next wall) — NOT adoption.** Rationale: G28 conditioned
adoption on understanding brightness — the black is now localized to "the
circuit path emits cleared pattern while its nominal VRAM source holds
stale non-cleared bytes" but the final (b1)-vs-(b2) split is open: (b1)
`sample_circuit` VRAM-sample misaddressing/mis-decode on Adreno vs (b2)
promoted-backbuffer-image content (promotion engaged but fed cleared bytes,
or engaged differently than mac). Discriminator: in-`vsync()` state dump
(`promoted1` null? + DISPFB-region VRAM bytes at sample time + promoted
image checksum if present) on the SAME dump/iterations. Queued behind it
(not this action): G26+G28 adoption once brightness is understood; the
Adreno filing — STILL OPEN regardless (content upgrades again: "uploads +
raster land byte-exact, circuit stage mis-samples with readback
exonerated"); G18-hunk fix adoption (still queued); O1 writer naming
(still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G30 additions | the ONE replayer hunk (SSD clone worktree only) + session files: `g30-build.sh` + `g30-run.sh` + `g30-content.diff` (G30-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanouts | run receipts of our own binary in SSD `ps2x-g30/` ONLY (not in git); no PII (`uid: shell`) |
| host analysis | `/tmp/g30-*.py` + `/tmp/g30-swizzle*` (session-only; swizzle harness built from verbatim-extracted function bodies, standalone, no repo deps) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
shasum -a 256 <g28-binary> ; xxd -l 16 <g28-binary>  # §2a INTACT (450471e2…)
python3 -c <nonzero census over g29-binary>          # §2a 0 of 265846144 (8th recurrence)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g30 + 11 build dirs> ; df -h / $SSD           # §0 (pre + post)
python3 /tmp/g30-load.py $SSD/ps2x-g13/g13-dump.gs               # §2b (load FNV == G29 line)
python3 /tmp/g30-xfers.py $SSD/ps2x-g13/g13-dump.gs              # §2c (38 dests, descriptors)
python3 /tmp/g30-regs.py $SSD/ps2x-g13/g13-dump.gs               # §2d (FRAME/ZBUF, ZMSK corrected)
python3 /tmp/g30-predict.py $SSD/ps2x-g13/g13-dump.gs            # §2e (174 pred pages)
clang++ -O2 -o /tmp/g30-swizzle /tmp/g30-swizzle.cpp ; python3 <diff-test>  # §2e (96632 vectors, 0 mismatch)
grep -h 'G11:   inst/tex' $SSD/ps2x-g28/g28-logcat.txt           # §2d (FBP112/FBP0 records)
python3 -c <priv DISPFB walk> ; python3 -c <FRAME-write census>  # §2d (DISPFB1=112, FRAME x0)
# (write the ONE hunk: pre-restart VRAM page dump, new lines ~310-352)
git -C $SSD/parallel-gs-g7 diff --stat ; diff tools/gs_dump_replayer.cpp | grep -c '^@@'  # hunk shape (+43/-0)
cmake -S <clone> -B $SSD/parallel-gs-g30-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g30-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warning
shasum -a 256 <g30-binary> (build, pre-push, report)            # a1963e66… x3 match (intact)
llvm-readelf --notes <g30-binary> ; strings grep x1/x1/x1/x2/x1/x1/x2/x0 ; xxd -l 4  # 9452cce3… + ELF
grep -h 'G30: vpage' <g30-logcat> | wc -l                          # §3e (512)
python3 /tmp/g30-score.py                                        # §3g (174/174 landed)
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g30  # §3i
cmp g29/g30 PPMs ; shasum <g30 PPMs>                            # byte-identical black files
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g30/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 29G)
shell 'rm -rf /data/local/tmp/g30 && mkdir -p /data/local/tmp/g30'
push <dump> $G30DIR/g13-dump.gs ; push <g30-binary> $G30DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G30DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G30DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g30-run-stdout.txt 2> g30-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (probe fired)
logcat -d -s Granite:V > $SSD/ps2x-g30/g30-logcat.txt                # 2328 lines
pull $G30DIR/g30-run-stderr.txt $SSD/ps2x-g30/ (0 B) ; pull stdout (0 B)
shell 'ls -la $G30DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts; ZERO new tombstone
pull $G30DIR/*.ppm $SSD/ps2x-g30/ (10 files)
shell 'rm -rf /data/local/tmp/g30 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The (b1)-vs-(b2) split is open: VRAM-sample misaddressing vs
   promoted-image content (queued as the §4 next action — needs
   in-`vsync()` promotion state + circuit-input bytes).
2. No mac VRAM oracle exists for FBP112 (would say whether composite
   VRAM write-back ALSO differs; out of budget — ONE build max, Android).
   The verdict does not need it (stale bytes ≠ cleared output either way).
3. The FBP=112 composite record's FRAME-state origin is unresolved (state
   ctxs are FBP=0, packets never write FRAME, yet records show FBP=112 —
   mechanism untraced; content-neutral for the split, bounds used the
   empirical G11 values).
4. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G30 binary intact at all three).
5. An initial ZMSK bit-28 misread was caught and corrected mid-analysis
   (true bit is 32; device Z-page changes forced the recheck) — final
   verdict uses the corrected decode (ctx0 ZMSK=0, writes enabled).
6. My quick priv-reg walk's PMODE MMOD/ALP bit positions were not used
   (G29's blend parse cited instead); only EN1/EN2/DISPFB1/DISPFB2 from
   that walk enter the verdict (all cross-checked vs G29/G11).
7. The `:3117` CPU-upload block (G29 gap 3), first/last stale oldLayout
   (G29 gap 4), the Δ=31 counter note (G13 §8.2), and the 1-stall question
   (G29 gap 5): carried, unjudged, content-neutral here.
8. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness per §4; no port, no upstream contact).
9. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
10. The zero-destroyed G29 binary was left destroyed (superseded binary,
    out of scope). 8th recurrence overall (completed this window); G28
    intact; G30 intact (no 9th recurrence).
11. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
12. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
13. Build warnings were observed via tail (pre-existing `-Wshadow` class);
    the full warning log was not retained — same treatment as G22–G29, and
    zero warnings point at the hunk lines.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g30/` (13 files: `g30-logcat.txt`
  2328 lines incl. 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g30-run-stderr.txt` 0 B, `g30-run-stdout.txt` 0 B, 10 PPMs × 688,143 B
  all `99418f1b…` black) +
  `parallel-gs-g30-android-build/` (binary 265,847,904 B `a1963e66…`
  BuildID `9452cce3…`, intact at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g29/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27/G28/G29 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 hunks uncommitted; Granite `16e7395f…` + G20-capture
  set + G28 hunk, all uncommitted — ZERO commits anywhere).
- Session-only: `/tmp/g30-*.py` (load/xfers/regs/predict/score),
  `/tmp/g30-swizzle.cpp` + binary, `/tmp/g30-load-pages.txt`,
  `/tmp/g30-predict-pages.txt`, `/tmp/g30-build.sh`, `/tmp/g30-run.sh`.
- Commits: ssx3 `local/research/G30/` `[G30]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G30 report ends here. Task-1 statics proved G29's VRAM read
was load state (trailing-restart mechanism) and built a byte-exact host
prediction for 174 upload-only pages (swizzle differential-verified); ONE
pre-restart page-dump hunk + ONE build exit 0 + ONE run exit 0 with 512/512
vpage lines shows uploads 174/174 LANDED byte-exact with scene+Z raster
landed and zero stray — while circuit1 emits uniform cleared pattern from
a stale non-cleared nominal source with no cleared 512x448 region anywhere
in VRAM: (b) CONFIRMED, (a) refuted per write class. Next wall is the
(b1)/(b2) promotion/circuit-input split, not adoption; filing still open.

Outcome: (b) — writes landed correctly (uploads byte-exact, scene + Z
raster landed, zero misplaced); the sample/circuit path mis-samples on
Adreno. No tuning loop was entered: one hunk, one build, one device run.
Retry not used (exit 0 — no retry condition); lldb not used (zero new
tombstone — nothing to triage).
