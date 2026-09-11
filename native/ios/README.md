# iOS development milestone

This app embeds the GXBE69 revision 0 AOT module as a static archive and uses
the Dolphin-derived Metal/runtime implementation. It includes two virtual sticks
(left: main stick for turning, crouching and braking; right: the D-pad, which
is what the game reads for spins and flips), A/B/X/Y, L/R, Z, and Start.
The C-stick (board press) has no touch control yet. No physical controller is required for basic play.
Stop shuts the runtime down; relaunch the app to start another session.

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
