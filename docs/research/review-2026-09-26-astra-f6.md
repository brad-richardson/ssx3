# RV5 — F6 pre-release code review

**Recommendation: hold default-on Android Vulkan presentation for B1 and B2.** Both
allow the GPU to overwrite a buffer before the compositor has released it. The
successful short Odin runs do not exercise those failure paths. S1 also needs a
lifetime fix before sustained lifecycle testing. I found no new functional defect
in VR2 stage 1, HP1's final diff, or in SS1/SS2 with save/load knobs unset. Save-state correctness has
additional holes (S2–S5); these do not block a build that keeps save/load disabled.
HP1's two commits arrived during the final revision check and were also reviewed.

Source review only: no builds, tests, boots, device operations, or source edits.
Failure scenarios below are deductions from source, not reproduced device failures.
Existing reports supply context, not proof that untested paths are safe.

## Revisions and location notation

Locations below are relative to these pinned trees, with `R/` meaning
`ps2xRuntime/` inside the indicated PS2Recomp tree.

| Prefix | Reviewed source |
| --- | --- |
| `V` | `~/dev/ssx3-work/VK1/PS2Recomp`, `cdc831692023c40e7027f3aa30f777aa6a43db98` (folded VK1); VK1 files equal the brief's `vk1-part2` tip `15275cddc375c9074ae5213b0ee842384aaaae56` |
| `S` | PS2Recomp `173b31f4884ea3abd05242629728ae3eb2980b87`, read from the clean HP1 worktree and pinned git objects; SS1/SS2 delta from `a3efbfe` |
| `U` | VR2 stage-1 delta `5474956..d4fc12e`; same VU code in `S`; stage 2 excluded |
| `P` | `~/dev/ssx3-work/parallel-gs-ssx3`, `464f263dc51829b4ec76d7c223a4c3c5696571cf` (CLUT accessor) |
| `PV` | `~/dev/ssx3-work/VK1/parallel-gs`, `1b3a2948cc55e74f975e42b79d08983f31c2dbb6` (CLUT accessor plus counters) |
| `G` | VK1's Granite, `166ba21a247a681903cc9d0bb6562fe50a554c85` |
| `H` | `~/dev/ssx3-work/HP1/PS2Recomp`, branch `hp1`, clean at `554fbd992b10af3f97033bc2ead38fafbcdf0cd2`; trace guard commit `da7c1a7cc00493ca7f8de682aadd0bbcc8873dea` |

The live `~/dev/PS2Recomp` checkout had advanced to `f949ff0` and no longer contained
the named savestate files; it is not the review target. No checkout was changed.
Reports read: `local/research/{VK1,SS1,SS2,VR2,HP1}/REPORT.md`, especially VK1 Part 2B
and its gaps, SS1's inventory/fold notes, SS2's map-order fix, and VR2's exactness table.

## Blockers

### B1 — A failed compositor release wait still leads to a GPU write

**Locations:** `V:R/src/lib/gs/ps2_gs_parallel_backend.cpp:1062`;
`V:R/src/lib/gs/ps2_present_vk_android.cpp:479`, `:485`, `:491`.

**Scenario:** a queued slot returns around the four-slot ring while its replacement
callback has not arrived, or its delivered release fence remains unsignaled for
100 ms. `waitReusable()` clears `pending` on callback timeout, removes the stored fd,
and closes it even on poll timeout/error. `presentVk()` discards the boolean result
and immediately records the next blit into that same AHardwareBuffer. SurfaceFlinger
or HWC can still be reading it: concurrent read/write, torn/corrupt presentation,
and undefined synchronization. A later callback can also mark the newly reused slot
free. `poll()` returning positive for `POLLNVAL`/`POLLERR` is accepted without checking
`revents`; an interrupted poll is treated as failure but the caller still proceeds.

