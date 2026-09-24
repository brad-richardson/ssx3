#!/usr/bin/env bash
# N9 Part 2 transfer: stream the four staged roots + manifest + collector to
# the fresh WSL root over SSH (no public remote). Adapted from
# N8D7M12P6M6R/transfer.sh (root n9, scratch stage). Reuses the P6M6R byte
# counter rather than copying it.
set -euo pipefail
export COPYFILE_DISABLE=1
repo=/Users/brad/dev/ssx3
stage=/Users/brad/dev/ssx3-work/N9/stage
receipt="$repo/local/research/N9"
tar -c -f - \
  -C "$stage" PS2Recomp parallel-gs codegen-ssx3 jniLibs \
  -C "$receipt" source-manifest.json \
  -C "$repo/local/tooling/orch" source_manifest.py \
  2>"$receipt/transfer-tar.err" \
| python3 "$repo/local/research/N8D7M12P6M6R/count_bytes.py" \
| ssh bytesize 'wsl -d Ubuntu -- bash -lc "mkdir -p /home/brad/n9 && tar -x -C /home/brad/n9 -f - && du -sb /home/brad/n9 && ls /home/brad/n9"'
