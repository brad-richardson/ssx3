# MF2 REPORT — MetalFX as a smoothing-style app option: integration map + toggle prototype

Tables + hypothesis + next-action recommendation, no verdicts. Time box: 6 h.
Evidence dir: `local/research/MF2/` (STANDALONE). Prototype diffs to tracked
files ride in the SAME commit, separately listed in section 3. No PS2 boots,
no lease, no game-content moves, no toolchain changes, no trial-infra refactor.
Docs read first (per brief): `local/research/MF1/REPORT.md` (all),
`tools/mobile_gamecube.py`, `tools/native_gamecube.py`,
`tools/gamecube_schedule_check.py`, `tools/mobile_pacing_check.py` end to end,
plus `docs/research/review-2026-09-20-first-frame-and-gs.md` (paraLLEl-GS
adoption context, applied in section 2e).

## 0. Experiment contract + byte caps

| Item | Content |
| --- | --- |
| Hypothesis (H1) | MetalFX interpolation can ride the smoothing option's plumbing shape (launch flag → app config → runtime switch → frame-boundary stage) with zero behavior change when off and a present-but-bypassed stage when on-without-motion |
| Observable | `--metalfx` → `-ssxMetalFX` → `launch.json` `metalFX:true` → lifecycle `metalfx_option` + one `metalfx_stage` (mode bypassed) at first present; off → `false`/absent with no new per-frame work beyond one atomic load |
| Alternatives | (A) new trial `Kind::MetalFX`: rejected, it would flow into the non-F predicates (single-XFB alias, pose interpolation) and need trial-infra edits; (B) menu on/off toggle: deferred, live-switch semantics unscoped; (C) real `MTLFXFrameInterpolator` now: rejected, needs motion + textures + framework link, which is MF3 |
| Stop | Any existing test failing → fix, never skip; App.mm TU not compilable in-box → table recipe, mark compile-unverified; sim/device run not fitting the subordinate box → table recipe, do not rush a build |

Byte caps (declared up front, ALLOCATED bytes via `du -sk`):

| Cap | Ceiling | Actual | Receipt |
| --- | --- | --- | --- |
| MF2 evidence (`local/research/MF2/`) | 8 MiB allocated | see §6 | `receipts/byte-accounting.txt` |
| New build trees | 0 (single-TU recompile inside existing `local/native/ios-device` only) | 0 | §4 |
| Prototype diff | 4 named files, ≤ 60 added lines | 4 files, +57 incl. new header | §3, `git diff --stat` |
| System volume `/` | nothing new (workspace + `/tmp` scratch only) | `/tmp/mf2-ninja.log` scratch only | §6 |

## 1. Smoothing end-to-end map (the template)

User-facing flag → trial config → build/run plumbing → runtime switch →
measurable effect. Line numbers are the committed (post-MF2) tree.

