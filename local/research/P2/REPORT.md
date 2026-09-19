# P2 report — PCSX2 reference for EE interrupt / alarm / CD-callback stacks

Read-only research. No builds, no boots, no emulator runs, no leases, no
`adb`, no edits outside `local/research/P2/`. Tables, no verdicts. Wall:
single session 2026-09-19 ~00:20 → 00:50 UTC, inside the 4-hour box.

Paths: `REF = /Volumes/Extreme SSD/pcsx2-ref` (PCSX2 source, unbuilt),
`FORK = /Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (branch `ssx3`,
read at `6046260`, never checked out / stashed / modified).

## P2-0. Inputs read

| Item | Value |
|---|---|
| P1 REPORT Part 5 (P1d) | `local/research/P1/REPORT.md` lines 2091–2803: sweep recompile, boot ladder (thread 2 on sema 26, thread 1 Dormant pc=0), Return-to-0 at `0x42cba8`, CD payload lines |
| P1 REPORT Part 6 (P1e) | Lines 2804–3067: thread-1 return-to-0 at `0x3dcc7c` (`sub_003DCBD8` epilogue, `sp=0x1ffff60`, trace ending `0x3e57f8 -> 0x3dcc64`), semaphore-26 table (26 creates, thread-2 park `waitId=26 pc=0x423de8`) |
| P1 REPORT Part 7 (P1f) | Lines 3068–3259: watchpoint names INTC cause-10 handler prologue (`0x3e4dc0/0x3e4dc8 sq`, thread -1, `sp=0x1fffed0`) overwriting ra slot `0x1ffff00`; fix `6046260`; boot-2 ladder (thread 1 Running at `0x391330`, threads 3/4) |
| P1f brief | `local/muse/prompts/P1f.md` (all of it): watchpoint + stack map, writer table, one fix |
| P1f fix | FORK `6046260` `Kernel: run INTC/DMAC/alarm handlers on reserved stacks, not thread sp` (full `git show` read; diff quoted in P2-3) |

## P2-1. Clone record

| Item | Value |
|---|---|
| Command | `git clone --filter=blob:none --depth 1 --no-recurse-submodules https://github.com/pcsx2/pcsx2.git "/Volumes/Extreme SSD/pcsx2-ref"` |
| Checkout | 2805 files, exit 0. ExFAT AppleDouble `._*.idx` sidecar noise (`error: non-monotonic index ...`) during fetch/checkout; non-fatal, log works |
| Rev | `1275b25ac02dc8138a0c43ec91bfc2c2df831f94` |
| `git log -1` | `1275b25ac02dc8138a0c43ec91bfc2c2df831f94 Tue Sep 15 12:30:30 2026 +0200 GS/GL: Remove extra fb attachment binding.` |
| No reuse | No prior clone existed at that path |
| Build | Never built (source only) |

## P2-2. Comparison table (one row per question)

Conventions: `REF/pcsx2/...` lines are PCSX2 @ `1275b25a`; `FORK/ps2xRuntime/...`
lines are PS2Recomp @ `6046260` (post-P1f). Decisive lines are quoted in P2-3.

