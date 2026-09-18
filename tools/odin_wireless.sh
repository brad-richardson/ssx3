#!/bin/zsh
# Switch the Odin to adb-over-TCP so it can charge on a wall charger while
# being driven. Run `tools/odin_wireless.sh enable` with the device on USB
# (about 15 s), then `tools/odin_wireless.sh connect` after moving it to
# the charger. `status` prints what adb sees. The TCP serial (ip:5555) is
# written to local/odin-serial and android-spike/ODIN_SERIAL for the
# briefs; tools/android_trial.py falls back to the sole attached device
# when the USB serial is absent.
#
# The USB serial is never hard-coded: ODIN_USB_SERIAL comes from the
# environment, or from the ignored local/odin-usb-serial file when unset.
set -e
ODIN_USB_SERIAL="${ODIN_USB_SERIAL:-$(cat local/odin-usb-serial 2>/dev/null || true)}"
USB="$ODIN_USB_SERIAL"
PORT=5555
SERIAL_FILE=local/odin-serial
SSD_FILE="/Volumes/Extreme SSD/android-spike/ODIN_SERIAL"
case "${1:-status}" in
  enable)
    adb -s $USB wait-for-device
    IP=$(adb -s $USB shell ip -f inet addr show wlan0 | awk '/inet /{print $2}' | cut -d/ -f1)
    [ -n "$IP" ] || { echo "no wlan0 address: is the Odin on Wi-Fi?"; exit 1; }
    adb -s $USB tcpip $PORT
    sleep 3
    printf '%s:%s\n' "$IP" "$PORT" | tee $SERIAL_FILE "$SSD_FILE"
    echo "now unplug USB, put it on the charger, then: tools/odin_wireless.sh connect"
    ;;
  connect)
    TARGET=$(cat $SERIAL_FILE)
    adb connect "$TARGET"
    sleep 2
    adb -s "$TARGET" shell 'dumpsys battery | grep -E "level|status"; getprop ro.product.model'
    ;;
  status)
    adb devices -l
    [ -f $SERIAL_FILE ] && echo "tcp serial: $(cat $SERIAL_FILE)"
    ;;
  *) echo "usage: $0 enable|connect|status"; exit 2;;
esac
