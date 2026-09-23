#!/usr/bin/env python3
"""AU1: list IRX import (0x41e00000) and export (0x41c00000) tables.
Import stub = jr $ra (0x03e00008) + addiu $zero,$zero,N (0x2400NNNN)."""
import struct, sys
for path in sys.argv[1:]:
    b = open(path, "rb").read()
    words = [struct.unpack_from("<I", b, i)[0] for i in range(0, len(b) - 3, 4)]
    imps, exps = [], []
    for wi, w in enumerate(words):
        if w in (0x41E00000, 0x41C00000):
            name = b[wi*4+12:wi*4+20].split(b"\0")[0].decode("latin1", "replace")
            ver = words[wi+2]
            if w == 0x41E00000:
                fns = []; j = wi + 5
                while j + 1 < len(words) and words[j] == 0x03E00008 and (words[j+1] >> 16) == 0x2400:
                    fns.append(words[j+1] & 0xFFFF); j += 2
                imps.append((name, ver, fns))
            else:
                exps.append((name, ver))
    print(f"== {path.split('/')[-1]} ({len(b)} B)")
    for n, v, f in imps:
        print(f"  import {n:8s} v{v:#06x} fns={f}")
    for n, v in exps:
        print(f"  export {n:8s} v{v:#06x}")
