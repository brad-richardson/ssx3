#!/bin/sh
# Run one measurement: measure.sh PROFILE SECONDS [--no-replay] with SSX3_* variables set by the caller.
# Launches the Metal runtime with a pipe controller, attaches the Snow Jam smoke sequence, and
# prints the log path it wrote. Run from the repository root.
set -e
profile=$1; seconds=$2; replay=${3:-replay}
python3 tools/native_gamecube.py run --profile "$profile" --seconds "$seconds" --pipe-controller &
runner=$!
sleep 4
if [ "$replay" = "replay" ]; then
  python3 tools/native_replay.py --profile "$profile" --sequence native/ios/snow-jam-smoke.json &
fi
wait $runner || true
