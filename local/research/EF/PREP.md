# EF — E-lane preparation and E7 decision framing

**Prep complete at E6 landing; no E7 execution.** The leading E7 question is
whether the display function's copy packet reaches the GS. A fixed
`S+0x5a88=112` is compatible with the guest's explicit copy mode. It does
not, by itself, justify making that field alternate or selecting fbp0 in
Present. EF names a concrete missing CPU-to-VIF1 FIFO ingestion path as a
candidate emulator gap; its causal role in the E4/E5 window remains open.

The independent receipt bundle was completed against ssx3
`d12366565486872ff114e01fff2f30350b597dcd`, before E6 landed. E6 then landed
as `57e1afb`; its entire 414-line report, including the complete tail, was
read. E6 supersedes overlapping allocation/writer enumeration. EF's
additional historical S-address join, copy-tail trace, and fix design are
retained below. No new dynamic observations were taken by EF or E6.

## 1. Scope, provenance, and read receipt

| Item | Receipt / limit |
|---|---|
| Authorized work | Static prep and standalone evidence files only; no boots, builds, lease acquisition, adb, or fork writes. The subsequent E7 handover explicitly authorizes finishing the EF evidence commit first. |
| Commit authority | The initial prep brief both prohibited and requested a commit; EF initially followed the no-commit gate. The E7 handover resolves that conflict by explicitly instructing an EF commit. Only `local/research/EF/` is included; no ssx3 push. |
| E4 / E5 | Both REPORTs read in full, including errata and tails. E5 G6 is the S-trace handoff. E5 watch-series head/shape, complete census/tail, flip-dis in full, history head/census/tail, and present in full read. |
| E6 | Prompt read before prep; no E6 capture duplicated. Landed REPORT read in chunks through line 414. E6 took no boot. |
| ELF | `/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72`, 3,890,784 bytes, SHA-256 `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`. |
| Fork | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, HEAD `a13b66a540514544007c121e7220b02846e1275d`; pre-existing generated `register_functions.cpp` modification not touched. |
| Decode | ELF PT_LOAD mapping follows AC1's approach. Every reused OUT disassembly annotation is checked against the ELF instruction word. Unknown annotations remain raw words. No disassembler installation or regeneration. |
| Runtime inputs | Only committed E4/E5/P1/T1/T5/T12 research artifacts. Old boots are explicitly separated from the E4/E5 window. |
| SSD hygiene | `COPYFILE_DISABLE=1` on SSD shell steps; miners run with `python3 -B`. No cache files or generated runner changes. |

Local receipt key: [R1–R11](ef-static-receipts.txt) is the independent,
1,581-line bundle. [H1–H3](ef-handover-receipts.txt) records the landed E6
revision and supplements the CPU store-path audit. The bundle retains
source hashes and complete tails; it does not copy the large VRAM binaries.

| R1 joined evidence | Independently checked result |
|---|---|
| E5 watch series | 7,329 rows; 1,466 DISPFB1 writes, all `0x9070` (FBP 112): one thread-1 boot write and 1,465 thread-5 writes at `0x382cf0`, return `0x382824`. PMODE has 1,465 rows; E5's missing-row caveat remains. |
| E4 / E5 steady histories | Each has 122 draw events, all fbp0; 46 GIF-tag events; 59 register events. E4 has one additional Present event. These are tag events, not necessarily 46 distinct submitted packets. |
| Missing copy signatures | Neither history contains `FRAME_2` register `0x4d`, nor packed A+D tag `(nloop=16, flg=0, nreg=1)`, nor the copy-prefix packed A+D tag with nloop 11. |
| Present | E4/E5 present files are byte-identical, SHA-256 `f6e08a9d85893051acd5c528093ee4fcb77888a31d91ed830ef998618901bc3f`; display/source fbp112, preferred source absent. |
| Window limit | These are bounded 600→601 receipts. Sparse watch-series `tick~` labels are not exact event timestamps. The copy tail follows the display MMIO, so its absence needs a same-call completion/boundary join before being assigned a cause. |

## 2. S identity, allocation, runtime address, and fields

E6's allocation and singleton-publication trace agrees with EF. E6 adds
the allocator name `PS2GraphicsMan`, the teardown-null store, and another
gate writer (`0x27a950`); those are adopted here.

