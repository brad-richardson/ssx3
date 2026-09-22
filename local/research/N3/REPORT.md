# N3 — First PS2-recomp boot on the Odin: title screen on launch 1

- Date: 2026-09-22. Brief: `local/muse/prompts/N3.md`.
- Read first, in full: `local/research/N2/REPORT.md` + manifests, `local/research/N1/REPORT.md` §P1–P8/H4–H7, `local/research/E29/REPORT.md`, `AGENTS.md`, `local/AGENTS.local.md`, `local/muse/prompts/E31.md`, I24 §Task-2 rows, G41 run script.
- HEADLINE: stock SSX 3 title screen renders and animates on the Odin 3 on the first launch — "Press START button" legible on screencap at t+20 s and still animating at t+310 s. Bars (a)(b)(d) met directly; (c) met by proxy (its log marker is compiled out of release builds — tabled below, not swapped silently).
- Budget: 1/3 launches, ~3 h of 6 h. No push anywhere; `n2-android` local-only on bytesize.

## Mission 1 — env shim + arm64 build (bytesize, branch `n2-android`)

| Step | Receipt |
|---|---|
| Fetch | `git fetch origin` (remote is `origin` on bytesize, not `fork`); `origin/e29-movie-bypass` = `ee39b9f` + `194133c` + scrubbed base. Those two commits only, per brief |
| Cherry-pick 1 | `194133c` [E29] bypass → `8c04667`, clean, 1 file +46 |
| Cherry-pick 2 | `ee39b9f` [E31] pad script → `b003c8a`, clean, 3 files +489 |
| Shim commit | `6ec61ee` [N3-local]: 5 files, +216/−0 (see design rows) |
| arm64-only commit | `619d48a` [N3-local]: `abiFilters 'arm64-v8a'` (was + x86_64), 1 line |
| Ref hygiene | Local `ssx3` = `3adc0478` unmoved; tree clean except N2's untracked wrapper files; zero pushes. Full log: `logs/branch-log.txt` |

Shim design (all in `shim/` + `shim/wiring.txt`):

| Piece | Content |
|---|---|
| `ps2xRuntime/include/ps2_android_env.h` (new, 93 lines) | Platform-neutral parser: `KEY=VALUE` lines, `#` comments (leading-ws tolerant), blank skip, first-`=` split, ASCII-trim, malformed/empty-key ignored, CRLF tolerant; plus `envFilePathForBootElf()` = dirname(`PS2X_DEFAULT_BOOT_ELF`) + `/ps2x.env` |
| `ps2xRuntime/src/lib/ps2_android_runtime.cpp` (+48) | Android-only (`#if defined(__ANDROID__)`): static-initializer loader runs before `main()` reads anything; `setenv` per entry; every key logged to logcat tag `ps2x`; one line when the file is absent. Shared code untouched (no `main.cpp` edit) |
| `ps2xTest/src/ps2_android_env_tests.cpp` (new, 72 lines) | 4 MiniTest cases mirroring the pad-test idiom exactly (`MiniTest::Case`/`tc.Run`/`t.Equals`/`t.IsTrue`); wired via 3 lines (CMakeLists:50, main.cpp:9/:32) |
| Host test | Real TU + real MiniTest header compiled with `g++ -std=c++17 -Wall -Wextra`: 0 warnings, **4/4 pass** (`logs/unittest.txt`). Wiring name-checked by grep. Full 465-test suite build NOT attempted (WSL restarted twice mid-mission; Linux host build is unproven ground — see Anomalies) |

Build bars (`./gradlew assembleRelease`, same N2 recipe, `logs/build3-bars.txt` + `logs/so-probe.txt`):

| Bar | Value |
|---|---|
| Exit | 0, BUILD SUCCESSFUL in 17 s (incremental), 0 `error:` lines |
| arm64 `.so` (unstripped) | 905,591,144 B, `e75fd86e…`, ELF aarch64, BuildID `22250126…` |
| APK | 134,162,896 B, `69a79e29a0955b31c50771367ca0847f706e36cfacc71b7cab8b4814ab16e466` — build tree + Windows landing + SSD ×2 reads (45 s apart) all agree |
| APK members | Single ABI: `lib/arm64-v8a/libps2EntryRunner.so` only (+ dex/manifest/arsc/metadata) |
| Symbols | `T ANativeActivity_onCreate`, `T main`, game `sub_*` **9,441/9,441 distinct `T`, 0 `U`** (mangled `_Z…sub_…`; my first probe pattern was wrong, corrected in `so-probe.txt`) |
| Strings | `PS2X_SKIP_MOVIE` ×1, `PS2X_PAD_SCRIPT` ×2, `ps2x.env` ×4, `ps2x.env: set ` ×1, `SLUS_207.72` ×3, `[MPEG] … without FFmpeg…` present |
| `[MPEG:DEV-SKIP-MOVIE]` | **×0 — compiled out.** The marker sits inside `PS2_IF_AGRESSIVE_LOGS`, gated by `#if AGRESSIVE_LOGS` ← `PS2X_ENABLE_AGRESSIVE_LOGS` (default OFF, `ps2xRuntime/CMakeLists.txt:16`). Same gate removes `[MPEG:feed*]`, `[MPEG:GetPicture]`, `[frame:upload]`, `[diag:stubs]` from this build. The bypass *code* (`streamEnded=true`) is compiled in — only the trace is gated |

## Mission 2 — stage + launch on the Odin (lease 18:10:08Z–18:18:18Z)

