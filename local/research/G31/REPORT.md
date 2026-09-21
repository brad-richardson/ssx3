# G31 report — (b1)/(b2) split: promotion provably off, VRAM sampler mis-samples stale source as cleared (b1) on Adreno (Odin)

Brief: G31 (this turn) — executes G30 §4's ONE next action ONLY: the
(b1)-vs-(b2) promotion/circuit-input split probe ((b1)
`sample_circuit` VRAM-sample misaddressing/mis-decode on Adreno vs (b2)
promoted-backbuffer-image content). Tables + hypothesis + next-action
recommendation, no verdicts beyond the hypothesis. Time box 6 h (used
~0.3 h — measured wall 19:03:55→19:26 EDT; dir snapshot → commit). Read
first per the brief: `local/research/G30/REPORT.md` (all of it: 174/174
uploads land byte-exact, scene + Z raster land, control unchanged, zero
stray — yet circuit1 emits uniform cleared pattern from stale
non-cleared FBP112, with no cleared 512×448 region anywhere in VRAM: (b)
CONFIRMED, (a) refuted per write class). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8–G30 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g31/`
ONLY; removed at end (`mg/` only).

Headline result: **(b1) — the VRAM sampler mis-samples; (b2) is
impossible in this configuration.** (1) Task 1 statics PROVED promotion
cannot engage (`Hacks::backbuffer_promotion` defaults false with
`set_hacks()` uncalled anywhere → register path dead → `promoted1/2`
null on all 16 vsyncs; renderer `layers < super_samples` nulling inert
since `super_samples=1`; host byte-exact predictions for regs + bytes at
every sample time). (2) ONE hunk (in-`vsync()` state dump in
`GSInterface::vsync`, G29 ladder + G30 vpage retained), ONE build (exit 0
`[458/458]`, full identity), verify-then-push with NO gap, ONE run:
**exit 0**, 16/16 `G31: state` + 16/16 `G31: bytes` lines, ZERO new
tombstone. (3) Discriminating bytes: `promoted1` null ×16
(`nprom=0/hack=0` on-device) while the DISPFB1 region (FBP112) holds
stale LOAD bytes at EVERY sample time (16/16 == host `eea04488c453e75b`)
and the circuit emits uniform cleared `(0,0,0,128)` (10/10 ladder ==
G29): the `sample_quad[0]` VRAM path provably does not emit its source
bytes. (b2) is refuted structurally (no promoted image exists to be "fed
cleared bytes"). Procedural note: the 10 scanout PPMs were lost to a
local-glob pull error before device cleanup (G31-E1); the 10 ladder
checksums (P1 == file bytes' checksum) substitute byte-exactly — no
re-run (retry condition not met).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g31-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g31/` (retrieval: logcat + stderr/stdout; PPMs lost, G31-E1) | 50 MB | 3 files, 5,120 KiB allocated PASS |
| SSD `ps2x-g10..g30` + G14/G15/G16/G18/G20/G22/G24/G26/G27/G28/G29/G30 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (snapshot 19:04:10; post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (diagnostic-dump ONLY) | ONE hunk in `gs/gs_interface.cpp` (+65/−0, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 hunks untouched, HUNK_MATCH re-verified); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g31-*` ~30 KB (5 session scripts + build log + hunk applier + score, session-only); G31 evidence dir ~15 KB (text) PASS |
| device | `/data/local/tmp/g31/` ONLY | staged 2 files, pulled 3 (PPMs lost to G31-E1), dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The in-`vsync()` state dump discriminates (b1) vs (b2): `promoted1` null ×16 + DISPFB1-region == load at sample time + cleared circuit output ⟹ (b1) (VRAM sampler mis-reads); `promoted1` non-null ⟹ (b2)-shaped (promotion engaged) |
| observable signal | design tables (§2: promotion-off proof + call census + host predictions + site + matrix) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + verdicts (§3g–3h) |
| alternatives | (b1)-pure (null + stale source + cleared output); (b1)-SOURCE (null + cleared source at sample time — transient writer); OTHER-presence (promoted non-null — static prediction violated, stop); OTHER-transient (null + neither-load-nor-cleared source) |
| stop condition | ONE hunk max (diagnostic-dump ONLY); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: (b1) on all 16 vsyncs (null + stale-load source + cleared
output); live-write control + determinism check both pass; both
retained controls reconfirm byte-exact. No tuning loop was entered: one
hunk, one build, one device run. Retry not used (exit 0 — no retry
condition, and G31-E1 does not meet it); lldb not used (zero new
tombstone — nothing to triage).

## 2. Task 1 — static design (no device runs)

### 2a. Pin verification (pre-work — G30 end state reproduced, ZERO edits before the hunk)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G30 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 39, gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 (320+/4-) — G30 end state (257 = 214 + G30's 43) |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` (pre-existing) |
| G29 ladder + G30 vpage | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 markers) |
| Granite submodule | HEAD `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (== pin); 5 files incl. `memory_allocator.cpp` with `G28: create_image_view` ×1 (G28 hunk present, uncommitted) |
| G28 binary (re-sha, standing hygiene) | 265,841,104 B, sha `450471e2…` FULL-match, magic `7f45 4c46` ELF — **INTACT** |
| G30 binary (re-sha) | 265,847,904 B, **0 nonzero bytes**, sha `75e14219…` (all-zeros), magic `0000` — **9th zero-damage recurrence COMPLETED** (was intact `a1963e66…` at G30 report time; destruction is progressive, not instant) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G30 §0 exactly (snapshot 19:04:10; + G30's own two dirs); post-run re-verified §0 |
| recipe | NDK r30; cmake + ninja; G22/G26/G28/G29/G30 non-sanitizer flags |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 28 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 10 PPMs (8 vsync + first + last) |

### 2b. Promotion-off proof (the split collapses statically; the run confirms on-device)

| link | evidence (file:line) |
| --- | --- |
| default | `Hacks::backbuffer_promotion = false` (`gs/gs_interface.hpp:229`) |
| no enabler | `set_hacks` has ZERO callers in `gs/` + `tools/` + `dump/` + `vulkan/` (declaration + definition only) → flag stays false for the whole run |
| register dead | `register_backbuffer_promotion_fbp` called ONLY from the `if (hacks.backbuffer_promotion && result.image)` post-vsync block (`gs_interface.cpp:4728–4734`) → never fires → `num_promoted_backbuffers == 0` forever |
| fill dead | `promote_render_pass_to_backbuffer` (called from `flush_render_pass:321`) early-returns on the flag (`:4514`) → no `img` ever attached |
| lookup null | `find_promoted_backbuffer` scans `num_promoted_backbuffers` entries (`:4496–4503`) → always nullptr → `promoted1/2 = nullptr` at `:4692–4699` |
| renderer nulling inert | `high_res_scanout=false` (replayer default, unset on cmdline) → `super_samples=1` (`gs_renderer.cpp:4333–4335`) → `layers < 1` never true (`:4337–4340`) → interface-null ⟹ sample-site-null, airtight |
| path taken | `sample_quad[promoted ? 1 : 0]` + `buffers.gpu` storage buffer in the null branch (`gs_renderer.cpp:4160–4164`) → circuit1 ALWAYS samples raw VRAM bytes on this run |
| EN2 guard | `promoted2` lookup guarded by `EN2` (`:4697`); EN2=0 all vsyncs (§2d) → `promoted2` null by guard |

Consequence: (b2) in the strict sense ("promotion engaged but fed
cleared bytes") is STRUCTURALLY IMPOSSIBLE here — no promoted image
exists. The run's job is (i) on-device confirmation (`nprom/hack/p1null`
rule out any missed enable path), (ii) the discriminating sample-time
bytes, (iii) the sampler-input regs for the next wall.

### 2c. Call census + byte regions (what fires, what is read)

| item | observed |
| --- | --- |
| `iface->vsync` calls | 8 Vsync packets, ALL transfer-backed (`xfer=1` §2d) → 8 iterate-true per pass; the terminating iterate call hits EOF without invoking `iface->vsync` → **16 calls/run** (8/pass × 2; `Running frame` ×18 = 8 true + 1 false per pass) |
| `G31: state` lines | 16 (one per call; static seq 0..15; pass 0 = seq 0..7, pass 1 = seq 8..15 — `restart()` reloads VRAM between passes) |
| `G31: bytes` lines | 16 (one per call; zero map-fails expected) |
| logcat cost | +32 lines (~4 KB; 2328 → ~2360, inside the buffer) |
| region B (discriminator) | DISPFB1 FBP112 512×448 → linear bytes [112·8192, 224·8192) = [917504, 1835008), the SAME page window G30 proved == load (mechanism parity with G30's read) |
| region A (live control) | FBP0 pages 0..111 → bytes [0, 917504); proves the read path observes GPU writes as they land |
| last-vsync == G30 | NOTHING between the last `iface->vsync` and G30's read except counter reads + handle swap (replayer loop audit); `GSInterface::vsync` + `renderer.vsync` contain ZERO VRAM writes (register block is flag-dead, FFMD restore is CPU regs) → last-vsync bytes == G30 post-run bytes on every page |

### 2d. Host predictions (byte-exact, pre-registered)

Priv walk (packet-ordered, `Vsync`-packet snapshots; EOF_SYNC=True,
nvsync=8): all 8 vsyncs identical except phase alternating 1,0,1,0,1,0,1,0:

| field | predicted (all 16 seq; phase alternates per pass) |
| --- | --- |
| EN1 / EN2 | 1 / 0 |
| DISPFB1 (FBP/FBW/PSM/DBX/DBY) | 112/8/1/0/0 (== G30 §2d) |
| DSP1 (DW/DH/MAGH/MAGV/DX/DY) | 2560/447/4/0/641/50 (DH corrected mid-analysis: an initial shift-11 host decode gave 895; device data forced the recheck — true shift is 12 → 447; DH+1=448 and (DW+1)/(MAGH+1)=512 close the 512×448 rect math exactly) |
| SM (CMOD/INT/FFMD) | 2/1/0 |
| nprom / hack / p1null / p1 / p2null | 0 / 0 / 1 / 0x0x0x0 / 1 |

Byte predictions (load-blob extraction, G30 math reused; FNV-1a
TRUNCATED basis, G29-E1 carries; sanity full-FNV `6002946899e9cae0` reproduces):

| region | predicted |
| --- | --- |
| B (FBP112) all 16 seq | fnv=`eea04488c453e75b` nz=149721 head=`00000000…` (== load; no writer ever touches pages 112..223) |
| A (FBP0) | ≠ load once scene lands (live control); load-A is `aa2fa32572450383`/nz=229376 = the CLEARED pattern (trap noted: A==ladder-FNV in load state — B is the discriminator, not A); last-vsync head starts `ff490180` (G30 page-0 device head); pass 1 repeats pass 0 exactly under deterministic replay (seq[i] == seq[i+8], bonus check) |

### 2e. Dump-site decision (tabled — exactly one shape picked)

| site | shape | verdict |
| --- | --- | --- |
| A. `GSInterface::vsync`, immediately AFTER `auto result = renderer.vsync(…)` (new lines ~4727–4791) | interface-TU; sees promotion decision + priv regs + `map_vram_read` (G29/G30-proven read, same class); post-call placement = zero submission reordering (wait+read after the vsync's own submission); 2 LOGI lines/call | **CHOSEN** — complete for the decision: interface-null ⟹ sample-site-null is PROVEN (§2b), so the renderer's effective null needs no separate observation; presence routes to OTHER regardless of renderer nulling |
| B. `renderer.vsync` / `sample_crtc_circuit` | renderer-TU; sees effective null + push constants | REJECTED — no CPU VRAM read without bypassing the interface tracker (flush/wait live in `map_vram_read`); calling `flush_submit` mid-vsync with an ad-hoc timeline perturbs the submission stream; zero decision gain over A given §2b |
| C. Promoted-image GPU checksum (manual barrier+copy+submit+wait+restore) | +~25 lines of readback that cannot fire in the expected case | REJECTED — no 1-call helper exists (`device.hpp` has buffer-map only); layout transitions on the about-to-be-sampled image intrude ON the probed path; presence routes to OTHER/stop anyway, so no verdict depends on the checksum — deferred to a follow-up wall IF presence is ever observed (deviation from the brief's letter, tabled with rationale: Task-1 statics proved absence, which the brief assumed plausible) |

Hunk spec: ONE contiguous +65/−0 insertion (`{…}` block at 1-tab
scope); static seq counter; promotion identity (`null?/W/H/layers/fmt`
+ `nprom` + `hack` flag — the flag field closes the "missed enable
path" question empirically); regs (EN/DISPFB1/DSP1/SMODE/phase — the
rect inputs for the next wall); single FNV/nz/head-8B per region
(1,835,008 B map covering pages 0..223). Costs tabled up front: +32
logcat lines (~4 KB); runs inside the timed region (expect inflated
ms/VBlank — diagnostic cost, not a signal); 16 extra HostAccess
wait+reads (content-neutral). Ladder + vpage retained as controls (the
ladder guards non-perturbation: cleared must persist, else the probe
moved the defect).

### 2f. Decision matrix (pre-registered)

| p1 (all 16) | region B (all 16) | region A | reading |
| --- | --- | --- | --- |
| null ×16 | == load `eea04488…` ×16 | varies ≠ load (live) | (b1) CONFIRMED — VRAM-path sampler mis-reads (stale source, cleared output) |
| null ×16 | == cleared `aa2fa325…` at sample times | — | (b1)-SOURCE — source actually cleared live (transient writer); NOT mis-sample; re-examine |
| non-null (any) | — | — | OTHER — static prediction violated → STOP, re-examine enable path; (b2) shape TBD by a follow-up readback wall |
| null ×16 | ≠ load AND ≠ cleared | — | OTHER — transient writer on FBP112?! → re-examine (tear/stale map vs real writer) |

## 3. Task 2 — ONE state probe + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G30's run is the G31 hunk)

| knob / flag | G30 setting | G31 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G30 = G29 + page-dump hunk | G31 = G30 + state-dump hunk | the single delta |

### 3b. Hunk record (ONE hunk, diagnostic-dump ONLY)

`gs/gs_interface.cpp`, ONE contiguous +65/−0 insertion (new lines
~4727–4791) in `GSInterface::vsync()` after the `renderer.vsync` call,
before the `hacks` register block: `g31_seq`-counted state line
(EN/DISPFB1/DSP1/SMODE/nprom/hack/p1+p2 identity/phase, `G31: state`
LOGI) + region-FNV bytes line (A/B FNV-1a truncated basis + nz + head 8
B, `G31: bytes` LOGI; `G31: bytes … map failed` fallback). Files/regs/
loop untouched. Full diff text in `g31-state.diff` beside this report
(mechanically extracted: 65+/0-, single @@ block). G22 HUNK_MATCH + G26
block + G28 Granite hunk + G29 ladder + G30 vpage all untouched; zero
commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G30 recipe, `g31-build.sh` mirrored): exit 0
(`Configuring done (13.3s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp`); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,851,416 B (+3,512 vs G30 — the hunk; NEW size expected) |
| sha (build-time) | `c91719a0c96ef57a6ac2b80f6d4d29f54f515566bc249e0e2c4fd87a5d92367a` (NEW) |
| build-id | `c180f320527af30fd0c1444308a1fb3edf8fb2f2` (distinct from G30 `9452cce3…`) |
| plumbing presence | `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 19:19:24 | `c91719a0…` (binary) + `154d9d85…` (dump) FULL-match build sha |
| device stage | 19:19:24–27 | `rm -rf` + `mkdir` + push dump (0.010 s) + push binary (2.167 s) into `/data/local/tmp/g31/` ONLY |
| on-device sha match | 19:19:27 | `154d9d85…` + `c91719a0…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 19:19 | `logcat -c` (verified empty before) then run — no idle window |
| on-device post-run re-sha | 19:19 | `c91719a0…` FULL-match — intact |
| report-time re-sha | 19:21 | `c91719a0…` FULL-match + ELF magic — **binary INTACT, no 10th zero-damage recurrence this window** |

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g31/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g31/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g31-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790032774→1790032775; logcat 19:19:34.2→19:19:35.0) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28/G29/G30) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 `map failed` |
| logcat | 2360 lines (== G30's 2328 + 32 G31 exactly): init + 18 `Running frame` + 18 G10 + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 9.194 ms` (inflated vs G30's 3.880 — PREDICTED diagnostic cost of 16 extra map+wait+FNV inside the timed region, §2e) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical line 29 in G29/G30 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each — sizes observed in `ls` but files LOST to G31-E1 before pull; §3i) ; stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (ladder + vpage + load line — continuity with G29/G30)

| receipt | observed |
| --- | --- |
| 10 `G29: ladder` | ALL == G29/G30 values: P1 = P2 = P3 = FNV `aa2fa32572450383`, nz = 229,376 (this run's black == G29's black; the probe did NOT move the defect — non-perturbation guard passes) |
| 512 `G30: vpage` | timestamp-stripped lines BYTE-IDENTICAL to G30's run (512/512 equal) — post-run VRAM reconfirmed: uploads landed, scene+Z landed, FBP112 stale, zero stray |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz = 1,184,729 == host load FNV (§2d sanity) — trailing-restart mechanism reproduced on-device a third time |

### 3g. State + bytes verdicts (the split — device vs prediction)

State lines (16/16 match prediction — every field, every seq):

| field | predicted | observed |
| --- | --- | --- |
| seq | 0..15 | 0..15 (8/pass) |
| EN1 / EN2 | 1 / 0 | 1 / 0 ×16 |
| DISPFB1 | 112/8/1/0/0 | 112/8/1/0/0 ×16 |
| DSP1 | 2560/447/4/0/641/50 | 2560/447/4/0/641/50 ×16 (DH corrected §2d) |
| SM | 2/1/0 | 2/1/0 ×16 |
| nprom / hack | 0 / 0 | 0 / 0 ×16 (flag off ON-DEVICE — no missed enable path) |
| p1null / p1 / p2null | 1 / 0x0x0x0 / 1 | 1 / 0x0x0x0 / 1 ×16 |
| phase | 1,0,1,0… per pass | 1,0,1,0,1,0,1,0 ×2 passes |

Bytes lines (16/16 fire, 0 map-fails):

| region | predicted | observed |
| --- | --- | --- |
| B (FBP112, the discriminator) | `eea04488c453e75b` nz=149721 head=`00000000…` ×16 | **16/16 EXACT match** — stale LOAD bytes at EVERY sample time |
| A (FBP0, live control) | ≠ load, varying (scene landing) | all 8 seq values ≠ load, varying per vsync (nz 778796→915657, heads `d5530015…`→`ff490180…`); last-vsync head `ff490180…` == G30 page-0 device head ✓ |
| A determinism (bonus) | seq[i] == seq[i+8] | **8/8 EXACT** — pass 1 repeats pass 0 byte-exact (replay determinism proven; consecutive-equal pairs seq 3==4, 5==6, 11==12, 13==14 show frames sharing scene content — content-neutral) |

### 3h. Split analysis ((b1) — the VRAM sampler reads the wrong bytes)

| link | evidence |
| --- | --- |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0` + §2b structural proof + inert renderer nulling) → `sample_quad[0]` + `buffers.gpu` on every vsync — the circuit ALWAYS samples raw VRAM |
| source bytes at sample time | DISPFB1 region == stale load (`eea04488…`, 16.3% nonzero) at ALL 16 sample times — never cleared, never transient-written |
| circuit output | uniform `(0,0,0,128)` cleared (10/10 ladder §3f) |
| elimination | null-promotion + stale-source + cleared-output ⟹ the VRAM sampler provably does not emit its source bytes; (b1)-SOURCE refuted (B never cleared); OTHER-transient refuted (B == load everywhere); presence-OTHER never triggered |
| verdict | **(b1): VRAM-sample misaddressing/mis-decode on Adreno. (b2) refuted structurally** — no promoted image exists in this configuration, so none could be "fed cleared bytes"; "engaged differently than mac" cannot explain cleared output from a stale source either (the taken path is VRAM sampling, whose source is observed stale) |

### 3i. Scanouts (G31-E1 — files lost, checksums substitute)

The 10 scanout PPMs (observed 688,143 B each in device `ls`) were lost:
the pull loop passed a remote glob that expanded locally (`adb: failed
to stat remote object '…/*.ppm'`), and device cleanup ran in the same
command chain. No re-run was made (§3j). Substitution (exact):
`save_scanout_ppm` writes the P1-readback bytes to the file, so each
`G29: ladder` P1 FNV IS its file's content checksum — 10/10 P1 ==
`aa2fa32572450383`/nz=229376 == G29/G30 values ⟹ the 10 files were
byte-identical to G29/G30's black files (`99418f1b…`). `g14-diff.py`
could not run (no PPMs); its score table would be value-identical to
G30 §3i by the checksum proof above. Lesson recorded: pull by explicit
filename list (or `adb pull <dir>`), never a remote glob; separate
cleanup into its own verified step.

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 32 G31 lines + all controls + `Done!`; G31-E1 (host-side retrieval error) is not a retry condition, and the ladder checksums substitute exactly |
| second shape | NOT USED | out of budget by the stop rule (split closed on the first run) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The in-`vsync()` state dump discriminates (b1) vs (b2) (`promoted1` null ×16 + DISPFB1-region == load at sample time + cleared output ⟹ (b1); non-null ⟹ (b2)-shaped) | **CONFIRMED as (b1), decisively.** Promotion is off structurally (§2b) and on-device (`nprom=0/hack=0/p1null=1` ×16, §3g: no promoted image exists to hold content); the DISPFB1 region holds stale load bytes at all 16 sample times (16/16 `eea04488…`, §3g) while the circuit emits uniform cleared pattern (10/10 ladder, §3f) via the always-taken `sample_quad[0]` VRAM path — the sampler provably does not emit its source bytes (§3h). (b2) refuted. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **a `sample_quad[0]`
VRAM-sample unit probe (the next wall) — NOT adoption.** Rationale: the
defect is now localized to "the circuit's VRAM sampler emits cleared
pattern while its addressed source holds stale bytes" with all sampler
inputs pinned (§3g: FBP=112/FBW=8/PSM=1/DBX=DBY=0, DW=2560/DH=447/MAGH=
4/MAGV=0, super_samples=1, `vram_size-1` spec). Discriminator: controlled
VRAM patterns (e.g. address-echo words) sampled through `sample_circuit[0]`
with known push constants — maps WHERE the Adreno sampler actually reads
(addressing vs decode vs bindless-descriptor fault). Queued behind it
(not this action): G26+G28 adoption once brightness is understood at the
sample level; the Adreno filing — STILL OPEN regardless (content upgrades
again: "circuit VRAM-sampler misaddresses on Adreno with promotion
provably off, readback exonerated"); G18-hunk fix adoption (still queued);
O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G31 additions | the ONE interface hunk (SSD clone worktree only) + session files: `g31-build.sh` + `g31-run.sh` + `g31-state.diff` (G31-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g31/` ONLY (not in git); no PII (`uid: shell`); scanout PPMs lost to G31-E1 (sizes + ladder checksums survive) |
| host analysis | `/tmp/g31-*.py` + `/tmp/g31-*.sh` + `/tmp/g31-build.log` (session-only; `/tmp/g30-*.py` survivors reused for extraction math) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
shasum -a 256 <g28-binary> ; xxd -l 16 <g28-binary>  # §2a INTACT (450471e2…)
python3 -c <nonzero census over g28+g30 binaries>    # §2a 0 of 265847904 (9th recurrence)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g7..g31 + 12 build dirs> ; df -h / $SSD           # §0 (pre 19:04:10 + post 19:21:32)
grep -rn 'set_hacks|promote_render_pass|register_backbuffer|invalidate_promoted' <clone>/gs <clone>/tools <clone>/dump <clone>/vulkan  # §2b (no enabler)
python3 /tmp/g31-predict.py $SSD/ps2x-g13/g13-dump.gs            # §2d (region FNVs)
python3 /tmp/g31-priv.py                                        # §2d (per-vsync regs; DH fixed 895->447)
grep -h 'G30: vpage pass=1 page=000|112' $SSD/ps2x-g30/g30-logcat.txt  # §2d (device anchors)
# (write the ONE hunk: python3 /tmp/g31-hunk.py -- anchor-asserted insertion)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff | grep -c '^@@'  # hunk shape (+65/-0, 5th @@)
cmake -S <clone> -B $SSD/parallel-gs-g31-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g31-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g31-binary> (build, pre-push, report)            # c91719a0… x3 match (intact)
llvm-readelf --notes <g31-binary> ; strings grep x1/x2/x1/x1/x1/x2/x1/x1/x2/x0 ; xxd -l 4  # c180f320… + ELF
python3 /tmp/g31-score.py                                       # §3g (16/16 + 16/16 + 8/8 + controls)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g31/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 28G)
shell 'rm -rf /data/local/tmp/g31 && mkdir -p /data/local/tmp/g31'
push <dump> $G31DIR/g13-dump.gs ; push <g31-binary> $G31DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G31DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G31DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g31-run-stdout.txt 2> g31-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (probe fired)
logcat -d -s Granite:V > $SSD/ps2x-g31/g31-logcat.txt                # 2360 lines
pull $G31DIR/g31-run-stderr.txt $SSD/ps2x-g31/ (0 B) ; pull stdout (0 B)
shell 'ls -la $G31DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
pull $G31DIR/*.ppm -> FAILED (G31-E1, local-glob; files lost)        # §3i (ladder checksums substitute)
shell 'sha256sum parallel-gs-replayer'                               # c91719a0… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g31 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The 10 scanout PPMs were lost to G31-E1 (host-side pull error);
   content is proven byte-identical-black via the 10 ladder P1 checksums
   (§3i), but `g14-diff.py` could not run and no sha-unanimity check exists
   for this run's files. No re-run: retry condition not met.
2. The promoted-image checksum was NOT implemented (site C rejected, §2e):
   justified only because Task-1 statics proved absence AND the run
   confirmed null ×16. If a future configuration ever engages promotion,
   a follow-up wall must add the GPU readback.
3. The (b1) mechanism (misaddressing vs mis-decode vs descriptor fault)
   is open — queued as the §4 next action (unit probe with
   controlled patterns). This brief pins the sampler inputs, not the fault.
4. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
5. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G31 binary intact at all four).
6. An initial DH shift-11 host misread (895) was caught and corrected
   mid-analysis (true shift is 12 → 447; device data forced the recheck)
   — final verdict uses the corrected decode (DH+1=448 closes the rect).
7. G31-E1 lesson recorded (§3i: explicit pull lists, separate cleanup).
8. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness at the sample level per §4; no port, no upstream contact).
9. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
10. The zero-destroyed G30 binary was left destroyed (superseded binary,
    out of scope). 9th recurrence overall (completed this window); G28
    intact; G31 intact (no 10th recurrence).
11. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
12. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
13. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes); zero warnings point at the
    hunk lines.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g31/` (3 files:
  `g31-logcat.txt` 2360 lines incl. 16 `G31: state` + 16 `G31: bytes` +
  512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g31-run-stderr.txt` 0 B, `g31-run-stdout.txt` 0 B; PPMs lost to
  G31-E1) + `parallel-gs-g31-android-build/` (binary 265,851,416 B
  `c91719a0…` BuildID `c180f320…`, intact at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g30/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27/G28/G29/G30 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 hunks uncommitted; Granite `16e7395f…` + G20-capture
  set + G28 hunk, all uncommitted — ZERO commits anywhere).
- Session-only: `/tmp/g31-*.py` (hunk/predict/priv/score),
  `/tmp/g31-*.sh` (build/run), `/tmp/g31-build.log`.
- Commits: ssx3 `local/research/G31/` `[G31]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G31 report ends here. Task-1 statics proved promotion
cannot engage (flag defaults false, set_hacks uncalled, register/fill
dead) and pre-registered byte-exact regs + region FNVs for all 16
sample times; ONE in-vsync() state hunk + ONE build exit 0 + ONE run
exit 0 with 16/16 state + 16/16 bytes lines shows promoted1 null ×16
while FBP112 holds stale load bytes at every sample time and the
circuit emits uniform cleared pattern via the always-taken VRAM path:
(b1) CONFIRMED, (b2) refuted structurally. Next wall is the
sample_quad[0] unit probe, not adoption; filing still open (G31-E1:
PPMs lost, ladder checksums substitute).

Outcome: (b1) — the VRAM sampler mis-samples on Adreno (stale source,
cleared output, promotion provably off). No tuning loop was entered: one
hunk, one build, one device run. Retry not used (exit 0 — no retry
condition, and G31-E1 is not one); lldb not used (zero new tombstone —
nothing to triage).
