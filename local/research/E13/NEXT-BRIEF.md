# Proposed next brief — MPEG input callback delivery at the first picture wait

This is the **one next-action recommendation**, not an extension of E13's
authorization. E13 closes with outcome (ii). Standing no-regen applies;
the relevant MPEG wrappers and guest callback entries already exist.

## 1. Preserve the checkpoint

| Prerequisite | Required identity / guard |
|---|---|
| Fork | `83fb4d60904abb016522c477cce704c52118f95f`, branch `ssx3`, pushed to fork remote only |
| Active build | `/tmp/p1-link/runtime`; protect this tree and DerivedData |
| Runner | SHA256 `b2099130a366940fb0fa3d273a8bebc7d3ac28618cf0ceac1c743f90939fbbf6` |
| Generated mirror | All 9,452 names/hashes in `after/generated.json`; registry SHA256 `98753bfad809d7b54fdbef1c41cc6757724bcbfee9f957f3f89219a39da69e59` |
| Canonical CSV | SHA256 `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4`; no row changes or regeneration proposed |
| Regressions | Suite 452/0; actual leaf 24 cases, consumer 3, predicate 14, busy query 4 and DROP handler; preserve exact results and full register/RAM checks |
| Fork staging | Generated sources never staged. Existing dirty generated registry and untracked `ps2_log.txt` remain outside named-files commits |

Read E13 REPORT, the complete retained MPEG sources/disassembly and
`e13a-residual-join.json`. Recheck identities before extending observations.
Do not repeat the completed leaf repair.

## 2. Forcing receipts and open question

| Link | E13 observation / remaining uncertainty |
|---|---|
| Guest advance | 142 exact leaf returns; six complete flag/store chains; UI state 3→6→29. The live flag writes are 0→0, not an observed 8→0 clear |
| MPEG request | Raw line 10381: GetPicture waits at MPEG object `0x587b30`, `ended=0 failed=0 sawInput=0`; T1 remains at PC/RA `0x3b1028` |
| Actual binding | ELF call `0x3b1020→0x402a10`; generated wrapper invokes `sceMpegGetPicture` |
| Registration | Entry `0x402c08` reached once, RA `0x3b0f6c`; ELF fixes type 1, callback `0x3b0b10`, userdata=s2. Original runtime arguments were not directly logged |
| Callback producer | `0x3b0b10` passes reordered arguments to `0x3b0b40`; that helper obtains guest data through `0x3b06b0`, copies/pads it, then calls `0x4029d0→sceMpegAddBs` |
| Missing delivery observation | Full hot-PC JSON has zero dispatches at `0x3b0b10`, `0x3b0b40`, `0x4029d0`. All exact bindings exist. One owner-label `sub_003B0B40` log is actually constructor alias `0x3b0c58` |
| Runtime candidate | `MPEG.cpp:1939` records AddCallback with `stream=false`; the callback map's only selecting reader at 1141–1157 requires `stream=true`. GetPicture waits with no input; AddBs would feed the decoder and conditionally wake its waiter |
| Dependency limit | Nearby CD reads have not been joined to this MPEG input. Their presence does not name a CD/SIF/storage/input failure |

**Hypothesis:** the runtime records the non-stream type-1 callback but never
delivers it, leaving the guest AddBs producer uninvoked before GetPicture
parks. Establish the original registration and callback contract before
implementing anything. Do not assume that stream-callback event layout or
return semantics also apply to this callback type.

## 3. Exact next probe and fixture

Use bounded read-only extensions of the current taps and a fixture linked
against the actual generated wrappers. A future brief must declare its boot,
wall, progress, byte and storage budgets before execution; E13 grants none.

