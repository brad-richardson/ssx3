# M4 — Android runtime rebuild: armv8.2+LSE, no outline atomics, shader-cache persistence

Date: 2026-09-17/18 (device runs 23:09 EDT → 01:0x EDT). Executor: muse session, herdr pane wN:p3.
Method note: this report contains tables, recipes, and receipts only, per M4.md.

## 0. Workload caveat (read first)

Window-anchored emulator screenshots show the **pause menu** (MCOMM −12 °C,
Return/Restart/Audio/Options/Quit) on every checked frame of the analysis
window — the `m3-menu.dtm` movie pauses the game and never unpauses. So all
numbers below are **pause-menu emulation at full rate**, not race pace, on all
five arms identically. The step-2 "race-start dip" column is therefore
pause-menu pace, labelled as such.

Anchored shots (pulled to receipts): `shots/win-lo.png` (≈ sample 45),
`shots/win-hi.png` (≈ sample 55) in each `m4-base-*-receipts/` dir.

## 1. Rebuild: armv8.2-a+crc+lse, -mno-outline-atomics

- Pristine `m4-src` worktree + patch stack; live tree untouched. Build ran
  `-j4` under host lease `/tmp/ssx3-host-lease` (id M4-build, released after;
  overlap loads in `host-waits.log`).
- New files (committed `[M4]`, one commit, these two files only):
  - `native/patches/recompcore-android-flags.patch` — CMake hunk:
    `-O3 -march=armv8.2-a+crc+lse -mno-outline-atomics`.
  - `native/patches/moderngekko-android-flags.patch` — EGL-ON fix: the first
    LSE binary failed video init (`Failed to initialize video backend`)
    because an outer `ENABLE_EGL OFF FORCE` plus an ExFAT zero-read link ghost
    combined; fixed the EGL hunk and relinked via an APFS-side workaround.
- `nm` on the pushed binary: **0 `__aarch64_*` outline-atomics references**.
- Binaries (pushed to `/data/local/tmp/mg/`, sha256-verified at push):

| device name | sha256 (prefix) | role |
|---|---|---|
| (A/B base binary) | `84de2c226c87d831` | base, 3 arms |
| `moderngekko-run-lse` | `106087350ff327ef` | LSE, 2 arms |
| `moderngekko-run-trial-lse` | `220488ca10868785` | step-4 trial-TU relink (FIFO fix 309f639 in tree) |

Note: at report time the device holds only `moderngekko-run-trial-lse`; the
A/B binaries are no longer on the device (per-run push names, since cleaned).
All run receipts record their sha256.

## 2. Shader-cache persistence (D1 evidence + corroboration)

- D1 evidence (`android-spike/D1/run-notes.log`, d1-cache-late): after a 330 s
  graceful stop the user dir contains only
  `Config/Dump/GC/Load/ScreenShots/Wii/config.ini` — **NO `Cache/` dir** —
  and zero shader/cache lines in err+out. Treated as the D1 finding: no
  persisted shader cache exists to save or seed.
- M4 corroboration: device user dirs `user-m4-base-a`, `user-m4-lse-a`,
  `user-m4-control-probe` contain no `Cache/` dir; the only
  shader|cache-matching stderr lines in the LSE arms are the asset-list lines
  `[ssx3-assets] metadata cache hit (110 files)` (×2), which are not GPU
  shader cache. Hence **no graceful-stop change and no warmed-`Cache/` seed**
  (nothing is ever written, so there is nothing to save and no warm state to
  construct). Warm-vs-cold dip A/B is moot; the extra base repeat (`m4-base-b2`)
  covers dip variance instead.

## 3. Device A/B: base ×3, LSE ×2, interleaved, pinned, uncapped, D1 sampler

Launch shape (all arms): `--template aff-tpl --movie m3-menu.dtm
--module gGXBE69_recomp.so --graphics OGL --idle on --affinity emu=80,video=40
--sampler --screenshot-seconds 2`, stock clocks, device lease M4
(`/data/local/tmp/mg/LEASE`, released after this report).
Run order (device wall): base-a 23:15 → base-b 00:06 → lse-a 00:36 →
base-b2 00:45 → lse-b 00:51 → control-probe 01:03.
Analysis: `android-spike/M4/analyze.py` (same sampler math as D1: jiffy deltas
per tick, per-guest-frame via metric speed), window samples 43–55.

