#!/usr/bin/env python3
"""SS1: gb8_hashdiff.py with a --from tick (a loaded run starts after the save tick).

Usage: ss1_hashdiff.py --base RUN_DIR --cand RUN_DIR --from 2001 --to 2600
"""
import argparse
import re
import sys
from pathlib import Path

# Not anchored: another thread's line can precede it without a newline.
HASH_LINE = re.compile(rb'\[det-hash:v1\] tick=(\d+)\b[^\n]*')
FIELD = re.compile(rb'(\w+)=([0-9a-fx]+)')


def hash_lines(run):
    data = (Path(run) / 'boot.log').read_bytes()
    return {int(m.group(1)): m.group(0) for m in HASH_LINE.finditer(data)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--cand', required=True)
    ap.add_argument('--from', dest='lo', type=int, required=True)
    ap.add_argument('--to', dest='hi', type=int, required=True)
    args = ap.parse_args()
    hb, hc = hash_lines(args.base), hash_lines(args.cand)
    want = range(args.lo, args.hi + 1)
    missing_b = [t for t in want if t not in hb]
    missing_c = [t for t in want if t not in hc]
    first_diff = next((t for t in want if t in hb and t in hc and hb[t] != hc[t]), None)
    good = not missing_b and not missing_c and first_diff is None
    print('hash %s  ticks %d..%d: base=%s lines=%d cand=%s lines=%d missing=%d/%d first_diff=%s'
          % ('IDENTICAL' if good else 'DIFFER', args.lo, args.hi, args.base, len(hb),
             args.cand, len(hc), len(missing_b), len(missing_c), first_diff))
    if missing_b[:5] or missing_c[:5]:
        print('  missing base[:5]=%s cand[:5]=%s' % (missing_b[:5], missing_c[:5]))
    if first_diff is not None:
        print('  base: %s' % hb[first_diff].decode(errors='replace'))
        print('  cand: %s' % hc[first_diff].decode(errors='replace'))
        fb = dict(FIELD.findall(hb[first_diff]))
        fc = dict(FIELD.findall(hc[first_diff]))
        print('  fields differing: %s' % [k.decode() for k in fb if fb.get(k) != fc.get(k)])
    return 0 if good else 1


if __name__ == '__main__':
    sys.exit(main())
