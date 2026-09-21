# I18 — Instrument guest execution past 0x2c5358 (P1c periodic console sampler + [diag:frame] tap) and NAME the next layer

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I17/REPORT.md` read first (all of it: base moved to `9da21ff` + E12-row dedupe + 7 ports + 1-line CSV entry closed `0x2c5358` (I16 wall GONE — normalized dedup diff = exactly the wall line deleted, 0 additions), and NO successor wall is named: guest alive the full 90 s with a byte-identical event prefix, no crash, no new `.ips` two briefs running, screen still black; gap 1 = this brief; the I11–I17 map-entry line is DONE until a wall names an address again).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I17; the I17 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4316, I17's bundle UUID — relaunched after I17's cleanup by an unknown launcher, same pattern as I16→I17; state tabled in Task 2).
- BASE: MOVED `9da21ff` → `83fb4d6` (E-lane advanced exactly 1 commit; the `0x2c5358` row HAS landed fork-side inside `83fb4d6` itself — DEDUPE case again, as I17 predicted) — separate fork worktree at `83fb4d6` + ported I17's 7 non-`0x2c5358` commits (patches content-identical to I17's) + ONE local tap commit `16e1b9a` (14 lines, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane live: recon `M register_functions.cpp` + `?? ps2_log.txt`; end-of-brief peek identical).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9455 SSX3 sources, byte-identical lib sha to I17's — host `ps2_recomp` NOT re-run, map unchanged) on the E9 runtime + E11 read-only card-query taps + E12 card status predicate + E-lane card-result leaf + the I18 `[diag:frame]` tap, probed with `PS2X_DIAG_PERIOD_MS=15000`.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i18/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` ZERO runs (codegen skipped by the unchanged-map rule, tabled); fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging + evidence; evidence `local/research/I18/` standalone, `[I18]` commit, no push.
- Outcome shape: taps PROVE liveness (5 `[diag:frame]` + 5 `[diag:threads]` + 30 `[diag:thread]` + 5 `[diag:stubs]` + 82 `[diag:stub]` + 28 `[diag:syscall]` on the 90 s console; `guest-branch`/`missing-target` still 0) and NAME the next layer: guest is WAITING, not spinning — 6/6 threads `status=Waiting` with frozen pcs all 5 blocks (main in `sceMpegGetPicture` Mpeg wait @`0x3b1028`, zero decoded frames; workers in `WaitSema` @`0x423de8` on semas 26/30/31/32/36), steady state = a vsync-locked 13-function pump (thread 4, 900/15 s), vsync advancing full-rate while ALL GS/DMA counters frozen since boot, CD reads+callbacks ALL in the first ~15 s then 75+ s silence. No crash; no NEW `.ips` for I18 AND no late filing for I17 (three briefs running). Screen still black.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i18/`, `WT` = `W/fork-wt` (fork worktree), `W17` = `/Volumes/Extreme SSD/ps2x-i17/`, `C17` = `W17/codegen-output/` (reused read-only; NO `W/codegen-output/` this brief), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | A minimal console-sink execution tap (periodic pc sampling + frame/GS observation) names the next layer past `0x2c5358`: guest pc region/behavior (spinning / advancing / waiting — on an RPC sid? on vsync? on file I/O?) — where the event-driven console sees only silence |
| Observable | Tap-surface reads (named files/lines); tap commit (named file, local commit, diff); tap's own liveness receipt (predictable per-period console lines); codegen decision receipts; device Release build WITH game objects exit 0; install-overwrite behavior; instrumented-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present; first `ls` also checks for late I17 filing) + screenshot; named-layer tables (thread pcs/status, stub histogram, syscalls, frame counters, CD timing) |
| Alternatives | H-a guest spinning (one pc/hot loop dominates). H-b guest advancing (pcs move, histogram spreads, GS flows). H-c guest waiting (frozen pcs + wait reasons name the object). H-d taps blind too (no tap lines — obstacle receipted, not the layer) |
| Stop | All bars tabled (tap/liveness/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~90 min wall: worktree+ports → tap read/commit → configure 79s → build 7m14s → stage/sign ~40s → install 112s → probe 90s → analysis) |
| One gap | Task 3 attempts a fix ONLY if config-level; the named layer's fix gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 8.9 GB (11%) — device tree ~5.5G + signed app ~2.9G + WT ~350M + logs (NO codegen dir — C17 reused) | `du -sh W` after evidence step |
| Evidence `local/research/I18/` | ≤ 5 MB | 2.4 MB + REPORT, 16 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i18-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`) | exact commands + build log line |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 8 local commits (7 ports + 1 tap), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 0 runs (skipped: map unchanged — tabled decision) | §codegen decision |
| Probe console committed | complete-or-extract | 2649-line deterministic diag extract (220 KB) + dormant samples + full-log shas (full 23245-line/13.9 MB console on SSD — over cap, tabled) | `logs/launch-cdimage-console.diag-extract.log` header |

## Task 1 — Dedupe + tap + link (no iPad)

### Pin + E-lane check + worktree + cherry-picks (BASE MOVED — dedupe case)

