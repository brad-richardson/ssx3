#!/usr/bin/env bash
# N9 Part 2 compiled-input evidence (read-only). Adapted from
# N8D7M12P6M6R/compiled_inputs.sh (root n9; ARM dir discovered, not hardcoded).
set -euo pipefail
root=/home/brad/n9
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
