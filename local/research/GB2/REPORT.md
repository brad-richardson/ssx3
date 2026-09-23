# GB2 report — GS bridge step (a): CPU backend on a worker thread behind a queue

Brief `local/muse/prompts/GB2.md`. Tables + receipts; the orchestrator decides.

## 0. Outcome first

- **Steps (1) and (2) PASS.** Existing suites green unmodified; new
  determinism suite proves the queued CPU backend **byte-exact vs direct**
  on synthetic streams (op-by-op RPC results + VRAM + Present + priv regs)
  and on a **256-packet captured stream** (VRAM + Present + consume + regs).
- **Step (3) FAILS literally but exonerates the queue.** A/B frame hashes
  at matched guest vsyncs: 331/395 mismatch (84%). The A2 null control
  (second queue-off boot, identical conditions) mismatches A on 1106/1267
  (87%): **the gate measures the inherent cross-boot present-timing race,
  not queue correctness.** Guest trajectory is identical across A/B/A2
  (park semaphore histories exact, hot-PC ±3/955K, tick curves match,
  packet accounting closes to tick counts). Mismatch rate on ≈ mismatch
  rate off. First A/B divergence ~tick 43–81 (interleaved), persistent
  after; same scenes, torn-frame cut positions differ.
- No stall, no deadlock: B ran the full route healthy (1360 ticks; a
  mid-task stall read was wrong, corrected by snap-curve + diag-heartbeat
  evidence below).
- Fork commit `c937929` on `gb2-gs-queue` (no push). Merges cleanly onto
  `ssx3` tip (0 textual conflicts; 1 shared file, disjoint hunks).

## 1. Pins and receipts

- Fork branch `gb2-gs-queue` in worktree `~/dev/ssx3-work/GB2/PS2Recomp`,
  cut from `ssx3` @ `571579e`; `~/dev/PS2Recomp` untouched (only worktree
  metadata). Commit `c937929` (single commit, §2; no push).
- `ssx3` tip moved during the task: `571579e` → `943d609` (E44 Part-3).
  Conflict list in §6.
- Build `~/dev/ssx3-work/GB2/build`: Release, ninja,
  `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (read-only),
  `RUNTIME_LOGS=OFF`, `AGRESSIVE_LOGS=OFF` (E33 logs-off recipe).
  Configures: 1. Builds: 4 (tests ×2 after a test-side fix, runner ×1).
- Runner `d2df5332…94fa024` (352,306,736 B), **2 matching SHA reads
  separated by all 4 boots**. Suite binary `2377dad5…6cd9ec` (1 read).
- `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty
  (verified pre-commit).
- Disk: `GB2/` 3.0 GB + `GB2-run/` 61 MB of 5 GB cap; all-ssx3 33.3/200 GB
  (budget script exit 0, end). Capture `gb2-capture/` 1.0 MB, 256 packets
  + index (NOT in git: game-derived bytes).
- Lease: mini slot 1 for all 4 boots, claimed via `p_lane_lease.py`,
  released cleanly each time. Runner tracked by PID only. No preemption.
- Boots used: 4/4 (cap, A, B, A2). Time box respected.

## 2. Diff summary (fork commit `c937929`)

New `gs_worker` (ring + GS thread + moved decode core, GB1 §5a):

