# AP1 — Android polish: immersive mode + GL-fallback aspect (muse, 2 h)

## Goal
Two small visible issues on Brad's Odin (F6/F7 screencaps): (1) Android's gesture-bar handle is drawn over the game (system bars not hidden); (2) the GL fallback path (used only if the Vulkan present can't start, or with `PS2X_PRESENT_VULKAN=0`) still letterboxes into raylib's 640×448 canvas, showing a bordered 1544×868 box, against Brad's display rule (`AGENTS.md`: 16:9 default, aspect-preserving, largest fit, no unapproved stretch).

## Facts
- App: NativeActivity (`hasCode="false"`), raylib 5.5 owns `android_main`/EGL (VK1 D4–D5, `local/research/VK1/REPORT.md`). Immersive mode for a NativeActivity: JNI to `getWindow().getDecorView()` → `WindowInsetsController.hide(systemBars())` + `BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE` (API 30+; minSdk 29 → fall back to `setSystemUiVisibility(IMMERSIVE_STICKY|FULLSCREEN|HIDE_NAVIGATION|…)` on 29), re-applied on window focus / `APP_CMD_INIT_WINDOW`. VK2's sink already does JNI `DecorView` size reads (`ps2_present_vk_android.cpp`).
- GL fallback: start raylib at the display size on Android (the window's pixel size instead of 640×448) so `presentRect` fills 1920×1080 at 16:9; check the on-screen virtual pad layout still scales (it's off on the Odin by default; verify with `PS2X_VIRTUAL_PAD=1`).
- Fork `ssx3` tip `f0d2d3c`. Android build: VR3's recipe on bytesize (`-Pps2xVu0RecompDir`, hold the ssh, one heavy job at a time — FS2/VR4 may build there too). Odin: `local/tooling/odin_lease.sh` for every install/launch/force-stop; `local/tooling/odin_restore_play.sh <LABEL>` after every run; keyguard/battery/cool-down not needed for screenshots-only runs but force-stop after each.

## Steps
1. Branch `ap1` in `~/dev/ssx3-work/AP1/PS2Recomp` from the fork tip; two commits (immersive; GL display-size canvas). Mac suite green (Android-only code otherwise); runner-dir check empty.
2. One Android build; Odin runs (≤ 4 launches, play env keys): (a) Vulkan path default — screencap in the race: no gesture handle, full 16:9; swipe-to-reveal still works (`input swipe` from the bottom edge, then check bars auto-hide); (b) `PS2X_PRESENT_VULKAN=0` — GL fallback fills 1920×1080 at 16:9; (c) `PS2X_ASPECT=4:3` on the GL path — 1440×1080 with bars; (d) `PS2X_VIRTUAL_PAD=1` on the Vulkan path — pad drawn correctly, no system bars. View every screencap.
3. Speed not required (no hot-path change); note if anything looks slower.

## Rules
Never push; Brad's save untouched; restore play state after each run. Text only in git (screencaps in scratch). First failure: stop, save the error, hand back.

## Deliverable
`local/research/AP1/REPORT.md` (commits, APK SHA, screencap table with verdicts, gaps) + `[AP1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
