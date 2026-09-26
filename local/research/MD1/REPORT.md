# MD1 — why loading runs at 0.32× on the Odin: count the GPU work per loading frame

Worker: Muse Code. Brief: `local/muse/prompts/MD1.md`. Date: 2026-09-26.
Method: per-vsync GPU-work counters (`PGS_STATS=1`, compiled in only with
`PGS_ENABLE_STATS=ON`), one det boot to t2400 (FR1-R1, paraLLEl,
`PGS_HIER_BINNING=force`), phase means from the `[pgs-stats]` lines.

## Status

**Counters delivered; verdict: none — no single mechanism named, no fix.**
Loading is bimodal: ticks 1440–1610 are menu-quiet, ticks 1610–1714 do
race-level GPU work with no single pathological counter. All three
hypothesized mechanisms (submit/flush per upload, buffer per transfer,
descriptor set per draw) are directly ruled out, plus pipeline compiles
(zero in loading) and FIFO readbacks (`l2h_bytes=0`). Per brief step 3,
stopping with the table; no fix, so no base-vs-fix speed pair.

## Counter table (per-vsync means, run-stats2)

Coverage (stats lines / ticks): mode 291/341 (85%), loading 269/274 (98%),
load-early 165/170, load-late 104/104 (100%), race 687/687 (100%).
2286/2286 lines clean, complete (all keys), strictly monotonic ticks.
Source lines are pre-edit numbers at the pinned revs (Granite `166ba21a`,
paraLLEl-GS `19d93b2`).

| Key | Meaning | Source (file:function:line) | Mode 1099→1440 | Loading 1440→1714 | Load-early 1440→1610 | Load-late 1610→1714 | Race 1714→2400 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| gsub | Granite submits | device.cpp:submit_nolock:1341 | 6.0 | 7.9 | 5.8 | 11.2 | 11.3 |
| qsub | vkQueueSubmit2 calls | device.cpp:queue_submit:1757 | 4.0 | 5.8 | 4.1 | 8.4 | 8.5 |
| qbatch | submit batches | device.cpp:queue_submit:1757 | 6.0 | 9.6 | 6.2 | 14.8 | 15.0 |
| cmd | command buffers | device.cpp:request_command_buffer_nolock:1994 | 6.0 | 7.9 | 5.8 | 11.2 | 11.3 |
| cmds | secondary cmdbufs | device.cpp:request_secondary…:2048 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| dreq | descriptor-set requests | descriptor_set.cpp:request_descriptor_set:360 | 17.1 | 19.2 | 7.6 | 37.5 | 50.8 |
| dpush | push-descriptor sets | command_buffer.cpp:push_descriptor_set:2977 | 39.6 | 68.7 | 22.5 | 141.9 | 186.6 |
| dalloc | desc-pool alloc batches | descriptor_set.cpp:412 | 4.0 | 4.9 | 2.9 | 8.0 | 8.0 |
| dupd | bindless desc updates | descriptor_set.cpp:591 | 2.4 | 3.3 | 1.9 | 5.6 | 6.4 |
| buf | buffers created | device.cpp:create_buffer:5069 | 10.5 | 7.7 | 4.4 | 12.9 | 17.1 |
| bufB | buffer bytes (B) | device.cpp:create_buffer:5069 | 3.1 MB | 11.1 MB | 2.9 MB | 24.1 MB | 30.5 MB |
| img | images created | device.cpp:create_image_from_staging_buffer:4056 | 2.0 | 2.2 | 2.3 | 2.0 | 2.0 |
| imgB | image bytes (B) | device.cpp:allocate_image_memory:~4035 | 1.9 MB | 1.9 MB | 1.9 MB | 1.9 MB | 1.9 MB |
| iview | image views | device.cpp:create_image_view:3670 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| bview | buffer views | device.cpp:create_buffer_view:3355 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| stag | image staging bufs | device.cpp:create_image_staging_buffer:3737 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| bind | pipeline binds | command_buffer.cpp:bind_pipeline:1769 | 36.5 | 41.2 | 17.0 | 79.5 | 107.8 |
| copy | vkCmdCopy* cmds | command_buffer.cpp:copy_*:143–247 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| copyB | copy_buffer bytes | command_buffer.cpp:copy_buffer:143,159 | 0 | 0 | 0 | 0 | 0 |
| updin | vkCmdUpdateBuffer cmds | command_buffer.cpp:update_buffer_inline:2358 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| updinB | update-inline bytes | command_buffer.cpp:update_buffer_inline:2358 | 0 | 0 | 0 | 0 | 0 |
| ffl | frame flushes | device.cpp:flush_frame:1941 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| fwait | frame fence waits | device.cpp:PerFrame::wait:2869 | 6.0 | 6.9 | 6.1 | 8.2 | 8.3 |
| widle | wait_idle (det artifact) | device.cpp:wait_idle:2559 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| fence | fence waits | fence.cpp:FenceHolder::wait:45 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| fencet | fence wait_timeout | fence.cpp:wait_timeout:107 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| gflush | GSInterface::flush | gs_interface.cpp:flush:4267 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| fsub | renderer flush_submit | gs_renderer.cpp:flush_submit:1117 | 2.0 | 2.9 | 2.1 | 4.2 | 4.3 |
| pcreate | pipeline creates | pipeline_cache.cpp:create_pipeline:~625 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| pcomp | fresh compiles | pipeline_cache.cpp:create_pipeline_and_place:512 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| sreq | scratch requests | command_buffer.cpp:request_scratch…:2350 | 6.3 | 16.9 | 1.7 | 41.0 | 58.5 |
| sreqB | scratch bytes (B) | command_buffer.cpp:request_scratch…:2350 | 0.41 MB | 0.13 MB | 0.04 MB | 0.28 MB | 0.46 MB |
| rp | render passes | FlushStats via consume_flush_stats | 2.4 | 3.9 | 2.0 | 6.9 | 9.8 |
| prim | primitives | FlushStats | 448 | 11,553 | 938 | 28,393 | 25,438 |
| pal | palette updates | FlushStats | 10.6 | 25.5 | 6.6 | 55.5 | 62.9 |
| gcopy | VRAM copy ops | FlushStats | 6.3 | 16.9 | 1.7 | 41.0 | 58.5 |
| gct | copy threads (px) | FlushStats | 411,458 | 88,279 | 29,980 | 180,774 | 150,376 |
| gcb | copy barriers | FlushStats | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| scrB | scratch demand (B) | FlushStats | 1.4 MB | 8.4 MB | 1.2 MB | 19.9 MB | 23.9 MB |
| imgFB | texture image bytes (B) | gs_renderer.cpp pull-from-slab miss:1384 | 0 | 27 KB | 44 KB | 0.04 KB | 1.0 KB |

