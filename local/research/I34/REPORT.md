# I34 — virtual pad layout v2 (Part 1 complete)

Worker: Muse. Brief: `local/muse/prompts/I34.md`.
Fork worktree `~/dev/ssx3-work/I34/PS2Recomp`, local branch `i34-pad` =
fork `ssx3` `0ed07c4` + 1 commit (`3d52208`). No push. Runner-dir diff
vs `14b1e5cb` empty (checked before commit).

Headline: the stick is 1.5x and the D-pad is 80% of the face-button
cluster's bounding box, placed below the cluster and pushed right to the
no-overlap limit — literal down-right of the cluster cannot fit (proof
below). The change is implemented and verified against the real header
with a lightweight check (no-overlap, hit tests, stick mapping on all
three sizes) plus a syntax compile of the new test TU. **The full host
suite and the Simulator build + screenshots did not run: the mini is
over the 200 GB internal-disk cap (205.3 GB), so per the standing rule
the >1 GB steps were not started.** Resume recipe at the end.

## What changed (fork `3d52208`, 2 files)

`ps2xRuntime/include/ps2_virtual_pad.h` (`makeLayout` only; no logic
changes — draw i.e. base/knob, drag radius, 2.5x re-anchor distance all
scale with `stickR` already; dead zone stays 10%):

| Item | Before (I32) | After (I34) |
| --- | --- | --- |
| Stick radius | `0.10u` | `0.15u` (x1.5); rest `(0.205u, 0.60u)` unchanged, still left-half in-zone, rest disc on screen and clear of L1/L2/SELECT |
| D-pad overall (disc diameter) | `0.19u` | `0.32u` = 0.8 x face-cluster bbox (`0.40u`) |
| D-pad centre | `(w-0.205u, 0.285u)` (above the face buttons) | `(w-0.532u, 0.78u)` (below the face centre, right of screen centre) |
| D-pad arrows | `dOff 0.055u`, `dBr 0.040u` | `dOff = dpadR*11/19`, `dBr = dpadR*8/19` (arrow bbox == disc diameter, as I32) |

Face buttons, shoulders, Select/Start: untouched.

