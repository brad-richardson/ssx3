# D2 — Replay capacity test: REPORT (final: desktop done, Odin EGL blocked, Vulkan unattempted)

Status (final, 2026-09-18Z): desktop 200-replay table DONE (below).
Odin EGL: seven device attempts, no 200-row table — blocked with diagnosis.
Vulkan: unattempted (attempt budget exhausted). Leases released, session stopped.
Desktop runs were blocked on `/tmp/ssx3-host-lease` (M3 census 07:04–08:05Z,
S3 device A/B, S1 LLVM phase 2 continuously since ~08:26Z, still held at
09:02Z after ~2 h of 5-min polls); device half blocked on S3/M3b device
order. Session stopped while waiting per brief; orchestrator re-prompts.
No verdicts.

## What is ready

- Research header copy: `local/research/D2/d2_replay_capacity.h` — resurrects
  the September-13 FifoRecorder + `RunFifo<false>` loop (repo commit
  `e0525cc`), adapted to the brief: 200 unmodified replays back to back at
  one seam (pc `0x801cad24`/lr `0x801cd724`), presentation suppressed
  (`bImmediateXFB` off during the sequence), `Flush()` + `WaitForGPUIdle()`
  after each replay (real overrides exist on Metal, OGL, Vulkan, D3D12),
  per-replay wall ms + `CLOCK_THREAD_CPUTIME_ID` CPU ms rows, guest
  RAM/EXRAM snapshot save/restore with watched-window re-hash (mismatch
  stops the run). Env-gated on `SSX_NATIVE_REPLAY=1`. Never copied into
  `native/diagnostics/`.
- Player build driver: `local/research/D2/build_replay_player.py` — mirrors
  `gamecube_native_trace.py build --scheduler --replay` semantics (header
  set/order, probe namespace, compile_copy + relink, launcher/receipt shape)
  with the replay header sourced from the D2 copy.
- Player: `local/research/D2/players/d2-desktop2` (`d465c41c`, built on the
  S3-inclusive tree after the orchestrator's pin-check hazard steer; pin
  check passes, no bypass used; production runner untouched `24c2e26c`).
  A pre-S3 player (`players/d2-desktop`, `c38f1ff1`) is superseded.
- Analysis: per-replay `capacity` rows in the probe JSONL; median/p95 to be
  computed by script at run time.

## Gate log (full history: local/research/D2/waits.log)

M1/REPORT.md gained `# Part 4` at ~07:18Z (M1d runs went first). Host lease
sequence: M3 (census) 07:04–08:05Z → S3 (device A/B) → S1 (LLVM phase 2,
still held at 08:41Z). Desktop run needs lease absent + load < 3.

## Device half plan (after S3 frees the device per D2 isolation, and after
M3b's `m3-odin-crows-cap-receipts` or 4 h)

Relink the same header into the Android trial TU (`tools/android_trial.py`
build technique: D2 variant driver on the SSD with headers
`native_callback_trace.h`, `callback_timing.h`, `render_deadline.h`,
`native_render_schedule.h`, `replay_plan.h`, the D2 copy, plus the trial
driver lifecycle; step call `NativeReplay::Step` beside the trial step),
run on the Odin EGL then Vulkan pinned (`--affinity emu=80,video=40`,
uncapped? per brief the replay runs at the idle seam; thermal rules as D1b:
wait < 50 °C per arm; kill only ≥ 110 °C or cpu7 < 2.0 GHz for > 5 ticks).

## Desktop run recipe (ready)

```
# lease absent, load<3, M1 Part 4 present, pin check passes
echo D2 > /tmp/ssx3-host-lease
# 10-min clean cool, then (game: gxbe69-stock for cross-platform parity):
SSX_NATIVE_REPLAY=1 SSX_NATIVE_PROBE=$PWD/local/research/D2/d2-desktop-run.jsonl \
python3 tools/gamecube_schedule_check.py --player-dir local/research/D2/players/d2-desktop2 \
  --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock \
  --profile d2-desktop --output local/research/D2/d2-desktop-run --seconds 240
rm /tmp/ssx3-host-lease
```

Backend note: `native_gamecube.py` launches headed runs with
`--graphics Metal`; the run receipt/log will confirm the actual backend
(`schedule_check` writes a Vulkan frontend config that the headless/headed
runner may ignore). Report whichever ran.

