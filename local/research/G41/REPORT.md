# G41 report — Masked-write canary on Odin: masking REFUTED (C4/C5 land byte-exact); only C1 (plain PSM0) lost; B-loss is pass-contextual, not draw-state

Brief: G41 — Mission 1: quarantined env-gated canary (default off) firing
5 synthetic sprites (C1..C5, 2×2 PSM×FBMSK matrix + composite-exact C5)
into scratch VRAM pages (never B) at boundary 1 (cord 1), same draw path
as the game, plus G40's (b) piggyback (8 O4m hash inputs raw + rect +
TexInfo); Mission 2: ONE fix only if the matrix names a single cell
pattern. Tables + receipts; the orchestrator decides. Time box 6 h. Read
first per the brief, all of each: `local/research/G40/REPORT.md` (F2
execution-loss, O5 state, §4 next action, §7 gaps) and `AGENTS.md`. No
upstream contact of any kind.

Machine: same as G8–G40 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir
`/data/local/tmp/g41/` ONLY; removed at end.

Headline result: **the masked-PSM1 hypothesis is refuted with bytes, and
so are its two siblings — but NOT by a clean sweep.** On Odin, C2/C3/C4/C5
land **byte-exact vs Mac** (FNV/nz/head identical), while **only C1 (plain
unmasked PSM0 flat fill) is lost** (acc=1, nchg=0 over the full arena,
persists through 3+ later submit+waits → true execution loss, not a race;
no stray writes anywhere: G31/vpage 0-diff). The C5-lands/B-lost split
proves B's loss is **not determined by draw state** (PSM/MSK/texture/
blend/test all identical) — it is **pass-contextual** (scale/target).
F2 execution-loss for B **stands and is strengthened** (C2–C5 validate the
read path: same map+wait reads see fresh bytes). The (b) piggyback is
**closed**: the O4m hash divergence is uninitialized-garbage padding in
two semantically-void inputs (texa, mb46), content-neutral (O4 exact),
recomputed hash == O4m hash on both sides. Mission 2 **skipped** (no exact
addressable construct for B; firing blind forbidden). Bonus: G40's gap-3
(seen=18/acc=17 ±1) is **explained** (queued trigger vertex + count-check
before FB-check), and the R0→R2 repair trail names a real resumed-kick
hazard (pre-flush-consumed scissor cache).

## 0. Budgets (declared) vs actuals

| class | budget | actual |
| --- | --- | --- |
| Mac builds | 1 | 4 (R0a failed-link + R0 + R1 + R2 — OVERAGE, causes below) |
| Mac runs | 1 | 3 (R0 VOID + R1 diag + R2 F0 — OVERAGE, causes below) |
| Odin builds / runs | 1 / ≤2 | 1 / 1 PASS (first-try, exit 0) |
| time box | 6 h | ~3.5 h PASS |
| new SSD build dirs | (no cap in brief; G40 de-facto ≤6 GB/dir) | 3,808,256 + 4,482,048 KiB PASS |
| new SSD `ps2x-g41/` | (no cap in brief; G40 de-facto 50 MB) | 30 files, 70,656 KiB allocated — OVER DE-FACTO (4 interface snapshots kept for R0/R1 provenance; logs were overwritten per-run, see §7.8) |
| device | `/data/local/tmp/g41/` only | staged 2, pulled 13 by explicit list, dir removed after; ZERO new tombstones (newest still _23); pre-existing `n3/` untouched PASS |
| network | none | no clones, no installs PASS |
| committed to git | text only | REPORT.md + 3 appliers + 4 scripts + scorer + wall.diff; no binaries |

