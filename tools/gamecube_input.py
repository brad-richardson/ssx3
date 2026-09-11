#!/usr/bin/env python3
"""Send a bounded input to an isolated native_gamecube.py --pipe-controller run."""
import argparse
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
BUTTONS = ("A", "B", "X", "Y", "Z", "START", "L", "R", "D_UP", "D_DOWN", "D_LEFT", "D_RIGHT")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--hold", type=float, default=0.25)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("tap").add_argument("buttons", nargs="+", choices=BUTTONS)
    stick = sub.add_parser("stick")
    stick.add_argument("x", type=float)
    stick.add_argument("y", type=float)
    args = parser.parse_args()
    if Path(args.profile).name != args.profile or args.profile in (".", ".."):
        parser.error("--profile must be a single directory name")
    if not 0 < args.hold <= 30:
        parser.error("--hold must be in (0, 30]")
    if args.action == "stick" and not (0 <= args.x <= 1 and 0 <= args.y <= 1):
        parser.error("Stick coordinates must be in [0, 1]; 0.5, 0.5 is centered")
    profile = ROOT / "local/native/profiles" / args.profile
    if "Device = Pipe/0/ssx3" not in (profile / "Config/GCPadNew.ini").read_text():
        parser.error("Profile is not configured for our test pipe")
    try:
        fd = os.open(profile / "Pipes/ssx3", os.O_WRONLY | os.O_NONBLOCK)
    except OSError as error:
        parser.exit(1, f"Test controller unavailable: {error}\n")

    def send(command):
        os.write(fd, (command + "\n").encode("ascii"))

    try:
        if args.action == "tap":
            for button in args.buttons:
                try:
                    send(f"PRESS {button}")
                    time.sleep(args.hold)
                finally:
                    send(f"RELEASE {button}")
                time.sleep(0.3)
        else:
            try:
                send(f"SET MAIN {args.x} {args.y}")
                time.sleep(args.hold)
            finally:
                send("SET MAIN 0.5 0.5")
    finally:
        os.close(fd)
    with (profile / "test-input.jsonl").open("a") as log:
        log.write(json.dumps({"time": time.time(), **vars(args)}) + "\n")


if __name__ == "__main__":
    main()