| # | Mechanism | PCSX2 behavior + file:line | PS2Recomp behavior + file:line | P1f fix touches it? |
|---|---|---|---|---|
| 1 | INTC handler stack. Which stack runs an EE interrupt handler registered via `AddIntcHandler` (syscall `0x10`)? | CPU exception only; PCSX2 never writes `sp` on the delivery path. `hwIntcIrq` sets the `INTC_STAT` bit and nudges the event test (`Hw.cpp:103-107`); `_cpuEventTest_Shared` ORs `intcInterrupt()\|dmacInterrupt()` and calls `cpuException(mask)` when enabled (`R5900.cpp:362-374`, shared by interpreter and recompiler); `cpuException` writes `EPC`/`Cause`/`EXL` and sets `pc` to `0x80000000+0x200` (or `0xBFC00200+0x200` when `BEV`) (`R5900.cpp:95-166`). `SYSCALL()` has no `AddIntcHandler` case, so registration and handler invocation fall through `default:` to `cpuException(0x20)` into the real BIOS (`R5900OpcodeImpl.cpp:908-920,1200-1206`; handled set: `R5900OpcodeTables.h:10-26`). The `bios[0x10..0x13]` names are log-only (`R5900OpcodeImpl.cpp:84-95,917`). Regs: `INTC_STAT=0x1000F000`, `INTC_MASK=0x1000F010` (`Hw.h:304-305`). No PCSX2 source states which stack the BIOS handler runs on. | `AddIntcHandler` stores caller `gp`/`sp` with the registration (`Syscalls/Interrupt.cpp:26-40` → `EeScheduler::addIrqHandler`, `EeScheduler.cpp:1452-1480`; `EeIrqHandler.sp`, `ee_scheduler.h:168-178`). `dispatchIrq` builds an `Interrupt` invocation (`pc`=handler, `a0`=cause, `a1`=arg, `gp`, `ra`=0) with `sp=0` (`EeScheduler.cpp:1545-1560`). Both `run()` dequeue sites assign `invocationStackTop()` when `sp==0` (`EeScheduler.cpp:405-408,498-501`). `invocationStackTop()` keys `(threadId,depth)` → `reserveAsyncCallbackStack(0x4000)` (`EeScheduler.cpp:1426-1450`), which hands down from `0x100000` with floor `0x80000` (`ps2_runtime.cpp:2193-2229`; inits `ps2_runtime.h:521-525`). | Yes. `6046260` changed `dispatchIrq` `sp` from `handler.sp` to `0u` and moved the reserve region from the RAM top to `[0x80000,0x100000)`. |
| 2 | Alarm stack. `SetAlarm` (syscalls `0x18`/`0xFC`) callback context and stack. | No alarm model. Zero `alarm` hits in `Counters.cpp`/`Counters.h`/`Hw.cpp` (searched); the `Syscall` enum has no `SetAlarm` (`R5900OpcodeTables.h:10-26`); `bios[0x18]` = `"_SetAlarm"` is a log name only (`R5900OpcodeImpl.cpp:94,917`); falls to `cpuException(0x20)` → the real BIOS owns the alarm queue, context, and stack. No PCSX2 source states the alarm stack. | `SetAlarm` stores ticks/handler/arg/`gp`/caller-`sp` (`Syscalls/Sync.cpp:333-342` → `EeScheduler::setAlarm`, `EeScheduler.cpp:1329-1351`; `EeAlarm.sp`, `ee_scheduler.h:158-166`). The `Alarm` event builds an `Alarm` invocation (`a0`=id, `a1`=ticks, `a2`=arg, `gp`, `ra`=0) with `sp=0` (`EeScheduler.cpp:2195-2217`); stack comes from `invocationStackTop()` at dequeue (same path as Q1). Dispatcher accepts both `0x18` and `0xFC` (`Syscalls/Dispatcher.cpp:158-173`). | Yes. Same commit: `alarm.sp` → `0u` + shared region move. |
| 3 | CD callback thread. `sceCdInitEeCB` / `sceCdCallback`: stack address/size, owning thread, PCSX2 model. | No EE-side model. Zero source hits for `sceCdInitEeCB`/`InitEeCB`/`EeCB` across all PCSX2 `.cpp`/`.h` (searched). The only `sceCdCallback` hit is IOP module `cdvdman` export #37 in the debugger name table (`IopModuleNames.cpp:9,29`), consumed only via `irxImportFuncname` (`IopBios.cpp:1311-1313`). All `CDVD/` "callback" hits are host-side (`CDVDcommon.h` `ProgressCallback`/`newDiscCB`). CD completion reaches the EE as a hardware IRQ (`Hw.cpp:103-107` path) into BIOS + guest libcdvd code. | `sceCdInitEeCB` records `g_cdCallbackStackTop = a1(stack)+a2(size)` (`Stubs/CD.cpp:494-508`); `sceCdCallback` records fn + `gp` (`Stubs/CD.cpp:440-448`); `queueCdCallback` builds an `Interrupt`-kind invocation on `g_cdCallbackStackTop` (`Stubs/CD.cpp:66-88`). Boot value `0x51a480+0x800 = 0x51ac80` (P1 P7-1). No thread is created; the invocation runs on whatever context dequeues it, or on an ephemeral id<0 thread (`EeScheduler.cpp:388-410`; `acquireInvocationThread`, `EeScheduler.cpp:1851-1867`) — the P1 Part 6 `id=-1` dormant lines. | No. Untouched: `sp` stays nonzero so dequeue keeps the game-supplied stack. |
| 4 | Async / SIF RPC callbacks. Where SIF RPC server threads and other async callbacks get stacks. | SIF is DMA FIFOs only: `sifData`/`sifFifo` (`Sif.h:12-52+`); `Sif.cpp` holds only reset + savestate; `Sifcmd.h` holds only `t_sif_dma_transfer` (`Sifcmd.h:6-12`); zero `rpc` hits in `Sif.cpp`/`Sif0.cpp`/`Sif1.cpp`/`sif2.cpp`/`Sif.h` (searched). The `sceSifSetDma` syscall case is log-only (`R5900OpcodeImpl.cpp:1102-1125`). IOP HLE intercepts IRX imports synchronously in the calling IOP thread (`irxImportHLE` loadcore/sysmem/ioman, `IopBios.cpp:1346-1370`; `irxImportExec`, `IopBios.cpp:1423-1442`; `host:` root, `IopBios.cpp:84-94`) — no EE stacks created. RPC server-thread stacks are guest BIOS/module behavior. | RPC server dispatch and RPC completion callbacks are built as `RpcCallback` invocations with `sp = invocationStackTop()` directly (`Syscalls/RPC.cpp:662-673,678-692`) — the same reserved region as Q1/Q2. | Partially. No `RPC.cpp` change; the shared `reserveAsyncCallbackStack` region move covers these stacks. |
| 5 | EE kernel reserved area. What `0x00000000-0x000FFFFF` holds; is any of it free to borrow? | 32 MB MainRam (`MemoryTypes.h:9`); physical-RAM window comment (`Memory.cpp:4-23`). `R5900.h:293-297`: `// modules loaded at hardcoded addresses by the kernel / EEKERNEL_START = 0; EENULL_START = 0x81FC0; EELOAD_START = 0x82000; EELOAD_SIZE = 0x20000; // overestimate for searching`. Fast-boot hooks read live BIOS code at `EELOAD_START+0x470..0x618` (`Interpreter.cpp:622-640`). Kernel code pattern is scanned at `0x80000000+0x0..0x5000` (`"instructions are in between 0x4000 -> 0x5000"`), thread list derived near `0x80010000` (`R5900OpcodeImpl.cpp:1065-1092`); the debugger reads the EE kernel thread array (`stackMem`/`stackSize`/`regCtx` fields) there (`BiosDebugData.cpp:9-27`; `BiosDebugData.h:33-55`). No PCSX2 source or `Docs/` file declares any low-RAM subrange free (checked `Docs/` listing: config guide, FAQ, GameIndex — no kernel-RAM doc). | P1f borrows `[0x80000,0x100000)` for invocation stacks (`ps2_runtime.h:521-525`; ctor + `loadELF` reset in `ps2_runtime.cpp` per the `6046260` diff). Rationale recorded in P1 P7-3: below the ELF `PT_LOAD` (`vaddr 0x100000`), below the guest heap base, away from thread/CD stacks. | Yes — this region IS the P1f change (moved off the RAM top). Reference tension noted in P2-4 (no verdict). |

