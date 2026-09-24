# N8D7M12 Part 5F2 — packaged renderer source located; scoped readback audit

**State: COMPLETE, outcome A (exact packaged source located, scoped audit
grounded in pinned bytes). Read-only: no source edit, build, replay, boot,
device/lease action, fetch, push, board/global edit, or upstream contact.
LSP `documentSymbol` on the renderer file returned no results (no language
server for this C++ tree); all edges below are verified by exact line reads.
No root-cause verdict; the orchestrator decides.**

Brief: `local/muse/prompts/N8D7M12P5F2.md`. Prior reports/gates read: N8D7H
REPORT §§1–2, N8D7M12 Part 3 REPORT/gate, Part 5E2 REPORT/gate, Part 5F1
REPORT/gate. `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md` read.

## 1. SHA/provenance table (handback)

Pinned packaged bytes (N8D7H REPORT §1, double-read Mac + WSL):

| File | Pinned SHA-256 | Found at (working tree) | Read 1 | Read 2 (independent) | Rev | Tree state |
| --- | --- | --- | --- | --- | --- | --- |
| `gs/gs_renderer.cpp` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_renderer.cpp` | `85c29cb0…3de77e` MATCH | `85c29cb0…3de77e` MATCH (`sha256sum`) | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` | DIRTY (`M` entry) |
| `gs/gs_interface.hpp` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_interface.hpp` | `3a1751b4…05954d9d` MATCH | `3a1751b4…05954d9d` MATCH (`sha256sum`) | same `3a66c19` | DIRTY (`M` entry) |
| `gs/gs_renderer.hpp` | `fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a` | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_renderer.hpp` | `fae3261a…a93a401a` MATCH | `fae3261a…a93a401a` MATCH (`sha256sum`) | same `3a66c19` | DIRTY (`M` entry) |
| Fork backend (context) | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` | `~/dev/ssx3-work/N8D7F/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | `c6135b3c…6d4fb41f` MATCH | `c6135b3c…6d4fb41f` MATCH (`shasum -a 256`) | N/A (overlay source) | — |

Bounded negative search (same method, all differ from pins):

| Location | `gs_renderer.cpp` | `gs_interface.hpp` | `gs_renderer.hpp` | Rev |
| --- | --- | --- | --- | --- |
| `~/dev/ssx3-work/G43/parallel-gs/gs/` | `8071dd2e…` differ | `b74f5d22…` differ | `7f7a1e2b…` differ | `3a66c19`, dirty |
| `~/dev/parallel-gs/gs/` | `8071dd2e…` differ | `b74f5d22…` differ | `7f7a1e2b…` differ | `faf6400` over `3a66c19` |
| `~/dev/ssx3-work/G45/parallel-gs/gs/` | `193111de…` (= `3a66c19` HEAD blob) | `b74f5d22…` | `4066826a…` | — |
| `~/dev/ssx3-work/N8D5B/parallel-gs/gs/` | `8071dd2e…` differ | `b74f5d22…` | `7f7a1e2b…` | — |
| `~/dev/ssx3-work/N8D6A/parallel-gs/gs/` | `33224814…` (= N8D7H "N8D6B before") | `4c78cf9d…` (= before) | `8f511a44…` (= before) | — |
| `3a66c19` HEAD blobs (`git show HEAD:…`) | `193111de…` differ | `b74f5d22…` differ | `4066826a…` differ | `3a66c19` |
| `faf6400` blobs (`git show`) | `8071dd2e…` differ | `b74f5d22…` differ | — | `faf6400` |

Notes:

- The pinned bytes live in the **working tree only**: `git hash-object`
  gives `1812a3e5…` / `acd96122…` / `247d5ef1…`, and `git cat-file -e`
  fails for them in both `N8D7F/parallel-gs` and `~/dev/parallel-gs` — the
  exact bytes are **not committed in any local git history searched**.
- The brief's "currently dirty files do not match" is refined: the files
  are dirty vs their own HEAD `3a66c19` (HEAD blobs differ, row above), but
  the **working-tree bytes match the N8D7H pins exactly** (two reads each).
  Dirty-vs-HEAD does not contradict packaged provenance here.
- APK tie (receipts, P3 §1/§3–§4 + N8D7H §§1–2): the Part 3 APK
  (`caa11102…f512`) overlaid exactly the 7 fork files onto the N8D7M1 tree
  with `parallel [] jniLibs []` unchanged; N8D7M1 was N8D7H's tree plus one
  fork backend overlay with G43 files byte-identical. N8D7H read the same
  three SHAs from this N8D7F worktree as overlay sources (Mac) and
  re-pinned them canonically (WSL). Therefore these working-tree bytes are
  the **APK-tied source**, not merely similar code. Fork P2 worktree
  `~/dev/ssx3-work/N8D7M12P2/PS2Recomp` @ `a608ed1e161f60334a0cf3a80d1af3e54b692bd2`,
  `status --short` empty (clean, verified this part).

