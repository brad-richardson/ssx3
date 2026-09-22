"""E28 SSD-corroboration gate. The link is PROVEN pattern-dependent corrupt, so:

  * every file this lane quotes is hashed TWICE, separated in time (pass 1 and
    pass 2 are separate invocations);
  * anything git TRACKS is additionally compared against the git object, which
    is content-addressed and therefore an independent check that does not go
    through the same read path;
  * the two e26a capture logs are compared against the SHA E26 COMMITTED.

The generated guest sources are .gitignore'd (`ps2xRuntime/src/runner`), so for
them repetition in time is the only available corroboration; that is stated,
not hidden.
"""
import subprocess, sys
from e28_common import *

GEN = R / 'ps2xRuntime/src/runner'
RUN = Path('/Volumes/Extreme SSD/ps2recomp-spike/P1/run')

GEN_FILES = [
 'sub_003DFED0_0x3dfed0.cpp',   # the walker
 'sub_003DFE88_0x3dfe88.cpp',   # the classifier
 'sub_003E0170_0x3e0170.cpp',   # the walker's caller (read completion)
 'sub_003DFC48_0x3dfc48.cpp',   # releaseBytes / refill threshold
 'sub_003DFBD0_0x3dfbd0.cpp',   # the STRM type check
 'sub_003E12E0_0x3e12e0.cpp',   # the dequeue that STRIPS the tag
 'sub_003E13E8_0x3e13e8.cpp',   # the chunk release
 'sub_003AEAD0_0x3aead0.cpp',   # descriptor staging + its retry loop
 'sub_003B06B0_0x3b06b0.cpp',   # the pop
 'sub_003B06F8_0x3b06f8.cpp',   # the release
 'sub_003B0B10_0x3b0b10.cpp',   # the producer callback entry
 'sub_003B0B40_0x3b0b40.cpp',   # the feeder (AddBs call site)
 'sub_003B0FB8_0x3b0fb8.cpp',   # the GetPicture call site + its re-ask loop
 'sub_00402A10_0x402a10.cpp',   # sceMpegGetPicture thunk
 'sub_004029D0_0x4029d0.cpp',   # sceMpegAddBs thunk
 'sub_00402B38_0x402b38.cpp',   # the loop guard accessor
]
TRACKED = ['ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp']
CAPTURES = {
 'ps2_log-e26a-1.txt': 'd849775b9f8199ae65a701f90668ede247f7d9afd41d1e18b12e450ccf1024ec',
 'boot-e26a-1.log':    'c9ddf91a413b9c05c168b373c596ad79cc32aa15b0a0f7e7047ba362178e33e5',
}

def git_blob_sha(rel):
    p = subprocess.run(['git', '-C', str(R), 'show', f'{BASE_SHA}:{rel}'],
                       capture_output=True)
    if p.returncode != 0:
        return None
    import hashlib
    return hashlib.sha256(p.stdout).hexdigest()

pss = sys.argv[1]
rows = []
for n in GEN_FILES:
    p = GEN / n
    rows.append(dict(kind='generated-source (gitignored: SSD-only)', path=str(p),
                     bytes=p.stat().st_size, sha256=sha(p), git_object=None))
for rel in TRACKED:
    p = R / rel
    rows.append(dict(kind='tracked source', path=str(p), bytes=p.stat().st_size,
                     sha256=sha(p), git_object=git_blob_sha(rel)))
for n, pinned in CAPTURES.items():
    p = RUN / n
    s = sha(p)
    rows.append(dict(kind='e26a capture', path=str(p), bytes=p.stat().st_size,
                     sha256=s, committed_pin=pinned, equals_committed_pin=(s == pinned)))
out = dict(utc=utc(), pass_=int(pss), ssd_mounted=Path('/Volumes/Extreme SSD').is_dir(),
           rows=rows)
save(f'pins-pass-{pss}.json', out)
for r in rows:
    tag = ''
    if r.get('git_object') is not None:
        tag = '  git=' + ('EQUAL' if r['git_object'] == r['sha256'] else 'DIFFER')
    if 'equals_committed_pin' in r:
        tag = '  pin=' + ('EQUAL' if r['equals_committed_pin'] else 'DIFFER')
    print(f"{r['sha256'][:16]}  {r['bytes']:>10}  {Path(r['path']).name}{tag}")
print(f'# E28 PINS PASS {pss} TAIL COMPLETE rows=' + str(len(rows)))
