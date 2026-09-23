# E33 report — VU1 budget census + vsync-clock pad script; H1 shows, fix attempted and negative

Brief `local/muse/prompts/E33.md`. Tables + receipts; the orchestrator decides.

## Outcome

- Two feature commits on fork `ssx3` (`071d240` pad vsync clock, `d85e293`
  gfx stats), suite **472/472** flags-unset from the fork root, pushed
  `e57b5f8..03d6549` (fast-forward, runner-dir diff empty).
- Vsync-clock script converted from the E31 e31l route via laptop
  tick→guest-ms interpolation; reaches the same screens on the Mac
  (Select Character settled in A; race HUD 00:00:03 in B).
- **H1 shows on both screens**: Select Character settled has
  `vu_exhausted=498/583` programs/vsync with `mscnt=0` (all dropped);
  pre-race/race has up to 166/573, also `mscnt=0`.
- **Fix attempted, result negative**: resume-to-E-bit (16-slice cap) burns
  17× VU cycles with byte-identical kicks/packets/draws; Zoe still absent;
  slice-exhaustions 8466. The truncated programs spin without issuing —
  truncation is a symptom, not the mechanism. Recommend reverting the fix
  commit (it taxes every future boot ~2× in slow scenes for no gain).

## Commits (fork `~/dev/PS2Recomp`, branch `ssx3`)

| Commit | Subject |
|---|---|
| `071d240` | `[E33] DEV-ONLY vsync-clock pad script behind PS2X_PAD_SCRIPT_CLOCK (default wall)` |
| `d85e293` | `[E33] DEV-ONLY per-vsync VU1/GIF/GS census behind PS2X_GFX_STATS (default off)` |
| `03d6549` | `[E33] Resume budget-exhausted VU1 programs to their end marker (H1 fix)` |

