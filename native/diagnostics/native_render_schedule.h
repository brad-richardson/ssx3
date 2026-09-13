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
static bool ScheduleEnabled(){static bool on=std::getenv("SSX_NATIVE_SCHEDULE")!=nullptr;return on;}
static bool CompletionEnabled(){static bool on=std::getenv("SSX_NATIVE_COMPLETION_RELEASE")!=nullptr;return on;}
static RenderResearch::Deadline deadline;
static u64 last_draw=0;
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
 std::fprintf(Output(),"{\"event\":\"schedule\",\"action\":\"%s\",\"wall\":%.6f,\"ticks\":%llu,\"host_seconds\":%.9f,\"missed\":%llu,\"pending\":%u}\n",event,Now(),(unsigned long long)ticks,PresentationClock(),(unsigned long long)missed,Word(c,c.gpr[13]-20556));
 std::fflush(Output());
}
static inline void Step(CPUState& c){
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
 if(completed&&enabled){
  last_draw=timing.GetTicks();
  if(schedule_started)ScheduleEvent(c,extra?"extra_complete":"regular_complete",last_draw);
 }
 NativeProbe::Step(c);
 if(!enabled)return;
 if(mode_changed&&(finished||c.pc==0x801cad24)&&Now()>=175){
  c.ram[mode_address-0x80000000u]=saved_mode;mode_changed=false;
  ScheduleEvent(c,"restore_mode",timing.GetTicks());
 }
 if(c.pc!=0x801cad24||c.lr!=0x801cd724||render.pending||update.pending)return;
 const double wall=Now();if(wall<140||wall>=175)return;
 const u32 manager=Word(c,0x803da9d8);
 // Recover the active application through the manager and validate its type.
 const u32 app=Word(c,manager+4);
 if(!Valid(c,manager,64)||!Valid(c,app,0x400)||Word(c,app)!=0x802e543c)return;
 const auto state=Capture(c,app);
 if(!Valid(c,state.rider,0x800)||state.state!=0)return;
 const u64 ticks=timing.GetTicks();
 const u64 period=system.GetSystemTimers().GetTicksPerSecond()/120;
 if(!schedule_started){
  schedule_started=true;deadline={ticks+period,period,0};last_draw=ticks;
  ScheduleEvent(c,"start",ticks);
  if(CompletionEnabled()){
   const u32 graphics=Word(c,c.gpr[13]-22644);
   const u32 bytes=Word(c,graphics+7552);
   first_xfb=Word(c,c.gpr[13]-20600);
   if(!Config::Get(Config::GFX_HACK_IMMEDIATE_XFB)||
      Config::Get(Config::GFX_HACK_CAP_IMMEDIATE_XFB)||
      !bytes||bytes>2*1024*1024||!Valid(c,first_xfb,bytes)||
      first_xfb!=Word(c,graphics+7556)||Word(c,c.gpr[13]-20596)){
    ScheduleEvent(c,"invalid_immediate_copy_setup",ticks);std::abort();
   }
   StoreWord(c,c.gpr[13]-20596,first_xfb);
   ScheduleEvent(c,"shared_xfb_alias",ticks);
   mode_address=c.gpr[13]-20602;
   auto* mode=c.ram+mode_address-0x80000000u;saved_mode=*mode;*mode=1;mode_changed=true;
   ScheduleEvent(c,"completion_mode",ticks);
  }
 }
 const auto decision=deadline.Poll(ticks,last_draw,Word(c,c.gpr[13]-20556));
 const u64 missed=deadline.missed;
 if(decision==RenderResearch::Decision::InvalidQueue){ScheduleEvent(c,"invalid_queue",ticks);std::abort();}
 if(decision==RenderResearch::Decision::Covered)ScheduleEvent(c,"covered",ticks,missed);
 if(decision==RenderResearch::Decision::Full)ScheduleEvent(c,"queue_full",ticks,missed);
 if(decision==RenderResearch::Decision::Render){
   ScheduleEvent(c,"request",ticks,missed);
   const u32 original_r3=c.gpr[3];
   c.gpr[3]=app;c.pc=0x8010a4c8;
   NativeProbe::Step(c);render.repeated=true;render.first_result=original_r3;++repeats;
   return;
 }
 // Cooperatively yield a CPU slice instead of sleeping the guest main thread
 // until VI wakes it. Interrupt delivery and CoreTiming events stay enabled.
 c.pc=c.lr;timing.Idle();
}
}
