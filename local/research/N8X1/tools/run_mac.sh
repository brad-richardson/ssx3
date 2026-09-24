#!/bin/zsh
# usage: run_mac.sh <label> <stream> [extra env assignments...]
set -e
label=$1; stream=$2; shift 2
out=/Users/brad/dev/ssx3-work/N8X1/runs/mac-$label; mkdir -p $out/frames
slot=$(python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py claim "N8X1 mac $label" | tail -1)
echo "lease: $slot"
cd /Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp
env PS2X_GS_REPLAY_CAPTURE=$stream PS2X_GS_REPLAY_BACKEND=parallel PS2X_GS_REPLAY_STEP=1 \
  PS2X_GS_REPLAY_PPM_TICKS=${PPM_TICKS:-2050} PS2X_GS_REPLAY_PPM_DIR=$out/frames PS2X_GS_REPLAY_OUT=$out/parallel.hashes \
  PS2X_GS_REPLAY_PKTSEQ=1 GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib "$@" \
  nice ${BIN:-/Users/brad/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests} > $out/replay.log 2>&1 || echo "rc=$?"
python3 /Users/brad/dev/ssx3/local/tooling/p_lane_lease.py release $slot || true
wc -l < $out/parallel.hashes
