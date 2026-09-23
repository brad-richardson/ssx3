# E47 report: why is the race world dark?

**Part 2 (re-run) has the verdict: see the end of this report.** H1–H4 are refuted or not supported; the evidence points at race 3D geometry landing off-viewport. Part 1 below is kept as written.

Brief `local/muse/prompts/E47.md`. Worker: Claude Code (Opus pane). This
report gives tables and receipts only; the orchestrator decides.

## Outcome

- **Stopped at the boot budget without race data.** Boot B (race window
  7600–7610) hit its 360 s wall at **tick 6395**, on the pre-race
  "Rival Challenge / Happiness - Race" rules screen. None of the four
  windowed logs opened and E4 never armed. The e46g reference run passed
  tick 7403 at 240 s and 7653 at 250 s.
- **Cause: host contention, not the route.** The runner binary is
  byte-identical to e46g/e46h (`a2521d92…` ×2), and the pad script fired
  on schedule through i=8. During both boots, E48 was building two trees
  at once (`~/dev/ssx3-work/E48/build-on` and `build-off`, 11+ `clang++`
  processes at about 100% CPU each). Load average was **22–25** at the
  end of boot B. Boot B ran at **0.63×** e46g's tick rate throughout
  (table below). I can't separate this from the overhead of the E43/E4
  taps being enabled: both boots had them and both overlapped the
  builds. This is stated as a gap below.
- **No hypothesis verdict is possible for the race.** H1–H4 need the race
  window. Boot A (SC control) is complete and gives the healthy baseline
  the race tables would be compared against.
- **Boot A (SC control, 1300–1310): healthy and bit-steady.** The frame
  shows Zoe rendered at Select Character. All 11 vsyncs are identical:
  611 MSCAL, **0 budget-exhausted programs** (max 2,406 cycles), 5,079
  draws per vsync, draw records mode 3 ×4 plus mode 6 ×2 (`0x363cf4`)
  plus mode 6 ×9 (`0x363d74`), and a nonblack display surface.
  E33-era SC had 498 of 583 programs exhausted, so that symptom is gone
  on this build.
- **Two tooling findings for the next lane:** (1) the gfx-stats `top`
  field is (FRAME.fbp, PRIM.type), not (TBP0, PRIM) as its header says.
  (2) The E43 and MPG logs flush only every 128 lines, and the harness
  SIGTERM drops the unflushed tail. I ran their windows past `to` so any
  loss falls outside the window.

## Recommendation (the orchestrator decides)

Re-run **boot B only**, unchanged, once the host is quiet (no E48
builds, no second runner). Command below; 360 s is enough at e46g's
pace, and a 450 s wall would also clear 7611 at 0.8× pace. Expected cost
is about 6 min and about 50 MB. Boot A does not need repeating. After
that, `e47_analyze.py e47a 1300 1310 e47b 7600 7610` produces every
table the brief asks for.

## Boots (Mac mini, E47-build, slot 1, own run dir, PID-tracked)

| Boot | Window / E4 arm | Wall | Final tick | Result |
|---|---|---|---|---|
| e47a | 1300–1310 / 1305 | 90 s, rc 0 | 1691 | COMPLETE: all logs in window; E4 `span-complete`, 512 history entries, 6 surfaces |
| e47b | 7600–7610 / 7605 | 360 s, rc 0 | 6395 | WINDOW NOT REACHED: rules screen before race; 0 log files, no E4 arm |

Tick against wall time, same runner binary (from snap `.txt`):

| Wall (s) | e46g (quiet host) | e47b (E48 builds running) | ratio |
|---|---|---|---|
| 60 | 1754 | 1277 | 0.73 |
| 120 | 3454 | 2243 | 0.65 |
| 180 | 5483 | 3273 | 0.60 |
| 240 | 7403 | 4376 | 0.59 |
| 280 | 8404 | 5054 | 0.60 |
| 355 | — | 6323 | — |

