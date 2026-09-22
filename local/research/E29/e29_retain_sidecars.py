"""E29 -- retain the AppleDouble sidecars CMake's globs would COMPILE. No deletion.

E18 hit this with TWO files and retained them by RENAME rather than deleting
them; E25 recorded that the internal build had 0 AppleDouble compile entries
BECAUSE those two had been out of the tree since. E29 builds into an ExFAT
build dir instead of /tmp, which puts FetchContent's `_deps` checkout on a
filesystem with no native xattrs, so macOS writes a `._x` sidecar beside every
file that carries one -- 7,865 of them in this tree.

Only the ones a CMake GLOB picks up matter, and `compile_commands.json` names
them exactly: 32 in rabbitizer-src plus `._MPEG.cpp`, which E29's OWN edit
created in the fork source tree at 16:14Z -- E18's bug, reproduced on E29's own
diff. Each is renamed to a name no C/C++ glob matches. NOTHING is deleted, and
the manifest below restores every one byte-for-byte.
"""
import json, subprocess
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
SUFFIX = '.appledouble-retained-e29'
CC = NEWB / 'compile_commands.json'

entries = json.loads(CC.read_text())
ad = sorted({e['file'] for e in entries if '/._' in e['file']})
# Also sweep the two directories whose CMakeLists GLOB, so a re-configure
# cannot re-add a sidecar this pass did not see.
sweep = []
for d in [NEWB / '_deps/rabbitizer-src', R / 'ps2xRuntime/src', R / 'ps2xTest/src']:
    for p in d.rglob('._*'):
        if p.suffix in ('.c', '.cpp', '.cc', '.cxx', '.h', '.hpp'):
            sweep.append(str(p))
targets = sorted(set(ad) | set(sweep))

rows, moved = [], 0
for f in targets:
    src = Path(f)
    if not src.exists():
        rows.append(dict(path=f, present=False)); continue
    dst = src.with_name(src.name + SUFFIX)
    row = dict(path=f, retained_as=str(dst), bytes=src.stat().st_size,
               sha256=sha(src), in_compile_commands=f in ad,
               in_fork_source_tree=str(R) in f)
    if dst.exists():
        row['already_retained'] = True
    else:
        os.rename(src, dst); moved += 1
        row['already_retained'] = False
        row['sha256_after_rename'] = sha(dst)
        row['bytes_preserved'] = dst.stat().st_size == row['bytes']
        row['sha_preserved'] = row['sha256_after_rename'] == row['sha256']
    rows.append(row)

save('appledouble-retained.json', dict(
    utc=utc(), procedure='E18 retain-by-rename; ZERO deletions',
    suffix=SUFFIX,
    compile_commands_appledouble_entries_before=len(ad),
    swept_glob_dirs=[str(NEWB / '_deps/rabbitizer-src'), str(R / 'ps2xRuntime/src'), str(R / 'ps2xTest/src')],
    targets=len(targets), renamed=moved,
    deletions=0,
    all_bytes_preserved=all(r.get('bytes_preserved', True) for r in rows),
    all_shas_preserved=all(r.get('sha_preserved', True) for r in rows),
    the_one_E29_created=[r for r in rows if r['path'].endswith('/._MPEG.cpp')],
    rows=rows))
print('compile_commands AppleDouble entries before:', len(ad))
print('targets', len(targets), 'renamed', moved, 'deletions 0')
st = subprocess.run(['git', '-C', str(R), 'status', '--short'], text=True, capture_output=True).stdout
print('fork status after:', repr(st))
assert sorted(st.splitlines()) == sorted([' M ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp', '?? ps2_log.txt']), st
print('# E29 RETAIN-SIDECARS TAIL COMPLETE')