## Files

- `local/research/D2/`: `d2_replay_capacity.h`, `build_replay_player.py`,
  `players/d2-desktop2/` (live), `players/d2-desktop/` (superseded),
  `waits.log`
- `/Volumes/Extreme SSD/android-spike/D2/`: `REPORT.md` (this file; results
  to follow)

## What D2 could not do (yet)

Android relink + Odin EGL/Vulkan runs; per-platform table. Desktop done
below. No commit (brief names no files to commit yet; TBD).

## Desktop measurement (Metal, 640x528, 2026-09-18T09:22Z, lease D2)

Run: `SSX_NATIVE_REPLAY=1 SSX_NATIVE_PROBE=.../d2-desktop-run.jsonl
gamecube_schedule_check.py --player-dir players/d2-desktop2
--immediate-xfb --resolution 640x528 --game gxbe69-stock --profile
d2-desktop --output d2-desktop-run --seconds 240`. Backend Metal
("native Metal check"), single core, immediate XFB (suppressed during the
200 only). Gates at start: lease absent, load 2.40, no dolrecomp/builds,
pin check pass, player receipt match. Frame captured at host second 140:
268,836 GP bytes, 2,455 memory updates. Watched window: unchanged
(`done`, RAM/EXRAM re-hash match). Continuation: riding (state 0) at
t=242 s, zero gpu_command_errors, zero invalid_memory_accesses.

| Metric (200 unmodified replays, present suppressed, Flush+WaitForGPUIdle each) | Value |
| --- | ---: |
| Wall per replay (decode+submit+GPU idle), median | 10.072 ms |
| Wall per replay, p95 / min / max | 16.947 / 3.250 / 25.365 ms |
| Thread-CPU per replay (CLOCK_THREAD_CPUTIME_ID), median | 3.255 ms |
| Thread-CPU per replay, p95 | 4.735 ms |
| Late-half (replays 100-199) wall median / p95 | 10.107 / 16.352 ms |
| 200 replays in | 1.94 s wall (~103 replays/s) |

No warmup trend (first5 3.8-17.1 ms, last5 5.5-14.3 ms); spread is
alternating 3-6 ms vs 12-17 ms, consistent with a 2-deep GPU queue behind
WaitForGPUIdle rather than thermal drift (host load 2.4-2.6 throughout).
GPU time is included via the idle wait; no finer per-replay GPU timestamp
is exposed on this path. Raw rows: `local/research/D2/d2-desktop-run.jsonl`
(`capacity` actions 0-199).

Host lease released after the run. Device half waits per orchestrator
order: M3b `m3-odin-crows-cap-receipts` (absent at 09:30Z) or 4 h, plus
device lease absent (S3 held it at 09:30Z).

## Odin EGL outcome (BLOCKED — attempt budget exhausted, 2026-09-18Z)

Seven device attempts on Odin 622c49b1 (OGL/EGL, d2single template,
`--affinity emu=80,video=40`, movie m3-snow-jam-3min.dtm, module
gGXBE69_recomp.so). No 200-row table was produced. Per orchestrator budget
(cap5 + at most two more: cap6, cap7), work stopped after cap7.

| Attempt | Build | Result |
| --- | --- | --- |
| cap1 | trial-egl | died on affinity race |
| cap2 | trial-egl | headless trial, no D2 window reached |
| cap3-5 | trial-egl9 | `blocked` events: dual=1 sched=1 (GameINI `GXBE69.ini` CPUThread=False ignored on Android; `DEFAULT_CPU_THREAD` true on ANDROID, so trial builds are always dual-core) |
| cap6 | trial-egl10 (`3fa07f40…`, dual-tolerant gate) | 1 frame captured, 30 capacity rows, process exit ~100 s host, no `done` |
| cap7 (LAST) | trial-egl11 (`162a9c1f…`, + video-thread stall) | 1 frame captured, `gpu_stall` fired, 30 capacity rows, process exit ~100 s host, no `done` |

### Exact event (cap6, cap7 — identical signature)