| Hop | File + line | Behavior |
| --- | --- | --- |
| 1. CLI flag | `tools/mobile_gamecube.py:494` | `--smoothing-at` (float): one guarded trial at active test seconds |
| 2. Validation | `tools/mobile_gamecube.py:369-374` | Requires bounded `--sequence`; finite; `0 <= at <= duration-40`, else `ValueError` before any device change |
| 3. Launch-only guard | `tools/mobile_gamecube.py:543-544` | Non-`launch` commands exit 2 |
| 4. App-arg forwarding | `tools/mobile_gamecube.py:412-413` | Appends `-ssxSmoothingAt <at>` after the `--` devicectl separator |
| 5. Flag tests | `tests/test_mobile_gamecube.py:140-151,221-234` | Rejects unbounded/out-of-range pre-device; asserts exact post-separator argv |
| 6. App parse | `native/ios/App.mm:739-747` | Inside the `-ssxAutoTest` block: scans `-ssxSmoothingAt` → `_scheduledTrialAt`, ignores out-of-range with stderr |
| 7. Launch config record | `native/ios/App.mm:784` | `launch.json` `scheduledSmoothingAt` (or null) |
| 8a. Automated dispatch | `native/ios/App.mm:1044-1055` | At scheduled active seconds (never into an in-flight checkpoint): terminal-state guard → `NativeTrial::Request()` + `trial_requested` (kind Smoothing), else `scheduled_trial_skipped` |
| 8b. Menu dispatch | `native/ios/SessionMenu.mm:241-249,305`, `native/ios/App.mm:1144-1155,985-994` | "Try smoothing" → `onSmoothing` → `_trialAfterOutput=YES` → after output settles, same terminal-state guard → `Request()` + `trial_requested` |
| 9. Runtime switch | `native/diagnostics/trial_control.h:12,23-30` | `Kind::Smoothing`; `Begin()` refuses to overwrite a live trial (backstop); `Request()` = `Begin(Smoothing)` |
| 10. Trial start/epoch | `native/diagnostics/native_render_schedule.h:163-170` | `Waiting` → `Running`, 35 s cap (`ends=Now()+35`), per-trial epoch reset (stale-budget regression guard) |
| 11. XFB alias | `native/diagnostics/native_render_schedule.h:179-207` | Non-F kinds take the single-XFB completion alias under immediate-XFB validation; invalid setup → `Unavailable`, never abort |
| 12. Extra-draw gate | `native/diagnostics/native_render_schedule.h:218-249` | 10 s grace, then SpeedFloor guard (`made<15` extras or long_rate<0.95 → `performance_limit` + cancel); per-frame veto withholds extras during dips |
| 13. Pose interpolation | `native/diagnostics/native_pose_interpolation.h:157-161,75-90` | `smoothing_trial = kind!=F`; `active` needs trial window + riding state; counts frames/extras/blended; emits `interpolation` rows |
| 14. Finish | `native/diagnostics/native_render_schedule.h:131-135` | Quiescent `Finished` for Smoothing (Combined also needs dt-const restore); mode restored at `:117-121` with `restore_mode` |
| 15. Refresh-rate effect | `native/ios/App.mm:1312-1323,1347` | Display link raised while a non-F trial runs; status line reports smoothing end on load limit |
| 16. Desktop lifecycle gate | `tools/gamecube_schedule_check.py:16-108` | `validate_trial_trace`: cancel/drain/restart/idle-cancel/combined/complete + clean doubled update + blended extras (existential + ≥0.5 aggregate ratio) + watched-state unchanged |
| 17. Phone pacing gate | `tools/mobile_pacing_check.py:25-28,326-417` | `POLICY` (117/s, 8.6/10/17 ms spacing, 0.98x speed, thermal ≤1); `analyze_window`/`analyze_trial` over `launch.json` + `native-trial.jsonl` + `present.csv` + `metrics.jsonl` + `runtime.log`; short bursts → `inconclusive`, never pass |

What "measurable effect" means for smoothing: injected extra draws with
blended poses reaching glass (present.csv positive `presentedTime`), counted in
`native-trial.jsonl` (`render` repeat rows, `interpolation` blended rows) and
gated by the pacing policy. MF2 mirrors hops 1–9 + a frame-boundary stage; full
MF effect measurement reuses hop 17 unchanged.

## 2. MF integration map

### 2a. GC recomp frame boundaries (where the interpolator inserts)

Phone frame path today: immediate XFB (`ImmediateXFBEnable=True`,
`CapImmediateXFB=False`, `MTLUsePresentDrawable=1` —
`native/ios/App.mm:628`) → Dolphin Metal backend acquires a CAMetalLayer
drawable and presents it → `after_present_event` hook observes.

