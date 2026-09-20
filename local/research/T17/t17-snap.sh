#!/usr/bin/env bash
# T17: screenshot Xvfb root -> JPEG named $1 (default snap).
set -xe
export DISPLAY=:99
NAME=${1:-snap}
date -u
xwd -root -out /home/brad/pcsx2-t4/$NAME.xwd
xwdtopnm /home/brad/pcsx2-t4/$NAME.xwd | pnmtojpeg -quality=80 > /home/brad/pcsx2-t4/$NAME.jpg
ls -la /home/brad/pcsx2-t4/$NAME.*
