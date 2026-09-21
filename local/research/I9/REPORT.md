# I9 — Boot REAL ELF on iPad: guest binary + argv probe to run()

- Date: 2026-09-20. Tables, no verdicts.
- `local/research/I8/REPORT.md` read first (all of it: device toolchain + SDL2 iphoneos prebuilt + Release device build, provision/install via MF1's mechanism, `3006a07` CFBundleName fix on topic branch `i8-device-bundle-name`, miniaudio green on device, loadELF RAN on the probe path; gap 4 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P`, iPadOS 27.0 (`24A437`) — same OS build as I8's iPhone.
- Fork: separate worktree `/Volumes/Extreme SSD/ps2x-i9/fork-wt` at pinned `b6252bb` + topic-branch checkout of `3006a07` (exact hash, zero new fork commits, zero pushes). Shared clone untouched except the one `worktree add` + read-only inspection (E5 owns it).
- Product: `/Volumes/Extreme SSD/ps2x-i9/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app` — byte-identical binary to I8 (`77d1a396…`, 2944712 B). Installed on the iPad as `org.ps2x.ps2entryrunner` with the real `SLUS_207.72` (3890784 B) shipped as a bundle resource.
- Rules honored: subordinate to E5 (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i9/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; app fate from console + `.ips`, never exit code; screenshots to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I9/` standalone, `[I9]` commit, no push.
- Outcome shape: argv probe with the REAL guest ELF reaches `run()` — `loadELF` opens/parses `SLUS_207.72` (K1 provenance arm fires), the EE scheduler dispatches the main thread at entry `0x100008`, then a NEW named wall: `hasFunction(0x100008)` is false (empty recompiled-function table — `registerFunction` has no callers in the RECOMP-off device build), the thread goes Dormant, the scheduler idles (`[ee:idle]`), the host loop keeps presenting black frames, no crash, no `.ips`, deterministic across 2 launches.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i9/`, `WT` = `W/fork-wt` (fork worktree), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E5-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The real guest ELF shipped through the app's own input mechanism reaches `run()` on the iPad and executes guest code, or a NEW named wall appears past I8's `Failed to open/load ELF` probe fate |
| Observable | Device build exit; force-install exit + apps-list; guest ELF presence via the app's own path; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`) + screenshot; same-fate-vs-new-wall table vs I8 |
| Alternatives | H-a `run()` reached + guest executes (further than any probe). H-b new wall past `loadELF` (layer named with evidence). H-c same fate (`Failed to open/load ELF` — shipping failed) |
| Stop | All bars tabled (build/install/ship/boot/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~1 h wall; box not binding) |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 20 GB | 3.3 GB (17%) | `du -sh W` after evidence step |
| Evidence `local/research/I9/` | ≤ 5 MB | 2.2 MB, 14 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i9-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 (Xcode `-jobs 2`; no SDL rebuild — I8 prebuilt reused) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no `ssx3` push | 0 fork edits, 0 commits, 0 pushes | `status` clean, §Task 1 |

## Task 1 — Input mechanism + worktree + build (no iPad)

### Pin + worktree + `3006a07`

| Item | Receipt |
|---|---|
| Pin | `b6252bb` (brief's pin); `rev-parse` confirms `b6252bbc0f25e195f9650943149bfb38c83829d4` |
| Remote HEAD (tabled) | `fork/ssx3` at `a13b66a` (`[E4] Steady-frame GS boundary capture taps…`); shared clone `ssx3` also `a13b66a` (E5's line moved past I8's `b34b481`) |
| Worktree | `git -C FORK worktree add --detach W/fork-wt b6252bb` → `HEAD is now at b6252bb` (`logs/worktree-add.log`); `status` clean |
| `3006a07` method | **Topic-branch checkout** (not cherry-pick): `git fetch fork i8-device-bundle-name` + `checkout --detach 3006a07` → exact hash preserved, zero new commits. `ls-remote` confirms the branch tip is `3006a07d7ef7c5a4fce43c0a78e6c6c3b9871cbc` |
| Fix present | `CFBundleName = ps2EntryRunner` in `ps2xRuntime/ios/Info.plist` + in the build-dir copy at FIRST configure (no I8-style reconfigure needed) |
| Shared-clone contact | One `worktree add` + read-only `log / rev-parse / ls-remote / worktree list`; no reads of its working tree, no builds, no checkout/pull/stash |
| Sidecars | 327 `._*` in fresh worktree → purged → 0; `status` clean after |

### Guest-input mechanism (from source, BEFORE shipping anything)

| # | Finding | Code proof |
|---|---|---|
| 1 | argv[1] is the ONLY input in this build: non-empty `argv[1]` → used verbatim as the ELF path (`Using argv boot path`) | `ps2xRuntime/src/main.cpp:155-161` (`getExecutablePath`) |
| 2 | No container-relative or bundle-resource lookup exists: the path goes to `std::ifstream` open inside `loadELF` | `ps2_runtime.cpp:831-840` (`loadELF` opens `elfPath` directly) |
| 3 | `PS2X_DEFAULT_BOOT_ELF` fallback is compiled OUT (CMake default `""` → `PS2X_DEFAULT_BOOT_ELF_DEFINE` empty → no `-D`) | `ps2xRuntime/CMakeLists.txt:61,160-165,518-520`; no-arg launch = clean fatal (I8 launch A) |
| 4 | Companions are DERIVED, not required: `configureIoPathsFromElf` sets hostRoot/cdRoot = ELF dir, mc0 = ELF dir + `/mc0` — pure path config, no existence checks | `ps2_runtime.cpp:1123-1138` |
| 5 | Only optional companion: `PS2X_CD_IMAGE` env → `ioPaths.cdImage` (unset on device; CD path not needed to reach `run()`) | `main.cpp:242-250` |
| 6 | Shipping decision | Bundle resource + argv absolute path: copy ELF into staged `.app` pre-sign, pass `installationURL + /SLUS_207.72`. `devicectl` offers NO bundle-listing domain (`appBundle` rejected; valid: `temporary, appDataContainer, appGroupDataContainer, systemCrashLogs`), so presence is verified by the app's own open (absence of `Failed to open ELF file`) |

### Guest ELF provenance

| Item | Receipt |
|---|---|
| Source | `/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72` (P1 extraction; `P1/cd/` copy identical) |
| Size | 3890784 B (matches brief) |
| sha256 | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` — matches P1's tracked record (`local/research/P1/REPORT.md:173`) |
| Companions shipped | NONE — per mechanism rows 4–5 nothing else is provably required |

### Toolchain + SDL2 (reuse; every iPad-vs-iPhone delta tabled)

| # | Item | I8 (iPhone) | I9 (iPad) | Delta? |
|---|---|---|---|---|
| 1 | Toolchain file | `local/research/I8/logs/ios-device.toolchain.cmake` | `logs/ios-device.toolchain.cmake` | NONE — byte-identical copy (`diff` clean) |
| 2 | Arch | arm64 (`CMAKE_OSX_ARCHITECTURES arm64`) | same | none |
| 3 | Sysroot / signing | `iphoneos`, signing OFF | same | none |
| 4 | Min SDK / OS | minos 27.0 / iOS 27.0 (`24A437`) | minos 27.0 / iPadOS 27.0 (`24A437`) | none (same build train) |
| 5 | SDL2 | fresh `release-2.32.10` iphoneos prebuilt (`W-i8/sdl2-ios-device`) | REUSED read-only (`-DSDL2_DIR` → I8's install; `libSDL2.a` Non-fat arm64) | build step skipped; I9 lane holds no SDL tree |
| 6 | raylib | `FETCHCONTENT_SOURCE_DIR_RAYLIB` → I4's `raylib-5.5` | same (0 sidecars at check) | none |
| 7 | Compiler | `CC=Homebrew clang`, `CXX` unset | same | none |
| 8 | Configure flags | `-G Xcode`, Release-only, RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | identical | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0 (`Configuring done (77.1s)`, `Generating done (2.4s)`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (`logs/ios-runtime-build-tail.log`; full log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 2944712 B / `77d1a3960a3e26102786a1b980fd56111b6a4698a9b8cd975ed0edb370510ce7` — BYTE-IDENTICAL to I8 |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0 / sdk 27.0` |
| SDL count | 296 `T _SDL_` — identical to I8 |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (built plist; no rename) |
| Build tree | part of `W` 3.3 GB total |

## Task 2 — Provision + force-install + real boot (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 (`24A437`), UDID `P`, connected (`logs/ipad-details.json` + stdout log on SSD).

### iPad state before install (running sessions are the user's — reported, not killed)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check (both physical devices + 4 shutdown sims in `list devices`); no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 566-line list pre-install; 0 `ps2` matches. Only OUR 2 probe PIDs ever signaled (4076 via `--terminate-existing` on launch 2, 4080 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0 |
| Installed apps | No prior `org.ps2x.*`; `MF1Probe` (`com.bradrichardson.mf1probe`) present, never launched/touched. Post-install: `ps2EntryRunner org.ps2x.ps2entryrunner` listed |
| Post-brief state | Our instance terminated; app left installed (MF1/I8 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (install 180, launches 60/30, info 60/30) |

### Provision + sign + install (I8/MF1 mechanism reused; every delta tabled)

Profile: `f0793278-…` (`iOS Team Provisioning Profile: *`, XC Wildcard, team `LQ3V7772Q2`) — verified to CONTAIN the iPad UDID (1 match; 2 other dev profiles also contain it, 7 do not). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I8 shape | I9 delta |
|---|---|---|
| Stage | `cp -R` unsigned `APP` → `SAPP` | identical + `cp SLUS_207.72` (3890784 B) into bundle root pre-sign; purge regenerated `._*` (0 after) |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical (same profile covers the iPad) |
| Entitlements | 3 keys (`application-identifier`, `com.apple.developer.team-identifier`, `get-task-allow`) | identical bytes (`logs/entitlements.plist`; matched against I8's file before signing) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, ON ExFAT | identical — exit 0, `codesign --verify --strict` exit 0; `Identifier=org.ps2x.ps2entryrunner`, `TeamIdentifier=LQ3V7772Q2`, `Authority=Apple Development: Brad Richardson (E4R78PLLKY)` |
| Install | `devicectl device install app --timeout 180` (no force flag in I8) | `--force-install` does NOT exist in this `devicectl` (exit 64 `Unknown option` — usage has no force/replace flag); plain install is force-equivalent on this fresh target (no prior `org.ps2x.*`). Install exit 0: `bundleID org.ps2x.ps2entryrunner`, `installationURL …/A5148C04-D14C-40DC-B48F-D487651D0123/ps2EntryRunner.app/` (`logs/install.log`) |

### Guest ELF on-device path + presence

| Item | Receipt |
|---|---|
| Device path | `/private/var/containers/Bundle/Application/A5148C04-D14C-40DC-B48F-D487651D0123/ps2EntryRunner.app/SLUS_207.72` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open: console shows NO `Failed to open ELF file` (the I8 probe-path line); instead `loadELF` proceeds to the K1 arm line naming the file (`[k1] armed … elf=SLUS_207.72`) + `SYSTEM: Working Directory` = the same bundle dir. Direct bundle listing is impossible via `devicectl` (no `appBundle` domain — rejection receipted) |
| Sandbox note | ELF dir (bundle root) is read-only, so the derived `mc0` path is not writable — untested this brief (guest never reached I/O); tabled as gap 4 |

### Launches (argv probe with the REAL ELF)

Fate from console + `.ips`, never exit code (device `devicectl` propagates: exit 2 = timeout-abort with the app alive).

| Launch | Shape | Result |
|---|---|---|
| R1 (real ELF) | `--console`, `--timeout 60` + bundle `SLUS_207.72` path | Exit 2 (timeout, app alive). Console (complete, 3483 lines, `logs/launch-realelf-console.log`; 58-line noise-stripped `logs/launch-realelf-dedup.log`): `Using argv boot path` → raylib 5.5 → `DISPLAY: Device initialized successfully` (820×1180 display, 640×448 screen/render) → `GLAD: OpenGL ES 2.0` → **Renderer: Apple M2 GPU** → `AUDIO: Device initialized successfully` (miniaudio \| Core Audio, 48 kHz) → **`[k1] armed name=ssx3-copied-payload elf=SLUS_207.72`** → **`[guest-branch:missing-target] kind=DirectJump op=EE scheduler source=0x100008 target=0x100008 pc=0x100008 … codeRegion=yes policy=1 trace=(empty)`** → **`[ee:idle] no runnable thread for 3s; threads=1`** + **`[ee:idle] id=1 status=5 waitReason=0 waitId=0 pc=0x100008 entry=0x100008`** → per-frame `GetWindowScaleDPI() not implemented` spam (~57/s) until the timeout abort. No teardown, no exception, no `Failed to …ELF…` |
| R2 (repeat) | `--console`, `--timeout 30`, `--terminate-existing` (fresh PID 4080) | Exit 2 (timeout). Dedup console matches R1 line-for-line modulo NSLog interleave order + PID/addresses (diff receipt in session; both 58 lines; 1× `missing-target`, 2× `ee:idle` each). DETERMINISTIC |
| Screenshots | 2 captures, internal `/tmp` path first then `mv` (ExFAT owner warnings only, files landed) | `i9-shot1.png` + `i9-shot2.png`, 2360×1640, byte-IDENTICAL: app window foreground (Stage-Manager portrait phone-aspect window, status bar names `ps2EntryRunner`), full-black content. Shot 1 committed as `logs/i9-shot1.png`; shot 2 scratch on SSD |

Crash-log record: `device info files --domain-type systemCrashLogs -s ps2EntryRunner` → `0 files:` after sleep + re-`ls` (`logs/crashlog-check.log`). No `.ips` on device across all launches. PID 4076/4080 observed alive; cleanup terminated only our PIDs.

### Same-fate-vs-new-wall table vs I8's probe-path fate

| I8 iPhone probe fate (`/nonexistent-boot.elf`) | I9 iPad real-ELF fate | Wall status |
|---|---|---|
| `Failed to open ELF file` + `Failed to load ELF file`, orderly teardown, idle, no `.ips` | No open/load failure; K1 arm fires; `run()` entered; scheduler dispatches entry; `missing-target` + `ee:idle` (Dormant); host loop presents black frames; no `.ips` | NEW WALL (H-b): past `loadELF`, walled at first guest dispatch — empty recompiled-function table |
| miniaudio init OK (48 kHz) | miniaudio init OK (48 kHz) | same |
| Renderer Apple A18 Pro GPU; 440×956 display | Renderer Apple M2 GPU; 820×1180 display | device characteristics only |
| Black window post-teardown idle | Black window, run-loop alive | same pixels, different process state |
| `GetWindowScaleDPI() not implemented` 1× (init) | same warning ~57/s (per-frame — proves the `run()` loop iterates) | new quantitative signal, benign source |

## Task 3 — Diagnosis (no fix attempted; wall is codegen class, not config class)

### Diagnosis: failing layer = empty recompiled-function table at first guest dispatch

| # | Claim | Evidence |
|---|---|---|
| 1 | `run()` IS reached and the guest main thread is created Ready at the ELF entry | `run()` spawns the game thread (`ps2_runtime.cpp:2863-2894`); scheduler `reset()` creates thread id 1 `Ready` with `entry = pc = 0x100008` (`EeScheduler.cpp:393-404`); console `ee:idle` line confirms `id=1 … entry=0x100008` |
| 2 | First dispatch finds NO recompiled function for the entry and reports it | Scheduler loop: `!hasFunction(context.pc)` → `reportMissingFunction(… DirectJump, "EE scheduler")` (`EeScheduler.cpp:702-712`) — matches the console's `op=EE scheduler`, `source=target=pc=0x100008`, `policy=1` (= `ContinueToTarget`, the default in `ps2_runtime.h:333-339,527`); `codeRegion=yes` proves the ELF bytes ARE mapped — only the compiled function is missing |
| 3 | The thread is then Dormant and the scheduler idles forever | Same block calls `makeDormant(*running)` (`EeScheduler.cpp:737`); `status=5` = `Dormant` in `EeThreadStatus` (`ee_scheduler.h:25-33`); loop head prints `[ee:idle]` after 3 s with no runnable thread and no pending invocations, then `waitForEvent()` (`EeScheduler.cpp:540-568`) |
| 4 | The table is empty BY CONSTRUCTION in this build: `registerFunction` has zero callers in `ps2xRuntime/{src,include}`; the linked `register_functions.cpp` is only a zeroed `g_ps2RecompiledFunctionTable` stub | `grep registerFunction` → decl/def only; `src/runner/register_functions.cpp` = table of `{}` |
| 5 | Functions come only from the OFFLINE host recompiler, which is excluded here | `ps2xRecomp` generates registration + function objects from `games/ssx3/ssx3.toml` via `ps2_recomp` (`ps2_recompiler.cpp:1661`, `code_generator.cpp:292`); device build sets `PS2X_BUILD_RECOMP=OFF` (top `CMakeLists.txt:16` default ON, I8/I9 configure forces OFF); runtime `CMakeLists.txt` wires NO `games/` objects at all |
| 6 | No fallback execution path exists in the binary | No `PS2X_BUILD_RECOMP`/`HAS_RECOMP` guards in `ps2_runtime.cpp`; no interpreter sources under `src/lib`; policy `ContinueToTarget` only logs + unwinds (`ps2_runtime.cpp:1738-1801`) |
| 7 | The host side is healthy throughout | Init/GL/audio all OK; run loop iterates (~57 DPI warnings/s); no exception/teardown/crash lines; 0 `.ips`; process alive at both timeouts; fate deterministic across 2 launches |

### Fix analysis (config-level only per the brief — none qualifies)

| Candidate | Class | Outcome |
|---|---|---|
| Build flags (`PS2X_BUILD_RECOMP=ON`, analyzer on) | flag, but pulls a NEW subsystem into the device slice | NOT attempted: the host recompiler + generated game objects were never built for `iphoneos`; wiring game codegen into the iOS link is fork-build work, not a flag flip (and on-device JIT would need `dynamic-codesigning`/MAP_JIT entitlement design) |
| Plist / paths / packaging / env | config | Nothing in this class fills the function table (claims 4–6); no-op by inspection |
| `MissingFunctionPolicy::Stop` | behavior flag (default is `ContinueToTarget`) | Would only convert the idle into a stop — changes the symptom, not the wall; not attempted |

Fix attempted: NONE. Guest-boot stall is a finding, not a fix mandate (brief Task 3).

Contract outcome: **H-b** — new wall past `loadELF` (`run()` reached, guest dispatched once, Dormant-at-entry on the empty function table). The ONE next action: **generate the SSX3 recompiled objects on the host (`ps2_recomp games/ssx3/ssx3.toml`) and link them into the iphoneos device runtime** (or ship them as a game-objects static lib the device build consumes), then re-probe — that is a fork-build/codegen brief (app/fork-code class), not a device-harness brief.

## Exact commands

```sh
# --- Task 1: read-only pin verification + worktree (FORK otherwise untouched) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i9"
git -C "$FORK" log --oneline -8; git -C "$FORK" rev-parse b6252bb
git -C "$FORK" ls-remote fork ssx3   # a13b66a (E5's line; tabled, not touched)
git -C "$FORK" worktree list
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I9/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" b6252bb     # the one metadata write
# --- 3006a07 via topic-branch checkout (exact hash, no new commit) ---
WT="$W/fork-wt"
git -C "$WT" fetch fork i8-device-bundle-name
git -C "$WT" checkout --detach 3006a07
git -C "$WT" log --oneline -2; git -C "$WT" status --short
find "$WT" -name "._*" -delete   # 327 -> 0
# --- Input mechanism (source reads; Table 1 rows 1-5) ---
grep -rn "loadELF\|Using argv\|executable path" "$WT/ps2xRuntime/src" "$WT/ps2xRuntime/include"
sed -n '100,280p' "$WT/ps2xRuntime/src/main.cpp"
sed -n '1123,1138p' "$WT/ps2xRuntime/src/lib/ps2_runtime.cpp"   # configureIoPathsFromElf
# --- Guest ELF provenance ---
stat -f "%z %N" "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (== P1 record)
# --- Toolchain (byte-identical reuse) + SDL2 prebuilt check ---
cp local/research/I8/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"
cp local/research/I8/logs/ios-device.toolchain.cmake local/research/I9/logs/ios-device.toolchain.cmake
diff local/research/I8/logs/ios-device.toolchain.cmake local/research/I9/logs/ios-device.toolchain.cmake
lipo -info "/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/libSDL2.a"  # Non-fat arm64
# --- Runtime configure + build (I8 shape, -j2) ---
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -S "$WT" -B "$W/ios-runtime-device"                            # exit 0 (77.1s+2.4s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2   # BUILD SUCCEEDED
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 77d1a396... (== I8)
codesign -dvv "$APP"   # not signed at all (by design)

# --- Task 2: iPad recon (state reported, nothing killed) ---
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details.json"
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 566 lines, 0 ps2
xcrun devicectl device info apps --device "$P" --timeout 60        # no org.ps2x.*
# --- Profile coverage check (roster scan) ---
for f in ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/*.mobileprovision; do
  security cms -D -i "$f" | grep -c "$P"   # f0793278 (XC Wildcard *): 1
done
# --- Stage (bundle resource ship) + sign (I8 mechanism) ---
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"
cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
# (write 3-key entitlements.plist; diffed against I8's file first; see logs/entitlements.plist)
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0
codesign --verify --strict "$SAPP"                              # exit 0
# --- Install (--force-install does not exist; exit 64; plain install is force-equivalent here) ---
xcrun devicectl device install app --device "$P" --timeout 180 "$SAPP"   # exit 0
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -i ps2
# --- Bundle-listing attempt (no appBundle domain; rejection receipted) ---
xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type appBundle --domain-identifier org.ps2x.ps2entryrunner  # invalid value
# --- Real-ELF argv probes + crash-log + screenshots ---
ELF="/private/var/containers/Bundle/Application/A5148C04-D14C-40DC-B48F-D487651D0123/ps2EntryRunner.app/SLUS_207.72"
xcrun devicectl device process launch --device "$P" --timeout 60 --console \
  org.ps2x.ps2entryrunner "$ELF" >"$W/logs/launch-realelf-console.log" 2>&1   # R1: exit 2 (alive)
xcrun devicectl device process launch --device "$P" --timeout 30 --console --terminate-existing \
  org.ps2x.ps2entryrunner "$ELF" >"$W/logs/launch-realelf2-console.log" 2>&1  # R2: exit 2, deterministic
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i9 -s ps2EntryRunner --no-recurse  # 0 files
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i9-shot1.png
sleep 3; xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i9-shot2.png
mv /tmp/i9-shot1.png /tmp/i9-shot2.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4080  # cleanup only
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Device runtime links ZERO recompiled guest functions (Dormant-at-entry wall) | `registerFunction` callerless + stub table + `missing-target`/`ee:idle` console pair (Task 3 claims 2–5) | Fork-build/codegen brief: run host `ps2_recomp games/ssx3/ssx3.toml`, link game objects into the iphoneos runtime (or a game-objects static lib), re-probe on iPad (THE one next action) |
| 2 | `3006a07` still rides topic branch `i8-device-bundle-name`, not `fork/ssx3` | Remote `ssx3` at E5's `a13b66a`; I9 added 0 commits (checkout reuse) | No code brief — merge/cherry-pick onto `ssx3` when E5's line allows (unchanged from I8 gap 3) |
| 3 | `--force-install` is not a `devicectl` option (brief's standing policy names a nonexistent flag) | Exit 64 `Unknown option` + usage text with no force/replace flag | Standing-policy note: plain `install` overwrites on fresh targets; re-test overwrite behavior on an occupied target before relying on it |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` derives `mc0` under the ELF dir; guest never reached I/O | Data-container brief (only if gap 1's guest reaches file I/O and fails): ship ELF via `appDataContainer` + File Sharing or a first-run copy-out, then argv into the container |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6/I7/I8 carried) | Untouched this brief | Optional hardening brief (unchanged) |

## Receipt paths

- `local/research/I9/REPORT.md` (this file)
- `local/research/I9/logs/ios-device.toolchain.cmake` (byte-identical to I8's)
- `local/research/I9/logs/worktree-add.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I9/logs/ipad-details.json`, `ipad-apps-pre.log`, `entitlements.plist`
- `local/research/I9/logs/install.log` (exit 0; `--force-install` exit-64 note in report body)
- `local/research/I9/logs/elf-device-path.txt`, `launch-realelf-console.log` (complete R1), `launch-realelf-dedup.log`, `launch-realelf2-dedup.log` (R2 determinism)
- `local/research/I9/logs/crashlog-check.log` (0 files after sleep + re-`ls`)
- `local/research/I9/logs/i9-shot1.png` (iPad window, black content, 2.0 MB)
- `W/logs/` (same + full R2 console, full build log, `i9-shot2.png`, process list, details stdout); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits incl. ELF); `W/fork-wt/` (worktree @ `3006a07`, clean, 0 new commits)
- No fork push this brief (nothing to push — `3006a07` reused from `fork i8-device-bundle-name`)

## What I could not do

- Execute a single guest instruction — the function table is empty by construction (gap 1 owns it); `run()` + scheduler dispatch + idle are the observed ceiling.
- Verify the ELF's on-device bytes directly — `devicectl` has no bundle-listing domain; presence is proven by the app's own open path (no `Failed to open`, K1 arm names the file).
- Test `mc0`/CD/file-I/O behavior — the guest never got that far (gap 4).
- Test install-overwrite semantics — the target was fresh, and no force flag exists (gap 3).
- Merge `3006a07` onto `fork/ssx3` — E5's line is ahead and mutating (gap 2; checkout reuse instead).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8); no crash occurred anyway.
- Render a guest frame — window is black with the run loop alive; first presented content awaits gap 1.
- Explain the `mv` owner/group warnings on screenshots — ExFAT noise only; files landed byte-complete (screenshot read + pixel-sampled from the landed copy).

## TAIL RECEIPT

Report written in 3 chunks (header + contract + Task 1; Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 292 lines, sha256 `85be749b953df882266a15f5c1acc4def699b39ec20c88f3a16bbcc9160e9a94`.
Tail content line: "Explain the `mv` owner/group warnings on screenshots — ExFAT noise only; files landed byte-complete (screenshot read + pixel-sampled from the landed copy)." This receipt line ends the report. END-I9-REPORT.
