# P4 REPORT — PS2Recomp fork network + downstream ports: borrowable fixes (read-only research)

Runbook: `local/muse/prompts/P4.md`. Tables, no verdicts (license verdicts are re-cites of P3 §8.6 only).
Read first (per runbook): `local/research/P3/REPORT.md` §8 (clone paths, license verdicts, gaps P1/P5) and
`local/research/P1/REPORT.md` Part 8 (current rung: LUI+ORI MMIO fold; P1h owns that fix — this report covers
everything AFTER and AROUND it: scheduler/IRQ/alarm/CD/VIF lifecycles).
No builds, no boots, no emulator runs, no leases, no `adb`, no fork edits. No `git push` (orchestrator owns origin).
All `file:line` cites below are paths I opened; `diff -rq`/`grep` only located candidates.
Our-fork line numbers in Q2/Q4 are against our fork at `6046260` (exported via `git archive` to `/tmp`, read-only).

## 0. Rev table (Q1 scope + what was actually on disk)

P3 M-table revs requested: M1–M14. All `fork-survey/` clones are depth-1 (single commit, no history),
so revs other than the checked-out HEAD are unrecoverable from disk (recorded `absent`).

| # | M-table rev | Clone on disk | Disk rev | Diff base | Status |
|---|---|---|---|---|---|
| M1 | TheTharin `rogue-galaxy@7f29bbd` | `fork-survey/thetharin-rogue-galaxy` | `7f29bbd` | `upstream-baseline` (`14b1e5c`) | diffed, 17 entries |
| M2 | Sorachi00 `@2f5d48c` | `fork-survey/sorachi00-main` | `2f5d48c` | `upstream-baseline` | diffed, 19 entries |
| M3 | smmathews `fiber@c7b2edc` | `fork-survey/smmathews-fiber-sched` | `c7b2edc` | `upstream-baseline` | mechanism files read; tree diff 103 entries (old base, drift dominates) |
| M4 | phmdacosta `cd-cb@184158a` | `fork-survey/phmdacosta-ee-timer` | `e465b4d` (ee-timer, NOT `184158a`) | — | **unresolved**: M4 rev absent from disk; `e465b4d` EE-timer mechanism read instead (bonus row) |
| M5 | hedgeg0d `katamari@3096823` | `fork-survey/hedgeg0d-lazy-bind` | `cfcd341` (lazy-bind, NOT `3096823`) | — | **unresolved**: M5 rev absent from disk |
| M6 | MrCool `@7978365` | `fork-survey/mrcool-main` | `7978365` | `upstream-baseline` | mechanism hunks read; tree diff 318 entries (old base + feature work, drift dominates) |
| M7 | GTT `#222@c4d099b` | `fork-survey/gtteancum-di-preempt` | `c4d099b` | `upstream-baseline` | diffed, 2 files (full bodies below) |
| M8 | GTT `#226@1fa97b8` | (same checkout `c4d099b`) | — | — | **unresolved**: rev absent from disk |
| M9 | GTT `#224/#223/#217` | (same checkout `c4d099b`) | — | — | **unresolved**: revs absent from disk |
| M10 | hedge `#235@cfcd341` | `fork-survey/hedgeg0d-lazy-bind` | `cfcd341` | `upstream-baseline` | diffed, 2 files (full bodies below) |
| M11 | hedge `#241` (no rev) | (same checkout `cfcd341`) | — | — | **unresolved**: no rev given, no second checkout |
| M12 | Sinan `#211@8dc8b54` | `fork-survey/sinan-syscall-override` | `8dc8b54` | `upstream-baseline` | diffed, 5 files (full bodies below) |
| M13 | TheTharin `#216@7ea9a2c` | `fork-survey/thetharin-rogue-galaxy` | `7f29bbd` | — | **unresolved** as rev; NOTE the `7f29bbd` checkout itself contains a heap-limit layout rework (quoted below) that may subsume #216 — identity unconfirmed |
| M14 | phm `heap@9e00466` | `fork-survey/phmdacosta-ee-timer` | `e465b4d` | — | **unresolved**: rev absent from disk |

## 1. Q1 — Fork diffs with bodies (90 min cap; partials recorded above)

### M1 — TheTharin `rogue-galaxy@7f29bbd` (17 entries)

Files changed vs `upstream-baseline`: `ps2xRuntime/CMakeLists.txt`,
`ps2xRuntime/include/ps2_runtime.h`, `ps2xRuntime/include/ps2_runtime_macros.h`,
`ps2xRuntime/include/runtime/ps2_memory.h`, `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`,
`ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp`, `ps2xRuntime/src/lib/Kernel/Syscalls/FileIO.cpp`,
`ps2xRuntime/src/lib/Kernel/Syscalls/System.cpp`, `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`,
`ps2xRuntime/src/lib/ps2_memory.cpp`, `ps2xRuntime/src/lib/ps2_runtime.cpp`,
`ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`, new `ps2xRuntime/src/runner/rg_game_override.cpp` (292 lines),
`ps2xTest/CMakeLists.txt`, `ps2xTest/src/main.cpp`, new `ps2xTest/src/ps2_fpu_macros_tests.cpp`,
`ps2xTest/src/ps2_runtime_kernel_tests.cpp`.

Mechanism 1a — handler stack from owner SP (EeScheduler.cpp; 3 dispatch sites + 3 enqueue sites).
Dispatch site hunk (`@@ -188,7 +188,14 @@`, same shape at `@@ -258,7 +265,11 @@` and `@@ -1110,7 +1121,11 @@`):

```cpp
                 if (getRegU32(&invocation.context, 29) == 0u)
                 {
-                    SET_GPR_U32(&invocation.context, 29, invocationStackTop());
+                    // Like hardware, run the handler on the interrupted
+                    // thread's stack below its live sp; a dedicated top-of-RAM
+                    // stack would overwrite the main thread's frames.
+                    const uint32_t ownerSp = getRegU32(&owner->activeContext(), 29);
+                    const uint32_t invSp = (ownerSp > 0x20000u && ownerSp <= PS2_RAM_SIZE)
+                                               ? ((ownerSp & ~0xFu) - 0x800u)
+                                               : invocationStackTop();
+                    SET_GPR_U32(&invocation.context, 29, invSp);
                 }
```

Enqueue site hunk (`@@ -1278,7 +1293,9 @@`, IRQ dispatch; same "sp deliberately left 0" at vsync `:1910` and alarm `:1940`):

```cpp
         SET_GPR_U32(&invocation.context, 28, handler.gp);
-        SET_GPR_U32(&invocation.context, 29, handler.sp);
+        // sp deliberately left 0: the registration-time sp points into the
+        // registering thread's live stack; the dispatcher assigns a borrowed
+        // stack below the interrupted thread's sp instead.
         SET_GPR_U32(&invocation.context, 31, 0u);
```

Mechanism 1b — drain DMAC completions from the event pump (EeScheduler.cpp `@@ -1745,6 +1762,11 @@`):

```cpp
+    // DMA completion handlers are otherwise only drained from guest stores; a
+    // thread that blocks waiting for a transfer it just kicked would never see
+    // the interrupt that wakes it. Deliver them from the event pump too.
+    m_runtime.drainCompletedDmacHandlers(m_rdram);
+
```

Mechanism 1c — empty DMA transfers still complete (ps2_memory.cpp). Kick path records the channel
(`@@ -1281,6 +1290,15 @@`):

```cpp
+            // Remember the kick so the channel completes even if it ends up
+            // moving no data (see m_dmaStartedChannels).
+            if (channelBase == 0x10008000u)
+                m_dmaStartedChannels.fetch_or(1u << 0, std::memory_order_relaxed);
+            else if (channelBase == 0x10009000u)
+                m_dmaStartedChannels.fetch_or(1u << 1, std::memory_order_relaxed);
+            else if (channelBase == 0x1000A000u)
+                m_dmaStartedChannels.fetch_or(1u << 2, std::memory_order_relaxed);
+
```

Completion path (`PS2Memory::processPendingTransfers`, `@@ -1765,27 +1789,41 @@`):

```cpp
+    // A channel that was kicked completes even when its source chain yielded
+    // no data; otherwise CHCR.STR would stay set and the guest would wait for
+    // a transfer that never reports done.
+    const uint32_t startedChannels = m_dmaStartedChannels.exchange(0, std::memory_order_relaxed);
...
-    if (hadGif)
+    if (hadGif || (startedChannels & (1u << 2)) != 0u)
...
-    if (hadVif0)
+    if (hadVif0 || (startedChannels & (1u << 0)) != 0u)
...
-    if (hadVif1)
+    if (hadVif1 || (startedChannels & (1u << 1)) != 0u)
```

(with `m_ioRegisters[ch+0x00] &= ~0x100u` STR clear + `queueCompletedDmacCause` in each arm, unchanged lines).
State: `std::atomic<uint32_t> m_dmaStartedChannels{0}` (`ps2_memory.h`, "Bit 0 = VIF0, bit 1 = VIF1, bit 2 = GIF").

Mechanism 1d — VIFcode interrupt bit raises INTC (ps2_vif1_interpreter.cpp + ps2_memory.h/cpp + ps2_runtime.cpp).
VIF0 site (`@@ -77,7 +77,10 @@`; VIF1 same shape at `:315` with cause 5):

```cpp
         if (irq)
+        {
             vif0_regs.stat |= (1u << 11);
+            queueIntcCause(4u); // INTC cause 4 = VIF0
+        }
```

