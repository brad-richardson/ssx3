# X15B orchestrator gate — local dense Qwen retry

The pane wrote `rows.tsv` and `REPORT.md` but had not made its requested worker commit when the orchestrator closed it after the five-minute wall cap. This is an orchestrator audit, not a worker pass or a GS result.

| Check | Observation |
| --- | --- |
| Input | Pinned 11,013-byte excerpt SHA `eac602143522d2ec2fe3c6b062070ee822c32a5fecd258400a9e66a1a102c146` matched an independent read |
| Table | Eight fields in order; all evidence anchors exist in the excerpt; EN1/EN2/INT/FFMD are correct |
| Downstream | `force_progressive`, `is_interlaced`, `deinterlace_branch` left `unknown`; `raw_circuit_early_return=0` matches the full source result but its supplied derivation is wrong |
| Bitfield error | `REPORT.md` says `0xff21` has MMOD bit 5 = 0; `0xff21 & 0x20` is `0x20`, so MMOD = 1. It also cites the EN1 branch at renderer line 4758 as if it excluded circuit2 |
| Initialization error | `REPORT.md` says the excerpt lacks aggregate initialization; backend line 248 explicitly has `VSyncInfo vsync = {}`. The full interface path does not set these bools true, so full-source downstream values are `0/1/0/1` |
| LSP | One `goToDefinition` on the requested file/line returned `No results found for goToDefinition` |
| Budget | `rows.tsv` was written by 08:54 EDT; report says ~2.5 min elapsed based on timestamps around the LSP call, but the pane remained active past 09:00 EDT, beyond the five-minute cap. Pane context displayed 24.3k, above the <18k target |
| Scope | No source, build, boot, device, config or push change observed; only the two named receipt files were written |

The returned numeric `0` on raw-circuit is not accepted as evidence of sound interpretation because its MMOD calculation is false. The trial is **not accepted for interpretive source work**; the two worker receipts are kept verbatim for comparison. No engineering claim is made from the table.
