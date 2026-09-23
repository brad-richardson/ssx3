#!/usr/bin/env python3
"""GB2 A/B: compare [frame:dump] tick->fnv1a series from two boot logs.

Usage:
  python3 local/research/GB2/gb2_ab.py <boot-off.log> <boot-on.log>

Parses lines like:
  [frame:dump] seq=12 tick=345 size=512x448 fbp=112/0 fallback=0 fnv1a=fd889dc5
Matches on guest vsync tick (first upload per tick wins; duplicates from
re-uploads are dropped with a count). Prints match/mismatch table over the
tick intersection and exits 0 iff all matched non-fallback hashes agree.
"""
import re
import sys

DUMP_RE = re.compile(
    r"\[frame:dump\] seq=(\d+) tick=(\d+) size=(\d+)x(\d+) fbp=(\d+)/(\d+) fallback=(\d) fnv1a=([0-9a-f]+)"
)


def parse(path):
    series = {}
    dups = 0
    with open(path, "rb") as f:
        for raw in f:
            try:
                line = raw.decode("utf-8", "replace")
            except OSError:
                continue
            m = DUMP_RE.search(line)
            if not m:
                continue
            seq, tick, w, h, dfbp, sfbp, fb, fnv = m.groups()
            tick = int(tick)
            if tick in series:
                dups += 1
                continue
            series[tick] = (fnv, int(w), int(h), int(dfbp), int(sfbp), int(fb), int(seq))
    return series, dups


def main():
    off_log, on_log = sys.argv[1], sys.argv[2]
    off, off_dups = parse(off_log)
    on, on_dups = parse(on_log)
    common = sorted(set(off) & set(on))
    only_off = sorted(set(off) - set(on))
    only_on = sorted(set(on) - set(off))
    print(f"off: {len(off)} ticks ({min(off) if off else '-'}..{max(off) if off else '-'}) dups={off_dups}")
    print(f"on:  {len(on)} ticks ({min(on) if on else '-'}..{max(on) if on else '-'}) dups={on_dups}")
    print(f"matched ticks: {len(common)}  only-off: {len(only_off)}  only-on: {len(only_on)}")
    if only_off:
        print(f"  only-off range: {only_off[0]}..{only_off[-1]}")
    if only_on:
        print(f"  only-on range: {only_on[0]}..{only_on[-1]}")
    print()
    print("tick      off-fnv    on-fnv     size       fbp     fb  verdict")
    mism = 0
    shown = 0
    for tick in common:
        fnv_off, w0, h0, d0, s0, fb0, _ = off[tick]
        fnv_on, w1, h1, d1, s1, fb1, _ = on[tick]
        ok = (fnv_off == fnv_on and (w0, h0, d0, s0, fb0) == (w1, h1, d1, s1, fb1))
        if not ok:
            mism += 1
        if not ok or shown < 25:
            print(f"{tick:<9d} {fnv_off:>8s}   {fnv_on:>8s}   {w0}x{h0:<7d} {d0}/{s0:<6d} "
                  f"{fb0}/{fb1}  {'OK' if ok else 'MISMATCH'}")
            shown += 1
    if len(common) > shown:
        print(f"... ({len(common) - shown} further matching ticks not shown)")
    print()
    print(f"matched={len(common)} mismatches={mism}")
    return 0 if mism == 0 and len(common) >= 20 else 1


if __name__ == "__main__":
    sys.exit(main())
