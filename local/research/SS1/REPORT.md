# SS1: save states for the recomp runtime (Opus spike)

Worker: Claude Code (Opus 5.5), Mac mini, 2026-09-25, ~19:03–19:55 EDT. Brief: `local/muse/prompts/SS1.md`,
plus the orchestrator's mid-run design change (runner-SHA mismatch warns, acceptance (d), the
non-deterministic note). Fork worktree `~/dev/ssx3-work/SS1/PS2Recomp`, local branch `ss1-savestate`
from `ssx3` `a3efbfe` (not pushed). The orchestrator decides; this report hands back tables.

## Outcome

**Feasible, and the prototype works.** A det runner saves the whole machine at a vsync boundary. A
fresh process loads it and runs **bit-exactly**: det-hash IDENTICAL for ticks 2001–2600 against a
straight run. The same holds for 938/938 SND events and the `cid0`/tick counters, and 3/3 presented
frames (t2100/2300/2600) are byte-identical. A state saved by runner A loads in runner B (a different
SHA, one unrelated source change) and matches through t2600. A race-start state (t1720) reaches the
race in **1.0 s wall instead of 33.0 s**. Default off: with the knobs unset, the new runner is
det-hash IDENTICAL to F5's B1 over ticks 1–2400.

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
| 25 | Memory card: fds, last cmd/result/pending, ports, cursor; card contents on disk | `MemoryCard.cpp:89-95`, `getMcRootPath` `:118` | C for the POD. Fds Q. The card dir was meant to travel with the state: **not implemented** (see Gaps; empty under FR1-R1) |
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

## Stage 2: prototype (fork `ss1-savestate`, local)

| Commit | What |
| --- | --- |
| `e76a4fc` | Save/load of every inventory row, file format, knobs, tests (31 files, +2,938/−13) |
| `53a1b1d` | MPEG playback bookkeeping saved; a decoder whose stream has ended is dropped (found by boot B; +59/−4) |
| `f1ead87` | Force-link the syscall section (static-library dead strip, found from the section list); validate every section before applying any (+62) |

`git diff --stat a3efbfe HEAD`: 31 files, +3,055/−13 (net). **Nothing under `ps2xRuntime/src/runner/`**
(`--stat` empty). New files: `include/runtime/ps2_savestate.h` (format, Writer/Reader, ordered-map
round trip, registries), `src/lib/ps2_savestate.cpp` (header, SHA-256, orchestration, memory / kernel
/ VU / GS / SND / pad-latch sections), `src/lib/ps2_savestate_internal.h` (friend serializers +
section versions), `src/lib/Kernel/EeSchedulerSavestate.cpp`, `src/lib/Kernel/Syscalls/Savestate.cpp`,
`ps2xTest/src/ps2_savestate_tests.cpp`. Owners gain one friend line or a small section at the end
of their `.cpp`. `Support.h` registers one section per including TU (`__BASE_FILE__` key).

### How it works

- **Knobs (all default off):** `PS2X_SAVESTATE_SAVE_AT=<tick>` + `PS2X_SAVESTATE_PATH=<file>` (+
  dev-only `PS2X_SAVESTATE_EXIT_AFTER_SAVE=1`), `PS2X_SAVESTATE_LOAD=<file>`, `PS2X_SAVESTATE_STRICT=1`.
  Each needs `PS2X_DETERMINISTIC=1`, or it is switched off with one log line. Unset, the per-dispatch
  cost is one bool test and one `u64` compare against 0 in `EeScheduler::run()`.
- **Save point:** `EeScheduler::run()` right after `processPendingEvents()`, at the first
  iteration with `m_vsyncTick >= SAVE_AT` where every readiness check passes. On load, the first
  iteration skips `processPendingEvents()`. The GS worker is drained, and GS + paraLLEl state
  (VRAM via `map_vram_read`/`map_vram_write`, `RegisterState`, `PrivRegisterState`, GIF paths) is
  saved and restored *on the worker* through `GS::privWrite`.
- **Deferral, not failure:** the save waits while any of these is live, and logs
  `[savestate] deferred tick=N reason=…` once per tick: an untagged host closure (named by
  `target_type()`), host events, open fio/libc/IOP-host/memory-card files, DECI2 sessions, pending
  GIF/VIF transfers, host pad input, an MPEG decoder mid-stream, or `std::rand` use.
