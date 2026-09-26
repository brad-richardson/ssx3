#!/usr/bin/env python3
"""GB8 Q2: compare [det-hash:v1] lines between two det runs (E57 check.py hash part).

Usage: gb8_hashdiff.py --base RUN_DIR --cand RUN_DIR [--min-tick 2400]
"""
import argparse
import re
import sys
from pathlib import Path

# Unanchored, and stops at the next '[': the runtime's stderr writes can interleave (a [frame:dump]
# line without its newline before a det-hash line, SS1/MD1), which otherwise reads as a missing tick.
HASH_LINE = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b[^\n\[]*')


def hash_lines(run):
    data = (Path(run) / 'boot.log').read_bytes()
    return {int(m.group(1)): m.group(0) for m in HASH_LINE.finditer(data)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--cand', required=True)
    ap.add_argument('--min-tick', type=int, default=2400)
    args = ap.parse_args()
    hb, hc = hash_lines(args.base), hash_lines(args.cand)
    want = range(1, args.min_tick + 1)
    missing_b = [t for t in want if t not in hb]
    missing_c = [t for t in want if t not in hc]
    first_diff = next((t for t in want if t in hb and t in hc and hb[t] != hc[t]), None)
    good = not missing_b and not missing_c and first_diff is None
    print('hash %s  ticks 1..%d: base=%s lines=%d cand=%s lines=%d missing=%d/%d first_diff=%s'
          % ('IDENTICAL' if good else 'DIFFER', args.min_tick, args.base, len(hb),
             args.cand, len(hc), len(missing_b), len(missing_c), first_diff))
    if missing_b[:5] or missing_c[:5]:
        print('  missing base[:5]=%s cand[:5]=%s' % (missing_b[:5], missing_c[:5]))
    if first_diff is not None:
        print('  base: %s' % hb[first_diff].decode(errors='replace'))
        print('  cand: %s' % hc[first_diff].decode(errors='replace'))
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