| Link | Static receipt | Consequence |
|---|---|---|
| Factory caller | `0x226970 → 0x375a08` | One directly named factory call. |
| Allocation | `0x375a20 → 0x317d70`, delay `$a0=0x75e0`; `0x375a28 → 0x395288` | S is a 30,176-byte allocated object; ctor receives allocation return. |
| Publication | `sw v0,-0x854(gp)` at `0x22697c`; gp `0x4a30f0` | Singleton pointer at **`0x4a289c`**. E6 also identifies teardown-null at `0x2280ac`. |
| Base-ctor publication | `0x395294 → 0x3691f8`; `sw s2,+0x2a90(gp)` at `0x369378` | Additional S pointer slot **`0x4a5b80`**. These slots' ELF zero/BSS contents are not runtime pointer values. |
| Vtable and init | `S+0x10d8=0x493260` at `0x3952ac`; `[0x493274]=0x375a40`; indirect call `0x226988` | S reaches bring-up; ELF adjustment word at `0x493270` is zero. |
| Thread binding | `s4=S+0x5ae0` at `0x375c1c`; stack size `0x1000`, entry `0x382740`, priority 5; StartThread delay at `0x375e44` passes S | Thread 5 receives S directly. |
| Steady call | entry `0x382740 → 0x382760`; latter keeps S in s0; `0x38281c → 0x382af0` with a0=s0 | E5's per-frame caller is this object's worker. |
| Boot call | JAL at `0x37c158`, return `0x37c160` | `0x37c160` is the return address, not the call instruction. |

**Historical numeric address: `S=0x61ba60`.** R2 has two independent
committed joins. T1, T5, and both T12 snapshots give thread 5
`sp=0x622480`. Its stack is embedded at S+0x5ae0, with size 0x1000;
entry frames subtract 0x10 and 0xb0. Scheduler stack setup gives
`S = 0x622480 + 0xc0 - 0x1000 - 0x5ae0 = 0x61ba60` for the aligned
allocation. Separately, committed P1 REPORT line 4166 directly records
`a0=0x61ba60` at virtual call `0x3760d0 → 0x395cf0`.
This is usable as a candidate watch address with a singleton-pointer
guard. It is not a new same-boot E5 value receipt or a guarantee that every
future allocation has the same address.

| S field | Candidate address if S=`0x61ba60` | Writer / role |
|---|---|---|
| `+0xf44` G | `0x61c9a4` | One-call select-skip flag; writers in §3. |
| `+0x59e8` M | `0x621448` | Fixed-buffer/copy mode; initialized 1 at `0x375fbc`. |
| `+0x5a74` C | `0x6214d4` | Counter initialized at `0x37be38`, incremented at `0x382b30`. |
| `+0x5a78` A | `0x6214d8` | First VRAM allocation; store `0x37c004`. |
| `+0x5a7c` B | `0x6214dc` | Second VRAM allocation; store `0x37c018`. |
| `+0x5a80` Z | `0x6214e0` | Third VRAM allocation; store `0x37c03c`. |
| `+0x5a84` P | `0x6214e4` | Producer FBP; direct writer `0x382b64`. |
| `+0x5a88` D | **`0x6214e8`** | Display FBP; direct writer **`0x382b68`**. |
| `+0x5a8c` state | `0x6214ec` | Worker/IRQ progress state. |

VRAM allocator `0x3673d8` returns an address shifted right by 13,
so A/B/Z/P/D are 8-KiB framebuffer page numbers. Producer loads include
`0x36ad5c`, `0x36b224`, `0x36c91c`, `0x37d4c4`, and `0x37d708`.
For example `0x36ad74 → 0x36ae20` passes P from `S+0x5a84`.
The observed P=0 / D=112 pair is consistent with the first two allocated
buffers; actual A/B/M/G values still need their guarded runtime receipt.

## 3. Writer census and exact advance/gate logic

R3 scans executable CPU sections for field offsets and for immediate
store spans overlapping `+0x5a88..+0x5a8b`, including byte, halfword,
word, doubleword, and quadword forms. It finds one direct field store:
`0x382b68`. E6's larger LOAD-segment scan agrees after excluding data and
instruction-bit coincidences.

