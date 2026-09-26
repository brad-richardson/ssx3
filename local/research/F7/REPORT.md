# F7 — device build with MTVU + VU1 blocks + the fixed Vulkan present

Worker: muse. Brief: `local/muse/prompts/F7.md` (Parts 1+2; stop before
the Odin play install and the iPhone install) plus two orchestrator
updates: (1) fork `ssx3` `a5e5940` = `703a554` + Android-only `-O3`
(BA1, gradle flags only) — Part 1 stays on MT1's APK for the knob
comparison, Part 2 iOS builds from `a5e5940`; (2) fork `ssx3` `5d5c382` =
`a5e5940` + VR3's VU0 recompile — remaining Odin legs may switch to VR3's
APK if verified `-O3` and from `5d5c382`, add a VU0 pair (F = best knob
set, G = F + VU0 knobs), launch budget raised to 12.

**Status: done. Stopped before the Odin play install and the iPhone
install, as briefed. Hand back: Odin 1× pipelined 0.285× (knob 0, VR3
APK) → 0.425× (MTVU + blocks + LAG); VU0 neutral (1.000×, engagement
proven); iPad green with MTVU + blocks.**

## Pins

| Item | Value |
| --- | --- |
| Fork `ssx3` (Odin MT1 APK) | `703a5548bbe4dd851d9a094902e3645f3b0a1264` (pushed, verified) |
| Fork `ssx3` (Odin VR3 APK) | `5d5c382` (pushed; `703a554` + BA1 `-O3` + VR3 VU0; `android/app/build.gradle` hash-identical to the APK source tree) |
| Fork `ssx3` (iOS build) | `a5e5940612e4dfdcaa98a6d1c49f6c221abf41c5` (pushed, verified; predates the VR3 fold — iOS has no VU0 image wiring in this build) |
| paraLLEl-GS `ssx3` | `1b3a2948cc55e74f975e42b79d08983f31c2dbb6` (pushed, verified); Granite `166ba21a` |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` (9,457 files) |
| VU1 images | `vu1gen-ssx3` = VR2's new set (`vu1gen-vr2d.sha`, 7/7 OK) |
| VU0 image | `vu0gen-ssx3` = `vu0_40829a098c260b4f.cpp` `2652966b…` (single file) |
| MT1 APK (C0, C0b, A) | `b91f827f30e89d3bdd28662c82b934d9e5e51430a55c518673240b5f4badaf42` (192,206,412 B; local ×4 + installed base.apk per leg) |
| VR3 APK (B–G2) | `825b436dd2cfc9f3ee42e7ac06643623b9651df409892c6a3e25af27cc531254` (190,748,236 B; remote ×2 + pulled ×2 + installed base.apk per leg) |
| iPad bundle | `7C9BE9DF-…` (seq 2004; signed `60ac6331…`) |

## Part 1 — Odin

### APK verification

MT1 reuse: `b91f827f…` read ×4 locally (all match; no rebuild).
VR3 switch (all verified before leg B):
- APK `825b436d…`: remote ×2 + pulled ×2, all match; 190,748,236 B =
  VR3's receipt (`local/research/VR3/android-vr3.txt`).
- Source = `5d5c382`: bytesize `/home/brad/vr3/PS2Recomp/android/app/build.gradle`
  hashes `fa864116…` = `git show 5d5c382:android/app/build.gradle` exactly
  (carries both the `-O3` lines and the `-Pps2xVu0RecompDir` wiring).
- Built `-O3`: the APK's own `.cxx/RelWithDebInfo/.../CMakeCache.txt` reads
  `CMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING=-O3 -g -DNDEBUG` (answers the
  orchestrator's `-O2?` question: no, it is `-O3`).
- VU0 input: `/home/brad/vr3/vu0gen/vu0_40829a098c260b4f.cpp` = `2652966b…`
  = the mini's canonical `vu0gen-ssx3`.

### Method

F6 method: `local/research/F7/launch.py` + `cooldown.py` (F6 lineage: F7
dirs/lease, `--env K=V` added for every knob, atomic claim/release through
`local/tooling/odin_lease.sh`), I26-FAST, unpaced, sound on, pipelined 1×,
stop 4500, cool to status 0 + fixed 180 s. Every leg pins
`PS2X_GAME_THREAD_CPUS=6 PS2X_MTVU_CPUS=7`. `restore-play.sh` (F6's) after
every leg; env `a8d651a7…` + save 6/6 + `mc0-test` empty verified each time.

Race rate = (STOP_tick − 1714) ÷ wall(STOP), wall interpolated from the
`[vsync-rate]` points exactly as `local/research/F4/phases.py` does (F6's
table definition). On three fast legs the sparse vsync-rate sampler emits
one extra point during wind-down (logcat-last > STOP: C 4721, E2 4733, D2
4709); the STOP-capped numbers below are primary and the raw `phases.py`
rows stay in the per-leg receipts.

### Legs (12/12 launches; order run: C0 C0b A B C D E A2 E2 D2 G G2)

| Leg | APK | Env (beyond pins) | End | Race (ticks→wall) | Race rate | GPU busy race mean (n) | Thermal | `[mtvu]` waits / violations | `[present-vk]` | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0 census | MT1 | `PS2X_MTVU=census`, OUT=/data… (unreadable, see gaps) | STOP 4549, 218 s | 1714→4549 / 174.5 s | 16.25/s = **0.271×** | 36.9 % (29) | 0→2 | census, 0 | dropped 0, timeouts 0 | 0 |
| C0b census | MT1 | `PS2X_MTVU=census`, OUT=$FILES (pulled) | STOP 4533, 216 s | 1714→4533 / 174.8 s | 16.13/s = **0.269×** | 37.6 % (29) | 0→3 | census, 0 | dropped 0, timeouts 0 | 0 |
| A knob 0 | MT1 | (none) | STOP 4517, 216 s | 1714→4517 / 174.6 s | 16.05/s = **0.268×** | 37.1 % (29) | 0→3 | n/a (knob off) | dropped 0, timeouts 0 | 0 |
| B blocks | VR3 | `PS2X_VU1_BLOCKS=1` | STOP 4529, 196 s | 1714→4529 / 155.9 s | 18.05/s = **0.301×** | 40.6 % (26) | 0→2 | n/a | dropped 0, timeouts 0 | 0 |
| C mtvu | VR3 | `PS2X_MTVU=1` | STOP 4587, 168 s | 1714→4587 / 126.7 s | 22.67/s = **0.378×** | 51.0 % (22) | 0→3 | vblank 2951/101.3 s, 0 | dropped 0, timeouts 0 | 0 |
| D mtvu+blocks | VR3 | `PS2X_MTVU=1 PS2X_VU1_BLOCKS=1` | STOP 4574, 162 s | 1714→4574 / 122.1 s | 23.43/s = **0.391×** | 52.7 % (20) | 0→3 | vblank 2929/95.5 s, 0 | dropped 0, timeouts 0 | 0 |
| E D+LAG | VR3 | D + `PS2X_MTVU_LAG=1` | STOP 4584, 151 s | 1714→4584 / 112.8 s | 25.45/s = **0.425×** | 57.9 % (19) | 0→3 | vblank 2921/85.4 s, 0 | dropped 0, timeouts 0 | 0 |
| A2 knob 0 | VR3 | (none) | STOP 4532, 206 s | 1714→4532 / 165.3 s | 17.05/s = **0.284×** | 38.3 % (28) | 0→3 | n/a | dropped 0, timeouts 0 | 0 |
| E2 = F (E repeat) | VR3 | E env | STOP 4588, 153 s | 1714→4588 / 112.9 s | 25.46/s = **0.425×** | 58.0 % (19) | 0→3 | vblank 2914/84.9 s, 0 | dropped 0, timeouts 0 | 0 |
| D2 (D repeat) | VR3 | D env | STOP 4569, 164 s | 1714→4569 / 122.0 s | 23.40/s = **0.390×** | 52.9 % (19) | 0→3 | vblank 2938/95.7 s, 0 | dropped 0, timeouts 0 | 0 |
| G = F+VU0 | VR3 | F + `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1` | STOP 4585, 153 s | 1714→4585 / 112.8 s | 25.44/s = **0.424×** | 57.3 % (18) | 0→3 | vblank 2912/90.5 s, 0 | dropped 0, timeouts 0 | 0 |
| G2 (G+STATS proof) | VR3 | G + `PS2X_VU1_RECOMP_STATS=1` | STOP 4604, 152 s | 1714→4604 / 112.9 s | 25.59/s = **0.427×** | 58.0 % (19) | 0→3 | vblank 2912/90.1 s, 0 | dropped 0, timeouts 0 | 0 |

`[mtvu]` waits = cumulative vblank waits at tick 4500; `jobs=55501` on
every threaded leg (deterministic job count). Thermal = `thermal.txt`
status first→last. `[present-vk]` = `vk_dropped=0 vk_cb_timeouts=0
vk_fence_timeouts=0` on all 12 legs (`vk_fences_held=1`).

Ratios on the VR3 base (vs A2 17.05/s): B **1.059×**, C **1.330×**, D
**1.374×**, E **1.493×**; D/C = 1.034× (blocks on top of MTVU); E/D =
1.086× (LAG on top). A2/A = **1.062×** (the `-O3` step, cf. BA1's 1.053×;
VR3's knobs-off code is also present). Repeats: E2/E = 1.000×, D2/D =
0.999× (ABBA order D E E2 D2). VU0: G/F = **0.999×** (neutral), G2/G =
1.006×. Vs F6's 1× pipelined 15.75/s: E is **1.616×**.

Cool-downs (all green, status 0 at launch, 100 % on AC): C0 34.5→34.5 °C
(immediate 0 + 180 s); C0b 39.9→36.4; A 46.9→39.1; B 48.0→39.5; C
46.9→38.4; D 47.7→38.7; E 46.5→37.6; A2 48.4→38.4; E2 46.9→38.4; D2
48.0→38.0; G 47.7→38.0; G2 37.6→36.0. Every run: atomic lease claim,
keyguard false, 100 % on AC, app stopped, Brad env + mc0 pins before, env
restored + `restore-play.sh` after, force-stopped, lease released, 0
disconnects.

Per-phase table (guest vsyncs/s; `phases.py` raw rows — race column differs
from the STOP-capped table above on C0/C/E2/D2 only):

| Phase | C0 | C0b | A | B | C | D | E | A2 | E2 | D2 | G | G2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| title/startup | 57.11 | 56.93 | 56.95 | 56.74 | 56.80 | 56.77 | 56.68 | 56.44 | 56.55 | 56.47 | 56.32 | 56.37 |
| main menu | 60.06 | 57.67 | 58.54 | 58.87 | 60.10 | 59.95 | 60.04 | 58.74 | 60.08 | 60.10 | 60.08 | 59.94 |
| Select Character | 60.06 | 57.67 | 58.54 | 58.87 | 60.10 | 59.95 | 60.04 | 58.74 | 60.08 | 60.10 | 60.08 | 59.94 |
| Setup Character / Peak | 59.98 | 62.18 | 61.17 | 60.94 | 59.95 | 59.95 | 60.00 | 61.14 | 60.00 | 60.00 | 60.01 | 60.00 |
| Select Mode / Event / My Rules | 55.76 | 55.02 | 54.75 | 55.53 | 55.05 | 54.89 | 54.75 | 54.77 | 55.21 | 60.00 | 54.92 | 60.00 |
| loading + Rival card | 24.40 | 25.64 | 25.31 | 28.39 | 30.28 | 31.70 | 34.68 | 26.92 | 35.05 | 29.69 | 34.75 | 32.90 |
| race (raw) | 16.35 | 16.13 | 16.05 | 18.05 | 22.83 | 23.43 | 25.45 | 17.05 | 25.61 | 23.58 | 25.44 | 25.59 |

### Census (C0b file pulled; C0's lost to file perms)

C0b: `~/dev/ssx3-work/F7/odin/C0b/census-c0b.txt`, 3,596,527 B, 110,379
events. Final line: `jobs=33373 fifo=13284 unit_ms=93532.9
snap_bytes=7510032 snap_ms=1.69 violations=0 hits: vblank=4500/4436
gsprivread=2/0 gsprivread-masked=244351/13278 gsprivwrite=48784/0
vif1reg=2/0` (C0's logcat agrees: `jobs=33380 … violations=0`,
masked 220479/13281 — spin counts vary run to run). `PS2X_MTVU_CENSUS_OUT`
under `/data/local/tmp` is unreadable to shell (app-owned 0600, release
APK not debuggable); `$FILES` works — C0b re-ran with that path.

`mtvu_sim.py` on the C0b file, race t1800–2400 (model, not speed): sync
frame 73.0 ms (EE 34.2 + unit 38.8, 8.0 jobs/frame). S1 (MTVU as shipped)
**1.377×** ideal / 1.281× costed (`--submit 2000 --wake 20000 --slow
1.10`); S3 (LAG) **1.788×** / 1.679×. Measured on the VR3 base: C/A2 =
1.330× (between the S1 ideal and costed lines) and E/A2 = 1.493× (under
the S3 costed line — the model ignores GS-worker contention and the
census ran on the MT1/`-O2` base, see gaps).

### VU0 pair

G (F + `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1`) = 25.44/s vs F 25.45–25.46/s:
**0.999× — neutral** on the Odin race. Engagement is proven, not assumed:
G2 adds `PS2X_VU1_RECOMP_STATS=1` and logs `[vu0-recomp] runs=3735552
generated_cycles=234575976 interpreted_cycles=0 generated_share=1.0000`
(VU1 likewise 1.0000). G2's rate (25.59/s) agrees with G, so the stats tap
costs nothing measurable.

### Screencaps viewed (all 1920×1080, full-screen, no borders)

| Cap | Verdict |
| --- | --- |
| C0 `sc01-tick2100` | Race 2ND/2 00:00:06 1 %, rider mid-crash wipeout with board up, RECOVER meter, EA Radio "Avalanche / Powerplant", correct colours |
| C0b `sc01-tick2100` | 00:00:07, rider down in snow with spray, HUD crisp |
| A `sc01-tick2100` | 00:00:07, rider mid-crash with spray, 15 MPH |
| B `sc01-tick2100` | 00:00:06, rider mid-crash arms up, EA Radio "Glass Danse - Oakenfold Remix / The Faint" |
| C `sc01-tick2100` | 00:00:06, trick 310, rider solid mid-carve with spray, EA Radio "Ride / Deepsky / In Silico" |
| D `sc01-tick2100` | 00:00:08, rider in spray cloud carving, carve groove trailing, 15 MPH |
| E `sc01-tick2100` | 00:00:08, rider in spray, board visible, groove trailing, 14 MPH (no LAG artifact at this tick) |
| A2 `sc01-tick2100` | 00:00:07, rider down in spray cloud, groove trailing |
| E2 `sc01-tick2100` | 00:00:08 2 %, rider solid mid-carve with spray + groove, 15 MPH |
| D2 `sc01-tick2100` | 00:00:07, rider mid-crash in spray, groove trailing |
| G `sc01-tick2100` | 00:00:08 2 %, rider solid mid-carve with spray + groove, 16 MPH |
| G2 `sc01-tick2100` | 00:00:09 2 %, rider solid carving with spray, 15 MPH |

EA-Radio cards differ run to run (Avalanche / Glass Danse / Ride) — the
known device RNG divergence class (F6 G3), not chased.

## Part 2 — iOS (device build `a5e5940`, iPad MTVU + blocks; iPhone stopped)

Source: pushed fork `ssx3` `a5e5940` in a detached worktree
`~/dev/ssx3-work/F7/PS2Recomp` (clean). First-failure rule never triggered.
No push. (The orchestrator's `a5e5940` update landed after the F7 worktree
was cut at `703a554`; the worktree was moved to `a5e5940` before
configure. The delta is the Android-only `-O3` gradle file — no iOS
effect. This build predates the VR3 fold: no VU0 image wiring.)

**Result: iPad green on MTVU + blocks. Stopped before the iPhone install.**
One device build (14,343 `VU1RecompImage` symbols, the exact F5/F6 count);
bundled env = F5's plus `PS2X_MTVU=1` and `PS2X_VU1_BLOCKS=1` (committed at
`local/research/F7/ps2x.env`, SHA `cffff3e8…`). One fresh-card iPad launch:
parallel backend, `ssaa=4 hires_scanout=1 present_pipeline=1`,
1280×896→1024×896 scanout, 4× `ios bind … rc=0`, stats
`readback_ms_avg=0 copy_ms_avg=0 l2h_bytes=0` (zero-copy kept), `[mtvu]
mode=threaded` + 7 summary lines all `violations=0`, 0 FATAL, race reached
in 49 s wall. Frames viewed: Select Event, race start, and t2100 with
rider + spray; pad v2 in place. Brad's `mc0` byte-identical after (deploy
re-ran: 7 OKs). One knobs-off launch (`PS2X_MTVU=0 PS2X_VU1_BLOCKS=0`) for
a diagnostic pace comparison: 57 s wall vs 49 s (labelled diagnostic:
console-pty + vsync-rate overhead, one run each — not a speed number).

Recipe: `~/dev/ssx3-work/F7/ios/build-install.sh` = F6's script +
`W`/`FORK_WT`/`PGS→F7`/`PIN→a5e5940`/`ENVFILE→F7/ps2x.env`
(`VU1GEN→vu1gen-ssx3` and `MVK→moltenvk-1.4.2` unchanged);
`ipad-probe.sh`/`ipad-run.sh` from F6's copies (`OUT` repointed). No sim
build (F3 precedent plus I33's sim descriptor-indexing blocker).

| Item | Pin | Receipt |
| --- | --- | --- |
| Fork worktree `~/dev/ssx3-work/F7/PS2Recomp` (detached) | `a5e5940612e4d…` == `fork/ssx3` at build time, clean | `logs/fork-head.txt`, preflight rc=0 (runner-dir diff empty, PIN ancestor) |
| parallel-gs (F7 clone) | `1b3a2948cc55…`, clean; Granite `166ba21a` | preflight re-hashed |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` (9,457 files) | `logs/codegen-sha.txt` |
| VU1 images (`vu1gen-ssx3`) | 7/7 SHAs match `vu1gen-vr2d.sha` | `logs/vu1-sha.txt`; configure `VU1 recomp: 7 images` |
| MoltenVK 1.4.2 device slice | staged `6cd58884…` = F5/F6 pin | `logs/device-mvk-stage-sha.txt` |
| ELF / ISO staged | `1b49d05c…` / `3c2f8eb1…` | stage SHAs |
| Bundled env `local/research/F7/ps2x.env` | SHA `cffff3e8…` (= staged copy) | `logs/env-sha.txt` |
| Device binary unsigned | `ff5bf443…` (×2), 159,681,384 B | `logs/device-source-binary-sha.txt` |
| Device binary signed (installed) | `60ac6331…` (×2) | `logs/signed-binary-sha.txt`; `codesign --verify --strict` passed |

