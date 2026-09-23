# G42 report — Turnip contrast: Turnip leg FAILED TO START (HAL device exposes no proc-addr query); sys control replicates G41-O1 except C1 LANDED this time

## 0. Outcome first

Mission 1 took branch 3 of the brief ("run fails to start ⇒ table it and
stop; that is not a verdict"). The Turnip `.so` loads and its legacy HMI
HAL opens (rc=0), but the returned HAL device struct has a NULL proc-addr
query (`get_proc=0x0`), so no `vkGetInstanceProcAddr` can be obtained and
the hunk exits 1 by design — before any Vulkan init, before any draw.
Nothing about B's loss under Turnip was measured. Mission 2 did not run
(its precondition, "B still lost under Turnip", is unmet — B under Turnip
is unknown). Mission 3 did not run (no construct named).

New data point from the sys control (same binary, system driver): G41-O1
shape replicated (B lost `eea04488…`, blank scanouts, HOLD rows, C2–C5
byte-exact) **except C1 LANDED byte-exact** (G41-O1: C1 lost nchg=0).
Same kick params; unseparated between Odin run-variance and
loader-hunk perturbation (needs a same-binary rerun; run budget spent).

## 1. Pins and receipts

- Clone `parallel-gs-g7` @ `3a66c19` (+ G26/G28 + G40 wall + G41 canary +
  G42 loader, uncommitted, 1451+/5- across 7 files); Granite `16e7395f`.
- Odin `622c49b1`, Android 15. Keyguard `showing=false` pre-run; battery
  95 %, AC powered. Lease claimed `G42 2026-09-23T00:45:45Z`, released +
  `/data/local/tmp/g42/` removed after pulls. No APK launched (shell
  binary only; nothing to force-stop). No new tombstone (`_23` newest
  before and after).
- Turnip driver: StevenMXZ `Turnip_Gen8_V36.zip` (tag `v36`, 2026-09-08,
  A8xx incl. a830, Vulkan 1.4.359),
  `https://github.com/StevenMXZ/Adreno-Tools-Drivers/releases/download/v36/Turnip_Gen8_V36.zip`,
  zip sha256 `a7b1209e…7388a`; `.so` sha256 `717812c3…1ac29d`
  (14,188,488 B aarch64 ELF, exports one symbol `HMI`).
- Binary SHAs (two matching reads each, plus post-run re-read):
  replayer ELF `37fedbb7f9f13f92` (host pre-push = on-device pre-run =
  on-device post-run), dump `154d9d8577a210fb` (host = on-device),
  Turnip `.so` `717812c3c51fd283` (host = on-device). Mac binary
  `ee1fea70…` (F0 no-perturbation proven pre-resume; see CHECKPOINT).
- Runs: `bash local/research/G42/g42-run-odin.sh both` — leg T
  (`PGS_G42_TURNIP=…/libvulkan_freedreno.so`) RUN_EXIT=1 in <1 s, no PPMs;
  leg S (system control) RUN_EXIT=0, all 10 PPMs, `Done!`.
- Receipts: SSD `/Volumes/Extreme SSD/ps2x-g42/g42-{turnip,sys}-logcat.txt`,
  `g42-sys-g13-dump.gs.*.ppm` (10); share mirror `/Volumes/share/ssx3/
  ps2x-g42/` (same 12 files); loader diff text `local/research/G42/
  g42-loader.diff` (whole replayer-file diff incl. carried G40/G41 hunks).

## 2. Turnip vs system-driver table

| row | Turnip leg (T) | System control (S) |
| --- | --- | --- |
| driver identity (first log line) | `G42: Vulkan loader: /data/local/tmp/g42/libvulkan_freedreno.so` → HMI tag=48574d54 id=vulkan name="Mesa 3D Vulkan HAL" author="Mesa 3D" → `HAL open rc=0` → `HAL dev tag=48574454 get_proc=0x0` → **`HAL has no GetInstanceProcAddr`**, exit 1 | `G42: Vulkan loader: (system)` → Adreno (TM) 830, API 1.3.284, Driver 512.800.58 |
| B at boundary 1 (O3/O3b/G31) | n/a (no init, no draws) | O3 `eea04488c453e75b` nz=149721 head=0; O3b identical; G31 bytes B identical (Mac: `840cd308c91c4d8a`/699122 — fault persists on system driver) |
| scanouts (10/10 SHA) | none produced | all `99418f1b1a94ed9f` (blank; Mac: g8-first/vsync0 `99418f1b`, g8-last/vsync6/vsync7 `bc5ca6de`, vsync1 `7e9daa21`, vsync2 `5d4ff853`, vsync3 `11370e59`, vsync4/5 `6aa54f3b` — content) |
| canary C1–C5 | n/a | §3 |
| G26 / G28 HOLD | absent (exited pre-init) | G26 ×1, G28 ×1 (both HOLD) |
| census / overlap | n/a | 32/32 rows, fov=0 zov=0 clean; cord rows 16/16; recomputed==O4m both sides (`46e36067adb426ea` Odin, `20dc126f006088ea` Mac); hash-input diffs ⊆ {texa, mb46} as in G41 |

## 3. Canary matrix (Mac F0 vs sys-Odin S vs G41-Odin O1)

| cell | Mac F0 (expected) | Sys S (this brief) | G41 O1 (reference) |
| --- | --- | --- | --- |
| C1 PSM0/unmasked FBP492 | LANDED `0c1f0f28e9418a4b`/4932 | **LANDED byte-exact** (`0c1f0f28…`/4932, verd landed=1 nchg=1 chg0=492) | LOST (nchg=0) |
| C2 PSM0/masked FBP496 | LANDED `8803470a2c858767`/4211 | LANDED byte-exact | LANDED byte-exact |
| C3 PSM1/unmasked FBP500 | LANDED `19a7754f3f51bb87`/4211 | LANDED byte-exact | LANDED byte-exact |
| C4 PSM1/masked FBP504 | LANDED `dfce146764938517`/4211 | LANDED byte-exact | LANDED byte-exact |
| C5 snap-exact FBP508 | LANDED `b8d9711bf6c8b8c3`/1328 | LANDED byte-exact | LANDED byte-exact |

All kicks acc=1, restored=1 ×5, arena pre identical
(`e9bec547192d3a43`/36864/vq=2), all `Done!`. Full scorer output:
`python3 local/research/G41/g41-score.py <mac-stderr> <odin-logcat>`.
C1 kick params identical G41-O1 vs G42-S
(`prim=…0006 FBP=492 FBW=8 PSM=0 MSK=00000000 ZBP=511 ZMSK=1
bb=0,0,30,30`); only the verdict flipped. Odin O4m hash varies run to
run (`f5a789e1` G41 vs `46e36067` G42 — the documented garbage variance,
G41 REPORT §3c), consistent with run-variance as one candidate cause.

## 4. Why the Turnip setup failed (one mechanism, no fix attempted)

The adrenotools zip is APK-loader packaging (`meta.json` + `.so`, no ICD
JSON): on a real device it works via adrenotools' linker-namespace hooks
inside an app process. From an adb-shell binary the only door is the
exported `HMI` hw-module entry; `HAL open` succeeds but the resulting
`hw_device_t` carries no Vulkan proc-addr query (get_proc NULL), so there
is no path from the HAL device to `vkCreateInstance`. The hunk correctly
refused silent fallback (exit 1, error in logcat). No rendering-code
change is implicated — the failure is entirely in driver plumbing.

## 5. Budgets: Mac builds/runs 1/1, Odin builds/runs 1/2, ~2.5 h of 5 h.

## 6. The ONE next action (orchestrator decides)

**G43 — Turnip HAL-device-ops probe (one hunk, one build, 1–2 Odin runs
in one session).** Extend the loader hunk to dump the HAL device's full
ops struct (all function pointers, not just get_proc) and attempt
instance creation through whatever query it does expose; same session,
re-run the sys control leg on the same binary (free C1-intermittency
test: C1 lands again ⇒ run-variance, C1 lost ⇒ loader-hunk perturbation
on Odin, which the Mac F0 check cannot see). Rationale: Mission 1's
question is still open and the failure names exactly one construct (the
HAL-device→ICD gap); the C1 flip additionally means Mission 2's premise
("C1-only loss") must be re-checked before any combined wall fires. If
the ops struct has no usable query, the fallback is an APK harness with
adrenotools-style loading — a bigger brief, not a hunk. No workaround
hunt: under a future pure-driver verdict, recommend Turnip bundling per
the product direction.
