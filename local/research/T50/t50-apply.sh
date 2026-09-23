#!/usr/bin/env bash
# T50 apply: record pre-patch SHA, apply t50-hook.py (asserts count==1 or aborts).
set -e
G=/home/brad/pcsx2-g7/pcsx2
sha256sum $G/pcsx2/R5900OpcodeImpl.cpp
python3 /home/brad/pcsx2-g7/t50-hook.py
echo "=== T50 diffstat ==="
cd $G && git diff --stat
echo T50_APPLY_DONE
