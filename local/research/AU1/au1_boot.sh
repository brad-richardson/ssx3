#!/bin/zsh
# AU1 census boot: E51 runner (E50 build, sha 20163c2a...), E51 race route,
# PS2X_CD_READ_TRACE on (every CD read + sceCdSearchFile name->LBN), park
# snapshot (all SIF loads/binds/calls). No code changes.
# Usage: au1_boot.sh <label> <wall>
set -eu
label=$1 wall=$2
W=$HOME/dev/ssx3-work
RUN=$W/AU1/run
mkdir -p $RUN
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/E50/build
export PS2X_CD_READ_TRACE=$RUN/cdread-$label.txt
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap 30 --script "$ROUTE"