Queue/drain (`ps2_memory.h` `queueIntcCause`/`consumeIntcCauses` + mutex'd vector; `ps2_runtime.cpp`
`drainCompletedDmacHandlers` tail):

```cpp
+    // Peripheral INTC sources (VIF interrupt bit) share this drain point.
+    for (uint32_t cause : m_memory.consumeIntcCauses())
+    {
+        m_eeScheduler->dispatchIrq(false, cause);
+    }
```

Mechanism 1e — heap-limit layout rework ("rest of RAM" resolves to main-thread stack base).
`System.cpp` SetupThread tail (`@@ -550,6 +550,13 @@`):

```cpp
+        // SetupHeap resolves a "rest of RAM" heap to this stack base.
+        if (runtime && initialStack != 0u)
+        {
+            runtime->setGuestMainStackBase(initialStack);
+        }
+
```

`System.cpp` SetupHeap (`@@ -561,21 +568,20 @@`):

```cpp
-        // Silent Hill and other games often pass -1 (0xFFFFFFFF) to mean "rest of RAM".
-        static constexpr uint32_t kDefaultGuestHeapEnd = 0x01F00000u;
-        uint32_t heapLimit = kDefaultGuestHeapEnd;
-
+        // heap_size of 0 or -1 means "rest of RAM"; like the retail kernel,
+        // that resolves to the main thread's stack base recorded by
+        // SetupThread (limit 0 below).
+        uint32_t heapLimit = 0u;
         if (heapSize != 0u && heapSize != 0xFFFFFFFFu)
         {
             const uint64_t candidate = static_cast<uint64_t>(heapBase) + static_cast<uint64_t>(heapSize);
-            heapLimit = static_cast<uint32_t>(std::min<uint64_t>(candidate, kDefaultGuestHeapEnd));
+            heapLimit = static_cast<uint32_t>(std::min<uint64_t>(candidate, PS2_RAM_SIZE));
+            if (heapLimit <= heapBase)
+            {
+                heapLimit = 0u;
+            }
         }
```

plus `defaultGuestHeapLimitLocked()` (`ps2_runtime.cpp`, returns `m_guestMainStackBase` or `0x01F00000u`
fallback), `EndOfHeap` returning `guestHeapLimit()`, `configureGuestHeap` raising
`m_asyncCallbackStackFloor` above the configured limit, tests proving a `0x18B0000` Rogue Galaxy arena fits.

Other M1 hunks (quoted titles only, bodies opened): `FileIO.cpp` `translateFioMode` O_RDONLY/O_WRONLY
bit tests (was: every open counted read+write); `ps2_runtime_macros.h` `FPU_CVT_W_S` truncate-toward-zero
with INT32 clamp (was `nearbyintf`); `GS.cpp` packet-builder tag sizing on close + PMODE/SMODE2 direct
apply; `gs_cpu_backend.cpp` progressive-present + PCRTC anti-blur collapse; `ps2_memory.cpp` GS priv-reg
128-bit store split; overlay side table `m_registeredFunctions` in `replaceFunction`/`hasFunction`/
`lookupFunction` + `runner/title/*.cpp` glob with `SKIP_UNITY_BUILD_INCLUSION`; `rg_game_override.cpp`
DVD9 OTP ISO9660 absolute-LBA lookup.

| Rung | SSX 3 relevance (mechanism → rung mapping, no verdict) |
|---|---|
| handler/alarm stacks | 1a replaces P1f's reserved-stack model with borrowed-below-owner-sp; SSX 3 currently parks on MMIO, thread stacks otherwise stable — bears on the NEXT rung (post-MMIO handler delivery) |
| dispatch | 1b closes the block-then-miss-completion race class directly above SSX 3's VIF0 poll loop shape |
| VIF/DMA lifecycle | 1c is the STR-clears-on-empty-transfer rule; SSX 3's park loop polls CHCR.STR — once MMIO addresses are right, this decides whether empty kicks stall |
| VIF lifecycle | 1d wires VIF IRQ→INTC 4/5; SSX 3 shows zero VIF IRQ traffic yet |
| heap layout | 1e replaces the `0x01F00000u` hard ceiling; SSX 3 `[SetupHeap]` log line shows `size=0xffffffff` rest-of-RAM — same input shape |
| GS/other | packet-builder/FPU/FileIO/present fixes are GS/correctness rungs SSX 3 has not reached |

### M2 — Sorachi00 `@2f5d48c` (19 entries)

Files changed vs `upstream-baseline`: `.gitignore`, `README.md`, `ps2xIOP/CMakeLists.txt`,
`ps2xIOP/include/ps2x/iop/iop_host.h`, `ps2xIOP/include/ps2x/iop/iop_types.h`,
`ps2xIOP/src/builtin_profiles.cpp`, `ps2xIOP/src/module_factories.h`, new
`ps2xIOP/src/modules/cdvd.cpp` (141 lines), new `ps2xIOP/src/modules/ezsound.cpp` (59 lines),
`ps2xRuntime/include/runtime/ee_scheduler.h`, `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`,
`ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp`, `ps2xRuntime/src/lib/Kernel/Stubs/CD.h`,
`ps2xRuntime/src/lib/Kernel/Syscalls/FileIO.cpp`, `ps2xRuntime/src/lib/ps2_iop_host.cpp`,
`ps2xRuntime/src/lib/ps2_iop_host.h`, `ps2xRuntime/src/lib/ps2_runtime.cpp`,
`ps2xRuntime/src/runner/register_functions.cpp` (169,912 lines vs 6-line stub — generated Drakengard
game output checked in; NOT read, recorded as game-specific), new `tools/` (`drakengard_merged.toml`
10,669 B + `drakengard.csv` 370,146 B).

Mechanism 2a — handler.sp zero + nesting/start guard (EeScheduler.cpp `@@ -252,7 +252,18 @@`,
`@@ -293,6 +304,11 @@`, `@@ -1278,7 +1294,7 @@`; `ee_scheduler.h` `@@ -99,6 +99,8 @@`):

```cpp
-        if (!m_pendingInvocations.empty())
+        const bool hasActiveInterrupt = std::any_of(running->invocations.begin(), running->invocations.end(),
+            [](const GuestInvocation& invocation)
+            {
+                return invocation.kind == GuestInvocationKind::Interrupt;
+            });
+
+        const bool deferPendingInterrupt = !m_pendingInvocations.empty() && m_pendingInvocations.front().kind == GuestInvocationKind::Interrupt && hasActiveInterrupt;
+
+        if (!m_pendingInvocations.empty() &&
+            !deferPendingInterrupt &&
+            (running->invocations.empty() ||
+                running->invocations.back().started))
```

```cpp
             m_insideInterrupt = !running->invocations.empty() && running->invocations.back().kind == GuestInvocationKind::Interrupt;
+            if (!running->invocations.empty())
+            {
+                running->invocations.back().started = true;
+            }
+
```

```cpp
         SET_GPR_U32(&invocation.context, 28, handler.gp);
-        SET_GPR_U32(&invocation.context, 29, handler.sp);
+        SET_GPR_U32(&invocation.context, 29, 0u);
```

```cpp
     std::function<void(const R5900Context &, R5900Context &)> onComplete;
+
+    bool started = false;
 };
```

Mechanism 2b — `sceCdLayerSearchFile` + IOP `cdvd`/`ezsound` services + `sceCdlFILE` struct
(CD.cpp `@@ -169,6 +170,42 @@` quoted in full in §6 row M2b; iop_types.h `@@ -142,4 +142,12 @@`):

```cpp
+    struct sceCdlFILE
+    {
+        uint32_t lsn;
+        uint32_t size;
+        char name[16];
+        uint8_t date[8];
+    };
```

wired via `IopHost::sceCdLayerSearchFile` pure virtual (`iop_host.h`), `PS2IopHostAdapter` override,
`createCdvdService`/`createEzSoundService` factories registered in `builtin_profiles.cpp`.
`cdvd.cpp:15` `constexpr uint32_t CD_SERVER_SEARCHFILE = 0x80000597u;` ("from the sdk").

Mechanism 2c — misc: `FileIO.cpp` `rom0:`/`rom:` early `-1` ("this should read romver...");
`ps2_runtime.cpp` hardcodes `paths.cdImage = paths.elfDirectory / "disc" / "drakengard.iso"`.

| Rung | SSX 3 relevance |
|---|---|
| handler stacks | 2a zeroes handler sp at enqueue (dispatcher assigns); same enqueue half as M1-1a, different dispatch half (keeps `invocationStackTop`) |
| dispatch | 2a no-preempt-active-IRQ + started-gate is the dequeue guard shape Q4 names |
| CD callback | 2b adds dual-layer search + CDVD RPC service; SSX 3 CD is single-layer and idle since boot — no current rung |
| other | 2c rom0 stub + hardcoded ISO path are title-specific |

### M3 — smmathews `fiber@c7b2edc` (103 entries; old base, no `EeScheduler.cpp`)

Tree diff vs `upstream-baseline` is dominated by base drift (pre-#184: no `ee_scheduler.h`,
old GS include/src layout, `Lifecycle.cpp/h` instead of scheduler syscalls). Mechanism read directly
from the author's files. New scheduler: `ps2xRuntime/include/ps2_scheduler.h` (221 lines),
`ps2xRuntime/src/lib/ps2_scheduler.cpp` (1,249 lines), `ps2xRuntime/src/lib/ps2_fiber.h`,
`ps2xRuntime/include/ps2_dispatch_history.h`, `ps2xRuntime/include/ps2_syscall_override_state.h`.

