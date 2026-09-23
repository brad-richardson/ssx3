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
