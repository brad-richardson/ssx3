#!/usr/bin/env python3
"""Summarize independent scheduling without counting requests as rendered frames."""
import argparse
import collections
import csv
import json
import statistics
from pathlib import Path


def complete(row):
    return (row.get('event') == 'render' and row.get('result', 0) & 255 and
            row.get('view_matrix_calls', 0) > 0 and row.get('frame_end_calls', 0) > 0)


def summarize(rows, start=145, end=170, presents=None):
    if end <= start:
        raise ValueError('Window must have positive duration')
    window = [r for r in rows if start <= r['wall'] < end]
    schedule = [r for r in window if r['event'] == 'schedule']
    callbacks = [r for r in window if r['event'] in ('render', 'update')]
    renders = [r for r in callbacks if complete(r)]
    extras = [r for r in callbacks if r['event'] == 'render' and r['repeat']]
    updates = [r for r in callbacks if r['event'] == 'update']
    result = dict(window=[start, end], seconds=end-start,
                  actions=dict(collections.Counter(r['action'] for r in schedule)),
                  missed_deadlines=sum(r.get('missed', 0) for r in schedule),
                  complete_renders=len(renders), attempted_extras=len(extras),
                  complete_extras=sum(bool(complete(r)) for r in extras),
                  render_callbacks_per_host_second=len(renders)/(end-start),
                  update_callbacks_per_host_second=len(updates)/(end-start),
                  update_callbacks=len(updates),
                  retries=sum(r.get('retries', 0) for r in extras),
                  extra_state_changes={},
                  queue_values=sorted({r['pending'] for r in schedule}),
                  median_extra_callback_ms=statistics.median(r['duration_ms'] for r in extras)
                  if extras else None)
    for label, group in (('extra', extras), ('regular', [r for r in renders if not r['repeat']])):
        wall_costs = sorted(r['duration_ms'] for r in group if 'duration_ms' in r)
        result[f'{label}_callback_wall_ms'] = dict(
            median=statistics.median(wall_costs) if wall_costs else None,
            p95=wall_costs[int(.95*(len(wall_costs)-1))] if wall_costs else None)
        costs = [(r['tb_end']-r['tb_start'])/40500 for r in group
                 if 'tb_start' in r and 'tb_end' in r]
        result[f'median_{label}_guest_callback_ms'] = statistics.median(costs) if costs else None
    for field in ('position_changed', 'rng_changed', 'body_offsets', 'app_offsets', 'view_offsets'):
        result['extra_state_changes'][field] = sum(bool(r.get(field)) for r in extras)
    result['extra_state_changes']['identity_or_state'] = sum(
        not r['same_rider'] or not r['same_view'] or r['state_before'] != r['state_after']
        for r in extras)
    # Native timebase includes a wall-clock-derived offset: use only differences.
    if len(updates) > 1:
        tb_seconds = (updates[-1]['tb_end'] - updates[0]['tb_end']) / 40500000
        result['guest_seconds_per_host_second'] = tb_seconds / (updates[-1]['wall'] - updates[0]['wall'])
        result['updates_per_guest_second'] = (len(updates)-1)/tb_seconds if tb_seconds else None
    if presents is not None:
        anchors = [r['host_seconds'] - r['wall'] for r in rows if 'host_seconds' in r]
        if not anchors:
            result['presentation'] = {'error': 'Trace has no host-clock alignment anchor'}
        else:
            offset = statistics.median(anchors)
            # The adapter records mach_absolute_time, matching Metal uptime.
            # Its separate wall clock includes sleep; reject drift in the run.
            if max(anchors)-min(anchors) > .01:
                raise ValueError('Host clock alignment drift exceeds 10 ms')
            events = [r for r in presents if start <= float(r[2])-offset < end]
            display = [float(r[3]) for r in presents if r[0] == 'display' and
                       float(r[3]) > 0 and start <= float(r[3])-offset < end]
            display.sort()
            intervals = [(b-a)*1000 for a,b in zip(display, display[1:])]
            result['presentation'] = dict(
                submits=sum(r[0] == 'submit' for r in events),
                valid_displays=len(display),
                displays_per_second=len(display)/(end-start) if display else None,
                zero_display_timestamps=sum(r[0]=='display' and float(r[3])==0 for r in events),
                median_interval_ms=statistics.median(intervals) if intervals else None,
                p95_interval_ms=sorted(intervals)[int(.95*(len(intervals)-1))] if intervals else None)
            if presents and not events:
                result['presentation']['error'] = 'No events overlap the aligned window; check clock domain and capture'
            elif not display:
                result['presentation']['note'] = 'No positive presentation timestamps; actual display rate is unknown'
            for label, samples in (
                    ('drawable_acquire_ms', [float(r[3])*1000 for r in events if r[0]=='acquire']),
                    ('final_command_buffer_gpu_ms', [(float(r[4])-float(r[3]))*1000
                     for r in events if r[0]=='gpu' and float(r[3])>0])):
                result['presentation'][label] = dict(
                    median=statistics.median(samples) if samples else None,
                    p95=sorted(samples)[int(.95*(len(samples)-1))] if samples else None)
    result['limits'] = ('Callback completion is not distinct interpolated motion. Extra state checks '
                        'cover bounded windows only. Callback duration includes preemption and waits. '
                        'Update callbacks are not a proven count of physics steps. Mac display '
                        'timestamps do not establish mobile performance or input latency.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--present', type=Path)
    parser.add_argument('--start', type=float, default=145)
    parser.add_argument('--end', type=float, default=170)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.trace.read_text().splitlines()]
    presents = list(csv.reader(args.present.read_text().splitlines())) if args.present else None
    result = summarize(rows, args.start, args.end, presents)
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
