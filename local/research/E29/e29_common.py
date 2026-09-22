import datetime, hashlib, json, os, shutil
from pathlib import Path

E = Path(__file__).resolve().parent
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
R = W / 'PS2Recomp'
# E29 CHANGE 1 -- the DEV-ONLY bypass build lives in a NEW dir ON THE SSD. The
# internal volume cannot hold two trees (floor rule), and the brief forbids a
# /tmp build outright. The mainline tree below is NOT touched, NOT rebuilt and
# NOT deleted; E29 only pins it.
NEWSSD = W / 'e29-movie-bypass-build'
# The MAINLINE protected build tree (E18's recipe, rebuilt bit-identically by
# E25). E29 BUILDS NOTHING HERE and EDITS NOTHING HERE: it pins this tree as the
# reference the 458 suite and the e28a receipts were taken on, and builds its
# own DEV-ONLY bypass binary into NEWSSD instead.
B0 = Path('/tmp/e18-mpeg-link/runtime')
MAINLINE_RUNNER = B0 / 'ps2xRuntime/ps2EntryRunner'
MAINLINE_SUITE = B0 / 'ps2xTest/ps2x_tests'
PROTECTED_BUILDS = [Path('/tmp/p1-link/runtime'), Path('/tmp/e17-map-link/runtime'), B0]
# E29 CHANGE 1 (cont.) -- NEWB is the bypass build, on the SSD.
NEWB = NEWSSD
B = Path(os.environ.get('E29_BUILD_DIR', str(NEWSSD)))
BYPASS_RUNNER = NEWSSD / 'ps2xRuntime/ps2EntryRunner'
BYPASS_SUITE = NEWSSD / 'ps2xTest/ps2x_tests'
OUT = Path('/tmp/e29-no-codegen')
P = W / 'P1'
M = 1024**2
G = 1024**3
BASE_SHA = '3adc0478b6d2260acdd28a249466f2eef9a20176'
# E29 CHANGE 2 -- the brief caps the INTERNAL volume at a 512 MB DELTA, because
# E29 runs no internal build at all (the bypass tree is on the SSD). E28's 3 GiB
# reservation was sized for a tree this lane does not create. FLOOR and GUARD
# stay 2 GiB + 0.5 GiB, untouched. SSD: NEW build dir <= 6 GB, all NEW e29-*
# paths <= 16 GB.
IRES = 32*M   # AMENDMENT A1 (amendment-A1.json): was 512*M
# AMENDMENT A2 (amendment-A2.json): this volume is ExFAT with 1 MiB allocation
# blocks, measured, so a 1.25 GB CMake tree occupies 17.2 GB of clusters. The
# brief's caps are read as LOGICAL bytes and paired with explicit ALLOCATION
# ceilings and a free-space floor 13x stricter than the carried one.
BUILD_CAP = 6*G            # logical
BUILD_ALLOC_CEIL = 48*G    # allocation
SSD_CAP = 16*G             # logical
SSD_ALLOC_CEIL = 64*G      # allocation
SSD_FREE_FLOOR = 32*G      # was 2*G+512*M

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
    # E29 CHANGE 3 -- the NEW SSD build dir and every NEW e29-* path are charged
    # to the SSD caps; the internal figure now covers evidence only, because
    # this lane creates no internal tree.
    paths = list(P.glob('e29-*')) + list(P.glob('._e29-*')) + list((P/'run').glob('*e29*'))
    paths += list(W.glob('e29-*')) + list(W.glob('._e29-*'))
    # The shared function trace is charged even though its name lacks E29.
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
    owned_logical=sum(size(p, allocated=False) for p in set(paths))
    return dict(utc=utc(), internal_free=shutil.disk_usage('/private/tmp').free,
                internal_allocated=size(OUT)+size(E), codegen_allocated=size(OUT), evidence_allocated=size(E),
                build_allocated=size(NEWB), build_logical=size(NEWB, allocated=False),
                ssd_logical=owned_logical,
                ssd_free=shutil.disk_usage(W).free, ssd_allocated=owned+fork_delta,
                ssd_owned_paths_allocated=owned,fork_positive_growth=fork_delta,
                ssd_paths=[str(p) for p in sorted(set(paths)) if p.exists()])
def bound(s):
    if OUT.exists(): return 'unexpected_codegen'
    if s['build_logical'] >= BUILD_CAP - 256*M: return 'ssd_build_dir_logical_cap'
    if s['build_allocated'] >= BUILD_ALLOC_CEIL: return 'ssd_build_dir_allocation_ceiling'
    # AMENDMENT A1: the carried trip was `IRES-128*M`, which assumes IRES is
    # much larger than 128 MiB and goes NEGATIVE (always trips) once the cap
    # is right-sized. The threshold now scales with the cap: trip at 75%.
    if s['internal_allocated'] >= IRES*3//4: return 'internal_allocation'
    if s['internal_free'] <= 2*G+512*M: return 'internal_floor'
    if s['ssd_logical'] >= SSD_CAP-512*M: return 'ssd_logical_cap'
    if s['ssd_allocated'] >= SSD_ALLOC_CEIL: return 'ssd_allocation_ceiling'
    if s['ssd_free'] <= SSD_FREE_FLOOR: return 'ssd_floor'
def admission(s):
    assert not bound(s), s
    assert s['internal_free'] >= 2*G+512*M+max(0,IRES-s['internal_allocated']), s
    assert s['ssd_free'] >= SSD_FREE_FLOOR, s
