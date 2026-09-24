#!/usr/bin/env bash
# N9 Part 2 codegen-in-graph refinement (read-only). Adapted from
# N8D7M12P6M6R/codegen_graph.sh (root n9; ARM dir discovered, not hardcoded).
set -euo pipefail
root=/home/brad/n9
arm=$(dirname "$(ls "$root/PS2Recomp/android/app/.cxx"/RelWithDebInfo/*/arm64-v8a/CMakeCache.txt | head -1)")
echo "ARM_DIR=$arm"
cf="$arm/ps2xRuntime/CMakeFiles"
echo "== unity files incl. codegen sources (sample) =="
grep -rl "codegen-ssx3" "$cf" --include="unity_*.cxx" > /tmp/n9_unity.txt || true
head -3 /tmp/n9_unity.txt || true
echo "== count unity files incl. codegen =="
wc -l < /tmp/n9_unity.txt
echo "== register_functions.cpp includes in unity files =="
grep -rn "codegen-ssx3/register_functions.cpp" "$cf" --include="unity_*.cxx" > /tmp/n9_reg.txt || true
head -3 /tmp/n9_reg.txt || true
echo "== sub_ sample includes =="
grep -rh "codegen-ssx3/sub_" "$cf" --include="unity_*.cxx" > /tmp/n9_sub.txt || true
head -3 /tmp/n9_sub.txt || true
echo "== distinct codegen files included across unity batches =="
grep -rho "codegen-ssx3/[A-Za-z0-9_./-]*\.cpp" "$cf" --include="unity_*.cxx" > /tmp/n9_all.txt || true
sort -u /tmp/n9_all.txt | wc -l
echo "== game source count message in build log =="
grep -a -o "PS2X_GAME_SOURCE_COUNT[ =:]*[0-9]*" "$root/assembleRelease.log" || echo "no PS2X_GAME_SOURCE_COUNT line"
grep -a -oi "game[_ ]sources\?[^a-z]*[0-9]*" "$root/assembleRelease.log" | head -5 || echo "no game-sources line"
echo "== build log: BUILD lines =="
grep -a -c "BUILD SUCCESSFUL" "$root/assembleRelease.log"
grep -a -c "FAILED" "$root/assembleRelease.log" || echo "no FAILED lines"
