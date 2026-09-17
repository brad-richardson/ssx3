"""GPU-trace capture around an automated trial window on a tethered iOS device.

Flow: launch the app with the given run flags, wait until just before the
trial window, attach an xctrace recording (default: Metal System Trace) for a
bounded window, then collect the session so the trace aligns with trial data.

Wall-clock note: the sequence clock starts ~19 s after launch (boot +
checkpoint), so a trial at sequence 155 fires around wall 174. The default
attach delay (160 s) plus window (60 s) covers sequence ~141-201.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mobile_gamecube

ROOT = Path(__file__).resolve().parents[1]
PROCESS = "SSXNative"  # CMake target / executable name in SSXNative.app
DEFAULT_TEMPLATE = "Metal System Trace"


def sha(path):
    path = Path(path)
    if path.is_dir():
        # A .trace bundle is a directory: hash names plus contents.
        digest = hashlib.sha256()
        for file in sorted(path.rglob("*")):
            if not file.is_file():
                continue
            digest.update(str(file.relative_to(path)).encode())
            with open(file, "rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(chunk)
        return digest.hexdigest()
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trace_size(trace):
    trace = Path(trace)
    if trace.is_file():
        return trace.stat().st_size
    return sum(p.stat().st_size for p in trace.rglob("*") if p.is_file())


def check_device(device, run=subprocess.run):
    """Prove the device is ready for tracing with a 1 s probe capture."""
    with tempfile.TemporaryDirectory(prefix="ssx-gpu-check-") as tmp:
        probe = str(Path(tmp) / "probe.trace")
        completed = run(["xctrace", "record", "--template", "System Trace",
                         "--device", device, "--all-processes",
                         "--time-limit", "1s", "--output", probe],
                        capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f"Device {device} is not ready for tracing "
                           f"(dev mode / DDI mounted?): {completed.stderr.strip()[:300]}")
    return True


def build_record_command(*, device, template, window, output, pid=None,
                         all_processes=False):
    target = ["--all-processes"] if all_processes else ["--attach", str(pid)]
    return ["xctrace", "record", "--template", template, "--device", device,
            *target, "--time-limit", f"{window}s",
            "--no-prompt", "--output", str(output)]


def wait_for_process(device, timeout_s=30, poll_s=2, sleep=time.sleep):
    """Poll the device process list for our executable; attach needs a PID."""
    deadline = time.monotonic() + timeout_s
    while True:
        result = mobile_gamecube.device_call(
            ["device", "info", "processes", "--device", device], timeout=60)
        # device_call already unwraps the top-level "result" key.
        processes = (result or {}).get("runningProcesses", [])
        for process in processes:
            executable = process.get("executable", "")
            if executable.rsplit("/", 1)[-1] == PROCESS:
                return process["processIdentifier"]
        if time.monotonic() >= deadline:
            raise RuntimeError(f"{PROCESS} not running on {device} "
                               f"(exited early? check the session)")
        sleep(poll_s)


def launch_namespace(args):
    return argparse.Namespace(
        device=args.device, simulator=False, sequence=args.sequence,
        internal_scale=args.internal_scale, cpu_thread=args.cpu_thread,
        single_core=args.single_core, smoothing_at=args.smoothing_at,
        f_at=args.f_at, combo_at=args.combo_at, textures=args.textures,
        preload_textures=args.preload_textures,
        course_manifest=args.course_manifest)


def capture(args, clock=time.sleep, run=subprocess.run):
    if args.window <= 0 or args.attach_delay < 0:
        raise ValueError("--window must be positive and --attach-delay nonnegative")
    outdir = args.output or (ROOT / "local/reports/gpu-captures" /
                             datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    outdir.mkdir(parents=True, exist_ok=True)
    trace = outdir / "capture.trace"
    mobile_gamecube.launch(launch_namespace(args))
    clock(args.attach_delay)
    # Device-process attach is broken host-side (xctrace cannot resolve any
    # device PID or name); --all-processes records system-wide instead and the
    # app's counters are extracted from the trace by process name.
    all_processes = getattr(args, "all_processes", False)
    pid = None if all_processes else wait_for_process(args.device)
    completed = run(build_record_command(device=args.device, template=args.template,
                                         window=args.window, output=trace, pid=pid,
                                         all_processes=all_processes),
                    capture_output=True, text=True)
    if completed.returncode:
        stderr = (completed.stderr or "").strip()[:300]
        raise RuntimeError(f"xctrace record failed: {stderr}")
    collect_args = argparse.Namespace(device=args.device, simulator=False)
    mobile_gamecube.collect(collect_args)
    receipt = write_receipt(outdir, trace, args,
                            target="all-processes" if all_processes else f"pid:{pid}")
    print(f"Captured {trace} ({trace_size(trace) / 1e6:.0f} MB)")
    return receipt


def write_receipt(outdir, trace, args, target):
    """Write the receipt for a finished capture; reused to salvage runs
    whose recording completed but whose receipt step never ran."""
    receipt = {
        "device": args.device, "template": args.template, "target": target,
        "attach_delay_wall_s": args.attach_delay, "window_s": args.window,
        "trace": str(trace), "trace_sha256": sha(trace),
        "sequence": str(args.sequence), "sequence_sha256": sha(args.sequence),
        "run_flags": {k: getattr(args, k) for k in
                      ("internal_scale", "cpu_thread", "single_core", "smoothing_at",
                       "f_at", "combo_at", "textures", "preload_textures",
                       "course_manifest")},
    }
    (Path(outdir) / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Probe that a device is ready for tracing")
    check.add_argument("--device", required=True)
    cap = sub.add_parser("capture", help="Record a GPU trace around a trial window")
    cap.add_argument("--device", required=True,
                     help="Target UDID (iPad Air: 00008112-001224302184A01E)")
    cap.add_argument("--sequence", type=Path, required=True)
    cap.add_argument("--template", default=DEFAULT_TEMPLATE)
    cap.add_argument("--attach-delay", type=float, default=160,
                     help="Wall seconds after launch to attach (default 160)")
    cap.add_argument("--window", type=float, default=60,
                     help="Recording seconds (default 60)")
    cap.add_argument("--all-processes", action="store_true",
                     help="Record system-wide; extract the app by process name later")
    cap.add_argument("--output", type=Path, help="Capture directory")
    cap.add_argument("--internal-scale", type=int, choices=(1, 2, 3, 4))
    cap.add_argument("--cpu-thread", action="store_true")
    cap.add_argument("--single-core", action="store_true")
    cap.add_argument("--smoothing-at", type=float)
    cap.add_argument("--f-at", type=float)
    cap.add_argument("--combo-at", type=float)
    cap.add_argument("--textures", choices=("stock", "remaster"))
    cap.add_argument("--preload-textures", choices=("on", "off"))
    cap.add_argument("--course-manifest")
    args = parser.parse_args(argv)
    if args.command == "check":
        check_device(args.device)
        print(f"Device {args.device} is ready for tracing")
    else:
        capture(args)


if __name__ == "__main__":
    main()
