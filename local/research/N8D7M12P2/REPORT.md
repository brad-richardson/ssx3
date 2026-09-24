# N8D7M12 Part 2 — dev-only Android replay entrypoint (source only)

**State: COMPLETE, outcome A (source only). No build, replay, APK transfer,
stream copy, Odin/iOS action, lease, push, board/global edit, upstream
contact, or generated guest code. No Android compile, loader, or runtime
behavior is proven or concluded.**

Brief: `local/muse/prompts/N8D7M12P2.md`. Goal: the single default-off
Android NativeActivity replay branch from N8D7M11 §7, calling the Part 1
shared core (`ps2x_gs_replay_run()`).

## 1. Pins

| Item | Value |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7M12P2/PS2Recomp`, branch `n8d7m12-app` |
| Fork base / HEAD | `24801bc` (Part 1) / `a608ed1` (`[N8D7M12] Part 2` + drain correction, `Orchestrated-By: opencode`, no push) |
| Part 1 gate | `local/research/N8D7M12/ORCH-GATE-P1.md` (A, desktop parity) |
| Design gate | `local/research/N8D7M11/ORCH-GATE.md` (A, design only) |
| Scope | `ps2xRuntime/src/main.cpp` only (+67/−0, bounded hunk vs `24801bc`) |
| Runner-dir diff vs `14b1e5cb` | empty (0 lines) |

## 2. Implementation (N8D7M11 §7 item 3)

Single `#if defined(__ANDROID__)` branch, first statement inside `try` in
`main()`, after `redirectStdioToLogcat()`/`setupTerminateLogger()` and
before `getExecutablePath`, `PS2Runtime` construction, `initialize`,
`loadELF`, and `run` — so no live EE/game thread starts in replay mode:

- **Entry key (default off):** only `PS2X_GS_REPLAY_ONDEVICE=1`
  (`getenv` + null guard + `strcmp == "1"`) enters. Unset, empty, `0`, or
  any other value falls through to the byte-identical game boot path.
- **Strict gates (explicit reject, no silent CPU/system-Vulkan fallback):**
  nonempty `PS2X_GS_REPLAY_CAPTURE`, `PS2X_GS_REPLAY_BACKEND=parallel`,
  `PS2X_GS_TURNIP=1`. Any mismatch prints one
  `[n8d7m12] replay rejected: ...` line and `_Exit(1)`.
- **Core call:** Part 1 `ps2x_gs_replay_run()`; result flags mapped to one
  `[n8d7m12] replay ok: packets=… markers=…` line with `_Exit(0)`, or one
  `[n8d7m12] replay failed: open=… header=… backend=… parse=… stream=…
  samples=…` line with `_Exit(1)`. Gate requires `!skipped` and all of
  `openOk/headerOk/rtzOk/pathFileOk/wordsOk/backendOk/parseOk/
  packetTraceOk/outOk/expectOk/hasStream/hasSamples`.
- **Exit pattern:** `std::cout.flush(); std::cerr.flush();` then
  `stopLogcatRedirect()` (drains/joins the logcat pipe reader so the
  tick2050 census/end-marker receipt reaches logcat — `_Exit` bypasses the
  `atexit` registration), then `std::_Exit(...)`. Drain runs on all three
  replay exit sites (reject, ok, fail); the default-off game boot path
  keeps its original flush + `_Exit` with no added call. Drain safety:
  idempotent on failed init (`pipe()` fail → fds stay `-1`, no thread;
  `atexit` fail → fds already closed, thread already joined; close errors
  ignored) and exactly one call per process (reject `_Exit`s before the
  result path; `_Exit` never re-runs `atexit`). No unsafe case found.
- **Unchanged:** manifest (zero `uses-permission`, NativeActivity
  `ps2EntryRunner`), Gradle, CMake (Part 1 already compiles the core into
  `ps2_runtime`, which `ps2EntryRunner` links — no new binary/target),
  Turnip/HAL, game code. Key and capture path arrive via the proven
  `ps2x.env` static-init shim (`ps2_android_runtime.cpp:12-49`), which runs
  before `main()` reads anything.

