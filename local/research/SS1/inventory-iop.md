# SS1 inventory: IOP HLE, CD, file IO, MC, pad, sound, MPEG

Read-only subagent read for SS1 (Opus); file:line against fork a3efbfe, paths relative to ps2xRuntime/.

## Save-state inventory: HLE and stub state in ps2xRuntime (SS1 checkout)

Read-only. Nothing was edited, built or run. Paths are relative to `/Users/brad/dev/ssx3-work/SS1/PS2Recomp/ps2xRuntime`.

### 0. Findings that affect the whole design

- **Some "globals" exist once per source file.** `Stubs/Helpers/Support.h` declares its variables in an anonymous namespace (Support.h:4-35, 558-560, 1225-1237, 1597). `Stubs/Common.h:30` includes it in every `Stubs/*.cpp`, and `ps2_runtime` is not a unity build (CMakeLists.txt:587-593; unity is only on `ps2EntryRunner`/`ps2_game_objects`, :634, :690). So each Stubs file has its own copy. Save/restore code has to run inside the file that changes each copy:
  - CD.cpp: `g_cdFilesByKey`, `g_nextPseudoLbn`, `g_cdStreaming*`, `g_lastCdError`, `g_cdMode`, `g_cdInitialized`
  - SIF.cpp: `g_iopHeapNext`
  - LibC.cpp: `g_file_map`
  - DMA.cpp: `g_dmaPendingPolls`
  - GS.cpp: `g_gparam`

  `Syscalls/Helpers/State.h` uses C++17 `inline` variables, so there is one copy there.
- **Paused host code (C++ callbacks/lambdas) is the main blocker.** Guest waits and nested calls keep `std::function` callbacks that capture host pointers:
  - `EeWaitState::completion` (ee_scheduler.h:82)
  - `GuestInvocation::onComplete` (:102)
  - `GuestThread::resumeCompletion` / `invocations` (:124-125)

  The in-scope code that creates them:
  - CD.cpp:1002-1011: `sceCdStRead` blocking wait. It captures `rdram`, `runtime` and a plain-data `CdStReadContinuation`.
  - MPEG.cpp:1876 (free callback data), 1922-1936 (non-stream callback chain), 2760 (`GetPicture` vsync wait).
  - RPC.cpp:779-783 (end-function callback), 798-802 (server dispatch).
  - IPU.cpp:86-90 (init only).

  None of these can be serialized as they are. Two options:
  - (a) Only save when every thread's `invocations` list is empty and each `wait.completion` is empty or of a known kind.
  - (b) Replace them with a tagged "kind" plus plain arguments. The CD case is easy because its state is already plain data.

  The plain queued invocations carry no callback, so they can be captured as data: the CD callback (CD.cpp:69-90) and the SND handler calls (ps2_snd_spike.h:352-363).
- **There are two vsync clocks, and both must be restored.**
  - `EeScheduler::m_vsyncTick` (ee_scheduler.h:470) drives CD streaming (CD.cpp:93-96, 148-154) and MPEG (MPEG.cpp:2899).
  - `PS2Memory::gs().vsyncTick` (runtime/ps2_memory.h:210) drives the pad script (Pad.cpp:896-898).
  - Scheduler state outside my scope that still has to be captured: `m_events` (ee_scheduler.h:465, which includes the `SoundTick` event type, :235), `m_pendingInvocations` (:467), and the guest heap (`m_guestHeapBlocks`/Base/End/Limit, ps2_runtime.h:535-540; the `malloc` stubs use it, LibC.cpp:53-90).

### 1. Mutable state, by subsystem

"Host?" says whether the item holds a host pointer (ptr), file handle (fd), host thread (thr) or host time (time). Mutexes are left out: none is held at a vsync boundary. Log-only counters are listed once at the end of the section they belong to.

