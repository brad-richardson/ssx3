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

---

## Part 2 — visual gate, GB4 fold, and promotion

Brad accepted E56 and replaced the fixed-tick hash gate: free-running boots are not yet frame-deterministic because of the GB3 ±1-tick phase race. The Part-1 hash mismatch remains a measured fact, not evidence against the implementation. I viewed the saved E58 and E56 SC frames at ticks 837/836 and 873/873, and race frames at 1810/1815 and 1947/1943. Both SC runs show Zoe and the same Select Character layout; both race runs show an active HUD, snowy terrain, and the same dark foreground. Pose and radio text differ. There is **no difference in kind**. I also viewed the folded boot’s three frames (SC tick 830, race ticks 1810 and 1940); they show the same kind of rendering.

| Gate | Part-2 result / receipt |
| --- | --- |
| Fetch/fold | Fetched `fork/ssx3` at `13cac7f`, cherry-picked `102bd72` into local `e56-fold`. Final local/pushed commit `8e2864a3c7e41a6544b2fc3aeed0eba38293cdda` (`Orchestrated-By: Codex`). |
| Recompiler/codegen | New `fold/build/ps2xRecomp/ps2_recomp` regenerated 9,457 files into `E56/codegen-fold` before promotion. Counts reproduced Part 1: 2,049 added, 3,226 already present, 404 rejected prologues; E46+AU5 self-check 22/22. `fold/regen.log`. |
| Code size | 266,829,319 B vs previous canonical 266,643,935 B (+0.07%); 9,457 files each. Runner `__TEXT,__text` 117,622,040 B. |
| Taps-OFF build/suite | Release with diagnostic taps, runtime logs, and aggressive logs OFF. **548/548 pass** from the folded fork root. `fold/{build.log,suite-off-final.log,build/CMakeCache.txt}`. |
| Taps-ON build/suite | Separate Release `fold/build-taps`, `PS2X_ENABLE_DIAG_TAPS=ON`; **643/643 pass** from the folded fork root. `fold/{build-taps.log,suite-taps-final.log,build-taps/CMakeCache.txt}`. |
| Runner SHA-256, reads 1/2 | `2f55eeba87e004ffb722c78c475dcac31e6ced8ee4b1d997dbcb289489069e84` / same. ELF, ISO, map two reads again matched Part-1 pins. |
| Stop-policy boot | I26-FAST, `PS2X_MISSING_FUNCTION_POLICY=stop`, target tick 5350, wall cap 600 s. **PASS:** tick 5353 after 597.952 s, own PID 28983, one mini lease slot, `rc=0`, zero missing-target lines, normal counter output. Tick 5353 is 60.71 guest seconds after the ~1714 race start. `fold/run/gate-part2/{boot.log,result.json}` and `part2-gate.txt`. |
| Coverage at exit | `[coverage:missing-functions] targets=0`; `[coverage:unknown-syscalls] ids=0`; four unhandled RPC pairs, one hit each (SID/FNO: `80000211/1`, `237/0`, `534e44/0`, `80000006/ff`). Exact lines in `part2-gate.txt`. |
| Snapshots | Exactly three selected frame-dump events at ticks 830, 1810, 1940; three numbered retained PNGs plus the overwritten latest file. No per-frame PNG encoding. `fold/run/gate-part2/` and `part2-gate.txt`. |
| Runner-dir check | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty before push and after. Generated guest code remained outside Git. |
| Push | `git ls-remote fork refs/heads/ssx3` was `13cac7f` immediately before; `git push fork e56-fold:ssx3` fast-forwarded to `8e2864a`; remote verification afterward matched the full SHA. |
| Promotion/disk | Moved old `codegen-ssx3` to `codegen-ssx3-pre-e56`, then `E56/codegen-fold` to canonical `codegen-ssx3`. Both are 9,457 files. Canonical `register_functions.cpp` SHA-256 read twice: `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. Disk budget 97.6 GB / 200 GB; no cleanup deletion needed. |

Two small gate-support changes joined the fold commit. `ps2xRuntime/src/main.cpp` prints coverage after `runtime.run()` because it then calls `_Exit`, which skips `PS2Runtime`'s destructor. `PS2X_FRAME_DUMP_ONCE_TICKS=830,1810,1940` filters the existing frame dumper to one frame near each selected tick; the boot encoded three PNGs rather than every present. Both test suites were rebuilt and rerun after these changes. The harness enabled `PS2X_DIAG_PARK=1`, so its SIGTERM at the target triggered a graceful scheduler stop, coverage print, and process exit 0. The previous E56 boot had no counter output because it used default SIGTERM behavior.

Exact Part-2 commands (fork worktree except disk/lease checks):

```sh
git fetch fork ssx3
git worktree add -b e56-fold /Users/brad/dev/ssx3-work/E56/PS2Recomp-fold fork/ssx3
git cherry-pick -x 102bd72
zsh /Users/brad/dev/ssx3-work/E56/fold/build-recomp.sh
/Users/brad/dev/ssx3-work/E56/fold/build/ps2xRecomp/ps2_recomp /Users/brad/dev/ssx3-work/E56/fold/ssx3-fold.toml > /Users/brad/dev/ssx3-work/E56/fold/regen.log 2>&1
zsh /Users/brad/dev/ssx3-work/E56/fold/build.sh
/Users/brad/dev/ssx3-work/E56/fold/build/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/E56/fold/suite-off-final.log 2>&1
zsh /Users/brad/dev/ssx3-work/E56/fold/build-taps.sh
/Users/brad/dev/ssx3-work/E56/fold/build-taps/ps2xTest/ps2x_tests > /Users/brad/dev/ssx3-work/E56/fold/suite-taps-final.log 2>&1
python3 /Users/brad/dev/ssx3-work/E56/fold/e56_fold_boot.py --label gate-part2 --capture --target 5350 --wall 600
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git ls-remote fork refs/heads/ssx3
git push fork e56-fold:ssx3
local/tooling/disk_budget.sh
```

The SHA reads, boot counter lines, remote pins, and promotion details are in `part2-gate.txt` and the cited workdir logs. The folded build directories' CMake caches still name the former `E56/codegen-fold` path; reconfigure them to the canonical codegen path before any future incremental build. The three images and full boot log remain outside Git. No further E56 work is required by this brief.
