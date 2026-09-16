"""Reject false high-refresh evidence and exercise deadline overload behavior."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
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
 RealTimeBudget budget{10,1000};
 assert(budget.Allows(10.02,1010,1000));  // a steady 10 ms throttle offset is allowed
 assert(budget.Allows(10.04,1030,1000));  // still 10 ms behind
 assert(!budget.Allows(10.06,1040,1000)); // debt grew to 20 ms: host falling behind
 assert(budget.Allows(10.08,1070,1000));  // recovered to the reference
 assert(budget.Allows(11.0,1960,1000));   // old minimum expired: a new steady offset passes
 assert(!budget.Allows(11.2,2140,1000));  // growth inside the window still blocks
 assert(!budget.Allows(9.9,1010,1000));
 assert(!budget.Allows(10.01,999,1000));
 assert(!budget.Allows(10.01,1010,0));
 SpeedFloor floor;
 assert(!floor.Allows());                  // no history: stay real-time
 for(unsigned i=0;i<41;++i)floor.Observe(i*0.025,uint64_t(i)*25000,1000000);
 assert(floor.Allows());                   // guest keeps pace: 1.0
 assert(floor.span>=0.5-1e-9);
 SpeedFloor slow;
 for(unsigned i=0;i<41;++i)slow.Observe(i*0.025,uint64_t(i)*15000,1000000);
 assert(!slow.Allows());                   // 0.6 speed blocks extras
 for(unsigned i=1;i<=32;++i)slow.Observe(1+i*.000002,600000+i*41,1000000);
 assert(!slow.Allows());                   // bursty idle visits cannot erase the slow window
 double wall=1.000064;uint64_t ticks=601312;
 auto advance=[&](double speed){
  for(unsigned i=0;i<41;++i){wall+=.025;ticks+=uint64_t(25000*speed);slow.Observe(wall,ticks,1000000);}
 };
 advance(.985);assert(!slow.Allows());      // hysteresis: not yet recovered
 advance(1.0);assert(slow.Allows());
 advance(.985);assert(slow.Allows());       // avoid toggling around one threshold
 advance(.96);assert(!slow.Allows());
 advance(1.0);assert(slow.Allows());
 slow.Observe(wall-1,ticks,1000000);assert(!slow.Allows()); // clock reset
 advance(1.0);assert(slow.Allows());
 slow.Observe(wall,0,1000000);assert(!slow.Allows());       // savestate rewind
 slow.Observe(wall,0,0);assert(!slow.Allows());
 SpeedFloor burst;
 for(unsigned i=0;i<1000;++i)burst.Observe(i*.000002,i*41,1000000);
 assert(!burst.Allows());                  // minimum elapsed warm-up
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
