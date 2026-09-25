# DK1 — paraLLEl half-brightness: PS2 alpha blended over black (fixed)

Worker: Muse Code, brief `local/muse/prompts/DK1.md`. 2 h box.

## Result

The ~50 % dimness is the shared presenter alpha-blending the game quad
over black while the parallel backend hands it PS2 alpha (0x80 rows).
One fix on fork branch `dk1-bright` (`6cba433`, from fork `ssx3`
`0ed07c4`): `Present` forces presentation alpha to 255, mirroring the
CPU backend's `normalizePresentationAlpha`. iPad validation (one
fresh-card launch, live container path): post-fix parallel renders at
**0.98–1.04× the CPU backend** (pre-fix: 0.54–0.57×), all three shots,
0 FATAL.

## 1. Present-path trace (same code on all platforms)

| Stage | File:line (fork @ `0ed07c4`) |
| --- | --- |
| paraLLEl scanout | `ps2_gs_parallel_backend.cpp:260` `m_iface->vsync(vsync)` → `parallel-gs/gs/gs_interface.cpp:4636` → `gs_renderer.cpp:4281` |
| GPU→CPU readback | `ps2_gs_parallel_backend.cpp:280-312` (`copy_image_to_buffer`, CachedHost) |
| Stride copy (**fix here**) | `ps2_gs_parallel_backend.cpp:305-322` → `PresentationFrame` (640-px stride) |
| Latch / copy | `gs_frontend.cpp:937` `latchHostPresentationFrame` / `:1025` `copyLatchedHostPresentationFrame` (byte copy, no alpha touch) |
| Upload | `ps2_runtime.cpp:707` `UploadFrame` → `:823` `UpdateTexture(tex, …)` (R8G8B8A8) |
| Draw | `ps2_runtime.cpp:3926-3948`: `BeginDrawing; ClearBackground(BLACK); DrawTexturePro(frameTex, …, WHITE);` default blend, `:3997` `EndDrawing` |

Platform differences: **none in fork code**. The run loop, upload and
draw call are fully shared; `ps2_android_runtime.cpp` (51 lines) is an
env shim only. raylib is 5.5 everywhere (`ps2xRuntime/CMakeLists.txt:85-104`):
Desktop GL 3.3 on Mac, SDL+GLES2 on iOS, GLES on Android — all default
to `BLEND_ALPHA` (`SRC_ALPHA, ONE_MINUS_SRC_ALPHA`) with the stock
`texture * color` shader. So texel alpha 0x80 over black renders
0.502× everywhere; the "Mac normal" evidence is an artifact of capture
point (below), not platform.

The contract gap: CPU `Present` **always** forces alpha 255
(`gs_cpu_backend.cpp:479` `normalizePresentationAlpha`, called at
`:1963` and `:1981`); parallel `Present` returned raw scanout alpha.

## 2. Measurements

Pre-present (Mac `dumpPresentationFrame` PNGs = `s_scratch`, before the
blend; F2 B1): 512×448 RGBA, RGB correct, alpha exactly two values —
**128 on 50.2 % of pixels, 255 on 49.8 %**, in strictly alternating
rows (even rows 128 including edge row 447, odd rows 255; RGB means
identical on both row sets). Same pattern on menu (`snap-001052t`) and
race (`snap-002090t`) snaps: structural, not content. F2's Mac snaps are
copies of `upload-latest.png` (`f2_boot.py` snapshotter), i.e.
pre-blend — the Mac window itself was never captured.

Post-present (device screenshots, after the blend):

| Pair | Game-region ratio (par ÷ ref) | Ripple? |
| --- | --- | --- |
| Odin S1 sc01 (tick ~2100) ÷ Mac pre-present (tick 2096) | 0.527 / 0.517 / 0.504 per channel | No (row lag-1 autocorr 0.99, no ~2.4-row peak) |
| I33 iPad pre-fix parallel ÷ CPU, game-center bright px, t1090/t1810/t2100 | median 0.543 / 0.551, peak 0.48–0.53, uniform across rows | No |
| I33 iPad pre-fix parallel ÷ CPU, whole-image mean | ~0.83 (contaminated by vpad-overlay pixels — see below) | — |

So on device the effective blend is uniform ≈0.5×. The iPad shots need
care: the app runs in a portrait-compat window (I32/F1) with another
app's static form around it (79.8 % of pixels bit-identical across
backends/scenes) plus the translucent vpad overlay; only tight
game-center pixels (rows 600–1050, cols 950–1450) give a clean number.

Open question (G5): Mac scanout alpha alternates by row while iOS/Odin
behave as uniform 0x80. Prime suspect is paraLLEl's dynamic
`force_progressive` toggle on complex scanmasks
(`gs_interface.cpp:4641-4647`): weave (`weave.frag`: field rows keep
VRAM alpha, blended rows hardcode 1.0) reproduces the Mac pattern
exactly, including the row-447 edge case. Driver variance is the
alternative. Either way the fix normalizes both patterns; no
paraLLEl-side change needed.

## 3. The fix (one mechanism, one commit)

`6cba433 [DK1] parallel Present: normalize presentation alpha to opaque`
on `dk1-bright` (+13/−2, `ps2_gs_parallel_backend.cpp`, folded into the
readback copy loop — no extra pass; padding past `out.width` untouched,
same as the CPU backend). Alternatives rejected: blend-off in the run
loop (blend-state save/restore around vpad + debug UI, riskier; leaves
semi-transparent pixels in dumps/shadow), RGB texture repack (more
invasive). Shadow `compareRgb` is RGB-only (`ps2_gs_shadow.cpp:316`),
so PSNR/diff receipts are unaffected (only `par_fnv` values change).
Runner-dir check empty before/after; never pushed.

