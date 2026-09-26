# MT1 — VU1 on its own thread (MTVU), deterministic by design

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/MT1.md`, 2026-09-25/26.
Stage 1 (map + design) only. I built nothing and ran no boots. The orchestrator gates this stage.

- Fork worktree: `~/dev/ssx3-work/MT1/PS2Recomp`, local branch `mt1` = fork `ssx3` **`fb28d99`**,
  no commits yet. VR2's fold `d4fc12e` is an ancestor. Nothing is pushed.
- In this report, source paths are relative to `ps2xRuntime/` at `fb28d99` unless another
  location is given. PCSX2 files are cited by path: `Q1/src/…` means
  `local/research/Q1/src/` (read-only; GPL, so I took techniques only and copied no code).

## Headline

1. **No semantics change is needed.** Our synchronous runtime already uses PCSX2's default guest-time model for VU1, which is **instant VU1**:
   - An MSCAL runs the whole program inside the VIF1 delivery, at the D1_CHCR store that kicked the DMA.
   - The EE is charged 0 cycles.
   - VPU_STAT VBS1 (bit 8) is never set.
   - VIF1 FLUSH/FLUSHE/FLUSHA are no-ops.

   PCSX2 at P=`ae2bac2b` defaults to `vu1Instant = true`, `vuThread` off and `EECycleSkip = 0`
   (`pcsx2/Pcsx2Config.cpp`, `SpeedhackOptions()`: `DisableAll(); WaitLoop = true;
   IntcStat = true; vuFlagHack = true; vu1Instant = true;`).
   - Its instant path runs the program to completion at the kick: `Q1/src/VU1micro.cpp:76-79`.
   - It adds no EE cycles unless `add_cycles` is set: `VU1micro.cpp:36-49`.
   - PCSX2's own MTVU shows the guest the same model:
     - VPU_STAT is cleared at the kick and the busy bit is deliberately not set (`VU1micro.cpp:51-64`).
     - The busy bit is set only when instant VU1 is off (`Q1/src/MTVU.cpp:460-464`).
     - Cycle skip is 0 by default (`MTVU.cpp:456-457`).

   So the step-1 build **is today's build**. The threaded build must be det-hash IDENTICAL to the
   **current key**. That is a stronger proof than the brief asked for, and no re-baseline is needed. The
   65,536-cycle budget stays: it is deterministic, and the route peaks at 23,540 cycles
   (`docs/facts.md`, T48/E36).
2. **What the worker should own: the VIF1 → VU1 → GIF → GS-frontend unit, not only VU1.** A worker
   that owned only VU1 would have to wait before every PATH2/PATH3 arbiter touch. SSX 3 opens 20–31
   `MSKPATH3 0/1` windows per race frame inside the VIF1 list (RR1 E9), so the EE would wait about 30
   times per frame and the threading would buy almost nothing. The worker should instead run the
   **whole VIF1 delivery** (the unchanged `processVIF1Data` parser: UNPACK, MPG, MSCAL/MSCNT,
   DIRECT/DIRECTHL, MSKPATH3) plus the GIF (PATH3) deliveries, in submit order. The arbiter drains
   and GS-frontend parsing happen on the worker, exactly as they happen inline today. The EE keeps
   the DMA completion (D_STAT, CHCR STR, DMAC handlers), which the model says is instant anyway.
   PCSX2 does the same thing more narrowly: MTVU moves VU memory writes and unpacks into its ring
   (`MTVU.cpp:19-31`, handlers `:130-195`) and puts a PATH1 placeholder into the GIF stream at the
   kick (`MTVU.cpp:452`).
3. **Determinism comes from ownership.**
   - Every EE-thread access to unit-owned state first waits until the job queue is empty.
   - Each job's inputs are snapshots taken at submit, plus unit-owned state.
   - The unit never writes RDRAM or scratchpad, and never writes EE state the EE can read without a sync.

   So at every sync point the EE sees exactly what the synchronous build sees. The next section is
   the full map.
4. **Go/no-go is still open.** The overlap is bounded by the EE work between a unit kick and the
   next sync point. The nearest unavoidable sync point is the next VBlankStart. This depends on the
   game's frame structure and is unmeasured. I propose running a **census build first** (revised
   stage 2 below). It is det-identical and inert, logs per-frame kick → sync gaps, and a small
   replay model turns those gaps into a predicted speedup before any threading code exists. As a
   reference, N12 puts the Odin race frame at 68.3 ms, of which VU1 is 46.7 and
   GameThread-minus-VU1 is 21.6 (`local/research/N12/REPORT.md:18-19`).

## Map: every point where the EE side can observe or affect VU1 (and the unit)

"Owned" means owned by the unit worker while a job is in flight. The "Threaded action" column
says what the EE does at that point.

| # | Point | Where (fb28d99) | What it touches | Threaded action |
| --- | --- | --- | --- | --- |
| 1 | D1 (VIF1) / D2 (GIF) CHCR store kicks DMA | `src/lib/ps2_memory.cpp:1563-1597` (normal), chain walker `…:1600-1921` (copies the chain into `pt.chainData`, `:1911`), `processPendingTransfers()` call `:1942` | queues `PendingTransfer`s | **Submit a job.** Chain data is already a snapshot. Normal-mode and scratchpad transfers are **copied at submit** (the sync build reads RDRAM/SPR at the same instant). |
| 2 | `processPendingTransfers` | `ps2_memory.cpp:2070`: GIF `2073-2143`, VIF0 `~2145-2201`, VIF1 `2203-2303`, arbiter drain `2305-2309`, completion `2311-2355` | GIF → PATH3 submits, VIF1 parse, drain, D_STAT/CHCR | GIF, VIF1 and drain go into **one job, in this order**. VIF0 (VU0 memory only, no DIRECT) and completion stay on the EE and run now. VIF0 touches no unit state, so moving it ahead of the GIF work is invisible. `m_seenGifCopy`/`m_gifCopyCount` are set on the EE when the job is packaged. |
| 3 | VIF1 parser | `src/lib/ps2_vif1_interpreter.cpp:410` (`processVIF1DataImpl`): pending PATH2 image `417-443`, MSKPATH3 `513-519`, FLUSH* `531-537` (no-op), MSCAL `539-585`, MSCNT `587-616`, MPG `687-744` (`markVU1CodeModified`), DIRECT/HL `776-795`, UNPACK `837-1128` (writes `m_vu1Data`, and in modes 1/2 VIF1 ROW `1106-1108`); `drainPath3IfUnmasked` `:407` | VU1 code/data, `vif1_regs`, PATH2/PATH3 state, arbiter | Runs **unchanged on the worker**. |
| 4 | MSCAL/MSCNT callbacks | `src/lib/ps2_runtime.cpp:1289-1324` | read `currentContext()->vu0_fbrst` bits 10/11 (D/T enable), run VU1, write `vu0_vpu_stat` bits 9/10 | Worker uses the **FBRST snapshot taken at submit**. The sync build reads FBRST at the same instant because every MSCAL of a delivery runs inside the kick. For the VPU_STAT write, see #10. |
| 5 | VU1 run | `src/lib/vu/ps2_vu1_core.cpp:1343` execute / `:1388` resume / `:1408` run; FP control `:1421-1422`; recomp lookup `:1451` (→ `ps2_vu1_recomp.cpp:97,124` via `getVU1Code()`/generation); XGKICK `:783-803`, `finishXgkick` `:771-779` (PATH1 `submitGifPacket`, drain now); D/T stop only when enabled `src/lib/vu/ps2_vu1_step_impl.h:463-489` | VU1 state, VU1 memory, arbiter | Worker. The generated VU1 code is untouched (VR2 stays in its lane). |
| 6 | GIF arbiter → GS frontend | `src/lib/gs/ps2_gif_arbiter.cpp:73-86` submit, `:88-121` drain (stable sort by path: the output depends on what is queued at drain time); process fn `ps2_runtime.cpp:1266-1267` → `GS::processGIFPacket`; SIGNAL/FINISH/LABEL write `csr`/`siglblid` atomics `src/lib/gs/gs_frontend.cpp:2029-2066` | arbiter queue, GS frontend state, GsWorker producer side | Worker. The GsWorker queue is mutexed. Only one producer runs at a time because every EE GS entry is a sync point (#9, #12). |
| 7 | PATH3 masked FIFO | `ps2_memory.cpp:2485-2528` submit, `:2415-2443` release, `:2451-2483` flush | `m_path3Masked`, FIFO | Worker (reached through jobs). |
| 8 | EE loads/stores to VU1 code/data (0x11008000/0x1100C000) | Generated code sends every non-RDRAM address to the runtime (`include/ps2_runtime_macros.h:457-530, 607-653`; `include/ps2_runtime.h:462`) → `ps2_runtime.cpp:3583-3810` Load/Store8..128 → `PS2Memory::read*/write*` → `mapVuMemory` `ps2_memory.cpp:672-708` | VU1 memory | **Sync**, then access. |
| 9 | GS privileged registers (EE) | read CSR/SIGLBLID `ps2_memory.cpp:887-906` (and `read64`), `gsPrivStore` `:1017-1084`, `gsPrivSync` `:1086-1090`; Load* priv drain `ps2_runtime.cpp:3589-3676` | GS frontend, `csr` | **Sync**. |
| 10 | CFC2 VPU_STAT / CTC2 FBRST (inline in generated EE code, **not hookable**) | `ps2xRecomp/src/lib/vu_translator.cpp:57-59` (reads `ctx->vu0_vpu_stat`), `:101` (writes `vu0_fbrst & 0x0C0C`) | D/T enable; VU1 stop bits 9/10 | **Fallback rule at submit:** if `fbrst & 0xC00` or `vpu_stat & 0x600` is set in the current context, run the delivery synchronously, inline. Otherwise every VU1 run in it ends with D/T stop false (`step_impl.h:463-489`), so the callback's VPU_STAT write is a no-op and the EE loses nothing by not waiting. |
| 11 | VIF1 register writes (FBRST RST/STC, MARK, CYCLE, MODE, MASK, ITOPS, BASE, OFST, TOPS, TOP, ITOP) | `ps2_memory.cpp:1495-1550` | `vif1_regs`, pending PATH2 | **Sync**, then write. (VIF1 register **reads** return `m_ioRegisters` in `readIORegister` `:2866+`, never `vif1_regs`, so today the EE cannot observe the unit through them. That is identical in both builds and needs no sync.) |
| 12 | HLE GS stubs and native GIF paths | `src/lib/Kernel/Stubs/GS.cpp:120-125, 766` (`consumeLocalToHostBytes`: GS→RDRAM readback), `:1198, 1209`; `Stubs/Helpers/Support.h:1902`; `Syscalls/System.cpp:107,130` (IMR); `ps2_runtime.cpp:3830-3843` (`tryProcessNativeGif*`) | GS frontend | **Sync**, placed at the GS object's entry points (see Design §2). |
| 13 | VIF1 FIFO write (0x10005000) | `ps2_memory.cpp:1331-1342` | VIF1 parse | **Sync**, then run inline. |
| 14 | CTC2 CMSAR1 → VU1 start from the EE | `ps2_runtime.cpp:2977-2995` (reads `vif1.top/itop`, runs VU1); translator `vu_translator.cpp:104` | VU1 | **Sync**, then run inline (rare: E53 prints the first 8). |
| 15 | VU0 | `ps2_runtime.cpp:2918` (VU0 on the EE); VU0 XGKICK is gated off at `ps2_vu1_core.cpp:785`; no VU0→VU1 register window exists (no 0x4000 map in `ps2_vu1_lower_impl.h`) | none | Nothing needed. If a VU0→VU1 window is ever added, it becomes a sync point. |
| 16 | VBlankStart | `src/lib/Kernel/EeScheduler.cpp:2923-2990`: pacer sleep `2924-2930`, `vsyncTick` store, GS taps (E4/VQ/capture), `completeVSync`, INTC 2, **det-hash tap** `:2990` (snapshot `:234-263` hashes VU1 data/code + `programStartCount`) | GS, VU1 memory | **Sync after the pacer sleep, before `++m_vsyncTick`**. This is the nearest unavoidable sync point. `vsyncTick` never changes while a job runs. |
| 17 | Save/load state | `src/lib/ps2_savestate.cpp:519-522` (VU1 save), `:698-700` (load), `:746` (refuses pending DMA), `:779/836` (`vif1_regs`), `:789-793/847-851` (PATH3 FIFO), `:876` | everything | **Sync** before save and before load. PCSX2 asserts the same (`MTVU.cpp:51`). |
| 18 | DMAC completion + guest DMAC handlers | `ps2_memory.cpp:2311-2355`; `drainCompletedDmacHandlers` `ps2_runtime.cpp:3753` (after the kick store) | D_STAT, CHCR (EE-owned) | Stays on the EE and runs immediately; completion is instant in the model. A handler that touches unit state hits a sync point. |
| 19 | Host presentation latch | `ps2_runtime.cpp:819-837` | GS output (host-side) | Not guest-visible. Live presents are already torn at racy cut points (`docs/facts.md`, GB2/GB3). |

**EE state the unit reads:**
- the FBRST snapshot (#4);
- the FP control word snapshot (Design §4);
- `gs_regs.vsyncTick`, which changes only at VBlank (#16, a sync point);
- the job's own byte snapshots.

**EE state the unit writes:**
- `csr`/`siglblid` atomics: EE reads and the VBlank writes are both sync points.
- `vpu_stat`: handled by the fallback rule in #10.
- Diagnostic counters and taps: every dev trace forces sync mode (Design §6).

Nothing else. **The unit never writes RDRAM or scratchpad.** GS→host readback reaches RDRAM only through the EE-side stub at #12, which is a sync point.

## Design

### 1. Guest-time model (unchanged; cite and keep)

A kick (D1/D2 CHCR store, VIF1 FIFO write, CMSAR1) completes all of its VIF1/VU1/GIF/GS-frontend
effects at the kick instant. The EE is charged zero cycles. VU1 is never observed busy. This is
PCSX2's default instant-VU1 behaviour (headline 1) and our current behaviour. The threaded build
changes only which host thread performs those effects and when on the host clock.

### 2. Worker, queue, sync

- **Knob:** `PS2X_MTVU=0|1|census`, default 0. `0` is today's code path, with the hooks compiled
  down to one predictable branch.
- **Job:** the tail of `processPendingTransfers()` from #2, i.e. an ordered list of {GIF chunk
  snapshot | VIF1 chunk snapshot}, then the drain. It also carries the FBRST snapshot and the FP
  control snapshot.
- **Bounded FIFO:** at most 8 jobs and 64 MiB of payload. When full, the EE waits. That wait is
  host time only, so it is not guest-visible.
- **Unit thread:** one worker (`MTVU`) that runs jobs strictly in FIFO order and publishes
  `completed` (release) after each job.
- **`mtvu::syncFromEe()`:** returns at once on the unit thread (a `thread_local` flag). Otherwise, if
  `completed == submitted` (acquire), it returns. Otherwise it spins briefly, then blocks on a
  condvar.
- **Where the sync lives:** at object boundaries rather than at every caller, so a missed caller
  still stays correct:
  - `GS` public entry points other than `processGIFPacket` from the unit;
  - `GifArbiter::submit/drain` when called on the EE;
  - `PS2Memory::getVU1Code/getVU1Data`, `mapVuMemory` VU1 ranges, `gsPrivStore/gsPrivSync`, GS
    privileged reads, `vif1_regs` writers (#11/#14), the VIF1 FIFO;
  - VBlankStart and save/load.
- **Census mode** logs a per-reason hit counter so that any unexpected sync point shows up.
- **Ordering argument:**
  - The EE thread is the only submitter, and it submits in the program order of the synchronous build.
  - The worker applies jobs in that order to state only it touches, using inputs fixed at submit.
  - The EE touches that state only after `completed == submitted`.

  So each read sees the same bytes as the sync build, and each EE write lands between the same pair of unit operations.
- **VIF1 UNPACK against a running program:** in the model, an UNPACK after an MSCAL lands after the
  program has ended, and on the worker it is simply the next parser step. There is no concurrent
  VIF write into a running VU, so the TOPS double buffering does not need emulating.
- **GS path ordering:** PATH1/2/3 reach the arbiter in the same sequence and with the same
  drain points (the same parser code), so RR1's PATH3 EOP-window model is preserved byte for byte.

### 3. VU1 memory and code ownership

- The unit owns VU1 code/data memory, `m_vu1CodeGeneration`, `m_vu1` (the interpreter,
  decode/recomp caches and `programStartCount`), `vif1_regs`, the pending PATH2 image state, the
  PATH3 mask/FIFO, the arbiter queue and the GS frontend.
- The EE reaches any of these only through the sync hooks.
- No double buffering or copy of VU memory is needed. The EE never reads it while a job is in
  flight, because it waits first.

### 4. FP environment and stack

- VU1 `run()` derives its control word from the calling thread's word (`ps2_vu1_core.cpp:1421`;
  `ps2_fpmode.h:55-67` keeps every bit except RMode/FZ). The GS frontend runs under the caller's
  mode (see `docs/facts.md` E52/E53 on PATH1).
- The worker therefore **sets the FP control word snapshotted at submit** before each job. This
  keeps FPCR/MXCSR bits such as DN/AH/DAZ identical to the GameThread's.
- The worker's stack size comes from `PS2X_GAME_THREAD_STACK_KB`, so the 512 KB test covers it too.

### 5. Save states

- Sync before save and before load, so no in-flight job ever exists in a state. SS1/SS2 formats
  are unchanged.
- After a load the queue is empty, and the worker needs no state of its own: it holds nothing
  between jobs.

### 6. Diagnostics and fallbacks

- Force sync mode (`PS2X_MTVU` treated as 0) when any dev tap that keeps global or unit-crossing
  state is armed:
  - E36/E37 VU1 traces (their MSCAL context stash is consumed in `execute`);
  - E40 payload map;
  - RR1 taps;
  - E7;
  - GS capture;
  - `PS2X_PK`;
  - gfx-stats `top`.
- The D/T fallback is in #10.

### 7. Android / iOS threading

- **Odin:** the GameThread is pinned with `PS2X_GAME_THREAD_CPUS`
  (`include/ps2_thread_affinity.h:3-6, 58-70`, N11). Proposal:
  - the GameThread on prime core 6;
  - the unit on prime core 7, through a new `PS2X_MTVU_CPUS`;
  - the GS worker and present threads stay off the prime pair.

  The two prime cores share their cluster L2, which suits the VU1 data handoff. This must be
  measured on the device: N11 found Odin menus GsWorker-bound in Turnip's CPU side, so the unit
  could end up feeding a GS worker that is already saturated.
- **iOS:** there is no affinity API, so the worker runs at QoS USER_INTERACTIVE. The same knob
  applies.
- **Mac:** there is no pinning. The speed ABBA runs unpaced as usual.

## Proposed stage plan (revised; the orchestrator decides)

**Stage 2′ — hooks + census, synchronous (≤ 3 builds, bradflix det + mini speed).** Stage 2 as
written, a semantics change, is a no-op. Replace it with:
- Land the knob, the sync hooks, the job packaging in `processPendingTransfers`, and a census.
  With `PS2X_MTVU=census`, still synchronous, the census records per VBlank interval:
  - host ns of each would-be job;
  - EE host ns from each job submit to the next sync point, by reason;
  - the per-reason sync counts.
- Acceptance:
  - det-hash IDENTICAL to the current key with the knob at 0 and at census (bradflix, plus 512 KB);
  - suite green;
  - runner-dir check empty.
- Then a small offline replay turns the census log into a predicted threaded wall time per frame
  (a two-timeline schedule: EE and unit).
- **Go/no-go for stage 3** rests on that prediction for the race window (t1800–2400) on the mini. The
  Odin census is scheduled by the orchestrator.

**Stage 3 — threaded (`PS2X_MTVU=1`)**, as in the brief:
- det-hash IDENTICAL to the current key, 3× Mac and 3× bradflix, plus 512 KB;
- a jitter stress run (a random 0–2 ms sleep before each job, `PS2X_MTVU_JITTER`) still IDENTICAL;
- Mac speed ABBA against stage 2′ with the knob at 0;
- stop before the Odin.

Stage 3 also adds a unit test: a synthetic VIF1 stream with MSCAL + XGKICK + DIRECT + MSKPATH3
windows gives an identical GIF packet sequence in sync and threaded modes, including forced sync
points between jobs.

## Risks and gaps

- **Overlap may be small.** If SSX 3 kicks its VIF1 list late in the frame, or touches the GS
  (CSR polls, privileged writes, HLE GS stubs) soon after the kick, the EE waits right away. The
  census answers this before any threading work. It is the main gap.
- **GS worker becomes the bottleneck on the Odin** (N11). The threading moves the frontend's
  producer load off the GameThread but does not shrink it.
- **Snapshot cost:** normal-mode VIF1/GIF transfers get a new copy (chain transfers are already
  copied). The race GIF chain is about 337 KB per frame (RR1 E2), which is small next to 47 ms. The census measures it.
- **Hooks at object boundaries** could fire from non-EE host threads (the debug panel). Those would
  wait on the unit in host time only. That is harmless for determinism, and the debug panel is
  dev-only.
- **Not verified in this stage:**
  - that nothing outside the listed entry points reaches `GS`/`GifArbiter`/`vif1_regs`. The census
    reason counter plus a debug assert (unit-owned object touched off the unit thread while a job
    is in flight) will catch misses in stage 2′;
  - PCSX2 defaults were read from GitHub at P (`pcsx2/Pcsx2Config.cpp`, not in Q1/src).
- **VR2:** nothing here touches generated VU1 code or the pair/block emitters. The hooks sit in
  `ps2_memory.cpp`, `ps2_runtime.cpp`, `EeScheduler.cpp`, `ps2_savestate.cpp`, a new
  `mtvu.{h,cpp}`, and the GS/arbiter entry points. I will rebase onto fork `ssx3` when VR2 folds.

## Budget used (stage 1)

0 builds, 0 boots, 0 device runs. Reads only. The worktree `~/dev/ssx3-work/MT1/PS2Recomp` holds a
clean checkout of `fb28d99`.

## Orchestrator gate, stage 1 (2026-09-26)

**Pass; revised plan approved.** The key finding — our synchronous VU1 already is PCSX2's default
instant-VU1 model (cited from PCSX2 source), so threading needs no semantics change and must be
det-IDENTICAL to the **current** key — makes the proof stronger and removes the parity re-baseline.
Owning the whole VIF1 → VU1 → GIF → GS-frontend unit (not VU1 alone) is right given SSX 3's 20–31
MSKPATH3 windows per frame. Go with **stage 2′** (hooks + census, synchronous, det-identical at
knob 0 and census; offline two-timeline replay predicts the threaded frame time). Add the debug
assert for unit-owned objects touched off-thread in census mode. Stop after 2′ with the prediction;
stage 3 is decided from it. Budget as proposed (≤ 3 builds).

## Stage 2′ — hooks + census, synchronous (worker, 2026-09-26)

### Result

- **Exact at both knob settings.** Every det boot is **IDENTICAL** to the current key
  `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` (hash ticks 1..2400 and snd/coverage):

  | Host | Commit | Knob-0 boots | Census boots |
  | --- | --- | --- | --- |
  | Mac | `e708185` | 1 | 1 |
  | bradflix | `965de96` | 2 (default stack, 512 KB) | 2 (default stack, 512 KB) |

  - Suites: 668/668 (Mac det; bradflix det, run from the fork root), 664/664 (Mac non-det).
  - The runner-dir check is empty.
  - Census costs nothing measurable: race 30.52 vsyncs/s at knob 0 against 30.48 and 30.45 with
    census, in one exclusive hold on the mini.
- **The debug assert did its job.**
  - The first census run reported 6,981 `VIOLATION site=gs-drain`. `PS2Runtime::Load*` drains the
    GS queue for a privileged read (`PS2X_GS_CSR_DRAIN`, on by default) *before*
    `PS2Memory::read32`, where the sync sat. A threaded build would have raced there.
  - Fixed in `d52a18e`, which syncs before the drain. It is **0 violations** since then, on Mac and
    Linux, with and without the 512 KB stack.
- **Prediction** (mini M5 Pro, race t1800–2400, clean non-det census, two runs; model, not a speed
  measurement). Today's frame is 31.7 ms: EE 12.5 ms plus unit 19.2 ms, 8 jobs per frame.

  | Scenario (rules added on top of the stage-1 design) | EE wait/frame | Threaded frame | Predicted | + 2 µs submit / 20 µs wake / unit ×1.10 | ×1.25 |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | S0 as hooked (every CSR read syncs) | 19.0 ms | 31.5 ms | **1.005×** | 0.95× | 0.87× |
  | S1 masked CSR reads free (below) | 13.0 ms (VBlank) | 25.6 ms | **1.24×** | 1.15× | 1.04× |
  | S2 S1 + GS privileged writes queued in stream order | 13.0 ms | 25.6 ms | 1.24× | 1.15× | 1.04× |
  | S3 S2 + no VBlank sync outside det-hash ticks, unit ≤ 1 frame behind | 6.6 ms | 19.2 ms | **1.65×** (= ideal max(EE, unit)) | 1.49× | 1.32× |

  - The two census runs agree within 0.2 %.
  - The Mac race would go from 30.5 to about 37.8 vsyncs/s under S1, or about 50 under S3, at ideal
    handoff. These are model numbers, not measured speed.

### What the census shows

One race frame (t2100, clean build, host ms from VBlankStart; `frame-t2100-events.txt`):

```
0.06  CSR poll @0x382c30 (FIFO-empty spin), then display flip: PMODE, SMODE2, DISPFB1, DISPLAY1, BGCOLOR
0.10  2 small jobs (FIFO write, 1.3 µs DMA)
5.99  CSR poll @0x3828e0
7.46  FIFO job, CSR poll @0x3829d8
7.62  THE frame's VIF1 list: one job, 18.0 ms of unit work (VU1 + VIF + GS frontend)
7.64  FIFO job, CSR poll @0x382aa0   <- S0 waits the whole 18 ms here
7.65  0.14 ms job
10.09 VBlankStart                     <- S1/S2 wait here: only ~2.4 ms of EE work follows the list
```

- **Per frame:** 5 DMA jobs, 3 VIF1 FIFO jobs, 4 CSR loads, 11 GS privileged writes (the 5
  display registers plus `gsPrivStore`'s own and the VBlank CSR store), and 1 VBlank.
- **Other sync reasons:** VU1-memory, VIF1-register, CMSAR1, HLE-GS, native-GIF and D/T-fallback
  syncs are 0 in the race. In the whole boot there are 2 VIF1-register writes, 0 CMSAR1 and 0
  fallbacks. The D/T rule never fires on SSX 3.
- **CSR reads:** 278,530 of 278,532 CSR loads in the boot are the four spin sites
  `ld v0, CSR; andi v0, v0, 0xC000; bne …0x4000` (`ee-at`, `pklog-csr-t1990-2001.txt`), a GS-FIFO-empty
  wait. The value is always `0x4008`.
- **Snapshot copies:** normal-mode source copies are 3.9 MB over the boot (1.1 ms total). They are
  negligible.

### The rules S1–S3 need (all exact; for the stage-3 gate)

- **R1 (S1): a CSR load that the next instruction masks away from the unit's bits needs no sync.**
  - The unit writes only CSR bits 0–1 (SIGNAL/FINISH, `gs_frontend.cpp` `fetch_or(0x1/0x2)`) and
    SIGLBLID.
  - CSR's FIFO field is HLE'd constant (`kGsCsrFifoEmpty`, re-imposed on every CSR write in
    `ps2_memory.cpp`).
  - VSINT/FIELD come from the EE's VBlank store (`ps2xGsCsrVBlankStart`).
  - So after `ld rt, CSR` followed by `andi rt, rt, imm` with `imm & 3 == 0`, all architectural
    state is independent of the unit.
  - The census already classifies loads this way (`ps2_mtvu::privReadReason` reads the two guest
    instructions at `ctx->pc`). Stage 3 would skip the wait for `GsPrivReadMasked`.
  - It must also skip the host-only `drainQueue` for such a read, because the CSR value lives in
    an atomic and not in the GS stream.
- **R2 (S2): EE GS-privileged writes join the unit queue** in stream order, instead of making the
  EE wait. Two exceptions:
  - A CSR store that only touches EE-owned bits (VSINT W1C, FIELD, the VBlank OR) applies
    directly on the EE. It commutes with the unit's bit-0/1 ORs, and it keeps R1's VSINT polls
    (`andi 8` at 0x382c64) free.
  - A CSR store that W1C-clears bits 0–1 still syncs.

  S2 buys nothing on this route: every write lands while the unit is idle. R2 is needed only as a
  prerequisite for S3.
- **R3 (S3): VBlankStart is not a sync point outside det-hash ticks.** The unit trails by at most
  one frame (a bounded queue).
  - Guest-visible VBlank work (INTC 2, vsync callback, `completeVSync`, CSR VSINT through R2) does
    not read unit state.
  - The unit reads `vsyncTick` only in diagnostics (E7/RR1/E39/E40/UV1 taps, GS capture, packet
    VRAM trace; all force sync mode) and in the paraLLEl present request's field phase
    (`ps2_gs_parallel_backend.cpp:312`), which is presentation, not guest state.
  - Det-hash ticks must still sync, because the snapshot hashes VU1 memory and
    `programStartCount`. So a det run with `--hash-every 1` exercises S2 timing, and S3 needs a det
    run with a sparse hash (for example every 60th tick) plus the jitter stress run to exercise the
    lagged schedule.
  - **Cost:** presentation can show the GS state up to one frame later (latency, not a guest
    change). R3 is the one rule that changes host presentation timing.

### Odin projection (rough; needs an Odin census)

N12's race frame is 68.3 ms, with VU1 at 46.7 ms and GameThread-minus-VU1 at 21.6 ms. The unit
also carries VIF parsing and the GS frontend; on the Mac, unit share (60 %) ≈ VU1 share (57 %) +
3 points. So on the Odin the unit is roughly 50 ms and the EE roughly 18 ms.

- **S3:** about 68/50 ≈ **1.35×** at the ideal bound.
- **S1:** about **1.1×**, if the Odin frame has the Mac's shape: roughly 60 % of EE work before the
  list kick.

The Odin runs unit-bound under every scenario. After threading, VR2's VU1 work is the whole lever.
The census knob works in any build (`PS2X_MTVU=census`, `PS2X_MTVU_CENSUS_OUT=`), so one Odin APK
census run would replace this projection with a measurement.

### Fork commits (branch `mt1` from `fb28d99`, not pushed; bradflix private ref `refs/mt1/census`)

| Commit | Change |
| --- | --- |
| `e708185` | `include/ps2_mtvu.h` (header-only; off = one cached-flag branch per hook). Sync hooks at VU1-memory MMIO (`mapVuMemory`), GS privileged reads, writes and sync, VIF1 register writes, CMSAR1, HLE GS stubs (`applyGsClearPacket`, `applyGsRegPairs`, the StoreImage readback, SwapDBuffDc clears), native GIF kicks, VBlankStart (after the pacer), save/load. Job scopes around GIF + VIF1 + drain in `processPendingTransfers` (VIF0 paused out) and around VIF1 FIFO writes. `touch()` asserts in 10 GS entry points, arbiter submit/drain, and the PATH3 FIFO. D/T fallback rule. Snapshot-cost timing. |
| `d52a18e` | Sync before the GS CSR drain in `Load*`, the bug the assert found. |
| `965de96` | Census logs every sync hit (spins collapsed) with pc or address. Masked-CSR classification. `PS2Memory` privileged reads assert instead of syncing (`Load*` syncs). |

- No header that generated code includes was touched, so ccache kept every game TU:
  - Mac builds took 76 s and 83 s;
  - bradflix took 394 s, in a private clone `HS1/PS2Recomp-mt1` with build dir `HS1/mt1-det`, so
    the shared checkout was never switched while VR2 was building.
- No generated VU1 code or emitter was touched (VR2 stays in its lane).
- Edits in G-lane files are one-line `touch()` calls in `gs_frontend.cpp` and `ps2_gif_arbiter.cpp`.

### Commands

- Builds:
  - `mac_build.sh …/MT1/PS2Recomp …/MT1/build-det --det` (`e708185`, runner `1daf8e8b…`);
  - `mac_build.sh …/MT1/PS2Recomp …/MT1/build-rel` (`965de96`, runner `8c66106b…`);
  - bradflix: `bradflix_build.sh`'s configure/build lines with `-S /work/PS2Recomp-mt1`, det=ON
    (`965de96`, runner `d97fc507…`, two matching reads). Inputs were verified against the mini
    pins first: vu1gen `aa8127bc…`, codegen register and vf0, PGS `1b3a294`, Granite `166ba21`.
- Det boots: `ssx3_boot.py [--host bradflix] --mode det --backend parallel --runner R --label L --vu1-stats
  --dump-ticks 1090,1800,2100 --route fr1r1 [--env PS2X_MTVU=census] [--stack-kb 512]`, then
  `baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` (`det-compares.txt`).
- Census/speed (mini, exclusive, A-B-A): `ssx3_boot.py --mode speed --backend parallel --runner build-rel
  … [--env PS2X_MTVU=census --env PS2X_MTVU_CENSUS_OUT=…]`. Rates come from `race_rate.py` on
  `trace.jsonl`. The model is `mtvu_sim.py <events> [--submit ns --wake ns --slow f]`
  (`model-mini.txt`, `census-summary.txt`).
- CSR sites: one Mac det boot to t2005 with `PS2X_PKLOG=1`. The 66 MB log was deleted after
  extracting `pklog-csr-t1990-2001.txt`.

### Gaps

- **The model is the model.**
  - It assumes the unit's work costs the same on another core (the `--slow` sweep covers that).
  - It ignores GS-worker contention. The unit becomes the GS producer while the EE runs, and N11
    already found the Odin GS worker-bound in menus.
  - It ignores cache effects of the snapshot and job handoff.
- **R1–R3 are argued from source and have not been run threaded.**
  - R3 also needs `PS2X_GS_CSR_DRAIN` semantics revisited for masked reads.
  - The EE-applied CSR path must be kept equal to what `gsPrivStore` does in stream order for the
    GS capture/replay tools (GB2/GB3), or those tools must force sync mode.
- **Presentation latency under S3** (≤ 1 frame) is not measured.
- **The Mac det census ran on `e708185`, before the fix.** The final commit's det identity comes
  from the four bradflix boots.
- **Budget used:** 3/3 builds (2 Mac, 1 bradflix). 12 boots:
  - 2 Mac det, 1 Mac PK-log, 3 mini exclusive speed/census;
  - 4 bradflix det;
  - plus the 2 stage-1-era Mac det boots counted in the first two.

  Mini exclusive hold: about 3 min. Scratch: `~/dev/ssx3-work/MT1` 1.8 GB (`build-rel` kept as the
  stage-3 knob-0 control; `build-det` removed). bradflix `HS1/mt1-det` and `HS1/PS2Recomp-mt1` are
  kept for stage 3.

### Recommended next action (orchestrator decides)

The go/no-go turns on R3.

- **S1 alone:** about 1.24× on the Mac at ideal handoff, 1.15× with realistic costs; the rough Odin
  projection is about 1.1×. That is modest for the ordering risk it carries.
- **S1 + R2 + R3:** reaches the max(EE, unit) bound on both hosts: 1.65× on the Mac (1.3–1.5×
  with costs) and roughly 1.35× on the Odin, where it is capped by the unit, i.e. VU1.

**Recommendation:** approve stage 3 with R1–R3 behind `PS2X_MTVU=1`, with these det proofs:
- hash-every-1 runs, which exercise the S2 schedule;
- sparse-hash runs, which exercise the S3 lag;
- the jitter stress run.

Also schedule one Odin census before stage 3 finishes, so the Odin number is measured rather than
projected.
