#!/bin/zsh
# E50 boot 3: SC value-match store watch on the recomp's SC camera words.
# Usage: e50_valwatch_boot.sh <label> <from> <to> <values> <wall>
set -eu
label=$1 from=$2 to=$3 values=$4 wall=$5
W=$HOME/dev/ssx3-work
RUN=$W/E50/run
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E50/build
export PS2X_E50_VALWATCH=$RUN/valwatch-$label.txt PS2X_E50_VALWATCH_VALUES=$values \
  PS2X_E50_VALWATCH_FROM=$from PS2X_E50_VALWATCH_TO=$to
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap 5 --script "$ROUTE"