Push receipt: `git push fork ssx3` → `e57b5f8..03d6549 ssx3 -> ssx3`;
`git ls-remote fork ssx3` = `03d6549a229d89324fb5388f79a326fcd0a4fcb7baf302e2496bf1e`.
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` is empty.
Pre-push gate: suite 472/472 + flags-unset boots e33eq/e33eq2 match E32
boot (a) terminal state (park pc=0x3b1028, final `fnv1a=fd889dc5`).

## Change 1 — `PS2X_PAD_SCRIPT_CLOCK=vsync` (`071d240`)

Entries' `t_ms`/`hold_ms` count guest time (`vsyncTick × 100000/5994` ms)
when set to `vsync`; unset = today's wall clock. Tick is read from the GS
vsync register at each pad read (null runtime in tests = 0). Test hooks
`setPadScriptVsyncClockForTest` / `setPadScriptVsyncTickForTest`; one new
pad test (tick→ms mapping drives presses). Armed line gains `clock=wall|vsync`.

## Change 2 — `PS2X_GFX_STATS` (`d85e293`)

New header-only module `ps2xRuntime/include/ps2_gfx_stats.h` (ps2_e3.h
pattern): one line per guest vsync with MSCAL/MSCNT, VU1
cycles, budget-exhausted programs, max single-program cycles, XGKICKs,
GIF packets/bytes per PATH1/2/3, draw kicks per path with vertex count
and xyz box, top-5 (TBP0, PRIM). `PS2X_GFX_STATS_FROM/_TO` window
(inclusive), hard cap 20,000 lines, per-line flush (tail-able). Unset =
one relaxed check per event, no I/O. Windows cut at VBlankStart; events
before the first observed VBlank open no window; trailing partial window
not flushed.
Wiring: VIF MSCAL/MSCALF/MSCNT notes; VU1 `run()` records cycles-used and
budget-without-end; `startXgkick` notes kicks; new `GifArbiter`
packet-listener (drain fires it before each process call) feeds the GIF
census and `GS::noteGifPath` draw attribution (default Path1); draw note
in `vertexKick` under `drawing && m_backend`; `noteVsync` in the
scheduler VBlankStart. Seven tests (line format, window filter, VU1
budget, VIF counts, arbiter listener, GS draw attribution, default-off).

## Build + suite

`~/dev/ssx3-work/E32-build` reconfigured in place
(`-DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF`;
E32 left aggressive ON) and rebuilt. Suite from the fork root, all
feature flags unset: **472/472, rc 0** (463 E32 + 1 pad vsync + 7 stats
+ 1 fix test). Two self-found failures on the way, both test-side:
ofstream buffering (added per-line flush) and test packets re-sending
PRIM per loop (PRIM resets the vertex queue; resent once).

Runner SHAs: pre-fix `ea0ed728…ac8` (two matching reads separated by
boots); fix `97a9e4a7c…bf1e` (two matching reads).

## Vsync-clock script (converted from E31 e31l route)

Calibration: e31l ran on the laptop, so wall times don't transfer — but
guest ticks do. Interpolated the tick at each e31l press wall from the
e31l snap curve (`frames-e31l-1/snap`, 279 pts), converted with
`ms = tick × 100000/5994`, rounded down, holds ≈ laptop guest durations:

| # | Button | e31l wall (s) | tick | guest ms | hold ms |
|---|---|---|---|---|---|
| 0 | start | 25.04 | 622 | 10350 | 2500 |
| 1 | cross | 50.03 | 1238 | 20650 | 2000 |
| 2 | cross | 76.81 | 1391 | 23200 | 400 |
| 3 | cross | 101.64 | 1439 | 24000 | 400 |
| 4 | cross | 125.04 | 1852 | 30890 | 1700 |
| 5 | cross | 150.04 | 2371 | 39560 | 1750 |
| 6 | down | 172.01 | 2832 | 47240 | 4200 |
| 7 | cross | 195.05 | 3324 | 55450 | 1800 |
| 8 | cross | 220.01 | 3892 | 64920 | 2000 |
| 9 | cross | 470.10 | 6794 | 113340 | 800 |
| 12 | down (tuck) | 470.10 | 6794 | 113340 | 20000 |
| 10 | cross | 505.12 | 7089 | 118270 | 700 |
| 11 | cross | 540.08 | 7344 | 122510 | 700 |

Script string:

```
10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000
```

Live proof the clock works: Boot A log shows
`armed n=13 clock=vsync`, `press i=0 now=10360ms`, `press i=1 now=20653ms`
— guest-ms fire times land on the anchors.

## Boots (all Mac mini, E32-build, lease-claimed, rc 0)

| Boot | Script / env | Result |
|---|---|---|
| e33eq | flags-unset, wall 120 | EQUIVALENT to E32a: DEV-SKIP×0, park pc=0x3b1028, final `fnv1a=fd889dc5` (GetPicture/feedES log lines absent — brief-mandated logs-off build, guest state identical) |
| e33a (A) | vsync route, wall 300, stats 1200–1500 | Select Character settled (tick 1350 snap); 173 stats lines 1200–1372; only i=0/i=1 fired (mini char-idle ≈ 0.4 tick/s) |
| e33b (B) | vsync route, wall 700, stats 7200–7800 | **Race reached**: i=10 dismissed pre-race early (mini drift ~250 ticks), HUD 2ND/2 00:00:03 1% at tick 7288; 88 stats lines 7200–7287; i=11 never fired |
| e33eq2 | flags-unset + fix, wall 120 | EQUIVALENT (same three rows as e33eq) |
| e33ap (A') | vsync route + fix, wall 450, stats 1200–1500 | tick 1282 only (fix ~2× slower/vsync); Zoe absent; exhausted 8466 |

Mini tick-rate notes (for the next lane): menus ~30/s, loading
~10–15/s, char-select idle ~0.4/s, pre-race ~0.8/s. E32b's char-idle
rate matches (0.4/s) — no anomaly, just a heavy scene.

## Per-vsync tables

Raw files under `~/dev/ssx3-work/E33-run/` (text, no compression needed):

| File | Lines | SHA256 |
|---|---|---|
| `gfx-stats-e33a.txt` (1200–1372) | 173 | `1fffd33c…2ea52acfd` |
| `gfx-stats-e33b.txt` (7200–7287) | 88 | `60dc96c1…0774f8a727` |
| `gfx-stats-e33ap.txt` (1200–1281) | 82 | `e87a5cf0…8a32939b4c99` |

Boot A settled (Select Character idle, 1300–1372, 73 lines, all
bit-identical): `mscal=583 mscnt=0 vu_cycles=32645598 vu_exhausted=498
vu_maxcyc=65536 xgkick=85 p1_pkt=85 p2_pkt=194 p3_pkt=3 d1_n=170/510v
d2_n=880/1990v d3_n=33/66v top=0:6,0:4,0:3,112:6`. Transition 1260–1263:
menu (85,0) → 3 idle vsyncs (0 MSCAL) → char 3D (583, 498).
Boot B pre-race→race (7200–7287): mscal 0–573, exhausted 0–166,
maxcyc 65536, mscnt always 0; PATH1 draws dominate (d1_n to 10285, box
0.00,3071.50×0.00,3071.50 — full-screen, not degenerate). Race line
7287: `mscal=573 exhausted=143 xgkick=382 d1_n=9933`.
Boot A' line 1281: `mscal=583 exhausted=8466 cycles=554836446`,
kicks/packets/draws/verts/top **byte-identical to pre-fix line 1350**.

## H1/H2/H3 read-out (evidence, not verdict)

- **H1 budget truncation: SHOWS on both screens.** Char settled:
  498/583 programs spend the full 65536-cycle slice with no end marker,
  `mscnt=0` so none is ever resumed — dropped every vsync, 73/73 lines
  identical. Pre-race/race: up to 166/573, also `mscnt=0`.
- **H2 GS-side: not separated.** Draws are plentiful whenever programs
  complete (880–9933/vsync); pixels still missing. Consistent with H1
  (the missing draws are the dropped programs') but a GS-side drop of
  specific batches is not ruled out.
- **H3 VU1 math/unpack: disfavored for issued draws.** Recorded boxes are
  screen-covering (char d1 1741–2359×1799–2325; race d1 0–3071×0–3071),
  never degenerate/off-screen. No position data exists for the
  never-issued draws.

## Fix result (negative)

`executeToEnd`/`resumeToEnd` (cap 16) in the VIF1 callbacks; unit test
proves the mechanism (runaway caps at 16 and terminates; E-bit needs 0;
two-slice program finishes with exactly 1 continuation — all in suite).
Boot A': Zoe absent on Select Character (snap-0118.49s, SHA below);
`vu_exhausted` 498 → 8466 (slice count, ≈17×); VU cycles 32.6M →
554.8M/vsync; kicks/packets/draws/verts/top all identical. The extra
522M cycles issue zero new work: the truncated programs spin without
XGKICKing — they are stuck, not long. Truncation is a symptom.
Recommended next action: **revert `03d6549`** (2× boot tax, no gain) and
diagnose per-program (record startPCs of exhausted programs; pc trace
across slices to separate spin-wait-on-unmodeled-condition from
interpreter loop-semantics gaps). No tuning loop was run, per the brief.

## Frames (path + SHA, viewed by eye)

| Point | File | Bytes | SHA256 | Shows |
|---|---|---|---|---|
| A Select Character settled, tick 1350 | `E33-run/frames-e33a-1/snap/snap-0238.52s.png` | 209622 | `f9539f35…5d4eb14cde` | Zoe name+bars+silhouettes, **no 3D rider model** |
| B race HUD 00:00:03, tick 7288 | `E33-run/frames-e33b-1/upload-latest.png` | 71275 | `24dff495…21e508d2d1` | 2ND/2, 1%, SUPER UBER, EA RADIO, near-black 3D |
| A' Select Character, tick 1275 | `E33-run/frames-e33ap-1/snap/snap-0118.49s.png` | 208558 | `d88cbf58…b122fc1c` | same as A, **Zoe still absent** |

## Gaps / notes

- Boot B captured only ~25 race vsyncs (7260–7287), not ~300: the mini
  pre-race runs ~0.8 tick/s and i=10 dismissed early. A 300-race-vsync
  window needs ~1000+ s wall — over cap, needs orchestrator OK.
- A' reached tick 1282, not the 1300–1372 settled band (fix slowdown);
  comparison used line 1281 vs A line 1350 (same scene, counts equal).
- Lease contention: T48 held the P-lane lease ~01:32–01:50Z, G lane
  ~02:2x–02:3xZ; one refused Boot B launch, several waits. No lane
  violated the lease; total time box respected (~5 h elapsed 21:00–23:10Z
  incl. waits).
- E32-build config changed per brief (RUNTIME+AGGRESSIVE logs OFF);
  E32-era log-line comparisons (GetPicture/feedES) rest on frame hash +
  park PC instead.
- Mini char-idle (0.4 tick/s) is 5× slower than the laptop (1.9/s);
  cause not investigated (scene-bound, matches E32b).
- Disk: 17.0 → 26.6/200 GB total (lanes share the box); E33-run 174 MB,
  well inside the 10 GB brief cap. Stats files < 100 KB, uncompressed.

## Exact commands

```
cmake -S ~/dev/PS2Recomp -B ~/dev/ssx3-work/E32-build -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
cmake --build ~/dev/ssx3-work/E32-build -j4
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ... ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 472/472 from ~/dev/PS2Recomp
python3 local/research/E32/e32_boot.py --label e33eq --wall 120
python3 local/research/E33/e33_boot.py --label e33a --wall 300 --snap 2.0 --stats-from 1200 --stats-to 1500 --script "<route>"
python3 local/research/E33/e33_boot.py --label e33b --wall 700 --snap 2.0 --stats-from 7200 --stats-to 7800 --script "<route>"
python3 local/research/E32/e32_boot.py --label e33eq2 --wall 120
python3 local/research/E33/e33_boot.py --label e33ap --wall 450 --snap 2.0 --stats-from 1200 --stats-to 1500 --script "<route>"
git push fork ssx3  # e57b5f8..03d6549
```

(`<route>` = the script string in the table above.)
