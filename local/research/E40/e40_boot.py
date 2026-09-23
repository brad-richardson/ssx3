#!/usr/bin/env python3
"""E40 boot wrapper: vsync-clock pad script + MPG source trace.

Usage:
  python3 local/research/E40/e40_boot.py --label e40a --wall 300 --snap 30 \
      --script "..." --src-from 1000 --src-to 1400

Env added over E33's base: PS2X_MPG_SRC_TRACE=<run>/mpg-src-<label>.txt
plus _FROM/_TO.
"""

import os
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "E40-run")
b.RUNNER = os.path.join(WORK, "E32-build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

import argparse

pre = argparse.ArgumentParser(add_help=False)
pre.add_argument("--src-from", type=str, default=None)
pre.add_argument("--src-to", type=str, default=None)
pre.add_argument("--mpg-from", type=str, default=None)
pre.add_argument("--mpg-to", type=str, default=None)
known, rest = pre.parse_known_args()
sys.argv = [sys.argv[0]] + rest

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]
    elif a.startswith("--label="):
        label = a.split("=", 1)[1]

src_file = os.path.join(b.RUN, f"mpg-src-{label}.txt") if label else None
mpg_file = os.path.join(b.RUN, f"vif-mpg-{label}.txt") if label else None

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
}
if src_file:
    BASE["PS2X_MPG_SRC_TRACE"] = src_file
if known.src_from is not None:
    BASE["PS2X_MPG_SRC_TRACE_FROM"] = known.src_from
if known.src_to is not None:
    BASE["PS2X_MPG_SRC_TRACE_TO"] = known.src_to
if mpg_file and known.mpg_from is not None:
    BASE["PS2X_VIF_MPG_LOG"] = mpg_file
if known.mpg_from is not None:
    BASE["PS2X_VIF_MPG_LOG_FROM"] = known.mpg_from
if known.mpg_to is not None:
    BASE["PS2X_VIF_MPG_LOG_TO"] = known.mpg_to
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.exit(b.main())
