# RV7 — emulator techniques for the SSX 3 static runtime

2026-09-26, Codex. Research and recommendations for the orchestrator; no adoption verdict.
Read-only source/web survey: no builds, boots, benchmarks, source edits, or upstream contact.
Only this report is changed. Evidence retrieved across the September 25–26 UTC boundary.

## 1. What changes the plan

**The best transfers remove host work while preserving guest behavior:** register residency
across generated blocks, architecture-appropriate flag packing, exact memory specialization,
and fewer GS handoffs/submissions at dependency-safe boundaries. Most are refinements of
RV4's priorities, not an alternative route around the present VU cost. The most useful new
source is **ARMSX2's inspectable ARM64 core**, including work merged from yaps2. Its source
also exposes correctness tests and hardware-model work worth comparing independently.
[AR], [AF], [AM], [YP]

**Do not import emulator speed settings as our performance solution.** EE underclocking,
cycle stealing, instant VU1, lower clamping, disabled readbacks, and SSX frame-skip patches
can change guest timing, state, or pixels. They may help an emulator's FPS display while
failing our exactness requirement. MTVU is a different category—parallel execution with
ordering obligations—but remains parked by Brad. No inspected patch proves true SSX 3
120 Hz simulation at normal wall-clock speed. [PC], [PA], [PV], [PD], [S1], [S2]

**The strongest game-specific leads are concrete:** NTSC-U Metro patch sites `0x00230704`
and `0x00230710`; two-player patch site `0x00317184`; aspect scalars `0x00622600/604`.
The Metro sites are **a branch and a store**, not two branches. The two-player change
increments a loop counter by two; that is not a recovered timestep control. The default
16:9 route should remain the approved in-game anamorphic mode plus aspect-preserving output.
(§4; [X3]; repository AGENTS.md)

### Performance basis and limits

- [RV4](review-2026-09-26-astra-perf.md) is the sizing source. Its N12 **68.31 ms/frame**
  normalization produces **model-ms**, not separately measured CPU milliseconds. VU0's
  approximately **5.5 model-ms** overlaps the mixed VU bucket; it cannot be added again.
- The [ledger](../numbers-ledger.md) records clean Odin F5 1× races at **0.245×/0.244×**
  (14.67/14.60 guest vsyncs/s), APK `4ff81032…`, runtime `a3efbfe`, sound on. The Mac VR2
  stage-1 **1.095×** gain is a Mac result; this report assigns it no measured Odin gain.
- RV4 corrects GT libc/kernel to **7.34 model-ms**, rather than the all-thread 10.81 value.
  VK1's early 1× frame contains **54.6 ms GT CPU + 20.9 ms off-CPU**; that window is not
  interchangeable with N12's race normalization. VK1 Part 2A identifies `flush_submit`
  as the unresolved span and rejects frame-context starvation as the main explanation.
- Therefore the ranking below uses conditional RV4 envelopes or qualitative benefit.
  No new speed number is established, and upper bounds must not be summed. The approximately
  **16.7 ms / 8.3 ms** 60/120 budgets remain targets, not outcomes of this survey.

Prior VU work is already substantial: [VR1](../../local/research/VR1/REPORT.md) compiled
all observed VU1 images on its gate route, [VB1](../../local/research/VB1/REPORT.md) removed
safe commit overhead, and [VR2](../../local/research/VR2/REPORT.md) tightened generated
pairs. [Q1](../../local/research/Q1/REPORT.md) already covers microVU pipeline-state keys,
hazards and flag liveness; this report does not repeat that analysis. Retain RV4's block
entry/exit, pending-write, budget-cut and ordered-GIF obligations.

## 2. PCSX2: what each speed technique actually buys

Source baseline **P = `ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89`**, September 26 UTC.
Current inspected files carry GPL-3.0+ notices; the older Aether announcement's LGPL
explanation describes a historical licensing arrangement, not permission to copy P. [PL], [AE]

