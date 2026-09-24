# N8D7M12 Part 5F4P3 — remove diagnostic cost when disabled (COMPLETE)

**State: COMPLETE. One minimal source fix, one validation pass (1 incremental build + 1 suite + 1 same-stream Mac OFF replay, one mini-lease slot). No Android build, no Odin, no push, no upstream contact. No Android/GPU verdict; no wall-time speed is quoted.**

Brief: `/Users/brad/dev/ssx3/local/muse/prompts/N8D7M12P5F4P3.md`. Sources read in full:
`~/dev/AGENTS.md`, `~/dev/ssx3/AGENTS.md`, `~/dev/ssx3/local/AGENTS.local.md`,
`local/muse/prompts/N8D7M12P5F4P2.md` (via ssx3),
`local/research/N8D7M12P5F4P2/{REPORT.md,ORCH-GATE.md}` (via ssx3).
Citations are local source, not web. REPORT was written early with `not found` cells and refined after.

## 1. Pins

| Item | Value |
| --- | --- |
| Fork worktree | `/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp`, branch `n8d7m12-p5f4` |
| Fork base / HEAD (pre-commit) | `679968143763444291ca83505babe7e8a17b86f0` (`6799681`, gated P2) |
| Reference stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs`, 1100696462 B, SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` (two matching `shasum` reads before use) |
| New binary | `~/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests`, SHA `3b21ce6149b3e4b6ddb6757589cb0b6a688c553d016d53bcd8fb2221cbd56153` (two matching reads after build) |
| Private scratch | `~/dev/ssx3-work/N8D7M12P5F4/{build/ (P2 reuse, 1.4 GiB),mac-fastoff/ (new, 6.2 MiB)}` |
| Prior Mac ON control | `parallel.hashes` SHA `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290`; tick2050 PPM SHA `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` |
| Toolchain idle | no `ninja`/`clang` build procs before build (only clangd LSP); both P-lane slots free before claim |
| Private bytes / receipts | ~6.2 MiB new private bytes (≤2 GiB cap); receipt text ~110 KiB (≤256 KiB cap) |

## 2. Gate finding and fix

Gate (`ORCH-GATE.md`): `GS::executeQueuedCommand` unconditionally calls `noteConsumedCommand`; that function locked `m_pktSeqMutex` **before** checking the default-off gate, so OFF still locked once per consumed command.

Fix (only `ps2xRuntime/include/runtime/gs/gs_frontend.h`, `ps2xRuntime/src/lib/gs/gs_frontend.cpp`; +32/−14):

| Piece | Change |
| --- | --- |
| Flag | `bool m_pktSeqEnabled = false` → `std::atomic<bool> m_pktSeqEnabled{false}` + comment |
| Per-command path (`noteConsumedCommand`) | relaxed fast check `if (!load(relaxed)) return;` **before** `lock_guard`; guarded re-check `if (!load(relaxed)) return;` **after** locking; ON digest/count/Fence logic byte-identical below |
| Quiescent `drainQueue` | same pattern: fast check before mutex, re-check under lock, then copy running→snapshot (ON only) |
| Setter / getter | `setPktSeqEnabled` locks, then `store(enabled, relaxed)` + same digest/snapshot reset as before; `pktSeqEnabled()` is now a lock-free relaxed load |
| Call site (`executeQueuedCommand`) | comment only; still calls `noteConsumedCommand` first so ON sees prior-consumed `m_curGifPath` |

Why OFF does not acquire the mutex per command: while disabled the relaxed atomic load returns false, so `noteConsumedCommand` returns before constructing the `lock_guard`; the mutex is only taken when the flag reads true, and the guarded re-check under lock covers a concurrent toggle (setter holds the same mutex while storing). The replay sets the flag before worker start (`gs_replay_core.cpp:226` before `setQueueEnabled(true)`), giving a worker-start happens-before in the pinned replay. ON retains exactly the prior FNV-1a-64 field encoding, Fence snapshot-only rule, PrivWrite kind-only rule, sampled `GB4_PKTSEQ` grammar and default-off silence. No queue refactor, no broader instrumentation.

## 3. Validation

