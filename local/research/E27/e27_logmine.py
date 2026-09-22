"""E27 Mission 2(b): mine the RETAINED e26a function log. STATIC lane -- no boot.

Reads the pinned function log (sha checked by the caller against the committed
E26 pin) in ONE streaming pass and records, per symbol of interest, the enter
count and the first/last line. Also records what runs AFTER the last entry of
each of the three legs the brief names (walker, feeder, GetPicture call site).
"""
import re, sys, json
from e27_common import *

LOG = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run/ps2_log-e26a-1.txt')

SYMS = {
 'walker            sub_003DFED0': 'sub_003DFED0_0x3dfed0',
 'classifier        sub_003DFE88': 'sub_003DFE88_0x3dfe88',
 'walker-caller     sub_003E0170': 'sub_003E0170_0x3e0170',
 'chunk-src-A       sub_003DFBD0': 'sub_003DFBD0_0x3dfbd0',
 'chunk-src-B       sub_003DFC48': 'sub_003DFC48_0x3dfc48',
 'chunk-src-C       sub_003E13E8': 'sub_003E13E8_0x3e13e8',
 'desc-fill         sub_003AECE0': 'sub_003AECE0_0x3aece0',
 'desc-fill2        sub_003AED20': 'sub_003AED20_0x3aed20',
 'pop               sub_003B06B0': 'sub_003B06B0_0x3b06b0',
 'release           sub_003B06F8': 'sub_003B06F8_0x3b06f8',
 'producer-cb       sub_003B0B10': 'sub_003B0B10_0x3b0b10',
 'feeder            sub_003B0B40': 'sub_003B0B40_0x3b0b40',
 'getpic-callsite   sub_003B0FB8': 'sub_003B0FB8_0x3b0fb8',
 'getpic-helper     sub_003B10D0': 'sub_003B10D0_0x3b10d0',
 'GetPicture thunk  sub_00402A10': 'sub_00402A10_0x402a10',
 'AddBs thunk       sub_004029D0': 'sub_004029D0_0x4029d0',
 'memcpy            sub_003E6574': 'sub_003E6574_0x3e6574',
 'lock              sub_003E5700': 'sub_003E5700_0x3e5700',
 'unlock            sub_003E5760': 'sub_003E5760_0x3e5760',
 'WaitSema stub     sub_00423DE0': 'sub_00423DE0_0x423de0',
 'thread4 entry     sub_0031AC08': 'sub_0031AC08_0x31ac08',
 'sema36 waiter     sub_003C1980': 'sub_003C1980_0x3c1980',
 'sema36 signaller  sub_003C1298': 'sub_003C1298_0x3c1298',
}
NAME2KEY = {v: k for k, v in SYMS.items()}

enters = {k: 0 for k in SYMS}
exits  = {k: 0 for k in SYMS}
first  = {k: None for k in SYMS}
last   = {k: None for k in SYMS}

pat = re.compile(r'^\t*(>>|<<) (\S+) (enter|exit)$')
total = 0
bad = 0
# tail window after the last feeder enter, filled on a second concern below
with LOG.open('r', errors='replace') as f:
    for n, line in enumerate(f, 1):
        total = n
        m = pat.match(line.rstrip('\n'))
        if not m:
            bad += 1
            continue
        k = NAME2KEY.get(m.group(2))
        if k is None:
            continue
        if m.group(1) == '>>':
            enters[k] += 1
            if first[k] is None: first[k] = n
            last[k] = n
        else:
            exits[k] += 1

rows = []
for k in SYMS:
    rows.append(dict(symbol=k, enters=enters[k], exits=exits[k],
                     first_line=first[k], last_line=last[k]))
out = dict(utc=utc(), log=str(LOG), log_lines=total, unparsed_lines=bad,
           note='depth() in ps2_log.h is thread_local; the EE runs its guest '
                'threads on one host thread, so indentation is ONE interleaved '
                'stack and does NOT separate guest threads. Counts are exact; '
                'nesting is not a per-guest-thread stack.',
           rows=rows)
save('logmine.json', out)
w = max(len(k) for k in SYMS)
print(f"log lines {total}  unparsed {bad}")
print(f"{'symbol'.ljust(w)}  {'enters':>8} {'exits':>8}  {'first':>9} {'last':>9}")
for r in rows:
    print(f"{r['symbol'].ljust(w)}  {r['enters']:>8} {r['exits']:>8}  "
          f"{str(r['first_line']):>9} {str(r['last_line']):>9}")
print('# E27 LOGMINE TAIL COMPLETE lines=' + str(total))
