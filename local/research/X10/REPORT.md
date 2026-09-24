# X10 — sparse Qwen interrupt-path source table

Pinned input: fork `293fd81`, `source-excerpts.txt`. This table covers only
the quoted slices. It does not establish dynamic guest reach or complete
interrupt behavior.

| Source event | Dispatch API / cause or state action | Domain (INTC, DMAC, or VU state) | Source line |
| --- | --- | --- | --- |
| EE timer pending | FILL | FILL | FILL |
| VBlankStart | FILL | FILL | FILL |
| VBlankEnd | FILL | FILL | FILL |
| VIF1 transfer completion | FILL | FILL | FILL |
| `dispatchDmacHandlersForCause` | FILL | FILL | FILL |
| VU1 `stoppedByD` / `stoppedByT` callbacks | FILL | FILL | FILL |

From these slices alone, the demonstrated `dispatchIrq(false, ...)` cause
values are: FILL. The INTC 5/7 firing path in these slices is: FILL.

Model/tool notes: FILL.
