# E55D14 Part 1B — default-off GetDir path tap (fork worktree resume)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D14P1B.md`
(resume inside the fork worktree left clean at E55D3 base by Part 1).
Outcome: **A — source/tests/build and runner guard pass.**

## Acceptance table

| Item | Value |
| --- | --- |
| A source/tests/build + runner guard | **MET** — 3 named files patched; Release/Ninja build OK (1 repair rebuild for a new-code test failure, no compile error); full suite 693/693 incl. 9/9 probe tests; runner double-SHA match; runner-dir diff vs `14b1e5cb` empty; codegen untouched |
| B bounded compile/test failure row | NOT TAKEN — no compile failure; one interim test failure (`getdirpath tiny cap`) diagnosed, fixed in the named header, rebuilt, now passing (row below) |
| OTHER permission/pin/resource mismatch | NOT TAKEN — pin `bab6eb382673155ffd756fe8db265964eeff9703` + branch `e55d14p1-getdir-path` + clean status all matched; `edit` inside the worktree allowed; disk 150.4/200 GB, lane 1.9/3 GiB |

## Interim failure (fixed, not a compile break)

- After the first green build, the full suite was 692/693: new test
  `getdirpath tiny cap yields one cap line and no partial record` failed
  (probe stayed armed, no cap line). Cause: `noteGetDirPath` delegated its
  over-cap path to `emitRecordLocked(s, "", ...)` whose 1-byte empty record
  still fit under the cap, so a blank line was written instead of the cap
  line with no disarm. Fix (header only): the sibling's over-cap path now
  emits the single `cap` line directly and disarms permanently, mirroring
  `emitRecordLocked`'s cap block. Existing `getdir`/pad/mcread code untouched.
  Rebuilt (`build-repair.log`, exit 0) and reran: 693/693.

## What was implemented (one default-off sibling tap)

- `ps2xRuntime/include/ps2_e55d3_pad_card_probe.h`
  - New `getdirpath` line: `getdirpath seq=<s> vsync=<t> pord=<p> port=<p>
    slot=<sl> max=<m> rawLen=<r> raw="<esc>" query="<esc>" parent="<esc>"
    pattern="<esc>" host="<esc>"`, shared `seq`, own `pathOrd` (`pord`).
  - Escaping: `\`→`\\`, `"`→`\"`, all other bytes outside 0x20–0x7E as
    `\xHH`; each escaped field capped at 1024 chars (whole line ~5 KiB);
    whole-or-nothing against the same 16 MiB `kByteCap` + 256 B reserve,
    one `cap` line then permanent disarm, flush every 16. Disabled cost is
    the single `armed()` relaxed-atomic (no string build when off).
  - `configureForTest`/`clearForTest` reset `pathOrd`.
- `ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp` (`sceMcGetDir` only)
  - Sibling emitted before the existing status tap on the `unformatted` and
    `bad-port` early exits with `rawPath` + `"-"` sentinels for
    query/parent/pattern/host (no normalization moved into those branches).
  - One sibling after `hostDir.lexically_normal()` covering
    no-dir/empty/ok/bad-addr with `(rawPath, guestQuery, parentRel,
    pattern, hostDir)`. Read-only: no RDRAM/result/sort/copy change.
- `ps2xTest/src/ps2_e55d3_probe_tests.cpp`
  - Ordering test updated for the sibling shift (pad seq1 / getdirpath seq2
    pord1 / getdir seq3 / mcread seq4; per-family ords all 1).
  - New: disabled-getdir silence, normal-path fields, escaping + field cap,
    early-exit sentinels (bad-port via stub; unformatted via
    unformat/query/reformat), `pord` 1..3 ordering, sibling tiny-cap.

## Pins

- Fork base: `bab6eb382673155ffd756fe8db265964eeff9703` (verified `rev-parse`
  match at start; branch `e55d14p1-getdir-path`; status clean at start).
- Fork commit: `[E55D14] Part 1B` (this worktree; `Orchestrated-By: opencode`,
  no push) — see `git log -1`.
