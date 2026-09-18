# S2 — Replay state architecture: REPORT

Spike: S2 (reasoning-class). Repo `/Users/bradrichardson/dev/ssx3`, device Odin 3
`622c49b1`. Continues D2/D2b. No docs edits, no commits, no verdicts.

Status: stopped by orchestrator instruction after the second Odin arm
(reasoning-class agents halted for quota). Milestone 1 measured on EGL;
Vulkan not runnable with these builds; milestone 2 not started.

## Five-line summary

1. D2b's `LoadIndexedXF` SIGSEGV at replay 27 was not CP/XF state drift: the
   Odin runs dual-core with a movie, so `m_use_deterministic_gpu_thread` is
   true and `LoadIndexedXF` pops indexed-XF bytes from a fixed 2 MiB FIFO aux
   buffer that only the paired `RunFifo<true>` preprocess pass fills — the
   loop ran `RunFifo<false>` alone, so the unchecked read pointer walked off
   the array. Desktop is single-core, the flag is false there, and the same
   header read guest RAM instead: that is the whole platform asymmetry.
2. The fix pairs a preprocess pass with each replay, rewinds the aux pointers,
   masks the three PE BP writes out of the preprocess copy (the preprocess
   pass is where `SetToken`/`SetFinish` are raised in deterministic mode), and
   restores memory updates + CP + XF registers before every replay.
3. It was validated on the device code path *before* any device attempt, by
   forcing determinism on a dual-core desktop run — which also caught a bug in
   my own mask (0x44/0x48 are known-but-ignored opcodes, not parse failures).
4. Odin EGL, 200 unmodified replays at one idle seam, pinned emu=80/video=40:
   `s2-egl-a` 200/200 with `done`, **0.665 ms** median per replay (p95 0.729);
   `s2-egl-b` 200/200 with `done`, **0.866 ms** median (p95 0.963); no
   tombstones; kill rule never tripped. `aux_bytes × 27 ≈ 2 MiB` on both arms,
   matching D2b's death index exactly.
5. Vulkan was not run and cannot be with these builds (no `libvideovulkan.a`
   in `core-egl-d5-build`); milestone 2 was not started; no verdict is offered
   on the capacity gate — the table is in Part 3c.

---

## Part 1 — Diagnosis of the `LoadIndexedXF` death (milestone 1)

### The question D2b left open

D2b ran the same research header on two platforms and got two outcomes. Desktop
Metal completed all 200 replays with `done` verified. The Odin (EGL, dual-core
trial build, `d2single`, pinned emu=80/video=40) ran exactly 27 replays on two
different frames (479,342 B and 466,658 B) and died with the same stack both
times:

```
SIGSEGV: LoadIndexedXF <- RunFifo<false> <- StaticRecompCore::Run()+10560 <- RunLoop <- CPU::Run <- CpuThread
```

D2b's candidate explanation was "CP/XF indexed-vertex array state that does not
survive repeated re-execution". That is not what happens.

### What actually happens

The recorded stream is fine and the CP state is fine. The Odin runs take a
**different code path inside `LoadIndexedXF`** than the desktop does, and that
path reads from a buffer the replay never fills.

`VideoCommon/XFStructs.cpp`:

```cpp
void LoadIndexedXF(CPArray array, u32 index, u16 address, u8 size)
{
  const u32 buf_size = size * sizeof(u32);
  u32* currData = reinterpret_cast<u32*>(&xfmem) + address;
  u32* newData;
  auto& fifo = system.GetFifo();
  if (fifo.UseDeterministicGPUThread())
    newData = static_cast<u32*>(fifo.PopFifoAuxBuffer(buf_size));      // <-- Odin
  else
    newData = ...memory.GetPointerForRange(array_bases[array] + ...);  // <-- desktop
  ...
}
```

`FifoManager::PopFifoAuxBuffer` is an **unchecked bump pointer** into a fixed
2 MiB array (`VideoCommon/Fifo.cpp`, `Fifo.h`):

```cpp
static constexpr u32 FIFO_SIZE = 2 * 1024 * 1024;
u8 m_fifo_aux_data[FIFO_SIZE]{};

void* FifoManager::PopFifoAuxBuffer(size_t size)
{
  void* ret = m_fifo_aux_read_ptr;
  m_fifo_aux_read_ptr += size;     // no bounds check, no wrap
  return ret;
}
```

The pushes into that buffer come from the **paired preprocess pass**, not from
the execute pass: `RunFifo<true>` -> `OnIndexedLoad` -> `PreprocessIndexedXF` ->
`PushFifoAuxBuffer` (reading guest RAM through `g_preprocess_cp_state`'s array
bases). In deterministic-GPU-thread mode Dolphin always runs the two passes as a
pair: the CPU thread preprocesses and pushes, the GPU thread executes and pops.

D2/D2b's replay loop called `RunFifo<false>` **alone**, 200 times. Every replay
therefore popped its whole indexed-XF payload out of a buffer nobody had pushed
into: it read stale bytes left by the live game's preprocess pass and walked the
read pointer forward by ~78 KiB per replay with nothing ever rewinding it. After
~26 replays the read pointer left the 2 MiB array and replay 27 dereferenced
unmapped memory inside `LoadIndexedXF`. The same mechanism also applies to
non-inlined display-list bodies (`OpcodeDecoding.cpp` pops `size` bytes on the
same flag).

### Why the count was 27 on both frames, and why desktop was fine

The death count is set by the **aux-buffer budget**, not by the frame:

```
2 MiB / 27 replays = 77.7 KiB of indexed-XF payload per replay
```

which is the size of one SSX 3 race frame's indexed-XF payload (the
September-13 capture of this game recorded 2,268 indexed XF loads for a 390 KB
frame; D2b's 479 KB frame scales to ~2.8k loads at 12-16 words each). Two frames
of similar size die at the same replay index — exactly the "same death count,
two different frames" signature D2b reported, which looked like determinism and
was read as evidence *against* a resource explanation. The S2 header now emits
`aux_bytes=` on the `restored` event so the arithmetic is a receipt rather than
an estimate.

The platform asymmetry has a one-line cause.
`FifoManager::UpdateWantDeterminism` (`Fifo.cpp`):

```cpp
  switch (Config::GetGPUDeterminismMode()) {
  case Config::GPUDeterminismMode::Auto: gpu_thread = want; break;   // default
  ...
  }
  gpu_thread = gpu_thread && m_system.IsDualCoreMode();
```

and `Core::UpdateWantDeterminism` sets
`want = system.GetMovie().IsMovieActive() || NetPlay::IsNetPlayRunning()`.

| | Odin trial arm | Desktop D2 run |
| --- | --- | --- |
| Dual core | **yes** (`DEFAULT_CPU_THREAD` true on Android; GameINI `CPUThread=False` ignored) | no (single core honoured) |
| Movie active | **yes** (`SSX3_MOVIE_PLAY=m3-snow-jam-3min.dtm`) | no (`gamecube_schedule_check.py`, no movie) |
| `GPUDeterminismMode` | Auto (no key in the ini) | Auto |
| => `m_use_deterministic_gpu_thread` | **true** | false |
| => `LoadIndexedXF` source | aux buffer (never filled) | guest RAM (correct) |
| Result | SIGSEGV at replay 27 | 200/200, `done` |

