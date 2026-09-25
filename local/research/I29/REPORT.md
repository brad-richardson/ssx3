# I29 — iOS rebuild with sound (fork `ssx3` @ `fb11e18`), Simulator + iPad run, iPhone install-only

Worker: Muse. Brief: `local/muse/prompts/I29.md`. No fork source edits, no push,
no upstream contact. All builds `nice -n 10` (UP1 building concurrently; no
wait-for-idle). **No iPhone launch, test or screenshot; install only.**

Headline: the first iOS build with the AU7 sound HLE runs to the race on both
the Simulator and the iPad, and the sound path starts on both
(`[snd-output] stream rate=36000 channels=2 bits=16`). The iPhone has the
build installed (Brad tests it himself). **Caveat for Brad: the bundled
`ps2x.env` does not set `PS2X_SOUND`, and both the SND guest-clock tick and
the host AudioStream are gated on `PS2X_SOUND=1`** (`ps2_snd_spike.h:2,211`,
`ps2_runtime.cpp:1116-1118`). Both validation runs enabled it via launch-env
override (same mechanism as `PS2X_VSYNC_RATE_LOG=1`). A home-screen iPhone
launch will be silent unless `PS2X_SOUND=1` is added to `Documents/ps2x.env`
via the Files app. Whether sound should default on is an E-lane call.

