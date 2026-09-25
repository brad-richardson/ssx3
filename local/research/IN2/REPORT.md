# IN2 — taps get lost at low guest speed: latch presses until the game reads them

Worker: muse. Fork branch `in2-latch` `43b61a4` from fork `ssx3` `0ed07c4` (no push).
Scratch: `~/dev/ssx3-work/IN2/` (2.9 GB: host-test + runner builds, run dirs).

## Result

Brad's lost taps were presses shorter than the guest pad-read interval: at
~0.1× a guest frame lasts ~150 ms wall while host input publishes every
~16 ms, so a tap lands between two guest reads and the edge-triggered menus
never see it. Fixed with a per-button latch: the render thread publishes
the vpad + raylib button union every host frame; port 0 consumes one
presented mask per guest read. A press shows until a read returns it
pressed and the host released; a release shows up for a read before a
re-press. Sticks bypass; the pad script applies on top, untouched.

Proof (one Mac CPU-backend binary, I26-FAST to the race, 93 injected
wall-clocked taps, `PS2X_PAD_READ_LOG=1`; taps fully between two
consecutive guest reads graded):

| Run | Qualifying taps | Seen exactly once | Dropped |
| --- | --- | --- | --- |
| `PS2X_PAD_LATCH=0` (pre-IN2 path) | 68 | 7 (all read ≤14 ms after release: stale-`liveMask` luck) | 61 |
| Latch on (default) | 56 | 56 | 0 |

Plus: taps whose in-window reads all missed (frame quantization) are still
caught by the next read 20/20 with the latch vs 2/15 without. Host suite
623/623/0 Release from the worktree root, incl. 11 new `Ps2PadLatch` runs.

## Guest read site and rate (brief Q1)

`scePadRead` (`Pad.cpp:1234`) → `readPadPortData` (`Pad.cpp:844`) →
`PSPadBackend::readState` (`ps2_pad.cpp:131`). The read log shows SSX 3
polls **both ports once per guest frame** (port-0 + port-1 reads per tick,
no tick read twice on one port): 2877 port-0 reads over 340 s off / 3468
on. Read gaps (port 0): off p50 64 ms / p90 223 ms / max 305 ms; on p50
136 ms / p90 160 ms / max 197 ms. Guest 0.80×→0.116× (off, tick 2904) and
0.89×→0.123× (on, tick 3492); CPU backend on a loaded mini.

Because the game reads both ports every frame, only port 0 consumes the
latch; other ports follow live without advancing it (`readState`).

## Before / after log lines (tap R3 [75000,75040], `key-lines-*.txt`)

Off (`DROPPED`, tick 1606–1608, nothing pressed the whole time):

```
[padread] read tick=1606 port=0 buttons=0xffff wall=74991ms
[padread] read tick=1607 port=0 buttons=0xffff wall=75184ms
[padread] read tick=1608 port=0 buttons=0xffff wall=75373ms
```

