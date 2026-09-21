# E18 experiment contract

| Item | Bound / observable |
|---|---|
| Start / deadline | 2026-09-21T18:38:00.452951+00:00 / 2026-09-22T02:38:00.452951+00:00; eight hours |
| Required reads | Full I20 REPORT (complete chunks/tail), E15 NEXT-BRIEF including §4, E16 NEXT-BRIEF, full E17 REPORT; consumed I20 A1–A13/P1–P3/S1–S10/H1–H6 |
| Hypothesis | Generic non-stream selection and GetPicture-triggered type1 delivery preserve caller-thread/stack ownership and enable actual AddBs/completion without changing stream behavior |
| Observable | Checkpoint9457/suite452/prior+closure/MPEG fail-before; ownership audit first; fixture rc1→rc0; R1–R6; one guarded probe joins delivery/input/completion or the first exact missing edge |
| Ownership gate | Queue/RpcCallback evidence for and against compared; failure to preserve caller ownership selects synchronous current-thread invocation, not a guest-PC special case |
| Permitted fork files | MPEG.cpp; MPEG.h only if cross-TU trigger necessary; regression tests. No scheduler/main/CSV/generated edits; need for regenerated source→stop |
| Internal budget |6GiB: build4GiB,evidence1GiB,scratch0.5GiB,reserve0.5GiB (including32MiB evidence Git cap);2GiB floor+0.5GiB guard; admission9,126,805,504B; stop owned5.5GiB or free≤2.5GiB |
| SSD budget |16GiB: temporary8GiB,fixtures2GiB,probe1.5GiB,source/Git1GiB,reserve3.5GiB;2GiB floor+0.5GiB guard; admission19,864,223,744B; stop owned15.5GiB or free≤2.5GiB |
| Fresh admission | Internal 13019901952B; SSD 230192840704B; both fit before edits/builds. Recheck before behavior mutation |
| Allocation | st_blocks×512 includes ExFAT directory/AppleDouble allocation; all E18 owned paths, positive fork source/Git growth, shared boot ps2_log.txt charged; COPYFILE_DISABLE=1 |
| Protected | /tmp/p1-link, /tmp/e17-map-link, DerivedData; no reclaim. New build /tmp/e18-mpeg-link/runtime, no generator invocation |
| Tool caps | Ninja-j2/CMAKE_BUILD_PARALLEL_LEVEL=2; configure1800s/build7200s/link1200s;15s reserve; stdout16MiB/reserve1MiB; temp8GiB/reserve512MiB; fixture2GiB/reserve64MiB; suite scratch32MiB |
| Probe caps |1 boot;90s/SIGTERM75s;1M syscall lines;1.5GiB logical/allocated aggregate; boot256MiB,trace96MiB,function1GiB;E4 12/64MiB,park32/128MiB,frames32/64MiB,E7 8/64MiB;8MiB reserve;REPORT_ALL=1 |
| Probe gates | Full regression green first; fresh T13/space/hash/suite and shared atomic P-lane lease. Occupied→table and stop; never wait. Release before analysis |
| ABI | Callback(mpeg,cbData,userdata), cbData word0-only, callback v0 discarded; type1 trigger only; mutex-free AddBs reentry; pending cancellation and no-input distinct |
| Stop | Any regression red→table and stop/no boot. First missing link after delivery ends behavior work; no decoder/EOF/lifetime second fix, guest-gate bypass, iOS FFmpeg change or sema change |
| Publication | BEHAVIOR fork commit with named permitted files; push fork only, ls-remote agreement. Standalone E18 evidence force-added [E18], Orchestrated-By: Muse Code; no main ssx3 push |

**E18 CONTRACT TAIL COMPLETE — before behavior source edits, builds or title launch.**

| Fresh probe progress guard (declared before the sole launch) | Bound / reason |
|---|---|
| E7 source-window evidence | `ps2_e7.h` stops event rows after tick603, while E15 lifetime counters continue. A progressing MPEG path can therefore invalidate count closure if captured past that window |
| Added progress stop | Signal at first sampled E7 tick≥540 (0.25s polling); 63-tick reserve before source window end603. Existing 90s wall/75s TERM, 1M syscall and all byte ceilings remain upper limits |
| Interpretation | This is one title probe, not a fixture; no second launch. Final footer tick and exact count agreement are checked, never assumed. No observed later dependency before this guard is reported as unobserved |
| Source scope | Evidence capture driver only; no runtime observation or scheduler edits |
