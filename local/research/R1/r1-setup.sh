#!/usr/bin/env bash
# R1 setup (runs INSIDE WSL as brad): snapshot T4 datapath to r1 (T4 dat untouched).
set -x
date -u
rm -rf /home/brad/pcsx2-r1/dat /home/brad/pcsx2-r1/logs
mkdir -p /home/brad/pcsx2-r1/logs
cp -a /home/brad/pcsx2-t4/dat /home/brad/pcsx2-r1/dat || { echo R1_FAIL:DATCP; exit 1; }
ls -la /home/brad/pcsx2-r1/dat/PCSX2/bios
ls -la /home/brad/pcsx2-r1/dat/PCSX2/logs
grep -n EnableEE /home/brad/pcsx2-r1/dat/PCSX2/inis/PCSX2.ini
grep -n -A8 EmuCore.TraceLog /home/brad/pcsx2-r1/dat/PCSX2/inis/PCSX2.ini
grep -n Cross /home/brad/pcsx2-r1/dat/PCSX2/inis/PCSX2.ini
echo R1_SETUP_DONE
