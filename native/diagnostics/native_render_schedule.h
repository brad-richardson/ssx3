// Authored GXBE69 adapter for an isolated native deadline experiment.
// Requires native_callback_trace.h first. Addresses are pinned by the builder.
// Game input, VI and queue completion remain active. Only the main idle wait
// is replaced by cooperative CPU-slice yields during the bounded experiment.
// The optional existing submission mode changes XFB selection as well as
// completion timing; it is not safe to generalize without ownership validation.
// Completion mode reuses the original single XFB for both queue indices.
// Requires the host immediate-XFB-copy path, whose texture versions own frames.
// This is not a double-buffered physical-console implementation. No guest
// allocation or queue counters are changed. The alias survives mode restoration
// until process exit so queued entries cannot select a null destination.
#pragma once
#include "render_deadline.h"
#include <mach/mach_time.h>
#include "Core/Config/GraphicsSettings.h"
namespace NativeSchedule {
using namespace NativeProbe;
static bool ScheduleEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 return true;
#else
 static bool on=std::getenv("SSX_NATIVE_SCHEDULE")!=nullptr;return on;
#endif
}
static bool CompletionEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 return true;
#else
 static bool on=std::getenv("SSX_NATIVE_COMPLETION_RELEASE")!=nullptr;return on;
#endif
}
static RenderResearch::Deadline deadline;
static RenderResearch::RealTimeBudget budget;
static RenderResearch::SpeedFloor speed_floor;
#ifdef SSX_NATIVE_TRIAL_TEST
// Desktop lifecycle test only: reach one injected draw even on a slow host.
static bool test_force_extra=false;
#endif
static bool SpeedFloorEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 return true;
#else
 static bool on=std::getenv("SSX_NATIVE_SPEED_FLOOR")!=nullptr;return on;
#endif
}
static bool BudgetEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 // SpeedFloor supplies the phone load guard using measured elapsed time.
 return false;
#else
 static bool on=std::getenv("SSX_NATIVE_REALTIME_GUARD")!=nullptr;return on;
#endif
}
static u64 last_draw=0;
static bool StartSpacingEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 return true;
#else
 static bool on=std::getenv("SSX_NATIVE_START_SPACING")!=nullptr;return on;
