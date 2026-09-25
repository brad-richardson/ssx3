# HR1 — 4× super-sampling + double-resolution output, and presenting without the CPU copy

Worker: Claude Code (Opus 5.5), exploratory, brief `local/muse/prompts/HR1.md`. Mac mini + iPad
Air M2 (no iPhone, no Odin). Time box 3 h of active time (13:17–13:57, paused for Brad, resumed
15:15). Running notes: `NOTEBOOK.md`.

## Outcome

1. **The knobs work and change nothing in the guest.** `PS2X_PGS_SSAA=4` +
   `PS2X_PGS_HIRES_SCANOUT=1` gives a 1024×896 frame. Det-hash for ticks 1..2400 is identical at
   1×, 4× and 4×+hi-res. The race looks visibly sharper and no SSX 3 effect breaks. SSX 3 draws
   the race straight into the buffer it scans out, so paraLLEl's "a blit loses the SSAA" caveat
   doesn't apply.
2. **What 4× costs is mostly a wait, not a copy.** The CPU copies are small: 0.1–0.45 ms per
   frame at 1024×896. The real cost is that the backend calls `wait_idle()` on every present, so
   the GsWorker waits for the whole GPU to finish. The GsWorker queue then fills up and blocks
   the GameThread (backpressure in `GsWorker::enqueue`). On the iPad, 4×+hi-res costs −9 % in
   the race for that reason alone.
3. **Pipelined present fixes that on every platform.** `PS2X_PGS_PRESENT_PIPELINE=1` (fork
   `4825123`) shows each frame one frame later and never drains the GPU. On the iPad, 4×+hi-res
   pipelined runs at 10.40–10.49 vs/s. That's faster than today's 1× (10.31) and only −4 %
   against 1× pipelined (10.90).
4. **Option A zero-copy works on the Mac.** `PS2X_PRESENT_ZERO_COPY=1` (fork `fb3dca0`) sends
   the frame through an IOSurface into GL. What GL displays is RGB byte-identical to the readback
   frame at t2100, and the path has no CPU pixel copy. Plans for iOS and Android are below.
5. **paraLLEl caps SSAA at 4× on Apple GPUs.** MoltenVK reports `requiredSubgroupSizeStages =
   None` and subgroup sizes 4..32, so `get_max_supported_super_sampling()` returns X4 and a
   request for 8× or 16× quietly runs at 4×. Adreno under Turnip may allow 8× and 16×.

## Fork changes (branch `hr1-ssaa` from fork `ssx3` `ec2dbf1`, not pushed)

