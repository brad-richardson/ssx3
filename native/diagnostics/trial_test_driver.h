// Desktop integration test of the same bounded trial controls compiled on iOS.
// Starts after course navigation, cancels during a render, checks the quiescent
// return, then runs another trial through automatic expiration.
#pragma once
namespace NativeTrialTest {
static inline void Step(CPUState& c) {
 static bool initialized=false,requested=false,cancelled=false,restarted=false,finished=false;
 if(!initialized){SSXResetNativeTrial(std::getenv("SSX_NATIVE_PROBE"));initialized=true;}
 const double now=NativeProbe::Now();
 if(now>=140&&!requested){NativeTrial::Request();requested=true;}
 // Ensure one injected draw is reached even on an overloaded test host. This
 // override is confined to the first cancellation test; the second trial uses
 // the production time budget and automatic fallback without intervention.
 if(requested&&!cancelled&&NativeSchedule::schedule_started)
  NativeSchedule::budget.wall_start=now;
 if(requested&&!cancelled&&NativeProbe::render.pending&&NativeProbe::render.repeated){
  NativeTrial::Cancel();cancelled=true;
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"cancel_during_extra\",\"wall\":%.6f}\n",now);
 }
 const auto before=NativeTrial::status.load();
 NativeInterpolation::Step(c);
 if(before==NativeTrial::Status::Running&&NativeTrial::status.load()==NativeTrial::Status::Finished){
  if(NativeProbe::render.pending||NativeProbe::update.pending||NativeSchedule::mode_changed)std::abort();
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"quiescent\",\"wall\":%.6f}\n",now);
  if(restarted)finished=true;
 }
 if(now>=147&&cancelled&&!restarted&&NativeTrial::status.load()==NativeTrial::Status::Finished){
  NativeTrial::Request();restarted=true;
 }
 if(now>=185&&!finished){std::fprintf(stderr,"native trial did not finish both lifecycle checks\n");std::abort();}
}
}
