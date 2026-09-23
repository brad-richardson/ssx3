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

## 9. Part 2 — quiescent gate (orchestrator amendment)

One build, 2 boots (A queue-off, B queue-on, same E33 route, 300 s).
Game-thread VBlank hook at fixed guest ticks (every 50 from 100 to 1350):
stop-the-world drain (Fence RPC when queued, no-op when direct), then
`SnapshotVram` + priv-reg fnv, logged as
`[vq] tick=<T> vram=<fnv> regs=<fnv> size=<B> sub=<n> reg=<n>`.
Pass = identical fnv at every matched tick.

### 9.1 Change (fork commit `a77b933` on `gb2-gs-queue`, no push)

| File | Change |
| --- | --- |
| `ps2xRuntime/include/ps2_vq.h` (new) | Header-only gate (E4 pattern): `PS2X_VQ=1` arming, tick filter, drain + snapshot + fnv + log |
| `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | +1 include, +1 `ps2_vq::noteVBlank` line after the E4 call in `VBlankStart` (game thread) |
| `gs_frontend.h/.cpp` | Atomic `submitCount` (executed packets: `processGIFPacket` + direct `uploadImageNative` + direct `processNativePackedGIFPacket`, each counted once at execution) and `regWriteCount` (public `writeRegister`) |
| `local/research/GB2/gb2_boot.py` | `--vq` flag → `PS2X_VQ=1` |
| `local/research/GB2/gb2_vq.py` (new) | Compare script: table + first-mismatch tick + packet-index range; exit 0 on pass |

Quiescence: game thread is the only producer, so post-drain every
submitted command has executed; main-thread presents don't mutate VRAM or
priv regs. `merge-tree` vs `ssx3` tip (`943d609`, unchanged): still 0
textual conflicts (E44 touched neither `EeScheduler.cpp` nor `ps2_vq.h`).

### 9.2 Build + suite + boots

- THE one build: `cmake --build build -j4` (all targets), rc 0, 648 edges
  (header change rebuilt broadly). Suite after: **576/576 flags-unset**,
  rc 0 (`/tmp/gb2-suite-p2.log`, scratch).
- Runner `d9a0154c…9226ad7`, 2 matching SHA reads separated by both boots.
- `[vq] armed` ×1 in both logs. Lease: slot 1, both boots, clean.

| Boot | Env | Ticks | VQ samples | Result |
| --- | --- | --- | --- | --- |
| gb2c (A) | queue off + `--vq`, wall 300, rc 0 | 0..~1370 | 26 (100..1350) | Select Character, healthy |
| gb2d (B) | `--gs-queue 1` + `--vq`, wall 300, rc 0 | 0..~1360 | 26 (100..1350) | Select Character, healthy |

### 9.3 VQ table (all 26 matched ticks)

| tick | off-vram | off-regs | on-vram | on-regs | off-sub | on-sub | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 100 | 43e5391b | 618977f1 | 450b75c9 | 618977f1 | 536 | 558 | MISMATCH |
| 150 | 2ebbd68f | 3242e903 | 4be23470 | 3242e903 | 1267 | 1301 | MISMATCH |
| 200 | 2ebbd68f | 45e21e5d | 4be23470 | 45e21e5d | 2117 | 2151 | MISMATCH |
| 250 | 5aeb6ee1 | 169b8f6f | e16e8f9c | 169b8f6f | 3505 | 3910 | MISMATCH |
| 300 | 6c0c82ec | c6364d9e | 39aa4b34 | c6364d9e | 10353 | 10597 | MISMATCH |
| 350 | 769cc32f | 96efbeb0 | 767f4bc9 | 96efbeb0 | 16453 | 16697 | MISMATCH |
| 400 | 110a252f | 1b0c63ea | 4c80cdf2 | 1b0c63ea | 22553 | 22797 | MISMATCH |
| 450 | 91d1633c | acaf53c | 4211ceb | acaf53c | 28653 | 28897 | MISMATCH |
| 500 | f63c8a3a | b7a3c246 | 2820cfce | b7a3c246 | 34753 | 34997 | MISMATCH |
| 550 | 598f2568 | bd9dce9 | 3ac50ecd | bd9dce9 | 40853 | 41097 | MISMATCH |
| 600 | ba5b8ba7 | 7fb93997 | b7bad924 | 7fb93997 | 46997 | 47243 | MISMATCH |
| 650 | 9a5511f4 | f0328355 | f103084d | f0328355 | 53149 | 53395 | MISMATCH |
| 700 | 6f7ed2c1 | 1c5097f3 | 87fb3005 | 1c5097f3 | 59880 | 60126 | MISMATCH |
| 750 | 8dd24112 | 8cc9e1b1 | 67391f86 | 8cc9e1b1 | 66330 | 66576 | MISMATCH |
| 800 | d4493492 | 73e89f64 | cd93da2c | 73e89f64 | 72780 | 73026 | MISMATCH |
| 850 | fa7333a7 | c55cc8e2 | 3ce6f11 | c55cc8e2 | 79230 | 79476 | MISMATCH |
| 900 | 397aec3a | 107ffdc0 | ee277246 | 107ffdc0 | 85680 | 85926 | MISMATCH |
| 950 | e2fda837 | 61f4273e | c48b73b0 | 61f4273e | 92130 | 92376 | MISMATCH |
| 1000 | d200fe2d | f4d8a42c | 3cc73cbb | f4d8a42c | 98580 | 98826 | MISMATCH |
| 1050 | 45140d79 | a94ee623 | c9146e2a | a94ee623 | 105030 | 105276 | MISMATCH |
| 1100 | 3f5af563 | 76a24445 | 8443bee9 | 76a24445 | 111480 | 111726 | MISMATCH |
| 1150 | 7c38e5d1 | 475bb557 | 61818039 | 475bb557 | 117930 | 118176 | MISMATCH |
| 1200 | f428ace2 | ca02e9b9 | 2724bceb | ca02e9b9 | 124380 | 124626 | MISMATCH |
| 1250 | be88d1cd | b9c17b0b | 671c0d12 | b9c17b0b | 131204 | 131450 | MISMATCH |
| 1300 | f3ea1a52 | 4bcc89d2 | c4ba2732 | 4bcc89d2 | 144468 | 144714 | MISMATCH |
| 1350 | 93fac383 | 3b8b1b24 | 4efb1645 | 3b8b1b24 | 158568 | 158814 | MISMATCH |

Matched 26, mismatches 26 (all VRAM; **regs identical at all 26**).
`reg=0` at every sample in both boots (no HLE reg writes on this route
by tick 1350). `size=4194304` throughout.

### 9.4 Stop-rule receipt (first mismatch)

Per the brief: stop, no tuning, both boots used.

- **First mismatch: tick 100** (the first sample).
- **Packet index range since previous match: off (0, 536], on (0, 558].**
- Reg writes at tick: off 0, on 0.

### 9.5 Analysis (why this is NOT a queue-execution defect)

1. **Regs identical at 26/26** ⟹ every priv-reg write the guest can see
   (EE MMIO, HLE disp env, A+D, SIGNAL/FINISH/LABEL) landed identically.
   Guest control flow is not diverged.
2. **Submit deltas lockstep after tick 300.** On−off sub: 22@100,
   34@150, 34@200, 405@250, 244@300, then constant 244 (600: 246) through
   1350 — per-window deltas EXACTLY equal for 1000+ ticks (e.g. +6100 both
   300→550, +6450 both 750→1200, +14100 both 1300→1350). The submitted
   streams are identical after tick ~300; the divergence window is ticks
   0–300 (boot/startup).
3. **Unit determinism (Part 1 §3) proves same-packets ⟹ same-VRAM**,
   including a 256-packet captured replay. Combined with (1)+(2): the
   queue executes correctly; the guest *submitted* ~246 extra packets in
   B during ticks 0–300, and VRAM (cumulative) never reconverges.
4. Leading hypothesis for the extra submits (same class as Part 1
   analysis): a timing-dependent guest read during init (single-shot CSR
   SIGNAL/FINISH poll, timer, or device-status read) observes a different
   value under async decode than under synchronous decode, and init code
   submits extra/recovery packets. Steady-state code (tick 300+) uses
   proper sync, hence the lockstep. The discriminating next step: E7
   packet-fnv logs in both boots to find the first differing submitted
   packet (2 boots, not run — budget exhausted).

### 9.6 Presents/sec queue-on vs queue-off (for step d)

From `[frame:dump]` counts over wall in THESE boots (both wall-bound,
≈302.4 s elapsed):

| Boot | Dumps | Elapsed (s) | Presents/s |
| --- | --- | --- | --- |
| A (off) | 1337 | 302.433 | **4.42** |
| B (on) | 464 | 302.437 | **1.53** |

Queue-on presents **2.9× fewer** (Part 1: 1320 vs 433, same ratio).
Mechanism: each latch RPC waits for full-burst raster + present on the
worker, so the main thread presents slower while the game thread runs
ahead. Step (d) input: the present path needs the GPU-resident swapchain
(GB1 §3b) — the RPC round-trip + full CPU raster per present does not
scale.

### 9.7 Part 2 receipts

- Build: 1 (`cmake --build build -j4`, rc 0); suite 576/576 after.
- Boots: 2/2 (gb2c, gb2d), slot 1, PIDs tracked, released cleanly.
- Runner SHA `d9a0154c…9226ad7` matched pre/post both boots.
- Disk 33.5/200 GB. `ssx3` tip unchanged (`943d609`); merge still clean.
- Exact commands: §9 boots = `gb2_boot.py --label gb2c --wall 300
  --snap 10.0 --script "<E33 route>" --vq` and `--label gb2d ... --vq
  --gs-queue 1`; compare = `gb2_vq.py boot-gb2c-1.log boot-gb2d-1.log`
  (exit 1, first mismatch tick 100 as above).

### 9.8 Recommended next action (orchestrator decides)

1. The queue executes correctly (regs 26/26, lockstep submits after
   tick 300, unit byte-exactness). The open item is the tick 0–300
   submit divergence: run the E7 packet-fnv A/B to isolate the first
   differing submitted packet and the guest read that caused it.
2. Step (d) takes the presents/sec number (2.9× fewer when queued).

## 10. Exact commands (Part 1)

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

## 11. Part 3 — packet/CSR bisection (orchestrator amendment)

Max 4 boots: (1) two boots (off/on, to tick 320) logging each submitted
packet (`pk idx tick fnv len src`) plus each guest GS CSR/SIGLBLID read
(`csr idx tick value pc`); (2) if a CSR/SIGNAL/FINISH read precedes the
divergence, ONE candidate fix (drain-on-CSR-load when queued) + ONE vq
validation pair, else stop and hand back.

**Outcome: (1) points elsewhere — STOPPED per the brief. No CSR read
precedes (or follows) the divergence; no validation boots run (2/4 used).
The drain fix is built env-gated but never enabled/booted.**

### 11.1 Change (fork commit `b975930` on `gb2-gs-queue`, no push)

| File | Change |
| --- | --- |
| `ps2xRuntime/include/ps2_pk.h` (new) | `PS2X_PKLOG=1` packet + CSR log; `PS2X_GS_CSR_DRAIN=1` fix flag (dev, default off); 2M-line cap + TRUNCATED marker |
| `ps2_memory.cpp` | 4 call sites: `submitGifPacket` (src=path), masked-flush emit (src=3), native P6 (src=img, setup+image fnv), native P7 (src=packed, verdict-true only) |
| `ps2_runtime.cpp` | `Load16/32/64/128`: CSR/SIGLBLID branch (drain-if-flagged + log); matcher requires the GS priv range (see bug below) |
| `gs_worker.h/.cpp`, `gs_frontend.cpp` | `isQuiescent()` + drain fast-path (skip Fence only when queue-empty-and-idle under one mutex — provably a no-op, same guarantee) |
| `gb2_boot.py` | `--pklog`, `--csr-drain` flags |
| `gb2_pkdiff.py` (new) | First-divergence finder (idx-aligned + 5-deep indel check), 10-before table, CSR reads before, pcs |

CSR collapse rule (documented deviation from "log each read", forced by
volume — a tight spin would emit billions): every read is COUNTED (idx),
a line is emitted only on (pc,addr,value) change; idx gaps are spin
lengths. Format fields match the brief plus `addr` (CSR vs SIGLBLID half).

**Matcher bug (mine, fixed in `b975930`):** the first cut matched on
`(vaddr & 0x1FFFFFFF)` physical base alone, which over-matches
scratchpad `0x70001000/0x70001080` (same physical as CSR/SIGLBLID
`0x10001000/0x10001080`). All 13.6K raw `csr` lines in the (1) boots are
scratchpad reads. Corrected analytically by `addr=` filter (below); the
fix requires the `0x12000000` priv range first, exactly mirroring
`read32`'s dispatch. The pk log is unaffected.

### 11.2 (1) boots (pristine: pklog on; NO vq, NO csr-drain)

Same binary `efaa4ecf…19421f` (suite 576/576 before boots), E33 route,
wall 120 (ticks 0–1300 reached; brief asked to tick 320 — superset):

| Boot | Env | Ticks | pk lines | csr lines | Result |
| --- | --- | --- | --- | --- | --- |
| gb2e (off) | `--pklog` | 0..1299 | 144,591 | 13,639 | rc 0, wall, no truncation |
| gb2f (on) | `--gs-queue 1 --pklog` | 0..1300 | 144,759 | 13,649 | rc 0, wall, no truncation |

### 11.3 Handoff per the brief

**First differing packet: idx 352 @ tick 80** — Path2, len 64, same tick,
same src, different bytes: off fnv `85d9d4e9`, on fnv `888f9292`.
Single substitution (353 realigns; both sides fully parseable with
consistent fields — not a torn line; idx 0–351 verified clean+matching).

**10 packets before it (idx 342–351, identical in both boots):**

| idx | tick | fnv | len | src |
| --- | --- | --- | --- | --- |
| 342 | 79 | 11346f13 | 48 | 2 |
| 343 | 79 | 628ef1a1 | 64 | 2 |
| 344 | 79 | 27fe7be6 | 48 | 2 |
| 345 | 79 | eb4606c | 80 | 2 |
| 346 | 79 | 53ef76a6 | 144 | 2 |
| 347 | 79 | 53ef76a6 | 144 | 2 |
| 348 | 80 | cc6dd8df | 1696 | 3 |
| 349 | 80 | 53ef76a6 | 144 | 2 |
| 350 | 80 | 3dcd5d1 | 80 | 2 |
| 351 | 80 | 11346f13 | 48 | 2 |

**CSR reads before it: NONE.** After correcting the matcher bug by
`addr=` filter: **zero genuine guest CSR/SIGLBLID loads in ticks 0–1300
in either boot** (9,176/9,181 scratchpad lines at `0x70001000/04/80/84`;
zero at `0x12001000/04/80/84`). Completeness: every vaddr `read32/64`
routes to CSR passes `isGsPrivReg` (`0x12000000` range), all of which the
hook matches; `0x12001000` is special (via the IO physical range), so
recompiled loads route through the hooked `Load32/64` (with pc).
**Guest pc: N/A** — no CSR reads precede; pk lines carry tick, not pc.

**Further structure (strict-src filter, mutually present idx):** 9
packets/tick ticks 75–92; the FIRST packet after each VBlank (Path2,
len 64) differs ticks 80–91 (idx 352–451, every 9th); then a 143-packet
structural burst idx 467–609 (len/src differ too), realigning at 610.
Later-stream comparison is corruption-limited: concurrent `cerr` writers
tear lines (garbage `src` values observed), so only the verified-clean
prefix and strict-filtered rows are cited.

**Ruled out as mechanisms:** guest CSR/SIGLBLID loads (zero); HLE-direct
CSR reads (none exist in-tree); GS interrupts (the emulator never asserts
them — no INTC_STAT channel); GIF_STAT backend-state reads (no callers
outside GS); the `readIORegister` GS branch (unreachable, per its own
comment). (1) points elsewhere ⟹ **STOP, no validation boots.**

### 11.4 What the next lane gets

- The divergence is a VIF1-Path2 packet *content* substitution with no
  preceding completion observation — NOT deviation #2 (FINISH in-stream).
  That deviation remains untested as a mechanism (it may still matter in
  phases where CSR spins exist, e.g. E33's `0x375d10` — outside ticks
  0–1300); the env-gated fix stands by, never booted.
- First move should be an A2-pklog null: the every-9th periodic
  substitution could be embedded run-varying bytes (pointer/uninit) that
  would differ off/off too — 1 boot discriminates queue-vs-noise before
  any fix work. Second: packet BYTES at idx 352 (capture tap with N>352),
  and the unlogged channels (VIF/DMAC/GIF STAT loads, timers, CDVD).
- For step (d): presents/s numbers stand from Part 2 §9.6 (4.42 off vs
  1.53 on); the drain fast-path (`isQuiescent`) is in place for any
  future per-read draining.

### 11.5 Part 3 receipts

- Builds: 2 (neither capped): `efaa4ecf` (logging + gated fix; the (1)
  boot binary) and `93cd2d08` (matcher fix; suite-only, unbooted).
  Suites 576/576 after both (`/tmp/gb2-suite-p3.log`,
  `/tmp/gb2-suite-p3b.log`, scratch).
- Boots: 2/4 (gb2e, gb2f), slot 1, PIDs tracked, released cleanly.
- SHA gap (minor, stated): boot binary `efaa4ecf` has ONE pre-boot read
  (rebuilt before a second read was possible); final binary `93cd2d08`
  one post-build read. Non-device binaries.
- Disk 36.7/200 GB. `ssx3` tip `e52b6bf` (E44 Part-4, moved during task);
  `merge-tree` still 0 conflicts; overlap still only `ps2_runtime.cpp`
  (E44's `loadELF` hunk vs GB2's `syncCoreSubsystems` + Load hooks —
  disjoint). GB2's `ps2_memory.cpp` additions (4 log call sites) are new
  overlap surface for E's fold (no textual conflict today).
- Exact commands: §11.2 boots = `gb2_boot.py --label gb2e --wall 120
  --snap 10.0 --script "<E33 route>" --pklog` and `--label gb2f ... --pklog
  --gs-queue 1`; compare = `gb2_pkdiff.py boot-gb2e-1.log boot-gb2f-1.log`
  (exit 1, first divergence idx 352 as above).

## 12. Part 4 — A2-pklog null + byte decode (orchestrator amendment)

Brief: (1) one more queue-OFF boot with `--pklog` (does off/off differ
at idx 352?); (2) for whichever pair differs, capture BYTES of idx 352
(and 361, 370), decode the differing qwords, and if possible name the
guest builder (VIF1 DMA source + store pc via a one-word watch). Plus
fix the concurrent-cerr tearing. Max 3 boots. Stay on the GB2 worktree
and current codegen dir (E46 regenerating).

### 12.1 What was built (one build, runtime `1234451`)

- Tearing fix: all pk/csr lines go to `./ps2_pklog.txt` (per-boot cwd)
  under the existing mutex; stderr keeps one `[pklog] writing to ...`
  line. Formats unchanged.
- `PS2X_PKCAP=<idx,...>`: dumps `[pkbytes] idx= tick= len= src=
  base= data=<hex>` (bytes capped at 4 KiB) for listed packets.
- Source-base classify: each submit site calls
  `ps2_pk::setBases(m_rdram, ..., m_scratchpad, ...)`; capture reports
  `base=rdram+0xPHYS | spad+0xOFF | other`.
- No new watch code: the prescribed one-word store watch already exists
  (`PS2X_DIAG_WATCH=<addr,...>` → `[diag:watch] addr= width= value=
  pc= thread= ra= sp=`, covering fast WRITE* macros and Store* paths).
  Boot wrapper gained `--pkcap`/`--watch`, pklog rotation
  (`pklog-<label>-1.txt` + bytes/lines in the result JSON) and a 512 MB
  pklog cap. New offline decoder `gb2_pktdecode.py` (GIF-tag walk +
  A+D decode; self-tested on synthetic data).
- Suites 576/576 flags-unset and 576/576 queue-capture, from the
  worktree root (a 575/576 run from the wrong cwd was the CWD-dependent
  `instructions.h` test, green on rerun). Runner SHA-256
  `245bbaedc15733974b0afc7bd3b6c33d09ebe8c71ea8b92d63cbe159b1efa371`
  (one read; non-device binary).
- Codegen dir stable across all 3 boots: 9457 files, newest
  `register_functions.cpp` @1790012496 (Sep 21 13:41 — E46 had not
  regenerated yet; same codegen as Part 3's E/F).

### 12.2 Boots (3/3 + 1 void)

| Boot | Env | Result |
|---|---|---|
| gb2g-try1 (VOID) | off + pklog + pkcap | rc -11 after 2 s: JetKVM display asleep → GLFW `InitWindow` null-GL-proc segfault (`.ips` receipt). No emulation. Woke with `caffeinate -u`, retried same label |
| gb2g (boot 1) | off + pklog + pkcap 352,361,370 | rc 0, wall 120 s, slot 1. pklog 7.7 MB / 149,611 lines: 144,591 `[pk]`, 5,017 `[csr]`, 3 `[pkbytes]`, 0 bad lines, no TRUNCATED |
| gb2h (boot 2) | on + pklog + pkcap 352,361,370 | rc 0, wall, slot 1. pklog 7.7 MB / 150,024 lines, 144,996 `[pk]`, 3 captures, 0 bad lines |
| gb2i (boot 3) | on + pklog + pkcap 352,361,370 (H-repeat; see §12.6) | rc 0, wall, slot 1. pklog 7.8 MB / 152,026 lines, 146,970 `[pk]`, 3 captures, 0 bad lines |

### 12.3 (1) Null HOLDS — off/off deterministic, queue causes 352

E (Part-3 `boot-gb2e-1.log`) vs G (`pklog-gb2g-1.txt`): 144,405/144,405
mutually-parsed packets identical (tick+fnv+len; src where unclobbered).
The 42 apparent mismatches and 186 parse gaps are all E-side tear
artifacts (proven: tick/fnv/len identical, `src=` clobbered by
interleaved raylib `FILEIO:` lines, e.g. idx 3390/4393).

| idx | E (off) | G (off) |
|---|---|---|
| 352 | tick=80 fnv=85d9d4e9 len=64 src=2 | identical |
| 361 | tick=81 fnv=e674152f len=64 src=2 | identical |
| 370 | tick=82 fnv=b8fa4a72 len=64 src=2 | identical |

### 12.4 (2) Bytes: no differing pair at 352/361/370 — the question vacates

`gb2_pktdecode.py pklog-gb2g pklog-gb2h 352 361 370`: **0 differing
qwords at all three** (H-vs-I likewise 0). The packets are REGLIST
`NLOOP=1 EOP=1 NREG=6 [PRIM,ST,RGBAQ,XYZ2,ST,XYZ2]` textured-sprite
packets. Ticks shift by one (G 80/81/82 vs H 79/80/81) but bytes match.
All three report `base=other`: the VIF1 DIRECT chunks come from
heap-assembled DMA chains (`ps2_memory.cpp:2035` `p.chainData`; the 16 B
stack feeder at :1197 is excluded by size), so there is no RDRAM word to
watch — the one-word watch is impossible for this pair (see §12.6).
(The chains carry `p.srcSpans` via E40's pay-map: a follow-up can thread
chain-offset→RDRAM into the capture instead of rebuilding it.)

What the tear-free logs show INSTEAD (the actual queue-vs-direct
structure):

**Systematic −1-tick phase shift.** G-vs-H first row-divergence is idx 0
(same content `fnv=3af1a56c len=128 src=3`, tick 40 vs 39). Shift
histogram (G tick − H tick): {0: 11,861, 1: 132,485, 2: 122, 3: 1,
4: 122}. The queue guest runs ~1 vsync ahead of the counter.

**First genuine CSR read differs (FIELD bit).** pc `0x375d10`,
addr `0x12001000`: G `tick=40 value=0x4000`, H/I `tick=39
value=0x6000` — the difference is CSR bit 13 (FIELD), consistent with
the phase shift. All following ~2,300 CSR reads are ordinal-locked (same
4-pc rotation `0x382c30/0x3828e0/0x3829d8/0x382aa0`, one per tick) with
phase-flipped values (`0x4008` even / `0x6008` odd).

**Content identical to idx 49,792, then deterministic Path1 divergence.**
G-vs-H first content (tick-insensitive) divergence: idx 49,793 (tick
G621/H620, XGkick len-208). Both sides keep evolving after (~6,800
distinct Path1 fnvs each — not a freeze). No new CSR trigger at 620:
FIELD differs throughout; the guest ignores it for 49,792 packets and
something (non-CSR observation or accumulated phase) amplifies there.
Trigger unknown — follow-up work.

**F is the outlier: stale replay + novel content.** F's idx 352
(`fnv=888f9292`, clean line) is a byte-identical replay of the idx-190
packet (tick 62); the fresh content (`85d9d4e9`) appears ZERO times in
F. From 361 on, F's per-tick packets are NOVEL (fnv not found in G;
+9 series 352, 361, 370, ... then ~128k content diffs). Neighbors
348–351/353–356 match G exactly: single-packet substitution, alignment
preserved. The logged fnv is computed at submit from the passed bytes,
so the staleness was in the submitted VIF1-chain bytes, not in the
queue worker.

**H == I bit-for-bit.** 144,996/144,996 full rows identical (tick+fnv+
len+src); same 49,793 content divergence; I ran longer (tick 1307 vs
1300). On this binary the queue path is deterministic; F (older
logging build, same codegen + queue code) hit a different outcome → the
queue path has a timing-sensitive race with a rare early-divergence
tail (1 F-like in 3 on-boots; caveat: logging-build timing differs, and
the tail rate is unsized).

**Presents decouple (mechanism hint).** Host frame uploads (raylib
FILEIO lines) per 120 s wall: E=1279, G=1285 (off) vs F=367, H=388,
I=397 (on) — same direction as Part 2 (1320 off vs 433 on). The guest
submits MORE packets per wall on-queue (H 144,996 > G 144,591) while
the host presents ~3× FEWER frames per guest tick: the guest outruns
present/vsync coupling, consistent with the −1 phase shift.

### 12.5 Part 3 correction (retract "zero genuine CSR reads")

E/F's csr lines are SCRATCHPAD hits only (`0x70001000/70001004/
70001080/70001084`; 13,639/13,649 lines, ZERO `0x12001000`), while G/H/I
(fixed matcher) show only `0x12001000` (~5,020 genuine reads/boot).
Timeline: E/F booted 13:35/13:37 from the pre-commit tree (binary
`efaa4ecf`, buggy matcher — see §11.5's own receipt); the matcher fix
was committed in `b975930` (13:44; verified fixed in that tree) and is
in `1234451`. The Part-3 "over-match" model was wrong: the boot matcher
never matched true CSR, so "zero genuine CSR reads" was a false
negative. Corrected: genuine CSR reads DO precede the divergence
(first: pc `0x375d10` @tick 39/40) and their values DO differ (FIELD).
Orchestrator's prime suspect (deviation #2 / GB1 §2c completion
visibility) is rehabilitated; the env-gated CSR-drain fix is back on
the table for a future brief — NOT validated here.

### 12.6 Deviations and gaps

- Boot 3 = on-side H-repeat, not the brief's watch boot: with G/H bytes
  identical and `base=other`, there is no differing word and no RDRAM
  addr — the watch is impossible. The repeat discriminated H-typical
  (deterministic phase shift) from F-typical (early stale replay):
  I == H, so F is the tail. `PS2X_DIAG_WATCH` stands by for the
  follow-up that has an addr (no new watch code needed).
- gb2g attempt 1 void (display asleep, §12.2); same-label retry.
- Gaps: F's first-CSR value unknowable (buggy-matcher log, no budget to
  re-run that binary); 49,793 amplification trigger unknown; F-tail rate
  unsized (needs an N-run on-side study); VIF1 RDRAM source unmapped for
  chain-fed streams (`srcSpans` handoff noted in §12.4).
- Presents direction: Part 2's "433 vs 1320" = on vs off per ~1360
  guest ticks (§9: A/off 1320, B/on 433); Part 4 FILEIO counts agree.

### 12.7 Recommended next (orchestrator decides)

1. Root-cause the −1 phase shift (guest–vsync coupling on the queue
   path; presents decoupling is the lead symptom) — E/G lane.
2. Validate the CSR-drain fix (GB1 §2c rehabilitated by §12.5): one
   on+drain boot; pass = first-read FIELD matches off-side.
3. Size the F-tail: N on-side repeats on one binary (spontaneous early
   stale replay? or logging-timing-only?).
4. Thread E40 `srcSpans` into `[pkbytes]` so chain-fed packets map to
   RDRAM sources for `PS2X_DIAG_WATCH`.

### 12.8 Part 4 receipts

- Build: 1 (`cmake --build build -j4`, rc 0); suites 576/576 ×2.
- Boots: 3/3 (gb2g, gb2h, gb2i) + 1 void (display asleep), slot 1,
  PIDs tracked, released cleanly. No boot over 600 s.
- Disk: `local/tooling/disk_budget.sh` → 37.1/200 GB (208 Gi free).
- Exact commands: boots = `gb2_boot.py --label gb2{g,h,i} --wall 120
  --snap 10.0 --script "<E33 route>" --pklog --pkcap 352,361,370`
  (+ `--gs-queue 1` for h/i); null = full-parse join E-vs-G (not the
  indel-diff, which trips on E's torn gaps); decode =
  `gb2_pktdecode.py pklog-gb2g-1.txt pklog-gb2h-1.txt 352 361 370`.

## 13. Part 5 — CSR-drain fix validation (orchestrator amendment)

Brief: validate the env-gated fix (`PS2X_GS_CSR_DRAIN=1`, committed in
`b975930`, never booted): (a) queue-on + drain + `--vq` + `--pklog`,
(b) a repeat. Pass = VQ VRAM fnv identical at all 26 ticks vs a fresh
queue-off `--vq` boot, or Part-2 A if the binary's VQ output is
unchanged (state which). Report first CSR read vs G, phase histogram,
first content divergence. Presents/s only if pass. On fail: first
differing CSR read + first differing packet, then stop. Note the F-type
stale replay as an open item, don't chase it. Max 3 boots.

**Verdict: FAIL.** Both (a) and (b) mismatch VRAM at all 26 ticks (regs
26/26 match, same shape as Part-2 B). Worse: (a) and (b) disagree with
each other from idx 0 — the drain path is nondeterministic, with two
distinct failure modes (J immediate-behind, K delayed-behind). The
drain is the wrong tool: it stalls phase backward without restoring
off-ness, and K proves the content trigger is a NON-CSR channel (K's
CSR reads match G through tick 246; content diverges at tick 80).

### 13.1 Baseline: Part-2 A (gb2c) is valid — stated per brief

No fresh off boot was run (2/3 boots used). `a77b933..1234451` touches
6 files, all additions: pklog/capture logging (no guest writes), 4 CSR
Load hooks (dormant unless PKLOG/DRAIN set; otherwise read-then-log,
identical semantics), and the drain fast-path (`isQuiescent` skip of a
proven-no-op Fence — timing-only). VQ code (`ps2_vq.h`, EeScheduler
hook, submit counters) byte-identical; off-path guest execution is
single-threaded with no drain calls, so gb2c's 26 VRAM hashes stand.
(E==G packet-identity independently proves off-path determinism.)

### 13.2 Boots (2/3)

| Boot | Env | Result |
|---|---|---|
| gb2j (a) | on + drain + vq + pklog (+pkcap, §13.6) | rc 0, wall 330 s, slot 1. 26 VQ samples, pklog 8.9 MB / 172,536 lines (167,196 pk), max tick 1380 |
| gb2k (b) | repeat of (a) | rc 0, wall, slot 1. 26 VQ samples, pklog 8.8 MB / 170,089 lines (164,781 pk), max tick 1371 |

Codegen stable (9457 files, newest Sep 21 13:41); display awake; no
build (binary `1234451`, runner `245bbaed…efa371`).

### 13.3 VQ gate: 26/26 VRAM mismatch, both boots

| tick | C-vram (off) | J-vram | K-vram | regs | J-sub/C-sub | K-sub/C-sub |
|---|---|---|---|---|---|---|
| 100 | 43e5391b | 07dd1249 | dc2e1eaa | match ×3 | 534/536 | 545/536 |
| 150 | 2ebbd68f | 4be23470 | 4be23470 | match ×3 | 1259/1267 | 1276/1267 |
| … | … | … | … | match ×3 | J ≈ C−114 | mixed |
| 1350 | 93fac383 | 1c561099 | 72b99954 | match ×3 | 158454/158568 | 158577/158568 |

First mismatch tick 100 in both. J ≠ B ≠ C at tick 100 (B was
`450b75c9`): the drain reaches a third state, not the off state.

### 13.4 Packet/CSR hand-back (the fail items)

First differing CSR read vs G:

| Boot | csr-idx | pc | G (tick/val) | Boot (tick/val) |
|---|---|---|---|---|
| J (a) | 0 | 0x375d10 | 40 / 0x4000 | 41 / 0x6000 (FIELD=1, behind) |
| K (b) | 822 | 0x3828e0 | 247 / 0x6008 | 246 / 0x4008 (phase-flipped) |

K's csr-idx 0 matches G exactly (tick 40, 0x4000) — the drain "worked"
for the first read in K's run, yet K still fails. (All K csr addrs are
`0x12001000`; zero SIGLBLID reads.)

First differing packet vs G (both boots @352, the +9 series):

| idx | G | J | K |
|---|---|---|---|
| 352 | tick 80, 85d9d4e9 | tick 81, 888f9292 (F's stale) | tick 80, 888f9292 (F's stale) |
| 361/370/… | fresh | F's novels (ff624a51/5ee4ec87/…) | F's novels |

Phase ladder (X−G tick, dominant value): H −1 (ahead, G-content to
49,792); G 0; F +1 (F-content); K +1 (F-content); J +2 (F-content to
49,555, == F bytes). Full histograms: G−J {−4: 236, −3: 75, −2:
111,744, −1: 30,341, 0: 2,195}; G−K {−4: 113, −3: 1, −2: 113, −1:
121,220, 0: 23,135, 1: 9}. J-vs-K differ from idx 0 (164,661 full-row
diffs): J behind from the first read, K aligned for ~3.4k packets then
behind-1 (wobbling late). K's content diverges (tick 80) while
phase-aligned and 166 ticks before its first CSR difference —
causal direction is content-state → phase-drift, and the trigger is
not CSR.

### 13.5 Byte decode (the Part-4 (2) question, answered on K/G)

Tags identical at 352/361/370; exactly one differing qword each
(qw[2], reglist RGBAQ+XYZ2, byte+32 — one alpha byte):

| idx | G word (alpha) | K word (alpha) |
|---|---|---|
| 352 | 0x75808080 (0x75) | 0x80808080 (0x80) |
| 361 | 0x6b808080 (0x6b) | 0x75808080 (0x75) |
| 370 | 0x60808080 (0x60) | 0x6b808080 (0x6b) |

K's per-tick alpha LAGS G's by exactly one tick (K-361 = G-352 etc.;
J-352 == K-352, 0 diffs). The "stale replay of idx 190" and the
"one-tick lag" are the same mechanism (fade plateau 0x80 across ticks
62–79). Decoder wart fixed: A+D detail now only fires on real A+D regs
(it misfired on reglist pixel data).

### 13.6 Partial effect + deviations + gaps

- Presents (asked only-if-pass; reporting anyway): `[frame:dump]`
  counts J=1326, K=1330 ≈ C=1337 (off) vs B=464 (on, no drain). The
  drain restores off-rate presents while breaking phase the other way —
  its one positive effect, and evidence the present/vsync coupling is
  the control surface, not completion visibility.
- Deviations: (i) `--pkcap 352,361,370` included (logging-only
  insurance for the fail case; paid off — §13.5 came from it);
  (ii) wall 330 (drain-stall margin over Part-2's 300; J/K tick rates
  4.1/s vs G 10.8/s show the stalls are real); (iii) no fresh off
  baseline (§13.1 states why Part-2 A stands).
- Gaps: trigger read unknown — must be an UNLOGGED channel (GIF_STAT /
  VIF_STAT / DMAC_STAT / EE timers / INTC / non-CSR priv regs; guest
  RAM may diverge before tick 80 with no packet impact; hunt window
  ticks 40–80). J-vs-K bimodality rate unsized (1 sample each);
  leading hypothesis is the `isQuiescent` fast-path making the drain
  itself racy (stall iff queue busy at the read), but drain
  invocations are unlogged so J-immediate vs K-delayed is unattributed.
- OPEN ITEM (carried, not chased): F-type stale replay = one-tick alpha
  lag (§13.5). On-path outcomes now 3 F-state (F, J, K) vs 2 H-state
  (H, I) across 3 binary/flag combos — timing-race with (at least) two
  attractors; needs an N-run study, not more GB2 boots.

### 13.7 Recommended next (orchestrator decides)

1. Log the unlogged guest-observable channels (GIF_STAT first: the
   arbiter drains async on the worker, so APATH/OPH leak worker timing
   to any polling guest) over ticks 40–80; find the read whose value
   first differs on F-state runs.
2. Treat guest/vsync PHASE as the control variable (drain stalls push
   it behind; the +9-series content follows the F-state, not vice
   versa). GB1 §2c completion-visibility is the wrong mechanism for
   this divergence — do not re-validate drain variants.
3. If the queue route continues: an N-run on-side study on ONE binary
   to size H-state vs F-state (GB2 has 3+2 across mixed builds).

### 13.8 Part 5 receipts

- Build: 0 (binary `1234451` reused deliberately — same binary as H/I
  keeps on-path compares clean).
- Boots: 2/3 (gb2j, gb2k), slot 1, PIDs tracked, released cleanly. No
  boot over 600 s.
- Disk: `local/tooling/disk_budget.sh` → 42.2/200 GB (202 Gi free).
- Exact commands: boots = `gb2_boot.py --label gb2{j,k} --wall 330
  --snap 10.0 --script "<E33 route>" --gs-queue 1 --csr-drain --vq
  --pklog --pkcap 352,361,370`; VQ = `gb2_vq.py boot-gb2c-1.log
  boot-gb2{j,k}-1.log` (rc 1, 26/26 VRAM mismatch); decode =
  `gb2_pktdecode.py pklog-gb2g-1.txt pklog-gb2k-1.txt 352 361 370`.