| Static match | Classification |
|---|---|
| `0x382b68: sw v1,0x5a88(t9)` | S display writer; t9=a0=S. |
| `0x382b64: sw v0,0x5a84(t9)` | Paired producer writer. |
| `0x37cd54`, `0x39554c`, `0x382cd8`, `0x382ebc` | Display-FBP readers. The last is the copy destination load. |
| `0x21697c`, `0x216f50` | Constant address `0x475a88`, formed after `lui 0x47`; unrelated string references. |
| Computed aliases / bulk stores | Not exhaustively excluded by an immediate scan. Generic memset/memcpy, rebased pointers, and computed dispatch remain separate alias/reachability obligations. “Sole direct identified writer” is the supported claim. |

Exact semantics of `0x382b20..0x382b68` (R5; branch-likely delay slots
checked against ELF and generated runner):

```text
C = C + 1                         // always stored, even when G is set
if G != 0:
    G = 0
    retain P and D
else if M != 0 or (C & 1) != 0:
    P = A; D = B
else:
    P = B; D = A
continue to display MMIO and the packet-building tail
```

| G at entry | M | C after increment | P / D | E7 implication |
|---|---|---|---|---|
| nonzero | any | any | retained; G cleared | Skips selection only; not a gate on the whole display function or its copy tail. |
| zero | nonzero | any | A / B | Fixed buffers are explicitly implemented. An alternating-display patch would change guest policy. |
| zero | zero | odd | A / B | Parity mode, first selection. |
| zero | zero | even | B / A | Parity mode, second selection; this is the named D→A advance. |

| Control | Identified writers / forcing receipt | Remaining limit |
|---|---|---|
| M=`+0x59e8` | Bring-up `0x375fbc` stores s1=1; E6 audited the intervening branches and callee-saved value. Set-1 trampoline `0x395568`, store `0x395570`; clear trampoline `0x395578`, store `0x39557c`. | No direct call or stored-function-word references to either trampoline were found. This does not prove all computed reachability or bulk aliases impossible. Mode persistence is a strong static hypothesis, not a sampled M series. |
| Other `+0x59e8` store | `0x294890` belongs to an indexed six-element accessor, a different object protocol. | Offset match alone does not bind its base to S. |
| G=`+0xf44` | Base ctor clears at `0x369370`; `0x37cc98` sets at `0x37d050`; E6 adds singleton-derived set at `0x27a950`; setter `0x3946d8` stores 1 at `0x3946e0`; display consumes/clears at `0x382b38`. | G alone cannot explain a missing copy when M remains 1. Multiple writers also prevent deriving the fp-user's unique call rate from a G series alone. |

Under M=1, D remaining 112 is expected once B=112 is selected. The
unresolved join is production-to-display copying, not an assumed need to
clear M. The OUT and runner files for `0x382af0`, `0x382760`, `0x371940`,
and the allocator wrapper are byte-identical (R11); no branch-likely or
generated-source mismatch was found.

## 4. The copy and submission join beyond E6's sliced window

The copy producer is in **the tail of `0x382af0` itself**. It should not
be conflated with `0x37cc98`, which reads the displayed buffer for a
different packet path and sets G. R7 contains the instruction receipts.

| Stage | Guest receipt | Meaning / expected observation |
|---|---|---|
| Copy gate | `0x382e78` loads M; `0x382e7c` branches to `0x3833a8` when zero | M≠0 both fixes A/B selection and enables the explicit P→D copy. G does not guard this branch. |
| Packet storage | a0=`0x004ffcc0`; fp=a0 OR `0x30000000` at `0x382e80` | CPU builds through alias **`0x304ffcc0`**; GIF reads physical **`0x004ffcc0`**. Current memory translation already maps this RAM alias. |
| Copy prefix | Tag `0x100000000000000b`; FRAME_1 from D at `0x382ebc..0x382ef4` | Packed A+D, nloop 11; destination D, display stride `+0x5a5c`, display PSM `+0x5a38`. |
| Texture source | `0x382f04..0x382f54` | TEX0 source uses **P<<5**, producer stride `+0x5a50`, PSM `+0x5a3c`. P uses 8-KiB pages; TEX0 uses 256-byte blocks. |
| Copy geometry | Sprite/reglist strip loop `0x383298..0x3832d0` | Consistent with the boot texture-copy shape. No claim that this proves a same-window invocation. |
| Unconditional suffix | Starts `0x3833a8`, tag **`0x1000000000008010`**; FRAME_1 and **FRAME_2** built through `0x383438` from P | Packed A+D nloop 16 plus `FRAME_2` register **`0x4d`** must be consumed if this completed packet reaches the normal parser, even when M=0 skips the copy prefix. |
| Submission | QWC derived from final pointer at `0x383724..0x383734`; `0x383738 → 0x371940`, a0=physical buffer, a1=QWC, a2=6 | A concrete submission path exists after both mode branches. |
| CPU VIF write | `0x37199c` loads command block `0x44b430`; **SQ at `0x3719a4` to `0x10005000`** | Block is `[0x06000000,0,0,0]`: opcode 0x06 with mask bit clear, followed by NOPs, under the existing VIF interpreter. |
| Normal GIF DMA | `0x3719b4` writes GIF_MODE=4; `0x3719e8` MADR; `0x3719fc` QWC; `0x371a04` CHCR=`0x101` | Transfer uses channel `0x1000a000`, then waits for STR clear (a2 bit 1). DMA completion is not necessarily GS consumption. |
| Related masks | Worker SQ sites `0x382980` and `0x382a48`, command block `0x44b9c0=[0x06008000,0,0,0]`; `0x44b3dc` also contains 0x06008000 in a stream template | Both CPU mask and unmask ingress are absent in the current source path. A causality claim therefore needs evidence that an interpreted VIF stream actually set the mask. |

