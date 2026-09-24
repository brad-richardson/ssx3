#!/usr/bin/env bash
# N9 Part 2 WSL source verify (pre-build and post-build): collector verify on
# the four transferred roots + runner-dir guard. Read-only. Adapted from
# N8D7M12P6M6R/source_verify.sh (root n9).
set -euo pipefail
root=/home/brad/n9
python3 "$root/source_manifest.py" verify \
  --manifest "$root/source-manifest.json" \
  --fork "$root/PS2Recomp" \
  --parallel "$root/parallel-gs" \
  --codegen "$root/codegen-ssx3" \
  --jni "$root/jniLibs" \
  --max-files 40000 --max-bytes 2000000000
echo "== runner dir =="
ls -la "$root/PS2Recomp/ps2xRuntime/src/runner/"
sha256sum "$root/PS2Recomp/ps2xRuntime/src/runner/register_functions.cpp"
wc -c "$root/PS2Recomp/ps2xRuntime/src/runner/register_functions.cpp"
echo "== root size =="
du -sb "$root"
