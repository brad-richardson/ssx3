# Named pad routes (PS2X_PAD_SCRIPT with PS2X_PAD_SCRIPT_CLOCK=vsync)

Times are guest ms (`vsyncTick x 100000/5994`); entries are `at_ms:button:hold_ms`.
Both routes need `PS2X_SKIP_MOVIE=1` (dev-only movie bypass) and an empty
memory card (no profile prompt), as in E32-inputs and the iOS bundle.

## I26-FAST (I26, 2026-09-23): title -> Happiness race, race HUD at tick ~1714

Checked on the Mac: i26v4a race at tick 1713, i26v5 at 1714 (same presses to the race).
Checked on the iOS 27 Simulator: two runs, race HUD at tick 1714, 59 s after launch.
Built by `make_route.py v5`. Each menu press lands 1.0-1.4 s (guest) after
its screen has settled. At the Rival Challenge card there are ten X taps, one
per second, with down released during each tap: **X is ignored while down
(tuck) is held**, which is why E33's route waited there. After the race
starts, the extra taps are jumps. Then a steady 30 s tuck.

```
10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000
```

| # | Guest tick | Button | Screen |
|---|---|---|---|
| 0 | 636 | start | Title, 66 ticks after "Press START button" shows (~570; START is ignored before that) |
| 1 | 766 | cross | Main Menu: Single Event |
| 2 | 884 | cross | Select Character: Zoe |
| 3 | 993 | cross | Setup Character: Continue |
| 4 | 1099 | cross | Select Peak: Peak 1 |
| 5 | 1185 | cross | Select Mode: Race |
| 6-7 | 1271, 1301 | down, down | Select Event: Snow Jam -> Metro-City -> Happiness |
| 8 | 1337 | cross | Select Event: Happiness |
| 9 | 1440 | cross | My Rules: Continue (then Loading, ~200 ticks) |
| 10-19 | 1709 + 60k | cross (+ down between taps) | Rival Challenge card (appears ~1640); the first tap starts the race |
| 20 | 2309 | down 30 s | Tuck |

## E33 (E33, 2026-09-21): the E-lane route, still the default in E-lane briefs

Race HUD at tick ~7100: the card tap is at 6793 (E50f), and the menus are
paced to the laptop-era rates.

```
10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000
```
