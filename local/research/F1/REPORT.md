# F1 Part 1 — fold RR1 + AU9 + E57 + N11 onto fork `ssx3`, Mac check

Worker: Muse Code, brief `local/muse/prompts/F1.md` Part 1 only. No push (orchestrator gates and pushes).

## Fold (worktree `~/dev/ssx3-work/F1/PS2Recomp`, branch `f1-fold` from fork `ssx3` `71c952e`)

All 14 cherry-picks (`git cherry-pick -x`, brief order) applied clean, no conflicts. N11's
`20db28f` auto-merged `ps2xRuntime/src/lib/ps2_runtime.cpp` (AU9 touched nearby lines).

| # | Source | New SHA | Subject |
| --- | --- | --- | --- |
| 1 | `69b3256` | `8c4ddd80642562747f6e600bdb899d0776146889` | [E57] VU1: gate pipeline commits on the earliest queued ready cycle |
| 2 | `ed35abf` | `bb582f436c5b2350f3d794cda0416b9c89b79ce5` | [E57] VU1: inline operand/result normalization, select-based lane hazards |
| 3 | `cbca1ad` | `b9103a7e3bfaa33ef18620791ceef6cb7023fc62` | [E57] VU1: inline commit gate, skip idle XGKICK calls, upper-NOP early out |
| 4 | `802f5d2` | `2fbe98aedabbce80ff9e7dffe3f951621b39a6e9` | [E57] VU1: one-decode FMAC exact results, memcpy XGKICK qwords |
| 5 | `0a4aa5e` | `ef25a6268ecb21829988bf9dde073e5493a955a7` | [E57] VU1: reference the cached decoded pair instead of copying it |
| 6 | `a4ecce5` | `bef95fd017f78f782b2d304d72d8d5fc31c231b3` | [E57] VU1: drop a stale speed note from the commit-gate comment |
| 7 | `3bc0449` | `8381cfbf36aee2ffd7881573cf463510dc93e5f2` | [RR1] PATH3 mask: release one EOP packet per MSKPATH3 unmask window |
| 8 | `f3dff5b` | `556eb0f30eafe147c3e288a58dbd68e33f4c960c` | [RR1] VIF UNPACK V4-5: expand RGBA5551 to 8-bit channels |
| 9 | `4f69c98` | `e8a1a617f87fe68c88ec216dc172297bbcd78bc5` | [RR1] DMA chain walker: raise the 4096-tag cap to a runaway guard |
| 10 | `fb75ec3` | `7ca39f0f8de2d8f2779ac3ee14e41eb84d888790` | [AU9] SSX 3: override the file-table comparator 0x3E3968 |
| 11 | `8af43c1` | `3120bba224721fbbaa6110a79043876ac00ba352` | [AU9] SND HLE: SPU2 voice layer at 48 kHz |
| 12 | `243b759` | `0b7e0fae93fd4964eb261854c7699346d822e15a` | [AU9] ps2_snd_spu.h: include \<cstdlib\> |
| 13 | `9dadccd` | `2c57180d958e0f737d6acf7929de8576f7b7a50f` | [N11] profileable manifest for Odin simpleperf |
| 14 | `20db28f` | `56a5e8a6b249601a6193fea9ce77caf54d0cd584` | [N11] PS2X_GAME_THREAD_CPUS self-pinning + list parser test |

`a46fb2e` (unvalidated emitter change) excluded per brief. Tip: `56a5e8a`.
Runner-dir guard `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`: empty.

## Suite

From the worktree root, `../build/ps2xTest/ps2x_tests`: **611/611 pass, 0 fail, rc=0**
(`suite.log` in scratch). New folded tests present and passing: "PATH3 mask releases one EOP
packet per MSKPATH3 unmask window", "VIF UNPACK V4-5 expands RGBA5551 to 8-bit channels",
`Ps2ThreadAffinity` suite.

