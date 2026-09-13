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
# Keep the pinned upstream checkout untouched. Compile one local source copy
# with the authored, opt-in research hook, using core's normal build settings.
set(TRIAL_DIR "${SSX_ROOT}/native/diagnostics")
set(RUN_SOURCE "${CORE}/Source/Core/Core/PowerPC/StaticRecomp/StaticRecompCore_Run.cpp")
file(READ "${RUN_SOURCE}" RUN_CODE)
set(DISPATCH_MARKER "          const u32 runtime_dispatch_address = m_guest.pc;")
string(FIND "${RUN_CODE}" "${DISPATCH_MARKER}" DISPATCH_POSITION)
if(DISPATCH_POSITION LESS 0)
  message(FATAL_ERROR "Native trial dispatch seam changed")
endif()
string(REPLACE "namespace\n{" "#define SSX_NATIVE_TRIAL_APP 1\n#include \"${TRIAL_DIR}/native_callback_trace.h\"\n#include \"${TRIAL_DIR}/native_render_schedule.h\"\n#include \"${TRIAL_DIR}/native_pose_interpolation.h\"\nnamespace\n{" RUN_CODE "${RUN_CODE}")
string(REPLACE "${DISPATCH_MARKER}" "          NativeInterpolation::Step(m_guest);\n${DISPATCH_MARKER}" RUN_CODE "${RUN_CODE}")
set(TRIAL_SOURCE "${CMAKE_CURRENT_BINARY_DIR}/NativeTrial_Run.cpp")
file(WRITE "${TRIAL_SOURCE}" "${RUN_CODE}")
get_target_property(CORE_SOURCES core SOURCES)
list(FILTER CORE_SOURCES EXCLUDE REGEX "(^|/)StaticRecompCore_Run\\.cpp$")
set_property(TARGET core PROPERTY SOURCES "${CORE_SOURCES}")
target_sources(core PRIVATE "${TRIAL_SOURCE}")
# Observe save stages and Metal completion in local source copies. Desktop and
# upstream runtime sources retain their normal behavior and build products.
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(DIAGNOSTIC_BUILDER "${SSX_ROOT}/tools/ios_diagnostic_sources.py")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  "${CORE}/Source/Core/Core/State.cpp"
  "${CORE}/Source/Core/VideoBackends/Metal/MTLGfx.mm")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${DIAGNOSTIC_BUILDER}"
  --core "${CORE}" --header "${CMAKE_CURRENT_SOURCE_DIR}/SessionDiagnostics.h"
  --output "${CMAKE_CURRENT_BINARY_DIR}" --run "${TRIAL_SOURCE}"
  COMMAND_ERROR_IS_FATAL ANY)
get_target_property(CORE_SOURCES core SOURCES)
list(FILTER CORE_SOURCES EXCLUDE REGEX "(^|/)State\\.cpp$")
set_property(TARGET core PROPERTY SOURCES "${CORE_SOURCES}")
target_sources(core PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/DiagnosticState.cpp")
get_target_property(METAL_SOURCES videometal SOURCES)
list(FILTER METAL_SOURCES EXCLUDE REGEX "(^|/)MTLGfx\\.mm$")
set_property(TARGET videometal PROPERTY SOURCES "${METAL_SOURCES}")
target_sources(videometal PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/DiagnosticMTLGfx.mm")
set(GAME_ID GXBE69 CACHE STRING "" FORCE)
set(GENERATED_DIR "${SSX_ROOT}/local/native/ssx3-module/codegen/generated" CACHE PATH "" FORCE)
set(GXRUNTIME_DIR "${CORE}/GXRuntime" CACHE PATH "" FORCE)
set(CHASSIS_ABI_DIR "${CORE}/Source/Core/Core/PowerPC/StaticRecomp" CACHE PATH "" FORCE)
set(RECOMPCORE_MODULE_STATIC ON CACHE BOOL "" FORCE)
add_subdirectory("${CORE}/module-template" game-module)

add_executable(SSXNative MACOSX_BUNDLE App.mm SessionStore.mm SessionDiagnostics.mm)
# Saved machine state must not cross incompatible frontend/runtime builds.
set(SESSION_SOURCES App.mm CMakeLists.txt Info.plist SessionStore.mm SessionStore.h SessionPause.h
  SessionDiagnostics.h SessionDiagnostics.mm ../../tools/ios_diagnostic_sources.py
  ../diagnostics/native_callback_trace.h ../diagnostics/native_render_schedule.h
  ../diagnostics/callback_timing.h
  ../diagnostics/native_pose_interpolation.h ../diagnostics/pose_history.h
  ../diagnostics/render_deadline.h ../diagnostics/trial_control.h ../patches/recompcore-platform.patch
  ../patches/moderngekko-platform.patch ../dependencies.json)
set(SESSION_HASHES "")
foreach(SOURCE IN LISTS SESSION_SOURCES)
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE}")
  file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE}" SOURCE_HASH)
  string(APPEND SESSION_HASHES "${SOURCE_HASH}")
endforeach()
string(SHA256 SESSION_BUILD_ID "${SESSION_HASHES}")
target_compile_definitions(SSXNative PRIVATE SSX_SESSION_BUILD_ID="${SESSION_BUILD_ID}" SSX_NATIVE_TRIAL_APP=1)
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
