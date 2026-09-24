# N8D7M9 — live identity-carrying witness design (read-only source design)

**State: design COMPLETE, verdict B (corrected 2026-09-24 per orchestrator
gate: the v1 conditional-A attribution claim is withdrawn as unsound).
Read-only: no source edit, build, replay, boot, device action, lease, push,
board/global edit, or upstream contact. No Turnip/shader/barrier/driver
cause is claimed. The orchestrator gates. Cited source strings cannot prove execution; the
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
| B6 | GIF decode → draw recording (candidate draws only) | parallel `gs_interface.cpp:5191+` (`gif_transfer(path, data, size)`), optimized handler `:5234-5241`, `drawing_kick_append` at `:3329`, prim append `render_pass.prim[primitive_count]` at `:3694` | Carriable: `GSInterface` field `curPkt` set at `gif_transfer` entry; each recorded prim stores its `pktId` (+8 B/prim; array bound unconfirmed — gap G5). Per-`gif_transfer` footprint log: `(eeSeq, eeTick, path, primDelta, fbTouch)` where `primDelta` = `primitive_count` exit−entry and `fbTouch` = whether `tracker.mark_fb_write` fired (`:3673-3679` bbox-expand path) with FBP112 ctx. **Limit (correction M8): the footprint is a candidate draw, not proof of an executed VRAM write** — GIF IMAGE-mode transfers, qword/VRAM clears (separate `clear_cmd` submit path, `gs_renderer.cpp:1158-1167`), host map writes, and fully-clipped prims never pass through (or never land from) the tagged prim path | +8 B `GSInterface` field; +8 B/recorded prim; footprint line ≈ 48 B text per packet into the GS ring (deferred emit, never fprintf on the hot path) |
| B7 | Internal pressure/hazard cuts — CORRECTION: unattributed | `flush_if_memory_pressure()` calls `flush_render_pass(PressureFlush)` **directly** (parallel `page_tracker.cpp:970-977`), with **no** `mark_submission_timeline` and no new timeline value; direct `flush_render_pass` calls (Overflow at `gs_interface.cpp:1622`, TextureHazard `:1739,1747`, FBPointer `:1815`, CopyHazard `page_tracker.cpp:231,344,629`, Overflow `:3817`) likewise bypass the timeline. Fired from the record path (`handle_tex0_write` at `gs_interface.cpp:1626-1629`, draw path at `:3820`). Cut-flushed prims sit in command buffers and are stamped with the *next* `mark_submission_timeline` value — misattributed later than their flush | Attribution by timeline value is unsound for cut work (correction M7). No new log can fix this at the `mark_submission_timeline` site alone |
| B8 | Per-flush attribution — PARTIAL: sound only for `mark_submission_timeline` flushes; withdrawn as a three-way discriminator | parallel `page_tracker.cpp:935-961` (`mark_submission_timeline`: `++timeline`, `flush_render_pass(reason)`, returns value); reasons enum `page_tracker.hpp:122-134`; `GSInterface::flush` at `gs_interface.cpp:5153-5165` (`flush_pending_transfer` + `mark_submission_timeline` + `flush_submit(value)` at `:5161-5162`) | Carriable: at each `mark_submission_timeline`, one attribution line `(timelineValue, reason, eeSeqLo, eeSeqHi, pktCount, eeTickLo, eeTickHi)` for the flushed render-pass range. **Withdrawn as discriminator (corrections M7, M9):** (a) B7 cuts flush work with no timeline value, so stamped values misorder cut work; (b) min/max `eeSeq` ranges overstate membership — a range cannot say which packets a flush held, and exact per-flush sets are unbounded. Present-entry flush (backend `:452` `m_iface->flush()`) still yields a `V_pre` marker, and a post-`V_pre` tagged packet was submitted after the copy — but absence of a tag cannot prove relevant writes absent (M8) | ≈ 128 B text per flush; flushes/vsync O(10s); no GPU bytes; no new lock |
| B9 | Scanout cmd: descriptor + S1 copy | parallel `gs_renderer.cpp:4779-4792` (descriptor latch), `:4806-4820` (staging alloc + barrier `:4813-4815` + `copy_buffer` `:4816-4817` + barrier `:4818-4819`, guarded `:4793-4804`) | No change (the *original* copy is witnessed, never moved). Ordering ground: same-`direct_cmd` record order + in-order queue + barriers ⟹ draws submitted pre-S1 execute pre-S1 | zero |
| B10 | Circuit sample + readback + submit | `gs_renderer.cpp:4834` (`sample_crtc_circuit` after S1), `:5054-5077` (circuit1 → staging, `selected_capture_status=2` at `:5076`), `:5354` (`flush_submit(0)`); `flush_submit` body `:1116-1226`, timeline signal `:1197-1208` | No change. `flush_submit(value)` submission order = record order; per-submit completion stays unattributed (§4). Log: `(timelineValue → submitOrdinal)` one line at `flush_submit` entry — text only | ≈ 64 B text per submit |
| B11 | Ordered completion + host map | fork backend `:601-602` (`submit(cmd)` + `wait_idle()`, decl `Granite/vulkan/device.hpp:274`); map + decode `:621-729` (`map_host_buffer`, `selectedDecode`, oracle census, SHAs, `oracle_input_equal`) | No change. Rings drained to the text log here (post-`wait_idle`, off the hot path). Full 448-tile census decoded from mapped bytes exactly as today | log ≤ 4 MiB text total (cap §6); committed receipts ≤ 512 KiB (summaries only) |

