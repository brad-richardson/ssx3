# SS1 inventory: PS2Runtime, PS2Memory, VU, GS (CPU + paraLLEl)

Read-only subagent read for SS1 (Opus); file:line against fork a3efbfe, paths relative to ps2xRuntime/.

## Save-state inventory: PS2Recomp `ps2xRuntime` @ a3efbfe (SS1 worktree), paraLLEl-GS @ 19d93b2 (F2)

This is a read-only inventory. Nothing was edited, built or run. Paths are relative to `/Users/brad/dev/ssx3-work/SS1/PS2Recomp/ps2xRuntime` unless they start with `pgs/`, which means `/Users/brad/dev/ssx3-work/F2/parallel-gs`.

Plan legend:
- **C**: capture it.
- **R**: rebuild it, or drop/invalidate it on load.
- **D**: diagnostic only. Ignore it; it must be off while saving.
- **B**: blocker or gap.

### 1. Mutable state table

#### PS2Runtime (`include/ps2_runtime.h`)
| item | file:line | size/type | host ptr / thread / GPU | plan | notes |
|---|---|---|---|---|---|
| m_cpuContext (R5900Context) | ps2_runtime.h:527 (struct 58-195) | ~1.3 KB POD (__m128 GPRs, VU0 macro regs, COP0, FPU) | no | C | Boot context only. The running guest threads' contexts live in EeScheduler (out of scope). VU0 macro state (vu0_vf/vi/acc/q/p/flags/fbrst/itop) lives in each R5900Context, 71-102. |
| m_vu0 / m_vu1 | :525-526 | VU1Interpreter | yes (see VU section) | C/R | See VU section. |
| m_memory, m_gs, m_gifArbiter | :518-520 | objects | – | – | See their own sections. |
| m_iopHost, m_iopSubsystem, m_audioBackend, m_padBackend | :521-524 | unique_ptr / objects | yes | out of scope | IOP/SIF/audio/pad must be covered separately. `run()` resets them via `ps2_stubs::resetSifState/…` (ps2_runtime.cpp:3984-3988). |
| m_eeScheduler | :528 | unique_ptr<EeScheduler> | – | out of scope | Owns guest threads/contexts, events, the vsync tick (EeScheduler.cpp:2896) and the GS vsync callback (set from GS.cpp:1332). |
| m_eeExitHandlers, m_eeSyscallOverrides, m_eeSyscallMirrorAddresses | :530-532 | unordered_map/set | no | C | Guest-kernel state. |
| guest heap: m_guestHeapBlocks + base/end/limit/suggested/configured | :535-540 | vector<POD> + u32s | no | C | |
| m_asyncCallbackStackFloor/Top | :544-545 | u32 | no | C | |
| m_loadedModules | :581 | vector{string,u32,size_t,bool} | no | C | |
| missing-function policy/counts, unknown syscall/RPC counts | :547-553 | atomics/maps | no | D | |
| m_stopRequested, debugUi callbacks/userData, m_debugPc/Ra/Sp/Gp | :559-570 | atomics/fn ptrs | yes | R | |
| m_boundRdram, m_boundGSVram | :582-583 | host ptrs | yes | R | Set by syncCoreSubsystems (ps2_runtime.cpp:1177-1293). |
| m_eeKernelStateMutex, heap/async/coverage mutexes | :529,533-534,550 | mutex | – | R | |
| g_dispatchHistory | ps2_runtime.cpp:185 | thread_local ring of 64 PCs | GameThread | D | |
| IoPaths static | ps2_runtime.cpp:407 | paths | – | R | Config, from the ELF/CLI. |
| g_ssx3WidescreenActive/Mode | ps2_runtime.cpp:137-138 | atomics | – | R | Config; could also be C. |
| UploadFrame statics (s_lastPresentationTick, s_hasLatchedInitialFrame, s_last*, s_scratch, s_uploadBuffer) | ps2_runtime.cpp:774-783 | host present latch | main thread | R | Host-only. Reset s_lastPresentationTick after load so the first frame latches. |
| g_hr1*Ns, g_hr1ShareTex | ps2_runtime.cpp:728,732 | atomics / GL texture | main, GPU | R/D | |
| g_e3rec/g_e3inv/g_e3n394, diag statics 512-620, 2126-2198, 2896, 2940 | ps2_runtime.cpp | diag | – | D | |