Build/run overage causes (all Mac-diagnosed pre-device, G40 precedent
3+3): R0a — `write_register(addr, 0)` binds the `int` template overload
(static_assert); compile-only, fixed in applier, re-applied from backup.
R0 — C5 caught live *scene* regs (PSM0/MSK0: composite flush is triggered
by the next pass's FBPointer kick, so live FRAME at flush-end is the
scene's) + clip poison (ford=3 bb=198). R0 VOID for C5 (C1–C4 valid but
superseded). R1 — diagnostic: kick-time snapshot (C5 PSM1/MSK exact,
landed) + state dumps (named the stale word: scissor cache (63,63) at
cend, everything else live). R2 — direct scissor-cache restore → ford=3
clean (113/0/97), full 0-diff battery. Odin got R2 first-try.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Adreno drops the composite's masked PSM1 writes; the 2×2+1 matrix isolates PSM vs FBMSK vs composite-state |
| observable signal | canary table (Mac vs Odin per cell, bytes) + hash-input breakdown + named condition (or refutation) |
| alternatives | masked-PSM1-dropped (C4/C5 lost); PSM1-dropped (C3/C4/C5 lost); FBMSK≠0-dropped (C2/C4/C5 lost); all-land (refutation → binning/Turnip); OTHER (off-matrix pattern) |
| stop condition | one hunk (+repairs folded, no second hunk); env-gated default-silent; per-cell + full-VRAM save/restore (zero perturbation: G31/G30-vpage/scanouts 0-diff per side); Mission 2 only with an exact construct |
| outcome → next action | OTHER (only-C1-lost) + (b) closed; Mission 2 skipped; ONE next wall recommended (§4) |

Outcome: all three brief hypotheses refuted; C1-only loss + C5-lands
names no B-fix construct. Retry not used (O1 exit 0).

## 2. Hunk design + repair cycles (one file, `gs/gs_interface.cpp`)

### 2a. Pin verification (pre-work — G40 end state reproduced)

HEAD `3a66c19…` (== pin), diff 804+/4- (== 385 G39 + 419 G40),
Granite `16e7395f…`, G40 ×34 markers, G26/G28 present, dump `154d9d85…`,
device Odin3/15 with LEASE free and tombstone _23 newest. Applied R0
(replay-verified: applier-on-copy == worktree, `cmp` identical),
then R1/R2 (11 + 2 asserted edits). Final hunk +565/−0, one file,
env-gated `PGS_G41_CANARY=1`, uncommitted in the clone.

### 2b. Design (what the hunk does)

- **Arena**: VRAM pages 492..511 (20 pages, FBP==page for PSM0/1; never
  B; above the G31 A/B window). Textures reach page ~506, so strict
  non-overlap is impossible — instead every cell **saves and restores
  both registers and VRAM bytes** (map/verify/restore/verify), making the
  canary transparent by construction. Census (below) proves no *render
  pass* overlaps the arena; vpage 0-diff proves byte transparency.
- **Fire**: composite-flush ordinal 1 (keys off G40's cord when both
  enabled → exact coincidence, verified 16/16 cord-joins g41==g40 both
  sides). Fires once (pass 0 only).
