# G33 report — H1-vs-H2 write-back control: VOID (stale-correct ≡ cleared), write-back integrity proven (Odin)

Brief: G33 (this turn) — executes G32 §4's ONE next action ONLY: the
write-back control (same sync structure, stale bytes re-written —
splits H1 ordering/coherency from H2 content-dependent fault). Tables +
hypothesis + next-action recommendation, no verdicts beyond the
hypothesis. Time box 6 h (used ~1.35 h — measured walls 21:06:08→22:09:43
EDT prior session Task 1 + staging, 07:22→07:38 EDT resume Task 2; task
start → commit). Read first per the brief: `local/research/G32/
REPORT.md` (all of it: the sampler reads EXACTLY under host-committed
pattern (10/10 ladder == expected FNV, 10/10 scanouts byte-identical to
the model); G32 changed TWO things vs G31 (content + sync), so the
defect reframes to ordering/coherency (H1) vs content-dependent fault
(H2)). No upstream contact of any kind (standing no-upstream order —
local hunks only, filing stays local).

Machine: same as G8–G32 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g33/`
ONLY; removed at end (`mg/` only).

Headline result: **the briefed H1/H2 discriminator is VOID — and the
void was proven, not assumed.** (1) Task 1 statics tabled the W1
read→temp→write→commit shape with barrier parity, pre-registered H2
scalars, and a six-row matrix. (2) The Task-2 predictor (rebuilt after
the host restart wiped `/tmp`) censused stale region B: **0/229376
words have nonzero RGB** (all 149721 nonzero bytes sit in alpha
position) — so stale-correct renders BYTE-IDENTICAL to cleared
(ladder `aa2fa32572450383`/nz=229376, PPM sha `99418f1b…` ==
all 10 G29 blacks, byte-compared). The model chain is doubly validated:
G32-pattern self-check reproduces the committed `dfe2b651…` +
`9dd120bc…` scalars exactly, and the H1 render matches G29's on-device
black. H1 and H2 predict the same bytes; no H1/H2 verdict is possible
from this control. (3) ONE hunk (pre-`renderer.vsync` write-back +
`G33: writeback` receipt, +51/−0, G32's +30 excised in the same edit),
ONE build (exit 0 `[458/458]`, full identity), verify-then-push with NO
gap, ONE run: **exit 0**, 16/16 `G33: writeback` (temp == stale ×16) +
16/16 `G31: state` + 16/16 `G31: bytes` (B == stale ×16, full lines
byte-identical to G31) + 512 `G30: vpage` (512/512 == G31: write-back
changed ZERO bytes) + 10 `G29: ladder` (cleared ×10) + 1 `G29: vram`,
ZERO new tombstone, 10/10 scanouts black-exact by explicit list. The run
proves write-back integrity (the commit path works, content-neutral) and
rules out both-refuted (no non-black output): the void verdict is
empirical. The ONE next action is a tagged write-back (same W1 sync, a
sparse nonzero-RGB tag OR-masked into the temp→B copy): H1 predicts the
exact tag render, H2 predicts cleared — that splits.

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g33-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g33/` (retrieval: logcat + stdout + stderr + 10 PPMs, explicit list) | 50 MB | 13 files, 25,600 KiB allocated PASS |
| SSD `ps2x-g10..g32` + G14/G15/G16/G18/G20/G22/G24/G26/G27/G28/G29/G30/G31/G32 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (snapshot 07:23:03; post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (write-back + retained dumps) | ONE hunk in `gs/gs_interface.cpp` (+51/−0 G33, G32 +30 excised same edit, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 + G31 hunks untouched, HUNK_MATCH re-verified); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g33-*` ~1.5 MB (5 rebuilt scripts + stub + build log + predict/score + 2 expected PPMs + diff blocks, session-only); G33 evidence dir text-only PASS |
| device | `/data/local/tmp/g33/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Re-writing the SAME stale bytes through G32's sync structure (map-read B → temp → map-write back → commit, per vsync) splits H1 from H2: H1 (ordering/coherency — the commit/barrier was G32's fix) predicts output goes stale-correct (ladder == stale-model FNV, scanouts == stale-model image); H2 (content-dependent fault — the pattern content was the fix) predicts output stays cleared (ladder == `aa2fa32572450383` ×10, scanouts byte-identical black) |
| observable signal | design tables (§2: shape + barrier parity + named bytes + matrix + hunk spec) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G33: writeback` (temp == stale) + 16 `G31: state` + 16 `G31: bytes` (B == stale) + 512 `G30: vpage` (512/512 == G31) + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + 10 scanouts scored (exact-vs-model / exact-vs-black / stale-set census) + verdict (§4) |
| alternatives | H1-STALE-CORRECT (stale source ×16 + model-exact output ×10); H2-STILL-CLEARED (stale source ×16 + cleared output ×10); OTHER-writeback (temp or B ≠ stale — write-back path failed, stop, no H1/H2 verdict); OTHER-mixed (stale source + neither-cleared-nor-model output — partial/torn coherency, triage by per-pixel deltas); OTHER-fixed (stale source + uniform single stale word — addressing-fixed degenerate) |
| stop condition | ONE hunk max (write-back + retained dumps); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: VOID-BLACK — the predictor censused stale B at 0/229376
nonzero-RGB words, so H1-STALE-CORRECT and H2-STILL-CLEARED predict
identical bytes (§2c2); the run then confirmed black output with full
write-back integrity (16/16 temp == stale, 512/512 vpage == G31) and no
both-refuted signal (§3h). No H1/H2 verdict is possible from this
control — by byte census, not by assumption. No tuning loop was
entered: one hunk, one build, one device run. Retry not used (exit 0);
lldb not used (zero new tombstone — nothing to triage).

## 2. Task 1 — static design (no device runs)

### 2a. Pin verification (pre-work — G32 end state reproduced, ZERO edits)

Prior session (21:07–21:16 EDT) + resume re-verification (07:23 EDT,
post-SSD-remount — every pin re-checked, `/tmp` staging rebuilt):

| item | prior observed | resume re-verify |
| --- | --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) | SAME (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G32 end state exactly | SAME — G32 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 134 (39 + G31's 65 + G32's 30 — arithmetic closes), gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 — G32 end state + nothing | SAME (gs_interface 134 pre-hunk; post-hunk §3b) |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) | HUNK_MATCH (re-verified pre- AND post-hunk) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` (pre-existing) | ×1 (same) |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (pre-existing; Granite HEAD `16e7395f…` == pin) | ×1; Granite HEAD `16e7395f…` == pin (same) |
| G29 ladder + G30 vpage + G31 state + G32 inject | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 + `G31: state` ×1 + `G31: bytes` ×2 + `G32: inject` ×2 markers) | SAME counts |
| G31 binary (re-sha, standing hygiene) | 265,851,416 B, sha `c91719a0…` FULL-match, magic `7f45 4c46` ELF — **INTACT** | SAME — **INTACT** |
| G28 binary (re-sha) | 265,841,104 B, sha `450471e2…` FULL-match, magic `7f45 4c46` ELF — **INTACT** | SAME — **INTACT** |
| G32 binary (re-sha + census) | 265,852,240 B, sha `feb485f0…` (≠ build `35288fd0…`), magic `0000`, **0 nonzero bytes — 10th zero-damage recurrence COMPLETED** | 265,852,240 B, sha `35288fd0…` FULL-match build sha, magic `7f45 4c46` ELF, 222,594,188 nonzero — **reads INTACT post-remount** (observation tabled §7.8; run validity unaffected either way — receipts in `ps2x-g32/`) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match | SAME full-match |
| dirs 0-growth | pre-run `du -sk` snapshot 21:07:19 (ps2x-g10 43008 … g32 25600; builds 4480000/4816896/4577280/4482048…/4817920 KiB; `/` 87%, SSD 93%) | fresh snapshot 07:23:03 — EVERY value identical; post-run re-verified §0 (every value identical) |
| recipe | NDK r30 (`/opt/homebrew/share/android-ndk`, toolchain file present); cmake + ninja on PATH; G22/G26/G28/G29/G30/G31/G32 non-sanitizer flags | SAME (toolchain file + cmake + ninja + clang++ + python3 + adb all present) |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 28 G free | `622c49b1`, Odin3, Android 15; `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 29 G free |
| session survivors | `/tmp/g30-load.py` … `/tmp/g32-expected*.ppm` all present (same boot) — host toolchain intact | HOST RESTARTED: `/tmp` wiped — all 5 `g33-*` session scripts rebuilt from committed evidence + clone sources (§2g); dump/clone/builds SSD-resident, intact |
| SSD-DEAD event | ~21:09 EDT: `ls /Volumes/Extreme SSD` → ENOENT; disk4 gone; `AppleUSBXHCICommandRing::executeCommand timeout` + persistent enumeration failures; no backup on `/Volumes/share`; `/Users/bradrichardson/dev/ps2xGS` is a different repo (harness — not the lane clone) | SSD back as disk6 (ExFAT, 93%); all pins above reproduce |

### 2b. Write-back shape (tabled — exactly one picked) + barrier parity

Per-vsync pre-`renderer.vsync` sequence, G32 vs candidates (region B =
pages 112..223 = bytes [917504, 1835008), base/n `112*8192`/`112*8192`):

| shape | sequence | verdict |
| --- | --- | --- |
| G32 (reference) | `map_vram_write(B)` [get_host_write_timeline → flush_submit? → wait_timeline → begin_host_vram_access] + CPU pattern fill + `end_vram_write(B)` [end_host_write_access + commit_host_write(B rect)] + `G32: inject` receipt | REFERENCE — content=pattern, sync=commit-per-vsync |
| W1. read→temp→write→commit (CHOSEN) | `map_vram_read(B)` [get_host_read_timeline → flush? → wait → begin] + CPU copy B→static temp + `map_vram_write(B)` [identical leg to G32's] + CPU copy temp→B + `end_vram_write(B)` [identical commit, same rect] + `G33: writeback` FNV receipt (temp FNV/nz, truncated basis) | **CHOSEN** — the brief's prescribed discriminator verbatim; read completes into temp BEFORE the write map is taken, so src/dst aliasing (both `begin_host_vram_access()+base`) is harmless; temp FNV proves WHAT was re-written at write time (closes read-leg vs write-leg triage in the OTHER branch) |
| W2. in-place same-value store | single `map_vram_write(B)` + `dst[i]=dst[i]` self-copy + `end_vram_write(B)` | REJECTED — deviates from the prescribed discriminator; read-through-write-mapping has unproven coherency semantics vs the G29/G30/G31-proven `map_vram_read` path; no temp to checksum (can't name the re-written bytes independently of the post-sample line) |
| W3. dual-map word-by-word | `map_vram_read(B)`→R + `map_vram_write(B)`→W, `W[i]=R[i]`, `end_vram_write(B)` (no temp) | REJECTED — behaviorally W1 minus the temp checksum; R/W alias the same mapping, so the "read" leg is cosmetic and the temp-FNV triage is lost |

Barrier parity argument (why W1 isolates the commit):

| link | evidence |
| --- | --- |
| write leg call-identical | `map_vram_write(917504, 917504)` + `end_vram_write(917504, 917504)` — same calls, same base/n/rect, same position (immediately pre-`renderer.vsync`) as G32 (`gs_interface.cpp:4228–4271` impl, `:4754` call site post-hunk) |
| commit marks the same pages | `end_vram_write` → `tracker.commit_host_write(page_rect{112,112})` marks pages 112..223 host-newest exactly as in G32, so the vsync's sample submission takes the same barrier |
| extra read leg is content-neutral class | `map_vram_read` performs flush+wait+begin but NO commit (`:4274–4299` — no `end_vram_read` exists); identical class to G31's retained post-call read, proven content-neutral ×16 in G31 (null+stale preserved) and G32 (pattern preserved) |
| begin-after-begin in proven envelope | G32 already exercised un-ended read-begin followed by next pre-call write-begin across every vsync boundary (16/16 clean); W1's read-begin→write-begin within the pre-call block is the same nesting with no new API state |
| content held at stale | temp→B copy writes back the bytes just read; on-device proof is the 16 temp FNVs (== stale at write time) + 16 G31-B lines (== stale at sample time) + 512 vpage (== G31: ZERO bytes changed) |
| delta vs G32, total | +1 read leg (neutral class) + content stale-instead-of-pattern; everything else (site, regs, knobs, loop, dumps) identical — any output change vs G31 isolates to the commit/barrier |

### 2c. Expected outputs under H1 vs H2 (named bytes)

Stale-correct means WHAT bytes: region-B stale load bytes (FNV
`eea04488c453e75b`, nz=149721, head `00000000…` — G31 §2d, re-asserted by
`g33-predict.py`) sampled through the G32-validated exact sampler: each
output pixel (x,y) = RGB of
`vram32[swizzle_PS2(x, y, base_ptr=112*32, stride=8, PSM=1,
VRAM_MASK=0x3FFFFF)]` with alpha forced `0x80` (PSMCT24 32-bit path),
coord=pixel (progressive 1:1), 512×448, y-down as modeled. The H1
expected image is the swizzle-model render of THOSE bytes (not echo, not
constant); the H1 ladder FNV is the truncated-basis FNV over that image's
RGBA bytes (α=0x80), computed by `/tmp/g33-predict.py` (same code path
as G32's predictor, stale bytes substituted; asserts load-full ==
`6002946899e9cae0`/1184729, B == `eea04488…`/149721, swizzle bijective
229376/229376 in-window).

| observable | H1 (ordering/coherency) | H2 (content-dependent fault) |
| --- | --- | --- |
| 16 `G33: writeback` temp FNV | `eea04488c453e75b` nz=149721, base/n=917504/917504 (premise — same both columns) | same |
| 16 `G31: bytes` B | `eea04488c453e75b` nz=149721 head=`00000000…` (premise — stale at sample time) | same |
| 16 `G31: bytes` full lines | byte-identical to G31's 16 (A untouched, B untouched) | same |
| 16 `G31: state` | all fields == G31 predictions (regs/knobs identical) | same |
| 512 `G30: vpage` | 512/512 == G31's vpage (write-back changed ZERO bytes — content-neutral proven on-device) | same |
| 1 `G29: vram` | `6002946899e9cae0`/1184729 (restart control) | same |
| 10 `G29: ladder` P1/P2/P3 | == H1 stale-model FNV/nz ×10 | == cleared `aa2fa32572450383` nz=229376 ×10 (G29/G30/G31 unanimity) |
| 10 scanouts | BYTE-IDENTICAL to `/tmp/g33-expected.ppm` | BYTE-IDENTICAL black (== G29 black, sha `99418f1b…`) |
| logcat | 2376 lines (G31's 2360 + 16 G33); `Total time per VBlank` inflated class (diagnostic cost of 16 extra map+copy+commit inside the timed region, §2e) | same shape |

### 2c2. VOID CORRECTION (predictor finding — pre-registered BEFORE the run)

The census the prior session deferred ("exact count from
`g33-predict.py`") collapses the table above: stale B holds
**0/229376 nonzero-RGB words** — every nonzero byte sits in alpha
position (top words `0x07000000`, `0x00000000`, …). The H1 render is
therefore uniform `(0,0,0,0x80)` — byte-identical to cleared:

| check | observed |
| --- | --- |
| stale-B word census | 0/229376 nonzero-RGB; 149721/229376 nonzero-alpha (== byte-nz 149721: each nonzero word contributes exactly 1 nonzero byte) |
| H1 stale-model ladder | fnv=`aa2fa32572450383` nz=229376 — EQUALS cleared |
| H1 expected PPM | sha `99418f1b1a94ed9f…` — byte-identical (`cmp`) to ALL 10 G29 black scanouts |
| G32-pattern self-check (same renderer) | pattern B fnv=`dfe2b6516a519f83`/915264 + model P1 fnv=`9dd120bc6b0df383`/915264 — both == committed G32 scalars EXACTLY (model chain validated against G32's on-device match) |
| swizzle audit | 229376/229376 sample addrs in-window, all distinct (bijective — the render covers all of B, no subset artifact) |
| consequence | H1-STALE-CORRECT ≡ H2-STILL-CLEARED observationally; the briefed split is VOID. The run's remaining power: write-back integrity proof (temp==stale ×16, vpage 512/512==G31) + BOTH-REFUTED detector (any non-black output refutes H1+H2 jointly) |

The §2c TRAP ("some output pixels WILL be black") understated: ALL of
them are black under H1. The A==ladder-FNV-in-load trap stands as noted
(G31) and is now joined by B-renders-to-cleared.

### 2d. Decision matrix (pre-registered; VOID-aware revision)

Original six-row matrix (as briefed) + the revised reading after §2c2:

| G33 temp + B (16+16) | ladder P1 (10) + scanouts | reading |
| --- | --- | --- |
| temp == stale ×16, B == stale ×16 | == H1 stale-model FNV ×10, scanouts model-exact | H1 — ordering/coherency (ORIGINAL row; §2c2 proves this observable == the H2 row — VOID) |
| temp == stale ×16, B == stale ×16 | == cleared `aa2fa325…` ×10, scanouts black-exact | H2 — content-dependent fault (ORIGINAL row; == H1 row — VOID) |
| temp == stale ×16, B == stale ×16 | black-exact ×10 (== BOTH rows above) | **VOID-BLACK** (REVISED verdict — no H1/H2 split possible; write-back integrity still proven) |
| temp == stale ×16, B == stale ×16 | non-black (neither model nor cleared), any pattern | **BOTH-REFUTED** (REVISED — H1+H2 jointly refuted; new physics; per-pixel deltas name it) |
| temp ≠ stale (any) OR B ≠ stale (any) | — | OTHER-writeback — write-back path failed → STOP, no H1/H2 reading; temp FNV vs G31-B splits read-leg (temp≠stale, B==stale: read returned bad bytes) from write-leg (temp==stale, B≠stale: writeback wrote bad bytes) from transient-writer (both≠stale but equal: something else moved B) |

The original OTHER-mixed / OTHER-fixed / OTHER-partial rows are
subsumed by BOTH-REFUTED (any non-black output with stale source
refutes both hypotheses jointly — the fault would be neither
ordering-fixed-by-commit nor content-fixed-by-pattern).

### 2e. Hunk spec (the ONE hunk, named)

ONE hunk: **G33 pre-`renderer.vsync` stale write-back** (map-read B →
static temp + temp FNV → map-write temp back → commit + `G33: writeback`
FNV receipt), with **G32's pattern-injection block excised in the same
edit** (its diff survives committed in G32 evidence — excision is
lossless and REQUIRED: live pattern content would confound the control).

| item | spec → actual |
| --- | --- |
| site | `GSInterface::vsync`, immediately BEFORE `auto result = renderer.vsync(…)` — the same anchor G32 used (anchor `"\tauto result = renderer.vsync(priv_registers, info,\n"`, unique ×1) → CONFIRMED ×1 (`:4754` pre-hunk) |
| shape | ONE contiguous insertion (`{…}` block at 1-tab scope); G32's +30 block excised first (derived from the committed `g32-inject.diff` `+` lines — no transcription); net vs G31 worktree: write-back only → +51/−0 contiguous, single @@; worktree `gs_interface.cpp` diff 155 = 134 − 30 + 51 (arithmetic closes) |
| temp | `static uint32_t g33_temp[(112*8192)/4]` (function-static, 917504 B BSS; fully rewritten each call before use; vsync is serial — no reentrancy) → as spec'd |
| receipt | `G33: writeback base=%u n=%u fnv=%016llx nz=%u.` (temp FNV/nz, truncated basis G29-E1) + `read-map failed` / `write-map failed` fallbacks (3 `G33: writeback` markers total) → as spec'd |
| applier | `/tmp/g33-hunk.py`: asserts G32-block ×1 + immediately-pre-anchor + G33-absent + anchor ×1; single file write; post-asserts G32-gone + G33 ×3 + G31 neighbors intact (`G31: state` ×1, `G31: bytes` ×2) → DRY-OK then APPLIED; post: G32 ×0, G33 ×3, G31 ×1/×2, G22 HUNK_MATCH |
| syntax | hunk text extracted from the applier compiles clean in a stub TU (`clang++ -std=c++17 -Wall -Wextra -fsyntax-only` — STUB_SYNTAX_OK; 2 unused-set warnings are stub artifacts of no-op LOGI) → as spec'd |
| costs (tabled up front) | +16 logcat lines (~2 KB: longer receipt than G32's); runs inside the timed region (expect inflated ms/VBlank — diagnostic cost, not a signal); 16 extra HostAccess read+write+commit cycles + 2×917504 B CPU copies/vsync (content-neutral by construction — temp→B is identity) → 2376 lines; 12.064 ms/VBlank (§3e) |
| retained | G22 + G26 + G28 + G29 ladder + G30 vpage + G31 state/bytes all untouched (HUNK_MATCH + marker counts re-verified post-hunk) → all intact |

### 2f. Knob matrix (flag SET — the ONLY delta vs G32's run is G33's hunk-for-hunk swap)

| knob / flag | G32 setting | G33 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G32 = G31 + pattern-injection hunk | G33 = G31 + write-back hunk (G32 block excised) | the single delta (content stale, sync same) |

### 2g. Resume staging note (host restart rebuilt `/tmp`)

The prior session's 5 scripts were session-only and wiped by the host
restart. All were rebuilt from committed evidence + clone sources
before the run: `g33-predict.py` (dump layout from
`dump/gs_dump_parser.cpp::restart()` + G30 §2b; swizzle port
validated via the G32-pattern self-check §2c2);
`g33-hunk.py` (G32 block derived from committed `g32-inject.diff`;
DRY-OK + STUB_SYNTAX_OK before apply); `g33-build.sh` / `g33-run.sh`
(mirrored from committed `g32-*.sh` with g33 paths); `g33-score.py`
(VOID-aware matrix). Rebuild validity is proven by the receipts, not
asserted: predictor asserts hit every committed scalar (load
`6002946899e9cae0`/1184729, B `eea04488…`/149721, pattern
`dfe2b651…`/915264, P1 `9dd120bc…`/915264, black `99418f1b…`).

## 3. Task 2 — ONE write-back control + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G32's run is the G33 hunk-for-hunk swap)

Same table as §2f (SET / UNSET / KEPT / ABSENT / hunk-for-hunk swap —
the single delta).

### 3b. Hunk record (ONE hunk, write-back + retained dumps)

`gs/gs_interface.cpp`, G32's +30 pattern block excised + ONE contiguous
+51/−0 insertion (new lines ~4723–4773) in `GSInterface::vsync()`
immediately BEFORE the `renderer.vsync` call: `map_vram_read(917504,
917504)` → CPU copy into `static uint32_t g33_temp[]` + truncated-basis
FNV/nz → `map_vram_write(917504, 917504)` → CPU copy temp back →
`end_vram_write` (commit) + `G33: writeback` receipt (`read-map failed` /
`write-map failed` fallbacks). Regs/loop/circuit untouched. Full diff
text in `g33-writeback.diff` beside this report (mechanically extracted
with `-U1`: 51+/0-, single @@ block). G22 HUNK_MATCH + G26 block + G28
Granite hunk + G29 ladder + G30 vpage + G31 state all untouched; zero
commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G32 recipe, `g33-build.sh` mirrored): exit 0
(`Configuring done (7.4s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`,
07:26:53→07:30:59).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp` + cmake-deprecation noise); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,853,048 B (+808 vs G32 — the hunk delta; NEW size expected) |
| sha (build-time) | `7e0ea8031c6a581fb20b3107b968bcb9a77d3f1c22192621a94aec1b7ee87b00` (NEW) |
| build-id | `8a89ed2c80eb9fc230404e556203e533930de98e` (distinct from G32 `eb6bfa53…`) |
| plumbing presence | `G33: writeback` ×3, `G32: inject` ×0, `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 07:31:33 | `7e0ea803…` (binary) + `154d9d85…` (dump) FULL-match build sha |
| device stage | 07:31:33–37 | `rm -rf` + `mkdir` + push dump (0.011 s) + push binary (2.260 s) into `/data/local/tmp/g33/` ONLY |
| on-device sha match | 07:31:37 | `154d9d85…` + `7e0ea803…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 07:31 | `logcat -c` then run — no idle window |
| on-device post-run re-sha | 07:31 | `7e0ea803…` FULL-match — intact |
| report-time re-sha | 07:32:10 | `7e0ea803…` FULL-match + ELF magic — **binary INTACT, no zero-damage recurrence this window** |

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g33/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g33/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g33-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790076701→1790076702; logcat 07:31:41.475→07:31:42.389) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G32) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G33: writeback` + 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 map-fails of any kind |
| logcat | 2376 lines (== G31's 2360 + 16 G33 exactly): init + 18 `Running frame` + 18 G10 + `Total time per VBlank: 12.064 ms` (same inflated class as G31's 9.194 / G32's 8.871 — diagnostic cost of 16 extra map+copy+commit inside the timed region, §2e) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical in G29–G32 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each) ALL pulled by explicit list (§3i); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (writeback + ladder + vpage + load line — continuity with G29–G32)

| receipt | observed |
| --- | --- |
| 16 `G33: writeback` | ALL `base=917504 n=917504 fnv=eea04488c453e75b nz=149721`, 0 map-fails — the bytes re-written were stale at write time, on every vsync, both passes |
| 10 `G29: ladder` | ALL P1=P2=P3=FNV `aa2fa32572450383`, nz=229376 == cleared (== H1-model FNV per §2c2 — VOID, not H2) |
| 512 `G30: vpage` (all pass=1, pages 0..511) | timestamp-stripped lines BYTE-IDENTICAL to G31's vpage 512/512 — write-back perturbed NOTHING (content-neutral proven on-device, including all 112 B pages) |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz=1,184,729 == host load FNV — trailing-restart mechanism reproduced on-device a fifth time (restart control passes) |
| 16 A-lines | BYTE-IDENTICAL to G31's 16 A-lines (scene path untouched — non-perturbation proven beyond determinism; §3g) |

### 3g. Writeback + state + bytes verdicts (stale source at every write and sample time)

Writeback lines (16/16 full receipts, 0 fallbacks):

| field | predicted | observed |
| --- | --- | --- |
| base / n | 917504 / 917504 ×16 | **16/16 EXACT** |
| temp FNV / nz | `eea04488c453e75b` / 149721 ×16 | **16/16 EXACT** — re-written bytes were stale at write time |

State lines (16/16 match G31 predictions — every field, every seq;
regs/knobs identical by construction; full lines byte-identical to G31's
16/16):

| field | predicted | observed |
| --- | --- | --- |
| seq | 0..15 | 0..15 (8/pass) |
| EN1 / EN2 | 1 / 0 | 1 / 0 ×16 |
| DISPFB1 | 112/8/1/0/0 | 112/8/1/0/0 ×16 |
| DSP1 | 2560/447/4/0/641/50 | 2560/447/4/0/641/50 ×16 |
| SM | 2/1/0 | 2/1/0 ×16 |
| nprom / hack | 0 / 0 | 0 / 0 ×16 (promotion still off on-device) |
| p1null / p1 / p2null | 1 / 0x0x0x0 / 1 | 1 / 0x0x0x0 / 1 ×16 (`sample_quad[0]` VRAM path on every vsync) |
| phase | 1,0,1,0… per pass | 1,0,1,0,1,0,1,0 ×2 passes |

Bytes lines (16/16 fire, 0 map-fails; full lines byte-identical to G31's
16/16):

| region | predicted | observed |
| --- | --- | --- |
| B (the discriminator) | stale `eea04488c453e75b` nz=149721 head=`00000000…` ×16 | **16/16 EXACT match** — stale source at EVERY sample time (OTHER-writeback never triggered) |
| A (live control) | ≠ load, varying, pass-repeat 8/8 | 8/8 EXACT pass-repeat; all ≠ load; all 16 lines byte-identical to G31's A-lines |

### 3h. Split analysis (VOID-BLACK — the control cannot split H1/H2; write-back integrity proven)

| link | evidence |
| --- | --- |
| write-back path works | 16/16 temp == stale at write time + 16/16 B == stale at sample time + 512/512 vpage == G31 — the read leg reads stale, the write leg writes it back, the commit changes zero bytes (content-neutral, as constructed) |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0`) → `sample_quad[0]` + `buffers.gpu` on every vsync — same path as G31/G32 |
| source bytes at sample time | region B == stale load (16/16 `eea04488…`, 0/229376 nonzero-RGB words) — never cleared-as-content, never transient-written |
| circuit output | 10/10 ladder P1/P2/P3 == `aa2fa32572450383`/nz=229376; 10/10 scanouts byte-identical black (sha `99418f1b…`, §3i) — equals BOTH the H2 prediction AND the H1 stale-model (§2c2) |
| elimination | OTHER-writeback never triggered (path proven); BOTH-REFUTED never triggered (no non-black output — H1+H2 remain jointly alive); H1-vs-H2 UNSPLITTABLE by this control (identical predictions, proven by census + double-validated model) |
| verdict | **VOID-BLACK: the write-back ran with full integrity and the output is black — which H1 and H2 both predict.** The value delivered: (a) the commit path is proven to run content-neutrally per-vsync (16 commits, zero byte drift) — the prerequisite for ANY future commit-based control; (b) the void is empirical (a non-black outcome would have refuted both hypotheses jointly); (c) G31's cleared-from-stale observation stands with the commit exercised (output black WITH per-vsync host commit on the sampled pages — constrains H1's "commit fixes sampling" to "commit preserves black-on-black", uninformative but recorded) |

