# NP1 Part 1 — Odin race call-graph profile on the F1 APK (BLOCKED before launch)

Worker: Muse Code, brief `local/muse/prompts/NP1.md` Part 1 only.
Status: **blocked, no launch.** The Odin sits at 15% and net-discharges on the
mini's USB even with the screen off (-81 mA; -237 mA screen-on), so the
≥20% launch gate is unreachable by waiting; my screen-off charge test also
left the keyguard `showing=true` (PIN lock, adb dismiss fails). Needs
Brad hands-on: unlock + wall-charge to ≥20%. First failure → stop, hand back.

## Blocker (for the orchestrator)

1. **Power:** `current_now` -237 mA screen-on idle, -81 mA screen-off
   (`usb online=1`, `AC powered: true`, status Discharging — status ignored
   per AGENTS.md, but the level fell 16% → 15% over ~10 min idle). The mini's
   USB port cannot charge the Odin; waiting cannot reach the 20% gate.
   Fix: wall charger (hands-on).
2. **Lock:** keyguard `showing=true` after my wake test. `input keyevent 82`
   + swipe-up dismiss both fail → secure lock. Fix: Brad unlocks.
   (Before my test it was `showing=false`; the lock is my doing.)

Device left-state (verified): lease `LEASE_FREE F1 done` (never claimed),
app not running (`pid-none`), Brad env `9fb46f85…d13` intact, mc0 6/6 pins
match (preflight), screen OFF (slow drain), level 15%, thermal status 0.

## Preflight receipts (all pass except battery)

| Check | Result |
| --- | --- |
| Disk `disk_budget.sh` | 117.7 GB of 200 GB; free 137 Gi |
| F1 APK local SHA ×2 | `c822a2b3787b6caa7bfabebbdad0cea95c398bbc5b186e889eac824c829dbeb9` match |
| Installed `base.apk` SHA | `c822a2b3…` match (F1 play build already installed) |
| Device env SHA | `9fb46f85…d13` = Brad's |
| Brad mc0 | 6/6 SHAs match I31 pins |
| mc0-test | absent (F1 cleaned it); driver `mkdir -p`s it, then empty-checks |
| Keyguard (then) | `showing=false` |
| Thermal | status 0 |
| Battery | 16% → 15%, AC true — **gate (≥20%) fails** |
| Lease / app | free / not running |
| bytesize WSL | idle (load 0.00; just booted, `up 0 min`) |

## Ready for resume (no rework needed)

- Driver `local/research/NP1/launch.py` = F1 launcher with NP1 paths/lease
  (`/data/local/tmp/np1`, `NP1 …` / `LEASE_FREE NP1 done`) and the profile
  step switched to `simpleperf record --call-graph fp` (brief: fp first,
  dwarf if fp unwinds are shallow). Compiles (`py_compile` OK).
  `buckets.py`, `phases.py` copied from N11/F1.
- Bytesize symdir `/home/brad/np1/symdir/`: unstripped `libps2EntryRunner.so`
  (997 MB, SHA `255f1846…`, BuildID `22bd531b…` = the APK's merged `.so`
  BuildID → symbolization will match), `libc.so` (`dd242326…`, N11's pull,
  same ROM), `libhardware.so` (`1b49d27c…`, = TL1/F1 manifest pin).
- `.eh_frame` present in the unstripped `.so` (dwarf fallback viable); no
  `-fno-omit-frame-pointer` flag found (ninja path differs; fp depth judged
  empirically from the first `perf-*.data` children view).
- N11 S2 baseline on file (`local/research/N11/reports/`): fp-vs-dwarf
  comparison target is the children depth there (EeScheduler→…→VU1 run).
- F1 race wall/frame anchor for the stage table: 8.42/8.38 vsyncs/s →
  **119.0 ms** (brief value confirmed).

Resume command (after unlock + ≥20% + thermal ≤2 re-check):

```sh
adb -s 622c49b1 install -r ~/dev/ssx3-work/F1/app-release.apk
python3 local/research/NP1/launch.py --label P1 --wall 600 --profile-after-tick 2400 --profile-secs 30
```

## Budgets and gaps

Builds 0, launches 0 (+0 spare used), ~40 min wall (mostly charge waits).
Scratch `~/dev/ssx3-work/NP1/` empty; NP1 git dir text-only. Bytesize
`/home/brad/np1/` holds `symdir/` (~1 GB, the only heavy bytes; light
`simpleperf report` work pending). Gap: everything after the launch
(profile, symbolization, stage/callers tables, N11 row-by-row compare).

## Exact commands

```sh
mkdir -p local/research/NP1/logs ~/dev/ssx3-work/NP1
cp local/research/F1/launch.py local/research/NP1/launch.py  # + NP1/fp edits
cp local/research/N11/buckets.py local/research/NP1/buckets.py
cp local/research/F1/phases.py local/research/NP1/phases.py
sha256sum ~/dev/ssx3-work/F1/app-release.apk  # x2: c822a2b3...
bash local/tooling/disk_budget.sh
adb -s 622c49b1 shell 'cat /data/local/tmp/mg/LEASE; dumpsys window policy | grep -m1 showing; dumpsys battery | grep -E "level|AC powered"; dumpsys thermalservice | grep -m1 "Thermal Status"; pidof com.ps2x.runner || echo pid-none'
adb -s 622c49b1 shell 'sha256sum .../files/ps2x.env; for f in $(pm path com.ps2x.runner | cut -d: -f2); do sha256sum $f; done'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "... cp unstripped .so + N11 libc/libhardware to /home/brad/np1/symdir/; sha256sum; readelf -n BuildID obj vs merged (match 22bd531b...)"'
adb -s 622c49b1 shell 'cat /sys/class/power_supply/battery/current_now'  # -237mA on, -81mA off
adb -s 622c49b1 shell 'input keyevent 26'  # screen-off charge test -> locked on wake
adb -s 622c49b1 shell 'input keyevent 82' ; 'input swipe 540 1400 540 400 300'  # dismiss fails
adb -s 622c49b1 shell 'input keyevent 26'  # screen back off; left-state verified
```
