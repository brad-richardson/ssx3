#!/usr/bin/env python3
"""E31 boot driver: lease-claimed, wall-capped boot with frame snapshots.

Usage:
  python3 e31_boot.py --label e31a --wall 150 --after 1 --wallmin 60

Lease: claims /tmp/ssx3-p-lane-lease, releases at end. Refuses to boot if
another runner lives or the lease is held. Snapshots upload-latest.png
every --snap seconds into <frames>/snap/snap-<elapsed>s.{png,txt}.
"""
import argparse, json, os, shutil, signal, subprocess, sys, threading, time

SPIKE = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = os.path.join(SPIKE, "P1", "run")
RUNNER = os.path.join(SPIKE, "e29-movie-bypass-build", "ps2xRuntime", "ps2EntryRunner")
CDDIR = os.path.join(SPIKE, "P1", "cd", "SLUS_207.72")
ISO = os.path.join(SPIKE, "SSX 3 (USA).iso")
LEASE = "/tmp/ssx3-p-lane-lease"

BASE_ENV = {
    "PS2X_CD_IMAGE": ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "PS2X_SKIP_MOVIE": "1",
    "COPYFILE_DISABLE": "1",
}

CAPS = {
    "boot_log": 256 * 1024 * 1024,
    # e31f hit 2 GiB at 300 s (guest function trace ~7 MB/s); 550 s needs ~4 GiB.
    "function_log": 5 * 1024 * 1024 * 1024,
    "frames_dir": 256 * 1024 * 1024,
    "park_dir": 64 * 1024 * 1024,
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
    ap.add_argument("--after", type=str, default="1")
    ap.add_argument("--wallmin", type=str, default="60")
    ap.add_argument("--snap", type=float, default=2.0)
    ap.add_argument("--runner", type=str, default=RUNNER,
                    help="ps2EntryRunner binary (default: E29 bypass build)")
    ap.add_argument("--script", type=str, default=None,
                    help="PS2X_PAD_SCRIPT value (Mission 2+); omit for stim-only")
    ap.add_argument("--no-stim", action="store_true",
                    help="do not set PS2X_PAD_STIM_* at all")
    args = ap.parse_args()

    label = args.label
    runner = args.runner
    boot_log = os.path.join(RUN, f"boot-{label}-1.log")
    frames_dir = os.path.join(RUN, f"frames-{label}-1")
    park_dir = os.path.join(RUN, f"park-{label}-1")
    snap_dir = os.path.join(frames_dir, "snap")
    os.makedirs(snap_dir, exist_ok=True)
    os.makedirs(park_dir, exist_ok=True)  # park writer does not create dirs

    # Pre-claim checks.
    if os.path.exists(LEASE):
        print(f"REFUSE: lease held: {open(LEASE).read()!r}", file=sys.stderr)
        return 2
    p = subprocess.run(["pgrep", "-x", "ps2EntryRunner"],
                       capture_output=True, text=True)
    if p.returncode == 0:
        print(f"REFUSE: runner alive: {p.stdout!r}", file=sys.stderr)
        return 2
    for path in (runner, CDDIR, ISO):
        if not os.path.exists(path):
            print(f"REFUSE: missing {path}", file=sys.stderr)
            return 2

    with open(LEASE, "w") as f:
        f.write(label + "\n")
    claim_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(json.dumps({"event": "claimed", "label": label, "utc": claim_utc}),
          flush=True)

    env = dict(os.environ)
    env.update(BASE_ENV)
    env["PS2X_DIAG_PARK_DIR"] = park_dir
    env["PS2X_FRAME_DUMP_DIR"] = frames_dir
    if not args.no_stim:
        env["PS2X_PAD_STIM_AFTER"] = args.after
        env["PS2X_PAD_STIM_WALLMIN"] = args.wallmin
    else:
        env.pop("PS2X_PAD_STIM_AFTER", None)
        env.pop("PS2X_PAD_STIM_WALLMIN", None)
    if args.script is not None:
        env["PS2X_PAD_SCRIPT"] = args.script
    else:
        env.pop("PS2X_PAD_SCRIPT", None)

    stop = threading.Event()

    def snapshotter(t0):
        latest = os.path.join(frames_dir, "upload-latest.png")
        latest_txt = os.path.join(frames_dir, "upload-latest.txt")
        while not stop.wait(args.snap):
            el = time.monotonic() - t0
            try:
                if os.path.exists(latest):
                    shutil.copyfile(latest,
                                    os.path.join(snap_dir, f"snap-{el:07.2f}s.png"))
                if os.path.exists(latest_txt):
                    shutil.copyfile(latest_txt,
                                    os.path.join(snap_dir, f"snap-{el:07.2f}s.txt"))
            except OSError:
                pass

    rc, bound = -1, "none"
    t0 = time.monotonic()
    th = threading.Thread(target=snapshotter, args=(t0,), daemon=True)
    with open(boot_log, "wb") as lf:
        proc = subprocess.Popen([runner, CDDIR], cwd=RUN, env=env,
                                stdout=lf, stderr=subprocess.STDOUT)
        print(json.dumps({"event": "boot", "pid": proc.pid, "runner": runner,
                          "env": {k: env[k] for k in
                                  ("PS2X_SKIP_MOVIE", "PS2X_PAD_STIM_AFTER",
                                   "PS2X_PAD_STIM_WALLMIN", "PS2X_PAD_SCRIPT",
                                   "PS2X_FRAME_DUMP_DIR")
                                  if k in env}}), flush=True)
        th.start()
        poll = 1.0
        while True:
            ret = proc.poll()
            el = time.monotonic() - t0
            if ret is not None:
                rc, bound = ret, "exit"
                break
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
                fblog = os.path.join(RUN, "ps2_log.txt")
                if os.path.exists(fblog) and \
                        os.path.getsize(fblog) > CAPS["function_log"]:
                    over = "function_log"
                if dir_bytes(frames_dir) > CAPS["frames_dir"]:
                    over = "frames_dir"
                if os.path.isdir(park_dir) and \
                        dir_bytes(park_dir) > CAPS["park_dir"]:
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
            time.sleep(poll)
    stop.set()
    th.join(timeout=5)
    elapsed = time.monotonic() - t0

    # Rotate the function trace out of the shared cwd.
    fblog = os.path.join(RUN, "ps2_log.txt")
    fbrot = os.path.join(RUN, f"ps2_log-{label}-1.txt")
    try:
        if os.path.exists(fblog):
            os.rename(fblog, fbrot)
    except OSError as e:
        print(f"WARN: rotate failed: {e}", file=sys.stderr)
        fbrot = fblog

    # Release.
    try:
        os.remove(LEASE)
    except OSError as e:
        print(f"WARN: release failed: {e}", file=sys.stderr)
    p = subprocess.run(["pgrep", "-x", "ps2EntryRunner"],
                       capture_output=True, text=True)
    result = {"label": label, "rc": rc, "bound": bound, "runner": runner,
              "elapsed_s": round(elapsed, 3),
              "boot_log": boot_log,
              "boot_log_bytes": os.path.getsize(boot_log),
              "function_log": fbrot,
              "frames_dir": frames_dir, "park_dir": park_dir,
              "lease_released": not os.path.exists(LEASE),
              "pgrep_rc": p.returncode}
    print(json.dumps(result), flush=True)
    with open(os.path.join(RUN, f"{label}-result.json"), "w") as f:
        json.dump(result, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