- **Cells** (32×32 sprite at origin, single-page footprint, per-cell
  kick→SubmissionFlush→submit+wait→full-arena-diff→restore→verify):
  C1 FBP492/PSM0/MSK0, C2 FBP496/PSM0/MSKff000000, C3 FBP500/PSM1/MSK0,
  C4 FBP504/PSM1/MSKff000000, C5 FBP508 + composite-exact state.
  C1–C4: flat RGBAQ=11223344, PRIM sprite/TME0/ABE0 (+PRMODE cover for
  AC=0), TEST/FBA/PABE 0, XYOFFSET 0, SCISSOR 63, ZBP511/ZMSK1 (stray-Z
  detector). C5 (R1): **kick-time snapshot** (every FBP112 append copies
  `registers`; at fire time it holds composite#1's last kick) replayed
  wholesale via write_register with FBP→508 + fixed geometry (XYOFFSET 0,
  SCISSOR 63, Q=1, UV/ST (0,0)/(511,511) per vertex). C4/C5 use
  FBMSK=ff000000 exactly as O5.
- **Verdict logic**: per-cell full-arena memcmp vs pre-bytes (attribution
  exact: single outstanding cell) + changed-page list (cap 8, FNV/nz/
  head) + acc (render_pass.primitive_count) + kick line (actual instance
  state) + restore-verify.
- **Census** (every outer flush with prims): instance FRAME+Z+bb+coarse
  page spans + arena-overlap flags (fov/zov) + reason. 32 rows/side.
- **(b) piggyback** (cord 1, pre-canary): 8 hash inputs from
  `state_tracker.last_texture_descriptor` (== composite's: single-texture
  pass, last resolve before flush) + recomputed `Util::Hasher` (proves
  completeness) + rect + live ctx regs (normalization delta) + TexInfo[0]
  (entry snapshot) + dims.
- **State dumps (R1)**: ofx/ofy, scissor cache (lo/hi/hi_x_fb/wrap),
  dirty flags, sampling log2s, PRIM/FRAME0/SCISSOR0/XYOFFSET0/TEST0/ZBUF0/
  TEX0_0/ALPHA0/AC at every cord-join + canary edges.
- **Save/restore envelope** (around all cells): G40 statics, vertex queue
  (pos/attr/count — vq=2 at fire, the trigger pair), whole StateTracker,
  potential_feedback, parallelogram order, scissor cache words (R2);
  per-cell full touched-register round-trip via write_register; G40 busy
  held (zero extra G40 rows).

### 2c. Repair cycles (each Mac-diagnosed, receipts in §3/§8)

| cycle | defect (named cause) | receipt | fix (same hunk) |
| --- | --- | --- | --- |
| R0a | `write_register(addr, 0)` binds `int` template overload (static_assert 4==8) | build exit 1, 2 errors | `uint64_t(0)` ×5 in applier, re-applied from backup |
| R0→R1 (C5) | live regs at flush-end are the *next* pass's (FBPointer trigger overwrote FRAME): C5 ran PSM0/MSK0 scene state | C5 kick PSM=0 MSK=0 (R0 Mac log, session transcript) | kick-time FBP112 snapshot; C5 replays it (R1: snap frame=ff00000001080070, kick PSM=1 MSK=ff000000) |
| R0→R2 (poison) | resumed trigger-kick consumed SCISSOR_BIT pre-flush and reuses the cache post-flush: canary's (63,63) leaked → strip cascade bb=198 at ford=3 | ford=3 prims=7/bb=198 (R0); cend scihi=63,63 with regs+ofx+dirty live (R1 dump) | direct scissor-cache save/restore (R2: ford=3 113/0/97, full 0-diff) |

Order proof for the poison (append path): SCISSOR consume (+79) →
check_frame_buffer_state/flush (+182) → update_state (+208, post-flush).
The scissor cache is the sole pre-flush-consumed render_pass word-set;
ofx/ofy were proven clean (cend-dump) and need no direct restore.

## 3. Task 2 — ONE Mac F0 run (R2) + ONE Odin run (SAME shape)

### 3a. Knob matrix (only deltas: platform + binary)

| knob | Mac | Odin (O1) |
| --- | --- | --- |
| dump | `g41-dump.gs` (`154d9d85…` copy) | `g13-dump.gs` (`154d9d85…`) |
| `--iterations 2` / `--disable-sampler-feedback` | SET | SET |
| `PGS_G40_WALL=1` + `PGS_G41_CANARY=1` + `PGS_SKIP_COMPILATION_TASKS=1` | SET | SET |
| binary | Mach-O `a2aeba1c…` (51,934,616 B) | ELF `96de5803…` (265,914,952 B; 2 matching SHA reads + on-device post-run match) |
| driver | MoltenVK 1.4.2 (full G7 env) | Adreno 830 |

Builds exit 0 (Mac zero warnings in `gs_interface.cpp`; one pre-existing
warning class elsewhere; Odin [458/458]). Run exits 0 both, `Done!` LAST,
zero `success: no`, zero new tombstones, G26 ×1 both, G28 ×1 Odin (HOLD).

### 3b. Canary matrix (the verdict table; F0 = Mac column)

| cell | PSM | FBMSK | Mac (F0 expected) | Odin (O1) |
| --- | --- | --- | --- | --- |
| C1 | 0 | 0 | acc=1 LANDED nchg=1 chg0=492 fnv=0c1f0f28e9418a4b nz=4932 head=11223344 | acc=1 **LOST** nchg=0 |
| C2 | 0 | ff000000 | acc=1 LANDED nchg=1 chg0=496 fnv=8803470a2c858767 nz=4211 head=11223300 | acc=1 LANDED **byte-exact** (FNV/nz/head == Mac) |
| C3 | 1 | 0 | acc=1 LANDED nchg=1 chg0=500 fnv=19a7754f3f51bb87 nz=4211 head=11223300 | acc=1 LANDED **byte-exact** |
| C4 | 1 | ff000000 | acc=1 LANDED nchg=1 chg0=504 fnv=dfce146764938517 nz=4211 head=11223300 | acc=1 LANDED **byte-exact** |
| C5 | 1 (snap-exact) | ff000000 | acc=1 LANDED nchg=1 chg0=508 fnv=b8d9711bf6c8b8c3 nz=1328 head=00000000 | acc=1 LANDED **byte-exact** |

All kicks acc=1 both sides (CPU-accepted; bb=0,0,30,30; C5 snapshot
prim=0x11e (sprite/TME/ABE) frame=ff00000001080070 both sides).
restored=1 ×5 both sides. Arena pre identical both sides
(e9bec547192d3a43/36864, vq=2). Census 32/32 fov=0 zov=0 both sides
(no game pass touches the arena).
Odin-B at boundary 1 still load (O3 eea04488/149721 vs Mac 840cd308/
699122 — fault persists, as predicted for Mission 1).

C1-loss is TRUE execution loss, not a race: (i) nchg=0 over the full
20-page arena at C1's post-read (after forced submit+wait); (ii) page
492 still == pre at C2's post-read (3+ submit+waits after C1's record);
(iii) no stray writes anywhere (G31 + vpage 0-diff on Odin, §3d).
A micro-race would have landed by (ii); a misplaced write would show
in (iii).

