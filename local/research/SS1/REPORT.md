# SS1: save states for the recomp runtime (Opus spike)

Worker: Claude Code (Opus 5.5), Mac mini, 2026-09-25. Brief: `local/muse/prompts/SS1.md`.
Fork worktree `~/dev/ssx3-work/SS1/PS2Recomp`, local branch `ss1-savestate` from `ssx3` `a3efbfe`.
The orchestrator decides; this report hands back tables.

## Stage 1: inventory and design (committed before any code)

### Build 1 (control, unchanged source)

| Item | Value |
| --- | --- |
| Configure | F5 recipe with `PS2X_ENABLE_DET_HASH_TAP=ON`, `PS2X_VU1_RECOMP_DIR=~/dev/ssx3-work/vu1gen-ssx3` (7 images), paraLLEl `~/dev/ssx3-work/F2/parallel-gs` @ `19d93b2` |
| Build | cold, `--parallel 8`, **227 s** wall (1298 s user) |
| Runner | `bin/runner-det0` SHA-256 `119389a74f857e56460ef448e23563d464528db9a819b249049693e563993c38` (2 reads). **Byte-identical to F5's `runner-det`** |
| Suite | `ps2x_tests` from the worktree root: **658/658** |

### Why it is feasible

A guest thread never keeps guest state on the host stack across a yield. A checkpoint throws
`EeDispatcherTransfer` (or unwinds by returning, PF1) back to `EeScheduler::run()`
(`EeScheduler.cpp:911-917`), and the thread resumes from `R5900Context.pc`. `R5900Context`
(`ps2_runtime.h:58-195`) is plain data. VU1 runs synchronously on the game thread (no VU1 thread).
The GS worker is the only other thread that holds guest-derived state, and it can be drained
(`GS::drainQueue`, `gs_frontend.cpp:209`). So at a vsync boundary in `run()`, the whole machine is data
held in the runtime's own objects.

### Inventory (owner, file:line, plan)

Plans: **C** = captured in the file. **R** = rebuilt or dropped on load. **Q** = must be empty or idle
at the save point: the save is deferred to the next vsync while it isn't, and the log names the
reason. **B** = blocker. Paths are relative to `ps2xRuntime/`. Per-subsystem detail, with every
member and static: `inventory-kernel.md`, `inventory-mem-vu-gs.md`, `inventory-iop.md` (three
read-only subagent reads, spot-checked).