Pre-flight: lease free (claimed `N3 2026-09-22T18:10Z`, released after pulls); device unlocked (`deviceLocked=0`, uptime 1 d 22 h); battery 62% but **not charging** (USB-powered false, status discharging — deviation from the "≥20% and charging" clause, proceeded: 62% ≫ needs, no action available to change it; ended 59%).

| Step | Receipt |
|---|---|
| Install | `adb install` (plain, app already present? no — fresh) → `Success`, 18:10:16Z |
| Stage | `ps2x.env` 220 B (`87bae945…` on device), `SLUS_207.72` 3,890,784 B (`1b49d05c…` ✓ on device), `SSX3.iso` 3,005,415,424 B pushed in 50.5 s @56.8 MB/s, `3c2f8eb1…` ✓ on device. SSD ISO ×2 reads separated ~1 h, both `3c2f8eb1…` |
| Launch | `am start -n com.ps2x.runner/android.app.NativeActivity`, pid 7755, same pid all 15 ticks, alive at loop end, force-stopped after pulls. 5-min loop, 15/15 screencaps, 5/5 cpu+thermal snapshots |
| Logcat | Filtered `ps2x+raylib` 19,873 lines + full main/system/crash to `/Volumes/Extreme SSD/n2-android/n3-launch1/`. Crash buffer: **0 FATAL/tombstone/died/ANR** |
| Mission 2.5 | Not taken: E31 has no REPORT (6 boots run, `e31a–e31f` results on SSD, no verdict) → precondition unmet |

Bar table (device clock; t0 = 14:12:02.767 first shim line):

| Bar | Time | Evidence |
|---|---|---|
| (a) shim keys on `ps2x` tag | t+0 s | `ps2x.env: set PS2X_CD_IMAGE/SKIP_MOVIE/FRAME_DUMP_DIR` at 02.767 — H5/H6 proven on device |
| (b) ELF loads, guest starts | t+0.1 / t+0.9 s | `Using default boot file` 02.770; `[k1] armed … elf=SLUS_207.72` 02.900; IOP module loads 03.6–04.1 (CD reads via ISO work); first guest frame (fallback=0, fbp=112, 512×448) 03.692 |
| (c) bypass arms | proxy window t+5…t+20 s | Marker N/A (compiled out — see Mission 1). Proxy: `[MPEG] without FFmpeg` 07.612; guest never parks — 6,557 real frames flow continuously with 1,510 distinct fnv; thread-1 Mpeg-park lines absent; title on screen by t+20 s (a parked run shows 42 frozen frames per E29) |
| (d) title renders | ≤ t+20 s, live at t+310 s | scap-00 (t+20 s) and scap-14 (t+300 s) read directly: SSX 3 logo, "Press START button", "© 2003 Electronic Arts Inc." All 15 screencaps byte-distinct (`logs/scap-shas.txt`); upload sidecars `upload-latest.txt` seq=6599 |

Performance notes (not bars — CPU GS backend):

| Note | Value |
|---|---|
| Guest frame dumps | 6,592 total (35 fallback + 6,557 real), seq 0→6591 over 309.7 s ≈ **21.3/s** avg; thirds 22.9 / 21.0 / 20.1 per s (mild taper, cause undetermined) |
| App CPU | **156%** (≈1.5 cores, ~all user) in the run window; device load ~9–11 throughout (9.25 already before launch — pre-existing churn) |
| Thermal | cpu-1 zones **~103–104 °C steady** across all 5 snapshots (no pre-launch baseline; attribution unclear) |
| Battery | 62% → 59% over staging + run |

## Findings (table exactly, no verdicts)

1. **Frame PNG export fails on Android**: every dump logs `raylib FILEIO: […/frames/upload-latest.png] Failed to open/export` — the `.txt` sidecars (same dir, std::ofstream) succeed, so it is raylib `ExportImage`, not a path/permission issue. Evidence carried by screencaps + sidecars + fnv log lines instead. Next lane: E/G file bug, or switch dump writer off raylib.
2. **Thin vertical line artifact** at the right edge of the game viewport in scap-00 and scap-14 (same position both) — rendering or viewport-scale edge; needs a G-lane look, not a blocker.
3. **`[guest-branch:missing-target]`** once at 07.640 (`JALR … target=0x3b1140`, policy=1, wide guest trace): boot continued to the title; informational for E.
4. **WSL on bytesize restarted twice** (~13:59, ~14:17 UTC; tmpfs wiped, ext4 + git intact). Killed both detached-launch attempts of the host suite build; explains N2's build1b vanishing. Foreground-only work on that box until the cause is found.
5. **E-lane fork worktree is mid-E31** (`e29-movie-bypass`, 6 boots, pad-script commit present, no REPORT). Untouched by N3 — all N3 fork reads came from the bytesize clone.

## Recommendation (orchestrator decides)

1. ACCEPT: first Odin boot reaches an animating stock title screen; shim + `ps2x.env` mechanism proven (covers H4/H7 class without runtime-semantic changes).
2. Next device step needs no new mechanism: once E31 validates a menu path on the Mac, the same `PS2X_PAD_SCRIPT` value rides `ps2x.env` on the next N-boot (string already in the APK).
3. RULE on bar (c) as written: recommend MET-BY-PROXY (behavioral proof above), or brief an `AGRESSIVE_LOGS=1` instrumented APK (needs a Gradle-exposed cmake arg — E-lane call) if E needs the trace lines on device.
4. File to E/G: frame-PNG export failure; viewport edge line.

## What N3 could not do

- Pin the bypass-arm instant (no aggressive logs in release builds).
- Run the full 465-test suite (standalone harness 4/4 is the test evidence; see Anomalies row 4).
- Take the 2.5 pad-script launch (E31 unverd
...[truncated 870 chars]