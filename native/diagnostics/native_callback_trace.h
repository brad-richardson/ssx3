// Authored diagnostic hooks for the pinned GXBE69 executable. Not game source.
// Isolated research players only: repeat calls are an intentionally incomplete
// experiment, not a production 120 Hz implementation. No guest instructions
// are patched. Graphics readiness, guest clocks and interrupts remain active.
// Snapshot ranges are bounded RAM windows, not complete object ownership maps.
// WAIT_REPEAT polls through the original renderer; it is intentionally slow.
// SKIP_BOOKKEEPING omits two helpers only on verified extra draws.
// CAMERA_OFFSET adds 500 to one copied matrix component, not a complete camera.
// FROZEN_VIEW_SWEEP holds one application state for 40 normal, 40 offset and
// 40 restored draws. Screenshot names mark requests, not exact display IDs.
// DOUBLE_UPDATE re-enters the application update once per ordinary update in
// the window when rider state is stable across the callback. Same dt, same
// render rate: a 2x-update workload probe for the phase-1 budget question,
// not a timestep change or a 120 Hz mode.
// HALF_CADENCE skips every other application update in the window (entry
// jumps straight to return, same dt, same render rate). Wrong-control probe:
// fingerprints cadence-dependent advancement. Combined with DOUBLE_UPDATE it
// is the time-normalized 30 Hz mode: skipped alternates plus doubled
// survivors, 60 executions per guest second in back-to-back pairs.
// HALF_DT one-shot rewrites dt constants in guest RAM on window entry:
// eleven 1/60 floats to 1/120 plus the render divisor 60.0 to 120.0
// (pinned-DOL census, SDA-resolved). Verified before writing; aborts on
// drift. With DOUBLE_UPDATE this is the 120 Hz candidate v0: const-driven
// systems normalize while fixed-step integration still double-advances,
// which cleanly separates the two consumer classes. v1 adds sqrt
// renormalization of the 0x8002784C damping factors (0.98/0.956/0.978333).
// v2 gates the speed update (0x8002DE04) to first-body-only: its additive
// accel carries no dt const, so re-entered bodies must not re-apply it.
// GUEST_WINDOW replaces the host-clock window with guest-timed edges: the
// window arms on the first stable update that moves the rider (menus and
// loading never repeat, so movie inputs cannot desync), engages (consts
// patch) SSX_NATIVE_WINDOW_SKIP ordinary ticks later, repeats start the
// NEXT tick (no 1.5x transitional tick), and after
// SSX_NATIVE_WINDOW_TICKS doubled ticks the window closes and the consts
// restore under the same drift check (no half-speed tail). All edges are
// guest-deterministic: identical-prefix runs arm, engage and close on
// identical ticks. The default tick limit is effectively infinite;
// SSX_NATIVE_SPEED_GATE re-arms the v2 0x8002DE04 skip (off by default);
// SSX_NATIVE_WATCH_OFFS="0x24,0x30,..." logs pc/lr/body of in-window
// rider-body word changes (cap 500 lines).
// SSX_NATIVE_COUNTER_RESTORE=1 (v3) saves the integer bookkeeping (race
// tick counter, five element stamps, app+168 flag, 48 RNG bytes) at each
// in-window ordinary entry and restores it at repeat entry, so both
// halves replay the tick from identical integer state (aborts if the
// counter did not advance exactly +1 in the first half).
#pragma once
#include "Core/Core.h"
#include "callback_timing.h"
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#ifdef SSX_NATIVE_TRIAL_APP
#include "trial_control.h"
#endif

namespace NativeProbe {
using Clock=std::chrono::steady_clock;
static auto start=Clock::now();
static double Now(){return std::chrono::duration<double>(Clock::now()-start).count();}
// Reading the clock on every native dispatch (millions per second) slowed the
// game by roughly 25-30% whenever the experimental window was active. Window
// checks use a copy refreshed at the callback and idle-seam boundaries, which
// occur at least once per frame.
static double now_cached=0;
static inline void RefreshNow(CPUState& c){
 if(c.pc==0x801cad24||c.pc==0x8010550c||c.pc==0x8010a4c8)now_cached=Now();
}
#ifdef SSX_NATIVE_TRIAL_APP
// Route F on the phone: the trial arms the v3b configuration (doubled updates,
// halved dt consts, full integer replay) without any environment. FMode is the
// live window; FTrial owns finish/restore once Running even after cancel.
static bool FMode(){
 return NativeTrial::status.load()==NativeTrial::Status::Running&&
  NativeTrial::kind.load()==NativeTrial::Kind::F&&NativeTrial::Active(now_cached);
}
static bool FTrial(){
 return NativeTrial::status.load()==NativeTrial::Status::Running&&
  NativeTrial::kind.load()==NativeTrial::Kind::F;
}
static bool f_patched=false;
#endif
static bool GuestWindowEnabled(){static bool value=[](){const char* p=std::getenv("SSX_NATIVE_GUEST_WINDOW");return p&&std::strcmp(p,"1")==0;}();return value;}
static unsigned GuestWindowTicks(){static unsigned value=[](){const char* p=std::getenv("SSX_NATIVE_WINDOW_TICKS");if(!p||!*p)return 4000000000u;long v=std::strtol(p,nullptr,10);return v>0?(unsigned)v:4000000000u;}();return value;}
static unsigned GuestWindowSkip(){static unsigned value=[](){const char* p=std::getenv("SSX_NATIVE_WINDOW_SKIP");if(!p||!*p)return 0u;long v=std::strtol(p,nullptr,10);return v>0?(unsigned)v:0u;}();return value;}
static bool SpeedGateEnabled(){static bool value=[](){const char* p=std::getenv("SSX_NATIVE_SPEED_GATE");return p&&std::strcmp(p,"1")==0;}();return value;}
static bool CounterRestoreEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 if(FMode())return true;
#endif
 static bool value=[](){const char* p=std::getenv("SSX_NATIVE_COUNTER_RESTORE");return p&&std::strcmp(p,"1")==0;}();return value;}
