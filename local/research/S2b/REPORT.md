# S2b — host replay capacity: third EGL arm + Vulkan arms (REPORT)

Brief: `local/muse/prompts/S2b.md`. Continuation of S2
(`local/research/S2/REPORT.md`). No verdicts; tables only.

## 0. Gates, rules, compliance log

- Start (UTC): 2026-09-18T16:26:28Z. Time box 5 h wall incl. waits
  (ends ~21:26Z). D8 fallback (start + 3 h) would have been ~19:26:28Z but
  was not needed: D8's REPORT.md appeared 17:10Z.
- Serial: `local/odin-serial` read before every adb call. Was
  `192.168.1.53:5555` (Wi-Fi); per operator note the Odin moved to USB and
  the file now reads `622c49b1`. One `adb connect` was run at 16:35Z while
  Wi-Fi flapped, before the note (timed out); none after, no `adb tcpip`.
- Device lease: 16:26Z `USER-nethersx2` (USER-* = user has device: waited,
  never removed). 16:29:05Z absent. 16:29:18Z `D8` (D8's
  `d8-base-cap-prelaunch.json`, gate log t=12:29:18 EDT) — foreign lease,
  waited. Absent again after D8 finished; absent after every S2b arm
  (`arm.py` `finally` verified each time). Never written except by
  `arm.py` itself (`S2`); never removed a foreign lease.
- `moderngekko` process: none on any poll; none remains after the last arm.
- Battery: 83–86% status 2 while on Wi-Fi; 97→92 status 3 (discharging, AC
  powered true) on the Mac USB port, static across polls. `arm.py`'s gate
  (level >= 20 AND status 2/5) refused this state.
- Orchestrator gate update (17:25Z): D8 complete (REPORT.md exists), lease
  absent, 97% cabled device cannot drain to zero — instruction: copy
  `local/research/S2/arm.py` to `local/research/S2b/arm.py`, change only
  the battery check to accept status 3 when level >= 80, record the diff,
  use `local/research/S2b/arm.py` for every arm. Done: every arm
  (s2-egl-c, s2-vk-a, s2-vk-b) ran under `S2b/arm.py`. Diff:
  `local/research/S2b/arm-battery-diff.txt` (accept `status in (2, 5)` OR
  `(status == 3 AND level >= 80)`; level >= 20 floor unchanged; refusal
  message updated to match). Verified live (97/3 → ok_to_launch True)
  before the first arm.
- Thermals (read-only): hottest `cpu-*` 61.9 C at 16:26Z idle; per-arm
  launch values in §5 (`arm.py` thermal wait applied; hottest was already
  below 60 C at each launch, 0.5 s waits).
- D8 ordering: REPORT.md absent on all polls 16:26Z–17:06Z while D8 ran
  (lease D8); present 17:10Z with `d8-base-cap/spin/adpf` receipts. First
  S2b arm launched 17:36Z, after the gate cleared and the battery
  exception arrived.
- Host lease `/tmp/ssx3-host-lease`: claimed `printf 'S2b-build'` for the
  relink only, released 16:29:05Z after copy+verify. Later held by foreign
  `P1`, then absent at 17:5xZ through the end. Never removed a foreign
  lease. Device arms do not use the host lease.
- Receipts dir pre-exist rule: `s2-egl-c/vk-a/vk-b-receipts` each verified
  absent before its arm. `arm.py` fix verified by code read (refuse
  existing dir; stage `<tag>-pre.json` beside the dir, move in after; pull
  probe/sampler/err/out + post inis when the harness dies early) and then
  exercised end-to-end on three arms: full harness success (egl-c) and two
  early-harness-death recoveries (vk-a/b, where the re-pull found no
  probe/sampler because the trial died at boot).
- Binary sha rule: verified `shasum -a 256` == `build.json`
  `trial_binary_sha256` before every arm (egl15 `b25f61b0…22bcb` twice;
  vk1 `dd5fb34b…7e14` twice).
- Header sha note: the brief quotes header `31ffc39d…`; the file on disk
  (and at HEAD, and in `trial-egl15/build.json` and `trial-vk1/build.json`
  as `s2_header_sha256`) is
  `ffbb81b2516f3e47fbb9cb4af94e85fb560f72b473533cae97b3804904a82396`.
  `trial-egl14/build.json` records `31ffc39d…`. Both S2b-used builds carry
  the current header. Recorded, not resolved.
