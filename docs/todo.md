# Working todo

Open work per lane, newest first. Only the orchestrator edits this file.
Rules: `AGENTS.md`. Board: `docs/status.md`. Numbers:
`docs/numbers-ledger.md`. History up to 2026-09-22, including every gate
read: `docs/archive/todo-2026-09-22.md`. Parked GameCube work:
`docs/reserve.md`.

**Milestone:** stock SSX 3 gameplay through the PS2 static recomp on the
Odin (menu → input → stock race advancing). Then Odin native race
with measured budgets, then 120 Hz simulation.

## E — PS2 runtime (fork `ssx3` @ `3adc0478`)

- [x] **E29 PASS (09-22):** dev-only bypass reaches the rendered SSX 3
      title screen. Branch `e29-movie-bypass` @ `e5ce086d`, local.
- [ ] **E31 (running):** scripted pad input on the bypass build, title →
      menu → stock race start and advancing; owns fork + P-lane lease.
- [x] **E30 PASS (09-22, design):** zero packets = correct parser + host
      latch. Each 5,040 B chunk is one unterminated picture; the terminator
      is in chunk 2, which is never requested. Fix: `e30-fix.diff`
      (re-dispatch while decoder-accepted bytes flow without frames, cap
      4096 rounds). Regression: `e30-regression.diff` (R7–R11, suite → 464).
- [ ] **E32 fold** (brief written, launches when E31 closes): fold the
      bypass + pad script, `i23-ffmpeg-ios`, `i8-device-bundle-name` and the
      branchless I10–I21 commits onto fork `ssx3`; suite + 2 boots; push
      `ssx3` fast-forward. Backups pushed 09-22 as `fork/archive/*` +
      `fork/e29-movie-bypass`. After the orchestrator verifies, delete the
      folded branches locally and on `fork` (Brad authorized 09-22).
- [ ] E33: apply E30's two diffs on `ssx3` after E32, then 464/464, then an A/B
      boot with the flag off vs the bypass title screen (`e32-handoff.md`).
      Watch `round=` in boot logs: an empty-queue `sequence_end` spins up to
      the 4097 cap before parking (E30 residual 3). Mid-movie CD refill
      still can't wake a dry park (residual 2).
- [ ] Android handoffs from N1 (E owns the edits): H1 adopt
      `PS2X_GAME_CODEGEN_DIR`, H4 no-env `cdImage` derivation, H3 merge
      the C3/C5 MPEG vector diagnostics from `i23-ffmpeg-ios`, H2 an
      Android FFmpeg IMPORTED block, H5 entry-provider check, H7 non-env
      diagnostic triggers if N5 needs them.
- [ ] Older queue, check before briefing: `3006a07` cherry-pick onto the
      fork, K1 ret0 retirement, E2b/E2c (held since 09-20).

## G — GS composite / GPU backend (paraLLEl-GS `3a66c19` + carried G26/G28)

- [ ] **G40 (running):** sub-vsync A→B wall at boundary 1 on the Odin
      splits F1 rejected draw / F2 write-back lost / F3 stale read, then
      one candidate fix if a single mechanism shows up. Acceptance: Odin-B
      equals Mac-B `840cd308…` and the scanouts show content.
- [ ] Commit G26 + G28 in the clone after the storage cutover (G39
      decision: carried diffs until then), with a clean rebuild and G39's
      R1/R2 shapes re-run as proof.
- [ ] G22 env-gated sampler-feedback workaround needs its own gate. G18
      hunk adoption queued. O1 writer naming still open.
- [ ] Then integrate the GS backend with the PS2 runtime (the standalone
      replay is not the product path).
- [ ] Turnip contrast probe (sideload Mesa Turnip, re-run the replayer):
      after the F-split closes, only if the fault looks driver-side.
- [ ] Adreno filing: paused (Brad, 09-22). Any rewrite drops the
      withdrawn sampling inference.

## N — Android app (Odin)

- [ ] **N2 (running, on bytesize):** stub `ps2EntryRunner` APK via the
      fork's Gradle build (bars B1–B6), then the full-title link with a
      local `PS2X_GAME_CODEGEN_DIR` port. No device.
- [ ] N4: Android FFmpeg prefix + ON build + host vector parity.
- [ ] N5: install + stock-title launch to a named checkpoint on the Odin
      (needs H4/H5, ELF + ISO staging, logcat `ps2x` tag confirmed, input
      overlay H8).

## T — PCSX2 reference traces (bytesize)

- [ ] T47: continue the healthy series (hold-step samples under both
      trackers; hold-window crash lottery at 3/4). Queued behind N2
      because they share bytesize.
- [ ] Keep T tied to named E/G questions (reference captures for
      menu/race timing once E reaches them).

## I — iOS recomp (parked)

- [ ] Re-probe on the iPad only after a relevant runtime change (E30's
      MPEG fix or the E29 bypass path). Branch `i23-ffmpeg-ios` @ `aa73dbc`.

## V — storage and hosts

- [ ] Mac mini cutover per `local/research/V1/CUTOVER.md`. Blocked:
      the mini isn't set up (Brad). Waits for active leases.
- [x] Pruned 2 stale ssx3 + 7 stale fork worktree entries (09-22, dirs were
      already gone). Keep the SSD `ps2x-i*/fork-wt` worktrees: they are
      the only refs holding the branchless I10–I21 commits until the fold.
- [ ] V1 follow-up: mirror `emulog-t46r3.txt` to the share.
- [ ] Mac internal disk ~3 GB free: keep builds on the SSD or bytesize.

## Cross-lane

- [ ] Update `docs/route-criteria.md` for the 120 Hz simulation
      preference, and drop its stale work-queue snapshot.
- [ ] Update `docs/plan-gs-gpu-backend-2026-09-18.md` to the paraLLEl-GS
      path the G lane actually uses (it still describes a greenfield
      backend).
- [ ] PS2 120 Hz simulation: the game-side timestep patch sites are
      published for the PS2 build. Scope this once a stock race runs.
