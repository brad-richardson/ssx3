# SJ1 report — full Happiness race stalls on the route (down = brake); Snow Jam 99 % stall is GONE

Brief `local/muse/prompts/SJ1.md`. Worker: Muse Code, Mac mini. Tables + receipts; the orchestrator decides.

| SJ1 | Receipt |
|---|---|
| Stop point | **R1 + R1b (spare) + R2 executed, all three boots healthy, zero FATAL.** R1 (tuck+X): rider parks, 10 % at 00:03:31, no finish. R1b control (I26-FAST, no race inputs): rider rides, 52 % at 00:02:38 and climbing when the 700 s cap hit. R2: **Snow Jam loads past 99 % and races** (card → start gate → 00:01:26 at STOP). |
| Headline | **No stock race has finished yet — but the blocker is the route, not the runtime.** Continuous d-pad down parks the rider (0–2 MPH); release it and the same rider rides at 44 MPH. E31's "down-tuck" assumption is wrong: down behaves as a brake. Separately, the E31 Snow Jam 99 % stall does not reproduce on fork `0ed07c4`: CD reads flow through loading into the race (2,223 lines, 0 unresolved). |
| Build | 1/1 (Release, diag off; `configure rc=0`, `build rc=0`, 455 steps). Runs 3/3 (R1 1000 s + R1b 700 s + R2 455 s). No source changes, never pushed. |

## Pins and inputs

