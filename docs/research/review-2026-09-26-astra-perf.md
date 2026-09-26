# RV4 — Odin performance: remove work, then expose overlap

2026-09-26, Codex. Recommendations for the orchestrator, not adoption decisions.
Read-only review; no builds, boots, device access, source edits, or new benchmarks.
Runtime citations use **R = PS2Recomp at `173b31f`**, read with `git show` (live tip `f949ff0`).
**V = R:ps2xRuntime/src/lib/vu/**; bare runtime filenames refer to the previously named directory.
Reports use ssx3 `3ba8794c`, except **VK1 Part 2 at `424a97a3`**, committed during this review.
paraLLEl source read: `ssx3-work/parallel-gs-ssx3`, `464f263`. No generated game code reproduced.

## Executive summary

- **The current evidence does not establish a route to 16.7 ms, much less 8.3 ms.** A useful
  planning case is roughly 35–50 ms after substantial serial optimization; a successful VU1
  split might reach 20–30 ms only with effective GS overlap. These are assumptions, not speed
  predictions. The explicit example and limitations are in §1. [N12 Table 2; VK1 Stage 1]
- **Fix the performance accounting first.** N12's 68.3 ms is wall time, distributed as though
  GameThread were continuously running. VK1 measures 54.6 ms CPU + 20.9 ms off-CPU in an early
  75.5 ms frame. Also, the quoted 10.81 ms libc/kernel includes other threads; GameThread's
  portion is **7.34 model-ms**. VU0 overlaps the VU bucket. [§3 receipt; N12 Table 2]
- **Block compilation is the largest identified CPU lever.** Aim for fewer state round trips
  and longer register lifetimes, not merely constant stalls. The proposed all-ready entry guard
  is a safe starting subset only with complete pending-state handling; it may miss hot loops.
  The Mac 1.12–1.2× estimate is plausible upside, not a conservative promise. [§2; VR2 Stage 4]
- **Audit Android optimization now.** `RelWithDebInfo` does not receive the helper's
  Release-only IPO setting; generated EE objects never receive that helper. Verify actual
  compile/link commands before an isolated ThinLTO experiment. [R build evidence in §1]
- **Queue VU0 compilation and bounded EE improvements; retain the VU1-thread park.** VU0 has
  a useful but overlapping ~5.5 model-ms envelope. Moving VU1 cannot remove VU0, EE, GS waits,
  or the work itself. Re-size the split after blocks on the Odin. [N12 Table 2/gate; §1]
- **Update the GS hypothesis:** VK1 Part 2A refutes frame-context starvation as the main cost.
  Four versus sixteen contexts leaves ~0.6 ms/context-advance time per present at 4×; the large
  unresolved span is `flush_submit`. More contexts and Vulkan presentation are not the speed fix.
- **True 120 Hz needs both a throughput architecture and a game-time change.** EE/VU0,
  compiled VU1, GS submission, and GPU work each need an approximately 8 ms service budget,
  with bounded queues and correct dependencies; 120 guest vsyncs alone does not prove
  twice as many simulation steps at normal speed. [§4; AGENTS.md Product direction]

## 1. Ranked levers and the real-time ceiling

Evidence anchors: [N12](../../local/research/N12/REPORT.md) Tables 2–5/gate; [VR2](../../local/research/VR2/REPORT.md) Stage 1/4/Gaps; [VK1](../../local/research/VK1/REPORT.md) Stage 1/Part 2A; [VB1](../../local/research/VB1/REPORT.md) profile/What’s left; [Q1](../../local/research/Q1/REPORT.md) microVU analysis.
**Model-ms** below means N12's original 68.31-ms normalization, not measured CPU milliseconds.
Savings are conditional reviewer estimates after stage 1 unless stated; regressions remain possible.
Rows overlap: do not sum upper ends. Confidence concerns gains; costs estimate focused engineering time.

| Rank / action | Lever and estimated saving per guest frame | Confidence / cost | Evidence and limit |
| --- | --- | --- | --- |
| 0 **do now** | Correct same-window CPU/wait attribution; no speed credit | High value / 0.5–1 day | §3; N12 and VK1 currently use incompatible anchors. |
| 1 **do now** | Gate the existing VU1 block work: **5–12 model-ms** beyond stage 1 | Low–medium / VR2's 3–5 days total, work underway | Roughly 15–35% of a 32–35 model-ms residual pair budget; requires substantial hot-path coverage and removal of state traffic (§2). |
| 2 **do now** audit, **queue** experiment | Android O-level/ThinLTO: **0–5 model-ms combined** | Low gain confidence, high confidence in configuration gap / 0.5–1 day plus build capacity | Build evidence below. Do not separately credit the EE/state-traffic savings this enables. |
| 3 **do now** attribution, **queue** fix | GS submission serialization: **0–10 actual wall-ms at 1×** as a planning envelope; larger 4× opportunity | Low / hours to localize, 2–5 days if batching suffices | VK1 Stage 1 exposes 20.9 ms total GT off-CPU; not all is removable. Part 2A localizes, but does not identify, the blocking submit mechanism. |
| 4 **queue** | VU0 static recompile: **2–4 model-ms**, within the ~5.5 inclusive envelope | Medium / 2–4 days | N12 VU0 subtree; R:ps2xRuntime/src/lib/ps2_runtime.cpp:2869; V:ps2_vu1_recomp.cpp:88. Not an extra 5.5 ms on top of VU1 total. |
| 5 **queue** | Remaining VU1 flag/scoreboard work: **0–2 model-ms** after blocks | Low / 1–3 days | N12 issue/hazard only 2.50 model-ms, shared with VU0; VR2 flag-liveness +0.6% is noise. Bigger claims must identify work still inside generated functions. |
| 6 **do now** attribution, **queue** one fix | Host libc/kernel/TLS/formatting: **0.5–2 model-ms** plausible, not 10.8 | Low / hours to attribute, 0.5–2 days per mechanism | §3: GT libc/kernel 7.34 model-ms, largely unidentified kernel PCs; N12 gate snprintf ~0.8 model-ms inclusive, TLS ~0.36 GT self. |
| 7 **queue** | Guest EE: **0.5–2 model-ms** from dispatch/local state/guard hoisting | Low / 1–3 days for a bounded hot path | N12 guest self 8.71; memory and control-flow evidence below. Large SSA/codegen redesign is a separate project. |
| 8 **queue** | PGO **0–3**, CPU tuning **0–2 model-ms**, NDK update **0 credited** | Low / 1–3 days; overlapping compiler envelope | Freeze block code first. Profile representative phases; prove the supported CPU target and emitted code. No blanket compiler-upgrade gain. |
| 9 **queue** measurement, **park** blanket pinning | Core placement: **0–2 wall-ms**, possible regression | Low / half-day paired experiment | N12 Table 5 already observes GT on prime CPUs 6/7; sustained frequencies vary. No evidence of a race spending most time on slow cores. |
| 10 **park** | VU1 thread: old model ideal **~21.6 model-ms** removed from serial path; after CPU fixes perhaps **8–18**, conditional on dependencies | Low / at least 1–2 weeks including ordering tests | N12 gate's 47–50 ms outcome is a sizing hypothesis, not measured overlap. Must separate VU0 and include GS backpressure. |

**Stage 1 transfer assumption.** VR2 measured 1.095× on the Mac only. Applying that *whole-frame*
factor to Odin gives 68.31/1.095 = 62.38 ms, a 5.93-ms saving; this is a scenario, not a ported
measurement. Different wait fractions, thermals, compiler settings, and pair-code fractions
invalidate direct multiplication. Budget roughly 4–8 model-ms pending an Odin pair. [VR2 Speed holds/Gaps]

**Android build evidence and order.** R:android/app/build.gradle:17 pins NDK `28.2.13676358`;
:69 selects `RelWithDebInfo`. R:ps2xRuntime/CMakeLists.txt:769 calls `EnableFastReleaseMode` for
both configurations, but `ps2xRuntime/cmake/ReleaseMode.cmake:37` sets only
`INTERPROCEDURAL_OPTIMIZATION_RELEASE`. The EE archive is created at CMakeLists.txt:690 and is
absent from the helper calls at :770. VU1 images belong to the runner at :719. This establishes
a source-config gap, **not the final APK flags**: remote build commands were not read. IPO is configuration-specific. [CMake documentation](https://cmake.org/cmake/help/latest/prop_tgt/INTERPROCEDURAL_OPTIMIZATION_CONFIG.html)

Inspect EE, VU1 and runtime compile commands plus the link; verify the effective `-O` option (expected O2). Test O3 and
ThinLTO separately; include `ps2_game_objects` in IPO coverage. Keep debug symbols, exact FP
semantics, and exception support. Avoid full LTO initially given the seven huge VU1 TUs and
documented Android compiler memory pressure. `-Bsymbolic` is already at R:ps2xRuntime/CMakeLists.txt:628;
PLT is only 0.065 GT model-ms (§3). This review found no `-fno-plt` in the pinned config; either
way, redoing PLT work is not a major lever. [R build files; VR2 Part 2A; N12 Table 2]

The root CMakeLists.txt:81–93 supplies generic armv8-a flags, not an Odin scheduling model.
For `-mcpu`, verify the actual core identity against the pinned NDK's supported targets and
audit option ordering; do not select a Cortex target or a first-generation Oryon model merely
from the product name. LLVM documents `-mcpu=help`; its `oryon-1` target is evidence of support
for that model, not a match to this device. Keep the ISA valid on every allowed execution core.
[Clang options](https://clang.llvm.org/docs/UsersManual.html), [LLVM Oryon target](https://lists.llvm.org/pipermail/cfe-commits/Week-of-Mon-20240506/575522.html)
PGO needs representative training and separate validation after codegen settles; never time its training build. [Clang PGO](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization)

**EE and VU0 specifics.** EE memory access is already specialized: known RAM addresses emit
FAST access, known MMIO runtime calls, unknown addresses guarded READ/WRITE.
[R:ps2xRecomp/src/lib/instruction_translator.cpp:82; ps2xRuntime/include/ps2_runtime_macros.h:475]
FAST_READ32 masks/wraps addresses and uses fixed-size memcpy, so replacing all access with
unchecked pointer loads is not a justified optimization. [R:ps2xRuntime/include/ps2_runtime_macros.h:262]
Local branches already use goto plus backward-edge checkpoints. External ordinary JAL still
uses `dispatchGuestBranch`; direct named function calls in the emitter are for Jump, not Call.
Specialize a measured hot constant-target call while preserving invocation/unwind semantics;
do not remove scheduler checkpoints or MMIO effects. [R:ps2xRecomp/src/lib/control_flow_emitter.cpp:175,210,323,
under ps2xRecomp/src/lib; N12 children report: dispatch 17.16% inclusive vs 0.16% self]
The inclusive dispatch share is mostly callees, not dispatch overhead. VU0 currently resets,
copies context in/out, and executes with a 4096-cycle budget; the generated lookup rejects
VU0 and non-16-KiB images. Port unit/address-mask/keying rules explicitly, and measure whether
reset/copies rather than dispatch dominate the remainder. [R:ps2xRuntime/src/lib/ps2_runtime.cpp:2869; V:ps2_vu1_recomp.cpp:88]

**Do-now brief sketches.** (1) Gate the already-running stage-4 lane against §2's state/budget
rules; request dynamic fast-path coverage weighted by baseline work, guard-failure reasons,
and an Android assembly check before extending the design. Use its existing build budget,
synthetic differential suite, det/GS checks, then a clean Odin pair; stop expansion if guards
miss hot loops or spills erase savings. (2) One build-audit brief reads actual commands and
sizes first, then one candidate enabling ThinLTO for the current Android configuration and EE
archive; at most two Android builds and an ABBA comparison after correctness checks. Preserve
other flags so the result is attributable; O3 waits for a separate decision. (3) Fold host and
GS attribution into §3's single measurement brief, then choose one mechanism; no speculative
kernel replacement or additional presentation rewrite.

**Ceiling, with arithmetic.** Even deleting N12's entire mixed VU bucket leaves
68.31−46.72 = **21.59 model-ms** (0.773×), so VU work alone does not close the old serial model.
An illustrative successful package saves 6 stage-1 + 9 blocks + 1 residual flags + 3 VU0 +
1.5 EE + 1.5 host + 3 additional compiler = 25 model-ms: **43.3 ms, 0.385×**. This motivates a
35–50-ms planning range, not a confidence interval. Avoid duplicate compiler/EE/block credit.
If the optimized VU1 portion were 22 ms and the rest 21 ms, perfect overlap would give 22 ms;
handoffs and exposed GS waits increase it. Thus 20–30 ms is an ambitious threaded *scenario*,
conditional on independently reducing waits; an unchanged GS path may exceed it. A pipeline
must satisfy both resource throughput and dependency latency. No valid real-time ceiling can
be inferred by subtracting all N12 rows from wall time. [N12 Table 2; VK1 Stage 1; §3]

## 2. Stage-4 design: keep the idea, narrow its promises

**Rank 1, do now: prove state residency and guard coverage.** The design is directionally right.
Current generated pairs tail-call through a function table; source-visible registers and
scoreboards live in the VU object between calls. A block can expose reuse to the compiler.
But a function containing repeated `issuePair<true>` calls is not automatically a register
allocator: helpers mutate the shared object, and opaque commit/GS calls can force spills.
[V:ps2_vu1_recomp.cpp:180–221; ps2_vu1_step_impl.h:217,304–434; VR2 Stage 4]

| Priority | Design correction / proposed implementation | Evidence or obligation |
| --- | --- | --- |
| **do now** | Retain exact pair fallback; guard **all relevant pending effects**, not only ready times and flags. Pending VF/VI/ACC/store writes can retire during the block. Preserve sequence cancellation and direct-pending tail timing. | V:ps2_vu1_step_impl.h:127–166; V:ps2_vu1_core.cpp:812–829; R:ps2xRuntime/include/runtime/ps2_vu1.h:412–439. |
| **do now** | Budget guard must cover issue/stall costs **and observable write tails** when committing early. Do not let the last write become visible before a cut where the pair path queues it. Preserve E/D/T, branch delay and VI branch-backup state. | V:ps2_vu1_step_impl.h:252–280,418–434,450–480; VR2 Stage 2's caught end-slot bug. |
| **queue** | Carry a compact normalized entry pipeline signature between known predecessor/successor blocks; specialize only hot signatures. Do not require every VF lane ready if the block cannot observe that lane before it becomes ready. | Q1 §Q1 unknown-entry/state-passing and §Mapping. This requires a dependency proof, not a relaxed unchecked guard. |
| **queue** | Use SSA-like versions of touched VF lanes, VI and ACC; load live-ins, keep locals across a hot loop, spill dirty architectural values at observable exits. Avoid copying the entire VF file. | V:ps2_vu1_step_impl.h:304–416 currently snapshots/reverts/copies writes; N12 Table 3 identifies adjacent hot pairs. |
| **queue** | Chain internal loop edges inside one host function, with budget safepoints and bounded code size. One function per tiny basic block still loses residency on every backedge. Preserve all architectural state at exits; “live-out” must include later fallback/readers. | V:ps2_vu1_recomp.cpp:180–221; VR2 Stage 4; Q1 §Q3. |
| **park** broad implementation | Handle XGKICK/Q/P by exact event boundaries before attempting whole-block cycle jumps; initially terminate unsupported blocks. An XGKICK ending one block can remain active through later blocks. | V:ps2_vu1_step_impl.h:69–82,217–227; core.cpp:806–829. LSU commits precede PATH1 consumption. |

**Cheaper alternative, queue:** fuse straight-line sequences of the existing inlined pair step
in one function, preserving dynamic scoreboard and exact cycle handling. Separately bypass
the snapshot/revert round trip for proven direct writes while retaining same-pair operand
shadows and sequence bookkeeping. This can remove table handoffs and expose redundant-load
elimination without a new static timing engine. Expect **1–4 model-ms**, low confidence; check
assembly before claiming even that. It can capture much of *handoff/copy* benefit, not most
of static scheduling's unmeasured benefit. Do not abandon the in-flight lane to build it now.
[V:ps2_vu1_step_impl.h:304–416; V:ps2_vu1_recomp.cpp:180–221; VB1 What's left]

**Estimate challenge.** VR2's 36% Mac pair share implies that a 1.12× total gain must remove
29.8% of pair time; 1.2× requires 46.3%, if savings are confined there. Removing 12–18% of
total time actually gives 1.136–1.220×. Both calculations assume all other time unchanged.
VB1's 48.3% sampled-load class predates VR2's control-load removals, includes sampling skid,
and is not a removable memory-stall fraction. It also cannot bound the cost of FP work, whose
loads, conversions, integer classification and stores live in other instruction classes.
[VR2 Stage 4; VB1 VU1 profile share; V:ps2_vu1_fmac_impl.h:39–163]

My planning range is **1.05–1.15× Mac**, with **1.2× a stretch** if hot-loop residency and
guard coverage are strong. A useful model is saved time = residual pair cost × covered
work fraction × local cost reduction − guard/spill overhead. A whole-pipeline-empty guard
may make that first fraction small; a loop-state signature can improve it. Odin may gain
more from larger pair share or less from waits/thermal behavior. Measure, do not transfer.
The §1 block estimate assumes roughly 0.6–0.9 coverage and 0.3–0.4 local reduction, less overhead.
[N12 Table 2; VR2 VU1 profile; Q1 §Q1]

**Correctness gap:** the existing differential suite omits XGKICK, EFU/WAITP, MFP, JR/JALR and
I-bit pairs. Add fixtures for any of these that the block fast path admits, with active-entry
pipelines, overlapping masked writes, branches into delay slots, and cuts/resume/fresh execution
through the last write's landing. Compare VU state, cycles, data memory and ordered GIF output;
fallback-only cases still need an exit-state test. The existing game hash route alone is not
proof for newly admitted interactions. [VR2 Gaps; Q1 §Q2–Q4; §1 do-now block brief]

## 3. What the measurements do not establish

**Rank 1, do now: the single most decision-changing measurement is a matched-window Odin
critical-path timeline**, after stage 1, with GT running versus blocked time and the GS/GPU
dependency causing each material block. It decides whether more VU optimization buys wall time
or simply exposes an existing submit bottleneck. VK1 already shows why this could change the
plan: GT is only 72% busy at 1× and 52% at 4× in its early-race windows. [VK1 Stage 1]

**Brief sketch:** use one pinned route/save and identical guest-tick endpoints, APK/codegen/GS
SHAs, 1× settings, sound and thermal protocol. One diagnostic run records scheduler on/off-CPU
intervals, thread CPU deltas, frequency residency, GS queue depth and waits, and GPU timestamps;
split `flush_submit` into `device->submit`, both `submit_empty` calls and compilation drain.
First resolve *which thread blocks on what*, then classify GT self work by caller (VU0 vs VU1,
formatting, TLS, unwind). Bound to one instrumented build/run plus clean before/after controls;
an additional 4× diagnostic run only if needed to distinguish the submit mechanism. Report
diagnostic overhead and separate clean speed results. Existing VK1 timers, N12 bucketer and
phase tools supply most of the scaffolding. If submit is not the wait, hand back the actual
stack; do not pre-authorize a submit-thread implementation. [VK1 Part 2A; N12 Exact commands]

**Recomputed evidence, no new run.** I read `ssx3-work/N12/reportse.tgz` → `S2e.txt` in memory,
used N12/buckets.py's STAGES regexes, and summed EventCount by thread. Raw text SHA256:
`b0f1f8002830d575b33c8660dd95202fefab50510a4a543bb193b7b3b8c14704`.
Total = 98,380,655,774 cycles; GT = 85,634,719,248 (87.0443%). Each model-ms below is
`68.31 × bucket_GT_cycles / GT_cycles`; reproducible from that archive and classifier.

| Bucket | All-thread cycle share | GT cycle share of all | GT model-ms |
| --- | ---: | ---: | ---: |
| Generated VU1 pairs | 48.414% | 48.414% | 37.994 |
| VU interpreter/other, shared | 7.928% | 7.928% | 6.221 |
| VU issue/hazard, shared | 3.189% | 3.189% | 2.502 |
| Guest EE self | 11.097% | 11.097% | 8.708 |
| libc/kernel/vdso | 13.768% | **9.350%** | **7.337** |
| Scheduler/sync symbols | 2.135% | 1.491% | 1.170 |
| Bucket labelled profiler unwind | 0.913% | 0.913% | 0.716 |
| PLT | 0.145% | 0.083% | 0.065 |

**Corrections, ranked.** (1) N12's k makes GT CPU equal wall by construction; it cannot measure
sleeping time. Across threads, cycle weights at different frequencies are not CPU-time weights
either. VK1's 54.6/75.5 ratio illustrates the issue, but must not be applied numerically to
N12's different tick interval. “GsWorker 7.2 CPU-ms” is also model-dependent. (2) “VU1 total”
contains shared VU0 helpers; full VU0 children include other buckets, so simply subtracting all
5.5 from that bucket is not an exact disjoint split. (3) 10.81 libc/kernel is an all-thread
row, not a subcomponent wholly inside 21.59 GT-minus-VU. [N12 Table 2/Symbolization; table above]

**What libc/kernel likely contains.** N12 Table 3 has GT kernel self ~3.70 model-ms at an unnamed
PC, memcpy ~0.53, vfprintf ~0.45 and TLS ~0.36; none establishes the kernel's cause. Futex/driver
work, exception-related loader work, and real formatting/copying are candidates, not labels for
unknown PCs. Much `clock_gettime` in the committed self report is on the main thread. Also
“profiler unwind overhead” is an unproven classifier: those samples are on **GameThread**, and
the scheduler uses `throw EeDispatcherTransfer{}` when blocking. Verify its caller before
subtracting it as measurement noise. [N12 reports/s2-self-comm-sym.txt and s2-children.txt;
R:ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2699; N12/buckets.py STAGES]

Some snprintf is legitimate guest formatting; some scheduler drop arguments are formatted
before emitDrop's mute check. Attribute before removing or suppressing observability.
[R:ps2xRuntime/src/lib/Kernel/Stubs/Helpers/Support.h:1056; R:ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1624; R:ps2xRuntime/include/ps2_log.h:127]
Android minSdk 28 and API-29 ELF TLS support suggest a small Odin-specific build experiment:
target API 29+ and verify native TLS codegen, rather than replacing thread-local state with
unsafe globals. Do not count the entire cross-thread TLS share as GT savings.
[R:android/app/build.gradle:21; N12 Table 3] [Bionic TLS support](https://android.googlesource.com/platform/bionic/%2Bshow/52f14fd2178e2670dee604a1a269f73863d09deb/android-changes-for-ndk-developers.md)

**Queue measurement hygiene:** report identical tick-window distributions and sustained
warm-run p50/p95/p99, frequency residency and thermal status during the window. N12's cooldown
did not prevent race status 3 and CPU7 2246–4320 MHz; its late-race bins speed up with workload.
Unpaced means throughput headroom, not paced delivery; N12 SF ~60 presents/s coexists with
14.64 guest vsyncs/s. S3 spans menus, loading and early race, so it cannot set a pure menu budget.
GPU busy 35–37% does not mean 3× GPU headroom: even the crude product 0.371×68.31 is 25.3 ms
busy per guest tick, with other work/DVFS/overlap unknown. Obtain per-guest GPU timestamps.
[N12 Tables 1,4,5; VK1 Stage 1]

## 4. True 120 Hz simulation

**Rank 1, queue: prove 60 Hz service budgets first. Rank 2, park: promise of 120 Hz.** Current
wall time needs ~4.1× for 59.94 Hz and ~8.2× for 120 Hz. Nothing measured here supplies the latter.
I cannot rule it out on this hardware, but it is implausible as the product of the listed small
optimizations. The conservative outcome is a much faster sub-real-time build. [N12 S1; §1]

The architecture would have EE/scheduler/VU0 on a fast core, compiled VU1 on another,
a GS consumer/submission owner, and overlapping GPU execution/presentation. Feed immutable VIF/microcode-generation jobs and
ordered GIF output through bounded queues. Synchronize guest-visible VU completion, shared
memory/code reuse, PATH ordering and readbacks; never share the mutable VU object unsafely or
assume a whole frame of independence. VU0 remains close to EE because its current entry copies
EE context synchronously. Offloading GS submission only helps if dependencies and queue
ownership allow GT to continue. [R:ps2xRuntime/src/lib/ps2_runtime.cpp:2869; V:ps2_vu1_step_impl.h:217; Q1 §Q4; VK1 Part 2A]

For 120 unique rendered updates, target **each** EE/VU0, VU1, GS CPU and GPU stage below roughly
8 ms sustained, with synchronization margin inside 8.33 ms; for 60, below roughly 16 ms.
More buffers cannot repair a stage whose service time exceeds its budget. VU1 likely needs
loop-sized register-resident code, static pipeline/flag versioning, exact SIMD arithmetic where
profitable, and cold fallback. GS needs measured submit batching/overlap and lower GPU service
cost at the chosen resolution. Threading alone leaves today's VU1 work far over either budget.
[§1–§3; Q1 §Q1–Q4; N12 Table 2; VK1 Part 2A]

Separately, inspect the stock physics/input/timer cadence. Doubling the emulated vsync clock
may merely run the game faster; duplicated or interpolated images do not increase simulation
rate. Establish unique update counts, normal-speed race timer/distance under fixed input,
consistent audio and input sampling, then change timestep-dependent physics, animation and
timers coherently. No such game-time analysis was performed in RV4, so 8.33 ms is a target
service budget, not proof that the stock guest frame maps to a 120 Hz physics step.
[AGENTS.md Product direction; N12 Table 1 and screencap readings]

## 5. Other concerns and disagreement with the previous review

1. **do now, via §3:** stop describing the 4× penalty as a presentation-copy problem or a
   frame-context shortage. VK1 Stage 3's pixel-correct Vulkan prototype was speed-neutral;
   Part 2A refuted the context hypothesis. Also keep per-present and per-guest-frame units
   separate: Stage 1's 4× run presented only ~0.8 times per guest tick. `flush_submit` is an
   inclusive span, not an extra stage to add to GT blocked time. Its children still need timing.
2. **queue:** track hot text size, spills and instruction-cache behavior along with speed.
   Seven giant VU1 TUs and per-pair functions make “inline everything/O3/full LTO” a hypothesis,
   not an automatic win. Hot-only block versions and cold fallback may beat indiscriminate
   cloning. Exact FMAC uses double already; there is no remaining default quad-to-double win,
   and fast-math would change the correctness contract. [R:ps2xRuntime/CMakeLists.txt:711;
   R:ps2xRuntime/include/runtime/ps2_vu1.h:12–20; V:ps2_vu1_fmac_impl.h:39–163; VB1 VU1 profile share]
3. **park** blind affinity and exception rewrites. N12's prime-core observations argue against
   treating placement as a hidden multiplier; the libunwind row argues for attribution, not
   removal of scheduler semantics. Measure running/blocked time and sustained clocks first.
   Compare default placement with GT on 6/7 and GS/compile workers elsewhere; never pin the whole
   process to the prime pair. [N12 Tables 4–5; R:ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:2699]
4. I agree with the [Fable review](review-2026-09-25-fable.md) §3 that VU1 alone is insufficient
   and correctness gates precede complexity. I disagree with reusing its **~2× thread sizing**,
   **20–35-ms static-scoreboard saving**, or PLT-led host plan now: N12 is a new baseline, most
   scoreboard/PLT work has already gone, and the bucket model masks waits and overlaps VU0.
   Its identification of branch/MMIO correctness risks remains relevant; optimizing away those
   contracts would be a regression, not progress. [N12 Table 2; VR2 Stage 1; R build evidence]

Limits: no APK disassembly, PMU experiments, Android command audit, or new validation.
Estimates propose measurements. Only this report is written; no other lane or planning file is changed.
