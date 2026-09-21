# G28 report — Writer fix verified: guarded `create_image_view` branch, exit 0, O5/O6 gone, black persists as a separate trait (Odin)

Brief: G28 (this turn) — executes G27 §4's ONE next action ONLY: gate
`create_image_view`'s descriptorBuffer branch
(`Granite/vulkan/memory_allocator.cpp:1424`) on
`supports_descriptor_buffer_or_heap`, rebuild (non-sanitizer), ONE bounded
WITH-FLAG verification run expecting exit 0. Tables + hypothesis + next-action
recommendation, no verdicts beyond the hypothesis. Time box 6 h (used ~0.3 h
— measured wall 16:02:48→16:20 EDT; dir snapshot → commit, plus ~2 min
pre-snapshot reading/pins). Read first per the brief: `local/research/G27/
REPORT.md` (all of it: HWASan names the writer — stride-0 storage-image slab
+ unguarded use branch + driver's 64-byte `vkGetDescriptorEXT` write, 5
convergent links + on-device `MISMATCH=1`). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local; filing
content upgrades per G27 §4 + this brief's verification, filing itself still
needs user identity/tracker).

Machine: same as G8–G27 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g28/`
ONLY; removed at end (`mg/` only).

Headline result: the writer fix VERIFIES. (1) ONE hunk in the Granite
submodule worktree (guard + once-LOGI receipt, UNCOMMITTED there; diff text
committed beside this report): the `:1424` branch now requires
`supports_descriptor_buffer_or_heap`, the guard `init()` and every sibling
path already carry. Guard-choice + no-new-hazard reasoning tabled (§2b). (2)
ONE build (G22 recipe, `-j2`, non-sanitizer), exit 0 `[458/458]`, full
identity (NEW size/sha/BuildID, `G28:` ×1, G26 strings ×1/×2/×0). (3)
Verify-then-push with NO gap (host re-sha → push → on-device FULL-match →
run). (4) ONE flag run: **exit 0**, `Done!` last line, 10 scanouts, ZERO new
tombstone — O5/O6 gone. The `G28:` receipt fired exactly once (guard engaged
on-device, supports=0/feature=1 as predicted). (5) The three discriminations
(§3g): single-writer family CONFIRMED; scanouts still pure BLACK —
byte-identical to G27's black (G27 §3i aliasing link REFUTED, black is a
separate device trait); O4 absent (4-leg proof, streak extends). The G28
binary was zero-destroyed post-run (7th recurrence, tabled — run validity
unaffected: 3 matching pre-run reads + on-device match).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g28-android-build` | 6 GB | 4,482,048 KiB (== G26 dir scale) PASS |
| NEW SSD `ps2x-g28/` (retrieval: logcat + stderr/stdout + 10 PPMs) | 50 MB | ~7.0 MB apparent; 25,600 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g27` + G14/G15/G16/G18/G20/G22/G24/G26/G27 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g15 31744, g16 43008, g18–g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24–g26 5120, g27 28672; g14-build 4480000, g15-hwasan 4816896, g16-asan 4577280, g18/g20/g22/g24/g26-build 4482048, g27-hwasan 4817920 KiB) PASS |
| SSD clone (source) | ONE hunk max (the Granite guard + ≤1 LOGI) | ONE hunk in Granite worktree (guard + once-LOGI), UNCOMMITTED there; G22 + G26 hunks untouched (HUNK_MATCH re-verified pre-hunk); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 8.9 Gi avail before → 9.3 Gi after (other-lane delta); G28 `/tmp` residue ~4 KB (2 block-compare files) PASS |
| SSD volume | — | 189 Gi avail before → 177 Gi after (new build dir + retrieval; remainder other-lane) |
| device | `/data/local/tmp/g28/` ONLY | staged 2 files, pulled 13, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (verification + retry iff O1/O3) | ONE verification run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Gating `create_image_view`'s descriptorBuffer branch on `supports_descriptor_buffer_or_heap` removes the G27-named heap writer: the ONE WITH-FLAG verification run exits 0 with `Done!` + 10 scanouts + no tombstone, and the `G28:` skip receipt fires (guard engaged on-device) |
| observable signal | guard-choice table + hunk diff + build exit/sha/build-id + verify-then-push chain (host re-sha → push → on-device match, no gap) + ONE bounded flag run (exit/wall/fate + `G28:`/`G26:` receipts + knob receipts + tombstone census) + scanouts scored (`g14-diff.py` + pixel census) + O4 legs + the three discrimination verdicts |
| alternatives | (a) exit 0 + receipt => writer fixed, single-writer family confirmed; black-vs-bright discriminates the aliasing link; (b) still crashes => full tombstone triage + writer-family revision; (c) exit 0 but no `G28:` receipt => guard never engaged, fix unproven on-device; (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ONE hunk max (guard + ≤1 LOGI); ONE build (new dir); TWO bounded device runs max (verification + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: alternative (a) — exit 0 with the receipt firing once, O5/O6 gone,
O4 absent, scanouts black-but-identical-to-G27. No tuning loop was entered:
one hunk, one build, one device run. Retry not used (exit 0 — no retry
condition); lldb not used (nothing to triage — zero new tombstone).

## 2. Task 1 — hunk + build + verify-then-stage (no run until §3)

### 2a. Pin verification (pre-work — G27 §2a reproduced, ZERO edits before the hunk)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G27 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 39, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 116 (179+/4-) — G26 end state (G22 + G26 + pre-existing G8/G10/G11/G18 blocks) |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | worktree `@@ -93,9 +96,15 @@` block line-identical to committed `g26-narrowing.diff` (HUNK_MATCH; the live diff's 16th line `}` is trailing context the committed file trimmed — all 15 captured lines match) |
| Granite submodule | HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (== pin); pre-existing diffs in 4 files ONLY (platforms/CMakeLists 4, timer 11, command_buffer 18, shader 8 = G20-capture set, 39+/2-); `memory_allocator.cpp` pristine pre-hunk |
| G24 | stays SUPERSEDED (no G24-shaped code in tree; diff text survives in `local/research/G24/`) |
| G27 binary (6th zero-damage recurrence, persisting) | 289,112,232 B, mtime frozen 15:34 (G27's build), sha `13d2fc69…` (zeros), magic `0000` — still destroyed, as left by G27; tabled, not rebuilt (superseded binary, out of scope) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G27 §0 exactly (see §0, snapshot 16:02:48); post-run re-verified §0 |
| recipe | NDK r30 (`/opt/homebrew/share/android-ndk`); cmake + ninja; G22/G26 non-sanitizer flags (no `ANDROID_STL` override, no sanitizer) |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's O6-site sanitizer abort, 15:35); `/data` 28 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 8 vsync PPMs |

### 2b. Guard choice (tabled BEFORE editing — exactly one shape picked)

| shape | change | verdict |
| --- | --- | --- |
| A. Gate the `:1424` condition on `supports_descriptor_buffer_or_heap` (+ once-LOGI skip receipt) | 1 condition line + 1 receipt `else if` block (18+/1-, all in `create_image_view`) | **CHOSEN** — one-line-class fix mirroring the sibling guards (`:1488`, `sampler.cpp:139`, `descriptor_set.cpp:488/:570`); guarded-false path is the long-tested plain-`VkImageView` path |
| B. Initialize the slabs unconditionally + fall back cleanly | touches `init()` + alloc paths + teardown + range sizing | REJECTED — larger blast radius (new allocation behavior on a 128 KiB-range device), violates the minimal-hunk rule; strictly more new-hazard surface for the same on-device outcome |

No-new-hazard reasoning (shape A):

| hazard question | answer |
| --- | --- |
| What runs when the guard is false? | The pre-existing non-descriptorBuffer path: `view.view` was already created above (`:1323-1326`), the descriptor block is skipped, `return true` — the exact state every non-DB device already produces and every consumer already handles |
| Does `supports == true` behavior change? | No: the added conjunct is a true literal there, so the branch condition is unchanged — byte-identical behavior on all devices that initialize slabs |
| Is the `heap` branch above affected? | No: `heap == true` ⟹ `supports == true` (`context.cpp:2287-2288`), so the heap path always runs with initialized slabs, before and after |
| Are the sibling paths consistent? | Yes: sampler / descriptor-set / buffer-view / device paths ALL already branch on `supports_descriptor_buffer_or_heap` — the hunk joins the consistent family instead of creating a mixed mode |
| Is the LOGI receipt safe? | Yes: `LOGI` is already used twice in this file (no new dependency); the `static bool` once-guard is idempotent under threads (worst case: the line prints twice); it fires only when the skip is real (see detector row) |
| Does the receipt detector prove the skip? | Yes: reaching the `else if` means `!(supports && feature && need_view)`; conjoining `(need_view && feature)` leaves `!supports` — the receipt fires ⟺ the guard skipped a would-be writer call |

Hunk written 16:04:03 (Granite worktree, UNCOMMITTED — G20-capture-hunk
precedent; zero commits in submodule, zero in ps2xGS). Full diff text in
`g28-writer-fix.diff` beside this report (1,770 B, two `@@` blocks).

### 2c. Full hunk state (this brief adds at most the ONE Granite hunk)

| site | state |
| --- | --- |
| ps2xGS top-level (uncommitted, 0 commits) | G22 HUNK_MATCH + G26 HUNK_MATCH + pre-existing G8/G10/G11/G18 blocks — tested shape stays flag-only, untouched |
| Granite `memory_allocator.cpp` (uncommitted, 0 commits) | **G28: 18+/1- (the ONE new hunk)** |
| Granite other 4 files (uncommitted, 0 commits) | G20-capture set as before (39+/2-), untouched |

### 2d. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G26 recipe, `g28-build.sh` mirrored): exit 0
(`Configuring done (16.5s)`, `Generating done (8.9s)`,
`Processor: aarch64`), 16:04:21. Build `cmake --build … --target
parallel-gs-replayer -j2`: exit 0 (`[458/458]`, 16:04:56→~16:13).

| item | observed |
| --- | --- |
| warnings | pre-existing `-Wshadow` (`FileDeleter`, `gs_dump_parser.hpp:49` — same class/file as G22/G24/G26/G27); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,841,104 B (+696 vs G26's 265,840,408 — the hunk; NEW size expected) |
| sha (build-time, 16:14:03) | `450471e2048b2a1db406ebf1e52dbc44ef3dba48c566eba1bb070d45153f9705` (NEW — expected; all later pre-run reads must match THIS) |
| build-id | `53af7a56618d58af38429b12cff81a1ceb6ac1a9` (distinct from G26 `2e946006…` and G27 `52977886…`) |
| plumbing presence | `strings` grep: `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24: debug_mode delivered` ×0 (fix + narrower hunk in the binary) |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 2e. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 16:14:44 | `450471e2…` (binary) + `154d9d85…` (dump) FULL-match build sha (41 s after identity — no zero-damage window) |
| device stage | 16:14:45–47 | `rm -rf` + `mkdir` + push dump (0.016 s) + push binary (2.042 s) into `/data/local/tmp/g28/` ONLY |
| on-device sha match | 16:14:47 | `154d9d85…` (dump) + `450471e2…` (binary) BOTH FULL-match host — push→match gap ~0 s |
| run launch | 16:14:54 | `logcat -c` (verified: only `beginning of main` before) then run — on-device match→run gap 7 s, no idle window |
| report-time re-sha | 16:16:06 | `3a11581e…` MISS + ELF magic `0000` (size/mtime frozen) — **7th zero-damage recurrence**, ~2 min post-push; run validity UNAFFECTED (3 matching pre-run reads + on-device match; destruction came after the completed run) |

Identity gate: build→pre-push→on-device ALL MATCHING (3 host reads +
2 files on-device). The zero-destroyer fired inside this brief's window but
AFTER the run, not inside the verify-then-push chain.

## 3. Task 2 — ONE verification run + score + three verdicts (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G26's run is the fixed binary)

| knob / flag | G26 setting | G28 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape (flag-only hunk in tree) |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env (`HWASAN_OPTIONS`, `LD_LIBRARY_PATH`) | n/a | ABSENT | non-sanitizer fix-verification shape (G27-only knobs) |

Predicted discriminators: `G28: …skipped…` receipt (guard engaged) +
`G26: …disable_sampler_feedback=1…` receipt + exit 0 with `Done!` + no
tombstone.

### 3b. Run table (ONE run — retry not used, §3h)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g28/` ONLY; dump + fixed binary pushed; 2/2 on-device shas FULL-match host (§2e); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g28/g13-dump.gs --iterations 2 --disable-sampler-feedback` (stdout→file, stderr→file; `g28-run.sh` mirrored) |
| exit / wall | **0** (clean — the predicted outcome) / ~1 s wall (`date` 1790021695→1790021696; logcat 16:14:55.6→16:14:56.2) |
| FIX receipt | line 24 `G28: create_image_view descriptorBuffer branch skipped (supports=0, feature=1).` (×1 — once-guard held; guard ENGAGED on-device exactly as G27 predicted) |
| NARROWING receipt | line 30 `G26: debug_mode delivered (disable_sampler_feedback=1, feedback_render_target=0, use_rdoc=0).` (×1) — ONLY the flag delivered |
| knob receipts | `Skipping precompilation…` ×1 (async knob effective); `Failed to load RenderDoc` ×1 (benign as ever); 0 `G22: skipping` (knob unset, as designed) |
| logcat | 1805 lines (== G27's 1804 + 1 = the `G28:` receipt line exactly): init + ext list (`VK_EXT_descriptor_buffer` enabled) + 18 `Running frame` + 18 G10 lines (BOTH iterations complete) + 8 Stalled posts, all `success: yes` + `Total time per VBlank: 1.847 ms` (non-sanitizer speed vs G27's 7.743, cf. G26's 1.810) + 10 `G8: wrote … scanout` + `Done!` as the LAST line; 0 `success: no`; 0 ERROR/LOGE; 0 `corrupted chunk` |
| behavioral narrowing | warm-pass `img=`: 0/0/0/0/0/0/0/0 (== G26's 0×8 — feedback writes gone; the G27 8192-residue line was HWASan-layout-only); cold pass keeps first-touch residue (1966080/28672/0/327680/0/0/0/0 — same shape as G27's cold pass, layout-dependent values) |
| fate | NOT O1/O2/O3 (full loop completed); NOT O4 (proof §3e); NOT O5/O6 (no Scudo signature anywhere, no death at all) → **clean exit 0 through Device teardown** |
| device outputs | 10 scanouts (vsync0–7 + first + last, 688,143 B each); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23, G27's); device dir removed after (`mg/` only ✓) |

### 3c. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g28` (tool exit 0): oracles **ALL OK** (8/8
pixel-shas); device PPMs: **10** (vsync0–7 + first + last):

