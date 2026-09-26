# IP1 — iPad full screen: universal device family

Worker: muse. Brief: `local/muse/prompts/IP1.md` (steps 1–6; stop before
the iPhone install).

**Status: first failure — hand back. `UIDeviceFamily = [1, 2]` is confirmed
in the built and staged plists, but iPadOS opened the app in the same
centered 1180×1640 portrait window the iPhone-compat builds got
(`window=590x820`, byte-identical to F7's and IS1's console lines), not
full screen. The present path is correct for the window it got (picture is
exactly 16:9, full window width), so this is neither briefed alternative
(a) nor (b): it is a new alternative (c), persisted/default compact window
geometry on iPadOS 26. No rebuild consumed, no budget exceeded. The IP1
build is left installed per the brief, but it does NOT deliver the goal —
the orchestrator should decide whether it stays as Brad's play build.**

## Pins

| Item | Value |
| --- | --- |
| Fork worktree `~/dev/ssx3-work/IP1/PS2Recomp`, local branch `ip1` | `ae6b137178b401f1de69bfbf566fb2d487154f83` = fork/ssx3 `b97b241` + IP1 commit (plain, no push) |
| Fork `ssx3` parent | `b97b24117e1de632d7990cf2a244162412a9898d` ([VR4] FMAC fold) |
| paraLLEl-GS clone (detached) | `3d72467033ce6c4a8c7319e567880578aca39f6b`; Granite `166ba21a247a681903cc9d0bb6562fe50a554c85`; status clean |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` (9,455 sources at configure) |
| VU1 images (`vu1gen-ssx3`) | 7 files |
| Bundled env `local/research/F7/ps2x.env` | `cffff3e8…` (= F7, unchanged) |
| ELF / ISO staged | `1b49d05c…` / `3c2f8eb1…` (= F7) |
| MoltenVK device slice staged | `6cd58884…` (= F5/F6) |
| Device binary unsigned | `31faaa58…` (×2, 151,855,912 B) |
| Device binary signed (installed) | `f46e6da9…` (×2 at sign, ×2 re-read before install; 152,171,680 B) |
| iPad install | seq 2028, bundle `48333EAD-…`, Data container `C207B22D-…` |
| `VU1RecompImage` symbols (staged binary) | 17,607 (F7: 14,343 — fork moved a5e5940 → b97b241; descriptive) |

## Fix (committed, no push)

`[IP1] iOS: universal device family so iPadOS runs full screen` — 2-line
addition in the `if(PS2X_IS_IOS)` block of `ps2xRuntime/CMakeLists.txt`
(`# IP1:` comment + `set_target_properties(ps2EntryRunner PROPERTIES
XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2")`). Runner-dir check
(`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) empty before
and after. Generated `PS2RetroX.xcodeproj` contains
`TARGETED_DEVICE_FAMILY = "1,2"`.

## Build (device only)

`preflight configure_device build_device stage_device sign`, all rc=0.
One setup fix, no code rebuild: the fresh PGS clone lacked Granite's
nested submodules (`vulkan-headers` missing → configure error), fixed with
`submodule update --init --recursive` (18/18) + build-dir wipe + configure
retry. `** BUILD SUCCEEDED **` ×1, `-O3 -DNDEBUG` cache lines = 2, PGS
shadow ON, VU1 recomp 7 images, `codesign --verify --strict` passed.

Alternative (a) ruled out:

- Built `Info.plist`: `UIDeviceFamily => [1, 2]`.
- Staged `Info.plist`: `UIDeviceFamily => [1, 2]`.

## iPad run (1 install, probe + 1 run)

Install rc=0 over IS1's build (update-in-place; Documents survived:
deploy SKIP + 7 OKs). Probe rc=0 in 2 s (bundle path matches install URL).
One fresh-card run (`mc-ip1`, route byte-exact vs bundled I26-FAST,
`PS2X_VSYNC_RATE_LOG=1`): 45 s wall, ticks 1200/1839/2100, terminated
after (0 procs left, re-verified at close). Post-run deploy re-ran: SKIP +
7 OKs; `mc-ip1` + `mc-ip1_slot1` present on device (run wrote to the fresh
card); Brad's `mc0` sizes unchanged. Build left installed, app stopped.

Console: parallel backend, `ssaa=4 hires_scanout=1 present_pipeline=1`,
scanout 1280×896→1024×896, `readback_ms_avg=0 copy_ms_avg=0
l2h_bytes=0` (zero-copy kept), `[mtvu] mode=threaded` + summaries all
`violations=0`, **0 FATAL**.

## The failure: windowed, not full screen

`[ios-window] window=590x820 drawable=1180x1640` — byte-identical to F7's
compat-box runs and IS1's run on this same iPad. All three shots are
2360×1640 (full screen capture) with the app in a centered portrait
window; measured with a stdlib PNG decoder (`/tmp/ip1_measure.py`, kept
outside the repo per rules — rerun on request):

| Shot (tick) | Shot size | Window rect | Picture rect | Ratio | Verdict |
| --- | --- | --- | --- | --- | --- |
| `shot-t1090` (1200) | 2360×1640 | x[592,1771] × full height (1180×1640) | x[592,1771] y[488,1151] = 1180×664 | 1.7771 | Select Event (Snow Jam / Metro-City / Happiness + Race map, legible), full brightness |
| `shot-t1810` (1839) | 2360×1640 | same | same geometry | 1.7771 | Race 2ND/2 00:00:03, EA Radio "Poor Leno - Silicon Soul Remix / Royksopp" (same card as F6/F7 iPad runs), rider mid-air with spray |
| `shot-t2100` (2100) | 2360×1640 | same | same geometry | 1.7771 | Race 2ND/2 00:00:07 1 %, rider mid-trick, board visible, spray trailing |

SHA-256 (12): t1090 `33b0980c9bce`, t1810 `ff79f497adbd`, t2100 `c70477e8e0eb`.

Geometry notes (all measured, not eyeballed):

- Window is centered (margins 592/588) and spans the full 1640 height; it
  is exactly half the screen width. The iPadOS 26 window chrome (traffic
  lights, rounded corners, wallpaper both sides) is visible in every shot.
- Picture touches both window edges (sharp wallpaper→content steps at
  x=592 and x=1772 on a mid-picture row) and is 1180×664 = **1.7771**
  (16:9 ± 0.01 ✓), so the present path is right for the window it got —
  alternative (b) ruled out.
- Pad v2 in place: L2/L1/R1/R2 top bar; d-pad bottom-left; X bottom-right;
  SELECT/START overlapping center-bottom (the known I28 portrait-compat
  overlap — still present because the window is still portrait
  phone-sized). The translucent face buttons (○/△/□) overlay the right
  part of the game picture.

## Hypothesis scorecard

- H (universal family → full 2360×1640 window): **not confirmed**.
- (a) plist lacks the key: ruled out (`[1, 2]` in both plists).
- (b) picture sized from a stale iPhone drawable: ruled out (1.7771, full
  window width).
- (c, new): iPadOS 26 gave the universal app the persisted/default compact
  portrait window (590×820 pt, exactly the compat-box size) despite
  `UIRequiresFullScreen`. Sub-hypotheses: (c1) geometry restored from the
  previous installs under the same bundle ID (update-in-place; Documents
  and plausibly scene state survived); (c2) system default / the key no
  longer forces full screen on iPadOS 26. Not discriminated — needs a
  delete + reinstall + launch, or a hand resize by Brad, both outside this
  brief's budget.

## Budgets and gaps

- Builds: 1 device (+1 failed-then-fixed configure, setup only). Installs:
  1. Launches: probe + 1 run (2). Time ~1 h of 1.5 h. Scratch
  `~/dev/ssx3-work/IP1`: 4.9 GB. Disk 124.1/200 GB at build start.
- Never pushed (either repo); fork branch `ip1` local; iPhone never
  targeted (no command named its UDID).
- Gaps:
  - G1. (c1) vs (c2) undiscriminated (see above). Cheapest next test:
    delete app → reinstall same staged bundle → launch → screenshot;
    if full screen, (c1). Needs orchestrator OK (extra install+launch).
  - G2. `/tmp/ip1_measure.py` is scratch, not committed (rules); geometry
    is reproducible from the staged shots on request.
  - G3. Play-build question: this build is installed as briefed but misses
    the goal; restoring IS1's `a6718f22` (or keeping IP1 for its newer
    fork code) is the orchestrator's call.

## Recommended next action

Follow-up brief: delete + reinstall + one launch/screenshot to test (c1);
if still windowed, investigate iPadOS 26 scene size restrictions /
full-screen request APIs (one named fix + one validation run). Do not
tune `TARGETED_DEVICE_FAMILY` further — that part is proven.

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add -b ip1 ~/dev/ssx3-work/IP1/PS2Recomp fork/ssx3  # b97b241
# + 2-line CMake edit, commit ae6b137 (no push)
cp ~/dev/ssx3-work/F7/ios/{build-install.sh,ipad-probe.sh,ipad-run.sh} ~/dev/ssx3-work/IP1/ios/
# repoint W/FORK_WT/PGS/PIN->b97b241/PGSPIN->3d72467 (ENVFILE unchanged)
git clone ~/dev/parallel-gs ~/dev/ssx3-work/IP1/parallel-gs  # checkout 3d72467
git -C ~/dev/ssx3-work/IP1/parallel-gs submodule update --init --recursive
bash ~/dev/ssx3-work/IP1/ios/build-install.sh preflight configure_device build_device stage_device sign
bash ~/dev/ssx3-work/IP1/ios/build-install.sh install_ipad  # after 'iPad free'
bash local/research/I31/deploy-ios.sh ipad  # SKIP + 7 OKs
bash ~/dev/ssx3-work/IP1/ios/ipad-probe.sh  # Data C207B22D-..., bundle path match
bash ~/dev/ssx3-work/IP1/ios/ipad-run.sh ~/dev/ssx3-work/IP1/ios/run-ipad-ip1 ~/dev/ssx3-work/IP1/ios/run-ipad-env.json "1090 1810 2100"
bash local/research/I31/deploy-ios.sh ipad  # byte-identical after; STOP before install_iphone
```

## Orchestrator gate (2026-09-26)

**Stopped correctly; half the goal.** The universal family is proven (`UIDeviceFamily [1, 2]` in both plists) and the
present path fills the window it gets at exactly 16:9. The window itself is iPadOS 26's windowed-apps mode (traffic
lights visible) restoring a 590×820 pt window; `UIRequiresFullScreen` doesn't force full screen there. Folded: the
CMake change cherry-picked onto fork `ssx3` `1425844` → `1c37c41` (iOS-gated, 2 lines; runner-dir diff empty), pushed
ff. The IP1 build stays installed on the iPad (newer runtime than IS1's). Next: Brad maximizes the window by hand
once (does it resize cleanly mid-run?); if a programmatic default is still wanted, a follow-up sets the scene's
size restrictions / requests the full-screen geometry at launch (one named fix + one run).
