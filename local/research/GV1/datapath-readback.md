# GV1 data-path code read (read-only subagent hand-back, 2026-09-26)

Revisions: PS2Recomp **`fork/ssx3` `1c37c41`** (contains MT1 `703a554`; the local `ssx3` checkout at
`f949ff0` is stale), paths relative to `ps2xRuntime/`; paraLLEl-GS **`3d72467`** (= `1b3a294` F7/CP1 pin
+ SS3 save-state accessors), paths relative to `gs/`. Nothing edited, built or run.

## Data path
```
EE CHCR store (D1/D2) → PS2Memory chain walk → processPendingTransfers   [ps2_memory.cpp:1644,2004,2132]
  │ PS2X_MTVU=1: GIF+VIF1 chunks copied, submitted as ONE unit job     [ps2_memory.cpp:2163-2200, 2500-2515]
  ▼ (MTVU thread)
processVIF1DataImpl: UNPACK → m_vu1Data (16 KiB) / MPG → m_vu1Code      [ps2_vif1_interpreter.cpp:410, 878-1128, 743-744]
  │ MSCAL/MSCNT → m_vu1MscalCallback → VU1Interpreter::execute/resume  [:539-617; ps2_runtime.cpp:1441-1497]
  ▼
VU1 run (generated pairs/blocks or interpreter, per-cycle pipeline)   [vu/ps2_vu1_core.cpp:1416-1535]
  │ XGKICK → startXgkick; 1 QW per 2 VU cycles; whole packet at EOP    [:791-812, 695-777]
  ▼
PS2Memory::submitGifPacket(Path1, drain now) → GifArbiter submit+drain [ps2_memory.cpp:2703-2747; gs/ps2_gif_arbiter.cpp:73-121]
  │ (PATH2 DIRECT and PATH3 DMA/masked FIFO go through the same arbiter)
  ▼
GS::processGIFPacket → GsWorker::enqueue(copy)   [gs/gs_frontend.cpp:1094-1106; gs/gs_worker.cpp:44-78]
  ▼ (GsWorker thread)
GS::processGIFPacket again: RawGifPacket → GSInterface::gif_transfer    [gs_frontend.cpp:1121-1122; ps2_gs_parallel_backend.cpp:758-762]
  + the runtime's own GIFtag/register/vertexKick decode (Submit is a no-op) [gs_frontend.cpp:1145-1214, 2113-2222; backend:285]
  ▼
paraLLEl: packed_XYZ → vertex_kick → drawing_kick_append → mapped scratch [gs_interface.cpp:4056-4101, 859-900, 2484-2847]
  ▼ flush_render_pass (overflow/hazard) / flush() at present → flush_rendering: triangle_setup → binning → ubershader
```

## 1. VIF1
- Parser `processVIF1Data` (`ps2_vif1_interpreter.cpp:389-408`) → `processVIF1DataImpl` (`:410`) →
  `drainPath3IfUnmasked()` (`:407`). Opcodes NOP, STCYCL, OFFSET, BASE, ITOP, STMOD, MSKPATH3, MARK,
  FLUSHE/FLUSH/FLUSHA, MSCAL/MSCALF, MSCNT, STMASK, STROW, STCOL, MPG, DIRECT/DIRECTHL, UNPACK (`:103-122`).
- UNPACK `:814-1160`, writes `m_vu1Data` (`:1076`, `:1128`), honours `+TOPS` (`:858-859`), ROW modes 1/2
  (`:1106-1108`).
- UV1 census vsync 92–2403 (`local/research/UV1/REPORT.md:46-61`): 3,850,530 UNPACKs — V4_32 31.1 %,
  V3_16 16.0 %, V2_16 11.5 %, V2_8 11.5 %, V4_5 10.0 %, V2_32 8.3 %, V3_32 6.1 %, V4_16 2.9 %, V4_8 1.4 %,
  S_32 1.0 %; mode always 0, masking on for 40 %, 95.6 % use `+TOPS`.
