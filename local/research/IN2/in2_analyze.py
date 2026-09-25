#!/usr/bin/env python3
"""IN2: grade injected taps against guest pad reads.

Pairs host press/release edges into taps; a tap fully between two
consecutive guest reads is QUALIFYING (pre-latch: never seen; latched:
seen exactly once - first read after shows it, second shows up).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

BIT = {'select': 0x0001, 'l3': 0x0002, 'r3': 0x0004, 'start': 0x0008,
       'up': 0x0010, 'right': 0x0020, 'down': 0x0040, 'left': 0x0080,
       'l2': 0x0100, 'r2': 0x0200, 'l1': 0x0400, 'r1': 0x0800,
       'triangle': 0x1000, 'circle': 0x2000, 'cross': 0x4000, 'square': 0x8000}

HOST_RE = re.compile(r'\[padread\] host (.*?)wall=(\d+)ms')
READ_RE = re.compile(r'\[padread\] read tick=(\d+) port=(\d) buttons=0x([0-9a-f]{4}) wall=(\d+)ms')
RATE_RE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)/s \(([\d.]+)x')


def mask_of(token):
    token = token.strip()
    if token in BIT:
        return BIT[token]
    if token.startswith('0x'):
        return int(token, 16)
    raise SystemExit('bad edge token %r' % token)


def main():
    lane = Path(sys.argv[1])
    lines = (lane / 'boot.log').read_text(errors='replace').splitlines()
    edges, reads, rates = [], [], []
    for ln in lines:
        m = HOST_RE.search(ln)
        if m:
            wall = int(m.group(2))
            for tok in m.group(1).split():
                if tok[0] == '+':
                    edges.append((wall, mask_of(tok[1:]), +1))
                elif tok[0] == '-':
                    edges.append((wall, mask_of(tok[1:]), -1))
            continue
        m = READ_RE.search(ln)
        if m:
            reads.append((int(m.group(4)), int(m.group(1)), int(m.group(2)),
                          int(m.group(3), 16)))
            continue
        m = RATE_RE.search(ln)
        if m:
            rates.append((int(m.group(1)), float(m.group(3))))
    reads.sort()
    edges.sort()
    print('run=%s reads=%d host_edges=%d ports=%s' %
          (lane.name, len(reads), len(edges), sorted({r[2] for r in reads})))

    # Guest read cadence: reads per tick (port 0), gap sizes.
    by_tick = Counter((r[1], r[2]) for r in reads)
    multi = {k: c for k, c in by_tick.items() if c > 1}
    p0 = [r for r in reads if r[2] == 0]
    gaps = [b[0] - a[0] for a, b in zip(p0, p0[1:]) if b[0] > a[0]]
    gaps.sort()
    q = lambda f: gaps[min(int(len(gaps) * f), len(gaps) - 1)] if gaps else None
    print('port0_reads=%d multi_read_ticks=%d read_gap_ms min=%s p50=%s p90=%s max=%s' %
          (len(p0), len(multi), q(0), q(0.5), q(0.9), q(1.0)))
    if rates:
        print('guest_rate first=%sx@tick%d last=%sx@tick%d' %
              (rates[0][1], rates[0][0], rates[-1][1], rates[-1][0]))

    # Tap windows come from the injection schedule (same wallMs epoch as
    # the read log, so exact); host edge lines, when present (latch path),
    # cross-check that the producer sampled each tap. The off path never
    # calls publish, so it has no edge lines by design.
    sched = [(ms, BIT['r3'], 40) for ms in range(30000, 300000, 3000)] + \
        [(282000, BIT['cross'], 60), (292000, BIT['cross'], 60), (302000, BIT['cross'], 60)]
    name = {v: k for k, v in BIT.items()}
    taps = [{'bit': b, 'press': p, 'release': p + d} for p, b, d in sched]
    agree = disagree = 0
    for t in taps:
        pe = [e for e in edges if e[1] == t['bit'] and e[2] == +1 and
              t['press'] <= e[0] <= t['press'] + 50]
        re_ = [e for e in edges if e[1] == t['bit'] and e[2] == -1 and
               t['release'] <= e[0] <= t['release'] + 50]
        t['edge_press'] = pe[0][0] if pe else None
        t['edge_release'] = re_[0][0] if re_ else None
        if pe and re_:
            agree += 1
        elif edges:
            disagree += 1
    if edges:
        print('producer_edge_agreement=%d disagree=%d (50ms window)' % (agree, disagree))

    # Grade each tap against port-0 reads.
    walls = [r[0] for r in p0]
    for t in taps:
        t['name'] = name.get(t['bit'], hex(t['bit']))
        inside = [r for r in p0 if t['press'] <= r[0] <= t['release']]
        before = [r for r in p0 if r[0] < t['press']]
        after = [r for r in p0 if r[0] > t['release']]
        t['tick'] = after[0][1] if after else (before[-1][1] if before else None)
        t['gap_ms'] = (after[0][0] - before[-1][0]) if before and after else None
        if inside:
            seen = any((r[3] & t['bit']) == 0 for r in inside)
            t['verdict'] = 'SPANNING-seen' if seen else 'SPANNING-MISSED?'
            continue
        if not after:
            t['verdict'] = 'NO-READ-AFTER'
            continue
        seen1 = (after[0][3] & t['bit']) == 0
        seen2 = len(after) > 1 and (after[1][3] & t['bit']) == 0
        was_up = (before[-1][3] & t['bit']) != 0 if before else True
        t['read1_wall'] = after[0][0]
        t['read1_tick'] = after[0][1]
        if not was_up:
            t['verdict'] = 'CONTAMINATED(held-before)'
        elif seen1 and not seen2:
            t['verdict'] = 'SEEN-ONCE'
        elif seen1 and seen2:
            t['verdict'] = 'SEEN-MULTI?'
        elif not seen1:
            t['verdict'] = 'DROPPED'
        else:
            t['verdict'] = 'SEEN-ONCE(eof)'

    qual = [t for t in taps if t['verdict'] in ('SEEN-ONCE', 'DROPPED', 'SEEN-MULTI?') or
            t['verdict'].startswith('SEEN-ONCE(')]
    print('taps=%d qualifying=%d verdicts=%s' %
          (len(taps), len(qual), dict(Counter(t['verdict'] for t in taps))))
    for t in taps:
        if t['verdict'] == 'SEEN-ONCE' and t['name'] == 'r3' and len(qual) > 12 and \
                t is not next(iter(qual), None):
            continue  # trim the long middle; full table in taps.json
        print('tap %-6s press=%6d rel=%6d tick=%5s gap=%4sms -> %s' %
              (t['name'], t['press'], t['release'] or -1, t.get('tick'),
               t.get('gap_ms'), t['verdict']))
    (lane / 'taps.json').write_text(json.dumps(taps, indent=1) + '\n')
    print('wrote %s' % (lane / 'taps.json'))


if __name__ == '__main__':
    main()
