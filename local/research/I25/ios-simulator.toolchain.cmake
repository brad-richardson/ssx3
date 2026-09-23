# I1 spike: minimal iOS Simulator toolchain v2 (written for this spike).
# v2 adds CMAKE_SYSTEM_PROCESSOR (Xcode generator leaves it unset, which
# silently disabled the repo's sse2neon-on-ARM FetchContent block).
set(CMAKE_SYSTEM_NAME iOS)
set(CMAKE_SYSTEM_PROCESSOR arm64)
set(CMAKE_OSX_SYSROOT iphonesimulator)
set(CMAKE_OSX_ARCHITECTURES arm64 CACHE STRING "Target arch" FORCE)
set(CMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH YES)
