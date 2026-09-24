#!/usr/bin/env bash
set -euo pipefail
test -d /home/brad/n8d6b/PS2Recomp
test -d /home/brad/n8d6b/parallel-gs
test -d /home/brad/n8d6b/jniLibs
test ! -e /home/brad/n8d7h
echo "== base pins (N8D6B) =="
sha256sum \
  /home/brad/n8d6b/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp \
  /home/brad/n8d6b/parallel-gs/gs/gs_interface.hpp \
  /home/brad/n8d6b/parallel-gs/gs/gs_renderer.hpp \
  /home/brad/n8d6b/parallel-gs/gs/gs_renderer.cpp \
  /home/brad/n8d6b/parallel-gs/gs/n8d5_tile_spirv.hpp \
  /home/brad/n8d6b/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp \
  /home/brad/n8b1/codegen-ssx3/register_functions.cpp \
  /home/brad/n8d6b/jniLibs/arm64-v8a/libvulkan_freedreno.so \
  /home/brad/n8d6b/jniLibs/arm64-v8a/libhardware.so
echo "== sizes =="
du -sh /home/brad/n8d6b /home/brad/n8d5f 2>/dev/null || true
df -h /home | tail -1
echo "== heavy jobs =="
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
echo "== n8d7h absent check and n8b1 codegen =="
test ! -e /home/brad/n8d7h && echo "n8d7h absent OK"
test -d /home/brad/n8b1/codegen-ssx3 && echo "codegen present OK"
test -d /home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358 && echo "ndk present OK"
