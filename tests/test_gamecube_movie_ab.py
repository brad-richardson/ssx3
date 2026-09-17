"""Movie A/B compares same-trajectory plays by ordinal-aligned callback CPU."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import gamecube_movie_ab as ab


def probe_row(cpu=1.0, event='update', repeat=0, state=0, same=1, body=7):
    return dict(event=event, repeat=repeat, state_before=state, state_after=state,
                same_rider=same, cpu_duration_ms=cpu, position_changed=0,
                rng_changed=0, body_hash_before=body, body_hash_after=body)


def determinism(movie='movie', module='module'):
    return dict(movie_sha256=movie, module_sha256=module,
                evidence=dict(module_loaded=True, fallback_jit_runs=0,
                              invalid_memory_accesses=0, gpu_command_errors=0,
                              unknown_guest_instructions=0, shutdown_counters={}),
                execution_status=dict(exit_code=0, stopped_on_fault=None))


class MovieAbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_env_sets_clears_and_unsets(self):
        env, unset = ab.parse_env(['A=1', 'B=', 'C!'])
        self.assertEqual((env, unset), ({'A': '1', 'B': ''}, ['C']))
        with self.assertRaisesRegex(ValueError, 'KEY=VALUE'):
            ab.parse_env(['BARE'])
        merged = ab.apply_env({'A': '0', 'C': 'x', 'K': 'k'}, env, unset)
        self.assertEqual(merged, {'A': '1', 'B': '', 'K': 'k'})

    def test_stats_handles_single_and_multi_samples(self):
        one = ab.stats([4.0])
        self.assertEqual((one['mean'], one['stdev'], one['n']), (4.0, 0.0, 1))
        two = ab.stats([1.0, 3.0])
        self.assertAlmostEqual(two['mean'], 2.0)
        self.assertAlmostEqual(two['stdev'], 2.0 ** 0.5)

    def test_riding_series_keeps_ordinal_riding_callbacks(self):
        trace = self.root / 'probe.jsonl'
        rows = [probe_row(1.0), probe_row(2.0, event='render'),
                probe_row(9.0, repeat=1), probe_row(9.0, state=6),
                probe_row(9.0, same=0), dict(event='trial_test')]
        trace.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        series = ab.riding_series(trace, want_hashes=True)
        self.assertEqual([r['cpu_ms'] for r in series], [1.0, 2.0])
        self.assertEqual(series[0]['key'][-1], 7)
        plain = ab.riding_series(trace, want_hashes=False)
        self.assertEqual(len(plain[0]['key']), 4)
        trace.write_text(json.dumps(dict(probe_row(), cpu_duration_ms=None)) + '\n')
        with self.assertRaisesRegex(ValueError, 'cpu_duration_ms'):
            ab.riding_series(trace, want_hashes=True)
        trace.write_text('\n'.join(json.dumps(probe_row(1.0, state=s)) for s in (0, 6, 14)) + '\n')
        self.assertEqual(len(ab.riding_series(trace, want_hashes=True)), 1)
        self.assertEqual(len(ab.riding_series(trace, want_hashes=True, states=(6, 14))), 2)

    def test_check_player_verifies_receipt_and_locality(self):
        with mock.patch.object(ab, 'ROOT', self.root):
            player = self.root / 'local/player'
            player.mkdir(parents=True)
            (player / 'player').write_bytes(b'P')
            (player / 'run_native.py').write_bytes(b'L')
            (player / 'build.json').write_text(json.dumps(dict(
                player_sha256=ab.sha256(player / 'player'),
                launchers={'run_native.py': ab.sha256(player / 'run_native.py')})))
            self.assertIn('player_sha256', ab.check_player(player))
            (player / 'player').write_bytes(b'TAMPERED')
            with self.assertRaisesRegex(ValueError, 'build receipt'):
                ab.check_player(player)
            with self.assertRaisesRegex(ValueError, 'under local'):
                ab.check_player(self.root / 'elsewhere')

    def test_swapped_player_rewrites_only_the_runtime_launch(self):
        target = str(ab.ROOT / 'tools/native_gamecube.py')
        other = [sys.executable, '-c', 'pass']
        with mock.patch('subprocess.Popen') as popen:
            with ab.swapped_player('/tmp/player'):
                import gamecube_course_check as course
                course.subprocess.Popen([sys.executable, target, 'run'])
                course.subprocess.Popen(other)
        first = popen.call_args_list[0].args[0]
        self.assertEqual(first[1], str(Path('/tmp/player/run_native.py').resolve()))
        self.assertEqual(popen.call_args_list[1].args[0], other)

    def test_run_alternates_arms_and_stops_on_failure(self):
        movie = self.root / 'movie.dtm'
        movie.write_bytes(b'M')
        args = SimpleNamespace(movie=movie, game=self.root, output=self.root / 'ab',
                               rounds=2, seconds=200, player_dir=None, module=None,
                               course_manifest=None, screenshot_seconds=None,
                               profile_prefix='p', probe=False, signposts=False,
                               pc_hist=False, quiet=False, env=['S=0'], min_disk_bytes=0,
                               env_a=['A=1'], env_b=['B=2'])
        with mock.patch.object(ab, 'one_run', return_value=0) as run, \
                mock.patch.object(ab, 'finish') as finish:
            manifest = ab.run(args)
        labels = [call.args[4] for call in run.call_args_list]
        self.assertEqual(labels, ['round0-a', 'round0-b', 'round1-b', 'round1-a'])
        arm_envs = [call.args[3] for call in run.call_args_list]
        self.assertEqual(arm_envs[0][0], {'S': '0', 'A': '1'})
        self.assertEqual(arm_envs[1][0], {'S': '0', 'B': '2'})
        self.assertEqual(manifest['env_shared'], ['S=0'])
        self.assertEqual(len(manifest['runs']), 4)
        self.assertEqual(manifest['movie_sha256'], ab.sha256(movie))
        self.assertEqual(finish.call_count, 4)
        args.output = self.root / 'ab2'
        with mock.patch.object(ab, 'one_run', side_effect=[0, 1]), \
                mock.patch.object(ab, 'finish'), \
                self.assertRaisesRegex(SystemExit, 'round0-b'):
            ab.run(args)
        self.assertEqual(len(json.loads((self.root / 'ab2/manifest.json').read_text())['runs']), 2)
        args.output = self.root / 'ab3'
        with mock.patch.object(ab, 'one_run', side_effect=RuntimeError('observer died')), \
                mock.patch.object(ab, 'finish'), \
                self.assertRaisesRegex(SystemExit, 'round0-a'):
            ab.run(args)
        manifest = json.loads((self.root / 'ab3/manifest.json').read_text())
        self.assertEqual(manifest['runs'][0]['crashed'], 'RuntimeError: observer died')
        self.assertEqual(manifest['runs'][0]['exit_code'], 1)

    def test_one_run_invokes_course_check_in_process_with_arm_env(self):
        movie = self.root / 'movie.dtm'
        movie.write_bytes(b'M')
        output = self.root / 'run'
        output.mkdir()
        args = SimpleNamespace(movie=movie, game=self.root, seconds=200, player_dir=self.root,
                               module=None, course_manifest=None, screenshot_seconds=None,
                               probe=True, signposts=True, pc_hist=False, quiet=True)
        seen = {}

        def capture():
            seen['argv'] = list(sys.argv)
            seen['env'] = dict(os.environ)
            seen['swapped'] = ab.course.subprocess.Popen.__name__ == 'launch'

        old_argv, old_env = list(sys.argv), dict(os.environ)
        with mock.patch.object(ab.course, 'main', side_effect=capture):
            code = ab.one_run(args, output, 'prof', ({'EXTRA': '1'}, []), 'round0-a')
        self.assertEqual(code, 0)
        self.assertIn('--profile', seen['argv'])
        self.assertIn('prof', seen['argv'])
        self.assertIn('--metal-validation', seen['argv'])
        self.assertIn('off', seen['argv'])
        self.assertEqual(seen['env']['SSX3_MOVIE_PLAY'], str(movie.resolve()))
        self.assertEqual(seen['env']['SSX_NATIVE_PROBE'], str(output / 'probe.jsonl'))
        self.assertEqual(seen['env']['SSX_NATIVE_SIGNPOSTS'], str(output / 'signposts.json'))
        self.assertNotIn('SSX_NATIVE_PC_HIST', seen['env'])
        self.assertEqual(seen['env']['SSX_NATIVE_QUIET'], '1')
        self.assertEqual(seen['env']['EXTRA'], '1')
        self.assertTrue(seen['swapped'])
        self.assertEqual(list(sys.argv), old_argv)
        self.assertEqual(dict(os.environ), old_env)
        with mock.patch.object(ab.course, 'main', side_effect=SystemExit(3)):
            self.assertEqual(ab.one_run(args, output, 'prof', ({}, []), 'x'), 3)
        (output / 'probe.jsonl').write_bytes(b'taken')
        with mock.patch.object(ab.course, 'main'):
            with self.assertRaisesRegex(ValueError, 'Preserving existing'):
                ab.one_run(args, output, 'prof', ({}, []), 'x')

    def test_run_refuses_without_disk_headroom(self):
        movie = self.root / 'm'
        movie.write_bytes(b'M')
        args = SimpleNamespace(movie=movie, game=self.root, env=[], env_a=[], env_b=[],
                               output=self.root / 'ab', rounds=1, seconds=200, probe=False,
                               player_dir=None, min_disk_bytes=10**18)
        with self.assertRaisesRegex(ValueError, 'free'):
            ab.run(args)
        self.assertFalse((self.root / 'ab').exists())

    def test_run_rejects_probe_without_player(self):
        args = SimpleNamespace(movie=self.root / 'm', game=self.root, env=[],
                               output=self.root / 'ab', rounds=1, player_dir=None, probe=True)
        (self.root / 'm').write_bytes(b'M')
        with self.assertRaisesRegex(ValueError, '--probe needs --player-dir'):
            ab.run(args)

    def make_compare_dir(self, cpus, states=0, prefix_profiles=True, dirname='ab'):
        """cpus: {run_name: (arm, cpu_per_callback, count)}."""
        output = self.root / dirname
        runs = []
        for name, (arm, cpu, count) in cpus.items():
            run_dir = output / name
            run_dir.mkdir(parents=True)
            rows = [probe_row(cpu, state=states if not isinstance(states, dict) else states[name])
                    for _ in range(count)]
            (run_dir / 'probe.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
            det = determinism()
            (run_dir / 'determinism.json').write_text(json.dumps(det))
            runs.append(dict(name=name, arm=arm, profile=f'{dirname}-{name}', exit_code=0, determinism=det))
        (output / 'manifest.json').write_text(json.dumps(dict(
            schema=1, movie_sha256='movie', rounds=2, quiet=False,
            env_a=['SSX3_IDLE_PC=0x80288ED4'], env_b=['SSX3_IDLE_PC='],
            runs=runs)))
        if prefix_profiles:
            for run in runs:
                config = self.root / 'local/native/profiles' / run['profile'] / 'Config'
                config.mkdir(parents=True)
                idle = '0x80288ED4' if run['arm'] == 'a' else ''
                (config / 'Dolphin.ini').write_text(
                    f'[Core]\nCPUThread = False\nStaticRecompIdlePC = {idle}\n[Analytics]\nID = {run["name"]}\n')
        return output

    def test_compare_resolves_consistent_one_percent_delta(self):
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 1.01, 1200),
                'round1-a': ('a', 1.0, 1200), 'round1-b': ('b', 1.01, 1200)}
        output = self.make_compare_dir(cpus)
        with mock.patch.object(ab, 'ROOT', self.root):
            result = ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0]))
        self.assertTrue(result['gate_passed'])
        self.assertTrue(result['resolved'])
        self.assertAlmostEqual(result['delta_pct'], 1.0)
        self.assertTrue(result['sign_consistent'])
        self.assertEqual(len(result['round_pairs']), 2)
        self.assertTrue((output / 'ab_report.json').exists())

    def test_compare_rejects_divergent_fingerprints(self):
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 1.01, 1200),
                'round1-a': ('a', 1.0, 1200), 'round1-b': ('b', 1.01, 1200)}
        output = self.make_compare_dir(cpus)
        drifted = output / 'round0-b/probe.jsonl'
        rows = [json.loads(line) for line in drifted.read_text().splitlines()]
        rows[500]['body_hash_before'] = 999
        drifted.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        with mock.patch.object(ab, 'ROOT', self.root), self.assertRaises(SystemExit) as stop:
            ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0]))
        self.assertEqual(stop.exception.code, 1)
        report = json.loads((output / 'ab_report.json').read_text())
        self.assertFalse(report['resolved'])
        self.assertTrue(any('diverge' in i for i in report['issues']))

    def test_compare_gates_mixed_quiet_arms_on_states_and_flags(self):
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 0.9, 1200),
                'round1-a': ('a', 1.0, 1200), 'round1-b': ('b', 0.9, 1200)}
        output = self.make_compare_dir(cpus)
        for name in ('round0-b', 'round1-b'):
            path = output / name / 'probe.jsonl'
            rows = [dict(json.loads(line), body_hash_before=0, body_hash_after=0)
                    for line in path.read_text().splitlines()]
            path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
        with mock.patch.object(ab, 'ROOT', self.root):
            result = ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0],
                                                allow_single_round=False))
        self.assertTrue(result['gate_passed'])
        self.assertIn('quiet', result['gate_strength'])
        self.assertTrue(result['resolved'])
        self.assertLess(result['delta_pct'], 0)

    def test_compare_requires_replication_or_explicit_single_round(self):
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 1.01, 1200)}
        output = self.make_compare_dir(cpus)
        (output / 'manifest.json').write_text(json.dumps(dict(
            json.loads((output / 'manifest.json').read_text()), rounds=1)))
        with mock.patch.object(ab, 'ROOT', self.root):
            with self.assertRaises(SystemExit):
                ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0],
                                           allow_single_round=False))
            report = json.loads((output / 'ab_report.json').read_text())
            self.assertFalse(report['resolved'])
            self.assertIn('provisional', report['confidence'])
            result = ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0],
                                                allow_single_round=True))
            self.assertTrue(result['resolved'])

    def test_compare_rejects_short_prefix_and_config_drift(self):
        cpus = {'round0-a': ('a', 1.0, 100), 'round0-b': ('b', 1.01, 100)}
        output = self.make_compare_dir(cpus)
        (output / 'manifest.json').write_text(json.dumps(dict(
            json.loads((output / 'manifest.json').read_text()), rounds=1)))
        with mock.patch.object(ab, 'ROOT', self.root), self.assertRaises(SystemExit):
            ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0]))
        report = json.loads((output / 'ab_report.json').read_text())
        self.assertTrue(any('prefix' in i for i in report['issues']))
        # Config drift beyond the declared idle knob also fails the gate.
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 1.01, 1200)}
        output = self.make_compare_dir(cpus, dirname='ab-drift')
        bad = self.root / 'local/native/profiles/ab-drift-round0-b/Config/Dolphin.ini'
        bad.write_text(bad.read_text() + 'CPUThread = True\n')
        with mock.patch.object(ab, 'ROOT', self.root), self.assertRaises(SystemExit):
            ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0]))
        report = json.loads((output / 'ab_report.json').read_text())
        self.assertTrue(any('Core configs' in i for i in report['issues']))

    def test_host_monitor_samples_context_until_exit(self):
        path = self.root / 'host.jsonl'
        sample = dict(t=1.0, loadavg=[2.0, 1.0, 0.5], moderngekko=1, compilers=0, thermal='ok')
        with mock.patch.object(ab, 'host_sample', return_value=sample):
            import time as time_module
            with ab.host_monitor(path, interval=0.01):
                deadline = time_module.time() + 10
                while ((not path.exists() or not path.read_text().strip())
                       and time_module.time() < deadline):
                    time_module.sleep(0.05)
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(rows[0]['moderngekko'], 1)

    def test_host_monitor_waits_for_late_run_directory(self):
        path = self.root / 'late' / 'host.jsonl'
        sample = dict(t=1.0, loadavg=[2.0, 1.0, 0.5], moderngekko=1, compilers=0, thermal='ok')
        with mock.patch.object(ab, 'host_sample', return_value=sample):
            import time as time_module
            with ab.host_monitor(path, interval=0.01):
                path.parent.mkdir(parents=True)
                deadline = time_module.time() + 5
                while ((not path.exists() or not path.read_text().strip())
                       and time_module.time() < deadline):
                    time_module.sleep(0.05)
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertGreaterEqual(len(rows), 1)

    def test_host_sample_counts_emulators_and_compilers(self):
        patterns = []

        def fake_run(command, **kwargs):
            if command[0] == 'pmset':
                return mock.Mock(stdout='No thermal warning', stderr='', returncode=0)
            patterns.append(command[-1])
            out = '2' if 'moderngekko' in command[-1] else ''
            code = 0 if out else 1
            return mock.Mock(stdout=out, stderr='', returncode=code)
        with mock.patch.object(ab.subprocess, 'run', side_effect=fake_run), \
                mock.patch.object(ab.os, 'getloadavg', return_value=(9.0, 8.0, 7.0)):
            sample = ab.host_sample()
        self.assertEqual(sample['moderngekko'], 2)
        self.assertEqual(sample['compilers'], 0)
        self.assertEqual(sample['loadavg'][0], 9.0)
        # The emulator pattern must catch isolated players too, not only the
        # production runner name, or the concurrency gate is blind.
        import re
        emulator = next(p for p in patterns if 'moderngekko' in p)
        self.assertTrue(re.search(emulator, '/x/moderngekko-run --game g'))
        self.assertTrue(re.search(emulator, '/x/player/player --game g'))
        self.assertFalse(re.search(emulator, '/x/replay_video --game g'))

    def test_compare_fails_gate_on_concurrent_emulator(self):
        cpus = {'round0-a': ('a', 1.0, 1200), 'round0-b': ('b', 1.01, 1200)}
        output = self.make_compare_dir(cpus)
        (output / 'manifest.json').write_text(json.dumps(dict(
            json.loads((output / 'manifest.json').read_text()), rounds=1)))
        (output / 'round0-b/host.jsonl').write_text(json.dumps(dict(
            t=1.0, loadavg=[20.0, 1.0, 1.0], moderngekko=2, compilers=3, thermal='x')) + '\n')
        with mock.patch.object(ab, 'ROOT', self.root), self.assertRaises(SystemExit):
            ab.compare(SimpleNamespace(output=output, min_callbacks=1000, states=[0]))
        report = json.loads((output / 'ab_report.json').read_text())
        self.assertFalse(report['gate_passed'])
        self.assertTrue(any('concurrently' in i for i in report['issues']))
        self.assertTrue(any('round0-b' in w for w in report['host_warnings']))

    def test_calibrate_pins_idle_knob_and_chains_run_compare(self):
        args = SimpleNamespace(profile_prefix='dctx-cal')
        with mock.patch.object(ab, 'run') as run, mock.patch.object(ab, 'compare') as compare:
            ab.calibrate(args)
        self.assertEqual(args.env_a, ['SSX3_IDLE_PC=0x80288ED4'])
        self.assertEqual(args.env_b, ['SSX3_IDLE_PC='])
        run.assert_called_once_with(args)
        compare.assert_called_once_with(args)


if __name__ == '__main__':
    unittest.main()
