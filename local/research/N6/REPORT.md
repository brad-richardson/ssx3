# N6 — Odin built-in controller → PS2 pad (real input on the device)

- Date: 2026-09-23. Brief: `local/muse/prompts/N6.md`.
- Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/N4/REPORT.md`.
- HEADLINE: the Odin's controller already drives the game through raylib's
  Android gamepad path with a correct mapping (START, dpad, face buttons,
  sticks, shoulders all device-proven). Two N6 changes on `n2-android`,
  both Android-only `#if` blocks in one file: (1) union keyboard +
  gamepad state instead of if/else (the old code permanently ignored
  keyboard state, including adb-injected keys, after the first controller
  event latched gamepad-0 ready); (2) env-gated `PS2X_PAD_LOG` pad-state
  log used for the per-button proof. Injected keys now drive title →
  main menu → Select Character with no pad script, and three 60 s idle
  checks show no phantom input. One inference left for Brad's hands-on:
  physical X/Y positions (see §5).
- Budget: 2/3 builds, 4/4 launches, ~2.5 h of 4 h. No push anywhere;
  `n2-android` local-only on bytesize (`f9d78da` → `ae210c9` → `65c95d9`).

## 1. getevent facts (the controller)

`logs/getevent-lp.txt`. One gamepad on the device:

- `/dev/input/event8` **"Xbox Wireless Controller"**, `dumpsys input`
  classes `KEYBOARD | GAMEPAD | JOYSTICK | EXTERNAL`, ControllerNumber 1,
  VID/PID `2020:0112`. This is the only gamepad-class device, so it is
  what the game reads (whether it is the built-in pad or something on the
  dock is not distinguished; the Odin Station virtual mouse is also
  present, but it has no buttons/axes the game could use).
- Keys: `BTN_SOUTH/EAST/C/NORTH/WEST/Z`, `BTN_TL/TR/TL2/TR2`,
  `BTN_SELECT/START/MODE/THUMBL/THUMBR`, `BTN_DPAD_*` (+ `KEY_BACK`,
  `KEY_APPSELECT` on the same device).
- Axes: `ABS_X/Y/Z/RZ` −32767..32767 flat 15 (sticks), `ABS_GAS/BRAKE`
  0..32767 (analog triggers), `ABS_HAT0X/Y` −1..1 (dpad hat).
- `adb shell` is in the `input` group, so `sendevent` on event8 works and
  produces real gamepad-source events (used for every gamepad-path test).
- Second input used: `/dev/input/event5` `ff_key`, pure `KEYBOARD` class
  with `KEY_ENTER/UP/DOWN/LEFT/RIGHT/BACK` — holdable keyboard-source
  keys for single-step control (`sendevent` holds; `input keyevent`
  down+up is instant and can miss polls or double-land).
- The effective keylayout is the Odin vendor file
  `Vendor_2020_Product_0112.kl` (`logs/odin-keylayout.txt`): standard
  except **`0x133(307)→BUTTON_X` and `0x134(308)→BUTTON_Y`** (transposed
  vs stock AOSP; the Odin Generic.kl transposes them too). Reading: the
  firmware emits 307 for the physical X-position button and 308 for
  Y-position, and the vendor layout corrects them to proper
  BUTTON_X/Y — so physical X = BUTTON_X = PS2 square and physical Y =
  BUTTON_Y = PS2 triangle. Brad's 30 s test (§5) confirms the physical
  positions definitively.

## 2. Before/after mapping table

Chain: kernel code → Android keycode (Odin .kl) → raylib 5.5
(`AndroidTranslateGamepadButton` / axis+NUL keyboard map) →
`ps2_pad.cpp` → PS2 active-low bit. Proven column = launch-4 `[padlog]`
press/release pairs at the title (49 lines, `logs/launch4-padlog.txt`
+ `logs/launch4-press-marks.txt`), except where noted.

| Odin input (kernel) | Android | PS2 bit | btns pressed | Proven |
|---|---|---|---|---|
| A, 304 | BUTTON_A | cross 0x4000 | 0xbfff | padlog + screen (T8: menu→SC) |
| B, 305 | BUTTON_B | circle 0x2000 | 0xdfff | padlog |
| X-pos, 307 | BUTTON_X | square 0x8000 | 0x7fff | padlog (as code; §5 for position) |
| Y-pos, 308 | BUTTON_Y | triangle 0x1000 | 0xefff | padlog (as code; §5 for position) |
| dpad 544/545/546/547 | DPAD_* | up/down/left/right | 0xffef/bf/7f/df | padlog + screen (W2: →Conquer) |
| hat X/Y ±1 | HAT_X/Y | right/down | 0xffdf/0xbf | padlog |
| L1/R1 310/311 | BUTTON_L1/R1 | L1/R1 | 0xfbff/0xf7ff | padlog |
| L2/R2 digital 312/313 | BUTTON_L2/R2 | L2/R2 | 0xfeff/0xfdff | padlog |
| L3/R3 317/318 | THUMBL/R | L3/R3 | 0xfffd/0xfffb | padlog |
| select 314 | BUTTON_SELECT | select 0x0001 | 0xfffe | padlog |
| start 315 | BUTTON_START | start 0x0008 | 0xfff7 | padlog + screen (T3/V/W1: title→menu) |
| mode 316 | BUTTON_MODE | (none) | no line | padlog (correct: no PS2 bit) |
| left stick X/Y | AXIS_X/Y | lx/ly bytes | 01/ff at ±max, 80 center | padlog |
| right stick Z/RZ | AXIS_Z/RZ | rx/ry bytes | ff at +max, 80 center | padlog |
| analog GAS/BRAKE | AXIS_GAS/BRAKE | (none: pad reads digital L2/R2 keys only) | no line | padlog (documented, by design) |

