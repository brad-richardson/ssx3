#!/usr/bin/env python3
"""Gate bounded phone smoothing trials and describe full/half drawable comparisons.

Only positive Metal presentedTime values count as displayed frames. A short burst
can establish high-refresh output, but cannot pass the sustained pacing gate.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

try:
    from .gamecube_schedule_trace import complete
    from .mobile_report import distribution
    from .native_gamecube import runtime_evidence
except ImportError:
    from gamecube_schedule_trace import complete
    from mobile_report import distribution
    from native_gamecube import runtime_evidence


POLICY = dict(warmup_seconds=2.0, tail_seconds=0.5, minimum_steady_seconds=25.0,
              minimum_displayed_fps=117.0, maximum_median_spacing_ms=8.6,
              maximum_p95_spacing_ms=10.0, maximum_p99_spacing_ms=17.0,
              minimum_game_speed=0.98, maximum_thermal_state=1)
WATCHED = ('position_changed', 'rng_changed', 'body_offsets', 'app_offsets', 'view_offsets',
           'same_rider', 'same_view', 'state_before', 'state_after')


def verdict(failures=(), unknowns=()):
    return dict(status='failed' if failures else 'inconclusive' if unknowns else 'passed',
                failures=list(failures), unknowns=list(unknowns))


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def known_watched_state(row):
    for field in ('position_changed', 'rng_changed', 'same_rider', 'same_view'):
        if type(row.get(field)) not in (bool, int) or row[field] not in (0, 1):
            return False
    for field in ('state_before', 'state_after'):
        if type(row.get(field)) is not int or not 0 <= row[field] <= 0xffffffff:
            return False
    for field, bound in (('body_offsets', 0x800), ('app_offsets', 0x400), ('view_offsets', 0x100)):
        values = row.get(field)
        if not isinstance(values, list) or any(type(value) is not int or not 0 <= value < bound or value % 4 for value in values):
            return False
    return True


def read_lines(path):
    """A live copy's unterminated last record is always incomplete evidence."""
    if not path.exists():
        return [], ['missing ' + path.name]
    text = path.read_text()
    lines = text.splitlines()
    incomplete = bool(text) and not text.endswith('\n')
    return (lines[:-1] if incomplete else lines), ([f'incomplete {path.name}'] if incomplete else [])


def read_jsonl(path):
    lines, issues = read_lines(path)
    rows = [json.loads(line) for line in lines]
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f'{path.name}: record must be an object')
        for field in ('host_seconds', 'wall'):
            if field in row and (not finite(row[field]) or row[field] < 0):
                raise ValueError(f'{path.name}: invalid {field}')
    return rows, issues