Android explicitly requires release completion for **all** pending buffer references
before reuse; a timeout grants no ownership. See the
[NDK release-fence contract](https://developer.android.com/ndk/reference/group/native-activity#asurfacetransactionstats_getpreviousreleasefencefd).
This also defeats the advertised runtime fallback: successful `queue()` calls reset
the drop counter even if every release wait fails. `vk_release_timeouts` counts the
condition-variable timeout only, so fence-poll timeouts can leave that counter zero.

**Fix:** keep the slot unavailable, retain its fence, and propagate failure to the
caller. Drop the new frame/use another genuinely free slot, or detach and retire the
pool before switching to GL. Retry `EINTR` within one deadline and require a valid
signaled-fence result. Never convert a wait failure into permission to write. Count
callback and fence timeouts separately. Verify with delayed callbacks, an unsignaled
fence, and `EINTR`, asserting that no blit is submitted to the held slot.

### B2 — Window replacement bypasses release, and old callbacks mutate new use

**Locations:** `V:R/src/lib/gs/ps2_present_vk_android.cpp:334`, `:395`, `:135`, `:170`;
slot retirement at `:451`; `V:R/src/lib/gs/ps2_gs_parallel_backend.cpp:946`.

**Scenario A:** `TERM_WINDOW` reparents the child to null with an asynchronous
transaction and no completion callback. On the next window, `setHostWindow()` clears
all `pending` flags and closes every release fd immediately. The existing Vulkan
pool is retained when the scanout dimensions match. A quick recreate/resume can
therefore write a slot before the old layer's last use has completed, independently
of B1. The comment claiming detached buffers are never released is not a safe basis
for reuse: Android documents release completion for a transaction removing a surface
from the tree, including any fence that must still signal.

**Scenario B:** an outstanding old-layer transaction carries only `SC*` and raw
`AHardwareBuffer*`. After the same buffer is queued on the new layer, its old callback
writes `s.bufs[prev].pending = false` and replaces the fd for the **new** use. The mutex
prevents a C++ data race but cannot distinguish the two uses. Size-change/fallback
retirement has a related problem: `releaseBuffer()` erases the record, yet a late
callback's `operator[]` recreates it, retaining stale metadata/fds and allowing an
address-reuse collision. Merely honoring B1's return value does not repair this.

**Fix:** track buffer submissions by allocation identity, layer generation, and
submission sequence (or retain a refcounted retired pool). Register completion for
the detach transaction so the final displayed buffer has a release path. Do not clear
ownership on window change; retire old slots until their callbacks/fences finish.
Callbacks must resolve their own submission and close stale fds without inserting or
altering current slot records. Test same-pointer `TERM/INIT_WINDOW`, delayed old-layer
callbacks, and resolution changes with callbacks outstanding.

## Should-fix

### S1 — Every retired SurfaceControl is leaked

**Locations:** `V:R/src/lib/gs/ps2_present_vk_android.cpp:105`, `:343`, `:413`;
`Api::release` at `:41`/`:71` has no call site.

Each background/window-replacement cycle creates another child and moves the old
handle into `graveyard`. Nothing drains that vector or calls `ASurfaceControl_release`;
there is no sink shutdown path either. Fallback also retires its child permanently.
Repeated activity lifecycle changes therefore accumulate client handles and associated
resources for the lifetime of the process. Keeping handles alive for callbacks is
necessary; keeping every handle forever is not. The
[NDK ownership contract](https://developer.android.com/ndk/reference/group/native-activity#asurfacecontrol_createfromwindow)
requires releasing the reference returned by creation.

**Fix:** retire a layer with outstanding-callback accounting, then release it when no
callback can name it; close remaining owned fds as part of retirement. Coordinate this
with B2 rather than immediately releasing raw pointers still held by callbacks. Verify
bounded live-layer, fd, and buffer-record counts over repeated recreate cycles.

### S2 — CLUT bytes are restored, but the active GSInterface palette index is not

**Locations:** `P:gs/gs_interface.cpp:4416`, `P:gs/gs_renderer.cpp:5278`;
consumers `P:gs/gs_interface.cpp:688`, `:1304`; fields `P:gs/gs_interface.hpp:372`;
load call `S:R/src/lib/gs/ps2_gs_parallel_backend.cpp:602`.

**Scenario:** save after a palette upload and flush with current CLUT instance `k != 0`
and no pending palette uploads. Restore into a fresh interface, then draw a paletted
primitive without reloading its CLUT (e.g. CLD=0). `write_clut_state()` restores the ring
and the renderer's `base_clut_instance`/`next_clut_instance` only. The interface's
`render_pass.clut_instance` and `latest_clut_instance` remain zero. Texture descriptors
select bank zero instead of `k`; a subsequent partial palette update also takes its
incoming palette from zero. A later flush can rewind the restored renderer cursors to
that wrong interface index (`gs_interface.cpp:312`). `clobber_register_state()` at
`:4276` marks registers dirty and rebuilds handlers; it does not restore those indices.

**Fix:** capture/restore the interface's active palette state along with the renderer
ring, or reconstruct it from a documented flush invariant and set both interface
indices explicitly. Invalidate related memoization. Add a save/load continuation that
uses CLD=0 immediately after loading, and one that updates only part of the palette.
This is an additional omission beyond SS1's documented vertex/transfer gap; screenshots
many ticks after loading can miss it after a full guest palette reload.

### S3 — The save readiness gate accepts partial GS input it cannot restore

**Locations:** `S:R/src/lib/gs/ps2_gs_parallel_backend.cpp:548`, `:521`;
`S:R/src/lib/ps2_savestate.cpp:1068`;
`P:gs/gs_interface.hpp:337`, `:600`; `P:gs/gs_interface.cpp:4267`, `:3968`, `:2872`.

**Scenario:** the guest completes one DMA packet containing TRXDIR plus the first part
of an IMAGE upload, then yields across the requested save tick before sending the
remaining packet. Host queues can be drained while paraLLEl still has an active
host-to-local transfer. `SavestateIdle()` tests only local-to-host pending bytes and
palette uploads. `flush()` deliberately keeps the transfer alive via
`flush_pending_transfer(true)`. The save omits its payload/cursor/active flag; after
load, `a_d_HWREG_multi()` ignores continuation data because `host_to_local_active` is
false. VRAM diverges with no load refusal. Similarly, a strip/fan spanning the save
boundary loses paraLLEl's retained vertices; saving the separate frontend vertex queue
does not repair a backend receiving raw GIF packets.

**Fix:** serialize the backend transfer and vertex state, or expose an actual safe
checkpoint predicate that refuses/defer saves with uncaptured state. A vsync tick and
empty host work queue do not establish that predicate. Add continuations splitting an
IMAGE upload and a strip/fan across a save point. This promotes SS1's acknowledged
assumption into a concrete correctness restriction; no claim that the reported race
save happened to hit it.

### S4 — Memory-card restore loses directories and guest-visible timestamps

**Locations:** `S:R/src/lib/ps2_savestate.cpp:312`, `:338`, especially `:322` and `:377`;
`S:R/src/lib/Kernel/Stubs/MemoryCard.cpp:823`, `:1042`, `:1616`.

**Scenario:** save after `sceMcMkdir("/SAVE")` but before opening its first file. The
serializer stores only regular files, so `/SAVE` is absent after loading into an empty
card root. The guest's next `sceMcOpen("/SAVE/data", O_CREAT)` now fails because its
parent directory does not exist. The reverse case also fails silently: an extra empty
directory already in the destination is ignored by the compatibility check and remains
visible to `sceMcGetDir`. Even regular files are opened with truncation and rewritten
on every restore, including identical files; their original `last_write_time` is not
saved, while `sceMcGetDir` explicitly returns that time to guest RAM.

**Fix:** version the card section to include directories and the metadata exposed to
the guest, validate the entire destination tree, and preserve timestamps on restore.
Propagate directory traversal/read errors instead of silently saving a partial tree.
Test an empty directory followed by file creation and a directory-table read after
restore. Deterministic treatment of the separate `.`/`..` wall-clock timestamps also
needs a stated policy; copying file bytes alone cannot make card operations exact.

### S5 — Android strict runner identity hashes the launcher, not the game library

**Locations:** `S:R/src/lib/ps2_savestate.cpp:224`, `:395`, `:601`.

On Android, `runnerPath()` follows `/proc/self/exe`; the NativeActivity runtime lives in
`libps2EntryRunner.so`, while the executable is the system app-process launcher. Save
with APK A, then load with changed APK B on the same OS: `runner_sha` can still match,
including under `PS2X_SAVESTATE_STRICT=1`. This defeats the advertised strict binary
check and can accept behaviorally incompatible runtime code with unchanged section
versions. SS1's fold report already identifies this gap; it is still present here.

**Fix:** identify/hash the loaded runtime library using an address and `dladdr`, or use
a build identity embedded in that library; fail strict mode if identity cannot be
obtained. Verify that different runtime libraries on the same Android system fail
strict identity matching. Keep device save/load disabled until addressed.

## Areas checked, no additional issue found

### Vulkan ownership, synchronization, fallback, and EGL

- AHB import uses dedicated allocation, queried allocation size/type bits, and a
  four-slot pool. Partial setup failure is unwound through `destroyVkSlots()`;
  `G:vulkan/device.cpp:2271` confirms `wrap_image()` disowns the image, so resetting
  the wrapper followed by explicit `vkDestroyImage` is not a double destruction.
  GPU work is drained before freeing imports. Releasing the application's AHB ref
  does not itself invalidate SurfaceFlinger's separately held ref. B2 concerns the
  application's bookkeeping/reuse, not an invented immediate AHB use-after-free.
- Rewriting the entire destination from `UNDEFINED` can discard the old contents;
  omitting a content-preserving acquire is not independently a finding. The Vulkan
  [ownership-transfer rules](https://registry.khronos.org/vulkan/specs/latest-ratified/pdf/vkspec.pdf)
  allow skipping ownership transfer when old contents need not survive, provided
  dependencies are satisfied. The graphics-to-foreign release transitions to GENERAL,
  and CPU GPU-fence completion precedes `setBuffer(..., -1)`. B1/B2 break the separate
  compositor-to-producer execution dependency; discarding contents cannot replace it.
- On the normal callback path, the stats array is released, the caller owns the
  returned fd, and the fd is closed by wait/retirement. No normal-path double-close
  found under the sink mutex. Stale callback records and early closes are B1/B2.
- `TERM_WINDOW` is hooked before raylib destroys EGL state, clears the stored window
  pointer, and bumps a generation. This correctly detects same-pointer window reuse.
  The three-swap warmup resets per generation. The ownership reset that follows is
  still defective. Sink fields are mutex-protected and global flags are atomic;
  backend slots are used on GsWorker through the synchronous latch RPC.
- Missing API symbols/extensions and slot-creation failure disable the Vulkan path;
  source-image transitions have not occurred when setup falls back to readback.
  The missing-child drop threshold also disables it. Release failures are not covered.
- The EGL patch requests eight alpha bits and refuses an unknown unpatched raylib
  source hash. Android-only CMake routing, RGBA selection before `InitWindow`,
  premultiplied separate pad blending, and the scissored transparent game rectangle
  are consistent. Skipping GL still polls input/lifecycle. Non-Android presentation
  calls are preprocessor-guarded. The already-patched check checks text, not the whole
  resulting hash; this is a reproducibility limitation, not a demonstrated device bug.
- Existing documented limitations remain: GL fallback has the smaller bordered canvas;
  fallback after RGBA setup has imperfect pad alpha. GPU fence waits are unbounded in
  Granite, as in the pre-existing readback path; automatic fallback is not recovery
  from a hung/lost Vulkan device. No new bounded device-loss recovery was demonstrated.
- `PV` counters use atomics; additions do not change submit order. They do add steady
  clock calls/atomic operations even with diagnostic compile knobs off. Their frame
  context default remains four. No new speed claim is made in this review.

### Save states with all knobs unset

- `S:R/src/lib/ps2_savestate.cpp:37` uses function-local registries. Per-TU Support
  registrars (`Helpers/Support.h:1967`) install callbacks without invoking serializers
  or touching cards/GS/audio. Their TU-derived keys distinguish header-local globals;
  explicit syscall linkage at `Kernel/Syscalls/Savestate.cpp:112` prevents dead stripping.
  Static registry/string/map allocation and startup cost do exist; this is not a
  zero-overhead compile-in, but no static-init guest-state mutation was found.
- `Kernel/EeScheduler.cpp:562` reads cached config once per `run()`, and performs one
  resume-skip atomic exchange. The loop adds skip/save conditionals; unset knobs keep
  `processPendingEvents()` in the previous order and never enter serialization.
  `PS2Runtime::loadELF` stores the ELF path; hashing and card I/O are save/load-only.
  `rand`/`srand` gain an atomic used-state store, and wait transitions copy completion
  tags even when saves are off. These are actual residual costs, not measured here.
- The CD continuation factory rebuilds captured guest addresses against the fresh
  runtime, instead of serializing host pointers. Untagged closures/open file handles
  defer saves. Pad frame-counter relocation preserves its increment behavior.
  SND serialization holds its mutex; VU decode/recomp caches are invalidated on load.
- SS2 retains saved keys **before** moving entries, checks nonempty-map bucket shape
  and order, and bounds counts. Its empty-map rule addresses the documented same-STL
  Linux refusal. Cross-STL refusal remains intentional, not a portability promise.
- Section preflight checks framing/presence/version before application; it is not a
  transactional validation of every payload. Later payload/load errors can leave a
  partly restored machine; current `run()` refuses to execute it. Do not reuse this
  loader as an in-process resume API without stronger rollback. Existing IOP-module,
  live MPEG, SSAA-history, and cross-host/path restrictions remain outside exactness
  claims. S2–S4 show why a matching EE hash alone cannot certify a full-machine load.

### VR2 stage 1: exactness arguments independently checked

- **Lever 2, budget:** `U:R/src/lib/vu/ps2_vu1_step_impl.h:252` stalls no farther than
  `budgetEnd`, then returns before executing an upper/lower operation when at the
  boundary. A generated tail dispatch at an exhausted budget therefore performs no
  guest instruction. Reserved pairs have null table entries (`ps2_vu1_recomp.cpp:191`),
  so falling back at the boundary does not report an extra reserved instruction.
- **Lever 2, commits/PC:** every completed pair calls `advanceOneCycle()` (`:491`),
  which commits due writes before XGKICK progress (`:217`). No intervening new pipeline
  write requires the removed loop-header commit. Generated lookup requires VU1 and
  exactly 0x4000 bytes (`ps2_vu1_recomp.cpp:93`); first entry is aligned/bounds-checked
  by `run()`. Sequential wrap and immediate/VI branch targets remain aligned and in
  range. The constant mask equals VU1's old mask. VU0 and short images still interpret.
- **Lever 3, flags:** map eligibility is set after stalls; upper FMAC/CLIP evaluates
  `directFlagsNow()` before the lower operation can queue FSSET. No queue mutation
  between the old check location and that upper write changes its answer. Pairs with
  no flag write avoid the scan; queued FSSET still prevents direct flag updates.
- **Lever 3, pending-until:** decoder VF writes have latency four; direct VI writes
  are restricted to at most one, ACC forwarding/stores to one, FMAC/CLIP to four.
  FDIV/EFU's longer latencies remain queued and do not call `noteDirect()`. With
  monotonic `m_cycle`, the new `m_cycle + 4` store cannot shorten an earlier direct
  landing. Shorter-latency calls still take the max. Reset clears the pending deadline.
  SS1 continues to save that value and pair-local flags are reset before return.
- Trace-armed runs are sent to the interpreter before generated dispatch; the pair
  trace removal cannot suppress an already armed E36/E37 stream. The differential
  test really selects generated fixtures versus the queued interpreter and compares
  VU state/data at cut, resume, and fresh execute. Its mix does **not** establish full
  coverage of XGKICK, EFU/WAITP, MFP, JR/JALR, or I-bit programs. No stage-1 defect was
  found in the corresponding source paths; targeted additions would strengthen the
  regression suite. Stage-2 liveness conclusions are not part of this review.

### HP1 final diff: no issue found

`H:R/src/lib/ps2_vif1_interpreter.cpp:562`, `:747`, `:1134` now guard the three
formatting blocks with `ps2_vu1_entry_trace::enabled()`. `e37AppendVif()` already
returns immediately when disabled (`:32`), so this removes formatting for a no-op
call. `noteMscalEntry()` stays outside the new guard, and VIF memory writes and `pos`
advancement remain unconditional. `enabled()` performs the same lazy initialization
that the old helper call performed. No trace-on ordering change found.

`H:android/app/build.gradle:21` changes only `minSdk 28` to `29`; no contradictory
`ANDROID_PLATFORM`/`android-28` setting was found under `android/`. This raises the
install floor intentionally; it does not change iOS code. Final Android compiler
target and linked-library TLS behavior still require the build check. The HP1 report
at review time describes the earlier worker permission denial and is stale relative
to these two source commits; no build/test success is inferred from it.

## Review limits

No standalone cosmetic nits were promoted into findings. Device/driver validation,
final APK/iOS linkage, and the full combined F6 binary remain
unverified here. In particular, the existing Vulkan pixel comparisons test import
layout/normal rendering, not delayed releases; existing save-state frame samples do
not test the first CLD=0 draw, split transfers, or nonempty memory cards.
