# N8D7M12 Part 5F3 — GPU readback source coverage + pre-submit packet fingerprint design (no run)

**State: COMPLETE, outcome A (source map and discriminating design complete).
Read-only: no build, replay, boot, device/lease action, source/fork change,
fetch, push, board/global edit, or upstream contact. LSP `goToDefinition` and
`hover` returned no results (no language server for this C++ tree); all edges
below are verified by exact line reads. No root-cause verdict; the
orchestrator decides.**

Brief: `local/muse/prompts/N8D7M12P5F3.md`. Prior reports/gates read in full:
N8D7M12 Part 5F2 REPORT + ORCH-GATE, Part 5F1 REPORT + ORCH-GATE (correction),
N8D7H REPORT §§1–2 + ORCH-GATE, Part 5E2 REPORT + ORCH-GATE, Part 1 (N8D7M12)
REPORT. `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md` read.

Context (5E2 §4 / 5F2 §2c): same APK (`caa11102…f512`), stream
(`f6a78f71…a593`), env, backend OFF1/OFF2 — 41 ordered ticks; priv 41/41;
vram 16/41; present 25/41; first difference tick850. `priv` proves only
sampled CPU-mirror equality (5F1 correction), not packet order.

## 1. Provenance table (handback)

Double-hash = `sha256sum` + `shasum -a 256` (both match). Rev =
`git -C <tree> rev-parse HEAD`. Dirty = `status --short`.