| Item | Pin | Receipt |
|---|---|---|
| Fork source (SJ1 clone, read-only) | `ssx3` `0ed07c4` (`0ed07c4362b9bd53c09094fd028ee05e8aaf021a`) | `git log -1`, clean `status` |
| paraLLEl-GS source (SJ1 copy of F2's tree) | `19d93b2` (+ `pgs_env_knobs.hpp`, the force knob) | `git log -1`, clean `status` |
| Granite (submodule of the above) | `166ba21a247a681903cc9d0bb6562fe50a554c85` | `git submodule status` |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…62d688a3` | two SHA reads per boot |
| ISO / ELF | `3c2f8eb1…61ebf5` / `1b49d05c…67af7bc` | two SHA reads per boot |
| Runner `bin/runner-clean` | SHA-256 `bd2290f4…88c66ad` (×2), 135,104,224 B | copy-out + two reads |
| Build flags | Release, Homebrew clang, `PS2X_GS_SHADOW_PARALLEL=ON`, TEST/STUDIO/UI OFF, RUNTIME/AGGRESSIVE/DIAG_TAPS/DET_HASH OFF | `configure.log`, GB8 recipe |
| `[gs-path]` all boots | `hier_rule=hier-if-large hier_t2=2 hier_t4=4 … desc=plain … gpu=Apple M5 Pro` | `result.json` each run |

Common env: `PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`,
`PGS_HIER_BINNING=force`, `PS2X_SOUND=1` (`[snd-output] stream rate=48000` live on all runs),
`PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, vsync pad clock, empty mc0/mc1,
`PS2X_MISSING_FUNCTION_POLICY=stop` (never tripped), `PS2X_VSYNC_RATE_LOG=1`,
`PS2X_FRAME_DUMP_DIR` + 20 s snapshotter. One mini slot each (R1 slot 2, R1b slot 2, R2 slot 3).
Scratch `~/dev/ssx3-work/SJ1` 2.3 GB (build 1.7 GB, runs 57 MB).

## R1 full race — rider parks under tuck+X, no finish (wall_cap 1000.5 s, tick 14754)

Route R1 (94 entries, full string in the appendix): I26-FAST through the Rival card, then from
38522 ms guest an X tap (200 ms) every 10 s with down held between taps (9,750 ms holds, 250 ms
down-free windows for the taps since X is ignored while down is held), out to ~358 s guest.
Delivered: 72 presses / 71 releases (last press i=71 at 238,772 ms; the run ended mid-hold).
Zero FATAL. Host load 104 → 8 across the run (rates are context, not speed numbers).

Frames viewed (all 512×448, 2ND/2 throughout):

| Wall | Tick | Race clock | Prog | Speed | Screen |
|---|---|---|---|---|---|
| 20 s | 853 | — | — | — | Setup Character (Zoe, Continue): menus on rails |
| 40 s | 1659 | — | — | — | Rival Challenge card (Happiness - Race, vs Mac) |
| 60 s | 1775 | 00:00:01 | 0 % | — | Race start, EA Radio card |
| 140 s | 2501 | 00:00:13 | 2 % | 1 MPH | Crawling from the start |
| 200 s | 3263 | 00:00:25 | 3 % | 2 MPH | Barely moving |
| 300 s | 4610 | 00:00:49 | 4 % | 2 MPH | Still crawling |
| 400 s | 6531 | 00:01:21 | 5 % | 10 MPH | RECOVER prompt (rider down) |
| 540 s | 8315 | 00:01:50 | 6 % | 12 MPH | Upright, trick 480, slow |
| 880 s | 12284 | 00:02:56 | 8 % | 0 MPH | Fully parked mid-slope |
| 980 s | 14362 | 00:03:31 | 10 % | 14 MPH | Final: 10 % after 3.5 min of racing |

End state: **no finish, no results, no menu return** — the rider crawls 0 → 10 % in 3 min 31 s
of race time and is nearly stationary at the cap. The race clock always advanced, so the
brief's 60 s clock-stall stop rule never tripped; the run used the full approved 1000 s.

Coverage at vsync 9000: `targets=0`, `ids=0`, `pairs=4` — the E56 four, one hit each
(`80000211/1`, `237/0`, `534e44/0`, `80000006/ff`). Matches baseline exactly.

## R1b control (spare) — no race inputs: the rider RIDES (wall_cap 700.7 s, tick 11178)

Route R1b = I26-FAST verbatim (31 entries, verified byte-identical to `ROUTES.md`: 30 s tuck,
then nothing). All 31 presses/releases delivered. Zero FATAL. Same binary, same prefix as R1;
only the race inputs differ.

| Wall | Tick | Race clock | Prog | Speed | Screen |
|---|---|---|---|---|---|
| 140 s | 3297 | 00:00:27 | 2 % | 1 MPH | Tuck still held: crawling |
| 200 s | 4355 | 00:00:45 | 4 % | 44 MPH | 15 s after release: riding |
| 300 s | 5794 | 00:01:08 | 14 % | 20 MPH | RECOVER (a fall), progressing |
| 540 s | 9118 | 00:02:04 | 37 % | 43 MPH | Ice-cave section (dark scenery, HUD crisp) |
| 660 s | 10626 | 00:02:29 | 50 % | 44 MPH | Open slope, spray, riding hard |
| 700 s | 11178 | 00:02:38 | 52 % | 19 MPH | Cap hit mid-race, healthy |

End state: **healthy mid-race, 52 %**, cut off by the wall cap — not by any stall.

Coverage at vsync 7000: `targets=0`, `ids=0`, `pairs=4` (E56 four). Matches baseline.

## Finding: d-pad down is a brake, not a tuck — the R1 park is route-caused

Three independent contrasts, all pointing the same way:

1. **R1 vs R1b** (same binary/prefix, inputs differ): at matched race clocks R1 crawls and R1b
   rides — 00:00:45/49: 4 % at 44 MPH vs 4 % at 2 MPH; end: 52 % riding vs 10 % parked.
2. **Within R1b** (tuck release): 1 MPH at 00:00:27 (held) → 44 MPH at 00:00:45 (released).
3. **N10 consistency**: on the Odin the rider sat at 0–1 MPH with a RECOVER prompt during the
   I26-FAST 30 s tuck (00:00:06–00:00:40) and rode at 43–44 MPH after it ended — the same
   hold/release shape. The N-lane "rider idle at race start" item is almost certainly this
   effect, not a runtime bug.

E31's "down-tuck" evidence (timer advance + scene motion over ~4 s of racing) is consistent
with down-as-brake: R1 also rolls 0 → 2 % in the first seconds before parking. E31 never ran
long enough to see the park. I26-FAST's "steady 30 s tuck" should be renamed, not reused, for
any race-progress attempt.

Confound left standing: R1 held down AND tapped X every 10 s, so down-vs-X is unsplit (one
down-only run would split it; no budget left). Recommended next full-race attempt: the R1b
shape (no race inputs) with a ~1,300–1,400 s wall cap (needs approval past 1000 s — R1b's
0.42 %/s extrapolates to a ~00:04:30 finish) — or an analog-stick tuck (`lx/ly`) if a lane
wants to test the real tuck input first. No race has finished yet: results/menu-return are
still unobserved.

## R2 Snow Jam — the 99 % stall is GONE (stop_file 454.5 s, tick 7647)

Route R2 (92 entries): R1 minus the two Select-Event downs, so cross@22306 confirms Snow Jam
(the default). Delivered: 48 presses / 47 releases. Zero FATAL. `PS2X_CD_READ_TRACE` on.

| Wall | Tick | Screen (viewed) |
|---|---|---|
| 20 s | 886 | Select Event, Snow Jam highlighted (route correct) |
| 40 s | 1709 | "Snow Jam - Race / Single Event" pre-race card (6 riders, record 02:57, X Continue) |
| 60 s | 1878 | Start gate, countdown "1", 00:00:00, riders in gates |
| 80 s | 2056 | Race: 00:00:02, 6TH/6, 1 %, RECOVER bar, pack ahead under the gantry |
| 420 s | 7070 | Race: 00:01:26, 6TH/6, 4 %, 5 MPH, trick 370, sunny gated course |

Loading completed between tick ~1440 and the card at 1709 (no 20 s-cadence snap landed inside
the ~200-tick load window, so no loading-% frame; the pass verdict rests on the card → gate →
race chain plus the CD trace). The run was STOP-stopped at 454 s with the race healthy — the
rider crawls at 5 MPH exactly as R1 predicts (R2 carries the same down-hold tail), which is
further confirmation of the brake effect, not a Snow Jam problem.

CD trace (`cdread.log`, 2,223 lines, last line partial from SIGTERM): **all `cdread`, 0
`unresolved`**, reads flowing through every phase — 923 boot (<1440), 871 load window
(1440–1750), 429 race (>1750), last seq 2223 at vsync 7226. E31's stall signature (reads stop
~95 %, zero reads for minutes) is absent: the `_sceCdSC` loop reads into the race. The todo
item's suspected fix (sound HLE now folded) is consistent with this re-test; the stall itself
is closed empirically on `0ed07c4`.

