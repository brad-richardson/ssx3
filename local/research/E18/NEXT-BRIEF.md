# E18 handoff — initial MPEG input reaches a parser with no output

| Consumed checkpoint | Receipt |
|---|---|
| Fork | `3adc0478b6d2260acdd28a249466f2eef9a20176`, BEHAVIOR, pushed to fork/ssx3; ls-remote agreement |
| Files | `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` (+189/−3), `ps2xTest/src/ps2_runtime_expansion_tests.cpp` (+284) |
| Verification | Generated9457 unchanged; original452 + R1–R6 =458/458; prior bindings, E16 closure6, E17 exact bindings5; E15 actual-wrapper no-input/input rc1→rc0 |
| Protected builds | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link`; preserve all and DerivedData |
| E18 boot allowance | 1/1 spent, released, rc0; no second E18 boot |
| Source closure | Real run-exit tick4446; calls10=9returns+1unwind; pending0; selection1/invocation1; E7 events6401, byte/count match, all truncation flags0 |

| First demonstrated post-delivery edge | Evidence |
|---|---|
| Dynamic request | Create→type1 registration→GetPicture for this run's MPEG `0x587b30`; callback `0x3b0b10`, userdata `0x587b00` |
| Ownership | Callback on caller thread1 and SP `0x1fffd60`; original parent continues at supplied RA `0x3b1028` when completion is available |
| Actual producer | `0x3b0b10`→`0x3b0b40`→source descriptor `0x548800`, data `0xd48748`, bytes5036; descriptor source/release routines entered |
| Actual input | `0x4029d0` accepted5040 bytes from `0xdc8340`; first sequence header `000001b3`; full-span FNV64 `0xd2a9588f0e0fd358`, first64B retained |
| Parser | Host FFmpeg ON: parsed5040, packets0, newFrames0, totalFrames0; `decoderFailed=0` |
| Resulting wait | Callback returns v0=1, ignored. No second callback/input/completion; main Waiting/Mpeg at `0x3b1028`; `ended=0 failed=0 sawInput=1` |
| Named dependency | Accepted initial input → additional input / complete parser packet → decoded frame → GetPicture wake. Further-input demand after a successful but incomplete feed requires its own brief |
| Source boundary | `dispatchGuestNonStreamCallback` onComplete frees cbData then continues `getMpegPicture(..., false)`; empty output takes the existing typed wait. No further-input policy was added in E18 |
| Limits | No decoder-error or EOF claim. Full5040B payload not separately retained; first64B/hash cannot support a full standalone decoder replay. No second fix was attempted |

| Binding design constraints for the next brief | Required preservation |
|---|---|
| Ownership | queueInvocation/RpcCallback failed the actual ownership audit (parked caller moved to thread−1, async stack). Keep caller-owned synchronous HleCall or independently prove any replacement |
| ABI | `(mpeg,cbData,userdata)`, word0-only callback data, observed type1 trigger, supplied parent continuation, full saved128 and stack preservation |
| Return value | Callback v0 is discarded; no v0→EOF rule. Valid-no-input must remain waiting |
| Locking / lifetime | Collect under MPEG mutex, dispatch outside; AddBs re-entry; registration order/dedupe; delete/reset cancellation; free cbData in onComplete |
| Scope | First missing edge only; no semaphore workaround, guest-PC special case, generated-source/CSV edit, fabricated frame/EOF, or guest-gate bypass |
| Regression carry | 458 tests + prior actual bindings + E15 no-input/input + E16 closure. Existing stream helper/test bytes retained |

| I-lane S9 trigger (their brief, not executed here) | Action / observation |
|---|---|
| Install base | Consume fork `3adc0478`; rebuild and reinstall device runner |
| Probe | Their90s diagnostic probe with `PS2X_DIAG_PERIOD_MS` and `PS2X_DIAG_SEMA_CREATE=1`; creator census already closed in I20 |
| Compare | `0x3b0b10` / `0x4029d0` dispatches, actual bytes, main beyond `0x3b1028` or named successor, sema26/30/32 traffic |
| Device decode boundary | I20's FFmpeg-OFF stub residual remains device-side. A warning / no decode after observed delivery names their next dependency; do not infer it from this FFmpeg-ON host parser receipt |
| Stop | First demonstrated missing link after delivery; no stacked second fix |

**E18 NEXT-BRIEF TAIL COMPLETE — delivery landed; initial-input / parser-output / further-input dependency tabled.**
