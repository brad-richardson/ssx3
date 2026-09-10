#!/bin/sh
# Cold-boot an image with a test-002 launcher, enter Conquer the Mountain with the first
# saved character, transport to Peak 1 > Freeride > Green Station, and hand over to
# tools/ride_route.py. Usage: green_station_ride.sh LAUNCHER OUT_DIR "x1,y1;x2,y2"
# Environment: SIGN (default 1), CAPTURE_AT (x,y). Requires local/bin from tools/macos/build.sh.
set -e
root=$(cd "$(dirname "$0")/../.." && pwd); bin="$root/local/bin"
launcher=$1; out=$2; wps=$3; mkdir -p "$out"
if pgrep -f PCSX2 >/dev/null; then echo "PCSX2 already running; stop it first" >&2; exit 1; fi
nohup "$launcher" > "$out/pcsx2-launch.log" 2>&1 &
sleep 42
"$bin/press_keys" 36; sleep 3; "$bin/press_keys" 36; sleep 4; "$bin/press_keys" 36; sleep 4
"$bin/press_keys" 125 7; sleep 4; "$bin/press_keys" 7; sleep 32
z=$(python3 -c "import sys; sys.path.insert(0,'$root/tools'); from pine import Pine; p=Pine(); print(int(p.read_floats(0x5409c0,3)[2])); p.close()")
echo "gameplay z=$z"
[ "$z" -gt 400000 ] || { echo "not in Peak 3 gameplay; aborting before menu navigation" >&2; exit 1; }
"$bin/press_keys" 36; sleep 1.5; "$bin/press_keys" 125 7; sleep 1.5; "$bin/press_keys" 125 125 7; sleep 1.5; "$bin/press_keys" 125 125 7; sleep 2
"$root/tools/macos/capture.sh" "$out/freeride-list.png" >/dev/null
"$bin/press_keys" 125 7 7
SIGN=${SIGN:-1} python3 "$root/tools/ride_route.py" "$out" "$out/ride.jsonl" "$wps"
