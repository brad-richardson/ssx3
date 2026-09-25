# I32 — virtual analog stick (left), D-pad (right)

Worker: Muse. Brief: `local/muse/prompts/I32.md` (Parts 1 + 2).
Fork worktree `~/dev/ssx3-work/I32/PS2Recomp`, local branch `i32-controls` =
fork `ssx3` `f949ff0` + 1 commit (`71c952e`). No push. Part 1 gated PASS,
Brad approved the layout; Part 2 below.

Headline: the left D-pad is now a floating analog stick (touch-down
anchors, drag deflects, release recentres; ~10% dead zone; drawn base +
knob) driving the left-stick pad bytes, and the D-pad moved to the right
above the face buttons. Simulator Release build runs I26-FAST to the race
with the new overlay; injected stick vector `(1,0)` lands in the pad bytes
as `lx=0xff ly=0x80`. Host suite 601/601.

## Brief steps

| Step | Result | Receipt |
| --- | --- | --- |
| 1. Overlay code cited | Layout + hit test `ps2_virtual_pad.h`; button union + stick bytes `ps2_pad.cpp:141-171`; draw `drawVirtualPad` + touch glue `virtualPadTouches` + main-loop publish `ps2_runtime.cpp:639-700,3850-3890`; UIKit→SDL fingers `touchPoints` `ps2_ios_runtime.mm:188` | fork commit `71c952e` |
| 2. Floating stick left | `updateStick` state machine (anchor/track/re-anchor/release), dead zone 10%, clamped to unit circle; `stickBytes` → `liveStick()` → `data[6..7]`; left D-pad removed | `host-suite-vpad.txt`, `stick-key-lines.txt` |
| 3. D-pad right, buttons stay | D-pad disc (right, above triangle, clear of R1/R2 drawn + hit); face/shoulders/Select/Start untouched; multi-touch via independent button mask + stick candidates | `shot-*.png` (viewed), layout test |
| 4. Unit test + suite | 5 new vpad Runs (mapping, dead zone, clamp, track/re-anchor/button-exclusion, backend union, env parse); Release suite from worktree root 601/601/0; runner-dir diff empty | `host-suite-vpad.txt`, `source-pin.txt` |
| 5. Sim screenshots + stick log | Title, Select Character, Setup, Select Peak, 2× race with overlay; deflected-knob title shot; `[vpad] stick pad bytes lx=0xff ly=0x80` | frames in `~/dev/ssx3-work/I32/run-{sim,stick,select2}/`, SHAs `frame-sha-read{1,2}.txt` |

## Layout decisions

- Stick zone: touches with `x < w/2` that press no button (checked through
  the same `pressedMask`, so L1/L2/Select + stick multi-touch works).
  Tracking needs no finger IDs: a zone touch within 2.5× stick radius of
  the anchor drives; a jump further out re-anchors (new touch-down); no
  zone touch releases to centre.
- Stick bytes round (`128 + lround(v*127)`) rather than truncate like the
  gamepad path, so a full drag lands exactly on `0xFF`/`0x01`.
- D-pad: disc R `0.095u` at `(w-0.205u, 0.285u)` — drawn 8pt clear of
  R1/R2 above and triangle below; hit disc (1.15×) clears every drawn
  button (asserted in the suite). Disc diameter 76pt ≥ 44pt.
- While the overlay shows, the stick (centred when untouched) overrides
  `data[6..7]`; hidden behind a used controller it stores
  `kStickNoOverride` and the gamepad bytes pass through. `PS2X_PAD_SCRIPT`
  still applies on top of both.
- DEV-ONLY `PS2X_VPAD_TEST_STICK="lx,ly"` injects a raw vector (no dead
  zone) and arms the one-line-per-distinct-value `[vpad] stick pad bytes`
  proof log in `readState`; unset everywhere else, production stays quiet.

## Viewed frames (SHA-256 matched on two reads; full SHAs in `frame-sha-read1.txt`)

