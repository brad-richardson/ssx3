# Repeated native rendering and camera experiment

September 13, 2026. Follow-up to the [first native investigation](120hz-native-path.md).
The installed phone build remains unchanged.

Follow-up: [independent rendering deadlines and framebuffer ownership](120hz-independent-schedule.md).

**A repeatable native drawing boundary now works in an isolated experiment.**
The corrected test completes 120 original/extra-render pairs, retaining the
graphics queue limit and omitting two duplicate timing helpers. Watched gameplay
state remains unchanged across every extra draw. This is progress toward
retaining and interpolating render state; it is not working 120 Hz presentation
or evidence of reduced input latency.

**The frozen-state visual test also succeeds:** the offset phase changes the
rendered scene, and the normal/restored PNGs are byte-for-byte identical. This
establishes a reversible alternate render view for this captured scene.

## What the graphics handoff does

For the pinned GXBE69 executable, the graphics object has two different kinds
of state that must be treated separately:

- **Submission/completion:** readiness checks a pending count at `r13-20556`
  and rejects drawing when it equals two. Submission at `0x801CB9E4` increments
  the count and advances a producer index modulo two. Completion at
  `0x801CB964` decrements it and advances the consumer modulo two, with
  completion/retrace paths participating in that protocol. Queue records retain
  positions in the graphics command stream. Forcing readiness true would not
  allocate another buffer or safely extend this protocol.
- **Rendering and timing:** application render ends graphics work through
  `0x8021A5FC`, then processes accumulated update time and an event/work helper
  at `0x8015C5A0` and `0x80139F20`. Their call sites return to `0x8010AC24` and
  `0x8010AC2C`. The probe skips only those two calls on an extra render; it
  preserves their execution on the original frame and leaves actual graphics
  submission/completion intact. This does not identify every render side effect.

The experiment retries a rejected extra call through the **original** readiness
check, allowing guest interrupts and completion to progress. It stops retrying
after 100,000 retries or two host seconds per extra draw. That polling is
intentionally a correctness experiment. It stalls application updates and
performs millions of instrumented calls; it must not become the production
presentation scheduler. The guest video clock is unchanged.

## Completed tests and an important correction

Each completed run lasts 200 seconds with an isolated player and fresh profile.
The same Garibaldi 027 assets and course-start sequence are used, but host-timed
input and differing trajectories do not establish deterministic replay.

| Experiment | Complete additional renders | Result |
| --- | ---: | --- |
| First queue-wait probe | 61 of 120 candidates | 59 candidates followed rejected original calls; they were first draws, not extra draws |
| Corrected pairs, duplicate helpers skipped | 120 of 120 | Both members of every pair reach view setup and graphics frame end; both timing helpers skipped on every extra draw |
| Camera-copy offset on extra draws | 120 of 120 | Offset/restored the copied matrix 120 times; both helpers skipped; watched gameplay state unchanged |
| Frozen normal/offset/restored sequence | 120 after one original | No application updates between draws; 40 offsets/restorations; original and restored captures identical |

The first waiting probe initially looked like 120 successful second draws.
Checking the predecessor's readiness and scene counters exposed the mistake.
The corrected probe requires a completed original scene draw before beginning
an extra draw. The analyzer and regression tests now enforce this distinction;
adjacent callback events alone are not sufficient. A helper-skipping run with
the old pairing logic was interrupted before its experimental window and is
excluded from completed evidence.

In the corrected pair test, all 120 extra draws leave these snapshots unchanged:
rider position/state, both RNG arrays, the 0x100-byte gameplay view window,
0x400-byte application window, and 0x800-byte window beginning at the rider.
The extra calls execute zero instances of either timing helper, and record
120 skips of each helper. Original completed draws still execute both helpers.
There are no intervening top-level application updates within a pair.

These are net entry-to-return comparisons. Other threads, transient writes,
other objects, particles, trails, animations, streaming and audio need broader
audits. A complete graphics-frame path also does not prove that every object
is drawn correctly from a changed camera.

## Camera boundary

Graphics virtual slot +140 at `0x80224CC8` copies 16 floats from the active
view+64 into the current graphics matrix stack entry. Initialization points
that stack into the graphics object's own memory at +5360; push/pop moves the
entry pointer at +6132 in 64-byte increments. This is distinct from the gameplay
view's storage. Live samples have affine-matrix structure, with translation
components at byte offsets 48/52/56.

The camera probe adds 500 to the first translation component of the renderer's
copied matrix after the copy returns, and restores all 64 bytes after rendering.
This is a diagnostic perturbation, not a validated world-space camera movement,
nor interpolation. It does not write the original gameplay view matrix.

Screenshots requested during the first offset run show gameplay, but cannot
prove which individual draw was captured. The screenshot API requests a future
frame asynchronously, while the game queues graphics work. Request labels must
not be interpreted as exact display-frame identities.

The follow-up comparison therefore holds one application state for a continuous
120-render sequence: 40 normal, 40 with the matrix offset, and 40 restored.
Captures in the middle of each phase avoid treating a capture request at a phase
boundary as an exact frame match. Guest interrupts still run; this freezes
top-level application updates, not the entire machine.

