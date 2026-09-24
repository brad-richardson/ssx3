#!/usr/bin/env python3
"""N8D7M12 Part 4: exact stream staging + Odin preflight, no launch.

Read-only inputs (never written):
  ~/dev/ssx3-work/N8D7M6/n8d7m6.gs
  ~/dev/ssx3-work/N8D7M12P3/app-release.apk
Serial from local/odin-serial. Every adb uses -s. At most one push.
No install, no launch, no ps2x.env write, no device-file delete.
Lease /data/local/tmp/mg/LEASE held while touching Odin; released in
finally only when it still carries our exact tag.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SERIAL = (REPO / "local" / "odin-serial").read_text().strip()
PKG = "com.ps2x.runner"
FILES = f"/storage/emulated/0/Android/data/{PKG}/files"
REMOTE = f"{FILES}/n8d7m6.gs"
LEASE = "/data/local/tmp/mg/LEASE"
TAG = f"N8D7M12P4 staging {int(time.time())}"
STREAM = Path("/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs")
APK = Path("/Users/brad/dev/ssx3-work/N8D7M12P3/app-release.apk")
STREAM_PIN = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
STREAM_SIZE = 1100696462
APK_PIN = "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512"
APK_SIZE = 153753116

result = {"brief": "N8D7M12P4", "serial": SERIAL, "push_count": 0,
          "events": [], "verdict": "not found",
          "first_failure": "not found"}
claimed = False


def record(msg):
    print(msg, flush=True)
    result["events"].append(msg)
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")


def file_sha(path):
    d = hashlib.sha256()
    with path.open("rb") as h:
        for c in iter(lambda: h.read(4 * 1024 * 1024), b""):
            d.update(c)
    return d.hexdigest()


def adb(*args, timeout=90, check=True):
    p = subprocess.run(["adb", "-s", SERIAL, *args], capture_output=True,
                       text=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(f"adb {args} rc={p.returncode}: "
                           f"{p.stderr.strip()} {p.stdout.strip()}")
    return p.stdout


def shell(cmd, timeout=90):
    return adb("shell", cmd, timeout=timeout).strip()


def main():
    global claimed
    # 1. local pins: two matching SHA reads + size, both inputs
    for label, path, pin, size in (("local_stream", STREAM, STREAM_PIN, STREAM_SIZE),
                                   ("local_apk", APK, APK_PIN, APK_SIZE)):
        st = path.stat().st_size
        reads = [file_sha(path) for _ in range(2)]
        result["hashes_" + label] = reads
        result["size_" + label] = st
        record(f"LOCAL {label} size={st} sha={reads[0]} {reads[1]}")
        if st != size or reads != [pin, pin]:
            raise RuntimeError(f"{label} pin mismatch")
    # 2. host-side device presence
    devices = adb("devices", timeout=30)
    (HERE / "adb-devices.txt").write_text(devices)
    record("DEVICES " + devices.replace("\n", " | "))
    if f"{SERIAL}\tdevice" not in devices:
        raise RuntimeError("odin not in device state")
    # 3. lease must be free before claim
    lease0 = shell(f"cat {LEASE}", timeout=30)
    result["lease_before"] = lease0
    record(f"LEASE_BEFORE {lease0!r}")
    if not lease0.startswith("LEASE_FREE"):
        raise RuntimeError(f"lease not free: {lease0!r}")
    # 4. claim with unique tag, verify persistence
    shell(f"echo '{TAG}' > {LEASE}", timeout=30)
    lease1 = shell(f"cat {LEASE}", timeout=30)
    if lease1 != TAG:
        raise RuntimeError("lease claim did not persist")
    claimed = True
    result["lease_tag"] = TAG
    record(f"LEASE claimed {TAG!r}")
    # 5. read-only preflight under lease
    policy = shell("dumpsys window policy", timeout=60)
    (HERE / "adb-window-policy.txt").write_text(policy)
    m = re.search(r"KeyguardServiceDelegate\s+showing=(\w+)", policy)
    keyguard = m.group(1) if m else "unknown"
    battery = shell("dumpsys battery", timeout=60)
    (HERE / "adb-battery.txt").write_text(battery)
    lvl = re.search(r"\blevel:\s*(\d+)", battery)
    sts = re.search(r"\bstatus:\s*(\d+)", battery)
    if not lvl or not sts:
        raise RuntimeError("battery parse failed")
    level, status = int(lvl.group(1)), int(sts.group(1))
    df = shell("df -k /storage/emulated/0", timeout=60)
    (HERE / "adb-df.txt").write_text(df)
    free = int(df.splitlines()[-1].split()[3]) * 1024
    pid = adb("shell", f"pidof {PKG}", check=False, timeout=30).strip()
    exists = shell(f"if test -f {REMOTE}; then echo present; else echo absent; fi",
                   timeout=60)
    rsize = int(shell(f"if test -f {REMOTE}; then stat -c %s {REMOTE}; else echo 0; fi",
                      timeout=120))
    result.update({"keyguard": keyguard, "battery_level": level,
                   "battery_status": status, "free_bytes": free,
                   "app_pid_preflight": pid, "remote_exists": exists,
                   "remote_size": rsize})
    record(f"PREFLIGHT keyguard={keyguard} battery={level}% status={status} "
           f"free_bytes={free} app_pid={pid!r} remote={exists} rsize={rsize}")
    if keyguard != "false":
        record("NOTE keyguard showing: staging may proceed, no launch in this part")
    if level < 20 or status not in (2, 5):
        raise RuntimeError(f"battery gate failed: {level}% status={status}")
    if free < 10 * 1024**3:
        raise RuntimeError(f"space gate failed: {free} < 10 GiB")
    # 6. device stream: reuse on match, else one push, never overwrite mismatch
    if exists == "present":
        if rsize != STREAM_SIZE:
            result["remote_sha"] = []
            result["verdict"] = "B"
            record(f"REMOTE_MISMATCH size local={STREAM_SIZE} remote={rsize}; no overwrite")
            return
        reads = [shell(f"sha256sum {REMOTE}", timeout=300).split()[0]
                 for _ in range(2)]
        result["remote_sha"] = reads
        record(f"REMOTE_SHA {reads[0]} {reads[1]} size={rsize}")
        if reads != [STREAM_PIN, STREAM_PIN]:
            result["verdict"] = "B"
            record("REMOTE_MISMATCH sha differs; no overwrite")
            return
        record("REMOTE reuse: exact match, no push")
    else:
        adb("push", str(STREAM), REMOTE, timeout=600)
        result["push_count"] = 1
        record("PUSH one adb push complete")
        rsize2 = int(shell(f"stat -c %s {REMOTE}", timeout=120))
        reads = [shell(f"sha256sum {REMOTE}", timeout=300).split()[0]
                 for _ in range(2)]
        result["remote_sha"] = reads
        result["remote_size"] = rsize2
        record(f"REMOTE_SHA {reads[0]} {reads[1]} size={rsize2}")
        if rsize2 != STREAM_SIZE or reads != [STREAM_PIN, STREAM_PIN]:
            raise RuntimeError("pushed stream verify failed")
    # 7. app stopped at end
    pid_end = adb("shell", f"pidof {PKG}", check=False, timeout=30).strip()
    result["app_pid_end"] = pid_end
    record(f"APP_END pid={pid_end!r}")
    if pid_end:
        raise RuntimeError("app running at end (we never launched; left untouched)")
    result["verdict"] = "A"
    record("VERDICT A")


if __name__ == "__main__":
    try:
        main()
    except (Exception, SystemExit) as exc:
        if result["verdict"] == "not found":
            result["verdict"] = "OTHER"
        result["first_failure"] = str(exc)
        record("ERROR " + repr(exc))
        raise
    finally:
        if claimed:
            try:
                cur = shell(f"cat {LEASE}", timeout=30)
                if cur == TAG:
                    shell(f"echo 'LEASE_FREE N8D7M12P4 done' > {LEASE}", timeout=30)
                    result["lease_after"] = shell(f"cat {LEASE}", timeout=30)
                    record("LEASE released: " + result["lease_after"])
                else:
                    result["lease_after"] = cur
                    record(f"LEASE not ours at release ({cur!r}); left untouched")
            except Exception as exc:
                record("LEASE release error=" + repr(exc))
        (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
