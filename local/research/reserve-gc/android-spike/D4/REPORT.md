# D4 — Display proof: presented extras at display present time (device)

Part 2 (2026-09-18 ~17:57–19:30 UTC; orchestrator continuation: direct-boot
blocker cleared by 17:27 reboot + 17:52 unlock; `cmd package
resolve-activity` resolves `org.ssx3.onscreen/android.app.NativeActivity`).
Part 1 prep (entry movie/framerate params, Gap-2 hook, trial-d4.apk
42c52be2, run-apk driver, sampler, preflight) is taken as given. No
verdicts; tables, recipes, receipts.

Standing conditions every arm: serial 622c49b1 over USB (wireless flap
unused). Device lease `/data/local/tmp/mg/LEASE` claimed `D4` at start
(was absent), released at end. Host lease read `P1c` throughout (builds
allowed). `dumpsys user` never `RUNNING_LOCKED`. Screen on, brightness
108 (read-only). Battery 87–97, charging, low_power=0. Pre-launch every
arm: `performance_mode=1 fan_mode=4 cpu7max=4320000 cpu0max=3532800`.
Thermal gate CLEAR (<60 C) every arm; kill rule (zone ≥110 C, cpu7
<2.0 GHz 6×) never tripped. No foreign `moderngekko` processes.

## Build / sha inventory

| Artifact | sha256 | Note |
| --- | --- | --- |
| D1 pace binary (headless) | 84de2c22… (full in D1 run.json) | `d1-base-stock-a/b` revision |
| Device module `gGXBE69_recomp.so` | 1c6c89cf… | mtime 2026-09-17 10:45, predates D1; D1 receipts record no module sha |
| Movie `m3-menu.dtm` (parity) | bfa18911… | device file |
| Movie `m3-menu-imm.dtm` (display) | device file | default `kMovie`, ot3-validated |
| APK `trial-d4.apk` (parity + defaults) | 42c52be2… | Gap-2 hook + request params |
| `.so` in trial-d4.apk | 0143bc0e… | |
| APK `trial-d4-fps.apk` (120 Hz arm) | 19b4a9c9… | + dlopen fix, LINK_OK, 1× `GLContextEGL::Swap` |
| `.so` in trial-d4-fps.apk | 6400f295… | |
| Validated trial TU `trial.o` | 2c29d559… (hash-gated, unchanged) | same object ot3 used |

Seed: uncapped (`EmulationSpeed = 0.0`, matches `aff-tpl`) for parity;
capped-original (restored from `Dolphin.ini.d4orig` + `pm clear`) for
display arms (ot3-faithful). Seed GFX `ImmediateXFBEnable=True
CapImmediateXFB=False` matches `d1-base-stock-a` post-run GFX;
trial-probe `configured` rows confirm `immediate_xfb=1` on display arms.

## Parity arm (run FIRST per brief)

Same `m3-menu.dtm`, uncapped, pinned emu→cpu7 + video→cpu6, sampler for
the whole run, onscreen APK path, screen on, no smoothing trial
(`request-parity`: at=999 kind=smoothing secs=4 budget=330
movie=`m3-menu.dtm` framerate=0; at=999 never fires). The APK plays the
movie (`SSX3_MOVIE_PLAY` from the request file), so this is the movie
arm, not the free-ride fallback.

Method, D1-exact (`D1/analyze.py`): content-anchored window (gate→panic),
ticks ±5, roles by max-CPU comm (`GC Adapter Scan`, `Video thread`),
busy = thread CPU-s / tick wall-s, ms/f = CPU-s×1000 / (HUD guest-s×60),
freq = mode-PSR core. APK deltas (stated): no metric `sample=` rows reach
logcat, so TITLE fps (runner title, 1/s) replaces metric fps; HUD caps
carry logged device-wall times. Analyzer: `D4/parity_analyze.py`
(SSD-only, like `D1/analyze.py`).

