# I26: no pink startup, fast auto-route, 4:3 bilinear presentation, virtual controls

- Date: 2026-09-23. Brief: `local/muse/prompts/I26.md`, plus the
  orchestrator's scope addition (G46 §4: 4:3 aspect and bilinear filtering).
- Worker: Claude (Opus pane). Mac mini (M5 Pro).
- Fork worktree `~/dev/ssx3-work/I26/PS2Recomp`, local branch `i26-qol` =
  `i25-ios` (`eac6cba` + 2) + 2 commits. The fork's `ssx3` had not moved, so no
  rebase was needed. Not pushed.
- **iPhone: the new build is installed, not launched** (Brad's rule).
  - Signed binary `fe96d114…` (read twice, both match); unsigned build
    output `848b06aa…`, 357,255,864 B.
  - Profile `f0793278-…`; `logs/install-iphone.log`.

## Headlines

| Item | Result |
|---|---|
| Pink startup | **Fixed.** The fallback frame was `ff00fe` (magenta) and is now `000000` on every platform. `PS2X_FALLBACK_MAGENTA=1` (dev only) restores magenta. On the Simulator the first shots are black. Separate commit `73b8b3a`; it stands alone (601/601), so it can go to `ssx3`. |
| Fast route | **Title → race HUD is 21 % of today's time in guest time and 31 % on the Simulator wall clock, not the 10 % target.** The route is named I26-FAST in `ROUTES.md` and is in the bundle's `ps2x.env`. The 10 % target is below what the game allows with a ≥1 s margin (§Floor). |
| Why E33 waited 45 s at the Rival card | The card **ignores X while down (tuck) is held.** The E33 route pressed both at once, so the timing only worked by accident. I26-FAST releases down during each X tap: the first tap is taken at once (race HUD 4 ticks later). |
| Validation | Mac: two runs reached the race at tick **1713 and 1714** (i26v4a, i26v5; the same presses up to the race). Simulator: two runs, race HUD 59 s after launch in both. The race advances (00:00:13 by t=110 s). |
| 4:3 + bilinear (scope addition) | Done on all platforms: 4:3 display aspect by default (`PS2X_ASPECT=native` keeps 8:7); bilinear unless the scale is a whole number on both axes (`PS2X_PRESENT_FILTER=point|bilinear`). Select Mode before and after: `shots/i26-select-mode-before-after-crop.jpg`. |
| Virtual controls | First cut works on the Simulator. Synthetic touches drove START → Main Menu → cross → Select Character → cross → Setup Character with auto-route off. Settings toggle added. |
| Host suite | **608/608** at `8a357ac`: 600 before, plus 1 fallback, 2 presentation-geometry and 5 virtual-pad tests. |

## 1. Route timing

Guest ticks come from the frame-dump `tick` of the snapshots, every 0.5 s wall
(`settle.py`). A screen "settles" at the first snapshot after which the
picture stays within a mean grey difference of 6 of its final state until the
press. That is stricter than the screen's first frame (the first
frame-hash change after the previous press).

### Before (E33 route; boot i26base, race tick from E50f)

| Screen | Settled at tick | E33 press tick | Wait (guest s) |
|---|---|---|---|
| Title ("Press START button" shows at ~560) | 560 | 620 | 1.0 |
| Main Menu | 684 | 1237 | 9.2 |
| Select Character | 1276 | 1390 | 1.9 |
| Setup Character | 1431 | 1438 | 0.1 |
| Select Peak | 1466 | 1851 | 6.4 |
| Select Mode | 1860 | 2371 | 8.5 |
| Select Event (down held 4.2 s) | 2378 | 2831 | 7.6 |
| Select Event: Happiness | 2833 | 3323 | 8.2 |
| My Rules | 3360 | 3891 | 8.9 |
| Loading → Rival Challenge card | 4094 | 6793 | **45.0** |
| Race HUD | ~7100 (E50f: after 7068, by 7131) | | |

i26base stopped at its 420 s cap at tick 6810: the host was shared with
another lane's runner and my iOS build. Its ticks match E50f press for press;
the race tick is from E50f (`E50/run/boot-e50f-1.log`, same route).

### After (I26-FAST; boot i26v5, same as i26v4a up to the race)