| k | exact | \|d\|≤2 | \|d\|≤32 | PSNR R/G/B (dB) |
| --- | --- | --- | --- | --- |
| 1 | 0.0000 | 0.0000 | 0.0000 | 1.9 / 2.4 / 33.1 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 1.1 / 1.5 / 32.3 |
| 3 | 0.0000 | 0.0000 | 0.0000 | 0.4 / 0.8 / 31.2 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 5 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 6 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |
| 7 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |

The table is value-identical to G27 §3i — the fix moved heap behavior
(exit 134→0) without moving a single pixel.

### 3d. Pixel census (bright vs black — BLACK, byte-identical to G27)

All 10 device scanouts: mean 0.0,0.0,0.0, 0/688,128 nonzero bytes, identical
file sha `99418f1b…` — pure BLACK, vs BRIGHT oracles (means ~200+).
Cross-brief: `cmp` of G28 vsync0 vs G27 vsync0 = BYTE-IDENTICAL (same
`99418f1b…` sha). G22's no-flag device scanouts are likewise pure black —
flag, no-flag, sanitizer, and fixed runs all agree on-device (black), and
all differ from the bright mac oracles.

### 3e. O4-absent proof (four legs, G24/G26/G27 §3h shape — flag efficacy holds)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal differs | exit 0 clean, full loop + scanouts + `Done!`, vs O4's 139/SIGSEGV first-draw death |
| 2 | crashing input never exists | crasher pipeline/shader hashes logged 0×; 8/8 Stalled posts `success: yes`, 0 `success: no` |
| 3 | no death, no driver-compile frames anywhere | ZERO new tombstone (no death at all); logcat 0 ERROR/LOGE; `dispatch_texture_analysis`/`vkCreateComputePipelines` absent |
| 4 | clean teardown | process exited 0 normally through `Device` teardown (the phase that killed O5/G27-runs) — no abort, no signal |

