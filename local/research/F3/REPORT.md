# F3 Part 1 — fold FP1 + DK1 + I34 + IN2 + UV1 + RD1 onto fork `ssx3`, Mac + Android check

Worker: Muse Code, brief `local/muse/prompts/F3.md` Part 1 only (+ orchestrator
addition: RD1 `51c759b` as the 7th commit). No push (orchestrator gates and
pushes). First-failure rule never triggered.

**Result: fold clean, Mac green, rider fixed, Android green.** All 7
cherry-picks applied with no conflicts; suite 642/642; B1 races with sound on
(cid0 531, coverage 0/0/4, alpha-255 frames viewed), B2 (sound off + unpaced)
is det-hash identical to B1 on all 2,437 common ticks, B3 is speed-neutral vs
F2 B3 (race 0.249× vs 0.250×), B4 shows the player rider solid and lit at
screen centre. APK from the RD1 tip builds successfully.

## Fold (worktree `~/dev/ssx3-work/F3/PS2Recomp`, branch `f3-fold` from `0ed07c4`)

`git cherry-pick -x` in brief order, all clean (IN2 auto-merged the
`ps2_virtual_pad.h` / test files I34 also touched — disjoint lines).

| # | Source | New SHA | Subject |
| --- | --- | --- | --- |
| 1 | `51e730f` | `4d69178` | [FP1] pace guest vsyncs to wall clock, PS2X_UNPACED=1 disables |
| 2 | `6cba433` | `cc54438` | [DK1] parallel Present: normalize presentation alpha to opaque |
| 3 | `3d52208` | `e21562d` | [I34] virtual pad v2: 1.5x stick, 80% D-pad below the face cluster |
| 4 | `43b61a4` | `f959f61` | [IN2] latch short taps until the guest reads them |
| 5 | `8545eb2` | `4a7475b` | [UV1] Default-off PS2X_VIF_FMT_LOG + PS2X_DMA_STALL_LOG per-vsync census |
| 6 | `6acf5bb` | `3a51ceb` | [UV1] Part 2: PCSX2 V2/V3 UNPACK lane rules + 10 unit tests |
| 7 | `51c759b` | `ec2dbf1` | [RD1] VU0 vf0 = (0,0,0,1) in every EE context, not only the main one |

Tip: `ec2dbf186616c7d6cf2998ea2792c500efdf4478`. `1f3180d` (RD1 probe)
skipped per the addition. `games/` untouched (no regen needed).
Runner-dir guard `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`:
empty (checked after pick 6 and after pick 7). `git diff --check 0ed07c4
HEAD`: clean. Total: 21 files, +1697/−80.

## Builds (one dir `~/dev/ssx3-work/F3/build`, F2 recipe flags)

Release, Homebrew clang, canonical codegen `8ea8ed43…` (no regen;
`games/` untouched), paraLLEl-GS `19d93b2` (reused F2's worktree as
`PS2X_PARALLEL_GS_SOURCE_DIR`, read-only), `GS_SHADOW_PARALLEL=ON`,
runtime/aggressive logs OFF, diag taps OFF. Det runners = incremental
reconfigure (`DET_HASH_TAP=ON`) after copying the clean runner out.
Configure + all builds rc=0 (only the usual duplicate-library link
warnings).

| Runner | Source tip | Det-hash tap | SHA-256 (staged read; boot prechecks re-read ×2) |
| --- | --- | --- | --- |
| `bin/runner-clean` | `3a51ceb` (pre-RD1) | OFF | `1fc49e48c190ed5e8d46e07acd98fe34e6c1bfca7d8377375d42d78331f604f8` |
| `bin/runner-det` | `3a51ceb` (pre-RD1) | ON | `cbe27f3a981722bdd4d3c7040da643746863bd7e9d9fe3101e6b60477dfa685a` |
| `bin/runner-clean-rd1` | `ec2dbf1` | OFF | `d94753b4f1f6cfd72d8928ab3d430830f1bd4e4ee667dd1ceba1993d20ee700b` |
| `bin/runner-det-rd1` | `ec2dbf1` | ON | `1ece20538f8a9838b83aaecc953e53ae28663d5da99f3bc1a81edae2df964b46` |

Suite from the worktree root: **641/641/0** at `3a51ceb` (612 F2 baseline
+ 7 FP1 + 11 IN2 + 10 UV1 + 1 I34 = 641 exactly), then **642/642/0** at
`ec2dbf1` (+1 RD1 vf0 test, passing). Both rc=0.

