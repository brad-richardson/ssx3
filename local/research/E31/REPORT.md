# E31 report — title → menu → race loading (Snow Jam stalls at 99%)

Brief `local/muse/prompts/E31.md`. Tables + receipts; the orchestrator decides.

| E31 | Receipt |
|---|---|
| Stop point | **Missions 1–3 executed; see e31j/k for the ending.** Mission 1: START is live (guest polls pad, stim delivered) but a latched all-buttons hold never leaves the title. Mission 2: `PS2X_PAD_SCRIPT` implemented, 461/461 green, committed on `e29-movie-bypass`. Scripted presses drive title → main menu → character → setup → peak → mode → event → rules → **race loading**. Mission 3: Snow Jam loading stalls at **99%** (live loop, zero CD reads, zero errors), but the Happiness Rival event loads fully to its pre-race screen — the stall is course/mode-specific, not generic. |
| Headline | **The stock game is playable through its front end on the E29 bypass build: every menu responds to scripted pad input. Snow Jam (Race) loading stalls at 99%, but Happiness (Rival Challenge) loads completely — e31k attempts the race start there.** |
| Checkpoint verdict | **Bars 1, 2 MET · Bars 3, 4 TBD by e31k.** |
| Fork | `e29-movie-bypass` = `96893da` (parent `e5ce086`, grandparent `3adc0478`); **one commit, never merged, never pushed**. Mainline `ssx3` untouched at `3adc0478` (verified at close). Worktree back on `ssx3`, clean except `ps2_log.txt`, at close. |
| Mutations / launches | 11 boots (a–k), 11 lease claims/releases, 0 pushes, 0 merges. One code change (pad script + tests, 489 insertions / 0 deletions). One extra build dir (`e31-noaggr-build`, flag experiment, kept). |
| Boots used | **11 of 12** (8 + 4 extended; 600 s wall authorized mid-lane). |

## Mission 1 — is START live? (e31a, no code change)

