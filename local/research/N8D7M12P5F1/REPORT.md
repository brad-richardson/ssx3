# N8D7M12 Part 5F1 — read-only GPU hash/sync path audit

**State: COMPLETE, outcome A (source map grounded). Read-only: no source
edit, build, replay, boot, device/lease action, push, board/global edit, or
upstream contact. Scoped to the hash-producing and synchronization call path
only. No diagnostic elapsed time is speed. No root cause is asserted; the
orchestrator decides after the same-settings repeat.**

Brief: `local/muse/prompts/N8D7M12P5F1.md`.

Question: with the exact same Odin APK (`caa11102…f512`) and GS stream
(`f6a78f71…a593`), why can GPU VRAM/present hashes vary while all 41 priv
hashes match? ON/OFF first differs at tick850, before the three
selected/oracle/tile flags act at tick2050. **The same-settings OFF repeat
outcome is not assumed.**

Prior reports/gates read: N8D7M12 Part 1, P2, P3, P5B (+gate), P5C (+gate),
P5D1, P5D2 (+gate). `~/dev/AGENTS.md`, repo `AGENTS.md`,
`local/AGENTS.local.md` read.

LSP: `goToDefinition` and `hover` on `gs_replay_core.cpp:460` returned no
results (no language server for this C++ worktree). **LSP unavailable**; all
call edges below are verified by exact line reads instead.

## 1. Pins and provenance

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7M12P2/PS2Recomp` @ `a608ed1e161f60334a0cf3a80d1af3e54b692bd2`, `status --short` empty (verified this part, clean) |
| parallel-gs worktree (local read) | `~/dev/ssx3-work/N8D7F/parallel-gs` @ `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`, DIRTY (verified this part) |
| Dirty files (do NOT stand in for APK bytes) | `M CMakeLists.txt`, `m Granite`, `M gs/gs_interface.cpp`, `M gs/gs_interface.hpp`, `M gs/gs_renderer.cpp`, `M gs/gs_renderer.hpp`, `M tools/CMakeLists.txt`, `M tools/gs_dump_replayer.cpp`, `?? gs/n8d5_tile_spirv.hpp`, `?? gs/shaders/n8d5_tile.comp`, `?? gs/shaders/n8d5_tile.spv` |
| APK studied | `~/dev/ssx3-work/N8D7M12P3/app-release.apk`, 153,753,116 B, `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` (P3/P5B/P5D2 gates) |
| Packaged runner / Turnip / HAL | `329e44db…18a3d` / `717812c3…1ac29d` / `1b49d27c…fc387` (P3 §4, P5B §1) |
| Stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, 1,100,696,462 B, `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| ON hashes / PPM | `~/dev/ssx3-work/N8D7M12P5A/parallel.hashes` (`0e89a493…`, 2686 B) / `vq-002050.ppm` (`39b70d67…`, 688,143 B) |
| OFF hashes / PPM | `~/dev/ssx3-work/N8D7M12P5D1/parallel.hashes` (`19738cc3…`, 2686 B) / `vq-002050.ppm` (`5e0caca3…`, 688,143 B) |

APK→source chain (receipts, not re-read here — no `ssh` per worker
permissions): P3 proves the WSL build root was a zero-noncache-diff copy of
N8D7M1 plus exactly the 7 fork files (`d1ba1d4..a608ed1`), parallel/jniLibs
unchanged (P3 REPORT §§1–4). N8D7M1 was N8D7H's tree plus one fork backend
overlay with G43 files byte-identical (brief `N8D7M12P3.md:7`). N8D7H pins
the G43 renderer bytes by SHA: `gs_renderer.cpp` `85c29cb0…`,
`gs_interface.hpp` `3a1751b4…`, `gs_renderer.hpp` `fae3261a…`, backend
`c6135b3c…` (N8D7H REPORT §§1–2). Therefore the APK's renderer bytes are the
N8D7H SHAs above, **not** the current dirty worktree. Renderer-side line
numbers below are labeled `(dirty-tree)` and are mechanism-informative only.

Gap: the Mac Part 1 binary was built from the same dirty worktree path at an
earlier state (`PS2X_PARALLEL_GS_SOURCE_DIR=~/dev/ssx3-work/N8D7F/parallel-gs`,
P1 brief); its exact content then is unpinned. Mac numbers are context only.