Injected (`adb shell input keyevent`, keyboard/virtual source) mapping:

| Injected key | raylib keyboard map | PS2 (union block) | Observed |
|---|---|---|---|
| KEYCODE_BUTTON_START/A (any BUTTON_*) | `mapKeycode` = 0 (dropped) | — | no reaction (T1/T2, title) |
| KEYCODE_DPAD_* | → KEY_UP/DOWN/LEFT/RIGHT | dpad bits | works while keyboard state is read |
| KEYCODE_ENTER | → KEY_ENTER | start | works (V1: title→menu→SC) |
| KEYCODE_X | → KEY_X | cross | works post-fix (V6 leg; W-route) |

Before (N4 build, `if (useGamepad) … else …keyboard…`): raylib latches
`ready[0]` on the first controller event, so after T3's real START the
keyboard branch went permanently dead — T5 (DPAD_DOWN ×8), T6 (DPAD_UP
×8) and T7 (X ×8) all no-ops on the old build. After (N6 build,
Android-only union): the same post-latch keyboard input moves the menu
(W3: keyboard UP after real dpad-DOWN → Conquer → Single Event).
Desktop (`#else`) keeps the old if/else byte for byte.

No other mapping change was needed: sticks already land in the analog
bytes (`data[4..7]`, DualShock mode byte is game-driven in shared
`Pad.cpp`), `PS2X_PAD_SCRIPT` still applies after the backend in
`readPadPortData` (untouched, precedence kept), and the todo N-lane
manifest item (`showWhenLocked`/`turnScreenOn`, +`profileable`) was
re-verified present in both new APKs via `aapt` — no manifest edit.

## 3. The diff (`n2-android`, local-only, no push)

`f9d78da → ae210c9 → 65c95d9`, one file,
`ps2xRuntime/src/lib/ps2_pad.cpp` (+48/−1). Full text:
`logs/n2-android-diff.txt`.

- `ae210c9 [N6-local] Union keyboard and gamepad input on Android`:
  `const bool useKeyboard = true` under `#if defined(__ANDROID__)`
  (`!useGamepad` elsewhere); `else` → `if (useKeyboard)`.
- `65c95d9 [N6-local] Env-gated pad-state log for mapping proof`:
  `PS2X_PAD_LOG=1` logs `[padlog] gp=%d btns=0x%04x rx/ry/lx/ly`
  on change (plus one initial line). Off by default; zero behavior
  change when unset.

## 4. Builds + launches

Builds (N3/N4 recipe, `ps2xBootElf` + `c17-codegen` flags; T58 idle at
both builds; pins in `logs/apk-pins.txt`, ×2 reads agree build-tree +
mini):

| Build | Commit | APK SHA | Bytes | Bars |
|---|---|---|---|---|
| 1 (union) | `ae210c9` | `cd4b9330…ef8efd` | 134,164,884 | UNDEF 0, sub_ T 9457, aapt manifest ✓ |
| 2 (union+padlog) | `65c95d9` | `134616db…9094c5` | 134,165,236 | same |

(N4 APK `d93b81a7…` re-verified ×2 before launch 1. The build-script
`DEFINED_SUB_STAR_RAW=0` line is N4's known mangled-name grep artifact;
direct re-probe = 9457 `T`, matching N4.)

Launches (lease `N6 …` → `LEASE_FREE N6 done`, keyguard
`showing=false` every launch, BACK after each `am start`, no USB-dialog
frame in any scap, 0 FATAL on all runs; scripts in `scripts/`, envs
beside them, scaps + logcats in `~/dev/ssx3-work/N6/launchN/`):

