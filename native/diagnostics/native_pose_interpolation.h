// Isolated GXBE69 native interpolation experiment. Requires NativeProbe and
// NativeSchedule. The builder pins the executable; this is authored adapter
// code, not reconstructed game source. Never writes authoritative poses.
#pragma once
#include "pose_history.h"
#include <vector>

namespace NativeInterpolation {
using namespace NativeProbe;
using namespace RenderResearch;
struct Binding { u32 index; PoseKey key; };
static std::vector<Binding> bindings;
static std::unordered_map<u32,PoseKey> palette;
static PoseHistory history;
static u32 base=0, stride=0;
static u64 generation=0, update_ticks=0;
static float alpha=1;
static bool active=false, prepared=false, reset_next=true;
static unsigned loaded=0, blended=0, camera_only=0, texture_blended=0, captured_bindings=0;
static Matrix camera{}, camera_delta{};
static bool has_camera_delta=false;
static Matrix ReadMatrix(CPUState& c,u32 p) {
 Matrix m{};
 for(unsigned i=0;i<12;++i){u32 bits=Word(c,p+4*i);std::memcpy(&m[i],&bits,4);}
 return m;
}
// Filled only from a validated persistent owner at the palette-build seam.
// A scratch skeleton source or a transient render packet is not an owner.
static u32 Owner(CPUState& c) {
 const u32 parent=Word(c,c.gpr[1]), caller=Word(c,parent);
 if(!Valid(c,parent,32)||!Valid(c,caller,112)||Word(c,parent+4)!=0x8021aec8)return 0;
 const u32 ret=Word(c,caller+4);
 if(ret!=0x801c3580&&ret!=0x801c34f8&&ret!=0x801c32ac&&ret!=0x801c3210)return 0;
 // r25 is the model instance in both validated callers, with its own two
 // input bone arrays. Their multiplied global scratch matrices are shared.
 const u32 owner=c.gpr[25], count=Word(c,owner+16);
 if(!Valid(c,owner,320)||count==0||count>64||
    !Valid(c,Word(c,owner+52),count*64)||!Valid(c,Word(c,owner+56),count*64))return 0;
 return owner;
}
static void Prepare(CPUState& c) {
 if(!active||stride!=48||!Valid(c,base,48))return;
 history.Begin(generation); palette.clear();
 camera=ReadMatrix(c,base);
 history.Add({1,0,0,0},camera);
 palette.emplace(0,PoseKey{1,0,0,0});
 for(const auto& b:bindings){
  if(!Valid(c,base+b.index*48,48))continue;
  history.Add(b.key,ReadMatrix(c,base+b.index*48));
  auto [it,inserted]=palette.emplace(b.index,b.key);
  if(!inserted&&!(it->second==b.key)){active=false;history.Reset();return;}
 }
 history.Seal();prepared=true;captured_bindings=bindings.size();
 Matrix view,inv,old,old_inv;
 has_camera_delta=history.Sample({1,0,0,0},camera,alpha,view)&&Inverse(camera,inv);
 if(has_camera_delta&&history.Sample({1,0,0,0},camera,0,old)&&Inverse(old,old_inv)){
  double distance=0;for(unsigned i:{3u,7u,11u}){double d=inv[i]-old_inv[i];distance+=d*d;}
  if(distance>500.0*500.0){history.ForgetPrevious();has_camera_delta=false;}
 }
 if(has_camera_delta)camera_delta=Multiply(view,inv);
 else prepared=false; // warm-up or camera cut: keep the whole scene current
}
static void WriteXF(CPUState& c,const Matrix& m,u32 address,unsigned count) {
 c.external_write(&c,0xcc008000,0x10,1);
 c.external_write(&c,0xcc008000,((count-1)<<16)|address,4);
 for(unsigned i=0;i<count;++i){u32 bits;std::memcpy(&bits,&m[i],4);c.external_write(&c,0xcc008000,bits,4);}
 c.pc=c.lr;
}
static void Before(CPUState& c) {
 auto& timing=Core::System::GetInstance().GetCoreTiming();
 // Count one generation per tick at the first half's return: under F doubling
 // the repeat half returns through update.ret too, and counting it would
 // advance two generations per tick and empty the pose history every frame.
 if(update.pending&&c.pc==update.ret&&!update.repeated){++generation;update_ticks=timing.GetTicks();}
 if(render.pending&&c.pc==render.ret){
#ifdef SSX_NATIVE_TRIAL_APP
  // Frames count completed draws during any running trial; extras need an
  // active smoothing pass. Smoothing behavior is unchanged: active implies a
  // running smoothing trial.
  const bool f_run=NativeTrial::kind.load()==NativeTrial::Kind::F&&
                   NativeTrial::status.load()==NativeTrial::Status::Running;
  if((active||f_run)&&(c.gpr[3]&255)&&frame_end_calls){
   ++NativeTrial::frames;if(active&&render.repeated)++NativeTrial::extras;
   if(render.repeated&&blended>0)++NativeTrial::extras_blended;
  }
#endif
  if(active){
   std::fprintf(Output(),"{\"event\":\"interpolation\",\"wall\":%.6f,\"repeat\":%d,\"generation\":%llu,\"alpha\":%.6f,\"loaded\":%u,\"blended\":%u,\"camera_only\":%u,\"texture_blended\":%u,\"bindings\":%u}\n",Now(),render.repeated,(unsigned long long)generation,alpha,loaded,blended,camera_only,texture_blended,captured_bindings);
   std::fflush(Output());active=false;
  }
 }
 if(!render.pending||!active)return;
 if(c.pc==0x8029e9fc&&c.gpr[3]==21){base=c.gpr[4];stride=c.gpr[5];bindings.clear();}
 if(c.pc==0x8020f8f8&&c.lr==0x8021adf4&&stride==48){
  const u32 dest=c.gpr[5],spacing=c.gpr[6],count=c.gpr[7],owner=Owner(c);
  if(owner&&dest>=base&&(dest-base)%48==0&&(spacing==1||spacing==2)&&count<=512&&
     (u64(dest)-base)/48+u64(count)*spacing<=6144&&
     bindings.size()+count*spacing<=PoseHistory::Capacity){
   for(u32 i=0;i<count;++i)for(u32 k=0;k<spacing;++k)
    bindings.push_back({(dest-base)/48+i*spacing+k,{owner,c.gpr[9]+i*12,spacing,k}});
  }
 }
 if(c.pc==0x8021a5fc&&c.lr==0x8010abf0)Prepare(c);
 if(!prepared||!c.external_write)return;
 const bool position=c.pc==0x802a2e34;
 const bool texture=c.pc==0x802a2f9c&&c.lr==0x802334d4;
 if(!position&&!texture)return;
 const u32 index=c.gpr[3];
 if(index>6143||!Valid(c,base+index*48,48))return;
 ++loaded;
 Matrix raw=ReadMatrix(c,base+index*48),out;
 bool changed=false;
 const auto binding=palette.find(index);
 if(binding!=palette.end())changed=history.Sample(binding->second,raw,alpha,out);
 // Static scene batches have current model transforms: adjust only the view.
 // Camera-centred backgrounds use rotation only, preserving their centre.
 if(!changed&&position&&c.lr==0x8022e698&&has_camera_delta&&Finite(raw)){
  auto delta=camera_delta;
  if(std::abs(raw[3])+std::abs(raw[7])+std::abs(raw[11])<.1f)
   delta[3]=delta[7]=delta[11]=0;
  out=Multiply(delta,raw);changed=Finite(out);if(changed)++camera_only;
 }
 if(!changed)return;
 ++blended;
 if(position)WriteXF(c,out,c.gpr[4]*4,12);
 else {++texture_blended;const u32 slot=c.gpr[4];WriteXF(c,out,slot<64?slot*4:0x500+(slot-64)*4,c.gpr[5]==1?8:12);}
}
static inline void Step(CPUState& c){
 // Most native dispatches cannot affect the adapter. Avoid guest reads,
 // atomics, clock queries and runtime lookups until an observed boundary.
 if((!update.pending||c.pc!=update.ret)&&(!render.pending||c.pc!=render.ret)){
  switch(c.pc){
   case 0x801cad24: case 0x8010550c: case 0x8010a4c8: // idle/update/render
   case 0x80224cc8: case 0x8010a6a8: case 0x8021a5fc: // view/frame end
   case 0x8015c5a0: case 0x80139f20: case 0x8010a50c: // bookkeeping/readiness
   case 0x802a0144: // XFB destination validation
   case 0x8029e9fc: case 0x8020f8f8: // palette setup/build
   case 0x802a2e34: case 0x802a2f9c: // position/texture upload
    break;
   default:return;
  }
 }
 RefreshNow(c);
#ifdef SSX_NATIVE_TRIAL_APP
 const auto trial_status=NativeTrial::status.load();
 if(trial_status!=NativeTrial::Status::Waiting&&trial_status!=NativeTrial::Status::Running&&
    !render.pending&&!update.pending&&!NativeSchedule::mode_changed&&c.pc!=0x801cad24)return;
#endif
 Before(c);
 NativeSchedule::Step(c);
 if(!ExperimentalWindow())reset_next=true;
 if(c.pc==0x8010a4c8&&render.pending){
  const auto state=Capture(c,render.app);
#ifdef SSX_NATIVE_TRIAL_APP
  // F renders normally; the immediate-upload interpolation path stays off so
  // the trial measures doubled updates rather than matrix re-uploads.
  const bool smoothing_trial=NativeTrial::kind.load()!=NativeTrial::Kind::F;
#else
  const bool smoothing_trial=true;
#endif
  active=smoothing_trial&&ExperimentalWindow()&&NativeSchedule::ActiveRiderState(state.state)&&Valid(c,state.rider,0x800);
  prepared=false;has_camera_delta=false;loaded=blended=camera_only=texture_blended=captured_bindings=0;
  bindings.clear();
  if(!active){history.Reset();return;}
  if(reset_next){history.Reset();reset_next=false;}
  const auto ticks=Core::System::GetInstance().GetCoreTiming().GetTicks();
  const double period=Core::System::GetInstance().GetSystemTimers().GetTicksPerSecond()/59.94005994;
  alpha=float(std::clamp(double(ticks-update_ticks)/period,0.0,1.0));
 }
}
}
#ifdef SSX_NATIVE_TRIAL_APP
extern "C" void SSXResetNativeTrial(const char* path){
 using namespace NativeProbe;
 if(output_file){std::fclose(output_file);output_file=nullptr;}
 start=Clock::now();now_cached=0;update={};render={};offset_matrix=0;repeats=0;
 NativeTrial::log_path=path?path:"";NativeTrial::status=NativeTrial::Status::Idle;NativeTrial::cancel=false;
 NativeTrial::limited=false;
 NativeTrial::kind=NativeTrial::Kind::Smoothing;
 NativeTrial::frames=NativeTrial::extras=NativeTrial::updates_doubled=0;NativeTrial::extras_blended=0;NativeTrial::ends=0;
 f_patched=false;
 NativeSchedule::deadline={};NativeSchedule::last_draw=0;
 NativeSchedule::schedule_started=NativeSchedule::mode_changed=false;
 NativeSchedule::mode_address=NativeSchedule::first_xfb=0;
 NativeInterpolation::history.Reset();NativeInterpolation::bindings.clear();NativeInterpolation::palette.clear();
 NativeInterpolation::base=NativeInterpolation::stride=0;NativeInterpolation::generation=NativeInterpolation::update_ticks=0;
 NativeInterpolation::active=NativeInterpolation::prepared=NativeInterpolation::has_camera_delta=false;
 NativeInterpolation::reset_next=true;
}
#endif