| arm | binary sha | speed med (43–55) | pace min (50–90, pause-menu) | emu ms/frame med | video ms/frame med | pause-tail med (≥230) | cpu7 med/min GHz | tmax °C | shutdown | panic |
|---|---|---|---|---|---|---|---|---|---|---|
| m4-base-a | 84de2c22 | 1.239 | 1.239 | 11.98 | 3.65 | 2.242 | 4.32 / 4.09 | 103.5 | yes | no |
| m4-base-b | 84de2c22 | 1.255 | 1.198 | 11.76 | 3.62 | 2.201 | 4.32 / 4.32 | 103.5 | yes | no |
| m4-base-b2 | 84de2c22 | 1.201 | 1.186 | 12.30 | 3.75 | 2.192 | 4.32 / 4.32 | 103.9 | yes | no |
| m4-lse-a | 10608735 | 1.170 | 1.156 | 12.77 | 3.77 | 2.218 | 4.32 / 4.09 | 104.3 | yes | no |
| m4-lse-b | 10608735 | 1.370 | 1.225 | 10.97 | 3.46 | 2.209 | 4.32 / 4.32 | 104.3 | yes | no |

Observations (no verdicts):
- Base emu ms/frame spans 11.76–12.30 across repeats; LSE spans 10.97–12.77.
  The LSE pair straddles the base range with the direction flipping between
  repeats (lse-a slowest of all five, lse-b fastest). Video-thread numbers
  show the same straddle (base 3.62–3.75, LSE 3.46–3.77).
- All arms: graceful `[staticrecomp] shutdown:`, no FIFO/GatherPipe panics,
  cpu7 pinned ≈ 4.32 GHz stock, tmax 103.5–104.3 °C.
- LSE arms recorded **zero emulator screenshots** (same dead shot path as the
  post-15:50 tree noted in D1); workload identity across binaries rests on:
  identical movie/template/affinity/clocks, metric-speed parity, matching
  pause-tail (≈ 2.2 in all arms), and the anchored base-arm shots above.

## 4. Control-probe relink (orchestrator add-on)

- Relinked the trial TU from the LSE build tree (`tools/android_trial.py`
  build technique, recipe `android-spike/trial/build.json`), pushed as
  `moderngekko-run-trial-lse`, sha `220488ca10868785` (device-verified).
- One arm at stock with `--probe-quiet --trial-at 45 --trial-secs 20`
  (D1 launch shape): `m4-control-probe-receipts/`, exited=true, 60 metric rows.
- The trial never engaged: probe rows show `android_trial` 0→1 at wall 45.00,
  then **1→4 at wall 45.01** with a `schedule
  invalid_immediate_copy_setup` event at the same instant; the watchdog fired
  at wall 165 (status 4, frames=0). So **no per-callback update/render
  CPU/wall rows exist** — the medians/p95 table cannot be computed from this
  arm (same gap as D1b, different cause: trial skip here vs. mid-race panic
  on binary c59d173e there).
- Positive receipt: the FIFO-fix trial TU ran the full window and exited
  gracefully — `shutdown: native=2702018041 fallback=0 native_exc=425692
  hook_fb=436728 smc_failed=0 verifications=415` — where the pre-fix trial
  binary panicked mid-race.

## Receipts

`android-spike/M4/`: `m4-{base-a,base-b,base-b2,lse-a,lse-b,control-probe}-receipts/`
(run.json, .err/.out, sampler.log, probe.jsonl, GFX/Dolphin post-inis;
`shots/` only in base arms), `analyze.py`, `build-lse.log`, `host-waits.log`,
`thermal-waits.log`, `M4_NOTES.md`. No emulator shots exist for the LSE or
probe arms (dead shot path); no stray files were left in the probe output dir.
Device lease `/data/local/tmp/mg/LEASE` released on completion.
