# iOS development milestone

This app embeds the GXBE69 revision 0 AOT module as a static archive and uses
the Dolphin-derived Metal/runtime implementation. It includes two virtual sticks
(left: main stick for turning, crouching and braking; right: the D-pad, which
is what the game reads for spins and flips), A/B/X/Y, L/R, Z, and Start.
The C-stick (board press) has no touch control yet. No physical controller is required for basic play.
Menu pauses the runtime and saves your place. Resume continues immediately;
backgrounding the app also pauses and saves. Returning after backgrounding or
an audio interruption opens the menu and waits for Resume. Resume reactivates
audio and reconciles the actual runtime state; lifecycle state is independent
of pause-duration accounting. Relaunch restores that checkpoint
when the game files and app build still match. Full Reset discards the checkpoint
and starts a new runtime with the current files; it preserves memory-card saves.
Use Full Reset after copying new assets during development. The game's own
Restart option may retain cached assets and is not a reliable asset reload.

Faster cold launches are enabled by default, including Full Reset.
Turn **Fast start** off in Menu to restore ordinary startup; this saved
preference applies to the next cold boot or Full Reset. Compatible checkpoint
restores still take precedence. It skips
startup movies, waits for the initialized title screen, and advances once
through normal START input to the main menu. Required game/UI loading remains.
`mobile_gamecube.py launch --debug-main-menu` opts in for that process;
`--normal-boot` overrides a saved preference for ordinary-boot coverage. Neither
launch override changes the saved preference. Native and repeated Simulator testing reached the real
menu in about 20 seconds after guest execution began. Installed build 113c9b20
includes the active-input readiness fix; the latest phone run reaches the menu
at 20.61 seconds and the user confirms the shortcut works. Saved toggle/restore
combinations still need phone validation. See [startup evidence and reproduction](../../docs/research/startup-shortcut.md).

For state-based startup automation, use `--debug-main-menu --sequence
native/ios/main-menu-smoke.json`. Its 20-second clock begins at actual main-menu
readiness; it does not repeat the old timed START/A startup inputs. Metrics
retain the runtime clock and separately record `sequenceSeconds`; lifecycle
logs mark `sequence_started`. Smoothing scheduled for a state-anchored sequence
uses the same sequence clock. The usual overall startup deadline remains.

The pause menu shows the app version, short build identity, and binary build
date/time in the device's local timezone. It also shows the active course build
and archive build date. CMake stamps `build-info.json` after linking; the world
deployment command writes `Documents/course-build.json` outside the game's
asset tree. At runtime creation the app verifies that label against the actual
world SHA256 and snapshots it with the loaded session. A stale/missing label
falls back to the world hash; copying new assets during play cannot relabel
the old in-memory course. Save-status updates retain the version information.

Build and signing commands keep their latest receipts in the build directory
and archive exact copies under its `receipts/` directory, named by content hash.
Use the printed archive path for delivery records: later builds replace the
working receipts. Signing receipts include the app build identity and the
signed executable hash. These local records contain provisioning/device details
and stay outside version control.

The menu also offers an opt-in native smoothing trial, lasting up to 35 seconds.
It can end early if extra rendering cannot keep up, and always drains an injected
draw before pausing/saving. Ordinary rendering remains the default. This is a
geometry-interpolation experiment with a visual-delay tradeoff, not a verified
latency improvement. Device reports have shown short stretches of actual
120 Hz presentation; sustaining that pacing remains experimental.
See the [prototype findings](../../docs/research/120hz-native-interpolation.md)
for performance limits, ownership rules and reproduction.

The pause menu has direct **Half / 75% / Full / Match** output choices and
**1× / 2×** internal detail choices. It stays open while either setting changes;
Resume returns to play. Initial defaults are **Half output + 2× detail**, the
user's preferred clarity/performance compromise. Subsequent successful menu
changes are saved independently across launches and Full Reset. Explicit launch
overrides affect only that process and never overwrite either saved preference.
On the iPhone 16 Pro Max, full is 2868 × 1320, 75% is 2151 × 990, and half is
1434 × 660. Output and internal detail remain independent; touch controls and
UIKit text keep their normal screen resolution. Half uses one quarter of Full's
output pixels and about 46% fewer than the measured Match/2× output. Match is
not an automatic performance optimum. These choices do not establish sustained
smoothing performance.

The resolution labels show the visible picture and the complete output including
bars, separately from the selected internal detail. After a paused detail change,
new measured dimensions appear after Resume; the UI does not infer them from
EFB allocation size. Resolution controls are unavailable while a smoothing draw
drains or a checkpoint is being written. A Dolphin CPU/FIFO guard synchronizes
the change; the Metal renderer rebuilds its backbuffer after resuming.

