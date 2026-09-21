# I8: minimal iOS DEVICE toolchain (derived from I1 ios-simulator.toolchain.v2.cmake).
# Deltas vs the sim v2 toolchain (every one tabled in local/research/I8/REPORT.md):
#  1. CMAKE_OSX_SYSROOT iphoneos (was iphonesimulator) — the device slice.
#  2. Build-time code signing OFF (CODE_SIGNING_ALLOWED/REQUIRED NO): a device
#     .app needs a provisioning profile + entitlements, so the build stays
#     unsigned and Task 2 signs it manually with the MF1-proven mechanism
#     (wildcard profile + dev identity + entitlements plist).
# Unchanged from sim v2: CMAKE_SYSTEM_NAME iOS, CMAKE_SYSTEM_PROCESSOR arm64,
# CMAKE_OSX_ARCHITECTURES arm64, ONLY_ACTIVE_ARCH YES. No CMAKE_OSX_DEPLOYMENT_TARGET
# (same as I7: Xcode defaults to the SDK version; the iPhone runs iOS 27.0).
set(CMAKE_SYSTEM_NAME iOS)
set(CMAKE_SYSTEM_PROCESSOR arm64)
set(CMAKE_OSX_SYSROOT iphoneos)
set(CMAKE_OSX_ARCHITECTURES arm64 CACHE STRING "Target arch" FORCE)
set(CMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH YES)
set(CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED NO)
set(CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_REQUIRED NO)
