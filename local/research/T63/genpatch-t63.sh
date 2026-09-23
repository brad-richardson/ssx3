#!/usr/bin/env bash
# T61 receipts: file-scoped diff of the 3 TUs vs HEAD + tree pins.
set -e
G=/home/brad/pcsx2-g7/pcsx2
git -C "$G" rev-parse HEAD
git -C "$G" status --porcelain -- pcsx2/Interpreter.cpp pcsx2/R5900OpcodeImpl.cpp pcsx2/Vif_Transfer.cpp
git -C "$G" diff -- pcsx2/Interpreter.cpp pcsx2/R5900OpcodeImpl.cpp pcsx2/Vif_Transfer.cpp > /home/brad/pcsx2-t4/t63-patch.diff
sha256sum /home/brad/pcsx2-t4/t63-patch.diff
wc -c /home/brad/pcsx2-t4/t63-patch.diff
echo T61_PATCH_DONE