## Builds (one dir `~/dev/ssx3-work/F1/build`, GB8 recipe + `PS2X_BUILD_TEST=ON`)

Release, Homebrew clang, `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`
(`register_functions.cpp` `8ea8ed43…e662d688a3`, verified), `PS2X_GS_SHADOW_PARALLEL=ON`,
parallel-gs `963cb57` (clean), runtime/aggressive logs OFF, diag taps OFF.
Det runner = incremental reconfigure (`-DPS2X_ENABLE_DET_HASH_TAP=ON`, 354 steps) after
copying the clean runner out. Configure + both builds rc=0
(`configure-clean.log`, `build-clean.log`, `configure-det.log`, `build-det.log`).

| Runner | Det-hash tap | SHA-256 (two matching reads) |
| --- | --- | --- |
| `bin/runner-clean` | OFF (`det-hash:v1` absent from strings) | `86e328254d84322fe3e456d1022865c68f980179c25a34bafd07529aba66edde` |
| `bin/runner-det` | ON (string present) | `9587ef6204411eed3299db51e1cb24348c2562054fa08929aa2010307ac1f6b8` |

## B1 — det boot to t2400: frames + cid0 (one slot)

`f1_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400`
(GB8 driver + `PS2X_SOUND=1`, `PS2X_SND_LOG`; env: I26-FAST, empty mc0/mc1,
`PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, `PS2X_GS_BACKEND=parallel`,
`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`). bound=target, 85.8 s wall,
last_tick 2405, HUD at 35.4 s wall. `[gs-path]` matches GB8 (`hier_rule=flat-always …
desc=plain … gpu=Apple M5 Pro`). Zero FATAL. Sound live: `[snd-output] stream rate=48000`.
Boot-driver precheck: runner/ISO/ELF/codegen two SHA reads match, pins match.

**cid0 = 531, dmq = 531, done = 531** (`grep -c '^cid0 ' snd.log` = 531; final tick line
agrees). Matches AU9 and PCSX2 exactly.

Frames: 0.5 s snapshotter copies of `upload-latest.png`, selected by exact present tick from
the sidecar (GB8 Q3 method). I viewed all 5 (512×448):

| Target | Present tick | File (`run/B1/frames/snap/`) | Viewed verdict |
| --- | --- | --- | --- |
| 1090 | 1097 | `snap-001096t-0019.33s.png` | Select Peak: **Peak 1 mountain photo**, orange "3", SSX logo, ✕/△ glyphs, snowflakes. No atlas artifacts |
| 1180 | 1189 | `snap-001187t-0020.86s.png` | Post-1185-press, shows Select Event (Snow Jam, course map). Correct photo/map, no artifacts |
| 1800 | 1802 | `snap-001802t-0041.72s.png` | Race 00:00:01: lit snow, pines, mountain backdrop, EA Radio card, HUD 2ND/2. No dark region |
| 2100 | 2099 | `snap-002099t-0062.55s.png` | Race 00:00:06: pink checkpoint beam, rider, snow spray, panorama backdrop, trick counter 190, 1% |
| 2400 | 2399 | `snap-002398t-0082.41s.png` | Race 00:00:11: 14 MPH, 2%, slope/trees/spray, mountains |

All brief expectations met: Peak 1 photo, mountain backdrop, lit snow, trees, cid0=531.

## B2 — clean speed (exclusive lease, ≤ 5 min)

`f1_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B2 --stop-tick 2400`
(same env + `PS2X_SOUND=1`, `PS2X_VSYNC_RATE_LOG=1`). bound=target, **81.3 s wall**,
last_tick 2436, HUD at 35.9 s wall. Quiet host (no other runner/build; load 2.2 at claim).
Zero FATAL. Per-phase guest vsyncs/s ÷ 59.94 from the tick trace (`gb8_rates.py`; trace
authoritative — raw 5 s means smear at phase edges, same GB8 caveat):

| Phase (ticks) | B2 vs/s (×) | GB8 parallel vs/s (×) | B2 ÷ GB8 |
| --- | --- | --- | --- |
| Title [0,636) | 40.29 (0.672×) | 43.00 (0.717×) | 0.94× |
| Menus [636,1440) | 77.13 (1.287×) | 52.54 (0.877×) | 1.47× |
| Loading [1440,1714) | 28.30 (0.472×) | 27.05 (0.451×) | 1.05× |
| Race-start [1714,1800] | 16.69 (0.278×) | 16.46 (0.275×) | 1.01× |
| **Race (1800,2400]** | **15.01 (0.250×)** | **13.43 (0.224×)** | **1.12×** |
| Wall launch → race HUD (~t1714) | 35.9 s | 40.2 s | 1.12× |
| Wall launch → t2400 | 81.3 s | 90.4 s | 1.11× |

Raw 5 s cross-check (race window): n=8 mean 15.47 vs trace 15.01 — agrees. One run (brief
budget); no drift cancellation. Net effect of the fold on the Mac race: E57's VU1 win
outweighs RR1's ~50% more prims and AU9's voice layer. Sound costs nothing visible here
(B2 sound-on 0.250× vs GB8 sound-off 0.224× — different code, but no regression).

## Budgets and gaps

Builds 2/2 (one dir, clean + det reconfigure), boots 2/2 (B1 86 s, B2 81 s, each ≤ 500 s
wall cap), ~1 h of the 1.5 h box. Scratch `~/dev/ssx3-work/F1` 2.0 GB (≤ 20 GB).
Gaps: one speed run (no drift cancellation); frame ticks within Δ9 of target (snapshotter
phase, not exact-tick dumps — `PS2X_FRAME_DUMP_ONCE_TICKS` takes only 3 ticks); no Select
Mode frame (1185 press advances to Select Event within ~5 ticks, same as GB8); B1 carries
frame-dump + SND-log overhead (excluded from speed); menu glyph softness on parallel vs CPU
not re-checked (GB8 Q3 stands); N11's affinity knob untested on Mac (Linux/Android-only
code path, parser covered by unit test).

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/F1/PS2Recomp -b f1-fold fork/ssx3  # 71c952e
cd ~/dev/ssx3-work/F1/PS2Recomp
git cherry-pick -x 69b3256 ed35abf cbca1ad 802f5d2 0a4aa5e a4ecce5   # E57
git cherry-pick -x 3bc0449 f3dff5b 4f69c98                          # RR1
git cherry-pick -x fb75ec3 8af43c1 243b759                          # AU9 (never a46fb2e)
git cherry-pick -x 9dadccd 20db28f                                  # N11
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner             # empty
cd ~/dev/ssx3-work/F1
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON                                 # configure-clean.log
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner # build-clean.log
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests) > suite.log          # 611/611
cp build/ps2xRuntime/ps2EntryRunner bin/runner-clean
cmake -S PS2Recomp -B build -DPS2X_ENABLE_DET_HASH_TAP=ON           # configure-det.log
cmake --build build --parallel 8 --target ps2EntryRunner           # build-det.log
cp build/ps2xRuntime/ps2EntryRunner bin/runner-det
python3 f1_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400
python3 f1_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B2 --stop-tick 2400
python3 gb8_rates.py run/B2
```

## Orchestrator gate, Part 1 (2026-09-25)

**Pass.** I viewed the t2398 frame (race 00:00:11, 14 MPH, lit snow, trees, rock face, mountain
backdrop). 14 cherry-picks clean (not `a46fb2e`), suite 611/611, runner-dir diff empty, cid0 = 531.
Pushed `f1-fold` → fork `ssx3` **`56a5e8a`** (fast-forward from `71c952e`). Mac race 0.250× on
paraLLEl (one run). Menus ran at **1.287×**, i.e. faster than real time: the guest isn't paced to
59.94 Hz when it can outrun it (todo item). Parts 2 (Android) and 3 (iOS) released in parallel.

## Part 3 — iOS (device build `56a5e8a`, sim + iPad race, iPhone install-only)

Worker: Muse Code, brief `local/muse/prompts/F1.md` Part 3 only. Source: pushed
fork `ssx3` `56a5e8a6b249601a6193fea9ce77caf54d0cd584` (reused the Part 1
worktree `~/dev/ssx3-work/F1/PS2Recomp`; `HEAD == fork/ssx3`, clean).

Builds (`~/dev/ssx3-work/F1/ios/build-install.sh` = I32 recipe + 3-line sed:
`W`, `FORK_WT`, `PIN→56a5e8a…`; bundled env IS `local/research/I32/ps2x.env`,
SHA `0041e09a…` matches I32's committed `env-sha.txt` — sound on,
`PS2X_MC_ROOT=${DOCUMENTS}/mc0`): preflight rc=0 (runner-dir diff empty, deps
pinned, profile `f0793278` valid to 2027-09-17, both devices connected);
configure sim + device rc=0 (`-O3 -DNDEBUG` asserted 2 lines each, raylib DPI
patch "already applied"); sim build + stage + install rc=0; device build +
stage + sign rc=0 (`codesign --verify --strict` passed, ELF/ISO stage copies
`cmp`-equal, bundle `org.ps2x.ps2entryrunner`).

| Binary | SHA-256 (two matching reads) |
| --- | --- |
| sim `ps2EntryRunner` | `21f7954fd5848a3f1d496ee67eb019aa072ce19bbc2f8a9a612adcc493ff16ac` |
| device unsigned | `d989a3f5b7f9071240080118e52a140bd2a66a2ce0646e5969c695701bdc0b69` |
| device signed (installed) | `89ed20d41b93fdd7d6796c4a5a4a15adcf7a09896ed923d241ca9eb1f1134277` |

Simulator (fresh container: uninstalled first — I32's save-test `mc0` with
Brad's save was still in the sim container; reinstalled to empty Documents;
bundled I26-FAST route, sound on; one lease slot each, released; zero FATAL,
48 kHz stream, overlay shown; all frames SHA-matched on two reads):

| Run | Shot (capture tick) | Viewed verdict | SHA-256 |
| --- | --- | --- | --- |
| peak (31 s) | `shot-t1010` (1018) | **Select Peak: Peak 1 mountain photo**, Peaks 2/3 locked, correct text — RR1 fix visible on iOS | `e9c398bd…` |
| sim (134 s) | `shot-t1050` (1189) | Select Event (Snow Jam, course map); menu correct, Peak overshot by the 2 s poll | — (menu ref) |
| sim | `shot-t1750` (1762) | Race 2ND/2 00:00:00 0%, EA Radio "Glass Danse - Oakenfold Remix / The Faint", gate, lit snow | `c524c8a3…` |
| sim | `shot-t2100` (2126) | Race 2ND/2 00:00:07 1%, pines, spray, mountains; advancing | `6e1e76ce…` |

iPad (Air 11" M2): install rc=0 (seq 1884, bundle `9255EAFA…`); deploy SKIP +
7 exact-size OKs (Brad's save + 496-byte manual-play env intact). Live
container read from a ~5 s probe console (bogus-UUID `MC_ROOT`, title only,
terminated, no screenshots): **`E26D3546-…`** — rotated from I32's
`8B1267A4`, so reinstalls do rotate it. One test launch (env: I26-FAST script
byte-exact 484 chars, `MC_ROOT=<live>/Documents/mc-fresh`,
`PS2X_VSYNC_RATE_LOG=1`, no vpad injections): 209 s, ticks 1116/1751/1970/2155,
terminated after (`info processes` clean), zero FATAL, launcher kept all 3,
48 kHz, overlay shown. Portrait compat crop + background app form as in I32.

| Shot (tick) | Viewed verdict | SHA-256 |
| --- | --- | --- |
| `shot-t1050` (1116) | Select Mode (Race/Freestyle) — missed Peak by 17 ticks (2 s poll overshoot), menu correct | `a933bcb6…` |
| `shot-t1750` (1751) | Race 1ST/2 00:00:00 0%, EA Radio "Go / Andy Hunter / Exodus", gate — race start on-route | `b9752675…` |
| `shot-t1960` (1970) | Race 2ND/2 1%, gate pole, spray, pines; advancing | `dea4b0b8…` |
| `shot-t2140` (2155) | Race 2ND/2 1%, slope/trees/spray/mountains; advancing | `c797f838…` |

Fresh-card proof: `mc-fresh` + `mc-fresh_slot1` created at the live path
(this run's override resolved, unlike I32's stale UUID); route hit the race
on pace (Finding F1: save-present routes derail); deploy re-ran after: SKIP +
7 OKs, Brad's `mc0` byte-identical. Observed diagnostic pace: race window
1751@106s→2155@207s ≈ 4.0 vs/s ≈ **0.067×** (vsync-rate log + screenshots on —
not a speed number).

iPhone (16 Pro Max): install rc=0 (seq 4824, bundle `BC672081…`); deploy SKIP
+ 7 OKs. **Never launched** — no launch/process command targeted the iPhone.

Budgets and gaps: 2 builds, 2 sim runs (134 s + 31 s), 1 probe + 1 iPad test
(209 s), 2 installs; ~25 min of the 1 h box. Scratch `~/dev/ssx3-work/F1`
9.0 GB (ios 6.9 GB) ≤ 20 GB; disk 107.6/200 GB; Simulator shut down; no lease
held. Gaps: iPad Select Peak missed by 17 ticks (sim covers the Peak 1
photo); iPad pace is diagnostic, not a clean speed number; `mc-fresh`,
`mc-fresh_slot1`, `mc1` dirs left in iPad Documents (harmless); first probe
failed on `--environment-variables` taking JSON content, not a path (I32's
script passes content via `$1`) — fixed, no device state touched.

Exact commands:

```sh
sed -e 's|^W=.../I32$|W=.../F1/ios|' -e 's|^FORK_WT=.*|FORK_WT=.../F1/PS2Recomp|' \
  -e 's|^PIN=f949ff0...|PIN=56a5e8a6b249601a6193fea9ce77caf54d0cd584|' \
  local/research/I32/build-install.sh > ~/dev/ssx3-work/F1/ios/build-install.sh
bash ~/dev/ssx3-work/F1/ios/build-install.sh preflight configure_sim configure_device
bash ~/dev/ssx3-work/F1/ios/build-install.sh build_sim stage_sim sim_install
bash ~/dev/ssx3-work/F1/ios/build-install.sh build_device stage_device sign
xcrun simctl uninstall $SIM org.ps2x.ps2entryrunner   # I32 save-test mc0 was in the container
bash ~/dev/ssx3-work/F1/ios/build-install.sh sim_install
bash ~/dev/ssx3-work/F1/ios/sim-run.sh                # thresholds 1050 1750 2100
bash ~/dev/ssx3-work/F1/ios/sim-peak-run.sh 1010      # 0.5 s poll
bash ~/dev/ssx3-work/F1/ios/build-install.sh install_ipad
bash local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/F1/ios/ipad-probe.sh             # live container E26D3546-…
bash ~/dev/ssx3-work/F1/ios/ipad-run.sh run-ipad-env.json "1050 1750 1960 2140"
bash local/research/I31/deploy-ios.sh ipad           # save byte-identical after
bash ~/dev/ssx3-work/F1/ios/build-install.sh install_iphone
bash local/research/I31/deploy-ios.sh iphone         # never launched
xcrun simctl shutdown $SIM
```
