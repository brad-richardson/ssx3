# G42 CHECKPOINT (paused 2026-09-22 ~15:20 EDT, Brad needs laptop)

## Done
- Pin verified: clone `parallel-gs-g7` @ `3a66c19`, diff 1369+/4- (G39+G40+G41
  carried), Granite `16e7395f`, G40/G41/G28 markers present, Odin `622c49b1`
  Android 15, tombstone `_23` newest.
- Turnip driver sourced (Mission 1 step 1): StevenMXZ `Turnip_Gen8_V36.zip`
  (tag `v36`, 2026-09-08, for A8xx incl. a830, Vulkan 1.4.359), URL
  `https://github.com/StevenMXZ/Adreno-Tools-Drivers/releases/download/v36/Turnip_Gen8_V36.zip`,
  zip sha256 `a7b1209e…7388a`, `.so` sha256 `717812c3…1ac29d` (14,188,488 B
  aarch64 ELF). In `/Volumes/Extreme SSD/ps2x-g42/` (+ meta.json).
- Key finding: the Turnip `.so` exports ONE symbol (`HMI`, 248 B) — no
  `vk_icdGetInstanceProcAddr`/`vkGetInstanceProcAddr`. HMI decoded from file
  bytes: legacy pointer-layout hw module (tag `0x48574D54`, id→"vulkan",
  name→"Mesa 3D Vulkan HAL", author→"Mesa 3D", methods@32 → open fn @0xa7f2c8,
  disasm consistent with HAL open). Full adrenotools needs APK linker-namespace
  hooks; instead the hunk opens HMI directly (~80 lines, no extra builds).
- Loader hunk applied to clone (uncommitted): `local/research/G42/g42-loader-apply.py`
  (3 asserted edits, DRY-OK + APPLIED 3) → `tools/gs_dump_replayer.cpp`;
  `PGS_G42_TURNIP=<.so path>` gates Turnip, default = system loader, every
  Turnip-path failure exits non-zero (no silent fallback). Backup: `/tmp/g42-pre-replayer.cpp`.
- Mac build OK (`parallel-gs-g42-mac-build`, binary `ee1fea70…`, 51,934,696 B)
  + Mac F0 run OK: G42 first line `(system)`, B cord1 `840cd308…`/699122,
  C1–C5 all landed, 10/10 scanout SHAs == G41 Mac, normalized stderr 0-diff
  vs G41 except timing lines. No-perturbation proven.
- Odin build OK (`parallel-gs-g42-android-build`, `[458/458]`, binary
  `37fedbb7…`, 265,919,448 B, `G42:` marker ×1 in strings).
- Odin run script ready: `local/research/G42/g42-run-odin.sh [turnip|sys|both]`
  (G41-O1 shape, per-run logcat + tagged pulls, no cleanup inside).
- Orchestrator note recorded: if B lands under Turnip → verdict 'bundle Turnip',
  recommend adrenotools-style APK bundling, no workaround hunt (aligns w/ brief).

## In flight (blocked, nothing running)
- Odin runs NOT started: `/data/local/tmp/mg/LEASE` held by `PF1 2026-09-22T18:45:43Z`
  since 14:45 EDT. Waited 14:49–15:20 (~30 min, lease-wait loop killed for pause).
- No lease held by G42, nothing staged on device (`/data/local/tmp/g42/` never
  created), no background builds/runs owned. Other worker's adb logcat (PF1)
  left untouched.

## Exact next step to resume
1. Poll `adb -s 622c49b1 shell cat /data/local/tmp/mg/LEASE` until free.
2. Claim: `adb -s 622c49b1 shell 'echo "G42 $(date -u +%FT%TZ)" > /data/local/tmp/mg/LEASE'`.
3. Run: `bash local/research/G42/g42-run-odin.sh both` (stages dump+binary+Turnip
   `.so`, run T with `PGS_G42_TURNIP`, run S control, pulls all receipts).
4. Release lease (`rm /data/local/tmp/mg/LEASE`), score with
   `local/research/G41/g41-score.py` (mac-vs-turnip, mac-vs-sys), table B/scanouts/
   canary/HOLD rows → branch per brief (Turnip-lands → bundle-Turnip verdict;
   still-lost → Mission 2; fails-to-start → table + stop).
5. Cleanup `/data/local/tmp/g42/`, mirror receipts to share tier, write REPORT.md,
   `[G42]` commit, no push.

## Budgets used
- Mac builds/runs: 1/1. Odin builds/runs: 1/0. Time ~1 h of 5 h box.