class Report:
    def __init__(self, folder, *, internal_scale=1):
        if type(internal_scale) is not int or internal_scale not in (1, 2):
            raise ValueError('Expected internal scale must be 1 or 2')
        self.internal_scale = internal_scale
        self.expected_internal_size = (640 * internal_scale, 528 * internal_scale)
        self.folder = Path(folder)
        self.launch = json.loads((self.folder / 'launch.json').read_text())
        self.native, self.native_issues = read_jsonl(self.folder / 'native-trial.jsonl')
        self.lifecycle, self.lifecycle_issues = read_jsonl(self.folder / 'lifecycle.jsonl')
        self.metrics, self.metric_issues = read_jsonl(self.folder / 'metrics.jsonl')
        for name, rows, issues in (('lifecycle', self.lifecycle, self.lifecycle_issues),
                                  ('metrics', self.metrics, self.metric_issues)):
            if any('host_seconds' not in row for row in rows):
                issues.append(name + ' lacks common host clock')
            times = [row['host_seconds'] for row in rows if 'host_seconds' in row]
            if times != sorted(times):
                issues.append(name + ' host clock goes backwards')
        anchors = [row['host_seconds'] - row['wall'] for row in self.native
                   if 'host_seconds' in row and 'wall' in row]
        self.offset = statistics.median(anchors) if anchors else None
        self.clock_spread = max(anchors) - min(anchors) if anchors else None
        if self.offset is None:
            self.native_issues.append('native trace lacks common host clock anchor')
        elif self.clock_spread > .01:
            self.native_issues.append('native/host clock alignment drift exceeds 10 ms')
        self.native = [dict(row, host_seconds=row.get('host_seconds', row['wall'] + self.offset))
                       for row in self.native] if self.offset is not None else []
        native_times = [row['host_seconds'] for row in self.native]
        # Rounded wall records may differ from exact schedule anchors by <1 us.
        if any(a-b > .00001 for a, b in zip(native_times, native_times[1:])):
            self.native_issues.append('native host clock goes backwards')
        lines, self.presentation_issues = read_lines(self.folder / 'present.csv')
        self.present = []
        self.submits, self.displays = {}, {}
        for fields in csv.reader(lines):
            if len(fields) != 5:
                raise ValueError('Malformed Metal trace event')
            event, frame, host, a, b = fields
            frame, host, a, b = int(frame), float(host), float(a), float(b)
            if not all(math.isfinite(value) for value in (host, a, b)) or min(host, a, b) < 0:
                raise ValueError('Invalid Metal trace timestamp/value')
            self.present.append((event, frame, host, a, b))
            if event in ('submit', 'display'):
                records = self.submits if event == 'submit' else self.displays
                if frame in records:
                    raise ValueError(f'Duplicate {event} for drawable {frame}')
                records[frame] = (host, a, b)
        self.dropped = sum(int(a) for event, frame, host, a, b in self.present if event == 'dropped')
        if self.dropped:
            self.presentation_issues.append('Metal trace overflow; lost events cannot be assigned to windows')
        runtime_path = self.folder/'runtime.log'
        runtime_text = runtime_path.read_text(errors='replace') if runtime_path.exists() else ''
        self.runtime = runtime_evidence(runtime_text)
        self.runtime_issues = []
        if not self.runtime['module_loaded'] or self.runtime['cpu_fallback_mode'] != 'interpreter':
            self.runtime_issues.append('runtime startup/module/interpreter evidence missing')
        self.identity = next((row['identity'] for row in self.lifecycle
                              if row.get('event') == 'runtime_identity'), {})
        self.pauses = self.pause_intervals()
        self.trials = self.trial_intervals()

    def pause_intervals(self):
        intervals = []
        opened = {}
        for row in self.lifecycle:
            if 'host_seconds' not in row:
                continue
            event, host = row.get('event'), row['host_seconds']
            if event in ('runtime_paused', 'system_inactive', 'audio_interrupted'):
                if event != 'audio_interrupted' or row.get('audioInterrupted', True):
                    opened.setdefault(event, host)
            closes = {'runtime_resumed': ('runtime_paused', 'audio_interrupted'),
                      'system_active': ('system_inactive',)}.get(event, ())
            if event == 'audio_interrupted' and not row.get('audioInterrupted', True):
                closes = ('audio_interrupted',)
            for reason in closes:
                if reason in opened:
                    intervals.append((opened.pop(reason), host, reason))
        intervals.extend((host, None, reason) for reason, host in opened.items())
        return sorted(intervals)

    def trial_intervals(self):
        trials, active = [], None
        for row in self.native:
            if row.get('event') != 'schedule':
                continue
            action = row.get('action')
            if action == 'start':
                if active is not None:
                    active['end'] = row['host_seconds']
                    active['issues'].append('new trial started before restore_mode')
                active = dict(trial=len(trials)+1, start=row['host_seconds'], end=None,
                              restored=False, cutoffs=[], issues=[])
                trials.append(active)
            elif action == 'performance_limit' and active is not None:
                active['cutoffs'].append(dict(host_seconds=row['host_seconds'],
                                             speed_ratio=row.get('speed_ratio')))
            elif action == 'restore_mode':
                if active is None:
                    self.native_issues.append('restore_mode without a matching start')
                else:
                    active.update(end=row['host_seconds'], restored=True)
                    active = None
        if active is not None:
            active['end'] = max((row['host_seconds'] for row in self.native), default=active['start'])
            active['issues'].append('trial has no restore_mode; collection may still be live')
        return trials


def overlaps(start, end, interval):
    left, right = interval[:2]
    return left < end and (right is None or right > start)