Window (pinned run): GO! ≈ device 1789771302.5 (HUD 0:01@1303.459,
`bg-d4-parity-9.png`), death 1789771316.66 (sampler EXITED; tombstone_26
copied 18:41:55.8). HUD ladder: 0:01 (5th/6, 0%) → 0:06 (3%, 48 MPH) →
0:13 (5th/6, 6%, 47 MPH).

| Row | d1-base-stock-a (D1) | d1-base-stock-b (D1) | d4-parity (pinned APK) |
| --- | --- | --- | --- |
| Runtime | pace binary 84de2c22 | same | trial-d4.apk 42c52be2 |
| Movie | m3-menu.dtm | same | m3-menu.dtm bfa18911 |
| HUD race pace | 1.273x (14/11) | 1.273x (14/11) | 1.134x (13/11.5); TITLE 1.156x |
| emu busy | 0.93 | 0.92 | 0.86 |
| vid busy | 0.39 | 0.38 | 0.27 |
| emu ms/f | 26.42 | 24.20 | 17.59 |
| vid ms/f | 11.21 | 10.08 | 5.63 |
| cpu7 mean/min/max GHz | 4.30/4.09/4.32 | 4.31/4.20/4.32 | 4.29/4.09/4.32 (emu mode-PSR 7) |
| tmax cpu/gpu C | 103.9/64.5 | 103.9/62.1 | 103.5/61.7 |
| Shutdown counters | 438749/438968 | 443442/439768 | none (tombstone, no graceful exit) |
| SF composition | N/A (headless) | N/A | HWC DEVICE overlay for our layer (race-phase sf-6, attempt4 window) |
| cgroup / cpuset | not recorded in D1 | not recorded | cpu,cpuset:/top-app uid_10136 / `/top-app` |
| Pin | emu cpu7 vid cpu6 verified | same | emu mask 80 (PSR 7) + video mask 40 (PSR 6), set verified + held full run |

Pin receipts: `pin-d4-parity.log` (attempt=0 both, `PIN_END`); sampler
tick0/late PSR 6 (video) / 7 (emu); sampler `taskset -a` pre-pin `ff`.
Panel mode in sf: `1080x1920 vsyncRate=120.00 Hz` (120 Hz on the default
path). Swaps: 7622 over 73.7 s mono, tsok=0/7622 (see §Timestamps).
Gate CLEAR 46.1 C; battery 97 charging.

## Display-timestamp arms