| Screen | Settled at tick | Press tick | Wait (guest s) |
|---|---|---|---|
| Title prompt | ~570 | 636 | 1.1 |
| Main Menu | 708 | 766 | 0.97 (first frame ~690: 1.3) |
| Select Character | 802 | 884 | 1.4 |
| Setup Character | 926 | 993 | 1.1 |
| Select Peak | 1015 | 1099 | 1.4 |
| Select Mode | 1110 | 1185 | 1.3 |
| Select Event | 1189 | 1271 / 1301 (down ×2) / 1337 (cross) | 1.4 |
| My Rules | 1371 | 1440 | 1.2 |
| Rival Challenge card | 1636 | 1709 (first X tap) | 1.2 |
| **Race HUD 00:00:00** | **1714** (i26v4a: 1713) | | |

On the strict "settled" measure, the Main Menu press lands 58 ticks
(0.97 s) after the menu settles. Measured from the menu's first frame it is
≥1.3 s. The snapshot grid is ~10–20 ticks, so "settled" is an upper bound on
the true settle time.

### Totals

| Measure | E33 | I26-FAST | Ratio |
|---|---|---|---|
| Guest, title logo (tick 264) → race HUD | ~6840 ticks (114 s) | 1450 ticks (24.2 s) | **21 %** |
| Guest, "Press START" (~565) → race HUD | ~6535 ticks (109 s) | 1144 ticks (19.1 s) | 17.5 % |
| Simulator wall, logo → race (DIAGNOSTIC rate) | 174.4 s (I25 run F) | 54.4 / 53.8 s (two runs) | 31 % |
| Simulator wall, launch → race | ~180 s | 59.3 / 58.8 s | 33 % |

Simulator wall times are interpolated from the `[vsync-rate]` lines (5 s
apart). They are not speed numbers: the menus run at 0.3–0.55× there, while the
old Rival wait ran at 0.91×, so the wall ratio is worse than the guest ratio.

### Floor: why 10 % isn't reachable with a 1 s margin

Irreducible guest time from the title logo:

| Part | Ticks |
|---|---|
| Title intro before START is accepted (fixed; 264 → ~565) | ~300 |
| Menu transitions (press → next screen settled), 9 screens | ~430 |
| Loading after My Rules | ~200 |
| ≥1 s margin × 10 screens | 600 |
| **Total** | **~1530** |
| 10 % of today's time | ~685 |

I26-FAST is already slightly under this estimate (1450), because some
settles overlap the margin. Getting to ~10 % would need margins of ~0.2 s,
which the brief rules out.

### Probe history (6 Mac boots, all rc 0 at their wall cap, lease slot each)

| Boot | Route | Finding |
|---|---|---|
| i26base | E33 | Baseline table above |
| i26v1 | Presses at logo + 1.1 s | The title ignores START until "Press START button" (~570). The presses fell one screen early; the route broke at Select Peak (landed on locked Peak 2) |
| i26v2 | Title fixed; screen order Main → Char → Setup → Peak → Mode → Event → Rules | All menus correct (Happiness selected), but the card ignored 20 taps (1709–2849) with down held throughout |
| i26v3a | 50 taps (to 4649), down held | Still ignored. Down-held and "absolute load tick" were both open |
| i26v4a | X tap with down released, down between taps | **First tap taken; race at 1713**, advancing 00:00:38 by 4003. Down-held blocking confirmed |
| i26v5 | Final I26-FAST (v4 with 10 taps, then a 30 s tuck) | Race at 1714; all presses as tabled |

## 2. Presentation (scope addition, G46 §4)

- `ps2_present_geometry.h`:
  - `presentRect()` fits the largest 4:3 rectangle in the window (or keeps
    the uniform pixel-aspect scale under `PS2X_ASPECT=native`).
  - `useBilinear()` is on unless both axis scales, in drawable pixels, are
    whole numbers.
- The presenter calls `SetTextureFilter` only when the choice changes.
- Simulator Select Mode shots (full frames `shots/i26-1-…` and `i26-2-…`):
  - Before: 8:7 with point sampling.
  - After: 4:3 with bilinear. The picture is 536×402 pt instead of 459×402.
  - `shots/i26-select-mode-before-after-crop.jpg` shows the same text region
    at native resolution. "Race / Freestyle" is ~17 % wider, and strokes are
    more even (the "F", "y" and "e" stems no longer alternate).
