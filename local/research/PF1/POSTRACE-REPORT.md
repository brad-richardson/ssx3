# PF1 (post-race lane) — the post-results jump was a runtime unwind bug; fixed

> **ID collision:** `local/research/PF1/` also holds an older PF1 lane (Odin baseline: `REPORT.md`,
> `CHECKPOINT.md`, `logs/`), left untouched. This lane is `POSTRACE-REPORT.md`, `NOTEBOOK.md`,
> `pf1_*.py`.

Exploratory Opus worker (Claude Code), Mac mini, 2026-09-25. Active time ~95 min of 180 (13:02–13:58,
paused, 15:14–15:53). Notebook: `NOTEBOOK.md`. The orchestrator decides.

## Outcome

**Mechanism (ours, not the game's):** `PS2Runtime::dispatchGuestBranch` decides that a guest call
has returned when, after running the callee on the host, `ctx->pc == fallthroughPc`, **or
`ctx->pc == entryPc`** (a callee that never set pc). When a checkpoint suspends a callee **at a
recursive call to its own entry**, the callee's host function returns early with
`ctx->pc == entryPc`. The caller reads that as a return and carries on with the suspended callee's
registers.

SSX 3 hits this on the race results screen. The UI-element child walker `0x398868` (interior entry
of merged `sub_00398798`; list at this+0x74) recurses into child elements whose slot +0x88 is
`0x398868` again. When the timer-1 interrupt deadline (`0x3e4db8`) lands on that recursive
dispatch, the outer tree walker `sub_0039E6B8` (slot +0x78 in ~90 vtables) resumes at `0x39e72c`
with `0x398868`'s `s0`/`s1`. Its epilogue never ran. It then walks a UI element list, finds
+0x54 bit 6 set in a float, and calls through the float at +0x48. That gives `0x6c058000` in FR1
and `0x0` on the F3 tip, from `0x39e724`. A PS2 takes the interrupt and returns to the same
instruction, so it never does this.

**Fix** (fork `pf1-postrace`, local, from `ec2dbf1`, not pushed): **`3c037ab`**. When a checkpoint
returns true (at a dispatch or a generated backward edge) it marks an unwind. The post-call check
keeps returning false while the mark is set, before the `entryPc` heuristic. The scheduler clears
the mark before each top-level dispatch.

- `--stat`: `ee_guest_unwind.h` +22 (new; included only by the two .cpp files, so no codegen
  rebuild), `EeScheduler.cpp` +2, `ps2_runtime.cpp` +16/−1, `ps2_runtime_kernel_tests.cpp` +78.
- Validation: V1 runs **13,387 ticks (~3.7 guest min) past FR1's tick 20063** and 14,627 past the
  control's crash tick, on the live results screen, with zero missing targets.

## Evidence

| Row | Measurement | Receipt |
|---|---|---|
| E1 | FR1 crash: node `0x5aa300` +0x48 = `0x42640000` (57.0f); `s1 = 0x5ae940` = UI element `0x5ae900` + 0x40 | `FR1/run/r1-full/boot.log:60049`; B2 menu-time watches: both built by UI ctor `sub_0039FB30` |
| E2 | Control C1 (F3 tip + `a1eb9b9`, pre-fix scheduling): jump at `0x39e724` → `0x0`, **vsync 18823**, rc −6; `s1 = 0x5a7b40`, `s0 = 0x5a9d00 = [0x5a9b00+4]` | `run/C1-legacy/boot.log:1157` |
| E3 | Crash stack at sp `0x1ff7a80`: ra `0x39e72c`, saved s1 `0x5bef00`, s0 `0x5a7b00` = **`0x398868`'s frame** under the walker's jalr; parent ra `0x20e8f0` (`sub_0020E8E0`) | `C1-legacy/boot.log:1158-1166` |
| E4 | Crash RAM: parent list `0x5bef24` = {`0x5a8000`, `0x5a7b00`} (container nodes, vptr `0x494670`, embedded element at +0x40); element list `0x5a7bb4` = `0x5a3500…0x5a9b00, 0x5a9d00` (class `0x4949e8`, float at +0x48) | `C1-legacy/crash.ram` + `pf1_lists.py` |
| E5 | Dispatch trace tail `… 0x397718 → 0x397718 → 0x3e4db8 (timer-1 handler) → 0x397718 → 0x39e738` | E2 line |
| E6 | Generated code continues at `0x39e72c` iff `dispatchGuestBranch` returns true | `codegen-ssx3/sub_0039E6B8_0x39e6b8.cpp:255-285` |
| E7 | Control repeat V0 (same runner/env as C1): **identical crash line and byte-identical 32 MB crash RAM** (deterministic) | `run/V0-control/` |
| E8 | V1 (fix `3c037ab`, same env): `bound=wall_cap` at 1,801 s, **last tick 33450, `targets=0`**, E56 four RPCs only, `gs_fatal=null` | `run/V1-fix/result.json` |
| E9 | Frame hash at tick 17800 identical in V1/C1/V0 (`4a8a7b45`): the fix changes nothing before the bug site | `frames/upload-0.txt` |

## Frames viewed

| Frame | What |
|---|---|
| `run/C1-legacy/frames/upload-0.png` (t17800) | Happiness – Race, Single Event Results: 1 Mac 03:15, 2 Zoe 04:01, "Sorry, you didn't win." |
| `run/V1-fix/frames/upload-1.png` (t20100) | Same results screen, past FR1's crash tick |
| `run/V1-fix/frames/snap/snap-033450t-1800.45s.png` (t33450) | Same results screen, background camera moved (live) |

## Suite and checks

- Suite from the worktree root (`~/dev/ssx3-work/PF1/PS2Recomp`): green **643/643** on the final
  binary (`suite-green3.log`). Red (post-call check disabled) **642/643**, only "PF1: a checkpoint
  at a recursive call is an unwind, not a return" fails (`suite-red2.log`).
- Runner-dir check `git diff --stat 14b1e5cb pf1-postrace -- ps2xRuntime/src/runner`: empty.
- Runners (Release, diag taps OFF, TEST ON, paraLLEl `19d93b2` copy, codegen `8ea8ed43…`, two SHA
  reads each): fix `bin/runner-pf1-fix` `364cb0c13362f32d26ba20d94ad40b76d8074efd4e8371fbab48bdde53ddd264`
  (= `3c037ab`); control `bin/runner-pf1` `811c7928b35b3cdb3ef60add1535cbb2d765d87162c45ca6581512498763d747`
  (= `a1eb9b9`, run with `PS2X_EE_TIME_SLICE=1`, which equals `ec2dbf1`'s scheduling).

## Fork branch `pf1-postrace` (local, not pushed)

| Commit | What | Fold? |
|---|---|---|
| `3c037ab` | **the fix** + unit test | yes |
| `a1eb9b9` | dev-only `PS2X_MISSING_DUMP=<prefix>` (RDRAM + 64 stack words at the first missing target) | optional (useful for future stop-policy aborts) |
| `9c98713` + `f287b62` | an equal-priority time-slice change and its revert (net zero) | no; skip both |

## Boots (Mac mini, FR1-R1 route, `PS2X_DETERMINISTIC=1`, paraLLEl, sound, `PS2X_UNPACED=1`, stop policy, one slot each)

| Boot | Runner | Result |
|---|---|---|
| B1/B2 (0ed07c4 probe4, diag watch) | RD1 probe4 | menu-time watches only; stopped (host load 40–50, couldn't reach 20063 in 1,800 s) |
| A0, C0 | F3 / pf1 | stopped early for contention |
| C1 | pf1 control | crash t18823 (E2–E5) |
| V0 | pf1 control | identical crash (E7) |
| V1 | pf1-fix | no crash, t33450 at cap (E8) |

## Gaps

- The time slice: `EeScheduler::checkpointDue` round-robins **equal**-priority threads every 65,536
  cycles (upstream `f4309cd`, still in upstream `main`). The EE kernel doesn't do that. It was not
  this bug, and it is unmeasured whether it matters for SSX 3. A candidate for a separate lane.
- Other `ctx->pc == entryPc` ambiguities: a self tail-jump (`j` to one's own entry) still reads as a
  return. It isn't seen in SSX 3 and is not covered by this fix.
- The flag is a thread_local in a new header rather than a `PS2Runtime` member, to avoid a full
  codegen rebuild. Move it into the class at the next header-touching fold if preferred.
- No Odin/iOS run. The fix is shared runtime code. Brad's-card variant not run (the mechanism is
  card-independent).
- The ID collision above. Scratch `~/dev/ssx3-work/PF1` 2.7 GB (build + paraLLEl copy + runs; crash
  RAM images 2 × 32 MB).
