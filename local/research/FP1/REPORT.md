# FP1 — pace the guest to real time (REPORT)

Pacer works: paced menus never exceed 1.001× on any 5 s window, unpaced
peaks at 1.180× on the same route, and det-hash is identical paced vs
unpaced through t2400 (2422/2422 lines). Menu-window SND underruns fall
4.5× and overflows go 84,256 → 0. Speed tooling now sets `PS2X_UNPACED=1`.

## Mechanism (fork `ssx3` `0ed07c4`, before the fix)

- Guest VBlank fires on EE-cycle deadlines. Under `PS2X_DETERMINISTIC=1`
  (`m_cycleOnlyEvents`, `EeScheduler.cpp:195-198`) `processDueDeadlines`
  takes the whole cycle-due set with no host-time wait (`EeScheduler.cpp:
  2752-2763`). Only the non-det branch waits on `hostDeadline`
  (`EeScheduler.cpp:2784-2794`).
- `SetTargetFPS(60)` (`ps2_runtime.cpp:1153`) paces host presents only, on
  the render thread; the game thread's guest vsyncs run as fast as the host
  executes. Hence F1 B2 menus at 1.287×.
- Deterministic mode already decouples guest time from wall time: VBlank,
  SoundTick (cycle-scheduled, `EeScheduler.cpp:2944-2951`), pad script on
  `PS2X_PAD_SCRIPT_CLOCK=vsync` (`Pad.cpp:509`), and EE timers are all
  guest-cycle driven; `sceCdReadClock` is fixed (`CD.cpp:707`). No thread
  posts EE events mid-boot (`postEeEvent` has no callers outside the
  scheduler), so a host sleep cannot change guest state or event order.
  (`waitForEvent`, `EeScheduler.cpp:3072`, still wall-waits when idle even
  in det mode, then fast-forwards cycles — idle boots were already paced.)

## Implementation (fork branch `fp1-pace`, commit `51e730f4`, NOT pushed)

- New `ps2xRuntime/include/ps2_vsync_pacer.h`: `Pacer::onVsync(nowNs)`
  returns ns to sleep; first call anchors (`next = now + period`),
  ahead sleeps to the deadline and marches it, behind runs free, behind
  by > 2 frames resyncs (`next = now + period`). Period = 1001/60000 s =
  16683333 ns (59.94006 Hz). `PS2X_UNPACED=1` disables.
- `ee_scheduler.h` + `EeScheduler.cpp`: `m_vsyncPace` from env in the
  constructor (default on), pacer reset in `reset()`, one pace-and-
  `sleep_until` block at the top of the `VBlankStart` case. Sleeps only;
  no guest state touched. Unpaced path executes zero new code (one `if`).
- Unit test `ps2xTest/src/ps2_vsync_pacer_tests.cpp` (fake clock: anchor,
  march, on-time/behind, 2-frame boundary + resync, burst stacking, knob
  parsing) + CMake/`main.cpp` registration.

## Builds (1 full: clean + det reconfigure; F2 recipe §"Builds")

`~/dev/ssx3-work/FP1/build` (Release, Homebrew clang, canonical codegen
`8ea8ed43…`, parallel-gs `19d93b2`, logs/taps OFF, shadow-parallel ON):

| Runner | Det tap | SHA-256 (staged = both boot precheck reads) |
| --- | --- | --- |
| `bin/runner-clean` | OFF | `7045836e95cf8469aedba7705800a50af64c41b8e9214ff0b8dbf341ee336a8f` |
| `bin/runner-det` | ON | `7a50105825992743ad24a0751eda93769493862750b8eb19edcd6098103ae403` |

Suite from the worktree root: **619/619 pass, 0 fail** (`suite.log`;
612 F2 baseline + 7 pacer). Two first-run failures were test-authoring
arithmetic (deadline-1-ns case used the pre-march deadline; mHz bounds off
by 1000×); implementation untouched, details in `build-tests2.log` run.

## Boots (I26-FAST, empty mc0, `PS2X_SOUND=1`, paraLLEl + force, 1 slot each)

Driver: `fp1_boot.py` (committed here; F2 driver + `--unpaced` +
`PS2X_VSYNC_RATE_LOG=1` in det mode). P1/P2 envs differ ONLY by
`PS2X_UNPACED`. Same `runner-det` both. `[gs-path]` identical both;
coverage at vsync 2400 both; 0 FATAL, 0 hash markers both.

| Boot | Paced | Bound | Wall | Last tick | HUD wall |
| --- | --- | --- | --- | --- | --- |
| P1 det | yes | target | 111.6 s | 2404 | 40.3 s |
| P2 det | no (`PS2X_UNPACED=1`) | target | 158.0 s | 2400 | 73.4 s |

P2's longer wall is mini load (load 62→128 during P2 vs 40→67 during P1),
not pacing — pacing only adds sleeps. All rate claims below are per-window
rates, not total-time comparisons.

### Gate 1: paced ≤ 59.94/s (+1%) on any 5 s window — PASS

Independent `[vsync-rate]` 5 s lines: P1 max **59.98/s (1.001×)**; every
other window below 59.94. P2 peaks at **70.76/s (1.180×)** and 63.59/s
(1.061×). Full line lists in `~/dev/ssx3-work/FP1/run/{P1,P2}/boot.log`.