#### PS2Memory (`include/runtime/ps2_memory.h`; all members are public, from :266)
| item | file:line | size/type | host ptr/thread | plan | notes |
|---|---|---|---|---|---|
| m_rdram | :380 (alloc ps2_memory.cpp:485) | 32 MiB | ptr | C (bytes) | |
| m_scratchpad | :383 (alloc :489) | 16 KiB | ptr | C (bytes) | |
| ps2ScratchpadHostPtrStorage static | ps2_memory.h:74-78 | atomic<uint8_t*> | host ptr | R | Set in initialize (ps2_memory.cpp:490). |
| iop_ram | :386 (alloc :497) | 2 MiB | ptr | C | IOP-side consumers are out of scope. |
| m_gsVRAM | :400 (alloc :518) | 4 MiB | ptr | C | The CPU backend's live VRAM, and the paraLLEl hand-off buffer (see §2). |
| m_vu0Code/Data, m_vu1Code/Data | :422-425 (alloc :521-527) | 4K/4K, 16K/16K | ptrs | C | After loading, call markVU0CodeModified/markVU1CodeModified (:457-458) to invalidate the VU decode and recomp caches. |
| m_vu0/1CodeGeneration | :393-394 | atomic u64 | – | R | Bump on load; don't restore the value. |
| gs_regs (GSRegisters) | :399 (struct 192-216) | 160 B: PMODE…BGCOLOR, CSR (atomic), vsyncTick (atomic), IMR, BUSDIR, SIGLBLID (atomic) | written by the GS worker when queued (PrivWrite lambdas, ps2_memory.cpp:1017-1084) | C | vsyncTick is mirrored from EeScheduler (EeScheduler.cpp:2896). |
| m_ioRegisters | :396 | unordered_map<u32,u32> | – | C (sorted pairs) | Backs DMAC channel regs, D_STAT/PCR, INTC (0x1000F000…), IPU etc. (ps2_memory.cpp:2866-2969). |
| vif0_regs, vif1_regs | :401-402 (struct 222-241) | 92 B each | – | C | VIF work is synchronous per DMA buffer. No other interpreter state (ps2_vif1_interpreter.cpp uses only these + the fields below). |
| m_vif1PendingPath2ImageQwc, m_vif1PendingPath2DirectHl | :427-428 | u32, bool | – | C | DIRECT/HL image continuation across buffers. |
| m_path3Masked, m_path3MaskedFifo | :426, :429 | bool, vector<vector<u8>> | – | C | PATH3 packets held while masked. Guest-visible and can span vsyncs. |
| m_pendingGifTransfers / Vif0 / Vif1 | :441-443 | vector<PendingTransfer{…, vector chainData, srcSpans}> | – | C (expect empty) | Pushed at ps2_memory.cpp:1595-1599/1917-1925. Drained synchronously by processPendingTransfers (ps2_memory.cpp:2070; called from ps2_runtime.cpp:3792). Assert empty at save. |
| m_completedDmacCauses (+mutex) | :444-445 | vector<u32> | – | C (expect empty) | Drained by drainCompletedDmacHandlers (ps2_runtime.cpp:2977). |
| m_tlbEntries | :414 | 48 × {vpn,pfn,mask,valid} | – | C | |
| m_eeTimers | :471 (struct 462-469) | 4 × {count,mode,compare,hold,clockRemainder} | – | C | |
| m_codeRegions | :453 | vector{start,end,vector<bool>} | – | C | Self-modifying-code bitmap. |
| dma_regs[10] | :403 | 7×u32×10 | – | ignore | Only memset, never read (grep). The DMAC lives in m_ioRegisters. |
| m_gifPacketCallback, m_gifArbiter, m_gsFrontend, m_vu1MscalCallback/MscntCallback | :416-420 | std::function / ptrs | host | R | Re-wired by syncCoreSubsystems (ps2_runtime.cpp:1191-1286). |
| m_seenGifCopy, dma/gif/gs/vif counters | :388-392 | bool/atomics | – | D | |
| statics `warned`, `on` | ps2_memory.cpp:1893, 2375 | | | D | |