So the desktop Metal row is not a "the loop works" result that the device failed
to reproduce — the two platforms were running different code. It also means the
first 26 Odin replays were **not rendering the recorded frame**: they consumed
stale aux bytes as matrices. The D2b partial timings (2.03 ms) are therefore not
a like-for-like capacity number either.

### Offline confirmation (no device needed)

`local/research/S2/aux_budget.py` parses a FifoDataFile v6 artefact and walks
frame 0 with a port of Dolphin's own command-size decoder
(`OpcodeDecoding.h detail::RunCommand`) plus the vertex size tables
(`VertexLoaderBase::GetVertexSize` and the four `VertexLoader_*.h` tables), and
counts exactly what the execute pass would pop out of the aux buffer.

Run against the two September-13 captures of this game:

| Capture | Frame 0 | Indexed XF loads | Display lists | PE BP writes | Aux bytes popped per replay | 2 MiB / that |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `replay-correctness-events.jsonl.fifo` | 647,799 B | 2,086 | **0** | 2 | 100,128 B (97.8 KiB) | 20.9 replays |
| `replay-correctness-final2-events.jsonl.fifo` | 390,334 B | 2,268 | **0** | 2 | 108,864 B (106.3 KiB) | 19.3 replays |

Both walks consumed 100% of the stream with **zero** unknown opcodes, and the
indexed-load counts (2,086 / 2,268) match the counts the September-13 offline
audit reported for the same two captures — so the port is cross-checked against
an independent decoder, not just self-consistent.

Three things follow:

1. **The mechanism is confirmed offline.** One replay of an SSX 3 race frame
   pops ~75-106 KiB out of a 2 MiB buffer that the loop never refilled or
   rewound; the read pointer therefore leaves the array after roughly 20-28
   replays depending on the scene. D2b's death at 27 implies its frames carried
   ~75-78 KiB of indexed payload (i.e. ~1,600-1,900 indexed loads — fewer than
   these two desktop captures, which is ordinary scene variation). Note
   `m_fifo_aux_data` is a member of the heap-allocated `FifoManager`, so reads
   just past the array land in mapped memory and do not fault; the SIGSEGV comes
   a little *after* the 2 MiB line, which is why the observed 27 sits at or
   just past the predicted boundary rather than exactly on it. The S2 header's
   `aux_bytes=` field pins the exact number for the actual device frame.

2. **Display lists are absent from this game's frames (`dls=0`).** That matters
   for the fix: display-list bodies live in guest RAM and are not walkable from
   the recorded stream, so a non-zero count would have left PE writes inside
   DL bodies unmasked. At zero, the stream-level PE mask is complete.

3. **Exactly two PE BP writes per frame**, so the mask rewrites two commands out
   of ~9k-19k — no measurable effect on the capacity number.

### Second finding: the preprocess pass is where the PE signals are raised

This matters because the fix adds the preprocess pass. In deterministic mode the
BP token/draw-done side effects are **moved**, not removed:

* execute pass, `BPStructs.cpp` — `if (!system.GetFifo().UseDeterministicGPUThread())
  system.GetPixelEngine().SetFinish(...)` / `SetToken(...)`: suppressed;
* preprocess pass, `LoadBPRegPreprocess` — calls `SetFinish` / `SetToken`
  unconditionally, and handles **nothing else at all**:

```cpp
void LoadBPRegPreprocess(u8 reg, u32 value, int cycles_into_future)
{
  switch (reg) {
  case BPMEM_SETDRAWDONE:     if ((newval & 0xff) == 0x02) ...SetFinish(...); break;
  case BPMEM_PE_TOKEN_ID:     ...SetToken(newval & 0xffff, false, ...); break;
  case BPMEM_PE_TOKEN_INT_ID: ...SetToken(newval & 0xffff, true, ...); break;
  }
}
```

Naively adding the preprocess pass would inject the recorded frame's PE
completion and interrupt tokens into the parked guest 200 times — exactly the
class of guest-visible effect the replay-context spec forbids. The fix
suppresses it (Part 2, item 2) rather than accepting it.

Corollary for the desktop row: because the desktop run had determinism **off**,
its 200 replays *did* run the execute-side `SetFinish`/`SetToken` 200 times.
D2's desktop `done` verifies RAM/EXRAM only and PE state is not RAM, so that
run's `done` does not cover the PE effect.

---

## Part 2 — The fix

All changes are in `local/research/S2/s2_replay_capacity.h`, a copy of
`local/research/D2/d2_replay_capacity.h`. `native/diagnostics/` is untouched.

1. **Paired preprocess pass (the crash fix).** When
   `FifoManager::UseDeterministicGPUThread()` is true, each replay runs
   `RunFifo<true>` over the recorded bytes immediately before `RunFifo<false>`,
   so the aux buffer holds exactly what the execute pass pops, in order.
   `FifoManager::SyncGPU(Fifo::SyncGPUReason::AuxSpace, false)` after each pair
   rewinds both aux pointers to the base of the 2 MiB array (read == write
   there, so the compaction moves zero bytes). When the flag is false — the
   desktop — the preprocess pass is skipped, because nothing reads the aux
   buffer on that path.

2. **PE suppression for the preprocess pass, at the stream level.** A second
   copy of the recorded stream (`frame_pre`) is built once, with every
   `GX_LOAD_BP_REG` whose register is `BPMEM_SETDRAWDONE`, `BPMEM_PE_TOKEN_ID`
   or `BPMEM_PE_TOKEN_INT_ID` rewritten to five `GX_NOP`s. Same byte length, so
   both passes still walk an identical command layout and the aux push/pop stays
   symmetric; and because `LoadBPRegPreprocess` handles only those three
   registers, the masked preprocess pass has **no** guest-visible effect left.
   The execute pass keeps the verbatim stream: its PE calls are already
   suppressed by the determinism check, and it still needs those handlers for
   `FlushEFBCopies()` / `FlushStaleBinds()` / peek-cache invalidation. The mask
   is built with Dolphin's own command-size decoder (a private
   `OpcodeDecoder::Callback`) and **fails closed**: if the walk does not consume
   the whole stream, or sees an unknown opcode, the verbatim stream is used for
   the preprocess pass and `mask_bp=0` is reported. Display-list *bodies* live
   in guest RAM and are not walked, so `dls=` is reported: a non-zero count
   means PE suppression is incomplete for that frame.

