# N8D7M9 — live identity-carrying witness design (read-only source design)

**State: design COMPLETE, predeclared verdict A (conditional). Read-only: no
source edit, build, replay, boot, device action, lease, push, board/global
edit, or upstream contact. No Turnip/shader/barrier/driver cause is claimed.
The orchestrator gates. Cited source strings cannot prove execution; the
checker verifies pins, cited rows, and table invariants only.**

Brief: `local/muse/prompts/N8D7M9.md`. Question: the smallest live-Odin
identity-carrying witness that establishes which relevant GIF packets/draws
entered the original Present's GPU command stream before or after its
existing 4 MiB selected-VRAM copy — no extra flush/submit/wait, no packet
reorder, host submission never treated as GPU completion.

Facts to start from: N8D7M6 captured one complete Odin tick2050 stream (SHA
`f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`;
862,958 packets) with Mac 300/448 vs Odin 23/448 selected active tiles,
descriptor equal (N8D7M6 REPORT §§2–4, ORCH-GATE verdict A). N8D7M7 mapped
the S1 copy before circuit sampling, rejected post-wait S2late as an
intervention, left O unresolved and D self-contradictory (ORCH-GATE
PARTIAL). N8D7M8 found tick/index lost at the EE queue (L1) and raw-GIF
backend (L2) boundaries, per-flush timelines and whole-device wait-idle
unattributing per-draw completion, and Mac replay unable to reproduce the
live Odin interleave — verdict B for the inspected paths, recommending
exactly this identity-carrying design (N8D7M8 REPORT §5, ORCH-GATE).

LSP was attempted (no server for this file type, same basis as N8D7M7 §1 /
N8D7M8 §2); every code link rests on direct source reads at the pinned
revs. Full 448-tile census throughout (active = RGB max ≥ 32; sparse ≤
100/448, broad ≥ 250/448 per N8D7M6); individual control words never
represent the image.

## 1. Pins read in this design

