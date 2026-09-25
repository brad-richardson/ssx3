# I30 — iOS build with the fixed music, sound on (fork `ssx3` @ `d711506`)

Worker: Muse. Brief: `local/muse/prompts/I30.md`. No fork source edits, no push,
no upstream contact. **No iPhone launch, test or screenshot; install only.**

Headline: the first iOS build at fork `d711506` (AU8 planar tag-1 music fix
at `f2ec588`) with `PS2X_SOUND=1` in the bundled `ps2x.env` runs to the race
on both the Simulator and the iPad with the 36 kHz sound stream starting
from the bundled env alone — no launch-env sound override on either run.
The iPhone has the build installed for Brad's listening check.

| Step | Result | Receipt |
| --- | --- | --- |
| 1. Deps in `~/dev/ssx3-work/ios-deps/` | Reused read-only, **not rebuilt**: `dep-shas.txt` diff vs I29's is empty (device libavcodec `4722095f…`, device libSDL2 `d8a74d8c…`, sim libs likewise). Raylib `c1ab645c`, patch idempotent ("already applied", post SHA `df666c29…` both configures). | `dep-shas.txt`, `ffmpeg-{device,sim}-sha.txt`, `sdl2-{device,sim}-sha.txt`, `raylib-pre-sha.txt`, `{sim,device}-raylib-patch-result.txt`, `{sim,device}-raylib-post-sha.txt` |
| 2. Source | Fork worktree `~/dev/ssx3-work/I30/PS2Recomp` HEAD = remote `fork/ssx3` = `d7115063c59518fe3c7d13a79a2c9b75dc160fab` (`d711506` UP1-R1 VIF1 port on top of `f2ec588` AU8 planar fix). Runner-dir diff vs `14b1e5cb` empty. Codegen `register_functions.cpp` `8ea8ed43…` (= E54F2 canonical), ELF `1b49d05c…`, ISO `3c2f8eb1…`, each read twice, stage copies `cmp`-equal. Bundled env = I26's `ps2x.env` + `PS2X_SOUND=1` (2-line append, nothing else). | `source-pin.txt`, `codegen-sha.txt`, `elf/iso-input-sha.txt`, `{sim,device}-{elf,iso}-stage-sha.txt`, `ps2x.env`, `env-sha.txt` (`0041e09a…`), `env-i26-sha.txt` (`1f3105b9…`) |
| 3. Simulator | Release build `BUILD SUCCEEDED`; `-O3 -DNDEBUG` in cache + Xcode settings (OPT_LEVEL 3, `-DNDEBUG`), diag taps/logs OFF. Binary `09380226…`. Ad-hoc signed, installed on `7662ACD6`. One I26-FAST run (lease slot 2, 160 s): 31-press script armed, **all 31 fired** (i=0..30, tuck last), last tick **2382**. Sound stream started at 36 kHz from the bundled env. Title, menu and both race frames viewed. | `sim-{release-cache,raylib-patch-result,raylib-post-sha,source-binary-sha,flags-evidence,install}.log/txt`, `sim-run.txt`, `sim-console.log`, `sim-key-lines.txt`; frames in `~/dev/ssx3-work/I30/run-sim/` |
| 4. iPad | Same signed device build installed first try. One full run: 4 shots, ticks 260/740/1688/1968, 20 presses fired (i=0..19; the 30 s tuck at guest tick 2309 is past the 160 s wall cap, same shape as I29's 1969-tick run). Race HUD at 160 s, sound stream at 36 kHz from the bundled env. Portrait iPhone-compat window (I28's business); game cropped but correct. | `install-ipad.log`, `ipad-console.log`, `ipad-key-lines.txt`; frames in `~/dev/ssx3-work/I30/run-ipad/` |
| 5. iPhone | Signed binary `ae99bc45…` (`codesign --verify --strict` passed, identity `295EFB42…`, wildcard profile `f0793278-…`, team `LQ3V7772Q2`, same as I29). First install attempt failed (device momentarily `unavailable`, CoreDeviceError 4016 — transcribed in `iphone-install-first-attempt.txt`). Retry after it returned to `available (paired)`: one `devicectl device install app`, exit 0, same app record as I29 (`databaseUUID 785BBB17-…`, seq 4696). No process command. | `signed-binary-sha.txt`, `codesign-verify.log`, `codesign-details.txt`, `profile-check.txt`, `identity-check.txt`, `install-iphone.log`, `devices-install-iphone.txt`, `iphone-install-first-attempt.txt` |

## Sound path (no launch-env sound override on either run)

