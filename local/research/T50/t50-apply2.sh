#!/usr/bin/env bash
# T50 apply 2: record pre-patch SHAs, apply t50-hook2.py (validates all anchors first).
set -e
G=/home/brad/pcsx2-g7/pcsx2
sha256sum $G/pcsx2/R5900OpcodeImpl.cpp $G/pcsx2/Vif1_Dma.cpp $G/pcsx2/Vif_Codes.cpp $G/pcsx2/Vif1_MFIFO.cpp $G/pcsx2/Dmac.cpp
python3 /home/brad/pcsx2-g7/t50-hook2.py
echo "=== T50b diffstat ==="
cd $G && git diff --stat
echo T50_APPLY2_DONE
