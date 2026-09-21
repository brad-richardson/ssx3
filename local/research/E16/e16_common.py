import datetime, hashlib, json, os, shutil
from pathlib import Path

E = Path(__file__).resolve().parent
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
R = W / 'PS2Recomp'
B = Path('/tmp/p1-link/runtime')
P = W / 'P1'
M = 1024**2
G = 1024**3
BASE_SHA = '67c0a632d44cad8c0e47b4e2c0ee3782b22fd467'

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def save(name, obj): (E / name).write_text(json.dumps(obj, indent=2) + '\n')
def pin(p):
    p = Path(p); s = p.stat()
    return dict(path=str(p), bytes=s.st_size, allocated=s.st_blocks*512, sha256=sha(p))
def size(p, allocated=True):
    p = Path(p)
    try:
        s = p.lstat()
        if not p.is_dir(): return s.st_blocks*512 if allocated else s.st_size
        total = s.st_blocks*512 if allocated else 0
        for root, dirs, files in os.walk(p):
            for name in dirs+files:
                q = Path(root)/name
                try:
                    s = q.lstat()
                    total += s.st_blocks*512 if allocated else (s.st_size if q.is_file() else 0)
                except FileNotFoundError: pass
        return total
    except FileNotFoundError: return 0
def sample():
    paths = list(P.glob('e16-*')) + list(P.glob('._e16-*')) + list((P/'run').glob('*e16*'))
    # The shared function trace is charged even though its name lacks E16.
    paths += [P/'run/ps2_log.txt', P/'run/._ps2_log.txt']
    allocation_receipt=E/'fork-allocation-delta.json'
    fork_delta=json.loads(allocation_receipt.read_text())['positive_growth'] if allocation_receipt.exists() else 0
    owned=sum(size(p) for p in set(paths))
    return dict(utc=utc(), internal_free=shutil.disk_usage('/private/tmp').free,
                internal_allocated=size(B)+size(E), build_allocated=size(B), evidence_allocated=size(E),
                ssd_free=shutil.disk_usage(W).free, ssd_allocated=owned+fork_delta,
                ssd_owned_paths_allocated=owned,fork_positive_growth=fork_delta,
                ssd_paths=[str(p) for p in sorted(set(paths)) if p.exists()])
def bound(s):
    if s['internal_allocated'] >= 5*G-512*M: return 'internal_allocation'
    if s['internal_free'] <= 2*G+512*M: return 'internal_floor'
    if s['ssd_allocated'] >= 12*G-512*M: return 'ssd_allocation'
    if s['ssd_free'] <= 2*G+512*M: return 'ssd_floor'
def admission(s):
    assert not bound(s), s
    assert s['internal_free'] >= 2*G+512*M+max(0,5*G-s['internal_allocated']), s
    assert s['ssd_free'] >= 2*G+512*M+max(0,12*G-s['ssd_allocated']), s
