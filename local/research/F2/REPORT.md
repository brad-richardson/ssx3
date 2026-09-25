# F2 Part 1 — fold SB1 + AU10 + CT1 + GB9 onto fork `ssx3`, codegen promotion, Mac check

Worker: Muse Code, brief `local/muse/prompts/F2.md` Part 1 only. No push
(orchestrator gates and pushes). First-failure rule never triggered.

**Result: fold clean, codegen promoted, Mac green.** All 5 cherry-picks applied
with no conflicts; the folded tree's regen is byte-identical to SB1's codegen
(`diff -rq` empty) and is now the canonical `codegen-ssx3`; suite 612/612;
B1 races with sound on (cid0 531, coverage 0/0/4), B2 races with sound off
(det-hash identical to B1), B3 clean speed matches F1 B2 phase-for-phase
(race 0.250× both).

## Fold (worktree `~/dev/ssx3-work/F2/PS2Recomp`, branch `f2-fold` from `56a5e8a`)

`git cherry-pick -x` in brief order, all clean (CT1 auto-merged
`EeScheduler.cpp`, which SB1 also touched, nearby but disjoint lines).

| # | Source | New SHA | Subject |
| --- | --- | --- | --- |
| 1 | `a64ba5e` | `51ac2da7344a999c6dff00db8e53bbd5fb3d41ee` | [SB1] signed-branch tripwire: 64-bit predicates + dev-only 32/64 mismatch note |
| 2 | `90df7e0` | `2695df0b2d557ee3ae170262f480d9faf0adaa29` | [SB1] retire the 0x3E3968 file-key comparator override |
| 3 | `2fb2003` | `09a95d96c5db48f45e27a4a0bb05659378d89969` | [AU10] SND HLE: run the guest-time tick unconditionally, gate only host output on PS2X_SOUND |
| 4 | `3344013` | `b975fb22b664ecb498d341079ef5db12edf1ec10` | [CT1] EeScheduler: default-off PS2X_INTC_LOG + PS2X_COVERAGE_TICK counters |
| 5 | `5706858` | `96e9f45b5dca49e6cc1297d5984b506a61d1b369` | [GB9] [gs-path] prints the effective hier rule via PGS_HIER_BINNING (local-only) |

Old full SHAs: `a64ba5e94383505570628c43cee537e82d07ade7`,
`90df7e0c8afb9e48abd6ae8981bd81e5d5f5833a`,
`2fb200391a739088a10b16b5f7154de4d0d96837`,
`3344013bd17387e8e547b3534166220f12968580`,
`5706858db4145f1ea84cf3bfd4ae338255023cdc`.
Tip: `96e9f45`. `games/` untouched by the fold
(`git diff 56a5e8a HEAD --stat -- games/` empty).
Runner-dir guard `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`:
empty. `git diff --check 56a5e8a HEAD`: clean.

## Codegen (regen + equality + promotion)