- Disk incident: at ~17:38Z the host Data volume hit 100% (shared
  `/private/tmp`, ~12 GB across agents; `ENOSPC` on receipt writes).
  Removed only my own redundant `/tmp/s2b-link/` (228 MB; SSD copy of the
  vk1 build already verified identical) and re-saved the three receipts
  that failed. No other files touched.
- Backgrounding deviation: the session tool rejects shell `&`; arms ran in
  the foreground with the maximum wait and, when they exceeded it, under
  runtime-managed backgrounding (process not killed; `finally` lease
  release verified after every arm). `nohup` was not used.
- Untouched: `tools/android_trial.py`, `native/`, vendor tree, S2's files.
  Own files under `local/research/S2b/` and
  `/Volumes/Extreme SSD/android-spike/S2b/`. Exception: the three device
  arms' receipts land in `/Volumes/Extreme SSD/android-spike/S2/` because
  `arm.py`'s SSD path is fixed there (commands are S2's exact form, run
  via the S2b script).

## 1. Capacity table

S2's rows copied from `local/research/S2/REPORT.md` Part 3c for
side-by-side; S2b rows measured this run.

| Arm | Build / header | Replays | `done` | Wall per replay med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | 200-seq wall | Frame B / updates | Tombstone |
| --- | --- | ---: | :-: | --- | --- | ---: | --- | --- |
| **s2-egl-a** (S2) | `trial-egl14` `4e15d56e…`, header `31ffc39d…` | **200 / 200** | **YES** | **0.665** / 0.729 / 0.638 / 0.874 | 0.660 / 0.723 | 135.095 ms | 343,226 / 2,433 | none |
| **s2-egl-b** (S2) | `trial-egl15` `b25f61b0…`, header `31ffc39d…` (+ `xform` probe) | **200 / 200** | **YES** | **0.866** / 0.963 / 0.826 / 1.077 | 0.860 / 0.955 | 175.174 ms | 441,988 / 3,561 | none |
| **s2-egl-c** (S2b) | `trial-egl15` `b25f61b0…`, header `ffbb81b2…` (no rebuild) | **200 / 200** | **YES** | **0.806** / 0.874 / 0.781 / 1.013 | 0.802 / 0.872 | 163.934 ms | 422,600 / 3,389 | none |
| s2-vk-a (S2b) | `S2b/trial-vk1` `dd5fb34b…` | 0 / 200 | no | — (no rows) | — | — | — | SIGSEGV `StaticRecompCore::Run()+1032` at boot (uptime 20 s) |
| s2-vk-b (S2b) | same | 0 / 200 | no | — (no rows) | — | — | — | same, uptime 19 s (repeat) |
| *(prior)* D2b egl-a | `trial-egl12`, D2 header | 27 / 200 | no | 2.036 / 2.254 / 1.998 / 2.368 | 2.032 / 2.232 | died | 479,342 / 3,871 | SIGSEGV `LoadIndexedXF` |
| *(prior)* D2b egl-b | same | 27 / 200 | no | 2.027 / 2.304 / 1.961 / 2.304 | 1.999 / 2.301 | died | 466,658 / 3,748 | SIGSEGV `LoadIndexedXF` |

Phase medians, s2-egl-c: mem 0.206 / cp 0.001 / pre 0.046 / run 0.553 /
sync 0.000 (run p95 0.570). `restored`: `det=1 dual=1 mask_bp=2 dls=0
dl_bytes=0 indexed=2075 aux_bytes=99600 walk=422600/422600 unknown=0
benign=1`. 2 MiB / 99,600 B = 21.0 replays of aux budget. Receipt:
`local/research/S2b/analyze-egl-c.txt`.

