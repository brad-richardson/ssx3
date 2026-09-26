#!/bin/bash
# sbx_prep.sh <NAME> <GIT_URL_OR_PATH> <REV> [--depth N] — fresh clone for one sandboxed run, remotes removed.
set -eu
NAME=$1; SRC=$2; REV=$3; DEPTH=${5:-}
R=~/sbx/runs/$NAME; rm -rf "$R"; mkdir -p "$R"
if [ -n "$DEPTH" ]; then git clone -q --no-checkout --depth "$DEPTH" --branch "$REV" "$SRC" "$R/work"; git -C "$R/work" checkout -q "$REV"
else git clone -q --no-checkout "$SRC" "$R/work"; git -C "$R/work" checkout -q "$REV"; fi
for r in $(git -C "$R/work" remote); do git -C "$R/work" remote remove "$r"; done
git -C "$R/work" -c user.name=sbx -c user.email=sbx@local commit -q --allow-empty -m "sbx base $REV"
echo "prepped $R/work at $(git -C "$R/work" rev-parse --short HEAD) (base $REV)"
