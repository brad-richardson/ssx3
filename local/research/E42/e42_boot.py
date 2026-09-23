#!/usr/bin/env python3
"""E42 boot wrapper: vsync-clock pad script + CALL-plant attribution trace.

Usage:
  python3 local/research/E42/e42_boot.py --label e42a --wall 300 --snap 30 \
      --script "..." --cd-from 1270 --cd-to 1300

Env added over E31's base: PS2X_CD_READ_TRACE=<run>/cdread-<label>.txt
plus _FROM/_TO (the plant watch window).
"""

import os
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "E42-run")
b.RUNNER = os.path.join(WORK, "E32-build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

import argparse

pre = argparse.ArgumentParser(add_help=False)
pre.add_argument("--cd-from", type=str, default=None)
pre.add_argument("--cd-to", type=str, default=None)
known, rest = pre.parse_known_args()
sys.argv = [sys.argv[0]] + rest

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]
    elif a.startswith("--label="):
        label = a.split("=", 1)[1]

cd_file = os.path.join(b.RUN, f"cdread-{label}.txt") if label else None

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
}
if cd_file:
    BASE["PS2X_CD_READ_TRACE"] = cd_file
if known.cd_from is not None:
    BASE["PS2X_CD_READ_TRACE_FROM"] = known.cd_from
if known.cd_to is not None:
    BASE["PS2X_CD_READ_TRACE_TO"] = known.cd_to
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.exit(b.main())
