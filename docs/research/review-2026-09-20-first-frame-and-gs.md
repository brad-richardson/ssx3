# PS2 recomp progress, evidence, and next steps — 2026-09-20

Prepared for Brad and the Muse orchestrator. Priority: a verified SSX 3 recomp frame, then the PS2 GS GPU path. This is a review and steering document; no implementation changes, builds, boots, clones, or cleanup were performed. It supplements, and where explicitly stated corrects, the [September 19 review and Part 4 hand-back](review-2026-09-19-progress.md).

## Decisions to make now

1. **Continue K1, with a corrected contract.** The copied `0x80075000` payload is a TLB helper lookup. Its six observed results include a **data address**, so a general “return an original syscall trampoline” fix is insufficient. The exact table and acceptance criteria are below. This correction was sent to Muse through Herdr while K1 was active.
2. **Park E3 boots behind K1; do the bounded host-write audit now.** T26 excludes watched guest stores during its window, not all writes. If the same park survives K1, E3 should resolve read/write order within one or two guest frames, including scratchpad DMA, rather than repeat a long writer census.
3. **Capture the next runtime framebuffer and inspect it.** Existing T26 logs already show successful 512×448 uploads and substantial GS activity. There is still no visually verified recomp frame in the reviewed evidence. Those are different claims, with different next actions.
4. **Give paraLLEl-GS a bounded adoption test before committing to a new renderer.** Its raw interface and shaders are substantially closer to the desired GPU work than the broad recomp surveys. First verify actual initialization and a short SSX GS dump replay on the intended devices. This can proceed without a recomp first frame when it does not contend with K1.
5. **Reduce experiment size and interpretation latency.** The tools built since the last review are useful. The next gain comes from using them to answer one causal question per run and promptly changing the hypothesis when evidence contradicts it.

## What has actually advanced

The first-frame effort has made real progress. It has crossed failures in CD callback delivery, callback stacks, MMIO address generation, missing function entries, semaphore semantics, SIF initialization, and scratchpad DMA. The earlier game-specific callback shim has been replaced by proper function-map splitting. The reference now demonstrably reaches the game. Build iteration and park observability have improved substantially.

| Area | Supported progress | Limit on the conclusion |
| --- | --- | --- |
| PS2 runtime | Successive boot parks cleared; later boots execute a stable main loop with heavy GIF/GS activity. | No reviewed artifact establishes a recognizable recomp-rendered SSX screen. Clearing the six K1 drops is not yet demonstrated to unblock that screen. |
| Reference | R1 gets through BIOS setup and reaches SSX in both PCSX2 EE modes. | PCSX2 is a software reference, not a physical-hardware observation. Earlier BIOS epochs cannot serve as SSX traces. |
| Iteration | T12/T14 show approximately 315 s → 5.9 s for the relevant runtime-only incremental build after disabling development ThinLTO. | A shared-header rebuild still took 640.9 s. Do not quote 5.9 s as the cost of arbitrary changes. |
| Observability | Park snapshots, syscall attribution/alignment, entry discovery, and watchpoints exist and have been exercised. | Watchpoint coverage, trace epoch, suppression settings, and retained state must accompany each interpretation. |
| GS harness | G6 and the separate ps2xGS tree provide 102 synthetic captures, CPU regression checks, and useful sensitivity tests. | There is no implemented GPU backend in the reviewed tree. Its “strict” backend is not an independent correctness oracle. |
| Other work | The GameCube, iOS/iPad, input, and device lanes have produced independent results. | Their completion counts do not measure PS2 first-frame progress. Keep their resource use subordinate to this priority. |

Evidence: [P1](../../local/research/P1/REPORT.md), [T12](../../local/research/T12/REPORT.md), [T14](../../local/research/T14/REPORT.md), [T22](../../local/research/T22/REPORT.md), [T26](../../local/research/T26/REPORT.md), [R1](../../local/research/R1/REPORT.md), [G6](../../local/research/G6/REPORT.md), and the fork sources named below. These are results of earlier workers, not experiments repeated for this review.

## K1: the raw payload changes the proposed fix

### The failure is before the built-in handler

