# FS2 — the GsWorker's kgsl wait in paraLLEl's `submit_empty`

Worker: Claude Code (Opus). Brief: `local/muse/prompts/FS2.md`. Date: 2026-09-26.

## Status

**Stage 1 done; Stage 2 paused on a blocker after 1 of 8 Odin launches (S2 aborted before launch).**
- **Mechanism (source + Odin S1):** each Granite queue submission signals Granite's queue
  timeline. On Turnip/kgsl that timeline is emulated, and allocating its next point GCs the
  previous one with a zero-timeout wait. kgsl treats timeout 0 as **wait forever**. So
  paraLLEl's second, command-free `submit_empty` waits for the flush's GPU work to finish.
- **Odin S1 (fs2 APK, legacy two-submit path, split timers):**
  - 1st `submit_empty` (the real `vkQueueSubmit2`): **0.12 ms/frame**.
  - 2nd, command-free `submit_empty2` (makes no kernel call of its own, S8; its time is the GC
    wait): **22.2 ms/frame**.
  - Prediction (a) holds; (b) predicted the reverse.
  - GS-queue-full on MTVU: 8.2 ms/frame.
  - Race 23.43 vs/s = 0.391×, same as CP1 R1/R3.
- **Fix (one candidate):** signal the GS and descriptor timelines from the one real submission.
  It is built, and it passes the Mac gates:
  - det-hash IDENTICAL, both on the measured base and after the rebase.
  - Suite 681/681 measured, 689/689 rebased.
  - Every Mac frame-dump hash falls within control's own run-to-run set. Byte identity across
    runs is impossible with this dump path, see Gates.
- **Not measured on the Odin yet:** the fix's effect (S2), the gralloc compare and the ABBA.
- **Blocker** (Recommended next action): `odin_restore_play.sh` still requires the old play env
  (`WANT_ENV=ef9f94e1…`). Commit `931fc818` moved the play env to `090cc981…` (LAG on). The
  brief's ABBA says LAG off, but Brad's play build is now LAG on.

## Stage 1 — why `submit_empty` blocks (source reading)

Sources: Turnip = Mesa `c501e1d16e` (the bundled driver, VK1 D2), files fetched from
gitlab raw into `~/dev/ssx3-work/FS2/mesa/`; Qualcomm kgsl `adreno_drawctxt.c`
(LineageOS `android_kernel_qcom_sm8650-modules`, lineage-22.2); Granite `166ba21a`;
paraLLEl-GS `1b3a294`.