Threading note (O-window hypothesis, N8D7M7 §2 row 15 / N8D7M8 §2 row 17):
`RawGifPacket` (`:897-905`) takes no `m_backendLifetimeMutex`, while
Present's `Flush/Sync/Present` runs under it (`gs_frontend.cpp:804-812`).
The witness does not assume whether EE recording interleaves the Present
window on Odin — the B3 join logs record order per packet, and B8 logs
submit order for `mark_submission_timeline` flushes only (cut work excluded
per M7). Gap M2 is thus narrowed to measurement of the covered subset, not
closed.

## 3. Prediction table — corrected to B (no three-way discriminator)

`V_pre` = timeline value of the Present-entry flush (backend `:452` →
`gs_interface.cpp:5161`). The v1 design claimed per-flush attribution gives
unique (i)/(ii)/(iii) predictions. That claim is withdrawn for three
independent reasons (orchestrator gate 2026-09-24, verified against the
pinned source):

- **M7 — cut misattribution:** B7 pressure/hazard cuts flush render-pass
  work with no timeline value; the next `mark_submission_timeline` stamps
  cut work late. Stamped side of `V_pre` is therefore not a sound
  submitted-before/after-S1 signal for cut work.
- **M8 — footprint is candidate-only:** FBP112 bbox/prim footprint (B6) is
  not proof of an executed VRAM write. GIF IMAGE-mode transfers, VRAM
  clears (separate `clear_cmd` path), host map writes, and clipped prims
  bypass the tagged prim path entirely — in both directions (tagged prims
  that never land; landed writes with no tag).
- **M9 — range membership loss and absent-tag asymmetry:** min/max `eeSeq`
  ranges per flush overstate membership (a range cannot say which packets a
  flush held; exact sets are unbounded). A post-`V_pre` tagged packet was
  submitted after the copy, but **absence of a tag cannot prove relevant
  writes absent** from the original Present (M8 paths leave no tag).

| Case | Required unique observable (original Present order, full 448 census) | What the source actually offers | Met? |
| --- | --- | --- | --- |
| (i) relevant source before copy, sparse copy | S1 sparse AND G broad AND the relevant draws provably submitted pre-S1 | G broad + S1 sparse still implicates the copy path *as a shape*, but WHICH draws were pre-S1 is unsound under M7 (cut work mislabeled) and relevance itself is candidate-only (M8) | **No: partial shape only** |
| (ii) relevant writes after copy | S1 sparse AND G sparse AND relevant writes provably first submitted post-S1 | A post-`V_pre` tagged packet is a sound late instance, but the class "all relevant writes are late" is unprovable: untagged late paths (M8) and M7 misordering defeat the universal claim | **No** |
| (iii) relevant writes absent | S1 sparse AND G sparse AND proof no relevant write entered this Present | Absence of tags proves nothing (M8/M9): transfers, clears, and clipped prims leave no tag. Identical observable to (ii)-via-untagged-paths | **No: identical to (ii) in the untagged case** |
| Controls | Positive (Mac broad replay) + negative (draw-free tick) + same-binary ON/OFF | Calibrate census/plumbing only; cannot rescue the (ii)/(iii) split | Do not rescue A |
| OTHER | descriptor mismatch (11 fields), `selected_capture_status != 2`, map/decode error, any active 101–249, timestamp/query rows (§4), 8-word subsets, later-tick snapshots, any extra flush/submit/wait variant, footprint/count contradiction, any M7/M8/M9-shaped pattern | no award | — |

**Verdict: B.** Identity (`eeSeq`/`eeTick`) can be carried from EE enqueue
through the queue, `RawGifPacket`, `gif_transfer`, and draw recording
(B1–B6: a useful bounded design for record/submit-order logging), but
per-draw write/completion attribution and the original-Present cause are
unresolved: M7 breaks submit-side ordering soundness, M8 breaks
record-side relevance soundness, M9 breaks set-membership soundness, and
§4 shows no per-draw completion method. Per the brief, equal/unsound
predictions → B, not A. No implementation or Odin run is authorized from
this design.

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
`:3329`, `:3694`) — CANDIDATE-ONLY (M8):
```
// gif_transfer entry: curPkt = pktId; prim0 = render_pass.primitive_count;
// ... existing decode ...
// drawing_kick_append: render_pass.prim[n].pkt = curPkt.eeSeq;   // +8 B/prim (bound gap G5)
// gif_transfer exit: gsRing.push({eeSeq, eeTick, path,
//                                render_pass.primitive_count - prim0, fbTouchedFBP112});
// NOTE: tags candidate draws only. IMAGE transfers, clears, host writes and
// clipped prims bypass this path — absence of a tag proves nothing.
```

