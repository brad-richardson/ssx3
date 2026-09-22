"""E27 Mission 2(b), third pass: the refill-kick and staging symbols."""
import re
from e27_common import *
LOG = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run/ps2_log-e26a-1.txt')
SYMS = {
 'refill-kick       sub_003DCFC0': 'sub_003DCFC0_0x3dcfc0',
 'ring-advance      sub_003E03D0': 'sub_003E03D0_0x3e03d0',
 'stream-tick       sub_003DD310': 'sub_003DD310_0x3dd310',
 'desc-stage        sub_003AEB18': 'sub_003AEB18_0x3aeb18',
 'desc-stage-owner  sub_003AEAD0': 'sub_003AEAD0_0x3aead0',
 'movie-open        sub_003B04F8': 'sub_003B04F8_0x3b04f8',
 'movie-tick        sub_003B0600': 'sub_003B0600_0x3b0600',
 'mpeg-front        sub_003AECB8': 'sub_003AECB8_0x3aecb8',
 'mpeg-front2       sub_003AE450': 'sub_003AE450_0x3ae450',
 'cdstream-read     sub_003DD4E8': 'sub_003DD4E8_0x3dd4e8',
 'typecheck         sub_003DFE18': 'sub_003DFE18_0x3dfe18',
 'alloc             sub_00319B48': 'sub_00319B48_0x319b48',
 'freenode          sub_003204B8': 'sub_003204B8_0x3204b8',
}
N2K = {v: k for k, v in SYMS.items()}
c = {k: 0 for k in SYMS}; first = dict.fromkeys(SYMS); last = dict.fromkeys(SYMS)
pat = re.compile(r'^\t*>> (\S+) enter$')
with LOG.open('r', errors='replace') as f:
    for n, line in enumerate(f, 1):
        m = pat.match(line.rstrip('\n'))
        if not m: continue
        k = N2K.get(m.group(1))
        if k is None: continue
        c[k] += 1
        if first[k] is None: first[k] = n
        last[k] = n
rows = [dict(symbol=k, enters=c[k], first_line=first[k], last_line=last[k]) for k in SYMS]
save('logmine2.json', dict(utc=utc(), log=str(LOG), rows=rows))
w = max(len(k) for k in SYMS)
for r in rows:
    print(f"{r['symbol'].ljust(w)} {r['enters']:>7}  first={r['first_line']}  last={r['last_line']}")
print('# E27 LOGMINE2 TAIL COMPLETE')
