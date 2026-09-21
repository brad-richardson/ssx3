# I21 — S9 device re-probe on the E18 fork: rebuild + reinstall + 90 s diagnostic probe, delivery/progress vs host (NO implementation)

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/E18/REPORT.md` + `local/research/E18/NEXT-BRIEF.md` read first (all of both: E18 delivered 5,040 bytes on the host caller path — fixtures flipped, 458/458 — but parser output zero packets/frames and main still waits at `0x3b1028`; the device FFmpeg-OFF stub residual is a SEPARATELY observed dependency).
- `local/research/I20/REPORT.md` read (all of it: agreement A1–A13 + creator census 39/39 + spec S1–S10 — the comparison baseline).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I18/I19/I20; the I18 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4516, I18's bundle UUID — relaunched after I20's cleanup by an unknown launcher, same pattern as I16→I17→I18→I19→I20; state tabled in Task 1).
- BASE: `3adc0478` (E18 BEHAVIOR, PUSHED — verified by `ls-remote` at recon AND end; E-lane advanced 4 commits past I20's base: E15-obs → E16 → E17 → E18). Worktree pins `3adc0478` + 3 content-identical ports (plist + CMake wiring + tap) + ONE local wiring extension (drop E17's 5 in-tree `sub_*.cpp` when `PS2X_GAME_CODEGEN_DIR` is set — forced by unity-jumbo duplicate symbols, tabled); the 5 absorbed CSV rows DEDUPED (all byte-identical to fork lines 873/1022/2943/7012/7176 — skipped, so the probe tests the fork rows). Merged CSV sha `7c827add…` = I17 = I18 = E17's pin. 4 local worktree commits, ZERO fork commits (0 pushes, remote unmoved).
- Product: device Release REBUILD (C17 game objects reused read-only, lib byte-identical to I17/I18) + OVERWRITE reinstall + ONE 90 s probe (`PS2X_DIAG_PERIOD_MS=15000` + `PS2X_DIAG_SEMA=1` + `PS2X_DIAG_SEMA_CREATE=1`).
- Rules honored: no behavior implementation anywhere (E-lane owns the fork; no stacking); all trees under `/Volumes/Extreme SSD/ps2x-i21/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; shared clone touched once (`worktree add`) + read-only inspection (recon AND end: `?? ps2_log.txt` only, remote `3adc0478` both times — E-lane pane never prompted/steered); app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging + evidence; evidence `local/research/I21/` standalone, `[I21]` commit, no push.
- Outcome shape: DELIVERY LANDS ON DEVICE — callback `0x3b0b10` + producer `0x3b0b40`/`0x3b06b0` + release `0x3b06f8` + AddBs `0x4029d0` all dispatched (dispatch-history tails, boot phase, same routine order as the host chain); the stub-decoder warning FIRED ×1 (Cause B now the wall — I20 S7 predicted exactly this); main STILL at `0x3b1028` all 5 blocks (0 frames served — the stub enqueues nothing); creators 39/39 byte-identical to I20; steady state re-confirmed with tabled drift (id-31 pump wall variance, boot-phase ±1s, id-39 +6, stub-distinct +9, syscall boot deltas — each receipted as legitimate fork-change movement or wall variance, never smoothed).

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i21/`, `WT` = `W/fork-wt` (fork worktree @`3adc0478` + 4 local commits), `C17` = `/Volumes/Extreme SSD/ps2x-i17/codegen-output/` (reused read-only; NO `W/codegen-output/`), `W18` = `/Volumes/Extreme SSD/ps2x-i18/fork-wt` (port source), `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | E18's caller-owned delivery fires on device (`0x3b0b10`/`0x4029d0` dispatch observed), fed bytes reach the FFmpeg-OFF stub (ungated warning fires), but main stays parked at `0x3b1028` with 0 frames (the stub enqueues nothing) — i.e. device shows delivery-then-no-decode, naming "no on-device MPEG decode" as the first post-delivery wall |
| Observable | Dedupe table (5 rows, bytes both sides); rebuild identity (recipe + pins + binary identity); reinstall receipt; 90 s probe (exit/fate + console extracts + screenshot); host-vs-device comparison (dispatches/bytes/progress/sema/decode); first post-delivery device wall (or delivery-absent with the exact missing edge) |
| Alternatives | H-a delivery + stub warning + still-parked (observed). H-b delivery absent on device (dispatches ×0 — the exact missing edge named, no host inference). H-c main advances past `0x3b1028` (named successor state). H-d probe blind (no tap lines — obstacle receipted, not the wall) |
| Stop | All bars tabled or any cap (partial tabled as gap). Contract outcome: H-a on every row — delivery observed, warning observed, main still parked, wall named |
| Time box | 4 h (used ~3 h wall: recon → worktree+ports → configure 84s → build 18m08s → stage/sign → install 77s → probe 90s → census → extracts → report) |
| One gap | NO implementation in this brief (re-probe only); the named wall gets its own follow-up brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 8.9 GB (11%) — WT 382M + device tree 5.5G + signed app 2.9G + logs 37M (NO codegen dir — C17 reused) | `du -sh W` after evidence step |
| Evidence `local/research/I21/` | ≤ 5 MB | 3.9 MB + REPORT, 19 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i21-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`) | exact commands + build log line |
| Fork writes | worktree only, named `git add`, fork remote only, zero fork commits | 4 local commits (3 ports + 1 wiring), 0 pushes, remote `3adc0478` at recon AND end | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 0 runs (skipped: merged CSV byte-identical — tabled decision) | §codegen decision |
| Probe console committed | complete-or-extract | deterministic 2615-line non-sema extract + COMPLETE 39-line create extract + 11858-line sema extract + 7-line delivery extract + frame lines + sizes (full 45697-line/17.1 MB console on SSD — over cap, tabled) | `logs/*.log` headers |
| Device ops | ONE rebuild + ONE reinstall + ONE 90 s probe | 1 build (exit 0) + 1 install (exit 0, overwrite) + 1 probe (exit 2 = alive, PID 4669) | §Task 1/2 |

## Task 1 — Dedupe + rebuild + reinstall (no probe until §2)

### Dedupe table (5 rows vs E17 NEXT-BRIEF lines; keep-on-difference — all identical, all skipped)

| Origin | Local port (W18) | Local row bytes | Fork line @`3adc0478` | Fork row bytes | Standing |
|---|---|---|---|---|---|
| I12 | `a3bbabf` | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` | 873 | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` | SKIP — byte-identical |
| I13 | `6a37c90` | `sub_00156750,0x156750,0x1567b8,0x68` | 1022 | `sub_00156750,0x156750,0x1567b8,0x68` | SKIP — byte-identical |
| I14 | `b9bcfe6` | `sub_00243A80,0x243a80,0x243ab0,0x30` | 2943 | `sub_00243A80,0x243a80,0x243ab0,0x30` | SKIP — byte-identical |
| I11 | `7714a85` | `sub_00395730,0x395730,0x395750,0x20` | 7012 | `sub_00395730,0x395730,0x395750,0x20` | SKIP — byte-identical |
| I15 | `fe017b2` | `sub_003A0158,0x3a0158,0x3a0290,0x138` | 7176 | `sub_003A0158,0x3a0158,0x3a0290,0x138` | SKIP — byte-identical |

Dedupe proof beyond the 5 rows: fork CSV `diff 83fb4d6 3adc0478` = exactly the 5 added lines, zero removals; merged-CSV sha `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba` identical across I17's / I18's / I21's worktrees AND equal to E17 NEXT-BRIEF's pinned CSV hash. Keep-on-difference triggered zero times — no local row kept, no force-dedupe. The probe tests the fork rows.

### Worktree recon + iPad pre-state (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Pin (VERIFIED, not moved) | `3adc0478` = `3adc0478b6d2260acdd28a249466f2eef9a20176` (`[E18] Deliver non-stream MPEG input callbacks on the caller`) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `3adc0478` at recon AND at end (no E19 on the remote; E-lane advanced zero commits during I21) |
| Range `83fb4d6..3adc0478` | Exactly 4 commits: `67c0a63` (E15 obs) + `784f2b3` (E16) + `e63f161` (E17 absorb) + `3adc047` (E18 behavior); files: CSV (+5) + `ps2_e15.h` + `ps2_e4.h` + `ps2_e7.h` + `EeScheduler.cpp` + `MPEG.cpp` + `ps2_runtime.cpp` + runner generated (header + register + 5 `sub_*.cpp`) + expansion tests |
| E-lane owner | Shared `ssx3` @`3adc047` with `?? ps2_log.txt` ONLY at recon AND end (no mid-brief edits visible); pane never prompted/steered |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 3adc0478` → `HEAD is now at 3adc047` (exit 0; `non-monotonic index ._pack-…idx` stderr noise, cosmetic, outputs unaffected) |
| Sidecars | 337 `._*` in fresh worktree → purged → 0; 3 reappeared pre-configure → purged → 0; `status` clean after |
| iPad reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| iPad lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install — no `Locked` failure |
| iPad running processes | 582-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4516 = the I18 build STILL RUNNING (I18's bundle UUID `33603E5F-…`; relaunched after I20's cleanup by an unknown launcher — I20 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 8th brief running) |
| iPad installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| iPad details JSON | DIRECT `--json-output <path>`: WORKED again, 15382 B (I16/I17/I18: 15415 B — 33 B delta, tabled not root-caused), exit 0 |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, lock 30, apps/processes/details/files/screenshot 60, install 1200, launch 90, terminate 30) |

### Ports carried (3 cherry-picks, content-identical to I18's) + wiring extension (1 local commit)

| New commit | = I18 commit | Content | Identity |
|---|---|---|---|
| `3ae0570` (`3ae05709fa…`) | `46d12d3` (I8 plist) | CFBundleName `""` → `ps2EntryRunner` (base plist still empty — port REQUIRED) | `diff` of `^[+-][^+-]` lines clean |
| `842340c` (`842340c37a…`) | `6a58c9e` (I10 CMake) | `PS2X_GAME_CODEGEN_DIR` → `ps2_game_objects` static lib (absent at base — port REQUIRED) | clean |
| `3564273` (`35642733ce…`) | `16e1b9a` (I18 tap) | 14-line `[diag:frame]` emit (absent at base — port REQUIRED for frame counters) | clean; auto-merged into the P1c block (now :474), context re-verified inside the same gate |
| Pick mechanics | — | 3 individual picks, clean first try each | NO transient dirty-tree abort this brief (delta vs I16/I17/I18, tabled) |

Base-side gate receipts (why the probe env works unmodified): P1c sampler present (`diag:threads` in `EeScheduler.cpp` @base); `PS2X_DIAG_SEMA_CREATE` gate commit `de7ff17` IS an ancestor of `3adc0478` (2 `Sync.cpp` hits @base); `PS2X_ENABLE_FFMPEG=OFF` in the new `CMakeCache.txt:429` (same line as I18).

### Wiring extension (local commit `751a50f`, unpushed — the build does not link without it)

| # | Forcing receipt | Finding |
|---|---|---|
| 1 | E17 landed 5 generated `sub_*.cpp` + register changes in-tree (`ps2xRuntime/src/runner/`, 7 files); `RUNNER_SRC_FILES` = GLOB `src/runner/*.cpp` | All 5 compile into `ps2EntryRunner` directly |
| 2 | I10 wiring removes ONLY `register_functions.cpp` when `PS2X_GAME_CODEGEN_DIR` is set | The 5 in-tree `sub_*.cpp` stay in the executable's sources |
| 3 | In-tree `sub_0014F2A8` sha = C17's copy sha (`740bac80…`, byte-identical); same emitted symbol names | Same symbols defined in direct objects AND in `ps2_game_objects` |
| 4 | `PS2X_ENABLE_RUNNER_UNITY_BUILD` defaults ON (wiring line 8) | Unity-jumbo archive members drag the duplicate symbols in at link → duplicate-symbol failure |
| 5 | Decision | Extend the wiring's `if(PS2X_GAME_CODEGEN_DIR)` block: glob-remove `src/runner/sub_*.cpp` + count message. Build config only (same class as the I10 port itself); zero behavior change; full diff in `logs/wiring-extension.diff` |

Worktree stack: `3adc0478+3ae0570+842340c+3564273+751a50f`, `status` clean, 0 pushes. Shared-clone contact: one `worktree add` + read-only `ls-remote / log / status / diff / show / grep / merge-base`; no checkout/pull/stash/build; owner's `.git` sidecars left alone.

### Host `ps2_recomp` re-run decision (SKIPPED — 0 runs)

| Item | Receipt |
|---|---|
| Decision | **NO re-run**: merged CSV byte-identical to I17's/I18's (sha `7c827add…` ×3, above); base-move touches no recompiler/analyzer/toml (only generated-runner-output match); ELF identical (`1b49d05c…` re-sha'd); a re-run would emit byte-identical objects |
| Game objects source | C17 reused READ-ONLY as `PS2X_GAME_CODEGEN_DIR` (verified: 9457 files, `0x2c5358` slot present ×1, 0 `._*`); NO `W/codegen-output/` (I18 rule) |
| Post-build proof of identity | `libps2_game_objects.a` sha `f356aaa7ddfd9643…` — BYTE-IDENTICAL to I17's and I18's libs (all three shas re-read this brief). The probe tests the E18 RUNTIME, not new game code |

### Link mechanism (every CMake/packaging delta vs I18)

| # | Item | I18 | I21 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9455 sources) | Same wiring + extension; 9455 sources from C17; configure prints `dropped 5 in-tree game sources` | Wiring extension only (forced, §above) |
| 2 | Base | `83fb4d6` + 7 ports + tap | `3adc0478` + 3ae0570 + 842340c + 3564273 + 751a50f (E15-obs/E16/E17/E18 runtime; map identical; 5 CSV rows now from base) | BASE MOVED (+4 E-commits); −5 CSV ports (deduped) |
| 3 | Toolchain/SDL2/raylib/flags | I18 §toolchain | Byte-identical toolchain (`diff` clean I9=I18=I21); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1 re-verified via `--version`), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure | none |
| 5 | Generated-source placement | OUT of tree (C17, read-only reuse), never staged | Same (C17, read-only reuse), never staged | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m24s (`PS2X: game objects: 9455 sources from …/ps2x-i17/codegen-output` + `PS2X: dropped 5 in-tree game sources`; `logs/ios-runtime-configure.log`, full; 4 `non-monotonic index` lines, cosmetic) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (invocation line + `Build task concurrency set to 2`), 18m08s wall (delta vs I18 7m14s / I17 14m28s — tabled, not root-caused), 0 `error:` lines (`logs/ios-runtime-build-tail.log` in evidence, full log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121249160 B / `989b2c2ad40a3a963385a85594c532455092f307e091160a4acabe1bd7482226` (I17/I18: 121225416 B — delta +23744 B = E15/E16/E18 runtime delta, tabled as observed) |
| lib | `libps2_game_objects.a`, 155327984 B, sha `f356aaa7…` = I17's = I18's (byte-identical, §above) |
| Slice | Mach-O 64-bit arm64 |
| Table-populated proof | **9454** `T …_0x…` game text syms (same as I17/I18); all 6 key entries `T` ×1 each: `0x2c5358` + all 5 deduped rows (`0x14f2a8`/`0x156750`/`0x243a80`/`0x395730`/`0x3a0158` — the fork rows ARE in the slice) |
| Tap-linked proof | `"diag:frame"` string present 1× in the binary |
| Stub-compiled proof | `"without FFmpeg"` string present 1× in the binary (decode-boundary preset — the warning CAN fire) |
| SDL count | 296 `T _SDL_` — identical to I17/I18 |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `3ae0570` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 8.9G after staging (same shape as I18) |
| Build breaks fixed | NONE — clean first try at the new base (wiring extension compiled the intent on the first attempt) |

### Provision + sign + install (I18 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename). Install policy: force-install ONLY the previous shape (plain overwrite) — report, don't ask.

| Step | I18 shape | I21 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 1.3s, ISO `cp` 19.9s (ExFAT variance, tabled); sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I18=I21) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (5.1s; delta vs I18 15.2s, tabled), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (10× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 76.7s, clean replace** — new `installationURL …/AAA5E829-…/` (I18's was `33603E5F-…`), live occupant PID 4516 reaped BY the install (0 `ps2` after). Eleventh clean overwrite |
| Device paths | ELF+`SSX3.iso` under the new-UUID app dir (`logs/elf-device-path.txt`) | new UUID only |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt) | no `Failed to open ELF file`; ISO by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX modules, PVD bytes in first `[diag:cd]` payload) |
| Post-Task-1 state | Only OUR PIDs ever signaled | 4516 reaped BY the install itself; nothing else touched |

## Task 2 — ONE 90 s probe + host comparison

### Launch (I20 env + E18 runtime; new bundle UUID)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1"}'` + argv ELF path → exit 2 (alive, PID 4669), 45697 lines / 17.1 MB (sha `d92f8712…`; delta vs I20's 44620 = +1077 = +374 `[diag:sema]` + 521 `[diag:dormant]` + 1 stub warning + 1 `[diag:cd]`-in-extract (full-log 1103=1103; one I20 line was splice-filtered) − 94 splice fragments + 274 DPI-spam (residual — derived, not directly counted: the SSD detached before the full-log DPI census; all other components are direct counts)) |
| Liveness (RECEIPT — H-d excluded) | **39 `[diag:sema-create]`** + 5 `[diag:frame]` + 5 `[diag:threads]` + 30 `[diag:thread]` + 5 `[diag:stubs]` + 82 `[diag:stub]` + 5 `[diag:syscalls]` + 28 `[diag:syscall]` + 1103 `[diag:cd]` + 1062 `[cd:callback]` + 15604 `[diag:dormant]` + 22375 `[diag:sema]` + 130 `[diag:stacks]` — every predicted line class present |
| No wall | `guest-branch` 0, `missing-target` 0 |
| Boot prefix | K1 `armed` + `install#1–8` + `lookup#1–6`; 12 IRX modules (same 12); `[sif-handshake] sregs[1]=1`; same 4 unhandled RPC sids (byte-identical lines modulo the `\r` comparison artifact); `ee:idle` 0; open-fail 0; `sceCdRead unresolved` 0; no teardown; block-0 dump @line 18955 |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11–I15's own spin reports, 01:54–05:00 AM) — **NO new `.ips` for I21 AND no late filing for I20** (six briefs running with no filing; tabled, not root-caused) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i21-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content (viewed from the landed copy) |
| Evidence-size handling | Full console 45697 lines / 17.1 MB EXCEEDS the 5 MB evidence cap → full log + 24988-line dedup stay complete on SSD (`W/logs/`, shas in the extract headers + `logs/launch-e18-console.sizes`); evidence commits the deterministic 2615-line non-sema extract + COMPLETE 39-line create extract + 11858-line sema extract + 7-line delivery extract + the 5 frame lines. Reproducible by the exact commands in §Exact commands |
| Cleanup | Only OUR PID signaled (4669 via `process terminate` at cleanup); post-cleanup grep = 0; app left installed (I21 build + ISO; MF1/I8–I20 precedent) |

### Delivery on device (dispatches fire; stub warning fires; tails are samples, not a census)

| Line | Class | Content (dispatch order) |
|---|---|---|
| 15163 | `[MPEG]` ungated stderr | `runtime built without FFmpeg; MPEG video decode is disabled.` — ×1, the FIRST fed header reaching the stub (I19/I20: ×0) |
| 15164/15166 | `[diag:dormant]` tails (scheduled 398/399) | `… → 0x402c08 → 0x3b1050 → 0x402b38 → 0x3b10d0 → 0x402a10 → 0x3b0b10 → 0x3b0b40 → 0x3b06b0 → 0x3e6574 → 0x3b06f8 → … → 0x4029d0 → …` — registration → GetPicture → CALLBACK → producer → release → AddBs, same routine order as the host E18 chain |
| 15169/15171/15173/15175 | `[diag:dormant]` tails (scheduled 400–403) | Sliding window carries `0x4029d0` (AddBs dispatch) through 6 overlapping windows total |
| Full-line counts | `grep -c` over 45697 lines | `0x4029d0`: 6 lines; `0x402a10`/`0x402c08`/`0x3b0b10`/`0x3b0b40`/`0x3b06b0`: 2 lines each; `0x3b1028`: 10; `sceCdSt`: 0 (St path still never entered) |
| Caveat (I19 rule) | Tails are ~60-deep sliding-window samples | "6 lines" ≠ 6 AddBs calls — ONE actual call site appears in 6 overlapping windows; the dispatch ORDER (callback→producer→release→AddBs) is the receipt, not a call count |
| Timing | All delivery lines pre-block-0 | 15163–15175 < 18955 (boot phase, same window as the host's tick-249 request) |

### Thread rows (main still parked; pump unchanged)

| Thread | Entry | pc (all 5 blocks) | waitReason / waitId | scheduled (blk0 → blk1–4) | vs I20 |
|---|---|---|---|---|---|
| 1 (main) | `0x100008` | `0x3b1028` | 6 = Mpeg / 0 | 8255 → 0,0,0,0 | IDENTICAL — NOT past the park; no named successor |
| 2 | `0x3e3be0` | `0x423de8` | 2 / 26 | 206 → 0,0,0,0 | IDENTICAL |
| 3 | `0x31ac60` | `0x423de8` | 2 / 30 | 260 → 0,0,0,0 | IDENTICAL |
| 4 (pump) | `0x31ac08` | `0x423de8` | 2 / 31 | 859 → 900,900,900,900 | DRIFT: block-0 859 vs I20 861 (I18 859 / I19 860 / I20 861 / I21 859 — 1-count boot variance, tabled) |
| 5 | `0x382740` | `0x423de8` | 2 / 32 | 411 → 0,0,0,0 | IDENTICAL |
| 6 | `0x3c19a8` | `0x423de8` | 2 / 36 | 1 → 0,0,0,0 | IDENTICAL |

### Sema Census II — wait-set traffic vs I20 (FULL-log counts; spans tabled)

| Sema | I21 waits / signals (× waker) | vs I20 | Span (block-0 @18955) |
|---|---|---|---|
| 26 | 737 / 736 splice-inclusive (531 waker=2 + 182 waker=3 + 22 waker=1 + 1 spliced line 13677 `id=26WARNING…`) | IDENTICAL (I20: 737/736, 531+183+22 with the splice on a wait line; the splice moved wait→signal, counts equal) | BOOT ONLY (ends 15116) |
| 30 | 5 / 4 (4 waker=1) | IDENTICAL | BOOT ONLY (ends 14228) |
| 31 | 5292 / 5292 (5261 waker=`-1` + 29 waker=3 + 1 waker=1 + 1 spliced-waker line 25613) | DRIFT: +368 pump lines (wall variance — more vsync ticks in this window); boot-phase non-`-1` split IDENTICAL (29+1, ends 14614) | FULL RUN (steady 60/s pump) |
| 32 | 616 / 615 (206 waker=1 + 205 waker=5 + 175 waker=`-1` + 29 waker=3) | IDENTICAL split | BOOT ONLY (ends 14556) |
| 36 | 1 / 0 (single park @4687) | IDENTICAL | single boot-phase park |
| Other ids | 1:4, 4:3585, 5:2824, 6–25:2 ea, 29:414, 33:1640, 34:4, 35:404, 39:160 (Part C) | DRIFT: id-4 +1 / id-29 +1 / id-39 +6 (boot-phase lock traffic — the delivery path executes during boot; tabled, not root-caused) | — |
| Totals | 11190 waits + 11185 signals = 22375 | Δ +374 = +368 (pump) +1 (id-4) +1 (id-29) +6 (id-39) −2 (damaged-line delta: 2 destroyed-id lines 11057/40275 vs I20's 4 — DPI-splice class) | CLOSED (Part C sums 22373 + 2 destroyed-id = 22375) |

### Creator census cross-check (I20 closed it; I21 re-checks for free)

39 `[diag:sema-create]` (ret=1..39 in order, 0 failures) — the 39 lines are BYTE-IDENTICAL to I20's create extract as a sorted set (`diff` clean). Creators, call sites, max/init: unchanged by the fork move. Full 39-line transcript with line numbers in `logs/launch-e18-console.create-extract.log`.

### Steady-state re-confirmation (I20 baseline; drift tabled with both receipts, never smoothed)

| Check | I21 receipt | vs I20 |
|---|---|---|
| Thread rows (30) | 6/6 `status=2` all 5 blocks; t1 `waitReason=6 waitId=0 pc=0x3b1028 scheduled=8255→0,0,0,0`; t2/t3/t5/t6 `waitReason=2` waitIds 26/30/32/36 `pc=0x423de8`; t4 `waitId=31 scheduled=859→900,900,900,900` | IDENTICAL except t4 block-0 `scheduled` 859 vs 861 (1-count boot variance, §threads) |
| Stub sets | block-0 `distinct=1491`; blocks 1–4 `distinct=13` each, sets identical ×4 (same 13 targets + counts: 3×1800, 10×900, same RAs) | DRIFT: block-0 1491 vs 1482 (+9 — legitimate fork-change movement: the delivery path dispatches new boot-phase targets; delivery addresses are NOT in the printed top-30 — one-shot dispatches below threshold — so the +9 is receipted as a count, not a named set). Steady 13: IDENTICAL. Block-0 top `0x41ea18` ×953382 (I18's value; I19: 953385) |
| Syscall sets | block-0 `distinct=30` (incl. `id=0x40 count=39` — the 39 CreateSema calls); blocks 1–4 `distinct=2` each (`0x44` WaitSema ×900 + `-0x43` iSignalSema ×900) | SHAPE IDENTICAL; boot-count drift: `0x2f` 18062 vs 18050 (+12), `0x44` 6756 vs 6752 (+4), `0x42` 4931 vs 4927 (+4) — legitimate fork-change movement (delivery executes during boot). `0x40`=39 cross-checks the census |
| Frame counters | ALL FIVE `[diag:frame]` readable: vsync 900→4500 (+900/block); kicks=43708 kicksDrawing=43356 gif=2795 copyRegs=4655 dma=4542 gifCopy=210 gsWrites=0 vifWrites=2 BIT-IDENTICAL blocks 0–4 | IDENTICAL values (deterministic boot; submission frozen — 0 frames served) |
| CD timing | 1103 `[diag:cd]` + 1062 `[cd:callback]`; ALL reads precede block-0 dump (last-read line 15109 < 18955); first `lbn=0x10 sectors=1`, last `lbn=0x13bb13` | IDENTICAL (full-log 1103=1103; same first/last lbn; CD quiet 75+ s) |
| MPEG dispatch | `0x402c08` ×2, `0x402a10` ×2 lines (dormant tails); `0x4029d0` ×6 + `0x3b0b10`/`0x3b0b40`/`0x3b06b0` ×2 lines (delivery tails) | NEW (I20: AddBs/producer ×0) — the E18 behavior delta, §delivery |
| Stub-decoder tripwire | `without FFmpeg` ×1 (line 15163), `mpeg` (any case) ×1 | NEW (I20: ×0/×0) — first header fed to the stub |
| St-streaming tripwire | `sceCdSt` ×0 | IDENTICAL (guest still never enters streaming mode — EOF path unchanged) |
| Boot prefix / RPC | K1/install/lookup/handshake identical; same 4 RPC sids, byte-identical lines | IDENTICAL |

### Host-vs-device comparison (E18 host probe × I21 device probe — every row tabled)

| Row | Host E18 receipt | Device I21 receipt | Standing |
|---|---|---|---|
| `0x3b0b10` dispatch | Fires once (selection 1 / invocation 1 / callback 1; word0=1 readable; caller thread1/SP `0x1fffd60`) | FIRES (dormant tails lines 15164/15166, in callback→producer→release→AddBs order) | AGREE (dispatch observed both lanes; device has no ownership/ABI tap — thread/SP/word0 unobserved, never inferred) |
| Producer chain | `0x3b0b10`→`0x3b0b40`→`0x3b06b0`; descriptor `0x548800`, data `0xd48748`, bytes 5036; release `0x3b06f8` observed | `0x3b0b40`→`0x3b06b0`→`0x3e6574`→`0x3b06f8` dispatched in the same tail windows | AGREE (same routine order; descriptor/data/byte values are host-only — unobserved on device) |
| `0x4029d0` dispatch | Called once inside callback scope; buffer `0xdc8340`, requested 5040, returned 5040 | FIRES (6 overlapping tail windows carry it; one actual call site per the sliding-window caveat) | AGREE (dispatch observed both lanes) |
| Actual bytes accepted | 5040 requested = 5040 returned (safe-hash span 5040, FNV64 pinned) | UNOBSERVED — no byte-count line exists device-side (`[MPEG:*]` stub logs are `AGRESSIVE`-gated/compiled out). The stub warning proves `feed()` was ENTERED (bytes reached the decoder), never the count | DEVICE-BLIND (5040 NOT projected from host) |
| Main progress | Waiting/Mpeg at pc=ra=`0x3b1028`, SP `0x1fffd60`; completion events 0 | `waitReason=6 waitId=0 pc=0x3b1028` all 5 blocks; `scheduled=0` blocks 1–4 | AGREE (same park point, still parked both lanes; no named successor on device) |
| Sema 26/30/32 traffic | Not in the host probe (device-side census is the I-lane baseline) | 26: 737/736 boot-only; 30: 5/4 boot-only; 32: 616/615 boot-only — all IDENTICAL to I20 splice-inclusive; no traffic past boot | DEVICE-BASELINE-HELD (the sema chain does NOT unblock with delivery — producers still stall) |
| Decode boundary | FFmpeg-ON: parsed 5040, packets 0, newFrames 0, `decoderFailed=0`, no decoded-frame log | FFmpeg-OFF stub: warning ×1 (`MPEG video decode is disabled`), then NO decode — 0 frames served, main still waits, GS/DMA counters frozen | SPLIT-BY-CONFIG, BOTH OBSERVED (host parser-buffering vs device stub-refusal — the device row is observed, never inferred from the host's receipt) |
| Post-delivery wall | Accepted input → packet/frame → wake INCOMPLETE (parser holds 5040 B, emits 0) | Accepted input → stub `feed()` → `false` → silent retry (0 frames, still parked) | NAMED BOTH LANES (different walls: host = parser-output dependency; device = no-decode dependency) |

### First post-delivery device wall (NAMED — H-a)

**No on-device MPEG decode** (I20 S7 / I19 F7 predicted exactly this edge): delivery now occurs on device (callback + producer + AddBs dispatched, stub `feed()` entered per the ungated warning), but the FFmpeg-OFF stub returns `false` and enqueues nothing (`MPEG.cpp:447-469` + `:1107-1114` retry-later path) → 0 decoded frames → GetPicture's wait condition (`decodedFrames.empty() && !sawEof && !streamEnded && !decoderFailed`) never breaks → main still parked at `0x3b1028`, sema 26/30/32 chains still boot-only, GS/DMA still frozen, screen still black. NO stacking a second fix (this brief implements nothing); the wall gets its own follow-up brief (FFmpeg-for-iOS build? stub-frame completion? — not this report's call).

### Handoff table (what the next briefs consume / what stays)

| # | Item | Disposition |
|---|---|---|
| H1 | This re-probe (delivery-on-device receipts + wall) + I20's A1–A13/S1–S10 | CONSUMED by the follow-up brief that sequences Cause B (device-side decode edge, now DEMONSTRATED post-delivery — no longer behind a hypothesis) |
| H2 | E18's host parser-output dependency (5040 B in, 0 packets out) | STAYS E-lane (their next brief per E18 NEXT-BRIEF; device re-probe must NOT conflate it with the stub wall) |
| H3 | Sema creator census (39/39 byte-identical re-check) + steady-state baselines | STAYS as the I-lane device baseline the next re-probe diffs against |
| H4 | Local worktree stack (`3adc0478` + 3 ports + wiring extension, 0 pushes) | STAYS worktree-local until the E-line allows a merge conversation (note: the wiring extension exists ONLY because E17's in-tree game objects duplicate the I-lane lib — if the E-lane's device story ever consumes `PS2X_GAME_CODEGEN_DIR`, the extension's intent merges with the I10 wiring) |
| H5 | SSD detach before end-of-brief re-verification | Gap G1 (below) — full-log re-sha pending reattach; all committed evidence is intact on the internal drive |
| H6 | E-lane fork ownership + remote moves | E-lane ONLY — I21 moved nothing (remote `3adc0478` at recon AND end; 0 pushes) |

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i21"
git -C "$FORK" ls-remote fork ssx3          # 3adc0478 at recon AND end (E18 pushed; zero advances)
git -C "$FORK" log --oneline -5             # 3adc047 at top ([E18])
git -C "$FORK" status --short               # ?? ps2_log.txt only (recon AND end)
git -C "$FORK" log --oneline 83fb4d6..3adc0478   # exactly 4 commits (E15-obs/E16/E17/E18)
git -C "$FORK" diff --name-only 83fb4d6 3adc0478 # CSV + e15/e4/e7 headers + EeScheduler + MPEG + runtime + runner gen + tests
git -C "$FORK" diff 83fb4d6 3adc0478 -- games/ssx3/ssx3-functions.sweep.csv  # exactly the 5 added rows
for ln in 873 1022 2943 7012 7176; do git -C "$FORK" show 3adc0478:games/ssx3/ssx3-functions.sweep.csv | sed -n "${ln}p"; done
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60  # 582 lines, PID 4516 = I18 leftover
xcrun devicectl device info details --device "$P" --timeout 60 --json-output /tmp/i21-ipad-details.json  # 15382 B
# --- Dedupe reads (local rows from the I18 worktree) ---
W18="/Volumes/Extreme SSD/ps2x-i18/fork-wt"
for c in 7714a85 a3bbabf 6a37c90 b9bcfe6 fe017b2; do git -C "$W18" show "$c" -- games/ssx3/ssx3-functions.sweep.csv | grep "^[+-][^+-]"; done
git -C "$FORK" grep -c "PS2X_GAME_CODEGEN_DIR" 3adc0478        # empty (port needed)
git -C "$FORK" grep -c "diag:frame" 3adc0478                  # empty (port needed)
git -C "$FORK" merge-base --is-ancestor de7ff17 3adc0478 && echo GATE-IN-3ADC0478
# --- Worktree + 3 ports (dedupe: SKIP all 5 CSV rows) + wiring extension ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I21/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 3adc0478
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 337 -> 0
git -C "$WT" -c user.name="muse-i21" -c user.email="i21@local" cherry-pick 46d12d34ee52ab784ede18b87c4c55255a6a1a9d  # -> 3ae0570
git -C "$WT" -c user.name="muse-i21" -c user.email="i21@local" cherry-pick 6a58c9e  # -> 842340c
git -C "$WT" -c user.name="muse-i21" -c user.email="i21@local" cherry-pick 16e1b9a50530d1c230f7aaba3a6502711f7c58d1  # -> 3564273
# (extend the GAME_CODEGEN_DIR block in ps2xRuntime/CMakeLists.txt: glob-drop src/runner/sub_*.cpp + count message)
git -C "$WT" add ps2xRuntime/CMakeLists.txt
git -C "$WT" -c user.name="muse-i21" -c user.email="i21@local" commit -m "I21 wiring: drop in-tree sub_*.cpp when PS2X_GAME_CODEGEN_DIR is set (E17 landed 5 in-tree game objects duplicating the lib)"  # 751a50f
git -C "$WT" show HEAD:games/ssx3/ssx3-functions.sweep.csv | shasum -a 256  # 7c827add... (= I17 = I18 = E17 pin)
shasum -a 256 "$WT/ps2xRuntime/src/runner/sub_0014F2A8_0x14f2a8.cpp" /Volumes/Extreme\ SSD/ps2x-i17/codegen-output/sub_0014F2A8_0x14f2a8.cpp  # equal (740bac80...)
# --- Configure + build (I18 recipe; codegen SKIPPED, 0 runs) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I18=I21
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="/Volumes/Extreme SSD/ps2x-i17/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m24s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 18m08s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 989b2c2a...
shasum -a 256 "$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/libps2_game_objects.a"  # f356aaa7 = I17 = I18
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9454 game text syms
grep -c "diag:frame" "$APP/ps2EntryRunner"; strings -a "$APP/ps2EntryRunner" | grep -c "without FFmpeg"  # 1 / 1
# --- Stage/sign/install (I18 recipe) ---
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (5.1s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 76.7s
# --- ONE 90 s probe (I20 env) ---
B="/private/var/containers/Bundle/Application/AAA5E829-B0A3-4698-A46E-CB2785CE9EAD/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-e18-console.log" 2>&1    # exit 2 (alive, PID 4669), 45697 lines / 17.1 MB
L="$W/logs/launch-e18-console.log"
grep -c "diag:sema-create" "$L"              # 39 (creator cross-check)
grep -c "diag:sema]" "$L"                    # 22375 (census)
grep -c "guest-branch\|missing-target" "$L"  # 0 (no wall)
for a in 0x4029d0 0x402a10 0x402c08 0x3b0b10 0x3b0b40 0x3b06b0 0x3b1028; do printf "%s: " "$a"; grep -c "$a" "$L"; done
grep -c "without FFmpeg" "$L"; grep -ciE "mpeg" "$L"; grep -c "sceCdSt" "$L"  # 1 / 1 / 0
grep -h "\[diag:thread\]" "$L"               # 30 rows (main still 0x3b1028)
grep -h "diag:frame" "$L"                    # 5 lines, counters frozen
for id in 26 30 31 32 36; do echo "== $id"; grep -c "op=wait id=$id " "$L"; grep -c "op=signal id=$id " "$L"; done
grep "op=signal id=31 " "$L" | grep -oE "waker=-?[0-9]+" | sort | uniq -c   # per-id waker splits (x5 ids)
grep -oE "op=(wait|signal) id=[0-9]+" "$L" | grep -oE "id=[0-9]+" | sort -t= -k2 -n | uniq -c  # Part C
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i21 -s ps2EntryRunner --no-recurse  # 5 files, all priors
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i21-shot1.png
mv /tmp/i21-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4669  # cleanup only
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i21 -s ps2EntryRunner --no-recurse  # still 5
# --- Evidence extracts (deterministic; /tmp/i21-extracts.sh) ---
grep -v "GetWindowScaleDPI" "$L" | grep -v "diag:dormant" > "$W/logs/launch-e18-dedup.log"  # 24988 lines
grep -v "diag:sema" dedup >> diag-extract (2615 lines + header)
grep -n "diag:sema-create" full >> create-extract (COMPLETE 39 + header)
grep "diag:sema]" dedup | grep -v "id=31" >> sema-extract Part A (complete non-31)
id=31 head/tail-10 xwait/signal >> Part B; full-log per-id counts >> Part C
grep -n "0x4029d0|0x3b0b10|0x3b0b40|0x3b06b0" + warning >> delivery-extract (7 lines)
shasum -a 256 "$L" "$W/logs/launch-e18-dedup.log"
find local/research/I21 -name "._*" -delete; find local/research/I21 -name "._*" | wc -l  # 0
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | SSD detached before end-of-brief re-verification (volume gone from `diskutil list` — physical reattach needed; NOT a data event: all committed evidence is intact on the internal drive) | `ls /Volumes` + `diskutil list` (no Extreme SSD) after the extracts were built | No code brief — reattach the SSD, then re-run ONE command: `shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i21/logs/launch-e18-console.log` (expect `d92f8712…`) to close the full-log receipt |
| G2 | No on-device MPEG decode (delivery lands, stub warning fires, 0 frames, main still parked) | §first-post-delivery-wall (warning ×1 + frozen counters + still-parked threads) | The Cause-B follow-up brief (FFmpeg-for-iOS build? stub-frame completion? — its own brief per the no-stacking rule) |
| G3 | Actual bytes accepted on device UNOBSERVED (no byte-count line; AGRESSIVE-gated) | Host-vs-device bytes row (DEVICE-BLIND by design) | Fold into any future device-tap brief IF byte counts become observable (env-gated tap, no rebuild of the question here) |
| G4 | Block-0 stub-distinct +9 carried as a count, not a named set (delivery addresses below the top-30 print threshold) | Steady-state stub row (top-30 has 0 delivery hits) | Informational — no brief (the count moves legitimately with the fork; naming needs a deeper-histogram tap) |
| G5 | NO new `.ips` six briefs running (5 files, all priors' — I11–I15 each filed one spin report; I16–I21 file none) | `logs/crashlog-check.log` (sleep + re-`ls` AND post-terminate re-`ls`: still 5) | Informational — consistent with a non-spinning waiter; next brief's first `ls` confirms I21; no brief unless a later probe shows action-taken |
| G6 | `3ae0570` + `842340c` + `3564273` + `751a50f` unpushed (E-lane owns the fork; zero fork commits by design) | Worktree log, 0 pushes; remote `ssx3` at `3adc0478` | No code brief — merge conversation when the E-line allows (wiring-extension intent noted in H4) |
| G7 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest still in movie/sema wait | Data-container brief (only if a later probe fails on file I/O) |

## Receipt paths

- `local/research/I21/REPORT.md` (this file)
- `local/research/I21/logs/launch-e18-console.diag-extract.log` (2615-line deterministic non-sema extract + header with full-log sha)
- `local/research/I21/logs/launch-e18-console.create-extract.log` (COMPLETE 39-line creator transcript + header)
- `local/research/I21/logs/launch-e18-console.sema-extract.log` (11858-line sema extract: complete non-31 + id-31 samples + full-log counts)
- `local/research/I21/logs/launch-e18-delivery.log` (6 delivery tails + stub warning), `launch-e18-frame.log` (5 frame lines), `launch-e18-console.sizes` (counts + shas)
- `local/research/I21/logs/cherry-pick.log` (transcribed worktree-add + picks + wiring commit), `wiring-extension.diff` (the 7-line build fix)
- `local/research/I21/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I18's), `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I21/logs/ipad-details.json` (via DIRECT `--json-output <path>` — 15382 B), `processes-pre.log`, `entitlements.plist`
- `local/research/I21/logs/install.log` (overwrite, exit 0, 76.7 s), `elf-device-path.txt`
- `local/research/I21/logs/crashlog-check.log` (check1 + check2, still 5 priors), `screenshot.log`, `i21-shot1.png` (iPad window, black content)
- `W/logs/` (same + full 45697-line console + full dedup + full build log on SSD — pending G1 reattach for re-verification); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `751a50f`, clean, 4 local commits, 0 pushes); NO `W/codegen-output/` (C17 reused read-only)
- No fork push this brief (nothing to push — zero fork commits by design)

## What I could not do

- Observe actual bytes accepted on device — no byte-count line exists (AGRESSIVE-gated); the stub warning proves `feed()` entry, never the count (G3).
- Name the block-0 +9 stub targets individually — below the top-30 print threshold (G4).
- Verify the E18 host parser-output dependency from the device side — different config, different wall; the host row is E18's own receipt (§comparison).
- Re-verify the full-log sha at commit time — the SSD detached after the extracts were built (G1; sha `d92f8712…` receipted at probe time).
- Count full-log DPI lines directly for the line-bridge — same SSD detach; the +274 DPI term is an exactly-derived residual with every other component directly counted (§launch shape).
- Present a guest frame — window stays black with delivery landing but 0 frames decoded and GS submission frozen since boot; first presented content awaits the Cause-B brief (G2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I21); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (PVD bytes + IRX loads + 1103 reads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never observably reached file I/O past the boot CD reads (G7).
- Push the 4 local commits — the E-line owns the fork (G6; local commits only; H4 notes the wiring-merge intent).
- Explain why no `.ips` filed six briefs running — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); the non-spinning waiter profile is consistent but not proven causal (G5).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe and I-series precedent; blocks 1–4 identical steady sets are the in-probe determinism receipt.
- Name the launcher of pre-install PID 4516 — the I18 bundle was running though I20 reported 0 `ps2` at its cleanup (sixth brief running with a relaunched occupant); it was reaped by the install without investigation.

## TAIL RECEIPT

Report written in 5 chunks (header + contract + caps; Task 1 dedupe + recon + ports + wiring + codegen + build + install; Task 2 probe + delivery + threads + sema + creators; steady-state + host-vs-device + wall + handoff; commands + gaps + receipts + could-not-do). Pre-receipt measure: 380 lines total, sha256 `751ca557eb52409090afeab9c8e90b5c3626339128989c69f727368caa6bdac8` over lines 1–380 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Name the launcher of pre-install PID 4516 — the I18 bundle was running though I20 reported 0 `ps2` at its cleanup (sixth brief running with a relaunched occupant); it was reaped by the install without investigation." This receipt line ends the report. END-I21-REPORT.