`ps2xTest/src/ps2_virtual_pad_tests.cpp`: new `I34 layout` Run asserting,
on 874x402 (iPhone 16 Pro), 956x440 (16 Pro Max) and 1180x820 (iPad Air
11" landscape): stick 0.15u + rest placement, face bbox 0.40u, D-pad =
80% of it, D-pad below face centre / right of screen centre / on screen,
zone left of the D-pad hit disc, drawn+hit non-overlap every pair both
ways, every button centre presses exactly itself, picture centre presses
nothing. Existing I32 Runs unchanged (still pass by inspection: the
re-anchor test's `(400,100)` jump is still outside the new 2.5x track
radius).

## Sizes in points (u = window height)

| | 16 Pro (874x402) | 16 Pro Max (956x440) | iPad Air 11" (1180x820) |
| --- | --- | --- | --- |
| Stick base R / knob R, before | 40.2 / 16.9 | 44.0 / 18.5 | 82.0 / 34.4 |
| Stick base R / knob R, after | 60.3 / 25.3 | 66.0 / 27.7 | 123.0 / 51.7 |
| Stick rest (unchanged) | (82.4, 241.2) | (90.1, 264.0) | (168.1, 492.0) |
| Face bbox (unchanged) | 160.8 | 176.0 | 328.0 |
| D-pad diameter, before | 76.4 at (791.6, 114.6) | 83.6 at (865.8, 125.4) | 155.8 at (1011.9, 233.7) |
| D-pad diameter, after | 128.6 at (660.1, 313.6) | 140.8 at (721.9, 343.2) | 262.4 at (743.8, 639.6) |
| D-pad arrows off/R, after | 37.2 / 27.1 | 40.8 / 29.6 | 76.0 / 55.2 |
| Min no-overlap margin | 2.7pt (START/square) | 3.0pt | 2.9pt (stick zone) |

## Closest-fit note (what was picked and why)

Literal down-right of the face cluster is infeasible at 0.32u on the
iPhone: the cluster's right edge is at `w-0.005u` (2pt of room), and
below-with-x-overlap needs centre `y >= 0.98u` (bottom edge `1.14u`,
off screen); the bottom-right corner point `(w-0.16u, 0.84u)` is 0.119u
from Cross, needing 0.254u. The closest overlap-free spot is below the
face centre, tucked between Square/Cross and START, pushed right to the
limit: `(w-0.532u, 0.78u)` (grid-searched; binds START/square on the
phone, the stick-zone assertion on the iPad, ~3pt each). Consequence:
the D-pad sits left of the face column (not right of it) and overlaps
the game picture's bottom-right — the right column (R1/R2, face, START)
is full. Screenshots will show Brad exactly this; moving the face
cluster or START to make literal down-right fit was judged more invasive
than the brief allows.

## Verification done (all <1 MB; no >1 GB step started)

- `g++` standalone check against the real header (`/tmp/i34_vpad_check.cpp`,
  layout + `pressedMask` + `updateStick`/`stickBytes` on all three sizes):
  **ALL OK**.
- `g++ -fsyntax-only` on the modified `ps2_virtual_pad_tests.cpp` with the
  suite's include dirs: **SYNTAX-OK**.
- Host suite from the worktree root: NOT RUN (build ~1.3 GB, I32 precedent).
- Simulator build + title/race screenshots: NOT TAKEN (build+stage ~3.4 GB).
  No screenshot paths exist; nothing to view yet.

## Blocker: disk over cap (telling the orchestrator)

`local/tooling/disk_budget.sh` before the host-test build: **ssx3 internal
usage 205.3 GB of the 200 GB cap; disk free 68 Gi**. Biggest:
`ssx3-work` 185G (`VR1` 36G incl. `run/` 26G, `F2` 17G, `F1` 9G, `GB4`
8.5G, `I32` 8.2G, `I33` 7.6G). My I34 scratch is 1.2 GB (worktree +
cmake configure only). Nothing of other lanes' was touched.

## Resume recipe (after the V lane frees space)

```sh
WT=~/dev/ssx3-work/I34/PS2Recomp   # branch i34-pad = 0ed07c4 + 3d52208
# 1. Suite (build dir already configured Release, PS2X_BUILD_STUDIO=OFF):
cmake --build ~/dev/ssx3-work/I34/host-test -j8
(cd $WT && ~/dev/ssx3-work/I34/host-test/ps2xTest/ps2x_tests)
# 2. Sim build: copy ~/dev/ssx3-work/I32/build-install.sh to I34 with
#    W=I34, PIN=0ed07c4362b9bd53c09094fd028ee05e8aaf021a, ENVFILE=I32 ps2x.env;
#    bash build-install.sh preflight configure_sim build_sim stage_sim sim_install
# 3. Runs: copy I32 sim-stick-run.sh (PS2X_VPAD_TEST_STICK=1,0 title shot)
#    + sim-run.sh (race) with W=I34, claims I34-stick/I34-sim; view shots.
```

Budget: ~40 min elapsed, 0 builds, 0 boots, 0 lease claims.

## Part 1 complete — suite + Simulator build + screenshots (after disk cleared)

Disk back under cap (orchestrator deleted closed lanes' output; 154.4 GB
at resume). No new fork commits (`i34-pad` still `3d52208`).

**Suite:** Release from the worktree root, rc=0, **613/613/0** (I32-era
count was 601 at `f949ff0`; the tip suite is bigger). All 11
Ps2VirtualPad Runs pass, including the new I34 layout Run on all three
sizes. Full log `~/dev/ssx3-work/I34/host-tests.log`.

**Simulator build** (`~/dev/ssx3-work/I34/build-install.sh`, I32 recipe
with W=I34 + PIN `0ed07c4`; env = I32's `ps2x.env`, SHA `0041e09a…`,
CPU backend): `preflight configure_sim build_sim stage_sim sim_install`
all rc=0. Release `-O3 -DNDEBUG` (cache evidence), raylib patch already
applied, codegen `8ea8ed43…` (canonical), stage ISO/ELF `cmp`-equal.
Sim binary `1ff02dff…`. Receipts in `~/dev/ssx3-work/I34/logs/`.

**Runs** (lease slot 1, claimed/released each; Simulator shut down after):

| Frame (`~/dev/ssx3-work/I34/`) | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `run-stick/shot-0020s.png` (tick 538) | Title logo + Press START + EA copyright; stick knob deflected full-right; `[vpad] stick pad bytes lx=0xff ly=0x80` in console | `afbd0262…65e424` |
| `run-sim/shot-0010s.png` (tick 371) | Title logo + EA copyright; stick rest ring left, D-pad below face buttons | `7c635520…5c2a9c66` |
| `run-sim/shot-0030s.png` (tick 737) | Select Character, Zoe, stats bars, rider silhouettes | `e3ddba52…72c33e0a1` |
| `run-sim/shot-0035s.png` (tick 952) | Setup Character, Zoe, Continue/Equip Gear/Rider Details/Music | `facf17aa…5d12b21768` |
| `run-sim/shot-0100s.png` (tick 1795) | Race 2ND/2, 00:00:01, 0%, countdown digits, EA Radio "Poor Leno – Silicon Soul Remix / Royksopp" | `f5751639…7a6d5936` |
| `run-sim/shot-0160s.png` (tick 2031) | Race 2ND/2, 00:00:05, 1%; race advances | `c6076aea…2ad2e99` |

Full SHAs in `frame-sha-read1.txt` / `frame-sha-read2.txt` (identical).
Route: I26-FAST, script i=0..21 fired (22 presses; guest slower under
host load, last tick 2031 vs I32's 2221 — same shape as I32's note).
Sound stream started (48 kHz host rate here). Race pace ~4.0–4.6 vsync/s
tail — diagnostic only, not a speed number.

**Layout as seen:** the stick is visibly 1.5x at rest; the D-pad is a
large 4-arrow diamond below the face buttons, left of the face column;
no control overlaps in any frame. Closest-fit consequence, visible in
the Select/Setup Character shots: the D-pad covers the bottom-right
button-hint legend ("✕ Select / △ Previous / ☐ Options"). Brad's call
whether that placement stands.

Part 1 budget: 1 Simulator build, 2 runs (21 s + 160 s, slot 1).
I34 scratch 4.8 GB. No lease held at close.