## P2-3. Evidence quotes (decisive lines, from files opened)

### Q1 — PCSX2 interrupt delivery

`REF/pcsx2/Hw.cpp:57-77,103-107`:
```cpp
__fi uint intcInterrupt()
{
	if ((psHu32(INTC_STAT)) == 0) {
		//DevCon.Warning("*PCSX2*: intcInterrupt already cleared");
		return 0;
	}
	if ((psHu32(INTC_STAT) & psHu32(INTC_MASK)) == 0)
	...
	//cpuException(0x400, cpuRegs.branch);
	return 0x400;
}
...
void hwIntcIrq(int n)
{
	psHu32(INTC_STAT) |= 1<<n;
	if(psHu32(INTC_MASK) & (1<<n))cpuTestINTCInts();
}
```

`REF/pcsx2/R5900.cpp:360-374` (shared interpreter/recompiler event test):
```cpp
// Shared portion of the branch test, called from both the Interpreter
// and the recompiler.  (moved here to help alleviate redundant code)
__fi void _cpuEventTest_Shared()
{
	...
	uint mask = intcInterrupt() | dmacInterrupt();
	if (cpuIntsEnabled(mask))
		cpuException(mask, cpuRegs.branch);
```

`REF/pcsx2/R5900.cpp:95-116,139-163` (`cpuException`; no register touched
except `Cause`/`Status`/`EPC`/`pc`):
```cpp
__ri void cpuException(u32 code, u32 bd)
{
	...
	cpuRegs.CP0.n.Cause = code & 0xffff;
	...
		else if ((code & 0x7C) == 0x0)
			offset = 0x200; //Interrupt
	...
	if (cpuRegs.CP0.n.Status.b.EXL == 0)
	{
		cpuRegs.CP0.n.Status.b.EXL = 1;
		if (bd)
		{
			Console.Warning("branch delay!!");
			cpuRegs.CP0.n.EPC = cpuRegs.pc - 4;
			cpuRegs.CP0.n.Cause |= 0x80000000;
		}
		else
		{
			cpuRegs.CP0.n.EPC = cpuRegs.pc;
			cpuRegs.CP0.n.Cause &= ~0x80000000;
		}
	}
	...
	if (checkStatus)
		cpuRegs.pc = 0x80000000 + offset;
	else
		cpuRegs.pc = 0xBFC00200 + offset;
```

`REF/pcsx2/R5900OpcodeImpl.cpp:908-920` + `1200-1206` (EE `SYSCALL()`;
`AddIntcHandler`/`_SetAlarm` are names only, everything unhandled traps to
the BIOS):
```cpp
void SYSCALL()
{
	u8 call;
	if (cpuRegs.GPR.n.v1.SL[0] < 0)
		call = (u8)(-cpuRegs.GPR.n.v1.SL[0]);
	else
		call = cpuRegs.GPR.n.v1.UC[0];
	BIOS_LOG("Bios call: %s (%x)", R5900::bios[call], call);
	switch (static_cast<Syscall>(call))
	...
	default:
		break;
	}
	cpuRegs.pc -= 4;
	cpuException(0x20, cpuRegs.branch);
}
```

