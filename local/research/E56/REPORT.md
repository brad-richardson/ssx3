# E56 — function-boundary closure

Worker: Codex. Brief: `local/muse/prompts/E56.md`. The orchestrator decides. Fork branch `e56-closure` from pinned `b9647f5`; local fork commit `102bd72` (`Orchestrated-By: Codex`). No push.

## Gate result

**Stopped at the first failed gate:** the Select Character frame hash at guest tick 837 is `c419b1b8` with E56 and `847bd9e4` with the pinned `b9647f5` runner. Both lines report 512×448, FBP 112/112, no fallback. The different presentation sequence numbers (816 vs 786) and absence of an E55 determinism baseline mean the cause is **not established**. Exact receipt: `gate-failure.txt`; full logs at the paths below. I stopped my own runner PID after the mismatch, and the harness released the lease. The race boot did not reach the required 60 guest seconds into the race. No additional gate boot or fix was attempted.

| Gate | E56 result | Baseline / limit |
| --- | ---: | ---: |
| Automatic resume entries, added | 2,049 | — |
| Candidates already present | 3,226 | — |
| Interior negative `$sp` prologues, accepted / rejected | 3,717 / 404 | 4,121 observed |
| Data-referenced leaf starts accepted (excluding prologues) | 1,558 | — |
| E46 self-check | 19/19 table slots present | 19/19 present in baseline |
| AU5 self-check | 3/3 table slots present | `0x3c9520` new; `0x3c9518`, `0x3c95f0` already present |
| Generated code bytes | 266,829,319 | 266,643,935; +185,384 (+0.070%) |
| Runner Mach-O `__TEXT,__text` bytes | 117,568,728 | 115,045,720; +2,523,008 (+2.19%), below 15% |
| Suite (taps OFF) | 537/537 passed | — |
| Stop-policy I26-FAST boot | 0 missing-target lines through tick 2378; race began ~1714 | 60 guest seconds requires ~tick 5310; **not reached** |
| SC frame hash, tick 837 | `c419b1b8` | `847bd9e4`: **mismatch** |
| Unknown syscalls in boot log | 0 TODO / 0 unknown-ID lines | Runtime counters not emitted by SIGTERM |
| Unhandled RPC trace lines in boot log | 4 | Runtime counters not emitted by SIGTERM |
| Workdir / internal disk | ~858 MiB / 93.9 GB of 200 GB | 6 GB / 200 GB caps |
| Builds / boots | 3 / 1 | ≤4 / ≤5 |

## Rule and policy

`ps2xRecomp/src/lib/ps2_recompiler.cpp` scans decoded interiors after the existing direct-target and configured-extra discovery. A negative `addiu $sp,$sp,-N` is accepted when it begins after `jr $ra`, its delay slot, and zero to two NOP padding words. An 8-aligned address referenced by an allocated non-code ELF section is accepted as a plausible leaf start under the same return boundary. Both use the existing owner resume-entry map, so the generated table and owner `switch` use the same path as `extra_function_starts`. The 404 rejected prologues were not after this return boundary, such as a stack adjustment in a function body. The rule reported 2,049 additions and 3,226 duplicate/already-present entries. Regeneration processed 9,454 functions, recompiled 9,278, stubbed 176, with zero decode failures and zero recompiler errors. It logged 3,712 existing-style control-flow warnings.

`PS2X_MISSING_FUNCTION_POLICY=stop|continue` is read when constructing `PS2Runtime`: dev default `stop`, release default `continue`. An invalid value reports a warning and uses the build default. `stop` logs target, source, registers, and dispatch history before aborting; it prints coverage counters before abort. The per-runtime counter map records each missing target, unknown numeric/TODO syscall, and unhandled `(sid,function)` RPC pair. The destructor prints those maps on normal exit. Programmatic `setMissingFunctionPolicy(Stop)` keeps the prior request-stop behavior used by unit tests. The bounded gate harness ended the runner with SIGTERM, so destructor counts were not printed there; log searches are the only boot counts and cannot establish full 60-second coverage.

## Input pins, build, and receipts

| Input/artifact | SHA-256 read 1 | Read 2 |
| --- | --- | --- |
| ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | same |
| Function map `games/ssx3/ssx3-functions.sweep.csv` | `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba` | same |
| ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | same |
| Baseline E58 runner | `f3de8d2cc051c4ac30f8e0e07a84f45eb4889923727627b7416b67c79d251608` | same |
| E56 runner | `ec60ec928e639ca0cb8d63a7b691572caa39fa1d58e64a08b430e1f0a9e79e94` | same |

The first `ps2_recomp` build failed because the new helper accepted `std::map` while the production resume map is `std::unordered_map`. I fixed that type, then the recompiler build succeeded (one fix attempt). The subsequent full Release build succeeded with runtime/aggressive logs OFF and diagnostic taps OFF. The suite passed in 0.46 s. Logs and build configuration: `~/dev/ssx3-work/E56/{cmake.log,build-recomp.log,build-recomp-fix.log,regen.log,build.log,suite.log,build/CMakeCache.txt}`. The generated sources, game inputs, binaries, and frame dumps remain outside Git in the E56 workdir.

Commands, from the E56 fork worktree unless noted:

```sh
zsh /Users/brad/dev/ssx3-work/E56/build-recomp.sh
nice -n 10 ninja -j8 ps2_recomp > /Users/brad/dev/ssx3-work/E56/build-recomp-fix.log 2>&1  # cwd E56/build
/Users/brad/dev/ssx3-work/E56/build/ps2xRecomp/ps2_recomp /Users/brad/dev/ssx3-work/E56/ssx3-e56.toml > /Users/brad/dev/ssx3-work/E56/regen.log 2>&1
zsh /Users/brad/dev/ssx3-work/E56/build.sh
/Users/brad/dev/ssx3-work/E56/build/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/E56/suite.log 2>&1
python3 /Users/brad/dev/ssx3-work/E56/e56_boot.py --label gate-a --capture --target 5400 --wall 500
ps -p 10035 -o pid=,etime=,comm=; kill -TERM 10035  # E56's own PID, after failed frame-hash gate
```

Boot receipt `~/dev/ssx3-work/E56/run/gate-a/result.json`: slot 2, PID 10035, elapsed 178.531 s, last rate tick 2378, `rc=-15` due to intentional SIGTERM, five bounded SC/race snapshots, log 695,117 B. Both mini lease slots were free afterward. The boot showed four `[IOP/RPC trace:unhandled]` lines and zero missing-target lines. This diagnostic boot supplies no speed number.

`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` and the worktree diff for that directory were empty. No generated guest code was staged. No push.

## Recommended next action (orchestrator decides)

Establish whether tick-837 frame hashes match across two pinned `b9647f5` boots with the same route and host conditions. If they do, identify which newly registered entry first changes the SC frame before promoting E56. If they do not, use a deterministic guest-state/frame gate before attributing this mismatch to the entry rule. The 60-guest-second race gate still needs a full bounded boot.
