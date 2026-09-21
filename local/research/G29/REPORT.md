# G29 report — Black-scanout diagnosis: RENDER path — readback exonerated 3 ways, scanouts hold uniform VRAM-cleared-pattern (Odin)

Brief: G29 (this turn) — executes G28 §4's ONE next action ONLY: diagnose
the black (readback-path vs render-path — where do the zeros originate).
Tables + hypothesis + next-action recommendation, no verdicts beyond the
hypothesis. Time box 6 h (used ~0.5 h — measured wall 16:56:48→17:24 EDT;
dir snapshot → commit). Read first per the brief: `local/research/G28/
REPORT.md` (all of it: exit 0 with the writer demonstrably fixed, yet 10
scanouts byte-identical black to G27 — black is a SEPARATE device trait,
aliasing-caused REFUTED; flag, no-flag, sanitizer, and fixed runs ALL agree
on-device black vs BRIGHT mac oracles). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8–G28 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g29/`
ONLY; removed at end (`mg/` only).

Headline result: the zeros originate in the RENDER path. (1) Task 1 static +
log forensics could not discriminate from committed evidence (zero
intermediate pixel observations exist on-device, ever) but excluded every
code-level zero source on BOTH paths and named the ONE probe. (2) ONE hunk
(G29 ladder: per-image P1/P2/P3 checksums + once VRAM checksum, logcat only),
ONE build (exit 0 `[458/458]`, full identity), verify-then-push with NO gap,
ONE run: **exit 0**, 10 scanouts, ZERO new tombstone. (3) The ladder: all 10
images read **P1 = P2 = P3, FNV `aa2fa32572450383`, nz = 229,376** — three
independent readback mechanisms agree byte-for-byte on NONZERO data, and the
FNV solves to uniform **(0,0,0,128)** (RGB-black, half alpha). The files are
black because the render wrote RGB zeros, not because readback zeroed them.
(4) Dump priv regs (all 8 vsyncs: EN1=1/EN2=0/MMOD=ALP/ALP=`0xff`/BGCOLOR=0)
force an OPAQUE merge blit, so scanout == circuit1 == uniform VRAM cleared
pattern `00 00 00 80` — the circuits sample unlanded/misaddressed VRAM
content on-device while graphics execution itself provably works (clear,
raster, blend, copy, map, encode all exonerated). VRAM holds 1,184,729
nonzero bytes (load state + any run writes — split is the next probe).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g29-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g29/` (retrieval: logcat + stderr/stdout + 10 PPMs) | 50 MB | ~7.0 MB apparent; 25,600 KiB allocated PASS |
| SSD `ps2x-g10..g28` + G14/G15/G16/G18/G20/G22/G24/G26/G27/G28 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g15 31744, g16 43008, g18–g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24–g25 5120, g26 5120, g27 28672, g28 25600; g14-build 4480000, g15-hwasan 4816896, g16-asan 4577280, g18/g20/g22/g24/g26/g28-build 4482048, g27-hwasan 4817920 KiB) PASS |
| SSD clone (source) | ONE hunk max (diagnostic-dump ONLY) | ONE hunk in `tools/gs_dump_replayer.cpp` (ladder + VRAM checksum, UNCOMMITTED; G22 + G26 + G28 hunks untouched, HUNK_MATCH re-verified); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g29-privregs.py` ~1 KB (session-only); G29 evidence dir ~30 KB (text) PASS |
| device | `/data/local/tmp/g29/` ONLY | staged 2 files, pulled 13, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warning only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The ladder discriminates the black's origin: P2-or-P3-bright ⇒ READBACK path (render fine, zeros enter at readback); all-ladders-black + VRAM-nonzero ⇒ RENDER path scanout-localized; all-black + VRAM-zero ⇒ RENDER path upstream |
| observable signal | forensics tables (§2) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + scanouts scored + priv-reg/blend receipts + FNV proofs |
| alternatives | (a) P2/P3 bright ⇒ readback verdict + sub-cause (P2 names CachedHost-map, P3 names barrier-visibility); (b) all black + VRAM nonzero ⇒ render/scanout verdict; (c) all black + VRAM zero ⇒ render/upstream verdict; (d) O1/O3 instead of first draw ⇒ lottery note + ONE retry |
| stop condition | ONE hunk max (diagnostic-dump ONLY); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: a sharper-than-designed variant of (b) — all ladders AGREE on
NONZERO data (P1 = P2 = P3 = uniform `(0,0,0,128)`), so readback is
exonerated three ways AND the render defect is localized to circuit
sampling. No tuning loop was entered: one hunk, one build, one device run.
Retry not used (exit 0 — no retry condition); lldb not used (zero new
tombstone — nothing to triage).

## 2. Task 1 — forensics (no device runs)

### 2a. Pin verification (pre-work — G28 §2a reproduced, ZERO edits before the hunk)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G28 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 39, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 116 (179+/4-) — G28 end state |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | `@@ -93,9 +96,15 @@` block HUNK_MATCH (pre-existing) |
| Granite submodule | HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (== pin); 5 files incl. `memory_allocator.cpp` 18+/1- with `G28: create_image_view` ×1 (G28 hunk present, uncommitted) |
| G28 binary (re-sha, standing hygiene) | 265,841,104 B, sha `450471e2…` FULL-match, magic `7f45 4c46` ELF, BuildID `53af7a56…` — **INTACT** (the brief's "fixed G28 binary intact" premise holds; no rebuild needed) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G28 §0 exactly (see §0, snapshot 16:56:57); post-run re-verified §0 |
| recipe | NDK r30; cmake + ninja; G22/G26/G28 non-sanitizer flags |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 28 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 10 PPMs (8 vsync + first + last) |

### 2b. G10/G11 constraint table (which passes complete? what img=/texture state?)

G28's 18 G10 lines (16 shown + 2 resets; warm pass value-identical to G26):

| shape | prims | passes | pal | copies | copy_threads | scratch | img (cold / warm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #0, #1 | 130 | 2 | 0 | 61 | 147,456 | 885,440 | 1,966,080 / 28,672 / 0 |
| #2, #4, #6 | 129 | 2 | 0 | 61 | 147,456 | 883,352 | 0 / 0 |
| #3, #5, #7 | 129 | 2 | 0 | 96 | 229,376 | 1,211,032 | 327,680 (#3) / 0 |

Cross-run G10 constraints (all from retained SSD logcats):

| constraint | evidence | receipt |
| --- | --- | --- |
| BOTH iterations complete on-device (16 vsyncs) | 18 `Running frame` + 16 G10 vsync lines + 10 `G8: wrote` + `Done!` last | g28-logcat.txt:1795–1805 |
| G22 (no-flag) stats == mac stats EXACTLY | prims/passes/copies/threads/scratch/img-cold all match G13 §3a (scratch 919024/916936/1244616 both) | g22-logcat G10 block |
| scratch Δ=33,584 is FLAG-caused, not device-caused | G22 no-flag == mac; G26/G27/G28 flag-set all −33,584 uniformly (one feedback allocation gone) | G22 vs G26/G28 G10 blocks |
| uploads DISPATCHED identically on-device | copies = 61/96 = IMAGE-tag counts exactly; copy_threads×4 B = IMAGE bytes exactly | G10 all full runs |
| img= is allocation, not content | `allocated_image_memory` per vsync; warm pass all 0 (pools grown); cold residue layout-dependent (G27 HWASan differs, G28 §3b) | FlushStats struct + G10 |
| record order + binds == mac | 32 G11 records: 17-prim/tex=1 composite FIRST, then 112/113-prim/tex=96 scene — G13 §3a's structure exactly | g28-logcat (1664 G11 lines) |

### 2c. vsync/field handling vs the oracles' corrected labels

| constraint | evidence | receipt |
| --- | --- | --- |
| phases match dump on-device | G8 lines: phase 1,0,1,0…; 512×448 internal=mode, interlaced 0 — same as mac (G13 §3a) | g28-logcat G8 block |
| corrected labels hold | file N ↔ post-vsync#N (G12/G13, cited); oracle PPM#0 black on BOTH sides (cleared block-0 entailed), PPM#1–#7 bright | G13 §3c–§3d |
| device files == oracle #0's bytes | all 10 device PPMs sha `99418f1b…` == oracle vsync0/first; oracle #1–#7 distinct bright (`7e9daa21…`, `5d4ff853…`, `11370e59…`, `6aa54f3b…`×2, `bc5ca6de…`×2) | shasum ps2x-g13 + ps2x-g28 |
| one-frame lag does NOT explain device black | mac lag (G10/G11: scanout #k shows sprite(k−1), #0 black) still yields bright #1–#7; device is black at ALL k | G10 §3d, G11, G13 §3c |
| skip path dead | `vsync_can_skip` has decl + def but ZERO callers; parser calls `flush()` + `vsync()` directly | gs_interface.cpp:4741, gs_dump_parser.cpp:186-187 |

### 2d. Nonzero-evidence grep (all retained logcats — has anything EVER been nonzero on-device?)

| site | result |
| --- | --- |
| `ERROR\|LOGE\|Failed\|failed\|no image\|corrupted` over all 16 retained logcats | full runs (g22/g24/g26/g27/g28): ONLY the benign `Failed to load RenderDoc` line; early-crash runs: crash artifacts only; ZERO `no image`, ZERO pixel-content telemetry of ANY kind anywhere |
| pixel/census evidence on-device | NONE, ever — the ONLY on-device pixel observations in the whole series are the scanout PPMs (all RGB zeros) |
| nonzero DISPATCH evidence | abundant (prims/copies/threads/scratch/records/tex-binds all nonzero, §2b) — work is dispatched, pixels are the sole zero |

### 2e. Readback-chain walk (`save_scanout_ppm` — what it reads, what could zero it)

Chain (`tools/gs_dump_replayer.cpp:128-175`): `ScanoutResult.image` (fresh
`create_image` per vsync per circuit, `gs_renderer.cpp:4666/4724/4875` —
ref-counted, series-held; cross-vsync handle aliasing EXCLUDED by code) →
barrier READ_ONLY→TRANSFER_SRC → CachedHost buffer → copy → barrier →
submit + wait_idle → map READ → fwrite RGB → P6.

| zero candidate | verdict | receipt |
| --- | --- | --- |
| null image | EXCLUDED — 10/10 `G8: wrote`, 0 `no image` | logcats §2d |
| layout-mismatch barrier (B1) | EXCLUDED BY CODE — vsync honors the contract: fresh images, final barrier ATTACHMENT→`dst_layout` with proper COLOR_ATTACHMENT_WRITE srcAccess (`:4849-4853`, `:5019-5022`, `:5208-5210`); save's oldLayout is correct on first reads | gs_renderer.cpp vsync |
| stale CachedHost map (B2) | EXCLUDED BY CODE — `map_memory` invalidates non-coherent ranges on READ (`memory_allocator.cpp:489-503`); P1's map does invalidate | Granite device allocator |
| GPU-visibility gap (B3) | SPEC-VALID BY CODE — prior barrier made writes available (COLOR_ATTACHMENT_WRITE), save barrier gives TRANSFER_READ visibility + queue order + wait_idle | chain read |
| PPM encode | EXCLUDED — same encoder writes bright on mac; files faithfully carry given RGB | G13 oracles |
| Adreno mishandling a valid chain | OPEN (driver-behavior, unprovable statically) — the ladder's P2/P3 test exactly this | probe §2g |
| first/last stale oldLayout | NOTED (pre-existing): `first`/`last` re-read vsync0/vsync7 images already in TRANSFER_SRC while P1 claims READ_ONLY — mac-benign; cannot explain series black (first reads are correct) | replayer :246-249 + barrier |

### 2f. Render-chain walk (what could write black into the target)

Chain: IMAGE uploads → GPU `vram_copy` compute → VRAM storage buffer →
flush/raster compute → VRAM → circuit GRAPHICS (`sample_quad` samples VRAM
buffer, `:4144-4201`) → merge GRAPHICS blit (`blit_quad`, `:4918-5011`) →
barrier → READ_ONLY.

| zero candidate | verdict | receipt |
| --- | --- | --- |
| missing dispatch | EXCLUDED — G22 stats == mac exactly; G11 records/binds == mac (§2b) | logcats |
| sampler-feedback machinery | EXCLUDED as cause — flag (feedback OFF) and no-flag (feedback ON) both black; cause is in the COMMON path | G22 vs G26/G28 |
| G27 descriptor aliasing | REFUTED (G28 §3g) — writer fixed, pixels byte-identical pre/post fix | G28 |
| CPU-upload flush (`:3117` block lacks visible `end_`) | COLD for this dump — copies=61/96=IMAGE tags exactly ⇒ all uploads took the GPU `copy_vram` path; coherent scratch staging needs no flush | :2882-2920 |
| UMA VRAM flush | HANDLED — begin/end bracket + unmap-WRITE flush; discrete path n/a (UMA line logged) | :1513-1525, logcat |
| host-side scanout selection | EXCLUDED — same regs/dump ⇒ same EN/rects/blend; geometry/phases == mac | §2c |
| GPU-execution defect (shader/sampler/addressing on Adreno) | OPEN — no intermediate pixel observation exists; the ladder + VRAM checksum test exactly this | probe §2g |

### 2g. Task-1 verdict: NOT discriminated — the ONE probe

Static forensics excludes every host/code-level zero source on both paths
but contains ZERO on-device intermediate pixel observations, so no committed
evidence observes content at any pipeline stage. The discriminating
observation requires one device run. The ONE probe (single contiguous hunk
at ONE site — inside `save_scanout_ppm`, after the P1 map):

| leg | mechanism | names |
| --- | --- | --- |
| P1 | original path (CachedHost + READ_ONLY→TRANSFER_SRC barrier); checksum + file (unchanged behavior) | control: must reproduce black files |
| P2 | same-layout TRANSFER_SRC barrier + COHERENT Host buffer; checksum only | CachedHost-map/driver-invalidate zero |
| P3 | full-mask barrier (ALL_COMMANDS + all-write srcAccess) + coherent Host buffer; checksum only | GPU-visibility zero |
| VRAM | once-only `iface.map_vram_read(0, vram_size)` direct mapped read (no image copy); checksum only | upload+raster landing upstream |

Verdict matrix: P2-or-P3-nonzero ⇒ READBACK (render fine); all-black + VRAM
nonzero ⇒ RENDER scanout-localized; all-black + VRAM zero ⇒ RENDER upstream.
Common-mode caveat tabled: VRAM's different mechanism (direct map, no copy)
bounds any image-copy-common-mode misread.

## 3. Task 2 — ONE discriminating probe + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G28's run is the ladder hunk)

| knob / flag | G28 setting | G29 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G28 fixed | G29 = G28 + ladder hunk | the single delta |

### 3b. Hunk record (ONE hunk, diagnostic-dump ONLY)

`tools/gs_dump_replayer.cpp`, ONE contiguous +98 insertion (new lines
158–255) inside `save_scanout_ppm`: FNV-1a + nonzero-count lambda, P2/P3
re-read loop (coherent Host buffers, same-layout then full-mask barriers),
per-image `G29: ladder` LOGI, once-only `G29: vram` LOGI via
`iface.map_vram_read`. Files still carry P1 bytes; loop/timing untouched
(all after `end_ns`). Full diff text in `g29-ladder.diff` beside this
report (mechanically extracted: 2 context + 98 added + 1 context). G22
HUNK_MATCH + G26 block + G28 Granite hunk all untouched; zero commits in
submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G28 recipe, `g29-build.sh` mirrored): exit 0
(`Configuring done (13.5s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`).

| item | observed |
| --- | --- |
| warnings | pre-existing `-Wshadow` (`FileDeleter`) only; zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,846,144 B (+5,040 vs G28 — the hunk; NEW size expected) |
| sha (build-time) | `79e6f4d246869f6405091dfc6cc8dfeae9f11c540f241f4b52c96e49d6fe7303` (NEW) |
| build-id | `662ab626033d32c5c21f41414b483fde3024b3d0` (distinct from G28 `53af7a56…`) |
| plumbing presence | `G29: ladder` ×1, `G29: vram` ×2 (fnv + map-failed), `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 17:16:38 | `79e6f4d2…` (binary) + `154d9d85…` (dump) FULL-match build sha |
| device stage | 17:16:38–40 | `rm -rf` + `mkdir` + push dump (0.012 s) + push binary (2.090 s) into `/data/local/tmp/g29/` ONLY |
| on-device sha match | 17:16:40 | `154d9d85…` + `79e6f4d2…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 17:16:48 | `logcat -c` (verified empty before) then run — no idle window |
| report-time re-sha | 17:47 | `e353aabf4…` MISS + magic `0000` (size frozen) — **8th zero-damage recurrence (7th persistent)**; run validity UNAFFECTED (3 matching pre-run reads + on-device match; destruction came after the completed run) |

### 3e. Run table (ONE run — retry not used, §3i)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g29/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g29/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g29-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790025408→1790025409; logcat 17:16:48.4→17:16:49.1) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 10 `G29: ladder` (§3f) + 1 `G29: vram` (§3f) — all firing as designed |
| logcat | 1816 lines (== G28's 1805 + 10 ladder + 1 vram exactly): init + 18 `Running frame` + 18 G10 (warm == G28 exactly) + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 1.807 ms` + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 ERROR/LOGE; 0 `corrupted chunk` |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each, all sha `99418f1b…` — black files reproduced); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Ladder results (the discrimination — readback EXONERATED three ways)