| Item | Pin |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, HEAD `a8cfefad109134767b0810b7707b4b58a5dfcca7` |
| Parallel-GS worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` |
| Reference stream | N8D7M6 `n8d7m6.gs`, SHA `f6a78f71…a593` (Mac 300 / Odin 23, descriptor equal) |
| Repo HEAD (receipts only) | read at commit time by `check.py` (not pinned here) |

## 2. Boundary/clock table: EE enqueue → mapped staging

Order is top-to-bottom; record order == GPU execution order within and
across submits on one queue. Clocks: **(1)** EE enqueue time, **(2)** GS
record time, **(3)** Vulkan submission order, **(4)** GPU completion
relative to the copy. The witness carries identity through clocks 1–3;
clock 4 is surveyed in §4 and explicitly left unattributed per-draw.

| # | Boundary | Code site (pinned rev) | Identity carried / log point (default-OFF) | Lock/atomic/byte cost |
| --- | --- | --- | --- | --- |
| B1 | EE enqueue | fork `gs_frontend.cpp:931-939` (`m_worker && !t_inGsWorker` → `cmd.bytes.assign` + `enqueue`) | NEW: stamp `eeTick` (`vsyncTick.load(acquire)`, atomic per `gs_types.h` usage at `:948`) + `eeSeq` (new `m_eeEnqueueCount.fetch_add(relaxed)`) into two new `GsCommand` u64 fields before `enqueue`. Log: EE ring entry `(eeSeq, eeTick, sizeBytes)` | 1 acquire load + 1 relaxed fetch_add (~ns); +16 B/command descriptor (queue caps 1024 desc / 16 MiB in `gs_worker.h:123-124,154-160` absorb +16 KiB worst case); ring append = 1 relaxed fetch_add, no new mutex |
| B2 | Queue transport (FIFO) | `gs_worker.h:139` (`enqueue`), `:157-160` (mutex + deque), `:161` (`m_executing` under same mutex) | FIFO preserves EE submission order (`gs_worker.h:12-16`); no log, no change. New POD u64 fields ride `std::move` through the deque with existing move semantics | zero new sync; +16 B in-flight per queued command |
| B3 | Worker dispatch | fork `gs_frontend.cpp:192-199` (`executeQueuedCommand`, `GifPacket` → `processGIFPacket` under `GsWorkerScope` `:134-140`) | No change. Path is resolved here, not at B1: `m_curGifPath` is worker-mutated (EE-side read would race); `NoteGifPath` is itself a queued command (`gs_frontend.h:144-145`), so FIFO join at dequeue is exact. Log: GS ring entry `(eeSeq, eeTick, path_dq, tick_dq, idx_dq)` joining enqueue identity to dequeue identity | one ring append; no new lock (runs on worker under existing `m_stateMutex` at `:943`) |
| B4 | Execution identity (existing, kept) | fork `gs_frontend.cpp:947-950` (`m_submitCount.fetch_add` + `vsyncTick.load` into `GsPacketVramTrace`) | Existing dequeue-time `(tick_dq, idx_dq)` kept as-is; the new `(eeTick, eeSeq)` travels alongside as the EE-order identity that L1 previously dropped. `RawGifPacket` call at `:955-956` gains 3 u64 params `(eeTick, eeSeq, idx_dq)` | 3× u64 by value, no heap, no lock |
| B5 | Backend virtual + counters | fork `ps2_gs_parallel_backend.cpp:897-905` (`RawGifPacket` → `m_iface->gif_transfer(path,…:901)`); virtual decl `gs_backend.h:39-45` | Signature change (pseudocode §5, H1–H2): `RawGifPacket(path, data, size, eeTick, eeSeq, idx)` → `gif_transfer(path, data, size, pktId)` with `pktId = (eeSeq, eeTick)`. Existing per-packet relaxed `fetch_add` counters (`:902-904`) are the precedent that per-packet atomics are acceptable here | params only; zero new atomics required on this path |
| B6 | GIF decode → draw recording | parallel `gs_interface.cpp:5191+` (`gif_transfer(path, data, size)`), optimized handler `:5234-5241`, `drawing_kick_append` at `:3329`, prim append `render_pass.prim[primitive_count]` at `:3694` | NEW: `GSInterface` field `curPkt` set at `gif_transfer` entry; each recorded prim stores its `pktId` (+8 B/prim; array bound unconfirmed — gap G5). Per-`gif_transfer` footprint log: `(eeSeq, eeTick, path, primDelta, fbTouch)` where `primDelta` = `primitive_count` exit−entry and `fbTouch` = whether `tracker.mark_fb_write` fired (`:3673-3679` bbox-expand path) with FBP112 ctx. Relevance proxy = FBP112-footprint prims (residual: fully-clipped prims — gap G6) | +8 B `GSInterface` field; +8 B/recorded prim; footprint line ≈ 48 B text per packet into the GS ring (deferred emit, never fprintf on the hot path) |
| B7 | Internal pressure cuts | parallel `gs_renderer.cpp:879-910` (`check_flush_stats` → `tracker.mark_memory_pressure()` at `:903` → `flush_if_memory_pressure` → `flush_render_pass(PressureFlush)`); call sites `:1485,1588,1737,3037` | No change. Cuts only create *more* flushes, each with its own timeline value; attribution (§3) is per-flush-value, so cuts are covered, not defeated. Log point unchanged (B8) | zero |
| B8 | Per-flush attribution (the witness core) | parallel `page_tracker.cpp:935-961` (`mark_submission_timeline`: `++timeline`, `flush_render_pass(reason)`, returns value); reasons enum `page_tracker.hpp:122-134`; `GSInterface::flush` at `gs_interface.cpp:5153-5165` (`flush_pending_transfer` + `mark_submission_timeline` + `flush_submit(value)` at `:5161-5162`) | NEW: at each `mark_submission_timeline`, append one attribution line `(timelineValue, reason, eeSeqLo, eeSeqHi, pktCount, eeTickLo, eeTickHi)` for the flushed render-pass range (prim `pktId`s read off the B6 tags; empty flushes log `pktCount=0`). Present-entry flush (backend `:452` `m_iface->flush()`) yields `V_pre`; the S1 copy is recorded later in the same `direct_cmd` (B9), so `V ≤ V_pre` ⟹ submitted before S1 | ≈ 128 B text per flush; flushes/vsync O(10s) → single-digit KiB/vsync; no GPU bytes; no new lock (`timeline` is `++` on the presenting thread, existing discipline) |
| B9 | Scanout cmd: descriptor + S1 copy | parallel `gs_renderer.cpp:4779-4792` (descriptor latch), `:4806-4820` (staging alloc + barrier `:4813-4815` + `copy_buffer` `:4816-4817` + barrier `:4818-4819`, guarded `:4793-4804`) | No change (the *original* copy is witnessed, never moved). Ordering ground: same-`direct_cmd` record order + in-order queue + barriers ⟹ draws submitted pre-S1 execute pre-S1 | zero |
| B10 | Circuit sample + readback + submit | `gs_renderer.cpp:4834` (`sample_crtc_circuit` after S1), `:5054-5077` (circuit1 → staging, `selected_capture_status=2` at `:5076`), `:5354` (`flush_submit(0)`); `flush_submit` body `:1116-1226`, timeline signal `:1197-1208` | No change. `flush_submit(value)` submission order = record order; per-submit completion stays unattributed (§4). Log: `(timelineValue → submitOrdinal)` one line at `flush_submit` entry — text only | ≈ 64 B text per submit |
| B11 | Ordered completion + host map | fork backend `:601-602` (`submit(cmd)` + `wait_idle()`, decl `Granite/vulkan/device.hpp:274`); map + decode `:621-729` (`map_host_buffer`, `selectedDecode`, oracle census, SHAs, `oracle_input_equal`) | No change. Rings drained to the text log here (post-`wait_idle`, off the hot path). Full 448-tile census decoded from mapped bytes exactly as today | log ≤ 4 MiB text total (cap §6); committed receipts ≤ 512 KiB (summaries only) |

Threading note (O-window hypothesis, N8D7M7 §2 row 15 / N8D7M8 §2 row 17):
`RawGifPacket` (`:897-905`) takes no `m_backendLifetimeMutex`, while
Present's `Flush/Sync/Present` runs under it (`gs_frontend.cpp:804-812`).
The witness does not assume whether EE recording interleaves the Present
window on Odin — it *logs* it (B3/B8 join shows which `eeSeq` landed in
which post-`V_pre` flush). Gap M2 is thus converted from assumption into
measurement.

## 3. Why this separates (i) / (ii) / (iii)

`V_pre` = timeline value of the Present-entry flush (backend `:452` →
`gs_interface.cpp:5161`). The S1 `copy_buffer` is recorded after it in the
same `direct_cmd` (B9). In-order queue + barriers give: flushed at
`V ≤ V_pre` ⟹ submitted — and executed — before the S1 copy; first
flushed at `V > V_pre` ⟹ after it. Relevance = FBP112 footprint (B6) on
tick≤2050 packets (`eeTick ≤ 2050` from the B1 clock, not the dequeue
clock — immune to L1 skew).

| Case | Required unique observable (original Present order, full 448 census) | Witness prediction |
| --- | --- | --- |
| (i) relevant source before copy, sparse copy | S1 sparse AND G broad AND FBP112-footprint `eeSeq`s (eeTick≤2050) flushed at `V ≤ V_pre`, staging SHAs sparse-like vs Mac broad ref | copy/barrier/readback path loss; pre-S1 submission is execution-grounded (§2 B9) |
| (ii) relevant writes after copy | S1 sparse AND G sparse AND FBP112-footprint `eeSeq`s (eeTick≤2050) first flushed at `V > V_pre` (recorded after the Present-entry flush) | late-but-due writes; no extra submit was added — the order is the original order |
| (iii) relevant writes absent | S1 sparse AND G sparse AND EE ring shows no FBP112-footprint tick≤2050 `eeSeq` through end of tick 2050, per-flush logs contain none | nothing due ever entered the stream for this Present |
| Controls | Positive: same-stream Mac broad replay — S1 broad AND G broad with attribution complete (calibrates footprint + attribution plumbing). Negative: draw-free tick — no FBP112 `eeSeq`s, S1+G sparse. Same-binary ON/OFF: OFF census == pre-change baseline AND ON frame hash == OFF (nonperturbation gate) | calibrate the census, not the split |
| OTHER | descriptor mismatch (11 fields), `selected_capture_status != 2`, map/decode error, any active 101–249, timestamp/query rows (§4), 8-word subsets, later-tick snapshots, any extra flush/submit/wait variant, footprint/count contradiction | no award |

(ii) vs (iii) differ observably (footprint `eeSeq`s present-but-post-`V_pre`
vs absent from all logs); (i) vs (ii) differ by flush side of `V_pre` plus G
broad vs sparse. No two hypotheses share a prediction. Per the brief, this
supports predeclaring **A, conditional** on §6 (implementation as specified,
Mac calibration passing, same-binary ON/OFF control passing). If any
condition fails, the predeclare falls to B with the narrowest next step in
§6.

## 4. Clock-4 survey: no per-draw completion method exists in-tree

| Method in pinned source | Site | Why it cannot bind a *particular* draw's completion to the S1 copy |
| --- | --- | --- |
| `write_timestamp` in-cmd pair | `Granite/vulkan/command_buffer.hpp:840`, passthrough `query_pool.hpp:141`, polled `gs_renderer.cpp:1244-1254`, gated `:1263-1266` | Measures copy-execution *time*, not which draws completed; identical prediction in all three cases (M8 Q1, retained). Turnip support unproven: `VK_QUERY_TYPE_TIMESTAMP` gated only on `timestampComputeAndGraphics`, `timestampValidBits` explicitly ignored (`query_pool.cpp:332`) |
| Calibrated host intervals | `write_calibrated_timestamp` (`device.hpp:528`, used `gs_renderer.cpp:1052-1068,1121-1125`), `wait_timeline` (`:1052-1068`) | EE/host wall clock, not a GPU write due-date (same error as `post_tick==2050`, N8D7M7 §3 T4) |
| Timeline semaphores | signaled per flush at `gs_renderer.cpp:1197-1208`; `query_timeline` reads host counter (`:1082-1087`) or `vkGetSemaphoreCounterValue` (`:1070-1080`) | Per-flush submission progress; `wait_timeline` is whole-device/per-flush, and waiting mid-Present would stall (intervention) |
| `VkFence` per submit | `device->submit(cmd, fence)` (`device.hpp:301-302`); `FenceHolder::wait/wait_timeout` (`fence.hpp`) | API exists but `flush_submit` never requests one; signal-only + poll-after-`wait_idle` adds nothing over `wait_idle` (`device.hpp:274`); still per-submit (many draws), and submits fan out to async-transfer + generic queues (`:1149-1195`) |
| Debug labels | `insert_label` (`gs_renderer.cpp:44-50`), consumed only if `consumes_debug_markers()` (`device.hpp:518`) | Record-time annotations, no timing semantics (M8 M) |
| RenderDoc capture | `device.hpp:277-282` | Offline tool, not a live witness |
| GPU-side per-draw audit | no site (gap M3: no GPU analogue of `WriteVramUnlocked` on this path) | Would rewrite the draw shaders = intervention (M8 P, rejected) |

**Survey conclusion: no source-grounded query/fence/timeline method binds a
particular draw's GPU completion to the S1 copy.** Clock 4 is therefore
separated by construction: the (i)/(ii)/(iii) split rests on command-stream
order (clocks 1–3) plus the in-order-execution ground (B9), and claims
nothing about per-draw completion timestamps. Host submission is never
treated as GPU completion; post-`wait_idle` mapping is whole-device
completion by construction (B11). No Turnip, shader, barrier, or driver
cause is declared from static code.

## 5. Proposed hook diffs (pseudocode only — no source was edited)

H1 — enqueue identity (`gs_frontend.cpp`, near `:931-939`):
```
if (m_worker && !t_inGsWorker) {
    if (!data || sizeBytes < 16) return;
    GsCommand cmd;
    cmd.kind = GsCmdKind::GifPacket;
    cmd.bytes.assign(data, data + sizeBytes);
    if (witnessEnabled()) {                       // default-OFF env gate
        cmd.eeTick = privRegs->vsyncTick.load(acquire);
        cmd.eeSeq  = eeEnqueueCount.fetch_add(1, relaxed);
        eeRing.push({cmd.eeSeq, cmd.eeTick, sizeBytes});   // lock-free, drop-counted
    }
    m_worker->enqueue(std::move(cmd));
    return;
}
```

H2 — virtual + backend passthrough (`gs_backend.h:39-45`,
`ps2_gs_parallel_backend.cpp:897-905`):
```
// GSRasterBackend: RawGifPacket(path, data, sizeBytes,
//                               eeTick = 0, eeSeq = 0, dqIdx = 0);   // defaults = zero behavior change
// parallel override: m_iface->gif_transfer(path, data, size, PktId{eeTick, eeSeq, dqIdx});
// GSInterface::gif_transfer(path, data, size, pktId = {});          // default keeps old call sites compiling
```

H3 — dequeue join (`gs_frontend.cpp`, near `:947-956`, worker side):
```
idx = m_submitCount.fetch_add(1, relaxed); tickDQ = vsyncTick.load();
if (witnessEnabled())
    gsRing.push({cmd.eeSeq, cmd.eeTick, path, tickDQ, idx});  // (B3 join record)
