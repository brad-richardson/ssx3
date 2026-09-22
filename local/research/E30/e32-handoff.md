# E32 handoff — apply-and-boot validation for the E30 faithful-MPEG fix

E30 was read-only on the fork (E31 owns the worktree + P-lane lease). E32
applies two diffs, runs the suite, and A/B-boots against E29's flag-on
title screen. All paths below are E30 evidence in this repo unless noted.

## Inputs

| Artifact | Path / ref | SHA / pin |
|---|---|---|
| Fix diff (1 file, +105/−3) | `local/research/E30/e30-fix.diff` | applies to `MPEG.cpp` @ `3adc0478` (`patch -p1 --dry-run` PASS, E30 receipt) |
| Regression diff (1 file, +231/−1) | `local/research/E30/e30-regression.diff` | applies to `ps2_runtime_expansion_tests.cpp` @ `3adc0478` (dry-run PASS) |
| Base fork ref | `3adc0478b6d2260acdd28a249466f2eef9a20176` | `MPEG.cpp` sha256 `f83ed02e…ef600` (re-verify at apply time) |
| Bypass branch (A/B reference) | `e29-movie-bypass` (`e5ce086d`) + `PS2X_SKIP_MOVIE=1` | title screen, E29 REPORT |

## Step 1 — apply + suite (fail-before first)

1. New branch from `3adc0478` (NOT on `e29-movie-bypass`: the fix must
   prove itself without the bypass; keep the bypass branch pristine for A/B).
2. Apply the regression diff ONLY → build → run suite with cwd = fork
   worktree root (E29: the 458 gate is CWD-sensitive).
   - Expected: new R7, R8b, R10, R11 FAIL; R8, R9 PASS (characterization:
     R8 pins the dry-park bound, R9's dispatch half needs the fix but its
     resume half passes via EOF-flush on base too — E30 REPORT §Mission 2).
   - Record exact fail list; it must be a subset of the six new tests.
3. Apply the fix diff → rebuild → run suite.
   - Expected: 464/464 (458 + R7, R8, R8b, R9, R10, R11), flag absent.
   - The five E29-measured bypass-broken tests MUST be green (named in the
     regression diff header comment): R1, R2, R4, R6, "waits for new
     decoder output". R2 is the load-bearing one: its 16 pre-header bytes
     never reach the decoder, so no re-request fires.

## Step 2 — A/B boot (P-lane lease, one boot at a time, ≤ 600 s each)

Same binary, no `PS2X_SKIP_MOVIE` anywhere in env (the fix has no flag):

| Boot | Binary | Expected |
|---|---|---|
| A (control) | `e29-movie-bypass` build, flag OFF | parks on movie (E29 e29a: feedES ×1, GetPicture ×1, `packets=0`) |
| B (candidate) | E32 fix build | `[MPEG:nonstream-redispatch]` ≥ 1 (fix engaged), feedES ×N per movie (N > 1), packets > 0, frames served (`[MPEG:GetPicture:FRAME]` ≥ 1), thread 1 leaves `Mpeg:0` park |

Then compare B's reached state against E29 e29b (flag-ON title screen):
1,135 distinct frames / 251 stubs / title PNG. Outcomes:

- B reaches the title screen with REAL decoded frames (not
  `writeBlankMpegFrame`): fix validated end to end.
- B advances past the movie park but stops elsewhere: record the next
  blocker precisely (stub histogram, park snapshot); the movie stall is
  still closed if frames were served.
- B still parks with `packets=0`: the fix did not engage — check
  `[MPEG:nonstream-redispatch]` count and `decoderBytesFed` progression;
  hand back to orchestrator, do not tune.

## Do not

- No `flush every chunk`, no synthetic success, no changes beyond the two
  diffs (E32 is apply + validate; any red is a finding, not a fix task).
- No push (orchestrator pushes); evidence commit `[E32]` + trailer.
