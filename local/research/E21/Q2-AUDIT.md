| Q2 demand audit | Static receipt (fork `3adc0478`, `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`) |
|---|---|
| Sole input-request site | `getMpegPicture` L2467–2493: creates the type-1 `MpegNonStreamDelivery` and `HleCall`-dispatches the registered guest callback, only when `requestInput && !delivery && decodedFrames.empty() && !eof && !streamEnded && !decoderFailed` |
| Request signal shape | `cbData` word0 = type (`1`); callback `(mpeg, cbData, userdata)` on caller thread/stack; v0 discarded (L1742–1760) |
| Post-callback re-request | Absent by construction: `onComplete` continues with `getMpegPicture(..., false)` — "continue this request without re-triggering it" (L1757–1760) |
| Resume re-request | Suppressed: the parked `waitExternal` lambda captures the live `delivery` (L2518), so the resume `pending.lock()` (L2465) still succeeds and `!delivery` stays false |
| Park primitive | `waitExternal(Mpeg, kMpegPictureWaitType=1, mpegAddr)` (L2514–2525) is `[[noreturn]]` with no timeout (`ee_scheduler.h:337`); exit only via `completeExternalWait(1, mpegAddr, *)` |
| AddBs wake signal | L2053: wakes ONLY on `decodedFrames.size() != framesBefore \|\| streamEnded \|\| decoderFailed`; accepted-but-buffered bytes with no frame produce no wake |
| Other wake sources | `sceMpegDemuxPss(Ring)` on decoded-change/eof/completion (L2285/2291, L2378/2384); `notifyMpegCdStreamEof` (L1999); `sceMpegFlush` on change/ended/failed (L2023); Delete/Reset/Create cancellation with `KE_WAIT_DELETE` (L1231/2239) |
| Fires on buffered-but-incomplete AddBs | None of the above: no decoded change, no EOF, no demux, no flush, no cancellation in the E18/Q1 AddBs-only path |
| E18 baseline, consistent | Delivered 5,040 B → parsed 5,040/packets 0/frames 0 → no further MPEG events: exactly the L2053 no-wake + L2514 indefinite-park shape |
| Q1 refinement | At 5,040 fed bytes every GOP case still shows packets 0/frames 0 (first packet needs GOP + 5,461 continuation bytes); the wake precondition is unreachable at E18's input volume |

| Second-request verdict | Receipt |
|---|---|
| Guest re-call of `GetPicture` while parked | Reaches the same L2467 gate with the first delivery still alive via the wait-lambda capture → no second delivery, second park; no new callback |
| Runtime-initiated second input callback after insufficient AddBs | No static path: creation requires `!delivery` (dead first delivery) plus a fresh/requestInput entry, and no wake fires to reach one |
| Missing signal, named | A "buffered input grew but no frame completed" wake/re-request edge does not exist in `sceMpegAddBs`/`getMpegPicture`; the only input-demand signal is the single type-1 delivery per live-delivery lifetime |

| Q2 Q3 handoff | Receipt |
|---|---|
| Q3 must observe | Whether the guest, unprompted, sends more input after the first insufficient feed (no runtime signal asks it to) |
| Q2 result for the fix gate | Static absence proven on the runtime side; guest-side demand behavior is Q3's single guarded observation |

| E21 Q2 AUDIT TAIL COMPLETE | Runtime demand paths enumerated; re-request absence proven statically; guest demand left to Q3. |
|---|---|