| Item | Receipt |
|---|---|
| Pin (MOVED) | `83fb4d6` = `83fb4d60904abb016522c477cce704c52118f95f` |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `83fb4d6` at recon AND at end-of-brief (E-lane advanced exactly once past I17's base) |
| Range `9da21ff..83fb4d6` | Exactly 1 commit: `83fb4d6` "SSX3: restore the exact card-result leaf" (Brad, 07:13:38 — after I17's 07:06 probe): CSV +1, `ps2_e7.h` 27-line change (`cardTarget` gains `source` param + E13 UI fields), `ps2_runtime.cpp` 1 line (call site) |
| `0x2c5358` row at HEAD (BEFORE writing) | CSV at `83fb4d6` contains `sub_002C5358,0x2c5358,0x2c53b0,0x58` count 1, same sorted position (below `sub_002C5338`, above `sub_002C53B0`) — BYTE-IDENTICAL to I17's `32d37e7` hunk (the convergence I17 tabled in the E-lane's uncommitted tree has landed) |
| Dedupe (both shas+bytes tabled) | E-lane hunk (`83fb4d60904a…`): `+sub_002C5358,0x2c5358,0x2c53b0,0x58` — byte-identical line + same position as I17's `32d37e794fd876…` hunk |
| SKIP (not ported) | I17's `32d37e7` (`0x2c5358` row) SKIPPED — already in base via `83fb4d6`; other 5 rows confirmed ABSENT at HEAD (`0014F2A8`/`00156750`/`00243A80`/`00395730`/`003A0158` count 0; `002C5300` count 1 from I17's base) |
| E-lane owner | Live — recon peek: shared `ssx3` @`83fb4d6` with `M register_functions.cpp` + `?? ps2_log.txt`; end-of-brief peek: IDENTICAL (no mid-brief edits this time; remote unmoved) |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 83fb4d6` → `HEAD is now at 83fb4d6` (exit 0) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; 4 reappeared pre-configure → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry** (SAME shape as I16/I17): `46d12d3` = `71c2690` (Info.plist CFBundleName), `6a58c9e` = `258482d` (22-insertion CMake wiring), `7714a85` = `1b80226` (I11 CSV row), `a3bbabf` = `5ff15c4` (I12 CSV row), `6a37c90` = `028cf63` (I13 CSV row), `b9bcfe6` = `83126a6` (I14 CSV row), `fe017b2` = `7a8007a` (I15 CSV row); attempt 1 applied 3/7 then aborted on the transient dirty-tree complaint (tree verified clean); picks 4+5+6+7 applied individually exit 0; `logs/cherry-pick.log` |
| Patch identity | All 7 ports content-identical to I17's (`diff` of `^[+-][^+-]` lines clean for each pair) |
| Merged CSV | **Byte-identical to I17's merged CSV** (`diff` of `32d37e7:csv` vs `HEAD:csv` clean — E's `0x2c5358` now comes from base instead of a local commit, same bytes) |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / show / status / diff --name-only / diff <csv>`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | YES — `83fb4d6+46d12d3+6a58c9e+7714a85+a3bbabf+6a37c90+b9bcfe6+fe017b2` + new tap commit; NO tool binary run at all (codegen skipped — §decision) |

### Tap surfaces (read before writing — the mechanism is decided here)

| # | Surface (file:lines) | Sink / gate | What it can see | Fit for this brief |
|---|---|---|---|---|
| 1 | P1c periodic sampler: `EeScheduler::run` (`EeScheduler.cpp:427–538`) + `diagCallsPeriodicFlush` (`ps2_runtime.cpp:1213–1245`) + `diagSyscallsPeriodicFlush` (`Dispatcher.cpp:56–87`) | `std::cerr` = devicectl `--console`; env `PS2X_DIAG_PERIOD_MS` (unset = compiled in, silent) | Per period: `[diag:threads]` + per-thread `[diag:thread]` (id/status/waitReason/waitId/**pc**/entry/priority/scheduled) + `[diag:stacks]` (pc/sp/entry/invocations) + `[diag:stubs]` top-30 call-target histogram + `[diag:syscalls]` histogram + `[diag:cd]`/`[cd:callback]`/`[diag:dormant]` (same gate, `CD.cpp`/`EeScheduler.cpp:675,735`) | **CHOSEN (exists in-tree): wall-clock periodic, fires independent of guest event emission — sees silent waits where the event console cannot. Device path runs it: `PS2Runtime::run` → game thread → `m_eeScheduler->run()` (`ps2_runtime.cpp:3161–3167`)** |
| 2 | E7 ordered sink (`ps2_e7.h:39–92`) + E11/E12 card taps | FILE `$PS2X_E7_DIR/e7-events.txt`; env-gated; **tick-capped at 603** (`if (tick > 603u)` → COMPLETE + close) | Boot-window (ticks 0–603) card-query observations only | REJECTED: boot window long past by probe time; file lands inside the iOS sandbox (no retrieval domain — I9 receipt); 0 console lines I11–I17 |
| 3 | T1 park snapshot (`ps2_park_snapshot.h`, always-on tallies; write in `parkSnapshotWriteOnce`, `EeScheduler.cpp:233–337`) | FILE `$PS2X_DIAG_PARK_DIR/park-snapshot.{json,txt}` on SIGTERM or `PS2X_DIAG_PARK_TIMEOUT_MS` | Hot-pc cumulative, sema hists, RPC events, GS counters, thread/sema tables — the richest record | REJECTED: file-retrieval problem (same as E7); SIGTERM-via-`devicectl terminate` semantics unproven; P1c already streams the pc-critical subset to the console |
| 4 | `[run:tick]` host-loop sampler (`ps2_runtime.cpp:3185–3215`) | `RUNTIME_LOG`; `PS2_IF_AGRESSIVE_LOGS` | Host-side pc + dma/gif/gsw/vif every 120 loop iterations | REJECTED: compiled out (`AGRESSIVE_LOGS 0`, `ps2_log.h:20`); enabling flips build flags runtime-wide — bigger blast radius than one periodic line |
| 5 | Full dispatch trace (`formatDispatchHistory`, per-`dispatchGuestBranch` print) | `std::cerr` | Every inter-function transfer | REJECTED: millions of dispatches/90 s — floods + truncates the console and perturbs timing; the top-30 histogram is strictly smaller and sufficient (spin = 1 target dominates; advance = spread; wait = ~empty) |
| 6 | `PS2X_DIAG_SEMA` per-signal/wait lines (`EeScheduler.cpp:151–159`) | `std::cerr`, env-gated | Sema create/wait/signal ownership (WHICH sema, WHO signals) | NOT USED this probe — named as the next brief's first action (config-only relaunch, no rebuild): answers sema ownership, which P1c's `waitId` alone cannot |