| Technique | Mechanism and trade-off | Transfer to our runtime |
| --- | --- | --- |
| **MTVU** | Moves VU1 execution/unpacking into a worker protocol; `MTVU.cpp` communicates completion/cycles and PATH1 work, while `VU1micro.cpp` synchronizes at required boundaries. PCSX2 explicitly warns of incompatible games/hangs. It does not eliminate VU instructions. [PM], [PV], [PC] | **Park.** Our exact GIF ordering, VIF writes, VU memory visibility and EE dependencies need an explicit ownership model before a split. Existing GS threading does not prove VU1 can overlap safely. |
| **EE cycle rate** | `scaleblockcycles_calculation()` changes guest cycles charged per compiled block, with special handling for short blocks. Underclocking reduces guest EE work available per virtual video interval; overclocking permits more work and can prevent a game's internal slowdown, at higher host cost. [PE], [PC] | **Park as a speed lever.** Neither is faster execution of an unchanged machine. An overclock may support a game patch later, but does not supply a 120 Hz timestep. |
| **EE cycle skip** | PCSX2 exposes skipped EE cycles as a separate speedhack and warns it helps only a small subset of games and is often harmful. This is not equivalent to changing the display refresh or optimizing an instruction. [PC] | **Park.** Guest scheduling changes are incompatible with unchanged det-hash acceptance. The detailed current skip insertion path was not traced in this survey; no formula or precise skip percentage is claimed. |
| **INTC polling shortcut** | On an INTC_STAT read, `IntCHackCheck()` advances `cpuRegs.cycle` to the next event if it is ahead and more than eight cycles have elapsed since the last event; PS1 mode bypasses it. This is a targeted heuristic, not a proof that arbitrary polling bodies are empty. [PI] | **Queue only after finding hot polling.** A static loop proof can be stronger: skip repetitions only until the earliest producer event, preserving final registers, timer reads and ordering. Never treat every MMIO read as a wait. |
| **Wait-loop detection / vsync waits** | The EE recompiler's recognized loop path advances to the next event; a separate timeout-loop routine accounts for a loop register. Detection is distinct from the host frame limiter. [PE] | **Queue.** Recognize side-effect-free loops, or use a known HLE wait contract. Vsync is only one possible wake event; DMA/VIF/IOP/timers can wake sooner. Our HLE scheduler already has `waitVSync`, so prove additional work remains first. [R] |
| **Instant VU1** | Runs VU1 with altered EE/VU completion scheduling; the VU still executes. `vu1Finish()` and VIF completion paths distinguish instant and threaded behavior. PCSX2 warns of graphical errors in some games. [PV], [PV2], [PA] | **Park.** Not synonymous with statically compiled VU1. Preserve guest completion timing while optimizing the work inside the existing schedule. |
| **Fast CDVD** | Current CDVD code halves qualifying sector/read delays, excluding long seeks. Disc precaching instead moves host I/O earlier and uses RAM. [PD], [PC] | **Park timing shortcut; queue host caching if measured.** HLE streaming/callback timing is already game-sensitive. Faster host reads may preserve scheduled completion; earlier guest completion does not. No race-frame saving credited. |
| **VU clamping: None / Normal / Extra / Extra + Preserve Sign** | Modes progressively select overflow handling, extra operand/result clamping, and sign-aware handling. `microVU_Clamp.inl` contains mode-dependent paths and explicitly pragmatic NaN treatment; these are compatibility/performance choices, not a complete exact PS2 arithmetic specification. [PA], [PF] | **Park lowering accuracy. Queue exact specialization.** Prove an operand range or retain a slow fallback; preserve PS2 exponent range, underflow, signed zero, sticky flags and MADD behavior. Host `fast-math` or fused multiply-add is not justified by a visually correct race. |
| **Bounded GS queue / frame latency** | PCSX2 allows frames to queue; its optimal-pacing option waits for GS completion before input/next frame, reducing latency at throughput cost. [PC] | **Queue measurement within the existing GS thread.** Bound memory/latency and synchronize only for real consumers. Increasing queue depth cannot repair a slow submit path; RV4 already rejects that simple explanation. |

A safe fast-forward must preserve **observable state**, not necessarily every discarded
iteration. For a loop that increments a counter or reads a clock, reproducing only its exit
condition is insufficient. Our det-hash is a required regression gate, but a finite race
trace also needs small tests for early interrupts, timeout exhaustion and producer ordering.
An emulator default being broadly compatible does not establish exactness for our runtime.

## 3. GS: learn the dependency model, not a list of toggles

PCSX2's hardware renderer and paraLLEl-GS have different representations. PCSX2 translates
GS work into host raster draws and maintains host textures/render targets; paraLLEl uses
compute rasterization with explicit emulated-memory tracking. Ideas about avoiding work
transfer; copying a hardware-renderer fast path into paraLLEl need not. [PT], [PH], [G]

| Technique observed | What matters for us |
| --- | --- |
| **Texture source / render-target reuse** | `GSTextureCache::LookupSource()` can source texture data from already resident targets; `InvalidateVideoMem()` and `InvalidateLocalMem()` maintain the two directions of coherence. Base address alone is insufficient: formats, pitch, dimensions, channels, dirty regions and aliasing matter. Avoid GPU→CPU→GPU round trips when equivalent GPU data is already available. [PT] |
| **CLUT caching** | PCSX2 caches palette objects and recognizes GPU palette sources. A texture's pixels can remain unchanged while its effective palette changes. Key/invalidate the palette interpretation as well as the pixel storage; do not equate a texture-address hit with unchanged content. [PT] |
| **Batch primitives until an observable dependency** | `GSState::FlushPrim()` submits accumulated primitives; autoflush detects texture/framebuffer feedback and page boundaries. Some rules explicitly use assumptions about primitive overlap. Preserve primitive order for blending, destination alpha and self-texturing. Fewer host calls are useful only when the dependency analysis remains valid. [PG] |
| **Avoid copies/barriers with appropriate feedback facilities** | Vulkan framebuffer fetch/rasterization-order attachment access can reduce copies in a raster renderer. PCSX2 chooses between barriers, copies and blending paths. These extension paths are not a drop-in accelerator for paraLLEl's compute shaders. [PH], [PK] |
| **Read only needed regions, and only when needed** | PCSX2's texture-cache read paths download regions and flush when required. A correct deferred readback makes results available before the guest consumer; disabling readbacks omits required results. Nether's recommendation to disable them is a compatibility trade-off, not an exact optimization. [PT], [NE] |
| **Game-specific renderer rules** | SSX 3's current GameDB asks for blending level 4, texture-inside-RT handling, half-pixel offset 2 and native-scaling handling. Comments identify lighting/snow, pause-menu rainbow effects, depth lines and post-processing. Treat these as test-scene clues; their numeric settings describe PCSX2's renderer, not paraLLEl configuration. [GD] |

