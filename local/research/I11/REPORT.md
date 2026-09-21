# I11 — Close the 0x395730 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I10/REPORT.md` read first (all of it: game objects linked (9445 syms), I9 wall gone, CD wall removed by ISO+env, guest loads 12 IRX + SIF handshake, NEW wall = indirect JALR from `0x2322d4` to mid-function `0x395730` (inside emitted `sub_003956E8` `0x3956e8–0x395750`, no CSV function in `0x395700–0x39573x`); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0, UDID `P` — same device as I10; the I10 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start, I10's R3 probe PID 4137 still running (overwrite against a live occupant).
- BASE MOVE (required, done): separate fork worktree at `fork/ssx3` HEAD `4acc59f` (E7 fix, full hash below) + cherry-picked I10 wiring (`8fc0c14` plist, `89d1126` CMake) + ONE local map commit `af0a508` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane owner: frontier s27 E7 per orchestrator memory; shared-clone `ssx3` at `4acc59f` with the same 398k-line uncommitted `register_functions.cpp` replacement — read-only peeked, never touched).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9448 SSX3 sources from host `ps2_recomp` codegen, +1 vs I10) on the E7 runtime.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i11/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutates; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I11/` standalone, `[I11]` commit, no push.
- Outcome shape: I10 wall GONE — `0x395730` count 0 on probe, guest executes past it (entry `sub_00395730_0x395730` in slice + table slot 677322) and reaches a STRICTLY LATER wall: indirect JALR `0x14f660 → 0x14f2a8`, same gap class (mid-function entry, computed `jalr $v1`, 0 table refs). No crash; one `cpu_resource` spin report (action none). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i11/`, `WT` = `W/fork-wt` (fork worktree), `W10` = `/Volumes/Extreme SSD/ps2x-i10/`, `C` = `W/codegen-output/` (host codegen), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x395730` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I10's R3 wall — the `0x2322d4 → 0x395730` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x395730` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I10 R3 |
| Alternatives | H-a `0x395730` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x395730` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~1 h wall: worktree → codegen 2m46s → build 9m23s → install 68s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT 344M | `du -sh W` after evidence step |
| Evidence `local/research/I11/` | ≤ 5 MB | 2.8 MB, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i11-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutates | 3 files via named adds, 3 local commits, 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 2m46s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + worktree + cherry-picks + `af0a508`

| Item | Receipt |
|---|---|
| Pin (BASE MOVE) | `4acc59f` = `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2`, 2026-09-21 00:58 -0400, `[E7] Feed CPU quadword VIF1 FIFO writes into the interpreter` |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `4acc59f` (E-lane advanced past I10's `a13b66a`) |
| E-lane owner | Frontier s27 E7 per orchestrator memory; shared clone `ssx3` at `4acc59f` with uncommitted `M register_functions.cpp` (398779 lines, same E-work as I10 observed) — read-only `diff --stat` peek only |
| `b6252bb..4acc59f` | 27 files, 2530 insertions, runtime+test only; `ps2xRecomp`/`ps2xAnalyzer`/`games/` all EMPTY (recompiler identical — reuse decision below) |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 4acc59f` → `HEAD is now at 4acc59f` (exit 0; `logs/worktree-add.log`; `._*` pack-idx noise lines cosmetic) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean** (E-lane touched neither file): `8fc0c14` = `3006a07` (Info.plist CFBundleName — still empty at `4acc59f`, install would fail without it), `89d1126` = `3d2e22d` (22-insertion CMake wiring, byte-identical diff); no fetch needed (objects in shared store); `logs/cherry-pick.log` |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / worktree list / status / diff --stat / grep / show / diff --name-only`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | YES (required) — E7 runtime is the new baseline; recompiler byte-identical so the tool binary is reused, not rebuilt |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read: rows `sub_003956E8,0x3956e8,0x395750` then `sub_00395750,…`; global tiling check 9275 rows, 1 overlap (the `0x42c1f0` dup) | No function in `0x395700–0x39573x`; overlap is toolchain-tolerated (dup emits 1 file + 1 slot) |
| 2 | I10 emitted `sub_003956E8_0x3956e8.cpp`: `jr $ra` @`0x395724` (ds `0x395728`), nop `0x39572c`, then `0x395730` head + second `jr $ra` @`0x395748` | Two guest functions merged under one map entry; `0x395730` is a genuine function head |
| 3 | Caller emission `sub_00231FC0`: `0x2322d0: lw $v1,0x104($v0)` then `0x2322d4: jalr $v1` | Call target is runtime-computed (pointer load) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: resume/external points from static branches, `J`/`JAL`, `SYSCALL+4`, `JALR+8` (return slot) only; indirect targets never queued | Recompiler resume discovery is direct-edge-only — it CANNOT learn `0x395730` (0 direct edges: no `case 0x395730`, no constant-target dispatch in 9449 files) |
| 5 | `function_table_emitter.cpp`: 1 slot per function start + resume targets, first-wins dedupe by address; `ps2_runtime.cpp` `lookupFunction`: null slot → `missing-target` diagnostic, policy≠Stop parks `ctx->pc=target` | The ONLY path to a resolvable slot for an indirect-only target is a named map entry; splitting emission without a map entry creates no slot |
| 6 | Merge safety (`elf_parser.cpp` `addOrMerge`): ELF has 0 SYMTAB/DYNSYM sections (stripped) and 0 `.debug*` sections (no DWARF); all 13 named/authoritative CSV rows sit ≥`0x3ff088` | New auto-named row at `0x395730` is inside NO authoritative range → survives the merge with its CSV end; same-start dupes merge by max end |
| 7 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 7006: `sub_00395730,0x395730,0x395750,0x20` (inserted in sorted position; `sub_003956E8` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — tail has no SIMD/loops, neighbors unlisted) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `af0a508 SSX3 map: add missing function entry 0x395730 (I11)` (1 file, 1 insertion); worktree `4acc59f+8fc0c14+89d1126+af0a508`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I10 base | `diff` old-CSV new-CSV = exactly the 1 added line; tracked toml byte-identical across bases |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: `ps2xRecomp`+`ps2xAnalyzer` diff empty across the base move; toml identical; ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, 1567240 B, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place) |
| TOML | `W/ssx3-i11.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` = 2 lines |
| Exit / wall | exit 0, 2m46s (`Loaded 9276 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3710 `[warning]`s, same count/class as I10) |
| Outputs | 9450 files: 9448 `.cpp` (9447 functions + `register_functions.cpp`), 2 headers; 401370 resume entries across 7608 owners |
| `0x395730` census | NEW `sub_00395730_0x395730.cpp` 2190 B sha `8dbfb208…` (head `0x395730–0x395750`, `ctx->pc=0x395730` entry, `jr $ra`→return tail); table slot `g_ps2RecompiledFunctionTable[677322] = sub_00395730_0x395730; // 0x395730` |
| Non-perturbation | `sub_00100008` sha `c0a9c4e6…` == I10; `stubs.h` `5aa6553c…` == I10; `sub_003956E8` sha `db69e994…` == I10 (overlap changed nothing); `register`+`functions.h` differ only by the +1 entry |
| Size/purge | 9.3G ExFAT; 9450 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I10)

