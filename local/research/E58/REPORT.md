# E58 — fold and regeneration; Part 2 stopped at suite failure

Worker: Codex. Brief: `local/muse/prompts/E58.md`. The orchestrator decides. No fork push or codegen promotion was attempted. Part 1 stopped at a missing logger; after approval, Part 2 added it, built, and stopped at the first suite failure.

## Fold

Worktree: `~/dev/ssx3-work/E58/PS2Recomp`, local branch `e58-fold`, base `eac6cba`, Part-1 HEAD `c34d9c6a46592e2ac6830ea3ff26c90500b5beef`, Part-2 HEAD `50fe0a7`. All fold commits are local only; no generated guest code entered the fork. `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty.

| Order | Source | New SHA | Conflicts/resolution |
| --- | --- | --- | --- |
| 1 | `96fc89b` | `ee61374` | None (`git cherry-pick -x`) |
| 2 | `d3f7508` | `f4ba160` | None (`git cherry-pick -x`) |
| 3 | N5 tap guard `6c335e6` diff | `d050b6a` | `git apply` cleanly; changed CMake and standalone-header defaults to OFF on all platforms, as E58 requires |
| 4 | `73b8b3a` | `e09bb29` | Only `ps2xTest/CMakeLists.txt` and `ps2xTest/src/main.cpp` test registration conflicted. Kept `ps2_present_fallback_tests` registration and omitted I25's absent `ps2_env_file_tests` registration; then `git cherry-pick --continue` |
| 5 | `104dd7f` | `c34d9c6` | None (`git cherry-pick -x`) |

## Regeneration and inputs

| Item | Result |
| --- | --- |
| ELF `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72` SHA-256 reads 1 / 2 | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` / same |
| Function map in E58 worktree SHA-256 reads 1 / 2 | `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba` / same |
| Command | `/Users/brad/dev/ssx3-work/E52/build/ps2xRecomp/ps2_recomp /Users/brad/dev/ssx3-work/E58/ssx3-e58.toml > /Users/brad/dev/ssx3-work/E58/regen.log 2>&1` from E58 fork worktree |
| Result | Success: 9,454 functions processed, 9,278 recompiled, 176 stubs, 0 decode failures |
| Codegen | `~/dev/ssx3-work/codegen-ssx3-e58`, 273 MB |
| E53 comparison | `diff -qr codegen-ssx3-e53 codegen-ssx3-e58` produced **0 differences** (`~/dev/ssx3-work/E58/codegen-diff.txt`) |

The E58 toml is the folded fork toml with only the three absolute input/map/output paths pointed at the internal-disk inputs and E58 output. The E52 recompiler binary is the one used by E53's recorded regeneration; the folded translator source matches E53 and the E58 output matches E53 byte-for-byte.

## Failed brief-step preflight

Step 4 requires guest vsyncs/s from `[vsync-rate]` with `PS2X_VSYNC_RATE_LOG=1`. The folded worktree has **no implementation** of that environment variable or log line (`rg` in runtime and tests finds none). The line lives in the separately recorded N5 local patch `local/research/N5/logs/vsync-rate-1669d50.diff` (I25 origin `31d988d`), which E58 did not authorize for folding. Receipt: `local/research/E58/rate-preflight.txt`.

This makes the required clean-build Mac rate table impossible from the specified five-commit fold. Per the worker first-failed-step rule, I stopped before the build and boots. I did not add the unlisted logger, run a potentially noncompliant measurement, push, or promote codegen.

## Remaining checks

| Check | Result |
| --- | --- |
| Release build / suite | Not run after step-4 preflight failure; count not found |
| Runner SHA read 1 / read 2 | Not found / not found |
| Guest `.text` | E58 not found; E53 diagnostic runner Mach-O `__TEXT,__text` = 352,227,992 bytes (`xcrun size -m`) |
| Select Character screenshot / visual check | Not run |
| Race screenshot / visual check | Not run |
| Vsyncs/s, clean build, Mac | Not found; logger absent from folded source |
| Host load during boot | Not applicable. During preflight AU3 and GB4 clang/ninja builds were active, so E58 waited rather than starting a competing build. |
| Runner-dir check | Empty (`rate-preflight.txt`) |
| Fork push | Not attempted |
| Codegen promotion / final disk check | Not attempted; preflight disk check 82.1 / 200 GB, E58 work dir 22 MB + codegen 273 MB |
| Budgets | 0/3 builds, 0/3 boots; new bytes about 295 MB including codegen |

## Recommended next action

The orchestrator should amend the fold to include the env-gated rate logger (I25 `31d988d` or the N5 patch), then rerun E58 from this local worktree: build, suite, both smoke views, clean rate boot with both leases, runner-dir check, fast-forward push, and codegen promotion. The E58 five-commit fold and matching codegen are ready locally.

---

## Part 2 — orchestrator-approved continuation

Brad's follow-up gate approved one extra fold commit containing only the env-gated vsync-rate logger, ported from I25 via the N5-local patch. The earlier stop remains the Part-1 history above; work resumed at Build step 2.

| Source | New fork SHA | Change |
| --- | --- | --- |
| `local/research/N5/logs/vsync-rate-1669d50.diff` (`31d988d` origin) | `50fe0a7` | Exactly 23 added lines in `ps2xRuntime/src/lib/ps2_runtime.cpp`; `PS2X_VSYNC_RATE_LOG=1` gates one five-second rate line, default off. No other I25 change. |

The ISO `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso` was read twice before use: SHA-256 `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` both times. Host had another clang/ninja job during preflight, so E58 waited before configuring/building.