Probe sequence both runs: `record_start` → `recorded` → `restored` →
30 `capacity` rows (idx 0–29) → one torn partial line → silence; sampler
logs process EXITED ~100 s after start; run receipt `exited: true`; no
`done` / `watched_window_changed` event, so the RAM/EXRAM re-hash never
verified. The "30" is the 4 KB stdio flush point, NOT the death point:
per-row `fprintf` has no flush (single `fflush` after the loop), so ~27–30
rows fill the buffer, flush once, and rows 30+ die silently with the
process. True replay count at death is unknown (≥30, possibly all 200).

Partial rows (UNVERIFIED — no watched-window `done`; NOT a capacity table,
do not cite as one): cap6 frame 468,712 B / 3,609 updates, wall median
0.585 ms (min 0.559, max 0.691), cpu median 0.583 ms; cap7 frame 391,293 B
/ 2,913 updates at guest-t 100.1 s, wall median 0.519 ms (min 0.488, max
0.601), cpu median 0.51 ms. Stable timings, no degradation before death.

### What was tried

- `CPUThread=False` via GameINI (ignored on Android default-true path).
- Dual-tolerant gate (cap6): dual-core + trial scheduler no longer block;
  validity argued from parked guest + WaitForGPUIdle + re-hash. Produced
  the 30-row partial above, then death.
- `FifoManager::PauseAndLock` / `RestoreState(true)` around the bulk
  section (cap7; the same pair Core.cpp uses for savestates; `SyncGPU` is a
  no-op in non-deterministic mode, stall bounded by 100 ms `WaitYield`).
  `gpu_stall` is in the probe, no hang — same death. The concurrent-video-
  consumer race hypothesis is disfavored; the signature is deterministic
  (identical row counts and torn-write shape twice, different frames).
- Thermal/kill rules: new gate used both arms (cap6: 30 s wait, launch
  hottest-cpu 53 °C; cap7: immediate, 49 °C). Sampler tails show zones
  ~85–87 °C max (< 110 °C), cpu7 healthy. No thermal kill. Pin check clean.
  No `tools/` or `native/diagnostics/` edits (all changes confined to
  `local/research/D2/` + SSD trial dirs + `/tmp` backups).

### Adjacent evidence (NOT D2's — D1 control-probe runs, same device/game)

logcat tombstones for D1's `moderngekko-run-trial` (BuildId `96c200f5…`,
`--user-dir …/user-d1-control-probe*`; neither matches D2's egl10
`961e6e10…` / egl11 `984c912d…` builds) show SIGTRAP in
`CommandProcessorManager::GatherPipeB…` ← `GPFifo::UpdateGatherPipe` ←
`Write32` ← `StaticRecompCore::HookExternalWrite` ← live guest dispatch
(`chassis_dispatch` ← `StaticRecompCore::Run` ← `RunLoop` ← `CpuThread`).
I.e. the same trial+game family dies on live resume with gather-pipe
state residue — a candidate mechanism for D2's deaths (the bulk section
drives the backend through 200+ frames but never saves/drains/restores
the CPU-side GPFifo gather-pipe accumulator, so the first live pipe write
after resume can trap), but UNCONFIRMED for D2: D2's own tombstones had
rotated out of logcat by diagnosis time.

### Named fix for the next session (not implemented — budget spent)

1. `fflush` (or unbuffered fd) per `capacity` row, so a post-loop death
   still leaves a countable partial table instead of a torn line.
2. Save/drain/restore the GPFifo gather-pipe accumulator
   (`GPFifoManager` pipe buffer + size) around the bulk section, alongside
   the existing BP/CP/XF/TMEM + RAM/EXRAM save/restore.
3. Re-arm EGL (1 attempt should discriminate: full `done` vs same death),
   then Vulkan.

### Vulkan

Unattempted. The two-attempt budget covered the EGL diagnosis (cap6–cap7).

### Leases and hygiene

`/data/local/tmp/mg/LEASE` removed after cap7; `/tmp/ssx3-host-lease`
absent (removed right after each arm). Note: the cap7 host-lease write
used `echo -n`, which wrote the literal bytes `-n D2`; leases must be
written with `printf`. Queued agents were left a free device.

## Part 2 — D2b continuation (named fixes, 2026-09-18Z)

