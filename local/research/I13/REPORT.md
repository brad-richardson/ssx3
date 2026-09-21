# I13 — Close the 0x156750 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I12/REPORT.md` read first (all of it: base at `4acc59f` + cherry-picks + 1-line CSV entry closed `0x14f2a8` (count 0, guest strictly past it), guest reaches a STRICTLY LATER wall: indirect JALR `0x14dd18 → 0x156750` (mid-function of emitted `sub_001565C8` `0x1565c8–0x1567b8`, head after `jr $ra` @`0x156744`/ds/`nop`, tail `jr $ra` @`0x1567b0`/ds, observed bounds `0x156750–0x1567b8`, caller `jalr $v1` @`0x14dd18` with pointer-loaded target, 0 register refs — the neighbor-file mention is fall-through emission, not an edge); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I12; the I12 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start (overwrite target; state tabled in Task 2).
- BASE MOVE (E-lane advanced during I12): separate fork worktree at `fork/ssx3` HEAD `be0c9ee` (`[E9] Drop the unimplemented SIF command handler selector`, 1-line TOML stub deletion — tabled below) + cherry-picked I12 wiring+map (4 commits, patches byte-identical to I12's) + ONE local map commit `6166d1a` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane owner: frontier s27, E9 landed; shared-clone `ssx3` at `be0c9ee` with the same uncommitted `register_functions.cpp` replacement — read-only peeked, never touched).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9450 SSX3 sources from host `ps2_recomp` codegen, +1 vs I12) on the E9 runtime.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i13/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I13/` standalone, `[I13]` commit, no push.
- Outcome shape: I12 wall GONE — `0x156750` count 0 on probe, guest executes past it (entry `sub_00156750_0x156750` in slice + table slot 88530) and reaches a STRICTLY LATER wall: indirect JALR `0x317054 → 0x243a80`, same gap class (mid-function entry, computed `jalr $v1`, 0 table refs). No crash; one `cpu_resource` spin report (action none). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i13/`, `WT` = `W/fork-wt` (fork worktree), `W12` = `/Volumes/Extreme SSD/ps2x-i12/`, `C` = `W/codegen-output/` (host codegen), `C12` = `W12/codegen-output/`, `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x156750` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I12's wall — the `0x14dd18 → 0x156750` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x156750` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I12 |
| Alternatives | H-a `0x156750` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x156750` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~50 min wall: worktree → codegen 1m57s → build 27m01s → install 69s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT 344M | `du -sh W` after evidence step |
| Evidence `local/research/I13/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i13-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 5 local commits (4 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 1m57s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + worktree + cherry-picks (BASE MOVE — E-lane advanced)

| Item | Receipt |
|---|---|
| Pin (BASE MOVED `4acc59f` → `be0c9ee`) | `be0c9ee` = `be0c9eeaa337d9685e9536fa4f66c5ce5029aad8`, 2026-09-21 02:38 -0400, `[E9] Drop the unimplemented SIF command handler selector` |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `be0c9ee` (E-lane landed E9 during I12, as briefed) |
| Base delta (exact) | `git diff 4acc59f be0c9ee --stat` = 1 file, 1 deletion: `games/ssx3/ssx3.toml` line `-  "_sceSifCmdIntrHdlr@0x00426230",` from the `stubs` list. Recompiler/runtime/analyzer sources byte-identical by construction |
| E-lane owner | Frontier s27 (E9 landed); shared clone `ssx3` at `be0c9ee` with uncommitted `M ps2xRuntime/src/runner/register_functions.cpp` (398774 insertions — E-work in flight) — read-only `diff --stat` peek only |
| Worktree | `git -C FORK worktree add --detach W/fork-wt be0c9ee` → `HEAD is now at be0c9ee` (exit 0; `logs/worktree-add.log`; `._pack-*.idx` noise lines cosmetic, owner's tree) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry**: `55ffa6e` = `7975073` (Info.plist CFBundleName), `af7335a` = `ccefefe` (22-insertion CMake wiring), `27eef02` = `5f10c7d` (I11 CSV row), `ad34376` = `c8d08e6` (I12 CSV row); all 4 ported patches byte-identical to I12's originals (`diff` of `show --patch` clean); attempt 1 applied 3/4 then aborted on a transient dirty-tree complaint (tree verified clean, no sequencer residue); attempt 2 applied the 4th cleanly; `logs/cherry-pick.log` |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / worktree list / status / diff --stat / show`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | YES (required — E-lane advanced) — E9 runtime + I11 row + I12 row + new entry fix; recompiler byte-identical by construction so the tool binary is reused, not rebuilt |

### TOML-delta effect on codegen inputs (brief NOTE resolved by measurement, not assumption)

| # | Receipt | Finding |
|---|---|---|
| 1 | `be0c9ee` deletes `"_sceSifCmdIntrHdlr@0x00426230"` from TOML `stubs` | Codegen-input delta vs I12 is exactly: CSV +1 row (`0x156750`) AND stubs −1 (`0x426230`). The brief's "CSV map, not the selector set" does NOT hold — the stubs list selects per-address emission mode |
| 2 | CSV has NO row starting at `0x426230` (`sub_004261F0,0x4261f0,0x426358` container covers it); C12 emitted stub file `sub_00426230_0x426230.cpp` (358 B, calls `ps2_stubs::sceSifCmdIntrHdlr`) with 0 register refs (slot 825482 → container) and declarations in BOTH headers | In I12 the stub file was dead code: compiled in, never dispatched (slot served translated container code) |
| 3 | I13 codegen emits the SAME path as TRANSLATED guest code (21726 B, `Address: 0x426230 - 0x426358`, switch/case resume machine); slot 825482 → `sub_00426230_0x426230`; stubs.h −1 decl; +1 control-flow warning (`promoted 74 fallback entries`, ×2 lines) | The TOML entry controlled EMISSION MODE (stub-call vs translated), not file existence. E9's intent ("preserve translated guest code at `0x426230`") is realized: slot now serves the translated function |
| 4 | Functions.h diff I12→I13 is +1 line ONLY (the new `0x156750` decl) — `sub_00426230` was already declared there in I12 | Net header delta: functions.h +1, stubs.h −1 |
| 5 | Decision | **No codegen-input surprise**: TOML delta effect fully characterized (1 file mode-flipped, 1 slot re-homed, warning +2). Tool reuse stands (recompiler identical; stubs list is input data read generically) |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read (new WT, post-port): line 1021 `sub_001565C8,0x1565c8,0x1567b8`, line 1022 `sub_001567B8,0x1567b8,0x156810`; no row starts in `0x1566xx–0x1567ax` | No function in the gap range; new row overlaps the container (toolchain-tolerated per I11/I12 receipts) |
| 2 | C12 emitted `sub_001565C8_0x1565c8.cpp` RE-READ: `jr $ra` @`0x156744` (ds `0x156748` `sw`), nop `0x15674c`, then `0x156750: lw $v1,-0x1F3C($gp)` head; tail `jr $ra` @`0x1567b0` (ds `0x1567b4` `sw`), then `ctx->pc = 0x1567B8u; }` (function ends exactly at container end) | `0x156750` is a genuine function head with observed bounds `0x156750–0x1567b8` (`0x68` = 104 B, end-exclusive at the next CSV row start — same convention as I12's row). I12's observed row VERIFIED byte-for-byte |
| 3 | Caller emission `sub_0014DC80`: `0x14dd14: lw $v1,0x24($v0)` then `0x14dd18: jalr $v1` (I12 receipt, same slice) | Call target is runtime-computed (pointer load) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: direct-edge-only resume discovery (I11/I12 receipt; recompiler sources identical across the base move, so the receipt carries) | It CANNOT learn `0x156750` (0 direct edges: no `case 0x156750`, 0 register refs, no `*0x156750*` file in C12) |
| 5 | `function_table_emitter.cpp` first-wins dedupe + `lookupFunction` null-slot → `missing-target` park (I11 receipt, carries) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry |
| 6 | Merge safety: ELF stripped (I11 receipt, same ELF `1b49d05c…`); authoritative CSV rows ≥`0x3ff088` (I11 receipt, carries — this CSV is I12's +1 auto-named row below that floor) | New auto-named row at `0x156750` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 1022: `sub_00156750,0x156750,0x1567b8,0x68` (inserted in sorted position; `sub_001565C8` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — tail has no SIMD/loops, neighbors unlisted) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `6166d1a SSX3 map: add missing function entry 0x156750 (I13)` (1 file, 1 insertion); worktree `be0c9ee+55ffa6e+af7335a+27eef02+ad34376+6166d1a`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I12 base | `diff` old-CSV new-CSV = exactly the 1 added line; tracked toml = E9's (stub −1, tabled above) |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: base delta `4acc59f`→`be0c9ee` is TOML-only (recompiler identical by construction); toml = new tracked + 2 path edits (stubs −1 is input data, read generically); ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11/I12) |
| TOML | `W/ssx3-i13.toml` = E9 tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` = 2 lines; vs I12's TOML = 2 path edits + the E9 stub-line deletion |
| Exit / wall | exit 0, 1m57s (`Loaded 9278 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3712 `[warning]`s (+2, both the new `sub_00426230` control-flow warning — warning-set `diff` clean otherwise); 0 errors) |
| Recompiler report | (I12 → I13) discovered 9448→9449 (+1); recompiled 9270→9272 (+2: new entry + flipped `0x426230`); stubs 178→177 (−1); resumable entry points 401372→401446 (+74) across 7609→7610 owners (+1); fallback promotions 3710→3712 (+2, entries 739730→739878); unhandled 0→0 |
| Outputs | 9452 files: 9450 `.cpp` (9449 functions + `register_functions.cpp`), 2 headers; file-list `diff` C12→C = exactly +1 (`sub_00156750_0x156750.cpp` — stub path retained, mode-flipped) |
| `0x156750` census | NEW `sub_00156750_0x156750.cpp` 4888 B sha `aa6b35d8…` (head `0x156750 lw $v1,…`, `jr $ra` @`0x1567b0`→return tail); table slot `g_ps2RecompiledFunctionTable[88530] = sub_00156750_0x156750; // 0x156750` (exactly 1 slot — no resume re-homes; linear function) |
| `0x426230` census | Same path mode-flipped 358 B stub → 21726 B translated (`Address: 0x426230 - 0x426358`); register `diff` = exactly 2 hunks (slot 88530 added; slot 825482 re-homed container → translated); functions.h +1 / stubs.h −1 |
| Non-perturbation | `sub_00100008` SAME; `sub_001565C8` SAME (overlap changed nothing); `sub_0014F2A8` SAME; `sub_00395730` SAME; `ps2_recompiled_functions.h` +1 line only; `ps2_recompiled_stubs.h` −1 line only |
| Size/purge | 9.3G ExFAT; 9452 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I12)

| # | Item | I12 | I13 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9449 sources) | Same wiring, cherry-picked byte-identical (`af7335a` = `ccefefe`); 9450 sources | NO (count +1 only) |
| 2 | Base | `4acc59f+7975073+ccefefe+5f10c7d+c8d08e6` | `be0c9ee+55ffa6e+af7335a+27eef02+ad34376+6166d1a` (E9 runtime + I11 row + I12 row + new entry fix) | BASE MOVE (E-lane E9: TOML stub −1, tabled above); map +1 row |
| 3 | Toolchain/SDL2/raylib/flags | I12 §toolchain | Byte-identical toolchain (`diff` clean I9=I10=I11=I12=I13); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9452 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m05s (`PS2X: game objects: 9450 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full; 8 cosmetic `._pack-*.idx`/PhaseScript lines) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (in xcodebuild invocation line), 27m01s wall, 0 `error:` lines (`logs/ios-runtime-build-tail.log`; full 3357-line log on SSD). Slower than I12's 12m09s (same fresh-tree shape; wall variance, possibly E-lane contention — tabled as observed) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121208256 B / `f5f088fae6ec42f2d9bc76a6a705456ea253c0ae84c4039a34f8d5c0ba656d4a` (I12: 121191608 B — delta +16648 B = new function + stub→translated flip, not wiring) |
| lib | `libps2_game_objects.a`, 155314360 B (I12: 155299640 B, +14720 B), 297 members (296 unity objects + symdef — same count as I12) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0`, `sdk 27.0` |
| Table-populated proof | Entry `sub_00100008_0x100008` defined `T`; **9449** `T …_0x…` game text syms (I12: 9447, +2 = new `0x156750` entry + `0x426230` now referenced — I12's unreferenced stub was dead-stripped: 0 refs in the I12 slice, verified by re-`nm`); **`__Z21sub_00156750_0x156750…` defined `T`** (the gap entry is in the slice); I12's `sub_0014F2A8_0x14f2a8` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I12 (slice growth is game-only) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `55ffa6e` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 15G at this point (18G after staging) |
| Build breaks fixed | NONE — clean first try at the new base (wiring class + E9 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 build 24A437, UDID `P`, connected, developerMode enabled (`logs/ipad-details.json`).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 574-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4188 = the I12 build STILL RUNNING (same bundle UUID `431AAEF1-…` as I12's install; launcher unknown — I12 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 2nd brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4188 reaped BY the install itself; 4210 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I13 build + ISO; MF1/I8–I12 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/processes 60, install 1200, launch 90, files 60, screenshot 60, terminate 30, copy 120) |

### Provision + sign + install (I12 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I12 shape | I13 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 13.8s, ISO `cp` 49.9s; sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I12=I13) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (21.8s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (4× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 69s, clean replace** — new `installationURL …/8182D6A4-…/` (I12's was `431AAEF1-…`), live occupant PID 4188 reaped BY the install (0 `ps2` after). Fifth clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/8182D6A4-581B-4CD4-93EE-6F966F9AD129/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX loads from `cdrom0:`) |

### Launch (argv probe, ISO+env — I10/I11/I12 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive, PID 4210), 5280 lines, 77-line dedup (5203 DPI-spam lines) |
| I12 wall | **`0x156750` count = 0** (also `0x14dd18` 0, `0x14f2a8` 0, `0x14f660` 0, `0x395730` 0, `0x1567b0` 0) — the I12 wall is GONE |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (block lines 54–67, same position as I12); TEXTURE IDs 1–4; 12 IRX from `cdrom0:/data/modules/` (same 2 sets of 6, inside the 4 unhandled-RPC lines); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x317054 target=0x243a80 pc=0x243a80 … codeRegion=yes policy=1` (line 163; intact single line, no DPI tear) |
| RPC record | Same 4 unhandled sids as I12 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44` — normalized-dedup `diff` shows their lines byte-identical) |
| Crash-log record | Sleep + re-`ls`: **3 files** (I11's `…-015423.ips` + I12's `…-023911.ips` + NEW `ps2EntryRunner.cpu_resource-2026-09-21-032937.ips`, 12 KB) — new one fetched via `device copy from` (`logs/cpu-resource.ips`): `bug_type 202`, `Event: cpu usage`, `Action taken: none`, 96% CPU over 94 s, PID 4210 = our probe. Spin report, NOT a crash (no exception/termination; app alive at timeout) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i13-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content — same pixels as I12, new process state (past the I12 wall) |

### Past-the-wall table vs I12

| I12 fate | I13 fate | Wall status |
|---|---|---|
| `missing-target … source=0x14dd18 target=0x156750` (1×, line 147) | `0x156750` 0 refs anywhere in console (also `0x14dd18`/`0x14f2a8`/`0x395730` 0) | **I12 WALL GONE** |
| Faulting thread parks at `0x156750`; I12 console has 0 refs to `0x317054`/`0x243a80`/`0x2324f8`/`0x362cc8` — I12 never reached the later site | `0x14dd18 → 0x156750` JALR resolves to emitted `sub_00156750` (slot 88530); guest reaches a STRICTLY LATER wall `0x317054 → 0x243a80` (line 163) with a trace through regions I12 never emitted (`0x2324f8`, `0x362cc8`, `0x361f90`, `0x1dc930`, `0x3e6448`…) | **First post-entry code executes** (proven by reaching addresses I12 never reached, with identical event prefix) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical lines | Same boot phase, wall moved strictly later |
| 2 `.ips` (I11's + I12's own spin reports) | 1 NEW `cpu_resource` spin report (action none) + I11's/I12's retained | Same health (no crash); third spin report filed as gap 6 |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels, new state |

Event-prefix identity (the execution proof): normalized `diff` (PID/timestamp/UUID-stripped) of the 77-line dedups shows ONLY environmental noise before the wall swap (plist mouse-support line position, one DPI-spam count, VC address + appearance-transition count + game-controller warning) — then the wall-line swap (I12's torn 147–148 pair gone, I13's intact line 163 present). K1 block lines 54–67 byte-identical; TEXTURE 1–4 identical; all 4 RPC lines identical; I12's wall has NO counterpart in I13 (events flow uninterrupted to the new wall).

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x243a80`) — same class as `0x156750`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x317054 target=0x243a80 pc=0x243a80 … codeRegion=yes policy=1` (exactly 1×, line 163; `ee:idle` 0 — scheduler keeps other threads; `ra=0x31705c` normal return slot) |
| 2 | The target is a coverage hole, not out of range | `0x243a80` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `*0x243a80*` file, no `case 0x243a80u` in any of 9450 files, CSV rows jump `sub_00243A40,0x243a40,0x243ab0` → `sub_00243AB0,0x243ab0,0x243b50` (no function starting in `0x243a4x–0x243aax`) |
| 3 | Precise shape: merged functions, same signature | Emitted `sub_00243A40` shows `jr $ra` @`0x243a74` (ds `0x243a78` `sw`), nop `0x243a7c`, then `0x243a80: lui $v0,0x47` + `addiu $sp,$sp,-0x10` frame setup heading the next function; that function runs to `jr $ra` @`0x243aa8` (ds `0x243aac` `addiu $sp,$sp,0x10` epilogue) → observed bounds `0x243a80–0x243ab0` (`0x30`, end-exclusive at the next CSV row start) |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_00316F00` (CSV row 5893 `sub_00316F00,0x316f00,0x317328,0x428`): `0x317050: lw $v1,0xC($v0)` then `0x317054: jalr $v1` — vtable/record load (console `vtbl[c]=0x243a80`), same pointer-load shape as the `0x156750`/`0x14f2a8`/`0x395730` callers; direct-edge-only resume discovery can never learn it. (The `0x243a80` mention inside `sub_00242EB8_0x242eb8.cpp` is overlapping linear fall-through emission — file header `Address: 0x242eb8 - 0x244240` — not a direct edge: no `case`, no slot, no `dispatchGuestBranch`/`func_` reference anywhere.) |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_00243A80,0x243a80,0x243ab0,0x30` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9449 syms, 4 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I12 wall** (`0x156750` gone — JALR resolves, guest reaches strictly-later addresses I12 never emitted); **H-b overall** (new wall strictly past the target at `0x243a80` + the same 4 unhandled RPC sids + 1 new cpu spin report). The ONE next action: **fork-code brief — close the `0x243a80` indirect-target gap the same way** (add the CSV function entry — observed row `sub_00243A80,0x243a80,0x243ab0,0x30`, next brief re-verifies bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane = frontier s27, E9 landed; shared clone read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i13"
git -C "$FORK" ls-remote fork ssx3          # be0c9ee (E-lane ADVANCED past I12's base)
git -C "$FORK" log --oneline -5             # be0c9ee [E9] ... (._pack-*.idx noise lines cosmetic)
git -C "$FORK" worktree list                # shared ssx3 @be0c9ee + i8/i9/i10/i11/i12 WTs
git -C "$FORK" status --short               # M ps2xRuntime/src/runner/register_functions.cpp (E-lane uncommitted, 398774 insertions)
git -C "$FORK" diff --stat                  # read-only peek only
git -C "$FORK" show be0c9ee                 # 1-line TOML stubs deletion (_sceSifCmdIntrHdlr@0x00426230)
git -C "$FORK" diff 4acc59f be0c9ee --stat  # 1 file (TOML only)
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I13/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" be0c9ee
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i13" -c user.email="i13@local" cherry-pick 7975073 ccefefe 5f10c7d c8d08e6  # 3/4, transient abort on 4th
git -C "$WT" -c user.name="muse-i13" -c user.email="i13@local" cherry-pick c8d08e6  # retry clean: 55ffa6e, af7335a, 27eef02, ad34376 (patches byte-identical)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -n "001565C8\|001567B8\|00156750" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: container row only
grep -n "0x15674\|0x15675\|0x1567b" /Volumes/Extreme\ SSD/ps2x-i12/codegen-output/sub_001565C8_0x1565c8.cpp  # head/tail bounds
sed -n '660,700p' /Volumes/Extreme\ SSD/ps2x-i12/codegen-output/sub_001565C8_0x1565c8.cpp  # tail: jr/ds, ends at 0x1567b8
sed -n '9162,9168p' "$WT/games/ssx3/ssx3-functions.sweep.csv"    # 0x426230 container coverage
grep -n "0x426230" /Volumes/Extreme\ SSD/ps2x-i12/codegen-output/register_functions.cpp  # slot -> container
grep -c "sub_00426230_0x426230" /Volumes/Extreme\ SSD/ps2x-i12/codegen-output/register_functions.cpp  # 0 (dead stub)
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_00156750,0x156750,0x1567b8,0x68 after line 1021 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i13" -c user.email="i13@local" commit -m "SSX3 map: add missing function entry 0x156750 (I13)"  # 6166d1a
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i13.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i13.toml"  # exit 0, 1m57s
ls "$W/codegen-output" | wc -l                                       # 9452 (9450 cpp + 2 h)
grep -n "0x156750" "$W/codegen-output/register_functions.cpp"        # slot 88530 (exactly 1)
diff /Volumes/Extreme\ SSD/ps2x-i12/codegen-output/register_functions.cpp "$W/codegen-output/register_functions.cpp"  # 2 hunks
find "$W/codegen-output" -name "._*" -delete                        # 9452 -> 0
# --- Task 1d: device configure + build (I12 shape + new base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I12=I13
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m05s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 27m01s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # f5f088fa...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9449 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*156750_0x156750"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details.json"
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 574 lines, PID 4188 = I12 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (I12-identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (21.8s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 69s
B="/private/var/containers/Bundle/Application/8182D6A4-581B-4CD4-93EE-6F966F9AD129/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive), 5280 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i13 -s ps2EntryRunner --no-recurse  # 3 files (I11's + I12's + new)
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type systemCrashLogs \
  --domain-identifier ps2x-i13 --source "ps2EntryRunner.cpu_resource-2026-09-21-032937.ips" \
  --destination "$W/logs/cpu-resource.ips"                        # fetched: bug_type 202, action none
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i13-shot1.png
mv /tmp/i13-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4210  # cleanup only
# --- Task 3: new-wall diagnosis reads ---
grep -n "00243" "$WT/games/ssx3/ssx3-functions.sweep.csv" | head -12  # tiling: rows jump 0x243a40 -> 0x243ab0
grep -c "0x243a80" "$W/codegen-output/register_functions.cpp"        # 0 refs
grep -n "0x243a7\|0x243a8\|0x243aa\|0x243ab" "$W/codegen-output/sub_00243A40_0x243a40.cpp"  # jr/ds/nop/head shape
sed -n '150,185p' "$W/codegen-output/sub_00243A40_0x243a40.cpp"      # tail: jr @0x243aa8/ds, ends 0x243ab0
grep -n "0x317050\|0x317054" "$W/codegen-output/sub_00316F00_0x316f00.cpp"  # caller: lw + jalr $v1
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x243a80` has no table entry (mid-function of emitted `sub_00243A40` `0x243a40–0x243ab0`; head after `jr $ra` @`0x243a74`/ds/`nop` + frame setup; tail `jr $ra` @`0x243aa8`/ds epilogue; caller `jalr $v1` @`0x317054` with vtable-loaded target; 0 register refs; neighbor-file mention is fall-through emission, not an edge) | `kind=IndirectCall op=JALR source=0x317054 target=0x243a80` (1×, line 163) + emission census (Task 3) | Fork-code brief: add the `0x243a80` entry (observed row `sub_00243A80,0x243a80,0x243ab0,0x30` — re-verify `jr $ra` @`0x243aa8`/ds bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10/I11/I12) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `55ffa6e` + `af7335a` + `27eef02` + `ad34376` + `6166d1a` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `6166d1a^… = be0c9ee`, 0 pushes; remote `ssx3` at `be0c9ee` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I12 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | Third `.ips`: `cpu_resource` spin report (96% CPU, action none, PID 4210) | `logs/cpu-resource.ips` (bug_type 202, fetched from device) | Informational — no brief unless a later probe shows action-taken or the spin persists past wall fixes |

## Receipt paths

- `local/research/I13/REPORT.md` (this file)
- `local/research/I13/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I10's/I11's/I12's)
- `local/research/I13/logs/worktree-add.log`, `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I13/logs/ipad-details.json`, `processes-pre.log`, `entitlements.plist`
- `local/research/I13/logs/install.log` (overwrite, exit 0, 69 s)
- `local/research/I13/logs/elf-device-path.txt`
- `local/research/I13/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I13/logs/crashlog-check.log` (3 files after sleep + re-`ls`: I11's + I12's + new), `cpu-resource.ips` (fetched, bug_type 202, PID 4210)
- `local/research/I13/logs/i13-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i13.toml`, codegen log, full build log, details stdout); `W/codegen-output/` (9452 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `6166d1a`, clean, 5 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — `55ffa6e`/`af7335a`/`27eef02`/`ad34376`/`6166d1a` stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I12); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 5 local commits — the E-line is live with uncommitted work (gap 3; local commits only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4188 — the I12 bundle was running though I12 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.

## TAIL RECEIPT

Report written in 4 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link; Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 336 lines, sha256 `d5841cc29285b7843e3eb7c7860c0fa45d134f3a9334893fb81c5b6ff2e69317`.
Tail content line: "Name the launcher of pre-install PID 4188 — the I12 bundle was running though I12 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation." This receipt line ends the report. END-I13-REPORT.
