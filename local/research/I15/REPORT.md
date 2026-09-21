# I15 — Close the 0x3a0158 indirect-target gap, re-codegen, re-link, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I14/REPORT.md` read first (all of it: base stayed `be0c9ee` + cherry-picks + 1-line CSV entry closed `0x243a80` (count 0, guest strictly past it), guest reaches a STRICTLY LATER wall: indirect JALR `0x39cd74 → 0x3a0158` (mid-function of emitted `sub_003A0048` `0x3a0048–0x3a0290`, head after `jr $ra` @`0x3a014c`/nop @`0x3a0154` — no ds lines emitted at either `jr`, tail `jr $ra` @`0x3a0284`/nop `0x3a028c`, observed bounds `0x3a0158–0x3a0290`, caller `jalr $v1` @`0x39cd74` with vtable-loaded target, 0 register refs — the container mention is fall-through emission, not an edge); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I14; the I14 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4230, same bundle UUID as I14's install — relaunched after I14's cleanup by an unknown launcher; state tabled in Task 2).
- BASE: MOVED (E-lane advanced 1 past `be0c9ee` to `ffdf58c`; `ls-remote` confirms) — separate fork worktree at `ffdf58c` + ported I14 wiring+map (6 commits, patches content-identical to I14's) + ONE local map commit `00e8433` (1 CSV line, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane live: shared `ssx3` at `ffdf58c` with uncommitted `register_functions.cpp` E-work still in flight, +1 insertion vs I14's peek — read-only peeked, never touched).
- Product: device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9453 SSX3 sources from host `ps2_recomp` codegen, +2 vs I14: our `0x3a0158` + E-lane's `0x2c5140`) on the E9 runtime + E11 read-only card-query taps.
- Rules honored: subordinate to E-lane (`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i15/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` run is codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutating; generated sources never staged; app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging + evidence; evidence `local/research/I15/` standalone, `[I15]` commit, no push.
- Outcome shape: I14 wall GONE — `0x3a0158` count 0 on probe, guest executes past it (entry `sub_003A0158_0x3a0158` in slice + table slot 688212; E-lane's `0x2c5140` executes 3× in the new trace though I14 had no slot for it) and reaches a STRICTLY LATER wall: indirect JALR `0x242150 → 0x2c5300`, same gap class (mid-function entry, computed `jalr $v0` — `$v0` delta vs priors' `$v1` — 0 table refs). No crash; one `cpu_resource` spin report (action none). Deterministic single probe.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i15/`, `WT` = `W/fork-wt` (fork worktree), `W14` = `/Volumes/Extreme SSD/ps2x-i14/`, `C` = `W/codegen-output/` (host codegen), `C14` = `W14/codegen-output/`, `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | Closing the `0x3a0158` gap at its layer (map entry) + re-codegen + re-link gets the argv probe PAST I14's wall — the `0x39cd74 → 0x3a0158` JALR resolves, first post-entry code executes, or a NEW named wall appears strictly later |
| Observable | Gap-layer diagnosis with forcing receipts; codegen exit/counts/shas + `0x3a0158` entry census (file + table slot); device Release build WITH game objects exit 0; install-overwrite behavior; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`, fetched if present) + screenshot; past-the-wall table vs I14 |
| Alternatives | H-a `0x3a0158` gone, guest executes past (wall closed at its layer). H-b new wall strictly past the target (layer named with evidence). H-c same fate (`0x3a0158` still missing — entry did not land) |
| Stop | All bars tabled (entry/codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h (used ~85 min wall: worktree+ports → codegen 3m12s → build 8m04s → install 68s → probe 90s) |
| One gap | Task 3 attempts a fix ONLY if config-level; a second fork-code gap gets the next brief, not this one |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 18 GB (23%) — codegen 9.3G + device tree 5.5G + signed app 2.9G + WT 344M | `du -sh W` after evidence step |
| Evidence `local/research/I15/` | ≤ 5 MB | 2.5 MB + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i15-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (device build `-jobs 2`; codegen is single-threaded tool) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutating | 1 file via named add, 7 local commits (6 ports + 1 new), 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 3m12s, exit 0 | `codegen.log` (SSD) |

## Task 1 — Entry fix + host codegen + device link (no iPad)

### Pin + worktree + cherry-picks (BASE MOVE — E-lane advanced to `ffdf58c`)

| Item | Receipt |
|---|---|
| Pin (MOVED) | `ffdf58c` = `ffdf58c4ee3b95bc6dd8779a0baeed0b23afe19b`, 2026-09-21 04:15 -0400, `SSX3: restore the exact card busy-query entry` (1 commit past I14's `be0c9ee`) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `ffdf58c` (E-lane HAS advanced past I14's base) |
| Base delta (exact) | 1 commit, 3 files, +75: CSV +1 (`sub_002C5140,0x2c5140,0x2c5168,0x28` @line 5087), `ps2_e7.h` +53 (E11 read-only card-query taps sharing E7's ordered sink), `ps2_runtime.cpp` +21; recompiler/analyzer/TOML byte-identical (tracked toml `diff` clean `be0c9ee` vs `ffdf58c`) |
| E-lane owner | Live (shared `ssx3` @`ffdf58c` with uncommitted `M ps2xRuntime/src/runner/register_functions.cpp`, 398969 insertions — E-work still in flight, +1 vs I14's 398968 peek; session identity not re-confirmed this brief) — read-only `diff --stat` peek only |
| Worktree | `git -C FORK worktree add --detach W/fork-wt ffdf58c` → `HEAD is now at ffdf58c` (exit 0; `._pack-*.idx` noise lines cosmetic, owner's tree) |
| Sidecars | 330 `._*` in fresh worktree → purged → 0; `status` clean after |
| Port method | **Cherry-pick, clean after one transient retry** (same shape as I14): `ab443f6` = `19166a7` (Info.plist CFBundleName), `c3a6df1` = `aa0cb47` (22-insertion CMake wiring), `a0f86bf` = `b559a40` (I11 CSV row), `6fca9df` = `bb3dfe3` (I12 CSV row), `bbd5ab2` = `834f2cc` (I13 CSV row), `ab830e4` = `ed378c8` (I14 CSV row); attempt 1 applied 3/6 then aborted on the transient dirty-tree complaint (tree verified clean, sequencer ended via `--quit`); picks 4+5+6 applied individually exit 0; `logs/cherry-pick.log` |
| Patch identity | Plist + CMake patches byte-identical; 4 CSV-row patches content-identical (only `index` hash lines differ + 1 hunk-offset `-7003`→`-7004` shift from E-lane's CSV line at 5087 — the added row bytes identical) |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / show / status / diff --stat`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree) |
| Base move? | YES (1 commit) — `ffdf58c` + I11 row + I12 row + I13 row + I14 row + new entry fix; tool binary reused, not rebuilt (recompiler untouched by the move) |