Coverage at vsync 3000: `targets=0`, `ids=0`, `pairs=4` (E56 four). Matches baseline.

## Exact commands

```sh
# Sources (E checkout untouched; SJ1-local copies)
git clone ~/dev/PS2Recomp ~/dev/ssx3-work/SJ1/PS2Recomp && checkout 0ed07c4 (detached, clean)
cp -a ~/dev/ssx3-work/F2/parallel-gs ~/dev/ssx3-work/SJ1/parallel-gs  # 19d93b2, Granite 166ba21a, clean
# Build (GB8 flags; configure rc=0 66 s; build rc=0, 455 steps)
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=$PWD/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2EntryRunner   # nice -n 10 (loaded host)
cp build/ps2xRuntime/ps2EntryRunner bin/runner-clean       # bd2290f4…88c66ad ×2
# Boots (driver: local/research/SJ1/sj1_boot.py)
python3 sj1_boot.py --route r1 --runner bin/runner-clean --label r1-full --wall 1000 --coverage-tick 9000
python3 sj1_boot.py --route r1b --runner bin/runner-clean --label r1b-control --wall 700 --coverage-tick 7000
python3 sj1_boot.py --route r2 --runner bin/runner-clean --label r2-snowjam --wall 700 --coverage-tick 3000 --cd-trace
touch run/r2-snowjam/STOP   # early stop once the pass verdict was determined (454 s)
```

## Gaps and recommended next actions

- No race has finished: results screen and menu-return are unobserved. Next attempt: R1b shape
  (no race inputs) with ~1,300–1,400 s wall (extrapolated ~00:04:30 finish; needs >1000 s
  approval), or analog-stick tuck first. One down-only run would split the down-vs-X confound.
- No loading-% frame for Snow Jam (20 s cadence vs ~200-tick window); the pass verdict does not
  need one (card → gate → race + continuous CD reads), but a future run with a 5 s snapshotter
  over ticks 1400–1750 could pin the curve.
- R2's last cdread line is SIGTERM-truncated (`dest=0x00e7`, no newline); all 2,222 complete
  lines parsed.
- R1 ran under heavy host load (loadavg 104 → 8); race vsync rates (8–21/s across runs) are
  context, not speed numbers (frame-dump + sound diagnostics were on).
