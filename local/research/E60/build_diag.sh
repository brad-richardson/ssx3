#!/bin/zsh
set -eu
W=/Users/brad/dev/ssx3-work/E60
D=/Users/brad/dev/ssx3-work/E50/build/_deps
cmake -S $W/PS2Recomp -B $W/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF \
  -DPS2X_GAME_CODEGEN_DIR=$W/codegen \
  -DFETCHCONTENT_SOURCE_DIR_ELFIO=$D/elfio-src \
  -DFETCHCONTENT_SOURCE_DIR_FMT=$D/fmt-src \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI_CLUB=$D/imgui_club-src \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI_COLORTEXTEDIT=$D/imgui_colortextedit-src \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI_FILE_DIALOG=$D/imgui_file_dialog-src \
  -DFETCHCONTENT_SOURCE_DIR_IMGUI=$D/imgui-src \
  -DFETCHCONTENT_SOURCE_DIR_LIBDWARF=$D/libdwarf-src \
  -DFETCHCONTENT_SOURCE_DIR_NLOHMANN_JSON=$D/nlohmann_json-src \
  -DFETCHCONTENT_SOURCE_DIR_RABBITIZER=$D/rabbitizer-src \
  -DFETCHCONTENT_SOURCE_DIR_RAYLIB=$D/raylib-src \
  -DFETCHCONTENT_SOURCE_DIR_RLIMGUI=$D/rlimgui-src \
  -DFETCHCONTENT_SOURCE_DIR_SDL2=$D/sdl2-src \
  -DFETCHCONTENT_SOURCE_DIR_SSE2NEON=$D/sse2neon-src \
  -DFETCHCONTENT_SOURCE_DIR_TOML11=$D/toml11-src > $W/cmake.log 2>&1
cmake --build $W/build --target ps2EntryRunner -j8 > $W/build.log 2>&1