Historical committed call counters already constrain “never re-fires”:

| Snapshot (R2) | `0x382af0` entries | `0x371940` entries | Helper first / last return address |
|---|---:|---:|---|
| T1 | 5,293 | 5,293 | `0x383740` / `0x383740` |
| T5 | 5,279 | 5,279 | `0x383740` / `0x383740` |
| T12 dev | 5,297 | 5,297 | `0x383740` / `0x383740` |
| T12 rel | 5,242 | 5,242 | `0x383740` / `0x383740` |

These older boots support repeated submission-helper entry. They do not
measure per-call M, packet bytes, helper completion, or mask state in E5.
The lack of the unconditional FRAME_2/16-A+D signature in E4/E5 is the
stronger packet-consumption discriminator to join next.

## 5. Worker state and the candidate emulator gap

| State edge | Receipt | Limit on a guest-stall claim |
|---|---|---|
| Producer queues work | `0x377b1c` sequence stores queued index/chains, slot=2 at `0x377b58`, signals mutex/work | Names producer input to the worker. |
| 0→1 | Worker consumes queued slot, marks slot=3 and state=1 at `0x382920`, starts DMA | Active/queued fields `+0x5a98/+0x5aa4`; slot states `+0x5a90/+0x5a94`. |
| 1→2 and 3→4 | DMAC handler `0x382688`, stores at `0x3826a8/0x3826d0` | Handler registered for DMAC cause 1. |
| 2→3 | Worker optional callback then next submission; state=3 at `0x382acc` | A specific second phase, not an unnamed flip. |
| 4→5 | INTC handler `0x3825f8`, counter threshold and store at `0x382634` | Handler registered for INTC cause 2; threshold `+0x5ab8`. |
| 5→0→display | Worker releases active slot, state=0 at `0x382818`, call at `0x38281c` | E5's repeated steady caller is evidence this edge keeps firing. A global worker park is inconsistent with that observation. |

**H-FIFO (conditional causal hypothesis):** a VIF stream sets PATH3's
mask; the guest's CPU FIFO unmask at `0x3719a4` is stored as inert MMIO;
normal GIF copies enter a masked queue and never reach GS history, while
producer traffic through other paths continues. This would explain boot
copy activity followed by steady P=0 / D=112 black display without
changing guest buffer policy. The actual mask transition and queued
packet identity remain unobserved in the joined window.

