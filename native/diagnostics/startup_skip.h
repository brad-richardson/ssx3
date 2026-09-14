// GXBE69 development cold-boot presentation skip. The stock frontend/state loader
// still executes; no PC, instruction, guest clock, or initialization is faked.
#pragma once
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace StartupBoot {
enum class Phase { Disabled, Boot, Frontend, Title, TitleReady, MainMenuLoading, MainMenu, Failed };
enum class InputAction { None, PressStart, ReleaseStart };
struct AdvanceInput {
  bool attempted=false, held=false;
  double release_at=0;
  InputAction Update(Phase current,double now,bool allowed) {
    if(held && (!allowed || current!=Phase::TitleReady || now>=release_at)) {
      held=false; return InputAction::ReleaseStart;
    }
    if(!attempted && allowed && current==Phase::TitleReady) {
      attempted=held=true; release_at=now+2; return InputAction::PressStart;
    }
    return InputAction::None;
  }
};
inline std::atomic<Phase> phase{Phase::Disabled};
inline bool configured=false, enabled=false, observing=false, skipped=false;
inline uint32_t frontend=0, title=0, ready_return=0, ready_stack=0;
inline bool title_resources_ready=false;
inline uint32_t active_return=0, active_stack=0;
inline FILE* output=nullptr;
inline std::chrono::steady_clock::time_point started;
inline constexpr uint32_t SDA=0x803dfa60, MovieMask=SDA-31484;
inline constexpr uint32_t FrontendUpdate=0x80097dc4, TitleVTable=0x802dfd78, MainVTable=0x802dfd10;
inline constexpr uint32_t TitleUpdate=0x800d2628;
inline constexpr uint32_t MoviePointerOffset=0xb5a58, MovieDelayOffset=0xb5a60;

inline void Configure(const char* path, bool skip) {
  if (output) std::fclose(output);
  output=path && *path ? std::fopen(path,"wx") : nullptr;
  configured=true; enabled=skip; observing=output || skip; skipped=false;
  frontend=title=ready_return=ready_stack=0;
  title_resources_ready=false; active_return=active_stack=0;
  started=std::chrono::steady_clock::now();
  phase=observing ? Phase::Boot : Phase::Disabled;
}
inline bool CanSkipMovies(uint32_t mask, uint32_t player, uint32_t delay) {
  return mask==15 && player==0 && delay==0;
}
template<class CPU> bool Valid(const CPU& c,uint32_t address,size_t size) {
  return c.ram && address>=0x80000000u && uint64_t(address)+size<=0x80000000ull+c.ram_size;
}
template<class CPU> uint32_t Word(const CPU& c,uint32_t address) {
  if(!Valid(c,address,4))return 0;
  const auto* p=c.ram+address-0x80000000u;
  return uint32_t(p[0])<<24 | uint32_t(p[1])<<16 | uint32_t(p[2])<<8 | p[3];
}
template<class CPU> void Event(const CPU& c,const char* event) {
  if(!output)return;
  const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  const int title_state=Valid(c,title,76) ? int((Word(c,title+28)>>18)&63) : -1;
  std::fprintf(output,"{\"event\":\"%s\",\"elapsed_seconds\":%.6f,\"guest_timebase\":%llu,\"pc\":%u,\"lr\":%u,\"phase\":%d,\"enabled\":%s,\"movies_skipped\":%s,\"movie_mask\":%u,\"frontend\":%u,\"title\":%u,\"title_state\":%d,\"title_resources_ready\":%s}\n",
      event,elapsed,(unsigned long long)c.timebase,c.pc,c.lr,int(phase.load()),enabled?"true":"false",skipped?"true":"false",Word(c,MovieMask),frontend,title,title_state,title_resources_ready?"true":"false");
  std::fflush(output);
}
template<class CPU> void Fail(const CPU& c,const char* event) {
  enabled=false; phase=Phase::Failed; Event(c,event); observing=false;
}
template<class CPU> void Step(CPU& c) {
  if(!configured) {
    const char* flag=std::getenv("SSX_DEBUG_MAIN_MENU");
    Configure(std::getenv("SSX_STARTUP_TRACE"),flag && std::strcmp(flag,"1")==0);
  }
  if(!observing)return;
  if(c.pc!=FrontendUpdate && c.pc!=0x800d27e4 && c.pc!=0x800d2710 &&
      c.pc!=TitleUpdate && c.pc!=0x800d23cc && c.pc!=0x800d20bc &&
      (!ready_return || c.pc!=ready_return) && (!active_return || c.pc!=active_return))return;
  if(c.gpr[13]!=SDA || !Valid(c,MovieMask,4)) { Fail(c,"unsupported_guest_layout"); return; }
  if(c.pc==FrontendUpdate) {
    if(!frontend) {
      frontend=c.gpr[3]; phase=Phase::Frontend; Event(c,"frontend_update");
      if(!Valid(c,frontend,MovieDelayOffset+4)) { Fail(c,"invalid_frontend"); return; }
      // This is the first fully initialized frontend update, before a movie
      // player exists. Match the pinned instruction and initial movie mask.
      if(enabled) {
        if(Word(c,FrontendUpdate)!=0x9421ffc0 ||
            !CanSkipMovies(Word(c,MovieMask),Word(c,frontend+MoviePointerOffset),
                           Word(c,frontend+MovieDelayOffset))) {
          Fail(c,"movie_skip_precondition_failed"); return;
        }
        std::memset(c.ram+MovieMask-0x80000000u,0,4);
        skipped=true; Event(c,"startup_movies_skipped");
      }
    }
    // Checking at a frame-level seam avoids reading the clock every dispatch.
    if(std::chrono::steady_clock::now()-started>std::chrono::seconds(120))
      Fail(c,"startup_timeout");
  }
  if(c.pc==0x800d27e4 && phase.load()<Phase::TitleReady &&
      Valid(c,c.gpr[3],76) && Word(c,c.gpr[3])==TitleVTable) {
    title=c.gpr[3]; phase=Phase::Title; Event(c,"title_loading");
  }
  if(c.pc==0x800d2710 && c.gpr[3]==title && title && !title_resources_ready &&
      phase.load()<Phase::TitleReady) {
    ready_return=c.lr; ready_stack=c.gpr[1];
  } else if(ready_return && c.pc==ready_return && c.gpr[1]==ready_stack) {
    ready_return=0;
    if((c.gpr[3]&255) && frontend && !Word(c,MovieMask) &&
        !Word(c,frontend+MoviePointerOffset) && Word(c,title)==TitleVTable && Word(c,title+64)) {
      title_resources_ready=true; Event(c,"title_assets_ready");
    }
  }
  // The true readiness return precedes state-manager activation. An input
  // edge delivered there can be consumed before the title handles input.
  // State 5 dispatches TitleUpdate, whose first call is the ordinary input
  // handler (0x8023de94). Complete one whole active update before publishing
  // readiness to the host; no guessed delay, repeated presses or guest writes.
  if(c.pc==TitleUpdate && title_resources_ready && phase.load()==Phase::Title &&
      c.gpr[3]==title && Word(c,TitleUpdate)==0x9421fff0 &&
      Word(c,title)==TitleVTable && ((Word(c,title+28)>>18)&63)==5 && Word(c,title+64)) {
    active_return=c.lr; active_stack=c.gpr[1];
  } else if(active_return && c.pc==active_return && c.gpr[1]==active_stack) {
    active_return=0;
    if(title_resources_ready && phase.load()==Phase::Title && frontend &&
        !Word(c,MovieMask) && !Word(c,frontend+MoviePointerOffset) &&
        Word(c,title)==TitleVTable && ((Word(c,title+28)>>18)&63)==5 && Word(c,title+64)) {
      phase=Phase::TitleReady; Event(c,"title_ready");
    }
  }
  if(c.pc==0x800d23cc && Valid(c,c.gpr[3],88) && Word(c,c.gpr[3])==MainVTable) {
    phase=Phase::MainMenuLoading; Event(c,"main_menu_loading");
  }
  if(c.pc==0x800d20bc && phase.load()==Phase::MainMenuLoading &&
      Valid(c,c.gpr[3],88) && Word(c,c.gpr[3])==MainVTable && Word(c,c.gpr[3]+64)) {
    phase=Phase::MainMenu; Event(c,"main_menu_ready"); observing=false;
  }
}
}