#### VU0/VU1 (`include/runtime/ps2_vu1.h`, `src/lib/vu/*`, `Stubs/VU.cpp`)
| item | file:line | size/type | host | plan | notes |
|---|---|---|---|---|---|
| m_state (VU1State: vf[32][4], vi[16], acc, q, p, i, r, pc, mac, clip, status, cycles, ebit/halt/D/T flags, top/itop, branchPending/Target/Delay) | ps2_vu1.h:295 (struct 42-68) | ~650 B POD | – | C | |
| m_cycle | :338 | u64 | – | C | Every pipeline readyCycle is an absolute m_cycle value. |
| pipelines: m_flagPipeline, m_fdiv, m_efu, m_storePipeline, m_vf/vi/accWritePipeline, m_vf/vi/accReady, valid masks, m_nextCommitCycle, m_vf/vi/accLatestWrite | :307-336 | ~3 KB POD | – | C | Flushed at program end (ps2_vu1_core.cpp:1482-1488). Non-empty only if a program stopped on the budget or a D/T bit and waits for MSCNT. |
| m_nextWriteSequence, m_efuResourceReady, m_workingClip, m_currentUpperInstruction, m_viBranchBackup*, m_stopRequested, m_pendingHaltD/T | :339-352 | scalars | – | C | |
| m_xgkick (XgkickPipeline) | :314 (struct 254-283) | 64 KiB packet + progress | – | C | In-flight XGKICK. |
| m_directPendingUntil, m_directStores, m_directFlags | :416-418 | scalars | – | C | Needed for a cycle-exact flushPipelines (comment :400-411). |
| m_decodedCodeCache + m_cachedVuCode/Memory/Size/Generation/Valid, m_decodeScratch | :299-305 | ~2048 × ~56 B ≈ 110 KB | host ptrs | R | Keyed on the code generation (ps2_vu1_core.cpp:1303-1330). Invalidate with PS2Memory::markVU1CodeModified/markVU0CodeModified. reset() does NOT clear it. |
| recomp cache: m_recompProgram/Code/CodeSize/Generation/Hash/Valid | :392-397 | ptr into static registry | host ptrs | R | Re-looked up on a generation change (ps2_vu1_recomp.cpp:81-129). |
| m_directFlagSafe, m_directFlagMap, m_directRunOk, m_directOverride | :414-420 | ptr/vector | host | R | Rebuilt every run (ps2_vu1_core.cpp:1447-1453). |
| m_activeVuData/Size, m_activeGs, m_activeMemory | :346-349 | host ptrs | yes | R | Set at the start of run (ps2_vu1_core.cpp:1411-1414). |
| entry/trace members (m_entry*, m_trace*) | :359-379 | vectors | – | D | |
| m_recomp/interp cycles, m_recompRuns, m_vb* stats | :398-400, 493-498 | u64 | – | D | |
| static recompRegistry | ps2_vu1_recomp.cpp:41 | map hash→program | – | R | Registered at static init. Constant. |
| static directFlagMap `maps` | ps2_vu1_recomp.cpp:403 | map hash→vector | – | R | Content-keyed cache. |
| static `dumped` | ps2_vu1_recomp.cpp:131 | set | – | D | |
| m_vu0 as a whole | ps2_runtime.cpp:2881-2887 | – | – | R | Reset and loaded from the R5900Context on every VU0 microprogram call, then copied back. No persistent state. |
| VU.cpp stubs | Stubs/VU.cpp:1063 | `warnCount` only | – | D | Otherwise stateless. |

The VU1Interpreter can't be memcpy'd whole because pointer members are interleaved with POD. It needs a field-wise (friend) serializer.

