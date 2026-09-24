# AU3 report: guest-clock SND HLE and tag-1 host audio

Brief: `local/muse/prompts/AU3.md`. Worker: Codex. Source branch:
`au3-snd` in `~/dev/ssx3-work/AU3/PS2Recomp`, based on AU2 `7c2a02e`.

## Part 1 implementation

| Requirement | Result | Files / notes |
| --- | --- | --- |
| Dev-only HLE, default off | Implemented; enabled by `PS2X_SOUND=1`. | Replaced per-vblank `PS2X_SND_TICK` with a guest-cycle sound event. |
| Tick cadence | 93.75 Hz guest time; one event every 3,145,728 EE cycles. | `EeScheduler` starts the recurring event on cid-1 handler registration. It queues the type-0 handler call from the EE scheduler. |
| AU2 protocol details | Kept. | Status serial written at +0 and +0x23C; cid-1 type-2 completion answers retained. |
| Tag-1 PCM | Implemented. | Parser locates 1,536 bytes (384 stereo s16 frames) in SetDma tag buffer and pushes them to a bounded SPSC-style atomic ring. Overflow advances the oldest read position; underruns yield silence. |
| Host output | Implemented. | raylib `AudioStream`, 36 kHz stereo s16; falls back to 48 kHz with host-side linear interpolation if the 36 kHz stream is invalid. `PS2X_SOUND_WAV` records callback output up to 200,000,000 data bytes. |
| `_sceSifSendCmd` | Implemented unconditionally. | Decodes `a0..a6` as `(cid, mode, pkt, size, src, dst, esize)`; mode is ignored by this runtime. |
| Focused tests | Added three. | Guest-cycle cadence, tag-1 parser bytes, and seven-register binding. All three passed in the suite run. |

## Build and test gate

| Item | Result |
| --- | --- |
| Configure | Passed. Release/Ninja; codegen `~/dev/ssx3-work/codegen-ssx3`; dependencies reused from E50 `_deps`. |
| Build | Passed on second build invocation. The first build invocation failed compiling the new test because its suite registration function was missing; corrected once, then the incremental build completed and linked `ps2EntryRunner` and `ps2x_tests`. |
| Suite command | `~/dev/ssx3-work/AU3/build/ps2xTest/ps2x_tests` from fork worktree root. |
| Suite result | **599/600 passed, 1 failed.** All three `Ps2SoundHle` tests passed. The captured output was truncated before the failing test identity; failure not diagnosed. Per stop rule, no rerun or follow-up diagnosis was done. |
| Runner SHA ×2 | Not collected. |
| Runner-dir check | Not run. No push was attempted. |

## Validation not reached

The suite failure stopped the brief before boots. No leases or boots were
used. Boot A/B, title/menu/SC/race phase counters, semaphore 36 signals and
waits, race-start checks, WAV capture/conversion, and audio listen check are
not available. No `.m4a` was produced.

AU2 §AU2-4's lease incident was read before work resumed. No debugger was
attached to a harness child.

## Stop result

The remaining gate is the unidentified failing test in the 599/600 suite
result. This report and the current implementation are ready for the
orchestrator to inspect. No claim is made that race behavior or audible output
has been validated.

## Part 2 (continued worker)

Starting fork revision: `d2096ee` on local `au3-snd`. The Part 1 suite failure
was identified by the orchestrator as the unchanged P1ac SET_SREG handshake
test. Its call supplies the public six-argument ABI, while Part 1 decoded
every call as the private seven-register ABI. The source tree has separate
generated entries at `0x4261B0` and `0x426078`, but its existing external
codegen maps both to the same HLE function. The correction gives each entry
its own handler and binds `0x426078` at SSX3 override application. The
syscall-name list also gives a future recompile an exact private binding.

