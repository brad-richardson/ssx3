#!/usr/bin/env bash
set -euo pipefail
src=/home/brad/n8d3/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp
dst=/home/brad/n8d5f/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp
expect=358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96
test "$(sha256sum "$src" | cut -d' ' -f1)" = "$expect"
test "$(sha256sum "$src" | cut -d' ' -f1)" = "$expect"
cp "$src" "$dst"
test "$(sha256sum "$dst" | cut -d' ' -f1)" = "$expect"
test "$(sha256sum "$dst" | cut -d' ' -f1)" = "$expect"
