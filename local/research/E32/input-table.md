# E32 input table (step 1) — content compared against scrubbed `ssx3` @ `3d4feed`

Fork checkout `~/dev/PS2Recomp`. All `runner` diffs vs upstream `14b1e5cb`
are empty on every branch below (scrub holds).

| # | Source | Commits / files | Already on `ssx3`? | Fold decision |
|---|---|---|---|---|
| 1 | `fork/e29-movie-bypass` E29 `194133c` | `PS2X_SKIP_MOVIE` (MPEG.cpp +46/−0) | No (`PS2X_SKIP_MOVIE` grep-empty on `ssx3`) | FOLD as `6526329` |
| 2 | `fork/e29-movie-bypass` E31 `ee39b9f` | `PS2X_PAD_SCRIPT` (Pad.cpp +365, Pad.h +34, pad_input_tests +90) | No (`PS2X_PAD_SCRIPT` grep-empty) | FOLD as `5461ad8` |
| 3 | `fork/i23-ffmpeg-ios` `bbc8572` | FFmpeg-iOS wiring (CMakeLists +37) | No (`PS2X_FFMPEG_IOS_ROOT` grep-empty) | FOLD as `d824af0` |
| 4 | `fork/i23-ffmpeg-ios` `50775d0` | FFmpeg default ON for iOS (CMakeLists 1/1) | No | FOLD as `7bb956d` |
| 5 | `fork/i23-ffmpeg-ios` `d61bee0` | `PS2X_MPEG_VECTOR_PATH` (MPEG.cpp +135) | No (grep-empty) | FOLD as `9b3b077` |
| 6 | `fork/i23-ffmpeg-ios` `c36c5dd` | `ps2xRuntime/cmake/iOS-FFmpeg-7.1.1.md` (+55, new file) | No | FOLD as `bcdad38` |
| 7 | `fork/i23-ffmpeg-ios` `e74f1dd` | `PS2X_MPEG_FEED_TRACE` (MPEG.cpp +18) | No (grep-empty) | FOLD as `b329c21` |
| 8 | `fork/i8-device-bundle-name` `3006a07` | CFBundleName one-liner (Info.plist 4/1) | No (`ssx3` has empty `<string></string>`) | FOLD as `5ad0d81` |
| 9 | `archive/i10-codegen-dir` `3d2e22d` | `PS2X_GAME_CODEGEN_DIR` (CMakeLists +22) | No (grep-empty) | FOLD as `dbb63d7` (first commit on `fold`) |
| 10 | `archive/i10-codegen-dir-alt` `c4d0ea6` | Same mechanism (CMakeLists +22) | — | SKIP: hunk text byte-identical to #9 (only context line numbers differ); one copy folded |
| 11 | `archive/i21-drop-a` `996198a` | Drop in-tree `sub_*.cpp` when codegen dir set (CMakeLists +7) | N/A (scrubbed `ssx3` has no in-tree `sub_*.cpp`; configure reports "dropped 0") | SKIP in favor of #12 (see why) |
| 12 | `archive/i21-drop-b` `590d831` | Same wiring (CMakeLists +7) | N/A, same as #11 | FOLD as `bae962c`: hunk text byte-identical to #11, and this is the I23-line variant (ancestry includes `e74f1dd`), i.e. the one validated with the I23 FFmpeg wiring present |
| 13–19 | `archive/i11-map`…`archive/i17-map` (7 rows: 0x395730, 0x14f2a8, 0x156750, 0x243a80, 0x3a0158, 0x2c5300, 0x2c5358) | `games/ssx3/ssx3-functions.sweep.csv` +1 each | YES, all 7: each archive row byte-identical to the `ssx3` line; `git diff 3d4feed fork/archive/i17-map -- games/ssx3/ssx3-functions.sweep.csv` empty | SKIP all (already absorbed: 5 via E17 `4b446e6`, 2 via card-restore commits) |
| 20 | `archive/i18-tap` `16e1b9a` | `[diag:frame]` line (EeScheduler.cpp +14) | No | FOLD as `dcecf13`: sits strictly inside the `PS2X_DIAG_PERIOD_MS != 0` gate (EeScheduler.cpp:443), silent by default — meets the brief's env-gated criterion |
| 21 | New: `PS2X_DEINTERLACE` | weave default + bob restore (gs_cpu_backend.h/.cpp, ps2_gs_tests.cpp +2 tests) | No (new flag) | FOLD as `9b73ff7` (own commit, last) |

Nothing ambiguous: both variant pairs (#9/#10, #11/#12) are behavior-identical
(byte-identical hunk text), so the brief's stop rule did not trigger.
Map rows are byte-identical content matches, not SHA matches.
