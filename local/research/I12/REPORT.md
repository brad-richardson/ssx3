# I12 — Close the 0x14f2a8 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I11/REPORT.md` read first (all of it: base move to `4acc59f` + cherry-picks + 1-line CSV entry closed `0x395730` (count 0, 8 post-entry insns execute), guest reaches a STRICTLY LATER wall: indirect JALR `0x14f660 → 0x14f2a8` (mid-function of emitted `sub_0014F250` `0x14f250–0x14f418`, head after `jr $ra` @`0x14f29c`/ds/`nop`, observed bounds `0x14f2a8–0x14f35c`, caller `jalr $v1` @`0x14f660` with pointer-loaded target, 0 register refs); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0, UDID `P` — same device as I11; the I11 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start, a live occupant (PID 4165, I11 bundle) still running (overwrite against a live occupant).
- BASE (no move needed): separate fork worktree at `fork/ssx3` HEAD `4acc59f` — the E-lane did NOT advance past I11's base (`ls-remote` still `4acc59f`) — + cherry-picked I11 wiring+map (`7975073` plist, `ccefefe` CMake, `5f10c7d` I11 CSV row, patches byte-identical to I11's) + ONE local map commit `c8d08e6` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane owner: frontier s27 E7 per orchestrator memory; shared-clone `ssx3` at `4acc59f` with the same 398k-line uncommitted `register_functions.cpp` replacement — read-only peeked, never touched).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9449 SSX3 sources from host `ps2_recomp` codegen, +1 vs I11) on the E7 runtime.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i12/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutates; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I12/` standalone, `[I12]` commit, no push.
- Outcome shape: I11 wall GONE — `0x14f2a8` count 0 on probe, guest executes past it (entry `sub_0014F2A8_0x14f2a8` in slice + table slot 81064) and reaches a STRICTLY LATER wall: indirect JALR `0x14dd18 → 0x156750`, same gap class (mid-function entry, computed `jalr $v1`, 0 table refs). No crash; one `cpu_resource` spin report (action none). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i12/`, `WT` = `W/fork-wt` (fork worktree), `W11` = `/Volumes/Extreme SSD/ps2x-i11/`, `C` = `W/codegen-output/` (host codegen), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x14f2a8` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I11's wall — the `0x14f660 → 0x14f2a8` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x14f2a8` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I11 |
| Alternatives | H-a `0x14f2a8` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x14f2a8` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~1 h wall: worktree → codegen 2m40s → build 12m09s → install 68s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT 344M | `du -sh W` after evidence step |
| Evidence `local/research/I12/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i12-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutates | 1 file via named add, 4 local commits (3 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 2m40s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + worktree + cherry-picks

| Item | Receipt |
|---|---|
| Pin (NO BASE MOVE — E-lane static) | `4acc59f` = `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2`, 2026-09-21 00:58 -0400, `[E7] Feed CPU quadword VIF1 FIFO writes into the interpreter` — same base as I11 |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `4acc59f` (E-lane has NOT advanced past I11's base) |
| E-lane owner | Frontier s27 E7 per orchestrator memory; shared clone `ssx3` at `4acc59f` with uncommitted `M register_functions.cpp` (398779 lines, same E-work as I11 observed) — read-only `diff --stat` peek only |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 4acc59f` → `HEAD is now at 4acc59f` (exit 0; `logs/worktree-add.log`; `._*` pack-idx noise lines cosmetic) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean** (same base as I11, nothing to merge): `8fc0c14` = `7975073` (Info.plist CFBundleName), `89d1126` = `ccefefe` (22-insertion CMake wiring), `af0a508` = `5f10c7d` (I11 CSV row); all 3 ported patches byte-identical to I11's originals (`diff` of `show --patch` clean); no fetch needed (objects in shared store); `logs/cherry-pick.log` |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / worktree list / status / diff --stat`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | NO (none needed) — E-lane static at `4acc59f`; recompiler byte-identical by construction so the tool binary is reused, not rebuilt |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read: container row `sub_0014F250,0x14f250,0x14f418` line 872, next row `sub_0014F418` line 873; global tiling check 9276 rows, 2 overlaps (the `0x395730` I11 row + the `0x42c1f0` dup) | No function in `0x14f25x–0x14f2ax`; overlaps are toolchain-tolerated (dup emits 1 file + 1 slot, I11 receipt) |
| 2 | I11 emitted `sub_0014F250_0x14f250.cpp`: `jr $ra` @`0x14f29c` (ds `0x14f2a0`), nop `0x14f2a4`, then `0x14f2a8: lui $v0,0x53` head; second `jr $ra` @`0x14f354` (ds `0x14f358`), nop `0x14f35c`, next head @`0x14f360` | Two guest functions merged under one map entry; `0x14f2a8` is a genuine function head with observed bounds `0x14f2a8–0x14f35c` (`0xb4` = 180 B, end-exclusive at the post-ds nop — same convention as I11's row) |
| 3 | Caller emission `sub_0014F648`: `0x14f65c: lw $v1,0xC($v0)` then `0x14f660: jalr $v1` | Call target is runtime-computed (pointer load) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: resume/external points from static branches, `J`/`JAL`, `SYSCALL+4`, `JALR+8` (return slot) only; indirect targets never queued (I11 receipt, same base = same code) | Recompiler resume discovery is direct-edge-only — it CANNOT learn `0x14f2a8` (0 direct edges: no `case 0x14f2a8`, 0 register refs, no `*0x14f2a8*` file in I11 codegen) |
| 5 | `function_table_emitter.cpp`: 1 slot per function start + resume targets, first-wins dedupe by address; `ps2_runtime.cpp` `lookupFunction`: null slot → `missing-target` diagnostic, policy≠Stop parks `ctx->pc=target` (I11 receipt, same base) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry; splitting emission without a map entry creates no slot |
| 6 | Merge safety: ELF has 0 SYMTAB/DYNSYM sections (stripped) and 0 `.debug*` sections (I11 receipt, same ELF `1b49d05c…`); all 13 named/authoritative CSV rows sit ≥`0x3ff088` (I11 receipt — carries: this CSV is I11's +1 auto-named row below that floor) | New auto-named row at `0x14f2a8` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 873: `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` (inserted in sorted position; `sub_0014F250` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — tail has no SIMD/loops, neighbors unlisted) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `c8d08e6 SSX3 map: add missing function entry 0x14f2a8 (I12)` (1 file, 1 insertion); worktree `4acc59f+7975073+ccefefe+5f10c7d+c8d08e6`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I11 base | `diff` old-CSV new-CSV = exactly the 1 added line; tracked toml byte-identical across I11→I12 |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: same base as I11 (`4acc59f`, recompiler identical by construction); toml identical; ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11) |
| TOML | `W/ssx3-i12.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` = 2 lines |
| Exit / wall | exit 0, 2m40s (`Loaded 9277 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3710 `[warning]`s, same count/class as I11; 0 errors) |
| Outputs | 9451 files: 9449 `.cpp` (9448 functions + `register_functions.cpp`), 2 headers; 401372 resume entries across 7609 owners (+2/+1 vs I11) |
| `0x14f2a8` census | NEW `sub_0014F2A8_0x14f2a8.cpp` 14521 B sha `740bac80…` (head `0x14f2a8 lui $v0,0x53`, `jr $ra` @`0x14f354`→return tail); table slot `g_ps2RecompiledFunctionTable[81064] = sub_0014F2A8_0x14f2a8; // 0x14f2a8` (+ resume slots 81072/81093 for `0x14f2c8`/`0x14f31c` re-homed from `sub_0014F250` — the +2 resume entries) |
| Non-perturbation | `sub_00100008` SAME as I11; `sub_0014F250` SAME (overlap changed nothing); `sub_00395730` SAME; `ps2_recompiled_stubs.h` SAME `5aa6553c…`; `register`+`functions.h` differ only by the +1 entry (+2 slot re-homes) |
| Size/purge | 9.3G ExFAT; 9451 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I11)

| # | Item | I11 | I12 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9448 sources) | Same wiring, cherry-picked byte-identical (`ccefefe`); 9449 sources | NO (count +1 only) |
| 2 | Base | `4acc59f+8fc0c14+89d1126+af0a508` | `4acc59f+7975073+ccefefe+5f10c7d+c8d08e6` (same E7 runtime + I11 row + new entry fix) | NO base move (E-lane static); map +1 row |
| 3 | Toolchain/SDL2/raylib/flags | I11 §toolchain | Byte-identical toolchain (`diff` clean I9=I10=I11=I12); same SDL2 prebuilt, raylib, CC, RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9451 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m23s (`PS2X: game objects: 9449 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2`, 12m08.9s wall, 0 `error:` lines (`logs/ios-runtime-build-tail.log`; full 3358-line log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121191608 B / `4221c4f4131f58db40bf3dd7f627432e847c2f883154514dff99e87a7def1c7d` (I11: 121191480 B — delta is +1 function only, +128 B) |
| lib | `libps2_game_objects.a`, 155299640 B, 297 members (296 unity objects + symdef — same count as I11) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0` |
| Table-populated proof | Entry `sub_00100008_0x100008` defined `T`; **9447** `T …_0x…` game text syms (I11: 9446, +1); **`__Z21sub_0014F2A8_0x14f2a8…` defined `T`** (the gap entry is in the slice); I11's `sub_00395730_0x395730` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I11 (slice growth is game-only) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (staged plist via `plutil`; `7975073` port works) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 15G at this point (18G after staging) |
| Build breaks fixed | NONE — clean first try at the same base (wiring class + E7 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 build 24A437, UDID `P`, connected, developerMode enabled (`logs/ipad-details.json`).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 574-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4165 = the I11 build STILL RUNNING (same bundle UUID `02E31DCD-…` as I11's install; launcher unknown — I11 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4165 reaped BY the install itself; 4181 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I12 build + ISO; MF1/I8–I11 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/processes 60, install 1200, launch 90, files 60, screenshot 60, terminate 30, copy 120) |

### Provision + sign + install (I11 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I11 shape | I12 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; sidecars 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I10=I11=I12) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (18.3s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (3× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 68s, clean replace** — new `installationURL …/431AAEF1-…/` (I11's was `02E31DCD-…`), live occupant PID 4165 reaped BY the install (0 `ps2` after). Fourth clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/431AAEF1-7E07-4A26-83F5-8B126B42371B/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX loads from `cdrom0:`) |

### Launch (argv probe, ISO+env — I10/I11 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive), 5283 lines, 77-line dedup |
| I11 wall | **`0x14f2a8` count = 0** (also `0x14f660` 0, `0x395730` 0) — the I11 wall is GONE |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (block byte-identical, lines 54–67); TEXTURE IDs 1–4; 12 IRX from `cdrom0:/data/modules/` (same set); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x14dd18 target=0x156750 pc=0x156750 … codeRegion=yes policy=1` (line 147; trace torn across 147–148 by DPI-spam interleave — console tearing, target field intact) |
| RPC record | Same 4 unhandled sids as I11 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical payloads, `diff` clean) |
| Crash-log record | Sleep + re-`ls`: **2 files** (I11's `…-015423.ips` + NEW `ps2EntryRunner.cpu_resource-2026-09-21-023911.ips`, 14 KB) — new one fetched via `device copy from` (`logs/cpu-resource.ips`): `bug_type 202`, `Event: cpu usage`, `Action taken: none`, 96% CPU over 94 s, PID 4181 = our probe. Spin report, NOT a crash (no exception/termination; app alive at timeout) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i12-shot1.png`, 2360×1640, app window foreground, status bar names `ps2EntryRunner`, full-black content — same pixels as I11, new process state (past the I11 wall) |

### Past-the-wall table vs I11

| I11 fate | I12 fate | Wall status |
|---|---|---|
| `missing-target … source=0x14f660 target=0x14f2a8` (1×, line 147) | `0x14f2a8` 0 refs anywhere in console (also `0x14f660`/`0x395730` 0) | **I11 WALL GONE** |
| Faulting thread parks at `0x14f2a8` (policy≠Stop sets `ctx->pc=target`, first-report-once); I11 console has 0 refs to `0x14dd18`/`0x156750` — I11 never reached the later site | `0x14f660 → 0x14f2a8` JALR resolves to emitted `sub_0014F2A8` (slot 81064); guest reaches a STRICTLY LATER wall `0x14dd18 → 0x156750` (line 147) with a `0x15xxxx`-region trace (`0x155a50 → 0x1569c0 → 0x14dcdc → 0x156570 → 0x153088 → 0x156338`) I11 never emitted | **First post-entry code executes** (proven by reaching addresses I11 never reached, with identical event prefix) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical payloads | Same boot phase, wall moved strictly later |
| 1 `.ips` (I11's own spin report) | 1 NEW `cpu_resource` spin report (action none) + I11's retained | Same health (no crash); second spin report filed as gap 6 |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels, new state |

Event-prefix identity (the execution proof): normalized `diff` (PID/timestamp-stripped) shows ONLY environmental noise before line 147 (plist mouse-support line position, bundle-UUID working dir, audio period size 6144→1536, appearance-transition drift + VC address) — then the wall-line swap at 147–148 and trailing DPI-spam count. K1 block lines 54–67 byte-identical; TEXTURE 1–4 identical; R3/I11's wall has NO counterpart in I12 (events flow uninterrupted to the new wall).

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x156750`) — same class as `0x14f2a8`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x14dd18 target=0x156750 pc=0x156750 … codeRegion=yes policy=1` (exactly 1×, line 147; `ee:idle` 0 — scheduler keeps other threads) |
| 2 | The target is a coverage hole, not out of range | `0x156750` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `*0x156750*` file, no `case 0x156750u` in any of 9449 files, CSV rows jump `sub_001565C8,0x1565c8,0x1567b8` → `sub_001567B8,0x1567b8,0x156810` (no function starting in `0x1566xx–0x1567ax`) |
| 3 | Precise shape: merged functions, same signature | Emitted `sub_001565C8` shows `jr $ra` @`0x156744` (ds `0x156748`), nop `0x15674c`, then `0x156750: lw $v1,…` heading the next function; that function runs to `jr $ra` @`0x1567b0` (ds `0x1567b4`) → observed bounds `0x156750–0x1567b8` (`0x68`, end-exclusive at the next CSV row start) |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_0014DC80`: `0x14dd14: lw $v1,0x24($v0)` then `0x14dd18: jalr $v1` — same pointer-load shape as the `0x14f2a8`/`0x395730` callers; direct-edge-only resume discovery can never learn it. (The `0x156750` mention inside `sub_00156570_0x156570.cpp` is overlapping linear fall-through emission — file header `Address: 0x156570 - 0x1567b8` — not a direct edge: no `case`, no slot.) |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_00156750,0x156750,0x1567b8,0x68` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9447 syms, 3 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I11 wall** (`0x14f2a8` gone — JALR resolves, guest reaches strictly-later addresses I11 never emitted); **H-b overall** (new wall strictly past the target at `0x156750` + the same 4 unhandled RPC sids + 1 new cpu spin report). The ONE next action: **fork-code brief — close the `0x156750` indirect-target gap the same way** (add the CSV function entry — observed row `sub_00156750,0x156750,0x1567b8,0x68`, next brief re-verifies bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane = frontier s27 E7; shared clone read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i12"
git -C "$FORK" ls-remote fork ssx3          # 4acc59f (E-lane STATIC at I11's base)
git -C "$FORK" log --oneline -5             # 4acc59f [E7] ... (._pack-*.idx noise lines cosmetic)
git -C "$FORK" worktree list                # shared ssx3 @4acc59f + i8/i9/i10/i11 WTs
git -C "$FORK" status --short               # M register_functions.cpp (E-lane uncommitted, 398779 lines)
git -C "$FORK" diff --stat                  # read-only peek only
P="00008112-001224302184A01E"
# --- Task 1a: worktree at HEAD + cherry-picks ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I12/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 4acc59f
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i12" -c user.email="i12@local" cherry-pick 8fc0c14 89d1126 af0a508  # clean: 7975073, ccefefe, 5f10c7d (patches byte-identical)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -in "0014f2\|0014f3" "$WT/games/ssx3/ssx3-functions.sweep.csv"   # tiling: container row only
grep -n "0x14f2\|0x14f3" /Volumes/Extreme\ SSD/ps2x-i11/codegen-output/sub_0014F250_0x14f250.cpp  # head/tail bounds
grep -n "0x14f65c\|0x14f660" /Volumes/Extreme\ SSD/ps2x-i11/codegen-output/sub_0014F648_0x14f648.cpp  # caller shape
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_0014F2A8,0x14f2a8,0x14f35c,0xb4 after line 872 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i12" -c user.email="i12@local" commit -m "SSX3 map: add missing function entry 0x14f2a8 (I12)"  # c8d08e6
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i12.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i12.toml"  # exit 0, 2m40s
ls "$W/codegen-output" | wc -l                                       # 9451 (9449 cpp + 2 h)
grep -n "0x14f2a8" "$W/codegen-output/register_functions.cpp"        # slot 81064 (+ 2 resume re-homes)
find "$W/codegen-output" -name "._*" -delete                        # 9451 -> 0
# --- Task 1d: device configure + build (I11 shape + same base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I10=I11=I12
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m23s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 12m08.9s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 4221c4f4...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9447 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*14F2A8_0x14f2a8"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details.json"
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 574 lines, PID 4165 = I11 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (I11-identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (18.3s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 68s
B="/private/var/containers/Bundle/Application/431AAEF1-7E07-4A26-83F5-8B126B42371B/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive), 5283 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i12 -s ps2EntryRunner --no-recurse  # 2 files (I11's + new)
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type systemCrashLogs \
  --domain-identifier ps2x-i12 --source "ps2EntryRunner.cpu_resource-2026-09-21-023911.ips" \
  --destination "$W/logs/cpu-resource.ips"                        # fetched: bug_type 202, action none
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i12-shot1.png
mv /tmp/i12-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4181  # cleanup only
# --- Task 3: new-wall diagnosis reads ---
grep -in "001566\|001567" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: rows jump 0x1565c8 -> 0x1567b8
grep -c "0x156750" "$W/codegen-output/register_functions.cpp"        # 0 refs
grep -n "0x1567[45]" "$W/codegen-output/sub_001565C8_0x1565c8.cpp"   # jr/ds/nop/head shape
grep -n "0x1567b0\|0x1567b4" "$W/codegen-output/sub_001565C8_0x1565c8.cpp"  # tail bounds
grep -n "0x14dd14\|0x14dd18" "$W/codegen-output/sub_0014DC80_0x14dc80.cpp"  # caller shape
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x156750` has no table entry (mid-function of emitted `sub_001565C8` `0x1565c8–0x1567b8`; head after `jr $ra` @`0x156744`/ds/`nop`; tail `jr $ra` @`0x1567b0`/ds; caller `jalr $v1` @`0x14dd18` with pointer-loaded target; 0 register refs; neighbor-file mention is fall-through emission, not an edge) | `kind=IndirectCall op=JALR source=0x14dd18 target=0x156750` (1×, line 147) + emission census (Task 3) | Fork-code brief: add the `0x156750` entry (observed row `sub_00156750,0x156750,0x1567b8,0x68` — re-verify `jr $ra` @`0x1567b0`/ds bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10/I11) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `7975073` + `ccefefe` + `5f10c7d` + `c8d08e6` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `c8d08e6^… = 4acc59f`, 0 pushes; remote `ssx3` at `4acc59f` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I11 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | Second `.ips`: `cpu_resource` spin report (96% CPU, action none, PID 4181) | `logs/cpu-resource.ips` (bug_type 202, fetched from device) | Informational — no brief unless a later probe shows action-taken or the spin persists past wall fixes |

## Receipt paths

- `local/research/I12/REPORT.md` (this file)
- `local/research/I12/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I10's/I11's)
- `local/research/I12/logs/worktree-add.log`, `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I12/logs/ipad-details.json`, `processes-pre.log`, `entitlements.plist`
- `local/research/I12/logs/install.log` (overwrite, exit 0, 68 s)
- `local/research/I12/logs/elf-device-path.txt`
- `local/research/I12/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I12/logs/crashlog-check.log` (2 files after sleep + re-`ls`: I11's + new), `cpu-resource.ips` (fetched, bug_type 202, PID 4181)
- `local/research/I12/logs/i12-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i12.toml`, codegen log, full build log, details stdout); `W/codegen-output/` (9451 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `c8d08e6`, clean, 4 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — `7975073`/`ccefefe`/`5f10c7d`/`c8d08e6` stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I11); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 4 local commits — the E-line is live with uncommitted work (gap 3; local commits only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4165 — the I11 bundle was running though I11 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.

## TAIL RECEIPT

Report written in 3 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link + Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 314 lines, sha256 `6d4a91b854b9a7db5dd101975d54a5fb4575af7e680b8ea7aeff176548c55db8`.
Tail content line: "Name the launcher of pre-install PID 4165 — the I11 bundle was running though I11 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation." This receipt line ends the report. END-I12-REPORT.
