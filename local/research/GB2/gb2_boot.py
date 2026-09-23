#!/usr/bin/env python3
"""GB2 boot driver: two-slot-lease-aware, wall-capped boot with frame snapshots.

Usage:
  python3 local/research/GB2/gb2_boot.py --label gb2a --wall 300 --script "..."
  python3 local/research/GB2/gb2_boot.py --label gb2b --wall 300 --script "..." --gs-queue 1
  python3 local/research/GB2/gb2_boot.py --label gb2cap --wall 90 --script "..." --capture-dir <dir>

Lease: claims ONE mini slot via local/tooling/p_lane_lease.py, releases at
end. Tracks the runner by PID only (never pgrep/pkill: the other slot may
be running). Each boot runs from its own cwd.

Compared with E31's wrapper: two-slot lease, no pgrep, per-boot cwd, and
GB2 env (PS2X_GS_QUEUE, PS2X_GS_CAPTURE_DIR, optional `sample` capture).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time

REPO = os.path.expanduser("~/dev/ssx3")
WORK = os.path.expanduser("~/dev/ssx3-work")
sys.path.insert(0, os.path.join(REPO, "local", "tooling"))
import p_lane_lease as lease  # noqa: E402

RUN = os.path.join(WORK, "GB2-run")
RUNNER = os.path.join(WORK, "GB2", "build", "ps2xRuntime", "ps2EntryRunner")
CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

BASE_ENV = {
    "PS2X_CD_IMAGE": ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
}

CAPS = {
    "boot_log": 256 * 1024 * 1024,
    "function_log": 5 * 1024 * 1024 * 1024,
    "frames_dir": 256 * 1024 * 1024,
    "park_dir": 64 * 1024 * 1024,
    "pklog": 512 * 1024 * 1024,
}


def dir_bytes(path):
    total = 0
    for root, _ds, fs in os.walk(path):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--wall", type=int, default=150)
    ap.add_argument("--snap", type=float, default=2.0)
    ap.add_argument("--runner", default=RUNNER)
    ap.add_argument("--script", default=None)
    ap.add_argument("--gs-queue", default=None, help="PS2X_GS_QUEUE value (omit = unset)")
    ap.add_argument("--vq", action="store_true", help="set PS2X_VQ=1 (quiescent gate)")
    ap.add_argument("--pklog", action="store_true", help="set PS2X_PKLOG=1 (packet+CSR log)")
    ap.add_argument("--pkcap", default=None, help="PS2X_PKCAP value (packet idx byte capture)")
    ap.add_argument("--watch", default=None, help="PS2X_DIAG_WATCH value (one-word store watch)")
    ap.add_argument("--csr-drain", action="store_true",
                    help="set PS2X_GS_CSR_DRAIN=1 (drain-on-CSR-load fix)")
    ap.add_argument("--capture-dir", default=None, help="PS2X_GS_CAPTURE_DIR value")
    ap.add_argument("--capture-n", default=None, help="PS2X_GS_CAPTURE_N value")
    ap.add_argument("--sample-at", type=float, default=None,
                    help="wall seconds at which to run `sample` on the runner")
    ap.add_argument("--sample-secs", type=int, default=10)
    args = ap.parse_args()

    label = args.label
    runner = args.runner
    boot_log = os.path.join(RUN, f"boot-{label}-1.log")
    frames_dir = os.path.join(RUN, f"frames-{label}-1")
    park_dir = os.path.join(RUN, f"park-{label}-1")
    snap_dir = os.path.join(frames_dir, "snap")
    boot_cwd = os.path.join(RUN, f"cwd-{label}-1")
    os.makedirs(snap_dir, exist_ok=True)
    os.makedirs(park_dir, exist_ok=True)
    os.makedirs(boot_cwd, exist_ok=True)

    for path in (runner, CDDIR, ISO):
        if not os.path.exists(path):
            print(f"REFUSE: missing {path}", file=sys.stderr)
            return 2

    slot = lease.claim(label)
    if slot is None:
        print(f"REFUSE: no mini slot free: {lease.status()!r}", file=sys.stderr)
        return 2
    print(json.dumps({"event": "claimed", "label": label, "slot": slot}), flush=True)

    env = dict(os.environ)
    env.update(BASE_ENV)
    env["PS2X_DIAG_PARK_DIR"] = park_dir
    env["PS2X_FRAME_DUMP_DIR"] = frames_dir
    env.pop("PS2X_PAD_STIM_AFTER", None)
    env.pop("PS2X_PAD_STIM_WALLMIN", None)
    if args.script is not None:
        env["PS2X_PAD_SCRIPT"] = args.script
        env["PS2X_SKIP_MOVIE"] = "1"
    else:
        env.pop("PS2X_PAD_SCRIPT", None)
    if args.gs_queue is not None:
        env["PS2X_GS_QUEUE"] = args.gs_queue
    else:
        env.pop("PS2X_GS_QUEUE", None)
    if args.vq:
        env["PS2X_VQ"] = "1"
    else:
        env.pop("PS2X_VQ", None)
    if args.pklog:
        env["PS2X_PKLOG"] = "1"
    else:
        env.pop("PS2X_PKLOG", None)
    if args.pkcap is not None:
        env["PS2X_PKCAP"] = args.pkcap
    else:
        env.pop("PS2X_PKCAP", None)
    if args.watch is not None:
        env["PS2X_DIAG_WATCH"] = args.watch
    else:
        env.pop("PS2X_DIAG_WATCH", None)
    if args.csr_drain:
        env["PS2X_GS_CSR_DRAIN"] = "1"
    else:
        env.pop("PS2X_GS_CSR_DRAIN", None)
    if args.capture_dir is not None:
        os.makedirs(args.capture_dir, exist_ok=True)
        env["PS2X_GS_CAPTURE_DIR"] = args.capture_dir
        if args.capture_n is not None:
            env["PS2X_GS_CAPTURE_N"] = args.capture_n
    else:
        env.pop("PS2X_GS_CAPTURE_DIR", None)
        env.pop("PS2X_GS_CAPTURE_N", None)

    stop = threading.Event()

    def snapshotter(t0):
        latest = os.path.join(frames_dir, "upload-latest.png")
        latest_txt = os.path.join(frames_dir, "upload-latest.txt")
        while not stop.wait(args.snap):
            el = time.monotonic() - t0
            try:
                if os.path.exists(latest):
                    shutil.copyfile(latest, os.path.join(snap_dir, f"snap-{el:07.2f}s.png"))
                if os.path.exists(latest_txt):
                    shutil.copyfile(latest_txt, os.path.join(snap_dir, f"snap-{el:07.2f}s.txt"))
            except OSError:
                pass

    rc, bound = -1, "none"
    sample_file = None
    t0 = time.monotonic()
    th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
    with open(boot_log, "wb") as lf:
        proc = subprocess.Popen([runner, CDDIR], cwd=boot_cwd, env=env,
                                stdout=lf, stderr=subprocess.STDOUT)
        print(json.dumps({"event": "boot", "pid": proc.pid, "slot": slot,
                          "runner": runner,
                          "gs_queue": env.get("PS2X_GS_QUEUE", "(unset)"),
                          "capture": env.get("PS2X_GS_CAPTURE_DIR", "(unset)")}),
              flush=True)
        th.start()
        sampled = False
        while True:
            ret = proc.poll()
            el = time.monotonic() - t0
            if ret is not None:
                rc, bound = ret, "exit"
                break
            if args.sample_at is not None and not sampled and el >= args.sample_at:
                sampled = True
                sample_file = os.path.join(RUN, f"sample-{label}-1.txt")
                try:
                    with open(sample_file, "w") as sf:
                        subprocess.run(["sample", str(proc.pid), str(args.sample_secs)],
                                       stdout=sf, stderr=subprocess.STDOUT, timeout=args.sample_secs + 30)
                    print(json.dumps({"event": "sampled", "file": sample_file}), flush=True)
                except Exception as e:  # noqa: BLE001 - sampling is best-effort
                    print(json.dumps({"event": "sample-failed", "error": str(e)}), flush=True)
                    sample_file = None
            if el >= args.wall:
                bound = "wall"
                proc.terminate()
                try:
                    rc = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    rc = proc.wait(timeout=10)
                    bound = "wall+kill"
                break
            over = None
            try:
                if os.path.getsize(boot_log) > CAPS["boot_log"]:
                    over = "boot_log"
                fblog = os.path.join(boot_cwd, "ps2_log.txt")
                if os.path.exists(fblog) and os.path.getsize(fblog) > CAPS["function_log"]:
                    over = "function_log"
                pkblog = os.path.join(boot_cwd, "ps2_pklog.txt")
                if os.path.exists(pkblog) and os.path.getsize(pkblog) > CAPS["pklog"]:
                    over = "pklog"
                if dir_bytes(frames_dir) > CAPS["frames_dir"]:
                    over = "frames_dir"
                if os.path.isdir(park_dir) and dir_bytes(park_dir) > CAPS["park_dir"]:
                    over = "park_dir"
            except OSError:
                pass
            if over:
                bound = f"cap:{over}"
                proc.terminate()
                try:
                    rc = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    rc = proc.wait(timeout=10)
                break
            time.sleep(1.0)
    stop.set()
    th.join(timeout=5)
    elapsed = time.monotonic() - t0

    fblog = os.path.join(boot_cwd, "ps2_log.txt")
    fbrot = os.path.join(RUN, f"ps2_log-{label}-1.txt")
    try:
        if os.path.exists(fblog):
            os.rename(fblog, fbrot)
    except OSError as e:
        print(f"WARN: rotate failed: {e}", file=sys.stderr)
        fbrot = fblog

    pkblog = os.path.join(boot_cwd, "ps2_pklog.txt")
    pkrot = os.path.join(RUN, f"pklog-{label}-1.txt")
    pklog_lines = 0
    try:
        if os.path.exists(pkblog):
            os.rename(pkblog, pkrot)
    except OSError as e:
        print(f"WARN: pklog rotate failed: {e}", file=sys.stderr)
        pkrot = pkblog
    if os.path.exists(pkrot):
        try:
            with open(pkrot, "rb") as pf:
                pklog_lines = sum(1 for _ in pf)
        except OSError:
            pass

    lease.release(slot)
    result = {"label": label, "rc": rc, "bound": bound, "runner": runner,
              "elapsed_s": round(elapsed, 3), "slot": slot,
              "boot_log": boot_log,
              "boot_log_bytes": os.path.getsize(boot_log) if os.path.exists(boot_log) else 0,
              "function_log": fbrot if os.path.exists(fbrot) else None,
              "pklog": pkrot if os.path.exists(pkrot) else None,
              "pklog_bytes": os.path.getsize(pkrot) if os.path.exists(pkrot) else 0,
              "pklog_lines": pklog_lines,
              "frames_dir": frames_dir, "park_dir": park_dir,
              "sample": sample_file,
              "gs_queue": env.get("PS2X_GS_QUEUE", "(unset)"),
              "lease_released": True}
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