- **Observation (not changed): the app renders at point resolution.** The
  `[ios-window] window=874x402 drawable=874x402` line shows that raylib draws
  at 1× and iOS then upscales ×3. So on the device the frame is resampled
  twice: 448 → 402 by us, then ×3 by the system. G46's ×2.946 model assumed
  a native-pixel drawable.
  - A HiDPI drawable (`FLAG_WINDOW_HIGHDPI` / `SDL_WINDOW_ALLOW_HIGHDPI`)
    would give the text 3× more pixels.
  - That is the larger font lever, and a candidate follow-up. It isn't in
    this brief.

## 3. Virtual controls (first cut)

- **Layout** (`ps2_virtual_pad.h`):
  - Scaled by the window height.
  - D-pad (8-way by angle, with a dead zone) bottom-left; face buttons
    bottom-right; L2/L1 and R1/R2 in the top corners; Select/Start at the
    bottom inner corners.
  - All inside the 4:3 pillarbox on a 19.5:9 phone (clusters end at 0.405 ×
    height).
  - Semi-transparent. A pressed button brightens.
  - Face symbols are drawn in PS colours; shoulders and Start/Select are text.
- **Input:**
  - iOS reads SDL's finger state each frame. raylib's own touch array
    overwrites point 0 with the mouse position every poll, so it can't track
    held touches.
  - Pressed bits go through `liveMask()` into `PSPadBackend::readState`, as
    part of the keyboard/gamepad union. `Pad.cpp` then applies
    `PS2X_PAD_SCRIPT` on top, as before: a script press can't be undone by
    touch.
- **On/off:**
  - On by default on iOS: Settings → SSX3 PS2X → Touch → **Virtual
    controls**; off sets `PS2X_VIRTUAL_PAD=0`.
  - Desktop: dev only, with `PS2X_VIRTUAL_PAD=1` (the mouse is the finger).
