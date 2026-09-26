# AP1 — Android polish: immersive mode + GL-fallback aspect

Worker: muse, brief `local/muse/prompts/AP1.md`. Fork worktree
`~/dev/ssx3-work/AP1/PS2Recomp`, local branch `ap1` from fork `ssx3` tip `f0d2d3c`. Not pushed.

**Status: stopped on the first failure (brief rule). Immersive mode does NOT apply
(`[immersive] NOT applied`); root cause named below (wrong JNI signature for
`WindowInsetsController.hide`). The GL-fallback aspect runs (b, c) and the vpad run (d)
were not launched. The swipe check voided its run (swipe went HOME).**

## Commits (fork `ap1`, local)

| Commit | What |
| --- | --- |
| `4415067` | immersive mode (system bars hidden, transient swipe) — **broken, see root cause** |
| `a2e2953` (tip) | GL display-size canvas (`InitWindow(0, 0)` on Android) — VK-path interplay **validated on device** |

- Mac suite: **685/685** at tip `a2e2953` (both commits are Android-`ifdef`'d; host code identical)
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

## Not run (stopped per the brief's first-failure rule)

| Check | Needs |
| --- | --- |
| (b) GL fallback 16:9 (`--vk 0`) | install `b5c86e4b…`, expect game fills 1920×1080 |
| (c) GL fallback 4:3 (`--vk 0 --aspect 4:3`) | expect 1440×1080 + black bars |
| (d) Vulkan + `PS2X_VIRTUAL_PAD=1` (`--pad-probe`) | under-layer pad at display size, no system bars |

(b)/(c) verdicts on APK `b5c86e4b…` would stand regardless of the immersive fix
(immersive changes no window size); (d)'s no-bars half needs the fix.

## Play state after

Restored after A1 (`odin_restore_play.sh AP1`): installed base.apk `825b436d…`,
device env `090cc981…`, saves 6/6 OK, `mc0-test` empty, app stopped, battery 100 %,
lease released. Brad's save untouched.

## Pins and SHAs

| Item | Value |
| --- | --- |
| Fork base / tip | `f0d2d3c` → `a2e2953` (`ap1`, local; runner-dir diff vs `14b1e5cb` empty) |
| Source tar `a2e2953` | `9a0f6d5d…` (430 files; staged `/home/brad/ap1/PS2Recomp`, markers verified) |
| paraLLEl-GS | `3d72467` + Granite `166ba21a` (cloned on bytesize; SS3 marker present) |
| codegen / vu1gen / vu0gen | vr2d 9457 files (2/2 sample SHAs = mini) / 7 files (7/7 SHAs = mini `vu1gen-ssx3`) / vr3 `2652966b…` = mini |
| jniLibs | vr2d Turnip `libvulkan_freedreno.so` 14,188,488 B |
| Build script | `local/research/AP1/build-android-ap1.sh` (`a6e6a6fd…` both ends) |
| APK `b5c86e4b…` | pulled to `~/dev/ssx3-work/AP1/odin-apk/app-release.apk` (×2 local match) |

## Budgets

Android builds 1/1 (plus one 21 s config miss on the same slot). Odin launches 1/4.
Scratch `~/dev/ssx3-work/AP1` 1.5 GB (worktree + Mac build + APK + odin logs).
bytesize `/home/brad/ap1` (source, PGS 3d72467, build tree, APK).

## Exact commands

```sh
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

- Immersive fix + validation (a, swipe) need a follow-up brief (one-line fix, one rebuild, re-run).
- (b)/(c)/(d) never launched; runnable on APK `b5c86e4b…` as-is if the orchestrator wants
  the GL verdicts before the fix build.
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