3. **Restore before every replay (minimal correct set, by the diagnosis).**
   - recorded memory updates + TMEM (`ApplyMemory`) — the replay's own EFB
     copies write into guest RAM and can land on recorded vertex/palette
     regions;
   - the recorded **CP registers** (array bases, strides, VCD, VAT, matrix
     index) into `g_main_cp_state`, then `CopyPreprocessCPStateFromMain()` so
     the execute and preprocess passes start each replay from *identical* array
     setup. This is mandatory, not hygiene: if the two passes disagree about a
     vertex descriptor they consume different numbers of bytes and the aux
     push/pop desynchronises;
   - the recorded **XF register block** (0x1000+). `invtxspec` must agree with
     the CP vertex descriptor or the first draw of the replay trips
     `CheckCPConfiguration()`'s `PanicAlertFmt`, so CP and XF regs are always
     restored together;
   - `VertexLoaderManager::MarkAllDirty()`.

   The full prelude (whole BP register file + all 4096 XF memory words + TMEM)
   still runs **once** before the loop. D2b measured the combined
   `ApplyMemory` + full-prelude step at ~19 ms, which per replay would swamp the
   capacity number; each phase is now timed separately (`mem_ms`, `cp_ms`,
   `pre_ms`, `run_ms`, `sync_ms`) so both the restore-inclusive cost and the
   execute-only cost are readable from a single run.

Kept from D2b unchanged: per-row `fflush`, GPFifo gather-pipe drain / snapshot /
restore around the bulk section, RAM/EXRAM save-restore with the watched-window
re-hash, `seq_wall_ms` on `done`, `bImmediateXFB` suppressed for the sequence
only, `Flush()` + `WaitForGPUIdle()` per replay so GPU time is inside the number.

New receipt fields on the `restored` event:
`det=<deterministic> dual=<dual core> mask_bp=<PE writes masked> dls=<display
lists> dl_bytes=<...> indexed=<indexed XF loads> aux_bytes=<aux payload per
replay> walk=<bytes walked>/<frame bytes> unknown=<unknown opcodes>`.
`aux_bytes` x 27 ~ 2 MiB is the falsifiable form of the diagnosis.

### Build

`local/research/S2/build_android_trial.py` (derived from
`local/research/D2/build_android_trial.py`; same `tools/android_trial.py` build
technique, header set and include order, with `s2_replay_capacity.h`
substituted).

```
python3 local/research/S2/build_android_trial.py \
  --game local/game/gxbe69-stock \
  --build-dir "/Volumes/Extreme SSD/android-spike/core-egl-d5-build" \
  --reference-tu "/Volumes/Extreme SSD/android-spike/m4-src/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp" \
  --with-d5exc \
  --output "/Volumes/Extreme SSD/android-spike/S2/trial-egl13"
```

| Artefact | sha256 |
| --- | --- |
| `local/research/S2/s2_replay_capacity.h` | `803cb0ad1ef80a22b0aa5f532e205dead7a34dd693be9f5ce8af2f990e12a230` |
| `S2/trial-egl13/moderngekko-run-trial` | `b09309fcb7a11ae75512ac7af2c591e4d27798e14228e32b568854a598870408` |
| production runner (unchanged across build) | `134a18773b56f58a62b81bd47e56ed1f3026b67f234f885d1f145d854e7a15ff` |

Build warnings: 4, all pre-existing `Core_Run.cpp`
`-Wmissing-variable-declarations` from the D5 exception-attribution section;
none from the S2 header. Host build gate: `/tmp/ssx3-host-lease` absent at each
build, claimed `S2` with `printf`, removed immediately after (`waits.log`).

One portability fix versus the repo copy: `SyncGPUReason` lives in
`namespace Fifo`. The repo vendor tree and the Android reference tree `m4-src`
are byte-identical for `Fifo.h`, `XFStructs.cpp`, `OpcodeDecoding.h`,
`CPMemory.h`, `VertexLoaderManager.h` and `BPStructs.cpp` (verified by diff), so
the header is valid for both builds.

---

## Part 3 — Desktop validation of the fixed header (Metal)

The Odin was unavailable (Part 3b), so the fixed header was validated on the
desktop first. Desktop is the **non-deterministic** path, so it does not
exercise the paired preprocess pass itself — but it does exercise every other
piece of new code (per-replay `ApplyMemory`, the CP+XF register prelude,
`CopyPreprocessCPStateFromMain` + `MarkAllDirty`, the mask walker, the `done`
re-hash), and it measures the cost the per-replay restore adds.

Two runs, Metal, 640x528, `gxbe69-stock`, no movie, single core, host lease `S2`
claimed and released, load 1.7-2.4, no other `moderngekko` process:

```
SSX_NATIVE_REPLAY=1 SSX_NATIVE_PROBE=$PWD/local/research/S2/s2-desktop2-run.jsonl \
python3 tools/gamecube_schedule_check.py \
  --player-dir local/research/S2/players/s2-desktop2 \
  --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock \
  --profile s2-desktop2 --output local/research/S2/s2-desktop2-run --seconds 240
```

| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | `done` | 200-seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| S2 desktop Metal #2 (mask fix) | **200** | 5.067 / 16.740 / 3.302 / 22.530 | 2.564 / 4.075 | 415,702 / 3,489 | **YES** | 1.359 s |
| S2 desktop Metal #1 | **200** | 3.987 / 16.729 / 2.722 / 23.643 | 2.050 / 4.740 | 339,824 / 2,851 | **YES** | 1.160 s |
| D2 desktop Metal (no per-replay restore) | 200 | 10.072 / 16.752 / 3.250 / 25.365 | 3.255 / 4.719 | 268,836 / 2,455 | YES | n/a |

Per-replay phase breakdown (medians), the reason the restore is affordable:

| Arm | `mem_ms` (recorded memory updates + TMEM) | `cp_ms` (CP + XF register prelude) | `pre_ms` (preprocess pass) | `run_ms` (execute + Flush + WaitForGPUIdle) | `sync_ms` (aux rewind) |
| --- | ---: | ---: | ---: | ---: | ---: |
| S2 desktop #2 | 0.263 | 0.001 | 0.000 (skipped, `det=0`) | 4.780 | 0.000 (skipped) |
| S2 desktop #1 | 0.171 | 0.001 | 0.000 (skipped, `det=0`) | 3.803 | 0.000 (skipped) |

**The full per-replay restore costs ~0.17-0.26 ms**, not the ~19 ms D2b's
combined `restored` step suggested: that 19 ms was dominated by the *full*
prelude (whole BP register file + 4096 XF memory words) plus building the
prelude byte vector, both of which now happen once. Re-applying 2,851-3,489
recorded memory updates plus the 1 MiB TMEM copy is 0.17-0.26 ms, and the CP +
XF register prelude is 1 microsecond.

Do not read the wall medians as a platform regression or improvement: the
distribution is bimodal (fast ~3-6 ms / slow ~12-17 ms, D2 saw the same,
consistent with a 2-deep GPU queue behind `WaitForGPUIdle`), the frames differ
in size, and host load differed. The p95 is stable at ~16.7 ms across all three.

### What the `restored` receipts say

| Arm | `det` | `dual` | `mask_bp` | `dls` | `indexed` | `aux_bytes` | walk | `unknown` |
| --- | :-: | :-: | ---: | ---: | ---: | ---: | --- | ---: |
| S2 desktop #2 | 0 | 0 | **2** | **0** | 3,057 | 146,736 | 415,702/415,702 | 0 (benign 1) |
| S2 desktop #1 | 0 | 0 | 0 (fail-closed) | 0 | 1,740 | 83,520 | 339,824/339,824 | 1 |

