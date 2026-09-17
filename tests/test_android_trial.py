"""Android trial port: TU wiring, config seeding, launch and acceptance."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import android_trial as trial


TU = ('#include "Core/Core.h"\n'
      'namespace\n{\n'
      'void Run() {\n'
      '          const u32 runtime_dispatch_address = m_guest.pc;\n'
      '}\n'
      '}\n')


def trial_row(action, wall, kind=0, status=0, **extra):
    row = dict(event='android_trial', action=action, wall=wall, kind=kind,
               status=status, frames=10, extras=4, doubled=0, blended=2,
               limited=0)
    row.update(extra)
    return row


def render_row(wall, repeat=1, **extra):
    row = dict(event='render', wall=wall, repeat=repeat, result=255,
               view_matrix_calls=3, frame_end_calls=1, same_rider=1,
               same_view=1, state_before=0, state_after=0, rng_changed=0,
               position_changed=0, body_offsets=[], app_offsets=[],
               view_offsets=[])
    row.update(extra)
    return row


class AndroidTrialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_trial_env_validates_kind_and_times(self):
        env = trial.trial_env(134.0, 'combined', 8)
        self.assertEqual(env, {'SSX_ANDROID_TRIAL_AT': '134.0',
                               'SSX_ANDROID_TRIAL_KIND': 'combined',
                               'SSX_ANDROID_TRIAL_SECS': '8.0'})
        control = trial.trial_env(None, 'smoothing', 0)
        self.assertNotIn('SSX_ANDROID_TRIAL_AT', control)
        with self.assertRaisesRegex(ValueError, 'kind'):
            trial.trial_env(1, 'bogus', 0)
        with self.assertRaisesRegex(ValueError, 'at'):
            trial.trial_env(-1, 'f', 0)
        with self.assertRaisesRegex(ValueError, 'secs'):
            trial.trial_env(1, 'f', -2)

    def test_screenshot_env_zero_disables_by_omission(self):
        env = trial.screenshot_env(2)
        self.assertEqual(env, {'SSX3_SCREENSHOTS': '1',
                               'SSX3_SCREENSHOT_SECONDS': '2'})
        # The runner captures on presence, so 0 must omit the key entirely.
        self.assertEqual(trial.screenshot_env(0), {})
        with self.assertRaisesRegex(ValueError, 'Screenshot seconds'):
            trial.screenshot_env(-1)

    def test_seed_gfx_ini_preserves_settings_and_updates_hacks(self):
        before = ('[Settings]\nInternalResolution = 1\nShaderCache = True\n'
                  '[Hacks]\nImmediateXFBEnable = False\n')
        after = trial.seed_gfx_ini(before)
        self.assertIn('[Settings]\nInternalResolution = 1\nShaderCache = True\n', after)
        self.assertIn('ImmediateXFBEnable = True', after)
        self.assertIn('CapImmediateXFB = False', after)
        self.assertNotIn('ImmediateXFBEnable = False', after)
        seeded = trial.seed_gfx_ini('[Settings]\nInternalResolution = 1\n')
        self.assertIn('[Hacks]\nImmediateXFBEnable = True\nCapImmediateXFB = False\n', seeded)
        off = trial.seed_gfx_ini(before, immediate=False)
        self.assertIn('ImmediateXFBEnable = False', off)

    def test_generate_trial_source_wires_seams_exactly_once(self):
        out = trial.generate_trial_source(TU, self.root)
        self.assertTrue(out.startswith(trial.TRIAL_DEFINE))
        for name in trial.INCLUDE_ORDER:
            self.assertEqual(out.count(f'#include "{self.root / name}"'), 1)
        self.assertEqual(out.count(trial.STEP_CALL), 1)
        self.assertEqual(out.count(trial.DISPATCH_MARKER), 1)
        with self.assertRaisesRegex(ValueError, 'injection point'):
            trial.generate_trial_source('no seams here', self.root)
        with self.assertRaisesRegex(ValueError, 'injection point'):
            trial.generate_trial_source(TU + TU, self.root)

    def test_adapt_compile_command_retargets_source_and_object(self):
        argv = trial.adapt_compile_command(
            'clang++ -O3 -MF dep.d -MT target -o build/tu.o -c src/tu.cpp',
            self.root / 'Core_Run.cpp', self.root / 'trial.o')
        self.assertEqual(argv[-4:], ['-o', str(self.root / 'trial.o'),
                                     '-c', str(self.root / 'Core_Run.cpp')])
        self.assertNotIn('-MF', argv)
        self.assertNotIn('-MT', argv)
        self.assertIn('-O3', argv)

    def test_link_commands_parse_and_shadow_first_archive(self):
        text = ('cd /b && clang++ a.o -o moderngekko-run libx.a libcore.a && echo done\n'
                'clang++ -o other liby.a\n')
        argv = trial.parse_link_command(text)
        self.assertEqual(argv[:2], ['clang++', 'a.o'])
        adapted = trial.adapt_link_command(argv, self.root / 'trial.o',
                                           self.root / 'moderngekko-run-trial')
        self.assertEqual(adapted[adapted.index('-o') + 1],
                         str(self.root / 'moderngekko-run-trial'))
        self.assertLess(adapted.index(str(self.root / 'trial.o')),
                        adapted.index('libx.a'))
        with self.assertRaisesRegex(ValueError, 'link command'):
            trial.parse_link_command('clang++ -o other liby.a\n')
        with self.assertRaisesRegex(ValueError, 'archive'):
            trial.adapt_link_command(['clang++', 'a.o', '-o', 'out'], 't.o', 'n')

    def test_launch_command_backgrounds_a_bounded_headless_run(self):
        line = trial.launch_command('t1', dict(A='1', B='2'), 'user-t1',
                                    'mod.so', 240)
        self.assertIn('cd /data/local/tmp/mg;', line)
        self.assertIn('A=1 B=2 timeout 240 ./moderngekko-run-trial', line)
        self.assertIn('--headless --graphics OGL', line)
        self.assertIn('--user-dir /data/local/tmp/mg/user-t1', line)
        self.assertTrue(line.rstrip().endswith('& echo $!'))

    def test_analyze_accepts_a_full_smoothing_lifecycle(self):
        rows = [trial_row('configured', 0),
                trial_row('request', 134.0),
                trial_row('status', 134.5, status=2, **{'from': 1, 'to': 2}),
                dict(event='schedule', action='start', wall=134.5),
                dict(event='schedule', action='completion_mode', wall=134.5),
                dict(event='schedule', action='request', wall=135.0),
                dict(event='schedule', action='extra_complete', wall=135.1),
                render_row(135.1),
                dict(event='interpolation', wall=135.1, repeat=1, blended=3),
                trial_row('cancel', 142.0, status=2),
                trial_row('status', 142.1, status=3, **{'from': 2, 'to': 3}),
                trial_row('complete', 142.1, status=3)]
        stderr = ('[ssx3-metrics] sample=135 fps=0.000 vps=0.000 speed=1.000000\n'
                  'FIFO is overflowed by GatherPipe !\n')
        result = trial.analyze_probe(rows, stderr, shots=9)
        self.assertTrue(result['pass'], result['issues'])
        self.assertEqual((result['complete_extras'], result['blended_extras']), (1, 1))
        self.assertTrue(result['finished'])
        self.assertTrue(result['panic'])
        self.assertEqual(result['screenshots'], 9)
        self.assertEqual(result['trial_window_speeds']['min'], 1.0)

    def test_analyze_rejects_missing_running_and_dirty_extras(self):
        waiting = [trial_row('configured', 0), trial_row('request', 134.0),
                   trial_row('status', 134.5, status=1, **{'from': 0, 'to': 1})]
        result = trial.analyze_probe(waiting)
        self.assertFalse(result['pass'])
        self.assertIn('never reached Running', ' '.join(result['issues']))
        dirty = [trial_row('configured', 0), trial_row('request', 134.0),
                 trial_row('status', 134.5, status=2, **{'from': 1, 'to': 2}),
                 render_row(135.1, position_changed=1)]
        result = trial.analyze_probe(dirty)
        self.assertFalse(result['pass'])
        self.assertIn('watched guest state', ' '.join(result['issues']))

    def test_analyze_checks_f_consts_and_flags_missing_setup(self):
        rows = [trial_row('configured', 0, kind=1),
                trial_row('request', 134.0, kind=1),
                trial_row('status', 134.5, status=2, **{'from': 1, 'to': 2}),
                dict(event='f_trial', action='patched', wall=134.6),
                dict(event='update', wall=135.0, repeat=1),
                dict(event='f_trial', action='restored', wall=142.0),
                trial_row('status', 142.1, status=3, **{'from': 2, 'to': 3}),
                trial_row('complete', 142.1, status=3)]
        result = trial.analyze_probe(rows)
        self.assertTrue(result['pass'], result['issues'])
        self.assertTrue(result['consts_ok'])
        bad = [trial_row('configured', 0),
               dict(event='schedule', action='invalid_immediate_copy_setup',
                    wall=134.5)]
        result = trial.analyze_probe(bad)
        self.assertIn('Immediate-XFB', ' '.join(result['issues']))

    def test_ensure_idle_quotes_spaced_patterns_as_one_argv(self):
        seen = []

        def fake_adb(argv, serial=None, check=True, timeout=None):
            seen.append(argv)
            if argv[1].startswith('grep '):
                return SimpleNamespace(stdout='StaticRecompIdlePC = 0x80288ED4\n')
            return SimpleNamespace(stdout='0\n')
        with mock.patch.object(trial, 'adb', side_effect=fake_adb):
            trial.ensure_idle('serial', 'user-x', True)
            trial.ensure_idle('serial', 'user-x', False)
        # Spaced patterns travel as one argv element; spaceless calls stay split.
        self.assertEqual(len(seen), 3)
        self.assertEqual(seen[0], ['shell', "grep '^StaticRecompIdlePC = ' "
                                             '/data/local/tmp/mg/user-x/Config/Dolphin.ini'])
        self.assertEqual(seen[1], ['shell', "sed -i '/^StaticRecompIdlePC = /d' "
                                             '/data/local/tmp/mg/user-x/Config/Dolphin.ini'])
        self.assertEqual(seen[2][:3], ['shell', 'grep', '-c'])

    def test_build_refuses_repo_output_and_checks_the_game(self):
        game = self.root / 'game'
        (game / 'sys').mkdir(parents=True)
        (game / 'sys/boot.bin').write_bytes(b'GXBE69x')
        (game / 'sys/main.dol').write_bytes(b'dol')
        args = SimpleNamespace(game=game, build_dir=self.root,
                               output=trial.ROOT / 'local/x', ninja=None)
        with self.assertRaisesRegex(ValueError, 'pinned GXBE69'):
            trial.build(args)
        (game / 'sys/main.dol').write_bytes(b'dol')
        with mock.patch.object(trial, 'DOL_SHA256', trial.sha(game / 'sys/main.dol')):
            with self.assertRaisesRegex(ValueError, 'outside the repo'):
                trial.build(args)

    def test_reconstruct_tu_applies_the_stack_in_order(self):
        calls = []

        def runner(argv, **kw):
            calls.append(argv)
            return SimpleNamespace(stdout='')
        with mock.patch.object(trial.tempfile, 'mkdtemp',
                               return_value=str(self.root / 'wt')):
            tu = self.root / 'wt' / 'tree' / trial.TU_RELATIVE
            tu.parent.mkdir(parents=True, exist_ok=True)
            tu.write_text('TU-SOURCE')
            with mock.patch.object(trial.shutil, 'rmtree'):
                self.assertEqual(trial.reconstruct_tu(runner), 'TU-SOURCE')
        self.assertEqual(calls[0][3:5], ['worktree', 'add'])
        self.assertEqual(calls[0][-1], trial.PINS['recompcore_revision'])
        applied = [c[-1] for c in calls[1:-1]]
        self.assertEqual(applied, [str(trial.ROOT / 'native/patches' / n)
                                   for n in trial.INNER_ANDROID_STACK])
        self.assertEqual(calls[-1][3:5], ['worktree', 'remove'])


if __name__ == '__main__':
    unittest.main()

