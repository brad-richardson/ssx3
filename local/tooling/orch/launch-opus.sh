#!/bin/bash
# launch-opus.sh <ID> <prompt> — Claude Opus worker pane (quota fallback)
ID=$1; PROMPT=$2; name=$(echo "$ID" | tr A-Z a-z)
pane=$(herdr tab create --workspace ${WS:-w2} --cwd ~/dev/ssx3 --label "$ID" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["root_pane"]["pane_id"])')
sleep 4; herdr agent start "$name" --kind claude --pane "$pane" --timeout 120000 -- --model opus --permission-mode auto >/dev/null || { echo "$ID start failed"; exit 1; }
herdr agent prompt "$name" "$PROMPT Commit trailer for this brief: 'Orchestrated-By: Claude Code' (not Muse Code). You are a worker on a brief: follow ~/dev/AGENTS.md worker rules." --wait --until working --timeout 30000 | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"]["agent"];print(r["name"],r["pane_id"],r["agent_status"])'
