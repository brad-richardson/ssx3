#!/usr/bin/env bash
# run.sh <local-script> : stage to bytesize and run under WSL, foreground.
set -e
S=$1; shift
scp -q "$S" bytesize:C:/Users/bradr/t66stage/$(basename "$S")
ssh bytesize "wsl -d Ubuntu -- bash /mnt/c/Users/bradr/t66stage/$(basename "$S") $*"
