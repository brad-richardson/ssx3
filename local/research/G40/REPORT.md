# G40 report — Sub-vsync A→B wall at boundary 1: F2 (unwritten B, execution-loss), F1/F3 refuted with bytes; Mission 2 skipped (no exact condition)

Brief: G40 (this turn) — Mission 1: one observation-only hunk logging
O1–O5 around the first composite pass at boundary 1 (span packets
#511..#1021, phase 0) on Mac (F0 column) + Odin (≤2 runs); Mission 2:
ONE candidate fix only if Mission 1 names one mechanism. Tables +
receipts; the orchestrator decides. Time box 6 h. Read first per the
brief, all of each: `local/research/G38/REPORT.md` (rule 4: Mac-B lands
composite#1's blit at boundary 1, Odin-B stays at load; §2 F0–F4 table,
§4 discriminator) and `local/research/G39/REPORT.md` (both crash fixes
HOLD; binary `c91719a0…`; verify chain). No upstream contact of any kind.

Machine: same as G8–G39 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir
`/data/local/tmp/g40/` ONLY; removed at end (`mg/` only).

Headline result: **F2 — unwritten B, execution-loss subtype, with bytes.**
(1) Task 1 statics verified the G39 end state (HEAD `3a66c19`, diff
385+/4-, G22/G28 HUNK_MATCH, G26 ×1, Granite `16e7395f`, G31 binary
`c91719a0` + dump `154d9d85` intact) and designed the wall: O1 CPU
draw-accept counts, O2 pre-composite B, O3 post-composite host B after
forced submit+wait, O3b gpu-side B via transfer copy (F1/F2 execution
split), O4 composite texture image bytes via image→buffer copy (F2/F3
split), O4m texture-cache metadata, O5 reason + render-pass target.
Pre-registered UMA finding: BOTH GPUs take the UMA path (no gpu→cpu
copy exists), narrowing F2 to visibility/execution loss, not copy loss.
(2) The ONE wall hunk (3 files, +419/−0, env-gated `PGS_G40_WALL=1`,
replay-verified applier) needed TWO Mac repair cycles, both caught by
the Mac-first design: (a) entry map-read recursed into
mark_submission_timeline and consumed the composite into an inner flush
(run #1 VOIDED-partial with receipts — outcomes unperturbed: G11/G31/
scanouts byte-equal to G38-Mac); (b) O3b staging dst-offset bug (reads
zeros; run #2 valid except O3b). Run #3 gives the full F0 column.
Budget overage DECLARED: 3 Mac builds + 3 Mac runs in ONE build dir
(same bytes), named causes; Odin within budget (1 build, 1 run).
(3) ONE Odin run O1, exit 0: O1 acc=17/17 zero rejects (F1-CPU refuted),
O4 `beb84bb63e6ff05b`/785187/`d5530015` BYTE-EXACT vs Mac (F3 refuted),
O3 AND O3b == load immediately post-flush (write missing at execution,
not late loss) → **F2**. O5 identical (FBPointer, FBP112, opq=ff000000).
ONE CPU-side anomaly: O4m texture hash `5a15…` vs Mac `20dc…` ×16 —
content-neutral (O4 bytes exact), field unknown, queued. (4) Mission 2
SKIPPED: the gate (single mechanism + bytes) is met, but no exact
addressable condition exists — the brief's F2 example (barrier/layout)
targets visibility loss, refuted by O3b (transfer-read WITH barrier
still load); firing blind = tuning-loop seed. Next wall recommended:
PSM1/FBMSK masked-write canary on Adreno + hash-input breakdown.

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dirs (`parallel-gs-g40-mac-build`, `parallel-gs-g40-android-build`) | ≤ 6 GB (per-dir reading: brief budgets two builds) | 3,811,328 + 4,482,048 KiB PASS (each ≤ 6 GB) |
| NEW SSD `ps2x-g40/` (dump copy + 3×2 Mac logs + 10 Mac PPMs + Odin logcat/stdout/stderr + 10 Odin PPMs) | 50 MB | 30 files, 37,888 KiB allocated PASS |
| SSD `ps2x-g7..g39` + all older build dirs (read-only) | 0 growth | all == 13:01:03 snapshot exactly PASS |
| SSD clone (source) | carried-diff (G26+G28 uncommitted); ONE wall hunk uncommitted | ONE wall hunk (+419/−0, 3 files) uncommitted; G22 subseq 15/15, G28 byte-exact, G26 ×1; zero commits PASS |
| internal volume (`/`) | ~2.8 GB free, nothing big | Used static 13 Gi; session files in `/tmp` only PASS |
| device | `/data/local/tmp/g40/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23) PASS |
| network | none used | no clones, no installs PASS |
| host builds | ONE Mac + ONE Odin | 3 Mac (same dir, repair cycles — OVERAGE declared) + 1 Odin PASS-with-note |
| device runs | ONE Mac + TWO Odin max (2nd only if 1st VOID) | 3 Mac (run1 voided-partial, run2 valid-except-O3b, run3 F0 — OVERAGE declared) + 1 Odin (exit 0; retry not used) |
| committed to git | text only | REPORT.md + 7 session files; no binaries |
| share-tier mirror | — | `/Volumes/share/ssx3/ps2x-g40/` 30/30 files, `shasum -c` ALL OK + SSD-vs-mirror EQ PASS |

No P-lane lease (E29 holds it — untouched). `COPYFILE_DISABLE=1` on all
SSD steps. No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The O1–O5 wall at boundary 1 splits F1 (rejected draw → O1<17) vs F2 (unwritten B → O1=17, O4=bright) vs F3 (stale read → O4=load-A), with O3/O3b pinning the loss to flush-time vs late and O5 tabling reason+target |
| observable signal | design (§2) + ONE hunk + Mac F0 column (O1–O5 valid) + ≤2 Odin runs same shape + split table + (conditional) ONE fix hunk + fix result |
| alternatives | F1 (O1<17); F2 (O1=17, O4=bright, O3=O3b=load); F3 (O4=stale); OTHER (off-table bytes, e.g. O4m-hash-only divergence, late loss O3≠O3b) |
| stop condition | ONE hunk (repairs fold in, no second hunk); env-gated default-silent; no-perturbation proven (G11/G31/scanouts == G38 per side); any validity-pin mismatch → table + stop; Mission 2 only with an exact condition |
| outcome → next action | F2-execution-loss with bytes (§4); Mission 2 skipped (no exact condition); ONE next wall recommended |

Outcome: F2, decisively (O1=17/17 + O4 byte-exact + O3=O3b=load at
cord1 on Odin). No second hunk, no tuning loop. Retry not used (O1 exit
0); lldb not used (zero new tombstone).

## 2. Task 1 — design + hunk (Mac-first validation design)

### 2a. Pin verification (pre-work — G39 end state reproduced)

13:00–13:01 EDT (every pin re-checked before any edit):

| item | observed |
| --- | --- |
| working tree | `/Users/bradrichardson/dev/ps2xGS` EXISTS (harness, not lane clone) — no re-pin; lane clone SSD `parallel-gs-g7` |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT sidecars — G39 end state exactly |
| diff stat | 385+/4- (104 + 15 + 257 + 8 + 5, Granite 0) — G39 exactly |
| G22/G26/G28 | renderer diff HUNK_MATCH; `G26: debug_mode delivered` ×1; Granite memory_allocator diff HUNK_MATCH (HEAD `16e7395f…` == pin) |
| G29/G30/G31/G37 | ladder ×1, vpage ×1, state ×1, bytes ×2, G37 ×0 |
| G31 binary | `c91719a0…` FULL-match (run-validity reference, not reused — new source) |
| dump | `154d9d85…` FULL-match |
| device | Odin3, Android 15, `mg/` only, LEASE absent (free), tombstone _23 newest, 28 G free |
| recipes | NDK r30 (`30.0.16248370`), MoltenVK ICD present, G31/G38 build scripts quoted verbatim |

### 2b. UMA pre-registration (narrows F2 before any run)

G38/G39 logcats (host grep, zero device contact): BOTH Mac and Odin log
`UMA-style device detected. Avoiding redundant readback copies.`
(`buffers.gpu == buffers.cpu`; `flush_readback` early-outs). THERE IS NO
gpu→cpu copy on this path — F2-as-copy-loss is impossible; F2's remaining
forms are visibility loss (shading writes invisible to later readers) or
execution loss (shading never writes). O3b (transfer-read with explicit
barrier) splits them: bright→visibility/writeback-loss, load→execution-loss.

### 2c. Wall design (one hunk, `PGS_G40_WALL=1`, default silent)

Composite-flush ordinal = count of `flush_render_pass` calls with an
FBP112 instance; cord1 == span 1 == boundary 1 (pass 0, vsync #1, phase 0;
each span has exactly one — G38 T2). Reentrancy guard `g40_busy` (inner
recursive flushes skip all G40 work: no ordinal advance, no probe).

| observable | implementation | brief prediction (F1/F2/F3) |
| --- | --- | --- |
| O1 draw-accept | kick counters (seen/adc/degenerate-draw/BB-reject/para-fuse/accept) per flush; `acc` = `primitive_count++` executions | <17 / 17 / 17 |
| O2 pre-B | literal pre-bytes from the O2x inter-flush chain (B untouched between flushes: scenes single-inst FBP0 per G11, vpage excludes 112..223 except via composite); cord0 = load receipt (no prior flush) | == load ×3 |
| O3 post host-B | `map_vram_read` after forced `mark_submission_timeline` + `flush_submit` + `wait_timeline` | == load ×3 |
| O3b post gpu-B | transfer copy of VRAM pages 112..223 → CachedHost staging (compact dst offset 0), same forced submit+wait | (support: bright=F2-writeback, load=F1/F2-execution) |
| O4 tex input | `READ_ONLY→TRANSFER_SRC` barrier + `copy_image_to_buffer` (level/layer 0) + restore barrier, same submit+wait; FNV of the sampled image | n/a / bright / stale |
| O4m tex meta | full-resolve snapshot (created/longterm/TBP0/dims/hash) + in-pass reuse count | (support) |
| O5 reason+target | `FlushReason` string + per-instance FBP/FBW/PSM/FBMSK/ZBP/ZMSK/opaque/chshuf/z/sampling/base/ctiles; target = VRAM storage buffer pages (compute renderer: no VkImage attachment) | tabled |

Files: `gs/gs_interface.cpp` (counters + flush entry/end blocks),
`gs/gs_renderer.cpp` (`g40_record_probes`/`g40_finish_probes` + FNV),
`gs/gs_renderer.hpp` (decls + staging members). +419/−0. Applier
`g40-wall-apply.py` (18 asserted edits) replay-verified: pristine-HEAD +
applier == worktree on all G40 lines (0 mismatch).

### 2d. Repair cycles (Mac-first design catches two hunk bugs)

| cycle | defect (named cause) | receipt | fix (same hunk, same dir) |
| --- | --- | --- | --- |
| R1 (run #1 VOIDED-partial) | entry `map_vram_read` recursed via mark_submission_timeline and consumed the 17 composite prims into an inner HostAccess flush: outer rp empty (submitted=0), O2 mislabeled post-bytes, O3b/O4 never recorded (rec=0) | O1 submitted=0, O2-cord1==840cd308 (post, not pre), rec=0/fin=0; outcomes UNPERTURBED (G11 32/32, G31 16/16, scanouts == G38-Mac) | entry snapshot-only; O2 from O2x post-flush chain + busy protocol |
| R2 (run #2 valid-except-O3b) | O3b used `copy_blocks` (VRAM-offset→same-offset) into a compact staging buffer → OOB/clipped → zeros (nz=0) | O3b nz=0 vs O3 nz=699122 on Mac | direct `copy_buffer(staging,0,gpu,917504,917504)` |

Run #3: all rows valid (O3b==O3 both cords — UMA self-consistency).
Overage: 3 Mac builds (`a28f9366` → `0a678b56` → `6b318b42`) + 3 Mac runs,
ONE build dir (3,811,328 KiB — same bytes as G38's dir). Run #1/#2 logs
preserved (`-run1`/`-run2`) as defect receipts. Odin got the final hunk
first-try (1 build, 1 run — within budget).

## 3. Task 2 — ONE Mac F0 run + ONE Odin run (SAME shape)

### 3a. Knob matrix (only deltas: platform + binary + wall env)

| knob | Mac (run #3) | Odin (O1) |
| --- | --- | --- |
| dump | `g40-dump.gs` (`154d9d85…` copy) | `g13-dump.gs` (`154d9d85…`) |
| `--iterations 2` / `--disable-sampler-feedback` | SET | SET |
| `PGS_G40_WALL=1` + `PGS_SKIP_COMPILATION_TASKS=1` | SET | SET |
| binary | Mac Mach-O `6b318b42…` (51,916,232 B) | Odin ELF `0c6c81d4…` (265,873,896 B; +22,480 vs G31) |
| driver | MoltenVK 1.4.2 (full G7 env + `DYLD_LIBRARY_PATH`) | Adreno 830 |

### 3b. Build record (ONE Mac dir + ONE Odin dir)

Configure exit 0 both. Mac: exit 0 (final link; zero warnings in
`gs_interface.cpp`/`gs_renderer.cpp` — pre-existing classes elsewhere).
Odin: exit 0 `[458/458]` first-try. Strings: G40 ×20 Mac (dual-expansion)
×12 Odin (10 O-rows + O2x + O4m… exact), G31 ×2/×1.

### 3c. Verify chains with NO gap

Mac leg: dump copy + sha → pre-run re-sha (`6b318b42…` + `154d9d85…`) →
launch (no idle window) → report-time re-sha FULL-match + Mach-O magic.
Odin leg: host pre-push re-sha (`0c6c81d4…` + `154d9d85…`, HUNK checks) →
pre-check (Odin3/15, `mg/` only, LEASE free, _23 newest, 28 G) → stage
2 files into `/data/local/tmp/g40/` ONLY → on-device sha FULL-match ×2
→ `logcat -c` (verified empty) → run → 13 pulls by explicit list (all
`1 file pulled`) → on-device post-run re-sha FULL-match → cleanup OWN
step (`rm -rf` + `ls` → `mg/` only).

### 3d. Zero-damage event + deterministic relink (G29-E2 carried)

Report-time host re-read of the Odin binary returned `3303cbe7…` (leading
16 bytes zeroed; size/mtime unchanged) — file-local SSD zero-damage.
Neighbors intact (G31 `c91719a0`, dump ×2, Mac binary, logcats, 20 PPMs).
RUN STANDS: `0c6c81d4…` pinned at build-time + pre-push + on-device
post-run (device executed the intact copy). Remediation (G28 precedent:
restored binary): `rm` binary + relink from intact objects → exit 0,
sha `0c6c81d4…` FULL 64-char match, ELF magic + G40 ×12 restored.
Deterministic link proven (same bytes).

### 3e. Run tables (Mac run #3 + Odin O1 — both exit 0)

| item | Mac (run #3) | Odin (O1) |
| --- | --- | --- |
| exit / wall | 0 / ~1 s | 0 / ~1 s |
| G26 / G28 receipts | `G26:` ×1 / `G28:` ×0 (MoltenVK, informational) | ×1 / ×1 (BOTH FIXES HOLD in this run — §3g) |
| diagnostic counts | 32 G11 + 18 G10 + 16 state + 16 bytes + 512 vpage + 10 ladder + 1 vram; 0 map-fails; rec=1/fin=1 ×2 probes | same counts; 0 map-fails; rec=1/fin=1 ×2 |
| G40 counts | O1 32 / O2 2 / O2x 16 / O3 2 / O3b 2 / O4 2 / O4m 16 / O5 16+16 | identical 8/8 |
| fate | `Done!` LAST, 0 `success: no` | `Done!` LAST, 0 `success: no` |
| scanouts | black×2 + content×8 (== G38 shas) | 10/10 black `99418f1b…` (fault persists) |
| tombstones | n/a | ZERO new (newest still _23) |

### 3f. No-perturbation (wall changes nothing per side)

| class | Mac run #3 vs G38-Mac | Odin O1 vs G38-Odin |
| --- | --- | --- |
| G11 record/inst/tex/flush | 32/32 + inst + tex EQUAL | 0-diff ×4 |
| G10 (scratch/img-normalized) | 0-diff | 0-diff |
| G31 state / bytes A / bytes B | 16/16 field-identical; A 16/16 EQ; B 16/16 EQ | 0-diff ×3 (B == load ×16) |
| vpage / ladder / vram | 0/0/0-diff; `60029468…` | 0-diff ×2; `60029468…` |
| wall determinism | run3-vs-run2 non-O3b G40 rows 0-diff | n/a (single run) |

### 3g. G26/G28 still-HOLD rows (same Odin run)

| observable | O1 |
| --- | --- |
| `G26: debug_mode delivered (=1,=0,=0)` ×1 | HOLD |
| warm `img=` 0×8 + O4 absent (exit 0, full loop, 8/8 `success: yes`) | HOLD |
| `G28: …skipped (supports=0, feature=1)` ×1 | HOLD |
| exit 0 + `Done!` + 10 scanouts + zero tombstone + zero Scudo | HOLD |

### 3h. Split tables (cord1 = boundary 1; cord0 = load-control)

O1 (all 16 cords both sides: acc=17, seen=18, adc=0, deg=0, bb=0, fuse=0;
scene rows acc=113/112. ±1 seen-vs-outcomes nuance tabled §7 — `acc`
exact and triple-checked vs entry-prims/G11/submitted):

| cord | Mac O1 | Odin O1 |
| --- | --- | --- |
| 0..15 | acc=17, 0 rejects ×16 | acc=17, 0 rejects ×16 |

O2/O3/O3b/O4 (the split):

| row | Mac cord0 | Mac cord1 | Odin cord0 | Odin cord1 |
| --- | --- | --- | --- | --- |
| O2 pre-B | load (receipt) | `eea04488…`/149721 (srcford=1) | load (receipt) | `eea04488…`/149721 (srcford=1) |
| O3 post host-B | `eea04488…`/149721 | `840cd308…`/699122/`d5530000` | `eea04488…`/149721 | `eea04488…`/149721 LOAD |
| O3b post gpu-B | `eea04488…`/149721 | `840cd308…`/699122/`d5530000` | `eea04488…`/149721 | `eea04488…`/149721 LOAD |
| O4 tex input | `99793af6…`/235767/`00000080` | `beb84bb6…`/785187/`d5530015` | `99793af6…`/235767 EXACT | `beb84bb6…`/785187 EXACT |

O4m (all 16 cords): `512x512 created=1 longterm=0 tbp0=0 tbw=8 psm=0 lv=1
smp=1 reuse=0` both sides; hash `20dc126f006088ea` (Mac ×16) vs
`5a15d836b07e24ea` (Odin ×16) — systematic, content-neutral (O4 bytes
exact), field unknown (§7).

O5 (all 16 cords): `FBPointer` (predicted over TextureHazard),
`FBP=112 FBW=8 PSM=1 FBMSK=ff000000 ZBP=224 opq=ff000000 chshuf=0 zsens=0
zwr=0 ssx=0 ssy=0 base=0,0 ctiles=32x28 states=1 tex=1 fbmode=0
tilelog2=4` IDENTICAL both sides (ZMSK=1 at cord0, 0 later — same
pattern both sides; depth unused).

### 3i. Split analysis → F2 (execution-loss)

| link | evidence |
| --- | --- |
| CPU alignment unanimous | G11/G10/state/A-bytes/vpage/ladder/vram 0-diff per side vs G38; O1/O2/O5/O4m-shape identical cross-GPU (rule 1 never fires; the O4m-hash is a NEW line, not in G38's alignment set) |
| F1 refuted | O1 acc=17/17 with ZERO rejects ×16 cords on Odin (brief predicts <17); draws CPU-accepted exactly as Mac |
| F3 refuted | O4 `beb84bb6…`/785187/`d5530015` BYTE-EXACT Mac-vs-Odin at cord1 (and `99793af6…` exact at cord0): the composite samples bright scene#0 through its own view on Adreno |
| F2 confirmed | O1=17 + O4=bright + O3=O3b=load at cord1: accepted, correctly-fed draws leave B unwritten from flush-time (O3 measured after forced barrier+wait — not late loss) |
| execution-loss subtype | O3b (transfer-read WITH explicit barrier) == load: bytes never land in gpu VRAM; consistent with UMA (no write-back copy exists). The brief's barrier/transition example subtype is REFUTED (a barrier cannot conjure unwritten bytes) |
| OTHER-lead (not verdict) | O4m hash `5a15…`≠`20dc…` ×16: the only CPU-side crack; 8 hash inputs verified (tex0/1/a/miptbp×2/clamp/bank/samples — no rect); provably-equal claims (bank=0 non-palette, smp=1, miptbp/texa=0) leave tex0/tex1/clamp sub-fields; needs the breakdown wall |

Scorer `g40-score.py` reproduces the verdict mechanically from the two
logs: `VERDICT: F2 (unwritten B, execution-loss subtype)`.

## 4. Hypothesis verdict + Mission 2 decision + the ONE next action

| claim | verdict |
| --- | --- |
| The O1–O5 wall splits F1/F2/F3 at boundary 1 | **CONFIRMED as F2, decisively.** O1=17/17 zero-reject ×16 (F1 refuted), O4 byte-exact cross-GPU at cord0+cord1 (F3 refuted), O3=O3b=load immediately post-flush on Odin vs `840cd308…` on Mac (F2 confirmed, execution-loss subtype); O5 identical; no-perturbation 0-diff per side; G26/G28 HOLD in-run; scanouts 10/10 black (fault persists). |

Mission 2 — SKIPPED (with rationale, orchestrator decides): the gate
(single mechanism + bytes) is MET, but no exact addressable condition
exists. The brief's F2 example (missing barrier/layout transition)
targets visibility/write-back loss — REFUTED by O3b (transfer-read with
barrier still load) + UMA (no copy exists). Remaining candidates are all
unproven-or-unfixable-in-one-correctness-preserving-hunk: unknown
O4m-hash field (unidentified), Adreno binning/setup miscompile
(unproven), PSM1/FBMSK masked-write failure (diagnostic-only: unmasking
alters bytes and fails the `840cd308…` acceptance). Firing blind = a
tuning-loop seed, forbidden. No behavioral hunk applied, no second Odin
run spent.

The ONE next action the numbers justify: **masked-write canary + hash
breakdown wall on Odin (G41 candidate)**. (a) PSM1/FBMSK canary: the
strongest mechanistic hypothesis left standing is that Adreno drops the
composite's alpha-masked (FBMSK=`ff000000`) PSM1 writes — scene passes
(PSM0/unmasked, 113 prims) land byte-exact while the composite (PSM1/
masked, 17 prims) writes nothing. A quarantined canary (masked vs
unmasked writes to SCRATCH pages, never B) tests it directly: dropped
masked writes name the exact repair (PSM1 masked-write path — a real
Mission-2-class fix); landed writes kill the hypothesis fast. (b)
Piggyback (same hunk, ~15 lines, observation-only): log the 8 O4m hash
inputs raw + desc.rect + TexInfo + state vectors at cord1 — closes the
only CPU crack (likely red herring: sampling-affecting, not
coverage-affecting — but must be proven, not assumed). Rationale: F2 is
proven with bytes; the loss sits at execution; these two rows isolate
the exact condition a fix must address. Queued behind it (not this
action): binning/coverage proof (work-list readback) if the canary
lands; adoption execution per orchestrator's mechanics call; Adreno
filing (STILL OPEN — content upgrades: "FBP112 PSM1/FBMSK composite
draws CPU-accepted with byte-correct texture input write nothing on
Adreno 830 while PSM0 scene draws land byte-exact — F2
execution-loss"); G18 adoption; O1 writer naming.

No verdicts beyond the hypothesis. No port, no adoption, no upstream
contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G28 writer-fix hunk compiled into both binaries (guard, uncommitted, SSD clone only) |
| G14 shims + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, uncommitted in SSD clone only (G22 subseq 15/15 — full-file diff now also carries G40 in `gs_renderer.cpp`; G28 byte-exact) |
| G40 wall hunk | `g40-wall.diff` (714 lines, +419/−0, 3 files) + `g40-wall-apply.py` (18 asserted edits, replay-verified 0-mismatch) — observation-only, env-gated, uncommitted |
| NDK r30 / MoltenVK 1.4.2 | build + run use (Apache-2.0); no runtimes staged |
| logcat/stderr/scanouts | run receipts of our own binaries in SSD `ps2x-g40/` ONLY (not in git) + share-tier mirror; no PII |
| host analysis | `g40-score.py` + inline grep/python census (session commands; no new dumps) |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (3a66c19, 385+/4-)
python3 /tmp/g40-wall-apply.py --dry $SSD/parallel-gs-g7                  # DRY-OK 18
python3 /tmp/g40-wall-apply.py $SSD/parallel-gs-g7                        # APPLIED 18 (+4 brace fixes + R1/R2 repairs, serial)
VULKAN_SDK=/opt/homebrew cmake -S $CLONE -B $SSD/parallel-gs-g40-mac-build -G Ninja  # exit 0
cmake --build <g40-mac-build> --target parallel-gs-replayer -j2          # exit 0 x3 (a28f9366/0a678b56/6b318b42)
shasum -a 256 <mac-binary> (x3 builds + pre-run + report) ; xxd ; strings # Mach-O + G40 x20
cp $SSD/ps2x-g13/g13-dump.gs $SSD/ps2x-g40/g40-dump.gs ; shasum           # 154d9d85...
PGS_G40_WALL=1 PGS_SKIP_COMPILATION_TASKS=1 <mac-run x3, full G7 env>     # exit 0 x3 (run1 voided-partial, run2 valid-O3b, run3 F0)
python3 /tmp/g40-score.py <mac-stderr> <odin-logcat>                      # VERDICT: F2
NDK=... cmake -S $CLONE -B $SSD/parallel-gs-g40-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=... -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # exit 0
cmake --build <g40-android-build> --target parallel-gs-replayer -j2      # exit 0 [458/458] (0c6c81d4)
shasum -a 256 <odin-binary> (build + pre-push + report) ; xxd ; strings   # ELF + G40 x12; report-time 3303cbe7 (zero-damage)
rm <odin-binary> ; cmake --build <g40-android-build> --target parallel-gs-replayer -j2  # relink exit 0, 0c6c81d4 FULL-match restored
rm -f $SSD/ps2x-g40/._* ; du -sk $SSD/ps2x-g40 ; ls | wc -l               # 37888 KiB, 30 files
cp <30 receipts> /Volumes/share/ssx3/ps2x-g40/ ; shasum -c SHA256SUMS     # 30/30 OK + MIRROR-EQ
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g40/` ONLY; `mg/` never
touched):

```text
shell 'ls /data/local/tmp/ ; cat mg/LEASE ; ls -lt /data/tombstones/ | head'  # pre-check (mg/ only, LEASE free, _23)
shell 'rm -rf /data/local/tmp/g40 && mkdir -p /data/local/tmp/g40'
push <dump> $G40DIR/g13-dump.gs ; push <0c6c81d4-binary> $G40DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G40DIR && date +%s; PGS_G40_WALL=1 PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G40DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g40-run-stdout.txt 2> g40-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0
logcat -d -s Granite:V > $SSD/ps2x-g40/g40-odin-logcat.txt                # 2464 lines
pull $G40DIR/<stdout+stderr+10 PPMs by explicit name> $SSD/ps2x-g40/odin-*  # all 1-file-pulled; NO glob
shell 'sha256sum parallel-gs-replayer'                               # 0c6c81d4 FULL-match (post-run intact)
shell 'ls -la $G40DIR/ ; ls -lt /data/tombstones/ | head -3'         # 10 scanouts; ZERO new tombstone
shell 'rm -rf /data/local/tmp/g40 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. F2's exact condition is unidentified (execution-loss proven; the
   reject/mask/binning sub-cause needs the §4 canary+breakdown wall).
   Mission 2 skipped on those grounds — no behavioral hunk fired.
2. The O4m tex-hash divergence (`5a15…` vs `20dc…` ×16) is unexplained
   (content-neutral per O4-bytes-exact; 8 inputs verified, no rect;
   bank/samples/miptbp/texa provably equal — sub-field logging queued).
3. O1 seen-vs-outcomes ±1 (comp seen=18/acc=17; scene seen=209/
   acc+fuse=210): `acc` exact and triple-checked; the residual kick is
   unaccounted (all 3 append returns instrumented; single call site).
   Diagnostic only — does not affect the split.
4. O2-cord0 is receipted load, not wall-measured (no prior flush exists;
   host extraction + G29-vram + run-#1 direct measurement agree).
5. The G10 raw `scratch`/`img` values may carry staging-alloc deltas
   (normalized 0-diff; pre-registered informational, G38 §2g note d).
6. `g14-diff.py` did not run (N/A by design — FNV/bytes/scanout
   comparison closed without it; same call as G38/G39).
7. G29-E1 carried (truncated FNV basis reused for comparability); G29-E2
   FIRED (Odin binary zero-damage at report-time re-read; push-time +
   post-run shas pin the run; deterministic relink restored exact bytes).
8. Mac budget overage: 3 builds + 3 runs in ONE dir (R1 recursion defect
   + R2 O3b offset bug, both with receipts). Odin within budget (1+1).
   Same-filesystem parallel edits were found to race (one lost write,
   caught by replay-verify) — serial edits thereafter.
9. No lldb; OS tombstone store untouched. `upstream/` + harness code
   untouched; no new dumps.
10. The Adreno filing is still open and unfiled (needs user identity /
    tracker — unchanged owner; content upgrades per §4).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g40/` (30 files:
  `g40-dump.gs` 11,537,377 B `154d9d85…`, `g40-mac-stderr.txt` 2448
  lines (32 `G40: O1` + 2 O2 + 16 O2x + 2 O3 + 2 O3b + 2 O4 + 16 O4m +
  32 O5 + full G11/G10/G31/G30/G29 witnesses), `-run1`/`-run2` pairs,
  `g40-odin-logcat.txt` 2464 lines (same classes), `odin-` 0-B pair +
  10 Odin PPMs (black `99418f1b…` ×10) + 10 Mac PPMs (black×2 +
  content×8, == G38 shas)) + `parallel-gs-g40-mac-build/` (binary
  51,916,232 B `6b318b42…` Mach-O) + `parallel-gs-g40-android-build/`
  (binary 265,873,896 B `0c6c81d4…` ELF, relink-restored exact).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g39/` + all older
  build dirs + SSD clone (HEAD `3a66c19…`, wall hunk + G22/G26/G29/G30/
  G31 uncommitted; Granite `16e7395f…` + G28, uncommitted — ZERO commits
  anywhere).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g40/` (30/30 files,
  `shasum -c` ALL OK + SSD-vs-mirror EQ on key files).
- Session-only: `/tmp/g40-*.py`, `/tmp/g40-*.sh`, `/tmp/g40-*.diff`,
  `/tmp/g40-pristine/` (replay workarea).
- Commits: ssx3 `local/research/G40/` `[G40]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G40 report ends here. Statics verified the G39 end state
and pre-registered the UMA narrowing (no write-back copy on either GPU);
the ONE wall hunk (O1/O2/O3/O3b/O4/O4m/O5, env-gated, replay-verified)
needed two Mac repair cycles (recursion-consume + O3b-offset, both
receipted, outcomes never perturbed); run #3 + Odin O1 (both exit 0)
give O1=17/17 zero-reject, O4 byte-exact cross-GPU at cord0+cord1, and
O3=O3b=load on Odin vs `840cd308…` on Mac — F2 execution-loss,
decisively. Mission 2 skipped (gate met, no exact condition — the
barrier example is refuted by O3b+UMA; blind fire forbidden). G26/G28
HOLD in-run. Next: PSM1/FBMSK masked-write canary + hash-input breakdown
on Odin; filing still open (zero-damage event tabled with deterministic
relink proof; E29 lease untouched).
