#!/usr/bin/env python3
"""Summarize an explicitly selected time window from an SSX iOS test report.

Confirm gameplay in the matching captures before treating a window as a course
benchmark. Simulator measurements are host measurements, not phone results.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics

try:
    from .native_gamecube import runtime_evidence
except ImportError:
    from native_gamecube import runtime_evidence


def distribution(values):
    values = sorted(value for value in values if value is not None and math.isfinite(value))
    if not values:
        return None
    return dict(count=len(values), median=statistics.median(values),
                p95=values[int(.95*(len(values)-1))], p99=values[int(.99*(len(values)-1))],
                max=values[-1])


def presentation_summary(path, start, end):
    """Select displays by presentedTime, even if their callbacks arrive later."""
    events = []
    text = path.read_text()
    lines = text.splitlines()
    incomplete = False
    for i, line in enumerate(lines):
        if i == len(lines)-1 and not text.endswith('\n'):
            incomplete = True
            break
        fields = next(csv.reader([line]))
        if len(fields) != 5:
            raise ValueError('Malformed Metal trace event')
        event, frame, host, a, b = fields
        host, a, b = map(float, (host, a, b))
        if not all(math.isfinite(value) for value in (host, a, b)):
            raise ValueError('Nonfinite Metal trace event')
        events.append((event, int(frame), host, a, b))
    submitted = {frame: host for event, frame, host, a, b in events if event == 'submit'}
    displays = {}
    for event, frame, host, a, b in events:
        if event != 'display':
            continue
        if frame in displays:
            raise ValueError('Duplicate display callback for one submitted drawable')
        displays[frame] = a
    times = sorted(time for time in displays.values() if time > 0 and start <= time < end)
    window = [e for e in events if start <= e[2] < end]
    submitted_window = {frame for frame, host in submitted.items() if start <= host < end}
    dropped = sum(int(a) for event, frame, host, a, b in events if event == 'dropped')
    return dict(
        host_window=[start, end], submits=len(submitted_window), valid_displays=len(times),
        displays_per_second=len(times)/(end-start) if times else None,
        display_interval_ms=distribution([(b-a)*1000 for a, b in zip(times, times[1:])]),
        duplicate_positive_timestamps=len(times)-len(set(times)),
        zero_display_timestamps=sum(time <= 0 for frame, time in displays.items() if frame in submitted_window),
        submits_without_display_callback=len(submitted_window-displays.keys()),
        submit_to_display_ms=distribution([(time-submitted[frame])*1000 for frame, time in displays.items()
            if frame in submitted and time > 0 and start <= time < end and time >= submitted[frame]]),
        drawable_acquire_ms=distribution([a*1000 for event, frame, host, a, b in window if event == 'acquire']),
        failed_acquires=sum(event == 'acquire' and b == 0 for event, frame, host, a, b in window),
        final_command_buffer_gpu_ms=distribution([(b-a)*1000 for event, frame, host, a, b in window
                                                  if event == 'gpu' and 0 < a <= b]),
        gpu_errors=sum(event == 'gpu_error' for event, frame, host, a, b in window),
        presentation_timing_unavailable=sum(event == 'display_unavailable' for event, frame, host, a, b in window),
        dropped_trace_events_in_report=dropped, incomplete_final_record=incomplete,
        trace_complete=not dropped and not incomplete,
        note='Positive Metal presentedTime measures presentation; it does not prove distinct motion. '
             'Zero timestamps are unknown. Missing callbacks may be in flight during collection. '
             'GPU duration covers only the final command buffer. Rates with dropped trace events are incomplete.')


def summarize(folder, start, end, clock='active'):
    if clock not in ('active', 'host'):
        raise ValueError('Choose active or host clock')
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
        field = 'seconds' if clock == 'active' else 'host_seconds'
        if field in row and start <= row[field] <= end:
            rows.append(row)
    log = (folder / "runtime.log").read_text(errors="replace")
    result = {"report": str(folder), "launch": launch, "requested_window": [start, end],
              "clock": clock,
              "sample_count": len(rows), "runtime": runtime_evidence(log),
              "incomplete_final_record": incomplete,
              "allocator_guard_reported": "[ssx3-nojit] executable allocation guard enabled" in log,
              "forbidden_allocation_reported": "[ssx3-nojit] forbidden" in log,
              "app_stopped_cleanly": "[ssx-app] stopped error=0" in log,
              "frame_interval_note": "These are video frame-event intervals; p95/p99 values are per-window statistics, not global percentiles."}
    if rows:
        result.update({
            "actual_window": [rows[0][field], rows[-1][field]],
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
        if any('maxSpeedExcludingThrottle' in row for row in rows):
            result['max_speed_excluding_throttle'] = distribution(
                [row['maxSpeedExcludingThrottle'] for row in rows if 'maxSpeedExcludingThrottle' in row])
        workloads = [row['workload'] for row in rows if row.get('workload', {}).get('frameEvents')]
        if workloads:
            result['renderer_workload'] = dict(
                frame_events=sum(row['frameEvents'] for row in workloads),
                draw_calls=sum(row['drawCalls'] for row in workloads),
                max_draw_calls_per_frame_event=max(row['maxDrawCallsPerFrameEvent'] for row in workloads),
                shader_creation_delta={key: workloads[-1][key]-workloads[0][key]
                                       for key in ('vertexShadersCreated', 'pixelShadersCreated')},
                texture_upload_delta=workloads[-1]['texturesUploaded']-workloads[0]['texturesUploaded'],
                note='Work is aggregated over frame events in each metric interval; creation counters '
                     'are snapshots and may reset on cache reload. Counts do not measure compilation time.')
    if clock == 'host' and (folder / 'present.csv').exists():
        result['presentation'] = presentation_summary(folder / 'present.csv', start, end)
    elif (folder / 'present.csv').exists():
        result['presentation_note'] = 'Use --clock host and host_seconds from lifecycle/native trace events to align presentation across pauses.'
    lifecycle = folder / 'lifecycle.jsonl'
    if lifecycle.exists():
        events = []
        text = lifecycle.read_text()
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if i == len(lines)-1 and not text.endswith('\n'):
                result['incomplete_lifecycle_record'] = True
                break
            events.append(json.loads(line))
        checkpoints = {}
        for row in events:
            if row['event'] not in ('checkpoint_requested', 'checkpoint_stage', 'checkpoint_finished'):
                continue
            name = row.get('file') or row.get('checkpoint')
            if name:
                checkpoints.setdefault(name, []).append(row)
        result['checkpoint_diagnostics'] = [dict(file=name, events=group) for name, group in checkpoints.items()]
        if clock == 'host':
            samples = [r for r in events if r['event'] == 'recomp_sample' and start <= r['host_seconds'] < end]
            if len(samples) > 1:
                fields = ('native_dispatches', 'fallback_steps', 'fallback_jit_runs', 'native_exceptions',
                          'hle_returns', 'hle_vectors', 'hle_rejects')
                result['recomp_deltas'] = dict(
                    host_window=[samples[0]['host_seconds'], samples[-1]['host_seconds']],
                    counters={key: samples[-1][key]-samples[0][key] for key in fields},
                    note='Dispatches and fallback instructions are different units; their ratio is not time spent in fallback. Negative deltas indicate a counter reset.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--end", type=float, required=True)
    parser.add_argument('--clock', choices=('active', 'host'), default='active',
                        help='active seconds exclude pauses; host seconds share the Metal/native trace clock')
    args = parser.parse_args()
    if not math.isfinite(args.start) or not math.isfinite(args.end) or not 0 <= args.start < args.end:
        parser.error("Choose an ordered, nonnegative time window")
    print(json.dumps(summarize(args.report,args.start,args.end,args.clock),indent=2))


if __name__ == "__main__":
    main()