| Step | Result | Receipt |
| --- | --- | --- |
| 1. Deps in `~/dev/ssx3-work/ios-deps/` | FFmpeg 7.1.1 tarball SHA `73398439…a03b1` verified twice; SDL2 `release-2.32.10` = `5d24957`; raylib pinned `c1ab645c`, pre-patch source `30db3e9f…` (same as I27B/C). All four prefixes built, all archives arm64. **Library SHAs differ from I27C's** (rebuilt from the same sources): device libavcodec `4722095f…` (was `2edcc781…`), device libSDL2 `d8a74d8c…` (was `f7ce01fb…`). | `dep-shas.txt`, `ffmpeg-{device,sim}-sha.txt`, `sdl2-{device,sim}-sha.txt`, `raylib-pre-sha.txt`, `build-deps.sh`; build logs in `ios-deps/logs/` (scratch) |
| 2. Source | Fork worktree `~/dev/ssx3-work/I29/PS2Recomp` HEAD = remote `fork/ssx3` = `fb11e182310555c65201635f8d6c7fe8e170de74`. Runner-dir diff vs `14b1e5cb` empty. Codegen `register_functions.cpp` `8ea8ed43…` (= E54F2 canonical), ELF `1b49d05c…`, ISO `3c2f8eb1…`, each read twice, stage copies `cmp`-equal. | `source-pin.txt`, `codegen-sha.txt`, `elf/iso-input-sha.txt`, `{sim,device}-{elf,iso}-stage-sha.txt` |
| 3. Simulator | Release build `BUILD SUCCEEDED`; `-O3 -DNDEBUG` in cache + Xcode settings (OPT_LEVEL 3, `-DNDEBUG`), diag taps/logs OFF. Binary `635742b0…`. Ad-hoc signed, installed on `7662ACD6`. One I26-FAST run (lease slot 2, 161 s): 31-press script armed, 28 presses fired, last tick **2216**. Sound stream started at 36 kHz (no resample fallback). Title, menu and both race frames viewed. | `sim-{release-cache,raylib-patch-result,raylib-post-sha,source-binary-sha,flags-evidence,install}.log/txt`, `sim-run.txt`, `sim-console.log`, `sim-key-lines.txt`; frames in `~/dev/ssx3-work/I29/run-sim/` |
| 4. iPad | Same signed device build installed. First launch refused (device Locked — observed, see Gaps). Retry probe launched (tick 1246, sound started), terminated. Fresh full run: 4 shots, ticks 349/738/1688/1969, race HUD at 160 s. Portrait iPhone-compat window 820×410 pt, render 1640×820 (I28's business); game cropped but correct. | `install-ipad.log`, `ipad-console.log`, `ipad-probe-console.log`, `ipad-key-lines.txt`; frames in `~/dev/ssx3-work/I29/run-ipad/` |
| 5. iPhone | Signed binary `853007c0…` (`codesign --verify --strict` passed, identity `295EFB42…`, wildcard profile `f0793278-…`, team `LQ3V7772Q2`, valid to 2027-09-17, lists iPhone + iPad). One `devicectl device install app`, exit 0, same app record as I27C (`databaseUUID 785BBB17-…`, seq 4680). No process command. | `signed-binary-sha.txt`, `codesign-verify.log`, `codesign-details.txt`, `profile-check.txt`, `identity-check.txt`, `install-iphone.log`, `devices-install-iphone.txt` |

## Sound path (both runs used launch-env `PS2X_SOUND=1`)

- `[ios-env] launcher kept PS2X_SOUND` then `[snd-output] stream rate=36000
  channels=2 bits=16` on both Simulator and iPad hardware: the guest-clock
  SND tick and the host 36 kHz stereo 16-bit stream start. No
  `[snd-output] unable to initialize` line on either.
- Wall-minute lines report large `underruns=` with `overflows=0` on both
  (e.g. sim 1.2M then 2.0M; iPad 1.5M then 1.8M). Expected direction: the
  host callback consumes at wall clock while the guest runs well under 1×,
  so the PCM ring starves. No audible check was possible (Simulator has no
  listener here; iPad run unattended).
- There is no "SND clock start" log line in the source; stream-rate +
  underrun lines are the observables.

## Viewed frame tables (SHA-256 matched on two reads each)

Simulator (2622×1206, `~/dev/ssx3-work/I29/run-sim/`):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `shot-0010s.png` (tick 270) | SSX 3 title logo + EA copyright; full-width geometry, pad aligned | `34ec3167…f4ff1ae` |
| `shot-0035s.png` (tick 956) | Select Peak menu, Peak 1 | `d4707398…2760d12d` |
| `shot-0100s.png` (tick 1861) | Race 00:00:02 / 0%, EA Radio "Glass Danse – Oakenfold Remix / The Faint", slope + sky | `0d685bda…7b7c8bc2` |
| `shot-0160s.png` (tick 2216) | Race 00:00:08 / 1%, 15 MPH, rider visible; race advances | `791b5e68…51330a9f2` |

iPad (2360×1640 device shots, game in portrait compat window,
`~/dev/ssx3-work/I29/run-ipad/`):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `shot-0010s.png` (tick 349) | Title logo (cropped by portrait window) | `e6d0c54a…06b1afb4d` |
| `shot-0035s.png` (tick 738) | Select Character, Zoe's 3D model | `822d967e…2e2a02cad` |
| `shot-0100s.png` (tick 1688) | Rival Challenge "Happiness – Race" card (pre first-tap tick 1709) | `f3a88256…378455257` |
| `shot-0160s.png` (tick 1969) | Race 2ND/2, 1%, EA Radio "Avalanche / Powerplant", slope; timer cropped | `6fcf534c…b109958a` |

Guest rendering matches I27B (full-width geometry on sim, known dark GS
region in-race, guest font detail unchanged). Full SHAs in
`frame-sha-read2.txt` (second reads; first reads in run output above).

## Rates (DIAGNOSTIC only — Simulator on M5 Pro mini, iPad hardware; not speed numbers)

- Sim: menus ~18–54 vsync/s; race tail ~5.8–6.0/s ≈ 0.10×.
- iPad: title ~52/s early; race tail ~4.6–5.2/s ≈ 0.08×.

## Exact commands and pins

```sh
git -C ~/dev/PS2Recomp fetch fork ssx3
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/I29/PS2Recomp fb11e18
bash ~/dev/ssx3-work/I29/build-deps.sh   # ffmpeg+SDL2 x2 SDKs, nice'd
bash ~/dev/ssx3-work/I29/build-install.sh preflight configure_sim build_sim stage_sim sim_install
bash ~/dev/ssx3-work/I29/sim-run.sh      # slot 2, 161 s, PS2X_SOUND=1 + PS2X_VSYNC_RATE_LOG=1
bash ~/dev/ssx3-work/I29/build-install.sh configure_device build_device stage_device sign install_iphone
bash ~/dev/ssx3-work/I29/ipad-run.sh     # install ok, launch refused (Locked)
# retry probe launched -> terminated; then:
bash ~/dev/ssx3-work/I29/ipad-run.sh     # full run, 4 shots, terminated after
```

Pins: fork `fb11e18`, raylib `c1ab645c`, SDL2 `5d24957`, FFmpeg tarball
`73398439…a03b1`, I26 toolchain/env/entitlements, identity `295EFB42…`,
profile `f0793278-…`. Scripts use absolute paths; device builds
`configure` reuses the persistent raylib clone (patch hook reports
"already applied" — idempotent, post-patch SHA `df666c29…` both times).

## Budget

2 app builds (sim, device; deps not counted), 1 Simulator run (161 s),
1 iPad validation run + 1 short terminated probe + 1 refused launch,
1 iPhone install. I29 scratch 6.9 GB, ios-deps 618 MB; global ssx3 use
56.9 / 200 GB. Committed receipts 1.1 MB. Lease slot 2 claimed/released;
both slots free of me at close. Elapsed ~25 min of 120.

## Gaps

- G1 (for Brad): home-screen iPhone launches are silent until
  `PS2X_SOUND=1` reaches the app (bundled env lacks it; use
  `Documents/ps2x.env` via Files). Recommend E decide the default.
- G2: no audible verification of the 36 kHz stream on either target;
  underrun counts only. Needs a listening check (iPad run with audio
  capture, or Brad on the phone).
- G3: iPad shows the portrait iPhone-compat window (820×410 pt); the
  landscape game is cropped left/right. That's I28, not this lane.
- G4: first iPad launch refused — `FBSOpenApplicationErrorDomain error 7`,
  "Unable to launch … because the device was not, or could not be,
  unlocked". Observed in run output; its 1 KB console was overwritten by
  the successful rerun's console, so no separate file. Recovered: retry
  probe + full run both launched (device had been unlocked meanwhile).
- G5: `PS2X_ENABLE_IOP_RPC_TRACE=1` (fork default ON) is in both builds,
  same as I27C; unhandled-RPC trace lines appear in consoles.
