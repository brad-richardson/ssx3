# IP1 — iPad full screen: universal device family (muse, 1.5 h)

## Goal
Brad (09-26): the iPad build runs in "the weird iPhone size box". Make it run full screen on the iPad
with the picture scaled by the display rule (AGENTS.md: 16:9 anamorphic, aspect-preserving, fill as much
as possible, bars never stretch). Then install it on Brad's iPad as his new play build (fork `ssx3` tip
also brings VR4's SIMD FMAC and the rest since F7's `a5e5940`).

## Facts
- The iOS app is a CMake Xcode-generator bundle (`ps2xRuntime/CMakeLists.txt`, `if(PS2X_IS_IOS)` block
  ~line 853; plist template `ps2xRuntime/ios/Info.plist`: landscape only, `UILaunchScreen`,
  `UIRequiresFullScreen`). Nothing sets `TARGETED_DEVICE_FAMILY`; Xcode's default is `1` (iPhone), so
  iPadOS runs the app in iPhone compatibility mode. That's the box.
- The present path already letterboxes by window size: `ps2x::present::presentRect(...)` with
  `PS2X_ASPECT` (`ps2xRuntime/src/lib/ps2_runtime.cpp` ~4456/4597). With a real iPad window it should fill
  the width at 16:9 with bars top/bottom (iPad Air 11" M2 is 2360×1640, ≈ 1.44:1).
- Recipe: F7 Part 2 (`local/research/F7/REPORT.md` §Part 2 + commands ~line 276): 
  `~/dev/ssx3-work/F7/ios/build-install.sh`, `ipad-probe.sh`, `ipad-run.sh`, `local/research/I31/deploy-ios.sh`.

## Hypothesis and observable
H: adding `XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2"` to the iOS target makes the built bundle's
`UIDeviceFamily` = `[1, 2]`, and iPadOS gives the app the full 2360×1640 window.
Alternatives: (a) the plist template overrides/omits the key → built `Info.plist` lacks `UIDeviceFamily`
(check with `plutil -p`); (b) the window is full screen but the game picture is still sized from a stale
iPhone-sized drawable → screenshot full size but picture small/centered. Observable: `plutil -p` on the
built app, plus the iPad screenshot's picture rectangle (measure it: width, height, ratio 1.778 ± 0.01,
centered, touching the left/right edges).

## Steps
1. Fresh fork worktree `~/dev/ssx3-work/IP1/PS2Recomp` from `fork/ssx3` (`b97b241` or newer; record it).
   Add in the `if(PS2X_IS_IOS)` block, with a one-line `# IP1:` comment in the style around it:
   `set_target_properties(ps2EntryRunner PROPERTIES XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2")`.
   Commit `[IP1] iOS: universal device family so iPadOS runs full screen` (plain commit on a local branch
   `ip1`, no push; the orchestrator pushes after the gate). Runner-dir check must be empty.
2. Copy F7's `ios/` scripts to `~/dev/ssx3-work/IP1/ios/`; repoint `W`, `FORK_WT`, `PIN` (your commit's
   parent on `ssx3`), `PGS` → a clone at paraLLEl-GS `ssx3` `3d72467` (Granite `166ba21a`), `LOGS`.
   Keep `ENVFILE=local/research/F7/ps2x.env` (Brad's current bundled env) unchanged.
3. `preflight configure_device build_device stage_device sign` (device only; no sim build, per F7).
   Receipt: `plutil -p` of the built and the staged `Info.plist` (`UIDeviceFamily`), binary SHA ×2.
4. **Stop and wait for the orchestrator's "iPad free" message** (IS1 is using the iPad now). Do not touch
   the iPad before it.
5. `install_ipad`, `deploy-ios.sh ipad`, `ipad-probe.sh`, then one `ipad-run.sh` with shots at
   `1090 1810 2100`. Look at every shot: full-screen window? picture rect and ratio? virtual pad
   placement (note any control over the picture)? Force-quit the app after. Brad's `mc0` byte-identical
   after (deploy re-run: 7 OKs). Leave the build installed (it's his play build now).
6. No iPhone install (stop before `install_iphone`; the orchestrator decides).

## Budgets / rules
1 device build (+1 rebuild only if alternative (a) or (b) needs one named fix), 1 iPad install,
≤ 2 iPad launches, 1.5 h. Write only under `~/dev/ssx3-work/IP1/`, the fork worktree, and
`local/research/IP1/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/IP1/REPORT.md`: pins (fork commit, PGS, env SHA, binary SHA ×2), `UIDeviceFamily`
receipts, the shot table (size, picture rect, ratio, pad notes), `mc0` check, exact commands, gaps.
Commit `[IP1] …` with `git add -f local/research/IP1/REPORT.md` (+ small text receipts, and this brief is
already committed), trailer `Orchestrated-By: Muse Code`, no push.