All 10 images (vsync0–7 + first + last):

| leg | FNV-1a | nonzero bytes (n = 917,504) |
| --- | --- | --- |
| P1 (original CachedHost) | `aa2fa32572450383` | 229,376 |
| P2 (coherent Host, same barrier class) | `aa2fa32572450383` | 229,376 |
| P3 (coherent Host, full-mask barrier) | `aa2fa32572450383` | 229,376 |
| VRAM (direct mapped read, once) | `6002946899e9cae0` | 1,184,729 (n = 4,194,304) |

FNV proofs (host-recomputed, independent oracle):

| claim | proof |
| --- | --- |
| scanouts are uniform `(0,0,0,128)` | FNV-1a over 229,376 × `(0,0,0,128)` == `aa2fa32572450383` EXACTLY (X=128 solved over 1..255; the `(0,0,0,255)` guess gives `4613dfa1…`, mismatch) |
| nz = 229,376 = exactly 1 nonzero byte/pixel | RGB all zero (files carry RGB zeros) ⇒ the nonzero byte is alpha = 128 |
| P1/P2/P3 agree byte-for-byte | identical FNV across three mechanisms × 10 images; first == vsync0 and last == vsync7 (re-read determinism) |

Reading: the readback path is exonerated — three mechanisms (cached,
coherent, full-barrier) return IDENTICAL nonzero data, the copy/map/encode
chain provably works, and the files faithfully carry P1's RGB zeros. The
zeros originate UPSTREAM: the render wrote RGB-black into the scanout
images. The half-alpha (128, not 0 or 255) further proves the merge-blit
blend EXECUTED per regs (a pure bgcolor clear would carry alpha 0 —
`RenderPassInfo rp = {}` zero-inits clear alpha, `gs_renderer.cpp:4902-4912`).

