#!/usr/bin/env python3
"""E57 acceptance: is a VU1 candidate bit-exact against the baseline?

check.py --base RUN_DIR --cand RUN_DIR [--base-suite LOG --cand-suite LOG] [--min-tick 2400]

RUN_DIR is an e57_boot.py --mode hash run (boot.log with [det-hash:v1] lines, gs.cap).
Checks, each PASS/FAIL:
  suite    candidate suite: Failed 0 and Passed == Total >= baseline Total.
  hash     every [det-hash:v1] line with tick <= min-tick is byte-identical, both runs
           cover ticks 1..min-tick consecutively. Reports the first differing tick.
  gs       GS capture (PS2XGSC1 records): same record stream up to the capture stop;
           whole-file SHA-256 equal. Reports the first differing VBlank tick.
Exit 0 only when every check that ran passed.
"""
import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path

HASH_LINE = re.compile(rb'^\[det-hash:v1\] tick=(\d+)\b.*$', re.M)
SUITE = re.compile(r'Total Tests:\s*(\d+)\s+Passed:\s*(\d+)\s+Failed:\s*(\d+)')


def suite_counts(path):
    m = SUITE.search(Path(path).read_text(errors='replace'))
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def hash_lines(run):
    data = (Path(run) / 'boot.log').read_bytes()
    return {int(m.group(1)): m.group(0) for m in HASH_LINE.finditer(data)}


def gs_stream(run):
    """Yield (vblank_tick_before_record, record_bytes) and return file sha."""
    path = Path(run) / 'gs.cap'
    records = []
    sha = hashlib.sha256()
    with path.open('rb') as f:
        magic = f.read(8)
        sha.update(magic)
        if magic != b'PS2XGSC1':
            raise SystemExit('%s: bad magic %r' % (path, magic))
        vtick = 0
        while True:
            head = f.read(4)
            if len(head) < 4:
                break
            (size,) = struct.unpack('<I', head)
            payload = f.read(size)
            if len(payload) < size:
                records.append((vtick, None))  # truncated tail
                break
            sha.update(head)
            sha.update(payload)
            records.append((vtick, hashlib.blake2b(payload, digest_size=16).digest()))
            if size == 9 and payload[0] == 4:
                vtick = struct.unpack('<Q', payload[1:9])[0]
    return records, sha.hexdigest(), path.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--cand', required=True)
    ap.add_argument('--base-suite')
    ap.add_argument('--cand-suite')
    ap.add_argument('--min-tick', type=int, default=2400)
    args = ap.parse_args()
    ok = True

    if args.base_suite and args.cand_suite:
        b, c = suite_counts(args.base_suite), suite_counts(args.cand_suite)
        good = b is not None and c is not None and c[2] == 0 and c[1] == c[0] and c[0] >= b[0]
        print('suite  %s  base=%s cand=%s (total, passed, failed)' % ('PASS' if good else 'FAIL', b, c))
        ok &= good

    hb, hc = hash_lines(args.base), hash_lines(args.cand)
    want = range(1, args.min_tick + 1)
    missing_b = [t for t in want if t not in hb]
    missing_c = [t for t in want if t not in hc]
    first_diff = next((t for t in want if t in hb and t in hc and hb[t] != hc[t]), None)
    good = not missing_b and not missing_c and first_diff is None
    print('hash   %s  ticks 1..%d: base lines=%d cand lines=%d missing base=%d cand=%d first_diff=%s'
          % ('PASS' if good else 'FAIL', args.min_tick, len(hb), len(hc), len(missing_b),
             len(missing_c), first_diff))
    if first_diff is not None:
        print('  base: %s' % hb[first_diff].decode(errors='replace'))
        print('  cand: %s' % hc[first_diff].decode(errors='replace'))
    ok &= good

    rb, sb, zb = gs_stream(args.base)
    rc, sc, zc = gs_stream(args.cand)
    diff_at = next((i for i, (x, y) in enumerate(zip(rb, rc)) if x != y), None)
    if diff_at is None and len(rb) != len(rc):
        diff_at = min(len(rb), len(rc))
    last_vtick = rb[-1][0] if rb else 0
    good = diff_at is None and sb == sc and last_vtick >= args.min_tick - 1
    detail = 'records=%d/%d bytes=%d/%d sha=%s/%s last_vblank=%d' % (
        len(rb), len(rc), zb, zc, sb[:16], sc[:16], last_vtick)
    if diff_at is not None:
        tick = (rb[diff_at][0] if diff_at < len(rb) else rc[diff_at][0])
        detail += ' first_diff_record=%d after_vblank_tick=%d' % (diff_at, tick)
    print('gs     %s  %s' % ('PASS' if good else 'FAIL', detail))
    ok &= good

    print('RESULT %s' % ('BIT-EXACT' if ok else 'NOT BIT-EXACT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