Counters that jump in load-late vs mode: prim 63×, bufB 8× (32 MB
scratch realloc churn, gs_renderer.cpp:946–1010), scrB 14×, gcopy/sreq
6.5×, pal 5×, dpush 3.6×, submits/binds ~2×. Nothing jumps 10×+ in call
counts except primitives (inherent draw work, ~350 prims/bind).

## Ruled out (brief step 3)

- Submit/flush per GS upload: gsub 6.0→7.9 (loading) / 11.2 (late),
  fsub 2.0→2.9/4.2. No.
- Buffer allocated per transfer: buf 10.5→7.7 loading (FEWER than mode).
  No. (bufB jumps 8× via fewer, bigger 32 MB scratch reallocs.)
- Descriptor set per draw: dreq flat 17→19, dpush 40→69. No.
- Pipeline compiles: pcreate total 3507, of which 3496 in title (shader
  warmup), 9 in all of loading, 0 in race; pcomp 0 everywhere. No.
- FIFO readbacks: `l2h_bytes=0` in every periodic `[gs:parallel]` line
  (read_transfer_fifo never fires). No.
- wait_idle per present: Mac-det readback artifact
  (ps2_gs_parallel_backend.cpp:400; Odin uses PRESENT_PIPELINE=1, no
  drain). Discounted.
- `queue_wait_on_submission` quirk: default false, never set. No.

Race comparison kills churn theories: race does MORE per vsync than
load-late of everything (bufB 30.5 vs 24.1 MB, dpush 187 vs 142, binds
108 vs 80, gsub 11.3 vs 11.2) yet Odin race is GameThread/VU1-bound with
GsWorker at 7.2 ms/frame (N12 S2). No per-vsync GPU-work count explains
loading pool-bound.

## Named mechanism

**None.** Loading splits into a quiet load-early (1440–1610, menu-like:
47.6 vsync/s Mac-det) and a race-level load-late (1610–1714: 20.4
vsync/s Mac-det, vs race 19.5/s). The 0.32× Odin loading number blends
the two; load-late alone may run ~0.15×. S3's pool-bound signature
(Turnip 65% + malloc + mutex) has no counterpart in any spiking counter.

## Fix

None (step-3 stop rule). No speed pair: ABBA needs a fix to compare.

## Det result (run-stats2 vs baseline)

`baseline.py compare` → hash lines match (`first_diff=None`),
snd/coverage IDENTICAL; tool verdict DIFFER from ONE glommed log line
([frame:dump]+[det-hash] interleaved at tick 528, pre-existing racy
logging — det-line counts vary run to run: baseline 2485, stats1 2462,
stats2 2488, same binary twice differing most). Guest state identical;
counting run is representative. Frames at 1090/1800/2100 not compared
(no fix gate to pass).

## Build / boot pins

