# X10B — sparse Qwen pinned interrupt-path table

Input: `source-excerpts.txt`, fork `293fd81`. This is a static table of
the supplied slices only; it says nothing about dynamic guest reach.

| Source | Observed call or state | Domain | Citation |
| --- | --- | --- | --- |
| EE timer pending | `dispatchIrq(false, 9u + timer)` → 9, 10, 11, 12 | INTC | `EeScheduler.cpp:2507` |
| VBlankStart tail | `dispatchIrq(false, 2u)` | INTC | `EeScheduler.cpp:2696` |
| VBlankEnd | `dispatchIrq(false, 3u)` | INTC | `EeScheduler.cpp:2702` |
| VIF1 completion | `queueCompletedDmacCause(1u)` | DMAC | `ps2_memory.cpp:2286` |
| DMAC handler helper | `dispatchIrq(true, cause)` | DMAC | `Interrupt.cpp:70` |
| VU1 callback status | `stoppedByD ? 0x0200u` / `stoppedByT ? 0x0400u` | VU state | `ps2_runtime.cpp:1046` |

The direct `dispatchIrq(false, ...)` causes shown are: 2, 3, 9, 10, 11, 12. A direct INTC 5 or 7 firing call in the supplied slices is: not shown.

Model/tool notes (time to first complete table, context, extra reads): Read 3 files (brief, source-excerpts.txt, report skeleton). Context: fork 293fd81 excerpt, 3.6 KiB, 7 source blocks covering INTC/DMAC/VU1 paths. No extra source reads; all citations from supplied excerpts.
