# E15 contract — MPEG request/delivery observation only

Start 2026-09-21 12:39:32 UTC; eight-hour deadline 20:39:32 UTC. Baseline
fork `83fb4d60904abb016522c477cce704c52118f95f`. E14's five-row absorb stays
queued. No map edit, regeneration, generated-code rebuild or MPEG fix.

| Hypothesis / observable | Alternative / stop |
|---|---|
| E13 checkpoint is unchanged | Complete generated/config/binary identity, suite and prior leaf 24 / consumer 3 / predicate 14 / query 4 / DROP checks before extensions |
| Small observation budget fits | Fresh persisted admission before extending taps or fixture; if unmet, stop with exact shortfall. No reclamation targets are assumed |
| Type-1 registration precedes a real GetPicture request but receives no delivery | Actual-wrapper fixture and guarded boot distinguish registration, selection, invocation, valid no-input return and delivered input; original args and ABI receipts required |
| State 3→6 supplies the graphics capture trigger | Same-run constructor/UI guards and the old/new state write arm a bounded packet/source/GS/D/field-Present window; no fixed 599–603 substitute |
| Explicit closure proves observation completeness | Shutdown footer reports event/packet counts, pending observed calls and truncation flags independently of a future guest event |
| Scope closes at diagnosis | Request/delivery gap with ABI receipt → proposed later fix brief; different dependency → exact probe; missing/unfitting measurement → outcome (iii)-shaped stop. No fix in E15 |

| Resource | Declared bound and accounting |
|---|---|
| Internal admission | 512 MiB artifact-growth reservation + 1 GiB free floor + 256 MiB polling guard = **1,879,048,192 B**. This is a new no-regeneration observation budget; it does not lower E14's generation guard |
| Internal reservation breakdown | Up to 128 MiB evidence/logs, 128 MiB changed handwritten objects/libraries, 256 MiB transient runner replacement. Generated sources and generated object recompilation excluded |
| Internal runtime bounds | Abort at 512 MiB measured positive artifact growth minus 64 MiB reserve, or free bytes ≤1 GiB+256 MiB. Monitor active-build/evidence allocations; unrelated filesystem pressure is covered by the free-space guard |
| SSD admission | 6 GiB work/capture allocation allowance + 2 GiB free floor + 256 MiB guard = 8,858,370,048 B required. Owned task paths only |
| SSD build/link | TMPDIR on SSD, 4 GiB allocation cap with 256 MiB reserve; fixture output on SSD, 512 MiB allocation cap; 16 MiB tool log with 1 MiB reserve |
| Build / fixture wall | Handwritten targets only, `-j2`; 1,800 s build / 1,200 s fixture link, each with 15 s termination reserve. Dry-run dependency check must exclude generated translation units |
| Single probe boot | ≤1 boot, planned 90 s with 15 s reserve, ≤600 s absolute; 1,000,000 syscall lines. Shared P-lane lease; if occupied, table and stop without waiting |
| Boot byte caps | Aggregate 1.5 GiB logical/allocated on SSD; boot 256 MiB, syscalls 96 MiB, function log 1 GiB; E4 12/64 MiB, park 32/128 MiB, frames 32/64 MiB, E7 8/64 MiB logical/allocated; 8 MiB allocation reserve. Total SSD allowance still binds |
| Tap budgets | Existing E7 boot/boundary separation retained; aligned packet budget ≤512 KiB logical with bounded file count, and explicit truncation flags. Additional request events bounded within the declared E7 sink |
| Ownership / cleanup | `/tmp/p1-link` and DerivedData protected; no reclaim. All SSD steps export COPYFILE_DISABLE=1. Owned temporaries removed after close; canonical raws compressed after hash verification |
| Commits | Observation-only named fork files, generated sources never staged, fork-remote push only if committed. `[E15]` standalone evidence with `Orchestrated-By: Muse Code`; no main push |

The 1 GiB internal floor is the existing E13/E14 build/link floor; E15 adds
an explicit 256 MiB guard and measures internal growth. Admission is checked
again before extension and before each expensive command. Budgets are not
permission to proceed past a binding cap.

**E15 CONTRACT TAIL COMPLETE — recorded before checkpoint execution,
tap/fixture extension, compilation, linking or probe boot.**
