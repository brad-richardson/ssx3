#!/bin/zsh
# E53 race boot (E53 validation build): E50's race window (camera entry trace
# + E4 at 7605, gfx 7590-8280 in T65 format) and E51's GIF dump window
# 8258-8265 (+PATH2/3 images from 8200) for TEX1 K. VU0 start log on.
# Usage: e53_race.sh <label> <wall>   (PS2X_EE_FPMODE passes through)
set -eu
label=$1 wall=$2
W=$HOME/dev/ssx3-work
RUN=$W/E53/run
mkdir -p $RUN/e4-$label
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E53/build
export PS2X_GFX_STATS=$RUN/gfx-$label.txt PS2X_GFX_STATS_FROM=7590 PS2X_GFX_STATS_TO=8280
export PS2X_GIF_DUMP=$RUN/gif-$label.bin PS2X_GIF_DUMP_FROM=8258 PS2X_GIF_DUMP_TO=8265 PS2X_GIF_DUMP_IMG_FROM=8200
export PS2X_E4_DIR=$RUN/e4-$label PS2X_E4_ARM_TICK=7605 PS2X_E4_FREEZE_TICK=7606 PS2X_E4_HEAD=4096
export PS2X_VU1_ENTRY_TRACE=$RUN/entry-$label.txt PS2X_VU1_ENTRY_TRACE_PCS=all \
  PS2X_VU1_ENTRY_TRACE_VSYNC=7605 PS2X_VU1_ENTRY_TRACE_MAXPAIRS=4000 \
  PS2X_VU1_ENTRY_TRACE_MAXLINES=400000
export PS2X_E53_VU0_LOG=1
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap 5 --script "$ROUTE"