#### GS frontend (`include/runtime/gs/gs_frontend.h`)
| item | file:line | size/type | owner thread | plan | notes |
|---|---|---|---|---|---|
| m_ctx[2] (GSContext: frame, scissor, tex0, xyoffset, zbuf, tex1, miptbp1/2, clamp, alpha, test, fba) | :256 (gs_types.h:179-193) | ~200 B, decoded | GS worker if queued, else GameThread | C | Stored decoded, not as raw u64s. |
| m_prim, m_primRegister, m_prmodeRegister, m_curGifPath | :257-260 | POD | same | C | |
| RGBAQ/STQ/UV/fog latches: m_curR/G/B/A, m_curQ, m_curS/T, m_curU/V, m_curFog, m_fogR/G/B | :262-267 | POD | same | C | |
| m_prmodecont, m_pabe, m_scanmsk, m_dimx, m_dthe, m_colclamp, m_texa, m_texclut | :269-276 | POD | same | C | |
| transfer regs: m_bitbltbuf, m_trxpos, m_trxreg, m_trxdir | :278-281 | POD | same | C | |
| vertex queue: m_vtxQueue[6], m_vtxCount, m_vtxIndex | :285-287 | POD | same | C | A partial strip can span packets. |
| m_preferredDisplaySourceFrame/DestFbp/has | :292-294 | POD | same | C | Affects which buffer the CPU present picks. |
| m_localMemoryStorage/Size, m_privRegs | :249-251 | ptrs to PS2Memory VRAM and gs_regs | – | R | |
| m_displaySnapshot, m_lastDisplayBaseBytes | :289-291 | vector 4 MiB | host cache | R | |
| m_hostPresentationFrame + dims/fbp/flags | :295-301 | vector | main/worker | R | Refilled on the next latch. |
| debug history (512 entries), m_debug* | :306-312 | ~100 KB | – | D | Paused by default. |
| m_pktSeq*, m_submitCount, m_regWriteCount, m_privWriteCount, native counters | :302-303, 321-340 | – | – | D | |
| m_backend, m_worker, m_rawGifBackend | :314, 318, 324 | owned objects | – | R | Recreated by syncCoreSubsystems (ps2_runtime.cpp:1191-1225). |
| s_debug* atomics | gs_frontend.cpp:135-142 | – | – | D | |
| t_inGsWorker | gs_frontend.cpp:165 | thread_local bool | GS worker | R | |

#### GS worker (`gs_worker.h`)
| item | file:line | plan | notes |
|---|---|---|---|
| m_queue (deque<GsCommand>), m_queuedBytes, m_executing, m_batchDepth/Dirty, m_stopRequested/m_running, m_thread, counters | gs_worker.h:161-179 | R (must be empty) | GsCommand holds std::function and shared_ptr RPCs (:112-115), so the queue can't be serialized. Save only when quiescent. m_batchDepth is RAII-scoped per GIF drain (ps2_memory.cpp:28-43), so it is 0 at the dispatcher. |

#### GIF arbiter
| m_queue (vector<GifArbiterPacket>) | ps2_gif_arbiter.h:51 | C (expect empty) | submit/drain are synchronous (ps2_gif_arbiter.cpp:76, 91). Assert `empty()` (:45). Callbacks :48-50 are R. |
|---|---|---|---|

#### CPU backend (`gs_cpu_backend.h`)
| item | file:line | plan | notes |
|---|---|---|---|
| m_vram/m_vramSize | :75-76 | R | Points at PS2Memory::m_gsVRAM (Initialize, gs_cpu_backend.cpp:592-598). |
| m_transfer, m_transferState, m_localToHostBuffer, m_localToHostReadPos | :80-83 | C | An in-progress IMAGE transfer, or pending local→host bytes. Initialize() resets them (ResetUnlocked, cpp:606-614). |
| m_readVramFuncs/m_writeVramFuncs | :77-78 | R | Built in the constructor. |
| thread_local snapshot/snapshotBackend | gs_cpu_backend.cpp:1855, 1860 | R | Present scratch. |
| s_debug* atomics, bob override, lookupTablesOnce | cpp:117-120, 447, 455, 524 | D/R | |

#### paraLLEl backend wrapper (`ps2_gs_parallel_backend.cpp`)
| item | file:line | host/GPU | plan | notes |
|---|---|---|---|---|
| m_ctx/m_device/m_iface (Vulkan::Context, Device, GSInterface) | :846-848 | GPU | R + B | GSInterface holds hidden GS state (§4). |
| m_handoff/Size/m_needHandoff, m_initOk/Failed | :821-825 | host | R | |
| m_l2hPending | :826 | – | C | Pending local→host bytes. |
| m_rb[2]/m_rbIndex (HR1 pipelined readback) | :830-837 | GPU buffers + fences | R | One frame of present latency (:360-387). The first present after a restore returns empty. |
| m_share*/m_shareGraveyard, m_zeroCopy*, m_hiresScanout, m_pipeline, m_lastScanW/H | :827-845 | IOSurface/GPU | R | |
| g_shareMutex, static Counters | :42, 88 | – | D | |

