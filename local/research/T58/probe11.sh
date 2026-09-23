#!/usr/bin/env bash
# T58 probe 11: spr-dma srcs in capture emulog + state-run emulog ebw + binary liveness.
set -e
E=/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt
ES=/home/brad/pcsx2-g7/dat-t48/PCSX2/logs/emulog.txt
BIN=/home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt
echo "===== capture: spr-dma rows ====="
grep -c "via=spr-dma" $E || true
echo "===== capture: spr-dma src distribution ====="
grep "via=spr-dma" $E | grep -o "src=0x[0-9a-f]*" | sort | uniq -c | sort -rn | head -20 || true
echo "===== capture: w0=0x1b0 rows ====="
grep "value=0x1b0" $E | grep -o "via=[a-z0-9-]*" | sort | uniq -c || true
echo "===== state-run emulog: ebw/ebwlast ====="
ls -la $ES
grep -c "ebw vsync=" $ES || true
grep -c "ebwlast vsync=" $ES || true
echo "===== binary liveness ====="
sha256sum $BIN
strings $BIN | grep -c "ebw vsync=" || true
strings $BIN | grep -c "ebwlast vsync=" || true
nm -C $BIN 2>/dev/null | grep -c "t58_" || true
echo T58_PROBE11_DONE