`REF/pcsx2/R5900OpcodeImpl.cpp:84-95` (name table) and `:917` (only use
besides one more log line at `:1120`):
```cpp
const char * const R5900::bios[256]=
{
//0x00
	"RFU000_FullReset", "ResetEE",				"SetGsCrt",				"RFU003",
	...
//0x10
	"AddIntcHandler",	"RemoveIntcHandler",	"AddDmacHandler",		"RemoveDmacHandler",
	"_EnableIntc",		"_DisableIntc",			"_EnableDmac",			"_DisableDmac",
	"_SetAlarm",		"_ReleaseAlarm",		"_iEnableIntc",			"_iDisableIntc",
```

`REF/pcsx2/R5900OpcodeTables.h:10-26` (the only EE syscalls PCSX2
special-cases; `StartThread`/`ChangeThreadPriority` only scan for the BIOS
thread-list pattern for the debugger):
```cpp
enum Syscall : u8
{
	SetGsCrt = 2,
	ExecPS2 = 7,
	SetVTLBRefillHandler = 13,
	StartThread = 34,
	ChangeThreadPriority = 41,
	RFU060 = 60,
	SetOsdConfigParam = 74,
	GetOsdConfigParam = 75,
	SetOsdConfigParam2 = 110,
	GetOsdConfigParam2 = 111,
	sysPrintOut = 117,
	sceSifSetDma = 119,
	Deci2Call = 124,
	GetMemorySize = 127
};
```

### Q1 — PS2Recomp handler path (post-P1f)

`FORK/ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp:26-40`:
```cpp
        void addHandler(uint8_t *rdram,
                        R5900Context *ctx,
                        PS2Runtime *runtime,
                        bool dmac)
        {
            const int id = scheduler(rdram, ctx, runtime)
                               .addIrqHandler(dmac,
                                              getRegU32(ctx, 4),
                                              getRegU32(ctx, 5),
                                              getRegU32(ctx, 6) != 0u,
                                              getRegU32(ctx, 7),
                                              getRegU32(ctx, 28),
                                              getRegU32(ctx, 29));
```

`FORK/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1545-1560`
(`dispatchIrq`; P1f hunk):
```cpp
        GuestInvocation invocation{};
        invocation.kind = GuestInvocationKind::Interrupt;
        invocation.context.pc = handler.handler;
        SET_GPR_U32(&invocation.context, 4, cause);
        SET_GPR_U32(&invocation.context, 5, handler.argument);
        SET_GPR_U32(&invocation.context, 28, handler.gp);
        // P1f: never run a handler on its registration-time thread sp (that
        // stack belongs to a live guest thread; the 0x3e4db8 prologue stored
        // zeros over thread 1's ra slot at 0x1ffff00). sp=0 makes the run()
        // dequeue path assign invocationStackTop() from the reserved region.
        SET_GPR_U32(&invocation.context, 29, 0u);
        SET_GPR_U32(&invocation.context, 31, 0u);
        queueInvocation(std::move(invocation));
```

`FORK/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:405-408` and `:498-501`
(dequeue assigns a reserved top when `sp==0`):
```cpp
                if (getRegU32(&invocation.context, 29) == 0u)
                {
                    SET_GPR_U32(&invocation.context, 29, invocationStackTop());
                }
```

`FORK/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1426-1450`
(`invocationStackTop`):
```cpp
uint32_t EeScheduler::invocationStackTop()
{
    assertExecutor();
    const GuestThread *owner = currentThread();
    ...
    const size_t depth = owner ? owner->invocations.size() : 0u;
    const uint64_t key = (static_cast<uint64_t>(static_cast<uint32_t>(owner->id)) << 32u) |
                         static_cast<uint32_t>(depth);
    const auto existing = m_invocationStackTops.find(key);
    if (existing != m_invocationStackTops.end())
    {
        return existing->second;
    }
    constexpr uint32_t kInvocationStackSize = 0x4000u;
    const uint32_t top = m_runtime.reserveAsyncCallbackStack(kInvocationStackSize, 16u);
```

`FORK/ps2xRuntime/src/lib/ps2_runtime.cpp:2193-2229`
(`reserveAsyncCallbackStack`):
```cpp
uint32_t PS2Runtime::reserveAsyncCallbackStack(uint32_t size, uint32_t alignment)
{
    ...
    std::lock_guard<std::mutex> lock(m_asyncCallbackStackMutex);
    uint32_t top = m_asyncCallbackStackTop;
    ...
    uint32_t base = top - allocSize;
    base &= ~(normalizedAlignment - 1u);
    if (base < m_asyncCallbackStackFloor || base >= top)
    {
        return 0u;
    }
    m_asyncCallbackStackTop = base;
    return top - 0x10u;
}
```