### Tap commit (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Mechanism (ONE) | **P1c periodic sampler (in-tree, env-gated) + ONE new `[diag:frame]` line per period** — periodic pc sampling (in-tree `[diag:thread]` pcs + `[diag:stub]` histogram) + frame/GS observation (new line). Everything flows through the console sink, retrievable via `devicectl --console` |
| Why it sees post-`0x2c5358` execution where the console cannot | The console is event-driven (missing-target/K1/RPC/handshake) — a silently waiting guest emits nothing. P1c fires on WALL CLOCK from the scheduler loop + `dispatchGuestBranch`, independent of guest emission; per-thread pc + waitReason + schedule counts distinguish spin/advance/wait, and the frame line names vsync/GS progress |
| Edit | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` (+14 lines, inside the P1c block after the per-thread loop): one `std::cerr << "[diag:frame] block=… vsync=… kicks=… kicksDrawing=… gif=… copyRegs=… dma=… gifCopy=… gsWrites=… vifWrites=…"` — read-only relaxed-atomic reads (`m_runtime.memory()` + `ps2_park` GS counters, same accessor pattern as `parkSnapshotWriteOnce`), same `PS2X_DIAG_PERIOD_MS` gate, zero guest-state writes, zero behavior change when the env is unset |
| Commit | `git add ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` → `16e1b9a I18 tap: frame/GS line on the P1c periodic console sampler` = `16e1b9a50530d1c230f7aaba3a6502711f7c58d1` (1 file, 14 insertions); worktree `83fb4d6+46d12d3+6a58c9e+7714a85+a3bbabf+6a37c90+b9bcfe6+fe017b2+16e1b9a`, `status` clean, 0 pushes (E-lane mutating); full diff in `logs/tap-commit.diff` |
| Liveness receipt plan | Predictable per-period console lines at 15 s period over 90 s: ~5 `[diag:frame]` (new) + ~5 `[diag:threads]`/`[diag:stubs]`/`[diag:syscalls]` (in-tree gate proof). A tap that emits nothing is tabled as obstacle H-d, not evidence |
| Tap minimality | 14-line single-line emit reusing in-tree counters/gate/sink; no map entries, no recompiler changes, no guest-execution behavior change (when env unset: one `diagPeriodMs()` cached check per loop, as before) |

### Host `ps2_recomp` re-run decision (SKIPPED — 0 runs)

| Item | Receipt |
|---|---|
| Decision | **NO re-run — base move does not require it**: merged CSV byte-identical to I17's (proven above); base-move `diff --name-only 9da21ff 83fb4d6` = CSV + `ps2_e7.h` + `ps2_runtime.cpp` ONLY (tracked toml untouched, recompiler/analyzer byte-identical); ELF identical (`1b49d05c…` re-sha'd); a re-run would emit byte-identical objects |
| Game objects source | C17 reused READ-ONLY as `PS2X_GAME_CODEGEN_DIR` (verified: 9457 files, `0x2c5358` slot present ×1 in `register_functions.cpp`, 0 `._*`); NO `W/codegen-output/` this brief (delta vs I11–I17, tabled) |
| Post-build proof of identity | `libps2_game_objects.a` sha256 `f356aaa7…` — BYTE-IDENTICAL to I17's lib (recompiled from the same sources at a new base + tap; game objects provably unchanged) |

### Link mechanism (every CMake/packaging delta vs I17)

| # | Item | I17 | I18 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9455 sources) | Same wiring, ported content-identical (`6a58c9e` = `258482d`); 9455 sources from C17 | NO (same count; dir reused, not regenerated) |
| 2 | Base | `9da21ff` + 7 ports + local `0x2c5358` fix | `83fb4d6` + 7 ports (E's `0x2c5358` from base) + tap `16e1b9a` | BASE MOVED (card-result leaf: `0x2c5358` row + `cardTarget(source)` + E13 UI fields); map identical; +14-line tap |
| 3 | Toolchain/SDL2/raylib/flags | I17 §toolchain | Byte-identical toolchain (`diff` clean I9=I17=I18); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1 re-verified via `--version`), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 4 WT sidecars purged pre-configure; C17 verified 0 `._*` | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | OUT of tree (C17, read-only reuse), never staged | dir only |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall ~79s (`PS2X: game objects: 9455 sources from …/ps2x-i17/codegen-output`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (invocation line + `Build task concurrency set to 2`), 7m13.7s wall (delta vs I17 14m28s — tabled, not root-caused), 0 `error:` lines (`logs/ios-runtime-build-tail.log` in evidence, full log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121225416 B (**IDENTICAL size to I17**) / `ad9f6b3cb756dcc7dd70ad93a88358dd62be6d4a8662d8659641169e484d9dbf` (sha differs: tap + E-lane runtime delta, tabled as observed) |
| lib | `libps2_game_objects.a`, 155327984 B, sha `f356aaa7…` = I17's lib sha (byte-identical) |
| Slice | Mach-O 64-bit arm64 |
| Table-populated proof | **9454** `T …_0x…` game text syms (same as I17); **`__Z21sub_002C5358_0x2c5358…` defined `T`** (the gap entry is in the slice, now from base); `g_ps2RecompiledFunctionTable` linkage unchanged |
| Tap-linked proof | `"diag:frame"` string present 1× in the binary (the tap compiled into the slice) |
| SDL count | 296 `T _SDL_` — identical to I17 |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `46d12d3` port) |
| Build tree | `W/ios-runtime-device` ~5.5G; `W` total 8.9G after staging (no codegen dir this brief) |
| Build breaks fixed | NONE — clean first try at the new base (wiring class + E9/E11/E12/E-leaf runtime + tap compile clean) |

## Task 2 — Overwrite install + instrumented probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), UDID `P`, connected, developerMode enabled (`logs/ipad-details.json` — captured via DIRECT `--json-output <SSD path>`: WORKED again this brief, 15415 B — same size as I16/I17 — exit 0).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install — no `Locked` failure |
| Running processes | 576-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4316 = the I17 build STILL RUNNING (I17's bundle UUID `4F6584B3-…`; relaunched after I17's cleanup by an unknown launcher — I17 reported 0 `ps2` at its cleanup, same pattern as I16→I17). Untouched before install (overwrite tested against a live occupant, 7th brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4316 reaped BY the install itself; 4348 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I18 build + ISO; MF1/I8–I17 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/lock/processes/details/files/screenshot 60, install 1200, launch 90, terminate 30) |

### Provision + sign + install (I17 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I17 shape | I18 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 1.4s, ISO `cp` 24.1s (delta vs I17 25.7s — ExFAT variance, tabled); sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I17=I18) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (15.2s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (9× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 111.7s, clean replace** — new `installationURL …/33603E5F-…/` (I17's was `4F6584B3-…`), live occupant PID 4316 reaped BY the install (0 `ps2` after). Tenth clean overwrite (delta vs I17 68s — tabled, not root-caused) |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/33603E5F-978B-4D3D-A06B-6270872BC82A/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX modules, PVD bytes `0143443030310100` = `\x01CD001\x01` in the first `[diag:cd]` payload line) |

### Launch (instrumented probe, ISO+env — I10–I17 recipe + `PS2X_DIAG_PERIOD_MS`)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000"}'` + argv ELF path → exit 2 (alive, PID 4348), 23245 lines (5130 DPI-spam, 15471 dormant-spam, 2644 diag-relevant) |
| Tap liveness (RECEIPT — H-d excluded) | **5 `[diag:frame]`** (new tap) + 5 `[diag:threads]` + 30 `[diag:thread]` + 5 `[diag:stubs]` + 82 `[diag:stub]` + 5 `[diag:syscalls]` + 28 `[diag:syscall]` + 130 `[diag:stacks]` + 1102 `[diag:cd]` + 1062 `[cd:callback]` + 15471 `[diag:dormant]` (all P1c-gated) — every predicted line class present at the predicted ~15 s cadence |
| I17 wall | **Still gone — zero refs anywhere**: `guest-branch` 0, `missing-target` 0, `dispatchGuestBranch` 0 (any kind) |
| Boot prefix | K1 `armed` + `install#1–8` + `lookup#1–6` (15 lines, byte-identical shape); TEXTURE 5 lines; 12 IRX modules (same 12); `[sif-handshake] sregs[1]=1`; same 4 unhandled RPC sids (byte-identical); `ee:idle` 0; open-fail 0; `sceCdRead unresolved` 0; no teardown |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11–I15's own spin reports) — **NO new `.ips` for I18 AND no late filing for I17** (three briefs running with no filing; tabled, not root-caused) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i18-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content |
| Evidence-size handling | Full console 23245 lines / 13.9 MB EXCEEDS the 5 MB evidence cap → full log stays complete on SSD (`W/logs/launch-cdimage-console.log`, sha in the extract header); evidence commits the deterministic 2649-line diag extract (`grep -v DPI \| grep -v dormant` + 5-line header with counts + shas) + dormant head/tail samples + the 5 frame lines. Reproducible by the exact command in §Exact commands |