### 3i. Scanouts (10/10 pulled by explicit list — G31-E1 applied)

Explicit pull list (12 files + logcat; each named, zero globs):
`g33-run-stdout.txt`, `g33-run-stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0.ppm` … `g10-vsync7.ppm`,
`g13-dump.gs.g8-first.ppm`, `g13-dump.gs.g8-last.ppm` (all 688,143 B).
All 13 pulls individually confirmed (`1 file pulled, 0 skipped`).
Cleanup ran as its OWN verified step AFTER pull verification
(`rm -rf` + `ls` → `mg/` only, exit 0).

| file | sha256 | vs H1 model (= G29 black) |
| --- | --- | --- |
| 10/10 scanouts | `99418f1b1a94ed9ffcfadd6fc0b6573eca5275d6834a3d4cffb64da330233b34` (unanimous) | BYTE-IDENTICAL to `/tmp/g33-expected.ppm` AND to all 10 G29 blacks (same sha — 21-way unanimity incl. the host model) |

Pixel census (per file): uniform `(0,0,0)`; zero-RGB pixels 229376/229376.

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 16 G33 + 32 G31 lines + all controls + `Done!` |
| second shape | NOT USED | out of budget by the stop rule (VOID verdict is terminal for this control — the fix is a new discriminator, §4, not a second shape here) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Re-writing the SAME stale bytes through G32's sync structure splits H1 from H2 | **VOID — decisively.** Stale B holds 0/229376 nonzero-RGB words (§2c2 census), so the H1 stale-model render is byte-identical to the H2 cleared prediction (ladder `aa2fa32572450383`/nz=229376, PPM sha `99418f1b…` == all 10 G29 blacks; model chain double-validated via the G32-pattern self-check + G29-black identity). The run executed with full write-back integrity (16/16 temp == stale, 16/16 B == stale, 512/512 vpage == G31, exit 0, zero new tombstone) and produced black output — which both hypotheses predict. No H1/H2 verdict is possible from this control. OTHER-writeback and BOTH-REFUTED never triggered. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **a tagged write-back wall
(same W1 sync structure, stale bytes + a sparse nonzero-RGB tag) — NOT
adoption.** Rationale: the void comes from stale-correct ≡ cleared, so
the fix is a control whose H1 prediction differs from black while
keeping the W1 commit structure: in the temp→B copy, OR-mask a sparse
tag (e.g., one word per page forced to a nonzero-RGB tag word, or the
G32 echo formula applied to a sparse subset) + commit; the `G33:
writeback` receipt then checksums the TAGGED temp (proving what was
re-written) while G31-B verifies the tagged source at sample time.
Discriminator: H1 (ordering/coherency — the commit fixes sampling)
predicts the output renders the tag pattern EXACTLY (host-model FNV ≠
cleared, pre-registerable with this brief's validated renderer); H2
(content-dependent fault — G32's pattern content was the fix) predicts
output stays cleared (tag content is not the pattern). Queued behind it
(not this action): G26+G28 adoption once brightness is understood at
the sample level (UNCHANGED — the sampler is still proven exact only
under commit, G32); the Adreno filing — STILL OPEN regardless (content
upgrades again: "per-vsync host commit on the sampled pages preserves
black-on-black output from a zero-RGB stale source; H1/H2 split needs a
tagged control"); G18-hunk fix adoption (still queued); O1 writer
naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G32 pattern hunk | EXCISED from the worktree by this brief's edit (diff text survives committed in `local/research/G32/` — lossless) |
| G33 additions | the ONE write-back hunk (SSD clone worktree only) + session files: `g33-build.sh` + `g33-run.sh` + `g33-writeback.diff` (G33-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g33/` ONLY (not in git); no PII (`uid: shell`); all 10 PPMs pulled (shas + census in §3i) |
| host analysis | `/tmp/g33-*.py` + `/tmp/g33-*.sh` + `/tmp/g33-build.log` + `/tmp/g33-expected*.ppm` (session-only; rebuilt post-restart, §2g) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (prior + resume)
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (pre + post)
shasum -a 256 <g31-binary> ; xxd -l 16 <g31-binary>  # §2a INTACT (c91719a0…)
shasum -a 256 <g28-binary>                             # §2a INTACT (450471e2…)
shasum -a 256 <g32-binary> + python zero census        # §2a post-remount INTACT (35288fd0…)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g33 + 15 build dirs> ; df -h / $SSD           # §0 (pre 07:23:03 + post 07:32)
python3 /tmp/g33-predict.py $SSD/ps2x-g13/g13-dump.gs            # §2c2 (VOID census + H1 oracles + G32 self-check)
cmp /tmp/g33-expected.ppm $SSD/ps2x-g29/<each of 10 PPMs>        # §2c2 (H1 == G29 black x10)
python3 /tmp/g33-hunk.py --dry                              # §2e (DRY-OK: G32x1 pre-anchor, anchorx1)
clang++ -std=c++17 -Wall -Wextra -fsyntax-only /tmp/g33-stub.cpp  # §2e STUB_SYNTAX_OK
python3 /tmp/g33-hunk.py                                    # §3b (ONE single-write edit: -30/+51)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff -U1 | grep -c '^@@'  # hunk shape (155; single @@)
cmake -S <clone> -B $SSD/parallel-gs-g33-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g33-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g33-binary> (build, pre-push, post-run, report)  # 7e0ea803… x4 match (intact)
llvm-readelf --notes <g33-binary> ; strings grep 3/0/1/2/1/1/1/2/1/1/2/0 ; xxd -l 4  # 8a89ed2c… + ELF
python3 /tmp/g33-score.py                                       # §3f–3i (16/16 + 10/10 + 512 + BLACK x10 + VOID)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g33/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 29G)
shell 'rm -rf /data/local/tmp/g33 && mkdir -p /data/local/tmp/g33'
push <dump> $G33DIR/g13-dump.gs ; push <g33-binary> $G33DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G33DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G33DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g33-run-stdout.txt 2> g33-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (control fired)
logcat -d -s Granite:V > $SSD/ps2x-g33/g33-logcat.txt                # 2376 lines
pull $G33DIR/g33-run-stderr.txt $SSD/ps2x-g33/ (0 B) ; pull stdout (0 B)
pull $G33DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g33/   # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G33DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # 7e0ea803… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g33 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The H1-vs-H2 split (ordering/coherency vs content-dependent fault)
   is STILL open — the write-back control is void by byte census (§2c2);
   queued as the §4 next action (tagged write-back with the same sync
   structure). This brief proves write-back integrity + black output
   under per-vsync commit, not which delta (content vs sync) fixed
   G31's cleared output.
2. The H1 stale-model scalars ARE pre-registered (ladder
   `aa2fa32572450383`/nz=229376, expected-PPM sha `99418f1b…`,
   zero-RGB census 229376/229376) — they coincide with H2's, which is
   the void, not a gap in registration.
3. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the host swizzle model is this brief's oracle and
   matched byte-exactly, 21-way sha unanimity with G29 blacks).
4. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
5. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G33 binary intact at all four).
6. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness at the sample level per §4 — unchanged; no port, no
   upstream contact).
7. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
8. The G32 binary reads INTACT post-remount (`35288fd0…` FULL-match,
   222,594,188 nonzero) after reading fully zeroed pre-drop — tabled as
   an OBSERVATION only: the zero readings coincided with the dying USB
   link, so read-path artifact is now on the table alongside on-disk
   destruction; no verdict (forensics is out of scope; no lane data
   depended on the G32 binary bytes — all G32 receipts live in
   `ps2x-g32/`).
9. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
10. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
11. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes + cmake noise); zero
    warnings point at the hunk lines.
12. The `map_vram_read`-then-`map_vram_write` nesting had zero prior
    callers in this order within one pre-call block (first live use is
    this hunk); its correctness is proven empirically by temp==stale
    ×16 + B==stale ×16 + 512/512 vpage == G31 — not by a second
    independent writer.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g33/` (13 files:
  `g33-logcat.txt` 2376 lines incl. 16 `G33: writeback` + 16 `G31: state` +
  16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g33-run-stderr.txt` 0 B, `g33-run-stdout.txt` 0 B, 10 scanout PPMs
  688,143 B each sha `99418f1b…` unanimous) +
  `parallel-gs-g33-android-build/` (binary 265,853,048 B
  `7e0ea803…` BuildID `8a89ed2c…`, intact at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g32/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27/G28/G29/G30/G31/G32 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 + G33 hunks uncommitted (G32 excised);
  Granite `16e7395f…` + G20-capture set + G28 hunk, all uncommitted —
  ZERO commits anywhere).
- Session-only: `/tmp/g33-*.py` (hunk/predict/score),
  `/tmp/g33-*.sh` (build/run), `/tmp/g33-build.log`,
  `/tmp/g33-expected*.ppm` (host oracles, `99418f1b…`),
  `/tmp/g33-stub.cpp` (syntax stub).
- Commits: ssx3 `local/research/G33/` `[G33]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G33 report ends here. Task-1 statics tabled the W1
read→temp→write→commit shape with a call-identical write leg +
commit barrier-parity argument, pre-registered H2-exact scalars, and a
six-row decision matrix; the Task-2 predictor then censused stale B at
0/229376 nonzero-RGB words, proving stale-correct byte-identical to
cleared (H1-model ladder `aa2fa325…`, PPM sha `99418f1b…` == all 10 G29
blacks; G32-pattern self-check exact) and voiding the briefed split
BEFORE the run. ONE write-back hunk (+51/−0, G32 +30 excised same edit)
+ ONE build exit 0 + ONE run exit 0 with 16/16 stale-temp + 16/16
stale-B + 512/512 vpage==G31 proves write-back integrity with black
output (VOID-BLACK: both hypotheses predict it; both-refuted ruled
out). Next wall is the tagged write-back, not adoption; filing still
open (G31-E1 applied: explicit pull list, separate cleanup).

Outcome: VOID — the H1/H2 write-back control cannot split (stale-correct
≡ cleared by byte census); write-back integrity proven (16 commits, zero
byte drift). No tuning loop was entered: one hunk, one build, one device
run. Retry not used (exit 0); lldb not used (zero new tombstone —
nothing to triage).
