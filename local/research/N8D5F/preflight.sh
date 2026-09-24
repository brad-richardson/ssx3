#!/usr/bin/env bash
set -euo pipefail
for f in \
  /home/brad/n8d3/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp \
  /home/brad/n8d5d/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp \
  /home/brad/n8d5d/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp \
  /home/brad/n8d5d/parallel-gs/gs/n8d5_tile_spirv.hpp \
  /home/brad/n8b1/codegen-ssx3/register_functions.cpp; do
  sha256sum "$f" "$f"
done
du -sh /home/brad/n8d5d /home/brad/n8b1/codegen-ssx3
python3 - <<'PY'
from pathlib import Path
terms = ('gradle', 'ninja', 'clang', 'pcsx2')
active = []
for p in Path('/proc').iterdir():
    if not p.name.isdigit():
        continue
    try:
        cmd = (p/'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except (OSError, PermissionError):
        continue
    if any(t in cmd.lower() for t in terms) and 'preflight.sh' not in cmd:
        active.append((p.name, cmd[:240]))
print('HEAVY_JOBS', active)
PY
