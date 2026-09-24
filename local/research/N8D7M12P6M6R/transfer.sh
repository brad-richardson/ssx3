#!/usr/bin/env bash
# N8D7M12P6M6R transfer: stream the four P6M5 staged roots + private manifest
# + collector script to the fresh WSL root over SSH (no public remote).
# Byte-exact in-flight count via count_bytes.py on stderr.
set -euo pipefail
export COPYFILE_DISABLE=1
repo=/Users/brad/dev/ssx3
stage="$repo/local/research/N8D7M12P6M5/stage"
receipt="$repo/local/research/N8D7M12P6M6R"
tar -c -f - \
  -C "$stage" PS2Recomp parallel-gs codegen-ssx3 jniLibs \
  -C "$repo/local/research/N8D7M12P6M5" source-manifest.json \
  -C "$repo/local/tooling/orch" source_manifest.py \
  2>"$receipt/transfer-tar.err" \
| python3 "$receipt/count_bytes.py" \
| ssh bytesize 'wsl -d Ubuntu -- bash -lc "mkdir -p /home/brad/n8d7m12p6m6 && tar -x -C /home/brad/n8d7m12p6m6 -f - && du -sb /home/brad/n8d7m12p6m6 && ls /home/brad/n8d7m12p6m6"'
