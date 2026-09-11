# GameCube native prototype

This is the stock SSX 3 foundation for standalone Tricky courses with SSX 3
handling. It uses ahead-of-time PowerPC translation and a Dolphin-derived
hardware runtime. macOS runs the stock game; the new [iOS development app](ios/README.md)
embeds the translated module and adds on-screen controls. Android remains a
separate milestone.

As of 2026-09-10, stock SSX 3 boots through its menus and runs the Snow Jam race
with Metal rendering and CPU JIT fallback disabled. Captures show textured
terrain/scenery, opponents, the rider, and the HUD; pipe input has been used for
menu navigation, steering, and jumping. Restart returned to the starting
briefing. This is a short smoke test, not a full
gameplay/physics, audio, save, or mobile acceptance pass. See `validation.json`
for the recorded run evidence and remaining checks.

## Reproduce

Pins are in `dependencies.json`. These are the matched upstream revisions from
SunPad's bootstrap script inspected on 2026-09-10, with our small patches listed
below. No SunPad game-specific patches are applied. Use Apple's Clang on this
Mac: the Homebrew LLVM toolchain selected an incompatible `llvm-ranlib` command.
Homebrew libraries linked by the runtime make this a host-local build, even
though its nominal deployment target is macOS 14; it is not a distributable app.

Run from the repository root with Python 3.11+, Git, CMake, and Ninja installed:

```sh
python3 tools/native_gamecube.py bootstrap
python3 tools/native_gamecube.py configure
python3 tools/native_gamecube.py build --jobs 4
python3 tools/native_gamecube.py module --jobs 4
python3 tools/native_gamecube.py run --profile stock --seconds 60
```

The locally installed Ninja release URL and archive checksum are pinned. A
system Ninja also works. Bootstrap fetches the submodules used by these Metal
builds, leaving the large unused platform dependencies out.

The DOL defaults to `local/source/gamecube/ssx3/sys/main.dol`. Both compilation
and launch verify its SHA-256 against GXBE69 revision 0. The extracted disc root
defaults to `/Volumes/share-1/brad/games/ssx3-workbench/native/GXBE69`; override
with `run --game PATH`. The original RVZ remains unchanged. Extraction was:

```sh
local/tooling/dtk disc extract \
  '/Volumes/share-1/brad/games/gamecube/SSX 3 (USA).rvz' \
  '/Volumes/share-1/brad/games/ssx3-workbench/native/GXBE69'
```

Keep dependencies in ignored `third_party/`, game files and generated code in
ignored `local/` or on the share. Do not add generated code or disc data to Git.
The module command resumes compilation after a failure, checks its generation
identity, and records an independent manifest with the actual pins and hashes.
We bypass `moderngekko-port build` because this revision hardcodes stale revision
labels in its manifest and uses all CPU cores for compilation.

## Runtime evidence

`run` uses isolated profiles at `local/native/profiles/NAME`. New profiles use
single-threaded CPU/GPU scheduling, DSP HLE, and disabled DSP JIT. CPU fallback
defaults to the interpreter through our `STATICRECOMP_NO_JIT=1` patch. The runner
also sets `SSX3_NO_EXECUTABLE_MEMORY=1`, forces the portable vertex loader, and
aborts runtime executable allocations. For an
explicit desktop comparison only, `--jit-fallback` enables the upstream CPU JIT.
No interpreter-only module-loading bypass is passed: a rejected AOT module
must fail the launch.

Each run writes a log, launch receipt, and sampled dispatch CSV under
`local/reports/native-runs/`. GUI runs request a game-frame screenshot every
15 sampling intervals, saved inside the isolated profile's `ScreenShots` folder.
`--headless` selects Null video/audio. `--seconds` bounds the process, requesting
graceful shutdown first so counters are emitted. A forced kill loses shutdown
counters and is not a passing run.

Interpret the logs carefully:

- `native` counts generated block dispatches; `fallback` counts interpreted
  instructions. These units differ, so their ratio is **not** native coverage.
- `fallback_jit_runs` counts entries into JIT fallback, not instructions or time.
- `hook_fb` counts instructions delegated by generated code to runtime helpers.
- `smc_failed` reports chunks whose runtime bytes differ from the generated
  module. The 115 static warning ranges are a separate heuristic report.
- Dispatch/fallback site samples are taken every 4,096 events, so periodic code
  can bias the ranking. They are leads, not a complete profile.
- `ssx3-metrics` records FPS, vertical refresh rate, and simulation speed. Its
  `sample` field is the sampling-loop index, not precise elapsed time.

The September 10 validation predates the executable-allocation guard. Additional
guarded Mac runs reached Snow Jam with zero CPU JIT entries and clean shutdown.
The iOS build statically links its module, uses Metal and RemoteIO audio, and
disables CPU/DSP/vertex-loader JIT. Physical-device gameplay, lifecycle, audio,
and performance still require a device acceptance pass.

Patches:

- `recompcore-platform.patch`: interpreter fallback, dispatch diagnostics,
  executable-allocation guard, portable vertex loading, and Apple platform support.
- `moderngekko-platform.patch`: runtime metrics, captures, controller integration,
  and the iOS render surface.

Bootstrap applies these combined patches. The earlier observability/metrics
patch files are retained for historical reference, not applied separately.

For automated menu/course checks, launch a fresh profile with `--pipe-controller`.
This maps one GameCube controller to the profile's named pipe and permits input
while the test window is in the background. It preserves existing non-test
controller mappings by refusing to replace them. Send bounded inputs with:

```sh
python3 tools/gamecube_input.py --profile course-nojit tap START
python3 tools/gamecube_input.py --profile course-nojit tap A
python3 tools/gamecube_input.py --profile course-nojit --hold 1 stick 0.75 0.5
```

Inputs are recorded in that profile's `test-input.jsonl`. Button presses release
automatically; stick commands return to center. Without pipe mode the upstream
keyboard defaults use Return for Start, X for A, Z for B, arrow keys for the main
stick, and Q/W for the shoulder triggers.

## Targeted reverse engineering

```sh
python3 tools/gamecube_research.py \
  --dol local/source/gamecube/ssx3/sys/main.dol \
  --dol-info local/reports/gamecube/ssx3-dol-info.txt \
  --smc local/native/ssx3-module/codegen/generated/generated_smc.txt \
  --output local/reports/gamecube/ssx3-research-seeds.json
python3 -m unittest tests/test_gamecube_research.py
```

The report provides string addresses, conservative address-construction
candidates, data-pointer candidates, direct calls to the SDK-recognized `main`,
and instruction classes for SMC warnings. It does not invent function names or
identify safe patch locations. Current leads are in `research.md`.

The iOS simulator completed a 15-minute Snow Jam ride/restart soak at a median
60 FPS and full simulation speed with zero JIT fallback (see
`mobile-validation.json`); that is host performance, not phone performance.

Next: complete iOS stock ride/reset/save and sustained physical-device tests,
then trace the low-memory fallback paths to guide measured optimizations.
Standalone Garibaldi follows with its art, scenery, rails, collision, and event
lifecycle. The PS2 prototype remains a reference.
