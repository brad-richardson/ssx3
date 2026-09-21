# I16 — Close the 0x2c5300 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I15/REPORT.md` read first (all of it: base moved to `ffdf58c` + 6 ports + 1-line CSV entry closed `0x3a0158` (count 0, guest strictly past it), guest reaches a STRICTLY LATER wall: indirect JALR `0x242150 → 0x2c5300` (mid-function of emitted `sub_002C52D8` `0x2c52d8–0x2c5320`, head after `jr $ra` @`0x2c52f4`/ds `0x2c52f8`/nop @`0x2c52fc`, tail `jr $ra` @`0x2c5318` → return, ends `0x2c5320`, observed bounds `0x2c5300–0x2c5320`, caller `jalr $v0` @`0x242150` with table-loaded target — `$v0` delta vs priors' `$v1`, 0 register refs/case/file; gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I15; the I15 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4262, same bundle UUID as I15's install — relaunched after I15's cleanup by an unknown launcher; state tabled in Task 2).
- BASE: STAYED `ffdf58c` (E-lane has NOT advanced past I15's base; `ls-remote` confirms; no E12 commit exists anywhere — case (b)) — separate fork worktree at `ffdf58c` + ported I15 wiring+map (7 commits, patches content-identical to I15's) + ONE local map commit `b07f738` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane live: shared `ssx3` at `ffdf58c` with uncommitted E-work still in flight — recon peek showed only `register_functions.cpp`; end-of-brief peek shows 4 modified files + 1 untracked, INCLUDING the byte-identical `0x2c5300` row uncommitted in their tree — independent convergence, tabled in Task 1).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9454 SSX3 sources from host `ps2_recomp` codegen, +1 vs I15: our `0x2c5300`) on the E9 runtime + E11 read-only card-query taps.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i16/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging + evidence; evidence `local/research/I16/` standalone, `[I16]` commit, no push.
- Outcome shape: I15 wall GONE — `0x2c5300` executes in-trace (entry `sub_002C5300_0x2c5300` + table slot 464062; trace runs `0x2420c8 → 0x3e6448 → 0x2c5300 → 0x2c67a8 → …` past I15's trace end) and reaches a STRICTLY LATER wall: indirect JALR `0x2d3828 → 0x2c5358`, same gap class (mid-function entry, computed `jalr $v0`, 0 table refs). No crash; no NEW `.ips` (delta vs I11–I15: 5 files, all priors'). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i16/`, `WT` = `W/fork-wt` (fork worktree), `W15` = `/Volumes/Extreme SSD/ps2x-i15/`, `C` = `W/codegen-output/` (host codegen), `C15` = `W15/codegen-output/`, `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x2c5300` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I15's wall — the `0x242150 → 0x2c5300` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x2c5300` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I15 |
| Alternatives | H-a `0x2c5300` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x2c5300` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~100 min wall: worktree+ports → codegen 3m33s → configure 1m17s → build 8m22s → install 72s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT ~350M | `du -sh W` after evidence step |
| Evidence `local/research/I16/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i16-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 8 local commits (7 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 3m33s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + E12 check + worktree + cherry-picks (BASE STAYED — case (b))

| Item | Receipt |
|---|---|
| Pin (STAYED) | `ffdf58c` = `ffdf58c4ee3b95bc6dd8779a0baeed0b23afe19b` (same base as I15) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `ffdf58c` at recon AND at end-of-brief (E-lane has NOT advanced past I15's base) |
| E12 check at HEAD (BEFORE writing) | CSV at `ffdf58c`: rows jump `sub_002C52D8,0x2c52d8,0x2c5320` → `sub_002C5320,…` (`,0x2c5300,` count 0); `log --all --grep=E12` empty; `log --all --grep=2c5300` empty; no E12 branch/ref — **case (b): no E12 row to port** |
| E-lane owner | Live — recon peek: shared `ssx3` @`ffdf58c` with uncommitted `M register_functions.cpp` only (398969 insertions, same as I15's peek); end-of-brief peek: 4 modified (`register_functions.cpp` + CSV +1 + `ps2_e7.h` + `ps2_runtime.cpp`) + 1 untracked (`ps2_log.txt`) — E-lane edited DURING this brief; remote unmoved |
| E12 convergence (read-only peek) | E-lane's uncommitted CSV hunk is the BYTE-IDENTICAL row `sub_002C5300,0x2c5300,0x2c5320,0x20` at the same sorted position — independent convergence, zero merge conflict on that line |
| Worktree | `git -C FORK worktree add --detach W/fork-wt ffdf58c` → `HEAD is now at ffdf58c` (exit 0; `._pack-*.idx` noise lines cosmetic, owner's tree) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry** (same shape as I15): `52ac12e` = `ab443f6` (Info.plist CFBundleName), `61f1c9b` = `c3a6df1` (22-insertion CMake wiring), `6268acf` = `a0f86bf` (I11 CSV row), `35bdef3` = `6fca9df` (I12 CSV row), `dcae122` = `bbd5ab2` (I13 CSV row), `1607382` = `ab830e4` (I14 CSV row), `3832a67` = `00e8433` (I15 CSV row); attempt 1 applied 3/7 then aborted on the transient dirty-tree complaint (tree verified clean); `--quit` exit 1 this brief (linked-worktree `.git` is a file, no `.git/sequencer` dir — I15 delta, tabled not root-caused; subsequent individual picks prove the sequencer resolved); picks 4+5+6+7 applied individually exit 0; `logs/cherry-pick.log` |
| Patch identity | All 7 ports content-identical to I15's (`diff` of `^[+-][^+-]` lines clean for each pair; same base so same offsets) |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / show / status / diff --stat / diff <csv>`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | NO — `ffdf58c` + I8 plist + I10 wiring + I11 row + I12 row + I13 row + I14 row + I15 row + new entry fix; tool binary reused, not rebuilt (same base as I15) |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read (new WT, post-port): line 5096 `sub_002C52D8,0x2c52d8,0x2c5320`, line 5097 `sub_002C5320,0x2c5320,0x2c5338`; no row starts in `0x2c52d9–0x2c531f` | No function in the gap range; new row overlaps the container (toolchain-tolerated per I11–I15 receipts) |
| 2 | C15 emitted `sub_002C52D8_0x2c52d8.cpp` RE-READ: `jr $ra` @`0x2c52f4`, ds `addiu $sp` @`0x2c52f8` emitted, nop `0x2c52fc`, then `0x2c5300: addiu $v0,$zero,0x14` + `0x2c5304: addiu $v1,…` heading the next function; that function is the LAST in the container, running to `jr $ra` @`0x2c5318` (ds `sltiu` @`0x2c531c`) → return then `ctx->pc = 0x2C5320u; }` (function ends exactly at container end) | `0x2c5300` is a genuine function head with observed bounds `0x2c5300–0x2c5320` (`0x20`, end-exclusive at the next CSV row start — same convention as I11–I15 rows). I15's observed row VERIFIED byte-for-byte |
| 3 | Caller emission `sub_002420C8`: `0x242144: lw $v1,0x0($a2)` then `0x24214c: lw $v0,0x184($v1)` then `0x242150: jalr $v0` (re-grepped in C15, same slice) | Call target is runtime-computed (pointer-table load via `$v0`) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: direct-edge-only resume discovery (I11–I15 receipt; recompiler sources identical — same base — so the receipt carries) | It CANNOT learn `0x2c5300` (0 direct edges: no `case 0x2c5300`, 0 register refs, no `*0x2c5300*` file in C15; the 2 container-file mentions are linear `ctx->pc` fall-through, not edges) |
| 5 | `function_table_emitter.cpp` first-wins dedupe + `lookupFunction` null-slot → `missing-target` park (I11 receipt, carries) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry |
| 6 | Merge safety: ELF stripped (I11 receipt, same ELF bytes `1b49d05c…` re-sha'd); authoritative CSV rows ≥`0x3ff088` (I11 receipt, carries — this CSV is I15's + 1 auto-named row, all below that floor) | New auto-named row at `0x2c5300` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 5097: `sub_002C5300,0x2c5300,0x2c5320,0x20` (inserted in sorted position; `sub_002C52D8` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — precise toml grep shows zero `0x2c5*` entries and the new tail (addiu/mult/addu/lw/xor/jr) has no SIMD/loops; the `0x2425c0`/`0x2429b0` SIMD entries are distant, not neighbors) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `b07f738 SSX3 map: add missing function entry 0x2c5300 (I16)` = `b07f73888f0dcc75b68efd4cddeab6ed45f6d93e` (1 file, 1 insertion); worktree `ffdf58c+52ac12e+61f1c9b+6268acf+35bdef3+dcae122+1607382+3832a67+b07f738`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I15 worktree CSV | `diff` = exactly 1 added line (our `0x2c5300` row); tracked toml byte-identical to I15's (no base-move change) |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: base UNCHANGED from I15 (`ffdf58c` — recompiler/analyzer byte-identical by construction); toml = tracked (byte-identical to I15's) + 2 path edits; ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11/I12/I13/I14/I15) |
| TOML | `W/ssx3-i16.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` vs tracked = 2 lines; vs I15's TOML = the same 2 path lines re-pointed i15→i16 |
| Exit / wall | exit 0, 3m33s (`Loaded 9282 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3712 `[warning]`s (SAME count; warning SET identical — sorted-`diff` clean); 0 errors) |
| Recompiler report | (I15 → I16) discovered 9452→9453 (+1); recompiled 9275→9276 (+1); stubs 177→177; resumable entry points 401448→401448 (+0) across 7612→7612 owners (+0 — the new straight-line function contributes 0 resumable entries); unhandled 0→0 |
| Outputs | 9456 files: 9454 `.cpp` (9453 functions + `register_functions.cpp`), 2 headers; file-list `diff` C15→C = exactly +1 (`sub_002C5300_0x2c5300.cpp`) |
| `0x2c5300` census | NEW `sub_002C5300_0x2c5300.cpp` 2358 B sha `7bede90b…` (head `0x2c5300 addiu $v0,…`, `jr $ra` @`0x2c5318`→return tail, `Address: 0x2c5300 - 0x2c5320`); table slot `g_ps2RecompiledFunctionTable[464062] = sub_002C5300_0x2c5300; // 0x2c5300` (exactly 1 slot — register `diff` is exactly the 1 added line; no resume re-homes) |
| Non-perturbation | `sub_00100008` SAME; `sub_002C52D8` SAME (overlap changed nothing); `sub_002420C8` SAME; `sub_002C50E0` SAME; `sub_00243A80`/`sub_00156750`/`sub_0014F2A8`/`sub_00395730`/`sub_003A0158`/`sub_003A0048` SAME; `ps2_recompiled_functions.h` +1 line only; `ps2_recompiled_stubs.h` IDENTICAL |
| Size/purge | 9.3G ExFAT; 9456 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I15)

| # | Item | I15 | I16 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9453 sources) | Same wiring, ported content-identical (`61f1c9b` = `c3a6df1`); 9454 sources | NO (count +1 only) |
| 2 | Base | `ffdf58c+ab443f6+c3a6df1+a0f86bf+6fca9df+bbd5ab2+ab830e4+00e8433` | `ffdf58c+52ac12e+61f1c9b+6268acf+35bdef3+dcae122+1607382+3832a67+b07f738` (E9 runtime + E11 card taps + I8 plist + I10 wiring + I11 row + I12 row + I13 row + I14 row + I15 row + new entry fix) | SAME base; map +1 row |
| 3 | Toolchain/SDL2/raylib/flags | I15 §toolchain | Byte-identical toolchain (`diff` clean I9=I15=I16); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1 re-verified via `--version`), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure (same count as I15) | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9456 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m17s (`PS2X: game objects: 9454 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full). Note: 4 `non-monotonic index ._pack-0f6f5c…idx` lines inside the log (cosmetic, exit 0; sidecar hash differs across briefs — owner's tree, tabled not root-caused) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (in xcodebuild invocation line + `Build task concurrency set to 2`), 8m22s wall, 0 `error:` lines (`logs/ios-runtime-build-tail.log` in evidence, full log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121225288 B / `3c43c3e0c71b0dd4561ea05d3167f0cbbf2a2503263dc9a40d7bb3cfa65fc90b` (I15: 121225168 B — delta +120 B = 1 new game function, not wiring) |
| lib | `libps2_game_objects.a`, 155326176 B (I15: 155326688 B, −512 B — unity-build variance, tabled as observed) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0` |
| Table-populated proof | **9453** `T …_0x…` game text syms (I15: 9452, +1 = new `0x2c5300` entry); **`__Z21sub_002C5300_0x2c5300…` defined `T`** (the gap entry is in the slice); I15's `sub_003A0158_0x3a0158` + I14's `sub_00243A80_0x243a80` + I13's `sub_00156750_0x156750` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I15 (slice growth is game-only) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `52ac12e` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 18G after staging (same shape as I15) |
| Build breaks fixed | NONE — clean first try at the same base (wiring class + E9/E11 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), UDID `P`, connected, developerMode enabled (`logs/ipad-details.json` — captured via DIRECT `--json-output <SSD path>`: WORKED again this brief, 15415 B, exit 0 — I15's recovery holds, no longer a delta).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install — no `Locked` failure |
| Running processes | 577-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4262 = the I15 build STILL RUNNING (same bundle UUID `97479F48-…` as I15's install; relaunched after I15's cleanup by an unknown launcher — I15 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 5th brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4262 reaped BY the install itself; 4282 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I16 build + ISO; MF1/I8–I15 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/lock/processes/details/files/screenshot 60, install 1200, launch 90, terminate 30) |

### Provision + sign + install (I15 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I15 shape | I16 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 1.3s, ISO `cp` 19.5s; sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I15=I16) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (13.4s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (7× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 72s, clean replace** — new `installationURL …/736F005D-…/` (I15's was `97479F48-…`), live occupant PID 4262 reaped BY the install (0 `ps2` after). Eighth clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/736F005D-CFDA-4C6E-ADFF-FC70C512B215/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX modules in `loadedModules` lists — 24 occurrences, multiset identical to I15's) |

### Launch (argv probe, ISO+env — I10–I15 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive, PID 4282), 5199 lines, 77-line dedup (5122 DPI-spam lines, NO inline DPI suffix on the wall line this brief — the head is complete in-line) |
| I15 wall | **`0x2c5300` executes in-trace** (1 ref, mid-trace with successors — NOT a park); `0x242150` 0, `0x3a0158` 0, `0x39cd74` 0, `0x243a80` 0, `0x156750` 0, `0x14f2a8` 0, `0x395730` 0 — the I15 wall is GONE (`0x2c5140`: 1 ref, inside the new wall's trace) |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (14 lines, byte-identical positions modulo the mouse-plist timing move); TEXTURE IDs 1–4 (5 lines, byte-identical); 12 IRX modules (24 occurrences across the RPC `loadedModules` lists, multiset identical to I15's); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown; E11 card taps: 0 console lines (taps share E7's ordered sink, not the console — observed) |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x2d3828 target=0x2c5358 pc=0x2c5358 … codeRegion=yes policy=1` (raw line 192, COMPLETE 1330-byte line: all scalar fields intact, full trace to `… → 0x2d3810`, `\r`-terminated — no DPI tear this brief; line 193 is a plain DPI line) |
| RPC record | Same 4 unhandled sids as I15 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44` — dedup lines byte-identical to I15's) |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11's `…-015423.ips` + I12's `…-023911.ips` + I13's `…-032937.ips` + I14's `…-040134.ips` + I15's `…-050020.ips`) — **NO new `.ips` for I16** (delta vs I11–I15, each of which filed one spin report; tabled, not root-caused — possible late filing or under-threshold CPU) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i16-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content — sha differs from I15's (clock 6:03 AM + wallpaper phase), content same black, new process state (past the I15 wall) |

### Past-the-wall table vs I15

| I15 fate | I16 fate | Wall status |
|---|---|---|
| `missing-target … source=0x242150 target=0x2c5300` (1×, line 191 torn head + line 192 continuation); `0x2c5300` 1 ref total (as unexecuted `target=`); trace ENDS `… → 0x2420c8 → 0x3e6448` | `0x242150` 0 refs anywhere; `0x2c5300` 1 ref MID-TRACE with successors (`… → 0x2420c8 → 0x3e6448 → 0x2c5300 → 0x2c67a8 → …`); guest parks at a STRICTLY LATER wall `0x2d3828 → 0x2c5358` (line 192) | **I15 WALL GONE** |
| Faulting thread parks at `0x2c5300`; I15 console has 0 refs to `0x2d3828`/`0x2c5358`/`0x2d3810`/`0x2c67a8` (only `0x3e6448` 2× — a shared subroutine mid-trace in BOTH briefs) — I15 never reached the later site | `0x242150 → 0x2c5300` JALR resolves to emitted `sub_002C5300` (slot 464062); guest executes through it and ~50 further trace entries I15 never reached, with identical event prefix; single probe | **First post-entry code executes** (proven by executing the entry I15 parked at and reaching addresses I15 never reached, with identical event prefix; single probe) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical lines | Same boot phase, wall moved strictly later |
| 5 `.ips` (I11's + I12's + I13's + I14's + I15's own spin reports) | NO new `.ips` (5 files, all priors') | Healthier-or-equal (no crash; no spin report filed this brief) |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels (new capture), new state |

Event-prefix identity (the execution proof): normalized `diff` (timestamp/PID/UUID-stripped) of the 77-line dedups shows ONLY environmental noise before the wall swap (mouse-support plist line timing move 43→4, ASLR pointer in appearance-transition lines) — then the wall-fragment swap at dedup line 76 (I15's torn continuation fragment `-> 0x23fb20 → … → 0x2c5140 → …` gone, I16's COMPLETE new wall head `source=0x2d3828 target=0x2c5358 … trace=0x2c51d0 → … → 0x2d3810`). K1 block byte-identical; TEXTURE 1–4 identical; all 4 RPC lines identical; handshake identical; I15's wall has NO counterpart in I16 (events flow uninterrupted to the new wall). Note: I16's wall head (raw line 192) has NO inline DPI suffix, so it is INCLUDED in the dedup (delta vs I15, whose torn head was excluded) — the head with all intact scalar fields plus the full trace is preserved at raw line 192 of the complete console log.

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x2c5358`) — same class as `0x2c5300`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x2d3828 target=0x2c5358 pc=0x2c5358 … codeRegion=yes policy=1` (exactly 1×, raw line 192 complete; `ee:idle` 0 — scheduler keeps other threads; `ra=0x2d3830` normal return slot; `v0=0x2c5358` carries the computed target) |
| 2 | The target is a coverage hole, not out of range | `0x2c5358` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `case 0x2c5358u` in any of 9454 files, no `*0x2c5358*` file, 0 `func_2C5358` refs, 0 `dispatchGuestBranch…0x2c5358` refs; CSV rows jump `sub_002C5338,0x2c5338,0x2c53b0` → `sub_002C53B0,…` (no function starting in `0x2c5339–0x2c53af`) |
| 3 | Precise shape: merged functions, same signature (DELTA: internal control flow) | Emitted `sub_002C5338` shows `jr $ra` @`0x2c534c` (ds `addiu $sp` @`0x2c5350` emitted), nop `0x2c5354`, then `0x2c5358: addiu $v0,$zero,0x14` heading the next function; that function runs through internal branches (`beq` @`0x2c536c`/`0x2c5374`/`0x2c537c`, `b` @`0x2c5384`, `bgtz` @`0x2c538c`, `bnez` @`0x2c5398`) to `jr $ra` @`0x2c53a0` → return and `jr $ra` @`0x2c53a8` → return, then `ctx->pc = 0x2C53B0u; }` (function ends exactly at container end) → observed bounds `0x2c5358–0x2c53b0` (`0x58`, end-exclusive at the next CSV row start). The 2 file mentions (`sub_002C5338` own container + `sub_002C5320` overrun emission past its CSV end through `0x2c53c8`) are linear `ctx->pc` fall-through, NOT direct edges |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_002D2988` (CSV row 5276 `sub_002D2988,0x2d2988,0x2d4060,0x16d8`): `0x2d3818: lw $v1,0x0($a0)` then `0x2d3820: lh $a2,0x1A0($v1)` then `0x2d3824: lw $v0,0x1A4($v1)` then `0x2d3828: jalr $v0` (ds `addu` @`0x2d382c`) — record+offset table load via `$v0` (same `$v0` shape as I15's caller); direct-edge-only resume discovery can never learn it. (The caller itself executes via resume slot `[478728] // 0x2d3828` → `sub_002D2988_0x2d2988`, trace tail `… → 0x2d3810`.) |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_002C5358,0x2c5358,0x2c53b0,0x58` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9453 syms, 7 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I15 wall** (`0x2c5300` executes — JALR resolves, guest runs through the entry I15 parked at and reaches strictly-later addresses I15 never reached); **H-b overall** (new wall strictly past the target at `0x2c5358` + the same 4 unhandled RPC sids + NO new `.ips`). The ONE next action: **fork-code brief — close the `0x2c5358` indirect-target gap the same way** (add the CSV function entry — observed row `sub_002C5358,0x2c5358,0x2c53b0,0x58`, next brief re-verifies the `jr $ra` @`0x2c53a0`/`0x2c53a8` bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i16"
git -C "$FORK" ls-remote fork ssx3          # ffdf58c (E-lane has NOT advanced past I15's base)
git -C "$FORK" log --oneline -8             # ffdf58c at top (non-monotonic noise filtered)
git -C "$FORK" status --short               # M register_functions.cpp only at recon
git -C "$FORK" worktree list                # 14 entries incl. W15/fork-wt @00e8433
git -C "$FORK" show ffdf58c:games/ssx3/ssx3-functions.sweep.csv | grep -c ",0x2c5300,"  # 0 -> case (b)
git -C "$FORK" log --all --oneline --grep="E12"        # empty (no E12 commit anywhere)
git -C "$FORK" log --all --oneline --grep="2c5300"     # empty
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks (case b: port I15's 7) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I16/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" ffdf58c
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" cherry-pick ab443f6 c3a6df1 a0f86bf 6fca9df bbd5ab2 ab830e4 00e8433  # 3/7, transient abort on 4th
git -C "$WT" cherry-pick --quit   # exit 1 this brief (linked-worktree .git is a file; picks below prove resolution)
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" cherry-pick 6fca9df  # retry clean -> 35bdef3
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" cherry-pick bbd5ab2  # retry clean -> dcae122
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" cherry-pick ab830e4  # retry clean -> 1607382
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" cherry-pick 00e8433  # retry clean -> 3832a67
# 52ac12e, 61f1c9b, 6268acf, 35bdef3, dcae122, 1607382, 3832a67 (content-identical to I15's)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -n "002C5\|002C4F\|002C53" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: container row only
grep -n "0x2c52f\|0x2c530" /Volumes/Extreme\ SSD/ps2x-i15/codegen-output/sub_002C52D8_0x2c52d8.cpp  # jr/ds/nop/head
sed -n "96,120p" /Volumes/Extreme\ SSD/ps2x-i15/codegen-output/sub_002C52D8_0x2c52d8.cpp  # tail: jr @0x2c5318, ends 0x2c5320
grep -n "0x242144\|0x24214c\|0x242150" /Volumes/Extreme\ SSD/ps2x-i15/codegen-output/sub_002420C8_0x2420c8.cpp  # caller: lw+lw+jalr $v0
grep -c "0x2c5300" /Volumes/Extreme\ SSD/ps2x-i15/codegen-output/register_functions.cpp  # 0 refs
grep -n "0x2c5\|0X2C5\|002C5\|0x242\|00242" "$WT/games/ssx3/ssx3.toml"  # no 0x2c5 neighbors -> no toml change
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_002C5300,0x2c5300,0x2c5320,0x20 after line 5096 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i16" -c user.email="i16@local" commit -m "SSX3 map: add missing function entry 0x2c5300 (I16)"  # b07f738
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i16.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i16.toml"  # exit 0, 3m33s
ls "$W/codegen-output" | wc -l                                       # 9456 (9454 cpp + 2 h)
grep -n "0x2c5300" "$W/codegen-output/register_functions.cpp"  # slot 464062 (exactly 1)
diff /Volumes/Extreme\ SSD/ps2x-i15/codegen-output/register_functions.cpp "$W/codegen-output/register_functions.cpp"  # 1 added line
find "$W/codegen-output" -name "._*" -delete                        # 9456 -> 0
# --- Task 1d: device configure + build (I15 shape, same base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I15=I16
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m17s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 8m22s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 3c43c3e0...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9453 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*2C5300_0x2c5300"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details-direct.json"  # WORKED again (15415 B)
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 577 lines, PID 4262 = I15 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (13.4s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 72s
B="/private/var/containers/Bundle/Application/736F005D-CFDA-4C6E-ADFF-FC70C512B215/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive, PID 4282), 5199 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i16 -s ps2EntryRunner --no-recurse  # 5 files, all priors
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i16 -s ps2EntryRunner --no-recurse  # still 5 (no new .ips)
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i16-shot1.png
mv /tmp/i16-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4282  # cleanup only
# --- Task 3: new-wall diagnosis reads ---
grep -n "002C53\|002C54" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: rows jump 0x2c5338 -> 0x2c53b0
grep -c "0x2c5358" "$W/codegen-output/register_functions.cpp"        # 0 refs
grep -n "0x2c5348\|0x2c534c\|0x2c5350\|0x2c5354\|0x2c5358" "$W/codegen-output/sub_002C5338_0x2c5338.cpp"  # jr/ds/nop/head
sed -n '180,220p' "$W/codegen-output/sub_002C5338_0x2c5338.cpp"      # internal branches + jr @0x2c53a0/@0x2c53a8, ends 0x2c53b0
grep -n "0x2d3818\|0x2d3820\|0x2d3824\|0x2d3828" "$W/codegen-output/sub_002D2988_0x2d2988.cpp"  # caller: lw+lh+lw+jalr $v0
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x2c5358` has no table entry (mid-function of emitted `sub_002C5338` `0x2c5338–0x2c53b0`; head after `jr $ra` @`0x2c534c`/ds `0x2c5350`/nop @`0x2c5354`; internal branches + tail `jr $ra` @`0x2c53a0`/`0x2c53a8` → return, ends `0x2c53b0`; caller `jalr $v0` @`0x2d3828` with record+offset table load — same `$v0` shape as I15's caller; 0 register refs/case/file/func_/dispatch; the 2 file mentions are fall-through emission + neighbor overrun, not edges) | `kind=IndirectCall op=JALR source=0x2d3828 target=0x2c5358` (1×, raw line 192 complete) + emission census (Task 3) | Fork-code brief: add the `0x2c5358` entry (observed row `sub_002C5358,0x2c5358,0x2c53b0,0x58` — re-verify `jr $ra` @`0x2c53a0`/`0x2c53a8` bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10–I15) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `52ac12e` + `61f1c9b` + `6268acf` + `35bdef3` + `dcae122` + `1607382` + `3832a67` + `b07f738` unpushed (E-lane mutating; shared clone has uncommitted E-work including the byte-identical `0x2c5300` row) | Worktree log `b07f738^… = ffdf58c`, 0 pushes; remote `ssx3` at `ffdf58c` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows (note: E12's in-flight row is byte-identical, so the `b07f738` hunk will merge clean) |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I15 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | NO new `.ips` this brief (5 files, all priors' — I11–I15 each filed one spin report) | `logs/crashlog-check.log` (post sleep + re-`ls` AND post-terminate re-`ls`: still 5) | Informational — possible late filing (next brief's first `ls` confirms) or under-threshold CPU; no brief unless a later probe shows action-taken |

## Receipt paths

- `local/research/I16/REPORT.md` (this file)
- `local/research/I16/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I15's)
- `local/research/I16/logs/worktree-add.log` (transcribed, labeled), `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I16/logs/ipad-details.json` (via DIRECT `--json-output <path>` — worked again, 15415 B), `processes-pre.log`, `entitlements.plist`
- `local/research/I16/logs/install.log` (overwrite, exit 0, 72 s)
- `local/research/I16/logs/elf-device-path.txt`
- `local/research/I16/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I16/logs/crashlog-check.log` (5 files after sleep + re-`ls` AND post-terminate re-`ls`: all priors', no new `.ips`), `screenshot.log`
- `local/research/I16/logs/i16-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i16.toml`, codegen log, full build log, details stdout copy); `W/codegen-output/` (9456 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `b07f738`, clean, 8 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — all 8 commits stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I16); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 8 local commits — the E-line is live with uncommitted work (gap 3; local commits only; the E12 row convergence is tabled for the merge).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4262 — the I15 bundle was running though I15 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.
- Explain why no `.ips` filed this brief — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); late filing vs under-threshold CPU is the next brief's first `ls`, not this brief's bar (gap 6).
- Explain why `cherry-pick --quit` exited 1 — linked-worktree `.git` is a file (no `.git/sequencer` dir); the subsequent individual picks prove the sequencer resolved; tabled, not root-caused.
- Observe E11 card-tap output — 0 console lines from the new taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar.

## TAIL RECEIPT

Report written in 4 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link + Task 2; Task 3 + commands; gaps + receipts + could-not-do). Pre-receipt measure: 334 lines, sha256 `27e2f6c238d72feeaf0619a00c4d2dd67fa0f972b9058811a77094bf9b7c5b28`.
Tail content line: "Observe E11 card-tap output — 0 console lines from the new taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar." This receipt line ends the report. END-I16-REPORT.
