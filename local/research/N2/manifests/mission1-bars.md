# N2 Mission 1 bars (B1–B6) — stub build at pin 3adc0478

Three attempts, same gradle invocation
(`assembleRelease -Pps2xBootElf=.../SLUS_207.72`):
build1 = verbatim N1-Mission-3; build1b = headers staged, detached (lost);
build1c = headers staged, foreground.

## B1 — exit + configure lines

| Attempt | Exit | Wall | First failure |
|---|---|---|---|
| build1 (verbatim) | 1 | 33 s | `ps2xRuntime/src/runner/register_functions.cpp:4:10: fatal error: 'ps2_recompiled_stubs.h' file not found` (same include in all 5 `sub_*.cpp`) |
| build1b (headers staged, detached) | none recorded | ~35 s then silence | whole tree vanished, no `build1b-exit.txt`, no survivors; cause undetermined (suspected launcher-session teardown; foreground runs after were stable) |
| build1c (headers staged, foreground) | 1 | 18 m 20 s | `ld.lld: error: undefined symbol: sub_*` ×9,436 (40 shown, then error-limit stop) |

Configure lines (Mission-1 `configure_stdout.txt`, both present):
`-- Android target detected, building runtime only`,
`-- FFmpeg disabled; MPEG video decode falls back to stub frames`.
B1 verdict: FAIL (exit ≠ 0 on every attempt that ran to completion).

Root causes (both pre-existing at the pin, neither a toolchain fault):
1. Generated header `ps2_recompiled_stubs.h` exists nowhere on a fresh clone;
   Android forces `PS2X_BUILD_RECOMP OFF`, so nothing generates it. Recovery
   (no source edits, no cmake-arg change): staged the 2 byte-matched C17
   headers into the repo-designated gitignored `ps2xRuntime/include/` slot
   (`.gitignore:16-17`; `check-ignore` receipted; functions.h
   `e2fa11e8…` byte-identical to the in-tree copy).
2. The in-tree "stub" table is the FULL 398,961-assignment table: it
   references 9,441 distinct `sub_*`, only 5 of which have in-tree bodies.
   NDK r28 lld enforces `--no-undefined` on the shared link, so the stub
   cannot link at this pin. N1's Mission-3 spec assumed linkability; that
   premise does not hold (see `logs/m1-evidence2.txt` H2/H3: 9,436 U + 5 T
   = 9,441).

## B2 — file

No `.so`, no APK (`so_count=0`, `apk_count=0`). Bar not applicable.

## B3 — symbols (from build-tree objects; provider hunt succeeded)

| Check | Result |
|---|---|
| `ANativeActivity_onCreate` provider | RESOLVED: `T` in NDK `android_native_app_glue.c.o`; `android_main` `T` in raylib `rcore.c.o`; `main` `T` in runner unity. Chain: NativeActivity → glue → rcore `android_main` → runner `main()`. No object *references* the entry (it enters via the `--undefined` link flag) — matches N1 M1.10 |
| `main` defined | yes (`T main` in runner unity object) |
| defined `sub_*` | 5 (`T`), exactly N1's prediction |
| `without FFmpeg` string | object-level check superseded by Mission-2 `.so` receipt (string present) |
| `ps2x` tag string | superseded by Mission-2 `.so` receipt (present) |
| FetchContent pins | raylib `c1ab645ca298a2801097931d1079b10ff7eb9df8` (E25 `c1ab645c` ✓), sse2neon `92f6de174717aef09033ad21568d5bb9e5470404`; no imgui/rlImGui dirs (Android gate holds) |

## B4 — size budget

No `.so`/APK. Bar not applicable.

## B5 — reproducibility seed

No `.so` produced. No seed. (Mission 2 did not re-run the full link; no
reproducibility pair exists for either mission.)

## B6 — zero-drift

Fork held at `3adc0478b6d2260acdd28a249466f2eef9a20176` throughout Mission 1;
zero commits; untracked files = generated `android/gradlew*` only; staged
headers are gitignored (not shown in `git status`). E-lane SSD checkout
never checked out or written (all fork reads via `git show`).
