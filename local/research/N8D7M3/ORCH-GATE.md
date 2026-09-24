# N8D7M3 orchestrator gate — PARTIAL source map, discriminator rejected

Worker commit `20144020` (`Orchestrated-By: opencode`) is a read-only design. I read the full report and brief, checked the commit and source paths, and verified the selected descriptor and 4 MiB copy sites in the private fork/G43 source. There was no build, boot, device action, frame or speed measurement.

| Item | Gate read |
| --- | --- |
| Source map | Useful path from presentation tick and DISPFB1 selection through GPU buffer copy, mapped staging buffer and the two CPU decoders. The source references for the selected descriptor, copy and host decode resolve; the worker explicitly leaves its frontend ring and queue-depth sites unverified. |
| A versus B | `fbp112_draws < K` cannot establish sparse FBP112 content: one draw may cover many pixels, and many draws may change none. A different FBP with many draws need not contain a broad frame. The proposed Mac-derived `K` also has no demonstrated validity for a different Odin stream. |
| C timing | A last Draw stamped tick 2050, or a pending count at Present entry, does not prove that its VRAM write becomes visible after the selected copy executes. The exact GPU execution/order witness is missing. |
| D decode | Two nonzero control words can coexist with a sparse 448-tile census; they do not show that the census lost pixels. N8D7M2 already found 448/448 agreement between the independent fork-table and G43 decoders for its selected snapshot. |
| Same-run candidate | A broad census at a different base/phase would be useful evidence that content exists elsewhere in the same mapped 4 MiB snapshot, but by itself it cannot establish that this was the intended displayed region. The selection register/packet provenance is still needed. |

Verdict: **PARTIAL**. The source map is reusable, but the A/C/D classifications and the proposed one-run acceptance gate are not discriminating. Do not build or launch the proposed N8D7M3 tap as written. Next: design a direct same-stream packet/write-versus-snapshot comparison, using N8D4's Odin stream capture and Mac replay as the existing controlled reference where possible. Require actual byte/word or packet provenance and an ordering witness before spending another Odin launch. No upstream GS cause is declared.
