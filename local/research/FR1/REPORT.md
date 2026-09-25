# FR1 report — first stock race FINISHED (Happiness 2nd, 04:18); Snow Jam + Metro-City load and race

Brief `local/muse/prompts/FR1.md`. Worker: Muse Code, Mac mini. Tables + receipts; the orchestrator decides.

| FR1 | Receipt |
|---|---|
| Stop point | **R1 + R2 + R3 executed, all three boots healthy, zero FATAL.** R1 (no race inputs): **the rider finished** — "2nd place 04:18", results screen (Mac 03:13), then a guest JALR to `0x6c058000` at tick 20063 tripped the stop policy (rc −6). R2: Snow Jam replicates SJ1 (start gate → racing 6th/6). R3: Metro-City loads and races (night-city course, 6th/6). |
| Headline | **The first stock race has finished in our runtime.** Dropping I26-FAST's 30 s down-hold (down brakes, SJ1) lets the untouched rider ride Happiness start → 99 % → finish → results in 04:18 with no inputs at all. Three events now confirmed loading and racing on fork `0ed07c4`. |
| Build | 1/1 (Release, diag off; `configure rc=0`, `build rc=0`, 455 steps; runner bit-identical to SJ1's). Runs 3/4 (R1 1459 s + R2 298 s + R3 258 s; R2/R3 STOP-stopped once their verdicts were determined). No source changes, never pushed. |

## Pins and inputs

| Item | Pin | Receipt |
|---|---|---|
| Fork source (FR1 clone, read-only) | `0ed07c4` (`0ed07c43…af021a`, detached, clean) | `git log -1`, clean `status`; `ls-remote fork ssx3` = `0ed07c4` at build time, so per the brief F3's tip was **not** used (`f3-fold` = `ec2dbf1`, 7 ahead locally, unpushed) |
| paraLLEl-GS source (FR1 copy of F2's tree) | `19d93b2` (+ `pgs_env_knobs.hpp`, the force knob) | `git log -1`, clean `status` |
| Granite (submodule of the above) | `166ba21a247a681903cc9d0bb6562fe50a554c85` | `git submodule status` |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…62d688a3` | verified before build; two SHA reads per boot |
| ISO / ELF | `3c2f8eb1…61ebf5` / `1b49d05c…67af7bc` | `sha256sum` + two SHA reads per boot |
| Runner `bin/runner-clean` | SHA-256 `bd2290f4…88c66ad` (×2), 135,104,224 B | copy-out + two reads; **identical to SJ1's runner** |
| Build flags | Release, Homebrew clang, `PS2X_GS_SHADOW_PARALLEL=ON`, TEST/STUDIO/UI OFF, RUNTIME/AGGRESSIVE/DIAG_TAPS/DET_HASH OFF | `configure.log`, GB8 recipe |
| `[gs-path]` all boots | `hier_rule=hier-if-large hier_t2=2 hier_t4=4 … desc=plain … gpu=Apple M5 Pro` | `result.json` each run |

Common env: `PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`,
`PGS_HIER_BINNING=force`, `PS2X_SOUND=1` (`[snd-output] stream rate=48000` live on all runs),
`PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, vsync pad clock, empty mc0/mc1,
`PS2X_MISSING_FUNCTION_POLICY=stop`, `PS2X_VSYNC_RATE_LOG=1`,
`PS2X_FRAME_DUMP_DIR` + 30 s snapshotter. One mini slot each (slot 1 × 3; R2 waited one 30 s
lease cycle). Scratch `~/dev/ssx3-work/FR1` 2.2 GB (build 2.1 GB, runs 40 MB).

This build predates the RD1 vf0 rider fix (in `f3-fold` only): the RD1 player-rider collapse
applies here; no rider-rendering verdict was taken. No VR1 code is in `0ed07c4`, so per the
brief the VU1 dump was skipped and R2/R3 only record load+race.

## R1 full race — FINISHED 2nd, 04:18, results screen (bound=exit, tick 20033)

Route FR1-R1 (30 entries, `padscript armed n=30`): I26-FAST minus the final `38522:down:30000`
— verified byte-equal to I26-FAST without that entry. No inputs after the card taps. Zero FATAL.
The 60 s clock-stall stop rule never tripped (the clock advanced in every check). All 512×448, 2ND/2:

| Wall | Tick | Race clock | Prog | Speed | Screen |
|---|---|---|---|---|---|
| 30 s | 1543 | — | — | — | Rival card drawing in (mid-transition) |
| 60 s | 2021 | 00:00:06 | 1 % | — | Race start, EA Radio card |
| 90 s | 2476 | 00:00:13 | 3 % | 40 MPH | Riding |
| 210 s | 4331 | 00:00:44 | 14 % | 30 MPH | Open slope |
| 450 s | 6877 | 00:01:26 | 38 % | 18 MPH | RECOVER (a fall) |
| 510 s | 7617 | 00:01:39 | 43 % | 75 MPH | Ice-cave section |
| 660 s | 9585 | 00:02:11 | 53 % | 21 MPH | OFF LIMITS (off course, recovered) |
| 810 s | 11533 | 00:02:44 | 63 % | 61 MPH | Riding |
| 930 s | 13325 | 00:03:13 | 76 % | 44 MPH | BS Rail trick |
| 1050 s | 14727 | 00:03:37 | 85 % | 34 MPH | Riding |
| 1170 s | 16014 | 00:03:53 | 93 % | 17 MPH | Climbing |
| 1260 s | 16997 | 00:04:15 | 99 % | 28 MPH | Approaching the finish |
| 1290 s | 17391 | — (banner) | — | — | **"2nd place 04:18"**, HUD gone |
| 1320 s | 17798 | results | — | — | **Happiness – Race Single Event Results**: 1 Mac 03:13, 2 Zoe 04:18, "Sorry, you didn't win.", Next event / Restart / Replay / Records / Quit |
| 1410–1440 s | 19398–19826 | results | — | — | Results screen idle (no inputs left to give) |

End state: **finish + results screen, then a stop-policy abort** — at tick 20063 the guest took
an indirect call `JALR source=0x39e724 → target=0x6c058000` (`codeRegion=no`, vtable reads all
zero) and `PS2X_MISSING_FUNCTION_POLICY=stop` aborted the runner (`runner_rc=-6`, wall 1459.4 s).
First missing-function target ever seen past the finish; the E56 four RPC pairs are unchanged.

Coverage at vsync 16000: `targets=0`, `ids=0`, `pairs=4` — the E56 four, one hit each
(`80000211/1`, `237/0`, `534e44/0`, `80000006/ff`). At exit: `targets=1` (`0x6c058000`), same RPCs.

## R2 Snow Jam — replicates SJ1 (stop_file 298.4 s, tick 4309)

Route FR1-R2 = SJ1 R2 verbatim (92 entries, `padscript armed n=92`; verified byte-identical to
the SJ1 appendix). Zero FATAL.

| Wall | Tick | Screen (viewed) |
|---|---|---|
| 30 s | 1540 | Pre-race intro cutscene ("Press X to skip") |
| 60 s | 1829 | Start gate, countdown "2", 00:00:00, riders in gates |
| 240 s | 3657 | Race: 00:00:29, 6TH/6, 2 %, 16 MPH (brake-tail crawl, as in SJ1) |

Verdict: **loads and races** — the SJ1 R2 verdict replicates on the same tip with a
bit-identical runner. STOP-stopped once the gate → race chain was confirmed. Coverage at vsync
3000: `targets=0`, `ids=0`, `pairs=4` (E56 four). Sound live. VU1 dump skipped per the brief
(no VR1 code in this build); no code-image hashes observable.

## R3 Metro-City — loads and races, no save needed (stop_file 257.9 s, tick 4726)

Route FR1-R3 (29 entries, `padscript armed n=29`): I26-FAST shape with one Select-Event down
(Snow Jam → Metro-City), no tail — the rider rides untouched. Zero FATAL.

| Wall | Tick | Screen (viewed) |
|---|---|---|
| 30 s | 1521 | Pre-race intro cutscene ("Press X to skip") |
| 60 s | 1828 | Start gate, countdown "2", 00:00:00, riders in gates |
| 90 s | 2109 | Drop into the night city (skyscrapers, city lights), 6TH/6, 00:00:03, 1 % |
| 210 s | 3906 | Race: 00:00:33, 6TH/6, 5 %, 21 MPH, dark urban course |

Verdict: **Metro-City loads and races** from the menus with no save. STOP-stopped once the
gate → race chain was confirmed. Coverage at vsync 3000: `targets=0`, `ids=0`, `pairs=4`
(E56 four). Sound live. VU1 dump skipped per the brief; no code-image hashes observable.

## Exact commands

```sh
# Sources (E checkout untouched; FR1-local copies)
git clone ~/dev/PS2Recomp ~/dev/ssx3-work/FR1/PS2Recomp && checkout 0ed07c4 (detached, clean)
cp -a ~/dev/ssx3-work/F2/parallel-gs ~/dev/ssx3-work/FR1/parallel-gs  # 19d93b2, Granite 166ba21a, clean
git -C ~/dev/PS2Recomp ls-remote fork ssx3  # 0ed07c4 -> F3 had not pushed; brief says use 0ed07c4
# Build (GB8 flags; configure rc=0 52 s; build rc=0, 455 steps)
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=$PWD/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2EntryRunner
cp build/ps2xRuntime/ps2EntryRunner bin/runner-clean       # bd2290f4…88c66ad ×2
# Route byte-checks (driver vs ROUTES-FR1.md vs SJ1 appendix vs I26-FAST): all identical
# Boots (driver: local/research/FR1/fr1_boot.py)
python3 fr1_boot.py --route r1 --runner bin/runner-clean --label r1-full --wall 1800 --coverage-tick 16000
python3 fr1_boot.py --route r2 --runner bin/runner-clean --label r2-snowjam --wall 700 --coverage-tick 3000
python3 fr1_boot.py --route r3 --runner bin/runner-clean --label r3-metro --wall 700 --coverage-tick 3000
touch run/r2-snowjam/STOP run/r3-metro/STOP   # early stops once each verdict was determined
```

## Gaps and recommended next actions

- The post-results `JALR 0x39e724 → 0x6c058000` (tick 20063, idle results screen, no inputs) is a
  new E-lane lead: first missing-function target past any finish. Repro is the R1 route on
  `0ed07c4` to tick ~20063. Open: real game path (results-idle timer with an uninitialised
  function pointer?) vs runtime memory corruption; whether it reproduces with a non-stop
  missing-function policy and on the F3 fold (RD1's per-thread state fix is adjacent).
- R2's "Snow Jam" card text was not re-viewed this run (30 s cadence landed on the intro
  instead); the verdict rests on the route being byte-identical to SJ1 R2 (which showed the
  card), the 6-rider field, and a sunny gated course distinct from Happiness/Metro-City.
- No VU1 code-image hashes from any event (no VR1 code on `0ed07c4`): after the F4 fold,
  re-run Snow Jam + Metro-City + Happiness with `PS2X_VU1_RECOMP_DUMP` to cover their images.
- R1 vsync rates (~13–16/s in-race) are context, not speed numbers (frame-dump + sound on).
- Text in git: `fr1_boot.py` + `ROUTES-FR1.md` + this report. Scratch: `~/dev/ssx3-work/FR1`
  (2.2 GB).
- Recommended: mark the full-race-to-the-finish item done (finished + results observed);
  file the post-results JALR as an E-lane bug; keep the ROUTES.md "tuck" rename with the
  orchestrator (FR1 deliberately did not edit it).

## Orchestrator gate (2026-09-25)

**Pass: milestone.** I viewed `snap-017798t`: "Happiness – Race, Single Event Results", 1 Mac 03:13, 2
Zoe 04:18. **First stock race finished in our runtime**, with Snow Jam and Metro-City loading and racing.
Coverage clean through the race; past the results screen (tick 20063) an indirect call at `0x39e724`
(object-list virtual call through `*(obj+0x48)+0x8C`) jumps to `0x6c058000`: a runtime bug that a PS2
wouldn't hit. PF1 (Opus explorer) takes it. Route FR1-R1 (I26-FAST without the down-hold) becomes the
race-finish route; I26-FAST's ROUTES.md gets a note.
