# IS1 — first real iOS speed numbers (iPad), play settings

Worker: muse. Brief: `local/muse/prompts/IS1.md` (iPad only; ≤8 launches).

**Status: done. 8/8 launches (1 probe + 7 legs: A B B2 A2 C D A3). iPad race on the
b97b241 build at F7 settings: 0.639–0.647× cool (A/A3), 0.601× heat-soaked (A2);
1× 0.720× (C); MTVU=0 0.503× (D); LAG ≈ neutral (B 0.646× / B2 0.625× vs A/A2/A3).
0 FATAL, 0 MTVU violations everywhere. iPad restored (deploy SKIP + 7 OKs, 6/6 saves
byte-identical, 0 procs). Hand back: the table; don't conclude.**

## Pins

| Item | Value |
| --- | --- |
| Fork `ssx3` (iOS build) | `b97b24117e1de632d7990cf2a244162412a9898d` (pushed, verified; VR4 SIMD FMAC on by default, VU0 recompile off) |
| paraLLEl-GS `ssx3` | `1b3a2948cc55e74f975e42b79d08983f31c2dbb6` (F7 pin kept, clean); Granite `166ba21a247a681903cc9d0bb6562fe50a554c85`; nested `vulkan-headers` `11d68983` (all 3 match F7's clone exactly) |
| Canonical codegen | `register_functions.cpp` ×2 match (`logs/codegen-sha.txt`); 9455 game sources |
| VU1 images (`vu1gen-ssx3`) | 7/7 SHAs; configure `VU1 recomp: 7 images`; linked symbols identical to F7 (17607 total / 1632 block / 14336 pair) |
| VU0 image (`vu0gen-ssx3`) | `vu0_40829a098c260b4f.cpp` `2652966b…` (canonical); configure `VU0 recomp: 1 images`; `VU0RecompImage` symbols linked (new vs F7; dormant, knobs off) |
| MoltenVK 1.4.2 device slice | staged `6cd58884…` = F5/F6/F7 pin |
| ELF / ISO staged | ×2 SHAs in `logs/device-elf-stage-sha.txt`, `logs/device-iso-stage-sha.txt` |
| Bundled env `local/research/IS1/ps2x.env` | `cffff3e8dcb03fe8…` = F7's `ps2x.env` byte-identical (`cmp` clean) |
| Device binary unsigned | `b1ee6bde…` (×2) |
| Device binary signed (installed) | `a6718f22…` (×2), 152,888,960 B; `codesign --verify --strict` passed |
| iPad bundle | `5B8817AF-…` (seq 2020; install URL matches probe bundle path) |
| iPad live Data container | `5205A1BD-…` |

## Method

- One device build from fork `b97b241`: F7's `build-install.sh` + `W`/`FORK_WT`/`PGS`/`PIN`/`ENVFILE`
  repointed and `-DPS2X_VU0_RECOMP_DIR` wired (VR3's CMake option). PGS/Granite/submodule pins kept
  at F7's so the only delta vs F7 iOS is the fork (+ linked-but-dormant VU0 image). Configure needed
  one retry: nested Granite submodules (`vulkan-headers`) weren't initialized on the first pass (G5).
- Launch: `ipad-run-stop.sh` (F7 `ipad-run.sh` lineage): per-leg fresh card (`mc-is1<leg>` under the
  live container; never Brad's `Documents/mc0`), I26-FAST re-armed per launch (route byte-checked vs
  the bundled env), `PS2X_VSYNC_RATE_LOG=1`, `PS2X_UNPACED=1`, `PS2X_DROP_SILENCE=1`, one screenshot
  at tick 2100, stop at first console line with tick ≥ 4500 (then terminate). Wall cap 600 s, console
  cap 7.5 MB. Host-timestamped console (`python3` filter, `start_epoch` in `run.txt`).
- Console overhead: no file-logging key exists in the runtime, so `--console` capture stays.
  `PS2X_DROP_SILENCE=1` kills the `[drop]` lines (596 in F7's run; 0 here). Remaining overhead: one
  `[ios-render]` stderr line per present (~58/s, unconditional on iOS, no knob) + the devicectl relay
  + the 5 s `[vsync-rate]` sampler + one screenshot hitch per leg (~t2100).
- Race rate = (4500−1714) ÷ (wall(t4500)−wall(t1714)): wall(t1714) interpolated between `[vsync-rate]`
  samples, wall(t4500) = first line at tick ≥ 4500 (the `[mtvu] threaded tick=4500` summary; C/D
  overshot to 4545/4591 on the 5 s sampler so wall(t4500) is interpolated there). Per-phase table uses
  F4 `phases.py` boundaries. Timestamps are host-side (relay jitter ~ms; negligible over ~70 s race).
- Order run: A B B2 A2 C D A3 (ABBA on the A/B LAG pair + A3 drift anchor; 120 s idle between
  A/B/B2/A2, 300 s before C and D, 180 s before A3; battery% read from each leg's screenshot; no
  thermal channel in devicectl).
- Leg envs (launch `-e` over the bundled F7 env): A/A2/A3 = none; B/B2 = `PS2X_MTVU_LAG=1`;
  C = `PS2X_PGS_SSAA=1 PS2X_PGS_HIRES_SCANOUT=0`; D = `PS2X_MTVU=0` (blocks stay on).

## Legs (STOP-capped race; per-5s + full tables in `logs/<leg>/rates.txt`)

| Leg | Env (beyond bundled) | End | Race (ticks→wall) | Race rate | `[mtvu]` jobs / violations | Batt% |
| --- | --- | --- | --- | --- | --- | --- |
| A | (none) | STOP 4500, 104 s | 1714→4500 / 72.8 s | 38.29/s = **0.639×** | 55490 / 0 | 78 |
| B | `PS2X_MTVU_LAG=1` | STOP 4500, 104 s | 1714→4500 / 72.0 s | 38.70/s = **0.646×** | 55513 / 0 | 76 |
| B2 | LAG | STOP 4500, 105 s | 1714→4500 / 74.4 s | 37.46/s = **0.625×** | 55513 / 0 | 75 |
| A2 | (none) | STOP 4500, 109 s | 1714→4500 / 77.4 s | 36.01/s = **0.601×** | 55513 / 0 | 75 |
| C | `SSAA=1 HIRES=0` | STOP 4545, 96 s | 1714→4500 / 64.5 s | 43.17/s = **0.720×** | threaded / 0 | 75 |
| D | `PS2X_MTVU=0` | STOP 4591, 127 s | 1714→4500 / 92.4 s | 30.14/s = **0.503×** | n/a (knob off) | 75 |
| A3 | (none) | STOP 4500, 105 s | 1714→4500 / 71.8 s | 38.78/s = **0.647×** | 55513 / 0 | 76 |

Ratios (hand-back, no verdict): B/A = 1.011×, B2/B = 0.968×, A/A2 = 1.063×, A3/A = 1.013×;
(B+B2)/(A+A2) = 1.025×; C vs (A+A3)/2 = 1.121×; D vs (A+A3)/2 = 0.782×.
Every threaded leg: `[mtvu] mode=threaded`, `violations=0`, 0 FATAL, `ssaa=4 hires_scanout=1
present_pipeline=1` (C: `ssaa=1 hires_scanout=0`), `ios bind … rc=0` (zero-copy kept).

Per-phase table (guest vsyncs/s; race row = raw to last sample — STOP-capped numbers above are primary):

| Phase | A | B | B2 | A2 | C | D | A3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| title/startup | 55.08 | 54.83 | 54.87 | 52.03 | 54.54 | 54.28 | 55.35 |
| main menu | 59.92 | 60.26 | 60.19 | 67.35* | 60.01 | 60.02 | 59.96 |
| Select Character | 59.92 | 60.26 | 60.19 | 67.35* | 60.01 | 60.02 | 59.96 |
| Setup Character / Peak | 60.00 | 59.92 | 59.85 | 60.51 | 59.98 | 59.98 | 59.95 |
| Select Mode / Event / My Rules | 60.06 | 60.05 | 60.05 | 59.93 | 60.06 | 60.02 | 60.08 |
| loading + Rival card | 46.46 | 49.67 | 49.46 | 47.34 | 47.54 | 42.94 | 47.54 |
| race (raw) | 38.57 | 38.83 | 37.80 | 36.13 | 43.30 | 30.33 | 38.96 |

\* A2 menu 67.35 = sparse-sample boundary artifact in a ~2 s phase (F7 G6 class), not a real rate.

Race per-5s (thermal shape; dip deepens/starts earlier A→A2, gone in C/D/A3 after long gaps):

| Leg | per-5s |
| --- | --- |
| A | 35.4 35.5 36.1 37.6 38.8 40.0 41.3 41.6 40.7 41.1 41.2 41.6 38.7 30.3 |
| B | 38.6 38.8 38.7 39.2 41.5 42.8 43.5 43.5 43.2 43.3 41.4 29.8 28.1 30.3 |
| B2 | 38.6 38.5 38.8 38.3 41.3 43.1 43.2 43.2 42.4 42.3 31.3 28.9 28.3 29.9 |
| A2 | 35.7 35.4 35.7 37.9 38.9 40.2 41.7 41.7 41.2 41.3 36.5 28.0 28.5 28.6 30.3 |
| C | 38.0 37.8 38.6 41.7 43.7 44.2 44.3 44.7 44.3 44.0 44.3 43.9 53.3† |
| D | 29.4 30.3 29.8 30.4 31.5 30.2 29.3 29.7 29.5 29.3 29.7 29.5 29.5 29.3 29.5 31.2 31.2 37.6† |
| A3 | 35.4 35.4 35.5 37.9 38.9 40.2 41.7 41.5 40.9 41.3 41.8 41.7 40.3 32.9 |

† C/D last values = short final intervals (STOP overshoot to 4545/4591); STOP-capped numbers primary.

## Shots (tick 2100, portrait-compat + pad v2; SELECT/START overlap known I28)

| Shot | Viewed verdict | Batt |
| --- | --- | --- |
| A `shot-t2100` (t2100, 10:22) | Race 2ND/2 00:00:07 1 %, rider down in spray, RECOVER meter, EA Radio "Andy Hunter / Exodus" | 78 % |
| B `shot-t2100` (t2126, 10:27) | 00:00:07, rider down, RECOVER, EA Radio "Ride / Deepsky / In Silico" (RNG differs from A — known class) | 76 % |
| B2 `shot-t2100` (t2100, 10:31) | 00:00:07, rider mid-trick upside down, board visible, EA Radio "Poor Leno - Silicon Soul Remix / Royksopp" (F6/F7 card) | 75 % |
| A2 `shot-t2100` (t2100, 10:36) | 00:00:08 1 %, 14 MPH, rider solid mid-carve, no crash (same-tick gameplay divergence, G2) | 75 % |
| C `shot-t2100` (t2105, 10:43) | 00:00:07 1 %, rider upright in distance mid-spray, EA card half off-screen left | 75 % |
| D `shot-t2100` (t2150, 10:53) | 00:00:07, rider down in spray cloud mid-crash, EA card cut off at left edge | 75 % |
| A3 `shot-t2100` (t2100, 11:01) | 00:00:07, rider upright mid-carve with spray, EA Radio "Glass Danse - Oakenfold Remix / The Faint" | 76 % |

## Budgets and gaps

- Builds: 1 iOS device (+1 configure retry, G5). Launches: 8/8 (1 probe + 7 legs; all ≤ 600 s wall).
  Scratch `~/dev/ssx3-work/IS1`: **4.9 GB**. Committed receipts `local/research/IS1/logs`: 396 KB
  (`run.txt`, launch env, `rates.txt`, `key-lines.txt` = console minus `[ios-render]` spam, console+shot
  SHAs; full console.logs + PNGs stay in scratch).
- iPhone: never targeted (no command used the iPhone UDID).
- End state: IS1 build (`a6718f22…`, bundled env = F7's) installed on the iPad, deploy SKIP + 7 OKs,
  6/6 saves byte-identical (`cmp` vs `E55D16/mc0`), 0 procs. Fresh cards `mc-is1*` remain in Documents
  (no devicectl delete; F7's `mc-f7` precedent); Brad's `mc0` untouched (all legs used `-e PS2X_MC_ROOT`).
- Gaps:
  - G1. Thermal drift: A→A2 falls 38.29→36.01 with the late-race dip deepening/starting earlier each
    leg; A3 recovers to 38.78 after the lighter C/D legs + long gaps. Rate comparisons across different
    heat states carry this drift; ABBA + A3 bracket it but single legs (C, D) stand alone.
  - G2. Same-tick gameplay divergence: A2 rides while A/B2 crash at t2100; EA-Radio cards differ
    across legs (known device RNG divergence class, F6 G3/F7 G5). Rates unaffected.
  - G3. `[mtvu]` jobs=55490 on A vs 55513 on B/B2/A2/A3 (Odin: 55501). Unchased.
  - G4. Battery/thermal not readable via devicectl (battery% from screenshots only: 78→75→76,
    always charging). No thermal API; gaps recorded instead (120/120/120/300/300/180 s).
  - G5. First configure failed (empty `vulkan-headers` nested submodule; script's `rg` checks passed
    anyway so the failure surfaced at build). Fixed with recursive submodule init + clean reconfigure;
    pins verified identical to F7's clone afterwards.
  - G6. A3 reused leg A's env/card (`mc-is1a`, non-fresh) as the drift anchor. Legit for an anchor;
    recorded so nobody reads A3 as an independent fresh-card repeat.
  - G7. C/D STOP overshoot (4545/4591; 5 s sampler granularity on the stop poll). STOP-capped rates
    are interpolated and primary.

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/IS1/PS2Recomp b97b241
git clone ~/dev/parallel-gs ~/dev/ssx3-work/IS1/parallel-gs  # + checkout 1b3a294, submodules recursive
bash ~/dev/ssx3-work/IS1/ios/build-install.sh preflight configure_device build_device stage_device sign install_ipad
bash local/research/I31/deploy-ios.sh ipad; bash ~/dev/ssx3-work/IS1/ios/ipad-probe.sh
python3 ~/dev/ssx3-work/IS1/ios/mkemu.py  # per-leg env JSONs (fresh cards)
bash ~/dev/ssx3-work/IS1/ios/ipad-run-stop.sh ~/dev/ssx3-work/IS1/ios/leg-<L> ~/dev/ssx3-work/IS1/ios/run-env-<L>.json "2100" 4500
python3 ~/dev/ssx3-work/IS1/ios/is1_rates.py ~/dev/ssx3-work/IS1/ios/leg-<L>
bash local/research/I31/deploy-ios.sh ipad  # restore; saves cmp'd byte-identical after pull
```

## Orchestrator gate (2026-09-26)

**Pass as the first iPad speed numbers, labelled provisional:** release build, but the console relay stays on
(the unconditional per-present `[ios-render]` stderr line + devicectl relay; no file-logging key). iPad Air 11" M2,
fork `b97b241`, F7 bundled env (4× SSAA + hi-res + pipelined + zero-copy, MTVU + blocks): race **0.639 / 0.647×**
cool (A/A3), 0.601× heat-soaked (A2); 1× resolution **0.720×**; MTVU off 0.503× (MTVU = +28 % on iOS). LAG
(B/B2 vs A/A2) +2.5 % sits inside the thermal drift: not adopted on iOS for now. 0 FATAL, 0 violations; Brad's
`mc0` byte-identical. Follow-ups (todo): gate the `[ios-render]` per-present line behind a knob so iOS numbers can be
clean; G3 jobs 55490 vs 55513 unchased (one leg). The iPad now goes to IP1 (full-screen build).