#### Shadow / capture / present share
| ps2x_gs_shadow State (its own Vulkan device + GSInterface) | ps2_gs_shadow.cpp:36-60 | GPU | D | Must be off (PS2X_GS_SHADOW*). onReset re-inits it. |
|---|---|---|---|---|
| gs_stream_capture file state | gs_stream_capture.cpp | FILE | D | |
| ps2x_present_share frames | ps2_present_share.h:15-21 | IOSurface | R | |

#### GS HLE stubs (`Stubs/GS.cpp`)
| g_gparam (interlace/omode/ffmode) | Stubs/Helpers/Support.h:1597, written at GS.cpp:822-824 | 4 B | C | It sits in an anonymous namespace in a header pulled in through Common.h by ~29 stub TUs, so each TU has its own copy (§4). It is also mirrored into scratchpad+0x100 (Support.h:1955), which is captured. |
|---|---|---|---|---|
| s_swapDbuffLogCount, s_syncVCallbackLogCount, logCount | GS.cpp:1172, 1334, 1400 | – | D | |
| GS vsync callback | stored in EeScheduler (GS.cpp:1332) | – | out of scope | |

### 2. GS: VRAM, readback/upload, drain, host-side state

**Where the 4 MiB lives**
- **CPU backend:** a flat `PS2Memory::m_gsVRAM` (`new uint8_t[PS2_GS_VRAM_SIZE]`, ps2_memory.cpp:518). It is handed to the frontend by `m_gs.init(gsVram, …)` (ps2_runtime.cpp:1191) and to the backend by `GSCpuBackend::Initialize` (gs_cpu_backend.cpp:592-596). `SnapshotVram` is a memcpy (:666-676).
- **paraLLEl:** VRAM is inside GSInterface/GSRenderer: GPU buffer `buffers.gpu`, host mirror `buffers.cpu`, and a separate `clut` buffer (pgs/gs/gs_renderer.hpp:398-402). `m_gsVRAM` only goes stale, and serves as the hand-off buffer.

**paraLLEl readback and upload API** (public in pgs/gs/gs_interface.hpp)
- `const void *map_vram_read(size_t off, size_t size)`: hpp:283, cpp:4240-4265. It waits for the GPU timeline, then returns the host mirror. The wrapper already uses it: `SnapshotVram` → `flush()` + `map_vram_read(0, 4 MiB)` (ps2_gs_parallel_backend.cpp:470-490).
- `void *map_vram_write(off, size)` + `end_vram_write(off, size)`: hpp:281-282, cpp:4194-4238. `end_vram_write` calls `tracker.commit_host_write`, which invalidates texture caches. The GPU copy invalidates super-sampling state (pgs/gs/gs_renderer.cpp:1566-1574).
- The wrapper already has an upload path: `Initialize(vram)` stores a hand-off (:251-259), and `uploadHandoff()` does `map_vram_write` + memcpy + `end_vram_write` + a TEXFLUSH write (:779-788). It runs immediately if the backend is initialized, otherwise lazily on `ensureInit`.
- Register access:
  - `get_register_state()` (hpp:289; RegisterState :36-60: ctx[2] regs, PRIM, RGBAQ, ST, UV, FOG, PRMODECONT, TEXCLUT, TEXA, FOGCOL, DIMX, DTHE, COLCLAMP, PABE, BITBLTBUF/TRXPOS/TRXREG/TRXDIR, SCANMSK, internal_q, cached_cbp[2]).
  - `get_priv_register_state()` (:292; struct :70-108).
  - `get_gif_path(i)` (:295; GIFPath{tag, reg, loop} :63-68).
  - `clobber_register_state()` (:287, cpp:4276-4284) marks all state dirty.
  - `reset_context_state()` (:256, cpp:26-38) flushes, then zeroes registers, paths and the vertex queue.
  - `flush()` (:285, cpp:4267-4274).
  - `vsync()` (:298, cpp:4636).
  - `read_transfer_fifo()` (:304, cpp:3160).
