#!/bin/sh
# Regenerate native/patches/spike-120hz.patch: the diff of the vendored Dolphin tree
# (third_party/ModernGekko/vendor/dolphin) against its platform-patched baseline
# (pinned revision + native/patches/recompcore-platform.patch), so the spike patch applies
# on top of the stock bootstrap: `git -C third_party/ModernGekko/vendor/dolphin apply
# native/patches/spike-120hz.patch`.
set -eu
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
CORE="$ROOT/third_party/ModernGekko/vendor/dolphin"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$CORE"
# Build the baseline tree in a temporary index: HEAD + platform patch.
GIT_INDEX_FILE="$TMP/index" git read-tree HEAD
GIT_INDEX_FILE="$TMP/index" git apply --cached "$ROOT/native/patches/recompcore-platform.patch"
BASELINE=$(GIT_INDEX_FILE="$TMP/index" git write-tree)
# Make untracked files (platform-patch additions and spike additions) visible to git diff.
git ls-files --others --exclude-standard -z | xargs -0 git add -N --
git diff --no-color --no-ext-diff "$BASELINE" > "$ROOT/native/patches/spike-120hz.patch"
git diff --stat "$BASELINE"
