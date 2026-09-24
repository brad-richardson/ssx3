#!/bin/zsh
# AU3 diagnostic boots. Usage: au3_boot.sh <label> <0|1> <wall-seconds>
set -eu
label=$1
sound=$2
wall=$3
run=$HOME/dev/ssx3-work/AU3/run
mkdir -p "$run"
export E46_RUN_DIR=$run
export E46_BUILD_DIR=$HOME/dev/ssx3-work/AU3/build
export PS2X_SOUND=$sound
export PS2X_SND_LOG=$run/snd-$label.txt
if [[ $sound == 1 ]]; then
  export PS2X_SOUND_WAV=$run/au3-host-stream.wav
else
  unset PS2X_SOUND_WAV
fi
route='10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000'
exec nice -n 5 python3 $HOME/dev/ssx3/local/research/E46/e46_boot.py \
  --label "$label" --wall "$wall" --snap 30 --script "$route"
