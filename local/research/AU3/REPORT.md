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