m_backend->RawGifPacket(path, data, size, cmd.eeTick, cmd.eeSeq, idx);
```

H4 — record-time tag + footprint (`gs_interface.cpp`, near `:5191`,
`:3329`, `:3694`):
```
// gif_transfer entry: curPkt = pktId; prim0 = render_pass.primitive_count;
// ... existing decode ...
// drawing_kick_append: render_pass.prim[n].pkt = curPkt.eeSeq;   // +8 B/prim (bound gap G5)
// gif_transfer exit: gsRing.push({eeSeq, eeTick, path,
//                                render_pass.primitive_count - prim0, fbTouchedFBP112});
```

H5 — per-flush attribution (`page_tracker.cpp`, near `:935-961`):
```
// mark_submission_timeline(reason): value = ++timeline; ...existing...;
// if (witnessEnabled())
//     gsRing.push({value, reason, minPktInFlushedRange, maxPktInFlushedRange,
//                  flushedPktCount, minEeTick, maxEeTick});        // empty flush: count 0
```

H6 — submit log + deferred emit (`gs_renderer.cpp`, near `:1116`;
fork backend near `:601-626`):
```
// flush_submit entry: if (witnessEnabled()) gsRing.push({value, submitOrdinal++});
// post-wait_idle map region: drain eeRing + gsRing to stderr/file (off hot path)
```

Every H-row is observational when implemented as specified: no new
flush/submit/wait, no reorder (params and tags ride existing calls), no
fprintf on record/dispatch paths (rings drained post-`wait_idle`). Any
variant that printf-logs on the hot path, waits mid-Present, splits a
submit, or touches draw shaders is labeled intervention up front and is
not this witness. Same-binary ON/OFF control is required (§6).

## 6. Costs, caps, controls, and stop rules

- Default OFF behind one new env gate (unset/empty = zero behavior change;
  H2 defaults keep old call sites compiling). With the flag off, the only
  residue is cold parameter slots and one branch per packet.
- Text log ≤ 4 MiB (rings: EE ≈ 32 B/entry, GS footprint ≈ 48 B/entry,
  attribution ≈ 128 B/flush, submit ≈ 64 B/submit; drop-oldest with counters
  past the cap). Committed receipts ≤ 512 KiB (summaries + hashes only; raw
  rings stay in scratch).
- Byte costs: +16 B/queued command (B1–B2); +8 B `GSInterface` field; +8
  B/recorded prim (bound gap G5); zero GPU bytes; zero new mutexes; new
  atomics = 2 relaxed/acquire ops per EE packet + 1 ring-index op per log
  line (precedent: existing per-packet relaxed counters at backend
  `:902-904`).
- Controls (all required before any device brief): (a) Mac replay of the
  N8D7M6 stream with flag OFF reproduces baseline census/hashes; (b) flag ON
  reproduces OFF frame hash and S1 census (nonperturbation); (c) positive
  broad-stream attribution completeness; (d) draw-free-tick negative.
- Stop rules: any OFF/ON inequality, any attribution gap (footprint
  `eeSeq` with no flush home, or flushed `pktId` with no B3 join), or any
  intermediate 101–249 active voids the gate → fall back to B with the
  narrowest next design being a Mac-calibration fix, which still cannot
  prove live Odin order by itself (M8 M6).
- Narrowest next if B: Mac-only calibration of footprint proxy vs clipped
  prims (gap G6) + `render_pass.prim` bound confirmation (gap G5); states
  exactly what it cannot prove: live Odin EE/GS interleave (only an Odin
  run of this witness can show that).

## 7. Gaps (each forces OTHER until closed)

- **M1 (stream gap, inherited):** which tick≤2050 packets write selected
  addresses on the N8D7M6 stream is unproven from old-stream rows; the
  witness measures this live via footprint — Mac calibration maps replay
  ordinals to footprints but never crosses value oracles between streams.
- **M2 (threading):** Odin EE/GS interleave unconfirmed from source alone;
  converted to measurement by the B3/B8 join (not assumed).
- **M3 (audit gap):** no GPU-side per-draw/per-page write hook on the
  parallel path; accepted — the witness is host-side submit-order
  attribution, execution-grounded by in-order queue + barriers (B9).
- **M4 (query gap):** Turnip timestamp support unproven (`query_pool.cpp:332`
  ignores `timestampValidBits`); the witness uses no timestamps.
- **M5 (completion gap):** no per-draw completion attribution without an
  intervention or device extension (§4 survey: no such method identified);
  separated as clock 4, outside the (i)/(ii)/(iii) scope.
- **G5 (new, array bound):** `render_pass.prim[]` capacity unconfirmed from
  the read sites (`:3329`, `:3694`); the implementer confirms the bound for
  the +8 B/prim cost before sizing.
- **G6 (new, footprint residual):** fully-clipped FBP112 prims would read as
  relevant-but-invisible (`fbTouch` uses the `:3673-3679` bbox path, which
  fires on expansion, not on clip-out); Mac calibration bounds it, cannot
  remove it.
- **G7 (path at enqueue):** `m_curGifPath` is worker-owned; EE-side path is
  not read (would race) — path joins at dequeue via FIFO `NoteGifPath`
  (`gs_frontend.h:144-145`).
- **G8 (ABI):** `GsCommand` gains two POD u64 fields through existing move
  semantics (`gs_worker.h:112-118` deque transport); fork-internal type, no
  external ABI.

## 8. Recommended next action

Gate this design; if the conditional A is accepted, authorize implementation
exactly as §5 (observational only) followed by the §6 Mac calibration +
same-binary ON/OFF control before any Odin brief. Do not cut a device brief
from this paper design alone, and do not add timestamps, extra submits, or
shader audits to the witness. No push from this worker.

## 9. Receipts / commands (all read-only, repo root unless noted)

Reads: this brief; `~/dev/AGENTS.md`; repo `AGENTS.md`;
`local/AGENTS.local.md`; N8D7M6 `REPORT.md` + `ORCH-GATE.md`; N8D7M7
`REPORT.md` + `ORCH-GATE.md` (+ `check.py` for T4/W/D rejections); N8D7M8
`REPORT.md` + `ORCH-GATE.md` (+ `check.py` for L1–L7 loss points);
`docs/todo.md` (N8D7M9 row). Sources (direct reads): fork
`gs_frontend.cpp:100-279,700-829,920-1079,1118-1140`
(`processGIFPacket`, `executeQueuedCommand`, `drainQueue`, Present path,
`buildPresentationRequestUnlocked`),
`ps2_gs_parallel_backend.cpp:430-549,590-749,880-944`
(`Present`, selected/oracle decode, `RawGifPacket`),
`include/runtime/gs/gs_worker.h` (queue caps, `GsCommand`, `enqueue`),
`include/runtime/gs/gs_frontend.h:144-145` (`NoteGifPath`),
`include/runtime/gs/gs_types.h:275-295` (`GSPresentationRequest`),
`include/runtime/gs/gs_backend.h:36-48` (virtual decls); parallel
`gs_interface.cpp:3329-3700` (draw recording), `:5140-5165` (`flush`),
`:5191-5290` (`gif_transfer`), `:5527-5586` (`vsync`),
`gs_interface.hpp:130-329` (decls incl. `gif_transfer :269`,
`query_timeline :319`), `gs_renderer.cpp:40-84,879-943,1045-1279`
(labels, pressure cuts, `wait_timeline`, `query_timeline`,
`flush_submit`), `:4760-4889,5054-5080,5345-5360` (descriptor, S1 copy,
circuit copy, `flush_submit(0)`), `page_tracker.cpp:935-975`
(`mark_submission_timeline`), `page_tracker.hpp:118-209` (`FlushReason`,
tracker decl); Granite `vulkan/device.hpp:265-364,518-530`
(`wait_idle`, submit API, markers, calibrated timestamps),
`vulkan/command_buffer.hpp:840` (`write_timestamp`),
`vulkan/query_pool.hpp:133-153` + `query_pool.cpp:324-336` (timestamp
gating), `vulkan/fence.hpp` (`FenceHolder`). `git rev-parse` in both
worktrees for pins. New text < 512 KiB (see `check-result.json`).
