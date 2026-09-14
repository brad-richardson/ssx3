"""Check source-sized presentation geometry independently of UIKit."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
class OutputSizingTests(unittest.TestCase):
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
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'sizing.cpp'
            path.write_text(source)
            binary=Path(directory)/'sizing'
            subprocess.run(['c++','-std=c++17','-I',str(ROOT),str(path),'-o',str(binary)],
                           check=True,capture_output=True,text=True)
            subprocess.run([str(binary)],check=True,capture_output=True,text=True)


if __name__ == '__main__':
    unittest.main()
