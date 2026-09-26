# VK1 — present straight from Vulkan (option B): Odin cost split, design, Odin prototype

Worker: Claude Code (Opus 5.5), Opus spike approved by Brad 09-25, brief `local/muse/prompts/VK1.md`.
Worktrees `~/dev/ssx3-work/VK1/{PS2Recomp,parallel-gs}` on local branches `vk1-present`
(PS2Recomp from fork `ssx3` `a3efbfe`, paraLLEl-GS `19d93b2`, Granite `166ba21a`). Never pushed.

Status: **done; 8/8 Odin launches, 2/6 Android builds. Brad's F5 play build restored exactly.**
Design committed first (`573c6c5e`). Fork commits local only: `b2640de`, `b5d2c0d` (branch
`vk1-present` from `a3efbfe`).

## Answers (tables below; the orchestrator decides)

1. **Where the Odin's 4× cost goes** (early race window, per guest frame): 4×+hi-res adds
   +33.5 ms of wall, of which **+31 ms is GameThread stall**. The readback/copy/upload path is
   small: ~1.9 ms on the GsWorker (+1.3 over 1×) and +3.9 ms of GLES upload on the main thread,
   which is off the GameThread's chain. **Turnip's CPU is flat** (0.35 → 0.43 % of samples). What
   scales is **wall time inside paraLLEl's `flush()`/`vsync()` on the GsWorker (7.6 → 19.4 ms per
   present, little CPU)** with the GPU 37 → 52 % busy: GPU time serialized behind a CPU wait.
   Suspect (untested): `flush_submit()` → `next_frame_context()` on every flush with only 4
   Granite frame contexts.
2. **What option B takes per platform:** on the Odin, Turnip as we load it has **no Vulkan WSI**,
   so "present from Vulkan" = our own swapchain of AHardwareBuffers queued with
   `ASurfaceTransaction` on a child SurfaceControl. That hybrid is **prototyped here**: ~2–3 days
   to productize, +3–4 days for full B (Vulkan overlay, no GL). Mac hybrid ~1–1.5 days (low value:
   option A already costs nothing there); iOS hybrid ~2–3 days. All three hybrid ≈ 1–1.5 weeks;
   full B everywhere ≈ HR1's 1.5–2 weeks. Per-platform plan, lifecycle, 120 Hz hooks and risks:
   stage 2.
3. **The Odin prototype works, matches pixels, and is speed-neutral.** The buffer
   SurfaceFlinger gets is **byte-identical** (RGB, read through gralloc) to the readback frame at
   the same present (t1100 and t2100, two runs). Background/foreground, rotation and the pad
   check pass. Mac det-hash is identical 1..2400 with the knob off and on. Knob on:
   **1× 14.55 vs/s = 0.243× (F5 A: 0.244×), 4×+hi-res 10.07 = 0.168× (F5 B: 0.168×)**. B doesn't
   recover the 31 %, as answer 1 predicts. What it **does** change is the picture: today's GL
   path shows every frame at **360 lines in a bordered 1543×868 box** (raylib's 640×448 logical
   screen). The Vulkan layer fills 1920×1080 from the full-size buffer, so 4×+hi-res reaches the
   screen at 896 lines. It also removes the main thread's GLES upload.

## Stage 1 — Odin cost split (F5 play build `4ff81032…`, no code)

