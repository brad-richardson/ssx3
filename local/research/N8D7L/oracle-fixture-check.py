#!/usr/bin/env python3
"""N8D7L synthetic fixture + static source checks (Part 1, no build).

Expected values are HARDCODED literals from N8D7K REPORT §3. This script
never calls the oracle address algorithm to derive expected values: the
8 control addresses, the fixture words, and the expected tile counts are
all literals. Tile-index arithmetic ((py//16)*32 + px//16) and the
max(R,G,B)>=32 rule are the shared N8D7F census definition, not the
oracle under test.

Checks:
  S1  backend includes the fork literal-table header
  S2  backend calls GSPSMCT32::addrPSMCT32
  S3  backend has zero swizzle_PS2 references (independence)
  S4  all 8 N8D7K literal offsets appear verbatim in the backend
  S5  PS2X_N8D7L_ORACLE gate + OTHER branches + oracle_input_equal present
  S6  the 8 literals match N8D7K REPORT.md (source of truth, read-only)
  F1  fixture census simulation from literals matches hardcoded expectation
  F2  control-only offset (63,31 odd-y) contributes to no tile
  F3  worst-case added log < 16 KiB
"""
import re
import sys

BACKEND = "/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"
N8D7K_REPORT = "/Users/brad/dev/ssx3/local/research/N8D7K/REPORT.md"

# (gx, gy, literal byte) from N8D7K REPORT §3 — literals, do not derive.
CONTROLS = [
    (0, 0, 0xE0000),
    (31, 0, 0xE0534),
    (0, 2, 0xE0040),
    (511, 446, 0x1BFFF4),
    (64, 0, 0xE2000),
    (0, 32, 0xF0000),
    (63, 31, 0xE1FFC),
    (64, 32, 0xF2000),
]

# Synthetic VRAM: literal byte -> literal word. Spans base page, column
# break (0xE2000), row break (0xF0000), page corner (0xF2000) and far
# corner (0x1BFFF4). R = low byte; threshold is max(R,G,B) >= 32.
FIXTURE_WORDS = {
    0xE0000: 0xFF282828,   # sampled px(0,0):   R=40 hit
    0xE0534: 0xFF101010,   # sampled px(31,0):  16 miss
    0xE0040: 0xFF0000C8,   # sampled px(0,1):   R=200 hit
    0x1BFFF4: 0xFF00C800,  # sampled px(511,223): G=200 hit
    0xE2000: 0xFF1F1F1F,   # sampled px(64,0):  31 miss (edge below)
    0xF0000: 0xFF202020,   # sampled px(0,16):  32 hit (edge above)
    0xF2000: 0xFF000000,   # sampled px(64,16): 0 miss
    0xE1FFC: 0xFF7F7F7F,   # CONTROL ONLY: GS(63,31) odd-y, never a census pixel
}

# Literal (byte -> (px, py, tile)) selection mapping for dbx=dby=phase=0,
# stride=2: px=x, py=y//2, tile=(py//16)*32 + px//16. Hardcoded per pixel.
FIXTURE_PIXELS = {
    0xE0000: (0, 0, 0),
    0xE0534: (31, 0, 1),
    0xE0040: (0, 1, 0),
    0x1BFFF4: (511, 223, 447),
    0xE2000: (64, 0, 4),
    0xF0000: (0, 16, 32),
    0xF2000: (64, 16, 36),
}

# Hardcoded expected census: tile -> hit count (all other 441 tiles = 0).
EXPECTED_TILES = {0: 2, 1: 0, 4: 0, 32: 1, 36: 0, 447: 1}
EXPECTED_OCCUPIED = 4
EXPECTED_ACTIVE = 0  # no tile reaches 32 hits in this sparse fixture

failures = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        failures.append(name)


def main():
    src = open(BACKEND).read()
    k7 = open(N8D7K_REPORT).read()

    check("S1 header-include", '#include "runtime/gs/ps2_gs_psmct32.h"' in src)
    check("S2 oracle-call", "GSPSMCT32::addrPSMCT32" in src)
    check("S3 no-swizzle", "swizzle_PS2" not in src)
    lit_ok = True
    for gx, gy, byte in CONTROLS:
        pat = "0x%X" % byte
        if pat.lower() not in src.lower():
            lit_ok = False
            print("   missing literal", pat)
    check("S4 eight-literals-in-source", lit_ok, "(8 N8D7K offsets)")
    check("S5a env-gate", "PS2X_N8D7L_ORACLE" in src and "if (oracleRequested)" in src)
    check("S5b other-branches",
          "[n8d7l] OTHER metadata" in src and "[n8d7l] OTHER control-selfcheck" in src
          and "[n8d7l] OTHER address" in src)
    check("S5c comparison-log", "[n8d7l] oracle_input_equal=" in src)
    check("S5d mask-and-bounds",
          "kOracleVramMask" in src and "byte + 4u > kOracleVramBytes" in src)
    k_ok = all(("0x%X" % b).lower() in k7.lower() for _, _, b in CONTROLS)
    check("S6 literals-match-N8D7K", k_ok)

    # F1: simulate the census from literals only.
    tiles = [0] * 448
    for byte, word in FIXTURE_WORDS.items():
        if byte not in FIXTURE_PIXELS:
            continue  # control-only entry: no tile by construction
        px, py, tile = FIXTURE_PIXELS[byte]
        # shared census definition (same as N8D7F), not the oracle algorithm
        assert tile == (py // 16) * 32 + px // 16, "fixture mapping typo"
        r, g, b = word & 0xFF, (word >> 8) & 0xFF, (word >> 16) & 0xFF
        tiles[tile] += max(r, g, b) >= 32
    exp = [0] * 448
    for t, n in EXPECTED_TILES.items():
        exp[t] = n
    check("F1 fixture-tiles", tiles == exp,
          "occupied=%d active=%d" % (sum(tiles), sum(1 for t in tiles if t >= 32)))
    check("F1b occupied-active",
          sum(tiles) == EXPECTED_OCCUPIED
          and sum(1 for t in tiles if t >= 32) == EXPECTED_ACTIVE)
    check("F2 control-only-excluded",
          0xE1FFC not in FIXTURE_PIXELS and tiles[3] == 0,
          "(63,31) odd-y: in controls, in no tile)")

    # F3: worst-case added log size.
    counts_line = len("[n8d7f] oracle_tile_counts=") + 448 * 4  # each <= "256,"
    tiles_line = 120
    meta_line = 160
    controls_line = len("[n8d7l] oracle_controls=") + 8 * 20
    equal_line = 60
    total = counts_line + tiles_line + meta_line + controls_line + equal_line
    check("F3 log-cap", total < 16 * 1024, "(~%d B worst case)" % total)

    print("RESULT", "FAIL" if failures else "PASS", "%d failures" % len(failures))
    return 1 if failures else 0


sys.exit(main())
