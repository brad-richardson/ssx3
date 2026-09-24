# X10 — sparse Qwen interrupt-path source table

Pinned input: fork `293fd81`, `source-excerpts.txt`. This table covers only
the quoted slices. It does not establish dynamic guest reach or complete
interrupt behavior.

| Source event | Dispatch API / cause or state action | Domain (INTC, DMAC, or VU state) | Source line |
| --- | --- | --- | --- |
| EE timer pending | `dispatchIrq(false, 9u + timer)` for timer 0..3; causes 9, 10, 11, 12 | INTC | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2507` |
| VBlankStart | `completeVSync` and a GS callback invocation are shown; the excerpt omits the event label and INTC dispatch | GS callback/VSYNC state; INTC dispatch not shown | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2675-2685` |
| VBlankEnd | not shown; the slice ends before this event | unknown from excerpt | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2685` (slice boundary, not event evidence) |
| VIF1 transfer completion | `processVIF1Data` is shown; the completion and DMAC cause are outside this slice | VIF data processing; DMAC completion not shown | `ps2xRuntime/src/lib/ps2_memory.cpp:2164` |
| `dispatchDmacHandlersForCause` | `dispatchIrq(true, cause)` (DMAC path, `dmac=true`) | DMAC | `ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp:70` |
| VU1 `stoppedByD` / `stoppedByT` callbacks | not shown; the supplied slice is presenter code and the start of the runtime constructor | unknown from excerpt | `ps2xRuntime/src/lib/ps2_runtime.cpp:767-810` (slice scope, not callback evidence) |

From these slices alone, the demonstrated `dispatchIrq(false, ...)` cause
values are: 9, 10, 11, 12 (from `9u + timer` where timer ranges 0..3).
The INTC 5/7 firing path in these slices is: not shown in supplied slices.

## Orchestrator gate: INVALID TRIAL

The orchestrator built this excerpt using line ranges from another fork
checkout, then applied them to pinned `293fd81`. The supplied slices omit
the VBlankEnd dispatch, VIF1 DMAC completion, and VU1 callback code that
the brief expected. The worker's “not shown” answer for VBlankEnd and VU1
was justified. Its VBlankStart INTC and VIF1 DMAC labels, and citations
offered for absent paths, were unsupported by the supplied lines. The table
above corrects those cells and is limited to this excerpt; it makes no
fork-wide INTC 5/7 verdict.

Sparse Qwen3.6-35B-A3B-4bit passed `check_x10.py` because that checker
only enforced format and citations. It browsed directories despite the
fixed-read brief and reached about 27k context against an 18k cap before
committing. The input and checker defects make this trial unsuitable for a
model-accuracy score. A corrected pinned excerpt and stronger semantic
checker are needed for X10B. No source edit, build, boot, device use or
push came from X10.
