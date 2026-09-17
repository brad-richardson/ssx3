// Headless Android trial driver: env-scheduled bounded smoothing/F/combined
// trial for the Odin PIE, which has no trial UI. Ports the desktop
// trial_test_driver.h lifecycle (request, cancel, quiescent finish) without
// forced extras: the trial exercises the real speed floor and performance
// fallback, so extras starvation stays observable. Requires
// SSX_NATIVE_TRIAL_APP with native_callback_trace.h, native_render_schedule.h
// and native_pose_interpolation.h first; runs on the CPU thread only.
// SSX_NATIVE_PROBE names the JSONL receipt (also the trial log path).
// SSX_ANDROID_TRIAL_AT schedules the request in wall seconds from emulation
// start; unset means no trial (control run). SSX_ANDROID_TRIAL_KIND selects
// smoothing (default), f or combined. SSX_ANDROID_TRIAL_SECS cancels the
// trial that many seconds after it reaches Running (0 runs to natural end);
// the cancel path still drains quiescently and restores guest state, so a
// short trial demonstrates the full lifecycle inside the ~15 s pre-panic
// race window of a movie run.
#pragma once
namespace NativeTrialAndroid {
static void Emit(const char* action,double now){
 FILE* out=NativeProbe::Output();
 if(!out)return;
 std::fprintf(out,"{\"event\":\"android_trial\",\"action\":\"%s\",\"wall\":%.6f,\"kind\":%d,\"status\":%d,\"frames\":%u,\"extras\":%u,\"doubled\":%u,\"blended\":%u,\"limited\":%d}\n",
  action,now,static_cast<int>(NativeTrial::kind.load()),static_cast<int>(NativeTrial::status.load()),
  NativeTrial::frames.load(),NativeTrial::extras.load(),NativeTrial::updates_doubled.load(),
  NativeTrial::extras_blended.load(),NativeTrial::limited.load()?1:0);
 std::fflush(out);
}
static void EmitConfigured(double at,int kind,double secs){
 FILE* out=NativeProbe::Output();
 if(!out)return;
 std::fprintf(out,"{\"event\":\"android_trial\",\"action\":\"configured\",\"wall\":0,\"at\":%.6f,\"kind\":%d,\"secs\":%.6f,\"immediate_xfb\":%d,\"cap_immediate_xfb\":%d}\n",
  at,kind,secs,Config::Get(Config::GFX_HACK_IMMEDIATE_XFB)?1:0,
  Config::Get(Config::GFX_HACK_CAP_IMMEDIATE_XFB)?1:0);
 std::fflush(out);
}
static void EmitStatus(NativeTrial::Status from,NativeTrial::Status to,double now){
 FILE* out=NativeProbe::Output();
 if(!out)return;
 std::fprintf(out,"{\"event\":\"android_trial\",\"action\":\"status\",\"wall\":%.6f,\"from\":%d,\"to\":%d,\"frames\":%u,\"extras\":%u,\"doubled\":%u,\"blended\":%u,\"limited\":%d}\n",
  now,static_cast<int>(from),static_cast<int>(to),
  NativeTrial::frames.load(),NativeTrial::extras.load(),NativeTrial::updates_doubled.load(),
  NativeTrial::extras_blended.load(),NativeTrial::limited.load()?1:0);
 std::fflush(out);
}
static inline void Step(CPUState& c){
 static bool initialized=false,requested=false,cancelled=false,finished=false,warned=false;
 static double at=-1,secs=0,running_since=-1;
 static NativeTrial::Kind kind=NativeTrial::Kind::Smoothing;
 static NativeTrial::Status last=NativeTrial::Status::Idle;
 if(!initialized){
  SSXResetNativeTrial(std::getenv("SSX_NATIVE_PROBE"));
  if(const char* p=std::getenv("SSX_ANDROID_TRIAL_AT")){
   char* end=nullptr;const double value=std::strtod(p,&end);
   if(end!=p&&value>=0)at=value;
  }
  if(const char* p=std::getenv("SSX_ANDROID_TRIAL_KIND")){
   if(!std::strcmp(p,"f"))kind=NativeTrial::Kind::F;
   else if(!std::strcmp(p,"combined"))kind=NativeTrial::Kind::Combined;
  }
  if(const char* p=std::getenv("SSX_ANDROID_TRIAL_SECS")){
   char* end=nullptr;const double value=std::strtod(p,&end);
   if(end!=p&&value>0)secs=value;
  }
  initialized=true;
  EmitConfigured(at,static_cast<int>(kind),secs);
  if(at>=0&&!NativeProbe::Output())
   std::fprintf(stderr,"[android-trial] SSX_NATIVE_PROBE unset: trial machinery inert\n");
 }
 // A broken boundary hook must not also disable the watchdog. Refresh it
 // independently, without paying for a wall-clock read on every dispatch.
 static unsigned polls=0;
 if((++polls&4095u)==0)NativeProbe::now_cached=NativeProbe::Now();
 NativeProbe::RefreshNow(c);
 const double now=NativeProbe::now_cached;
 if(at>=0&&!requested&&now>=at){
  requested=true;
  if(kind==NativeTrial::Kind::F)NativeTrial::RequestF();
  else if(kind==NativeTrial::Kind::Combined)NativeTrial::RequestCombined();
  else NativeTrial::Request();
  Emit("request",now);
 }
 const auto before=NativeTrial::status.load();
 if(before==NativeTrial::Status::Running&&running_since<0)running_since=now;
 if(before==NativeTrial::Status::Running&&!cancelled&&secs>0&&running_since>=0&&now-running_since>=secs){
  NativeTrial::Cancel();cancelled=true;Emit("cancel",now);
 }
 NativeInterpolation::Step(c);
 const auto after=NativeTrial::status.load();
 if(after!=last){EmitStatus(last,after,now);last=after;}
 if(after==NativeTrial::Status::Finished&&!finished){finished=true;Emit("complete",now);}
 // Log-only: the outer timeout bounds the run, and a stuck trial's partial
 // receipts matter more than a loud death on device.
 if(at>=0&&!finished&&!warned&&now>at+120){warned=true;Emit("watchdog",now);}
}
}