Match internal uses the visible, aspect-correct picture reported after rendering,
not the whole allocated EFB. For the observed 2× gameplay picture (1556 × 896),
it requests a 1947 × 896 drawable with side bars. It preserves picture shape;
iOS still scales that drawable onto the physical screen. The app waits for two
consistent source frames at the selected internal detail before matching.
Automatic updates use the same CPU/FIFO guard outside waiting/active smoothing
trials, checkpoints and lifecycle transitions; output stays fixed throughout
a trial. If detail and Match change together, Try smoothing resumes first and
waits for the measured output to settle before requesting the trial; another
pause cancels that pending request. The menu labels a pending match as updating
on resume. The Metal backend
honors exact integer drawable dimensions on iOS, avoiding float-scale rounding.
Outputs larger than native screen size are capped and reported in telemetry.

**1× / 2×** changes the GameCube rendering resolution independently of output
size. The initial default is 2×, with subsequent menu choices remembered. The
allocated EFB is 640 × 528 at 1× (337,920 pixels) or 1280 × 1056 at 2×
(1,351,680 pixels), four times the pixels. These allocation dimensions differ
from the visible picture. The same paused, checkpoint-complete,
smoothing-drained gate applies. The app changes Dolphin's
configuration under its CPU/FIFO guard; the renderer recreates the EFB and
updates viewport/scissor state at its next frame config check after resuming.
The pinned savestate loader supports restoring differently sized EFB images by
resampling into the current framebuffer; phone checkpoint/relaunch behavior
across a detail change still needs device validation.

2× can improve geometry edges and scene detail but increases GPU rasterization,
memory bandwidth, and framebuffer memory use. It does not reduce guest CPU
work or establish sustained 120 Hz performance. Half output does not cancel
the cost of a 2× internal framebuffer. Keep internal detail at 1× for the
default Full/Half pacing comparison; the analyzer's baseline policy remains
640 × 528. `mobile_pacing_check.py --internal-scale 2` explicitly expects
1280 × 1056 with unchanged speed, audio and duration gates. Compare internal
detail separately and exclude resize/startup frames.

Launch metadata's `renderScale` records the selected initial integer. Launch,
metrics, and lifecycle rows also record `requestedInternalScale`; `efbWidth`,
`efbHeight`, and `efbSampleHostSeconds` describe the latest actual framebuffer
sample taken on the renderer thread (null before its first frame). The
`internal_resolution_requested`, `internal_resolution_configured`, and
`internal_resolution_rejected` events use the usual monotonic `host_seconds`
clock. A request/rejection includes `targetInternalScale`. Configured means the
setting was changed: the sampled EFB size may remain old until rendering resumes.

For a phone comparison, alternate Full / Half / Full on the same riding
section, including ordinary riding before each smoothing trial. Keep the
same controller input, course, camera, and device conditions as closely as
possible. Menu transitions, saves and resize startup do not count as steady
gameplay. The smoothing deadline and speed fallback apply at both resolutions.

For reproducible launches, `mobile_gamecube.py launch --output-scale half`
(with the usual device options) selects half output for that process. It can
be combined with `--sequence`; `--output-scale full` is the explicit baseline.
`--output-scale three-quarter` selects 75% output; `--output-scale match-internal`
selects automatic source matching. Metal's BGRA drawable path
uses integer pixel dimensions and imposes no even-width requirement here.
This option does not persist a preference; a normal app launch uses the saved
choice, initially Half. Always specify both output and internal detail for
controlled comparisons.
`--internal-scale 2` selects 2× internal detail for a launch, or use
`--internal-scale 1` for the explicit baseline. It accepts only `1` or `2`, is
launch-only, and can be combined with any output mode and with `--sequence`.
Invalid values or use on another command are rejected before device changes.
With a bounded `--sequence`, `--smoothing-at 155` requests one trial at that
active test time, using the same riding-state checks, 35-second cap and speed
fallback as the menu. The test must leave at least 40 seconds after the request;
the option is rejected before copying inputs otherwise. It never restarts an
already pending/running trial. Automated sessions skip player checkpoints.
Retain the sequence and compare actual riding state and presentations: equal
wall-timed inputs alone do not establish identical game trajectories.

If Simulator RemoteIO aborts in `AURemoteIO::Start` with an audio-service RPC
timeout, a bounded graphics check can use `--simulator-null-audio`:

```sh
python3 tools/mobile_gamecube.py launch --simulator --device SIMULATOR_UUID \
  --sequence native/ios/snow-jam-smoke.json --normal-boot --output-scale half \
  --internal-scale 1 --smoothing-at 155 --simulator-null-audio
```

