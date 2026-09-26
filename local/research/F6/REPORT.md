# F6 — Brad's next device build: Vulkan present on the Odin + VU1 speed-ups

Worker: muse. Brief: `local/muse/prompts/F6.md` (Parts 1+2; stop before play-build
install on the Odin / iPhone install).
Fork `ssx3` = `fb28d99` (pushed, verified); paraLLEl-GS fork `ssx3` = `1b3a294`
(pushed, verified). No push.

**Status: done. Stopped before the play-build install (Odin) and the iPhone
install, as briefed. Hand back: 1× pipelined race 0.263× new vs 0.244× F5
(+7.6 %); 4×+hi-res 0.178× (costs 32 %, over the 5 % budget); iPad green.**

**Result for the play-build decision: 1× pipelined** (4× costs 32 %).

## Pins

| Item | Value |
| --- | --- |
| Fork `ssx3` | `fb28d99aa1c41eaddb742dab49a4f6d5ae26cd94` (pushed, verified) |
| paraLLEl-GS `ssx3` | `1b3a2948cc55e74f975e42b79d08983f31c2dbb6` (pushed, verified); Granite `166ba21a` |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` (9,457 files) |
| VU1 images | `vu1gen-ssx3` = F5's 7 SHAs (VR2 stage 1 needs no regen) |
| F6 APK | `f39905db…` (180,213,320 B; remote ×2 + pulled ×2) |
| F5 play APK (ABBA ref) | `4ff81032…` (reused, SHAs re-read per leg) |
| iPad bundle | `CA7F6F82-…` (seq 1996; signed `e22bf2cf…`) |

## Part 1 — Odin

### Build (bytesize `/home/brad/f6` — GREEN)

Staging (F5 recipe + F6 pins): `PS2Recomp/` = `git archive fb28d99`
streamed from the mini (363 files both sides; `minSdk 29`,
`ps2_present_vk_android.cpp` present; tar kept as scratch
`fork-fb28d99.tar`, SHA `f736d903…`); `parallel-gs/` = tar of the mini's
`1b3a294` checkout with Granite (`gs_renderer.cpp` `52e8dc9e…` both sides,
0 `._*` — `COPYFILE_DISABLE=1`; tar `111099c1…`, 446 MB);
`codegen-ssx3`/`vu1gen-f6`/`jniLibs` symlinks to `/home/brad/f5/*`
(verified: 9,457 files, `register_functions.cpp` `8ea8ed43…`, all 7 VU1
SHAs = `vu1gen.sha`, Turnip `libvulkan_freedreno.so` 14,188,488 B).
`build.sh` (`local/research/F6/build-android.sh`) SHA `a5c8cab0…`
identical local/remote.

Build: **BUILD SUCCESSFUL in 23 m 45 s**, 56 task lines, zero FAILED,
`--max-workers=2` kept. Success log pulled to scratch
(`odin/assembleRelease-remote.log`, 31,484 B). APK
`f39905dbf13431cd184b2dccf4f5baef66d46c62857d9beba76aa4fb5655740a`,
180,213,320 B — remote ×2 + pulled ×2, all four match; kept at
`~/dev/ssx3-work/F6/odin/app-release.apk`.

Contention note: bytesize was idle at launch (checked, no java/ninja),
but BA1's `lto` build ran concurrently (`ba1/lto` log 23:57, BUILD
SUCCESSFUL in 22 m 26 s) — both walls are ~2.4× a solo build (F5: 9 m
26 s). The APK is unaffected (deterministic inputs, SHAs verified).
Bytesize held the ssh open throughout (F5 G5 rule); a plain `scp` cannot
reach WSL paths, so the APK/log were pulled via `ssh … cat` streams.

### ABBA (new 1× VK vs F5 play `4ff81032…`)

Method: `local/research/F6/launch.py` + `cooldown.py` (VK1 lineage, F6
dirs/lease), I26-FAST, unpaced, sound on, pipelined 1×, stop 4500, cool to
status 0 + fixed 180 s. New legs install `f39905db…` per leg; F5 legs install
`~/dev/ssx3-work/F5/odin/app-release.apk` (`4ff81032…`) per leg. Order ABBA =
new, F5, F5, new. Tooling: `launch.py` (F6 paths/lease, `--apk` per-leg
install), `cooldown.py`; rates via `local/research/F4/phases.py`.

| Run | Var | End | Race (ticks→wall) | Race rate | GPU busy race mean (n) | Thermal | `[present-vk]` / `vk_dropped` | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A-new | STOP 4587, 221.7 s | 1714→4587 / 182.2 s | 15.77/s = **0.263×** | 36.4 % (31) | 0→3 | layer active, dropped 0 (×14), timeouts 0 | 0 |
| R2 | A-F5 | STOP 4502, 232.3 s | 1714→4502 / 190.5 s | 14.63/s = **0.244×** | 32.0 % (32) | 1→3 | n/a (GL path) | 0 |
| R3 | A-F5 | STOP 4506, 231.2 s | 1714→4506 / 190.6 s | 14.65/s = **0.244×** | 31.8 % (32) | 0→3 | n/a (GL path) | 0 |
| R4 | A-new | STOP 4578, 222.4 s | 1714→4578 / 182.1 s | 15.73/s = **0.262×** | 35.9 % (30) | 0→3 | layer active, dropped 0 (×14), timeouts 0 | 0 |

Cool-downs (all green, status 0 at launch): R1 37.6→37.2 °C (immediate 0 +
180 s); R2 46.9→39.1 °C (retry; the first sample caught VK2's hot run, see
below); R3 43.8→38.4 °C; R4 46.5→38.0 °C. Every run: lease held (atomic claim
from R3 on, per the 09-26 rule), keyguard false, 100 % on AC, app stopped,
Brad env + mc0 pins before, env restored (`a8d651a7…` match=True) +
`restore-play.sh` (F5 APK + 6/6 saves) after, force-stopped, lease released,
0 disconnects.

A-new legs: 15.77 / 15.73 (agree 0.3 %), mean **15.75/s = 0.2628×**. A-F5
legs: 14.63 / 14.65 (agree 0.1 %), mean **14.64/s = 0.2443×** — reproduces
F5's 0.2441× in-session. **New/F5 = 1.076× (+7.6 %)** at 1× pipelined (VR2
stage 1, net of the −0.7 % VK1 present cost measured on the F5 base). New-leg
per-5s ramps 10→16 steady, 19–21 in the last 30 s (same shape as F5's A legs).
GPU: new ≈ 36 %, F5 ≈ 32 %. SF column on the new legs reads a flat 45.8–47.3/s
(the window layer barely updates with the GL swap skipped — stale-timestamp
artifact, guest ticks unaffected); F5 legs read 59.6–60.4 as before.

Per-phase table (guest vsyncs/s; menus are at/near full speed on both):

| Phase | R1 new | R4 new | R2 F5 | R3 F5 | R5 4× new |
| --- | --- | --- | --- | --- | --- |
| title/startup | 58.64 | 58.17 | 58.29 | 58.31 | 57.77 |
| main menu | 55.17 | 55.08 | 53.13 | 53.35 | 50.49 |
| Select Character | 55.72 | 55.58 | 54.85 | 54.81 | 49.21 |
| Setup Character / Peak | 64.66 | 64.99 | 66.92 | 66.47 | 47.03 |
| Select Mode / Event / My Rules | 54.40 | 54.10 | 54.74 | 54.65 | 64.12 |
| loading + Rival card | 20.88 | 20.67 | 18.53 | 18.64 | 16.10 |
| **race** | **15.77** | **15.73** | **14.63** | **14.65** | **10.69** |

Coordination: after R1, VK2 claimed the Odin (`VK2 … ST1`, pid 3567 live) for
the RV5-blocker fixes. R2's first cooldown sampled their hot run (status 3)
and was discarded; R2+ waited for `LEASE_FREE` and re-cooled from scratch.
Separately the orchestrator ruled (BA1's unleased install killed VK2's stress
run ~00:15): every install/launch/force-stop holds the lease through
`local/tooling/odin_lease.sh`; order F6 → VK2 → BA1. R1/R2 ran under the old
direct claim (format-compatible); R3+ claim atomically first, and
`local/research/F6/restore-play.sh` (VK1's steps, F6 label, atomic) runs after
every leg.

### 4×+hi-res leg (single, new APK)

R5-4x, variant B, new APK `f39905db…`: cool-down 45.3→37.2 °C (status 0 +
180 s); STOP 4524, 305.9 s wall; race 1714→4524 / 262.9 s = **10.69/s =
0.178×**; GPU busy race mean 52.7 % (n=44); thermal 0→0; `vk_dropped=0`
(×12), release timeouts 0; 0 FATAL; 0 disconnects; env restored +
`restore-play.sh` after. Per-5s is flat ~10–11 with 12–13 at the very end
(GPU/driver-bound, no ramp — F5's B shape).

4× vs F5's 0.168×: **1.062× (+6 %)**. 4× vs F6 1× (0.2628×): 0.679 —
**4×+hi-res costs 32 %**, far over Brad's 5 % budget. Handed back as asked;
the orchestrator decides 1× vs 4× for the play build (no install done here).

### Screencaps viewed (all 1920×1080)

| Cap | Verdict |
| --- | --- |
| R1 `sc01-tick2100` (race t~2114) | **Fills 1920×1080, no borders** (VK layer; F5's GL path showed a bordered box). Race 2ND/2 00:00:07 1 %, correct colours, full brightness; rider mid-crash wipeout with spray |
| R1 `sc02-tick3000` (race t~3000) | Full screen; **rider solid and lit mid-carve, white carve groove + spray trailing the board** (brief's rider + trail check) |
| R5 `sc01-tick2100` (4× race t~2114) | Full screen at full resolution (no 360-line downscale); race 2ND/2 00:00:06 1 %, trick 370, EA Radio "Go / Andy Hunter / Exodus" (same card as F4/F5 — same RNG), rider mid-crash RECOVER meter, crisp HUD |

## Part 2 — iOS (device build `fb28d99`, iPad 4×+hi-res + zero-copy; iPhone stopped)

Worker: muse, brief `local/muse/prompts/F6.md` Part 2 (alongside Part 1; Odin and
`~/dev/ssx3-work/F6/PS2Recomp` fork worktree shared with Part 1 staging only).
Source: pushed fork `ssx3` `fb28d99` in a detached worktree
`~/dev/ssx3-work/F6/PS2Recomp` (clean). First-failure rule never triggered. No push.

**Result: iPad green on the full F6 stack. Stopped before the iPhone install**
(orchestrator releases it after RV5). One device build (F6 = F5's VU1 images
linked: 14,343 `VU1RecompImage` symbols, the exact F5 count); bundled env =
F5's unchanged (committed at `local/research/F5/ps2x.env`). One fresh-card iPad
launch: parallel backend, `ssaa=4 hires_scanout=1 present_pipeline=1`,
1280×896→1024×896 scanout, 5× `ios bind … rc=0`, stats
`readback_ms_avg=0 copy_ms_avg=0 l2h_bytes=0` (zero-copy kept), 0 FATAL, race
reached in 58 s wall. Frames viewed: Select Event, race start, and t2100 with
the carve groove + spray; pad v2 in place. Brad's `mc0` byte-identical after.

Recipe: `~/dev/ssx3-work/F6/ios/build-install.sh` = F5i's script + `W`/`FORK_WT`/
`PGS→~/dev/ssx3-work/F6/parallel-gs`/`PIN→fb28d99…`/`PGSPIN→1b3a294…`/
`VU1GEN→~/dev/ssx3-work/vu1gen-ssx3`, `ENVFILE` kept at F5's `ps2x.env`;
`ipad-probe.sh`/`ipad-run.sh` from F5i's copies (`OUT` repointed). No sim build
(F3 precedent plus I33's sim descriptor-indexing blocker).

| Item | Pin | Receipt |
| --- | --- | --- |
| Fork worktree `~/dev/ssx3-work/F6/PS2Recomp` (detached) | `fb28d99aa1c4…` == `fork/ssx3`, clean | `logs/fork-head.txt`, preflight rc=0 (runner-dir diff empty, PIN ancestor) |
| parallel-gs (F6 clone, read check) | `1b3a2948cc55…`, clean; Granite `166ba21a` | preflight re-hashed |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` (9,457 files) | `logs/codegen-sha.txt` |
| VU1 images (`vu1gen-ssx3`) | 7/7 SHAs match F5 `vu1gen.sha` | `logs/vu1-sha.txt`; configure `VU1 recomp: 7 images` |
| MoltenVK 1.4.2 device slice | staged `6cd58884…` = F5 pin | `logs/device-mvk-stage-sha.txt` |
| ELF / ISO staged | `1b49d05c…` / `3c2f8eb1…` | stage SHAs |
| Bundled env `local/research/F5/ps2x.env` | SHA `4663d126…` (unchanged from F5) | `logs/env-sha.txt` |
| Device binary unsigned | `8e52f43b…` (×2), 150,860,184 B | `logs/device-source-binary-sha.txt` |
| Device binary signed (installed) | `e22bf2cf…` (×2) | `logs/signed-binary-sha.txt`; `codesign --verify --strict` passed |

iPad (Air 11" M2): install rc=0 (seq 1996, bundle `CA7F6F82-…`); deploy
SKIP + 7 OKs; probe Data `81C72E16-…` (bundle path matches install URL).
One fresh-card launch (`mc-f6`, route 484 chars byte-exact vs bundled,
re-armed via `-e`, `PS2X_VSYNC_RATE_LOG=1`, no backend overrides): 58 s
wall, ticks 1137/1860/2191, terminated after (0 procs left), zero FATAL.
Bundled env selected the full stack:
`[gs:parallel] live backend selected`,
`[gs:parallel] quality ssaa=4 (asked 4, device max 4) ssaa_textures=0
hires_scanout=1 present_pipeline=1`,
`[gs:parallel] scanout size 1280x896 tick=41 hires=1` (1024×896 follows,
F5's shape).

| Shot (tick) | Viewed verdict | SHA-256 (12) |
| --- | --- | --- |
| `shot-t1090` (1137) | Select Event (Snow Jam / Metro-City / Happiness + Race course map, legible), full brightness | `9dce5df5e4ae` |
| `shot-t1810` (1860) | Race 2ND/2 00:00:02 0%, EA Radio "Poor Leno - Silicon Soul Remix / Royksopp", rider at the gate, beam | `c05c04262df6` |
| `shot-t2100` (2191) | Race 2ND/2 00:00:08 1%, 14 MPH; **carve groove trailing down-slope + spray**, rider solid, no translucent boxes | `04d861092f36` |

Pad v2: D-pad, face buttons, shoulders in place; only the known
portrait-compat SELECT/START overlap (I28, pre-existing). RNG note: this run
shows "Poor Leno" where F5i's iPad run showed "Deepsky" — same class as F4/F5's
device EA-card divergence under identical inputs, not chased (Mac det-hash
gates in VK1 Part 3 prove the fold guest-identical). Post-run deploy re-ran: 7
OKs, Brad's `mc0` byte-identical. Diagnostic pace only: launch→t2100 58 s
(console-pty + vsync-rate overhead, one run — not a speed number).

Budgets and gaps: 1 device build (BUILD SUCCEEDED), 1 probe (~2 s) + 1
test (58 s), 1 install; iPhone install stopped per the brief (+ orchestrator
update: RV5's Android-only blockers don't affect iOS).

Exact commands:

```sh
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/F6/PS2Recomp fb28d99
git clone ~/dev/parallel-gs ~/dev/ssx3-work/F6/parallel-gs  # checkout 1b3a294 + submodules
bash ~/dev/ssx3-work/F6/ios/build-install.sh preflight configure_device build_device stage_device sign
bash ~/dev/ssx3-work/F6/ios/build-install.sh install_ipad
bash local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/F6/ios/ipad-probe.sh             # live container 81C72E16-…
bash ~/dev/ssx3-work/F6/ios/ipad-run.sh ~/dev/ssx3-work/F6/ios/run-ipad-f6 ~/dev/ssx3-work/F6/ios/run-ipad-env.json "1090 1810 2100"
bash local/research/I31/deploy-ios.sh ipad           # save byte-identical after
# STOP: no install_iphone (orchestrator releases after RV5)
```

## Budgets and gaps

- Builds: 1 iOS device (+ stage/sign), 1 Android (bytesize, 23 m 45 s under
  BA1 contention). Boots: 1 iPad probe + 1 iPad test (58 s), 5 Odin legs
  (R1–R4 ~225 s each, R5-4x 306 s; all ≤ 600 s wall). Nothing exceeded its cap.
- Scratch `~/dev/ssx3-work/F6`: **5.5 GB** (≤20 GB brief cap) — ios 3.5 G,
  parallel-gs 1.3 G + tar 426 M, odin 197 M (APK + caps + logs), fork tar
  22 M, worktree 23 M. Kept for the play-build decision.
- Disk: global mini usage was 182.8/200 GB before F6; F6 adds ~5.5 GB.
- Never pushed; fork worktree detached at the pushed tip; text in git
  (REPORT, 4 scripts, per-run text logs); runners signalled only by the
  drivers; no lease held at close (`LEASE_FREE F6 done`); BA1/VK2 lanes'
  files untouched.
- End state: Brad's F5 play APK `4ff81032…` installed, env `a8d651a7…`,
  save 6/6 OK, `mc0-test` empty, app stopped, 100 % on AC. No play-build
  install and no iPhone install (both stopped per the brief + RV5 gate).
- Gaps:
  - G1. Single 4× leg (brief: single, not ABBA); 1× legs are ABBA with
    0.3 % / 0.1 % leg agreement.
  - G2. SF presents/s on the VK legs is a stale-timestamp artifact
    (45.8/47.3/38.7 flat); display-side only, guest ticks unaffected.
  - G3. Device EA-Radio RNG differs run to run (iPad "Poor Leno" vs F5i's
    "Deepsky"; Odin R5 matches F4/F5's "Go") — known device divergence
    class, not chased; Mac det-hash gates prove the fold guest-identical.
  - G4. The F6 APK build wall (23 m 45 s) is contended (BA1's `lto` build
    overlapped); the APK is unaffected.
  - G5. RV5's 2 Android Vulkan-present blockers (VK2 fixing) landed during
    this brief; the numbers above are the as-briefed VK-default build. The
    orchestrator's fallback (`PS2X_PRESENT_VULKAN=0` in Brad's Odin env)
    is a play-build decision, not measured here.

## Exact commands

```sh
# pins
git -C ~/dev/PS2Recomp rev-parse fork/ssx3  # fb28d99
git -C ~/dev/parallel-gs rev-parse origin/ssx3  # 1b3a294
# iOS (Part 2)
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/F6/PS2Recomp fb28d99
git clone ~/dev/parallel-gs ~/dev/ssx3-work/F6/parallel-gs  # + checkout 1b3a294, submodules
bash ~/dev/ssx3-work/F6/ios/build-install.sh preflight configure_device build_device stage_device sign install_ipad
bash local/research/I31/deploy-ios.sh ipad; bash ~/dev/ssx3-work/F6/ios/ipad-probe.sh
bash ~/dev/ssx3-work/F6/ios/ipad-run.sh ~/dev/ssx3-work/F6/ios/run-ipad-f6 ~/dev/ssx3-work/F6/ios/run-ipad-env.json "1090 1810 2100"
bash local/research/I31/deploy-ios.sh ipad  # byte-identical after; STOP before install_iphone
# Android (Part 1)
git -C ~/dev/PS2Recomp archive --format=tar fb28d99 > ~/dev/ssx3-work/F6/fork-fb28d99.tar
tar -cf parallel-gs-1b3a294.tar --exclude=.git parallel-gs  # COPYFILE_DISABLE=1
ssh bytesize 'wsl -d Ubuntu -- bash -lc "mkdir -p /home/brad/f6/PS2Recomp ..."'
cat fork-fb28d99.tar | ssh bytesize 'wsl ... "tar -x -C /home/brad/f6/PS2Recomp"'
cat parallel-gs-1b3a294.tar | ssh bytesize 'wsl ... "tar -x -C /home/brad/f6"'
ssh bytesize 'wsl ... "ln -sfn /home/brad/f5/codegen-ssx3 /home/brad/f6/codegen-ssx3 ..."'  # + SHA verifies
ssh bytesize 'wsl -d Ubuntu -- bash -lc "chmod +x /home/brad/f6/build.sh && /home/brad/f6/build.sh"'  # held open
ssh bytesize 'wsl ... "cat .../app-release.apk"' > ~/dev/ssx3-work/F6/odin/app-release.apk  # SHA x2
# Odin (Part 1)
python3 local/research/F6/cooldown.py --label R1  # + R2/R3/R4/R5-4x
bash local/tooling/odin_lease.sh claim F6  # R3+ (atomic rule 09-26)
python3 local/research/F6/launch.py --label R1 --variant A --wall 600 --stop-tick 4500 --apk ~/dev/ssx3-work/F6/odin/app-release.apk --apk-sha f39905db...
python3 local/research/F6/launch.py --label R2 --variant A ... --apk ~/dev/ssx3-work/F5/odin/app-release.apk --apk-sha 4ff81032...  # R3 same; R4 new; R5-4x variant B new
python3 local/research/F4/phases.py local/research/F6/logs/R<N>
bash local/research/F6/restore-play.sh  # after every leg; F5 APK + env a8d651a7 + 6/6
```

## Orchestrator gate, Parts 1+2 (2026-09-26)

**Pass.** Odin 1× pipelined **0.263×** (+7.6 % vs F5, ABBA legs within 0.3 %); 4×+hi-res 0.178× (−32 %) →
the play build stays 1×. Viewed R1 `sc02-tick3000`: full-screen 16:9, rider lit, carve trail, HUD; the
Android gesture-bar handle shows at the bottom (immersive mode: small follow-up). iPad green.
Releases: **iPhone install now** (RV5 found nothing affecting iOS). **Odin play install waits**: VK2's and
BA1's device runs come next and their restore scripts reinstall F5; after them Brad's Odin gets one build
with VK2's present fix (Vulkan on) plus whatever else has folded by then.

## Part 3 brief (orchestrator)
iPhone only: `install_iphone` with the F6 device build (already signed `e22bf2cf…`), then
`bash local/research/I31/deploy-ios.sh iphone` (Brad's save + env). **Never launch.** Verify the installed
bundle and 7 OKs; append `## Part 3`; commit `[F6] Part 3 …`; stop.

## Part 3 — iPhone install only (device build `fb28d99`)

Worker: muse, brief above. No Odin play install (orchestrator: after VK2/BA1).

- Staged binary re-read `e22bf2cf…` before install (matches the Part 2 signed
  SHA); no rebuild.
- iPhone 16 Pro Max (`00008140-0002505001F3001C`): `available (paired)` at
  check and at install (never `unavailable`); install rc=0 (seq 4876,
  bundle `9D47612D-…`); deploy SKIP + 7 OKs (6/6 saves + `ps2x.env`).
- **Never launched** — no launch/process command targeted the iPhone UDID.

Exact commands:

```sh
xcrun devicectl list devices  # iPhone available (paired)
shasum -a 256 ~/dev/ssx3-work/F6/ios/staged/ps2EntryRunner.app/ps2EntryRunner  # e22bf2cf…
bash ~/dev/ssx3-work/F6/ios/build-install.sh install_iphone
bash local/research/I31/deploy-ios.sh iphone  # never launched
```