| File | Change |
| --- | --- |
| `include/runtime/gs/gs_worker.h` (new) | `GsWorker`: bounded MPSC FIFO (1024 descriptors / 16 MiB payload, producers block when full), GS thread, `GsRpc<T>` fences; 21-kind `GsCommand` |
| `src/lib/gs/gs_worker.cpp` (new) | Queue + `threadMain` (`GsWorker` thread name); drain-on-stop; oversize-single-command bypass (no deadlock) |
| `include/runtime/gs/gs_frontend.h` | `~GS`, `setQueueEnabled/drainQueue/queueEnabled`, `m_worker`, `noteGifPath` enqueue; worker assigns the field directly |
| `src/lib/gs/gs_frontend.cpp` | Every public method: `if (m_worker && !worker-thread) enqueue/RPC;` else today's body verbatim. Worker runs the exact direct bodies via `executeQueuedCommand` (thread-local re-entry guard) |
| `src/lib/ps2_runtime.cpp` | `PS2X_GS_QUEUE=1` enable in `syncCoreSubsystems` (main thread, pre-game-thread) + `[gs:queue]` line |
| `src/lib/gs/ps2_gif_arbiter.cpp` | `PS2X_GS_CAPTURE_DIR` packet tap (test infra; unset = zero change) |
| `ps2xRuntime/CMakeLists.txt` | + `gs_worker.cpp` |
| `ps2xTest/src/ps2_gs_queue_tests.cpp` (new) + `main.cpp` + `CMakeLists.txt` | 6-test determinism suite (§3) |

Routing: fire-and-forget (GifPacket, NoteGifPath, RegWrite,
UploadImageNative, NativePacked, WriteVram, ClearDebugHistory,
SetDebugPaused); RPCs with fences (Consume, ReadVram, RefreshSnapshot,
LatchPresent, Reset, GetDebugSnapshot, GetDebugHistory, IsDebugPaused,
GetPreferredSource, SetBackend, Fence). `processNativePackedGIFPacket`
verdict is EE-side (pure function of bytes); decode runs on the worker.

Deliberate deviations from GB1, all documented in code:

1. Transport is a bounded FIFO (mutex + condvars), not a literal
   contiguous ring with 256 KiB chunks — same observable contract
   (bounded, FIFO, backpressure). Backpressure is unit-tested (§3).
2. FINISH is in-stream with no EE wait: direct mode never blocks on
   FINISH, so a wait would be a behavior change, not a preservation.
3. Priv regs stay shared (no EE shadow / `priv_write`): EE↔GS priv traffic
   is already cross-thread racy in direct mode (main-thread present vs
   game-thread writes). A+D priv writes and SIGNAL/FINISH/LABEL execute on
   the worker in stream order. Remaining race (GB1 gap 2, acknowledged):
   worker RMW on `siglblid` vs EE loads — aligned u64, single writer, safe
   in practice.
4. One extra memcpy per packet at enqueue (arbiter copy retained so the
   flag-off path is untouched).

## 3. Tests

Suites run from the worktree root. New suite `PS2GSQueue` (6 tests):

| Test | Result |
| --- | --- |
| Synthetic streams byte-exact (script covers every command kind; RPC results op-by-op with first-divergence op index/kind/hashes; final VRAM + Present + priv regs) | Pass |
| Captured stream byte-exact (256 packets from §4 boot, replayed on fresh instances; VRAM + Present + consume + regs) | Pass with `PS2X_GS_QUEUE_CAPTURE` set; trivial pass when unset; **fails correctly** on empty dir (negative control) |
| RPCs execute at stream position (Write→Read fence, packet→present) | Pass |
| Concurrent producers deterministic (4 threads × disjoint IMAGE uploads vs sequential direct) | Pass |
| Lifecycle (default off, idempotent enable, disable resumes direct, state preserved) | Pass |
| Backpressure (2-deep ring blocks 4th producer until drain; all execute) | Pass |

Suite totals: **576/576 flags-unset** (570 pre-existing unmodified + 6
new), rc 0; **576/576 with `PS2X_GS_QUEUE_CAPTURE` set**, rc 0; 575/576
on the empty-dir negative control (only the captured test fails, as
designed). Logs `/tmp/gb2-suite2.log`, `/tmp/gb2-suite3.log`,
`/tmp/gb2-suite-neg.log` (scratch, not in git).

Two self-found failures on the way, both test-side: backpressure test
ignored the in-execution slot (worker parks one command in the handler);
synthetic script clobbered DISPFB1 before presenting (regs now compared
pre-restore, Present post-restore).

## 4. A/B table (E33 vsync route to Select Character, 300 s each)