`FORK/ps2xRuntime/include/ps2_runtime.h:521-525` (P1f inits):
```cpp
    // P1f: async-callback (invocation) stacks live in the EE kernel-reserved
    // low RAM below the ELF image and guest heap, never at the RAM top where
    // guest thread stacks live. See reserveAsyncCallbackStack.
    uint32_t m_asyncCallbackStackFloor = 0x00080000u;
    uint32_t m_asyncCallbackStackTop = 0x00100000u;
```

### Q2 — alarm path

PCSX2: no code to quote — `grep -rni "alarm"` over `Counters.cpp`,
`Counters.h`, `Hw.cpp` is empty; the `Syscall` enum above has no alarm
entry; `"_SetAlarm"` at `R5900OpcodeImpl.cpp:94` is consumed only by the
`BIOS_LOG` at `:917`.

`FORK/ps2xRuntime/src/lib/Kernel/Syscalls/Sync.cpp:333-342`:
```cpp
    void SetAlarm(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        setReturnS32(ctx,
                     scheduler(rdram, ctx, runtime)
                         .setAlarm(static_cast<uint16_t>(getRegU32(ctx, 4)),
                                   getRegU32(ctx, 5),
                                   getRegU32(ctx, 6),
                                   getRegU32(ctx, 28),
                                   getRegU32(ctx, 29)));
    }
```

`FORK/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2195-2217` (`Alarm` event;
P1f hunk):
```cpp
    case EeEventType::Alarm:
    {
        ...
        const EeAlarm alarm = it->second;
        m_alarms.erase(it);
        GuestInvocation invocation{};
        invocation.kind = GuestInvocationKind::Alarm;
        invocation.context.pc = alarm.handler;
        SET_GPR_U32(&invocation.context, 4, static_cast<uint32_t>(alarm.id));
        SET_GPR_U32(&invocation.context, 5, static_cast<uint32_t>(alarm.ticks));
        SET_GPR_U32(&invocation.context, 6, alarm.argument);
        SET_GPR_U32(&invocation.context, 28, alarm.gp);
        // P1f: same as dispatchIrq above; the SetAlarm caller sp belongs to
        // a live guest thread, so take sp from the reserved region instead.
        SET_GPR_U32(&invocation.context, 29, 0u);
        SET_GPR_U32(&invocation.context, 31, 0u);
        queueInvocation(std::move(invocation));
```

`FORK/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp:158-173`
(both numberings accepted):
```cpp
        case 0x18:
        case 0xFC:
            SetAlarm(rdram, ctx, runtime);
            return true;
        case 0x19:
        case 0xFE:
            CancelAlarm(rdram, ctx, runtime);
            return true;
```

### Q3 — CD callback

PCSX2: `grep -rn "sceCdInitEeCB\|InitEeCB\|EeCB"` over all `.cpp`/`.h` is
empty. Only `sceCdCallback` source hit:

`REF/pcsx2/IopModuleNames.cpp:4-9,29` (name table for IOP module imports):
```cpp
#define MODULE(n) if (#n == libname) switch (index) {
// machine generated
MODULE(cdvdman)
	...
	EXPORT( 37, sceCdCallback)
```

`REF/pcsx2/IopBios.cpp:1311-1313` (sole consumer is the import-name
lookup):
```cpp
	const char* irxImportFuncname(const std::string& libname, u16 index)
	{
#include "IopModuleNames.cpp"
```

`FORK/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:66-88` (`queueCdCallback`):
```cpp
        void queueCdCallback(R5900Context *ctx, PS2Runtime *runtime, uint32_t func)
        {
            ...
            GuestInvocation invocation{};
            invocation.kind = GuestInvocationKind::Interrupt;
            invocation.tag = kCdCallbackDiagTagBase | static_cast<uint64_t>(func);
            invocation.context.pc = g_cdCallbackFn;
            SET_GPR_U32(&invocation.context, 4, func);
            SET_GPR_U32(&invocation.context, 5, 0u);
            SET_GPR_U32(&invocation.context, 28, g_cdCallbackGp);
            SET_GPR_U32(&invocation.context, 29, g_cdCallbackStackTop);
            SET_GPR_U32(&invocation.context, 31, 0u);
```

`FORK/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:494-508`
(`sceCdInitEeCB`):
```cpp
    void sceCdInitEeCB(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
    {
        (void)rdram;
        (void)runtime;
        const uint32_t stackAddr = getRegU32(ctx, 5);
        const uint32_t stackSize = getRegU32(ctx, 6);
        g_cdCallbackStackTop = stackAddr + stackSize;
```

