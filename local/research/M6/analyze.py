#!/usr/bin/env python3
"""M5 replay-fidelity table from probe JSONLs (superset of S2 analyze.py).

Usage: analyze.py LABEL=path/to/probe.jsonl [LABEL=path ...]
Prints S2's capacity tables unchanged, then M5 sections: XFB fidelity,
side-effect counter summaries, scratch/live-XFB and continuation lines.
Missing keys (earlier steps) print as n/a. No verdicts.
"""
import json
import re
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


def kv(detail, key, default=None):
    m = re.search(r"(?:^|\s)%s=([^\s]+)" % re.escape(key), detail or "")
    return m.group(1) if m else default


def summarise(label, path):
    rows, events = load(path)
    by_action = {}
    for e in events:
        by_action.setdefault(e["action"], []).append(e)
    first = lambda a: (by_action.get(a) or [{}])[0]
    recorded = first("recorded")
    done = first("done")
    changed = first("watched_window_changed")
    wall = [r["wall_ms"] for r in rows]
    cpu = [r["cpu_ms"] for r in rows if r.get("cpu_ms", -1) >= 0]
    phases = {}
    for key in ("mem_ms", "cp_ms", "pre_ms", "run_ms", "sync_ms"):
        got = [r[key] for r in rows if key in r]
        if got:
            phases[key] = (median(got), pct(got, 0.95))
    deltas = {}
    for key in ("dtex", "dpend", "dframe", "dafter", "dafter_live", "dpres", "dimx",
                "pediff", "vidiff"):
        got = [r[key] for r in rows if key in r]
        if got:
            deltas[key] = (min(got), max(got))
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
        "restored_detail": first("restored").get("detail", ""),
        "counters_detail": first("counters_summary").get("detail", ""),
        "events": [e["action"] for e in events],
        "phases": phases,
        "deltas": deltas,
        "xfb_equal": sum(1 for r in rows if r.get("xfb_equal") == 1),
        "xfb_scratch": sum(1 for r in rows if r.get("xfb_scratch") == 1),
        "has_xfb": any("xfb_equal" in r for r in rows),
        "has_scratch": any("xfb_scratch" in r for r in rows),
        "record_starts": [e.get("detail", "") for e in by_action.get("record_start", [])],
        "resume_xfbs": [e.get("detail", "") for e in by_action.get("resume_xfb", [])],
        "present_traces": [e.get("detail", "") for e in by_action.get("present_trace", [])],
        "record_flag_set": bool(by_action.get("record_flag_set")),
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
    print("| Arm | xfb_copies | efb_total (non-XFB) | xfb range (addr, bytes) | ref_ok | "
          "scratch_ok (addr, patched) | xfb_equal | xfb_equal_scratch | live_xfb_untouched |")
    print("| --- | ---: | --- | --- | :-: | --- | --- | --- | :-: |")
    for r in results:
        rd, dd = r["restored_detail"], r["seq_wall_ms"]
        total, xfb = kv(rd, 'efb_total'), kv(rd, 'xfb_copies')
        try:
            nonx = str(int(total) - int(xfb))
        except (TypeError, ValueError):
            nonx = "n/a"
        print(f"| {r['label']} | {xfb or 'n/a'} | "
              f"{total or 'n/a'} ({nonx}) | "
              f"{kv(rd, 'xfb_addr', 'n/a')}, {kv(rd, 'xfb_bytes', 'n/a')} B | "
              f"{kv(rd, 'xfb_ref_ok', 'n/a')} | "
              f"{kv(rd, 'xfb_scratch_ok', 'n/a')} "
              f"({kv(rd, 'xfb_scratch_addr', 'n/a')}, {kv(rd, 'xfb_patch_n', 'n/a')}) | "
              f"{r['xfb_equal']}/{r['replays']} | "
              f"{r['xfb_scratch']}/{r['replays']} | "
              f"{kv(dd, 'live_xfb_untouched', 'n/a')} |")
    print()
    print("| Arm | counter | min | max |")
    print("| --- | --- | ---: | ---: |")
    for r in results:
        if r["deltas"]:
            for key in ("dtex", "dpend", "dframe", "dafter", "dafter_live", "dpres", "dimx",
                         "pediff", "vidiff"):
                if key in r["deltas"]:
                    lo, hi = r["deltas"][key]
                    print(f"| {r['label']} | {key} | {lo} | {hi} |")
        else:
            print(f"| {r['label']} | (no delta keys) | n/a | n/a |")
    print()
    for r in results:
        print(f"{r['label']}: events={r['events']}")
        if r["restored_detail"]:
            print(f"{r['label']}: restored detail = {r['restored_detail']}")
        if r["counters_detail"]:
            print(f"{r['label']}: counters_summary = {r['counters_detail']}")
        for d in r["record_starts"]:
            print(f"{r['label']}: record_start detail = {d}")
        for d in r["resume_xfbs"]:
            print(f"{r['label']}: resume_xfb detail = {d}")
        for d in r["present_traces"]:
            print(f"{r['label']}: present_trace detail = {d}")
        if r["record_flag_set"]:
            print(f"{r['label']}: RECORD_FLAG_SET (sequence stopped early)")
        if r["watched_window_changed"]:
            print(f"{r['label']}: WATCHED WINDOW CHANGED")


if __name__ == "__main__":
    main()
