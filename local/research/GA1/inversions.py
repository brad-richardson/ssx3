#!/usr/bin/env python3
"""GA1: count GIF arbiter drain-sort inversions from a PS2X_PK_ORDER log.

An inversion is a pair of packets in the SAME drain where the packet
submitted later is processed earlier (processed order != submit order).
The drain sort is stable within equal priority, so every inversion is
necessarily cross-path; the script verifies that.

Usage: inversions.py <pk-order.txt> [--tick N] [--first K]
  --tick N   dump every packet at processTick N in submit and process order
  --first K  list the first K inverted pairs (default 10)
"""
import argparse
import sys
from collections import defaultdict


def parse(path):
    pkts = []
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            d = {}
            for tok in line.split():
                k, _, v = tok.partition('=')
                d[k] = int(v)
            for k in ('drain', 'submitTick', 'processTick', 'submitIdx',
                      'processIdx', 'path', 'bytes', 'img', 'dhl'):
                if k not in d:
                    raise SystemExit(f'line {ln}: missing {k}')
            pkts.append(d)
    return pkts


def invert_pairs(drain_pkts):
    """Pairs (early, late) in processed order with early.submitIdx > late.submitIdx."""
    out = []
    n = len(drain_pkts)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = drain_pkts[i], drain_pkts[j]
            if a['submitIdx'] > b['submitIdx']:
                out.append((a, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log')
    ap.add_argument('--tick', type=int, default=None)
    ap.add_argument('--first', type=int, default=10)
    args = ap.parse_args()

    pkts = parse(args.log)
    if not pkts:
        raise SystemExit('empty log')

    # Sanity: file order is process order; processIdx consecutive; submitIdx unique.
    proc = [p['processIdx'] for p in pkts]
    assert proc == list(range(len(pkts))), 'processIdx not consecutive from 0'
    subs = [p['submitIdx'] for p in pkts]
    assert len(set(subs)) == len(subs), 'duplicate submitIdx'
    assert subs == sorted(subs) or True
    # submitIdx need not be consecutive (packets submitted but never drained
    # at SIGTERM are absent), but must be increasing in submit order; every
    # packet's submitIdx is unique, which is all the pair test needs.

    drains = defaultdict(list)
    for p in pkts:
        drains[p['drain']].append(p)
    for d in drains.values():
        d.sort(key=lambda p: p['processIdx'])

    per_vsync = defaultdict(lambda: [0, 0, 0, 0])  # tick -> [packets, drains, pairs, aff_drains]
    all_pairs = []  # (processTick, drain, early, late)
    for did in sorted(drains):
        dps = drains[did]
        ptick = dps[0]['processTick']
        assert all(p['processTick'] == ptick for p in dps), f'drain {did} spans ticks'
        row = per_vsync[ptick]
        row[0] += len(dps)
        row[1] += 1
        pairs = invert_pairs(dps)
        if pairs:
            row[2] += len(pairs)
            row[3] += 1
            for a, b in pairs:
                all_pairs.append((ptick, did, a, b))

    n_multi = sum(1 for d in drains.values() if len(d) > 1)
    n_cross = sum(1 for _, _, a, b in all_pairs if a['path'] != b['path'])
    print(f'packets={len(pkts)} drains={len(drains)} multi={n_multi} '
          f'inverted_pairs={len(all_pairs)} aff_drains={sum(1 for d in drains.values() if invert_pairs(d))} '
          f'aff_vsyncs={sum(1 for r in per_vsync.values() if r[2])} '
          f'cross_path_pairs={n_cross}')
    print(f'vsync_span={min(per_vsync)}..{max(per_vsync)} submitIdx_span={min(subs)}..{max(subs)}')

    print('\nper-vsync (only vsyncs with >=1 inversion): tick packets drains pairs aff_drains')
    for t in sorted(per_vsync):
        p, d, ip, ad = per_vsync[t]
        if ip:
            print(f'{t} {p} {d} {ip} {ad}')

    print(f'\nfirst {args.first} inverted pairs (boot order):')
    print('each row: later-submitted A processed BEFORE earlier-submitted B (sA>sB, qA<qB); '
          'p3img_after_p12=1 iff B is PATH3-IMAGE and A is PATH1/2')
    for ptick, did, a, b in all_pairs[:args.first]:
        flag = 1 if (b['path'] == 3 and b['img'] == 1 and a['path'] in (1, 2)) else 0
        print(f"{ptick} d{did} stA{a['submitTick']}/stB{b['submitTick']} "
              f"A=p{a['path']}({a['bytes']}B,img{a['img']},dhl{a['dhl']},s{a['submitIdx']},q{a['processIdx']}) "
              f"BEFORE B=p{b['path']}({b['bytes']}B,img{b['img']},dhl{b['dhl']},s{b['submitIdx']},q{b['processIdx']}) "
              f"p3img_after_p12={flag}")

    if args.tick is not None:
        sel = [p for p in pkts if p['processTick'] == args.tick]
        print(f'\n--- processTick {args.tick}: {len(sel)} packets, '
              f'{len(set(p["drain"] for p in sel))} drains ---')
        print('process order: qIdx sIdx path bytes img dhl drain submitTick')
        for p in sorted(sel, key=lambda p: p['processIdx']):
            print(f"  q{p['processIdx']} s{p['submitIdx']} p{p['path']} {p['bytes']}B "
                  f"img{p['img']} dhl{p['dhl']} d{p['drain']} st{p['submitTick']}")


if __name__ == '__main__':
    sys.exit(main())
