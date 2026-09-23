#!/usr/bin/env bash
# T49 apply: record pre-patch SHAs, apply t49-hook.py (asserts count==1 or aborts).
set -e
G=/home/brad/pcsx2-g7/pcsx2
sha256sum $G/pcsx2/VU1micro.cpp $G/pcsx2/VU1microInterp.cpp $G/pcsx2/VUops.cpp $G/pcsx2/Vif_Transfer.cpp $G/pcsx2/Vif_Codes.cpp
python3 /home/brad/pcsx2-g7/t49-hook.py
echo "=== T49 diffstat ==="
cd $G && git diff --stat
echo T49_APPLY_DONE
