# N8D7M12 Part 5F4 — queued-GS command fingerprint, host validation only

**State: BLOCKED (permission), outcome B/OTHER. First failure: the `edit`
tool denied the first fork source write on the brief-authorized private root.
Per worker rules no workaround was attempted (no bash edit, no other path).
No build, suite, replay, lease, Android/device action, fork/main push,
board/global edit, or upstream contact. No Android claim. No GPU verdict.**

Brief: `local/muse/prompts/N8D7M12P5F4.md`. Prior reports/gates read in full:
N8D7M12P5F3 REPORT + ORCH-GATE, Part 5M4 ORCH-GATE, N8D7M12 Part 1 REPORT.
`~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md` read.

## 1. First-failure receipt (verbatim denial)

At the first implementation step (header insertion in the private fork
worktree), the `edit` tool returned:

> `The user has specified a rule which prevents you from using this specific
> tool call. Here are some of the relevant rules
> [{"permission":"*","action":"allow","pattern":"*"},
> {"permission":"edit","pattern":"*","action":"allow"},
> {"permission":"edit","pattern":"**/opencode.json","action":"deny"},
> {"permission":"edit","pattern":"**/.opencode/**","action":"deny"},
> {"permission":"edit","pattern":"../*","action":"deny"},
> {"permission":"edit","pattern":"/Users/brad/dev/ssx3-work/N8D7M12P5F4/**","action":"allow"}]`

Target path (exactly under the allowed pattern):
`~/dev/ssx3-work/N8D7M12P5F4/PS2Recomp/ps2xRuntime/include/runtime/gs/gs_frontend.h`.
The allow rule names this root, but the `../*` deny (cwd-relative, this pane
runs from `~/dev/ssx3`) appears to shadow it. The brief-prescribed sentinel
(`touch` + `rm` of `.sentinel-p5f4` via shell) succeeded and was removed, and
`read` works on the root — only the `edit`-tool write is denied. Read-only
source analysis below is complete; it grounds a relaunch with a fixed
per-worker exception (the intended diff is small and fully specified in §4).

## 2. Pins (verified this part, read-only)

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7M12P5F4/PS2Recomp`, branch `n8d7m12-p5f4` |
| Fork HEAD | `a608ed1e161f60334a0cf3a80d1af3e54b692bd2`, `status --short` empty |
| Sentinel | created + removed; tree still clean (no fork change of any kind) |
| Reference stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` (pin `f6a78f71…a593`, not re-read) |
| Mac ON hashes | `~/dev/ssx3-work/N8D7M12/mac-parallel/parallel.hashes` (`94b433df…10c290`) |
| Other lanes | no `clang`/`ninja` heavy jobs (only clangd LSP); disk 150.4 GB of 200 GB |
| Suite / replay / build | NOT RUN (blocked before any mutation) |

## 3. Source-grounded design table (verified by exact line reads, unapplied)

| # | Fact | Citation (worktree @ `a608ed1`) |
| --- | --- | --- |
| D1 | Single consumer, strict FIFO: worker pops head, runs handler, signals RPC | `gs_worker.h:12-16`; `gs_worker.cpp:112-115,118` per 5F3 §3b |
| D2 | `executeQueuedCommand` switch covers every kind of §3b field table | `gs_frontend.cpp:192-279` (GifPacket `:197-199`, NoteGifPath `:200-202`, RegWrite `:203-205`, UploadImageNative `:206-209`, NativePacked `:210-212`, ClearCtx/Active `:213-219`, WriteVram `:220-223`, PrivWrite `:230-232`, Fence `:273-274` no-op) |
| D3 | `PrivWrite.apply` is opaque `std::function<void()>` — content unhashable | `gs_worker.h:97-115` (`apply` field `:115`); null apply returns before enqueue (`gs_frontend.cpp:1440-1441`) |
| D4 | `drainQueue` skips the Fence when `isQuiescent()` — Fence presence is timing-dependent, so Fence must never enter the digest | `gs_frontend.cpp:178-190`; `isQuiescent` doc `gs_worker.h:143-146` |
| D5 | GifPacket carries no path; consumed `m_curGifPath` comes from prior NoteGifPath consumption (FIFO) | enqueue sites `:929-939` (bytes only), header `noteGifPath` (separate command); worker branch `:949,955-956` reads `m_curGifPath` |
| D6 | Kind-4 marker calls `gs.drainQueue()` at `:443`, `refreshDisplaySnapshot()` at `:453`; sampled gate at `:446-449`; rows → stdout `:696-697` and `PS2X_GS_REPLAY_OUT` `:699-705` | `gs_replay_core.cpp:436-514,696-705` |
| D7 | Replay enables queue before any submit (`setQueueEnabled(true)` `:222-223`, before parallel `SetBackend` RPC `:224-233`); `PS2X_GS_REPLAY_PKTSEQ` name is free (no existing reader) | `gs_replay_core.cpp:175-243`; grep shows no `PKTSEQ` reader |
| D8 | RefreshSnapshot/DiagPresent/Consume RPCs enqueue deterministically at sampled ticks / kind-6 records, so kind-only mixing stays run-deterministic | `:443-459` (sampled-only snapshot/present), `:588-589` (kind-6 consume), frontend `:742-747,841-844,2100-2103` |
| D9 | Queue test file reuses MiniTest `tc.Run`; current suite 585/585/0; one new Run ⇒ expect 586/586/0 | `ps2_gs_queue_tests.cpp:446-830`; Part 1 REPORT §3 |

