#!/usr/bin/env bash
set -euo pipefail
test -d /home/brad/n8d5f/PS2Recomp
test -d /home/brad/n8d5f/parallel-gs
test -d /home/brad/n8d5f/jniLibs
test ! -e /home/brad/n8d6b
sha256sum /home/brad/n8d5f/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp /home/brad/n8d5f/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp
sha256sum /home/brad/n8d5f/parallel-gs/gs/n8d5_tile_spirv.hpp /home/brad/n8d5f/parallel-gs/gs/n8d5_tile_spirv.hpp
sha256sum /home/brad/n8b1/codegen-ssx3/register_functions.cpp /home/brad/n8b1/codegen-ssx3/register_functions.cpp
du -sh /home/brad/n8d5f
python3 - <<'PY'
from pathlib import Path
terms = ('gradle', 'ninja', 'clang', 'pcsx2')
active = []
for p in Path('/proc').iterdir():
    if not p.name.isdigit():
        continue
    try:
        comm = (p/'comm').read_text().strip().lower()
        cmd = (p/'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except (OSError, PermissionError):
        continue
    if any(term in comm for term in terms):
        active.append((p.name, comm, cmd[:180]))
print('HEAVY_JOBS', active)
PY