static u32 tick_saved=0;static bool tick_have=false;static unsigned tick_restores=0;
static u32 stamp_saved[5]={0,0,0,0,0};static u32 appflag_saved=0;static u32 rng_saved[12]={0,0,0,0,0,0,0,0,0,0,0,0};
static const u32 StampOffs[5]={0x30u,0x50u,0x70u,0x90u,0xB0u};
static unsigned WatchOffs[]{0,0,0,0,0,0,0,0};
static unsigned WatchCount(){static unsigned n=[](){const char* p=std::getenv("SSX_NATIVE_WATCH_OFFS");if(!p||!*p)return 0u;unsigned c=0;const char* s=p;while(*s&&c<8){while(*s==' '||*s==',')++s;if(!*s)break;char* e=nullptr;unsigned long v=std::strtoul(s,&e,0);if(e==s)break;WatchOffs[c++]=(unsigned)v;s=e;}return c;}();return n;}
static unsigned guest_phase=0;
static unsigned guest_doubled=0;
static unsigned guest_skipped=0;
static unsigned update_entries=0;
static bool ExperimentalWindow(){
 if(GuestWindowEnabled())return guest_phase==1;
#ifdef SSX_NATIVE_TRIAL_APP
 return NativeTrial::status.load()==NativeTrial::Status::Running&&NativeTrial::Active(now_cached);
#else
 return now_cached>=140&&now_cached<175;
#endif
}
static bool Valid(CPUState& c,u32 a,size_t n){return a>=0x80000000u && (u64)a+n<=0x80000000ull+c.ram_size;}
static u32 Word(CPUState& c,u32 a){
 if(!Valid(c,a,4))return 0;const auto* p=c.ram+(a-0x80000000u);
 return (u32(p[0])<<24)|(u32(p[1])<<16)|(u32(p[2])<<8)|p[3];
}
static u32 Rider(CPUState& c){u32 a=Word(c,0x803da1f8);for(u32 o:{0x74u,0xcu,0x28u}){if(!Valid(c,a,4))return 0;a=Word(c,a+o);}return a;}
static u32 TickCounterAddr(CPUState& c){u32 a=Word(c,c.gpr[13]-22632);for(u32 o:{116u,12u}){if(!Valid(c,a,4))return 0;a=Word(c,a+o);}return a?a+8:0;}
struct Snapshot {
 u32 rider=0,app=0,view=0,state=0;
 bool application_valid=false;
 std::array<unsigned char,0x800> body{};
 std::array<unsigned char,0x400> application{};
 std::array<unsigned char,0x100> camera{};
 std::array<unsigned char,48> random{};
};
static Snapshot Capture(CPUState& c,u32 app){
 Snapshot s;s.rider=Rider(c);s.app=app;
 s.state=Word(c,Word(c,s.rider+0x718)+0xd30);
 s.view=Word(c,Word(c,app+132)+4);
 auto copy=[&](auto& bytes,u32 a){if(Valid(c,a,bytes.size()))std::memcpy(bytes.data(),c.ram+(a-0x80000000u),bytes.size());};
 s.application_valid=Valid(c,app,s.application.size());
 copy(s.body,s.rider);copy(s.application,app);copy(s.camera,s.view);copy(s.random,0x8035de2c);
 return s;
}
template<size_t N>static std::string Diff(const std::array<unsigned char,N>&a,const std::array<unsigned char,N>&b){
 std::string s="[";int count=0;
 for(size_t i=0;i<N;i+=4){if(std::memcmp(a.data()+i,b.data()+i,4)) {if(count++)s+=",";s+=std::to_string(i);}}
 return s+"]";
}
// GXBE69 DOL b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce:
// 8010EBB4 requests 540 bytes (li r3,0x21c), 8010EBB8 calls allocator 801CCB88,
// and 8010EBC4 calls ctor 801073AC. The allocation label at 802E399C is GameModule.
// Ctor stores vtable 802E543C at 801073D4 and initializes through +536 at 80107604.
// Preserve the original 0x400-byte watch: its tail is adjacent RAM, not proven
// GameModule ownership. Classification adds evidence; it does not forgive a
// raw difference, identify neighboring owners, or restore any guest memory.
static constexpr u32 GameModuleVtable=0x802e543c;
static constexpr size_t GameModuleBytes=540;
static u32 ApplicationWord(const Snapshot& s,size_t offset){
 const auto* p=s.application.data()+offset;
 return (u32(p[0])<<24)|(u32(p[1])<<16)|(u32(p[2])<<8)|p[3];
}
static std::string ApplicationDiagnostics(const Snapshot& before,const Snapshot& after){
 const bool valid=before.application_valid&&after.application_valid;
 const u32 old_vtable=before.application_valid?ApplicationWord(before,0):0;
 const u32 new_vtable=after.application_valid?ApplicationWord(after,0):0;
 const bool known=valid&&before.app==after.app&&old_vtable==GameModuleVtable&&new_vtable==GameModuleVtable;
 std::string owned="[",adjacent="[",words="[";
 auto append=[](std::string& list,const std::string& value){if(list.size()>1)list+=",";list+=value;};
 if(valid)for(size_t offset=0;offset<before.application.size();offset+=4){
  const u32 old_word=ApplicationWord(before,offset),new_word=ApplicationWord(after,offset);
  if(old_word==new_word)continue;
  const auto index=std::to_string(offset);
  append(words,"{\"offset\":"+index+",\"before\":"+std::to_string(old_word)+",\"after\":"+std::to_string(new_word)+"}");
  if(known)append(offset<GameModuleBytes?owned:adjacent,index);
 }
 owned+="]";adjacent+="]";words+="]";
 return std::string(",\"app_snapshot_valid_before\":")+(before.application_valid?"true":"false")+
  ",\"app_snapshot_valid_after\":"+(after.application_valid?"true":"false")+
  ",\"app_vtable_before\":"+(before.application_valid?std::to_string(old_vtable):"null")+
  ",\"app_vtable_after\":"+(after.application_valid?std::to_string(new_vtable):"null")+
  ",\"app_owned_extent_bytes\":"+(known?std::to_string(GameModuleBytes):"null")+
  ",\"app_owned_offsets\":"+(known?owned:"null")+
  ",\"app_adjacent_offsets\":"+(known?adjacent:"null")+
  ",\"app_word_changes\":"+(valid?words:"null");
}
static u64 Hash(const unsigned char* p,size_t n){u64 h=14695981039346656037ull;for(size_t i=0;i<n;++i){h^=p[i];h*=1099511628211ull;}return h;}
struct Active {bool pending=false,repeated=false,skipped=false;u32 entry=0,ret=0,app=0,first_result=0;u64 tb=0;double wall=0,cpu_start=-1;Snapshot before;};
static Active update,render;
static unsigned repeats=0;
static unsigned update_repeats=0;
static unsigned half_cadence_updates=0;
static u32 offset_matrix=0;
static std::array<unsigned char,64> saved_matrix{};
static unsigned camera_offsets=0,camera_restores=0;
static unsigned retries=0,skipped_elapsed=0,skipped_queue=0;
static u32 queue_before=0,queue_after=0;
static unsigned view_matrix_calls=0,frame_end_calls=0,elapsed_calls=0,queue_calls=0,gate_calls=0,gate_ready=0;
static FILE* output_file=nullptr;
static FILE* Output(){
 if(!output_file){
#ifdef SSX_NATIVE_TRIAL_APP
  const char* p=NativeTrial::log_path.empty()?nullptr:NativeTrial::log_path.c_str();
#else
  const char* p=std::getenv("SSX_NATIVE_PROBE");
#endif
  if(!p)return static_cast<FILE*>(nullptr);
  FILE* f=std::fopen(p,"wx");
  if(!f){std::perror("native probe output");std::abort();}
  output_file=f;
 }
 return output_file;
}
static bool DoubleEnabled(){static bool value=[](){const char* p=std::getenv("SSX_NATIVE_DOUBLE_RENDER");return p&&std::strcmp(p,"1")==0;}();return value;}
static bool DoubleUpdateEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 if(FMode())return true;
#endif
 static bool value=[](){const char* p=std::getenv("SSX_NATIVE_DOUBLE_UPDATE");return p&&std::strcmp(p,"1")==0;}();return value;}
