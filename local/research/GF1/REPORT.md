# GF1 — the GS frontend on the MTVU unit thread: measured share and design

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/GF1.md`, 2026-09-26 from ~09:55 EDT.
**Stage 1 (measure + design) only. Stopped for the gate.**
- Fork worktree `~/dev/ssx3-work/GF1/PS2Recomp`, local branch `gf1` = fork `ssx3` **`b97b241`**,
  no commits.
- 0 builds, 1 diagnostic Mac boot (one lease slot), 0 device time.
- Source paths are relative to `ps2xRuntime/` at `b97b241`.

## Headline

1. **The GS frontend already runs on its own thread, the GsWorker.** The unit thread does not
   decode GS packets.
   - In queued mode, `GS::processGIFPacket` on a non-worker thread copies the packet into a
     `GsCommand` and enqueues it. It returns without decoding (`src/lib/gs/gs_frontend.cpp:1094-1106`).
   - The decode runs later on the GsWorker in `GS::executeQueuedCommand` (`:349-359`), right after
     paraLLEl's `RawGifPacket` (`:1121-1122`).
   - So the brief's premise, that the unit owns the GS frontend and moving it off would take
     "several ms" off the critical path, does not hold as stated. What the unit owns is the **GIF
     arbiter plus a per-packet handoff** into the GsWorker queue.
2. **That handoff costs 4.24 ms per frame of the unit's 30.3 ms on-CPU time on the Odin (14 %).**
   This is above the brief's ~2 ms stop line, so I designed rather than stopped.
   - **2.79 ms of it is the futex wake in `condition_variable::notify_one`.** This is one real
     wakeup of a sleeping GsWorker per GIF drain, i.e. per XGKICK. CP1 counts the GsWorker at about
     430 sleeps per frame.
   - Copies, allocator and lock work make up about 1 ms. Arbiter logic and packaging make up the
     rest.
   - Off-CPU, the unit also waits **6.6 ms per frame on a full GS queue** (CP1 R2b, pre-D1, no
     LAG). It is starved for 11.9 ms.
3. **On the Mac the unit-side share is smaller: 9.0 % of on-CPU time**, of which the wake is 3.1 %.
   The unit's waiting there is mostly queue-full backpressure too: about 300 of 335 waiting
   samples.
4. **Design recommendation: don't add a thread; make the handoff cheap.** A new GS-frontend stage
   between the unit and the GsWorker would need the same per-packet handoff (the wake *is* the
   cost), and it would add a third hop.
   - **Proposed:** handoff levers H1–H3 (one command per packet, move instead of copy, coalesced
     wakes), plus H4 (a deeper descriptor queue against the queue-full waits).
   - All four are host-transport-only and exact by construction.
   - Expected: about −2.5 to −3.3 ms per frame of unit on-CPU time on the Odin (estimate), plus
     part of the 6.6 ms queue-full wait.
   - The literal "second stage" worth having is splitting **the GsWorker** (our decode off
     paraLLEl's thread, option D). It is deferred until CP2 shows the GsWorker's CPU gating after
     the Turnip fix. **Your call.**

## Table 1 — MTVU unit thread on the Odin, on-CPU (CP1 R2b profile, ms per guest frame)

- **Source:** CP1 R2b `perf-R2b.data` (`1f835a3a…`, 20.02 s, 405 record frames, MTVU tid 30588),
  re-read with NDK 28.2 `simpleperf_report_lib` in `on-cpu` / `off-cpu` trace modes. CP1's
  published tables mixed on-CPU and off-CPU time.
- **Symbols:** the play build's unstripped `.so` `01fceae5…` (BuildID `837d7dbb…14fa` = APK
  `825b436d`), plus the device `libc.so` `dd242326…`.
- **Build:** fork `5d5c382`, before VR4's D1. D1 changed only the VU1 FMAC core. Between `5d5c382`
  and `b97b241` the GIF/GS transport is unchanged: SS3 touched only save-state fields. So these
  per-frame GS-path costs should carry over to the current build; the frame counts are guest-fixed.
- **Receipts:** `gsshare-R2b.txt`, `gsshare2-R2b.txt`.

| Slice | ms/frame | Note |
| --- | ---: | --- |
| MTVU on-CPU total | **30.29** | CP1 schedstat 30.1 (agrees) |
| inside `VU1Interpreter::run` (VU1 + XGKICK path) | 28.48 | |
| **GS-handoff subtree** (any frame in `submitGifPacket` / `flushMaskedPath3Packets` / `GifArbiter::*` / `GS::*` / `GsWorker::*`) | **4.24** | **14.0 %** of on-CPU |
| – of which `condition_variable::notify_one` (futex wake, kernel) | **2.79** | ends in `GifDrainBatch` → `GsWorker::endBatch` (`src/lib/ps2_memory.cpp:29-43`, `gs_worker.cpp:89-100`) |
| – other kernel leaves | ≈ 0.21 | |
| – `memcpy` | 0.25 | two copies per packet: arbiter `submit` (`ps2_gif_arbiter.cpp:84-85`) and `GsCommand.bytes.assign` (`gs_frontend.cpp:1102`) |
| – allocator (scudo, new/malloc/free) | ≈ 0.22 | two vectors per packet, plus the `deque<GsCommand>` blocks |
| – mutex lock/unlock and atomics | ≈ 0.3 | three lock rounds per packet: `NoteGifPath` enqueue, `GifPacket` enqueue, `endBatch` |
| – arbiter logic, `stable_sort`, `processGIFPacket` packaging, `touch()` | ≈ 0.45 | |
| `progressXgkick` inclusive (the XGKICK path incl. the handoff) | 4.61 | |

**Why the wake costs so much.** Bionic's `pthread_cond_signal` skips the futex when there are no
waiters on LP64 (`__pthread_cond_pulse`, bionic `libc/bionic/pthread_cond.cpp`). So each of these
wakes found the GsWorker asleep. The GsWorker drains a packet faster than the unit produces the
next one, sleeps, and is woken again: about 430 context switches per frame (CP1: 181,700 per
420 frames). That works out to about 6.5 µs per wake on cpu7 (inferred: 2.79 ms ÷ ~430).

## Table 2 — MTVU off-CPU and GsWorker on-CPU on the Odin (same profile, ms/frame)

| Thread / slice | ms/frame |
| --- | ---: |
| MTVU off-CPU total | 19.19 |
| – starved (`Worker::loop` job wait) | 11.91 |
| – **GS queue full** (`GsWorker::enqueue` → `m_hasSpace.wait`, `gs_worker.cpp:49-59`) | **6.59** |
| – GS-path mutex contended | 0.43 |
| GsWorker-30557 on-CPU total | 10.65 |
| – our GS frontend decode (`GS::processGIFPacket` body: `writeRegisterPacked`, `vertexKick`, `buildDrawBatch` …) | 3.65 |
| – paraLLEl (`GSParallelBackend::RawGifPacket` → `GSInterface::gif_transfer` …) | 3.73 |
| – outside `executeQueuedCommand` (queue pop, `GsCommand` move, wait/wake, libc 1.26, kernel 1.03, Turnip 0.35) | 3.25 |

Side findings on the GsWorker, for later and not in scope (`gswincl-R2b.txt`):
- `ps2_gfx_stats::detail::ensureInit` costs **0.39 ms/frame of self time** on a stats-off build.
- `GS::buildDrawBatch` and `vertexKick` cost 0.65 and 1.98 ms/frame inclusive. That is CPU draw
  batches built while paraLLEl renders from the raw stream.

## Table 3 — Mac (M5 Pro), MTVU unit thread (`sample`, diagnostic)

- **Boot:** a VR4 D1 runner `929b9e9a…` (SIMD on, same GS transport as `b97b241`),
  `PS2X_MTVU=1 PS2X_MTVU_LAG=1 PS2X_VU1_BLOCKS=1`, FR1-R1, paraLLEl. One lease slot, no other
  boots, load 3.2 at start.
- **Sample:** `sample` at 1 ms from race tick ~2090, 2,629 samples per thread.
- **Receipts:** `mac-split.txt`. The raw sample stays in scratch (`mac-sample.txt`
  `5cf57812…`).
- **Label:** a profiler-attached diagnostic, not a speed number.

| Slice | samples | share |
| --- | ---: | ---: |
| MTVU on-CPU | 2,294 | 100 % |
| GS-handoff subtree, on-CPU | 207 | **9.0 %** |
| – wake (`__psynch_cvsignal`) | 71 | 3.1 % |
| – memcpy / locks / allocator | 40 / 29 / 25 | 4.1 % |
| MTVU waiting | 335 | |
| – GS queue full (`GsWorker::enqueue` → cv wait) | ≈ 300 | |
| – starved | 24 | |

On the Mac, the GsWorker spends 807 of 2,630 samples in `LatchPresent` →
`GSParallelBackend::Present` → `Device::wait_idle`. That is why the unit hits a full queue there.
My boot used the driver's default present path, not the Odin play env's
`PS2X_PGS_PRESENT_PIPELINE=1` (gap below).

## What the unit's GS path reads and writes (the observability map the brief asked for)

Per XGKICK (`VU1Interpreter::finishXgkick` → `PS2Memory::submitGifPacket(Path1, drainImmediately)`,
`ps2_memory.cpp:2703-2747`):

1. `GifArbiter::submit`: copies the packet into the arbiter queue (`ps2_gif_arbiter.cpp:73-87`).
2. `GifDrainBatch` → `beginBatch`, then `drain()` (`:89-133`), which sorts by path priority and
   for each packet:
   - the listener enqueues a `NoteGifPath` command, because the raw-GIF backend needs the path
     (`ps2_runtime.cpp:1293-1305`, `gs_frontend.h:152-163`);
   - `processFn` → `GS::processGIFPacket` copies the packet into a `GifPacket` command and
     enqueues it.
3. `endBatch` notifies once.

PATH3 (`flushMaskedPath3Packets`, the masked FIFO) and the job-end drain in
`processPendingTransfers` (`:2497-2514`) take the same route.

- **The unit-side arbiter and handoff write nothing the EE can observe.** The arbiter queue is
  unit-owned (MT1 map #6). The `GsCommand` queue is only read by the GsWorker.
- **All guest-visible GS state is written on the GsWorker, in FIFO order.** That covers CSR
  SIGNAL/FINISH/LABEL, SIGLBLID, transfer and readback state, and VRAM.
- **The EE reaches that state only through RPCs** that enqueue behind everything and wait: Fence
  (`drainQueue`, `:211-238`), Consume, ReadVram, Reset, and LatchPresent. The one exception is
  the atomics that MT1's R1/R2 rules already cover.
- **Consequence:** the order in which commands reach the GsWorker is the whole contract. The
  timing of wakes and the queue depth are not guest-visible.
- **Sync points are unchanged:**
  - MT1's list (VBlank, CSR reads with R1, privileged writes, save/load);
  - the GS RPCs above;
  - `enqueue`'s full-queue wait, which is host time only (GB2 design, `gs_worker.h:17-23`).

## Design options (for your gate)

| Option | What | Thread | Exactness argument | Expected (Odin) | Cost / risk |
| --- | --- | --- | --- | --- | --- |
| **A** (brief, literal) | a new GS-frontend thread taking the arbiter drain and packaging off the unit | new | a stream of {packet, drain marker} events in unit order, so the arbiter sorts the same sets | ≤ 1.4 ms (arbiter + packaging), *minus* a new unit → stage handoff of the same kind as today's | adds a hop; the 2.8 ms wake moves rather than going away unless the handoff is fixed, and once it is fixed A buys little. **Not recommended** |
| **H1** | one command per packet: `GifPacket` carries `pathId` (the field exists), so there is no separate `NoteGifPath` | unit + GsWorker | today `NoteGifPath` always immediately precedes its packet in the same drain loop, nothing lands between them, and the worker sets `m_curGifPath` then processes, which is the same order | half the enqueues, locks and deque pushes on both threads (≈ 0.3–0.4 ms unit) | small. Keep a "has path" flag for callers that never noted a path. The replay-only pkt-seq digest (`gs_frontend.cpp:300-307`, `gs_replay_core.cpp:230`) must mix the note byte as before |
| **H2** | move, don't copy: the arbiter's `pkt.data` vector moves into `GsCommand.bytes` (new `processFn` overload) | unit | same bytes, one fewer allocation and copy | ≈ 0.2–0.3 ms unit | small; the G44 shadow and listener still see the data before the move |
| **H3** | coalesced wakes: inside a unit batch, `endBatch` notifies only when ≥ W commands are pending (W ≈ 32–64) or the queue is past half full. **Forced notify** at unit job end, before any producer blocks on a full queue, and on every non-batched enqueue (all RPCs and EE commands) | unit | wake timing only; FIFO order and contents are unchanged; RPCs still notify before waiting | most of the **2.79 ms** wake (÷ W wakes) on the unit, and fewer GsWorker sleep/wake cycles (part of its 3.25 ms "outside") | a missed forced notify stalls the GsWorker until the next enqueue. Guard with the jitter stress and a census assert (GsWorker idle with commands pending for > N ms) |
| **H4** | deeper descriptor queue: `kDefaultMaxDescriptors` 1024 → 8192 behind a knob; the 16 MiB byte cap is unchanged | — | host bound only (the GB2 FIFO-full stall is host time) | targets the **6.6 ms** queue-full wait. The gain depends on GsWorker headroom: ~30 of 50 ms busy before D1, less after | `LatchPresent`'s RPC waits behind a longer backlog (present latency, not guest state); memory ~1.6 MB of descriptors |
| **D** (the real "second stage") | split the GsWorker: our decode on a GS-frontend thread; paraLLEl (`RawGifPacket`, flush, present) on the GsWorker, fed the raw packet + path in order | GsWorker → 2 | paraLLEl already consumes only raw bytes + path; our decode state stays single-owner. RPCs route to the stage that owns their state, with Fence through both | −3.65 ms of GsWorker CPU (+ its share of queue overhead), **only useful while the GsWorker's CPU gates** | G-lane files; readback/present/VRAM RPCs need two-hop ordering. **Defer** until CP2's post-Turnip timeline |

**Recommended stage 2:** H1 + H2 + H3 behind one knob (the brief's `PS2X_MTVU_GSTHREAD=1` is
misnamed for this, so I propose `PS2X_GS_HANDOFF=1`, default off), and H4 as its own knob
(`PS2X_GS_QUEUE_DESC=N`) so their effects can be separated.
- **Files:** `gs_worker.{h,cpp}`, `gs_frontend.{h,cpp}` (H1/H2 paths), `ps2_gif_arbiter.{h,cpp}`
  (H2), `ps2_memory.cpp` (`GifDrainBatch`), and `ps2_mtvu.h` (the job-end flush). No generated
  code or VU1 changes. Nothing under `src/runner`.
- **Gates:**
  - det IDENTICAL to `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`, knob off and on: bradflix 3×,
    512 KB, `--hash-every 1`, plus LAG with `--hash-every 60`;
  - **GS stream identical:** the `[pk]` log (unit-side submits, unchanged by construction), plus
    a consumer-side digest of the executed commands. That means turning the replay-only
    pkt-seq digest on in live boots behind a dev env and printing it every 300 vsyncs; it must be
    equal knob on and off;
  - jitter stress: random 0–2 ms sleeps in the GsWorker consumer and before `endBatch`;
  - the census assert above at 0;
  - suites on Mac and Linux;
  - Mac ABBA (knob off / H / H + H4) on the play knobs **with** `PS2X_PGS_PRESENT_PIPELINE=1`.
- **Stage 3:** one Android build and one Odin pair on the play settings, as in the brief.
- **Budget ask:** ≤ 5 builds (Mac 2, bradflix det 1, Android 1, 1 spare), ~10 bradflix det boots,
  2 Mac holds, 4 Odin legs.

**What I expect, stated as a guess:**
- On the Odin, the unit's on-CPU time drops by about 2.5–3.3 ms per frame from H1–H3.
- Where the unit gates the frame (the early race, where D1's 5.8 ms gave +17 %), that is roughly
  +8–10 %.
- Mid-race after D1 and LAG, VR4 found the unit blocked ~18.5 ms per frame and the frame gated by
  the GsWorker/kgsl chain, so H1–H3 alone may move little there. H4 and the Turnip fix (FS2 part 3)
  are what change that window. The post-D1 split of the unit's blocked time (queue-full vs
  starved) is unmeasured, and CP2's profile would give it.

## Commands

```sh
git -C ~/dev/PS2Recomp worktree add -b gf1 ~/dev/ssx3-work/GF1/PS2Recomp fork/ssx3   # b97b241, read-only so far
# Odin profile re-read (bytesize, light; lock was FREE): stage perf data + symbols, SHA both ends
ssh bytesize 'wsl -d Ubuntu -- tee /home/brad/gf1/perf-R2b.data' < ~/dev/ssx3-work/CP1/odin/R2b/perf-R2b.data  # 1f835a3a… both ends
ssh bytesize 'wsl -d Ubuntu -- tee /home/brad/gf1/symdir/libc.so' < ~/dev/ssx3-work/CP1/libc-device.so           # dd242326… both ends
#   symdir/libps2EntryRunner.so = hard link of /home/brad/vr3/…/libps2EntryRunner.so (01fceae5…, BuildID 837d7dbb…); build_id_list via simpleperf_utils.ReadElf
python3 gsshare.py perf-R2b.data 405 > gsshare-R2b.txt   # SetTraceOffCpuMode('on-cpu')
python3 gsshare2.py > gsshare2-R2b.txt                   # MTVU off-cpu + GsWorker on-cpu split
python3 gswincl.py > gswincl-R2b.txt                     # GsWorker inclusive/self tops
# Mac (one slot, diagnostic)
local/research/GF1/macsample.sh     # boot VR4 runner-d1-clean, sample 8 s at race t≥1900
python3 macsplit.py mac-sample.txt MTVU > mac-split.txt
```

## Gaps

| Gap | Why / effect |
| --- | --- |
| The Odin numbers come from CP1's pre-D1 profile (`5d5c382`, no LAG) | no post-D1 Odin profile exists (PT1/CP2 pending). The GS transport is unchanged since, so the unit-side ms per frame should hold; the off-CPU split (queue-full vs starved) will have shifted with D1 + LAG |
| The wake count per frame (~430) is inferred | from CP1's GsWorker context switches (181,700 / 420 frames), not counted per XGKICK. Stage 2 can add a counter |
| The Mac sample window and ticks are approximate | the trace logs ticks every ~300; `sample` ran from t≈2090 until the boot's t2400 stop. I quote shares, not ms per frame |
| The Mac boot used the default present path, not `PS2X_PGS_PRESENT_PIPELINE=1` | its GsWorker `wait_idle` in Present (31 % of samples) inflates the Mac queue-full wait. The unit-side handoff share does not depend on it |
| H1–H4 gains are estimates | built on Table 1's slices; nothing was built |
| Lease release | my script's release call failed on a type error (a string slot id). I released slot 1 by hand right after, and the committed script copy is fixed |

Scratch: `~/dev/ssx3-work/GF1/` (worktree, profile scripts, the Mac sample 1.4 MB, the run dir);
bytesize `/home/brad/gf1/` (a 107 MB perf copy, symdir hard links, outputs). The mini disk is
unchanged in any meaningful way.
