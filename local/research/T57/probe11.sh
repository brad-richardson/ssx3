#!/usr/bin/env bash
# T57 probe 11: signs of life in the t57a emulog (read-only).
set -e
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
echo "===== T57 lines ====="
grep -c "vu0call vsync=" $E || true
grep -c "vif0op vsync=" $E || true
grep -c "T57_CAP" $E || true
grep -ci "t57" $E || true
echo "===== T48/T49 VU1/VIF1 lines ====="
grep -c "T48_VU1" $E || true
grep -c "T48_MODE" $E || true
grep -c "T49" $E || true
echo "===== PATHS span ====="
grep -o "T48_PATHS vsync=[0-9]*" $E | head -2
grep -o "T48_PATHS vsync=[0-9]*" $E | tail -2
echo "===== vu/VIF mentions (any) ====="
grep -ci "vu0\|vif0" $E || true
grep -o "VU0 [A-Za-z]* [A-Za-z]*" $E | sort | uniq -c | head
echo "===== VPU_STAT writes (CTC2 vu0ResetRegs evidence) ====="
grep -c "vu0ResetRegs\|VPU_STAT" $E || true
echo T57_PROBE11_DONE