| Observable | e31a receipt |
|---|---|
| Script | `PS2X_PAD_STIM_AFTER=1 PS2X_PAD_STIM_WALLMIN=60`, wall 150 s, E29 binary `8c09eefb…84b8` |
| Armed / fired | `[padstim] armed after=1 wallmin=60s` (line 447); `[padstim] FIRED reads=2795 wall=60s getstate=0 portopens=2` (line 9394) |
| Delivery | `[padread]` ×48 (cap) `data2=0x00 data3=0x00 guestButtons=0xffff` on ports 0+1 |
| Guest polls pad? | **Yes**: 2 port opens, ~2795 reads/60 s (~46/s across 2 ports) at the title screen |
| Screen after press | **Title screen persists** (snap-62.58s through upload-latest @151 s all show the title) |
| Stub regime | 267 (title) → 288/299 after the fire; coincidental-or-caused, unresolved — moot after Mission 2 |
| Conclusion | START **delivered but ineffective as a latched all-buttons hold**. A press-and-release script is needed (Mission 2's premise). |

Key frame: `frames-e31a-1/snap/snap-0058.42s.png` (title, pre-fire), 183002 B,
`sha256=07861bc18a7ae9059114761cf7984b59eb6361b02dc6a9a35ed46078ab001a0c`.

## Mission 2 — pad script + navigation (e31b–e31e)

### The change (commit `96893da` on `e29-movie-bypass` only)

`PS2X_PAD_SCRIPT="t_ms:spec:hold_ms,..."`, DEV-ONLY, default off (unset =
one relaxed atomic check per read). Each entry presses buttons and/or drives
analog axes while `atMs <= nowMs < atMs + holdMs` (host-wall ms since first
pad call). Spec = `+`-joined button names (select/l3/r3/start/up/right/down/
left/l2/r2/l1/r1/triangle/circle/cross/square) and/or `lx/ly/rx/ry=0..255`.
Overlapping buttons accumulate; overlapping analog resolves last-wins per axis.
Markers: `[padscript] armed/press/release`. Malformed spec = ignored with a
warning (never half-applied). Test hooks (`setPadScriptForTest`,
`setPadScriptNowMsForTest`, `clearPadScriptForTest`) — production never calls them.

| File | Delta |
|---|---|
| `ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp` | +365 (script block next to the E2a stim + call site + hooks) |
| `ps2xRuntime/src/lib/Kernel/Stubs/Pad.h` | +34 (`PadScriptEntry`, `parsePadScript`, test hooks) |
| `ps2xTest/src/pad_input_tests.cpp` | +90 (3 tests) |

Suite (fork root, both flags off): **461/461** (458 + 3 new: parser/combos/
analog + rejection of 13 malformed specs; press/release schedule incl. overlap;
default-off). New binary `cec1c024…fb9`, 163530496 B, pinned by two matching
SHA reads separated in time. Aggressive-logs build (same flags as E29).

Two measured input facts that shaped every later script:
1. **The guest polls pad ~once per rendered frame**, and software-rendered 3D
   menus run at 1–3 fps — so 500–1000 ms holds MISSED windows (e31b i=3;
   e31c i=2,3,4,6). All e31d+ presses use 5000 ms holds: every one delivered.
2. **D-pad repeats slowly under holds** (~1 step/10 s at 16 fps); face buttons
   edge-trigger (no runaway confirms). Long holds are safe.

### Navigation timeline (input → screen, e31b + e31d, fast runs ~16 ticks/s)

| Wall | Input (delivered) | Screen reached (read off PNG) |
|---|---|---|
| 0–5 s | — | 3 movies skipped (`[MPEG:DEV-SKIP-MOVIE]` ×3) |
| ~10 s | — | "Checking for memory card (PS2) in MEMORY CARD slot 1…" |
| ~12–25 s | — | Title screen ("Press START button", blinks) |
| 25–30 s | start 5 s | Main Menu, Single Event highlighted (~39 s) |
| 45–60 s | cross 5 s | (menu settles ~60 s) Select Character, Zoe default (~70–77 s) |
| 60–95 s | cross 5 s | Setup Character: Zoe / Continue / Equip Gear / Rider Details / Music |
| 130 s | cross 5 s | Select Peak: Peak 1/2/3, Peak 1 highlighted (~145 s) |
| 165 s | cross 5 s | Select Mode: Peak 1 / Race / Freestyle (~181 s) |
| 200 s | cross 5 s | Select Event: Race / Snow Jam (Beginner) / Metro-City / Happiness (~214 s) |
| 225–228 s | cross 5 s | My Rules: Continue + 11 toggles, all Off (~233 s) |
| 255 s | cross 5 s | **Single Event – Race loading screen** (Peak 1 Snow Jam, Zoe) |

Pinned frames (all under `/Volumes/Extreme SSD/ps2recomp-spike/P1/run/`):

| Screen | Path | Bytes | SHA256 |
|---|---|---|---|
| Main Menu | frames-e31b-1/snap/snap-0062.46s.png | 115427 | 56044f8926d44e619e6c19cc67050df57f98c1c6f2469e3cb029258630adc8b1 |
| Select Character (Zoe) | frames-e31b-1/snap/snap-0076.97s.png | 119594 | 9d02e3f8e26ad5d84ab20123b3c9c00faa18559f4455f5e318d4cb1647694c32 |
| Setup Character | frames-e31b-1/upload-latest.png | 77318 | aa355b87a6f183b724f499a3d5cbeb5c750a007ab9d57cdde4d0a3699fe196b6 |
| Select Peak | frames-e31d-1/snap/snap-0145.40s.png | 115635 | 75cd42dbc1568d772fcbe456274506019dbc57d132062d96809096512af5b964 |
| Select Mode | frames-e31d-1/snap/snap-0180.78s.png | 84618 | bebb5a0b15a6494757d45fdc18768a06775b52c7c8115cad499aaf4a06892589 |
| Select Event (Snow Jam) | frames-e31d-1/snap/snap-0214.16s.png | 90739 | c6821ceb5d57d3ede716dc776ed2574e7c041c89afb60ac40ecd8a35835bf7eb |
| My Rules | frames-e31e-1/snap/snap-0232.75s.png | 97941 | 7cf3f4b0dbbc20c05205f74aefd7939e8c7878a62c187b4cb3a40c7fd89b7abe |

Notes: START@30 in e31b appeared inert but the e31c/d runs show start@25–30
reliably exits the title (e31b's START likely raced title readiness; kept in
all later scripts as the proven prefix). e31d ran out of script at event
select (down@245 wandered Snow Jam → Happiness); e31e reached My Rules;
e31f first reached race loading (38% @295 s) but was killed by the 2 GiB
function-trace cap (driver cap raised to 5 GiB after).

## Mission 3 — race start (e31f–e31k)

| Bar | Receipt |
|---|---|
| (1) Menu reached and responding | **MET** — 7 distinct menu screens, all responding (e31b/d/e) |
| (2) Race loading begins | **MET** — Snow Jam 0→99% (e31f/g/h); Happiness 0→100% (e31j) |
| (3) Race HUD visible | TBD by e31k (Happiness Rival Challenge pre-race screen reached in e31j) |
| (4) Timer/position advances ≥3 frames | TBD by e31k |

Snow Jam loading curve (read off PNG % text):

| Boot | 299 s | 399 s | 449 s | 469 s | 499 s | 551–596 s |
|---|---|---|---|---|---|---|
| e31f (killed @301 s by trace cap) | 38% | — | — | — | — | — |
| e31g (wall 551 s) | 32% | 43% | 79% | — | 99% | 99% (frozen 52 s) |
| e31h (wall 596 s) | — | — | — | 99% | — | 99% (frozen 127 s+) |

Pinned loading frames: 399 s/43% `4b049d2b…388ae40` (160979 B),
449 s/79% `32247eb2…2e2abb0` (166570 B), 499 s/99% `a127f798…66f0d8`
(160993 B), e31g-final 99% `bf150cd9…85ff323` (165014 B), e31h 469 s/99%
`c0985666…a7baff5` (164754 B), e31h 559 s/99% `d1be51d9…7b692e7` (165564 B),
e31h-final 99% `8d796d36…42a75f` (163047 B). Full paths in `frame-pins.json`.

## e31j: Happiness (Rival) loads fully — the stall is course/mode-specific

e31j intended Metro-City but the 12 s down-hold moved two steps (Snow Jam →
Happiness); cross@245 confirmed **Happiness** ("A battle against your rival").
Happiness loading: 24% @299 s → 86% @450 s → **complete ~499 s** (snap-size
transition 499–511 s) → **"Rival Challenge / Happiness - Race / Face off
against Mac in a Rival Challenge! / X Continue"** pre-race screen, held to the
595 s wall. No stall at any percentage. (Happiness is a Rival/Backcountry
event rather than the preferred plain race — Snow Jam itself still stalls.)

Pinned: Happiness 24% `frames-e31j-1/snap/snap-0298.96s.png`, 86%
`snap-0449.74s.png`, Rival Challenge `upload-latest.png` (SHAs in
`frame-pins.json`).

Open confound: Snow Jam = Race-mode event, Happiness = Rival-mode event. The
stall may be Race-mode-specific (e.g., AI racer init) rather than
Snow-Jam-specific — Metro-City (Race) would discriminate; no boots spent on it.

## The blocker: SNOW JAM race loading stalls at 99%

| Aspect | Receipt (e31g wall 551 s + e31h wall 596 s, same screen both boots) |
|---|---|
| Last frame | Loading screen, "99% Loading…", Peak 1 Snow Jam / Zoe (SHAs above) |
| Thread states (park @wall) | t1 Ready pc=0x423dc8 ra=0x377b6c (menu-idle PC); t5 Running pc=0x423de8 (render); t2/4/6 on normal semaphores 26/31/36; t3 Ready. **No thread in an HLE wait, no park.** |
| Last stub calls | 0x27D330 217849×/5 s (43.5k/s, single ra 0x27CF58) + 0x284B58 217847×/5 s (ra 0x27CF48); rest ≤21k/5 s. Periodic blip blocks (233→358 distinct every ~45 s) share the same top rows. |
| What the loop is | Generated-code read: 0x27CEA8 registers a node then fans out s2 children through the 30-slot allocator 0x27D330 (0x284B58 = its virtual method_B). No infinite loop inside — the caller re-invokes or s2 is huge. |
| Same pump mid-load? | **Yes**: mid-trace (1900 MB) and tail (20 MB) samples both dominated ~106–113k by the same pair — the loader works at a constant rate, then progress cliffs to zero. |
| CD reads | 692 reads/3146 sectors during 360–480 s; **ZERO reads 480–551 s** (last read line 31427). Early loading (0–40%) also needs no CD reads. |
| Errors/warnings | **None** in 35,756-line log (no unimplemented stub, FATAL, assert, exception) |
| Frames | Still presenting ~8/s, all distinct fnv (snowfall animates) — **live loop, not a hang** |
| DMA | Steady ~18k/120 ticks through the stall (EE DMA, not CD) |
| Input ruled out | down-hold ended 490 s, stall persists 490–596 s; insurance crosses @500/540 s ignored (loading screens take no input) |
| Stall duration | 99% held 52 s (e31g) and 127 s+ (e31h); combined ~3 min across two boots |

Interpretation: asset streaming completes (~95%, CD stops ~478 s), the loader
pump keeps running at full rate, but the last step — plausibly a big compute
job (course build) or a non-CD gate (timer/vsync/audio rendezvous) — never
finishes or never fires. The progress cliff (0.4%/s → 0%/s for 127 s) reads
more like a stall than a slow tail, but a >127 s compute tail is not ruled out.

## Experiment: no-aggressive-logs build (trace-is-the-bottleneck test)

Built `e31-noaggr-build` (E18 recipe, only `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`):
configure rc 0/144 s, FetchContent HEADs byte-identical to E29's, 7281
AppleDouble sidecars purged from `_deps` (brief-blessed) → re-glob 0/531,
build rc 0, 547 edges, 8m11s. Binary `ee11b25d…5c05bb`, 155978592 B;
`[padread]` absent, `[padscript]`/`[frame:dump]`/`[diag:*]` survive (verified
in source). Suite **461/461** with flags off.

e31i (wall 596 s, same script): **no faster** — 5421 frame ticks (9.1/s) vs
e31g's 6400 (11.6/s); and a 5 s hold MISSED (i=5, longer poll gaps at low
fps), diverging the chain into the freestyle event list. **Verdict: the
function trace is NOT the guest bottleneck; the bottleneck is per-frame CPU
cost (software GS).** The no-aggr binary is parked; all later boots use the
E29-dir binary.