### Q4 — SIF RPC / async callbacks

PCSX2: `grep -rin "rpc"` over `Sif.cpp`/`Sif0.cpp`/`Sif1.cpp`/`sif2.cpp`/
`Sif.h` is empty. `REF/pcsx2/Sifcmd.h:6-12` (whole protocol surface):
```cpp
struct t_sif_dma_transfer
{
	void *src;
	void *dest;
	s32 size;
	s32 attr;
};
```

`REF/pcsx2/IopBios.cpp:1346-1370` (IOP HLE scope: IRX imports, synchronous
in the calling IOP thread):
```cpp
	irxHLE irxImportHLE(const std::string& libname, u16 index)
	{
		// debugging output
		// clang-format off
		MODULE(loadcore)
			EXPORT_H(  6, RegisterLibraryEntries)
			EXPORT_H(  7, ReleaseLibraryEntries);
		END_MODULE
		MODULE(sysmem)
			EXPORT_H( 14, Kprintf)
		END_MODULE
		// Special case with ioman and iomanX
		...
					EXPORT_H(  4, open)
					EXPORT_H(  5, close)
					EXPORT_H(  6, read)
					EXPORT_H(  7, write)
					EXPORT_H(  8, lseek)
```

`FORK/ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp:662-673` (completion
callback) and `:678-692` (server dispatch):
```cpp
            GuestInvocation callback{};
            callback.kind = GuestInvocationKind::RpcCallback;
            callback.context = parent;
            callback.context.pc = callbackFunction;
            SET_GPR_U32(&callback.context, 4, endParameter);
            SET_GPR_U32(&callback.context, 29, runtime->eeScheduler().invocationStackTop());
            SET_GPR_U32(&callback.context, 31, 0u);
...
            GuestInvocation invocation{};
            invocation.kind = GuestInvocationKind::RpcCallback;
            invocation.context = *ctx;
            invocation.context.pc = guestFunction;
            ...
            SET_GPR_U32(&invocation.context, 29, runtime->eeScheduler().invocationStackTop());
            SET_GPR_U32(&invocation.context, 31, 0u);
```

### Q5 — low RAM contents

`REF/pcsx2/MemoryTypes.h:7-11`:
```cpp
namespace Ps2MemSize
{
	static constexpr u32 MainRam = _32mb;      // 32 MB main memory.
```

`REF/pcsx2/R5900.h:293-297`:
```cpp
// modules loaded at hardcoded addresses by the kernel
const u32 EEKERNEL_START	= 0;
const u32 EENULL_START		= 0x81FC0;
const u32 EELOAD_START		= 0x82000;
const u32 EELOAD_SIZE		= 0x20000; // overestimate for searching
```

`REF/pcsx2/Interpreter.cpp:613-640` (fast boot still boots the real BIOS
EELOAD and hooks it):
```cpp
				if (cpuRegs.pc == EELOAD_START)
				{
					// The EELOAD _start function is the same across all BIOS versions afaik
					const u32 mainjump = memRead32(EELOAD_START + 0x9c);
					if (mainjump >> 26 == 3) // JAL
						g_eeloadMain = ((EELOAD_START + 0xa0) & 0xf0000000U) | (mainjump << 2 & 0x0fffffffU);
				...
						// See comments on this code in iR5900.cpp's recRecompile()
						const u32 typeAexecjump = memRead32(EELOAD_START + 0x470);
						const u32 typeBexecjump = memRead32(EELOAD_START + 0x5B0);
						const u32 typeCexecjump = memRead32(EELOAD_START + 0x618);
						const u32 typeDexecjump = memRead32(EELOAD_START + 0x600);
```

`REF/pcsx2/R5900OpcodeImpl.cpp:1065-1092` (kernel code + thread list in
low RAM, `StartThread`/`ChangeThreadPriority` debugger scan):
```cpp
		case Syscall::StartThread:
		case Syscall::ChangeThreadPriority:
		{
			if (CurrentBiosInformation.eeThreadListAddr == 0)
			{
				u32 offset = 0x0;
				// Suprisingly not that slow :)
				while (offset < 0x5000) // I find that the instructions are in between 0x4000 -> 0x5000
				{
					u32 addr = 0x80000000 + offset;
					...
						// We've found the instruction pattern!
						// We (well, I) know that the thread address is always 0x8001 + the immediate of the 6th instruction from here
						const u32 op = memRead32(0x80000000 + offset + (sizeof(u32) * 6));
						CurrentBiosInformation.eeThreadListAddr = 0x80010000 + static_cast<u16>(op) - 8; // Subtract 8 because the address here is offset by 8.
```

