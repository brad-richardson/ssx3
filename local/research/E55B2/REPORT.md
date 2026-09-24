# E55B2 — cycle-only EE event selection gate

Worker: Codex. Brief: `local/muse/prompts/E55B2.md`. The orchestrator decides the verdict. No push.

## Pins and gate results

Fork worktree `~/dev/ssx3-work/E55B2/PS2Recomp`, branch `e55-cycle-events`, started from `4f932166c773e04522ffa007228670894f8b4f44`. `git ls-remote fork refs/heads/ssx3` returned that exact pin before worktree creation. Source/test commit: `779e8048cd584586f6896fde0f049fa758f287db` (`[E55B2]`, `Orchestrated-By: Codex`). Canonical `~/dev/ssx3-work/codegen-ssx3` was reused without regeneration: 9,457 files, `register_functions.cpp` SHA-256 `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`.

| Gate | Observation | Receipt |
| --- | --- | --- |
| Source mechanism | `EeScheduler` parses exact `PS2X_DETERMINISTIC=1` once per instance in its constructor, before `reset`. In that mode `processDueDeadlines` extracts every cycle-due record without a host-deadline filter, then uses the existing cycle/type/ID/insertion-sequence sort. Idle selects the lower guest-cycle target of scheduled event and memory timer; strict `<` gives scheduled event priority at equality. Unset, empty, `0`, and other values retain the host-deadline selection branches. ExternalWake has no guest-cycle timestamp and is outside this guarantee; it and stop still interrupt the condition-variable idle wait. | `ps2xRuntime/include/runtime/ee_scheduler.h`; `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`; E55B1 audit |
| Focused source tests | All requested contrasts passed through actual due-batch or idle-wait dispatch with injected host deadlines and real memory timer registers. See table below. | `ps2xTest/src/ps2_runtime_kernel_tests.cpp`; `suite-off.log`, `suite-on.log` |
| Mac Release/Ninja taps OFF | First compile stopped on a test-only mixed `nullptr`/string initializer list. One named repair used `std::array<const char *, 5>`; repair build passed. Full suite from fork root **584/584**, zero failed (581 baseline + 3 cases). | `cmake-off.log`, `build-off.log`, `build-off-repair.log`, `suite-off.log` |
| Mac Release/Ninja taps ON | One configure/build passed. Full suite from fork root **679/679**, zero failed (676 baseline + 3 cases). | `cmake-on.log`, `build-on.log`, `suite-on.log` |
| One diagnostic CPU boot | Mini lease slot 1 claimed and released. `PS2X_DETERMINISTIC=1`, dev-only `PS2X_SKIP_MOVIE=1`, I26-FAST vsync route, exact frame targets `830,1810,2050`; target tick 2050 reached at last reported tick **2053** in **122.12 s** under 500 s wall cap. Own PID 55860 exited `rc=0`, bound `target`. Functional regression only, not a determinism or speed gate. | `boot-gate.txt`, `run/cycle-one/{result.json,boot.log}` |
| Three frames viewed | Tick 830: Zoe at Select Character. Tick 1810: race HUD `00:00:01`, 0%. Tick 2050: race HUD `00:00:05`, 1%. Known dark GS region persists. | `run/cycle-one/{sc-tick830.png,race_early-tick1810.png,race_late-tick2050.png}`; `frame-sha.txt` |
| Runner-dir guard and local commit | `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` passed before and after the fork commit; the fork worktree is clean. Only the three allowed source/test files entered the commit. No fork push. | Fork `git status --short --branch`, `git show -s --format='%H%n%B' HEAD` |

## Synthetic source-test cases

`EeSchedulerTestAccess` injects records into the real private scheduler queue, calls the actual dispatch and idle paths, and reads queued guest handler PCs. It adds no production test switch. Future host deadlines are one hour ahead, past deadlines one second behind, so the ordering tests need no sleeps. Memory timer 0 is configured through `PS2Memory::write32`; its half EE-clock rate makes compare 40/50 fire at guest cycle 80/100.

