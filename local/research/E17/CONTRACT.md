# E17 experiment contract

| Item | Hypothesis / observable / bound / stop |
|---|---|
| Start / deadline | 2026-09-21T17:32:16.155688+00:00; deadline 2026-09-22T01:32:16.155688+00:00; eight hours |
| Scope | Reverify and absorb exactly five E14 rows together. No MPEG implementation, runtime/header/main repair, extra row, or second title probe |
| Checkpoint | Pushed fork/ssx3, tracking ref, and HEAD must be784f2b3e668ffa7a238936be415dc2e03d6c283c; all9,452 generated names/hashes; suite452/452; E16 closure and E15 expected MPEG failures |
| Row hypothesis | All five retained E14 row bytes, I-lane current owners/entries, and ELF slices agree. Any disagreement stops the entire absorb; all five absent0/present1 cases re-run before edit |
| CSV / regeneration | Five sorted insertions only; predicted7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba; rc0, exact slot receipts, five new entry files byte-equal to pinned I-lane; existing generated bodies unchanged |
| Regression | Full suite452/452; new presence5; leaf24/consumer3/predicate14/query4/DROP; all E16 closure cases; both E15 MPEG cases remain rc1 FAIL-BEFORE |
| Internal budget | 6 GiB: separate build4 GiB, APFS codegen1.25 GiB, evidence/scratch0.5 GiB, reserve0.25 GiB. 2 GiB free floor +0.5 GiB guard; admission9,126,805,504 B. Stop at5.5 GiB allocated or free≤2.5 GiB |
| SSD budget | 36 GiB: generated installation/Git growth24 GiB, tool temporary8 GiB, fixtures1 GiB, probe1.5 GiB, reserve1.5 GiB. 2 GiB floor+0.5 GiB guard; admission41,339,060,224 B. Stop at35.5 GiB allocated or free≤2.5 GiB |
| Fresh admission | Initial 14172160000 B APFS / 236978176000 B SSD; fits before any fork edit. Recheck after fail-befores immediately before CSV edit and generator spawn; insufficient space→exact shortfall and stop |
| Protected data | /tmp/p1-link and DerivedData never reclaimed; E17 separate /tmp/e17-map-link/runtime and /tmp/ssx3-e17-absorb-codegen. No preexisting deletion authorized or planned |
| Allocation | st_blocks*512 for files/directories/AppleDouble metadata; logical bytes separately. Positive fork/.git growth and all E17 SSD paths plus shared ps2_log.txt charged. COPYFILE_DISABLE=1 on SSD steps |
| Configure/build/link | Host Ninja-j2 and CMAKE_BUILD_PARALLEL_LEVEL=2. Configure1800s, full build7200s, fixture link1200s;15s termination reserve; hard stdout16MiB with1MiB reserve; SSD TMPDIR8GiB with512MiB reserve |
| Generator | Existing pinned tool/source identity; APFS output only; logical1GiB, allocated1.25GiB with128MiB reserve; wall1200s/reserve15s; stdout16MiB/reserve1MiB; no config change except derived output path |
| Installation | Changed bytes only, full output manifests first; only five new entries plus generated declarations/registry expected. Proven E17-created source-glob sidecars moved into owned quarantine, no preexisting metadata deleted |
| Non-title fixtures | Current runner objects/registry, alternate fixture entry. Reuse pinned E16 binary for checkpoint closure; relink E17 five-presence fixture before and after absorb. No title ELF boot |
| Probe lease / wall | ≤1 new E17 title boot; fresh T13 preclaims, REPORT_ALL=1, atomic shared /tmp/ssx3-p-lane-lease. Occupied→table and stop without waiting.90s total/SIGTERM75s; absolute≤600s |
| Probe caps |1M syscall lines; aggregate1.5GiB logical/allocated; boot256MiB, syscall96MiB, function1GiB; E4 12/64MiB, park32/128MiB, frames32/64MiB, E7 8/64MiB;8MiB allocation reserve |
| Required probe joins | Dynamic objects/lifetimes, request/registration/wait and separate callback/input/completion fields; guarded UI3→6 packet/GS/source/display/later Present; real run-exit footer count/pending/truncation checks. Changed dependency or missing receipt is tabled, no promotion without request/completion evidence |
| Mutation/commit order | Reverify→fresh admission→CSV/regen→full regression→one guarded probe→single MAP fork commit. E17 explicit generated staging overrides E14's older no-generated-staging continuation text; stage named generated delta plus CSV only, audit inherited registry delta explicitly |
| Publication | Push MAP commit only to fork remote and verify ls-remote equality. E17 standalone evidence force-added with [E17] and Orchestrated-By: Muse Code; no main ssx3 push |
| Alternatives / stop | Row mismatch, admission failure, generation/scope/regression failure, lease occupancy, or first binding probe cap; preserve receipts, table exact gap, no partial absorb or MPEG repair |

**E17 CONTRACT TAIL COMPLETE — declared before fixture links, fork mutation, generation, build, or title boot.**