**Already implemented here:** local paraLLEl at `963cb57503245e31efb2df89a4740cd4da66513b`
has page/block/write-mask texture invalidation, CLUT-instance tracking, and host-read timeline
tracking in `gs/page_tracker.cpp`; texture-related and copy hazards can end a render pass.
Thus “add texture caching,” “keep VRAM on GPU,” and “batch draws” are not new proposals.
The actionable question is **which existing cache invalidation, flush, queue handoff or
host wait is unnecessary on the observed SSX stream**. [G]; RV4 §3

Iris provides an unusually close integration comparison: its release notes describe batching
GS transfers to reduce repeated render-mutex locking after adopting paraLLEl-GS. That is
an idea to audit in our bridge, not a measured SSX gain and not evidence that our mutex is
hot. Its pinned source tree includes `src/gs/renderer/hardware.cpp`. [IR], [IRREL]

For Odin, collect submit count/size/reason, cache misses/invalidation cause, bytes read back,
and the blocked consumer in the **same guest window**. Distinguish logical GS flushes from
Vulkan queue submissions. Merge adjacent compatible queue work without moving SIGNAL,
FINISH, readback, VBlank or cross-path visibility. Use existing replay/hash tools plus the
relevant GS output gate; CPU det-hash alone cannot certify a GPU-only batching change.

## 4. SSX 3 patches: verified bytes, narrower meanings

The maintained PCSX2 NTSC-U file is `patches/SLUS-20772_08FFF00D.pnach` at
**`9f82a4d2b8a2aaf83807421f18d5d30263ea826c`**. The broader SSXModding file of the same
name, under `PS2/SSX 3/`, is pinned at **`30264a35af494c892a1cafee4602029d6577f357`**.
The former includes Metro and aspect variants; the latter also includes two-player 60 FPS.
These are different collections, not contradictory accounts of one file. [S1], [S2]

| Patch / provenance | Exact guest changes | Established meaning and limit |
| --- | --- | --- |
| **Fix Metro Slowdown**, Meridian, both collections | Startup word writes: `0x00230704 = 0x00000000`; `0x00230710 = 0x00000000`. | Author calls it disabling performance frame skip. Local X3 correction identifies `bc1t` after `c.lt.s` at the first site and a store to `[*(gp+0x2A74)+0x34]` at the second. NOPs suppress that conditional flag-update sequence. This is not elimination of host emulation cost and may increase rendering work. [S1], [S2], [X3] |
| **60 FPS 2 Players**, Gabominated, SSXModding | Startup word `0x00317184 = 0x26310002`. | Changes `addiu s1,s1,1` to increment by 2 in the delay slot of the call at `0x00317180` to `cAppMan_checkHalt`. X3 finds the loop bound at `[s0+0x20]` and backedge at `0x00317190`. It reduces passes needed to reach a fixed bound; the author warns EE overclock may be needed. Not proof of doubled physics, nor unrestricted FPS. [S2], [X3] |
| **16:9 / cutscene recipe**, forum attribution to sergx12 | Repeated extended writes `20622600→3F400000`, `20622604→3F800000`; conditional `E0023F40,006225FE`, then `20622600→3F100000`, `20622604→3F400000`. | Direct-write guest addresses are `0x00622600/604`; values are 0.75/1.0, conditionally 0.5625/0.75. The E-code is a conditional over the following two writes, not a write to address `0xE0023F40`. The post reports an unresolved cutscene squeeze transition. Do not promote it over approved native anamorphic mode. [SW], [FMT] |
| **Wide/multi-monitor variants**, Virjoinga, PCSX2 collection | Repeated `0x00622600` writes: 32:9 `3EC00000`; 3840×1600 `3F0E38E4`; 3440×1440 `3F0EE23C`; 2560×1080 `3F100000`. All set `0x00622604 = 3F800000`. Triple-display sections additionally use `3E800000`, `3E888889`, `3E8E38E4`, `3EAAAAAB`, `3EB60B61`. | The file labels horizontal/vertical aspect scalars. These sections request host `Stretch`; that directive must **not** override Brad's aspect-preserving output requirement. They are optional aspect modifications, not a reason to change the default. [S1] |
| **Disable intro videos**, Meridian | NTSC-U startup words `0x001A2840`, `0x001A2864`, `0x001A28DC` each become `0000202D` (zeroing a0). | A separate guest modification; retain the already-approved dev-only movie bypass and fix faithful playback separately. This survey does not apply the patch. [S1], [S2] |
| **PAL Metro variant**, SSX modding wiki | PAL 1.0 CRC `CE942B2A`: `0x002306F4` and `0x00230700` become zero. | Useful relocation warning; not interchangeable with NTSC-U. The real PAL serial in current GameDB is `SLES-51697`; `SLES-51973` is War Chess, not SSX 3. No PAL binary disassembly was checked. [SP], [GD] |
| **“No Speed Cap”**, SSXModding | The section writes `4B18967F` to data locations including `0x0049B720`, `0x0049B724`, `0x0049B870`, `0x0049BE34`, `0x0049BF18`. | A title containing “speed” is not FPS evidence. The inspected section supplies no verified frame scheduler/timestep interpretation. Do not advertise it as an FPS unlock. [S2] |

