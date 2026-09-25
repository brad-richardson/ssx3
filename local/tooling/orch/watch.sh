#!/bin/bash
# watch.sh — the orchestrator's wake-up. Exits (and so re-invokes the orchestrator) on:
#   COMMIT   a new non-[orch] commit in ~/dev/ssx3
#   BLOCKED  a pane whose agent status is "blocked" (permission prompt etc.)
#   STOPPED  a worker that was working when the watch started and has been idle/done for GRACE s
#            (default 600) with no new commit (finished without committing, or died)
#   ERROR    a worker pane showing a known failure string (model/memory/rate-limit/API errors)
#   STALL    a "working" pane whose visible output hasn't changed for STALL seconds (hung)
#   heartbeat after MAX seconds, listing every pane's state
# Env: WS (workspace, default w2), MAX (default 1500 s), STALL (default 1200 s),
#      WATCH_IGNORE_AGENT (comma list; the orchestrator's own pane name is always ignored).
MAX=${MAX:-1500}; STALL=${STALL:-1200}; GRACE=${GRACE:-600}; start=$(date +%s)
base=$(git -C ~/dev/ssx3 rev-parse HEAD)
state=$(mktemp -d "${TMPDIR:-/tmp}/watch.XXXXXX")
export WS=${WS:-w2} STALL GRACE state
export WATCH_IGNORE_AGENT="${WATCH_IGNORE_AGENT:-orch-sol},ssx3_opus_orchestrator"
while :; do
  new=$(git -C ~/dev/ssx3 log --format='%h %s' $base..HEAD | grep -v '\[orch\]')
  [ -n "$new" ] && { echo "COMMIT: $new"; rm -rf "$state"; exit 0; }
  ev=$(herdr agent list | python3 -c '
import json, sys, os, subprocess, hashlib, time
WS = os.environ["WS"]; ign = set(os.environ["WATCH_IGNORE_AGENT"].split(","))
st = os.environ["state"]; stall = int(os.environ["STALL"]); grace = int(os.environ["GRACE"]); now = time.time()
# Real error output only (JSON error fields, API error lines). Each pattern is built from two
# halves so this source, if a worker opens it, cannot match itself.
ERR = tuple(x + y for x, y in (("\"code\":", "\"prefill_memory_aborted\""), ("\"type\":", "\"overloaded_error\""),
            ("\"type\":", "\"rate_limit_error\""), ("API Error", ": "), ("\"code\":", "\"insufficient_quota\""),
            ("Rate limit", " reached")))
for a in json.load(sys.stdin)["result"]["agents"]:
    n = a.get("name")
    if not n or n in ign or a.get("workspace_id") != WS: continue
    s = a["agent_status"]
    first = os.path.join(st, n + ".first")
    if not os.path.exists(first): open(first, "w").write(s)
    if s == "blocked": print(n, "BLOCKED"); continue
    idlef = os.path.join(st, n + ".idle")
    if open(first).read() == "working" and s in ("idle", "done"):
        # workers often end a turn while a backgrounded wait runs; only report after a grace period
        if not os.path.exists(idlef): open(idlef, "w").write(str(now))
        if now - float(open(idlef).read()) >= grace: print(n, "STOPPED (idle", int(now - float(open(idlef).read())), "s, no commit)")
        continue
    if os.path.exists(idlef): os.remove(idlef)
    try: out = subprocess.run(["herdr", "agent", "read", n], capture_output=True, text=True, timeout=20).stdout
    except Exception: continue
    tail = "\n".join(out.splitlines()[-40:])
    hit = [e for e in ERR if e in tail]
    if hit:
        # report an error once: only when this pane shows more occurrences than last reported
        seen = os.path.join(os.path.expanduser("~/dev/ssx3/local/.watch-errors"), n)
        os.makedirs(os.path.dirname(seen), exist_ok=True)
        cnt = sum(out.count(e) for e in ERR)
        prev = int(open(seen).read()) if os.path.exists(seen) else 0
        if cnt > prev:
            open(seen, "w").write(str(cnt)); print(n, "ERROR:", hit[0]); continue
    if s != "working": continue
    h = hashlib.sha1(tail.encode()).hexdigest(); f = os.path.join(st, n + ".hash")
    old = open(f).read().split() if os.path.exists(f) else []
    if not old or old[0] != h: open(f, "w").write(h + " " + str(now))
    elif now - float(old[1]) >= stall: print(n, "STALL (no output change for", int(now - float(old[1])), "s)")
')
  [ -n "$ev" ] && { echo "$ev"; rm -rf "$state"; exit 0; }
  [ $(( $(date +%s) - start )) -ge $MAX ] && { echo "heartbeat ${MAX}s"; herdr agent list | python3 -c 'import json,sys,os;WS=os.environ.get("WS","w2");[print(a.get("name"),a["agent_status"]) for a in json.load(sys.stdin)["result"]["agents"] if a.get("name") and a.get("workspace_id")==WS]'; rm -rf "$state"; exit 0; }
  sleep 45
done
