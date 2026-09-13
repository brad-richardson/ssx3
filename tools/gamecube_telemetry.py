#!/usr/bin/env python3
"""Read-only GXBE69 rider observations through Dolphin's MemoryWatcher.

Run before launching an isolated native --pipe-controller profile. Pointer
chains stop at unloaded objects in the runtime; no guest memory is written.
The addresses are specific to the pinned GXBE69 executable.
"""
import argparse
import json
import math
from pathlib import Path
import socket
import struct
import time

ROOT = Path(__file__).resolve().parents[1]
# GXBE69 game singleton -> race -> rider manager -> first rider.
RIDER = '803da1f8 74 c 28'
FIELDS = {RIDER: 'rider', **{f'{RIDER} {offset:x}': name for offset, name in
          [(240, 'x'), (244, 'y'), (248, 'z'), (1016, 'surface'), (684, 'terrain_flags')]},
          f'{RIDER} 718 d30': 'state', f'{RIDER} 718 2d8': 'reset_path_requested'}


def initial_values():
    # MemoryWatcher starts each watched word at zero and transmits only changes.
    # A normal snow surface (zero) may therefore never appear in a packet.
    return {name: 0 for name in FIELDS.values()}


def decode_messages(data):
    lines = data.rstrip(b'\0').decode('ascii').splitlines()
    if len(lines) % 2:
        raise ValueError('Incomplete MemoryWatcher message')
    result = {}
    for chain, value in zip(lines[::2], lines[1::2]):
        if chain not in FIELDS:
            raise ValueError(f'Unexpected memory chain: {chain}')
        word = int(value, 16)
        if not 0 <= word <= 0xffffffff:
            raise ValueError('Memory word outside uint32')
        name = FIELDS[chain]
        if name in ('x','y','z'):
            value = struct.unpack('>f', struct.pack('>I', word))[0]
        elif name == 'terrain_flags':
            value = word >> 16
        elif name == 'reset_path_requested':
            value = word >> 24
        else:
            value = word
        result[name] = value
    return result


def valid_rider(values):
    return (0x80000000 <= values.get('rider', 0) < 0x81800000 and
            all(k in values and math.isfinite(values[k]) and abs(values[k]) < 1e7 for k in ('x','y','z')) and
            0 <= values.get('surface', 0xffffffff) <= 18 and
            0 <= values.get('state', 0) < 64)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--seconds', type=float, default=360)
    args = ap.parse_args()
    if Path(args.profile).name != args.profile or args.profile in ('.','..'):
        ap.error('Use a single isolated profile name')
    if not math.isfinite(args.seconds) or not 0 < args.seconds <= 3600:
        ap.error('Seconds must be in (0,3600]')
    folder = ROOT/'local/native/profiles'/args.profile/'MemoryWatcher'
    path = folder/'MemoryWatcher'
    if len(str(path).encode()) >= 104:
        ap.error('Profile socket path too long; use a shorter profile name')
    folder.mkdir(parents=True, exist_ok=True)
    locations = folder/'Locations.txt'
    contents = '\n'.join(FIELDS)+'\n'
    if locations.exists() and locations.read_text() != contents:
        ap.error('Preserving existing memory watch configuration; use a fresh profile')
    if path.exists():
        ap.error('A watcher socket already exists; use a fresh profile')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as log, socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
        sock.bind(str(path))
        try:
            sock.settimeout(.5)
            locations.write_text(contents)
            start = time.monotonic(); values = initial_values(); last_emit = -1
            while time.monotonic()-start < args.seconds:
                try:
                    data = sock.recv(16384)
                except socket.timeout:
                    continue
                changes = decode_messages(data)
                transition = any(k in changes and changes[k] != values.get(k)
                                 for k in ('state', 'surface', 'rider', 'terrain_flags', 'reset_path_requested'))
                values.update(changes)
                elapsed = time.monotonic()-start
                if valid_rider(values) and (transition or elapsed-last_emit >= .1):
                    log.write(json.dumps(dict(t=elapsed, wall_time=time.time(), **values))+'\n')
                    log.flush(); last_emit = elapsed
        finally:
            path.unlink(missing_ok=True)
    print(args.output)


if __name__ == '__main__':
    main()
