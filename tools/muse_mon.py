#!/usr/bin/env python3
"""Summarize a muse exec --json log.

  python3 tools/muse_mon.py D1 [N]   (brief id -> local/muse/logs/D1.jsonl) or a path
"""
import json, sys, datetime, collections
import os
arg = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = arg if os.path.exists(arg) else os.path.join(root, "local", "muse", "logs", arg + ".jsonl")
rows = []
for line in open(path):
    line = line.strip()
    if not line: continue
    try: rows.append(json.loads(line))
    except Exception: pass
kinds = collections.Counter(r.get('payload_type') for r in rows)
first = rows[0].get('recorded_at') if rows else None; last = rows[-1].get('recorded_at') if rows else None
def ts(x):
    try: return datetime.datetime.fromtimestamp(x/1e6).strftime('%H:%M:%S')
    except Exception: return '?'
print(f"events={len(rows)} first={ts(first)} last={ts(last)}")
print("kinds:", ', '.join(f"{k}={v}" for k, v in kinds.most_common(8)))
cmds, texts, fails, status = [], [], [], []
for r in rows:
    pt = r.get('payload_type') or ''; pl = r.get('payload') or {}
    ev = pl.get('event') if isinstance(pl.get('event'), dict) else {}
    if pt == 'task.lifecycle.output':
        chunk = ev.get('chunk') or pl.get('chunk') or ''
        try:
            o = json.loads(chunk); cmds.append((ts(r.get('recorded_at')), o.get('description') or o.get('command','')[:90], o.get('exit_code'), (o.get('output') or '')[-160:].replace('\n',' | ')))
        except Exception:
            cmds.append((ts(r.get('recorded_at')), str(chunk)[:120].replace('\n',' | '), None, ''))
    if 'assistant_message' in pt or ev.get('kind') == 'assistant_message_committed':
        texts.append((ts(r.get('recorded_at')), (ev.get('text') or pl.get('text') or '')[:700]))
    if 'fail' in pt or 'error' in pt or ev.get('kind') in ('failed', 'cancelled'):
        fails.append((ts(r.get('recorded_at')), pt, json.dumps(pl)[:200]))
    if pt == 'task.lifecycle.status':
        status.append((ts(r.get('recorded_at')), (ev.get('message') or pl.get('message') or '')[:120]))
print(f"--- last {n} tool commands ({len(cmds)} total)")
for c in cmds[-n:]: print(" ", c[0], "|", c[1], "| exit", c[2], "|", c[3])
print(f"--- assistant messages ({len(texts)})")
for t in texts[-3:]: print(" ", t[0], t[1].replace('\n', ' ')[:700])
print(f"--- failures ({len(fails)})")
for f in fails[-5:]: print(" ", f)
print(f"--- last status: {status[-1] if status else None}")
