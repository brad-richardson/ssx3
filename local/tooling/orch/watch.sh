#!/bin/bash
# Exit on a new non-[orch] commit in ~/dev/ssx3, a blocked pane, or after MAX s (heartbeat).
MAX=${MAX:-1500}; start=$(date +%s)
base=$(git -C ~/dev/ssx3 rev-parse HEAD)
while :; do
  new=$(git -C ~/dev/ssx3 log --format='%h %s' $base..HEAD | grep -v '\[orch\]')
  [ -n "$new" ] && { echo "COMMIT: $new"; exit 0; }
  blk=$(herdr agent list | python3 -c '
import json,sys,os; WS=os.environ.get("WS","w2")
for a in json.load(sys.stdin)["result"]["agents"]:
    if a.get("name") and a.get("workspace_id")==WS and a["agent_status"]=="blocked": print(a["name"],"blocked")')
  [ -n "$blk" ] && { echo "$blk"; exit 0; }
  [ $(( $(date +%s) - start )) -ge $MAX ] && { echo "heartbeat ${MAX}s"; herdr agent list | python3 -c 'import json,sys,os;WS=os.environ.get("WS","w2");[print(a.get("name"),a["agent_status"]) for a in json.load(sys.stdin)["result"]["agents"] if a.get("name") and a.get("workspace_id")==WS]'; exit 0; }
  sleep 45
done
