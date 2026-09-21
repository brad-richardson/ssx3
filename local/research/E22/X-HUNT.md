# E22 X-signal hunt — every candidate second-demand edge

Scope: the demand surface is `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` at fork
`3adc0478` plus the scheduler primitives it calls. A repository-wide grep for
`getMpegPicture` / `kMpegPictureWaitType` / `MpegNonStreamDelivery` returns **zero
matches outside that one file**, so the enumeration below is closed, not a sample.
Static sites + the one E22 observed boot only; no probe code was changed to chase X.

| Observed state at the park (E22, new) | Receipt |
|---|---|
| Host parser calls in the whole title window | **1** (`parse-enter`/`parse-return` call=1 at observer ns 8,509,239,000; 9 µs) |
| That call | offered 5,040 / used 5,040 / `packetSize=0`; `sendCalls=0`, `receiveCalls=0`, `frames=0`, `errors=0` |
| Parser silence after it | 66.896 s to the real `_Exit` closure (`ns=75,405,554,000`), zero further calls |
| Payload identity | FNV64 `0xd2a9588f0e0fd358` and first64 byte-identical to E18's retained bytes; full 5,040 B now retained (`observed/parser-input.bin`, SHA256 `cde8a830…2a1c875a`) |
| Runtime liveness during the silence | thread 4 scheduled ~300×/5 s in all 14 diag samples; thread 1 parked at `pc=0x3b1028` `waitReason=6` with `scheduled=0` in samples 2–14 (≈60 s) |
| So | the runtime holds 5,040 accepted bytes, has emitted no packet, is fully alive, and nothing asks for more. |

| # | Candidate second-demand edge | Exact site | What would trigger it | Observation that proves fires / absent | E22 result |
|---|---|---|---|---|---|
| C1 | Broaden the AddBs wake to fire on accepted-but-buffered bytes | `MPEG.cpp:2053` `wakePictureWaiter = decodedFrames.size()!=framesBefore \|\| streamEnded \|\| decoderFailed` | add `\|\| copied > 0` | Ordering of the AddBs events vs the park in the E7 trace, plus `completeExternalWait`'s matching rule | **Proven inert.** AddBs is `seq=6397/6398`, the park is `seq=6401`, same tick 249, **same thread 1** — AddBs runs *inside* the callback, before its caller parks. `EeScheduler::completeExternalWait` scans only threads already `Waiting`; there is no latch and no pending-completion queue, so a wake raised here matches 0 threads and is lost. Trace confirms: **0 `mpeg-complete` events** in 6,401. Broadening C1 cannot reach the waiter. |
| C2 | Flip the post-callback continuation to re-request | `MPEG.cpp:1760` `getMpegPicture(rdram,&parent,runtime,false)` → `true` | the flag alone | Gate at `2467` needs `!delivery`; `2464/2465` re-`lock()` the map entry | **Inert.** `nonStreamDeliveries` is `weak_ptr` (`564`) but the `onComplete` lambda itself captures the `shared_ptr` (`1758`), so `pending.lock()` still succeeds and the gate stays closed. Flipping the flag changes nothing. |
| C2a | Release the delivery, *then* re-request | `1757–1760` + `2484` | reset/erase the delivery in `onComplete`, then `getMpegPicture(...,true)` | Would produce a real second demand — the mechanism works | **Reachable, but unbounded.** Needs a termination rule: how many rounds, stopped by what (a cap? a packet? source exhaustion? a failure?). None is observed anywhere in E18/E21/E22. **Policy invention — excluded.** |
| C3 | Loop the multi-callback dispatcher | `MPEG.cpp:1740` `while (!cancelled && nextCallback < callbacks.size())` | more than one registered type-1 callback | Registration census in the boot trace | **Absent.** Exactly one registration (`mpeg-request-registration … handle=1`; E15 closure `registrations=1`). The loop iterates once by data, not by policy. |
| C4 | Re-request just before parking | `MPEG.cpp:2496–2513` wait predicate | `if (sawInput && decodedFrames.empty()) re-request` | Is the precondition even true at the park? | **Site reachable, policy missing.** `[MPEG:GetPicture] waiting … sawInput=1` is in the E22 boot log, so the guard would pass. Same live-delivery gate as C2 plus the same unbounded-rounds problem as C2a. Excluded on the same ground. |
| C5 | Timer / vsync-driven re-poll | `ee_scheduler.h:337` `waitExternal`, `:311` `setAlarm`, `MPEG.cpp:2530/2678` `currentVSyncTick` | any periodic hook re-entering the MPEG path | Signature inspection + cross-file grep + BIOS trace | **Proven absent.** `waitExternal` is `[[noreturn]]` with **no timeout parameter**. `setAlarm` exists but MPEG.cpp never calls it. `currentVSyncTick` is read only to timestamp frames, never to drive a request. Zero cross-file references to the MPEG demand symbols. Dynamically: **0 alarm calls** in 54,944 traced BIOS lines, and 12 consecutive 5 s samples with thread 1 `scheduled=0`. |
| C6 | Guest-side unprompted retry | guest `0x3b1020` → `sceMpegGetPicture` (`0x402a10`), continuation `0x3b1028` | guest calls GetPicture again | Thread census + per-thread MPEG dispatch counts | **Proven absent.** Thread 1 is parked at `0x3b1028` `waitReason=6` from sample 2 to sample 14 with `scheduled=0` throughout; `waitExternal` is `[[noreturn]]`, exit only via `completeExternalWait`, which never ran. All 10 `mpeg-call` events are tick 249, thread 1. Threads 2–6 never touch MPEG; the still-running thread 4 only ping-pongs `iSignalSema`/`WaitSema` at `0x423dd8`/`0x423de8` for the last 60 s. |
| C7 | EOF / `streamEnded` wake | `MPEG.cpp:1999` `notifyMpegCdStreamEof` | CD-stream layer signals EOF | `ended=` at the park; `currentCdStreamEofSeen` | **Absent and excluded.** `ended=0` at the park and the flag is never set; the source is not exhausted (descriptor `0x548800` is live). Firing it would fabricate EOF — barred by the ABI carry ("no decoder/EOF claim", "no v0→EOF rule"). |
| C8 | Demux / flush wakes | `2285`/`2291` (`sceMpegDemuxPss`), `2378`/`2384` (Ring), `2023` (`sceMpegFlush`) | guest calls those entry points | Target dispatch census | **Absent.** The census has 10 distinct targets (`0x3b06b0 0x3b06f8 0x3b0b10 0x3b0b40 0x3b0c58 0x402708 0x4027b8 0x4029d0 0x402a10 0x402c08`); none is a demux or flush stub. The non-stream path never reaches them. |
| C9 | Delete / Reset cancellation | `1231`, `2239` (`KE_WAIT_DELETE`) | guest deletes or resets the MPEG object | Trace for those targets | **Absent, and not a demand edge** — it aborts the wait rather than supplying input. |

