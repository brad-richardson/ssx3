# G32 report — sample_quad[0] unit probe: sampler reads CORRECTLY under host-committed pattern (ordering/coherency reframe, Adreno/Odin)

Brief: G32 (this turn) — executes G31 §4's ONE next action ONLY: the
`sample_quad[0]` VRAM-sample unit probe (controlled patterns through
`sample_circuit[0]` with known push constants — maps WHERE the Adreno
sampler reads: addressing vs decode vs descriptor fault). Tables +
hypothesis + next-action recommendation, no verdicts beyond the
hypothesis. Time box 6 h (used ~0.5 h — measured wall 19:58→20:27 EDT;
task start → commit). Read first per the brief: `local/research/G31/
REPORT.md` (all of it: promotion off structurally + on-device
(`nprom=0/hack=0/p1null=1` ×16), DISPFB1 region stale load at all 16
sample times, circuit emits uniform cleared pattern via the
always-taken `sample_quad[0]` VRAM path: (b1) CONFIRMED, (b2) refuted
structurally). No upstream contact of any kind (standing no-upstream
order — local hunks only, filing stays local).

Machine: same as G8–G31 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g32/`
ONLY; removed at end (`mg/` only).

Headline result: **the sampler reads CORRECTLY — byte-exact — when the
sampled pages are host-committed before the sample.** (1) Task 1 statics
designed a two-zone pattern (zone E address-echo words, zone C constant
`0xE1ABCDEF`; zero zero-RGB words in the window), pinned every sampler
input (push FBP=112/FBW=8/DBX=DBY=0/phase=0/stride=1; spec PSM=1,
VRAM_MASK=`vram_size-1`, SUPER_SAMPLES=1), pre-registered byte-exact
FNVs plus a host swizzle-model expected image, and tabled the decision
matrix. (2) ONE hunk (pre-`renderer.vsync` tracker-aware pattern write
+ `G32: inject` receipt, +30/−0), ONE build (exit 0 `[458/458]`, full
identity), verify-then-push with NO gap, ONE run: **exit 0**, 16/16
`G32: inject` + 16/16 `G31: state` + 16/16 `G31: bytes` (B == pattern
FNV ×16) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`, ZERO new
tombstone, 10/10 scanouts pulled by explicit list. (3) Discriminating
bytes: 10/10 ladder P1/P2/P3 == expected-pattern FNV `9dd120bc6b0df383`
(nz=915264), 10/10 scanouts BYTE-IDENTICAL to the host swizzle-model
PPM (sha `1390410c…`, 11-way unanimity incl. the model), every pixel in
the echo/const set (229376/229376, zero=0) — while the G31 run with
identical regs/knobs emitted uniform cleared from stale source. The
addressing-vs-decode-vs-descriptor split did not trigger (all three
assumed mis-sample persists): the mechanism reframes to
ordering/coherency (H1, §3h) — the per-vsync host-write+commit
(flush+wait+invalidate+barrier for pages 112..223) is the structural
delta besides content. (b1)'s observation stands (cleared output from
stale source with promotion provably off); its mechanism refines.

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g32-android-build` | 6 GB | 4,482,048 KiB PASS |
| NEW SSD `ps2x-g32/` (retrieval: logcat + stdout + stderr + 10 PPMs, explicit list) | 50 MB | 13 files, 25,600 KiB allocated PASS |
| SSD `ps2x-g10..g31` + G14/G15/G16/G18/G20/G22/G24/G26/G27/G28/G29/G30/G31 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (snapshot 20:07:22; post-run re-verified §3: every value identical) PASS |
| SSD clone (source) | ONE hunk max (injection + retained dumps) | ONE hunk in `gs/gs_interface.cpp` (+30/−0, single @@, UNCOMMITTED; G22 + G26 + G28 + G29 + G30 + G31 hunks untouched, HUNK_MATCH re-verified); zero commits in submodule, zero in ps2xGS PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | `/tmp/g32-*` ~1.5 MB (5 session scripts + build log + predict/score + 2 expected PPMs + diff blocks, session-only); G32 evidence dir ~45 KB (text) PASS |
| device | `/data/local/tmp/g32/` ONLY | staged 2 files, pulled 13 by explicit list, dir removed after (`mg/` only); ZERO new tombstones (newest still _23, G27's) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (diagnostic + retry iff O1/O3) | ONE diagnostic run, exit 0; retry not used PASS |
| committed to git | text only | REPORT.md + hunk diff + 2 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Controlled VRAM patterns (address-echo words + constant zone) sampled through `sample_circuit[0]` with known push constants discriminate addressing vs decode vs descriptor fault: echo-set membership + uniformity + ladder FNVs name the fault class and WHERE the sampler reads |
| observable signal | design tables (§2: pattern set + injection site + push constants + pre-registered FNVs/expected image + matrix) + hunk diff + build exit/sha/build-id + verify-then-push chain + ONE bounded run (exit/wall/fate + 16 `G32: inject` + 16 `G31: state` + 16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` + tombstone census) + 10 scanouts scored (uniformity/membership/exact-match) + verdicts (§3g–3h) |
| alternatives | DESCRIPTOR (uniform cleared output from zero-zero-word source); ADDRESSING (pixels in echo set, wrong spots — incl. fixed-address degenerate); DECODE (pixels outside echo sets); CORRECT (byte-exact match to host model — surprise: reframe to ordering/content); OTHER-inject (B ≠ pattern at sample time — write path failed, stop, no sampler verdict) |
| stop condition | ONE hunk max (injection + retained dumps); ONE build (new dir); TWO bounded device runs max (diagnostic + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: CORRECT on all 10 scanouts (byte-exact vs host model) with
source verified patterned at all 16 sample times; A-live-control
byte-identical to G31; all retained controls pass; both post-circuit
calibration (zone-C footprint) and blend questions answered empirically
(1:1, no blend — the exact match proves it). No tuning loop was
entered: one hunk, one build, one device run. Retry not used (exit 0);
lldb not used (zero new tombstone — nothing to triage).

## 2. Task 1 — static design (no device runs)

### 2a. Pin verification (pre-work — G31 end state reproduced, ZERO edits before the hunk)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G31 end state exactly |
| top-level diff stat | CMakeLists 8, gs_interface 104 (39 + G31's 65), gs_renderer 15, tools/CMakeLists 5, gs_dump_replayer 257 (385+/4-) — G31 end state + nothing |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | `G26: debug_mode delivered` ×1 in `tools/gs_dump_replayer.cpp` (pre-existing) |
| G28 hunk | `G28: create_image_view` ×1 in `Granite/vulkan/memory_allocator.cpp` (pre-existing; Granite HEAD `16e7395f…` == pin, 5 files) |
| G29 ladder + G30 vpage + G31 state | still UNCOMMITTED in worktree (`G29: ladder` ×1 + `G29: vram` ×2 + `G30: vpage` ×1 + `G31: state` ×1 + `G31: bytes` ×2 markers) |
| G31 binary (re-sha, standing hygiene) | 265,851,416 B, sha `c91719a0…` FULL-match, magic `7f45 4c46` ELF — **INTACT** |
| G28 binary (re-sha) | 265,841,104 B, sha `450471e2…` FULL-match — **INTACT** |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` snapshot 20:07:22; post-run re-verified §0 (every value identical) |
| recipe | NDK r30; cmake + ninja; G22/G26/G28/G29/G30/G31 non-sanitizer flags |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_23` (G27's, 15:35); `/data` 29 G free |
| `g14-diff.py` + oracles | N/A by design this brief (reference PPMs are load-source renders; pattern source differs deliberately — §3i) |

### 2b. Sampler path audit (what the probe exercises)

| link | evidence (file:line) |
| --- | --- |
| program select | `sample_quad[promoted ? 1 : 0]` (`gs_renderer.cpp:4160`); promoted null ×16 (G31) → `sample_quad[0]` on every vsync |
| VRAM bind | `cmd.set_storage_buffer(0, 0, *buffers.gpu)` in the null branch (`:4164`) — raw VRAM words |
| decode (PSM=1=PSMCT24, 32-bit path) | `payload = vram32.data[addr]`; `PSM != PSMCT32` → alpha forced `0x80`, RGB passthrough (`sample_circuit.frag`); cleared output `(0,0,0,128)` ⟺ RGB=0 word read |
| address | `swizzle_PS2(x, y, fbp*32, fbw, PSM, VRAM_MASK)` with PSMCT32/24 geometry (page 64×32, block 8×8, col 2; log2 6/5/3/3/1) — host-replicated exactly (§2e) |
| coord | progressive (force_progressive, §2d): `coord = fragcoord*(1,1) + (dbx, dby+0)` — pixel-identity |
| post-circuit | merged-path blit (`blit_quad`, LinearClamp) at ≈1:1 into 512×448 (NTSC no-overscan + adapt normalize to 512; §2d); no weave/extwrite/deinterlace (all guards false); blend/offset diagnosed EMPIRICALLY by the constant zone (§2c), not assumed |

### 2c. Pattern set (tabled — exactly one picked)

Window: region B = DISPFB1 FBP112 512×448 = bytes [917504, 1835008)
= pages 112..223 (112 pages; the swizzle audit §2e proves all 229376
sample addrs land in-window, bijectively).

| pattern | shape | verdict |
| --- | --- | --- |
| E+C two-zone (CHOSEN) | zone E (pages 112..167): address-echo words `0xE1000000 \| (byte_addr & 0x00FFFFFF)`; zone C (pages 168..223): constant `0xE1ABCDEF`. EVERY word RGB≠0 (echo: addr ≥ 0x0E0000; const: 0xABCDEF) → uniform-zero output is IMPOSSIBLE under correct sampling | **CHOSEN** — echo maps WHERE (each output pixel inverts to the byte addr read); the constant zone triple-duties as post-circuit calibrator (observed const value solves the blend), viewport diagnosis (its scanout footprint shows scale/offset), and descriptor exclusion (varying output ⟹ content read). Pipeline-agnostic primary verdicts (uniformity + set membership), exact model as the firm leg |
| pure echo (no const zone) | full-window echo | REJECTED — loses the blend/viewport self-calibration; a varying-but-transformed output would need the PMODE packet walk to interpret |
| gradients | smooth ramps | REJECTED — subsumed by echo (monotonic + exact-address); weaker (no shift computation) |
| per-page tags only | 112 distinct page words | REJECTED — coarser than echo (page, not word); echo already encodes page in bits 13+ |

### 2d. Sampler inputs pinned (known push constants + spec + rect)

| input | value | source |
| --- | --- | --- |
| push fbp/fbw/dbx/dby | 112/8/0/0 | G31 state ×16 |
| push phase/phase_stride | 0/1 | `compute_circuit_rect` progressive branch (force_progressive=true from dump parser non-conservative path; `is_interlaced=false` ⟸ scanout `interlaced 0` ×10 G31; alternative-sampling cleared) |
| spec PSM | 1 (PSMCT24) | G31 state ×16 |
| spec VRAM_MASK | `vram_size-1` = 0x3FFFFF (vram_size 4 MiB default, untouched) | `gs_interface.hpp:203` + renderer spec `:4176` |
| spec SUPER_SAMPLES | 1 | `high_resolution_scanout=false` (replayer default) |
| rect | image 512×448, valid 512×448 | (2560+1)/5=512, (447+1)/1=448, progressive even-round |
| circuit image | 512×448 R8G8B8A8 | rect; scanout `internal 512x448, mode 512x448` (NTSC CMOD=2 no-overscan 640×448 + adapt ×4/5 → 512×448) |
| guards | force_deinterlace=false (FFMD=0), double_strike=false (INT=1), extwrite.WRITE=0 (G31 §2c loop audit), need_intermediate_pass=false | code + G31 |
| VSync phase | alternates 1,0 per pass | G31 state ×16 (field tag only; rect unaffected) |

### 2e. Host predictions (byte-exact, pre-registered)

FNV-1a TRUNCATED basis (G29-E1 carries); `/tmp/g32-predict.py`
(session-only); expected PPMs `/tmp/g32-expected{,-flip}.ppm` (688,143 B).

| region | predicted |
| --- | --- |
| B (pattern, all 16 seq) | fnv=`dfe2b6516a519f83` nz=915264 head=`00000ee104000ee1` |
| zone E | fnv=`874869b244559f83` nz=456512 |
| zone C | fnv=`1401c91a89990383` nz=458752 head=`efcdabe1efcdabe1` |
| zero-RGB words in pattern | 0/229376 (uniform-zero ⟹ mis-sample, structurally) |
| swizzle audit | 229376/229376 sample addrs in-window, all distinct (bijective — output set == pattern word set under correct sampling) |
| expected P1 (RGBA α=0x80 over model image) | fnv=`9dd120bc6b0df383` nz=915264 |
| A (live control) | ≠ load, varying, deterministic pass-repeat 8/8; byte-identical to G31's A lines (injection touches B only) |
| G29:vram (restart control) | == load `6002946899e9cae0`/nz=1184729 (trailing restart reloads from dump AFTER the pass — independent of injection) |
| G31 state ×16 | all fields == G31 predictions (regs/knobs identical; injection is VRAM-content-only) |
| logcat | G31's 2360 + 16 `G32: inject` = 2376 lines |

### 2f. Injection-site decision (tabled — exactly one shape picked)

| site | shape | verdict |
| --- | --- | --- |
| A. `GSInterface::vsync`, on EVERY call BEFORE `renderer.vsync` (new lines ~4723–4752) | interface-TU; `map_vram_write(base,n)` + CPU fill + `end_vram_write` (tracker-aware: flush+wait before, commit after — same class as the G29/G30/G31 read path, write direction) + `G32: inject` receipt; post-call G31 dump retained UNCHANGED (verifies B==pattern at sample time) | **CHOSEN** — every sample (both passes, restart-proof) sees the pattern; no dependence on pass boundary; write-path failure routes to OTHER-inject via the retained bytes line |
| B. preload once at startup | replayer post-load write | REJECTED — wiped by pass-1 `restart()` reload; second site = second hunk |
| C. host-side dump edit | modify `g13-dump.gs` | REJECTED — breaks the pinned dump sha (`154d9d85…` verify chain); not a hunk |
| D. inject AFTER `renderer.vsync` (lands before NEXT sample) | post-call write | REJECTED — first sample of each pass (seq 0, 8) sees stale load → mixed outcomes complicate the verdict |

Mechanism assumed by A: CPU map-write + tracker commit lands before
the vsync's own submission samples it (ordering mirrors G31's post-call
read; the commit marks pages 112..223 host-newest so the sample
submission takes the correct barrier — verified empirically by B==pattern
×16 AND, decisively, by the scanout verdict §3h).

Hunk spec: ONE contiguous +30/−0 insertion (`{…}` block at 1-tab
scope); NO counter needed (every-call injection); costs tabled up
front: +16 logcat lines (~1 KB); runs inside the timed region (expect
inflated ms/VBlank — diagnostic cost, not a signal); 16 extra
HostAccess flush+wait+commit cycles (content-neutral by construction —
scene pages untouched).

### 2g. Decision matrix (pre-registered)

| G32 bytes B (16) | ladder P1 (10) + scanouts | reading |
| --- | --- | --- |
| == pattern `dfe2b651…` ×16 | == cleared `aa2fa325…` ×10, scanouts byte-identical black | DESCRIPTOR-shaped — sampler emits content-independent zeros (unbound/zero storage descriptor on Adreno); decode-to-zero alternative; addressing excluded (0 zero-RGB words in window + vpage zero-window census) |
| == pattern ×16 | nonuniform, pixels ∈ echo/const sets (± calibrated blend) | ADDRESSING (real words, wrong spots) or CORRECT (== expected image, either flip) — per-pixel deltas name the shift |
| == pattern ×16 | nonuniform, pixels ∉ sets | DECODE (transform of true words) |
| == pattern ×16 | uniform single echo W | ADDRESSING-fixed to byte addr W (exact WHERE, no model needed) |
| ≠ pattern | — | OTHER-inject — write path failed → STOP, no sampler verdict |

## 3. Task 2 — ONE unit probe + verdict (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G31's run is the G32 hunk)

| knob / flag | G31 setting | G32 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| sanitizer env | ABSENT | ABSENT | non-sanitizer shape |
| binary | G31 = G30 + state-dump hunk | G32 = G31 + pattern-injection hunk | the single delta |

### 3b. Hunk record (ONE hunk, injection + retained dumps)

`gs/gs_interface.cpp`, ONE contiguous +30/−0 insertion (new lines
~4723–4752) in `GSInterface::vsync()` immediately BEFORE the
`renderer.vsync` call: `map_vram_write(917504, 917504)` + two-zone CPU
fill (echo `0xE1<addr>` under page 168, const `0xE1ABCDEF` at/above) +
`end_vram_write` + `G32: inject` receipt (`map failed` fallback).
Regs/loop/circuit untouched. Full diff text in `g32-inject.diff` beside
this report (mechanically extracted with `-U1`: 30+/0-, single @@
block; at default context it shares @@-5 with the adjacent G31 block,
4 lines apart — formatting artifact, tabled). G22 HUNK_MATCH + G26
block + G28 Granite hunk + G29 ladder + G30 vpage + G31 state all
untouched; zero commits in submodule, zero in ps2xGS.

### 3c. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G31 recipe, `g32-build.sh` mirrored): exit 0
(`Configuring done (17.1s)`, `Processor: aarch64`). Build
`cmake --build … --target parallel-gs-replayer -j2`: exit 0 (`[458/458]`).

| item | observed |
| --- | --- |
| warnings | pre-existing only (`-Wunused-function is_legacy_layout` in Granite `command_buffer.cpp` + `-Wshadow FileDeleter` ×3 in `gs_dump_parser.hpp` + cmake-deprecation noise); zero warnings point at the hunk lines |
| binary | `tools/parallel-gs-replayer`, 265,852,240 B (+824 vs G31 — the hunk; NEW size expected) |
| sha (build-time) | `35288fd03c8dd6f559c81fde02255fbe9339ebb0baf3389ec126b5bcdf8eb2b9` (NEW) |
| build-id | `eb6bfa53e9415c85024aa78ec1eee901d034df44` (distinct from G31 `c180f320…`) |
| plumbing presence | `G32: inject` ×2, `G31: state` ×1, `G31: bytes` ×2, `G30: vpage` ×1, `G30: vram` ×1, `G29: ladder` ×1, `G29: vram` ×2, `G28: create_image_view` ×1, `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24:` ×0 — exactly as specified |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓) |

### 3d. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha | 20:21:02 | `35288fd0…` (binary) + `154d9d85…` (dump) FULL-match build sha |
| device stage | 20:21:02–07 | `rm -rf` + `mkdir` + push dump (0.016 s) + push binary (2.121 s) into `/data/local/tmp/g32/` ONLY |
| on-device sha match | 20:21:07 | `154d9d85…` + `35288fd0…` BOTH FULL-match host — push→match gap ~0 s |
| run launch | 20:21 | `logcat -c` (verified empty before) then run — no idle window |
| on-device post-run re-sha | 20:21 | `35288fd0…` FULL-match — intact |
| report-time re-sha | 20:23 | `35288fd0…` FULL-match + ELF magic — **binary INTACT, no zero-damage recurrence this window** |

### 3e. Run table (ONE run — retry not used, §3j)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g32/` ONLY; 2/2 on-device shas FULL-match host (§3d); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g32/g13-dump.gs --iterations 2 --disable-sampler-feedback` (`g32-run.sh` mirrored) |
| exit / wall | **0** / ~1 s wall (`date` 1790036471→1790036472; logcat 20:21:11.9→20:21:12.8) |
| FIX receipt | `G28: create_image_view … skipped …` ×1 (guard engaged, as G28–G31) |
| NARROWING receipt | `G26: debug_mode delivered (…=1, …=0, …=0)` ×1 |
| DIAGNOSTIC receipts | 16 `G32: inject` + 16 `G31: state` + 16 `G31: bytes` (§3g) + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram` (§3f); 0 `map failed` |
| logcat | 2376 lines (== G31's 2360 + 16 G32 exactly): init + 18 `Running frame` + 18 G10 + 32 G11 records + 8 Stalled posts all `success: yes` + `Total time per VBlank: 8.871 ms` (same inflated class as G31's 9.194 — diagnostic cost of 16 extra map+wait+commit inside the timed region, §2f) + 10 `G8: wrote` + `Done!` LAST; 0 `success: no`; 0 `corrupted chunk`; the single `E Granite: Failed to load RenderDoc` init line is pre-existing noise (identical in G29–G31 logcats; `use_rdoc` false) |
| fate | clean exit 0 through Device teardown; NOT O1/O2/O3/O4/O5/O6 |
| device outputs | 10 scanouts (688,143 B each) ALL pulled by explicit list (§3i); stdout 0 B; stderr 0 B; ZERO new tombstone (newest still _23); device dir removed after (`mg/` only ✓) |

### 3f. Control receipts (inject + ladder + vpage + load line — continuity with G29–G31)

| receipt | observed |
| --- | --- |
| 16 `G32: inject` | ALL `base=917504 n=917504`, 0 `map failed` — injection fired on every vsync, both passes |
| 10 `G29: ladder` | ALL P1=P2=P3=FNV `9dd120bc6b0df383`, nz=915264 == expected-pattern FNV (§2e) — the probe moved the output EXACTLY onto the model (uniform cleared `aa2fa325…` gone) |
| 512 `G30: vpage` (all pass=1, pages 0..511) | 112 pattern pages (112..223) == per-page pattern FNVs 112/112; other 400 pages BYTE-IDENTICAL to G31's vpage 400/400 — injection perturbed nothing outside B |
| 1 `G29: vram` | FNV `6002946899e9cae0`, nz=1,184,729 == host load FNV — trailing-restart mechanism reproduced on-device a fourth time (restart control passes) |
| 16 A-lines | BYTE-IDENTICAL to G31's 16 A-lines (scene path untouched — non-perturbation proven beyond determinism) |

### 3g. Inject + state + bytes verdicts (source verified patterned at every sample time)

State lines (16/16 match G31 predictions — every field, every seq;
regs/knobs identical by construction):

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
| B (the discriminator) | pattern `dfe2b6516a519f83` nz=915264 head=`00000ee104000ee1` ×16 | **16/16 EXACT match** — patterned source at EVERY sample time (OTHER-inject never triggered) |
| A (live control) | ≠ load, varying, pass-repeat 8/8 | 8/8 EXACT pass-repeat; all ≠ load; all 16 lines byte-identical to G31's A-lines |

### 3h. Split analysis (CORRECT — the sampler reads its source exactly; mechanism reframes to ordering/coherency)

| link | evidence |
| --- | --- |
| sampling path taken | `promoted1` null ×16 (on-device `nprom=0/hack=0`) → `sample_quad[0]` + `buffers.gpu` on every vsync — same path as G31 |
| source bytes at sample time | region B == two-zone pattern (16/16 `dfe2b651…`, zero zero-RGB words) — never cleared, never stale |
| circuit output | 10/10 ladder P1/P2/P3 == expected-pattern FNV `9dd120bc6b0df383`/nz=915264; 10/10 scanouts byte-identical to the host swizzle-model PPM (sha `1390410c…`, §3i); 229376/229376 pixels in echo/const set, const pixels exactly 114688 (half-frame zone C), zero-RGB pixels 0 |
| post-circuit calibration | the byte-exact match (no flip needed) proves the blit is 1:1 with no blend and no offset — zone C's footprint lands exactly on-model; the PMODE/blend questions answer themselves empirically |
| elimination | DESCRIPTOR refuted (output varies with content, exact); ADDRESSING refuted (zero misplaced pixels — deltas all zero); DECODE refuted (all pixels in-set, exact); OTHER-inject never triggered |
| verdict | **CORRECT: the Adreno VRAM sampler emits its addressed source bytes exactly when the sampled pages are host-committed before the sample.** G31's cleared-from-stale observation stands; its mechanism (addressing/decode/descriptor) is superseded: the live mechanism is ordering/coherency (H1, §4) — the per-vsync host-write+commit (flush+wait+invalidate+barrier for pages 112..223) is the structural delta besides content |

### 3i. Scanouts (10/10 pulled by explicit list — G31-E1 applied)

Explicit pull list (12 files + logcat; each named, zero globs):
`g32-run-stdout.txt`, `g32-run-stderr.txt` (both 0 B),
`g13-dump.gs.g10-vsync0.ppm` … `g10-vsync7.ppm`,
`g13-dump.gs.g8-first.ppm`, `g13-dump.gs.g8-last.ppm` (all 688,143 B).
All 13 pulls individually confirmed (`1 file pulled, 0 skipped`).
Cleanup ran as its OWN verified step AFTER pull verification
(`rm -rf` + `ls` → `mg/` only, exit 0).

| file | sha256 | vs expected model |
| --- | --- | --- |
| 10/10 scanouts | `1390410c8ffc6edeeed35046bc65e49ed01c7f90ef4ed4645bbc7eee4039e293` (unanimous) | BYTE-IDENTICAL to `/tmp/g32-expected.ppm` (same sha — 11-way unanimity incl. the host model); flipped variant NOT matched (orientation is y-down as modeled) |

Pixel census (per file): uniform=false; in echo/const set
229376/229376; const-zone pixels 114688; zero-RGB pixels 0.
`g14-diff.py` N/A by design (reference PPMs are load-source renders;
the pattern source differs deliberately — the host swizzle model is
this brief's oracle, matched exactly).

### 3j. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — the run exited 0 with the full loop + 16 G32 + 32 G31 lines + all controls + `Done!` |
| second shape | NOT USED | out of budget by the stop rule (split closed on the first run — CORRECT branch) |
| lldb triage | NOT USED | zero new tombstone, exit 0 — nothing to triage |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Controlled VRAM patterns sampled through `sample_circuit[0]` with known push constants discriminate addressing vs decode vs descriptor fault | **SUPERSEDED by CORRECT — decisively.** Source verified patterned at all 16 sample times (16/16 `dfe2b651…`, §3g) while the circuit emitted the pattern EXACTLY (10/10 ladder P1/P2/P3 == `9dd120bc6b0df383`, 10/10 scanouts byte-identical to the host swizzle model, sha `1390410c…` unanimous, §3h–3i) via the same always-taken `sample_quad[0]` VRAM path G31 proved emits cleared from stale source. Addressing, decode, and descriptor fault are all refuted (zero misplaced pixels, all pixels in-set, output varies exactly with content). The sampler needs no fix at the sample level — the defect reframes to ORDERING/COHERENCY (H1): the per-vsync host-write+commit (flush+wait+invalidate+barrier for pages 112..223) is the structural delta besides content. One hunk, one build, one device run; retry + lldb correctly unspent (§3j). |

The ONE next action the numbers justify: **a write-back control wall
(same sync structure, stale bytes re-written) — NOT adoption.**
Rationale: G32 changed TWO things vs G31 (content: stale→pattern;
sync: +host-write+commit per vsync). Discriminator: the G32 hunk shape,
but re-writing the SAME bytes it read (map-read B → temp → map-write B
back → commit; no external data needed) — splits H1 (ordering/coherency:
output goes stale-correct ⟹ the commit/barrier was the fix) from H2
(content-dependent fault: output stays cleared ⟹ the pattern content
was the fix). Queued behind it (not this action): G26+G28 adoption
once brightness is understood at the sample level (CLOSER now — the
sampler is proven exact under commit); the Adreno filing — STILL OPEN
regardless (content upgrades again: "circuit VRAM sample goes stale→
cleared without a host commit, byte-exact with one — ordering/coherency,
promotion provably off, readback exonerated"); G18-hunk fix adoption
(still queued); O1 writer naming (still open).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk + G28 writer-fix hunk compiled in (logging-only/guard, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26/G29/G30/G31 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified post-hunk) |
| G24 plumbing hunk | stays SUPERSEDED (diff text survives in `local/research/G24/`) |
| G32 additions | the ONE injection hunk (SSD clone worktree only) + session files: `g32-build.sh` + `g32-run.sh` + `g32-inject.diff` (G32-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0); no runtimes staged (non-sanitizer binary) |
| logcat/scanout sizes | run receipts of our own binary in SSD `ps2x-g32/` ONLY (not in git); no PII (`uid: shell`); all 10 PPMs pulled (shas + census in §3i) |
| host analysis | `/tmp/g32-*.py` + `/tmp/g32-*.sh` + `/tmp/g32-build.log` + `/tmp/g32-expected*.ppm` (session-only) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7/Granite rev-parse HEAD ; diff --stat           # §2a (16e7395f…, G28 hunk present)
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
shasum -a 256 <g31-binary> ; xxd -l 16 <g31-binary>  # §2a INTACT (c91719a0…)
shasum -a 256 <g28-binary>                             # §2a INTACT (450471e2…)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g32 + 14 build dirs> ; df -h / $SSD           # §0 (pre 20:07:22 + post 20:23:46)
grep -n 'sample_quad|sample_circuit|super_samples' <clone>/gs/gs_renderer.cpp  # §2b audit
python3 /tmp/g32-predict.py                                # §2e (pattern FNVs + expected PPMs)
# (write the ONE hunk: python3 /tmp/g32-hunk.py -- anchor-asserted insertion)
git -C $SSD/parallel-gs-g7 diff --stat -- gs/gs_interface.cpp ; diff -U1 | grep -c '^@@'  # hunk shape (+30/-0, single @@)
cmake -S <clone> -B $SSD/parallel-gs-g32-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §3c exit 0
cmake --build <g32-build> --target parallel-gs-replayer -j2    # §3c exit 0 [458/458], pre-existing warnings
shasum -a 256 <g32-binary> (build, pre-push, post-run, report)  # 35288fd0… x4 match (intact)
llvm-readelf --notes <g32-binary> ; strings grep 2/1/2/1/1/1/2/1/1/2/0 ; xxd -l 4  # eb6bfa53… + ELF
python3 /tmp/g32-score.py                                       # §3f–3i (16/16 + 10/10 + 512 + EXACT x10)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g32/` ONLY; `mg/` never touched):

