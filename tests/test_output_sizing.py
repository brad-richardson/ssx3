"""Check measured presentation geometry and trial readiness without UIKit."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
class OutputSizingTests(unittest.TestCase):
    def compile_and_run(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'sizing.cpp'
            path.write_text(source)
            binary = Path(directory)/'sizing'
            subprocess.run(['c++', '-std=c++17', '-I', str(ROOT), str(path), '-o', str(binary)],
                           check=True, capture_output=True, text=True)
            subprocess.run([str(binary)], check=True, capture_output=True, text=True)

    def test_visible_source_height_bars_and_native_cap(self):
        source = r'''
#include "native/ios/OutputSizing.h"
#include <cassert>
#include <limits>
int main() {
  auto two=SSXOutput::Match(2868,1320,1556,896);
  assert(two.width==1947 && two.height==896 && !two.capped);
  auto one=SSXOutput::Match(2868,1320,778,448);
  assert(one.width==973 && one.height==448 && !one.capped);
  assert(std::abs(two.scale-896.0/1320)<1e-12);
  auto narrow=SSXOutput::Match(1000,1000,778,448);
  assert(narrow.width==778 && narrow.height==778); // bars above and below
  auto capped=SSXOutput::Match(800,600,1556,896);
  assert(capped.width==800 && capped.height==600 && capped.capped);
  assert(SSXOutput::Match(2868,1320,0,896).width==0);
  assert(SSXOutput::Match(2868,1320,1556,-1).width==0);
  assert(SSXOutput::Match(0,1320,1556,896).width==0);
  assert(SSXOutput::Match(std::numeric_limits<double>::quiet_NaN(),1320,1556,896).width==0);
  assert(SSXOutput::Match(1e30,1320,1556,896).width==0);
}
'''
        self.compile_and_run(source)

    def test_trial_waits_for_measured_detail_and_resized_output(self):
        self.compile_and_run(r'''
#include "native/ios/OutputSizing.h"
#include <cassert>
#include <limits>
int main() {
  // A paused 1x -> 2x edit must not start a fixed-output trial using the old
  // EFB, a stale timestamp, or only the first newly sized presentation.
  assert(!SSXOutput::SourceReady(778,448,640,528,3,11,10,2));
  assert(!SSXOutput::SourceReady(1556,896,1280,1056,3,9,10,2));
  assert(!SSXOutput::SourceReady(1556,896,1280,1056,1,11,10,2));
  assert(SSXOutput::SourceReady(1556,896,1280,1056,2,12,10,2));

  // Match may derive its surface from that source, but a trial must wait for
  // the next presentation after the guarded resize, even if source is stable.
  const double internal_changed=10, output_resized=13;
  const double trial_changed=std::max(internal_changed,output_resized);
  assert(SSXOutput::SourceReady(1556,896,1280,1056,3,12,internal_changed,2));
  assert(!SSXOutput::SourceReady(1556,896,1280,1056,3,12,trial_changed,2));
  assert(!SSXOutput::SourceReady(1556,896,1280,1056,3,13,trial_changed,2));
  assert(SSXOutput::SourceReady(1556,896,1280,1056,3,14,trial_changed,2));

  // The internal edit can also be the latest change. Old 2x EFB samples must
  // not satisfy a switch back to 1x, including at fixed output dimensions.
  assert(!SSXOutput::SourceReady(1556,896,1280,1056,3,16,std::max(15.0,13.0),1));
  assert(SSXOutput::SourceReady(778,448,640,528,2,17,std::max(15.0,13.0),1));
  assert(!SSXOutput::SourceReady(0,448,640,528,3,17,15,1));
  assert(!SSXOutput::SourceReady(778,-1,640,528,3,17,15,1));
  assert(!SSXOutput::SourceReady(778,448,640,527,3,17,15,1));
  assert(!SSXOutput::SourceReady(778,448,640,528,3,17,15,3));
  assert(!SSXOutput::SourceReady(778,448,640,528,3,
      std::numeric_limits<double>::quiet_NaN(),15,1));
}
''')


if __name__ == '__main__':
    unittest.main()
