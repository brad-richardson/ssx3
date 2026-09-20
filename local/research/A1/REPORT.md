# A1 report — Resolve G1: loader path vs HLE setup vs state dependency (dynamic reads, no config flips)

Brief `local/muse/prompts/A1.md`. Tables, no verdicts.
`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, read-only),
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `OUT=$W/P1/output` (recompiled,
read-only), `RUN=$W/P1/run`, `REF=/Volumes/Extreme SSD/ps2x-t4/emulog-boot3.txt`
(528 MB reference, read-only), ELF `$W/P1/SLUS_207.72` (read-only).
PCSX2 source: bytesize clone `/home/brad/pcsx2-t4/pcsx2` read via
`ssh bytesize "wsl …"` only (no builds).
No lease of any kind, no boots, no reference reruns, no fork changes, no builds, no `adb`.
Supersession note: this path previously held the 09-18 pre-publication audit
report (commit `c871824`); that file is preserved in this dir as
`REPORT-audit-2026-09-18.md` and in git history. This report is the G1 brief.

## A1-0. Rule record

| Item | Value |
|---|---|
| ssx3 HEAD at start | `b7a12f0` (`[orch] M62+T21+T22+A0+E2a gate reads…`, 2026-09-20) |
| Fork HEAD (read-only, `rev-parse`) | `6359fb625e5651b53c696aadb6bc44ece88cb560`; pre-existing `M ps2xRuntime/src/runner/register_functions.cpp` untouched (plus benign `._pack-*.idx` non-monotonic-index notices on macOS) |
| PCSX2 rev (via ssh, read-only) | `9056c08349cc29ad02a6d1a3a4133259019195af` (matches brief prefix) |
| Fork/OUT/ELF/REF writes | 0 (all reads read-only; scratch miners in `/tmp` only; reused `/tmp/a0_elf.py` from A0) |
| Lease / boots / reruns / builds / `adb` / push | none / 0 / 0 / 0 / unused / never run |
| Streams mined (committed/read-only) | `RUN/syscalls-t18-on.txt` (781,372 ev), `RUN/boot-t18-on.log` (518,344 lines), `REF` (899,714 post-`ExecPS2:2` EE Bios calls), `OUT` (9,278 files) |
| Wall | ~2.5 h of 4 h box, single session |

## Pins (paradox reproduced — or stop; reproduced)

### P1. Runtime opening events 1–26 (`syscalls-t18-on.txt` head)

PC/func join vs A0 (i-a)/(i-b). Counts over events 9–25: 8×`(74)` +
6×`(5b)` + 1×`(5a)` + 2×`(64)`; event 26 = post-`42C300` FlushCache.

| Ev | Time | Name (hex) | PC / source |
|---|---|---|---|
| 1 | 0.0000 | RFU060 (3c) | `0x100178` (`sub_00100008:324-327`) |
| 2 | 0.0000 | RFU061 (3d) | `0x100194` (`sub_00100008:347-350`) |
| 3–4 | 0.0001 | CreateSema (40) ×2 | `0x42c0f4`/`0x42c104` via `0x423DA0` |
| 5–8 | 0.0001–0.0003 | GetOsdConfigParam (4b), Set (4a), Get, Set | `0x42c3b4/d8/e0/e8` (`sub_0042C3A8`) |
| 9 | 0.0003 | RFU116/SetSyscall (74) | `0x42cbf8` (a0=`0x5A`, a1=`0x42CB78`) |
| 10 | 0.0003 | RFU090/Copy (5a) | `0x42cc10` via `0x42CB68` (dst `0x80075000`) |
| 11–12 | 0.0004 | FlushCache (64) ×2 | `0x42cc18` (a0=0), `0x42cc20` (a0=2) |
| 13–14 | 0.0004 | RFU116 (74) ×2 | `0x42cc2c` (a0=`0x5B`), `0x42cc38` (a0=`0x54`) |
| 15–25 odd | 0.0004 | RFU091/GetEntryAddress (5b) ×6 | `0x42cc48` loop ×5 + `0x42cc6c` (all drop) |
| 16–24 even | 0.0004 | RFU116 (74) ×5 | `0x42cc58` loop (a1=v0=`-1`) |
| 26 | 0.0004 | FlushCache (64) | `0x1001a0` (`jal func_424020`, a0=0) |

### P2. Reference zero counts (re-derived with `-E` end-anchored patterns)

Pattern shape (all receipts): `grep -cE "Bios call: .+ \(HEX\)$"`.
A0's printed BRE alternation was vacuous; every pattern below was run with `-E`.

| Window | EE Bios-call lines | (74) | (5b) | (5a) | (64) | (2f) | (40) | (4a) | (4b) | (3c) | (3d) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Post-`ExecPS2:2` (`tail -n +142465`) | 899,714 | 0 | 0 | 0 | 0 | 2 | 945 | 1 | 1 | 1 | 1 |
| Full file | — | 0 | 0 | 0 | 0 | — | — | — | — | — | — |
| Pre-142465 (`head -n 142464`) | — | 0 | 0 | 0 | 0 | — | 3 | 0 | 0 | 2 | 2 |

Reads: P1 matches the brief's event list exactly (order + counts);
P2 matches A0's `census-reference-patchpath.txt` on every cell.
`(64)=0` has a logging-artifact read (see R2 §Task 1, recSYSCALL row);
`(74)/(5b)/(5a)=0` have no such read (no skip path in source).

## Task 1 — loader path vs HLE setup (where do the paths fork?)

### R1. Reference-entry table (both `ExecPS2` windows + pre-context)

File lines from `REF` (`awk`/`grep -n`, receipts in §Commands).
"Head-consistent?" = whether the event could be the game entry head
(`0x100008` stream: RFU060 → RFU061 → CreateSema → …).

| File line | Log time | Event | Head-consistent? |
|---|---|---|---|
| 17–20 | 0.0360 | `(SYSTEM.CNF)` NTSC disc; `cdvdLoadElf(): 'cdrom0:\SLUS_207.72;1'` | — (mount metadata) |
| 22–23, 31–32 | 0.0378–0.0597 | GameDB init (12,841 games); `patches.zip` MISSING ("built-in game patches are not available"); `cheat` count 0 | cheat/patch bypass: no rows |
| 138641–138642 | 0.5503/0.5505 | RFU060 (3c), RFU061 (3d) — first pair overall, OSD phase | pair shape only (OSD's own init) |
| 139005/139260/139300 | 0.5583–0.5673 | CreateSema (40) ×3 (the pre-window `(40)=3`) | OSD context (360+ lines after the pair) |
| 142320 | 0.5716 | IOP `stdio.004: printf (1c93c, 100008, 15, 1fdbbc)` (a1=`0x100008`) | value equals game entry (undecoded format) |
| 142360/142361/142362/142368 | 0.5718–0.5719 | RFU005 (5), DeleteSema (41), _DisableDmac (17), RemoveDmacHandler (13) | loader teardown shape |
| 142369 | 0.5720 | `ExecPS2 (7)` #1 | issuer: non-game (game self-exec chain §B1 never fires pre-entry; runtime `(6)=(7)=0`) |
| 142370–142426 | 0.5721–0.5745 | IOP-only (`timrman`/`thevent`/`intrman` + microVU stall lines) | no EE event |
| 142427–142428 | 0.5762/0.5763 | RFU060 (3c), RFU061 (3d) | pair shape only |
| 142429–142464 | 0.5765–0.5995 | IOP-only (`thevent`/`intrman` pairs, no EE event) | 23 ms EE-quiet |
| 142465 | 0.5996 | `ExecPS2 (7)` #2 | issuer: non-game (same read as #1) |
| 142466–142533 | 0.6003–0.6079 | IOP-only (same pairs) | 9.4 ms EE-quiet |
| 142534–142535 | 0.6090 | RFU060 (3c), RFU061 (3d) | pair shape only |
| 142536 | 0.6092 | AddDmacHandler (12) | NOT head: head's 3rd event is CreateSema |
| 142537–142539 | 0.6093–0.6094 | _EnableDmac (16), sceSifGetReg (7a), sceSifSetDma (77) | SDK SIF-init shape |
| 142554–142559 | 0.6096–0.6098 | (7a), _DisableDmac (17), RemoveDmacHandler (13), sceSifStopDma (6b), (7a), (77) | SDK SIF-init shape |
| 142568–142571 | 0.6098 | sceSifSetReg (79) ×4 | SDK SIF-init shape |
| 142572–… | 0.6099–0.906 | sceSifGetReg (7a) storm: 260,722 in 142465..405064 | storm (F3 §19: ends 0.906) |
| 404828 | 0.9057 | Deci2Call (7c) (first) | post-storm marker |
| 404836 | 0.9062 | AddDmacHandler (12) #2 | second SIF setup |
| 405064 | 0.9073 | CreateSema (40) — FIRST post-window | 0.3 s after entry; thread-setup phase |
| 413025 | 0.9294 | CreateThread (20) — first post-window | helper thread (F3 §19) |
| 417354/417619 | 0.9375/0.9397 | IOP `modload.007: LoadStartModule` ×2 (the only two) | IOP-side; EE `(6)` count = 0 full-file |

Reads: `LoadExecPS2 (6)` = 0 full-file, `ExecPS2 (7)` = 2 (both pre-game);
`(null)` lines = 0. RFU060/061 appear as pairs in THREE phases
(OSD @138641, inter-window @142427, post-window @142534) — generic
SDK-program startup shape, not game-entry-specific. Neither window's
third EE event is CreateSema.

### R2. Loader-path source reads (PCSX2 @`9056c0834`, via ssh)

| # | Read | File:lines (bytesize clone) |
|---|---|---|
| 1 | `SYSCALL()` logs `BIOS_LOG("Bios call: %s (%x)")` BEFORE the switch; the format string occurs exactly once in `R5900OpcodeImpl.cpp` (`:917`) | `pcsx2/R5900OpcodeImpl.cpp:905-917` |
| 2 | `case Syscall::ExecPS2` (`:982-990`): debugger pause-on-entry hook ONLY, no `return` → falls through to `cpuRegs.pc -= 4; cpuException(0x20, …)` (`:1204-1205`) → the real BIOS handler runs | same file `:982-990`, `:1200-1205` |
| 3 | Between `ExecPS2` and the next EE event PCSX2 executes no loader logic of its own; the path is Sony BIOS code + the exec target's entry (pass-through) | R2-1 + R2-2 |
| 4 | `case Syscall::RFU060` (`:991-996`) EXTRAMEM tweak requires `a1==0xFFFFFFFF`; the game passes `a1=0x1FE0000` → inapplicable; early-`return` HLE cases (`GetOsdConfigParam2` @`:1040`, `GetMemorySize` @`:1191-1197`) are not on the entry path | same file `:991-996`, `:1040`, `:1191-1197` |
| 5 | `recSYSCALL()` (`iR5900.cpp:780-797`): when v1 is const `0x64`/`0x68` (FlushCache/iFlushCache) the JIT SKIPS the syscall with cycle compensation and NO `BIOS_LOG` line; all other numbers route to the logging `SYSCALL()` | `pcsx2/x86/ix86-32/iR5900.cpp:780-797` |
| 6 | T4 ran EErec (`iR5900` proven per numbers-ledger T4 row) and logged 899,714 other EE calls → `(64)=0` has a logging-skip read; `(74)/(5b)/(5a)=0` have none (R2-5 covers only `0x64/0x68`) | ledger + R2-5 |
| 7 | `bios[256]` names are non-null for `0x3C/0x3D` (RFU060/061), `0x54-0x5B` (incl. RFU090/091), `0x64` (FlushCache), `0x74` (RFU116) | same file `:84ff` (table head `:84`) |

### H1. HLE-setup table (runtime: what state exists at entry?)

| # | HLE call / log row | Args → returns / state established |
|---|---|---|
| 1 | `boot-t18-on.log:47-48` (strict pre-entry): `Loading segment: 0x100000-0x53eadc`; `Registered code region: 100000-4a4bf4` + `ssx3-sif-handshake` override + `ELF file loaded. Entry point: 0x100008` + `Starting execution at 0x100008` | mapping + entry jump only |
| 2 | `boot-t18-on.log:49-65`: `[diag:watch]` pc=`0x10012c` (bss loop), ra=`0x0` sp=`0x0`; `:66` trace channel opens (before first syscall) | bss-zero in progress at trace-open |
| 3 | SetupThread = game event 1 (`0x100178`; `Dispatcher.cpp:246-248` → `System.cpp:507-571`): a0=`0x4A30F0` (gp), a1=`0x1FE0000` (stack), a2=`0x20000` (size), a3=`0x4A5C00`, t0=`0x1001D0` | binds main ctx; gp set; sp=`0x1FE0000+0x20000`=`0x2000000`; `setupCurrentThread(0x1FE0000,0x20000,gp)`; returns sp → game `sp=v0` |
| 4 | SetupHeap = game event 2 (`0x100194`; `Dispatcher.cpp:249-251` → `System.cpp:573-615`): a0=`0x53F115`, a1=`0xFFFFFFFF` ("rest of RAM") | aligned base `0x53F120`; T18 log `:67`: `runtimeBase=0x53f120 runtimeEnd=0x53f120`; returns base (discarded by game). Current `configureGuestHeap` (`ps2_runtime.cpp:2206-2216`) clamps/normalizes — fork moved since T18 (`282ce92`→`6359fb6`), log values are T18 truth |
| 5 | InitAlarm (`0x42c318` → `42C7C8` 14-line stub → `Sync.cpp:392-395`) | returns `KE_OK`; establishes no state |
| 6 | InitThread (`0x42c320` → `424B78` 14-line stub → `Thread.cpp:183-186`) | returns `kMainThreadId`; establishes no state |
| 7 | ModuleLoad: 21 IRX (`SIO2MAN`…`VOIPF`, ids 1–21) — game-triggered via `(fc)` starting at runtime event 92 (0.0135); NOT pre-entry | reference contrast: 2 IOP `LoadStartModule` @0.9375/0.9397 |
| 8 | State-at-entry summary (runtime): thread-1 bound; sp=`0x2000000`; gp=`0x4A30F0`; heap base `0x53F120`; bss `0x4A4C00-0x53F115` zeroed (16 B stride); all GPR/FPU/hi/lo zeroed by prologue; COP0 untouched; interrupts disabled until `ei @0x1001a8` | prologue + H1-1..4 |

### F1. Fork table (earliest point the paths differ)

| Step | Runtime (event/time) | Reference window 1 (line/time) | Reference window 2 (line/time) |
|---|---|---|---|
| RFU060 | ev 1, 0.0000 | 142427, 0.5762 | 142534, 0.6090 |
| RFU061 | ev 2, 0.0000 | 142428, 0.5763 | 142535, 0.6090 |
| 3rd EE event (FORK) | ev 3 CreateSema, 0.0001 | 142465 `ExecPS2` #2, 0.5996 (after 23 ms EE-quiet) | 142536 AddDmacHandler, 0.6092 (+0.2 ms) |
| 4th EE event | ev 4 CreateSema | 142534 RFU060 (next window) | 142537 _EnableDmac |
| First CreateSema | ev 3 (0.0001) | 142427-pair: none follows | 405064 (0.9073) |
| First AddDmacHandler | ev 279 (1.4373) | — | 142536 (0.6092) |

Read: name-sequences match through RFU060/061 (reference side has no
PC/args — T18 G3/G4) and fork at the 3rd EE event in BOTH windows.

## Task 2 — avoidance mechanism (what skips the installer?)

### B1. Branch-hunt table (every conditional + indirect, entry → installer)

Scope: `sub_00100008` + `sub_0042C0D8` + `sub_0042C300` + `sub_0042C3A8`
+ `sub_0042C410` + `sub_0042CBC0` files + 7 wrapper files (`423DA0`,
`423E40`, `423E50`, `424020`, `42C340`, `42C350`, `42C398`) via per-file
control-flow grep (receipts in §Commands), plus `42C1F0`-real via ELF
disasm (`/tmp/a0_elf.py dis 0x42c1f0 75`, re-derived; joins A0 (i-f)).
True-byte control: ELF disasm of `0x100170-0x1001a4` matches the
recompiled stream (`jal 0x42c300 @0x100198`, `jal 0x424020 @0x1001a0`).

| # | PC | Disasm | Condition | Taken/not in runtime | Reference-divert value |
|---|---|---|---|---|---|
| 1 | `0x100140` | `bnez $at` → `0x10012c` | bss-zero loop (v0 `0x4A4C00`→`0x53F115`, step `0x10`) | loops, falls through | n/a (loop-only; sole exit is fall-through) |
| 2 | `0x42c428` | `beqz $v0` → `0x42c4a4` | `42C3A8` return == 0 (last OSD `Set` ret) | TAKEN (events 5–8 logged, block skipped) | non-zero v0 ADDS 3×`(74)`+1×`(5a)`+2×`(64)`+1 loop iter (moves away from reference zeros; gate is post-fork) |
| 3 | `0x42c49c` | `bnel $v0,$zero` → loop | skipped-block 1-iter loop (s2=2, `s2<3`) | not executed (inside B1-2 skip) | n/a |
| 4 | `0x42cc64` | `bnel $v0,$zero` → loop | installer s2 loop, 5 iters (s2=3..7) | 5 iters (events 15–24) | fewer iters would only trim loop rows, not zero the block |
| 5 | `0x42c364` / `0x42c388` | `beqz` / `bnez` | in `0x42c35c+` code (same file as the `42C350` wrapper, which ends `jr`; `0x42c360` = skipped-block Copy target) | not executed in runtime (no trace events) | off the fork segment; cannot produce RFU061→AddDmacHandler |
| 6 | `0x42c26c` / `0x42c278` / `0x42c2b0` | `beq s1,s0` → `0x42c2c0`; `beqz v0` → `0x42c298`; `bne s1,s0` → `0x42c278` | `42C1F0`-REAL converge loop (A0 (i-f)) | n/a (ret0-stubbed in runtime) | post-fork either way (`42C1F0` is called AFTER the first CreateSema) |
| 7 | — | `jr` ×7 (all files) | every `jr` is `jr $ra` (plain return); `jalr`: none; `j`/`jal`: all direct | — | no computed-jump divert exists |
| 8 | `0x1001a8` | `ei` | interrupts enabled AFTER installer returns (event 26 precedes it) | — | no IRQ diversion on the path, either side |
| 9 | — | wrappers (`423DA0/423E40/423E50/424020/42C340/42C398` + `42CBC0`-file trio) | straight `syscall`+`jr` (branch grep: zero conditionals) | — | — |

Skipped regions: none on the `0x100008`→installer segment (exhaustive
per §Commands). Post-installer (`0x1001a8+`: `jal 31AF80 @0x1001b8`,
`j 42C6E8 @0x1001c0`) out of scope except noted targets. Adjacent,
fires in NEITHER trace at boot: game self-exec chain
`256088→31B008→42C6A0→{4239E0 LoadExecPS2, 42C628}→42C628→4239F0 ExecPS2`
(wrappers `0x4239E0/0x4239F0` syscall-adjacent; sole callers
`42C6A0`/`42C628`; runtime `(6)=(7)=0`).

### S1. State-dependency table (registers/memory read before any write)

| # | Read (first consumer) | Runtime value | Could differ in reference? | Could it divert to the fork? |
|---|---|---|---|---|
| 1 | NONE on `0x100008-0x100170` (prologue writes only: GPR/FPU/hi/lo/`sq` bss-zero; `$zero`/immediates) | — | no read exists | no |
| 2 | RFU060 return → `sp` (`0x10017c`) | `0x2000000` (H1-3) | yes (real BIOS) | no consumer branches before CreateSema (`42C0D8` prologue writes only) |
| 3 | RFU061 return (`0x100194`) | discarded (`jal` next) | — | no (unread) |
| 4 | CreateSema returns (`0x42c0fc/0x42c10c`) | sema ids 1, 2 → stored `[0x455248]/[0x45524C]` | yes | no (stored, unbranched) |
| 5 | InitAlarm/InitThread returns (`0x42c318/0x42c320`) | `KE_OK` / main-tid (H1-5/6) | yes | no (discarded between jals) |
| 6 | OSD returns → `v0` → `beqz` B1-2 | 0 (taken) | yes (BIOS OSD bytes) | gate is POST-fork; untaken adds patch events (B1-2) |
| 7 | Installer table words `[0x456540..]` | ELF immediates (A0 (i-b)) | no (md5-matched bytes) | no |
| 8 | GetEntryAddress v0=`-1` passthrough (`0x42cc54`) | `-1` (6 drops) | n/a (installer unreached) | no |
| 9 | `42C1F0`-real KSEG0/`[0x455238..44]` scan reads | dead (stubbed) | yes (real table) | mark phase `(74)`×2 precedes any scan; reference `(74)`=0 excludes execution |
| 10 | Interrupt state (pre-`ei`) | disabled both sides (B1-8) | no | no |

Read: the RFU061→CreateSema segment (`0x100198`→`0x42c308`→`0x42c0f4`)
contains zero memory/register reads (S1-1..4) and zero
conditionals/indirects (B1-1..9) — no state exists on that segment
for any candidate to act through.

### V1. Verdict-shape table (no verdict — the shape per A0 candidate)

| Candidate | Reads for | Reads against | Settling dynamic experiment (brief-shape only, no execution) |
|---|---|---|---|
| Loader difference (different ELF / entry / stub runs post-`ExecPS2`) | fork at 3rd event both windows (F1); RFU pairs in 3 phases incl. OSD's own (R1) → pairs are not game-specific; SIF-init shape post-`ExecPS2:2` ≠ game head shape; PCSX2 runs no loader of its own (R2-3) so the target is whatever the BIOS execs (`a0`=entry, invisible in trace) | `BOOT2=cdrom0:\SLUS_207.72;1` (R1); no patches/cheats/pnach (R1, A0); md5-matched bytes (A0); open: how the reference reaches game main without the head | Reference run with `ExecPS2`-arg logging (`a0`=entry, `gp`) + RFU060/061 issuer-PC logging (debugger break or EE-args channel extension); receipt = per-window (entry, first-10-issuer-PCs) |
| HLE SetupThread/SetupHeap side effect | runtime HLE establishes sp/heap/thread (H1-3/4); real-BIOS values could differ (S1-2) | NOTHING on the RFU061→CreateSema segment reads HLE state (S1-1..4); InitAlarm/InitThread establish nothing (H1-5/6); no RFU non-return continuation exists on the segment (straight-line; next observed reference events are SIF-init) | Differential return-value read: real-BIOS RFU060/061 returns for the game's args (breakpoint at `0x10017c`/`0x100198` in a reference run) vs HLE (`0x2000000`/`0x53F120`); receipt = values + consumer-branch check (S1: none) |
| Unmodelled early state dependency | OSD-config bytes feed the only gate (S1-6); KSEG0/BIOS-table words feed `42C1F0`-real (S1-9) | both reads are POST-fork (CreateSema precedes them); zero reads pre-fork (S1-1..4); ELF immediates identical (S1-7); interrupts disabled (S1-10) | Paired snapshot diff at RFU061-return (reference vs runtime: KSEG0/BIOS table + stack + OSD bytes) intersected with the S1 read-set; receipt = diff words × consumers (S1 predicts empty divert-set) |

## Gaps (incl. kernel-true scanner premise — tabled, not decided)

| # | Gap | Needed by | Shape of the read |
|---|---|---|---|
| G1-a | Which ELF/entry each `ExecPS2` jumps to (`a0`=entry invisible: EE channel has no args/pc — T18 G3/G4) | loader-difference settler (V1) | `ExecPS2`-arg + issuer-PC logging run (brief-shape in V1) |
| G1-b | How the reference reaches game main without the entry head (installer `(74)`=0 full-file, yet boot reaches menu) | G1 remainder | follows G1-a (entry identity first) |
| G1-c | `(64)=0`: rec-skip (R2-5) vs never-issued — both predict zero; direct proof needs an interpreter-mode reference run (no JIT skip) showing `(64)`>0 | `(64)` pin strength | interpreter-mode rerun (not this brief: no reruns) |
| G1-d | Non-`addiu` v1=6/7 dataflow into the 84 syscall-site files (addiu-idiom sweep: 79 files, 3 contain syscalls, 2 true wrappers `0x4239E0/0x4239F0`; interprocedural v1 flow residual) | self-exec exclusion strength | dataflow sweep or runtime `(6)=(7)=0` + caller-chain rooting (done: `256088`-rooted) |
| G1-e | KERNEL-TRUE SCANNER PREMISE (F3 §20 rank 2, overridden shape): premise assumed a caller branch lets a kernel-true `42C1F0` return skip the patches. Tabled: A0 found no branch; A1 adds zero conditionals/indirects/reads on the RFU061→CreateSema segment (B1/S1) and the avoidance point at the 3rd EE event — BEFORE any `42C1F0` consumer could act (`42C1F0` is called after the first CreateSema). Premise survives only via [a branch both A0 and A1 missed] or [avoidance is non-game-code]. NOT decided | A1's successor | G1-a first; scanner build stays parked per brief |

## Commands + line refs (all read-only; `-E` throughout)

```text
# rule record
git -C "$R" rev-parse HEAD                                        # 6359fb6… (+M register_functions.cpp)
ssh bytesize "wsl git -C /home/brad/pcsx2-t4/pcsx2 rev-parse HEAD" # 9056c08349cc…
ls $W/P1/output | wc -l                                           # 9278
# pins: runtime head + reference zeros (end-anchored, -E)
head -26 $RUN/syscalls-t18-on.txt | cat -n                        # P1 events 1–26
tail -n +142465 $REF | grep -cE "Bios call: .+ \([0-9a-f]+\)$"     # 899714
for h in 74 5b 5a 64 2f 40 4a 4b 3c 3d; do tail -n +142465 $REF | grep -cE "Bios call: .+ \($h\)$"; done  # 0 0 0 0 2 945 1 1 1 1
for h in 74 5b 5a 64; do grep -cE "Bios call: .+ \($h\)$" $REF; done                      # 0 0 0 0
for h in 74 5b 5a 64 4a 4b 40 3c 3d; do head -n 142464 $REF | grep -cE "Bios call: .+ \($h\)$"; done  # 0 0 0 0 0 0 3 2 2
grep -n "ExecPS2" $REF                                            # 142369 + 142465
awk 'NR>=142369 && NR<=142465 && /Bios call: /' $REF              # 4 lines (R1)
awk 'NR>142465 && /Bios call: / {print NR": "$0; if (++c==22) exit}' $REF  # R1 post-window
awk 'NR<142369 && /Bios call: (RFU060 \(3c\)|RFU061 \(3d\)|CreateSema \(40\))$/' $REF      # 138641/42, 139005/60/300
awk 'NR>142465 && /Bios call: CreateSema \(40\)$/ {print NR; exit}' $REF                  # 405064
awk 'NR>142465 && /Bios call: CreateThread \(20\)$/ {print NR; exit}' $REF                # 413025
awk '/Bios call: Deci2Call \(7c\)$/ {print NR; exit}' $REF        # 404828
awk 'NR>142465 && /Bios call: AddDmacHandler \(12\)$/' $REF       # 142536 + 404836
awk 'NR>=142465 && NR<=405064 && /sceSifGetReg \(7a\)$/ {c++} END {print c}' $REF          # 260722
grep -cE "Bios call: .+ \(6\)$" $REF                              # 0 (LoadExecPS2)
grep -nE "SLUS|SYSTEM.CNF|BOOT2|LoadStartModule|cdrom0" $REF       # 17-20, 26, 417354/417619
grep -inE "gamedb|patch|cheat|widescreen|fastboot" $REF            # 22/23/31/32 only; cheat 0
grep -c "(null)" $REF                                             # 0
grep -n "1c93c, 100008" $REF                                      # 142320 (IOP printf a1=entry)
# PCSX2 source (ssh wsl only)
ssh bytesize "wsl sed -n '860,970p' …/pcsx2/R5900OpcodeImpl.cpp"  # SYSCALL head + BIOS_LOG
ssh bytesize "wsl sed -n '970,1080p' …"                           # ExecPS2/RFU060/OSD cases
ssh bytesize "wsl sed -n '1170,1250p' …"                          # switch tail + cpuException(0x20)
ssh bytesize "wsl sed -n '40,135p' …"                             # bios[256] table
ssh bytesize "wsl grep -rn 'Bios call' …/R5900OpcodeImpl.cpp"      # :917 only
ssh bytesize "wsl grep -rn recSYSCALL …/x86/ix86-32/iR5900.cpp"   # :780 + body (0x64/0x68 skip)
# OUT control-flow inventory (exhaustive)
for f in sub_00100008_0x100008 sub_0042C0D8_0x42c0d8 sub_0042C300_0x42c300 sub_0042C3A8_0x42c3a8 sub_0042C410_0x42c410 sub_0042CBC0_0x42cbc0; do grep -oE "// 0x[0-9a-f]+: 0x[0-9a-f]+ +(b[A-Za-z]+|j|jal|jalr|jr|syscall|break|eret|ei|di)( |$)" "$f.cpp"; done  # B1 (same loop rerun for the 7 wrapper files)
python3 /tmp/a0_elf.py dis 0x100170 40                            # true-byte control (entry)
python3 /tmp/a0_elf.py dis 0x42c1f0 75 | grep -E "bne|beq|jal|jr|syscall"  # B1-6
grep -rlnE "addiu[[:space:]]+\\\$v1,[[:space:]]+\\\$zero,[[:space:]]+0x0?[67]([^0-9a-fA-F]|$)" $OUT  # 79 files
grep -rln "func_4239F0" $OUT; grep -rln "func_4239E0" $OUT; grep -rln "func_42C628" $OUT; grep -rln "func_42C6A0" $OUT; grep -rln "func_31B008" $OUT  # self-exec chain (one pattern per run)
grep -rln "func_423AB0" $OUT; grep -rln "func_423AC0" $OUT         # SIF-init callers (362008 / 375A08+408DF0+409088)
# fork HLE (read-only) + boot log
grep -rn "SetupHeap" $R/ps2xRuntime/src/lib/Kernel/Syscalls/; grep -rn "0x3C" $R/ps2xRuntime/src/lib/Kernel/Syscalls/System.cpp  # H1-3/4
sed -n '500,629p' $R/…/Syscalls/System.cpp; sed -n '230,254p' $R/…/Dispatcher.cpp
grep -nE "Loading segment|Registered code region|Entry point|Starting execution|SetupHeap|trace:syscalls" $RUN/boot-t18-on.log  # :47/48/66/67
grep -c "SIF module" $RUN/boot-t18-on.log                         # 21
grep -nE "Bios call: .+ \(fc\)$" $RUN/syscalls-t18-on.txt | head -2  # ev 92 @0.0135
```

## Evidence inventory + tail receipt

Committed in this dir: `REPORT.md` (this file),
`REPORT-audit-2026-09-18.md` (the preserved prior report at this path).
Written in 4 chunks (`write_file` + 3 `edit_file` appends).

```text
$ tail -3 local/research/A1/REPORT.md
End of A1 report. Tables, no verdicts.
Evidence: REPORT.md + REPORT-audit-2026-09-18.md. Chunks: 4.
A1 tail receipt closes here.
```

End of A1 report. Tables, no verdicts.
Evidence: REPORT.md + REPORT-audit-2026-09-18.md. Chunks: 4.
A1 tail receipt closes here.