The completed sequence records 120 full view-setup/frame-end traversals,
40 matrix offsets and 40 restorations, zero executions of the two skipped
helpers, and no changes to any watched snapshot on an extra draw. All 120
draws form an uninterrupted chain anchored to one completed original frame.

For captures requested at repeats 20, 60 and 100 (middle of each phase):

| Comparison | Changed RGB pixels | Interpretation |
| --- | ---: | --- |
| Normal → offset | 2,758,177 of 2,830,080 | The perturbation produces a visibly different scene image |
| Normal → restored | 0 | Decoded images and the complete PNG files are identical |

Visual inspection shows the shifted scene moving the rider toward the right
edge, with fixed HUD values and pose; restoration returns the original picture.
This does not establish every object's correct visibility from the new view,
nor correct interpolation across moving states. The screenshots are phase
samples, not exact frame-ID or input-latency measurements. Their comparison
receipt is `sweep-image-comparison.json` in the local evidence directory.

The frozen render sequence took about 24 seconds between its first and last
extra return on this instrumented Mac run, with roughly 6.5 million readiness
retries. It is deliberately inefficient and cannot support a performance or
high-refresh claim. Input buffering and asynchronous systems continue while
application updates are withheld; this is not a gameplay-equivalence test.

## Next implementation boundary

1. **Recover a complete render view and visibility input.** The graphics matrix
   stack is a useful starting point, but the renderer also reads a separate
   projection stack, cached transforms and game-side visibility data. The
   frozen-state test now proves reversible image changes; next verify culling,
   occluded surfaces and attached rider/board geometry across camera movements.
2. **Retain render work independently of the original two-entry queue.** A host
   renderer needs ownership and lifetime rules for geometry, matrices, textures
   and completion. Decouple those render resources from the original submission
   cadence while keeping input, gameplay and once-per-update work at their
   validated cadence. The polling experiment provides no mobile timing budget.
3. **Add render-state history and measure latency.** Interpolate camera and
   rider/bone transforms together, handle discontinuities and recompute visibility.
   Measure actual phone display timestamps, missed deadlines and input latency.
   History-based interpolation adds delay unless sampling/prediction is handled
   explicitly. True higher-rate physics remains a separate later experiment.

These are executable-level hooks, with no Garibaldi coordinates or asset-name
conditions. The mechanisms should transfer to other courses, subject to
validation; the current camera probe assumes the single-player view. Share the
state/render contracts between iOS and Android, with Metal/Vulkan resource
ownership and presentation in platform adapters.

## Reproduce without replacing production

```sh
python3 tools/gamecube_native_trace.py build \
  --game local/game/gc-gari-027 \
  --output local/research/120hz/new-seam-player

# All paths and profile names below must be fresh.
SSX_NATIVE_PROBE="$PWD/local/research/120hz/new-seam-events.jsonl" \
SSX_NATIVE_DOUBLE_RENDER=1 SSX_NATIVE_WAIT_REPEAT=1 \
SSX_NATIVE_SKIP_BOOKKEEPING=1 \
python3 local/research/120hz/new-seam-player/course_check.py \
  --game local/game/gc-gari-027 --profile new-seam \
  --output local/research/120hz/new-seam-run --seconds 200

python3 tools/gamecube_native_trace.py summarize \
  local/research/120hz/new-seam-events.jsonl
```

For the frozen camera sequence, additionally set `SSX_NATIVE_CAMERA_OFFSET=1`,
`SSX_NATIVE_CAPTURE=1` and `SSX_NATIVE_FROZEN_VIEW_SWEEP=1`, and summarize with
`--frozen-sequence`. That explicit analyzer option accepts a chain of complete
extra draws only when it is anchored to a completed original render with no
intervening application update. Unset experimental flags to disable them.

Local evidence is under ignored `local/research/120hz/render-seam/`:
`wait`, `paired`, `camera`, their event traces, player build receipts and native
run logs, plus the frozen `sweep` run. The corrected pair trace SHA256 is
`47b3849458e4b0bfc723174a9236a33180c7b0b9cfc9aeaede5ade56a64a963d`.
The camera-offset trace SHA256 is
`94ae68940ca711a17a4b6910055e287b81405fd393fd50d463a51df19f4ecf1b`.
The frozen sequence trace SHA256 is
`c77e1f346a70e9fa632628f9ac2b7b238756d6dc7e768f3d470d6807d98a77bf`.
Normal/restored PNG SHA256:
`8f7b237ce9a913dd024c816a5ec007267b0d36fc61303c1ffb9cc9ebf55d2fd9`.
Offset PNG SHA256:
`64cb3f5ecf7fb79ad8668c91873a2675375d1097f0986b937cab926c20c521f8`.
All four completed runs report zero invalid memory accesses, GPU command errors
and JIT fallback runs. The reusable player builds successfully; its probe logic
matches the tested frozen-sequence header apart from explanatory comments.
The production player hash remains unchanged. Twenty-four focused Python tests
pass, including rejection of false pairs and unanchored frozen sequences.
Game disassembly, generated game source, assets, saves and screenshots stay
local. Only authored diagnostics, tests and engineering findings are committed.