This option requires `launch`, `--simulator`, and a valid bounded `--sequence`;
invalid combinations are rejected before device or container changes. The app
honors its `-ssxNullAudio` flag only in a Simulator build with `-ssxAutoTest`.
It selects Dolphin's `No Audio Output` backend and skips AVAudioSession setup,
activation and interruption handling for that diagnostic. Normal Simulator
launches and all phone builds continue using CoreAudio. `launch.json` records
`audioEnabled: false` and `audioBackend: "No Audio Output"` for the diagnostic;
it cannot establish audio health or real iPhone presentation performance.

Snapshots live in `Documents/Resume`, with a checksum and an atomically replaced
manifest. Incomplete snapshots leave the previous checkpoint intact; changed
assets, changed app builds, and damaged snapshots fall back to a normal boot.
Automated test sessions neither save nor restore player checkpoints. A cold
restore still initializes the runtime and verifies files before loading the
snapshot; it bypasses the game's splash screens and menu navigation.

The generated game code, assets, signing profiles, and build products are
private local inputs under ignored `local/` or the existing games share.
The app expects the extracted disc at `Documents/Game/{sys,files}`. Its own
configuration and saves live at `Documents/User`; reports live in
`Documents/Reports`. Reinstalling updates this app in place. Provisioning copies
game files and does not remove unrelated files or saves.

Build and deploy from the repository root:

```sh
python3 tools/mobile_gamecube.py build --jobs 4
python3 tools/mobile_gamecube.py sign --device 'YOUR PAIRED IPHONE'
python3 tools/mobile_gamecube.py install --device 'YOUR PAIRED IPHONE'
python3 tools/mobile_gamecube.py provision --device 'YOUR PAIRED IPHONE'
python3 tools/mobile_gamecube.py launch --device 'YOUR PAIRED IPHONE'
```

A new course build only changes the world archive, so after the first
provisioning push just that file (about 100 MB, a few seconds over USB or
Wi-Fi; it works while the phone is locked):

```sh
python3 tools/mobile_gamecube.py world --device 'YOUR PAIRED IPHONE' \
  --world local/builds/gc-gari-013/BAM.BIG
```

Signing selects an existing, unexpired Apple Development identity/profile that
matches this app and the selected device. It does not change another app's
identity or request JIT entitlements. If no matching profile exists, Xcode
provisioning is a separate prerequisite. Device access may require an unlock.

For a bounded automated test:

```sh
python3 tools/mobile_gamecube.py launch --device 'YOUR PAIRED IPHONE' \
  --sequence native/ios/snow-jam-smoke.json
python3 tools/mobile_gamecube.py collect --device 'YOUR PAIRED IPHONE'
```

The test sends the same virtual-controller commands used by the touch controls.
It requests game-frame captures every 15 seconds and records FPS, vertical
refresh, simulation speed, frame-event intervals, memory footprint, thermal
state, and empty DMA audio-queue dequeues. Frame-event intervals are not GPU
timestamps. Audio queue starvation is not a count of audible glitches; exclude
startup, loads, and pauses when evaluating it. Menu screenshots must confirm
that a timed sequence reached gameplay before its samples count as a course
benchmark. Simulator performance does not establish device performance.

Diagnostic report schema 2 adds a build identity and shared `host_seconds`
clock (the same uptime clock used by Metal and native trial schedule events).
The existing `seconds` field still excludes app pauses. Use host time when
comparing a smoothing cutoff, audio starvation, lifecycle events and presentation.
Launch metadata, metrics and lifecycle events also record `outputScale`
(the fixed fraction or measured Match fraction), `screenScale`, requested `outputWidth`/`outputHeight` and the
layer's actual `drawableWidth`/`drawableHeight`. `output_resolution_requested`
and `output_resolution_applied` mark the menu change. The latter means the
synchronized resize was queued; confirm actual submitted dimensions in
`present.csv` after resuming before classifying the new window. Internal EFB
dimensions remain in the existing metrics fields.

- `present.csv` records drawable acquire duration, submission ID, presentation
  callback time and the drawable's actual `presentedTime`, plus start/end/error
  for the final Metal command buffer. GPU completion alone is not display
  completion; that buffer's duration is not total GPU work for the frame.
  Zero/missing timestamps remain unknown. The simulator SDK has no presentation
  callback API, so its events explicitly say `display_unavailable`.
  The observer buffers up to 8,192 events and drains once per second, including
  while paused. Overflow is counted. Late callbacks retain their original
  report across runtime reset. The iOS build instruments local copies of the
  pinned Metal and savestate sources; no graphics settings change.
- `lifecycle.jsonl` records app/audio transitions, trial requests/cancellation,
  checkpoint request/CPU capture/compression-writer/file-ready/commit stages,
  failed stages, filesystem error codes, temporary-file sizes on failure,
  background-task expiration and long main-timer gaps. Low-level `errno` is
  best-effort; the named failing stage and Foundation underlying error are
  the primary evidence. A successful file rename alone is not save validation.
