#!/usr/bin/env python3
# G38: excise G37's +56 block (reverse of g37-shrunken-placement.diff).
# Single file write; asserts mirror prior-lane hunk.py discipline.
import sys

CLONE = "/Volumes/Extreme SSD/parallel-gs-g7"
P = CLONE + "/gs/gs_interface.cpp"
DIFF = "local/research/G37/g37-shrunken-placement.diff"

dry = "--dry" in sys.argv
src = open(P, encoding="utf-8").read()

# Derive the block from the committed diff's "+" lines (no transcription).
plus = [ln[1:] for ln in open(DIFF, encoding="utf-8")
        if ln.startswith("+") and not ln.startswith("+++")]
block = "".join(plus)
assert block.count("G37: writeback") == 3, block.count("G37: writeback")
assert block.count("\n") == 56, block.count("\n")

anchor = "\tauto result = renderer.vsync(priv_registers, info,\n"
assert src.count(anchor) == 1, ("anchor", src.count(anchor))
assert src.count(block) == 1, ("block", src.count(block))
# Block must sit immediately pre-anchor.
assert src.count(block + anchor) == 1, "block not immediately pre-anchor"
assert src.count("G36: writeback") == 0
assert src.count("G35: writeback") == 0

if dry:
    print(f"DRY-OK: G37x1 pre-anchor, anchorx1, G31-statex{src.count('G31: state')}")
    sys.exit(0)

out = src.replace(block + anchor, anchor)
assert "g37_temp" not in out and "G37: writeback" not in out
assert out.count("G31: state") == 1 and out.count("G31: bytes") == 2
open(P, "w", encoding="utf-8").write(out)
print("APPLIED: G37 excised; G31 neighbors intact")