Calibration (recorded): `at=128` (ot3's value) does NOT fire now — two
attempts (`d4-disp0-cold`, `d4-disp0` warm) ended `configured`-only with
the deterministic GatherPipe panic at ~+133–135 s wall. Causes: (1)
probe-now is steady-clock-since-`.so`-load and ot3's 18–19 s cold-install
load is now ~5 s warm-reinstall, so now reaches only ~123–127 by the
fixed-guest-point panic; (2) the first attempt additionally ran cold
shaders (`pm clear` had wiped the parity-warmed cache), stalling now
further. `at=1` proved the machinery healthy (request wall=1.006,
Idle→Requested; never Running = early-menu speed-floor veto, ot1/ot2
pattern). All arms below use at=120, secs=4, budget=154, imm movie,
capped, video+emu pinned (masks verified per pin log).

| Row | default #1 (`d4-calib2`, 42c52be2) | default #2 (`d4-disp120` run 1, 42c52be2) | 120 Hz (`d4-disp120fps`, 19b4a9c9) |
| --- | --- | --- | --- |
| Request | at=120 s=4 b=154 fr=0 | at=120 s=4 b=154 fr=120, dlsym missed → window untouched (default replicate) | at=120 s=4 b=154 fr=120, `OT_FRAMERATE req=120 rc=0` |
| Lifecycle (probe-wall) | req 120.00 → cancel+complete 124.00 | req 120.00 → cancel 124.01 + complete 124.02 | req 120.00 → cancel 124.01 + complete 124.02 |
| frames / extras / blended / limited | 327 / 93 / 93 / 0 | 326 / 97 / 97 / 0 | 324 / 91 / 91 / 0 |
| Swaps in-window (/s) | 327 (81.7) | 326 (81.3) | 325 (81.0) |
| Per-second swaps | 71/92/69/95 | 72/67/92/94 | 73/71/87/92 |
| Distinct display presents | 0 | 0 | 0 |
| Swap-return spacing ms med/p95/p99 | 12.00/16.89/17.49 | 12.00/17.01/19.65 | 12.09/16.95/19.65 |
| Rows with frame timestamps | 0/327 | 0/326 | 0/325 |
| In-window race cap | shot24: 5th/6, HUD 0:11, 5%, 50 MPH | shot24: 5th/6, HUD 0:10, 5%, 52 MPH | shot24: 5th/6, HUD 0:10, 5%, 51 MPH |
| SF our-layer comp | DEVICE (in-trial sf-24) | DEVICE | DEVICE |
| SF explicit-rate column | (empty) | (empty) | `120.00 ExactOrMultiple OnlySeamless` |
| Death | panic ~1 s after complete (ot3-like) | panic (tombstone_30) | panic after complete |

Acceptance frame of reference (`120hz-pacing-acceptance.md`, no
declaration): ≥117/s, med ≤8.6 ms, p95 ≤10 ms, p99 ≤17 ms.

## Timestamps: unavailable on this path

`eglGetNextFrameIdANDROID` resolves and frame ids increment 1:1 with
swaps (`FRAME_TS procs resolved` in early-logcat; EGL advertises
`EGL_ANDROID_get_frame_timestamps`), but every
`eglGetFrameTimestampsANDROID` query (current + previous frame id)
returns nothing: tsok=0 on all 7622 parity rows and all 327+326+325
trial rows (6 runs total). `analyze_display.py` therefore reports
`NO DATA` for distinct presents and present spacing; the per-second and
swap-return-spacing columns above are the measurable remainder.

## Recipes (exact)

Parity: `pm clear` (once, after uncapping seed) then
`./run-apk.sh d4-parity request-parity
…/onscreen-trial/apk/trial-d4.apk 180`.
Display default: `./run-apk.sh d4-calib2 request-calib2 …/trial-d4.apk
240` (request at=120, no movie/framerate lines → imm default).
Display 120 Hz: rebuild (`cp SSD src → /tmp/android-onscreen/src`;
new debug keystore — original was reboot-wiped from /tmp;
`python3 build_trial.py` → LINK_OK; `nm` 1× `GLContextEGL::Swap()`;
`python3 package_trial.py` → stage `apk/trial-d4-fps.apk` + sha file;
`pm uninstall` (signature change) + warm free ride) then
`./run-apk.sh d4-disp120fps request-disp120 …/trial-d4-fps.apk 240`.

## File list (new/changed, all under the allowed paths)

`D4/REPORT.md` (this file); `D4/run-apk.sh` (device-side bootstrap,
bg caps/sf, pin-by-name via run-as, early-logcat, sdcard cleanup, APK
sha log); `D4/d4-pin.sh`, `D4/d4-bg.sh`, `D4/d4-bootstrap.sh` (new);
`D4/apk-sampler.sh`, `D4/preflight.sh` (unchanged from Part 1);
`D4/parity_analyze.py`, `D4/analyze_display.py` (SSD-only analyzers);
`D4/request-*` (all request files); per-arm `*-receipts/` dirs
(run.json, probes, sampler, sf-dev, caps, pin/bg logs, GFX-post,
early-logcat); `D4/run-notes.log`, `D4/waits.log`,
`D4/thermal-waits.log`, `D4/runner-*.log` (appended, never overwritten);
attempt dirs kept: `d4-parity-attempt[1-8]-receipts`,
`d4-disp0-cold-nofire-receipts`, `d4-disp120-at128-nofire-receipts`.
`onscreen-trial/src/trial_entry.cpp` (dlopen fix + comment),
`onscreen-trial/apk/trial-d4-fps.apk` + `sha256-d4-fps.txt`.
Repo: untouched (`git status` clean) → no commit.

## What I could not do

- Distinct display presents per second: unmeasurable — Adreno returns no
  frame timestamps on this path (see §Timestamps). Swap-return spacing is
  reported instead; no pass/fail declared.
- `at=128` as briefed: does not fire under current warm-install timing
  (two documented no-fire attempts); at=120 is the calibrated equivalent
  (same race zone, full lifecycles, in-race caps).
- Headless cgroup/cpuset side-by-side: D1 recorded none; APK side only.
- Metric `sample=` rows in the APK: never reach logcat (0 rows all runs);
  TITLE fps used instead (method stated, analyzer committed).
- D1 `min50-90`/tail columns for the APK: no metric samples (TITLE min in
  window: 49.4) and no tail (deterministic panic ends every run).
- `d4-disp0` (at=128) and first `d4-disp120` (stale at=128) arms: no trial
  fired; kept as no-fire receipts, not measured arms.
- No repo commit: the brief's commit rule covers files the D4 section
  names (`REPORT.md`, APK sha, probes — all SSD-side); the repo tree is
  untouched, so there is nothing to commit.

## Conservative choices made while the brief is silent

- Display arms replicate ot3 exactly (capped seed, imm movie, smoothing
  4 s) except the recalibrated at; framerate=0 default leaves the window
  untouched.
- Driver fixes (device-side bootstrap/pin/caps, run-as taskset, sdcard
  cleanup, early-logcat, by-name-only emu pin) are logged per attempt in
  `run-notes.log`; failed attempts kept, never overwritten.
- Thread names carry spaces on device (`Video thread`, `GC Adapter
  Scan`); the sampler underscores them — pin patterns updated, analyzer
  matches sampler output. Emu thread spawns as `Emuthread - Sta…` and
  renames to `GC Adapter Scan` at emulation start (validates D1's comm).
- Stale same-tag `/sdcard` caps (12/13/0 from older runs) found, purged,
  driver now cleans per tag; `caps-list.txt` still lists them as pulled.

## Part 3 — presents counted by SurfaceFlinger timestats (2026-09-18 ~23:41–23:49 UTC)

EGL frame timestamps return nothing on this Adreno path (Part 2 §Timestamps),
so presents are counted here from `dumpsys SurfaceFlinger --timestats -dump`
sampled every 1.0 s on-device: per-tick deltas of per-layer `totalFrames` /
`droppedFrames` and of the present-to-present histogram (layer:
`present2present`; global: `presentToPresent`), spacing from bucket midpoints
(bucket start + 0.5 ms; exact for the 1 ms buckets where all in-window
spacings fall). No verdicts; tables, recipes, receipts.

Standing conditions as Part 2 except: device lease `D4c` (claimed before
arm A when absent, `D4c\n` verified by byte read; released at end), thermal gate
50 C (`D4_PREFLIGHT_GATE=50000`; CLEAR every arm), `dumpsys user` never
`RUNNING_LOCKED`, screen on brightness 108, battery 100 charging
low_power=0 all arms, `performance_mode=1 fan_mode=4 cpu7max=4320000
cpu0max=3532800` per preflight snapshot. Driver is Part 2 v11 plus the
Part 3 wiring only (push `part3/sfstats.sh`, start it from
`d4-bootstrap.sh` next to `d4-sampler.sh`, `touch ...stop` after the
monitor loop, pull `sfstats-<tag>.log`); lease check updated `D4`→`D4c`.
Seed capped (matches `seed-trial/Config/Dolphin.ini.d4orig` byte-for-byte
at end) except arm c (uncapped, then restored; restore verified by diff).
APKs unchanged: `trial-d4.apk` 42c52be2, `trial-d4-fps.apk` 19b4a9c9,
module `gGXBE69_recomp.so` 1c6c89cf.

Analyzer idle validation: 10 s launcher capture (`part3/idle-test-receipts/`,
39 ticks, no `ssx3` layer, global-only): static screen shows 0–2
presents/s (burn-in refresher; ticks 0–37 ≈ 0.7/s; tick 38 = 77, activity
artifact of the stop/pull itself). Expectation (~0 once static) met.

Exact layer names used (one per arm; suffix is the SurfaceFlinger instance
id, stable within a run):

| Arm | layerName |
| --- | --- |
| d4-p3-default | `org.ssx3.onscreen/android.app.NativeActivity#829` (129/130 ticks) |
| d4-p3-120fps | `org.ssx3.onscreen/android.app.NativeActivity#857` (129/130 ticks) |
| d4-p3-uncapped-notrial | `org.ssx3.onscreen/android.app.NativeActivity#885` (65/66 ticks) |

Early ticks of each run show only `NavigationBar0`, `StatusBar`, `none`
(activity not yet created).

### Per-arm table

Window = request→cancel/complete mapped to mono by the Part 2 method
(`analyze_display.py`); arm c has no window (at=999 never fires:
trial-probe is `configured`-only, 138 bytes), so whole-run rates are
reported with stated denominators instead. Swap-return spacing rows are
from the existing analyzer (`analyze_display.py`); arm c whole-run swap
spacing computed by the same quantile method. Panel-config time: this
build's `-dump` has no per-config time table (`displayConfigStats` shows
only `totalP2PTime`); the receipts are the per-tick
`displayRefreshRate = 120 fps` lines plus the sf-snapshot mode lines
quoted below. `droppedFrames` = 0 on every tick of every arm (layer and
global).

| Row | d4-p3-default (trial-d4.apk, fr=0) | d4-p3-120fps (trial-d4-fps.apk, fr=120) | d4-p3-uncapped-notrial (trial-d4.apk, uncapped, 75 s force-stop) |
| --- | --- | --- | --- |
| Trial lifecycle (probe-wall) | req 120.000 → cancel 124.005 + complete 124.010; 325 frames / 90 extras / 90 blended / 0 limited | req 120.000 → cancel+complete 124.002; 330 / 97 / 97 / 0; `OT_FRAMERATE req=120 rc=0` in early-logcat | configured-only (at=999 never fires); `immediate_xfb=0` in configured row but runtime `GFX-post.ini` `ImmediateXFBEnable=True CapImmediateXFB=False` like the other arms |
| swaps/s in window | 81.1 (325 / 4.01 s mono); per-s 72/93/68/91 | 82.5 (330 / 4.00 s); per-s 74/82/79/95 | n/a (no window); whole-run 101.2/s (7189 swaps / 71.0 s swap-mono span) |
| SF presents/s in window (layer) | 90.9 (364 / 4.01 s; 5 ticks) | 74.7 (299 / 4.00 s; 4 ticks) | n/a; whole-run 83.0/s (5497 / 66.2 s sfstats-uptime span) |
| SF presents/s (global) | 91.4 (366) | 75.0 (300) | n/a; whole-run 86.3/s (5715 / 66.2 s) |
| dropped (layer / global) | 0 / 0 | 0 / 0 | 0 / 0 |
| present spacing ms med/p95/p99 (layer) | 16.50 / 16.50 / 24.50 (n=364) | 16.50 / 16.50 / 24.50 (n=299) | 8.50 / 24.50 / 33.50 (n=5497, whole-run) |
| present spacing ms med/p95/p99 (global) | 16.50 / 16.50 / 24.50 (n=366) | 16.50 / 16.50 / 24.50 (n=299) | 8.50 / 24.50 / 33.50 (n=5713, whole-run) |
| swap-return spacing ms med/p95/p99 (existing analyzer) | 12.113 / 16.913 / 17.522 (n=324) | 11.822 / 16.841 / 20.429 (n=329) | 7.486 / 23.703 / 33.612 (n=7188, whole-run, same method) |
| presents/swaps | 1.141 layer / 1.147 global (window) | 0.917 / 0.920 (window) | ~0.77 / ~0.80 (whole-run; spans differ, see note) |
| panel at 120fps | `mDisplayModePtr={…1080x1920, vsyncRate=120.00 Hz…}` in all 5 sf snapshots; timestats `displayRefreshRate = 120 fps` every tick | same panel mode; additionally `requestedFrameRate: {120.00 Hz ExactOrMultiple}`, composition row `120.00 ExactOrMultiple OnlySeamless`, touch vote `(uid, frameRate)={10137, 120.00 Hz}` | same panel mode lines in all 3 sf snapshots |
| composition type (our layer, in-trial sf) | DEVICE (HWC overlay; sf-24, wall 1789775052.29, in-window) | DEVICE (sf-24; explicit-rate column `120.00 ExactOrMultiple OnlySeamless`) | DEVICE (sf-6 mid-run; explicit-rate column empty) |
| explicit-rate column | (empty) | `120.00 ExactOrMultiple OnlySeamless` | (empty) |
| pin | video mask 40 + emu mask 80, set verified + held | video mask 40 + emu mask 80, set verified + held | video mask 40 verified; emu UNPINNED (by-name rule: `GC Adapter Scan` not visible at pin time, `Emuthread - Sta` still; no loader fallback, as ot3) |
| thermal / battery | CLEAR 39.2 C / 100 chg | CLEAR 46.1 C / 100 chg | CLEAR 47.3 C / 100 chg |
| in-window screenshot | `bg-d4-p3-default-24.png` (wall 1789775052.28; window epoch 1789775049.90–5053.91 via tick anchor) | `bg-d4-p3-120fps-23.png` (wall 1789775231.13; window epoch 1789775229.35–5233.35) | no window; mid-run `bg-d4-p3-uncapped-notrial-6.png` (sf-6) |
| death | panic ~t+147 s, `tombstone_02` (device 19:44) | panic ~t+147 s, `tombstone_03` (device 19:47) | host force-stop at t+75 s; no tombstone |

Acceptance frame of reference (`120hz-pacing-acceptance.md`, no
declaration): ≥117/s, med ≤8.6 ms, p95 ≤10 ms, p99 ≤17 ms.

### Per-second series, 120fps arm (before / during / after the window)

Window mono 8387.484 → 8391.485 (W-marked). Columns: layer dTotal/dDrop,
layer p2p med/p95/p99, global dTotal/dDrop, swaps in the same second.

| tick | up (mono) | layer | layer p2p | global | swaps | win |
| --- | --- | --- | --- | --- | --- | --- |
| 115 | 8380.26 | 65/0 | 16.5/16.5/16.5 | 65/0 | 60 | |
| 116 | 8381.28 | 62/0 | 16.5/16.5/23.1 | 62/0 | 60 | |
| 117 | 8382.30 | 61/0 | 16.5/16.5/19.7 | 61/0 | 60 | |
| 118 | 8383.33 | 61/0 | 16.5/16.5/16.5 | 61/0 | 48 | |
| 119 | 8384.35 | 49/0 | 16.5/24.5/111.1 | 50/0 | 65 | |
| 120 | 8385.37 | 67/0 | 16.5/16.5/19.2 | 81/0 | 60 | |
| 121 | 8386.39 | 61/0 | 16.5/24.5/24.5 | 65/0 | 60 | |
| 122 | 8387.41 | 61/0 | 16.5/16.5/16.5 | 61/0 | 71 | W |
| 123 | 8388.43 | 74/0 | 16.5/16.5/24.5 | 74/0 | 87 | W |
| 124 | 8389.46 | 86/0 | 8.5/16.5/17.7 | 86/0 | 76 | W |
| 125 | 8390.48 | 78/0 | 8.5/16.5/51.6 | 79/0 | 96 | W |
| 126 | 8391.50 | 97/0 | 8.5/16.5/16.5 | 97/0 | 61 | |
| 127 | 8392.52 | 64/0 | 16.5/16.5/16.5 | 63/0 | 60 | |
| 128 | 8393.54 | 61/0 | 16.5/16.5/19.7 | 61/0 | 43 | |
| 129 | 8394.56 | 42/0 | 16.5/24.5/24.5 | 120/0 | 0 | |

(Full per-tick tables for all three arms: `sfstats-analyze.txt` beside
each arm's log. Tick 129 global 120 = status/nav-bar burst at process
death.)

### Scripts (quoted)

`D4/part3/sfstats.sh` (device-side; `<tag>` first arg per brief, optional
pid/pkg for the death-stop; tick line is `=== <epoch.ms>` plus a
monotonic-clock anchor used to align swap seconds and the trial window):

```sh
#!/system/bin/sh
# sfstats.sh TAG [PID] [PKG]  (D4 Part 3 device-side SurfaceFlinger timestats sampler.)
# Runs on the Odin from /data/local/tmp/mg. Enables + clears timestats,
# then every 1.0 s appends "=== <epoch.ms>" plus the full
# "dumpsys SurfaceFlinger --timestats -dump" to
# /data/local/tmp/mg/sfstats-<tag>.log until the stop file
# /data/local/tmp/mg/sfstats-<tag>.stop appears or the app pid dies;
# then disables timestats. dumpsys runs as shell (no run-as needed).
TAG=${1:?tag}; PID=${2:-}; PKG=${3:-}
cd /data/local/tmp/mg || exit 1
LOG=/data/local/tmp/mg/sfstats-$TAG.log
STOP=/data/local/tmp/mg/sfstats-$TAG.stop
rm -f "$LOG" "$STOP"
dumpsys SurfaceFlinger --timestats -enable >/dev/null 2>&1
dumpsys SurfaceFlinger --timestats -clear >/dev/null 2>&1
echo "SFSTATS_START wall=$(date +%s.%N) epoch_ms=$(date +%s%3N) uptime=$(cat /proc/uptime 2>/dev/null) tag=$TAG pid=[$PID] pkg=[$PKG]" >> "$LOG" 2>&1
while true; do
  if [ -f "$STOP" ]; then
    echo "SFSTATS_STOP wall=$(date +%s.%N) reason=stopfile" >> "$LOG" 2>&1
    break
  fi
  if [ -n "$PID" ] && [ ! -d /proc/$PID ]; then
    echo "SFSTATS_STOP wall=$(date +%s.%N) reason=pid-gone pid=$PID" >> "$LOG" 2>&1
    break
  fi
  if [ -z "$PID" ] && [ -n "$PKG" ]; then
    if ! pidof "$PKG" >/dev/null 2>&1; then
      echo "SFSTATS_STOP wall=$(date +%s.%N) reason=pkg-gone pkg=$PKG" >> "$LOG" 2>&1
      break
    fi
  fi
  echo "=== $(date +%s%3N) $(cat /proc/uptime 2>/dev/null)" >> "$LOG" 2>&1
  dumpsys SurfaceFlinger --timestats -dump >> "$LOG" 2>&1
  sleep 1
done
dumpsys SurfaceFlinger --timestats -disable >/dev/null 2>&1
echo "SFSTATS_END wall=$(date +%s.%N) tag=$TAG" >> "$LOG" 2>&1
```

`D4/part3/sfstats_analyze.py` (`<log> <layer-substring> <swaplog>`;
319 lines; parses global + per-layer sections, accepts both
`presentToPresent` (global) and `present2present` (layer) spellings,
global dropped = `missedFrames`, finds `trial-probe.jsonl` beside the
swap log for the mono window via the `analyze_display.py` wall→mono map,
aligns swap seconds via the per-tick uptime anchor): quoted by path —
`D4/part3/sfstats_analyze.py` (receipt; full text in the evidence root).

### Exact commands

```sh
adb -s 622c49b1 shell 'dumpsys SurfaceFlinger --timestats -enable; dumpsys SurfaceFlinger --timestats -clear; dumpsys SurfaceFlinger --timestats -dump'  # verified pre-arm
printf 'D4c\n' | adb -s 622c49b1 shell 'cat > /data/local/tmp/mg/LEASE'   # lease claim (was absent)
cp D4/request-calib2 D4/part3/request-p3-default
cp D4/request-disp120 D4/part3/request-p3-120fps
cp D4/request-parity D4/part3/request-p3-uncapped   # byte-identical (diff rc=0)
D4_PREFLIGHT_GATE=50000 ./run-apk.sh d4-p3-default part3/request-p3-default …/onscreen-trial/apk/trial-d4.apk 240
D4_PREFLIGHT_GATE=50000 ./run-apk.sh d4-p3-120fps part3/request-p3-120fps …/onscreen-trial/apk/trial-d4-fps.apk 240
# arm c only: uncap + pm clear, then restore + verify against backup
adb -s 622c49b1 shell 'printf "[Core]\nEmulationSpeed = 0.0\n" >> /data/local/tmp/mg/seed-trial/Config/Dolphin.ini; pm clear org.ssx3.onscreen'
D4_PREFLIGHT_GATE=50000 ./run-apk.sh d4-p3-uncapped-notrial part3/request-p3-uncapped …/onscreen-trial/apk/trial-d4.apk 75
adb -s 622c49b1 shell 'grep -v -e "^EmulationSpeed" … > …tmp; mv …tmp …Dolphin.ini'  # + re-add [Core] header
diff /data/local/tmp/mg/seed-trial/Config/Dolphin.ini.d4orig /data/local/tmp/mg/seed-trial/Config/Dolphin.ini  # rc=0
python3 D4/part3/sfstats_analyze.py <receipts>/sfstats-<tag>.log ssx3 <receipts>/swap-probe.jsonl > <receipts>/sfstats-analyze.txt
python3 D4/analyze_display.py <receipts>/swap-probe.jsonl <receipts>/trial-probe.jsonl  # swap-return spacing
adb -s 622c49b1 shell 'rm /data/local/tmp/mg/LEASE'   # lease release
```

### Receipt paths (all under `/Volumes/Extreme SSD/android-spike/D4/`)

`part3/sfstats.sh`, `part3/sfstats_analyze.py`,
`part3/request-p3-{default,120fps,uncapped}`,
`part3/idle-test-receipts/{sfstats-idle-test.log,empty-swap.jsonl,analyze.txt}`,
`d4-p3-default-receipts/`, `d4-p3-120fps-receipts/`,
`d4-p3-uncapped-notrial-receipts/` — each with `swap-probe.jsonl`,
`sfstats-<tag>.log` (130/130/66 ticks), `sfstats-analyze.txt`,
`trial-probe.jsonl`, `d4-<tag>-sampler.log`, `pin-<tag>.log`,
`bg-<tag>-shots.log`, 25/25/13 pngs, `sf-dev/sf-<tag>-{0,6,12,18,24}.txt`
(3 for uncapped: {0,6,12}), `cgroup.txt`, `cpuset.txt`, `GFX-post.ini`,
`early-logcat.txt`, `logcat.txt`, `run.json`;
`runner-d4-p3-{default,120fps,uncapped-notrial}.log`, `run-notes.log`,
`thermal-waits.log`, this `REPORT.md`.

### What I could not do

- Distinct display presents from EGL frame timestamps: still nothing
  (tsok=0 on all in-window rows of both trial arms, as Part 2); SF
  timestats counting is the substitute, not the same signal.
- Per-config time-at-120fps table: this build's `--timestats -dump` has
  no such table (`displayConfigStats` = `totalP2PTime` only); panel-mode
  receipts above are the substitute.
- Arm c swap/window alignment: no trial window exists (by design), so
  presents/s and swaps/s use different spans (66.2 s sfstats uptime vs
  71.0 s swap-mono); the ~0.77 ratio is whole-run, not windowed.
- Arm c emu pin: unpinned by the standing by-name-only rule (thread had
  not renamed at pin time); video pinned. Same situation as ot3.
- Arm c `configured` row reports `immediate_xfb=0` although runtime
  `GFX-post.ini` matches the other arms; cause not chased (counting
  unaffected).
- No repo commit: all outputs are on the SSD; the repo tree is untouched.
