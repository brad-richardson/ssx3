# G35 report — Commit-necessity wall: refined-H2 WINS (tag renders EXACTLY sans commit), H1-barrier refuted (Odin)

Brief: G35 (this turn) — executes G34 §4's ONE next action ONLY: the
commit-necessity wall (same W1 legs + same sparse nonzero-RGB tag
OR-masked into the temp pre-write, but SKIP `end_vram_write` — splits
H1-barrier, the commit itself is the fix, from refined-H2-threshold,
ANY nonzero-RGB content in B fixes sampling commit or no commit).
Tables + hypothesis + next-action recommendation, no verdicts beyond
the hypothesis. Time box 6 h (used 0.25 h — 09:05→09:20 EDT task start
→ commit; measured walls: 09:05:39 lane reads, Task 1 statics +
predictor 09:05→09:08, hunk + build 09:08→09:11:56, verify-push-run-
pull-cleanup-mirror 09:12:42→09:15:00, report 09:15→09:20). Read first
per the brief: `local/research/G34/REPORT.md` (all of it: H1 WINS —
the sparse 112-word tag renders EXACTLY, 10/10 ladders + 10/10
scanouts == pre-registered tag model; H2 refuted 0/10). No upstream
contact of any kind (standing no-upstream order — local hunks only,
filing stays local).

