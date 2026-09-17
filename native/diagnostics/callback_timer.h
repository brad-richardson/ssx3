// Always-on timing of the ordinary GXBE69 application update and render
// callbacks. The CPU thread reads clocks only at those four boundaries per
// frame, never per dispatch; the app's metric timer drains the rings once per
// second. Samples are skipped while any trial is pending or running so
// the numbers describe ordinary frames only. No guest state is read or written.
#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <vector>
#ifdef __APPLE__
#include <mach/mach_time.h>
#else
#include <time.h>
#endif
#include "callback_timing.h"
#include "trial_control.h"

namespace CallbackTimer {
inline constexpr std::uint32_t UpdateEntry=0x8010550cu, RenderEntry=0x8010a4c8u;
struct Sample { float cpu_ms=0, wall_ms=0; };
struct Ring {
  // Single writer (CPU thread). `count` is published after the slot is written
  // and the reader copies only slots below the count it acquired.
  std::array<Sample,1024> samples{};
  std::atomic<std::uint64_t> count{0};
  std::uint64_t consumed=0;  // reader only
  void Push(Sample s){
    const auto n=count.load(std::memory_order_relaxed);
    samples[n%samples.size()]=s;
    count.store(n+1,std::memory_order_release);
  }
};
struct Pending { bool active=false; std::uint32_t ret=0; double cpu=-1; std::uint64_t wall=0; };
inline Ring update_ring, render_ring;
inline Pending update, render;
inline std::uint64_t WallNow(){
#ifdef __APPLE__
  return mach_absolute_time();
#else
  timespec value{};
  clock_gettime(CLOCK_MONOTONIC,&value);
  return std::uint64_t(value.tv_sec)*1000000000ull+std::uint64_t(value.tv_nsec);
#endif
}
inline double WallMsPerTick(){
#ifdef __APPLE__
  static const double value=[]{ mach_timebase_info_data_t info; mach_timebase_info(&info);
    return double(info.numer)/double(info.denom)/1e6; }();
  return value;
#else
  return 1e-6;
#endif
}
template<class CPU> inline void Begin(Pending& p,const CPU& c){
  p.active=true; p.ret=c.lr; p.wall=WallNow(); p.cpu=RenderResearch::ThreadCPUSeconds();
}
template<class CPU> inline void End(Pending& p,Ring& ring,const CPU&){
  const auto wall=WallNow();
  const double cpu=RenderResearch::ThreadCPUSeconds();
  p.active=false;
  Sample s;
  s.wall_ms=float(double(wall-p.wall)*WallMsPerTick());
  s.cpu_ms=float(RenderResearch::CPUMilliseconds(p.cpu,cpu));
  ring.Push(s);
}
inline bool TrialQuiet(){
  const auto s=NativeTrial::status.load(std::memory_order_relaxed);
  return s!=NativeTrial::Status::Waiting && s!=NativeTrial::Status::Running;
}
template<class CPU> inline void SampleRider(const CPU& c);
template<class CPU> inline void Step(const CPU& c){
  const std::uint32_t pc=c.pc;
  if(pc==UpdateEntry){ SampleRider(c); if(TrialQuiet()) Begin(update,c); else update.active=false; return; }
  if(pc==RenderEntry){ if(TrialQuiet()) Begin(render,c); else render.active=false; return; }
  if(update.active && pc==update.ret) End(update,update_ring,c);
  else if(render.active && pc==render.ret) End(render,render_ring,c);
}
// Rider telemetry: once per second at the update callback, read the rider's
// position and state through the same pointer chain the Mac observer uses.
// Reads only; a seqlock publishes the sample to the app's metric timer.
struct RiderSample { bool valid=false; std::uint32_t rider=0, state=0; float x=0, y=0, z=0; std::uint64_t timebase=0; unsigned updates=0; };
inline RiderSample rider_sample;
inline std::atomic<unsigned> rider_seq{0};
inline unsigned rider_updates=0;
template<class CPU> inline bool RiderValid(const CPU& c, std::uint32_t a, std::size_t n) {
  return c.ram && a>=0x80000000u && std::uint64_t(a)+n<=0x80000000ull+c.ram_size;
}
template<class CPU> inline std::uint32_t RiderWord(const CPU& c, std::uint32_t a) {
  if(!RiderValid(c,a,4)) return 0;
  const unsigned char* p=c.ram+(a-0x80000000u);
  return (std::uint32_t(p[0])<<24)|(std::uint32_t(p[1])<<16)|(std::uint32_t(p[2])<<8)|p[3];
}
template<class CPU> inline float RiderFloat(const CPU& c, std::uint32_t a) {
  const std::uint32_t bits=RiderWord(c,a); float f; std::memcpy(&f,&bits,4); return f;
}
template<class CPU> inline void SampleRider(const CPU& c) {
  if(++rider_updates<60) return;
  RiderSample s; s.updates=rider_updates; rider_updates=0; s.timebase=c.timebase;
  std::uint32_t a=RiderWord(c,0x803da1f8u);
  for(std::uint32_t o: {0x74u,0xcu,0x28u}) { if(!RiderValid(c,a,4)) { a=0; break; } a=RiderWord(c,a+o); }
  if(a && RiderValid(c,a,0x800)) {
    s.valid=true; s.rider=a; s.x=RiderFloat(c,a+240); s.y=RiderFloat(c,a+244); s.z=RiderFloat(c,a+248);
    const std::uint32_t body=RiderWord(c,a+0x718);
    s.state=RiderValid(c,body,0xd34) ? RiderWord(c,body+0xd30) : 0;
  }
  rider_seq.fetch_add(1,std::memory_order_acq_rel);
  rider_sample=s;
  rider_seq.fetch_add(1,std::memory_order_acq_rel);
}
inline RiderSample ReadRider() {
  for(int attempt=0; attempt<8; ++attempt) {
    const unsigned before=rider_seq.load(std::memory_order_acquire);
    if(before&1u) continue;
    RiderSample s=rider_sample;
    std::atomic_thread_fence(std::memory_order_acquire);
    if(rider_seq.load(std::memory_order_acquire)==before) return s;
  }
  return RiderSample{};
}
// Reader side: summarize and consume samples published since the last drain.
struct Summary { unsigned count=0; double cpu_median_ms=-1, cpu_p95_ms=-1, wall_median_ms=-1, wall_p95_ms=-1; };
inline Summary Drain(Ring& ring){
  Summary result;
  const auto count=ring.count.load(std::memory_order_acquire);
  const auto available=std::min<std::uint64_t>(count-ring.consumed,ring.samples.size());
  std::vector<float> cpu, wall;
  for(std::uint64_t i=count-available;i<count;++i){
    const auto& s=ring.samples[i%ring.samples.size()];
    if(s.cpu_ms>=0) cpu.push_back(s.cpu_ms);
    wall.push_back(s.wall_ms);
  }
  ring.consumed=count;
  std::sort(cpu.begin(),cpu.end()); std::sort(wall.begin(),wall.end());
  const auto quantile=[](const std::vector<float>& v,double q){ return v.empty()?-1.0:double(v[std::min(v.size()-1,size_t(q*(v.size()-1)))]); };
  result.count=unsigned(available);
  result.cpu_median_ms=quantile(cpu,.5); result.cpu_p95_ms=quantile(cpu,.95);
  result.wall_median_ms=quantile(wall,.5); result.wall_p95_ms=quantile(wall,.95);
  return result;
}
}