iPad (Air 11" M2): install rc=0 (seq 2004, bundle `7C9BE9DF-…`); deploy
SKIP + 7 OKs; probe Data `400013A5-…` (bundle path matches install URL).
One fresh-card launch (`mc-f7`, route byte-exact vs bundled, re-armed via
env JSON, `PS2X_VSYNC_RATE_LOG=1`, no backend overrides): 49 s wall,
ticks 1200/1917/2100, terminated after (0 procs left), zero FATAL.
`[vu1-blocks]` has no line in release builds (counters are compiled under
`PS2X_ENABLE_DET_HASH_TAP` only — verified in source); `[ios-env] set
PS2X_VU1_BLOCKS=1` confirms the knob reached the runtime. Same applies to
the Odin APK legs (brief's "`[vu1-blocks]` if present" — absent as
expected, engagement proven by the B/A2 and D/C deltas).

| Shot (tick) | Viewed verdict | SHA-256 (12) |
| --- | --- | --- |
| `shot-t1090` (1200) | Select Event (Snow Jam / Metro-City / Happiness + Race course map, legible), full brightness | `1d90b2db10d0` |
| `shot-t1810` (1917) | Race 2ND/2 00:00:03 1 %, EA Radio "Poor Leno - Silicon Soul Remix / Royksopp" (same card as F6's iPad run), rider mid-air with spray | `aa9b560e9be0` |
| `shot-t2100` (2100) | Race 2ND/2 00:00:06 1 %, 14 MPH; rider mid-trick upside down, board visible, spray + groove trailing; rider solid, no translucent boxes | `356ebba3c2bc` |

Pad v2: D-pad, face buttons, shoulders in place; only the known
portrait-compat SELECT/START overlap (I28, pre-existing). Post-run deploy
re-ran: 7 OKs, Brad's `mc0` byte-identical. iPhone install stopped per the
brief (never launched, never installed — no command targeted the iPhone
UDID).

## Budgets and gaps

- Builds: 1 iOS device (+ stage/sign), 0 Android (MT1 reuse verified, VR3
  reuse verified — no rebuild). Boots: 1 iPad probe + 2 iPad tests (49 s,
  57 s), 12 Odin legs (C0–G2, 151–218 s wall each; all ≤ 600 s). Nothing
  exceeded its cap.
- Scratch `~/dev/ssx3-work/F7`: **5.2 GB** (≤ 20 GB brief cap).
- Global mini usage 85.0/200 GB after F7 (was 73.9 before).
- Never pushed; fork worktree detached at `a5e5940`; text in git
  (REPORT, `ps2x.env`, 2 Odin scripts, per-run text logs); runners
  signalled only by the drivers; no lease held at close (`LEASE_FREE F6
  done` — F6's restore script writes its own label); BA1/VK2 lanes'
  files untouched.
- End state: Brad's F5 play APK `4ff81032…` installed, env `a8d651a7…`,
  save 6/6 OK, `mc0-test` empty, app stopped, 100 % on AC. No play-build
  install and no iPhone install (both stopped per the brief).
- Gaps:
  - G1. C0's census file was written to `/data/local/tmp` (app-owned 0600,
    unreadable to shell on a release APK); C0b re-ran with `$FILES` and the
    file was pulled. C0's logcat census summaries are kept as a cross-check
    (jobs/unit_ms/hits agree with C0b). Cost: 1 extra launch (12/12 used).
  - G2. The census ran on the MT1/`-O2` base while the threaded legs ran on
    the VR3/`-O3` base, so the EE/unit split the model predicts from is not
    exactly the split the legs ran with. Direction-safe (S1 measured 1.330×
    sits between the model's 1.377× ideal and 1.281× costed), but the S3
    gap (measured E/A2 = 1.493× vs 1.679× costed) mixes this with the
    model's known blind spots (GS-worker contention, cache effects).
  - G3. Leg-A matrix note: A (knob 0) ran on the MT1 APK before the VR3
    switch; A2 re-baselines knob 0 on the VR3 APK. All knob ratios use A2.
  - G4. SF presents/s on the VK legs reads a flat 43–47 (the F6 G2
    stale-timestamp artifact); display-side only, guest ticks unaffected.
  - G5. Device EA-Radio RNG differs run to run (Odin) — known divergence
    class, not chased. iPad F7 matches F6's card ("Poor Leno") this time.
  - G6. D2/G2 `Select Mode / Event / My Rules` reads 60.00 (sparse-sample
    boundary interpolation in that short phase), not a real rate.
  - G7. VU0 on iOS is unmeasured (this iOS build predates the VR3 fold).
  - G8. `restore-play.sh` is F6's (per the brief); it removes only F6's
    device paths, so `/data/local/tmp/f7` PNGs persist between legs by
    design (pulled by the driver) — F7's start-of-run `rm` keeps it bounded.

## Exact commands

```sh
# pins
git -C ~/dev/PS2Recomp rev-parse fork/ssx3  # a5e5940 at iOS build; 5d5c382 by the VR3 switch
git -C ~/dev/parallel-gs rev-parse origin/ssx3  # 1b3a294
# iOS (Part 2)
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/F7/PS2Recomp 703a554  # then checkout a5e5940
git clone ~/dev/parallel-gs ~/dev/ssx3-work/F7/parallel-gs  # + checkout 1b3a294, submodules
bash ~/dev/ssx3-work/F7/ios/build-install.sh preflight configure_device build_device stage_device sign install_ipad
bash local/research/I31/deploy-ios.sh ipad; bash ~/dev/ssx3-work/F7/ios/ipad-probe.sh
bash ~/dev/ssx3-work/F7/ios/ipad-run.sh ~/dev/ssx3-work/F7/ios/run-ipad-f7 ~/dev/ssx3-work/F7/ios/run-ipad-env.json "1090 1810 2100"
bash ~/dev/ssx3-work/F7/ios/ipad-run.sh ~/dev/ssx3-work/F7/ios/run-ipad-f7-off ~/dev/ssx3-work/F7/ios/run-ipad-env-off.json "1090 1810 2100"  # knobs-off diagnostic
bash local/research/I31/deploy-ios.sh ipad  # byte-identical after; STOP before install_iphone
# Android (Part 1)
shasum -a 256 ~/dev/ssx3-work/MT1/odin/app-release.apk  # ×4 b91f827f (reuse, no rebuild)
ssh bytesize 'wsl -d Ubuntu -- bash -lc "sha256sum .../app-release.apk"'  # ×2 825b436d (VR3 verify)
ssh bytesize 'wsl -d Ubuntu -- bash -lc "sha256sum .../build.gradle; grep -n O3 ..."'  # fa864116 = 5d5c382
ssh bytesize 'wsl ... "grep -rh CMAKE_CXX_FLAGS_RELWITHDEBINFO .../CMakeCache.txt"'  # -O3 -g -DNDEBUG
ssh bytesize 'wsl -d Ubuntu -- bash -lc "cat .../app-release.apk"' > ~/dev/ssx3-work/F7/odin/app-release-vr3.apk  # ×2 local
# Odin (Part 1)
python3 local/research/F7/cooldown.py --label <LEG>
python3 local/research/F7/launch.py --label <LEG> --variant A --wall 600 --stop-tick 4500 --apk <APK> --apk-sha <SHA> --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 [--env <knobs...>]
python3 local/research/F4/phases.py local/research/F7/logs/<LEG>
python3 /tmp/f7_rates.py  # STOP-capped race rates + GPU/thermal/mtvu aggregation
python3 local/research/MT1/mtvu_sim.py ~/dev/ssx3-work/F7/odin/C0b/census-c0b.txt [--submit 2000 --wake 20000 --slow 1.10]
bash local/research/F6/restore-play.sh  # after every leg
```
