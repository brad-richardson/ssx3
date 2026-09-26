# HP1 — two hot-path fixes on Android: dev-trace string formatting and emulated TLS

Worker: local Qwen via opencode (brief `local/muse/prompts/HP1.md`).
Fork: `brad-richardson/PS2Recomp`, base `fork/ssx3` = `173b31f`, worktree `~/dev/ssx3-work/HP1/PS2Recomp` branch `hp1`.

**STOPPED ON FIRST FAILURE: permission denial.** File edits in the fork
worktree are outside this worker's workspace and were denied by the
permission rule `{"permission":"edit","pattern":"../*","action":"deny"}`
(full denial text in `error.txt`). Per WORKER-RULES-v2 the denied action
was not retried via another route. No fork commit, no build, no boot.
Read-only checks below were completed before stopping.

## Table

| Item | Value |
| --- | --- |
| Fork commit 1 | not made — edit of `ps2_vif1_interpreter.cpp` denied (see `error.txt`) |
| Fork commit 2 | not made — edit of `android/app/build.gradle` would be denied (same rule; not attempted) |
| `git diff --stat fork/ssx3 hp1` | empty (worktree unmodified at `173b31f`) |
| `git diff --stat 14b1e5cb hp1 -- ps2xRuntime/src/runner` | empty |
| Mac `--det` build | not run (blocked before edits) |
| `ps2x_tests` pass count | not run |
| Runner SHA-256 (`ps2EntryRunner`) | not found (no build) |
| Boot compare line | not run (no mini lease claimed) |
| minSdk check list | `android/app/build.gradle:21` `minSdk 28` — only occurrence in `android/`; no `ANDROID_PLATFORM`, no `android-28`/`android-29`, no CMake files under `android/` |

## Commands (exact, in order)

| # | Command | Result |
| --- | --- | --- |
| 1 | `git -C ~/dev/PS2Recomp fetch fork && git -C ~/dev/PS2Recomp worktree add -b hp1 ~/dev/ssx3-work/HP1/PS2Recomp fork/ssx3` | success — `branch 'hp1' set up to track 'fork/ssx3'`, HEAD `173b31f` |
| 2 | `git -C ~/dev/PS2Recomp diff --stat fork/ssx3 hp1` | empty, rc=0 |
| 3 | `git -C ~/dev/PS2Recomp diff --stat 14b1e5cb hp1 -- ps2xRuntime/src/runner` | empty, rc=0 |
| 4 | `grep -rn "ANDROID_PLATFORM" ~/dev/ssx3-work/HP1/PS2Recomp/android` | no match, rc=1 |
| 5 | `grep -rn "android-28\|android-29" ~/dev/ssx3-work/HP1/PS2Recomp/android` | no match, rc=1 |
| 6 | `grep -rn "minSdk" ~/dev/ssx3-work/HP1/PS2Recomp/android` | one match: `android/app/build.gradle:21` `minSdk 28` |
| 7 | `find ~/dev/ssx3-work/HP1/PS2Recomp/android -name CMakeLists.txt -o -name "*.cmake"` | no CMake files under `android/` |

Line numbers for the three VIF1 blocks were confirmed by grep/read at
`173b31f` before the denial (match the brief): MSCAL `snprintf` at
`ps2_vif1_interpreter.cpp:563`, `e37AppendVif` at `:565`, `noteMscalEntry`
at `:567-568`; MPG block `:744-753` (`snprintf` `:746`, `e37AppendVif`
`:751`); UNPACK block `:1129-1152` (`snprintf` `:1131/:1136/:1141/:1144`,
`e37AppendVif` `:1149`). `enabled()` confirmed at
`ps2xRuntime/include/ps2_vu1_entry_trace.h:279`; `noteMscalEntry`'s own
early-return at `:325-328`. The intended edit (not applied) wraps the
snprintf + `e37AppendVif` portions in `if (ps2_vu1_entry_trace::enabled())`
with `noteMscalEntry` left unconditional.

## Gaps

- Neither fork commit exists; the `hp1` branch is at the `fork/ssx3` tip
  with a clean tree, so a rerun can resume at edit 1 (skip `worktree add`
  — the branch already exists).
- Build, suite, boot and compare all pending; the boot compare target is
  unchanged: `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`.
- Unblock: relaunch the worker with an edit permission covering
  `~/dev/ssx3-work/HP1/**` (per-worker exception via `OPENCODE_CONFIG_CONTENT`,
  see `error.txt`), or point the brief's worktree inside `~/dev/ssx3`.
