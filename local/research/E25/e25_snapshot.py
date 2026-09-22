"""E25 mission 5 -- durability. Snapshot the rebuilt tree to the SSD so the
next host restart costs a COPY, not a rebuild.

Three hazards drive the shape of this snapshot, each measured before:
  1. `/tmp` is wiped by a host restart. That is what cost E24 its boot.
  2. The SSD is ExFAT with ~1 MiB clusters, so a 3,000-file tree copied file
     by file wastes gigabytes of allocation. The tree is TARred, never `mv`d.
  3. Large writes to the ExFAT volume have been observed to read back as zeros.
     Every artifact is therefore re-read and re-hashed AFTER it lands, and the
     tar is additionally listed so its member count is proven.
Nothing is deleted and the restore is NOT exercised -- the procedure is tabled.
"""
import subprocess, time
from e25_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
DEST = P / 'e25-snapshot'
assert B0.exists(), f'{B0} absent -- nothing to snapshot'
admission(sample())
DEST.mkdir(parents=True, exist_ok=False)

# --- per-file manifest of the tree, computed on the INTERNAL volume --------
files, total = [], 0
for root, _d, names in os.walk(B0):
    for n in sorted(names):
        q = Path(root) / n
        try:
            st = q.lstat()
            if not q.is_file() or q.is_symlink(): continue
            files.append(dict(path=str(q), bytes=st.st_size, sha256=sha(q)))
            total += st.st_size
        except (FileNotFoundError, PermissionError):
            pass
save('snapshot-manifest.json', dict(utc=utc(), tree=str(B0), files=len(files),
                                    bytes=total, entries=files))
print(f'manifest: {len(files)} files, {total} bytes')

def run(argv, **kw):
    t = time.monotonic()
    p = subprocess.run([str(x) for x in argv], text=True, capture_output=True, **kw)
    return dict(argv=[str(x) for x in argv], rc=p.returncode, elapsed_s=time.monotonic()-t,
                stdout_bytes=len(p.stdout), stderr=p.stderr[-2000:]), p.stdout

artifacts = {}
# --- 1. the whole tree as ONE tar (ExFAT cluster discipline) --------------
tar = DEST / 'e18-mpeg-link.tar'
rec, _ = run(['tar', '-C', '/tmp', '-cf', str(tar), 'e18-mpeg-link'])
assert rec['rc'] == 0, rec
listing, out = run(['tar', '-tf', str(tar)])
assert listing['rc'] == 0, listing
members = [l for l in out.splitlines() if l and not l.endswith('/')]
first = sha(tar); second = sha(tar)   # re-read guards the ExFAT zero-read hazard
artifacts['tree_tar'] = dict(path=str(tar), bytes=tar.stat().st_size,
                             allocated=tar.stat().st_blocks*512, sha256=first,
                             sha256_reread=second, reread_equal=first == second,
                             members_total=len([l for l in out.splitlines() if l]),
                             members_files=len(members),
                             manifest_files=len(files),
                             member_count_matches_manifest=len(members) == len(files),
                             create=rec, list=listing)

# --- 2. the two binaries E26 actually needs, standalone --------------------
for key, rel in (('runner', 'ps2xRuntime/ps2EntryRunner'), ('suite', 'ps2xTest/ps2x_tests')):
    src = B0 / rel
    dst = DEST / src.name
    rec, _ = run(['cp', '-p', str(src), str(dst)])
    assert rec['rc'] == 0, rec
    a, b = sha(dst), sha(dst)
    artifacts[key] = dict(source=str(src), path=str(dst), bytes=dst.stat().st_size,
                          allocated=dst.stat().st_blocks*512,
                          source_sha=sha(src), sha256=a, sha256_reread=b,
                          reread_equal=a == b, copy_faithful=a == sha(src), copy=rec)

ok = all(v.get('reread_equal', True) for v in artifacts.values()) and \
     all(v.get('copy_faithful', True) for v in artifacts.values()) and \
     artifacts['tree_tar']['member_count_matches_manifest']
s = sample()
save('snapshot.json', dict(utc=utc(), dest=str(DEST), artifacts=artifacts,
                           all_verified=ok, deletions=0, restore_tested=False,
                           restore_procedure='RESTORE.md', resources=s,
                           ssd_allocated_after=s['ssd_allocated']))
for k, v in artifacts.items():
    print(f"  {k:9} {v['bytes']:>12} B  alloc {v['allocated']:>12}  sha {v['sha256'][:16]}…  "
          f"reread_equal={v['reread_equal']}")
print('tar members(files)', artifacts['tree_tar']['members_files'],
      'manifest files', len(files),
      'match', artifacts['tree_tar']['member_count_matches_manifest'])
print('ALL VERIFIED', ok)
print('# E25 SNAPSHOT TAIL COMPLETE')