| Check | Result |
| --- | --- |
| `git diff --check` / changed-path list | PASS, clean; exactly `gs_frontend.h`, `gs_frontend.cpp` |
| Runner-dir diff `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` | empty |
| One incremental Ninja build `ps2x_tests` | rc=0 (pre-existing warnings only: vu1 `snprintf`, `System.cpp` format, `psm` switch, one known ld duplicate-library warning) |
| One suite from fork cwd | **586/586/0** PASS, incl. `pktseq fingerprint is stable [Passed]` |
| One pinned-stream OFF replay, exit 0, one P-lane slot (claimed 1, released; both free after) | PASS, log 4,814,937 B full in private scratch; excerpt (44 lines: 0 PKTSEQ + 41 replay + frame + summary + stats) in receipts; output tree 6.2 MiB |
| `PS2X_GS_REPLAY_PKTSEQ` | **unset** via `env -u`; `GB4_PKTSEQ` lines = 0 |
| Existing replay rows | exactly 41 `GB4_REPLAY tick=`, ticks 50…2050 ordered |
| Parser counts | packets 862958, priv 11499, transfers 25445, markers 2050, samples 41 — equal to P2/Part 1 |
| `parallel.hashes` vs pinned Mac ON | byte-identical (`cmp` clean), SHA `94b433df…10c290` |
| tick2050 PPM vs pinned Mac ON | byte-identical (`cmp` clean), SHA `9490484c…14fce3e`; frame `present=d19b96fe` |
| Two matching SHA reads (binary + stream) | PASS (binary `3b21ce61…`, stream `f6a78f71…`) |
| `check.py` | verdict **PASS** (`check-result.json`), 32/32 |

No diagnostic wall time is quoted as speed. No retry: exactly one build, one suite, one replay. No tuning loop.

## 4. Exact commands (worktree = start folder unless noted)

```sh
git branch --show-current && git rev-parse HEAD && git status --porcelain  # n8d7m12-p5f4, 6799681, only local/receipts untracked
shasum -a 256 ~/dev/ssx3-work/N8D7M6/n8d7m6.gs  # twice, f6a78f71… (before use)
ninja -C /Users/brad/dev/ssx3-work/N8D7M12P5F4/build ps2x_tests  # rc=0, log to local/receipts/N8D7M12P5F4P3/build.log
/Users/brad/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests  # workdir=worktree; rc=0, 586/586/0, log to receipts/suite.log
shasum -a 256 /Users/brad/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests  # twice, 3b21ce61…
python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py claim n8d7m12p5f4p3  # -> slot 1
env -u PS2X_GS_REPLAY_PKTSEQ PS2X_GS_REPLAY_CAPTURE=.../N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_N8D7F_SELECTED_CAPTURE=1 PS2X_N8D7L_ORACLE=1 PS2X_N8D5_TILE_CAPTURE=1 \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 \
PS2X_GS_REPLAY_PPM_DIR=.../N8D7M12P5F4/mac-fastoff/frames \
PS2X_GS_REPLAY_OUT=.../N8D7M12P5F4/mac-fastoff/parallel.hashes \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib \
  .../build/ps2xTest/ps2x_tests > .../mac-fastoff/replay.log 2>&1  # workdir=worktree, own PID; rc=0
grep -E "^(GB4_REPLAY tick=|GB4_FRAME|GB4_REPLAY_SUMMARY|GB4_PARALLEL_STATS|GB4_PKTSEQ)" .../mac-fastoff/replay.log > local/receipts/N8D7M12P5F4P3/replay-excerpt.txt
cmp .../mac-fastoff/parallel.hashes .../mac-pktseq/parallel.hashes  # byte-equal
cmp .../mac-fastoff/frames/vq-002050.ppm .../mac-pktseq/frames/vq-002050.ppm  # byte-equal
python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py release 1  # both slots free
python3 local/receipts/N8D7M12P5F4P3/check.py  # verdict PASS 32/32
```

## 5. Deviations

- None. No exploratory-command typo; the one `python3 -c` SHA attempt in planning errored without writing and was replaced by two `shasum` reads (not a brief-step failure).

## 6. Handback table

| Condition | Outcome | Next action |
| --- | --- | --- |
| OFF fast check before mutex + guarded re-check; ON digest/count/Fence/grammar/silence preserved; 586/586/0; 0 `GB4_PKTSEQ` + 41 replay rows; hashes/PPM byte-equal to Mac ON | **PASS, no Android claim** | Orchestrator gates any same-settings Odin pair separately; per P2/ARCH1, equal digest with differing output ends input-hash expansion (downstream state/readback probe), a differing digest calls for delivery investigation |
| Any GPU-cause reading from this part | none — host-only default-off cost removal; OFF output equality cannot prove GPU execution, PrivWrite contents, or a GPU cause | — |

Private fork commit: source-only `[N8D7M12] Part 5F4P3` with `Orchestrated-By: opencode`, no push (see §7).

## 7. Receipts (untracked on disk, never added to the fork commit)

`local/receipts/N8D7M12P5F4P3/{REPORT.md,check.py,check-result.json,replay-excerpt.txt,build.log,suite.log}` (`*.log` git-ignored but present for orchestrator copy).
Private scratch (not committed): `~/dev/ssx3-work/N8D7M12P5F4/{build/,mac-fastoff/}`.

Gaps: PrivWrite content absent (opaque callable, kind-only by design); 64-bit digest is a diagnostic sample of hashed fields, never proof of full command or GPU execution identity; ON hashing may perturb timing (OFF now avoids the per-command mutex); `emit_stdout_only` unchanged from P2 (single stdout-only emission site).
Cleanup: lease slot 1 released (both slots free); no runner process remains; own PID only, no pkill.