e47a reached tick 1199 at 60 s (e46h: 1834). Both boots report
missing targets for `0x3b1140` ×3 only, as in e46g.

## Flag window semantics (checked in source, fork `2e21cdc`)

| Flag | Window | Output | Caps / flush |
|---|---|---|---|
| `PS2X_GFX_STATS` | one `_FROM/_TO` vsync window, inclusive | 1 line/vsync | 20k lines; per-line flush |
| `PS2X_VU1_TRACE` | one window | **budget-exhausted programs only** (census + first 40 detail blocks); no line for programs that complete | 100k; per-line flush; file created lazily (none = 0 exhausted) |
| `PS2X_E43_TRACE` | one window (+ separate `H394_FROM/TO`) | drec/drecs/dprod/h394 | 40k; **flush every 128** |
| `PS2X_VIF_MPG_LOG` | one window | 1 line/MPG | 20k; **flush every 128** |
| `PS2X_E4_DIR` + `_ARM_TICK` | arm N, freeze N+1 (one per boot) | GS history (ring of **512 events**: the frame's tail), per-FBP draw census, VRAM at arm/freeze, surface samples, present inputs | 2 MiB text + 2×4 MiB VRAM |

All flags take one window, so the design was one boot per window. E4
provides the per-draw FRAME/ZBUF/TEST/ALPHA/SCISSOR/TEX0 the brief's
"10 largest draws" table needs; it is an existing flag, so no code
change was required. Limit: the 512-event ring covers only the last
~478 draws of a 5,079-draw frame. "Largest" therefore means largest in
the frame tail.

## Boot A tables (SC steady, vsync 1300–1310). Race column: not captured

### GS prims per frame (gfx stats; identical on all 11 vsyncs)

| Metric | SC (e47a) | Race |
|---|---|---|
| MSCAL / MSCNT | 611 / 0 | — |
| VU1 cycles / exhausted / max single | 258,614 / **0** / 2,406 | — |
| XGKICK | 387 | — |
| PATH1 / 2 / 3 packets | 387 / 195 / 3 | — |
| PATH1 draws (verts) | 4,166 (12,498) | — |
| PATH2 draws (verts) | 880 (1,990) | — |
| PATH3 draws (verts) | 33 (66) | — |
| PATH1 box x, y (GS coords) | 1741–2359, 1799–2325 | — |
| PATH1 z | 135,1xx – 8,388,467 | — |
| top (fbp:type) | 0:tstrip 4166, 0:sprite 666, 0:tri 230, 112:sprite 17 | — |

E4 census at tick 1305: 5,079 draws (fbp0 5,062, fbp112 17). The
history's 478 draw events (the frame tail) split as follows:

| prim | ctxt | tme | abe | FRAME fbp | ZBUF zbp | TEST | ALPHA | fbmsk | zmask | draws |
|---|---|---|---|---|---|---|---|---|---|---|
| tstrip | 0 | 1 | 1 | 0 | 224 | 0x515cd | 0x44 | 0 | 0 | 464 |
| sprite | 0 | 1 | 1 | 0 | 224 | 0x31143 | 0x44 | 0 | 1 | 14 |

### 10 largest-area draws in the SC history tail

All are textured, alpha-blended tstrips (3 verts) on ctx0 with FRAME
0/8/psm 0/fbmsk 0, ZBUF 224/0x31/zmask 0, TEST 0x515cd, ALPHA 0x44 and
SCISSOR 0,0,511,447. TEX0 is 11657 (psm 0x13, 128²) or 11721 (psm 0x13,
64²). Screen extents are small (about 7–13 × 11–18 px), consistent with
the rider mesh. The full rows are in `an-e47a.md`.

### VU1 program starts

| | SC | Race |
|---|---|---|
| budget-exhausted programs (VU1 trace census) | **0** (no file created) | — |
| total MSCAL/vsync (gfx stats) | 611 | — |

Gap: no existing flag logs completed programs by startPC. The VU1 trace
covers exhausted programs only, and the VU1 entry trace dumps listed PCs
once. A per-startPC table of *all* starts needs a new tap (a code
change, out of this brief's scope).

### Draw-record modes per vsync (E43 drec; identical on all 11)

| src | mode | records/vsync | w0 |
|---|---|---|---|
| `0x363cf4` | 3 | 4 | `0xcc` |
| `0x363cf4` | 6 | 2 | `0x1b0` |
| `0x363d74` | 6 | 9 | `0x1b0` |
| `0x364460` | 0 | 3 | `0` (struct, per E43) |

This matches PCSX2's settled 4×mode-3 + 2×mode-6 on `0x363cf4` (T54,
E43) and adds 9 mode-6 records from the second walker site.

### MPG uploads (418 in window, 38/vsync)

| dest bytes | num | fnv | per vsync |
|---|---|---|---|
| 0–14336 in 7 × 2 KiB blocks (imm 0…1536) + 14336–15880 (num 193) | 0 (=256) / 193 | `6a82dc60` `d2ed09dd` `ab5967d3` `dcb9c88b` `0fa6a688` `c2c2e4e6` `e2c484f4` `d0b66730` | 4.0 each |
| 0–4608 (imm 0/256/512) | 0,0,64 | `6baf3a7b` `e3a2ee15` `3428bac3` | 2.0 each |

Every upload was `copied`; none were dropped or clipped. Two upload
sets recur each vsync: a full 15.5 KiB set 4× and a 4.5 KiB set 2×
(order not tabled).

### Present (E4, tick 1306)

`pmode=0xff21`, disp1 fbp 112 (surface nonzero 1007/1024 samples),
draw target fbp 0 nonzero 999/1024. VRAM changed between arm and freeze
(`0x550bd1bf` → `0xc3e93299`).

## Hypothesis status

| H | What it needs | Status |
|---|---|---|
| H1 no world records / VU1 programs never start | race drec modes + MSCAL | OPEN (no race data) |
| H2 VU1 exits on budget / wrong microcode | race VU1 census + MPG fnv | OPEN. SC baseline: 0 exhausted, all MPG copied |
| H3 draws issued but invisible | race E4 TEST/ALPHA/ZBUF/FRAME/SCISSOR | OPEN. SC baseline row above |
| H4 drawn then overwritten | race E4 history + arm/freeze VRAM | OPEN |

## Exact commands

```
cmake -S ~/dev/PS2Recomp -B ~/dev/ssx3-work/E47-build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_BUILD_TEST=ON \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
cmake --build ~/dev/ssx3-work/E47-build --target ps2EntryRunner
local/research/E47/e47_boot.sh e47a 1300 1310 1305 90 5     # boot A
local/research/E47/e47_boot.sh e47b 7600 7610 7605 360 5    # boot B (re-run this)
python3 local/research/E47/e47_analyze.py e47a 1300 1310 > local/research/E47/an-e47a.md
```

`e47_boot.sh` wraps `E46/e46_boot.py` (the e46g script: E33 vsync
route, `PS2X_SKIP_MOVIE=1`, E44 trace as in e46g, frame dumps on) and
exports the windowed flags. CMake cache differs from E46-build only in
the codegen path (`codegen-ssx3`, the renamed e46g content) and
`PS2X_BUILD_STUDIO` (a different target).

## Receipts

- Fork `ssx3` @ `2e21cdca039b…`, clean worktree; runner
  `a2521d92f3f019f2208b2f6a66ef7a36357f639bd093ad4bfd90662d408bbd59` ×2
  (= e46g/e46h runner).
- In this dir: `e47_boot.sh`, `e47_analyze.py`, `an-e47a.md` (full
  analyzer output), `gfx-e47a.txt`, `e43-e47a-window.txt` (drec/drecs/
  dprod rows 1300–1310, h394 excluded), `mpg-e47a-window.txt`,
  `e4-e47a-history.txt.gz`, `e4-e47a-present.txt`, `e4-e47a-samples.txt`.
- Raw data in `~/dev/ssx3-work/E47-run/` (short SHA-256): boot-e47a
  `793e1748…` (3,576,245 B), boot-e47b `7689a07b…` (9,206,011 B),
  gfx `1e880981…`, e43 `9e165bcf…` (558,796 B), mpg `e7eddf12…`
  (1,257,056 B), e4 history `5a6b16ea…`, VRAM arm `d939ca17…` /
  freeze `7599e598…`.
- Frames: e47a SC snap-0070 (tick 1347) shows the Zoe rider; e47b's last
  frame is `upload-latest.png` (tick 6395, rules screen).
- Lease: slot 1 for both boots, peers [] at claim, released,
  `pgrep_rc 1`.
- Budget: 2/2 boots, about 45 min of 3 h. E47 disk is 2.97 GiB of the
  3 GB cap (build 2.93, run 0.04); a boot-B re-run adds about 0.05.
  Internal total 49.1 of 200 GB.

---

## Part 2: boot B re-run (orchestrator gate: quiet host, 450 s wall)

### Verdict (the orchestrator decides)

| H | Evidence (race window 7600–7610, E4 at 7605/7606) | Status |
|---|---|---|
| **H1** records never produced / VU1 never starts | 221–229 MSCAL/vsync; **6,474–6,828 PATH1 draws/vsync** (all tstrips, one triangle each); walker produces mode 3 ×9 + mode 1 ×1 every drawing vsync | **Refuted as stated.** World-class draws are produced and issued |
| **H2** budget exits / wrong microcode | **0 exhausted** (max 7,967 cycles vs 65,536 budget); all 693 MPG uploads `copied`; the same 8-upload set as SC (same FNVs) plus a second 5-upload set | **Refuted** |
| **H3** issued but invisible (alpha/Z/FRAME/SCISSOR) | Tail draws: fbmsk 0, full-screen scissor, ZTST ALWAYS/GREATER, standard blend (0x44/0x48). World pixels end the frame with **color 0 and Z 0**, and GEQUAL/GREATER always passes against Z 0, so a failing Z test cannot hide them. The world draws' own TEST/ALPHA/FRAME are not in the 512-event ring | **Not supported** by any observed register; only an alpha-test or alpha-0 cause on the unseen world draws remains unexcluded |
| **H4** drawn, then overwritten/cleared | No clear or large draw in the frame tail (seq 7100–7611); Z is also empty in the world area (a later color-only overwrite would leave Z); the arm snapshot (end of frame 7604) is equally dark | **Not supported** |
| **New lead: off-viewport geometry** | **All 81 3D draws in the tail (trail texture 13217) lie entirely outside the 512×448 viewport** (x 2270–2550 vs 1792–2304; many y 1670–1813, above the top edge 1824). Every SC draw and every race HUD draw is on-screen. The race PATH1 bounding box is pinned to **1023.5–3071.5 on both axes on every vsync** (SC: 1741–2359 × 1799–2325). XYOFFSET_1 = `0x720000007000` (1792/1824) confirms the viewport | **Best supported:** the 3D geometry is issued but lands off-screen or degenerate. The fault is in the vertex positions the VU programs emit (matrices, camera or projection inputs), not in GS state |

In short, H1–H4 as written don't explain the dark world; the evidence
points at wrong screen-space vertex positions for race 3D geometry. Two
caveats: (1) world draws before seq 7100 are not in the ring, so the
"off-screen" finding rests on the 81 trail draws plus the pinned
aggregate box. (2) The ±1024 box could also come from legitimate
guard-band clamping of near-camera triangles. A PCSX2 reference for the
same moment (trail positions, PATH1 box) would tell these apart.

### Recommended next action (the orchestrator decides)

1. **T lane:** at PCSX2 race tick ~7605 on the same route, capture the
   trail and world triangle screen positions (or a GS dump) and the
   PATH1 xyz box. If PCSX2's box stays inside the viewport, the recomp's
   vertex positions are wrong.
2. **E lane (needs a small code change, out of this brief):** add a
   per-vsync on-screen/off-screen draw count, or an E4 ring that keeps
   the *first* N draws, to see the world draws' positions and registers.
   Then trace one world VU1 program's inputs (the camera/view matrix in
   VU1 data memory) with `PS2X_VU1_ENTRY_TRACE` against PCSX2.
