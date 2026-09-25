# PF1 (post-race lane; report = POSTRACE-REPORT.md, not the older REPORT.md) notebook — post-race jump to 0x6c058000 (Opus exploratory, Mac mini)

Start 2026-09-25 13:02 EDT; time box to 16:02.

## 13:02–13:20 setup + first read

- FR1 R1 missing-target line (`~/dev/ssx3-work/FR1/run/r1-full/boot.log:60049`): `JALR source=0x39e724
  target=0x6c058000`, s0 = node `0x5aa300`, s1 = container `0x5ae940`, **v0 = [node+0x48] = 0x42640000
  (= 57.0f)**, so the "vtable pointer" slot holds a float. node[0]=0x5aa100, node[4]=0x5aa500
  (0x200-byte stride neighbours).
- `sub_0039E6B8` (ee-func): `first = func_397840(s1+0x24)`; loop: if `[node+0x54]` bit 6 then call
  `(*(node+0x48))[0x8C](node+0x40 + (short)[vt+0x88])`; `node = node->next ([+4])`; stop when
  `func_397718(node)` (sentinel test). So node = 0x40-byte link header + embedded object at +0x40
  whose vptr sits at object+8 (gcc2 vtable: 8-byte entries {short delta, short, fnptr}).
  0x39e6b8 is itself a vtable slot in ~90 rodata vtables (0x467e94…0x494744) + 8 direct jal callers:
  a generic "container: call child virtual 0x8C on every active child".
- Runners: A0 = F3 `ec2dbf1` release (`F3/bin/runner-clean-rd1` d94753b4…) = the brief's repro;
  B1 = RD1 `ps2EntryRunner-probe4` (0ed07c4 + RD1 probe commit 1f3180d, diag taps OFF; release
  WRITE* macros still call `ps2DiagWatchReport`), same guest code as FR1 → FR1's addresses hold under
  PS2X_DETERMINISTIC=1. B1 watches 0x5aa300 (links), 0x5aa348 (+0x48/+0x4c), 0x5aa350 (+0x50/+0x54),
  0x5ae964 (list head) with `PS2X_RD1_WATCH_REGS=1`.

## 13:10–13:20 static decode while B1/B2 run

- List primitives (ee-at): list = {H at +0 (H.prev = H, H.next = first), T at +0xc (T.prev = last,
  T.next = T)}. `0x3978f0` = insert after H, `0x397910` = append before T (does not fix
  next->prev), `0x397840(list)` = first or 0, `0x397718(node)` = 1 if node is a sentinel
  (next == node || prev == node).
- Walker `sub_0039E6B8` = vtable slot +0x78 in ~90 vtables (e.g. 0x467e18, 0x4946c8); its list is
  H = s1+0x24 (= 0x5ae964), T = 0x5ae970. Children must have an embedded object at +0x40 with its
  vptr at +0x48.
- Node 0x5aa300 is a UI element object: vptr at +8 (menu: `0x494bd8`, ctor `sub_0039FB30`; crash:
  `0x4949e8`), links at +0/+4, **+0x48 is a float** animated by base slot +0x60 `sub_003A0048`
  (0x3a0080/0x3a01a8 writes 39.0f…57.0f). So it can never be a legitimate walker child.
- UI screen loader `sub_0039CED0` appends each element to **screen+0xb4** (`addiu a0,s1,0xb4` →
  `jal 0x397910`), element array at screen+0x3c, layout at screen+0x38.
- Crash chain: 0x5aa300 → next 0x5aa500 → next **0x5ae9c0 = T of list 0x5ae9b4 = screen 0x5ae900
  +0xb4**. The walker's s1 = 0x5ae940 = 0x5ae900 + 0x40. So the walker (list at s1+0x24 =
  screen+0x64) is walking nodes that belong to screen 0x5ae900's element list (+0xb4).