| Source fact (fork a13b66a; R10/H2/H3) | Why it matters |
|---|---|
| `ps2_runtime.cpp:2896–2913`, `Store128` | After diagnostics it directly calls `m_memory.write128`; no FIFO-specific runtime interception. Generated `0x3719a4` uses this Store128 path. |
| `ps2_memory.cpp:1083–1128`, `write128` | I/O falls through to two write64 calls. |
| `ps2_memory.cpp:967–1081`, write32/write64 | Those become four write32 calls into `writeIORegister`. |
| `ps2_memory.cpp:1224–1293`, register dispatch | Stores register-map values and handles VIF control registers at `0x10003c00`; it does not ingest the `0x10005000` FIFO payload. Library/header textual cross-check finds no alternate literal-address handler. |
| `ps2_vif1_interpreter.cpp:352–359` | Existing MSKPATH3 handling sets `m_path3Masked` from bit 15 and flushes when it clears. The command semantics already exist; CPU ingress is missing. |
| `ps2_memory.cpp:1937–1959` | Masked PATH3 packets are copied into `m_path3MaskedFifo` and return without GS delivery. |
| `ps2_memory.cpp:1876–1895` | Pending-transfer processing still clears STR/QWC and raises completion. Guest progress does not prove those bytes were consumed by GS. |
| `ps2_memory_tests.cpp:850–900` | Existing mask/flush tests call the interpreter directly. They bypass CPU stores, so cannot detect this ingress omission. |

The source omission is concrete. Its classification as **the E7 blocker**
is conditional on the receipt above. In particular, a lost direct CPU
mask cannot establish a mask that the same broken path never set.

## 6. E7 candidate fix-design matrix

All paths below are relative to the fork unless noted. No implementation,
test execution, regeneration, or boot was performed in EF. “Verdict” here
means a conditional E7 branch, not a black-screen root-cause verdict.

| Candidate join | Emulator-gap vs guest-gate framing / forcing receipt | Candidate fix and exact files | Risks | Proving receipt / decision |
|---|---|---|---|---|
| **Fixed-mode copy: CPU VIF1 FIFO unmask** | **Named emulator ingress gap; leading causal candidate.** SQ/command/store descent above versus existing MSKPATH3 semantics. Need actual interpreted mask=true and copy queued at that edge. | Route a complete CPU quadword FIFO write to the existing VIF interpreter before generic I/O splitting in `ps2xRuntime/src/lib/ps2_memory.cpp`. Add a public-memory-path regression in `ps2xTest/src/ps2_memory_tests.cpp`. If general FIFO buffering is required, place state/API in `ps2xRuntime/include/runtime/ps2_memory.h` and decode integration in `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`. | Ordering with pending VIF payload, split commands, DMA reentrancy, synchronously flushing old packets, CPU mask writes becoming effective too. Define supported widths/aperture from the architectural contract; do not treat every I/O quadword as VIF data. | Before/after memory-ingress regression plus same-call unmask→mask-clear→ordered flush→copy FRAME_2/16-A+D→D draw→nonblack D VRAM→faithful Present. If mask is false throughout, this omission alone does not explain this window. |
| Copy reaches DMA but is lost elsewhere | Emulator gap only if packet bytes and unmasked submission are proved, followed by missing consumption. Current RAM-alias mapping is already present. | Narrow repair at demonstrated layer: `ps2xRuntime/src/lib/ps2_memory.cpp` / `include/runtime/ps2_memory.h` for transfer ownership/order; `ps2xRuntime/src/lib/gs/ps2_gif_arbiter.cpp` for arbiter loss; tests in `ps2xTest/src/ps2_memory_tests.cpp` or `ps2_gs_tests.cpp`. | Stale-pointer guesses, duplicate/reordered packets, treating completion as consumption, broad alias changes that alter other traffic. | Same packet hash at alias/physical source, declared QWC, DMA entry, arbiter delivery, parser tag; first missing edge selects the file. No transport fix from absence alone. |
| D parity advance | **Guest policy when M≠0 or G≠0.** Emulator gap only if M=0, G=0, alternating C, distinct A/B, yet actual writes disagree with the decoded branch. Current OUT/runner agree. | If proven codegen error: `ps2xRecomp/src/lib/control_flow_emitter.cpp`, regression `ps2xTest/src/code_generator_tests.cpp` / `ps2_recompiler_tests.cpp`. Any regeneration remains subject to the separate 0x426230 DROP gate. No S-specific runtime toggle. | Breaking intended fixed-copy mode, branch-likely delay-slot semantics, changing both P and D incorrectly. | Watch inputs and `0x382b64/68` outputs for two consecutive calls; reproduce a mismatch against guest semantics. Otherwise keep the field policy. |
| Guest G or M gate / mode transition | **Guest-gate finding** only when its actual values and named writer explain the missing intended join. G skips selection, not copy; M=1 enables copy. No static requirement that M must clear. | No emulator source change on a guest-gate finding. Extend E7 evidence only; investigate the named setter/caller dependency if values require it. | Inventing a stuck gate from no direct callers, promoting SIF/CD without a dependency, forcing M=0 to conceal lost copies. | Writer-attributed G/M series plus relevant branch/path receipt. Parking requires showing the guest withheld the needed operation under faithfully executed semantics. |
| Worker/IRQ advance | Broad stall disfavored by E5's recurring state-5 display caller. Gap only with a newly demonstrated missing transition. | If proved: `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `ps2xRuntime/src/lib/ps2_memory.cpp`, and narrowly selected `ps2xRuntime/src/lib/ps2_runtime.cpp`; tests `ps2xTest/src/ps2_runtime_interrupt_tests.cpp` / `ps2_runtime_kernel_tests.cpp`. | Duplicate interrupts, starvation, changing already-working producer progress. | Exact state/IRQ/semaphore predecessor and successor, source event present but transition absent. No global wakeup patch. |
| Raster / Present | **Not supported by current joined evidence.** Present faithfully reads black D; the copy packet's mandatory signature is absent. | No current fix proposed. Reconsider `ps2xRuntime/src/lib/gs/gs_frontend.cpp` plus `ps2xTest/src/ps2_gs_tests.cpp` only after actual copy consumption is proved. | Forcing scanout to P hides the missing join and breaks guest display selection. | Correct P→D packet consumed with valid state but D pixels wrong would reopen raster; D pixels correct but host wrong would reopen Present. Neither is currently receipted. |

