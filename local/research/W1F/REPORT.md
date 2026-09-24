# W1F — native 16:9 fold and iOS gate

Worker: Codex. Brief: `local/muse/prompts/W1F.md`. Mac gates passed and the fork fold was pushed. **Stopped at the first failed iOS gate:** the one Simulator run exited before the title. The iPad run and iPhone build/install were not attempted. The orchestrator decides the gate.

## Gate table

| Gate | Result | Receipt |
| --- | --- | --- |
| Source pin | `fork/ssx3` was `8e2864a3c7e41a6544b2fc3aeed0eba38293cdda` after fetch and on `ls-remote`. E56 canonical codegen `register_functions.cpp` SHA was `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` on both reads. | `local/research/E56/REPORT.md`; command transcript below |
| Fold | `0c32269` → `152ef5f`; `7a0e46a` → `a5cbd9c`, both clean cherry-picks. Added `8acb4b3` to expose/test the W1 host mode choice in the touched presentation/test files. Branch `w1f-fold` in `~/dev/ssx3-work/W1F/PS2Recomp` was clean. Beyond E56, the branch has only I26/W1 presentation, pad and test changes. | `git log fork/ssx3..8acb4b3`; `git diff --stat` |
| Runner directory | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty after the fold, immediately before push, and after push. No generated guest sources, game data, or binaries entered Git. | command transcript below |
| Mac Release build | Pass, one configure/build attempt, taps OFF, `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`, runtime/aggressive logs OFF. | `~/dev/ssx3-work/W1F/{cmake.log,build.log,build/CMakeCache.txt}` |
| Host suites | Taps OFF **556/556**; taps ON **651/651**. Both run from the fork worktree root. | `~/dev/ssx3-work/W1F/{suite-off.log,suite-taps.log,build-taps.log}` |
| Aspect unit cases | Pass: unset `PS2X_WIDESCREEN` maps to guest mode 2 and 16:9; explicit `0` maps to guest mode 0 and 4:3; explicit `1` maps to mode 2; `PS2X_ASPECT=4:3`, `16:9`, and `native` override the presenter. | `Ps2PresentGeometry` in both suite logs; `ps2xRuntime/include/ps2_present_geometry.h`, `ps2xTest/src/ps2_present_fallback_tests.cpp` |
| Mini boot | Pass, one lease boot, slot 1, own PID 47550, `PS2X_SKIP_MOVIE=1` dev-only, I26-FAST, default W1 mode, 500 s cap. Target tick 2050 reached at tick 2057 after 106.996 s; rc 0; three captured frames viewed. `[widescreen] SSX3 mode=2 (PS2X_WIDESCREEN=default)`; apply at source `0x2285a0` changed guest 0 to host 2. | `~/dev/ssx3-work/W1F/{boot-gate.txt,run/gate/boot.log,run/gate/result.json}` |
| Visual gate | Select Character shows Zoe with the same 3D proportions and layout in kind as W1/E56. The W1 16:9 presenter widens 2D title/menu/HUD elements; the W1F raw capture shows the same 2D elements. Race frames at ticks 1810 and 1940 show an advancing HUD and the known black GS composite occlusion over much of the scene. Free-running frame hashes were not compared as a gate. | Viewed `~/dev/ssx3-work/W1F/run/gate/{sc-tick830.png,race_early-tick1810.png,race_late-tick1940.png}` against `local/research/W1/{on-character.jpg,on-race.jpg}` and `~/dev/ssx3-work/E56/fold/run/gate-part2/{sc-tick830.png,race_early-tick1810.png}` |
| Fork push | Fast-forward `8e2864a..8acb4b3`; `ls-remote fork refs/heads/ssx3` afterward returned `8acb4b300866cb663569a60fca6b8b708ae50a91`. | `git push fork w1f-fold:ssx3`; remote readback |
| Simulator build/install | Build and `simctl install` passed from pushed source and promoted codegen. 9,455 generated game object sources, zero in-tree. One Simulator run exited by 10 s, before title/SC/race. Console: `[main] fatal exception: Unable to determine executable path. Pass the guest ELF as argv[1] or define PS2X_DEFAULT_BOOT_ELF.` The screenshot shows the Simulator home screen. | `~/dev/ssx3-work/W1F/{ios-sim-stage.txt,logs/runtime-sim-build.log,run-gate/console.log,run-gate/shot-0010s.png,sim-gate.txt}` |
| iPad | Not attempted after failed Simulator gate. Device was listed connected, but unlock state was not checked. | `xcrun devicectl list devices` before build |
| iPhone | **Not built or installed** after failed Simulator gate. `devicectl` listed `00008140-0002505001F3001C` as available/paired before build; the required final device-ID reread and install did not occur. | device list before build; no install receipt |