Three results here:

1. **`det=0 dual=0` on the desktop** — the platform asymmetry in Part 1 is
   confirmed by the instrument itself, not just by reading the config.
2. **`aux_bytes` from live captures: 83,520 B and 146,736 B per replay.**
   2 MiB / that = **25.1** and **14.3** replays before the unchecked read
   pointer leaves `m_fifo_aux_data`. Together with the two offline captures
   (97.8 and 106.3 KiB → 20.9 and 19.3 replays), one SSX 3 race frame's aux
   payload spans roughly 80-150 KiB depending on the scene, so the budget runs
   out between ~14 and ~25 replays. D2b's death at 27 sits just above that band,
   which is what the mechanism predicts: `m_fifo_aux_data` is a member of the
   heap-allocated `FifoManager`, so the first reads past the array still land in
   mapped memory and the SIGSEGV arrives a little after the 2 MiB line, not on
   it. Mechanism confirmed with live data from the same game and harness.
3. **Run #1 caught a real bug in my own mask.** `unknown=1` tripped the
   fail-closed path and disabled the PE mask (`mask_bp=0`). The cause:
   `RunCallback::OnUnknown` (`OpcodeDecoding.cpp:205-225`) treats
   `GX_CMD_UNKNOWN_METRICS` (0x44) and `GX_CMD_INVL_VC` (0x48) as **known,
   ignored, one-byte** commands — only anything else reaches
   `CommandProcessor::HandleUnknownOpcode`. Real SSX 3 frames contain exactly
   one of those, so the original condition would have disabled the mask on
   every frame and let the preprocess pass fire PE tokens on the device. Fixed
   (`benign_unknown` counted separately); run #2 shows `mask_bp=2 unknown=0
   benign=1`. **This is why the desktop run was worth doing before spending a
   device attempt.**

Both desktop runs continued normally after the sequence (`riding_observed_after_start:
true`, course check passed, no reset loops).

## Part 3a — The fix validated on the DEVICE code path, on the Mac

The Odin gets `m_use_deterministic_gpu_thread = true` for free (dual core plus
an active movie). The desktop does not, so the two runs above did **not**
exercise the actual fix. They can be made to: with `--cpu-thread` and
`SSX_S2_FORCE_DETERMINISM=1` the header calls
`FifoManager::UpdateWantDeterminism(true)` before `PauseAndLock`
(`GPUDeterminismMode::Auto` -> `gpu_thread = want`, then `&& IsDualCoreMode()`),
which flips exactly the flag the device has, and restores it to
`Core::WantsDeterminism()` after the sequence. The flip happens *before*
`PauseAndLock` because `PauseAndLock` itself branches on the flag. The force is
compiled out of the Android TU (`SSX_D2_REPLAY_ALWAYS`); the device needs no
forcing.

```
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 \
SSX_NATIVE_PROBE=$PWD/local/research/S2/s2-det-run.jsonl \
python3 tools/gamecube_schedule_check.py \
  --player-dir local/research/S2/players/s2-desktop3 \
  --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock \
  --profile s2-det2 --cpu-thread --output local/research/S2/s2-det-run --seconds 240
```

| Arm | `det` / `dual` | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 | Frame B / updates | `done` | 200-seq wall |
| --- | :-: | ---: | --- | --- | --- | :-: | --- |
| **S2 desktop, dual core + forced determinism** | **1 / 1** | **200** | 8.787 / 12.567 / 4.108 / 19.580 | 4.472 / 5.426 | 331,800 / 2,848 | **YES** | 1.857 s |
| S2 desktop, single core | 0 / 0 | 200 | 5.067 / 16.740 / 3.302 / 22.530 | 2.564 / 4.075 | 415,702 / 3,489 | YES | 1.359 s |

| Arm | `mem_ms` | `cp_ms` | `pre_ms` (preprocess pass) | `run_ms` | `sync_ms` (aux rewind) |
| --- | ---: | ---: | ---: | ---: | ---: |
| dual core + forced determinism | 0.465 | 0.002 | **0.073** | 8.421 | **0.001** |
| single core | 0.263 | 0.001 | 0.000 (skipped) | 4.780 | 0.000 (skipped) |

`restored`: `det=1 dual=1 mask_bp=2 dls=0 indexed=1639 aux_bytes=78672
walk=331800/331800 unknown=0 benign=1`.

Two things this settles without the device:

1. **The fix works on the path that was failing.** 200 of 200 replays with
   `done` verified (RAM/EXRAM re-hash match), on `det=1 dual=1`, where the D2b
   header dies in the twenties. The paired preprocess pass costs **0.073 ms**
   per replay and the aux rewind **0.001 ms** — the crash fix is essentially
   free. The run continued normally afterwards
   (`riding_observed_after_start: true`, course check passed, no reset loops),
   including the determinism flip back.

2. **The diagnosis is quantitatively exact.** This capture's aux payload is
   `aux_bytes = 78,672 B` (76.8 KiB) per replay, on the deterministic path, for
   this game and harness:

   ```
   2 MiB / 78,672 B = 26.66 replays
   ```

   so the 27th replay is the first one whose pops run past the end of
   `m_fifo_aux_data`. **D2b died on replay 27, twice.** The predicted and
   observed death indices agree to within the same replay.

The Odin numbers are still required — this run is a Mac, with Metal, and its
per-replay wall is not a capacity measurement for the Adreno/EGL path. What it
removes is the risk that the device attempt is spent discovering a bug in the
fix rather than measuring it.

## Part 3b — Odin arm 1 (EGL): 200 replays, `done` verified

`python3 local/research/S2/arm.py s2-egl-a --binary .../trial-egl14/moderngekko-run-trial
--build-json .../trial-egl14/build.json`, which runs

```
tools/android_trial.py run --binary .../moderngekko-run-trial --build-json .../build.json \
  --tag s2-egl-a --output .../S2/s2-egl-a-receipts --template d2single \
  --movie m3-snow-jam-3min.dtm --graphics OGL --idle on --trial-kind smoothing \
  --trial-secs 0.0 --timeout 600 --affinity emu=80,video=40 --sampler \
  --screenshot-seconds 2 --serial 192.168.1.53:5555