At reviewed fork revision `6359fb625e5651b53c696aadb6bc44ece88cb560`, `Syscalls/Dispatcher.cpp` checks `dispatchSyscallOverride` before dispatching the built-in syscall. `Kernel/Syscalls/System.cpp:422` handles that override; the missing-target failure is around line 443. All six observed failures are syscall `0x5B` routed to the copied target `0x80075000`.

Changing only built-in `GetEntryAddress` around line 1006 cannot fix that path. The source payload is at ELF `0x4561C0`, copied for `0x330` bytes. Current dense function lookup also does not automatically make code outside the generated text range executable. Registering an address, translating the code at it, and respecting its load address are separate requirements.

### New direct evidence: the six results are not six original handlers

I read the existing ELF's payload instructions and words directly, without modifying or exporting the binary. Its entry searches six pairs at destination `0x80075300` and returns the matched pair's value; an unmatched key returns zero. The pairs are stored in the ELF at `0x4564C0`:

| Lookup key | Payload result | Meaning supported by payload layout and SDK source |
| --- | --- | --- |
| `0x55` | `0x80075038` | PutTLBEntry helper in copied code |
| `0x56` | `0x800750C8` | SetTLBEntry helper in copied code |
| `0x57` | `0x80075108` | GetTLBEntry helper in copied code |
| `0x58` | `0x80075158` | ProbeTLBEntry helper in copied code |
| `0x59` | `0x800751A8` | ExpandScratchPad helper in copied code |
| `0x03` | `0x80075330` | Data address immediately after the copied payload; assigned to `_kExecArg` by the corresponding SDK initializer |