On (`SEEN-ONCE`, alongside the script's down hold — `0xffbf` vs `0xffbb`):

```
[padread] read tick=1743 port=0 buttons=0xffbf wall=74980ms
[padread] host +r3 wall=75007ms
[padread] host -r3 wall=75042ms
[padread] read tick=1744 port=0 buttons=0xffbb wall=75126ms
[padread] read tick=1745 port=0 buttons=0xffbf wall=75274ms
```

## What changed (fork `43b61a4`, 8 modified + 2 new, runner-dir diff empty)

| File | Change |
| --- | --- |
| NEW `ps2xRuntime/include/ps2_pad_latch.h` | `Latch` state machine (sticky press/release bits + shown state), mutex-guarded `SharedLatch` (render publishes, game consumes), shared `wallMs` epoch, `PS2X_PAD_LATCH` / `PS2X_PAD_READ_LOG` switches, host-edge log |
| `ps2_virtual_pad.h` | `PS2X_VPAD_TEST_TAP="ms:button:dur,..."` parser + windowing (wall clock, pad-script names); `kL3`/`kR3`; `liveMask` is now the latch-off channel |
| `runtime/ps2_pad.h`, `ps2_pad.cpp` | Raylib button selection/sampling extracted verbatim to `ps2xSampleRaylibPad()` (shared by sampler + off path); `readState`: latch consume (port 0) / live peek (others), else pre-IN2 direct sampling; sticks unchanged |
| `ps2_runtime.cpp` | Render loop publishes vpad+raylib+TEST_TAP union every host frame (`:3985`, plus raylib-only branches when the overlay hides/is off); off path keeps the old `liveMask` stores |
| `Kernel/Stubs/Pad.cpp` | `PS2X_PAD_READ_LOG=1` logs every guest read (tick, port, final buttons, wall ms); include only otherwise — script/stim/override untouched |
| `ps2xTest/` | NEW `ps2_pad_latch_tests.cpp` (11 runs) + registration; vpad union test moved to the latch-off path |

Design notes: two full taps between two reads coalesce to ONE press
(sticky bits, asserted + documented — replaying every tap would stack
stale presses; spam yields one menu step, not N). Latch adds ≤1 host frame
of input latency at full speed. `PS2X_PAD_LATCH`/`PS2X_PAD_READ_LOG` are
read per call (no cache), so the off path is testable in-process via
`setenv`. TEST_TAP needs the overlay shown (`PS2X_VIRTUAL_PAD=1`, no
gamepad in use); both proof runs log `overlay shown`.

## Exact commands and pins

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/IN2/PS2Recomp -b in2-latch 0ed07c4
cmake -S . -B ~/dev/ssx3-work/IN2/host-test -DPS2X_BUILD_STUDIO=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build ~/dev/ssx3-work/IN2/host-test --parallel 8 --target ps2x_tests
~/dev/ssx3-work/IN2/host-test/ps2xTest/ps2x_tests   # from the worktree root: 623/623/0
cmake -S . -B ~/dev/ssx3-work/IN2/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF
cmake --build ~/dev/ssx3-work/IN2/build --parallel 8 --target ps2EntryRunner
python3 in2_boot.py latch-off && python3 in2_boot.py latch-on   # slot 1, 340 s each, CPU backend
python3 in2_analyze.py run/latch-off; python3 in2_analyze.py run/latch-on
```

Pins: fork base `0ed07c4` + `43b61a4`; runner SHA
`3d1edfdf9c80f9f68d55806359f206ff602b9e2afa6df66cbcdb4801eb094ac0`
(same binary both runs, two matching reads); ISO/ELF = E32-inputs pins
(`3c2f8eb1…`, `1b49d05c…`, gated in the driver); codegen canonical
`~/dev/ssx3-work/codegen-ssx3`; I26-FAST route; taps R3 every 3 s 30–297 s
(40 ms) + cross at 282/292/302 s (60 ms). Full logs stay in scratch
(`run/*/boot.log`, `host-*.log`).

## Gaps and follow-ups

- **Orchestrator needs an Android compile check** (brief): touched
  `ps2_pad.cpp`, `ps2_runtime.cpp`, `Pad.cpp` all compile on Android. No
  new platform APIs (mutex/chrono/getenv only); Vita builds the same lib.
- Raylib gamepad/keyboard latch path is unit-tested (sampler helper +
  backend consume) but the proof boots only exercised the vpad publisher
  (no controller/keys on the mini); the iPhone field test (Brad's taps +
  any BT pad) is the real confirmation.
- 2/93 on-run taps logged a combined multi-bit edge (`+0x4004`: the
  282 s R3+cross overlap) — parsed as a disagreement artifact, verdicts
  fine (r3 SEEN-ONCE, cross SPANNING-seen).
- Off-run `SPANNING-MISSED?` (15) and on-run (20): in-window reads that
  all missed are frame quantization (read lands before the first frame
  publishing the tap); the latch recovers 20/20 on the next read.
- `liveMask()` remains for the off path and tests; a future lane could
  remove it if the kill switch ever goes.
- Recommended next action: fold `in2-latch` (`43b61a4`) and include it in
  the combined iPhone build (DK1 + I34); no device installs were done here.

## Orchestrator gate (2026-09-25)

**Pass.** Mechanism confirmed with a read log: taps between two guest reads were dropped 61/68 without
the latch, 0/56 with it; the pad script is untouched. `PS2X_PAD_LATCH=0` restores the old path.
Folds in F3; Brad's iPhone gets it in the F3 build.