### Named layer I — guest threads: 6/6 Waiting, frozen pcs, all 5 blocks (H-c)

Enum key (`ee_scheduler.h:25–44`): status 2 = Waiting; waitReason 2 = Semaphore, 6 = Mpeg. Block dumps at dedup lines 4569/7355/10106/12857/15608 (~15 s cadence).

| Thread | Entry | pc (all 5 blocks) | waitReason / waitId | scheduled (blk0 → blk1–4) | Reading |
|---|---|---|---|---|---|
| 1 (main) | `0x100008` | `0x3b1028` (resume site after `jal func_402A10` @`0x3b1020`; `lw $v1,0x10($s0)` in `sub_003B0FB8`) | 6 = Mpeg / 0 | 8255 → 0,0,0,0 | **Starved in `sceMpegGetPicture`** (sole Mpeg-wait issuer, `MPEG.cpp:2334`): 0 decoded frames, no EOF, stream not ended, decoder not failed — none of the 7 `completeExternalWait(kMpegPictureWaitType,…)` sites (`MPEG.cpp:1860/1884/1919/2098/2144/2150/2237/2243`) fired for its stream in 90 s |
| 2 | `0x3e3be0` | `0x423de8` | 2 = Semaphore / 26 | 206 → 0,0,0,0 | Parked in `WaitSema` (gateway resume label); entry region = CD-callback region (`cb=0x3e3ad8`, `ret=0x3e3694/0x3e3b8c`) — the CD-feeder thread candidate; never woken after boot |
| 3 | `0x31ac60` | `0x423de8` | 2 = Semaphore / 30 | 260 → 0,0,0,0 | Parked in `WaitSema`; never woken after boot |
| 4 | `0x31ac08` | `0x423de8` | 2 = Semaphore / 31 | 859 → 900,900,900,900 | **The vsync pump**: woken exactly 60×/s (900/15 s), cycles `iSignalSema` + `WaitSema` per vsync, re-parks — the ONLY thread executing in steady state (§stub/§syscall) |
| 5 | `0x382740` | `0x423de8` | 2 = Semaphore / 32 | 411 → 0,0,0,0 | Parked in `WaitSema`; never woken after boot |
| 6 | `0x3c19a8` | `0x423de8` | 2 = Semaphore / 36 | 1 → 0,0,0,0 | Parked in `WaitSema`; never woken after boot |