- Runner SHA256 (double read, match):
  `d8fa114d824a277592558425dd91357bcf2f75d0d09390a5680c41ba6002ef04`
  (`.work/build/ps2xRuntime/ps2EntryRunner`).
- Runner guard: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`
  empty (exit 0).
- Codegen: external `/Users/brad/dev/ssx3-work/codegen-ssx3` read-only
  (`PS2X_GAME_CODEGEN_DIR`); no writes issued there.
- Build pins: Release/Ninja, clang/clang++ 23.1.1
  (`/opt/homebrew/opt/llvm/bin`), `PS2X_ENABLE_DIAG_TAPS=ON`,
  `PS2X_ENABLE_DET_HASH_TAP=ON`, `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`,
  `PS2X_ENABLE_RUNTIME_LOGS=OFF`, `FETCHCONTENT_SOURCE_DIR_*` under
  `/Users/brad/dev/ssx3-work/E50/build/_deps/` (same recipe as E55D3
  `build-taps`; configure log notes the same 4 unused-cli vars).
- Tests: full suite from the fork root with `PS2X_PAD_CARD_PROBE` unset
  (`env -u`): Total 693, Passed 693, Failed 0; probe block 9 passed 0 failed.
- Disk: 150.4 GB / 200 GB cap after (148.7 before; under cap). Lane
  `~/dev/ssx3-work/E55D14P1` 1.9 GB (build 1.7 GB) under the 3 GiB lane cap.
  Receipt texts ~178 KiB total (< 512 KiB).
- Boots/builds/runs: 0 boots; 1 configure + 1 build + 1 repair rebuild;
  2 full-suite runs (692/693 interim, 693/693 final).

## Commands run (exact, from the fork root)

- `git rev-parse HEAD` → `bab6eb3…`; `git branch --show-current` →
  `e55d14p1-getdir-path`; `git status --short` (clean); `git diff --stat
  14b1e5cb -- ps2xRuntime/src/runner` (empty).
- `mkdir -p .work/receipts .work/build`; `~/dev/ssx3/local/tooling/disk_budget.sh`.
- `cmake -S . -B .work/build -G Ninja -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF
  -DPS2X_ENABLE_DIAG_TAPS=ON -DPS2X_ENABLE_DET_HASH_TAP=ON
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
  -DFETCHCONTENT_SOURCE_DIR_*=$D/…` → exit 0 (`cmake-configure.log`).
- `cmake --build .work/build --parallel 8 --target ps2x_tests
  ps2EntryRunner` → exit 0 (`build.log`); repair rebuild → exit 0
  (`build-repair.log`).
- `env -u PS2X_PAD_CARD_PROBE ./.work/build/ps2xTest/ps2x_tests` →
  interim exit 1 (692/693), final exit 0 (693/693) (`suite.log`).
- `shasum -a 256 .work/build/ps2xRuntime/ps2EntryRunner` ×2 (match);
  `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` (empty);
  `du -sh ~/dev/ssx3-work/E55D14P1` (1.9G); `disk_budget.sh` (150.4/200).
- `python3 .work/receipts/check.py` → ALL PASS (post-commit).
- `git add ps2xRuntime/include/ps2_e55d3_pad_card_probe.h
  ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp
  ps2xTest/src/ps2_e55d3_probe_tests.cpp` + commit `[E55D14] Part 1B`,
  no push; `git status --short` confirms `.work/` still untracked.

## Gaps (stated plainly)

- No guest query is claimed: the tap is built and unit-tested, but no boot
  ran in this part, so the tick1740 raw/pattern remains unobserved.
- No save-validity, card-determinism or speed claim is made.
- The pre-existing status-line over-cap delegation (`emitRecordLocked(s,
  "", …)` writing a blank line instead of `cap` when the empty record still
  fits) was left untouched as out-of-scope existing behavior; only the new
  sibling writes its cap line directly.
- The empty-card boot reusing E55D12's script belongs to the separate worker
  part after the orchestrator gate.