O4 is absent (the flag-set absent streak extends: G24 + G26 + G27 + G28 at
value-1 vs G25 + G23r2 at value-0/dropped — the bidirectional A/B stands).

### 3f. O5/O6 wall census (three detection sites, one writer — now silent)

| signature | phase | detector | status after G28 |
| --- | --- | --- | --- |
| O6 (G24/G26) | pre-first-write | Scudo `corrupted chunk header` | GONE: full loop + all 10 writes + `Done!` + clean exit; 0 `corrupted chunk` in logcat |
| O5 (G22) | post-`Done!` teardown | Scudo `corrupted chunk header` | GONE: teardown completed, exit 0, no tombstone |
| G27 (HWASan naming) | post-`Done!` teardown | HWASan `allocation-tail-overwritten` | GONE by construction (non-sanitizer binary) AND by fix (no Scudo signature in its place — the writer no longer writes) |

### 3g. The three discrimination verdicts (G27 §4's three questions)

| # | question | verdict |
| --- | --- | --- |
| 1 | O5/O6 gone => single-writer family confirmed? | **CONFIRMED.** Exit 0 through the exact phases that killed O5 (teardown), O6 (pre-first-write), and G27 (teardown detection), with the `G28:` receipt proving the guard engaged — one writer, three layout-dependent detection sites, all silent |
| 2 | Scanouts BRIGHT (aliasing caused the black) vs still BLACK (separate device trait)? | **Still BLACK => SEPARATE DEVICE TRAIT.** Byte-identical black to G27 (§3d) with the writer demonstrably fixed: G27 §3i's hypothesis-level aliasing link is REFUTED. Black needs its own diagnosis (next wall) |
| 3 | O4 legs (expect absent — flag kills it bidirectionally)? | **ABSENT** (§3e, 4 legs) — streak extends, A/B stands |