def active_segments(start, end, pauses):
    segments = [(start, end)]
    for left, right, reason in pauses:
        remaining = []
        for a, b in segments:
            if not overlaps(a, b, (left, right)):
                remaining.append((a, b))
                continue
            if a < left:
                remaining.append((a, left))
            if right is not None and right < b:
                remaining.append((right, b))
        segments = remaining
    return segments


def presentation_window(report, start, end):
    shown = {frame: a for frame, (host, a, b) in report.displays.items() if 0 < a and start <= a < end}
    times = sorted(shown.values())
    submitted = {frame for frame, (host, a, b) in report.submits.items() if start <= host < end}
    events = [row for row in report.present if start <= row[2] < end]
    sizes = sorted({(int(report.submits[frame][1]), int(report.submits[frame][2]))
                    for frame in submitted | shown.keys() if frame in report.submits})
    zeros = sum(report.displays[frame][1] == 0 for frame in submitted if frame in report.displays)
    missing = len(submitted - report.displays.keys())
    unlinked = len(shown.keys() - report.submits.keys())
    duplicates = len(times) - len(set(times))
    unknowns = list(report.presentation_issues)
    for value, message in ((zeros, 'zero presentedTime for an in-window submit'),
                           (missing, 'in-window submits lack display callbacks (possibly still in flight)'),
                           (unlinked, 'display lacks matching submit'),
                           (duplicates, 'duplicate positive presentedTime'),
                           (not times, 'no positive presentedTime in window')):
        if value:
            unknowns.append(message)
    return dict(valid_displays=len(times), displayed_fps=len(times)/(end-start),
                spacing_ms=distribution([(b-a)*1000 for a, b in zip(times, times[1:])]),
                zero_timestamps=zeros, missing_callbacks=missing, displays_without_submit=unlinked,
                duplicate_positive_timestamps=duplicates, drawable_sizes=sizes,
                drawable_acquire_ms=distribution([a*1000 for event, frame, host, a, b in events
                                                    if event == 'acquire']),
                final_command_buffer_gpu_ms=distribution([(b-a)*1000 for event, frame, host, a, b in events
                                                           if event == 'gpu' and 0 < a <= b]),
                gpu_errors=sum(event == 'gpu_error' for event, frame, host, a, b in events),
                failed_acquires=sum(event == 'acquire' and b == 0 for event, frame, host, a, b in events),
                unknowns=unknowns)


def native_window(report, start, end):
    rows = [row for row in report.native if start <= row['host_seconds'] < end]
    extras = [row for row in rows if row.get('event') == 'render' and row.get('repeat')]
    updates = [row for row in rows if row.get('event') == 'update']
    changes = sum(any(row.get(field) for field in WATCHED[:5]) or not row.get('same_rider') or
                  not row.get('same_view') or row.get('state_before') != row.get('state_after')
                  for row in extras if known_watched_state(row))
    missing = sum(not known_watched_state(row) for row in extras)
    speed = None
    if len(updates) > 1 and all('tb_end' in row for row in updates):
        elapsed = updates[-1]['host_seconds'] - updates[0]['host_seconds']
        if elapsed > 0 and all(b['tb_end'] >= a['tb_end'] for a, b in zip(updates, updates[1:])):
            speed = (updates[-1]['tb_end'] - updates[0]['tb_end']) / 40500000 / elapsed
    cpu_samples = [row for row in extras if finite(row.get('cpu_duration_ms'))
                   and row['cpu_duration_ms'] >= 0 and finite(row.get('duration_ms'))]
    return dict(completed_renders=sum(bool(complete(row)) for row in rows),
                completed_extras=sum(bool(complete(row)) for row in extras),
                attempted_extras=len(extras), changed_extra_callbacks=changes,
                extras_missing_watched_fields=missing, game_speed_from_timebase=speed,
                extra_callback_wall_ms=distribution([row.get('duration_ms') for row in extras]),
                extra_callback_thread_cpu_ms=distribution([row['cpu_duration_ms'] for row in cpu_samples]),
                extra_callback_wall_minus_thread_cpu_ms=distribution(
                    [row['duration_ms']-row['cpu_duration_ms'] for row in cpu_samples]),
                extras_without_thread_cpu_time=len(extras)-len(cpu_samples),
                cpu_timing_note='Callback thread only; includes nested work and probes before emission. '
                    'Wall minus CPU includes waits/descheduling, not a specific GPU stall or other-thread CPU cost.')


