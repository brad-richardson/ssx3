#!/usr/bin/env python3
"""MC1 analysis: tick-correlated [MC] sequence + mc0 before/after diff.

Log lines can concatenate (no trailing newline on some emitters), so all
patterns are scanned over the whole text with offset-based tick
correlation (last [vsync-rate] tick at or before the match).

Usage: mc1_analyze.py <run-dir>   (reads boot.log + result.json)
"""
import bisect
import json
import re
import sys
from pathlib import Path

CMD = {1: 'GetInfo', 2: 'Open', 3: 'Close', 4: 'Seek', 5: 'Read', 6: 'Write',
       10: 'Flush', 11: 'Mkdir', 12: 'Chdir', 13: 'GetDir', 14: 'SetFileInfo',
       15: 'Delete', 16: 'Format', 17: 'Unformat', 18: 'GetEntSpace',
       19: 'Rename'}
RES = {0: 'OK', -1: 'ChangedCard', -2: 'NoFormat', -4: 'NoEntry',
       -5: 'Denied', -6: 'NotEmpty', -7: 'HandleLimit'}


def main():
    lane = Path(sys.argv[1])
    text = (lane / 'boot.log').read_bytes().decode('utf-8', 'replace')
    marks = [(m.start(), int(m.group(1)))
             for m in re.finditer(r'\[vsync-rate\] tick=(\d+)\b', text)]
    offs = [o for o, _ in marks]

    def tick_at(pos):
        i = bisect.bisect_right(offs, pos) - 1
        return marks[i][1] if i >= 0 else 0

    syncs = []
    for m in re.finditer(r'\[MC\] Sync cmd=(-?\d+) result=(-?\d+)', text):
        c, r = int(m.group(1)), int(m.group(2))
        syncs.append((tick_at(m.start()), CMD.get(c, '?%d' % c),
                      RES.get(r, r)))
    print('== Sync sequence: %d commands ==' % len(syncs))
    for t, c, r in syncs:
        print('%6d  %-11s  %s' % (t, c, r))

    print('== GetDir/Chdir/GetInfo detail ==')
    for rx in (r"\[MC\] GetDir port=(\d+) '(.*?)' maxent=(\d+) -> result=(-?\d+)",
               r"\[MC\] Chdir port=(\d+) '(.*?)'.*?(?=result=(-?\d+))",
               r'\[MC\] GetInfo port=(\d+) type=(\d+) free=(\d+) format=(\d+) result=(-?\d+)'):
        for m in re.finditer(rx, text):
            print('%6d  %s' % (tick_at(m.start()), m.group(0)[:160]))

    res = json.loads((lane / 'result.json').read_text())
    before = {r['rel']: r for r in res['mc_before']}
    after = {r['rel']: r for r in res['mc_after']}
    print('== mc0 diff ==')
    for rel in sorted(set(before) | set(after)):
        b, a = before.get(rel), after.get(rel)
        if b is None:
            print('CREATED %s size=%s sha=%s' % (rel, a['size'], a['sha'][:12]))
        elif a is None:
            print('DELETED %s' % rel)
        elif b['sha'] != a['sha']:
            print('MODIFIED %s size %s->%s mtime %s->%s sha %s->%s'
                  % (rel, b['size'], a['size'], b['mtime'], a['mtime'],
                     (b['sha'] or '')[:12], (a['sha'] or '')[:12]))
        elif b['mtime'] != a['mtime']:
            print('TOUCHED %s size=%s mtime %s->%s'
                  % (rel, b['size'], b['mtime'], a['mtime']))
    print('bound=%s last_tick=%s log_bytes=%s' %
          (res['bound'], res['last_tick'], res['log_bytes']))


if __name__ == '__main__':
    main()
