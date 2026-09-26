# HP1 — two hot-path fixes on Android: dev-trace string formatting and emulated TLS (local Qwen, 1.5 h)

## Goal
The Odin race profile (N12, VK1) shows two avoidable costs on the game thread in release builds: `snprintf` (~1 % of samples) and `__emutls_get_address` (~0.7 %). The orchestrator already found both causes. Make the two exact edits below, prove nothing else changed, and hand back the table. Do not change anything else.

## Facts (verified by the orchestrator; cite them, don't re-derive)
- Call chain (VK1 Odin profile, `simpleperf report -g callee`): `snprintf` ← `PS2Memory::processVIF1DataImpl` ← `processVIF1Data` ← `processPendingTransfers` ← `writeIORegister` ← `Store32` ← guest code. In `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`, three blocks format strings with `std::snprintf` and then call `e37AppendVif(...)`, which returns immediately unless `ps2_vu1_entry_trace::enabled()` (`ps2_vif1_interpreter.cpp:26-35`; `enabled()` at `ps2xRuntime/include/ps2_vu1_entry_trace.h:279`). The three blocks (line numbers at fork `173b31f`; confirm with `lsp`/grep):
  1. MSCAL, about line 560: `char addr[16]; std::snprintf(addr, …, "%u", imm); … e37AppendVif(mname, …);` — **the `ps2_vu1_entry_trace::noteMscalEntry(...)` call in the same block must stay unconditional.**
  2. MPG, about line 744: the whole `{ char addr[16]; … e37AppendVif("MPG", …); }` block.
  3. UNPACK, about line 1127: the whole `{ char addr[24]; … e37AppendVif("UNPACK", …); }` block.
- Emulated TLS: `android/app/build.gradle:21` has `minSdk 28`. The NDK uses native ELF TLS only when minSdk ≥ 29; at 28 every `thread_local` goes through `__emutls_get_address` (hot users: `ps2_runtime.cpp:186` `g_dispatchHistory`, `gs_frontend.cpp:165`, `runtime/ee_guest_unwind.h:15`). The Odin runs API 35.

## Edits (fork worktree `~/dev/ssx3-work/HP1/PS2Recomp`, local branch `hp1` from fork `ssx3` `173b31f`)
Create it with: `git -C ~/dev/PS2Recomp fetch fork && git -C ~/dev/PS2Recomp worktree add -b hp1 ~/dev/ssx3-work/HP1/PS2Recomp fork/ssx3`.
- Commit 1 `[HP1] VIF1: skip E37 string formatting when the entry trace is off`: wrap the snprintf + `e37AppendVif` parts of blocks 1–3 in `if (ps2_vu1_entry_trace::enabled()) { … }`. Nothing else in those functions changes.
- Commit 2 `[HP1] Android: minSdk 29 for native ELF TLS`: `minSdk 28` → `minSdk 29`. Check for any `ANDROID_PLATFORM`/`android-28` in `android/` CMake/gradle files and list them in the report (change them to 29 only if they set the same thing).

## Checks (acceptance is by these commands, not by judgment)
1. `git diff --stat fork/ssx3 hp1` shows only `ps2_vif1_interpreter.cpp` and the gradle file(s). `git diff --stat 14b1e5cb hp1 -- ps2xRuntime/src/runner` is empty.
2. Mac build + suite: `local/tooling/build/mac_build.sh ~/dev/ssx3-work/HP1/PS2Recomp ~/dev/ssx3-work/HP1/build --det`, then from the worktree root `../build/ps2xTest/ps2x_tests` → record the pass count (all must pass).
3. One det boot on bradflix and compare (runner must be built there: `local/tooling/build/bradflix_build.sh` needs a pushed SHA, so instead boot the **Mac** det runner on the mini with one lease slot): `python3 local/tooling/boot/ssx3_boot.py --mode det --backend parallel --runner ~/dev/ssx3-work/HP1/build/ps2xRuntime/ps2EntryRunner --label HP1 --stop-tick 2400 --route fr1r1 --vu1-stats --dump-ticks 1090,1800,2100 --out ~/dev/ssx3-work/HP1/run/HP1`, then `python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/HP1/run/HP1` → must print IDENTICAL.
4. No Android build, no Odin (the orchestrator folds this into the next device build).

## Rules
Only the files above. Never push; never `git add -f` in the fork. Workers don't edit `docs/`. On the first failure, stop, save the error to `local/research/HP1/error.txt` and hand back.

## Deliverable
`local/research/HP1/REPORT.md`: a table with the two fork commits (SHA + subject), the diff stat, the suite count, the compare line, the runner SHA-256, and the list from the minSdk check. Commit `[HP1] …` with explicit paths (`git add -f local/research/HP1/REPORT.md`), trailer `Orchestrated-By: opencode`. No push. Hand back the table; don't conclude.