def metrics_window(report, start, end):
    snapshots = [row for row in report.metrics if start <= row.get('host_seconds', -1) < end]
    # A row aggregates the preceding metric interval. Exclude boundary-straddling
    # intervals and all pauses; do not equate active seconds with the host clock.
    intervals = [(a, b) for a, b in zip(report.metrics, report.metrics[1:])
                 if start <= a.get('host_seconds', -1) < b.get('host_seconds', -1) < end
                 and not any(overlaps(a['host_seconds'], b['host_seconds'], pause) for pause in report.pauses)]
    rows = [b for a, b in intervals]
    unknowns = list(report.metric_issues)
    speed = [row['speed'] for row in rows if finite(row.get('speed'))]
    thermal = [row['thermalState'] for row in snapshots if finite(row.get('thermalState'))]
    before = [row for row in report.metrics if row.get('host_seconds', math.inf) <= start]
    after = [row for row in report.metrics if row.get('host_seconds', -1) >= end]
    bracket = ([row for row in report.metrics if before[-1]['host_seconds'] <= row.get('host_seconds', -1) <= after[0]['host_seconds']]
               if before and after else [])
    audio = [row.get('audioDMAEmptyDequeues') for row in bracket]
    audio_ok = (len(audio) > 1 and all(type(value) is int and value >= 0 for value in audio)
                and start-bracket[0]['host_seconds'] <= 1.5 and bracket[-1]['host_seconds']-end <= 1.5)
    reset = audio_ok and any(b < a for a, b in zip(audio, audio[1:]))
    inside_audio = [row.get('audioDMAEmptyDequeues') for row in snapshots]
    inside_delta = (inside_audio[-1]-inside_audio[0] if len(inside_audio) > 1 and
                    all(type(value) is int and value >= 0 for value in inside_audio) else None)
    audio_delta = audio[-1]-audio[0] if audio_ok and not reset else None
    boundary_increase = audio_delta is not None and audio_delta > max(inside_delta or 0, 0)
    if len(speed) != len(rows) or not rows:
        unknowns.append('no complete game-speed metric intervals or missing speed values')
    if len(thermal) != len(snapshots) or not thermal:
        unknowns.append('thermal measurements missing')
    if not audio_ok or reset:
        unknowns.append('audio starvation counter missing, reset, or lacks close bracketing samples')
    if boundary_increase and not (inside_delta is not None and inside_delta > 0):
        unknowns.append('audio counter increased across a window boundary; exact event time unknown')
    if bracket and any(overlaps(bracket[0]['host_seconds'], bracket[-1]['host_seconds'], pause) for pause in report.pauses):
        unknowns.append('audio observation bracket crosses an interruption')
    if snapshots and (snapshots[0]['host_seconds']-start > 1.5 or end-snapshots[-1]['host_seconds'] > 1.5):
        unknowns.append('metrics do not cover window edges within 1.5 seconds')
    if any(b['host_seconds']-a['host_seconds'] > 1.5 for a, b in intervals):
        unknowns.append('gap in metrics exceeds 1.5 seconds')
    valid_efb = lambda row: all(type(row.get(field)) is int and row[field] > 0 for field in ('efbWidth', 'efbHeight'))
    sizes = sorted({(row['efbWidth'], row['efbHeight']) for row in snapshots if valid_efb(row)})
    if any(not valid_efb(row) for row in snapshots):
        unknowns.append('internal resolution measurements missing or invalid')
    output_scales = sorted({row['outputScale'] for row in snapshots if finite(row.get('outputScale'))})
    return dict(complete_intervals=len(rows), snapshot_count=len(snapshots),
                observed_host_span=[snapshots[0]['host_seconds'], snapshots[-1]['host_seconds']] if snapshots else None,
                speed_min=min(speed) if speed else None, speed_median=statistics.median(speed) if speed else None,
                max_thermal_state=max(thermal) if thermal else None,
                thermal_before_window=before[-1].get('thermalState') if before else None,
                audio_empty_dequeues_delta=audio_delta, audio_in_window_snapshot_delta=inside_delta,
                audio_observed_host_span=[bracket[0]['host_seconds'], bracket[-1]['host_seconds']] if bracket else None,
                audio_boundary_increase_unknown=boundary_increase,
                audio_counter_reset=bool(reset), internal_sizes=sizes, output_scales=output_scales,
                unknowns=unknowns,
                note='Speed uses complete intervals. Audio uses nearest <=start and >=end snapshots (within1.5s); '
                     'boundary-only increases cannot be attributed to an exact in-window instant.')


