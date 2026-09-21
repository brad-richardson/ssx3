# I10 — Link SSX3 recompiled objects into the iphoneos runtime, re-probe on iPad

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I9/REPORT.md` read first (all of it: real `SLUS_207.72` shipped as bundle resource, argv probe reaches `run()`, NEW wall = Dormant-at-entry on the empty recompiled-function table (`registerFunction` callerless, stub `register_functions.cpp`, device build `PS2X_BUILD_RECOMP=OFF`); gap 1 = this brief).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P`, iPadOS 27.0 — same device as I9; I9 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start (overwrite test, I9 gap 3).
- Fork: separate worktree `/Volumes/Extreme SSD/ps2x-i10/fork-wt` at pinned `b6252bb` + topic-branch checkout of `3006a07` + ONE local commit `3d2e22d` (CMake wiring, unpushed — E-lane mutating). Shared clone untouched except the one `worktree add` + read-only inspection (E-lane owner: E6 live in s26; shared-clone `ssx3` at `a13b66a` with a 398k-line uncommitted `register_functions.cpp` replacement — read-only peeked, never touched).
- Product: (pending Task 1 build) device Release `ps2EntryRunner.app` WITH `ps2_game_objects` static lib (9447 SSX3 sources from host `ps2_recomp` codegen).
- Rules honored: subordinate to E-lane (`-j2`/`-jobs 2` everywhere, never 4); all trees under `/Volumes/Extreme SSD/ps2x-i10/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; host `ps2_recomp` runs are codegen (no lease), bounded + tabled; fork worktree only, named `git add`, fork remote only, no push while E-lane mutates; generated sources never staged; app fate from console + `.ips`, never exit code; screenshots to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before configure + staging; evidence `local/research/I10/` standalone, `[I10]` commit, no push.
- Outcome shape: I9 wall GONE — guest executes past entry (K1 syscalls, texture uploads); R1/R2 spin on unmapped CD read (LBN 0x10); Task 3 config fix (ship `SSX3.iso` + `-e PS2X_CD_IMAGE`) removes the CD wall — guest loads 12 IRX modules, SIF handshake, then NEW named wall: indirect JALR to mid-function `0x395730` with no table entry (recompiler boundary gap, fork-code class). No crash, no `.ips`, deterministic.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i10/`, `WT` = `W/fork-wt` (fork worktree), `C` = `W/codegen-output/` (host codegen), `APP` = unsigned device `.app`, `SAPP` = staged signed copy, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E6-owned).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The iphoneos device runtime linked with host-generated SSX3 recompiled objects gets PAST I9's Dormant-at-entry wall (`missing-target`/`ee:idle` at `0x100008`) on argv probe — first guest function executes, or a NEW named wall appears past entry |
| Observable | Host `ps2_recomp` build exit + codegen exit/counts/shas; device Release build WITH game objects exit 0; install-overwrite behavior on the occupied target; argv-probe console (complete) + `systemCrashLogs` listing (sleep + re-`ls`) + screenshot; past-the-wall table vs I9 |
| Alternatives | H-a probe executes guest code past entry (wall gone). H-b new wall past entry (layer named with evidence). H-c same fate (`missing-target`/`ee:idle` — link did not populate the table) |
| Stop | All bars tabled (codegen/build/install/probe/diagnosis) or any cap (partial tabled as gap). Hypothesis outcome + ONE next action in Task 3 |
| Time box | 6 h |
| AOT-first | On-device JIT (`dynamic-codesigning`/MAP_JIT) OUT of scope unless receipts prove the AOT link cannot satisfy the table (decision tabled either way) |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 80 GB | 24 GB (30%) — codegen ~9G post-purge + host-recomp 5.7G + device tree 5.5G + signed apps 3.2G + WT 342M | `du -sh W` after evidence step |
| Evidence `local/research/I10/` | ≤ 5 MB | 2.8 MB, 19 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i10-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | 2 everywhere (host make `-j2`, Xcode `-jobs 2`) | exact commands |
| Fork writes | worktree only, named `git add`, fork remote only, no push while E-lane mutates | 1 file, 1 local commit `3d2e22d`, 0 pushes | `status` clean, §Task 1 |
| Host codegen runs | bounded, tabled (no lease — codegen, not boots) | 1 run, 6m34s, exit 0 | `logs/codegen.log` |

## Task 1 — Host codegen + device link (no iPad)

### Pin + worktree + `3006a07` + `3d2e22d`

