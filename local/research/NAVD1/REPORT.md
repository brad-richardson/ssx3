# NAVD1 — Mac ARM64 Android emulator setup and APK smoke (orchestrator, 2026-09-24)

Purpose: a quick Android install/startup check on the Mac mini, separate from the Odin GPU verdict.

## Installed locally

- Project-local, ignored SDK/AVD: `local/emulator/sdk`, `local/emulator/avd/ssx3_api35_arm64.avd`; no game/APK/image bytes in Git.
- Official ARM64 command-line tools archive `commandlinetools-mac_arm64-15859902_latest.zip`, verified SHA-256 `835b62a26162b229b441d1f6d4680383815a270809eb33522c0d480fa5002c4e` before extraction. Packages: emulator 37.1.11, platform-tools 37.0.1, Android 35 platform and default ARM64 image. Homebrew OpenJDK 17.0.20.1 used only via explicit `JAVA_HOME`; no global Java/OpenCode settings changed.
- AVD booted headless with `-gpu host -no-window -no-snapshot -no-audio -no-boot-anim -memory 4096`, serial `emulator-5580`; `sys.boot_completed=1`, API 35, arm64-v8a. Stopped after smoke with `adb -s emulator-5580 emu kill`.
- Before and after setup, project disk-budget script remained below its 200 GB cap; afterward 156.9 GB used, 88 GiB free. Local emulator tree uses about 5.1 GB.

## Bounded smoke

- Existing N8D7M12P3 APK (153,753,116 bytes, SHA-256 `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`) verified twice locally, installed successfully as `com.ps2x.runner`. Existing replay stream (1,100,696,462 bytes, SHA-256 `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`) verified twice locally and twice on emulator after push. `ps2x.env` verified local/device/device, SHA-256 `91ec6995fb2d56da90b69bfc1cdb4cd3869c28558142e9264f33b60a7c4944ab`.
- Claimed mini P slot 1, cleared emulator logcat, launched `com.ps2x.runner/android.app.NativeActivity`, observed app PID, capped the check at 25 two-second polls (stopped after 14.304 s when an app process exited), captured bounded local logs and output listing, force-stopped package, released slot. Slot 1 and 2 free at postcheck. All ADB calls used explicit emulator serial; Odin was untouched.
- Native entrypoint loaded the env, bundled Turnip library and HAL. Granite then logged `Failed to create Vulkan device`; paraLLEl logged `init_ok=0 init_failed=1`, zero packets/presents, and replay failed. The activity restarted while foregrounded, repeating the failure until force-stop. No frame/hash output was produced. This is an expected compatibility limit for bundled Adreno Turnip on the emulator's virtual GPU, **not** evidence for or against the Odin rendering defect.

Verdict: emulator installation, APK install and native startup path **PASS**. Current APK's Turnip replay/render path **cannot run** on this AVD. Use it for Android packaging/entrypoint checks; use Odin for Adreno/Turnip image comparison. Private full log and result are under ignored `local/emulator/`.