The local ps2sdk `ee/kernel/src/tlbfunc.c`, revision `d317f8f0a2a413db38c5ef2b46ba927996983e0a`, corroborates the initializer, syscall numbers, helper roles, and final `_kExecArg` assignment. It is supporting evidence for semantics, not proof that all SDK versions are byte-identical to this game. [Pinned SDK source](https://github.com/ps2dev/ps2sdk/blob/d317f8f0a2a413db38c5ef2b46ba927996983e0a/ee/kernel/src/tlbfunc.c).

This supersedes the blanket “original-handler chaining” requirement in the current K1 brief and my first steering message. Chaining is relevant where a particular patch actually does it; this lookup must return its payload-specific code **and data** values. A0's inherited event-flag names for `0x54–0x59` are misleading for this installed TLB path. Syscall numbers require the active table and executable epoch to interpret them.

Recommended K1 acceptance:

- Execute the copied lookup correctly, or use an equivalent implementation guarded by verified payload identity and load layout. Preserve the data result and its subsequent reads/writes; do not manufacture a syscall-3 executable address for it.
- Cover reached copied helper entries and the required original-text entries, including the scanner. If an entry remains intentionally dormant, say so. Do not turn this into an unbounded kernel rewrite.
- Retire the scanner's `ret0` only with evidence that its marker search converges and publishes the intended table base. A return value alone does not establish that side effect.
- Show the installed table, all six lookup returns, absence of `-1` poison handlers, and the first downstream use of the data result. Count semantic dispatch failures independently of whether their messages are silenced.
- Run the current relevant tests and report the actual baseline count, then one bounded boot with a captured framebuffer and before/after park signature. A second boot needs a new question or validation reason.

For a static recompiler, a load-address-aware generated overlay or a narrowly validated HLE equivalent is a better scoped proposal than introducing a general JIT. The TheTharin side-map candidate below supplies registration mechanics only; it does not solve translation or relocation.

**Do not promise K1 will produce the frame.** A0's census shows `0x54–0x59` themselves were not called in that run. Fixing the installer removes real bad state, but the causal connection to the later loop remains to be established. Evidence: [A0](../../local/research/A0/REPORT.md), [K1 brief](../../local/muse/prompts/K1.md).

### R1 fixes the reference, not the entire parity claim

R1's valid SSX window follows the game ELF entry at `0x100008`, after five ExecPS2 events. T4/T23's earlier `ExecPS2 #2` window was BIOS/settings activity. Matching RFU060/061 was not sufficient to identify the executable. R1's interpreter and recompiler agree on the game's patch-installation path; FlushCache logging differs.

The runtime's initial trace has eight SetSyscall, six GetEntryAddress, and one Copy, whereas R1's game trace has eighteen, twelve, and three respectively. **Do not treat that count difference alone as a runtime defect:** `InitAlarm@0x42C7C8` and `InitThread` are explicitly replaced by HLE, and the scanner is stubbed. The missing `0x42C758` alarm installer is therefore explained at the call-path level. Validate the replacement's alarm/timer/INTC contract instead of requiring identical internal events.

In particular, the reference's `SetSyscall(0x12C, …)` has a timer-3 interrupt meaning in Play!'s implementation; it is not just another ordinary syscall-table slot. Tag intentional HLE collapses in the alignment projection. Every reference comparison should name executable identity, entry epoch, mode, and PC before interpreting its first divergence. [R1](../../local/research/R1/REPORT.md), [Play! syscall implementation](https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/Source/ee/PS2OS.cpp).

## E3 disposition: audit now, order probe only if the park survives

**Answer to the hand-back: E3 remains conditional. Its next boot is parked behind K1.** A short read-only audit of host scratchpad and relevant buffer writers is useful immediately.

T26 is a strong negative result for its actual observation mechanism: the fixed block's watched guest writes were initialization-only, and watched flag rewrites did not change their values in the selected window. But its own coverage row states that host `memcpy`, DMA, and SIF blits bypass the guest WRITE-macro watcher. Therefore “neither SIF nor CD can write this state” and “immutable state” exceed what it establishes.

The source gives a concrete missing observation surface: `ps2_memory.cpp` around lines 1571–1625 transfers scratchpad data with `std::memcpy` in SPR_FROM and SPR_TO. This does **not** prove one of those transfers causes the park. It does make a host-only mutation or scratchpad reuse a live alternative to the current interpretation.

T26 G1 is the discriminating question: the trace implies one skipped record per invocation, while the retained/watched record state appears to contain four nonzero flags. A final snapshot and aggregate call counts cannot resolve what each load saw.

If K1 reaches the same park, the next E3 should record one complete invocation, expanding to at most one or two guest frames when needed:

| Record | Required information | What it distinguishes |
| --- | --- | --- |
| Guest flag read and branch | Monotonic event sequence, guest frame, thread, PC/RA, actual `s1`, record index, loaded halfword, branch outcome | Whether the apparent four records are the records read at that moment |
| Guest write | Same sequence domain, effective address, old/new value | A genuine within-frame guest mutation |
| SPR/DMA or relevant host write | Source/destination, size, sequence, small before/after watched slice | Mutations invisible to the existing macro watcher |
| Invocation boundaries | Entry/exit sequence and scratchpad/object identity | Reuse of the same address for a different object or iteration |

Do not force flag values as part of this observation. Reconcile the one-skip/four-nonzero discrepancy before choosing a SIF peer, CD fix, scheduler change, or game stimulus. If host writes are absent and the read-side records still contradict the counts, check probe attribution and branch-count assumptions next. [T26, especially coverage and G1](../../local/research/T26/REPORT.md).

## First frame: inspect the output already being produced

T26's retained snapshot reports 3,505,928 kicks, 3,477,164 drawing kicks, 402,432 GIF packets, and 532,262 DMA starts. Its boot log contains a successful upload at line 3701: `idx=0`, `tick=53`, display/source FBP 112, 512×448. Subsequent uploads follow.

In `ps2_runtime.cpp:379–455`, `UploadFrame` emits that diagnostic on the successful `copyLatchedHostPresentationFrame` path. The fallback magenta placeholder follows the failure path. This establishes that the GS produced a presentable buffer; it does not establish recognizable or correct game pixels. The zero `gs_writes` field in the same snapshot is therefore not evidence of zero graphics activity.

The cheapest useful next artifact is a small number of framebuffer images with their frame number, dimensions, display registers, source FBP, hash, and whether the fallback path was used. Save these on the next authorized K1 run, preferably at the first upload and at the settled park. Inspect the actual images. Nonuniform pixel counts help triage but are not a correctness verdict.

Call the first-frame milestone met when a recognizable SSX logo, title, menu, or scene is captured from the recomp path, with enough state to reproduce it. Record subsequent frame hashes for continuity; do not demand that a static logo animate. Identify any behavior-changing HLE/stimulus settings used. A rendered buffer and a verified game frame should be separate milestones.

This also loosens the GS dependency: current recomp traffic can already supply small captures, and R1's running PCSX2 instance can supply a real SSX GS dump before recomp boot is solved. No additional game asset download is needed.

## Prior art: targeted reuse is more valuable than another broad sweep

I revisited [P3](../../local/research/P3/REPORT.md), [P4](../../local/research/P4/REPORT.md), and [P5](../../local/research/P5/REPORT.md), checked selected raw implementation bodies and licenses, and compared their proposed uses with the current fork. This is a ranked second look, not an independent validation of every survey entry. No third-party code was copied into the project.

| Candidate and inspected source | Useful mechanism | Disposition and license |
| --- | --- | --- |
| TheTharin fork, `7f29bbd7a63f165e19450919a934f2a9133173d0`, `ps2_runtime.cpp` around 1055–1120 | A sparse registered-function map alongside the dense generated table, consulted by replace/has/lookup | Small immediate K1 candidate if an additional address space is needed. Verify aliases, reset, and fallback behavior. GPL-3.0 license file read; preserve notices and provenance. It cannot itself execute copied MIPS. |
| Play!, `83700b2c31e593bc94e845b4b31b797be84dda59`, `Source/ee/PS2OS.cpp` | Custom syscall routing, exception return, and the special `0x12C` timer interrupt installation | Strong semantic reference for HLE review. Its CPU executes guest-generated handlers, so its whole mechanism is not a direct static-recompiler patch. BSD-2-Clause; retain source and binary notices. [Code](https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/Source/ee/PS2OS.cpp), [license](https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/License.txt). |
| Play!, same pin, `Source/iop/Iop_SifCmd.cpp` | Rounded RPC payload transfer, invocation queues, callback completion, semaphore signaling, and serialized command delivery | Useful if E3 identifies a missing SIF transaction or completion. Capture the entire request → destination write → callback/IRQ → wake contract. Its interrupt approximation is explicitly not hardware truth. BSD-2-Clause. [Code](https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/Source/iop/Iop_SifCmd.cpp). |
| GTT DI/preemption fork, `c4d099bbbfe64bbf8c0d893bea3de82bd2673e69`, `EeScheduler.cpp:39–49,366–417` | Interrupt-enable and EXL/ERL gating of preemption | Inspect against a demonstrated switch inside a guest critical section. Do not transplant another scheduler speculatively. GPL-3.0 license file read. |
| PSPRecomp, `caca7595251410ae7887aa209ba56397a835d0e1`, `src/hle/hle.c:64–103`, `include/psprecomp/dispatch.h:44–80` | Small recent-event rings and dispatch-miss context; registration consistency checks | Good low-cost observability pattern. Adapt to typed return status: zero can be success, and unimplemented-return-zero must not become the runtime policy. MIT license file read. |
| N64Recomp, `ffb39cdad1da5de07eaaa48bd1db4a89a7986771`, `src/recompilation.cpp`, `src/analysis.cpp` | Explicit static targets and bounded jump-table analysis | T5 already covers a useful subset. Reopen when a specific new target or overlay escapes it. MIT license file read. |
| paraLLEl-GS, `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` | Existing compute GS, transfers, hazards, shaders, dump tooling | Highest-value new GPU candidate; bounded device/integration test below. Inspected source headers are LGPL-3.0-or-later; Granite has its own MIT license and dependency inventory. |
| ps2sdk, `d317f8f0a2a413db38c5ef2b46ba927996983e0a`, `tlbfunc.c`, `alarm.c` | Explains this game's kernel-patch ABI and the code/data distinction | Use as semantic evidence. These files specify AFL-2.0. Do not copy them into the GPL runtime under an assumed permissive-license equivalence. The FSF lists AFL as GPL-incompatible. [License](https://github.com/ps2dev/ps2sdk/blob/d317f8f0a2a413db38c5ef2b46ba927996983e0a/LICENSE), [FSF guidance](https://www.gnu.org/licenses/license-list.html.en#AcademicFreeLicense). |

One stale recommendation should be explicitly closed: P4 S10 suggests adding `return true` after `scheduler.invokeCurrent` to avoid falling through into a built-in syscall. In the current fork, `invokeCurrent` is declared `[[noreturn]]` (`ee_scheduler.h:314`, implementation around `EeScheduler.cpp:1745`). That specific proposed fix does not apply to this version. This is why rereading both sides of a suggested hunk matters.

The broad Xenon/Unleashed and N64 runtime material remains useful architecture background, but it is less directly connected to the current failure. P5's noncommercial or unlicensed candidates should not become verbatim snippet sources without an applicable grant. The root SSX repository's license does not relicense borrowed GPL runtime code. For an adopted hunk, record upstream URL, full revision, file/range, file-specific license, notice, local changes, and the behavior checked. Keep that receipt small.

## paraLLEl-GS: test adoption before writing another GS

This candidate was absent from the reviewed P3/P4/P5 shortlist. It offers a standalone Vulkan compute GS and GS dump replay tools. Its own documentation does not claim hardware bit-exact varying interpolation, so treat it as an independent implementation, not an infallible oracle. [Project](https://github.com/Arntzen-software/parallel-gs).

The pinned `GSInterface` accepts GIF transfers or register writes, exposes explicit VRAM map/read/write boundaries and FIFO readback, and produces scanout on vsync. These are useful integration seams. However, ps2xGS currently records decoded `GSPrimitiveBatch` work and per-primitive state, not the original GIF stream. An adapter is real work: arbitrary register re-emission can mishandle Q, XYZ/ADC, transfers, TEXFLUSH/CLUT effects, and SIGNAL/FINISH. Prefer interception at the existing GIF/register boundary with well-defined state ownership. [Interface source](https://github.com/Arntzen-software/parallel-gs/blob/3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd/gs/gs_interface.hpp#L251).

**Device compatibility is unresolved.** The actual initialization check at `gs_renderer.cpp:798–829` requires descriptor indexing, timeline semaphores, buffer device address, 8/16-bit storage access, shaderInt16, scalar block layout, arithmetic/shuffle/vote/ballot/basic subgroup operations, the implementation's subgroup-size-control predicate, and at least 32 KiB shared memory. The README's shorter feature list and a device's “Vulkan 1.1” label cannot establish support. Check the actual implementation on the Mac/MoltenVK path and Odin; report each failure instead of assuming portability. [Capability check](https://github.com/Arntzen-software/parallel-gs/blob/3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd/gs/gs_renderer.cpp#L798).

Recommended short adoption experiment: pin source and dependencies; initialize on each available target; replay one short SSX dump at native resolution and 1× sampling; capture an image, correctness differences, GPU time, and memory use. An unsupported feature or material integration obstacle is a useful result. Start on an available reference GPU if the target path fails, but report that distinction. Do not launch a porting program before this gate.

If whole-library adoption fails, these are specific source regions worth adapting, with file notices retained:

- `gs/page_tracker.hpp`: block masks and host read/write timelines for VRAM hazards. This is evidence that placing VRAM in one GPU buffer does not make coherence trivial. [Source](https://github.com/Arntzen-software/parallel-gs/blob/3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd/gs/page_tracker.hpp).
- `gs/shaders/ubershader.comp`: concrete AFAIL, PABE, DATE, clamp, dither, and masked-write behavior. Extract only a needed semantic slice with a matching test. [Source](https://github.com/Arntzen-software/parallel-gs/blob/3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd/gs/shaders/ubershader.comp).
- `dump/gs_dump_parser.cpp` and replayer tools: version-aware GS state, VRAM, GIF, and vsync replay. Verify the producer's dump version against the pinned parser; do not infer compatibility from an older README version number. [Parser](https://github.com/Arntzen-software/parallel-gs/blob/3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd/dump/gs_dump_parser.cpp).

No upstream submission, Discord request, or maintainer outreach is recommended or needed for this work, consistent with the standing user decision.

## Tighten the GS plan's evidence gates

The [GS GPU plan](../plan-gs-gpu-backend-2026-09-18.md) is a useful scaffold, but three assumptions need refinement before implementation:

**CPU agreement is regression evidence.** It is not automatically PS2 correctness. The current `harness/strict_backend.cpp` explicitly halves RGB as an AA1 coverage marker, uses a fixed mip selection for its synthetic setup, and approximates other features. Keep those valuable sensitivity checks, labeled accordingly. Use three complementary references: existing CPU output for regressions; small register/transfer cases with independently derived expected results; and real SSX dumps compared with independent renderers. Use exact comparisons where justified and document the tolerance for raster differences.

**Rare operations can be essential.** A low-frequency clear, synchronization, transfer, or readback can determine every later pixel. Do not omit a feature solely because a census gives it less than 0.1% frequency. Rank by dependency and semantic effect as well as frequency.

**Measure a real workload early.** G6's approximately 0.35–0.48 ms synthetic 64×64 Present measurements do not establish a 512×448 SSX frame budget or include the entire GS pipeline. Run an early native-resolution viability check before building every feature. Later, measure guest submission, synchronization, GPU work, scanout, and steady-state presentation separately from diagnostic readback. Preserve correctness gates while avoiding a large investment in a backend that cannot meet target throughput.

## Tooling and orchestration that would shorten the path

I read the old Muse orchestrator's session history and the new live session, selected decision/tool context, the current hand-back, and the project orchestration memory. The recurring cost is delayed or mistaken interpretation between otherwise competent execution tasks. Examples already documented include the missing callback-entry investigation, incorrect watch-address arithmetic, and the BIOS/game epoch confusion. The new raw TLB lookup is another instance where inspecting a small source region changes a large brief.

The standing authority to continue and launch follow-ups is already present. Preserve it. Do not recreate a user-confirmation loop for routine next steps. Preserve the single live orchestrator as well; resolve identity from the live pane/process/session, not an old session title. One session previously named as the new orchestrator was actually the R1 worker.

| Improvement | Concrete shape | Priority |
| --- | --- | --- |
| Interpretation checkpoint | After a behavior change, three unchanged parks, or before a new semantic workaround: reconcile the claim with raw source and choose the next discriminating experiment. Require a worker to challenge a contradicted premise and recommend a next action alongside tables. | Now |
| Small experiment contract | State hypothesis, observable signal, alternatives, stop condition, and how each outcome changes the next action. Distinguish “investigation completed” from “milestone advanced.” | Every new brief |
| Existing trace tools, richer context | Extend T1/T22/`tools/trace_align.py` outputs as needed with event sequence, executable epoch, frame, thread, caller, return, and explicit HLE projection. For callbacks, retain registration → enqueue → target lookup → invocation → completion/wakeup. | Next diagnostic change |
| Semantic failure counters | Increment independently of log silencing and attach a small recent-event ring. The current drop census can be affected by `PS2X_DROP_SILENCE`; zero visible drops is not sufficient. | With K1 diagnostics |
| Entry/config validation | Validate callback targets and actually used TOML selectors before a long run. P13 identifies four unmatched selectors; inspect the boot-relevant ones first. Keep CSV, TOML, generator, runtime, and binary identity in one manifest. | Low-cost preventive work |
| Controlled contention | One mutator/runner for the shared PS2 runtime/build output. Reference capture and a bounded GS capability study can work independently. T27/OD1 and other authorized lanes should not delay that critical path through shared CPU, disk, or device use. | Now |
| Completion delivery | Prefer worker-completion notifications plus an hourly watchdog. Record live owner, process/session, start, and expiry in an atomically claimed build/run lease; avoid overlapping edits and stale file-only ownership. | Small orchestration improvement |

Do not reopen the closed GameCube M16–M63 residual investigation or commission another broad survey merely to occupy workers. Do not duplicate the park snapshot, trace aligner, function-entry discovery, or incremental build work that already landed. Track time to the next discriminating observation and validated behavior; commit totals and table counts are secondary.

## Disk and logging: immediate savings without deleting anything

At the final filesystem check, the internal data volume had about **20 GiB free**, and the external SSD about **495 GiB free**. This review kept remote source reads in memory and streamed history/log selections. The only authored artifact is this document.

T26 retained 705,357,230 bytes of boot log, 46,963,370 bytes of syscall trace, and 1,394,136,084 bytes of function log: **2,146,456,684 bytes for roughly four minutes**, before any additional duplicate retained copy. At that rate, repeated runs generate roughly 32 GB/hour. There is little value in collecting another full run once its signature has stabilized.

The development cache has `PS2X_ENABLE_AGRESSIVE_LOGS=ON`; `ps2_log.h` writes and flushes function entry/exit records. The existing general runtime ring does not bound that separate function file. Prefer counters and a bounded recent-event ring, with a short armed window or dump-on-trigger. Give runs a byte cap as well as wall/progress caps. Retain one baseline, the latest useful failure, and the fix evidence; compress closed raw logs and reference a single canonical copy. Do not repeatedly hash multi-gigabyte artifacts at every poll when a creation-time hash and immutable receipt suffice.

No deletion is proposed as an action in this review. For subsequent storage work, inventory redundant artifacts and active readers first. Keep large assets and old traces off the nearly full internal volume. The external ExFAT volume's large allocation units and lack of ordinary symlink support also make it a poor location for huge generated build trees. A quota-limited APFS build area or reuse of an existing remote build cache is worth evaluating separately; it is not a reason to format the SSD or create another complete checkout now.

## Recommended next hand-back

The next useful report should answer five questions in order:

1. Does K1 now return the five actual copied-code addresses and the data address, and what consumes them?
2. What do the first uploaded and parked framebuffers visibly contain?
3. Did the park change? If it did not, which actual flag values did the loop read, with what intervening host/guest writes?
4. Can the pinned paraLLEl-GS initialize and replay the selected SSX dump on each tested target, and what blocks the others?
5. What is the one next behavior change justified by that evidence?

That is sufficient to steer the next batch. More long-running censuses or broad candidate rankings should need a specific unanswered question.

## Evidence boundaries and reproducibility

The SSX tree was initially reviewed at `963f081` and advanced through the user's `f88ec08` hand-back to `a1a4b731d33a8c64680f5acefa84bc2c0a069e74` while other agents worked. The runtime source snapshot was `6359fb625e5651b53c696aadb6bc44ece88cb560`; ps2xGS was `14a1974bf33895c5ad325d77508cddead0af8ace`. K1 was active, not completed, during this review. Line numbers refer to the inspected versions and can move.

Local source/evidence roots:

- Runtime: `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`; ELF, generated output, and run artifacts under the sibling `P1/` directory. Relevant retained artifacts: `run/boot-t26-1.log`, `run/syscalls-t26-on.txt`, `run/ps2_log-t26-1.txt`, `run/park-t26-1/park-snapshot.json`.
- Existing prior-art checkouts: `/Volumes/Extreme SSD/fork-survey/` and `/Volumes/Extreme SSD/q3-siblings/`. SDK corroboration: `/private/tmp/ps2sdk-ref` at the pin given above. GS harness: `/Users/bradrichardson/dev/ps2xGS`.
- Muse history: old orchestrator session `01a0b709-c19a-7c40-af9e-89c57d2cddeb` from September 18; live orchestrator `01a0c0b2-eeba-7531-85d7-44eb560436d6` from September 20; R1 worker `01a0c05d-6bd7-7390-8237-20cfb8a324e7`. Session JSONL files were read in place, with chronological user/decision messages and relevant tool context selected. This was not a claim to have read every repeated log line in the approximately 109 MB old session.
- Live delivery target: Herdr `wN:p3`, verified as the active Muse orchestrator. Raw-payload and E3 corrections were sent during the review; the terminal history confirms the K1 refinement was relayed and incorporated into its brief. The document's absolute path and final steering were also delivered successfully through Herdr on completion.

The source and license review supports the specific candidates above; it does not certify every transitive dependency or distribution configuration. No performance, target-driver compatibility, first-frame, or K1 success result is claimed without a corresponding experiment. No implementation code or proprietary source excerpts are included in this document.
