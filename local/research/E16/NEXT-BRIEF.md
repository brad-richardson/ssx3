# E16 handoff — queued work and retained constraints

| Queue / handoff | Evidence / boundary |
|---|---|
| E16 checkpoint | Rebuilt from remote/tracking/HEAD67c0a632; generated9,452 unchanged; suite452/452; prior SSD fixture reused; actual current-object fixture reverified |
| Observation repair | Local fork784f2b3e668ffa7a238936be415dc2e03d6c283c; one named runtime.cpp change; actual-linked non-title fail-before/pass-after; real boot source footers6410events,pending0,truncation0 |
| E16 boot allowance | **Spent1/1**; lease released; no additional probe authorized by this handoff |
| NEXT E brief | **E14 five-row absorb remains queued next**, untouched in E16. Re-establish that brief's own authorization/admission; no absorb retry was performed here |
| Later MPEG brief | Complete request diagnosis is tabled: dynamic Create→type1 registration→GetPicture→typed wait; callback selection0/invocation0; input0/completion0. Both delivery fixtures still FAIL-BEFORE. No MPEG implementation in E16 |
| Evidence scope | Private-map eligibility is inferred from unchanged source; scheduler selection, actual callback dispatch/return, valid-no-input outcome, AddBs, input, and completion remain separate fields |
| Owner-label caveat | One sub_003B0B40 owner log is the exact0x3b0c58 setup entry. It is not evidence of the exact0x3b0b40 helper or0x3b0b10 callback delivery |

| Preserved E15 §4 constraint for a later MPEG implementation | Required distinction |
|---|---|
| Original ABI | `(mpeg, callback-data, userdata)`; original type1 producer initializes only callback-data word0=1; callback v0 is ignored, never interpreted as EOF |
| Thread / stack / ordering | Original type1 service occurs in the GetPicture caller's thread and stack during the observed IPU busy-poll route; do not infer a host-wall callback cadence |
| Lock / reentry | A future guest callback must be able to reenter AddBs outside the MPEG mutex, with ownership/order preserved |
| Required behavior cases | Separate actual delivery, valid-no-input, completion, cancellation, lifetime, reentry, and existing stream callback behavior; a manual callback invocation is insufficient |
| API return residuals | Original AddCallback returns the previous function, current HLE returns a handle; original AddBs returns1, current HLE returns copied bytes. Differences remain tabled and unchanged |
| Input / decode residuals | No callback was delivered in E16, so source-read/feed/decode/completion failures cannot be inferred. Host FFmpeg remains enabled; I19 device path remains disabled and downstream |
| Source grounding | [E15-ABI.md](E15-ABI.md) and the six copied original-ELF disassembly receipts are standalone in E16; MPEG.cpp/h are pinned and unchanged |

**E16 NEXT-BRIEF TAIL COMPLETE — E14 absorb queued next; later MPEG work constrained, not implemented.**