| Commit | What | Files (+/−) |
| --- | --- | --- |
| `cf7c0df` | Knobs (all default off): `PS2X_PGS_SSAA=1\|2\|4\|8\|16`, `PS2X_PGS_SSAA_TEXTURES=1`, `PS2X_PGS_HIRES_SCANOUT=1`. Frames larger than 640×512 are packed at stride = width and the frontend infers that from the size, so no header changes (generated code includes `gs_frontend.h`, and a header edit recompiles ~300 units). The presenter grows the raylib texture once and uploads with `UpdateTextureRec`. Also `copy_ms_avg` in the stats line, and `PS2X_THREAD_CPU_LOG=1` (Apple: per-thread CPU with names, plus the main thread's latch-wait vs upload split) | 3 files +159/−7 |
| `fb3dca0` | Prototype, `PS2X_PRESENT_ZERO_COPY=1` (macOS): turns on `VK_EXT_metal_objects`, blits into 3 rotating IOSurface-backed BGRA8 images, and the GL side binds each with `CGLTexImageIOSurface2D` and copies it into the frame texture with `glBlitFramebuffer`, with an alpha swizzle of ONE. `PS2X_PRESENT_SHARE_DUMP_TICKS` saves the GL texture for checking | 5 files +342/−1 |
| `4825123` | `PS2X_PGS_PRESENT_PIPELINE=1`: 2 persistent readback buffers, each with its own fence, delivering the previous frame; the zero-copy path publishes the previous slot | 1 file |

Total `git diff --stat ec2dbf1 4825123`: 6 files, +578/−17. The suite passes **642/642** on each
commit (run from the worktree root). The runner-dir check (`git diff 14b1e5cb -- ps2xRuntime/src/runner`)
is empty. Nothing was pushed and the paraLLEl fork is unchanged: I use `19d93b2` as it is.

Binaries (`~/dev/ssx3-work/HR1/bin`, two matching SHA reads each): `runner-clean` `2ece529e…`
(cf7c0df), `runner-det` `93afd709…` (cf7c0df, det-hash tap), `runner-zc` `dce52a0a…` (fb3dca0),
**`runner-hr1` `15c5348d…` (4825123, used for every Mac speed number)**. iOS: device binary
`c8050cae…`, signed `5c897acd…` (4825123), installed on the iPad (seq 1948).

## Correctness

- **Det-hash**, runner-det, one slot each, I26-FAST to t2400: `gb8_hashdiff.py` gives
  `first_diff=None` for 1× vs 4× and for 1× vs 4×+hi-res. Tick 7 of det-1x shows as "missing"
  only because the `[gs-path]` line interleaved with it. I extracted it by hand and its md5 is
  identical across all three runs.
- **Scanout size**: 1280×896 at tick 40, then 1024×896 from tick 43 (`[gs:parallel] scanout
  size`). On the iPad it's 640×448 then 512×448 at 1×, and the same doubled at 4×+hi-res.
- **Zero-copy image**: at Select Peak (t1091) it's upright, colors are right, and brightness is
  full. With pipelining, the GL texture at t2100 is **RGB byte-identical** to the readback frame
  (md5 `e56d4c59…` for both).
- **Pipelined latency**: exactly one frame. The trick counter reads 210 where the sync frame
  reads 220 at the same tick.

## Frames (viewed; send-ready PNGs in `~/dev/ssx3-work/HR1/compare/`)

Each file puts 1× (bilinear to 1024×896, the way the phone stretches it) | 4× (same) |
4×+hi-res (native 1024×896) side by side. The frames come from the det boots at the same ticks.

| File | What it shows |
| --- | --- |
| `side-2100.png`, `side-2380.png` | Whole race frames. Same scene; spray and fog look the same in all three |
| `zoom-2100-slope.png` (**send**) | 1× has a stair-stepped slope edge. 4× is smooth but softer overall. 4×+hi-res has finer trees and a sharper edge; steps remain but are half the size, because each super-sample becomes an output pixel (2× resolution, no AA) |
| `zoom-2380-tree.png` (**send**) | Tree and mountain texture: 4×+hi-res is clearly crisper |
| `zoom-2100-hud2nd.png` (**send**) | HUD "2ND/2": 4×+hi-res has crisper outlines |
| `crop-2100-trees.png` | Tree line, snowball, spiral gauge |
| `crop-1090-text.png` | Select Peak menu: nearly identical at every setting (2D); hi-res text edges slightly crisper |
| `ipad-crop-2100.png` (**send**) | iPad screen (the game is ~1180×660 device px in the compat window), 1× vs 4×+hi-res. Different moments, so judge sharpness only |

Notes: in the snow shadows at hi-res there's a faint regular pattern (dither or texture at 2×,
minor). The thin vertical pink line near x≈217 at t2100 is present at every setting and on the
iPad, so it predates HR1 and isn't caused by the knobs. **No broken effect**, so no stop rule fired.

## Cost

### Mac mini M5 Pro, speed (exclusive hold, `PS2X_UNPACED=1`, sound on, runner-hr1, quiet host)

Race window t1800–2450, mean of the 5 s `[vsync-rate]` samples. Per-thread CPU % comes from the
paired `[thread-cpu]` lines over the same window; "other" means MoltenVK/Granite workers, audio
and the NSEvent thread. Receipt: `mac-cost.md`.

HOLD2_TABLE

`present`, `readback` and `copy` are the backend averages over the whole run. `latch` is how long
the main thread is blocked per new frame in `latchHostPresentationFrame`: the RPC to the GsWorker,
which also covers any queued GIF work ahead of it. `upload` is the main thread's own copy plus the
GL upload.