The narrow FIFO regression should enter through `PS2Memory::write128`
at `0x10005000`, not directly through the interpreter: first establish a
mask using interpreted input, queue two distinguishable PATH3 packets,
then store `[0x06000000,0,0,0]` and require one ordered flush. Also cover
CPU mask-on, repeated mask-off without duplicate delivery, and a normal
GIF DMA with the helper's MADR/QWC/CHCR shape. A broader FIFO implementation
needs meaningful fragmented-input and mixed CPU/DMA ordering tests. These
are proposed E7 tests, not tests run in prep.

## 7. Challenged premises and E6 reconciliation

| Premise | Forcing receipt / weakness | Correct E7 framing |
|---|---|---|
| E5 J2a favored because D is loaded rather than immediate | A loaded variable can be fixed by mode; M≠0 explicitly picks A/B on every call and enables a copy tail. | The trace demotes compulsory D alternation. Check the intended copy join first. |
| “Boot blit never re-fires” means guest never resubmits it | Older committed helper counts track display counts; the complete function builds/submits the packet. E4/E5 only prove missing observed copy work in their window. | Distinguish copy enabled, packet built, helper entered/completed, DMA completed, and GS consumed. |
| E6 §3/§6 fixed pick establishes guest-side cause and no emulator gap | It establishes a guest selection mechanism. The omitted display-function tail includes a copy whose CPU FIFO ingress is missing in the emulator. Static boot M=1 also is not a live persistence proof. | Accept E6's named allocation/writers/selection; keep black-screen cause open and carry H-FIFO into E7. |
| E6 identifies `0x37cc98` as the principal J2b carrier | That path reads D and sets G. The direct P→D copy is named inside `0x382af0`, using M and P/D explicitly. | Trace `0x382e78 → 0x383738 → 0x371940` for the production/display join. |
| E6 needs one boot solely to locate S, then another for fields | Historical P1 direct a0 plus four committed thread-stack joins already give candidate S=`0x61ba60`. | A single guarded observation can include `0x4a289c` and candidate field addresses. If the pointer differs, reject the candidate-field interpretation; do not assume stability. |
| “All writers closed” from literal/lea scans | Rebased pointers, generic bulk writes, and computed targets are not excluded just because exact offset/address literals are absent. | Sole identified direct writer is `0x382b68`; name the residual alias scope. |
| A G series uniquely measures fp-user rate | E6 itself names more than one G=1 writer. Multiple sets can occur before one consuming display call. | Attribute writes by PC; G values alone yield skip behavior, not a unique caller count. |
| Per-frame MMIO proves per-frame GS copy completion | MMIO occurs before the packet tail; masked PATH3 processing can mark DMA complete while retaining bytes. | Bracket the same call and capture downstream consumption, including an adjacent boundary if necessary. |
| E4 before/after identical VRAM establishes effects of all 122 draws | It proves net equality across the window, not that each event modified useful pixels. | Retain the useful fbp0 / black fbp112 / faithful Present finding; do not infer individual raster writes from event counts alone. |
| 46 history `gif` events are 46 packets | The frontend records GIF tags within packets. | Use 46 tag events; require packet identity to count submissions. |
| EF's missing FIFO ingestion proves H-FIFO | Direct CPU masks are missing too; an interpreted mask-setting stream and queued copy were not dynamically joined here. | Candidate semantic gap, conditional cause; keep the explicit falsifier mask=false / packet already delivered. |

