// Callback-thread CPU time, distinct from elapsed time and work on GPU/other threads.
#pragma once
#include <cmath>
#include <time.h>

namespace RenderResearch {
inline double ThreadCPUSeconds() {
#ifdef CLOCK_THREAD_CPUTIME_ID
  timespec value{};
  if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &value) == 0)
    return double(value.tv_sec) + double(value.tv_nsec) / 1e9;
#endif
  return -1;  // Unavailable is never reported as zero work.
}
inline double CPUMilliseconds(double start, double end) {
  return std::isfinite(start) && std::isfinite(end) && start >= 0 && end >= start ?
      (end-start)*1000 : -1;
}
}