### iPad Air M2 (diagnostic pace: one launch per config, console capture, fresh card, I26-FAST)

Receipt: `ipad-cost.md`.

| Config | Race vs/s (×) | GameThread busy | GsWorker CPU | Latch ms/frame | Present / readback / copy ms |
| --- | --- | --- | --- | --- | --- |
| 1× sync (today) | 10.31 (0.172×) | 91 % | 8 % | 14.9 | 10.7 / 8.1 / 0.13 |
| 1× pipelined | 10.90 (0.182×) | 98 % | 9 % | 4.6 | 2.3 / 0.03 / 0.13 |
| 4×+hi-res sync | 9.34 / 9.26 (0.156×) | 82 % | 9 % | 25.4 | 16.1 / 9.8 / 0.41 |
| **4×+hi-res pipelined** | **10.49 / 10.40 (0.174×)** | **94 %** | 9 % | 10.2 | 4.9 / 0.03 / 0.44 |

On the iPad, both the readback and the 4× GPU cost sit on the GsWorker as GPU wait. It uses only
8–9 % CPU, yet in sync mode it holds the GameThread back by ~9 % through queue backpressure.
Pipelining takes all of that back.

Where the readback lands, per thread: the GPU→host copy and the `wait_idle` run on the
**GsWorker**, plus the stride/alpha copy (≤ 0.45 ms). The **main thread** blocks on the latch RPC,
then does one or two more copies and the GL upload (0.2–0.9 ms per frame at 1024×896). The
**GameThread** does no copying at all, but it stalls whenever the GsWorker queue is full.

## Zero-copy plan (Brad chose option A; B is parked and sized below)

Take pipelined present first. It's portable and small, and it removes the cost that actually
hurts: the GPU drain. What zero-copy still saves after that is ≤ ~1 ms of CPU per frame at
1024×896 (on the Mac: GsWorker copy 0.25 ms plus main upload 0.6 ms), and ~11 MB of memory
traffic per frame. That matters for a 120 Hz budget (8.3 ms) and on the Odin's shared memory bus,
but it's second in line.

| Platform | Option A route | State / effort | Risks |
| --- | --- | --- | --- |
| **macOS** | `VK_EXT_metal_objects` IOSurface export → `CGLTexImageIOSurface2D` (rect texture) → `glBlitFramebuffer` into the raylib texture, alpha via `GL_TEXTURE_SWIZZLE_A` | **Prototype works** (`fb3dca0` + pipelined `4825123`). To productize, ~0.5 day: make the optional readback for dumps/shadow explicit, and free old surfaces on resize (a graveyard today) | GL is deprecated on macOS, but it still works |
| **iOS** | Same Vulkan side (MoltenVK 1.4.2 has the extension). GLES side: `CVPixelBufferCreateWithIOSurface` → `CVOpenGLESTextureCacheCreateTextureFromImage` (GL_TEXTURE_2D, BGRA) with the SDL EAGL context (`.mm` file). Wrap the texture id as a raylib `Texture2D` and draw it directly (no blit). GLES2 has no swizzle, so draw the game quad with blending off (flush the batch around it). Safer variant: allocate the CVPixelBuffer ourselves (IOSurface + Metal + GLES compatible) and import it into Vulkan with `VkImportMetalIOSurfaceInfoEXT` | ~1 day including iPad validation | IOSurface properties CoreVideo accepts; EAGL context access through SDL; OpenGL ES is deprecated on iOS (still works) |
| **Android (Odin)** | `AHardwareBuffer` (RGBA8, GPU_SAMPLED \| GPU_COLOR_OUTPUT) imported into Turnip (`VK_ANDROID_external_memory_android_hardware_buffer`), then into the Adreno GLES driver via `eglGetNativeClientBufferANDROID` + `EGL_NATIVE_BUFFER_ANDROID` + `glEGLImageTargetTexture2DOES`, with a fence before GLES samples it (pipelined) | ~2–3 days plus device risk | **Our app-local Turnip shim makes `hw_get_module` fail**, so Turnip's `u_gralloc` may not know the buffer layout (UBWC tiling) that the Adreno GLES driver uses. Try a linear allocation first (add `CPU_READ_RARELY` usage) and prove it with a pixel compare on the Odin |

