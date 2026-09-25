# N10 — clean Odin speed baseline on the fork-tip APK

Worker: Muse Code. Brief: `local/muse/prompts/N10.md`. Date: 2026-09-24/25.
Method: N7 clean-speed launcher (`local/research/N7/REPORT.md`) on N9's APK
(`local/research/N9/REPORT.md` §8: `25711bfe…08152`, six diagnostic flags OFF).
Launcher: `local/research/N10/launch.py` (N7 copy; paths/labels → N10, env →
N9-minus-dumps, battery gate → AC + level per standing rule, mc0 precondition,
ps2x.env save/restore, scap ticks 2100/3000/4000, wall 750). No build, no
source edit, no push, no retries, no failed steps.

## Status

**Both runs complete → clean speed.** L1 and L2 each reached guest tick ≥4500
(46.7 s / 46.9 s of racing after the race HUD at ~1714) inside the 750 s wall
cap, with zero FATAL lines. **The rider moves:** both runs read 43–44 MPH and
5% progress at the final capture (tick ~4513–4528), after 0–1 MPH at 1–2%
through tick ~4000.

## Build (reused, no rebuild)

| Item | Result |
| --- | --- |
| APK | `~/dev/ssx3-work/N9/app-release.apk`, `25711bfe1fedec6c4f60cf554b6401df1ca523bc06a82a5c736b2c9cebc08152`, 153,703,964 B |
| Pre-install SHA reads L1 | `25711bfe…08152` ×2 match |
| Pre-install SHA reads L2 | `25711bfe…08152` ×2 match |
| Installed `base.apk` SHAs | L1 `…/com.ps2x.runner-BbgFiMwc83Xm0QoMuiwMnQ==/base.apk` ×2 match; L2 `…/com.ps2x.runner-rGW7dezUa4QBTevGFhbBRA==/base.apk` ×2 match |
| Clean-build basis | N9 §8: sole arm64 cache, 6 diag flags OFF, `SHADOW=ON`; no dump/trace env at runtime (this report) |

## Env (N9 live env minus dumps)

`PS2X_GS_BACKEND=parallel`, `PS2X_GS_TURNIP=1`, `PS2X_SKIP_MOVIE=1`,
`PS2X_CD_IMAGE=…/SSX3.iso`, I26-FAST `PS2X_PAD_SCRIPT`,
`PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_VSYNC_RATE_LOG=1`. No `PS2X_PGS_*`,
no dump/trace key (`grep -c` = 0 in both env files; launcher asserts).

| Item | Result |
| --- | --- |
| L1 env SHA (device = local `logs/L1/ps2x.env`) | `e21bf24518e38af5a6bcd42e1139321b98b57da55df571f4e57cf324516bcdc4` |
| L2 env SHA (device) | `13989f057caaf828ed938003e5ccfee75f4b510b0d552efaeb568ea1ef6d3c70` |
| L1 vs L2 env diff | comment line only (`# N10 L1` vs `# N10 L2`); live keys identical |
| Restored `ps2x.env` SHA (both runs) | `176eff84eaf8e4f55800362f4827744b5f777ca0e3cbd623d271d4cd97cef32d` = N9 orig |
| mc0 | empty both runs (launcher precondition) |

## Launches

`python3 local/research/N10/launch.py --label L{1,2} --wall 750 --stop-tick 4500`.
Each run: lease claimed before install (`N10 … Lx-prep`), `adb install -r`
Success, keyguard `showing=false`, AC `true`, BACK after `am start`,
`am force-stop` after (pid-after=none), env restored, lease
`LEASE_FREE N10 done`. Installed-APK/ISO paths and pins as in §Build; ISO
already on device from N9 (same path, not re-hashed).

| Launch | Race duration | Result | Receipts |
| --- | --- | --- | --- |
| L1 | tick 1714→4513 = 2799 vsyncs = **46.7 s** guest; 477.1 s wall; 95 samples; 0 FATAL | STOP tick ≥4500 at t+476.9 s; battery 88→84% | `logs/L1/{driver.log,logcat.txt,sf-latency.txt,thermal.txt,ps2x.env,ps2x.env.orig,meta.json,scap-sha.txt}` + 4 PNGs |
| L2 | tick 1714→4528 = 2814 vsyncs = **46.9 s** guest; 508.5 s wall; 101 samples; 0 FATAL | STOP tick ≥4500 at t+508.5 s; battery 84→81% | same layout under `logs/L2/` |

PNG SHAs in `logs/Lx/scap-sha.txt` (L1: `10a1465e…`, `6c37c7f6…`, `04614eb1…`,
`c25aa36e…`; L2: `f129d752…`, `8320a453…`, `55da1cf6…`, `a71970ce…`).
Device left clean: lease `LEASE_FREE N10 done`, app not running (`pidof` empty),
`ps2x.env` = N9 orig SHA (re-read after L2).

## Screencap readings (rider moves? YES)

Viewed full-resolution PNGs directly. 2ND/2 in all captures. Fine horizontal
stripes persist (known since N8D2); large black foreground in early race shots
as in N7.

| Capture | Tick~ | Clock | Place | Progress | MPH | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| L1 sc01 | 2111 | 00:00:06 | 2ND/2 | 1% | hidden (EA Radio card) | "3-0" text, RECOVER prompt, rider not visible |
| L1 sc02 | 3028 | 00:00:21 | 2ND/2 | 2% | 1 | small rider center on board |
| L1 sc03 | 4011 | 00:00:38 | 2ND/2 | 2% | 0 | rider center, same slope view |
| L1 sc04 | 4513 | 00:00:46 | 2ND/2 | 5% | **44** | new terrain, snow spray, rider descending |
| L2 sc01 | 2105 | 00:00:06 | 2ND/2 | 1% | hidden (radio card) | "310", same scene as L1 sc01 |
| L2 sc02 | 3028 | 00:00:22 | 2ND/2 | 2% | 1 | same view as L1 sc02 |
| L2 sc03 | 4007 | 00:00:38 | 2ND/2 | 2% | 0 | same view as L1 sc03 |
| L2 sc04 | 4528 | 00:00:47 | 2ND/2 | 5% | **43** | same fast descent as L1 sc04 |