static bool HalfCadenceEnabled(){static bool value=[](){const char* p=std::getenv("SSX_NATIVE_HALF_CADENCE");return p&&std::strcmp(p,"1")==0;}();return value;}
static bool HalfDtEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 if(FMode())return true;
#endif
 static bool value=[](){const char* p=std::getenv("SSX_NATIVE_HALF_DT");return p&&std::strcmp(p,"1")==0;}();return value;}
static const u32 HalfDtAddrs[]={0x803db490,0x803dbba8,0x803dbd44,0x803dc0d4,0x803dc884,0x803dce70,0x803dd6dc,0x803dd8cc,0x803de62c,0x803df0b0,0x803df58c};
static const unsigned HalfDtCount=sizeof(HalfDtAddrs)/sizeof(HalfDtAddrs[0])+4;
struct PlannedConst {u32 addr,expect,value;};
static unsigned PlanConstSet(bool to_half,PlannedConst* plan){
 float sixth=1.0f/60.0f,twelfth=1.0f/120.0f,sixty=60.0f,onetwenty=120.0f;
 u32 exp6,half12,exp60,half120;
 std::memcpy(&exp6,&sixth,4);std::memcpy(&half12,&twelfth,4);
 std::memcpy(&exp60,&sixty,4);std::memcpy(&half120,&onetwenty,4);
 unsigned n=0;
 auto want=[&](u32 a,u32 stock,u32 halved){
  plan[n++]=PlannedConst{a,to_half?stock:halved,to_half?halved:stock};
 };
 for(u32 a:HalfDtAddrs)want(a,exp6,half12);
 want(0x803dcee0,exp60,half120);
 // v1: per-tick damping factors (0x8002784C loop) renormalized to sqrt.
 want(0x803db7e8,0x3f7ae148,0x3f7d6d55);
 want(0x803db7ec,0x3f74bc6a,0x3f7a4dfd);
 want(0x803db7f0,0x3f7a740e,0x3f7d3624);
 return n;
}
// Returns the first unverified index, or n when the whole set matches.
static unsigned VerifyConstSet(CPUState& c,PlannedConst* plan,unsigned n){
 for(unsigned i=0;i<n;++i)
  if(!Valid(c,plan[i].addr,4)||Word(c,plan[i].addr)!=plan[i].expect)return i;
 return n;
}
static void WriteConstPlan(CPUState& c,PlannedConst* plan,unsigned n){
 for(unsigned i=0;i<n;++i){
  auto* p=c.ram+plan[i].addr-0x80000000u;const u32 v=plan[i].value;
  p[0]=(unsigned char)(v>>24);p[1]=(unsigned char)(v>>16);p[2]=(unsigned char)(v>>8);p[3]=(unsigned char)v;
 }
}
static void WriteConstSet(CPUState& c,bool to_half,const char* tag){
 PlannedConst plan[HalfDtCount];
 const unsigned n=PlanConstSet(to_half,plan);
 // Verify the whole set before writing any of it. Interleaving the check with
 // the write leaves a drifting guest half-patched and then aborts, and on the
 // restore path that strands the run at 1/120 with no way back - the failure
 // this ordering exists to prevent.
 const unsigned bad=VerifyConstSet(c,plan,n);
 if(bad<n){
  std::fprintf(stderr,"[native-probe] %s const drift at %08x (%u of %u verified, none written)\n",
               tag,plan[bad].addr,bad,n);
  std::abort();
 }
 WriteConstPlan(c,plan,n);
}
static void PatchHalfDt(CPUState& c){
 static bool done=false;
 if(GuestWindowEnabled())return;
#ifdef SSX_NATIVE_TRIAL_APP
 if(FTrial())return; // F owns its patch/restore lifecycle below
#endif
 if(done||!HalfDtEnabled()||!ExperimentalWindow())return;
 WriteConstSet(c,true,"HALF_DT");
 done=true;
 std::fprintf(stderr,"[native-probe] HALF_DT patched %u consts\n",HalfDtCount);
}
#ifdef SSX_NATIVE_TRIAL_APP
static void FEmit(CPUState& c,const char* action){
 FILE* f=Output();
 if(f){
  std::fprintf(f,"{\"event\":\"f_trial\",\"action\":\"%s\",\"wall\":%.6f,\"tb\":%llu,\"doubled\":%u}\n",
               action,Now(),(unsigned long long)c.timebase,NativeTrial::updates_doubled.load());
  std::fflush(f);
 }
}
// Patch on the first live F update. Drift ends the trial gracefully with full
// evidence instead of aborting: the desktop abort exists to catch model errors
// during research, and a dead phone run keeps no more evidence than this.
static void FPatch(CPUState& c){
 if(f_patched||!FMode())return;
 PlannedConst plan[HalfDtCount];
 const unsigned n=PlanConstSet(true,plan);
 const unsigned bad=VerifyConstSet(c,plan,n);
 if(bad<n){
  std::fprintf(stderr,"[native-probe] F_TRIAL const drift at %08x (%u of %u verified, none written)\n",
               plan[bad].addr,bad,n);
  NativeTrial::limited=true;NativeTrial::Cancel();return;
 }
 WriteConstPlan(c,plan,n);
 f_patched=true;
 std::fprintf(stderr,"[native-probe] F_TRIAL patched %u consts\n",n);
 FEmit(c,"patched");
}
// Restore dt consts once the trial leaves the live window. Idempotent: the
// update-entry call does the work and the update-return call only finishes.
// A restore drift is loud and sticky: the guest stays halved until Full
// Reset rather than crashing the session.
static void FRestore(CPUState& c){
 if(!f_patched)return;
 PlannedConst plan[HalfDtCount];
 const unsigned n=PlanConstSet(false,plan);
 const unsigned bad=VerifyConstSet(c,plan,n);
 if(bad<n){
  std::fprintf(stderr,"[native-probe] F_TRIAL restore drift at %08x (%u of %u verified, guest stays halved)\n",
               plan[bad].addr,bad,n);
  NativeTrial::limited=true;
 }else{
  WriteConstPlan(c,plan,n);
  std::fprintf(stderr,"[native-probe] F_TRIAL restored %u consts\n",n);
 }
 f_patched=false;
 FEmit(c,"restored");
}
static bool FReady(){return !FTrial()||f_patched;}
static bool FCounterWindow(){return FMode()&&f_patched;}
#else
static bool FReady(){return true;}
static bool FCounterWindow(){return false;}
#endif
static bool CounterWindow(){
 if(FCounterWindow())return true;
 return CounterRestoreEnabled()&&GuestWindowEnabled()&&guest_phase==1;
}
static bool WaitEnabled(){static const bool on=std::getenv("SSX_NATIVE_WAIT_REPEAT")!=nullptr;return on;}
static bool SweepEnabled(){static const bool on=std::getenv("SSX_NATIVE_FROZEN_VIEW_SWEEP")!=nullptr;return on;}
static bool SkipEnabled(){
#ifdef SSX_NATIVE_TRIAL_APP
 return true;
#else
 static const bool on=std::getenv("SSX_NATIVE_SKIP_BOOKKEEPING")!=nullptr;return on;
#endif
}
static bool CameraEnabled(){static const bool on=std::getenv("SSX_NATIVE_CAMERA_OFFSET")!=nullptr;return on;}
static bool CaptureEnabled(){static const bool on=std::getenv("SSX_NATIVE_CAPTURE")!=nullptr;return on;}
static bool BodyDumpEnabled(){static const bool on=std::getenv("SSX_NATIVE_BODY_DUMP")!=nullptr;return on;}
static void Emit(CPUState& c,const char* kind,Active& a,const Snapshot& b){
 const double wall_end=Now();
 const double cpu_ms=RenderResearch::CPUMilliseconds(a.cpu_start,RenderResearch::ThreadCPUSeconds());
 char cpu_text[48]="null";
 if(cpu_ms>=0)std::snprintf(cpu_text,sizeof(cpu_text),"%.6f",cpu_ms);
 FILE* file=Output();
 if(!file)return;
 const auto body=Diff(a.before.body,b.body),app=Diff(a.before.application,b.application),camera=Diff(a.before.camera,b.camera);
 const auto app_details=ApplicationDiagnostics(a.before,b);
 const bool moved=std::memcmp(a.before.body.data()+240,b.body.data()+240,12)!=0;
 std::string body_words="null";
 if(BodyDumpEnabled()){
  body_words="[";const auto* p=b.body.data();
  for(size_t i=0;i+4<=b.body.size();i+=4){
   if(i)body_words.push_back(',');
   body_words+=std::to_string((u32)((u32)p[i]<<24|(u32)p[i+1]<<16|(u32)p[i+2]<<8|(u32)p[i+3]));
  }
  body_words.push_back(']');
 }
 std::fprintf(file,"{\"event\":\"%s\",\"repeat\":%d,\"retries\":%u,\"camera_offsets\":%u,\"camera_restores\":%u,\"skipped_elapsed\":%u,\"skipped_queue\":%u,\"skipped_update\":%d,\"queue_before\":%u,\"queue_after\":%u,\"result\":%u,\"view_matrix_calls\":%u,\"frame_end_calls\":%u,\"elapsed_calls\":%u,\"queue_calls\":%u,\"gate_calls\":%u,\"gate_ready\":%u,\"wall\":%.6f,\"duration_ms\":%.6f,\"cpu_duration_ms\":%s,\"tb_start\":%llu,\"tb_end\":%llu,\"app\":%u,\"rider\":%u,\"same_rider\":%d,\"state_before\":%u,\"state_after\":%u,\"position_changed\":%d,\"rng_changed\":%d,\"body_hash_before\":%llu,\"body_hash_after\":%llu,\"body_offsets\":%s,\"app_offsets\":%s,\"view\":%u,\"same_view\":%d,\"view_offsets\":%s%s,\"body_words\":%s}\n",
 kind,a.repeated,retries,camera_offsets,camera_restores,skipped_elapsed,skipped_queue,a.skipped?1:0,queue_before,queue_after,c.gpr[3],render.pending?view_matrix_calls:0,render.pending?frame_end_calls:0,render.pending?elapsed_calls:0,render.pending?queue_calls:0,render.pending?gate_calls:0,render.pending?gate_ready:0,wall_end,(wall_end-a.wall)*1000,cpu_text,(unsigned long long)a.tb,(unsigned long long)c.timebase,a.app,b.rider,a.before.rider==b.rider,a.before.state,b.state,moved,a.before.random!=b.random,(unsigned long long)Hash(a.before.body.data(),a.before.body.size()),(unsigned long long)Hash(b.body.data(),b.body.size()),body.c_str(),app.c_str(),b.view,a.before.view==b.view,camera.c_str(),app_details.c_str(),body_words.c_str());
 std::fflush(file);
}
static inline void Step(CPUState& c){
 RefreshNow(c);
 // v2: run the speed update (0x8002DE04) once per tick. Gate at its entry
 // (a block start, observed pre-execution, so no frame exists to undo).
 // Env-gated: HALF_DT alone must mean v1 consts, never the v2 gate.
 if(c.pc==0x8002de04&&SpeedGateEnabled()&&ExperimentalWindow()&&update.pending&&update.repeated){
  static bool logged=false;if(!logged){logged=true;std::fprintf(stderr,"[native-probe] SPEED_GATE engaged\n");}
  c.pc=c.lr;return;
 }
#ifdef SSX_NATIVE_TRIAL_APP
 // F restores consts at update entries, ahead of the trial-app early return:
 // a cancelled trial must restore even though its window is already closed.
 // Finishing waits for the matching return so Finished always means
 // quiescent. Repeats re-enter with pending set and skip both.
 if(c.pc==0x8010550c&&!update.pending&&!render.pending){
  if(FTrial()&&!NativeTrial::Active(now_cached))FRestore(c);
  else FPatch(c);
 }
 if(!ExperimentalWindow()&&!render.pending&&!update.pending)return;
#endif
 if(WatchCount()&&ExperimentalWindow()&&update.pending){
  static unsigned logged=0;static bool init=false;static u32 last[8]={0,0,0,0,0,0,0,0};
  u32 r=Rider(c);
  if(r&&Valid(c,r,0x800)){
   if(!init){for(unsigned i=0;i<WatchCount();++i)last[i]=Word(c,r+WatchOffs[i]);init=true;}
   else if(logged<500){
    for(unsigned i=0;i<WatchCount();++i){
     u32 v=Word(c,r+WatchOffs[i]);
     if(v!=last[i]){std::fprintf(stderr,"[native-probe] WATCH off=%x pc=%08x lr=%08x body%d %08x->%08x\n",WatchOffs[i],c.pc,c.lr,update.repeated?2:1,last[i],v);last[i]=v;if(++logged>=500)break;}
    }
   }
  }
 }
 if(!Output())return;
 // Count cross-chunk graphics calls. Same-chunk scene helpers compile to
 // direct gotos and cannot be counted at this dispatcher boundary.
 if(render.pending){
  if(c.pc==0x80224cc8&&c.lr==0x8010a6a8&&now_cached>140&&repeats<4){
   std::fprintf(stderr,"[native-matrix] repeat=%d ptr=%08x",render.repeated,c.gpr[4]);
   for(unsigned i=0;i<16;++i){u32 bits=Word(c,c.gpr[4]+i*4);float v;std::memcpy(&v,&bits,4);std::fprintf(stderr," %.6g",v);}
   std::fprintf(stderr,"\n");
  }
  if(render.repeated&&CameraEnabled()&&(!SweepEnabled()||(repeats>40&&repeats<=80))&&c.pc==0x8010a6a8){
   const u32 ptr=Word(c,c.gpr[3]+6132);
   if(!Valid(c,ptr,64)||offset_matrix){std::fprintf(stderr,"[native-probe] invalid matrix override\n");std::abort();}
   offset_matrix=ptr;std::memcpy(saved_matrix.data(),c.ram+ptr-0x80000000u,64);
   u32 bits=Word(c,ptr+48);float value;std::memcpy(&value,&bits,4);value+=500.0f;std::memcpy(&bits,&value,4);
   auto* bytes=c.ram+ptr+48-0x80000000u;for(unsigned i=0;i<4;++i)bytes[i]=bits>>(24-i*8);
   ++camera_offsets;
  }
  if(CaptureEnabled()&&c.pc==0x8021a5fc&&c.lr==0x8010abf0&&render.repeated&&repeats%20==0){
   Core::SaveScreenShot("native-seam-request-repeat-"+std::to_string(repeats));
  }
  if(render.repeated&&SkipEnabled()&&c.pc==0x8015c5a0&&c.lr==0x8010ac24){++skipped_elapsed;c.pc=c.lr;return;}
  if(render.repeated&&SkipEnabled()&&c.pc==0x80139f20&&c.lr==0x8010ac2c){++skipped_queue;c.pc=c.lr;return;}
  if(c.pc==0x80224cc8 && c.lr==0x8010a6a8)++view_matrix_calls;
  if(c.pc==0x8021a5fc && c.lr==0x8010abf0)++frame_end_calls;
  if(c.pc==0x8015c5a0)++elapsed_calls;
  if(c.pc==0x80139f20)++queue_calls;
  if(c.pc==0x8010a50c){++gate_calls;if(c.gpr[3]&255)++gate_ready;}
 }
 if(c.pc!=0x8010550c && c.pc!=0x8010a4c8 && (!update.pending||c.pc!=update.ret) && (!render.pending||c.pc!=render.ret))return;
 if(update.pending&&c.pc==update.ret){
  auto b=Capture(c,update.app);Emit(c,"update",update,b);
  bool just_armed=false;
  if(GuestWindowEnabled()&&guest_phase==0&&Valid(c,b.rider,0x800)&&update.before.state==b.state&&std::memcmp(update.before.body.data()+240,b.body.data()+240,12)!=0){
   guest_phase=3;guest_skipped=0;just_armed=true;
   std::fprintf(stderr,"[native-probe] GUEST_WINDOW armed at update %u (skip %u limit %u)\n",update_entries,GuestWindowSkip(),GuestWindowTicks());
  }
  if(GuestWindowEnabled()&&guest_phase==3&&!update.repeated){
   ++guest_skipped;
   if(guest_skipped>GuestWindowSkip()){
    if(HalfDtEnabled())WriteConstSet(c,true,"GUEST_WINDOW");
    guest_phase=1;just_armed=true;
    std::fprintf(stderr,"[native-probe] GUEST_WINDOW engaged at update %u\n",update_entries);
   }
  }
  if(!just_armed&&!update.repeated&&DoubleUpdateEnabled()&&ExperimentalWindow()&&FReady()&&Valid(c,b.rider,0x800)&&update.before.state==b.state){
   update.repeated=true;++update_repeats;
   if(GuestWindowEnabled()&&guest_phase==1)++guest_doubled;
   bool skip_repeat=false;
   if(CounterWindow()){
    const u32 g=TickCounterAddr(c);
    const bool have_addr=g&&Valid(c,g,4);
    const u32 v=have_addr?Word(c,g):0;
    const bool model_ok=have_addr&&tick_have&&(v-tick_saved)==1u;
    if(!model_ok){
     bool graceful=false;
#ifdef SSX_NATIVE_TRIAL_APP
     if(FTrial()){
      std::fprintf(stderr,"[native-probe] F_TRIAL counter drift (graceful end)\n");
      NativeTrial::limited=true;NativeTrial::Cancel();skip_repeat=true;graceful=true;
     }
#endif
     if(!graceful){
      if(!have_addr){std::fprintf(stderr,"[native-probe] COUNTER_RESTORE no addr\n");std::abort();}
      std::fprintf(stderr,"[native-probe] COUNTER_RESTORE model drift saved=%u have=%d now=%u\n",tick_saved,tick_have?1:0,v);std::abort();
     }
    }
    if(!skip_repeat){
     auto putw=[&](u32 a,u32 value){auto* q=c.ram+a-0x80000000u;q[0]=(unsigned char)(value>>24);q[1]=(unsigned char)(value>>16);q[2]=(unsigned char)(value>>8);q[3]=(unsigned char)value;};
     putw(g,tick_saved);
     const u32 r=Rider(c);
     if(r&&Valid(c,r,0x800))for(int i=0;i<5;++i)putw(r+StampOffs[i],stamp_saved[i]);
     if(Valid(c,update.app+168,4))putw(update.app+168,appflag_saved);
     if(Valid(c,0x8035de2c,48))for(int i=0;i<12;++i)putw(0x8035de2c+4*i,rng_saved[i]);
     if(++tick_restores<=5)std::fprintf(stderr,"[native-probe] COUNTER_RESTORE #%u saved=%u\n",tick_restores,tick_saved);
    }
   }
   if(skip_repeat){update.pending=false;}
   else{
#ifdef SSX_NATIVE_TRIAL_APP
    if(FTrial())++NativeTrial::updates_doubled;
#endif
    update.before=b;update.tb=c.timebase;update.wall=Now();update.cpu_start=RenderResearch::ThreadCPUSeconds();
    c.gpr[3]=update.app;c.pc=update.entry;c.lr=update.ret;return;
   }
  }
  update.pending=false;
#ifdef SSX_NATIVE_TRIAL_APP
  // Finish at the quiescent return, after the entry restore above has run:
  // the frontend waits for Running to clear before pausing/checkpointing.
  if(FTrial()&&!NativeTrial::Active(now_cached)){
   FRestore(c);
   NativeTrial::status=NativeTrial::Status::Finished;
  }
#endif
 }
 if(render.pending&&c.pc==render.ret){
  // This field describes callback completion, not intermediate dispatches.
  queue_after=Word(c,c.gpr[13]-20556);
  if(render.repeated&&WaitEnabled()&&!(c.gpr[3]&255)&&Now()-render.wall<2&&retries<100000){
   ++retries;c.gpr[3]=render.app;c.pc=render.entry;c.lr=render.ret;return;
  }
  if(offset_matrix){
   std::memcpy(c.ram+offset_matrix-0x80000000u,saved_matrix.data(),64);offset_matrix=0;++camera_restores;
  }
  auto b=Capture(c,render.app);Emit(c,"render",render,b);
  if((!render.repeated||SweepEnabled())&&(c.gpr[3]&255)&&view_matrix_calls&&frame_end_calls&&DoubleEnabled()&&now_cached>140&&repeats<120&&Valid(c,b.rider,0x800)&&b.state==0){
   if(!render.repeated)render.first_result=c.gpr[3];
   render.repeated=true;++repeats;
   view_matrix_calls=frame_end_calls=elapsed_calls=queue_calls=gate_calls=gate_ready=0;
   retries=skipped_elapsed=skipped_queue=camera_offsets=camera_restores=0;queue_before=Word(c,c.gpr[13]-20556);
   render.before=b;render.tb=c.timebase;render.wall=Now();render.cpu_start=RenderResearch::ThreadCPUSeconds();
   c.gpr[3]=render.app;c.pc=render.entry;c.lr=render.ret;return;
  }
  if(render.repeated)c.gpr[3]=render.first_result;
  render.pending=false;
 }
 if(c.pc==0x8010550c||c.pc==0x8010a4c8){
  auto& a=c.pc==0x8010550c?update:render;
  // Repeats deliberately re-dispatch with pending set; only genuinely
  // unexpected recursion is worth a log line.
  if(a.pending){if(!(a.repeated&&c.pc==a.entry))std::fprintf(stderr,"[native-probe] unexpected recursive callback\n");return;}
  if(c.pc==0x8010a4c8)view_matrix_calls=frame_end_calls=elapsed_calls=queue_calls=gate_calls=gate_ready=0;
  if(c.pc==0x8010a4c8){retries=skipped_elapsed=skipped_queue=camera_offsets=camera_restores=0;queue_before=Word(c,c.gpr[13]-20556);}
  if(c.pc==0x8010550c){
   ++update_entries;
   if(GuestWindowEnabled()&&guest_phase==1&&guest_doubled>=GuestWindowTicks()){
    if(HalfDtEnabled())WriteConstSet(c,false,"GUEST_WINDOW");
    guest_phase=2;
    std::fprintf(stderr,"[native-probe] GUEST_WINDOW closed at update %u (doubled %u)\n",update_entries,guest_doubled);
   }
   if(CounterWindow()){
    const u32 g=TickCounterAddr(c);
    if(g&&Valid(c,g,4)){tick_saved=Word(c,g);tick_have=true;}
    const u32 r=Rider(c);
    if(r&&Valid(c,r,0x800))for(int i=0;i<5;++i)stamp_saved[i]=Word(c,r+StampOffs[i]);
    const u32 app=c.gpr[3];
    if(app&&Valid(c,app+168,4))appflag_saved=Word(c,app+168);
    if(Valid(c,0x8035de2c,48))for(int i=0;i<12;++i)rng_saved[i]=Word(c,0x8035de2c+4*i);
   }
  }
  if(c.pc==0x8010550c)PatchHalfDt(c);
  if(c.pc==0x8010550c&&HalfCadenceEnabled()&&ExperimentalWindow()&&++half_cadence_updates%2==0){
   // Emit a zero-work marker without arming: the hook observes post-execution
   // pc, so an armed skip would miss its completion and wedge pending until
   // the next return. The guest body never runs.
   a.app=c.gpr[3];a.tb=c.timebase;a.wall=Now();a.cpu_start=RenderResearch::ThreadCPUSeconds();
   a.before=Capture(c,a.app);a.repeated=false;a.skipped=true;
   Emit(c,"update",a,a.before);a.skipped=false;
   c.pc=c.lr;return;
  }
  a.pending=true;a.repeated=false;a.skipped=false;a.entry=c.pc;a.ret=c.lr;a.app=c.gpr[3];a.tb=c.timebase;a.wall=Now();a.cpu_start=RenderResearch::ThreadCPUSeconds();a.before=Capture(c,a.app);
 }
}
}