#endif
}
static bool ActiveRiderState(u32 state){return StartSpacingEnabled()?(state<6||state==7):state==0;}
static bool schedule_started=false,mode_changed=false;
static unsigned char saved_mode=0;
static u32 mode_address=0,first_xfb=0;
// libc++ steady_clock includes time spent asleep on this Mac; Metal uses the
// absolute uptime clock. Use Metal's clock domain for presentation alignment.
static double PresentationClock(){
 static mach_timebase_info_data_t info=[](){mach_timebase_info_data_t value;mach_timebase_info(&value);return value;}();
 return double(mach_absolute_time())*info.numer/info.denom/1e9;
}
static void StoreWord(CPUState& c,u32 address,u32 value){
 if(!Valid(c,address,4))std::abort();
 auto* p=c.ram+address-0x80000000u;
 for(unsigned i=0;i<4;++i)p[i]=value>>(24-i*8);
}
static void ScheduleEvent(CPUState& c,const char* event,u64 ticks,u64 missed=0){
 std::fprintf(Output(),"{\"event\":\"schedule\",\"action\":\"%s\",\"wall\":%.6f,\"ticks\":%llu,\"host_seconds\":%.9f,\"missed\":%llu,\"pending\":%u,\"speed_window\":%.6f,\"speed_ratio\":%.6f}\n",event,Now(),(unsigned long long)ticks,PresentationClock(),(unsigned long long)missed,Word(c,c.gpr[13]-20556),speed_floor.span,speed_floor.rate);
 std::fflush(Output());
}
static inline void Step(CPUState& c){
 RefreshNow(c);
 if(!Output())return;
 auto& system=Core::System::GetInstance();
 auto& timing=system.GetCoreTiming();
 const bool enabled=ScheduleEnabled();
 static bool checked=false;
 if(enabled&&!checked){
  checked=true;
  if(DoubleEnabled()||WaitEnabled()||SweepEnabled()||!SkipEnabled()){
   std::fprintf(stderr,"[native-schedule] requires skipped duplicate helpers and no repeat/wait/sweep mode\n");std::abort();
  }
 }
 if(mode_changed&&c.pc==0x802a0144&&c.lr==0x801cbad0&&c.gpr[3]!=first_xfb){
  std::fprintf(stderr,"[native-schedule] unexpected XFB copy destination\n");std::abort();
 }
 const bool finished=render.pending&&c.pc==render.ret;
 const bool completed=finished&&(c.gpr[3]&255)&&view_matrix_calls&&frame_end_calls;
 const bool extra=render.repeated;
 if(enabled&&StartSpacingEnabled()&&c.pc==0x8010a4c8)last_draw=timing.GetTicks();
 if(completed&&enabled){
  if(!StartSpacingEnabled())last_draw=timing.GetTicks();
  if(schedule_started)ScheduleEvent(c,extra?"extra_complete":"regular_complete",timing.GetTicks());
 }
 NativeProbe::Step(c);
 if(!enabled)return;
 if(mode_changed&&(finished||c.pc==0x801cad24)&&!ExperimentalWindow()){
  c.ram[mode_address-0x80000000u]=saved_mode;mode_changed=false;
  ScheduleEvent(c,"restore_mode",timing.GetTicks());
  schedule_started=false;
 }
#ifdef SSX_NATIVE_TRIAL_APP
 // Completion is a quiescence property, independent of the call-site gate
 // used to inject work. Cancellation can restore the mode at a callback
 // return before the next eligible application idle call.
 if((finished||c.pc==0x801cad24)&&!mode_changed&&!render.pending&&!update.pending&&
    NativeTrial::status.load()==NativeTrial::Status::Running&&!ExperimentalWindow())
  NativeTrial::status=NativeTrial::Status::Finished;
#endif
 if(c.pc!=0x801cad24||c.lr!=0x801cd724||render.pending||update.pending)return;
#ifdef SSX_NATIVE_TRIAL_APP
 // A saved session can contain our persistent single-XFB alias. Normalize its
 // completion mode after restore, before accepting a new trial. Per-entry mode
 // flags still release any already queued frames through their original path.
 if(!mode_changed&&NativeTrial::status.load()!=NativeTrial::Status::Running&&c.gpr[13]==0x803dfa60){
  const u32 graphics=Word(c,c.gpr[13]-22644),xfb=Word(c,c.gpr[13]-20600);
  const u32 mode=c.gpr[13]-20602;
  if(Valid(c,graphics,7572)&&Valid(c,xfb,Word(c,graphics+7552))&&xfb&&
     Word(c,graphics+7556)==xfb&&!Word(c,graphics+7560)&&Word(c,c.gpr[13]-20596)==xfb&&
     Valid(c,mode,1)&&c.ram[mode-0x80000000u]==1)
   c.ram[mode-0x80000000u]=0;
 }
 if(NativeTrial::cancel.load()&&NativeTrial::status.load()==NativeTrial::Status::Waiting)
  NativeTrial::status=NativeTrial::Status::Finished;
 if(!ExperimentalWindow()&&NativeTrial::status.load()!=NativeTrial::Status::Waiting)return;
#else
 if(!ExperimentalWindow())return;
#endif
 const u32 manager=Word(c,0x803da9d8);
 // Recover the active application through the manager and validate its type.
 const u32 app=Word(c,manager+4);
 if(!Valid(c,manager,64)||!Valid(c,app,0x400)||Word(c,app)!=0x802e543c)return;
 const auto state=Capture(c,app);
 if(!Valid(c,state.rider,0x800)||!ActiveRiderState(state.state))return;
#ifdef SSX_NATIVE_TRIAL_APP
 if(NativeTrial::status.load()==NativeTrial::Status::Waiting){
  NativeTrial::ends=Now()+35;NativeTrial::status=NativeTrial::Status::Running;
 }
#endif
 const u64 ticks=timing.GetTicks();
 const u64 period=system.GetSystemTimers().GetTicksPerSecond()/120;
 if(!schedule_started){
  schedule_started=true;deadline={ticks+period,period,0};last_draw=ticks;
  budget={Now(),ticks};speed_floor={};
  ScheduleEvent(c,"start",ticks);
  if(CompletionEnabled()){
   const u32 graphics=Word(c,c.gpr[13]-22644);
   const u32 bytes=Word(c,graphics+7552);
   first_xfb=Word(c,c.gpr[13]-20600);
   if(!Config::Get(Config::GFX_HACK_IMMEDIATE_XFB)||
      Config::Get(Config::GFX_HACK_CAP_IMMEDIATE_XFB)||
      !bytes||bytes>2*1024*1024||!Valid(c,first_xfb,bytes)||
      first_xfb!=Word(c,graphics+7556)||
      (Word(c,c.gpr[13]-20596)&&Word(c,c.gpr[13]-20596)!=first_xfb)){
    ScheduleEvent(c,"invalid_immediate_copy_setup",ticks);
#ifdef SSX_NATIVE_TRIAL_APP
    NativeTrial::status=NativeTrial::Status::Unavailable;schedule_started=false;return;
#else
    std::abort();
#endif
   }
   StoreWord(c,c.gpr[13]-20596,first_xfb);
   ScheduleEvent(c,"shared_xfb_alias",ticks);
   mode_address=c.gpr[13]-20602;
   auto* mode=c.ram+mode_address-0x80000000u;saved_mode=*mode;*mode=1;mode_changed=true;
   ScheduleEvent(c,"completion_mode",ticks);
  }
 }
 if(SpeedFloorEnabled())speed_floor.Observe(now_cached,ticks,system.GetSystemTimers().GetTicksPerSecond());
#ifdef SSX_NATIVE_TRIAL_APP
 // Ordinary interpolated draws also cost time. Stop the entire trial when
 // it cannot produce useful extras, or sustained simulation speed suffers.
 if(now_cached-budget.wall_start>=3&&
    (NativeTrial::extras.load()<15||(speed_floor.span>=RenderResearch::SpeedFloor::Window&&speed_floor.rate<0.95))){
  NativeTrial::limited=true;NativeTrial::Cancel();
  ScheduleEvent(c,"performance_limit",ticks);return;
 }
#endif
 const auto decision=deadline.Poll(ticks,last_draw,Word(c,c.gpr[13]-20556));
 const u64 missed=deadline.missed;
 if(decision==RenderResearch::Decision::InvalidQueue){ScheduleEvent(c,"invalid_queue",ticks);std::abort();}
 if(decision==RenderResearch::Decision::Covered)ScheduleEvent(c,"covered",ticks,missed);
 if(decision==RenderResearch::Decision::Full)ScheduleEvent(c,"queue_full",ticks,missed);
 if(decision==RenderResearch::Decision::Render){
   if(BudgetEnabled()&&!budget.Allows(Now(),ticks,system.GetSystemTimers().GetTicksPerSecond())){
    ScheduleEvent(c,"host_budget",ticks,missed);c.pc=c.lr;timing.Idle();return;
   }
   bool floor_allows=speed_floor.Allows();
#ifdef SSX_NATIVE_TRIAL_TEST
   floor_allows|=test_force_extra;
#endif
   if(SpeedFloorEnabled()&&!floor_allows){
    ScheduleEvent(c,"speed_floor",ticks,missed);c.pc=c.lr;timing.Idle();return;
   }
   ScheduleEvent(c,"request",ticks,missed);
   const u32 original_r3=c.gpr[3];
   c.gpr[3]=app;c.pc=0x8010a4c8;
   NativeProbe::Step(c);render.repeated=true;render.first_result=original_r3;++repeats;
   if(StartSpacingEnabled())last_draw=ticks;
   return;
 }
 // Cooperatively yield a CPU slice instead of sleeping the guest main thread
 // until VI wakes it. Interrupt delivery and CoreTiming events stay enabled.
 c.pc=c.lr;timing.Idle();
}
}
