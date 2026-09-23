#!/usr/bin/env python3
"""E49 boot wrapper: E48's wrapper (E33 route + PS2X_DIAG_WATCH on the
0x3b1140 node/pool), pointed at the E49 runner, with the movie bypass as
an explicit switch.

Usage:
  python3 local/research/E49/e49_boot.py --skip 1|0 --label e49a \
      --wall 300 --snap 2 --script "<E33 route>"

--skip 1 sets PS2X_SKIP_MOVIE=1 (boot A); --skip 0 leaves it unset
(boot B, faithful movie path). Runner: ~/dev/ssx3-work/E49-build/ps2xRuntime/ps2EntryRunner (SHA read
twice before each boot; no rebuild while a boot runs).
"""

import json
import os
import subprocess
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
E49 = os.path.join(WORK, "E49")

# Node 0x548840 (+0..+0x20), sibling nodes' +8 links, a 5th candidate
# node's links, codec/pool 0x587b00 (+0x10 count, +0x18 active sentinel,
# +0x20 free sentinel), holder 0x587b80 (+0 player, +0xc picture), and
# guest 0x8..0xf (targets of an unlink through close-poisoned 0xb links).
WATCH = [
    0x548840, 0x548848, 0x548850, 0x548858,
    0x548788, 0x5487c8, 0x548808, 0x548888,
    0x587b10, 0x587b18, 0x587b20,
    0x587b80, 0x587b88,
    0x8,
]

skip = None
for i, a in enumerate(sys.argv):
    if a == "--skip" and i + 1 < len(sys.argv):
        skip = sys.argv[i + 1]
if skip not in ("1", "0"):
    print("need --skip 1|0", file=sys.stderr)
    sys.exit(2)
i = sys.argv.index("--skip")
del sys.argv[i:i + 2]

b.SPIKE = WORK
b.RUN = os.path.join(E49, "run")
b.RUNNER = os.path.join(WORK, "E49-build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
    "PS2X_DIAG_WATCH": ",".join(hex(a) for a in WATCH),
}
if skip == "1":
    BASE["PS2X_SKIP_MOVIE"] = "1"
else:
    os.environ.pop("PS2X_SKIP_MOVIE", None)
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.path.insert(0, os.path.join(REPO, "local/tooling"))
from p_lane_lease import SLOTS, claim, release

slot = claim(label if label else "e49x")
if slot is None:
    print("REFUSE: no free boot slot (p_lane_lease.py status)", file=sys.stderr)
    sys.exit(2)
b.LEASE = SLOTS[slot]
pp = subprocess.run(["pgrep", "-x", "ps2EntryRunner"],
                    capture_output=True, text=True)
peers = [x for x in pp.stdout.split() if x.strip().isdigit()] \
    if pp.returncode == 0 else []
os.environ["P_LANE_PEER_PIDS"] = ",".join(peers)
os.environ["P_LANE_HOLD"] = "1"
print(json.dumps({"event": "slot", "slot": slot, "peers": peers,
                  "skip": skip, "watch": BASE["PS2X_DIAG_WATCH"]}),
      flush=True)

rc = 99
try:
    rc = b.main()
finally:
    release(slot)
sys.exit(rc)
