#!/usr/bin/env bash
# G13: extract window trace + marker lines from the capture emulog (counts-only
# emulog stays on bytesize), print sizes/shas. Runs INSIDE WSL as brad.
set -x
D=/home/brad/pcsx2-g7
E=$D/dat-g13/PCSX2/logs/emulog.txt
grep -e G12_DRAW -e G12_RASTER -e G12_VSYNC -e G12_SKIP $E > $D/g13-window-trace.txt
grep -e G13_SCAN -e G13_DUMP_QUEUED -e G13_DUMP_FALLBACK -e G8_FIRST_NONZERO $E > $D/g13-markers.txt
grep -c -e G12_DRAW $D/g13-window-trace.txt
grep -c -e G12_RASTER $D/g13-window-trace.txt
grep -c -e "G12_VSYNC field=0" $D/g13-window-trace.txt
grep -c -e "G12_VSYNC field=1" $D/g13-window-trace.txt
grep -c -e "idle=1" $D/g13-window-trace.txt
grep -c -e "idle=0" $D/g13-window-trace.txt
wc -l $D/g13-window-trace.txt $D/g13-markers.txt
ls -la $D/dat-g13/PCSX2/snaps/
sha256sum $D/dat-g13/PCSX2/snaps/*.gs $D/dat-g13/PCSX2/snaps/*.png
stat -c "%s %n" $D/g13-park.jpg $D/g13-park.xwd $E $D/g13-window-trace.txt $D/g13-markers.txt
du -sb $D/dat-g13
echo G13_EXTRACT_DONE