Wrapper `local/research/GB2/gb2_boot.py` (two-slot lease, PID-tracked,
per-boot cwd, caps; `--gs-queue`, `--capture-dir`, `--sample-at` flags).
Compare `local/research/GB2/gb2_ab.py` (tick→fnv1a from `[frame:dump]`,
first upload per tick). Route = E33 §"Vsync-clock script" string.

| Boot | Env | Ticks (dumps) | End state |
| --- | --- | --- | --- |
| gb2cap | queue off + capture, wall 90 | 0..1293 (1261) | capture filled (256 pkts), healthy |
| gb2a (A) | queue off, wall 300 | 0..1371 (1320) | Select Character (Zoe), healthy |
| gb2b (B) | `PS2X_GS_QUEUE=1`, wall 300 | 0..1360 (433) | Select Character (Zoe), healthy |
| gb2a2 (A2) | queue off, wall 300, A repeat | 0..1367 (1307) | Select Character (Zoe), healthy |

All rc 0, wall-bound. `[gs:queue] enabled` ×1 in B's log only.

| Pair | Matched ticks | Mismatches | Verdict |
| --- | --- | --- | --- |
| A vs B (off vs on) | 395 | 331 (84%) | FAILS literally |
| A vs A2 (off vs off, null) | 1267 | 1106 (87%) | gate unpassable as stated |

First A/B divergence: ticks 43/45/47 (hashes never in A), interleaved
through ~81, persistent after (early ticks 0–49 match: fallback magenta +
first real frames). Tick-1274 snaps: same Select-Character scene both
boots, 25% RGB pixels differ, alpha identical, no shift explains it
(±2px search: (0,0) best). 351/433 B-hashes never occur anywhere in A:
systematic torn-frame cut difference, not a timing shift.

Guest-trajectory identity (queue changes nothing the guest can see):

- Park snapshots at shutdown: thread PCs/RAs identical, semaphore
  wait/signal histories EXACT (4803/1822), hot-PC 955857/955859/955856.
- Tick-vs-wall curves match (5s snaps): 265–267@5s, 1281–1284@60s,
  1360/1371/1367@300s. B advanced steadily all boot (also confirmed by 50
  interleaved diag heartbeats; an early "B stalled at 60s" read was wrong).
- T1 packet accounting closes: 164781/161793/163530 packets over
  1371/1360/1367 ticks; residuals fully explained by tick counts ×
  heavy-tail rate (~282/tick char-idle). Nothing submitted is lost.

Why frames differ (both pairs): the main thread latches mid-burst in heavy
scenes, so every present is a torn frame whose cut position is a
wall-clock race. Two identical direct boots therefore mismatch 87%. The
queue shifts cut positions systematically (game thread submits at
different wall times without raster; latch RPC drains full bursts vs
direct's torn snapshot; B presents 433 vs A's 1320 over the same ticks).
Same-scene pixels, different cuts — inside the direct envelope.

Guest vsyncs/s (DIAGNOSTIC build — frame dumps + diag on — not speed
numbers): menu phase (paced) A≈32 / B≈38 / A2≈29; char-idle A≈0.37 /
B≈0.32 / A2≈0.36; overall ≈4.5 all boots. Route is VU1-bound on the mini
(§5), so no GS-offload speedup is visible or claimed here.

## 5. CPU split (`sample`, 10 s at wall 200 s, diagnostic)

200 s lands in char-select idle (tick ~1330, VU1-bound) in all boots:

| Boot | GameThread (6650/4171/6873 samples) | GsWorker (4171, B only) | Main |
| --- | --- | --- | --- |
| A | ~100% EE→VIF1→VU1 path (`VU1Interpreter::run`, FMAC/pipe commit) | — | EndDrawing/present |
| B | ~100% same VU1 path, 0 GS frames on-stack | 4105 idle in cond-wait (drained, starved — game mid-VU1-burst, nothing submitted), 66 rastering (`Submit`/`SampleTexture`/`WritePixel`) | EndDrawing/present + latch RPC |
| A2 | same as A | — | same as A |