```text
shell 'getprop model/release ; ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _23 newest, 29G)
shell 'rm -rf /data/local/tmp/g32 && mkdir -p /data/local/tmp/g32'
push <dump> $G32DIR/g13-dump.gs ; push <g32-binary> $G32DIR/parallel-gs-replayer  # §3d
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§3d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G32DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G32DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g32-run-stdout.txt 2> g32-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 0 (probe fired)
logcat -d -s Granite:V > $SSD/ps2x-g32/g32-logcat.txt                # 2376 lines
pull $G32DIR/g32-run-stderr.txt $SSD/ps2x-g32/ (0 B) ; pull stdout (0 B)
pull $G32DIR/<each of the 10 PPMs by explicit name> $SSD/ps2x-g32/   # §3i (all 1-file-pulled; NO glob)
shell 'ls -la $G32DIR/ ; ls -lt /data/tombstones/ | head -4'         # 10 scanouts sized; ZERO new tombstone
shell 'sha256sum parallel-gs-replayer'                               # 35288fd0… FULL-match (post-run intact)
shell 'rm -rf /data/local/tmp/g32 && ls /data/local/tmp/'            # DEVICE_CLEAN, OWN step (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The H1-vs-H2 split (ordering/coherency vs content-dependent fault)
   is open — queued as the §4 next action (write-back control with the
   same sync structure). This brief proves exact sampling under commit,
   not which delta (content vs sync) fixed G31's cleared output.
2. The PMODE/blend/offset questions were answered empirically (1:1, no
   blend — the byte-exact match proves it), not by priv decodes; no
   packet-walk oracle was built (unneeded — the constant zone's
   footprint lands exactly on-model).
3. The vpage zero-window census found high-VRAM cleared-pattern pages
   (nz≈2048, RGB=0) plus two all-zero pages (510–511, nz=0): had the
   outcome been uniform-zero, addressing-to-zero-window could not have
   been excluded by census alone — moot here (CORRECT branch), recorded
   for honesty.
4. `g14-diff.py` did not run (reference PPMs are load-source renders;
   N/A by design — the host swizzle model is this brief's oracle and
   matched byte-exactly, 11-way sha unanimity).
5. No mac VRAM/sample oracle exists for the circuit path (would say how
   the same sampler inputs behave on a working backend; out of budget —
   ONE build max, Android).
6. G29-E1 carried (truncated FNV basis reused deliberately for
   comparability); G29-E2 carried (push-time + post-run + report-time
   re-shas taken — G32 binary intact at all four).
7. G26+G28 adoption is queued, not done (conditioned on understanding
   brightness at the sample level per §4 — closer now; no port, no
   upstream contact).
8. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
9. The zero-destroyed G30 binary was left destroyed (superseded binary,
   out of scope). Still 9 recurrences overall (none this window); G28
   intact; G31 intact; G32 intact.
10. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
11. No lldb (decision tabled §3j); OS tombstone store untouched (no new
    tombstone this brief). `upstream/` + harness code untouched; no new
    dumps; run budget 1/2 spent (retry intentionally unspent — exit 0).
12. Build warnings were observed via full-log grep (pre-existing
    `-Wunused-function` + `-Wshadow` classes + cmake noise); zero
    warnings point at the hunk lines.
13. The `map_vram_write` path had zero prior callers (first live use is
    this hunk); its correctness is proven empirically by B==pattern ×16
    + 112/112 pattern vpage + the exact scanout match — not by a second
    independent writer.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g32/` (13 files:
  `g32-logcat.txt` 2376 lines incl. 16 `G32: inject` + 16 `G31: state` +
  16 `G31: bytes` + 512 `G30: vpage` + 10 `G29: ladder` + 1 `G29: vram`,
  `g32-run-stderr.txt` 0 B, `g32-run-stdout.txt` 0 B, 10 scanout PPMs
  688,143 B each sha `1390410c…` unanimous) +
  `parallel-gs-g32-android-build/` (binary 265,852,240 B
  `35288fd0…` BuildID `eb6bfa53…`, intact at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g7/`-`ps2x-g31/` + G14/G15/G16/
  G18/G20/G22/G24/G26/G27/G28/G29/G30/G31 build dirs + SSD clone (HEAD `3a66c19…`,
  G22 + G26 + G29 + G30 + G31 + G32 hunks uncommitted; Granite `16e7395f…` + G20-capture
  set + G28 hunk, all uncommitted — ZERO commits anywhere).
- Session-only: `/tmp/g32-*.py` (hunk/predict/score),
  `/tmp/g32-*.sh` (build/run), `/tmp/g32-build.log`,
  `/tmp/g32-expected*.ppm` (host oracles, `1390410c…`).
- Commits: ssx3 `local/research/G32/` `[G32]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunks stay
  uncommitted in worktrees).

TAIL-RECEIPT: G32 report ends here. Task-1 statics designed a two-zone
pattern (echo + const, zero zero-RGB words) with pinned sampler inputs,
pre-registered FNVs, a host swizzle-model oracle, and a five-row
decision matrix; ONE pre-vsync injection hunk + ONE build exit 0 + ONE
run exit 0 with 16/16 inject + 16/16 pattern-source bytes shows the
Adreno sampler emitting its source EXACTLY (10/10 ladder == expected
FNV, 10/10 scanouts byte-identical to the model, sha-unanimous):
addressing/decode/descriptor all refuted, mechanism reframed to
ordering/coherency (H1). Next wall is the write-back control, not
adoption; filing still open (G31-E1 applied: explicit pull list,
separate cleanup).

Outcome: CORRECT — the VRAM sampler reads exactly under host-committed
pattern (byte-exact vs model on all 10 scanouts). No tuning loop was
entered: one hunk, one build, one device run. Retry not used (exit 0);
lldb not used (zero new tombstone — nothing to triage).
