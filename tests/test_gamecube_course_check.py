import unittest
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
