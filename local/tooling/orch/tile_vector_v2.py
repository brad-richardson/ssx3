#!/usr/bin/env python3
"""N8D6C logcat vector parser, v2.

Pure copy of the released ``tile_vector(lines, kind)`` from
``local/research/N8D6C/launch.py`` with one narrow parsing change: a single
leading comma on a continuation line is stripped before the fields are
split, so a wrapped ``_tile_counts=`` payload is accepted. Everything else,
including the return schema and the 896-word cap, is unchanged. ``sha256``
is the hexdigest helper the released parser's return schema uses.
"""

import hashlib
import re
import struct


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def tile_vector(lines, kind):
    marker = f'[n8d5b] {kind}_tile_counts='
    prefix = re.compile(r'^.*?\bI ps2x\s+: (.*)$')
    values = []
    collecting = False
    for line in lines:
        if marker in line:
            values = []
            collecting = True
            payload = line.split(marker, 1)[1]
        elif collecting:
            match = prefix.match(line)
            if not match or match.group(1).startswith('['):
                break
            payload = match.group(1)
            if payload.startswith(','):
                payload = payload[1:]
        else:
            continue
        fields = payload.rstrip(',').split(',')
        if any(not field.isdecimal() for field in fields):
            return None
        values.extend(map(int, fields))
        if len(values) > 896:
            return None
        if len(values) == 896:
            packed = struct.pack('<896I', *values)
            return {'words': 896, 'occupied': sum(values),
                    'active': sum(value >= 32 for value in values),
                    'sha256': sha256(packed), 'values': values}
    return None
