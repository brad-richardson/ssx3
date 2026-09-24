#!/usr/bin/env bash
# N8D7M12P6M6R compiled-input evidence (read-only): locate the CMake/Gradle
# build-system file list (compile_commands.json / Ninja graph) under .cxx,
# show whether the required fork frontend/worker/backend, renderer
# interface/page tracker/Granite and codegen inputs are in the compiled /
# linked graph, and capture PS2X_GAME_SOURCE_COUNT. Full lists stay in
# private WSL-root-top-level files (outside staged roots); stdout is the
# bounded summary committed here.
set -euo pipefail
root=/home/brad/n8d7m12p6m6
cxx="$root/PS2Recomp/android/app/.cxx"
echo "== .cxx tree =="
find "$cxx" -maxdepth 4 | head -20
arm=$(dirname "$(ls "$cxx"/RelWithDebInfo/*/arm64-v8a/CMakeCache.txt | head -1)")
echo "ARM_DIR=$arm"
echo "== compile_commands.json =="
if [ -f "$arm/compile_commands.json" ]; then
  python3 - "$arm/compile_commands.json" <<'PY'
import json, sys
cmds = json.load(open(sys.argv[1], encoding='utf-8'))
print(f"entries={len(cmds)}")
files = [c.get('file', '') for c in cmds]
probe = ['gs_frontend.cpp', 'gs_worker.cpp', 'ps2_gs_parallel_backend.cpp',
         'gs_interface.cpp', 'page_tracker.cpp', 'memory_allocator.cpp',
         'register_functions.cpp', 'ps2_android_runtime.cpp', 'unity_',
         'codegen-ssx3', 'parallel-gs', 'Granite']
for p in probe:
    hits = [f for f in files if p in f]
    print(f"{p}: {len(hits)}" + (f" e.g. {hits[0][-100:]}" if hits else ""))
PY
else
  echo "compile_commands.json ABSENT"
fi
echo "== ninja graph =="
if [ -f "$arm/build.ninja" ]; then
  wc -l "$arm/build.ninja"
  for p in gs_frontend.cpp gs_worker.cpp ps2_gs_parallel_backend.cpp gs_interface.cpp page_tracker.cpp memory_allocator.cpp register_functions.cpp codegen-ssx3 parallel-gs Granite unity_; do
    printf "%s: " "$p"; grep -c -- "$p" "$arm/build.ninja" || true
  done
else
  echo "build.ninja ABSENT"
  find "$arm" -maxdepth 2 -name "*.ninja" | head
fi
echo "== PS2X_GAME_SOURCE_COUNT =="
grep -rho "PS2X_GAME_SOURCE_COUNT[^\\n]*" "$root/assembleRelease.log" "$arm/CMakeCache.txt" 2>/dev/null | head -5 || true
grep -c "codegen-ssx3" "$arm/build.ninja" 2>/dev/null || true
echo "== linked runner inputs (ninja targets for libps2EntryRunner) =="
grep -o "libps2EntryRunner[^ :]*" "$arm/build.ninja" 2>/dev/null | sort -u | head -5 || true
echo "== cache path =="
ls "$cxx"/RelWithDebInfo/*/arm64-v8a/CMakeCache.txt
