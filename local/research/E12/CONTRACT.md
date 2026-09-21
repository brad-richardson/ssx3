# E12 experiment contract

Start 2026-09-21 09:39:09 UTC; deadline 17:39:09 UTC. Latest main pull was
already up to date. E12 brief and all E11 REPORT/NEXT-BRIEF read. The renewed
exception authorizes only the exact `0x2c5300` predicate entry. `0x2c5358`
remains out. No busy-query or DROP regeneration is repeated as a separate phase.

| Hypothesis / observable | Alternative / stop |
|---|---|
| E11 checkpoint remains byte-identical. | Compare all 9,450 names/hashes, registry, runner and test binaries; suite plus busy-query four-case test. Mismatch → table before mutation. |
| Actual baseline lacks predicate entry. | Relink against baseline runner objects; absent mode succeeds and expected-present fails. No handwritten predicate or owner-only binding. |
| Fresh APFS admission permits one CSV row. | Persist before edit and immediately before spawn. If short, oldest retired tree only after live board and no-file-handle proofs; stop reclamation at admission +512 MiB. Unmet requirement → (iii), no CSV mutation. |
| Generated predicate returns `status[port] == -10002`. | Both ports: -10002 true; 0, 1, -10001, -7 false; selected/unselected-port cross-checks, RA/SP/callee-save128/whole RAM/no API calls. Busy-query four + DROP + suite regressions. Failure → (iii), no second fix. |
| One boot takes the correct caller path. | Dynamic MC/UI guards, original predicate a0/a1/status, return, UI+0x344 stores, query/request and packet/source/D/field-Present joins. First remaining gap → (ii), table only; demonstrated progression → (i). Observation failure → precise repair only. |

| Resource / ownership | Declared bound |
|---|---|
| APFS generation admission | 1 GiB logical reservation +2 GiB free floor +256 MiB guard = **3,489,660,928 B**; reclamation target plus512 MiB = **4,026,531,840 B**. Never lower either guard. |
| Initial space | Read-only sample: internal 1,474,560,000 B. No admission inferred from E11. Checkpoint/fail-before precedes the admission/reclamation phase. |
| Scratch | Fresh owned `/tmp/ssx3-e12-predicate-codegen`, only predicate regeneration; clean after installed-copy hash verification. Protect `/tmp/p1-link` and DerivedData. |
| Generation | 1 GiB logical /1.25 GiB allocated;128 MiB output headroom;2 GiB free floor+256 MiB guard;1,200 s wall with15 s reserve;16 MiB log with1 MiB reserve;0.25 s polling. |
| Compiler/linker outputs | Existing checkpoint objects; all new fixture outputs and tool temporary files on owned SSD E12 paths. Temporary allocation cap8 GiB with256 MiB headroom;SSD free floor2 GiB;baseline link wall1,200 s, rebuild wall1,800 s,15 s reserve;log16 MiB. Internal free monitored separately with1 GiB build/link floor; this does not replace the higher generation admission/floor. Builds -j4. |
| SSD installation | Changed bytes only, no metadata;24 GiB allocation-growth cap with256 MiB guard,2 GiB SSD floor. Proven-created companions only removed. Generated runner sources never staged. |
| Boot | At most one, planned90 s wall with15 s termination reserve, maximum600 s;1,000,000 syscall lines;lease required and never wait if occupied;release immediately after exit. |
| Boot bytes | Aggregate1.5 GiB logical/allocated;boot256 MiB,syscalls96 MiB,function trace1 GiB;E4 12/64 MiB,park32/128 MiB,frames32/64 MiB,E7 8/32 MiB logical/allocated;8 MiB allocation headroom,SSD floor2 GiB. |
| Retention / commits | Closed captures compressed, canonical copies and hash manifests;fork named files only, pushed to fork remote only;evidence `[E12]` with `Orchestrated-By: Muse Code`;no ssx3 push. |

No adb, second entry fix, new HLE, storage/SIF/CD/input promotion without a
named request/completion dependency, raster/Present change or extra boot.
Standing no-regen resumes at close. I16 may independently port the canonical
row; neither lane waits on the other.

**E12 CONTRACT TAIL COMPLETE — recorded before checkpoint execution, fixture
relink, reclamation, CSV mutation, generation, build or boot.**