### 3g. Priv-regs + blend math (scanout == circuit1 == VRAM cleared pattern)

Dump priv regs parsed with the G13 packet walk (all 8 vsyncs identical,
EOF-synced): EN1=1, EN2=0, MMOD=ALP(1), SLBG=0, **ALP=`0xff`**,
**BGCOLOR=(0,0,0)**, SMODE1=`0x40814504`, SMODE2=`0x1` (INT=1, FFMD=0 ⇒
alternative sampling + force_progressive ⇒ progressive, interlaced 0 ✓).

| step | consequence |
| --- | --- |
| EN2=0 ⇒ circuit2 null ⇒ no circuit2 blit | merge draws circuit1 only |
| MMOD=ALP + ALP=`0xff` ⇒ `if (ALP != 0xff)` false ⇒ NO blend enable | OPAQUE blit (`gs_renderer.cpp:4982-4996`): scanout == circuit1 verbatim |
| scanout uniform `(0,0,0,128)` ⇒ circuit1 uniform `(0,0,0,128)` | `00 00 00 80` IS the VRAM cleared pattern (G13 §3d: initial block-0 bytes pure `00 00 00 80`) |
| circuits draw full-coverage (nz = full pixel count) | raster + fragment + writeback EXECUTED; the fragment output equals cleared-pattern content |