**Encoding matters.** For the shown extended `2xxxxxxx` writes, the leading 2 denotes a
32-bit direct-write operation, not an EE address bit. `patch=0` is startup application;
`patch=1` is repeated application at the emulator's patch cadence. Our static executable
will not start executing new C++ merely because a pnach writes new instruction bytes into
RAM: code patches need regeneration or an explicit address override/invalidation route.
Data patches may still work through memory. Match serial, CRC, ELF hash and original words
before choosing a route; preserve MIPS delay-slot semantics. [FMT], [R], [S1], [S2]

**120 Hz consequence:** start with these addresses as investigation anchors, not a ready
patch. Count simulation updates, game renders, guest video events and host presents
separately; record timestep and game-time progression. Disabling half-rate rendering can
restore visual updates without doubling simulation. Raising guest refresh can accelerate
timers, audio/input or gameplay unless the game-time contract is corrected. No verified
normal-speed PS2 SSX 3 120 Hz/unrestricted-FPS patch was found in the inspected collections
and targeted searches. SSX **On Tour** 60 FPS results are a different game's code.

The [X3 orchestrator correction](../../local/research/X3/ORCH-CORRECTIONS.md) is the local
semantic authority used above. Its companion raw report contains a missed delay-slot
relationship and an imprecise comparison summary; this report does not rely on those.
No new game disassembly, patch application or timing experiment was performed.

## 5. AetherSX2 / NetherSX2 and the inspectable ARM alternative

**Aether lineage is established; detailed optimizer provenance is not.** PCSX2's own
2021 announcement confirms the relationship and credits Tahlreth's performance work.
It is not a published explanation of the register allocator, fastmem layout or VU emitter.
NetherSX2-patch's current README describes maintenance over Aether **4248**, with Classic
using **3668**, game database/patch/controller updates and APK changes. Its patcher is not
an independently inspectable replacement ARM JIT. [AE], [NE]

| Requested ARM topic | Aether / Nether: evidence boundary | Source-backed lesson from current ARMSX2 |
| --- | --- | --- |
| **Register allocation** | No pinned allocator source or primary design description recovered; do not invent an Aether advantage such as global SSA allocation. | `iCore-arm64.cpp` has GPR/NEON allocation, dirty writeback and ABI-reserved registers; it explicitly reserves x19 for fastmem. Retaining guest values across instructions and minimizing helper-call spills transfers to generated C++ locals, subject to exits and aliasing. [AR] |
| **Fastmem** | Do not attribute a particular fault/backpatch scheme to Aether from its speed alone. | `recVTLB-arm64.cpp` documents and implements a 4 GB guest-address window, direct LDR/STR, fault-driven slow-path backpatches and a software VTLB fallback. Slow thunks preserve live register masks, including non-allocator constants. For us, guarded direct-memory specialization is the easier transfer; mutable JIT code/backpatching is not required. [AM] |
| **VU recompiler** | ARM64 JIT is the baseline specified by the brief; its exact Aether algorithms were not verified here. | ARMSX2 exposes EE, IOP, VU0 and VU1 emitters. `AsmHelpers.h` packs lane predicates with constant weights, incorporating lane order and destination mask; it avoids mechanically reproducing x86 shuffle/movemask work. Transfer the representation idea, not GPL emitter code. [AR], [AF] |
| **Threading** | Nether documents threaded presentation for 3668 and recommends settings by GPU/core version. This does not establish Aether's internal thread-synchronization details. | An ARM core's ability to use MTVU does not make our VU1 ownership split free. Study queue/synchronization patterns while retaining Brad's park; avoid prescribing blanket affinity from unrelated devices. [NE], [PM] |
| **Vulkan / Adreno** | Nether recommends 4248 for stronger/Adreno devices and Vulkan with disabled readbacks. Those are project recommendations, not a controlled Odin SSX comparison. | ARMSX2 has explicit GPU/driver profiles and centralized framebuffer-fetch policy with tests. Select a fast path from actual capability/driver facts and retain a correct fallback; do not map Snapdragon marketing names directly to GPU behavior. Raster feedback features still do not directly accelerate compute GS. [NE], [AG] |

**The ARM flag opportunity is not “disable flags.”** Constant lane weights can combine sign,
zero and destination-mask packing and keep constants resident. Our sticky/underflow/overflow
semantics must survive exactly. ARMSX2's newer `VuFmacFlags-arm64.h` and upper emitter also
handle unusual VU arithmetic with mode-specific paths; the tree contains console-conformance,
flag-pack and cut/resume-style tests. Their presence makes this a useful research corpus,
not an independently verified correctness oracle. Reconcile against our current model and
hardware evidence before admitting any operand fast path. [AF], [AF2], [AT]; VR2 and RV4 §2

**Persisted JIT versus AOT:** ARMSX2 carries yaps2's microVU disk-cache machinery: serialized
code chunks/relocations and build-ABI/options/architecture versioning. We already ship compiled
VU images, so a JIT disk cache buys no steady-state execution speed by itself. The transferable
part is robust generated-artifact identity and coverage reporting for unknown images. Cold
shader/JIT startup, steady race throughput and code-size reduction are separate metrics. [AC], [AC2]

