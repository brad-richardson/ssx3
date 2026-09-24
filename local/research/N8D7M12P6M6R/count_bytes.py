#!/usr/bin/env python3
"""Passthrough stdin->stdout counting bytes; prints STREAM_BYTES=<n> to stderr."""
import sys

n = 0
stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
while True:
    chunk = stdin.read(65536)
    if not chunk:
        break
    n += len(chunk)
    stdout.write(chunk)
stdout.flush()
print(f"STREAM_BYTES={n}", file=sys.stderr)