| Decode-threshold half (scope-limited) | Receipt |
|---|---|
| What the parser held | 5,040 B consumed, buffer retained, `packets=0`, `errors=0`, `decoderFailed=0` — the pre-threshold state Q1 characterised, now confirmed on the **real** stream rather than an authored one. |
| Real-stream GOP offset | 0: the payload's first four bytes are `000001b3` (sequence header), so the whole 5,040 B is stream from byte 0. |
| Deficit | **Not computable from this run.** Q1's `GOP offset + 5,461` was measured on `authored-black.m2v`; 5,461 = that stream's 5,457-byte first picture + 4 lookahead bytes. The real stream's first-picture length is unmeasured because the rest of it was never delivered. Importing 5,461 here would be a false precision. |
| What it does establish | The single feed is genuinely incomplete rather than malformed: the parser accepted every byte, raised no error, and simply has no full picture yet. |

| X, sharpened by E22 | Statement |
|---|---|
| E21's X | "a second input-demand signal after successful-but-incomplete AddBs." |
| E22's refinement | X is the edge from **"parser holds accepted bytes but emitted no packet"** back to the registered type-1 producer, **plus its termination rule**. The mechanism half is reachable (C2a/C4); the missing half is the rule. |
| Two named unknowns blocking a fix | (1) **Trigger point** — re-ask inside `onComplete`, before the park, or on a broadened wake? C1 is now eliminated, so it must be one of the other two. (2) **Loop bound** — how many rounds and stopped by what. Neither is observable from E18/E21/E22, and no reference trace of the firmware's real behavior is in hand. |
| What E22 eliminated | C1, C3, C5, C6, C7, C8, C9 are closed (proven inert or proven absent). Only C2a and C4 remain live, and both require inventing the same missing rule. |

| E22 X-HUNT TAIL COMPLETE | Nine candidates enumerated over a closed surface; seven closed; two remain and both need the excluded policy. |
|---|---|