| ID | Insertion point | File + line | Has at that point | Fit for MF |
| --- | --- | --- | --- | --- |
| I1 (MF3 target) | `Metal::Gfx::PresentBackbuffer`, between `EndRenderPass` and `presentDrawable` | `third_party/.../VideoBackends/Metal/MTLGfx.mm:469-492` (`:473`, `:483`, `:490`) | Backbuffer texture, render command buffer, drawable; `BindBackbuffer` (`:456-467`, `nextDrawable` at `:462`) supplies the input | Pre-present: the only point that can hold frame N+1, run the interpolator encode, and present real + synthetic in cadence |
| I1 seam (no vendor edits) | iOS diagnostic source-copy generator | `tools/ios_diagnostic_sources.py:13-21`, `native/ios/CMakeLists.txt:38-56` | `replace_once` seam injection into a local `DiagnosticMTLGfx.mm` copy (already injects acquire/submit tracing); pinned vendor checkout untouched | MF3 insertion rides this exact mechanism: extend `metal_source()` with the MF stage markers |
| I2 (MF2 prototype site) | `after_present_event` hook | `native/ios/App.mm:900-913` (`VideoInterfaceDuplicate` excluded at `:903`) | Post-present observation: suggested window size, target rect, EFB size, frame count | Bypass counting + reachability proof only; too late to intercept the drawable (table 3) |
| I3 (rejected) | `after_frame_event` hook | `native/ios/App.mm:872-899` | CPU frame event: perf metrics, EFB size, draw-call aggregates | No drawable access; observation only |
| I4 (future if I1 can't hold cadence) | Separate present scheduler owning the CAMetalLayer | none exists | Would own the 120 Hz cadence outright | Largest change; MF3+ fallback, not the first shape |

Constraints the map surfaced for MF3:

| # | Constraint | File + line | Implication |
| --- | --- | --- | --- |
| C1 | `layer.framebufferOnly = YES` | `native/ios/App.mm:361-365` (BGRA8Unorm layer, `:364`) | Drawable texture is not sampleable; MF3 sets `NO` (revisit cost) or renders into an intermediate target |
| C2 | `presentDrawable:` path forced on | `native/ios/App.mm:628`, `MTLGfx.mm:481-483` | Schedules present on the render command buffer; an MF mid-frame needs its own drawable acquire + present or a held frame |
| C3 | 2 establishing encodes per instance; 2 passthroughs after reset | MF1 §3c findings 4–5 | Startup/reset outputs non-interpolated frames for 2–3 intervals; live warmup handling open (MF1 G6) |
| C4 | `presentedTime` establishes delivery, not distinct motion or latency | `docs/research/120hz-pacing-acceptance.md:39-44` | MF3 quality needs a distinct-motion check beyond the pacing gate; input latency unmeasured |

### 2b. Motion-vector source OPTIONS

| ID | Source | Existence today | Cost to make live | What it can / can't prove |
| --- | --- | --- | --- | --- |
| M0 | Nothing (GX path emits no MV) | `native/diagnostics/reprojection_capture.h` emits color (`Save`, `:72`), depth (R32F), camera (slot 0 `Indexed`, `:62-71`), XFB addrs — no motion (MF1 input-table row 3) | Zero | Proves nothing; the bypass stays on |
| M1 | Camera-only offline warp | `tools/gamecube_reprojection_warp.py:predict_view` (`:26`), `warp()` → per-pixel `motion` (`:141-147`); depth-tested forward splat, NumPy/PIL, holes in magenta, "not a realtime backend" (`:1-10`); rider/objects/particles/transparency explicitly have no vectors (`:272`) | Port to live + per-frame camera/depth feed (capture is research-only: 8-frame cap, env-armed — `reprojection_capture.h:40-48`) | Proves camera-motion quality ceiling only; object motion still open (MF1 §2 starting point) |
| M2 | Full GX export (per-pixel MV from prev-frame reprojection of every vertex, or EFB-space derivation) | No seam exists; nearest inputs are the indexed-XF camera loads (M0) | New derivation stage (GPU or CPU) + RG16Float upload per frame; needs prev-frame pose + prev camera retention | Proves full real-content quality; the MF1 G1 blocker |
| M3a | Exact synthetic motion | MF1 harness (`local/research/MF1/harness/mf1_scene.h`): rect `(-32,0)`, rest `(0,0)` | ~Zero (in-harness only) | Interior bit-exact on all 3 devices (MF1 §4a) — proves stage correctness + cross-device determinism, never real-content quality |
| M3b | Zero / uniform fallback | MF1 measured both (MF1 §2 motion table) | ~Zero | NON-VIABLE at 32 px/frame (interior MAE 89–96, vs ~98 no-interp baseline); viable only where zero motion is exactly correct (static content) |

### 2c. UI/HUD routing decision

MF1 measured two paths (MF1 §4a): composited-in-color (`comp`) and separate
`uiTexture` (`sep`); static HUD strip reproduces exactly (MAE 0.00) on both.
Offline precedent: paired-background alpha solve reconstructs all 8 frames
within 2 levels (99.99% within 1) — `tools/gamecube_reprojection_hud.py`;
live HUD split exists only offline (first perspective→ortho boundary,
explicitly invalidated if perspective draws follow it —
`tools/gamecube_reprojection.py:4-8`).

| Path | MF1 evidence | Live-path cost | Decision |
| --- | --- | --- | --- |
| Separate `uiTexture` (primary) | hud 0.00; isolates HUD from world motion | Live split per frame + second texture upload; split detector is offline-only today | PRIMARY: real HUD animates (timer, speed, position, menus); composited color would expose moving HUD edges to interpolation under world motion vectors (HUD has no valid world motion → smear/halo risk at HUD boundaries); `sep` keeps HUD pixel-exact regardless |
| Composited in color (fallback) | hud 0.00 on static content | Zero (no split needed) | FALLBACK when the live split is unavailable or invalidated; acceptable for static-HUD content per MF1 |

### 2d. Perf model (GC recomp on device: frame budget vs MF1 costs)

Budgets (MF1 §4c, from `120hz-pacing-acceptance.md`): 16.67 ms aggregate (one
real + one synthetic share it: real render + capture + warp + HUD); 8.33 ms
per present.

| Term | Value | Source |
| --- | --- | --- |
| MF GPU, iPhone, 640x528 (phone 1x internal) | med 2.20 / p95 3.58 (exact); 1.42 / 1.57 (zero) | MF1 §4b |
| MF GPU, iPhone, 1280x720 | med 3.41 / p95 3.54 | MF1 §4b |
| MF GPU, iPhone, half drawable 1434x660 (~0.95 MP ≈ 720p 0.92 MP) | ≈720p cost by pixel count; exact size UNMEASURED | MF1 nearest datum (OPEN) |
| MF GPU, full drawable 2868x1320 (3.79 MP, 4.1x of 720p) | UNMEASURED (nearest: Mac 1080p med 5.34) | OPEN |
| Host submit overhead | 0.02–0.06 ms Mac; device UNMEASURED | MF1 §4b + G9 |
| Structural latency | +16.67 ms per interpolated frame (later-frame wait) | MF1 §4c (additive, not GPU work) |
| Real-frame GPU on phone | Final command buffer only in `present.csv`; full-frame UNMEASURED | `native/ios/SessionDiagnostics.mm:129-133` (OPEN: mine existing reports) |
| Real-frame CPU on phone | Extra draw 8.45 ms thread CPU in 8.64 ms median (build 1747c62a); smoothing dual-core held 35 s at ~91 displays/s (60 + ~32 extras/s); Match/2x limited at 3.49–13.55 s (113c9b20); longest warmed 15.88 s at 114.34/s (971dc928) | `docs/todo.md` 120 Hz item |
| Sustained headroom today | NO sustained pass on any phone trial; short bursts only | `docs/todo.md` 120 Hz item |

Why it likely misses on the GC recomp path: at half drawable the known MF
terms alone (med ~3.4, p95 ~3.5–6.3) sit inside one 8.33 ms slot but leave
~2–5 ms for the real frame's GPU + capture/upload + HUD composite — against a
phone that already load-limits smoothing trials on CPU with no sustained
headroom; at full drawable (4.1x pixels, no datum) the MF term grows while the
slot stays 8.33 ms. The +16.67 ms structural latency is additive regardless.
Learning that pays either way: smoothing extras cost emu-thread CPU per extra
(8.6 ms median), while MF shifts the synthetic-frame cost to a bounded GPU
post-process — different bottleneck, measurable independently of sim rate.

Flip conditions (what content/load change would flip it):

| # | Condition | Effect |
| --- | --- | --- |
| F1 | Match-internal output 640x528 | MF ≈ 2.2 med / 3.6 p95 (smallest measured phone cost) |
| F2 | Static/light content (menus, stills) | Zero-motion path is exact AND cheaper (1.42 vs 2.20 @528) |
| F3 | Real-frame GPU measured small | Mine `present.csv` final-cmdbuf series from existing reports; if real ≈ 2 ms, half-drawable fits on paper |
| F4 | Async MF encode overlapped with next-frame CPU | Needs scheduler work (MF3+); hides part of the MF term |
| F5 | Half (not full) drawable + 1x internal | Minimizes both MF input pixels and real-frame cost (course/trajectory caveats per `todo.md`: no causal size claim without matched route) |

### 2e. G7/G8 adoption context (paraLLEl-GS review §)

The review's adoption lessons transfer to MF lane shape, not to PS2 content:
adopt-before-write (MF reuses Apple's `MTLFXFrameInterpolator`, no custom
interpolator — MF1 §3b), measure a real workload early (MF1 measured real-GPU
cost on all three targets before any integration), and reuse existing
statistics before building new instrumentation (MF3 reuses `present.csv` +
`native-trial.jsonl` + the hop-17 pacing gate; the prototype adds exactly two
lifecycle rows, no new trace). `docs/research/review-2026-09-20-first-frame-and-gs.md:239-255` (§paraLLEl-GS; lines shifted +67 by a concurrent lane's follow-up insert during this session — cited by heading).

## 3. Toggle prototype (interpolator stage PRESENT but BYPASSED)

Design: a launch-only boolean app option (`--metalfx`, precedent:
`--audio-dump` / `--dispatch-samples`), NOT a trial kind — a new
`Kind::MetalFX` would flow into the non-F predicates (single-XFB alias at
`native_render_schedule.h:179-207`, pose interpolation at
`native_pose_interpolation.h:157-161`) and need trial-infra edits, which are
out of scope. The stage is a counted no-op behind one atomic; no trial state,
no vendor file, no build file touched.

### 3a. Diff table (4 NAMED files, +57 / -2)

| File | Lines | Change | Behavior off (default) | Behavior on (`--metalfx`) |
| --- | --- | --- | --- | --- |
| `tools/mobile_gamecube.py` | `:434-435` (forward), `:531-532` (argparse), `:534` (guard) | `--metalfx` store_true → appends `-ssxMetalFX` after `--` | No flag forwarded; argv identical to before | `-ssxMetalFX` in app argv |
| `native/ios/App.mm` | `:31` include, `:215` ivar, `:349-350` parse + arm, `:778` launch.json, `:795` option event, `:904-907` present-hook call | Parse `-ssxMetalFX` → `_metalFXEnabled` → `NativeMetalFX::enabled`; record + announce | `launch.json` `metalFX:false`; `metalfx_option` logged; present hook does one atomic load, no event, no counting | `metalFX:true`; `metalfx_option` + one `metalfx_stage` (mode bypassed) at first present; `bypassed` counter increments per present |
| `native/diagnostics/metalfx_stage.h` (NEW, 21 lines) | `:11-20` | `namespace NativeMetalFX { enabled, bypassed, announced; NotePresentBypassed() }` — counted no-op, announce-once | Same binary path, `enabled=false` short-circuits before the call | Per-present counting + single announce |
| `tests/test_mobile_gamecube.py` | `:285-304` | `test_metalfx_applies_only_to_launch_and_reaches_app` (mirrors the audio-dump test) | Guards the launch-only restriction + exact post-separator argv | Same test (flag present → forwarded) |

`git diff --stat`: 3 files changed, 36 insertions, 2 deletions, plus the new
992-byte header. No other tracked file modified; vendor, build files, trial
headers, and phone settings untouched.

### 3b. Synthetic-motion demo decision

NOT included as a subsystem. What falls out of the bypass naturally is the
dry-run trace itself: with the option on, every present passes the stage
(counted) and the first announces — demonstrating per-frame reachability with
zero frame effect, which is the complete observable the bypass can honestly
produce. A synthetic-motion *encode* would need a real
`MTLFXFrameInterpolator` instance + texture plumbing + a motion feed: a new
subsystem, disallowed by the brief, and MF1 already proved interpolator
quality headless — an in-app synthetic encode would re-prove MF1 §4a, not
advance MF3. Static-content identity (M3b exact-where-static) remains available
to MF3 as its first live correctness check once the instance exists.

## 4. Verification

### 4a. What ran in-box (receipts in `receipts/`)

| Check | Command | Result | Proven |
| --- | --- | --- | --- |
| Focused suite (flag + all neighbours) | `python3 -m pytest tests/test_mobile_gamecube.py -q` | 29 passed, 89 subtests passed | `--metalfx` validation/guard/forwarding + no ordering regressions in any launch-flag test |
| Related suites | `pytest tests/test_metal_capture.py tests/test_patch_ui_glyphs.py -q` | 15 passed | No collateral in the other `mobile_gamecube` importers |
| New test fails first | same, `-k metalfx`, before the tool edit | `unrecognized arguments: --metalfx` | Authentic failure observed pre-implementation |
| Header self-check | `clang++ -std=c++17 -fsyntax-only native/diagnostics/metalfx_stage.h` | clean | Header is self-contained C++ |
| App.mm TU compile (device SDK, `-j2`) | `./local/tooling/ninja -C local/native/ios-device -j2 CMakeFiles/SSXNative.dir/App.mm.o` | exit 0; `App.mm.o` 22:41:18 newer than `App.mm` 22:40:31 + header 22:40:16 | The App.mm edit compiles in the real TU with the real flags; single object only, no relink, no install |
| Tree scope | `git status --short` | 3 modified + 1 new header, exactly the named set | Re-configure + compile wrote only ignored `local/` paths |

NOT proven in-box: simulator-TU compile (touched lines are all outside
`TARGET_OS_SIMULATOR` branches, but the sim TU was not compiled), any runtime
behavior (no sim/device run), any interpolation (none exists by design), any
perf number (no presents observed). A full sim configure+build (no
`local/native/ios-simulator` tree exists; ~700 MB–2 GB, well over an hour at
subordinate `-j2`) does not fit this lane's box — recipe tabled below instead
of rushed, per the gates.

### 4b. Simulator verification recipe (tabled, not run)

```sh
# From /Users/bradrichardson/dev/ssx3, subordinate -j2; all outputs under existing local/ paths.
python3 tools/mobile_gamecube.py configure --simulator --device <SIM-UDID>
python3 tools/mobile_gamecube.py build --simulator --jobs 2
python3 tools/mobile_gamecube.py install --simulator --device <SIM-UDID>
python3 tools/mobile_gamecube.py provision --simulator --device <SIM-UDID>   # game data (disc required)
python3 tools/mobile_gamecube.py launch --simulator --device <SIM-UDID> \
  --sequence native/ios/snow-jam-smoke.json --metalfx
# ... let the bounded sequence run, then:
python3 tools/mobile_gamecube.py collect --simulator --device <SIM-UDID>
# Expect: launch.json metalFX:true; lifecycle.jsonl metalfx_option + exactly one
# metalfx_stage (mode bypassed); present.csv display_unavailable rows (simulator
# has no presentation callbacks — SessionDiagnostics.mm:124-128); no other new rows.
# Control arm: same launch WITHOUT --metalfx → metalFX:false, metalfx_option
# only, no metalfx_stage row.
```

Simulator caveat (carried, not discovered): `presentedTime` is unavailable on
sim (explicit `display_unavailable`), so the sim run proves plumbing + stage
reachability only — pacing/quality need the device arm.

### 4c. Device verification recipe (needs a FRESH orchestrator prompt; never `--force-install` unprompted)

Same as §4b without `--simulator`, plus `sign` before `install`, on the
user's phone only after the orchestrator explicitly prompts the install. Expect
the §4b rows plus real `display` rows in `present.csv`. This run was not
attempted: no prompt was issued in this lane's box.

## 5. License notes

None — no third-party interface touched. The prototype adds no MetalFX import
(Apple first-party framework, untouched), modifies no vendored file (the I1
seam mechanism is mapped, not used), and copies no upstream code. The new
header is project-authored in the style of `trial_control.h`.

## 6. Exact commands + byte accounting

```sh
cd /Users/bradrichardson/dev/ssx3
python3 -m pytest tests/test_mobile_gamecube.py -q
python3 -m pytest tests/test_metal_capture.py tests/test_patch_ui_glyphs.py -q
clang++ -std=c++17 -fsyntax-only native/diagnostics/metalfx_stage.h
./local/tooling/ninja -C local/native/ios-device -j2 CMakeFiles/SSXNative.dir/App.mm.o
git status --short; git diff --stat
du -sk local/research/MF2   # ALLOCATED bytes, tracked below
```

Byte accounting (cap table in §0):

```text
$ du -sk local/research/MF2
40	local/research/MF2   # vs 8192 KB cap; see receipts/byte-accounting.txt
```

Scratch outside the project (kept, not committed, per probe rules):
`/tmp/mf2-ninja.log` (ninja re-run log). No other scratch.

## 7. Gaps (OPEN rows with owners)

| ID | Gap | Owner | Note |
| --- | --- | --- | --- |
| G-MF2-1 | GX motion-vector export (M2) | G-lane (export) → MF3 (consume) | MF1 G1 carried; M1 camera-only is the interim ceiling |
| G-MF2-2 | Live HUD split + `uiTexture` routing | MF3 (G-lane if GX layer tags needed) | Split detector offline-only; comp fallback covers static HUD |
| G-MF2-3 | Pre-present insertion (I1) + present scheduler + history buffers + warmup handling | MF3 | Via the `DiagnosticMTLGfx.mm` copy mechanism; MF1 G6 warmup carried |
| G-MF2-4 | `framebufferOnly` revisit / intermediate target (C1) | MF3 | Cost of `NO` vs extra blit unmeasured |
| G-MF2-5 | Real-frame GPU + capture/upload + HUD-composite costs on phone | MF3 (measure first: mine `present.csv` final-cmdbuf series) | Decides F3 flip legibility |
| G-MF2-6 | Sustained pass + thermal soak (MF1 G2) | MF3 | No phone trial has passed sustained; MF inherits the bar |
| G-MF2-7 | MF1 G4/G5/G7/G9/G10 carried (fresh-pair recovery, NDC/!reversed retest, min-OS, device CPU/mem counters, near/far/fov mapping) | MF3 / G-lane per MF1 §6 | Unchanged by MF2 |
| G-MF2-8 | Menu on/off toggle + saved preference surface | MF3 / follow-up | Launch flag covers automation; menu needs live-switch semantics |

## 8. Hypothesis note + the ONE next action

H1 status: static observables green (flag → config → switch compiles and is
unit-gated end to end on the tool side); runtime observables (`metalfx_option`
/ `metalfx_stage` rows in a real session) pending the §4b sim run. No verdict
offered — the sim run is the discriminating observation.

ONE next action (MF3 shape): execute the §4b sim recipe to bank the
`metalfx_option`/`metalfx_stage` + `launch.json` receipts and a baseline
`present.csv`; that run's final-cmdbuf GPU series simultaneously opens G-MF2-5
and sizes the I1 insertion budget — the measurement MF3's pre-present stage
with pluggable motion (M3a exact-synthetic first for the in-app correctness
ceiling, M2 live when G-MF2-1 lands) is designed against.

TAIL: this report's last content line is the MF3-shape sentence above. END-MF2-REPORT.
