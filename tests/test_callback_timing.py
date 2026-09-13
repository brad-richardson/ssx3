"""Verify the platform clock measures this thread rather than elapsed sleep."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CallbackTimingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'Requires a C++ compiler')
    def test_sleep_is_not_callback_cpu_work(self):
        code = r'''
#include "native/diagnostics/callback_timing.h"
#include <cassert>
#include <chrono>
#include <thread>
using namespace RenderResearch;
int main() {
  const auto wall = std::chrono::steady_clock::now();
  const double start = ThreadCPUSeconds();
  assert(start >= 0);
  std::this_thread::sleep_for(std::chrono::milliseconds(40));
  const double cpu = CPUMilliseconds(start, ThreadCPUSeconds());
  const double elapsed = std::chrono::duration<double, std::milli>(
      std::chrono::steady_clock::now()-wall).count();
  assert(cpu >= 0 && cpu < elapsed/2);
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'timing.cpp'
            binary = Path(directory)/'timing'
            source.write_text(code)
            subprocess.run(['c++', '-std=c++20', '-pthread', '-I', str(ROOT),
                            str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