## Input and artifact SHA-256, two reads each

| Item | Read 1 | Read 2 |
| --- | --- | --- |
| E56 canonical `register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` | same |
| Stock `SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | same |
| Stock `SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | same |
| Release Mac runner | `5ab81a5900d14ae0a23417908980bb8337c8f59caacdfb1b50c4e262d07135c3` | same |
| Simulator unsigned app binary | `811858a74f0d72c5cc68a609fbdf2a0c456cae3a931be475e3d348b086431828` | same |
| Simulator staged/ad-hoc-signed app binary | `5c7e1f49918ea26903353ad1f4e88a7aa3a9c4aa067e6e175f23e69107b4c9bd` | same |
| iPhone signed app binary | not found | not found |

## iOS failure evidence

`w1f-fold` cherry-picked the I26 presentation commit `0c32269` and W1 commit `7a0e46a` as instructed. I26's branch also descends from two I25 commits, `31d988d` and `8a70aa6`, that were **not** in E56 and were not part of the two cherry-picks. The W1F `ps2xRuntime/src/main.cpp` lacks I25's `ps2x::ios::prepareEnvironment(...)` call and the `PS2X_BOOT_ELF` lookup when launched without `argv[1]`; compare `git diff b9647f5 8a357ac -- ps2xRuntime/src/main.cpp` and `local/research/I25/REPORT.md` §1. W1F's staged bundle contains `ps2x.env` and `SLUS_207.72`, but the current main path does not load that env file before `getExecutablePath`. This source difference explains the observed console fatal. No repair or second Simulator run was attempted under the brief's first-failure rule.

## Commands, budgets, and gaps

Commands, with fork commands run from `~/dev/ssx3-work/W1F/PS2Recomp` unless stated otherwise:

```sh
git fetch fork ssx3
git worktree add -b w1f-fold /Users/brad/dev/ssx3-work/W1F/PS2Recomp fork/ssx3
git cherry-pick -x 0c32269a1c7367ba66fad9cccfb4fec210ee2499
git cherry-pick -x 7a0e46a06da59887a55395234e53fd657bc7dd3a
git add ps2xRuntime/include/ps2_present_geometry.h ps2xRuntime/src/lib/ps2_runtime.cpp ps2xTest/src/ps2_present_fallback_tests.cpp
git commit -m '[W1F] Cover host widescreen mode choices' -m 'Orchestrated-By: Codex'
zsh /Users/brad/dev/ssx3-work/W1F/build.sh
/Users/brad/dev/ssx3-work/W1F/build/ps2xTest/ps2x_tests
zsh /Users/brad/dev/ssx3-work/W1F/build-taps.sh
/Users/brad/dev/ssx3-work/W1F/build-taps/ps2xTest/ps2x_tests
python3 /Users/brad/dev/ssx3-work/W1F/w1f_boot.py --label gate --capture --target 2050 --wall 500
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git ls-remote fork refs/heads/ssx3
git push fork w1f-fold:ssx3
git ls-remote fork refs/heads/ssx3
TARGET=sim bash /Users/brad/dev/ssx3-work/W1F/build-install.sh prefixes configure build stage sim_install
LABEL=gate WALL=140 SHOT_S=10 bash /Users/brad/dev/ssx3-work/W1F/sim-run.sh
```

The W1F copies of `build-install.sh` and `sim-run.sh` are in `~/dev/ssx3-work/W1F/`; I26's checked-in scripts were not edited. The Mac runner and Simulator app used E56's promoted codegen. W1F used 1/2 Mac builds, 1/1 Mac boot, 1/1 Simulator run, 0/1 iPad run, 0/1 iPhone install, and 4.2 GB of the 8 GB W1F cap. `local/tooling/disk_budget.sh` read 102.3 GB of the 200 GB internal cap after the Simulator build. Both mini lease slots were free at handback. An initial `simctl` read failed in the sandbox and succeeded when rerun escalated; it did not consume a gate run. No ssx3 `main` push.

**Gap:** the requested iPad validation and iPhone build/install are outstanding because the Simulator startup gate failed. The pushed fold remains at `8acb4b3`.
