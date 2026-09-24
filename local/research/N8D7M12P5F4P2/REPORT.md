# N8D7M12 Part 5F4P2 — worker-consumption GS fingerprint (COMPLETE, outcome A)

**State: COMPLETE, outcome A. One bounded implementation, one validation pass
(1 configure + 1 build + 1 suite + 1 exact-stream Mac replay, one P-lane slot).
No Android package, no Odin action, no push, no upstream contact.
No Android/GPU verdict; no wall-time speed is quoted.**

Brief: `/Users/brad/dev/ssx3/local/muse/prompts/N8D7M12P5F4P2.md`. Sources read in full:
`~/dev/AGENTS.md`, `~/dev/ssx3/AGENTS.md`, `~/dev/ssx3/local/AGENTS.local.md`,
`local/muse/prompts/N8D7M12P5F4.md` (via ssx3), `local/research/N8D7M12P5F4/{REPORT.md,ORCH-GATE.md}`,
`local/research/ARCH1/{REPORT.md,ORCH-GATE.md}`, plus N8D7M12 Part 1 REPORT and P5F3/P5M4 reports.
Citations are repo source, not web. LSP `goToDefinition` at `gs_frontend.cpp:193` returned
no results (no language server for this C++ tree, same as 5F3); call relationships confirmed
by exact line reads. REPORT was written early with `not found` cells and refined after.

## 1. Pins

| Item | Value |
| --- | --- |
| Fork worktree | start folder (private fork worktree), branch `n8d7m12-p5f4` |
| Fork base / HEAD | `a608ed1e161f60334a0cf3a80d1af3e54b692bd2` / private commit (see §6) |
| Reference stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, 1100696462 B, SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` (two matching reads before use) |
| New binary | `~/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests`, SHA `e21f6b8d2d6599114d7602548bcfed6e668e8415af76940b7c5a19404319fbc1` (two matching reads) |
| Parallel source / codegen | `~/dev/ssx3-work/N8D7F/parallel-gs`, `~/dev/ssx3-work/codegen-ssx3` (Part 1 values) |
| Toolchain idle | no `clang`/`ninja` (only clangd LSP) before build and replay; both P-lane slots free before claim |
| Private bytes | 1.4 GiB build dir, ≤10 GiB cap; receipt text 193 KiB, ≤512 KiB cap |

## 2. Implementation (F4 REPORT §4 followed; no broader API change needed)

F4 D1–D9 re-confirmed by line reads at `a608ed1` before editing; no concrete flaw found,
so no scope expansion and no stop-table was needed.

| Piece | File |
| --- | --- |
| `setPktSeqEnabled(bool)` / `pktSeqEnabled()` / `pktSeqSnapshot()` / `pktSeqSnapshotCommands()` + Fence-comment; private `noteConsumedCommand` decl, `m_pktSeqMutex`, `m_pktSeqEnabled=false`, digest/snapshot init FNV-64 offset / 0 while off | `ps2xRuntime/include/runtime/gs/gs_frontend.h` (+20) |
| FNV-1a-64 helpers with explicit LE encoding, length-prefixed payloads; getters lock mutex; `noteConsumedCommand` mixes kind + consumed fields (GifPacket: kind + live `m_curGifPath` + bytes; Fence: snapshot only, never hashed/counted); hooked at top of `executeQueuedCommand` before the handler; quiescent `drainQueue` copies running→snapshot when enabled | `ps2xRuntime/src/lib/gs/gs_frontend.cpp` (+147) |
| `PS2X_GS_REPLAY_PKTSEQ=="1"` gate, `setPktSeqEnabled` before `setQueueEnabled(true)`; sampled-gated `GB4_PKTSEQ tick=<t> seq=%016llx commands=%llu` to stdout only (never into `rows`/`OUT`) | `ps2xRuntime/src/lib/gs/gs_replay_core.cpp` (+18) |
| One new property-only `tc.Run` (never mirrors the hash): two instances same script ⇒ equal digest+count; swapped order of two distinguishable WriteVrams ⇒ digest differs, count equal; one payload byte flipped ⇒ differs; second (quiescent) `drainQueue` ⇒ snapshot stable; default-off instance ⇒ snapshot 0, count 0 | `ps2xTest/src/ps2_gs_queue_tests.cpp` (+79) |

Hash coverage: GifPacket / NoteGifPath / RegWrite / UploadImageNative / NativePacked /
ClearCtx / ClearActive / WriteVram by kind + consumed fields; PrivWrite kind-only
(opaque `apply` gap, declared); side RPCs kind-only; Fence excluded from digest/count.

## 3. Validation (A)

| Check | Result |
| --- | --- |
| `git diff --check` / runner-dir diff vs `14b1e5cb` (committed + working tree) | PASS, empty |
| One configure + one build (`ps2x_tests`), Release/Ninja, Part 1 flags | rc=0 (one known ld duplicate-library warning, as in Part 1) |
| One suite from fork cwd | **586/586/0** PASS (585 + 1 new `pktseq` test, `[Passed]`) |
| One pinned-stream parallel replay, exit 0, one P-lane slot (claimed 1, released) | PASS, log 4,817,707 B full (in private scratch; excerpt in receipts), output tree 680 KiB |
| Parser counts vs Part 1 baseline | packets 862958, priv 11499, transfers 25445, markers 2050, samples 41 — all equal |
| `GB4_PKTSEQ` rows | exactly 41, ticks 50…2050 ordered, grammar exact, commands strictly increasing 251→1737496 |
| Existing replay rows | exactly 41 `GB4_REPLAY tick=`, ticks 50…2050 ordered |
| `parallel.hashes` / `vq-002050.ppm` vs pinned Mac ON | byte-identical (`94b433df…10c290` / `9490484c…14fce3e`); tick2050 present `d19b96fe` |
| `check.py` | verdict **PASS** (`check-result.json`), 36/36 |

No diagnostic wall time is quoted as speed. No retry: exactly one build, one suite, one replay.

## 4. Exact commands (worktree = start folder unless noted)

```sh
cmake -S <worktree> -B ~/dev/ssx3-work/N8D7M12P5F4/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DPS2X_BUILD_TEST=ON \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D7F/parallel-gs \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3   # rc=0
ninja ps2x_tests            # workdir=build; rc=0 (absolute receipt-log path; one exploratory-log-path typo, rc=1 writing nothing, reran correctly — not a brief-step failure)
<worktree>/../build/ps2xTest/ps2x_tests  # workdir=worktree; rc=0, 586/586/0
python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py claim n8d7m12p5f4p2  # -> slot 1
PS2X_GS_REPLAY_CAPTURE=.../N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_N8D7F_SELECTED_CAPTURE=1 PS2X_N8D7L_ORACLE=1 PS2X_N8D5_TILE_CAPTURE=1 \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 \
PS2X_GS_REPLAY_PPM_DIR=.../N8D7M12P5F4/mac-pktseq/frames \
PS2X_GS_REPLAY_OUT=.../N8D7M12P5F4/mac-pktseq/parallel.hashes \
PS2X_GS_REPLAY_PKTSEQ=1 \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib \
  .../build/ps2xTest/ps2x_tests   # workdir=worktree, own PID; rc=0; slot released after