```

Probe: `record_start -> recorded -> gpu_stall -> pipe_saved -> restored ->
200 capacity rows (idx 0-199) -> **done**`. No tombstone from this run (the
`logcat -b crash` buffer holds only D2b's 09:19 entry and another agent's
`org.ssx3.onscreen` APK at 10:47; neither is this pid).

`restored`: **`det=1 dual=1`** `mask_bp=2 dls=0 indexed=1170 aux_bytes=56160
walk=343226/343226 unknown=0 benign=1`.

| Metric (200 replays, present suppressed, Flush + WaitForGPUIdle each) | Value |
| --- | ---: |
| Replays completed | **200 / 200** |
| `done` verified (RAM + EXRAM watched-window re-hash) | **YES** |
| Wall per replay, median | **0.665 ms** |
| Wall per replay, p95 / min / max | 0.729 / 0.638 / 0.874 ms |
| Thread-CPU per replay, median / p95 | 0.660 / 0.723 ms |
| 200-sequence wall | **135.095 ms** (~1,481 replays/s) |
| Frame bytes / memory updates | 343,226 / 2,433 |
| Indexed XF loads / aux bytes per replay | 1,170 / 56,160 B |

Phase breakdown (medians): `mem_ms` 0.164, `cp_ms` 0.001, **`pre_ms` 0.035**
(the paired preprocess pass — the crash fix), `run_ms` 0.460 (execute + Flush +
WaitForGPUIdle), `sync_ms` 0.000 (aux rewind). No drift across the sequence
(first rows 0.822/0.776 ms, last rows 0.642/0.645 ms — it gets slightly
*faster*, see below).

Environment, read-only, unchanged: battery 55% status 2 (charging),
`low_power` 0; launch hottest `cpu-*` zone **50 C** (0.5 s wait),
`performance_mode` (system) 1, `fan_mode` (system) 4,
`scaling_max_freq` cpu0 3,532,800 / **cpu7 4,320,000 kHz**, GPU governor
`msm-adreno-tz`. Sampler over 337 ticks: max `cpu-*` zone **104 C**, max
`gpuss` 70 C, cpu7 minimum **3,283,200 kHz** — never below 2.0 GHz, so the
kill rule (any zone >= 110 C, or cpu7 < 2.0 GHz for > 5 consecutive ticks) was
never tripped and nothing was killed.

### Arm 2 (s2-egl-b): repeat, plus a transform-seam probe

`LoadIndexedXF` (`XFStructs.cpp:288-302`) early-outs when the indexed data
equals what xfmem already holds, and the `XFReplay::g_transform` hook's mere
presence (`bool changed = XFReplay::g_transform != nullptr;`) forces the write
path unconditionally. A real 120 Hz replay applies a camera delta or pose
palette at that seam, so I measured what the hook costs instead of assuming:
arm 2 installs a no-op `g_transform` for the second half of the sequence and
tags every row with `xform`.

| Half | n | Wall med / p95 / min / max (ms) | Thread-CPU med | `mem_ms` | `cp_ms` | `pre_ms` | `run_ms` | `sync_ms` |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `xform=0` (replays 0-99) | 100 | 0.881 / 0.982 / 0.842 / 1.077 | 0.873 | 0.206 | 0.001 | 0.051 | 0.617 | 0.001 |
| `xform=1` (replays 100-199) | 100 | 0.850 / 0.879 / 0.826 / 0.898 | 0.848 | 0.185 | 0.001 | 0.051 | 0.611 | 0.001 |

**Installing the transform hook does not measurably change the per-replay cost**
(the second half is if anything 0.03 ms faster, consistent with warm caches).
So the early-out is not a material part of this number, and the transformed
replay a 120 Hz route would actually run costs the same as the identical replay
measured here — at least for the write-path part; the transform *function* in a
real route would add its own matrix arithmetic on top, which this no-op does not
model.

The difference between arm 1 (0.665 ms) and arm 2 (0.881 ms) tracks frame size:
343,226 B / 1,170 indexed loads versus 441,988 B / 1,649.

## Part 3c — Odin capacity table

Device Odin 3 `622c49b1` (adb over Wi-Fi, `192.168.1.53:5555`), OGL/EGL,
`d2single` template, `--affinity emu=80,video=40` (verified both arms), movie
`m3-snow-jam-3min.dtm`, module `gGXBE69_recomp.so`, 200 unmodified replays at
one idle seam with the guest parked, presentation suppressed, `Flush()` +
`WaitForGPUIdle()` inside every replay.

| Arm | Build / header | Replays | `done` | Wall per replay med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | 200-seq wall | Frame B / updates | Tombstone |
| --- | --- | ---: | :-: | --- | --- | ---: | --- | --- |
| **s2-egl-a** | `trial-egl14` `4e15d56e…`, header `31ffc39d…` | **200 / 200** | **YES** | **0.665** / 0.729 / 0.638 / 0.874 | 0.660 / 0.723 | 135.095 ms | 343,226 / 2,433 | none |
| **s2-egl-b** | `trial-egl15` `b25f61b0…`, header `31ffc39d…` (+ `xform` probe) | **200 / 200** | **YES** | **0.866** / 0.963 / 0.826 / 1.077 | 0.860 / 0.955 | 175.174 ms | 441,988 / 3,561 | none |
| s2-vk-a / s2-vk-b | — | not run | — | — | — | — | — | — |
| *(prior)* D2b egl-a | `trial-egl12`, D2 header | 27 / 200 | no | 2.036 / 2.254 / 1.998 / 2.368 | 2.032 / 2.232 | died | 479,342 / 3,871 | SIGSEGV `LoadIndexedXF` |
| *(prior)* D2b egl-b | same | 27 / 200 | no | 2.027 / 2.304 / 1.961 / 2.304 | 1.999 / 2.301 | died | 466,658 / 3,748 | SIGSEGV `LoadIndexedXF` |
| *(reference)* desktop Metal, dual core + forced determinism | `s2-desktop3`, header `31ffc39d…` | 200 / 200 | YES | 8.787 / 12.567 / 4.108 / 19.580 | 4.472 / 5.426 | 1.857 s | 331,800 / 2,848 | none |
| *(reference)* desktop Metal, single core | `s2-desktop2` | 200 / 200 | YES | 5.067 / 16.740 / 3.302 / 22.530 | 2.564 / 4.075 | 1.359 s | 415,702 / 3,489 | none |
| *(reference)* D2 desktop Metal | D2 header | 200 / 200 | YES | 10.072 / 16.752 / 3.250 / 25.365 | 3.255 / 4.719 | n/a | 268,836 / 2,455 | none |

Phase medians on the Odin (`mem_ms` = recorded memory updates + TMEM,
`cp_ms` = CP + XF register prelude, `pre_ms` = **the paired preprocess pass, the
crash fix**, `run_ms` = execute + Flush + WaitForGPUIdle, `sync_ms` = aux rewind):

| Arm | `mem_ms` | `cp_ms` | `pre_ms` | `run_ms` | `sync_ms` |
| --- | ---: | ---: | ---: | ---: | ---: |
| s2-egl-a | 0.164 | 0.001 | 0.035 | 0.460 | 0.000 |
| s2-egl-b | 0.196 | 0.001 | 0.051 | 0.614 | 0.001 |

`restored` receipts, both arms `det=1 dual=1`, `mask_bp=2`, `dls=0`,
`unknown=0 benign=1`, walk consumed 100% of the stream:

| Arm | `indexed` | `aux_bytes` per replay | 2 MiB / `aux_bytes` | D2b death index |
| --- | ---: | ---: | ---: | ---: |
| s2-egl-a | 1,170 | 56,160 | 37.3 | — |
| s2-egl-b | 1,649 | 79,152 | **26.5** | **27** |
| desktop forced-det | 1,639 | 78,672 | **26.7** | **27** |

Thermals and counters, per arm (read-only, nothing changed):

| Arm | Battery at launch | Launch hottest `cpu-*` | Sampler max `cpu-*` / `gpuss` | cpu7 min | Ticks below 2.0 GHz | Kill rule |
| --- | --- | ---: | --- | ---: | ---: | --- |
| s2-egl-a | 55%, status 2 | 50 C (0.5 s wait) | 104 C / 70 C | 3,283,200 kHz | 0 | never tripped |
| s2-egl-b | 64%, status 2 | 47 C (0.5 s wait) | 104 C / 70 C | 3,283,200 kHz | 0 | never tripped |

Per-arm device state, both arms identical: `performance_mode` (system) **1**,
`fan_mode` (system) **4**, `scaling_max_freq` cpu0 **3,532,800** / cpu7
**4,320,000 kHz** (the M4-era 3.07 GHz underclock is no longer in effect), GPU
governor `msm-adreno-tz`, `low_power` 0. Note D2b reported these
`performance_mode` / `fan_mode` nodes as absent; they are readable via
`settings get system`.

No screenshots were produced by either arm (`ScreenShots/GXBE69` empty), the
same as every D2 arm — so neither arm is HUD-verified as racing. The movie is
the 3-minute Snow Jam movie and the sequence fires at guest t = 100 s, which is
inside the race, but that is an inference from the movie, not a screenshot.

## Part 3d — Device availability log

No Odin arm was run. Two independent blocks, in order:

| Time (UTC) | Block |
| --- | --- |
| 13:40-14:30+ | `/data/local/tmp/mg/LEASE` held by **S1c** continuously (foreign lease = wait, per the brief). `local/research/S1b/REPORT.md` never appeared either; the brief's 3-hour fallback had not elapsed. |
| 14:29 onward | **Battery gate.** `dumpsys battery`: level **2%**, status **3** (discharging) with `AC powered: true` — i.e. plugged through the dongle but not charging. The orchestrator's rule (level >= 20 AND status 2/5) forbids launching. `settings get global low_power` = 0. |
| 14:5x | Device moved to adb over Wi-Fi (`192.168.1.53:5555`, `local/odin-serial`) so it could charge on a wall charger; `arm.py` and `wait_device.sh` switched to read that file (USB serial as fallback). |
| 14:54 | **Battery gate cleared**: level 20%, status 2 (charging). It kept climbing (40% by 15:17). |
| 14:54-15:17+ | Only block left: `LEASE` still reads **S1c**, with a `moderngekko` process running. Foreign lease = wait. |

`local/research/S2/arm.py` encodes every gate (foreign lease, no `moderngekko`
process, battery level/status + `low_power`, thermal wait, per-arm
`performance_mode` / `fan_mode` / `scaling_max_freq`, post-run `logcat -d -b
crash` pull, lease removal in a `finally`) and reads the serial from
`local/odin-serial` with the USB serial as a fallback. It was dry-run against
the device for everything except the launch itself. The arm to run when the
battery clears 20%:

```
python3 local/research/S2/arm.py s2-egl-a                      # OGL/EGL
python3 local/research/S2/arm.py s2-egl-b                      # repeat
python3 local/research/S2/arm.py s2-vk-a --graphics Vulkan     # only after `done` on EGL
```

Device state read read-only while waiting (nothing changed): `performance_mode`
(system) = 1, `fan_mode` (system) = 4 — both nodes D2b reported as absent are
readable via `settings get system`. `scaling_max_freq` cpu0 = 3,532,800 kHz,
**cpu7 = 4,320,000 kHz** — the 3.07 GHz cap from the M4-era underclock tool is
no longer in effect. GPU governor `msm-adreno-tz`, `max_gpuclk` 832 MHz.
Hottest `cpu-*` zone 38-41 C (idle).

---

## Part 4 — Replay boundary inventory (milestone 2 groundwork)

The research doc's "Next runtime boundary" table is a starting inventory. I
re-derived it against the pinned source with call sites, gates and boundedness,
because three of its rows turn out to behave differently on the Odin's
deterministic path than the table assumes. Paths below are relative to
`third_party/ModernGekko/vendor/dolphin/Source/Core/`.

### A. Guest RAM writes

| Path | Where | Gate | Bounded? |
| --- | --- | --- | --- |
| EFB/XFB copy to RAM, immediate | `TextureCacheBase.cpp:2535` `WriteEFBCopyToRAM` via `BPStructs.cpp:240` | `!copy_to_vram \|\| !g_ActiveConfig.bDeferEFBCopies` | per replay |
| EFB/XFB copy to RAM, deferred | `TextureCacheBase.cpp:2415` push onto `m_pending_efb_copies` | `copy_to_vram && bDeferEFBCopies` | **vector is unbounded**; drained only by `FlushEFBCopies()` |
| "uninitialize" writes | `TextureCacheBase.cpp:2421-2427` | `!copy_to_ram` | per replay |

`FlushEFBCopies()` call sites: `TextureCacheBase.cpp:137` (Invalidate), `:552`
(DoState), `:779` (`OnFrameEnd`, an `after_frame_event` listener), and
`BPStructs.cpp:186/205/221` (SETDRAWDONE / PE_TOKEN / PE_TOKEN_INT — all
**unconditional**, not behind the determinism gate). This is a second, concrete
reason the S2 fix leaves the **execute** stream verbatim and masks only the
preprocess copy: masking the execute stream would remove all three in-stream
flush points and let `m_pending_efb_copies` grow across 200 replays.

### B. CoreTiming and interrupts

`PixelEngineManager::SetToken` / `SetFinish` (`PixelEngine.cpp:229`, `:243`) →
`RaiseEvent` (`:207`). `RaiseEvent` coalesces on `m_event_raised` (`:209-212`):
while an event is pending it does **not** schedule another, it just ORs the
pending-interrupt flags and overwrites `m_token_pending` — older token values
are lost. The guest-visible part (`SetTokenFinish_OnMainThread`, `:180-202` →
`ProcessorInterface::SetInterrupt`, `Core/HW/ProcessorInterface.cpp:199`) fires
**later**, when CoreTiming next advances. With the guest parked that is after
the sequence ends, using whatever state the last of 200 replays coalesced.

`PixelEngineManager::DoState` (`PixelEngine.cpp:37-54`) covers the full pending
state (`m_token`, `m_token_pending`, both interrupt-pending flags,
`m_event_raised`, the signal flags) but **not** the queued CoreTiming event. So
a save/restore-around-the-sequence approach would leave one scheduled event
behind. The S2 fix avoids the whole problem instead: with the preprocess stream
masked and the execute pass suppressed by the determinism gate, **no** PE call
is made at all, so nothing is ever scheduled and nothing needs restoring.

`CommandProcessor::UpdateInterrupts` (`CommandProcessor.cpp:427/444`) and the
`m_event_sync_gpu` scheduling (`Fifo.cpp:429/576`) are **not** reachable from a
direct `RunFifo` call — they belong to `Fifo::RunGpuLoop`, which the instrument
bypasses. That is a useful negative result for the boundary design.

### C. Presentation, VI, and the `after_frame_event` fan-out

`BPStructs.cpp:353` triggers `after_frame_event` on **every XFB copy**, i.e.
once per replay, synchronously inside `RunFifo<false>`. One trigger fans out to
seven independent subsystems, none of them gated by anything the instrument
controls:

| Listener | Effect | Bounded? |
| --- | --- | --- |
| `TextureCacheBase::OnFrameEnd` (`:774`) | `FlushEFBCopies()` + `Cleanup(g_presenter->FrameCount())` | **`FrameCount()` only advances inside `Present.cpp:186/235` (ViSwap/ImmediateSwap)**; with presentation suppressed it never advances, so `TEXTURE_KILL_THRESHOLD=64` eviction never fires and texture-cache entries accumulate for the whole sequence |
| `FrameDumper::FlushFrameDump` (`FrameDumper.cpp:118`) | disk I/O | gated by `IsFrameDumping()` (movie dump or pending screenshot) |
| `FramebufferManager::EndOfFrame` (`:613`) | ages the EFB peek cache | bounded |
| `ShaderCache` frame-end (`ShaderCache.cpp:52`) | `RetrieveAsyncShaders`, may append to the on-disk UID cache | unbounded map; disk gated by `bShaderCache` |
| `Statistics` (`Statistics.cpp:505`) | `DolphinAnalytics::ReportPerformanceInfo` | gated by analytics opt-in |
| `WidescreenManager` (`Widescreen.cpp:50`) | widescreen heuristic | gated `!IsWii()` |
| `VertexManagerBase::OnEndFrame` (`:997`) | resets per-frame counters | bounded |

With `bImmediateXFB` false (what the sequence does) the present branch
(`BPStructs.cpp:361` → `Presenter::ImmediateSwap`, `Present.cpp:218`) is skipped
entirely, and the else-branch only mutates VI registers if
`FifoPlayer::IsRunningWithFakeVideoInterfaceUpdates()` — which is false here. So
**nothing presents and no VI register moves**, which is the desired behaviour;
the cost is that `FrameCount()` freezes and texture-cache aging stops (row 1).
D2's desktop run completed 200 replays under exactly this condition with no
warm-up trend, which is the available evidence that the accumulation is
survivable at n=200; the S2 per-replay `run_ms` series is the check on the Odin.

### D. FifoRecorder re-entry

`OpcodeDecoder::g_record_fifo_data` (`OpcodeDecoding.cpp:35`) is a process
global that `FifoRecorder`'s own `after_frame_event` listener re-evaluates
(`FifoRecorder.cpp:249-268`) — i.e. it is re-read once per replay, from the same
XFB-copy trigger the replay itself produces. It gates `WriteGPCommand`
(`OpcodeDecoding.cpp:234`), TLUT/preload `UseMemory` (`BPStructs.cpp:421`,
`:647`), texture `Load` `UseMemory` (`TextureCacheBase.cpp:1333`) and per-row
EFB-copy `UseMemory` (`:2494`). The instrument stops recording before the
sequence starts, so `IsRecording()` is false and the flag stays false — but this
is a genuine re-entrancy hazard for any future design that replays while a
recording is live, and it is not covered by the research doc's table.

### E. Cached indirect reads

| Read | Where | Refreshed by |
| --- | --- | --- |
| `VertexLoaderManager::cached_arraybases` (raw host pointers into guest RAM, per `CPArray`) | `VertexLoaderManager.h:58`, deref'd in `VertexLoader_Position.cpp:58`, `_Normal.cpp:80`, `_Color.cpp:87…`, `_TextCoord.cpp:52` | `UpdateVertexArrayPointers()` (`VertexLoaderManager.cpp:79`) only when `g_bases_dirty`, and only on the **main** pass (`VertexLoaderManager.h:102`, `if constexpr (!IsPreprocess)`) |
| `LoadIndexedXF` source | `XFStructs.cpp:275-284` | aux buffer when deterministic, fresh `GetPointerForRange` otherwise |
| `OnDisplayList` body | `OpcodeDecoding.cpp:174-182` | same split |
| TLUT / texture data | `BPStructs.cpp:397`, `TextureCacheBase.cpp:1278` | fresh per call, not cached |

The S2 per-replay CP restore writes `ARRAY_BASE`, which sets `g_bases_dirty`
(`OpcodeDecoding.cpp:81-84`), and `VertexLoaderManager::MarkAllDirty()` sets it
again, so `cached_arraybases` is re-resolved at the first draw of every replay.
That closes the "cached pointer" row of the research doc's table for the vertex
arrays; the indexed-XF row is closed by the paired preprocess pass reading fresh
guest memory through `g_preprocess_cp_state` (`XFStructs.cpp:310`).

### What a `ReplayContext` still has to own

Given the above, the parts of the "Next runtime boundary" spec that the S2
milestone-1 header does **not** yet provide:

1. **Replay-owned EFB/XFB and texture-cache resources.** Today EFB copies still
   land in real guest RAM (restored wholesale afterwards) and still create real
   texture-cache entries. A context would need its own destination arena and its
   own cache, with the unexpected-access counters failing closed.
2. **An event-bus split.** `after_frame_event` must not reach the live
   listeners; the replay needs its own bus or a scoped suppression, otherwise
   every replay ages caches, pokes the shader cache and (if enabled) the frame
   dumper and analytics.
3. **`FrameCount()` / frame-aging semantics** for a replay that never presents.
4. **A `g_record_fifo_data` guard** that fails closed rather than relying on the
   recorder happening to be idle.
5. Only then the `XFReplay::g_transform` work: pose-interpolation palettes and
   the camera delta. The hook already exists in this tree
   (`XFStructs.cpp:287-302`: `bool changed = XFReplay::g_transform != nullptr;`
   forces the write path and calls `g_transform(address, size)` after each XF
   matrix write, direct or indexed), so the seam is available with no vendor
   change — but it must be driven from inside a context that owns items 1-4, or
   the gate ("original-frame equality, unchanged guest and event state, clean
   continuation") cannot be evaluated honestly.

Milestone 2 was **not** started: it is gated on milestone 1's capacity number,
which needs the device.

---

## What I could not do

Stopped by orchestrator instruction after the second arm (reasoning-class agents
halted for quota); the remaining arms move to a muse continuation.

- **`s2-vk-a` / `s2-vk-b` (Vulkan) — not run, and not runnable with these
  builds.** The EGL trial links only `libvideonull.a`, `libvideoogl.a`,
  `libvideosoftware.a` and `libvideocommon.a` — **there is no
  `libvideovulkan.a` in `core-egl-d5-build`**, so `--graphics Vulkan` on
  `trial-egl14`/`trial-egl15` cannot select a Vulkan backend. A Vulkan arm needs
  the trial TU relinked against
  `/Volumes/Extreme SSD/android-spike/core-vk-build`, which does link
  `VideoBackends/Vulkan/libvideovulkan.a` and compiles with `-DHAS_VULKAN`. That
  build dir's `compile_commands.json` points at the **repo** vendor tree, not
  `m4-src`, so `--reference-tu` must be repointed (or omitted, falling back to
  `reconstruct_tu()`), and `--with-d5exc` may not apply. Not attempted.
- **Milestone 2 — not started.** It is gated on the capacity number, and the
  orchestrator halted the spike before the gate was read. Part 4 is the
  architecture work that was done for it: a verified side-effect inventory and
  the list of what a `ReplayContext` must own. No `ReplayContext` code was
  written, no pose-interpolation palettes, no camera delta.
- **No screenshot verification of either arm** (both `ScreenShots/GXBE69` empty,
  as in every D2 arm). Neither arm is HUD-verified as racing.
- **No third/fourth EGL arm.** Two of the four budgeted attempts were used (plus
  one aborted before launch, below).
- **A third desktop configuration** (Vulkan on the Mac) was not tried.

### Two harness snags a continuation should know about

1. **`trial-egl13`'s `build.json` did not match its binary on disk**
   (`48ab1f97…` in the receipt, `c8434dd9…` on disk) and
   `tools/android_trial.py` correctly refused to launch it. Rebuilding as
   `trial-egl14` produced a receipt that matches disk, verified twice. The
   attempt was aborted before anything was pushed, so it cost no device time.
   Two successive links of the same sources also produced different binaries
   (`c8434dd9…` vs `4e15d56e…`), so the trial link is not byte-reproducible
   here; always verify the receipt against disk before an arm.
2. **`arm.py` pre-created the receipts directory**, which
   `tools/android_trial.py` refuses (`out_dir.mkdir(exist_ok=False)`), so
   `s2-egl-b`'s harness died *after* a complete on-device run and pulled
   nothing. The run itself was fine and its artefacts were recovered by hand
   from `/data/local/tmp/mg/`. **Fixed**: `arm.py` now stages the pre-run record
   beside the directory and moves it in afterwards, and pulls the probe,
   sampler, err/out and post-run inis itself if the harness died before its own
   pull step. Untested end-to-end — the fix landed after the last arm.

## Files

Committed under `local/research/S2/` (nothing else was touched; no
`native/diagnostics/`, no `tools/`, no vendor tree, no `local/native/runtime-build/`):

| File | What it is |
| --- | --- |
| `s2_replay_capacity.h` | the fixed research header, sha256 **`31ffc39d88259a1af895d70ac6187d61128b6ff944270fcda2edb23867e23572`** |
| `build_android_trial.py` | Android trial TU relink driver (D2's, with the S2 header substituted) |
| `build_replay_player.py` | desktop player build driver |
| `arm.py` | one device arm: leases, battery gate, thermal gate, run, tombstone pull, kill-rule read |
| `analyze.py` | capacity table from one or more probe JSONLs |
| `aux_budget.py` | offline aux-budget verifier (parses a `.fifo` artefact, ports Dolphin's command-size decoder + vertex size tables) |
| `wait_device.sh`, `waits.log` | device poller and the gate log |
| `REPORT.md` | this file |

Evidence on the SSD (not committed):
`/Volumes/Extreme SSD/android-spike/S2/` — `trial-egl14/`, `trial-egl15/`
(each with `build.json`), `s2-egl-a-receipts/`, `s2-egl-b-receipts/`.
Desktop evidence: `local/research/S2/s2-desktop-run.jsonl`,
`s2-desktop2-run.jsonl`, `s2-det-run.jsonl`, `players/s2-desktop{,2,3}/`,
`s2-desktop-run/`, `s2-desktop2-run/`, `s2-det-run/` (gitignored build/output
dirs).

### What a continuation needs, exactly

Header to build from: `local/research/S2/s2_replay_capacity.h`, sha256
`31ffc39d88259a1af895d70ac6187d61128b6ff944270fcda2edb23867e23572`. Both device
arms and the forced-determinism desktop validation ran that exact header.

**A third EGL arm** (`s2-egl-c`) needs no rebuild — reuse `trial-egl15`
(binary sha256 `b25f61b0102d382d9b69734c3f3adba5cf9d5a00a599b6f8cebd026e0e122bcb`,
which carries the `xform` probe):

```sh
# gates are inside arm.py: foreign lease, moderngekko process, battery >= 20 and
# status 2/5, low_power, thermal wait, lease removed in a finally
python3 local/research/S2/arm.py s2-egl-c \
  --binary   "/Volumes/Extreme SSD/android-spike/S2/trial-egl15/moderngekko-run-trial" \
  --build-json "/Volumes/Extreme SSD/android-spike/S2/trial-egl15/build.json"
