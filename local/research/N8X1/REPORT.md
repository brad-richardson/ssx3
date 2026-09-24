# N8X1: exploratory Odin GPU session (report)

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/N8X1.md`, plus the orchestrator's lead (`N8D7M13/ORCH-GATE-B.md`) and its mid-session steering (live boot, then report).
Clock: first command 18:26:28 EDT; device work ended 19:16; report written 19:2x. Row-by-row log: [NOTEBOOK.md](NOTEBOOK.md).
All builds are diagnostic. **No speed claims.**

## Answer

The black Odin frames come from **paraLLEl-GS's hierarchical binner running with 128-wide subgroups on Turnip/Adreno 830**. The Mac never runs that code: `get_target_hierarchical_binning()` returns 1 under `#ifdef __APPLE__` (`gs/gs_renderer.cpp:1937-1943`). Adreno has no exact 32-wide subgroup, so `set_hierarchical_binning_subgroup_config()` falls through to the free `4..128` range with `wg = subgroupSize(128) * hier²` (logged on the Odin as `range 4..128, wg=512 (hier=2)`).

- Forcing flat binning (`PS2X_PGS_HIER=off`), or keeping hierarchical binning with a **fixed 64-wide subgroup** (`wave64`), makes the replayed tick-2050 frame a full race frame. Both give identical rows, and the frame is 97.4% pixel-equal to the Mac on the nearest-filter stream.
- Both also make the Odin **deterministic**: two `off` runs are byte-identical, where before runs split at tick850.
- A **fixed 128-wide** subgroup (`wave128`) breaks exactly like upstream. So the trigger is wave128, not the "varying" range as such.

A second, separate and much smaller difference explains the original tick44 split. **GS bilinear filtering uses the GPU's hardware linear sampler** (`ubershader.comp:1215-1227`: UV snapped to 1/16 texel, plus a 1/1024 bias, then `textureLod(linear_sampler)`). Adreno's filter rounds differently from Apple's. Tick44's first differing packet is the fading EA logo sprite (PSMT8H texture, bilinear, STQ). Forcing TEX1 to nearest makes that packet match exactly. Visually this is ±1–2 LSB noise: on the original stream with the fix, 91% of pixels are within ±2 per channel. It is not the black-frame cause.

A third, minor class: **per-primitive STQ triangle differences** (tick665 piece 108, a PRIM 0x5c textured tri-strip with nearest filtering, still differing with a sync after every packet). These are transient and not investigated further.

## Evidence

| # | Experiment (stream / build / env) | Result | Reading |
| --- | --- | --- | --- |
| 1 | Synthetic stream: prefix through tick43, tick-43 GIF packets split at EOP, marker after each piece (`tools/mkstream.py`); Mac vs Odin, old APK `da9a41a8…` | Mac final `97b13124` = ground truth. Odin equals it through the path-3 FB copy (`ced3975a`) and black clear (`ab21b091`); **first diff = logo sprite packet** (Odin `e11bfd7c` = M13 tick44) | The tick44 departure is one packet |
| 2 | Logo-sprite variants (`tools/mkvariant.py`) | ZMSK, RGB-only, alpha-only, ABE off: still differ. **TEX1_1=0 (nearest): equal `160743b5`** | Bilinear path |
| 3 | Whole stream with every TEX1 forced to nearest (`tools/nearestify.py`, 46,723 writes patched, `cca1d32f…`) | Odin = Mac tick50..650, split at 700, re-converges 1500–1600, black frame (0.089 non-black) | Bilinear explains the early split; a second fault remains |
| 4 | Nearest + `TU_DEBUG=flushall` / `syncdraw` (Turnip logs `TU_DEBUG=0x201`, so the flag is parsed) | Unchanged | Not a Turnip cache-flush/sync issue |
| 5 | STEP=1 bisect of the nearest stream, then per-piece markers at tick673 | With a marker after every piece, **Odin tick674 = Mac `4e882d1d`**. The Mac is unchanged by markers. Subset bisect (`hazard-674.log`, 18 runs): no single writer→reader pair; needs many batch cuts | Depends on batch size, not one hazard |
| 6 | Source read | Apple never uses hierarchical binning; Android uses it when `num_primitives >= 256` | H2 |
| 7 | APK 1 `19fed514…` (`PS2X_PGS_HIER` knob), nearest stream | `off`: 34/41 rows = Mac, frame 0.995 non-black, 97.4% px = Mac; default reproduces the failure | **H2 confirmed on device** |
| 8 | APK 1: `wave64`; `off` repeated; original stream `off` | wave64 ≡ off (rows and frame); off r1 = r2 byte-identical; original+off frame 0.998 non-black, 78.8% px exact, 91.0% within ±2 | Fix works with hierarchical binning kept; nondeterminism gone |
| 9 | APK 2 `13234420…` (fix as default + `wave128`/`fallback` modes) | default ≡ wave64 (byte-identical rows); **wave128 broken** (0.063 non-black); fallback broken (0.071) | Trigger = 128-wide waves |
| 10 | Mac host build with the same patches (`macbuild/`) | Default and `HIER=on` rows byte-identical to the old Mac; original stream 41/41 VRAM+priv = M13 Mac | Patch leaves the Mac untouched (gap: no log proves hier>1 engaged on the Mac under `on`) |