Machine: same as G8–G34 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g35/`
ONLY; removed at end (`mg/` only).

Headline result: **refined-H2 WINS — decisively, on pre-registered bytes.**
(1) Task 1 statics (ZERO device contact) tabled the commit-less shape
(G34's 8-step W1 with step 7 `end_vram_write` SKIPPED, all else
identical), the premise rows (writeback receipt MUST still read tagged
temp `c039a1d1c29cb293`/150057 — host-side, commit-independent; B1/B2
B-at-sample-time split with per-outcome verdict meanings tabled BEFORE
the run), reformulated H1/refined-H2 predictions (every scalar
pre-registered), the predictor reuse (unmodified `/tmp/g34-predict.py`
re-run: ALL CHECKS PASS — every scalar re-derived from the dump), and
a six-row decision matrix. (2) ONE hunk (G34's +55 excised + G35's +54
commit-less write-back inserted in the same edit), ONE build (exit 0
`[458/458]`, full identity), verify-then-push with NO gap, ONE run:
**exit 0**, 16/16 `G35: writeback` (tagged temp
`c039a1d1c29cb293`/150057 ×16) + 16/16 `G31: state` (fields == G31
×16, full lines stripped-identical) + 16/16 `G31: bytes` (B ==
tagged ×16 — outcome B1, A == G31 ×16) + 512 `G30: vpage` (112/112
tagged pages == per-page oracle, 400/400 non-B == G31) + 10 `G29:
ladder` (P1=P2=P3 == tagged-model `86ad7b887e140383`/229712 ×10, 0/10
cleared) + 1 `G29: vram`, ZERO new tombstone, 10/10 scanouts
BYTE-IDENTICAL to the host tag model (sha `d19e6beb…`, `cmp`
identical, 112 white pixels at exactly the predicted positions).
H1-barrier (output stays cleared without the commit) is refuted 0/10;
no OTHER branch fired. The ONE next action is the barrier-vs-content
wall (content WITHOUT the map_write flush+wait barrier): it splits
pure-refined-H2 (predicts tag-visible) from H1-resurrected-as-barrier
(the retained flush+wait is the necessary element, predicts cleared).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g35-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g35/` (retrieval: logcat + stdout + stderr + 10 PPMs, explicit list) | 50 MB | 13 files, 24,576 KiB allocated PASS |
| SSD `ps2x-g7..g34` + G14/G18/G20/G22/G24/G26/G28/G29/G30/G31/G32/G33/G34 build dirs (read-only) | 0 growth | all == 09:05:50 snapshot exactly (post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (commit-less write-back + retained dumps) | ONE hunk in `gs/gs_interface.cpp` (+54/−0 G35, G34 +55 excised same edit, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 + G31 hunks untouched, HUNK_MATCH re-verified pre + post + pre-push + post-run + report — 5/5); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g35-*` 124 KiB (hunk/build/run/score + stub + build log + diff extracts + share check, session-only; predictor + oracles + expected PPM reused from `/tmp/g34-*`); G35 evidence dir text-only PASS |
| `/` volume df shift (observed, tabled) | — | `/` Avail 4.0 Gi → 4.5 Gi (77%→75%) with Used static at 13 Gi — system-level (APFS/snapshot accounting), NOT lane files (measured lane footprint 124 KiB); no action, recorded for the gate |
| device | `/data/local/tmp/g35/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |
| share-tier mirror (drive distrusted) | — | `/Volumes/share/ssx3/ps2x-g35/` 13/13 files, `shasum -c` ALL OK PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Skipping `end_vram_write` on G34's tagged W1 write-back splits H1-barrier from refined-H2: H1-barrier (the commit itself is the fix) predicts output stays CLEARED (ladder == `aa2fa32572450383`/229376 ×10, scanouts byte-identical black `99418f1b…`); refined-H2-threshold (ANY nonzero-RGB content in B fixes sampling, commit or no commit) predicts output renders the tag EXACTLY (ladder == tagged-model `86ad7b887e140383`/229712 ×10, scanouts == tagged-model image sha `d19e6beb…`) |
| observable signal | design tables (§2: commit-less shape + premise rows incl. B1/B2 split + barrier anatomy + named bytes + predictor reuse + matrix + hunk spec) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G35: writeback` (tagged temp) + 16 `G31: state` + 16 `G31: bytes` (B1/B2 triage) + 512 `G30: vpage` (tagged-oracle-or-G31 second witness) + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + 10 scanouts scored (exact-vs-tag-model / exact-vs-black / white-set census) + verdict (§4) |
| alternatives | H1-BARRIER (tagged source ×16 + cleared output ×10); REFINED-H2 (tagged source ×16 + tag-visible output ×10); B2-CLEARED (stale B ×16 + cleared output — NO-VERDICT, cleared trivially expected under both); B2-TAG (stale B ×16 + tag-visible output — PARADOX, sampler saw what host reads cannot); OTHER-premise (receipt ≠ tagged — read leg corrupted, stop, no reading); OTHER-mixed (tagged source + neither-tagged-nor-cleared output — partial/torn coherency, triage by per-pixel deltas; refutes H1-barrier + refined-H2 jointly) |
| stop condition | ONE hunk max (commit-less write-back + retained dumps); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage; any validity-chain pin mismatch → table + stop |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: REFINED-H2 — all 16 write-back receipts carry the tagged
FNV, all 16 B-at-sample-time reads carry the tagged FNV (B1 — the
uncommitted stores persist in the host mapping), all 10 ladders carry
the tagged-model FNV (P1=P2=P3), all 10 scanouts are byte-identical to
the tagged model, and all 112 vpage B-pages match the per-page tagged
oracle while all 400 non-B pages match G31. H1-barrier is refuted
(0/10 cleared); B2/PARADOX/premise-break/mixed never triggered. No
tuning loop was entered: one hunk, one build, one device run. Retry
not used (exit 0); lldb not used (zero new tombstone — nothing to
triage).

## 2. Task 1 — static design (no device runs)

Zero device contact in this section: no `adb` invocation of any kind
before §3d (host tools only: git/grep/shasum/python/du/df/clang++).

### 2a. Pin verification (pre-work — G34 end state reproduced, ZERO edits)

09:05–09:08 EDT (every pin re-checked before any edit):

| item | observed |
| --- | --- |
| working tree (brief: VERIFY, re-pin if migrated) | `/Users/bradrichardson/dev/ps2xGS` EXISTS (superproject HEAD `fd781ef`, origin brad-richardson/ps2xGS) — VERIFIED, no re-pin; lane clone remains SSD `parallel-gs-g7` below |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G34 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 159 (155 − 51 + 55 + ... — G34 end state + nothing), gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 — G34 end state + nothing |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH; re-verified post-hunk + pre-push + post-run + report — 5/5) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (Granite HEAD `16e7395f…` == pin) |
| G29 ladder + G30 vpage + G31 state + G34 writeback | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 in replayer; `G31: state` ×1 + `G31: bytes` ×2 + `G34: writeback` ×3 + `G33: writeback` ×0 + `G32: inject` ×0 in interface) |
| G28 binary (re-sha) | 265,841,104 B, sha `450471e2…` FULL-prefix-match, magic `7f45 4c46` ELF — **INTACT** |
| G29 binary (re-sha) | 265,846,144 B, sha `79e6f4d2…` FULL-prefix-match, magic ELF — **INTACT** |
| G30 binary (re-sha) | 265,847,904 B, sha `a1963e66…` FULL-prefix-match, magic ELF — **INTACT** |
| G31 binary (re-sha) | 265,851,416 B, sha `c91719a0…` FULL-prefix-match, magic ELF — **INTACT** |
| G32 binary (re-sha) | 265,852,240 B, sha `35288fd0…` FULL-prefix-match, magic ELF — **INTACT** |
| G33 binary (re-sha PASS1 + PASS2 + report) | 265,853,048 B, mtime STILL frozen at build (07:30:55), sha `7e0ea8031c6a581f…` stable ×3, magic `7f45 4c46` ELF — **MORPHED BACK to BUILD sha** (was `46028004…` fully-zeroed at G34 time): the 12th read-artifact recurrence CLOSED on record (frozen-mtime morph, §2a2 of the brief's gate — corroborated, not re-litigated) |
| G34 binary (re-sha PASS1 + PASS2 + report) | 265,853,192 B, mtime 08:08:31, sha `2b101ddec1cb2783…` stable ×3, magic ELF — **INTACT** (== pin; committed full sha `2b101dde…2586` is the authority, prefix re-verified) |
| rich dump (host, ×4 reads this session) | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match (PASS1 full + PASS2 + pre-push ×2 + predictor-load + on-device + report) |
| dirs 0-growth | pre-run `du -sk` snapshot 09:05:50 (ps2x-g10 43008 … g34 25600; g35 absent; 13 build dirs 4480000/4482048 KiB; `/` 77%, SSD 93%); post-run re-verified §0 (every old value identical) |
| recipe | NDK r30 (`/opt/homebrew/share/android-ndk`, toolchain file present); cmake + ninja + clang++ + python3 + adb all on PATH (`llvm-readelf` via NDK toolchain path) |
| session survivors | ALL `/tmp/g33-*` + `/tmp/g34-*` session files PRESENT (same boot — see §2a2: the brief's restart note did not materialize; committed REPORT scalars kept as authority, `/tmp` oracles used as cross-check only) |
| share tier | `/Volumes/share/ssx3/ps2x-g34/` present (13 files); mirror target `ps2x-g35/` confirmed writable |

Lane-critical SSD bytes (G33/G34 binaries, dump) corroborated by 2+
matching reads separated in time (PASS1 09:05:39 → PASS2 09:06:07 →
pre-push 09:12:42 → on-device → report 09:14:16); single-read SSD
evidence was never relied upon.

### 2a2. Session-files vs the brief's gate note (tabled — proceeded, rationale on record)

The brief gates "`/tmp` session files did NOT survive the restart;
the committed REPORT scalars are the authority". Pre-work reads show
ALL `/tmp/g33-*` and `/tmp/g34-*` files present with G34-session
mtimes (same boot — no restart occurred between the gate and this
run). This was TABLED and the brief was PROCEEDED WITH, for three
on-record reasons: (1) the authority rule is honored regardless —
every §2d prediction cites COMMITTED report scalars (G33/G34 REPORT.md),
and the surviving `/tmp` oracles are used as CROSS-CHECK only
(§2e: the unmodified predictor re-derives every scalar from the dump);
(2) the alternative (deleting surviving oracles to simulate the
restart) would destroy corroboration for no validity gain; (3) nothing
in the validity chain depends on `/tmp` absence (the chain is
dump + new-binary shas at every gate, §3d). The discrepancy is
observational only: gate note was a (wrong) staleness prediction, not
a stop-rule trip — no pin mismatched.

### 2b. Commit-less shape (tabled — exactly one picked)

| shape | verdict |
| --- | --- |
| A. G34's W1 with ONLY `end_vram_write` skipped (CHOSEN) | **CHOSEN** — the single-call delta: steps 1–6 + 8 call-identical (same base/n/rect/site/temp/mask/receipt), step 7 dropped. Minimal treatment (one deleted call), maximal comparability (the ONLY delta vs G34's run is the hunk-for-hunk swap, and within the hunk the only delta is the skipped commit). The receipt stays INSIDE the write-map guard, so receipt ⟹ bytes were CPU-copied into the mapping (premise P1 keeps its force) |
| B. skip `map_vram_write` too (temp-only: mask + receipt, no write leg) | REJECTED — drops the CPU stores entirely: B-at-sample-time would be trivially stale (B2 forced), so cleared output could not discriminate H1-barrier from lost-writes; the wall would test nothing |
| C. skip the whole write leg + receipt (read + mask only) | REJECTED — same as B plus no write-time receipt: loses premise P1, strictly weaker |
| D. raw `begin_host_vram_access` placement (no map_write, no commit) | REJECTED for THIS wall (it is the §4 next action, not this action): it drops the map_write flush+wait barrier together with the commit, so tag-visible output could not separate content-sufficiency from barrier-necessity — a different (later) split |

Sequencing vs G34's W1 (exact — which call is skipped, what stays):

| step | G34 (W1 + tag) | G35 (commit-less) |
| --- | --- | --- |
| 1 | `map_vram_read(B)` | same call, same base/n |
| 2 | CPU copy B→temp | same |
| 3 | OR-mask `temp[p*2048] \|= 0x00FFFFFF` (p in 0..111) | same |
| 4 | temp FNV/nz (**tagged** — `c039a1d1c29cb293`/150057) | same |
| 5 | `map_vram_write(B)` (flush_submit + wait_timeline + begin_host_access) | same call, same base/n |
| 6 | CPU copy temp→B (mapped dst) | same |
| 7 | `end_vram_write(B)` = `end_host_write_vram_access` + `commit_host_write` | **SKIPPED — no commit of any kind** |
| 8 | `G34: writeback` receipt (tagged FNV) | `G35: writeback` receipt (tagged FNV, same guard) |

Barrier anatomy (read from the clone sources pre-run — what the
treatment keeps vs drops): `map_vram_write` (kept) performs
`get_host_write_timeline` → maybe `flush_submit(HostAccess)` →
`wait_timeline` → `begin_host_vram_access`; the skipped
`end_vram_write` would have performed `end_host_write_vram_access` +
`tracker.commit_host_write(page_rect)`. Reads (`map_vram_read`, kept —
G35 read leg + G31 + G30) have NO matching end call anywhere in the
lane (G29–G34 never close reads), so an unbalanced begin/end pairing
is not a new hazard class for the mapping itself; the treatment's
force is exactly: tracker never commits the write + whatever
`end_host_write_vram_access` finalizes never runs. Crash risk
(O1/O3) from the unbalanced write is the priced retry trigger (§3j),
not a design flaw — the brief permits ONE retry iff O1/O3 fires
instead of first draw.

### 2c. Premise rows (P1 MUST-hold + P2 B1/B2 split + P3 controls)

P1 — writeback receipt (host-side, commit-independent — MUST hold):
the receipt checksums the static temp AFTER the B→temp copy + OR-mask,
entirely on CPU. Predicted 16/16 `base=917504 n=917504
fnv=c039a1d1c29cb293 nz=150057`, 0 map-fails. The mask makes the
receipt robust to what the read leg saw: stale→tagged AND
tagged→tagged both land on the tagged model (OR is idempotent), so
receipt==tagged ⟺ read leg saw stale-or-tagged with intact alphas.
Receipt≠tagged (any) ⟹ the read leg returned something NEITHER stale
NOR tagged (corruption/torn/unbalanced-access artifact) ⟹
OTHER-premise: STOP, no H1/refined-H2 reading (the treatment broke the
read path itself).

P2 — B-at-sample-time (the split question — BOTH outcomes tabled with
verdict meanings BEFORE the run): the G35 block CPU-stores tagged
bytes into the host-visible mapping but never commits; G31-B (post-
`renderer.vsync` `map_vram_read`) + G30 vpage (post-loop
`map_vram_read`, last pass, pre-restart) witness what the read leg
sees:

| outcome | bytes | mechanism reading | verdict meaning (pre-registered) |
| --- | --- | --- | --- |
| B1: read leg sees TAGGED B | G31-B == `c039a1d1…`/150057 head `ffffff00…` ×16; vpage 112/112 == tagged oracle + 400/400 == G31 | uncommitted CPU stores persist in the host mapping through vsync; sampler and host reads COULD see the same bytes | output cleared ⟹ **H1-BARRIER** (sampler needed the commit; host bytes tagged but sampler emitted cleared — coherency gap at the sample level); output tag-visible ⟹ **REFINED-H2** (content sufficed, commit unnecessary) |
| B2: read leg sees STALE B | G31-B == `eea04488c453e75b`/149721 ×16; vpage 512/512 == G31 | something discards uncommitted stores (re-sync from device side, staging overwrite, access imbalance) — bytes never persisted anywhere readable | output cleared ⟹ **NO-VERDICT** (cleared trivially expected under BOTH hypotheses — sampler saw stale for a trivial reason; the treatment failed to place bytes); output tag-visible ⟹ **PARADOX** (sampler saw a tag host reads cannot see — device-side copy updated but staging reverted? — full triage, new theory) |

Mixed-B (some vsyncs tagged, some stale, or B-neither) ⟹ OTHER
(persistence flapping / torn writes — triage by seq pattern; no
H1/refined-H2 reading).

P3 — controls (same both hypothesis columns): 16 `G31: state` all
fields == G31 (§2d table; full lines stripped-identical); 16 A-lines
== G31's 16 A-fields (scene path untouched — non-perturbation); 1
`G29: vram` == load `6002946899e9cae0`/1184729 (restart control —
fires post-loop post-restart on reloaded bytes, commit-independent);
logcat 2376 lines (G31's 2360 + 16 G35) with the §3e shape; 0
map-fails of any kind. Any P3 break ⟹ triage per §2f (A≠G31 ⟹
non-perturbation violated; vram≠load ⟹ load path perturbed).

### 2d. Reformulated predictions (every scalar pre-registered)

Authorities: tagged TB `c039a1d1c29cb293`/150057 head `ffffff00…`
(G34 §2d/§3g); stale B `eea04488c453e75b`/149721 (G31, via G34 §2d);
cleared render `aa2fa32572450383`/229376 + black PPM
`99418f1b1a94ed9ffcfadd6fc0b6573eca5275d6834a3d4cffb64da330233b34`
(G33 REPORT full sha + G34 §2d); tagged render
`86ad7b887e140383`/229712 + tag PPM
`d19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f`
112 whites bbox x[0,448] y[0,416] first row x=0,64,…,448 @ y=0 (G34
§2d/§3i); load `6002946899e9cae0`/1184729 (G30, via G34 §2d).

| observable | H1-barrier (commit is the fix) | refined-H2 (content suffices) |
| --- | --- | --- |
| 16 `G35: writeback` temp FNV | `c039a1d1c29cb293` nz=150057, base/n=917504/917504 (premise P1 — same both columns) | same |
| 16 `G31: bytes` B | tagged `c039a1d1c29cb293` nz=150057 head=`ffffff00…` (B1 assumed; B2 ⟹ §2c re-route) | same |
| 16 `G31: state` | all fields == G31 predictions; full lines stripped-identical to G31's 16 | same |
| 512 `G30: vpage` | 112/112 B pages == per-page tagged oracle; other 400/400 == G31's vpage (B1 assumed) | same |
| 16 A-lines | == G31's 16 A-lines (scene path untouched) | same |
| 1 `G29: vram` | `6002946899e9cae0`/1184729 (restart control) | same |
| 10 `G29: ladder` P1/P2/P3 | == cleared `aa2fa32572450383` nz=229376 ×10 | == tagged-model `86ad7b887e140383` nz=229712 ×10 |
| 10 scanouts | BYTE-IDENTICAL black (sha `99418f1b…`, 688,143 B) | BYTE-IDENTICAL to `/tmp/g34-expected.ppm` (sha `d19e6beb…`, 688,143 B; exactly 112 white pixels at the predicted positions) |
| logcat | 2376 lines (G31's 2360 + 16 G35); `Total time per VBlank` inflated class | same shape |

### 2e. Predictor reuse (the REAL predictor, unmodified)

No host restart this session (§2a2): `/tmp/g34-predict.py` (the exact
artifact behind G34 §2d) ran unmodified against the pinned dump:

| check | observed |
| --- | --- |
| load full-VRAM | `6002946899e9cae0`/1184729 (== pin) |
| stale B | `eea04488c453e75b`/149721 head `0000000000000000` (== pin) |
| G32-pattern self-check | B `dfe2b6516a519f83`/915264 + model P1 `9dd120bc6b0df383`/915264 (== committed G32 scalars) |
| VOID reproduction | H1-FNV == cleared (`aa2fa32572450383`)? True; PPM sha `99418f1b1a94ed9f…`; 0/229376 nonzero-RGB words; swizzle bijective 229376/229376; stale-model PPM `cmp`-identical to G29 blacks |
| tagged oracle | TB `c039a1d1c29cb293`/150057 head `ffffff00…`; 112/229376 nonzero-RGB words; render `86ad7b887e140383`/229712; PPM `d19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f` (full-match G34 §3i); 112 whites + 112 nonblack; bbox x[0,448] y[0,416]; first row x=0,64,…,448 @ y=0 |
| verdict | ALL PREDICTOR CHECKS PASS — every §2d scalar re-derived from the dump (dump sha `154d9d85…` re-confirmed on load) |

Oracle reuse: `/tmp/g34-vpage.txt` (112 per-page tagged FNVs, each nz
exactly stale+3) + `/tmp/g34-whites.txt` (112 predicted positions) +
`/tmp/g34-expected.ppm` (re-emitted bit-identical by the re-run, sha
`d19e6beb…`) serve the G35 scorer unchanged — the tag is identical,
so no new oracle was derived (derivation would be a second shape).

### 2f. Decision matrix (pre-registered)

| G35 temp (16) + B (16) | ladder P1 (10) + scanouts | reading |
| --- | --- | --- |
| temp == tagged ×16, B == tagged ×16 (B1) | == cleared `aa2fa325…` ×10, scanouts black-exact (`99418f1b…`) | **H1-BARRIER** — the commit itself is the fix |
| temp == tagged ×16, B == tagged ×16 (B1) | == tagged-model `86ad7b887e…` ×10, scanouts tag-exact (`d19e6beb…`, 112 whites in-set) | **REFINED-H2** — content suffices, commit unnecessary |
| temp == tagged ×16, B == stale ×16 (B2) | == cleared ×10, black-exact | **NO-VERDICT** — uncommitted stores lost; cleared trivially expected under both (treatment failed to place bytes) |
| temp == tagged ×16, B == stale ×16 (B2) | == tagged-model ×10, tag-exact | **PARADOX** — sampler saw what host reads cannot; full triage, new theory required |
| temp ≠ tagged (any) OR B-neither/mixed (any) | — | OTHER-premise — read path broken (temp) or torn persistence (B) → STOP, no H1/refined-H2 reading |
| temp == tagged ×16, B == tagged ×16 (B1) | neither tag-exact nor cleared (any pattern, incl. partial-tag k<112 whites or uniform single-word degenerate) | **OTHER-mixed / BOTH-REFUTED** — H1-barrier + refined-H2 jointly refuted; per-pixel deltas (white-set membership + extras) name it |

### 2g. Hunk spec (the ONE hunk, named)

ONE hunk: **G35 pre-`renderer.vsync` commit-less tagged write-back**
(map-read B → static temp + sparse OR-mask pre-write → map-write
tagged temp back with NO `end_vram_write` + `G35: writeback`
TAGGED-temp receipt), with **G34's write-back block excised in the
same edit** (its diff survives committed in G34 evidence — excision is
lossless and REQUIRED: live committed content would confound the
wall).

| item | spec → actual |
| --- | --- |
| site | `GSInterface::vsync`, immediately BEFORE `auto result = renderer.vsync(…)` — the same anchor G32/G33/G34 used (anchor `"\tauto result = renderer.vsync(priv_registers, info,\n"`, unique ×1) → CONFIRMED ×1 |
| shape | ONE contiguous insertion (`{…}` block at 1-tab scope); G34's +55 block excised first (derived from the committed `g34-writeback-tagged.diff` `+` lines — no transcription); net vs G34 worktree: commit-less write-back only → +54/−0 contiguous, single @@ (`@@ -4684,2 +4723,56 @@`); worktree `gs_interface.cpp` diff 158 = 159 − 55 + 54 (arithmetic closes) |
| temp + tag | `static uint32_t g35_temp[(112*8192)/4]` (function-static, 917504 B BSS; fully rewritten each call before use; vsync is serial — no reentrancy) + `for (p in 0..111) temp[p*2048] \|= 0x00ffffffu` → as spec'd |
| skipped call | `end_vram_write(g35_base, g35_n)` ABSENT (asserted: `end_vram_write(` nowhere in the block but the SKIPS comment); receipt stays inside the write-map guard → as spec'd |
| receipt | `G35: writeback base=%u n=%u fnv=%016llx nz=%u.` (TAGGED-temp FNV/nz, truncated basis G29-E1) + `read-map failed` / `write-map failed` fallbacks (3 `G35: writeback` markers total) → as spec'd |
| applier | `/tmp/g35-hunk.py` (mirrors `/tmp/g34-hunk.py`): asserts G34-block ×1 + immediately-pre-anchor + G35-absent + anchor ×1 + `end_vram_write(`-absent; single file write; post-asserts G34-gone + G35 ×3 + G33-absent + G31 neighbors intact (`G31: state` ×1, `G31: bytes` ×2) → DRY-OK then APPLIED; post: G34 ×0, G35 ×3, G33 ×0, G31 ×1/×2, G22 HUNK_MATCH |
| syntax | hunk text extracted from the applier compiles clean in a stub TU (`clang++ -std=c++17 -Wall -Wextra -fsyntax-only` — STUB_SYNTAX_OK; 2 unused-set warnings are stub artifacts of no-op LOGI) → as spec'd |
| costs (tabled up front) | +16 logcat lines (~2 KB); runs inside the timed region (expect inflated ms/VBlank — diagnostic cost, not a signal); 16 extra HostAccess read+write (sans commit) cycles + 2×917504 B CPU copies + 112 ORs/vsync → 2376 lines; 12.049 ms/VBlank (§3e) |
| retained | G22 + G26 + G28 + G29 ladder + G30 vpage + G31 state/bytes all untouched (HUNK_MATCH + marker counts re-verified post-hunk) → all intact |

### 2h. Knob matrix (flag SET — the ONLY delta vs G34's run is G35's hunk-for-hunk swap)

| knob / flag | G34 setting | G35 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G34 = G31 + TAGGED write-back hunk | G35 = G31 + COMMIT-LESS tagged write-back hunk (G34 block excised) | the single delta (commit skipped, legs+content same) |

## 3. Task 2 — ONE commit-necessity wall + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G34's run is the G35 hunk-for-hunk swap)

Same table as §2h (SET / UNSET / KEPT / ABSENT / hunk-for-hunk swap —
the single delta).

### 3b. Hunk record (ONE hunk, commit-less write-back + retained dumps)

`gs/gs_interface.cpp`, G34's +55 block excised + ONE contiguous +54/−0
insertion (new lines ~4723–4776) in `GSInterface::vsync()`
immediately BEFORE the `renderer.vsync` call: `map_vram_read(917504,
917504)` → CPU copy into `static uint32_t g35_temp[]` → OR-mask
`temp[p*2048] \|= 0x00ffffffu` (p in 0..111) → truncated-basis
FNV/nz over the TAGGED temp → `map_vram_write(917504, 917504)` → CPU
copy tagged temp back → NO `end_vram_write` (the wall) + `G35:
writeback` receipt (`read-map failed` / `write-map failed`
fallbacks). Regs/loop/circuit untouched. Full diff text in
`g35-writeback-nocommit.diff` beside this report (mechanically
extracted with `-U1`: 54+/0-, single @@ block, `cmp`-identical to the
worktree extraction). G22 HUNK_MATCH + G26 block + G28 Granite hunk +
G29 ladder + G30 vpage + G31 state all untouched; zero commits in
submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G34 recipe, `g35-build.sh` mirrored): exit 0
(`Configuring done (6.6s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`,
binary mtime 09:11).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp` + cmake-deprecation noise); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,853,184 B (−8 vs G34 — the dropped commit-call delta; NEW size expected) |
| sha (build-time) | `f3a33f7c51c76c4979ed1cd0f977bd74491be314e9d020d6afd44876c69a41c0` (NEW) |
| build-id | `132df20bb2c1321cfb9f5e48e0a313b4a03d164b` (distinct from G34 `c696a76a…`) |
| plumbing presence | `G35: writeback` ×3, `G34: writeback` ×0, `G33: writeback` ×0, `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule + paranoia triple-gate)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (×2 reads) | 09:12:42 | `f3a33f7c…` (binary) + `154d9d85…` (dump) FULL-match build sha; G22 HUNK_MATCH; all dirs == baseline (new g35 build dir the only growth) |
| device stage | 09:12:51 | pre-check (Odin3, Android 15, `mg/` only, newest tombstone _23, 29 G free) then `rm -rf` + `mkdir` + push dump (0.013 s) + push binary (2.175 s) into `/data/local/tmp/g35/` ONLY |
| on-device sha match | 09:12:51 | `154d9d85…` + `f3a33f7c…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 09:12:58 | `logcat -c` then run — no idle window |
| on-device post-run re-sha | 09:13:04 | `f3a33f7c…` FULL-match — intact |
| report-time re-sha | 09:14:16 | `f3a33f7c…` FULL-match + ELF magic — **binary INTACT, no zero-damage recurrence this window** (5th matching read: build + pre-push ×2 + post-run + report) |
| G33/G34-binary track (report gate) | 09:14:16 | `7e0ea803…` (BUILD sha, stable — 12th recurrence stays closed) + `2b101dde…` (INTACT) — corroboration only, never in the push chain |

No validity-chain pin mismatched at any gate: the stop rule never
fired (and G34's §2a2 ratification was never needed — the G35 chain
is clean end to end).

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g35/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g35/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g35-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790082779→1790082780; logcat 09:12:59→09:13:00) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G34) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G35: writeback` + 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 map-fails of any kind |
| logcat | 2376 lines (== G31's 2360 + 16 G35 exactly): init + 18 `Running frame` + 18 G10 + `Total time per VBlank: 12.049 ms` (same inflated class as G31's 9.194 / G32's 8.871 / G33's 12.064 / G34's 12.139 — diagnostic cost of 16 extra map+copy sans commit inside the timed region, §2g) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical in G29–G34 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 (the unbalanced-write crash risk priced in §2b never materialized) |
| device outputs | 10 scanouts (688,143 B each) ALL pulled by explicit list (§3i); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (writeback + ladder + vpage + load line — continuity with G29–G34)

| receipt | observed |
| --- | --- |
| 16 `G35: writeback` | ALL `base=917504 n=917504 fnv=c039a1d1c29cb293 nz=150057`, 0 map-fails — premise P1 HOLDS: the bytes placed were tagged-stale at write time, on every vsync, both passes, commit or no commit |
| 10 `G29: ladder` | ALL P1=P2=P3=FNV `86ad7b887e140383`, nz=229712 == tagged-model (§2d) — 10/10 tag-visible, 0/10 cleared |
| 512 `G30: vpage` (all pass=1, pages 0..511) | 112/112 B pages == per-page tagged oracle (each nz exactly stale+3, head `ffffff00…` — the uncommitted stores persisted in the host mapping through the loop); other 400/400 timestamp-stripped lines BYTE-IDENTICAL to G31's vpage (the write leg perturbed NOTHING outside the 112 tag words); ALL-pages==G31 400/512 (exactly the 112 B pages differ — as constructed) |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz=1,184,729 == host load FNV — trailing-restart mechanism reproduced on-device a seventh time (restart control passes; the unbalanced write did not perturb the reload path) |
| 16 A-lines | A-fields BYTE-IDENTICAL to G31's 16 A-fields (scene path untouched — non-perturbation proven beyond determinism; §3g) |

### 3g. Writeback + state + bytes verdicts (B1: tagged source at every write and sample time)

Writeback lines (16/16 full receipts, 0 fallbacks):

| field | predicted | observed |
| --- | --- | --- |
| base / n | 917504 / 917504 ×16 | **16/16 EXACT** |
| tagged-temp FNV / nz | `c039a1d1c29cb293` / 150057 ×16 | **16/16 EXACT** — placed bytes were tagged at write time |

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
| B (the P2 discriminator) | tagged `c039a1d1c29cb293` nz=150057 head=`ffffff00…` ×16 (B1) | **16/16 EXACT match — outcome B1**: the read leg sees tagged B at EVERY sample time without any commit (B2: 0/16; B-neither: 0/16) |
| A (live control) | == G31's A (untouched), pass-repeat 8/8 | 16/16 A-fields BYTE-IDENTICAL to G31's; 8/8 EXACT pass-repeat |

### 3h. Split analysis (refined-H2 — the tag renders EXACTLY sans commit; H1-barrier refuted)

| link | evidence |
| --- | --- |
| write leg placed the tag (sans commit) | 16/16 temp == tagged at write time (P1) + 16/16 B == tagged at sample time (B1) + 112/112 vpage == per-page oracle — the read leg reads stale-or-tagged, the OR plants the tag, the write leg carries it into the host mapping WITHOUT any commit (content-exact, as constructed) |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0`) → `sample_quad[0]` + `buffers.gpu` on every vsync — same path as G31/G32/G33/G34 |
| source bytes at sample time | region B == tagged-stale (16/16 `c039a1d1…`, 112/229376 nonzero-RGB words) — never stale-as-content, never transient-written, never torn |
| circuit output | 10/10 ladder P1/P2/P3 == tagged-model `86ad7b887e140383`/nz=229712; 10/10 scanouts byte-identical to the tagged model (sha `d19e6beb…`, `cmp` identical, 112 whites in-set, §3i) — equals the refined-H2 prediction EXACTLY |
| elimination | OTHER-premise never triggered (P1 holds — read path intact); B2/PARADOX never triggered (B1 unanimous — stores persist); OTHER-mixed never triggered (no neither-nor output); H1-BARRIER refuted 0/10 (no cleared ladder, no black scanout — removing the ONLY delta, the commit, moved NOTHING off the tag model) |
| verdict | **refined-H2-threshold: ANY nonzero-RGB content in B fixes sampling, commit or no commit.** Same W1 legs + same sparse tag as G34, minus `end_vram_write`, renders the tag EXACTLY. The G34→G35 delta (the commit: `end_host_write_vram_access` + `commit_host_write`) is therefore NOT the fix — H1-barrier is refuted. What remains standing inside the treatment is the map_write leg's flush+wait barrier (§2b anatomy) plus the CPU stores themselves; separating those two is the §4 wall, not this verdict. |

