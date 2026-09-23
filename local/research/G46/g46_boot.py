#!/usr/bin/env python3
"""G46 boot wrapper: G44 shadow (paraLLEl) + G46 stride/recorder, E51 route.

Usage:
  python3 local/research/G46/g46_boot.py --label g46a --wall 540 \
      --sfrom 700 --sto 2300 --stride 8 [--rec] [--force-smode1 ntsc]

Lease: claims a p_lane slot (p_lane_lease.py), releases on exit.
"""
import json
import os
import subprocess
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import argparse

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "G46", "run")
b.RUNNER = os.path.join(WORK, "G46", "build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

# E51/I25 route (vsync clock): title -> Main Menu -> Select Character ->
# Select Peak -> Select Mode -> Select Event -> My Rules -> race.
ROUTE = ("10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,"
         "30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,"
         "64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,"
         "113340:down:20000")

ap = argparse.ArgumentParser()
ap.add_argument("--sfrom", default="0")
ap.add_argument("--sto", default="18446744073709551615")
ap.add_argument("--stride", default="1")
ap.add_argument("--rec", action="store_true")
ap.add_argument("--force-smode1", default="ntsc")
known, rest = ap.parse_known_args()
sys.argv = [sys.argv[0]] + rest
if "--script" not in sys.argv:
    sys.argv += ["--script", ROUTE]

label = ""
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_SKIP_MOVIE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
    "PS2X_GS_SHADOW": "parallel",
    "GRANITE_VULKAN_LIBRARY": "/opt/homebrew/lib/libvulkan.1.dylib",
    "PS2X_GS_SHADOW_FROM": known.sfrom,
    "PS2X_GS_SHADOW_TO": known.sto,
    "PS2X_GS_SHADOW_STRIDE": known.stride,
    "PS2X_GS_SHADOW_DIR": os.path.join(b.RUN, "shadow-%s" % label),
}
if known.force_smode1:
    BASE["PS2X_GS_SHADOW_FORCE_SMODE1"] = known.force_smode1
if known.rec:
    BASE["PS2X_GS_SHADOW_REC"] = os.path.join(b.RUN, "rec-%s.bin" % label)
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.path.insert(0, os.path.join(REPO, "local/tooling"))
from p_lane_lease import SLOTS, claim, release

slot = claim(label or "g46x")
if slot is None:
    print("REFUSE: no free boot slot (p_lane_lease.py status)", file=sys.stderr)
    sys.exit(2)
b.LEASE = SLOTS[slot]
pp = subprocess.run(["pgrep", "-x", "ps2EntryRunner"], capture_output=True, text=True)
peers = [x for x in pp.stdout.split() if x.strip().isdigit()] if pp.returncode == 0 else []
os.environ["P_LANE_PEER_PIDS"] = ",".join(peers)
os.environ["P_LANE_HOLD"] = "1"
print(json.dumps({"event": "slot", "slot": slot, "peers": peers}), flush=True)
rc = 99
try:
    rc = b.main()
finally:
    release(slot)
sys.exit(rc)