H5 — per-flush attribution (`page_tracker.cpp`, near `:935-961`) —
WITHDRAWN as discriminator (M7, M9):
```
// mark_submission_timeline(reason): value = ++timeline; ...existing...;
// if (witnessEnabled())
//     gsRing.push({value, reason, minPktInFlushedRange, maxPktInFlushedRange,
//                  flushedPktCount, minEeTick, maxEeTick});        // empty flush: count 0
// UNSOUND: cut-flushed work (B7) is stamped late; ranges overstate membership.
// Retained only as V_pre marker + submit-order log for mark_submission_timeline
// flushes, never as (ii)/(iii) evidence.
```

H6 — submit log + deferred emit (`gs_renderer.cpp`, near `:1116`;
fork backend near `:601-626`):
```
// flush_submit entry: if (witnessEnabled()) gsRing.push({value, submitOrdinal++});
// post-wait_idle map region: drain eeRing + gsRing to stderr/file (off hot path)
```

Every H-row is observational when implemented as specified: no new
flush/submit/wait, no reorder (params and tags ride existing calls), no
fprintf on record/dispatch paths (rings drained post-`wait_idle`). H1–H3
carry identity to record; H4 tags candidate draws; H5 is retained only as a
`V_pre`/submit-order marker, not as attribution evidence. Any variant that
printf-logs on the hot path, waits mid-Present, splits a submit, or touches
draw shaders is labeled intervention up front and is not this witness. No
implementation is authorized from this B design (§8).

## 6. Costs, caps, controls, and stop rules (design-only; no run authorized)

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
- Controls (design-only, not authorized): (a) Mac replay of the N8D7M6
  stream with flag OFF reproduces baseline census/hashes; (b) flag ON
  reproduces OFF frame hash and S1 census (nonperturbation); (c) positive
  broad-stream plumbing check; (d) draw-free-tick negative. None of these
  can rescue the (ii)/(iii) split (§3 M7/M8/M9).
- Stop rules: any OFF/ON inequality, any attribution gap (footprint
  `eeSeq` with no flush home, or flushed `pktId` with no B3 join), or any
  intermediate 101–249 active voids any future gate → stays B.
- Narrowest next (read-only, no build/run): analysis of the non-prim write
  paths that bypass tags — GIF IMAGE-mode transfers, qword/VRAM clears
  (`clear_cmd` at `gs_renderer.cpp:1158-1167`), host map writes — asking
  whether any record-order tag can cover them without reordering; states
  exactly what it cannot prove: per-draw write/completion attribution and
  the original-Present cause (only a sound witness, not yet designed, plus
  an Odin run could show that).

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
- **M7 (cut-misattribution gap, gate correction):**
  `flush_if_memory_pressure()` (`page_tracker.cpp:970-977`) and direct
  `flush_render_pass` calls (Overflow `gs_interface.cpp:1622`,
  TextureHazard `:1739,1747`, FBPointer `:1815`, CopyHazard
  `page_tracker.cpp:231,344,629`, Overflow `gs_interface.cpp:3817`) flush
  render-pass work with no timeline value; the next
  `mark_submission_timeline` stamps it late. Timeline-side-of-`V_pre` is
  unsound evidence for cut work.
- **M8 (candidate-footprint gap, gate correction):** FBP112 bbox/prim
  footprint is a candidate draw, not an executed VRAM write. GIF
  IMAGE-mode transfers, qword/VRAM clears (`clear_cmd`,
  `gs_renderer.cpp:1158-1167`), host map writes, and clipped prims bypass
  the tagged prim path in both directions; absence of a tag cannot prove
  relevant writes absent.
- **M9 (membership gap, gate correction):** min/max `eeSeq` ranges per
  flush overstate membership; exact per-flush sets are unbounded. Ranges
  are retained at most as `V_pre`-side hints, never as (ii)/(iii)
  evidence.
- **G5 (new, array bound):** `render_pass.prim[]` capacity unconfirmed from
  the read sites (`:3329`, `:3694`); the implementer confirms the bound for
  the +8 B/prim cost before sizing.
- **G6 (subsumed by M8):** fully-clipped FBP112 prims read as
  relevant-but-invisible (`fbTouch` uses the `:3673-3679` bbox path, which
  fires on expansion, not on clip-out); one instance of the candidate-only
  footprint limit, kept here as the concrete example.
- **G7 (path at enqueue):** `m_curGifPath` is worker-owned; EE-side path is
  not read (would race) — path joins at dequeue via FIFO `NoteGifPath`
  (`gs_frontend.h:144-145`).
- **G8 (ABI):** `GsCommand` gains two POD u64 fields through existing move
  semantics (`gs_worker.h:112-118` deque transport); fork-internal type, no
  external ABI.

## 8. Recommended next action

Gate this design as **B**. No implementation, Mac experiment, or Odin brief
is authorized from it: identity to record/submit (H1–H3, candidate tags H4)
is a useful bounded design, but per-draw write/completion attribution and
the original-Present cause are unresolved (M7/M8/M9, §4). Do not add
timestamps, extra submits, or shader audits to the witness. Narrowest next
is the §6 read-only non-prim-path analysis. No push from this worker.

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
