// The single per-dispatch entry compiled into the iOS build's local copy of
// StaticRecompCore_Run.cpp. Requires startup_skip.h, native_callback_trace.h,
// native_render_schedule.h and native_pose_interpolation.h first. Runs on the
// CPU thread only. Each hook keeps its own cheap gate; the callback timer adds
// two compares per dispatch and reads clocks only at callback boundaries.
#pragma once
#include "callback_timer.h"
static inline void SSXDispatchStep(CPUState& c){
  CallbackTimer::Step(c);
  StartupBoot::Step(c);
  NativeInterpolation::Step(c);
}
