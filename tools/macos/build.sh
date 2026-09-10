#!/bin/sh
# Compile the macOS input/capture helpers into local/bin (ignored by Git).
set -e
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
mkdir -p "$root/local/bin" "$root/local/swift-cache"
for name in keyd press_keys window_id; do
  swiftc -module-cache-path "$root/local/swift-cache" -O -o "$root/local/bin/$name" "$here/$name.swift"
done
echo "built: $root/local/bin"
