# HR1 notebook (Opus exploratory, 3 h box from 13:17:40 EDT 2026-09-25)

## 13:17 start
- Read brief + DK1/GB8/I33/ST1/NP1/N11 heads, facts, orchestration §3.
- Orchestrator additions mid-run: size option B (Vulkan WSI present) next to A;
  then Brad chose **A** (share the image into GL/GLES) as target, B parked — size B briefly.

## 13:25 present path read (fork ec2dbf1)
- Main thread `UploadFrame` (`ps2_runtime.cpp:709`) → `gs().latchHostPresentationFrame()` =
  blocking RPC to the GsWorker (`gs_frontend.cpp:937`: enqueue + `rpc->wait()`).
- GsWorker runs `Present` (`ps2_gs_parallel_backend.cpp:~240`): flush, `vsync()`, then a
  **per-frame `create_buffer` (CachedHost) + `copy_image_to_buffer` + submit + `wait_idle()`**,
  map, then a CPU row copy into a 640-stride vector with alpha forced to 255 (DK1).
- Main thread then: `copyLatchedHostPresentationFrame` (second CPU copy, packs rows),
  `std::fill` of a 640x512 upload buffer + third copy, `UpdateTexture` (GL upload).
- So one frame = 1 GPU→host DMA + 3 CPU copies + 1 GL upload; the GameThread only enqueues
  GIF packets (async), so readback cost lands on **GsWorker (copy+wait) and main (blocked on
  RPC + copies + upload)** — to be measured.
- `wait_idle()` drains the whole GPU queue every present: serialises with rendering.

## 13:30 knobs written (hr1-ssaa worktree, uncommitted yet)
- `PS2X_PGS_SSAA=1|2|4|8|16` → `GSOptions::super_sampling` (paraLLEl clamps to device max:
  X4 unless subgroup-size control gives X8/X16), `PS2X_PGS_SSAA_TEXTURES=1`,
  `PS2X_PGS_HIRES_SCANOUT=1` → `VSyncInfo::high_resolution_scanout` (paraLLEl ignores it
  unless force_progressive (on since ST1), both axes super-sampled (X4 ordered = 2x2), no
  EXTWRITE, no forced deinterlace; `gs_renderer.cpp:4310-4327`).
- Frames larger than 640x512 are packed at stride = width; frontend infers packing from size;
  the uploader grows the raylib texture once and uses `UpdateTextureRec` from the scratch
  vector (skips the fill + third copy on that path). Default path byte-identical.
- First attempt added a `stride` field to `PresentationFrame` + a GS member: reverted,
  because codegen includes `gs_frontend.h` → every header edit recompiles ~300 codegen units
  (bad for incremental iOS builds). Now .cpp-only (3 files).
