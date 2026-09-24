from pathlib import Path
import hashlib, os, subprocess

roots = [Path('/home/brad/n8b1/PS2Recomp'), Path('/home/brad/n8b1/parallel-gs'),
         Path('/home/brad/n8b1/codegen-ssx3'), Path('/home/brad/n8d3/jniLibs')]
for p in roots:
    print('INPUT', p, 'exists', p.exists())

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

for p in [roots[0]/'ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp',
          roots[2]/'register_functions.cpp',
          roots[3]/'arm64-v8a/libvulkan_freedreno.so',
          roots[3]/'arm64-v8a/libhardware.so']:
    if p.exists():
        print('SHA', p, sha(p), sha(p))
for pid in sorted(Path('/proc').iterdir()):
    if not pid.name.isdigit():
        continue
    try:
        raw = (pid/'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except (OSError, PermissionError):
        continue
    if any(term in raw.lower() for term in ('gradle', 'ninja', 'clang', 'pcsx2')) and 'inspect.py' not in raw:
        print('ACTIVE', pid.name, raw[:240])