Mixing rule (follows 5F3 §3b, 64-bit FNV-1a per brief): kind tag + consumed
fields per D2/D5; PrivWrite kind only (D3 gap); all side RPCs kind only;
Fence snapshots running→snapshot without mixing (D4); `drainQueue`
quiescent early-return copies running→snapshot (digest stable: queue empty
AND nothing executing, single producer in replay). Emission
`GB4_PKTSEQ tick=<t> seq=%016llx commands=%llu` directly to stdout between
`:449` and `:451`, gated on `pktSeq && sampled` — never into `rows`, so
`parallel.hashes` format stays intact. Setter must precede
`setQueueEnabled(true)` (worker-start happens-before; direct mode unaffected
since `executeQueuedCommand` never runs there).

Limits restated: diagnostic sample of hashed fields only; 64-bit collisions
possible; PrivWrite content absent; proves delivery order to renderer command
recording, not GPU execution order.

## 4. Intended source change (NOT APPLIED — uncompiled, for a fixed pane)

Allowed paths only (`gs_frontend.h`, `gs_frontend.cpp`, `gs_replay_core.cpp`,
`ps2_gs_queue_tests.cpp`):

1. `gs_frontend.h`: after `drainQueue()` decl, add `setPktSeqEnabled(bool)` /
   `pktSeqEnabled()` / `pktSeqSnapshot()` / `pktSeqSnapshotCommands()` with the
   D4/Fence comment; private: `noteConsumedCommand(const GsCommand&)` decl +
   `bool m_pktSeqEnabled=false`, `std::mutex m_pktSeqMutex`,
   `uint64_t m_pktSeqDigest/m_pktSeqCommands/m_pktSeqSnapshot/
   m_pktSeqSnapshotCommands` (digest/snapshot init FNV-64 offset
   `14695981039346656037ull`, counts/snapshot-when-off `0`).
2. `gs_frontend.cpp`: anonymous-namespace FNV-1a-64 mix helpers (u8/u32/u64-LE/
   bytes); getters lock the mutex; `noteConsumedCommand` mixes per §3 table
   (GifPacket: kind + consumed `m_curGifPath` + bytes; Fence: snapshot only);
   call it at the top of `executeQueuedCommand` when enabled (before the
   handler runs, so the path value is the prior-consumed one, D5); quiescent
   branch of `drainQueue` copies running→snapshot when enabled.
3. `gs_replay_core.cpp`: `const bool pktSeq` from
   `PS2X_GS_REPLAY_PKTSEQ=="1"`; `gs.setPktSeqEnabled(pktSeq)` immediately
   before `gs.setQueueEnabled(true)`; sampled-gated `GB4_PKTSEQ` stdout line
   after the `:448-449` early-continue, before `:451`.
4. `ps2_gs_queue_tests.cpp`: one new `tc.Run` (property-only, never mirroring
   the hash): two queued instances, same script ⇒ equal snapshot+count;
   swapped order of two distinguishable WriteVrams ⇒ digest differs, count
   equal; one payload byte changed ⇒ differs; second `drainQueue()`
   (quiescent) ⇒ snapshot stable; default-off instance ⇒ snapshot 0, count 0.

## 5. Validation (NOT RUN)

| Check | Result |
| --- | --- |
| `git diff --check` / runner-dir diff vs `14b1e5cb` | N/A — zero fork bytes changed |
| One configure+build / one suite / one Mac replay | NOT RUN (blocked; budget unspent, no lease claimed) |
| `check.py` | verdict **BLOCKED**, checks in `check-result.json` |

## 6. Handback table

| Condition | Outcome | Next action |
| --- | --- | --- |
| `edit`-tool write denied on authorized private root; sentinel/read OK | **BLOCKED (permission), B/OTHER, no Android claim** | Relaunch with a working per-worker exception (`../*` deny shadows the `N8D7M12P5F4` allow); then apply §4 (4 files), one build + suite (expect 586/586/0), one pinned-stream replay (41 `GB4_PKTSEQ` + 41 `GB4_REPLAY` rows) |
| Any GPU-cause reading from this part | none — no run, no verdict beyond the permission block | orchestrator gates any Odin pair separately |

## 7. Receipts (committed, explicit paths only)

`local/research/N8D7M12P5F4/{REPORT.md,check.py,check-result.json}`.
Commit `[N8D7M12] Part 5F4` with `Orchestrated-By: opencode`, explicit paths
only, no push. Private scratch (not committed): nothing new (no build dir
created, no replay outputs).
