# E19 experiment contract

| Item | Bound / observable |
|---|---|
| Start / deadline | 2026-09-21T19:48:28Z / 2026-09-22T03:48:28Z; eight hours |
| Required reads | E18 REPORT187 lines and NEXT-BRIEF41 lines, including both complete tails, read before other work |
| Hypothesis | Parser emission depends on a completed picture/boundary in available input; a successful but incomplete AddBs feed may leave the caller without a further-input signal |
| Ordered questions | Checkpoint first. Q1 parser: retained64 + authored continuation byte marks5040/8192/16384 and measured first-packet threshold. Only after Q1 receipt: Q2 demand static audit + E18 silence. Only after Q2 receipt: Q3 one guarded demand-watch title boot |
| Alternatives | Boundary supplied and parser emits; no boundary and parser buffers; caller re-requests; guest sends again; an already buffered remainder remains undrained; a missing signal must be named |
| Payload limits | Only64 E18 bytes retained. Every authored byte is labeled and hashed. No claim of full E18 payload replay or a universal/game threshold inferred from synthetic continuations |
| Fix gate | Exactly one demonstrated edge with a minimal ABI-preserving change and its own fail-before. Guest needs unknown X, decoder change, EOF invention, or policy invention → name signal and stop. No stacked fix |
| Checkpoint | fork/ssx3=3adc0478; generated9457/hash audit; suite458; R1–R6; E16 closure6; E15 remainsrc0; all prior actual bindings |
| Internal budget |6GiB: possible isolated build4GiB, evidence1GiB, parser/scratch0.5GiB, reserve0.5GiB (including64MiB main Git). Floor2GiB+guard0.5GiB; admission9,126,805,504B; stop owned5.5GiB or free≤2.5GiB |
| SSD budget |16GiB: tooltmp8GiB, fixtures2GiB, probe1.5GiB (including parser observations), possible source/Git1GiB, reserve3.5GiB. Floor+guard2.5GiB; admission19,864,223,744B; stop owned15.5GiB or free≤2.5GiB |
| Admission | `initial-admission.json`, sampled and checked before creating E19; no reclaim/deletion |
| Accounting | st_blocks×512, including ExFAT directory and AppleDouble allocations, E19 tool/fixture/observation paths, shared function log and positive fork source/Git growth. COPYFILE_DISABLE=1 on SSD steps |
| Protected | /tmp/p1-link, /tmp/e17-map-link, /tmp/e18-mpeg-link and DerivedData; reused read-only. Any E19 build is isolated. No CSV/PS2 regeneration; need for it→stop |
| Build/tool caps | Ninja-j2/CMAKE_BUILD_PARALLEL_LEVEL2; a single direct compiler/linker process is ≤2 jobs and tabled. configure1800s/build7200s/link1200s;15s reserve; stdout16MiB/reserve1MiB; tooltmp8GiB/reserve512MiB; fixture2GiB/reserve64MiB |
| Parser-fixture caps | Non-title only; authored payload≤64KiB/case; aggregate evidence64MiB; process wall120s; input marks and API-call counts recorded; no decoder EOF flush used to manufacture packet1 |
| Probe |≤1 title boot,90s wall/TERM75s,1M syscall lines; aggregate1.5GiB logical/allocated. boot256MiB,trace96MiB,function1GiB; E4 12/64MiB,park32/128MiB,frames32/64MiB,E7 8/64MiB, parser16/64MiB;8MiB reserve |
| Extended observation | Existing E15 lifetime counters and parser-boundary observations continue after first input. E7's tick603 window remains a declared limit; no artificial second launch or tick540 early stop |
| Lease / T13 | Fresh binaries/ELF/suite/aligner/space/process checks; atomic shared P-lane claim. Occupied→table and stop, never wait |
| Regression stop | Any regression red→table and stop; no title boot on red |
| ABI carry | Caller-owned synchronous HleCall; word0-only cbData; callback v0 discarded; valid-no-input waits; dispatch outside MPEG mutex; registration order/dedupe; delete/reset cancellation |
| Publication | Diagnosis-only: zero fork commits. Gated single fix: named BEHAVIOR files only, fork push with ls-remote agreement. Standalone local E19 evidence force-added [E19], Orchestrated-By: Muse Code; no main-repository push |

**E19 CONTRACT TAIL COMPLETE — before source edits, compilation or title launch.**
