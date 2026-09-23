#!/usr/bin/env python3
"""G44 boot wrapper: E32 recipe + parallel shadow env, internal paths.

Usage:
  python3 local/research/G44/g44_boot.py --label g44s1 --wall 150 \
      --script "25000:start:5000,45000:cross:5000" --sfrom 800 --sto 1200
"""
import os
import sys

REPO = os.path.expanduser("~/dev/ssx3")
sys.path.insert(0, os.path.join(REPO, "local/research/E31"))
sys.argv[0] = os.path.join(REPO, "local/research/E31/e31_boot.py")

import argparse

import e31_boot as b

WORK = os.path.expanduser("~/dev/ssx3-work")
b.SPIKE = WORK
b.RUN = os.path.join(WORK, "G44", "run")
b.RUNNER = os.path.join(WORK, "G44", "build", "ps2xRuntime", "ps2EntryRunner")
b.CDDIR = os.path.join(WORK, "E32-inputs", "cd", "SLUS_207.72")
b.ISO = os.path.join(WORK, "E32-inputs", "SSX 3 (USA).iso")

ap = argparse.ArgumentParser()
ap.add_argument("--sfrom", default="0")
ap.add_argument("--sto", default="18446744073709551615")
known, rest = ap.parse_known_args()
sys.argv = [sys.argv[0]] + rest

BASE = {
    "PS2X_CD_IMAGE": b.ISO,
    "PS2X_DIAG_PERIOD_MS": "5000",
    "PS2X_DIAG_PARK": "1",
    "PS2X_DIAG_REPORT_ALL": "1",
    "COPYFILE_DISABLE": "1",
}
if "--script" in sys.argv or any(a.startswith("--script=") for a in sys.argv):
    BASE["PS2X_SKIP_MOVIE"] = "1"
BASE["PS2X_GS_SHADOW"] = "parallel"
# MoltenVK loader for Granite's dlopen (no rpath on libvulkan.1.dylib).
BASE["GRANITE_VULKAN_LIBRARY"] = "/opt/homebrew/lib/libvulkan.1.dylib"
BASE["PS2X_GS_SHADOW_FROM"] = known.sfrom
BASE["PS2X_GS_SHADOW_TO"] = known.sto
b.BASE_ENV = BASE

label = ""
for i, a in enumerate(sys.argv):
    if a == "--label" and i + 1 < len(sys.argv):
        label = sys.argv[i + 1]
BASE["PS2X_GS_SHADOW_DIR"] = os.path.join(b.RUN, "shadow-%s" % label)

os.makedirs(b.RUN, exist_ok=True)
if "--no-stim" not in sys.argv:
    sys.argv.append("--no-stim")

sys.exit(b.main())
