# E14 continuation recipe — restore APFS admission, then absorb the verified rows

E14 stopped at its mandatory admission gate. This document proposes the one
next action; it does not renew regeneration authorization. MPEG remains
queued for E15 and is not part of this continuation.

| Prerequisite | Receipt / action |
|---|---|
| Preserve checkpoint | Fork `83fb4d60904abb016522c477cce704c52118f95f`; `/tmp/p1-link/runtime` and DerivedData protected |
| Preserve inputs | CSV `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4`; all 9,452 generated names/hashes and binaries unchanged in `after/` and `closeout.json` |
| Completed checks | Five rows verified; five actual-binding absent checks passed and five expected-present checks failed; prior leaf 24 / consumer 3 / predicate 14 / query 4 / DROP and suite 452/0 passed |
| Binding stop | At 12:04:11.434666 UTC, free APFS bytes 3,217,489,920 < required 3,489,660,928; shortfall 272,171,008 B |
| Reclamation target | Admission plus 512 MiB headroom = 4,026,531,840 B; shortfall from that sample 809,041,920 B. Fresh measurements govern; these are not reservations |
| Exhausted eligible set | `/tmp/t12-dev-link` was proven retired and removed. The only remaining `/tmp/*-link` tree is protected `/tmp/p1-link`. There is no further safe deletion target in the inspected eligible set |

**One next action:** obtain the declared APFS free space through a separately
identified and authorized safe reclamation or an external free-space change,
then resume this same five-row absorb under a renewed bounded brief. Do not
remove the active checkpoint, lower any guard, switch back to ExFAT output,
or infer that an arbitrary `/tmp` tree is retired.

| Ordered continuation | Required receipt |
|---|---|
| 1. Re-verify identity | Compare canonical inputs, complete generated mirror, runner and fixture hashes against E14 closeout. Repeat the five presence expectations and existing regressions if the next brief requires fresh checks; a changed checkpoint requires renewed byte verification |
| 2. Fresh admission before edit | Persist current free space and floor/reservation/guard arithmetic before CSV mutation, with at least 3,489,660,928 B and the 4,026,531,840 B reclamation stop target. Recheck immediately before spawn |
| 3. Insert verified subset | All five currently verify; rows and raw bytes are in `row-verification.json` and `row-sources/`. Insert in address order without changing existing owners or the prior 2c5300/2c5358 rows |
| 4. Expected CSV | Five-row result must be `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba`, computed before editing and independently matching I17 |
| 5. Scoped regeneration | Fresh owned APFS scratch with the same declared bounds; only output path changes in the derived config. Complete manifests, exact bindings, new entry bytes matching the pinned I-lane entries, and unchanged prior bodies |
| 6. Install and validate | Copy changed bytes only, dispose only proven-created metadata, clean owned scratch after installed hash verification; build `-j4`; relink actual-binding fixtures; five presence checks plus leaf 24 / consumer 3 / predicate 14 / query 4 / DROP / full suite |
| 7. Commit and one boot | One named-files CSV commit pushed to fork remote only, generated sources never staged; fresh T13 checks and suite, one guarded boot under the shared lease, caps recorded, immediate release before analysis. If occupied, table and stop |
| 8. Close | Confirm MC/UI, query/predicate/leaf and Present joins; table the first wall or any observed advance. Do not pursue MPEG or another gap. Commit standalone evidence with the Muse trailer; no main push |

Unexecuted adapter drafts were removed at E14's stop; their disposition is
recorded in `unexecuted-adapters.json`. Use the committed E13 tools as the
starting point and adapt them to the five-row scope. E14's retained tools
cover only work actually executed, plus the actual-binding fixture.

**E14 NEXT-BRIEF TAIL COMPLETE — storage admission first; five named rows
only under renewed authorization; no MPEG work or boot authorized here.**
