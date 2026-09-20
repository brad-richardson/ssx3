# E3 report — Bounded read-only host-write audit (no boots; boots parked behind K1)

Brief: E3 poll brief (bounded read-only SPR/DMA/host-write audit). Tables, no verdicts.
Frontier steering recorded in E3-0 rec 5 + E3-3 (record table adopted verbatim for the recipe).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, read-only),
`OUT=$R/ps2xRuntime/src/runner` (9,262 `sub_*` recompiled files, read-only),
`RUN=$W/P1/run` (committed streams, read-only). `$R`-relative paths below unless noted.
No boots. No lease (none taken, none needed — zero emulator runs). No fork changes
(`git diff` untouched by E3; K1-lane working-tree content flagged, not modified).
No `adb`. No push.

Headline readings: the guest watch (`WRITE*` macros +
`PS2Runtime::Store*`) fires on every guest store, including scratchpad, and on
4 host paths that call `ps2DiagWatchReportDirect`; every other host path below
bypasses it (0 lines). SPR normal-mode transfers (`ps2_memory.cpp:1569-1625`,
`std::memcpy` both directions) are guest-triggerable with fully dynamic
MADR/SADR/QWC; 8 static CHCR=0x100/0x101 trigger sites exist, and the
window-executing hash loop `362DE8` / sibling `362CC8` reach them
(`362DE8→38F4F8→371D10` SPR_TO, `362CC8→38F738→371DD8` SPR_FROM); T26's own
committed park snapshot shows `371DD8` n=431,302 + `38F598` n=272,650 +
`38F460` n=301,496 — SPR fires hundreds of thousands of times inside the
window T26's watch cannot see. The RDRAM block `0x501420..0x501437` has 30+
bypass-capable arbitrary-pointer host writers (SIF/RPC/IOP, CD/file, LibC
shims with 48/15/175 static caller files, syscall result structs); the s1
scratchpad ranges add SPR_TO + every `getMemPtr`-class writer. Fixed-address
host writes (syscall mirror <0x80000, RPC/TLS/BootMode pools 0x01F00000+,
guest heap ⊆[0,0x1F00000], callback stacks [0x80000,0x100000], SSX3 sregs
0x52BE04, font 0x176148) cannot touch either target. `sceSifSetDma`, all
`sceVu0*`, have no trampoline in 9,262 runner files (unreachable);
`sceSifGetOtherData`/`sceDmaSend(N)` trampolines exist with 0 static callers.

## E3-0. Rule record + inputs

