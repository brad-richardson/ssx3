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
- [x] **Fork history scrubbed (09-22):** `[E17]` had pushed generated guest
      code (full `register_functions.cpp`, `ps2_recompiled_functions.h`, 5
      `sub_*.cpp`) to public `fork/ssx3`. Rewrote 19 commits across 6
      branches (only those 7 paths changed); Brad ran the force-push with
      leases. `ssx3` `3adc0478` → `3d4feed`. No fork ref reaches `e63f161`.
      Old SHAs stay fetchable on GitHub until its GC.
- [ ] **E32 fold** (brief written, launches when E31 closes; base = scrubbed `3d4feed`): fold the
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

- [x] **G40 PASS (09-22): F2 execution-loss.** Composite prims 17/17
      accepted, texture input byte-exact cross-GPU, yet B unwritten on
      Odin right after the flush, even read behind a barrier. F1/F3
      refuted. The one CPU-side difference is the O4m texture-cache hash
      (`5a15…` vs `20dc…`); content-neutral.
- [ ] **G41 (running):** masked-write canary (PSM0/1 × FBMSK 0/ff000000 +
      the composite's full state) on scratch pages, hash-input breakdown,
      then ONE fix if a single condition is named. Fallbacks: binning
      readback or the Turnip driver contrast.
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

- [x] **N2 PASS (09-22):** first Android build. The stub link can't
      work at the old pin (E17's in-tree table is the full table); the
      full-title link with the codegen-dir port is green: APK 270,957,997 B
      `21a9230c…`, 9,441/9,441 `sub_*` defined, 0 undefined. Entry chain:
      NDK glue → raylib `android_main` → `main`. Gate exception accepted.
- [x] **N3 PASS (09-22): first PS2-recomp boot on the Odin reaches the
      animating stock title screen** (dev bypass, CPU GS, FFmpeg off).
      arm64 APK `69a79e29…` 134 MB; `ps2x.env` shim (+216 lines,
      Android-only) sets the CD image and dev flags; ELF + ISO staged and
      verified; title at t+20 s, 0 crashes over 5 min; ~21 guest frames/s
      with frame dumping on. Local branch `n2-android` @ `619d48a`.
- [ ] N4 (after E31): pad-script launch on the Odin to menus/race; a clean
      speed read with frame dumping off; fix PNG frame export on Android
      (raylib FILEIO); arm64 packaging stays. Watch: cpu-1 ~104 °C, and
      the battery was draining (62 → 59 %) during the run.
- [ ] N4: Android FFmpeg prefix + ON build + host vector parity.
- [ ] After N3: rebase `n2-android` onto the folded `ssx3` (E32 lands the
      codegen dir); the env shim goes onto `ssx3` through E. Input: pad
      script now, touch/controller H8 later.

## T — PCSX2 reference traces (bytesize)

- [ ] **T47 (running):** PCSX2 reference frames for title / main menu /
      Select Character / Select Event, using E31's input sequence, diffed
      against the recomp frames (character-select glitches). Then one
      healthy-series run if time allows.
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