Recomputed receipts for S2's arms (same script, same probe files, this
run) in `local/research/S2b/analyze-egl-ab.txt`: s2-egl-a identical to
S2's row; s2-egl-b recomputes as 0.861 / 0.940 / 0.826 / 1.077 wall and
0.856 / 0.929 CPU (S2's table: 0.866 / 0.963 and 0.860 / 0.955). Same 200
rows, `done`, frame bytes/updates, `restored` detail. Difference noted,
not explained.

## 2. Race proof

Method: probe `record_start` wall = capture seconds after launch (guest);
emu thread = `GC_Adapter_Scan` per `tools/android_trial.py`
`AFFINITY_ROLES` (pinned cpu7, mask 80); busy fraction = delta(utime+stime)
/ 100 / delta wall over sampler ticks in [capture − 10 s, capture].
Script: `/tmp/s2b-raceproof.py` (throwaway, not committed). The trial
records no screenshots, so there is no HUD proof; stated per arm.

| Arm | Capture wall rel launch (s) | Emu busy 10 s before | Ticks in win | Frame B / updates | Screenshots |
| --- | ---: | --- | ---: | --- | --- |
| s2-egl-a | 100.02 | 0.943 (8.3 s / 8.8 s) | 6 | 343226 / 2433 | none (no HUD proof) |
| s2-egl-b | 100.02 | 0.941 (8.2 s / 8.8 s) | 6 | 441988 / 3561 | none (no HUD proof) |
| s2-egl-c | 100.02 | 0.934 (8.2 s / 8.8 s) | 6 | 422600 / 3389 | none (no HUD proof) |
| s2-vk-a / s2-vk-b | — (died at boot) | — | 0 (no sampler) | — | none |

Receipt: `local/research/S2b/raceproof-abc.txt` (a/b rows identical to the
earlier `raceproof-ab.txt`). Reference: D2b's race frames were 479,342 B /
3,871 and 466,658 B / 3,748 updates. The movie is `m3-snow-jam-3min.dtm`
and each sequence fires at guest t = 100 s (inside the race by movie
timing — inference, not a screenshot).

## 3. Vulkan relink recipe (verified)

- `core-vk-build` has `VideoBackends/Vulkan/libvideovulkan.a`, compiles
  with `-DHAS_VULKAN`; its `compile_commands.json` points at the repo
  vendor tree, not `m4-src`.
- Attempt 1 (no `--reference-tu`, i.e. `reconstruct_tu()` from the current
  repo): compile OK, link FAILED:
  `ld.lld: error: undefined symbol: StaticRecompCore::TryHleFpUnavailable()`
  referenced by `Core_Run.cpp:180` (`trial.o: StaticRecompCore::Run()`).
  Cause: the current repo TU references `TryHleFpUnavailable` (repo
  `StaticRecompCore_Run.cpp:172`, defined in repo
  `StaticRecompCore_SMC.cpp:424`) but `core-vk-build`'s `libcore.a`
  (built 2026-09-17 08:51) predates the symbol — NDK `llvm-nm` shows no
  `HleFpUnavailable` in the vk `SMC.cpp.o` or `libcore.a`. First error
  lines: `local/research/S2b/vk-relink-attempt1-error40.txt`.
- Attempt 2: `--reference-tu
  /Volumes/Extreme SSD/android-spike/m4-src/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp`
  (m4-src lacks the symbol, matching the stale vk libs), no `--with-d5exc`:
  LINKED.
- Commands (also in `local/research/S2b/vk-relink-commands.log`):
  ```
  printf 'S2b-build' > /tmp/ssx3-host-lease
  mkdir -p /tmp/s2b-link
  python3 local/research/S2/build_android_trial.py --game local/game/gxbe69-stock --build-dir "/Volumes/Extreme SSD/android-spike/core-vk-build" --output /tmp/s2b-link/trial-vk1
  python3 local/research/S2/build_android_trial.py --game local/game/gxbe69-stock --build-dir "/Volumes/Extreme SSD/android-spike/core-vk-build" --reference-tu "/Volumes/Extreme SSD/android-spike/m4-src/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp" --output /tmp/s2b-link/trial-vk2
  mkdir -p "/Volumes/Extreme SSD/android-spike/S2b/trial-vk1" && cp -R /tmp/s2b-link/trial-vk2/. "/Volumes/Extreme SSD/android-spike/S2b/trial-vk1/"
  shasum -a 256 <binary>; python3 -c receipt sha check (link + SSD)
  rm -f /tmp/ssx3-host-lease
  ```
- Output dir `/tmp/s2b-link/` (APFS) used for the link, copied to
  `/Volumes/Extreme SSD/android-spike/S2b/trial-vk1/` (link dir was
  `trial-vk2`; SSD name `trial-vk1` per the brief; contents identical, sha
  re-verified after copy). `/tmp/s2b-link/` removed afterwards (disk
  incident, §0).
- Receipt: binary `dd5fb34b433afc39ce774b2307bbec286f049ce558d81d62dda24f16048d7e14`
  on disk at link AND on SSD, equals `build.json` `trial_binary_sha256`
  (receipt == disk, both). `file`: ELF 64-bit LSB pie executable, ARM
  aarch64, BuildID `550ea64a…`, 234,470,696 bytes. `build.json`:
  `tu_origin` reference-tree m4-src `StaticRecompCore_Run.cpp`, no `d5exc`,
  `s2_header_sha256 ffbb81b2…`.

## 4. Vulkan arms

Exact commands (via `local/research/S2b/arm.py`, brief §4 form):
```
python3 local/research/S2b/arm.py s2-vk-a --graphics Vulkan \
  --binary "/Volumes/Extreme SSD/android-spike/S2b/trial-vk1/moderngekko-run-trial" \
  --build-json "/Volumes/Extreme SSD/android-spike/S2b/trial-vk1/build.json"
```
then `s2-vk-b` the same way. Receipts in
`/Volumes/Extreme SSD/android-spike/S2/s2-vk-{a,b}-receipts/`.

Both arms: harness returncode 1 at the affinity step
(`grep /proc/<pid>/task/*/comm` → exit 2: the trial child was already
dead). 0 capacity rows, no probe JSONL, no sampler log, `.out` 0 bytes,
`.err` boot lines only (through `sample=10`). Device lease released by
`finally`; no `moderngekko` process remains. Tombstone (fresh entries,
same binary BuildId `550ea64a…`):

| Arm | Time (EDT) | pid/tid | Signal | Uptime | Cmdline graphics | #00 frame |
| --- | --- | --- | --- | ---: | --- | --- |
| s2-vk-a | 13:40:08 | 25280 / 25327 (`GC Adapter Scan`) | SIGSEGV SI_TKILL | 20 s | `--graphics Vulkan`, `user-s2-vk-a` | `StaticRecompCore::Run()+1032` (pc …36536c) |
| s2-vk-b | 13:40:49 | 25844 / 25880 (`GC Adapter Scan`) | SIGSEGV SI_TKILL | 19 s | `--graphics Vulkan`, `user-s2-vk-b` | identical (`Run()+1032`, same BuildId) |

Full frames #01–#05 identical on both: `PowerPCManager::RunLoop()+20`,
`CPUManager::Run()+488`, `Core::CpuThread(...)+620`,
`Core::EmuThread(...)+2064`, `__thread_proxy+92`, then libc
`__pthread_start` / `__start_thread`. Registers differ only in ASLR
addresses (x4 `4245363900000000`, x5/x6 `39364542` constant on both).
Same-crash repeat across two launches, 41 s apart. Older buffer entries
(D2b `LoadIndexedXF+464` 09:17/09:19, `org.ssx3.onscreen` SIGTRAP 10:47)
are not from these arms.

## 5. Device conditions per arm

| Arm | Battery at launch (before → after) | Launch hottest `cpu-*` | Sampler max `cpu-*` / `gpuss` | cpu7 min / median | Ticks below 2.0 GHz | Kill rule |
| --- | --- | ---: | --- | ---: | ---: | --- |
| s2-egl-a | 55% s2 → 55%+ (S2) | 50 C (0.5 s wait) | 104 C / 70 C | 3,283,200 / 4,320,000 kHz | 0 (337 ticks) | never tripped |
| s2-egl-b | 64% s2 (S2) | 51 C per pre.json, S2 table 47 C (0.5 s wait) | 104 C / 70 C | 3,283,200 / 4,320,000 kHz | 0 (336 ticks) | never tripped |
| s2-egl-c | 97% s3 → 93% s3 | 39 C (0.5 s wait) | 104 C / 66 C | 3,283,200 / 4,320,000 kHz | 0 (335 ticks) | never tripped |
| s2-vk-a | 93% s3 → 93% s3 | 42 C | — (no sampler; died at boot) | — | — | n/a |
| s2-vk-b | 93% s3 → 92% s3 | 43 C | — (same) | — | — | n/a |

Per-arm state (all five, from pre.json): `performance_mode` (system) 1,
`fan_mode` (system) 4, `scaling_max_freq` cpu0 3,532,800 / cpu7 4,320,000
kHz, GPU governor `msm-adreno-tz`, low_power 0. Receipts:
`local/research/S2b/sampler-conditions-ab.txt`,
`local/research/S2b/sampler-conditions-c.txt`.

## 6. Exact commands (this run)

- EGL-c (brief §1 form, via the S2b script):
  `python3 local/research/S2b/arm.py s2-egl-c --binary
  "/Volumes/Extreme SSD/android-spike/S2/trial-egl15/moderngekko-run-trial"
  --build-json "/Volumes/Extreme SSD/android-spike/S2/trial-egl15/build.json"`,
  then `python3 local/research/S2/analyze.py
  "s2-egl-c=/Volumes/Extreme SSD/android-spike/S2/s2-egl-c-receipts/s2-egl-c-probe.jsonl"`
  → `local/research/S2b/analyze-egl-c.txt`.
- Analyze a/b → `local/research/S2b/analyze-egl-ab.txt` (same form, two args).
- Race proof: `python3 /tmp/s2b-raceproof.py "s2-egl-a=…" "s2-egl-b=…"` →
  `raceproof-ab.txt`; `… "s2-egl-c=…"` row merged →
  `local/research/S2b/raceproof-abc.txt`.
- Conditions: python via `arm.py::kill_rule_check` + pre.json →
  `sampler-conditions-{ab,c}.txt`.
- Vulkan recipe: §3 and `vk-relink-commands.log`; vk arms §4.

## 7. Receipt paths and shas

- `/Volumes/Extreme SSD/android-spike/S2/trial-egl15/moderngekko-run-trial`:
  `b25f61b0…22bcb` (== build.json, == brief; verified before arm c).
- `/Volumes/Extreme SSD/android-spike/S2b/trial-vk1/moderngekko-run-trial`:
  `dd5fb34b…7e14` (== build.json at link and on SSD; verified before both
  vk arms).
- `local/research/S2/s2_replay_capacity.h`: `ffbb81b2…` (disk + HEAD +
  both used build.json files; brief quotes `31ffc39d…`, see §0).
- S2 receipts (pre-existing): `…/S2/s2-egl-{a,b}-receipts/`.
- S2b arms' receipts: `…/S2/s2-egl-c-receipts/` (probe, sampler, err/out,
  post inis, pre.json, arm.json, trial stdout/stderr, logcat-crash),
  `…/S2/s2-vk-a-receipts/` and `…/S2/s2-vk-b-receipts/` (arm.json, pre.json,
  trial stdout/stderr, err, empty out, post inis, logcat-crash; no probe,
  no sampler).
