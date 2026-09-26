#!/bin/bash
# sbx_run.sh <NAME> <MODEL> <BRIEF_FILE> — run one opencode worker on an untrusted model, sandboxed.
# Runs on bradflix. Before: put the task's clone at ~/sbx/runs/<NAME>/work (no git remotes, no secrets);
# sbx_prep.sh does that. The container gets: /work (that clone, rw), a tmpfs home, the brief, no host
# mounts beyond those, no capabilities, no new privileges, a CPU/memory/pid cap, and network only via
# the allowlisting proxy on the internal network `sbx-int` (opencode.ai / models.dev over HTTPS).
# Output: ~/sbx/runs/<NAME>/{out.log,rc,diff.patch,status.txt}. No herdr, no devices, no ssh.
set -u
NAME=$1; MODEL=$2; BRIEF=$3
R=~/sbx/runs/$NAME; W=$R/work
[ -d "$W" ] || { echo "no $W (run sbx_prep.sh first)"; exit 2; }
[ -z "$(git -C "$W" remote 2>/dev/null)" ] || { echo "refusing: $W has git remotes"; exit 2; }
cp "$BRIEF" "$R/brief.md"
docker network inspect sbx-int >/dev/null 2>&1 || docker network create --internal sbx-int >/dev/null
docker ps --format '{{.Names}}' | grep -qx sbx-proxy || ~/sbx/proxy_up.sh
docker run --rm --name "sbx-$NAME" --network sbx-int \
  --user 1000:1000 --cap-drop ALL --security-opt no-new-privileges \
  --cpus "${SBX_CPUS:-6}" --memory "${SBX_MEM:-12g}" --pids-limit 1024 \
  --tmpfs /home/sbx:rw,exec,size=4g -e HOME=/home/sbx \
  -e HTTPS_PROXY=http://sbx-proxy:3128 -e HTTP_PROXY=http://sbx-proxy:3128 \
  -e https_proxy=http://sbx-proxy:3128 -e http_proxy=http://sbx-proxy:3128 -e NO_PROXY=localhost,127.0.0.1 \
  -e OPENCODE_CONFIG_CONTENT='{"permission":"allow","share":"disabled","autoupdate":false}' \
  -v "$W":/work -v "$R/brief.md":/brief.md:ro -w /work \
  ssx3-sbx timeout "${SBX_TIMEOUT:-7200}" opencode run --auto -m "$MODEL" \
    "Your brief is /brief.md. Read it and execute it. Work only inside /work." \
  > "$R/out.log" 2>&1
echo $? > "$R/rc"
git -C "$W" add -A >/dev/null 2>&1; git -C "$W" diff --cached --stat > "$R/status.txt"; git -C "$W" diff --cached > "$R/diff.patch"
git -C "$W" reset -q >/dev/null 2>&1
echo "rc=$(cat "$R/rc") $(tail -1 "$R/status.txt")"
