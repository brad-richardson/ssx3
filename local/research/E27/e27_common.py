"""E27 common — STATIC autopsy lane. NO BOOT, NO LEASE, NO BUILD.

Deliberately minimal against E26's: E27 runs no build, no boot, no capture and
no probe, so the build-tree, admission and boot-cap machinery is not carried.
What IS carried verbatim is the fork base sha and the SSD/fork paths, because
the fork gate must be byte-identical in meaning to E26's.
"""
import datetime, hashlib, json, os
from pathlib import Path

E = Path(__file__).resolve().parent
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
R = W / 'PS2Recomp'
P = W / 'P1'
M = 1024**2
G = 1024**3
BASE_SHA = '3adc0478b6d2260acdd28a249466f2eef9a20176'

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def save(name, obj): (E / name).write_text(json.dumps(obj, indent=2) + '\n')
def pin(p):
    p = Path(p); s = p.stat()
    return dict(path=str(p), bytes=s.st_size, allocated=s.st_blocks*512, sha256=sha(p))
