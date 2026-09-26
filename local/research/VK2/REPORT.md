# VK2 — Android Vulkan present: buffer release and lifecycle fixes (RV5 B1, B2, S1)

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/VK2.md`. Fork worktree
`~/dev/ssx3-work/VK2/PS2Recomp`, local branch `vk2` from fork `ssx3` tip `fb28d99`. Not pushed.

**Status: done.** Fix + 10 Mac tests (mutation-checked), suite 674/674, Mac det-hash IDENTICAL; Odin:
**full lifecycle stress (20 bg/fg + 5 app switches) clean** with bounded layers, buffers, fences and
process fds; **pixels exact through gralloc** at t1100 and at t3000 (after ~11 window changes, on a
rebuilt pool); **ABBA vs F6's APK: +0.5 % (no speed change)**. Fork `vk2` tip `a523700` (local, not
pushed); APK `29d3ca06…`. Brad's play state restored after every run.

| Brief check | Result |
| --- | --- |
| Mac unit tests (delayed callbacks, unsignalled fence, `EINTR`, `POLLNVAL`, same-pointer TERM/INIT_WINDOW, resolution change mid-flight, 100 recreate cycles) | 10 tests pass; each RV5 behaviour planted back makes them fail |
| Odin (a) lifecycle stress | ST2: 25 window changes in one process, 25/25 old layers released, 1 live layer, 4 buffer records, ≤ 3 fences held, **`proc_fds` flat at 146**, every timeout/error/stale counter 0; screencaps viewed |
| Odin (b) ABBA vs F6 at 1× | VK2 15.91 / 15.79 vs F6 15.79 / 15.75 vs/s → **0.264× vs 0.263× (+0.5 %)**, inside the VK2 legs' own 0.8 % spread |
| Odin (c) pixels via gralloc at two ticks | `diff_px=0` at t1100 and t3000 |
| Mac det-hash vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` | IDENTICAL (hash 1..2400, snd, coverage) |

### Lease incident (first attempt, ST1)
ST1 (APK `df27f812…`) was killed at 00:15:44 by an APK install made while VK2 held the Odin lease
(`dumpsys activity exit-info`: reason 16 PACKAGE UPDATED, `installPackageLI`; `logs/ST1/exit-info.txt`).
The orchestrator attributed it to an unleased `adb install` from BA1 and introduced
`local/tooling/odin_lease.sh` (atomic claim/release). ST1's 17 valid cycles were already clean (below).
From then on VK2 claimed the lease once through `odin_lease.sh` for the whole session
(`odin_session.sh`: cool-down → `launch.py` → `restore-play.sh` per leg, release on exit); `launch.py`
and `restore-play.sh` only check that VK2 holds it and never write it. The session started after
F6's Part 1 legs had finished (F6 report rows R1–R4 + 4× leg filled, lease free).

## RV5 finding → fix → test

Design: the sink's bookkeeping moved out of the NDK file into `ps2x_present_vk::Ledger`
(`ps2xRuntime/include/runtime/gs/ps2_present_vk_ledger.h`, `src/lib/gs/ps2_present_vk_ledger.cpp`),
which calls the NDK only through a `Platform` interface. `ps2_present_vk_android.cpp` is now the
NDK platform plus the JNI/diagnostic glue; `presentVk` in `ps2_gs_parallel_backend.cpp` uses
buffer ids, a pool epoch and `pickReusable`. The Mac tests (`ps2xTest/src/ps2_present_vk_ledger_tests.cpp`)
drive the ledger with a fake SurfaceFlinger that tracks which buffers it really holds (displayed,
queued-not-latched, or released with an unsignalled fence) and checks every write against that.

