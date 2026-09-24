#!/usr/bin/env python3
"""Parse PS2XGSC1 replay stream: list records up to a tick; build truncated/synthetic streams."""
import struct, sys
KINDS = {1: "gif", 2: "priv", 3: "xfer", 4: "marker", 5: "k5"}

def records(path, max_tick):
    with open(path, "rb") as f:
        assert f.read(8) == b"PS2XGSC1"
        off = 8
        while True:
            hdr = f.read(4)
            if len(hdr) < 4:
                return
            (length,) = struct.unpack("<I", hdr)
            rec = f.read(length)
            kind = rec[0]
            (tick,) = struct.unpack_from("<Q", rec, 1)
            yield off, kind, tick, rec
            off += 4 + length
            if kind == 4 and tick >= max_tick:
                return

if __name__ == "__main__":
    path, tick = sys.argv[1], int(sys.argv[2])
    for off, kind, t, rec in records(path, tick):
        if t >= tick - 0 and t == tick or (kind == 4 and t >= tick - 1):
            extra = ""
            if kind == 1:
                extra = f" path={rec[9]} size={struct.unpack_from('<I', rec, 10)[0]}"
            elif kind == 2:
                o, v = struct.unpack_from("<IQ", rec, 9)
                extra = f" off=0x{o:x} val=0x{v:x}"
            elif kind == 5:
                extra = f" len={len(rec)}"
            print(f"{off} {KINDS.get(kind, kind)} tick={t}{extra}")