3. Keep `0x3b1140` (E48) in view: it is the only remaining missing
   target on this route (×3). A skipped refcount release on a shared
   node could plausibly leave stale camera or scene state; that link
   is untested.

### SC vs race side by side

| Metric (per vsync) | SC (e47a, 1300–1310) | Race (e47b, 7600–7610) |
|---|---|---|
| MSCAL / MSCNT | 611 / 0 | 221–229 / 0 (0 on 7602, 7606: no-draw vsyncs) |
| VU1 cycles / exhausted / max | 258,614 / 0 / 2,406 | ~254k–259k / **0** / 7,967 |
| XGKICK | 387 | 334–337 |
| PATH1 / 2 / 3 packets | 387 / 195 / 3 | 334–337 / 110 / 0–1 |
| PATH1 draws (verts) | 4,166 (12,498) | 6,474–6,828 (19,422–20,484) |
| PATH2 draws | 880 | 83 |
| PATH3 draws | 33 | 0 or 33 |
| PATH1 box x × y | 1741–2359 × 1799–2325 | **1023.5–3071.5 × 1023.4–3071.5** |
| top (fbp:type) | 0:tstrip 4166, 0:sprite 666, 0:tri 230, 112:sprite 17 | 0:tstrip ~6,370–6,720, 0:tfan 105–111, 0:sprite 83–99, 112:sprite 17 |
| E4 census draws (fbp0 / fbp112) | 5,079 (5,062 / 17) | 6,594 (6,577 / 17) |
| Draw-record modes (src `0x363cf4`) | m3 ×4 (`0xcc`) + m6 ×2 (`0x1b0`); `0x363d74` m6 ×9 | **m3 ×9** (`0xc0` mostly, `0xcc`) + **m1 ×1** (`0x70`); **no mode 6** |
| `0x364460` m0 | 3 | 3 |
| MPG uploads | 38 (8-set ×4, 3-set ×2) | 63 (same 8-set ×7.4, 5-set ×0.8) |
| fbp0 nonblack at freeze | 98.0%, mean 153.6 | **9.8%, mean 10.6** |
| Z (zbp 224) nonzero at freeze | 7.9% (rider) | 12.9% (HUD rectangles + one central patch) |

