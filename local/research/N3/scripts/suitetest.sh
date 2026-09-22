#!/bin/bash
# N3: build + run the real env-test TU under the real MiniTest harness (host).
cd ~/n2/PS2Recomp
g++ -std=c++17 -Wall -Wextra -I ps2xTest/include -I ps2xRuntime/include ps2xTest/src/ps2_android_env_tests.cpp /tmp/n3-suitemain.cpp -o /tmp/n3-suitetest
echo "COMPILE_EXIT=$?"
/tmp/n3-suitetest
echo "RUN_EXIT=$?"