### 3i. Scanouts (10/10 pulled by explicit list — G31-E1 applied) + share mirror

Explicit pull list (12 files + logcat; each named, zero globs):
`g35-run-stdout.txt`, `g35-run-stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0.ppm` … `g10-vsync7.ppm`,
`g13-dump.gs.g8-first.ppm`, `g13-dump.gs.g8-last.ppm` (all 688,143 B).
All 12 pulls individually confirmed (`1 file pulled, 0 skipped`).
Cleanup ran as its OWN verified step AFTER pull verification
(`rm -rf` + `ls` → `mg/` only, exit 0).

| file | sha256 | vs refined-H2 tag model |
| --- | --- | --- |
| 10/10 scanouts | `d19e6beb3ffee3acb31e7ca7efd817012a493433328d1549e27ff2aa7d74892f` (unanimous) | BYTE-IDENTICAL to `/tmp/g34-expected.ppm` (`cmp` 10/10 — 11-way unanimity incl. the host model) |

Pixel census (per file): exactly 112 white + 229264 black pixels;
112/112 whites at the predicted positions (expected-PPM identity
proves set membership); nonblack pixels 112/229376 (no extras, no
smear — the tag lands crisply, no torn coherency).

Share-tier mirror (drive distrusted): all 13 `ps2x-g35/` files copied
by explicit name to `/Volumes/share/ssx3/ps2x-g35/`; `shasum -c`
13/13 OK against the SSD shas.

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 16 G35 + 32 G31 lines + all controls + `Done!` (the §2b unbalanced-write crash risk never materialized) |
| second shape | NOT USED | out of budget by the stop rule (the barrier-vs-content refinement is a new discriminator, §4, not a second shape here) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Skipping `end_vram_write` on G34's tagged W1 write-back splits H1-barrier from refined-H2 | **REFINED-H2 — decisively.** Tagged source proven at every write time (16/16 `c039a1d1…`/150057) and every sample time (16/16 B == tagged, head `ffffff00…` — B1 unanimous), the uncommitted stores persisted on all 112 pages (112/112 vpage == per-page oracle, 400/400 non-B == G31), and the circuit rendered the tag EXACTLY (10/10 ladders P1=P2=P3 == `86ad7b887e140383`/229712, 10/10 scanouts byte-identical to the host tag model sha `d19e6beb…`, 112 whites in-set). H1-BARRIER is refuted 0/10. B2/PARADOX/premise-break/mixed never triggered. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **the barrier-vs-content
wall (content WITHOUT the map_write flush+wait barrier) — NOT
adoption.** Rationale: G35 refutes H1-barrier (the commit is not the
fix), but the treatment RETAINS `map_vram_write`'s flush+wait barrier
(§2b anatomy) — so a narrowed H1-as-barrier ("the retained flush+wait
is the necessary element") survives G35 untested vs pure-refined-H2
("the CPU stores alone suffice"). The discriminator: place the SAME
sparse tag via raw `begin_host_vram_access` + CPU copy with NEITHER
`map_vram_write` NOR `end_vram_write` (no flush, no wait, no commit);
the writeback receipt still checksums the tagged temp and G31-B still
verifies the placed source. Pure-refined-H2 predicts tag-visible;
H1-as-barrier predicts cleared. Queued behind it (not this action):
G26+G28 adoption — the brightness condition stays MET (output ==
content-render on every run to date: stale→cleared G31/G33,
pattern→pattern G32, tag→tag G34/G35 — commit-independent) but
adoption stays queued per the standing rule until the orchestrator
gates it; the Adreno filing — STILL OPEN regardless (content upgrades
again: "a 112-word sparse tag renders EXACTLY with no host commit of
any kind — neither the commit nor, pending the §4 wall, any barrier is
yet shown necessary; ordering/coherency fault models keep losing
cells"); G18-hunk fix adoption (still queued); O1 writer naming
(still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk + pre-push + post-run + report) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G33 write-back hunk | stays EXCISED from the worktree (diff text survives committed in `local/research/G33/` — lossless) |
| G34 tagged write-back hunk | EXCISED from the worktree by this brief's edit (diff text survives committed in `local/research/G34/` — lossless) |
| G35 additions | the ONE commit-less write-back hunk (SSD clone worktree only) + session files: `g35-build.sh` + `g35-run.sh` + `g35-writeback-nocommit.diff` (G35-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g35/` ONLY (not in git) + verified share-tier mirror `/Volumes/share/ssx3/ps2x-g35/` (13/13 `shasum -c` OK); no PII (`uid: shell`); all 10 PPMs pulled (shas + census in §3i) |
| host analysis | `/tmp/g35-*.py` (hunk/score) + `/tmp/g35-*.sh` (build/run) + `/tmp/g35-build.log` + `/tmp/g35-stub.cpp` + `/tmp/g35-*.diff` extracts + `/tmp/g35-*.txt` (g22check/share-check/block-check) + REUSED `/tmp/g34-predict.py` (unmodified re-run) + `/tmp/g34-expected.ppm` + `/tmp/g34-vpage*.txt` + `/tmp/g34-whites.txt` (session-only) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a (G34 end state)
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH (pre+post+pre-push+post-run+report)
shasum -a 256 <g28..g35 binaries> + xxd magic (x3 for g33/g34: PASS1+PASS2+report)  # §2a (g28-g32 INTACT, g33 BUILD-sha morph-back, g34 INTACT)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match (x4+ this session)
du -sk <ps2x-g10..g35 + 14 build dirs> ; df -h / $SSD           # §0 (pre 09:05:50 + post 09:14:27)
python3 /tmp/g34-predict.py                                       # §2e (REAL G34 predictor, unmodified: ALL CHECKS PASS)
python3 /tmp/g35-hunk.py --dry                              # §2g (DRY-OK: G34x1 pre-anchor, anchorx1, commit-absent)
clang++ -std=c++17 -Wall -Wextra -fsyntax-only /tmp/g35-stub.cpp  # §2g STUB_SYNTAX_OK
python3 /tmp/g35-hunk.py                                    # §3b (ONE single-write edit: -55/+54, commit skipped)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff -U1 | grep '^@@'  # hunk shape (158; single @@ ours)
cmake -S <clone> -B $SSD/parallel-gs-g35-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g35-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g35-binary> (build, pre-push x2, post-run, report)  # f3a33f7c… x5 match (intact)
llvm-readelf --notes <g35-binary> ; strings grep 3/0/0/1/2/1/1/1/2/1/1/2/0 ; xxd -l 4  # 132df20b… + ELF
python3 /tmp/g35-score.py                                       # §3f–3i (16/16 + B1-16/16 + 10/10 + 112/112 + 400/400 + TAG x10 + REFINED-H2)
cmp /tmp/g34-expected.ppm $SSD/ps2x-g35/<each of 10 PPMs>        # §3i (refined-H2 == model x10, byte-identical)
cp <13 ps2x-g35 files by name> /Volumes/share/ssx3/ps2x-g35/ ; shasum -c  # §3i (mirror 13/13 OK)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g35/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 29G)
shell 'rm -rf /data/local/tmp/g35 && mkdir -p /data/local/tmp/g35'
push <dump> $G35DIR/g13-dump.gs ; push <g35-binary> $G35DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G35DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G35DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g35-run-stdout.txt 2> g35-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (refined-H2 fired)
logcat -d -s Granite:V > $SSD/ps2x-g35/g35-logcat.txt                # 2376 lines
pull $G35DIR/g35-run-stderr.txt $SSD/ps2x-g35/ (0 B) ; pull stdout (0 B)
pull $G35DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g35/   # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G35DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # f3a33f7c… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g35 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The H1-as-barrier refinement ("the retained map_write flush+wait
   is the necessary element") survives G35 untested — the treatment
   keeps that barrier. Queued as the §4 next action (barrier-vs-content
   wall: raw-access tag placement, no map_write, no commit;
   pure-refined-H2 predicts tag-visible). Within-refined-H2 questions
   (minimum content threshold — 1 word? nonzero-alpha-only?) are
   likewise open and answered by later walls, not this one.
2. The H1-barrier-vs-refined-H2 split AS REGISTERED is CLOSED
   (refined-H2 wins, H1-barrier refuted) — not a gap; recorded so no
   future brief re-litigates it.
3. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the host swizzle model is this brief's oracle and
   matched byte-exactly, 11-way sha unanimity with the model PPM).
4. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
5. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G35 binary intact at all five).
6. G26+G28 adoption is queued, not done (brightness condition STAYS MET
   per §4 — but adoption stays queued per the standing rule until the
   orchestrator gates it; no port, no upstream contact).
7. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
8. The G33 binary reads BUILD-sha all session (`7e0ea803…`, ELF,
   mtime frozen — the brief's gated 12th recurrence, corroborated ×3)
   after reading fully-zeroed at G34 time — tabled as an OBSERVATION:
   the frozen-mtime morph-back closes the flash hypothesis on record;
   no verdict (forensics is out of scope; no lane data depended on the
   G33 binary bytes — all G33 receipts live in `ps2x-g33/` + the share
   mirror).
9. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
10. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
11. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes + cmake noise); zero
    warnings point at the hunk lines.
12. The `map_vram_read`-then-`map_vram_write`-sans-commit nesting is now
    proven empirically ×16 (G35 — uncommitted stores persist and the
    unbalanced write never crashes), joining G33 ×16 + G34 ×16
    committed nesting (48 total host-access cycles without incident) —
    not by a second independent writer.
13. Which memory the sampler reads (host-visible mapping vs device-side
    copy) is NOT isolated by this wall: B1 proves the host mapping held
    the tag at sample time, and the output proves the sampler rendered
    it — but whether the sampler read those same host bytes directly or
    a device copy refreshed by the retained flush+wait is exactly what
    the §4 wall separates. No claim beyond the hypothesis is made here.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g35/` (13 files:
  `g35-logcat.txt` 2376 lines incl. 16 `G35: writeback` + 16 `G31: state` +
  16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g35-run-stderr.txt` 0 B, `g35-run-stdout.txt` 0 B, 10 scanout PPMs
  688,143 B each sha `d19e6beb…` unanimous) +
  `parallel-gs-g35-android-build/` (binary 265,853,184 B
  `f3a33f7c…` BuildID `132df20b…`, intact at report time).
- Share-tier mirror: `/Volumes/share/ssx3/ps2x-g35/` (13/13 files,
  `shasum -c` ALL OK — drive distrusted, §2a).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g34/` + G14/G18/
  G20/G22/G24/G26/G28/G29/G30/G31/G32/G33/G34 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 + G35 hunks uncommitted (G34 excised);
  Granite `16e7395f…` + G20-capture set + G28 hunk, all uncommitted —
  ZERO commits anywhere).
- Session-only: `/tmp/g35-*.py` (hunk/score),
  `/tmp/g35-*.sh` (build/run), `/tmp/g35-build.log`,
  `/tmp/g35-stub.cpp`, `/tmp/g35-*.diff` + `/tmp/g35-*.txt` extracts,
  REUSED `/tmp/g34-predict.py` + `/tmp/g34-expected.ppm` (host oracle,
  `d19e6beb…`) + `/tmp/g34-vpage*.txt` + `/tmp/g34-whites.txt`.
- Commits: ssx3 `local/research/G35/` `[G35]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G35 report ends here. Task-1 statics tabled the
commit-less shape (G34's W1 with ONLY `end_vram_write` skipped), the
premise rows (P1 tagged-temp receipt MUST-hold + P2 B1/B2 split with
pre-registered verdict meanings + P3 controls), pre-registered every
H1-barrier/refined-H2 scalar (cleared `aa2fa32572450383`/229376 +
black `99418f1b…` vs tagged `86ad7b887e140383`/229712 + PPM
`d19e6beb…`, 112 whites), reused the REAL G34 predictor unmodified
(ALL CHECKS PASS), and tabled a six-row decision matrix. ONE
commit-less write-back hunk (+54/−0, G34 +55 excised same edit) + ONE
build exit 0 + ONE run exit 0 with 16/16 tagged-temp + 16/16 B1
tagged-B + 112/112 oracle vpages + 10/10 tag-model ladders + 10/10
tag-exact scanouts proves refined-H2 (content suffices, commit
unnecessary) and refutes H1-barrier (0/10 cleared). Next wall is the
barrier-vs-content wall (raw-access placement, no barrier at all), not
adoption; filing still open (G31-E1 applied: explicit pull list,
separate cleanup; share mirror 13/13 OK).

Outcome: refined-H2 — the sparse tag renders EXACTLY without the
commit (content suffices); H1-barrier refuted. No tuning loop was
entered: one hunk, one build, one device run. Retry not used
(exit 0); lldb not used (zero new tombstone — nothing to triage).
