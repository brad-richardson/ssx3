# IN2 — taps get lost at low guest speed: latch presses until the game reads them (muse, 2 h)

## Facts
- Brad (09-25, iPhone, paraLLEl build, race ~0.1×): "button inputs aren't consistently listened to… I have to spam tap the X button… it can still take a few seconds to make it through the race menus."
- At ~0.1× a guest frame lasts ~150 ms wall. The game polls the pad once per guest frame (pad RPC / `Pad.cpp` read path; confirm where the guest reads pad state and how often, file:line). A touch tap shorter than one guest frame can press and release between two reads and never be seen; menus usually need a press *edge* (up on one read, down on the next).
- Input sources: virtual pad (`ps2xRuntime/include/ps2_virtual_pad.h`, `ps2_pad.cpp:141-171`, touch glue `ps2_runtime.cpp` `virtualPadTouches`, iOS `ps2_ios_runtime.mm:188` `touchPoints`), gamepad/keyboard via raylib (`ps2_pad.cpp`), pad script (`PS2X_PAD_SCRIPT`, must stay exactly as is: tests rely on it).

## Hypothesis → observable
H: presses shorter than the guest read interval are dropped. Observable: a default-off log (`PS2X_PAD_READ_LOG=1`) of guest pad reads (tick, buttons seen) and host press/release events (wall time, button); at low speed, host presses with no read seeing them. Confirm on the Simulator or Mac with an injected short tap (a dev-only env like `PS2X_VPAD_TEST_TAP="<ms_after_start>:<button>:<duration_ms>"` or the existing `PS2X_VPAD_TEST_TOUCHES`), run under load or with a slowed guest so a 60 ms tap spans no read.

## Fix (one mechanism)
A per-button latch between host input and the guest's pad read: a host press sets `pendingDown`; the button reads as pressed until at least one guest read has returned it pressed **and** the host has released it; a release reads as up for at least one guest read before a new press can show. Apply to virtual pad + gamepad/keyboard; **not** to the pad script. Analog sticks unaffected. Unit tests with a fake read clock: a 1-ms tap between two reads is seen exactly once; a held button is continuous; two quick taps between reads become two presses (or document if it's one, and why).

## Steps
Fork branch `in2-latch` from fork `ssx3` `0ed07c4`. Code + tests; suite from the worktree root; one Mac or Simulator run proving the injected short tap is now seen (log lines before/after). If you touch code Android also compiles, note that the orchestrator needs an Android compile check (don't do the bytesize build yourself). No device installs (the orchestrator builds the combined iPhone app with DK1 + I34).
Never push; runner-dir check empty; text only in git. Deliverable `local/research/IN2/REPORT.md`; commit `[IN2] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push. Budget 2 h.