### Gap-layer diagnosis (forcing receipts — the fix layer is decided here)

| # | Receipt | Finding |
|---|---|---|
| 1 | CSV read (new WT, post-port): line 7173 `sub_003A0048,0x3a0048,0x3a0290`, line 7174 `sub_003A0290,0x3a0290,0x3a0318`; no row starts in `0x3a0049–0x3a028f` (line 7172 `0x3a0000` ends exactly at `0x3a0048`) | No function in the gap range; new row overlaps the container (toolchain-tolerated per I11/I12/I13/I14 receipts) |
| 2 | C14 emitted `sub_003A0048_0x3a0048.cpp` RE-READ: `jr $ra` @`0x3a014c` (no ds line emitted), nop `0x3a0154`, then `0x3a0158: daddu $a3,$a0,$zero` + `0x3a015c: beqz $a1` heading the next function; that function is the LAST in the container, running to `jr $ra` @`0x3a0284` (no ds line emitted) then nop `0x3a028c` → `ctx->pc = 0x3a0290u; }` (function ends exactly at container end) | `0x3a0158` is a genuine function head with observed bounds `0x3a0158–0x3a0290` (`0x138` = 312 B, end-exclusive at the next CSV row start — same convention as I11/I12/I13/I14 rows). I14's observed row VERIFIED byte-for-byte |
| 3 | Caller emission `sub_0039CD30`: `0x39cd70: lw $v1,0x6C($v0)` then `0x39cd74: jalr $v1` (re-grepped in C14, same slice) | Call target is runtime-computed (vtable/record load) — statically invisible |
| 4 | `control_flow_analyzer.cpp` `collectInternalBranchTargets`: direct-edge-only resume discovery (I11/I12/I13/I14 receipt; recompiler sources identical across the base move — same diffstat proof — so the receipt carries) | It CANNOT learn `0x3a0158` (0 direct edges: no `case 0x3a0158`, 0 register refs, no `*0x3a0158*` file in C14) |
| 5 | `function_table_emitter.cpp` first-wins dedupe + `lookupFunction` null-slot → `missing-target` park (I11 receipt, carries) | The ONLY path to a resolvable slot for an indirect-only target is a named map entry |
| 6 | Merge safety: ELF stripped (I11 receipt, same ELF bytes `1b49d05c…` re-sha'd); authoritative CSV rows ≥`0x3ff088` (I11 receipt, carries — this CSV is I14's + E-lane row + 1 auto-named row, all below that floor) | New auto-named row at `0x3a0158` is inside NO authoritative range → survives the merge with its CSV end |
| 7 | `0x3a0158` mention census in C14: the ONLY file is its own container `sub_003A0048_0x3a0048.cpp` (linear `ctx->pc` fall-through, no `case`/slot/`func_` reference) | Overlapping linear fall-through emission, NOT a direct edge — confirms 0-edge finding |
| 8 | Decision | **Map/analyzer boundary fix**: add the missing function entry. NOT a recompiler change (no recompiler change can discover a runtime-computed target; entry-splitting without a map entry is slot-less) |