| Item | Receipt |
|---|---|
| Pin | `b6252bb` (brief's pin); `b6252bbc0f25e195f9650943149bfb38c83829d4` |
| Remote HEAD (tabled) | `fork/ssx3` at `a13b66a` (unchanged since I9 — E-line not advanced); shared clone `ssx3` also `a13b66a` |
| E-lane owner | E6 live (s26 per orchestrator memory); shared clone carries a 398779-line uncommitted `M ps2xRuntime/src/runner/register_functions.cpp` (generated-table replacement, table base `0x100008`) — read-only `git diff` peek only, never touched |
| Worktree | `git -C FORK worktree add --detach W/fork-wt b6252bb` → `HEAD is now at b6252bb` (`logs/worktree-add.log`); `status` clean |
| `3006a07` method | **Topic-branch checkout** (not cherry-pick): `git fetch fork i8-device-bundle-name` + `checkout --detach 3006a07` → exact hash preserved, zero new commits at that point |
| Fix present | `CFBundleName = ps2EntryRunner` rides along (same as I9) |
| Shared-clone contact | One `worktree add` + read-only `log / rev-parse / ls-remote / worktree list / status / diff --stat + head-60`; no reads of its working tree, no builds, no checkout/pull/stash |
| Sidecars | 327 `._*` in fresh worktree → purged → 0; `status` clean after |
| Base move? | NO — recompiler at the pinned base built + ran clean; no newer base needed |

### Host `ps2_recomp` build (codegen tool, from the worktree pin)

| Item | Receipt |
|---|---|
| Configure | `cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -S WT -B W/host-recomp` → exit 0 (`Configuring done (241.8s)`, `Generating done (13.1s)`; FetchContent: elfio/toml11/fmt/libdwarf/rabbitizer/sse2neon) |
| Build break 1 (ExFAT class) | First `cmake --build -j2 --target ps2_recomp` exit 2: rabbitizer glob compiled `._*.c` AppleDouble sidecars (4890 in `_deps`) → 13 errors, ALL `._` paths. Fix: purge → rebuild exit 0. No source changes |
| Binary | `W/host-recomp/ps2xRecomp/ps2_recomp`, 1567240 B, sha256 `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763` |
| P1 binary (tabled, NOT used) | `/Volumes/Extreme SSD/ps2recomp-spike/P1/bin/ps2_recomp`, same size 1567240 B but sha256 `7654e7fe4a7316476dfcc00a418c850bd8ecffeb301b345624500304e22e826f` — different pin, provenance unknown; I10 codegen uses only the pin-built binary |

### Host codegen run (`ps2_recomp` over SSX3 toml)

| Item | Receipt |
|---|---|
| TOML | `W/ssx3-i10.toml` = `WT/games/ssx3/ssx3.toml` + exactly 2 path-line edits: `ghidra_output` → worktree tracked CSV (sha `b9aae747…`, byte-identical to the toml's shared-clone path; P1's CSV differs `6d231e81…`, not used), `output` → `W/codegen-output/`; `input` ELF unchanged (`P1/SLUS_207.72`, sha `1b49d05c…` as in I9); all other 1609 lines identical (`diff` = 2 lines) |
| Command | `time W/host-recomp/ps2xRecomp/ps2_recomp W/ssx3-i10.toml` |
| Exit / wall | exit 0, 6m34s (`logs/codegen.log`: `Loaded 9275 functions from Ghidra map`, `ELF entry point: 0x100008`, `Recompilation completed successfully`; 3710 `[warning]` lines, all control-flow/JR-promotion class) |
| Outputs | 9449 files: 9447 `.cpp` (9446 functions + `register_functions.cpp`), 2 headers (`ps2_recompiled_functions.h` 9446 decls, `ps2_recompiled_stubs.h`); 398953 table assignments; table base `0x100008` end `0x42e520`; entry `0x100008` = slot 0 (`sub_00100008_0x100008`) |
| Shas | `register_functions.cpp` `2ca28d6f…`, `ps2_recompiled_functions.h` `ace7e72c…`, `ps2_recompiled_stubs.h` `5aa6553c…`, `sub_00100008_0x100008.cpp` `c0a9c4e6…` (full shas in exact-commands block) |
| Size | `du -sh` 18G (ExFAT allocated); generated sources committed NOWHERE (build artifacts in `W/`, never staged) |
| Arch census | 0 AVX files (`_mm256_/_mm512_/immintrin`); 531 SSE-level files — covered by the sse2neon path the I9 device build already uses; `registerFunction` refs 0 (static-initializer table, no callers needed) |
| Unity safety probe | 400-file sample: 0 `^static`, 0 `^namespace {` — one global `sub_…` per file, labels function-local |

### Link mechanism (static lib + every CMake/packaging delta vs I9)

| # | Item | I9 | I10 | Delta? |
|---|---|---|---|---|
| 1 | Mechanism | Stub `register_functions.cpp` (zeroed table) globbed into runner | `ps2_game_objects` STATIC lib from `PS2X_GAME_CODEGEN_DIR` (9447 sources) linked into `ps2EntryRunner`; stub dropped from runner glob | YES — fork commit `3d2e22d`, 22 insertions, 1 file (`ps2xRuntime/CMakeLists.txt`), local only, no push (E-lane mutating) |
| 2 | `PS2X_GAME_CODEGEN_DIR` | n/a (empty default) | `-DPS2X_GAME_CODEGEN_DIR=W/codegen-output` | configure flag (empty default = zero behavior change) |
| 3 | Runner unity/PCH | UNITY ON batch 32, PCH ON | game lib mirrors runner unity switch (batch 32); PCH stays runner-private | same switch reused |
| 4 | ExFAT guard | `._*` purge before configure | purge + `list(FILTER … EXCLUDE REGEX "/\\._")` in the glob (9449 sidecars reappeared post-codegen → purged → 0) | hardening line, tabled |
| 5 | Generated-source placement | n/a | OUT of tree (`W/codegen-output/`), never staged; P1 precedent was in-tree overwrite (`.orig` backup) — not followed | placement decision, tabled |
| 6 | IPO/LTO | Xcode multi-config → `CMAKE_BUILD_TYPE` unset → IPO block never fires | same (game lib gets no IPO either) | none |
| 7 | Toolchain/SDL2/raylib/flags | I9 §toolchain | byte-identical toolchain file (`diff` clean); same SDL2 prebuilt, raylib, CC, RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF | NONE except row 2 |

### Configure + build + binary record

| Item | Receipt |
|---|---|
| Configure | Exit 0 (`Configuring done (49.7s)`, `Generating done (18.0s)`; `PS2X: game objects: 9447 sources from W/codegen-output`; `logs/ios-runtime-configure.log`, full) |
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2`, 24m4.9s wall, 0 `error:` lines (`logs/ios-runtime-build-tail.log`; full log on SSD) |
| Path | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app`, binary `ps2EntryRunner` |
| Size / sha256 | 121096664 B / `a96268db1e2c547d6d258729bcce600930563e0b5a37e3422275f0e7070fbe53` (I9: 2944712 B — 41x growth is the game) |
| lib | `libps2_game_objects.a`, 155292728 B, 297 members (296 unity objects + symdef) |
| Slice | Mach-O 64-bit arm64; `LC_BUILD_VERSION platform 2`, `minos 27.0` |
| Table-populated proof (census, not "it linked") | Entry `sub_00100008_0x100008` defined `T` (mangled `__Z21…`); **9445** `T …_0x…` game text symbols (≈9446 emitted); `g_ps2RecompiledFunctionTable` in `D` + Base/End/SlotCount in `S`; stub base `0x0` gone (generated base `0x100008` is the single definition — link would have failed on duplicates) |
| SDL count | 296 `T _SDL_` — identical to I9 (runtime slice unchanged) |
| Signature | `code object is not signed at all` (by toolchain design) |
| Identifier / CFBundleName | `org.ps2x.ps2entryrunner` / `ps2EntryRunner` (staged plist) |
| Build tree | `W/ios-runtime-device` 5.5G; `W` total 21G (sidecar purge freed ~9G ExFAT allocated: 9449 codegen + residual host-recomp `._*` → 0) |
| Build breaks fixed | NONE in wiring class beyond the host-side ExFAT purge (device compile+link clean first try) |

## Task 2 — Overwrite install + re-probe (iPad)

iPad: iPad Air 11-inch (M2) (`iPad14,9`), iPadOS 27.0, UDID `P`, connected (`logs/ipad-details.json`).

### iPad state before install (user sessions reported, not killed; our leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-install AND post-cleanup — no `Locked` failure |
| Running processes | 572-line list pre-install; 1 `ps2` match: PID 4088 = the I9 probe binary STILL RUNNING (same bundle UUID `A5148C04…` as I9's install; I9's cleanup had terminated 4076/4080 — 4088 postdates I9's session). Untouched before install (overwrite tested against a live occupant) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) |
| Post-brief state | Only OUR PIDs ever signaled (4125 via `process terminate` at cleanup; R1's PID via `--terminate-existing` on R2; 4088 reaped by the install itself); nothing else touched; post-cleanup grep = 0; app left installed (I10 build + ISO; MF1/I8/I9 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (installs 180/1200, launches 60/30/90, info 60/30) |

### Provision + sign + install (I9 mechanism reused; every delta tabled)

Profile: `f0793278-…` (XC Wildcard, team `LQ3V7772Q2`) — covers the iPad (I9 receipt, not re-probed). Identity: `295EFB42…` (Apple Development: Brad Richardson). Signed bundle keeps `org.ps2x.ps2entryrunner` (no rename).

| Step | I9 shape | I10 delta |
|---|---|---|
| Stage | `cp -R` unsigned `APP` → `SAPP` + `SLUS_207.72` pre-sign | identical for install 1 (sidecars 0 after purge); install 2 (Task 3 fix) adds `SSX3.iso` 3005415424 B as `SSX3.iso` pre-sign (`signed-app2/`) |
| Embed profile | `cp f0793278-*.mobileprovision SAPP/embedded.mobileprovision` | identical |
| Entitlements | 3 keys | identical bytes (`diff` clean vs I9's file) |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements`, on ExFAT | identical — exit 0 both bundles (19.8s for the 3 GB bundle), `codesign --verify --strict` exit 0 both |
| Install 1 (OVERWRITE TEST) | plain install on fresh target, exit 0 | **plain install on the OCCUPIED target: exit 0, clean replace** — new `installationURL …/B1611BC7-…/` (I9's was `A5148C04-…`), no error, no version dance, live occupant PID 4088 reaped BY the install (0 `ps2` after). I9 gap 3 closed: plain `install` overwrites |
| Install 2 (Task 3) | n/a | same plain mechanism, 3.1 GB bundle, exit 0 in 72s, new URL `…/4D96D6A2-…/` — second clean overwrite |

### Guest ELF + ISO on-device paths + presence

| Item | Receipt |
|---|---|
| Device paths | ELF `…/B1611BC7-…/ps2EntryRunner.app/SLUS_207.72` (R1/R2), ELF+`SSX3.iso` under `…/4D96D6A2-…/` (R3) (`logs/elf-device-path.txt`, `elf-device-path2.txt`) |
| Presence proof | App's own open (no `devicectl` bundle-listing domain, I9 receipt): no `Failed to open ELF file`; K1 arm names the file; R3 additionally proves ISO presence by BEHAVIOR (CD spin gone, IRX loads from `cdrom0:`) |
| ISO provenance | `/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso`, 3005415424 B, sha256 `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`, sector 16 = `CD001`, volume `SSX3` |

### Launches (argv probe; install 1, no CD image)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Launch | Shape | Result |
|---|---|---|
| R1 (real ELF, no image) | `--console`, `--timeout 60` + bundle ELF path | Exit 2 (timeout, app alive). Console (complete, 5272 lines; 77-line dedup): init identical to I9 → K1 arm → K1 `install#1–8` + `lookup#1–6` (guest syscalls dispatch) → **TEXTURE ID 3 (640x512) + ID 4 (512x128)** (guest-driven uploads; I9 never passed ID 2) → **`sceCdRead unresolved LBN 0x10 sectors=1`** ×1737 lines (30 full `[sceCdRead] unresolved request pc=0x3e3694 ra=0x3e3694 a0=0x10 a1=0x1 a2=0x519c80`, all IDENTICAL — guest spins one raw PVD read) → DPI spam until abort. **`missing-target` 0, `ee:idle` 0, open-fail 0.** No teardown, no exception, no `.ips` |
| R2 (repeat) | `--console`, `--timeout 30`, `--terminate-existing` (fresh PID 4120) | Exit 2 (timeout). 2661 lines; missing 0, idle 0, k1 15, cdread 879; dedup matches R1 modulo console-tearing fragments + timeout value. DETERMINISTIC |
| Screenshots | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed) | `i10-shot1.png`, 2360×1640: app window foreground (Stage-Manager, status bar names `ps2EntryRunner`), full-black content — same pixels as I9, different process state (guest executing) |
| Crash-log record | `systemCrashLogs -s ps2EntryRunner` → `0 files:` after sleep + re-`ls` (`logs/crashlog-check.log`) | No `.ips` on device across R1/R2 |

### Past-the-wall table vs I9

| I9 iPad fate | I10 fate (install 1) | Wall status |
|---|---|---|
| `missing-target` + `ee:idle` at `0x100008` (Dormant-at-entry, empty table) | `missing-target` 0, `ee:idle` 0; K1 installs + syscalls run; guest uploads textures; guest spins on `sceCdRead LBN 0x10` at pc `0x3e3694` | **I9 WALL GONE (H-a for gap 1)** — first guest function executes; NEW wall one layer up (CD/data, Task 3) |
| No guest syscalls (K1 arm only) | 8 installs + 6 lookups | guest dispatches |
| TEXTURE IDs 1–2 only | IDs 3–4 appear post-arm | guest GPU activity |
| Black window, scheduler idle | Black window, guest+loop alive | same pixels, new state |
| 0 `.ips` | 0 `.ips` | same |

## Task 3 — Diagnosis + config-level fix (fix attempted: ship ISO + launch env)

### Diagnosis round 1: failing layer = unmapped raw CD read (guest spins on PVD)

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest reads disc sector 16 (ISO PVD) raw and gets no data | `sceCdRead unresolved LBN 0x10` ×1737; every full request identical (`pc=0x3e3694`, 1 sector → `0x519c80`); first-to-last line identical → retry loop the whole run |
| 2 | Resolution order has exactly two data paths, both empty here | `readCdSectors` (`Support.h:437-482`): (a) `g_cdFilesByKey` file mappings — empty (no `sceCdSearchFile` lines; guest never path-resolves first); (b) `getCdImagePath()` = `ioPaths.cdImage` — empty (`PS2X_CD_IMAGE` unset) → falls to the `unresolved` line |
| 3 | No file shipment can satisfy a RAW LBN-16 read | `registerCdFile` assigns pseudo-LBNs from `kCdPseudoLbnStart = 0x100000` (`Support.h:7,22`) — true disc LBN 16 can never match a mapping; only a 2048-byte-sector image serves it |
| 4 | The host side is healthy throughout | Init/GL/audio OK; K1 + syscalls + texture uploads prove deep guest progress; no exception/teardown; 0 `.ips`; alive at both timeouts; deterministic R1/R2 |

### Fix candidacy (config-level only per the brief)

| Candidate | Class | Outcome |
|---|---|---|
| Ship files for path lookups | packaging, but impotent here | REJECTED by claim 3 (raw LBN read, pseudo-LBNs never match) |
| Ship CD image + `PS2X_CD_IMAGE` | packaging + flags — **IFF launch env exists** | `devicectl device process launch --help` HAS `-e/--environment-variables` (JSON dict) + `DEVICECTL_CHILD_` passthrough → **ATTEMPTED** |
| Derive `cdImage` from ELF dir / argv[2] / synthetic PVD | fork code | NOT attempted (code class, out of Task 3 scope) |
| On-device JIT / MAP_JIT | subsystem | NOT attempted — AOT decision table below |

### AOT-first decision (tabled either way per the brief)

| Option | Receipt | Decision |
|---|---|---|
| AOT link satisfies the table | 9445 game text syms in the slice; entry executes; guest runs ~90 s of boot (syscalls, textures, IRX loads) | **AOT SUFFICES — no JIT evidence either way against it** |
| JIT needed | No receipt: every observed wall is data/coverage class, never codegen-capability class | JIT stays OUT of scope |

### Fix attempt: `SSX3.iso` bundle resource + `-e '{"PS2X_CD_IMAGE":…}'` → R3

| Item | Receipt |
|---|---|
| Stage/sign/install | `signed-app2/`: ELF + `SSX3.iso` pre-sign; same profile/entitlements/identity; sign exit 0 (19.8 s), verify-strict exit 0; install exit 0 in 72 s, new URL `…/4D96D6A2-…/` (2nd clean overwrite) |
| R3 shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/4D96D6A2-…/ps2EntryRunner.app/SSX3.iso"}'` + argv ELF path → exit 2 (alive), 5276 lines, 75-line dedup |
| CD wall | **`sceCdRead unresolved` count = 0** — the spin is GONE; guest loads **12 IRX modules from `cdrom0:/data/modules/`** (dev9, usbkb, usbd, mcserv, mcman, snddrv, voipf, lgaud, drtysckf, libnet, msifrpc, pppoe); `[sif-handshake] sregs[1]=1`; 4 unhandled `[IOP/RPC trace]` (`sid=0x80000006 rpc=0xff`; `sid=0x237 rpc=0x0`; `sid=0x80000211 rpc=0x1`; `sid=0x534e44 rpc=0x0`) |
| Fix verdict at its layer | **SUCCESS — the CD/data wall is removed by packaging + flags alone** |
| Crash-log record | `0 files:` after sleep + re-`ls` (`logs/crashlog-check2.log`); no `.ips` |

### Diagnosis round 2: NEW wall = indirect-call target mid-function (`0x395730`)

| # | Claim | Evidence |
|---|---|---|
| 1 | Guest JALRs to an address with no table entry | `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x2322d4 target=0x395730 pc=0x395730 … codeRegion=yes policy=1` (exactly 1×; `ee:idle` 0 — scheduler keeps other threads) |
| 2 | The target is a coverage hole, not out of range | `0x395730` ∈ emitted range `0x100008–0x42e520` but: 0 refs in `register_functions.cpp`, no `*0x395730*` file, no CSV function in `0x395700–0x39573x` |
| 3 | Precise shape: mid-function entry missing | Emitted `sub_003956E8` spans `0x3956e8–0x395750` (contains `0x395730`); next emitted starts `0x395750` — the JALR lands 0x48 past a known entry with no label/entry for it (recompiler boundary/entry-discovery gap) |
| 4 | Class | Fork-code (recompiler coverage or runtime indirect-target fallback) — NOT config: no flag/plist/path/packaging change emits a function entry. No further fix attempted per the brief |

Fixes attempted: ONE (ISO + env — succeeded at its layer). No fork refactor, no new subsystems.

Contract outcome: **H-a for the I9 wall** (Dormant-at-entry gone — guest executes past `0x100008`); **H-b overall** (new wall past entry at `0x395730` + 4 unhandled RPC sids). The ONE next action: **fork-code brief — close the `0x395730` indirect-target gap** (split `sub_003956E8` at `0x395730` or add a mid-function entry + `entry_` wrapper via the Ghidra map/analyzer, re-run host `ps2_recomp`, re-link `ps2_game_objects`, re-probe with the ISO+env recipe) — app/fork-code class, not a device-harness brief.

## Exact commands

```sh
# --- Recon (E-lane owner = E6 live; shared clone read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i10"
git -C "$FORK" log --oneline -5; git -C "$FORK" worktree list
git -C "$FORK" ls-remote fork ssx3          # a13b66a (unchanged since I9)
git -C "$FORK" status --short               # M register_functions.cpp (E-lane uncommitted, 398779 lines)
git -C "$FORK" diff --stat                   # read-only peek only
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
# --- Task 1: worktree at pin + topic checkout ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I10/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" b6252bb
WT="$W/fork-wt"; git -C "$WT" fetch fork i8-device-bundle-name
git -C "$WT" checkout --detach 3006a07; find "$WT" -name "._*" -delete   # 327 -> 0
# --- Host ps2_recomp build (pin-built codegen tool) ---
cmake -S "$WT" -B "$W/host-recomp" -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF                    # exit 0 (241.8s+13.1s)
cmake --build "$W/host-recomp" --config Release -j2 --target ps2_recomp  # exit 2 (._* in _deps)
find "$W/host-recomp" -name "._*" -delete                            # 4890 -> 0
cmake --build "$W/host-recomp" --config Release -j2 --target ps2_recomp  # exit 0
shasum -a 256 "$W/host-recomp/ps2xRecomp/ps2_recomp"  # 511791795c16... (P1's: 7654e7fe..., unused)
# --- Host codegen ---
sed -e 's|^ghidra_output = .*|ghidra_output = "'"$WT"'/games/ssx3/ssx3-functions.sweep.csv"|' \
    -e 's|^output = .*|output = "'"$W"'/codegen-output/"|' \
    "$WT/games/ssx3/ssx3.toml" > "$W/ssx3-i10.toml"   # diff vs tracked toml = 2 lines
time "$W/host-recomp/ps2xRecomp/ps2_recomp" "$W/ssx3-i10.toml"     # exit 0, 6m34s
ls "$W/codegen-output" | wc -l                                       # 9449 (9447 cpp + 2 h)
shasum -a 256 "$W/codegen-output/register_functions.cpp"             # 2ca28d6f8f30...
shasum -a 256 "$W/codegen-output/ps2_recompiled_functions.h"         # ace7e72c8b4a...
shasum -a 256 "$W/codegen-output/ps2_recompiled_stubs.h"             # 5aa6553c0dd0...
# --- Fork edit (worktree only, named add, local commit, NO push: E-lane mutating) ---
# (edit ps2xRuntime/CMakeLists.txt: PS2X_GAME_CODEGEN_DIR option + stub drop + ps2_game_objects lib)
git -C "$WT" add ps2xRuntime/CMakeLists.txt
git -C "$WT" -c user.name="muse-i10" -c user.email="i10@local" commit -m \
  "Runtime: optional PS2X_GAME_CODEGEN_DIR game-objects static lib (I10)"  # 3d2e22d
# --- Device configure + build (I9 shape + game dir) ---
cp local/research/I9/logs/ios-device.toolchain.cmake "$W/logs/ios-device.toolchain.cmake"
export CC=/opt/homebrew/opt/llvm/bin/clang; unset CXX
cmake -G Xcode -DCMAKE_TOOLCHAIN_FILE="$W/logs/ios-device.toolchain.cmake" \
  -DCMAKE_CONFIGURATION_TYPES=Release -DPS2X_BUILD_RECOMP=OFF -DPS2X_BUILD_ANALYZER=OFF \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_SCCACHE=OFF \
  -DSDL2_DIR="/Volumes/Extreme SSD/ps2x-i8/sdl2-ios-device/lib/cmake/SDL2" \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB="/Volumes/Extreme SSD/ps2x-i4/raylib-5.5" \
  -DPS2X_GAME_CODEGEN_DIR="$W/codegen-output" \
  -S "$WT" -B "$W/ios-runtime-device"                              # exit 0 (49.7s+18.0s)
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # BUILD SUCCEEDED, 24m4.9s
APP="$W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app"
stat -f "%z %N" "$APP/ps2EntryRunner"; shasum -a 256 "$APP/ps2EntryRunner"  # a96268db1e2c...
nm -g "$APP/ps2EntryRunner" | grep -c " T .*_0x"                     # 9445 game text syms
# --- Task 2: recon + stage/sign/install + probe ---
xcrun devicectl device info details --device "$P" --timeout 60 --json-output "$W/logs/ipad-details.json"
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info processes --device "$P" --timeout 60   # 572 lines, PID 4088 = I9 leftover
SAPP="$W/signed-app/ps2EntryRunner.app"; rm -rf "$W/signed-app"; mkdir -p "$W/signed-app"
cp -R "$APP" "$SAPP"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP/SLUS_207.72"
find "$SAPP" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP/embedded.mobileprovision"
cp local/research/I9/logs/entitlements.plist "$W/signed-app/entitlements.plist"  # diff clean
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app/entitlements.plist" "$SAPP"     # exit 0
codesign --verify --strict "$SAPP"                              # exit 0
xcrun devicectl device install app --device "$P" --timeout 180 "$SAPP"   # exit 0 OVERWRITE
ELF="/private/var/containers/Bundle/Application/B1611BC7-61F5-48EF-A037-D0F92910A91A/ps2EntryRunner.app/SLUS_207.72"
xcrun devicectl device process launch --device "$P" --timeout 60 --console \
  org.ps2x.ps2entryrunner "$ELF" >"$W/logs/launch-realelf-console.log" 2>&1   # R1: exit 2 (alive)
xcrun devicectl device process launch --device "$P" --timeout 30 --console --terminate-existing \
  org.ps2x.ps2entryrunner "$ELF" >"$W/logs/launch-realelf2-console.log" 2>&1  # R2: exit 2, deterministic
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i10 -s ps2EntryRunner --no-recurse  # 0 files
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i10-shot1.png
mv /tmp/i10-shot1.png "$W/logs/"
# --- Task 3: ISO validation + fix install + env probe ---
ISO="/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"; stat -f "%z %N" "$ISO"  # 3005415424
dd if="$ISO" bs=2048 skip=16 count=1 2>/dev/null | dd bs=1 skip=1 count=5 2>/dev/null | xxd  # CD001
SAPP2="$W/signed-app2/ps2EntryRunner.app"; rm -rf "$W/signed-app2"; mkdir -p "$W/signed-app2"
cp -R "$APP" "$SAPP2"; cp "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72" "$SAPP2/SLUS_207.72"
cp "$ISO" "$SAPP2/SSX3.iso"; find "$SAPP2" -name "._*" -delete
cp ~/Library/Developer/Xcode/UserData/"Provisioning Profiles"/f0793278-*.mobileprovision \
  "$SAPP2/embedded.mobileprovision"
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements "$W/signed-app2/entitlements.plist" "$SAPP2"   # exit 0 (19.8s)
codesign --verify --strict "$SAPP2"                            # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP2"  # exit 0, 72s
B="/private/var/containers/Bundle/Application/4D96D6A2-BAF3-4AD0-B1F8-B792A12164C4/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-cdimage-console.log" 2>&1                        # R3: exit 2, cdread 0
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i10 -s ps2EntryRunner --no-recurse  # 0 files
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4125  # cleanup only
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| 1 | Indirect JALR target `0x395730` has no table entry (mid-function of emitted `sub_003956E8` `0x3956e8–0x395750`; no CSV function in `0x395700–0x39573x`) | `kind=IndirectCall op=JALR source=0x2322d4 target=0x395730` (1×, R3) + 0 refs in register + range census (Task 3 round 2) | Fork-code brief: add the `0x395730` entry (Ghidra map/analyzer boundary fix or recompiler mid-function entry splitting + `entry_` wrapper), re-run host `ps2_recomp` over `ssx3.toml`, re-link `ps2_game_objects` (`-DPS2X_GAME_CODEGEN_DIR`), re-probe with the ISO+env recipe (THE one next action) |
| 2 | 4 unhandled IOP/RPC sids (`0x80000006`, `0x237`, `0x80000211`, `0x534e44`) | 4 `[IOP/RPC trace:unhandled]` lines, R3 (guest continues past them today) | `ps2xIOP`-profile brief (only if gap 1's fix reveals them as blocking): implement handlers per the trace payloads |
| 3 | `3006a07` + `3d2e22d` unpushed (E-lane mutating; shared clone has uncommitted E-work) | Worktree log `3d2e22d^ = 3006a07`, 0 pushes; remote `ssx3` at `a13b66a` | No code brief — push/merge onto `fork/ssx3` (or a topic branch) when E6's line allows |
| 4 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest loaded `mcserv/mcman.irx` but never reached MC I/O | Data-container brief (only if a later probe fails on file I/O): ship ELF via `appDataContainer` + File Sharing or first-run copy-out |
| 5 | `PRODUCT_BUNDLE_IDENTIFIER` warning (I6–I9 carried) | Untouched this brief | Optional hardening brief (unchanged) |

## Receipt paths

- `local/research/I10/REPORT.md` (this file)
- `local/research/I10/logs/ios-device.toolchain.cmake` (byte-identical to I9's)
- `local/research/I10/logs/worktree-add.log`, `ios-runtime-configure.log` (full), `ios-runtime-build-tail.log`
- `local/research/I10/logs/ipad-details.json`, `ipad-apps-pre.log`, `entitlements.plist`
- `local/research/I10/logs/install.log` (overwrite, exit 0), `install2.log` (ISO bundle, exit 0, 72 s)
- `local/research/I10/logs/elf-device-path.txt`, `elf-device-path2.txt`
- `local/research/I10/logs/launch-realelf-console.log` (complete R1), `launch-realelf-dedup.log`, `launch-realelf2-dedup.log` (R2 determinism), `launch-cdimage-console.log` (complete R3), `launch-cdimage-dedup.log`
- `local/research/I10/logs/crashlog-check.log`, `crashlog-check2.log` (0 files after sleep + re-`ls`, both)
- `local/research/I10/logs/i10-shot1.png` (iPad window, black content)
- `W/logs/` (same + full R2 console, full build log, process lists, details stdout, codegen log, `ssx3-i10.toml`); `W/codegen-output/` (9449 files, build artifacts, uncommitted); `W/host-recomp/` (pin-built `ps2_recomp`); `W/ios-runtime-device/` (build tree); `W/signed-app/`, `W/signed-app2/` (installed bits); `W/fork-wt/` (worktree @ `3d2e22d`, clean, 1 local commit, 0 pushes)
- No fork push this brief (E-lane mutating — `3d2e22d` stays local until the line allows)

## What I could not do

- Present a guest frame — window stays black through IRX loading; first presented content awaits gap 1 (and possibly gap 2).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8/I9); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; ELF presence by the app's own open, ISO presence by behavior (CD spin → IRX loads).
- Test `mc0`/CD-write/file-I/O behavior — the guest never got that far (gap 4).
- Push `3d2e22d` — E6's line is live with uncommitted work (gap 3; local commit only).
- Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy).

## TAIL RECEIPT

Report written in 3 chunks (header + contract + Task 1 codegen/link; Task 1 build + Task 2; Task 3 + commands + gaps + receipts). Pre-receipt measure: 337 lines, sha256 `744151d18f2d21c1cf6ac148475abf1de823144bcfbe5d78d9c0bcde4e540dc3`.
Tail content line: "Explain the `mv` owner/group warning on the screenshot — ExFAT noise only; file landed byte-complete (read + pixel-verified from the landed copy)." This receipt line ends the report. END-I10-REPORT.
