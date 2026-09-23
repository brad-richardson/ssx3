#!/usr/bin/env python3
"""E33 boot wrapper: vsync-clock pad script + per-vsync gfx stats.

Usage:
  python3 local/research/E33/e33_boot.py --label e33a --wall 300 \
      --script "..." --stats-from 1300 --stats-to 1400
  python3 local/research/E33/e33_boot.py --label e33b --wall 700 \
      --script "..." --stats-from 7200 --stats-to 7800

Env added over E32's base: PS2X_PAD_SCRIPT_CLOCK=vsync,
PS2X_GFX_STATS=<run>/gfx-stats-<label>.txt plus the FROM/TO window.
Stats files are text; compress if > 50 MB (handled by caller).
"""

import os
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "E33-run")
b.RUNNER = os.path.join(WORK, "E32-build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

import argparse

pre = argparse.ArgumentParser(add_help=False)
pre.add_argument("--stats-from", type=str, default=None)
pre.add_argument("--stats-to", type=str, default=None)
known, rest = pre.parse_known_args()
sys.argv = [sys.argv[0]] + rest

label = None
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]
    elif a.startswith("--label="):
        label = a.split("=", 1)[1]

stats_file = os.path.join(b.RUN, f"gfx-stats-{label}.txt") if label else None

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
    "PS2X_PAD_SCRIPT_CLOCK": "vsync",
}
if stats_file:
    BASE["PS2X_GFX_STATS"] = stats_file
if known.stats_from is not None:
    BASE["PS2X_GFX_STATS_FROM"] = known.stats_from
if known.stats_to is not None:
    BASE["PS2X_GFX_STATS_TO"] = known.stats_to
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
b.BASE_ENV = BASE

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.exit(b.main())
