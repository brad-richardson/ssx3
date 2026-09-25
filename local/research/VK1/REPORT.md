# VK1 — present straight from Vulkan (option B): Odin cost split, design, Odin prototype

Worker: Claude Code (Opus 5.5), Opus spike approved by Brad 09-25, brief `local/muse/prompts/VK1.md`.
Worktrees `~/dev/ssx3-work/VK1/{PS2Recomp,parallel-gs}` on local branches `vk1-present`
(PS2Recomp from fork `ssx3` `a3efbfe`, paraLLEl-GS `19d93b2`, Granite `166ba21a`). Never pushed.

Status: **stage 2 (design) committed first; stage 1 (Odin cost split) and stage 3 (prototype) below.**

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
