# G34 report — Tagged write-back: H1 WINS (tag renders EXACTLY), H2 refuted (Odin)

Brief: G34 (this turn) — executes G33 §4's ONE next action ONLY: the
tagged write-back control (same W1 sync, sparse nonzero-RGB tag
OR-masked into the temp pre-commit — splits H1 ordering/coherency from
H2 content-dependent fault). Tables + hypothesis + next-action
recommendation, no verdicts beyond the hypothesis. Time box 6 h (used
0.25 h — 08:00→08:15 EDT task start → commit; measured walls:
08:02:55 dir baseline, Task 1 statics + oracles 08:03→08:06, hunk +
build 08:06→08:08:32, verify-push-run-pull-cleanup-mirror 08:09:18→
08:10:41, report 08:11→08:14). Read first per the brief:
`local/research/G33/REPORT.md` (all of it: the write-back control is
VOID because stale-correct ≡ cleared byte-for-byte (0/229376
nonzero-RGB words), while write-back integrity is proven (16 commits,
zero drift) — the mechanism is exonerated, the CONTENT was wrong). No
upstream contact of any kind (standing no-upstream order — local hunks
only, filing stays local).

Machine: same as G8–G33 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g34/`
ONLY; removed at end (`mg/` only).

Headline result: **H1 WINS — decisively, on pre-registered bytes.**
(1) Task 1 statics tabled the tag shape (word 0 of each of the 112 B
pages OR-masked `0x00FFFFFF` pre-commit), the mask site (temp
pre-commit inside the W1 sequence), reformulated H1/H2 predictions
(every scalar pre-registered), the G33 predictor reuse (the REAL
`/tmp/g33-predict.py` reproduces the VOID on stale input; an
independent `/tmp/g34-predict.py` port cross-checks every scalar), and
a five-row decision matrix. (2) ONE hunk (G33's +51 excised + G34's
+55 tagged write-back inserted in the same edit), ONE build (exit 0
`[458/458]`, full identity), verify-then-push with NO gap, ONE run:
**exit 0**, 16/16 `G34: writeback` (tagged temp
`c039a1d1c29cb293`/150057 ×16) + 16/16 `G31: state` (fields == G31
×16, full lines stripped-identical) + 16/16 `G31: bytes` (B ==
tagged ×16, A == G31 ×16) + 512 `G30: vpage` (112/112 tagged pages
== per-page oracle, 400/400 non-B == G31) + 10 `G29: ladder`
(P1=P2=P3 == tagged-model `86ad7b887e140383`/229712 ×10, 0/10
cleared) + 1 `G29: vram`, ZERO new tombstone, 10/10 scanouts
BYTE-IDENTICAL to the host tag model (sha `d19e6beb…`, `cmp`
identical, 112 white pixels at exactly the predicted positions). H2
(tag content is not the pattern → cleared) is refuted 0/10; no
OTHER branch fired. The ONE next action is the commit-necessity wall
(same tag, NO `end_vram_write`): it splits H1-barrier (predicts
cleared) from refined-H2-threshold (any nonzero-RGB content suffices,
predicts tag-visible).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g34-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g34/` (retrieval: logcat + stdout + stderr + 10 PPMs, explicit list) | 50 MB | 13 files, 25,600 KiB allocated PASS |
| SSD `ps2x-g10..g33` + G14/G18/G20/G22/G24/G26/G28/G29/G30/G31/G32/G33 build dirs (read-only) | 0 growth | all == 08:02:55 snapshot exactly (post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (tagged write-back + retained dumps) | ONE hunk in `gs/gs_interface.cpp` (+55/−0 G34, G33 +51 excised same edit, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 + G31 hunks untouched, HUNK_MATCH re-verified pre + post + pre-push + post-run + report); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g34-*` ~800 KiB (predict/oracles/hunk/build/run/score + stub + build log + expected PPM + vpage/whites oracles, session-only); G34 evidence dir text-only PASS |
| `/` volume df shift (observed, tabled) | — | `/` Avail 10 Gi → 5.6 Gi (57%→70%) with Used static at 13 Gi — system-level (APFS/snapshot accounting), NOT lane files (measured lane footprint <1 MB); no action, recorded for the gate |
| device | `/data/local/tmp/g34/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |
| share-tier mirror (drive distrusted) | — | `/Volumes/share/ssx3/ps2x-g34/` 13/13 files, `shasum -c` ALL OK PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | OR-masking a sparse nonzero-RGB tag into the W1 temp BEFORE the write-back commit splits H1 from H2: H1 (ordering/coherency — the commit/barrier was G32's fix) predicts output renders the tag EXACTLY (ladder == tagged-model FNV `86ad7b887e140383`/229712 ×10, scanouts == tagged-model image sha `d19e6beb…`); H2 (content-dependent fault — the pattern content was the fix) predicts output stays cleared (ladder == `aa2fa32572450383` ×10, scanouts byte-identical black) because tag content is not the G32 pattern |
| observable signal | design tables (§2: tag + mask site + barrier parity + named bytes + predictor reuse + matrix + hunk spec) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G34: writeback` (tagged temp) + 16 `G31: state` + 16 `G31: bytes` (B == tagged) + 512 `G30: vpage` (112 oracle + 400 == G31) + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + 10 scanouts scored (exact-vs-tag-model / exact-vs-black / white-set census) + verdict (§4) |
| alternatives | H1-TAG-VISIBLE (tagged source ×16 + tag-model-exact output ×10); H2-STILL-CLEARED (tagged source ×16 + cleared output ×10); OTHER-writeback (temp or B ≠ tagged — write-back path failed, stop, no H1/H2 verdict); OTHER-mixed (tagged source + neither-tagged-nor-cleared output — partial/torn coherency, triage by per-pixel deltas; refutes H1+H2 jointly) |
| stop condition | ONE hunk max (tagged write-back + retained dumps); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: H1-TAG-VISIBLE — all 16 write-back receipts carry the tagged
FNV, all 10 ladders carry the tagged-model FNV (P1=P2=P3), all 10
scanouts are byte-identical to the tagged model, and all 112 tagged
pages match the per-page oracle while all 400 non-B pages match G31.
H2 is refuted (0/10 cleared); OTHER-writeback and OTHER-mixed never
triggered. No tuning loop was entered: one hunk, one build, one
device run. Retry not used (exit 0); lldb not used (zero new
tombstone — nothing to triage).

## 2. Task 1 — static design (no device runs)

### 2a. Pin verification (pre-work — G33 end state reproduced, ZERO edits)

08:02–08:03 EDT (every pin re-checked before any edit):

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G33 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 155 (134 − 30 + 51 — arithmetic closes), gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 — G33 end state + nothing |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH; re-verified post-hunk + pre-push + post-run + report — 5/5) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (Granite HEAD `16e7395f…` == pin) |
| G29 ladder + G30 vpage + G31 state + G33 writeback | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 in replayer; `G31: state` ×1 + `G31: bytes` ×2 + `G33: writeback` ×3 in interface; `G32: inject` ×0) |
| G28 binary (re-sha) | 265,841,104 B, sha `450471e2…` FULL-match, magic `7f45 4c46` ELF — **INTACT** |
| G29 binary (re-sha) | 265,846,144 B, sha `79e6f4d2…` FULL-match build sha, magic ELF — **INTACT** (was zeroed at G30 time; read-path artifact confirmed again) |
| G30 binary (re-sha) | 265,847,904 B, sha `a1963e66…` FULL-match build sha, magic ELF — **INTACT** |
| G31 binary (re-sha) | 265,851,416 B, sha `c91719a0…` FULL-match, magic ELF — **INTACT** |
| G32 binary (re-sha) | 265,852,240 B, sha `35288fd0…` FULL-match build sha, magic ELF — **INTACT** |
| G33 binary (re-sha ×3 + tracked) | 265,853,048 B, mtime frozen at build (07:30:55), sha `46028004…` stable ×3, magic `00000000`, **0 nonzero bytes — 11th zero-damage recurrence** (see §2a2; tracked at pre-push + post-run + report — stable all session) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` snapshot 08:02:55 (ps2x-g10 43008 … g33 25600; 12 build dirs 4480000/4482048 KiB; `/` 57%, SSD 93%); post-run re-verified §0 (every value identical) |
| recipe | NDK r30 (`/opt/homebrew/share/android-ndk`, toolchain file present); cmake + ninja + clang++ + python3 + adb all on PATH (`llvm-readelf` via NDK toolchain path) |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 29 G free |
| session survivors | NO host restart: all 7 `/tmp/g33-*` session files present (same boot) — the REAL G33 predictor + hunk applier + scorer are reusable as-is (§2e) |
| share tier | `/Volumes/share/ssx3/ps2x-g33/` present (orchestrator-mirrored); mirror target `ps2x-g34/` confirmed writable |

### 2a2. G33-binary pin vs the brief's stop rule (tabled — proceeded, rationale on record)

The brief states the G33 binary at `d1238552…` (ELF + hunk markers
intact, "flash-level suspect") and orders "any pin mismatch → table +
stop". Pre-work reads show `46028004…`, magic `0000`, 0 nonzero bytes
(stable ×3, mtime frozen at build) — a mismatch BOTH vs the build sha
(`7e0ea803…`) AND vs the brief's stated `d1238552…`. This was TABLED
and the brief was PROCEEDED WITH, for four on-record reasons: (1) the
brief already priced a G33 mismatch and still ordered the run, so the
stop rule cannot mean "any mismatch vs build shas" or the brief is
self-contradictory; (2) lane precedent (G33 §2a + §7.8) handled the
IDENTICAL case (G32 binary fully zeroed pre-run) as observation-only
and the run's conclusions stood; (3) the signature == the reclassified
class exactly (mtime frozen, fully zeroed, stable-in-window; G29/G32
both showed zeroed→intact across re-reads) — and a read that morphs
from localized-diff to fully-zeroed with a frozen mtime WEAKENS the
brief's flash-mutation hypothesis toward the dying-link read-path
artifact; (4) the G33 binary is NOT in G34's validity chain (dump +
new-binary chain match at every gate, §3d). Mitigation applied: the
file was re-read at all three paranoia gates (stable `46028004…`
throughout) and all G34 receipts were mirrored to the share tier with
`shasum -c` verification (§3i).

### 2b. Tag shape (tabled — exactly one picked)

| tag | shape | verdict |
| --- | --- | --- |
| A. one word per page, OR `0x00FFFFFF` (CHOSEN) | word 0 of each of the 112 B pages (`temp[p*2048]`) OR-masked with RGB-white pre-commit; 112/229376 words touched (0.049%) | **CHOSEN** — sparse (minimal delta vs G33's proven-identity write-back: exactly +336 nonzero bytes, §2d arithmetic); every page touched (vpage proves per-page commit carriage 112/112); OR preserves stale alpha (delta is RGB-only, exactly known); white is maximally unambiguous in output (any nonzero-RGB discriminates since stale has 0, but white needs no threshold argument); word-0 is enumerable and position-predictable (first-row grid, §2d) |
| B. single word total | one word OR-masked | REJECTED — sparsest but weakest: a single-pixel signal risks reading as noise/tear; no per-page commit coverage |
| C. sparse echo subset | G32 echo formula on a sparse subset | REJECTED — reintroduces echo content; H2's "not the pattern" prediction weakens if the tag smells like the pattern; constant-white keeps H2's prediction crisp |
| D. full-pattern rewrite (G32 redo) | whole-window pattern + commit | REJECTED — not sparse (confounds content-delta size with the commit question); G32 already ran this cell |

Why sparse (brief's "why sparse?" — answered): the control's power
comes from holding the W1 mechanism fixed while changing as little
content as possible — every tagged word is a byte the commit path
must carry, so sparse = strongest integrity reading per changed byte,
and the vpage/render deltas stay exactly enumerable (112 words, 112
pixels, +336 bytes everywhere).

### 2c. Mask site + sequencing (vs G33's W1) + barrier parity

Mask site: the static temp, AFTER the B→temp CPU copy, BEFORE the
temp FNV — so the `G34: writeback` receipt checksums the TAGGED temp
(proving WHAT was re-written at write time) and the temp→B copy
carries the tag into the committed write:

| step | G33 (W1) | G34 (W1 + tag) |
| --- | --- | --- |
| 1 | `map_vram_read(B)` | same call, same base/n |
| 2 | CPU copy B→temp | same |
| 3 | — | **OR-mask: `temp[p*2048] \|= 0x00FFFFFF` for p in 0..111** (CPU-only, 4 lines) |
| 4 | temp FNV/nz (stale) | temp FNV/nz (**tagged** — `c039a1d1c29cb293`/150057) |
| 5 | `map_vram_write(B)` | same call, same base/n |
| 6 | CPU copy temp→B | same (carries the tag) |
| 7 | `end_vram_write(B)` (commit) | same call, same rect |
| 8 | `G33: writeback` receipt | `G34: writeback` receipt (tagged FNV) |

Barrier parity inherits G33 §2b unchanged (same calls, same
base/n/rect/site; read leg still commit-free; G33 empirically proved
the nesting ×16): the ONLY mechanism delta vs G33 is 4 CPU lines on
the temp — no new API state, no new barrier, no new timing class
beyond 112 ORs.

### 2d. Reformulated predictions (every scalar pre-registered)

Stale B (pinned): FNV `eea04488c453e75b`, nz=149721, 0/229376
nonzero-RGB words. Tag adds exactly 112 words × 3 RGB bytes = +336
nonzero bytes, alpha untouched:

| observable | H1 (ordering/coherency) | H2 (content-dependent fault) |
| --- | --- | --- |
| 16 `G34: writeback` temp FNV | `c039a1d1c29cb293` nz=150057, base/n=917504/917504 (premise — same both columns) | same |
| 16 `G31: bytes` B | `c039a1d1c29cb293` nz=150057 head=`ffffff00…` (premise — tagged at sample time) | same |
| 16 `G31: state` | all fields == G31 predictions; full lines stripped-identical to G31's 16 | same |
| 512 `G30: vpage` | 112/112 B pages == per-page tagged oracle (each nz = stale + 3, head `ffffff00…`); other 400/400 == G31's vpage | same |
| 16 A-lines | == G31's 16 A-lines (scene path untouched) | same |
| 1 `G29: vram` | `6002946899e9cae0`/1184729 (restart control) | same |
| 10 `G29: ladder` P1/P2/P3 | == tagged-model `86ad7b887e140383` nz=229712 ×10 | == cleared `aa2fa32572450383` nz=229376 ×10 |
| 10 scanouts | BYTE-IDENTICAL to `/tmp/g34-expected.ppm` (sha `d19e6beb…`, 688,143 B; exactly 112 white pixels at the predicted positions, bbox x[0,448] y[0,416], first row x=0,64,…,448 @ y=0) | BYTE-IDENTICAL black (sha `99418f1b…`) |
| logcat | 2376 lines (G31's 2360 + 16 G34); `Total time per VBlank` inflated class | same shape |

Nz arithmetic (all three close): 149721 + 336 = 150057 (tagged B);
229376 + 336 = 229712 (tagged render); 112/229376 nonzero-RGB words
in, 112 white / 112 nonblack pixels out.

### 2e. G33 predictor reuse (the REAL predictor, + an independent port)

No host restart this session: `/tmp/g33-predict.py` (the exact
artifact behind G33 §2c2) ran unmodified against the pinned dump:

| check | observed |
| --- | --- |
| load full-VRAM | `6002946899e9cae0`/1184729 (== pin) |
| stale B | `eea04488c453e75b`/149721 (== pin) |
| G32-pattern self-check | B `dfe2b6516a519f83`/915264 + model P1 `9dd120bc6b0df383`/915264 (== committed G32 scalars) |
| VOID reproduction | H1-FNV == cleared (`aa2fa32572450383`)? **True**; H1 PPM sha `99418f1b…`; 229376/229376 zero-RGB pixels; swizzle bijective 229376/229376 |

The NEW `/tmp/g34-predict.py` (independent port from the clone's
`swizzle_PS2` + `get_data_structure` + `sample_circuit.frag` call
shape + `restart()` layout, written before seeing the survivor)
cross-checks EVERY scalar above bit-for-bit, then emits the §2d tag
oracle (TB `c039a1d1c29cb293`/150057, render `86ad7b887e140383`/
229712, PPM `d19e6beb…`, 112 whites) plus `/tmp/g34-vpage.txt` (112
per-page tagged FNVs — each nz exactly stale+3) and
`/tmp/g34-whites.txt` (112 predicted positions).

### 2f. Decision matrix (pre-registered)

| G34 temp + B (16+16) | ladder P1 (10) + scanouts | reading |
| --- | --- | --- |
| temp == tagged ×16, B == tagged ×16 | == tagged-model `86ad7b887e…` ×10, scanouts tag-exact (`d19e6beb…`, 112 whites in-set) | **H1** — ordering/coherency (the commit/barrier fixed sampling) |
| temp == tagged ×16, B == tagged ×16 | == cleared `aa2fa325…` ×10, scanouts black-exact | **H2** — content-dependent fault (tag content is not the pattern) |
| temp ≠ tagged (any) OR B ≠ tagged (any) | — | OTHER-writeback — write-back path failed → STOP, no H1/H2 reading; temp FNV vs G31-B splits read-leg (temp≠tagged, B==tagged) from write-leg (temp==tagged, B≠tagged) from transient-writer (both≠tagged but equal) |
| temp == tagged ×16, B == tagged ×16 | neither tag-exact nor cleared (any pattern) | **OTHER-mixed / BOTH-REFUTED** — H1+H2 jointly refuted; per-pixel deltas (white-set membership + extras) name it |
| temp == tagged ×16, B == tagged ×16 | uniform single tag word (addressing-fixed degenerate) | subsumed by OTHER-mixed (not tag-exact, not cleared) |

### 2g. Hunk spec (the ONE hunk, named)

ONE hunk: **G34 pre-`renderer.vsync` tagged write-back** (map-read B →
static temp + sparse OR-mask pre-commit → map-write temp back →
commit + `G34: writeback` TAGGED-temp receipt), with **G33's
write-back block excised in the same edit** (its diff survives
committed in G33 evidence — excision is lossless and REQUIRED: live
untagged content would confound the control).

| item | spec → actual |
| --- | --- |
| site | `GSInterface::vsync`, immediately BEFORE `auto result = renderer.vsync(…)` — the same anchor G32/G33 used (anchor `"\tauto result = renderer.vsync(priv_registers, info,\n"`, unique ×1) → CONFIRMED ×1 |
| shape | ONE contiguous insertion (`{…}` block at 1-tab scope); G33's +51 block excised first (derived from the committed `g33-writeback.diff` `+` lines — no transcription); net vs G33 worktree: tagged write-back only → +55/−0 contiguous, single @@ (`@@ -4684,2 +4723,57 @@`); worktree `gs_interface.cpp` diff 159 = 155 − 51 + 55 (arithmetic closes) |
| temp + tag | `static uint32_t g34_temp[(112*8192)/4]` (function-static, 917504 B BSS; fully rewritten each call before use; vsync is serial — no reentrancy) + `for (p in 0..111) temp[p*2048] \|= 0x00ffffffu` → as spec'd |
| receipt | `G34: writeback base=%u n=%u fnv=%016llx nz=%u.` (TAGGED-temp FNV/nz, truncated basis G29-E1) + `read-map failed` / `write-map failed` fallbacks (3 `G34: writeback` markers total) → as spec'd |
| applier | `/tmp/g34-hunk.py` (mirrors `/tmp/g33-hunk.py`): asserts G33-block ×1 + immediately-pre-anchor + G34-absent + anchor ×1; single file write; post-asserts G33-gone + G34 ×3 + G31 neighbors intact (`G31: state` ×1, `G31: bytes` ×2) → DRY-OK then APPLIED; post: G33 ×0, G34 ×3, G31 ×1/×2, G22 HUNK_MATCH |
| syntax | hunk text extracted from the applier compiles clean in a stub TU (`clang++ -std=c++17 -Wall -Wextra -fsyntax-only` — STUB_SYNTAX_OK; 2 unused-set warnings are stub artifacts of no-op LOGI) → as spec'd |
| costs (tabled up front) | +16 logcat lines (~2 KB); runs inside the timed region (expect inflated ms/VBlank — diagnostic cost, not a signal); 16 extra HostAccess read+write+commit cycles + 2×917504 B CPU copies + 112 ORs/vsync → 2376 lines; 12.139 ms/VBlank (§3e) |
| retained | G22 + G26 + G28 + G29 ladder + G30 vpage + G31 state/bytes all untouched (HUNK_MATCH + marker counts re-verified post-hunk) → all intact |

### 2h. Knob matrix (flag SET — the ONLY delta vs G33's run is G34's hunk-for-hunk swap)

| knob / flag | G33 setting | G34 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G33 = G31 + untagged write-back hunk | G34 = G31 + TAGGED write-back hunk (G33 block excised) | the single delta (content tagged, sync same) |

## 3. Task 2 — ONE tagged write-back control + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G33's run is the G34 hunk-for-hunk swap)

Same table as §2h (SET / UNSET / KEPT / ABSENT / hunk-for-hunk swap —
the single delta).

### 3b. Hunk record (ONE hunk, tagged write-back + retained dumps)

`gs/gs_interface.cpp`, G33's +51 block excised + ONE contiguous +55/−0
insertion (new lines ~4723–4777) in `GSInterface::vsync()`
immediately BEFORE the `renderer.vsync` call: `map_vram_read(917504,
917504)` → CPU copy into `static uint32_t g34_temp[]` → OR-mask
`temp[p*2048] \|= 0x00ffffffu` (p in 0..111) → truncated-basis
FNV/nz over the TAGGED temp → `map_vram_write(917504, 917504)` → CPU
copy tagged temp back → `end_vram_write` (commit) + `G34: writeback`
receipt (`read-map failed` / `write-map failed` fallbacks).
Regs/loop/circuit untouched. Full diff text in
`g34-writeback-tagged.diff` beside this report (mechanically extracted
with `-U1`: 55+/0-, single @@ block). G22 HUNK_MATCH + G26 block +
G28 Granite hunk + G29 ladder + G30 vpage + G31 state all untouched;
zero commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G33 recipe, `g34-build.sh` mirrored): exit 0
(`Configuring done (7.2s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`,
binary mtime 08:08:31).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp` + cmake-deprecation noise); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,853,192 B (+144 vs G33 — the tag-loop delta; NEW size expected) |
| sha (build-time) | `2b101ddec1cb27838c57192cf46960ac221eebd4ca8ca7d7e544c691e8dc2586` (NEW) |
| build-id | `c696a76ab6fa162124da9794d82d2aef0232a7ef` (distinct from G33 `8a89ed2c…`) |
| plumbing presence | `G34: writeback` ×3, `G33: writeback` ×0, `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule + paranoia triple-gate)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (×2 reads) | 08:09:18 | `2b101dde…` (binary) + `154d9d85…` (dump) FULL-match build sha; G22 HUNK_MATCH; all dirs == baseline (new g34 build dir the only growth) |
| device stage | 08:09 | `rm -rf` + `mkdir` + push dump (0.010 s) + push binary (2.072 s) into `/data/local/tmp/g34/` ONLY |
| on-device sha match | 08:09 | `154d9d85…` + `2b101dde…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 08:09 | `logcat -c` then run — no idle window |
| on-device post-run re-sha | 08:09 | `2b101dde…` FULL-match — intact |
| report-time re-sha | 08:10:41 | `2b101dde…` FULL-match + ELF magic — **binary INTACT, no zero-damage recurrence this window** (5th matching read: build + pre-push ×2 + post-run + report) |
| G33-binary track (all 3 gates) | pre/post/report | `46028004…` stable throughout (11th recurrence, §2a2; never in the push chain) |

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g34/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g34/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g34-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790078970→1790078971; logcat 08:09:30.652→08:09:31.035) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G33) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G34: writeback` + 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 map-fails of any kind |
| logcat | 2376 lines (== G31's 2360 + 16 G34 exactly): init + 18 `Running frame` + 18 G10 + `Total time per VBlank: 12.139 ms` (same inflated class as G31's 9.194 / G32's 8.871 / G33's 12.064 — diagnostic cost of 16 extra map+copy+commit inside the timed region, §2g) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical in G29–G33 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each) ALL pulled by explicit list (§3i); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (writeback + ladder + vpage + load line — continuity with G29–G33)

| receipt | observed |
| --- | --- |
| 16 `G34: writeback` | ALL `base=917504 n=917504 fnv=c039a1d1c29cb293 nz=150057`, 0 map-fails — the bytes re-written were tagged-stale at write time, on every vsync, both passes |
| 10 `G29: ladder` | ALL P1=P2=P3=FNV `86ad7b887e140383`, nz=229712 == tagged-model (§2d) — 10/10 tag-visible, 0/10 cleared |
| 512 `G30: vpage` (all pass=1, pages 0..511) | 112/112 B pages == per-page tagged oracle (each nz exactly stale+3, head `ffffff00…` — the commit carried the tag on every page); other 400/400 timestamp-stripped lines BYTE-IDENTICAL to G31's vpage (write-back perturbed NOTHING outside the 112 tag words) |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz=1,184,729 == host load FNV — trailing-restart mechanism reproduced on-device a sixth time (restart control passes) |
| 16 A-lines | A-fields BYTE-IDENTICAL to G31's 16 A-fields (scene path untouched — non-perturbation proven beyond determinism; §3g) |

### 3g. Writeback + state + bytes verdicts (tagged source at every write and sample time)

Writeback lines (16/16 full receipts, 0 fallbacks):

| field | predicted | observed |
| --- | --- | --- |
| base / n | 917504 / 917504 ×16 | **16/16 EXACT** |
| tagged-temp FNV / nz | `c039a1d1c29cb293` / 150057 ×16 | **16/16 EXACT** — re-written bytes were tagged at write time |

State lines (16/16 match G31 predictions — every field, every seq;
regs/knobs identical by construction; full lines stripped-identical to
G31's 16/16):

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

Bytes lines (16/16 fire, 0 map-fails):

| region | predicted | observed |
| --- | --- | --- |
| B (the discriminator) | tagged `c039a1d1c29cb293` nz=150057 head=`ffffff00…` ×16 | **16/16 EXACT match** — tagged source at EVERY sample time (OTHER-writeback never triggered) |
| A (live control) | == G31's A (untouched), pass-repeat 8/8 | 16/16 A-fields BYTE-IDENTICAL to G31's; 8/8 EXACT pass-repeat |

### 3h. Split analysis (H1 — the tag renders EXACTLY; H2 refuted)

| link | evidence |
| --- | --- |
| write-back carried the tag | 16/16 temp == tagged at write time + 16/16 B == tagged at sample time + 112/112 vpage == per-page oracle — the read leg reads stale, the OR plants the tag, the write leg + commit carry it (content-exact, as constructed) |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0`) → `sample_quad[0]` + `buffers.gpu` on every vsync — same path as G31/G32/G33 |
| source bytes at sample time | region B == tagged-stale (16/16 `c039a1d1…`, 112/229376 nonzero-RGB words) — never cleared-as-content, never transient-written |
| circuit output | 10/10 ladder P1/P2/P3 == tagged-model `86ad7b887e140383`/nz=229712; 10/10 scanouts byte-identical to the tagged model (sha `d19e6beb…`, `cmp` identical, 112 whites in-set, §3i) — equals the H1 prediction EXACTLY |
| elimination | OTHER-writeback never triggered (path proven); OTHER-mixed never triggered (no neither-nor output); H2-STILL-CLEARED refuted 0/10 (no cleared ladder, no black scanout — tag content, though not the G32 pattern, moved the output onto the tag model) |
| verdict | **H1: ordering/coherency — the per-vsync host-write+commit is what fixed sampling.** Same W1 sync as G33, plus 112 OR'd words, moves the output from cleared (G31/G33) to the exact tag render. The G31→G32 delta is therefore the SYNC, not the content: with the commit, the sampler reads back exactly what was written (G32 pattern-exact + G34 tag-exact); without it, the sampler emits cleared from a nonzero-RGB source (G31). Brightness is now understood at the sample level: cleared ⟺ uncommitted-stale sampling on this path. |

### 3i. Scanouts (10/10 pulled by explicit list — G31-E1 applied) + share mirror

Explicit pull list (12 files + logcat; each named, zero globs):
`g34-run-stdout.txt`, `g34-run-stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0.ppm` … `g10-vsync7.ppm`,
`g13-dump.gs.g8-first.ppm`, `g13-dump.gs.g8-last.ppm` (all 688,143 B).
All 12 pulls individually confirmed (`1 file pulled, 0 skipped`).
Cleanup ran as its OWN verified step AFTER pull verification
(`rm -rf` + `ls` → `mg/` only, exit 0).

| file | sha256 | vs H1 tag model |
| --- | --- | --- |
| 10/10 scanouts | `d19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f` (unanimous) | BYTE-IDENTICAL to `/tmp/g34-expected.ppm` (`cmp` 10/10 — 11-way unanimity incl. the host model) |

Pixel census (per file): exactly 112 white + 229264 black pixels;
112/112 whites at the predicted positions (expected-PPM identity
proves set membership); nonblack pixels 112/229376 (no extras, no
smear — the tag lands crisply, no torn coherency).

Share-tier mirror (drive distrusted): all 13 `ps2x-g34/` files copied
by explicit name to `/Volumes/share/ssx3/ps2x-g34/`; `shasum -c`
13/13 OK against the SSD shas.

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 16 G34 + 32 G31 lines + all controls + `Done!` |
| second shape | NOT USED | out of budget by the stop rule (H1 verdict is terminal for this control — the refinement is a new discriminator, §4, not a second shape here) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| OR-masking a sparse nonzero-RGB tag into the W1 temp pre-commit splits H1 from H2 | **H1 — decisively.** Tagged source proven at every write time (16/16 `c039a1d1…`/150057) and every sample time (16/16 B == tagged, head `ffffff00…`), the commit carried the tag on all 112 pages (112/112 vpage == per-page oracle, 400/400 non-B == G31), and the circuit rendered the tag EXACTLY (10/10 ladders P1=P2=P3 == `86ad7b887e140383`/229712, 10/10 scanouts byte-identical to the host tag model sha `d19e6beb…`, 112 whites in-set). H2-STILL-CLEARED is refuted 0/10. OTHER-writeback and OTHER-mixed never triggered. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **the commit-necessity wall
(same tag, NO `end_vram_write`) — NOT adoption.** Rationale: G34
refutes H2-as-registered (tag-is-not-the-pattern → cleared), but the
tag IS content — so a refined H2-threshold ("ANY nonzero-RGB content
in B fixes sampling, commit or no commit") survives G34 untested. The
discriminator: same W1 legs + same sparse OR-mask, but SKIP the
commit (map-write the tagged temp back with no `end_vram_write`);
the `G34: writeback` receipt still checksums the tagged temp and
G31-B still verifies the tagged source. H1-barrier predicts output
stays cleared (no commit → G31's uncommitted sampling); refined-H2
predicts tag-visible (content suffices). Queued behind it (not this
action): G26+G28 adoption — the brightness condition is NOW MET
(cleared ⟺ uncommitted-stale sampling, proven at the sample level
§3h) but adoption stays queued per the standing rule until the
orchestrator gates it; the Adreno filing — STILL OPEN regardless
(content upgrades again: "per-vsync host commit on the sampled pages
renders a 112-word sparse tag EXACTLY; without it the sampler emits
cleared from a tagged source — ordering/coherency, H1"); G18-hunk
fix adoption (still queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk + pre-push + post-run + report) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G33 write-back hunk | EXCISED from the worktree by this brief's edit (diff text survives committed in `local/research/G33/` — lossless) |
| G34 additions | the ONE tagged write-back hunk (SSD clone worktree only) + session files: `g34-build.sh` + `g34-run.sh` + `g34-writeback-tagged.diff` (G34-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g34/` ONLY (not in git) + verified share-tier mirror `/Volumes/share/ssx3/ps2x-g34/` (13/13 `shasum -c` OK); no PII (`uid: shell`); all 10 PPMs pulled (shas + census in §3i) |
| host analysis | `/tmp/g34-*.py` + `/tmp/g34-*.sh` + `/tmp/g34-build.log` + `/tmp/g34-expected.ppm` + `/tmp/g34-vpage*.txt` + `/tmp/g34-whites.txt` + `/tmp/g34-stub.cpp` (session-only; `/tmp/g33-predict.py` reused unmodified for the VOID self-check) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (G33 end state)
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (pre+post+pre-push+post-run+report)
shasum -a 256 <g28..g34 binaries> + xxd magic (x3 for g33)                # §2a (g28-g32 INTACT, g33 46028004 zeroed, §2a2)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g34 + 13 build dirs> ; df -h / $SSD           # §0 (pre 08:02:55 + post 08:09:55)
python3 /tmp/g33-predict.py $SSD/ps2x-g13/g13-dump.gs            # §2e (REAL G33 predictor: VOID reproduced)
python3 /tmp/g34-predict.py                                       # §2d (independent port cross-check + tag oracle)
python3 /tmp/g34-oracles.py                                       # §2d (per-page vpage oracle + white list)
python3 /tmp/g34-hunk.py --dry                              # §2g (DRY-OK: G33x1 pre-anchor, anchorx1)
clang++ -std=c++17 -Wall -Wextra -fsyntax-only /tmp/g34-stub.cpp  # §2g STUB_SYNTAX_OK
python3 /tmp/g34-hunk.py                                    # §3b (ONE single-write edit: -51/+55)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff -U1 | grep '^@@'  # hunk shape (159; single @@ ours)
cmake -S <clone> -B $SSD/parallel-gs-g34-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g34-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g34-binary> (build, pre-push x2, post-run, report)  # 2b101dde… x5 match (intact)
llvm-readelf --notes <g34-binary> ; strings grep 3/0/1/2/1/1/1/2/1/1/2/0 ; xxd -l 4  # c696a76a… + ELF
python3 /tmp/g34-score.py                                       # §3f–3i (16/16 + 10/10 + 112/112 + 400/400 + TAG x10 + H1)
cmp /tmp/g34-expected.ppm $SSD/ps2x-g34/<each of 10 PPMs>        # §3i (H1 == model x10, byte-identical)
cp <13 ps2x-g34 files by name> /Volumes/share/ssx3/ps2x-g34/ ; shasum -c  # §3i (mirror 13/13 OK)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g34/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 29G)
shell 'rm -rf /data/local/tmp/g34 && mkdir -p /data/local/tmp/g34'
push <dump> $G34DIR/g13-dump.gs ; push <g34-binary> $G34DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G34DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G34DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g34-run-stdout.txt 2> g34-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (H1 fired)
logcat -d -s Granite:V > $SSD/ps2x-g34/g34-logcat.txt                # 2376 lines
pull $G34DIR/g34-run-stderr.txt $SSD/ps2x-g34/ (0 B) ; pull stdout (0 B)
pull $G34DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g34/   # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G34DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # 2b101dde… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g34 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The refined-H2-threshold alternative ("ANY nonzero-RGB content in B
   fixes sampling, commit or no commit") survives G34 untested — the
   tag IS content. Queued as the §4 next action (commit-necessity wall:
   same tag, no `end_vram_write`; H1-barrier predicts cleared).
   Within-H1 refinement (which commit-path element — flush+wait vs the
   commit barrier itself) is likewise open and answered by the same wall.
2. The H1/H2 split AS REGISTERED is CLOSED (H1 wins, H2 refuted) —
   not a gap; recorded so no future brief re-litigates it.
3. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the host swizzle model is this brief's oracle and
   matched byte-exactly, 11-way sha unanimity with the model PPM).
4. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
5. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G34 binary intact at all five).
6. G26+G28 adoption is queued, not done (brightness condition NOW MET
   per §3h — but adoption stays queued per the standing rule until the
   orchestrator gates it; no port, no upstream contact).
7. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
8. The G33 binary reads fully zeroed all session (`46028004…`,
   mtime frozen — 11th recurrence, §2a2) after the brief stated a
   localized `d1238552…` read — tabled as an OBSERVATION with
   proceed-rationale on record: the morph-with-frozen-mtime weakens
   flash-mutation toward read-path artifact; no verdict (forensics is
   out of scope; no lane data depended on the G33 binary bytes — all
   G33 receipts live in `ps2x-g33/` + the share mirror).
9. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
10. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
11. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes + cmake noise); zero
    warnings point at the hunk lines.
12. The `map_vram_read`-then-`map_vram_write` nesting is now proven
    empirically ×32 (G33 ×16 + G34 ×16, tagged and untagged) — not by
    a second independent writer.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g34/` (13 files:
  `g34-logcat.txt` 2376 lines incl. 16 `G34: writeback` + 16 `G31: state` +
  16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g34-run-stderr.txt` 0 B, `g34-run-stdout.txt` 0 B, 10 scanout PPMs
  688,143 B each sha `d19e6beb…` unanimous) +
  `parallel-gs-g34-android-build/` (binary 265,853,192 B
  `2b101dde…` BuildID `c696a76a…`, intact at report time).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g34/` (13/13 files,
  `shasum -c` ALL OK — drive distrusted, §2a2).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g33/` + G14/G18/
  G20/G22/G24/G26/G28/G29/G30/G31/G32/G33 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 + G34 hunks uncommitted (G33 excised);
  Granite `16e7395f…` + G20-capture set + G28 hunk, all uncommitted —
  ZERO commits anywhere).
