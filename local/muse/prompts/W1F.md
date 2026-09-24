# W1F — Fold native 16:9 and iOS presentation into fork `ssx3`

You are a worker in a herdr pane in `~/dev/ssx3` on the Mac mini. Follow
`~/dev/AGENTS.md` and `AGENTS.md`. Hand back tables and receipts; the
orchestrator decides the gate. Read `local/research/W1/REPORT.md`,
`local/research/I26/REPORT.md`, `local/research/E56/REPORT.md`, and
`docs/orchestration.md` §4 and §6 first.

Brad accepted the W1 title/menu/HUD 2D stretch for now (09-24). The native
anamorphic mode keeps the 3D rider proportioned, and should be the 16:9
default. `w1-wide` at `7a0e46a` contains I26 presentation and virtual pad
commit `0c32269` plus W1. E56 pushed fork `ssx3` at `8e2864a`; verify the
remote tip before starting. The E56 codegen must be the canonical
`~/dev/ssx3-work/codegen-ssx3` (verify from its report). Do not use the
stale W1 codegen.

Write scope: `local/research/W1F/`, `~/dev/ssx3-work/W1F/`, and a new fork
worktree there on local branch `w1f-fold` from `fork/ssx3`. The local iOS
build scripts may be copied into W1F and adjusted there; do not edit I26's
checked-in scripts. Lease files via `local/tooling/p_lane_lease.py` are in
scope. No other lane's worktree or build dir may be changed.

## Work and gates

1. Fetch `fork/ssx3`, verify `8e2864a`, and create the worktree. Cherry-pick
   the two W1 branch commits **as new commits, no rebase**. Resolve only
   conflicts in the touched presentation/test files. Verify the diff under
   `ps2xRuntime/src/runner/` from upstream `14b1e5cb` is empty, and the
   branch contains only the intended I26/W1 change set beyond E56.
2. Configure and build the Release Mac runner with E56's promoted codegen.
   Run `ps2x_tests` from the fork root, taps OFF and taps ON. Wait for other
   `clang`/`ninja` builds and use `nice`. Exercise the unit cases for default
   16:9, explicit `PS2X_WIDESCREEN=0`, and `PS2X_ASPECT` override.
3. One mini-lease boot (I26-FAST, `PS2X_SKIP_MOVIE=1`, dev-only, capped at
   500 s) to Select Character and a race frame, default W1 mode. Save
   bounded frames, view them, and state whether the 3D rider, 2D stretch,
   and known GS composite occlusion match W1/E56. No fixed-tick frame-hash
   gate: free-running boots remain nondeterministic until E55.
4. After gates 1–3 pass, fast-forward push `w1f-fold:ssx3` to `fork`.
   Repeat the runner-dir check immediately before the push and verify the
   remote tip afterward. Generated guest sources, game data and binaries
   stay out of git.
5. Rebuild iOS from this pushed source and E56 codegen. Use a W1F copy of
   `local/research/I26/build-install.sh` with its branch/path assertions
   updated. Test on the Simulator first (title, SC and race; bounded), then
   on the iPad if unlocked. If the iPad is locked, report that immediately;
   do not launch on it. Re-read the iPhone device id, then **build and
   install only** on the iPhone: never launch, test or screenshot it. Record
   app SHA and `devicectl` install result. Tell the orchestrator once the
   iPhone install lands.

## Budgets and stop rules

At most 2 Mac configure/build attempts, 1 boot, 1 Simulator run, 1 iPad
run and 1 iPhone install. 6 h; ≤8 GB new bytes in W1F. Check
`local/tooling/disk_budget.sh` before and after large writes. If a cherry-pick
conflict needs an E-lane design choice, a test fails after one clear repair,
or the Mac boot regresses, stop before pushing and hand back the evidence.
If the iOS stage fails after the fork push, keep the pushed fold and report
the exact iOS blocker; do not silently skip the install.

Deliver `local/research/W1F/REPORT.md` with revisions, exact commands,
suite counts, runner/app SHAs read twice, viewed frames, install receipts,
remote-tip and runner-dir checks, and gaps. Commit `[W1F]` in ssx3 with
`Orchestrated-By: Codex`; do not push ssx3 `main`.