def analyze_window(report, start, end):
    if not all(finite(value) and value >= 0 for value in (start, end)) or end <= start:
        raise ValueError('Choose a finite, positive host-time window')
    presentation = presentation_window(report, start, end)
    native = native_window(report, start, end)
    metrics = metrics_window(report, start, end)
    pauses = [pause for pause in report.pauses if overlaps(start, end, pause)]
    unknowns = list(dict.fromkeys(report.native_issues + report.lifecycle_issues + report.runtime_issues +
                                 presentation['unknowns'] + metrics['unknowns']))
    if end-start < POLICY['minimum_steady_seconds']:
        unknowns.append('less than 25 seconds of continuous warmed evidence; short burst only')
    if pauses:
        unknowns.append('window crosses pause/background/audio interruption; explicitly segment before comparing')
    if report.launch.get('simulator') != 0 or report.launch.get('presentationTimestampsSupported') is not True:
        unknowns.append('physical iPhone presentation support is not established')
    if report.launch.get('audioEnabled', True) is not True:
        unknowns.append('audio disabled or availability unknown; audio integrity is not established')
    if metrics['internal_sizes'] != [report.expected_internal_size]:
        width, height = report.expected_internal_size
        unknowns.append(f'internal resolution is not consistently measured at {width}x{height}')
    if len(presentation['drawable_sizes']) != 1 or any(min(size) <= 0 for size in presentation['drawable_sizes']):
        unknowns.append('drawable resolution missing or changed within the window')
    if len(metrics['output_scales']) > 1:
        unknowns.append('output scale changed within the window')
    if any(start <= row.get('host_seconds', -1) < end and row.get('event') in
           ('output_resolution_requested', 'output_resolution_applied') for row in report.lifecycle):
        unknowns.append('output resize crosses the window')
    if any(start <= row.get('host_seconds', -1) < end and row.get('event') in
           ('internal_resolution_requested', 'internal_resolution_configured') for row in report.lifecycle):
        unknowns.append('internal detail change crosses the window')
    if native['game_speed_from_timebase'] is None:
        unknowns.append('guest timebase speed unavailable')
    if not native['completed_extras'] or native['extras_missing_watched_fields']:
        unknowns.append('complete extra-render watched-state evidence missing')
    containing = [trial for trial in report.trials if trial['start'] <= start < end <= trial['end']]
    if len(containing) != 1 or not containing[0]['restored']:
        unknowns.append('window is not inside one completed native start/restore trial')
    violations = []
    if presentation['displayed_fps'] < POLICY['minimum_displayed_fps']:
        violations.append('displayed FPS below 117')
    spacing = presentation['spacing_ms']
    for field in ('median', 'p95', 'p99'):
        if spacing and spacing[field] > POLICY[f'maximum_{field}_spacing_ms']:
            violations.append(f'{field} presentation spacing exceeds policy')
    for field, value in (('metric', metrics['speed_min']), ('timebase', native['game_speed_from_timebase'])):
        if value is not None and value < POLICY['minimum_game_speed']:
            violations.append(field + ' game speed below 0.98x')
    if not metrics['audio_counter_reset'] and (metrics['audio_in_window_snapshot_delta'] or 0) > 0:
        violations.append('audio starvation counter increased')
    if metrics['max_thermal_state'] is not None and metrics['max_thermal_state'] > POLICY['maximum_thermal_state']:
        violations.append('thermal state above fair')
    if presentation['gpu_errors'] or native['changed_extra_callbacks']:
        violations.append('functional integrity violation')
    return dict(host_window=[start, end], seconds=end-start, presentation=presentation, native=native,
                metrics=metrics, pause_intersections=pauses, measured_target_misses=violations,
                sustained_120=verdict(violations if not unknowns else [], unknowns))