| # | Fact | Where |
| --- | --- | --- |
| S1 | Granite `Device::submit(cmd)` with no fence/semaphore only queues the command buffer; the real `vkQueueSubmit2` happens in the next `submit_queue`, i.e. inside `flush_submit`'s first `submit_empty`. CP1's "main submits 6 µs" are pure queueing. | Granite `vulkan/device.cpp` `submit_nolock` (only calls `submit_queue` when `fence \|\| semaphore_count`) |
| S2 | Every Granite queue submission (including an empty one) signals Granite's own queue timeline semaphore with `++current_timeline`. | `submit_queue` / `submit_empty_inner` → `emit_queue_signals` |
| S3 | Turnip's kgsl backend implements timelines as **emulated** `vk_sync_timeline` over binary kgsl syncobjs → runtime timeline mode `EMULATED` → submit mode `DEFERRED`. No submit thread exists in this mode (`MESA_VK_ENABLE_SUBMIT_THREAD` only applies to `ASSISTED`). | `tu_knl_kgsl.cc:1878` `vk_sync_timeline_get_type(&vk_kgsl_sync_type)`; `vk_device.c` `get_timeline_mode`, `vk_device_init` switch |
| S4 | Signalling an emulated timeline allocates a point, and allocation first garbage-collects: for each pending (already submitted) point with no other reference, `vk_sync_wait(point, …, abs_timeout_ns = 0)` — meant as a poll. | `vk_sync_timeline.c` `vk_sync_timeline_alloc_point_locked` → `vk_sync_timeline_gc_locked`; called from `vk_queue_submit_final` (`vk_sync_signal_unwrap`) **before** `driver_submit` |
| S5 | Turnip's kgsl wait on a timestamp syncobj converts the absolute timeout to relative ms (`get_relative_ms(0)` = 0) and calls `IOCTL_KGSL_DEVICE_WAITTIMESTAMP_CTXTID` with `timeout = 0`. | `tu_knl_kgsl.cc` `kgsl_syncobj_wait` → `wait_timestamp_safe` |
| S6 | **kgsl treats `timeout == 0` as "wait forever"**: `if (timeout == 0) timeout = UINT_MAX;` then `wait_event_interruptible_timeout(...)` until the timestamp retires. | `adreno_drawctxt.c` `adreno_drawctxt_wait` |
| S7 | So each "poll" in S4 is a blocking wait until that point's GPU work retires. Mesa `main` has the same code in both files (checked 2026-09-26). | S4 + S5 + S6; `diff` of `tu_knl_kgsl.cc` wait helpers vs `main`: identical |
| S8 | A Turnip submit with no command buffers never reaches the kernel (it only merges wait syncobjs into the signal syncobjs). | `kgsl_queue_submit` `commands.size == 0` branch |
| S9 | paraLLEl's `flush_submit` does `submit_empty(GS timeline)` (= the real `vkQueueSubmit2` of the flush, S1), then a **second, command-free** `submit_empty(descriptor timeline)`. The second one signals Granite's queue timeline again (S2), whose point allocation GCs the point the first submit just installed → blocks in kgsl until **this flush's GPU work has finished**. | `gs/gs_renderer.cpp` `flush_submit` |
| S10 | The GS timeline's GC normally does not block: PGS-Waiter holds a reference on the point it waits on (`refcount > 1` → GC stops). The Granite queue timeline and the descriptor timeline have no waiter. | `GSRenderer` ctor (PGS-Waiter), `vk_sync_timeline_wait_locked` refs the point |

**Verdict on the brief's hypotheses (from source; Odin split below):** (a) is the mechanism, in
a specific form: emulated timelines + a zero-timeout "poll" that the kgsl kernel turns into an
infinite wait. It is not (b): no fence is waited on, and the command-free submit makes no ioctl
at all (S8), so its time is all in the GC wait. (c) is unlikely: GPU 50 % busy at a flat 660 MHz
(CP1 Table 4) means the GPU is not saturated. What the wait does is serialize CPU and GPU once
per flush.

**Predictions (observable = the CP1 split timers, with the second `submit_empty` now timed
separately as `submit_empty2`):**

| Hypothesis | legacy path: 1st `submit_empty` | legacy path: 2nd (`submit_empty2`) | fix (one submit, both signals) |
| --- | --- | --- | --- |
| (a) GC wait on Granite's queue timeline | small (the GC waits only for the *previous* flush) | ≈ the flush's GPU time (~5 ms/flush) | 2nd gone; the 1st waits only if the previous flush hasn't retired → most of the ~22 ms/present disappears |
| (b) kernel back-pressure in `GPU_COMMAND` | carries the wait | ≈ 0 (no ioctl, S8) | no change |
| (c) GPU behind | wait anywhere | — | no change in race rate |