| File | Pinned SHA-256 (N8D7H §1) | Read 1 | Read 2 | Rev | Tree state |
| --- | --- | --- | --- | --- | --- |
| `gs/gs_renderer.cpp` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` | MATCH | MATCH | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` | DIRTY (`M gs/gs_renderer.cpp`) |
| `gs/gs_interface.hpp` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` | MATCH | MATCH | same `3a66c19` | DIRTY (`M gs/gs_interface.hpp`) |
| `gs/gs_renderer.hpp` | `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` | MATCH | MATCH | same `3a66c19` | DIRTY (`M gs/gs_renderer.hpp`) |
| Fork backend (APK-tied context, N8D7H §1/F2 §1) | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` at `~/dev/ssx3-work/N8D7F/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | MATCH (`sha256sum`) | not re-read (F2 double-read) | N/A (overlay source) | — |

Working tree: `~/dev/ssx3-work/N8D7F/parallel-gs`. All paths in §2 tables are
under it unless marked `P2:` (= `~/dev/ssx3-work/N8D7M12P2/PS2Recomp` @
`a608ed1e161f60334a0cf3a80d1af3e54b692bd2`, `status --short` empty, verified
this part). HEAD blobs of the three files differ from pins (`193111de…`,
`b74f5d22…`, `4066826a…` per `git show HEAD:… | shasum`); `git hash-object`
gives `1812a3e5…`/`acd96122…`/`247d5ef1…` (working-tree bytes uncommitted) —
same refinement as F2 §1. Backend citations in §2 use the `c613…` N8D7F file
(APK-tied per N8D7H/F2); the P2 worktree's committed backend blob is
`84a13a80…` (≠ pin), so backend line numbers are NOT taken from the P2 tree.

Additional files read (SHA-pinned here, **unpinned to APK** — informative
only, never built behavior):

| File | SHA-256 (this part) | Status |
| --- | --- | --- |
| `gs/gs_interface.cpp` | `5ccc962f080bbb1e1fc637155799823008409f2fd3b283d1f2f0e9d6eb5077f4` | unpinned to APK (dirty `M`) |
| `gs/page_tracker.cpp` | `96edd79a27a48e0a5dc84d130aea3da4c09f3111d9df65ee1986243ff4893fd1` | unpinned to APK |
| `gs/page_tracker.hpp` | `5e66cd51007c22874ffcdde948a7e37bfb455bc73aa4d8d48ae7ccb129ede349` | unpinned to APK |
| `Granite/vulkan/device.cpp` | `df8c3d69850ae4ea12f0203df19b5692f38ecee22861d38bdd6fffb5b7807163` | unpinned to APK (Granite `m`, dirty: `M vulkan/memory_allocator.cpp`, `M vulkan/command_buffer.cpp`, …) |
| `Granite/vulkan/device.hpp` | `62d06627a04c2116b574863053926fa7a2547b4d0502e4429d9efa7a12ea712a` | unpinned to APK |
| `Granite/vulkan/memory_allocator.cpp` | `efb09a5d5fbf01a7986344ec342c2bddc4afcee2c7c6bcc562ae6717b75c07e7` | unpinned to APK (dirty `M`) |
| `Granite/vulkan/buffer.hpp` | `1bf6abaf9b2ce6d77be8c95f16f3addbaaf77acf4f1fec3b0861ea42d4574a1e` | unpinned to APK |
| Granite rev | `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5` (submodule, dirty per above) | unpinned to APK |
| P2 `ps2xRuntime/src/lib/gs/gs_replay_core.cpp` | `c5fdaf64ee065ba43e054eff821887aa9db980abf2367e7e6a227ccdbfda396c` | fork-rev-pinned (`a608ed1`); APK tie by P3 overlay receipt only |
| P2 `ps2xRuntime/src/lib/gs/gs_frontend.cpp` | `f6972433d6cbe4a246bb02d40c6642bc73f78bcc3e2b378d2352fca063dc1808` | fork-rev-pinned; APK tie by receipt only |
| P2 `ps2xRuntime/include/runtime/gs/gs_frontend.h` | `a9798a0198cda86ae9c1a88ee6e947e38368d5418dd0f637c5c30fe5d0195451` | fork-rev-pinned; APK tie by receipt only |
| P2 `ps2xRuntime/src/lib/gs/gs_worker.cpp` | `3300f41deae93b7b6cb2ec4929d9f93c24171ee0f619f8057422906803538341` | fork-rev-pinned; APK tie by receipt only |
| P2 `ps2xRuntime/include/runtime/gs/gs_worker.h` | `e874fe818c903e1e8e57df0b1ca82873549ee45dcbc0f5414e6db8df96e26d8f` | fork-rev-pinned; APK tie by receipt only |

## 2. Readback coverage: call/writer/reader table

Legend: **[P]** = pinned APK-tied bytes; **[U]** = unpinned, informative only;
**(unproved)** = driver/Turnip behavior outside all pins.

### 2a. Reader path (`SnapshotVram` / `map_vram_read(0,4MiB)`)

| # | Edge | Citation |
| --- | --- | --- |
| R1 | Backend `SnapshotVram`: `flush()` + `map_vram_read(0,4MiB)` + memcpy; **no `wait_idle` of its own** | **[P]** N8D7F backend `:729-748` |
| R2 | `map_vram_read(offset,size)`: full-mask `PageRect` over the range; `get_host_read_timeline`; if `UINT64_MAX` → `mark_submission_timeline(HostAccess)` + `flush_submit`; then `wait_timeline(host_read_timeline)`; return `begin_host_vram_access()+offset`. No invalidate call at this layer | **[U]** `gs/gs_interface.cpp:5126-5151` |
| R3 | `begin_host_vram_access` = `device->map_host_buffer(*buffers.cpu, READ_WRITE)`; write close = `unmap(WRITE)` | **[P]** `gs/gs_renderer.cpp:1513-1525` |
| R4 | Granite `map_host_buffer` → `DeviceAllocator::map_memory`: `vkInvalidateMappedMemoryRanges` **only if** READ access **and** memory type lacks `HOST_COHERENT_BIT` (`:480-506`); `unmap` flushes only if WRITE and non-coherent (`:508-530`) | **[U]** `Granite/vulkan/device.cpp:346-368`, `Granite/vulkan/memory_allocator.cpp:480-530` |
| R5 | `CachedHost` allocation priority prefers `HOST_VISIBLE\|HOST_CACHED` **without requiring** `HOST_COHERENT_BIT` (`:3194-3198`); whether Turnip-on-Adreno returns coherent memory for it is **(unproved)** — so the R4 invalidate is conditional, not unconditional | **[U]** `Granite/vulkan/device.cpp:3194-3198` |
| R6 | `flush()` (map path's pre-step): `flush_pending_transfer` + `mark_submission_timeline` + `flush_submit`; waits only if `deterministic_timeline_query` (defaults false, hpp `:137-143`) | **[U]** `gs/gs_interface.cpp:5153-5165`; **[P]** `gs/gs_interface.hpp:137-143` |
| R7 | `wait_timeline(value)` waits on the CPU `timeline_value` advanced by the `PGS-Waiter` thread via `wait_timeline` on the Vulkan timeline semaphore — a driver-observed value | **[P]** `gs/gs_renderer.cpp:1052-1068,756-784` |
| R8 | `flush_submit(value)`: submits async/clear/setup/heuristic/binning/direct buffers; `value==0` takes no wait branch; nonzero signals timeline semaphores | **[P]** `gs/gs_renderer.cpp:1116-1208` |

### 2b. Reader path (`Present` scanout staging)

| # | Edge | Citation |
| --- | --- | --- |
| P1 | Backend `Present`: `syncPriv` → flag gating → `m_iface->flush()` → `m_iface->vsync()` → readback copy + barrier + `submit` + **`wait_idle`** → (2050-only blocks) → map + 640-stride pack | **[P]** N8D7F backend `:363-385` (entry/flush/vsync), `:524-534` (staging + `wait_idle`), `:681-691` (pack) |
| P2 | Scanout-image→host staging copy (`512×224×4`, `CachedHost`) recorded in-scanout, gated on `capture_selected_input && selected_vram_staging`; full-VRAM (`4MiB`, `CachedHost`) staging copy gated on `capture_selected_input`; `pre_deinterlace_merged` retention gated on `capture_scanout_stages` | **[P]** `gs/gs_renderer.cpp:4806-4817`, `:5054-5077`, `:5314-5315`; gates at `:4759,4983` |
| P3 | Backend maps `rb` (`:652-653`), selected/circuit/stage buffers (`:553-558`, `:605-606`, `:626-627`) with `MEMORY_ACCESS_READ_BIT` after `wait_idle` (`:534`); R4/R5 conditional-invalidate applies to every one of these maps | **[P]** N8D7F backend `:534,553-558,605-627,652-656` |
| P4 | Pinned `GSRenderer::vsync` ends with `flush_submit(0)` and **no wait** (`:5354`); `vsync` assumes pending ops flushed (`:4396-4405`); the only `wait_idle` in the pinned renderer file is in `invalidate_super_sampling_state`, off the scanout path (`:315-342`) | **[P]** `gs/gs_renderer.cpp:4396-4405,5354,315-342` |
| P5 | `GSInterface::vsync` wrapper (incl. G31 log-only probe with its own `map_vram_read` AFTER the vsync submission) | **[U]** `gs/gs_interface.cpp:5540-5556,5576-5578,5580-5643` |

### 2c. GPU writer classes in the bounded path (marks tracker?)

| Writer | Mark call (this tree) | Citation | Reader-side wait/invalidate |
| --- | --- | --- | --- |
| W1 host→VRAM transfer write (upload path: `acquire_host_write` → `begin_host_vram_access` memcpy → `commit_host_write` → `mark_transfer_write`) | `mark_transfer_write` sets `need_host_write/read_timeline_mask`, `copy_write_block_mask` | **[U]** `gs/gs_interface.cpp:3918,3969,4002,4007`; `page_tracker.cpp:621-673` | `map_vram_write` pre-waits `get_host_write_timeline` (`:5085-5104` **[U]**); read path R2 |
| W2 VRAM→VRAM transfer copy (`mark_transfer_copy`, hazard flushes) | sets readback/copy-page registrations | **[U]** `gs/gs_interface.cpp:4075`; `page_tracker.cpp:221-326` | `flush_copy`/`flush_render_pass` on hazard **[U]** |
| W3 render-pass store (FB write, incl. depth `mark_fb_read`) | `mark_fb_write` sets `fb_write_mask`, `need_host_*_mask`, `MAY_SUPER_SAMPLE`; `mark_fb_read` sets `fb_read_mask` | **[U]** `gs/gs_interface.cpp:3674,3680,3682`; `page_tracker.cpp:155-219` | `flush_render_pass` (`gs_interface.cpp:232` **[U]**, `page_tracker.cpp:501-514` **[U]**) |
| W4 scanout ext-feedback compute write | **`tracker.mark_external_write`** — the one pinned tracker-marking call site; body sets `need_host_read/write_timeline_mask` + texture invalidation | **[P]** call `gs/gs_renderer.cpp:5282-5285`; **[U]** body `page_tracker.cpp:122-145` | R2 via `need_host_read_timeline_mask` |
| W5 promotion (`promote_render_pass_to_backbuffer`, `copy_cached_texture`) | registration gated on `hacks.backbuffer_promotion` (`:5645-5651`); defaults false (`Hacks`, hpp `:212-232`); `set_hacks` never called (5F1 edge 17 receipt); invalidation on transfer write (`:4015,4078`) | **[U]** `gs/gs_interface.cpp:5364-5524,5645-5651,4015,4078`; **[P]** defaults `gs/gs_interface.hpp:212-232` | statically off for OFF runs (source-text consequence, not APK proof) |
| W6 `LOCAL_TO_HOST` fifo readback consumer | reads via `get_host_read_timeline` + `wait_timeline` + `begin_host_vram_access`; zero-fills if `unsynced_readbacks` (default false) | **[U]** `gs/gs_interface.cpp:4090-4126` | wait at `:4124` **[U]** |
| W7 qword clears (`clear_cmd` dispatch) | no `mark_*` call observed adjacent in the bounded path — **not asserted as a bypass** (brief rule; tracker coverage of clears is unmapped here) | **[P]** dispatch `gs/gs_renderer.cpp:1089-1106` | — |
| Copy-out primitives (`copy_blocks` gpu→cpu in `flush_readback` / host→gpu in `flush_host_vram_copy`) | reader-side barriers `COPY→…HOST_READ` (`:1732-1734`) | **[P]** `gs/gs_renderer.cpp:1527-1546,1548-1589,1709-1738` | barrier, not a tracker mark |

Stale-data reading for the orchestrator (not a verdict): the map path's
correctness rests on (a) tracker `need_host_*` coverage whose bodies are all
**[U]**, (b) the conditional Granite invalidate R4/R5 (**[U]** + dirty
Granite + **(unproved)** Turnip memory type), and (c) the driver-observed
timeline R7. No writer bypass is proved — W7 is unmapped, not a finding — so
an observed GPU-hash difference may reflect genuinely different GPU memory
contents just as readily as stale host-visible data. The §3 fingerprint is
still required to separate H1 from H2.

## 3. Pre-submit packet-sequence fingerprint site

### 3a. Correction (gate): parse-time accumulation is invalid

The v1 design accumulated FNV in `gs_replay_core` while parsing the fixed
stream. A fixed stream yields an identical parse-time digest in every run
even if queued commands execute in a different order, so its §3c H1/H2
predictions were invalid. The fingerprint MUST be accumulated at worker
command consumption (or backend `RawGifPacket` entry). What follows replaces
the v1 site; the v1 field list is kept only as the record-shape reference.

### 3b. Site: running digest at worker consumption, snapshotted at Fence

Single consumer, strict FIFO: `GsWorker::threadMain` pops the queue front
and runs the handler (`gs_worker.cpp:112-115,118`), documented as
"commands execute strictly FIFO on the worker thread" (`gs_worker.h:12-16`).
Accumulate a running FNV-1a-32 inside `GS::executeQueuedCommand` (P2
`gs_frontend.cpp:192-195`), i.e. at actual consumption, mixing a kind tag
plus these per-kind fields:

| Consumed command | Case site (P2, fork-rev-pinned) | Fields mixed (consumption order) |
| --- | --- | --- |
| `GifPacket` | `gs_frontend.cpp:197-199` → worker-branch `processGIFPacket` (`:929-939,941-956`) | kind + **consumed** `m_curGifPath` (set by prior `NoteGifPath` consumption, `:200-202`) + `cmd.bytes` |
| `NoteGifPath` | `:200-202` | kind + `pathId` |
| `RegWrite` | `:203-205` | kind + `regAddr` + `regValue` |
| `UploadImageNative` | `:206-209` | kind + `setupRegs[0..3]` + `bytes` |
| `NativePacked` | `:210-212` | kind + `bytes` |
| `ClearCtx` / `ClearActive` | `:213-219` | kind + `u32a` + `u32b` |
| `WriteVram` | `:220-223` | kind + `u32a..u32e` + `regValue` |
| `PrivWrite` | `:230-232` | kind tag ONLY — `apply` is an opaque `std::function` (`gs_worker.h:97-115`); content unhashable at consumption (gap) |
| Read-only/side RPCs (`Consume`, `ReadVram`, `RefreshSnapshot`, `DiagPresent`, …) | `:233-247,275-277` | kind tag only (no packet bytes carried) |

Sampling at a Fence without reordering: the `Fence` case (`:273-274`,
currently a no-op) travels the same FIFO, so the worker consumes it strictly
after all prior commands; snapshot the running digest into a member there.
`drainQueue` enqueues that Fence and waits (`gs_frontend.cpp:178-190`);
`GsRpcBase::signal` runs after the handler returns (`gs_worker.cpp:118-125`)
under mutex+cond (`gs_worker.h:69-89`), so the core thread reading the
snapshot after `drainQueue()` returns (replay-core kind-4 handler,
`gs_replay_core.cpp:436-444`) sees all prior consumption — no new wait, no
GPU call, no reordering introduced. Emit per sampled tick after `:443`,
before `:453`/`:459`:
`GB4_PKTSEQ tick=<t> seq=<hex> packets=<n>`.

Why this is pre-submit/readback: consumption through `RawGifPacket` →
`gif_transfer` (`[P]` backend `:759-767`; **[U]** `gs_interface.cpp:5191-5196`)
only records renderer commands; submission happens later inside the readback
path (`flush_submit` at SnapshotVram/Present). Readback RPCs
(`RefreshSnapshot`, `DiagPresent`) are consumed strictly after the Fence
snapshot (`gs_frontend.cpp:245-247,275-277`; backend `Flush`/`Sync` are
no-ops, `[P]` backend `:359-361`). Direct (non-queued) mode has no worker
and is NOT covered by this design (needs parallel updates at the direct-call
sites); OFF1/OFF2 run queued+parallel, so the pair comparison is valid.

Closest alternative (narrower): hash `(path, sizeBytes, bytes)` at backend
`RawGifPacket` entry (`[P]` backend `:759-767`), called on the worker thread
(`gs_frontend.cpp:955-956`) — consumption order, but `GifPacket` kinds only;
misses priv-writes/uploads/clears.

### 3c. Existing artifacts do NOT prove this fingerprint (verified)

| Artifact | Why insufficient (verified this part) |
| --- | --- |
| 1.1 GB stream SHA `f6a78f71…a593` | proves file bytes on disk, not consumption order through the queue/worker (`NoteGifPath` and `GifPacket` are separately enqueued commands; pairing/interleave unproved for APK) |
| `GB4_REPLAY_SUMMARY` counts (862958/11499/25445/2050) | totals only (`gs_replay_core.cpp:678-685`); equal counts are consistent with reordered consumption |
| `priv` 41/41 | sampled CPU mirrors only (`privHash`, `:84-92`; 5F1 correction) |
| `PS2X_GS_REPLAY_PACKET_TRACE` (`:238-243,405-407,568-570`) | hashes `fnv(vram.data(),…)` (CPU-side mirror, not packet bytes); gated on `tick < bisectTo`; unset in OFF runs |
| `m_submitCount` / FIFO comment | counts executions (`gs_frontend.cpp:947`); the strict-FIFO comment (`gs_worker.h:12-16`) is a code claim, not a same-device observation — this fingerprint tests it |

### 3d. Prediction table (corrected)

| Result (two same-settings runs) | Favored hypothesis | What remains unproved in each case |
| --- | --- | --- |
| Equal consumption-`seq` through tick2050 + different GPU hash at tick850 | favors **H2** (identical command stream consumed in identical order; GPU state/readback differs) | timing-only differences (Fence orders worker execution, not GPU submit timing); which readback/writer leg diverged (§2 gaps); `PrivWrite`-confined reorderings (opaque `apply`) partially mitigated by sampled `privHash` |
| Different consumption-`seq` at/before tick850 (first-divergence tick locatable per sampled row) | favors **H1** (delivery/order differs before/at the renderer) | whether the divergence arose at enqueue vs worker vs `gif_transfer`; whether the GPU difference is fully explained by it |
| Equal consumption-`seq` + equal GPU hashes | neither (run-to-run determinism on this pair; towards 5F1 mechanism C) | single pair only; says nothing about the earlier OFF1/OFF2 pair |

Note the corrected limit shared by both outcomes: the snapshot proves
delivery order to renderer command recording, not GPU execution order.

## 4. One bounded next observable (design only — no code change in this part)

Instrument (future part): (a) worker-side running digest in P2
`gs_frontend.cpp` `executeQueuedCommand` (§3b field table; `PrivWrite`
content excluded by opacity) with snapshot at `Fence` consumption (`:273-274`);
(b) in `gs_replay_core.cpp` kind-4 branch, after `gs.drainQueue();` (`:443`)
and before `refreshDisplaySnapshot()` (`:453`), emit one line per **sampled**
tick: `GB4_PKTSEQ tick=<tick> seq=<fence-snapshot hex> packets=<packets>`.
No per-packet device readback, no added GPU wait, no capture-flag change.
Expected bytes: 41 lines × ≤80 B ≈ 3.3 KB on stdout + verbatim rows in
`PS2X_GS_REPLAY_OUT` (`:699-705`). Run cap: one same-settings Odin OFF pair
(same APK/stream/env as OFF1/OFF2, to tick2050, ≤600 s boot cap, lease-held,
force-stop after). Receipt: field-diff of the two `GB4_PKTSEQ` series plus
the existing 41-row comparison. Stop rule: `seq` equal through 2050 →
H2-favored, next a readback-coverage probe (§2 gaps); `seq` differs at/before
tick850 → H1-favored, next an enqueue-order trace; any harness/error row →
void, no mechanism read. Closest alternative:
`RawGifPacket`-entry hash (`[P]` backend `:759-767`; `GifPacket` kinds only).

## 5. Gaps

- `gs_interface.cpp`, page-tracker bodies, Granite, Turnip/Adreno behavior,
  and the `GSInterface::vsync` wrapper/G31 probe are **unpinned to the APK**;
  all **[U]** edges are mechanism-informative only.
- Backend line numbers use the `c613…` N8D7F file; P2-tree backend differs
  (`84a13a80…`); core/frontend line numbers are fork-rev-pinned with APK tie
  by P3 receipt only.
- Mac Part 1 binary dirty state still unpinned (5F1 §1 gap, unchanged).
- No behavior beyond source text is asserted; OFF1/OFF2 PPMs viewed only via
  prior gates, not re-viewed here.

## 6. Receipts and checks

- `local/research/N8D7M12P5F3/REPORT.md` (this file), `check.py`,
  `check-result.json`. Commit `[N8D7M12] Part 5F3` with `Orchestrated-By:
  opencode`, explicit paths only, no push.
- `check.py` verifies: 3 pinned SHAs (two-method statement in REPORT) + rev +
  dirty-noted + HEAD-blob difference; backend `c613…` re-match at the N8D7F
  path; every §2–§3 cited line anchor present at its path (keyword within ±2
  lines), incl. worker FIFO/`executeQueuedCommand`/Fence/`GsRpcBase` anchors;
  required table fields present; no root-cause verdict claimed.

(End of file)
