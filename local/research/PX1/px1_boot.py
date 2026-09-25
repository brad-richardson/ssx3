#!/usr/bin/env python3
"""PX1 deterministic I26-FAST race boot: one lease slot (waits), bounded by
target vsync (from [diag:frame] lines), wall cap and output caps.
Usage: px1_boot.py <label> <target_vsync> [--runner R] [--wall S]
                   [--dump-ticks A,B,C] [--capture 0|1] [ENV=VAL ...]
Run dir: ~/dev/ssx3-work/PX1/run-<label> (boot.log, result.json, frames/,
gs.cap when --capture 1). ParaLLEl backend + PGS_HIER_BINNING=force (GB9),
sound on (play-like). Adapted from RR1's rr1_boot.py for the PX1 workdir."""
import json, os, re, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/Users/brad/dev/ssx3/local/tooling")
from p_lane_lease import claim, release, status

W = Path("/Users/brad/dev/ssx3-work/PX1")
W.mkdir(parents=True, exist_ok=True)
ELF = Path("/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72")
ISO = Path("/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso")
I26_FAST = ("10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,"
            "18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,"
            "22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,"
            "29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,"
            "31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,"
            "33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,"
            "35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,"
            "37521:cross:200,37772:down:700,38522:down:30000")
VULKAN_LIB = "/opt/homebrew/lib/libvulkan.1.dylib"

args = sys.argv[1:]
label, target = args[0], int(args[1])
runner = Path("/Users/brad/dev/ssx3-work/F2/bin/runner-det")
wall = 500
dump_ticks = "1090,1180,1800"
capture = True
extra = {}
i = 2
while i < len(args):
    if args[i] == "--runner":
        runner = Path(args[i + 1]); i += 2
    elif args[i] == "--wall":
        wall = int(args[i + 1]); i += 2
    elif args[i] == "--dump-ticks":
        dump_ticks = args[i + 1]; i += 2
    elif args[i] == "--capture":
        capture = args[i + 1] != "0"; i += 2
    else:
        k, v = args[i].split("=", 1); extra[k] = v; i += 1
assert wall <= 600
RUN = W / f"run-{label}"
assert not RUN.exists(), f"refusing to reuse {RUN}"
RUN.mkdir(parents=True)
(RUN / "frames").mkdir()
(RUN / "mc0").mkdir()
(RUN / "mc1").mkdir()
BOOT = RUN / "boot.log"
CAP = RUN / "gs.cap"
CAPS = {BOOT: 256 << 20, CAP: 6 << 30}
VS = re.compile(rb"\[diag:frame\] block=\d+ vsync=(\d+)")


def size(p):
    return p.stat().st_size if p.exists() else 0


def last_vsync():
    try:
        with BOOT.open("rb") as f:
            f.seek(max(0, size(BOOT) - (1 << 20)))
            m = VS.findall(f.read())
            return int(m[-1]) if m else 0
    except OSError:
        return 0


slot = None
t0 = time.monotonic()
while slot is None:
    slot = claim(f"px1-{label}")
    if slot is None:
        if time.monotonic() - t0 > 1800:
            print(json.dumps({"refuse": "no slot in 30 min", "slots": status()})); sys.exit(2)
        time.sleep(3)
print(json.dumps({"slot": slot}), flush=True)
proc = None
try:
    env = dict(os.environ)
    env.update({
        "PS2X_CD_IMAGE": str(ISO), "PS2X_SKIP_MOVIE": "1", "PS2X_DETERMINISTIC": "1",
        "PS2X_PAD_SCRIPT_CLOCK": "vsync", "PS2X_PAD_SCRIPT": I26_FAST,
        "PS2X_DIAG_PERIOD_MS": "3000", "PS2X_DIAG_PARK": "1", "PS2X_DIAG_REPORT_ALL": "1",
        "PS2X_GS_BACKEND": "parallel", "GRANITE_VULKAN_LIBRARY": VULKAN_LIB,
        "PGS_HIER_BINNING": "force", "PS2X_SOUND": "1",
        "PS2X_MC_ROOT": str(RUN / "mc0"),
        "PS2X_FRAME_DUMP_DIR": str(RUN / "frames"),
        "PS2X_FRAME_DUMP_ONCE_TICKS": dump_ticks,
        "COPYFILE_DISABLE": "1",
    })
    if capture:
        env["PS2X_GS_CAPTURE"] = str(CAP)
        env["PS2X_GS_CAPTURE_STOP_TICK"] = str(target)
    env.update(extra)
    start = time.monotonic()
    with BOOT.open("wb") as log:
        proc = subprocess.Popen([str(runner), str(ELF)], cwd=RUN, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
        print(json.dumps({"pid": proc.pid, "runner": str(runner)}), flush=True)
        bound, lastv, lastp = None, 0, start
        while True:
            now = time.monotonic()
            if proc.poll() is not None:
                bound = "exit"; break
            v = last_vsync()
            if v >= target:
                bound = "target"; break
            if now - start > wall:
                bound = "wall"; break
            over = [str(p) for p, c in CAPS.items() if size(p) > c]
            if over:
                bound = "cap:" + over[0]; break
            if v > lastv:
                lastv, lastp = v, now
            if now - start > 120 and now - lastp > 90:
                bound = "stall"; break
            time.sleep(1)
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=10); bound += "+kill"
    res = {"label": label, "slot": slot, "pid": proc.pid, "rc": proc.returncode, "bound": bound,
           "vsync": last_vsync(), "elapsed_s": round(time.monotonic() - start, 1),
           "boot_bytes": size(BOOT), "cap_bytes": size(CAP), "env_extra": extra}
    (RUN / "result.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res), flush=True)
finally:
    if proc is not None and proc.poll() is None:
        proc.kill()
    release(slot)