- `threadcpu.c` (libproc `PROC_PIDTHREADINFO`): per-thread user/sys ns **with names**, same
  uid, no root — works (GB8's ctypes attempt failed; C works).

## 13:31 build + suite
- Build (`~/dev/ssx3-work/HR1/build`, F3 recipe, BUILD_TEST=ON) rc=0; suite from worktree root
  **642/642**. Commit `cf7c0df` (knobs, 3 files +159/−7). runner-clean `2ece529e…` (×2).
- Det runner: separate detached worktree `PS2Recomp-det` @ `cf7c0df`, build-det (DET_HASH_TAP=ON),
  `runner-det` `93afd709…` (×2), `det-hash:v1` string present.

## 13:33 smoke 4x+hires (runner-clean, diag, 1 slot, loaded host ~20-30 load)
- `[gs:parallel] quality ssaa=4 (asked 4) … hires_scanout=1`; scanout **1280x896 at tick 40,
  1024x896 from tick 43**; texture grown to 1280x896 once; 0 FATAL; race HUD 43.1 s wall.
- present_ms_avg 10.3, readback_ms_avg 4.19, copy_ms_avg 0.37 (GsWorker side).
- thread-cpu at t1948: main 6.3 s, GsWorker 7.7 s, GameThread 37.2 s, 3 unnamed Granite/MVK
  workers ~1.7-1.8 s each; main_latch_ms 17496 over 1415 uploads = **12.4 ms/frame blocked on
  the latch RPC** (queue drain + vsync + readback), main_upload 0.84 ms/frame.

## 13:34 zero-copy prototype (commit fb3dca0) — works first try
- `VK_EXT_metal_objects` enabled; 3 IOSurface-backed BGRA8 images per size; CGL bind
  cgl_err=0; first glBlitFramebuffer gl_err=0.
- Smoke zc 4x+hires: present_ms_avg **4.64** (vs 10.3), readback 0; thread-cpu at t1913: main
  3.2 s (vs 6.3), GsWorker 5.9 s (vs 7.7), main_latch 7.7 s over 1520 (5.1 ms/frame vs 12.4).
  Diagnostic, loaded host, one run each — direction only; speed pair below.
- Verified visually: GL texture dump (`PS2X_PRESENT_SHARE_DUMP_TICKS`) at t1091 = correct Select
  Peak, 1024x896, upright, right colors, full brightness. (`screencapture` can't see windows:
  no screen-recording permission → returns wallpaper only.)
- Suite on fb3dca0 642/642. iOS device build of fb3dca0 started 13:37 (HR1/ios).

## 13:40 det boots (runner-det @ cf7c0df, 1 slot each, frames at 1090/2100/2380, to t2400)
- det-1x / det-4x / det-4x-hires: all `target`, 0 FATAL; frames 512x448 / 512x448 / 1024x896.
- **Det-hash 1..2400 identical** 1x vs 4x and 1x vs 4x+hires (gb8_hashdiff first_diff=None;
  tick 7 missing in det-1x because the [gs-path] line interleaved with it: extracted by hand,
  identical md5 across all three).
- Frames viewed (compare/): menus (1090) ~identical at all settings (2D; hi-res text edges a
  bit crisper). Race: 4x downsampled = smooth AA edges but overall softer than 1x; 4x+hires =
  genuinely finer geometry (tree needles, slope edge, HUD, snowball) → SSX 3 renders 3D straight
  into the scanout buffer; the "blit loses SSAA" caveat does not apply to the race. Hi-res edges
  still stair-step (each super-sample is an output pixel: 2x res, no AA). Snow shadow shows a fine
  regular pattern at hi-res (dither/texture at 2x; minor). Spray/fog at 2380 renders the same in
  all three. **No broken effect** → no stop rule.
- Pre-existing: thin vertical pink line near x≈217 at t2100 in all three (and on the iPad) — not
  from the knobs.

## 13:44-13:50 iPad (Air M2), fb3dca0 device build, installed seq 1940, deploy-ios OK
- signed binary `dfa10a2f…` (×2); probe: Data BBACF011-…, Bundle 109411C8-… (= install URL).
- One launch each, fresh cards mc-hr1-1x / mc-hr1-4xhr, PS2X_THREAD_CPU_LOG=1, diagnostic pace:
  1x race 10.31 vs/s (0.172x), 4x+hires 9.34 (0.156x, −9 %). GameThread busy 91 → 82 %;
  GsWorker CPU 8-9 % both; main latch wait 14.9 → 25.4 ms/frame; backend present 10.7 → 16.3 ms,
  readback 8.1 → 9.8 ms (mostly `wait_idle` = GPU drain; the CPU copy is 0.13 → 0.37 ms).
  Reading: on the iPad the 4x cost is **GPU time exposed by the synchronous present**, not CPU
  copying; the GameThread loses ~9 % waiting on the GS path.

## 13:50 pipelined present (fork commit 4825123), iPad A/B
- Finding: `GsWorker::enqueue` blocks the producer when the ring is full (gs_worker.cpp:44-60),
  so the per-present `wait_idle` (GPU drain) on the GsWorker stalls the **GameThread** too.
  The CPU copies themselves are 0.1-0.45 ms/frame; the cost is the synchronous GPU wait.
- `PS2X_PGS_PRESENT_PIPELINE=1` (default off): readback path = 2 persistent buffers + per-frame
  fence, deliver previous frame (1 frame latency); zero-copy path = publish previous IOSurface
  slot. Suite 642/642; runner-hr1 `15c5348d…` (×2). iOS rebuild: binary `c8050cae…`, signed
  `5c897acd…` (×2), installed seq 1948 (bundle AC25A30E-…), deploy-ios OK, probe Data F126FB8B-….
- iPad, one launch each, diagnostic pace (receipt `ipad-cost.md`):

| Run | race vs/s | GameThread busy | latch wait ms/frame | backend present / readback ms |
| --- | --- | --- | --- | --- |
| 1x (fb3dca0 build) | 10.31 (0.172x) | 91 % | 14.9 | 10.7 / 8.1 |
| 4x+hires sync | 9.34 (0.156x) | 82 % | 25.4 | 16.3 / 9.8 |
| 4x+hires sync, repeat (4825123 build) | 9.26 (0.155x) | 82 % | 25.5 | 15.9 / 9.8 |
| **4x+hires pipelined** | **10.49 (0.175x)** | **94 %** | 10.1 | 5.1 / 0.03 |

  → 4x+hires costs ~9-10 % on the iPad only because of the synchronous present; pipelined it
  runs at (or above) the 1x sync rate. One run per config; second decimal is noise.
- Mac smoke numbers (diagnostic: loaded host 15-30, 1 slot, not speed; `mac-smoke-cost.md`,
  window t1500-1950): 4x+hires readback 13.9 vs/s, main 10 % CPU, latch 15.9 ms/frame; zero-copy
  20.3 vs/s, main 5 %, latch 5.9 ms/frame. Direction only.

## 13:57 PAUSED (orchestrator: Brad needs the machine)
State at pause:
- Fork `~/dev/ssx3-work/HR1/PS2Recomp` branch `hr1-ssaa` = ec2dbf1 + `cf7c0df` (knobs) +
  `fb3dca0` (Mac zero-copy prototype) + `4825123` (pipelined present). Not pushed. Runner dir
  check empty. Detached det worktree `HR1/PS2Recomp-det` @ cf7c0df.
- Binaries (`~/dev/ssx3-work/HR1/bin`): runner-clean `2ece529e…` (cf7c0df), runner-det
  `93afd709…` (cf7c0df, det-hash tap), runner-zc `dce52a0a…` (fb3dca0), runner-hr1 `15c5348d…`
  (4825123), threadcpu (libproc probe). Build dirs: HR1/build (clean, BUILD_TEST=ON @4825123),
  HR1/build-det, HR1/ios/ios-runtime-device-release (@4825123).
- iPad has the HR1 4825123 build installed (knobs default off = F3 behavior + HR1 changes);
  Brad's save + env redeployed (deploy-ios OK). iPhone/Odin untouched.
- No leases held (all four mini slots free at 13:57); no HR1 runner alive. Two queued smokes
  (smoke-pipe-rb/zc) were stopped before/at boot: their run dirs are partial, ignore/delete.
- The Mac speed ABBA **never ran** (other lanes held the slots; hold killed while waiting).

Resume plan (in order):
1. Mac smoke of pipelined readback + pipelined zc with frame/texture dumps (note: pass
   PS2X_FRAME_DUMP_ONCE_TICKS with commas — hr1_boot `--extra-env` splits on commas, so use
   `--dump-ticks` in det mode or add a separate flag; the stopped smoke used `;` = dump every frame).
2. Mac speed holds with `hr1_hold.py` (RUNNER = runner-hr1): A 1x, B 4x+hires sync, C 4x+hires zc,
   D 4x+hires pipelined readback, E 4x+hires zc+pipelined; ≤ 3 boots per hold, ABBA order across
   holds, gap between holds.
3. Optional: X16 clamp check on Mac (`--ssaa 16`, read the `[gs:parallel] quality` line).
4. REPORT.md: knobs, det-hash, frames (send-ready crops listed below), cost tables, zero-copy plan
   (A per platform + B sizing), recommended defaults, gaps.

Send-ready frames (`~/dev/ssx3-work/HR1/compare/`): side-2100.png, side-2380.png (1x up | 4x up |
4x+hires), crop-2100-trees.png, zoom-2100-slope.png, zoom-2380-tree.png, zoom-2100-hud2nd.png,
crop-1090-text.png, ipad-crop-2100.png (iPad display, 1x vs 4x+hires, different moments).

Zero-copy plan notes so far (for the report):
- A, macOS: prototype works (IOSurface export via VK_EXT_metal_objects + CGLTexImageIOSurface2D +
  FBO blit + alpha swizzle); productize ~0.5 day (keep dumps via optional readback, resize handling).
- A, iOS: same Vulkan side (MoltenVK 1.4.2 has VK_EXT_metal_objects); GLES side
  CVPixelBufferCreateWithIOSurface + CVOpenGLESTextureCache → GL_TEXTURE_2D usable directly as a
  raylib Texture2D; no GLES2 swizzle → draw the game quad with blending off. ~1 day incl. device.
- A, Android: AHardwareBuffer imported into Turnip (VK_ANDROID_external_memory_android_hardware_buffer)
  + EGLImage in the Adreno GLES driver. Risk: our app-local Turnip shim makes hw_get_module fail,
  so Turnip's u_gralloc may not know UBWC/layout → request a linear/CPU-readable AHB usage; must be
  proven on the Odin. ~1.5-3 days.
- Pipelined present (done, portable) removes the GPU drain on every platform now; the copies it
  leaves are < 0.5 ms/frame at 1024x896.
- B (Vulkan WSI present, parked): size briefly at resume.
- Brad's GameCube "3x + 75 % display": paraLLEl output is 1x or 2x linear only (X4+hires = 2x2
  samples → 1024x896; X8/X16 add AA on top of 2x); 896 lines ≈ 83 % of a 1080p panel, so
  X4+hires is the nearest match; there is no 3x.

## 15:15 RESUMED (active time used before pause ≈ 40 min; box now ends ≈ 17:36)
- Hold 1 (15:16-15:21, exclusive, quiet host load 2-6, runner-hr1 `15c5348d…`): A 1x 14.16 vs/s,
  B 4x+hires sync 13.24, C 4x+hires zero-copy sync 13.33 (GameThread 81 %: the blit fence still
  waits for all prior rendering). Receipt `mac-cost.md` (below).
- Hold 2 queued from 15:22 (other lanes resumed; waiting for all four slots).
- Mac pipelined smokes (1 slot): pipelined readback frame t2100 correct (trick counter 210 vs 220
  = the expected one frame of latency); zero-copy + pipelined GL texture dump at t2100 is
  **RGB byte-identical** to the pipelined readback frame (md5 e56d4c59… both).
- iPad (4825123 build): 1x pipelined 10.90 vs/s (98 % GameThread) vs 1x sync 10.31; 4x+hires
  pipelined repeat 10.40 (first 10.49). One 1x-pipe launch hit a devicectl transport error
  (CoreDeviceError 1010, app never started); relaunched once, fine.
