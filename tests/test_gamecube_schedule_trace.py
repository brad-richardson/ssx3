"""Reject false high-refresh evidence and exercise deadline overload behavior."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from gamecube_schedule_trace import summarize
from test_gamecube_native_trace import event

ROOT = Path(__file__).resolve().parents[1]


class ScheduleTraceTests(unittest.TestCase):
    def test_requests_and_rejected_callbacks_are_not_frames(self):
        rows = [dict(event='schedule', action='request', wall=150, pending=1, missed=4),
                event(repeat=1, result=0, duration_ms=1)]
        result = summarize(rows)
        self.assertEqual(result['complete_renders'], 0)
        self.assertEqual(result['complete_extras'], 0)
        self.assertEqual(result['attempted_extras'], 1)
        self.assertEqual(result['missed_deadlines'], 4)

    def test_independent_extra_need_not_follow_a_render_immediately(self):
        rows = [event('update'), event(repeat=1, result=1, view_matrix_calls=1,
                frame_end_calls=1, duration_ms=2, position_changed=1)]
        result = summarize(rows)
        self.assertEqual(result['complete_extras'], 1)
        self.assertEqual(result['extra_state_changes']['position_changed'], 1)

    def test_display_count_excludes_zero_timestamps_and_outside_window(self):
        rows = [dict(event='schedule', action='start', wall=140, host_seconds=1140,
                     ticks=0, pending=0)]
        presents = [['submit','1','1150','10','10'], ['display','1','1151','1150.5','0'],
                    ['display','2','1151','0','0'], ['display','3','1180','1180','0']]
        result = summarize(rows, presents=presents)['presentation']
        self.assertEqual(result['valid_displays'], 1)
        self.assertEqual(result['zero_display_timestamps'], 1)
        self.assertEqual(result['submits'], 1)

    def test_unaligned_presentations_cannot_produce_display_rate(self):
        self.assertIn('error', summarize([], presents=[])['presentation'])

    def test_only_zero_timestamps_means_unknown_display_rate(self):
        rows = [dict(event='schedule', action='start', wall=140, host_seconds=1140)]
        result = summarize(rows, presents=[['display','1','1150','0','0']])['presentation']
        self.assertIsNone(result['displays_per_second'])

    def test_wrong_clock_domain_is_not_reported_as_zero_frames(self):
        rows = [dict(event='schedule', action='start', wall=140, host_seconds=1140)]
        result = summarize(rows, presents=[['submit','1','2150','10','10']])['presentation']
        self.assertIn('error', result)

    def test_clock_drift_is_rejected(self):
        rows = [dict(event='schedule', action='start', wall=140, host_seconds=1140),
                dict(event='schedule', action='start', wall=175, host_seconds=1176)]
        with self.assertRaises(ValueError):
            summarize(rows, presents=[])

    @unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
    def test_compiled_policy_drops_late_work_and_preserves_phase(self):
        code = r'''
#include "native/diagnostics/render_deadline.h"
#include <cassert>
using namespace RenderResearch;
int main() {
 Deadline d{100,100,0};
 assert(d.Poll(99,0,0)==Decision::Early && d.next==100);
 assert(d.Poll(100,90,0)==Decision::Covered && d.next==200);
 assert(d.Poll(200,90,2)==Decision::Full && d.next==300);
 assert(d.Poll(799,90,1)==Decision::Render && d.missed==4 && d.next==800);
 assert(d.Poll(799,799,1)==Decision::Early); // no catch-up burst
 assert(d.Poll(800,799,1)==Decision::Covered && d.next==900);
 assert(d.Poll(900,799,3)==Decision::InvalidQueue);
 Deadline uninitialized{};
 assert(uninitialized.Poll(0,0,0)==Decision::InvalidQueue);
}
'''
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'policy.cpp'; source.write_text(code)
            binary=Path(temp)/'policy'
            subprocess.run(['c++','-std=c++17','-I',str(ROOT),str(source),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)


if __name__ == '__main__':
    unittest.main()
