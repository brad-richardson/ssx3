# G39 report — G26+G28 regression/adoption gate: both fixes HOLD on current HEAD, adoption-mechanics recommendation (Odin)

Brief: G39 (this turn) — the G26+G28 regression/adoption gate: (1)
regression proof that each fix still holds its defect closed on
current HEAD + (2) a no-perturbation proof that valid behavior is
unchanged + (3) an adoption-mechanics RECOMMENDATION (carried-diff vs
in-clone commit — recommend, do not execute either; the orchestrator
decides). Tables + hypothesis + next-action recommendation, no
verdicts beyond the hypothesis. Time box 6 h. Read first per the
brief, all of each: `local/research/G26/REPORT.md` (flag-path
narrowing), `local/research/G28/REPORT.md` (writer fix), and
`docs/research/review-2026-09-22-progress-and-parallelization.md`
§G-lane (adoption gets its OWN gate, must NOT wait on later
experiments). The sub-vsync F1/F2/F3 wall is G40 — explicitly OUT.
No upstream contact of any kind (standing no-upstream order — local
hunks only, filing stays local).

Machine: same as G8–G38 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir
`/data/local/tmp/g39/` ONLY; removed at end (`mg/` only).

Headline result: **both fixes HOLD on current HEAD.** (1) Task 1 statics (ZERO device contact)
tabled per-fix defect receipts with G26/G28 report line numbers,
regression observables with exact expected bytes, no-perturbation
observables against adopted baselines (G38 O1 primary, G31
cross-check), and a per-fix HOLD/REGRESSED/PERTURBED decision matrix
with the correct-behavior alternative honored per observable. (2) The
worktree matches G38's end state exactly (HEAD, diff stat 385+/4-,
G22/G28 HUNK_MATCH, G26 block line-identical, G37 ×0, Granite
`16e7395f…`, superproject `fd781ef` clean) — the gate proceeds, ZERO
hunks, ZERO excisions. (3) Binary under test: G31 Odin binary
`c91719a0…` REUSED (source == current tree, both fixes + full
witnesses in-binary) — build budget ZERO. (4) Task 2: TWO bounded
Odin runs (R1 G26-shape, R2 G28-shape), both exit 0 — every
regression observable matches (G26 `=1,=0,=0` + warm `img=` 0×8 +
O4 absent; G28 skip receipt + `Done!` + 10 scanouts + zero
tombstone + zero Scudo) and all 12 no-perturbation classes are
EQUAL vs BOTH baselines (48/48) with 20/20 scanouts black
`99418f1b…` — HOLD-both with the F0 alternative honored. (5)
Adoption-mechanics RECOMMENDATION: carried-diff NOW (ssx3-committed
diffs are the durable record), in-clone commit AFTER storage
cutover — orchestrator decides; G40 queued behind this gate.

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir (if any) | 6 GB | NONE (valid binary reused) PASS |
| NEW SSD `ps2x-g39/` (retrieval by explicit list) | 50 MB | 24 files, 23,552 KiB allocated PASS |
| SSD `ps2x-g7..g38` + all build dirs (read-only) | 0 growth | all == 12:08:06 snapshot exactly (post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ZERO hunks, ZERO excisions (read-only) | ZERO worktree writes; G22/G28 HUNK_MATCH 4/4 (pre + pre-push + post-run + report); diff stat 385+/4- throughout; zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g39-shas.txt` ~2 KB (session-only); G39 evidence dir text-only; `/` Used static 13 Gi PASS |
| device | `/data/local/tmp/g39/` ONLY | staged 2 files, pulled 24 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host builds | ZERO unless no valid binary | ZERO builds (G31 binary valid, §2f) PASS |
| device runs | TWO bounded max (one per fix shape) | R1 (G26 shape) + R2 (G28 shape), both exit 0; retry not used (no retry budget — both slots are the shapes) PASS |
| committed to git | text only | REPORT.md + 3 session scripts; no binaries |
| share-tier mirror | — | `/Volumes/share/ssx3/ps2x-g39/` 24/24 files, `shasum -c` ALL OK PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Each fix still holds its defect closed on current HEAD: the G26 flag-only delivery shows its narrowing receipt + warm-pass `img=`=0 + O4 absent, and the G28 writer guard shows its engaged receipt + exit 0 + `Done!` + 10 scanouts + zero tombstone + zero Scudo signature — while every valid-behavior observable stays byte-equal to its adopted baseline |
| observable signal | design tables (§2: pins + defect receipts + regression observables + no-perturbation observables + baselines + decision matrix + binaries + quoted shapes) + HUNK_MATCH chain (pre + post + pre-push + post-run + report) + verify-then-push with NO gap + at most TWO bounded Odin runs of the SAME shapes (exit/wall/fate + `G26:`/`G28:` receipts + knob receipts + O4 legs + tombstone census, each run) + scanouts scored + per-fix HOLD/REGRESSED + no-perturbation verdicts + adoption-mechanics recommendation (§4) |
| alternatives | HOLD-both (all R-* + all N-* match); REGRESSED-G26 (O4/defect signature returns); REGRESSED-G28 (Scudo/exit-134 signature returns or guard disengaged); PERTURBED (R-* pass but N-* classes differ — valid behavior changed); OTHER-upstream (validity-chain pin mismatch → table + stop) |
| stop condition | ZERO new hunks, ZERO excisions (worktree must match G38 end state or table + stop); ZERO builds unless no valid binary (then ONE); TWO bounded Odin runs max (one per fix shape, no second shape per fix, no retry — both slots are the shapes); no tuning loop, no new dumps; no lldb unless a tombstone needs triage; a REGRESSED fix is a finding — table bytes + STOP that leg, do not repair |
| outcome → next action | numbers name the next single experiment (§4); adoption-mechanics RECOMMENDED not executed (orchestrator decides); G40 sub-vsync wall queued behind this gate |

## 2. Task 1 — static gate design (no device)

Zero device contact in this section: no `adb` invocation of any kind
before §3 (host tools only: git/grep/shasum/xxd/strings/llvm-readelf/
python/du/df). All line citations below are 1-based file lines of the
named committed report unless suffixed `logcat`.

### 2a. Pin verification (pre-work — G38 end state reproduced, ZERO edits)

12:08 EDT (every pin re-checked before any run; worktree read-only
this whole brief):

| item | observed |
| --- | --- |
| working tree (brief: VERIFY, re-pin if migrated) | `/Users/bradrichardson/dev/ps2xGS` EXISTS (harness repo — not the lane clone) — VERIFIED, no re-pin; lane clone remains SSD `parallel-gs-g7` below (same as G38 §2a) |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-run) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G38 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 104, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 (385+/4-) — G38 end state exactly (104 == 160 − 56 excised; 385 == 441 − 56) |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH — pre; post + pre-push + post-run + report §3) |
| G26 hunk | worktree `@@ -93,9 +96,15 @@` block line-identical to committed `g26-narrowing.diff` on all 15 captured lines (live diff carries 1 extra trailing-context line — the same nuance G28 §2a tabled as HUNK_MATCH) |
| G28 hunk | `git diff vulkan/memory_allocator.cpp` byte-identical to `g28-writer-fix.diff` (HUNK_MATCH) |
| G29/G30/G31 markers | `G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 (replayer) + `G31: state` ×1 + `G31: bytes` ×2 (interface) — G38 §3b exactly |
| G37/G36/G35/G34/G33 | ×0 / ×0 (excision holds — zero content hunks in tree) |
| Granite submodule | HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (== pin); 5 files + `? third_party/spirv-tools` untracked (tabled content-neutral since G38) |
| ps2xGS superproject | HEAD `fd781ef42924d471bb35b84c95e2bf673eb8a0f3`, status clean — G38 §3b exactly |
| G31 binary PASS1 (12:08:15) | 265,851,416 B, sha `c91719a0c96ef57a6ac2b80f6d4d29f54f515566bc249e0e2c4fd87a5d92367a` FULL-match, magic `7f45 4c46` ELF — INTACT |
| G31 binary PASS2 (12:08:53) | `c91719a0…` FULL-match (separated read; pre-push + on-device + post-run + report–time reads §3) |
| G31 binary corroboration | BuildID `c180f320527af30fd0c1444308a1fb3edf8fb2f2` FULL-match G31 report; `strings` markers exactly as specified (`G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G29: ladder` ×1, `G28:` ×1, `G26:` ×1, `G24:` ×0, `G37:` ×0) |
| rich dump PASS1 + PASS2 | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match ×2 |
| dirs 0-growth | pre-run `du -sk` snapshot 12:08:06 (every value == G38 §2a plus G38's own two dirs: ps2x-g38 35840, g38-mac-build 3811328); post-run re-verified §0 |
| recipe (Android leg) | NDK r30 (`/opt/homebrew/share/android-ndk`); NOT NEEDED — no rebuild (G31 binary valid, §2f) |
| baseline receipts | SSD `ps2x-g38/` 28 files + `/Volumes/share/ssx3/ps2x-g38/` 28 files + `g38-odin-logcat.txt` 2360 lines — all present |
| volume | `/` 3.0 Gi avail; SSD 119 Gi free |

Gate decision: worktree == G38 end state on every pin — the gate
PROCEEDS (no table-and-stop). SSD-rule note: lane-critical SSD bytes
(binary, dump) already have 2+ matching reads separated in time
(PASS1/PASS2) PLUS independent corroboration (BuildID, strings,
size/magic); the §3 chain adds pre-push + on-device + post-run +
report-time reads.

### 2b. Per-fix defect receipts (what failed before — G26/G28 report lines)

G26 fix = flag-only delivery (`tools/gs_dump_replayer.cpp`
`@@ -93,9 +96,15 @@`, +8/−1 vs HEAD, UNCOMMITTED — diff text G26
REPORT lines 93–110; committed `g26-narrowing.diff`):

| id | defect receipt | report lines |
| --- | --- | --- |
| D-G26-1 (defect closed: O4) | WITHOUT the flag (G25 value-0 / G23r2 dropped): Adreno `dispatch_texture_analysis` SIGSEGV, exit 139, first-draw death. WITH the flag (G24 + G26 at value-1): O4 ABSENT — 4-leg proof: (1) 134/SIGABRT≠139 with full loop completed, (2) crasher hashes 0× + 8/8 Stalled `success: yes` + 0 `success: no`, (3) death stack zero driver-compile frames, (4) death post-loop | G26:219–229 (§3d); bidirectional A/B G26:228–229 |
| D-G26-2 (attribution delivered: O6 persists) | WITH the narrow hunk: O6 PERSISTS at the SAME Scudo site — exit 134, `corrupted chunk header`, 16-frame stack `save_scanout_ppm → wait_idle → DescriptorSetAllocator::clear → vkDestroyDescriptorPool`, 16 ms after Total-time — ride-along exonerated, FLAG's full-upload path implicated | G26:208–217 (§3c), verdict G26:253–265 (§3g) |
| D-G26-3 (narrowing proof) | Logcat :29 `G26: debug_mode delivered (disable_sampler_feedback=1, feedback_render_target=0, use_rdoc=0).` (×1) + warm-pass `img=` collapsing to 0×8 while every other counter is line-identical to G24 (feedback writes GONE) | G26:189 (§3b receipt row), G26:196–206 (behavioral table) |
| D-G26-4 (demonstration binary) | 265,840,408 B, sha `81141181…`, BuildID `2e946006…`, `G26:` ×1 / `G24:` ×0 | G26:142–152 (§2c) |

G26-on-current-tree note (pre-registered): D-G26-2's exit-134 arm is
a HISTORICAL defect-demonstration receipt, not a current-tree
expectation — G28 closed O6's writer, so on the current tree (which
carries the guard) the G26 leg expects R-G26-1..3 (receipt + img +
O4-absent) with exit 0, never 134. Reproducing 134 would require
excising G28 — explicitly forbidden (ZERO excisions).

G28 fix = writer guard (Granite `vulkan/memory_allocator.cpp:1424`
branch gated on `supports_descriptor_buffer_or_heap` + once-LOGI
skip receipt, 18+/1-, UNCOMMITTED in the submodule — guard choice +
no-new-hazard table G28 REPORT lines 93–113; committed
`g28-writer-fix.diff` 1,770 B):

| id | defect receipt | report lines |
| --- | --- | --- |
| D-G28-1 (defect closed: single-writer family) | O6 pre-first-write Scudo abort (exit 134, G24/G26) + O5 post-`Done!` teardown Scudo abort (G22) + G27 HWASan `allocation-tail-overwritten` — three detection sites, one writer (stride-0 storage-image slab + unguarded use branch + driver's 64-byte `vkGetDescriptorEXT` write) | G28:223–230 (§3f census) |
| D-G28-2 (fix demonstration) | Exit **0**, `Done!` LAST, 10 scanouts, ZERO new tombstone; logcat :24 `G28: create_image_view descriptorBuffer branch skipped (supports=0, feature=1).` (×1, once-guard held — guard ENGAGED on-device exactly as G27 predicted) | G28:169–182 (§3b run table; receipt row :176) |
| D-G28-3 (separation: black is separate) | Scanouts still pure BLACK (mean 0.0, 0/688,128 nonzero, sha `99418f1b…`), byte-identical (`cmp`) to G27's black — G27 §3i's aliasing link REFUTED; black is a separate device trait (now explained: cleared-from-stale-B is correct, G33/G38) | G28:184–209 (§3c score table value-identical to G27 + §3d census) |
| D-G28-4 (O4 leg carried) | O4 absent 4-leg proof (exit-0 arm) — flag-set absent streak extends (G24 + G26 + G27 + G28 at value-1) | G28:211–221 (§3e) |
| D-G28-5 (demonstration binary) | 265,841,104 B (+696 vs G26), sha `450471e2…`, BuildID `53af7a56…`, `G28:` ×1 + `G26:` ×1 / `G24:` ×0 | G28:130–138 (§2d) |

### 2c. Regression observables (which receipt proves the defect STAYS closed)

Expected bytes/lines per run (BOTH runs are scored against BOTH
fixes' observables — each fix is tested once in its own shape;
cross-witnessing is free corroboration, not a second shape):

| id | observable | exact expectation |
| --- | --- | --- |
| R-G26-1 | narrowing receipt | `G26: debug_mode delivered (disable_sampler_feedback=1, feedback_render_target=0, use_rdoc=0).` ×1 (values, not line number, gate — async lines may shift absolute positions) |
| R-G26-2 | feedback writes stay gone | warm-pass (pass 1) G10 `img=` 0×8; cold pass keeps first-touch residue (shape `1966080/28672/0/327680/0/0/0/0`-class — layout-dependent values, shape-note informational per G28:180) |
| R-G26-3 | O4 stays absent (4 legs) | (1) exit 0 + full loop (`Total time per VBlank` printed, `Done!` last) ≠ 139 first-draw death; (2) crasher pipeline/shader hashes 0× + all Stalled posts `success: yes` + 0 `success: no`; (3) zero driver-compile frames (`dispatch_texture_analysis`/`vkCreateComputePipelines`/`libllvm-qgl`-executing absent); (4) clean exit through Device teardown phase |
| R-G28-1 | guard engaged | `G28: create_image_view descriptorBuffer branch skipped (supports=0, feature=1).` ×1 |
| R-G28-2 | clean fate | exit 0 + `Done!` LAST line + 10 scanouts written + ZERO new tombstone (newest stays G27's `_23`) |
| R-G28-3 | O5/O6 stay gone | 0 `corrupted chunk` in logcat + 0 ERROR/LOGE (modulo the pre-existing RenderDoc init noise line) |

### 2d. No-perturbation observables + adopted baselines (valid outputs byte-equal)

| id | baseline | which committed run's which receipts | why adopted |
| --- | --- | --- | --- |
| B0 (primary) | G38 O1 Odin | SSD `ps2x-g38/g38-odin-logcat.txt` (2360 lines) + 10 `odin-*.ppm` (black `99418f1b…` unanimous, G38:509–513) + `odin-g38-run-stdout/stderr.txt` (0 B) + share-tier mirror (28/28) | SAME source as current tree (G38 excised to == G31; G38 §3f fresh-vs-committed equality) + fullest receipts (logcat + PPMs + mirror) |
| B1 (cross-check) | G31 committed | SSD `ps2x-g31/g31-logcat.txt` (2360 lines: 18 Running + 18 G10 + 32 G11 + 8 Stalled + 16 state + 16 bytes + 512 vpage + 10 ladder + 1 vram + 10 `G8: wrote` + `Done!`, G31:240) | independent committed run proven equal to B0 by G38 §3f (timestamp-stripped EQUAL on all 9 classes) |

Per-class no-perturbation expectations (comparison method: G38 §3f
— timestamp-stripped class equality + counts; content+counts gate,
absolute logcat line numbers supporting):

| class | B0/B1 value | G39 expectation |
| --- | --- | --- |
| FRAME / RECORD / TEX / FLUSH | 32/32 + 64/64 + 1552/1552 + 16/16 (G38:448) | EQUAL (CPU-deterministic alignment — any mismatch = OTHER-upstream, STOP) |
| G10 | 18/18 (scratch/img-normalized; G38:448) | EQUAL |
| G31 state | 16/16 field-identical (G38:453–455) | EQUAL |
| G31 bytes A | varying ≠ load, pass-repeat 8/8, byte-exact (G38:459–466) | EQUAL |
| G31 bytes B | == load `eea04488c453e75b`/149721/`00000000…` ×16 (G38:461 — the Odin rule-3/4 expectation) | EQUAL |
| G30 vpage | 512/512 (B pages == load; G38:482–485) | EQUAL |
| G29 ladder | 10/10 cleared `aa2fa325…`/229376, P1==P2==P3 (G38:475–480) | EQUAL |
| G29 vram | `6002946899e9cae0`/1184729 (G38:444) | EQUAL |
| scanouts | 10/10 black `99418f1b…` unanimous (G38:511) | EQUAL (shas) |
| stdout/stderr | 0 B / 0 B (G31:381, G38:502–503) | EQUAL (R2 shape; R1 shape has no redirect by verbatim design) |
| logcat length | 2360 lines (B0 + B1) | EQUAL (supporting — informational init-line counts may vary by driver; classes gate) |

Informational-only (driver-dependent, never gating — G38 §2g note d):
`Total time per VBlank` ms, Stalled post counts (8-vs-9 class),
`G28:`-absent-vs-present on non-Adreno (n/a — Odin only),
`scratch`/`img` allocator sizes, RenderDoc init noise line.

### 2e. Decision matrix (HOLD vs REGRESSED vs PERTURBED, per fix, with triage)

| # | condition | reading | triage |
| --- | --- | --- | --- |
| 1 | any validity-chain pin mismatch (HEAD/diff/HUNK_MATCH/sha/BuildID/magic/size/du) | OTHER-upstream | table + STOP (no tuning, no run) |
| 2 | all R-G26-* + all R-G28-* + all N-* classes match (both runs) | HOLD-both | proceed to §4 recommendation |
| 3 | any R-G26-* fails (O4 legs fail: 139/crashers/`success: no`/driver frames; or receipt ≠ `=1,=0,=0`; or warm `img=` ≠ 0×8) | REGRESSED-G26 | table discriminating bytes + STOP that leg (finding, not failure — do NOT repair) |
| 4 | any R-G28-* fails (exit≠0 with Scudo signature; or `G28:` ×0 while supports=0; or new tombstone; or `corrupted chunk` in logcat) | REGRESSED-G28 | table discriminating bytes + STOP that leg (finding — do NOT repair) |
| 5 | all R-* pass but any N-* class differs | PERTURBED (valid behavior changed — not a defect return) | table + STOP (adoption blocked pending triage; no repair here) |
| 6 | O1/O3 lottery fires instead of first draw | VOID that leg | lottery note, no retry (both run slots are the two shapes — budget has no retry); the other leg still runs (independent) |
| 7 | exit 0 but scanouts ≠ black (content appears) | NOT a regression signal | table as a G40-relevant surprise (fixes hold; composite behavior moved — out of this gate) |

Correct-behavior alternative F0 ("the implementation is behaving
correctly on these inputs" — honored per scored observable):

| scored output | F0 prediction | discriminates? |
| --- | --- | --- |
| exit / fate | exit 0 + `Done!` + 10 scanouts + zero tombstone (fixes hold; cleared-from-stale-B correct per G33/G38) | F0 ≡ HOLD — NON-discriminated BY DESIGN (this gate proves hold, not mechanism) |
| black scanouts | black `99418f1b…` (stale-B render, G38 rule 4) | F0 ≡ HOLD — black-vs-black cannot split; only content (rule 7) would surprise, and it is not scored against the fixes |
| receipts R-G26-1/R-G28-1 | fire ×1 (delivery + guard execute) | F0 ≡ HOLD |
| REGRESSED arms (139/134, Scudo strings, tombstone, `success: no`) | absent | YES — any regressed signature differs from F0 and closes the leg |

### 2f. Binaries under test (REUSE — state which + pins + reason)

| binary | pins | intact? | verdict |
| --- | --- | --- | --- |
| G26 original (`parallel-gs-g26-android-build`) | 265,840,408 B, `811411816969b1f5…` FULL, ELF | YES (2 matching full-sha reads 12:08) | NOT VALID — predates the G28 guard (would exit 134: tests OLD source, not current HEAD) + predates G29–G31 witnesses (cannot witness N-* classes) |
| G28 original (`parallel-gs-g28-android-build`) | 265,841,104 B, `450471e2048b2a1d…` FULL, ELF | YES (restored since its G28 report-time destruction) | NOT VALID — predates G29–G31 witnesses (cannot witness N-* classes) |
| **G31 (`parallel-gs-g31-android-build`)** | **265,851,416 B, `c91719a0c96ef57a…` FULL, BuildID `c180f320…`, markers ×1/×2/×1/×1/×1/×1/×0/×0 (§2a)** | **YES (PASS1 + PASS2 + BuildID + strings + ELF)** | **VALID — REUSE. Reasons: (1) built from G31 source == current tree (G38 excision arithmetic 160−56=104 + G38 §3f fresh-vs-committed all-equal); (2) carries BOTH fixes under test (`G26:` ×1 + `G28:` ×1 strings-proven); (3) carries FULL witnesses (G31/G30/G29/G11/G10/G8) for every N-* class. ZERO builds.** |
| G32–G37 | various | — | NOT VALID — content-placement hunks (different source than current tree) |
| G38-mac | 51,898,120 B Mach-O | — | NOT VALID — wrong platform (reference leg only) |

Build budget: ZERO (a valid binary exists for both shapes — same
binary, same source; shapes differ only in shell redirect, §2g).

### 2g. Run shapes (quoted verbatim from the reports — do NOT redesign)

G26's narrow run shape (G26 REPORT §3b line 187; G26 §6 line 342):

```text
PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g26/g13-dump.gs --iterations 2 --disable-sampler-feedback
```

G28's writer run shape (G28 REPORT §3b line 174; G28 §6 line 313):

```text
PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g28/g13-dump.gs --iterations 2 --disable-sampler-feedback > g28-run-stdout.txt 2> g28-run-stderr.txt
```

G39 adaptations (content-neutral, brief-mandated): transient dir
`g26`/`g28` → `g39` (the brief's transient dir); stdout/stderr
filenames → `g39-r2-run-stdout/stderr.txt` (R2 leg). Nothing else
changes (same dump bytes, same iterations, same flag, same env,
no sanitizer, no G22 skip):

| leg | shape | command (cwd `/data/local/tmp/g39/`) |
| --- | --- | --- |
| R1 | G26 narrow | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g39/g13-dump.gs --iterations 2 --disable-sampler-feedback` |
| R2 | G28 writer | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g39/g13-dump.gs --iterations 2 --disable-sampler-feedback > g39-r2-run-stdout.txt 2> g39-r2-run-stderr.txt` |

Retrieval (explicit list per the G31-E1 rule — zero globs): R1:
logcat → `g39-r1-logcat.txt` + 10 PPMs → `r1-*` (pulled BEFORE R2
overwrites the device-side names); R2: logcat →
`g39-r2-logcat.txt` + stdout/stderr + 10 PPMs → `r2-*`. Tombstone
census pre + post (newest must stay G27's `_23`).

## 3. Task 2 — TWO bounded Odin runs (SAME shapes) + verdicts

### 3a. Knob matrix (identical to the G26/G28 demonstrations — the ONLY deltas are dir + binary generation)

| knob / flag | G26 §3a | G28 §3a | G39 R1 | G39 R2 | rationale |
| --- | --- | --- | --- | --- | --- |
| dump | `154d9d85…` | `154d9d85…` | `154d9d85…` (PASS1+PASS2+PASS3+on-device+report FULL-match) | same | same bytes |
| `--iterations 2` | SET | SET | SET | SET | same pass shape |
| `--disable-sampler-feedback` | SET | SET | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | KEPT | KEPT | same async-path control |
| sanitizer env | n/a | ABSENT | ABSENT | ABSENT | non-sanitizer shape |
| stdout/stderr redirect | ABSENT (verbatim) | PRESENT (verbatim) | ABSENT (verbatim G26) | PRESENT (verbatim G28) | the one shape delta, observationally neutral |
| binary | G26 `81141181…` | G28 `450471e2…` | G31 `c91719a0…` (current source) | same | current-HEAD regression needs current-source binary (§2f) |

### 3b. Verify chain with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (PASS3) | 12:11:30 | `c91719a0…` (binary) + `154d9d85…` (dump) FULL-match; G22/G28 HUNK_MATCH (pre-push) |
| device pre-check (read-only) | 12:11 | Odin3, Android 15, `/data/local/tmp/` == `mg/` only, newest tombstone `_23` (G27's), `/data` 28 G free — G38 pre-check exactly |
| device stage | 12:11 | `rm -rf` + `mkdir` + push dump (0.013 s) + push binary (2.170 s) into `/data/local/tmp/g39/` ONLY |
| on-device sha match | 12:11 | `154d9d85…` + `c91719a0…` BOTH FULL-match host — push→match gap ~0 s |
| R1 launch | 12:11 | `logcat -c` (verified empty: no Granite lines before) then run — no idle window |
| R1→R2 bridge | 12:11–12 | R1 logcat dumped + 10 R1 PPMs pulled (all `1 file pulled, 0 skipped`); device PPMs removed (`ls` → dump + binary only); `logcat -c`; R2 launched |
| R2 pulls | 12:12 | R2 logcat dumped + stdout/stderr + 10 R2 PPMs pulled (all 12 `1 file pulled, 0 skipped`); census: 10 scanouts sized, stdout/stderr 0 B, ZERO new tombstone |
| on-device post-run re-sha | 12:12 | `c91719a0…` FULL-match — intact |
| cleanup (OWN verified step, after pull verification) | 12:12 | `rm -rf` + `ls` → `mg/` only, exit 0 (DEVICE_CLEAN) |
| report-time re-sha | 12:12:40 | `c91719a0…` + `154d9d85…` FULL-match + ELF magic — intact, no zero-damage recurrence this window |
| HUNK_MATCH report-time | 12:14:11 | G22-OK + G28-OK + G26 ×1 (4/4: pre + pre-push + post-run + report) |

Identity gate: PASS1→PASS2→PASS3→on-device→post-run→report ALL
MATCHING (4 host sha reads + 2 on-device, plus BuildID + strings +
magic corroboration). No validity-chain pin mismatched at any gate:
rule 1 never fired.

### 3c. Run tables (R1 + R2 — both exit 0)

| item | R1 (G26 shape) | R2 (G28 shape) |
| --- | --- | --- |
| staging | `/data/local/tmp/g39/` ONLY; 2/2 on-device shas FULL-match host (§3b) | same staging (no re-push — post-R1 device state verified, bridge §3b) |
| exit / wall | **0** / ~0 s (`date` 1790093503→1790093503; logcat 12:11:43.1→12:11:43.7) | **0** / ~1 s (`date` 1790093521→1790093522; logcat 12:12:01.4→12:12:02.5) |
| FIX receipt | `G28: … skipped (supports=0, feature=1).` ×1 | ×1 (same bytes) |
| NARROWING receipt | `G26: … (=1, =0, =0).` ×1 | ×1 (same bytes) |
| knob receipts | `Skipping precompilation…` ×1; `Failed to load RenderDoc` ×1; 0 `G22: skipping` | same ×1/×1/0 |
| logcat | 2360 lines (== B0/B1 exactly): init + 18 `Running frame` + 18 G10 + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 8.239 ms` + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk` | 2360 lines, same classes; `Total time 8.385 ms` (timing-only delta, informational) |
| fate | clean exit 0 through Device teardown | clean exit 0 through Device teardown |
| outputs | 10 scanouts × 688,143 B; ZERO new tombstone (newest still _23) | 10 scanouts × 688,143 B + stdout/stderr 0 B; ZERO new tombstone |

R1-vs-R2 stripped-logcat diff: 2351/2360 lines identical; the 9
differences are 8 Stalled-compile microsecond timings (same 8
hashes incl. graphics `e5825dd1…`, all `success: yes`) + the
Total-time ms — all pre-registered informational (§2d). The shell
redirect is behaviorally neutral, as designed.

### 3d. Regression verdicts (per fix, both runs scored)

| id | R1 | R2 | verdict |
| --- | --- | --- | --- |
| R-G26-1 (receipt `=1,=0,=0`) | ×1 exact | ×1 exact | PASS |
| R-G26-2 (warm `img=` 0×8) | 0×8 (`img-tail8` all `0`); cold residue `1966080/28672/0/327680/0/0/0/0`-class | 0×8; same cold shape | PASS |
| R-G26-3 (O4 absent, 4 legs) | (1) exit 0 + full loop + `Done!`; (2) 8/8 `success: yes` + 0 `success: no`; (3) `dispatch_texture_analysis` ×0, `vkCreateComputePipelines` ×0; (4) clean teardown | same 4/4 | PASS |
| R-G28-1 (guard engaged) | ×1 `supports=0, feature=1` | ×1 same | PASS |
| R-G28-2 (exit 0 + `Done!` last + 10 scanouts + zero tombstone) | 0 + last + 10 + newest _23 | 0 + last + 10 + newest _23 | PASS |
| R-G28-3 (0 Scudo + 0 ERROR/LOGE) | 0 `corrupted chunk`; only pre-existing RenderDoc noise | same | PASS |

Per-fix verdict: **G26 HOLDS** (all R-G26-* PASS in its own R1 shape
+ cross-witnessed in R2) and **G28 HOLDS** (all R-G28-* PASS in its
own R2 shape + cross-witnessed in R1). Rules 3/4 never fired (no
regressed signature anywhere); rule 6 never fired (no O1/O3);
rule 7 never fired (scanouts black, §3e).

### 3e. No-perturbation verdicts (byte-equal to adopted baselines)

`g39-score.py` (mirrored; one self-bug — a doubled regex escape in
a display-only line — caught by the empty `vals` output, fixed,
re-verified via direct grep §3d):

| class | R1-vs-B0 | R1-vs-B1 | R2-vs-B0 | R2-vs-B1 |
| --- | --- | --- | --- | --- |
| FRAME 32 | eq | eq | eq | eq |
| RECORD 64 | eq | eq | eq | eq |
| TEX 1552 | eq | eq | eq | eq |
| FLUSH 16 | eq | eq | eq | eq |
| G10 18 (scratch/img-normalized) | eq | eq | eq | eq |
| STATE 16 | eq | eq | eq | eq |
| BYTES 16 | eq | eq | eq | eq |
| VPAGE 512 | eq | eq | eq | eq |
| LADDER 10 | eq | eq | eq | eq |
| VRAM 1 | eq | eq | eq | eq |
| WROTE 10 (basename-normalized: run dir differs) | eq | eq | eq | eq |
| RUN 18 | eq | eq | eq | eq |

48/48 class comparisons EQUAL. Scanouts: 20/20 black `99418f1b…`
unanimous (== B0's unanimous sha; equality via full-sha match).
B-bytes == load `eea04488…`/149721 ×16 both runs (the Odin
rule-3/4 expectation — G40's territory, unchanged). stdout/stderr
0 B (R2 shape). Logcat length 2360 == B0/B1 exactly (both runs).

No-perturbation verdict: **UNPERTURBED** — rule 5 never fired. F0
note: every scored observable matches F0's predictions byte-exactly
(exit 0, black, receipts fire, regressed arms absent) — HOLD and F0
remain non-discriminated by design (§2e); the gate proves hold, not
mechanism, and no observation in this gate contradicts
correct-behavior.

### 3f. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| retry | NOT USED (no budget) | Both run slots are the two shapes by brief design; in any case both runs exited 0 with the full loop + `Done!` — no retry condition fired |
| second shape per fix | NOT USED | out of budget by the stop rule (each fix tested once in its own shape; cross-witnessing is corroboration, not a second shape) |
| lldb triage | NOT USED | zero new tombstone, both exit 0 — nothing to triage |

## 4. Hypothesis verdict + adoption-mechanics recommendation + the ONE next action

| claim | verdict |
| --- | --- |
| Each fix still holds its defect closed on current HEAD (G26: receipt + warm `img=`=0 + O4 absent; G28: engaged receipt + exit 0 + `Done!` + 10 scanouts + zero tombstone + zero Scudo) while every valid-behavior observable stays byte-equal to its adopted baseline | **CONFIRMED, decisively.** R1 (G26 shape) + R2 (G28 shape) both exit 0 with all 6 regression observables PASS (§3d — G26 HOLDS, G28 HOLDS) and all 12 no-perturbation classes EQUAL vs BOTH baselines (48/48, §3e — UNPERTURBED): 20/20 scanouts black `99418f1b…`, B==load ×16, zero new tombstone. Zero hunks, zero excisions, zero builds, zero commits anywhere; HUNK_MATCH 4/4; identity chain 4+2 matching sha reads (+ BuildID/strings/magic); all byte caps PASS (§0). Retry + lldb correctly unspent (§3f). |

### 4a. Adoption-mechanics RECOMMENDATION (recommend — do NOT execute; orchestrator decides)

Scope (pre-registered): G26 + G28 ONLY. Out of scope: G22
(env-gated workaround — unset in every run here, needs its own
gate), G29–G31 observation hunks (diagnostic, never adoption
candidates), G18 (separately queued), G24 (superseded).

| mechanics | shape | risk | rollback |
| --- | --- | --- | --- |
| A. carried-diff (RECOMMENDED now) | Keep both hunks UNCOMMITTED in the SSD clone worktrees (G26 in `parallel-gs-g7`, G28 in its Granite submodule); the ssx3-committed diff texts (`g26-narrowing.diff`, `g28-writer-fix.diff`) + this gate's regression proof are the durable record | worktree fragility: a stray `checkout -- .` / re-clone drops the fixes (mitigated: re-apply is 2 files from ssx3; HUNK_MATCH re-verifies byte-exact); SSD-corrupt-path reads keep the standing 2-read rule (unchanged) | trivial: `git checkout -- <files>` restores HEAD; re-apply from ssx3 diffs |
| B. in-clone commit (DEFERRED until storage cutover) | Fix-only commits: 1 in Granite (guard + receipt) + 1 in `parallel-gs-g7` (narrowing), diagnostics stay uncommitted; submodule pointer + superproject bookkeeping per the owner's tree layout | committing onto the PROVEN-corrupt path buys NO durability (objects need mirror+verify anyway) while breaking the lane's zero-commit invariant mid-stack and complicating the active diagnostic worktree (G29–G31 uncommitted around the fix files); false-durability hazard if objects are trusted before the cutover | `git revert` per commit (once committed post-cutover) |

Recommendation: **A now, B after the storage cutover.** Rationale:
(1) durability already holds — the fix texts live in ssx3 git on
the internal volume (pushed by the orchestrator), hash-pinned and
HUNK_MATCH-verified against the worktree 4× this brief; (2) an
in-clone commit today would land its objects on the corrupt link
without changing any trust boundary (the standing 2-read rule
would still apply to every lane-critical byte); (3) the lane's
zero-commit invariant has held G18→G38 deliberately — breaking it
mid-diagnostic-stack (G29–G31 uncommitted, G40 queued) adds
pointer/bookkeeping churn for zero evidence gain. Revisit B as the
first commit(s) on the verified path once the cutover lands (the
review's track 1): fix-only, diagnostics excluded, with a clean-tree
rebuild + this gate's R-shapes re-run as the commit's own proof.

Neither mechanics was executed: zero commits in submodule, zero in
ps2xGS (verified §0/§3b). The orchestrator decides.

The ONE next action the numbers justify: **G40 — the sub-vsync
F1/F2/F3 wall at boundary 1** (B pre/post-composite-flush reads +
flush reason + draw-accept logging, observation-only, no
injection), per G38 §4. Rationale: this gate closes adoption-proof
for the crash fixes (HOLD-both, UNPERTURBED) without touching the
composite question; B==load ×16 re-confirmed here keeps G38's rule-4
localization ("composite#1+ writes never land in B on Odin")
current, and F1/F2/F3 remain unsplit at vsync granularity. Queued
behind it (not this action): adoption execution per the
orchestrator's mechanics call; the Adreno filing — STILL OPEN
regardless (needs user identity/tracker; content must drop the
sampling inference per the review); G18-hunk adoption (still
queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption execution,
no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture set + G28 writer-fix hunk compiled into the reused binary (guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22/G28 HUNK_MATCH 4/4; G26 block line-identical) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G37 shrunken-tag hunk | stays EXCISED (diff text survives committed in `local/research/G37/` — lossless) |
| G39 additions | ZERO source hunks + session files: `g39-run-r1.sh` + `g39-run-r2.sh` + `g39-score.py` (G39-original, text, mirrored) |
| NDK r30 | `llvm-readelf` use only (Apache-2.0); no builds, no runtimes staged |
| logcat/scanouts | run receipts of our own binary in SSD `ps2x-g39/` ONLY (not in git) + share-tier mirror; no PII (device shell user) |
| host analysis | `g39-score.py` + inline grep/python census (session commands; no new dumps) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief; no adoption executed |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, 5 files + ? spirv-tools)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (4/4)
git -C $SSD/parallel-gs-g7/Granite diff vulkan/memory_allocator.cpp | diff local/research/G28/g28-writer-fix.diff -  # HUNK_MATCH (4/4)
git -C $SSD/parallel-gs-g7 diff tools/gs_dump_replayer.cpp | grep -A20 '93,9 +96,15'  # vs g26-narrowing.diff: line-identical
grep -c 'G31: state|G31: bytes|G29: ladder|G29: vram|G30: vpage|G37: writeback' $SSD/parallel-gs-g7/gs/*.cpp $SSD/parallel-gs-g7/tools/*.cpp  # §2a markers
git -C /Users/bradrichardson/dev/ps2xGS rev-parse HEAD ; status --short   # fd781ef clean
du -sk $SSD/ps2x-g* $SSD/parallel-gs-*-build ; df -h / $SSD               # §0 (pre 12:08:06 + post 12:12:48)
shasum -a 256 <g31-binary> (PASS1 12:08:15 + PASS2 12:08:53 + PASS3 12:11:30 + report 12:12:40)  # c91719a0… x4 FULL-match
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs (x4, same gates)                  # 154d9d85… x4 FULL-match
shasum -a 256 <g26-binary> <g28-binary>                                   # 81141181… + 450471e2… FULL-match (intact, §2f)
llvm-readelf --notes <g31-binary> ; strings grep x1/x2/x1/x1/x1/x1/x0/x0 ; xxd -l 4  # c180f320… + ELF
ls $SSD/ps2x-g38/ ; ls /Volumes/share/ssx3/ps2x-g38/ ; wc -l g38-odin-logcat.txt  # B0 present (28 + 28 + 2360)
mkdir -p $SSD/ps2x-g39                                                     # §3b
adb -s 622c49b1 logcat -d -s Granite:V > $SSD/ps2x-g39/g39-r1-logcat.txt  # R1 2360 lines
adb -s 622c49b1 logcat -d -s Granite:V > $SSD/ps2x-g39/g39-r2-logcat.txt  # R2 2360 lines
adb -s 622c49b1 pull <each of 10 R1 PPMs by explicit name> r1-*.ppm       # §3b (all 1-file-pulled; NO glob)
adb -s 622c49b1 pull g39-r2-run-stdout/stderr.txt + <10 R2 PPMs by name>  # §3b (all 12 1-file-pulled)
python3 local/research/G39/g39-score.py                                   # §3e (48/48 eq; R-* table)
grep -h 'G26: debug_mode delivered' g39-r1-logcat.txt g39-r2-logcat.txt   # R-G26-1 (=1,=0,=0 x1 each)
shasum -a 256 $SSD/ps2x-g39/r1-*.ppm $SSD/ps2x-g39/r2-*.ppm                # §3e (20x 99418f1b…)
grep -c Skipping/RenderDoc/G22 <logcats> ; R1-vs-R2 stripped diff         # §3c census (9 timing-only diffs)
rm -f $SSD/ps2x-g39/._* ; du -sk $SSD/ps2x-g39 ; ls $SSD/ps2x-g39 | wc -l  # 23552 KiB, 24 files
cp <24 receipts> /Volumes/share/ssx3/ps2x-g39/ ; shasum -c                # mirror ALL OK
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g39/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g39 && mkdir -p /data/local/tmp/g39'
push <dump> $G39DIR/g13-dump.gs ; push <g31-binary> $G39DIR/parallel-gs-replayer  # §3b
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3b)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before R1 (empty)
shell 'cd $G39DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G39DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback; echo RUN_EXIT=$?; date +%s'  # R1 0 (G26 shape)
shell 'ls -la $G39DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts; ZERO new tombstone
shell 'cd $G39DIR && rm -f <10 R1 PPM names> && ls'                  # bridge (dump + binary only)
logcat -c                                                            # before R2
shell 'cd $G39DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G39DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g39-r2-run-stdout.txt 2> g39-r2-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # R2 0 (G28 shape)
shell 'ls -la $G39DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts + 0-B pair; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # c91719a0… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g39 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. Adoption is RECOMMENDED, not executed (orchestrator decides per
   §4a — carried-diff now, in-clone commit after cutover; zero
   commits made anywhere by this brief).
2. G22's env-gated workaround is un-regressed (unset in both shapes
   by verbatim design — needs its own gate with the knob SET if
   adoption is ever sought).
3. The G26 exit-134 arm (D-G26-2) is not reproducible on the current
   tree without excising G28 (forbidden) — tabled as historical
   receipt (§2b note), not re-demonstrated.
4. `g14-diff.py` did not run (reference PPMs are load-source
   renders; N/A by design — B0/B1 are this gate's oracles and the
   full-sha scanout comparison closed without it; same call as G38
   gap 4).
5. The scorer's one self-bug (doubled regex escape, display-only)
   was fixed in the mirrored script; the R-G26-1 values rest on
   direct grep (§3d), not the fixed line alone.
6. G29-E1 carried (explicit pull lists, zero globs, separate
   cleanup — applied on both legs); G29-E2 carried (push-time +
   post-run + report-time re-shas — binary intact at every gate).
7. F1 vs F2 vs F3 UNSPLIT (G40's wall — explicitly OUT here).
8. The Adreno filing is still open and unfiled (needs user identity
   / tracker — unchanged owner; content must drop the sampling
   inference per the review).
9. The `? third_party/spirv-tools` untracked Granite entry is tabled
   content-neutral (pre-existing; untouched).
10. No lldb (decision tabled §3f); OS tombstone store untouched (no
    new tombstone this brief). `upstream/` + harness code untouched;
    no new dumps; run budget 2/2 spent (both shapes, as designed).
11. Internal `/tmp/g39-shas.txt` (~2 KB) is session-only (kept for
    re-verification, outside the repo).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g39/` (24 files:
  `g39-r1-logcat.txt` + `g39-r2-logcat.txt` 2360 lines each (16
  `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` + 10 `G29:
  ladder` + 1 `G29: vram` each), `g39-r2-run-stdout/stderr.txt`
  0 B, 10 R1 PPMs + 10 R2 PPMs × 688,143 B (black `99418f1b…`
  unanimous)) — no build dir (ZERO builds).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g38/` + all
  build dirs + SSD clone (HEAD `3a66c19…`, G22 + G26 + G29 + G30 +
  G31 hunks uncommitted; Granite `16e7395f…` + G20-capture set +
  G28 hunk, all uncommitted — ZERO commits anywhere).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g39/` (24/24 files,
  `shasum -c` ALL OK).
- Session-only: `/tmp/g39-shas.txt` (~2 KB).
- Commits: ssx3 `local/research/G39/` `[G39]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G39 report ends here. Task-1 statics tabled per-fix
defect receipts (G26/G28 line numbers) + regression observables
(exact bytes) + no-perturbation observables (B0 G38-O1 primary, B1
G31 cross-check) + HOLD/REGRESSED/PERTURBED matrix with F0 honored;
worktree == G38 end state (gate proceeds, ZERO hunks/excisions);
G31 binary reused (ZERO builds); TWO Odin runs (R1 G26-shape + R2
G28-shape) both exit 0 with all R-* PASS and 48/48 N-* classes
EQUAL + 20/20 black scanouts — HOLD-both, UNPERTURBED;
adoption-mechanics RECOMMENDED (carried-diff now, in-clone commit
after cutover — orchestrator decides, nothing executed); G40 queued;
filing still open.

Outcome: rule 2 — HOLD-both (all R-G26-* + all R-G28-* + all N-*
match on both runs). No tuning loop was entered: zero hunks, zero
excisions, zero builds, two bounded runs. Retry not used (no retry
budget — both slots are the shapes); lldb not used (zero new
tombstone — nothing to triage).