`~/dev/ssx3-work/I32/` (Simulator 2622×1206):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `run-sim/shot-0010s.png` (tick 271) | Title logo + EA copyright; stick rest ring left, D-pad right | `cf9c06ce…38ad76` |
| `run-sim/shot-0030s.png` (tick 865) | Setup Character, Zoe, Continue/Equip Gear/Rider Details/Music | `38f34f65…1855327` |
| `run-sim/shot-0035s.png` (tick 975) | Select Peak, Peak 1 (2/3 locked), Peak Access card | `65f8bbbf…22f63091` |
| `run-sim/shot-0100s.png` (tick 1865) | Race 2ND/2, 00:00:02, 0%, EA Radio "Emerge - Junkie XL Remix / Fischerspooner" | `2c1660d3…5e8eb9c6` |
| `run-sim/shot-0160s.png` (tick 2221) | Race 2ND/2, 00:00:08, 2%, 16 MPH; race advances | `70332770…e6f05456` |
| `run-stick/shot-0020s.png` (tick 538) | Title, auto-route off; stick knob deflected full-right at rest | `c4e7ba7c…42049d1e99` |
| `run-select2/shot-select.png` (tick 802) | Select Character, Zoe, stats bars, rider silhouettes | `d5345f93…73bc1d` |

Race composition matches I30 (dark foreground + lit slope + EA Radio
card); the radio track varies run to run (I30 G5).

## Stick proof (run-stick, `stick-console.log`)

```
[ios-env] launcher kept PS2X_PAD_SCRIPT          (empty: auto-route off)
[ios-env] launcher kept PS2X_VPAD_TEST_STICK
[vpad] test stick lx=1.000 ly=0.000
[vpad] on=1 pad_in_use=0 first_pad=-1 name="" -> overlay shown
[vpad] stick pad bytes lx=0xff ly=0x80           (exactly the injected bytes)
```

