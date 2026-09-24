# GB6 Part 2 — repair the live capture gate before the GPU fold

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md` and
`AGENTS.md`. Read `local/research/GB6/REPORT.md` in full. Hand back
evidence; the orchestrator decides the fold gate and pushes the fork.
GB6's source, taps-OFF suite and matched CPU/GPU replays passed, but its
one live boot captured only one race frame. The exact cause is in
`ps2xRuntime/src/lib/ps2_runtime.cpp:482-494`: the env parser stores
**three** comma-separated target ticks, while GB6 supplied four. PKLOG
then consumed most of its 64 MiB combined-log cap. This brief repairs
only that capture setup, not the renderer.

Pin local fork worktree `~/dev/ssx3-work/GB6/PS2Recomp` branch
`gb6-fold` at `293fd81` and remote fork `ssx3` at `1aaed05` (verify).
Reuse GB6's taps-OFF Release runner and canonical E54D codegen without
rebuild. Read GB6's title/menu/race frames but do not edit GB6 output.
Write only `~/dev/ssx3-work/GB6B/` (copy the bounded GB6 boot driver
there) and `local/research/GB6B/REPORT.md`. No fork source edit,
generated code, device, Odin, iOS, or push.

Correct behavior: one I26-FAST mini-lease boot with `PS2X_GS_BACKEND=parallel`,
`PS2X_SKIP_MOVIE=1` dev-only, and **exactly three** target ticks
`PS2X_FRAME_DUMP_ONCE_TICKS=1810,2050,2150`. In the copied driver,
request two distinct race screenshots (first at/after 1810 and second
at/after 2050; the third is a spare), target guest tick ≥2200, and
wall cap 500 s. Remove `PS2X_PKLOG`, `PS2X_DIAG_PARK` and its directory
from this run; keep missing-function stop, vsync progress and frame dumps.
Combined logs ≤32 MiB, frames ≤25 MiB. Verify the copied driver sets
only the three target ticks and bounded progress/caps **before** boot.

Gate: two matching SHA reads of ISO, ELF, runner and canonical register
file before use; claim/release one mini slot, kill only own PID. One boot,
no retry or tuning. Require rc=0, ≥2200 guest ticks, two saved race
frames with distinct SHA-256, advancing HUD time, and rider/terrain
still visible; view both. Do not require rider distance to increase
(N7 saw a possible stall). Record known broken menu glyphs/dark GS
composite from GB6 without making a new parity claim. The screenshots are functional
evidence, not a clean speed run. Check global disk cap before/after.
If two frames or progression fail, stop and report; no fork push.

Deliver `local/research/GB6B/REPORT.md` with exact commands, pins,
script diff, SHA pairs, lease/log/disk receipts, frame table, gaps, and
one recommendation on fold readiness. Commit only the explicit report
`[GB6B]` with trailer `Orchestrated-By: Codex`; no push. The orchestrator
will inspect frames and runner-dir safety before its fork fast-forward.
