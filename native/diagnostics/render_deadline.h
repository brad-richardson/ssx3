// Authored, platform-independent scheduling policy for isolated research.
#pragma once
#include <cstdint>

namespace RenderResearch {
enum class Decision { Early, Covered, Full, Render, InvalidQueue };
struct Deadline {
  uint64_t next = 0;
  uint64_t period = 0;
  uint64_t missed = 0;
  Decision Poll(uint64_t now, uint64_t last_draw, unsigned pending) {
    missed = 0;
    if (!period || pending > 2) return Decision::InvalidQueue;
    if (now < next) return Decision::Early;
    // Keep the original phase. Late requests are dropped, never queued in a burst.
    missed = (now - next) / period;
    next += (missed + 1) * period;
    if (now >= last_draw && now - last_draw < period * 3 / 4)
      return Decision::Covered;
    if (pending == 2) return Decision::Full;
    return Decision::Render;
  }
};
}