Per-phase vsyncs/s from `trace.jsonl` (tick boundaries as F2 `phases.py`):

| Phase | P1 paced (×) | P2 unpaced (×) |
| --- | --- | --- |
| title/startup 0→636 | 58.41 (0.974×) | 17.10 (0.285×, shader/load) |
| main menu 636→766 | 59.94 (1.000×, capped) | 67.30 (1.123×) |
| Select Character 766→884 | 40.53 (0.676×) | 22.56 (0.376×) |
| Setup / Peak 884→1099 | 48.83 (0.815×) | 52.12 (0.870×) |
| Mode / Event / Rules 1099→1440 | 59.22 (0.988×) | 78.01 (1.301×) |
| loading + Rival 1440→1714 | 20.81 (0.347×) | 13.36 (0.223×) |
| race 1714→ | 10.11 (0.169×) | 8.42 (0.140×) |

Below 1× nothing changes by construction (`onVsync` returns 0 when
behind; unit-tested); the race delta is load (P1's race ran faster
despite pacing, so no sleep fired there).

### Gate 2: det-hash identical paced vs unpaced to t2400 — PASS

`[det-hash:v1]` lines: P1 2447, P2 2422 (P1 settled further past the stop
tick). Common 2422-line prefix **byte-identical** (`cmp` rc=0), covering
t2400. `eeCycle@1714 = 8424822486` both; snd-tick guest cycles identical
47/47 lines.

### Gate 3: audio — menu underruns 4.5× down, overflows eliminated

SND tick-line counters at the race-HUD guest cycle, menu window vs totals:

| Window | P1 underruns / overflows | P2 underruns / overflows |
| --- | --- | --- |
| menus (to HUD) | 480,416 / **0** | 2,140,992 / 84,256 |
| end of boot | 3,301,792 / 0 | 5,688,576 / 84,256 |

Underruns don't reach zero because slow phases (loading 0.35×, some menus
< 1× on this loaded mini) starve the 48 kHz host consumer no matter what;
pacing caps only the fast side. All of P2's overflows happened in the menu
window; paced has none anywhere.

## Speed-tooling updates (`PS2X_UNPACED=1`)

- `local/research/F1/launch.py:148`, `local/research/F2/launch.py:148`,
  `local/research/N11/launch.py:148` — Odin speed envs (Brad's on-device
  play env untouched; launchers restore it).
- `local/research/F2/f2_boot.py:7,146` — Mac speed mode only; det mode
  stays default-paced (hashes equal either way).
- No `f1_boot.py` exists in-repo (F1 has no committed Mac driver), so
  nothing else matched the brief's `f1_boot.py`/`f2_boot.py` pattern.
  Closed-lane drivers (GB8, E57, …) deliberately untouched — they are
  evidence of past runs.
- All four files `py_compile` clean. Old builds ignore the unknown var.

## Gaps and notes

- No 3rd boot / 2nd build used (budget: 1 build, 2 boots, ~1 h wall).
- `PS2X_UNPACED=1` byte-for-byte vs pre-FP1 base: shown by construction
  (one `if` around new code; zero new calls when set) + the stronger
  P1==P2 check with pacing active — no separate base-commit A/B boot.
  Request one if the gate wants it run rather than reasoned.
- P1's 1.001× peak is sleep overshoot + 5 s window quantization, inside
  the +1% tolerance.
- Runner-dir guard empty; fork branch `fp1-pace` never pushed.

## Receipts

- Fork: `~/dev/ssx3-work/FP1/PS2Recomp` @ `51e730f4b2402e96aa5024b2e48dd94a16d6f21f`
  (from `ssx3` `0ed07c4`); `git status` clean.
- Logs: `~/dev/ssx3-work/FP1/{configure,build,suite,configure-det,build-det}.log`,
  `run/{P1,P2}/{boot.log,snd.log,trace.jsonl,result.json,frames/}`.
- Commands (from `~/dev/ssx3-work/FP1`):
  `cmake -S PS2Recomp -B build -G Ninja …` (F2 flags) → `cmake --build
  build --parallel 8 --target ps2x_tests ps2EntryRunner` → `(cd
  PS2Recomp && ../build/ps2xTest/ps2x_tests)` → `cmake -S … -B build
  -DPS2X_ENABLE_DET_HASH_TAP=ON` → build `ps2EntryRunner` →
  `python3 fp1_boot.py --mode det --backend parallel --runner
  bin/runner-det --label P1 --stop-tick 2400 --sound on
  --coverage-tick 2400` (P2 adds `--unpaced`).

## Recommended next action

Fold `fp1-pace` (`51e730f4`) onto fork `ssx3`: default-on pacing is
guest-state-neutral (det-hash proof) and required for Brad's play. No
follow-up brief needed unless the gate wants the base-commit A/B.

## Orchestrator gate (2026-09-25)

**Pass.** Paced menus ≤ 1.001× on every 5 s window (unpaced 1.180×), det-hash identical paced vs
unpaced (2,422 lines), menu SND overflows 84,256 → 0. Pacing sleeps only at VBlankStart; below 1×
nothing changes. `51e730f4` folds in F3 with UV1 Part 2 / NP1 Part 2 / VR1 as they gate; speed
tooling sets `PS2X_UNPACED=1` from then on. Note: the mini's load reached 62–128 during these boots
(many lanes building at once); speed numbers still need the exclusive lease and a quiet host.
