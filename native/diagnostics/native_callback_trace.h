// Authored diagnostic hooks for the pinned GXBE69 executable. Not game source.
// Isolated research players only: repeat calls are an intentionally incomplete
// experiment, not a production 120 Hz implementation. No guest instructions
// are patched. Graphics readiness, guest clocks and interrupts remain active.
// Snapshot ranges are bounded RAM windows, not complete object ownership maps.
#pragma once
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace NativeProbe {
using Clock=std::chrono::steady_clock;
static const auto start=Clock::now();
static double Now(){return std::chrono::duration<double>(Clock::now()-start).count();}
static bool Valid(CPUState& c,u32 a,size_t n){return a>=0x80000000u && (u64)a+n<=0x80000000ull+c.ram_size;}
static u32 Word(CPUState& c,u32 a){
 if(!Valid(c,a,4))return 0;const auto* p=c.ram+(a-0x80000000u);
 return (u32(p[0])<<24)|(u32(p[1])<<16)|(u32(p[2])<<8)|p[3];
}
static u32 Rider(CPUState& c){u32 a=Word(c,0x803da1f8);for(u32 o:{0x74u,0xcu,0x28u}){if(!Valid(c,a,4))return 0;a=Word(c,a+o);}return a;}
struct Snapshot {
 u32 rider=0,app=0,view=0,state=0;
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
 copy(s.body,s.rider);copy(s.application,app);copy(s.camera,s.view);copy(s.random,0x8035de2c);
 return s;
}
template<size_t N>static std::string Diff(const std::array<unsigned char,N>&a,const std::array<unsigned char,N>&b){
 std::string s="[";int count=0;
 for(size_t i=0;i<N;i+=4){if(std::memcmp(a.data()+i,b.data()+i,4)) {if(count++)s+=",";s+=std::to_string(i);}}
 return s+"]";
}
static u64 Hash(const unsigned char* p,size_t n){u64 h=14695981039346656037ull;for(size_t i=0;i<n;++i){h^=p[i];h*=1099511628211ull;}return h;}
struct Active {bool pending=false,repeated=false;u32 entry=0,ret=0,app=0,first_result=0;u64 tb=0;double wall=0;Snapshot before;};
static Active update,render;
static unsigned repeats=0;
static unsigned view_matrix_calls=0,frame_end_calls=0,elapsed_calls=0,queue_calls=0,gate_calls=0,gate_ready=0;
static FILE* Output(){
 static FILE* file=[](){
  const char* p=std::getenv("SSX_NATIVE_PROBE");
  if(!p)return static_cast<FILE*>(nullptr);
  FILE* f=std::fopen(p,"wx");
  if(!f){std::perror("native probe output");std::abort();}
  return f;
 }();
 return file;
}
static bool DoubleEnabled(){static bool value=[](){const char* p=std::getenv("SSX_NATIVE_DOUBLE_RENDER");return p&&std::strcmp(p,"1")==0;}();return value;}
static void Emit(CPUState& c,const char* kind,Active& a,const Snapshot& b){
 FILE* file=Output();
 if(!file)return;
 const auto body=Diff(a.before.body,b.body),app=Diff(a.before.application,b.application),camera=Diff(a.before.camera,b.camera);
 const bool moved=std::memcmp(a.before.body.data()+240,b.body.data()+240,12)!=0;
 std::fprintf(file,"{\"event\":\"%s\",\"repeat\":%d,\"result\":%u,\"view_matrix_calls\":%u,\"frame_end_calls\":%u,\"elapsed_calls\":%u,\"queue_calls\":%u,\"gate_calls\":%u,\"gate_ready\":%u,\"wall\":%.6f,\"duration_ms\":%.6f,\"tb_start\":%llu,\"tb_end\":%llu,\"app\":%u,\"rider\":%u,\"same_rider\":%d,\"state_before\":%u,\"state_after\":%u,\"position_changed\":%d,\"rng_changed\":%d,\"body_hash_before\":%llu,\"body_hash_after\":%llu,\"body_offsets\":%s,\"app_offsets\":%s,\"view\":%u,\"same_view\":%d,\"view_offsets\":%s}\n",
 kind,a.repeated,c.gpr[3],render.pending?view_matrix_calls:0,render.pending?frame_end_calls:0,render.pending?elapsed_calls:0,render.pending?queue_calls:0,render.pending?gate_calls:0,render.pending?gate_ready:0,Now(),(Now()-a.wall)*1000,(unsigned long long)a.tb,(unsigned long long)c.timebase,a.app,b.rider,a.before.rider==b.rider,a.before.state,b.state,moved,a.before.random!=b.random,(unsigned long long)Hash(a.before.body.data(),a.before.body.size()),(unsigned long long)Hash(b.body.data(),b.body.size()),body.c_str(),app.c_str(),b.view,a.before.view==b.view,camera.c_str());
 std::fflush(file);
}
static inline void Step(CPUState& c){
 if(!Output())return;
 // Count cross-chunk graphics calls. Same-chunk scene helpers compile to
 // direct gotos and cannot be counted at this dispatcher boundary.
 if(render.pending){
  if(c.pc==0x80224cc8 && c.lr==0x8010a6a8)++view_matrix_calls;
  if(c.pc==0x8021a5fc && c.lr==0x8010abf0)++frame_end_calls;
  if(c.pc==0x8015c5a0)++elapsed_calls;
  if(c.pc==0x80139f20)++queue_calls;
  if(c.pc==0x8010a50c){++gate_calls;if(c.gpr[3]&255)++gate_ready;}
 }
 if(c.pc!=0x8010550c && c.pc!=0x8010a4c8 && (!update.pending||c.pc!=update.ret) && (!render.pending||c.pc!=render.ret))return;
 if(update.pending&&c.pc==update.ret){auto b=Capture(c,update.app);Emit(c,"update",update,b);update.pending=false;}
 if(render.pending&&c.pc==render.ret){
  auto b=Capture(c,render.app);Emit(c,"render",render,b);
  if(!render.repeated&&DoubleEnabled()&&Now()>140&&repeats<120&&Valid(c,b.rider,0x800)&&b.state==0){
   render.repeated=true;render.first_result=c.gpr[3];++repeats;
   view_matrix_calls=frame_end_calls=elapsed_calls=queue_calls=gate_calls=gate_ready=0;
   render.before=b;render.tb=c.timebase;render.wall=Now();
   c.gpr[3]=render.app;c.pc=render.entry;c.lr=render.ret;return;
  }
  if(render.repeated)c.gpr[3]=render.first_result;
  render.pending=false;
 }
 if(c.pc==0x8010550c||c.pc==0x8010a4c8){
  auto& a=c.pc==0x8010550c?update:render;
  if(a.pending){std::fprintf(stderr,"[native-probe] unexpected recursive callback\n");return;}
  if(c.pc==0x8010a4c8)view_matrix_calls=frame_end_calls=elapsed_calls=queue_calls=gate_calls=gate_ready=0;
  a.pending=true;a.repeated=false;a.entry=c.pc;a.ret=c.lr;a.app=c.gpr[3];a.tb=c.timebase;a.wall=Now();a.before=Capture(c,a.app);
 }
}
}