| Probe | Required receipt |
|---|---|
| Create/register identity | Original arguments and supplied RA at MPEG Create and `0x402c08`; record returned handle, dynamic MPEG pointer, type, function and userdata. Require callback entry `0x3b0b10` and its actual binding; never reuse E13 heap addresses without guards |
| Picture request | At `0x402a10`, record original a0/a1, RA/SP, frame queue, sawInput/end/failure flags, selected registered callbacks and wait registration. Join object identity to Create/AddCallback |
| Callback selection/delivery | Record eligibility, scheduling, actual target dispatch, original a0/a1/a2, callback-data bytes, userdata, return value and return destination. Derive the type-1 ABI from the guest consumer and an authoritative contract before making a fixture expectation |
| Guest data source | Join `0x3b0b10→0x3b0b40→0x3b06b0` and the resulting buffer address/length; record helper fields +0x78/+0x7c with a guarded object, not guessed globals |
| Input and completion | At `0x4029d0`, record original MPEG/data/count, exact input bytes or bounded hash plus retained source bytes, copied count, decoder result, queued frame count and wake operation. Join to resumed GetPicture and supplied return PC |
| Lifetime | Record callback removal, MPEG deletion/reset and any terminal event; distinguish a removed callback or exhausted input from failure to dispatch |
| Existing guards | Re-derive MC/UI from constructor `0x2c3fc4` and UI store `0x23d5c8`; retain leaf/flag/state and S-singleton/slot guards. End object interpretation at destructor/reuse |

The fail-before fixture must exercise registration and the real request path,
not call the guest callback manually and count that as runtime delivery.
It should distinguish callback selection, invocation, valid no-input return,
and successful input delivery. Preserve guest ABI/stack/callee-saved state;
use the actual generated guest wrapper where applicable. If the callback
contract cannot be established, table that specific missing receipt and stop.

## 4. Align the graphics observation with the advance

E13's last copy was at tick 248; the fixed 599–603 packet window missed it.
For the next probe, arm a bounded capture from the guarded UI state 3→6
transition or earlier observed packet activity. Keep enough source VRAM and
packet bytes to join the actual packet to GS consumption, D pixels and the
field-processed Present. Do not substitute E12 packet bytes or a matching hash
for this run's source/content evidence.

Give the observation sink an explicit shutdown closure receipt as well as
its normal window-end receipt. Source quiescence must not require a later
event to prove closure. Retain raw bounds, sequence continuity and call-pair
balance; do not manufacture a runtime footer in a miner. A changed image
alone does not prove guest progression or callback delivery.

## 5. Conditional implementation shape for a later authorized brief

| Condition / files | Implementation and proving receipt |
|---|---|
| Registration and ABI confirmed; request path demonstrably omits delivery | One generic runtime fix in `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`; declaration changes in `MPEG.h` only if needed. No guest-PC special case, handwritten leaf or generated-source edit |
| Scheduler and locking | Deliver with the required guest invocation semantics. Do not invoke a callback while holding the MPEG mutex: the callback may re-enter AddBs. Preserve request ordering and avoid duplicate/reentrant deliveries; cancellation/deletion must invalidate pending work |
| Regression location | Extend existing MPEG tests in `ps2xTest/src/ps2_runtime_expansion_tests.cpp`, plus the actual-binding fixture. Require fail-before/pass-after for non-stream registration→request→delivery, AddBs re-entry, wait completion, valid no-input return and teardown; retain stream-callback behavior |
| Re-probe | Fresh suite and identities, `-j4` rebuild, one scoped change followed by a guarded capture under the shared P-lane lease. Release immediately at the first binding cap; analyze lease-free |
| Stop | If delivery now occurs but input, decode or a later guest edge fails, name the first demonstrated missing link and stop. Do not stack another fix or route around a guest-side gate |

This is a design proposal only. E13 made no MPEG code change and used its
single authorized boot.

| Next observation | Recommended disposition |
|---|---|
| Callback request/delivery gap established with ABI receipt | Review the single generic fix above under a new execution brief |
| Registration/producer names a different dependency | Table the first missing request/completion edge and its exact next probe; no automatic CD/SIF promotion |
| Truncated, unguarded or unaligned evidence | Repair that measurement only |

**E13 NEXT-BRIEF TAIL COMPLETE — one proposed MPEG delivery investigation;
no renewed regeneration, boot or second-fix authorization implied.**