python3 local/receipts/N8D7M12P5F4P2/check.py  # verdict PASS 36/36
```

## 5. Deviations (disclosed, no budget impact)

- First `ninja` invocation used a worktree-relative receipt-log path while cwd was the build
  dir and wrote nothing (rc=1); reran with the absolute path. Counts as the one build.
- Full 4.8 MiB replay log lives in private scratch (`mac-pktseq/replay.log`); receipts carry
  the 85-line `replay-excerpt.txt` (all GB4 rows/summary) to hold receipt text under 512 KiB.

## 6. Handback table

| Condition | Outcome | Next action |
| --- | --- | --- |
| Same-sequence ⇒ equal digest+count; reorder / payload-flip ⇒ digest differs; default-off silent; 586/586/0; 41 `GB4_PKTSEQ` + 41 replay rows; hashes/PPM byte-equal to Mac ON | **A PASS, no Android claim** | Orchestrator gates any same-settings Odin pair separately; per ARCH1, equal digest with differing output ends input-hash expansion (downstream state/readback probe), a differing digest calls for delivery investigation |
| Any GPU-cause reading from this part | none — host-only delivery fingerprint; equality cannot prove GPU execution, PrivWrite contents, or a GPU cause | — |

Private fork commit: source-only `[N8D7M12] Part 5F4P2` with `Orchestrated-By: opencode`, no push.

## 7. Receipts (untracked, never added to the fork commit)

`local/receipts/N8D7M12P5F4P2/{REPORT.md,check.py,check-result.json,configure.log,build.log,suite.log,replay-excerpt.txt}`.
Private scratch (not committed): `~/dev/ssx3-work/N8D7M12P5F4/{build/,mac-pktseq/}`.

Gaps: PrivWrite content absent (opaque callable); 64-bit digest is a diagnostic sample of hashed
fields, never proof of full command or GPU execution identity; added hashing may perturb timing;
`emit_stdout_only` is structural (single stdout-only emission site, never into `rows`/`OUT`).
Cleanup: lease slot 1 released (both slots free); no runner process remains; own PID only, no pkill.
