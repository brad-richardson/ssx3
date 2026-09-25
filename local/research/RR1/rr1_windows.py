#!/usr/bin/env python3
"""RR1: per tick, PATH3 GS packets before the first PATH1 packet (drained leftovers)
vs after it (released in MSKPATH3 windows), plus PATH1 packet count. Needs a capture
taken with PS2X_GFX_STATS on (path labels). Usage: rr1_windows.py <gs.cap> <from> <to>"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
import rr1_cap as cap


def main():
    path, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rows = {}
    for kind, tk, body in cap.iter_records(path, a, b):
        if kind != 1:
            continue
        r = rows.setdefault(tk, {'lead3': 0, 'win3': 0, 'p1': 0, 'p2': 0, 'seen1': False})
        pth = body[0]
        if pth == 1:
            r['p1'] += 1; r['seen1'] = True
        elif pth == 2:
            r['p2'] += 1
        elif pth == 3:
            r['win3' if r['seen1'] else 'lead3'] += 1
    print('tick lead3 win3 p1 p2')
    for t in sorted(rows):
        r = rows[t]
        print(t, r['lead3'], r['win3'], r['p1'], r['p2'])

if __name__ == '__main__':
    main()
