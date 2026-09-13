// Host-side frame replay experiment (milestone 1). Records one guest frame's
// GP command stream with Dolphin's FifoRecorder, then re-runs that stream
// through the video pipeline once per idle-seam visit, 120 times: 40 as
// recorded, 40 with +500 added to every position matrix's first translation
// component as it is loaded into XF memory, 40 as recorded again. No guest
// code runs for a replay; the guest is paused at its idle seam meanwhile.
// Screenshots are requested at the seam before a replay so the next present
// is that replay's XFB copy (immediate XFB). Requires NativeSchedule.
#pragma once
#include "Core/FifoPlayer/FifoDataFile.h"
#include "Core/FifoPlayer/FifoRecorder.h"
#include "VideoCommon/DataReader.h"
#include "VideoCommon/OpcodeDecoding.h"
#include "VideoCommon/XFMemory.h"
#include "VideoCommon/BPMemory.h"
#include "VideoCommon/CPMemory.h"
#include "VideoCommon/TextureDecoder.h"
#include <cstring>
#include <vector>
namespace NativeReplay {
using namespace NativeProbe;
static bool Enabled(){static const bool on=std::getenv("SSX_NATIVE_REPLAY")!=nullptr;return on;}
enum class Phase{Idle,Recording,Replaying,Done};
static Phase phase=Phase::Idle;
static unsigned replays=0,transformed=0,memory_updates=0;
static float offset=0;
static std::vector<u8> PreludeFrom(const u32* bp,const u32* cp,const u32* xf,const u32* regs);
static std::vector<u8> frame;
static u32 fifo_start=0,fifo_end=0;
static double record_wall=0;
static void Transform(u16 address,u32 count){
 if(offset==0)return;
 float* words=reinterpret_cast<float*>(&xfmem);
 for(u32 a=address;a+12<=u32(address)+count&&a+12<=u32(XFMEM_POSMATRICES_END);a+=12){words[a+3]+=offset;++transformed;}
}
// Command bytes that restore the recorded initial BP/CP/XF state, mirroring
// FifoPlayer::LoadRegisters (same register exclusions), so draw command sizes
// and matrices decode as they did when the frame was recorded.
static void Put8(std::vector<u8>& v,u32 x){v.push_back(u8(x));}
static void Put32(std::vector<u8>& v,u32 x){v.push_back(u8(x>>24));v.push_back(u8(x>>16));v.push_back(u8(x>>8));v.push_back(u8(x));}
static std::vector<u8> Prelude(FifoDataFile* file){
 return PreludeFrom(file->GetBPMem(),file->GetCPMem(),file->GetXFMem(),file->GetXFRegs());
}
static std::vector<u8> PreludeFrom(const u32* bp,const u32* cp,const u32* xf,const u32* regs){
 std::vector<u8> v;
 for(u32 i=0;i<FifoDataFile::BP_MEM_SIZE;++i){
  switch(i){case BPMEM_SETDRAWDONE:case BPMEM_PE_TOKEN_ID:case BPMEM_PE_TOKEN_INT_ID:case BPMEM_TRIGGER_EFB_COPY:
   case BPMEM_LOADTLUT1:case BPMEM_PRELOAD_MODE:case BPMEM_PERF1:continue;default:break;}
  Put8(v,0x61);Put32(v,((i<<24)&0xff000000u)|(bp[i]&0x00ffffffu));
 }
 auto cpreg=[&](u32 r){Put8(v,0x08);Put8(v,r);Put32(v,cp[r]);};
 cpreg(MATINDEX_A);cpreg(MATINDEX_B);cpreg(VCD_LO);cpreg(VCD_HI);
 for(u32 i=0;i<CP_NUM_VAT_REG;++i){cpreg(CP_VAT_REG_A+i);cpreg(CP_VAT_REG_B+i);cpreg(CP_VAT_REG_C+i);}
 for(u32 i=0;i<CP_NUM_ARRAYS;++i){cpreg(ARRAY_BASE+i);cpreg(ARRAY_STRIDE+i);}
 for(u32 i=0;i<FifoDataFile::XF_MEM_SIZE;i+=16){Put8(v,0x10);Put32(v,0x000f0000u|(i&0xffffu));for(u32 k=0;k<16;++k)Put32(v,xf[i+k]);}
 for(u32 i=0;i<FifoDataFile::XF_REGS_SIZE;++i){
  const u32 address=i+0x1000;
  if(address==XFMEM_UNKNOWN_1007||(address>=XFMEM_UNKNOWN_GROUP_1_START&&address<=XFMEM_UNKNOWN_GROUP_1_END)||
     (address>=XFMEM_UNKNOWN_GROUP_2_START&&address<=XFMEM_UNKNOWN_GROUP_2_END)||
     (address>=XFMEM_UNKNOWN_GROUP_3_START&&address<=XFMEM_UNKNOWN_GROUP_3_END))continue;
  Put8(v,0x10);Put32(v,(address&0x0fffu)|0x1000u);Put32(v,regs[i]);
 }
 return v;
}
static void ApplyMemory(Core::System& system,FifoDataFile* file){
 auto& memory=system.GetMemory();
 std::memcpy(s_tex_mem.data(),file->GetTexMem(),FifoDataFile::TEX_MEM_SIZE);
 for(const auto& update:file->GetFrame(0).memoryUpdates){
  u8* mem=(update.address&0x10000000u)?&memory.GetEXRAM()[update.address&memory.GetExRamMask()]:&memory.GetRAM()[update.address&memory.GetRamMask()];
  std::memcpy(mem,update.data.data(),update.data.size());
 }
}
// Snapshot of the live video registers, restored after the sequence so the
// game's own command stream keeps decoding with the state it expects.
struct LiveState{std::vector<u32> bp,cp,xf;std::vector<u8> tmem;};
static LiveState SaveLive(){
 LiveState l;l.bp.assign(reinterpret_cast<const u32*>(&bpmem),reinterpret_cast<const u32*>(&bpmem)+FifoDataFile::BP_MEM_SIZE);
 l.cp.assign(256,0);g_main_cp_state.FillCPMemoryArray(l.cp.data());
 l.xf.assign(reinterpret_cast<const u32*>(&xfmem),reinterpret_cast<const u32*>(&xfmem)+FifoDataFile::XF_MEM_SIZE+FifoDataFile::XF_REGS_SIZE);
 l.tmem.assign(s_tex_mem.begin(),s_tex_mem.end());return l;
}
static std::vector<u8> PreludeFrom(const u32* bp,const u32* cp,const u32* xf,const u32* regs);
static void RestoreLive(const LiveState& l){
 std::memcpy(s_tex_mem.data(),l.tmem.data(),l.tmem.size());
 std::vector<u8> v=PreludeFrom(l.bp.data(),l.cp.data(),l.xf.data(),l.xf.data()+FifoDataFile::XF_MEM_SIZE);
 u32 cycles=0;OpcodeDecoder::RunFifo<false>(DataReader(v.data(),v.data()+v.size()),&cycles);
}
static void Run(std::vector<u8>& bytes){u32 cycles=0;OpcodeDecoder::RunFifo<false>(DataReader(bytes.data(),bytes.data()+bytes.size()),&cycles);}
static void Event(const char* action,double ms=0){
 std::fprintf(Output(),"{\"event\":\"replay\",\"action\":\"%s\",\"wall\":%.6f,\"replay\":%u,\"offset\":%.1f,\"bytes\":%zu,\"memory_updates\":%u,\"fifo_start\":%u,\"fifo_end\":%u,\"transformed\":%u,\"ms\":%.3f}\n",
  action,Now(),replays,offset,frame.size(),memory_updates,fifo_start,fifo_end,transformed,ms);
 std::fflush(Output());
}
static inline void Step(CPUState& c){
 NativeSchedule::Step(c);
 if(!Enabled()||!Output())return;
 if(c.pc!=0x801cad24||c.lr!=0x801cd724||render.pending||update.pending)return;
 if(!ExperimentalWindow()||phase==Phase::Done)return;
 auto& system=Core::System::GetInstance();
 auto& recorder=system.GetFifoRecorder();
 if(phase==Phase::Idle){
  // The next present is the frame rendered after the coming retrace, which is
  // also the first frame the recorder captures.
  Core::SaveScreenShot("native-replay-original");
  recorder.StartRecording(1,[]{});record_wall=Now();
  phase=Phase::Recording;Event("record_start");return;
 }
 if(phase==Phase::Recording){
  // The recorder appends the frame when the following frame's first data
  // arrives, after it has already stopped recording.
  FifoDataFile* file=recorder.GetRecordedFile();
  const bool ready=!recorder.IsRecording()&&file&&file->GetFrameCount()>=1;
  if(!ready){
   if(Now()-record_wall>2.0){Event("record_failed");phase=Phase::Done;}
   return;
  }
  const FifoFrameInfo& info=file->GetFrame(0);
  frame=info.fifoData;memory_updates=unsigned(info.memoryUpdates.size());
  fifo_start=info.fifoStart;fifo_end=info.fifoEnd;
  Event("recorded");phase=Phase::Replaying;return;
 }
 // One seam visit performs the whole sequence with the guest paused, so RAM
 // and video state cannot drift between replays: restore the recorded memory
 // and registers once, then replay 120 times.
 FifoDataFile* file=recorder.GetRecordedFile();
 const LiveState live=SaveLive();
 ApplyMemory(system,file);
 std::vector<u8> prelude=Prelude(file);
 Run(prelude);
 Event("restored",double(prelude.size()));
 for(replays=0;replays<120;++replays){
  const unsigned n=replays;
  offset=(n>=40&&n<80)?500.f:0.f;
  if(n==20||n==60||n==100)Core::SaveScreenShot("native-replay-"+std::to_string(n));
  transformed=0;
  XFReplay::g_transform=&Transform;
  const double start=Now();
  Run(frame);
  XFReplay::g_transform=nullptr;
  Event("replay",(Now()-start)*1000);
 }
 RestoreLive(live);
 phase=Phase::Done;Event("done");
}
}