### 3c. Hash-input breakdown (b) — CLOSED

| # | input | Mac | Odin | same? |
| --- | --- | --- | --- | --- |
| 1 | tex0.bits | 0000000268020000 | 0000000268020000 | YES |
| 2 | tex1.bits | 0000000000000000 | 0000000000000000 | YES |
| 3 | texa.bits | 0000010000000000 | 00000000f4b31300 | **NO** |
| 4 | miptbp1_3.bits | 0000000000000000 | 0000000000000000 | YES |
| 5 | miptbp4_6.bits | 0000000000000000 | **f000000000000000** | **NO** |
| 6 | clamp.bits | 00000000007fc006 | 00000000007fc006 | YES |
| 7 | palette_bank | 0 | 0 | YES |
| 8 | samples | 1 | 1 | YES |
| — | recomputed vs O4m | 20dc126f006088ea == O4m ✓ | f5a789e12b4dbcea == O4m ✓ | complete |
| — | rect / TexInfo / dims | 0,0,512×512,lv1; sizes 1024,512,…; 512×512 | IDENTICAL | YES |

Verdict: the divergence lives **entirely** in texa + mb46
(recomp==O4m both sides ⇒ no hidden 9th input; 6 identical ⇒
divergence ⊆ {texa, mb46}). Both are **unwritten on this path and
semantically void**: texa is written only in palette branches
(lines 2138/2167; composite is TPSM0 non-palette), miptbp only for
levels≥2 (rect.levels==1 here); reads are palette-gated (upload) or
mip-gated. `Reg64() : desc{}` leaves **padding indeterminate**
(MIPTBPBits tail PAD(4) reads 0xf on Odin — no writer sets padding,
so this is definitive for uninitializedness). Content-neutrality is
**empirical**: O4 texture bytes are byte-exact cross-GPU
(beb84bb6…/785187) despite different texa. Neither sampling nor
coverage — G40's `5a15…` vs `20dc…` question is answered (garbage in,
hash out). Note: Odin's O4m hash also varies run-to-run
(`5a15…` G40-run vs `f5a7…` G41-run, differing already at pre-canary
cord 0) — consistent with garbage; whether the alloy is run variance
or hunk stack-traffic is unseparated (would need a same-binary Odin
rerun; the conclusion is unaffected either way).

### 3d. No-perturbation (canary changes nothing per side)