`REF/pcsx2/DebugTools/BiosDebugData.h:33-55` (PCSX2's model of the real EE
kernel thread struct):
```cpp
struct EEInternalThread
{ // internal struct
	u32 prev;
	u32 next;
	int status;
	u32 resumeAddr; // address to return to when switching
	u32 regCtx; // points to the saved regs on stack
	u32 gpReg;
	...
	u32 entry;
	...
	u32 stackMem;
	int stackSize;
	u32 root;
	u32 heap_base;
};
```

`REF/pcsx2/R5900.cpp:67` (EE reset boots the BIOS ROM, not an HLE kernel):
```cpp
	cpuRegs.pc				= 0xbfc00000; //set pc reg to stack
```

### P1f fix (FORK `6046260`, read via `git show`; applied, on `ssx3`)

Stat: `ps2_runtime.h` (+7/-2), `EeScheduler.cpp` (+10/-2),
`ps2_runtime.cpp` (+15/-6). Semantic hunks: `dispatchIrq`
`handler.sp` → `0u`; `Alarm` event `alarm.sp` → `0u`;
`m_asyncCallbackStackFloor`/`Top` `0x01F00000`/`PS2_RAM_SIZE` →
`0x00080000`/`0x00100000` in the header inits, the `PS2Runtime` ctor, and
the `loadELF` reset. Full text in `git show 6046260` (3 files,
23 insertions, 9 deletions).

## P2-4. Patch sketch (NOT applied; prose — no PCSX2-grounded diff exists)

No unified diff is proposed for any of Q1–Q4. Reason, per question: the
PCSX2 reference contains no handler/alarm/CD/RPC stack behavior to differ
from — on every question the EE behavior is owned by the real BIOS, which
PCSX2 executes as guest code (`cpuReset` boots `0xbfc00000`;
`R5900.cpp:67`) and does not HLE (EE `SYSCALL()` falls through to
`cpuException`; `R5900OpcodeImpl.cpp:1200-1206`). PS2Recomp HLEs the whole
EE kernel, so parity with the reference is game-observable, not
mechanistic. Each item below states the exact function-level position
instead of a diff.

