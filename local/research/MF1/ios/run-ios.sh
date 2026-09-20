#!/bin/sh
# MF1 iOS probe: build, sign (wildcard dev profile), install, launch, pull.
# Usage: sh run-ios.sh "<device>" <outdir>
# Example: sh run-ios.sh "Brad’s iPhone" ../runs-ios/iphone
set -e
export COPYFILE_DISABLE=1
cd "$(dirname "$0")"
DEVICE="$1"; OUT="$2"
BUNDLE=com.bradrichardson.mf1probe
FP=295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1
PROFILE="/Users/bradrichardson/Library/Developer/Xcode/UserData/Provisioning Profiles/f0793278-db43-413c-9260-f120dc740845.mobileprovision"
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
APP=build/MF1Probe.app
rm -rf build; mkdir -p "$APP"
echo "== compile =="
clang -arch arm64 -isysroot "$SDK" -miphoneos-version-min=27.0 -fobjc-arc -O2 \
  -I../harness -framework UIKit -framework Metal -framework MetalFX -framework Foundation \
  -o "$APP/MF1Probe" mf1_ios_probe.m
cp Info.plist "$APP/Info.plist"
cp "$PROFILE" "$APP/embedded.mobileprovision"
cat > build/entitlements.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>application-identifier</key>
	<string>LQ3V7772Q2.$BUNDLE</string>
	<key>com.apple.developer.team-identifier</key>
	<string>LQ3V7772Q2</string>
	<key>get-task-allow</key>
	<true/>
</dict>
</plist>
EOF
echo "== sign =="
codesign --force --sign "$FP" --timestamp=none --entitlements build/entitlements.plist "$APP"
codesign --verify --strict "$APP"
echo "== install =="
xcrun devicectl device install app --device "$DEVICE" "$APP"
echo "== launch =="
xcrun devicectl device process launch --device "$DEVICE" --terminate-existing --timeout 60 "$BUNDLE" || true
echo "== poll for DONE (up to 240s) =="
mkdir -p "$OUT"
i=0
while [ "$i" -lt 48 ]; do
  if xcrun devicectl device copy from --device "$DEVICE" --source Documents/MF1/DONE \
      --destination "$OUT/DONE" --domain-type appDataContainer --domain-identifier "$BUNDLE" --quiet 2>/dev/null; then
    echo "DONE after ~$((i * 5))s"
    break
  fi
  sleep 5; i=$((i + 1))
done
[ -f "$OUT/DONE" ] || { echo "TIMEOUT waiting for DONE"; exit 1; }
echo "== pull results =="
xcrun devicectl device copy from --device "$DEVICE" --source Documents/MF1 \
  --destination "$OUT/MF1" --domain-type appDataContainer --domain-identifier "$BUNDLE" --quiet
ls -la "$OUT/MF1"
cat "$OUT/MF1/mf1-result.json"
