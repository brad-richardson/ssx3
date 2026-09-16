// Desktop integration test of the same bounded trial controls compiled on iOS.
// Runs an F trial first (cancelled mid-repeat), checks the quiescent return,
// then runs a smoothing trial through automatic expiration. The F-first order
// is the regression test for the schedule epoch: an F trial never takes
// completion mode, so without a per-trial epoch reset the smoothing trial
// inherits a stale budget and dies instantly past its grace. A third leg
// re-runs F and cancels it genuinely idle (nothing in flight), the phone
// path for a pre-ride or user cancel that lands between callbacks. Without
// an entry-site finish the trial restores its consts but never clears
// Running, and the watchdog below fires.
#pragma once
namespace NativeTrialTest {
static inline void Step(CPUState& c) {
 static bool initialized=false,requested=false,cancelled=false,cancelled_idle=false,finished=false;
 static unsigned leg=0;
 if(!initialized){SSXResetNativeTrial(std::getenv("SSX_NATIVE_PROBE"));initialized=true;}
 // A broken boundary hook must not also disable the watchdog. Refresh it
 // independently, without paying for a wall-clock read on every dispatch.
 static unsigned polls=0;
 if((++polls&4095u)==0)NativeProbe::now_cached=NativeProbe::Now();
 NativeProbe::RefreshNow(c);
 const double now=NativeProbe::now_cached;
 if(now>=130&&!requested){
  NativeTrial::RequestF();requested=true;
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"request\",\"wall\":%.6f}\n",now);
 }
 // Confined to this test build and the first cancellation check. The second
 // trial exercises the actual speed floor and performance fallback.
 NativeSchedule::test_force_extra=requested&&!cancelled;
 if(leg==0&&requested&&!cancelled&&NativeProbe::update.pending&&NativeProbe::update.repeated){
  NativeTrial::Cancel();cancelled=true;NativeSchedule::test_force_extra=false;
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"cancel_during_repeat\",\"wall\":%.6f}\n",now);
 }
 // Leg 2 cancels with no callback in flight and away from an update entry,
 // so no return dispatch is owed. Ten doubled updates prove the trial was
 // live before the cancel landed.
 if(leg==2&&!cancelled_idle&&NativeTrial::status.load()==NativeTrial::Status::Running&&
    NativeTrial::updates_doubled.load()>=10&&!NativeProbe::update.pending&&!NativeProbe::render.pending&&
    c.pc!=0x8010550c){
  NativeTrial::Cancel();cancelled_idle=true;
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"cancel_idle\",\"wall\":%.6f}\n",now);
 }
 const auto before=NativeTrial::status.load();
 NativeInterpolation::Step(c);
 if(before==NativeTrial::Status::Running&&NativeTrial::status.load()==NativeTrial::Status::Finished){
  if(NativeProbe::render.pending||NativeProbe::update.pending||NativeSchedule::mode_changed)std::abort();
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"quiescent\",\"wall\":%.6f}\n",now);
  if(leg==1){
   NativeTrial::RequestF();leg=2;
   std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"restart2\",\"wall\":%.6f}\n",now);
  }else if(leg==2){
   finished=true;
   std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"complete\",\"wall\":%.6f}\n",now);
  }
 }
 // Restart past trial 1's 10 s grace: without the per-trial epoch reset the
 // smoothing trial inherits trial 1's budget and limits instantly with zero
 // extras, which the runner below rejects.
 if(now>=142&&leg==0&&cancelled&&NativeTrial::status.load()==NativeTrial::Status::Finished){
  NativeTrial::Request();leg=1;
  std::fprintf(NativeProbe::Output(),"{\"event\":\"trial_test\",\"action\":\"restart\",\"wall\":%.6f}\n",now);
 }
 if(now>=185&&!finished){std::fprintf(stderr,"native trial did not finish all three lifecycle checks\n");std::abort();}
}
}