def analyze_trial(report, trial, segment_pauses=False):
    start, end = trial['start'], trial['end']
    unknowns = list(dict.fromkeys(report.native_issues + report.runtime_issues + trial['issues']))
    failures = []
    native = native_window(report, start, math.nextafter(end, math.inf)) if end > start else {}
    if native.get('changed_extra_callbacks'):
        failures.append('extra render changed watched guest state')
    if native.get('extras_missing_watched_fields') or not native.get('completed_extras'):
        unknowns.append('no complete extras with all watched state evidence')
    if not trial['restored']:
        unknowns.append('normal rendering restoration not observed')
    for field in ('invalid_memory_accesses', 'gpu_command_errors', 'unknown_guest_instructions'):
        if report.runtime.get(field):
            failures.append('session runtime reported ' + field)
    if any(event == 'gpu_error' and start <= host < end for event, frame, host, a, b in report.present):
        failures.append('Metal reported a GPU error during trial')
    segments = active_segments(start, end, report.pauses) if segment_pauses else [(start, end)]
    windows = []
    for a, b in segments:
        left, right = a+POLICY['warmup_seconds'], b-POLICY['tail_seconds']
        if right > left:
            windows.append(analyze_window(report, left, right))
    if windows:
        status = ('passed' if any(w['sustained_120']['status'] == 'passed' for w in windows) else
                  'failed' if any(w['sustained_120']['status'] == 'failed' for w in windows) else 'inconclusive')
    else:
        status = 'inconclusive'
    if not trial['restored'] or failures or unknowns:
        status = 'failed' if failures else 'inconclusive'
    return dict(**trial, duration_seconds=end-start, native=native,
                functional_integrity=verdict(failures, unknowns), steady_windows=windows,
                sustained_120_status=status,
                scope='Integrity covers observed extra-render watched fields and mode restoration, not all guest state.')


def analyze_session(report, segment_pauses=False):
    trials = [analyze_trial(report, trial, segment_pauses) for trial in report.trials]
    files = ('launch.json', 'lifecycle.jsonl', 'metrics.jsonl', 'native-trial.jsonl', 'present.csv', 'runtime.log')
    return dict(report=str(report.folder), launch=report.launch, runtime_identity=report.identity,
                policy=dict(POLICY, expected_internal_scale=report.internal_scale,
                            expected_internal_size=report.expected_internal_size),
                clock='host_seconds / Metal presentedTime; native wall aligned by measured anchors',
                clock_anchor_spread_seconds=report.clock_spread, segment_pauses=segment_pauses,
                trial_count=len(trials), trials=trials,
                trace_health=dict(unknowns=list(dict.fromkeys(report.native_issues+report.lifecycle_issues+
                                                            report.metric_issues+report.presentation_issues+report.runtime_issues)),
                                  dropped_metal_events=report.dropped,
                                  zero_presented_times_in_session=sum(a == 0 for host, a, b in report.displays.values())),
                evidence_sha256={name: hashlib.sha256((report.folder/name).read_bytes()).hexdigest()
                                 for name in files if (report.folder/name).exists()},
                limits=['Positive presentedTime establishes delivery, not distinct motion or input latency.',
                        'Final command-buffer GPU timing excludes earlier command buffers.',
                        'Passing 25 seconds is bounded evidence, not long-session thermal acceptance.',
                        'Do not extend the 35-second trial or weaken its speed floor to manufacture a pass.'])


