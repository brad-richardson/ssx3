"""Exercise ownership, missing frames and temporal interpolation in compiled C++."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PoseHistoryTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
    def test_history(self):
        code = r'''
#include "native/diagnostics/pose_history.h"
#include "native/diagnostics/trial_control.h"
#include <cassert>
#include <limits>
using namespace RenderResearch;
int main() {
 NativeTrial::Request();
 assert(NativeTrial::status.load()==NativeTrial::Status::Waiting);
 assert(!NativeTrial::Active(1));
 NativeTrial::ends=36; NativeTrial::status=NativeTrial::Status::Running;
 assert(NativeTrial::Active(35.9)); assert(!NativeTrial::Active(36));
 NativeTrial::Cancel(); assert(!NativeTrial::Active(2));
 // Cancellation cannot claim quiescence: the CPU adapter must drain first.
 assert(NativeTrial::status.load()==NativeTrial::Status::Running);
 // Requests are terminal-state-only: a live trial ignores Request, and a
 // terminal one resets the counters including the blended-extra count.
 NativeTrial::limited=true; NativeTrial::extras_blended=7; NativeTrial::Request();
 assert(NativeTrial::limited.load()); assert(NativeTrial::extras_blended.load()==7);
 NativeTrial::status=NativeTrial::Status::Finished; NativeTrial::Request();
 assert(!NativeTrial::limited.load()); assert(NativeTrial::extras_blended.load()==0);
 assert(NativeTrial::status.load()==NativeTrial::Status::Waiting);
 Matrix first{1,0,0,0, 0,1,0,0, 0,0,1,0}, next=first, out{};
 next[3]=10;
 Matrix inverse;
 assert(Inverse(next,inverse));
 auto identity=Multiply(next,inverse);
 for(unsigned i=0;i<12;++i) assert(std::abs(identity[i]-first[i])<1e-5f);
 assert(!Inverse(Matrix{},inverse));
 PoseKey rider{123,456,0,0}, tree{124,456,0,0};
 PoseHistory h;
 h.Begin(1); h.Add(rider,first); h.Seal();
 assert(!h.Sample(rider,first,0,out));
 h.Begin(2); h.Add(rider,next); h.Seal();
 assert(h.Sample(rider,next,0,out) && out[3]==0);
 assert(h.Sample(rider,next,.5f,out) && out[3]==5);
 assert(h.Sample(rider,next,1,out) && out[3]==10);
 assert(!h.Sample(tree,next,.5f,out)); // same palette slot, different owner
 assert(!h.Sample(rider,first,.5f,out)); // palette replaced after capture
 h.Begin(2); h.Add(rider,next); h.Seal(); // extra draw does not advance history
 assert(h.Sample(rider,next,.5f,out) && out[3]==5);
 assert(!h.Sample(rider,next,std::numeric_limits<float>::quiet_NaN(),out));
 h.Begin(3); h.Add(rider,next); h.Add(rider,first); h.Seal();
 assert(!h.Sample(rider,next,.5f,out)); // ambiguous identity, rejected before draw
 h.Begin(5); h.Add(rider,next); h.Seal();
 assert(!h.Sample(rider,next,.5f,out)); // missed generation, no stale motion
 h.Reset(); h.Begin(6); h.Add(rider,next); h.Seal();
 assert(!h.Sample(rider,next,.5f,out)); // lifecycle/reset discards history
 assert(!Continuous(first,Matrix{}));
 auto teleported=first; teleported[3]=10000;
 assert(!Continuous(first,teleported));
 auto rotated=first; rotated[0]=-1; rotated[10]=-1;
 assert(!Continuous(first,rotated));
 auto nan=first; nan[0]=std::numeric_limits<float>::infinity();
 assert(!Continuous(first,nan));
 h.Begin(7);
 for(unsigned i=0;i<=PoseHistory::Capacity;++i) h.Add({i,0,0,0},next);
 h.Seal(); assert(!h.Sample({0,0,0,0},next,.5f,out));
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'history.cpp'
            source.write_text(code)
            binary = Path(directory)/'history'
            subprocess.run(['c++', '-std=c++20', '-I', str(ROOT), str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
