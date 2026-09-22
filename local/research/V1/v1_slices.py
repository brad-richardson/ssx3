"""V1 slice checks: committed head/tail slices vs mirror file bytes (read-only).

Slices are Tier-1 HEAD blobs; targets are read fresh (one read here, but the
bytes also carry PASS1+PASS2 full-sha stability from the audit).
"""
import subprocess
from pathlib import Path
from v1_common import E, REPO, SSD, SHARE, run, git_blob_id, utc, save

# (lane, slice-stem, t4-file, sides-present)
MAP = []
for lane, stem in [('T27', 't27r1'), ('T27', 't27r2'), ('T27', 't27r3'),
                   ('T28', 't28r1'), ('T29', 't29r1'), ('T30', 't30r1'),
                   ('T31', 't31r1'), ('T32', 't32r1'), ('T33', 't33r2'),
                   ('T34', 't34r1'), ('T35', 't35r1'), ('T36', 't36r1'),
                   ('T37', 't37r1'), ('T38', 't38r1'), ('T39', 't39r1'),
                   ('T40', 't40r2'), ('T41', 't41r4')]:
    MAP.append((lane, f'{stem}-trace-head.txt', f'{stem}-trace-tail.txt', f'emulog-{stem}.txt',
                ['ssd', 'share']))
MAP.append(('T42', 't42r3-emulog-head.txt', 't42r3-emulog-tail.txt', 'emulog-t42r3.txt', ['ssd', 'share']))
MAP.append(('T43', 't43r1-emulog-head.txt', 't43r1-emulog-tail.txt', 'emulog-t43r1.txt', ['ssd', 'share']))
MAP.append(('T45', 't45r2-variant-emulog-head.txt', 't45r2-variant-emulog-tail.txt',
            'emulog-t45r2-variant.txt', ['share']))
MAP.append(('T46', 't46r3-emulog-head.txt', 't46r3-emulog-tail.txt',
            'emulog-t46r3.txt', ['ssd']))

def blob_bytes(relpath):
    cp = subprocess.run(['git', '-C', str(REPO), 'show', f'HEAD:{relpath}'], capture_output=True)
    assert cp.returncode == 0, relpath
    return cp.stdout

def edge(path, n, which):
    with Path(path).open('rb') as f:
        if which == 'head':
            return f.read(n)
        f.seek(-n, 2)
        return f.read(n)

rec = {'utc': utc(), 'rows': {}, 'head_match': 0, 'head_mismatch': [], 'tail_match': 0,
       'tail_mismatch': [], 'missing': []}
for lane, hname, tname, tfile, sides in MAP:
    hrel, trel = f'local/research/{lane}/{hname}', f'local/research/{lane}/{tname}'
    try:
        hb, tb = blob_bytes(hrel), blob_bytes(trel)
    except AssertionError:
        rec['missing'].append(hrel)
        continue
    for side in sides:
        root = SSD / 'ps2x-t4' if side == 'ssd' else SHARE / 'ps2x-t4'
        p = root / tfile
        key = f't4_{side}/{tfile}'
        try:
            size = p.stat().st_size
            hm = edge(p, len(hb), 'head') == hb
            tm = edge(p, len(tb), 'tail') == tb
        except OSError:
            rec['missing'].append(key)
            continue
        rec['rows'][key] = {'target_bytes': size, 'head_bytes': len(hb), 'tail_bytes': len(tb),
                            'head_match': hm, 'tail_match': tm,
                            'head_blob': git_blob_id(REPO, hrel),
                            'tail_blob': git_blob_id(REPO, trel)}
        if hm:
            rec['head_match'] += 1
        else:
            rec['head_mismatch'].append(key)
        if tm:
            rec['tail_match'] += 1
        else:
            rec['tail_mismatch'].append(key)
        print(f'{key}: head={hm} tail={tm} ({len(hb)}/{len(tb)} B of {size})', flush=True)
save('slices.json', rec)
print(f"head {rec['head_match']}/{len(rec['rows'])} tail {rec['tail_match']}/{len(rec['rows'])} "
      f"missing={rec['missing']}", flush=True)
