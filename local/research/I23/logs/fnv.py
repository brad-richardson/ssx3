#!/usr/bin/env python3
"""FNV-1a 64 + hex slices for I23 parity comparison (host side)."""
import hashlib
import sys

path = sys.argv[1]
data = open(path, "rb").read()
h = 0xCBF29CE484222325
for b in data:
    h ^= b
    h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
print(f"file={path}")
print(f"len={len(data)}")
print(f"fnv64={h:016x}")
print(f"sha256={hashlib.sha256(data).hexdigest()}")
print(f"first64={data[:64].hex()}")
print(f"last64={data[-64:].hex()}")
