# X9 — signed branch source table

Worker: local dense Qwen3.8-27B, per-pane thinking budget 512.
Pinned source: `source-excerpts.txt` (`1aaed05`).

| Family and variants | Current emitted predicate + line | A current / expected s64 | B current / expected s64 | Zero current / expected s64 |
| --- | --- | --- | --- | --- |
| BLTZ | FILL | FILL | FILL | FILL |
| BGEZ | FILL | FILL | FILL | FILL |
| BLEZ | FILL | FILL | FILL | FILL |
| BGTZ | FILL | FILL | FILL | FILL |

A = `0x0000000180000000`; B = `0xffffffff00000000`.
Expected s64 means mathematical signed-low-64 comparison from the
review hypothesis, not an independently checked PS2 hardware oracle.

Emitter connection, source evidence: FILL.
Any source gap or unverified claim: FILL.
Exact commands and elapsed time: FILL.