Sema-wait park site `0x423de8` decoded (C17 emission): `sub_00423DE0` = 3-instruction gateway `addiu $v1,$zero,0x44; syscall; jr $ra` — `0x423de0` = WaitSema call (syscall `0x44` = `WaitSema`, `Dispatcher.cpp:270`), `0x423de8` = the `jr $ra` resume label where suspended waiters park. Likewise `sub_00423DD0` = `addiu $v1,$zero,-0x43; syscall; jr $ra` = iSignalSema gateway (syscall `-0x43` = `iSignalSema`, `Dispatcher.cpp:267`).

### Named layer II — steady state = 13-function vsync pump (NOT spinning, NOT advancing boot)

| Block | `[diag:stubs]` distinct | Content |
|---|---|---|
| 0 (boot) | 1482 | Boot storm (top: `0x41ea18` ×953382, `0x41aa88` ×192589, …) — boot executes ~1M+ dispatches, then ENDS |
| 1–4 (steady, IDENTICAL sets) | 13 | ×1800 (2/vsync): `0x3ffa58` (ra `0x3271e8`), `0x3ffbc0` (ra `0x326f24`), `0x326eb0` (ra `0x326bf8`); ×900 (1/vsync): `0x423de0` (WaitSema gw, ra `0x31ac30`), `0x423dd0` (iSignalSema gw, ra `0x31abf8`), `0x31aac8`, `0x326b88`, `0x227f58`, `0x317348`, `0x317500`, `0x317520`, `0x31abd0`, `0x3825f8` (ra chain rooted in thread 4's entry `0x31ac08`) |

| Block | `[diag:syscalls]` distinct | Content |
|---|---|---|
| 0 (boot) | 30 | Boot syscalls (top: `0x2f` GetThreadId ×18050, `0x30` ReferThreadStatus ×7796, `0x2b` ×7795, `0x44` WaitSema ×6752, `0x42` SignalSema ×4927, `-0x43` iSignalSema ×1820, …) |
| 1–4 (steady, IDENTICAL) | 2 | `0x44` WaitSema ×900 from `0x423de8` + `0xffffffbd` (−0x43) iSignalSema ×900 from `0x423dd8` — exactly one signal+wait pair per vsync (thread 4's loop) |

Spin-vs-wait forcing: NO hot loop (no single target dominates — max steady count is 1800/15 s = 120/s, vs block-0's 953382); NO boot advance after ~15 s (identical 13-target sets ×4 blocks); guest pc = frozen wait pcs + the vsync pump. H-a (spinning) and H-b (advancing) excluded.

### Named layer III — frame/GS: vsync alive, ALL submission counters frozen since boot

`[diag:frame]` blocks 0–4 (`logs/launch-cdimage-frame.log`):

| block | vsync | kicks | kicksDrawing | gif | copyRegs | dma | gifCopy | gsWrites | vifWrites |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 900 | 43708 | 43356 | 2795 | 4655 | 4542 | 210 | 0 | 2 |
| 1 | 1800 | 43708 | 43356 | 2795 | 4655 | 4542 | 210 | 0 | 2 |
| 2 | 2700 | 43708 | 43356 | 2795 | 4655 | 4542 | 210 | 0 | 2 |
| 3 | 3600 | 43708 | 43356 | 2795 | 4655 | 4542 | 210 | 0 | 2 |
| 4 | 4500 | (line interleaved mid-write by a host-thread DPI warning — `kicks=WARNING: GetWindowScaleDPI…`; vsync readable, counters unreadable on this line only; the `grep -v DPI` dedup drops it, hence the 5-vs-4 `[diag:frame]` census) | | | | | | | |

Reading: vsync advances exactly 900/block = 60/s (VBlank alive, scheduler loop alive — the guest is NOT waiting ON vsync). Every GS/DMA counter is BIT-IDENTICAL across blocks 0–3 (all submission happened during boot; ZERO new kicks/GIF/DMA/GS-writes for 75+ s) — the black screen is consequential: nothing is submitted. `gsWrites=0` (no direct GS register writes at all) and `vifWrites=2` (boot-only) bound the GS path further.

### Named layer IV — CD/file-I/O: reads + callbacks ALL in the first ~15 s, then silence

| Item | Receipt |
|---|---|
| Timing | ALL 1102 `[diag:cd]` (dedup lines 71–2640) + ALL 1062 `[cd:callback]` (lines 158–2642) precede the block-0 dump (line 4569, ~15 s) → CD goes TOTALLY quiet (no reads, no callbacks) for 75+ s |
| First read | `sceCdRead lbn=0x10 sectors=1 buf=0x519c80` + payload `bytes=0143443030310100` (`\x01CD001\x01` = ISO PVD — ISO parses) |
| Last read | `sceCdRead lbn=0x13bb13 sectors=16 buf=0xdb8740` (16-sector streaming-style read, then nothing) |
| Callbacks | `queued`/`start func=1 cb=0x3e3ad8` pairs only (same single callback; thread 2's entry region) |
| Reading | The game is NOT waiting ON file I/O (no pending-read park, no open-fail, `unresolved` 0) — but the CD-stream pump STOPPED before delivering EOF/frames to the MPEG layer: `currentCdStreamEofSeen` never set (else GetPicture's wait condition `!sawEof` would break differently — main still waits with `!streamEnded`), and no `notifyMpegCdStreamEof` completion fired |

### The 4 RPC sids (NOT the wait cause)

Same 4 `[IOP/RPC trace:unhandled]` sids as I10–I17 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`), byte-identical lines, boot-phase only; no thread's wait reason is RPC/External-with-RPC-token (waits are Mpeg + Semaphore); guest continues past them since I10. I17 gap 2 stays informational.

### `[diag:dormant]` ×15471 (P1c-gated idle-iteration spam — read, not the layer)

`id=-1 pc=0x0` from the `context.pc == 0u` path (`EeScheduler.cpp:675–692`): the scheduler loop's no-runnable-thread iterations (all 6 threads Waiting) each emit one line + dispatch-history trace (~172/s). Proves the host loop is alive-but-starved; the `trace=` tails corroborate steady traffic in `0x31xxxx/0x3exxxx/0x40xxxx/0x42xxxx` (the pump + gateways). Excluded from the committed extract by the documented filter (counts + head/tail samples committed).

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: H-c — guest WAITING in EE-kernel MPEG/sema starvation (layer NAMED with evidence)

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest pc is frozen in waits, not spinning or advancing boot | 6/6 threads `status=2` (Waiting) with identical pcs all 5 blocks; steady dispatches = the same 13 targets at exact vsync rates (no hot loop, no boot advance); `ee:idle` 0 (scheduler never fully idle — the pump runs) |
| 2 | Main (thread 1) is starved in `sceMpegGetPicture` @`0x3b1028` | `waitReason=6` (Mpeg) `waitId=0` `scheduled=0` after block 0; GetPicture is the SOLE Mpeg-wait issuer (`MPEG.cpp:2334`, `Ssx3Movie.cpp` has no waits); wait condition = 0 decoded frames + no EOF + `!streamEnded` + `!decoderFailed`; none of the 7 `completeExternalWait` sites fired in 90 s |
| 3 | Workers (threads 2,3,5,6) are parked in `WaitSema` on semas never signaled | All at `0x423de8` (WaitSema-gateway resume label, emission-read), `waitReason=2`, waitIds 26/30/32/36, `scheduled=0` blocks 1–4; thread 2's entry region = the CD-callback region (feeder-thread candidate) |
| 4 | The only execution is thread 4's vsync pump (sema 31 ping-pong) | `scheduled=900`/block every block; steady syscalls = exactly iSignalSema + WaitSema 900 each; stub ra chain rooted at entry `0x31ac08` |
| 5 | Frame/GS layer: vsync alive, submission dead | `[diag:frame]`: vsync +900/block; kicks/gif/copyRegs/dma/gifCopy/gsWrites/vifWrites bit-identical blocks 0–3 → black screen is consequential, not a GS fault |
| 6 | NOT waiting on the 4 RPC sids / vsync / file I/O | RPC sids byte-identical boot-only + no RPC-token waits; vsync advances 60/s and is consumed by the pump; CD reads end cleanly (no error park) — the failure is the MPEG/sema completion that never arrives, one layer above |
| 7 | Class | EE-kernel/HLE subsystem starvation (MPEG stub + semaphore completion) — NOT map layer (no address named, `missing-target` 0), NOT config (no flag/plist/path change completes a decode or signals a sema), NOT recompiler (every dispatched target resolves) |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Signal the semas / complete the MPEG wait from outside | Kernel-HLE behavior change (fork code) | NOT config — belongs to the next brief |
| `PS2X_DIAG_SEMA=1` re-probe to census sema ownership | Config (env-only relaunch, no rebuild) | NOT a fix — sharper diagnosis, and the I-series precedent is a single probe per brief; named as the next brief's FIRST action instead |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: there is no failing surface to tweak — the guest waits correctly on objects that are never completed |
| Unhandled RPC sids | `ps2xIOP` subsystem | NOT attempted — proven NOT the wait cause this brief (see §RPC) |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every dispatched target (9454 syms, `missing-target` 0) |

Fixes attempted: ZERO in Task 3 (the brief's one gap — observability — was closed in Tasks 1–2; the named layer's fix belongs to the next brief).

Contract outcome: **H-c** (guest waiting — main in MPEG GetPicture starvation, workers in never-signaled Sema waits, vsync pump the only execution, GS/DMA frozen, CD quiet after boot). H-a/H-b excluded by the frozen pcs + identical steady sets; H-d excluded by the tap liveness receipt. The ONE next action: **`ps2xKernel` MPEG/sema-completion brief — FIRST relaunch the installed I18 app (or its rebuild) with `PS2X_DIAG_SEMA=1` added to the env (config-only, no rebuild) to census sema 26/30/31/32/36 ownership (creator thread, signalers, counts), THEN audit the MPEG feeder path (who calls `sceMpegAddBs`/flush, why the CD-stream pump stops before EOF, why 0 frames decode) and implement the completion** — kernel-HLE class, NOT a map-entry brief, NOT an observability brief.

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i18"
git -C "$FORK" ls-remote fork ssx3          # 83fb4d6 (E-lane advanced exactly once past I17's base)
git -C "$FORK" log --oneline -5             # 83fb4d6 at top (non-monotonic noise filtered)
git -C "$FORK" status --short               # M register_functions.cpp + ?? ps2_log.txt at recon AND end
git -C "$FORK" log --oneline 9da21ff..83fb4d6          # exactly 1 commit (83fb4d6)
git -C "$FORK" show 83fb4d6 --stat           # CSV +1, ps2_e7.h, ps2_runtime.cpp
git -C "$FORK" diff --name-only 9da21ff 83fb4d6  # same 3 files (recompiler/analyzer/toml identical)
git -C "$FORK" diff 9da21ff 83fb4d6 -- games/ssx3/ssx3-functions.sweep.csv  # byte-identical 0x2c5358 row
for a in 002C5358 0014F2A8 00156750 00243A80 00395730 003A0158 002C5300; do
  git -C "$FORK" show 83fb4d6:games/ssx3/ssx3-functions.sweep.csv | grep -c "$a"; done  # 1,0,0,0,0,0,1
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks (dedupe: port I17's 7, SKIP 32d37e7) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I18/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 83fb4d6
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" cherry-pick 71c2690ccc6505825c029f589064b616489e2479 258482d035bc8ffa2141b86f5fe1cb0be90ab102 1b8022631e43375b969fbecfef11f22ace3ae447 5ff15c43d1f3defdb3e66e0d431ca1b0476d61b0 028cf6371e80d3b6bf866dc24e93ac9a8ce41580 83126a6304fd04e963bd7654833555214d9fd7b3 7a8007a4aef7c80e783e2d3e224499999884a34c  # full SHAs; 3/7, transient abort on 4th
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" cherry-pick 5ff15c43d1f3defdb3e66e0d431ca1b0476d61b0  # -> a3bbabf
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" cherry-pick 028cf6371e80d3b6bf866dc24e93ac9a8ce41580  # -> 6a37c90
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" cherry-pick 83126a6304fd04e963bd7654833555214d9fd7b3  # -> b9bcfe6
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" cherry-pick 7a8007a4aef7c80e783e2d3e224499999884a34c  # -> fe017b2
# 46d12d3, 6a58c9e, 7714a85, a3bbabf, 6a37c90, b9bcfe6, fe017b2 (content-identical to I17's)
# --- Task 1b: tap-surface reads + tap commit (named add, local commit, NO push) ---
grep -n "dispatchGuestBranch\|diagCallsPeriodicFlush\|tallyDispatch" "$WT/ps2xRuntime/src/lib/ps2_runtime.cpp
grep -n "parkSnapshotDue\|installParkTermHandler" "$WT/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
grep -n "AGRESSIVE_LOGS" "$WT/ps2xRuntime/include/ps2_log.h"  # 0 -> [run:tick] compiled out
grep -n "memory()" "$WT/ps2xRuntime/include/ps2_runtime.h"    # accessor path for the frame line
# (insert the 14-line [diag:frame] emit after the per-thread loop in EeScheduler::run's P1c block)
git -C "$WT" add ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
git -C "$WT" -c user.name="muse-i18" -c user.email="i18@local" commit -m "I18 tap: frame/GS line on the P1c periodic console sampler"  # 16e1b9a
# --- Task 1c: codegen SKIPPED (0 runs) - C17 reused read-only ---
ls /Volumes/Extreme\ SSD/ps2x-i17/codegen-output | wc -l   # 9457 (verified intact)
grep -c "0x2c5358" /Volumes/Extreme\ SSD/ps2x-i17/codegen-output/register_functions.cpp  # 1 slot
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
# --- Task 1d: device configure + build (I17 shape, new base + tap, C17 sources) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I17=I18
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="/Volumes/Extreme SSD/ps2x-i17/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall ~79s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 7m13.7s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # ad9f6b3c...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9454 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*2C5358_0x2c5358"             # T (from base now)
shasum -a 256 "$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/libps2_game_objects.a"  # f356aaa7 = I17's
grep -c "diag:frame" "$APP/ps2EntryRunner"                           # 1 (tap linked)
# --- Task 2: recon + stage/sign/install + instrumented probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details-direct.json"  # WORKED again (15415 B)
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 576 lines, PID 4316 = I17 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (15.2s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 111.7s
B="/private/var/containers/Bundle/Application/33603E5F-978B-4D3D-A06B-6270872BC82A/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive, PID 4348), 23245 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i18 -s ps2EntryRunner --no-recurse  # 5 files, all priors
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i18-shot1.png
mv /tmp/i18-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4348  # cleanup only
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i18 -s ps2EntryRunner --no-recurse  # still 5 (no new .ips)
# --- Task 3: diagnosis reads ---
grep -v "GetWindowScaleDPI" "$W/logs/launch-cdimage-console.log" > "$W/logs/launch-cdimage-dedup.log"  # 18115 lines
grep -v "GetWindowScaleDPI" "$W/logs/launch-cdimage-console.log" | grep -v "diag:dormant" > extract  # 2644 + header
grep -c "\[diag:frame\]" "$W/logs/launch-cdimage-console.log"  # 5 (tap liveness)
grep -c "guest-branch\|missing-target" "$W/logs/launch-cdimage-console.log"  # 0 (no wall)
grep -o "lbn=0x[0-9a-f]*" dedup | sort | uniq -c | sort -rn  # CD lbn census (all pre-block-0)
grep -n "0x423de0:\|0x423dd0:" C17/sub_00423D*.cpp  # gateway emission reads (WaitSema / iSignalSema)
grep -rn "waitExternal" WT/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp  # :2334 = sole Mpeg-wait issuer
grep -n "completeExternalWait" WT/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp  # 7 wake sites, none fired
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | EE-kernel MPEG/sema starvation: main starved in `sceMpegGetPicture` (0 frames, no EOF/end/fail); threads 2,3,5,6 parked in `WaitSema` on semas 26/30/32/36 never signaled; only thread 4's vsync pump executes; GS/DMA frozen; CD quiet after boot | 6/6 `status=Waiting` frozen pcs ×5 blocks + steady 13-target/2-syscall sets + `[diag:frame]` vsync-advancing/counters-frozen + CD lines 71–2642 pre-block-0 + sole-issuer `MPEG.cpp:2334` + 7 unfired wake sites | `ps2xKernel` MPEG/sema-completion brief: FIRST `PS2X_DIAG_SEMA=1` config-only relaunch to census sema ownership, THEN audit the MPEG feeder (AddBs callers, CD-stream EOF path, decoder) and implement the completion (THE one next action; kernel-HLE class) |
| 2 | Sema 26/30/31/32/36 ownership unknown (creator, signalers, counts) | P1c prints `waitId` only; `PS2X_DIAG_SEMA` exists but was not enabled this probe (single-probe precedent) | Folded into gap 1's first action (config-only relaunch — no separate brief) |
| 3 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10–I17) | 4 `[IOP/RPC trace:unhandled]` lines, boot-only; proven NOT the wait cause this brief | Informational — no brief (guest continues past them; no RPC-token waits) |
| 4 | `46d12d3` + `6a58c9e` + `7714a85` + `a3bbabf` + `6a37c90` + `b9bcfe6` + `fe017b2` + `16e1b9a` unpushed (E-lane mutating; shared clone `M register_functions.cpp` + `?? ps2_log.txt`) | Worktree log `16e1b9a^… = 83fb4d6`, 0 pushes; remote `ssx3` at `83fb4d6` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows (note: the tap commit is local-observability class — confirm with the E-lane owner whether it merges or stays worktree-local) |
| 5 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest never reached MC I/O (still in movie/sema wait) | Data-container brief (only if a later probe fails on file I/O) |
| 6 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I17 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 7 | NO new `.ips` three briefs running (5 files, all priors' — I11–I15 each filed one spin report; I16/I17/I18 file none) | `logs/crashlog-check.log` (post sleep + re-`ls` AND post-terminate re-`ls`: still 5) | Informational — consistent with a non-spinning waiter (no spin-hot faulting thread); next brief's first `ls` confirms I18; no brief unless a later probe shows action-taken |

## Receipt paths

- `local/research/I18/REPORT.md` (this file)
- `local/research/I18/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I17's)
- `local/research/I18/logs/cherry-pick.log`, `logs/tap-commit.diff` (the 14-line tap), `logs/ios-runtime-configure.log` (full), `logs/ios-runtime-build-tail.log`
- `local/research/I18/logs/ipad-details.json` (via DIRECT `--json-output <path>` — worked again, 15415 B), `processes-pre.log`, `entitlements.plist`
- `local/research/I18/logs/install.log` (overwrite, exit 0, 111.7 s)
- `local/research/I18/logs/elf-device-path.txt`
- `local/research/I18/logs/launch-cdimage-console.diag-extract.log` (2649-line deterministic extract + header with full-log shas), `launch-cdimage-dormant-samples.log`, `launch-cdimage-frame.log` (5 frame lines)
- `local/research/I18/logs/crashlog-check.log` (check1 + check2 concatenated, labeled; 5 files at both: all priors', no new `.ips`, no late I17 filing), `screenshot.log`
- `local/research/I18/logs/i18-shot1.png` (iPad window, black content)
- `W/logs/` (same + full 23245-line console + full dedup + full build log + details stdout copy); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `16e1b9a`, clean, 8 local commits, 0 pushes); NO `W/codegen-output/` (C17 reused read-only)
- No fork push this brief (E-lane mutating — all 8 commits stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black past the I17 wall with the guest in MPEG/sema waits and GS submission frozen since boot; first presented content awaits gap 1's completion brief.
- Name the sema signalers — P1c prints `waitId` only; `PS2X_DIAG_SEMA` was deliberately not enabled (single-probe precedent) — gap 1's first action is the config-only DIAG_SEMA relaunch.
- Read block-4's GS counters — the 5th `[diag:frame]` line was interleaved mid-write by a host-thread DPI warning; vsync=4500 readable, counters lost on that line only (blocks 0–3 carry the frozen-counter proof).
- Prove which thread feeds MPEG bitstream — no `sceMpegAddBs`/flush call was observed completing a frame; thread 2 is the feeder candidate by entry-region proximity only (tabled, not over-claimed).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I18); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (PVD bytes + IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never observably reached file I/O past the boot CD reads (gap 5).
- Push the 8 local commits — the E-line is live (gap 4; local commits only; tap-merge intent needs the owner's call).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Root-cause the build-time/install-time deltas (7m14s vs I17's 14m28s; install 111.7s vs 68s, same `-jobs 2`/plain-install) — tabled, not root-caused.
- Re-run a second probe for determinism (e.g. with `PS2X_DIAG_SEMA=1`) — single 90 s probe per the brief's recipe and I-series precedent; period-2–4 identical steady sets are the in-probe determinism receipt.
- Name the launcher of pre-install PID 4316 — the I17 bundle was running though I17 reported 0 `ps2` at its cleanup (third brief running with a relaunched occupant); it was reaped by the install without investigation.
- Explain why no `.ips` filed three briefs running — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); the non-spinning waiter profile is consistent but not proven causal (gap 7).
- Observe E11/E12/E-leaf card-tap output — 0 console lines from the taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar.

## TAIL RECEIPT

Report written in 5 chunks (header + contract + caps; Task 1 dedupe + tap surfaces + tap; codegen + link + Task 2 install/probe; named layers I–IV + Task 3; commands + gaps + receipts + could-not-do). Pre-receipt measure: 393 lines, sha256 `b1ed575b31ab1aac89ff25b4fcea7859a7415591e02f4d6cefb85f4452523492`.
Tail content line: "Observe E11/E12/E-leaf card-tap output — 0 console lines from the taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar." This receipt line ends the report. END-I18-REPORT.
