#!/usr/bin/env python3
"""Summarize an explicitly selected time window from an SSX iOS test report.

Confirm gameplay in the matching captures before treating a window as a course
benchmark. Simulator measurements are host measurements, not phone results.
"""
import argparse
import json
import math
from pathlib import Path
import statistics

try:
    from .native_gamecube import runtime_evidence
except ImportError:
    from native_gamecube import runtime_evidence


def summarize(folder, start, end):
    if not math.isfinite(start) or not math.isfinite(end) or not 0 <= start < end:
        raise ValueError("Choose a finite, ordered, nonnegative time window")
    launch = json.loads((folder / "launch.json").read_text())
    rows = []
    metrics = (folder / "metrics.jsonl").read_text()
    lines = metrics.splitlines()
    incomplete = False
    for index, line in enumerate(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            if index == len(lines)-1 and not metrics.endswith("\n"):
                incomplete = True  # A live copy can end mid-record.
                continue
            raise
        if start <= row["seconds"] <= end:
            rows.append(row)
    log = (folder / "runtime.log").read_text(errors="replace")
    result = {"report": str(folder), "launch": launch, "requested_window": [start, end],
              "sample_count": len(rows), "runtime": runtime_evidence(log),
              "incomplete_final_record": incomplete,
              "allocator_guard_reported": "[ssx3-nojit] executable allocation guard enabled" in log,
              "forbidden_allocation_reported": "[ssx3-nojit] forbidden" in log,
              "app_stopped_cleanly": "[ssx-app] stopped error=0" in log,
              "frame_interval_note": "These are video frame-event intervals; p95/p99 values are per-window statistics, not global percentiles."}
    if rows:
        result.update({
            "actual_window": [rows[0]["seconds"], rows[-1]["seconds"]],
            "fps": {"min": min(r["fps"] for r in rows), "median": statistics.median(r["fps"] for r in rows),
                    "max": max(r["fps"] for r in rows)},
            "speed": {"min": min(r["speed"] for r in rows), "median": statistics.median(r["speed"] for r in rows)},
            "max_footprint_bytes": max(r["footprintBytes"] for r in rows),
            "max_thermal_state": max(r["thermalState"] for r in rows),
            "worst_window_frame_p95_ms": max(r["frameIntervalP95ms"] for r in rows),
            "worst_window_frame_p99_ms": max(r["frameIntervalP99ms"] for r in rows),
            "audio_dma_empty_dequeues_delta": (
                rows[-1]["audioDMAEmptyDequeues"]-rows[0]["audioDMAEmptyDequeues"]
                if len(rows)>1 and all("audioDMAEmptyDequeues" in r for r in rows) else None),
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--end", type=float, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.start) or not math.isfinite(args.end) or not 0 <= args.start < args.end:
        parser.error("Choose an ordered, nonnegative time window")
    print(json.dumps(summarize(args.report,args.start,args.end),indent=2))


if __name__ == "__main__":
    main()