def compare_trials(baseline, candidate, baseline_trial=1, candidate_trial=1):
    """Equal-duration, warmed descriptive comparison; never claims causality."""
    left, right = baseline.trials[baseline_trial-1], candidate.trials[candidate_trial-1]
    a, b = left['start']+POLICY['warmup_seconds'], right['start']+POLICY['warmup_seconds']
    duration = min(left['end']-a, right['end']-b)-POLICY['tail_seconds']
    if duration <= 0:
        return dict(comparison_validity=verdict(unknowns=['no common warmed duration']))
    full, half = analyze_window(baseline, a, a+duration), analyze_window(candidate, b, b+duration)
    failures, unknowns = [], []
    if baseline.internal_scale != candidate.internal_scale:
        failures.append('expected internal-resolution policies differ')
    for label, report, trial in (('full', baseline, left), ('half', candidate, right)):
        integrity = analyze_trial(report, trial)['functional_integrity']
        failures.extend(label+': '+reason for reason in integrity['failures'])
        unknowns.extend(label+': '+reason for reason in integrity['unknowns'])
    for field in ('appBuild', 'disc', 'moduleABI', 'os', 'device', 'metalDevice', 'simulator',
                  'cpuJIT', 'cpuThread', 'vertexLoader', 'renderScale'):
        if field not in baseline.launch or field not in candidate.launch:
            unknowns.append('missing comparable config field: '+field)
        elif baseline.launch[field] != candidate.launch[field]:
            failures.append('config differs: '+field)
    for field in ('assets', 'dol'):
        if field not in baseline.identity or field not in candidate.identity:
            unknowns.append('missing runtime identity: '+field)
        elif baseline.identity[field] != candidate.identity[field]:
            failures.append('runtime identity differs: '+field)
    fs, hs = full['presentation']['drawable_sizes'], half['presentation']['drawable_sizes']
    if len(fs) != 1 or len(hs) != 1 or any(abs(x-2*y) > 1 for x, y in zip(fs[0], hs[0])):
        failures.append('candidate Metal drawable is not half the full drawable in both dimensions')
    for label, result, scale in (('full', full, 1.0), ('half', half, .5)):
        expected = baseline.expected_internal_size if label == 'full' else candidate.expected_internal_size
        if result['metrics']['internal_sizes'] != [expected]:
            failures.append(f'{label} internal resolution is not {expected[0]}x{expected[1]}')
        if result['metrics']['output_scales'] != [scale]:
            unknowns.append(label+' measured outputScale is missing or inconsistent')
        unknowns.extend(label+': '+reason for reason in result['sustained_120']['unknowns'])
    if full['metrics']['thermal_before_window'] != half['metrics']['thermal_before_window']:
        unknowns.append('starting thermal states differ')
    return dict(comparison_validity=verdict(failures, list(dict.fromkeys(unknowns))),
                baseline_trial=baseline_trial, candidate_trial=candidate_trial,
                equal_warmed_seconds=duration, full=full, half=half,
                observed_displayed_fps_difference=half['presentation']['displayed_fps']-full['presentation']['displayed_fps'],
                causal_speedup_established=False,
                note='Descriptive comparison only: manual trajectories, cache state and prior thermal exposure are unmatched.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--compare', type=Path, help='half-output report; positional report is full output')
    parser.add_argument('--baseline-trial', type=int, default=1)
    parser.add_argument('--candidate-trial', type=int, default=1)
    parser.add_argument('--internal-scale', type=int, choices=(1, 2), default=1,
                        help='explicit expected EFB scale; default 1, unchanged pacing/audio/speed requirements')
    parser.add_argument('--segment-pauses', action='store_true',
                        help='analyze separate active segments, warming each; never stitch durations together')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-sustained', action='store_true', help='exit nonzero unless a warmed trial passes')
    args = parser.parse_args()
    try:
        report = Report(args.report, internal_scale=args.internal_scale)
        result = analyze_session(report, args.segment_pauses)
        if args.compare:
            candidate = Report(args.compare, internal_scale=args.internal_scale)
            if not 1 <= args.baseline_trial <= len(report.trials) or not 1 <= args.candidate_trial <= len(candidate.trials):
                parser.error('comparison trial numbers must identify recorded native trials')
            result['comparison'] = compare_trials(report, candidate, args.baseline_trial, args.candidate_trial)
    except (ValueError, OSError, KeyError) as error:
        parser.error(str(error))
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
    if args.require_sustained:
        accepted = any(t['sustained_120_status'] == 'passed' and t['functional_integrity']['status'] == 'passed'
                       for t in result['trials'])
        if args.compare:
            comparison = result['comparison']
            accepted = (comparison['comparison_validity']['status'] == 'passed' and
                        all(comparison[label]['sustained_120']['status'] == 'passed' for label in ('full', 'half')))
        return 0 if accepted else 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
