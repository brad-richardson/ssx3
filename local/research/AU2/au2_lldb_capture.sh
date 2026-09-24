#!/bin/zsh
# AU2 boot 2: au2_boot.sh + lldb attached to the runner; every
# ps2_stubs::sceSifSetDma entry appends 0x620 bytes of EE RAM from the SND
# tag buffer (0x512B80 + 0x2C0: tag-1 header, 384 stereo s16 frames, tag-5
# serial) to a capture file. No rebuild; the runner is ad-hoc signed.
# Usage: au2_lldb_capture.sh <label> <wall>
set -u
label=$1 wall=$2
W=$HOME/dev/ssx3-work/AU2
OUT=$W/run/pcm-$label.bin
rm -f $OUT
$HOME/dev/ssx3/local/research/AU2/au2_boot.sh $label $wall 1 > $W/wrap-$label.log 2>&1 &
bp=$!
pid=""
for i in $(seq 1 600); do
  pid=$(grep -o '"event": "boot", "pid": [0-9]*' $W/wrap-$label.log 2>/dev/null | grep -o '[0-9]*$')
  [ -n "$pid" ] && break
  grep -q REFUSE $W/wrap-$label.log 2>/dev/null && { echo refused; wait $bp; exit 2; }
  sleep 0.5
done
echo "runner pid $pid"
lldb -p $pid --batch \
  -o "br set -n 'ps2_stubs::sceSifSetDma(unsigned char*, R5900Context*, PS2Runtime*)'" \
  -o "br command add -o 'memory read --binary --force --outfile $OUT --append-outfile -c 0x620 \$x0+0x512e40' 1" \
  -o "br modify --auto-continue true 1" \
  -o "process continue" > $W/lldb-$label.log 2>&1 &
lp=$!
wait $bp; echo "boot rc=$?"
wait $lp; echo "lldb rc=$?"
ls -la $OUT
