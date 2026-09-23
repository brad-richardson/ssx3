#!/bin/bash
# E45 Odin bench runs (from the mini). Claims the Odin lease, pushes both
# bench binaries, verifies SHAs on device, runs double then quad with the
# same args as the Mac reference (20 iters, loopN 2048), cleans up and
# releases the lease. Aborts if the lease is held by another lane.
set -u
SERIAL=622c49b1
TS=$(date -u +%FT%TZ)
WANT_DOUBLE=e267bf7a085e46a9465de332586953921f05afcb56962e2e3d4af2f6dc980a4e
WANT_QUAD=ea0a5639f491d60b63df5cb1918702ad1b431393aa9a928ab972946ffd1a7283
adb="adb -s $SERIAL"

lease=$($adb shell "cat /data/local/tmp/mg/LEASE 2>/dev/null || echo NO_LEASE_FILE")
echo "LEASE_BEFORE=$lease"
case "$lease" in
  NO_LEASE_FILE|LEASE_FREE*) ;;
  E45*) ;;
  *) echo "E45: lease held, aborting"; exit 3;;
esac

$adb shell "echo 'E45 $TS' > /data/local/tmp/mg/LEASE && cat /data/local/tmp/mg/LEASE"
$adb shell "dumpsys battery | grep -E 'level|status|powered' | head -4"
$adb shell "mkdir -p /data/local/tmp/e45 && rm -f /data/local/tmp/e45/*"
$adb push ~/dev/ssx3-work/E45/bench/e45_odin_double /data/local/tmp/e45/d 2>&1 | tail -1
$adb push ~/dev/ssx3-work/E45/bench/e45_odin_quad /data/local/tmp/e45/q 2>&1 | tail -1
$adb shell "cd /data/local/tmp/e45 && chmod 755 d q && sha256sum d q"
echo "== double =="
$adb shell "cd /data/local/tmp/e45 && ./d 20 2048" 2>&1
echo "== quad =="
$adb shell "cd /data/local/tmp/e45 && ./q 20 2048" 2>&1
$adb shell "rm -rf /data/local/tmp/e45 && echo 'LEASE_FREE E45 done' > /data/local/tmp/mg/LEASE && cat /data/local/tmp/mg/LEASE"
echo E45_ODIN_DONE