**SIF / RPC**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| g_sifRegs / g_sifSregs | Stubs/SIF.cpp:65-66 | unordered_map<u32,u32> | – | captured | reset at :87-96; guest polls sregs |
| g_sifCmdHandlers | SIF.cpp:67 | map cid→guest fn | – | captured | |
| g_sifHeapAllocations | SIF.cpp:68 | map addr→size | – | captured | |
| **g_sifHeapStorage** | SIF.cpp:69 | array<u8,0x500000> | – | captured | real IOP-heap memory, read/written via readSifIopHeap (SIF.cpp:417+) and the IOP host (ps2_iop_host.cpp:231); save only the allocated ranges |
| g_sifCmdBuffer / SysCmdBuffer / CmdInitialized | SIF.cpp:70-72 | u32/bool | – | captured | |
| g_nextSifDmaTransferId | SIF.cpp:62 | u32 | – | captured | returned to the guest (SIF.cpp:126) |
| g_iopHeapNext | Support.h:35 (SIF.cpp's copy) | u32 | – | captured | |
| g_rpc_servers / g_rpc_clients | Syscalls/Helpers/State.h:212-213 | maps of guest addresses | – | captured | |
| g_rpc_next_id / packet_index / server_index / active_queue / initialized | State.h:218-222 | u32/bool | – | captured | pool slots are guest-visible (Helpers/Runtime.h:121-137) |
| g_sif_rpc_debug_history / next_seq | State.h:214-215 | ring, holds `const char* op` | ptr | rebuildable | diagnostics only; clear on load |
| g_sif_modules_by_id / id_by_path / next id | State.h:355-357 | maps + strings | – | captured | module ids are returned to the guest |
| g_bootmode_*, g_tls_index, g_osd_* | State.h:224-239 | POD + map | – | captured | |
| g_ssx3SifHandshakeEnabled | RPC.cpp:165 | atomic<bool> | – | rebuildable | set by the game-override hook at load |
| log counters | RPC.cpp:112, 1154, 1164; SIF.cpp:73-74, 609, 634, 973 | static | – | rebuildable | |

**IOP host adapter / ps2xIOP**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| m_hostFiles | src/lib/ps2_iop_host.h:101 | map<u64,{FILE*,size}> | fd | **needs change** | the path is not stored (ps2_iop_host.cpp:325-350); add path + offset |
| m_nextHostFileHandle, m_nextToken | ps2_iop_host.h:102, 94 | u64 | – | captured | |
| m_activeContext / m_activeRdram / m_activeToken | ps2_iop_host.h:91-93 | ptr | ptr | rebuildable | only set inside a CallScope; null at a vsync boundary |
| ps2xIOP module state (TSNDDRV, CRI DTX, CLFILE, SDRDRV, mcserv) | ../ps2xIOP/src/modules/* | module objects | ? | likely inert | builtin_profiles.cpp:108-148 has no SLUS_207.72 profile; check `iopDebugSnapshot()` shows no active service for SSX 3 |

**CDVD**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| **g_cdFilesByKey + g_nextPseudoLbn** | Support.h:17, 22 (CD.cpp's copy) | map key→{hostPath, size, baseLbn, sectors} | path | captured | pseudo LBNs depend on the order files were first looked up (Support.h:394-401), and the guest holds them (CD.cpp:856). Save key, relative path, LBN and sectors |
| g_cdLeafIndex / LoosePathIndex / Root / Built | Support.h:18-21 | path caches | path | rebuildable | |
| g_cdImageSize* | Support.h:23-25 | cache | path | rebuildable | |
| g_lastCdError, g_cdMode, g_cdInitialized | Support.h:26-27, 30 | POD | – | captured | |
| g_cdStreamingLbn / EndLbn | Support.h:28-29 | u32 | – | captured | read position (CD.cpp:530-533) |
| g_cdStreamTiming | CD.cpp:19-35 | struct (produced/consumed/remainder/lastVSyncTick) | – | captured | runs on the scheduler vsync tick, so it is deterministic |
| g_cdCallbackFn / Gp / StackTop | CD.cpp:40-42 | u32 | – | captured | |
| sceCdStRead blocked thread | CD.cpp:921-927, 1002-1011 | waitVSync callback | ptr | **needs change** | likely to be live during streaming; convert to a tagged continuation |
| ISO / file handle | Support.h:421 | ifstream opened per read | – | nothing to do | no persistent handle; reads happen on the game thread |
| log statics | CD.cpp:34, 378, 415, 758, 774, 796, 816-817 | static | – | rebuildable | |

**File IO**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| g_fileDescriptors / g_nextFd | State.h:6-7 | map<int,FILE*> | fd | **needs change** | the path is not recorded at fioOpen (Syscalls/FileIO.cpp:104); add path, mode and ftell |
| g_vagAccum | Syscalls/FileIO.cpp:41 | map fd→bytes | – | captured or dropped | only feeds the host-side legacy audio backend (:163-167) |
| host process cwd | Syscalls/FileIO.cpp:453 | `current_path()` | host | captured | fioChdir changes the process cwd; also g_host_cwd / g_cdrom_cwd / g_ps2_cwd_device (State.h:243-247) |
| g_file_map / g_next_file_handle | Support.h:558-559 (LibC.cpp's copy) | map<u32,FILE*> | fd | **needs change** | libc fopen stub (LibC.cpp:866-872) keeps no path |
| Stubs/FileIO.cpp | :8-171 | — | – | nothing to do | stateless forwarders (log counter at :163) |

**Memory card**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| g_mcFiles | MemoryCard.cpp:93 (McOpenFile :75-80) | map fd→{FILE*, port, hostPath} | fd | captured (reopen + seek) | path is stored; save ftell |
| g_mcNextFd / LastCmd / CommandPending / LastResult | MemoryCard.cpp:89-92 | POD | – | captured | sceMcSync reads the pending flag (:1225-1240) |
| g_mcPorts (currentDir, formatted) | MemoryCard.cpp:94, 81-85 | array | – | captured | |
| g_cvMcFileCursor | MemoryCard.cpp:95 | i32 | – | captured | |
| card contents on disk | getMcRootPath MemoryCard.cpp:118 | host dir | fd | snapshot alongside the state | otherwise a load after a save diverges |
| getdir timestamps | MemoryCard.cpp:269-271, 776 | wall clock | time | determinism caveat | guest-visible host time |

**Pad**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| g_padPorts[2] | Pad.cpp:53-72, 75 | struct (open, analogMode, dmaAddr, reqState, lastData[32], readCount…) | – | captured | |
| g_padOverrideEnabled / State | Pad.cpp:73-74 | POD | – | captured | debug override API (:1472-1487) |
| **scePadGetFrameCount counter** | Pad.cpp:1008 | static atomic<u32> inside the function | – | captured (move it to file scope) | guest-visible |
| g_padScript | Pad.cpp:313-330 | struct (entries, vsyncClock, startWall, logged flags) | time (wall mode) | rebuildable | see section 3 |
| g_padStim | Pad.cpp:83-99 | struct with steady_clock start | time | unsupported | dev-only PS2X_PAD_STIM_AFTER; wall-clock gated |
| padlatch Latch (live, pendDown/Up, owedDown/Up, shown) | include/ps2_pad_latch.h:91-98, 212-215 | 6×u16 | thr | captured | on by default (:37-45); the game thread reads it once per port-0 read (ps2_pad.cpp:161-166) |
| vpad liveMask / liveStick | include/ps2_virtual_pad.h:256-259, 437-440 | static atomics | thr | rebuildable | published by the render thread from host input |
| ps2_pad.cpp s_last | ps2_pad.cpp:190 | static | – | rebuildable | log only |

**Sound (SND HLE / SPU / output)**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| ps2_snd_spike::State handler / handlerData / handlerGp / statusAddr | include/ps2_snd_spike.h:84-85 | u32 | – | captured | |
| serial | spike.h:86 | u32 | – | captured | written to the guest status block (:388-390) |
| ticks, **cid0**, dmq, done, setdma, tagbufs | spike.h:87 | u64 | – | captured | `cid0` is incremented in onSendCmd (:521). The others are counters, but `tagbufs` affects dump gating |
| doneRing | spike.h:88 | u32 | – | captured | chooses the guest packet slot (:547) |
| iopMem | spike.h:89 | map<IOP addr, bytes> | – | captured | source for SPU uploads (:531-543) |
| spu (m_ram 2 MiB, m_voices[48] incl. ADSR/ADPCM hist/counter, upload counters) | include/ps2_snd_spu.h:77-83, 157-172, 375-377 | POD + vector | – | captured | |
| driver (m_word, status arrays, pitch, vol, keyOns) | ps2_snd_spu.h:455-460 | arrays | – | captured | goes into the guest status (spike.h:395-397) |
| upLeft / upRight m_history | ps2_snd_spu.h:482; spike.h:95 | i32 | – | captured | |
| voices flag, init/enabled | spike.h:76-77, 90 | bool | – | rebuildable | from env (:273-289) |
| log / tag1File / mixRaw / dumpDir + byte counters | spike.h:78-83, 91-92 | FILE*, string | fd | rebuildable | diagnostics only |
| PcmRing | spike.h:195-243 | 32k atomic frames + read/write | thr | rebuildable | host-only; clear on load |
| g_output (AudioStream, resample phase/previous/next, wav) | ps2_snd_audio_output.cpp:21-36 | struct | thr, fd, time | rebuildable | host-only |
| Audio stub libsd state (voice/block transfers) | Stubs/Audio.cpp:21-50 | POD | – | captured | |
| PS2AudioBackend (sampleBank, loadOrder, activeSounds raylib Sound) | include/runtime/ps2_audio.h:36-41; ps2_audio.cpp:79 | host handles | ptr | rebuildable | host playback only (stopAll); only reached through IOP audioCommand |

**MPEG / IPU / movie**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| FFmpeg decoder (AVCodecContext / AVFrame / AVPacket / SwsContext) | MPEG.cpp:470-473, held at :665 | host lib state | ptr | **blocker** | reference frames can't be captured; only save when `playbackByMpeg` has no decoder |
| MpegPlaybackState (buffers, decodedFrames, timing Q32) | MPEG.cpp:648-676 | vectors/deque/POD | – | captured if no decoder | |
| MpegStubState (nextCallbackHandle, cdStream generation/bytes/EOF, callbacksByMpeg) | MPEG.cpp:705-722, 728 | POD + maps | – | captured | trace counters rebuildable |
| nonStreamDeliveries | MPEG.cpp:691-703, 723 | weak_ptr + runtime ptr | ptr | blocker mid-delivery | |
| s_vectorRan / s_warnedNoFfmpeg / log statics | MPEG.cpp:501, 614, 100, 174-175, 356, 380, 2162, 2494 | static | – | rebuildable | |
| g_ssx3movie_invocations | Ssx3Movie.cpp:10 | atomic counter | – | rebuildable | diagnostics |
| IPU stub | IPU.cpp:1-110 | none (registers live in PS2Memory) | – | nothing to do | init-only callback at :86-90 |

**Font / libc / other stubs**
| item | file:line | type | host? | plan | notes |
|---|---|---|---|---|---|
| Font | Font.cpp:7-16 and throughout | none | – | nothing to do | writes only to guest RAM |
| **std::rand state** | LibC.cpp:1255-1262 | host libc | host | **blocker-lite** | libc's rand state can't be read. Swap in our own LCG (small change) or show SSX 3 never calls this stub |
| malloc stubs | LibC.cpp:53-90 | → PS2Runtime heap | – | captured | outside my scope, see section 0 |
| s_warnCounts, g_printfLogCount, g_stubWarningCount | LibC.cpp:21; Support.h:1225, 1229 | counters | – | rebuildable | |
| g_dmaCurrentEnv | DMA.cpp:36 | struct | – | captured | |
| g_dmaPendingPolls | Support.h:1236 (DMA.cpp's copy, :1401-1475) | map | – | captured | |
| g_gparam | Support.h:1597 (GS.cpp's copy, :822-824) | struct | – | captured | |
| sceCdReadClock | CD.cpp:705-725 | wall clock unless PS2X_DETERMINISTIC=1 | time | set PS2X_DETERMINISTIC | |

### 2. Host threads in scope

- **Game thread** (ps2_runtime.cpp:4052-4085): runs `EeScheduler::run()` and every stub. The CD reads happen here synchronously (Support.h:421); there is no CD reader thread. FFmpeg also decodes here, single-threaded (`thread_count=1`, MPEG.cpp:300). The quiesce point is the vsync boundary in `run()`.
- **Audio device callback** (raylib/miniaudio; registered at ps2_snd_audio_output.cpp:176, callback :75): reads only `PcmRing` and `g_output`, and nothing it touches is guest-visible. To quiesce, `PauseAudioStream` or just ignore it; on load, clear the ring and reset phase/havePair.
- **Render / main thread**: publishes host input via `padlatch::sharedLatch().publish` (ps2_pad_latch.h:159-186) and `vpad::liveMask/liveStick`. For bit-exact restores, save when there is no host input (latch live=0, nothing pending/owed) and restore the Latch as plain data.
- Outside my scope but running: the GS worker (PS2X_GS_QUEUE, ps2_runtime.cpp:1196-1200) and the Android logcat thread (main.cpp:48, 79).

### 3. Pad route cursor (PS2X_PAD_SCRIPT, vsync clock)

- There is no stored cursor; the route position is recomputed on every read. `padScriptOnRead` (Pad.cpp:586-642) checks every entry against `nowMs = padScriptNowMsLocked(tick)` (:569-583).
- With `PS2X_PAD_SCRIPT_CLOCK=vsync` (:540-543), `nowMs = tick*100000/5994` (:510-513). `tick` is the absolute `memory().gs().vsyncTick` (:896-898), not "time since the first pad call" as the comment at :303 says. So restoring `gs().vsyncTick` resumes the route at the right tick.
- The entries are parsed from the environment on the first pad read (:544-555). The restored process needs the same `PS2X_PAD_SCRIPT`/`_CLOCK` values.
- `loggedPress`/`loggedDone` (:306-311) only control log lines. Restoring them just avoids duplicate log output.
- In wall-clock mode, `startWall` (:323, 524, 539) is host time, so a restored run starts the route from zero. Only vsync mode supports save-states.

### 4. Blockers (host state that can't be captured as it is)

1. **Host callbacks in waits and invocations** (section 0; CD.cpp:1002, MPEG.cpp:1876/1922/2760, RPC.cpp:779/798, IPU.cpp:86). Fix: allow saves only at quiescent points, or replace the callbacks with tagged kinds. The CD `sceCdStRead` wait is the one most likely to be live mid-race during streaming.
2. **FFmpeg decoder state** (MPEG.cpp:470-473, 665): no saves during movie playback.
3. **FILE\* handles with no recorded path**: `g_fileDescriptors` (State.h:6), `g_file_map` (Support.h:558), `PS2IopHostAdapter::m_hostFiles` (ps2_iop_host.h:101). They can be rebuilt once the open code records path, mode and offset (small change). `g_mcFiles` already stores the path.
4. **libc `std::rand`** (LibC.cpp:1257): opaque; replace with our own PRNG.
5. **Per-file Support.h copies** (section 0): not a blocker, but a single central save function can't reach them. Each owning Stubs file needs an exported save/restore hook.
6. **Host wall time the guest can see**: memory-card getdir times (MemoryCard.cpp:776, 269-271), and `sceCdReadClock` unless `PS2X_DETERMINISTIC=1` (CD.cpp:705-725). This affects determinism, not capture.

Everything else in scope is plain data or maps of guest addresses and can be serialized directly.