| Launch | APK / env | Input → result (screens viewed) |
|---|---|---|
| 1 (Step 1, `d93b81a7`, no script) | injected BUTTON_START ×8 → title; BUTTON_A ×8 → title; **real START (sendevent 315) → Main Menu**; ENTER ×8 → menu; DPAD_DOWN/UP ×8 → **no move (latch finding)**; X ×8 → no-op; **real A (304) → Select Character (Zoe)**; 60 s idle → still Zoe (tick 2553→2563) |
| 2 (validate, `cd4b9330`, no script) | **injected ENTER ×8 → title → menu → SC (Zoe)** in one burst (START confirms at the menu; tick 869→968, then ~0.1/s settled); rest of run at SC |
| 3 (mechanisms, `cd4b9330`, no script) | event5-ENTER hold → menu (single step); real dpad-DOWN → Conquer; **keyboard UP post-latch → Single Event (union proven)**; real triangle → Options; ENTER/X → Game Options; 60 s idle → still Game Options |
| 4 (mapping, `134616db`, +`PS2X_PAD_LOG=1`) | 12 buttons + 4 dpad keys + hat X/Y + 6 stick deflections + GAS/BRAKE + START at title: **49 padlog lines, every line the predicted word** (§2); START → menu; 60 s idle → log silent, still menu |

Scap SHAs: `logs/launchN-scap-sha.txt`. Ticks are diagnostic
(frame-dump build), not speed.

## 5. Hands-on test for Brad (BLOCKER — needs Brad + 2 min)

Inference to close: physical X/Y button positions (§1). Staged state:
padlog APK `134616db…` installed, device env =
`scripts/ps2x-launch4.env` (`PS2X_PAD_LOG=1`, no script); a worker
records logcat during the test.

1. Worker: `adb logcat -c`, start `adb logcat -b main -s ps2x`, launch
   the app, dismiss the USB dialog, wait for the title (~25 s).
2. Brad, at the title (about 30 s of pressing): **hold physical X
   (left face) 3 s** → release; **hold physical Y (top) 3 s** →
   release; **hold the left stick full-left 3 s** → release; **press
   START**; at the menu **press A**.
3. Pass: log shows `btns=0x7fff`, then `0xefff`, then `lx=01`, then
   `0xfff7` + menu on screen, then Select Character on screen.
   (Anything else = the X/Y firmware-compensation reading is wrong;
   say exactly which line differed.)

## 6. Findings

1. Real controller input works end to end on the Odin with a correct
   mapping; the only code gap was the gamepad/keyboard if/else, now a
   union on Android.
2. `input keyevent` BUTTON_* can never reach the game (virtual-keyboard
   source + raylib drops BUTTON_* in its keyboard map); DPAD/letters
   work via the keyboard map. `sendevent` on event8/event5 is the
   deterministic injector for both paths (holds, exact timing).
3. Odin ROM transposes kernel 307/308 → BUTTON_X/Y in its own vendor
   keylayout; physical positions inferred correct (§1), Brad confirms.
4. Analog triggers (GAS/BRAKE axes) intentionally produce no PS2 input;
   digital L2/R2 come from the 312/313 keys. MODE is intentionally
   unmapped.
5. No phantom input in three 60 s windows (SC screen pixels, Game
   Options pixels, menu padlog silence).

## 7. Recommendation (orchestrator decides)

1. ACCEPT the union fix + padlog diagnostic on `n2-android` (both
   Android-only, script precedence untouched); fold or drop per E.
2. Run the §5 hands-on to close X/Y positions (only open mapping item).
3. Keep `sendevent` (event8 gamepad / event5 keyboard) as the standard
   Odin input injector; `input keyevent` only for bursts.

## 8. Gaps

- Physical X/Y positions inferred (§1), not pressed (§5 test staged).
- Circle/square/triangle/select/L1–R3 proven as PS2 bits via padlog,
  but only START/cross/dpad/triangle also proven through game-screen
  transitions (deeper menus run ~0.1–0.2 ticks/s, too slow for
  per-button screen tests).
- Stick linearity/centering beyond ±max/center not measured (one byte
  each end + center per axis).
- The title→menu→SC route proof (launch 2) is one ENTER burst covering
  two transitions; stepwise injected ENTER-then-X was not isolated
  (launch-3 detour into Options).
- `~/dev/ssx3-work/N6/` = 290 MB (2 APKs + scaps + logcats); share
  mirror `/Volumes/share/ssx3/N6/`.

## Receipts

- In-repo: `scripts/` (4 launches + 4 envs), `logs/` (getevent,
  keylayout, dumpsys devices, n2-android diff, apk pins, 4 scap-SHA
  lists, launch-4 padlog + press marks).
- `~/dev/ssx3-work/N6/`: `app-release.apk` (`cd4b9330…`),
  `app-release-padlog.apk` (`134616db…`), `launch1..4/` (scaps,
  logcats, ticks). Share mirror `/Volumes/share/ssx3/N6/`.
- Bytesize: `n2-android` = `65c95d9` (local-only, never pushed);
  build logs `~/n2/logs/build6-assembleRelease.log`,
  `~/n2/logs/build7-assembleRelease.log`.
- Leases: Odin claimed `N6 2026-09-23T15:36Z`, released after
  force-stop + `/data/local/tmp/n6` removal; bytesize built only while
  `pgrep -f pcsx2` was idle.