- TOML: folded tree's tracked `games/ssx3/ssx3.toml` with only the 3 SB1
  paths repointed (`ssx3-f2.toml`; diff vs SB1's TOML = the 2 expected
  path lines; CSV copy SHA `7c827add…b9ba` matches SB1's).
- Tool build (SB1 recipe flags): configure rc=0, build rc=0
  (`cmake-recomp.log`, `build-recomp.log`). `ps2_recomp`
  `ccc2d8cc0b7c90aa89f0c72bd946323e9fd9b6b163095a80a4809c85c1dfe755`
  (differs from SB1's tool binary — embedded paths; the output is the gate).
- Regen: rc=0, 9,457 files (`regen.log`).
- **Equality: `diff -rq ~/dev/ssx3-work/SB1/codegen ~/dev/ssx3-work/F2/codegen`
  rc=0, 0 bytes of diff** (`codegen-diff.txt`).
- Promotion: `mv codegen-ssx3 codegen-ssx3-pre-sb1` + `cp -R F2/codegen
  codegen-ssx3`, rc=0; post-copy `diff -rq` rc=0 (exact copy).
  `register_functions.cpp` SHA `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`
  (two matching reads; unchanged by the promotion — the SBR change touches
  predicate lines in function files only). File counts 9,457 / 9,457.
  New canonical: 623 files reference `PS2X_SBR_LT` (pre-promotion: 0).
- Never committed: generated code lives only in scratch + the canonical dir.

## Builds (one dir `~/dev/ssx3-work/F2/build`, GB8/F1 recipe + `BUILD_TEST=ON`)

Release, Homebrew clang, `PS2X_GAME_CODEGEN_DIR=` promoted canonical,
`PS2X_GS_SHADOW_PARALLEL=ON`, paraLLEl-GS worktree
`~/dev/ssx3-work/F2/parallel-gs` at `19d93b2` (detached HEAD on
`origin/ssx3`; Granite `166ba21a247a681903cc9d0bb6562fe50a554c85`, matches
pin), runtime/aggressive logs OFF, diag taps OFF, tripwire default OFF
(release collapses to `GPR_S64`). Det runner = incremental reconfigure
(`DET_HASH_TAP=ON`, 353 steps) after copying the clean runner out.
Configure + both builds rc=0.

| Runner | Det-hash tap | SHA-256 (staged read + 2 boot-precheck reads match) |
| --- | --- | --- |
| `bin/runner-clean` | OFF (`det-hash:v1` 0× in strings) | `62d56f268afffdcd40bc488090c05dfa47ffcf4d7e3f8038955b85602055ddaf` |
| `bin/runner-det` | ON (string present) | `54789f9afadd4a87a79138e1663fd47d2e9ca9dfc4a1dbde9ce958b296542ba0` |

Suite from the worktree root: **612/612 pass, 0 fail, rc=0** (`suite.log`;
611 + AU10's "keyed-off voice ENVX decays to zero with no output device,
then retriggers" `[Passed]`; the SB1/AU10 4 extra det-hash tests compile
in only with the tap on, and this build has it off).

## Boots (I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, deterministic, paraLLEl + `PGS_HIER_BINNING=force`)

Driver: `f2_boot.py` (committed here; F1 driver + force-binning in the
parallel env and recorded env + `PS2X_COVERAGE_TICK` in det mode + `--sound
on|off` in det mode; speed mode always sound-on per F1). `[gs-path]` on all
three boots: `hier_rule=hier-if-large hier_t2=2 hier_t4=4 … desc=plain …
gpu=Apple M5 Pro` (the GB9 effective-rule print + Odin binning rule live).
Boot-driver prechecks: two SHA reads match on runner/ISO/ELF/codegen every
boot; ISO `3c2f8eb1…`, ELF `1b49d05c…`, codegen `8ea8ed43…` all pinned.

| Boot | Sound | Bound | Wall | Last tick | HUD wall | cid0/dmq/done | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 det | on | target | 85.9 s | 2403 | 35.44 s | 531/531/531 | 0 |
| B2 det | off | target | 83.9 s | 2400 | 34.49 s | 531/531/531 | 0 |
| B3 speed | on | target | 81.3 s | 2418 | 35.92 s | — | 0 |

B1: `[snd-output] stream rate=48000` live; coverage at vsync 2400 =
`targets=0`, `ids=0`, `pairs=4` (the E56 four SIDs, one hit each —
identical list to CT1 B2). B2: no `[snd-output]` (host stream off, as
designed); B2's snd tick serials carry identical guest cycle counts to B1's
(e.g. `cycle=11550757345 ticks=3572` both); B1 underruns = 2.1M (consumer
starved on a loaded mini, same AU8/AU9/AU10 symptom, diagnostic build —
not a speed number), B2 underruns = 0 / overflows as designed.

**B1 vs B2 det-hash: 2,448/2,448 common ticks byte-identical, all fields,
0 differing payloads** (glue-immune regex extract; B1 ticks 1..2450, B2
1..2448 — 2-tick settle overrun, the documented GB8 variance).
`gb8_hashdiff.py` reports DIFFER only because of the GB9 glued-line
artifact (`[frame:dump]...[det-hash:v1]` sharing one line, no newline
between threads; line-anchored parser misses 1 tick in B1, 3 in B2 — all
verified present by field extract). AU10's property holds on the fold.

## Frames (0.5 s snapshotter, picked by exact present tick from the sidecar)

All viewed, all 512×448 fbp 112, no tiles/stripes/corruption:

| Boot | Present tick | File (`run/<B>/frames/snap/`) | Viewed verdict |
| --- | --- | --- | --- |
| B1 | 1094 | `snap-001052t-0019.30s.png` (`fnv1a=e9825b18`) | Select Peak: Peak 1 mountain photo, Peak 1 highlighted, 2/3 locked, correct text |
| B1 | 1800 | `snap-001793t-0041.65s.png` (`fnv1a=44ebc4b0`) | Race 00:00:01 2ND/2: rider, lit snow, pines, mountains, EA Radio card |
| B1 | 2096 | `snap-002090t-0062.47s.png` (`fnv1a=a5a4bd9f`) | Race 00:00:06 2ND/2, 1%, checkpoint beam, trick 160 |
| B1 | 2392 | `snap-002387t-0082.27s.png` (`fnv1a=ecc2ff82`) | Race 00:00:11 2ND/2, 2%, 14 MPH, slope/trees/spray |
| B2 | 2103 | `snap-002097t-0061.47s.png` (`fnv1a=e710d8d5`) | Sound-off race 00:00:06 2ND/2, 1%, beam, trick 270 (animation Δ vs B1's 160 across ~7 ticks, not a state diff — det-hash identical) |

## B3 per-phase vs F1 B2 (trace authoritative; guest vsyncs/s ÷ 59.94)

Exclusive lease ("both" slots), quiet host (load 1.9 at claim, quieter than
F1's 2.2). The fold is speed-neutral on the Mac.

| Phase (ticks) | F2 B3 vs/s (×) | F1 B2 vs/s (×) | F2 ÷ F1 |
| --- | --- | --- | --- |
| Title [0,636) | 40.32 (0.673×) | 40.29 (0.672×) | 1.00× |
| Menus [636,1440) | 76.96 (1.284×) | 77.13 (1.287×) | 1.00× |
| Loading [1440,1714) | 28.26 (0.472×) | 28.30 (0.472×) | 1.00× |
| Race-start [1714,1800] | 16.61 (0.277×) | 16.69 (0.278×) | 1.00× |
| **Race (1800,2400]** | **14.98 (0.250×)** | **15.01 (0.250×)** | **1.00×** |
| Wall launch → race HUD (~t1714) | 35.92 s | 35.9 s | 1.00× |
| Wall launch → t2400 | 81.3 s | 81.3 s | 1.00× |

Raw 5 s cross-check (race window): n=8 mean 15.13 vs trace 14.98 — agrees.
One run (brief budget); no drift cancellation.

## Budgets and gaps

Builds: 1 tool + 1 full (clean + det reconfigure). Boots 3/3 (B1 86 s, B2
84 s one slot each; B3 81 s exclusive), each ≤ 500 s wall cap. ~1 h of the
1.5 h box. Scratch `~/dev/ssx3-work/F2` 3.2 GB (≤ 20 GB); global 122.0/200 GB.
Never pushed; fork branch `f2-fold` local-only; text in git (`f2_boot.py`,
this report); no runners signalled except by recorded PID.

Gaps, stated plainly:

- G1. One speed run (no drift cancellation); B3's force-binning-vs-flat
  cost split is unmeasured (GB9 proved force correct, not its Mac cost —
  the F2÷F1 1.00× is fold+force combined vs F1's flat-always).
- G2. Frame ticks within Δ8 of target (snapshotter phase, not exact-tick
  dumps — `PS2X_FRAME_DUMP_ONCE_TICKS` takes only 3 ticks).
- G3. B2's S-on pixels not separately diffed (one B2 frame viewed; the gate
  is det-hash identity, which passed on all 2,448 common ticks).
- G4. `gb8_hashdiff.py` remains line-anchored and trips on the glued
  `[frame:dump]`/`[det-hash]` lines (tooling note, also seen in GB9);
  the glue-immune extract is the authoritative gate here.
- G5. The promoted canonical codegen changes every downstream build: lanes
  that built against `codegen-ssx3-pre-sb1` must rebuild (the old tree is
  preserved at that path; `register_functions.cpp` SHA is unchanged, so
  SHA-pinned prechecks still pass — they do not detect the promotion).

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/F2/PS2Recomp -b f2-fold fork/ssx3  # 56a5e8a
git -C ~/dev/ssx3-work/F2/PS2Recomp cherry-pick -x a64ba5e 90df7e0 2fb2003 3344013 5706858
git -C ~/dev/ssx3-work/F2/PS2Recomp diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner  # empty
git -C ~/dev/parallel-gs worktree add ~/dev/ssx3-work/F2/parallel-gs origin/ssx3  # 19d93b2
git -C ~/dev/ssx3-work/F2/parallel-gs submodule update --init --recursive Granite  # 166ba21
cp ~/dev/ssx3-work/SB1/ssx3-functions.sweep.csv ~/dev/ssx3-work/F2/  # SHA 7c827add…b9ba match
# ssx3-f2.toml = folded tracked TOML, 3 paths repointed (diff vs SB1's = 2 path lines)
cmake -S F2/PS2Recomp -B F2/build-recomp -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3
cmake --build F2/build-recomp                              # ps2_recomp ccc2d8cc…
F2/build-recomp/ps2xRecomp/ps2_recomp F2/ssx3-f2.toml       # regen.log, 9457 files
diff -rq ~/dev/ssx3-work/SB1/codegen ~/dev/ssx3-work/F2/codegen  # rc=0, empty
mv ~/dev/ssx3-work/codegen-ssx3 ~/dev/ssx3-work/codegen-ssx3-pre-sb1
cp -R ~/dev/ssx3-work/F2/codegen ~/dev/ssx3-work/codegen-ssx3
cmake -S F2/PS2Recomp -B F2/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build F2/build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd F2/PS2Recomp && ../build/ps2xTest/ps2x_tests)           # 612/612
cp F2/build/ps2xRuntime/ps2EntryRunner F2/bin/runner-clean
cmake -S F2/PS2Recomp -B F2/build -DPS2X_ENABLE_DET_HASH_TAP=ON
cmake --build F2/build --parallel 8 --target ps2EntryRunner
cp F2/build/ps2xRuntime/ps2EntryRunner F2/bin/runner-det
python3 f2_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400 --sound on --coverage-tick 2400
python3 f2_boot.py --mode det --backend parallel --runner bin/runner-det --label B2 --stop-tick 2400 --sound off --coverage-tick 2400
python3 f2_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B3 --stop-tick 2400
python3 gb8_rates.py run/B3
python3 local/research/GB8/gb8_hashdiff.py --base ~/dev/ssx3-work/F2/run/B1 --cand ~/dev/ssx3-work/F2/run/B2  # glued-line caveat, see above
```

## Part 3 — iOS (device build `96e9f45`, sim + iPad race, iPhone install-only)

Worker: Muse Code, brief `local/muse/prompts/F2.md` Part 3 only. Source: pushed
fork `ssx3` `96e9f45b5dca49e6cc1297d5984b506a61d1b369` (reused the Part 1
worktree `~/dev/ssx3-work/F2/PS2Recomp`; `HEAD == fork/ssx3` after fetch, clean).

Builds (`~/dev/ssx3-work/F2/ios/build-install.sh` = F1 recipe + 3-line sed:
`W`, `FORK_WT`, `PIN→96e9f45…`; codegen = promoted canonical
`register_functions.cpp` `8ea8ed43…`; bundled env IS
`local/research/I32/ps2x.env`, SHA `0041e09a…` matches I32's committed
`env-sha.txt` — sound on, `PS2X_MC_ROOT=${DOCUMENTS}/mc0`): preflight rc=0
(runner-dir diff empty, deps pinned, profile `f0793278` valid, both devices
connected); configure sim + device rc=0 (`-O3 -DNDEBUG` asserted 2 lines each,
raylib DPI patch "already applied"); sim build + stage + install rc=0; device
build + stage + sign rc=0 (`codesign --verify --strict` passed, ELF/ISO stage
copies `cmp`-equal, bundle `org.ps2x.ps2entryrunner`).

| Binary | SHA-256 (two matching reads) |
| --- | --- |
| sim `ps2EntryRunner` | `92df7a0d9e60dc20ab833ad52bcdd0baaad14d5b227924608f7438aade08bf1b` |
| device unsigned | `b91e83c2377b5f95390f9e30816c38e868aa9b0d454dae6a3e5c9c66d6d48c79` |
| device signed (installed) | `14ec858da43c80ac58cfc86d10cdc145b62747f96b319780c0754e6378bf7916` |

Simulator (fresh container: uninstalled first, reinstalled to empty Documents;
bundled I26-FAST route, sound on; one lease slot each, released; zero FATAL;
all frames SHA-matched on two reads):

| Run | Shot (observed tick) | Viewed verdict | SHA-256 |
| --- | --- | --- | --- |
| peak series | `series-0` (1032) | **Select Peak: Peak 1 mountain photo**, Peak 1 highlighted, 2/3 locked, correct text — RR1 fix visible on the F2 fold | `4a55d241…` |
| sim (131 s) | `shot-t1050` (1187) | Select Event (Snow Jam, course map); menu correct, Peak overshot by the 2 s poll | `8c20b38d…` |
| sim | `shot-t1750` (1763) | Race 2ND/2 00:00:00 0%, gate, lit snow, EA Radio "Poor Leno - Silicon Soul Remix / Royksopp" | `267ab29b…` |
| sim | `shot-t2100` (2109) | Race 2ND/2 00:00:06 1%, spray, pines, mountains, checkpoint beam; advancing | `0ad2fc46…` |

Peak timing note (artifact, not a regression): two early peak shots at observed
tick ~1018 showed the Select Peak menu with the photo panel still empty (solid
blue box). The sim runs are non-deterministic (no `PS2X_DETERMINISTIC` in the
bundled env) and the only console tick source is the 5 s-quantized
`[vsync-rate]` line (~150 ticks apart at menu speed), so single-shot capture is
luck; the photo populates ~1020–1030, after the early shots. A 6-shot series
across the window (`peak-series.sh`, scratch) caught it: `series-0` at observed
1032 has the full photo. The Event map and race frames render fully throughout,
and the Mac B1 frame shows the same photo — texture loading is healthy.

iPad (Air 11" M2): install rc=0 (seq 1892, bundle `3E1BDD2F…`); deploy SKIP +
7 exact-size OKs (Brad's save + 496-byte manual-play env intact). Live
container read from a ~1 s probe console (bogus-UUID `MC_ROOT`, title only,
terminated, no screenshots): **`E3BC4F4E-…`** — rotated from F1's
`E26D3546`, so reinstalls do rotate it. One test launch (env: I26-FAST script
byte-exact 484 chars, `MC_ROOT=<live>/Documents/mc-fresh`,
`PS2X_VSYNC_RATE_LOG=1`, no vpad injections): 208 s, ticks 1112/1751/1969/2153
(F1's pace was 1116/1751/1970/2155), terminated after (`info processes`
clean), zero FATAL, 48 kHz, overlay shown. Portrait compat crop as in F1.

| Shot (tick) | Viewed verdict | SHA-256 |
| --- | --- | --- |
| `shot-t1050` (1112) | Select Mode (Race/Freestyle) — missed Peak by ~13 ticks (2 s poll overshoot), menu correct | `54838b1b…` |
| `shot-t1750` (1751) | Race 1ST/2 00:00:00 0%, EA Radio "Emerge - Junkie XL Remix / Fischerspooner", gate — race start on-route | `2c98f1b7…` |
| `shot-t1960` (1969) | Race 2ND/2 00:00:04 1%, gate pole, spray, pines; advancing | `d0e14aaf…` |
| `shot-t2140` (2153) | Race 2ND/2 00:00:07 1%, slope/trees/spray/beam; advancing | `b1c032fb…` |

Fresh-card proof: `mc-fresh` + `mc-fresh_slot1` present in the live-container
file listing (this run's override resolved); the route hit the race on pace.
Oddity (observation only): both dirs are stamped 9/25 7:18 AM while the run
was ~8:26–8:30 — likely a stale iPad clock at creation, corrected by the time
of the screenshots (status bar 8:28/8:30, dyld cache 8:26). All functional
gates pass. Deploy re-ran after: SKIP + 7 OKs, Brad's `mc0` byte-identical.
Observed diagnostic pace: race window 1751@106s→2153@207s ≈ 4.0 vs/s ≈
**0.067×** (vsync-rate log + screenshots on — not a speed number).

iPhone (16 Pro Max): install rc=0 (seq 4840, bundle `6550D7B8…`); deploy SKIP
+ 7 OKs. **Never launched** — no launch/process command targeted the iPhone.

Budgets and gaps: 2 builds, 2 sim runs (131 s + 31 s) + 4 peak retries/series
(~45 s each), 1 probe + 1 iPad test (208 s) + 1 failed iPad attempt (relative
env path after the script's `cd`; nothing launched, `info processes` clean,
re-ran with the absolute path), 2 installs; ~1.5 h of the 1 h box (peak-timing
series + retries). Scratch `~/dev/ssx3-work/F2` 10 GB ≤ 20 GB; Simulator shut
down; no lease held. Gaps: iPad Select Peak missed again (sim series covers
the Peak 1 photo); iPad pace is diagnostic, not a clean speed number; the
`mc-fresh*` timestamp oddity above is unexplained but functionally inert; one
failed-then-retried iPad launch (recipe assumes the env path resolves from the
run dir — pass it absolute).

Exact commands:

```sh
sed -e 's|^W=.../F1/ios$|W=.../F2/ios|' -e 's|^FORK_WT=.*|FORK_WT=.../F2/PS2Recomp|' \
  -e 's|^PIN=56a5e8a...|PIN=96e9f45b5dca49e6cc1297d5984b506a61d1b369|' \
  ~/dev/ssx3-work/F1/ios/build-install.sh > ~/dev/ssx3-work/F2/ios/build-install.sh
# sim-run.sh / sim-peak-run.sh / ipad-probe.sh / ipad-run.sh: same W-sed (+ claim F2-sim)
git -C ~/dev/PS2Recomp fetch fork ssx3   # fork/ssx3 = 96e9f45 = worktree HEAD
bash ~/dev/ssx3-work/F2/ios/build-install.sh preflight configure_sim configure_device
bash ~/dev/ssx3-work/F2/ios/build-install.sh build_sim stage_sim sim_install
xcrun simctl uninstall $SIM org.ps2x.ps2entryrunner   # F1 runs were in the container
bash ~/dev/ssx3-work/F2/ios/build-install.sh sim_install
bash ~/dev/ssx3-work/F2/ios/sim-run.sh                # thresholds 1050 1750 2100
bash ~/dev/ssx3-work/F2/ios/sim-peak-run.sh 1010      # 0.5 s poll: photo panel empty
bash ~/dev/ssx3-work/F2/ios/sim-peak-run.sh 1040      # overshot (1193, Select Event)
bash ~/dev/ssx3-work/F2/ios/sim-peak-run.sh 1000      # photo panel still empty
bash ~/dev/ssx3-work/F2/ios/sim-peak-run.sh 1000 4    # +4 s post-sleep: overshot (Select Event)
bash ~/dev/ssx3-work/F2/ios/sim-peak-run.sh 1000 2    # +2 s: overshot (Select Mode)
bash ~/dev/ssx3-work/F2/ios/peak-series.sh 950 6 2    # 6-shot series: series-0 has the photo
bash ~/dev/ssx3-work/F2/ios/build-install.sh build_device stage_device sign
bash ~/dev/ssx3-work/F2/ios/build-install.sh install_ipad
bash local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/F2/ios/ipad-probe.sh             # live container E3BC4F4E-…
# run-ipad-env.json = F1's + live UUID (route byte-exact 484 chars, mc-fresh, VSYNC_RATE_LOG)
bash ~/dev/ssx3-work/F2/ios/ipad-run.sh /Users/brad/dev/ssx3-work/F2/ios/run-ipad-env.json "1050 1750 1960 2140"
bash local/research/I31/deploy-ios.sh ipad           # save byte-identical after
bash ~/dev/ssx3-work/F2/ios/build-install.sh install_iphone
bash local/research/I31/deploy-ios.sh iphone         # never launched
xcrun simctl shutdown $SIM
```

## Orchestrator gate, Part 1 (2026-09-25)

**Pass.** I viewed B1 t2090 (race 00:00:06, checkpoint beam, lit snow, trees, mountains). Five
cherry-picks clean; regen byte-identical to SB1's and promoted (`codegen-ssx3-pre-sb1` kept); suite
612/612; cid0 = 531 without the override; coverage 0/0/4; sound off races with det-hash identical to
sound on; Mac race 0.250× (unchanged). Pushed `f2-fold` → fork `ssx3` **`96e9f45`** (fast-forward
from `56a5e8a`). Fine horizontal stripes are visible in the Mac paraLLEl frames too (the Odin
"stripes" item), so that bug can now be chased on the Mac. Part 3 (iOS) released; Part 2 (Odin)
waits for the Odin (wall-charging, off USB).

## Orchestrator gate, Part 3 (2026-09-25)

**Pass.** I viewed the iPad `shot-t1960.png`: race 00:00:04 with lit snow, pines, mountains, spray and the
checkpoint beam. This time the iPad was in portrait, and the overlay's portrait layout collides:
SELECT/START overlap, and the D-pad and face buttons sit over the picture. That goes to I28 (iPad-native
layout); the iPhone plays in landscape. Signed build `14ec858d…` from fork `96e9f45` is on Brad's iPhone
(install only) and iPad; save and manual-play env re-applied and verified on both.

## Part 2 — Android (BLOCKED before any APK: CT1 lambda fails the NDK compile)

Worker: Muse Code, brief `local/muse/prompts/F2.md` Part 2 only. Fork `ssx3`
`92f999190ce2f1cd8c634396e469b3aebad5f82e` (F2 fold + ST1 progressive scanout).
**Status: blocked, no APK, no Odin launch.** Bytesize staging is complete and
verified, but the one build fails in 30 s on a genuine fork compile error in
CT1's `coverageTick()` lambda. First-failure rule: stopped, error saved
(`build-error.txt`, full 621-line log kept at `/home/brad/f2/assembleRelease.log`
on bytesize), handing back. No fix applied anywhere (E lane owns the fork).

### Staging (bytesize `/home/brad/f2`, WSL idle, load 0.00, no other heavy job)

| Input | Receipt |
| --- | --- |
| Fork | `git archive 92f9991…5f82e` (`origin/ssx3` after fetch = mini's tip); tar 334 files + 63 dirs, extracted tree 334 files (zero missing/extra); `runner/` = 438 B upstream stub `cf62c485…` only; `force_progressive` (ST1) + `PS2X_SBR_LT` (SB1) present. Mini runner guard `git diff --stat 14b1e5cb 92f9991 -- ps2xRuntime/src/runner` empty; `56a5e8a→92f9991` = 15 files (the F2 fold + ST1) |
| Codegen (refreshed) | Streamed mini canonical → bytesize (`tar` over held ssh stdin); 9,457 files both sides; `register_functions.cpp` `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` (two reads each side, all match); **623 files ref `PS2X_SBR_LT` both sides** (bytesize's f1/tl1 copies have 0 — pre-SB1; the `register_functions.cpp` SHA alone can't detect the promotion, F2 G5); zero `._*` files |
| paraLLEl-GS `19d93b2` | Streamed mini F2 worktree (`19d93b2d0b…`, Granite `166ba21a…`); 24,314 files; `diff -rq` vs tl1's copy = exactly `gs_renderer.cpp` differs + new `pgs_env_knobs.hpp`, matching mini `git diff 963cb57 19d93b2` (2 files, the GB9 `PGS_HIER_BINNING` knob); `Granite/` byte-identical to tl1's |
| jniLibs | `cp -a` from tl1: Turnip `717812c3…` 14,188,488 B + HAL `1b49d27c…` 7,112 B (pins + sizes match) |
| `build.sh` | Committed here (= F1 recipe, root f2); SHA `790a3053…` identical local/remote |
| Toolchain | Wrapper pins `a3648413…`/`49849512…`, Gradle 8.9, NDK 28.2.13676358, `--max-workers=2` (all = F1/TL1) |

### Build failure (the blocker)

`BUILD FAILED in 30s`, one error, rest of the 434 ninja steps unaffected:

```text
EeScheduler.cpp:2016:13: error: return type 'uint64_t' (aka 'unsigned long')
must match previous return type 'unsigned long long' when lambda expression
has unspecified explicit return type
   2016 |             return value;
```

CT1's `coverageTick()` lambda (commit `b975fb2`, folded as-is) returns `~0ull`
(`unsigned long long`) in two branches and `value` (`uint64_t`) in one.
Deduced lambda return types must match exactly. **Mac builds are green
because on Darwin `uint64_t` IS `unsigned long long`** (mini probe:
u64-is-ulong=0, u64-is-ull=1) — F2 Part 1 (suite 612/612 + runners) and ST1
(616/616) compiled this file cleanly, and iOS builds on macOS are unaffected.
Only Android/Linux (LP64 stdint: `uint64_t` = `unsigned long`) breaks.

Minimal fix shape, E lane's call, **not applied**: `~0ull` →
`~uint64_t(0)` (2 occurrences, same lambda), or an explicit `-> uint64_t`.

### Not done / untouched

- No APK, so no Odin runs: the stripes check in the screencaps and the race
  comparison vs F1's 0.140× are both pending, as are the play build + deploy.
- Odin untouched (read-only checks only, never claimed): lease still
  `LEASE_FREE F1 done`, 58 %, `AC powered: true`, `showing=false`. No
  screen/keyguard toggle, no launch, no force-stop needed.
- Bytesize staging left in place for resume (codegen/parallel-gs/jniLibs/
  build.sh all verified; only `PS2Recomp/` needs re-archiving at the new tip).
  Resume: fetch, confirm tip, `rm -rf /home/brad/f2/PS2Recomp`,
  `git archive <new-tip> | tar -x -C /home/brad/f2/PS2Recomp` (+ stub check),
  `bash /home/brad/f2/build.sh` on one held ssh (WSL sleeps across ssh gaps).

### Exact commands

```sh
git -C ~/dev/PS2Recomp fetch fork ssx3  # fork/ssx3 = 92f9991...5f82e
git -C ~/dev/PS2Recomp diff --stat 14b1e5cb 92f9991 -- ps2xRuntime/src/runner  # empty
ssh bytesize 'wsl ...'  # fetch origin/ssx3 = 92f9991; git archive | tar -x -C /home/brad/f2/PS2Recomp
COPYFILE_DISABLE=1 tar -czf - -C ~/dev/ssx3-work codegen-ssx3 | ssh bytesize 'wsl ... tar -xzf - -C /home/brad/f2'
COPYFILE_DISABLE=1 tar --no-xattrs --exclude='.git' -czf - -C ~/dev/ssx3-work/F2 parallel-gs | ssh bytesize 'wsl ...'
# bytesize verifies: 9457/9457, SHA x2, SBR 623; diff -rq parallel (2-file delta); Granite identical; jniLibs pins+sizes
cat local/research/F2/build.sh | ssh bytesize 'wsl ... cat > /home/brad/f2/build.sh'  # SHA 790a3053 both sides
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/f2/build.sh"'  # BUILD FAILED in 30s (one held ssh)
clang /tmp/u64check.c -o /tmp/u64check && /tmp/u64check  # Darwin: u64-is-ull=1
```