## 8. One next-action recommendation for E7

**Author E7 around the copy-submission/FIFO boundary, retaining E6's
field-value check as a guard in the same investigation.** Do not start
with a forced D advance or a two-boot address-discovery assumption.

| Ordered E7 decision | Required receipt | Resulting action |
|---|---|---|
| Validate identity and mode | Singleton store `0x4a289c`; candidate S fields A/B/P/D/C/G/M with writer PCs. Use candidate addresses in §2 only if the same run confirms S. | Select parity or fixed-copy semantics from actual values. Unexpected S invalidates the candidate-address join. |
| Locate the copy at the boundary | `0x371940` from return `0x383740`; CPU unmask at `0x3719a4`; physical packet hash/QWC and mandatory suffix; helper completion aligned to GS history. | Establish whether the guest actually offered the packet in the observed window. |
| Resolve H-FIFO | Mask before/after CPU command, prior interpreted mask setter, masked queue count/packet identity, and actual GS delivery. | If the missing ingress suppresses this packet, implement the generic ingress fix with the regression above. If not, follow the first demonstrated missing edge or record the actual guest gate. |
| Prove the resulting join | Copy destination remains guest-selected D; packet consumed; D VRAM becomes nonblack with expected content; Present reads the same D correctly. | Demonstrate the production→display join, not merely a changed host picture or increased helper count. |

Existing address watches can receipt singleton/field writes, the CPU
FIFO store, and DMA register writes; they do **not** expose the private
mask/queue state or prove packet consumption. E7 must use an existing
state interface if one exists or explicitly scope a bounded tap at these
named interfaces in its execution brief. Avoid claiming the E5 watch
format alone closes H-FIFO. Any E7 capture must specify wall, byte, and
progress caps and acquire the shared P-lane lease under its own brief;
EF neither acquired it nor ran a capture.

## 9. Reproduction, deliverables, and tail

From the ssx3 root (all scripts read only; shell redirection writes EF
evidence only):

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/EF/ef_static.py dis 0x382b20 0x382b74
python3 -B local/research/EF/ef_static.py dis 0x382e64 0x382f60
python3 -B local/research/EF/ef_static.py dis 0x371940 0x371a54
python3 -B local/research/EF/ef_static.py imm 0x5a88 0x5a84 0x59e8 0xf44
python3 -B local/research/EF/ef_receipts.py > local/research/EF/ef-static-receipts.txt
python3 -B local/research/EF/ef_handover.py > local/research/EF/ef-handover-receipts.txt
```

`ef_receipts.py` records the current ssx3 HEAD and hashes its committed
inputs; the retained pre-E6 run names `d123665...`. Reproduction at a
later HEAD can change the header or inputs; compare source hashes before
equating results. Fork-source excerpts likewise carry hashes. No tests
of emulator behavior were executed; validation consists of ELF/OUT word
checks, OUT/runner identity checks, complete committed-event censuses,
script execution, and bounded report/tail reads.

Deliverables: `PREP.md`, `ef_static.py`, `ef_receipts.py`,
`ef_handover.py`, `ef-static-receipts.txt`, and
`ef-handover-receipts.txt`. The E7 handover explicitly authorizes this
EF evidence commit; no push. E6 report was read through its complete tail
after landing. This prep artifact supplies hypotheses and decision
branches; the newly authorized two-boot value-series work belongs in E7.

---
**Tail receipt: EF PREP §§1–9 complete. R1–R11 independent receipts and
H1–H3 E6 handover supplement end with explicit COMPLETE markers. E4 and
E5 reports read in full; E6 landed and was read in full. No boots, builds,
lease, adb, fork writes, pushes, or fresh runtime observations in EF.
EF evidence commit authorized by the subsequent E7 handover.
Leading E7 hypothesis: missing CPU VIF1 FIFO ingress prevents the
fixed-mode copy's PATH3 unmask; causality remains to be receipted.**
