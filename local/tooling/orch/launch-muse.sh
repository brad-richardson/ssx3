#!/bin/bash
# launch-muse.sh <ID> <prompt> — muse worker pane (quota out until 2026-09-26)
ID=$1; PROMPT=$2; name=$(echo "$ID" | tr A-Z a-z)
pane=$(herdr tab create --workspace ${WS:-w2} --cwd ~/dev/ssx3 --label "$ID" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["root_pane"]["pane_id"])')
sleep 4; herdr agent start "$name" --kind muse --pane "$pane" --timeout 120000 -- --yolo >/dev/null || { echo "$ID start failed"; exit 1; }
herdr agent prompt "$name" "$PROMPT" --wait --until working --timeout 20000 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"]["agent"];print(r["name"],r["pane_id"],r["agent_status"])'
