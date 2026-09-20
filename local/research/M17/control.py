#!/usr/bin/env python3
"""M17 positive controls: estimators must recover synthetic shifts."""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from m17 import (load_dump, split_planes, shift_plane, shift_frac, rint_u8,
                 model_g, model_b)

y0, u0, v0p = split_planes(np.frombuffer(
    load_dump(Path("/Volumes/Extreme SSD/m16/m16-v0-s0000.bin")), np.uint8))

# G: +0.5 x half-shift
fh = rint_u8(shift_frac(y0.astype(np.float64), 0.5, 0.0))
g = model_g(y0, u0, v0p, fh, u0, v0p)
print(f"G half control: recovered={g['shift']} want=(0.5, 0.0) "
      f"sad={g['sad']:.0f} sad00={g['sad00']:.0f} nmoved={g['nmoved']}")

# G: +1 x integer shift
fi = shift_plane(y0, 1, 0)
g2 = model_g(y0, u0, v0p, fi, u0, v0p)
print(f"G int control: recovered={g2['shift']} want=(1.0, 0.0) "
      f"sad={g2['sad']:.0f} sad00={g2['sad00']:.0f} nmoved={g2['nmoved']}")

# B: +2 x integer shift
f2 = shift_plane(y0, 2, 0)
b = model_b(y0, u0, v0p, f2, u0, v0p)
c = Counter(b["vecs"])
print(f"B int control: top vecs={c.most_common(3)} want=(2.0, 0.0) majority, "
      f"moved_blocks={b['moved_blocks']} sad00={b['sad00']:.0f} "
      f"sadbest={b['sadbest']:.0f}")

# B: (+0.5,+0.5) half shift
fhh = rint_u8(shift_frac(y0.astype(np.float64), 0.5, 0.5))
b2 = model_b(y0, u0, v0p, fhh, u0, v0p)
c2 = Counter(b2["vecs"])
print(f"B half control: top vecs={c2.most_common(3)} want=(0.5, 0.5) majority, "
      f"moved_blocks={b2['moved_blocks']} sad00={b2['sad00']:.0f} "
      f"sadbest={b2['sadbest']:.0f}")