Licensing boundary: current PCSX2/ARMSX2/yaps2 sources inspected are GPL-3.0+; Nether's
patch repository is **Unlicense**, which does not relicense the underlying Aether binary.
The historical PCSX2 post discusses LGPL core arrangements; Nether Classic's FAQ states
noncommercial app terms. Treat these as separate layers, and do not infer permission to
copy Aether implementation code. No source code is copied by this survey. [PL], [AR], [YP], [NE], [AE], [NF]

## 6. Project map: activity, maturity, novelty, transfer

“Active” below means dated public development/release evidence, not verified compatibility.
Default-branch dates can differ from release dates and a fresh fork/push need not add code.
The sample is deliberately broader than Android, but it is not a census of every fork.

| Project and observed pin/activity | Maturity and license | Novelty and static-recompiler relevance |
| --- | --- | --- |
| **PCSX2**, P, September 26 | Established general emulator; GPL-3.0+ inspected core. | Primary reference for scheduling, VU and GS semantics. The inspected upstream ARM directory has VIF support/stubs, not ARMSX2's full ARM EE/VU emitter set; do not assume every PCSX2 binary is an equivalent native ARM baseline. [PL], [AR] |
| **Aether / Nether**, Nether `f5f89b3…`, September 22 | Established Android baseline over legacy 3668/4248 cores; patch layer maintained. App/core/patch licenses differ (§5). | Useful controlled comparison target; maintained GameDB and compatibility patches are transferable evidence. No new independent JIT technology established from the patch project. [NE], [AE] |
| **ARMSX2**, `247fa6f…`, September 25; releases include September nightlies | Actively changing native ARM64 emulator with games running; GPL-3.0+. No SSX/Odin benchmark performed here. | Best open ARM allocator/fastmem/VU reference; centralized driver policy, VU validation cases and persistent cache. Transfer selected techniques with our own gates, not an assumption of compatibility parity. [AR], [AM], [AF], [AG], [AC], [AT], [ARREL] |
| **yaps2**, `57ea93c…`, September 5 | README explicitly says discontinued and development merged into ARMSX2; GPL-3.0+. | Historical source for ARM handheld work, including persisted microVU cache; **not a second currently active independent core**. [YP] |
| **Play!**, `83700b2…`, September 3 | Maintained independent multi-platform emulator, including Android/iOS/web; two-clause BSD-style license text. Compatibility is title-specific. | Shared code-generation framework with an AArch64 backend; separate desktop/mobile Vulkan drawing implementations and HLE idle-event detection. Useful independent comparison for HLE scheduling and mobile renderer boundaries. Replacing our backend/JIT with it is not proposed. [PLAY], [PJ], [PMOB], [PIDLE] |
| **Iris**, `90dae6a…`, April 6 | Early emulator; README warns low/unplayable rates and identifies missing EE/VU JITs. MIT core; paraLLEl-GS dependency has its own license. | Independent paraLLEl integration, scheduling/software-fastmem/interpreter caching and transfer batching; useful GS bridge and correctness reference, not a faster Odin deliverable. [IR], [IRREL] |
| **DobieStation**, `68dd073…`, April 21, 2021 | Historical experimental emulator; no recent default-branch activity found in this check; GPL-3.0. | Secondary architectural reference; do not label it an active new Android competitor. No new adoption candidate established. [DOB] |
| **PS2Recomp upstream**, `75d729c…`, September 20 | Experimental GPL-3.0 framework; README acknowledges partial hardware and poor VU/GS performance. | Literal EE→C++, function-entry discovery, instruction patches and address overrides; newer `ps2xIOP` executes original IRX with HLE fallbacks. That could improve sound/IOP fidelity, but replacing current HLE may add work and is not an Odin performance shortcut. [UP] |
| **Our PS2Recomp fork** | Local inspected checkout `f949ff0`; newer report baselines are named in §1. GPL fork; static guest output remains private. | Already has VU AOT, exactness gates and paraLLEl integration beyond upstream's generic README. Evaluate other projects against this actual work, not upstream's earlier feature list. [R]; VR1–VR2 |
| **Other PS2Recomp derivatives** | SHO/GTA-VCS fork `659a2b0…` (August 5) is archived, GPL-3.0. RE Outbreak project `73ad3c9…` (April 10) reports main-loop/render/input bring-up; repository license was not declared in API metadata. | Game-specific maps/configs and hardware-bridge approaches, not proven universal optimizers. A sampled recent fork, `yagolasse/sm-recomp`, still resolves to upstream `75d729c…`; its fresh push is not a new implementation. Additional fork assessment was cut short by API rate limiting. [FORK1], [FORK2], [UP]; §8 |
| **ssxdecomp/ssx3**, `0b287a3…`, September 25 | Work-in-progress matching PS2 decomp; no repository license detected in metadata. NTSC-U target SHA-1 is documented. | Names, types and control-flow anchors can improve selective specialization and the 120 Hz investigation. Matching PS2 output is not a native port; verify labels against the exact binary and do not infer code-reuse permission. GameCube remains reserve. [SD] |
| **OpenGOAL**, `76e8eec…`, September 22 | ISC tools; Jak 1 polished, Jak 2 effectively complete/beta, Jak 3 ongoing per README. x86-64 target, no mobile plan stated. | Demonstrates semantic recovery plus a custom native compiler/runtime. GOAL-specific decompilation is not a generic R5900/VU optimizer and SSX is not established to use GOAL. Selective semantic replacement is a longer-term option, not a change of milestone. [OG] |
| **N64Recomp**, `ffb39cd…`, May 27 | MIT tool used with a separate runtime in released recomp projects. | Direct known calls, detected switch tables, loaded-section-aware overlay lookup, patch-function linking and RSP AOT. Transfer call/overlay metadata and isolated patch builds; do not import N64 timing or assume RSP and PS2 VU pipelines are equivalent. [N64] |
| **XenonRecomp**, `ddd128b…`, August 4, 2025 | MIT tool used by Unleashed Recompiled; game/ABI assumptions remain explicit. | ABI-justified local guest registers, removal of save/restore scaffolding, fast indirect lookup and patch hooks. Strong precedent for residency; weak precedent for blindly removing our RA/unwind/checkpoint machinery. Published gains are for another game/CPU, not Odin predictions. [XEN] |

