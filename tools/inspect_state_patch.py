#!/usr/bin/env python3
"""Look for a disc terrain patch in a PCSX2 save state's EE memory (read-only).

Python 3.14 is needed for PCSX2's ZIP/Zstandard states. A match proves byte
presence, not rendering, active use, or collision behavior. Absence is inconclusive:
the engine may transform or unload the data.
"""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack, resource_records


def matches(memory, pattern):
    found, start = [], 0
    while (offset := memory.find(pattern, start)) >= 0:
        found.append(offset)
        start = offset + 1
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--world-report", type=Path, default=Path("local/reports/ssx3-world.json"))
    parser.add_argument("--group", type=int, default=2)
    parser.add_argument("--track", type=int, default=1)
    parser.add_argument("--rid", type=int, default=76)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.world_report.read_text())
    with args.archive.open("rb") as stream:
        archive = Region(stream, 0, args.archive.stat().st_size)
        _, members = big_members(archive)
        ssb = file_region(archive, members, "data/worlds/bam.ssb")
        raw = b"".join(refpack(ssb.read(block["offset"], block["size"])[8:])[0]
                       for block in report["groups"][args.group]["blocks"])
    if hashlib.sha256(raw).hexdigest() != report["groups"][args.group]["sha256"]:
        raise ValueError("Decoded group differs from supplied world report")
    patches = [payload for entry, payload in resource_records(raw)
               if entry["kind"] == 1 and entry["track"] == args.track and entry["rid"] == args.rid]
    if len(patches) != 1 or len(patches[0]) != 432:
        raise ValueError("Expected exactly one 432-byte SSX 3 terrain patch")
    payload = patches[0]
    with zipfile.ZipFile(args.state) as state:
        info = state.getinfo("eeMemory.bin")
        if info.file_size != 32 * 1024 * 1024:
            raise ValueError("Expected retail PS2 32 MiB EE memory")
        memory = state.read(info)
    result = {
        "state": str(args.state), "state_sha256": hashlib.sha256(args.state.read_bytes()).hexdigest(),
        "archive": str(args.archive), "group": args.group, "track": args.track, "rid": args.rid,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "ee_bytes": len(memory),
        "matches": {name: matches(memory, data) for name, data in {
            "full_payload": payload, "coefficients": payload[64:320],
            "bounds_and_corners": payload[344:416]}.items()},
        "interpretation": "Byte presence only; does not establish active use, rendering, or collision.",
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
