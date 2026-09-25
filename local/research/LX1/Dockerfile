# LX1 builder/runner image: Ubuntu 24.04 + clang + X11/GL dev + xvfb + Vulkan.
# Build: docker build -t ssx3-lx1 -f Dockerfile .
# Run: bind-mount ~/dev/ssx3-work/LX1 at /work, --user <brad uid:gid>.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  clang lld cmake ninja-build pkg-config python3 git ca-certificates \
  libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev \
  libgl1-mesa-dev libglu1-mesa-dev libasound2-dev \
  libwayland-dev libxkbcommon-dev \
  libavcodec-dev libavformat-dev libavutil-dev libswresample-dev libswscale-dev \
  xvfb vulkan-tools mesa-vulkan-drivers libvulkan1 \
  && rm -rf /var/lib/apt/lists/*
