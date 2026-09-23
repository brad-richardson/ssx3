#!/bin/zsh
# E47 boot: E46 e46g race-route boot on E47-build with windowed diagnostics.
# Usage: e47_boot.sh <label> <from> <to> <e4_arm> <wall> <snap>
# All flags are existing env gates (no code change). Each flag takes ONE
# inclusive vsync window, so SC and race are two boots.
set -eu
label=$1 from=$2 to=$3 arm=$4 wall=$5 snap=$6
W=$HOME/dev/ssx3-work
RUN=$W/E47-run
mkdir -p $RUN/e4-$label
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E47-build
export PS2X_GFX_STATS=$RUN/gfx-$label.txt PS2X_GFX_STATS_FROM=$from PS2X_GFX_STATS_TO=$to
export PS2X_VU1_TRACE=$RUN/vu1-$label.txt PS2X_VU1_TRACE_FROM=$from PS2X_VU1_TRACE_TO=$to
# E43 + MPG flush every 128 lines and SIGTERM drops the buffer: run their
# windows past $to so the lost tail is out-of-window (analysis filters vsync).
export PS2X_E43_TRACE=$RUN/e43-$label.txt PS2X_E43_TRACE_FROM=$from PS2X_E43_TRACE_TO=$((to + 60))
export PS2X_E43_H394_FROM=$from PS2X_E43_H394_TO=$to
export PS2X_VIF_MPG_LOG=$RUN/mpg-$label.txt PS2X_VIF_MPG_LOG_FROM=$from PS2X_VIF_MPG_LOG_TO=$((to + 300))
export PS2X_E4_DIR=$RUN/e4-$label PS2X_E4_ARM_TICK=$arm PS2X_E4_FREEZE_TICK=$((arm + 1))
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap $snap --script "$ROUTE"