- Crash thread sp = 0x1ff7a80, not the menu-time main thread (sp 0x1fffd70–0x1ffff20).
- A0 (F3 repro with frame dumps) and B1/B2 first launches were too slow (7–10 vsync/s under
  another lane's build load; the frame dump PNG-encodes every present) to reach tick 20063 inside
  1,800 s. Stopped them (`run/*-aborted`); relaunched B1 and B2 with `--no-frames`.

## 13:12–13:25 thread angle → EE time slice

- B2 menu-time hits: `0x5ae900` is built by the same UI-element ctor `sub_0039FB30` (tick 601), so the
  walker's `this` (0x5ae940) is **the middle of a UI element**, not an object with a list at +0x24.
- FR1's missing-target `trace=` ring (targets dispatched through the function table) just before the
  jump: `… sub_003C7080 → FlushCache (0x424020) → syscall 0x77 (0x424160) → 0x3b5880 (sub_003B55F0
  +0x290) → sub_003C33E0 → GetThreadId → SignalSema → WaitSema → 0x397718 → 0x39e738`: the walker's
  thread did SIF work + mutex traffic inside a child call, then resumed in the walker loop.
- `sub_003C3380` / `sub_003C33E0` = recursive mutex lock/unlock (owner tid `0x50c814`, count
  `0x50c818`, sema id `0x50c810`), reached through the pointer table at `0x44c46c` (0x3b5860/0x3b5880).
- **Runtime model difference:** `EeScheduler::checkpointDue` (`EeScheduler.cpp`, upstream `f4309cd`)
  preempts the running thread when its 65,536-cycle slice expires and *any* thread is Ready at the
  **same or higher** priority (`hasReadyAtOrAbovePriority(prio)`), re-queuing it at the back: an
  equal-priority round-robin. The EE kernel never time-slices; equal priorities switch only on
  block / RotateThreadReadyQueue (upstream's own test "RotateThreadReadyQueue is the only
  same-priority rotation" encodes that, but never burns a slice). Prediction: a thread walking a UI
  list can be preempted mid-walk by an equal-priority thread that frees/rebuilds the screen — a PS2
  never does that.
- Candidate (pf1-postrace, uncommitted yet): slice expiry preempts only for a strictly higher
  priority; `PS2X_EE_TIME_SLICE=1` = legacy for A/B; `PS2X_SCHED_SLICE_LOG=<tick>` logs each
  slice preemption. Unit test "PF1: slice expiry never preempts for an equal-priority ready thread".
- Discriminator: legacy + slice log on the F3 tip should show a slice preemption of the crashing
  thread (sp ≈ 0x1ff7a80) shortly before the jump; the fixed build should idle on the results screen
  past tick 20063 + 2 min with no missing target.

## 13:25–13:35 host contention; boots re-planned

- Mini at load 40–50: three builds (VB1 -j12, HR1 -j8, PF1 -j6 niced), an F4 runner, oMLX, on
  6 P-cores. B2 got ~0.6 core (≈8 vsync/s) and could not reach tick 20063 inside 1,800 s: stopped at
  tick 8580 (`run/B2-ram-stopped`; its menu-time watch data is what the 13:12 entry used). B1 stopped
  at ~7200 (`run/B1-watch-aborted`, second launch).
- Added `PS2X_MISSING_DUMP=<prefix>` (RDRAM + 64 stack words + thread at the first missing target) to
  pf1-postrace so the control boot captures the crash state itself; RD1's tick-based RAM dump isn't
  needed.
- Plan once the build lands: C1 = legacy slicing (`PS2X_EE_TIME_SLICE=1`) + slice log from tick
  19500 + missing dump (control: should reproduce the jump on the F3 tip); C0 = fixed default,
  frames at ticks 17800/20100/26000 via `PS2X_FRAME_DUMP_ONCE_TICKS`.

## 13:27–13:35 build, suite, C boots

- Build (`~/dev/ssx3-work/PF1/build`, Release, diag taps OFF, TEST ON, paraLLEl 19d93b2 copy, codegen
  8ea8ed43…): rc=0. Runner `bin/runner-pf1` sha256 `811c7928…d747` (two reads).
- Suite from the worktree root: **643/643** default; **642/643** with `PS2X_EE_TIME_SLICE=1` — only
  "PF1: slice expiry never preempts for an equal-priority ready thread" fails (red = legacy rule).
- Fork commits on `pf1-postrace` (from `ec2dbf1`, local): `9c98713` fix + test, `a1eb9b9` dump knob.
  Runner-dir check empty.
- C1-legacy (control, `PS2X_EE_TIME_SLICE=1`) and C0-fix launched 13:28 on slots 1/2, same route/env
  as FR1 (+ `PS2X_UNPACED=1`, slice log from 19000, missing dump, frames 17800/19000|20100/20000|27000).
  Both ~13 vsync/s at load 24.

## 13:44–13:58 C1 reproduces; the mechanism is NOT the time slice — PAUSED (Brad needs the mini)

- C0-fix stopped at tick 10992 to give C1 headroom (`run/C0-fix-stopped`); relaunch waited for a lease
  (VB1 speed hold on slots 2–4) and was killed at the pause without booting (`run/C0-fix-neverbooted`).
- **C1-legacy (F3 tip `ec2dbf1` + PF1 commits, `PS2X_EE_TIME_SLICE=1`) reproduced the jump**: tick
  18823, wall ~1370 s, rc −6, `JALR source=0x39e724 target=0x0`, s1 = 0x5a7b40, s0 = 0x5a9d00
  (`run/C1-legacy/boot.log:1157`, RAM image `run/C1-legacy/crash.ram`, stack at `:1158`). Different
  addresses from FR1, same shape. No `[sched:slice]` lines (crash came before the log's tick 19000).
- Crash-RAM walk (`pf1_lists.py`): parent walker `this=0x5bef00` list 0x5bef24 = {0x5a8000,
  0x5a7b00}, both container nodes (vptr 0x494670) that embed a UI element at +0x40 (vptr 0x4949e8,
  self-linked) and own an element list at +0xb4. List 0x5a7bb4 = 0x5a3500, 0x5a4b00, 0x5a8300,
  0x5a9b00, 0x5a9d00 (all class 0x4949e8, float at +0x48).
- Stack at sp 0x1ff7a80: +0 ra 0x39e72c, +0x10 s1 0x5bef00, +0x20 s0 0x5a7b00 = **the frame of
  `0x398868`** (element child walker, list at this+0x74; interior entry of merged `sub_00398798`)
  called from the walker's jalr at 0x39e724; parent frame at +0x40 has ra 0x20e8f0 (`sub_0020E8E0`).
- Registers at the crash are `0x398868`'s (this = 0x5a7b40, node s0 = [0x5a9b00+4] = 0x5a9d00) but
  execution is in `0x39e6b8` at 0x39e72c→0x39e738: the walker continued after its jalr while
  `0x398868` was suspended, and its epilogue (restore s0/s1) never ran. Trace tail:
  `… 0x384dc0 → 0x397718 → 0x397718 → 0x3e4db8 (timer-1 INTC handler) → 0x397718 → 0x39e738`.
- **Mechanism (runtime bug, PS2Recomp `ps2_runtime.cpp` `PS2Runtime::dispatchGuestBranch`):** after
  running a callee on the host, the caller's continuation test is
  `if (ctx->pc == entryPc) ctx->pc = fallthroughPc; return ctx->pc == fallthroughPc;`.
  `0x398868` recurses: a UI element's slot +0x88 is `0x398868` again (jalr 0x3988d4). When a
  checkpoint (here the timer-1 interrupt deadline) fires **in dispatchGuestBranch at that recursive
  call**, it returns false with `ctx->pc = targetPc = 0x398868`; the outer `0x398868` returns early;
  the walker's jalr dispatch (target 0x398868, so entryPc = 0x398868) sees `ctx->pc == entryPc`,
  takes it as a normal return, rewrites pc to 0x39e72c and returns **true**, so the walker runs on
  with the suspended callee's registers. Same ambiguity for a backward-edge `eeCheckpointDue()`
  whose loop head is the callee's entry, and a self tail-jump. A PS2 takes the interrupt and returns
  to the same instruction — so this is ours, not the game's.
- **The time-slice commit `9c98713` is not this mechanism** (the trigger was the interrupt deadline;
  the equal-priority slice is still a kernel-model difference, but unproven as a cause of anything).
  Keep or drop it at the orchestrator's call; don't fold it as the PF1 fix.

## Resume plan (next session)

1. Fix candidate (one mechanism): `EeScheduler::checkpointDue` returning true sets an
   "unwind pending" flag; `dispatchGuestBranch`'s post-call check returns false while it is set
   (before the entryPc heuristic); the scheduler run loop clears it right before each top-level
   `function(m_rdram, &context, &m_runtime)` (EeScheduler.cpp ≈ line 935; the loop's own
   `checkpointDue` at ≈925 is top level). Callers: `ps2_runtime.cpp:2520` (dispatch),
   `:3661` (`eeCheckpointDue`, backward edges via `control_flow_emitter.cpp:180`), scheduler ≈925.
   Returning false after a genuine return is safe (ctx->pc = fallthrough is a resume entry).
2. Unit test: a guest function A that calls itself (entry X) where the checkpoint fires at the nested
   dispatch; assert the outer caller does not continue (trace), and that it resumes correctly.
   Suite red→green from the worktree root.
3. Validation boot: FR1-R1 route, fixed build, default slicing (drop `PS2X_EE_TIME_SLICE` from the
   picture or revert 9c98713 first), `PS2X_MISSING_DUMP`, frames 17800/20100/27000. Needs a quiet
   mini: at load ≤ 10 the route reaches the results screen in ~1,300 s; at load 40–50 no boot
   reached tick 20063 inside 1,800 s. Idling 2 min past the crash tick likely needs > 1,800 s wall
   (ask the orchestrator for more wall or a quiet window).

## Resumed 15:14 (active time so far 56 min)

- Reverted the slice commit: `f287b62` (revert of 9c98713; history kept).
- Fix `3c037ab` `[PF1] Checkpoint unwinds propagate past a callee suspended at its own entry`: new
  `ps2xRuntime/include/runtime/ee_guest_unwind.h` (thread_local flag, included only by
  `ps2_runtime.cpp` and `EeScheduler.cpp`, so no codegen rebuild); `dispatchGuestBranch` checkpoint
  path and `eeCheckpointDue()` mark it, the post-call check returns false while marked (before the
  `ctx->pc == entryPc` heuristic), the scheduler clears it before each top-level dispatch. Generated
  backward edges always `return` after a true `eeCheckpointDue()` (`control_flow_emitter.cpp:180`).
- Test "PF1: a checkpoint at a recursive call is an unwind, not a return" (outer → F → F with an
  ExternalWake posted so the nested dispatch checkpoints): expected trace {1,10,11,12,3}.
  Suite from the worktree root: green **643/643** (`suite-green2.log`, `suite-green3.log` on the final
  binary); red with the check disabled **642/643**, only the PF1 test fails (`suite-red2.log`).
  Runner-dir check empty.
- Runner `bin/runner-pf1-fix` sha256 `364cb0c1…d264` (two reads) = `3c037ab`.
- V1 validation boot queued 15:18 (HR1 speed hold on all four slots). Pre-fix control = C1 (same
  env: C1's `PS2X_EE_TIME_SLICE=1` is the default again after the revert).

## 15:20–15:53 validation

- V0 (control repeat, `runner-pf1` + `PS2X_EE_TIME_SLICE=1`): crash at vsync 18823, **crash line
  and 32 MB crash RAM byte-identical to C1**.
- V1 (fix `3c037ab`): wall cap 1,801 s at **tick 33450, zero missing targets**; frames 20100 and
  33450 show the live results screen (Mac 03:15 / Zoe 04:01). The t17800 frame hash `4a8a7b45` is
  identical across V1/C1/V0.
- No leases held at close. Report: `POSTRACE-REPORT.md`.