The useful distinction between the last two approaches is **recompiled instructions versus
recovered contracts**. Native calls and locals let the host compiler optimize more, but are
safe only when all possible entries, callbacks, aliasing, unwinds and external observations
are represented. Our runtime's resumable interior entries make blanket ABI assumptions
particularly risky. Begin with a bounded hot region, not a whole-EE rewrite. [R], [XEN]; RV4 §1

## 7. Ranked transfers and suggested briefs

Savings are **conditional planning estimates**, not measurements; costs are rough focused
engineering effort, excluding queues/build turnaround. M = RV4 model-ms. “No conflict” means
no new thread split; it does not authorize implementation. Rows overlap substantially.

| Rank / tag | Candidate and Odin benefit | Cost / exactness risk | Park conflict / evidence |
| --- | --- | --- | --- |
| 1 **do now** | Gate in-flight VU1 blocks for actual register residency/coverage; **5–12 M** RV4 envelope beyond stage 1 | Existing lane, roughly 3–5 days total; high risk at pending writes, exits, helpers and budget cuts | No conflict. Q1/RV4 already cover pipeline analysis; ARMS/Xenon strengthen the residency lesson. [AR], [XEN] |
| 2 **do now** attribution; **queue** one fix | GS submit/transfer batching and deferred exact readback; **0–10 wall-ms** RV4 planning envelope at 1×, possibly zero | 0.5–1 day attribution; 2–5 days bounded fix; medium/high alias/order risk | No conflict inside current GS worker. Not permission for a new thread. [PT], [PG], [G], [IRREL] |
| 3 **do now** audit; **queue** experiment | Verify Android optimization and generated ARM code; **0–5 M combined compiler envelope** from RV4 | 0.5–1 day audit; builds later; low configuration risk, exact FP must remain | No conflict. O-level/ThinLTO/residency overlap; avoid double credit. RV4 §1; [AR], [AF] |
| 4 **queue** | VU0 AOT using the same exact model; **2–4 M** within overlapping ~5.5 M envelope | 2–4 days; unit-specific masks, entry state and context copies | No conflict; both PCSX2 and ARMS expose compiled VU0. [PA], [AR]; RV4 |
| 5 **queue** | ARM-native packing of live flags, constant residency and proven operand specialization; **small/unknown**, not an extra large VU bucket | 1–3 days for one mechanism; high arithmetic/flag risk | No conflict. After blocks settle; VR2 liveness alone was noise. [AF], [AT]; VR2 |
| 6 **queue** | Bounded EE direct-call/local-state/guard-hoisting work; **0.5–2 M** RV4 envelope | 1–3 days per hot region; medium/high resume/alias risk | No conflict. Our FAST RAM paths already exist; measure residual guarded calls first. RV4 §1; [N64], [XEN] |
| 7 **queue** evidence first | Proven idle-loop/event fast-forward; **unknown, likely small in VU-heavy racing**, potentially useful in loading/menu | 0.5–1 day hot-loop census, then one candidate; high if timer/side effects ignored | No conflict. No current hot-polling budget was identified. [PI], [PE], [PIDLE], [R] |
| 8 **do now** read-only audit; **queue** optional patch gate | CRC-specific SSX patch semantics and 16:9 regression scenes; **zero throughput credit** | 0.5 day evidence consolidation; guest patches intentionally alter state | No thread conflict; actual 120 Hz modification remains later. [S1], [S2], [SW], [X3] |
| 9 **queue** | Generated-artifact identity/coverage, hardware-referenced differential fixtures, driver fallback policy; **no immediate frame-time claim** | 1–3 days bounded harness work; low runtime risk | No conflict; use existing tools, do not build a second framework. [AC], [AT], [AG] |
| 10 **park** | VU1/EE/GS pipeline expansion; potential overlap, **no revised ms promise here** | At least weeks with dependency tests; high ordering risk | **Explicit Brad park.** Re-size only after serial work and submit attribution. [PM]; RV4 |
| 11 **park** | Cycle-rate/skip, instant VU1, weaker clamps, disabled downloads, blanket renderer swaps or wholesale decomp rewrite | Variable; changes timing/results or scope | Violates exact baseline or milestone focus; not credited toward 60/120 targets. §§2–6 |