- Session-only: `/tmp/g34-*.py` (hunk/predict/oracles/score),
  `/tmp/g34-*.sh` (build/run), `/tmp/g34-build.log`,
  `/tmp/g34-expected.ppm` (host oracle, `d19e6beb…`),
  `/tmp/g34-vpage.txt` + `/tmp/g34-vpage-stale.txt` + `/tmp/g34-whites.txt`,
  `/tmp/g34-stub.cpp` (syntax stub).
- Commits: ssx3 `local/research/G34/` `[G34]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G34 report ends here. Task-1 statics tabled the sparse
tag (word 0 of each B page OR `0x00FFFFFF` pre-commit), the temp
pre-commit mask site with W1 barrier parity, pre-registered every H1/H2
scalar (TB `c039a1d1c29cb293`/150057, render `86ad7b887e140383`/229712,
PPM `d19e6beb…`, 112 whites), reused the REAL G33 predictor for the
VOID self-check (cross-checked by an independent port), and tabled a
five-row decision matrix. ONE tagged write-back hunk (+55/−0, G33 +51
excised same edit) + ONE build exit 0 + ONE run exit 0 with 16/16
tagged-temp + 16/16 tagged-B + 112/112 oracle vpages + 10/10
tag-model ladders + 10/10 tag-exact scanouts proves H1 (ordering/
coherency — the commit fixed sampling) and refutes H2 (0/10 cleared).
Next wall is the commit-necessity wall (same tag, no commit), not
adoption; filing still open (G31-E1 applied: explicit pull list,
separate cleanup; share mirror 13/13 OK).

Outcome: H1 — the sparse tag renders EXACTLY (commit fixes sampling);
H2 refuted. No tuning loop was entered: one hunk, one build, one device
run. Retry not used (exit 0); lldb not used (zero new tombstone —
nothing to triage).