Validation build: cherry-pick `9e21edf` onto `dk1-ios` in the I33
worktree (validation only; worktree restored to `i33-pgs-ios` @
`0ed07c4`, clean), incremental iOS device rebuild in I33's build dir.

## 4. iPad validation (before/after, all viewed)

| Item | Pin |
| --- | --- |
| Fix commit | `6cba433` (validation: `9e21edf` = same diff) |
| Device binary pre-sign | SHA `fdd26c59…` (×2) |
| Device binary signed | SHA `01067ef4…` (×2) |
| Install | iPad seq 1924, bundle `A02FC93C-…` (rotated); `deploy-ios.sh ipad` SKIP + 7 OKs |
| Probe | Data `F54F8675-…`, bundle path matches install URL |
| Launch | fresh card `mc-dk1`, I26-FAST (484 chars), parallel, 83 s wall, ticks 1202/1833/2127, 0 FATAL, terminated, 0 procs left |

Post-fix parallel ÷ I33 CPU (game-center bright pixels):

| Shot | Post ÷ CPU (RGB) | Pre ÷ CPU (RGB) |
| --- | --- | --- |
| t1090 Select Event (tick 1202 vs CPU 1101) | 0.992 / 0.996 / 0.993 | 0.569 / 0.565 / 0.557 |
| t1810 race (1833 vs 1825) | 1.002 / 0.980 / 0.992 | 0.559 / 0.538 / 0.534 |
| t2100 race (2127 vs 2116) | 1.036 / 1.016 / 1.023 | 0.569 / 0.549 / 0.543 |

Viewed (ASCII + stats): t1090 shows the Select Event card matching the
CPU shot's structure at full brightness; t1810/t2100 show bright race
scenes. Menu tick 1202 vs pre-fix parallel 1201: 1 tick apart, same
frame — the before/after is a pure brightness A/B.

## 5. Exact commands

```sh
# Fix (DK1 worktree, branch dk1-bright from 0ed07c4)
git worktree add ~/dev/ssx3-work/DK1/PS2Recomp -b dk1-bright 0ed07c4
# … edit ps2_gs_parallel_backend.cpp … then commit (trailer Orchestrated-By: Muse Code)
# Validation build (borrow I33 worktree + build dir, restore after)
git -C ~/dev/ssx3-work/I33/PS2Recomp checkout -b dk1-ios && git cherry-pick 6cba433
cmake --build ~/dev/ssx3-work/I33/ios/ios-runtime-device-release --config Release \
  --target ps2EntryRunner -- -jobs 8        # BUILD SUCCEEDED
git -C ~/dev/ssx3-work/I33/PS2Recomp checkout i33-pgs-ios
# Stage/sign/install/probe/run (DK1 scratch; ISO via clonefile, ~0 bytes)
bash ~/dev/ssx3-work/DK1/ios/dk1-ios.sh stage sign install_ipad
bash ~/dev/ssx3/local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/DK1/ios/ipad-probe.sh  # live Data/Bundle paths
# env-dk1.json: live paths + fresh mc-dk1 + route + VSYNC_RATE_LOG + parallel
bash ~/dev/ssx3-work/DK1/ios/ipad-run.sh ~/dev/ssx3-work/DK1/ios/run-ipad-dk1 \
  ~/dev/ssx3-work/DK1/ios/env-dk1.json '1090 1810 2100'
```

Analysis scripts: `/tmp/dk1_stats.py`, `/tmp/dk1_alpha_map.py`,
`/tmp/dk1_ripple.py`, `/tmp/dk1_ipad_ab.py`, `/tmp/dk1_thumb.py`,
`/tmp/dk1_ipad_diff.py`, `/tmp/dk1_ipad_geo.py`, `/tmp/dk1_ipad_hist.py`,
`/tmp/dk1_after.py`, `/tmp/dk1_view.py` (run with the AU4 venv python,
read-only). Scratch: `~/dev/ssx3-work/DK1/` 3.0 GB (worktree + staged
.app); `~/dev/ssx3-work/DK1/ios/` holds `dk1-ios.sh`, logs, staged SHAs,
probe + validation runs.

## 6. Budgets and gaps

~2 h box used. Builds: 1 incremental iOS device (1 TU + link). Boots: 1
probe + 1 validation (< 420 s each). iPhone untouched per brief.

- G1. Odin: not validated — NP1 holds the lease (read-only check;
  battery 49 % + AC would've passed). Same shared code path, so the fix
  applies; needs an APK rebuild + run.
- G2. Android compile check: not run (plain-C++ change, iOS TU clean;
  bytesize untouched).
- G3. iPhone: nothing per brief (orchestrator installs a combined build).
- G4. Mac window never directly observed (all Mac evidence is
  pre-present dumps); fixed by construction via the shared path.
- G5. Mac-vs-device scanout alpha pattern difference unexplained (see
  §2 suspect); doesn't affect the fix.
- G6. One iPad run (no drift cancellation); pace is diagnostic, not a
  speed number.
- G7. Share tier (`/Volumes/share`) not mounted: no receipt mirror.
- Disk: global budget already **203.7/200 GB (OVER CAP) before DK1 wrote
  anything** (pre-existing; `disk_budget.sh` tail kept in scratch
  logs); DK1 added ~3.0 GB logical (ISO staged via clonefile).

## Recommended next action (orchestrator decides)

Fast-forward the `6cba433` fix to fork `ssx3` (runner-dir check already
empty) so the combined iPhone build and the next Odin APK pick it up;
close DK1 after an Odin screenshot confirms full brightness there.