Honest limits: the sample hits a VU1-bound phase, so it shows the worker
correctly starved (not spinning, not blocked) and raster offloaded when
active, but does not quantify the raster split. Re-sample in a
raster-bound scene (race 3D) for the true GameThread/GsWorker split. No
speed is claimed from this route (§4).

## 6. Conflict list vs `ssx3` tip (`943d609`)

`git merge-tree` of `gb2-gs-queue` (`c937929`) onto `ssx3` tip: **0
textual conflicts**. One file changed on both sides,
`ps2xRuntime/src/lib/ps2_runtime.cpp`, with disjoint hunks (E44 Part-3
`loadELF` tap ~line 1021 vs GB2 `syncCoreSubsystems` enable ~line 753)
that merge cleanly. E44's `ps2_memory.cpp` edits do not touch any GB2
file (GB2 modifies no `ps2_memory.*`). New files (`gs_worker.h/.cpp`,
`ps2_gs_queue_tests.cpp`) cannot conflict.

## 7. Gaps (stated plainly)

- Boot A/B gate fails literally; evidence says the gate (live-present
  hashes) is inherently racy, not that the queue diverges. A quiescent
  gate (E4 freeze VRAM at matched ticks, or stop-the-world drain +
  snapshot) would discriminate queue correctness; not run (no boots left).
- Queue-on presents are sparser (433 vs ~1320): each latch RPC waits for
  full-burst raster + present on the worker (GB1 §2e's predicted hop
  cost). Fine for correctness; step (d) owns present performance.
- `siglblid` worker-RMW vs EE-load race remains (GB1 gap 2); aligned-u64
  single-writer, safe in practice, not a formal fix.
- E4 `ReadVram` census now pays an RPC round-trip per sample (GB1 gap 3);
  fine at census rates, not re-budgeted.
- `sample` split is from a VU1-bound phase (§5 limits); raster-phase
  split unmeasured.
- One extra packet memcpy at enqueue; flag-off path untouched.

## 8. Recommended next action (orchestrator decides)

1. Accept step (a) on the determinism evidence (byte-exact same-inputs
   incl. 256-packet captured replay) + guest-trajectory identity (park
   exact, tick curves match, packet accounting closes) + direct-envelope
   A/B read.
2. Re-baseline the boot A/B gate on quiescent snapshots (E4 freeze VRAM
   at matched ticks) instead of racy live presents before gating step (b).
3. Step (b) (paraLLEl feed) can build on this queue; no blocker found.
   Fold `gb2-gs-queue` (`c937929`) at E's convenience — merges cleanly.

## 9. Exact commands

```
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GB2/PS2Recomp -b gb2-gs-queue ssx3
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF   # in GB2/
cmake --build build --target ps2x_tests -j4
./build/ps2xTest/ps2x_tests                                          # 576/576 flags-unset, from worktree root
PS2X_GS_QUEUE_CAPTURE=~/dev/ssx3-work/GB2-run/gb2-capture ./build/ps2xTest/ps2x_tests  # 576/576
cmake --build build --target ps2EntryRunner -j4
python3 local/research/GB2/gb2_boot.py --label gb2cap --wall 90 --snap 5.0 --script "<E33 route>" --capture-dir ~/dev/ssx3-work/GB2-run/gb2-capture
python3 local/research/GB2/gb2_boot.py --label gb2a --wall 300 --snap 5.0 --script "<E33 route>" --sample-at 200 --sample-secs 10
python3 local/research/GB2/gb2_boot.py --label gb2b --wall 300 ... --gs-queue 1 --sample-at 200 --sample-secs 10
python3 local/research/GB2/gb2_boot.py --label gb2a2 --wall 300 ... --sample-at 200 --sample-secs 10
python3 local/research/GB2/gb2_ab.py boot-gb2a-1.log boot-gb2b-1.log    # 395 matched / 331 mismatch
python3 local/research/GB2/gb2_ab.py boot-gb2a-1.log boot-gb2a2-1.log   # 1267 matched / 1106 mismatch
```

(`<E33 route>` = the script string in `local/research/E33/REPORT.md` §"Vsync-clock script".)