Movement onset is between tick ~4000 and ~4513 in both runs (guest clock
00:00:38 → 00:00:46). N7's window ended at tick 4042 (00:00:38, 0 MPH), just
before the onset — consistent, not contradictory.

## Ledger-ready rates

Guest vsyncs per wall second; ratio ÷ 59.94. Interpolated from epoch-stamped
`[vsync-rate]` ticks at I26-FAST boundaries by `phases.py`.

| Phase | L1 vsyncs/s | L2 vsyncs/s | L1 ratio | L2 ratio | L1 SF presents/s | L2 SF presents/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Title/startup (0→636) | 32.98 | 31.53 | 0.550× | 0.526× | 52.1 (n=1) | 56.0 (n=1) |
| Main menu (636→766) | 29.85 | 29.49 | 0.498× | 0.492× | 50.4 (n=1) | 53.2 (n=1) |
| Select Character (766→884) | 18.75 | 15.15 | 0.313× | 0.253× | — | 57.3 (n=1) |
| Setup Character / Peak (884→1099) | 22.44 | 20.63 | 0.374× | 0.344× | 53.4 (n=1) | 49.4 (n=1) |
| Select Mode / Event / My Rules (1099→1440) | 36.51 | 38.91 | 0.609× | 0.649× | 48.7 (n=1) | 50.7 (n=1) |
| Loading / Rival card (1440→1714) | 11.18 | 9.61 | 0.187× | 0.160× | 56.8–59.0 (n=3) | 57.7–59.5 (n=2) |
| **Race (1714→4513/4528)** | **6.93** | **6.59** | **0.116×** | **0.110×** | **54.7–59.0 (n=37)** | **55.6–58.6 (n=39)** |

Run-to-run spread (race): mean 6.76/s = **0.113×**; L2 4.9% slower than L1
(heat soak — see Thermal). Race per-5s bins: L1 ~6.6–7.8 (one dip to 4.6–5.0
near t+172 s, recovered); L2 ~6.2–7.0 with a dip to 4.4–5.0 near t+183–194 s,
then 7.4–8.0 in the final bins as the rider descends. Presents are not guest
frames (SF holds ~55–59/s throughout). APK SHA `25711bfe…08152` for all rows.
Context (not a controlled A/B — GS path and sound changed): N7 race 0.076×
(CPU GS, 1 run, 38.8 s); E58 Mac mini race 0.13×.

## Thermal / clocks

`thermal.txt` columns: wall s, tick, cpu5 Hz, cpu7 Hz, cpu-1-1-1 temp (raw),
thermal-service status. Final `top -H`: GameThread ~85% of one CPU, GsWorker
23–27%, app main 4–8% both runs.

- L1: status 0 → 2 → 3 (t+32 s) → 4 (t+442 s); cpu5 3.53 GHz early, 1.79 GHz
  most of the race; cpu7 4.32 GHz (last poll 2.25 GHz); temp raw 84,900–105,500.
- L2 (back-to-back, heat-soaked): status 3 at first poll, **5 from t+21 s to
  end**; cpu5 3.53 GHz early, 1.79 GHz most of the race; cpu7 mostly
  4.32 GHz with dips (2.85/3.28/2.25 GHz); temp raw 83,700–105,800.
- L2's 4.9% lower race rate is consistent with sustained status-5 throttling;
  a spaced repeat would test this (not run — brief allows 2 launches).

## Exact commands

```sh
mkdir -p local/research/N10/logs ~/dev/ssx3-work/N10
cp local/research/N7/phases.py local/research/N10/phases.py
cp local/research/N7/launch.py local/research/N10/launch.py  # then N10 edits
sha256sum ~/dev/ssx3-work/N9/app-release.apk  # ×2 before each install
adb -s 622c49b1 shell "echo 'N10 <utc> Lx-prep' > /data/local/tmp/mg/LEASE"
adb -s 622c49b1 install -r ~/dev/ssx3-work/N9/app-release.apk
adb -s 622c49b1 shell 'sha256sum <pm-path>/base.apk'  # ×2 each run
python3 local/research/N10/launch.py --label L1 --wall 750 --stop-tick 4500
python3 local/research/N10/launch.py --label L2 --wall 750 --stop-tick 4500
python3 local/research/N10/phases.py local/research/N10/logs/L1
python3 local/research/N10/phases.py local/research/N10/logs/L2
```

## Gaps and recommended next action

| Gap | Reason |
| --- | --- |
| Spaced (non-heat-soaked) repeat | L2 ran back-to-back at thermal status 5; brief allows 2 launches |
| Movement-onset tick (4000–4513 window) | no capture between sc03 and final; a ~4250-tick capture would narrow it |
| Select Character rider shot | N7 gap carried over; race-tick captures per brief only |

**Recommended next action for the orchestrator:** record 0.113× (6.76 guest
vsyncs/s, mean of 2 clean runs, APK `25711bfe…`) as the first clean Odin speed
baseline on the GPU-GS product path, and rider motion confirmed (43–44 MPH at
tick ~4520). No code change proposed — this brief was measurement only.
Budgets used: 0 builds, 2/2 launches, ~30 min wall, N10 git dir 4.8 MB,
scratch `~/dev/ssx3-work/N10/` empty.
