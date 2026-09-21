# Proposed next E-lane brief — restore exact `0x2c5358` result and join UI flag bit3

This is a proposal, **not authorization**. E12's predicate-only regeneration
exception is closed. A new bounded exception is required for one entry.

| Prerequisite | Checkpoint |
|---|---|
| Fork baseline | `9da21ff8aeb9529368b32d91b0eec6a82ba79344`, pushed to fork `ssx3` |
| Active build | `/tmp/p1-link/runtime`; protect it and DerivedData |
| Generated mirror |9,451 names/hashes in E12 `after/generated.json`; registry `4fb59437942fd0b2bc1a9a3fd18a5fa4610d1867e4f2959d80a7c67db9f2bb21` |
| Runner |163,437,168 B; `97b8dc25fe315eb7b68a9fd83879fb4d9ef2a9ab1a71dd1283f724846220260c` |
| Regressions | Suite452/0; actual query4, predicate5300 fourteen cases, guest DROP handler all pass |
| Authorization needed | `0x2c5358` only; no analyzer sweep, second entry, HLE or storage change |
| Admission | Fresh persisted sample BEFORE CSV edit and again immediately before generator. At least1 GiB reservation +2 GiB floor +256 MiB guard. Separate build/link headroom; never assume E12's final free space persists |

## Forcing receipt

| Link | E12 evidence |
|---|---|
| Repaired predecessor | Both `0x2c5300` calls return0 for status0; caller advances and no UI+0x344 clear at`0x2421b4` occurs |
| Exact missing input | Raw9061 / E7seq5092 tick225: `0x2d3828→0x2c5358`, same-run MC=`0xb851a0`, vtable`0x486f78`, original a1=0, slot0=0, stalev0=`0x2c5358`, policy1 |
| Required leaf result | ELF`0x2c5358..0x2c53ac` returns **1** for status0 |
| Reached consumer | `0x241c3c` calls wrapper`0x2d3810`; `0x241c48/4c/58` computes `((v0 ^ 1) & 1) << 3`. Stale even value contributes **8**, exact1 contributes **0** |
| Downstream join | Flags stored by`0x241d10` toUI+0x43c; complete function trace reaches`0x23e608→0x23eb50→0x23cdb0`; ELF`0x23eb54` supplies state4. Direct flag-word/state-argument taps remain required |
| Challenged premise | Nonzero branch equivalence does not imply exact-result or low-bit equivalence. Do not validate this entry with truthiness-only assertions |

Read E12 REPORT, `e12a-residual-join.json`, complete residual receipts,
predicate/flag/selector ELF, and actual generated source pins before editing.
The screen remains the no-card message; no storage/input dependency follows.

## One-entry repair and regressions

| Step | Required check |
|---|---|
| Checkpoint/fail-before | Re-verify full manifest/binaries/suite. Relink actual-binding fixture; sibling `hasFunction=false`; expected-present must fail before mutation. Do not repeat earlier repairs |
| Fresh admission | Persist before CSV edit, recheck before spawn. Reclaim only independently proven retired trees, oldest-first, live board + no handles; stop at admission +512 MiB. Never active checkpoint/DerivedData |
| Sanctioned row | Insert `sub_002C5358,0x2c5358,0x2c53b0,0x58` after `sub_002C5338,0x2c5338,0x2c53b0,0x78`, before `sub_002C53B0`; preserve owner, query and5300 rows |
| Predicted CSV SHA | `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4`, computed without editing the E12 CSV |
| Generate/install | Owned bounded APFS output; normal exit, complete manifests, exact registry/body check; changed bytes only/no metadata; generated runner sources never staged; clean scratch after installed-copy verification |
| Actual-binding leaf cases | **Each port0 and1**: true for `-10001,-7,-5,-4,-3,-2,-1,0`; false for `-10002,-8,-6,1`. Include cross-port contradictory statuses; require v0 exactly0/1 |
| Preservation | Supplied RA, unchanged SP, full callee-save128 GPRs, whole RAM, no memory-card API call; no handwritten replacement |
| Consumer regression | Feed actual generated result to the reached low-bit calculation: status0 must contribute0; demonstrate the old stale`0x2c5358` contributes8. Prefer actual generated wrapper/consumer where practical, pin any isolated calculation to raw ELF words |
| Other regressions | E12 predicate5300 fourteen cases, busy query4, DROP empty-buffer RA/SP/s0, full suite, fresh pre-boot suite |

The precise truth table comes from raw comparisons: `-7` and`-10001` return1;
otherwise values below-6 return0; -6 returns0; -5 through0 return1; positives
return0. Both signed comparisons and both ports must be exercised.

## One guarded verification boot proposed

Same shared lease/fresh T13 checks/REPORT_ALL/E7/E4 and wall, progress, logical
and allocated byte caps. One boot; release immediately before analysis.
Original arguments must be captured before guest predicates mutate them.

| Probe | Purpose |
|---|---|
| Constructor`0x2c3fc4`, UI pointer`0x23d5c8` | Derive fresh MC/UI, require `[MC]=0x486f78` and `[UI+0x434]=MC`; never assume E12 heap addresses |
| New5358 call/return | Original a0/a1, selectedstatus, v0/RA/SP, sources`0x2d3828`,`0x23e364`; wrapper return`0x2d3830` and caller return`0x241c44` |
| UI flags | Direct UI+0x43c writes, especially PC`0x241d10`; capture old/new value and relevant MC statuses. Observe consumer before/after`0x241c48..0x241c64` without changing results |
| State route | Capture `0x23e608`, `0x23eb68` original statea1, and the target reached through UI+0x748; direct state-handler inputs and next state store |
| Prior guards | Predicate5300 returns, UI+0x344 store PCs, busy-query/request/completion, UIpending clear; bounded missing-target retention |
| Copy/frame | Singleton/S guards and packet/source/GS/D/field-Present join; changed pixels alone do not prove progression |

| Outcome | Stop / one next action |
|---|---|
| Exact result repaired and flag/state path advances | Join ensuing guest request and content; name one next action |
| Another entry or guest gate appears | Table its first forcing receipt and exact recipe; no stacked repair or menu claim |
| Resource, generation, binding or observation fails | Table that failure and its repair only; never lower a declared guard |

No storage/SIF/CD/input promotion without an actual guest request/completion
dependency. No raster/Present change follows from the faithful copy join.

**NEXT-BRIEF TAIL COMPLETE — proposal only; no `0x2c5358` repair executed in E12.**