- Text in git: `sj1_boot.py` + this report. Scratch: `~/dev/ssx3-work/SJ1` (2.3 GB). Global
  disk ~161/200 GB.
- Recommended: close the Snow Jam 99 % todo item; reassign the N-lane "rider idle" item to the
  route (down = brake); rename I26-FAST's "tuck" leg in `ROUTES.md` so no future brief reuses it
  for race progress.

## Appendix: route strings (guest ms, `PS2X_PAD_SCRIPT_CLOCK=vsync`)

R1 (94 entries) — I26-FAST + X-tap every 10 s guest with down between taps to ~358 s:

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:cross:200,38772:down:9750,48522:cross:200,48772:down:9750,58522:cross:200,58772:down:9750,68522:cross:200,68772:down:9750,78522:cross:200,78772:down:9750,88522:cross:200,88772:down:9750,98522:cross:200,98772:down:9750,108522:cross:200,108772:down:9750,118522:cross:200,118772:down:9750,128522:cross:200,128772:down:9750,138522:cross:200,138772:down:9750,148522:cross:200,148772:down:9750,158522:cross:200,158772:down:9750,168522:cross:200,168772:down:9750,178522:cross:200,178772:down:9750,188522:cross:200,188772:down:9750,198522:cross:200,198772:down:9750,208522:cross:200,208772:down:9750,218522:cross:200,218772:down:9750,228522:cross:200,228772:down:9750,238522:cross:200,238772:down:9750,248522:cross:200,248772:down:9750,258522:cross:200,258772:down:9750,268522:cross:200,268772:down:9750,278522:cross:200,278772:down:9750,288522:cross:200,288772:down:9750,298522:cross:200,298772:down:9750,308522:cross:200,308772:down:9750,318522:cross:200,318772:down:9750,328522:cross:200,328772:down:9750,338522:cross:200,338772:down:9750,348522:cross:200,348772:down:9750
```

R2 (92 entries) — R1 minus the two Select-Event downs (Snow Jam is the default):

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:cross:200,38772:down:9750,48522:cross:200,48772:down:9750,58522:cross:200,58772:down:9750,68522:cross:200,68772:down:9750,78522:cross:200,78772:down:9750,88522:cross:200,88772:down:9750,98522:cross:200,98772:down:9750,108522:cross:200,108772:down:9750,118522:cross:200,118772:down:9750,128522:cross:200,128772:down:9750,138522:cross:200,138772:down:9750,148522:cross:200,148772:down:9750,158522:cross:200,158772:down:9750,168522:cross:200,168772:down:9750,178522:cross:200,178772:down:9750,188522:cross:200,188772:down:9750,198522:cross:200,198772:down:9750,208522:cross:200,208772:down:9750,218522:cross:200,218772:down:9750,228522:cross:200,228772:down:9750,238522:cross:200,238772:down:9750,248522:cross:200,248772:down:9750,258522:cross:200,258772:down:9750,268522:cross:200,268772:down:9750,278522:cross:200,278772:down:9750,288522:cross:200,288772:down:9750,298522:cross:200,298772:down:9750,308522:cross:200,308772:down:9750,318522:cross:200,318772:down:9750,328522:cross:200,328772:down:9750,338522:cross:200,338772:down:9750,348522:cross:200,348772:down:9750
```

R1b (31 entries) = I26-FAST verbatim (`local/research/I26/ROUTES.md`); verified byte-identical
by the driver check.

## Orchestrator gate (2026-09-25)

**Pass.** (1) **Snow Jam's 99 % loading stall is gone** on `0ed07c4` (loads and races; the SPU banks
and 64-bit branches are the likely cure). (2) **The "rider idle at race start" (N10/N11/F1/F2: 0–1
MPH until ~00:00:40) is our route, not the runtime:** I26-FAST holds d-pad down for 30 s, and down
brakes; released, the rider rides at 44 MPH. The control run with no race inputs reached 52 % at
00:02:38 when the 700 s cap hit, so a full race needs ~20 min of Mac wall time at 0.25×. Next:
drop the down-hold from I26-FAST (ROUTES.md note) and run one no-input race to the finish with a
1,800 s cap, preferably on bradflix once LX1 passes. Coverage 0/0/4 throughout.