| # | PS2Recomp behavior vs reference | Sketch (not applied) |
|---|---|---|
| 1 | Post-P1f, `dispatchIrq` queues with `sp=0` → `invocationStackTop()` from `[0x80000,0x100000)`. Reference delivery (`hwIntcIrq` → `_cpuEventTest_Shared` → `cpuException`) never writes `sp`; the BIOS then invokes the handler by unknown (to this source) means. | No diff. The P1f direction (handlers off the interrupted thread's stack) is consistent with the only reference-established fact on the path (delivery touches no GPR). A diff toward "run handlers on the interrupted thread's stack" would need BIOS evidence PCSX2 source does not contain. P1f (`6046260`) is already on `ssx3`. |
| 2 | Post-P1f, the `Alarm` event queues with `sp=0` → same reserved region. Reference has no alarm queue, context, or stack. | No diff, same reason as Q1. A diff reproducing the BIOS alarm context (whatever registers/stack the real `_SetAlarm` path uses) needs non-PCSX2 evidence. |
| 3 | `queueCdCallback` runs the game's callback on the game's own stack (`stack+size` from `sceCdInitEeCB`), as an `Interrupt`-kind invocation on the dequeuing/ephemeral thread. Reference has no EE-side CD callback model. | No diff. P1f correctly left this path alone (`sp` stays nonzero, so the dequeue sites keep it). A diff creating a dedicated parked `GuestThread` for the callback (real libcdvd shape) is ungrounded by PCSX2 source, which never names the EE-side thread. |
| 4 | RPC server + completion callbacks already take `invocationStackTop()` directly. Reference models SIF DMA only; RPC threading is guest BIOS/module behavior. | No diff. The shared P1f region move already covers these stacks; no `RPC.cpp` change is indicated by the reference. |

Cross-cutting note (labeled, no verdict): the one PCSX2-grounded tension
with P1f sits under Q5, outside the Q1–Q4 diff scope. `R5900.h:293-297`
places kernel-loaded modules inside P1f's borrowed region (`EENULL_START
= 0x81FC0`, `EELOAD_START = 0x82000`, search bound `0x20000`), and
`Interpreter.cpp:622-640` reads live BIOS code at `EELOAD_START+0x470`
through `+0x618` during boot. PS2Recomp runs no BIOS, so no direct
collision is established either — but the reference does not corroborate
`[0x80000,0x100000)` as free. Whether any game touches that range, and
whether EELOAD stays resident after boot, are outside PCSX2 source (see
P2-6). No region-move diff is proposed here.

## P2-5. Exact commands used

From `/Users/bradrichardson/dev/ssx3` (reads via file tools, not listed;
all FORK/REF access read-only — `git show`/`git log`, `grep`, `ls`):

```
git clone --filter=blob:none --depth 1 --no-recurse-submodules https://github.com/pcsx2/pcsx2.git "/Volumes/Extreme SSD/pcsx2-ref"
git -C "/Volumes/Extreme SSD/pcsx2-ref" log -1 --format="%H %ad %s"
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" log --oneline -15
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" branch --show-current
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" status --short
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" show 6046260 --stat
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" show 6046260
grep -rn "reserveAsyncCallbackStack|invocationStackTop|g_cdCallbackStackTop|..." ps2xRuntime/src/lib ps2xRuntime/include   # FORK
grep -n "AddIntcHandler|SetAlarm|..." ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp   # FORK
grep -rn "AddIntcHandler|SetAlarm" pcsx2 --include=*.cpp --include=*.h   # REF
grep -rn "hwIntc|intcInterrupt|INTC_STAT" pcsx2/Hw.cpp pcsx2/Hw.h   # REF
grep -n "cpuException|R5900Exception|..." pcsx2/R5900.cpp   # REF
grep -rn "cpuTestINTCInts|cpuTestDMACInts|intcInterrupt()|dmacInterrupt()" pcsx2 --include=*.cpp --include=*.h   # REF
grep -rn "R5900::bios" pcsx2 --include=*.cpp --include=*.h   # REF
grep -n "FastBoot|loadElf|..." pcsx2/VMManager.cpp pcsx2/Elfheader.cpp   # REF
grep -rn "sceCdInitEeCB|sceCdCallback|CdCallback" pcsx2 --include=*.cpp --include=*.h -l   # REF
grep -rn "Hle_SetHostRoot" pcsx2 --include=*.cpp --include=*.h -l   # REF
grep -rn "eeThreadListAddr|ThreadListInstructions" pcsx2 --include=*.cpp --include=*.h   # REF
grep -rn "intstack|interrupt stack|kernel stack|0x80000|0x100000" pcsx2/DebugTools/MipsStackWalk.* pcsx2/Memory.cpp pcsx2/Elfheader.cpp pcsx2/ps2/BiosTools.cpp   # REF (empty)
grep -rn "callback|Callback" pcsx2/CDVD --include=*.cpp --include=*.h   # REF (host-side only)
grep -rni "alarm" pcsx2/Counters.cpp pcsx2/Counters.h pcsx2/Hw.cpp   # REF (empty)
grep -rin "rpc" pcsx2/Sif.cpp pcsx2/Sif0.cpp pcsx2/Sif1.cpp pcsx2/sif2.cpp pcsx2/Sif.h   # REF (empty)
grep -rn "sceCdInitEeCB|InitEeCB|EeCB" pcsx2 --include=*.cpp --include=*.h   # REF (empty)
grep -rn "g_eeloadMain|g_eeloadExec" pcsx2 --include=*.cpp --include=*.h   # REF
grep -rn "EELOAD_START" pcsx2 --include=*.h   # REF
git add -f local/research/P2/REPORT.md; git commit -m "[P2] ..." (trailer Orchestrated-By: Muse Code)
```

## P2-6. What I could not do

- Q1 hardware truth: which stack the real BIOS runs `AddIntcHandler`
  handlers on (interrupted thread's stack, kernel interrupt stack, or
  other) is not stated anywhere in PCSX2 source. Searched: `Hw.cpp`,
  `R5900.cpp`, `R5900OpcodeImpl.cpp`, `COP0.cpp`, `DebugTools/`
  (incl. `MipsStackWalk.cpp`, which takes `sp` as an input and models no
  interrupt frames), `Docs/` (filename listing only: config guide, FAQ,
  GameIndex — no kernel-RAM doc). Never guessed from memory.
- Q2 hardware truth: alarm callback context/stack — same; no PCSX2 alarm
  model exists to quote.
- Q3 hardware truth: the EE-side CD callback thread (libcdvd creates it;
  stack/size/owner details) — PCSX2 names only the IOP `cdvdman` export
  for logging; the EE side runs as guest code.
- Q4 hardware truth: SIF RPC server-thread stacks — guest BIOS/module
  behavior; PCSX2 models DMA FIFOs only.
- Q5 free subrange: no PCSX2 source declares any of `0x0-0xFFFFF` free;
  only occupants are established (kernel code `0x4000-0x5000`, thread
  list ~`0x10000`, `EENULL` `0x81FC0`, `EELOAD` `0x82000+`). Whether any
  game uses `[0x80000,0x100000)`, and whether EELOAD stays resident after
  boot (`EELOAD_SIZE` is labeled an overestimate "for searching"), are
  outside PCSX2 source.
- FORK state note: `git status` in the fork shows the pre-existing local
  modification `M ps2xRuntime/src/runner/register_functions.cpp`
  (generated replacement, per P1 reports); it was already modified before
  P2 started and was not touched — P2 ran zero writes outside
  `local/research/P2/`.
- Time box: finished inside the 4-hour box; no `waits.log` (no leases
  taken or needed).
