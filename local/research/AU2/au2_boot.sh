#!/bin/zsh
# AU2 spike boot: au2-snd runner, E51 race route, PS2X_SND_TICK on
# (IOP tick delivered to the EE SND cid-1 handler), SND log + dumps,
# PS2X_CD_READ_TRACE for the music-read observable.
# Usage: au2_boot.sh <label> <wall> [ticks-per-vblank]
set -eu
label=$1 wall=$2 tpv=${3:-1}
W=$HOME/dev/ssx3-work
RUN=$W/AU2/run
mkdir -p $RUN/dump-$label
export E46_RUN_DIR=$RUN E46_BUILD_DIR=$W/AU2/build
export PS2X_CD_READ_TRACE=$RUN/cdread-$label.txt
export PS2X_SND_TICK=$tpv PS2X_SND_LOG=$RUN/snd-$label.txt PS2X_SND_DUMP_DIR=$RUN/dump-$label
ROUTE="10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000"
exec nice -n 5 python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py --label $label \
  --wall $wall --snap 30 --script "$ROUTE"