| class | Mac R2 vs G40-Mac | Odin O1 vs G40-Odin |
| --- | --- | --- |
| G40 O-rows | 28 diff lines, ALL `label=` (+5 canary passes); 0 value diffs | 60 diff lines = 28 O5 `label=`-shifts + 32 O4m run-variance (16 pairs, §3c); 0 other value diffs |
| G11 game rows | +11 canary-attributable only (5× record prims=1, 5× FRAME_1 restore, 1× C5 tex); 0 game rows changed/removed | +11 identical canary lines (same position); 0 game rows changed/removed |
| G10 | 1 line: vsync#1 prims 130→135 (+5), passes 2→7 (+5), scratch +9280, img +C5 texture (2125824); others 0-diff | identical shape (135/7/same deltas) |
| G31 state/bytes | 0-diff | 0-diff |
| G30 vpage (512 pp.) | 0-diff (restore proven) | 0-diff |
| scanouts (10/10) | SAME | SAME (10/10 black, fault persists) |
| G26 / G28 | ×1 / n/a (MoltenVK) | ×1 / ×1 (BOTH HOLD) |

### 3e. Split analysis

| link | evidence |
| --- | --- |
| masked-PSM1-dropped REFUTED | C4 (PSM1+mask, flat) lands byte-exact on Odin |
| PSM1-dropped REFUTED | C3 (PSM1, unmasked) lands byte-exact |
| FBMSK≠0-dropped REFUTED | C2 (PSM0+mask) lands byte-exact |
| composite-state-dropped REFUTED | C5 (snapshot-exact composite regs) lands byte-exact |
| C1-only loss (OTHER) | C1 (PSM0/unmasked/flat, first cell, FBP492) acc=1 but nchg=0; true loss (§3b); only cell lost of five |
| C5-lands/B-lost split | identical draw state lands (scratch) vs lost (B pass) ⇒ B's loss is NOT draw-state-determined ⇒ pass-contextual |
| F2 for B stands, strengthened | C2–C5 prove the map+wait read path sees fresh bytes on Adreno; B's load-reads (O3/O3b/G31) are true |
| (b) closed | §3c (padding garbage, content-neutral, complete) |

No per-pass fill/clear fast path exists for trivial draws (grep:
fill_buffer only for VRAM/atomics infra) — C1 shades like the rest,
so the H1 variant-difference below is shader-define-level, if real.

## 4. Hypothesis verdict + Mission 2 decision + the ONE next action

| claim | verdict |
| --- | --- |
| Masked PSM1 writes vanish on Adreno | **REFUTED.** C4 and C5 (masked PSM1, flat and composite-exact) land byte-exact. All three brief alternatives (masked-PSM1 / PSM1 / FBMSK≠0) are refuted by bytes. The observed pattern is the inverse cell (C1-only loss) — see below. |

Mission 2 — SKIPPED (with rationale, orchestrator decides): the gate
names no actionable construct. "Only C1 lost" is a single-cell pattern
but (i) C1's own mechanism is unidentified (three surviving
sub-hypotheses: H1 trivial-fill-variant (opaque+flat+unblended+untested
shader variant), H2 first-cycle-cold (first kick→flush→submit→wait→read→
restore cycle), H3 FBP492-specific), and (ii) a C1 fix cannot serve the
brief's acceptance (Odin-B == 840cd308): C1 and B have disjoint params
and the C5-proof shows B's loss is not draw-state-determined at all.
Firing a hunk at either without a named construct = blind (tuning-loop
seed, forbidden). No behavioral hunk applied, no second Odin run spent.

The ONE next action the numbers justify: **G42 combined wall —
C1-triage + B-scale/B-target probes (one hunk, same canary shape)**.
(a) C1-triage (deconfounds FIRST): C1-exact params at first AND last
ordinals + swapped FBPs (492↔508): C1-params-last lands ⇒ H2
(first-effect — then ask what "first" means and whether B-cord1 shares
it, which would unify both losses into one mechanism); lost ⇒ H1
(params — names the variant construct for a force-shading fix +
validation run); FBP-following ⇒ H3. (b) B-scale: C5-exact state at
B-scale (17 prims, 511×447 coverage) into scratch (tests pass-scale/
binning with identical state). (c) B-target: C5-exact state at B-scale
into the B pages themselves with save/restore (tests target-context;
"never B" was this brief's rule — G42's call, restore makes it safe).
Rationale: (a) must precede any B-fix claim (two losses, unknown
relation); (b)+(c) need no new machinery. Queued behind it (not this
action): Mesa Turnip contrast (if (a)+(b)+(c) all land-normal ⇒
Adreno pass-fault ⇒ Turnip discriminates driver vs shader);
binning/coverage work-list readback (if B-scale lost); Adreno filing
(still paused per AGENTS.md).