| # | Item | Value |
|---|---|---|
| 1 | ssx3 HEAD at E3 start/work/commit | `084fa2d` (evidence dir `local/research/E3/` standalone) |
| 2 | Fork HEAD (read-only) | `6359fb625e5651b53c696aadb6bc44ece88cb560`, branch `ssx3` (same as T26) |
| 3 | Fork working tree (read, not modified) | `M Syscalls/System.cpp` (+9: K1 hook), `M ps2_runtime.cpp` (+102: K1 frame-dump), `M runner/register_functions.cpp` (regenerated, foreign, pre-existing), `M ps2xTest/...kernel_tests.cpp` (+188), `?? Syscalls/Ssx3CopiedPayload.cpp` (K1, untracked). All `$R` line numbers below are working-tree numbers; K1-lane rows flagged K1 (absent from T26's binary) |
| 4 | Prerequisite reads | `local/research/T26/REPORT.md` (all; watch semantics T26-0 row 6, G1 one-skip/four-nonzero, routing-to-E3 row 3) + `local/research/A0/REPORT.md` §(ii-d) (20 B block writer gap G2; per-iteration copies `3634d4-534`/`377bd0-fc`) + `ps2_memory.cpp:1596/1598` SPR `memcpy` shape + `docs/research/review-2026-09-20-first-frame-and-gs.md` §E3 (record table + pointers, rec 5) |
| 5 | Frontier input recorded | (a) Start surface `ps2_memory.cpp:1569-1625` SPR_FROM/SPR_TO `std::memcpy` (done: path class A + trigger/call-graph tables). (b) Parked follow-up recipe MUST match the doc's record table (guest flag read+branch / guest write / SPR-DMA-host write / invocation boundaries — adopted as E3-3 rows R1-R4). (c) Do NOT force flag values in the recipe (E3-3 constraint C1). (d) E3 boots parked behind K1; one-or-two-frame order probe only if the same park survives (E3-3 gate G0) |
| 6 | Lease / boots / runs / fork writes / push | none / 0 / 0 / 0 / never run (static source reads + committed-stream greps only) |
| 7 | Committed streams mined (read-only) | `RUN/syscalls-t26-on.txt` (785,356 ev; key-syscall census), `RUN/boot-t26-1.log` (handshake/SendCmd counts), `RUN/park-t26-1/park-snapshot.txt` (hot_pc SPR/pad/LibC rows) |
| 8 | Wall | single session, inside the 4 h box |

Watch semantics (verified in fork source; the bypass boundary for every row):

| # | Mechanism | Receipt |
|---|---|---|
| 1 | Guest `WRITE8/16/32/64/128` macros fire `ps2DiagWatchReport` BEFORE the special-address check | `ps2_runtime_macros.h:356-434` (each macro: watch call, then `isSpecialAddress` branch) |
| 2 | Scratchpad is special, so guest SPR stores ALSO fire via `Store*` (second report) | `ps2_address.h:41-58` (`Ps2IsPhysicalSpecialAddress` incl. `PS2_SCRATCHPAD_BASE`); `ps2_runtime.cpp:2480-2571` (`Store8/16/32/64/128` each call `ps2DiagWatchReport`) |
| 3 | Window overlap test: emit iff `writeAddr < w+8 && w < writeAddr+width` per watched `w` | `ps2_runtime.cpp:1187-1228` (`diagWatchEmit`); T26's 83 windows cover `0x501420..0x501437` fully + 80 flag windows |
| 4 | Host paths fire IFF they call `ps2DiagWatchReportDirect`: exactly 2 call sites in `EeScheduler.cpp:1998,2720` (3 host writes covered: tick-zero, `writeGuestU32` + its 4 callers) | grep receipt `e3-greps.txt` §1 (0 hits in SIF/CD/DMA/FileIO/`ps2_memory.cpp`/all other Kernel files) |
| 5 | `getMemPtr`/`getConstMemPtr`/`getEeGuestStruct` resolve scratchpad via `ps2GetScratchpadHostPtr` | `ps2_memory.h:100-184`; `Syscalls/Common.h:40-86` (with bounds+alignment validation) |
| 6 | `ps2TraceGuestRangeWrite` (present on many host paths) is a SEPARATE trace channel, not the watch | e.g. `SIF.cpp:313,331`, `RPC.cpp` `rpcCopyToRdram`; emits 0 `[diag:watch]` lines |

## E3-1. Host-write path table

Reachability vocabulary (static/call-graph only): YES = static trigger path exists
(cited); NO = static barrier (cited); COND = gated (gates listed); DEAD = no
binding/dispatch in this build (cited). Watch column: FIRES = emits
`[diag:watch]`; BYPASS = 0 lines. Targets: `R` = `0x501420..0x501437` (RDRAM),
`S` = s1 flag ranges (`0x70000000`/`0x70001C00` +`0x10/+0x18` windows, SPR).
"Arb" = guest-controlled destination (can name either target).

### Class A — SPR/DMA engine (`ps2xRuntime/src/lib/ps2_memory.cpp`)

| ID | Site | Target | Trigger | Park-window reachability | Watch | Distinguishing observable |
|---|---|---|---|---|---|---|
| A1 | SPR_FROM `memcpy` `:1596` (SPR→RAM, QWC quads, wrap+ `MADR+=n/QWC=0/STR-clear/D_STAT CIS b8`) | R-arb (MADR dyn; `&PS2_RAM_MASK`, wraps at 32 MiB) | CHCR `@0x1000D000` write with STR (`&0x100`) + mode 0 (`(v>>2)&3==0`) + DMAC enabled + MADR/QWC/SADR set | YES: `362CC8→38F738→371DD8` (per-VBLANK sibling, 2 call sites); `3666F8` (exit-unwind fn)→`38F738`; park hot_pc `371DD8` n=431,302 ra=`0x38f758`, `38F598` n=272,650 (committed `park-snapshot.txt:105-111`) | BYPASS | New-hook record (E3-3 R3): MADR/SADR/QWC at trigger + before/after watched slice. Committed: hot_pc rows above; D_STAT CIS b8 set + `queueCompletedDmacCause(8)` → Dmac IRQ handler dispatch (guest code, fires) |
| A2 | SPR_TO `memcpy` `:1598` (RAM→SPR) | S-arb (SADR dyn `&0x3FFF`, wraps at 16 KiB) | CHCR `@0x1000D400` STR + mode 0 + DMAC | YES: `362DE8→38F4F8→371D10` (per-invocation hash loop itself, 2 call sites; `38F4F8:84` jal is straight-line after `:524`); SADR/MADR/QWC fully dynamic (`38F4F8`: a0=s1-p, a1=`38F460` ret, a2=s2>>4, a3=s3-p); park hot_pc `38F460` n=301,496 (38F4F8's callee ⇒ 38F4F8 ran ~301k×) | BYPASS | Same R3 record. Committed: `38F460`/`38F598` hot_pc rows; CIS b9. s1-overlap is SADR/QWC-dynamic ⇒ not statically excludable (E3-4 row 1) |
| A3 | SPR via `sceDmaSendN→submitDmaSend` (`Stubs/Helpers/Support.h:1343-1440`, chcr `0x181` mode-0 STR; SPR bases idx 8/9 in `kDmaChannelBases:1232`) | R/S-arb (same engine; SADR = whatever is programmed — Send path does NOT set SADR) | Guest `sceDmaSendN` with SPR chanArg | DEAD-direct: trampoline `0x3FE320` exists, 0 static caller files; indirect-only if at all | BYPASS | `[sceDmaSend]` RUNTIME_LOG (capped 64) + CIS b8/b9; absent from T26 boot log (see `e3-greps.txt` §7) |
| A4 | SPR via `sceDmaSend/SendI/SendM` (chcr `0x185` mode 1) | — | — | NO: SPR branch requires `sprMode==0` (`:1577`); chain-mode SPR unhandled (no copy, STR left set) | n/a | Non-path (verified by branch condition) |
| A5 | `403398` CHCR←0; `408988` CHCR←`0x105` (mode 1) | — | — | NO: no STR bit / mode≠0 | n/a | Non-paths (constant/mode analysis) |
| A6 | GIF/VIF0/VIF1 DMA (`writeIORegister:1309-1568`, `processPendingTransfers:1645-1843`, `ps2_vif1_interpreter.cpp:48-262`) | — (guest-mem READ-only: chain walk + `submitGifPacket`/`processVIF*` take `const` src; VIF writes land in VU mem; 0 `m_rdram/m_scratchpad` refs in `vu/`+`gs/`) | Guest CHCR STR on `0x10008000/9000/A000` | n/a (no guest-mem write exists) | n/a | Non-path. Counters: `m_dmaStartCount`, `m_gifCopyCount`, `[frame:upload]` |
| A7 | SIF0/SIF1 (`0x1000C000/C400`), IPU (`0x1000B000/B400`), SIF2 (`0x1000C800`) channels | — | CHCR writes fall through `writeIORegister` (only VIF0/VIF1/GIF/SPR branches exist) | NO: no emulation (P26-1h confirmed in source) | n/a | Non-path; observable = absence (no transfer, no log, STR never cleared by engine) |
| A8 | `submitDmaSend` to SIF/IPU channels | — | — | NO: same missing-handler fall-through | n/a | Non-path |
| A9 | VIF1_FBRST `:1221` (`memset(&vif1_regs,0,…)`) | — (host struct, not guest SPR) | `0x10003C10` RST bit | n/a | n/a | Non-path (address class) |
| A10 | EE timers/INTC/D_STAT/D_CTRL writes | — (IO regs + host state) | MMIO | n/a | n/a | Non-path |

SPR trigger-site constants (all `Store32` to SPR CHCR in 9,262 runner files; 10 sites):

| Game site | CHCR value | Fires engine? | Callers (direct, static) |
|---|---|---|---|
| `371D10` SPR_TO (`:153`, MADR←t0 SADR←a0&3FFF QWC←a2) | `0x100` const (`:149`) | YES | `38F4F8`, `38F708` |
| `371DD8` SPR_FROM (`:155`) | `0x100` const (`:149`) | YES | `38F598`, `38F738` |
| `3BC968` TO / `3BCA28` FROM (`:134` each) | `0x100` const (`:132`) | YES | TO←`3BD220`,`3BE6E0`(×4),`3BF0F0`(×4); FROM←`3BD220` |
| `3C4978` TO / `3C4A38` FROM (`:134` each) | `0x100` const (same shape) | YES | TO←`3C0A60`; FROM←`3C09B8`; both←`3C1638` |
| `408278` TO (`:358`) / FROM (`:476`) | `0x101`/`0x100` const (mode 0, STR) | YES | `4086C0`, `4087D0` (both); L2 `4032B8`, `407E90` |
| `403398:106` | `$zero` | NO | — |
| `408988:299` | `0x105` (mode 1) | NO | — |
| `382760` (`:898,942`) | `Load32` (poll only) | NO (reads) | steady VBLANK fn; no STR store |

### Class B — SIF/RPC/IOP host copies

| ID | Site | Target | Trigger | Park-window reachability | Watch | Distinguishing observable |
|---|---|---|---|---|---|---|
| B1 | `sceSifSetDma` (`Stubs/SIF.cpp:794-919`): `copyGuestByteRange` per desc (≤32, immediate) + Dmac cause 5 | R/S-arb (`isCopyableGuestAddress` incl. SPR `:216-237`) | Guest SetDma | DEAD: 0 refs to `SifSetDma` in 9,262 runner files (no trampoline) | BYPASS (trace `sifCopyGuestByteRange` only) | If wired: `[sceSifSetDma:CALL/DESC]` (aggressive-only) + cause-5 handler dispatch |
| B2 | `sceSifGetOtherData` (`SIF.cpp:552-630`): range copy + `rd+0x10/14/18` fields | R/S-arb | Guest GetOtherData | DEAD-direct: trampoline `0x4268F0`, 0 static caller files | BYPASS | Failure → `[drop] stub/sceSifGetOtherData`; else new hook (R3) |
| B3 | `sceSifSendCmd` live (`Syscalls/RPC.cpp:1060-1139`): `rpcCopyToRdram(destExtra←srcExtra,sizeExtra)` + fixed `0x52BE04←1` handshake (`cid==0x80000001`, sreg 1) | Arb part R/S; fixed part EXCLUDED (≠R, RDRAM-only) | Guest SendCmd; trampolines `0x426078` (1 caller file) + `0x4261B0` (8) | YES (9 caller files; T26 boot log: `[sif-handshake]`×2 + SendCmd×1, init line ~3706) | BYPASS | `[sif-handshake]` (cap 5), `[sceSifSendCmd]` (cap 5), park tally `op=sendcmd` + `claimed`, SIF RPC debug ring |
| B4 | `ps2_stubs::sceSifSendCmd` (`SIF.cpp:24-43`, direct `getMemPtr` loop, NO trace call) | R/S-arb (if wired) | — | DEAD: 0 callers (only B3 wired via `426078/4261B0`) | BYPASS | Non-path as wired; note: even `ps2Trace` absent here |
| B5 | `SifCallRpc→finishCall` (`Syscalls/RPC.cpp:651-682`): `rpcCopyToRdram(recvBuf←result/sendBuf)` or `rpcZeroRdram(recvBuf)` fallback | R-arb; S COND (copy engine SPR-capable via `getMemPtr`, but pack-selection heuristic `:432-470` requires `&0x1FFFFFFF < RAM_SIZE` — SPR `recvBuf` pack routing OPEN, gap G4) | Guest SifCallRpc; trampoline `0x426D18`, 20 caller files | YES | BYPASS (trace `rpcCopyToRdram`/`rpcZeroRdram`) | `SifRpcDebugEvent` ring (send/recv previews+sizes), park tally `op=call` (sid/fno/sizes/`claimed`), `[SifCallRpc]` clamp warnings |
| B6 | IOP HLE modules → `IopHostAdapter::writeGuest/zeroGuest` (`ps2_iop_host.cpp:155-199`): `clfile:82,297,541,548,582`, `cri_dtx:239,389,392,423,857,867,875,1039,1185,1187`, `dbcman:64`, `mcserv:245,248,262,265,319,344`, `sdrdrv:52` (+`tsnddrv`/`sound_update_stub`) | R-arb (+S via `guestRange→getMemPtr`) | Guest SifCallRpc routed to module SID | YES (same 20 caller files feed all SIDs; per-SID routing dynamic) | BYPASS (trace `IopHost::writeGuest/zeroGuest`) | Same RPC debug/tally + per-module logs |
| B7 | `SifBindRpc/RegisterRpc/Set/RemoveRpc(Queue)` (`RPC.cpp:301-404,792-1054`): client/server/queue struct writes to guest ptrs | R/S-arb | Guest Bind/Register | YES (same RPC callers) | BYPASS | RPC debug ring |
| B8 | `g_sifCmdHandlers` (`SIF.cpp:63,444,741`) | — | Add/Remove only; NEVER read for dispatch | NO (write-only map; P26-1h confirmed) | n/a | Non-path: no HLE SIF dispatch exists |
| B9 | SIF regs (`SIF.cpp:631-678,926-983`) | — (host-side `g_sifRegs/g_sifSregs` maps) | Set/GetReg/Sreg | n/a | n/a | Non-path (address class) |
| B10 | `AllocIopHeap/AllocSysMemory/Free*` (`SIF.cpp:448-535`) | — (host-side `g_sifHeapStorage` + zero-on-alloc) | Alloc | n/a | n/a | Non-path (IOP-heap mirror, not EE R/SPR) |
| B11 | `StopDma/SyncIop/WriteBackDCache/SetDChain/SetIopAddr` (`SIF.cpp:777-1006`) | — (return-constant no-ops) | — | n/a | n/a | Non-path (no store exists) |
| B12 | `SifLoadModule/LoadModuleBuffer` (`RPC.cpp:217-270`, `System.cpp:313-351`; trampolines `42B840/42B230`) | — (host-side ID tracker) | Module load | n/a | n/a | Non-path (no guest store); tally `op=load` |
| B13 | `runSifLoadElfPart` (`Syscalls/Helpers/Loader.h:224-470`): PT_LOAD→RDRAM (`rdram+phys`) or SPR (`getScratchpad()+off` iff vaddr∈SPR!) + BSS `memset` + `GuestExecData` struct to guest `execDataAddr` | R-by-ELF; S COND (SPR segment iff ELF says so); struct R/S-arb | Guest SifLoadElf/Part; trampolines `42BBD0/42BAA8` | YES (bindings exist; per-game ELF-dynamic) | BYPASS (0 `ps2DiagWatch` in `Loader.h`) | `[SifLoadElfPart]` RUNTIME_LOG (cap 16) + failure lines; follow-up re-checks post-K1 |
| B14 | `SifStopModule` (`RPC.cpp:182-216`): `*hostResult = known?0:-1` via `getMemPtr(resultAddr=a3)` | R/S-arb (4 B) | Guest StopModule | YES (same RPC surface) | BYPASS | Module `stop` log line |

### Class C — CD/file completion (all BYPASS)

| ID | Site | Target | Trigger | Park-window reachability | Watch | Distinguishing observable |
|---|---|---|---|---|---|---|
| C1 | `sceCdRead` success (`CD.cpp:269-415`, `tryRead→readCdSectors(lbn→rdram+offset)`) | R-only (`&PS2_RAM_MASK`; SPR buf values do NOT land in SPR) | Guest sceCdRead; trampoline `0x401DF8`, 3 caller files | YES (T26: `lbn=` boot-log lines 95-96 = init; window statically open) | BYPASS | `[diag:cd]` (diagPeriod-gated) + `queueCdCallback` → guest callback stores (those FIRE) |
| C2 | `sceCdRead` failure-zero (`:366-370`, `memset` zeros) | R-only (same mask) | Unresolvable LBN | YES (same callers) | BYPASS | `[sceCdRead] unresolved request` (cap 32) |
| C3 | `sceCdReadChain` (`:576-617`, per-entry `readCdSectors`) | R-only | Guest ReadChain | DEAD (no trampoline) | BYPASS | Non-path as built |
| C4 | `sceCdStRead` + `continueCdStRead` (`:830-1018`, stream `readCdSectors` + `errorOut` u32 via `getMemPtr`) | Data R-only; errorOut R/S-arb | Guest StRead | DEAD (no trampoline) | BYPASS | Non-path as built (synchronous in stub, no async thread write) |
| C5 | Small CD writers (bound): `GetToc` `:482-491` (1024 B zero, tramp `401FD8` 1 caller); `ReadClock` `:618-647` (8 B BCD wall-time, tramp `402520` 2 callers); `TrayReq` `:1090-1103` (u32 status, tramp `402618`) | R/S-arb (`getMemPtr`) | Respective stubs | YES | BYPASS | Values: zeros / BCD LSN / **host wall-clock BCD** (ReadClock — clock-shaped bytes are its signature) |
| C6 | Dead CD writers (no trampoline): `IntToPos`, `ReadChain`(C3), `StRead`(C4), `StStat` | — | — | DEAD | BYPASS | Non-paths as built |
| C7 | `fioRead` (`Syscalls/FileIO.cpp:178-256`, `fread(host file)→getMemPtr(bufAddr)`) | R/S-arb | Guest `read/sceRead` (Stubs/FileIO forward; syscall-dispatched) | YES | BYPASS (trace `fioRead`) | `fioOpen:` RUNTIME_LOG + fd/mode; bytes = host-file content |
| C8 | `fstat/stat` (`Stubs/FileIO.cpp:30-44,124-141`, 128 B zero to a1) | R/S-arb | Guest fstat/stat | YES (live libc-class stubs) | BYPASS | — (new hook R3) |
| C9 | `sceIoctl` cmd==1 (`Stubs/FileIO.cpp:74-102`, u32 `ready=0` to a2) | R/S-arb | Guest Ioctl poll | YES | BYPASS | HTCI-busy-poll shape (1→0 transition at polled addr) |
| C10 | MC `Chdir` (`MemoryCard.cpp:517-562`, cwd string to guest addr) + `GetDir` (`:697-843`, dir-table array to `tableAddr`) | R/S-arb | Guest MC calls | YES (same stub surface) | BYPASS | `[MC] Chdir/GetDir …` RUNTIME_LOG lines |

### Class D — syscall result writes (dispatch order: override → K1/drop/guest-invocation → HLE `switch`; `Dispatcher.cpp:106-110` + `System.cpp:422-461`)

| ID | Site | Target | Trigger | Park-window reachability | Watch | Distinguishing observable |
|---|---|---|---|---|---|---|
| D1 | VSync arm (`Syscalls/Interrupt.cpp:84-97` → `EeScheduler::setVSyncFlag:1974-2003`): `writeGuestU32(flag,0)` + tick-zero `memcpy` | R-only (`&0x1FFFFFFF` + RAM check; SPR addrs dropped with `sched/writeGuestU32` drop) | Syscall `0x73` (`Dispatcher.cpp:373`) | COND (armed): T26 trace `(73)`×0 (never issued in T26) — statically open, dynamically unarmed in T26 | FIRES (both: `:1998` Direct + `writeGuestU32:2720` Direct) | Trace `(73)` event + `[diag:watch]` line (host pc/ra/sp, thread = current) |
| D2 | VBlank tick (`EeScheduler::processEvent:2573-2583`): `writeGuestU32(flag,1)` + tick `memcpy:2579` (8 B `m_vsyncTick`); one-shot (addrs cleared) | R-only | VBlankStart event + D1-armed addrs | COND (follows D1; 0 firings in T26) | SPLIT: flag FIRES; tick BYPASS | Flag line present + 8 tick bytes changed with NO line = tick-bump signature |
| D3 | EvF wait wake (`EeScheduler:1671` immediate + `:2654` waiter wake, via `writeGuestU32`) | R-only | `WaitEventFlag` 0x56 | SHADOWED: `0x56→0xFFFFFFFF` override drops before HLE (`System.cpp:440-456`); live only if guest erases via `SetSyscall(0x56,0)`; T26 `(56)`×0 | FIRES | Trace `(56)` + watch line; drop line if shadowed |
| D4 | `PollEventFlag` (`Sync.cpp:300-336`, `*output=observed` direct) | R/S-arb (`getEeGuestStruct`) | `0x57` / i-variant `-0x58` | SHADOWED at `0x57` (same drop); LIVE via `iPollEventFlag` (`-0x58`, `Dispatcher.cpp:315`, unshadowed); T26 `(57)`×0 | BYPASS | Trace event; value = event-flag bits at poll |
| D5 | `ReferEventFlagStatus` (`Sync.cpp:338-375`, 28 B struct) | R/S-arb | `0x59` / `-0x5A` | SHADOWED `0x59`; LIVE `-0x5A`; T26 `(59)`×0 | BYPASS | Trace event; struct shape (attr/option/initBits/bits/waiters/0/0) |
| D6 | `ReferSemaStatus` (`Sync.cpp:150-180`, 24 B struct) | R/S-arb | `0x47` (NOT overridden) | YES; T26 `(47)`×0 | BYPASS | Trace `(47)`; struct shape (count/max/init/waiters/attr/option) |
| D7 | `ReferThreadStatus` (`Thread.cpp:342-376`, `ee_thread_status_t`) | R/S-arb | `0x30` (NOT overridden) | YES; T26 `(30)`×1 (trace line 212, t=1.38 s, init) | BYPASS | Trace `(30)`; zeroed-then-filled struct shape |
| D8 | `Copy` HLE (`System.cpp:987-1005`, `memcpy(dest←src,size)`) | R/S-arb | `0x5A` | SHADOWED → guest word-loop `0x42CB78` (guest stores FIRE); HLE live only if override erased; T26 `(5a)`×1 (installer self-copy → loop) | HLE BYPASS / loop FIRES | Trace `(5a)` + EITHER guest-loop store lines (loop) OR silent bytes (HLE) |
| D9 | `GetOsdConfigParam` (`System.cpp:94-120`, `*param=raw` u32) | R/S-arb | `0x4B` (NOT overridden) | YES; T26 `(4b)`×9 (trace lines 5-238, init) | BYPASS | Trace `(4b)`; value = OSD config word |
| D10 | `GetOsdConfigParam2` (`System.cpp:212-256`, ≤4 B) | R/S-arb | `0x6F` (`Dispatcher.cpp:358`) | YES | BYPASS | Trace `(6f)` |
| D11 | `GetRomName` (`System.cpp:257-283`, `strncpy "ROMVER 0100"`) | — | — | DEAD: no `Dispatcher.cpp` case (declaration only, `System.h:19`) | BYPASS | Non-path (no dispatch) |
| D12 | `GetThreadTLS→allocTlsAddr→rpcZeroRdram` (TLS pool `0x1F20000`, `State.h:258-261`) | EXCLUDED (fixed pool ≠R, RDRAM-only) | — | DEAD as syscall (no dispatch case) + address-excluded regardless | BYPASS | Non-path both ways |
| D13 | `QueryBootMode` pool (`0x1F30000`, `State.h:263-264`) | EXCLUDED (fixed pool) | BootMode query | Address-excluded | BYPASS (trace `rpcZeroRdram`) | Non-path (address class) |
| D14 | `SetupHeap` (`System.cpp:574-617`) | — (configures heap caps only; heap writes = G3) | `0x3D` | n/a | n/a | Non-path (no store); `[SetupHeap]` aggressive-only |
| D15 | Syscall mirror (`ps2_runtime.cpp:2685-2764`): `0x11F80+idx*4` + probe `0x2F0/0x2F8`, bounded `<0x80000` | EXCLUDED (`0x501420>0x80000`; RDRAM-only; SPR impossible) | `SetSyscall` 0x74 + `run()` init; T26 `(74)`×8 (installer, init) | Address-excluded (fires any time incl. window, still can't touch R/S) | BYPASS | Non-path (address class) |
| D16 | K1 `0x57`-helper zero×4 (`Ssx3CopiedPayload.cpp:137-152`, K1-UNCOMMITTED file): `writeGuestWord` ×4 to a1/a2/a3/t0 | R/S-arb (4×u32 zero) | Copied-payload dispatch (`System.cpp:445` K1 hook, K1-UNCOMMITTED hunk) | COND×3: K1 armed (`applySsx3CopiedPayload` at boot) + `handler==kPayloadDst+off` (T26: `0xFFFFFFFF` ⇒ no match) + guest issues `0x57` (T26: 0). Dormant in T26 config; conditional post-K1 | BYPASS (no watch, no trace) | `[k1] helper#… n=0x57 …` stderr lines; absent from T26 boot log |
| D17 | K1 lookup `0x5B` + `applySsx3CopiedPayload` (`Ssx3CopiedPayload.cpp:42-95`) | — (reads + flag set) | — | n/a | n/a | Non-path; `[k1] armed/lookup#` lines |

### Class E — stub result writes

| ID | Site | Target | Trigger | Park-window reachability | Watch | Distinguishing observable |
|---|---|---|---|---|---|---|
| E1 | `scePadRead` (`Pad.cpp:860-901`, 32 B pad state to a2 via `fillPadStatus:468`) | R/S-arb | Guest pad poll; trampoline `0x3FFA58`, caller files `326DF0`,`326EB0` (`326EB0` = E2a tripwire fn) | YES (per-frame poll loop statically; no window barrier) | BYPASS (trace `scePadRead`) | Value shape: `[1]=mode(Digi/DualShock) [2..3]=buttons(active-low) [4..7]=rx/ry/lx/ly`; `[padread]` aggressive-only |
| E2 | `scePadPortOpen` (`Pad.cpp:829-859`, 32 B zero to a2) | R/S-arb | Port open; trampoline `0x3FF708`, 2 caller files | YES | BYPASS (trace `scePadPortOpen`) | Zero block at dmaAddr |
| E3 | `scePadReqIntToStr/StateIntToStr` (`Pad.cpp:903-921,1000-1018`, ≤32 B strings) | R/S-arb | Guest str lookup | YES | BYPASS | String bytes at strAddr |
| E4 | `sceDmaGetEnv` (`DMA.cpp:57-66`, `0x14` B env to a0) | R/S-arb | Guest GetEnv; trampoline `0x3FE268` | DEAD-direct (0 caller files) | BYPASS | Non-path as built |
| E5 | `sceGsExecStoreImage` (`GS.cpp:674-762`, `consumeLocalToHostBytes(dst,…)` VRAM→guest) | R/S-arb (`getMemPtr`) | Guest StoreImage | DEAD (no trampoline) | BYPASS | Non-path as built |
| E6 | `sceGsSetDefDrawEnv(2)` (`GS.cpp:1036-1121`, env structs to envAddr) | R/S-arb | Guest SetDef | DEAD (no trampoline) | BYPASS | Non-path as built |
| E7 | GS pkt builds (`GS.cpp:628,727,828`) + Font pkts (`Font.cpp:47-65`) | EXCLUDED (`guestMalloc` heap ⊆[0,0x1F00000], class G3) | LoadImage/StoreImage/ResetGraph/eFontInit | Address-excluded | BYPASS | Non-path (address class) |
| E8 | VU0 math/copy (`VU.cpp`, ~40 `writeVu*` sites + `CopyMatrix/Vector(XYZ):369-407`) | — | — | DEAD: 0 `sceVu0*/sceVpu0*` refs in 9,262 runner files (entire class unbound) | BYPASS | Non-path (strong: no binding exists) |
| E9 | MPEG struct writes (`MPEG.cpp`: callback block `:1573`, `mpegGuestWrite32/64` `:1978-1990`, `sceMpegCreate:2064`, `GetPicture:2402`, `Reset:2524`) | R/S-arb (guest-handle-derived) | Guest MPEG calls; `sceMpegCreate` trampoline `0x4027B8` (1 caller file); GetPicture/Reset bindings OPEN (gap G5) | COND (Create YES; others pending binding check) | BYPASS | Callback-event word shape (streamType@0, dataAddr@8, len@0xC, pts@0x10, dts@0x18) |
| E10 | Font fixed writes (`Font.cpp:82-157`, `kFontBase=0x176148` + heap `glyphAlloc`) | EXCLUDED (fixed≠R; heap class G3) | eFontLoadFont | Address-excluded | BYPASS | Non-path; `GenerateString:228-503` has 0 guest stores (verified) |
| E11 | `mbtowc_r` (`Compatibility.cpp:90-119`, u32 to wcAddr) | R/S-arb | Guest mbtowc | DEAD (no trampoline) | BYPASS | Non-path as built |
| E12 | Audio/System/TTY/Deci2/IPU/Ssx3Movie stubs | — | — | n/a (0 `getMemPtr` + 0 `getEeGuestStruct` in all six files) | n/a | Non-path (verified no store exists) |
| E13 | `sceGsGetGParam` scratch read (`GS.cpp:1367-1376`, `memcpy(&gparam_val, scratch+0x100,8)`) | — (read-only) | — | n/a | n/a | Non-path (load, not store) |

### Class F — LibC host shims (`Stubs/LibC.cpp`, all `getMemPtr`-arb R/S, all BYPASS trace-only)

| ID | Site | Static caller files | Window note |
|---|---|---|---|
| F1 | `memcpy:90-131` (tramp `0x41605C`); `memmove:206-245` (`0x41610C`); `memset:132-169` (`0x416210`); `memclr:170-205`; `strcpy:272-296`; `strncpy:297-321`; `strcat:393-416`; `strncat:417-441`; `sprintf:565-624`; `snprintf:625-670`; `fread:765-790` (host file→guest) | `memcpy` 48, `memmove` 15, `memset` 175 (rest uncounted, gap G6) | YES statically (223 counted caller files; no window-func DIRECT use in `362DE8/363490/376938/362CC8` — window firing needs a window-executed caller; T26 precedent: init writer `3691F8` mixes guest stores + host `416210` in one function). Observable: trace `memcpy`/`sprintf` range writes + changed-bytes-without-watch-line at dst. Follow-up records shim entries (E3-3 R3h) |

### Class G — loader/init/heap/pools (time- or address-excluded)

| ID | Site | Why it cannot explain in-window R/S mutation |
|---|---|---|
| G1 | `PS2Memory::initialize:320-368` (full-RDRAM + full-SPR `memset`) | Boot-only (constructor path); pre-window. Covers both targets but T26's 17 init writes land after it |
| G2 | `PS2Runtime::loadELF:729-940` (PT_LOAD→RDRAM/SPR `:883` + BSS `:903`) | Boot-only (`loadELF` at startup); pre-window. Segment⊇`0x501420` check OPEN (gap G7; `readelf -l` command in E3-5) |
| G3 | Guest heap `guestCalloc/guestRealloc` (`ps2_runtime.cpp:2060-2130`) | Address: heap ⊆[0,`kGuestHeapHardLimit=0x1F00000`] (`:96` + clamp `:2016-2036` + SetupHeap cap `System.cpp:584`); `0x501420` outside; SPR impossible (`rdram+phys` only). Note: `guestCalloc` has NO watch AND NO trace call |
| G4 | RPC/TLS/BootMode pools (`State.h:249-264`: `1F00000/1F10000/1F20000/1F30000`) | Address: disjoint from R; RDRAM-only (`rpcZeroRdram`) |
| G5 | Async callback stacks (`ps2_runtime.cpp:2377-2415`, bounds `[0x80000,0x100000]` `:519-520`) | Address: disjoint from R/S; plus written by GUEST callback code (FIRES), not host — scheduler only sets `sp` |
| G6 | SIF IOP-heap zero (`SIF.cpp:allocateSifHeapBlock`) | Address class: host-side `g_sifHeapStorage` mirror, not EE R/SPR |

Mid-run scratchpad-clear search: NO path found (only G1 `:368` at boot; VIF/DMA resets touch host structs/IO regs, A9/A10). If s1 flags change without a guest line, the remaining SPR writers are A2/B5-partial/B13-partial/F1/C7-C10/E1-E3/E9 (each named above).

### Class H — host paths that FIRE (T26's zero constrains these on covered addrs)

| ID | Site | Coverage note |
|---|---|---|
| H1 | `writeGuestU32` + 4 callers (D1-flag, D2-flag, D3) | R-only; every write emits a line (`EeScheduler.cpp:2720`) |
| H2 | Tick-zero (`EeScheduler.cpp:1998`) | R-only; emits |
| H3 | Copy-via-guest-loop (`0x5A→0x42CB78`) | Guest stores; emit |
| H4 | Guest callback/invocation stores (CD/RPC/Dmac/alarm handler bodies) | Normal `WRITE*`; emit |

## E3-2. Exclusion table — what T26's "0 guest writes" CAN vs CANNOT exclude

CAN exclude (mechanism fires on these; 0 lines in-window ⇒ 0 such writes to covered bytes):

| # | Excluded class | Evidence |
|---|---|---|
| C-1 | All guest stores (`WRITE8/16/32/64/128` + `Store*`) to `0x501420..0x501437` during lines 276-6,764,707 | T26 writer table (17 init writes prove the mechanism sees R; 0 in-window) |
| C-2 | All guest stores to s1 flag windows (steady `0x70001C00+k*0x80`, ramp `0x70000000+…`) during the window (value flips; per-invocation stable rewrites seen) | T26 flag tables (6.2M lines prove the mechanism sees S; 0 value flips in-window) |
| C-3 | Host `writeGuestU32` family (H1: VSync flag arm/set, EvF immediate/waiter results) to covered R bytes | E3-0 rec 4 (Direct emit `:2720`); 0 matching lines in-window (any such line would name a host pc/ra/sp + thread) |
| C-4 | Host VSync tick-zero (H2) to covered R bytes | Same (`:1998` Direct) |
| C-5 | Copy-via-guest-loop + guest callback stores (H3/H4) to covered bytes | Guest-macro path (E3-0 rec 1-2) |

CANNOT exclude (each bypass path named; 0 lines is consistent with ANY activity here):

| # | Unexcluded path | Rows | Why T26 is blind to it |
|---|---|---|---|
| N-1 | SPR_FROM onto R (MADR-dynamic) | A1 (+A3 if called indirectly) | `memcpy` bypass; window-reachable from `362CC8`; 431k firings in T26's own run |
| N-2 | SPR_TO onto S (SADR-dynamic) | A2 (+A3) | Same; reachable from INSIDE `362DE8`; ~301k firings; SADR overlap not statically boundable |
| N-3 | SIF/RPC/IOP range copies + struct writes | B2,B3-arb,B5,B6,B7,B13,B14 (B1,B4 DEAD) | `copyGuestByteRange`/`rpcCopyToRdram`/`IopHost::writeGuest`/struct stores bypass; B3/B5/B6/B7/B13/B14 statically window-reachable |
| N-4 | CD sector data onto R | C1,C2 (C3,C4 DEAD) | `readCdSectors→rdram+offset` bypass; `401DF8` has 3 caller files |
| N-5 | CD/file/MC small + file-content writes onto R/S | C5(bound 3),C7,C8,C9,C10 | `getMemPtr`-class bypass each |
| N-6 | VBlank tick bump (8 B) onto R | D2-tick | `:2579` has NO Direct call (sibling flag write fires); gated on D1 arming (0× in T26 ⇒ also 0 ticks in T26 — but the BLINDNESS stands for any armed run) |
| N-7 | Syscall result structs/words onto R/S | D4(`-0x58`),D5(`-0x5A`),D6,D7,D9,D10 (D3-shadowed-fires; D8-shadowed-to-guest; D11/D12 DEAD; D15/D13/D14/G-pools address-excluded) | Direct/`getEeGuestStruct` stores bypass; `0x30/0x47/0x4B/0x6F` live; i-variants live |
| N-8 | Pad state/strings onto R/S | E1,E2,E3 | 32 B/polled-frame `getMemPtr` bypass; live callers `326DF0/326EB0` |
| N-9 | MPEG handle writes onto R/S | E9-partial (Create YES; GetPicture/Reset OPEN G5) | `mpegGuestWrite*` bypass |
| N-10 | LibC host shims onto R/S | F1 (11 functions; 223 counted caller files) | `::memcpy/::memset/str*` via `getMemPtr` bypass; init precedent (`3691F8→416210`) |
| N-11 | K1 `0x57`-helper zeros onto R/S | D16 | K1-working-tree-only; triple-gated; dormant in T26 (no `[k1] helper#` lines); live-conditional post-K1 |

"Immutable flags" / "neither SIF nor CD" (T26 routing row 3) exceed the
mechanism: N-1–N-11 are each consistent with T26's 0 lines. The SIF/CD
routing evidence (init-only guest pcs, pre-handshake timing, sync CD) stands
as evidence about GUEST-store causation, not about host-path exclusion.

## E3-3. Parked follow-up recipe (DEFINE ONLY — gated, not run)

Gate G0 (frontier steering): the follow-up boots ONLY IF the same park
survives K1. Constraint C1: DO NOT force flag values as part of the
observation. Scope: ONE complete invocation, expanding to at most one or two
guest frames when needed — NOT another long census. Pre-capture re-verify
(post-K1 tree may differ): override table contents, K1 dispatch state,
trampoline/binding deltas for rows marked DEAD/COND.

Record table (adopted from `docs/research/review-2026-09-20-first-frame-and-gs.md` §E3):

| Record (doc row) | Required fields | Hook (fork site, defined not installed) | Trigger | Caps + binds |
|---|---|---|---|---|
| R1. Guest flag read + branch | Monotonic event seq; guest frame; thread; PC/RA; actual `s1`; record index k; loaded halfword; branch outcome | Read-tap at `362DE8` halfword checks (`0x362f74-88`: `[s1+0x1E]` gate, `[s1+0x1C]`/`[s1+0x10..12]` compares, `jal 395000@0x363008` taken/skipped) + `s1` capture at `394ED0` entry (a1, T24-probe style) | `s1` in steady window AND invocation-counter == target (armed, not always-on) | Cap: 1 invocation (20 records ×~3 halfwords + 20 outcomes ≈ 80 rows) → ≤2 frames if the skip straddles; bind: `PS2X_E3_INV` (invocation index), `PS2X_E3_S1BASE` (expected steady base, checked not assumed) |
| R2. Guest write | Same seq domain; effective addr; old/new value | Extend `diagWatchEmit` (`ps2_runtime.cpp:1187`) with old-value load (pre-store read at `writeAddr`, width-aware) on the EXISTING 83 T26 windows (`watch-env.txt` verbatim) | Any overlapping guest `WRITE*`/`Store*` during the armed invocation(s) | Cap: same windows; rows bounded by observed guest traffic (~40/invocation for k=0..3 per T26 per-inv rates ×2 frames). Old-value read must precede the store it annotates |
| R3. SPR/DMA/host write | Src/dst; size; seq; small before/after slice of each overlapped watched window | R3a SPR: tap `writeIORegister` SPR branch (`:1569-1625`) logging MADR/SADR/QWC/DIR + 8 B before/after per overlapped window. R3b SIF/RPC: tap `copyGuestByteRange` (`SIF.cpp:275`), `rpcCopyToRdram/Zero` (`Runtime.h:44-120`), `IopHost::writeGuest/zeroGuest` (`ps2_iop_host.cpp:155-199`). R3c file/CD: tap `fread→hostBuf` (`FileIO.cpp:178`), `readCdSectors` call sites (`CD.cpp`), result-struct writers (D4-D10). R3d VSync tick `:2579`. R3e stubs: `scePadRead`, MPEG writers, `sceCdRead*`. R3f K1 helper D16 (if live post-K1). R3g CD callbacks (guest; covered by R2). R3h LibC shims F1 (entry log: dst/src/size at `41605C/41610C/416210` + str*). | Any tap whose `[dst,dst+size)` overlaps a watched window during the armed span | Cap: log ONLY overlapping transfers (window-intersection filter at each tap) + 8 B before/after slices (not whole ranges); byte cap per frontier disk section (abort past cap, keep partial). Binds: same `PS2X_E3_INV` + `PS2X_E3_BYTES` |
| R4. Invocation boundaries | Entry/exit seq; scratchpad/object identity | Entry/exit taps at `362DE8` bounds + `363490`/`376938` bounds + VBLANK tick (`m_vsyncTick`) + s1-base identity per invocation (a1 at each `394ED0` entry: ramp `0x70000000` vs steady `0x70001C00+k*0x80` vs other) | Function entry/exit dispatcher (existing `PS_LOG_ENTRY` plane, filtered to the 4 functions) | Cap: ≤2 invocations of boundary rows + 20 s1-identity rows per invocation |

Sequence domain: one `u64` counter shared by R1-R4 taps (guest + host), emitted
on every row; frame = VBLANK tick at row time; thread = `eeScheduler().currentThreadId()`.

## E3-4. What that capture would settle (that this audit cannot)

| # | Question | Decided by | Alternatives closed |
|---|---|---|---|
| 1 | Does any SPR_TO transfer overlap s1 flag bytes (`+0x10/+0x1C/+0x1E` of any live record) within the invocation? | R3a SADR/QWC rows ∩ R4 s1-identity rows | N-2: overlap ⇒ silent s1 mutation live; disjoint ⇒ SPR_TO excluded for s1 (this invocation) |
| 2 | Does any SPR_FROM transfer overlap `0x501420..0x501437` within the invocation? | R3a MADR rows | N-1 for R |
| 3 | Do the 4 apparently-nonzero records' addresses match the records actually READ (R1 `s1`/k/loaded-halfword) at each of the 20 lookups? (T26 G1 core) | R1 rows vs R4 s1-identity | Probe-attribution error vs genuine 4-nonzero state; read-vs-write order (R1 seq vs R2/R3 seqs) |
| 4 | Which `+0x1E`-nonzero record(s) does `395000` skip per invocation (1 vs 4)? | R1 branch outcomes (20/invocation) | Branch-count assumption vs flag-state contradiction (frontier: check this if host writes are absent) |
| 5 | Any in-window host write (R3b-R3h) overlapping R or live S bytes? | R3 rows (all taps) | N-3–N-11 each: a row ⇒ named writer; zero rows ⇒ all excluded for the captured span |
| 6 | Same address reused for a different object/iteration (SPR reuse across invocations)? | R4 s1-identity drift + R1 `s1` per lookup | Scratchpad-reuse alternative (frontier §E3 ¶3) |
| 7 | Post-K1 state: override table, K1-helper liveness, binding deltas? | Pre-capture re-verify block (G0) | D16 COND resolution; DEAD-row re-checks |

## E3-5. Exact commands (reads + greps; every SSD step with `export COPYFILE_DISABLE=1`)

From `/Users/bradrichardson/dev/ssx3` unless noted; `R="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"`, `RUN=/Volumes/Extreme\ SSD/ps2recomp-spike/P1/run` (quote paths with spaces):

```text
# Recon (read-only)
read local/research/T26/REPORT.md + local/research/A0/REPORT.md + docs/research/review-2026-09-20-first-frame-and-gs.md (§E3)
git -C . rev-parse HEAD; git -C "$R" rev-parse HEAD; git -C "$R" status --short; git -C "$R" diff --stat
sed -n '1560,1650p' $R/ps2xRuntime/src/lib/ps2_memory.cpp          # SPR block (frontier pointer 1)
grep -n "memcpy(m_rdram\|memcpy(m_scratchpad\|memset(m_rdram\|memset(m_scratchpad" $R/ps2xRuntime/src/lib/ps2_memory.cpp
sed -n '356,470p' $R/ps2xRuntime/include/ps2_runtime_macros.h      # WRITE macros (watch-before-special)
sed -n '1138,1270p' $R/ps2xRuntime/src/lib/ps2_runtime.cpp         # diagWatchEmit + Report/Direct
sed -n '2415,2600p' $R/ps2xRuntime/src/lib/ps2_runtime.cpp         # Store* (second report for special)
grep -c "ps2DiagWatchReport\|diagWatchEmit" $R/ps2xRuntime/src/lib/Kernel/Stubs/{SIF,CD,DMA,FileIO}.cpp $R/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp $R/ps2xRuntime/src/lib/ps2_memory.cpp  # §1 receipt
# Per-class surveys (all read-only; see report rows for line windows)
grep -rn "m_rdram\s*[\[+]\|m_scratchpad\s*[\[+]\|rdram\[" $R/ps2xRuntime/src/lib/ $R/ps2xRuntime/include/
grep -n "writeGuest\|m_rdram" $R/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
grep -n "getMemPtr\|memcpy\|memset" $R/ps2xRuntime/src/lib/Kernel/Syscalls/{Thread,Sync,System,RPC,FileIO,Deci2,Interrupt}.cpp
grep -n "getMemPtr\|memcpy\|memset" $R/ps2xRuntime/src/lib/Kernel/Stubs/{Pad,MemoryCard,GS,VU,LibC,Font,Compatibility,MPEG,Audio,System,TTY,Deci2,IPU,Ssx3Movie}.cpp
grep -rn "writeGuest\|zeroGuest" $R/ps2xIOP/src/
# SPR trigger + call-graph (OUT = fork runner/, 9,262 files)
grep -rln "0x1000D000\|0x1000D400" $R/ps2xRuntime/src/runner/                    # 16 files
grep -rn "Store32(rdram, ctx, 0x1000D000\|Store32(rdram, ctx, 0x1000D400" $R/ps2xRuntime/src/runner/  # 10 sites -> /tmp/e3_spr_stores.txt
grep -rln "func_371D10\|func_371DD8\|func_3BC968\|func_3BCA28\|func_3C4978\|func_3C4A38\|func_408278" $R/ps2xRuntime/src/runner/  # 11 L1 callers
grep -rln "func_38F4F8\|func_38F598\|func_38F708\|func_38F738\|func_3BD220\|func_3BE6E0\|func_3BF0F0\|func_3C09B8\|func_3C0A60\|func_4086C0\|func_4087D0" $R/ps2xRuntime/src/runner/  # 16 L2 (incl 362DE8/362CC8)
# Trampoline/binding checks (aporefs = trampoline; func_ = callers)
grep -rln "SifSetDma" $R/ps2xRuntime/src/runner/                               # 0 (B1 DEAD)
grep -rln "sceVu0\|sceVpu0" $R/ps2xRuntime/src/runner/                          # 0 (E8 DEAD)
for f in 426D18 426078 4261B0 4268F0 3FFA58 3FF708 41605C 41610C 416210 3FE320 3FE2B8 3FE268 401DF8 402520 401FD8 4027B8; do grep -rl "func_$f" $R/ps2xRuntime/src/runner/ | wc -l; done
grep -rln "sceCdStRead\|sceCdIntToPos\|sceGsExecStoreImage\|sceGsSetDefDrawEnv\|sceMpegCreate\|mbtowc_r\|sceSifLoadElf" $R/ps2xRuntime/src/runner/  # tramp2 set
grep -c "RomName\|ThreadTLS" $R/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp  # 0 (D11/D12 DEAD)
# Committed-stream observables (read-only)
for pat in "(73)" "(30)" "(47)" "(4b)" "(56)" "(57)" "(59)" "(5a)" "(74)"; do grep -c "Bios call: .* $pat" $RUN/syscalls-t26-on.txt; done
grep -c "sif-handshake" $RUN/boot-t26-1.log                                    # 2
grep -n "371d10\|371dd8\|38f4f8\|38f598\|38f708\|38f738\|38f460\|38f524" $RUN/park-t26-1/park-snapshot.txt  # 105/106/111
# Evidence
mkdir -p local/research/E3; write REPORT.md in 5 chunks; write e3-greps.txt; tail -3 local/research/E3/REPORT.md
git add -f local/research/E3/; git commit -m "[E3] ..." --trailer "Orchestrated-By: Muse Code"  # no push
```

## E3-6. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Indirect calls invisible to the static graph | DEAD-direct rows (B2,A3,E4) + all caller counts cover DIRECT `jal func_*` only; computed/indirect calls (vtables, function pointers like the `376938` indirect caller, A0 G2) could reach trampolines with 0 static callers. Follow-up R3/R4 would show the firing; statically OPEN |
| G2 | K1-lane drift | D16 + `System.cpp:445` hook + `ps2_runtime.cpp` frame-dump hunk are UNCOMMITTED working-tree content (E3-0 rec 3); post-K1 line numbers/content/bindings may move. G0 pre-capture re-verify covers it |
| G3 | Line numbers are working-tree numbers | Cite `$R` @ `6359fb6` + listed diffs; `ps2_runtime.cpp` K1 hunk (+102 @~376-560) shifts all later cited numbers vs HEAD |
| G4 | SifCallRpc SPR-recvBuf routing | `rpcCopyToRdram` engine resolves SPR, but the register/stack pack heuristic (`RPC.cpp:432-470`) prefers RAM-looking values; whether an SPR `receiveBuffer` survives pack selection was not traced end-to-end (B5 marked S-COND) |
| G5 | MPEG GetPicture/Reset bindings | `sceMpegCreate→4027B8` bound (1 caller); trampoline checks for `sceMpegGetPicture`/`sceMpegReset` (writers `:2402/2524`) not run (E9 COND). Command: extend the tramp2 grep pattern |
| G6 | LibC str*/fread caller counts | Only `memcpy/memmove/memset` counted (48/15/175); `memclr/strcpy/strncpy/strcat/strncat/sprintf/snprintf/fread` trampolines exist (same file) but caller files uncounted (F1). Same `func_` grep shape |
| G7 | Boot-ELF segment ⊇ `0x501420` | G2's pre-window coverage of R by a PT_LOAD segment not checked (`readelf -l $W/P1/SLUS_207.72 \| grep LOAD`). Decides whether G2 ever wrote R (still pre-window either way) |
| G8 | `sceCdTrayReq` caller count | Trampoline `402618` bound; caller files uncounted (C5). Same `func_402618` grep |
| G9 | i-variant trace naming | D4/D5 cite `-0x58/-0x5A` dispatch; exact `TraceChannel` spellings for negative ids not re-read (observable shape minor) |
| G10 | DWARF-free value provenance | SPR MADR/SADR/QWC + all arb-dst values are guest-dynamic by construction; no static bound attempted (that IS the follow-up's job, E3-4 rows 1-2) |
| G11 | Session wall | Single session inside the 4 h box; 0 boots/leases/runs by design |

## Evidence files

`REPORT.md` (this file), `e3-greps.txt` (key grep receipts: §1 watch-fire
sites, §2 SPR stores, §3 SPR callers L1/L2, §4 trampoline map + caller counts,
§5 binding-absence receipts, §6 T26 trace census, §7 boot-log counts, §8 K1
diff stat). Full-size artifacts stay on the SSD by path (never copied):
`syscalls-t26-on.txt`, `boot-t26-1.log`, `park-t26-1/park-snapshot.txt`.

## E3-7. Tail receipt

Report written in 5 chunks; closing 3 lines quoted verbatim below
(`tail -3 local/research/E3/REPORT.md` at commit):

```text
E3 evidence complete: host-write path audit + exclusion table + parked follow-up recipe (no boots).
Trailer: Orchestrated-By: Muse Code.
End of E3 report.
```

E3 evidence complete: host-write path audit + exclusion table + parked follow-up recipe (no boots).
Trailer: Orchestrated-By: Muse Code.
End of E3 report.
