# E17 handoff

| Item | Receipt / next boundary |
|---|---|
| Absorb commit | `e63f1616320d12c3f213899af6fba03fee3eafb2`; pushed to `fork/ssx3`, HEAD/tracking/ls-remote agree |
| CSV | `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba`; exactly five insertions; existing query/predicate/leaf retained |
| Regression | Suite452/452; five exact bindings; leaf24/consumer3/predicate14/query4/DROP; six E16 closure cases; both E15 MPEG delivery cases remain rc1 FAIL-BEFORE |
| E17 boot |1/1 spent. Real6,386-event source footer,5=4+1 scope closure,pending0,truncation0; complete dynamic request and graphics joins. No E17 boot remains |
| Protected builds | /tmp/p1-link/runtime remains E16 with554 hashes unchanged; /tmp/e17-map-link/runtime is the verified E17 build. Retain both and DerivedData |
| I-lane action | Dedupe local ports against the following exact CSV lines in the named fork commit; I-lane performs its own dedupe brief. No I-lane edits in E17 |

| Origin | CSV line | Exact row |
|---|---:|---|
| I12 | 873 | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` |
| I13 | 1022 | `sub_00156750,0x156750,0x1567b8,0x68` |
| I14 | 2943 | `sub_00243A80,0x243a80,0x243ab0,0x30` |
| I11 | 7012 | `sub_00395730,0x395730,0x395750,0x20` |
| I15 | 7176 | `sub_003A0158,0x3a0158,0x3a0290,0x138` |

| Later MPEG brief | Required boundary |
|---|---|
| Queue | Five-row absorb landed; MPEG brief is now unblocked and queued. E17 made no MPEG implementation change |
| First missing edge | Dynamic MPEG0x587b30, type1 registration func0x3b0b10/userdata0x587b00, GetPicture request at0x3b1020→typed wait0x3b1028; selections/dispatches/returns/AddBs/input/completion all0. Object addresses are this boot only; rediscover dynamically in later probes |
| Observation limits | Private callback-map selection is not tapped; static stream=false versus stream=true selector eligibility is separate. Zero valid-no-input returns is absence, not a guest no-source outcome |
| Original ABI | Callback receives(mpeg,callback-data,userdata); original type1 producer initializes only word0=1; callback v0 is discarded there. Do not invent a stream-event layout or use callback v0 as EOF. [E15-ABI.md](E15-ABI.md) retains instruction-level proof |
| Continuation / delivery | Preserve supplied continuation, full128-bit saved registers and RAM; service actual request-driven callback delivery with independent selection/dispatch/return/AddBs/completion receipts. No synthetic footer, manual callback, no-input conflation or guessed wall cadence |
| Existing API differences | Original AddCallback returns previous function vs HLE handle; original AddBs returns1 vs HLE copied bytes. Tabled separately; neither substituted for missing delivery or repaired in E17 |
| Future probe admission | A later authorized brief needs fresh allocation admission,T13 preclaims,shared lease and its own boot cap; occupied lease→stop without waiting |
| Evidence | [REPORT.md](REPORT.md), [boot-analysis-summary.json](boot-analysis-summary.json), [fork-push.json](fork-push.json), [TAIL-RECEIPT.md](TAIL-RECEIPT.md) |

**E17 NEXT-BRIEF TAIL COMPLETE — I-lane dedupe handed off; MPEG queued; E17 stops after its evidence commit.**
