# E55A2 — fixed RTC HLE gate

Worker: Codex. Brief: `local/muse/prompts/E55A2.md`. The orchestrator decides the gate. No push.

## Pins and gate table

| Item | Observation | Receipt |
| --- | --- | --- |
| Fork pin | `fork/ssx3` resolved to required E54F2 pin `0cab7d733179e0706b6262e6b6f0a8cd89b274b9`. New worktree `~/dev/ssx3-work/E55A2/PS2Recomp`, branch `e55-fixed-rtc`. | `git ls-remote fork refs/heads/ssx3`; `git worktree add` |
| Codegen | Reused canonical `~/dev/ssx3-work/codegen-ssx3` through a symlink, 9,457 files; no regeneration. Register file two-read SHA matches the brief. | `~/dev/ssx3-work/E55A2/{codegen-sha.txt,input-sha.txt}` |
| Mechanism | Exact per-call `PS2X_DETERMINISTIC=1` selects **2004-07-16 12:34:56 UTC**, which the existing BCD writer emits as `00 56 34 12 00 16 07 04`. Other flag values keep the existing `std::time`/host-local path. Return values remain 0 for an invalid pointer and 1 for a valid pointer. E3/E41 source labels distinguish fixed UTC from host-local. | Fork `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:696-745` |
| Focused actual-stub test | Calls `ps2_stubs::sceCdReadClock` using guest RAM at `0x1800`. Checks all eight fixed bytes on repeated calls, after `TZ` changes, and after switching back from host mode. An unbacked scratchpad pointer returns 0 and leaves sentinel RAM intact. Unset, `0`, empty and `yes` flags match a host-local reply bracketed by before/after host time. Restores flag and `TZ` on exit. | Fork `ps2xTest/src/ps2_runtime_kernel_tests.cpp:562-700`; both suite logs |
| Mac Release/Ninja taps OFF | One configure/build, `ps2x_tests` and `ps2EntryRunner`; full suite from fork root **581/581**, zero failed. | `cmake-off.log`, `build-off.log`, `suite-off.log` |
| Mac Release/Ninja taps ON | One configure/build, `ps2x_tests`; full suite from fork root **676/676**, zero failed. | `cmake-on.log`, `build-on.log`, `suite-on.log` |
| One diagnostic CPU boot | One mini lease, slot 1, released by harness. `PS2X_DETERMINISTIC=1`, dev-only `PS2X_SKIP_MOVIE=1`, I26-FAST vsync pad route, exactly frame targets `830,1810,2050`. Tick **2054** reached in **101.976 s** under 500 s wall cap; own PID 42678, `rc=0`, bound `target`. Functional regression, not a clean speed number. | `run/fixed-one/{result.json,boot.log}`, `boot-gate.txt` |
| Three frames viewed | Select Character tick 830 (Zoe); race tick 1810 (HUD `00:00:01`, 0%); race tick 2050 (HUD `00:00:05`, 1%). Known dark GS region persists. | `run/fixed-one/{sc-tick830.png,race_early-tick1810.png,race_late-tick2050.png}`, `frame-sha.txt` |
| Guest shim reach | Park snapshot has `pc=0x402520`, count **2**, first return `0x31ae88`, last return `0x2c75c0`. This records shim reach, not reply bytes. Snapshot SHA-256 `fbc41a9af7f1862dd30b36ba1242721978e0b2d890b686355949fa3cf172f74b`. | `run/fixed-one/park-snapshot.json:3250` |
| Runner check and fork commit | `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty before and after commit. Only the allowed source/test files committed as `[E55A2] Fix RTC reply in deterministic mode`, `4f932166c773e04522ffa007228670894f8b4f44`, trailer `Orchestrated-By: Codex`. Branch clean; no push. | Fork git log/status/diff |

## Two-read SHA-256 pairs

Each input below had two identical reads before the boot, recorded with literal paths in `~/dev/ssx3-work/E55A2/input-sha.txt`; frame pairs are in `frame-sha.txt`.

| Input or frame | SHA-256 on both reads |
| --- | --- |
| ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| E55A2 taps-OFF `ps2EntryRunner` | `80d22389073f0a8b258c55b2066663564098716f1bbc06e170bd4f6b28e08b8a` |
| Canonical `register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Select Character tick 830 | `6d7978a47b957c349d8526cae850550ed0e457f70f03e801c881da8cd47affe2` |
| Race tick 1810 | `9a20f5afa9b6356b54dc08d7bfa8010cc3ccd89b6065d191cb7971ccc7526c71` |
| Race tick 2050 | `df9623c3a50c2f108f99529aa3b524eaa9144964e47497b1ed2c03f7716125e5` |

## Budgets and exact commands

One build per tap mode, one boot, no repair loop. `du -sh ~/dev/ssx3-work/E55A2` was 681 MiB after boot, under 5 GiB. `local/tooling/disk_budget.sh` reported 111.4 GB of 200 GB used, 131 GiB free. Boot log was 10,463 B; no PK log. Run directory including frames was 1.8 MiB, under frame and log caps.

`build.sh` and `e55a2_boot.py` are E55A2-local adaptations of the E54F2 scripts. The build script runs `nice -n 10 cmake -S ... -B ... -G Ninja -DCMAKE_BUILD_TYPE=Release`, using the canonical codegen and local E50 dependency sources. The boot script claims/releases the mini lease and caps wall time, progress, logs and frames. These are the executed gate commands, with working directories shown:

```text
cd ~/dev/PS2Recomp && git ls-remote fork refs/heads/ssx3
cd ~/dev/PS2Recomp && git worktree add -b e55-fixed-rtc ~/dev/ssx3-work/E55A2/PS2Recomp 0cab7d733179e0706b6262e6b6f0a8cd89b274b9
cd ~/dev/ssx3-work/E55A2 && ./build.sh off
cd ~/dev/ssx3-work/E55A2/PS2Recomp && ~/dev/ssx3-work/E55A2/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E55A2/suite-off.log 2>&1
cd ~/dev/ssx3-work/E55A2 && ./build.sh on
cd ~/dev/ssx3-work/E55A2/PS2Recomp && ~/dev/ssx3-work/E55A2/build-taps/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E55A2/suite-on.log 2>&1
cd ~/dev/ssx3-work/E55A2 && python3 e55a2_boot.py --label fixed-one --capture --target 2050 --wall 500 > boot-gate.txt 2>&1
cd ~/dev/ssx3-work/E55A2/PS2Recomp && git diff --check
cd ~/dev/ssx3-work/E55A2/PS2Recomp && git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner
cd ~/dev/ssx3-work/E55A2/PS2Recomp && git add -- ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp ps2xTest/src/ps2_runtime_kernel_tests.cpp
cd ~/dev/ssx3-work/E55A2/PS2Recomp && git commit -m '[E55A2] Fix RTC reply in deterministic mode' -m 'Return a fixed UTC calendar through the existing BCD writer only for exact PS2X_DETERMINISTIC=1, and exercise fixed and host-local replies through the HLE stub.' -m 'Orchestrated-By: Codex'
```

Hash commands used `shasum -a 256` with each literal input/frame path listed twice, writing `input-sha.txt` and `frame-sha.txt`; those receipts preserve the full executed paths. The codegen count used `find ~/dev/ssx3-work/codegen-ssx3 -type f | wc -l`.

## Gaps

The diagnostic boot did not capture RTC reply bytes separately. The actual-stub test proves byte-exact fixed replies and host-local passthrough; the snapshot proves the shim was reached. A fixed RTC reply alone does not establish full-frame determinism: idle event ordering, pad state and memory card state remain separate. No Windows or Linux build was run.