### Entry fix (named files only, local commit, no push)

| Item | Receipt |
|---|---|
| Edit | `games/ssx3/ssx3-functions.sweep.csv` line 7174: `sub_003A0158,0x3a0158,0x3a0290,0x138` (inserted in sorted position; `sub_003A0048` row UNCHANGED — overlap tolerated per receipt 1; no toml `[performance]` change — tail has no SIMD/loops, neighbors unlisted) |
| Commit | `git add games/ssx3/ssx3-functions.sweep.csv` → `00e8433 SSX3 map: add missing function entry 0x3a0158 (I15)` (1 file, 1 insertion); worktree `ffdf58c+ab443f6+c3a6df1+a0f86bf+6fca9df+bbd5ab2+ab830e4+00e8433`, `status` clean, 0 pushes (E-lane mutating) |
| CSV delta vs I14 worktree CSV | `diff` = exactly 2 added lines (E-lane's `0x2c5140` row + our `0x3a0158` row); tracked toml byte-identical to I14's (no base-move change) |

### Host `ps2_recomp` re-run (tool reuse decision tabled)

| Item | Receipt |
|---|---|
| Rebuild? | **NO — old binary provably runs the new inputs**: recompiler/analyzer sources untouched by the base move (move diffstat = CSV + `ps2_e7.h` + `ps2_runtime.cpp` only); toml = tracked (byte-identical to I14's) + 2 path edits; ELF identical (`1b49d05c…`); CSV +2 rows through a loader with no overlap validation |
| Binary | `W10/host-recomp/ps2xRecomp/ps2_recomp`, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` (I10's pin-built tool, run in place — same sha as I11/I12/I13/I14) |
| TOML | `W/ssx3-i15.toml` = tracked toml + exactly 2 path-line edits (`ghidra_output` → WT CSV with new row, `output` → `W/codegen-output/`); `diff` vs tracked = 2 lines; vs I14's TOML = the same 2 path lines re-pointed i14→i15 |
| Exit / wall | exit 0, 3m12s (`Loaded 9281 functions from Ghidra map` (+2), `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3712 `[warning]`s (SAME count; warning SET identical up to line order — emission order is nondeterministic, sorted-`diff` clean); 0 errors) |
| Recompiler report | (I14 → I15) discovered 9450→9452 (+2); recompiled 9273→9275 (+2); stubs 177→177; resumable entry points 401447→401448 (+1) across 7611→7612 owners (+1); fallback promotions 3712→3712, entries 739878→739878; unhandled 0→0 |
| Outputs | 9455 files: 9453 `.cpp` (9452 functions + `register_functions.cpp`), 2 headers; file-list `diff` C14→C = exactly +2 (`sub_002C5140_0x2c5140.cpp`, `sub_003A0158_0x3a0158.cpp`) |
| `0x3a0158` census | NEW `sub_003A0158_0x3a0158.cpp` 19474 B sha `cbc6a2ad…` (head `0x3a0158 daddu $a3,…`, `jr $ra` @`0x3a0284`→return tail, `Address: 0x3a0158 - 0x3a0290`); table slot `g_ps2RecompiledFunctionTable[688212] = sub_003A0158_0x3a0158; // 0x3a0158` (exactly 1 slot — register `diff` is exactly the 2 added lines; no resume re-homes) |
| E-lane entry census | NEW `sub_002C5140_0x2c5140.cpp` 3043 B sha `d2f29e7f…`; table slot `[463950]` (exactly 1) |
| Non-perturbation | `sub_00100008` SAME; `sub_003A0048` SAME (overlap changed nothing); `sub_002C50E0` SAME (E-lane overlap changed nothing); `sub_00243A80`/`sub_00156750`/`sub_0014F2A8`/`sub_00395730` SAME; `ps2_recompiled_functions.h` +2 lines only; `ps2_recompiled_stubs.h` IDENTICAL |
| Size/purge | 9.3G ExFAT; 9455 `._*` reappeared post-codegen → purged → 0; generated sources committed NOWHERE |

### Link mechanism (every CMake/packaging delta vs I14)

| # | Item | I14 | I15 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9451 sources) | Same wiring, ported content-identical (`c3a6df1` = `aa0cb47`); 9453 sources | NO (count +2 only) |
| 2 | Base | `be0c9ee+19166a7+aa0cb47+b559a40+bb3dfe3+834f2cc+ed378c8` | `ffdf58c+ab443f6+c3a6df1+a0f86bf+6fca9df+bbd5ab2+ab830e4+00e8433` (E9 runtime + E11 card taps + I11 row + I12 row + I13 row + I14 row + new entry fix) | BASE MOVED 1 commit; map +2 rows |
| 3 | Toolchain/SDL2/raylib/flags | I14 §toolchain | Byte-identical toolchain (`diff` clean I9=I14=I15); same SDL2 prebuilt, raylib, CC (Homebrew clang 23.1.1 re-verified via `--version`), RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE |
| 4 | ExFAT guard | `._*` purge + glob `EXCLUDE REGEX` | Same; 3 WT sidecars purged pre-configure (same count as I14) | none |
| 5 | Generated-source placement | OUT of tree (`W/codegen-output/`), never staged | Same (`W/codegen-output/`, 9455 files) | none |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0, wall 1m21s (`PS2X: game objects: 9453 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full). Note: `non-monotonic index ._pack-0f6f5c…idx` PhaseScriptExecution noise inside the log (cosmetic, exit 0; new sidecar hash vs I14's — owner's tree, tabled not root-caused) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2` (in xcodebuild invocation line), 8m04s wall, 0 `error:` lines (`logs/ios-runtime-build.log` full on SSD; tail in evidence) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121225168 B / `2517ff01a9951281847cd6d1079b94b845c3f61aeba955d496c51b8c2df5758a` (I14: 121208384 B — delta +16784 B = 2 new game functions + E11 runtime taps, not wiring) |
| lib | `libps2_game_objects.a`, 155326688 B (I14: 155317384 B, +9304 B), 297 members (296 unity objects + symdef — same count as I14) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0`, `sdk 27.0` |
| Table-populated proof | Entry `sub_00100008_0x100008` defined `T`; **9452** `T …_0x…` game text syms (I14: 9450, +2 = new `0x3a0158` + E-lane `0x2c5140` entries); **`__Z21sub_003A0158_0x3a0158…` defined `T`** (the gap entry is in the slice); `__Z21sub_002C5140_0x2c5140…` defined `T`; I14's `sub_00243A80_0x243a80` + I13's `sub_00156750_0x156750` still `T`; `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S` |
| SDL count | 296 `T _SDL_` — identical to I14 (slice growth is game+E11-taps only) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (unsigned plist already correct via `ab443f6` port) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 18G after staging (same shape as I14) |
| Build breaks fixed | NONE — clean first try at the moved base (wiring class + E9/E11 runtime compile clean) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0 build 24A437, UDID `P`, connected, developerMode enabled (`logs/ipad-details.json` — captured via DIRECT `--json-output <SSD path>`: WORKED this brief, 15415 B, exit 0 — I14's silent-no-write did NOT reproduce, tabled delta; stdout-redirect copy also kept on SSD).

### iPad state before install (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install — no `Locked` failure |
| Running processes | 576-line list pre-install (`logs/processes-pre.log`); 1 `ps2` match: PID 4230 = the I14 build STILL RUNNING (same bundle UUID `725718D8-…` as I14's install; relaunched after I14's cleanup by an unknown launcher — I14 reported 0 `ps2` at its cleanup). Untouched before install (overwrite tested against a live occupant, 4th brief running) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4230 reaped BY the install itself; 4255 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I15 build + ISO; MF1/I8–I14 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, apps/lock/processes/details/files/screenshot 60, install 1200, launch 90, copy 120, terminate 30) |

### Provision + sign + install (I14 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I14 shape | I15 delta |
|---|---|---|
| Stage | Single install, ELF+ISO pre-sign | identical; app `cp -R` 1.4s, ISO `cp` 24.3s; sidecars 5 → 0 after purge |
| ELF+ISO bytes | ELF `1b49d05c…` 3890784 B; ISO `3c2f8eb1…` 3005415424 B | Re-sha'd: BOTH IDENTICAL |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean I9=I14=I15) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 (16.1s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Plain install exit 0, clean replace (6× cumulative) | **Plain install on the OCCUPIED target: exit 0 in 68s, clean replace** — new `installationURL …/97479F48-…/` (I14's was `725718D8-…`), live occupant PID 4230 reaped BY the install (0 `ps2` after). Seventh clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF+`SSX3.iso` under `…/97479F48-D03E-4A60-B2F2-999269C43C26/ps2EntryRunner.app/` (`logs/elf-device-path.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; ISO presence by BEHAVIOR (`sceCdRead unresolved` 0, 12 IRX loads from `cdrom0:`) |

### Launch (argv probe, ISO+env — I10/I11/I12/I13/I14 recipe)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso"}'` + argv ELF path → exit 2 (alive, PID 4255), 5200 lines, 77-line dedup (5123 DPI-spam lines + 1 inline DPI suffix on the wall head line) |
| I14 wall | **`0x3a0158` count = 0** (also `0x39cd74` 0, `0x243a80` 0, `0x317054` 0, `0x156750` 0, `0x14f2a8` 0, `0x395730` 0) — the I14 wall is GONE (`0x2c5140`: 2 refs, both inside the new wall's trace) |
| Guest progress | K1 `install#1–8` + `lookup#1–6` (dedup lines 53–66, byte-identical, position −1 vs I14 — the mouse-support plist line moved 4→43 on timing jitter); TEXTURE IDs 1–4 (5 lines, byte-identical); 12 IRX from `cdrom0:/data/modules/` (same 2 sets of 6, inside the 4 unhandled-RPC lines); `[sif-handshake] sregs[1]=1`; `sceCdRead unresolved` 0; `ee:idle` 0; open-fail 0; no teardown; E11 card taps: 0 console lines (taps share E7's ordered sink, not the console — observed) |
| NEW wall | 1× `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x242150 target=0x2c5300 pc=0x2c5300 … codeRegion=yes policy=1` (raw line 191 head: all scalar fields intact; trace torn mid-address by an INLINE `GetWindowScaleDPI()` suffix + continuation at raw line 192 — I12/I14-style tear) |
| RPC record | Same 4 unhandled sids as I14 (`0x80000006`, `0x237`, `0x80000211`, `0x534e44` — dedup lines byte-identical to I14's) |
| Crash-log record | Sleep + re-`ls`: **5 files** (I11's `…-015423.ips` + I12's `…-023911.ips` + I13's `…-032937.ips` + I14's `…-040134.ips` + NEW `ps2EntryRunner.cpu_resource-2026-09-21-050020.ips`, 13 KB) — new one fetched via `device copy from` (`logs/cpu-resource.ips`): `bug_type 202`, `Event: cpu usage`, `Action taken: none`, 90 s CPU over 91 s, PID 4255 = our probe. Spin report, NOT a crash (no exception/termination; app alive at timeout) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i15-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content — sha differs from I14's (clock 5:00 AM + wallpaper phase), content same black, new process state (past the I14 wall) |

### Past-the-wall table vs I14

| I14 fate | I15 fate | Wall status |
|---|---|---|
| `missing-target … source=0x39cd74 target=0x3a0158` (1×, line 172) | `0x3a0158` 0 refs anywhere in console (also `0x39cd74`/`0x243a80`/`0x156750`/`0x14f2a8`/`0x395730` 0) | **I14 WALL GONE** |
| Faulting thread parks at `0x3a0158`; I14 console has 0 refs to `0x242150`/`0x2c5300`/`0x2c5140`/`0x2c4480`/`0x2c55d8`/`0x2c63e8`/`0x2c6074`/`0x23d618`/`0x241ac0`/`0x39c778` (only `0x39d860` 2× / `0x317670` 1× nearby in I14's trace) — I14 never reached the later site | `0x39cd74 → 0x3a0158` JALR resolves to emitted `sub_003A0158` (slot 688212); E-lane's `0x2c5140` executes 3× in the new trace though I14 had NO slot for it (that same call would have parked in I14); guest parks at a STRICTLY LATER wall `0x242150 → 0x2c5300` (line 191). I14's register ALSO lacked `0x2c5300` (0 refs) yet I14 parked at `0x3a0158` first — under identical inputs the I15 thread necessarily executed past I14's park point | **First post-entry code executes** (proven by executing an entry I14 could not resolve and reaching addresses I14 never reached, with identical event prefix; single probe) |
| Unhandled RPCs + handshake (other threads, post-wall) | Same events, byte-identical lines | Same boot phase, wall moved strictly later |
| 4 `.ips` (I11's + I12's + I13's + I14's own spin reports) | 1 NEW `cpu_resource` spin report (action none) + I11's/I12's/I13's/I14's retained | Same health (no crash); fifth spin report filed as gap 6 |
| Black window, guest+loop alive | Black window, guest+loop alive | same pixels (new capture), new state |

Event-prefix identity (the execution proof): normalized `diff` (timestamp/PID/UUID-stripped) of the 77-line dedups shows ONLY environmental noise before the wall swap (mouse-support plist line timing move 4→43, audio `Periods size` 6144→1536, ASLR pointer in appearance-transition lines) — then the wall-fragment swap at dedup line 76 (I14's `0x39`/`0x3a` tail `…0x39cd30 → 0x39d860 → 0x39fd38` gone, I15's `0x23`/`0x2c`/`0x24` run through `0x2c5140` 3× ending at caller container `0x2420c8`). K1 block byte-identical; TEXTURE 1–4 identical; all 4 RPC lines identical; handshake identical; I14's wall has NO counterpart in I15 (events flow uninterrupted to the new wall). Note: I15's wall head (raw line 191) carries an INLINE DPI suffix, so the `grep -v DPI` recipe (kept identical to I14's for comparability) excludes it from the dedup — the head with all intact scalar fields is preserved at raw line 191 of the complete console log.

## Task 3 — Diagnosis + config-level fix only (no fix attempted)

### Diagnosis: NEW wall = indirect-call target mid-function (`0x2c5300`) — same class as `0x3a0158`

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x242150 target=0x2c5300 pc=0x2c5300 … codeRegion=yes policy=1` (exactly 1×, raw line 191 head; `ee:idle` 0 — scheduler keeps other threads; `ra=0x242158` normal return slot; `v0=0x2c5300` carries the computed target) |
| 2 | The target is a coverage hole, not out of range | `0x2c5300` ∈ emitted range but: 0 refs in `register_functions.cpp`, no `case 0x2c5300u` in any of 9453 files, no `*0x2c5300*` file, CSV rows jump `sub_002C52D8,0x2c52d8,0x2c5320` → `sub_002C5320,0x2c5320,0x2c5338` (no function starting in `0x2c52d9–0x2c531f`) |
| 3 | Precise shape: merged functions, same signature | Emitted `sub_002C52D8` shows `jr $ra` @`0x2c52f4` (ds `0x2c52f8` `addiu $sp` EMITTED here — delta vs the `0x3a0158` container), nop `0x2c52fc`, then `0x2c5300: addiu $v0,$zero,0x14` heading the next function; that function is the LAST in the container, running to `jr $ra` @`0x2c5318` → return then `ctx->pc = 0x2c5320u; }` (function ends exactly at container end) → observed bounds `0x2c5300–0x2c5320` (`0x20`, end-exclusive at the next CSV row start). Container emission byte-identical I14→I15 (bounds stable across the base move) |
| 4 | Caller is runtime-computed, statically undiscoverable | `sub_002420C8` (CSV row 2929 `sub_002420C8,0x2420c8,0x242288,0x1c0`): `0x242144: lw $v1,0x0($a2)` then `0x24214c: lw $v0,0x184($v1)` then `0x242150: jalr $v0` — pointer-table load (DELTA: via `$v0`; all priors via `$v1`); direct-edge-only resume discovery can never learn it. (`0x2c5300` appears in its container file — linear fall-through emission, not a direct edge — plus 4 comment-substring matches of the opcode word `0x2c530001` (`sltiu`) in unrelated files: no `case`, no slot, no `dispatchGuestBranch`/`func_` reference anywhere.) |
| 5 | Class | Fork-code, map layer (missing CSV function entry) — NOT config: no flag/plist/path/packaging change emits a function entry or table slot |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Add CSV row `sub_002C5300,0x2c5300,0x2c5320,0x20` + re-codegen + re-link + re-probe | Fork-code (map edit + full Task 1 cycle) — the SAME class as this brief's own gap-closing work | NOT attempted: one gap per brief; a second fork-code cycle belongs to the next brief, not to Task 3 |
| Launch flags / env / plist / packaging tweaks | Config | No candidate exists: the wall is a missing table slot, unreachable from any config surface |
| On-device JIT / MAP_JIT | Subsystem | NOT attempted — AOT keeps resolving every entry the map names (9452 syms, 6 walls closed-or-named by map coverage, never codegen capability) |

Fixes attempted: ZERO in Task 3 (the brief's one gap was closed in Task 1; the next gap is the next brief's).

Contract outcome: **H-a for the I14 wall** (`0x3a0158` gone — JALR resolves, guest executes an entry I14 could not resolve and reaches strictly-later addresses I14 never reached); **H-b overall** (new wall strictly past the target at `0x2c5300` + the same 4 unhandled RPC sids + 1 new cpu spin report). The ONE next action: **fork-code brief — close the `0x2c5300` indirect-target gap the same way** (add the CSV function entry — observed row `sub_002C5300,0x2c5300,0x2c5320,0x20`, next brief re-verifies the `jr $ra` @`0x2c5318` bounds — re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane live, shared ssx3 @ffdf58c + uncommitted E-work; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i15"
git -C "$FORK" ls-remote fork ssx3          # ffdf58c (E-lane advanced 1 past I14's be0c9ee)
git -C "$FORK" log -1 --format='%H %ad %s' ffdf58c  # full hash + date + subject
git -C "$FORK" log --oneline be0c9ee..ffdf58c       # 1 commit
git -C "$FORK" diff --stat be0c9ee ffdf58c          # 3 files, +75 (CSV + e7.h + runtime.cpp)
git -C "$FORK" show ffdf58c -- games/ssx3/ssx3-functions.sweep.csv  # E-lane CSV line @5087
git -C "$FORK" status --short               # M register_functions.cpp (E-lane uncommitted, 398969 insertions)
git -C "$FORK" diff --stat                  # read-only peek only
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
# --- Task 1a: worktree at HEAD + cherry-picks ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I15/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" ffdf58c
WT="$W/fork-wt"; find "$WT" -name "._*" -delete   # 330 -> 0
git -C "$WT" -c user.name="muse-i15" -c user.email="i15@local" cherry-pick 19166a7 aa0cb47 b559a40 bb3dfe3 834f2cc ed378c8  # 3/6, transient abort on 4th
git -C "$WT" cherry-pick --quit   # sequencer end (tree verified clean)
git -C "$WT" -c user.name="muse-i15" -c user.email="i15@local" cherry-pick bb3dfe3  # retry clean
git -C "$WT" -c user.name="muse-i15" -c user.email="i15@local" cherry-pick 834f2cc  # retry clean
git -C "$WT" -c user.name="muse-i15" -c user.email="i15@local" cherry-pick ed378c8  # retry clean
# ab443f6, c3a6df1, a0f86bf, 6fca9df, bbd5ab2, ab830e4 (content-identical to I14's)
# --- Task 1b: diagnosis reads (forcing receipts) ---
grep -n "0039FF\|003A0048\|003A0158\|003A0290\|003A0318" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: container row only
grep -n "0x3a014\|0x3a015\|0x3a016" /Volumes/Extreme\ SSD/ps2x-i14/codegen-output/sub_003A0048_0x3a0048.cpp  # jr/nop/head shape
grep -n "0x3a028\|0x3a029" /Volumes/Extreme\ SSD/ps2x-i14/codegen-output/sub_003A0048_0x3a0048.cpp  # tail: jr @0x3a0284, ends 0x3a0290
grep -n "0x39cd70\|0x39cd74" /Volumes/Extreme\ SSD/ps2x-i14/codegen-output/sub_0039CD30_0x39cd30.cpp  # caller: lw + jalr $v1
grep -c "0x3a0158" /Volumes/Extreme\ SSD/ps2x-i14/codegen-output/register_functions.cpp  # 0 refs
# --- Task 1b: entry fix (named add, local commit, NO push: E-lane mutating) ---
# (insert sub_003A0158,0x3a0158,0x3a0290,0x138 after line 7173 of games/ssx3/ssx3-functions.sweep.csv)
git -C "$WT" add games/ssx3/ssx3-functions.sweep.csv
git -C "$WT" -c user.name="muse-i15" -c user.email="i15@local" commit -m "SSX3 map: add missing function entry 0x3a0158 (I15)"  # 00e8433
# --- Task 1c: host codegen (I10 tool binary reused, NOT rebuilt) ---
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp  # 511791795c16...
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"  # 1b49d05c... (identical)
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i15.toml"   # diff vs tracked toml = 2 lines
time "/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i15.toml"  # exit 0, 3m12s
ls "$W/codegen-output" | wc -l                                       # 9455 (9453 cpp + 2 h)
grep -n "0x3a0158\|0x2c5140" "$W/codegen-output/register_functions.cpp"  # slots 688212 + 463950 (exactly 1 each)
diff /Volumes/Extreme\ SSD/ps2x-i14/codegen-output/register_functions.cpp "$W/codegen-output/register_functions.cpp"  # 2 added lines
find "$W/codegen-output" -name "._*" -delete                        # 9455 -> 0
# --- Task 1d: device configure + build (I14 shape + moved base) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"  # diff clean I9=I14=I15
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (wall 1m21s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 8m04s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # 2517ff01...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9452 game text syms
nm -g "$APP/ps2EntryRunner" | grep "T .*3A0158_0x3a0158"             # new entry T
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details-direct.json"  # WORKED this brief (I14 delta)
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 576 lines, PID 4230 = I14 leftover
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; shasum -a 256 "$ISO"  # 3c2f8eb1... (I14-identical)
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
cp "$ISO" "$SAPP/SSX3.iso"; find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0 (16.1s)
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"   # exit 0 OVERWRITE, 68s
B="/private/var/containers/Bundle/Application/97479F48-D03E-4A60-B2F2-999269C43C26/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # exit 2 (alive), 5200 lines
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i15 -s ps2EntryRunner --no-recurse  # 5 files (I11's + I12's + I13's + I14's + new)
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type systemCrashLogs \
  --domain-identifier ps2x-i15 --source "ps2EntryRunner.cpu_resource-2026-09-21-050020.ips" \
  --destination "$W/logs/cpu-resource.ips"                        # fetched: bug_type 202, action none
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i15-shot1.png
mv /tmp/i15-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4255  # cleanup only
# --- Task 3: new-wall diagnosis reads ---
grep -n "002C5\|002C4F\|002C53" "$WT/games/ssx3/ssx3-functions.sweep.csv"  # tiling: rows jump 0x2c52d8 -> 0x2c5320
grep -c "0x2c5300" "$W/codegen-output/register_functions.cpp"        # 0 refs
grep -n "0x2c52f\|0x2c530\|0x2c531" "$W/codegen-output/sub_002C52D8_0x2c52d8.cpp"  # jr/ds/nop/head/tail shape
sed -n '280,296p' "$W/codegen-output/sub_002420C8_0x2420c8.cpp"      # caller: lw $v1 + lw $v0 + jalr $v0
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x2c5300` has no table entry (mid-function of emitted `sub_002C52D8` `0x2c52d8–0x2c5320`; head after `jr $ra` @`0x2c52f4`/ds `0x2c52f8`/nop @`0x2c52fc`; tail `jr $ra` @`0x2c5318` → return, ends `0x2c5320`; caller `jalr $v0` @`0x242150` with table-loaded target — `$v0` delta; 0 register refs/case/file; container mention is fall-through emission + 4 opcode-word comment substrings, not edges) | `kind=IndirectCall op=JALR source=0x242150 target=0x2c5300` (1×, raw line 191 head) + emission census (Task 3) | Fork-code brief: add the `0x2c5300` entry (observed row `sub_002C5300,0x2c5300,0x2c5320,0x20` — re-verify `jr $ra` @`0x2c5318` bounds), re-run host `ps2_recomp`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action; same 1-line class as this brief) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`, byte-identical to I10/I11/I12/I13/I14) | 4 `[IOP/RPC trace:unhandled]` lines (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `ab443f6` + `c3a6df1` + `a0f86bf` + `6fca9df` + `bbd5ab2` + `ab830e4` + `00e8433` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `00e8433^… = ffdf58c`, 0 pushes; remote `ssx3` at `ffdf58c` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when the E-line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I14 carried) | Untouched this brief | Optional hardening brief (unchanged) |
| 6 | Fifth `.ips`: `cpu_resource` spin report (90 s CPU over 91 s, action none, PID 4255) | `logs/cpu-resource.ips` (bug_type 202, fetched from device) | Informational — no brief unless a later probe shows action-taken or the spin persists past wall fixes |

## Receipt paths

- `local/research/I15/REPORT.md` (this file)
- `local/research/I15/logs/ios-device.toolchain.cmake` (byte-identical to I9's/I10's/I11's/I12's/I13's/I14's)
- `local/research/I15/logs/worktree-add.log` (transcribed, labeled), `cherry-pick.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I15/logs/ipad-details.json` (via DIRECT `--json-output <path>` — worked this brief, tabled delta), `processes-pre.log`, `entitlements.plist`
- `local/research/I15/logs/install.log` (overwrite, exit 0, 68 s)
- `local/research/I15/logs/elf-device-path.txt`
- `local/research/I15/logs/launch-cdimage-console.log` (complete probe), `launch-cdimage-dedup.log`
- `local/research/I15/logs/crashlog-check.log` (5 files after sleep + re-`ls`: I11's + I12's + I13's + I14's + new), `cpu-resource.ips` (fetched, bug_type 202, PID 4255)
- `local/research/I15/logs/i15-shot1.png` (iPad window, black content)
- `W/logs/` (same + `ssx3-i15.toml`, codegen log, full build log, details stderr + stdout copy); `W/codegen-output/` (9455 files, build artifacts, uncommitted); `W/ios-runtime-device/` (build tree); `W/signed-app/` (installed bits); `W/fork-wt/` (worktree @ `00e8433`, clean, 7 local commits, 0 pushes)
- No fork push this brief (E-lane mutating — `ab443f6`/`c3a6df1`/`a0f86bf`/`6fca9df`/`bbd5ab2`/`ab830e4`/`00e8433` stay local until the line allows)

## What I could not do

- Present a guest frame — window stays black through the new wall; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I14); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push the 7 local commits — the E-line is live with uncommitted work (gap 3; local commits only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe; the new wall's determinism is the next brief's first check, not this brief's bar.
- Name the launcher of pre-install PID 4230 — the I14 bundle was running though I14 reported 0 `ps2` at its cleanup; it was reaped by the install without investigation.
- Explain why direct `--json-output <file>` worked this brief after I14's silent no-write — the flag produced byte-valid JSON (15 KB) on the first try, so the record is complete; the behavior delta is tabled, not root-caused.
- Observe E11 card-tap output — 0 console lines from the new taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar.

## TAIL RECEIPT

Report written in 4 chunks (header + contract + Task 1 diagnosis/codegen; Task 1 link + Task 2; Task 3 + commands; gaps + receipts + could-not-do). Pre-receipt measure: 332 lines, sha256 `ed7f902c9756d100b06f589e17a0e814e48966e6d6b71095ee136f36f4c78572`.
Tail content line: "Observe E11 card-tap output — 0 console lines from the new taps (they share E7's ordered sink, not the console); tap behavior is the E-lane's own record, not this brief's bar." This receipt line ends the report. END-I15-REPORT.