| Case | Injected guest/host arrangement | Observed queued PCs or first cycle |
| --- | --- | --- |
| Exact flag | Separate scheduler instances with unset, empty, `0`, `yes`, `1`; env changed after construction | Only exact `1` enabled cycle-only mode; each instance retained its initial mode |
| Same-cycle alarms | ID 1 at cycle 100 with future host deadline; ID 2 at cycle 100 with past host deadline; current cycle 120 | ID 1 then ID 2 (`0x1100,0x1200`) |
| Different-cycle alarms | ID 1 at cycle 100/future host; ID 2 at cycle 110/past host; current cycle 120 | Cycle 100 then 110 (`0x1100,0x1200`) |
| Timer before event | Timer IRQ at cycle 80; alarm at 100 with past host deadline | First idle target cycle 80 and timer PC `0x1300`; then alarm PC `0x1100` at cycle 100 |
| Equal-cycle timer/event | Timer IRQ and alarm at cycle 100 | First target 100; alarm PC `0x1100` then timer PC `0x1300` |
| Default contrast | `PS2X_DETERMINISTIC=0`, timer at 80, alarm at 100 with past host deadline | Host-selected first target cycle 100; alarm then timer PCs, preserving legacy behavior |

## SHA pairs and budgets

Each path below was read twice immediately before boot, and each frame was read twice after boot. Both reads matched within every pair. Full paths and two literal hash lines per path are in `input-sha.txt` and `frame-sha.txt` under `~/dev/ssx3-work/E55B2/`.

| Input or frame | SHA-256 on both reads |
| --- | --- |
| ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| E55B2 taps-OFF `ps2EntryRunner` | `65a9415ab8c4f4b1237cdf421b07180b21fe2c1b1bd800188606bffe2abceac6` |
| Canonical `register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Select Character tick 830 | `f4db5618056250e9debdff14e8227ea5ee064cbd5dd793b78392bec91e40a33b` |
| Race early tick 1810 | `9a20f5afa9b6356b54dc08d7bfa8010cc3ccd89b6065d191cb7971ccc7526c71` |
| Race late tick 2050 | `df9623c3a50c2f108f99529aa3b524eaa9144964e47497b1ed2c03f7716125e5` |

One OFF configure/build, one OFF repair build, one ON configure/build, two full suites, one boot. E55B2 directory: **681 MiB** against 5 GiB cap; global ssx3 workstreams after builds: **113.3 GB / 200 GB**. Boot log 10,676 B, no PK log, all PNGs in the run directory 1,273,898 B, whole run directory 1.8 MiB; below 32 MiB log and 25 MiB frame caps. Both mini lease files were absent after the boot.

## Commands and gaps

Gate commands, with the test commands run from the fork worktree root:

```sh
git ls-remote fork refs/heads/ssx3
git worktree add -b e55-cycle-events ~/dev/ssx3-work/E55B2/PS2Recomp 4f932166c773e04522ffa007228670894f8b4f44
find ~/dev/ssx3-work/codegen-ssx3 -type f | wc -l
shasum -a 256 ~/dev/ssx3-work/codegen-ssx3/register_functions.cpp
cd ~/dev/ssx3-work/E55B2/PS2Recomp
/bin/zsh ~/dev/ssx3-work/E55B2/build.sh off
nice -n 10 cmake --build ~/dev/ssx3-work/E55B2/build --parallel 8 --target ps2x_tests ps2EntryRunner > ~/dev/ssx3-work/E55B2/build-off-repair.log 2>&1
~/dev/ssx3-work/E55B2/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E55B2/suite-off.log 2>&1
/bin/zsh ~/dev/ssx3-work/E55B2/build.sh on
~/dev/ssx3-work/E55B2/build-taps/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E55B2/suite-on.log 2>&1
cd ~/dev/ssx3-work/E55B2
python3 e55b2_boot.py --label cycle-one --wall 500 --target 2050 --capture > boot-gate.txt 2>&1
cd ~/dev/ssx3-work/E55B2/PS2Recomp
git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner
```

`build.sh` carries the exact Release/Ninja configure flags, canonical codegen path, E50 dependency source paths, and `nice -n 10`; `e55b2_boot.py` carries the exact I26-FAST pad route, environment, lease claim/release and progress, wall, log and frame bounds. Input/frame two-read SHA commands and outputs are preserved in the named SHA receipts. No regeneration, other platform build, determinism repeat, or speed measurement was performed. ExternalWake timing remains outside the cycle-only guarantee because its interface carries no guest-cycle timestamp.