## Boot table

| Boot | Binary | Wall/cap | Script summary | Furthest screen |
|---|---|---|---|---|
| e31a | E29 `8c09eefb` | 150 s | stim START@60 (latched) | Title (no advance) |
| e31b | `cec1c024` | 120 s | start@30 + 4×cross/15 s | Setup Character |
| e31c | `cec1c024` | 295 s | 7× 1 s holds + down 20 s | Setup Character (4 holds missed) |
| e31d | `cec1c024` | 298 s | 6× 5 s holds + down 40 s | Select Event (Snow Jam) |
| e31e | `cec1c024` | 298 s | +cross@225 | My Rules |
| e31f | `cec1c024` | 301 s | +cross@255; **killed by 2 GiB trace cap** | Loading 38% |
| e31g | `cec1c024` | 551 s | +down@290 200 s | Loading 99% (stuck 52 s) |
| e31h | `cec1c024` | 596 s | +cross@500/540, down@500 | Loading 99% (stuck 127 s) |
| e31i | noaggr `ee11b25d` | 596 s | same as e31h | Select Event (freestyle list; chain diverged) |
| e31j | `cec1c024` | 595 s | down 12 s → Happiness (2 steps, not 1) | Rival Challenge pre-race screen |
| e31k | `cec1c024` | 595 s | e31j prefix + cross@525/560 + down tuck | TBD |