| Item | Result |
| --- | --- |
| ABI correction | Split public six-argument SendCmd from private seven-register `_sceSifSendCmd`; the SSX3 override binds 0x426078 to the private handler when using the existing codegen tree. |
| Tests | P1ac is unchanged and passes. Added an actual private-handler test with `a1=mode`, `a2=packet`. Part 1's three sound tests also pass. |
| Build | `nice -n 5 cmake --build ~/dev/ssx3-work/AU3/build --target ps2EntryRunner ps2x_tests -j 4` from the fork worktree, exit 0; full output `~/dev/ssx3-work/AU3/build-part2.log`. Recompiled 353 targets because the syscall list changed. |
| Full suite | `~/dev/ssx3-work/AU3/build/ps2xTest/ps2x_tests` from the fork worktree root; **601/601 passed, 0 failed**. Complete output: `receipts/suite-part2.log` (743 lines). |
| Runner SHA read 1 / read 2 | `4c3ffc07d4195ebea6a029f9bd971059b92925126b197126b7091f5d9bded6c9` / same. Runner: `~/dev/ssx3-work/AU3/build/ps2xRuntime/ps2EntryRunner`. |
| Runner-dir check | `git diff --stat 14b1e5cb au3-snd -- ps2xRuntime/src/runner` empty. No push. |
| Boot A | `zsh local/research/AU3/au3_boot.sh au3a 1 540`; E46 harness, I26-FAST vsync route, `PS2X_SKIP_MOVIE=1`, `PS2X_SOUND=1`, `PS2X_SOUND_WAV=~/dev/ssx3-work/AU3/run/au3-host-stream.wav`, slot 1; runner PID 64204; wall bound 540.376 s; runner rc -15 (SIGTERM), lease released. The 909-byte log stops during raylib/macOS service startup, before guest execution. No frame, park, SND log or WAV was created. `receipts/wrap-au3a.log`, `receipts/boot-au3a-1.log`, `receipts/au3a-result.json`. |
| Boot B | Not run: Boot A failed to initialize, so the brief's first-failure stop applies. |
| Title / menus / Select Character / race | Not observed. Race-start checks and matched-wall tick comparison unavailable. |
| Guest-cycle / wall tick rate; underruns / overflows per phase; sema 36 signals / waits | Not observed: no guest or audio stream started. |
| WAV / M4A | Not found / not found. Conversion and audio listen check unavailable. |
| Storage | AU3 work directory 1.7 GB after boot; internal ssx3 workstream usage 91.9 GB of 200 GB before boot; the boot made no material new output. |

Boot A's last lines are `Connection Invalid error for service
com.apple.hiservices-xpcservice` and `Failure on line 688 in function id
scheduleApplicationNotification(...)`. A window-service startup stall is an
inference from those lines and the absence of guest output; the precise cause
is unproven. The harness's `nice` request reported `setpriority: Operation not
permitted` and proceeded at normal priority. No debugger was attached, and no
other process was killed.

**Recommended next action for the orchestrator:** rerun the same pinned
runner and script in a Mac session where raylib can initialize its window,
then perform the A/B gate and WAV conversion. Do not infer audio or race
behavior from this boot.

Commit gate: after `git log -1` and `git diff --check`, the fork
`git add ... && git commit -m '[AU3] Preserve public and private SIF SendCmd ABIs'
-m 'Orchestrated-By: Codex'` command exited 128 before staging with
`fatal: Unable to create '/Users/brad/dev/PS2Recomp/.git/worktrees/PS2Recomp11/index.lock': Operation not permitted`.
Per the worker denial rule, no retry or alternate commit path was attempted.
The fork changes and this report/receipts remain uncommitted; no push was
attempted.

### Part 2 resume (Brad, 2026-09-23)

The prior commit denial and Boot A were caused by the Codex filesystem/process
sandbox. Brad approved escalation for fork git writes and runner boots. The
`au3a` attempt above is a **void sandboxed boot** and does not consume either
validation boot. The 601/601 suite and matching runner SHA remain the gate for
the resumed boots. The commands and receipts above are retained as the
diagnosis of the sandbox stall; the validation table will be appended below.
