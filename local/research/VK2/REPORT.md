# VK2 — Android Vulkan present: buffer release and lifecycle fixes (RV5 B1, B2, S1)

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/VK2.md`. Fork worktree
`~/dev/ssx3-work/VK2/PS2Recomp`, local branch `vk2` from fork `ssx3` tip `fb28d99`. Not pushed.

**Status: stopped at the first unexpected failure (external, not VK2): during the Odin lifecycle
stress run ST1, while this lane held the Odin lease, an APK was installed over the running app
(Android exit reason `16 PACKAGE UPDATED`, `installPackageLI`, 00:15:44).** Cycles 1–17 of the stress
are valid and clean (table below). Everything else in the brief that doesn't need the Odin is done:
the fix, 10 unit tests with mutation checks, suite 674/674, Mac det-hash IDENTICAL, one Android build.
Remaining: the stress rerun, the ABBA pair vs F6, the pixel run (5 of 6 launches left, 5 of 6 builds left).

### Blocker for the orchestrator: Odin lease conflict
- ST1 claimed the lease at 00:12:39 (`VK2 … ST1`, driver.log), installed `df27f812…` and ran.
- `dumpsys activity exit-info`: pid 3567 (ST1's app) ended **00:15:44.774, reason=16 (PACKAGE UPDATED),
  "stop com.ps2x.runner due to installPackageLI"** (`logs/ST1/exit-info.txt`). No crash, no tombstone.
- The relaunched process (pid 6875, started by the stress driver's next `am start`) **never made a
  `ps2x-game` layer** (`stress.txt` fg19..switch5), which fits the F5 play APK (GL) having been installed.
- Timeline pointing at F6 (not proven): F6's R2 cool-down ran alongside ST1 and finished 00:12:58 seeing
  ST1's app (`F6/logs/R2/cooldown.txt`: `pid=3567`); F6's R2 is an "A-F5" leg, which installs
  `4ff81032…`; F6's cool-down restarted at 00:18:21, right after ST1 released the lease.
  F6's `launch.py` checks the lease before installing, so the install came from outside it. Two adb
  transports reach the Odin (TLS mDNS serial and the old `192.168.1.53:5555`).
- ST1's restore then reinstalled F5 `4ff81032…` + env `a8d651a7…` (`logs/ST1/restore-play.txt`),
  which is Brad's play state, and may also have overwritten whatever the other agent had installed.
- Needed: serialize F6 and VK2 on the Odin (or confirm F6 is done), then resume VK2 from the stress
  rerun.

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

### ABBA vs F6 and pixels

Not run (stopped at the failure above).

## Pins and SHAs

| Item | Value |
| --- | --- |
| Fork base | `fb28d99` (fork `ssx3` tip at start, `git fetch fork`) |
| Fork `vk2` (local, not pushed) | `ace5b53` (ledger + tests + sink/backend), `91f65d5` (window-change counter log), `a523700` (proc fd count; not in an APK yet). Runner-dir diff vs `14b1e5cb`: empty |
| Mac suite runner | `ps2x_tests` `31cb0cb3…` (from `ace5b53`): 674/674 |
| Mac det runner | `7436ec9e…` (`ace5b53`; later commits are Android-only) |
| APK VK2 | `df27f812c9645433dfb103c7d7d8850c5e57858c145a6e8ae843c7d0ced784d6` (`91f65d5`) |
| APK F6 (ABBA reference) | `f39905dbf13431cd184b2dccf4f5baef66d46c62857d9beba76aa4fb5655740a` (`fb28d99`) |
| Brad's play state after ST1 | base.apk `4ff81032…`, env `a8d651a7…`, mc0 pins OK, lease `LEASE_FREE VK2 done` |

## Budgets

Android builds 1/6. Odin launches 1/6 (ST1). Mac: 2 builds (suite, det), 1 det boot (mini, one slot).
Scratch `~/dev/ssx3-work/VK2` ~1.6 GB after deleting the det build (mini 196.0/200 GB). bytesize
`/home/brad/vk2fix`.

## Gaps

- The stress rerun (20 cycles + 5 switches, with `proc_fds`), the ABBA pair vs F6 and the gralloc pixel
  run are still to do (blocked on the Odin lease conflict above).
- Detach semantics on device: the ledger resolves the last shown buffer from the detach transaction's
  completion (Android's documented contract). ST1 shows those completions arrive (18/18 layers
  released, 0 absent). Whether the compositor reports the detach's release early can't be observed from
  the app; the pool retirement makes it irrelevant (test "a detach that reports release early").
- No device run of the failure paths themselves (timeouts, POLLNVAL, give-up fallback): they are proven
  by the Mac tests only. ST1 hit none of them (all counters 0).
- Frame skip on no free slot keeps the last frame on screen; with 4 slots and pipelining, ST1 never skipped.

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
ssh bytesize 'wsl -d Ubuntu -- bash -lc /home/brad/vk2fix/build.sh'      # 9 m 54 s
python3 local/research/VK2/cooldown.py --label ST1
python3 local/research/VK2/launch.py --label ST1 --variant A --apk ~/dev/ssx3-work/VK2/apk/app-release.apk --apk-sha df27f812… \
  --stress 1850 --after-stress-s 60 --stop-tick 99999 --wall 590 --scap-ticks 1800
bash local/research/VK2/restore-play.sh
adb shell dumpsys activity exit-info com.ps2x.runner                     # reason=16 PACKAGE UPDATED
```

## Recommended next action (orchestrator decides)

Once the Odin is free of F6: one incremental build of `a523700` (fd log), then ST2 = the full stress
(20 + 5), then the ABBA pair vs F6 `f39905db…` (VK2, F6, F6, VK2), then the pixel run (compare ticks 1100 +
2100 with one bg/fg at 1300, so the second compare lands on a post-window-change pool). That is 6 launches
against the 5 left: drop one leg (e.g. fold the pixel compare into ST2) or grant one more.