| Part-2 gate | Result |
| --- | --- |
| Build | **PASS**, 1/3 builds. `~/dev/ssx3-work/E58/build.sh` ran CMake Release with `PS2X_ENABLE_RUNTIME_LOGS=OFF`, `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`, `PS2X_ENABLE_DIAG_TAPS=OFF`, tests ON, E58 codegen. After waiting for all other clang/ninja jobs, `nice -n 10 ninja -j8 ps2x_tests ps2EntryRunner` finished 559/559. Receipts: `cmake.log`, `build.log`, `build/CMakeCache.txt` under E58 workdir. |
| Runner SHA-256 reads 1 / 2 | `f3de8d2cc051c4ac30f8e0e07a84f45eb4889923727627b7416b67c79d251608` / same. |
| Runner Mach-O `__TEXT,__text` | E58 clean **115,045,720 B** vs E53 diagnostic **352,227,992 B** (`xcrun size -m`); 3.06× smaller. This section includes host code as well as guest code; it is a runner text-section comparison, not a guest-only symbol sum. |
| Suite | **FAIL**, 619/632 pass, 13 fail, exit 13. Exact command from fork root: `../build/ps2xTest/ps2x_tests > ../suite.log 2>&1`. All failures are macro-tap trace expectations: 5 in `Ps2E41Trace`, 8 in `Ps2MpgSrcTrace`. With taps OFF, those macro calls compile out. Receipt: `local/research/E58/suite-failures.txt`; full bounded 67,809-byte log: `~/dev/ssx3-work/E58/suite.log`. |
| SC and race smoke frames | Not run: first suite failure stops the brief. 0/3 boots. |
| Clean Mac vsyncs/s | Not found: no boots after suite failure. |
| Runner-dir check | Empty at Part-2 HEAD: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`. |
| Fork ff push | Not attempted: suite gate failed. |
| Codegen promotion | Not attempted: suite gate failed; E58 codegen remains separate. |
| Disk | After build `local/tooling/disk_budget.sh`: **92.5 / 200 GB**, E58 worktree/build 603 MB plus 273 MB codegen. |

### Part-2 stop and recommended next action

The suite is the first failed Part-2 brief step. I made no fix attempt or second suite run, then stopped before either smoke boot and push. The 13 failed tests explicitly require the guest-memory taps that E58 compiled OFF for a clean runner; the other 619 passed. The orchestrator can set a test policy for taps-off builds (for example, gate those 13 tap-specific tests on `PS2X_ENABLE_DIAG_TAPS`, or run a separate taps-on test build), then authorize continuation of the smoke, push, and promotion gates. The clean runner is built and its two SHA reads match.

---

## Part 3 — tap test guard and continuation

Orchestrator approved conditional compilation and registration of the guest-store tap trace suites for `PS2X_ENABLE_DIAG_TAPS=ON`, followed by both suite gates, boots, push, and codegen promotion. The permission denial below stopped this continuation before commit and boots.

| Part-3 gate | Result |
| --- | --- |
| Test guard | `ps2xTest/CMakeLists.txt` conditionally compiles `ps2_mpg_src_trace_tests.cpp`, `ps2_e41_trace_tests.cpp`, `ps2_e43_trace_tests.cpp`, and `ps2_e44_trace_tests.cpp` when `PS2X_ENABLE_DIAG_TAPS=ON`; `ps2xTest/src/main.cpp` conditionally declares/registers the same suites with `#if PS2X_ENABLE_DIAG_TAPS`. E43/E44 also assert on guest-store tap output. No test body changed. Changes remained uncommitted after the denial. |
| Taps-OFF incremental build and suite | PASS. `nice -n 10 ninja -j8 ps2x_tests` in `~/dev/ssx3-work/E58/build`, then `../build/ps2xTest/ps2x_tests` from the fork root: **537/537 passed, 0 failed**. Receipts: `~/dev/ssx3-work/E58/build-part3-off.log`, `suite-part3-off.log`. |
| Taps-ON separate build and suite | PASS. `~/dev/ssx3-work/E58/build-taps.sh` configured Release with `PS2X_ENABLE_DIAG_TAPS=ON`, the same codegen, and built only `ps2x_tests` in `build-taps`; `../build-taps/ps2xTest/ps2x_tests` from the fork root: **632/632 passed, 0 failed**. Receipts: `cmake-taps.log`, `build-taps.log`, `suite-part3-taps.log`, and `build-taps/CMakeCache.txt`. |
| Build budget | Part 2: 1 build; Part 3: 1 incremental test rebuild and 1 separate taps-ON test build; **3/3 total**. |
| Disk preflight | `local/tooling/disk_budget.sh`: **92.4 / 200 GB**, 149 GiB free, before the taps-ON build. No post-build disk check after the denial. |
| Commit gate | **DENIED**. `git add ps2xTest/CMakeLists.txt ps2xTest/src/main.cpp` in the E58 worktree returned exit 128: `fatal: Unable to create '/Users/brad/dev/PS2Recomp/.git/worktrees/PS2Recomp13/index.lock': Operation not permitted`. No retry, escalation, or commit attempted, per the worker denial stop rule. Fork HEAD remains `50fe0a7` as last observed. |
| Smoke boots / clean rate boot | Not run after the denial. 0/3 boots in Part 3; no frames, visual checks, or vsync rates. |
| Runner-dir check / fork push / codegen promotion | Not run after the denial; no push and no promotion. |

### Part-3 resumption after sandbox clarification

Brad clarified that the `index.lock` error came from the Codex sandbox and authorized escalated Git writes and runner boots. `git add` and `git commit` succeeded with escalation. The guard is fork commit `b9647f5` (`[E58] Register E41/mpg_src tap tests only with PS2X_ENABLE_DIAG_TAPS`, trailer `Orchestrated-By: Codex`). The two suite gates above remain valid. Smoke boots, clean rate, push, and promotion are pending.
