# N8D7M8 — execution witness for the original Odin selected copy (read-only source design)

**State: design COMPLETE, verdict B. Read-only: no source edit, build,
replay, boot, device action, lease, push, board/global edit, or upstream
contact. No Turnip/shader/barrier cause is claimed. The orchestrator gates.**

Brief: `local/muse/prompts/N8D7M8.md`. Question: can a nonperturbing
execution witness say whether relevant tick≤2050 GPU draws completed before
the *existing* selected-VRAM copy ran, using the original Present command
and no extra flush, submit, wait, or changed packet order?

Facts to start from: N8D7M6 captured one complete Odin tick2050 GS stream
(SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`;
862,958 packets) and replayed those exact bytes on Mac paraLLEl — Mac
selected input/oracle 300/448 active, Odin 23/448, all 11 descriptor fields
equal (N8D7M6 REPORT §§2–4, ORCH-GATE verdict A). N8D7M7 established the 4
MiB selected copy is recorded before circuit sampling, rejected a second
post-wait flush as an intervention, left O (ordering) unresolved and D
self-contradictory (N8D7M7 REPORT §§2–5, ORCH-GATE PARTIAL). N8D7M5 proved
six FBP112 addresses are written by *executed* packets on the older N8D4
stream (SHA `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d`),
but only 2/6 CPU finals match Mac paraLLEl — packet presence only, never
Odin GPU word values (N8D7M5 REPORT §6, ORCH-GATE).

LSP hover was attempted on the pinned fork and returned no results (no LSP
server for this file type — same basis as N8D7M7 REPORT §1); every code link
below rests on direct source reads at the pinned revs.

## 1. Pins read in this design

| Item | Pin |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, HEAD `a8cfefad109134767b0810b7707b4b58a5dfcca7` |
| Parallel-GS worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` |
| Reference stream (Odin/Mac comparison) | N8D7M6 `n8d7m6.gs`, SHA `f6a78f71…a593` (Mac 300 / Odin 23) |
| Exemplar packet rows (call-path only) | N8D7M5 `trace-excerpt.txt` on old stream SHA `38ace1a3…93f97d` |
| Repo HEAD (receipts only) | read at commit time by `check.py` (not pinned here) |

## 2. Command-order table: one selected-address packet, EE → mapped staging

Exemplar: N8D7M5 replay ordinal **idx 861291 / submit 861292 / tick 2049 /
path 3 / kind draw**, which changed `0x0E0000`, `0x0E0534`, `0x0F0000`
(`0x260703→0x260803`, `0x270903→0x260803`, `0xff230501→0xff230401`) among
others (`trace-excerpt.txt:14-16`); first touch of these words was idx 5223
/ tick 257 (`trace-excerpt.txt:4-8`). Stream caveat: these rows prove the
call path on the *old* stream only; the N8D7M6 stream's writes are unproven
(§5, OTHER). Order is top-to-bottom; record order == GPU execution order
within and across submits on one queue.

| # | Stage | Code site (pinned rev) | Owner / clock |
| --- | --- | --- | --- |
| 1 | EE submits GIF packet | `GS::processGIFPacket`, fork `gs_frontend.cpp:929-956` | EE thread owns packet bytes; EE `vsyncTick` clock |
| 2 | Queue-or-direct split | same file `:931-940` (enqueue `GifPacket` iff `m_worker && !t_inGsWorker`, else synchronous `:942-1048`) | Live device queues; Mac CPU-direct replay executes synchronously (N8D7M5 REPORT §1) |
| 3 | Execution identity assigned | `:947` `m_submitCount.fetch_add` + `:948` `vsyncTick.load` into `GsPacketVramTrace` | Identity is **dequeue-time**: tick/index are read when the worker executes, not when EE enqueued — **loss L1** |
| 4 | Worker dispatch | `GS::executeQueuedCommand`, fork `gs_frontend.cpp:192-199` (`GifPacket` → `processGIFPacket` `:197-198` under `GsWorkerScope`) | GS-worker thread; `RawGifPacket` path `:954-956` iff raw-GIF backend |
| 5 | Renderer recording (parallel) | backend `ps2_gs_parallel_backend.cpp:897-905` → `m_iface->gif_transfer(path,…:901)`; `GSInterface::gif_transfer`, G43 `gs_interface.cpp:5191+` | Presenting/GS-worker thread owns `m_iface` record state; **no GPU execution yet** |
| 6 | Present request built | `GS::buildPresentationRequestUnlocked`, fork `gs_frontend.cpp:757-769` (`vsyncTick` at `:769`); consumed under `m_backendLifetimeMutex` with `Flush()+Sync()+Present` at `:804-812` | Tick owned by priv regs (EE vblank clock) |
| 7 | Selected gate + phase | backend `:441-447` (`selectedRequested` iff `request.vsyncTick==2050` and env `==1`; `vsync.phase = tick&1` at `:447`) | Tick owned by priv regs; phase owned by backend Present |
| 8 | Prior draws flushed first | backend `:452` `m_iface->flush()` → `GSInterface::flush`, G43 `gs_interface.cpp:5153-5165` (`flush_pending_transfer` `:5160` + `renderer.flush_submit(value)` with fresh timeline value `:5161-5162`) | GPU executes previously flushed draws first in submission order |
| 9 | Scanout cmd built | `GSInterface::vsync`, G43 `gs_interface.cpp:5527+` → `renderer.vsync(…)` at `:5576-5578`, recorded into `direct_cmd` | Same presenting thread; record order below is GPU order |
| 10 | Selected descriptor latched | G43 `gs_renderer.cpp:4779-4792` (FBP/FBW/PSM/DBX/DBY from `priv.dispfb1`; phase/stride from `compute_circuit_rect` at `:4776`; mask/samples/promoted `:4786-4788`) | DISPFB1 + DISPLAY1/SMODE own the fields (EE register clock) |
| 11 | **S1: existing early raw copy** | `gs_renderer.cpp:4806-4820`: 4 MiB staging alloc (`:4806-4810`); barrier COMPUTE\|TRANSFER → TRANSFER_READ (`:4813-4815`); `copy_buffer(staging←buffers.gpu, 4 MiB)` (`:4816-4817`); barrier TRANSFER_READ → FRAGMENT_READ (`:4818-4819`); guarded by `:4793-4804` | GPU owns `buffers.gpu` and staging; executes at submit time, not record time |
| 12 | Circuit shader sample (existing) | `sample_crtc_circuit`, `gs_renderer.cpp:4262-4318`: binds `buffers.gpu` (`:4282`), pushes FBP/FBW/DBX/DBY/phase/stride (`:4307-4313`), draws (`:4316`); invoked at `:4834` (after S1) | GPU-side consumer of the same `buffers.gpu` through the shader path, independent of the `copy_buffer` path |
| 13 | Circuit readback + status (existing) | `gs_renderer.cpp:5054-5077` (circuit1 → `circuit1_staging` 512×224×4 `:5060-5073`; `selected_capture_status=2` at `:5076`); raw-circuit early return at `:4990-5031` leaves status 1 (OTHER) | status 2 = ordered completion of the scanout cmd up to this point |
| 14 | End of scanout submit | `flush_submit(0)` at `gs_renderer.cpp:5354`; `GSRenderer::flush_submit` at `:1116+` submits `direct_cmd` at `:1194-1195` | GPU submission order: S1 copy → circuit sample → circuit copy → merged render |
| 15 | Ordered completion (existing) | backend `:601-602` (`m_device->submit(cmd)`; `m_device->wait_idle()`; `Device::wait_idle` decl `Granite/vulkan/device.hpp:274`) | Host observes only after whole-device idle: every mapped byte is post-completion by construction |
| 16 | Host map + decode (existing) | backend `:621-626` (map `selected_vram_staging`, `circuit1_staging`, stage counts); `selectedDecode` `:100-156` + `selectedTileCounts`; oracle `oracleDecodeCensus` `:190-222` on the same mapped bytes; SHAs + 448-vectors + agreements at `:647-663`; oracle controls + `oracle_input_equal` at `:712-729` | Host owns mapped snapshot; clock = post-`wait_idle` |
| 17 | O-window (hypothesis, not fact) | `RawGifPacket` (`:897-905`) takes no `m_backendLifetimeMutex`, while Present's `Flush/Sync/Present` runs under it (`gs_frontend.cpp:804-812`): EE-recorded draws flushed **after** step 8 execute **after** the S1 cmd | If tick≤2050 draws are recorded after step 8, they land after S1 in GPU order — the exact O mechanism; line-cited hypothesis, not observed |

Where packet/tick identity is lost (each is a hard attribution break):

- **L1 — enqueue boundary** (`gs_frontend.cpp:931-948`): the queued
  `GsCommand` carries bytes only; tick and `submitCount` index are assigned
  at worker-execution time (`:947-948`), so on a live device the logged
  tick can differ from the EE-submit-time tick and the replay ordinal ≠ the
  EE submission ordinal. (N8D7M5's witness holds only because CPU-direct
  replay has no worker.)
- **L2 — backend boundary** (`ps2_gs_parallel_backend.cpp:897-905`,
  decl `gs_interface.hpp:269`): `gif_transfer(path, data, size)` takes no
  tick, index, or vsync — identity is dropped at the call.
- **L3 — GIF decode** (`gs_interface.cpp:5191+`): bytes expand into
  register/draw state (`write_register`, packed handlers, optimized draw
  handler `:5234-5241`); no per-packet tag is carried into the pending
  render-pass/transfer state.
- **L4 — submit batching** (`gs_renderer.cpp:1116+`,
  `gs_interface.cpp:5161-5162`): draws from many packets merge into
  `direct_cmd`/async/clear/binning submits; the timeline value is per flush,
  not per packet; `check_flush_stats` (`gs_renderer.cpp:879-909`) can force
  mid-stream submits on memory pressure — submit points are not packet
  points.
- **L5 — GPU execution** (`device.hpp:274,301`, backend `:601-602`):
  cross-submit order is queue submission order; `wait_idle` is
  whole-device and `query_timeline` (`gs_renderer.cpp:1070-1087`) reads a
  device counter — neither attributes completion to a draw.
- **L6 — the S1 copy itself** (`gs_renderer.cpp:4816`): `copy_buffer`
  reads all of `buffers.gpu` with no record of which draws contributed.
- **L7 — host decode** (backend `:621-729`): the full 448-tile census is
  decoded from bytes; bytes ↔ draws are unattributable after L1–L6.

## 3. Candidate witness table

Recording clock = host/EE observation time. GPU execution clock = when the
draw's bytes actually land in `buffers.gpu` relative to the S1 copy in GPU
order. Every census below is the **full 448-tile census** (active = tiles
with RGB max ≥ 32; sparse ≤ 100/448, broad ≥ 250/448 per N8D7M6; else
OTHER), 8 words never stand for the image, and no later tick is used.

| ID | Candidate | Recording clock vs GPU execution clock | Observational or intervention? | (i) writes complete before S1 copy, snapshot sparse | (ii) writes complete after S1 copy | (iii) writes never complete for original Present | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | Existing S1 copy + full census (baseline) | Post-`wait_idle` host map of a same-cmd copy | Observational | sparse | sparse | sparse | OTHER alone (anchors all rows; separates nothing) |
| G | Existing circuit shader sample + 448 `circuit` vector | Same-cmd GPU shader read of same source, after S1 | Observational (independent read path) | broad if copy path lost a broad source; sparse if source itself sparse (then informative OTHER, §4) | sparse | sparse | Separates (i-copy-loss) from {(ii),(iii)} only; (ii) vs (iii) equal → insufficient for three-way |
| Q1 | In-`direct_cmd` `write_timestamp` pair around S1 (`Granite/vulkan/command_buffer.hpp:840`; passthrough `query_pool.hpp:141`; polled in `log_timestamps`, `gs_renderer.cpp:1244-1254`, gated by `enable_timestamps :1263-1266`) | GPU timestamp writes record *when* the copy executed | Same-submit record addition: no reorder of draws/copy, but adds query-pool writes and needs a supported timestamp queue (Turnip `timestampValidBits` unproven — OTHER gap M4). Even if nonperturbing, timestamps measure time, not content | timestamps ordered | timestamps ordered (same order, later content) | timestamps ordered | **Insufficient**: identical prediction in all three cases; counts time, not executed writes |
| Q2 | Calibrated CPU/GPU intervals (`write_calibrated_timestamp` in `flush_submit` `:1121-1125` / `:1221-1225`, `wait_timeline` `:1054-1067`) | Host-wall intervals around submit/wait | Observational for wall time | same intervals | same intervals | same intervals | **Insufficient**: EE/host clock, not a GPU write due-date (same error as `post_tick==2050`, N8D7M7 §3 T4) |
| M | Debug markers/labels (`insert_label`, `gs_renderer.cpp:44-50`; consumed only if `device->consumes_debug_markers()`, e.g. `:4763`, `:3102-3111`) | Record-time annotations, no timing semantics | Observational (ignored by drivers that don't consume them) | same labels | same labels | same labels | **Insufficient**: no completion signal |
| P | GPU page-write audit (per-page counters/atomics in draw/upload shaders) | Would execute inline with draws | **Intervention**: changes the draw shaders themselves; also has no existing hook (no GPU-side analogue of `WriteVramUnlocked` exists on this path — gap M3) | perturbs the work it claims to witness | same | same | **Rejected**: cannot witness the *original* order; new code, new order |
| F | Per-flush timeline attribution, fork-log-only (§5 EXP1) | Host submit clock (timeline value per `flush`, `gs_interface.cpp:5161`) correlated with EE tick at Present | Observational (text only, no Vulkan command change) | same log shape | same log shape | same log shape | **Insufficient for execution** (host submits ≠ GPU completion) but settles the queue-order fact: were tick≤2050 draws recorded after the step-8 flush? |
| L | Post-`wait_idle` extra flush + fresh submit/copy (N8D7M7 T4 S2late) | Extra submit executes work the original Present never ran | **Intervention — rejected** (N8D7M7 REPORT §3): broad fits (ii) late-but-due writes and delayed/missing work equally | broad | broad | sparse | Equal predictions for (i)/(ii) under intervention → cannot award; OTHER |
| W | 8 control words (`kOracleControls`, backend `:712-724`) | Subset of the S1-mapped bytes | Observational but non-census | — | — | — | **Rejected**: no raw word or 8-word set stands for a 448-tile image (brief §1) |
| T | later-tick (2052) snapshot | Different vsync; intervening packets | Different Present | — | — | — | **Rejected** (N8D7M4 gate: intervening packets can change content) |
| X1 | Split-submit between S1 and rest (extra wait mid-order) | Changes execution order | **Intervention — rejected** (N8D7M7 §3 X1) | — | — | — | OTHER, proves nothing about the original order |

Reading the surviving rows: G separates at most (i-copy-loss) from
{(ii),(iii)}. No observational row separates (ii) from (iii): both predict
S1 sparse + G sparse in the original Present, and their only divergence
appears after the Present order is altered (L), where the broad outcome is
equally consistent with late-but-due writes and with work the extra submit
itself flushed. Q1/Q2/M/F all predict identically across the three cases.
Equal predictions cannot discriminate.

## 4. Predeclared A / B / OTHER table

- **A** = a source-grounded witness with a unique observable for each of
  (i) relevant GPU writes complete before the original copy but copied
  snapshot sparse, (ii) those writes complete after that copy, (iii) writes
  never complete for the original Present; with positive/negative controls
  (positive: same-stream Mac broad reference — S1 broad ≥250 AND G broad
  with input==oracle 448/448; negative: a draw-free tick — S1 sparse AND G
  sparse) and a full 448-tile snapshot comparison.
- **B** = source does not expose a sound three-way witness without an
  implementation experiment or device-specific extension; smallest next
  *Mac-only* measurement named (§5).
- **OTHER** = pin/citation/call-path gap (§5 M1–M5), gate miss (descriptor
  mismatch, `selected_capture_status != 2`, map/decode error,
  intermediate 101–249 active), intervention row (L, P, X1), or
  nondiscriminating row (S1 alone, Q1, Q2, M, F, W, T).

| Case | Required unique observable (all on the original Present order, full 448 census) | What the source actually offers | Met? |
| --- | --- | --- | --- |
| (i) | S1 sparse AND G broad AND staging SHAs sparse-like vs Mac broad reference, with positive/negative controls passing | G (`:4262-4318` read of `buffers.gpu` after S1) can show this shape — but only the (i-copy-loss) subcase; a sparse source with "complete" writes (misdirected/elsewhere) predicts S1 sparse + G sparse, identical to (ii)/(iii) | Partial: (i) as a whole has no unique signature |
| (ii) | S1 sparse AND G sparse in-command, with a nonperturbing proof the writes landed after S1 | No nonperturbing post-S1 read exists inside the original order; the only later read (L) is an intervention with equal predictions | **No** |
| (iii) | S1 sparse AND G sparse in-command, with a nonperturbing proof the writes never landed for this Present | Same observable as (ii) under every observational tap (S1, G, Q1, Q2, M, F) | **No: identical to (ii)** |
| Controls | Positive (Mac broad) + negative (draw-free) full-448 runs through identical decoders/descriptor | Exist as procedure (N8D7M6 Mac replay + a draw-free tick), but they calibrate the census, not the (ii)/(iii) split | Do not rescue A |

**Verdict: B.** The (ii)/(iii) pair has no separating observable that
preserves the original Present order: every candidate that keeps the order
(S1, G, Q1, Q2, M, F) predicts identically for (ii) and (iii), and every
candidate that separates them (L extra flush/submit, P shader audit, X1
split-submit) alters what executes. Per the brief, equal predictions → B,
not A. No Turnip, shader, or barrier cause is declared from static code;
this checker record cannot prove execution from source strings alone — it
verifies citations, pins, and table consistency only (see `check.py`).

## 5. Missing links and smallest Mac-only experiment

Explicit gaps (each forces OTHER until closed):

- **M1 (stream gap):** the exemplar packet rows (§2) are from the N8D4
  stream (`38ace1a3…93f97d`); which tick≤2050 packets write selected
  addresses on the N8D7M6 stream (`f6a78f71…a593`) is unproven. No value
  oracle may cross streams (N8D7M5 REPORT §6).
- **M2 (threading gap):** whether EE `gif_transfer` recording can
  interleave the Present thread's step-8→15 window on the Odin build is
  unconfirmed from source alone (N8D7M7 REPORT §7); the O-window (§2 row
  17) is a line-cited hypothesis, not an observed race.
- **M3 (audit gap):** no GPU-side per-draw/per-page write hook exists on
  the parallel path; the only addressed write sink (`WriteVramUnlocked`,
  CPU backend) does not run on the Odin renderer.
- **M4 (query gap):** Turnip timestamp-query support/resolution
  (`timestampValidBits`, query-pool availability inside `direct_cmd`) is
  unproven from this source tree; Q1 cannot be assumed recordable on the
  Odin device.
- **M5 (ordering gap):** no source string binds a specific draw's GPU
  completion to before/after the S1 `copy_buffer` in GPU order; timeline
  values are per-flush (L4) and `wait_idle` is whole-device (L5).

Smallest next **Mac-only** measurement (EXP1, fork-only log attribution —
no device, no Android build, no Vulkan command change):

1. Add a default-OFF, text-only log (new env, e.g.
   `PS2X_N8D7M8_FLUSHLOG=1`; unset/empty = zero behavior change) at two
   existing fork sites: `Present()` entry (backend `:436-453`: log
   `request.vsyncTick` + `counters().presents/gifPackets`) and
   `RawGifPacket` (backend `:897-905`: log sequence counters only — no
   tick is available there by construction, L2, so no tick is claimed).
   Cap 4096 lines (N8D7M5 precedent); zero new probe bytes on top of the
   existing ~5 MiB budget; logs ≤16 MiB.
2. Rebuild `ps2x_tests` only; suite must pass with the flag OFF;
   record fork + G43 pins, binary SHA, codegen SHA. One OFF + one ON
   parallel replay of the N8D7M6 stream (one mini P-lane slot, ≤600 s
   each). Require OFF/ON frame hashes equal AND S1 full-448 census equal
   (nonperturbation gate); stop on any inequality.
3. What it settles: the **queue-order fact** — how many GIF packets were
   recorded before vs after the tick2050 Present's step-8 flush on the
   replay path, and the timeline order of draw submits vs the scanout
   submit. What it cannot settle (stated plainly): GPU execution
   completion — host submits are not execution (row F), so the (ii)/(iii)
   split stays unresolved and no Odin package follows from EXP1 alone.
   After EXP1, the next design is a device-extension question (M4: what
   Turnip-specific completion query exists), not another copy comparison.

## 6. Recommended next action

Gate this design as **B**; if accepted, run the §5 EXP1 Mac-only
flush-attribution experiment first (fork-only, bounded, nonperturbing).
Do not cut a device brief from this design: no nonperturbing tap on the
original Present order separates (ii) from (iii). No push from this worker.

## 7. Receipts / commands (all read-only, repo root unless noted)

Reads: this brief; `~/dev/AGENTS.md`; repo `AGENTS.md`;
`local/AGENTS.local.md`; N8D7M6 `REPORT.md` + `ORCH-GATE.md`; corrected
N8D7M7 `REPORT.md` + `ORCH-GATE.md` (+ `check.py` for the T4/W/D
rejections); N8D7M5 `REPORT.md` + `ORCH-GATE.md` + `trace-excerpt.txt` (+
`check.py` for the CPU-direct witness limits). Sources (direct reads):
fork `ps2_gs_parallel_backend.cpp:100-164,190-222,430-509,590-749,890-905`,
`gs_frontend.cpp:170-271,750-829,920-1059`; G43 `gs_renderer.cpp:40-84,
860-909,1045-1104,1110-1229,1240-1299,4262-4331,4760-4872,4990-5080,5354`,
`gs_interface.cpp:5148-5177,5191-5270,5527-5586`,
`gs_interface.hpp:130-329`, `Granite/vulkan/device.hpp:274,301-310,340`,
`Granite/vulkan/command_buffer.hpp:306,364-367,840`,
`Granite/vulkan/query_pool.hpp:141`. One LSP hover attempt (no server).
`git rev-parse` in both worktrees for pins. New text < 512 KiB (see
`check-result.json`).
