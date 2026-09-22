"""E27 Mission 2(b), second pass: what runs AFTER the one feed.

Histograms the function log from the producer callback's exit to EOF and lists
every distinct symbol, so "thread 1 never revisits the walker / feeder /
GetPicture call site" is a count, not an assertion.
"""
import re
from collections import Counter
from e27_common import *

LOG = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run/ps2_log-e26a-1.txt')
CB_EXIT = 3456226          # '<< sub_003B0B10 exit'  (the producer callback ends)
pat = re.compile(r'^\t*(>>|<<) (\S+) (enter|exit)$')

after_cb = Counter()
tail_first = {}
total = 0
with LOG.open('r', errors='replace') as f:
    for n, line in enumerate(f, 1):
        total = n
        if n <= CB_EXIT:
            continue
        m = pat.match(line.rstrip('\n'))
        if not m or m.group(1) != '>>':
            continue
        s = m.group(2)
        after_cb[s] += 1
        tail_first.setdefault(s, n)

rows = [dict(symbol=s, enters=c, first_line_after_cb=tail_first[s])
        for s, c in after_cb.most_common()]
out = dict(utc=utc(), log=str(LOG), log_lines=total,
           boundary_line=CB_EXIT,
           boundary_meaning='the line on which the ONE producer callback '
                            'sub_003B0B10 exits; everything counted here ran after '
                            'the single feed',
           distinct_symbols_after=len(rows), rows=rows)
save('tail-after-feed.json', out)
print(f"log lines {total}; symbols entered after line {CB_EXIT}: {len(rows)}")
for r in rows:
    print(f"  {r['symbol']:<34} {r['enters']:>8}  first@{r['first_line_after_cb']}")
print('# E27 TAIL TAIL COMPLETE distinct=' + str(len(rows)))
