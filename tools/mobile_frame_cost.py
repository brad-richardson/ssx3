#!/usr/bin/env python3
"""Per-second frame-cost timeline and comparison for SSX iOS session reports.

Reads metrics.jsonl (schema 2 with callbackTiming) from one or more collected
session directories. Gameplay rows are selected by renderer workload, not by
guessing from the clock: a row counts as riding when its frame events carry at
least --min-draw-calls draw calls each. Pauses show up as gaps in `seconds`.
This summarizes the phone's own per-interval statistics; it is not a
trajectory-matched comparison and cannot attribute a difference to one cause.
"""
import argparse
import json
import statistics
from pathlib import Path


def load_rows(session):
    rows = []
    for line in (Path(session) / 'metrics.jsonl').read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def per_frame_draws(row):
    w = row.get('workload') or {}
    return w['drawCalls'] / w['frameEvents'] if w.get('frameEvents') else 0.0


def timing(row, kind, field):
    t = (row.get('callbackTiming') or {}).get(kind) or {}
    value = t.get(field)
    return value if isinstance(value, (int, float)) and t.get('count') else None


def median(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return statistics.median(values) if values else None


def fmt(value, digits=2):
    return '-' if value is None else f'{value:.{digits}f}'


def selected(row, selection):
    if selection.get('ordinary_only') and row.get('trialStatus') != 0:
        return False
    for option, field in (('internal_scale', 'requestedInternalScale'), ('output_scale', 'outputScale')):
        if selection.get(option) is not None and row.get(field) != selection[option]:
            return False
    maximum = selection.get('max_thermal')
    if maximum is not None and (row.get('thermalState') is None or row['thermalState'] > maximum):
        return False
    return True


def summarize(session, min_draw_calls, selection=None):
    rows = load_rows(session)
    launch = json.loads((Path(session) / 'launch.json').read_text())
    selection = selection or {}
    workload_rows = [r for r in rows if per_frame_draws(r) >= min_draw_calls]
    riding = [r for r in workload_rows if selected(r, selection)]
    selected_ids = {id(r) for r in riding}
    audio_deltas = []
    for before, after in zip(rows, rows[1:]):
        if id(before) not in selected_ids or id(after) not in selected_ids:
            continue
        clock = 'host_seconds' if 'host_seconds' in before and 'host_seconds' in after else 'seconds'
        if clock not in before or clock not in after:
            continue
        elapsed = after[clock] - before[clock]
        previous, current = before.get('audioDMAEmptyDequeues'), after.get('audioDMAEmptyDequeues')
        if (0 < elapsed <= 2 and isinstance(previous, (int, float)) and
                isinstance(current, (int, float)) and current >= previous):
            audio_deltas.append(current - previous)
    configurations = {}
    for r in riding:
        key = (r.get('requestedInternalScale'), r.get('outputScale'),
               (r.get('callbackTiming') or {}).get('cpuThread'))
        configurations[key] = configurations.get(key, 0) + 1
    slow = [r for r in riding if r.get('speed', 1) < 0.97 or r.get('fps', 60) < 57]
    result = dict(
        session=str(session), app_build=launch.get('appBuild', '')[:8], cpu_thread=launch.get('cpuThread'),
        fast_disc=launch.get('fastDiscSpeed'), dispatch_samples=launch.get('dispatchSamples'),
        output=f"{launch.get('outputWidth')}x{launch.get('outputHeight')} scale {launch.get('outputScale')}",
        internal_scale=launch.get('requestedInternalScale'),
        selection=selection, excluded_riding_rows=len(workload_rows) - len(riding),
        observed_configurations=[dict(internal_scale=k[0], output_scale=k[1], cpu_thread=k[2], rows=v)
                                 for k, v in configurations.items()],
        timing_note='Timing summaries are medians of per-interval statistics, not pooled callback percentiles. '
                    'Launch settings may differ from observed row settings. Filters do not match trajectories.',
        rows=len(rows), riding_rows=len(riding), slow_rows=len(slow),
        fps_median=median([r['fps'] for r in riding]),
        speed_median=median([r['speed'] for r in riding]),
        speed_min=min((r['speed'] for r in riding), default=None),
        max_speed_excluding_throttle_median=median([r.get('maxSpeedExcludingThrottle') for r in riding]),
        thermal_max=max((r.get('thermalState', 0) for r in rows), default=None),
        thermal_riding_median=median([r.get('thermalState') for r in riding]),
        update_cpu_median_ms=median([timing(r, 'update', 'cpuMedianMs') for r in riding]),
        update_cpu_p95_ms=median([timing(r, 'update', 'cpuP95Ms') for r in riding]),
        render_cpu_median_ms=median([timing(r, 'render', 'cpuMedianMs') for r in riding]),
        render_cpu_p95_ms=median([timing(r, 'render', 'cpuP95Ms') for r in riding]),
        render_wall_median_ms=median([timing(r, 'render', 'wallMedianMs') for r in riding]),
        update_wall_median_ms=median([timing(r, 'update', 'wallMedianMs') for r in riding]),
        draw_calls_per_frame_median=median([per_frame_draws(r) for r in riding]),
        primitives_per_frame_median=median([(r['workload']['primitives'] / r['workload']['frameEvents']) for r in riding]),
        vertex_kb_per_frame_median=median([(r['workload']['vertexBytes'] / r['workload']['frameEvents'] / 1024) for r in riding]),
        footprint_mb_max=max((r.get('footprintBytes', 0) for r in rows), default=0) / 1048576,
        audio_empty_dequeues_delta=sum(audio_deltas) if audio_deltas else None,
        audio_observed_intervals=len(audio_deltas),
        audio_note='Cumulative-counter deltas only between adjacent selected rows with increasing '
                   'timestamps no more than 2 seconds apart; excluded intervals and resets are omitted.',
    )
    return result, rows, riding, slow


def rider_text(row):
    r = row.get('rider') or {}
    if not r.get('valid'):
        return '-'
    return f"{r['x']:9.0f} {r['y']:8.0f} {r['z']:9.0f} st{int(r['state']):2d}"


def print_timeline(rows, min_draw_calls, every):
    print('   sec   fps  speed thm  upd.cpu upd.p95 rnd.cpu rnd.p95 rnd.wall draws/f prims/f  vtxKB/f  maxSpd  rider x        y         z  state')
    for i, r in enumerate(rows):
        if per_frame_draws(r) < min_draw_calls or i % every:
            continue
        w = r.get('workload') or {}
        f = w.get('frameEvents') or 1
        print(f"{r['seconds']:6.0f} {r['fps']:5.1f} {r['speed']:6.3f} {r.get('thermalState', 0):3d}"
              f"  {fmt(timing(r, 'update', 'cpuMedianMs')):>7} {fmt(timing(r, 'update', 'cpuP95Ms')):>7}"
              f" {fmt(timing(r, 'render', 'cpuMedianMs')):>7} {fmt(timing(r, 'render', 'cpuP95Ms')):>7}"
              f" {fmt(timing(r, 'render', 'wallMedianMs')):>8}"
              f" {per_frame_draws(r):7.0f} {w.get('primitives', 0) / f:7.0f} {w.get('vertexBytes', 0) / f / 1024:8.1f}"
              f" {fmt(r.get('maxSpeedExcludingThrottle')):>7}  {rider_text(r)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sessions', nargs='+', type=Path)
    parser.add_argument('--min-draw-calls', type=float, default=100,
                        help='Draw calls per frame event that count a metric row as riding')
    parser.add_argument('--timeline', action='store_true', help='Print the per-second riding timeline')
    parser.add_argument('--every', type=int, default=1, help='Timeline row stride')
    parser.add_argument('--slow', action='store_true', help='List riding rows below 0.97 speed or 57 FPS')
    parser.add_argument('--json', type=Path, help='Write the summaries as JSON')
    parser.add_argument('--ordinary-only', action='store_true',
                        help='Require explicit idle trialStatus=0; exclude unknown and other trial states')
    parser.add_argument('--max-thermal', type=int, choices=range(4),
                        help='Only metric rows at or below this thermal state (0 nominal, 1 fair, 2 serious, 3 critical)')
    parser.add_argument('--internal-scale', type=int, choices=(1, 2, 3, 4), help='Filter actual per-row detail')
    parser.add_argument('--output-scale', type=float, help='Filter actual per-row output scale (e.g. 0.5)')
    args = parser.parse_args()
    summaries = []
    for session in args.sessions:
        selection = {k: getattr(args, k) for k in ('ordinary_only', 'max_thermal', 'internal_scale', 'output_scale')}
        summary, rows, riding, slow = summarize(session, args.min_draw_calls, selection)
        summaries.append(summary)
        print(f"== {session}  build {summary['app_build']}  cpuThread={summary['cpu_thread']}  "
              f"output {summary['output']}  internal {summary['internal_scale']}x")
        for key in ('rows', 'riding_rows', 'excluded_riding_rows', 'observed_configurations',
                    'slow_rows', 'fps_median', 'speed_median', 'speed_min',
                    'max_speed_excluding_throttle_median', 'thermal_max', 'thermal_riding_median',
                    'update_cpu_median_ms', 'update_cpu_p95_ms', 'update_wall_median_ms',
                    'render_cpu_median_ms', 'render_cpu_p95_ms', 'render_wall_median_ms',
                    'draw_calls_per_frame_median', 'primitives_per_frame_median', 'vertex_kb_per_frame_median',
                    'footprint_mb_max', 'audio_empty_dequeues_delta', 'audio_observed_intervals'):
            value = summary[key]
            print(f"  {key:38s} {fmt(value, 3) if isinstance(value, float) else value}")
        print(f"  {summary['audio_note']}")
        if args.timeline:
            print_timeline(riding, args.min_draw_calls, args.every)
        if args.slow and slow:
            print('  slow riding rows:')
            print_timeline(slow, args.min_draw_calls, 1)
        print()
    if args.json:
        args.json.write_text(json.dumps(summaries, indent=2) + '\n')


if __name__ == '__main__':
    main()