So on-device the circuit sampler emits cleared-pattern content while the
same dispatch on mac emits bright scene content: the defect sits between
VRAM bytes and circuit-fragment output (composite writes unlanded/misplaced
vs sample addressing/decode on Adreno — the split is the §4 next action,
not this verdict).

### 3h. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g29` (tool exit 0): oracles **ALL OK** (8/8
pixel-shas); device PPMs: **10**, all black, byte-identical to G28
(`cmp` IDENTICAL). Score table value-identical to G27/G28 §3i:

| k | exact | \|d\|≤2 | \|d\|≤32 | PSNR R/G/B (dB) |
| --- | --- | --- | --- | --- |
| 1 | 0.0000 | 0.0000 | 0.0000 | 1.9 / 2.4 / 33.1 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 1.1 / 1.5 / 32.3 |
| 3 | 0.0000 | 0.0000 | 0.0000 | 0.4 / 0.8 / 31.2 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 5 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 6 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |
| 7 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |

The P1 path reproduced the black files exactly (ladder hunk changes no
render behavior — checksums are read-only).

### 3i. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + ladder + `Done!`; nothing to retry |
| second shape | NOT USED | out of budget by the stop rule (discrimination closed on the first run) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The ladder discriminates the black's origin (P2/P3-bright ⇒ readback; all-black + VRAM-nonzero ⇒ render/scanout; all-black + VRAM-zero ⇒ render/upstream) | **CONFIRMED, sharper than designed.** All 10 ladders read P1 = P2 = P3 = FNV `aa2fa32572450383` = uniform `(0,0,0,128)` (§3f): readback EXONERATED three ways (cached/coherent/full-barrier agree byte-for-byte on nonzero data; files faithfully carry P1's RGB zeros), so the zeros originate in the RENDER path. Opaque-blit blend math (ALP=`0xff`) makes scanout == circuit1 == VRAM cleared pattern `00 00 00 80` (§3g): graphics execution provably works end-to-end (dispatch == mac, raster/blend/copy/map/encode all exonerated) while circuit fragments emit cleared-pattern content. One hunk, one build, one device run; retry + lldb correctly unspent (§3i). |

