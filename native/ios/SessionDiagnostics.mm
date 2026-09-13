#import "SessionDiagnostics.h"
#import <QuartzCore/QuartzCore.h>
#include <TargetConditionals.h>
#include <array>
#include <algorithm>
#include <cstdio>
#include <memory>
#include <mutex>
#include <utility>

namespace {
struct PresentEvent { const char* event; unsigned long long frame; double host, a, b; };
struct Session {
  std::mutex mutex;
  FILE* lifecycle = nullptr;
  FILE* present = nullptr;
  // About 17 seconds at 120 FPS. Callbacks only append scalars; the app drains
  // once per second, also while paused. Overflow is explicit, never hidden.
  std::array<PresentEvent, 8192> events;
  size_t count = 0;
  unsigned long long frame = 0, dropped = 0;

  explicit Session(NSString* report) {
    lifecycle = std::fopen([report stringByAppendingPathComponent:@"lifecycle.jsonl"].fileSystemRepresentation, "wx");
    present = std::fopen([report stringByAppendingPathComponent:@"present.csv"].fileSystemRepresentation, "wx");
    if (!lifecycle || !present) std::fprintf(stderr, "[ssx-diagnostics] could not open report files\n");
  }
  ~Session() {
    Flush();
    if (lifecycle) std::fclose(lifecycle);
    if (present) std::fclose(present);
  }
  void Push(const char* event, unsigned long long id, double a, double b) {
    const double host = CACurrentMediaTime();
    std::lock_guard lock(mutex);
    if (count == events.size()) { ++dropped; return; }
    events[count++] = {event, id, host, a, b};
  }
  unsigned long long NextFrame() {
    std::lock_guard lock(mutex);
    return ++frame;
  }
  void Flush() {
    // Normally drained by the app. A session's final callback may release its
    // last reference after reset; its destructor then flushes the bounded tail
    // to the original file. Routine Metal callbacks only append to memory.
    std::array<PresentEvent, 8192> batch;
    size_t size;
    unsigned long long lost;
    {
      std::lock_guard lock(mutex);
      size = count; count = 0;
      std::copy_n(events.begin(), size, batch.begin());
      lost = std::exchange(dropped, 0);
    }
    if (!present) return;
    for (size_t i = 0; i < size; ++i) {
      const auto& e = batch[i];
      std::fprintf(present, "%s,%llu,%.9f,%.9f,%.9f\n", e.event, e.frame, e.host, e.a, e.b);
    }
    if (lost) std::fprintf(present, "dropped,0,%.9f,%llu,0\n", CACurrentMediaTime(), lost);
    std::fflush(present);
  }
  void Event(NSString* event, NSDictionary* details) {
    NSMutableDictionary* row = [details mutableCopy];
    row[@"event"] = event;
    row[@"host_seconds"] = @(CACurrentMediaTime());
    row[@"unix_seconds"] = @(NSDate.date.timeIntervalSince1970);
    NSData* data = [NSJSONSerialization dataWithJSONObject:row options:0 error:nil];
    std::lock_guard lock(mutex);
    if (!lifecycle || !data) return;
    std::fwrite(data.bytes, 1, data.length, lifecycle);
    std::fputc('\n', lifecycle);
    std::fflush(lifecycle);
  }
};
std::mutex session_mutex;
std::shared_ptr<Session> session;
std::shared_ptr<Session> Current() { std::lock_guard lock(session_mutex); return session; }
}

void SSXDiagnosticsBegin(NSString* report) {
  auto next = std::make_shared<Session>(report);
  { std::lock_guard lock(session_mutex); session.swap(next); }
}
void SSXDiagnosticsFlush() { if (auto s = Current()) s->Flush(); }
void SSXDiagnosticsEnd() {
  std::shared_ptr<Session> previous;
  { std::lock_guard lock(session_mutex); previous.swap(session); }
  if (previous) previous->Flush();
}
void SSXSessionEvent(NSString* event, NSDictionary* details) {
  if (auto s = Current()) s->Event(event, details);
}
void SSXCheckpointStage(const char* stage, const char* path, std::uint64_t bytes, int error) {
  @autoreleasepool {
    SSXSessionEvent(@"checkpoint_stage", @{@"stage":@(stage), @"file":@(path).lastPathComponent,
      @"bytes":@(bytes), @"errno":@(error)});
  }
}
void SSXRecompSample(std::uint64_t ticks, std::uint64_t native, std::uint64_t fallback,
                    std::uint64_t jit, std::uint64_t exceptions, std::uint64_t hle_returns,
                    std::uint64_t hle_vectors, std::uint64_t hle_rejects) {
  @autoreleasepool {
    SSXSessionEvent(@"recomp_sample", @{@"ticks":@(ticks), @"native_dispatches":@(native),
      @"fallback_steps":@(fallback), @"fallback_jit_runs":@(jit), @"native_exceptions":@(exceptions),
      @"hle_returns":@(hle_returns), @"hle_vectors":@(hle_vectors), @"hle_rejects":@(hle_rejects)});
  }
}
void SSXDrawableAcquired(double start, bool acquired) {
  if (auto s = Current()) s->Push("acquire", 0, CACurrentMediaTime()-start, acquired);
}
void SSXDrawableSubmitted(id<CAMetalDrawable> drawable, id<MTLCommandBuffer> buffer) {
  auto s = Current();
  if (!s) return;
  const auto frame = s->NextFrame();
  s->Push("submit", frame, drawable.texture.width, drawable.texture.height);
  // The handlers retain this session, so delayed callbacks from an old runtime
  // cannot contaminate a new report. Zero presentedTime is recorded as unknown.
#if !TARGET_OS_SIMULATOR
  [drawable addPresentedHandler:^(id<MTLDrawable> value) {
    s->Push("display", frame, value.presentedTime, 0);
  }];
#else
  // Apple's simulator SDK omits presentation callbacks. Keep submission/GPU
  // evidence while explicitly recording that scanout timing is unavailable.
  s->Push("display_unavailable", frame, 0, 0);
#endif
  [buffer addCompletedHandler:^(id<MTLCommandBuffer> value) {
    s->Push("gpu", frame, value.GPUStartTime, value.GPUEndTime);
    if (value.status == MTLCommandBufferStatusError)
      s->Push("gpu_error", frame, value.status, value.error.code);
  }];
}