**Brief A — do now, residency gate of the existing block lane.** Read its candidate and
Android assembly; report work-weighted fast-path coverage, entry rejection reasons and
loads/stores/spills across the hottest blocks. Hypothesis: blocks remove context traffic;
alternative: helpers/guards force the same traffic or hot loops miss. Do not start a rival
implementation. Within the lane's existing build budget, require pending-entry and every-cut
state/memory/cycle/GIF differential checks plus det-hash and the applicable GS gate; only
then use a diagnostics-off Odin control/candidate pair. Stop expansion if coverage or
residency fails. Expected artifact is an evidence table, not an automatic fold. RV4 §2

**Brief B — do now, one GS critical-path attribution.** Reuse VK1/N12 tooling on one pinned
route/window, 1×, sound/driver/APK fixed. One diagnostic build/run records submit/flush reason,
queue waits, batch sizes, cache/readback activity and thread running/blocked intervals.
Hypothesis: avoidable handoffs/submissions serialize the producer; alternatives: required
GPU dependency, shader compilation or driver work. Stop with attribution if the predicted
span is absent. Authorize at most one dependency-safe batching candidate only after that
read; require exact stream/output checks, then clean ABBA speed runs with device/thermal
rules. Do not credit the diagnostic run as speed or silently introduce another thread.

**Brief C — do now, Android code-generation audit.** Read actual EE/VU/runtime compile and
link commands, not only CMake intent. Check effective optimization, current-configuration IPO,
EE archive coverage and selected hot VU ARM assembly. Hypothesis: missing optimization or
avoidable context spills; alternative: already efficient code and runtime waits. One candidate
ThinLTO experiment may follow the audit within two builds, preserving FP and all other flags;
O3 and NEON flag packing are separate candidates. Stop on no configuration gap or excessive
compiler memory cost. Reuse RV4's exactness and clean speed gates; claim no independent
compiler gain that merely enables Brief A's savings. RV4 §1

**Brief D — do now, patch evidence consolidation.** Read only the pinned NTSC-U ELF/map and
X3 corrections; check original words, owners, both delay slots, the bound loaded near
`0x00317188`, and consumers of the Metro flag/aspect scalars. Reuse existing EE lookup data
without adding a second index. Deliver a table separating proven behavior, author claims
and unresolved timestep/render questions; no boot/build or patch application is necessary.
For later optional validation, define independent update/render/video/present counters and
normal-time checks, plus anamorphic gameplay/HUD/cutscene-transition scenes. Stop at the
unproven contract; do not turn a loop-counter patch into a 120 Hz claim or a new default.

## 8. Provenance, gaps and reproducibility

Local inputs: RV4, ledger, Q1, VR1/VB1/VR2, X3 report/corrections, the archived 120 Hz
handoff, and read-only runtime/paraLLEl source searches. ssx3 HEAD observed during research:
`9d0737330a93a058ab573feedd97e3258bac9d21`. Runtime inspected checkout: `f949ff0…`;
performance comparisons use their explicitly named report revisions, not that checkout.
Source pins below were resolved through GitHub repository/commit/tree APIs, then individual
raw files were read in memory. No checkout/download tree or external receipt was written.

Search coverage included PCSX2 speed settings/source, SSX 3 pnach/60 FPS/widescreen/120 Hz,
Aether/Nether, ARMSX2/yaps2, Play!, Iris/DobieStation, PS2Recomp and derivatives, matching
decomp, N64Recomp and XenonRecomp. Primary repositories, official documentation and patch
author/community-maintainer material support the findings. Search snippets and popularity
claims were not treated as benchmark evidence. No APK, ROM, or emulator was downloaded/run.

**Failure receipt / boundary:** the final extra-fork batch exited 1 with
`urllib.error.HTTPError: HTTP Error 403: rate limit exceeded` while querying GitHub's API,
after returning `yagolasse/sm-recomp` at the unchanged upstream SHA. Under
`~/dev/AGENTS.md`'s first-failure rule, further research stopped; no API retry or alternate
route was used. No substantive assessment is claimed for the other forks in that batch
(`noahbaxter/PS2Recomp`, Drakengard, .hack). Earlier guessed project URLs returning 404 were
recorded as not-found lookups, not evidence those projects do not exist. The survey is not
an exhaustive active-project census; Aether internals, a verified 120 Hz patch, actual Odin
benefits and current EE-cycle-skip insertion details remain unestablished.

The source links below identify exact files/revisions for code claims. Raw/API metadata was
used for activity/license identification; SPDX/file text takes precedence over GitHub's
license classifier. Patch collections and matching-decomp metadata did not establish a
reuse license. **Techniques only:** no GPL implementation is proposed for copying without
Brad's decision, and no public game-derived source is added to our forks.