| RV5 | Fix (fork `vk2`) | Test that proves it (Mac, fake SF) |
| --- | --- | --- |
| **B1** failed/timed-out release wait still led to a write; `revents` unchecked; `EINTR` = failure; drop counter reset by successful queues; one timeout counter | A buffer is **usable only when every submission of it has been resolved by its completion and every delivered release fence polled `POLLIN`**. `pick()` waits (one 100 ms deadline) for a completion, then polls `dup`s of the fences; timeout → no slot, fences **kept open**; `POLLNVAL`/`POLLERR`/no `POLLIN` → the buffer is marked lost (never reused); `EINTR`/`EAGAIN` retried within the same deadline. No usable slot → **the frame is skipped** (screen keeps the last one), not written. **30 consecutive skips → fallback**: retire the pool, detach, readback/GL. `queue()` itself refuses a held buffer. Counters: `vk_cb_timeouts`, `vk_fence_timeouts`, `vk_fence_errors`, `vk_eintr`, `vk_skipped` (`vk_release_timeouts` = cb + fence) | "delayed completion keeps the buffer held": no pick before the completion (waited the 5 ms bound, `cb_timeouts=1`); completion with an **unsignalled fence** → still held, `fence_timeouts=1`, fence still open; signalled → picked, no fd left. "completion arriving during the wait wakes it" (thread delivers after 20 ms, 2 s budget). "EINTR / POLLNVAL": 3× EINTR then ready (`eintr=3`); POLLNVAL → `Error`, buffer never picked or queued again, a genuinely free buffer is used instead; EINTR forever → timeout inside the deadline, fence kept. "persistent failure": completions withheld → fallback after ≤ 31 frames, 0 writes into held buffers |
| **B2** window change cleared ownership and closed release fds; detach without completion; old callbacks keyed by raw pointer mutate the new use; `operator[]` recreated erased records | Every transaction carries a **unique token** `{layer id, buffer submission it releases}` (the callback context is the token number, never a pointer). Completions resolve only their own token; an unknown token or buffer **closes its fd and changes nothing** (`find`, never `operator[]`). Buffers have **allocation ids** (never reused), so an AHB address reused by the allocator is a new record. The **detach transaction registers completion** (reparent-to-null reports the last shown buffer's release). A window change **does not touch ownership**: it bumps the pool epoch; the backend **retires the whole slot pool** (never written again) and allocates a new one; `queue()` refuses any buffer of an older epoch; retired buffers keep the app's AHB reference until their completions arrive | "same-pointer TERM/INIT_WINDOW with completions outstanding": new layer for the reused pointer, epoch bumped, old-epoch buffer refused on the new layer, old layer kept while its completions pend, late old-layer completions resolve only their own records (`stale=0`), 0 held writes. "a detach that reports release early" (compositor says -1 but keeps scanning the buffer): 20 cycles, 0 writes into those buffers (pool retirement). "resolution change mid-flight; late completion vs a reused handle address": retired buffers kept until their completion, same pointer re-registered gets a new id, late completion releases only the old one, the new one has no stale fence |
| **S1** every retired `ASurfaceControl` leaked | Layers are records with an **outstanding-completion count**; a detached layer is `ASurfaceControl_release`d when its count reaches 0 (no completion can name it any more; the glue reads the layer from the token, alive by construction). **> 8 detached layers still owed completions → no new layer, GL fallback** (bounded). Fence fds are owned by records and closed on signal/retire; `dup`s closed after every poll | "100 recreate cycles" (alternating reused/new pointers, completions left outstanding across each change): 100 layers made, **100 released**, 0 records/tokens/fds left, every AHB reference released once; during the run ≤ 3 live layers, ≤ 12 records, ≤ 8 fds; 0 held writes; no layer used/released with a completion pending. "completions that never arrive": fallback at 8 detached layers. **Randomized** (4 seeds × 5000 frames: random latch/completion delays, 10 % out-of-order completions, fence delays, EINTR bursts, window churn with reused pointers, pool retirements; seed 3 omits the layer from detach stats): 0 held writes, everything released at the end, bounded throughout, 0 stale completions |

**Mutation checks** (each planted into the ledger, built, suite run, reverted): the tests fail for
each of the RV5 behaviours put back — (M1) delivered fence dropped instead of waited → 2 tests fail;
(M2) buffer reused while a completion is outstanding (VK1's timeout-grants-ownership) → 3 fail;
(M3) detach without completion, refs cleared at once (VK1's window change) → 2 fail;
(M5) no pool retirement / no epoch refusal on window change → 2 fail (the early-release test was
tightened until it caught this one: first version passed).

## Mac

| Check | Result |
| --- | --- |
| Suite (worktree root) | 674/674 (was 664/664 at `fb28d99`; +10 ledger tests) |
| Mutation checks | 4 planted RV5 behaviours, each caught (see above) |
| Det-hash, FR1-R1 to t2400 vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` | IDENTICAL (hash 1..2400, snd, coverage) |

## Android build (bytesize `/home/brad/vk2fix`, F6 inputs)

Source `git archive vk2` at `91f65d5` (tar `355f205d…` both ends); codegen, `vu1gen-f6`, paraLLEl-GS
`1b3a294` and jniLibs read from `/home/brad/f6` (the same inputs as F6's APK, so VK2 vs F6 differs only
by the fork delta). Script `local/research/VK2/build-android.sh` (`3646a1b6…` both ends). bytesize was
idle when it started (F6 and BA1 had finished). **BUILD SUCCESSFUL in 9 m 54 s**, no warnings from the
VK2 files. APK **`df27f812c9645433dfb103c7d7d8850c5e57858c145a6e8ae843c7d0ced784d6`**, 180,229,708 B
(×2 remote, ×2 local, installed base.apk matched). F6's APK pulled for the ABBA: `f39905db…` (×2 each end).
Local NDK r30 `-fsyntax-only` of the sink, ledger and the backend's Android block passed before the build
(checked that the backend check really parses the Android block: a planted typo fails it).

## Odin

### ST1 — lifecycle stress (APK `df27f812…`, 1× pipelined, VK default on, I26-FAST; stopped: external install)

Cool-down to status 0 + 180 s; lease, keyguard `showing=false`, AC, 100 %; force-stop + env restore after;
Brad's play state restored (`restore-play.sh`: F5 `4ff81032…`, env `a8d651a7…`, save 6/6, `mc0-test` empty).
Stress from tick 1899 in the race: HOME → back with 0.5 / 1 / 2 / 5 s in the background, then Settings → back.

| Measure (valid part: start + cycles 1–17, pid 3567) | Result |
| --- | --- |
| Window changes (layers made) | 19 (the first layer + 18 recreations: TERM/INIT_WINDOW each time on the **same** `ANativeWindow` pointer `0xb400006f0ccbe8e0`) |
| Layers released (`ASurfaceControl_release`) | **18**; at each of the 28 window-change samples **`vk_layers=1`, `vk_layers_detached=0`**: each detached layer's completion had arrived and it was released before the next change (VK1 would hold 18 in `graveyard`) |
| SurfaceFlinger `ps2x-game` layers | 1 in the foreground, 0 in the background, every cycle (`stress.txt`) |
| Slot pools | retired and remade at each change (epochs 1→19); **76 buffers released** (19 × 4); `vk_bufs=4` (just the live pool) |
| Completions / timeouts / errors | 2,818 completions for 2,800 queued (+ 18 detach completions); **`vk_cb_timeouts=0 vk_fence_timeouts=0 vk_fence_errors=0 vk_eintr=0 vk_stale_cb=0 vk_absent_cb=0 vk_refused=0 vk_skipped=0 vk_dropped=0`**, `vk_tokens=0` |
| Release fences held by the ledger | ≤ 3 (`vk_fences_held`) |
| Process fd count | **not measured**: the release APK isn't debuggable, so `run-as` can't list `/proc/<pid>/fd` (cell reads `run-as:` empty). Fixed for the rerun: fork `a523700` logs `proc_fds` from `/proc/self/fd` at every window change (not built yet) |
| Screencaps viewed | `sc02` (after cycle 5), `sc03` (10), `sc04` (15): full-screen 16:9 race, HUD, rider, trail, correct colours. `sc05`/`sc06` come from the reinstalled app (not VK2) |
| Cost | `vk_release_wait_ms_avg=0.013`, `vk_apply_ms_avg=0.141` (VK1 V2: 0.009 / 0.121) |
| Cycles 18–20 and the 5 app switches | **void**: pid 3567 killed by the external install during cycle 18's background wait |

### ST2 — full lifecycle stress + pixel compares (APK `29d3ca06…` = `a523700`)

Same method as ST1 (cool-down to status 0 + 180 s, keyguard off, AC, 100 %), stress from tick 1903;
`PS2X_PRESENT_VK_COMPARE_TICKS=1100,3000` (sync present + readback at those ticks; t3000 falls during
the stress, after ~11 window changes, so it checks a rebuilt pool). One process (pid 1041) throughout.

| Measure | Result |
| --- | --- |
| Window changes | 20 HOME→back (0.5 / 1 / 2 / 5 s away) + 5 Settings→back = **25**; layers made 26 (first + 25), **released 25** |
| At each of the 26 window-change samples | **`vk_layers=1 vk_layers_detached=0 vk_bufs=4 vk_tokens=0`**, `vk_fences_held` ≤ 3 |
| Process fds (`proc_fds`, `/proc/self/fd`) | **123** at the first window (before the Vulkan slots/fences), then **146 at every one of the next 25 changes**: no growth |
| SurfaceFlinger `ps2x-game` layers | exactly 1 in the foreground (26 samples), 0 in the background (25 samples) |
| Slot pools | a new pool after every change (+ two boot-time scanout size changes 2560×448 → 640×448 → 512×448, which exercised the size-change retirement too); **104 buffers released**, 4 live |
| Final counters (tick ~5440) | `vk_queued=3270 vk_callbacks=3295` (3270 queues + 25 detaches), **`vk_dropped=0 vk_skipped=0 vk_cb_timeouts=0 vk_fence_timeouts=0 vk_fence_errors=0 vk_eintr=0 vk_stale_cb=0 vk_absent_cb=0 vk_refused=0`**; `vk_release_wait_ms_avg=0.013`, `vk_apply_ms_avg=0.139` |
| **Pixels via gralloc** | **t1100: `diff_px=0`**, ahb = readback `ad2e9e852b54155a` (same hash as VK1's t1100); **t3000: `diff_px=0`**, `9e19d118a201e2ee`; 512×448, gralloc stride 768; PPM pairs byte-identical (`7cab2999…`, `88b05c26…`) |
| Screencaps viewed | `sc01` (t1846), after cycles 5/10/15/20, after the 5 switches (race t~0:45, 44 mph) and final (t5440, race t~1:02, "SUPER UBER"): full-screen 16:9, HUD, rider, trail, correct colours |
| End | env restored `a8d651a7…`, mc0 pins OK, 0 disconnects, no FATAL |

### ABBA vs F6 (1× pipelined, VK default on, I26-FAST, unpaced, sound on, stop 4500)

Cool-down to status 0 + 180 s before each leg, reinstall each leg (installed base.apk SHA matched every
time), Brad's play state restored after each. Rates by F4's `phases.py` (race = ticks 1714→stop);
per-thread CPU over ticks ~1900→2550 (unprofiled); GPU = kgsl `gpubusy` race mean.

| Leg | APK | Race (ticks / wall) | vs/s | × | GameThread ms/frame | GsWorker ms/frame | GPU busy (n) | Thermal status | VK counters |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Q1 | VK2 `29d3ca06…` | 1714→4686 / 186.8 s | 15.91 | 0.265× | 45.69 | 12.55 | 36.4 % (31) | 0→3→2 | dropped/skipped/timeouts/errors 0 |
| Q2 | F6 `f39905db…` | 1714→4586 / 181.9 s | 15.79 | 0.263× | 44.84 | 12.29 | 36.3 % (30) | 0→3→2 | (F6's sink: no split counters) |
| Q3 | F6 | 1714→4579 / 181.9 s | 15.75 | 0.263× | 46.66 | 12.60 | 36.5 % (31) | 0→3→2 | — |
| Q4 | VK2 | 1714→4587 / 182.0 s | 15.79 | 0.263× | 44.74 | 12.25 | 36.7 % (31) | 0→3 | all 0 |

**VK2 15.85 vs/s (0.2644×) vs F6 15.77 (0.2631×): +0.5 %**, smaller than the spread between the two VK2
legs (0.8 %) and in line with F6's own R1/R4 (15.77 / 15.73). No speed change. The per-frame pick adds a
`dup` + `poll(0)` + `close` of one release fence; `vk_release_wait_ms_avg` stays 0.013 ms. Screencaps at
t~2170 are the same game frame on both APKs (Q2 vs Q4, including the game's own cyan panel at that moment).

## Pins and SHAs

| Item | Value |
| --- | --- |
| Fork base | `fb28d99` (fork `ssx3` tip at start, `git fetch fork`) |
| Fork `vk2` (local, not pushed) | `ace5b53` (ledger + tests + sink/backend), `91f65d5` (window-change counter log), **`a523700`** (proc fd count) = tip. Runner-dir diff vs `14b1e5cb`: empty |
| Mac suite | `ps2x_tests` `31cb0cb3…`: 674/674 at `ace5b53` and at the tip (`91f65d5`/`a523700` touch only the Android file) |
| Mac det runner | `7436ec9e…` (`ace5b53`) |
| APK 1 (ST1 only) | `df27f812c9645433dfb103c7d7d8850c5e57858c145a6e8ae843c7d0ced784d6` (`91f65d5`) |
| **APK 2 (ST2, Q1, Q4)** | **`29d3ca066de3b8dfe74c511dbf87e99168ba13acbf4262396c4006228e914469`** (`a523700`; incremental, 19 s), ×2 remote ×2 local, installed match every leg |
| APK F6 (Q2, Q3) | `f39905dbf13431cd184b2dccf4f5baef66d46c62857d9beba76aa4fb5655740a` (`fb28d99`, same inputs) |
| Build inputs | bytesize `/home/brad/f6/{codegen-ssx3,vu1gen-f6,parallel-gs (1b3a294),jniLibs}`; source `/home/brad/vk2fix` (tar `355f205d…`, delta `2914c252…` both ends) |
| Brad's play state after the session | base.apk `4ff81032…`, env `a8d651a7…`, mc0 pins OK, `mc0-test` empty, app stopped, lease `LEASE_FREE VK2 done` |

## Budgets

Android builds 2/6 (full 9 m 54 s; incremental 19 s). Odin launches 6/6 (ST1, ST2, Q1–Q4; the pixel check
was folded into ST2). Mac: 2 builds, 1 det boot (mini, one slot). Scratch `~/dev/ssx3-work/VK2` ~2 GB
(det build deleted; mini 196/200 GB). bytesize `/home/brad/vk2fix`. Wall ~23:30–01:35.

## Gaps

- The failure paths (callback/fence timeouts, `POLLNVAL`, 30-skip give-up, 8-detached-layer cap) are
  proven by the Mac tests only; no device run hit them (all counters 0 in 7,000+ presents and 43 window changes).
- Detach semantics on device: every detach completion arrived (43/43 layers released over ST1+ST2, 0
  absent). Whether the compositor might report a detached buffer's release early can't be seen from the
  app; the pool retirement makes it irrelevant (Mac test "a detach that reports release early").
- Frame skip (no released slot) keeps the last frame on screen; never happened on device.
- ST2's pixel compares are diagnostic sync presents inside a stress run; the ABBA legs carry no compare.
- Retiring the pool on every window change costs one `wait_idle` + 4 AHB allocations/imports per
  background/foreground (not timed separately; the app is in the background then).

## Exact commands

```sh
git -C ~/dev/PS2Recomp fetch fork && git -C ~/dev/PS2Recomp worktree add -b vk2 ~/dev/ssx3-work/VK2/PS2Recomp fork/ssx3
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/VK2/PS2Recomp ~/dev/ssx3-work/VK2/build --target ps2x_tests
(cd ~/dev/ssx3-work/VK2/PS2Recomp && ../build/ps2xTest/ps2x_tests)       # 674/674
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/VK2/PS2Recomp ~/dev/ssx3-work/VK2/build-det --det --target ps2EntryRunner
python3 local/tooling/boot/ssx3_boot.py --host mini --mode det --backend parallel --runner ~/dev/ssx3-work/VK2/build-det/ps2xRuntime/ps2EntryRunner \
  --label VK2-det --stop-tick 2400 --sound on --route fr1r1 --coverage-tick 2400 --vu1-stats --dump-ticks 1090,1800,2100 --out ~/dev/ssx3-work/VK2/run/VK2-det
python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/VK2/run/VK2-det   # IDENTICAL
$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/clang++ --target=aarch64-linux-android29 -std=c++20 -fsyntax-only -Ips2xRuntime/include ps2xRuntime/src/lib/gs/ps2_present_vk_android.cpp
git archive --format=tar vk2 | ssh bytesize 'wsl -d Ubuntu -- bash -c "… tar -x -C /home/brad/vk2fix/PS2Recomp"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc /home/brad/vk2fix/build.sh'      # 9 m 54 s; a523700 delta: 19 s
python3 local/research/VK2/cooldown.py --label ST1; python3 local/research/VK2/launch.py --label ST1 …   # pre-odin_lease.sh (ST1 only)
local/research/VK2/odin_session.sh \
  "ST2|--variant A --apk …/apk2/app-release.apk --apk-sha 29d3ca06… --stress 1850 --after-stress-s 60 --stop-tick 99999 --wall 590 --scap-ticks 1800 --compare-ticks 1100,3000" \
  "Q1|--variant A --apk …/apk2/app-release.apk --apk-sha 29d3ca06… --stop-tick 4500 --cpu-window 1850,2550 --scap-ticks 2100" \
  "Q2|… f6-apk … f39905db …" "Q3|… f6-apk …" "Q4|… apk2 …"
python3 local/research/F4/phases.py local/research/VK2/logs/Q{1,2,3,4}
adb shell dumpsys activity exit-info com.ps2x.runner                     # ST1: reason=16 PACKAGE UPDATED
```

## Recommended next action (orchestrator decides)

Fold fork `vk2` (`ace5b53`, `91f65d5`, `a523700`; clean on `fb28d99`) into fork `ssx3` and let the Odin
play build ship with the Vulkan present on by default (drop `PS2X_PRESENT_VULKAN=0` from Brad's env).
Keep the `proc_fds` / window-change stats line (one line per window change, no per-frame cost).