Vsyncs 7602 and 7606 issued no 3D draws (0 MSCAL); the other nine
drew. E4 armed on 7605, a drawing vsync.

### E4 race history (seq 7100–7611: 244 draws, 148 GIF tags, 120 register writes)

| prim | tme | abe | TEST | ALPHA | zmask | TEX0 | on-screen | draws |
|---|---|---|---|---|---|---|---|---|
| tstrip | 1 | 1 | 0x71143 (ATST ALWAYS, ZTST GREATER) | 0x48 | 1 | 13217 (32², CT32 gradient) | **0 / 81** | 81 |
| sprite | 1 | 1 | 0x31143 (ZTST ALWAYS) | 0x44 | 0 | 14505 / 3712 / 11017 / … | yes | 83 |
| tstrip | 1 | 1 | 0x31143 | 0x44 | 0 | 3712 / 9472 / 4736 | yes | 78 |
| tstrip | 0 | 1 | 0x31143 | 0x44 | 0 | — | yes | 2 |

The "10 largest-area draws" table for the race (`an-e47b.md`) consists
only of tail trail and HUD triangles: the ring cannot hold the frame's
world draws (6,594 draws vs 512 events). All ten share FRAME 0/8/CT32/
fbmsk 0 and SCISSOR 0,0,511,447. TEST is 0x71143 or 0x31143, ALPHA
0x48 or 0x44, ZBUF 224/Z24.