One stick-bytes line total (log-on-change). Script run: 31-press script
armed, i=0..27 fired (i=28..30 past the 160 s wall cap — the guest ran
slower under host load, last tick 2221 vs I30's 2382); race HUD reached
and advancing.

## Suite

Release from the worktree root (`-DCMAKE_BUILD_TYPE=Release`,
`PS2X_BUILD_STUDIO=OFF`, no codegen): rc=0, **601/601/0** (I26-era count
was 608; the tip suite differs). All 10 Ps2VirtualPad Runs pass, the 5
I26 ones unmodified. Observation: a default (asserts-on) build aborts in
`PS2SifDma` (`assertExecutor`, EeScheduler thread check) before reaching
the vpad suites; neither the crashing TU nor EeScheduler references any
I32-touched file (0 hits), so it is pre-existing/environmental — lanes
run Release. Full logs in scratch (`host-tests-release.log`,
`host-tests.log`).

## Exact commands and pins

```sh
git -C ~/dev/PS2Recomp fetch fork ssx3
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/I32/PS2Recomp fork/ssx3
git -C ~/dev/ssx3-work/I32/PS2Recomp checkout -b i32-controls  # + commit 71c952e
cmake -S . -B ~/dev/ssx3-work/I32/host-test -DPS2X_BUILD_STUDIO=OFF   # then Release rebuild
~/dev/ssx3-work/I32/host-test/ps2xTest/ps2x_tests   # from the worktree root
bash ~/dev/ssx3-work/I32/build-install.sh preflight configure_sim build_sim stage_sim sim_install
bash ~/dev/ssx3-work/I32/sim-run.sh         # slot 1, 160 s, 5 shots
bash ~/dev/ssx3-work/I32/sim-stick-run.sh   # slot 1, stick proof
bash ~/dev/ssx3-work/I32/sim-select2-run.sh # slot 1, tick-triggered Select Character
```

Pins: fork base `f949ff0` (= `fork/ssx3` at fetch) + `71c952e`;
bundled env identical to I30 (`cmp` clean); ios-deps reused read-only —
`dep-shas.txt` diff vs I30's is empty; raylib `c1ab645c`, patch
idempotent ("already applied", post SHA `df666c29…`); codegen
`register_functions.cpp` + ELF `SLUS_207.72` + ISO pinned in
`codegen-sha.txt`, `elf/iso-input-sha.txt` (stage copies `cmp`-equal).
Sim binary `b87868e2…` (`-O3 -DNDEBUG`, `sim-flags-evidence.txt`).

## Budget

1 Simulator build; 4 Simulator runs (160 s + 22 s + 31 s + 33 s, one
lease slot each, all released; the Simulator was shut down after).
I32 scratch 4.7 GB; global ssx3 use 69.4 / 200 GB at build time.
Elapsed ~75 min of the 90 min Part 1 box.

## Part 2 — device build, iPad test, iPhone install-only

Device build from `71c952e` (no new fork commits): Release
`-O3 -DNDEBUG` (`device-flags-evidence.txt`), signed binary `d6735a0e…`
(`codesign --verify --strict` passed). Bundled env unchanged from Part 1
(sound on, `PS2X_MC_ROOT=${DOCUMENTS}/mc0`).

| Step | Result | Receipt |
| --- | --- | --- |
| iPad install | exit 0 (seq 1844); deploy re-applied: SKIP mc0 + ps2x.env, all 7 sizes OK | `install-ipad.log`, `deploy-ipad.txt` |
| iPad launch (one) | 198 s, 5 tick-screenshots, process terminated after; race reached (tick 2140), advancing | `ipad-run.txt`, `ipad-console.log`, frames below |
| Stick on iPad | `[vpad] stick pad bytes lx=0xff ly=0x80` (exactly once); knob deflected in shots; route+race completed with stick held | `ipad-key-lines.txt` |
| D-pad on iPad | down-hold armed through the tested hit-test path (log); game-visible tuck not isolated (portrait crop hides MPH/posture) | `ipad-key-lines.txt`, gap G8 |
| iPhone | install exit 0 (seq 4704); deploy SKIP/OK; **never launched** (no process command) | `install-iphone.log`, `deploy-iphone.txt` |

iPad launch env (`run-ipad-env.json`, via `devicectl -e`, wins over the
manual-play Documents env): I26-FAST `PS2X_PAD_SCRIPT` (byte-exact from
the bundled env), `PS2X_VPAD_TEST_STICK="1,0"`,
`PS2X_VPAD_TEST_TOUCHES="1900:0.8975:0.34:120"` (D-pad down hold in the
race; fractions for the 820×410 game window),
`PS2X_MC_ROOT=…/Documents/mc-fresh`, `PS2X_VSYNC_RATE_LOG=1`. Script:
31 armed, i=0..25 fired. Sound: 36 kHz stream from the bundled env
(manual-play env inherits it), underruns as usual below 1×.

iPad frames (viewed; portrait compat window crops left/right per I28 —
game-window content correct; background shows another app's form, as in
I30):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `run-ipad/shot-t400.png` (tick 442) | Title logo (cropped); deflected knob visible | `e5186187…` |
| `run-ipad/shot-t900.png` (tick 939) | Setup Character (non-Zoe rider — held stick drifted the rider row; route is rider-agnostic) | `bc43350b…` |
| `run-ipad/shot-t1750.png` (tick 1750) | Race 1ST/2, 00:00:00, EA Radio card | `4f4e94ef…` |
| `run-ipad/shot-t1960.png` (tick 1962) | Race 2ND/2, 1%, mid D-pad hold | `133fec6c…` |
| `run-ipad/shot-t2120.png` (tick 2140) | Race 2ND/2, 1%, post-hold, advancing | `c8bba43e…` |

Full SHAs in `frame2-sha-read1.txt` (matched twice). Precision notes:
the iPad shows the rider advancing with `lx=0xff` in the pad bytes, but
there is no stick-off control run, so this is input-level proof, not a
differential steering proof (I30's no-stick iPad run was also 2ND/2 at a
like tick). The non-Zoe rider is consistent with the held stick moving
the rider row (same drift mechanism as the Select Peak 1→2 move on sim),
i.e. stick input demonstrably reaches game menu logic on device.

The `mc-fresh` override used a stale container UUID (I30's `AAF168EA…`;
live container is `8B1267A4…` — some lane reinstalled the app since
I30), so it resolved to a nonexistent path: effective behavior was an
empty card (route worked fresh-like), and Brad's `mc0` is verified
byte-identical after the run (deploy reran: SKIP + exact sizes). Nothing
was created to clean up. Future `-e PS2X_MC_ROOT` uses must read the
live path from the previous run's console.

Sim derisk runs (all on the Part 1 sim build, `71c952e`): pretest
(route + held stick, fresh card → race at 1715, menus tolerate the
stick); savetest/saveroute/savenostick/savediag with Brad's `mc0` copied
to the sim container. Run.txt files committed (`sim-*-run.txt`); shots
in scratch.

**Finding F1 (for the orchestrator/E-lane, not a controls defect): with
Brad's save present, I26-FAST misses the Select Peak confirm and runs
~1 screen behind.** `run-savenostick` (route only): Peak 1 highlighted
at tick 1808 after crosses at ~1100/1186/1337/1440 all failed to
advance, while script downs demonstrably moved the highlight 1→2→3
(locked Peak 3 at tick 2179) — inputs register, crosses don't confirm.
`run-saveroute` (up-tap + held stick): still Peak at 1828, Select Event
(Happiness) at 2035, My Rules at 2161 — progressing late via redundant
crosses. Sim evidence: `1ecd2794…` (Peak 1 stuck), `9d27895e…` (Peak 3
drift), `068bbf38…` (Event), `22d0d322…` (Rules). Mechanism unknown
(game/card behavior under Brad's save, not pad input). Any future
scripted device run must use a fresh card (as here) or a save-aware
route.

Part 2 budget: 1 device build, 1 iPad launch (198 s), 2 installs,
5 sim derisk runs; ~65 min vs the 45 min box (overrun: save derisk +
lease waits behind E57/AU lanes). Scratch 8.2 GB; no I32 lease held at
close; Simulator shut down; iPad app terminated (`info processes`
clean). iPhone: install + file copy only, never launched.

## Gaps (updated)

- G1: real touches (UIKit → SDL fingers) still unexercised — Part 2 used
  injected vectors/touches (carries I26 V1). Brad's hands-on play is the
  first real-touch test of the stick anchor/drag/release cycle.
- G2: closed — I31's `deploy-ios.sh` consumed in Part 2 (SKIP + exact
  sizes on both devices, before and after the iPad run).
- G3: while the overlay shows, an untouched virtual stick centres
  `data[6..7]`, overriding a connected-but-unused physical stick (drift
  included). Using the controller hides the overlay and restores the
  gamepad bytes. Flagging in case Brad plays hybrid.
- G4: `PS2X_ENABLE_IOP_RPC_TRACE=1` (fork default ON) in the sim build,
  same as I30; unhandled-RPC trace lines in consoles.
- G5: run-3 (wall-clock 20/25/30 s shots) missed Select Character under
  host load 20; run-4 used a tick trigger instead. Wall-time shot
  schedules are unreliable while other lanes build.
- G8: no isolated game-visible D-pad proof on iPad (tuck MPH/posture
  hidden by the portrait crop) and no differential stick-steering proof
  (no stick-off control run). Input-level proof only: exact bytes in the
  pad log, deflected knob rendered, rider advancing, menu drift from the
  held stick. Brad's hands-on play closes both.

## Orchestrator gate (Part 1)

**Pass; Brad approved the layout (09-24).** I viewed `run-stick/shot-0020s.png` (stick knob deflected
full right on the left, D-pad on the right between R1/R2 and △) and `run-sim/shot-0100s.png` (race
with the overlay; the D-pad clears the face and shoulder buttons). The stick log shows the injected
`(1,0)` as `lx=0xff ly=0x80`; suite 601/601; runner-dir diff empty. Part 2 released: device build
from `i32-controls` `71c952e`, iPad install + test, iPhone install only (never launched), then re-apply
`local/research/I31/deploy-ios.sh` on both.
