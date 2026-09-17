"""Per-process GPU-busy time from a Metal System Trace bundle.

Pipeline: `xctrace export` the metal-gpu-intervals table, then union the
depth-0 intervals per process (nested intervals overlap, so only the
outermost level counts toward wall time). Frame numbers give per-display-
frame GPU cost, the number the 120 Hz budget question needs.

Usage:
  python3 tools/metal_gpu_ms.py report --trace <capture.trace> --process SSXNative
  python3 tools/metal_gpu_ms.py report --intervals <export.xml> --process SSXNative
"""
import argparse
import json
import statistics
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

INTERVALS_XPATH = '/trace-toc/run/data/table[@schema="metal-gpu-intervals"]'

# Column order in the metal-gpu-intervals schema export.
(IDX_START, IDX_DUR, IDX_CHAN, IDX_FRAME, _LAT, IDX_DEPTH, _LABEL, _STATE,
 _CONN, _COLOR, IDX_PROC, _GPU, _SUB, _ACC, _BYTES, _CMD, _ENC,
 _SUBM) = range(18)


def export_intervals(trace, destination):
    completed = subprocess.run(
        ["xctrace", "export", str(trace), "--xpath", INTERVALS_XPATH,
         "--output", str(destination)],
        capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(f"xctrace export failed: {(completed.stderr or '').strip()[:300]}")
    return destination


def union_ms(intervals):
    total = 0
    cur_s = cur_e = None
    for start, end in sorted(intervals):
        if cur_s is None:
            cur_s, cur_e = start, end
        elif start <= cur_e:
            cur_e = max(cur_e, end)
        else:
            total += cur_e - cur_s
            cur_s, cur_e = start, end
    if cur_s is not None:
        total += cur_e - cur_s
    return total / 1e6


def parse_intervals(path):
    """Stream the export; return rows as (start_ns, dur_ns, depth, frame, channel, process)."""
    ids = {}
    rows = []
    for _ev, el in ET.iterparse(str(path), events=("end",)):
        if el.tag != "row":
            continue
        kids = [(ch.tag, ch.get("fmt"), (ch.text or "").strip(), ch.attrib.get("ref"))
                for ch in el]
        for ch in el.iter():
            if "id" in ch.attrib and "ref" not in ch.attrib:
                ids[ch.attrib["id"]] = (ch.get("fmt"), (ch.text or "").strip())

        def cell(i):
            _tag, fmt, text, ref = kids[i]
            if ref:
                return ids[ref]
            return (fmt, text)

        try:
            start = int(cell(IDX_START)[1])
            dur = int(cell(IDX_DUR)[1])
            depth = int(cell(IDX_DEPTH)[1])
        except (IndexError, ValueError, KeyError):
            el.clear()
            continue
        try:
            proc = cell(IDX_PROC)[0] or ""
            frame = cell(IDX_FRAME)[1]
            chan = cell(IDX_CHAN)[0] or ""
        except IndexError:
            proc, frame, chan = "", "", ""
        rows.append((start, dur, depth, frame, chan, proc))
        el.clear()
    return rows


def summarize(rows, process):
    ours = [r for r in rows if process in r[5]]
    if not ours:
        names = Counter(r[5] for r in rows).most_common(5)
        raise RuntimeError(f"No GPU intervals for {process!r}; saw: {names}")
    depth0 = [(s, s + d) for s, d, dep, _f, _c, _p in ours if dep == 0]
    channels = defaultdict(list)
    for start, dur, depth, _frame, chan, _proc in ours:
        if depth == 0:
            channels[chan or "unknown"].append((start, start + dur))
    frames = defaultdict(list)
    for start, dur, _depth, frame, _chan, _proc in ours:
        if frame:
            frames[frame].append((start, start + dur))
    per_frame = sorted(union_ms(v) for v in frames.values())
    starts = [s for s, _d, _dep, _f, _c, _p in ours]
    ends = [s + d for s, d, _dep, _f, _c, _p in ours]
    span_s = (max(ends) - min(starts)) / 1e9
    busy = union_ms(depth0)
    report = {
        "process": process,
        "intervals": len(ours),
        "span_s": round(span_s, 1),
        "gpu_busy_ms": round(busy, 1),
        "gpu_busy_pct": round(100 * busy / (span_s * 1000), 2),
        "channels_ms": {k: round(union_ms(v), 1) for k, v in sorted(channels.items())},
        "frames": len(per_frame),
        "per_frame_gpu_ms": {
            "median": round(statistics.median(per_frame), 3),
            "p90": round(per_frame[int(len(per_frame) * 0.9)], 3),
            "p99": round(per_frame[int(len(per_frame) * 0.99)], 3),
            "max": round(max(per_frame), 3),
        } if per_frame else None,
    }
    others = Counter(r[5] for r in rows if process not in r[5])
    report["other_processes"] = [
        {"process": name,
         "union_ms": round(union_ms([(s, s + d) for s, d, dep, _f, _c, p in rows
                                     if p == name and dep == 0]), 1)}
        for name, _count in others.most_common(5)]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="Report per-process GPU time")
    rep.add_argument("--trace", type=Path, help="Capture .trace bundle")
    rep.add_argument("--intervals", type=Path, help="Existing intervals export XML")
    rep.add_argument("--process", default="SSXNative")
    args = parser.parse_args(argv)
    if bool(args.trace) == bool(args.intervals):
        parser.error("Pass exactly one of --trace or --intervals")
    if args.intervals:
        rows = parse_intervals(args.intervals)
    else:
        with tempfile.TemporaryDirectory(prefix="ssx-gpu-ms-") as tmp:
            export = export_intervals(args.trace, Path(tmp) / "intervals.xml")
            rows = parse_intervals(export)
    print(json.dumps(summarize(rows, args.process), indent=2))


if __name__ == "__main__":
    main()
