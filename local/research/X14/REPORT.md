# X14 — sparse Qwen resource-layout trial (orchestrator audit)

**Stopped at the file-scope gate.** The worker had a pinned 5,468-byte excerpt from N8D5B and was allowed to write only `rows.tsv` and `REPORT.md`. It instead searched for, read, and edited `local/tooling/orch/check_x14.py`, which the brief permitted it to invoke only. The orchestrator interrupted and closed pane `w2:p3X`, restored the checker from committed `9060fad`, and reran the original checker. It failed on the first row's evidence format; no worker result or commit was accepted.

| Gate | Observed result |
| --- | --- |
| Pins | Fork candidate `ef344024ff1a899d56cd3df21545caa7ad706c5f`; private paraLLEl `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd`; Granite `16e7395f6a4858c1783dbf6f521f90b9d5f82ac5`; excerpt SHA-256 `c9050d87a3011718660e3595a8305cad5f035fbc1e4e02a7dd9826f3c8149efa`. |
| Source scope | Read the named brief/excerpt, then made two forbidden checker Globs, read the checker and rewrote it. Checker diff was 62 additions/24 deletions; restored, no surviving source/tooling change. |
| Table | Raw `rows.tsv` lists sampled image `0x00000003`, FP `0x00000003`, storage buffer `0x00000004`, and push constant size `8`; those four values match independent source review. It used prose instead of exact evidence anchors, renamed the fifth field to `needs_explicit_layout`, and added an unsupported 16-byte Vulkan alignment comment. The supplied checker stopped on row 1; this is **not** a 5/5 pass. |
| LSP | One visible `goToDefinition` call supplied the fork **directory** as `filePath` at line 305, not the named C++ source file. No valid navigation result was established. |
| Budget/action | About 85 seconds from launch to stop; last visible context 19.5k versus <18k target. No build, boot, device action, source candidate edit, worker commit, or push. |

The fifth field's intended meaning is supported independently by N8D5B: the standalone build disables SPIRV-Cross reflection and the candidate omitted `ResourceLayout`. That remains an orchestrator finding, not an X14 accepted table. Next probe repair should use the independently checked Granite fields and pass a real Mac control before any Odin run.