- **Hide rule, a deviation from the brief ("hidden while a controller is
  connected"):**
  - The iOS Simulator reports an always-connected device named "Gamepad"
    with nothing attached to the Mac (`logs/sim-console-padname.log.gz`).
    Under "connected" the overlay vanished a second after launch
    (`logs/sim-console-after.log.gz`).
  - The overlay now hides **once a connected controller is used** (any
    button, or a stick past half-way), and returns when it disconnects.
  - One `[vpad]` stderr line per state change.
- **Simulator check.** This Mac has no Simulator.app (Xcode ships only the
  CoreSimulator runtime), so mouse clicks can't be injected.
  - Instead, the dev-only `PS2X_VPAD_TEST_TOUCHES=tick:fx:fy:hold,…` feeds
    synthetic touches through the same hit test.
  - Run `vpad`: auto-route off (`PS2X_PAD_SCRIPT=` from the launcher),
    touches START@640, cross@780, cross@900.
  - Result: title → Main Menu → Select Character → Setup Character
    (`shots/i26-4-…` title with the overlay, `shots/i26-3-…` cross drawn
    pressed).
  - The real UIKit → SDL finger path isn't exercised (gap V1).
- The layout was not hand-tuned (per the brief).

## Diff (fork `i26-qol`, local only)

| Commit | What |
|---|---|
| `73b8b3a` | Black presentation fallback (`ps2_present_fallback.h`, test). Candidate for `ssx3`. |
| `8a357ac` | 4:3 + bilinear presenter (`ps2_present_geometry.h`, tests)<br>Virtual pad (`ps2_virtual_pad.h`, tests, `ps2_pad.cpp` union, draw + touch glue in `ps2_runtime.cpp` / `ps2_ios_runtime.mm`)<br>Settings.bundle "Virtual controls"<br>`[vpad]` log; dev-only test touches |

- `logs/i26-qol-branch.diff` is the full diff against `eac6cba`;
  `logs/i26-only-diffstat.txt` has the I26 commits only (11 + 5 files).
- `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` is empty.
- Desktop behaviour changes:
  - the black fallback;
  - 4:3 + bilinear presentation by default (E-lane frame dumps are guest
    frames, so they're unaffected);
  - the virtual pad only with `PS2X_VIRTUAL_PAD=1`.

## How to use it (for Brad)

1. Open **SSX3 PS2X** on the iPhone.
   - Startup is now black, not pink.
   - With auto-route on (default), it plays itself to the Happiness race in
     about **1 minute** on the Mac's Simulator (it was ~3 minutes). Phone
     speed isn't measured yet.
2. The picture is now 4:3 with smooth scaling, so text should look less
   uneven.
3. **Touch controls:** on-screen D-pad, △○×□, L1/L2/R1/R2, Start/Select in the
   black side bars.
   - Multi-touch works (D-pad + a button together).
   - They hide once you use a paired controller.
   - Turn them off in Settings → SSX3 PS2X → Virtual controls, then relaunch.
4. **To play yourself:** Settings → SSX3 PS2X → Auto-route off, relaunch,
   then press START on the touch pad.
   - With auto-route on, the script's presses still happen on top of yours.
5. As before, `Files → On My iPhone → SSX3 PS2X → ps2x.env` can override
   options:
   - `PS2X_ASPECT=native` for the old 8:7;
   - `PS2X_PRESENT_FILTER=point` for sharp pixels;
   - `PS2X_VIRTUAL_PAD=0` to turn the touch controls off.

## Gaps

| # | Gap | Next step |
|---|---|---|
| R1 | The target (≤10 % of today's time) is not met: 21 % guest, 31 % Simulator wall. Floor analysis above. | Orchestrator decides: accept, or allow sub-second margins |
| R2 | Card retries (10 × 1 s) assume the card is ready within ~10 s of appearing on slower hosts. The Mac and Simulator took the first tap. Device timing unmeasured (iPhone install-only). | iPad run when it's unlocked |
| V1 | Real touches (UIKit → SDL fingers) not exercised: no Simulator GUI here, iPhone install-only | iPad run, or Brad's first use; the `[vpad]` log line shows the state |
| V2 | The Simulator's phantom "Gamepad" is unexplained. The hide rule works around it. | Check on the iPad: a phantom there would show as `pad_in_use=0` with a name |
| P1 | Presentation is at point resolution (drawable = window points). The bilinear gain is modest; HiDPI would matter more. | Small follow-up brief (HiDPI drawable + retest the fonts) |
| B1 | i26base hit its 420 s wall cap before the race (shared host); the race tick is from E50f (same route) | none needed |

## Recommendation (the orchestrator decides)

1. Take `73b8b3a` (pink fix) to `ssx3` now.
2. Accept I26-FAST for the iOS/Android check-in bundles. Consider it for the
   E-lane: it reaches the race 5,400 ticks sooner, but E-lane briefs keep E33
   until told otherwise.
3. Note for every lane: **X at the Rival card needs down released**.
4. HiDPI drawable as a small follow-up, for the fonts.

## Budget and receipts

- Mac boots: 6 of 6 (i26base, v1, v2, v3a, v4a, v5).
- Simulator runs: 4 (before, after, padname, vpad), each with a lease slot.
- Builds:
  - Mac: 1 full + 6 incremental.
  - Simulator: 1 full + 4 incremental.
  - Device: 1 full.
- About 2 h of the 6 h box.
- Disk: `~/dev/ssx3-work/I26` is 6.3 GB at close (cap 10). The staged
  bundles were removed; `build-install.sh stage` recreates them.
  `disk_budget.sh`: 80.2 / 200 GB.
- Leases were released after every run; the Simulator was shut down.
- Scripts:
  - `i26_boot.py` (Mac boot);
  - `make_route.py` (routes v1–v5);
  - `settle.py`, `snap_screens.py`, `sheet.py` (screen timing);
  - `build-install.sh`, `sim-run.sh` (I25's scripts, pointed at I26);
  - `simtap.swift` (unused: no Simulator GUI).
- `logs/`:
  - `settle-*`, `padscript-*`, `screens-*`, `*-result.json` per boot;
  - Simulator consoles (gz);
  - host tests (summary + gz);
  - branch diff and log;
  - `install-iphone.log`.
- Mac runner at HEAD `eef38afb…`. The route boots used `a002c674…`
  (i26base–i26v4a) and the presenter build (i26v5); the guest side is
  identical.