**Option B** (Vulkan presents directly, raylib dropped or kept only for input/audio; parked): a
Granite WSI swapchain on a `CAMetalLayer` (Mac/iOS via SDL2 `SDL_Vulkan_CreateSurface`) and on an
`ANativeWindow` (Android). The virtual pad, labels and debug text would need to be redrawn in
Vulkan. Standalone paraLLEl builds only Granite's Vulkan core, so that means a small quad/text
pipeline plus a glyph atlas. Input and lifecycle would move to SDL2 on all three platforms, or
stay on raylib with raylib's GL disabled, which it doesn't support cleanly. **~1.5–2 weeks**, and
riskiest on Android: Turnip's Android WSI allocates swapchain images through gralloc, the same
dependency as A. What it buys: no GL anywhere (both Apple GL stacks are deprecated), no
intermediate texture, and precise present control for 120 Hz (`VK_KHR_present_wait`/`present_id`,
`VK_GOOGLE_display_timing` on MoltenVK/Android, explicit FIFO at 120 Hz on ProMotion/120 Hz
panels). Revisit it when the 120 Hz simulation work needs precise present timing.

## Recommended defaults (orchestrator/Brad decide)

| Device | Recommendation | Why |
| --- | --- | --- |
| Mac | 4×+hi-res + pipelined (see the hold 2 rows) | Quiet-host cost is small; pixels are clearly better |
| iPad / iPhone | **4×+hi-res + pipelined** | Measured on the iPad: faster than today's 1× sync and −4 % against 1× pipelined. The A18 Pro in the iPhone should do at least as well (unmeasured; install-only rule) |
| Odin | Pipelined now (lane N measures it); 4×+hi-res as the candidate, **after** an Odin run measuring race rate and GPU busy | The Odin GPU runs 15–25 % busy at 1× (N11/NP1), and 4× means roughly 4× the per-pixel raster work. Pipelining should matter even more there, because the Turnip driver's CPU cost already sits on the GsWorker |

Brad's GameCube setting (3× internal + ~75 % of display resolution) against paraLLEl: paraLLEl
only outputs at 1× or 2× linear. There's no 3×. X4+hi-res (2×2 samples, 1024×896) is the closest
match: 896 lines is ~83 % of the Odin's 1080-line panel, near his 75 % rule. X8/X16 would add AA
on top of the 2× output, but on Apple it's capped at X4 (above), and on the Odin only a device run
can show the cost.

## Exact commands