- Crash buffers also contain stale entries (D2b 09:17/09:19
  `user-d2b-egl-{a,b}` SIGSEGV `LoadIndexedXF+464`, `org.ssx3.onscreen`
  SIGTRAP 10:47); s2 entries identified by pid/cmdline/BuildId in §4.

## 8. Waits log

`local/research/S2b/waits.log`: start, USER-* lease, clear, D8 claim (with
D8-active evidence), Wi-Fi flap + reconnect attempts, USB switch, D8
REPORT appearance, battery-status-3 block, orchestrator battery exception,
three launches, disk incident.

## 9. What I could not do

- Vulkan capacity: unmeasurable with this build — `trial-vk1` SIGSEGVs in
  `StaticRecompCore::Run()+1032` ~20 s into boot on both arms, before any
  replay or probe row. Two documented relink attempts were spent (one
  failed at link, one produced this binary); no further relink was
  attempted. The m4-src TU that links is older than the repo TU the EGL
  builds used, so even a working boot would pair the current S2 header
  with a stale core.
- No screenshots exist for any arm (receipt dirs contain none), so no HUD
  verification is possible from these receipts; the race proof is
  sampler + probe only.
- `s2-egl-b` recomputed medians differ slightly from S2's table (§1);
  `s2-egl-b` launch temp in pre.json (51 C) differs from S2's table
  (47 C). Both noted, neither explained.
- Milestone 2: not started (unchanged from S2).