## 2. Scoped audit: VRAM-snapshot and scanout-Present readback paths

Scope: only what the three pinned files plus the pinned fork backend prove.
`gs/gs_interface.cpp` (which defines `GSInterface::map_vram_read`,
`flush`, `vsync`) is **not among the N8D7H pins** and is dirty (`+956`
lines vs HEAD) — its bodies are cited as `(unpinned .cpp, informative
only)` and prove nothing about the APK. Same for `Granite` (`m Granite`)
and the Vulkan driver. Unproved call edges are labeled `(unproved)`.

### 2a. Pinned call-path table

| # | Edge | Exact citation (pinned bytes) |
| --- | --- | --- |
| 1 | `map_vram_read(offset, size)` is a public `GSInterface` method; `flush()` likewise; `vsync(info)` returns `ScanoutResult` | `gs_interface.hpp:286,288,301` |
| 2 | No extra CPU↔GPU sync is promised beyond `flush()` on signal paths | `gs_interface.hpp:247-248` |
| 3 | `deterministic_timeline_query` defaults **false** (`DebugMode`); `set_hacks` never called ⇒ `Hacks` defaults (P5F1 edge 17) | `gs_interface.hpp:142` |
| 4 | `ScanoutResult` carries `image` + staging handles (`selected_vram_staging`, `circuit1_staging`) + capture status/rect fields | `gs_renderer.hpp:23-35` |
| 5 | Renderer keeps cross-vsync state: `vsync_last_fields[4]`, texture/promotion caches, `exhausted_descriptor_pools`, `descriptor_timeline` / `next_descriptor_timeline_signal` | `gs_renderer.hpp:464-467,559-560`; `gs_renderer.cpp:1791,5320-5329` |
| 6 | `GSRenderer::vsync` assumes pending ops already flushed; records scanout into `direct_cmd`; ends with **`flush_submit(0)` and no wait** | `gs_renderer.cpp:4396-4405,5354` |
| 7 | `flush_submit(0)` submits async/clear/setup/heuristic/binning/direct command buffers; with `value==0` takes **no timeline branch, no `wait_idle`, no `wait_timeline`** | `gs_renderer.cpp:1116-1208` (value branch `:1197-1208`) |
| 8 | The only `wait_idle` in the pinned renderer file is in `invalidate_super_sampling_state`, not on the scanout path | `gs_renderer.cpp:315-341` |
| 9 | The only full-VRAM (`4 MiB`) `CachedHost` staging copy in the pinned renderer is gated on `capture_selected_input` | `gs_renderer.cpp:4759,4806-4816` |
| 10 | The only scanout-image→host staging copy (`512×224×4`) is gated on `capture_selected_input && selected_vram_staging` | `gs_renderer.cpp:5054-5067` |
| 11 | `pre_deinterlace_merged` retention gated on `capture_scanout_stages`; field-history shift gated on deinterlace need | `gs_renderer.cpp:5314-5315,5317-5333` |
| 12 | Descriptor-pool recycle is timeline-gated: `query_timeline(*descriptor_timeline)` vs recorded signal | `gs_renderer.cpp:1746-1761` |
| 13 | Background `PGS-Waiter` thread advances `timeline_value` by `wait_timeline`; `flush_submit(value)` signals it only when `value!=0` | `gs_renderer.cpp:756-784` |
| 14 | Backend `Present` submits readback and calls **`wait_idle`**; `SnapshotVram` calls `flush()` + `map_vram_read(0,4MiB)` with **no backend-level wait** (fork, pinned via P5F1 edge 14/16; backend bytes here re-pinned `c6135b3c` this part) | P5F1 REPORT §2 edges 14, 16; `ps2_gs_parallel_backend.cpp` `c6135b3c…` (this REPORT §1) |
| 15 | `map_vram_read` body (page-tracker timeline wait then map) is in the **unpinned** `.cpp` — `(unproved for APK)` | (unpinned .cpp) `gs_interface.cpp:5126-5165` (informative only) |

### 2b. Synchronization: guaranteed by pinned source vs driver-dependent