[PC]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2-qt/Settings/EmulationSettingsWidget.cpp
[PA]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2-qt/Settings/AdvancedSettingsWidget.cpp
[PE]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/x86/ix86-32/iR5900.cpp
[PI]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/HwRead.cpp
[PM]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/MTVU.cpp
[PV]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/VU1micro.cpp
[PD]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/CDVD/CDVD.cpp
[PF]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/x86/microVU_Clamp.inl
[PL]: https://github.com/PCSX2/pcsx2/tree/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89
[PT]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/GS/Renderers/HW/GSTextureCache.cpp
[PH]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/GS/Renderers/HW/GSRendererHW.cpp
[PG]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/GS/GSState.cpp
[PK]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/GS/Renderers/Vulkan/GSDeviceVK.cpp
[GD]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/bin/resources/GameIndex.yaml
[G]: https://github.com/brad-richardson/parallel-gs/blob/963cb57503245e31efb2df89a4740cd4da66513b/gs/page_tracker.cpp
[R]: https://github.com/brad-richardson/PS2Recomp/blob/f949ff060d9a0c53f3ab47998068b771f20653e3/ps2xRuntime/src/lib/ps2_runtime.cpp
[S1]: https://github.com/PCSX2/pcsx2_patches/blob/9f82a4d2b8a2aaf83807421f18d5d30263ea826c/patches/SLUS-20772_08FFF00D.pnach
[S2]: https://github.com/SSXModding/SSX-Patches/blob/30264a35af494c892a1cafee4602029d6577f357/PS2/SSX%203/SLUS-20772_08FFF00D.pnach
[SW]: https://forums.pcsx2.net/Thread-PCSX2-Widescreen-Game-Patches?page=790
[SP]: https://ssx.computernewb.com/wiki/PS2_Patches
[FMT]: https://pcsx2.net/docs/advanced/writing-patches/
[X3]: ../../local/research/X3/ORCH-CORRECTIONS.md
[AE]: https://pcsx2.net/blog/2021/aethersx2-brings-pcsx2-to-mobile/
[NE]: https://github.com/Trixarian/NetherSX2-patch/blob/f5f89b3b76e89a8f684da91cf5ad6e542825c0cb/README.md
[NF]: https://github.com/Trixarian/NetherSX2-classic/blob/main/assets/faq.html
[AR]: https://github.com/ARMSX2/ARMSX2/tree/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64
[AM]: https://github.com/ARMSX2/ARMSX2/blob/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64/recVTLB-arm64.cpp
[AF]: https://github.com/ARMSX2/ARMSX2/blob/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64/AsmHelpers.h
[AG]: https://github.com/ARMSX2/ARMSX2/tree/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/GS/Renderers/Common
[AC]: https://github.com/ARMSX2/ARMSX2/blob/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64/microVU_ProgCache-arm64.h
[AT]: https://github.com/ARMSX2/ARMSX2/tree/247fa6f09499f69192c52c0542305ed16119518b/tests/ctest/core/recompilers
[ARREL]: https://github.com/ARMSX2/ARMSX2/releases/tag/nightly-20260924
[YP]: https://github.com/yaps2/yaps2/blob/57ea93c0ce8306063b31fe6658dab6b492bbedfe/README.md
[PLAY]: https://github.com/jpd002/Play-/tree/83700b2c31e593bc94e845b4b31b797be84dda59
[PJ]: https://github.com/jpd002/Play--CodeGen/blob/a5009f7dca062695b8e5aebbd71e67b4ddfa9251/src/Jitter_CodeGen_AArch64.cpp
[PMOB]: https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/Source/gs/GSH_Vulkan/GSH_VulkanDrawMobile.cpp
[PIDLE]: https://github.com/jpd002/Play-/blob/83700b2c31e593bc94e845b4b31b797be84dda59/Source/ee/Ee_IdleEvaluator.cpp
[IR]: https://github.com/allkern/iris/tree/90dae6afaa055444bdf89fa04f14cffafc271f9f
[IRREL]: https://github.com/allkern/iris/releases
[DOB]: https://github.com/PSI-Rockin/DobieStation/tree/68dd073e751960fd01c839ac34ce6e056d70024a
[UP]: https://github.com/ran-j/PS2Recomp/blob/75d729ce40d7eed9649fd4bb05628dee520f3d0c/README.md
[FORK1]: https://github.com/BlackLineInteractive/SHO-GTA-VCS-PS2Recomp/tree/659a2b0db11a14e818001f57331e216f5c604000
[FORK2]: https://github.com/sp00nznet/reo/tree/73ad3c9f8802b48b811f17dd6bb7d815afb9a727
[SD]: https://github.com/ssxdecomp/ssx3/blob/0b287a3216268d501b1c359f43fb84919df93c7f/README.md
[OG]: https://github.com/open-goal/jak-project/blob/76e8eeca35064ed83c3481b4eff51ee38c8ee361/README.md
[N64]: https://github.com/N64Recomp/N64Recomp/blob/ffb39cdad1da5de07eaaa48bd1db4a89a7986771/README.md
[XEN]: https://github.com/hedge-dev/XenonRecomp/blob/ddd128bcca99fe8bfbb99bea583c972351fa6ace/README.md
[PV2]: https://github.com/PCSX2/pcsx2/blob/ae2bac2b09a7622e5181dc7bf5f6b521c53f7b89/pcsx2/Vif1_Dma.cpp
[AF2]: https://github.com/ARMSX2/ARMSX2/blob/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64/VuFmacFlags-arm64.h
[AC2]: https://github.com/ARMSX2/ARMSX2/blob/247fa6f09499f69192c52c0542305ed16119518b/pcsx2/arm64/microVU_Persist-arm64.h
