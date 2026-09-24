#!/usr/bin/env python3
"""I26 Mac route-timing boot: the E31 driver (lease slot, wall cap, frame
dump + snapshots) on the I26 build, with only the route env set.

Usage: i26_boot.py --label i26a --wall 420 --snap 0.5 --script "<route>"
Env set: PS2X_CD_IMAGE, PS2X_SKIP_MOVIE=1, PS2X_PAD_SCRIPT_CLOCK=vsync,
COPYFILE_DISABLE=1 (+ the driver's PS2X_FRAME_DUMP_DIR). No trace taps.
"""
import json, os, subprocess, sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "I26", "run")
b.RUNNER = os.path.join(WORK, "I26", "build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")
b.BASE_ENV = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_SKIP_MOVIE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
    "COPYFILE_DISABLE": "1",
}
os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")
label = sys.argv[sys.argv.index("--label") + 1]

sys.path.insert(0, os.path.join(REPO, "local/tooling"))
from p_lane_lease import SLOTS, claim, release

slot = claim("I26-" + label)
if slot is None:
    print("REFUSE: no free boot slot", file=sys.stderr)
    sys.exit(2)
b.LEASE = SLOTS[slot]
pp = subprocess.run(["pgrep", "-x", "ps2EntryRunner"], capture_output=True, text=True)
os.environ["P_LANE_PEER_PIDS"] = ",".join(pp.stdout.split()) if pp.returncode == 0 else ""
os.environ["P_LANE_HOLD"] = "1"
print(json.dumps({"event": "slot", "slot": slot}), flush=True)
rc = 99
try:
    rc = b.main()
finally:
    release(slot)
sys.exit(rc)