**Fix candidate (the brief's first one):** signal both the GS timeline and the descriptor
timeline from the one real submission. Granite gets a `submit_empty(type, fence, sem, sem2)`
overload; the second external signal goes into the same `VkSubmitInfo2` batch as the first.
Vulkan semaphore-signal ordering: a signal's first sync scope covers every command earlier in
submission order, so a descriptor-timeline value signalled with the flush's batch completes no
later than the old empty submit's signal did. The descriptor pool recycling that reads it
(`get_bindless_pool`) is at least as safe. No GPU command changes.
`PS2X_PGS_FS2_LEGACY=1` restores the two-submit path, for the A/B inside one APK.

**Not taken (out of this brief's allowed changes; recorded as the root-cause fix):** patch Turnip
so a zero-timeout wait on a timestamp syncobj polls, e.g. `IOCTL_KGSL_CMDSTREAM_READTIMESTAMP_CTXTID`
(retired) + `timestamp_cmp`, instead of calling `WAITTIMESTAMP` with 0. That would remove every such
wait (all Granite submits, frame-context and present submits included), not just the one in
`flush_submit`. It needs our own Mesa Android build (we ship a prebuilt), and it's a driver change.
No upstream contact.

## Branches (local only, never pushed)

| Repo | Branch | Measured (Odin APK, Mac gates) | Rebased (orchestrator 09-26: fork `f0d2d3c`, paraLLEl `3d72467`) |
| --- | --- | --- | --- |
| Granite (submodule in the FS2 clone) | `fs2` | `f0009780` on `166ba21a` | same (`3d72467` still pins `166ba21a`) |
| paraLLEl-GS `~/dev/ssx3-work/FS2/parallel-gs` | `fs2` (`fs2-measured` keeps the old base) | `8a89cbb` CP1 timers (cherry-pick of `b0e331a`) + `35f4462` fix, on `1b3a294` | `b1bca63` + **`19ee3f2`** on `3d72467`, clean |
| PS2Recomp fork `~/dev/ssx3-work/FS2/PS2Recomp` | `fs2` (`fs2-measured` keeps the old base) | `3ad5038` CP1 print (cherry-pick of `10dfcb2`) + `f6529bf` print + `90499a0` GS-queue counter, on `5d5c382` | `cd6ec8a` + `668e777` + **`f532dc8`** on `f0d2d3c`, clean; runner-dir guard empty |

The fix itself is paraLLEl `19ee3f2` + Granite `f0009780`. Everything else is diagnostics:
- CP1's split timers (default off, `PS2X_PGS_FLUSH_SPLIT=1`).
- The legacy toggle (`PS2X_PGS_FS2_LEGACY=1`).
- `submit_empty2_ms` and `gsq_full_{ms,waits}` on the existing `[gs:parallel] sync` line (every
  300 presents).
- The GS queue-full counter times only an `enqueue` that actually blocks; the non-blocking path
  is one predicate call, as before.

The orchestrator decides what to fold. If the diagnostics shouldn't ship, fold only the two fix
commits.

## Gates (Mac mini, M5 Pro, MoltenVK)

| Gate | Result | Receipt |
| --- | --- | --- |
| Det-hash + snd/coverage, FR1-R1 t2400, vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` | control (tip `5d5c382`+`1b3a294`) **IDENTICAL**; fs2 measured **IDENTICAL**; fs2 rebased **IDENTICAL** | `mac/det-compare.txt`, runner SHAs `mac/runners.txt` |
| Suite `ps2x_tests` (from worktree root) | measured 681/681; rebased 689/689 | build logs in scratch |
| Mac frame dumps at fixed ticks, byte-identical to control | **Not achievable as specified, for control either.** `PS2X_FRAME_DUMP_ONCE_TICKS` takes "the first frame within the following two guest seconds" (`ps2_runtime.cpp` ~l.556), and the GS runs on the GsWorker. What a dump captures depends on host timing: **control differs from control** at 6 of 8 ticks, and one dump landed on tick 1501 instead of 1500. Over 11 boots (5 control + 3 fs2 at 1090/1100/1110; 3 control + 1 fs2 at 1500/2250/2390; 1 + 1 at 1090/1800/2100): **every fs2 hash is one control also produced, at all 8 ticks**. 1800 and 2100 are single-valued and byte-identical across control, fs2 and the key. | `mac/frame-dumps.txt`; table below |
| Deterministic replay (2.5 GB GS capture of the control run, FR1-R1 t0–2400, 1,833,413 packets) through control ×2, fs2, fs2+legacy | all 4 replays ran the whole stream, identical summaries, suite green. **No pixels:** the Mac parallel replay path returns `vram=0 present=0` (no readback), so this checks that the new submit path runs, not the pixels | `mac/replay.txt` |
| Odin gralloc compare `diff_px=0` (VK1/VK2 t1100/t3000) | **not run** (S2 aborted before launch) | — |

Frame-dump hashes (fnv1a of the RGBA dump) per tick; control runs vs fs2 runs:

| Tick | control hashes seen | fs2 hashes seen | fs2 ⊆ control |
| ---: | --- | --- | --- |
| 1090 | 5136e0ea, 5ad91594 | 5136e0ea, 5ad91594 | yes |
| 1100 | 528e7d00, 0a907c9a | 0a907c9a | yes |
| 1110 | ea1ebd4b, f80c0d2a | f80c0d2a | yes |
| 1500 | 7e6f2dcd, 8e6eecd1 | 8e6eecd1 | yes |
| 1800 | 26b7c5c7 | 26b7c5c7 | yes |
| 2100 | 7ad8f18d | 7ad8f18d | yes |
| 2250 | 65894ff2, ced28e5c | 65894ff2 | yes |
| 2390 | 7fbfda38, f51bb617 | 7fbfda38 | yes |

(Control vs control, 1090: 3,882 px differ, bbox x19–496 y63–345 on the Select Peak screen;
`pngdiff.py` in scratch.)

## Odin

Driver: CP1's `launch.py` + `cooldown.py` copied and repointed (label/lease `FS2`,
`/data/local/tmp/fs2`, allowlist + `PS2X_PGS_FS2_LEGACY`); `run1.sh` = cool-down → launch →
`odin_restore_play.sh`. Settings as CP1 R1: variant A (1×, present pipeline), MTVU + VU1 blocks,
GameThread cpu6, MTVU cpu7, LAG off, I26-FAST, unpaced, stop 4500, cpu window 1900–2500.

APK (build #2 = the only one used): `d5f83cef…5659ece` (`d5f83cefa4bfd6ab17591ee0f27694b0307002ba8ca2bebe940434eff5659ece`),
190,764,620 B, pulled from bytesize and read twice on the mini (match). Strings
`gsq_full_ms_per_present`, `PS2X_PGS_FS2_LEGACY`, `submit_empty2_ms_per_present` checked
inside `libps2EntryRunner.so`. Build #1 (`71f984b8…`) is superseded, never installed.

| Launch | Env beyond play keys | Result |
| --- | --- | --- |
| S1 | `PS2X_PGS_FS2_LEGACY=1 PS2X_PGS_FLUSH_SPLIT=1` | STOP 4574, 156 s wall, race 23.43 vs/s = 0.391×; `[mtvu] jobs=55501 violations=0`; cool-down PRE/POST status 0; 100 % on AC; restore RC 0 (then env `ef9f94e1`) |
| S2 | `PS2X_PGS_FLUSH_SPLIT=1` + `--compare-ticks 1100,3000` | **aborted before install**: device env was `090cc981…` (the orchestrator's `ORCH-LAG` had changed the play env meanwhile). The driver refused to touch it (pin `ef9f94e1`). The restore then pushed the play APK + the new play env and failed its own env check (`WANT_ENV` still `ef9f94e1`). No launch consumed |

S1 race window, sync line (ticks 2196→4296, 2,100 presents = 2,100 frames; `logs/S1/syncsum.txt`):

| ms per frame | S1 legacy |
| --- | ---: |
| `flush_submit` | 22.74 |
| main `device->submit` ×~6 (queueing only) | 0.006 |
| 1st `submit_empty` (the real `vkQueueSubmit2`, GS timeline signal) | **0.12** |
| **2nd `submit_empty` (command-free descriptor-timeline signal)** | **22.21** |
| compile drain | 0.0004 |
| MTVU GS-queue-full (`GsWorker::enqueue` blocked; 3.2 waits/frame) | **8.24** |
| flush_submits per frame | 4.17 |

S1 three-way (schedstat, ticks 1948→2574, 48.42 ms/frame): MTVU 28.6 / 0.6 / 19.2,
GameThread 12.3 / 0.1 / 36.0, GsWorker 10.1 / 3.4 / 34.9 (run / runnable / blocked). This matches
CP1 R1 (MTVU 28.7 / 1.9 / 18.2, GsWorker 9.6 / 3.7 / 35.4) and R3's 22.1 ms `submit_empty`
total, so the fs2 APK on the legacy path reproduces the play build.

Device state after S2 (read-only check, `logs/S2-device-state.txt`):
- APK `825b436d…`, env `090cc981…`: Brad's current play state per `odin-play/SHA256SUMS`.
- App not running, `mc0-test` empty.
- **6/6 saves match** the E55D16 pins.
- Lease `LEASE_FREE ORCH-LAG done`.

The restore script didn't reach its own save loop. The check above stands in for it.

## Recommended next action (orchestrator decides)

1. Unblock the restore. Set `odin_restore_play.sh` `WANT_ENV` to `090cc981…`, or read it from
   `odin-play/SHA256SUMS`. Workers may not edit shared tooling, so I stopped here.
2. Decide the ABBA settings: the brief's "LAG off" (comparable to CP1/S1), or Brad's new play
   settings (LAG on). The ABBA B leg is the play APK with its env built by the driver, so either
   is one flag. My driver's device-env pin also needs `090cc981`.
3. Then resume with the same APK (`d5f83cef…`), no new build:
   - S2: fix + split timers + gralloc compare at 1100/3000.
   - ABBA ×4 vs the play APK: race rate, GsWorker blocked, gsq_full.

   That is 5 more launches (6 of 8 in total).
   - Prediction: `submit_empty2` goes to 0.
   - The one `submit_empty` waits only when the previous flush hasn't retired.
   - GsWorker's kgsl wait and MTVU's GS-queue-full both drop.
4. Root cause beyond this brief: Turnip's `kgsl_syncobj_wait` with `abs_timeout_ns == 0`. It
   should poll the retired timestamp (`IOCTL_KGSL_CMDSTREAM_READTIMESTAMP_CTXTID`), not
   `WAITTIMESTAMP` with 0. That would remove the same wait from every other Granite submission
   too (frame-context, present). It needs our own Mesa Android build.

## Exact commands

```sh
# sources
mkdir -p ~/dev/ssx3-work/FS2/mesa && curl -sfL https://gitlab.freedesktop.org/mesa/mesa/-/raw/c501e1d16e/<path>  # tu_knl_kgsl.cc, tu_queue.cc, vk_queue.c, vk_device.c, vk_sync_timeline.c, vk_sync.c, …
curl -sfL https://raw.githubusercontent.com/LineageOS/android_kernel_qcom_sm8650-modules/lineage-22.2/qcom/opensource/graphics-kernel/adreno_drawctxt.c
# branches
git clone ~/dev/parallel-gs ~/dev/ssx3-work/FS2/parallel-gs && git checkout -b fs2 1b3a294 && git submodule update --init --recursive
git fetch ~/dev/ssx3-work/CP1/parallel-gs cp1 && git cherry-pick b0e331a        # + FS2 edits (Granite fs2 f0009780, pgs 35f4462)
git -C ~/dev/PS2Recomp worktree add -b fs2 ~/dev/ssx3-work/FS2/PS2Recomp 5d5c382 && git cherry-pick 10dfcb2   # + f6529bf, 90499a0
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/FS2/PS2Recomp-ctl 5d5c382
# Mac gates
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/FS2/PS2Recomp-ctl ~/dev/ssx3-work/FS2/build-ctl-det --det --target ps2EntryRunner --target ps2x_tests
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/FS2/PS2Recomp ~/dev/ssx3-work/FS2/build-fs2-det --det --pgs ~/dev/ssx3-work/FS2/parallel-gs --target ps2EntryRunner --target ps2x_tests
python3 local/tooling/boot/ssx3_boot.py --host mini --mode det --backend parallel --runner …/build-{ctl,fs2}-det/ps2xRuntime/ps2EntryRunner --label FS2-det-{ctl,fs2} --stop-tick 2400 --sound on --route fr1r1 --coverage-tick 2400 --vu1-stats --dump-ticks 1090,1800,2100
python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/FS2/run/FS2-det-{ctl,fs2,fs2r}
# (+ dump-variance boots: --stop-tick 1200 --dump-ticks 1090,1100,1110; --stop-tick 2400 --dump-ticks 1500,2250,2390)
python3 local/tooling/boot/ssx3_boot.py … --label FS2-cap --env PS2X_GS_CAPTURE=…/cap/fr1r1-t2400.capture.bin --env PS2X_GS_CAPTURE_STOP_TICK=2400
(cd <worktree> && PS2X_GS_REPLAY_CAPTURE=…capture.bin PS2X_GS_REPLAY_BACKEND=parallel PS2X_GS_REPLAY_PPM_TICKS=1090,1100,1500,1800,2100,2250,2390 PS2X_GS_REPLAY_PPM_DIR=… [PS2X_PGS_FS2_LEGACY=1] …/ps2xTest/ps2x_tests)
# Android (bytesize, CP1/VR3 recipe; build-android.sh here)
git -C ~/dev/ssx3-work/FS2/PS2Recomp archive --format=tar fs2 > fork-fs2.tar   # c9ba2765… both ends
tar -cf pgs-fs2.tar --exclude=.git -C ~/dev/ssx3-work/FS2 parallel-gs          # 4ea3178c… both ends
ssh bytesize 'wsl -d Ubuntu -- bash -lc /home/brad/fs2/build.sh'              # #1 14m09s; #2 (3 changed files copied in, fresh mtimes) 14m32s
# Odin
local/research/FS2/run1.sh S1 …/app-release-fs2.apk d5f83cef… --env PS2X_PGS_FS2_LEGACY=1 --env PS2X_PGS_FLUSH_SPLIT=1
local/research/FS2/run1.sh S2 …/app-release-fs2.apk d5f83cef… --env PS2X_PGS_FLUSH_SPLIT=1 --compare-ticks 1100,3000   # aborted (blocker)
python3 local/research/FS2/phases.py local/research/FS2/logs/S1; python3 local/research/FS2/syncsum.py local/research/FS2/logs/S1
```

## Gaps

| Gap | Reason |
| --- | --- |
| Fix not measured on the Odin (S2, ABBA, gralloc compare) | blocker above; 1 of 8 launches used |
| Mac pixel identity is set-membership, not byte identity | dumps are host-timing dependent for control too; Mac parallel replay has no readback. The Odin gralloc compare (VK2 hashes t1100 `ad2e9e852b54155a`, t3000 `9e19d118a201e2ee`) is the pending hard pixel gate |
| The Odin kgsl is assumed to match the sm8650 source | Odin 3 = SM8750, whose kgsl source I didn't fetch; S1's split (0.12 vs 22.2 ms) matches the infinite-wait reading, not a poll |
| The Odin APK is on the pre-rebase bases | measured build = fork `5d5c382` + paraLLEl `1b3a294`. The rebase onto `f0d2d3c`/`3d72467` is clean and Mac-det-identical, but no Android build of it exists |
| The fix removes only the per-flush serialization | the 1st submit still GCs Granite's queue timeline (waits if the previous flush hasn't retired), and other Granite submits (present, frame contexts) keep the same wait. Only the driver fix removes all of them |
| Scratch 10 GB in `~/dev/ssx3-work/FS2` | 2.5 GB capture + 3 Mac det build dirs + APK; mini total 107.8 of 200 GB. Can go at close |

Budgets: 2 of 4 Android builds, 1 of 8 Odin launches (+1 aborted pre-install), ~2 h.