```sh
# worktrees + builds (from ~/dev/ssx3-work/HR1)
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/HR1/PS2Recomp -b hr1-ssaa ec2dbf1
git -C ~/dev/PS2Recomp worktree add --detach ~/dev/ssx3-work/HR1/PS2Recomp-det cf7c0df
cmake -S PS2Recomp -B build -G Ninja <F3 recipe: Release, Homebrew clang, codegen-ssx3, BUILD_TEST=ON,
  logs/taps/det OFF, PS2X_GS_SHADOW_PARALLEL=ON, PS2X_PARALLEL_GS_SOURCE_DIR=~/dev/ssx3-work/F2/parallel-gs (19d93b2)>
nice -n 10 cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)            # 642/642 at cf7c0df, fb3dca0, 4825123
cmake -S PS2Recomp-det -B build-det … -DPS2X_ENABLE_DET_HASH_TAP=ON -DPS2X_BUILD_TEST=OFF
clang -O2 -o bin/threadcpu ~/dev/ssx3/local/research/HR1/threadcpu.c
# det + frames (one slot each)
python3 hr1_boot.py --mode det --backend parallel --runner bin/runner-det --label det-1x --dump-ticks 1090,2100,2380 --stop-tick 2400
python3 hr1_boot.py … --label det-4x --ssaa 4 …;  … --label det-4x-hires --ssaa 4 --hires …
python3 ../GB8/gb8_hashdiff.py --base run/det-1x --cand run/det-4x(-hires)
# Mac speed holds (exclusive, <= 5 min each)
python3 hr1_hold.py "spd1-A-1x:" "spd1-B-4xhr:--ssaa 4 --hires" "spd1-C-4xhr-zc:--ssaa 4 --hires --extra-env PS2X_PRESENT_ZERO_COPY=1"
python3 hr1_hold.py "spd2-D-4xhr-pipe:--ssaa 4 --hires --extra-env PS2X_PGS_PRESENT_PIPELINE=1" \
  "spd2-E-4xhr-zc-pipe:--ssaa 4 --hires --extra-env PS2X_PRESENT_ZERO_COPY=1,PS2X_PGS_PRESENT_PIPELINE=1" "spd2-A-1x:"
python3 hr1_cost.py A=run/spd1-A-1x/boot.log …
# iPad (HR1/ios: copy of F3 build-install.sh with the HR1 worktree + build dir)
bash build-install.sh preflight configure_device build_device stage_device sign install_ipad
bash ~/dev/ssx3/local/research/I31/deploy-ios.sh ipad && bash ipad-probe.sh
bash ipad-run.sh run-ipad-<cfg> env-<cfg>.json '1090 1810 2100 2400'   # env: route + fresh card + THREAD_CPU_LOG (+ knobs)
```

Scripts committed here: `hr1_boot.py` (F3 driver + knobs, `--dump-ticks`, diag mode, per-thread
samples), `hr1_hold.py` (one exclusive hold around ≤ 3 speed boots), `hr1_cost.py` (race rate +
per-thread table), `threadcpu.c` (libproc per-thread CPU with names). Scratch
`~/dev/ssx3-work/HR1/` (worktrees, 3 build dirs, runs, compare/).

## Budgets and gaps

- Builds: Mac clean ×4 incremental after the first, det ×1, iOS device ×2 (full plus
  incremental). Boots: 3 det, 5 diag smokes, speed holds (see table), 7 iPad launches (plus 2
  probes and 1 devicectl transport failure where the app never started). Nothing exceeded 600 s.
- G1. **No Odin run** (the brief forbids it). The Odin cost of 4× and the Android zero-copy
  feasibility (the gralloc layout) are unmeasured.
- G2. iPad numbers are diagnostic pace: one or two launches per config, no drift cancellation.
  The second decimal is noise.
- G3. Mac speed: one run per config per hold, ABBA over two holds where the slots allowed (see
  table notes).
- G4. The `[gs:parallel] quality` line prints the **requested** SSAA, not paraLLEl's clamped
  value. On Apple, `ssaa=16` really runs at 4×. It should print the effective rate
  (`GSRenderer::get_max_supported_super_sampling`) before any fold.
- G5. The zero-copy path skips frame dumps, the G44 shadow compare and diagnostic presents. It's
  a prototype: surfaces from old sizes are kept (a graveyard), and the GL side is macOS-only.
- G6. Pipelined present adds one frame of display latency, which the input-latency budget needs
  to count.
- G7. iPhone: nothing done (install-only rule; no install in HR1). The iPad keeps the HR1
  `4825123` build, which behaves like F3 when all knobs are off, with Brad's save and env
  redeployed.
- G8. The 4×+hi-res image still stair-steps (2× resolution, no AA), and there's a faint regular
  pattern in hi-res snow shadows. `PS2X_PGS_SSAA_TEXTURES=1` wasn't tried.

## Recommended next action (orchestrator decides)

1. Fold `4825123`'s pipelined present, the knobs (`cf7c0df`) and a fix for G4 onto fork `ssx3`.
   Make pipeline + 4×+hi-res the iOS bundled default after one iPhone-class check.
2. Odin brief (lane N): 1× sync vs 1× pipelined vs 4×+hi-res pipelined, with race rate, GPU busy
   and per-thread top.
3. Zero-copy A on iOS next (~1 day), then an Android AHardwareBuffer spike on the Odin with a
   pixel-compare gate.
