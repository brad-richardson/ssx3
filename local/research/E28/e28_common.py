import datetime, hashlib, json, os, shutil
from pathlib import Path

E = Path(__file__).resolve().parent
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
R = W / 'PS2Recomp'
# The protected build tree E15-E23 ran on, wiped by the host restart that opened
# E24 red and REBUILT BIT-IDENTICALLY by E25 (runner e462e448..., suite
# 2152e5ad..., both byte-equal to the lost pins). E28 BUILDS NOTHING and EDITS
# NOTHING: it spends its one boot on the binary already standing at this exact
# path, which is the very binary E23 and E26 booted. Host-side MPEG.cpp logging
# is E29's lane, not this one; E28 is a GUEST-half confirmation on the EXISTING
# byte-identical binary. The other two trees stay absent and are NOT rebuilt.
B0 = Path('/tmp/e18-mpeg-link/runtime')
PROTECTED_BUILDS = [Path('/tmp/p1-link/runtime'), Path('/tmp/e17-map-link/runtime'), B0]
NEWB = B0
B = Path(os.environ.get('E28_BUILD_DIR', str(B0)))
OUT = Path('/tmp/e28-no-codegen')
P = W / 'P1'
M = 1024**2
G = 1024**3
BASE_SHA = '3adc0478b6d2260acdd28a249466f2eef9a20176'
# E28 CONTRACT: internal reservation 3 GiB, the brief's declared value. E28's
# Mission 0 is verify-or-restore; on path (a) no build runs, so the reservation
# is declared, not consumed. FLOOR and GUARD stay 2 GiB + 0.5 GiB, untouched.
IRES = 3*G

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def save(name, obj): (E / name).write_text(json.dumps(obj, indent=2) + '\n')
def pin(p):
    p = Path(p); s = p.stat()
    return dict(path=str(p), bytes=s.st_size, allocated=s.st_blocks*512, sha256=sha(p))
def pin_or_missing(p):
    p = Path(p)
    if not p.exists(): return dict(path=str(p), present=False)
    row = pin(p); row['present'] = True; return row
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
    paths = list(P.glob('e28-*')) + list(P.glob('._e28-*')) + list((P/'run').glob('*e28*'))
    # The shared function trace is charged even though its name lacks E28.
    paths += [P/'run/ps2_log.txt', P/'run/._ps2_log.txt']
    allocation_receipt=E/'fork-allocation-before.json'
    fork_delta=0
    if allocation_receipt.exists():
        old=json.loads(allocation_receipt.read_text())['allocated']
        roots=[R/'.git',R/'ps2xRuntime/src/lib/Kernel/Stubs',R/'ps2xTest/src']
        for root in roots:
            for p in [root,*root.rglob('*')]:
                try:fork_delta+=max(0,p.lstat().st_blocks*512-old.get(str(p),0))
                except FileNotFoundError:pass
    owned=sum(size(p) for p in set(paths))
    return dict(utc=utc(), internal_free=shutil.disk_usage('/private/tmp').free,
                internal_allocated=size(NEWB)+size(OUT)+size(E), build_allocated=size(NEWB), codegen_allocated=size(OUT), evidence_allocated=size(E),
                ssd_free=shutil.disk_usage(W).free, ssd_allocated=owned+fork_delta,
                ssd_owned_paths_allocated=owned,fork_positive_growth=fork_delta,
                ssd_paths=[str(p) for p in sorted(set(paths)) if p.exists()])
def bound(s):
    if OUT.exists(): return 'unexpected_codegen'
    if s['internal_allocated'] >= IRES-128*M: return 'internal_allocation'
    if s['internal_free'] <= 2*G+512*M: return 'internal_floor'
    if s['ssd_allocated'] >= 16*G-512*M: return 'ssd_allocation'
    if s['ssd_free'] <= 2*G+512*M: return 'ssd_floor'
def admission(s):
    assert not bound(s), s
    assert s['internal_free'] >= 2*G+512*M+max(0,IRES-s['internal_allocated']), s
    assert s['ssd_free'] >= 2*G+512*M+max(0,16*G-s['ssd_allocated']), s
