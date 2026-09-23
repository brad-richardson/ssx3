#!/bin/zsh
# E51 race boot at ~00:00:18 (E50 build dir, canonical codegen-ssx3).
# Usage: e51_boot.sh <label> <wall> [vu1trace 0|1]
# gfx stats 8200-8280 (T65 counts + per-startPC census); GIF dump PATH1-3
# 8258-8265 (8 vsyncs, as T65's PCSX2 dump) plus PATH2/3 from 8200;
# E4 arm 8260 (head 4096, VRAM arm/freeze); VU1 trace 8240-8280.
set -eu
label=$1 wall=$2 vt=${3:-1}
W=$HOME/dev/ssx3-work
RUN=$W/E51/run
mkdir -p $RUN/e4-$label
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E50/build
export PS2X_GFX_STATS=$RUN/gfx-$label.txt PS2X_GFX_STATS_FROM=8200 PS2X_GFX_STATS_TO=8280
export PS2X_GIF_DUMP=$RUN/gif-$label.bin PS2X_GIF_DUMP_FROM=8258 PS2X_GIF_DUMP_TO=8265 PS2X_GIF_DUMP_IMG_FROM=8200
export PS2X_E4_DIR=$RUN/e4-$label PS2X_E4_ARM_TICK=8260 PS2X_E4_FREEZE_TICK=8261 PS2X_E4_HEAD=4096
if [ "$vt" = 1 ]; then
  export PS2X_VU1_TRACE=$RUN/vu1-$label.txt PS2X_VU1_TRACE_FROM=8240 PS2X_VU1_TRACE_TO=8280
fi
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap 5 --script "$ROUTE"