- PS2Recomp md1 `5573ba7` (= `a3efbfe` + 2 tick lines); parallel-gs md1
  `5fc7ea1` (= `19d93b2` + counters/print, Granite gitlink → `30c87a6b`);
  Granite md1 `30c87a6b` (= `166ba21a` + counters). Never pushed.
- B1 stats+det build: `mac_build.sh --det`, then
  `cmake -S <wt> -B <bd> -DPGS_ENABLE_STATS=ON` + rebuild (PGS flag
  reaches 80 ninja edges). Runner
  `c6207ded…bd8f6f` (169.6 MB), tests `6d1d1bb7…8ce7f02`.
- Suite: 658/658 from the fork root (one cwd-sensitive test fails from
  other cwds — pre-existing, unrelated).
- Boots: MD1-stats (slot 1, 73.2 s, 2202 lines) + MD1-stats2 (slot 2,
  63.9 s, 2286 lines), both `bound=target`, tick 2406. Present cadence
  varies run to run (host-side skip race); det-hash unaffected.
- Runner-dir check `git diff --stat 14b1e5cb md1 -- ps2xRuntime/src/runner`
  empty. Scratch `~/dev/ssx3-work/MD1` 2.3 GB (≤ 10 GB).

## Fork commits

- Granite `30c87a6b` [MD1] counters (6 files, +206)
- parallel-gs `5fc7ea1` [MD1] option + tick + print (5 files incl. gitlink)
- PS2Recomp `5573ba7` [MD1] tick plumbing (2 files, +2)

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/MD1/PS2Recomp a3efbfe
git -C ~/dev/ssx3-work/MD1/PS2Recomp checkout -b md1
git -C ~/dev/parallel-gs worktree add --detach ~/dev/ssx3-work/MD1/parallel-gs 19d93b2
git -C ~/dev/ssx3-work/MD1/parallel-gs checkout -b md1
git -C ~/dev/ssx3-work/MD1/parallel-gs submodule update --init Granite
git -C ~/dev/ssx3-work/MD1/parallel-gs/Granite checkout -b md1
# third_party working files copied from F2 (same Granite rev/pins), no git:
cd ~/dev/ssx3-work/F2/parallel-gs/Granite/third_party && tar cf - --exclude=.git . | (cd ~/dev/ssx3-work/MD1/parallel-gs/Granite/third_party && tar xf -)
local/tooling/build/mac_build.sh ~/dev/ssx3-work/MD1/PS2Recomp ~/dev/ssx3-work/MD1/build-stats --pgs ~/dev/ssx3-work/MD1/parallel-gs --det
cmake -S ~/dev/ssx3-work/MD1/PS2Recomp -B ~/dev/ssx3-work/MD1/build-stats -DPGS_ENABLE_STATS=ON
cmake --build ~/dev/ssx3-work/MD1/build-stats --parallel 8 --target ps2x_tests ps2EntryRunner
cd ~/dev/ssx3-work/MD1/PS2Recomp && ~/dev/ssx3-work/MD1/build-stats/ps2xTest/ps2x_tests  # 658/658
python3 local/tooling/boot/ssx3_boot.py --mode det --backend parallel --runner ~/dev/ssx3-work/MD1/build-stats/ps2xRuntime/ps2EntryRunner --label MD1-stats2 --out ~/dev/ssx3-work/MD1/run-stats2 --env PGS_STATS=1
python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/MD1/run-stats2
```

## Gaps / recommended next action

| Gap | Reason / next step |
| --- | --- |
| Counts are Mac-only (MoltenVK) | Turnip-only branches (`desc=buffer` vs Mac `desc=plain`, map-failure paths) not covered. Next: Android stats build (`PGS_ENABLE_STATS=ON`, counters already in place) + Odin boot with `PGS_STATS=1` → direct Odin counts. Orchestrator schedules. |
| No Odin sub-phase profile | S3's window (867→1802) blends menu/setup/mode/loading/early-race; pool-bound sub-window unlocated. Next: windowed simpleperf on 1610–1714. |
| HybridMutex not counted | Symbol is in none of our sources (static third-party dep?); "if cheap" clause — skipped. |
| Present cadence racy | 2202 vs 2286 lines across two det-identical boots (host-side skip race). Means unaffected (loading 98%, race 100% coverage). |
| det-hash line count racy | 2485/2462/2488 across three runs; one glommed [frame:dump]+[det-hash] line. Pre-existing; hashes match. |
| Speed pair not run | Needs a fix to A/B; det-boot walls (mode 61, load-early 47.6, load-late 20.4, race 19.5/s) are diagnostic-build numbers, not speed. |

Budgets: 1 build dir (+1 incremental for round-2 counters), 2/6 boots
(one slot each), 0 exclusive holds, ~2 h of 2.5 h.
