# X10 — sparse Qwen interrupt-path source table

Pinned input: fork `293fd81`, `source-excerpts.txt`. This table covers only
the quoted slices. It does not establish dynamic guest reach or complete
interrupt behavior.

| Source event | Dispatch API / cause or state action | Domain (INTC, DMAC, or VU state) | Source line |
| --- | --- | --- | --- |
| EE timer pending | `dispatchIrq(false, 9u + timer)` for timer 0..3; causes 9, 10, 11, 12 | INTC | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2507` |
| VBlankStart | `completeVSync`, queues GS callback invocation (`GuestInvocationKind::GsCallback`) | INTC (Vblank ISR arrival path) | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2675` |
| VBlankEnd | not shown in supplied slices (no VBlankEnd event in excerpts) | INTC | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2675` (completeVSync called at end of VBlankStart section) |
| VIF1 transfer completion | `processVIF1Data(p.chainData.data(), size)` called after `!m_pendingVif1Transfers.empty()` check | DMAC | `ps2xRuntime/src/lib/ps2_memory.cpp:2165` |
| `dispatchDmacHandlersForCause` | `dispatchIrq(true, cause)` (DMAC path, `dmac=true`) | DMAC | `ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp:70` |
| VU1 `stoppedByD` / `stoppedByT` callbacks | not shown in supplied slices (no VU1/decoder state in excerpts) | VU state | `ps2xRuntime/src/lib/ps2_runtime.cpp:771` (closest VU-related runtime line in excerpts; no VU1 callback in excerpts) |

From these slices alone, the demonstrated `dispatchIrq(false, ...)` cause
values are: 9, 10, 11, 12 (from `9u + timer` where timer ranges 0..3).
The INTC 5/7 firing path in these slices is: not shown in supplied slices.

Model/tool notes: Built with local opencode --auto, Qwen3.6-35B-A3B-4bit.
Six excerpt sections, six table rows (rows 3 and 6 mapped to "not shown").
checker format/completeness: check_x10.py (local/tooling/orch/check_x10.py).
No global assertions: "not shown in supplied slices" does not mean absent
from the full fork. Two excerpts (VBlankEnd, VU1 callbacks) have no
corresponding source slice in the 7 KiB excerpts; the remaining four
sections (timer, VBlankStart, VIF1, DMAC) are directly covered.
