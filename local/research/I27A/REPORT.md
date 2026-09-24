# I27A — iOS HiDPI Simulator gate

Worker: Codex. Brief: `local/muse/prompts/I27A.md`. Evidence only; the orchestrator owns the Part 2 decision. One candidate, one Mac build, one Simulator build/install, one bounded run. No device action or fork push.

| Gate | Result | Receipt |
| --- | --- | --- |
| Fork pin and source review | `git ls-remote fork refs/heads/ssx3` and local `fork/ssx3` both read `ddaee780288adb076ce40050d87969b20bc4bb05`. Fresh `i27-hidpi` branch/worktree at this pin. W1F2 baseline window/drawable is 874×402/874×402; pinned raylib `c1ab645ca298a2801097931d1079b10ff7eb9df8` maps `FLAG_WINDOW_HIGHDPI` to `SDL_WINDOW_ALLOW_HIGHDPI`. | Remote read, W1F2 report/console, raylib source |
| Candidate and Mac taps-OFF suite | `PS2X_IOS` only: OR `FLAG_WINDOW_HIGHDPI` with the existing resizable flag before `InitWindow`; one `[ios-render]` statement logs screen/render sizes per frame. Non-iOS retains the original flag. Local fork commit `4ebb2ac`, trailer `Orchestrated-By: Codex`. Mac Release build passed; suite **585/585**, zero failed, from fork worktree root. Canonical codegen `register_functions.cpp` SHA matches E54F2: `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`. The log statement was added after the Mac compiler read this file, but is under `PS2X_IOS` and absent in the Mac target. | Fork commit `4ebb2ac`; `mac-{cmake,build,suite}.log`, `~/dev/ssx3-work/I27A/build.sh` |
| Simulator build/install | One Xcode Release Simulator build succeeded; `.mm` and changed runtime compiled and app linked. Staged app ad-hoc signed and installed on booted iPhone 18 Pro Simulator `7662ACD6-6294-4676-B426-26A3F8C7B258`. Binary SHA pair `06fc7ed52709a210ca41b3ad08f0a49af54c5605587d7c7dd2cc2b26b074843b`; stock ELF pair `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`, ISO pair `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`, source and staged matching. | `sim-{configure,build,install}.log`, `input-sha.txt`, `stage-sha.txt`, `binary-sha.txt`; `~/dev/ssx3-work/I27A/sim-build-install.sh` |
| Drawable transport | W1F2: window 874×402, drawable 874×402 (1×1). I27A: window 874×402, drawable 2622×1206 (3×3). **Transport PASS:** SDL exposes a Retina drawable. | `sim-console.log`, `acceptance.txt` |
| Actual render size and geometry | Last live raylib screen/render is 874×402/874×402, **one third** of drawable per axis. Four viewed screenshots show game and virtual pad in the lower-left 874×402 region, black elsewhere. **Native render-size FAIL.** Larger drawable alone does not establish native-resolution drawing or improved fonts. | `accept.py`, `acceptance.txt`, four PNGs under `~/dev/ssx3-work/I27A/run-i27a/` |
| I26-FAST route | One Simulator boot, bundled `ps2x.env`, 31 vsync-clock presses armed, last tick **2372**. Race HUD viewed at elapsed 100 s (00:00:04, 1%) and 160 s (00:00:11, 2%). Scripted route advanced despite geometry regression; touch was not tested. | `sim-run.txt`, `sim-console.log`, viewed frames |
| Limits and cleanup | Elapsed 161 s (<180). Four PNGs 804 KiB (<12 MiB), console 402,465 B, all copied text receipts 1.6 MiB (<8 MiB). I27A work area 4.0 GiB (<8 GiB), global disk 116.0 GB before and 120.0 GB after (<200 GB). Lease slot 1 released; slot 2 free. Script terminated app and own launch PID 82306. Runner-dir diff against `14b1e5cb` empty. Local fork branch clean; no push. | `sim-run.txt`, `disk_budget.sh`, lease status, fork git checks |

## Pinned raylib render path

Pinned raylib source is `~/dev/ssx3-work/E46-build/_deps/raylib-src` at `c1ab645ca298a2801097931d1079b10ff7eb9df8`.

