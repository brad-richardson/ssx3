#!/usr/bin/env python3
"""Replay an iOS benchmark input sequence through a desktop test controller.

Attach only to an isolated native_gamecube.py --pipe-controller profile.
The sequence clock begins at attachment; launch shortly after runtime startup.
"""
import argparse
import json
import os
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[1]
BUTTONS = r"(?:A|B|X|Y|Z|START|L|R|D_UP|D_DOWN|D_LEFT|D_RIGHT)"


def validate_sequence(sequence):
    duration = sequence.get("duration", 0)
    if not isinstance(duration, (int, float)) or not 0 < duration <= 3600:
        raise ValueError("duration must be in (0, 3600]")
    previous = -1
    for event in sequence["events"]:
        at = event["at"]
        if not isinstance(at, (int, float)) or not previous <= at <= duration:
            raise ValueError("Event times must be ordered within the duration")
        previous = at
        for line in event["commands"].splitlines():
            if re.fullmatch(r"(?:PRESS|RELEASE) " + BUTTONS, line):
                continue
            match = re.fullmatch(r"SET (?:MAIN|C) ([\d.]+) ([\d.]+)", line)
            if not match or not all(0 <= float(v) <= 1 for v in match.groups()):
                raise ValueError(f"Invalid controller command: {line!r}")
    return sequence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--sequence", type=Path, default=ROOT / "native/ios/snow-jam-smoke.json")
    args = parser.parse_args()
    if Path(args.profile).name != args.profile or args.profile in (".", ".."):
        parser.error("Profile must be a single directory name")
    sequence = validate_sequence(json.loads(args.sequence.read_text()))
    profile = ROOT / "local/native/profiles" / args.profile
    if "Device = Pipe/0/ssx3" not in (profile / "Config/GCPadNew.ini").read_text():
        parser.error("Profile is not configured for the isolated test controller")
    deadline = time.monotonic() + 60
    while True:
        try:
            fd = os.open(profile / "Pipes/ssx3", os.O_WRONLY | os.O_NONBLOCK)
            break
        except OSError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.2)
    started = time.monotonic()
    try:
        with (profile / "replay.jsonl").open("a") as log:
            for event in sequence["events"]:
                time.sleep(max(0, event["at"] - (time.monotonic() - started)))
                data = event["commands"].encode("ascii")
                if os.write(fd, data) != len(data):
                    raise RuntimeError("Incomplete pipe write")
                log.write(json.dumps({"elapsed": time.monotonic()-started, "wall_time":time.time(), **event}) + "\n")
                log.flush()
    finally:
        try:
            os.write(fd, b"SET MAIN 0.5 0.5\nSET C 0.5 0.5\nRELEASE A\nRELEASE B\nRELEASE X\nRELEASE Y\nRELEASE Z\nRELEASE START\nRELEASE L\nRELEASE R\n")
        finally:
            os.close(fd)


if __name__ == "__main__":
    main()
