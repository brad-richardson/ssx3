#!/bin/zsh
# GV1: the one allowed microbenchmark. Claims one mini slot (blocks exclusive speed holds), runs, releases.
set -u
cd ~/dev/ssx3-work/GV1
OUT=~/dev/ssx3-work/GV1/receipts; mkdir -p $OUT
LEASE=~/dev/ssx3/local/tooling
SLOT=$(cd $LEASE && python3 -c "from p_lane_lease import claim; s=claim('GV1-bench'); print(s if s else '')")
if [ -z "$SLOT" ]; then echo "lease busy"; exit 3; fi
echo "claimed $SLOT at $(date +%T)"; uptime
{
  echo "== $(date) host $(hostname) $(sysctl -n machdep.cpu.brand_string)"
  uptime
  echo "== sha256"; shasum -a 256 bench/fmac_core.glsl bench/test.comp bench/bench.comp bench/host.cpp bench/*.spv ref/gen_cases.cpp ref/gen_cases
  echo "== CPU reference (real VR4 core, fork b97b241 VU sources) + CPU throughput"
  ./ref/gen_cases 1000000 ref/cases.bin
  echo "== GPU bit-exact test"
  ./bench/host test bench/test.spv ref/cases.bin
  echo "== GPU throughput: vertex-parallel (32768 threads x 64 transforms) and program-parallel (1024 threads x 200)"
  for m in 0 1 2; do ./bench/host bench bench/bench$m.spv 32768 64 7; done
  for m in 0 1 2; do ./bench/host bench bench/bench$m.spv 1024 200 7; done
  echo "== saturation: 262144 threads x 64"
  for m in 0 1 2; do ./bench/host bench bench/bench$m.spv 262144 64 5; done
  echo "== dispatch floor: 64 threads x 1"
  ./bench/host bench bench/bench0.spv 64 1 20
  uptime
} 2>&1 | tee $OUT/bench-$(date +%H%M).txt
(cd $LEASE && python3 -c "from p_lane_lease import release; release($SLOT)" ) && echo "released at $(date +%T)"
