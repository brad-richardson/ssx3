// Authored, platform-independent scheduling policy for isolated research.
#pragma once
#include <cstdint>
#include <cmath>

namespace RenderResearch {
// Host-debt guard for extra draws. The throttle keeps guest time near wall
// time overall, but at the scheduling seam the guest is normally behind: its
// virtual clock advances with executed cycles while the host spent real time
// running them, and the idle skip to the next retrace has not happened yet. A
// fixed 2 ms tolerance therefore vetoed every opportunity on the Mac and the
// phone. Compare against the least debt seen over the recent window instead:
// a steady offset is allowed, while debt that keeps growing (the host falling
// behind, including because of extra draws) blocks further extra work.
struct RealTimeBudget {
  double wall_start=0;
  uint64_t ticks_start=0;
  static constexpr unsigned Buckets=5;
  static constexpr double BucketSeconds=0.1; // 0.5 s reference window
  static constexpr double Slack=0.008;       // one 120 Hz period
  double minimum[Buckets]={};
  long bucket_index[Buckets]={-1,-1,-1,-1,-1};
  bool Allows(double wall,uint64_t ticks,uint64_t frequency) {
    if(!frequency||ticks<ticks_start||wall<wall_start)return false;
    const double debt=(wall-wall_start)-double(ticks-ticks_start)/frequency;
    const long index=long((wall-wall_start)/BucketSeconds);
    const unsigned slot=unsigned(index%Buckets);
    if(bucket_index[slot]!=index||debt<minimum[slot]){
      minimum[slot]=debt;bucket_index[slot]=index;
    }
    double reference=debt;
    for(unsigned i=0;i<Buckets;++i)
      if(bucket_index[i]>=0&&bucket_index[i]>index-long(Buckets)&&minimum[i]<reference)reference=minimum[i];
    return debt<=reference+Slack;
  }
};
// Observe elapsed time, not a fixed count of idle-seam visits: one frame can
// visit the seam hundreds of times while CoreTiming skips short slices.
// Sampling is bounded to 50 Hz, with at least half a second of history and
// hysteresis before resuming extras. This is a reactive guard, not a guarantee
// that the next draw will fit its deadline.
struct SpeedFloor {
  static constexpr unsigned Samples=32;
  static constexpr double Interval=0.02, Window=0.5;
  static constexpr double Stop=0.98, Resume=0.995;
  double wall[Samples]={};
  double guest[Samples]={};
  unsigned count=0,next=0;
  double last_wall=0, rate=0, span=0;
  uint64_t last_ticks=0, last_frequency=0;
  bool allowed=false;
  void Observe(double wall_now,uint64_t ticks,uint64_t frequency){
    if(!frequency||!std::isfinite(wall_now)){*this={};return;}
    if(count&&(wall_now<last_wall||ticks<last_ticks||frequency!=last_frequency||wall_now-last_wall>1.0))
      *this={};
    last_wall=wall_now;last_ticks=ticks;last_frequency=frequency;
    if(count&&wall_now-wall[(next+Samples-1)%Samples]<Interval)return;
    wall[next]=wall_now;guest[next]=double(ticks)/frequency;
    next=(next+1)%Samples;if(count<Samples)++count;
    const unsigned newest=(next+Samples-1)%Samples;
    span=rate=0;
    for(unsigned age=1;age<count;++age){
      const unsigned old=(newest+Samples-age)%Samples;
      const double elapsed=wall[newest]-wall[old];
      if(elapsed+1e-9<Window)continue;
      span=elapsed;rate=(guest[newest]-guest[old])/elapsed;
      allowed=rate>=(allowed?Stop:Resume);return;
    }
    allowed=false;
  }
  bool Allows() const {return allowed;}
};
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