Fixes from Part 1 implemented exactly in `local/research/D2/d2_replay_capacity.h`
(never in `native/diagnostics/`): (1) `fflush` after every `capacity` row
(`Event` already flushed); (2) `GPFifoManager::UpdateGatherPipe` drain +
`DoState` snapshot of the pipe buffer/count into a 1024 B `PointerWrap`
memory buffer before the bulk section, `ResetGatherPipe` + `DoState` restore
after RAM/EXRAM restore (`ChunkFile.h` + `Core/HW/GPFifo.h` includes,
`system.GetGPFifo()`); (3) `done`/`watched_window_changed` detail carries
`seq_wall_ms` for the whole 200. Rebuilt trial TU with the trial-egl11
recipe → `/Volumes/Extreme SSD/android-spike/D2/trial-egl12`
(`moderngekko-run-trial` sha256 `6b883e00cebe4215…`, build.json receipt
matches disk; 4 build warnings, all pre-existing `Core_Run.cpp`
`-Wmissing-variable-declarations`, none from the D2 header). Host build gate
was clear (lease absent). `tools/android_trial.py` ran unmodified despite
D8's uncommitted edits — no breakage observed.

Device gate: lease read M3, then adb lost the device (~t+1170–2350 s of the
3 h clock; `adb devices` empty), device returned with lease D4, D4 released
it (~t+2940 s) with no D4 REPORT; orchestrator override then sent D2b in.
Claimed `D2b` (printf) on the device lease and host lease; `ps -A |
grep moderngekko` empty before each arm; both leases removed at the end.

| Arm | Build / shape | Replays | Wall med/p95/min/max (ms) | Thread-CPU med/p95 (ms) | Frame B / updates | `done`? | 200-seq wall | Launch thermals | Counters |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d2b-egl-a | egl12 `6b883e00…`, d2single OGL, emu=80/video=40 verified | 27 (idx 0–26) | 2.036 / 2.368 / 1.998 / 2.368 | 2.032 / 2.365 | 479,342 / 3,871 | NO | n/a (died) | hottest-cpu 38 °C immediate | exc=0, shots=0, host life 100.6 s |
| d2b-egl-b | same binary/shape | 27 (idx 0–26) | 2.027 / 2.304 / 1.961 / 2.304 | 1.999 / 2.301 | 466,658 / 3,748 | NO | n/a (died) | hottest-cpu 38 °C immediate | exc=0, shots=0, host life 99.8 s |

Mode/fan/caps per arm (read-only, unchanged): GPU governor
`msm-adreno-tz`, max_gpuclk 832 MHz; cpu governor/hwmon/dumpsys-power-mode
nodes absent on this build. No thermal kills (kill rules never tripped).

Exact event (both arms, identical): probe runs `record_start` →
`recorded` → `gpu_stall` → `pipe_saved` → `restored` → 27 flushed
`capacity` rows (zero torn lines — fix 1 verified working) → silence; no
`done`, watched window never verified. Death is mid-loop during replay 27,
not on live resume — the Part-1 gather-pipe-resume hypothesis is dead.

Tombstone stacks (pulled immediately per brief, `logcat -d -b crash`;
both mine by pid/tid — egl-a tid 7403 is the pinned emu thread):

```
egl-a 09:17:03Z pid 7393 SIGSEGV: LoadIndexedXF ← RunFifo<false> ← StaticRecompCore::Run()+10560 ← RunLoop ← CPU::Run ← CpuThread
egl-b 09:19:45Z pid 19070/1 SIGSEGV: identical PCs (LoadIndexedXF … Run()+10560 … CpuThread)
```

Two different frames, same death count, same stack: the replayed frame
stream references CP/XF indexed-vertex array state that does not survive
repeated re-execution (first ~26 replays fine, wild pointer on ~27).
Candidate next fix (NOT implemented — brief allowed exactly the three named
fixes plus one more attempt): re-apply the prelude/register snapshot (or
per-replay `RestoreLive` + prelude) inside the loop instead of once, so each
replay starts from identical array setup. Vulkan arms (`d2b-vk-a`/`d2b-vk-b`)
not run: `done` never verified.

Receipts: `d2b-egl-a-receipts/`, `d2b-egl-b-receipts/` (run.json, probe
jsonl, err/out, post-run inis, sampler log, build.json). Raw rows:
`capacity` actions 0–26 in each probe file. No screenshots were produced by
either arm (pull empty, as in cap6/7).

What D2b could not do: the 200-row table on EGL or Vulkan; per-replay rows
past index 26; screenshot verification of these arms.