- Both consoles show `[ios-env] set PS2X_SOUND=1` from the bundled env file
  (`[ios-env] read …/ps2EntryRunner.app/ps2x.env`, no `Documents/ps2x.env`
  in either fresh container), and the only `launcher kept` key is
  `PS2X_VSYNC_RATE_LOG`. Zero `launcher kept PS2X_SOUND` lines: the bundled
  env alone turns sound on, so Brad's home-screen iPhone launch will have
  sound. (I29's G1 closed.)
- `[snd-output] stream rate=36000 channels=2 bits=16` on both, no
  `[snd-output] unable to initialize` line on either.
- Wall-minute lines: sim `underruns=1190684` then `1891776`, iPad
  `underruns=1453824` then `1826688`, `overflows=0` throughout. Expected
  direction: the host callback consumes at wall clock while the guest runs
  well under 1×, so the PCM ring starves. No audible check here (G1).

## Viewed frame tables (SHA-256 matched on two reads each)

Simulator (2622×1206, `~/dev/ssx3-work/I30/run-sim/`):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `shot-0010s.png` (tick 419) | SSX 3 title logo + EA copyright; full-width geometry, pad aligned | `94b3fcdf…b2d0b56a` |
| `shot-0035s.png` (tick 979) | Select Peak menu, Peak 1 | `cecf9dd2…81a7ada7` |
| `shot-0100s.png` (tick 1945) | Race 2ND/2, 00:00:04, 1%, EA Radio "Poor Leno – Silicon Soul Remix / Royksopp"; dark foreground + lit slope (known dark GS region) | `53394d82…6a07eec7` |
| `shot-0160s.png` (tick 2382) | Race 2ND/2, 00:00:11, 2%, 14 MPH; race advances | `bd837dbf…312578a0` |

iPad (2360×1640 device shots, game in portrait compat window,
`~/dev/ssx3-work/I30/run-ipad/`):

| Frame | Content (viewed) | SHA-256 |
| --- | --- | --- |
| `shot-0010s.png` (tick 260) | Title logo (cropped by portrait window) + EA copyright | `01c8cee8…f762068d` |
| `shot-0035s.png` (tick 740) | Select Character, Zoe's 3D model + stats | `88541f4a…9a64116e` |
| `shot-0100s.png` (tick 1688) | Rival Challenge "Happiness – Race" card (pre first-tap tick 1709) | `5ce79565…11768b2b77` |
| `shot-0160s.png` (tick 1968) | Race 2ND/2, 1%, EA Radio "Poor Leno – Silicon Soul Remix / Royksopp", slope; timer cropped | `17d6979b…cdb92d083` |

Full SHAs in `frame-sha-read1.txt` / `frame-sha-read2.txt` (identical).
In-race composition matches I29 (viewed I29's `run-sim/shot-0100s.png`
side by side: same dark foreground + lit slope + EA Radio card layout);
only the radio track differs, and both I30 runs agree with each other
("Poor Leno" twice vs I29's "Glass Danse"/"Avalanche") — the track varies
run to run, not pinned. The iPad shots show another app's registration
form behind the portrait game window (whatever was open on the iPad);
game-window content is correct.

## Rates (DIAGNOSTIC only — Simulator on M5 Pro mini, iPad hardware; not speed numbers)

- Sim: race tail ~7.2–7.6/s ≈ 0.12×.
- iPad: race tail ~4.6–5.0/s ≈ 0.08×.

## Exact commands and pins

```sh
git -C ~/dev/PS2Recomp fetch fork ssx3
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/I30/PS2Recomp d711506
# ps2x.env: cp local/research/I26/ps2x.env local/research/I30/ps2x.env + PS2X_SOUND=1
bash ~/dev/ssx3-work/I30/build-install.sh preflight configure_sim build_sim stage_sim sim_install
bash ~/dev/ssx3-work/I30/sim-run.sh      # slot 2, 160 s, VSYNC_RATE_LOG only
bash ~/dev/ssx3-work/I30/build-install.sh configure_device build_device stage_device sign install_iphone
# install_iphone failed once (device unavailable, 4016); polling showed
# available (paired); reran install_iphone -> exit 0
bash ~/dev/ssx3-work/I30/ipad-run.sh     # install ok, full run, terminated after
```

Pins: fork `d711506` (= `fork/ssx3` at fetch), raylib `c1ab645c`, SDL2/FFmpeg
prefixes bit-identical to I29 (no rebuild), I26 toolchain/env/entitlements,
identity `295EFB42…`, profile `f0793278-…`. Scripts use absolute paths.

## Budget

2 app builds (sim, device; deps not rebuilt), 1 Simulator run (160 s),
1 iPad run, 1 iPhone install (+ 1 transient-failed attempt and retry).
I30 scratch 6.9 GB, ios-deps 618 MB; global ssx3 use 65.5 / 200 GB.
Committed receipts ~1 MB. Lease slot 2 claimed/released; both slots free
of me at close (slot 1 holds another lane's `au8-race`, untouched).
Elapsed ~25 min of 60.

## Gaps

- G1: no audible verification of the 36 kHz stream on either target;
  underrun counts only. Brad's iPhone listening check is the audible test.
- G2: iPad shows the portrait iPhone-compat window; the landscape game is
  cropped left/right. That's I28, not this lane. A background app's
  registration form is visible around the game window in the iPad shots.
- G3: first iPhone install attempt failed transiently (CoreDeviceError
  4016, device briefly `unavailable`); retry succeeded. Transcription in
  `iphone-install-first-attempt.txt` (the retry overwrote the log).
- G4: `PS2X_ENABLE_IOP_RPC_TRACE=1` (fork default ON) is in both builds,
  same as I29; unhandled-RPC trace lines appear in consoles.
- G5: the EA Radio track differs between I29 and I30 runs ("Poor Leno"
  both times here); track selection is not pinned, so don't read anything
  into which song shows.

## Orchestrator gate (2026-09-24)

**A.** Read the report and commit `070f3594` (text receipts only). The bundled env alone turns sound
on (`[ios-env] set PS2X_SOUND=1`, `[snd-output] stream rate=36000`) on Simulator and iPad; iPhone:
signed `ae99bc45…` installed (retry after a transient CoreDevice unavailable), no launch. Frames
viewed by the worker; the composition matches I29 (known dark GS region). Expect gaps in Brad's
listening: the host ring underruns (~1.2–1.9 M samples/min) because the guest runs below real
time; below-full-speed audio policy is an open A-lane decision.
