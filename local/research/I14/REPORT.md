# I14 — Close the 0x243a80 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I13/REPORT.md` read first (all of it: base move to `be0c9ee` + cherry-picks + 1-line CSV entry closed `0x156750` (count 0, guest strictly past it), guest reaches a STRICTLY LATER wall: indirect JALR `0x317054 → 0x243a80` (mid-function of emitted `sub_00243A40` `0x243a40–0x243ab0`, head after `jr $ra` @`0x243a74`/ds/`nop` + frame setup, tail `jr $ra` @`0x243aa8`/ds epilogue, observed bounds `0x243a80–0x243ab0`, caller `jalr $v1` @`0x317054` with vtable-loaded target, 0 register refs — the neighbor-file mention is fall-through emission, not an edge); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I13; the I13 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start (overwrite target; state tabled in Task 2).
- BASE: NO MOVE (E-lane still at `be0c9ee`; `ls-remote` confirms) — separate fork worktree at `be0c9ee` + cherry-picked I13 wiring+map (5 commits, patches byte-identical to I13's) + ONE local map commit `ed378c8` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane owner: frontier s27, E9 landed; shared-clone `ssx3` at `be0c9ee` with the same uncommitted `register_functions.cpp` replacement — read-only peeked, never touched).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9451 SSX3 sources from host `ps2_recomp` codegen, +1 vs I13) on the E9 runtime.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i14/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I14/` standalone, `[I14]` commit, no push.
- Outcome shape: I13 wall GONE — `0x243a80` count 0 on probe, guest executes past it (entry `sub_00243A80_0x243a80` in slice + table slot 331422) and reaches a STRICTLY LATER wall: indirect JALR `0x39cd74 → 0x3a0158`, same gap class (mid-function entry, computed `jalr $v1`, 0 table refs). No crash; one `cpu_resource` spin report (action none). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i14/`, `WT` = `W/fork-wt` (fork worktree), `W13` = `/Volumes/Extreme SSD/ps2x-i13/`, `C` = `W/codegen-output/` (host codegen), `C13` = `W13/codegen-output/`, `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x243a80` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I13's wall — the `0x317054 → 0x243a80` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x243a80` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I13 |
| Alternatives | H-a `0x243a80` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x243a80` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~60 min wall: worktree → codegen 3m14s → build 8m43s → install 70s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT 344M | `du -sh W` after evidence step |
| Evidence `local/research/I14/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i14-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 6 local commits (5 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 3m14s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + worktree + cherry-picks (NO BASE MOVE — E-lane still at `be0c9ee`)

| Item | Receipt |
|---|---|
| Pin (NO MOVE) | `be0c9ee` = `be0c9eeaa337d9685e9536fa4f66c5ce5029aad8`, 2026-09-21 02:38 -0400, `[E9] Drop the unimplemented SIF command handler selector` (same as I13's base) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `be0c9ee` (E-lane has not advanced past I13's base) |
| Base delta (exact) | NONE — I14 base == I13 base; recompiler/runtime/analyzer/TOML all byte-identical by construction |
| E-lane owner | Frontier s27 (E9 landed); shared clone `ssx3` at `be0c9ee` with uncommitted `M ps2xRuntime/src/runner/register_functions.cpp` (398968 insertions — E-work still in flight, +194 vs I13's 398774 peek) — read-only `diff --stat` peek only |
| Worktree | `git -C FORK worktree add --detach W/fork-wt be0c9ee` → `HEAD is now at be0c9ee` (exit 0; `._pack-*.idx` noise lines cosmetic, owner's tree) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry**: `19166a7` = `55ffa6e` (Info.plist CFBundleName), `aa0cb47` = `af7335a` (22-insertion CMake wiring), `b559a40` = `27eef02` (I11 CSV row), `bb3dfe3` = `ad34376` (I12 CSV row), `834f2cc` = `6166d1a` (I13 CSV row); all 5 ported patches byte-identical to I13's originals (`show --patch` diffs clean); attempt 1 applied 3/5 then aborted on the transient dirty-tree complaint (tree verified clean, sequencer ended via `--quit`); picks 4+5 applied individually exit 0; `logs/cherry-pick.log` |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / worktree list / status / diff --stat`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | NO — same `be0c9ee` + I11 row + I12 row + I13 row + new entry fix; tool binary reused, not rebuilt |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read (new WT, post-port): line 2942 `sub_00243A40,0x243a40,0x243ab0`, line 2944 `sub_00243AB0,0x243ab0,0x243b50`; no row starts in `0x243a41–0x243aaf` (line 2939 `0x2438f0` ends exactly at `0x243a40`) | No function in the gap range; new row overlaps the container (toolchain-tolerated per I11/I12/I13 receipts) |
| 2 | C13 emitted `sub_00243A40_0x243a40.cpp` RE-READ: `jr $ra` @`0x243a74` (ds `0x243a78` `sw`), nop `0x243a7c`, then `0x243a80: lui $v0,0x47` + `0x243a84: addiu $sp,$sp,-0x10` frame setup heading the next function; that function runs to `jr $ra` @`0x243aa8` (ds `0x243aac` `addiu $sp,$sp,0x10` epilogue) then `ctx->pc = 0x243AB0u; }` (function ends exactly at container end) | `0x243a80` is a genuine function head with observed bounds `0x243a80–0x243ab0` (`0x30` = 48 B, end-exclusive at the next CSV row start — same convention as I11/I12/I13 rows). I13's observed row VERIFIED byte-for-byte |
| 3 | Caller emission `sub_00316F00`: `0x317050: lw $v1,0xC($v0)` then `0x317054: jalr $v1` (re-grepped in C13, same slice) | Call target is runtime-computed (vtable/record load) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: direct-edge-only resume discovery (I11/I12/I13 receipt; recompiler sources identical — same base — so the receipt carries) | It CANNOT learn `0x243a80` (0 direct edges: no `case 0x243a80`, 0 register refs, no `*0x243a80*` file in C13) |
| 5 | `function_table_emitter.cpp` first-wins dedupe + `lookupFunction` null-slot → `missing-target` park (I11 receipt, carries) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry |
| 6 | Merge safety: ELF stripped (I11 receipt, same ELF `1b49d05c…`); authoritative CSV rows ≥`0x3ff088` (I11 receipt, carries — this CSV is I13's +1 auto-named row below that floor) | New auto-named row at `0x243a80` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | `0x243a80` mention inside `sub_00242EB8_0x242eb8.cpp` (file header `Address: 0x242eb8 - 0x244240`, linear `ctx->pc` fall-through at source lines 2912–2913, no `case`/slot/`func_` reference) | Overlapping linear fall-through emission, NOT a direct edge — confirms 0-edge finding |
| 8 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 2943: `sub_00243A80,0x243a80,0x243ab0,0x30` (inserted in sorted position; `sub_00243A40` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — tail has no SIMD/loops, neighbors unlisted) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `ed378c8 SSX3 map: add missing function entry 0x243a80 (I14)` (1 file, 1 insertion); worktree `be0c9ee+19166a7+aa0cb47+b559a40+bb3dfe3+834f2cc+ed378c8`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I13 worktree CSV | `diff` = exactly the 1 added line; tracked toml byte-identical to I13's (no base move) |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: base identical to I13 (`be0c9ee`, recompiler identical); toml = tracked + 2 path edits (same 2 as I13, re-pointed i13→i14); ELF identical (`1b49d05c…`); CSV +1 row through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11/I12/I13) |
| TOML | `W/ssx3-i14.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` vs tracked = 2 lines; vs I13's TOML = the same 2 path lines re-pointed i13→i14 |
| Exit / wall | exit 0, 3m14s (`Loaded 9279 functions from Ghidra map` (+1), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3712 `[warning]`s (SAME count; warning-set `diff` vs I13 clean); 0 errors) |
| Recompiler report | (I13 → I14) discovered 9449→9450 (+1); recompiled 9272→9273 (+1); stubs 177→177; resumable entry points 401446→401447 (+1) across 7610→7611 owners (+1); fallback promotions 3712→3712, entries 739878→739878; unhandled 0→0 |
| Outputs | 9453 files: 9451 `.cpp` (9450 functions + `register_functions.cpp`), 2 headers; file-list `diff` C13→C = exactly +1 (`sub_00243A80_0x243a80.cpp`) |
| `0x243a80` census | NEW `sub_00243A80_0x243a80.cpp` 3176 B sha `f75aeb02…` (head `0x243a80 lui $v0,…`, `jr $ra` @`0x243aa8`→return tail, `Address: 0x243a80 - 0x243ab0`); table slot `g_ps2RecompiledFunctionTable[331422] = sub_00243A80_0x243a80; // 0x243a80` (exactly 1 slot — register `diff` is exactly the 1 added line; no resume re-homes; linear function) |
| Non-perturbation | `sub_00100008` SAME; `sub_00243A40` SAME (overlap changed nothing); `sub_00156750` SAME; `sub_0014F2A8` SAME; `sub_00395730` SAME; `ps2_recompiled_functions.h` +1 line only; `ps2_recompiled_stubs.h` IDENTICAL |
| Size/purge | 9.3G ExFAT; 9453 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I13)

| # | Item | I13 | I14 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9450 sources) | Same wiring, cherry-picked byte-identical (`aa0cb47` = `af7335a`); 9451 sources | NO (count +1 only) |
| 2 | Base | `be0c9ee+55ffa6e+af7335a+27eef02+ad34376+6166d1a` | `be0c9ee+19166a7+aa0cb47+b559a40+bb3dfe3+834f2cc+ed378c8` (same E9 runtime + I11 row + I12 row + I13 row + new entry fix) | NO BASE MOVE; map +1 row |
| 3 | Toolchain/SDL2/raylib/flags | I13 §toolchain | Byte-identical toolchain (`diff` clean I9=I13=I14); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9453 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m19s (`PS2X: game objects: 9451 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (in xcodebuild invocation line), 8m43s wall, 0 `error:` lines (`logs/ios-runtime-build.log` full on SSD; tail in evidence). Faster than I13's 27m01s (same fresh-tree shape; wall variance, possibly E-lane contention in I13 — tabled as observed) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121208384 B / `a3406ad2e444a96a2a4b3849c1f9d5b7ea5971542b25567025951b0acf3d19bf` (I13: 121208256 B — delta +128 B = new function, not wiring) |
| lib | `libps2_game_objects.a`, 155317384 B (I13: 155314360 B, +3024 B), 297 members (296 unity objects + symdef — same count as I13) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0`, `sdk 27.0` |
| Table-populated proof | Entry `sub_00100008_0x100008` defined `T`; **9450** `T …_0x…` game text syms (I13: 9449, +1 = new `0x243a80` entry); **`__Z21sub_00243A80_0x243a80…` defined `T`** (the gap entry is in the slice); I13's `sub_00156750_0x156750` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I13 (slice growth is game-only) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `19166a7` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 15G at this point (18G after staging) |
| Build breaks fixed | NONE — clean first try at the same base (wiring class + E9 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 build 24A437, UDID `P`, connected, developerMode enabled (`logs/ipad-details.json` — captured via `--json-output /dev/stdout` redirect: direct `--json-output <SSD path>` silently wrote nothing this brief, tabled delta vs I13).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 576-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4214 = the I13 build STILL RUNNING (same bundle UUID `8182D6A4-…` as I13's install; launcher unknown — I13 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 3rd brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4214 reaped BY the install itself; 4223 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I14 build + ISO; MF1/I8–I13 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/processes 60, install 1200, launch 90, files 60, screenshot 60, terminate 30, copy 120, details 60) |

### Provision + sign + install (I13 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I13 shape | I14 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 4.0s, ISO `cp` 40.8s; sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I13=I14) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (21.5s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (5× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 70s, clean replace** — new `installationURL …/725718D8-…/` (I13's was `8182D6A4-…`), live occupant PID 4214 reaped BY the install (0 `ps2` after). Sixth clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/725718D8-9012-4156-968A-A07E1D4DA854/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX loads from `cdrom0:`) |

### Launch (argv probe, ISO+env — I10/I11/I12/I13 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive, PID 4223), 5287 lines, 77-line dedup (5210 DPI-spam lines + 1 inline DPI suffix on the wall head line) |
| I13 wall | **`0x243a80` count = 0** (also `0x317054` 0, `0x156750` 0, `0x14dd18` 0, `0x14f2a8` 0, `0x395730` 0) — the I13 wall is GONE |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (block lines 54–67, same position as I13); TEXTURE IDs 1–4 (5 lines incl. default-texture line, same as I13); 12 IRX from `cdrom0:/data/modules/` (same 2 sets of 6, inside the 4 unhandled-RPC lines); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x39cd74 target=0x3a0158 pc=0x3a0158 … codeRegion=yes policy=1` (raw line 172 head: all scalar fields intact; trace torn mid-address by an INLINE `GetWindowScaleDPI()` suffix + continuation at raw line 173 — I12-style tear) |
| RPC record | Same 4 unhandled sids as I13 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44` — dedup lines 70–75 byte-identical to I13's) |
| Crash-log record | Sleep + re-`ls`: **4 files** (I11's `…-015423.ips` + I12's `…-023911.ips` + I13's `…-032937.ips` + NEW `ps2EntryRunner.cpu_resource-2026-09-21-040134.ips`, 13 KB) — new one fetched via `device copy from` (`logs/cpu-resource.ips`): `bug_type 202`, `Event: cpu usage`, `Action taken: none`, 96% CPU over 94 s, PID 4223 = our probe. Spin report, NOT a crash (no exception/termination; app alive at timeout) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i14-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content — same pixels as I13, new process state (past the I13 wall) |

### Past-the-wall table vs I13

| I13 fate | I14 fate | Wall status |
|---|---|---|
| `missing-target … source=0x317054 target=0x243a80` (1×, line 163) | `0x243a80` 0 refs anywhere in console (also `0x317054`/`0x156750`/`0x14f2a8`/`0x395730` 0) | **I13 WALL GONE** |
| Faulting thread parks at `0x243a80`; I13 console has 0 refs to `0x39cd74`/`0x3a0158`/`0x39fb30`/`0x3a4a88` — I13 never reached the later site | `0x317054 → 0x243a80` JALR resolves to emitted `sub_00243A80` (slot 331422); guest reaches a STRICTLY LATER wall `0x39cd74 → 0x3a0158` (line 172) with a trace through regions I13 never emitted (`0x39fb30`, `0x3a4a88`, `0x398998`, `0x39fe00`, `0x423c90`…) | **First post-entry code executes** (proven by reaching addresses I13 never reached, with identical event prefix) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical lines | Same boot phase, wall moved strictly later |
| 3 `.ips` (I11's + I12's + I13's own spin reports) | 1 NEW `cpu_resource` spin report (action none) + I11's/I12's/I13's retained | Same health (no crash); fourth spin report filed as gap 6 |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels, new state |

Event-prefix identity (the execution proof): normalized `diff` (timestamp/PID/UUID/address-stripped) of the 77-line dedups shows ONLY environmental noise before the wall swap (PID in plist mouse-support + appearance-transition lines, audio `Periods size` 1536→6144) — then the wall-line swap (I13's intact line 76 gone, I14's torn head excluded by the DPI filter + tail fragment present). K1 block lines 54–67 byte-identical; TEXTURE 1–4 identical; all 4 RPC lines identical; I13's wall has NO counterpart in I14 (events flow uninterrupted to the new wall). Note: I14's wall head (raw line 172) carries an INLINE DPI suffix, so the `grep -v DPI` recipe (kept identical to I13's for comparability) excludes it from the dedup — the head with all intact scalar fields is preserved at raw line 172 of the complete console log.

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x3a0158`) — same class as `0x243a80`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x39cd74 target=0x3a0158 pc=0x3a0158 … codeRegion=yes policy=1` (exactly 1×, raw line 172 head; `ee:idle` 0 — scheduler keeps other threads; `ra=0x39cd7c` normal return slot) |
| 2 | The target is a coverage hole, not out of range | `0x3a0158` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `*0x3a0158*` file, no `case 0x3a0158u` in any of 9451 files, CSV rows jump `sub_003A0048,0x3a0048,0x3a0290` → `sub_003A0290,0x3a0290,0x3a0318` (no function starting in `0x3a0049–0x3a028f`) |
| 3 | Precise shape: merged functions, same signature | Emitted `sub_003A0048` shows `jr $ra` @`0x3a014c` (no ds line emitted; `0x3a0150` unmentioned), nop `0x3a0154`, then `0x3a0158: daddu $a3,$a0,$zero` + `beqz $a1` heading the next function; that function is the LAST in the container, running to `jr $ra` @`0x3a0284` (no ds line emitted) then nop `0x3a028c` → observed bounds `0x3a0158–0x3a0290` (`0x138`, end-exclusive at the next CSV row start) |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_0039CD30` (CSV row 7112 `sub_0039CD30,0x39cd30,0x39cd90,0x60`): `0x39cd70: lw $v1,0x6C($v0)` then `0x39cd74: jalr $v1` — vtable/record load (console `record[*]`/`vtbl[*]` fields), same pointer-load shape as the `0x243a80`/`0x156750`/`0x14f2a8`/`0x395730` callers; direct-edge-only resume discovery can never learn it. (`0x3a0158` appears ONLY inside its own container file — linear fall-through emission, not a direct edge: no `case`, no slot, no `dispatchGuestBranch`/`func_` reference anywhere.) |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_003A0158,0x3a0158,0x3a0290,0x138` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9450 syms, 5 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I13 wall** (`0x243a80` gone — JALR resolves, guest reaches strictly-later addresses I13 never emitted); **H-b overall** (new wall strictly past the target at `0x3a0158` + the same 4 unhandled RPC sids + 1 new cpu spin report). The ONE next action: **fork-code brief — close the `0x3a0158` indirect-target gap the same way** (add the CSV function entry — observed row `sub_003A0158,0x3a0158,0x3a0290,0x138`, next brief re-verifies bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane = frontier s27, E9 landed; shared clone read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i14"
git -C "$FORK" ls-remote fork ssx3          # be0c9ee (E-lane NOT advanced past I13's base)
git -C "$FORK" log --oneline -8             # be0c9ee [E9] ... (._pack-*.idx noise lines cosmetic)
git -C "$FORK" worktree list                # shared ssx3 @be0c9ee + i8/i9/i10/i11/i12/i13 WTs
git -C "$FORK" status --short               # M ps2xRuntime/src/runner/register_functions.cpp (E-lane uncommitted, 398968 insertions)
git -C "$FORK" diff --stat                  # read-only peek only
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I14/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" be0c9ee
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i14" -c user.email="i14@local" cherry-pick 55ffa6e af7335a 27eef02 ad34376 6166d1a  # 3/5, transient abort on 4th
git -C "$WT" cherry-pick --quit   # sequencer end (tree verified clean)
git -C "$WT" -c user.name="muse-i14" -c user.email="i14@local" cherry-pick ad34376  # retry clean
git -C "$WT" -c user.name="muse-i14" -c user.email="i14@local" cherry-pick 6166d1a  # retry clean
# 19166a7, aa0cb47, b559a40, bb3dfe3, 834f2cc (patches byte-identical to I13's)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -n "00243A40\|00243A80\|00243AB0" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: container row only
grep -n "0x243a7\|0x243a8\|0x243aa\|0x243ab" /Volumes/Extreme\ SSD/ps2x-i13/codegen-output/sub_00243A40_0x243a40.cpp  # head/tail bounds
sed -n '155,185p' /Volumes/Extreme\ SSD/ps2x-i13/codegen-output/sub_00243A40_0x243a40.cpp  # tail: jr/ds, ends at 0x243ab0
grep -n "0x317050\|0x317054" /Volumes/Extreme\ SSD/ps2x-i13/codegen-output/sub_00316F00_0x316f00.cpp  # caller: lw + jalr $v1
grep -c "0x243a80" /Volumes/Extreme\ SSD/ps2x-i13/codegen-output/register_functions.cpp  # 0 refs
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_00243A80,0x243a80,0x243ab0,0x30 after line 2942 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i14" -c user.email="i14@local" commit -m "SSX3 map: add missing function entry 0x243a80 (I14)"  # ed378c8
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i14.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i14.toml"  # exit 0, 3m14s
ls "$W/codegen-output" | wc -l                                       # 9453 (9451 cpp + 2 h)
grep -n "0x243a80" "$W/codegen-output/register_functions.cpp"        # slot 331422 (exactly 1)
diff /Volumes/Extreme\ SSD/ps2x-i13/codegen-output/register_functions.cpp "$W/codegen-output/register_functions.cpp"  # 1 added line
find "$W/codegen-output" -name "._*" -delete                        # 9453 -> 0
# --- Task 1d: device configure + build (I13 shape + same base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I13=I14
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m19s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 8m43s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # a3406ad2...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9450 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*243A80_0x243a80"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output /dev/stdout > /tmp/ipad-details.json  # file-flag wrote nothing; stdout redirect
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 576 lines, PID 4214 = I13 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (I13-identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (21.5s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 70s
B="/private/var/containers/Bundle/Application/725718D8-9012-4156-968A-A07E1D4DA854/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive), 5287 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i14 -s ps2EntryRunner --no-recurse  # 4 files (I11's + I12's + I13's + new)
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type systemCrashLogs \
  --domain-identifier ps2x-i14 --source "ps2EntryRunner.cpu_resource-2026-09-21-040134.ips" \
  --destination "$W/logs/cpu-resource.ips"                        # fetched: bug_type 202, action none
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i14-shot1.png
mv /tmp/i14-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4223  # cleanup only
# --- Task 3: new-wall diagnosis reads ---
grep -n "0039FF\|003A00\|003A01\|003A02" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: rows jump 0x3a0048 -> 0x3a0290
grep -c "0x3a0158" "$W/codegen-output/register_functions.cpp"        # 0 refs
grep -n "0x3a014\|0x3a015\|0x3a016" "$W/codegen-output/sub_003A0048_0x3a0048.cpp"  # jr/nop/head shape
grep -n "jr          \$ra" "$W/codegen-output/sub_003A0048_0x3a0048.cpp" | tail -3  # tail: jr @0x3a0284, ends 0x3a0290
grep -n -A2 "0x39cd70\|0x39cd74" "$W/codegen-output/sub_0039CD30_0x39cd30.cpp"  # caller: lw + jalr $v1
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x3a0158` has no table entry (mid-function of emitted `sub_003A0048` `0x3a0048–0x3a0290`; head after `jr $ra` @`0x3a014c`/nop @`0x3a0154`; tail `jr $ra` @`0x3a0284`/nop `0x3a028c` — no ds lines emitted at either `jr`; caller `jalr $v1` @`0x39cd74` with vtable-loaded target; 0 register refs; container-only mention is fall-through emission, not an edge) | `kind=IndirectCall op=JALR source=0x39cd74 target=0x3a0158` (1×, raw line 172 head) + emission census (Task 3) | Fork-code brief: add the `0x3a0158` entry (observed row `sub_003A0158,0x3a0158,0x3a0290,0x138` — re-verify `jr $ra` @`0x3a0284`/nop bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10/I11/I12/I13) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `19166a7` + `aa0cb47` + `b559a40` + `bb3dfe3` + `834f2cc` + `ed378c8` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `ed378c8^… = be0c9ee`, 0 pushes; remote `ssx3` at `be0c9ee` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I13 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | Fourth `.ips`: `cpu_resource` spin report (96% CPU, action none, PID 4223) | `logs/cpu-resource.ips` (bug_type 202, fetched from device) | Informational — no brief unless a later probe shows action-taken or the spin persists past wall fixes |

## Receipt paths

- `local/research/I14/REPORT.md` (this file)
- `local/research/I14/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I10's/I11's/I12's/I13's)
- `local/research/I14/logs/worktree-add.log` (transcribed, labeled), `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I14/logs/ipad-details.json` (via stdout redirect — tabled delta), `processes-pre.log`, `entitlements.plist`
- `local/research/I14/logs/install.log` (overwrite, exit 0, 70 s)
- `local/research/I14/logs/elf-device-path.txt`
- `local/research/I14/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I14/logs/crashlog-check.log` (4 files after sleep + re-`ls`: I11's + I12's + I13's + new), `cpu-resource.ips` (fetched, bug_type 202, PID 4223)
- `local/research/I14/logs/i14-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i14.toml`, codegen log, full build log, details stderr); `W/codegen-output/` (9453 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `ed378c8`, clean, 6 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — `19166a7`/`aa0cb47`/`b559a40`/`bb3dfe3`/`834f2cc`/`ed378c8` stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I13); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 6 local commits — the E-line is live with uncommitted work (gap 3; local commits only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4214 — the I13 bundle was running though I13 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.
- Explain why `--json-output <file>` wrote nothing — worked in I13; the stdout redirect produced byte-valid JSON (15 KB), so the record is complete; the flag behavior delta is tabled, not root-caused.

## TAIL RECEIPT

Report written in 4 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link; Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 327 lines, sha256 `9a0dbc22427f1f8a17f2d7ac43eeb390a57237406f0c72e15bf7a157ac8412cd`.
Tail content line: "Explain why `--json-output <file>` wrote nothing — worked in I13; the stdout redirect produced byte-valid JSON (15 KB), so the record is complete; the flag behavior delta is tabled, not root-caused." This receipt line ends the report. END-I14-REPORT.
