#!/bin/zsh
# E50 boot: E47 race route on the E50 build with the E50 taps.
# Usage: e50_boot.sh <label> <from> <to> <e4_arm> <entry_vsync> <wall> <snap> [gfx_from]
# gfx stats (with E50 dN_scr + pcs fields) over from..to; E4 arm/freeze
# at arm/arm+1 with the first 4096 draws kept (PS2X_E4_HEAD); VU1 entry
# trace in all-PCs mode from entry_vsync (first 16 distinct startPCs,
# 4000 pairs each, VF/VI regs + vumem + packet log incl. UNPACK src=).
set -eu
label=$1 from=$2 to=$3 arm=$4 entry=$5 wall=$6 snap=$7 gfx_from=${8:-$2}
W=$HOME/dev/ssx3-work
RUN=$W/E50/run
mkdir -p $RUN/e4-$label
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E50/build
export PS2X_GFX_STATS=$RUN/gfx-$label.txt PS2X_GFX_STATS_FROM=$gfx_from PS2X_GFX_STATS_TO=$to
export PS2X_VIF_MPG_LOG=$RUN/mpg-$label.txt PS2X_VIF_MPG_LOG_FROM=$from PS2X_VIF_MPG_LOG_TO=$((to + 300))
export PS2X_E4_DIR=$RUN/e4-$label PS2X_E4_ARM_TICK=$arm PS2X_E4_FREEZE_TICK=$((arm + 1)) PS2X_E4_HEAD=4096
export PS2X_VU1_ENTRY_TRACE=$RUN/entry-$label.txt PS2X_VU1_ENTRY_TRACE_PCS=all \
  PS2X_VU1_ENTRY_TRACE_VSYNC=$entry PS2X_VU1_ENTRY_TRACE_MAXPAIRS=4000 \
  PS2X_VU1_ENTRY_TRACE_MAXLINES=400000
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap $snap --script "$ROUTE"