- **Closures:** `EeCompletionTag {kind, 4×u32}` on waits and resumes. `sceCdStRead`'s vsync wait is
  tagged (kind 1), and its factory rebuilds the same lambda. The other 10 creation sites are
  untagged and defer. None was live at t1720 or t2000.
- **Map order:** `unordered_map`/`set` are stored with their bucket count and iteration order, and
  rebuilt by reverse insertion at the same bucket count. A unit test proves identical iteration
  order, including after 3,000 more mixed inserts/erases with rehashes.
- **File:** `PS2XSAVE` + format 1, then `[key][version][size][payload]` sections. The header section
  has key=value lines. **Refuse:** format, `elf_sha`, `iso` (size + SHA-256 of the first/last MiB,
  path-independent), `deterministic`, `pad_clock`, `pad_prefix_sha` (SHA of the route entries
  that start at or before the save tick, so a candidate may change the route *after* it),
  `gs_backend`. **Warn:** `runner_sha` (refuse under STRICT), `skip_movie`. Every section carries a
  version. Before anything is applied, the loader refuses unknown, missing, duplicate or
  mismatched sections.
- **Size/time:** 52.85 MB per state, 38 sections. `memory` 40.9 MB (RDRAM, IOP RAM, scratch, the
  4 MiB CPU-side VRAM, VU memories), `stub:sif` 5.2 MB (IOP heap storage), `gs` 4.2 MB, `snd`
  2.4 MB, the rest < 71 KB each. Save 450–533 ms and load 463–472 ms, mostly the runner SHA-256
  over the 170 MB executable (cacheable).

### Builds (budget 8) and suite

| # | Kind | Wall | Runner SHA-256 | Suite (worktree root) |
| --- | --- | --- | --- | --- |
| 1 | cold, unchanged source | 227 s | `119389a7…` (= F5 `runner-det`) | 658/658 |
| 2 | savestate (headers → full codegen rebuild) | ~210 s | `4c268636…` (`runner-ss2`) | 664/664 |
| 3 | MPEG playback captured | 24 s | `4df61d64…` (`runner-ss3`) | 664/664 |
| 4 | MPEG ended-decoder rule | ~25 s | `b6b4caa4…` (`runner-ss4`) | 664/664 |
| 5 | runner B for (d): ss4 + one log string (`[vpad] off (… SS1 runner B)`) | 22 s | `cd0cbbf5…` (`runner-ss4-B`) | – |
| 6 | syscall section linked | ~25 s | `7c917be7…` (`runner-ss6`) | 664/664 |
| 7 | pre-validation + link test | ~25 s | `6da0a03d…` (`runner-ss7`, final) | **665/665** |

Build 2 was preceded by compile-only checks of the `ps2_runtime` and `ps2x_tests` targets (no codegen)
to fix errors before the full rebuild. SHAs are two matching reads each (`receipts.txt`).

## Stage 3: acceptance (det build, FR1-R1, sound on, paraLLEl 1×, one mini slot each)