## 3. Validation (A, static only)

`check.py` (50 checks, all PASS, verdict A — see `check-result.json`):
pinned branch/base advance, diff touches only `main.cpp` (67 insertions,
≤80 cap), single `getenv` entry, strict `== "1"`/`parallel`/`"1"` gates,
nonempty capture, core call, all 13 result fields, ok/fail lines and exit
codes, `__ANDROID__` guard, flush + drain + `_Exit` on both replay exit
sites with the game-boot path drain-free, branch line after
`setupTerminateLogger()` and before all five game-boot calls, boot path
intact with no `#else`, no manifest/Gradle/CMake/`add_executable` change,
runner-dir diff empty.

## 4. Exact commands (repo root unless noted)

```sh
touch ~/dev/ssx3-work/N8D7M12P2/.sentinel_n8d7m12p2 && rm ~/dev/ssx3-work/N8D7M12P2/.sentinel_n8d7m12p2  # write-scope check
# edit: ps2xRuntime/src/main.cpp (+1 include, +58 branch) in worktree
git -C ~/dev/ssx3-work/N8D7M12P2/PS2Recomp diff --stat 24801bc -- .  # 1 file, +59
python3 local/research/N8D7M12P2/check.py  # A, 47/47 (first run B 45/47 pre-commit + comment-literal count; fixed checker, committed, reran A)
git -C ~/dev/ssx3-work/N8D7M12P2/PS2Recomp commit -m "[N8D7M12] Part 2 ..."  # 1a5e3dc, no push
```

## 5. Deviations and correction history

- First `check.py` run was B (45/47): `fork_head_advances_base` failed
  (fork commit not yet made — by design, checker ran before commit) and
  `key_single_occurrence` counted the key literal in the code comment.
  Fixed the checker to count the single `getenv(...)` entry (the
  meaningful single-branch condition), committed the fork (`1a5e3dc`),
  reran A 47/47. No source change from this loop.
- Source-review correction (no amend): the first commit flushed iostreams
  then `_Exit`ed, bypassing `atexit(stopLogcatRedirect)` with census lines
  possibly still in the pipe. Added `stopLogcatRedirect()` after the
  flushes on both replay exit paths (commit `a608ed1`), extended the
  checker with `replay_drain_calls` / `drain_before_replay_exits` /
  `default_off_no_drain`, reran A 50/50. Safety review found no unsafe
  case (§2).
- `check-result.json` first landed at the repo root (checker cwd); moved
  into `local/research/N8D7M12P2/` before the ssx3 commit (reruns execute
  with the evidence dir as cwd so the receipt lands there directly).

## 6. Receipts

- ssx3 (this dir): `REPORT.md`, `check.py`, `check-result.json`,
  `result.json`, `fork-n8d7m12p2.patch` (4,274 B) — `[N8D7M12] Part 2
  source` commit(s), no push.
- Fork: `[N8D7M12] Part 2` commit `1a5e3dc` plus drain correction
  `a608ed1` on `n8d7m12-app`, no push, no amend.

## 7. Gaps / handback

- Source strings cannot prove Android compile (NDK/CMake), Turnip/HMI
  loader behavior in the replay-mode path (N8D7M11 G1 carried), or runtime
  output. No build/device verdict from this part.
- Recommended next action (orchestrator decision): gate the Android
  build/package and OFF-path behavior, then stage the pinned stream for a
  separately gated Odin run.

| Condition | Outcome | Next action |
| --- | --- | --- |
| Source branch with all checks | **A (this report)** | Gate Android build/OFF-path, then staged Odin run |
| One source condition missing | B (state smallest fix) | Fix and re-run `check.py` |
| Pin/permission mismatch | OTHER | Void; diagnose pin or scope first |