## Boots (I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, deterministic, paraLLEl + `PGS_HIER_BINNING=force`)

Driver: `f3_boot.py` (committed here; F2 driver + `--unpaced` for det mode,
needed for B2 — F2's driver only set `PS2X_UNPACED=1` in speed mode).
`[gs-path]` on all four boots: `hier_rule=hier-if-large … desc=plain …
gpu=Apple M5 Pro`. Boot-driver prechecks: two SHA reads match on
runner/ISO/ELF/codegen every boot; ISO `3c2f8eb1…`, ELF `1b49d05c…`,
codegen `8ea8ed43…` all pinned.

| Boot | Runner | Sound | Paced | Bound | Wall | Last tick | HUD wall | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 det | det (pre-RD1) | on | yes | target | 105.4 s | 2403 | 40.70 s | 0 |
| B2 det | det (pre-RD1) | off | no (`--unpaced`) | target | 102.9 s | 2405 | 37.43 s | 0 |
| B3 speed | clean (pre-RD1) | on | no (speed mode) | target | 86.3 s | 2471 | 36.44 s | 0 |
| B4 det | det-rd1 | on | yes | target | 94.5 s | 2405 | 37.42 s | 0 |

B1–B3 stay valid for everything else per the RD1 addition (same binaries,
same tip for their gates).

B1: `[snd-output] stream rate=48000` live; snd tick line `cid0=531 dmq=531
done=531`; coverage at vsync 2400 = `targets=0`, `ids=0`, `pairs=4` (the
E56 four SIDs — `0x80000211/0x237/0x534e44/0x80000006`, same list as F2).
B2: no `[snd-output]` (host stream off, as designed); same guest snd
cycles as B1 (`cycle=11550757345 ticks=3572` both); underruns 0 /
overflows as designed (sound-off shape matches F2 B2). B4: `cid0=531`,
coverage 0/0/4 — same gates hold with the rider fix.

**B1 vs B2 det-hash: 2,437/2,437 common ticks byte-identical, all fields,
0 differing payloads** (glue-immune regex extract; B1 ticks 1..2440, B2
1..2437 — settle overrun only). Paced+sound-on vs unpaced+sound-off
identical: the FP1 + AU10 properties both hold on the fold.

## Frames (B1 snapshotter picks by exact present tick from the sidecar)

DK1 check (stdlib `/tmp/f3_alpha.py`, all three B1 frames + B4 2099):
**alpha = 255 on 100.0% of pixels** (229,376/229,376), even-row mean 255.0,
odd-row mean 255.0 — the pre-fix 0x80 alternating rows are gone on the Mac
path. All 512×448 fbp 112, no tiles/stripes/corruption.

| Boot | Present tick | File (`run/<B>/frames/snap/`) | Viewed verdict |
| --- | --- | --- | --- |
| B1 | 1101 (sidecar 1102, `fnv=2fa435`) | `snap-001101t-0021.89s.png` | Select Mode (Race/Freestyle), Peak 1 panel still loading (~3 ticks after the Peak-1 press) |
| B1 | 1163 | `snap-001163t-0022.91s.png` | Same screen: Peak 1 course map fully populated — the t1101 empty panel is transition timing, not a regression |
| B1 | 1799 (`fnv=c2522f31`) | `snap-001799t-0048.88s.png` | Race 2ND/2 00:00:01 0%: gate, lit snow, pines, mountains, EA Radio "Go / Andy Hunter / Exodus" |
| B1 | 2099 (`fnv=4ebca52a`) | `snap-002099t-0076.90s.png` | Race 2ND/2 00:00:06 1%, checkpoint beam, trick 210, spray |
| B4 | 2099 (sidecar 2105, `fnv=79e2689d`) | `snap-002099t-0066.46s.png` | **Rider gate: PASS** — solid lit snowboarder at screen centre (dark outfit, arms up, board + shadow), race 2ND/2 00:00:06 1%, trick 280. Matches RD1's `rider-2100-before-after.png` "after" panel |

B1-vs-B4 det-hash (expected to differ — the fix changes guest state):
first differing tick **231**, `rdram`+`combined` only (`eeCycle` and
program count identical — same execution path, different matrix data, the
vf0-fix signature: the loader thread's bind matrices now compute). 923 of
2,440 common ticks differ.

## B3 per-phase vs F2 B3 (trace authoritative; guest vsyncs/s ÷ 59.94)

Exclusive lease (slot "both"; one 30 s retry — RD1 released quickly). Host
load at claim 3.4 → 2.3 at end (F2 B3: 1.9 → 1.7; RD1 had just released,
omlx + system background). The fold is speed-neutral.

| Phase (ticks) | F3 B3 vs/s (×) | F2 B3 vs/s (×) | F3 ÷ F2 |
| --- | --- | --- | --- |
| Title [0,636) | 40.26 (0.672×) | 40.32 (0.673×) | 1.00× |
| Menus [636,1440) | 77.11 (1.287×) | 76.96 (1.284×) | 1.00× |
| Loading [1440,1714) | 26.84 (0.448×) | 28.26 (0.472×) | 0.95× |
| Race-start [1714,1800] | 9.29 (0.155×) | 16.61 (0.277×) | — (quantization, see below) |
| **Race (1800,2400]** | **14.94 (0.249×)** | **14.98 (0.250×)** | **1.00×** |
| Raw 5 s race cross-check | n=8 mean 14.87 | n=8 mean 15.13 | 0.98× |
| Wall launch → race HUD (~t1714) | 36.44 s | 35.92 s | 1.01× |

Race-start note: the trace-interpolated 9.29 vs 16.61 is 5 s-quantization
noise on an 86-tick phase (`wall_at` uses the last stale trace row, so the
window stretches/compresses by up to 5 s depending on where the 5 s
`[vsync-rate]` boundary lands: F3's landed at t1796, F2's at t1803). The
raw 5 s windows covering the phase agree — F3 t1726 14.57/s + t1796
13.98/s vs F2 t1730 15.19/s + t1803 14.56/s (~4%, consistent with the
slightly higher host load). Real race-start ≈ 6.1 s vs ≈ 5.9 s. Loading
0.95× is the same load noise. B3 stopped at t2471 (71 over) vs F2's t2418:
speed-mode stop detection reads the 5 s `[vsync-rate]` lines, so the
overshoot is one window boundary, not slower running.

## Android compile check (bytesize `/home/brad/f3`, F2 recipe)

Staging: `PS2Recomp/` = `git archive` of the f3-fold tip streamed from the
mini over held ssh stdin (the fold is unpushed, so bytesize can't fetch
it): first `3a51ceb` (339 files = F2's 334 + 5 new F3 headers/tests),
then `rm -rf` + re-archive of `ec2dbf1` (339 files — RD1 adds none).
Tars kept both sides of the re-archive (`fork-3a51ceb.tar`,
`fork-ec2dbf1.tar`). `codegen-ssx3/`, `parallel-gs/`, `jniLibs/` are
symlinks to `/home/brad/f2/*` (F2 recipe inputs, unchanged per the brief;
the build only reads them), re-verified through the links: codegen 9,457
files, `register_functions.cpp` `8ea8ed43…`, SBR 623; parallel-gs 24,314
files + `PGS_HIER_BINNING` knob; jniLibs HAL `1b49d27c…` + Turnip
`717812c3…` (all match F2's pins).

Tree markers on bytesize: runner stub `cf62c485…` (1 upstream file);
`force_progressive` (ST1), alpha `255` (DK1), `-> uint64_t` at
`EeScheduler.cpp:2005` (HF1), `m_vsyncPace` (FP1), `Latch` (IN2),
`0.15f * u` (I34), `PS2X_VIF_FMT_LOG` (UV1), vf0 lines in `ps2_runtime.h`
(RD1). `build.sh` (committed here; F2 recipe with `root=/home/brad/f3`)
SHA `569db288…` identical local/remote. Bytesize idle for both builds
(load 0.00 / 0.91, no gradle/ninja).

| Build | Tip | Result | APK SHA-256 (remote ×2, pulled ×2, all match) |
| --- | --- | --- | --- |
| 1 (superseded) | `3a51ceb` | BUILD SUCCESSFUL in 5m 22s | `cb8f522d0e044c75200881b4ec19bed9e0b29527c85b52b867a0a99ca2dad6ca`, 153,769,544 B (kept as `odin/app-release-3a51ceb.apk`) |
| 2 (**Part 1 APK**) | `ec2dbf1` | BUILD SUCCESSFUL in 6m 35s, 48 tasks, zero FAILED | `d5a94c278aabac86fdf0b0570a6bb4f68680d2b5041bf595f86f3e271526ee78`, 153,769,544 B (`odin/app-release.apk`) |

+16,384 B over F2's APK (same delta as F1→F2). Part 3 rebuilds from the
pushed SHA if it differs from `ec2dbf1`.

## Budgets and gaps

Builds: 2 full Mac (clean + det reconfigure each: pre-RD1 and RD1 tip) +
2 Android. Boots 4/4 (B1 105 s, B2 103 s, B4 95 s one slot each; B3 86 s
exclusive), each ≤ 500 s wall cap. Scratch `~/dev/ssx3-work/F3` 2.4 GB ≤
15 GB (build dir deleted at close per the brief; worktree kept for the
push). Never pushed; fork branch `f3-fold` local-only; text in git
(`f3_boot.py`, `build.sh`, this report); runners signalled only by
recorded PID (SIGTERM via the driver); no lease held at close.

Gaps, stated plainly:

- G1. One speed run, no drift cancellation; B3 host load 3.4 → 2.3 vs F2
  B3's 1.9 → 1.7 (RD1 had just released the lease). Loading reads 0.95×
  and raw race 0.98× — within load noise; race trace matches at 1.00×.
- G2. Race-start trace number (9.29 vs 16.61) is 5 s-quantization noise
  (see §B3 note); raw windows agree. Short-phase trace rates need the
  boundary caveat whenever they're quoted.
- G3. B3 stop overshoot to t2471 (5 s `[vsync-rate]` stop detection).
- G4. Frame ticks within Δ11 of target (snapshotter phase, as F2).
- G5. B4-vs-B1 frame at 2099 is 6 ticks apart (sidecar 2099 vs 2105) —
  the rider gate is visual (solid + lit at centre), not a pixel diff.
- G6. `menu`/`title` B3 phases exceed 1× (77.11 vs/s) because speed mode
  is unpaced by design (FP1); paced play caps at 59.94 (FP1 Gate 1).
- G7. Share tier (`/Volumes/share`) not mounted: no receipt mirror.
- G8. The pre-RD1 APK (`cb8f522d`) is superseded but kept for the record;
  only `d5a94c27` (RD1 tip) is the Part 1 APK.

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/F3/PS2Recomp -b f3-fold fork/ssx3  # 0ed07c4
git -C ~/dev/ssx3-work/F3/PS2Recomp cherry-pick -x 51e730f 6cba433 3d52208 43b61a4 8545eb2 6acf5bb
git -C ~/dev/ssx3-work/F3/PS2Recomp diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner  # empty
cmake -S F3/PS2Recomp -B F3/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build F3/build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd F3/PS2Recomp && ../build/ps2xTest/ps2x_tests)           # 641/641
cp F3/build/ps2xRuntime/ps2EntryRunner F3/bin/runner-clean
cmake -S F3/PS2Recomp -B F3/build -DPS2X_ENABLE_DET_HASH_TAP=ON
cmake --build F3/build --parallel 8 --target ps2EntryRunner
cp F3/build/ps2xRuntime/ps2EntryRunner F3/bin/runner-det
python3 local/research/F3/f3_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400 --sound on --coverage-tick 2400
python3 local/research/F3/f3_boot.py --mode det --backend parallel --runner bin/runner-det --label B2 --stop-tick 2400 --sound off --coverage-tick 2400 --unpaced
python3 local/research/F3/f3_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B3 --stop-tick 2400
python3 local/research/GB8/gb8_rates.py ~/dev/ssx3-work/F3/run/B3
python3 /tmp/f3_hashdiff.py ~/dev/ssx3-work/F3/run/B1/boot.log ~/dev/ssx3-work/F3/run/B2/boot.log  # 2437/2437, 0 diffs
python3 /tmp/f3_alpha.py ~/dev/ssx3-work/F3/run/B1/frames/snap/snap-*.png  # alpha 255 everywhere
git -C ~/dev/ssx3-work/F3/PS2Recomp cherry-pick -x 51c759b  # RD1, -> ec2dbf1
cmake -S F3/PS2Recomp -B F3/build -DPS2X_ENABLE_DET_HASH_TAP=OFF && cmake --build F3/build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd F3/PS2Recomp && ../build/ps2xTest/ps2x_tests)           # 642/642
cp F3/build/ps2xRuntime/ps2EntryRunner F3/bin/runner-clean-rd1
cmake -S F3/PS2Recomp -B F3/build -DPS2X_ENABLE_DET_HASH_TAP=ON && cmake --build F3/build --parallel 8 --target ps2EntryRunner
cp F3/build/ps2xRuntime/ps2EntryRunner F3/bin/runner-det-rd1
python3 local/research/F3/f3_boot.py --mode det --backend parallel --runner bin/runner-det-rd1 --label B4 --stop-tick 2400 --sound on --coverage-tick 2400
git -C ~/dev/ssx3-work/F3/PS2Recomp archive HEAD | ssh bytesize 'wsl -d Ubuntu -- bash -lc "rm -rf /home/brad/f3/PS2Recomp && mkdir -p /home/brad/f3/PS2Recomp && cat > /home/brad/f3/fork-ec2dbf1.tar && tar -x -f /home/brad/f3/fork-ec2dbf1.tar -C /home/brad/f3/PS2Recomp"'
cat local/research/F3/build.sh | ssh bytesize 'wsl ... cat > /home/brad/f3/build.sh'  # SHA 569db288 both sides
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/f3/build.sh"'  # SUCCESS 6m35s (one held ssh)
ssh bytesize 'wsl ... cat .../app-release.apk' > ~/dev/ssx3-work/F3/odin/app-release.apk  # d5a94c27 x4
```

## Recommended next action

Push `f3-fold` (`ec2dbf1`) → fork `ssx3` (fast-forward from `0ed07c4`;
runner-dir guard empty, suite 642/642) and release F3 Part 2 (iPhone) and
Part 3 (Odin; rebuild the APK from the pushed SHA if it differs).

## Orchestrator gate, Part 1 (2026-09-25)

**Pass.** I viewed B4 t2093: race 00:00:06 with the player rider solid and lit at centre, full brightness,
trees, mountains, beam. Seven picks clean; suite 642/642; alpha 255 on every pixel; paced+sound-on and
unpaced+sound-off det-hash identical (FP1 and AU10 hold); Mac race speed-neutral (0.249×); the APK
builds from the RD1 tip (Android compile gate met). Pushed `f3-fold` → fork `ssx3` **`ec2dbf1`**
(fast-forward from `0ed07c4`). Parts 2 (iPhone) and 3 (Odin, APK `d5a94c27…` from `ec2dbf1`, over
Wi-Fi) released in parallel.

## Part 2 — iOS (device build `ec2dbf1`, iPad race, iPhone install-only)

Worker: Muse Code, brief `local/muse/prompts/F3.md` Part 2 only. Source:
pushed fork `ssx3` `ec2dbf1` (reused the Part 1 worktree
`~/dev/ssx3-work/F3/PS2Recomp`; `HEAD == fork/ssx3` after fetch, clean).

Builds (`~/dev/ssx3-work/F3/ios/build-install.sh` = I33 recipe + 3-line
sed: `W`, `FORK_WT`, `PIN→ec2dbf1…`; paraLLEl-GS `19d93b2` + MoltenVK 1.4.2
reused read-only from I33's scratch; bundled env IS
`local/research/I33/ps2x.env`, SHA `8e0547fc…` matches I33's pin —
parallel default, embedded MoltenVK, `PGS_HIER_BINNING=force`, sound on,
I26-FAST route): preflight rc=0 (runner-dir diff empty, PIN ancestor of
HEAD, PGS/Granite/codegen/MoltenVK pins re-hashed, profile `f0793278`
valid, both devices reachable); configure_device rc=0 (`-O3 -DNDEBUG`
asserted 2 lines, `G44 parallel-gs shadow backend ON`); build_device
**BUILD SUCCEEDED** (126.8 MB binary); stage_device rc=0 (ELF/ISO/MoltenVK
staged copies SHA-match inputs: `1b49d05c…`, `3c2f8eb1…`, `6cd58884…` =
I33's device-slice pin; bundle `org.ps2x.ps2entryrunner`); sign rc=0
(MoltenVK.framework signed explicitly before the bundle — I33 lesson;
`codesign --verify --strict` passed). One fix in the F3 script copy: the
`install_iphone` pre-gate now excludes `unavailable` before matching
`connected|available` (the F2 3b substring bug, fixed "when next touched"
per that gate).

| Binary | SHA-256 (two matching reads) |
| --- | --- |
| device unsigned | `87e80a403f56d7ea43032d92cd1db29672c6571b296f1b42d0c6b51bbb7ebaa5` |
| device signed (installed) | `7bc7e57cf9de38488790a7eab186524063fa3a6fa7253c7964d158a6c05c2b16` |

iPad (Air 11" M2): install rc=0 (seq 1932, bundle `37AC9E67-…`); deploy
SKIP + 7 exact-size OKs. Live container `D3C32E8F-…` from a ~2 s probe
console (bundle path matches install URL). One fresh-card launch
(`mc-f3`, route byte-exact 484 chars re-armed via `-e`,
`PS2X_VSYNC_RATE_LOG=1`, no backend overrides): 82 s wall, ticks
1137/1814/2108, terminated after (0 procs left), zero FATAL, 48 kHz,
overlay shown. Bundled env selected parallel with the force rule:
`[gs:parallel] live backend selected`, `[gs-path] hier_rule=hier-if-large
… gpu=Apple M2 GPU`, `init ok`.

| Shot (tick) | Viewed verdict | SHA-256 (two matching reads) |
| --- | --- | --- |
| `shot-t1090` (1137) | Select Event (Snow Jam / Metro-City / Happiness + Race course map, legible), full brightness | `5965b2a5…` |
| `shot-t1810` (1814) | Race 2ND/2 00:00:01 0%, gate, EA Radio "Glass Danse - Oakenfold Remix / The Faint", rider at the gate | `8daa360b…` |
| `shot-t2100` (2108) | Race 2ND/2 00:00:06 1%, trick 370, checkpoint beam; **rider solid and lit at screen centre** (dark outfit, red accents, arms up, board) | `d0084273…` |

Brightness (DK1 gate): game-center bright-pixel mean (DK1 geometry, stdlib
`/tmp/f3_ipad_bright.py`) = (154.2, 176.8, 240.5) vs DK1 post-fix
(151.0, 173.3, 240.3) — within 3 LSB per channel (different run/tick,
same full-bright level; pre-fix was 0.54×). Pad v2 (I34 gate): large
4-arrow D-pad below-left of the face cluster, no control overlaps; the
only collision is the known portrait-compat SELECT/START overlap (I28,
pre-existing — the iPhone plays in landscape). Fresh-card proof: `mc-f3`
override resolved, route hit the race on pace. Deploy re-ran after: SKIP
+ 7 OKs, Brad's `mc0` byte-identical. Diagnostic pace only: launch→t2100
81 s (console-pty + vsync-rate overhead, one run — not a speed number).

iPhone (16 Pro Max): `available (paired)` at check and at install (never
`unavailable`); install rc=0 (seq 4856, bundle `4485DAB1-…`); deploy SKIP
+ 7 OKs. **Never launched** — no launch/process command targeted the
iPhone.

Budgets and gaps: 1 device build (no sim build — the brief doesn't ask,
and the sim Vulkan path is I33's known descriptor-indexing blocker), 1
probe + 1 iPad test (82 s), 2 installs; ~25 min. Scratch
`~/dev/ssx3-work/F3` 4.5 GB. Gaps: one iPad run (no drift cancellation);
pace diagnostic, not a speed number; iPhone unlaunched-by-us, so its
first F3 boot is Brad's; share tier still not mounted (G7 carries).

Exact commands:

```sh
sed -e 's|^W=.../I33/ios$|W=.../F3/ios|' -e 's|^FORK_WT=.../I33/PS2Recomp|FORK_WT=.../F3/PS2Recomp|' \
  -e 's|^PIN=0ed07c4...|PIN=ec2dbf186616c7d6cf2998ea2792c500efdf4478|' \
  local/research/I33/build-install.sh > ~/dev/ssx3-work/F3/ios/build-install.sh
# + install_iphone gate fix (grep -v unavailable); run scripts: W-sed into F3/ios/
git -C ~/dev/PS2Recomp fetch fork ssx3   # fork/ssx3 = ec2dbf1 = worktree HEAD
bash ~/dev/ssx3-work/F3/ios/build-install.sh preflight configure_device build_device stage_device sign
bash ~/dev/ssx3-work/F3/ios/build-install.sh install_ipad
bash local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/F3/ios/ipad-probe.sh             # live container D3C32E8F-…
bash ~/dev/ssx3-work/F3/ios/ipad-run.sh ~/dev/ssx3-work/F3/ios/run-ipad-f3 ~/dev/ssx3-work/F3/ios/run-ipad-env.json "1090 1810 2100"
bash local/research/I31/deploy-ios.sh ipad           # save byte-identical after
bash ~/dev/ssx3-work/F3/ios/build-install.sh install_iphone
bash local/research/I31/deploy-ios.sh iphone         # never launched
```

## Orchestrator gate, Part 2 (2026-09-25)

**Pass.** I viewed the iPad `run-ipad-f3/shot-t2100.png`: race 00:00:06 on the GPU backend, full brightness,
the player rider solid and lit mid-trick. Brad's iPhone has build `ec2dbf1` installed (never launched),
save + manual-play env verified. The iPad-in-portrait pad overlap is the known I28 item.

## Part 3 — Odin (APK `d5a94c27…`, 2 speed runs, play build installed)

Worker: Muse Code, brief `local/muse/prompts/F3.md` Part 3 only. Source:
the pushed fork `ssx3` tip `ec2dbf1` — the pushed SHA equals the Part 1
fold tip, so the Part 1 APK is reused with no rebuild: two local SHA
reads `d5a94c278aabac86fdf0b0570a6bb4f68680d2b5041bf595f86f3e271526ee78`,
153,769,544 B, both match; `base.apk` on the device reads `d5a94c27…`
after the run install and again after the play install. Over Wi-Fi
(serial `adb-622c49b1-IJnTHA._adb-tls-connect._tcp` from
`local/odin-serial`, read by the launcher); no drops all session.

Launcher: `launch.py` = F2's driver with F2→F3 paths/lease (`sed`, zero
`F2` remnants, committed here) + `phases.py` verbatim; env = the F2
launcher env relabelled (parallel, Turnip, `SSX3.iso`, skip-movie, sound
on, empty mc0-test, I26-FAST, `PS2X_VSYNC_RATE_LOG=1`,
`PS2X_UNPACED=1`). Pair method per the runbook: thermal status ≤ 1 gate
plus a fixed 180 s wait before each run. S1: thermal 0 pre-wait, 0 at
launch. S2: cooldown polls 3, 3, then 1 (~60 s), 180 s wait, thermal 0
at launch. Keyguard `showing=false`, AC powered, app not running before
both; Brad env `9fb46f85…` + mc0 pins verified before and after every
run; force-stop after; lease `LEASE_FREE F3 done` at close.

| Launch | Window | Result | Battery (wall charger) |
| --- | --- | --- | --- |
| S1 | tick 1714→4511 = 2797 vsyncs; 336.6 s race wall; 81 samples; 0 FATAL | STOP tick ≥4500 at t+406.4 s | 68→72 %, thermal 0 at launch |
| S2 | tick 1714→4556 = 2842 vsyncs; 340.9 s race wall; 82 samples; 0 FATAL | STOP tick ≥4500 at t+412.2 s | 76→80 %, thermal 0 at launch |

Logcat keys both runs: `[snd-output] stream rate=48000`,
`[gs-path] … hier-if-large … desc=buffer … gpu=Adreno (TM) 830` (same
as F2), zero FATAL. Run thermal: S1 32×3/2×4 (34 polls), S2 33×3/2×4
(35 polls). GameThread CPU: S1 28/34 polls on cpu6–7, S2 28/35. Race
GPU: S1 24.1 % (n=57), S2 24.2 % (n=58) — F2 read 23.1/17.3 %; still
CPU-bound.

Ledger-ready rates vs F2 (guest vsyncs/s ÷ 59.94, `phases.py`):

| Phase | S1 /s (×) | S2 /s (×) | F2 S1/S2 /s (×) | F3 mean ÷ F2 |
| --- | --- | --- | --- | --- |
| Title | 32.71 (0.546×) | 31.65 (0.528×) | 43.26/33.29 (0.722/0.555×) | = F2 S2 (F2 S1 was the known startup noise) |
| Main menu | 30.73 (0.513×) | 31.28 (0.522×) | 31.30/31.08 (0.522/0.519×) | 1.00× |
| Select Character | 24.58 (0.410×) | 24.54 (0.409×) | 25.11/24.99 (0.419/0.417×) | 0.98× |
| Setup/Peak | 26.22 (0.437×) | 25.65 (0.428×) | 26.48/26.58 (0.442/0.443×) | 0.98× |
| Mode/Event | 37.97 (0.633×) | 40.24 (0.671×) | 38.63/37.96 (0.644/0.633×) | 1.02× |
| Loading | 11.22 (0.187×) | 10.91 (0.182×) | 11.21/11.12 (0.187/0.185×) | 0.99× |
| **Race** | **8.31 (0.139×)** | **8.34 (0.139×)** | **8.36/8.20 (0.139/0.137×)** | **1.01×** |

Race per-5s bins climb 7.2→8.6 with final fast bins (10–12) — same
shape as F2/F1. The fold (pacing, alpha, pad v2, latch, VIF/UNPACK,
vf0) is speed-neutral on the Odin.

Screencaps (all 8 viewed; **full brightness, no stripes, rider solid**):

| Cap | Viewed verdict | SHA-256 (12) |
| --- | --- | --- |
| S1 sc01 (~t2127) | Race 2ND/2 00:00:07 1 %, crash spray, RECOVER, EA Radio Big Leave Home/Chemical Brothers — full-bright | `415638695e17` |
| S1 sc02 (~t3033) | 00:00:22 2 %, 1 MPH, rider solid and lit mid-slope | `b8e61c7532be` |
| S1 sc03 (~t4007) | 00:00:38 2 %, 0 MPH — no stripes | `ac5facdaa754` |
| S1 sc04 (t4511) | 00:00:46 5 %, 44 MPH dark forest gully = F2's sc04 scene | `995605f9f392` |
| S2 sc01 (~t2119) | 00:00:06 1 %, crash, EA Radio Big Emerge-Junkie XL Remix/Fischerspooner (RNG), board + rider mid-tumble | `2b0813865061` |
| S2 sc02 (~t3022) | 00:00:22 2 % 1 MPH — no stripes | `639a3b756e6d` |
| S2 sc03 (~t4040) | 00:00:39 2 % 0 MPH | `dab8d2377ebd` |
| S2 sc04 (t4556) | 00:00:47 5 % 42 MPH dark gully | `29a385de9a5d` |

Progression matches F2 exactly (crash → 1 MPH → 0 MPH → 42–44 MPH
gully), so no fold regression; the RD1 rider fix is visible on the
Odin path too.

Brad's play build: installed F3 APK (`Success`, `base.apk`
`d5a94c27…`), then `bash local/research/I31/deploy-odin.sh "$S"` with
the serial from `local/odin-serial`: env SKIP + 6 save SKIPs, verify
7/7 OK. **No launch.** Device left: lease `LEASE_FREE F3 done`, app
not running (force-stopped + `pidof` clean), `/data/local/tmp/f3` +
`files/mc0-test` removed, battery 80 % on AC. No screen/keyguard
toggle at any point (read-only `dumpsys` checks only).

Budgets and gaps: installs 2 (run + play), launches 2 (~411 s +
~417 s wall), battery 66→80 % (wall charger net positive). Scratch
`~/dev/ssx3-work/F3` 4.5 GB ≤ 15 GB (`odin/` holds the APK + 8 PNGs);
text logs (S1+S2, 968 K) + `launch.py` + `phases.py` committed here.
Gaps: two runs, no profile; S2 stopped at t4556 (45 over — the 5 s
`[vsync-rate]` stop-detection overshoot, same as F2/Mac G3); installed
once before S1 (base.apk SHA-verified) with the same install serving
S2 rather than F2's install-per-run (no other writer held the lease
between runs); share tier still not mounted (G7 carries).

Exact commands:

```sh
shasum -a 256 ~/dev/ssx3-work/F3/odin/app-release.apk  # d5a94c27 x2
sed -e 's/F2/F3/g; s|/data/local/tmp/f2|/data/local/tmp/f3|g' local/research/F2/launch.py > local/research/F3/launch.py
cp local/research/F2/phases.py local/research/F3/phases.py  # verbatim
adb -s "$S" install -r ~/dev/ssx3-work/F3/odin/app-release.apk  # Success; base.apk d5a94c27
# S1: thermal 0, sleep 180, thermal 0
python3 local/research/F3/launch.py --label S1 --wall 600 --stop-tick 4500
# S2: thermal 3,3,1 polls, sleep 180, thermal 0
python3 local/research/F3/launch.py --label S2 --wall 600 --stop-tick 4500
python3 local/research/F3/phases.py local/research/F3/logs/S1|S2
adb -s "$S" install -r ~/dev/ssx3-work/F3/odin/app-release.apk  # play build, no launch
bash local/research/I31/deploy-odin.sh "$S"  # 7/7 OK
adb -s "$S" shell 'rm -rf /data/local/tmp/f3 .../files/mc0-test; am force-stop com.ps2x.runner'
```

Recommended next action: F3 is complete on all three targets (Mac
green + rider fixed, iPhone/iPad installed, Odin speed-neutral with
the play build installed). Gate Part 3 and ledger the Odin race
0.139× pair.

## Orchestrator gate, Part 3 (2026-09-25)

**Pass.** I viewed S1 sc01: Odin race 00:00:07 at full brightness, no stripes. APK `d5a94c27…` (fork
`ec2dbf1`) over Wi-Fi, no drops; race 0.139× / 0.139× (speed-neutral vs F2), thermal status 3 in race
(the cool-down method held both runs at 0 at launch). Installed as Brad's play build, env + save
verified, no launch. F3 is complete.