| Synchronization | Status in pinned bytes |
| --- | --- |
| Scanout command recording happens-before `flush_submit(0)` submission | Guaranteed by source (edge 6–7) |
| Submission itself (queue submit calls) | Guaranteed by source (edge 7) |
| Any CPU wait for scanout work before `vsync` returns | **Not present** in pinned renderer (edge 7–8); the Present-path `wait_idle` lives in the fork backend (edge 14), outside these three files |
| VRAM-map visibility of scanout/render writes | **Not provable** from pinned bytes: tracker-wait body is unpinned (edge 15) |
| `CachedHost` coherency/invalidation on map | **Not provable** from pinned bytes: Granite device code (`m Granite`) + driver behavior |
| Descriptor-pool reuse safety | Timeline-gated in source (edge 12), but the timeline signal itself is a driver-observed value |
| Cross-vsync determinism of `vsync_last_fields`/promotion/texture caches | State is retained by source (edge 5); equality across runs depends on identical input history + driver execution — **not guaranteed by source** |
| `deterministic_timeline_query` stricter submit-wait | Exists but defaults **false** (edge 3); P5F1 established `set_hacks` never called |

### 2c. Relation to OFF1/OFF2 (no mechanism asserted proven)

Observed pair (5E2 REPORT §4 / gate): same APK, stream, env, backend —
full pins: APK `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`,
stream `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` —
41 ordered ticks; priv **41/41**; vram
**16/41**; present **25/41**; OFF1 hashes `19738cc3…783af9`, OFF2 hashes
`e78d7589…4ec580e`; first difference **tick850**; matching ticks
50–800 only; tick2050 vram/present differ with priv equal; both PPMs
512×448 P6, mostly black, different SHAs (`5e0caca3…` vs `050d864f…`).

Consistent-with (not proof of) readings under the pinned source:

- Pinned renderer `vsync` is submission-only with retained cross-vsync
  state (edges 5–7): with identical sampled priv mirrors, per-tick outputs
  can still differ across runs if any unflushed/unwaited GPU work,
  cache/promotion state, field history, descriptor-heap state, or
  `CachedHost` visibility differs at map time. The 19→16/41 intermittent
  re-match shape (ticks 1500/1550/1600 re-matching in ON/OFF; OFF1/OFF2
  matching only 50–800) fits state-dependent variance better than it fits
  monotonic drift — stated as shape consistency only.
- The three capture flags provably cannot explain tick850 (P5F1 §4; pinned
  gates at `gs_renderer.cpp:4759,4983,5054,5314`): the only in-renderer
  extra work they gate is staging copies/retention at scanout time.
- What the pinned bytes do **not** decide: whether packet ordering through
  the queue differed (priv equality covers only sampled CPU mirrors, P5F1
  correction), whether the page tracker covers scanout-render writes for
  the VRAM map path (edge 15 unpinned), or any Turnip-on-Adreno behavior.

## 3. One bounded next observable (no new live game boot)

Host-only static audit, no run of any kind: in the already-pinned trees,
trace `Vulkan::BufferDomain::CachedHost` map/invalidate handling in the
Granite device (`Device::map_host_buffer`/`unmap_host_buffer`) and the
page-tracker's write-coverage for the two readback consumers —
`SnapshotVram`'s `map_vram_read(0, 4 MiB)` (backend edge 14) and the
scanout staging copies (edges 9–10). Concretely: list every writer class
(transfer upload, render-pass store, `copy_blocks`, promotion) that marks
the tracker vs every reader the two paths map, and flag any writer that
bypasses the tracker or any `CachedHost` map without an invalidate. If the
coverage is complete and invalidates are unconditional, source-level
sync/readback trouble is disfavored toward input/order variation (closed
by a same-stream packet-trace diff, which is a replay-harness run, not a
game boot); any bypass/invalidate gap is a concrete named suspect for the
orchestrator — still not proof of the Odin variance.

## 4. Gaps

- `gs_interface.cpp` body (actual `map_vram_read` wait+map,
  `flush()`, `GSInterface::vsync` wrapper incl. any G31 probe) is **not
  SHA-pinned** — the VRAM-map wait claim rests on dirty-tree reads only.
- `Granite` device (`map_host_buffer`, `wait_idle`, timeline semaphores)
  and Turnip-on-Adreno behavior are outside all pins.
- Mac Part 1 binary's exact dirty state remains unpinned (P5F1 §1 gap,
  unchanged).
- No behavior beyond source text is asserted; OFF1/OFF2 PPMs viewed only
  via prior gates, not re-viewed here.

## 5. Receipts and checks

- `local/research/N8D7M12P5F2/REPORT.md` (this file), `check.py`,
  `check-result.json`. Commit `[N8D7M12] Part 5F2` with
  `Orchestrated-By: opencode`, explicit paths only, no push.
- `check.py` verifies: 3 pinned SHAs (two-method reads) + rev + dirty-noted
  + HEAD-blob difference; backend pin re-match; all §2 citation lines
  present at pinned paths; APK/stream/OFF1/OFF2 receipt SHAs; LSP
  unavailability stated; no root-cause verdict claimed.

(End of file)