Two launches on the installed F5 APK (fork `a3efbfe`), Brad's play keys + I26-FAST, sound on,
`PS2X_UNPACED=1`, pipelined present, cool-down before each (thermal 0, fixed 180 s). Per-thread
CPU from `/proc/<pid>/task/*/stat` (utime+stime) over an **unprofiled** race window (ticks
~1815→2390), then a 30 s `simpleperf record -g --app` from tick ~2430 (N11's command),
symbolized on the mini with NDK r30's host simpleperf + F5's unstripped `.so` (Build ID
`e39b09b3…`, same as the APK). GPU busy = kgsl `gpubusy` over the same tick window. Backend
per-present numbers are window deltas of the cumulative `[gs:parallel] periodic` lines
(`stage1.py`). Receipts: `logs/P1`, `logs/P2`, `reports/P{1,2}-*.txt`.

| ms per guest frame (early race window) | P1: 1× pipelined | P2: 4×+hi-res pipelined | Δ |
| --- | ---: | ---: | ---: |
| Window | ticks 1815→2395, 43.8 s | ticks 1833→2381, 59.7 s | |
| **Wall** (rate) | **75.5** (13.24 vs/s, 0.221×) | **109.0** (9.18 vs/s, 0.153×) | **+33.5** (B/A 0.693; F5: 0.688) |
| GameThread CPU | 54.6 (72 % busy) | 57.1 (52 % busy) | +2.6 |
| **GameThread stall** (wall − CPU) | **20.9** | **51.9** | **+31.0** |
| GsWorker CPU | 13.5 | 15.5 | +2.0 |
| – `Present()` inclusive (readback copy + alpha loop + submit), profile share × CPU | 0.54 (4.0 %) | 1.88 (12.2 %) | +1.3 |
| Backend `readback_ms` per present (our fence waits + map) | 0.16 | 0.30 | +0.14 |
| Backend `copy_ms` per present (stride/alpha copy) | 0.31 | 1.22 | +0.91 |
| Backend `present_ms` per present (wall) | 8.02 | 20.89 | +12.9 |
| – **inside paraLLEl `flush()`+`vsync()`** (present − readback − copy; wall, little CPU) | **7.55** | **19.37** | **+11.8** |
| Main thread CPU (latch RPC, copy, **GLES upload**, raylib loop) | 4.55 | 8.49 | +3.9 |
| Turnip CPU (`libvulkan_freedreno.so`, % of all samples) | 0.35 % | 0.43 % | ≈ 0 |
| Adreno GLES (main thread, % of all samples) | 0.40 % | 1.19 % | |
| GPU busy (kgsl, window mean) | 36.6 % (n=7) | 51.6 % (n=11) | +15 pts |

Per present ≈ per guest frame: the main loop latches once per new tick (P1: 900 presents over
~900 ticks; P2: 900 over ~1110 ticks, so P2's per-present rows are ~0.8 of a frame).

**Answer to (1).** Of the +33.5 ms per frame that 4×+hi-res costs, **+31 ms is GameThread
stall**, not GameThread work. The readback/copy/upload path is small and mostly off the
critical chain: on the GsWorker it is ~1.9 ms/frame at 4× (+1.3 over 1×); the GLES upload is on
the main thread (+3.9 ms), which only blocks itself in the latch RPC. **Turnip's CPU is flat**
(0.35 → 0.43 % of samples). The time that scales is **wall time inside paraLLEl's
`flush()`/`vsync()` on the GsWorker (7.6 → 19.4 ms per present, little CPU)**, with the GPU at
37 → 52 % busy: GPU time serialized into the GsWorker behind a CPU wait (H-gpu). A candidate
mechanism (not tested; out of scope): paraLLEl's `GSRenderer::flush_submit()` calls Granite's
`device->next_frame_context()` on **every** flush (`gs_renderer.cpp:1217`), and the backend
creates only **4 frame contexts** (`m_device->init_frame_contexts(4)`), so several flushes per
vsync make the GsWorker wait for GPU work only a few flushes old. Counting flushes per vsync
and trying more frame contexts is a one-knob experiment.

Predicted effect of option B on the 4× cost: it removes ≤ ~2 ms/frame from the GsWorker chain
(and ~4–8 ms of main-thread CPU off the chain), so **≤ ~2–5 %**, not the 31 %. Stage 3 measures it.

Also found (screen geometry of today's GL path on the Odin): raylib's Android "screen" is
**640×448 inside a 796×448 window buffer** that SurfaceFlinger upscales ×2.41 to 1920×1080
(`DISPLAY: Upscaling required … Screen size 640 x 448 … Viewport offsets 156, 0` in F5's R2
logcat). The presenter letterboxes SSX 3's 16:9 picture into that 640×448 screen, i.e.
**640×360**, so the game shows at **1543×868, centred with black borders** (F5 R2 `sc01`: 105 px
bands top and bottom) and **every frame is resampled to 360 lines before display** — 448-line
frames at 1× and the 1024×896 4×+hi-res frame alike. On the Odin, 4×+hi-res therefore buys
anti-aliasing but not resolution through the GL path. The Vulkan path hands SurfaceFlinger the
full-size buffer and fills the screen (below).

## Stage 2 — Design

### Facts the design rests on (checked 09-25)

| # | Fact | Evidence |
| --- | --- | --- |
| D1 | On Android we load Turnip **as a HAL module directly** (`dlopen("libvulkan_freedreno.so")` → `HMI` → `open("vulkan0")` → `getInstanceProcAddr`), not through the system Vulkan loader. | fork `ps2_gs_parallel_backend.cpp` `initTurnipLoader()` |
| D2 | The bundled Turnip (Mesa **26.3.0-devel** `c501e1d16e`) has **no Android WSI of its own**: no `ANativeWindow_*` imports, no `wsi_*` code; its only platform imports are `AHardwareBuffer_{allocate,acquire,release,describe,getNativeHandle,isSupported}`, `hw_get_module`, `sync_merge`, `sync_wait`. The `vkCreateAndroidSurfaceKHR`/`tu_*Swapchain*` strings are Mesa's generated extension/entrypoint tables. On Android, the swapchain is normally implemented by the **platform loader** (`libvulkan.so`) on top of the driver's `VK_ANDROID_native_buffer`. | `llvm-nm -D --undefined-only`, `strings` on the F5 APK's `lib/arm64-v8a/libvulkan_freedreno.so` (14,188,488 B) |
| D3 | So **a Vulkan swapchain on the Odin is not available as we load Turnip today**. The swapchain would need either the system loader (adrenotools-style namespace hook, and the platform swapchain then allocates through gralloc and imports into Turnip via `VK_ANDROID_native_buffer` → `u_gralloc` → the same `hw_get_module` dependency our shim breaks), or **our own swapchain**: AHardwareBuffers imported into Turnip (`VK_ANDROID_external_memory_android_hardware_buffer`) and queued to SurfaceFlinger with the public NDK `ASurfaceControl`/`ASurfaceTransaction_setBuffer` (API 29+). | D1, D2; NDK `surface_control.h` |
| D4 | The app is a `NativeActivity` (`hasCode="false"`), landscape-locked, `configChanges` covers orientation/screenSize (no relaunch on rotation). raylib 5.5 owns `android_main`, the EGL context and the window; it exposes `GetAndroidApp()`. | fork `android/app/src/main/AndroidManifest.xml`; raylib `rcore_android.c` |
| D5 | raylib's Android EGL config asks for R8G8B8 + depth 16 and **no alpha**, so the window's buffers are RGBX (opaque). A layer placed *under* the GL window can only show through if raylib gets an alpha config (a configure-time patch like the existing iOS DPI patch), the window format is set to RGBA (`ANativeActivity_setWindowFormat`; NativeActivity defaults to RGB_565, which makes the window layer opaque), and the overlay is drawn with premultiplied-correct alpha (`BLEND_CUSTOM_SEPARATE`, alpha `ONE, ONE_MINUS_SRC_ALPHA`). | raylib `InitGraphicsDevice()` |
| D6 | On the Odin the virtual pad is **off** (Brad's env has no `PS2X_VIRTUAL_PAD`; on Android it defaults off like desktop). raylib draws only the game quad; input comes from the hardware pad through raylib's input queue. | fork `ps2_runtime.cpp` `virtualPadWanted()`; env `a8d651a7…` keys (F5 Part 2) |
| D7 | The backend's `Present()` runs on the **GsWorker**, called through the main thread's latch RPC (`GS::latchHostPresentationFrame`), once per new guest tick the main loop sees. | fork `gs_frontend.cpp:937` |
| D8 | Odin 3: Android 15 (API 35), SoC `CQ8725S`, panel 1080×1920 (landscape 1920×1080) with **120 Hz** (mode 1, default) and 60 Hz modes. | `getprop`, `dumpsys display` (read-only, 09-25 19:4x) |
| D9 | The Apple zero-copy (option A) already works and costs nothing measurable on the M5 Pro / iPad (HR1); what option B adds on Apple is no GL (both GL stacks deprecated) and present-timing control. | HR1 REPORT |

### What "option B" means per platform

| | Hybrid (separate surface, raylib keeps the window) | Full B (Vulkan draws everything visible) |
| --- | --- | --- |
| **Android (Odin)** | A child `ASurfaceControl` of the NativeActivity window (`ASurfaceControl_createFromWindow`) carries the game. The GsWorker blits each scanout into one of 4 AHardwareBuffer-backed VkImages and queues it with `ASurfaceTransaction_setBuffer` + `setGeometry` (scaled by SurfaceFlinger/HWC, not by GL). **z = +1 (above the GL window)** when no overlay is drawn (the Odin default, D6): no raylib change at all. **z = −1 (under)** when the virtual pad/text is on: needs D5's raylib alpha patch + RGBA window format + premultiplied overlay blend. raylib keeps input, lifecycle, the EGL loop (clears black, no texture upload). | The same child layer (D3: there is no other present path without the system loader). The overlay (pad quads, labels, debug text) is drawn in Vulkan into the AHB before queueing; raylib's GL window stays as an input/lifecycle shell and stops drawing, or raylib is dropped for our own `android_native_app_glue` loop (input queue + AAudio already native). |
| **macOS** | A `CAMetalLayer` added to raylib's GLFW content view, MoltenVK swapchain (`VK_EXT_metal_surface`) presented from the GsWorker. Above the GL layer when no overlay (desktop default), under it with a transparent GL framebuffer (`GLFW_TRANSPARENT_FRAMEBUFFER`) when the dev pad is on. | Same layer, overlay in Vulkan, GLFW window without a GL context (`GLFW_NO_API`) — raylib can't do that, so input moves to GLFW/SDL directly. |
| **iOS** | A `CAMetalLayer` sublayer **under** SDL's `CAEAGLLayer` (the virtual pad is on by default on iOS, so the GL layer must be non-opaque with alpha 0 outside the pad); MoltenVK swapchain. | `SDL_WINDOW_METAL` + Vulkan surface, overlay in Vulkan, raylib's SDL platform replaced by SDL2 directly (input, lifecycle). |

### Lifecycle, rotation, pacing (per platform)

| Topic | Android | macOS | iOS |
| --- | --- | --- | --- |
| Surface lost / recreated | `APP_CMD_TERM_WINDOW`: the parent window goes away; the main loop sees `GetAndroidApp()->window` change and tells the sink, which reparents the child to null and releases it; on `INIT_WINDOW` a new child is made from the new window. The GsWorker keeps rendering; frames with no child are dropped (counted). | Swapchain `VK_ERROR_OUT_OF_DATE_KHR`/`SUBOPTIMAL` → recreate at the new drawable size. | Same as macOS; plus `SDL_APP_WILLENTERBACKGROUND` must stop GPU submits (iOS kills background GPU work). |
| Background / foreground | raylib blocks its loop while unfocused; the latch RPC stops, so the GsWorker stops presenting. Transactions to a detached child are harmless. On resume a new child is created (window pointer change). | n/a (window minimise = occluded; MoltenVK keeps presenting). | Pause presents in background; recreate swapchain on foreground. |
| Rotation | Manifest is landscape-locked (`screenOrientation="landscape"`, D4), so rotation is a no-op; a window resize (multi-window, display change) re-reads the window size (JNI `DecorView` width/height) and recomputes the destination rect. | Window resize → drawable size → swapchain recreate. | `viewDidLayoutSubviews`/SDL size event → drawable size → swapchain recreate. |
| 120 Hz hooks | No WSI, so no `VK_KHR_present_id/present_wait`/`VK_GOOGLE_display_timing`. The NDK equivalents: `ASurfaceTransaction_setFrameRate(sc, 120, FIXED_SOURCE)` (API 30) to pin the 120 Hz mode; `setDesiredPresentTime` (API 29) for a target vsync; `AChoreographer_postVsyncCallback` (API 33) for expected-present timelines; `ASurfaceTransaction_setOnComplete` stats (`getLatchTime`, `getPresentFenceFd`) for the actual present time. | MoltenVK: `VK_GOOGLE_display_timing`; `present_id`/`present_wait` availability to check on MoltenVK 1.4.2; `CAMetalLayer.displaySyncEnabled`. | ProMotion: `CADisplayLink.preferredFrameRateRange` + Info.plist `CADisableMinimumFrameDurationOnPhone`; MoltenVK `VK_GOOGLE_display_timing` (maps to `presentDrawable:atTime:`). |
| Release / reuse of buffers | 4 slots; SurfaceFlinger's release fence for the previous buffer arrives in the `setOnComplete` callback (`ASurfaceTransactionStats_getPreviousReleaseFenceFd`); a slot is reused only after its release fence signalled (`sync_wait`, bounded, counted). | Swapchain acquire semaphore. | Same as macOS. |

### The Android gralloc/UBWC risk (HR1) and how the prototype handles it

The AHardwareBuffers are allocated by **the system allocator** (`AHardwareBuffer_allocate` → the
gralloc/IAllocator HAL service), which our app-local `libhardware.so` shim doesn't touch. The
risk is on the **import** side: Turnip must learn the buffer's layout (linear vs UBWC tiling,
stride) through Mesa's `u_gralloc`, whose Qualcomm backend needs `hw_get_module("gralloc")` —
which our shim makes fail. If Turnip falls back to "linear, stride from `AHardwareBuffer_describe`"
while gralloc chose UBWC, the image is garbled. The prototype allocates with
**`CPU_READ_RARELY`** added to the usage bits, which makes Qualcomm gralloc pick a **linear**
layout (UBWC is only used without CPU usage), plus `GPU_COLOR_OUTPUT | GPU_SAMPLED_IMAGE |
COMPOSER_OVERLAY`. The pixel check reads the same buffer back **through gralloc**
(`AHardwareBuffer_lock`, CPU view = the layout SurfaceFlinger/HWC will scan) and compares it
byte for byte with the Vulkan readback of the scanout image at the same present: a layout
mismatch shows up as a mismatch. Cost of linear: one 1:1 blit per frame into a linear target and
linear scanout by the display processor (UBWC would save memory bandwidth; small at 512×448
or 1024×896).

### Choice for the Odin prototype: **hybrid, game layer above the GL window**

(Corrected on the device, stage 3: a child layer's rect lives in the **parent's buffer space**,
not display pixels, and window loss must be caught from `APP_CMD_TERM_WINDOW`, since the
`ANativeWindow` pointer is reused across background/foreground.)

Why: on the Odin nothing is drawn over the game (D6), so a z = +1 child needs **no raylib
change**; the AHardwareBuffer + SurfaceControl path is *the same code* full B would use on
Android (D3), so nothing is thrown away; the pad stays usable because input never went through
the GL surface (child SurfaceControls take no input). Full B's extra work on Android is only
the Vulkan overlay renderer and removing the idle GL loop. The prototype keeps the readback
path as the fallback (any failure → `[present-vk] … falling back to readback`, once).

### Hypotheses for stage 1 and the observable that separates them

| Hypothesis for the 4×+hi-res −31 % | Predicts (4× vs 1×, per guest frame) | Separating observable |
| --- | --- | --- |
| H-copy: readback + CPU copy + GLES upload | GsWorker `readback_ms`/`copy_ms` and main-thread GLES upload grow ~4× (3.6 MB/frame) and add up to ~30 ms | backend `[gs:parallel] stats` + simpleperf GsWorker/main rows; **B's prototype removes it → knob-on 4× recovers most of the 31 %** |
| H-gpu: GPU time serialized behind a CPU wait | GsWorker CPU flat, GsWorker off-CPU (fence waits) grows; GPU busy up (47–51 % vs 32–37 %); GameThread stalls on the full GsWorker queue | GameThread wall − CPU per frame; GsWorker CPU vs wall; **knob-on 4× stays near 0.168×** |
| H-driver: Turnip CPU grows with SSAA | `libvulkan_freedreno.so` samples on the GsWorker grow | simpleperf dso rows per thread |

Equal predictions are avoided: only H-copy predicts that the prototype recovers the 4× cost.

### Estimates (per platform) and risks

| Platform | Hybrid | Full B | Main risks |
| --- | --- | --- | --- |
| Android | prototype here; **~2–3 days** to productize (under-layer variant with the raylib alpha patch for the pad, lifecycle hardening, 120 Hz `setFrameRate` + pacing, release-fence edge cases) | **+3–4 days**: Vulkan overlay (quad + glyph atlas pipeline, ~1.5–2 days shared with Apple), idle/removed GL loop, own native-app loop if raylib goes | gralloc layout on import (above); HWC may fall back to GPU composition (check `dumpsys SurfaceFlinger` composition type); vendor quirks with `ASurfaceControl` children of a NativeActivity window |
| macOS | **~1–1.5 days** (CAMetalLayer + MoltenVK swapchain from the GsWorker; transparent GL for the dev pad) | **+2–3 days** (GLFW/SDL without raylib GL; overlay shared) | Low value: option A already costs nothing on the M5 Pro (HR1); GL deprecation is the reason |
| iOS | **~2–3 days** (sublayer under a transparent EAGL layer, ProMotion pacing, background rules) | **+3–4 days** (SDL2 direct, Metal window, overlay) | raylib's SDL platform owns the view; GL deprecation; iPhone checks are Brad's (install-only rule) |

HR1's "~1.5–2 weeks" for full B on all three stands if raylib is dropped everywhere; the
hybrid route is **~1–1.5 weeks for all three**, Android first.

## Stage 3 — Odin prototype (`PS2X_PRESENT_VULKAN=1`, default off)

**What it is** (fork branch `vk1-present`, local only): `b2640de` + fix `b5d2c0d` on fork `ssx3`
`a3efbfe`; 5 files, +943/−2 (`ps2_present_vk.h`, `ps2_present_vk_android.cpp` new;
`ps2_gs_parallel_backend.cpp`, `ps2_runtime.cpp`, `CMakeLists.txt`). paraLLEl-GS/Granite unchanged
(`19d93b2`/`166ba21a`). Runner-dir diff vs `14b1e5cb`: empty. Suite **654/654** (Mac, from the
worktree root) at both commits.

- **GsWorker** (`GSParallelBackend::presentVk`): 4 slots, each an `AHardwareBuffer`
  (RGBA8, `GPU_COLOR_OUTPUT | GPU_SAMPLED_IMAGE | COMPOSER_OVERLAY | CPU_READ_RARELY`) imported
  into Turnip (`VK_ANDROID_external_memory_android_hardware_buffer` + `VK_EXT_queue_family_foreign`,
  dedicated allocation) and wrapped as a Granite image. Per present: wait the slot's old fence and
  SurfaceFlinger's release fence (bounded 100 ms), blit scanout → slot (1:1, nearest), release
  barrier to `VK_QUEUE_FAMILY_FOREIGN_EXT`, submit; with `PS2X_PGS_PRESENT_PIPELINE=1` the
  **previous** slot is queued (same one-frame latency as the readback pipeline). No readback, no
  CPU copy; `Present()` returns an empty frame.
- **Sink** (`ps2_present_vk_android.cpp`): `ASurfaceControl_createFromWindow(window, "ps2x-game")`,
  `ASurfaceTransaction_setBuffer/setGeometry/setZOrder(+1)/setBufferTransparency(OPAQUE)/
  setOnComplete` (dlsym'd from `libandroid.so`, API 29+, so minSdk 28 still loads); release fences
  from `ASurfaceTransactionStats_getPreviousReleaseFenceFd`; JNI `DecorView` size for logging.
- **Main thread** (`ps2_runtime.cpp`, Android only): passes the window, aspect and **raylib's EGL
  surface size** each frame; skips `UploadFrame`'s copy/upload and the game quad once a buffer is
  queued; wraps raylib's `onAppCmd` so `APP_CMD_TERM_WINDOW` detaches the child.
- **Why hybrid, above**: see stage 2. The on-screen virtual pad (off on the Odin) would sit under
  the layer; the under-layer variant (raylib alpha patch) is the productize step for it.

**Two bugs found on the device in V1 and fixed in `b5d2c0d`** (re-verified in V2):
1. The child inherits the parent's **buffer-to-window scaling**: raylib's window buffers are
   796×448 and SurfaceFlinger scales them ×2.41 to 1920×1080. A destination rect in display
   pixels (1920×1080) showed the top-left ~41 % of the frame, zoomed. The rect is now placed in
   the EGL surface's buffer space (`eglQuerySurface`), and the composition samples the child's
   own full-size buffer (no loss of resolution).
2. After HOME → foreground the window's layer is recreated **behind the same `ANativeWindow`
   pointer** (V2 log: new child on window `0xb400006f0ccbe8e0`, the same address), so comparing
   pointers orphaned the child (V1: `ps2x-game` without a `parentId`, screen black under the pad).
   The `onAppCmd` wrapper detaches on `TERM_WINDOW` and the next frame makes a new child.

### Acceptance

| Check | Method | Result |
| --- | --- | --- |
| (a) pixels, same present | `PS2X_PRESENT_VK_COMPARE_TICKS=1100,2100`: at that tick the present is synchronous; the scanout is also read back (the normal readback path's copy), and the **exact buffer queued to SurfaceFlinger is read through gralloc** (`AHardwareBuffer_lock`, CPU view = the layout HWC/SF scan) and compared byte for byte, RGB (alpha: PS2 0x80 in the scanout, ignored by `OPAQUE`) | **V1 and V2: `diff_px=0` at both ticks**, identical FNV hashes (t1100 `ad2e9e852b54155a` both runs; t2100 `57c031478a2650c5` V1, `794b83ff17796edb` V2 — race RNG differs by run), 512×448, gralloc stride 768 honoured. The gralloc/UBWC import risk is cleared with the linear (`CPU_READ_RARELY`) allocation. PPMs in scratch (`odin/V{1,2}/vk-t*-{ahb,readback}.ppm`) |
| (a) pixels, on screen | Screencaps (1920×1080 composite, after HWC scaling) viewed: V2 `sc01` (My Rules, ~t1201), `sc03` (after foreground: race start), `sc06` (race t~2122: HUD, carve groove, spray, full brightness), full 16:9 frame, colours right. Scaling: SurfaceFlinger/HWC scale 512×448 → 1920×1080 with the display scaler's filter (not raylib's bilinear GL quad), from the full-size buffer (1024×896 at hi-res), where the GL path first draws into the 796×448 window buffer | **Pass (viewed).** Gap: no same-tick screen-vs-readback number (screencaps land ~2 s after the compare tick; `scapcompare.py` is ready for a static-screen capture) |
| (b) guest unchanged | Mac det build (`mac_build.sh --det`) of the branch, I26-FAST to t2400, knob off vs on (the knob is inert on the Mac: no Mac path), one slot each, `gb8_hashdiff.py` | `b2640de`: **IDENTICAL 1..2400**. `b5d2c0d`: IDENTICAL except tick 761 "missing" in the knob-on log (interleaved with a `[frame:dump]` line; extracted by hand: `combined=8c2d846509fdd6a0`, eeCycle `3740542539`, **equal** to knob-off). Knob-off `b2640de` vs `b5d2c0d`: IDENTICAL |
| (d) pad | V2 with `PS2X_VIRTUAL_PAD=1` (for its `[vpad] pad_in_use` log): injected `input gamepad keyevent --longpress KEYCODE_BUTTON_A` at the end | raylib saw the pad with the layer on top: `[vpad] on=1 pad_in_use=1 first_pad=0 -> overlay hidden`. The layer takes no input (child SurfaceControls have no input channel); the window keeps focus |
| (d) background / foreground | HOME, 8 s, screencap; `am start` back, 8 s, screencap + layer list | V2: `APP_CMD_TERM_WINDOW: child layer detached` → new child → race frame on screen after foreground; 0 dropped buffers, 0 release timeouts over the run |
| (d) rotation | `cmd window user-rotation lock 3`, 6 s, screencap, restore the saved `lock 1` | App is landscape-locked: display stays `ROTATION_0` (1920×1080), no window change, picture unchanged; setting restored to `lock 1` (V1, V2) |

Present-path counters (V2, 1×): `vk_queued=2063 vk_dropped=0 vk_callbacks=2062
vk_release_timeouts=0 vk_release_wait_ms_avg=0.009 vk_apply_ms_avg=0.121` (a transaction apply
costs ~0.12 ms on the GsWorker); the backend's `readback_ms_avg`/`copy_ms_avg` are 0.

### (c) Odin speed, knob on (ABBA, vs F5 Part 2's legs)

Same method as F5 Part 2: F5's launcher lineage (via N12), I26-FAST, `--stop-tick 4500`,
`PS2X_UNPACED=1`, sound on, pipelined, empty `mc0-test`, cool-down to status 0 + fixed 180 s
before each, reinstall each time (APK `3e493b44…`), Brad's env restored and checked after each.
Race rate by F4's `phases.py` (ticks 1714→stop). Wi-Fi adb, 0 disconnects on every run.

| Leg | Variant | Race (ticks → wall) | Race vs/s | × | GPU busy race mean (n) | Thermal | VK counters |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| S1 | VA: 1× + VK | 1714→4554 / 195.3 s | 14.54 | 0.243× | 37.0 % (33) | 0→2→3 | dropped 0, release timeouts 0 |
| S2 | VB: 4×+hi-res + VK | 1714→4543 / 280.9 s | 10.07 | 0.168× | 52.0 % (46) | 0→3→2 | 0 / 0 |
| S3 | VB | 1714→4539 / 280.5 s | 10.07 | 0.168× | 52.2 % (48) | 0→3→2→1 | 0 / 0 |
| S4 | VA | 1714→4562 / 195.5 s | 14.56 | 0.243× | 37.4 % (33) | 0→3 | 0 / 0 |

| | Knob on (this) | F5 Part 2, knob off (same device, 09-25 afternoon) | Δ |
| --- | ---: | ---: | ---: |
| 1× pipelined | **14.55 vs/s = 0.2427×** (legs agree 0.1 %) | 14.635 = 0.2441× | −0.6 % (inside F5's 0.5 % leg spread) |
| 4×+hi-res pipelined | **10.07 vs/s = 0.1680×** (legs agree 0.0 %) | 10.07 = 0.1680× | 0.0 % |
| 4× / 1× | 0.692 | 0.688 | |

Backend `present_ms_avg` (whole run): 6.8 ms at 1×, 17.0 ms at 4× with the VK path, against
6.5/16.6 in F5's R1/R2 readback runs: the time is paraLLEl's, not the copy's (stage 1).

**Scaling/framing difference (stated, not matched):** the VK layer's rect is SSX 3's 16:9 over
the whole window, so the game fills **1920×1080**. The GL path draws a 640×360 letterboxed quad
into raylib's 640×448 screen inside a 796×448 buffer, which shows as **1543×868 with borders**
(F5 R2 `sc01`: 105 px bands top and bottom; VK S2 `sc01`: none). Filtering: the VK path's
512×448 (or 1024×896) buffer is scaled once by the display scaler; the GL path resamples to
360 lines with GL bilinear, then SurfaceFlinger upscales ×2.41.

## Exact commands

```sh
# worktrees (fork branch vk1-present from a3efbfe; paraLLEl clone of the fork at 19d93b2)
git -C ~/dev/PS2Recomp worktree add -b vk1-present ~/dev/ssx3-work/VK1/PS2Recomp a3efbfe
git clone --branch ssx3 https://github.com/brad-richardson/parallel-gs.git ~/dev/ssx3-work/VK1/parallel-gs
git -C ~/dev/ssx3-work/VK1/parallel-gs checkout -b vk1-present 19d93b2 && git submodule update --init --recursive
# Turnip WSI check (F5 APK's driver)
llvm-nm -D --undefined-only lib/arm64-v8a/libvulkan_freedreno.so   # no ANativeWindow_*, AHardwareBuffer_* only
# Mac builds + suite + det pair (one slot each)
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/VK1/PS2Recomp ~/dev/ssx3-work/VK1/build --pgs ~/dev/ssx3-work/VK1/parallel-gs
(cd ~/dev/ssx3-work/VK1/PS2Recomp && ../build/ps2xTest/ps2x_tests)                     # 654/654
bash local/tooling/build/mac_build.sh … ~/dev/ssx3-work/VK1/build-det --det --pgs … --target ps2EntryRunner
python3 local/research/VK1/vk1_boot.py --mode det --backend parallel --runner bin/runner-det2 --label det-off2 --route i26 --stop-tick 2400 --no-snap
python3 local/research/VK1/vk1_boot.py … --label det-on2 … --env PS2X_PRESENT_VULKAN=1
python3 local/research/GB8/gb8_hashdiff.py --base run/det-off2 --cand run/det-on2
# Android syntax check on the mini (NDK r30), then bytesize builds (held ssh)
git archive --format=tar b2640de | ssh bytesize 'wsl -d Ubuntu -- bash -lc "… tar -x -C /home/brad/vk1/PS2Recomp"'
cat local/research/VK1/build-android.sh | ssh bytesize 'wsl … cat > /home/brad/vk1/build.sh && /home/brad/vk1/build.sh'
git archive b5d2c0d -- <3 changed files> | ssh bytesize '… tar -x …'; ssh bytesize '… /home/brad/vk1/build.sh'  # incremental
# Odin (cooldown.py before every launch.py)
python3 local/research/VK1/launch.py --label P1 --variant A --cpu-window 1800,2350 --profile-after-tick 2400 --profile-secs 30 --scap-ticks 2100
python3 local/research/VK1/launch.py --label P2 --variant B …(same)
bash local/research/VK1/report.sh P{1,2}; python3 local/research/VK1/stage1.py logs/P1 logs/P2
python3 local/research/VK1/launch.py --label V2 --variant VA --stop-tick 2400 --apk …/odin-apk2/app-release.apk --apk-sha 3e493b44… \
  --compare-ticks 1100,2100 --lifecycle 1300 --pad-probe --scap-ticks 1100,2100,2300
python3 local/research/VK1/launch.py --label S{1..4} --variant VA|VB|VB|VA --wall 600 --stop-tick 4500 --apk … --scap-ticks 2100,3000,4000
python3 local/research/F4/phases.py local/research/VK1/logs/S{1..4}
bash local/research/VK1/restore-play.sh     # F5 APK 4ff81032 + deploy-odin.sh + F5 play knobs → env a8d651a7
```

## Pins and SHAs

| Item | Value |
| --- | --- |
| Fork base / branch tip | `a3efbfe` → `b2640de` → **`b5d2c0d`** (`vk1-present`, local; runner-dir diff vs `14b1e5cb` empty) |
| paraLLEl-GS / Granite | `19d93b2` / `166ba21a` (unchanged; bytesize used F5's `/home/brad/f5/parallel-gs` copy) |
| Turnip | F5/TL1 jniLibs `libvulkan_freedreno.so` 14,188,488 B (Mesa 26.3.0-devel `c501e1d16e`) |
| Android APK 1 (`b2640de`, V1 only) | `7667628a5b70ccd0e71ccb54ae9497f55f772ef7ad6845b2f6b79fb356e3d5a3` (×2 remote, ×2 local, installed base.apk match) |
| **Android APK 2 (`b5d2c0d`, V2 + S1–S4)** | **`3e493b44697d8e61866b43bed70d86536f57764dc7c7b812310fcf1cc5776220`** (×2 remote, ×2 local, installed match every launch) |
| Source tar `b2640de` | `b975b24f…` both ends; `b5d2c0d` delta: 3 files, SHAs match both ends |
| Mac det runners | `b2640de` `b754aafc…`; `b5d2c0d` `a93cbdf5…` |
| F5 APK restored | `4ff81032a175…09753` (local ×2, installed base.apk) |
| Brad env after | `a8d651a7…0ebd`; save 6/6 OK; `mc0-test` empty; `/data/local/tmp/vk1` removed; lease `LEASE_FREE VK1 done` |
| Symbols | F5 unstripped `libps2EntryRunner.so` (Build ID `e39b09b3…` = APK), streamed to `~/dev/ssx3-work/VK1/symdir` |

## Budgets

Android builds **2/6** (full 9 m 41 s; incremental 19 s). Odin launches **8/8** (P1, P2 profiles;
V1, V2 diagnostics; S1–S4 speed) plus one no-launch restore. Mac: 4 det boots (one slot each,
on the mini — the brief predates HS1's bradflix default), 4 builds (ccache). Scratch
`~/dev/ssx3-work/VK1` 6.9 GB (cap 15). Mini 163.4/200 GB. bytesize `/home/brad/vk1` (source,
build tree, APK). Wall ~19:28–21:00.

## Gaps

- G1. No same-tick **screen-vs-readback** number: the screencaps land ~100 ticks after the
  compare tick. The same-tick check is the byte compare of the exact queued buffer (gralloc
  view). `scapcompare.py` is ready for a static-screen capture.
- G2. **HWC composition type** of `ps2x-game` (device overlay vs GPU client composition) and its
  present rate were not polled (`phases.py`'s SF column reads the window layer, still raylib's
  60 Hz clear). The layer carries `COMPOSER_OVERLAY` usage; `dumpsys SurfaceFlinger` would show.
- G3. The virtual pad (off on the Odin) sits **under** the layer; the under-layer variant (raylib
  EGL alpha patch + RGBA window) is designed, not built.
- G4. Pipelined present kept (one frame of latency, as today). A sync_fd acquire fence would drop
  the CPU fence wait, but stage 1 measured those waits at 0.16–0.30 ms, so it wasn't built.
- G5. **Framing differs** from the GL path (fills the screen vs 1543×868 bordered); not matched.
- G6. The stage-1 mechanism (4 frame contexts × a flush per `next_frame_context`) is a
  hypothesis: flushes per vsync not counted, no frame-context experiment (out of scope).
- G7. Speed legs are compared with F5's knob-off legs from earlier the same day, not
  interleaved in one session. The same-session knob-off windows (P1/P2) agree with F5.
- G8. Mac and iOS: design and estimates only (no prototype, per the brief).
- G9. raylib's GL loop still clears and swaps the window at 60 Hz under the layer (not measured;
  the main thread's CPU with VK wasn't split out, since the speed legs carry no per-thread window).

## Recommended next action (orchestrator decides)

1. The Odin's 4× cost is GPU work serialized into the GsWorker inside paraLLEl, not the present
   path. A small brief: count `flush_submit`/`next_frame_context` per vsync on the Odin and try
   a `PS2X_PGS_FRAME_CONTEXTS` knob (e.g. 8/16) with a 1× + 4× pair.
2. Keep the Vulkan present for **picture quality and the 120 Hz path**, not speed: it fills the
   screen from the full-size buffer (so 4×+hi-res shows its resolution), drops the GLES upload, and
   gives `setFrameRate`/`setDesiredPresentTime` for pacing. Productize (~2–3 days): under-layer
   variant for the pad, HWC composition check, framing decision (fill vs today's box).
3. Independent of B, and cheap: today's GL path shows **360 lines** because raylib's logical
   screen is 640×448. Initializing raylib at the display size on Android would give the GL path
   full resolution too. A Brad-visible choice; either path fixes it.


## Orchestrator gate, stages 1–3 (2026-09-26)

**Pass.** Excellent separation: the 4× cost is +31 ms of GameThread stall behind GPU work serialized in
paraLLEl's `flush()`/`vsync()` (H-gpu), not the copy (H-copy predicted recovery; the prototype showed
none, exactly as stage 1 said). The prototype is pixel-exact through gralloc, speed-neutral, and
survives background/foreground. The big user-visible finding: **the Odin shows every frame at 360 lines
in a bordered 1543×868 box** today (raylib's 640×448 logical screen); the Vulkan layer fills
1920×1080 from the full-size buffer. The canonical build of fork `5474956` with paraLLEl `464f263`
(mac_build.sh defaults) was verified by me (CLUT accessor linked).

## Part 2 brief (orchestrator) — same pane, Odin
**2A frame contexts (first, small):** count `flush_submit`/`next_frame_context` per vsync (Odin, 1× and
4×) and add `PS2X_PGS_FRAME_CONTEXTS` (default 4 = today). Try 8 and 16 at 4×+hi-res and at 1× (≤ 6
launches, cool-down method, ABBA where it matters). Mac det-hash unchanged with the knob set. Table;
say whether it recovers the 4× cost.
**2B productize the Odin Vulkan present** on a branch from fork `ssx3` **`5474956`** (save states landed):
default **on** for Android with the GL path as automatic fallback; framing **fill the screen** (16:9 at
1920×1080) unless the orchestrator says otherwise (Brad is being asked); the under-layer variant for the
virtual pad (raylib EGL alpha + RGBA window); HWC composition check (G2); stop raylib's 60 Hz clear/swap
under the layer if cheap (G9). Validation: pixels via gralloc at two ticks, bg/fg, pad on and off,
Mac det-hash unchanged, Odin 1× speed pair vs the F5 play build. Suite green, runner-dir empty, one
Android build per candidate on bytesize. Stop before any push or play-build install; I fold it (F6).
Budget 6 h, ≤ 6 Android builds, ≤ 12 Odin launches. Brad's env/save rules unchanged.

## Part 2A — frame contexts (orchestrator brief, 09-26)

**Answer: no. More Granite frame contexts don't recover the 4× cost, and the frame-context wait
was never the cost.** The time is the GsWorker **blocked inside paraLLEl's `flush_submit()`**,
which doubles at 4×.

Code (local): paraLLEl branch `vk1-part2` from `464f263`: `8013170` (counters: `flush_submit`
calls, `next_frame_context` advances + wall, `wait_timeline` calls + wall) and `1b3a294`
(`flush_submit` wall). Fork branch `vk1-part2` from `5474956`: prototype cherry-picked
(`b99ae9f`, `b5ed3c8`), `ef039cb` (`PS2X_PGS_FRAME_CONTEXTS`, 2..16, default 4 = before; a
periodic `[gs:parallel] sync` line with per-present deltas), `321773e` (Present's
`GSInterface::flush`/`vsync` wall). Cost: four `steady_clock` reads and relaxed atomics per
flush; the sync line prints every 300 presents like the existing stats line.

| Run (APK) | Settings | Race rate | flush_submits / present | frame-ctx wait ms / present | timeline waits | `flush_submit` wall ms / present | Present: `flush()` / `vsync()` ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| A1 (`b2fc7f65…`) | 4×+hi-res, **FC=16**, GL present | 1714→4529: **10.16 vs/s = 0.169×** | 3.99 | 0.60 | 0 | — | — |
| A2 (`b2fc7f65…`) | 4×+hi-res, FC=4, GL | 1714→4558: **9.93 = 0.166×** | 4.02 | 0.60 | 0 | — | — |
| L1 (`8c74352d…`) | 4×+hi-res, FC=4, GL (`PS2X_PRESENT_VULKAN=0`) | 1714→3036: 9.38 (0.157×, early race only) | 3.97 | 0.59 | 0 | **48.7** | 17.2 / 0.60 |
| L2 (`8c74352d…`) | 1×, FC=4, GL | 1714→3014: 13.54 (0.226×, early race only) | 4.03 | 0.31 | 0 | **23.4** | 6.5 / 0.29 |

(Race-window means of the sync lines from tick 1800. A1/A2 per-thread windows: GameThread
57.6 ms CPU of 106.8 / 109.9 ms wall; GPU 47.2 / 51.2 %. Reference, F5 Part 2 B legs: 10.21 /
9.93, VK1 S2/S3: 10.07 / 10.07.)

Reading:
- FC=16 vs FC=4: +2.3 % (10.16 vs 9.93), inside the B-leg spread already seen (F5: 2.8 %). The
  frame-context wait is **0.6 ms per present at both settings** (0.3 at 1×), so there's nothing
  for more contexts to recover. FC=8 and the 1× FC pair weren't run: the counter rules them out,
  and those launches went to localizing the real wait instead (L1/L2).
- The race does **~4 `flush_submit`s per present** (the Mac shows the same, 4.3). Their wall is
  **23.4 ms per present at 1× and 48.7 ms at 4×**: +25 ms, which is the +31 ms GameThread stall
  from stage 1 to within the window differences. Most of it happens **outside `Present()`**
  (Present's own `flush()` is 6.5 / 17.2 ms; `vsync()` < 1 ms), i.e. in flushes triggered while
  the GsWorker processes GIF packets. The GsWorker's CPU stays ~15.5 ms/frame, so this is
  **blocked time**, not work.
- Inside `flush_submit`, the frame-context advance (0.3–0.6 ms) and timeline waits (0) are
  excluded. What remains is Granite's `device->submit(...)` of the recorded command buffers
  (Turnip `vkQueueSubmit` → kgsl), the two timeline `submit_empty` calls, and
  `drain_compilation_tasks_nonblock()`. Splitting those is the next measurement: one more timer
  pair, no Odin budget question.
- Mac det-hash with FC=16: **identical 1..2400** (`ef039cb` det build, one slot each).

Recommended (orchestrator decides): keep `PS2X_PGS_FRAME_CONTEXTS` (default 4, harmless) or drop
it at fold; next brief: time `device->submit` vs `submit_empty` vs compile-drain inside
`flush_submit` on the Odin at 1× and 4×. If it's the kgsl submit blocking, the lever is fewer,
larger submits per frame or a submit thread in paraLLEl, not the present path.

## Part 2B — productized Odin Vulkan present (fork branch `vk1-part2` from `5474956`)

**State: done up to the fold; nothing pushed, no play-build install.** Framing is fill-the-screen
(16:9 over the whole 1920×1080 panel), per the orchestrator.

| Commit (fork `vk1-part2`) | What |
| --- | --- |
| `b99ae9f`, `b5ed3c8` | stage 3 prototype + geometry/lifecycle fix (cherry-picked from `b2640de`, `b5d2c0d`) |
| `ef039cb`, `321773e` | Part 2A: `PS2X_PGS_FRAME_CONTEXTS` (default 4) and the `[gs:parallel] sync` line (flush/frame-context/timeline/present wall split) |
| `c0c449e` | **Default on** for Android (`PS2X_PRESENT_VULKAN=0` forces GL). **Automatic fallback**: API < 29, no AHB import extensions, AHB slot setup failure, or > 240 consecutive dropped buffers while a window exists → the sink marks itself broken, detaches the child, the backend returns to the readback path and the presenter draws the GL quad again. **Under-layer variant** when the virtual pad is on: `ANativeActivity_setWindowFormat(RGBA_8888)` before `InitWindow`, raylib EGL alpha via a hash-pinned configure patch (`cmake/patch_raylib_android_egl_alpha.cmake`, raylib 5.5 `rcore_android.c` `a17a8c75…`), child at z = −1, GL clears to transparent, pad drawn with premultiplied separate blending. **No GL clear/swap under the layer** when there is no overlay: input polling and the pad latch still run, paced by a 60 Hz sleep |
| `2c1c4ba` | Skip the GL swap only after 3 GL swaps on the current window (D2 bug below) |
| `51f8215` | Keep the main thread's name across the JNI attach (an unnamed attach renamed it `Thread-N`, hiding it from per-thread profiles) |
| **`15275cd`** (tip) | Aspect-exact rect: round the size, then centre (4:3 = 597 of 796 buffer px = exactly 1440 panel px; edge rounding gave 598 = 1442). Under-layer: GL clears black, then a scissored clear makes only the child's rect transparent, so bars stay black |

paraLLEl branch `vk1-part2` from `464f263`: `8013170`, `1b3a294` (counters only). Suite
**662/662** at every fork commit (Mac, worktree root); runner-dir diff vs `14b1e5cb` empty.
Android builds **6/6**: `b2fc7f65…` (2A), `cbac70df…` (not launched), `8c74352d…` (L1, L2, D1,
D2), `5cd153da…` (D3, Q1, Q4), `203ba47d…` (H1), **`727242b1…` (tip `15275cd`, not yet on a
device)**; each two local + two remote SHA reads, installed `base.apk` matched every launch. Mac
det-hash **identical 1..2400** vs the `ef039cb` baseline at `c0c449e`, at `2c1c4ba` (with
`PS2X_PGS_FRAME_CONTEXTS=16`) and at `15275cd`.

### Device checks (Odin, APK `8c74352d…` for D1/D2, `5cd153da…` for D3 and the speed legs)

| Check | Run | Result |
| --- | --- | --- |
| Default on, no env key | D1, D2, D3, Q1, Q4 | `[present-vk]` layer + 4 AHB slots; no `PS2X_PRESENT_VULKAN` in the env |
| GL fallback knob | L1, L2 (`PS2X_PRESENT_VULKAN=0`) | `[present-vk] off (PS2X_PRESENT_VULKAN=0): GL present`; readback path, normal picture |
| Pixels via gralloc | D1 t1103 + t2100, D2 t2100, D3 t2100 (after bg/fg) | **`diff_px=0` all four**, stride 768 |
| Pad **on** (under-layer) | D1 (`PS2X_VIRTUAL_PAD=1`) | child `z=-1`; screencap t2100: full-screen race with the translucent pad drawn over it, colours right; injected gamepad press → `[vpad] pad_in_use=1` |
| Pad **off** | D2, D3 | child above, GL swap skipped once 3 GL frames are on the window |
| Background / foreground | D1, D2, D3 | `APP_CMD_TERM_WINDOW: child layer detached` → new child; D1/D3 full-screen after foreground. **D2 bug (fixed in `2c1c4ba`, re-checked in D3):** with the swap skipped, the new window never got a GL buffer, so its buffer→window scaling was missing and the child showed at 796×448 in a corner |
| HWC composition (G2) | D1, D2, D3 (one `dumpsys` each at t~2220) | D1: `ps2x-game` **DEVICE** (display overlay, `ROT_90`, full panel); GL window CLIENT. D2/D3: **every** layer on the display CLIENT (nav bar and screen decor too), i.e. SurfaceFlinger chose GPU composition for that frame; the covered GL window is culled. Single samples |
| Counters | D1–D3, Q1, Q4 | `vk_dropped=0`, `vk_release_timeouts=0` |
| HWC, more samples | H1 (`203ba47d…`, pad off, 6 `dumpsys` at t1919–3209) | **6/6: every layer CLIENT**, `ps2x-game` included, i.e. SurfaceFlinger GPU-composites the whole display each frame with the pad off; D1 (pad on, GL window updating above) got `ps2x-game` as a DEVICE overlay. Not investigated further; see the speed note below |
| Thread name | H1 | main thread back as `com.ps2x.runner` (0.09 ms/frame) |

### 1× speed vs the F5 play build (ABBA, same session)

Same method as F5 Part 2 (cool-down to status 0 + 180 s, reinstall each leg, I26-FAST, unpaced,
sound on, pipelined, stop 4500); per-thread CPU window ticks ~1866→2600 (unprofiled).

| Leg | APK | Race (ticks / wall) | vs/s | × | Main thread CPU ms/frame | GsWorker | GameThread |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Q1 | new `5cd153da…` (VK default, GL swap skipped) | 1714→4569 / 195.5 s | 14.60 | 0.244× | **0.08** (`Thread-3`, renamed) | 12.70 | 50.09 |
| Q2 | F5 play `4ff81032…` (GL readback) | 1714→4516 / 190.8 s | 14.68 | 0.245× | 4.53 | 14.18 | 54.92 |
| Q3 | F5 play | 1714→4526 / 191.0 s | 14.72 | 0.246× | 4.24 | 13.69 | 51.81 |
| Q4 | new | 1714→4572 / 196.0 s | 14.58 | 0.243× | **0.08** | 12.95 | 50.59 |

New **14.59 vs/s = 0.2434×** vs F5 **14.70 = 0.2452×: −0.7 %** (legs agree within 0.1 % and
0.3 %, ABBA order consistent), in line with stage 3's −0.6 %. The main thread drops from ~4.4
to 0.08 ms/frame and the GsWorker by ~1.1 ms/frame, but the race is GameThread-bound, so that
doesn't show in the rate. A lead for the −0.7 % (not tested): with the pad off, SurfaceFlinger
GPU-composites the whole display (H1: 6/6 CLIENT), which puts composition work on the GPU that
paraLLEl uses. A test would be one pair with the GL swap kept on (does HWC return to DEVICE?).

### Aspect (orchestrator/Brad 09-26: 16:9 default, largest fit, never stretched)

The child's rect is `presentRect(parent buffer, frame, aspect)` with `aspect` from
`aspectFromEnv(PS2X_ASPECT, anamorphic)`, the same as the GL presenter. Computed for the Odin
(parent buffer 796×448 → panel 1920×1080, ×2.412 / ×2.411):

| Aspect | Vulkan layer on the panel (`15275cd`) | GL path today (raylib 640×448 canvas) |
| --- | --- | --- |
| 16:9 (default: anamorphic) | **1920×1080**, exact (buffer [0,0 796,448]) — **seen on device**: D1/D3/Q/H1 screencaps full screen | **1544×868 box**, borders on all four sides (F5 R2 `sc03`) — wrong for Brad's rule |
| 4:3 (`PS2X_ASPECT=4:3` or widescreen off) | **1440×1080**, black bars 239/241 px (buffer [99,0 696,448]; the 1.2 px off-centre is one buffer pixel = 2.41 panel px) — **not yet seen on device** | 1440.8×1080, bars ~240 — already right |
| native (512×448) | 1235×1080 | 1235×1080 |

The panel's buffer is 796 px wide for a 796.4 px ideal, so the x/y scales differ by 0.06 %
(below a pixel across the frame); nothing is stretched beyond that rounding.

**GL fallback path:** it does **not** match at 16:9. It still letterboxes the picture into
raylib's 640×448 canvas, which shows as the 1544×868 bordered box. Cheap follow-up (not built,
per the orchestrator): start raylib at the display size on Android (`InitWindow` with the
window's size instead of 640×448), so the GL canvas is the panel and the same `presentRect`
fills 1920×1080 at 16:9.

### Gaps (Part 2)

- **4:3 on-screen check pending**: the brief's 12 Odin launches are used (A1, A2, L1, L2, D1,
  D2, D3, Q1–Q4, H1). The tip APK `727242b1…` (rounding + under-layer bars) hasn't run on the
  device. Needs **2 more launches** (4:3 pad off; 4:3 pad on/under-layer), orchestrator's call.
- HWC composition is sampled by `dumpsys` (single frames); the −0.7 % mechanism is a lead only.
- Under-layer after a runtime fallback: the RGBA window stays RGBA and the pad is drawn with
  plain alpha blending, so pad pixels are faintly see-through over black (cosmetic, fallback only).
- 16:9 fill relies on raylib's 796×448 buffer mapping to the whole panel; a device whose window
  isn't full screen would get the same rule inside its window (largest fit), not checked.
- Mac det boots ran on the mini (brief: "Mac det-hash"; HS1's bradflix default is for Linux det).

### Exact commands (Part 2 delta)

```sh
git -C ~/dev/ssx3-work/VK1/PS2Recomp checkout -b vk1-part2 5474956 && git cherry-pick -x b2640de b5d2c0d
git -C ~/dev/ssx3-work/VK1/parallel-gs checkout -b vk1-part2 464f263
bash local/tooling/build/mac_build.sh ~/dev/ssx3-work/VK1/PS2Recomp ~/dev/ssx3-work/VK1/build2 --pgs ~/dev/ssx3-work/VK1/parallel-gs   # 662/662
bash local/tooling/build/mac_build.sh … ~/dev/ssx3-work/VK1/build2-det --det … --target ps2EntryRunner
python3 local/research/VK1/vk1_boot.py --mode det … --label det-fc16 --env PS2X_PGS_FRAME_CONTEXTS=16; gb8_hashdiff.py --base run/det-fc4 --cand run/det-…
git archive <rev> | ssh bytesize '… tar -x -C /home/brad/vk2/PS2Recomp'; tar -cf - (paraLLEl worktree) | ssh bytesize '… /home/brad/vk2/parallel-gs'
ssh bytesize 'wsl … VK1_ROOT=/home/brad/vk2 VK1_PGS=/home/brad/vk2/parallel-gs /home/brad/vk2/build.sh'   # full 9m39s, then ~20 s increments
python3 local/research/VK1/launch.py --label A1 --variant B --fc 16 --cpu-window 1800,2350 --apk …b2fc7f65 …   # A2: --fc 4
python3 local/research/VK1/launch.py --label L1 --variant B --vk 0 --stop-tick 3000 --apk …8c74352d …          # L2: --variant A
python3 local/research/VK1/launch.py --label D1 --variant A --pad-probe --compare-ticks 1100,2100 --lifecycle 1300 --sf-dump-tick 2200 …
python3 local/research/VK1/launch.py --label Q1..Q4 --variant A --stop-tick 4500 --cpu-window 1850,2550 --apk <new|F5> …
python3 local/research/VK1/launch.py --label H1 --variant A --stop-tick 3300 --sf-dump-tick 1900,2150,2400,2650,2900,3150 --apk …203ba47d …
python3 local/research/VK1/sync.py logs/A1 logs/A2 logs/L1 logs/L2; python3 local/research/F4/phases.py logs/Q1
bash local/research/VK1/restore-play.sh   # F5 4ff81032 + env a8d651a7, after Part 2
# pending (2 launches): launch.py --label AS1 --variant A --aspect 4:3 --scap-ticks 1100,2100 --apk …727242b1 …;  AS2: + --pad-probe
```

