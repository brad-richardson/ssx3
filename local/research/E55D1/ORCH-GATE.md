# E55D1 orchestrator gate — ExternalWake, pad and card boundaries

Verdict: **PASS for read-only source mapping; no determinism or runtime verdict**.

I read the entire report and eight-row TSV, verified fork pin `ddaee78`, worker commit `4313690` scope/trailer, and checked the named enqueue, drain, VBlank hash, pad-read and card-stub source lines. A broad in-tree search of `ps2xRuntime` and `ps2xTest` found the `postEvent` definition, `PS2Runtime::postEeEvent` forwarder, and no caller of either; `m_events.push_back` occurs only inside `postEvent`. This supports **no in-tree production ExternalWake poster at this pin**, with out-of-tree callers unexamined. The live MPEG path calls `completeExternalWait` directly on the executor, separately from `m_events`.

The scheduler drains scheduled deadlines, then pending timer IRQs, then the FIFO `m_events`; `EeEvent` has no guest-cycle field. `PS2X_DETERMINISTIC=1` changes scheduled event selection, not this FIFO. The VBlank hash tap runs after INTC2 and hashes memory plus a VU1 count, not waiter readiness or the queue. Pad data is sampled and written into guest RDRAM during `scePadRead`; the vsync-clock script uses guest tick, whereas live/host-frame input can vary. Card stubs write host file bytes and directory timestamps into guest RDRAM synchronously; even `.`/`..` entries use host `std::time(nullptr)` in `sceMcGetDir`.

Decision: do not design a production ExternalWake timestamp policy until a real poster is identified. Prioritize independent pad-read and card-state isolation with pinned inputs and first-difference receipts. E55C2's matching VBlank hashes remain a bounded observation, not a full-frame or all-input determinism claim. No source change, build, boot, device action or speed number in this gate.