Mechanism 3a — async-callback stack pool (`ps2_runtime.h:271-299`, constants at :272-273):

```cpp
// Async callback stack pool [floor, top): kernel-reserved guest memory. See
// the pool layout comment in ps2_runtime.cpp for why this range is disjoint
// from every other guest allocation.
constexpr uint32_t kAsyncCallbackStackFloor = 0x00080000u;
constexpr uint32_t kAsyncCallbackStackTop = 0x00100000u;
```

plus `kAsyncCallbackFallbackSp = kAsyncCallbackStackTop - 0x10u` ("NOT PS2_RAM_SIZE-0x10 — that address
is inside the guest's own main stack ... running a handler there would corrupt live guest frames") and
`KernelStackPool::carve()` (downward-carving cursor, re-armed by `loadELF()`).

Mechanism 3b — N=1 fiber cooperative scheduler (`ps2_scheduler.h:4-13` header comment):

```
// ps2_scheduler.h — public API for the N=1 fiber cooperative scheduler.
//
// Exactly one dedicated host OS thread (g_guest_thread, the "guest executor")
// runs all guest fibers. This eliminates cross-thread swapcontext UB structurally.
```

IRQ/alarm/RPC delivery model (`ps2_scheduler.h:155-164`): host worker threads borrow the guest via
`async_guest_begin()`/`async_guest_end()` ("Acquire the \"guest token\": blocks until no fiber is
executing guest code"), normally through `struct AsyncGuestScope` RAII (`:213-219`); `yield_point()`
sampled every 128 back-edges (`:166-172`); stale-wakeup-safe external wakeups via `FiberToken`
generation+tid (`:117-127`); `arm_park()`/`block_current()` park protocol (`:77-103`).

| Rung | SSX 3 relevance |
|---|---|
| handler/alarm stacks | 3a pool `[0x80000,0x100000)` is the SAME range as our P1f fix — already converged, nothing further |
| dispatch | 3b is a whole-scheduler replacement (fibers + guest token), not a portable hunk; the `FiberToken` stale-wakeup guard is the portable idea |
| other | old base — every other hunk is drift, not a borrow candidate |

### M6 — MrCool `@7978365` (318 entries; old base + feature work)

Tree diff dominated by drift and large feature subsystems (EE timing/cycle models, VU recompiler,
GS Vulkan backend, save states, debug server, ~100 new test files). Mechanism read directly.

Mechanism 6 — callbacks on interrupted SP + BIOS fallback (`ps2_runtime.cpp:322-324` constants,
`PS2Runtime::beginAsyncCallbackInvocation` `:2561`, stack selection `:2623-2636`):

```cpp
    // RAC1's BIOS VSync entry captured in PCSX2 uses this handler stack.
    // The idle PC is the BIOS EENULL continuation used when no guest thread
    // owns the interrupted boundary.
    constexpr uint32_t kEeBiosInterruptHandlerStack = 0x01FFFC20u;
    constexpr uint32_t kEeBiosIdleThreadPc = 0x00081FC0u;
```

```cpp
    scope.m_stackTop = kEeBiosInterruptHandlerStack;
    const uint32_t interruptedSp =
        static_cast<uint32_t>(
            _mm_cvtsi128_si32(
                scope.m_interruptedContext.r[29]));
    const uint32_t alignedSp =
        interruptedSp & ~0xFu;
    if (!scope.m_idle &&
        alignedSp >= 0x10u &&
        alignedSp <= PS2_RAM_SIZE)
    {
        scope.m_stackTop = alignedSp;
    }
```

(plus private-register-context isolation for the callback in the same function, `:2600-2622` quoted
in the borrowable table.) Scheduler context: no `EeScheduler.cpp`; uses `ee_thread_scheduler.h` (532
lines) + `ee_thread_scheduler.cpp` (1,673 lines) + `ee_scheduler_executor.h`.

Bonus mechanism 6b — analyzer folds ORI/ADDIU low halves (LUI+ORI fix class, P1h's rung, included for
corroboration only): `ps2xAnalyzer/src/elf_analyzer.cpp` `tryResolveLuiBase` (8-instruction window,
recursive):

```cpp
            if ((prev.opcode == OPCODE_ADDIU || prev.opcode == OPCODE_ORI) && prev.rt == reg)
            {
                uint32_t hiBase = 0;
                if (!tryResolveLuiBase(instructions, pos, prev.rs, hiBase))
                {
                    return false;
                }
                if (prev.opcode == OPCODE_ADDIU)
                {
                    baseAddr = hiBase + static_cast<uint32_t>(static_cast<int32_t>(static_cast<int16_t>(prev.immediate))));
                }
                else
                {
                    baseAddr = hiBase | static_cast<uint32_t>(prev.immediate);
                }
                return true;
            }
```

| Rung | SSX 3 relevance |
|---|---|
| handler/alarm stacks | 6 runs callbacks on the interrupted SP (aligned) with a PCSX2-captured BIOS fallback — third stack-model data point beside P1f-reserved and M1-borrowed |
| other | 6b corroborates the P1h fix class (P1h owns it); all other MrCool hunks are old-base drift or far-future subsystems |

### M7 — GTT `#222@c4d099b` (2 files; full bodies)

`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` + `ps2xTest/src/ps2_runtime_kernel_tests.cpp`.
Full runtime diff:

```diff
@@ -36,6 +36,17 @@
     constexpr uint64_t kAlarmTickMicroseconds = 64u;
     constexpr uint32_t kDebugPublishDispatchInterval = 4096u;
 
+    bool eeInterruptsEnabled(const R5900Context &context)
+    {
+        constexpr uint32_t kStatusIe = 1u << 0u;
+        constexpr uint32_t kStatusExl = 1u << 1u;
+        constexpr uint32_t kStatusErl = 1u << 2u;
+        constexpr uint32_t kStatusEie = 1u << 16u;
+        const uint32_t status = context.cop0_status;
+        return (status & (kStatusIe | kStatusEie)) == (kStatusIe | kStatusEie) &&
+               (status & (kStatusExl | kStatusErl)) == 0u;
+    }
+
@@ -358,6 +369,12 @@
     if (m_checkpointPending.load(std::memory_order_acquire) ||
         m_stopRequested.load(std::memory_order_acquire))
+    {
+        return true;
+    }
+
+    const GuestThread *running = currentThread();
+    if (m_rescheduleRequested && running != nullptr && eeInterruptsEnabled(running->activeContext()))
     {
         return true;
     }
@@ -374,9 +391,12 @@
         return false;
     }
 
-    const GuestThread *running = currentThread();
     if (running != nullptr && hasReadyAtOrAbovePriority(running->currentPriority))
     {
+        if (!eeInterruptsEnabled(running->activeContext()))
+        {
+            return false;
+        }
         m_rescheduleRequested = true;
         m_timeSliceExpired = true;
         return true;
@@ -1726,6 +1746,10 @@
     GuestThread *self = currentThread();
     assert(self != nullptr);
+    if (!eeInterruptsEnabled(self->activeContext()))
+    {
+        return;
+    }
     enqueueReady(*self, !m_timeSliceExpired);
```

Test added (`ps2_runtime_kernel_tests.cpp` `@@ -831,7 +831,36 @@`): "time-slice preemption waits
until EE interrupts are enabled" — `cop0_status = IE` alone defers `checkpointDue`, `IE|EIE` makes it due.

| Rung | SSX 3 relevance |
|---|---|
| dispatch | DI-gated preemption: with SSX 3's main thread spinning at `0x391330` with checkpoints yielding ~300/period, this decides whether time-slice rotation can interrupt DI regions — next-rung scheduling correctness |
| other | none |

### M10 — hedge `#235@cfcd341` (2 files; full bodies)

`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` + `ps2xTest/src/ps2_runtime_kernel_tests.cpp`.
Full runtime diff:

```diff
@@ -1251,6 +1251,10 @@
 void EeScheduler::dispatchIrq(bool dmac, uint32_t cause)
 {
+    if (m_executorThread == std::thread::id{})
+    {
+        m_executorThread = std::this_thread::get_id();
+    }
     assertExecutor();
@@ -1453,7 +1457,7 @@
 void EeScheduler::bindMainContextForSyscall(R5900Context &ctx, uint8_t *rdram)
 {
-    if (m_executorThread == std::thread::id{})
+    if (m_executorThread == std::thread::id{} || m_threads.empty())
```

Test added: "an early dispatchIrq without reset cannot break a later syscall bind".

| Rung | SSX 3 relevance |
|---|---|
| dispatch | hardens boot-ordering (IRQ before `reset()`); SSX 3 boots past this point already — no open rung |
| other | none |

### M12 — Sinan `#211@8dc8b54` (5 files; full bodies)

`ps2xRecomp/src/lib/control_flow_analyzer.cpp`, `ps2xRuntime/include/ps2_runtime.h`,
`ps2xRuntime/src/lib/Kernel/Syscalls/System.cpp`, `ps2xRuntime/src/lib/ps2_runtime.cpp`,
`ps2xTest/src/code_generator_tests.cpp`. Full diffs:

```diff
--- control_flow_analyzer.cpp
@@ -135,14 +135,6 @@
         for (const auto &inst : instructions)
         {
-            // A guest-installed syscall handler runs as a separate invocation,
-            // so the scheduler resumes this thread at syscall+4 and needs an
-            // entry point there. +4, not +8: syscall has no delay slot.
-            if (inst.opcode == OPCODE_SPECIAL && inst.function == SPECIAL_SYSCALL)
-            {
-                queueResumeEntryTarget(inst.address + 4u);
-            }
-
--- ps2_runtime.h (R5900Context constructor)
-        // Status as the EE kernel leaves it at handoff. IE (bit 0) and EIE
-        // (bit 16) are separate enables and guest code reads both; libkernel's
-        // StartThread refuses to run while IE is clear.
-        cop0_status = 0x00010001; // EIE | IE
+        // cop0_status = 0x400000; // BEV set, ERL clear, kernel mode
+        // 0x00400000 = BEV (Boot Exception Vectors).
+        // 0x00000000 = Normal mode (after BIOS handoff).
+        cop0_status = 0x00000000;
--- System.cpp (guest syscall override hook)
         scheduler.invokeCurrent(std::move(invocation));
+        // The invocation is queued and the caller must not fall through to the
+        // built-in handler. Falling off the end of a non-void function here was
+        // undefined behaviour: whatever happened to be in the return register
+        // decided whether the built-in ran as well as the override.
+        return true;
--- ps2_runtime.cpp (reset path)
-    // Assign rather than memset: R5900Context's constructor zeroes itself and
-    // then applies the COP0 reset values, which a memset here would discard.
-    m_cpuContext = R5900Context{};
+    std::memset(&m_cpuContext, 0, sizeof(m_cpuContext));
```

plus removal of the matching `makeSyscall` helper + "syscall marks the following instruction as a
resume entry" test in `code_generator_tests.cpp`.

| Rung | SSX 3 relevance |
|---|---|
| dispatch | the `return true` hunk fixes UB (override + built-in double-dispatch); SSX 3 `SetSyscall` count is 8 in block 0 — same hook |
| other | the `cop0_status = 0` + `memset` + resume-entry-removal hunks CONTRADICT upstream #214 (IE set at handoff); recorded as-is, see borrowable table for split |

### Bonus — phmdacosta `ee-timer@e465b4d` (68 entries; old base, NOT M4)

Old-base checkout (no `EeScheduler.cpp`); timer mechanism read directly. `EeTimer` struct
(`ps2_memory.h:460-468`): `count/mode/compare/hold` + `lastHostNs/fractionNs` sub-tick remainder;
registers deliberately NOT in `m_ioRegisters` ("concurrent operator[] on that unordered_map can rehash
under another thread's iterator", `:470-473`); `m_pendingTimerCauses` bitmask indexed by INTC cause 9..12.
Bases `kEeTimerBase[4] = {0x10000000, 0x10000800, 0x10001000, 0x10001800}` (`ps2_memory.cpp:146`), causes
`{9,10,11,12}` (`:149`), MODE bits CLKS/ZRET/CUE/CMPE/OVFE/EQUF/OVFF with write-1-to-clear (`:152-158`).
Consumer (`Interrupt.cpp:392-425` `serviceEeTimers`, called from the interrupt worker):

```cpp
        PS2Memory &memory = runtime->memory();
        memory.advanceEeTimers();

        const uint32_t causes = memory.consumePendingTimerCauses();
        if (causes == 0u)
        {
            return;
        }

        for (uint32_t cause = kIntcTimer0; cause <= kIntcTimer3; ++cause)
        {
            ...
                PS2Runtime::GuestExecutionScope guestExecution(runtime);
                PS2Runtime::DeferredGuestYieldScope deferYield(reschedulePending);
                dispatchIntcHandlersForCause(rdram, runtime, cause);
```

with the comment: "Nothing fires unless the guest itself armed the timer ... the SDK's timer ISR reads
those flags and returns immediately if it finds none, so delivering the cause speculatively both
achieves nothing and risks running guest code before the game has finished setting itself up."

| Rung | SSX 3 relevance |
|---|---|
| alarm/IRQ lifecycle | full EE-timer HLE (registers + host-clock advance + INTC 9..12 delivery); SSX 3 shows `SetAlarm` only in block 0 and no timer waits — above the current rung, below VIF/GS |
| other | old base — remaining 60+ entries are drift |

## 2. Q2 — bt3-recomp: diff a WORKING port (90 min cap)

Target: `/Volumes/Extreme SSD/q2-recomp-scan/z3xox_bt3-recomp` @ `4b8a766` ("Merge pull request #20").
Baseline: our fork at `6046260` (exported to `/tmp/p4/ourfork-6046260`).
Tree diff: 205 entries (89 bt3-only paths: `games/`, `mods/`, `tools/`, `docs/`, `tasks/`, `textures/`,
GPU renderer, netplay, SDL UI, GS replay harness, overlay table). bt3 is a full-fork divergence on an
OLD base: **no `EeScheduler`** (no `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, zero `eeScheduler`
references in `ps2_runtime.cpp`); its scheduler is a cooperative round-robin guest-token policy gated on
`PS2X_SCHED=1` (`ps2_runtime.cpp:1246-1258`, "fibers replace HOW a guest thread waits for the token, not
the round-robin policy"), optional fibers via `PS2X_FIBERS` (`ps2_fiber.h` 61 lines).
README status (`README.md:168-169`): "Playable: boots through logos and title, menus work, and fights
render in the GPU path at close to the engine's 30 fps cap". License: GPL-3.0 (P3 §8 re-cite: compatible).

### Q2a — boot/loader path

| # | Difference | bt3 file:line | our `6046260` file:line |
|---|---|---|---|
| B1 | Same live shape (`initialize` → `loadELF` → `run()`); bt3 adds ~25 baked `PS2X_*` env defaults (GPU path, barrier serving, `PS2X_BT3_CDTICK`, `PS2X_SCHED`, `PS2X_FORCE_MC`, `PS2X_ASYNC_KICK=1`) unless `PS2X_NODEFAULTS=1`, game-ID title, settings overlay, GS replay harness (diagnostic, `PS2X_GS_REPLAY`-gated) | `ps2xRuntime/src/main.cpp:551-578` (defaults), `:694-700` (`loadELF`/`run`) | `ps2xRuntime/src/main.cpp:147-151` ("Using argv boot path"), `:223-239` (`loadELF`/`run`) |
| B2 | `PS2X_CD_IMAGE` env wires `IoPaths.cdImage`; memory cards in `savedata/` beside deploy root | `ps2xRuntime/src/lib/ps2_runtime.cpp:2005-2035` (`configureIoPathsFromElf`; quote below) | `ps2xRuntime/src/lib/ps2_runtime.cpp:1020-1037` (no `cdImage` source; `mcRoot = elfDirectory / "mc0"`) |
| B3 | Second overlay function table for recompiled `DBZP.BIN` overlay (base `0x334c00`), `runner_overlay/overlay_register.cpp` | `ps2xRuntime/src/lib/ps2_runtime.cpp:2037-2043` (`g_ps2OverlayFunctionTable*` externs) | single dense table only (`replaceFunction` errors outside it) |
| B4 | One-script port pipeline (detect/deps/build/package) + overlay patch scripts + Ghidra decompiler | `games/bt3/setup.py:1-19`, `apply_overlay_patches.py`, `gen_overlay.py`, `ps2xRecomp/tools/ghidra/DecompileBt3.java` | manual analyzer+recomp+copy flow (P1) |

B2 bt3 body (`ps2_runtime.cpp:2005-2035`):

```cpp
void PS2Runtime::configureIoPathsFromElf(const std::string &elfPath)
{
    ...
    if (!paths.elfDirectory.empty())
    {
        paths.hostRoot = paths.elfDirectory;
        paths.cdRoot = paths.elfDirectory;
        // [deploy] Memory cards live in savedata/ (beside data/), not data/mc0.
        paths.mcRoot = paths.elfDirectory.parent_path() / "savedata";
    }

    // Allow pointing the CDVD backend at a disc image via environment variable.
    if (const char *cdImageEnv = std::getenv("PS2X_CD_IMAGE"))
    {
        if (cdImageEnv[0] != '\0')
        {
            paths.cdImage = std::filesystem::path(cdImageEnv);
        }
    }
```

### Q2b — `[mmio]` TOML handling (the highest-value row)

| # | Difference | bt3 file:line | our `6046260` file:line |
|---|---|---|---|
| M1 | Analyzer MMIO detector: IDENTICAL files (byte-equal) — bt3's detector has the SAME LUI-only fold | `ps2xAnalyzer/src/elf_analyzer.cpp` (no diff) | same path (P1g cites `:424-456`) |
| M2 | Checked-in `[mmio]` map shows the SAME fold: 183 entries, 160 × `0x10000000` | `games/bt3/config.toml.in:588+` (`"0x2bb260" = "0x10000000"` etc.) | `$W/P1/ssx3.toml` (273 entries, 249 × `0x10000000` per P1g) |
| M3 | MMIO codegen IGNORES the folded value: emits `runtime->Load32(rdram, ctx, ADD32(GPR_U32(ctx, rs), imm))` — the TOML hit is only a boolean `isMmio` marker; the address is computed from LIVE registers at runtime. bt3 is immune to the fold by construction. | `ps2xRecomp/src/lib/instruction_translator.cpp:26-45` (`genRead`/`genWrite`), `:87-88` (`OPCODE_LW` passes `ADD32(GPR_U32(ctx, rs), imm)`) | `ps2xRecomp/src/lib/instruction_translator.cpp:71-80` (`effectiveMemoryHintFor` bakes `inst.mmioAddress`), `:91-98`/`115-122` (emit `addressLiteral(resolvedAddress)`) — the folded constant is baked |
| M4 | TOML `[mmio]` read/write paths identical | `ps2xRecomp/src/lib/config_manager.cpp:130-145,283-286` | same file `:129-144,281-284` |

M3 bt3 body:

```cpp
        auto genRead = [&](int width, const std::string &addr)
        {
            if (inst.isMmio)
            {
                return fmt::format("runtime->Load{}(rdram, ctx, {})", width, addr);
            }
            return fmt::format("READ{}({})", width, addr);
        };
...
        case OPCODE_LW:
            return fmt::format("SET_GPR_S32(ctx, {}, (int32_t){});", inst.rt, genRead(32, fmt::format("ADD32(GPR_U32(ctx, {}), {})", inst.rs, inst.immediate)));
```

This is exactly the "dynamic MMIO dispatch" alternative P1g P8-5 named next to P1h's static fix.

### Q2c — GS/GPU-path init

| # | Difference | bt3 file:line | our `6046260` file:line |
|---|---|---|---|
| G1 | GPU renderer selected by `PS2X_GPU=1` (defaulted ON in main): `GsGpuRenderer::enabled()` → `ps2GpuRenderer()` singleton serves present/barriers/textures | `ps2xRuntime/src/lib/ps2_gs_gpu_renderer.cpp:1804-1808`, `ps2xRuntime/src/main.cpp:565` (`def("PS2X_GPU", "1")`) | CPU backend only (`gs_cpu_backend.cpp`); `GS::setRasterBackend` exists (`gs_frontend.cpp:1633`) but nothing selects a GPU backend |
| G2 | Whole GPU stack bt3-only: `src/gfx/` (GL/D3D11 contexts, `gs_gl.*`, `gs_rt.*`, `gs_resources.*`), `ps2_gs_gpu.cpp`, `ps2_gs_gpu_renderer.cpp`, `ps2_gs_pgs.cpp` + headers | `ps2xRuntime/src/gfx/*`, `ps2xRuntime/src/lib/ps2_gs_gpu*.cpp` | absent |
| G3 | Async DMA-kick worker (`PS2X_ASYNC_KICK=1` defaulted ON): `enqueueKickJob` + `kickWorkerLoop` with SwapFrame backpressure (cap 2 frames) | `ps2xRuntime/src/lib/ps2_memory.cpp:2410-2443` (`asyncKickEnabled`, `ensureKickWorker`, `enqueueKickJob`) | synchronous DMA in `writeIORegister` |
| G4 | Present path branches on `gpuMode` (textures, barriers, D3D/GL present, FMV overlay) | `ps2xRuntime/src/lib/ps2_runtime.cpp:6568,6687-6870` | `UploadFrame` CPU path (`ps2_runtime.cpp:2657-2659`) |

### Q2d — CD handling

| # | Difference | bt3 file:line | our `6046260` file:line |
|---|---|---|---|
| C1 | Fully SYNCHRONOUS model: `sceCdRead` copies inline via `readCdSectors(lbn, sectors, rdram+offset)` and returns 1; `sceCdSync` always returns 0 (completed); `sceCdCallback`/`sceCdInitEeCB` are no-op stubs (return 0/1, register nothing, invoke nothing). bt3 sidesteps the async-CD thread model entirely. CD.cpp 955 lines vs ours 1,098; diff 1,084 lines. | `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:94-368` (`sceCdRead`, `tryRead`→`readCdSectors` at `:189-196`), `:369-372` (`sceCdSync`), `:399-402` (`sceCdCallback`), `:447-450` (`sceCdInitEeCB`) | `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp:37-39` (`g_cdCallbackFn/Gp/StackTop`), `:66-98` (`queueCdCallback` → `eeScheduler().queueInvocation`), `:403` (queued on read), stream-production timing `:27-43,101-189` |
| C2 | Game-specific completion pump: `bt3PumpCdTick` runs the game's tick dispatcher `FUN_0028a3b0` each (gated) vblank under `GuestExecutionScope`, because "with no IOP firing a CD completion interrupt, nothing drives that tick" | `ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp:346-430` (`pumpGuestFunction` `:364-393` with `getAsyncHandlerStackTop`, 1M-step cap; gate `:424+`) | no guest-function pump |
| C3 | AFS sector-remap diagnostics (`PS2X_AFSREMAP`, `PS2X_AFSSWAP`), ADX rate sniffing, `[cdload]` counters | `CD.cpp:59-92` (`noteAdxHeaderIfPresent`), `:163-188` (remaps) | absent |

### Q2e — scheduler/IRQ posture (context row)

bt3 has no `EeScheduler`, no `queueInvocation`, no `m_pendingInvocations`; IRQ/DMAC/alarm lifecycles
live in the old `Interrupt.cpp` worker + `GuestExecutionScope` model. Consequence for borrowing:
bt3's thread-lifecycle mechanics do NOT transfer to our `#184`-era scheduler; its transferable wins are
M3 (dynamic MMIO dispatch), C1/C2 (sync-CD + pump pattern), G1-G4 (GPU/async-kick architecture), B2/B3.

## 3. Q3 — Other downstreams, boot learnings only (30 min each)

### sm2 — `saltyboosack-blip_spider-man-2-ps2-recomp` @ `98aef96` (base `f4309cd`, pre-EeScheduler)

Rung reached: boots through pink/black-screen blockers → memory-card warning → legal splash on Cross
input; Activision + Spider-Man logos render; stuck at 4/5 legal-splash `TEX0` descriptors
(`README.md:13-20`, `docs/HANDOFF.md:8-25`). Tree diff vs `upstream-baseline`: 109 entries, dominated by
old-base drift (no `EeScheduler.cpp`, old GS layout) + new IOP modules.

| Fix/workaround we lack | File:line |
|---|---|
| LIQUID stream completion via polled status (`response[offset + 0x35u] = 1u; // completed event`) + `PendingRead{token, callback, callbackContext}` — RPC-level HLE that delivers completion WITHOUT invoking guest code (poll, not callback); cleared the "LIQUID scheduler loop" at `0x38D8B8` | `ps2xIOP/src/modules/liquid.cpp:124-131` (struct), `:284-291` (completed event) |
| VIF1/DMAC interrupt contract notes: VIF1 DMA completion = DMAC cause 1 via DMAC path; INTC 5 only from VIFcode IRQ/exception; unconditional `queueIntcCause(5)` on DMA completion experimentally INVALID ("woke the game's VIF callback for empty zero-code tags but did not advance execution") | `docs/RESEARCH_FINDINGS.md:29-46` |
| New IOP HLE modules `padman` (110 lines), `loadfile` (134), `cdvd` (248), `liquid` (529) | `ps2xIOP/src/modules/*.cpp` |

### halogen — `0xjjjjjj_halogen` @ `5383328`

Rung reached: `halogen-headless` boots recompiled C++ to steady state ~55 FPS, all subsystems running;
progresses boot → engineInit → gameInit → gameLoop → runFrontEnd (main menu); live pad input drives
menus (`README.md:62-63`). Hangs later at menu screens on missing-texture `lumpFind` data (`README.md:69`).
NOTE: the nested `vendor/PS2Recomp` fork is NOT in this checkout (only `notes/ps2recomp-build.md`
references it), so fork diffs were unrecoverable; learnings below are from halogen's own tree.

| Fix/workaround we lack | File:line |
|---|---|
| Cooperative-yield discipline: main dispatch thread registers via `ps2_syscalls::setMainThread()` — "only the main thread polls VBlank in cooperative WaitSema (worker threads just yield)"; dispatch holds the guest-exec mutex (`README.md:66` cites this + `ReferThreadStatus` semantics + KbmReader IOP spin fixes, all in the absent fork) | `src/main_headless.cpp:271-273` (+`:326-328` mutex'd dispatch). `setMainThread` does NOT exist in our `6046260` (grep-verified) |
| Headless boot harness pattern: `memory().initialize()` only (no window) → `registerAllFunctions` → `loadELF` → manual dispatch loop with trace/max-calls + stuck-PC watchdog | `src/main_headless.cpp:213-280,326-348` |
| `-msse4.1` build fix for `_mm_extract_epi32` in public headers (NixOS, blocks `-march=native`) | `notes/ps2recomp-build.md:31-46` |
| ELF-load RAM patch pattern (`HALOGEN_DEBUG_MENU` writes guest `0x17FA04`) + `cdRoot` post-load override via `setIoPaths` | `src/main_headless.cpp:234-249` |
| Recomp config: libc-name stubs + `skip = ["abort", "exit", "_exit"]`, no `[mmio]` section | `configs/champions-of-norrath.toml:1-35` |

### drakengard — `sorachi00_ps2recomp-drakengard` @ `2f5d48c` (tree-IDENTICAL to `sorachi00-main`)

Full SHA `2f5d48c14d5dc86f9628b2f39b5c4fb69fae5268` equals `sorachi00-main` full SHA; tree diff
`sorachi00-main` vs drakengard = 0 entries (resolves P3 §8.7 P3 at full-SHA + tree level).
Rung reached: unstated (11-line README, no status; `README.md:1` "Fork of PS2Recomp focused on
Drakengard"). One Q3 row:

| Fix/workaround we lack | File:line |
|---|---|
| None beyond M2 (same tree): `sceCdLayerSearchFile` + `cdvd`/`ezsound` IOP services + nesting guard (see Q1 M2). Port ships `tools/drakengard_merged.toml` + `tools/drakengard.csv` as its recomp inputs (per `README.md:7-8`) | `tools/drakengard_merged.toml`, `tools/drakengard.csv` (sizes §7) |

### reo — `sp00nznet_reo` @ `73ad3c9` (own native runtime; `third_party/PS2Recomp` EMPTY — submodule uninitialized)

Rung reached: File #1 boots to main loop, 60 FPS, 6 active tasks, textured rendering through GS
software rasterizer (title screen pixel-accurate); File #2 pending (`README.md:193-207,246`).
reo uses PS2Recomp only as the MIPS→C++ tool (`recomp/CMakeLists.txt:13`
`PS2RECOMP_DIR=third_party/PS2Recomp`); its `runtime/` is a from-scratch native bridge, so no
PS2Recomp-runtime diff exists.

| Fix/workaround we lack (patterns, different codebase) | File:line |
|---|---|
| Timer WITHOUT EE-timer hardware: `reo::Timer` is a host-clock wrapper (QPC init, `elapsed_us`, `bus_clock_ticks` @147.456MHz, `ee_clock_ticks` @294.912MHz, frame pacing + `wait_for_vsync`) — textured main loop reached with NO timer-register emulation and NO INTC 9..12 delivery. Evidence EE timers are not on every engine's critical boot path | `runtime/timer/timer.h:1-48`, `runtime/timer/timer.cpp` (82 lines) |
| Synchronous CDVD file-map: `read_file`/`read_sectors` redirect to extracted `game_data/` via prebuilt map (85 files); no async completion | `runtime/cdvd/cdvd.h:1-46`, `runtime/cdvd/cdvd.cpp` |
| SIF RPC bridge to native CDVD/PADMAN/MCSERV/LIBSD handlers (`SIF_CDVD = 0x80000592` etc.) | `runtime/iop/iop_hle.h:22-52` |
| 25+ boot-chain bypasses catalogued (SIF DMA status check, IOP task-wait bypass, TIM2 validation bypass, HLE allocators, mid-function entry registration) — the "bypass, don't emulate" ladder strategy that reached textures | `README.md:224-233` |

## 4. Q4 — Delivery point for message-not-nesting (30 min cap; P3 §8.4 NOT redone)

One row. References are our fork at `6046260`
(`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, identical at HEAD `f2149e7` — P1h touched only the analyzer).

| Item | Value |
|---|---|
| Enqueue function | `EeScheduler::queueInvocation` (`EeScheduler.cpp:1370-1376`): `assertExecutor(); invocation.sequence = ++m_invocationSequence; m_pendingInvocations.push_back(...); m_checkpointPending.store(true, ...)` — a queued-event handoff lands HERE (or a kind/tag-carrying sibling); the queue is `m_pendingInvocations` (`ee_scheduler.h:434`, `std::deque<GuestInvocation>`) |
| Dequeue function + lines | `EeScheduler::run()` (`EeScheduler.cpp:229+`), TWO pop sites: **Site B** `:489-504` (a thread is running: `if (!m_pendingInvocations.empty())` → pop front `:491-492` → sp-assign-if-0 `:498-501` → `running->invocations.push_back` `:502` → `continue` `:503` re-enters the loop and runs the event on the owning thread's own stack); **Site A** `:388-410` (no ready thread: owner = `acquireInvocationThread()` `:390`, same pop/assign/push) |
| What the dequeue site would check | At Site B `:489`, before popping: (a) the pending event's OWNER is the running thread — NOTE `GuestInvocation` (`ee_scheduler.h:95-102`) carries `kind/sequence/tag/context/onComplete` but NO owner-thread field today, so the handoff must add one (or tag-encode the owner); (b) the running thread's invocation stack is idle/resumable — the check shape exists in M2 (`deferPendingInterrupt` + `back().started`, §1 M2) and as unconditional-pop today (`:489` pops regardless); kinds available: `Interrupt/Alarm/GsCallback/RpcCallback/SyscallOverride/ExitHandler/HleCall` (`ee_scheduler.h:84-93`) |
| Negative (what NOT to use) | `invokeCurrent` (`:1378-1391`) / `invokeCurrentSequence` (`:1393-1410`) push directly onto `currentThread()->invocations` and `throw EeDispatcherTransfer{}` — that IS the nesting path message-not-nesting replaces |

## 5. Borrowable-snippet table

Adaptation sketches are function-level prose, NOT applied. License column RE-CITES P3 §8.6 (no new verdicts).

| # | Mechanism → source (rev, file:line, quoted body) | Adaptation sketch to our fork at `6046260` (NOT applied) | License re-cite (P3 §8.6) |
|---|---|---|---|
| S1 | Borrowed handler stack (M1). TheTharin `7f29bbd`, `EeScheduler.cpp:191-196 dispatch` (3 sites) + `:1296 enqueue` + `:1913/:1943` vsync/alarm: `const uint32_t ownerSp = getRegU32(&owner->activeContext(), 29); const uint32_t invSp = (ownerSp > 0x20000u && ownerSp <= PS2_RAM_SIZE) ? ((ownerSp & ~0xFu) - 0x800u) : invocationStackTop();` + `sp deliberately left 0` at all 3 enqueue sites | In our `run()` Sites A (`:405-408`) and B (`:498-501`) and `invokeCurrent*`, replace the `invocationStackTop()` fallback with owner-sp-derived `(ownerSp & ~0xF) - 0x800` within the same range guard; at our IRQ (`:1293`), vsync, alarm enqueue sites leave `sp` 0 with the same comment. Coexists with or replaces the P1f reserved pool; keep `invocationStackTop()` as the out-of-range fallback | compatible (P3 §8.6: fork LICENSE GPL-3 v3 body) |
| S2 | No-preempt-active-IRQ + started gate (M2). Sorachi00 `2f5d48c`, `EeScheduler.cpp:255-264` + `ee_scheduler.h:103` (`bool started`) + `:1297` (`sp → 0u`): `const bool deferPendingInterrupt = !m_pendingInvocations.empty() && m_pendingInvocations.front().kind == GuestInvocationKind::Interrupt && hasActiveInterrupt;` gate `if (!empty && !defer && (invocations.empty() \|\| back().started))` | In our `run()` Site B (`:489`), add the `deferPendingInterrupt` conjunct + `started` flag set at our guest-execute point (`:553-560` region, mirroring their `:304-311`); zero handler sp at our `:1293` enqueue | compatible (P3 §8.6: BOTH checkouts GPL-3, fork-license question moot; full-SHA identity now confirmed §3/§7) |
| S3 | DMAC-drain-from-event-pump (M1). TheTharin `7f29bbd`, `EeScheduler.cpp` pump tail: `m_runtime.drainCompletedDmacHandlers(m_rdram);` | In our event-pump path (the `drainCompletedDmacHandlers` caller set / `processPendingEvents` `:2025`), add the same drain call so a thread blocked on a just-kicked transfer observes its completion | compatible (same fork LICENSE as S1) |
| S4 | Empty-transfer completion (M1). TheTharin `7f29bbd`, `ps2_memory.cpp` kick record + `processPendingTransfers` `startedChannels` arms + `ps2_memory.h` `m_dmaStartedChannels` | In our `writeIORegister` DMA-kick block (`:1268+`) record the kicked channel bit; in our `processPendingTransfers` OR the started bits into the `hadGif/hadVif0/hadVif1` completion arms so STR clears and `queueCompletedDmacCause` runs for zero-data kicks | compatible (same fork LICENSE as S1) |
| S5 | VIF IRQ→INTC 4/5 delivery (M1). TheTharin `7f29bbd`, `ps2_vif1_interpreter.cpp:77-92,315-324` (`queueIntcCause(4u/5u)`), `ps2_memory.h` queue + `ps2_runtime.cpp` drain loop into `dispatchIrq(false, cause)` | In our VIF interpreter IRQ-bit sites add `queueIntcCause`; add the mutex'd pending-cause vector + accessors to our `PS2Memory`; extend our `drainCompletedDmacHandlers` to forward consumed causes to `dispatchIrq` | compatible (same fork LICENSE as S1) |
| S6 | Rest-of-RAM heap limit (M1; possibly M13's substance). TheTharin `7f29bbd`, `System.cpp` SetupThread/SetupHeap + `ps2_runtime.cpp` `defaultGuestHeapLimitLocked`/`setGuestMainStackBase` + `EndOfHeap` | In our `SetupThread` record `initialStack` via a new setter; in our `SetupHeap` treat size 0/`0xFFFFFFFF` as limit-0 → resolve to recorded stack base with `0x01F00000u` fallback; return `guestHeapLimit()` from `EndOfHeap`; raise async-callback floor above the configured limit | compatible (same fork LICENSE as S1) |
| S7 | Overlay side table (M1). TheTharin `7f29bbd`, `ps2_runtime.cpp` `m_registeredFunctions` in `replaceFunction`/`hasFunction`/`lookupFunction` + `runner/title/*.cpp` glob | In our `replaceFunction`, store out-of-dense-range addresses in a side map consulted by `hasFunction`/`lookupFunction` instead of returning false; add the title-overlay glob to our `ps2xRuntime/CMakeLists.txt` | compatible (same fork LICENSE as S1) |
| S8 | DI-gated preemption (M7). GTT `c4d099b`, `EeScheduler.cpp` `eeInterruptsEnabled` (`:39-49` fork-side) + `checkpointDue` gates + yield gate (`:1749-1752` fork-side) | In our `checkpointDue` (`:616`) and time-slice/yield path, add the `(IE|EIE)==set && (EXL|ERL)==clear` gate with the same early-`return true` for checkpoint/stop; port the kernel test | compatible (P3 §8.6: fork LICENSE GPL-3) |
| S9 | Lazy executor bind (M10). hedge `cfcd341`, `EeScheduler.cpp` `dispatchIrq` claim-if-unset + `bindMainContextForSyscall` `m_threads.empty()` OR | In our `dispatchIrq` (`:1513`) claim `m_executorThread` when unset; in our `bindMainContextForSyscall` add the `m_threads.empty()` disjunct; port the kernel test | compatible for `cfcd341` (P3 §8.6) |
| S10 | Syscall-override `return true` ONLY (M12 fragment). Sinan `8dc8b54`, `System.cpp` `tryResolveGuestSyscallOverride`-region: `return true;` after `invokeCurrent` + UB comment | In our override hook (`System.cpp`, same shape), return true after queueing so the built-in handler cannot also run. Do NOT port the `cop0_status = 0`, `memset`, or resume-entry-removal hunks (they contradict #214) | compatible (P3 §8.6: fork LICENSE GPL-3) |
| S11 | `sceCdLayerSearchFile` + CDVD RPC service (M2). Sorachi00 `2f5d48c`, `CD.cpp:170-213` + `CD.h` + `iop_host.h` virtual + `cdvd.cpp` (`CD_SERVER_SEARCHFILE = 0x80000597u`) + `ezsound.cpp` | In our `CD.cpp`/`CD.h` add the layer-search entry; extend our `IopHost` with the virtual + adapter override; add the two IOP service factories to our `builtin_profiles.cpp`/`module_factories.h`. Single-layer SSX 3 does not need it today | compatible (same as S2) |
| S12 | EE-timer HLE (bonus, NOT M4). phmdacosta `e465b4d`, `ps2_memory.h:348-481` (`EeTimer`, mutex, `m_pendingTimerCauses`), `ps2_memory.cpp:144-240` (bases/causes/modes/advance/read/write) + `:604-626` (`advanceEeTimers`/`consumePendingTimerCauses`), `Interrupt.cpp:392-425` (`serviceEeTimers` under `GuestExecutionScope`) | In our `PS2Memory` add the out-of-`m_ioRegisters` timer block + advance/consume pair; drive it from our interrupt/vblank worker and deliver causes 9..12 via our `dispatchIrq(false, cause)` (NOT the old `dispatchIntcHandlersForCause` shape — that symbol is pre-#184) | compatible-if-same-fork (P3 §8.6: checkout rev differs from M4/M14 revs; fork LICENSE GPL-3) |
| S13 | FiberToken stale-wakeup guard IDEA (M3). smmathews `c7b2edc`, `ps2_scheduler.h:27-35,117-127` (generation+tid token, validated external wakeup) | If/when our scheduler gains cross-thread wakeups, validate wakeups against a generation-tagged token instead of bare tid. The N=1 fiber scheduler itself is a replacement, not a hunk — not sketched | compatible (P3 §8.6: fork LICENSE GPL-3) |
| S14 | Interrupted-SP callback + private context (M6). MrCool `7978365`, `ps2_runtime.cpp:322-324` (`kEeBiosInterruptHandlerStack = 0x01FFFC20u`) + `beginAsyncCallbackInvocation:2623-2636` stack pick + `:2600-2622` private-context isolation | In our invocation dispatch, consider interrupted-SP-anchored stacks with a captured (not top-of-RAM) fallback; isolate callback register writes from the interrupted continuation. Cross-architecture (their executor ≠ `EeScheduler`) — sketch only | compatible (P3 §8.6: fork LICENSE GPL-3) |
| S15 | DYNAMIC MMIO dispatch (bt3). `4b8a766`, `instruction_translator.cpp:26-45,87-88`: `runtime->Load{width}(rdram, ctx, ADD32(GPR_U32(ctx, rs), imm))` — TOML hit used as boolean only | ALTERNATIVE to P1h (P1h owns the static fix): in our `effectiveMemoryHintFor`, stop baking `inst.mmioAddress` and emit the dynamic `addr` expression for `isMmio` accesses. bt3's checked-in map proves the working end state tolerates 160 folded entries | compatible (P3 §4: bt3 LICENSE GPL-3.0) |
| S16 | Synchronous CD + `PS2X_CD_IMAGE` (bt3). `4b8a766`, `CD.cpp:94-450` (inline copy, Sync→0, Callback/InitEeCB no-ops) + `ps2_runtime.cpp:2025-2031` (`PS2X_CD_IMAGE` env) | In our `configureIoPathsFromElf` add the `PS2X_CD_IMAGE` env source (SSX 3 needs its image staged anyway); consider a sync-CD mode that skips `queueCdCallback` for engines that poll `sceCdSync` | compatible (same as S15) |
| S17 | Guest tick-function pump PATTERN (bt3). `4b8a766`, `Interrupt.cpp:346-430` (`pumpGuestFunction` under `GuestExecutionScope`, 1M-step cap, swap-gated) | If SSX 3 stalls on an undriven guest-side queue, pump its tick function from the vblank worker under `GuestExecutionScope` with a step cap and progress gate. bt3's `FUN_0028a3b0` is title-specific — the pattern is the borrow | compatible (same as S15) |
| S18 | LIQUID poll-completion (sm2). `98aef96`, `liquid.cpp:124-131,284-291` (`PendingRead` + `completed event` status byte) | For future IOP HLE services, deliver completion through guest-polled status rather than guest-code invocation where the protocol allows it | compatible (P3 §8.6 upgrade: sm2 LICENSE file EXISTS, GPL-3) |
| S19 | `FPU_CVT_W_S` truncate+clamp (M1). TheTharin `7f29bbd`, `ps2_runtime_macros.h`: `ps2_fpu_cvt_w_s` (truncate toward zero, clamp INT32_MIN/MAX) | In our `ps2_runtime_macros.h` replace the `nearbyintf` macro with the truncating helper; port `ps2_fpu_macros_tests.cpp` | compatible (same fork LICENSE as S1) |
| S20 | `translateFioMode` bit tests (M1). TheTharin `7f29bbd`, `FileIO.cpp`: test `O_RDONLY`/`O_WRONLY` bits individually (`O_RDWR` is `0x3`) | In our `translateFioMode`, apply the same per-bit tests so O_RDONLY opens of read-only host files stop failing with EACCES | compatible (same fork LICENSE as S1) |

Not borrowed: M4/M5/M8/M9/M11/M13/M14 (revs absent, §0); M12's `cop0_status=0`/`memset`/resume-removal
(contradict #214); smmathews/bt3/mrcool whole-scheduler replacements (architecture, not hunks);
thetharin GS-present/packet-builder/PMODE hunks (rungs SSX 3 has not reached — recorded in §1 for later).

## 6. Clone revs + paths (verified this session)

| Clone | Full SHA (`rev-parse HEAD`) / short | Path |
|---|---|---|
| upstream-baseline | `14b1e5c` (short verified; full = `14b1e5cb39b4af7e6fc12f9a29fdc751efde49d7` per P1) | `/Volumes/Extreme SSD/fork-survey/upstream-baseline` |
| thetharin-rogue-galaxy | `7f29bbd` | `/Volumes/Extreme SSD/fork-survey/thetharin-rogue-galaxy` |
| sorachi00-main | `2f5d48c14d5dc86f9628b2f39b5c4fb69fae5268` | `/Volumes/Extreme SSD/fork-survey/sorachi00-main` |
| smmathews-fiber-sched | `c7b2edc` | `/Volumes/Extreme SSD/fork-survey/smmathews-fiber-sched` |
| phmdacosta-ee-timer | `e465b4d` | `/Volumes/Extreme SSD/fork-survey/phmdacosta-ee-timer` |
| hedgeg0d-lazy-bind | `cfcd341` | `/Volumes/Extreme SSD/fork-survey/hedgeg0d-lazy-bind` |
| mrcool-main | `7978365` | `/Volumes/Extreme SSD/fork-survey/mrcool-main` |
| gtteancum-di-preempt | `c4d099b` (git index unreadable — AppleDouble `._*.idx` artifacts; all reads via `diff`, git untouched) | `/Volumes/Extreme SSD/fork-survey/gtteancum-di-preempt` |
| sinan-syscall-override | `8dc8b54` | `/Volumes/Extreme SSD/fork-survey/sinan-syscall-override` |
| our fork (P1f base for Q2/Q4) | `6046260` (HEAD `f2149e7` = 6046260 + P1h analyzer-only change; `EeScheduler` identical) | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` |
| bt3-recomp | `4b8a766` | `/Volumes/Extreme SSD/q2-recomp-scan/z3xox_bt3-recomp` |
| sm2 | `98aef96` (short; full `rev-parse` blocked by AppleDouble `._*.idx`, same as P3) | `/Volumes/Extreme SSD/q2-recomp-scan/saltyboosack-blip_spider-man-2-ps2-recomp` |
| halogen | `5383328` | `/Volumes/Extreme SSD/q2-recomp-scan/0xjjjjjj_halogen` |
| drakengard | `2f5d48c14d5dc86f9628b2f39b5c4fb69fae5268` — EQUALS sorachi00-main full SHA; tree diff 0 entries | `/Volumes/Extreme SSD/q2-recomp-scan/sorachi00_ps2recomp-drakengard` |
| reo | `73ad3c9` | `/Volumes/Extreme SSD/q2-recomp-scan/sp00nznet_reo` |

Sizes recorded where read: sorachi00 `tools/drakengard_merged.toml` 10,669 B, `tools/drakengard.csv`
370,146 B; sorachi00 `register_functions.cpp` 169,912 lines; thetharin `rg_game_override.cpp` 292 lines;
bt3 `config.toml.in` 5,272 lines ([mmio] 183 entries @ `:588+`); smmathews `ps2_scheduler.cpp` 1,249 lines;
mrcool `ee_thread_scheduler.*` 532 + 1,673 lines; sm2 `liquid.cpp` 529 lines; halogen `main_headless.cpp`
414 lines; reo `timer.*` 48 + 82 lines. No new clones; no clone over 200 MB touched.

## 7. Exact commands

All run from `/Users/bradrichardson/dev/ssx3` unless noted (CWD `fork-survey/` where shown).
Read-only: `git rev-parse/log/cat-file/show/archive`, `diff -rq/-ru/-u`, `grep/sed/awk/wc/head`, `ls`.
`git archive` wrote only to `/tmp/p4/` (scratch, outside the repo). No builds, no boots, no `git push`.

```
# Q1 rev inventory + history probe
cd "/Volumes/Extreme SSD/fork-survey"
for d in upstream-baseline thetharin-rogue-galaxy sorachi00-main smmathews-fiber-sched phmdacosta-ee-timer hedgeg0d-lazy-bind mrcool-main gtteancum-di-preempt sinan-syscall-override xjjjjjj-main dothack-gsfix dustindustindustin-main liorv63afk-main maxigasparini-main sh2dow-main trulio2-iop; do git -C "$d" rev-parse --short HEAD; done
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" rev-parse --short HEAD; git log --oneline -3
git -C <each fork> cat-file -t 14b1e5cb39b4af7e6fc12f9a29fdc751efde49d7   # absent everywhere (shallow)
git -C <each fork> log --oneline -6                                        # single commit each (depth-1)
git -C <fork> log --all --oneline | grep -i <7ea9a2c|184158a|9e00466|3096823>  # no hits (M4/M5/M13/M14 absent)
# Q1 file lists + bodies
diff -rq -x .git -x '._*' upstream-baseline <fork> > /tmp/p4/filelist-<fork>.txt   # x8 forks
diff -u upstream-baseline/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp <hedge|gtt>/.../EeScheduler.cpp
diff -u upstream-baseline/ps2xTest/src/ps2_runtime_kernel_tests.cpp <hedge|gtt>/.../ps2_runtime_kernel_tests.cpp
diff -ru -x .git -x '._*' upstream-baseline/ps2xRuntime thetharin-rogue-galaxy/ps2xRuntime > /tmp/p4/diff-thetharin-runtime.txt
diff -ru -x .git -x '._*' upstream-baseline/ps2xRuntime sorachi00-main/ps2xRuntime > /tmp/p4/diff-sorachi00-runtime.txt
diff -ru -x .git -x '._*' upstream-baseline/ps2xIOP sorachi00-main/ps2xIOP
diff -ru -x .git -x '._*' upstream-baseline/ps2xTest thetharin-rogue-galaxy/ps2xTest
diff -ru upstream-baseline/ps2xRecomp/src/lib/control_flow_analyzer.cpp sinan-syscall-override/... (etc. x5 files)
sed -n '230,320p' smmathews-fiber-sched/ps2xRuntime/include/ps2_runtime.h   # pool constants
(opened) smmathews-fiber-sched/ps2xRuntime/include/ps2_scheduler.h (221 lines) + src/lib/ps2_fiber.h (49)
sed -n '300,340p;2595,2660p' mrcool-main/ps2xRuntime/src/lib/ps2_runtime.cpp  # M6 hunks
sed -n '595,650p' mrcool-main/ps2xAnalyzer/src/elf_analyzer.cpp               # tryResolveLuiBase
grep -n timer phmdacosta-ee-timer/ps2xRuntime/include/runtime/ps2_memory.h + src/lib/ps2_memory.cpp
sed -n '340,380p;455,482p' phmdacosta-ee-timer/.../ps2_memory.h; sed -n '375,440p' .../Interrupt.cpp
# Q2 baseline export + diffs (quoted paths; an early unquoted-$U variant silently matched nothing and was redone)
mkdir -p /tmp/p4/ourfork-6046260 && git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" archive 6046260 | tar -x -C /tmp/p4/ourfork-6046260
diff -rq -x .git -x '._*' /tmp/p4/ourfork-6046260 "$BT" > /tmp/p4/filelist-bt3.txt   # 205 entries, 89 bt3-only
diff -u /tmp/p4/ourfork-6046260/ps2xAnalyzer/src/elf_analyzer.cpp "$BT/ps2xAnalyzer/src/elf_analyzer.cpp"  # empty
awk '/^\[mmio\]/{f=1;next} /^\[/{f=0} f' "$BT/games/bt3/config.toml.in" | ... distribution (183 entries)
grep -n -i mmio $BT/ps2xRecomp/src/lib/ps2_recompiler.cpp + instruction_translator.cpp (both sides)
sed -n '1,80p;87,110p' $BT/ps2xRecomp/src/lib/instruction_translator.cpp; sed -n '65,130p' <ours>
grep -n loadELF/configureIoPaths $BT + ours main.cpp/ps2_runtime.cpp; sed -n '540,600p;600,710p' $BT/.../main.cpp
sed -n '2005,2045p' $BT/ps2_runtime.cpp vs sed -n '1020,1045p' <ours> (configureIoPathsFromElf)
diff -u <ours>/CD.cpp $BT/CD.cpp > /tmp/p4/diff-bt3-CD.txt (1,084 lines); sed bodies :1-120, :340-430 Interrupt.cpp
grep -rn BT3_CDTICK/GPU/async $BT/ps2xRuntime; sed -n '2400,2440p' $BT/ps2_memory.cpp
# Q3
ls <reo|sm2|halogen|drake> layouts; grep -n -i boot README.md (x4)
git -C <drake> rev-parse HEAD (= 2f5d48c14d5d...); diff -rq sorachi00-main drake (= 0 entries)
diff -rq -x .git -x '._*' upstream-baseline sm2 > /tmp/p4/filelist-sm2.txt (109 entries)
head HANDOFF.md/UPSTREAM.md/RESEARCH_FINDINGS.md (sm2); sed -n '100,230p' liquid.cpp
head notes/ps2recomp-build.md; sed -n '205,280p' halogen main_headless.cpp; cat champions-of-norrath.toml
grep -rn setMainThread /tmp/p4/ourfork-6046260 (no hits); cat reo runtime/timer/timer.h runtime/cdvd/cdvd.h
# Q4
git -C <ourfork> diff 6046260 f2149e7 --stat (analyzer only)
grep -n queueInvocation/m_pendingInvocations/invokeCurrent <ours>/EeScheduler.cpp + ee_scheduler.h
(opened) <ours>/EeScheduler.cpp:229-517 (run() drain sites), :1370-1412 (queue/invoke), ee_scheduler.h:84-102
# Report commit (no push)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P4/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P4] ..." --trailer "Orchestrated-By: Muse Code"
```

## 8. What I could not do

| # | Item |
|---|---|
| 1 | M4 (`184158a`), M5 (`3096823`), M8 (`1fa97b8`), M9 (`#224/#223/#217`), M11 (`#241`), M13 (`7ea9a2c`), M14 (`9e00466`): revs absent — all `fork-survey/` clones are depth-1 with no history; no fetch attempted (read-only runbook, no new clones). Recorded as unresolved in §0; M13 may be subsumed by the M1 heap rework (unconfirmed). |
| 2 | Full-body quotes for smmathews (103 files) and mrcool (318 files): tree diffs dominated by old-base drift; quoted mechanism bodies + file counts instead of per-file diffs (cap discipline). |
| 3 | sorachi00 `register_functions.cpp` (169,912 lines of generated Drakengard game code): deliberately unopened — game-specific, not a runtime mechanism. |
| 4 | bt3 scheduler-portable detail: bt3 is pre-#184 (no `EeScheduler`), so its IRQ/alarm internals were surveyed for posture only, not diffed hunk-by-hunk (nothing ports directly). |
| 5 | halogen's `vendor/PS2Recomp` fork: absent from the checkout (only `notes/` references it) — its deadlock/cooperative-yield fixes are README-described, not read. |
| 6 | reo's `third_party/PS2Recomp`: empty (submodule uninitialized) + broken git index; reo learnings are patterns from its own runtime, not diffs. |
| 7 | Applied nothing: all §5 sketches are prose, per runbook. No verification boots (forbidden). |
| 8 | git index reads blocked by AppleDouble `._*.idx` sidecars in `gtteancum-di-preempt`, bt3, sm2, reo-third_party: used `diff`/`rev-parse` fallbacks; left the sidecars untouched (read-only). |
| 9 | P3 §8.7 P2 (DobieStation `cdvd.cpp` body) and P4 (N64ModernRuntime COPYING body): out of P4 scope (P3's gaps, not P4's questions); P1/P5 admitted gaps ARE closed by this report (fork-diff bodies §1, downstream mechanisms §2-§3). P3 (sorachi00 identity) incidentally closed at full-SHA + tree level (§3/§6). |