| # | State | Owner (file:line) | Plan |
| --- | --- | --- | --- |
| 1 | EE RDRAM 32 MiB, scratchpad 16 KiB, IOP RAM 2 MiB | `PS2Memory` `ps2_memory.h:380-386` | C (bytes) |
| 2 | VU0/VU1 code + data (4K/4K/16K/16K) | `ps2_memory.h:422-425` | C. After load, `markVU0/1CodeModified` invalidates the decode and recomp caches (`:457-458`) |
| 3 | IO registers (DMAC channels, D_STAT/PCR, INTC, IPU) | `m_ioRegisters` `ps2_memory.h:396` | C (unordered_map, sorted pairs) |
| 4 | VIF0/VIF1 regs, PATH2 image continuation, PATH3 masked FIFO | `ps2_memory.h:401-402, 426-429` | C |
| 5 | Pending GIF/VIF transfers, completed DMAC causes | `ps2_memory.h:441-445` | Q (drained synchronously; asserted empty) |
| 6 | TLB, EE timers (count/mode/compare/hold/remainder), code-region SMC bitmap | `ps2_memory.h:414, 462-471, 453` | C |
| 7 | GS privileged regs (PMODE…BGCOLOR, CSR, IMR, SIGLBLID), mirrored `vsyncTick` | `GSRegisters` `ps2_memory.h:192-216` | C after a GS drain |
| 8 | Scheduler: threads (ctx, status, priority, waits), ready queues, semas, event flags, alarms, INTC/DMAC handlers, id counters, masks, cycle/count/slice, deadlines, pending invocations, sequences, vsync tick, vsync flag/callback addresses, invocation stack tops | `ee_scheduler.h:418-485` | C. `unordered_map` iteration order is guest-visible (`acquireInvocationThread`, `EeScheduler.cpp:2541-2549`), so maps are stored with their bucket count and iteration order and rebuilt in the same order (unit test) |
| 9 | Deadline host times, vsync pacer | `ScheduledEvent::hostDeadline` `ee_scheduler.h:374`, `Pacer` `ps2_vsync_pacer.h:79-80` | R. Rebased to load-time `now` plus the saved offset; the pacer is reset as in `reset()` (`:514`). Deterministic mode ignores host time when choosing events (`:2756-2767`) |
| 10 | **Host closures**: `EeWaitState::completion`, `GuestThread::resumeCompletion`, `GuestInvocation::onComplete` | `ee_scheduler.h:82, 102, 124`. 11 creation sites (`inventory-kernel.md` §2) | Q in general. **C via a tagged descriptor** for `sceCdStRead`'s vsync wait (`CD.cpp:1002-1012`; POD continuation of 4×u32), the one most likely live mid-race. Other kinds defer the save and are named in the log |
| 11 | PS2Runtime kernel side: exit handlers, syscall overrides + mirrors, guest heap blocks/base/end/limit, async-callback stack floor/top, loaded modules | `ps2_runtime.h:530-545, 581` | C |
| 12 | VU1 interpreter: VU1State, m_cycle, all pipelines/latest-write/ready tables, XGKICK packet (64 KiB), direct-commit state | `ps2_vu1.h:295-352, 314, 416-418` | C field by field (pointer members are interleaved). Decode/recomp/direct-flag caches R (keyed by the code generation) |
| 13 | VU0 | `ps2_runtime.cpp:2881-2887` | R: reloaded from the `R5900Context` on every microprogram call |
| 14 | GS frontend decoded state: 2 contexts, PRIM/PRMODE, RGBAQ/ST/UV/FOG latches, TEXA/TEXCLUT/DIMX/…, transfer regs, vertex queue, preferred display source | `gs_frontend.h:256-294` | C, on the GS worker thread after a drain |
| 15 | GS VRAM 4 MiB. CPU backend: `PS2Memory::m_gsVRAM`. paraLLEl: GPU buffer + host mirror | `ps2_memory.cpp:518`; `pgs/gs/gs_renderer.hpp:398-402` | C. paraLLEl: `map_vram_read` / `map_vram_write`+`end_vram_write` (`gs_interface.hpp:281-283`), on the worker |
| 16 | paraLLEl register state, priv state, GIF paths | `gs_interface.hpp:289-296` (mutable refs) | C (trivially-copyable structs), then `clobber_register_state()` |
| 17 | paraLLEl CLUT buffer (GPU, outside VRAM), private vertex queue / transfer state, SSAA planes | `gs_renderer.hpp:400`; `gs_interface.hpp:331-348, 593-600` | R. CLUT is stale until the guest's next CLUT load; `cached_cbp` is cleared to force the CLD 4/5 reloads. The vertex queue and transfer state are assumed idle at a drained vsync. Exact fix = a paraLLEl accessor (not in this spike). Checked by the t2100 frame |
| 18 | CPU GS backend transfer state | `gs_cpu_backend.h:80-83` | Q (idle) |
| 19 | GS worker queue, GIF arbiter queue | `gs_worker.h:161-179`, `ps2_gif_arbiter.h:51` | Q (drained; asserted empty) |
| 20 | SIF regs/sregs, cmd handlers, heap allocations, **IOP heap storage 5 MiB**, cmd buffers, DMA transfer id, `g_iopHeapNext` | `Stubs/SIF.cpp:62-72`, `Support.h:35` | C |
| 21 | RPC servers/clients, pool indices, bootmode, TLS index, OSD config, SIF modules | `Syscalls/Helpers/State.h:212-239, 355-357` | C |
| 22 | CD: files-by-key + pseudo LBNs, error, mode, init, streaming LBN/end, stream timing, callback fn/gp/stack | `Support.h:17-30` (**per-TU copy**), `CD.cpp:19-42` | C |
| 23 | **Per-TU `Support.h` globals** (anonymous namespace in a header included by ~29 Stubs TUs, not unity-built) | `Support.h:4-35, 558-560, 1236, 1597` | C: every TU registers its own copy through a static registrar in the header, keyed by TU name |
| 24 | fio fds, libc `FILE*` map, IOP host files | `State.h:6`, `Support.h:558`, `ps2_iop_host.h:101` | Q (no path/offset recorded; must be closed) |
| 25 | Memory card: fds, last cmd/result/pending, ports, cursor; card contents on disk | `MemoryCard.cpp:89-95`, `getMcRootPath` `:118` | C for the POD. Fds Q. The card dir is snapshotted with the state (empty under FR1-R1) |
| 26 | Pad: ports, override, `scePadGetFrameCount` counter, pad latch | `Pad.cpp:53-75, 1008`; `ps2_pad_latch.h:91-98` | C. The pad script has no cursor: it recomputes from `gs().vsyncTick` (`Pad.cpp:510-513, 896-898`), so it needs only the same env |
| 27 | SND HLE: handler/status/serial/counters incl. **cid0**, doneRing, iopMem, SPU (2 MiB RAM, 48 voices), driver, upsamplers | `include/ps2_snd_spike.h:76-95`, `ps2_snd_spu.h` | C. Log/dump FILEs and the PCM ring + host output R |
| 28 | Audio stub (libsd) state, DMA env + pending polls, `g_gparam`, `g_wiredAlloc` | `Stubs/Audio.cpp:21-50`, `DMA.cpp:36`, `Support.h:1236, 1597`, `Ssx3CopiedPayload.cpp:41` | C |
| 29 | MPEG/IPU: FFmpeg decoder, playback state, non-stream deliveries | `MPEG.cpp:470-473, 648-723` | Q (no decoder or delivery live; a race plays no movie). A true blocker only for saves during a movie |
| 30 | libc `std::rand` | `LibC.cpp:1255-1262` | Q/B-lite: host libc state is opaque. Checked as unused before the save |
| 31 | Diagnostics (e3/e4/e7/e41/e44 traces, park, gfx stats, det-hash line cap, log caps) | many; statics census below | R / off |
| 32 | Host GPU/present objects, raylib texture, UploadFrame latch, HR1 readback ring | `ps2_runtime.cpp:774-783`; `ps2_gs_parallel_backend.cpp:826-845` | R (the first present after a load is empty) |

