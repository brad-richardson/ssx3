# X10B — sparse Qwen pinned interrupt-path table

Input: `source-excerpts.txt`, fork `293fd81`. This is a static table of
the supplied slices only; it says nothing about dynamic guest reach.

| Source | Observed call or state | Domain | Citation |
| --- | --- | --- | --- |
| EE timer pending | FILL | FILL | FILL |
| VBlankStart tail | FILL | FILL | FILL |
| VBlankEnd | FILL | FILL | FILL |
| VIF1 completion | FILL | FILL | FILL |
| DMAC handler helper | FILL | FILL | FILL |
| VU1 callback status | FILL | FILL | FILL |

The direct `dispatchIrq(false, ...)` causes shown are: FILL. A direct
INTC 5 or 7 firing call in the supplied slices is: FILL.

Model/tool notes (time to first complete table, context, extra reads): FILL.