### VRAM decode (`e47_vram.py`; PNGs in `frames/`)

| label | snapshot | surface | nonblack | mean |
|---|---|---|---|---|
| e47a | arm / freeze | fbp0 | 98.0% / 98.0% | 153.6 |
| e47a | arm / freeze | fbp112 | 97.6% / 97.6% | 153.0 |
| e47b | arm / freeze | fbp0 | 9.9% / 9.8% | 10.6 |
| e47b | arm / freeze | fbp112 | 9.9% / 9.9% | 10.6–10.7 |

Z24 at zbp 224, same snapshots: e47a 7.9% nonzero (140k–182k); e47b
12.9% nonzero (987–16,777,215, HUD sprites at 0xFFFFFF). The decode is
validated: `e47a-freeze-fbp0.png` reproduces the SC frame with Zoe.
`e47b-freeze-fbp0.png` shows the full HUD (1ST/2, 00:00:09, 2%, 23
MPH, "+280 STYLE BONUS", "LATE FLIP!") and one small snow-geometry
fragment on a black background. Viewed by eye.

### Re-run receipts

- Wait: poll every 2 min for no `clang++`/`ninja` and 1-min load < 8.
  Quiet at 15:57:12 (load 6.46). My first poll misfired: `pgrep -x
  clang++` is an invalid regex. It was caught within one poll and
  restarted with `'clang\+\+'`; no boot started early.
