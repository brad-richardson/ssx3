import json
from pathlib import Path
import tempfile
import unittest

from tools.mobile_pacing_check import Report, analyze_session, analyze_window, compare_trials


class MobilePacingCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_rows(self, folder, name, rows):
        (folder/name).write_text(''.join(json.dumps(row)+'\n' for row in rows))

    def fixture(self, name='full', duration=30, scale=1.0, delayed_callbacks=False):
        folder = self.root/name
        folder.mkdir()
        launch = dict(appBuild='build-a', disc='GXBE69', moduleABI=3, os='26.6.2', device='iPhone',
                      metalDevice='Apple A18 Pro GPU', simulator=0, presentationTimestampsSupported=True,
                      cpuJIT=False, cpuThread=False, vertexLoader='software', renderScale=1,
                      outputScale=scale)
        (folder/'launch.json').write_text(json.dumps(launch))
        (folder/'runtime.log').write_text('[staticrecomp] module loaded: test entry=0x80003154\n'
                                        '[staticrecomp] fallback mode: interpreter\n')
        lifecycle = [dict(event='running', host_seconds=95),
                     dict(event='runtime_identity', host_seconds=95.01,
                          identity=dict(assets='assets-a', dol='dol-a'))]
        self.write_rows(folder, 'lifecycle.jsonl', lifecycle)
        rows = [dict(host_seconds=float(host), seconds=float(host-95), speed=1, thermalState=0,
                     audioDMAEmptyDequeues=0, efbWidth=640, efbHeight=528, outputScale=scale)
                for host in range(96, 102+duration)]
        self.write_rows(folder, 'metrics.jsonl', rows)
        native = [dict(event='schedule', action='start', host_seconds=100, wall=0)]
        for index in range(duration*60):
            wall = (index+.25)/60
            native.append(dict(event='update', wall=wall, tb_end=round(wall*40500000)))
            native.append(dict(event='render', wall=wall+.001, repeat=1, result=1,
                               view_matrix_calls=1, frame_end_calls=1, duration_ms=1,
                               position_changed=0, rng_changed=0, body_offsets=[], app_offsets=[],
                               view_offsets=[], same_rider=1, same_view=1, state_before=5, state_after=5))
        native.append(dict(event='schedule', action='restore_mode', host_seconds=100+duration, wall=duration))
        self.write_rows(folder, 'native-trial.jsonl', native)
        present = []
        for frame in range((duration+2)*120):
            stamp = 99+(frame+.5)/120
            callback = stamp+50 if delayed_callbacks else stamp+.001
            present.extend([f'submit,{frame},{stamp-.001:.9f},{2868*scale},{1320*scale}\n',
                            f'display,{frame},{callback:.9f},{stamp:.9f},0\n'])
        (folder/'present.csv').write_text(''.join(present))
        return folder

    def json_rows(self, folder, name):
        return [json.loads(line) for line in (folder/name).read_text().splitlines()]

    def test_complete_long_trace_and_late_callbacks_establish_bounded_target(self):
        report = Report(self.fixture(delayed_callbacks=True))
        result = analyze_session(report)
        trial = result['trials'][0]
        window = trial['steady_windows'][0]
        self.assertEqual(trial['functional_integrity']['status'], 'passed')
        self.assertEqual(trial['sustained_120_status'], 'passed')
        self.assertEqual(window['presentation']['displayed_fps'], 120)
        self.assertAlmostEqual(window['presentation']['spacing_ms']['p99'], 1000/120, places=5)
        # Callback delivery occurs outside the window; presentedTime owns the frame.
        self.assertEqual(window['presentation']['missing_callbacks'], 0)

    def test_four_seconds_at_120_is_not_sustained_acceptance(self):
        report = Report(self.fixture(duration=4))
        window = analyze_window(report, 100, 104)
        self.assertEqual(window['presentation']['displayed_fps'], 120)
        self.assertEqual(window['sustained_120']['status'], 'inconclusive')
        self.assertIn('short burst', ' '.join(window['sustained_120']['unknowns']))

    def test_cpu_time_is_optional_and_not_inferred_from_wall_time(self):
        folder = self.fixture(duration=4)
        original = analyze_window(Report(folder), 100, 104)['native']
        self.assertIsNone(original['extra_callback_thread_cpu_ms'])
        rows = self.json_rows(folder, 'native-trial.jsonl')
        for row in rows:
            if row.get('event') == 'render':
                row['cpu_duration_ms'] = .25
        rows[2]['cpu_duration_ms'] = None
        self.write_rows(folder, 'native-trial.jsonl', rows)
        result = analyze_window(Report(folder), 100, 104)['native']
        self.assertEqual(result['extras_without_thread_cpu_time'], 1)
        self.assertEqual(result['extra_callback_thread_cpu_ms']['median'], .25)
        self.assertEqual(result['extra_callback_wall_minus_thread_cpu_ms']['median'], .75)

    def test_guard_cutoff_is_not_restore_and_inflight_extra_remains_checked(self):
        folder = self.fixture(duration=4)
        rows = self.json_rows(folder, 'native-trial.jsonl')
        rows.insert(-2, dict(event='schedule', action='performance_limit', host_seconds=103.99,
                             wall=3.99, speed_ratio=.94))
        rows[-2]['position_changed'] = 1
        # Keep the last extra after cutoff and before restoration.
        rows[-2]['wall'] = 3.999
        rows.sort(key=lambda row: row['wall'])
        self.write_rows(folder, 'native-trial.jsonl', rows)
        trial = analyze_session(Report(folder))['trials'][0]
        self.assertEqual(trial['duration_seconds'], 4)
        self.assertEqual(trial['cutoffs'][0]['host_seconds'], 103.99)
        self.assertEqual(trial['functional_integrity']['status'], 'failed')

    def test_zero_time_outside_window_is_retained_but_inside_is_unknown(self):
        folder = self.fixture()
        with (folder/'present.csv').open('a') as out:
            out.write('submit,9000,96,2868,1320\ndisplay,9000,96.01,0,0\n')
        result = analyze_session(Report(folder))
        self.assertEqual(result['trace_health']['zero_presented_times_in_session'], 1)
        self.assertEqual(result['trials'][0]['sustained_120_status'], 'passed')
        with (folder/'present.csv').open('a') as out:
            out.write('submit,9001,110,2868,1320\ndisplay,9001,160,0,0\n')
        result = analyze_session(Report(folder))['trials'][0]['steady_windows'][0]
        self.assertEqual(result['presentation']['zero_timestamps'], 1)
        self.assertEqual(result['sustained_120']['status'], 'inconclusive')

    def test_dropped_events_cannot_be_assumed_outside_window(self):
        folder = self.fixture()
        with (folder/'present.csv').open('a') as out:
            out.write('dropped,0,200,12,0\n')
        result = analyze_session(Report(folder))
        self.assertEqual(result['trace_health']['dropped_metal_events'], 12)
        self.assertEqual(result['trials'][0]['sustained_120_status'], 'inconclusive')

    def test_incomplete_final_record_and_missing_callback_do_not_pass(self):
        folder = self.fixture()
        with (folder/'present.csv').open('a') as out:
            out.write('submit,9000,110,2868,1320\ndisplay,9000,')
        window = analyze_session(Report(folder))['trials'][0]['steady_windows'][0]
        self.assertEqual(window['presentation']['missing_callbacks'], 1)
        self.assertEqual(window['sustained_120']['status'], 'inconclusive')

    def test_paused_windows_are_not_stitched_into_a_sustained_pass(self):
        folder = self.fixture(duration=56)
        rows = self.json_rows(folder, 'lifecycle.jsonl')
        rows += [dict(event='runtime_paused', host_seconds=126), dict(event='runtime_resumed', host_seconds=130)]
        self.write_rows(folder, 'lifecycle.jsonl', rows)
        report = Report(folder)
        result = analyze_session(report)['trials'][0]
        self.assertEqual(result['sustained_120_status'], 'inconclusive')
        self.assertTrue(result['steady_windows'][0]['pause_intersections'])
        segmented = analyze_session(report, segment_pauses=True)['trials'][0]
        self.assertEqual(len(segmented['steady_windows']), 2)
        self.assertGreater(sum(w['seconds'] for w in segmented['steady_windows']), 25)
        self.assertEqual(segmented['sustained_120_status'], 'inconclusive')
        self.assertTrue(all(not w['pause_intersections'] for w in segmented['steady_windows']))

    def test_metric_interval_straddling_window_is_excluded(self):
        folder = self.fixture()
        rows = self.json_rows(folder, 'metrics.jsonl')
        next(row for row in rows if row['host_seconds'] == 102)['speed'] = .1
        self.write_rows(folder, 'metrics.jsonl', rows)
        result = analyze_window(Report(folder), 101.5, 129.5)
        self.assertEqual(result['metrics']['speed_min'], 1)
        self.assertEqual(result['sustained_120']['status'], 'passed')

    def test_audio_reset_is_not_a_clean_zero_delta_and_gaps_are_unknown(self):
        folder = self.fixture()
        rows = self.json_rows(folder, 'metrics.jsonl')
        for row in rows:
            row['audioDMAEmptyDequeues'] = 10 if row['host_seconds'] == 110 else 0
        rows = [row for row in rows if row['host_seconds'] != 115]
        self.write_rows(folder, 'metrics.jsonl', rows)
        result = analyze_window(Report(folder), 102, 129.5)
        self.assertTrue(result['metrics']['audio_counter_reset'])
        self.assertIsNone(result['metrics']['audio_empty_dequeues_delta'])
        self.assertIn('gap in metrics', ' '.join(result['sustained_120']['unknowns']))
        self.assertEqual(result['sustained_120']['status'], 'inconclusive')

    def test_adequate_evidence_with_slowdown_or_audio_starvation_fails(self):
        folder = self.fixture()
        rows = self.json_rows(folder, 'metrics.jsonl')
        for row in rows:
            if row['host_seconds'] >= 110:
                row['audioDMAEmptyDequeues'] = 1
            if row['host_seconds'] == 110:
                row['speed'] = .95
        self.write_rows(folder, 'metrics.jsonl', rows)
        window = analyze_session(Report(folder))['trials'][0]['steady_windows'][0]
        self.assertEqual(window['sustained_120']['status'], 'failed')
        self.assertIn('audio starvation counter increased', window['sustained_120']['failures'])

    def test_common_clock_drift_and_missing_restore_are_inconclusive(self):
        folder = self.fixture()
        rows = self.json_rows(folder, 'native-trial.jsonl')
        rows[-1]['host_seconds'] += .02
        self.write_rows(folder, 'native-trial.jsonl', rows)
        result = analyze_session(Report(folder))
        self.assertIn('drift', ' '.join(result['trace_health']['unknowns']))
        self.assertEqual(result['trials'][0]['sustained_120_status'], 'inconclusive')
        self.write_rows(folder, 'native-trial.jsonl', rows[:-1])
        result = analyze_session(Report(folder))['trials'][0]
        self.assertFalse(result['restored'])
        self.assertEqual(result['functional_integrity']['status'], 'inconclusive')

    def test_full_half_comparison_is_equal_duration_and_never_claims_causality(self):
        full, half = Report(self.fixture()), Report(self.fixture('half', duration=31, scale=.5))
        result = compare_trials(full, half)
        self.assertEqual(result['comparison_validity']['status'], 'passed')
        self.assertEqual(result['full']['seconds'], result['half']['seconds'])
        self.assertEqual(result['equal_warmed_seconds'], 27.5)
        self.assertFalse(result['causal_speedup_established'])

    def test_mismatched_configs_and_internal_resolution_reject_comparison(self):
        full = Report(self.fixture())
        folder = self.fixture('half', scale=.5)
        launch = json.loads((folder/'launch.json').read_text())
        launch['cpuThread'] = True
        (folder/'launch.json').write_text(json.dumps(launch))
        rows = self.json_rows(folder, 'metrics.jsonl')
        for row in rows:
            row['efbWidth'] = 1280
        self.write_rows(folder, 'metrics.jsonl', rows)
        result = compare_trials(full, Report(folder))
        self.assertEqual(result['comparison_validity']['status'], 'failed')
        self.assertIn('config differs: cpuThread', result['comparison_validity']['failures'])
        self.assertIn('half internal resolution is not 640x528', result['comparison_validity']['failures'])

    def test_resize_inside_window_is_not_a_valid_configuration(self):
        folder = self.fixture()
        with (folder/'present.csv').open('a') as out:
            out.write('submit,9000,110,1434,660\ndisplay,9000,110.003,110.002,0\n')
        result = analyze_window(Report(folder), 102, 129.5)
        self.assertEqual(result['sustained_120']['status'], 'inconclusive')
        self.assertIn('drawable resolution', ' '.join(result['sustained_120']['unknowns']))

    def test_duplicate_display_callback_is_malformed_not_double_fps(self):
        folder = self.fixture()
        with (folder/'present.csv').open('a') as out:
            out.write('display,0,110,110,0\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate display'):
            Report(folder)

    def test_missing_runtime_log_cannot_pass_without_startup_evidence(self):
        folder = self.fixture()
        (folder/'runtime.log').unlink()
        result = analyze_session(Report(folder))['trials'][0]
        self.assertEqual(result['functional_integrity']['status'], 'inconclusive')
        self.assertEqual(result['sustained_120_status'], 'inconclusive')

    def test_null_and_wrong_typed_watched_values_are_unknown(self):
        folder = self.fixture()
        original = self.json_rows(folder, 'native-trial.jsonl')
        for field, value in (('position_changed', None), ('rng_changed', 0.0), ('body_offsets', None),
                             ('app_offsets', False), ('view_offsets', [3]), ('state_before', None),
                             ('state_after', False), ('same_rider', '1')):
            rows = [dict(row) for row in original]
            for row in rows:
                if row.get('event') == 'render':
                    row[field] = value
            self.write_rows(folder, 'native-trial.jsonl', rows)
            result = analyze_session(Report(folder))['trials'][0]
            self.assertEqual(result['functional_integrity']['status'], 'inconclusive', field)
            self.assertEqual(result['sustained_120_status'], 'inconclusive', field)

    def test_bracketing_audio_catches_boundary_starvation_without_claiming_exact_time(self):
        folder = self.fixture()
        rows = self.json_rows(folder, 'metrics.jsonl')
        for row in rows:
            row['audioDMAEmptyDequeues'] = int(row['host_seconds'] >= 103)
        self.write_rows(folder, 'metrics.jsonl', rows)
        result = analyze_window(Report(folder), 102.5, 129.5)
        self.assertEqual(result['metrics']['audio_in_window_snapshot_delta'], 0)
        self.assertEqual(result['metrics']['audio_empty_dequeues_delta'], 1)
        self.assertEqual(result['metrics']['audio_observed_host_span'], [102, 130])
        self.assertTrue(result['metrics']['audio_boundary_increase_unknown'])
        self.assertEqual(result['sustained_120']['status'], 'inconclusive')

    def test_one_unknown_efb_sample_does_not_establish_consistent_resolution(self):
        folder = self.fixture()
        original = self.json_rows(folder, 'metrics.jsonl')
        for value in (None, 0, -1, 640.5, True):
            rows = [dict(row) for row in original]
            next(row for row in rows if row['host_seconds'] == 110)['efbWidth'] = value
            self.write_rows(folder, 'metrics.jsonl', rows)
            result = analyze_window(Report(folder), 102, 129.5)
            self.assertEqual(result['metrics']['internal_sizes'], [(640, 528)])
            self.assertEqual(result['sustained_120']['status'], 'inconclusive')

    def test_disabled_audio_cannot_establish_phone_audio_integrity(self):
        folder = self.fixture()
        launch = json.loads((folder/'launch.json').read_text())
        launch['audioEnabled'] = False
        (folder/'launch.json').write_text(json.dumps(launch))
        result = analyze_window(Report(folder), 102, 129.5)
        self.assertEqual(result['sustained_120']['status'], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