## 2. Compact call-path table (@ `a608ed1` unless marked)

| # | Edge | Exact citation |
| --- | --- | --- |
| 1 | Android entry: `PS2X_GS_REPLAY_ONDEVICE=="1"` → strict capture/parallel/Turnip gates → `ps2x_gs_replay_run()` → `_Exit`, no EE/game thread | `ps2xRuntime/src/main.cpp:215-269` (call at `:239`) |
| 2 | Core setup: `BACKEND=parallel` ⇒ `queued=true`; stride default 50 (`STEP`); `dropPriv=false`, no RTZ/path defaults; queue enabled; parallel backend created | `ps2xRuntime/src/lib/gs/gs_replay_core.cpp:175-180,209-214,222-233` |
| 3 | Hash primitives: `fnv` = FNV-1a-32 (basis 2166136261, prime 16777619) | same file `:25-34` |
| 4 | `priv` = FNV over CPU `GSRegisters` mirror only (pmode…siglblid + csr/vsyncTick atomics). No backend call | same file `:84-92` |
| 5 | `present` = FNV over `PresentationFrame` pixels, 640×4 stride, `width*4` valid bytes/row | same file `:94-113` |
| 6 | Marker barrier: every kind-4 record runs `gs.drainQueue()` before sampling | same file `:443` |
| 7 | `vram` (sampled ticks only): `refreshDisplaySnapshot()` → `lockDisplaySnapshot()` → FNV over snapshot → `unlockDisplaySnapshot()` | same file `:450-458` |
| 8 | `frame` (sampled OR named ticks): `presentForDiagnostics()`; PPM dump + `GB4_FRAME` only when named (`PPM_TICKS`); row emitted only when sampled | same file `:446-449,459-472,506-513` |
| 9 | Receipt: `PS2X_GS_REPLAY_OUT` gets verbatim row copies | same file `:699-705` |
| 10 | `drainQueue`: worker Fence RPC + wait; no-op if quiescent/in-worker | `ps2xRuntime/src/lib/gs/gs_frontend.cpp:178-190` |
| 11 | `refreshDisplaySnapshot`: worker RPC → `snapshotVRAM()` = `Sync(DebugReadback)` + `SnapshotVram()` under backend-lifetime lock | same file `:742-755,377-390` |
| 12 | `presentForDiagnostics`: worker RPC → `Flush()` + `Sync(Presentation)` + `Present(request)`; request built from priv mirror + ctx frames | same file `:839-864,757-776` |
| 13 | Parallel backend `Flush()` / `Sync()` are **empty no-ops**; all GPU sync delegates to renderer internals | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:427-429` |
| 14 | `Present`: `ensureInit` → `syncPriv` (memcpy priv→renderer) → flag gating → `m_iface->flush()` → `m_iface->vsync()` → readback copy + barrier + `submit` + **`wait_idle`** → (2050-only blocks) → map + 640-stride pack | same file `:431-453,593-602,790-836` |
| 15 | `out` packing: zero-filled 640-stride buffer, valid rows memcpied; `displayFbp`/`sourceFbp` from CPU `m_priv->dispfb1` | same file `:819-829` |
| 16 | `SnapshotVram`: `flush()` + `map_vram_read(0,4MiB)` + memcpy; **no `wait_idle` of its own** | same file `:867-886` |
| 17 | `ensureInit`: Android+`TURNIP=1` → Turnip HAL loader; else system loader. Same device flags both hosts (1 thread index, push-descriptor + descriptor-heap + descriptor-buffer, 4 frame contexts); `set_hacks` never called ⇒ `Hacks` defaults | same file `:916-963`; defaults (dirty-tree) `gs/gs_interface.hpp:214-240` |
| 18 | Renderer readback sync (dirty-tree): `map_vram_read` waits page-tracker timeline then maps; `flush()` submits and waits only if `deterministic_timeline_query` (default false) | (dirty-tree) `gs/gs_interface.cpp:5126-5165`, `gs/gs_interface.hpp:142` |
| 19 | Renderer vsync (dirty-tree): `renderer.vsync(...)` then a local G31 probe doing its own `map_vram_read` + LOGI (log-only, timing-affecting); `ScanoutResult` carries image + staging handles | (dirty-tree) `gs/gs_interface.cpp:5576-5643`, `gs/gs_renderer.hpp:23-35` |
| 20 | Capture blocks (dirty-tree): selected staging copies recorded in-scanout gated on `capture_selected_input`; stage-image retention gated on `capture_scanout_stages`; both default false | (dirty-tree) `gs/gs_renderer.cpp:4759,4777,4983-4984,5054,5314-5315` |
| 21 | PPM receipt (dirty-free fork header): P6 `width×height`, 640-stride source, RGB bytes (alpha dropped) | `ps2xRuntime/include/ps2_vq.h:115-139` |

## 3. What each hash actually measures

- `priv`: deterministic function of the CPU register mirror at fenced
  marker boundaries. Identical 41/41 across ON/OFF (incl. tick850
  `60a25873`, tick2050 `6621fe06`) establishes equality of the sampled
  CPU GS-register mirror only. It does not establish packet ordering
  through the queue or equality of inter-marker state.
- `vram`: FNV over the 4 MiB VRAM image returned by the page-tracker-synced
  map path (no backend-level wait). Which writers (transfers, uploads,
  render output) are reflected in those bytes is not proven by the cited
  source and is stated as unknown.
- `present`: FNV over the scanout image re-rendered fresh per sample
  (`vsync` per sampled/named tick), read back through submit+`wait_idle`.
  Reflects renderer-internal state (caches, promotion, deinterlace field
  history, descriptor heap) plus driver execution.

Within-run self-consistency (receipt-level, constrains mechanism C):
`GB4_FRAME tick=2050 present` equals the tick2050 `GB4_REPLAY present` in
both runs (`b167a719` ON, `1dc1aba8` OFF) — the present hash function is
stable on identical input within a run. Both PPMs are 688,143 B =
512×448×3+15, so frame geometry/stride path is identical; only pixels differ.

## 4. Flag-gating verification (scoped source)

VERIFIED: the three flags are truly without effect before tick2050.

- Whole-fork search for the three env names finds exactly 3 `getenv`
  sites, all in `Present` (`ps2_gs_parallel_backend.cpp:439,440,667`).
- `selectedRequested` requires `vsyncTick==2050` AND `=="1"`; unset,
  empty, `0` all disable (`:441-442`). `tileRequested` is
  `selectedRequested` OR (`vsyncTick==2050` AND `=="1"`) (`:443-444`).
- `ORACLE` is read only inside `if (selectedRequested)` (`:603,667-669`),
  so it runs only at tick2050 with selected on.
- `getenv` executes on every `Present`, but the resulting booleans are
  false before tick2050, and the renderer's extra blocks are gated on the
  resulting `VSyncInfo` flags (edge 20), which default false. Env presence
  alone changes nothing.
- The non-gated readback spine (renderer flush+vsync, copy+`wait_idle`,
  map, 640-stride pack) runs identically on every sampled tick regardless
  of flags (edges 14–15).

Hence divergence starting at tick850 cannot be the three flags. The
ON/OFF GPU-work difference is confined to tick2050 (extra tile dispatches,
staging copies and maps in the same command stream).

## 5. Android vs Mac (source-grounded deltas)

| Aspect | Android (Odin APK) | Mac (Part 1 binary) |
| --- | --- | --- |
| Replay core → frontend → backend code | identical (`a608ed1` fork files overlaid; P3) | identical (same worktree files at build time, exact dirty state unpinned — §1 gap) |
| Vulkan loader | Turnip HAL via `initTurnipLoader` (backend `:927-934`), packaged `libvulkan_freedreno.so` `717812c3…` | system loader `init_loader(nullptr)` + `GRANITE_VULKAN_LIBRARY` → MoltenVK (Part 1 §4) |
| Driver | Turnip/Freedreno on Adreno | MoltenVK on Apple silicon |
| Env contract | same replay/step/PPM keys; `PS2X_GS_TURNIP=1` | same minus Turnip; `GRANITE_VULKAN_LIBRARY` set |
| Sync code | same no-op Flush/Sync, same Present/SnapshotVram, same 1-thread/4-frame-context device | same |

## 6. Candidate-mechanism evidence table (handback — no root cause)

Observed pair (P5D2 §4): SUMMARY identical
(queue/parallel 862958/11499/25445/2050); priv 41/41; vram 19/41; present
25/41; first diff tick850 (`00c4eed5/6e74ea59` ON vs `23589ef3/9d6d204c`
OFF, priv `60a25873` both); matching ticks 50–800 + 1500/1550/1600;
tick2050 `4ba27b77/b167a719` ON vs `9035e824/1dc1aba8` OFF (priv equal);
PPMs same size, different SHA.

| Mechanism | Source evidence (this audit) | What remains unknown | One bounded observable, no new live game boot |
| --- | --- | --- | --- |
| (A) Replay input/ordering variation before backend | No positive evidence; narrow counter-evidence: identical SUMMARY counts; priv 41/41 equal, which establishes sampled CPU-mirror equality only — packet ordering through the queue and inter-marker state remain unproven either way; `mode=queue` both runs (edge 2); `drainQueue` Fence at every marker (edges 6,10); no RTZ/path/drop env in either env (P5D1 §2) | Whether packet ordering or inter-marker transient state differed between the runs | Bounded replay of the same stream with packet-trace env (desktop or device replay, not a game boot), diffing per-packet path/order; identical traces close (A). Field-diff of the two pinned hash files + SUMMARY lines is the first half (already yields sampled-priv/count equality) |
| (B) GPU submission/readback sync or uninitialized state | Plausible by structure, unproved: backend Flush/Sync are no-ops (edge 13) — sync lives in renderer internals; Present readback fenced by submit+`wait_idle` (edge 14) but SnapshotVram has no wait of its own (edge 16, relies on dirty-tree tracker wait, edge 18); 19/41 intermittent matches (1500/1550/1600 re-matching after divergence) fit state-dependent variance, not monotonic drift; renderer keeps cross-vsync state (field history, promotion/texture caches, descriptor heap) | Tracker coverage of scanout-render writes for the VRAM map path; `CachedHost` coherency handling in `map_host_buffer`; Turnip timeline behavior on the Odin; any uninitialized-descriptor/staging reads | The prepared same-settings OFF repeat, field-diffed vs OFF#1: first-diff tick moving from 850 (or a changed match set) supports run-to-run GPU-side nondeterminism (B); byte-identity disfavors it toward (C). Host-only static half: audit `map_host_buffer` invalidate + tracker write-coverage on both readback paths |
| (C) Deterministic backend + hashing/receipt artifact | Constrained but not closed: within-run present self-consistency (`GB4_FRAME`==row present both runs, §3); OUT file is verbatim rows (edge 9); PPM derives from the same frame object (edge 8); both PPMs 512×448 P6 (geometry path identical); `vram` has no within-run double-hash and snapshots are not retained | Whether retained PPMs reproduce row `present` values offline (needs per-pixel alpha: `dumpPpm` drops it, edge 21) | Host-only recompute: FNV-1a-32 over retained PPM rasters mapped back through the `dumpPpm` transform (edge 21), testing alpha-constancy explicitly; mismatch-or-geometry-anomaly supports artifact, match (under stated alpha) constrains it. Repeat-equality (O-B's observable) supports the determinism half of (C) but does not by itself locate the ON/OFF difference |

Reading guide, not a verdict: O-repeat equality → (C)-family determinism
supported, (A)/(B) disfavored; O-repeat variance → (B) or (A), separated by
O-trace (input-level difference required for (A), absent for (B)); O-PPM
recompute bears only on (C)'s artifact sub-claim. If the repeat matches
OFF#1 while ON#1 still differs, the ON/OFF pair difference lies outside all
three backend mechanisms (run-context/harness class) — the predeclared VOID
reading (P5C §4) stands.

## 7. Receipts and checks

- `local/research/N8D7M12P5F1/REPORT.md` (this file), `check.py`,
  `check-result.json`. Commit `[N8D7M12] Part 5F1` with
  `Orchestrated-By: opencode`, explicit paths only, no push.
- `check.py` verifies: fork pin `a608ed1` + clean; parallel-gs pin
  `3a66c19` + dirty-noted; all §2 citation lines present at pinned paths;
  ON/OFF receipt SHAs/sizes; flag-gating lines; no-op Flush/Sync lines.

(End of file)
