# GB6 — fold the opt-in paraLLEl backend onto current `ssx3`

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md`,
`AGENTS.md`, and `docs/orchestration.md` §4. Read `local/research/GB4/REPORT.md`
Part 6 and `local/research/GB5D/REPORT.md`. Hand back tables and receipts;
the orchestrator decides the fold gate and pushes the fork. The paraLLEl
backend has **visible broken glyph strokes** at title tick 300 and menu
tick 700 in matched replay. Do not claim visual parity or fix glyphs here.

Pin remote fork `ssx3` at `1aaed05` and canonical E54D codegen at
`~/dev/ssx3-work/codegen-ssx3`; verify both. Create
`~/dev/ssx3-work/GB6/PS2Recomp`, local branch `gb6-fold`, from that remote
tip. GB4's local `gb4-parallel` at `f796669` is the source branch, but
cherry-pick only these six commits, in order, **as new commits without
rebase/history rewrite**: `50d03a8 55f8253 9517210 8f49a9c 520bd61
c5913e4`. The last two GB5/GB5B probe commits stay on the G worktree.
Resolve conflicts only in the files those commits touch. If the current
E54D/W1 runtime needs a design choice, stop with conflict evidence.

Write scope: new `GB6/` worktree/build/run only, and
`local/research/GB6/REPORT.md`. No other worktree, generated source,
canonical codegen, game data, device, or `ssx3` docs edits. No fork or
ssx3 push. Existing GB4 capture `run/gb4p4.capture.bin` and true-path
sidecar may be read but never copied/modified.

Correct behavior/gates:

1. Source review: `PS2X_GS_SHADOW_PARALLEL` remains CMake default OFF,
   `PS2X_GS_BACKEND` absent uses CPU, and requesting parallel in an OFF
   build falls back to CPU with a clear message. Check that the fold's
   diff against `1aaed05` is confined to the six intended changes.
   `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` must be
   empty. No generated guest code/binaries in Git.
2. Configure Mac Release/Ninja with current E54D codegen and local
   `~/dev/ssx3-work/G43/parallel-gs` source, shadow ON, diagnostics taps
   OFF; build `ps2x_tests ps2EntryRunner`, run full suite from fork root.
   Wait for other clang/ninja work; use `nice`. One additional ON-mode
   suite if configuration permits within budget. Run one CPU and one
   paraLLEl replay from the *same* GB4 capture/path sidecar. Both suites
   pass; GPU replay has `init_ok=1`, 1,982,063 packets, 0 unsupported
   clear/VRAM operations and 0 null scanouts; compare CPU hashes to GB4
   Part 6 direct baseline. An environment-induced unit-test failure is
   a failed gate, not a clean GPU result.
3. One mini-lease I26-FAST live boot with `PS2X_GS_BACKEND=parallel`,
   `PS2X_SKIP_MOVIE=1` (dev-only), target race HUD tick ≥2050, wall cap
   500 s; view title/menu and two race frames. Record whether the known
   glyph damage persists and whether rider/terrain/HUD advance. This is
   functional/diagnostic only, **not** a clean speed number. No fixed-
   tick hash A/B before E55. Check ISO/ELF, runner and codegen register
   file with two matching SHA reads before boot. Claim/release one mini
   slot, kill only own PID, logs ≤64 MiB.

Budget: two configure/build attempts (one clear repair), two replay runs
plus one setup retry, one boot, ≤8 GiB GB6 new bytes, 200 GB global cap.
Stop on a failed gate after one clear repair; leave branch local and
report. Do not tune graphics or alter glyph rendering in this lane.

Deliver `local/research/GB6/REPORT.md` with pins, cherry-pick/conflict
table, diff/runner-dir review, suites, replay counters/hash comparison,
boot frames/SHAs, budgets, exact commands and gaps. Commit local fork
branch `[GB6]` as applicable with `Orchestrated-By: Codex`; commit only
the explicit report in ssx3 `[GB6]` with the same trailer. **No push:**
the orchestrator reviews and pushes the fork only after its own gate.