## Live Odin boot (orchestrator steering; diagnostic)

APK `19fed514a192468529dcb1ecf7dc3e86125d2cd90f3645ccbc927dfd6a068569` (runner `8ef277c9…6ef2`, Turnip `717812c3…` unchanged). N8D2 env: parallel backend, bundled Turnip, `PS2X_SKIP_MOVIE=1`, I26-FAST vsync pad route, empty `mc0`, `PS2X_VSYNC_RATE_LOG=1`. Keyguard `showing=false` and battery ≥93% (status 3 on AC) before each launch; force-stop after each run. Runner: [tools/run_live.sh](tools/run_live.sh).

| Run | Menu screen | Race screen (tick-2050 host dump) | `[vsync-rate]` lines |
| --- | --- | --- | --- |
| `wave64` | Select Peak menu, fully drawn (guest tick ~1000) | **Correct race**: 2ND/2, 00:00:05, terrain, rider, HUD, radio card | Invalid: my 2-value dump list isn't parsed (needs 3), so it dumped every present (1,551 dumps) |
| `off` | Select Peak menu mid-transition (right panel empty), tick ~1012 | **Correct race** (tick ~2028 log / dump 2050 `fnv1a=4483c15c`, fbp 112/112, fallback 0) | 0.743x at tick 224; **0.123x (7.39/s) at tick 2028**. Diagnostic build, no speed claim |

Both screens show fine horizontal stripes, as N8D2 also saw; not investigated. No `GameThread` line reached my logcat tag filter (gap). The host dump PNGs were not in the pulled dump dir (only `.txt` sidecars; gap). The device screencaps are the evidence.

## Candidate fix (not merged)

paraLLEl-GS is not in the PS2Recomp fork, so the fix is a diff against the staged renderer (`gs/gs_renderer.cpp` `85c29cb0…`, identical to `~/dev/ssx3-work/N8D7F/parallel-gs` working tree). The fork worktree `~/dev/ssx3-work/N8X1/PS2Recomp` (branch `n8x1-explore` @ `4fa0df1`) has **no commits**.

- **Clean candidate:** [n8x1-fix-clean.diff](n8x1-fix-clean.diff) (19 lines, `dabf37ce…`; patched file `a5688162…`; Mac `-fsyntax-only` OK). In `set_hierarchical_binning_subgroup_config`, before the free-range fallback, require a fixed wave64 when supported (`wg = min(subgroupSize, 64) * hier²`). On Adreno this is exactly the path validated as build 2's default and as build 1's `wave64` (rows 9 and 8). The clean diff itself was not built; build 2's default also tries 128 after 64, which is never reached on Adreno.
- Diagnostic knob patches actually built: [n8x1-hier.diff](n8x1-hier.diff) (APK 1), [n8x1-hier-knobs-build2.diff](n8x1-hier-knobs-build2.diff) (APK 2).