- The wrapper's per-pixel `ReadVram`/`WriteVram` are unsupported stubs (ps2_gs_parallel_backend.cpp:459-468). Only whole-VRAM snapshot and hand-off work.
- **Existing precedent:** `GS::setRasterBackend` already does old backend `SnapshotVram` → `m_localMemoryStorage` → new backend `Initialize` (gs_frontend.cpp:2283-2323). Don't use it directly for restore: it overwrites `m_localMemoryStorage` with the old backend's VRAM (:2310-2316). Restore needs a small new worker-side RPC: memcpy into `m_localMemoryStorage`, `m_backend->Initialize(...)`, then set the register state.

**Queue drain.** `GS::drainQueue()` (gs_frontend.cpp:209-235) returns immediately if `GsWorker::isQuiescent()` (gs_worker.cpp:110-114). Otherwise it enqueues a Fence RPC and waits. The worker loop is gs_worker.cpp:116-149. A ready-made stop-the-world hook already runs on the game thread at VBlankStart: `ps2_vq::noteVBlank` (include/ps2_vq.h:141-160: drain, `refreshDisplaySnapshot`, VRAM hash, `presentForDiagnostics`), called at EeScheduler.cpp:2898. `PS2Memory::gsPrivSync()` also drains (ps2_memory.cpp:1086-1090). Every backend call must run on the one worker thread when paraLLEl is live (ps2_runtime.cpp:1206-1225).

**Host-side GS state that exists**
- **Privileged regs:** `gs_regs` (ps2_memory.h:192-216). With the queue on, guest stores are applied by the worker in stream order (`gsPrivStore` → `GS::privWrite`, ps2_memory.cpp:1017-1084; gs_frontend.cpp:1600-1614). paraLLEl gets a copy only at present (`syncPriv`, ps2_gs_parallel_backend.cpp:790-818). CSR is atomic; its vblank bits are set by `ps2xGsCsrVBlankStart` (EeScheduler.cpp:2900).
- **Context/latch regs:** two decoders run side by side.
  - The frontend decodes every packet: m_ctx, PRIM, RGBAQ, UV, transfer regs, vertex queue (gs_frontend.h:256-287; gs_frontend.cpp:1091-1211). It still runs on paraLLEl for CSR/transfer/preferred-source state (:1115-1118).
  - paraLLEl decodes the same raw stream into its own RegisterState, paths[4], vertex_queue and transfer_state (pgs/gs/gs_interface.hpp:331-348, 600, 612).
  - HLE register writes feed both (gs_frontend.cpp:1590-1593).
- **Pending GIF packet state:**
  - The frontend has no partial-packet state across calls; each call decodes a whole buffer (gs_frontend.cpp:1145-1211).
  - Pending state lives in `m_path3MaskedFifo`, `m_vif1PendingPath2ImageQwc`, the arbiter queue, the CPU backend's `m_transferState` and paraLLEl's `paths[]`/`transfer_state`.

### 3. Host threads in scope
| thread | created at | owns | how to quiesce |
|---|---|---|---|
| GameThread | ps2_runtime.cpp:4063 (pthread) or :4085 | EE/EeScheduler, all PS2Memory state, VIF/DMA/GIF arbiter, VU0 and **VU1 (synchronous: MSCAL/MSCNT callbacks ps2_runtime.cpp:1251-1286, CMSAR1 start :2928-2939)**; the GS frontend and backend too when the queue is off | Park at the dispatcher or VBlankStart (EeScheduler.cpp:2880-2900). This thread performs the save itself. |
| GsWorker | gs_worker.cpp:23 (only with PS2X_GS_QUEUE=1 or PS2X_GS_BACKEND=parallel, ps2_runtime.cpp:1196-1221) | GS frontend state, backend (CPU VRAM writes / all Vulkan), gs_regs PrivWrite application, CSR SIGNAL/FINISH | From the game thread, `m_gs.drainQueue()`. Once the game thread (the only guest producer) is parked, the worker is idle. Do the VRAM snapshot/restore as a worker RPC (`RefreshSnapshot` path, gs_frontend.cpp:416-418 → `snapshotVRAM` :536-548). |
| Main / render thread | `PS2Runtime::run` loop, ps2_runtime.cpp:4095-4295 | raylib texture, UploadFrame statics, pad latch/vpad publish, debug UI | Present is a `LatchPresent` RPC into the same queue (ps2_runtime.cpp:808 → gs_frontend.cpp:937-996). It is serialized with the stream and doesn't write VRAM or priv regs (ps2_vq.h:15-17). For restore, gate UploadFrame (or restore before presents start), then reset `s_lastPresentationTick`. With the queue off, present runs directly on this thread under `m_backendLifetimeMutex` alongside the game thread. |
| (no VU1 thread) | – | – | The only `std::thread`/`pthread_create` sites in scope are gs_worker.cpp:23 and ps2_runtime.cpp:4063/4085. |