- Once per emulated second, `recomp_sample` records existing native dispatch,
  interpreter fallback, exception and host-HLE counters on the CPU thread.
  Counts have different units and do not measure CPU time in each path.
- Once per app metric interval, `workload` aggregates renderer frame-event
  draw calls, primitives, geometry upload bytes and EFB peeks/pokes, with latest
  shader/texture creation and upload counters. These are captured on the
  renderer thread; the UI receives an aggregate. Shader creation counts are
  not compilation durations and may reset with a cache reload. The existing
  speed estimate excluding intentional throttle sleep is also recorded as
  `maxSpeedExcludingThrottle`; it is not a guaranteed achievable FPS.

Summarize an explicit host-clock window from `native-trial.jsonl` or
`lifecycle.jsonl` with:

```sh
python3 tools/mobile_report.py local/reports/mobile/CAPTURE/Reports/SESSION \
  --clock host --start HOST_START --end HOST_END
```

The summary selects displays by actual presentation time even when callbacks
arrive late, reports pacing and acquire/GPU costs, and includes checkpoint
stage histories. Collection can leave callbacks in flight; missing callbacks
are not automatically dropped frames. Positive presentation timestamps still
do not prove that each frame contains distinct interpolated motion.

On iOS, the runtime uses interpreter CPU fallback, disables DSP JIT, forces
the portable vertex loader, and aborts any call to the runtime's executable
memory allocator. The same allocator guard can run on macOS through
`SSX3_NO_EXECUTABLE_MEMORY=1`. Metal shader compilation remains handled by the
system graphics driver. Successful compilation alone is not runtime acceptance.

## Controls

The GameCube build's own Controller Settings screen (captured 2026-09-11 in the
native Mac build) defines two presets. Default: main stick and D-pad turn,
crouch/brake, spin/flip; A jump; B boost/tweak; X hand plant; Y reset; Z grab
board; L and R grab/block/punch; C-stick board press; Start pause. Pro swaps Z
to reset, Y to hand plant, and X to grab board. The touch overlay and the game's prompt icons both use Xbox letters at Xbox
positions: `tools/patch_ui_glyphs.py` repaints the GameCube B/X/Y icons in
`data/ui/{fe_1,ov_1,gl_1}.gsh` as a blue X, red B and yellow Y, so a prompt for
boost reads X (left) and hand plant reads B (right).

GameCube grabs come from three inputs, PS2 grabs from four shoulders. The
verified tables are in `GrabMap.h`; `tests/test_native_grab_map.py` checks them.

| GameCube input | Grab |
| --- | --- |
| L | Mute |
| R | Method |
| Z | Stalefish |
| L+R | Indy |
| L+Z | Nosegrab |
| R+Z | Tailgrab |
| L+R+Z | Shifty |

A physical controller (GameController framework, so DualSense, Xbox, Backbone,
and MFi pads) uses PS2 positions: cross/A jump, square/X boost and tweak,
circle/B hand plant, triangle/Y reset, Options reset, Menu start, left stick
main and also the D-pad (PS2 feel: one stick turns and spins), right stick
C-stick, D-pad D-pad. L1/L2/R1/R2 form the PS2 grab mask
(Method/Mute/Stalefish/Indy) and are translated to the GameCube combo with the
same name: Nosegrab and Tailgrab and Shifty match exactly; the eight PS2 grabs
with no GameCube input (Melancholy, Swiss Cheese, Stiffy, Lein, Stalemasky,
Seatbelt, Chicken Salad, Spaghetti) fall back to the union of their
single-button grabs. Restoring those eight needs a DOL-level patch of the grab
lookup, not an input remap. The overlay dims to 25% while a pad is attached.
The physical-controller path compiles and is covered by the header test, but
has not yet been exercised with a real pad.

## Upstream provenance

Apple platform support is adapted from
[SunPad ec20f8d](https://github.com/chrissotraidis/sunpad/tree/ec20f8d843fa40a484c7455cacb90b19884867ec):
its Dolphin `0001-sunpad-ios-runtime.patch` supplies the iOS platform, Metal
guards, RemoteIO audio, and unavailable-service stubs. Its ModernGekko CMake
changes supply iOS platform selection. The app follows the host's Metal-layer,
runtime-thread, and controller-pipe integration. Upstream copyright and GPL
notices are retained in the platform patch. Sunshine-specific addresses,
cheats, widescreen fixes, and scheduler settings are not used by SSX.

The complete SSX changes are recorded in `native/patches/*-platform.patch`,
against the exact dependency revisions in `native/dependencies.json`. Earlier
observability/metrics patches remain as historical evidence; bootstrap applies
the combined platform snapshots.