No verdicts beyond the hypothesis. No port, no adoption, no upstream
contact. Bonus findings for the record: G40 gap-3 explained (q0 queued
unappended — sprite count-check precedes the FB-check so q0 doesn't
flush; q1 triggers the FBPointer flush with vq=2 and is counted
post-flush ⇒ seen=18/acc=17 with vq=2 — all three numbers from one
mechanism); G41-ford label drift (+1 after O2x-inner empties — benign,
cords align 16/16).

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited) |
| G14/G7/G8/G10/G11/G18/G22/G26/G29/G30/G31/G40 hunks | untouched, uncommitted in SSD clone only |
| G41 hunk (R0+R1+R2) | `g41-wall.diff` (+565/−0, 1 file) + 3 appliers (3+11+2 asserted edits; R0 replay-verified `cmp`-identical) — env-gated, uncommitted |
| NDK r30 / MoltenVK 1.4.2 | build + run use (Apache-2.0); no runtimes staged |
| logcat/stderr/scanouts | run receipts of our own binaries in SSD `ps2x-g41/` ONLY (not in git) + share-tier mirror; no PII |
| host analysis | `g41-score.py` + diff/sed census (session commands; no new dumps) |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (3a66c19, 804+/4-)
python3 local/research/G41/g41-canary-apply.py --dry $SSD/parallel-gs-g7   # DRY-OK 3
cp $CLONE/gs/gs_interface.cpp /tmp/g41-pre-interface.cpp (+ replay copy)  # backup
python3 local/research/G41/g41-canary-apply.py /tmp/g41-replay ; ... $CLONE  # APPLIED 3 x2
cmp /tmp/g41-replay/gs/gs_interface.cpp $CLONE/gs/gs_interface.cpp        # REPLAY-IDENTICAL
bash local/research/G41/g41-build-mac.sh                                  # R0a exit 1 (overload) → fix → exit 0
bash local/research/G41/g41-run-mac.sh                                    # R0 exit 0 (VOID C5 + poison, transcript)
python3 local/research/G41/g41-r1-apply.py --dry $CLONE ; ... $CLONE       # DRY-OK/APPLIED 11
bash local/research/G41/g41-build-mac.sh ; bash local/research/G41/g41-run-mac.sh  # R1 exit 0 (diag)
python3 local/research/G41/g41-r2-apply.py --dry $CLONE ; ... $CLONE       # DRY-OK/APPLIED 2
bash local/research/G41/g41-build-mac.sh ; bash local/research/G41/g41-run-mac.sh  # R2 exit 0 (F0)
python3 local/research/G41/g41-score.py $SSD/ps2x-g41/g41-mac-stderr.txt $SSD/ps2x-g41/g41-odin-logcat.txt  # matrix
bash local/research/G41/g41-build-odin.sh                                 # exit 0 [458/458] (96de5803)
cp /tmp/g41-{pre-interface,r0-interface,r1-interface}.cpp + worktree gs_interface.cpp $SSD/ps2x-g41/  # 4 snapshots
cp $SSD/ps2x-g41/* /Volumes/share/ssx3/ps2x-g41/ ; shasum -c SHA256SUMS    # 30/30 OK
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g41/` ONLY; `mg/`+`n3/`
untouched):

```text
shell 'ls /data/local/tmp/ ; cat mg/LEASE ; ls -lt /data/tombstones/ | head'  # pre-check (LEASE free, _23)
shasum -a 256 $BIN (build-time + pre-push re-read, FULL match 96de5803)  # two matching reads
shell 'rm -rf /data/local/tmp/g41 && mkdir -p /data/local/tmp/g41'
push <dump> $G41DIR/g13-dump.gs ; push <96de5803-binary> $G41DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G41DIR && date +%s; PGS_G40_WALL=1 PGS_G41_CANARY=1 PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer ... --iterations 2 --disable-sampler-feedback > g41-run-stdout.txt 2> g41-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0
logcat -d -s Granite:V > $SSD/ps2x-g41/g41-odin-logcat.txt                # 2585 lines
pull $G41DIR/<stdout+stderr+10 PPMs by explicit name> $SSD/ps2x-g41/odin-*  # all 1-file-pulled; NO glob
shell 'sha256sum parallel-gs-replayer'                               # 96de5803 FULL-match (post-run intact)
shell 'ls -lt /data/tombstones/ | head -3'                           # ZERO new tombstone
shell 'rm -rf /data/local/tmp/g41 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step
```

## 7. Gaps (what this brief could not do)

1. C1's loss mechanism is unidentified (H1 trivial-fill-variant / H2
   first-cycle-cold / H3 FBP492 — the §4 triage separates them in one
   wall). No C1 fix fired (no exact construct).
2. B's pass-contextual mechanism is unidentified (B1 scale/binning vs B2
   target-context — the §4 probes test both with no new machinery).
3. The 198-reject strip cascade after the resumed-kick misclip is the
   best-supported mechanism for R0's ford=3 (order-proven stale word +
   transient + strip/fuse workload), not a traced proof.
4. O4m run-to-run alloy on Odin (5a15 vs f5a7: hunk stack-traffic vs
   pure run variance) is unseparated (needs a same-binary Odin rerun);
   the content-neutral-garbage conclusion is independent of it.
5. TEXA-read-for-upload neutrality rests on O4 empirical exactness
   (stronger than tracing); the upload shader's AEM/TAx gating for
   non-palette formats was not traced to the shader.
6. `g14-diff.py` did not run (N/A by design — FNV/bytes/scanout
   comparison closed without it; same call as G38/G40).
7. G29-E1 carried (truncated FNV basis reused for comparability). No
   zero-damage event this turn (all post-run re-reads matched).
8. R0/R1 Mac logs + PPMs were overwritten by later runs (same
   filenames); R0/R1 numbers in this report come from the session
   transcript, R0/R1 *sources* from the SSD interface snapshots +
   versioned appliers (in git). G42 should version log names per run
   (G40 `-runN` style).
9. No lldb; OS tombstone store untouched. `upstream/` + harness code
   untouched; no new dumps. The (b) upstream hygiene note (zero the two
   unwritten desc words) is not filed anywhere (no upstream contact).
10. The Adreno filing is still paused (AGENTS.md standing rule).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g41/` (30 files: `g41-dump.gs`
  11,537,377 B `154d9d85…`, `g41-mac-stderr.txt` (R2 F0: 16 cord-joins +
  16 st-dumps + 32 census + hash trio + arena + 5×(kick+verd+chg+
  restored) + full G40/G11/G10/G31/G30 witnesses), `g41-mac-stdout.txt`
  (0 B), `g41-odin-logcat.txt` (2585 lines, same classes + timestamps),
  `odin-` 0-B pair + 10 Odin PPMs (black, == G40 shas) + 10 Mac PPMs
  (== G40 shas) + 4 interface snapshots (pre/R0/R1/R2))
  + `parallel-gs-g41-mac-build/` (binary 51,934,616 B `a2aeba1c…`
  Mach-O) + `parallel-gs-g41-android-build/` (binary 265,914,952 B
  `96de5803…` ELF).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g41/` (30/30 files,
  `shasum -c` ALL OK + SSD-vs-mirror implied by copy+verify).
- Session-only: `/tmp/g41-*.py` (none — appliers live in git),
  `/tmp/g41-pre-interface.cpp`, `/tmp/g41-replay/`, `/tmp/g41-r0-…`,
  `/tmp/g41-r1-interface.cpp` (replay workarea + backups; SSD holds
  copies of the interfaces).
- Commits: ssx3 `local/research/G41/` `[G41]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); clone holds R0+R1+R2 uncommitted (ZERO commits
  anywhere).
