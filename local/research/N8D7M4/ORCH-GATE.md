# N8D7M4 orchestrator gate — PARTIAL same-stream plan

Worker commit `744bcdd2` (`Orchestrated-By: opencode`) is read-only. I read the whole report, checked the commit, and verified the replay packet/marker and selected-capture source lines in the pinned private fork. No build, replay, device action, frame or speed measurement occurred.

| Item | Gate read |
| --- | --- |
| Reusable finding | N8D4's captured Odin GS stream has one SHA and already produced broad Mac CPU and paraLLEl replay images. A future Odin launch must capture its own stream **together with** its selected VRAM snapshot before comparing them. The N8D4 and N8D7M2 Odin boots are distinct. Source and APK string checks suggest the current N8D7M1 package contains both capture flags, but their combined operation has not been tested. |
| Source path | Replay applies type-1 packets and drains the queue at markers; tick2050 selected snapshot comes from DISPFB1 and a 4 MiB GPU-buffer copy, then the backend submits/waits and maps staging. Direct source lines resolve. These establish a useful capture path, not a fault location. |
| Proposed per-packet tap | Reading the test harness's `vram[]` immediately before/after `gs.processGIFPacket` does not prove that the queued packet executed between reads. The backend write hook or an explicitly drained, non-perturbing equivalent must supply the actual packet old→new witness. |
| Eight control words | The chosen Mac control addresses are real swizzled addresses, but several words are dark/background and one pixel has a zero census tile. Six or eight individual word matches cannot prove a 448-tile census is broad or that its decoder lost content. A future gate needs full same-run vector/occupancy plus packet-provenance at genuinely discriminating addresses. |
| Tick2052 branch | A broad image two ticks later does not prove the tick2050 copy was early; normal intervening packets could change it. A sparse 2052 image also does not prove GPU writes were missing. The S-ORDER/S-MISSING categories need a same-packet, controlled ordering witness; no COLOR_ATTACHMENT_OUTPUT barrier cause follows from the present evidence. |

Verdict: **PARTIAL design**. Do not run its proposed Odin classification as written. Next: one bounded Mac replay experiment on the pinned N8D4 stream to log **executed** old→new writes at exact GS addresses with packet identity, while preserving OFF/ON frame hashes. Use that to choose meaningful comparison pixels and revise mutually exclusive Odin outcomes. No upstream or Turnip cause is declared.
