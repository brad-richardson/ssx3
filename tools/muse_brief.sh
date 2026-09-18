#!/bin/zsh
# Launch one brief from docs/plan-120fps-2026-09-17.md as a headless muse run.
#   tools/muse_brief.sh D1        launch brief D1 in the background
#   tools/muse_brief.sh D1 stop   stop it
#   python3 tools/muse_mon.py D1  summarize its log
# Prompts live in local/muse/prompts/<ID>.md, logs in local/muse/logs/.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ID=${1:?usage: tools/muse_brief.sh <brief id> [stop]}
DIR="$ROOT/local/muse"
PROMPT="$DIR/prompts/$ID.md"
PIDFILE="$DIR/logs/$ID.pid"
mkdir -p "$DIR/logs"
if [[ "${2:-}" == "stop" ]]; then
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")"; echo "stopped $ID"; rm -f "$PIDFILE"
  else
    echo "$ID is not running"
  fi
  exit 0
fi
[[ -f "$PROMPT" ]] || { echo "no prompt file: $PROMPT" >&2; exit 1; }
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "$ID already running as pid $(cat "$PIDFILE")" >&2; exit 1
fi
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="$DIR/logs/$ID-$STAMP"
cd "$ROOT"
nohup muse exec --prompt-file "$PROMPT" --permission-profile :unrestricted \
  --reasoning-effort high --user-input-auto-resolve --json \
  > "$LOG.jsonl" 2> "$LOG.err" < /dev/null &
PID=$!
echo "$PID" > "$PIDFILE"
ln -sf "$LOG.jsonl" "$DIR/logs/$ID.jsonl"
ln -sf "$LOG.err" "$DIR/logs/$ID.err"
echo "launched $ID pid $PID"
echo "log: $LOG.jsonl"
echo "status: python3 tools/muse_mon.py $ID"
