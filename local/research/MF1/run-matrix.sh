#!/bin/sh
# MF1 run matrix driver. Usage: sh run-matrix.sh
# Builds the harness, runs the motion x UI x resolution x colorfmt matrix, analyzes.
set -e
export COPYFILE_DISABLE=1
cd "$(dirname "$0")"
HARNESS=harness/mf1_interp
clang -fobjc-arc -framework Metal -framework MetalFX -framework Foundation \
  -o "$HARNESS" harness/mf1_interp.m
echo "build ok: $HARNESS"
mkdir -p runs
run_one() {
  name="$1"; w="$2"; h="$3"; motion="$4"; ui="$5"; colorfmt="${6:-bgra8}"
  d="runs/$name"
  echo "=== $name (${w}x${h} motion=$motion ui=$ui colorfmt=$colorfmt) ==="
  out=$("./$HARNESS" --out "$d" --width "$w" --height "$h" --iters 30 \
    --motion "$motion" --ui "$ui" --colorfmt "$colorfmt")
  echo "$out"
  echo "$out" | python3 -c "
import json,sys
o = json.loads(sys.stdin.read())
o.update(motion='$motion', ui='$ui', colorfmt='$colorfmt', name='$name')
open('$d/run.json','w').write(json.dumps(o, indent=2) + '\n')
"
}
# Core matrix at 720p BGRA8: motion fallback x UI handling
run_one res720-exact-none   1280 720 exact none
run_one res720-zero-none    1280 720 zero none
run_one res720-uniform-none 1280 720 uniform none
run_one res720-exact-comp   1280 720 exact composited
run_one res720-exact-sep    1280 720 exact separate
# Resolution sweep (exact motion, no UI, BGRA8)
run_one res528-exact-none   640 528 exact none
run_one res1080-exact-none  1920 1080 exact none
# Color format arm (exact motion, no UI, 720p)
run_one res720-exact-none-16f 1280 720 exact none rgba16f
python3 analyze.py runs/res*
