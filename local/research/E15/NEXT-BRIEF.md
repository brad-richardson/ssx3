# Proposed next brief — close the actual runner observation exit

This is E15's **one next-action recommendation**, not new authorization.
E15 exhausted its single boot and closes with a measurement-incomplete
(iii-shaped) stop. No MPEG implementation, CSV change, regeneration or E14
absorb retry is proposed here.

## 1. Preserve and reverify

| Item | Required checkpoint |
|---|---|
| Fork | `67c0a632d44cad8c0e47b4e2c0ee3782b22fd467`, branch ssx3, pushed to fork only |
| Protected build | `/tmp/p1-link/runtime`; also protect DerivedData; no assumed reclamation |
| Runner | `7544d4ebde5d501e450f473c0d81073cc312d48335fa03dfbb7c76eafaf2f599` |
| Suite | `8ba90048da7804a3dd278f172efbeb92d968ca89fd4ac9209b243e3d15c5a2eb`, 452/0 |
| Generated/config | Same 9,452 names/hashes as E15 `before/generated.json`; registry `98753bfa…`; CSV `0c608574…`; no regeneration |
| Fixtures | Actual leaf24/consumer3/predicate14/query4/DROP pass; MPEG `no-input` and `input` both expected rc1 FAIL-BEFORE. Actual fixture SHA `b0aefc016c69a0dd693093828bda828a1c7f9eaf36c17a38bb757763642321f2` |
| Source changes | E15's five observation files only; MPEG.cpp/h unchanged; inherited generated registry dirt and untracked fork log remain outside staging |

Fresh explicit small-budget admission is required before any extension or
link. Do not infer availability from E15's ending free space. Retain the hard
stdout cap, APFS suite-data control charged to the evidence reservation, and
owned-path allocation checks. Include shared boot `ps2_log.txt` in whole-task
SSD accounting as well as the boot-specific byte caps. Keep list/stat cleanup
races harmless. No budget increase or reclaim is implied.

## 2. Forcing closure receipt and observation-only repair

| Before | Required repair / proof |
|---|---|
| `main.cpp:252 runtime.run();` then `:259 std::_Exit(0)` | Do not change main or rebuild its generated unity group merely to reach a destructor. Emit diagnostic closure from the existing handwritten runtime run-exit path |
| Destructor-only hook at runtime.cpp:698–699 | Call the same closure operations after `gameThread.join()` and after the last diagnostic producers finish, before `run()` returns; retain safe destructor fallback |
| E15 fixtures close naturally | Add an actual-linked non-title fixture for the run-exit closure path; fail before the repair, pass after. A synthetic manually appended footer or destructor-only test is insufficient |
| Quiescent event source | Test last event below tick603 with no subsequent guest event; verify a real E15 counter footer and E7 shutdown footer still appear |
| Duplicate/error exit | Closure must be idempotent with explicit-run plus destructor fallback; safe when taps disabled, unopened, or normal window already complete. Verify no guest register/RAM/scheduling behavior change |
| Counter acceptance | calls=returns+unwinds, pending=0, registration truncation false, contiguous event count equals footer count; final boot/boundary/packet counters and truncation flags present |

Rebuild only handwritten runtime/test code, `-j2`; relink the actual fixture
against the current runner objects. Full suite and all prior actual-binding
cases must remain green. The two MPEG delivery cases must still fail before
an implementation. No MPEG behavior edit belongs in this repair.

## 3. Separately authorized guarded probe

The orchestrator must assign a fresh boot cap; a single probe is the proposed
scope, not an allowance inherited from E15. T13 preclaims, suite re-green,
fresh hashes/space, shared lease, wall/progress/logical/allocated-byte caps,
REPORT_ALL=1, E15/E7/E4 observations; if lease occupied, table and stop.
Release immediately at the first binding cap before analysis.

| Required join | Probe / acceptance |
|---|---|
| Objects and lifetime | Re-derive S from `0x4a289c`, MC from constructor `0x2c3fc4` / vtable `0x486f78`, UI store `0x23d5c8`; stop object interpretation at reuse |
| MPEG request | Join actual Create/register/GetPicture original args and supplied continuation by dynamic MPEG object, not E15 numeric addresses |
| Callback absence/delivery | Preserve separate eligibility, scheduler selection, invocation, valid-no-input, AddBs/input/completion and lifetime fields; do not call callbacks manually |
| Graphics | Reuse guarded UI3→6 alignment. Retain this run's primary copy bytes, GS receipt, [arm,freeze) source/D VRAM and actual later field-processed Present. An earlier upload is not the primary copy's output receipt |
| Shutdown | Require real final source footers from the run-exit path, even after source quiescence; count match, pending/truncation checks. `_Exit` must occur only after those recorded observations |

| Observation | Stop / handoff |
|---|---|
| Closure and guarded joins complete, same missing MPEG delivery | Table a complete diagnosis for a later separately authorized MPEG implementation brief; preserve E15 ABI constraints below |
| Another measurement gap | Name the missing receipt and repair only that gap; no additional boot without its assigned cap |
| Different runtime/guest dependency | Name the first demonstrated edge and stop; no automatic storage/CD/SIF/input promotion |

## 4. Parked MPEG design constraints, not work in this brief

E15's original ELF closes `(mpeg, callback-data, userdata)`, type word1 only,
callback v0 ignored, and type1 service within the GetPicture caller thread
during IPU busy polling. A later generic implementation must preserve that
ownership, avoid the MPEG mutex during AddBs reentry, and test request order,
no-input behavior, delivery, completion, cancellation/lifetime and existing
stream callbacks. Do not assume a synthetic RPC-callback thread preserves
the original call contract. GetPicture's architectural type1 trigger is
specific; other callback types/layouts must not be invented.

I19 independently identifies the device-side missing selector; its FFmpeg-OFF
decoder residual is downstream. E15 host is FFmpeg-ON. Neither lane has
implemented a fix, and closure repair does not authorize stacking one.

**E15 NEXT-BRIEF TAIL COMPLETE — one measurement repair and newly authorized
probe proposed; no MPEG fix, regeneration or absorb authorization implied.**