## Exact commands

```
# Mission 1 (existing E29 binary, verified 8c09eefb…84b8 before boot)
python3 local/research/E31/e31_boot.py --label e31a --wall 150 --after 1 --wallmin 60 --snap 2.0
# Mission 2 edit+build+test (branch e29-movie-bypass; AppleDouble sidecars of edited files removed, checkout sidecar retained by rename)
cmake --build "/Volumes/Extreme SSD/ps2recomp-spike/e29-movie-bypass-build" -j2   # 13 edges, rc 0
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT .../e29-movie-bypass-build/ps2xTest/ps2x_tests  # 461/461 from fork root
# Navigation / race boots (driver: lease + progress caps + PNG snapshotter)
python3 local/research/E31/e31_boot.py --label e31b --wall 120 --no-stim --script "30000:start:500,..." --snap 2.0
# ... e31c–e31h same driver, scripts in boot-results.json; e31i adds --runner .../e31-noaggr-build/...
# No-aggr build: E18 configure-command.json with -B e31-noaggr-build and PS2X_ENABLE_AGRESSIVE_LOGS=OFF
```

## Gaps and recommendation

- The 99% stall is characterized but its gate is unnamed: the next lane needs
  the address/condition 0x27CEA8's driver waits on (watch the progress value?
  trace 27CEA8's caller and s2 across the 95→99% boundary on the aggr build,
  whose function trace is intact).
- Guest-speed variance is large and unexplained (title 23 ticks/s, 3D menus
  1–3/s, loading 8–17/s; ±40% boot-to-boot on the same screen). Host-wall
  scripts must keep ≥5 s holds and ≥25 s spacing.
- START vs cross at the title: START@30 sometimes inert, sometimes advances
  (readiness race); cross is the reliable title exit. Not investigated further.
- e31j result: TBD (fills in before commit).