- `local/research/E47/e47_boot.sh e47b 7600 7610 7605 450 5`: slot 2,
  peer `98145` (E48's runner in slot 1, allowed), rc 0, wall 450.7 s,
  final tick 8717, lease released, `pgrep_rc 1`. Pace: 60 s→1767,
  120→3541, 240→5378, 355→6832, 445→8630. Pad presses i=0…12 all
  fired. Missing targets: `0x3b1140` ×3 only.
- Same runner `a2521d92…` (unchanged E47-build).
- Raw data (`~/dev/ssx3-work/E47-run/`, short SHA-256): boot-e47b
  `f2b448e3…` (11,265,576 B; the first attempt's log was overwritten
  by the same label), gfx `9fba01a5…`, e43 `92e2ac70…` (235,964 B),
  mpg `78daaacc…` (1,932,617 B), e4 history `3e8d834c…`, VRAM arm
  `5ea77022…` / freeze `79524463…`. No VU1 trace file (0 exhausted).
- In this dir: `an-e47b.md`, `an-both.md`, `gfx-e47b.txt`,
  `e43-e47b-window.txt`, `mpg-e47b-window.txt`,
  `e4-e47b-history.txt.gz`, `e4-e47b-{present,samples}.txt`,
  `vram-table.md`, `e47_vram.py`, `frames/*.png` (8 color + 4 Z).
- Budget: 3 boots total (2 briefed + 1 orchestrator-approved re-run).
  E47 disk 2.95 GiB of 3 GB.
- Commands:
  `python3 local/research/E47/e47_analyze.py e47a 1300 1310 e47b 7600 7610 > local/research/E47/an-both.md`;
  `python3 local/research/E47/e47_vram.py e47a e47b`; Z decode inline
  (PSMZ32 block table `[[24,25,28,29,8,9,12,13],[26,27,30,31,10,11,14,15],[16,17,20,21,0,1,4,5],[18,19,22,23,2,3,6,7]]`,
  CT32 column table, block = 224<<5, low 24 bits).