### Statics census

`llvm-nm` on the bitcode objects of `libps2_runtime.a` + `libps2_gs_shadow.a` (the Xcode `nm` can't
read LLVM 23 bitcode), plus `nm -m` on the linked runner for header-inline statics:

| Class | Count | Examples | Plan |
| --- | ---: | --- | --- |
| Writable data symbols (runtime lib, excl. guard vars/strings/tables) | 474 | | |
| — sync/registry (mutexes, once, registries) | 101 | `g_rpc_mutex`, `registryMutex` | R |
| — diagnostics / log caps / env caches | 126 | `ps2_e3::*`, `warnCount`, `diagPeriodMs` | R/off. `scePadGetFrameCount::frameCount` is guest-visible (moved to C) |
| — candidate guest-affecting | 247 | 7 `Support.h` globals × ~29 TUs, SIF/MC/Pad/CD/Audio/MPEG state | covered by rows 20-30 |
| Header-inline statics in the runner (weak) | – | `ps2_snd_spike::state()::s`, `pcmRing()::ring`, `padlatch::sharedLatch()::latch`, `ps2_uv1_dma_stall::state()::s` | rows 26-27; `uv1_dma_stall` is diagnostic |
| `__DATA,__common` (third-party: GLAD, raylib, glfw) | 1937 | `_CORE`, `_GLAD_GL_*` | R (host) |

Receipts: `ss1-statics-census.tsv` (all 474 rows: lib, object, nm class, demangled name).

### Blockers

**No true blocker for a vsync save in a race.** Items that would block a save *at an arbitrary point*
are handled by deferring (Q): unregistered host closures (row 10), an open host file (24), a live
movie decoder (29). The save lands at the first vsync ≥ the requested tick where they are all idle,
and the log names the tick and anything that deferred it. Exactness gaps outside the det-hash: the
paraLLEl CLUT/SSAA (row 17). SPU/pad/GS VRAM are captured, so they are checked separately (cid0
progression, frame view).

### Design

- **Save point.** In `EeScheduler::run()`, right after `processPendingEvents()`
  (`EeScheduler.cpp:566-570`), once `m_vsyncTick >= PS2X_SAVESTATE_SAVE_AT` and the Q items are idle.
  No guest frame is on the host stack there, events are drained, and the tick's det-hash line is
  already out. On load, the first loop iteration skips `processPendingEvents()`, so both runs execute
  the same next step.
- **Load point.** In the game thread, after `m_eeScheduler->reset()` and before `run()`
  (`ps2_runtime.cpp:4034-4035`), so the ELF load, IOP/SIF/stub resets and GS/backend init have run.
  The load overwrites them. GS VRAM and backend state are written on the GS worker via a `PrivWrite`
  closure, then a fence.
- **File.** `ps2x-savestate` magic plus format version 1. A header holds the runner SHA-256 (computed
  from the executable), the ELF SHA-256, the ISO path and size, PS2X_DETERMINISTIC, the pad-script
  hash, the GS backend, the det-hash flag and the save tick. Tagged sections (`tag, u32 version, u64
  size, bytes`) follow, one per subsystem. **The load refuses on any header mismatch.** The file holds
  game RAM, so it lives only in scratch.
- **Knobs (default off).** `PS2X_SAVESTATE_SAVE_AT=<tick>` + `PS2X_SAVESTATE_PATH=<file>` (+
  dev-only `PS2X_SAVESTATE_EXIT_AFTER_SAVE=1`); `PS2X_SAVESTATE_LOAD=<file>`. Requires
  `PS2X_DETERMINISTIC=1`. Unset = no code path changes (one getenv at `run()` start).
- **Unit tests** for the writer/reader, the ordered-map round trip (iteration order and later
  inserts), the scheduler and VU1 round trips, and the header refusal.
