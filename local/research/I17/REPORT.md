# I17 — Close the 0x2c5358 indirect-target gap at the E12 base (dedupe E12's row), re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I16/REPORT.md` read first (all of it: base stayed `ffdf58c` (case (b) — no E12 commit existed) + 7 ports + 1-line CSV entry closed `0x2c5300` (`0x2c5300` executes mid-trace with successors `→ 0x2c67a8 → 0x2d3928 → …`), guest reaches a STRICTLY LATER wall: indirect JALR `0x2d3828 → 0x2c5358` (mid-function of emitted `sub_002C5338` `0x2c5338–0x2c53b0`, head after `jr $ra` @`0x2c534c`/ds `0x2c5350`/nop @`0x2c5354`, INTERNAL branches + tail `jr $ra` @`0x2c53a0`/`0x2c53a8` → return, ends `0x2c53b0`, observed bounds `0x2c5358–0x2c53b0`, caller `jalr $v0` @`0x2d3828` with record+offset table load, 0 register refs/case/file; gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I16; the I16 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4290, same bundle UUID as I16's install — relaunched after I16's cleanup by an unknown launcher; state tabled in Task 2).
- BASE: MOVED `ffdf58c` → `9da21ff` (E-lane advanced exactly 1 commit; the E12 row HAS landed fork-side inside `9da21ff` itself — DEDUPE case, not case (b)) — separate fork worktree at `9da21ff` + ported I16's 7 non-`0x2c5300` commits (patches content-identical to I16's) + ONE local map commit `32d37e7` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane live: recon `M register_functions.cpp` + `?? ps2_log.txt`; end-of-brief peek 4 modified + 1 untracked, INCLUDING the byte-identical `0x2c5358` row uncommitted in their tree — independent convergence again, tabled in Task 1).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9455 SSX3 sources from host `ps2_recomp` codegen, +1 vs I16: our `0x2c5358`) on the E9 runtime + E11 read-only card-query taps + E12 card status predicate.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i17/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging + evidence; evidence `local/research/I17/` standalone, `[I17]` commit, no push.
- Outcome shape: I16 wall GONE — NO `[guest-branch:missing-target]` of any kind in the 90 s console (`0x2c5358`/`0x2d3828` 0 refs anywhere; normalized dedup `diff` vs I16 = exactly I16's wall line deleted, ZERO additions) and NO successor wall is named: guest alive the full 90 s (exit 2, PID 4314) with a byte-identical event prefix. No crash; no NEW `.ips` for I17 AND no late filing for I16 (5 files, all priors'). Screen still black. Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i17/`, `WT` = `W/fork-wt` (fork worktree), `W16` = `/Volumes/Extreme SSD/ps2x-i16/`, `C` = `W/codegen-output/` (host codegen), `C16` = `W16/codegen-output/`, `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x2c5358` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I16's wall — the `0x2d3828 → 0x2c5358` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | E12-dedupe receipts (HEAD row bytes + I16 row bytes); codegen exit/counts/shas + `0x2c5358` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present; first `ls` also checks for late I16 filing) + screenshot; past-the-wall table vs I16 |
| Alternatives | H-a `0x2c5358` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x2c5358` still missing — entry did not land) |
| Stop | All bars tabled (dedupe/entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~60 min wall: worktree+ports → codegen 3m15s → configure 1m25s → build 14m28s → install 68s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT ~350M | `du -sh W` after evidence step |
| Evidence `local/research/I17/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i17-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 8 local commits (7 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 3m15s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Dedupe + entry fix + host codegen + device link (no iPad)

### Pin + E12 check + worktree + cherry-picks (BASE MOVED — dedupe case)

| Item | Receipt |
|---|---|
| Pin (MOVED) | `9da21ff` = `9da21ff8aeb9529368b32d91b0eec6a82ba79344` (expectation `9da21ff`-or-later met exactly) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `9da21ff` at recon AND at end-of-brief (E-lane advanced exactly once past I16's base) |
| Range `ffdf58c..9da21ff` | Exactly 1 commit: `9da21ff` "SSX3: restore the exact card status predicate" (Brad, 06:15:17 — after I16's 05:42 local `b07f738`): CSV +1, `ps2_e7.h` 12 +/-, `ps2_runtime.cpp` 6 +/- |
| E12 row at HEAD (BEFORE writing) | CSV at `9da21ff` line 5094 `sub_002C5300,0x2c5300,0x2c5320,0x20`; `,0x2c5300,` count 1; `log --all --grep=E12` empty (no commit literally named E12 — the "E12 row" is the row E12 was converging on, landed inside `9da21ff`) |
| Dedupe (both shas+bytes tabled) | E12 hunk (`9da21ff8aeb…`): `+sub_002C5300,0x2c5300,0x2c5320,0x20` with context `sub_002C52D8` above / `sub_002C5320`+`sub_002C5338`+`sub_002C53B0` below — BYTE-IDENTICAL added line + same sorted position as I16's `b07f73888f0dcc…` hunk (hunk offsets `@@ -5091` vs `@@ -5094` differ only by the 3 I12/I13/I14 local rows above the site — expected, tabled) |
| SKIP (not ported) | I16's `b07f738` (`0x2c5300` row) SKIPPED — already in base via `9da21ff`; merged-CSV `,0x2c5300,` count re-verified = 1 (no duplicate) |
| E-lane owner | Live — recon peek: shared `ssx3` @`9da21ff` with `M register_functions.cpp` + `?? ps2_log.txt`; end-of-brief peek: 4 modified (CSV +1, `ps2_e7.h` 27+/-, `ps2_runtime.cpp` 2+/-, `register_functions.cpp` 398976 churn) + 1 untracked (`ps2_log.txt`) — E-lane edited DURING this brief; remote unmoved |
| Convergence (read-only peek) | E-lane's uncommitted CSV hunk is the BYTE-IDENTICAL row `sub_002C5358,0x2c5358,0x2c53b0,0x58` — independent convergence on THIS brief's row, zero merge conflict on that line |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 9da21ff` → `HEAD is now at 9da21ff` (exit 0) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry** (SAME shape as I16): `71c2690` = `52ac12e` (Info.plist CFBundleName), `258482d` = `61f1c9b` (22-insertion CMake wiring), `1b80226` = `6268acf` (I11 CSV row), `5ff15c4` = `35bdef3` (I12 CSV row), `028cf63` = `dcae122` (I13 CSV row), `83126a6` = `1607382` (I14 CSV row), `7a8007a` = `3832a67` (I15 CSV row); attempt 1 applied 3/7 then aborted on the transient dirty-tree complaint (tree verified clean); NO `--quit` needed this brief (delta vs I16's exit-1 `--quit` — picks below prove the sequencer resolved); picks 4+5+6+7 applied individually exit 0; `logs/cherry-pick.log` |
| Patch identity | All 7 ports content-identical to I16's (`diff` of `^[+-][^+-]` lines clean for each pair) |
| Merged CSV rows | E12's `0x2c5300` @5097 + ported `0x14f2a8` @873 + `0x156750` @1022 + `0x243a80` @2943 + `0x395730` @7011 + `0x3a0158` @7175 |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / show / status / diff --stat / diff <csv>`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | YES — `9da21ff+71c2690+258482d+1b80226+5ff15c4+028cf63+83126a6+7a8007a` + new entry fix; tool binary reused, not rebuilt (base move touches CSV + runtime only — recompiler/analyzer byte-identical by `diff --name-only`) |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read (new WT, post-port): line 5099 `sub_002C5338,0x2c5338,0x2c53b0`, line 5100 `sub_002C53B0,0x2c53b0,0x2c53c8`; no row starts in `0x2c5339–0x2c53af` | No function in the gap range; new row overlaps the container (toolchain-tolerated per I11–I16 receipts) |
| 2 | C16 emitted `sub_002C5338_0x2c5338.cpp` RE-READ: `jr $ra` @`0x2c534c`, ds `addiu $sp` @`0x2c5350` emitted, nop `0x2c5354`, then `0x2c5358: addiu $v0,$zero,0x14` + `0x2c535c: addiu $v1,…` heading the next function; internal branches `beq` @`0x2c536c`, `beqz` @`0x2c5374` (I16's receipt said `beq` — corrected here, tabled), `beq` @`0x2c537c`, `b` @`0x2c5384`, `bgtz` @`0x2c538c`, `bnez` @`0x2c5398`; tail `jr $ra` @`0x2c53a0` (ds `addiu $v0` @`0x2c53a4`) → return AND `jr $ra` @`0x2c53a8` → return, then `ctx->pc = 0x2C53B0u; }` (function ends exactly at container end) | `0x2c5358` is a genuine function head with observed bounds `0x2c5358–0x2c53b0` (`0x58`, end-exclusive at the next CSV row start — same convention as I11–I16 rows). I16's observed row VERIFIED byte-for-byte |
| 3 | Caller emission `sub_002D2988` (I16 receipt carries — recompiler/analyzer byte-identical across the base move, and the caller file is SAME in the new codegen per §non-perturbation): `0x2d3818: lw $v1,0x0($a0)` then `0x2d3820: lh $a2,0x1A0($v1)` then `0x2d3824: lw $v0,0x1A4($v1)` then `0x2d3828: jalr $v0` | Call target is runtime-computed (record+offset table load via `$v0`) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: direct-edge-only resume discovery (I11–I16 receipt; recompiler sources identical across the base move — `diff --name-only` proves — so the receipt carries) | It CANNOT learn `0x2c5358` (0 direct edges: `0x2c5358` count 0 in `register_functions.cpp`, 0 `case 0x2c5358u` in any of 9456 C16 files, no `*0x2c5358*` file) |
| 5 | `function_table_emitter.cpp` first-wins dedupe + `lookupFunction` null-slot → `missing-target` park (I11 receipt, carries) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry |
| 6 | Merge safety: ELF stripped (I11 receipt, same ELF bytes `1b49d05c…` re-sha'd); authoritative CSV rows ≥`0x3ff088` (I11 receipt, carries — this CSV is I16's + 1 auto-named row, all below that floor) | New auto-named row at `0x2c5358` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 5100: `sub_002C5358,0x2c5358,0x2c53b0,0x58` (inserted in sorted position; `sub_002C5338` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — precise toml grep shows zero `0x2c5*` entries and the new body (addiu/mult/addu/lw/beq/b/bgtz/bnez/jr) has no SIMD/loops) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `32d37e7 SSX3 map: add missing function entry 0x2c5358 (I17)` = `32d37e794fd87635a559e9baa85fa554f143393b` (1 file, 1 insertion); worktree `9da21ff+71c2690+258482d+1b80226+5ff15c4+028cf63+83126a6+7a8007a+32d37e7`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I16 worktree CSV | `diff` = exactly 1 added line (our `0x2c5358` row — E12's `0x2c5300` now comes from base instead of a local commit, same bytes); tracked toml byte-identical to I16's (no base-move change) |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: base-move `diff --name-only ffdf58c 9da21ff` = CSV + `ps2_e7.h` + `ps2_runtime.cpp` ONLY (`ps2xRecomp`/`ps2xAnalyzer` byte-identical); toml = tracked (byte-identical to I16's) + 2 path edits; ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11/I12/I13/I14/I15/I16) |
| TOML | `W/ssx3-i17.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` vs tracked = 2 lines; vs I16's TOML = the same 2 path lines re-pointed i16→i17 |
| Exit / wall | exit 0, 3m15s (`Loaded 9283 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3712 `[warning]`s (SAME count; warning SET identical — sorted-`diff` clean); `errors: 0`) |
| Recompiler report | (I16 → I17) discovered 9453→9454 (+1); recompiled 9276→9277 (+1); stubs 177→177; resumable entry points 401448→401448 (+0) across 7612→7612 owners (+0 — the new function contributes 0 resumable entries despite its internal branches, tabled as observed); unhandled 0→0 |
| Outputs | 9457 files: 9455 `.cpp` (9454 functions + `register_functions.cpp`), 2 headers; file-list `diff` C16→C = exactly +1 (`sub_002C5358_0x2c5358.cpp`) |
| `0x2c5358` census | NEW `sub_002C5358_0x2c5358.cpp` 6271 B sha `f1922e80…` (`Address: 0x2c5358 - 0x2c53b0`; head `0x2c5358 addiu $v0,…`; `jr $ra` @`0x2c53a0`/`0x2c53a8` → return tails; ends `ctx->pc = 0x2C53B0u`); table slot `g_ps2RecompiledFunctionTable[464084] = sub_002C5358_0x2c5358; // 0x2c5358` (exactly 1 slot — register `diff` is exactly the 1 added line; no resume re-homes) |
| Non-perturbation | `sub_00100008` SAME; `sub_002C5338` SAME (overlap changed nothing); `sub_002D2988` SAME (caller); `sub_002C52D8`/`sub_002C5300`/`sub_002420C8` SAME; `sub_00243A80`/`sub_00156750`/`sub_0014F2A8`/`sub_00395730`/`sub_003A0158` SAME; `ps2_recompiled_functions.h` +1 line only; `ps2_recompiled_stubs.h` IDENTICAL |
| Size/purge | 9.3G ExFAT; 9457 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I16)

| # | Item | I16 | I17 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9454 sources) | Same wiring, ported content-identical (`258482d` = `61f1c9b`); 9455 sources | NO (count +1 only) |
| 2 | Base | `ffdf58c+52ac12e+61f1c9b+6268acf+35bdef3+dcae122+1607382+3832a67+b07f738` (E9 runtime + E11 card taps + I8 plist + I10 wiring + I11 row + I12 row + I13 row + I14 row + I15 row + local `0x2c5300` fix) | `9da21ff+71c2690+258482d+1b80226+5ff15c4+028cf63+83126a6+7a8007a+32d37e7` (E9 runtime + E11 card taps + E12 card status predicate + I8 plist + I10 wiring + I11 row + I12 row + I13 row + I14 row + I15 row + E12's `0x2c5300` from base + new `0x2c5358` fix) | BASE MOVED (E12: card predicate + `0x2c5300` row); map +1 row |
| 3 | Toolchain/SDL2/raylib/flags | I16 §toolchain | Byte-identical toolchain (`diff` clean I9=I16=I17); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1 re-verified via `--version`), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure (same count as I16) | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9457 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m25s (`PS2X: game objects: 9455 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full). Note: 4 `non-monotonic index ._pack-…idx` lines inside the log (cosmetic, exit 0; owner's tree, tabled not root-caused) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (in xcodebuild invocation line + `Build task concurrency set to 2`), 14m28s wall (delta vs I16 8m22s — tabled, not root-caused), 0 `error:` lines (`logs/ios-runtime-build-tail.log` in evidence, full 3360-line log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121225416 B / `7e12163c6ed3243784fa00c33561cc5b8617d4de69c81d3c29703b8fc528c693` (I16: 121225288 B — delta +128 B = 1 new game function + E12 card-predicate runtime delta, tabled as observed) |
| lib | `libps2_game_objects.a`, 155327984 B (I16: 155326176 B, +1808 B — unity-build variance + new file, tabled as observed) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0` |
| Table-populated proof | **9454** `T …_0x…` game text syms (I16: 9453, +1 = new `0x2c5358` entry); **`__Z21sub_002C5358_0x2c5358…` defined `T`** (the gap entry is in the slice); I16's `sub_002C5300_0x2c5300` + I15's `sub_003A0158_0x3a0158` + I14's `sub_00243A80_0x243a80` + I13's `sub_00156750_0x156750` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base in `S` |
| SDL count | 296 `T _SDL_` — identical to I16 (slice growth is game+runtime, not SDL) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `71c2690` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 18G after staging (same shape as I16) |
| Build breaks fixed | NONE — clean first try at the new base (wiring class + E9/E11/E12 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), UDID `P`, connected, developerMode enabled (`logs/ipad-details.json` — captured via DIRECT `--json-output <SSD path>`: WORKED again this brief, 15415 B — same size as I16 — exit 0).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install — no `Locked` failure |
| Running processes | 578-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4290 = the I16 build STILL RUNNING (same bundle UUID `736F005D-…` as I16's install; relaunched after I16's cleanup by an unknown launcher — I16 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 6th brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4290 reaped BY the install itself; 4314 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I17 build + ISO; MF1/I8–I16 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/lock/processes/details/files/screenshot 60, install 1200, launch 90, terminate 30) |

### Provision + sign + install (I16 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I16 shape | I17 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 1.8s, ISO `cp` 25.7s (delta vs I16 19.5s — ExFAT variance, tabled); sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I16=I17) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (15.1s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (8× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 68s, clean replace** — new `installationURL …/4F6584B3-…/` (I16's was `736F005D-…`), live occupant PID 4290 reaped BY the install (0 `ps2` after). Ninth clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/4F6584B3-435A-4B52-A6EA-B1AFB571F752/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX modules in `loadedModules` lists — same 12, sort-u listed) |

### Launch (argv probe, ISO+env — I10–I16 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive, PID 4314), 5211 lines, 76-line dedup (5135 DPI-spam lines) |
| I16 wall | **GONE — zero refs anywhere**: `0x2c5358` 0, `0x2d3828` 0, `0x2c5300` 0, `0x242150` 0, `0x3a0158` 0, `0x39cd74` 0, `0x243a80` 0, `0x156750` 0, `0x14f2a8` 0, `0x395730` 0; `guest-branch` lines 0 (ANY kind, not just `missing-target`); `dispatchGuestBranch` 0 |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (14 lines, byte-identical); TEXTURE IDs 1–4 (5 lines, byte-identical); 12 IRX modules (same 12 `cdrom0:/data/modules/*.irx`, sort-u identical to I16's); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown; E11/E12 card taps: 0 console lines (taps share E7's ordered sink, not the console — observed) |
| NEW wall | **NONE in 90 s**: no `missing-target` of any kind; `trap/fault/abort/exception/panic` grep = 4× `Default` substring (TEXTURE/SHADER/RLGL/FONT lines) + the timeout-abort line (all environmental); only the same 4 unhandled RPC sids (byte-identical lines) |
| RPC record | Same 4 unhandled sids as I16 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44` — dedup lines byte-identical to I16's) |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11's `…-015423.ips` + I12's `…-023911.ips` + I13's `…-032937.ips` + I14's `…-040134.ips` + I15's `…-050020.ips`) — **NO new `.ips` for I17 AND no late filing for I16** (delta vs I11–I15, each of which filed one spin report; tabled, not root-caused) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i17-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content — sha differs from I16's (clock 7:06 AM + wallpaper phase), content same black, new process state (past the I16 wall, no successor wall) |

### Past-the-wall table vs I16

| I16 fate | I17 fate | Wall status |
|---|---|---|
| `missing-target … source=0x2d3828 target=0x2c5358` (1×, line 192 complete); `0x2c5358` 1 ref total (as unexecuted `target=`); trace ENDS `… → 0x2d3810` | `0x2d3828`/`0x2c5358` 0 refs anywhere; `guest-branch` 0 lines; guest alive the full 90 s (exit 2, PID 4314, terminated by us); normalized dedup `diff` I16→I17 = exactly I16's wall line deleted, ZERO additions | **I16 WALL GONE, no successor named** |
| Faulting thread parks at `0x2c5358`; I16 console carries the deterministic park at the previously-unreached site | No park at the deterministic site with a byte-identical event prefix; single probe | **JALR resolves** (proof shape: absence-of-park at the deterministic site + identical prefix + live guest — differs from I16's in-trace-successor proof; tabled, not over-claimed) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical lines | Same boot phase, wall gone, nothing new |
| 5 `.ips` (I11's + I12's + I13's + I14's + I15's own spin reports), I16 filed none | NO new `.ips` (5 files, all priors' — no late I16 filing either) | Healthier-or-equal (no crash; no spin report filed two briefs running) |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels (new capture), new state |

Event-prefix identity (the execution proof): normalized `diff` (timestamp/PID/UUID-stripped) of the dedups shows ONLY the wall-line deletion (`76d75` — I16's complete `source=0x2d3828 target=0x2c5358 … trace=0x2c51d0 → … → 0x2d3810` head) with ZERO additions and ZERO other moves — not even the mouse-plist timing move I16 showed vs I15. K1 block byte-identical; TEXTURE 1–4 identical; all 4 RPC lines identical; handshake identical; I16's wall has NO counterpart in I17 (events flow uninterrupted, then silence — no wall of any kind for the remaining ~89 s).

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: I16 wall gone, NO successor wall named — guest runs past silently

| # | Claim | Evidence |
|---|---|---|
| 1 | The `0x2d3828 → 0x2c5358` JALR resolves — no park at the deterministic site | `guest-branch` lines 0 (any kind); `0x2c5358`/`0x2d3828` 0 refs in the complete 5211-line console; normalized dedup `diff` I16→I17 = exactly the wall line deleted, 0 additions; the slot exists (`[464084]`, sym `T`) |
| 2 | No successor wall is named in 90 s | No `missing-target` of any kind; `dispatchGuestBranch` 0; `trap/fault/abort/exception/panic` = environmental only; only the same 4 unhandled RPC sids (byte-identical, guest continues past them since I10); no crash; no NEW `.ips` (5 priors; no late I16 filing either) |
| 3 | Guest + loop alive, same boot phase, still no frame | Exit 2 with PID 4314 alive the full 90 s (terminated by us); `ee:idle` 0; no teardown; open-fail 0; `sceCdRead unresolved` 0; 12 IRX loaded; screenshot black content, app foreground |
| 4 | The next layer is un-instrumented, not a coverage hole | The console names NO address, symbol, or failing call past `0x2c5358` — there is no target to write a map entry for and no config surface that emits one; the guest's post-entry pc is unobserved |
| 5 | Class | Observability gap (runtime/device-harness) — NOT map layer (no address named), NOT config (no flag/plist/path/packaging change names or moves guest pc) |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add a CSV map entry + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the class of I11–I17's own gap-closing work | NO CANDIDATE: no address is named by any wall; a second fork-code cycle with no target belongs to no brief |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: there is no failing surface to tweak — the guest runs, it just runs silently |
| Unhandled RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`) | `ps2xIOP` subsystem | NOT attempted — guest continues past them today (I10–I17); only actionable if the next brief's instrumentation shows the guest waiting on one |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9454 syms, 8 walls closed-or-passed by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; there is no second gap to close — only an un-named next layer).

Contract outcome: **H-a for the I16 wall** (`0x2d3828 → 0x2c5358` resolves — deterministic park gone, guest runs with an identical prefix and stays alive); **past H-b overall** (the "NEW named wall" alternative did NOT occur — 90 s of silence). The ONE next action: **observability brief — instrument guest execution past `0x2c5358` to name the next layer** (pc/trace taps or periodic pc sampling + frame/GS observation; if the guest is found waiting on one of the 4 unhandled RPC sids, THEN a `ps2xIOP`-profile brief) — runtime/device-harness class, NOT a map-entry brief.

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i17"
git -C "$FORK" ls-remote fork ssx3          # 9da21ff (E-lane advanced exactly once past I16's base)
git -C "$FORK" log --oneline -4             # 9da21ff at top (non-monotonic noise filtered)
git -C "$FORK" status --short               # M register_functions.cpp + ?? ps2_log.txt at recon
git -C "$FORK" worktree list                # 16 entries incl. W16/fork-wt @b07f738
git -C "$FORK" show 9da21ff:games/ssx3/ssx3-functions.sweep.csv | grep -n "002C5300"  # line 5094 -> dedupe case
git -C "$FORK" log --all --oneline --grep="E12"        # empty (row landed inside 9da21ff, untagged)
git -C "$FORK" log --oneline ffdf58c..9da21ff          # exactly 1 commit (9da21ff)
git -C "$FORK" show 9da21ff --stat              # CSV +1, ps2_e7.h, ps2_runtime.cpp
git -C "$FORK" diff --name-only ffdf58c 9da21ff # same 3 files (recompiler/analyzer identical)
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks (dedupe: port I16's 7, SKIP b07f738) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I17/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 9da21ff
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" cherry-pick 52ac12e 61f1c9b 6268acf 35bdef3 dcae122 1607382 3832a67  # full SHAs; 3/7, transient abort on 4th
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" cherry-pick 35bdef3  # retry clean -> 5ff15c4
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" cherry-pick dcae122  # retry clean -> 028cf63
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" cherry-pick 1607382  # retry clean -> 83126a6
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" cherry-pick 3832a67  # retry clean -> 7a8007a
# 71c2690, 258482d, 1b80226, 5ff15c4, 028cf63, 83126a6, 7a8007a (content-identical to I16's)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -n "002C5338\|002C53B0" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: rows jump 0x2c5338 -> 0x2c53b0
grep -n "0x2c5348\|0x2c534c\|0x2c5350\|0x2c5354\|0x2c5358" /Volumes/Extreme\ SSD/ps2x-i16/codegen-output/sub_002C5338_0x2c5338.cpp  # jr/ds/nop/head
grep -n "0x2c536c:\|0x2c5374:\|0x2c537c:\|0x2c5384:\|0x2c538c:" /Volumes/Extreme\ SSD/ps2x-i16/codegen-output/sub_002C5338_0x2c5338.cpp  # internal branches
sed -n '185,220p' /Volumes/Extreme\ SSD/ps2x-i16/codegen-output/sub_002C5338_0x2c5338.cpp  # jr @0x2c53a0/@0x2c53a8, ends 0x2c53b0
grep -c "0x2c5358" /Volumes/Extreme\ SSD/ps2x-i16/codegen-output/register_functions.cpp  # 0 refs
grep -rl "case 0x2c5358u" /Volumes/Extreme\ SSD/ps2x-i16/codegen-output  # 0 files
grep -n "0x2c5\|0X2C5\|002C5" "$WT/games/ssx3/ssx3.toml"  # no 0x2c5 neighbors -> no toml change
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_002C5358,0x2c5358,0x2c53b0,0x58 after line 5099 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i17" -c user.email="i17@local" commit -m "SSX3 map: add missing function entry 0x2c5358 (I17)"  # 32d37e7
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i17.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i17.toml"  # exit 0, 3m15s
ls "$W/codegen-output" | wc -l                                       # 9457 (9455 cpp + 2 h)
grep -n "0x2c5358" "$W/codegen-output/register_functions.cpp"  # slot 464084 (exactly 1)
diff /Volumes/Extreme\ SSD/ps2x-i16/codegen-output/register_functions.cpp "$W/codegen-output/register_functions.cpp"  # 1 added line
find "$W/codegen-output" -name "._*" -delete                        # 9457 -> 0
# --- Task 1d: device configure + build (I16 shape, new base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I16=I17
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m25s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 14m28s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 7e12163c...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9454 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*2C5358_0x2c5358"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details-direct.json"  # WORKED again (15415 B)
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 578 lines, PID 4290 = I16 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (15.1s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 68s
B="/private/var/containers/Bundle/Application/4F6584B3-435A-4B52-A6EA-B1AFB571F752/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive, PID 4314), 5211 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i17 -s ps2EntryRunner --no-recurse  # 5 files, all priors
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i17-shot1.png
mv /tmp/i17-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4314  # cleanup only
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i17 -s ps2EntryRunner --no-recurse  # still 5 (no new .ips)
# --- Task 3: diagnosis reads ---
grep -v "GetWindowScaleDPI" "$W/logs/launch-cdimage-console.log" > "$W/logs/launch-cdimage-dedup.log"  # 76 lines
diff <(normalized I16 dedup) <(normalized I17 dedup)  # 76d75: exactly I16's wall line deleted, 0 additions
grep -c "guest-branch" "$W/logs/launch-cdimage-console.log"  # 0 (any kind)
git -C "$FORK" diff -- games/ssx3/ssx3-functions.sweep.csv  # E-lane uncommitted: byte-identical 0x2c5358 row
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Next guest layer past `0x2c5358` is UN-NAMED (no console wall of any kind in 90 s; byte-identical event prefix; guest + loop alive; screen still black; no crash; no `.ips`) | Normalized dedup `diff` I16→I17 = exactly 1 deletion (I16's wall line), 0 additions + `guest-branch` 0 + exit 2/PID 4314 alive + black `i17-shot1.png` | Observability brief: instrument guest execution past `0x2c5358` (pc/trace taps or periodic pc sampling + frame/GS observation) to NAME the next layer — runtime/device-harness class, NOT a map-entry brief (THE one next action; the I11–I17 map-entry line is done until a wall names an address again) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10–I16) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's instrumentation shows the guest waiting on one): implement handlers per the trace payloads |
| 3 | `71c2690` + `258482d` + `1b80226` + `5ff15c4` + `028cf63` + `83126a6` + `7a8007a` + `32d37e7` unpushed (E-lane mutating; shared clone has uncommitted E-work including the byte-identical `0x2c5358` row + card-predicate edits + `register_functions.cpp` churn) | Worktree log `32d37e7^… = 9da21ff`, 0 pushes; remote `ssx3` at `9da21ff` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows (note: E's in-flight row is byte-identical, so the `32d37e7` hunk will merge clean) |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I16 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | NO new `.ips` two briefs running (5 files, all priors' — I11–I15 each filed one spin report; I16 filed none and I17 confirms no late I16 filing) | `logs/crashlog-check.log` (post sleep + re-`ls` AND post-terminate re-`ls`: still 5) | Informational — possible under-threshold CPU (no spin-hot faulting thread anymore?) or late filing; next brief's first `ls` confirms I17; no brief unless a later probe shows action-taken |

## Receipt paths

- `local/research/I17/REPORT.md` (this file)
- `local/research/I17/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I16's)
- `local/research/I17/logs/worktree-add.log` (transcribed, labeled), `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I17/logs/ipad-details.json` (via DIRECT `--json-output <path>` — worked again, 15415 B), `processes-pre.log`, `entitlements.plist`
- `local/research/I17/logs/install.log` (overwrite, exit 0, 68 s)
- `local/research/I17/logs/elf-device-path.txt`
- `local/research/I17/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I17/logs/crashlog-check.log` (transcribed, labeled; 5 files after sleep + re-`ls` AND post-terminate re-`ls`: all priors', no new `.ips`, no late I16 filing), `screenshot.log`
- `local/research/I17/logs/i17-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i17.toml`, codegen log, full build log, details stdout copy); `W/codegen-output/` (9457 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `32d37e7`, clean, 8 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — all 8 commits stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black past the I16 wall with no successor wall; first presented content awaits gap 1's instrumentation.
- Prove post-entry execution by trace — no successor wall carries `0x2c5358` mid-trace (the I16 proof shape); the proof here is absence-of-park at the deterministic site + identical prefix + live guest (tabled, not over-claimed).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I17); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never observably reached file I/O (gap 4).
- Push the 8 local commits — the E-line is live with uncommitted work (gap 3; local commits only; the row convergence is tabled for the merge).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Root-cause the build-time delta (14m28s vs I16's 8m22s, same `-jobs 2`, fresh tree both briefs) — tabled, not root-caused.
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; silence-across-90 s determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4290 — the I16 bundle was running though I16 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.
- Explain why no `.ips` filed two briefs running — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); late filing vs under-threshold CPU is the next brief's first `ls`, not this brief's bar (gap 6).
- Observe E11/E12 card-tap output — 0 console lines from the taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar.

## TAIL RECEIPT

Report written in 5 chunks (header + contract + Task 1 dedupe; Task 1 diagnosis/codegen; Task 1 link + Task 2; Task 3 + commands; gaps + receipts + could-not-do). Pre-receipt measure: 341 lines, sha256 `95b86aa54d4bdb8bdb138585553a66f1f43c095078167df8664bec9a1f61f60b`.
Tail content line: "Observe E11/E12 card-tap output — 0 console lines from the taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar." This receipt line ends the report. END-I17-REPORT.
