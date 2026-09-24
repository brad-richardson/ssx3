# N8B2 — one Odin Turnip app-process launch

Worker: Codex. Brief: `local/muse/prompts/N8B2.md`. Date: 2026-09-24. The orchestrator decides the gate. No fork edit or push.

## First unmet runtime gate

The one Odin launch selected the parallel backend and requested bundled Turnip, then `dlopen` failed because `libhardware.so` was unavailable in the app namespace. The same-PID log at epoch `1790236087.703` is:

```text
7240 7262 I ps2x: [gs:parallel] Turnip dlopen failed: dlopen failed: library "libhardware.so" not found: needed by /data/app/~~Mxepu1LrYjvT0Zd3nM0kFw==/com.ps2x.runner-ava8jYJl3j2yE5kMh08e3A==/base.apk!/lib/arm64-v8a/libvulkan_freedreno.so in namespace clns-7
7240 7262 I ps2x: [gs:parallel] FATAL: Context::init_loader failed (frames will be empty)
```

The app was force-stopped after this definitive requested-Turnip failure. There was no second launch. This is a loader dependency/namespace failure; HMI, Granite identity, GIF/present counters, and race visuals were not reached.

## Pin and preflight table

| Gate | Observation |
| --- | --- |
| Source APK, bytesize | `/home/brad/n8b1/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk`, 153,687,506 bytes; SHA-256 `1096a28e2e343fbcfc1d28390ea72a8e3d2aee32f3c40b81102e773c50b190da` on two independent source reads. N8B1 source `n8-turnip-apk` @ `17e90de`; packaged runner SHA `cdbaa6dd6eaf77a9026fb1fc5a291c15054f4d396e44b37ee3655705d10eb033`, Build ID `28340bbe3652b251a6ecda201cf6ae01f6550add`, bundled Turnip member SHA `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` per N8B1 pin. |
| Mac APK | `~/dev/ssx3-work/N8B2/app-release.apk`, 153,687,506 bytes; SHA-256 `1096a28e2e343fbcfc1d28390ea72a8e3d2aee32f3c40b81102e773c50b190da` / same. Kept outside Git. |
| Install | Exactly one `adb -s 622c49b1 install -r`; `Performing Streamed Install`, `Success`. Installed `/data/app/~~Mxepu1LrYjvT0Zd3nM0kFw==/com.ps2x.runner-ava8jYJl3j2yE5kMh08e3A==/base.apk`; SHA-256 `1096a28e2e343fbcfc1d28390ea72a8e3d2aee32f3c40b81102e773c50b190da` / same before launch. Rechecked twice after the repaired prelaunch check; same pair. |
| Staged stock ELF | `files/SLUS_207.72`; SHA-256 `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` / same before launch; matches E55B2 pin. Rechecked twice after repair. |
| Staged stock ISO | `files/SSX3.iso`; SHA-256 `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same before launch; matches N7 pin. Rechecked twice after repair. |
| First preflight | Odin `622c49b1` connected; `/data/local/tmp/mg/LEASE` was `LEASE_FREE N7 done …`; `KeyguardServiceDelegate showing=false`; battery 100%, status 5 (full/charging). |
| Launch preflight | After claiming `N8B2 one-launch`, device connected, lease owned by N8B2, keyguard `showing=false`, battery 100%, status 5. Empty `files/mc0` verified. |
| Environment | `PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`, dev-only `PS2X_SKIP_MOVIE=1`, `PS2X_CD_IMAGE=files/SSX3.iso` absolute device path, exact I26-FAST route with `PS2X_PAD_SCRIPT_CLOCK=vsync`, and `PS2X_VSYNC_RATE_LOG=1` for progress only. Device env SHA-256 `d2ab46b4c725b2a7ecca2c50ac26b9184d0b10f8d4d62629afde6a9c038404a5`. |

## Launch evidence

| Requested observation | Same-PID result |
| --- | --- |
| App PID / cleanup | `am start -n com.ps2x.runner/android.app.NativeActivity` once; PID `7240`; force-stop completed, PID absent; lease `LEASE_FREE N8B2 done` verified again independently. |
| Backend selection | PID 7240: `[gs:queue] enabled (forced by PS2X_GS_BACKEND=parallel)` and `[gs:parallel] live backend selected (PS2X_GS_BACKEND=parallel)`. |
| Requested Turnip | PID 7240: `[gs:parallel] Turnip requested via PS2X_GS_TURNIP=1`; `GRANITE_VULKAN_LIBRARY=(unset)`; then the `libhardware.so` `dlopen` error above. |
| `dladdr(HMI)` mapped APK path | Not found: failure occurred before `dlsym(HMI)` or `dladdr(HMI)`. The APK member path in the loader error proves the requested library was located, not that HMI loaded. |
| HAL `open("vulkan0")` / operation addresses | Not found: not reached. |
| Granite device/API/driver | Not found: not reached. OpenGL's `Adreno (TM) 830` line is from raylib and does not establish Turnip Vulkan identity. Expected G43 Turnip API 1.4.359 / driver 26.2.99 remains unproved. |
| `[gs:parallel] init` | `FATAL: Context::init_loader failed (frames will be empty)`; no `init ok`. |
| GIF/presents / SF latency | No nonzero backend counters or SF latency sample before early stop. System Vulkan or CPU fallback was not observed. |
| Title/menu and race images | None: stopped at the first definitive requested-Turnip failure, before a valid game frame. Race tick target 2050 not reached; no speed number quoted. |

## Repaired prelaunch attempt

The launcher’s first run passed preflight, claimed the lease, installed the APK once, and verified installed APK, ELF, and ISO hashes. Its second preflight incorrectly required `LEASE_FREE` even though N8B2 held the lease. This was a launcher self-check error **before any `am start`**. It force-stopped the app and released the lease. I changed that second check to accept the exact `N8B2 one-launch` owner and made `pidof` exit 1 mean PID absent. The continuation used `--resume-after-install`, skipped install, reclaimed the free lease, repeated device hash pairs and the keyguard/battery/lease checks, then made the one actual launch. Both attempts are recorded in `driver.log`.

Receipts committed here: `driver.log`, `logcat-pid.txt` (PID 7240 only), `ps2x.env`. Full tiny log and the 153.7 MB APK remain under `~/dev/ssx3-work/N8B2/` with `launch.py` and `result.json`. New Mac bytes were about 154 MB, under the 1 GiB cap; text logs were about 22 KiB and images 0 bytes. No second launch, build, profile, fork edit, or push.