- MSCNT 0 in the race; MSKPATH3 20–31 windows/frame (`RR1/REPORT.md:35`); VIF1 i-bit never set
  (`IN1/REPORT.md:75-90`); MPG ~24/vsync in menus (`E39/REPORT.md:100`), race rate not found.
- FLUSH/FLUSHE/FLUSHA are no-ops (`:531-537`), PCSX2's instant-VU1 model (`MT1/REPORT.md:14-28`).
- MSCAL (`:539-585`): `startPC = imm*8`, `TOP = TOPS`, `ITOP = ITOPS`, then TOPS/DBF flip. The callback
  (`ps2_runtime.cpp:1441-1470`) sets D/T from FBRST (or the job's snapshot), calls
  `execute(code, data, gs, &memory, startPC, top, itop, 65536)` synchronously. `execute`
  (`ps2_vu1_core.cpp:1351-1394`) resets only scheduler, pc, vf0: **VF/VI/ACC/Q/P and flags persist across
  MSCALs** (full reset only in `reset()`, `:106-117`). Generated code by code-image hash
  (`lookupRecompProgram`, `:1463`); 7 images (`MT1/REPORT.md:638`).

## 2. XGKICK, PATH1/2/3
- `XGKICK` (`vu/ps2_vu1_lower_impl.h:677-679`) → `startXgkick` (`ps2_vu1_core.cpp:791-812`);
  `advanceOneCycle` calls `progressXgkick` each VU cycle (`vu/ps2_vu1_step_impl.h:219-227`), which copies
  one QW per 2 cycles, parses GIFtag sizes, wraps at 16 KiB (`ps2_vu1_core.cpp:695-777`). LSU commits land
  before PATH1 reads each QW (`step_impl.h:222-224`); a second XGKICK stalls while one is active
  (`step_impl.h:81-82`). Submitted whole at EOP (`finishXgkick`, `:779-789`) as `submitGifPacket(Path1, …)`,
  `drainImmediately=true` (`ps2_memory.h:353`).
- PATH2: DIRECT/DIRECTHL → `submitGifPacket(Path2, …, true, directHl)` (`ps2_vif1_interpreter.cpp:763-808`);
  pending IMAGE re-tags following VIF data as PATH2 (`:417-443`).
- PATH3: GIF DMA → `submitGifPacket(Path3, …, false)` (`ps2_memory.cpp:2233-2285`); masked packets split
  at EOP into `m_path3MaskedFifo` (`:2711-2731`); each MSKPATH3 unmask releases one EOP packet
  (`ps2_vif1_interpreter.cpp:519-520`; `ps2_memory.cpp:2630-2660`); unmasked end flushes the rest
  (`:2662-2701`).
- Arbitration: `GifArbiter::drain` stable-sorts by path 1 < 2 < 3, DIRECTHL can't preempt a PATH3 IMAGE
  (`ps2_gif_arbiter.cpp:88-104, 136-139`). Ordering matters: before RR1's fix, PATH3 texture uploads meant
  to interleave per object all landed at the first window (`RR1/REPORT.md:15, 28`).
- Copies per PATH1 packet: 64 KiB kick buffer (`ps2_vu1.h:304-305`) → arbiter vector
  (`ps2_gif_arbiter.cpp:83-85`) → `GsCommand` bytes (`gs_frontend.cpp:1103`).

## 3. GS ingestion into paraLLEl-GS
- GsWorker: `GS::processGIFPacket` → `m_backend->RawGifPacket` → `GSInterface::gif_transfer(path, data, size)`
  (`gs_frontend.cpp:1121-1122`; `ps2_gs_parallel_backend.cpp:758-765`), then the runtime's own full decode
  (GIFtag PACKED/REGLIST/IMAGE, `writeRegisterPacked`, `vertexKick`, `buildDrawBatch` copying the context
  per primitive; `gs_frontend.cpp:1145-1214, 1398+, 2113-2222, 2380-2405`). `Submit`/`UploadImage` no-ops
  on paraLLEl (`backend:285-286`).
- paraLLEl: `gif_transfer` per-path tag state (`gs_interface.cpp:4301-4408`), optimized PACKED loops for
  ST/RGBAQ/XYZ(F) and UV/RGBAQ/XYZ(F) (`:3327-3380`, `:4103-4143`). Per vertex `vertex_kick_xyz(f)`
  (`:846-900`) → `drawing_kick<PRIM>` (`:2894-2939`). Per primitive `drawing_kick_append` (`:2484-2847`):
  bbox/scissor, degeneracy, parallelogram/feedback/channel-shuffle detection, `check_frame_buffer_state`,
  `drawing_kick_update_state` when dirty (texture cache, CLUT, state vectors; `:1815+`, `:1255+`, `:1066`),
  page-tracker hazards; then memcpy pos/attr/prim into mapped GPU scratch (`:2831-2834`).
- Buffers: `reserve_primitive_buffers(MaxPrimitivesPerFlush = 65,536)` maps UMA cached-coherent scratch
  (`gs_renderer.cpp:3188-3211, 947-978`; `gs_renderer.hpp:154`), re-reserved after each flush
  (`gs_interface.cpp:59-62, 348-351`). Layouts `shaders/data_structures.h:55-80, 139-144`.
- Flush: `post_draw_kick_handler` on overflow (`gs_interface.cpp:2941-2954`); reasons TextureHazard,
  CopyHazard, HostAccess, FBPointer, PressureFlush, Overflow; `flush_render_pass` → `flush_rendering`
  (`:134-302`) → triangle_setup → binning → shading (`gs_renderer.cpp:3237+, 1986, 2167, 2589`);
  `GSInterface::flush()` → `flush_submit` (`gs_interface.cpp:4268-4275`) at present (`backend:328-330`).
- **No path takes primitives already in a GPU buffer.** `num_primitives` is a CPU count for push constants,
  dispatch sizes and scratch sizing (`gs_renderer.cpp:1745-1771, 1794, 1805, 2002`); indirect dispatch only
  for texture-upload analysis (`:1467-1480`). Primitive setup depends on PRIM, FRAME/ZBUF/TEST/ALPHA/
  SCISSOR/XYOFFSET/TEX0-2/CLAMP/MIPTBP/FBA, TEXA/TEXCLUT/FOGCOL/DIMX/DTHE/COLCLAMP/PABE/PRMODE, and the
  CLUT/texture-cache/page-tracker state, all resolved on the CPU per draw.

## 4. MTVU threading and sync points
- `ps2_mtvu::submit` (`include/ps2_mtvu.h:533-543`) snapshots FP control word + FBRST; queue bounded 64
  jobs / 64 MiB (`:154-165`), EE blocks on `cvSpace` (`:288-303`); `waitFor` spins then blocks
  (`:311-325`). Jobs: GIF+VIF1+drain (`ps2_memory.cpp:2500-2515`), VIF1 FIFO QWs (`:1386-1398`), EE GS
  privileged writes (`:1025-1037`).
- GsWorker `enqueue` blocks on `m_hasSpace` at 1,024 descriptors / 16 MiB (`gs_worker.h:123-124`;
  `gs_worker.cpp:44-78`); `GifDrainBatch` coalesces wakeups (`ps2_memory.cpp:26-44`); each packet also
  enqueues `NoteGifPath` (`ps2_runtime.cpp:1406-1409`; `gs_frontend.h:152-161`).

| Sync point | Direction | Race frequency | Citation |
| --- | --- | --- | --- |
| VBlankStart: wait all jobs (LAG: previous frame's; full on det-hash ticks) | EE waits unit | 1/frame; Odin 36.2 ms/frame blocked; Mac 13.8 (MTVU), 6.4 (LAG) | `ps2_mtvu.h:725-753`; `EeScheduler.cpp:2956`; `CP1:134`; `MT1:510` |
| GS priv read (CSR); masked free under R1, others sync + GsWorker fence | EE waits unit + GsWorker | 4 CSR loads/frame; 278,530/278,532 masked | `ps2_runtime.cpp:3925-3945`; `ps2_mtvu.h:576-603`; `MT1:312-319` |
| GS priv write (R2 queued; CSR W1C bits 0–1 syncs) | EE → unit queue | 11/frame | `ps2_memory.cpp:1025-1039, 1215-1300`; `MT1:312` |
| `gsPrivSync` | EE waits unit + GsWorker | not found | `ps2_memory.cpp:1107-1111` |
| EE access to VU1 code/data | EE waits unit | 0 in race | `ps2_memory.cpp:704-712`; `MT1:314` |
| VIF1 register writes | EE waits unit | 2 per boot | `ps2_memory.cpp:1557-1559`; `MT1:315` |
| CTC2 CMSAR1 VU1 start | EE waits unit | 0 | `ps2_runtime.cpp:3321`; `MT1:315` |
| HLE GS stubs / native GIF | EE waits unit | 0 in race | `Kernel/Stubs/GS.cpp:116,768,1201,1213`; `ps2_runtime.cpp:4219` |
| CFC2 VPU_STAT / CTC2 FBRST (inline) → D/T fallback | EE runs VIF1 inline | never fires | `ps2xRecomp/src/lib/vu_translator.cpp:57-59,101`; `ps2_memory.cpp:1387,2140,2166`; `MT1:316` |
| Save/load state | EE waits unit | on demand | `ps2_savestate.cpp:1023,1081,1349,1389` |
| MTVU queue full | EE waits | not found | `ps2_mtvu.h:293-296` |
| GsWorker queue full | unit waits GsWorker | Odin 6.7 ms/frame | `gs_worker.cpp:48-60`; `CP1:131` |
| Present latch RPC + paraLLEl flush/vsync | host waits GsWorker | 1/present; flush_submit 22.6 ms/present (Odin, pre-FS2) | `gs_frontend.cpp:940-975`; `backend:328-330`; `CP1:98-101` |

## 5. Per-frame counters (race t1800–2400, 601 vsyncs; gfx_stats of a diagnostic build, fork `56a5e8a`,
`~/dev/ssx3-work/CT1/run/B2/gfx_stats.log` = `IN1/run/B1/gfx_stats.log`; counts, not speed)

| Counter | Mean | Min–max |
| --- | ---: | --- |
| MSCAL/vsync (MSCNT 0) | 1,040 | 890–1,155 |
| VU1 cycles/vsync | 1,413,741 | 1.27–1.53 M |
| Max cycles in one program | 23,178 | 20,830–26,870; 0 budget-exhausted |
| XGKICK = PATH1 packets | 1,683 | 1,384–1,909 |
| PATH1 bytes | 2,154,932 | 1.84–2.39 MB |
| PATH2 packets / bytes | 256 / 14,274 | |
| PATH3 packets / bytes | 28 / 508,077 | |
| PATH1 drawn primitives (`d1_n`) | 32,309 | 26,901–36,123 |
| PATH1 primitive-vertices (`d1_vert`) | 96,572 | ≈3 per primitive; top (FBP, PRIM) = 0:4 TRISTRIP |
| PATH2 / PATH3 primitives | 71 / 113 | |

Other: MTVU `jobs=55479` to t4500 on the Odin (`CP1:91`), `jobs=28226` to t2400 Mac/bradflix (`MT1:473`),
8 jobs per race frame (5 DMA + 3 FIFO; `MT1:284, 312`); one VIF1 list/frame ≈ 18 ms unit work on the Mac
(`MT1:306`); unit 19.2 ms/frame Mac (`MT1:284`); Odin MTVU 30.1 ms/frame (`CP1:128`), generated VU1 21.6,
FMAC core 13.0 (`VR4:14-17`); GsWorker 9.7 (`CP1:130`); GPU busy 24.8 ms/frame (`CP1:156-160`). GIF packets
1.99 M through ~t2494 (PATH1 1.66 M, PATH2 0.30 M, PATH3 30 k; `MT1:480`). paraLLEl render-pass flushes
per race frame: not found.
