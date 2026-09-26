# AP1 — Android polish: immersive mode + GL-fallback aspect

Worker: muse, brief `local/muse/prompts/AP1.md`. Fork worktree
`~/dev/ssx3-work/AP1/PS2Recomp`, local branch `ap1` from fork `ssx3` tip `f0d2d3c`. Not pushed.

**Status: done (Part 2).** Part 1 stopped on the immersive failure and named the root
cause (wrong `hide()` JNI signature); Part 2 fixed it and all four checks pass on
APK `52f9d2b6…`: (a) no gesture handle + transient swipe/reveal/auto-hide, (b) GL
fills 1920×1080 at 16:9, (c) GL 1440×1080 pillarbox at 4:3, (d) vpad correct over
Vulkan. Nothing pushed.

## Commits (fork `ap1`, local)

| Commit | What |
| --- | --- |
| `4415067` | immersive mode (system bars hidden, transient swipe) — **broken, see root cause** |
| `a2e2953` | GL display-size canvas (`InitWindow(0, 0)` on Android) — VK-path interplay **validated on device** |
| `1bed138` (tip) | Part 2: `hide` as `(I)V`, bool return, bounded frame-loop retry |

- Mac suite: **685/685** at `a2e2953` and at tip `1bed138` (all three commits are Android-`ifdef`'d; host code identical)
- Runner-dir diff vs `14b1e5cb`: empty
- Immersive JNI syntax-checked against NDK r30 headers (`-fsyntax-only`, harness in `/tmp/ap1/`;
  this checks C++/JNI-API shapes only — the method *signature strings* are runtime data)

## Android build (bytesize `/home/brad/ap1`)

VR3's recipe (`local/research/AP1/build-android-ap1.sh`, `a6e6a6fd…` both ends).
Waited for FS2's then VR4's build (one heavy job at a time); PGS cloned from the
fork (I/O only) while they compiled.

| Item | Value |
| --- | --- |
| APK SHA | `b5c86e4b5259d828937624dfa0c95814b23bf36cca355a4a55136a5c0789b310` (×2 remote, ×2 local) |
| Size | 190,781,004 B |
| Build time | BUILD SUCCESSFUL in 14 m 54 s (after a 21 s config miss: Granite nested submodules needed `--recursive`) |

## Odin run A1 — (a) Vulkan default + swipe (1/4 launches)

APK `b5c86e4b…`, variant A (1× pipelined, Vulkan default on), I26-FAST, play knobs
(`PS2X_MTVU=1 PS2X_MTVU_LAG=1 PS2X_VU1_BLOCKS=1` + CPU pins 6/7, per the
orchestrator's LAG-on FYI), stop-tick 2400, scaps at 1100/2100, swipe at 2250.
Driver `local/research/AP1/launch.py` (F7 lineage; play-env pin now read from
`odin-play/SHA256SUMS`, currently `090cc981…`). Lease claimed/released cleanly;
no FS2/VR4 contention during the run.

| Screencap | Tick | Verdict (all viewed) |
| --- | --- | --- |
| `sc01-tick1100` | ~1201 | Select Event menu (Happiness), full-screen Vulkan, colours right — **gesture handle visible** (immersive failed) |
| `sc02-tick2100` | ~2180 | Race (2nd/2, 15 mph, HUD, rider, trail), full 16:9 — **gesture handle visible** (immersive failed) |
| `sc03-swipe-bars` | ~2288 | **Void: launcher home screen** — the swipe went HOME (bars were never hidden, nothing consumed it) |
| `sc04-swipe-autohide` | ~2288 | **Void: byte-identical to sc03** (launcher) |
| `sc05-final` | 2288 | **Void: launcher** (tick frozen after backgrounding; wall cap 600 s hit) |

Log evidence (`local/research/AP1/logs/A1/`):
- Exactly one `[immersive]` line: **`[immersive] NOT applied`** (the post-`InitWindow`
  shot; no `INIT_WINDOW`/`GAINED_FOCUS` re-fire — focus arrives before the wrapper installs).
- `[present-vk] parent buffer 1920x1080`, `child layer made … (1920x1080 buffers)`,
  `geometry src 512x448 -> dst [0,0 1920,1080] in parent buffer 1920x1080 aspect=1`:
  **`InitWindow(0,0)` works** — raylib's buffers went 796×448 → 1920×1080 and the Vulkan
  child maps 1:1 onto the panel. sc01/sc02 confirm the picture is correct full-screen.
- `[present-vk] child layer … layer 1920x1080` (the `g_winLog` fields): the sink's
  DecorView JNI (`getWindow→getDecorView→getWidth/getHeight`) **succeeded** at the first
  frame — the window/DecorView chain is fine; the failure is inside the API-30 branch.
- `SWIPE focus='…QuickstepLauncher' pid=22595`: app alive but backgrounded.

## Root cause (immersive; single mechanism, verified against the docs)

`WindowInsetsController.hide(int)` returns **`void`**
([docs](http://developer.android.com/reference/android/view/WindowInsetsController):
`public abstract void hide (int types)`). The AP1 code looks it up as
`(I)Landroid/view/WindowInsetsController;`, so `GetMethodID` returns null,
`hide == nullptr`, the call is skipped and the line prints `NOT applied` —
deterministically, on every call. Fix: signature `(I)V` + `CallVoidMethod`
(two lines in `ap1HideSystemBars`, fork `ap1` `ps2xRuntime/src/lib/ps2_runtime.cpp`).
Not timing: the DecorView chain provably works, and no re-fire would have helped.
(Recommend the follow-up also retry until applied, bounded, from the frame loop —
cheap insurance for the attach/focus window — but the signature is the fix.)

## Not run in Part 1 (stopped per the first-failure rule; all run in Part 2)

| Check | Part 1 state | Part 2 |
| --- | --- | --- |
| (b) GL fallback 16:9 | not launched | B1 PASS |
| (c) GL fallback 4:3 | not launched | C1 PASS |
| (d) Vulkan + vpad | not launched | D1 PASS |

## Play state after

Restored after A1 (`odin_restore_play.sh AP1`): installed base.apk `825b436d…`,
device env `090cc981…`, saves 6/6 OK, `mc0-test` empty, app stopped, battery 100 %,
lease released. Brad's save untouched.

## Pins and SHAs

| Item | Value |
| --- | --- |
| Fork base / tip | `f0d2d3c` → `1bed138` (`ap1`, local; runner-dir diff vs `14b1e5cb` empty) |
| Source tar `a2e2953` | `9a0f6d5d…` (430 files; staged `/home/brad/ap1/PS2Recomp`, markers verified) |
| paraLLEl-GS | `3d72467` + Granite `166ba21a` (cloned on bytesize; SS3 marker present) |
| codegen / vu1gen / vu0gen | vr2d 9457 files (2/2 sample SHAs = mini) / 7 files (7/7 SHAs = mini `vu1gen-ssx3`) / vr3 `2652966b…` = mini |
| jniLibs | vr2d Turnip `libvulkan_freedreno.so` 14,188,488 B |
| Build script | `local/research/AP1/build-android-ap1.sh` (`a6e6a6fd…` both ends) |
| APK `b5c86e4b…` | pulled to `~/dev/ssx3-work/AP1/odin-apk/app-release.apk` (×2 local match) |

## Budgets

Android builds 2 total (Part 1: 1 + a 21 s config miss; Part 2: 1 incremental under
the bytesize lock). Odin launches 5 total (A1 Part 1 + A2/B1/C1/D1 Part 2; Part 2
used 4/5). Scratch `~/dev/ssx3-work/AP1` ~1.7 GB (worktree + Mac build + 2 APKs +
odin logs). bytesize `/home/brad/ap1` (source, PGS 3d72467, build tree, APK).

## Exact commands

```sh
# Part 2 delta (after the gate): commit 1bed138 on ap1; suite; NDK check; delta tar
git archive --format=tar 1bed138 ps2xRuntime/src/lib/ps2_runtime.cpp | ssh bytesize 'wsl … "tar -x -C /home/brad/ap1/PS2Recomp"'  # 9567914f both ends
bash local/tooling/bytesize_lock.sh run AP1 -- ssh bytesize 'wsl -d Ubuntu -- bash -c "/home/brad/ap1/build.sh"'  # BUILD SUCCESSFUL
python3 local/tooling/odin_cooldown.py --out local/research/AP1/logs/<A2|B1|C1|D1> --mode screen   # before each
python3 local/research/AP1/launch.py --label A2 … --apk …/odin-apk2/app-release.apk --apk-sha 52f9d2b6… --scap-ticks 1100,2100 --swipe-tick 2250 --env …(play knobs)
python3 local/research/AP1/launch.py --label B1 … --vk 0 …   # C1: + --aspect 4:3; D1: + --pad-probe
bash local/tooling/odin_restore_play.sh AP1   # after every run
```
```sh
# Part 1 (for the record)
git -C ~/dev/PS2Recomp worktree add -b ap1 ~/dev/ssx3-work/AP1/PS2Recomp f0d2d3c
# ... two commits 4415067, a2e2953 ...
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/AP1/PS2Recomp ~/dev/ssx3-work/AP1/build --target ps2x_tests
(cd ~/dev/ssx3-work/AP1/PS2Recomp && ../build/ps2xTest/ps2x_tests)   # 685/685
git diff --stat 14b1e5cb ap1 -- ps2xRuntime/src/runner               # empty
NDK=/opt/homebrew/share/android-ndk; $NDK/.../clang++ --target=aarch64-linux-android29 -std=c++20 -fsyntax-only /tmp/ap1/ap1_immersive_check.cpp
git archive --format=tar ap1 > /tmp/ap1/ap1-a2e2953.tar              # 9a0f6d5d
cat /tmp/ap1/ap1-a2e2953.tar | ssh bytesize 'wsl -d Ubuntu -- bash -lc "mkdir -p /home/brad/ap1/PS2Recomp && tar -x -C /home/brad/ap1/PS2Recomp"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "git clone --quiet https://github.com/brad-richardson/parallel-gs.git /home/brad/ap1/parallel-gs"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "git -C /home/brad/ap1/parallel-gs checkout --quiet 3d72467"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "git -C /home/brad/ap1/parallel-gs submodule update --init --recursive --quiet"'
cat local/research/AP1/build-android-ap1.sh | ssh bytesize 'wsl … "cat > /home/brad/ap1/build.sh"'  # a6e6a6fd both ends
ssh bytesize 'wsl -d Ubuntu -- bash -lc "/home/brad/ap1/build.sh"'   # BUILD SUCCESSFUL in 14m 54s
python3 local/research/AP1/launch.py --label A1 --variant A --wall 600 --stop-tick 2400 --apk …/app-release.apk --apk-sha b5c86e4b… --scap-ticks 1100,2100 --swipe-tick 2250 --env PS2X_MTVU=1 --env PS2X_MTVU_LAG=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7
bash local/tooling/odin_restore_play.sh AP1
```

## Gaps

- The API-29 `setSystemUiVisibility` fallback path is untested (Odin is API 35; no API-29 device).
- `InitWindow(0,0)` takes raylib's portrait-config branch (`0<=0`) — local `AConfiguration`
  field + a warning line only (manifest locks landscape); A1 shows no ill effect.

## Recommended next action (orchestrator decides)

AP1b: fix the `hide` signature to `(I)V` (+ optional bounded frame-loop retry), Mac suite,
one bytesize build, re-run (a) with swipe + (b) + (c) + (d) (4 launches). The launcher,
build script and bytesize PGS/input staging are all reusable as-is.

## Orchestrator gate (2026-09-26)

**Stopped correctly; root cause is clear and small.** `WindowInsetsController.hide` is `(I)V`; the lookup used a wrong
return type. The display-size canvas (`InitWindow(0,0)`) works with the Vulkan child 1:1 on the panel.

## Part 2 brief (orchestrator)
Fix the signature (`(I)V` + `CallVoidMethod`), add a bounded retry from the frame loop until `[immersive] applied`
(e.g. once per second for 10 s, and again on every `APP_CMD_INIT_WINDOW`/`GAINED_FOCUS`). One Android build. Then the
remaining runs: (a) Vulkan default — no gesture handle in menu + race screencaps; swipe from the bottom edge **with a
short partial swipe** (`input swipe 960 1079 960 900 150`) so it reveals the bars instead of going HOME, then bars
auto-hide; (b) `PS2X_PRESENT_VULKAN=0` fills 1920×1080 at 16:9; (c) GL + `PS2X_ASPECT=4:3` → 1440×1080 with bars;
(d) `PS2X_VIRTUAL_PAD=1` on Vulkan — pad drawn right, no bars. ≤ 5 launches. Restore play state after each. Then stop.

## Part 2 — done (4/4 runs pass)

Runs A2/B1/C1/D1 all used APK `52f9d2b6…`, variant A + play knobs
(`PS2X_MTVU=1 PS2X_MTVU_LAG=1 PS2X_VU1_BLOCKS=1` + pins 6/7), I26-FAST,
stop-tick 2400, screen-mode cooldown before each (new Odin rule; all
launched within ~1 min of ready). Play state restored after every run
(`odin_restore_play.sh AP1`: base.apk `825b436d…`, env `090cc981…`, 6/6
saves, `mc0-test` empty, stopped). Every run reached its stop tick in
~70 s wall; nothing looks slower (no speed numbers taken — screening only,
nothing for the ledger).

### Fix

Fork `ap1` commit **`1bed138`** (`[AP1] Part 2: fix hide() JNI signature, bounded immersive retry`):
`hide` looked up as `(I)V` + `CallVoidMethod` (was `(I)L…`, never resolved);
`ap1HideSystemBars` returns bool and logs `[immersive] applied (…)` /
`[immersive] NOT applied`; the frame loop retries once a second for 10 s per
window (generation-gated) until applied. Window/focus re-apply through the
app-command wrapper unchanged.

- Mac suite: **685/685** at `1bed138`. Runner-dir diff vs `14b1e5cb`: empty.
- NDK r30 `-fsyntax-only -Wall` of the fixed function + retry snippet (stubs):
  pass — and it caught a real leftover (`return;` in the now-bool function), fixed
  before commit. Harness: `/tmp/ap1/ap1_immersive_check2.cpp`.
- Launcher: swipe is now the brief's short partial `input swipe 960 1079 960 900 150`.

### Build staging (done) / build (HELD by orchestrator)

- Delta `1bed138` (`ps2_runtime.cpp` only) streamed to `/home/brad/ap1/PS2Recomp`:
  file SHA `9567914f…` matches the mini; `(I)V` marker verified on bytesize.
  Tar `9271b0ff…`.
- bytesize WSL restarted mid-stage (fresh VM, `up 0 min`); `/home/brad/ap1`
  (source, PGS 3d72467, `.cxx` tree, `build.sh`) survived.
- An unlocked Part 2 build ssh started, then killed locally AND remotely
  (`kill` + `pkill -f ap1/build.sh`; verified no gradle/clang left) when the
  orchestrator ordered VR4 → FS2 → AP1 under `local/tooling/bytesize_lock.sh`.
- Then HOLD: bytesize C: full (4 GB free, 356 GB WSL image); orchestrator
  cleaned (124 GB free, sparse disk). Released: rebuilt under
  `bytesize_lock.sh run AP1` (queued behind VR4; no LOWDISK): **BUILD
  SUCCESSFUL** (48 tasks: 7 executed, 41 up-to-date — the killed first attempt
  had done the recompile). APK **`52f9d2b6424c84f86a3b8458517ebf92e74818a5196174363d22d0796b855846`**,
  190,781,004 B (×2 remote, ×2 local, pulled to `odin-apk2/`). Fix verified
  **inside** the artifact: new `.so` has `applied (` (1×) and no `bars hidden`;
  Part 1's has `bars hidden` (1×) and no `applied (`; `.so` SHAs differ.

### Runs (pending)

| Run | Settings | Result |
| --- | --- | --- |
| A2 (a) | Vulkan default + short swipe at 2250, scaps 1100/2100 | **PASS.** Log: `NOT applied` then `applied (insets-transient)` ×2 (retry works). sc01 menu + sc02/sc05 race: full 16:9, **no gesture handle**. sc03 (1 s post-swipe): transient status + nav bars, app foreground. sc04 (+4 s): bars auto-hidden. Focus stayed on the app, clean STOP at t2443 |
| B1 (b) | `--vk 0` (GL 16:9 fill) | **PASS.** raylib: screen/render 1920×1080, offsets 0,0. sc02/sc03 race fills the frame, no borders, no handle; immersive `applied` on the GL path too. sc01 caught My Rules mid-fade (tick-sample lag, not a GL bug — same nominal tick shows different settled screens across runs) |
| C1 (c) | `--vk 0 --aspect 4:3` | **PASS.** Pillarbox measured 240→1679 (1440×1080, exact 240/240 bars) on two rows; black bars, no handle. Note: a static 3×276 px bright segment at x≈1905, y 402–677 sits in the right bar, byte-identical across all 3 C1 shots (menu + race) — device chrome above our all-black clear, not our rendering |
| D1 (d) | `--pad-probe` on Vulkan | **PASS.** `[vpad] overlay shown` through the run (hidden only by the end-of-run injected press); immersive `applied`. All 3 shots: translucent pad (L1/L2/R1/R2, face buttons, D-pad, stick ring, SELECT/START) correctly laid out at display size over the full-screen race/menu, no system bars |
