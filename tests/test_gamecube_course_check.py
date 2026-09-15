import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gamecube_course_check
from gamecube_course_check import reset_events, reset_loops


def sample(t, state, surface, flags=0):
    return dict(t=t,state=state,surface=surface,terrain_flags=flags)


def riding(start, count=5):
    return [sample(start+i,0,0) for i in range(count)]


class CourseCheckTests(unittest.TestCase):
    def test_wipeout_without_reset_is_not_recovery(self):
        self.assertEqual(reset_events([sample(1,8,18),sample(2,0,0)]),[])

    def test_require_recent_hazard_and_sustained_ordinary_ground_contact(self):
        r=[sample(1,0,0,11),sample(4,9,0,11),sample(4.1,9,0)]+riding(5)
        events=reset_events(r)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['hazard'],r[0])
        self.assertEqual(events[0]['recovered'],r[3])
        self.assertIsNone(reset_events([sample(1,8,18),sample(20,9,0)])[0]['hazard'])
        self.assertIsNone(reset_events(r[:4])[0]['recovered'])

    def test_repeated_reset_sequences_stay_separate(self):
        r=[sample(1,8,18),sample(4,9,18)]+riding(5)+[sample(10,8,18),sample(13,9,18)]+riding(14)
        self.assertEqual(len(reset_events(r)),2)
        self.assertTrue(all(e['recovered'] for e in reset_events(r)))

    def test_aerial_recovery_and_immediate_reset_loop_are_not_success(self):
        r=[sample(1,8,18),sample(4,9,18),sample(5,4,0),sample(6,0,0),sample(7,8,18),sample(8,9,18)]
        self.assertTrue(all(e['recovered'] is None for e in reset_events(r)))

    def test_three_failed_nearby_resets_are_a_loop(self):
        r=[sample(t,s,18 if s==9 else 0) for t,s in [(1,9),(2,4),(4,9),(5,4),(7,9),(8,4)]]
        self.assertTrue(reset_loops(reset_events(r)))


class RestartArgumentTests(unittest.TestCase):
    """The restart bounds are rejected before any profile or output is created."""

    def run_main(self, *extra, profile='p'):
        argv = ['gamecube_course_check.py', '--game', 'g', '--profile', profile,
                '--output', 'o', *extra]
        with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit):
                gamecube_course_check.main()
        return err.getvalue()

    def test_restart_must_leave_time_to_ride_again(self):
        self.assertIn('leave 120 seconds', self.run_main('--seconds', '200', '--restart-after', '100'))
        self.assertIn('at least 5 riding seconds', self.run_main('--seconds', '400', '--restart-after', '4'))

    def test_restart_at_the_bounds_passes_validation(self):
        # The profile check follows the restart check, so reaching it means the
        # bounds were accepted; a rejected profile stops before any run starts.
        for after in ('280', '5'):
            self.assertIn('isolated profile',
                          self.run_main('--seconds', '400', '--restart-after', after,
                                        profile='../escape'))


class CourseManifestTests(unittest.TestCase):
    def parse(self, text):
        return gamecube_course_check.parse_course_manifest(text)

    def test_parses_a_full_redirect(self):
        self.assertEqual(self.parse('''
            # Snow Jam -> Aloha
            event = 0
            archive = ALOHA
            code = ASS1
            name = Aloha Ice Jam
            short = Aloha
            location = 5
            mode = 3
        '''), [dict(event=0, archive='ALOHA', code='ASS1', name='Aloha Ice Jam',
                    short='Aloha', location=5, mode=3)])

    def test_several_event_blocks(self):
        self.assertEqual(self.parse('event = 0\narchive = GARI\nevent = 5\nmode = 2\n'),
                         [dict(event=0, archive='GARI'), dict(event=5, mode=2)])

    def test_values_keep_their_spaces_but_not_their_padding(self):
        self.assertEqual(self.parse('event = 0\nname =   Snow  Jam  \n')[0]['name'], 'Snow  Jam')

    def reject(self, text):
        with self.assertRaises(ValueError) as caught:
            self.parse(text)
        return str(caught.exception)

    def test_rejects_an_out_of_range_event(self):
        self.assertIn('[0,23)', self.reject('event = 23\nmode = 2\n'))

    def test_rejects_a_field_that_cannot_hold_a_terminator(self):
        # 15 bytes plus the NUL exactly fills the 16-byte archive field.
        self.assertEqual(self.parse('event = 0\narchive = ' + 'A'*15)[0]['archive'], 'A'*15)
        self.assertIn('16 bytes', self.reject('event = 0\narchive = ' + 'A'*16))
        self.assertIn('32 bytes', self.reject('event = 0\nname = ' + 'A'*32))

    def test_rejects_non_ascii_and_control_bytes(self):
        self.assertIn('printable ASCII', self.reject('event = 0\nname = Aloha’s\n'))

    def test_rejects_an_out_of_range_location_or_mode(self):
        self.assertIn('[0,50)', self.reject('event = 0\nlocation = 50\n'))
        self.assertIn('1..6', self.reject('event = 0\nmode = 0\n'))
        self.assertIn('[0,7)', self.reject('event = 0\nmode = 7\n'))

    def test_rejects_structural_mistakes(self):
        self.assertIn('before any', self.reject('archive = BAM\n'))
        self.assertIn('unknown key', self.reject('event = 0\npeak = 1\n'))
        self.assertIn('repeated', self.reject('event = 0\nmode = 2\nmode = 3\n'))
        self.assertIn('not key = value', self.reject('event = 0\nmode 3\n'))
        self.assertIn('no events', self.reject('# nothing here\n'))
        self.assertIn('at least one field', self.reject('event = 0\n'))

    def test_main_rejects_a_bad_manifest_before_running(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory)/'course.txt'
            manifest.write_text('event = 99\n')
            self.assertIn('--course-manifest',
                          RestartArgumentTests.run_main(self, '--course-manifest', str(manifest)))
