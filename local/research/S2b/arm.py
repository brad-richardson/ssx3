#!/usr/bin/env python3
"""S2 device arm: lease + thermal gate + run + tombstone pull, one command.

Brief rules encoded here so no step is forgotten:
  * device lease `/data/local/tmp/mg/LEASE` must be absent (or already S2);
    claimed with printf, removed at the end even on failure;
  * `ps -A | grep moderngekko` must be empty before launch;
  * battery gate (orchestrator addition, 2026-09-18): read `dumpsys battery`
    first; refuse to launch unless level >= 20 AND status is 2 (charging) or
    5 (full); also record `settings get global low_power` (1 = battery saver,
    which throttles the CPU and makes an arm suspect). Level/status are logged
    per arm in the receipts;
  * thermal gate: wait until the hottest `cpu-*` zone is below 60 C or five
    minutes have passed, record the max at launch;
  * record performance_mode, fan_mode and scaling_max_freq cpu0/cpu7 per arm;
    never change a device setting, never reboot;
  * kill only on any zone >= 110 C or cpu7 < 2.0 GHz for more than five
    consecutive sampler ticks -- evaluated from the sampler log after the run
    (the harness timeout bounds the run anyway);
  * `logcat -d -b crash` pulled immediately after the run, before it rotates.

Writes only into the arm's receipts directory on the SSD.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _serial():
    """The Odin moved to adb over Wi-Fi so it can charge on a wall charger;
    local/odin-serial carries the current serial (USB 622c49b1 may vanish)."""
    for candidate in (ROOT / "local/odin-serial",
                      Path("/Volumes/Extreme SSD/android-spike/ODIN_SERIAL")):
        try:
            value = candidate.read_text().strip()
        except OSError:
            continue
        if value:
            return value
    return "622c49b1"


SERIAL = _serial()
LEASE = "/data/local/tmp/mg/LEASE"
BRIEF = "S2"
SSD = Path("/Volumes/Extreme SSD/android-spike/S2")


def adb(*args, check=False):
    out = subprocess.run(["adb", "-s", SERIAL, *args], capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(f"adb {args}: {out.stderr.strip()}")
    return out.stdout.replace("\r", "")


def shell(cmd, check=False):
    return adb("shell", cmd, check=check).strip()


def cpu_zones():
    """{type: milli-or-deci-C as reported} for thermal zones whose type starts cpu-."""
    raw = shell(
        "for z in /sys/class/thermal/thermal_zone*; do "
        "t=$(cat $z/type 2>/dev/null); case \"$t\" in cpu-*) "
        "echo \"$t $(cat $z/temp 2>/dev/null)\";; esac; done")
    zones = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("-").isdigit():
            value = int(parts[1])
            zones[parts[0]] = value // 1000 if abs(value) > 1000 else value
    return zones


def battery():
    """dumpsys battery, as a dict, plus the battery-saver flag."""
    raw = shell("dumpsys battery")
    info = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.strip().partition(":")
        info[key.strip()] = value.strip()
    out = {"level": None, "status": None, "ac_powered": info.get("AC powered"),
           "usb_powered": info.get("USB powered"), "temperature": info.get("temperature"),
           "low_power": shell("settings get global low_power")}
    for key in ("level", "status"):
        try:
            out[key] = int(info.get(key, ""))
        except ValueError:
            pass
    # status: 1 unknown, 2 charging, 3 discharging, 4 not charging, 5 full
    # Orchestrator exception 2026-09-18: status 3 (discharging) is accepted
    # when level >= 80 (cabled device on a port that always reports 3; the
    # rule exists to prevent drain to zero). Level >= 20 floor unchanged.
    out["ok_to_launch"] = bool(out["level"] is not None and out["level"] >= 20 and
                               (out["status"] in (2, 5) or
                                (out["status"] == 3 and out["level"] >= 80)))
    out["suspect_battery_saver"] = out["low_power"] == "1"
    return out


def device_settings():
    return {
        "performance_mode_system": shell("settings get system performance_mode"),
        "performance_mode_global": shell("settings get global performance_mode"),
        "fan_mode_system": shell("settings get system fan_mode"),
        "fan_mode_global": shell("settings get global fan_mode"),
        "scaling_max_freq_cpu0":
            shell("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2>/dev/null"),
        "scaling_max_freq_cpu7":
            shell("cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_max_freq 2>/dev/null"),
        "gpu_governor":
            shell("cat /sys/class/kgsl/kgsl-3d0/devfreq/governor 2>/dev/null"),
        "max_gpuclk": shell("cat /sys/class/kgsl/kgsl-3d0/max_gpuclk 2>/dev/null"),
    }


def thermal_gate(limit_c=60, max_wait_s=300):
    """Wait for the hottest cpu-* zone to fall below limit, or five minutes."""
    start = time.time()
    hottest_seen = 0
    while True:
        zones = cpu_zones()
        hottest = max(zones.values()) if zones else -1
        hottest_seen = max(hottest_seen, hottest)
        waited = time.time() - start
        if hottest < limit_c or waited >= max_wait_s:
            return {
                "max_cpu_zone_temp_at_launch": hottest,
                "zones": zones,
                "max_during_wait": hottest_seen,
                "waited_s": round(waited, 1),
                "rule": f"hottest-cpu-below-{limit_c}C-or-{max_wait_s // 60}min",
            }
        time.sleep(10)


def kill_rule_check(sampler_log):
    """Post-hoc kill-rule read from the sampler log.

    Format is `key value` per line (`cpu7 4320000`, `cpu-0-1-0 71100`), with
    thermal-zone temperatures in milli-C.
    """
    empty = {"max_zone_c": None, "cpu7_min_khz": None, "ticks": 0,
             "cpu7_below_2ghz_max_run_ticks": 0, "any_zone_ge_110": False}
    if not sampler_log or not Path(sampler_log).exists():
        return empty
    max_zone, cpu7_min, run, worst, ticks = None, None, 0, 0, 0
    by_prefix = {}
    for line in Path(sampler_log).read_text(errors="replace").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        key, value = parts
        if not value.lstrip("-").isdigit():
            continue
        number = int(value)
        if key.startswith("cpu-") or key.startswith("gpuss") or key.startswith("skin"):
            celsius = number // 1000 if abs(number) > 1000 else number
            max_zone = celsius if max_zone is None else max(max_zone, celsius)
            group = "cpu" if key.startswith("cpu-") else key.split("-")[0]
            by_prefix[group] = max(by_prefix.get(group, -999), celsius)
        elif key == "cpu7":
            ticks += 1
            cpu7_min = number if cpu7_min is None else min(cpu7_min, number)
            run = run + 1 if number < 2_000_000 else 0
            worst = max(worst, run)
    return {"max_zone_c": max_zone, "max_by_group_c": by_prefix,
            "cpu7_min_khz": cpu7_min, "ticks": ticks,
            "cpu7_below_2ghz_max_run_ticks": worst,
            "any_zone_ge_110": bool(max_zone is not None and max_zone >= 110)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tag")
    ap.add_argument("--graphics", default="OGL", choices=["OGL", "Vulkan", "Null"])
    ap.add_argument("--binary", default=str(SSD / "trial-egl13/moderngekko-run-trial"))
    ap.add_argument("--build-json", default=str(SSD / "trial-egl13/build.json"))
    ap.add_argument("--template", default="d2single")
    ap.add_argument("--movie", default="m3-snow-jam-3min.dtm")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    out = SSD / f"{args.tag}-receipts"
    if out.exists():
        raise SystemExit(f"receipts dir already exists: {out}")

    held = shell(f"cat {LEASE} 2>/dev/null")
    if held and held != BRIEF:
        raise SystemExit(f"foreign device lease: {held!r} -- stop")
    running = shell("ps -A | grep moderngekko | grep -v grep")
    if running:
        raise SystemExit(f"moderngekko already running:\n{running}")

    batt = battery()
    if not batt["ok_to_launch"]:
        raise SystemExit(
            "battery gate: need level >= 20 and (status 2/5, or status 3 with "
            "level >= 80); "
            f"have level={batt['level']} status={batt['status']} "
            f"ac_powered={batt['ac_powered']} -- do not launch")
    if batt["suspect_battery_saver"]:
        raise SystemExit("battery saver is on (low_power=1): arm would be CPU-throttled")

    shell(f"printf {BRIEF} > {LEASE}")
    confirmed = shell(f"cat {LEASE}")
    if confirmed != BRIEF:
        raise SystemExit(f"lease write failed, reads {confirmed!r}")
    meta = {"tag": args.tag, "graphics": args.graphics, "brief": BRIEF,
            "battery_before": batt, "settings_before": device_settings()}
    try:
        meta["thermal"] = thermal_gate()
        # android_trial.py creates the receipts dir itself with exist_ok=False,
        # so it must NOT exist yet: stage the pre-run record next to it and move
        # it in afterwards.
        staged_pre = out.parent / f"{args.tag}-pre.json"
        staged_pre.parent.mkdir(parents=True, exist_ok=True)
        staged_pre.write_text(json.dumps(meta, indent=2) + "\n")
        cmd = [sys.executable, str(ROOT / "tools/android_trial.py"), "run",
               "--binary", args.binary, "--build-json", args.build_json,
               "--tag", args.tag, "--output", str(out),
               "--template", args.template, "--movie", args.movie,
               "--graphics", args.graphics, "--idle", "on",
               "--trial-kind", "smoothing", "--trial-secs", "0.0",
               "--timeout", str(args.timeout),
               "--affinity", "emu=80,video=40", "--sampler",
               "--screenshot-seconds", "2", "--serial", SERIAL]
        meta["command"] = " ".join(cmd)
        print(meta["command"], flush=True)
        run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        meta["returncode"] = run.returncode
        out.mkdir(parents=True, exist_ok=True)  # harness may have failed early
        staged_pre.replace(out / f"{args.tag}-pre.json")
        (out / f"{args.tag}-trial-stdout.txt").write_text(run.stdout)
        (out / f"{args.tag}-trial-stderr.txt").write_text(run.stderr)
        # Tombstones rotate fast: pull the crash buffer immediately.
        (out / f"{args.tag}-logcat-crash.txt").write_text(adb("logcat", "-d", "-b", "crash"))
        meta["battery_after"] = battery()
        meta["settings_after"] = device_settings()
        meta["thermal_after"] = {"zones": cpu_zones()}
        # If the harness died before its own pull step, the run's artefacts are
        # still on the device; fetch them so the arm is not lost.
        for name in (f"{args.tag}-probe.jsonl", f"{args.tag}-sampler.log",
                     f"{args.tag}.err", f"{args.tag}.out"):
            if not (out / name).exists():
                adb("pull", f"/data/local/tmp/mg/{name}", str(out / name))
        for remote, local in ((f"/data/local/tmp/mg/user-{args.tag}/Config/GFX.ini",
                               f"{args.tag}-GFX-post.ini"),
                              (f"/data/local/tmp/mg/user-{args.tag}/Config/Dolphin.ini",
                               f"{args.tag}-Dolphin-post.ini")):
            if not (out / local).exists():
                adb("pull", remote, str(out / local))
        sampler = next(iter(sorted(out.glob("*sampler*.log"))), None)
        meta["kill_rule"] = kill_rule_check(sampler)
        (out / f"{args.tag}-arm.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(json.dumps({k: meta[k] for k in
                          ("returncode", "kill_rule")}, indent=2))
    finally:
        shell(f"rm -f {LEASE}")
        left = shell(f"cat {LEASE} 2>/dev/null")
        print(f"device lease after arm: {left!r}", flush=True)


if __name__ == "__main__":
    main()