Boot driver: `local/research/SS1/ss1_boot.py` (F5's driver + `--save-at/--save-path/--exit-after-save/--load`).
Comparison: `ss1_hashdiff.py` (`gb8_hashdiff.py` + `--from/--to`, and an unanchored match because
one `[frame:dump]` line was written without a newline before a det-hash line in boot B).

| Row | Runner | Command (label) | Result |
| --- | --- | --- | --- |
| (a) straight to t2600 | ss4 | `A4` | 2615 ticks, 70.0 s. IDENTICAL to F5 B1 1..2400 and to `A` (ss2) 1..2600 |
| (b) save t2000, exit | ss7 | `B7 --save-at 2000 --exit-after-save` | saved tick=2000 eeCycle=9830598000, 52,852,689 B, 464 ms. Hashes 1..2000 IDENTICAL to A4 |
| (c) load → t2600 | ss7 | `C7 --load t2000-v7.state --dump-ticks 2100,2300,2600` | **IDENTICAL 2001..2600**. SND 938/938 events identical, `ticks=4042 counter=0x10cb cid0=531` = A4. Frames t2100 `7ad8f18d`, t2300 `e6f87cdd`, t2600 `fad39c2b` = A4 (3/3). t2001 at 1.01 s, t2600 at 25.9 s wall |
| (c) first pass | ss4 | `B4` save + `C` load | IDENTICAL 2001..2600, frames 3/3 = A4, SND identical (the syscall section was not linked yet; see gaps) |
| (d) runner A state in runner B | ss4-B | `D --load t2000.state` (saved by ss4) | `warning: runner_sha differs … loading anyway`, **IDENTICAL 2001..2600**, SND 938/938 |
| (d) strict | ss4-B | `D-strict --env PS2X_SAVESTATE_STRICT=1` | `load refused: header mismatch runner_sha`, exit in 1.0 s |
| Refusal: route | ss4 | `D-padprefix --env PS2X_PAD_SCRIPT=10611:start:250` | `load refused: header mismatch pad_prefix_sha` |
| Refusal: layout | ss6 | `C6-oldfile` (ss4 file, no `syscalls` section) | `load refused: missing section syscalls` |
| Race-start | ss4 | `E --save-at 1720` + `F --load t1720.state` | saved t1720 (533 ms, hashes 1..1720 = A). Load: **HUD tick at 1.01 s vs 33.0 s straight**, IDENTICAL 1721..2100, t1800 frame viewed (race HUD, rider, carve trail, 00:00:01) |
| Deferral only | ss2/ss3 | `B`, `B3` | never saved: `stub:mpeg: MPEG playback state live` / `MPEG decoder live` every tick 2000–2607. **IDENTICAL to A 1..2600**, so failed attempts don't perturb the run |

**Frames viewed.** t2100 from the straight run A and from the load C show the same scene. One is a
single present behind the other (trick counter 210 vs 220, rider pose). This is host present-latch
timing, not guest state. Two *straight* runs disagree the same way: A dumped `fdbbd91c`, while A4
and F5's B1/B1b dumped `7ad8f18d`. The loaded C/C7 frame is byte-identical to A4's, so the frame
check is 3/3 against A4. The t1800 frame after the t1720 load shows the race (HUD, 2nd/2, rider,
trail).

**Times (mini, M5 Pro, det build, paced):**

| | Straight | From a state |
| --- | ---: | ---: |
| To race HUD (t1714) | 33.0 s | **1.01 s** (t1720 state) |
| To t2001 | 44.7 s | **1.01 s** (t2000 state) |
| Load → t2600 | – | 25.9 s (600 ticks run at the det build's in-race rate; A4 takes 22.8–24 s for the same ticks) |
| Save / load cost | – | ~0.46–0.53 s each (runner SHA dominates) |

Boots: 14 of 16 (A, B, B3, B4, C, D, D-strict, D-padprefix, E, F, A4, C6-oldfile, B7, C7), all
slot 1, all ≤ 71 s, runner by PID (driver), lease released on every path. Receipts:
`receipts.txt`. Run dirs and states in `~/dev/ssx3-work/SS1/{run,states}` (states hold game RAM:
scratch only, never git).

## What a lane gets

A lane can store one race-start state per (ELF, ISO, route prefix, backend) and boot its own
candidate from it: `PS2X_DETERMINISTIC=1 PS2X_SAVESTATE_LOAD=t1720.state` (the rest of the FR1-R1 env
unchanged). The candidate may be any build as long as every section version matches. A layout
change in an owner bumps that section's version and refuses cleanly. Proposed store: next to RS2's
baselines, keyed like them (`<fork>-det-fr1r1-t1720-snd1-1x.state` + manifest).

## Android / iOS port needs

- **Paths/identity:** the runner SHA needs the right file. Android: the `.so` via `dladdr`, not
  `/proc/self/exe` (that is `app_process`). iOS: `_NSGetExecutablePath` works (the fallback today
  is `/proc/self/exe`, so Android needs this change). ELF and ISO identity are content-based, so
  device paths don't matter.
- **Transport:** `adb push` / Files into the app sandbox; `PS2X_SAVESTATE_LOAD` through the bundled
  env file.
- **Cross-host states (Mac → Odin):** the layouts are the same arm64 PODs, paraLLEl is the same
  source, and both use libc++ (bucket policy and insertion order are what the map test proves on
  macOS). Unverified: NDK libc++ bucket sizing, and LX1's Mac/Linux det parity carrying over to
  loads. A mismatch fails loudly (`bucket count not reproducible`) rather than silently.
- **GPU:** Adreno/Turnip and MoltenVK iOS go through the same `map_vram_*` paths on the GS worker.
  Not run there.
- **App lifecycle:** loading must happen before the first present on Android (it does: the game
  thread loads before `run()`). A UI trigger would replace `SAVE_AT` for hand use.

## Dropping `PS2X_DETERMINISTIC=1` later (device play)

Captured state is complete in either mode. Determinism only decides whether the *continuation*
is reproducible. What non-deterministic mode adds:

1. **Host-gated events.** Default mode delivers deadlines only when host time has also passed
   (`EeScheduler.cpp:2771-2808`). Deadlines are already saved as host offsets and rebased on load,
   so a loaded run continues correctly but not bit-exactly. Change: turn the `deterministic`
   header line from refuse into warn, and drop the config gate.
2. **Host inputs.** Live pad input: the pad-latch readiness check requires an idle pad. For play,
   clear pending edges on load instead of refusing. ExternalWake events: the queue must be empty
   (already checked). The CD clock and OSD timezone are host-derived but live in guest RAM, so
   they are captured.
3. **Save trigger and stall.** A hotkey/menu instead of a tick. Copy the ~53 MB snapshot and write
   it off the game thread. Compute the runner SHA once per process. That brings the stall to about
   one drain + memcpy.
4. **Pacer.** Already reset on load; it re-anchors on the next vsync.

## Gaps

- **paraLLEl exactness:** not captured are the GPU CLUT buffer (`cached_cbp` is cleared so CLD 4/5
  reload; CLD 0 draws before the guest's next CLUT load would use a stale palette), the private
  vertex queue and transfer state (assumed idle at a drained vsync), and the SSAA/hi-res planes
  (only 1× tested). No visible effect in the 3 compared frames. The exact fix is a paraLLEl
  accessor for the CLUT (fork patch), not done here.
- **Closures:** only `sceCdStRead` is tagged. RPC end-function / server-dispatch, MPEG, IPU,
  syscall-override and exit-handler closures defer the save. Not seen live at t1720/t2000;
  elsewhere a save may land a few ticks late (logged).
- **MPEG:** a decoder whose stream has ended is dropped. That diverges only if the guest continues
  the same stream without a new sequence header. A mid-stream decoder defers.
- **Memory card:** the HLE state is saved and open card files defer, but the card directory on
  disk is **not** copied with the state (the design row says snapshot). FR1-R1's cards stay empty
  (`mc0/`, `mc1/` empty in every run). A saving lane needs this.
- **IOP modules (ps2xIOP subsystem):** not captured. Per the inventory, SSX 3 has no builtin
  profile, and the det-hash, SND and frames all match, but this is unverified for other titles.
- **The first acceptance pass (B4/C/D/F) ran without the `syscalls` section.** It still matched,
  because RPC/bootmode/TLS/OSD/module state is equal after init or unused in the window. Fixed in
  `f1ead87`: the section is now linked, a unit test checks the registry, and the final runner
  re-passed (b)/(c) (`B7`/`C7`). (d) and the race-start rows were not re-run on ss7.
- **Det-hash scope:** it covers RDRAM, scratch, VU1 data/code, the VU1 program count and eeCycle.
  GS VRAM is checked only through the 3 frames; the SPU only through the SND event log and
  counters. Pad state is not hashed directly (the route is recomputed from the tick).
- **Portability of the map-order technique** beyond libc++ (e.g. libstdc++ on bradflix/LX1) is
  untested. A mismatch refuses.
- One save per run (`SAVE_AT`). The `libc rand` flag was never set in these runs.
- Scratch `~/dev/ssx3-work/SS1`: 2.7 GB (build 1.8 GB, bin 810 MB, states 157 MB, runs 19 MB),
  under the 10 GB cap. Internal total 148.1 of 200 GB.

## Orchestrator gate, stages 1–3 (2026-09-25)

**Pass.** Re-ran `ss1_hashdiff.py` myself: C7 (load t2000) and D (cross-runner load) IDENTICAL 2001..2600
vs A4; F (load t1720) IDENTICAL 1721..2100; tick-2600 det-hash lines equal byte for byte. F's t1800
frame viewed (race HUD, rider, trail) and its `fnv1a=26b7c5c7` equals F5 B1's straight-run t1800
frame. Race start 33.0 s → 1.01 s. Part 2 released (below).

## Part 2 brief (orchestrator, 2026-09-25) — make it the default lane tool, then fold

1. Re-run (d) cross-runner and the t1720 race-start rows on the final runner (ss7 + an ss7-B).
2. `local/tooling/boot/ssx3_boot.py`: `--save-at/--save-path/--exit-after-save/--load/--strict`
   (from `ss1_boot.py`; no second driver). `local/tooling/boot/baseline.py`: `put-state`/`get-state`
   keyed like baselines (fork, route, tick, backend, SSAA; manifest with the header lines), states in
   `~/dev/ssx3-work/baselines/states/` (scratch only). Seed a3efbfe-equivalent states at t1720 and
   t2000 from your final runner; `README.md` usage.
3. Gaps that lanes will hit: (a) memory-card directory snapshot/restore with the state (MC lanes);
   (b) a 4×+hi-res save/load pair (det-hash + frame at the load's next dumped tick); (c) the paraLLEl
   CLUT: add the accessor in a paraLLEl-GS worktree branch `ss1-clut` (local, never push) if it's
   small, else state the plan.
4. Fold prep: rebase-free — your branch is on `a3efbfe`, fork `ssx3` hasn't moved. Suite green,
   runner-dir check empty, `git log --format=%s a3efbfe..` clean subjects. **Don't push**; the
   orchestrator pushes after the gate.
Budget: ≤ 6 builds, ≤ 12 boots (one slot each), 3 h. Append `## Part 2`; commit `[SS1] Part 2 …`.

## Part 2 (worker, 2026-09-25 ~20:00–20:35 EDT)

**Outcome:** every Part 2 row passes. The final runner reproduced (d) cross-runner and the t1720
race start. The shared driver and store now carry states, and two a3efbfe-equivalent states are
seeded. The memory-card dir travels with the state. A 4×+hi-res pair is bit-exact against F5's
straight 4× B4, and the paraLLEl CLUT is now saved/restored by a 64-line accessor on a local
paraLLEl branch. The branch is fold-ready (fast-forward onto fork `ssx3` `a3efbfe`).

### Code (local, not pushed)

| Repo / branch | Commit | What |
| --- | --- | --- |
| PS2Recomp `ss1-savestate` | `5474956` | paraLLEl CLUT as an optional tail of the GS blob (**gs section v2**; compiles against paraLLEl with or without the accessor via `PARALLEL_GS_HAS_CLUT_STATE`); `stub:mcdir` section (card roots for ports 0/1 go into the state; the restore refuses when the target card dir holds a different file, so a real card is never overwritten); `pgs_ssaa`/`pgs_hires` header lines (warn-level); save defers while paraLLEl palette uploads are pending |
| paraLLEl-GS `ss1-clut` (worktree `~/dev/ssx3-work/SS1/parallel-gs`, from `19d93b2`, Granite `166ba21a` + 18 third-party submodules = F2's) | `464f263` | `GSRenderer::read_clut_state`/`write_clut_state` (the 1 MiB ring, `CLUTInstances`×`CLUTSize`, plus `base/next_clut_instance`, via one-off copy + fence after `flush_submit`) and `clut_state_idle()` (palette uploads pending); `GSInterface` wrappers. 4 files, +87 |

Fork totals `git diff --stat a3efbfe HEAD`: 31 files, +3,243/−13. Subjects `a3efbfe..HEAD`:

    5474956 [SS1] Save paraLLEl CLUT (optional tail, gs v2), memory-card dir with the state, SSAA/hi-res header lines
    f1ead87 [SS1] Link the syscall section (static-lib dead strip); validate all sections before applying
    53a1b1d [SS1] Save MPEG playback bookkeeping; drop a decoder whose stream ended (race states)
    e76a4fc [SS1] Save states (dev, default off): vsync-boundary save/load of the whole runtime

Runner-dir check `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`: **empty**. Fork `ssx3`
is still `a3efbfe` (fetched), and `ss1-savestate` fast-forwards onto it. Suite from the worktree
root: **666/666** (+1 test: card-dir round trip that never overwrites a different card).

### Builds (budget 6)

| # | What | Wall | Result |
| --- | --- | --- | --- |
| P2-1 | CLUT + mcdir + header, build pointed at the `ss1-clut` paraLLEl dir | 238 s | `runner-p2a` `c93e9c9b970f39b1d19eddb2f37993408106d2a8fe28ab81cb051f4eb8033f04` (×2), suite 666/666 |
| P2-2 | runner B = p2a + one log string (`[vpad] off (… SS1 runner B)`, `logs/runnerB-p2.diff`), reverted after | ~25 s | `runner-p2a-B` `cac2fbe86ced378ad8e49f9ea04c37598f1b45c04e712ff7da955f341f421df0` (×2) |
| P2-3 | compile-only check of the fork against canonical paraLLEl `19d93b2` (F2 dir, no accessor), separate build dir, targets `ps2_gs_shadow ps2_runtime` | 10.8 s | exit 0: `ps2_gs_parallel_backend.cpp` + `ps2_runtime` compile with `PARALLEL_GS_HAS_CLUT_STATE` undefined (F2 `gs_interface.hpp` has 0 hits); not linked or booted |

### Boots (budget 12; all one slot, slot 1, via the shared driver's code)

| Label | Runner | Row | Result |
| --- | --- | --- | --- |
| P-B | p2a | save t2000 (1×) | deferred once (`gs: GS backend transfer active` = palette uploads pending), then **saved at t2000** later in the same tick (eeCycle 9830600296), 53,898,015 B, 39 sections (+1 MiB CLUT, `stub:mcdir`) |
| P-C | p2a | load → t2600 | **IDENTICAL 2001..2600** vs A4; SND 938/938; counters `ticks=4042 counter=0x10cb cid0=531`; frames t2300 `e6f87cdd`, t2600 `fad39c2b` = A4, t2100 `fdbbd91c` (= straight run A: the known ±1-present dump) |
| P-D | **p2a-B** | (d) cross-runner | `warning: runner_sha differs … loading anyway` → **IDENTICAL 2001..2600**, SND 938/938, frames 3/3 = A4 |
| P-E | p2a | save t1720 | saved t1720, hashes 1..1720 = A4 |
| P-F | p2a | load t1720 → t2100 | **IDENTICAL 1721..2100**; race HUD tick at **1.03 s vs 31.9 s** straight (A4); frames t2000 `3692fd39`, t2100 `7ad8f18d` = Stage 3's F |
| P-A1800 | p2a | straight, dump 1799/1800/1801 | settles P-F's t1800 frame (`22136e8c` ≠ F5 B1's `26b7c5c7`): the straight run dumps **t1799 = `22136e8c`**, t1800 = `26b7c5c7`. So P-F's t1800 dump is the t1799 picture, one present behind: jitter, not state. Hashes 1..1810 = A4 |
| P-4B | p2a | save t2000, `PS2X_PGS_SSAA=4 PS2X_PGS_HIRES_SCANOUT=1 PS2X_PGS_PRESENT_PIPELINE=1` | saved t2000 (same deferral once), 53,898,017 B |
| P-4C | p2a | load → t2200, same env, dump 2098/2100/2102 | **IDENTICAL 2001..2200**; 1024×896 frames t2098 `51f30795`, t2100 `3e5b75ed`, t2102 `5d0b8f9d` = **F5 B4 (straight 4×+hi-res+pipeline) 3/3 byte-identical**; t2100 viewed: sharp 4×, rider + trail, trick 190 as F5 recorded |

A driver bug found on the way: with a relative `--out`, the env paths nest under the run dir (the
runner's cwd), so P-C's frames and `snd.log` landed in `run/P-C/run/P-C/`. They were read from
there. Fixed in the shared driver (`lane = (...).resolve()`).

### Tools (step 2)

- `local/tooling/boot/ssx3_boot.py`: `--save-at/--save-path/--exit-after-save/--load/--strict` (det
  only; a clean exit after a save counts as target; paths resolved) + the absolute-`--out` fix. It
  is the only driver; `ss1_boot.py` stays as the Stage 3 receipt.
- `local/tooling/boot/baseline.py`: `put-state --state F --pins P --tick T [--note]`,
  `get-state <key|--pins P --tick T>` (two SHA reads, `MISSING <key>` rc 2, `CORRUPT` rc 3),
  `list-states`. Store `<store>/states/<key>/{state.bin, manifest.json}`. The manifest holds the
  pins, the key pins, the state's header lines, the SHA and the source. Key = guest-relevant pins
  (`fork, codegen×2, vu1_images, parallel_gs, route, backend, ssaa, hires, iso_sha, elf_sha`) + the
  tick, e.g. `a3efbfe-fr1r1-t1720-parallel-1x-ba8aa72b`.
- Seeds (pins `local/research/SS1/pins-state-a3efbfe-fr1r1-1x.json`; guest a3efbfe, saved by
  `runner-p2a`):

  | Key | Bytes | SHA-256 |
  | --- | ---: | --- |
  | `a3efbfe-fr1r1-t1720-parallel-1x-ba8aa72b` | 53,901,345 | `a5dd300e45d8d6c99a4b0b969d3aa7d891df229c034835e6b02de876376faaa2` |
  | `a3efbfe-fr1r1-t2000-parallel-1x-433cb405` | 53,898,015 | `74bba029288604ada380ab5969f9135e62e68c272ba789164e1e0094b0a35aec` |

- `local/tooling/boot/README.md`: a "Save states" section (get-state → `--load` → compare from T+1).
- **Shared-tree note:** another pane (HS1) had uncommitted edits in `ssx3_boot.py`,
  `baseline.py` and `p_lane_lease.py` when I started. My commit carries **only my hunks on top of
  HEAD** (staged as blobs built from `HEAD` + my patch). Their working-tree edits are untouched, and
  the working copies contain both.

### Gap status after Part 2

| Gap (Stage 3) | Now |
| --- | --- |
| Memory-card dir not with the state | **Closed** for saves: `stub:mcdir` (unit test). Not exercised by a boot: FR1-R1 cards are empty, so both roots are empty in every file |
| paraLLEl CLUT stale after load | **Closed with the `ss1-clut` accessor**: both 1× and 4× loads restore it. With canonical paraLLEl (no accessor) the old behaviour stays: `cached_cbp` cleared, a one-line warning if a state carries a CLUT. Folding needs the paraLLEl commit too (orchestrator's push decision) |
| 4×/hi-res untested | **Closed**: P-4B/P-4C bit-exact against F5 B4 at 1024×896 |
| Syscall section missing | closed in Stage 3 (`f1ead87`), re-verified: every file has 39 sections |
| Still open | paraLLEl private vertex queue / transfer state (assumed idle at a drained vsync, not captured); only `sceCdStRead` among the closures is tagged; IOP modules not captured; a mid-stream MPEG decoder defers; libstdc++ map order untested; the deferral text `GS backend transfer active` also covers "palette uploads pending" (wording only) |

Scratch: `~/dev/ssx3-work/SS1` 4.4 GB (two build dirs, paraLLEl worktree 336 MB, runners, states)
≤ 10 GB; store `baselines/states` 103 MB. No push anywhere.

## Orchestrator gate, Part 2 (2026-09-25)

**Pass.** Verified: `list-states`/`get-state` (rc 0), P-4C frames t2098/2100/2102 FNVs equal F5 B4's
straight 4× run. Good catch on the relative `--out` bug and on keeping HS1's uncommitted hunks out of
your commit. Before the fold (fork `ssx3` + paraLLEl `ssx3` fast-forwards, orchestrator pushes):

## Part 3 brief (orchestrator) — fold checks, then stop
1. **Android compile** of `ss1-savestate` + paraLLEl `ss1-clut` on bytesize (F5 recipe
   `local/research/F5/build-android.sh`, hold the ssh open; `ps aux` first — HS1 uses bradflix, not
   bytesize). `assembleRelease` must succeed; keep the APK (SHA ×2), don't install. Note the
   `/proc/self/exe` runner-SHA fallback on Android as a gap (no device use now).
2. **Speed-neutral with knobs off:** clean (non-det) Mac runner from your branch vs F5's
   `~/dev/ssx3-work/F5/bin/runner-clean`, ABBA, exclusive lease ≤ 5 min per hold, FR1-R1 unpaced to
   t2400, race vsyncs/s. Pass = within run-to-run spread (state the spread).
3. Commit `[SS1] Part 3 …` with the table and stop. ≤ 2 builds, 4 speed boots.

## Part 3 (worker, 2026-09-25 ~20:40–21:05 EDT): fold checks. Both pass

### 1. Android compile (bytesize, F5 recipe, one held ssh)

bytesize was idle at the start (`ps aux`: no java/gradle/ninja/cmake; 739 GB free, 11 GB RAM).
Staging in `/home/brad/ss1`:

- `PS2Recomp/` = `git archive ss1-savestate` (`5474956`) streamed from the mini (tar SHA `04b76f6e…`, 358 files both sides).
- `codegen-ssx3/` = a real copy of F5's (9,457 files; `register_functions.cpp` `8ea8ed43…`, changed file `89953ba2…`).
- `vu1gen` → F5's `vu1gen-f5` (7 images, SHAs verified in F5).
- `jniLibs` → F2's.
- `parallel-gs/` = a copy of F2's `19d93b2` tree (4 GS files byte-identical to the mini's `19d93b2`), with the 4 `ss1-clut` (`464f263`) files dropped in. Remote SHAs match the mini: `gs_renderer.cpp 8e6b30c3…`, `.hpp 852258ef…`, `gs_interface.cpp 20565557…`, `.hpp fee5389f…`.

`build.sh` = F5's `build-android.sh` with only the root, source dirs and VU1 dir changed
(`local/research/SS1/build-android-ss1.sh`, SHA `59095232…` local = remote).

| Item | Value |
| --- | --- |
| `assembleRelease` | **BUILD SUCCESSFUL in 9m 8s**, 48 tasks executed, 0 FAILED (`--max-workers=2`) |
| APK | `9940c8f37ce21ccf75a94239d72a904cebacc6c51b76d308e02768e76f6601a6`, 187,258,440 B. Remote ×2 + pulled ×2 match. Kept at `~/dev/ssx3-work/SS1/odin/app-release.apk`. **Not installed** |
| Contents (`strings -a libps2EntryRunner.so`, 173 MB) | `PS2XSAVE`, `PS2X_SAVESTATE_LOAD`, `[savestate] loaded`, `ssx3-clut-readback` all present: the savestate code and the paraLLEl CLUT accessor compiled for arm64 |
| Gap (as briefed) | the runner-SHA header uses `/proc/self/exe` on non-Apple (string present in the `.so`). On Android that is `app_process64`, not `libps2EntryRunner.so`, so a device state would pin the wrong file. Before device use: hash the library via `dladdr(&someSymbol)`. No device use now |

### 2. Speed-neutral with the knobs off (Mac mini, ABBA, exclusive lease per boot)

Clean runner from my branch (build 2 of 2): F5's clean flags (det-hash tap off, logs/taps off,
paraLLEl on) with the paraLLEl dir = `ss1-clut`. `runner-ss-clean`
`bd8d5661a7aa8dccd058c2f7458048f5a7a2a08b1aa9020c61067137aae8b6d0`, built in 239 s. Control:
F5's `bin/runner-clean` `e1e598c2…`. Boots via the shared driver, speed mode (`PS2X_UNPACED=1`,
sound on, `PS2X_PGS_PRESENT_PIPELINE=1`, FR1-R1 to t2400, exclusive `both`). Each hold ≤ 62 s.
Metric: F5's B6 method, the mean of the 5 s `[vsync-rate]` samples at ticks 1800–2420 (race).

| Order | Label | Runner | Race samples (/s) | Race mean | × 59.94 | HUD wall | loadavg at start |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | S1-A | F5 clean | 26.75 23.56 23.37 24.59 29.10 | 25.47 | 0.425 | 35.0 s | 10.2 |
| 2 | S2-B | SS1 clean | 28.34 27.52 28.13 26.80 19.97 | 26.15 | 0.436 | 36.1 s | 6.5 |
| 3 | S3-B | SS1 clean | 27.51 27.35 27.92 28.11 29.78 | 28.13 | 0.469 | 35.1 s | 4.6 |
| 4 | S4-A | F5 clean | 27.32 27.37 27.74 27.91 29.75 | 28.02 | 0.467 | 35.1 s | 3.8 |

**A (F5) mean 26.75/s, B (SS1) mean 27.14/s, B/A = 1.015.** Run-to-run spread: A 9.5 %, B 7.3 %
(the first two boots ran under loadavg 6–10 from other panes' non-boot work; the exclusive lease
covers boots only). The quiet middle pair is 28.13 vs 28.02 (+0.4 %), and both agree with F5's
B6 (28.17/s). **The difference is inside the spread, so speed-neutral: PASS.** Expected: with the
knobs unset, the per-dispatch cost is one bool test and one `u64` compare.

### Part 3 budget

Builds 2/2 (Android, Mac clean). Speed boots 4/4, exclusive per boot, lease released every time.
Nothing pushed or installed. The fold candidates are unchanged since Part 2: fork `ss1-savestate`
`5474956` (fast-forwards onto `ssx3` `a3efbfe`) and paraLLEl `ss1-clut` `464f263` (from `19d93b2`).
Stopping here.

## Orchestrator gate, Part 3 (2026-09-26) — folded

**Pass; pushed.** Fork `ssx3` `a3efbfe..5474956` and paraLLEl-GS `ssx3` `19d93b2..464f263` fast-forwarded
after my checks (clean trees, ancestors, runner-dir diff empty, `[SS1]` subjects only). Speed-neutral
(B/A 1.015 inside a 7–10 % spread; the quiet pair +0.4 %); Android `assembleRelease` green. New canonical
paraLLEl checkout `~/dev/ssx3-work/parallel-gs-ssx3` at `464f263` is `mac_build.sh`'s default. Open for
device use: Android runner-SHA via `dladdr`, a UI save/load trigger, non-det loads.