### 3h. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + `Done!`; there is nothing to retry |
| second shape | NOT USED | out of budget by the stop rule (fix verified on the first run — no second shape needed) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Gating `create_image_view`'s descriptorBuffer branch on `supports_descriptor_buffer_or_heap` removes the G27-named heap writer: the ONE WITH-FLAG run exits 0 with `Done!` + 10 scanouts + no tombstone, and the `G28:` receipt fires | **CONFIRMED, decisively.** Exit 0 (§3b) with `Done!` last + 10 scanouts + ZERO new tombstone; `G28:` receipt ×1 (guard engaged on-device, supports=0/feature=1 as predicted); `G26:` receipt ×1 (flag-only shape); 0 ERROR/LOGE, 0 `corrupted chunk`. O5/O6 gone (§3f — single-writer family confirmed); O4 absent (§3e — A/B stands). Pixels SCORED: black, byte-identical to G27 (§3c–§3d — aliasing link refuted, black is a separate trait). One hunk, one build, one device run; retry + lldb correctly unspent (§3h). |

The ONE next action the numbers justify: **a black-scanout diagnosis brief
(the next wall) — NOT adoption.** Rationale: G27 §4 conditioned adoption of
the G26 narrower hunk on "exit 0 + brightness agree" — exit 0 agrees but
brightness does not (byte-identical black with the writer demonstrably
fixed), so adoption stays queued and the black needs its own experiment
(first discriminations: readback-path vs render-path — e.g. whether the
zeros originate in the swapchain/offscreen readback or the rendered target;
device-trait candidates given flag/no-flag/sanitizer/fixed all agree
on-device). Queued behind it (not this action): G26+G28 adoption once
brightness is understood; the Adreno filing — STILL OPEN regardless (submit
needs user identity/tracker; content upgrades again: "named Granite
init/use bug + Adreno's 128 KiB sampler range + fix verified exit 0");
G18-hunk fix adoption (still queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only); G28 writer-fix hunk compiled in (guard + once-LOGI, uncommitted, SSD clone only; diff text committed beside this report) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26 hunks | untouched, still uncommitted in SSD clone only (G22 + G26 HUNK_MATCH re-verified pre-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G28 additions | the ONE Granite hunk (SSD clone worktree only) + session files: `g28-build.sh` + `g28-run.sh` + `g28-writer-fix.diff` (G28-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanouts | run receipts of our own binary in SSD `ps2x-g28/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, 4 files pre-hunk)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
git -C $SSD/parallel-gs-g7 diff tools/gs_dump_replayer.cpp | grep -A15 '93,9 +96,15'  # vs g26-narrowing.diff: HUNK_MATCH
shasum -a 256 <g27-binary> ; xxd -l 16 <g27-binary>             # §2a 6th zero-damage confirm (13d2fc69…, zeros)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g28 + 9 build dirs> ; df -h / $SSD           # §0 (pre + post)
# (write the ONE hunk: memory_allocator.cpp :1424-1431 guard + :1472-1483 receipt; 16:04:03)
git -C $SSD/parallel-gs-g7/Granite diff vulkan/memory_allocator.cpp > local/research/G28/g28-writer-fix.diff  # 1770 B
cmake -S <clone> -B $SSD/parallel-gs-g28-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §2d exit 0
cmake --build <g28-build> --target parallel-gs-replayer -j2    # §2d exit 0 [458/458], pre-existing warnings
shasum -a 256 <g28-binary> (build, pre-push, report)            # 450471e2… ×2 match, then 3a11581e… destroyed
llvm-readelf --notes <g28-binary> ; strings grep ×1/×1/×2/×0 ; xxd -l 4  # 53af7a56… + ELF
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g28  # §3c
grep -c Running/G10/success/G28/G26/G22 <logcat> ; census ; cmp g27/g28 PPMs  # §3 census (byte-identical black)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g28/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g28 && mkdir -p /data/local/tmp/g28'
push <dump> $G28DIR/g13-dump.gs ; push <g28-binary> $G28DIR/parallel-gs-replayer  # §2e
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§2e)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G28DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G28DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g28-run-stdout.txt 2> g28-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (fix verified)
logcat -d -s Granite:V > $SSD/ps2x-g28/g28-logcat.txt                # 1805 lines
pull $G28DIR/g28-run-stderr.txt $SSD/ps2x-g28/ (0 B) ; pull stdout (0 B)
shell 'ls -la $G28DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts; ZERO new tombstone
pull $G28DIR/*.ppm $SSD/ps2x-g28/ (10 files)
shell 'rm -rf /data/local/tmp/g28 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The black scanouts are undiagnosed (separate device trait per §3g verdict
   2 — refuted as aliasing-caused, but its own cause is unnamed; queued as
   the §4 next action, not this brief).
2. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness per §4; no port, no upstream contact).
3. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
4. The zero-destroyed G28 binary was left destroyed (run already complete
   and valid; rebuilding a receipt binary is out of scope). 7th recurrence
   overall (6th was the G27 binary, §2a).
5. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
6. No lldb (decision tabled §3h); OS tombstone store untouched (no new
   tombstone this brief). `upstream/` + harness code untouched; no new
   dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
7. Build warnings were observed via tail (pre-existing `-Wshadow` class);
   the full warning log was not retained — same treatment as G22–G27, and
   zero warnings point at the hunk lines.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g28/` (13 files: `g28-logcat.txt`
  1805 lines, `g28-run-stderr.txt` 0 B, `g28-run-stdout.txt` 0 B,
  10 PPMs × 688,143 B, all pure black) +
  `parallel-gs-g28-android-build/` (binary 265,841,104 B `450471e2…`
  BuildID `53af7a56…` at push time; zero-destroyed at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g27/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G26
  hunks uncommitted; Granite `16e7395f…` + G20-capture set + G28 hunk,
  all uncommitted — ZERO commits anywhere).
- Session-only: `/tmp/g28-g26block.txt`, `/tmp/g28-g26ref.txt` (~4 KB).
- Commits: ssx3 `local/research/G28/` `[G28]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunk stays
  uncommitted in the submodule worktree).

TAIL-RECEIPT: G28 report ends here. ONE Granite guard hunk, one build exit
0, ONE flag run exit 0 with the G28 receipt firing (writer fixed,
single-writer family confirmed), 10 black scanouts byte-identical to G27
(black is a separate trait — next wall, not adoption), O4 absent, filing
still open.

Outcome: alternative (a) — exit 0 with the receipt firing once, O5/O6 gone,
O4 absent, scanouts black-but-identical-to-G27. No tuning loop was entered:
one hunk, one build, one device run. Retry not used (exit 0 — no retry
condition); lldb not used (nothing to triage — zero new tombstone).