| Source | Behavior relevant to this gate |
| --- | --- |
| `src/platforms/rcore_desktop_sdl.c:1812` | Maps the HiDPI flag to `SDL_WINDOW_ALLOW_HIGHDPI` at window creation. |
| `src/platforms/rcore_desktop_sdl.c:1064-1080` | SDL2 `GetWindowScaleDPI()` returns `(1,1)`; the SDL3 branch alone reads display scale. This build links SDL2. |
| `src/rcore.c:809-831` | Apple `GetRenderWidth/Height()` multiply `CORE.Window.render` by `GetWindowScaleDPI()`. The live post-resize log remains 874×402. |
| `src/platforms/rcore_desktop_sdl.c:1436-1446` | SIZE_CHANGED passes event window dimensions to `SetupViewport` and stores them as screen/current-FBO dimensions. `ps2_ios_runtime.mm:178` forwards window points, 874×402. |
| `src/rcore.c:3537-3561`, `src/platforms/rcore_desktop_sdl.c:1881-1884` | Viewport/render and initial current-FBO dimensions use point sizes with SDL2 scale 1. Inference: 874×402 viewport in a 2622×1206 drawable explains lower-left output. This is supported by screenshots; no GL state readback was made. A separate 1× intermediate FBO is not established. |

## Viewed frames and SHA pairs

The W1F2 baseline title, Setup Character and race images were viewed. Free-running frame hashes need not match. All I27A PNGs are 2622×1206; each SHA below matched two independent reads.

| I27A frame | Observation | SHA-256, both reads |
| --- | --- | --- |
| `shot-0010s.png` | SSX 3 title and virtual pad at lower left; black elsewhere. | `68ecbf26128a064b472bd68e65f4f363d97641e388f4f55f785c2f40c7224eb0` |
| `shot-0035s.png` | Select Mode / Peak 1 at lower left. **Setup Character capture missed**; W1F2 has that baseline frame, but there is no I27A pair. | `957ab7c6f67ac531b7e220c5823337d5f33da4299cc6569a90b90360e9f5ecbb` |
| `shot-0100s.png` | Race HUD 00:00:04, 1%; same geometry and known dark GS region. | `588a57a13a00694355f69a535e9bb82de64f2174c3756b3d49b9577c91d278a5` |
| `shot-0160s.png` | Race HUD 00:00:11, 2%; same geometry and dark region. | `78af0e9abacc292b4464e6a7abc839dd2a5ead5140e1f45f12d70a8b68c44b15` |

`acceptance.txt` separately reports drawable transport **PASS**, native render size **FAIL**, route and suite counts, and full HiDPI gate **FAIL**. The missing I27A Setup Character screenshot and lack of GL viewport readback are evidence gaps. No further build or run was made after the geometry failure.

## Exact commands

```sh
git ls-remote fork refs/heads/ssx3
git worktree add -b i27-hidpi ~/dev/ssx3-work/I27A/PS2Recomp ddaee780288adb076ce40050d87969b20bc4bb05
shasum -a 256 ~/dev/ssx3-work/codegen-ssx3/register_functions.cpp ~/dev/ssx3-work/E54F2/codegen/register_functions.cpp
bash ~/dev/ssx3-work/I27A/build.sh
# from ~/dev/ssx3-work/I27A/PS2Recomp:
~/dev/ssx3-work/I27A/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/I27A/suite.log 2>&1
bash ~/dev/ssx3-work/I27A/sim-build-install.sh
bash ~/dev/ssx3-work/I27A/sim-run.sh
python3 local/research/I27A/accept.py > local/research/I27A/acceptance.txt 2>&1
python3 local/tooling/p_lane_lease.py status
local/tooling/disk_budget.sh
# from fork worktree:
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git add ps2xRuntime/src/lib/ps2_runtime.cpp
git commit -m '[I27A] Probe iOS HiDPI drawable' -m 'Enable the SDL HiDPI window flag only on iOS and record raylib render dimensions for the bounded Simulator gate.' -m 'Orchestrated-By: Codex'
```

The three scripts under `~/dev/ssx3-work/I27A/` hold the exact configure, build, stage, `simctl`, lease and own-PID cleanup commands. Initial sandboxed read-only `simctl list devices` and `pgrep` failed due to sandbox services and passed on escalated retry. There was no denied escalation, build failure or boot crash. No iPhone, iPad, Odin or fork remote action occurred.
