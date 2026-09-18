#!/usr/bin/env python3
"""S2 capacity table from a replay probe JSONL (works on D2's rows too).

Usage: analyze.py LABEL=path/to/probe.jsonl [LABEL=path ...]
Prints one markdown row per probe plus the per-phase breakdown. No verdicts.
"""
import json
import sys
from statistics import median


def pct(values, q):
    if not values:
        return float("nan")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


def load(path):
    rows, events = [], []
    with open(path, errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("{") or not line.endswith("}"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("event") != "replay":
                continue
            (rows if obj.get("action") == "capacity" else events).append(obj)
    return rows, events


def summarise(label, path):
    rows, events = load(path)
    by_action = {e["action"]: e for e in events}
    recorded = by_action.get("recorded", {})
    done = by_action.get("done")
    changed = by_action.get("watched_window_changed")
    wall = [r["wall_ms"] for r in rows]
    cpu = [r["cpu_ms"] for r in rows if r.get("cpu_ms", -1) >= 0]
    phases = {}
    for key in ("mem_ms", "cp_ms", "pre_ms", "run_ms", "sync_ms"):
        got = [r[key] for r in rows if key in r]
        if got:
            phases[key] = (median(got), pct(got, 0.95))
    out = {
        "label": label,
        "replays": len(rows),
        "wall_median": median(wall) if wall else None,
        "wall_p95": pct(wall, 0.95) if wall else None,
        "wall_min": min(wall) if wall else None,
        "wall_max": max(wall) if wall else None,
        "cpu_median": median(cpu) if cpu else None,
        "cpu_p95": pct(cpu, 0.95) if cpu else None,
        "frame_bytes": recorded.get("bytes"),
        "memory_updates": recorded.get("memory_updates"),
        "done": bool(done),
        "watched_window_changed": bool(changed),
        "seq_wall_ms": (done or changed or {}).get("detail", ""),
        "restored_detail": by_action.get("restored", {}).get("detail", ""),
        "events": [e["action"] for e in events],
        "phases": phases,
    }
    return out


def fmt(value, nd=3):
    return "n/a" if value is None else f"{value:.{nd}f}"


def main():
    results = []
    for arg in sys.argv[1:]:
        label, _, path = arg.partition("=")
        results.append(summarise(label or path, path))
    print("| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) "
          "| Frame B / updates | done | seq wall |")
    print("| --- | ---: | --- | --- | --- | :-: | --- |")
    for r in results:
        print(f"| {r['label']} | {r['replays']} | "
              f"{fmt(r['wall_median'])} / {fmt(r['wall_p95'])} / "
              f"{fmt(r['wall_min'])} / {fmt(r['wall_max'])} | "
              f"{fmt(r['cpu_median'])} / {fmt(r['cpu_p95'])} | "
              f"{r['frame_bytes']} / {r['memory_updates']} | "
              f"{'YES' if r['done'] else 'no'} | {r['seq_wall_ms']} |")
    print()
    print("| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) "
          "| sync_ms med | run_ms p95 |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in results:
        p = r["phases"]
        cell = lambda k, i=0: fmt(p[k][i]) if k in p else "n/a"  # noqa: E731
        print(f"| {r['label']} | {cell('mem_ms')} | {cell('cp_ms')} | {cell('pre_ms')} "
              f"| {cell('run_ms')} | {cell('sync_ms')} | {cell('run_ms', 1)} |")
    print()
    for r in results:
        print(f"{r['label']}: events={r['events']}")
        if r["restored_detail"]:
            print(f"{r['label']}: restored detail = {r['restored_detail']}")
        if r["watched_window_changed"]:
            print(f"{r['label']}: WATCHED WINDOW CHANGED")


if __name__ == "__main__":
    main()