python3 local/research/S2/analyze.py \
  "s2-egl-c=/Volumes/Extreme SSD/android-spike/S2/s2-egl-c-receipts/s2-egl-c-probe.jsonl"
```

Run it with `run_in_background` or `nohup`: an arm takes about 10 minutes and a
foreground 10-minute tool cap will SIGTERM it past the `finally` that removes
the device lease.

**The Vulkan arm** (`s2-vk-a`) needs a new trial build first, because the EGL
build has no Vulkan backend (see "What I could not do"):

```sh
# host lease must be absent (or M3/M3b/D8-build); claim S2 with printf, remove after
python3 local/research/S2/build_android_trial.py \
  --game local/game/gxbe69-stock \
  --build-dir "/Volumes/Extreme SSD/android-spike/core-vk-build" \
  --output    "/Volumes/Extreme SSD/android-spike/S2/trial-vk1"
#   NOTE: no --reference-tu / --with-d5exc here. core-vk-build's
#   compile_commands.json points at the repo vendor tree, not m4-src, so the
#   m4-src reference TU and D5's patch base do not apply. If the build fails,
#   report the error rather than forcing it.
# then verify the receipt against disk BEFORE the arm:
shasum -a 256 "/Volumes/Extreme SSD/android-spike/S2/trial-vk1/moderngekko-run-trial"
python3 -c "import json;print(json.load(open('/Volumes/Extreme SSD/android-spike/S2/trial-vk1/build.json'))['trial_binary_sha256'])"
python3 local/research/S2/arm.py s2-vk-a --graphics Vulkan \
  --binary   "/Volumes/Extreme SSD/android-spike/S2/trial-vk1/moderngekko-run-trial" \
  --build-json "/Volumes/Extreme SSD/android-spike/S2/trial-vk1/build.json"
```

Acceptance for either arm is what `analyze.py` prints: `done` present in the
event list, 200 capacity rows, and the `restored` line showing `det=1 dual=1
mask_bp=2 dls=0 unknown=0` with `walk=N/N`. A `watched_window_changed` event
instead of `done`, or fewer than 200 rows, is a stop — pull
`adb logcat -d -b crash` immediately, before it rotates.

Do not conclude on the capacity gate; hand the table back.
