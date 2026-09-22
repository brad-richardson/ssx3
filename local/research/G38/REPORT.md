# G38 report — First-composite-pass comparison, Mac vs Odin: the A→B producer/composite boundary (NO injection)

Brief: G38 (this turn) — REDIRECTS the lane to the reached divergence
(scene region A changes while composite destination B stays stale):
compare the SAME first composite pass on Mac and Odin at matched
packet/pass/field boundaries. Tables + hypothesis + next-action
recommendation, no verdicts beyond the hypothesis. Time box 8 h.
Read first per the brief, all of each:
`local/research/G30/REPORT.md` (scene at FBP0, composite targeting
FBP112), `local/research/G31/REPORT.md` (B stale-unchanged at every
sampled boundary while A changes), `local/research/G33/REPORT.md` §2c2
(B is zero-RGB — cleared output is the CORRECT render), and
`docs/research/review-2026-09-22-progress-and-parallelization.md`
§correction (the G30/G31 mis-sampling inference is WITHDRAWN;
G32/G34–G37 are positive controls). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8–G37 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir
`/data/local/tmp/g38/` ONLY; removed at end (`mg/` only).

Headline result: **the FIRST difference is at boundary 1 (pass 0,
vsync #1, seq 1, phase 0): Mac-B = `840cd308c91c4d8a`/699122/
`d5530000…` (composite#1's blit of scene#0 LANDED) vs Odin-B =
`eea04488c453e75b`/149721/`00000000…` (load — the write is MISSING).**
(1) Task 1 statics (ZERO device/Mac-run contact) pinned the first
composite pass to packet #0 (Transfer #0, path 3, 1056 B, GIF
qw2..qw49 — closing G30 gap 3: packets DO write FRAME_1 via PACKED
A+D), tabled 16 matched sample-time boundaries with byte receipts,
pre-registered correct-behavior (F0) + fault alternatives (F1–F4) with
per-observable predictions, and a 8-rule decision matrix — including
the pre-registered seq0 NON-DISCRIMINATION caveat (correct passthrough
of cleared scene predicts B==load, identical to the fault). (2)
Excision only (G37's +56 block removed — worktree == G31 source
exactly, zero new hunks), ONE Mac build (exit 0 `[458/458]`), ONE
budgeted Mac run (exit 0 — after voiding M0, a silent loader exit from
a mistranscribed env, with root-cause receipts) + ONE Odin run (exit 0,
G31 binary reused, zero rebuild): **16/16 CPU-alignment lines identical
Mac vs Odin** (FRAME/record/tex/flush/G10/G31-state — rule 1 never
fires), **A byte-exact ×16** (scene path agrees cross-GPU — rule 7
clean), **B == load on BOTH at seq0/seq8** (rule 3 confirmed
empirically) **then Mac ≠ load / Odin == load at all of seq1–7/9–15**
(rule 4 FIRES at seq=1), vpage delta confined EXACTLY to pages
112..223 (400/400 other pages identical), Mac scanouts black→content
(vsync0/first black, vsync1–7/last content — 1-frame-lag pipeline
visible end to end) vs Odin 10/10 black. F0-Mac CONFIRMED (composite =
alpha-masked blit, lands from seq1); F0-Odin REFUTED (Odin missing the
writes); F4 refuted-outside-A (again). The ONE next action is a
sub-vsync observation wall (§2d-granularity note) splitting F1
(rejected draw) vs F2 (unwritten B) vs F3 (stale-read) — NOT adoption.

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g38-mac-build` | 6 GB | 3,811,328 KiB PASS |
| NEW SSD `ps2x-g38/` (dump copy + M0 0-B pair + Mac stderr/stdout + 10 Mac PPMs + Odin logcat/stdout/stderr + 10 Odin PPMs) | 50 MB | 28 files, 35,840 KiB allocated PASS |
| SSD `ps2x-g7..g37` + G7/G14/G15/G16/G18/G20/G22/G24/G26/G27/G28/G29/G30/G31/G32/G33/G34/G35/G36/G37 build dirs (read-only) | 0 growth | all == 11:32:26 snapshot exactly (post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | excision + AT MOST one observation hunk | EXCISION ONLY (G37 +56 removed; ZERO new hunks; G22 + G26 + G28 + G29 + G30 + G31 untouched, HUNK_MATCH 5/5); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g38-*` ~100 KB (6 session scripts + build log + score outputs, session-only); G38 evidence dir text-only; `/` Used static 13 Gi (Avail 4.1→2.9 Gi is APFS accounting, not writes) PASS |
| device | `/data/local/tmp/g38/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host builds | ONE Mac build, `-j2`, new dir; NO Odin rebuild (reuse valid binary) | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only; G31 Odin binary reused (7 matching reads, §3d) PASS |
| device runs | ONE Mac + ONE Odin max, same shape | M0 voided (non-recipe env — tabled §3d0, zero observation); M1 Mac exit 0; O1 Odin exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + 6 session scripts; no binaries |
| share-tier mirror | — | `/Volumes/share/ssx3/ps2x-g38/` 28/28 files, `shasum -c` ALL OK PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The SAME first composite pass (packet #0, pass 0, vsync #0, phase 1, §2b–§2c) observed on Mac (reference) and Odin at matched boundaries locates the FIRST differing input, rejection, write, or dependency in the A→B producer/composite chain: source A bytes + composite state/selected draw + destination B before/after + final scanout |
| observable signal | design tables (§2: pins + packet map + boundary match + observation set + correct-behavior predictions + fault alternatives + decision matrix) + excision record + build/run identities + ONE Mac run + at most ONE Odin run of the SAME shape (exit/wall/fate + G11 FRAME/record + G10 + 16 `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` + tombstone census, each side) + 10+10 scanouts scored + first-difference verdict (§4) |
| alternatives | F0 correct-on-both (NO-DIFFERENCE — B-stale is correct behavior, lane redirects); F1 rejected draw; F2 unwritten B (write-back lost); F3 dependency-stale read; F4 wrong target (refuted-outside-A by G30 receipts); OTHER-partial (both write, differently); OTHER-upstream (CPU-alignment mismatch → STOP, no GPU comparison) |
| stop condition | excise G37's injection block ONLY + AT MOST one observation-only hunk; ONE Mac build (new dir); reuse of the existing observation binaries where valid (no Odin rebuild unless none valid); TWO bounded runs max (one Mac + one Odin, same shape); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage; any validity-chain pin mismatch → table + stop; Mac-run failures are OBSERVATIONS (table + stop that leg) |
| outcome → next action | numbers name the next single experiment (§4); G26+G28 adoption stays OUT (separate G39 brief, not a rider) |

Outcome: rule 4 — FIRST DIFFERENCE at boundary 1 (seq=1):
Mac-B `840cd308c91c4d8a`/699122 vs Odin-B `eea04488c453e75b`/149721
(load). Rules 1/5/6/7/8 never fired; rule 3 (seq0 non-discrimination)
confirmed empirically; rule 2 open-and-shut (Mac seq0 == load, as
predicted-likely). F0-Mac confirmed, F0-Odin refuted, F4
refuted-outside-A; F1/F2/F3 queued for the sub-vsync wall (§4). No
tuning loop was entered: excision only, one Mac build, one Mac run
(+1 voided non-run), one Odin run. Retry not used (both exit 0); lldb
not used (zero new tombstone — nothing to triage).

## 2. Task 1 — static design (no device, no Mac run)

Zero device contact in this section: no `adb` invocation of any kind
before §3d (host tools only: git/grep/shasum/python/du/df/clang++).
Zero Mac-run invocation before §3 (recipe audit only, §2h).

### 2a. Pin verification (pre-work — G37 end state reproduced, ZERO edits)

11:32–11:38 EDT (every pin re-checked before any edit):

| item | observed |
| --- | --- |
| working tree (brief: VERIFY, re-pin if migrated) | `/Users/bradrichardson/dev/ps2xGS` EXISTS (harness repo — not the lane clone) — VERIFIED, no re-pin; lane clone remains SSD `parallel-gs-g7` below (same as G37 §2a) |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G37 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 160, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 (441+/4-) — G37 end state + nothing (160 = G36's 163 − 59 + G37's 56) |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH 5/5: pre + post-excision + pre-push + post-run + report) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (Granite HEAD `16e7395f…` == pin; 5 files + `? third_party/spirv-tools` untracked, tabled content-neutral) |
| G29 ladder + G30 vpage + G31 state + G37 raw-access | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 in replayer; `G31: state` ×1 + `G31: bytes` ×2 + `G37: writeback` ×3 + `G36/G35/G34/G33: writeback` ×0 in interface) + retained G8/G10/G11 markers |
| G31 binary PASS1 (re-sha, the Odin observation binary) | 265,851,416 B, sha `c91719a0c96ef57a6ac2b80f6d4d29f54f515566bc249e0e2c4fd87a5d92367a` FULL-match build sha, magic `7f45 4c46` ELF — **INTACT** (PASS2 + on-device corroboration §3d) |
| rich dump PASS1 (host) | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match (PASS2 + predictor assert §2b) |
| dirs 0-growth | pre-run `du -sk` snapshot 11:32:26 (ps2x-g7 13312, g8 16384, g9 28672, g10 43008, g11 28672, g12 9216, g13 35840, g14 7168, g15 31744, g16 43008, g17 17408, g18–g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24–g26 5120, g27 28672, g28–g34 25600 except g31 5120, g35 24576, g36–g37 25600; g38 absent; g7-build 3808256, g14 4480000, g15-hwasan 4816896, g16-asan 4577280, g18/g20/g22/g24/g26/g28–g37 4482048, g27-hwasan 4817920 KiB; `/` 76% 4.1 Gi avail, SSD 94% 126 Gi free); post-run re-verified §0 (TBD) |
| recipe (Android leg) | NDK r30; NOT NEEDED — no Odin rebuild (G31 binary valid, §2i) |
| recipe (Mac leg) | VULKAN_SDK=/opt/homebrew + MoltenVK ICD present + timer shim present — audited §2h |
| session survivors | ALL `/tmp/g33-*` … `/tmp/g37-*` files PRESENT (same boot); authority rule honored — every prediction cites COMMITTED report scalars or fresh derivations below; survivors used as CROSS-CHECK only |

Lane-critical SSD bytes (dump, G31 binary, new Mac binary) are
corroborated by 2+ matching reads separated in time; single-read SSD
evidence is never relied upon (standing SSD rule).

### 2b. Packet map (host walk — `/tmp/g38-packets.py`, dump sha re-asserted on load)

Packet layout from `dump/gs_dump_parser.cpp::restart` +
`iterate_until_vsync` (FakeCRC + header_size + DumpHeader(36) +
serial/shot skip + regs 425 + VRAM 4 MiB + GIF paths 80 + internal_q 4
== state_size 4194813 + priv 8192 → packets at file offset 5431859):

| property | observed |
| --- | --- |
| packets | 4601, EOF_SYNC=True (end == file size exactly) |
| Vsync packets | 8 at packet idx [510, 1021, 1530, 2214, 2723, 3407, 3916, 4600], phases [1,0,1,0,1,0,1,0] (== G31 priv walk) |
| span sizes (xfers/privs/xfer-bytes) | #0: 509/1/626768; #1: 509/1/626768; #2: 507/1/626512; #3: 682/1/959792; #4: 507/1/626512; #5: 682/1/959792; #6: 507/1/626512; #7: 682/1/959792 (61/61/61/96-copy shape per G10/G30) |
| path init | path3 tag 0x3026400000008000/0x41f (IMAGE-mode residue — uploads flow on path 3) |

Span-0 GIF census (PACKED A+D exact per `gif_transfer`; ADDR = word
bits 64..71; FRAME_1 = 0x4c per `gs_register_addr.hpp:51`):

| xfer (packet #) | size | vertices | A+D notes |
| --- | --- | --- | --- |
| #0 | 1056 B | 34 PACKED XYZ | qw1: FRAME_1 = `0xff00000001080070` (FBP=112/FBW=8/PSM=1/FBMSK=ff000000 — byte-exact vs G11 logcat line 33); qw50: FRAME_1 = `0x0000000000080000` (FBP=0 — vs line 34); qw51: FRAME_2 FBP=0/FBMSK=ff000000 (no G11 line — bits unchanged from init) |
| #1 | 592 B | 32 via A+D XYZ2 (0x05) | PRIM=6 (sprite), RGBAQ, TEST_1 — first scene vertices @FBP0 |
| #2–#7 | small | 0 | state setup (SCISSOR/ALPHA/TEST/ZBUF/CLAMP/TRXDIR) |
| #8 | 4112 B | 0 (IMAGE) | first upload frag (4K leg of the base triple) |
| #12 | 80 B | 0 | FRAME_1 = `0x0000000000080000` (repeat FBP0 — SAME bits, no G11 line ✓) |
| rest | — | 4-per-xfer scene sprites + IMAGE uploads | scene body (113 prims total per device record) |

Span-0 FRAME_1 census: EXACTLY 3 writes, 2 changing (112 then 0).
G30 gap 3 ("FBP=112 origin unresolved — packets never write FRAME") is
CLOSED: packets DO write FRAME_1 via PACKED A+D (G30/G13's census
covered IMAGE tags only). Correction recorded, not re-litigated.

First-composite-pass packet identity: **packet #0 (Transfer #0, path
3, 1056 B), GIF qw2..qw49** — the 17 device-recorded prims between the
two FRAME_1 writes. Composite flush fires during packet #1 processing
(FRAME changed 112→0 with 17 prims pending → `check_frame_buffer_state`
FBPointer-class or TextureHazard flush; flush reason is unlogged —
queued, content-neutral for the boundary match).

### 2c. Boundary-match table (16 matched sample-time boundaries + load + post-loop)

Run shape (BOTH sides): dump `154d9d85…` + `--iterations 2` +
`--disable-sampler-feedback` + `PGS_SKIP_COMPILATION_TASKS=1`, no
sanitizer, source = G31-equivalent (G37 excised, zero new hunks, §2i).
Pass 1 repeats pass 0 after `restart()` reload (determinism check:
seq[i] == seq[i+8] expected both sides, both regions).

Sub-boundary structure within EVERY vsync span N (pass P, seq S,
Odin receipts = `ps2x-g31/g31-logcat.txt` line numbers for span 0;
all 16 spans share the shape):

| sub | event | span-0 Odin receipt | Mac match criterion |
| --- | --- | --- | --- |
| T0 | FRAME_1 → FBP112/PSM1/FBMSK=ff000000 (composite target set) | G11 line :33 | identical line on Mac stderr (CPU-deterministic) |
| T1 | FRAME_1 → FBP0/PSM0/FBMSK=0 (scene target set) | G11 line :34 | identical |
| T2 | composite hazard flush → record prims=17 inst=1 FBP112 + tex TBP0=0/TBW=8/TPSM=0 | G11 lines :41–:43 | identical (prims/inst/tex counts + values) |
| T3 | Vsync packet → flush() acc + scene record prims=113/112 @FBP0 + 96 tex | G11 lines :85–:86 (+tex) | identical (113 on spans 0–1, 112 on spans 2–7 per pass — G10/G11 unanimity) |
| T4 | post-`renderer.vsync` sample-time witness: G31 state (all fields) + bytes (A + B FNV/nz/head) | G31 lines :196–:197 | state fields identical; A/B FNVs = THE COMPARISON (§2e–§2g) |
| T5 | G10 vsync summary (prims/passes/pal/copies/copy_threads/copy_barriers) | G10 line :198 | identical EXCEPT scratch/img (allocator sizes — informational only) |

Boundary 0 (the FIRST composite pass): pass 0, vsync #0, seq 0,
phase 1, packets #0..#510 (span 0: 509 xfers + 1 priv + Vsync).
Boundaries 1..15: same shape (spans 1..7 × pass 1 after reload).

Load boundary (B-LOAD): A-load = cleared pattern (FNV
`aa2fa32572450383`/nz=229376 — G31 §2d trap note), B-load FNV
`eea04488c453e75b`/nz=149721/head=`00000000…`, full-VRAM
`6002946899e9cae0`/1184729 — host extraction + G29-vram receipt.

Post-loop boundary (B-POST): 512 `G30: vpage` (pass 1, pre-restart)
+ 1 `G29: vram` (post-restart load receipt) + 10 scanouts.

Match rule: T0–T3 + T5(−scratch/img) + G31-state are CPU-deterministic
from the same dump+source — ANY Mac-vs-Odin mismatch = OTHER-upstream
(STOP, no GPU comparison). Informational-only (driver-dependent, never
gating): scratch/img, `Total time per VBlank`, Stalled-compile
lines/counts, G28 receipt (fires iff supports==0 && feature==1 —
MoltenVK-dependent, content-neutral).

### 2d. Per-boundary observation table (A / state / draw / B-before / B-after / scanout)

B-before(composite#N) = B-after(vsync N−1) = G31-B(seq N−1); B-before
of boundary 0 = B-load. So the per-seq B series IS the before/after
chain at vsync granularity. (Sub-vsync pre/post-flush reads need a new
hunk — queued as the next wall IF the first difference needs
splitting, §2i.)

| observable | witness (each side) | Odin (committed G31) | Mac prediction (correct-behavior F0-class) |
| --- | --- | --- | --- |
| composite state | G11 FRAME_1 ×2/span + G31 state regs | FRAME 112→0; DISPFB1 112/8/1/0/0; DSP1 2560/447/4/0/641/50; SM 2/1/0; nprom/hack 0/0; p1null 1; phase alternating | IDENTICAL (CPU — alignment only, §2g NON-DISCRIMINATION note a) |
| selected draw | G11 record 17 + inst FBP112 + tex TBP0=0 | 17/1/1/1 + FBP112 + TBP0=0 ×16 | IDENTICAL (CPU — alignment only, note a) |
| source A per seq | G31 bytes A-field (FNV/nz/head) | varying ≠ load (nz 778796→915657, heads `d5530015…`→`ff490180…`); pass-repeat 8/8 | A LANDS (≠ load, varying, pass-repeat 8/8); byte-exact Mac==Odin SUPPORTING but NOT REQUIRED (cross-GPU raster variance allowed — note b) |
| dest B per seq | G31 bytes B-field | == load `eea04488…`/149721 ×16 | seq0: == load OR ≠ load (note c — THE seq0 caveat); seq1+: ≠ load (composite of bright scene writes nonzero-RGB — PRIMARY discriminator) |
| scanout per vsync (last pass) | G8 PPM + G29 ladder P1/P2/P3 | black ×10 (`99418f1b…`, `aa2fa325…`/229376) | == correct render of Mac-B-at-sample-time (seq8+k): black where Mac-B is RGB0, content where Mac-B gained RGB (downstream confirmation) |
| post-loop VRAM | G30 vpage ×512 | B pages == load; changed set == {0..111, 224..509} exactly | B pages == Mac pass-1 composite output (≠ load predicted — downstream confirmation) |

### 2e. Correct-behavior predictions per boundary (F0: "the implementation is behaving correctly")

F0-Mac (reference behavior — composite writes land): composite#N
executes its 17 prims sampling TBP0=0 (scene output of vsync N−1;
load-cleared for N=0) and writes FBP112 through FBMSK=ff000000 (RGB
written, alpha preserved). Per-seq B predictions:

| seq | composite input (A at flush) | F0 predicts Mac-B | rationale |
| --- | --- | --- | --- |
| 0, 8 | load-cleared (RGB=0 everywhere scene#0 unrun; restart reloaded) | == load LIKELY (passthrough/blend of RGB0 over RGB0 preserves B — FBMSK keeps alpha) but ≠ load POSSIBLE (constants/non-texel prims) | seq0 is CONDITIONALLY discriminating (note c) |
| 1–7, 9–15 | bright scene (nonzero-RGB, `ff490180…`-class) | ≠ load (nonzero-RGB written into B) | PRIMARY split vs Odin's == load ×16 |

F0-Odin (the explicit correct-on-Odin alternative): Odin-B == load
×16 is ALSO correct behavior — i.e., the composite function genuinely
preserves B on both sides (passthrough of RGB0 + masked alpha at every
seq — requires composite#1+ to sample RGB0 too, i.e. scene invisible
to composite reads). F0-Odin predicts Mac-B == Odin-B == load ×16
(NO-DIFFERENCE). If observed, the lane redirects (B-stale is correct;
G33's correct-render model covers the scanout; the "reached
divergence" dissolves — see §4 rule 5).

### 2f. Fault alternatives (conditioned on Mac showing the F0-Mac split)

| fault | mechanism | Odin-B prediction | Mac-B prediction | split needs (next wall) |
| --- | --- | --- | --- | --- |
| F1 rejected draw | composite draws rejected/dropped on Odin (cull/degenerate/resource) | == load ×16 | ≠ load at k≥1 (≠ load at 0 iff constants) | draw-accept logging (next-wall hunk) |
| F2 unwritten B | draws execute, writes don't land (Adreno coherency/barrier/addressing) | == load ×16 | same as F1 | post-flush B read + barrier audit (next-wall hunk) |
| F3 stale-read dependency | composite reads load-A every seq (scene writes invisible to its texture path) | == load ×16 (f of RGB0 preserves B — same trap as §2e) | ≠ load (Mac reads land) | A-visibility test (next wall) |
| F4 wrong target | composite writes land elsewhere on Odin | == load ×16 + STRAY changed pages | ≠ load, no stray | REFUTED-outside-A by G30 (changed set exact, zero stray); untestable-inside-A at page level — tabled, not pursued |

G32/G34–G37 positive controls (sampler exact under placed content;
1-word tag renders exactly) rule out a sampling/readback artifact for
ANY B difference: if Mac-B ≠ Odin-B at some seq, the bytes genuinely
differ in VRAM at sample time.

### 2g. Decision matrix (first-difference triage rules — BEFORE any run)

Boundaries compared in EXECUTION order (T2 composite-write precedes T3
scene-write within a span; spans in seq order). B compared before A
within a sample (execution order).

| # | condition | reading |
| --- | --- | --- |
| 1 | any CPU-alignment line differs (T0–T3, T5−scratch/img, G31-state) | OTHER-upstream → STOP, no GPU comparison (dump/source/shape mismatch) |
| 2 | Mac-B(seq0 or seq8) ≠ load while Odin-B == load | FIRST DIFFERENCE at boundary 0/8 (composite#0 write missing on Odin; F1/F2-class; F3/F4 splits queued) |
| 3 | Mac-B(seq0) == load == Odin-B(seq0) | seq0 NON-DISCRIMINATING (correct ≡ fault — pre-registered, note c) → advance to seq1 |
| 4 | first seq k≥1 (or k≥9) with Mac-B(k) ≠ load, Odin-B(k) == load | FIRST DIFFERENCE at boundary k (composite#k write missing; same fault class) |
| 5 | Mac-B == Odin-B == load ×16 (and scanout/vpage consistent) | NO-DIFFERENCE on B → F0 holds on both → REDIRECT lane (B-stale is correct; next question: why scene never reaches DISPLAY — 1-frame-lag pipeline vs genuinely-correct static frame) |
| 6 | Mac-B(k) ≠ load AND Odin-B(k) ≠ load but Mac ≠ Odin (any k) | OTHER-partial (both write, differently — new physics; per-page deltas name it; no F1–F4 verdict) |
| 7 | B matches but Mac-A ≠ Odin-A at some seq | scene-path variance note (triage by per-page deltas; byte-exact cross-GPU NOT required — UNCLASSIFIED pending triage, never alone a composite verdict) |
| 8 | B matches but scanouts differ | sample/scanout-path divergence (unexpected given G32+ controls — full triage, new theory) |

NON-DISCRIMINATION notes (process correction — honored per observable):
(a) CPU-side lines (FRAME/record/flush/G10-stats/G31-state) cannot
discriminate GPU behavior — alignment only. (b) A byte-exact match is
supporting, not required — cross-GPU raster variance is allowed; an A
difference without a B difference is UNCLASSIFIED, not a fault.
(c) seq0/seq8 B==load on BOTH sides cannot discriminate (correct
passthrough/blend of cleared scene predicts == load, identical to the
fault prediction) — the split lives at seq1+ UNLESS Mac shows ≠ load
at seq0 (rule 2). (d) scratch/img/Stalled/G28-receipt are
driver-dependent — informational only, never gating.

### 2h. Mac recipe audit (recipe from the repo's Mac path — audited before promising)

G7 REPORT §2a recipe (Mac/MoltenVK E1 PASSED + E3 replayed on this
machine class): configure `cmake -S <clone> -B <newdir> -G Ninja` with
`VULKAN_SDK=/opt/homebrew`; build `cmake --build <newdir> --target
parallel-gs-replayer -j2`; run with
`VK_ICD_FILENAMES=/opt/homebrew/etc/vulkan/icd.d/MoltenVK_icd.json`.

| audit item | observed |
| --- | --- |
| MoltenVK ICD | `/opt/homebrew/etc/vulkan/icd.d/MoltenVK_icd.json` PRESENT; molten-vk 1.4.2 installed (== G7) |
| timer shim | `M util/timer.cpp` (11 lines, G7's nanosleep shim) still in Granite worktree |
| LOGI routing (desktop) | `logging.hpp`: non-Android → `fprintf(stderr, "[INFO]: " …)` — ALL G-lines land on stderr (logcat-equivalent = captured stderr) |
| G22 | env-gated (`PGS_SKIP_SAMPLER_FEEDBACK`), unset → inert no-op — desktop-safe |
| G26 | unconditional debug_mode delivery + LOGI — desktop-safe |
| G28 | guard + receipt, driver-queried — desktop-safe (receipt ×0-or-1 per MoltenVK features — informational, §2c) |
| G29/G30/G31/G8/G10/G11 | plain C++ + LOGI + `map_vram_read` (same class as Android) — compile risk only, low |
| PPM outputs | `dump_path + ".g10-….ppm"/".g8-first/last.ppm"` (replayer :387–390) — written ALONGSIDE the dump ⇒ Mac run needs a dump COPY in the NEW `ps2x-g38/` dir (11.5 MB — inside the 50 MB cap; sha-verified before the run) |
| space | SSD 126 Gi free (Mac build ~3.7 GB precedent `parallel-gs-g7-build` — fits 6 GB cap); `/` 4.1 Gi avail, no builds on `/` |
| pre-existing desktop binary | `parallel-gs-g7-build/tools/parallel-gs-replayer` (51 MB, Sep 20, G7-era source — PREDATES all observation hunks → NOT valid for G38; the ONE new Mac build is required) |

Mac-run failure policy (per brief): failures are OBSERVATIONS (table +
stop that leg — no fix beyond the recipe; a broken Mac recipe is itself
a finding for the next brief).

### 2i. Excision + observation hunk (named)

Excision: **G37's raw-access shrunken-tag placement block** (+56/−0 in
`GSInterface::vsync`, immediately pre-`renderer.vsync`) — derived from
the committed `local/research/G37/g37-shrunken-placement.diff` `+`
lines (no transcription); diff survives committed — LOSSLESS and
REQUIRED (live tag content would confound the baseline comparison).
Post-excision arithmetic (pre-registered): worktree
`gs/gs_interface.cpp` diff 160 − 56 = **104** (== G31 end state
39 + 65 — G32 §2a receipt).

Observation hunk: **NONE.** Retained witnesses cover all five
observation classes at per-vsync granularity (G11 FRAME/record ×32,
G10 ×18, G31 state/bytes ×16, G30 vpage ×512, G29 ladder ×10 + vram,
G8 scanouts ×10 — §2d). Sub-vsync granularity (pre/post-flush B reads,
flush-reason logging) is queued as the next wall IF the first
difference needs splitting. Consequences: post-excision source ==
G31 source exactly ⇒ the existing G31 Odin binary IS the valid
observation binary (re-verified §2a/§3d) ⇒ NO Odin rebuild per the
brief's build-budget rule; the ONE Mac build comes from the same tree
⇒ perfectly matched comparison.

## 3. Task 2 — ONE Mac run + ONE Odin run (SAME shape)

### 3a. Knob matrix (identical shape both legs — the ONLY deltas are platform + binary)

| knob / flag | Mac (M1) | Odin (O1) | rationale |
| --- | --- | --- | --- |
| dump | `g38-dump.gs` (copy of `154d9d85…`, sha-verified §3d) | `g13-dump.gs` (`154d9d85…`) | same bytes (copy forced by alongside-PPM rule §2h) |
| `--iterations 2` | SET | SET | same pass shape |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| source | excised tree (== G31) | excised tree (== G31) | matched comparison |
| binary | NEW Mac Mach-O `321e8582…` | REUSED G31 ELF `c91719a0…` (no rebuild — valid, §2i) | the single delta (platform) |
| Vulkan driver | MoltenVK 1.4.2 (`VK_ICD_FILENAMES` + `DYLD_LIBRARY_PATH=/opt/homebrew/lib` — full G7 env) | Adreno 830 | reference vs target |

### 3b. Excision record (ONE edit, zero new hunks)

`/tmp/g38-excise.py` (mirrored): asserts G37-block ×1 (derived from
the committed `g37-shrunken-placement.diff` `+` lines — no
transcription) + immediately-pre-anchor + anchor ×1 + G36/G35-absent;
single file write; post-asserts G37-gone + G31 neighbors intact.
DRY-OK then APPLIED (one applier self-bug — a doubled newline in the
join — caught by the DRY assert, fixed, re-DRY-OK; tabled, no
worktree write before the fix).

| item | observed |
| --- | --- |
| worktree `gs/gs_interface.cpp` diff | 160 → **104** (== 160 − 56; == G31 end state 39 + 65 — arithmetic closes per §2i) |
| markers post-excision | G37 ×0; G31 state ×1 / bytes ×2; G30 vpage ×1; G29 ladder ×1; G26 ×1; G28 ×1; G22 HUNK_MATCH (post + pre-push + post-run + report — 5/5 with §2a) |
| Granite | HEAD `16e7395f…` == pin; zero commits |
| ps2xGS superproject | clean, HEAD `fd781ef`, zero commits (never touched) |

### 3c. Build record (ONE Mac build, NEW SSD dir — all older dirs untouched)

Configure (G7 recipe + full env audit §2h, `g38-build-mac.sh`
mirrored): exit 0 (`Configuring done (141.1s)`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0
(`[458/458]`, 11:41→11:45).

| item | observed |
| --- | --- |
| warnings | pre-existing classes only (`-Wshadow FileDeleter` ×3, `-Wunused-function is_legacy_layout`, `-Wdeprecated sprintf` ×2, `-Wunused-private-field`, thread-priority `#warning`, ld duplicate-libs); zero warnings in `gs_interface.cpp` / `gs_dump_replayer.cpp` / `memory_allocator.cpp` (zero point at hunk lines) |
| binary | `tools/parallel-gs-replayer`, 51,898,120 B (Mach-O 64-bit arm64, magic `cffa edfe`) |
| sha (build-time) | `321e85826c4a2d134c71da36101ab8b0699ffd5aa8aa228c83055889846e0625` (NEW; stable at pre-run + report re-shas) |
| plumbing presence | `G37/G36: writeback` ×0 (excision proven in binary), `G24:` ×0; all observation markers present (`G31: state` ×2, `G31: bytes` ×4, `G30: vpage` ×2, `G30: vram` ×2, `G29: ladder` ×2, `G29: vram` ×4, `G28:` ×2, `G26:` ×2, `G11: record` ×2, `G10: pass` ×4, `G8: wrote` ×2 — 2× Android counts: LOGI's dual-expansion literal lands twice in Mach-O `strings`; pattern self-consistent) |
| build dir | 3,811,328 KiB (cap 6 GB ✓) |

No Odin build: the G31 binary (`c91719a0…`, ELF, 265,851,416 B)
re-verified with SEVEN matching reads (build-time record + PASS1
11:32 + PASS2 11:40 + pre-push 11:48 + on-device 11:49 + post-run +
report) — valid, reused per the brief's build-budget rule.

### 3d0. M0 — voided non-run (tabled with root-cause receipts, zero observation)

M0 (11:46): exit 1, 0 B stdout + 0 B stderr, ~1 s wall. Read-only
diagnosis (no second run, no second shape to diagnose): no fresh crash
report (not a crash); codesign silent; static link (no missing dylib);
`main()` has a SILENT `return EXIT_FAILURE` when
`Context::init_loader(nullptr)` fails (replayer :79–80); the loader
`dlopen("libvulkan.1.dylib")`/`dlopen("libMoltenVK.dylib")` cannot
resolve from `/opt/homebrew/lib` without `DYLD_LIBRARY_PATH` — and
G7's recipe DOES set it (G7 REPORT §2b:91–93 + §6:255), which the §2h
audit mistranscribed. M0 executed ZERO lane code (no log line, no
Vulkan, no dump read) — observationally equivalent to "binary not
run". VOIDED as a non-recipe execution; the ONE budgeted recipe-faithful
Mac run (M1) executed next. M0's 0-B pair preserved as
`g38-m0-mac-stdout/stderr.txt`. Lesson recorded: recipe audits must
quote the prior brief's §6 exact-commands env VERBATIM (this brief's
§2h now carries the full env for the next lane).

### 3d. Verify chains with NO gap (both legs)

Mac leg (host reads; binary + dump copy):

| step | time (EDT) | observed |
| --- | --- | --- |
| dump copy + sha | 11:45 | `g38-dump.gs` 11,537,377 B `154d9d85…` FULL-match pin |
| M1 pre-run re-sha | 11:47 | `321e8582…` (binary) + `154d9d85…` (dump) FULL-match |
| M1 launch | 11:47 | full G7 env + same shape — no idle window |
| report-time re-sha | 11:51 | `321e8582…` FULL-match + Mach-O magic — binary intact |

Odin leg (standing verify-then-push):

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (PASS3) | 11:48:29 | `c91719a0…` (binary) + `154d9d85…` (dump) FULL-match; HUNK_MATCH; markers; old dirs 0-growth |
| device stage | 11:48–49 | pre-check (Odin3, Android 15, `mg/` only, newest tombstone _23, 28 G free) then `rm -rf` + `mkdir` + push dump (0.029 s) + push binary (2.172 s) into `/data/local/tmp/g38/` ONLY |
| on-device sha match | 11:49 | `154d9d85…` + `c91719a0…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 11:49 | `logcat -c` (verified empty: no Granite lines before) then run — no idle window |
| on-device post-run re-sha | 11:49 | `c91719a0…` FULL-match — intact |
| report-time re-sha | 11:51 | `c91719a0…` FULL-match + ELF magic — intact, no zero-damage recurrence this window |

No validity-chain pin mismatched at any gate: the stop rule never fired.

### 3e. Run tables (M1 + O1 — both exit 0)

| item | Mac (M1) | Odin (O1) |
| --- | --- | --- |
| staging | `ps2x-g38/g38-dump.gs` (sha-verified copy) | `/data/local/tmp/g38/` ONLY; 2/2 on-device shas FULL-match host (§3d) |
| command | `PGS_SKIP_COMPILATION_TASKS=1 …/parallel-gs-replayer ps2x-g38/g38-dump.gs --iterations 2 --disable-sampler-feedback` + full G7 env (`g38-run-mac.sh` mirrored) | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer …/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g38-run-odin.sh` mirrored) |
| exit / wall | **0** / ~2 s (`date` 1790092062→1790092064) | **0** / ~1 s (`date` 1790092162→1790092163) |
| FIX receipt | `G28:` ×0 (MoltenVK: no supports/feature split — informational per §2c) | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G37) |
| NARROWING receipt | `G26: debug_mode delivered` ×1 | ×1 (same) |
| DIAGNOSTIC receipts | 16 `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`; 0 map-fails | same counts; 0 map-fails |
| log | 2349-line stderr: init (`Found Vulkan GPU: Apple M4` class) + 18 `Running frame` + 18 G10 + 32 G11 records + 9 Stalled posts all `success: yes` + `Total time per VBlank: 8.018 ms` + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 ERROR; the single RenderDoc init line is pre-existing noise | 2360-line logcat (== G31's 2360 exactly): init + 18 `Running frame` + 18 G10 + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 8.258 ms` + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; same RenderDoc noise |
| fate | clean exit 0 through Device teardown | clean exit 0 through Device teardown |
| outputs | 10 scanouts (688,143 B each) + stdout 0 B | 10 scanouts (688,143 B each, explicit pull) + stdout/stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

Line-count delta 2349 vs 2360 = 9 Mac-Stalled vs 8 Odin-Stalled
(−1) + driver-specific init-line counts (−10) — all informational,
pre-registered as non-gating (§2c).

### 3f. Control receipts (both legs — continuity + determinism)

| receipt | Mac | Odin (fresh) |
| --- | --- | --- |
| 1 `G29: vram` | `6002946899e9cae0`/1184729 == host load FNV (restart control passes — 10th on-device reproduction counting G29–G37) | same (11th) |
| 16 A-lines pass-repeat | 8/8 EXACT (seq[i]==seq[i+8]) | 8/8 EXACT |
| 16 B-lines pass-repeat | 8/8 EXACT | 8/8 EXACT (trivially — all load) |
| fresh-Odin vs committed-G31 | — | FRAME 32/32 + RECORD 1616/1616 + FLUSH 16/16 + G10 18/18 + STATE 16/16 + BYTES 16/16 + VPAGE 512/512 + LADDER 10/10 + VRAM + RUN 18/18 timestamp-stripped EQUAL (only `G8: wrote` paths differ: `g38/` vs `g31/` — the run dir) — excision non-perturbation PROVEN |
| Mac vs Odin CPU-alignment | FRAME 32/32 + RECORD 64/64 + TEX 1552/1552 + FLUSH 16/16 + G10 18/18 (scratch/img-normalized) + STATE 16/16 + RUN 18/18 EQUAL | (rule 1 never fires) |
| G10 full-line (incl scratch/img) | 17/18 equal; the 1 diff = pass 0 vsync #5 img 327680 (Mac) vs 0 (Odin) — allocator-size class, informational per §2g note d | — |

### 3g. State + bytes verdicts (the comparison — Mac vs Odin per seq)

State lines: 16/16 field-identical both sides (EN1/EN2 1/0, DISPFB1
112/8/1/0/0, DSP1 2560/447/4/0/641/50, SM 2/1/0, nprom/hack 0/0,
p1null/p2null 1, phase alternating — == G31 predictions).

Bytes lines (16/16 fire both sides, 0 map-fails):

| seq | A Mac==Odin | B Mac | B Odin | B Mac==Odin |
| --- | --- | --- | --- | --- |
| 0, 8 | YES (byte-exact) | == load `eea04488…` | == load `eea04488…` | YES — rule 3 (non-discriminating, as pre-registered) |
| 1, 9 | YES | `840cd308c91c4d8a`/699122/`d5530000…` | == load | **NO — rule 4 FIRES (first at seq=1)** |
| 2, 10 | YES | `f4309a0811acdc25`/699122/`eb5c0000…` | == load | NO |
| 3, 11 | YES | `b69df312be23faec`/826205/`ff640000…` | == load | NO |
| 4–5, 12–13 | YES | `afe33fd83d762d2e`/836140/`ff590200…` | == load | NO |
| 6–7, 14–15 | YES | `ad874f4b69bebd73`/835477/`ff490100…` | == load | NO |

Mechanism note (read off the heads, no new model needed):
Mac-B(seq1) head `d5530000…` == scene#0's A-head `d5530015…` with alpha
zeroed — exactly the alpha-masked blit the composite state predicts
(FBMSK=ff000000 preserves load-alpha 0x00 over the sampled RGB). The
correct composite function is CONFIRMED as a blit; Odin is missing the
writes from composite#1 onward (F1/F2/F3 — §4).

Ladders: Mac vsync0+first == cleared `aa2fa325…`/229376 (B==load at
seq8 ✓ consistent); Mac vsync1–7+last show content (P1=P2=P3:
`d111f164…`/778777, `57ca89e6…`/778777, `d6168520…`/905860,
`6552ff91…`/915795 ×2, `fdfd4f4d…`/915132 ×2+last — equalities track
the B-series equalities seq12==13, seq14==15 ✓); Odin 10/10 cleared.
P1==P2==P3 unanimous both sides (readback consistent).

Vpage (pass 1, pre-restart): 512/512 lines both sides; differing
lines == EXACTLY the 112 B pages (112..223); other 400/400 pages
timestamp-stripped identical Mac vs Odin. The cross-platform VRAM
delta is EXACTLY the composite destination — no stray, no scene delta.

### 3h. Split analysis (rule 4 — the composite#1+ writes are missing on Odin)

| link | evidence |
| --- | --- |
| boundaries matched | 16/16 CPU-alignment classes identical Mac vs Odin (FRAME/record/tex/flush/G10/G31-state); rule 1 never fired — the GPU comparison is valid |
| scene path agrees | A byte-exact ×16 cross-GPU (Adreno vs Apple); rule 7 clean — stronger than the required supporting level |
| seq0 non-discrimination confirmed | B == load on BOTH at seq0/seq8 — the pre-registered note-c caveat is empirical, not just theoretical (correct blit of cleared scene preserves B) |
| FIRST DIFFERENCE at boundary 1 | pass 0, vsync #1, seq 1, phase 0, span packets #511..#1021: Mac-B `840cd308c91c4d8a`/699122/`d5530000…` (composite#1's blit of bright scene#0) vs Odin-B `eea04488c453e75b`/149721/`00000000…` (load — write missing) |
| persistence | Mac ≠ load / Odin == load at ALL of seq1–7/9–15; vpage delta == exactly pages 112..223; Mac scanouts black→content vs Odin 10/10 black |
| elimination | OTHER-upstream never triggered (alignment unanimous); OTHER-partial never triggered (Odin never writes B); F0-Odin REFUTED (correct behavior writes B from seq1 — Mac proves it); F0-Mac CONFIRMED (blit lands, alpha-masked, 1-frame-lag pipeline visible end to end); F4 refuted-outside-A (vpage diff confined to B; zero stray on either side); F1/F2/F3 all predict Odin-B==load — UNSPLIT by this wall (all consistent; G10 `passes=2` proves CPU-side submit of both passes on Odin, not GPU execution) |
| verdict | **Rule 4: the A→B composite writes from composite#1 onward do not land in B on Odin. The fault is downstream of draw submission (passes=2 both sides) and upstream of sampling (G32+ positive controls) — i.e., in draw execution / write-back / texture-visibility on Adreno (F1/F2/F3).** |

### 3i. Scanouts (10+10 pulled/written — G31-E1 applied on the Odin leg)

Odin explicit pull list (12 files + logcat; each named, zero globs):
`g38-run-stdout/stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0..7.ppm`, `g13-dump.gs.g8-first/last.ppm` (all
688,143 B, pulled as `odin-*`). All 13 pulls individually confirmed
(`1 file pulled, 0 skipped`). Cleanup ran as its OWN verified step
AFTER pull verification (`rm -rf` + `ls` → `mg/` only, exit 0). Mac
PPMs written alongside the dump copy (10 × 688,143 B).

| side | file shas |
| --- | --- |
| Odin 10/10 | `99418f1b…` UNANIMOUS (black — recovers what G31-E1 lost; == G29 blacks) |
| Mac vsync0 + first | `99418f1b…` (black — B==load at seq8 ✓) |
| Mac vsync1/2/3/4+5/6+7+last | `7e9daa21…` / `5d4ff853…` / `11370e59…` / `6aa54f3b…` / `bc5ca6de…` (content — equalities track ladder/B-series ✓) |

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| Mac retry | NOT USED (M0 voided, M1 exit 0) | M0 was a non-recipe execution (voided with receipts §3d0), not a run failure; M1 exited 0 with the full loop + all controls + `Done!` |
| Odin retry | NOT USED | Brief permits bounded runs only — the run exited 0 with the full loop + 32 G31 lines + all controls + `Done!` |
| second shape | NOT USED | out of budget by the stop rule (split closed: rule 4 fired decisively) |
| lldb triage | NOT USED | zero new tombstone, both exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The SAME first composite pass observed on Mac and Odin at matched boundaries locates the FIRST differing input, rejection, write, or dependency in the A→B chain | **CONFIRMED as rule 4, decisively.** 16/16 CPU-alignment classes identical Mac vs Odin (FRAME/record/tex/flush/G10/G31-state — rule 1 never fired, §3f); A byte-exact ×16 (scene path agrees cross-GPU — rule 7 clean); B == load on BOTH at seq0/seq8 (rule 3's pre-registered non-discrimination confirmed empirically); then Mac ≠ load / Odin == load at ALL of seq1–7/9–15 with the FIRST difference at boundary 1 (pass 0, vsync #1, seq 1, phase 0): Mac-B `840cd308c91c4d8a`/699122/`d5530000…` (composite#1's alpha-masked blit of bright scene#0) vs Odin-B `eea04488c453e75b`/149721/`00000000…` (load — write missing, §3g–3h); vpage delta confined EXACTLY to pages 112..223; Mac scanouts black→content (1-frame-lag pipeline end to end) vs Odin 10/10 black (§3i). F0-Mac confirmed, F0-Odin refuted, F4 refuted-outside-A. Excision only, one Mac build, one Mac run (+1 voided non-run with receipts), one Odin run (G31 binary reused, zero rebuild); retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **a sub-vsync A→B
observation wall on Odin (B pre/post-composite-flush reads + flush
reason + draw-accept logging around boundary 1) — NOT adoption.**
Rationale: rule 4 localizes the fault to "composite#1+ draws submit
(passes=2) but their writes never land in B" with the correct function
proven to be an alpha-masked blit of the previous scene — yet F1
(rejected draw), F2 (unwritten B / write-back lost), and F3
(stale-read: composite samples load-A every seq, so its blit preserves
B) ALL predict Odin-B==load and are unsplit at vsync granularity.
Discriminator (observation-only, no injection — the lane stays
redirected): B bytes immediately pre-T2 (== B of seq N−1 expected),
immediately post-T2 composite flush, and post-T3 scene flush, plus the
logged flush reason (FBPointer vs TextureHazard, §2b) and a draw-accept
count for the 17 prims — at boundary 1 first (span packets
#511..#1021, phase 0), where Mac proves the write should land.
F1 predicts post-T2 B == pre-T2 B with draws rejected/dropped; F2
predicts draws accepted but post-T2 B == pre-T2 B; F3 predicts draws
accepted AND post-T2 B == blit-of-load (== load — needs the input-side
read to split from F2: sample scene#0's bytes through the composite's
own texture path). Queued behind it (not this action): G26+G28 adoption
(separate G39 brief — explicitly OUT here); the Adreno filing — STILL
OPEN regardless (content upgrades again: "composite render-pass writes
don't land in FBP112 on Adreno while scene writes land byte-exact and
sampling is proven exact — draw execution / write-back /
texture-visibility, with a Mac reference"); G18-hunk fix adoption
(still queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture set + G28 writer-fix hunk compiled into BOTH binaries (guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH 5/5) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G37 shrunken-tag hunk | EXCISED from the worktree by this brief's edit (diff text survives committed in `local/research/G37/` — lossless) |
| G38 additions | ZERO source hunks (excision only) + session files: `g38-packets.py` + `g38-excise.py` + `g38-build-mac.sh` + `g38-run-mac.sh` + `g38-run-odin.sh` + `g38-score.py` (G38-original, text, mirrored) |
| NDK r30 / MoltenVK 1.4.2 / vulkan-headers | build + run use (Apache-2.0); no runtimes staged (non-sanitizer binaries) |
| logcat/stderr/scanouts | run receipts of our own binaries in SSD `ps2x-g38/` ONLY (not in git) + share-tier mirror; no PII |
| host analysis | `/tmp/g38-*.py` + `/tmp/g38-*.sh` + `/tmp/g38-build-mac.log` (session-only; dump layout from `dump/gs_dump_parser.cpp` + `gs_interface.cpp::gif_transfer`, validated by pin re-derivation + EOF_SYNC) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (5/5)
grep -h 'G10: pass|G11: record|G31: state' $SSD/ps2x-g31/g31-logcat.txt    # §2c (per-vsync structure)
sed -n '270,340p' $SSD/parallel-gs-g7/gs/gs_interface.cpp                 # §2c (G11 record site)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs (PASS1 11:32 + PASS2 11:40)        # 154d9d85… x2 (separated)
shasum -a 256 <g31-binary> (PASS1 + PASS2) ; xxd -l 4                     # c91719a0… x2 + ELF
du -sk <ps2x-g7..g37 + 19 build dirs> ; df -h / $SSD                     # §0 (pre 11:32:26 + post 11:51)
python3 /tmp/g38-packets.py $SSD/ps2x-g13/g13-dump.gs                     # §2b (4601 pkts, span-0 FRAME census)
python3 /tmp/g38-excise.py --dry ; python3 /tmp/g38-excise.py             # §3b (DRY-OK; -56, 104 closes)
VULKAN_SDK=/opt/homebrew cmake -S <clone> -B $SSD/parallel-gs-g38-mac-build -G Ninja  # §3c exit 0
cmake --build <g38-mac-build> --target parallel-gs-replayer -j2          # §3c exit 0 [458/458]
shasum -a 256 <mac-binary> ; xxd -l 4 ; strings grep 0/0/2/4/2/2/2/4/2/2/2/4/2/3/0  # 321e8582… + Mach-O
cp $SSD/ps2x-g13/g13-dump.gs $SSD/ps2x-g38/g38-dump.gs ; shasum           # 154d9d85… (dump copy)
VK_ICD_FILENAMES=... ./parallel-gs-replayer <dump> --iterations 2 --disable-sampler-feedback  # M0 exit 1/0B (no DYLD)
VK_ICD_FILENAMES=... DYLD_LIBRARY_PATH=/opt/homebrew/lib PGS_SKIP_COMPILATION_TASKS=1 <M1 same>  # M1 exit 0 (§3d0)
python3 /tmp/g38-score.py                                                 # §3f–3h (rule 4 @ seq=1)
shasum -a 256 $SSD/ps2x-g38/*.ppm                                         # §3i (Odin black x10; Mac black+content)
rm -f $SSD/ps2x-g38/._* ; du -sk $SSD/ps2x-g38                            # 35840 PASS
cp <28 receipts> /Volumes/share/ssx3/ps2x-g38/ ; shasum -c                # mirror ALL OK
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g38/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g38 && mkdir -p /data/local/tmp/g38'
push <dump> $G38DIR/g13-dump.gs ; push <g31-binary> $G38DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G38DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G38DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g38-run-stdout.txt 2> g38-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (probe fired)
logcat -d -s Granite:V > $SSD/ps2x-g38/g38-odin-logcat.txt                # 2360 lines
pull $G38DIR/g38-run-stderr.txt $SSD/ps2x-g38/odin-g38-run-stderr.txt (0 B) ; pull stdout (0 B)
pull $G38DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g38/odin-*.ppm  # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G38DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # c91719a0… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g38 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. F1 vs F2 vs F3 (rejected draw vs unwritten B vs stale-read) is
   UNSPLIT — queued as the §4 next action (sub-vsync observation wall
   at boundary 1 with flush-reason + draw-accept logging). This brief
   proves the writes are missing from composite#1 onward, not which
   leg drops them.
2. The composite flush reason (FBPointer vs TextureHazard,
   `check_frame_buffer_state` vs feedback path) is unlogged —
   content-neutral for the boundary match; the next wall logs it.
3. The G10 pass-0-vsync-#5 `img` delta (327680 Mac vs 0 Odin) is
   tabled as allocator-size informational (pre-registered note d) —
   unjudged, content-neutral (all counters + all bytes it could affect
   match elsewhere).
4. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the Mac leg is this brief's oracle and the
   cross-side FNV/bytes/scanout comparison closed without it).
5. M0's void rests on read-only diagnosis + the committed G7 env
   receipt — the silent-loader mechanism is proven by source, not by a
   re-run without the env (a second non-recipe run would be waste, not
   evidence).
6. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — both binaries intact at every gate).
7. G26+G28 adoption is queued, not done (separate G39 brief —
   explicitly OUT here; no port, no upstream contact).
8. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
9. The `? third_party/spirv-tools` untracked Granite entry is tabled
   content-neutral (pre-existing; untouched).
10. SSD free 126→119 Gi vs ~3.8 GB accounted new-dir growth: remainder
    is filesystem accounting (all old dirs byte-identical) — tabled,
    no action.
11. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget spent as tabled (M0 voided + M1 + O1).
12. Build warnings were observed via full-log grep (pre-existing
    classes); zero warnings point at hunk lines. The configure-log
    `--`-prefixed find-note lines were not retained (exit 0,
    `Configuring done` recorded).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g38/` (28 files:
  `g38-dump.gs` 11,537,377 B `154d9d85…`, `g38-mac-stderr.txt` 2349
  lines incl. 16 `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` +
  10 `G29: ladder` + 1 `G29: vram`, `g38-mac-stdout.txt` 0 B,
  `g38-m0-mac-*` 0-B pair, `g38-odin-logcat.txt` 2360 lines (same
  classes), `odin-g38-run-*` 0-B pair, 10 Mac PPMs × 688,143 B
  (black×2 + content×8), 10 Odin PPMs × 688,143 B (black `99418f1b…`
  unanimous)) + `parallel-gs-g38-mac-build/` (binary 51,898,120 B
  `321e8582…` Mach-O, intact at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g37/` + G7/G14/
  G15/G16/G18/G20/G22/G24/G26/G27/G28/G29/G30/G31/G32/G33/G34/G35/G36/
  G37 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G26 + G29 + G30 +
  G31 hunks uncommitted, G37 excised; Granite `16e7395f…` + G20-capture
  set + G28 hunk, all uncommitted — ZERO commits anywhere).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g38/` (28/28 files,
  `shasum -c` ALL OK).
- Session-only: `/tmp/g38-*.py` (packets/excise/score),
  `/tmp/g38-*.sh` (build-mac/run-mac/run-odin), `/tmp/g38-build-mac.log`,
  `/tmp/g38-score-out.txt`, `/tmp/g38-m-g10.txt`, `/tmp/g38-o-g10.txt`.
- Commits: ssx3 `local/research/G38/` `[G38]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G38 report ends here. Task-1 statics pinned the first
composite pass to packet #0 (FRAME_1 via PACKED A+D — G30 gap 3
closed), tabled 16 matched boundaries with the F0/fault predictions +
8-rule matrix incl. the seq0 non-discrimination caveat; excision only
+ ONE Mac build exit 0 + ONE Mac run exit 0 + ONE Odin run exit 0 (G31
binary reused, zero rebuild) with 16/16 CPU-alignment identical and A
byte-exact ×16 shows B == load on BOTH at seq0/seq8 then Mac ≠ load /
Odin == load from seq1: FIRST DIFFERENCE at boundary 1
(Mac `840cd308…`/699122 vs Odin `eea04488…`/149721 load) with the
vpage delta confined exactly to pages 112..223 — F0-Mac confirmed
(alpha-masked blit), F0-Odin refuted, F4 refuted-outside-A. Next wall
is the sub-vsync F1/F2/F3 split, not adoption; filing still open
(M0 voided with receipts; G31-E1 applied: explicit pull list, separate
cleanup).

Outcome: rule 4 — the A→B composite writes from composite#1 onward do
not land in B on Odin (first missing write at boundary 1: pass 0,
vsync #1, seq 1, phase 0). No tuning loop was entered: excision only,
one Mac build, one Mac run (+1 voided non-run), one Odin run. Retry
not used (both exit 0); lldb not used (zero new tombstone — nothing
to triage).