| # | Item | I10 | I11 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9447 sources) | Same wiring, cherry-picked byte-identical (`89d1126`); 9448 sources | NO (count +1 only) |
| 2 | Base | `b6252bb+3006a07+3d2e22d` | `4acc59f+8fc0c14+89d1126+af0a508` (E4 taps + E7 observe + E7 FIFO feed + entry fix) | YES — required base move (runtime-only delta) |
| 3 | Toolchain/SDL2/raylib/flags | I10 §toolchain | Byte-identical toolchain (`diff` clean I9=I10=I11); same SDL2 prebuilt, raylib, CC, RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9450 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0 (`Configuring done (65.4s)`, `Generating done (20.0s)`; `PS2X: game objects: 9448 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2`, 9m23s wall, 0 `error:` lines (`logs/ios-runtime-build-tail.log`; full 3357-line log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121191480 B / `5673e9df0172771e622e682bdb3025319ad7b09c4512584878cca4891d78db55` (I10: 121096664 B — delta is E7 runtime + 1 function) |
| lib | `libps2_game_objects.a`, 155295392 B, 297 members (296 unity objects + symdef — same count as I10) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0` |
| Table-populated proof | Entry `sub_00100008_0x100008` defined `T`; **9446** `T …_0x…` game text syms (I10: 9445, +1); **`__Z21sub_00395730_0x395730…` defined `T`** (the gap entry is in the slice); `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I10 (runtime slice growth is E7 + game, not SDL) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (staged plist via `plutil`; `8fc0c14` port works) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 15G at this point (18G after staging) |
| Build breaks fixed | NONE — clean first try at the new base (wiring class + E7 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 build 24A437, UDID `P`, connected, developerMode enabled (`logs/ipad-details.json`).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 570-line list pre-install; 1 `ps2` match: PID 4137 = the I10 R3 probe binary STILL RUNNING (same bundle UUID `4D96D6A2-…` as I10's install 2). Untouched before install (overwrite tested against a live occupant) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4137 reaped BY the install itself; 4144 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I11 build + ISO; MF1/I8/I9/I10 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/processes 60, install 1200, launch 90, files 60, screenshot 60, terminate 30, copy 120) |

### Provision + sign + install (I10 install-2 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I10 shape | I11 delta |
|---|---|---|
| Stage | `cp -R` unsigned `APP` → `SAPP` + ELF pre-sign (install 1); +`SSX3.iso` pre-sign (install 2) | **Single install, ELF+ISO pre-sign** (ISO+env is the known-good recipe — no bare-ELF probe repeated); sidecars 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I10=I11) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (17.6s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (twice) | **Plain install on the OCCUPIED target: exit 0 in 68s, clean replace** — new `installationURL …/02E31DCD-…/` (I10's was `4D96D6A2-…`), live occupant PID 4137 reaped BY the install (0 `ps2` after). Third clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/02E31DCD-EB49-4D44-93DF-FAA01644CF7F/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX loads from `cdrom0:`) |

### Launch (argv probe, ISO+env — I10 R3 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive), 5286 lines, 77-line dedup |
| I10 wall | **`0x395730` count = 0** — the R3 wall is GONE (was 1× at R3 line 123) |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (identical lines 54–67); TEXTURE IDs 1–4; 12 IRX from `cdrom0:/data/modules/` (same set); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x14f660 target=0x14f2a8 pc=0x14f2a8 … codeRegion=yes policy=1` (line 147; line torn mid-trace by DPI-spam interleave — console tearing, target field intact) |
| RPC record | Same 4 unhandled sids as R3 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical payloads) |
| Crash-log record | Sleep + re-`ls`: **1 file** `ps2EntryRunner.cpu_resource-2026-09-21-015423.ips` (15 KB) — fetched via `device copy from` (`logs/cpu-resource.ips`): `bug_type 202`, `Event: cpu usage`, `Action taken: none`, 96% CPU over 94 s, PID 4144 = our probe. Spin report, NOT a crash (no exception/termination; app alive at timeout) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i11-shot1.png`, 2360×1640, app window foreground, status bar names `ps2EntryRunner`, full-black content — same pixels as I10, new process state (past the R3 wall) |

### Past-the-wall table vs I10 R3

| I10 R3 fate | I11 fate | Wall status |
|---|---|---|
| `missing-target … source=0x2322d4 target=0x395730` (1×, line 123) | `0x395730` 0 refs anywhere in console | **I10 WALL GONE** |
| Faulting thread parks at `0x395730` (policy≠Stop sets `ctx->pc=target`, first-report-once); R3 console has 0 refs to `0x14f660`/`0x14f2a8` — R3 never reached the later site | `0x2322d4 → 0x395730` JALR resolves to emitted `sub_00395730` (slot 677322), executes 8 insns, returns; guest reaches a STRICTLY LATER wall `0x14f660 → 0x14f2a8` (line 147) | **First post-entry code executes** (proven by reaching an address R3 never reached, with identical event prefix) |
| Unhandled RPCs + handshake at lines 125–145 (other threads, post-wall) | Same events at lines 122–133 + 149 (identical payloads; ±4-line drift) | Same boot phase, wall moved strictly later |
| 0 `.ips` | 1 `cpu_resource` spin report (action none) | Same health (no crash); first spin report filed as gap 6 |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels, new state |

Event-prefix identity (the execution proof): lines 32–67 byte-identical (TEXTURE 1–3, K1 installs/lookups); TEXTURE 4 at 69→70; R3's wall at 123 has NO counterpart in I11 (events flow 122→133 uninterrupted); I11's wall at 147 sits where R3 (line ~140–144) had none.

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x14f2a8`) — same class as `0x395730`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x14f660 target=0x14f2a8 pc=0x14f2a8 … codeRegion=yes policy=1` (exactly 1×, line 147; `ee:idle` 0 — scheduler keeps other threads) |
| 2 | The target is a coverage hole, not out of range | `0x14f2a8` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `*0x14f2a8*` file, CSV has no function starting in `0x14f25x–0x14f2ax` (container row `sub_0014F250,0x14f250,0x14f418`) |
| 3 | Precise shape: merged functions, same signature | Emitted `sub_0014F250` shows `jr $ra` @`0x14f29c` (ds `0x14f2a0 addiu $sp`), nop `0x14f2a4`, then `0x14f2a8: lui $v0,0x53` heading the next function; that function runs to `jr $ra` @`0x14f354` (ds `0x14f358`) → observed bounds `0x14f2a8–0x14f35c` |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_0014F648`: `0x14f65c: lw $v1,0xC($v0)` then `0x14f660: jalr $v1` — same pointer-load shape as the `0x395730` caller; direct-edge-only resume discovery can never learn it |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9446 syms, 2 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I10 wall** (`0x395730` gone — JALR resolves, 8 post-entry insns execute, guest reaches a strictly later address); **H-b overall** (new wall strictly past the target at `0x14f2a8` + the same 4 unhandled RPC sids + 1 cpu spin report). The ONE next action: **fork-code brief — close the `0x14f2a8` indirect-target gap the same way** (add the CSV function entry — observed row `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4`, next brief re-verifies bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane = frontier s27 E7; shared clone read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i11"
git -C "$FORK" ls-remote fork ssx3          # 4acc59f (E-lane advanced past I9/I10's a13b66a)
git -C "$FORK" log --oneline -8             # 4acc59f [E7] ... (._pack-*.idx noise lines cosmetic)
git -C "$FORK" worktree list                # shared ssx3 @4acc59f + i8/i9/i10 WTs
git -C "$FORK" status --short               # M register_functions.cpp (E-lane uncommitted, 398779 lines)
git -C "$FORK" diff --stat                  # read-only peek only
git -C "$FORK" diff --name-only b6252bb..4acc59f | grep -iE "recomp|analyz|games/"  # empty: recompiler identical
git -C "$FORK" show 4acc59f:ps2xRuntime/ios/Info.plist | grep -A1 BundleName  # empty: 3006a07 still needed
P="00008112-001224302184A01E"
# --- Task 1a: worktree at HEAD + cherry-picks ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I11/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 4acc59f
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i11" -c user.email="i11@local" cherry-pick 3006a07 3d2e22d  # clean: 8fc0c14, 89d1126
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -iE "395[67]" "$WT/games/ssx3/ssx3-functions.sweep.csv"   # tiling around target
grep -n "0x395730" /Volumes/Extreme\ SSD/ps2x-i10/codegen-output/*.cpp  # 2 files, comments only, 0 edges
sed -n '95,200p' "$WT/ps2xRecomp/src/lib/control_flow_analyzer.cpp"     # direct-edge-only discovery
sed -n '1787,1914p' "$WT/ps2xRecomp/src/lib/ps2_recompiler.cpp"         # discoverAdditionalEntryPoints
/opt/homebrew/opt/llvm/bin/llvm-readelf -S ELF | grep -ciE "SYMTAB|DYNSYM"  # 0: stripped, merge safe
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_00395730,0x395730,0x395750,0x20 after line 7005 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i11" -c user.email="i11@local" commit -m "SSX3 map: add missing function entry 0x395730 (I11)"  # af0a508
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i11.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i11.toml"  # exit 0, 2m46s
ls "$W/codegen-output" | wc -l                                       # 9450 (9448 cpp + 2 h)
grep -n "0x395730" "$W/codegen-output/register_functions.cpp"        # slot 677322
find "$W/codegen-output" -name "._*" -delete                        # 9450 -> 0
# --- Task 1d: device configure + build (I10 shape + new base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I10=I11
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (65.4s+20.0s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 9m23.4s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 5673e9df...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9446 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*395730_0x395730"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details.json"
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 570 lines, PID 4137 = I10 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (I10-identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (17.6s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 68s
B="/private/var/containers/Bundle/Application/02E31DCD-EB49-4D44-93DF-FAA01644CF7F/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive), 5286 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i11 -s ps2EntryRunner --no-recurse  # 1 cpu_resource file
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type systemCrashLogs \
  --domain-identifier ps2x-i11 --source "ps2EntryRunner.cpu_resource-2026-09-21-015423.ips" \
  --destination "$W/logs/cpu-resource.ips"                        # fetched: bug_type 202, action none
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i11-shot1.png
mv /tmp/i11-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4144  # cleanup only
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x14f2a8` has no table entry (mid-function of emitted `sub_0014F250` `0x14f250–0x14f418`; head after `jr $ra` @`0x14f29c`/ds/`nop`; caller `jalr $v1` @`0x14f660` with pointer-loaded target; 0 register refs) | `kind=IndirectCall op=JALR source=0x14f660 target=0x14f2a8` (1×, line 147) + emission census (Task 3) | Fork-code brief: add the `0x14f2a8` entry (observed row `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` — re-verify `jr $ra` @`0x14f354`/ds bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `8fc0c14` + `89d1126` + `af0a508` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `af0a508^… = 4acc59f`, 0 pushes; remote `ssx3` at `4acc59f` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I10 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | First `.ips`: `cpu_resource` spin report (96% CPU, action none, PID 4144) | `logs/cpu-resource.ips` (bug_type 202, fetched from device) | Informational — no brief unless a later probe shows action-taken or the spin persists past wall fixes |

## Receipt paths

- `local/research/I11/REPORT.md` (this file)
- `local/research/I11/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I10's)
- `local/research/I11/logs/worktree-add.log`, `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I11/logs/ipad-details.json`, `ipad-apps-pre.log`, `entitlements.plist`
- `local/research/I11/logs/install.log` (overwrite, exit 0, 68 s)
- `local/research/I11/logs/elf-device-path.txt`
- `local/research/I11/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I11/logs/crashlog-check.log` (1 cpu_resource file after sleep + re-`ls`), `cpu-resource.ips` (fetched, bug_type 202)
- `local/research/I11/logs/i11-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i11.toml`, codegen log, full build log, process lists, details stdout); `W/codegen-output/` (9450 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `af0a508`, clean, 3 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — `8fc0c14`/`89d1126`/`af0a508` stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I10); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 3 local commits — the E-line is live with uncommitted work (gap 3; local commits only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.

## TAIL RECEIPT

Report written in 3 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link + Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 312 lines, sha256 `07264f119397d3e5c7757500096e4e27f98b9016e60fa7c9c2860804dc172e7e`.
Tail content line: "Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar." This receipt line ends the report. END-I11-REPORT.