The ONE next action the numbers justify: **a VRAM-content/circuit-content
probe brief (the next wall) — NOT adoption.** Rationale: G28 conditioned
adoption on understanding brightness — the black is now localized to
"circuit fragments emit cleared-pattern content" but the final split is
open: (a) composite/scene GPU writes never landed or landed misplaced in
VRAM (then sample reads true cleared bytes) vs (b) writes landed correctly
but `sample_quad` mis-samples/mis-decodes on Adreno (then sample reads the
wrong bytes). Discriminator: dump post-run VRAM bytes (or checksum circuit
images inside `vsync()`) and compare against dump-load state + expected
upload dests (DBP 10756/10820/11017 + 38 stream dests, G13 §2e). Queued
behind it (not this action): G26+G28 adoption once brightness is understood;
the Adreno filing — STILL OPEN regardless (content upgrades again:
"Granite init/use bug FIXED + verified + black localized to
circuit-sampling stage with readback exonerated"); G18-hunk fix adoption
(still queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G29 additions | the ONE replayer hunk (SSD clone worktree only) + session files: `g29-build.sh` + `g29-run.sh` + `g29-ladder.diff` (G29-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanouts | run receipts of our own binary in SSD `ps2x-g29/` ONLY (not in git); no PII (`uid: shell`) |
| dump priv-reg parse | `/tmp/g29-privregs.py` (~1 KB, session-only; walk reuses G13's verified packet framing) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
shasum -a 256 <g28-binary> ; xxd -l 16 <g28-binary> ; llvm-readelf --notes  # §2a INTACT (450471e2…, 53af7a56…)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g29 + 10 build dirs> ; df -h / $SSD           # §0 (pre + post)
grep -h G10:/G11:/G8:/Running <g22/g27/g28 logcats>              # §2b–§2c (18 G10, 32 G11 records, phases)
grep -h -c ERROR/LOGE/no image/corrupted <all 16 logcats>       # §2d (zero pixel telemetry, ever)
grep -n vsync/scanout/barrier/map/invalidate <gs+Granite sources>  # §2e–§2f chain walks (targeted greps + reads)
# (write the ONE hunk: save_scanout_ppm ladder + VRAM checksum, new lines 158-255)
git -C $SSD/parallel-gs-g7 diff --stat ; diff tools/gs_dump_replayer.cpp | grep -c '^@@'  # hunk shape
cmake -S <clone> -B $SSD/parallel-gs-g29-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g29-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warning
shasum -a 256 <g29-binary> (build, pre-push, report)            # 79e6f4d2… ×2 match, then e353aabf… destroyed
llvm-readelf --notes <g29-binary> ; strings grep ×1/×2/×1/×1/×2/×0 ; xxd -l 4  # 662ab626… + ELF
grep -h 'G29:' <g29-logcat>                                     # §3f (10 ladder + 1 vram)
python3 -c <fnv-uniform-proof> ; python3 /tmp/g29-privregs.py   # §3f–§3g (X=128, ALP=0xff/BGCOLOR=0)
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g29  # §3h
cmp g28/g29 PPMs ; shasum <g29 PPMs>                            # byte-identical black files
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g29/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g29 && mkdir -p /data/local/tmp/g29'
push <dump> $G29DIR/g13-dump.gs ; push <g29-binary> $G29DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G29DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G29DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g29-run-stdout.txt 2> g29-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (ladder fired)
logcat -d -s Granite:V > $SSD/ps2x-g29/g29-logcat.txt                # 1816 lines
pull $G29DIR/g29-run-stderr.txt $SSD/ps2x-g29/ (0 B) ; pull stdout (0 B)
shell 'ls -la $G29DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts; ZERO new tombstone
pull $G29DIR/*.ppm $SSD/ps2x-g29/ (10 files)
shell 'rm -rf /data/local/tmp/g29 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The final (a)-vs-(b) split is open: composite writes unlanded/misplaced
   vs `sample_quad` mis-sampling on Adreno (queued as the §4 next action —
   needs VRAM-byte or circuit-image content, not checksums).
2. VRAM checksum is load-state-confounded: 1,184,729 nonzero bytes mix dump
   load state (incl. cleared-pattern `00 00 00 80` regions, nonzero via
   alpha) with run writes — landing is suggested, not proven byte-wise.
3. The `:3117` CPU-upload block's missing visible `end_host_write_vram_access`
   is tabled unjudged (cold for this dump — all uploads took the GPU path;
   may matter for other dumps).
4. The first/last P1 barriers carry a stale oldLayout (re-reads of images
   already in TRANSFER_SRC) — mac-benign, noted, not implicated (series
   first-reads are correct and equally black).
5. The "1 graphics stall" observation (vs ≥2 graphics programs on the scanout
   path) stays an open question (async-no-stall is the plausible mechanism;
   no ERROR suggests every program compiled).
6. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness per §4; no port, no upstream contact).
7. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
8. The zero-destroyed G29 binary was left destroyed (run already complete
   and valid; rebuilding a receipt binary is out of scope). 8th recurrence
   overall (7th persistent; G28's 7th was reclassified transient per the
   brief). The G28 binary remains INTACT (re-verified `450471e2…`).
9. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
10. No lldb (decision tabled §3i); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
11. Build warnings were observed via tail (pre-existing `-Wshadow` class);
    the full warning log was not retained — same treatment as G22–G28, and
    zero warnings point at the hunk lines.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g29/` (13 files: `g29-logcat.txt`
  1816 lines incl. 10 `G29: ladder` + 1 `G29: vram`, `g29-run-stderr.txt` 0 B,
  `g29-run-stdout.txt` 0 B, 10 PPMs × 688,143 B all `99418f1b…` black) +
  `parallel-gs-g29-android-build/` (binary 265,846,144 B `79e6f4d2…`
  BuildID `662ab626…` at push time; zero-destroyed at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g28/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27/G28 build dirs + SSD clone (HEAD `3a66c19…`, G22 +
  G26 + G29 hunks uncommitted; Granite `16e7395f…` + G20-capture set + G28
  hunk, all uncommitted — ZERO commits anywhere).
- Session-only: `/tmp/g29-privregs.py` (~1 KB).
- Commits: ssx3 `local/research/G29/` `[G29]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G29 report ends here. Task-1 forensics excluded every
code-level zero source but could not discriminate (zero intermediate pixel
observations on-device, ever); ONE ladder hunk + ONE build exit 0 + ONE run
exit 0 with 10/10 P1 = P2 = P3 = uniform (0,0,0,128) EXONERATES readback
three ways — zeros originate in the RENDER path (opaque-blitted circuits
emit VRAM cleared pattern; graphics execution provably works). Next wall is
the VRAM/circuit-content split, not adoption; filing still open.

Outcome: sharper-than-designed variant of (b) — all ladders agree on NONZERO
data (P1 = P2 = P3), readback exonerated, render path named with
circuit-stage receipts. No tuning loop was entered: one hunk, one build,
one device run. Retry not used (exit 0 — no retry condition); lldb not used
(zero new tombstone — nothing to triage).