**wave64 vs off tradeoff:** both give identical output on every replay tested. `wave64` keeps hierarchical binning (cheaper binning for render passes with ≥256 primitives, full-screen 3D). `off` is the blunter fallback: it touches every big pass, and paraLLEl chose hierarchical binning for performance there. Prefer `wave64`. The live `off` race segment measured 0.12x, but that is a diagnostic build and no wave64 vs off comparison without dumps was run, so **no performance comparison is claimed**.

**Why does 4..128 break on Adreno? (hypothesis)** The free range behaves exactly like a required 128 (row 9), so the question is why the hierarchical binner fails at wave128. The shader code (`binning.comp:130-240`) looks subgroup-size-agnostic: tile per `gl_SubgroupID`, a 32-lane uniform loop stepping by `gl_SubgroupSize`, `subgroupBallot` counts. Suspects, untested:
- Turnip/ir3 wave128 lowering of `gl_SubgroupID` or ballot/`subgroupBallotExclusiveBitCount` in lanes 64–127.
- Shared-memory atomics plus `barrier()` in a 512-invocation workgroup at double thread size.

Two waves computing the same `gl_SubgroupID` would leave some coarse tiles with no primitive list, which fits the **block-shaped black holes and the run-to-run variance**. A minimal Vulkan compute probe on the Odin (write `gl_SubgroupID`, `gl_SubgroupInvocationID`, and ballot counts per invocation at required 64 vs 128) would confirm or refute it without the game. Keep this local; no upstream contact.

## Frames to view (scratch, not in git)

1. `/Users/brad/dev/ssx3-work/N8X1/compare-2050.png`: top row Mac / old Odin (M13) / **Odin HIER=off** (original stream); bottom row Odin wave64 / Mac (nearest stream).
2. `/Users/brad/dev/ssx3-work/N8X1/live-wave64-screens.png`: **live Odin screen**, menu + race.
3. `/Users/brad/dev/ssx3-work/N8X1/live-off-screens.png`: live Odin screen, off.
4. `/Users/brad/dev/ssx3-work/N8X1/runs/odin-a2-nearest-wave128/frames/vq-002050.ppm`: wave128 still black.

## Next

1. Take the clean diff into the renderer the E/N lanes build (one APK), then re-run the N8D2 live route with no `PS2X_PGS_HIER` env.
2. Build the wave64-vs-wave128 subgroup probe to name the Turnip/ir3 fault (hypothesis above).
3. Exact bilinear: replace the hardware linear sample in `ubershader.comp:1224-1227` with a 4-tap nearest fetch plus 1/16 integer weights. This needs the slangmosh SPIR-V regeneration, which isn't available in this tree (shaders ship precompiled in `slangmosh.hpp`). It would make Mac and Odin bit-identical on bilinear textures, but it also changes the Mac ground truth, so re-baseline.
4. Tick665-class STQ triangle differences (nearest filtering, per-primitive): a float interpolation/snap precision study, low priority.
5. Clean speed number with diagnostics compiled out, wave64 vs off, labelled per the ledger rules.

## Gaps

- Hypotheses above are labelled; no Turnip source was read (flag names came from the pinned `.so` strings).
- The Mac `HIER=on` run doesn't prove hierarchical binning engaged there.
- No live run of build 2's default path; the live runs used build 1 with env knobs.
- Live-run rate lines are diagnostic; the wave64 live run's rate is void (per-present dumps).
- No `GameThread` log line captured; host dump PNGs not pulled.
- Left on the Odin: knob APK `19fed514…` installed, original `ps2x.env` restored, lease free, my `n8x1-*` files under `<FILES>` (≈1.2 GB, including `n8x1-nearest-full.gs`). bytesize: `~/n8x1/root` (7.5 GB build root). Mac scratch `~/dev/ssx3-work/N8X1` 3.1 GB. Disk budget 161.4/200 GB.
