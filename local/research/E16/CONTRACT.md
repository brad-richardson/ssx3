# E16 experiment contract

| Item | Bound / observable / stop |
|---|---|
| Start / deadline | Admission clock 2026-09-21 16:17:13 UTC; eight-hour deadline 2026-09-22 00:17:13 UTC |
| Scope | E15 NEXT-BRIEF §1–§3 only; checkpoint rebuild, observation exit repair, ≤1 guarded title probe. No MPEG implementation, CSV/map change, guest regeneration, E14 absorb, or main edit |
| Checkpoint hypothesis | Remote fork/ssx3 and local HEAD/tracking ref equal 67c0a632d44cad8c0e47b4e2c0ee3782b22fd467; 9,452 generated names/hashes and config hashes match E15. Mismatch stops |
| Repair hypothesis | Existing E15/E7 closures called after the game thread joins and the remaining diagnostic producers finish in PS2Runtime::run() produce real final counters before main's _Exit |
| Forcing observable | Actual-linked non-title fixture calls run(), inspects footers before destruction, then uses _Exit; fail before/pass after. Quiescent last event <603, normal-window-complete, disabled/unopened, and destructor fallback/idempotence cases |
| Regression observable | Suite 452/452, leaf24/consumer3/predicate14/query4/DROP; both actual MPEG delivery cases remain rc1 FAIL-BEFORE. Full RAM and relevant 128-bit register receipts retained |
| Probe observable | Dynamic objects/lifetimes and MPEG Create/register/request/wait; separate eligibility/selection/invocation/no-input/AddBs/completion; guarded UI3→6 copy/GS/VRAM/later Present; real final footer count/pending/truncation checks |
| Alternatives / stop | Identity mismatch, unfitting admission, occupied lease, first binding cap, missing measurement receipt, or first different demonstrated dependency is tabled. No second title boot |
| Internal allocation | 4 GiB build + 512 MiB evidence/test scratch + 512 MiB repair/link reserve = 5 GiB positive allocation; 2 GiB free floor + 512 MiB guard; admission requires 7.5 GiB. Stop growth at 4.5 GiB or free ≤2.5 GiB |
| SSD allocation | 12 GiB total: 8 GiB tool temporary, 1 GiB fixtures, 1.5 GiB probe, 1.5 GiB reserve; 2 GiB free floor + 512 MiB guard; admission requires 14.5 GiB. Stop at 11.5 GiB or free ≤2.5 GiB |
| Accounting | st_blocks×512 allocated bytes including directories/sidecars on ExFAT; logical bytes separately. Include shared boot ps2_log.txt. COPYFILE_DISABLE=1 on all SSD operations. Harmless vanished-path races. No reclamation authorized |
| Build | Host -j2. Configure ≤1800 s, full rebuild ≤7200 s, repair ≤1800 s, fixture link ≤1200 s, each 15 s termination reserve. Hard bounded stdout 16 MiB with 1 MiB reserve. Temp stop at 7.5 GiB; fixtures stop at 960 MiB |
| Generated code | Compile existing generated sources only as required to reconstruct lost checkpoint; no regeneration. After repair, dry-run and actual log must exclude generated/main unity rebuild |
| Non-title fixtures | Actual runner objects and registry, separate entry point; no ELF/title execution; bounded wall/log/allocation. APFS suite scratch ≤32 MiB within evidence budget |
| Probe lease/caps | Fresh T13 preclaims; /tmp/ssx3-p-lane-lease; occupied → table and stop, never wait. REPORT_ALL=1. One 90 s probe, SIGTERM at 75 s, no inherited boot allowance; absolute ≤600 s |
| Probe bytes | 1.5 GiB aggregate logical/allocated; boot 256 MiB, syscalls 96 MiB, function trace 1 GiB; E4 12/64 MiB, park32/128 MiB, frames32/64 MiB, E7 8/64 MiB logical/allocated; 8 MiB allocation reserve; 1,000,000 syscall lines |
| Source tap limits | E7 boot4 MiB/boundary1 MiB/packet512 KiB, ≤16 aligned packet files, ≤4 extra aligned actual Present pairs; source truncation flags must be false |
| Commit | Observation-class named fork file only; generated sources never staged, MPEG.cpp/h unchanged. Fork remote only if publishing authorized; this task's final instruction is no push. Standalone E16 forced staging, [E16] prefix and Orchestrated-By: Muse Code trailer |

**E16 CONTRACT TAIL COMPLETE — declared before rebuilding, repair, link, or boot.**
