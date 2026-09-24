# E58 — fold and regeneration; stopped at rate-log preflight

Worker: Codex. Brief: `local/muse/prompts/E58.md`. The orchestrator decides. No fork push or codegen promotion was attempted.

## Fold

Worktree: `~/dev/ssx3-work/E58/PS2Recomp`, local branch `e58-fold`, base `eac6cba`, HEAD `c34d9c6a46592e2ac6830ea3ff26c90500b5beef`. All five commits are local only; no generated guest code entered the fork. `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty.

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