Adjacent but out of scope: the IOP host, audio output (raylib callback) and pad backends may have their own threads.

### 4. Likely blockers and gaps
1. **Hidden paraLLEl GS state with no public accessor (B).** A fork patch is allowed; this is the main work item.
   - **The CLUT buffer lives on the GPU, outside VRAM** (pgs/gs/gs_renderer.hpp:400). `RegisterState::cached_cbp` (gs_interface.hpp:58) makes CLD=4/5 skip the reload when CBP matches (pgs/gs/gs_interface.cpp:578-582). If `cached_cbp` is restored without the CLUT, restored draws sample an empty palette. If it is zeroed, CLD 4/5 reloads, but CLD=0 draws after load still use the empty CLUT. Needs a fork API to read and upload the CLUT, or a save point after the game reloads its palettes.
   - `vertex_queue` (hpp:593-600) and `transfer_state` (host_to_local_active, payload, hpp:331-341) are private. Either save only when `vertex_queue.count==0` and no transfer is active, or add accessors.
   - `paths[]` can be reached through `get_gif_path()`. Assert `loop==0` at save.
2. **Super-sampling and hi-res scanout state is not in VRAM (B for bit-exact).** Host VRAM upload clears the SS planes (gs_renderer.cpp:1566-1574). Promoted backbuffers (hpp:624) are dropped. Output is only bit-exact at SSAA=1, or after one fully redrawn frame; watch for effects that read back the previous frame.
3. **Two GS decoders must be restored consistently.** The frontend's decoded `GSContext` can't regenerate paraLLEl's raw `RegisterState`. Replaying through `write_register` has side effects (TEX0 → CLUT upload, TRXDIR → transfer start, gs_interface.cpp:550+). Save paraLLEl's `RegisterState`, priv regs and paths directly, restore them after `Initialize`/`uploadHandoff`, then call `clobber_register_state()`. Also note `Reset()` → `reset_context_state()` zeroes them (ps2_gs_parallel_backend.cpp:262-266; gs_interface.cpp:26-38).
4. **Stub globals in `Helpers/Support.h` are per-TU copies (B, design).** They sit in anonymous namespaces (Support.h:4, 584, 608, 1487) in a header included through Common.h by about 29 Kernel TUs, and the Kernel sources are not unity-built (CMakeLists.txt:587-588). So g_gparam, g_file_map (FILE* host handles, :558-560), g_dmaPendingPolls (:1236) and the CD state (:17-35) have one copy per TU, with no central registry. FILE* handles need reopening by path. Mostly outside this scope, but a full save state needs it.
5. **The VU1Interpreter needs a field-wise serializer.** Pointers are interleaved with POD (ps2_vu1.h:299-420). Not a real blocker. After restoring VU code bytes, bump `markVU1CodeModified()`: `VU1Interpreter::reset()` (ps2_vu1_core.cpp:106-117) does not clear the decode or recomp caches.
6. **The GS queue can't be serialized** (GsCommand holds std::function and shared_ptr, gs_worker.h:112-115). Save only after `drainQueue()`. The same applies to the PrivWrite lambdas, so gs_regs is only stable after a drain.
7. **Pipelined present latency** (m_rb, ps2_gs_parallel_backend.cpp:360-387): the first present after a restore is empty. This is host-only, but affects frame-compare tests.
8. **Out of scope but required:** EeScheduler (thread contexts, events, vsync tick, callbacks), IOP/SIF, audio/SPU, pad.
9. **No real blocker for the CPU backend.** The full GS state is flat 4 MiB VRAM + gs_regs + the POD frontend fields + CPU backend transfer state.
