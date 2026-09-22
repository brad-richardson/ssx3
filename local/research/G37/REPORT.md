# G37 report — Minimum-content threshold wall: shrunken tag, same raw legs (Odin)

Brief: G37 (this turn) — executes G36 §4's ONE next action ONLY: the
minimum-content threshold wall (same raw-access legs as G36, SMALLER
tag — splits "ANY nonzero-RGB content", threshold = 1 word, from
higher-threshold models). Tables + hypothesis + next-action
recommendation, no verdicts beyond the hypothesis. Time box 6 h (used
0.25 h — 11:00→11:15 EDT task start → commit; measured walls: 11:00:09
lane reads, Task 1 statics + predictor 11:00→11:04, hunk + build
11:04→11:09, verify-push-run-pull-cleanup-mirror 11:09:42→11:10:30,
report 11:10→11:15). Read first per the brief: `local/research/G36/REPORT.md`
(all of it: pure-refined-H2 WINS — the 112-word tag renders EXACTLY
with zero write-path ordering ops, 16/16 B1 + 10/10 ladders + 10/10
scanouts == tag model; H1-as-barrier refuted 0/10). No upstream contact
of any kind (standing no-upstream order — local hunks only, filing
stays local).

Machine: same as G8–G36 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g37/`
ONLY; removed at end (`mg/` only).

Headline result: **ANY-nonzero-RGB WINS with threshold = 1 word — decisively, on pre-registered bytes.**
(1) Task 1 statics (ZERO device contact) tabled the threshold
candidates (T1 single-word-of-one-page CHOSEN over T2 single-page /
T3 sparse-subset / T4 alpha-only, with per-threshold predictions),
the ONE picked shrunken tag (word 0 of page 112 only,
`temp[0] |= 0x00FFFFFF`, alpha 0x00), the premise rows (shrunken-temp
receipt MUST still read `13bd6843a14ee366`/149724 — host-side,
barrier-independent; B1/B2/B-neither B-at-sample-time split with
per-outcome verdict meanings tabled BEFORE the run), reformulated
ANY(1)/higher-threshold predictions (every scalar pre-registered via
the reused G34 renderer), and a six-row decision matrix with seven
per-pixel triage rules. (2) ONE hunk (G36's +59 excised + G37's +56
shrunken-tag raw-access placement inserted in the same edit), ONE
build (exit 0 `[458/458]`, full identity), verify-then-push with NO
gap, ONE run: **exit 0**, 16/16 `G37: writeback` (shrunken temp
`13bd6843a14ee366`/149724 ×16) + 16/16 `G31: state` (fields == G31
×16, full lines stripped-identical) + 16/16 `G31: bytes` (B ==
shrunken ×16 — outcome B1, A == G31 ×16) + 512 `G30: vpage` (112/112
== shrunken per-page oracle, 511/512 ALL == G31 with exactly page 112
differing) + 10 `G29: ladder` (P1=P2=P3 == shrunken-model
`debe0cda9c919bde`/229379 ×10, 0/10 cleared) + 1 `G29: vram`, ZERO new
tombstone, 10/10 scanouts BYTE-IDENTICAL to the host 1-white-pixel
model (sha `34697c14…`, `cmp` identical, white-set == {(0,0)}).
Higher-threshold (threshold > 1, per-page-quorum, nonzero-alpha-only)
is refuted 0/10; no OTHER branch fired. The ONE next action is the
channel-specificity wall (§2b's T4: alpha-only 1-word tag, same raw
legs — it splits RGB-specific from ANY-channel thresholds).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g37-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g37/` (retrieval: logcat + stdout + stderr + 10 PPMs, explicit list) | 50 MB | 13 files, 25,600 KiB allocated PASS |
| SSD `ps2x-g7..g36` + G14/G18/G20/G22/G24/G26/G28/G29/G30/G31/G32/G33/G34/G35/G36 build dirs (read-only) | 0 growth | all == 11:00:53 snapshot exactly (post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (shrunken-tag raw-access placement + retained dumps) | ONE hunk in `gs/gs_interface.cpp` (+56/−0 G37, G36 +59 excised same edit, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 + G31 hunks untouched, HUNK_MATCH re-verified pre + post + pre-push + post-run + report — 5/5); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g37-*` 788 KiB (hunk/build/run/score + stub + build log + diff extracts + share check + predictor + expected PPM + vpage + whites, session-only; `/tmp/g34-*` oracles reused as cross-check); G37 evidence dir text-only PASS |
| `/` volume df shift (observed, tabled) | — | `/` Avail 4.3 Gi → 4.3 Gi (75%→75%) with Used static at 13 Gi — no shift; SSD 93%→94% is the NEW g37 build dir only (all older dirs 0 growth); no action, recorded for the gate |
| device | `/data/local/tmp/g37/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |
| share-tier mirror (drive distrusted) | — | `/Volumes/share/ssx3/ps2x-g37/` 13/13 files, `shasum -c` ALL OK PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Placing a 1-word shrunken tag (word 0 of page 112 ONLY, `temp[0] \|= 0x00FFFFFF`, alpha stays 0x00) via G36's raw `begin_host_vram_access` + CPU-copy legs splits "ANY nonzero-RGB content" (threshold = 1 word) from higher-threshold models: ANY(1) predicts the shrunken tag renders EXACTLY (ladder == `debe0cda9c919bde`/229379 ×10, scanouts byte-identical to the 1-white-pixel model sha `34697c14…`, white at exactly (0,0)); higher-threshold models (threshold > 1 word, per-page-quorum, nonzero-alpha-only) predict output stays CLEARED (ladder == `aa2fa32572450383`/229376 ×10, scanouts byte-identical black `99418f1b…`) |
| observable signal | design tables (§2: threshold candidates + the ONE picked shrunken tag + premise rows incl. B1/B2/B-neither split + named bytes + predictor reuse + matrix with per-pixel triage rules + hunk spec) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G37: writeback` (shrunken temp) + 16 `G31: state` + 16 `G31: bytes` (B1/B2 triage) + 512 `G30: vpage` (1-word-oracle-or-G31 second witness) + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + 10 scanouts scored (exact-vs-shrunken-model / exact-vs-black / white-set census) + verdict (§4) |
| alternatives | ANY-1 (shrunken source ×16 + exact 1-pixel output ×10); HIGHER-THRESHOLD (shrunken source ×16 + cleared output ×10); B2-CLEARED (stale B ×16 + cleared output — NO-VERDICT, cleared trivially expected under both); B2-TAG (stale B ×16 + 1-pixel output — PARADOX, sampler saw what host reads cannot); OTHER-premise (receipt ≠ shrunken — read leg corrupted, stop, no reading); OTHER-mixed (shrunken source + neither-shrunken-nor-cleared output — partial/torn/quorum-bleed, triage by per-pixel rules §2f; refutes ANY(1) + higher-threshold jointly) |
| stop condition | ONE hunk max (shrunken-tag raw-access placement + retained dumps); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage; any validity-chain pin mismatch → table + stop |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: ANY-NONZERO-RGB(1) — all 16 write-back receipts carry the
shrunken FNV, all 16 B-at-sample-time reads carry the shrunken FNV
(B1 — the barrier-less 1-word store persists in the host mapping),
page 112 matches the shrunken per-page oracle while all other 511
pages match G31, all 10 ladders carry the shrunken-model FNV
(P1=P2=P3), all 10 scanouts are byte-identical to the 1-white-pixel
model with the white pixel at exactly the pre-registered corner
(0,0). HIGHER-THRESHOLD is refuted (0/10 cleared);
B2/PARADOX/premise-break/mixed never triggered. No tuning loop was
entered: one hunk, one build, one device run. Retry not used (exit
0); lldb not used (zero new tombstone — nothing to triage).

## 2. Task 1 — static design (no device runs)

Zero device contact in this section: no `adb` invocation of any kind
before §3d (host tools only: git/grep/shasum/python/du/df/clang++).

### 2a. Pin verification (pre-work — G36 end state reproduced, ZERO edits)

11:00–11:04 EDT (every pin re-checked before any edit):

| item | observed |
| --- | --- |
| working tree (brief: VERIFY, re-pin if migrated) | `/Users/bradrichardson/dev/ps2xGS` EXISTS (superproject HEAD `fd781ef`, clean) — VERIFIED, no re-pin; lane clone remains SSD `parallel-gs-g7` below |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G36 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 163 (G36 end state + nothing), gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 — G36 end state + nothing |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH; re-verified post-hunk + pre-push + post-run + report — 5/5) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (Granite HEAD `16e7395f…` == pin) |
| G29 ladder + G30 vpage + G31 state + G36 raw-access | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 in replayer; `G31: state` ×1 + `G31: bytes` ×2 + `G36: writeback` ×3 + `G35: writeback` ×0 + `G34: writeback` ×0 + `G33: writeback` ×0 in interface) |
| G28 binary (re-sha) | 265,841,104 B, sha `450471e2…` FULL-prefix-match, magic `7f45 4c46` ELF — **INTACT** |
| G29 binary (re-sha) | 265,846,144 B, sha `79e6f4d2…` FULL-prefix-match, magic ELF — **INTACT** |
| G30 binary (re-sha) | 265,847,904 B, sha `a1963e66…` FULL-prefix-match, magic ELF — **INTACT** |
| G31 binary (re-sha) | 265,851,416 B, sha `c91719a0…` FULL-prefix-match, magic ELF — **INTACT** |
| G32 binary (re-sha) | 265,852,240 B, sha `35288fd0…` FULL-prefix-match, magic ELF — **INTACT** |
| G33 binary (re-sha) | 265,853,048 B, sha `7e0ea8031c6a581f…` FULL-prefix-match, magic ELF — **BUILD-sha stable** (the 12th read-artifact recurrence stays closed — corroborated, not re-litigated) |
| G34 binary (re-sha PASS1 + PASS2) | 265,853,192 B, sha `2b101ddec1cb2783…` stable ×2 FULL-match committed `2b101dde…`, magic ELF — **INTACT** |
| G35 binary (re-sha PASS1 + PASS2) | 265,853,184 B, sha `e2998ffcc1f0001a…` stable ×2, magic `00000000` — **FULLY-ZEROED** (the gated 14th read artifact, re-pinned with 2+ separated reads; NOT in G37's validity chain; committed `f3a33f7c…`/BuildID `132df20b…` remain the authority for what the G35 binary was; tabled, proceeded per the brief's stop rule) |
| G36 binary (re-sha PASS1 + PASS2) | 265,853,160 B (== size pin), sha `6430dbe875adcfc3…` stable ×2, magic `00000000` first bytes zero — **ZEROED READ ARTIFACT** (the brief's gated 15th read artifact, re-pinned with 2+ separated reads; NOT in G37's validity chain — the chain is the G37 binary + dump; committed `4e68911d…`/BuildID `384d6429…` remain the authority for what the G36 binary was; tabled, proceeded per the brief's stop rule) |
| rich dump (host, ×3 reads this session: PASS1 + PASS2 + predictor) | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match (PASS1 + PASS2 + predictor-load assert) |
| dirs 0-growth | pre-run `du -sk` snapshot 11:00:53 (ps2x-g7 13312 … g35 24576, g36 25600; g37 absent; 15 build dirs 4480000/4482048 KiB; `/` 75%, SSD 93%); post-run re-verified §0 (every old value identical) |
| recipe | NDK r30 (`/opt/homebrew/share/android-ndk`, toolchain file present); cmake + ninja + clang++ + python3 + adb all on PATH (`llvm-readelf` via NDK toolchain path) |
| session survivors | ALL `/tmp/g34-*` + `/tmp/g35-*` + `/tmp/g36-*` session files PRESENT (same boot; committed REPORT scalars kept as authority, `/tmp` oracles used as cross-check only) |
| share tier | `/Volumes/share/ssx3/ps2x-g36/` present (13 files); mirror target `ps2x-g37/` confirmed writable |

Lane-critical SSD bytes (G37 binary, dump) corroborated by 2+
matching reads separated in time (build + pre-push + on-device +
report); single-read SSD evidence was never relied upon.

### 2a2. Session-files vs the brief's gate note (tabled — proceeded, rationale on record)

Same observation as G35 §2a2 / G36 §2a2: ALL `/tmp/g34-*`,
`/tmp/g35-*`, and `/tmp/g36-*` files present with prior-session mtimes
(same boot — no restart occurred between the gate and this run). TABLED
and PROCEEDED WITH, for the same three on-record reasons: (1) the
authority rule is honored regardless — every §2d prediction cites
COMMITTED report scalars (G31/G33/G34/G36 REPORT.md), and the surviving
`/tmp` oracles are used as CROSS-CHECK only (§2e: the unmodified G34
predictor re-derives every scalar from the dump, and the G37 predictor
re-asserts every pin before deriving the new scalars); (2) the
alternative (deleting surviving oracles to simulate the restart) would
destroy corroboration for no validity gain; (3) nothing in the validity
chain depends on `/tmp` absence (the chain is dump + new-binary shas at
every gate, §3d). The discrepancy is observational only — no pin
mismatched.

### 2b. Threshold candidates (tabled — exactly one picked)

The lane question (G35 §7.1, now the ONLY open discriminator per G36
§4): is pure-refined-H2's quantifier "ANY nonzero-RGB content"
(threshold = 1 word) or something higher? Four candidate thresholds
were tabled; the picked one must split "ANY nonzero" (exact render of
whatever the shrunken tag is) from the higher-threshold field
(cleared-or-partial) in ONE run. All four keep G36's legs (raw
`begin_host_vram_access` + CPU copy, no flush/wait/commit, never
closed) — content is the ONLY delta.

Stale-B facts constraining the table (derived from the pinned dump
pre-run, host-side): stale B = 229376 words, nonzero-RGB words 0,
nonzero-ALPHA words 149721 (widespread nonzero alpha renders CLEARED
per G31); word 0 of page 112 = `0x00000000` (alpha 0 AND RGB 0). The
full tag (`|= 0x00FFFFFF` × 112) is therefore an RGB-ONLY delta: tagged
B carries the SAME 149721 alpha-nonzero words as stale, plus 112
RGB-white words — and renders the tag EXACTLY (G34/G35/G36).

| # | candidate threshold | shape | "ANY nonzero-RGB" predicts | higher-threshold field predicts | verdict |
| --- | --- | --- | --- | --- | --- |
| T1. Single word 0 of ONE page (page 112) — 1 word total (CHOSEN) | `temp[0] \|= 0x00FFFFFF` only; word = `0x00FFFFFF` (RGB white, alpha 0x00) | EXACT 1-pixel render (1 white at the pre-registered position) | CLEARED (1 word is below EVERY threshold > 1, below every per-page quorum > 1 word, below every sparse quorum > 1; and the tag word's alpha is 0, so cleared under nonzero-alpha-only too) | **CHOSEN** — the maximal split: the ONLY candidate whose content sits below the entire higher field simultaneously, so exact-render confirms threshold = 1 word against ALL higher models at once, and cleared refutes threshold = 1 (naming the follow-up: bisect upward + an alpha-only 1-word tag to separate threshold>1 from alpha-necessary). Directly answers G35 §7.1's queued "threshold = 1 word?" Simplest hunk delta vs G36 (4-line OR loop → single statement), same base/n/legs — minimal confound risk. Corner-pixel render (0,0) leaves no adjacency/smear ambiguity in triage |
| T2. Single full page (page 112, all 2048 words) | 2048 tagged words in one page | exact render | exact under every threshold ≤ 2048 — splits NOTHING except extreme cross-page-quorum variants | REJECTED — 2048 words renders exact under ANY(1) AND under nearly every higher model; no discriminating power for the threshold = 1 question |
| T3. Sparse subset (word 0 of K pages, 1 < K < 112) | K tagged words | exact render | exact iff threshold ≤ K — splits ANY only from thresholds > K | REJECTED — strictly less power than T1 for the threshold = 1 question (any K > 1 leaves thresholds 2..K live on an exact-render); useful ONLY as a follow-up if T1 clears (bisect upward toward the true threshold) |
| T4. Nonzero-alpha-only variant (1 word `\|= 0xFF000000`, RGB stays 0) | 1 alpha-tagged word, RGB zero | CLEARED (RGB zero — consistent with ANY-nonzero-RGB, which counts RGB words) | cleared under threshold>1/quorum (1 word); exact only under alpha-sufficiency | REJECTED as the first pick — predicts cleared under ANY-RGB too, so it cannot CONFIRM the threshold = 1 claim; it tests the channel axis, not the threshold question. Natural follow-up AFTER T1: if T1 renders (RGB suffices at threshold 1), does an alpha-only 1-word tag also render (is the threshold RGB-specific, or any-channel?) |

Note on nonzero-alpha-only as a FULL-tag theory (already dead,
tabled so no future brief re-litigates it): stale B's 149721
alpha-nonzero words render CLEARED (G31), and tagged B's IDENTICAL
149721 alpha words + 112 RGB words render the TAG (G34/G35/G36) — the
RGB-only delta moved the output, so output is NOT a function of alpha
content alone. Nonzero-alpha-only survives in the §2d table ONLY as a
shrunken-tag predictor (cleared — the T1 tag word has alpha 0), where
this wall over-determines it either way; the LIVE split is ANY(1) vs
threshold > 1 vs per-page-quorum.

### 2b2. The ONE picked shrunken tag (T1 — specified exactly)

- Which words: `temp[0]` ONLY — word 0 of page 112 (byte offset 0 of
  region B, VRAM word 229376). All other 229375 B words are
  stale-exact.
- What RGB: `|= 0x00FFFFFF` (white RGB; alpha preserved `0x00` — the
  tag word is `0x00FFFFFF`, nonzero-RGB count 1/229376).
- Why that threshold splits "ANY" from the field: 1 nonzero-RGB word
  is the minimum nonzero content — "ANY nonzero-RGB" (threshold = 1)
  predicts it renders EXACTLY (one white pixel at the pre-registered
  position (0,0), §2e), while EVERY higher model predicts cleared
  (threshold > 1: 1 < threshold; per-page-quorum: 1 word in the page
  is below any quorum > 1; nonzero-alpha-only: tag alpha is 0). No
  other single content choice sits below the whole field at once.
- Render position: the single white pixel is at (0,0) — the top-left
  corner (predictor-derived, §2e; member of the G34 112-set, subset
  property verified). Corner placement means a partial/smeared
  outcome cannot hide in adjacency ambiguity: any nonblack pixel
  outside (0,0), or any nonwhite value at (0,0), is mechanically
  classifiable by the §2f triage rules.

### 2c. Premise rows (P1 MUST-hold + P2 B1/B2/B-neither split + P3 controls)

P1 — writeback receipt (host-side, barrier-independent — MUST hold):
the receipt checksums the static temp AFTER the B→temp copy + the
single-word OR-mask, entirely on CPU. Predicted 16/16 `base=917504
n=917504 fnv=13bd6843a14ee366 nz=149724`, 0 map-fails. The mask makes
the receipt robust to what the read leg saw: stale→shrunken AND
shrunken→shrunken both land on the shrunken model (OR is idempotent),
so receipt==shrunken ⟺ read leg saw stale-or-shrunken with intact
alphas. Receipt≠shrunken (any) ⟹ the read leg returned something
NEITHER stale NOR shrunken (corruption/torn/unbalanced-access
artifact) ⟹ OTHER-premise: STOP, no ANY(1)/higher-threshold reading
(the treatment broke the read path itself).

P2 — B-at-sample-time (the split question — ALL outcomes tabled with
verdict meanings BEFORE the run): the G37 block CPU-stores shrunken
bytes into the host-visible mapping via the raw pointer with no
barrier and no commit; G31-B (post-`renderer.vsync` `map_vram_read`) +
G30 vpage (post-loop `map_vram_read`, last pass, pre-restart) witness
what the read leg sees. G36 proved barrier-less stores of the FULL tag
persist (B1 ×16); the shrunken treatment stores FEWER nonzero bytes
through the identical path, so B1 is expected under BOTH threshold
hypotheses, and the split fires purely at the sampler/output level:

| outcome | bytes | mechanism reading | verdict meaning (pre-registered) |
| --- | --- | --- | --- |
| B1: read leg sees SHRUNKEN B | G31-B == `13bd6843a14ee366`/149724 head `ffffff00…` ×16; vpage page-112 == `eb42866db438f31c`/698 + other 511/511 == G31 | barrier-less CPU stores persist in the host mapping through vsync (as G36 ×16); sampler and host reads COULD see the same bytes | output 1-pixel-exact ⟹ **ANY-NONZERO(1)** (threshold is 1 word; alpha not necessary — the tag word's alpha is 0); output cleared ⟹ **HIGHER-THRESHOLD** (threshold > 1 word, or per-page-quorum, or alpha-necessary — the residual ambiguity names the follow-up wall: sparse-subset bisection + alpha-only 1-word tag); output other ⟹ **OTHER-mixed** (§2f triage) |
| B2: read leg sees STALE B | G31-B == `eea04488c453e75b`/149721 ×16; vpage 512/512 == G31 | something discards barrier-less stores — bytes never persisted anywhere readable | output cleared ⟹ **NO-VERDICT** (cleared trivially expected under BOTH hypotheses — the treatment failed to place bytes); output 1-pixel-exact ⟹ **PARADOX** (sampler saw a tag host reads cannot see — full triage, new theory) |
| B-neither/mixed (any) | B == neither shrunken nor stale, or flapping across seqs | torn race between un-waited CPU stores and concurrent GPU writes | OTHER — torn writes; triage by seq pattern + per-page deltas; no ANY(1)/higher-threshold reading |

P3 — controls (same both hypothesis columns): 16 `G31: state` all
fields == G31 (§2d table; full lines stripped-identical); 16 A-lines
== G31's 16 A-fields (scene path untouched — non-perturbation); 1
`G29: vram` == load `6002946899e9cae0`/1184729 (restart control —
fires post-loop post-restart on reloaded bytes, barrier-independent);
logcat 2376 lines (G31's 2360 + 16 G37) with the §3e shape; 0
map-fails of any kind. Any P3 break ⟹ triage per §2f (A≠G31 ⟹
non-perturbation violated; vram≠load ⟹ load path perturbed).

### 2d. Reformulated predictions (every scalar pre-registered)

Authorities: shrunken TB `13bd6843a14ee366`/149724 head `ffffff00…`
(§2e, predictor-derived); stale B `eea04488c453e75b`/149721 (G31, via
G36 §2d); cleared render `aa2fa32572450383`/229376 + black PPM
`99418f1b1a94ed9ffcfadd6fc0b6573eca5275d6834a3d4cffb64da330233b34`
(G33 REPORT full sha + G36 §2d); shrunken render
`debe0cda9c919bde`/229379 + 1-white PPM
`34697c14ddac68db3529595d26eb9cf3e51584ae266848379aac22d1d219a276`
(§2e, predictor-derived; single white at exactly (0,0)); load
`6002946899e9cae0`/1184729 (G30, via G36 §2d); page-112 oracle
`eb42866db438f31c`/698 (== G34 vpage line for page 112, §2e
re-derived).

| observable | ANY nonzero-RGB (threshold = 1 word) | higher-threshold (threshold > 1 / per-page-quorum / nonzero-alpha-only) |
| --- | --- | --- |
| 16 `G37: writeback` temp FNV | `13bd6843a14ee366` nz=149724, base/n=917504/917504 (premise P1 — same both columns) | same |
| 16 `G31: bytes` B | shrunken `13bd6843a14ee366` nz=149724 head=`ffffff00…` (B1 assumed; B2/B-neither ⟹ §2c re-route) | same |
| 16 `G31: state` | all fields == G31 predictions; full lines stripped-identical to G31's 16 | same |
| 512 `G30: vpage` | page 112 == `eb42866db438f31c` nz=698 head=`ffffff00…` (== G34's page-112 line); other 511/511 == G31's vpage (B1 assumed) | same |
| 16 A-lines | == G31's 16 A-lines (scene path untouched) | same |
| 1 `G29: vram` | `6002946899e9cae0`/1184729 (restart control) | same |
| 10 `G29: ladder` P1/P2/P3 | == shrunken-model `debe0cda9c919bde` nz=229379 ×10 | == cleared `aa2fa32572450383` nz=229376 ×10 |
| 10 scanouts | BYTE-IDENTICAL to `/tmp/g37-expected.ppm` (sha `34697c14…`, 688,143 B; exactly 1 white pixel at (0,0), nonblack count 1) | BYTE-IDENTICAL black (sha `99418f1b…`, 688,143 B; 0 nonblack) |
| logcat | 2376 lines (G31's 2360 + 16 G37); `Total time per VBlank` inflated class | same shape |

### 2e. Predictor reuse (the REAL G34 predictor unmodified + the G37 derivation)

No host restart this session (§2a2): `/tmp/g34-predict.py` (the exact
artifact behind G34 §2d, re-run unmodified by G35 and G36) ran
unmodified against the pinned dump:

| check | observed |
| --- | --- |
| load full-VRAM | `6002946899e9cae0`/1184729 (== pin) |
| stale B | `eea04488c453e75b`/149721 head `0000000000000000` (== pin) |
| G32-pattern self-check | B `dfe2b6516a519f83`/915264 + model P1 `9dd120bc6b0df383`/915264 (== committed G32 scalars) |
| VOID reproduction | H1-FNV == cleared (`aa2fa32572450383`)? True; PPM sha `99418f1b1a94ed9f…`; 0/229376 nonzero-RGB words; stale-model PPM `cmp`-identical to G29 blacks |
| tagged oracle | TB `c039a1d1c29cb293`/150057 head `ffffff00…`; 112/229376 nonzero-RGB words; render `86ad7b887e140383`/229712; PPM `d19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f` (full-match G34 §3i/G36 §3i); 112 whites + 112 nonblack; bbox x[0,448] y[0,416]; first row x=0,64,…,448 @ y=0 |
| verdict | ALL PREDICTOR CHECKS PASS — every §2d carried scalar re-derived from the dump (dump sha `154d9d85…` re-confirmed on load) |

`/tmp/g34-predict.py` was left UNMODIFIED. The shrunken-tag scalars
were derived by `/tmp/g37-predict.py`, which reuses the G34 renderer
VERBATIM (same `swizzle_ps2_ct` + `render` + `fnv_nz`, same dump
layout) and re-asserts every G34 pin (dump sha, load, stale B,
full-tag TB) BEFORE deriving anything new — so the new scalars come
from the same predictor, not from guessing:

| check | observed |
| --- | --- |
| pins re-asserted | dump sha `154d9d85…` + load `6002946899e9cae0`/1184729 + stale B `eea04488c453e75b`/149721 + full-tag TB `c039a1d1c29cb293`/150057 — ALL reproduced from the dump |
| stale word0/page112 | `0x00000000` (asserted — the alpha-0 split holds: the tag word carries RGB only) |
| SHRUNK TB | `13bd6843a14ee366`/149724 head `ffffff00…`; 1/229376 nonzero-RGB words (asserted); nz == 149721+3 (arithmetic cross-check) |
| SHRUNK render | `debe0cda9c919bde`/229379 (nz == 229376+3 cross-check) |
| SHRUNK PPM | sha `34697c14ddac68db3529595d26eb9cf3e51584ae266848379aac22d1d219a276`, 688,143 B → `/tmp/g37-expected.ppm` |
| white census | exactly 1 white + 1 nonblack (asserted); single white at (0,0) → `/tmp/g37-whites.txt` |
| subset property | (0,0) IS a member of the G34 112-set (`/tmp/g34-whites.txt` — asserted) |
| vpage oracle | page 112 == G34's page-112 line (`112 eb42866db438f31c 698 ffffff0000000000`, asserted byte-equal); pages 113..223 == stale lines (111/111 asserted) → `/tmp/g37-vpage.txt` |
| verdict | ALL G37 PREDICTOR CHECKS PASS — every §2d NEW scalar derived from the dump via the reused renderer |

Oracle reuse: `/tmp/g34-vpage-stale.txt` (511 stale lines serve the
G37 scorer for pages 113..223) + `/tmp/g34-vpage.txt` line 112 (the
G37 page-112 oracle, byte-equal by construction — the 1-word tag
touches page 112's word 0 exactly as the full tag does) serve
alongside the new `/tmp/g37-expected.ppm` + `/tmp/g37-whites.txt` +
`/tmp/g37-vpage.txt`.

### 2f. Decision matrix (pre-registered, with per-pixel triage rules)

| G37 temp (16) + B (16) | ladder P1 (10) + scanouts | reading |
| --- | --- | --- |
| temp == shrunken ×16, B == shrunken ×16 (B1) | == shrunken-model `debe0cda9c…` ×10, scanouts 1-pixel-exact (`34697c14…`, `cmp`-identical to `/tmp/g37-expected.ppm`, white-set == {(0,0)}, nonblack == 1) | **ANY-NONZERO(1)** — threshold is 1 word; alpha not necessary |
| temp == shrunken ×16, B == shrunken ×16 (B1) | == cleared `aa2fa325…` ×10, scanouts black-exact (`99418f1b…`, nonblack == 0) | **HIGHER-THRESHOLD** — threshold > 1 word (or per-page-quorum, or alpha-necessary — the residual ambiguity names the follow-up wall, §4) |
| temp == shrunken ×16, B == stale ×16 (B2) | == cleared ×10, black-exact | **NO-VERDICT** — barrier-less stores lost; cleared trivially expected under both (treatment failed to place bytes) |
| temp == shrunken ×16, B == stale ×16 (B2) | == shrunken-model ×10, 1-pixel-exact | **PARADOX** — sampler saw what host reads cannot; full triage, new theory required |
| temp ≠ shrunken (any) OR B-neither/mixed (any) | — | OTHER-premise — read path broken (temp) or torn persistence (B) → STOP, no ANY(1)/higher-threshold reading |
| temp == shrunken ×16, B == shrunken ×16 (B1) | neither 1-pixel-exact nor cleared (any pattern) | **OTHER-mixed / BOTH-REFUTED** — ANY(1) + higher-threshold jointly refuted; per-pixel triage rules below name it |

Per-pixel triage rules (registered BEFORE the run — applied per
scanout to the RGB plane; white == (255,255,255), black ==
(0,0,0)):

| rule | pixel pattern | triage meaning |
| --- | --- | --- |
| EXACT | white-set == {(0,0)}, nonblack == 1 | the ANY(1) prediction (row 1 of the matrix) |
| CLEARED | white-set == {}, nonblack == 0 | the higher-threshold prediction (row 2) |
| MISPLACED | 1 white at (x,y) ≠ (0,0), nonblack == 1 | refutes BOTH (ANY(1) names (0,0); higher names none) — address-path anomaly; triage by (x,y) membership in the G34 112-set (in-set ⟹ wrong-word-rendered; out-of-set ⟹ swizzle-model break) |
| SUPERSET | k whites with 1 < k ≤ 112, (0,0) ∈ set, nonblack == k | quorum-bleed/partial — more content rendered than placed; triage by k + set membership (in-112-set ⟹ ghost of full-tag positions; extras ⟹ smear) |
| FULL-GHOST | white-set == the G34 112-set | full-tag contamination (prior-run bytes? — but B reads shrunken, so paradox-adjacent; full triage, no threshold reading) |
| SMEAR | any nonwhite nonblack pixel (gray/partial) | torn coherency — partial word visibility; triage by position (at (0,0) ⟹ torn single-word write; elsewhere ⟹ wider tear) |
| DEGENERATE | uniform single non-black value, or any pattern matching none of the above | unclassified — full per-pixel diff against both models names the next wall; no threshold reading |

A mixed ladder/scanout split (ladders shrunken-model but scanouts
cleared, or vice versa) is OTHER-mixed regardless of pixel rules —
the ladder is the circuit's own checksum and the scanout is the
pulled image; their disagreement means the capture path, not the
threshold, needs triage first.

### 2g. Hunk spec (the ONE hunk, named)

ONE hunk: **G37 pre-`renderer.vsync` raw-access SHRUNKEN-tag placement**
(map-read B → static temp + single-word OR-mask pre-write
(`temp[0] |= 0x00FFFFFF` — word 0 of page 112 ONLY) → RAW
`renderer.begin_host_vram_access()` + offset + CPU copy back with
NEITHER `map_vram_write` NOR `end_vram_write` (no flush, no wait, no
commit; mapping never closed) + `G37: writeback` SHRUNKEN-temp
receipt), with **G36's raw-access block excised in the same edit**
(its diff survives committed in G36 evidence — excision is lossless
and REQUIRED: live committed content would confound the wall).

| item | spec → actual |
| --- | --- |
| site | `GSInterface::vsync`, immediately BEFORE `auto result = renderer.vsync(…)` — the same anchor G32/G33/G34/G35/G36 used (anchor `"\tauto result = renderer.vsync(priv_registers, info,\n"`, unique ×1) → CONFIRMED ×1 |
| shape | ONE contiguous insertion (`{…}` block at 1-tab scope); G36's +59 block excised first (derived from the committed `g36-rawaccess-placement.diff` `+` lines — no transcription); net vs G36 worktree: shrunken-tag placement only → +56/−0 contiguous, single @@ (`@@ -4684,2 +4723,58 @@`); worktree `gs_interface.cpp` diff 160 = 163 − 59 + 56 (arithmetic closes) |
| temp + tag | `static uint32_t g37_temp[(112*8192)/4]` (function-static, 917504 B BSS; fully rewritten each call before use; vsync is serial — no reentrancy) + `g37_temp[0] \|= 0x00ffffffu` (word 0 of page 112 ONLY — the 1-word tag) → as spec'd |
| raw write | `void *g37_raw = renderer.begin_host_vram_access()` (null-checked; `raw-map failed` fallback keeps the 3-marker shape) + `reinterpret_cast<uint32_t *>(static_cast<uint8_t *>(g37_raw) + g37_base)` dst → as spec'd |
| skipped calls | `map_vram_write(` / `end_vram_write(` / `flush_submit(` / `wait_timeline(` / `commit_host_write(` / `end_host_write_vram_access(` ALL ABSENT from the block (asserted; names appear only in the SKIPS comment without call parens); nothing closes the mapping → as spec'd |
| receipt | `G37: writeback base=%u n=%u fnv=%016llx nz=%u.` (SHRUNKEN-temp FNV/nz, truncated basis G29-E1) + `raw-map failed` / `read-map failed` fallbacks (3 `G37: writeback` markers total) → as spec'd |
| applier | `/tmp/g37-hunk.py` (mirrors `/tmp/g36-hunk.py`): asserts G36-block ×1 + immediately-pre-anchor + G37-absent + anchor ×1 + all-six-skips-absent + raw-call-present + single-OR-present + loop-absent; single file write; post-asserts G36-gone + G37 ×3 + G35/G34/G33-absent + G31 neighbors intact (`G31: state` ×1, `G31: bytes` ×2) → DRY-OK then APPLIED; post: G36 ×0, G37 ×3, G35 ×0, G34 ×0, G33 ×0, G31 ×1/×2, G22 HUNK_MATCH |
| syntax | hunk text extracted from the applier compiles clean in a stub TU (`clang++ -std=c++17 -Wall -Wextra -fsyntax-only` — STUB_SYNTAX_OK) → as spec'd |
| costs (tabled up front) | +16 logcat lines (~2 KB); runs inside the timed region (expect inflated ms/VBlank — diagnostic cost, not a signal); 16 extra HostAccess read cycles + 16 raw begins + 2×917504 B CPU copies + 1 OR/vsync → 2376 lines; 12.007 ms/VBlank (§3e) |
| retained | G22 + G26 + G28 + G29 ladder + G30 vpage + G31 state/bytes all untouched (HUNK_MATCH + marker counts re-verified post-hunk) → all intact |

### 2h. Knob matrix (flag SET — the ONLY delta vs G36's run is G37's hunk-for-hunk swap)

| knob / flag | G36 setting | G37 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G36 = G31 + RAW-ACCESS full-tag placement hunk | G37 = G31 + RAW-ACCESS shrunken-tag (1-word) placement hunk (G36 block excised) | the single delta (content shrunk 112 words → 1 word, legs identical) |

## 3. Task 2 — ONE minimum-content threshold wall + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G36's run is the G37 hunk-for-hunk swap)

Same table as §2h (SET / UNSET / KEPT / ABSENT / hunk-for-hunk swap —
the single delta).

### 3b. Hunk record (ONE hunk, shrunken-tag raw-access placement + retained dumps)

`gs/gs_interface.cpp`, G36's +59 block excised + ONE contiguous +56/−0
insertion (new lines ~4723–4778) in `GSInterface::vsync()`
immediately BEFORE the `renderer.vsync` call: `map_vram_read(917504,
917504)` → CPU copy into `static uint32_t g37_temp[]` → single-word
OR-mask `g37_temp[0] |= 0x00ffffffu` (word 0 of page 112 ONLY) →
truncated-basis FNV/nz over the SHRUNKEN temp → RAW
`renderer.begin_host_vram_access()` + offset → CPU copy shrunken temp
back → mapping NEVER closed + `G37: writeback` receipt (`raw-map
failed` / `read-map failed` fallbacks). Regs/loop/circuit untouched.
Full diff text in `g37-shrunken-placement.diff` beside this report
(mechanically extracted with `-U1`: 56+/0-, single @@ block,
`cmp`-identical to the worktree extraction). G22 HUNK_MATCH + G26 block
+ G28 Granite hunk + G29 ladder + G30 vpage + G31 state all untouched;
zero commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G36 recipe, `g37-build.sh` mirrored): exit 0
(`Configuring done`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`,
binary mtime 11:08).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp` + cmake-deprecation noise); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,853,016 B (−144 vs G36 — the dropped loop delta; NEW size expected) |
| sha (build-time) | `97c339552a193ee9c718e8aee34dcf860c6ccf8913f0dc99584bfba73078d1c0` (NEW) |
| build-id | `722427ed1ef8942d3c0d8c521590d96076be1cfa` (distinct from G36 `384d6429…`) |
| plumbing presence | `G37: writeback` ×3, `G36: writeback` ×0, `G35: writeback` ×0, `G34: writeback` ×0, `G33: writeback` ×0, `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule + paranoia triple-gate)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 11:09:42 | `97c33955…` (binary) + `154d9d85…` (dump) FULL-match build sha; G22 HUNK_MATCH; all dirs == baseline (new g37 build dir the only growth) |
| device stage | 11:09:4x | pre-check (Odin3, Android 15, `mg/` only, newest tombstone _23, 28 G free) then `rm -rf` + `mkdir` + push dump (0.014 s) + push binary (2.089 s) into `/data/local/tmp/g37/` ONLY |
| on-device sha match | 11:09:4x | `154d9d85…` + `97c33955…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 11:09:5x | `logcat -c` then run — no idle window |
| on-device post-run re-sha | 11:09:5x | `97c33955…` FULL-match — intact |
| report-time re-sha | 11:10:26 | `97c33955…` FULL-match + ELF magic — **binary INTACT, no zero-damage recurrence this window** (4th matching read: build + pre-push + post-run + report) |
| G33/G34/G35/G36-binary track (report gate) | 11:10:26 | `7e0ea803…` (BUILD sha, stable — 12th recurrence stays closed) + `2b101dde…` (INTACT) + `e2998ffc…` (zeroed — gated 14th artifact, tabled §2a) + `6430dbe8…` (zeroed — gated 15th artifact, stable ×3, tabled §2a) — corroboration only, never in the push chain |

No validity-chain pin mismatched at any gate: the stop rule never
fired.

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g37/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g37/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g37-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790089795→1790089796; logcat 11:09:55) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G36) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G37: writeback` + 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 map-fails of any kind |
| logcat | 2376 lines (== G31's 2360 + 16 G37 exactly): init + 18 `Running frame` + 18 G10 + `Total time per VBlank: 12.007 ms` (same inflated class as G31's 9.194 / G32's 8.871 / G33's 12.064 / G34's 12.139 / G35's 12.049 / G36's 11.983 — diagnostic cost of 16 extra map+copy sans barrier inside the timed region, §2g) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical in G29–G36 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each) ALL pulled by explicit list (§3i); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (writeback + ladder + vpage + load line — continuity with G29–G36)

| receipt | observed |
| --- | --- |
| 16 `G37: writeback` | ALL `base=917504 n=917504 fnv=13bd6843a14ee366 nz=149724`, 0 map-fails — premise P1 HOLDS: the bytes placed were shrunken-tagged at write time, on every vsync, both passes, barrier or no barrier |
| 10 `G29: ladder` | ALL P1=P2=P3=FNV `debe0cda9c919bde`, nz=229379 == shrunken-model (§2d) — 10/10 1-pixel-exact, 0/10 cleared |
| 512 `G30: vpage` (all pass=1, pages 0..511) | 112/112 B pages == shrunken per-page oracle (page 112 == `eb42866db438f31c`/698 head `ffffff00…`, pages 113..223 == stale lines — the barrier-less 1-word store persisted in the host mapping through the loop); other 400/400 timestamp-stripped lines BYTE-IDENTICAL to G31's vpage (the write leg perturbed NOTHING outside the 1 tag word); ALL-pages==G31 511/512 (exactly page 112 differs — as constructed) |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz=1,184,729 == host load FNV — trailing-restart mechanism reproduced on-device a ninth time (restart control passes; the shrunken write did not perturb the reload path) |
| 16 A-lines | A-fields BYTE-IDENTICAL to G31's 16 A-fields (scene path untouched — non-perturbation proven beyond determinism; §3g) |

### 3g. Writeback + state + bytes verdicts (B1: shrunken source at every write and sample time)

Writeback lines (16/16 full receipts, 0 fallbacks):

| field | predicted | observed |
| --- | --- | --- |
| base / n | 917504 / 917504 ×16 | **16/16 EXACT** |
| shrunken-temp FNV / nz | `13bd6843a14ee366` / 149724 ×16 | **16/16 EXACT** — placed bytes were shrunken-tagged at write time |

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
| B (the P2 discriminator) | shrunken `13bd6843a14ee366` nz=149724 head=`ffffff00…` ×16 (B1) | **16/16 EXACT match — outcome B1**: the read leg sees shrunken B at EVERY sample time without any barrier or commit (B2: 0/16; B-neither: 0/16) |
| A (live control) | == G31's A (untouched), pass-repeat 8/8 | 16/16 A-fields BYTE-IDENTICAL to G31's; 8/8 EXACT pass-repeat |

### 3h. Split analysis (ANY-nonzero-RGB — the 1-word tag renders EXACTLY; higher-threshold refuted)

| link | evidence |
| --- | --- |
| write leg placed the 1-word tag (sans barrier, sans commit) | 16/16 temp == shrunken at write time (P1) + 16/16 B == shrunken at sample time (B1) + 112/112 vpage == shrunken per-page oracle — the read leg reads stale-or-shrunken, the single OR plants the 1-word tag, the raw write leg carries it into the host mapping WITHOUT any barrier or commit (content-exact, as constructed) |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0`) → `sample_quad[0]` + `buffers.gpu` on every vsync — same path as G31–G36 |
| source bytes at sample time | region B == shrunken (16/16 `13bd6843a14ee366`, 1/229376 nonzero-RGB words, tag alpha 0x00) — never stale-as-content, never transient-written, never torn |
| circuit output | 10/10 ladder P1/P2/P3 == shrunken-model `debe0cda9c919bde`/nz=229379; 10/10 scanouts byte-identical to the shrunken model (sha `34697c14…`, `cmp` identical, white-set == {(0,0)}, nonblack == 1, §3i) — equals the ANY(1) prediction EXACTLY |
| elimination | OTHER-premise never triggered (P1 holds — read path intact); B2/PARADOX never triggered (B1 unanimous — barrier-less 1-word stores persist); OTHER-mixed never triggered (no neither-nor output — every per-pixel triage rule but EXACT fired 0/10); HIGHER-THRESHOLD refuted 0/10 (no cleared ladder, no black scanout — shrinking the content 112 words → 1 word moved NOTHING off the exact-render model) |
| verdict | **ANY-nonzero-RGB with threshold = 1 word: a SINGLE nonzero-RGB word in B renders EXACTLY — no flush, no wait, no commit is necessary, and no quorum is required.** Same raw legs as G36, 1/112th the content, renders the 1-word tag EXACTLY (one white pixel at exactly the pre-registered corner (0,0)). The threshold > 1, per-page-quorum, and nonzero-alpha-only models are therefore refuted together — the tag word's alpha is 0x00, so alpha is proven NOT necessary either. What remains standing is the bare quantifier: ANY nonzero-RGB content suffices. Whether the threshold is RGB-specific or any-channel is the §4 wall, not this verdict. |

### 3i. Scanouts (10/10 pulled by explicit list — G31-E1 applied) + share mirror

Explicit pull list (12 files + logcat; each named, zero globs):
`g37-run-stdout.txt`, `g37-run-stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0.ppm` … `g10-vsync7.ppm`,
`g13-dump.gs.g8-first.ppm`, `g13-dump.gs.g8-last.ppm` (all 688,143 B).
All 12 pulls individually confirmed (`1 file pulled, 0 skipped`).
Cleanup ran as its OWN verified step AFTER pull verification
(`rm -rf` + `ls` → `mg/` only, exit 0).

| file | sha256 | vs ANY(1) shrunken model |
| --- | --- | --- |
| 10/10 scanouts | `34697c14ddac68db3529595d26eb9cf3e51584ae266848379aac22d1d219a276` (unanimous) | BYTE-IDENTICAL to `/tmp/g37-expected.ppm` (`cmp` 10/10 — 11-way unanimity incl. the host model) |

Pixel census (per file): exactly 1 white at (0,0) + 229375 black
pixels; white-set == {(0,0)} (the pre-registered corner — subset of
the G34 112-set, as predicted); nonblack pixels 1/229376 (no extras,
no smear — the single word lands crisply, no torn coherency, no
quorum-bleed, no misplacement).

Share-tier mirror (drive distrusted): all 13 `ps2x-g37/` files copied
by explicit name to `/Volumes/share/ssx3/ps2x-g37/`; `shasum -c`
13/13 OK against the SSD shas.

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 16 G37 + 32 G31 lines + all controls + `Done!` |
| second shape | NOT USED | out of budget by the stop rule (the channel-axis refinement is a new discriminator, §4, not a second shape here) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Placing a 1-word shrunken tag via G36's raw legs splits "ANY nonzero-RGB content" (threshold = 1) from higher-threshold models | **ANY-NONZERO-RGB(1) — decisively.** Shrunken source proven at every write time (16/16 `13bd6843a14ee366`/149724) and every sample time (16/16 B == shrunken, head `ffffff00…` — B1 unanimous), the barrier-less 1-word store persisted on its page (112/112 vpage == shrunken oracle, 511/512 ALL == G31 with exactly page 112 differing), and the circuit rendered the 1-word tag EXACTLY (10/10 ladders P1=P2=P3 == `debe0cda9c919bde`/229379, 10/10 scanouts byte-identical to the host 1-white-pixel model sha `34697c14…`, white-set == {(0,0)}). HIGHER-THRESHOLD is refuted 0/10 (threshold > 1, per-page-quorum, and nonzero-alpha-only fall together — the tag word's alpha is 0x00). B2/PARADOX/premise-break/mixed never triggered (every §2f triage rule but EXACT fired 0/10). One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **the channel-specificity
wall (alpha-only 1-word tag, same raw legs) — NOT adoption.**
Rationale: G37 proves RGB suffices at threshold 1 with alpha 0x00,
closing the threshold question (threshold = 1 word — the G35 §7.1
quantifier is answered) but leaving the channel axis open: §2b's T4
(tabled-but-unrun) asks whether an alpha-only 1-word tag
(`temp[0] |= 0xFF000000`, RGB stays 0) ALSO renders exactly — i.e.,
whether the threshold counts RGB words specifically or any-channel
nonzero words. The discriminator: the same 1-word raw-access
treatment with the mask moved to the alpha byte and per-channel
predictions pre-registered; ANY-channel predicts exact render,
RGB-specific predicts cleared. Queued behind it (not this action):
G26+G28 adoption — the brightness condition stays MET (output ==
content-render on every run to date: stale→cleared G31/G33,
pattern→pattern G32, tag→tag G34/G35/G36, 1-word→1-pixel G37 —
commit-independent AND barrier-independent AND quorum-independent)
but adoption stays queued per the standing rule until the orchestrator
gates it; the Adreno filing — STILL OPEN regardless (content upgrades
again: "a SINGLE nonzero-RGB word renders EXACTLY with no host
barrier or commit of any kind on the write path and no quorum —
neither the commit, nor any flush, nor any wait, nor any second word
is shown necessary"); G18-hunk fix adoption (still queued); O1 writer
naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk + pre-push + post-run + report) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G33 write-back hunk | stays EXCISED from the worktree (diff text survives committed in `local/research/G33/` — lossless) |
| G34 tagged write-back hunk | stays EXCISED from the worktree (diff text survives committed in `local/research/G34/` — lossless) |
| G35 commit-less write-back hunk | stays EXCISED from the worktree (diff text survives committed in `local/research/G35/` — lossless) |
| G36 raw-access placement hunk | EXCISED from the worktree by this brief's edit (diff text survives committed in `local/research/G36/` — lossless) |
| G37 additions | the ONE shrunken-tag raw-access placement hunk (SSD clone worktree only) + session files: `g37-build.sh` + `g37-run.sh` + `g37-shrunken-placement.diff` (G37-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g37/` ONLY (not in git) + verified share-tier mirror `/Volumes/share/ssx3/ps2x-g37/` (13/13 `shasum -c` OK); no PII (`uid: shell`); all 10 PPMs pulled (shas + census in §3i) |
| host analysis | `/tmp/g37-*.py` (hunk/predict/score) + `/tmp/g37-*.sh` (build/run) + `/tmp/g37-build.log` + `/tmp/g37-stub.cpp` + `/tmp/g37-*.diff` extracts + `/tmp/g37-*.txt` (g22check/share-check/whites/vpage) + `/tmp/g37-expected.ppm` + REUSED `/tmp/g34-predict.py` (unmodified re-run) + `/tmp/g34-expected.ppm` + `/tmp/g34-vpage*.txt` + `/tmp/g34-whites.txt` (session-only) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (G36 end state)
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (pre+post+pre-push+post-run+report)
shasum -a 256 <g28..g37 binaries> + xxd magic (x2+ for g34/g35/g36: PASS1+PASS2+report)  # §2a (g28-g34 INTACT/BUILD-stable, g35/g36 zeroed-gated)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match (x3+ this session)
du -sk <ps2x-g7..g37 + 16 build dirs> ; df -h / $SSD           # §0 (pre 11:00:53 + post 11:10:2x)
python3 /tmp/g34-predict.py                                       # §2e (REAL G34 predictor, unmodified: ALL CHECKS PASS)
python3 /tmp/g37-predict.py                                       # §2e (G37 derivation, reused renderer: ALL CHECKS PASS)
python3 /tmp/g37-hunk.py --dry                              # §2g (DRY-OK: G36x1 pre-anchor, anchorx1, 1-word-OR present)
clang++ -std=c++17 -Wall -Wextra -fsyntax-only /tmp/g37-stub.cpp  # §2g STUB_SYNTAX_OK (stub-artifact warnings only)
python3 /tmp/g37-hunk.py                                    # §3b (ONE single-write edit: -59/+56, shrunken tag)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff -U1 | grep '^@@'  # hunk shape (160 = 163-59+56; single @@ ours)
cmake -S <clone> -B $SSD/parallel-gs-g37-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g37-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g37-binary> (build, pre-push, post-run, report)  # 97c33955… x4 match (intact)
llvm-readelf --notes <g37-binary> ; strings grep 3/0/0/0/0/1/2/1/1/1/2/1/1/2/0 ; xxd -l 4  # 722427ed… + ELF
python3 /tmp/g37-score.py                                       # §3f–3i (16/16 + B1-16/16 + 10/10 + 112/112 + 511/512 + 1PX x10 + ANY(1))
cmp /tmp/g37-expected.ppm $SSD/ps2x-g37/<each of 10 PPMs>        # §3i (ANY(1) == model x10, byte-identical)
cp <13 ps2x-g37 files by name> /Volumes/share/ssx3/ps2x-g37/ ; shasum -c  # §3i (mirror 13/13 OK)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g37/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g37 && mkdir -p /data/local/tmp/g37'
push <dump> $G37DIR/g13-dump.gs ; push <g37-binary> $G37DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G37DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G37DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g37-run-stdout.txt 2> g37-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (ANY(1) fired)
logcat -d -s Granite:V > $SSD/ps2x-g37/g37-logcat.txt                # 2376 lines
pull $G37DIR/g37-run-stderr.txt $SSD/ps2x-g37/ (0 B) ; pull stdout (0 B)
pull $G37DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g37/   # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G37DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # 97c33955… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g37 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The channel axis (RGB-specific vs any-channel threshold —
   §2b's T4, alpha-only 1-word tag) is untested — the treatment
   places an RGB-white word with alpha 0x00. Queued as the §4 next
   action (channel-specificity wall: same raw-access legs, alpha-byte
   mask, per-channel predictions; ANY-channel predicts exact render,
   RGB-specific predicts cleared). No alpha tag was run here (ONE
   hunk max).
2. The ANY(1)-vs-higher-threshold split AS REGISTERED is CLOSED
   (ANY-nonzero-RGB(1) wins, higher-threshold refuted) — not a gap;
   recorded so no future brief re-litigates it. The G35 §7.1
   quantifier is answered (threshold = 1 word); every higher model
   is now dead (threshold > 1, per-page-quorum, and
   nonzero-alpha-only all 0/10 G37).
3. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the host swizzle model is this brief's oracle and
   matched byte-exactly, 11-way sha unanimity with the model PPM).
4. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
5. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G37 binary intact at all four).
6. G26+G28 adoption is queued, not done (brightness condition STAYS MET
   per §4 — but adoption stays queued per the standing rule until the
   orchestrator gates it; no port, no upstream contact).
7. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
8. The G36 binary reads fully-zeroed all session (`6430dbe8…`, magic
   `00000000` — the brief's gated 15th read artifact, re-pinned ×3
   separated: PASS1 + PASS2 + report) after reading intact at G36 time
   (`4e68911d…`, ELF) — tabled as an OBSERVATION: the link's
   pattern-dependent corruption keeps recurring on large binaries; no
   verdict (forensics is out of scope; no lane data depended on the
   G36 binary bytes — all G36 receipts live in `ps2x-g36/` + the share
   mirror, and the G36 binary was explicitly OUT of G37's chain).
   (The G35 binary's gated 14th artifact likewise persists, `e2998ffc…`.)
9. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
10. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
11. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes + cmake noise); zero
    warnings point at the hunk lines.
12. The raw-`begin_host_vram_access`-then-never-closed nesting is now
    proven empirically ×16 more (G37 — 1-word barrier-less stores
    persist and the unbalanced raw access never crashes), joining
    G36 ×16 + G35 ×16 uncommitted/commit-less nesting + G33 ×16 + G34
    ×16 committed nesting (80 total host-access cycles without
    incident) — not by a second independent writer.
13. Which memory the sampler reads (host-visible mapping vs device-side
    copy) is narrowed but NOT fully isolated by this wall: B1 proves the
    host mapping held the 1-word tag at sample time with zero write-path
    ordering ops, and the output proves the sampler rendered it — so no
    host-side flush/wait/commit/quorum stands between a SINGLE CPU store
    word and the sampled image in this path. The exact transport
    (direct host-mapping read vs a coherent interconnect/copy that needs
    no host ordering) remains unisolated — but any transport model must
    now explain single-word-exact rendering with zero host-side ordering
    ops. No claim beyond the hypothesis is made here.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g37/` (13 files:
  `g37-logcat.txt` 2376 lines incl. 16 `G37: writeback` + 16 `G31: state` +
  16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g37-run-stderr.txt` 0 B, `g37-run-stdout.txt` 0 B, 10 scanout PPMs
  688,143 B each sha `34697c14…` unanimous) +
  `parallel-gs-g37-android-build/` (binary 265,853,016 B
  `97c33955…` BuildID `722427ed…`, intact at report time).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g37/` (13/13 files,
  `shasum -c` ALL OK — drive distrusted, §2a).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g36/` + G14/G18/
  G20/G22/G24/G26/G28/G29/G30/G31/G32/G33/G34/G35/G36 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 + G37 hunks uncommitted (G36 excised);
  Granite `16e7395f…` + G20-capture set + G28 hunk, all uncommitted —
  ZERO commits anywhere).
- Session-only: `/tmp/g37-*.py` (hunk/predict/score),
  `/tmp/g37-*.sh` (build/run), `/tmp/g37-build.log`,
  `/tmp/g37-stub.cpp`, `/tmp/g37-*.diff` + `/tmp/g37-*.txt` extracts,
  `/tmp/g37-expected.ppm` (host oracle, `34697c14…`) +
  `/tmp/g37-vpage.txt` + `/tmp/g37-whites.txt`, REUSED
  `/tmp/g34-predict.py` + `/tmp/g34-expected.ppm` + `/tmp/g34-vpage*.txt`
  + `/tmp/g34-whites.txt`.
- Commits: ssx3 `local/research/G37/` `[G37]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G37 report ends here. Task-1 statics tabled the
threshold candidates (T1 single-word-of-one-page CHOSEN over T2
single-page / T3 sparse-subset / T4 alpha-only, with the
already-dead status of nonzero-alpha-only as a full-tag theory
derived on record) + the ONE picked shrunken tag (word 0 of page 112
only, `0x00FFFFFF`, alpha 0x00) + the premise rows (P1
shrunken-temp receipt MUST-hold + P2 B1/B2/B-neither split with
pre-registered verdict meanings + P3 controls) + pre-registered every
ANY(1)/higher-threshold scalar (shrunken `debe0cda9c919bde`/229379 +
1-white PPM `34697c14…` at (0,0) vs cleared `aa2fa32572450383`/229376
+ black `99418f1b…`) via the reused G34 renderer (G34 predictor
unmodified ALL CHECKS PASS + G37 derivation ALL CHECKS PASS) + a
six-row decision matrix with seven per-pixel triage rules. ONE
shrunken-tag raw-access hunk (+56/−0, G36 +59 excised same edit) +
ONE build exit 0 + ONE run exit 0 with 16/16 shrunken-temp + 16/16 B1
shrunken-B + 112/112 shrunken-oracle vpages + 10/10 shrunken-model
ladders + 10/10 1-pixel-exact scanouts proves ANY-nonzero-RGB(1)
(threshold is 1 word; alpha not necessary) and refutes
higher-threshold (0/10 cleared). Next wall is the channel-specificity
wall (alpha-only 1-word tag, same legs), not adoption; filing still
open (G31-E1 applied: explicit pull list, separate cleanup; share
mirror 13/13 OK).

Outcome: ANY-nonzero-RGB with threshold = 1 word — a SINGLE
nonzero-RGB word renders EXACTLY with zero write-path ordering ops
and zero quorum (CPU stores alone suffice down to one word);
higher-threshold (threshold > 1, per-page-quorum, nonzero-alpha-only)
refuted. No tuning loop was entered: one hunk, one build, one device
run. Retry not used (exit 0); lldb not used (zero new tombstone —
nothing to triage).
