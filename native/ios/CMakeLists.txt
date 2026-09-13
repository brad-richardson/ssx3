cmake_minimum_required(VERSION 3.22)
project(SSXNative LANGUAGES C CXX OBJCXX)
get_filename_component(SSX_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
set(MG "${SSX_ROOT}/third_party/ModernGekko")
set(CORE "${MG}/vendor/dolphin")
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(DOLRECOMP_ENABLE_LLVM OFF CACHE BOOL "" FORCE)
set(ENABLE_VULKAN OFF CACHE BOOL "" FORCE)
set(USE_BUNDLED_MOLTENVK OFF CACHE BOOL "" FORCE)
set(USE_SANITIZERS OFF CACHE BOOL "" FORCE)
set(MODERNGEKKO_ENABLE_DYNAMIC_MODULES OFF CACHE BOOL "" FORCE)
set(MODERNGEKKO_GAMECUBE_CONTROLLERS ON CACHE BOOL "" FORCE)
set(HAVE_PIPE2 0 CACHE BOOL "" FORCE)
foreach(DEP FMT LZ4 ZSTD ZLIB MBEDTLS CURL LIBSPNG PUGIXML MINIZIP BZIP2)
  set(USE_SYSTEM_${DEP} OFF CACHE BOOL "" FORCE)
endforeach()
add_subdirectory("${MG}" moderngekko EXCLUDE_FROM_ALL)
set(GAME_ID GXBE69 CACHE STRING "" FORCE)
set(GENERATED_DIR "${SSX_ROOT}/local/native/ssx3-module/codegen/generated" CACHE PATH "" FORCE)
set(GXRUNTIME_DIR "${CORE}/GXRuntime" CACHE PATH "" FORCE)
set(CHASSIS_ABI_DIR "${CORE}/Source/Core/Core/PowerPC/StaticRecomp" CACHE PATH "" FORCE)
set(RECOMPCORE_MODULE_STATIC ON CACHE BOOL "" FORCE)
add_subdirectory("${CORE}/module-template" game-module)

add_executable(SSXNative MACOSX_BUNDLE App.mm SessionStore.mm)
# Saved machine state must not cross incompatible frontend/runtime builds.
set(SESSION_SOURCES App.mm SessionStore.mm SessionStore.h SessionPause.h ../patches/recompcore-platform.patch
  ../patches/moderngekko-platform.patch ../dependencies.json)
set(SESSION_HASHES "")
foreach(SOURCE IN LISTS SESSION_SOURCES)
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE}")
  file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE}" SOURCE_HASH)
  string(APPEND SESSION_HASHES "${SOURCE_HASH}")
endforeach()
string(SHA256 SESSION_BUILD_ID "${SESSION_HASHES}")
target_compile_definitions(SSXNative PRIVATE SSX_SESSION_BUILD_ID="${SESSION_BUILD_ID}")
set_target_properties(SSXNative PROPERTIES
  CXX_STANDARD 23 OBJCXX_STANDARD 23
  MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist"
  MACOSX_BUNDLE_GUI_IDENTIFIER "com.brad-richardson.ssx-native"
  XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED NO)
target_compile_options(SSXNative PRIVATE -fobjc-arc)
target_link_options(SSXNative PRIVATE "LINKER:-cache_path_lto,${CMAKE_CURRENT_BINARY_DIR}/lto-cache")
target_include_directories(SSXNative PRIVATE
  "${MG}/include" "${CORE}/Source/Core" "${CORE}/GXRuntime/include"
  "${MG}/src/runtime"
  "${CORE}/Externals/fmt/fmt/include" "${CORE}/Externals/picojson"
  "${CMAKE_CURRENT_BINARY_DIR}/moderngekko/vendor/dolphin/Source/Core")
target_link_libraries(SSXNative PRIVATE moderngekko gGXBE69_recomp
  "-framework UIKit" "-framework Metal" "-framework QuartzCore"
  "-framework AVFAudio" "-framework AudioToolbox" "-framework GameController"
  "-framework CoreGraphics" "-framework CoreMotion" "-framework CoreHaptics"
  "-framework CoreVideo" "-framework CoreMedia" "-framework CoreText"
  "-framework Security" "-framework SystemConfiguration" z bz2 iconv resolv compression)
# Resources are upstream runtime support files, not game content.
add_custom_command(TARGET SSXNative POST_BUILD
  COMMAND "${CMAKE_COMMAND}" "-DOUTPUT=$<TARGET_BUNDLE_DIR:SSXNative>/build-info.json"
    "-DBUILD_ID=${SESSION_BUILD_ID}" -P "${CMAKE_CURRENT_SOURCE_DIR}/WriteBuildInfo.cmake"
  COMMAND "${CMAKE_COMMAND}" -E copy_directory
    "${CORE}/Data/Sys" "$<TARGET_BUNDLE_DIR:SSXNative>/Sys")
