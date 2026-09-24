#!/usr/bin/env bash
# N8D7M12P6M6R WSL source verify (pre-build and post-build): collector verify
# on the four transferred roots + runner-dir guard. Read-only.
set -euo pipefail
root=/home/brad/n8d7m12p6m6
python3 "$root/source_manifest.py" verify \
  --manifest "$root/source-manifest.json" \
  --fork "$root/PS2Recomp" \
  --parallel "$root/parallel-gs" \
  --codegen "$root/codegen-ssx3" \
  --jni "$root/jniLibs" \
  --max-files 30000 --max-bytes 2000000000
echo "== runner dir =="
ls -la "$root/PS2Recomp/ps2xRuntime/src/runner/"
sha256sum "$root/PS2Recomp/ps2xRuntime/src/runner/register_functions.cpp"
echo "== root size =="
du -sb "$root"
